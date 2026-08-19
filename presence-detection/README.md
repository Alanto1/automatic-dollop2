# Presence detection on video files

Step 1 of the desk-robot project, done **before you own a Pi, a camera or a
robot.** Record yourself at a desk on your phone, run YOLOv8n over the file,
and find out how often it is wrong — while being wrong is still free.

The output you want from this stage is a number: **how often would this thing
nag me while I was actually working?** Carry that into the build.

---

## Why it is split into three programs

| File | Touches | Testable without |
|---|---|---|
| `detect.py` | YOLO, OpenCV, the video | — |
| `state.py` | nothing but a CSV | model, video, GPU |
| `score.py` | nothing but two CSVs | model, video, GPU |

All the decisions worth arguing about live in `state.py`, which is pure
standard-library Python. So you can re-tune the logic fifty times without
re-running the detector, and `test_logic.py` runs in milliseconds.

That is the same reason `HapticMapper.h` has zero Arduino dependencies. Same
lesson, different hardware: **keep the logic away from the thing that is slow
and awkward to run.**

```
desk.mp4 ──detect.py──► detections.csv ──state.py──► states.csv ──score.py──► numbers
              (YOLO)                      (pure logic)             (pure logic)
                                                │
                          truth.csv ────────────┘  (you, watching the video)
```

---

## Step 0 — install

```bash
cd presence-detection
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

This pulls PyTorch, so expect a few hundred MB. The weights (`yolov8n.pt`,
~6MB) download automatically the first time you run `detect.py`.

**Check the logic works before any of that finishes:**

```bash
python3 test_logic.py     # 33 tests, no dependencies at all
```

---

## Step 1 — record the video

20 minutes, phone propped on a shelf or a stack of books, roughly where a
robot on your desk would sit. Landscape.

Do these deliberately, and **write down the times as you go** — that is your
ground truth and it costs nothing now versus twenty minutes of scrubbing later:

- Work normally for a few minutes
- Pick up your phone and use it for 1-2 minutes — a few times, in different
  postures: in your lap, at desk height, leaning back
- Leave the frame entirely, twice, for different lengths
- Lean over a notebook while **not** on your phone. This is the case that
  breaks naive head-down detection, and you want it in the data.
- Have someone walk behind you if you can

Aim for roughly 60% working, 25% phone, 15% gone. If it is 95% working the
accuracy number will look great and mean nothing.

> **If it came off a phone, check the rotation.** OpenCV frequently ignores
> rotation metadata, so a portrait video can arrive sideways and every box will
> be wrong. Run step 2 first and look at the frame.

---

## Step 2 — look at one frame before processing 20 minutes

Never run a long job before checking a short one.

```python
import cv2
from ultralytics import YOLO

cap = cv2.VideoCapture("desk.mp4")
cap.set(cv2.CAP_PROP_POS_FRAMES, 300)      # ~10s in
ok, frame = cap.read()
print("frame:", frame.shape)               # sideways? that is your rotation bug

res = YOLO("yolov8n.pt").predict(frame, conf=0.25)[0]
for b in res.boxes:
    print(res.names[int(b.cls[0])], round(float(b.conf[0]), 2),
          [round(v) for v in b.xyxy[0].tolist()])

