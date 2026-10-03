#!/usr/bin/env python3
"""Tests for the Sesame client, run entirely against FakeTransport.

No robot, no WiFi, no serial port. These assert on the exact JSON that would
go over the wire, which is what lets the behaviour layer be finished before
any hardware exists.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "brain"))

from mood import Mood  # noqa: E402
from sesame import FACES, MOOD_FACE, FakeTransport, Sesame  # noqa: E402


class _Ctx:
    def __init__(self):
        self.passed = True

    def check(self, cond, what):
        if not cond:
            print("  FAILED (line %d): %s" % (sys._getframe(1).f_lineno, what))
            self.passed = False


def bot():
    t = FakeTransport(verbose=False)
    return Sesame(t, min_gap_s=0.0), t


# -- the wire format -------------------------------------------------------


def test_Walk_SendsTheRightJson():
    c = _Ctx()
    b, t = bot()
    b.walk("forward", steps=3)
    c.check(t.log == [{"cmd": "walk", "dir": "forward", "steps": 3}],
            "exact payload, got %r" % t.log)
    return c.passed


def test_Turn_RoundsAndSigns():
    c = _Ctx()
    b, t = bot()
    b.turn(-30.44)
    c.check(t.log[0] == {"cmd": "turn", "deg": -30.4}, "negative is left, 1dp")
    return c.passed


def test_Turn_ClampsInsteadOfRaising():
    c = _Ctx()
    b, t = bot()
    # Aiming code hands this whatever the pixel->degree calibration produced.
    # A bad frame should make the robot turn too far, not raise inside the
    # control loop and stop the demo.
    b.turn(999)
    b.turn(-999)
    c.check(t.log[0]["deg"] == 180.0, "clamped high")
    c.check(t.log[1]["deg"] == -180.0, "clamped low")
    return c.passed


def test_Walk_RejectsNonsense():
    c = _Ctx()
    b, _ = bot()
    for bad in ("sideways", "FORWARD", ""):
        try:
            b.walk(bad)
            c.check(False, "should have rejected direction %r" % bad)
        except ValueError:
            pass
    try:
        b.walk("forward", steps=0)
        c.check(False, "should have rejected steps=0")
    except ValueError:
        pass
    return c.passed


def test_Face_RejectsTypos():
    c = _Ctx()
    b, _ = bot()
    # A typo'd face is otherwise silently ignored by the firmware, which is
    # a very quiet bug to hunt on a robot that just looks blank.
    try:
        b.face("smugg")
        c.check(False, "should have rejected an unknown face")
    except ValueError:
        pass
    b.face("smug")
    return c.passed


# -- the mood -> face seam -------------------------------------------------


def test_ShowMood_AcceptsTheEnum():
    c = _Ctx()
    b, t = bot()
    b.show_mood(Mood.SMUG)
    c.check(t.log[0] == {"cmd": "face", "name": "smug"}, "enum in, face out")
    t.clear()
    b.show_mood("warning")
    c.check(t.log[0] == {"cmd": "face", "name": "angry"}, "string works too")
    return c.passed


def test_EveryMoodMapsToARealFace():
    c = _Ctx()
    # If someone adds a mood to mood.py and forgets the mapping here, the
    # robot silently goes neutral. Catch it in CI instead.
    for m in Mood:
        c.check(m.value in MOOD_FACE, "mood %r has a mapping" % m.value)
        c.check(MOOD_FACE.get(m.value) in FACES,
                "mood %r maps to a face Sesame knows" % m.value)
    return c.passed


# -- composite behaviours --------------------------------------------------


def test_CreepIn_IsTheWholeSequence():
    c = _Ctx()
    b, t = bot()
    b.creep_in(steps=2)
    c.check(t.cmds() == ["crouch", "walk", "face"],
            "crouch, close the distance, then glare -- got %r" % t.cmds())
    c.check(t.log[1]["steps"] == 2, "steps passed through")
    return c.passed


def test_BackOff_ReturnsToNeutral():
    c = _Ctx()
    b, t = bot()
    b.back_off()
    c.check(t.cmds() == ["walk", "stand", "face"], "retreat, stand, reset")
    c.check(t.log[0]["dir"] == "back", "backwards")
    c.check(t.log[2]["name"] == "neutral", "face resets")
    return c.passed


# -- failure handling ------------------------------------------------------


def test_FailedCommandIsCountedNotRaised():
    c = _Ctx()
    t = FakeTransport(verbose=False, fail_on={"walk"})
    b = Sesame(t, min_gap_s=0.0)
    ok = b.walk("forward")
    c.check(ok is False, "reports the failure")
    c.check(b.failures == 1, "counts it")
    return c.passed


def test_CompositeStopsAtTheFirstFailure():
    c = _Ctx()
    t = FakeTransport(verbose=False, fail_on={"crouch"})
    b = Sesame(t, min_gap_s=0.0)
    ok = b.creep_in()
    c.check(ok is False, "creep_in reports failure")
    # If crouching failed the robot is in an unknown posture; walking anyway
    # is how a quadruped falls off a desk.
    c.check(t.cmds() == ["crouch"], "did not carry on regardless, got %r" % t.cmds())
    return c.passed


def test_ContextManagerCloses():
    c = _Ctx()
    t = FakeTransport(verbose=False)
    with Sesame(t, min_gap_s=0.0) as b:
        b.stand()
    c.check(t.cmds() == ["stand"], "worked inside the with block")
    return c.passed


# -- the interlock ---------------------------------------------------------


def test_ThereIsNoFireMethod():
    c = _Ctx()
    b, _ = bot()
    # BEHAVIOURS.md keeps the pump behind the firmware interlocks on the
    # ESP32's own GPIO. If firing were reachable from this object, anything
    # holding it could soak someone -- including, eventually, an LLM.
    for name in ("fire", "squirt", "pump", "shoot"):
        c.check(not hasattr(b, name), "client must not expose %r" % name)
    return c.passed


TESTS = [
    ("Walk_SendsTheRightJson", test_Walk_SendsTheRightJson),
    ("Turn_RoundsAndSigns", test_Turn_RoundsAndSigns),
    ("Turn_ClampsInsteadOfRaising", test_Turn_ClampsInsteadOfRaising),
    ("Walk_RejectsNonsense", test_Walk_RejectsNonsense),
    ("Face_RejectsTypos", test_Face_RejectsTypos),
    ("ShowMood_AcceptsTheEnum", test_ShowMood_AcceptsTheEnum),
    ("EveryMoodMapsToARealFace", test_EveryMoodMapsToARealFace),
    ("CreepIn_IsTheWholeSequence", test_CreepIn_IsTheWholeSequence),
    ("BackOff_ReturnsToNeutral", test_BackOff_ReturnsToNeutral),
    ("FailedCommandIsCountedNotRaised", test_FailedCommandIsCountedNotRaised),
    ("CompositeStopsAtTheFirstFailure", test_CompositeStopsAtTheFirstFailure),
    ("ContextManagerCloses", test_ContextManagerCloses),
    ("ThereIsNoFireMethod", test_ThereIsNoFireMethod),
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
