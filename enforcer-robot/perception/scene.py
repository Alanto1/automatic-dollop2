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
CONF_PHONE = 0.25

# How far outside the person's box a phone still counts as "theirs", as a
# fraction of the person's box size. A phone lying on the far side of the
# desk is not an offence; a phone in your hand is.
PHONE_NEAR_PAD = 0.15

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

    "Belongs to" means its centre lands inside the person's box grown by
    PHONE_NEAR_PAD. Without this test the robot fires at you because your
    phone is charging on the other side of the desk, which is both wrong and
    the exact failure that makes people unplug a device like this.
    """
    if person is None:
        return None
    phones = [b for b in boxes if b.label == "cell phone" and b.conf >= CONF_PHONE]
    if not phones:
        return None

    padx = person.w * PHONE_NEAR_PAD
    pady = person.h * PHONE_NEAR_PAD
    near = [
        p for p in phones
        if person.x1 - padx <= p.cx <= person.x2 + padx
        and person.y1 - pady <= p.cy <= person.y2 + pady
    ]
    return max(near, key=lambda b: b.conf) if near else None


class HeadDownCalibrator:
    """Learns what *your* upright posture looks like, then flags deviations.

    There is no universal "head down" aspect ratio -- it depends on your
    chair, your desk, and where the camera sits. So the first CALIB_FRAMES
    of a run establish a personal baseline and everything is judged against
    that. Run the calibration while sitting normally.
    """

    def __init__(self, calib_frames: int = CALIB_FRAMES, drop: float = HEAD_DOWN_DROP):
        self.calib_frames = calib_frames
        self.drop = drop
        self._samples: list[float] = []
        self.baseline: float | None = None
        # Frames where the person was present but their box ran off the top
        # of the frame. Reported by evaluate.py: a high count is a camera
        # mounting problem, not a threshold problem.
        self.clipped = 0
        self.seen = 0

    @property
    def calibrating(self) -> bool:
        return self.baseline is None

    def feed(self, person: Box | None, frame_h: float | None = None) -> bool:
        """Returns True if this frame reads as head-down.

        Always False while calibrating -- an uncalibrated guess is worse than
        no guess, because the mood machine would start escalating on it. Also
        always False when the box is clipped by the top of the frame, for the
        same reason: a measurement that cannot mean what it says is worse
        than no measurement, and this one escalates to STRIKE.
        """
        if person is None:
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
    head_down = calibrator.feed(person, frame_h)

    return Scene(
        person_present=person is not None,
        phone_visible=phone is not None,
        head_down=head_down,
        range_mm=None,  # the VL53L0X fills this in on the real robot
    )
