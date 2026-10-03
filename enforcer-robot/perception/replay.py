#!/usr/bin/env python3
"""Run detections through the mood machine. The whole software loop, offline.

    python3 replay.py detections.jsonl
    python3 replay.py detections.jsonl --video desk.mp4 --out annotated.mp4

This is the payoff: real footage of you -> YOLO -> Scene -> mood -> would it
have fired. No Pi, no camera, no robot, no water. Every shot it reports is a
shot the real robot would have taken, and you can watch it happen.

With --video it burns the mood onto the frames, which is the single most
useful thing to have on a laptop at a competition table when the robot is
between demos.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "brain"))

from mood import MoodMachine, Mood, post_strike  # noqa: E402
from scene import Box, HeadDownCalibrator, build_scene  # noqa: E402

BGR = {
    Mood.CHILL: (196, 216, 79),
    Mood.SUSPICIOUS: (78, 193, 242),
    Mood.WARNING: (78, 146, 242),
    Mood.STRIKE: (78, 85, 242),
    Mood.SMUG: (240, 140, 185),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("detections")
    ap.add_argument("--video", help="original footage, to render an annotated copy")
    ap.add_argument("--out", default="annotated.mp4")
    ap.add_argument("--calib-frames", type=int, default=30)
    args = ap.parse_args()

    records = [json.loads(l) for l in open(args.detections)]
    if not records:
        print("No detections in %s" % args.detections, file=sys.stderr)
        return 1

    cal = HeadDownCalibrator(calib_frames=args.calib_frames)
    machine = MoodMachine()
    decisions = {}
    shots = []
    last = None

    for rec in records:
        boxes = [Box(**b) for b in rec["boxes"]]
        scene = build_scene(boxes, cal, rec.get("h"))
        # The clock is VIDEO time, not wall time. A slow laptop must not be
        # able to change what the robot would have decided.
        d = machine.update(scene, rec["t"])
        if d.should_fire:
            shots.append(rec["t"])
            post_strike(machine, rec["t"])  # the real robot confirms first
        decisions[rec["frame"]] = d

        key = (d.mood, d.reason)
        if key != last:
            print("%7.1fs  %-11s %-10s %s"
                  % (rec["t"], d.mood.value.upper(), d.offence.value, d.reason))
            last = key

    span = records[-1]["t"] - records[0]["t"]
    print("\n%d frames over %.1f min at %.2f FPS"
          % (len(records), span / 60, len(records) / span if span else 0))
    print("SHOTS FIRED: %d%s" % (len(shots),
          ("  at " + ", ".join("%.1fs" % t for t in shots)) if shots else ""))
    if not shots:
        print("(none -- either you behaved, or the thresholds are too forgiving)")

    if not args.video:
        return 0

    try:
        import cv2
    except ImportError:
        print("\nOpenCV needed for --video:  pip install -r requirements.txt",
              file=sys.stderr)
        return 2

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print("Could not open %s" % args.video, file=sys.stderr)
        return 1
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    srcW = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    srcH = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # detect.py --crop means the boxes are in cropped coordinates. Each record
    # carries the frame size they were measured against, so match it here or
    # every rectangle lands in the wrong place.
    W, H = records[0].get("w", srcW), records[0].get("h", srcH)
    if (W, H) != (srcW, srcH):
        if W > srcW or H > srcH:
            print("detections are %dx%d but %s is %dx%d -- wrong video?"
                  % (W, H, args.video, srcW, srcH), file=sys.stderr)
            return 1
        print("cropping %dx%d -> %dx%d to match the detections"
              % (srcW, srcH, W, H))
    x0, y0 = (srcW - W) // 2, (srcH - H) // 2

    writer = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))

    boxes_by_frame = {r["frame"]: r["boxes"] for r in records}
    held = None
    held_boxes = []
    idx = 0
    print("\nrendering %s ..." % args.out)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if (W, H) != (srcW, srcH):
            frame = frame[y0:y0 + H, x0:x0 + W]
        if idx in decisions:                 # hold the last decision between
            held = decisions[idx]            # sampled frames, exactly as the
            held_boxes = boxes_by_frame[idx] # robot does between inferences
        if held is not None:
            col = BGR[held.mood]
            for b in held_boxes:
                cv2.rectangle(frame, (int(b["x1"]), int(b["y1"])),
                              (int(b["x2"]), int(b["y2"])), col, 2)
                cv2.putText(frame, "%s %.2f" % (b["label"], b["conf"]),
                            (int(b["x1"]), int(b["y1"]) - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 1)
            cv2.rectangle(frame, (0, 0), (W, 64), (24, 20, 16), -1)
            cv2.putText(frame, "%s  %s" % (held.mood.value.upper(), held.reason),
                        (14, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, col, 2)
            cv2.putText(frame, "%s held %.1fs" % (held.offence.value, held.held_s),
                        (14, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (170, 170, 170), 1)
            if held.should_fire:
                cv2.rectangle(frame, (0, 0), (W, H), BGR[Mood.STRIKE], 14)
        writer.write(frame)
        idx += 1

    cap.release()
    writer.release()
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