cv2.imwrite("check.jpg", res.plot())       # open this and actually look at it
```

You are checking three things: is the person found, is the phone found when
you are holding it, and is the frame the right way up. If the phone is never
detected at this camera distance, that changes the design — you will lean
harder on posture, and you need to know now.

---

## Step 3 — the detection pass

```bash
python detect.py desk.mp4 --fps 2 --out detections.csv
```

**Why 2 FPS.** A Pi Zero 2 W will give you roughly 1-2 FPS with YOLOv8n and
nothing else running. Testing at 30 FPS on a laptop and discovering your
thresholds need 10 FPS to work is the expensive mistake this whole step exists
to avoid. Sample at the rate you will actually have.

The script uses `cap.grab()` to skip frames and `cap.retrieve()` only on the
ones it wants — much faster than decoding everything, and more reliable than
seeking by frame index, which lands on keyframes with some codecs.

Frames with nothing detected still get a row, with `cls = -1`. Without that
sentinel you cannot tell "empty frame" from "never sampled", and **gone becomes
unmeasurable**.

---

## Step 4 — detections to states

```bash
python state.py detections.csv --out states.csv
```

Three decisions live here.

**Gone** — no person box above `person_conf`.

**On phone, via the phone box.** A phone only counts if it is *near you*. A
phone sitting on the desk in shot all day is not "on phone", so the person box
is expanded by 15% and the phone's centre must fall inside it.

**On phone, via posture.** No pose estimation — 512MB of RAM will not hold
MediaPipe Pose alongside the detector. Instead: the top of your person box
drops when your head goes down. Measured against *your own* upright baseline
and expressed as a fraction of body height, so it survives the camera moving.

The baseline is the **20th percentile of box-top across the session**, not the
median. Image `y` grows downward, so the smallest `y1` values are your
head-up frames. If you spent half the session on your phone, a median baseline
would sink to head-down and hide the very thing you are looking for.

**Then hysteresis.** A single-sample decision flickers badly. A raw state must
persist for 4 consecutive samples (6 for `gone`) before it commits.

This is the photoresistor threshold from lab manual #8, and button debouncing,
and your wristband's zone edges. Same problem every time: **a noisy signal
crossing a threshold needs sustained evidence, not an instant.**

It is not free. On the synthetic fixture, smoothing takes transitions from
**49 down to 3** — but nudges `on_phone` false positives from 0% to 1.0%,
because transitions now report a couple of samples late. 49 flips in five
minutes would make a robot twitch continuously, so the trade is obviously
right. Know that you are making it.

---

## Step 5 — watch what it saw

```bash
python annotate.py desk.mp4 detections.csv states.csv --out annotated.mp4
```

**Do this before touching a single threshold.** Numbers tell you it is wrong
8% of the time. The video tells you it is wrong every time you reach for your
coffee — which is a different problem with a different fix.

The overlay shows the committed state and the raw one together, so you can
watch `raw` flip and `state` follow a beat later. That is your debounce lag,
made visible.

---

## Step 6 — ground truth

Scrub the video and write intervals. Per-frame labelling is not worth the
hours; intervals are.

```csv
start,end,label
0,125,working
125,180,on_phone
180,240,gone
240,600,working
```

Seconds, `end` exclusive, labels exactly `working` / `on_phone` / `gone`. Gaps
are allowed — anything outside an interval is excluded from scoring, which is
the honest way to handle moments you genuinely cannot call.

---

## Step 7 — score it

```bash
python score.py states.csv truth.csv
python score.py states.csv truth.csv --column raw    # compare without smoothing
```

You get a confusion matrix, per-class precision/recall/F1, and the headline:

```
on_phone false positives: 5/480 = 1.0%
  (samples where you were NOT on your phone but it thought you were)
```

**That is the number that decides whether the robot is usable.** A missed phone
pickup is a small loss. A robot that nags you while you are concentrating gets
switched off and put in a drawer. Optimise `on_phone` *precision* over recall,
and be suspicious of any overall accuracy figure — with 60% working in the
data, "always say working" scores 60%.

---

## Step 8 — the loop

Change one thing, re-run steps 4 and 7 only. Detection does not need repeating —
that is the whole reason the CSV sits in the middle.

```bash
python state.py detections.csv --head-drop 0.14 --out states.csv && python score.py
```

| Symptom | Knob |
|---|---|
| Nags while you lean over a notebook | `--head-drop` up (0.14, 0.18) |
| Misses phone use where you stay upright | `--head-drop` down; check phone detection rate first |
| State flickers | `--commit` up (6, 8) — costs more lag |
| Slow to notice you left | `gone_samples` down in `Config` |
| Chair or coat detected as you | `--person-conf` up (0.5, 0.6) |

Record a **second** video on another day and score it with the thresholds you
tuned on the first. If the numbers collapse, you tuned to one recording rather
than to the problem. That is the single most common way projects like this
fool their authors.

---

## What to carry into the build

1. The `on_phone` false-positive rate at 2 FPS. If you cannot get it under
   ~5%, the interaction design has to change — a gentle glance rather than a
   nag — and that is a finding, not a failure.
2. Whether the phone class is detectable at your camera distance at all.
3. Your tuned thresholds, and whether they held up on the second video.
4. `state.py` itself. It is pure Python with no model dependency, so it runs
   unchanged on the Pi.

---

## Files

| File | What it does |
|---|---|
| `detect.py` | YOLOv8n over a video → `detections.csv` |
| `state.py` | detections → state timeline. All the real logic. Pure stdlib. |
| `score.py` | states + ground truth → confusion matrix and FP rate. Pure stdlib. |
| `annotate.py` | burns boxes and state onto the video |
| `make_fake.py` | synthetic fixture — exercise the pipeline with no video at all |
| `test_logic.py` | 33 tests for the logic. No dependencies. |

```bash
python3 make_fake.py
python3 state.py fake_detections.csv --out fake_states.csv
python3 score.py fake_states.csv fake_truth.csv
```

That runs the whole pipeline end to end without a camera, a model or a video —
useful for checking your environment, and as a regression test when you change
the logic.
