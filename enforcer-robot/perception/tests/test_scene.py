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

from scene import (  # noqa: F401
    PHONE_NEEDS_WRIST,
    head_down_from_face,  # noqa: E402
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


def wrist(cx, cy):
    return Box("wrist", 1.0, cx - 14, cy - 14, cx + 14, cy + 14)


def test_Phone_InHandCounts():
    c = _Ctx()
    p = person()
    w = wrist(320, 300)
    got = phone_in_hand(p, [p, w, phone(320, 300)])
    c.check(got is not None, "a phone at the wrist is in hand")
    return c.passed


def test_Phone_OnTheDeskWithWristsVisibleIsNot():
    c = _Ctx()
    # THE failure this rule exists for. Second recording, camera aimed at the
    # desk: 131 of 311 working frames were called "phone", every one a correct
    # detection of a phone lying on the desk inside the person's box. The box
    # rule cannot tell that from a phone in a hand; a wrist can.
    p = person(200, 100, 440, 480)
    hands = [wrist(240, 300), wrist(400, 300)]
    on_desk = phone(320, 460)          # inside the box, far from both wrists
    c.check(phone_in_hand(p, [p] + hands + [on_desk]) is None,
            "a phone on the desk, away from the wrists, is not in hand")
    in_hand = phone(400, 308)          # same box, at a wrist
    c.check(phone_in_hand(p, [p] + hands + [in_hand]) is not None,
            "the same box, at a wrist, is")
    return c.passed


def test_Phone_NoWristsMeansNoOffence():
    c = _Ctx()
    # PHONE_NEEDS_WRIST: with no wrists to go on, the looser box rule is what
    # produced 42% false positives, so the frame is not judged at all. A
    # missed offence costs a slower reaction; a false one costs a soaking.
    p = person(200, 100, 440, 480)
    c.check(PHONE_NEEDS_WRIST, "the strict rule is the deployed default")
    c.check(phone_in_hand(p, [p, phone(320, 300)]) is None,
            "no wrists visible, no phone offence")
    return c.passed


def test_Phone_AcrossTheDeskDoesNot():
    c = _Ctx()
    # THE false positive that matters. Your phone is charging over there and
    # you are working. The robot must not fire.
    p = person(200, 100, 440, 480)
    far = phone(900, 460)
    c.check(phone_in_hand(p, [p, far]) is None, "a phone across the desk is not an offence")
    return c.passed


def test_Phone_HeldOutToTheSideStillCounts():
    c = _Ctx()
    # Holding it out beyond the torso is still using it -- the wrist goes
    # with the hand, so the rule follows it out of the box for free.
    p = person(200, 100, 440, 480)
    out = wrist(p.x2 + p.w * 0.20, 300)
    c.check(phone_in_hand(p, [p, out, phone(p.x2 + p.w * 0.20, 300)]) is not None,
            "a phone at a wrist outside the box still counts")
    return c.passed


def test_Phone_ReachIsScaleInvariant():
    c = _Ctx()
    # Rolling the chair back shrinks everything in frame. The reach is a
    # fraction of the person's height for exactly this reason.
    for scale in (1.0, 0.5):
        h = 380 * scale
        p = Box("person", 0.9, 200, 100, 200 + 240 * scale, 100 + h)
        w = wrist(p.cx, p.cy)
        near = phone(p.cx + h * 0.15, p.cy)
        far = phone(p.cx + h * 0.45, p.cy)
        c.check(phone_in_hand(p, [p, w, near]) is not None, "near counts at %g" % scale)
        c.check(phone_in_hand(p, [p, w, far]) is None, "far does not at %g" % scale)
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
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=10)
    hunched = person(200, 300, 440, 480)  # very squat box
    for _ in range(9):
        c.check(cal.feed(hunched) is False, "never flags during calibration")
    c.check(cal.calibrating, "still calibrating at 9 of 10 frames")
    cal.feed(hunched)
    c.check(not cal.calibrating, "baseline set on the 10th frame")
    return c.passed


def test_HeadDown_UprightIsNotFlagged():
    c = _Ctx()
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=5)
    upright = person(200, 100, 440, 480)   # aspect 380/240 = 1.58
    for _ in range(5):
        cal.feed(upright)
    c.check(cal.feed(upright) is False, "sitting the same way you calibrated")
    return c.passed


