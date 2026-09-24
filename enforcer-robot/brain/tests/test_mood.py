#!/usr/bin/env python3
"""Desktop unit tests for mood.py -- escalation, hysteresis and interlocks.

No external test framework: runs with a bare `python3` (see run_tests.sh),
no camera, no robot, no network. Re-run after any mood.py change to confirm
nothing broke.

Every test drives the clock by hand, so a 30-second escalation takes zero
seconds to verify. That is the entire reason MoodMachine takes `now` as an
argument instead of calling time.monotonic() itself.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from mood import (  # noqa: E402
    CLEAR_GRACE,
    COOLDOWN,
    HEAD_DOWN_CAN_FIRE,
    HEAD_DOWN_DWELL,
    NOTICE_AFTER,
    PHONE_DWELL,
    SMUG_DURATION,
    STRIKE_AFTER_WARNING,
    Decision,
    Mood,
    MoodMachine,
    Offence,
    Scene,
    can_ever_fire,
    classify,
    post_strike,
)


# Each test function owns a local `passed` list that check() flips to
# False on the first failed assertion (and prints why) -- the same
# convention as firmware/tests/test_haptic_mapper.cpp.
class _Ctx:
    def __init__(self):
        self.passed = True

    def check(self, cond, what):
        if not cond:
            line = sys._getframe(1).f_lineno
            print("  FAILED (line %d): %s" % (line, what))
            self.passed = False


# -- scene shorthands ------------------------------------------------------

WORKING = Scene(person_present=True)
ON_PHONE = Scene(person_present=True, phone_visible=True)
HEAD_DOWN = Scene(person_present=True, head_down=True)
EMPTY_CHAIR = Scene(person_present=False)


def run(machine, scene, t):
    """One frame. Returns the Decision, for readability at call sites."""
    return machine.update(scene, t)


def frames(machine, scene, start, stop, step=0.5):
    """Feed the same scene from `start` to `stop` at a plausible frame rate.

    Real perception runs at 1-2 FPS; 0.5s steps is the optimistic end of
    that, which is what the timing constants were picked against.
    """
    last = None
    t = start
    while t <= stop + 1e-9:
        last = machine.update(scene, t)
        t += step
    return last


# -- classify --------------------------------------------------------------


def test_Classify_NobodyThere_IsAbsent():
    c = _Ctx()
    c.check(classify(EMPTY_CHAIR) is Offence.ABSENT, "empty chair -> ABSENT")
    # Absent wins even if a stale phone box is still in frame.
    ghost = Scene(person_present=False, phone_visible=True, head_down=True)
    c.check(classify(ghost) is Offence.ABSENT, "no person outranks everything")
    return c.passed


def test_Classify_PhoneOutranksHeadDown():
    c = _Ctx()
    both = Scene(person_present=True, phone_visible=True, head_down=True)
    c.check(classify(both) is Offence.PHONE, "phone outranks head-down")
    c.check(classify(HEAD_DOWN) is Offence.HEAD_DOWN, "head-down alone")
    return c.passed


def test_Classify_PersonWorking_IsNone():
    c = _Ctx()
    c.check(classify(WORKING) is Offence.NONE, "present, no phone, head up")
    return c.passed


# -- the firing interlock that lives in this file --------------------------


def test_CanEverFire_AbsentCanNever():
    c = _Ctx()
    # Interlock 1 in BEHAVIOURS.md: no detected person, no pump. Firing at an
    # empty chair must be impossible by construction, not by luck of timing.
    c.check(not can_ever_fire(Offence.ABSENT), "ABSENT can never fire")
    c.check(not can_ever_fire(Offence.NONE), "NONE can never fire")
    c.check(can_ever_fire(Offence.PHONE), "PHONE can fire")
    # HEAD_DOWN is gated on a measurement, not a belief -- it scored 0.000
    # precision on real footage, so it escalates but does not fire. The test
    # asserts the switch is honoured in both directions rather than pinning
    # today's value, so re-measuring on a raised camera does not break it.
    c.check(can_ever_fire(Offence.HEAD_DOWN) is HEAD_DOWN_CAN_FIRE,
            "HEAD_DOWN firing follows HEAD_DOWN_CAN_FIRE")
    return c.passed


def test_Absent_EscalatesToWarningButNeverFires():
    c = _Ctx()
    m = MoodMachine()
    # Well past ABSENT_DWELL + STRIKE_AFTER_WARNING, and past the cooldown
    # too, so nothing but the interlock is holding the pump shut.
    end = frames(m, EMPTY_CHAIR, 0.0, 60.0, 1.0)
    c.check(end.mood is Mood.WARNING, "sulks at the empty desk, mood=%s" % end.mood)
    c.check(end.offence is Offence.ABSENT, "offence stays ABSENT")
    c.check(not end.should_fire, "never fires at nobody")
    return c.passed


# -- escalation ------------------------------------------------------------


def test_Phone_BelowNoticeThreshold_Ignored():
    c = _Ctx()
    m = MoodMachine()
    d = run(m, ON_PHONE, 0.0)
    c.check(d.mood is Mood.CHILL, "first frame is CHILL")
    d = run(m, ON_PHONE, NOTICE_AFTER - 0.1)
    c.check(d.mood is Mood.CHILL, "a glance at a notification is not slacking")
    return c.passed


def test_Phone_EscalationLadder():
    c = _Ctx()
    m = MoodMachine()
    run(m, ON_PHONE, 0.0)

    d = run(m, ON_PHONE, NOTICE_AFTER)
    c.check(d.mood is Mood.SUSPICIOUS, "at NOTICE_AFTER -> SUSPICIOUS")

    d = run(m, ON_PHONE, PHONE_DWELL - 0.1)
    c.check(d.mood is Mood.SUSPICIOUS, "still SUSPICIOUS just under the dwell")

    d = run(m, ON_PHONE, PHONE_DWELL)
    c.check(d.mood is Mood.WARNING, "at PHONE_DWELL -> WARNING")
    c.check(not d.should_fire, "WARNING does not fire")

    d = run(m, ON_PHONE, PHONE_DWELL + STRIKE_AFTER_WARNING - 0.1)
    c.check(d.mood is Mood.WARNING, "warned, but not yet out of patience")

    d = run(m, ON_PHONE, PHONE_DWELL + STRIKE_AFTER_WARNING)
    c.check(d.mood is Mood.STRIKE, "at dwell + warning window -> STRIKE")
    c.check(d.should_fire, "STRIKE fires")
    c.check(d.fire_ms > 0, "fire_ms is a real pulse length")
    return c.passed


def test_HeadDown_IsJudgedSlowerThanPhone():
    c = _Ctx()
    m = MoodMachine()
    # You might be reading paper. At the moment a phone would already have
    # earned a WARNING, a bowed head has not.
    d = frames(m, HEAD_DOWN, 0.0, PHONE_DWELL)
    c.check(d.mood is Mood.SUSPICIOUS, "phone dwell is not enough for a head")
    d = frames(m, HEAD_DOWN, PHONE_DWELL, HEAD_DOWN_DWELL)
    c.check(d.mood is Mood.WARNING, "HEAD_DOWN_DWELL -> WARNING")
    c.check(HEAD_DOWN_DWELL > PHONE_DWELL, "constants stay ordered")
    return c.passed


def test_Fire_HappensExactlyOncePerEpisode():
    c = _Ctx()
    m = MoodMachine()
    shots = 0
    t = 0.0
    while t <= 30.0 + 1e-9:
        if run(m, ON_PHONE, t).should_fire:
            shots += 1
        t += 0.5
    # 30 seconds of continuous phone use is one soaking, not sixty.
    c.check(shots == 1, "one shot per episode, got %d" % shots)
    return c.passed


# -- hysteresis: the reason this file exists -------------------------------


def test_DroppedFrame_DoesNotResetEscalation():
    c = _Ctx()
    m = MoodMachine()
    run(m, ON_PHONE, 0.0)
    run(m, ON_PHONE, 1.0)
    run(m, ON_PHONE, 2.0)
    # YOLO misses the phone for one frame -- a hand moves across it.
    d = run(m, WORKING, 2.5)
    c.check(d.offence is Offence.PHONE, "one miss does not clear the accusation")
    c.check(d.mood is not Mood.CHILL, "and does not reset the mood")
    # Detector recovers, and the escalation lands on schedule.
    run(m, ON_PHONE, 3.0)
    d = run(m, ON_PHONE, PHONE_DWELL + STRIKE_AFTER_WARNING)
    c.check(d.should_fire, "still fires on time despite the dropped frame")
    return c.passed


def test_TwoConsecutiveDroppedFrames_SurviveAt_1_5_FPS():
    c = _Ctx()
    m = MoodMachine()
    # The number CLEAR_GRACE was actually chosen for: 1.5 FPS is 0.67s per
    # frame, so two misses in a row is 1.33s of silence.
    c.check(CLEAR_GRACE > 2 * (1.0 / 1.5), "CLEAR_GRACE survives 2 misses at 1.5 FPS")
    run(m, ON_PHONE, 0.0)
    run(m, ON_PHONE, 0.67)
    run(m, WORKING, 1.33)
    run(m, WORKING, 2.0)
    d = run(m, ON_PHONE, 2.67)
    c.check(d.offence is Offence.PHONE, "two misses in a row do not clear it")
    c.check(d.held_s > 2.0, "the held timer kept running, held=%.2f" % d.held_s)
    return c.passed


def test_ActuallyStopping_ClearsAfterGrace():
    c = _Ctx()
    m = MoodMachine()
    frames(m, ON_PHONE, 0.0, 4.0)

    # The grace clock is anchored to the first frame that actually *sees* you
    # clean, not to the last frame that saw the phone. That matters when the
    # camera stalls: a gap in the feed is not evidence that you stopped, so a
    # stall makes the robot slower to forgive rather than faster.
    first_clean = 4.5
    run(m, WORKING, first_clean)
    d = run(m, WORKING, first_clean + CLEAR_GRACE - 0.1)
    c.check(d.offence is Offence.PHONE, "not forgiven a moment early")

    d = run(m, WORKING, first_clean + CLEAR_GRACE)
    c.check(d.offence is Offence.NONE, "put it away and it lets go")
    c.check(d.mood is Mood.CHILL, "back to CHILL")
    c.check(d.held_s == 0.0, "held timer cleared")
    return c.passed


def test_SwitchingOffence_RestartsTheClock():
    c = _Ctx()
    m = MoodMachine()
    # Nearly at a head-down WARNING...
    frames(m, HEAD_DOWN, 0.0, HEAD_DOWN_DWELL - 1.0)
    # ...then a phone appears. That is a new accusation, not a continuation:
    # the robot must not inherit five seconds of head-down anger and fire
    # almost immediately.
    d = run(m, ON_PHONE, HEAD_DOWN_DWELL - 0.5)
    c.check(d.offence is Offence.PHONE, "offence switched")
    c.check(d.held_s == 0.0, "clock restarted, held=%.2f" % d.held_s)
    c.check(d.mood is Mood.CHILL, "and so did the escalation")
    return c.passed


# -- SMUG and the refused shot ---------------------------------------------


def test_PostStrike_GoesSmugThenChill():
    c = _Ctx()
    m = MoodMachine()
    fire_t = PHONE_DWELL + STRIKE_AFTER_WARNING
    frames(m, ON_PHONE, 0.0, fire_t)
    c.check(m.mood is Mood.STRIKE, "fired")

    post_strike(m, fire_t)
    c.check(m.mood is Mood.SMUG, "pump ran -> gloating")

    d = run(m, ON_PHONE, fire_t + SMUG_DURATION - 0.1)
    c.check(d.mood is Mood.SMUG, "still gloating")
    c.check(not d.should_fire, "no firing while smug")

    d = run(m, ON_PHONE, fire_t + SMUG_DURATION)
    c.check(d.mood is not Mood.SMUG, "gloating ends on its own timer")
    return c.passed


def test_RefusedShot_StaysAngryInsteadOfSmug():
    c = _Ctx()
    m = MoodMachine()
    # The firmware interlocks can veto the shot (out of range, stale command,
    # hardware switch open). post_strike is only called when water actually
    # moved, so a robot that missed must not celebrate.
    frames(m, ON_PHONE, 0.0, PHONE_DWELL)
    c.check(m.mood is Mood.WARNING, "warning, no shot taken")
    post_strike(m, PHONE_DWELL)
    c.check(m.mood is Mood.WARNING, "post_strike is a no-op unless STRIKE")
    return c.passed


# -- cooldown --------------------------------------------------------------


def test_Cooldown_BlocksASecondSoakingTooSoon():
    c = _Ctx()
    m = MoodMachine()
    fire_t = PHONE_DWELL + STRIKE_AFTER_WARNING
    d = frames(m, ON_PHONE, 0.0, fire_t)
    c.check(d.should_fire, "first shot")
    post_strike(m, fire_t)

    # Phone away long enough to clear, then straight back to it.
    frames(m, WORKING, fire_t, fire_t + SMUG_DURATION + CLEAR_GRACE)
    restart = fire_t + SMUG_DURATION + CLEAR_GRACE + 0.5
    d = frames(m, ON_PHONE, restart, restart + fire_t)
    c.check(not d.should_fire, "second soaking inside COOLDOWN is refused")
    c.check(d.mood is Mood.WARNING, "held at WARNING instead, mood=%s" % d.mood)
    c.check("cooling" in d.reason, "and says why: %r" % d.reason)
    return c.passed


def test_Cooldown_ExpiresAndAllowsTheNextShot():
    c = _Ctx()
    m = MoodMachine()
    fire_t = PHONE_DWELL + STRIKE_AFTER_WARNING
    frames(m, ON_PHONE, 0.0, fire_t)
    post_strike(m, fire_t)

    # Wait out the whole cooldown working, then offend again.
    frames(m, WORKING, fire_t, fire_t + COOLDOWN)
    restart = fire_t + COOLDOWN + 0.5
    d = frames(m, ON_PHONE, restart, restart + fire_t)
    c.check(d.should_fire, "fires again once the cooldown has expired")
    return c.passed


# -- shape of the output ---------------------------------------------------


def test_Decision_AlwaysCarriesAReason():
    c = _Ctx()
    m = MoodMachine()
    # The reason string is what the simulator prints and what the on-robot
    # log records when a demo misbehaves in front of a jury. It must never
    # be empty on any path.
    for scene, t in [(WORKING, 0.0), (ON_PHONE, 1.0), (ON_PHONE, 3.0),
                     (ON_PHONE, 6.0), (EMPTY_CHAIR, 40.0), (WORKING, 60.0)]:
        d = run(m, scene, t)
        c.check(isinstance(d, Decision), "returns a Decision")
        c.check(bool(d.reason), "reason set at t=%.1f" % t)
        c.check(d.fire_ms >= 0, "fire_ms never negative")
    return c.passed


def test_Reset_ReturnsToAKnownState():
    c = _Ctx()
    m = MoodMachine()
    frames(m, ON_PHONE, 0.0, 10.0)
    m.reset(10.0)
    c.check(m.mood is Mood.CHILL, "reset -> CHILL")
    c.check(m.offence is Offence.NONE, "reset -> no offence")
    # And the cooldown is gone too, so a reset machine can fire immediately.
    d = frames(m, ON_PHONE, 10.0, 10.0 + PHONE_DWELL + STRIKE_AFTER_WARNING)
    c.check(d.should_fire, "a reset machine is not stuck in cooldown")
    return c.passed


TESTS = [
    ("Classify_NobodyThere_IsAbsent", test_Classify_NobodyThere_IsAbsent),
    ("Classify_PhoneOutranksHeadDown", test_Classify_PhoneOutranksHeadDown),
    ("Classify_PersonWorking_IsNone", test_Classify_PersonWorking_IsNone),
    ("CanEverFire_AbsentCanNever", test_CanEverFire_AbsentCanNever),
    ("Absent_EscalatesToWarningButNeverFires",
     test_Absent_EscalatesToWarningButNeverFires),
    ("Phone_BelowNoticeThreshold_Ignored", test_Phone_BelowNoticeThreshold_Ignored),
    ("Phone_EscalationLadder", test_Phone_EscalationLadder),
    ("HeadDown_IsJudgedSlowerThanPhone", test_HeadDown_IsJudgedSlowerThanPhone),
    ("Fire_HappensExactlyOncePerEpisode", test_Fire_HappensExactlyOncePerEpisode),
    ("DroppedFrame_DoesNotResetEscalation", test_DroppedFrame_DoesNotResetEscalation),
    ("TwoConsecutiveDroppedFrames_SurviveAt_1_5_FPS",
     test_TwoConsecutiveDroppedFrames_SurviveAt_1_5_FPS),
    ("ActuallyStopping_ClearsAfterGrace", test_ActuallyStopping_ClearsAfterGrace),
    ("SwitchingOffence_RestartsTheClock", test_SwitchingOffence_RestartsTheClock),
    ("PostStrike_GoesSmugThenChill", test_PostStrike_GoesSmugThenChill),
    ("RefusedShot_StaysAngryInsteadOfSmug", test_RefusedShot_StaysAngryInsteadOfSmug),
    ("Cooldown_BlocksASecondSoakingTooSoon", test_Cooldown_BlocksASecondSoakingTooSoon),
    ("Cooldown_ExpiresAndAllowsTheNextShot", test_Cooldown_ExpiresAndAllowsTheNextShot),
    ("Decision_AlwaysCarriesAReason", test_Decision_AlwaysCarriesAReason),
    ("Reset_ReturnsToAKnownState", test_Reset_ReturnsToAKnownState),
]


def main():
    passed = 0
    for name, fn in TESTS:
        ok = fn()
        print("[%s] %s" % ("PASS" if ok else "FAIL", name))
        if ok:
            passed += 1
    print("\n%d/%d tests passed" % (passed, len(TESTS)))
    return 0 if passed == len(TESTS) else 1


if __name__ == "__main__":
    sys.exit(main())
