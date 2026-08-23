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

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "brain"))

from mood import CLEAR_GRACE, DWELL, Offence, can_ever_fire  # noqa: E402

# Ground-truth label -> what the Scene should look like.
CLASSES = ["working", "phone", "head_down", "gone"]

# The offences that can actually reach STRIKE, straight from the mood machine
# rather than restated here, so the two can never drift apart.
FIREABLE = [c for c in CLASSES
            if any(o.value == c and can_ever_fire(o) for o in Offence)]


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
    t_first = t_last = None
    n_rec = 0

    with open(args.detections) as fh:
        for line in fh:
            rec = json.loads(line)
            if t_first is None:
                t_first = rec["t"]
            t_last = rec["t"]
            n_rec += 1
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

    span = (t_last - t_first) if t_last is not None else 0.0
    sample_fps = (n_rec - 1) / span if span > 0 else 0.0
    DWELL_FRAMES = {o.value: max(1, round(DWELL[o] * sample_fps))
                    for o in Offence if o in DWELL and sample_fps}

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
    #
    # Every offence mood.can_ever_fire() accepts counts here, not just phone.
    # head_down escalates to STRIKE exactly like phone does, so calling a
    # working frame head_down is a squirt you did not deserve in precisely
    # the same way -- and there are usually far more of them, because leaning
    # toward a screen and bowing your head look alike to a bounding box.
    working = sum(matrix["working"].values())
    per_offence = {c: matrix["working"][c] for c in FIREABLE}
    false_fire = sum(per_offence.values())
    print("\n" + "=" * 62)
    if working:
        rate = false_fire / working
        print("  FALSE POSITIVES while working: %d / %d frames = %.1f%%"
              % (false_fire, working, rate * 100))
        print("    " + "  ".join("%s %d (%.1f%%)" % (c, v, v / working * 100)
                                 for c, v in per_offence.items()))
        print()
        if rate == 0:
            print("  Zero. Now check the recall on the fireable classes above --")
            print("  a detector that never fires also scores zero here.")
        elif rate < 0.02:
            print("  Under 2%%. With PHONE_DWELL=3.0s at this frame rate, isolated")
            print("  bad frames will not survive the mood machine's dwell timer.")
        elif rate < 0.10:
            print("  Borderline. Tighten whichever class dominates the line above:")
            print("  CONF_PHONE / PHONE_NEAR_PAD, or HEAD_DOWN_DROP, in scene.py.")
            print("  Re-running this costs one second -- no model, no video.")
        else:
            print("  TOO HIGH. This robot would squirt you while you work.")
            print("  Fix this before building anything else -- it is the")
            print("  difference between a demo and a device.")
    else:
        print("  No 'working' frames labelled, so no false-positive rate.")
    print("=" * 62)

    # ---- recall, against what the dwell timer actually needs --------------
    for c in FIREABLE:
        support = sum(matrix[c].values())
        if not support:
            continue
        hit = matrix[c][c]
        rec = hit / support
        need = DWELL_FRAMES.get(c)
        print("\n  Missed %s: %d / %d = %.1f%%"
              % (c, support - hit, support, (1 - rec) * 100))
        if need and rec >= 0.5:
            print("  Per-frame recall %.0f%% still reaches STRIKE: the dwell needs" % (rec * 100))
            print("  ~%d frames and CLEAR_GRACE=%.1fs bridges the gaps." % (need, CLEAR_GRACE))
        elif need:
            print("  ⚠ Per-frame recall is only %.0f%%. The dwell needs ~%d frames"
                  % (rec * 100, need))
            print("  held together across gaps of under CLEAR_GRACE=%.1fs, and at" % CLEAR_GRACE)
            print("  this hit rate the offence keeps clearing before it gets there.")
            print("  This is not 'a slower reaction' -- it may never fire at all.")
            print("  Confirm with replay.py: SHOTS FIRED is the honest answer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