def test_HeadDown_BowedHeadIsFlagged():
    c = _Ctx()
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=5)
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
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=5)
    near = person(200, 100, 440, 480)          # 240 x 380
    for _ in range(5):
        cal.feed(near)
    far = person(280, 190, 400, 380)           # 120 x 190, same aspect
    c.check(abs(near.aspect - far.aspect) < 1e-9, "same shape, half the size")
    c.check(cal.feed(far) is False, "moving away is not slouching")
    return c.passed


def test_HeadDown_NoPersonIsNeverHeadDown():
    c = _Ctx()
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=1)
    cal.force_baseline(1.5)
    c.check(cal.feed(None) is False, "an empty chair has no posture")
    return c.passed


def test_HeadDown_MedianResistsOneBadFrame():
    c = _Ctx()
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=5)
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
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=1)
    cal.force_baseline(1.58)
    s = build_scene([person()], cal)
    c.check(s.person_present, "person seen")
    c.check(not s.phone_visible, "no phone")
    c.check(not s.head_down, "head up")
    return c.passed


def test_Scene_EmptyFrameIsAbsent():
    c = _Ctx()
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=1)
    cal.force_baseline(1.58)
    s = build_scene([], cal)
    c.check(not s.person_present, "nobody there")
    c.check(not s.phone_visible, "and therefore no phone offence")
    return c.passed


def test_Scene_RangeIsAlwaysNoneFromVideo():
    c = _Ctx()
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=1)
    cal.force_baseline(1.58)
    s = build_scene([person()], cal)
    # A video file has no rangefinder. None means "no reading", which the
    # firmware interlocks treat as out-of-band -- so replaying video can
    # never produce a scene that would authorise a shot on the real robot.
    c.check(s.range_mm is None, "no range from a video file")
    return c.passed


def test_HeadDown_ClippedBoxIsNeverJudged():
    c = _Ctx()
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=5)
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
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=3)
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
    cal = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=3)
    upright = person(200, 100, 440, 480)
    for _ in range(3):
        cal.feed(upright)
    bowed = person(200, 100 + 380 * (HEAD_DOWN_DROP + 0.05), 440, 480)
    c.check(cal.feed(bowed) is True, "head-down still works without a frame height")
    c.check(cal.clipped == 0, "and nothing is counted as clipped")
    return c.passed


def test_HeadDown_DisabledIsAlwaysSilent():
    c = _Ctx()
    # The deployed default. Measured 0.000 precision / 0.000 recall on real
    # footage, so the signal is off entirely -- not merely barred from firing.
    # Off means it cannot reach WARNING either, which is the point: a robot
    # that glares at you for 11% of your working day is still a bad robot.
    cal = HeadDownCalibrator(enabled=False, calib_frames=3)
    upright = person(200, 100, 440, 480)
    for _ in range(3):
        cal.feed(upright, frame_h=1000)
    bowed = person(200, 100 + 380 * (HEAD_DOWN_DROP + 0.05), 440, 480)
    c.check(cal.feed(bowed, frame_h=1000) is False, "head-down never fires when disabled")
    c.check(cal.baseline is None, "and no baseline is even collected")
    return c.passed


def face(x1, y1, x2, y2):
    return Box("face", 1.0, x1, y1, x2, y2)


def test_Face_MissingFaceIsHeadDown():
    c = _Ctx()
    p = person(200, 100, 440, 480)
    c.check(head_down_from_face(p, [p]) is True,
            "a person with no findable face is looking down")
    return c.passed


def test_Face_FaceHighInBoxIsUpright():
    c = _Ctx()
    p = person(200, 100, 440, 480)          # 380 tall, top at y=100
    f = face(290, 120, 350, 190)            # centre 25% down the box
    c.check(head_down_from_face(p, [p, f]) is False, "a face up top is upright")
    return c.passed


def test_Face_FaceLowInBoxIsHeadDown():
    c = _Ctx()
    p = person(200, 100, 440, 480)
    f = face(290, 380, 350, 450)            # centre ~92% down the box
    c.check(head_down_from_face(p, [p, f]) is True,
            "a face down near the desk is a bowed head the cascade still saw")
    return c.passed


