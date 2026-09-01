"""Mood state machine for The Enforcer — the personality, as pure logic.

No camera, no servos, no network, no clock of its own. That's deliberate, for
the same reason `HapticMapper.h` has no Arduino in it: this one file can be
unit-tested on a desktop (see tests/), watched in a browser (see
simulator/mood_simulator.html), and ported line-for-line to whatever ends up
running it. Everything hardware-shaped lives outside: perception fills in a
Scene, and the caller turns a Decision into servo commands, faces and a pump
pulse.

The state machine answers exactly one question:

    given what the camera currently sees, and what time it is,
    what mood is the robot in and should it fire right now?

CHILL -> SUSPICIOUS -> WARNING -> STRIKE -> SMUG -> CHILL

Read `BEHAVIOURS.md` first — the arbitration stack there outranks everything
here. This module is level 3 ("the mood state machine's intent"); the cliff
reflex and the flee reflex live on the ESP32 and can pre-empt any decision
this file makes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# --------------------------------------------------------------------------
# Timing. All seconds.
# --------------------------------------------------------------------------
#
# These are the knobs that decide whether the robot is "impressive" or
# "a machine that soaks you while you are working". Nothing else in the
# project matters as much, and none of it needs hardware to tune -- which is
# why this is the first thing built.

# How long an offence must be held before the robot even reacts. Below this
# it ignores you completely: a glance at a notification is not slacking.
NOTICE_AFTER = 1.0

# Per-offence dwell before WARNING. They differ because the evidence differs.
PHONE_DWELL = 3.0      # a phone in your hand is unambiguous
HEAD_DOWN_DWELL = 6.0  # you might just be reading paper. Be slower to judge
ABSENT_DWELL = 20.0    # you are allowed to stand up

# Whether head-down may escalate all the way to STRIKE, or only to WARNING.
#
# ON, on measurement -- but only once the signal came from the head. Same
# 10.8 min hand-labelled recording, three ways of asking the same question:
#
#     box aspect ratio, uncropped   0.000 precision, 0.000 recall
#     box aspect ratio, 53.5 deg    0.039 precision, 0.600 recall
#     pose head keypoints           0.529 precision, 0.900 recall
#
# The precision figure understates the last one. Of its 16 false positives,
# 11 were frames where the subject genuinely was on their phone and YOLO had
# lost the phone box -- an offence caught under the wrong name, not a false
# accusation. Only 4 were real working frames: 0.4% of them.
#
# It also covers for the phone detector: phone recall alone is 32%, and
# 37 of 81 phone frames now trigger some offence because a head tilted at a
# phone is still a head that is down.
#
# Sample size is 20 head-down frames. Promising, not settled -- record more
# before quoting the number without it.
HEAD_DOWN_CAN_FIRE = True

# Extra time in WARNING before it fires. This is the "you have been warned"
# window -- the robot is taunting and creeping at you for this long before
# any water moves. A commitment device warns; it does not ambush.
STRIKE_AFTER_WARNING = 3.0

SMUG_DURATION = 4.0    # gloating time after a hit
COOLDOWN = 15.0        # minimum gap between shots, whatever the scene says

# THE IMPORTANT ONE. How long the offence must be *continuously gone* before
# the robot de-escalates.
#
# It is not symmetric with the dwell times above, and that asymmetry is the
# whole trick. The detector runs at 1-2 FPS, so a 3-second phone dwell is
# only 4-5 frames of evidence. YOLO will drop a frame -- a hand moves over
# the phone, the box flickers -- and if a single miss reset the escalation,
# the robot would never reach STRIKE at all.
#
# 1.5s survives two consecutive dropped frames at 1.5 FPS. Raise it if your
# measured frame rate is worse; lower it and the robot starts forgiving you
# for things it should not.
CLEAR_GRACE = 1.5


class Mood(Enum):
    CHILL = "chill"
    SUSPICIOUS = "suspicious"
    WARNING = "warning"
    STRIKE = "strike"
    SMUG = "smug"


class Offence(Enum):
    """What the robot thinks you are doing wrong. NONE means you're working."""

    NONE = "none"
    PHONE = "phone"
    HEAD_DOWN = "head_down"
    ABSENT = "absent"


# Dwell before WARNING, per offence.
DWELL = {
    Offence.PHONE: PHONE_DWELL,
    Offence.HEAD_DOWN: HEAD_DOWN_DWELL,
    Offence.ABSENT: ABSENT_DWELL,
}


@dataclass
class Scene:
    """What perception saw this frame. Filled in by the detector on the Pi.

    `range_mm` is the forward VL53L0X. None means "no reading" -- which is
    treated as out-of-band, so a dead sensor fails safe (no fire) rather than
    firing blind.
    """

    person_present: bool = False
    phone_visible: bool = False
    head_down: bool = False
    range_mm: float | None = None


@dataclass
class Decision:
    """What the robot should do about it. The caller renders this."""

    mood: Mood
    offence: Offence
    fire_ms: int = 0          # non-zero for exactly one update, on the shot
    held_s: float = 0.0       # how long the current offence has been held
    reason: str = ""          # human-readable, for logs and the simulator

    @property
    def should_fire(self) -> bool:
        return self.fire_ms > 0


def classify(scene: Scene) -> Offence:
    """Reduce a Scene to the single worst thing happening.

    Order matters: a visible phone outranks a bowed head, because the phone
    is the offence the project is actually about. If the person is gone
    entirely there is nothing else to judge.
    """
    if not scene.person_present:
        return Offence.ABSENT
    if scene.phone_visible:
        return Offence.PHONE
    if scene.head_down:
        return Offence.HEAD_DOWN
    return Offence.NONE


