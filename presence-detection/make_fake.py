#!/usr/bin/env python3
"""
Generate a synthetic detections.csv + truth.csv so the pipeline can be
exercised end-to-end before you own a video, a camera or a robot.
Also useful as a regression fixture.

    python3 make_fake.py && python3 state.py fake_detections.csv --out fake_states.csv
"""
import csv, random

random.seed(7)
SRC_FPS, STRIDE = 30.0, 15          # -> 2 FPS sampling
W, H = 1280, 720
PERSON, CELL_PHONE, NO_DETECTION = 0, 67, -1

# (start_s, end_s, label)
SCRIPT = [(0, 100, "working"), (100, 160, "on_phone"),
          (160, 220, "gone"),  (220, 300, "working")]

def label_at(t):
    for s, e, l in SCRIPT:
        if s <= t < e:
            return l
    return "working"

rows = []
frame = 0
while frame / SRC_FPS < 300:
    t = frame / SRC_FPS
    lab = label_at(t)
    out = []

    if lab != "gone":
        # 3% of the time the detector simply misses a present person.
        if random.random() > 0.03:
            y1 = 100 if lab == "working" else 185
            y1 += random.gauss(0, 6)                       # jitter
            h   = 400 + random.gauss(0, 10)
            out.append([PERSON, 0.90, 200, round(y1), 400, round(y1 + h)])
            if lab == "on_phone" and random.random() < 0.55:  # phone often occluded
                out.append([CELL_PHONE, 0.55, 280, 300, 320, 360])
    else:
        # 2% spurious person detection while actually away (a chair, a coat)
        if random.random() < 0.02:
            out.append([PERSON, 0.45, 210, 110, 400, 500])

    if not out:
        rows.append([frame, f"{t:.3f}", NO_DETECTION, 0, 0, 0, 0, 0, W, H])
    else:
        for cls, conf, x1, y1, x2, y2 in out:
            rows.append([frame, f"{t:.3f}", cls, f"{conf:.3f}", x1, y1, x2, y2, W, H])
    frame += STRIDE

with open("fake_detections.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["frame","t","cls","conf","x1","y1","x2","y2","W","H"])
    w.writerows(rows)

with open("fake_truth.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["start","end","label"])
    w.writerows(SCRIPT)

print(f"wrote fake_detections.csv ({len(rows)} rows) and fake_truth.csv")