def test_Face_FaceOutsideThePersonDoesNotVouch():
    c = _Ctx()
    # A face on a poster behind you, or a flatmate's, must not certify that
    # *you* are upright -- otherwise anything on the wall disables head-down.
    p = person(200, 100, 440, 480)
    f = face(700, 120, 760, 190)
    c.check(head_down_from_face(p, [p, f]) is True,
            "a face outside the person box does not count as theirs")
    return c.passed


def test_Face_NoPersonIsNeverHeadDown():
    c = _Ctx()
    c.check(head_down_from_face(None, []) is False, "an empty chair is not head-down")
    return c.passed


def test_HeadDown_FaceSourceIsNeverStuckCalibrating():
    c = _Ctx()
    # build_scene does not feed the calibrator when the source is "face", so
    # a calibrator that reports "still calibrating" forever makes evaluate.py
    # skip every frame in the run and print "Nothing scoreable".
    cal = HeadDownCalibrator(enabled=True, source="face", calib_frames=3)
    c.check(cal.calibrating is False, "face source is never calibrating")
    cal2 = HeadDownCalibrator(enabled=True, source="aspect", calib_frames=3)
    c.check(cal2.calibrating is True, "aspect source still calibrates first")
    return c.passed


TESTS = [
    ("PickPerson_NoneWhenEmpty", test_PickPerson_NoneWhenEmpty),
    ("PickPerson_IgnoresLowConfidence", test_PickPerson_IgnoresLowConfidence),
    ("PickPerson_TakesTheBiggest", test_PickPerson_TakesTheBiggest),
    ("Phone_InHandCounts", test_Phone_InHandCounts),
    ("Phone_OnTheDeskWithWristsVisibleIsNot", test_Phone_OnTheDeskWithWristsVisibleIsNot),
    ("Phone_NoWristsMeansNoOffence", test_Phone_NoWristsMeansNoOffence),
    ("Phone_ReachIsScaleInvariant", test_Phone_ReachIsScaleInvariant),
    ("Phone_AcrossTheDeskDoesNot", test_Phone_AcrossTheDeskDoesNot),
    ("Phone_HeldOutToTheSideStillCounts", test_Phone_HeldOutToTheSideStillCounts),
    ("Phone_NoPersonMeansNoPhone", test_Phone_NoPersonMeansNoPhone),
    ("Phone_LowConfidenceIgnored", test_Phone_LowConfidenceIgnored),
    ("Phone_ThresholdIsLooserThanPerson", test_Phone_ThresholdIsLooserThanPerson),
    ("HeadDown_SilentWhileCalibrating", test_HeadDown_SilentWhileCalibrating),
    ("HeadDown_UprightIsNotFlagged", test_HeadDown_UprightIsNotFlagged),
    ("HeadDown_BowedHeadIsFlagged", test_HeadDown_BowedHeadIsFlagged),
    ("HeadDown_IsScaleInvariant", test_HeadDown_IsScaleInvariant),
    ("HeadDown_NoPersonIsNeverHeadDown", test_HeadDown_NoPersonIsNeverHeadDown),
    ("HeadDown_MedianResistsOneBadFrame", test_HeadDown_MedianResistsOneBadFrame),
    ("HeadDown_DisabledIsAlwaysSilent", test_HeadDown_DisabledIsAlwaysSilent),
    ("HeadDown_FaceSourceIsNeverStuckCalibrating", test_HeadDown_FaceSourceIsNeverStuckCalibrating),
    ("Face_MissingFaceIsHeadDown", test_Face_MissingFaceIsHeadDown),
    ("Face_FaceHighInBoxIsUpright", test_Face_FaceHighInBoxIsUpright),
    ("Face_FaceLowInBoxIsHeadDown", test_Face_FaceLowInBoxIsHeadDown),
    ("Face_FaceOutsideThePersonDoesNotVouch", test_Face_FaceOutsideThePersonDoesNotVouch),
    ("Face_NoPersonIsNeverHeadDown", test_Face_NoPersonIsNeverHeadDown),
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
