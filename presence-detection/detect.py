#!/usr/bin/env python3
"""
Pass 1 — run YOLOv8n over a video file and dump raw detections to CSV.

This is the ONLY file that imports the model. Everything downstream
(state.py, score.py) works on the CSV alone, so you can re-tune the logic
a hundred times without re-running the detector, and unit-test it with no
GPU, no video and no 800MB of PyTorch installed.

That separation is deliberate — it is the same reason HapticMapper.h has
zero Arduino dependencies.

    python detect.py desk.mp4 --fps 2 --out detections.csv
"""
import argparse, csv, sys, time

# COCO class ids we care about. YOLOv8 is trained on COCO's 80 classes.
PERSON, LAPTOP, CELL_PHONE, BOOK = 0, 63, 67, 73
WANTED = [PERSON, LAPTOP, CELL_PHONE, BOOK]

NO_DETECTION = -1   # sentinel row: this sample WAS taken, nothing was found.
                    # Without it you cannot tell "empty frame" from "never sampled",
                    # and "gone" becomes unmeasurable.


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--out", default="detections.csv")
    ap.add_argument("--fps", type=float, default=2.0,
                    help="samples per second (default 2 — what a Pi Zero 2 W gives you)")
    ap.add_argument("--conf", type=float, default=0.25,
                    help="keep detections above this; filter harder later in state.py")
    ap.add_argument("--model", default="yolov8n.pt")
    ap.add_argument("--imgsz", type=int, default=640)
    args = ap.parse_args()

    import cv2
    from ultralytics import YOLO

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        sys.exit(f"could not open {args.video!r}")

    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total   = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    stride  = max(1, round(src_fps / args.fps))
    print(f"source: {src_fps:.2f} fps, {total} frames "
          f"({total/src_fps/60:.1f} min)" if total else f"source: {src_fps:.2f} fps")
    print(f"sampling every {stride} frames -> {src_fps/stride:.2f} fps effective")

    model = YOLO(args.model)

    fh = open(args.out, "w", newline="")
    w = csv.writer(fh)
    w.writerow(["frame", "t", "cls", "conf", "x1", "y1", "x2", "y2", "W", "H"])

    idx = kept = nrows = 0
    t0 = time.time()
    while True:
        # grab() advances the decoder without doing the full colour-convert
        # that retrieve() does. Skipping frames this way is much faster than
        # read()-ing every frame, and more reliable than seeking by index
        # (which lands on keyframes with some codecs).
        if not cap.grab():
            break
        if idx % stride == 0:
            ok, frame = cap.retrieve()
            if not ok:
                break
            H, W = frame.shape[:2]
            t = idx / src_fps
            res = model.predict(frame, classes=WANTED, conf=args.conf,
                                imgsz=args.imgsz, verbose=False)[0]
            if len(res.boxes) == 0:
                w.writerow([idx, f"{t:.3f}", NO_DETECTION, 0, 0, 0, 0, 0, W, H])
                nrows += 1
            else:
                for b in res.boxes:
                    x1, y1, x2, y2 = (round(v) for v in b.xyxy[0].tolist())
                    w.writerow([idx, f"{t:.3f}", int(b.cls[0]),
                                f"{float(b.conf[0]):.3f}", x1, y1, x2, y2, W, H])
                    nrows += 1
            kept += 1
            if kept % 100 == 0:
                rate = kept / (time.time() - t0)
                print(f"  {kept} samples  t={t:6.0f}s  {rate:.1f} samples/s")
        idx += 1

    cap.release()
    fh.close()
    print(f"done: {kept} samples, {nrows} rows -> {args.out} "
          f"in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
