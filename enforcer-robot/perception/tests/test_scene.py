#!/usr/bin/env python3
"""Desktop unit tests for scene.py -- no video, no model, no camera.

Same convention as brain/tests/test_mood.py and the wristband's
test_haptic_mapper.cpp: bare python3, a local `passed` flag, no framework.

Every box below is hand-written, so these run in milliseconds and tell you
whether the *geometry rules* are right, independently of whether YOLO is
having a good day.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))

from scene import (  # noqa: E402
    CONF_PERSON,
    CONF_PHONE,
    HEAD_DOWN_DROP,
    Box,
    HeadDownCalibrator,
    build_scene,
    phone_in_hand,
    pick_person,
)


class _Ctx:
    def __init__(self):
        self.passed = True

    def check(self, cond, what):
        if not cond:
            print("  FAILED (line %d): %s" % (sys._getframe(1).f_lineno, what))
            self.passed = False


def person(x1=200, y1=100, x2=440, y2=480, conf=0.9):
    return Box("person", conf, x1, y1, x2, y2)


def phone(cx, cy, conf=0.6, size=30):
    return Box("cell phone", conf, cx - size / 2, cy - size / 2,
               cx + size / 2, cy + size / 2)


# -- picking the person ----------------------------------------------------


def test_PickPerson_NoneWhenEmpty():
    c = _Ctx()
    c.check(pick_person([]) is None, "empty frame")
    c.check(pick_person([phone(300, 300)]) is None, "a phone alone is not a person")
    return c.passed


def test_PickPerson_IgnoresLowConfidence():
    c = _Ctx()
    faint = person(conf=CONF_PERSON - 0.01)
    c.check(pick_person([faint]) is None, "below the person threshold")
    solid = person(conf=CONF_PERSON)
    c.check(pick_person([solid]) is not None, "exactly at the threshold counts")
    return c.passed


def test_PickPerson_TakesTheBiggest():
    c = _Ctx()
    # Someone walking past a doorway behind you is smaller than you are.
    at_desk = person(200, 100, 440, 480)
    passer_by = person(600, 150, 660, 330)
    got = pick_person([passer_by, at_desk])
    c.check(got is at_desk, "the person at the desk wins, not the first listed")
    return c.passed


# -- the phone rule --------------------------------------------------------


def test_Phone_InHandCounts():
    c = _Ctx()
    p = person()
    got = phone_in_hand(p, [p, phone(320, 300)])
    c.check(got is not None, "phone inside the person's box is theirs")
    return c.passed


def test_Phone_AcrossTheDeskDoesNot():
    c = _Ctx()
    # THE false positive that matters. Your phone is charging over there and
    # you are working. The robot must not fire.
    p = person(200, 100, 440, 480)
    far = phone(900, 460)
    c.check(phone_in_hand(p, [p, far]) is None, "a phone across the desk is not an offence")
    return c.passed


def test_Phone_JustOutsideTheBoxStillCounts():
    c = _Ctx()
    # Holding it out to the side is still using it, so the box is padded.
    p = person(200, 100, 440, 480)
    just_outside = phone(p.x2 + p.w * 0.10, 300)
    c.check(phone_in_hand(p, [p, just_outside]) is not None,
            "held just outside the box still counts")
    way_outside = phone(p.x2 + p.w * 0.40, 300)
    c.check(phone_in_hand(p, [p, way_outside]) is None, "but not way outside")
    return c.passed


def test_Phone_NoPersonMeansNoPhone():
    c = _Ctx()
    c.check(phone_in_hand(None, [phone(300, 300)]) is None,
            "a phone with nobody holding it is not an offence")
    return c.passed


def test_Phone_LowConfidenceIgnored():
    c = _Ctx()
    p = person()
    faint = phone(320, 300, conf=CONF_PHONE - 0.01)
    c.check(phone_in_hand(p, [p, faint]) is None, "below the phone threshold")
    return c.passed


def test_Phone_ThresholdIsLooserThanPerson():
    c = _Ctx()
    # Deliberate: phones are small, blurry and half-occluded by a hand. Being
    # strict here builds a detector that never fires. The mood machine's
    # dwell timers are what reject the noise.
    c.check(CONF_PHONE < CONF_PERSON, "phone threshold is the looser one")
    return c.passed


# -- head down -------------------------------------------------------------


def test_HeadDown_SilentWhileCalibrating():
    c = _Ctx()
    cal = HeadDownCalibrator(calib_frames=10)
    hunched = person(200, 300, 440, 480)  # very squat box
    for _ in range(9):
        c.check(cal.feed(hunched) is False, "never flags during calibration")
    c.check(cal.calibrating, "still calibrating at 9 of 10 frames")
    cal.feed(hunched)
    c.check(not cal.calibrating, "baseline set on the 10th frame")
    return c.passed


def test_HeadDown_UprightIsNotFlagged():
    c = _Ctx()
    cal = HeadDownCalibrator(calib_frames=5)
    upright = person(200, 100, 440, 480)   # aspect 380/240 = 1.58
    for _ in range(5):
        cal.feed(upright)
    c.check(cal.feed(upright) is False, "sitting the same way you calibrated")
    return c.passed


def test_HeadDown_BowedHeadIsFlagged():
    c = _Ctx()
    cal = HeadDownCalibrator(calib_frames=5)
    upright = person(200, 100, 440, 480)
    for _ in range(5):
        cal.feed(upright)
    # Head bows: the top of the box drops, the desk pins the bottom.
    bowed = person(200, 100 + 380 * (HEAD_DOWN_DROP + 0.05), 440, 480)
    c.check(cal.feed(bowed) is True, "a squatter box than baseline reads as head-down")
    return c.passed


def test_HeadDown_IsScaleInvariant():
    c = _Ctx()
    # Rolling the chair back makes you smaller in frame without changing your
    # posture. Aspect ratio is used precisely so this does not read as an
    # offence -- with a raw top-edge test, it would.
    cal = HeadDownCalibrator(calib_frames=5)
    near = person(200, 100, 440, 480)          # 240 x 380
    for _ in range(5):
        cal.feed(near)
    far = person(280, 190, 400, 380)           # 120 x 190, same aspect
    c.check(abs(near.aspect - far.aspect) < 1e-9, "same shape, half the size")
    c.check(cal.feed(far) is False, "moving away is not slouching")
    return c.passed


def test_HeadDown_NoPersonIsNeverHeadDown():
    c = _Ctx()
    cal = HeadDownCalibrator(calib_frames=1)
    cal.force_baseline(1.5)
    c.check(cal.feed(None) is False, "an empty chair has no posture")
    return c.passed


def test_HeadDown_MedianResistsOneBadFrame():
    c = _Ctx()
    cal = HeadDownCalibrator(calib_frames=5)
    upright = person(200, 100, 440, 480)
    cal.feed(upright)
    cal.feed(upright)
    cal.feed(person(200, 400, 440, 480))  # YOLO clipped the box badly
    cal.feed(upright)
    cal.feed(upright)
    c.check(abs(cal.baseline - upright.aspect) < 1e-9,
            "one garbage frame does not move the baseline, got %.3f" % cal.baseline)
    return c.passed


# -- the whole frame -------------------------------------------------------


def test_Scene_WorkingLooksLikeWorking():
    c = _Ctx()
    cal = HeadDownCalibrator(calib_frames=1)
    cal.force_baseline(1.58)
    s = build_scene([person()], cal)
    c.check(s.person_present, "person seen")
    c.check(not s.phone_visible, "no phone")
    c.check(not s.head_down, "head up")
    return c.passed


def test_Scene_EmptyFrameIsAbsent():
    c = _Ctx()
    cal = HeadDownCalibrator(calib_frames=1)
    cal.force_baseline(1.58)
    s = build_scene([], cal)
    c.check(not s.person_present, "nobody there")
    c.check(not s.phone_visible, "and therefore no phone offence")
    return c.passed


def test_Scene_RangeIsAlwaysNoneFromVideo():
    c = _Ctx()
    cal = HeadDownCalibrator(calib_frames=1)
    cal.force_baseline(1.58)
    s = build_scene([person()], cal)
    # A video file has no rangefinder. None means "no reading", which the
    # firmware interlocks treat as out-of-band -- so replaying video can
    # never produce a scene that would authorise a shot on the real robot.
    c.check(s.range_mm is None, "no range from a video file")
    return c.passed


def test_HeadDown_ClippedBoxIsNeverJudged():
    c = _Ctx()
    cal = HeadDownCalibrator(calib_frames=5)
    upright = person(200, 100, 440, 480)
    for _ in range(5):
        cal.feed(upright, frame_h=1000)
    # A box that runs off the top of the frame is squat enough to trip the
    # threshold, but it is squat because the head is out of shot -- not
    # because it is bowed. Measured on real footage this was 26% of frames.
    clipped = person(200, 0, 440, 300)
    c.check(clipped.aspect < cal.baseline * (1.0 - HEAD_DOWN_DROP),
            "the clipped box would trip the threshold on aspect alone")
    c.check(cal.feed(clipped, frame_h=1000) is False,
            "but it is not judged, because a clipped box means nothing")
    c.check(cal.clipped == 1, "and it is counted, so evaluate.py can say so")
    return c.passed


def test_HeadDown_ClippedFramesStayOutOfTheBaseline():
    c = _Ctx()
    cal = HeadDownCalibrator(calib_frames=3)
    upright = person(200, 100, 440, 480)
    cal.feed(person(200, 0, 440, 300), frame_h=1000)   # clipped, must not count
    for _ in range(3):
        cal.feed(upright, frame_h=1000)
    c.check(cal.baseline == upright.aspect,
            "a clipped frame does not drag the posture baseline down")
    return c.passed


def test_HeadDown_UnknownFrameHeightKeepsOldBehaviour():
    c = _Ctx()
    # frame_h is optional: callers that do not know the frame size (the unit
    # tests, and any caller written before this guard existed) must still work.
    cal = HeadDownCalibrator(calib_frames=3)
    upright = person(200, 100, 440, 480)
    for _ in range(3):
        cal.feed(upright)
    bowed = person(200, 100 + 380 * (HEAD_DOWN_DROP + 0.05), 440, 480)
    c.check(cal.feed(bowed) is True, "head-down still works without a frame height")
    c.check(cal.clipped == 0, "and nothing is counted as clipped")
    return c.passed


TESTS = [
    ("PickPerson_NoneWhenEmpty", test_PickPerson_NoneWhenEmpty),
    ("PickPerson_IgnoresLowConfidence", test_PickPerson_IgnoresLowConfidence),
    ("PickPerson_TakesTheBiggest", test_PickPerson_TakesTheBiggest),
    ("Phone_InHandCounts", test_Phone_InHandCounts),
    ("Phone_AcrossTheDeskDoesNot", test_Phone_AcrossTheDeskDoesNot),
    ("Phone_JustOutsideTheBoxStillCounts", test_Phone_JustOutsideTheBoxStillCounts),
    ("Phone_NoPersonMeansNoPhone", test_Phone_NoPersonMeansNoPhone),
    ("Phone_LowConfidenceIgnored", test_Phone_LowConfidenceIgnored),
    ("Phone_ThresholdIsLooserThanPerson", test_Phone_ThresholdIsLooserThanPerson),
    ("HeadDown_SilentWhileCalibrating", test_HeadDown_SilentWhileCalibrating),
    ("HeadDown_UprightIsNotFlagged", test_HeadDown_UprightIsNotFlagged),
    ("HeadDown_BowedHeadIsFlagged", test_HeadDown_BowedHeadIsFlagged),
    ("HeadDown_IsScaleInvariant", test_HeadDown_IsScaleInvariant),
    ("HeadDown_NoPersonIsNeverHeadDown", test_HeadDown_NoPersonIsNeverHeadDown),
    ("HeadDown_MedianResistsOneBadFrame", test_HeadDown_MedianResistsOneBadFrame),
    ("HeadDown_ClippedBoxIsNeverJudged", test_HeadDown_ClippedBoxIsNeverJudged),
    ("HeadDown_ClippedFramesStayOutOfTheBaseline", test_HeadDown_ClippedFramesStayOutOfTheBaseline),
    ("HeadDown_UnknownFrameHeightKeepsOldBehaviour", test_HeadDown_UnknownFrameHeightKeepsOldBehaviour),
    ("Scene_WorkingLooksLikeWorking", test_Scene_WorkingLooksLikeWorking),
    ("Scene_EmptyFrameIsAbsent", test_Scene_EmptyFrameIsAbsent),
    ("Scene_RangeIsAlwaysNoneFromVideo", test_Scene_RangeIsAlwaysNoneFromVideo),
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