def can_ever_fire(offence: Offence) -> bool:
    """Which offences may reach STRIKE. The rest top out at WARNING.

    ABSENT never can: interlock 1 in BEHAVIOURS.md requires a detected person
    before the pump may run, so firing at an empty chair is impossible by
    construction. The robot is still allowed to be visibly annoyed about it --
    it just sulks at your empty desk, which is funnier anyway.

    HEAD_DOWN is gated on HEAD_DOWN_CAN_FIRE, which is off because the signal
    measured at 0.000 precision on real footage. Same idea: it may still
    escalate and taunt, it may not pull the trigger.
    """
    if offence is Offence.PHONE:
        return True
    if offence is Offence.HEAD_DOWN:
        return HEAD_DOWN_CAN_FIRE
    return False


@dataclass
class MoodMachine:
    """Feed it a Scene and a monotonic clock; get a Decision back.

    The caller owns the clock (`now` in seconds, any epoch, must not go
    backwards). Injecting it rather than calling time.monotonic() internally
    is what lets the tests run a whole 30-second escalation instantly and
    lets the browser simulator scrub time by hand.
    """

    mood: Mood = Mood.CHILL
    offence: Offence = Offence.NONE

    # Timestamps. None means "not currently tracking".
    _offence_since: float | None = field(default=None, repr=False)
    _clear_since: float | None = field(default=None, repr=False)
    _mood_since: float = field(default=0.0, repr=False)
    _last_fire: float | None = field(default=None, repr=False)
    _fired_this_episode: bool = field(default=False, repr=False)

    def reset(self, now: float = 0.0) -> None:
        self.mood = Mood.CHILL
        self.offence = Offence.NONE
        self._offence_since = None
        self._clear_since = None
        self._mood_since = now
        self._last_fire = None
        self._fired_this_episode = False

    # -- internals ---------------------------------------------------------

    def _go(self, mood: Mood, now: float) -> None:
        if mood is not self.mood:
            self.mood = mood
            self._mood_since = now

    def _cooling_down(self, now: float) -> bool:
        return self._last_fire is not None and (now - self._last_fire) < COOLDOWN

    # -- the loop ----------------------------------------------------------

    def update(self, scene: Scene, now: float) -> Decision:
        current = classify(scene)

        # --- track how long the offence has been held -------------------
        #
        # A *different* offence restarts the clock: switching from head-down
        # to phone is a new accusation, not a continuation of the old one.
        if current is Offence.NONE:
            if self._clear_since is None:
                self._clear_since = now
            # Only forget the offence once you have been clean for a while.
            if now - self._clear_since >= CLEAR_GRACE:
                self._offence_since = None
                self.offence = Offence.NONE
                self._fired_this_episode = False
        else:
            self._clear_since = None
            if current is not self.offence or self._offence_since is None:
                self.offence = current
                self._offence_since = now
                self._fired_this_episode = False

        held = 0.0 if self._offence_since is None else now - self._offence_since

        # --- SMUG runs on its own timer, not on the scene ----------------
        if self.mood is Mood.SMUG:
            if now - self._mood_since >= SMUG_DURATION:
                self._go(Mood.CHILL, now)
            else:
                return Decision(self.mood, self.offence, 0, held, "gloating")

        # --- nothing wrong -----------------------------------------------
        if self._offence_since is None:
            self._go(Mood.CHILL, now)
            return Decision(self.mood, Offence.NONE, 0, 0.0, "working, left alone")

        dwell = DWELL[self.offence]

        # --- escalate ----------------------------------------------------
        if held >= dwell + STRIKE_AFTER_WARNING and can_ever_fire(self.offence):
            if self._fired_this_episode:
                # Already soaked them for this episode. Hold at WARNING and
                # keep glaring rather than firing on every single update.
                self._go(Mood.WARNING, now)
                return Decision(self.mood, self.offence, 0, held, "already fired")
            if self._cooling_down(now):
                self._go(Mood.WARNING, now)
                left = COOLDOWN - (now - self._last_fire)
                return Decision(self.mood, self.offence, 0, held,
                                f"cooling down, {left:.1f}s left")

            self._go(Mood.STRIKE, now)
            self._last_fire = now
            self._fired_this_episode = True
            return Decision(self.mood, self.offence, 250, held, "FIRE")

        if held >= dwell:
            self._go(Mood.WARNING, now)
            return Decision(self.mood, self.offence, 0, held, "escalating")

        if held >= NOTICE_AFTER:
            self._go(Mood.SUSPICIOUS, now)
            return Decision(self.mood, self.offence, 0, held, "noticed")

        # Held, but under the notice threshold -- deliberately ignore it.
        self._go(Mood.CHILL, now)
        return Decision(self.mood, self.offence, 0, held, "below notice threshold")


def post_strike(machine: MoodMachine, now: float) -> None:
    """Call once the pump has actually run, to move STRIKE -> SMUG.

    Kept separate so the state machine never assumes a shot happened. The
    firmware interlocks in BEHAVIOURS.md can refuse the shot (out of range,
    stale command, hardware switch open) and in that case the robot should
    stay angry rather than smugly celebrating a hit it never landed.
    """
    if machine.mood is Mood.STRIKE:
        machine._go(Mood.SMUG, now)
