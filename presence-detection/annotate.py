#!/usr/bin/env python3
"""
Optional pass — burn the boxes and the decided state onto the video so you can
watch what the detector actually saw.

This is the highest-value debugging tool here. Numbers tell you the system is
wrong 8% of the time; the video tells you it is wrong every time you reach for
your coffee. Run it before you touch a threshold.

    python annotate.py desk.mp4 detections.csv states.csv --out annotated.mp4
"""
import argparse, csv
from collections import defaultdict

NAMES = {0: "person", 63: "laptop", 67: "phone", 73: "book"}
COLOURS = {"working": (80, 200, 80), "on_phone": (60, 140, 250), "gone": (150, 150, 150)}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("detections", nargs="?", default="detections.csv")
    ap.add_argument("states",     nargs="?", default="states.csv")
    ap.add_argument("--out", default="annotated.mp4")
    ap.add_argument("--fps", type=float, default=4.0, help="output playback fps")
    args = ap.parse_args()

    import cv2

    dets = defaultdict(list)
    with open(args.detections, newline="") as fh:
        for r in csv.DictReader(fh):
            if int(r["cls"]) >= 0:
                dets[int(r["frame"])].append(r)

    states = {}
    with open(args.states, newline="") as fh:
        for r in csv.DictReader(fh):
            states[int(r["frame"])] = (r["state"], r["raw"])

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"could not open {args.video!r}")
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"),
                             args.fps, (W, H))

    idx = written = 0
    while True:
        if not cap.grab():
            break
        if idx in states:
            ok, frame = cap.retrieve()
            if not ok:
                break
            state, raw = states[idx]
            colour = COLOURS.get(state, (255, 255, 255))

            for d in dets.get(idx, []):
                x1, y1, x2, y2 = (int(float(d[k])) for k in ("x1", "y1", "x2", "y2"))
                cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
                cv2.putText(frame, f'{NAMES.get(int(d["cls"]), "?")} {d["conf"]}',
                            (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.55, colour, 2)

            cv2.rectangle(frame, (0, 0), (W, 54), (0, 0, 0), -1)
            # Showing raw alongside the committed state makes the debounce lag
            # visible — you can watch raw flip first and state follow.
            cv2.putText(frame, f"{state.upper()}   (raw: {raw})  t={idx/30:.0f}s",
                        (12, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.9, colour, 2)
            writer.write(frame)
            written += 1
        idx += 1

    cap.release()
    writer.release()
    print(f"wrote {written} annotated frames -> {args.out}")


if __name__ == "__main__":
    main()
