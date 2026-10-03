"""Turn YOLO boxes into a Scene the mood machine can read.

This is the second half of perception and, like `brain/mood.py`, it is pure
logic: no ultralytics, no OpenCV, no camera. You hand it a list of boxes and
it hands you a `Scene`. That means the interesting decisions -- what counts
as "on the phone", what counts as "head down" -- are unit-testable in
milliseconds without a 20-minute video or a 200MB model.

`detect.py` is the dirty half that owns the model. It writes boxes; this file
interprets them. Keep the split: when you move to the Pi, only detect.py
changes.
"""

from __future__ import annotations

import math
import os
import statistics
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "brain"))

from mood import Scene  # noqa: E402

# --------------------------------------------------------------------------
# Thresholds
# --------------------------------------------------------------------------

# A person fills a lot of frame and YOLO is confident about them.
CONF_PERSON = 0.40

# A phone does not. It is small, often half-occluded by a hand, and often
# motion-blurred. Being strict here is the classic way to build a detector
# that never fires: set it low and let the mood machine's dwell timers throw
# away the noise instead. That is what they are for.
#
# 0.15 rather than 0.25, measured on the hand-labelled recording:
#
#            recall  precision  false strikes
#     0.25    0.321      0.897          0.6%
#     0.15    0.444      0.818          1.1%
#
# Precision falls and it is still the right trade, because the dwell timer
# does not treat the two symmetrically. A real pickup lasts five seconds and
# lands ten consecutive frames; a misdetection lands one. PHONE_DWELL needs
# six frames held together, so clustered evidence accumulates and scattered
# noise does not. Ten more true frames push episodes over the threshold; five
# more scattered false ones do nothing.
#
# 0.321 was also likely below the floor where the dwell ever completes, which
# makes the difference firing at all rather than reacting sooner.
CONF_PHONE = 0.15

# How far outside the person's box a phone still counts as "theirs", as a
# fraction of the person's box size. A phone lying on the far side of the
# desk is not an offence; a phone in your hand is.
#
# Only used when there are no wrists to go on -- see PHONE_NEEDS_WRIST.
PHONE_NEAR_PAD = 0.15

# Whether a phone must be near a WRIST to count as in hand.
#
# The person-box rule stopped working the moment the camera was aimed at the
# desk, which it had to be, because that is where hands and phones are. On
# the second recording it called 131 of 311 working frames "phone" -- 42% --
# and every one was a correct detection of a phone lying on the desk. No
# confidence threshold fixes that: YOLO is right, the geometry is wrong.
#
# Pose gives wrists for free, and "is it in a hand" is exactly what a wrist
# answers. When wrists are visible the phone must be within
# PHONE_WRIST_REACH of one; when they are not, the frame is not judged at all
# rather than falling back to the looser rule, because the looser rule is
# what produced the 42%.
PHONE_NEEDS_WRIST = True

# How close to a wrist a phone must be, as a fraction of the person's box
# height. A hand holding a phone puts the two within roughly a hand's length,
# and a person box is roughly seven hand-lengths tall.
PHONE_WRIST_REACH = 0.22

# Whether head-down is computed at all.
#
# ON, now that HEAD_DOWN_SOURCE = "face" gives it something worth computing.
# It was off while the only available signal was box aspect ratio, which
# measured 0.000 precision and 0.000 recall -- 119 working frames accused and
# every genuine one missed. Off meant it could not even reach WARNING, which
# is what stopped the robot glaring at its owner for 11% of the working day.
#
# Two switches, deliberately: this one decides whether the signal is
# measured, mood.HEAD_DOWN_CAN_FIRE whether a measured signal may fire.
HEAD_DOWN_ENABLED = True

# Which signal head-down is derived from, when it is enabled at all.
#
#   "aspect"  the person box's height/width against a calibrated baseline
#   "face"    whether a frontal face is findable inside the person box
#
# "aspect" is the original and it measured 0.000 precision AND 0.000 recall:
# every genuine head-down frame was called working, and 119 working frames
# were called head-down. Anti-correlated, not merely noisy. The cause is that
# a head is a small part of a torso-height box, so bowing it barely moves the
# ratio -- while leaning in and rolling the chair back move it a great deal.
# Aspect ratio measures lean and distance, not head pose.
#
# "face" looks at the head instead: a frontal Haar cascade loses you when you
# bow, so "person in frame, no findable face" is head-down. It needs
# detect.py --face, which emits the extra boxes. Cheap enough for a Pi Zero
# (a few ms on a downscaled frame) and it needs no posture calibration.
HEAD_DOWN_SOURCE = "face"

