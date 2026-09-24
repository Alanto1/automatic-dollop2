#!/usr/bin/env python3
"""Hand-label your footage so you have a ground truth to measure against.

    python3 label.py desk.mp4 -o labels.csv

Plays the video and lets you mark spans. You are answering one question per
moment: what were you actually doing?

    w  working      at the desk, not on the phone
    p  on phone     phone in your hand
    d  head down    hunched, but no phone visible
    g  gone         not at the desk
    SPACE  pause          LEFT/RIGHT  skip 5s          q  save and quit

Writes one row per change of state, not per frame, so a 20-minute video is
maybe 40 rows and you can fix mistakes in a text editor afterwards.

This file is the boring part and it is the part that makes the project a
project. Without it you have opinions about your detector; with it you have
numbers.
"""

from __future__ import annotations

import argparse
import csv
import sys

KEYS = {ord("w"): "working", ord("p"): "phone", ord("d"): "head_down", ord("g"): "gone"}
COLOURS = {"working": (90, 200, 90), "phone": (60, 80, 240),
           "head_down": (60, 190, 240), "gone": (150, 150, 150), "?": (200, 200, 200)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("-o", "--out", default="labels.csv")
    ap.add_argument("--speed", type=float, default=4.0,
                    help="playback speed (default 4x -- you are marking spans, not frames)")
    args = ap.parse_args()

    try:
        import cv2
    except ImportError:
        print("Missing OpenCV:  pip install -r requirements.txt", file=sys.stderr)
        return 2

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print("Could not open %s" % args.video, file=sys.stderr)
        return 1

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    delay = max(1, int(1000 / (fps * args.speed)))

    spans: list[tuple[float, str]] = []
    current = "?"
    paused = False

    print(__doc__)
    while True:
        if not paused:
            ok, frame = cap.read()
            if not ok:
                break
        t = cap.get(cv2.CAP_PROP_POS_FRAMES) / fps

        view = frame.copy()
        cv2.rectangle(view, (0, 0), (view.shape[1], 46), (24, 20, 16), -1)
        cv2.putText(view, "%s   %5.1fs / %5.1fs   %s" % (
            current.upper().ljust(9), t, total / fps, "PAUSED" if paused else ""),
            (12, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOURS.get(current), 2)
        cv2.imshow("label  [w]orking [p]hone hea[d] down [g]one  SPACE=pause  q=save", view)

        k = cv2.waitKey(0 if paused else delay) & 0xFF
        if k == ord("q"):
            break
        elif k == ord(" "):
            paused = not paused
        elif k == 81:   # left arrow
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, cap.get(cv2.CAP_PROP_POS_FRAMES) - 5 * fps))
        elif k == 83:   # right arrow
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + 5 * fps)
        elif k in KEYS and KEYS[k] != current:
            current = KEYS[k]
            spans.append((round(t, 2), current))
            print("  %6.1fs  ->  %s" % (t, current))

    cap.release()
    cv2.destroyAllWindows()

    with open(args.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["t_start", "label"])
        w.writerows(spans)

    print("\nwrote %d spans to %s" % (len(spans), args.out))
    if not spans:
        print("(nothing labelled -- press w/p/d/g while it plays)")
    elif spans[0][0] > 1.0:
        print("NOTE: the first %.1fs is unlabelled and will be skipped when scoring."
              % spans[0][0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
