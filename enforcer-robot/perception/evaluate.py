#!/usr/bin/env python3
"""Score the detector against your hand labels. This produces the numbers.

    python3 evaluate.py detections.jsonl labels.csv

Prints a confusion matrix, per-class precision/recall, and the one figure
that decides whether this robot is usable:

    the false-positive rate on "phone" while you are actually working.

Every false positive there is a squirt you did not deserve. A robot that
soaks you while you work gets unplugged on day one, and no amount of clever
motion makes up for it.

Needs no model and no video -- it reads the two files the other tools wrote,
so you can re-run it in a second after changing any threshold in scene.py.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scene import Box, HeadDownCalibrator, build_scene  # noqa: E402

# Ground-truth label -> what the Scene should look like.
CLASSES = ["working", "phone", "head_down", "gone"]


def scene_to_class(s) -> str:
    """Collapse a Scene to one label, in the same priority order as mood.classify."""
    if not s.person_present:
        return "gone"
    if s.phone_visible:
        return "phone"
    if s.head_down:
        return "head_down"
    return "working"


def load_labels(path: str):
    times, labels = [], []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            times.append(float(row["t_start"]))
            labels.append(row["label"])
    return times, labels


def label_at(times, labels, t):
    """Which span covers video time t. None before the first label."""
    i = bisect.bisect_right(times, t) - 1
    return labels[i] if i >= 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("detections", help="detections.jsonl from detect.py")
    ap.add_argument("labels", help="labels.csv from label.py")
    ap.add_argument("--calib-frames", type=int, default=30)
    args = ap.parse_args()

    times, labels = load_labels(args.labels)
    if not times:
        print("No labels in %s" % args.labels, file=sys.stderr)
        return 1

    cal = HeadDownCalibrator(calib_frames=args.calib_frames)
    matrix = {t: {p: 0 for p in CLASSES} for t in CLASSES}
    skipped = 0
    n = 0

    with open(args.detections) as fh:
        for line in fh:
            rec = json.loads(line)
            boxes = [Box(**b) for b in rec["boxes"]]
            got = scene_to_class(build_scene(boxes, cal))

            truth = label_at(times, labels, rec["t"])
            # Frames before the first label, and frames spent calibrating,
            # are not scoreable -- head_down is deliberately always False
            # during calibration, so counting them would flatter the result.
            if truth is None or cal.calibrating:
                skipped += 1
                continue
            matrix[truth][got] += 1
            n += 1

    if not n:
        print("Nothing scoreable. Is the calibration window longer than the video?")
        return 1

    w = max(len(c) for c in CLASSES) + 2
    print("\nConfusion matrix   (rows = what you were doing, cols = what it said)\n")
    print(" " * w + "".join(c.rjust(w) for c in CLASSES) + "   total")
    for truth in CLASSES:
        row = matrix[truth]
        tot = sum(row.values())
        print(truth.rjust(w) + "".join(str(row[p]).rjust(w) for p in CLASSES)
              + str(tot).rjust(8))

    print("\nPer class\n")
    print("  class        precision   recall    support")
    for c in CLASSES:
        tp = matrix[c][c]
        fp = sum(matrix[t][c] for t in CLASSES if t != c)
        fn = sum(matrix[c][p] for p in CLASSES if p != c)
        prec = tp / (tp + fp) if tp + fp else float("nan")
        rec = tp / (tp + fn) if tp + fn else float("nan")
        print("  %-12s %8.3f %8.3f %10d" % (c, prec, rec, tp + fn))

    acc = sum(matrix[c][c] for c in CLASSES) / n
    print("\n  overall accuracy: %.3f  over %d frames (%d skipped)" % (acc, n, skipped))

    # ---- the number that actually matters --------------------------------
    working = sum(matrix["working"].values())
    false_phone = matrix["working"]["phone"]
    print("\n" + "=" * 62)
    if working:
        rate = false_phone / working
        print("  FALSE POSITIVES while working: %d / %d frames = %.1f%%"
              % (false_phone, working, rate * 100))
        print()
        if rate == 0:
            print("  Zero. Now check the recall on 'phone' above -- a detector")
            print("  that never fires also scores zero here.")
        elif rate < 0.02:
            print("  Under 2%%. With PHONE_DWELL=3.0s at this frame rate, isolated")
            print("  bad frames will not survive the mood machine's dwell timer.")
        elif rate < 0.10:
            print("  Borderline. Raise CONF_PHONE in scene.py, or PHONE_DWELL in")
            print("  brain/mood.py, and re-run. Re-running costs one second.")
        else:
            print("  TOO HIGH. This robot would squirt you while you work.")
            print("  Fix this before building anything else -- it is the")
            print("  difference between a demo and a device.")
    else:
        print("  No 'working' frames labelled, so no false-positive rate.")
    print("=" * 62)

    missed = matrix["phone"]["working"]
    phone_total = sum(matrix["phone"].values())
    if phone_total:
        print("\n  Missed phones: %d / %d = %.1f%% (these cost you nothing but a"
              % (missed, phone_total, missed / phone_total * 100))
        print("  slower reaction -- the dwell timer needs only 4-5 good frames)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