# How far down the person's box a face may sit before it stops counting as
# "looking up".
#
# 0.30, from measurement rather than taste. On the hand-labelled recording
# the head sat at median 0.213 of body height while working and 0.367 while
# bowed, and the two distributions did not overlap: working's 90th percentile
# was 0.234, head-down's 10th was 0.309. evaluate.py sweeps every candidate
# cut and reports the best one, which is how this number was found.
FACE_LOW_IN_BOX = 0.34

# How much the person's box has to get *squatter* than their calibrated
# upright baseline before it reads as head-down, as a fraction.
#
# Aspect ratio (height/width) is used rather than the raw top edge because
# it is scale-invariant: leaning back or rolling the chair changes the box
# size but not much its shape, whereas bowing your head genuinely removes
# height from the top of the box while the desk pins the bottom.
HEAD_DOWN_DROP = 0.12

# Frames of calibration before head-down is judged at all. At 2 FPS this is
# 15 seconds of sitting normally.
CALIB_FRAMES = 30

# How close to the top of the frame the person's box may come before its
# aspect ratio stops meaning anything, as a fraction of frame height.
#
# This is the failure that head-down detection dies of. If the top of your
# head is outside the frame, YOLO's box stops at the edge, so the box gets
# shorter when you sit *up* -- exactly backwards -- and squatter whenever you
# shift forward. Measured on real desk footage the result was 3.9% precision:
# 278 working frames called head-down out of 310 calls.
#
# There is no threshold that rescues a clipped box, so clipped frames are not
# judged at all and are kept out of the calibration baseline. The fix is
# physical: raise the camera until the head has headroom.
EDGE_MARGIN = 0.01


