#!/usr/bin/env python3
"""Run YOLOv8n over a video file at the frame rate a Pi Zero 2 W can manage.

    python3 detect.py desk.mp4 --fps 2 -o detections.jsonl
    python3 detect.py desk.mp4 --crop 0.72 -o detections.jsonl   # narrow the lens
    python3 detect.py desk.mp4 --face -o detections.jsonl        # head-down signal

This is the dirty half of perception: it owns the model and OpenCV, and it is
the only file you have to rewrite when you move to the Pi. It writes one JSON
object per sampled frame, so everything downstream (scene.py, evaluate.py,
replay.py) works on a small text file instead of re-running the model.

Why sample instead of processing every frame: a Pi Zero 2 W gives 1-2 FPS on
YOLOv8n. Tuning against 30 FPS laptop footage would produce timings that fall
apart on the robot. Sample at the rate you will actually have.
"""

from __future__ import annotations

import argparse
import json
import sys
import time

# The two classes we care about, out of COCO's 80.
KEEP = {"person", "cell phone"}

# --face adds a third, from OpenCV's Haar cascade rather than the model.
# Frontal-face cascades fail when the head turns or bows, and that failure is
# the signal: a person in frame with no findable face is looking down.
FACE_CASCADE = "haarcascade_frontalface_default.xml"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", help="path to your recorded desk footage")
    ap.add_argument("-o", "--out", default="detections.jsonl")
    ap.add_argument("--fps", type=float, default=2.0,
                    help="frames per second to SAMPLE (default 2, what a Pi Zero gives)")
    ap.add_argument("--imgsz", type=int, default=320,
                    help="model input size (default 320, what the Pi will run)")
    ap.add_argument("--crop", type=float, default=1.0, metavar="FRAC",
                    help="centre-crop to this fraction of the frame, to narrow "
                         "your phone's lens to the robot's 53.5 deg one. "
                         "0.72 takes a typical ~70 deg phone camera to 53.5. "
                         "Default 1.0 = no crop")
    ap.add_argument("--model", default="yolov8n.pt")
    ap.add_argument("--conf", type=float, default=0.20,
                    help="floor confidence; scene.py applies the real per-class ones")
    ap.add_argument("--face", action="store_true",
                    help="also run a Haar face cascade and emit 'face' boxes. "
                         "Costs a few ms/frame and gives scene.py a head-down "
                         "signal that looks at the head, unlike box aspect ratio")
    ap.add_argument("--show", action="store_true", help="preview window while running")
    args = ap.parse_args()

    try:
        import cv2
        from ultralytics import YOLO
    except ImportError as e:
        print("Missing dependency: %s" % e, file=sys.stderr)
        print("\n  pip install -r requirements.txt\n", file=sys.stderr)
        return 2

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print("Could not open %s" % args.video, file=sys.stderr)
        return 1

    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    stride = max(1, round(src_fps / args.fps))

    print("source     : %s" % args.video)
    print("source fps : %.1f  (%d frames, %.1f min)"
          % (src_fps, total, total / src_fps / 60 if src_fps else 0))
    print("sampling   : every %d frames -> %.2f FPS" % (stride, src_fps / stride))
    print("model      : %s @ %dpx" % (args.model, args.imgsz))
    if not 0.05 < args.crop <= 1.0:
        print("--crop must be in (0.05, 1.0]", file=sys.stderr)
        return 1
    if args.crop < 1.0:
        import math
        # Report the FOV this crop implies, assuming a ~70 deg source lens, so
        # the number in the log can be checked against RPIZ-CAM-15's 53.5.
        fov = 2 * math.degrees(math.atan(args.crop * math.tan(math.radians(70) / 2)))
        print("crop       : centre %.2f -> ~%.1f deg (from a ~70 deg phone lens)"
              % (args.crop, fov))
    print()

    model = YOLO(args.model)
    names = model.names

    cascade = None
    if args.face:
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + FACE_CASCADE)
        if cascade.empty():
            print("Could not load %s" % FACE_CASCADE, file=sys.stderr)
            return 2
        print("face       : %s" % FACE_CASCADE)

    kept = 0
    idx = 0
    t_start = time.time()
    infer_total = 0.0

    with open(args.out, "w") as fh:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % stride:
                idx += 1
                continue

            if args.crop < 1.0:
                h, w = frame.shape[:2]
                ch, cw = int(h * args.crop), int(w * args.crop)
                y0, x0 = (h - ch) // 2, (w - cw) // 2
                frame = frame[y0:y0 + ch, x0:x0 + cw]

            t0 = time.time()
            res = model.predict(frame, imgsz=args.imgsz, conf=args.conf, verbose=False)[0]
            infer_total += time.time() - t0

            boxes = []
            for b in res.boxes:
                label = names[int(b.cls[0])]
                if label not in KEEP:
                    continue
                x1, y1, x2, y2 = (float(v) for v in b.xyxy[0])
                boxes.append({"label": label, "conf": round(float(b.conf[0]), 3),
                              "x1": round(x1, 1), "y1": round(y1, 1),
                              "x2": round(x2, 1), "y2": round(y2, 1)})

            if cascade is not None:
                # Downscaled to 640 wide: Haar is the slow part otherwise, and
                # a face big enough to matter here survives the reduction.
                fh_, fw_ = frame.shape[:2]
                k = 640.0 / fw_ if fw_ > 640 else 1.0
                small = cv2.resize(frame, None, fx=k, fy=k) if k < 1.0 else frame
                gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                for (fx, fy, fw2, fh2) in cascade.detectMultiScale(gray, 1.15, 5,
                                                                   minSize=(24, 24)):
                    boxes.append({"label": "face", "conf": 1.0,
                                  "x1": round(fx / k, 1), "y1": round(fy / k, 1),
                                  "x2": round((fx + fw2) / k, 1),
                                  "y2": round((fy + fh2) / k, 1)})

            # `t` is video time, not wall time. Everything downstream is
            # driven by it, so a slow laptop cannot distort the timings.
            fh.write(json.dumps({
                "frame": idx,
                "t": round(idx / src_fps, 3),
                "h": frame.shape[0],
                "w": frame.shape[1],
                "boxes": boxes,
            }) + "\n")
            kept += 1

            if args.show:
                cv2.imshow("detect", res.plot())
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            if kept % 50 == 0:
                print("  %d frames..." % kept, end="\r", flush=True)
            idx += 1

    cap.release()
    if args.show:
        cv2.destroyAllWindows()

    wall = time.time() - t_start
    print("\nwrote %d frames to %s in %.1fs" % (kept, args.out, wall))
    if kept:
        ms = infer_total / kept * 1000
        print("inference: %.0f ms/frame on this laptop = %.1f FPS" % (ms, 1000 / ms))
        print("NOTE: a Pi Zero 2 W will be roughly 10-20x slower than this.")
        print("      Expect ~1-2 FPS there, which is what --fps already assumes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