@dataclass
class Box:
    """One detection. Pixel coordinates, top-left origin, y grows downward."""

    label: str
    conf: float
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def w(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def h(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def cx(self) -> float:
        return (self.x1 + self.x2) / 2.0

    @property
    def cy(self) -> float:
        return (self.y1 + self.y2) / 2.0

    @property
    def area(self) -> float:
        return self.w * self.h

    @property
    def aspect(self) -> float:
        """height / width. Tall box = sitting up. Squat box = hunched."""
        return self.h / self.w if self.w > 0 else 0.0


def pick_person(boxes: list[Box]) -> Box | None:
    """The biggest confident person in frame.

    Biggest, not first: if a flatmate wanders past in the background you want
    the one at the desk, and the one at the desk is nearer the camera and
    therefore larger.
    """
    people = [b for b in boxes if b.label == "person" and b.conf >= CONF_PERSON]
    return max(people, key=lambda b: b.area) if people else None


def phone_in_hand(person: Box | None, boxes: list[Box]) -> Box | None:
    """The phone that belongs to this person, if any.

    Two rules, and which one applies depends on whether pose found wrists.

    With wrists: the phone must be within PHONE_WRIST_REACH of one. This is
    the only rule that separates "in my hand" from "on my desk" once the
    camera is aimed at the desk, and aiming it there is not optional -- the
    hands and the phone are what the robot cares about.

    Without wrists: the phone's centre must land inside the person's box
    grown by PHONE_NEAR_PAD. Looser, and it is what produced a 42%
    false-positive rate on desk-facing footage, so PHONE_NEEDS_WRIST refuses
    to fall back to it. A missed offence costs a slower reaction; a false one
    costs someone a soaking they did not earn.
    """
    if person is None:
        return None
    phones = [b for b in boxes if b.label == "cell phone" and b.conf >= CONF_PHONE]
    if not phones:
        return None

    wrists = [b for b in boxes if b.label == "wrist"]
    if wrists:
        reach = person.h * PHONE_WRIST_REACH
        near = [
            p for p in phones
            if any(math.hypot(p.cx - w.cx, p.cy - w.cy) <= reach for w in wrists)
        ]
        return max(near, key=lambda b: b.conf) if near else None

    if PHONE_NEEDS_WRIST:
        return None

    padx = person.w * PHONE_NEAR_PAD
    pady = person.h * PHONE_NEAR_PAD
    near = [
        p for p in phones
        if person.x1 - padx <= p.cx <= person.x2 + padx
        and person.y1 - pady <= p.cy <= person.y2 + pady
    ]
    return max(near, key=lambda b: b.conf) if near else None


def face_in_person(person: Box | None, boxes: list[Box]) -> Box | None:
    """The face belonging to this person, if the cascade found one.

    Restricted to faces whose centre is inside the person box, so a face on a
    poster behind you does not vouch for you being upright.
    """
    if person is None:
        return None
    faces = [b for b in boxes if b.label == "face"
             and person.x1 <= b.cx <= person.x2
             and person.y1 <= b.cy <= person.y2]
    return max(faces, key=lambda b: b.area) if faces else None


def head_down_from_face(person: Box | None, boxes: list[Box]) -> bool:
    """Head-down when no frontal face is findable, or the face sits low.

    Two ways a bowed head shows up, and both count:

    - the cascade loses the face entirely, which is the common case; or
    - it still finds it, but low in the person box, because the head has
      dropped toward the desk.

    A person turned fully away also reads as head-down here. That is a known
    confusion and an honest one to measure rather than assume: turning away
    from the screen is not obviously innocent either.
    """
    if person is None:
        return False
    face = face_in_person(person, boxes)
    if face is None:
        return True
    if person.h <= 0:
        return False
    return (face.cy - person.y1) / person.h > FACE_LOW_IN_BOX


class HeadDownCalibrator:
    """Learns what *your* upright posture looks like, then flags deviations.

    There is no universal "head down" aspect ratio -- it depends on your
    chair, your desk, and where the camera sits. So the first CALIB_FRAMES
    of a run establish a personal baseline and everything is judged against
    that. Run the calibration while sitting normally.
    """

    def __init__(self, calib_frames: int = CALIB_FRAMES, drop: float = HEAD_DOWN_DROP,
                 enabled: bool = HEAD_DOWN_ENABLED, source: str = HEAD_DOWN_SOURCE):
        self.calib_frames = calib_frames
        self.drop = drop
        self.enabled = enabled
        self.source = source
        self._samples: list[float] = []
        self.baseline: float | None = None
        # Frames where the person was present but their box ran off the top
        # of the frame. Reported by evaluate.py: a high count is a camera
        # mounting problem, not a threshold problem.
        self.clipped = 0
        self.seen = 0

    @property
    def calibrating(self) -> bool:
        # Only the "aspect" source feeds this calibrator, and only when
        # head-down is enabled at all. In every other configuration there is
        # nothing to calibrate, so this is not "still calibrating" -- and
        # since evaluate.py skips calibrating frames, saying True here
        # silently discarded every frame in the run.
        if not self.enabled or self.source != "aspect":
            return False
        return self.baseline is None

    def feed(self, person: Box | None, frame_h: float | None = None) -> bool:
        """Returns True if this frame reads as head-down.

        Always False while calibrating -- an uncalibrated guess is worse than
        no guess, because the mood machine would start escalating on it. Also
        always False when the box is clipped by the top of the frame, for the
        same reason: a measurement that cannot mean what it says is worse
        than no measurement, and this one escalates to STRIKE.
        """
        if person is None or not self.enabled:
            return False

        self.seen += 1
        if frame_h is not None and person.y1 <= frame_h * EDGE_MARGIN:
            self.clipped += 1
            return False

        if self.baseline is None:
            self._samples.append(person.aspect)
            if len(self._samples) >= self.calib_frames:
                # Median, not mean: one frame where YOLO clips your box in
                # half should not move the baseline.
                self.baseline = statistics.median(self._samples)
            return False

        return person.aspect < self.baseline * (1.0 - self.drop)

    def force_baseline(self, value: float) -> None:
        """Set the baseline directly, for tests and for reusing a calibration."""
        self.baseline = value


def build_scene(boxes: list[Box], calibrator: HeadDownCalibrator,
                frame_h: float | None = None) -> Scene:
    """One frame of detections in, one Scene out.

    Note what is *not* here: no timers, no hysteresis, no memory of previous
    frames beyond the posture baseline. This reports what the camera sees
    right now and nothing else. All the judgement about how long something
    has been true belongs to `brain/mood.py`, which already has tests for it.
    """
    person = pick_person(boxes)
    phone = phone_in_hand(person, boxes)
    # The calibrator carries the configuration, taken from the module
    # constants when it was built. Reading the globals here instead would let
    # a caller hold a calibrator configured one way while build_scene judged
    # it another -- which is exactly what a test caught.
    if not calibrator.enabled:
        head_down = False
    elif calibrator.source == "face":
        head_down = head_down_from_face(person, boxes)
    else:
        head_down = calibrator.feed(person, frame_h)

    return Scene(
        person_present=person is not None,
        phone_visible=phone is not None,
        head_down=head_down,
        range_mm=None,  # the VL53L0X fills this in on the real robot
    )
