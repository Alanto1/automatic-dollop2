# perception/ — the detector, on video files

**No Pi, no camera, no robot.** Your laptop and your phone's camera, today.

This is the Week 6 work pulled forward, because the Pi Zero 2 W is sold out
until 25 September and there is no reason to wait for it. When the board
arrives, only `detect.py` changes.

```
detect.py    video  -> detections.jsonl     (owns YOLO + OpenCV)
label.py     video  -> labels.csv           (you, pressing keys)
scene.py     boxes  -> Scene                (pure logic, 18 tests)
evaluate.py  both   -> confusion matrix + the false-positive rate
replay.py    detections -> moods, and an annotated video
```

---

## Step 0 — install (5 min)

```bash
cd enforcer-robot/perception
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Check the geometry rules pass before you record anything. This needs no
model, no video, and no network:

```bash
./tests/run_tests.sh          # 18/18 tests passed
```

## Step 1 — record ~20 minutes (30 min)

Phone on a stack of books, roughly where the robot will stand: **~10 cm above
the desk, 50–80 cm from you, pointing at your upper body.** Record yourself
actually working, and make sure the footage contains all four things:

| Do this | For how long | Why |
|---|---|---|
| Work normally | ~10 min | This is the false-positive test set. Most of the video |
| Pick up your phone | 6–8 separate times | Vary it: one hand, two hands, held low, held up |
| Put the phone on the desk, in shot, and keep working | ~2 min | **The single most important clip.** A phone visible but not in use must not fire |
| Lean in and hunch over paper | 3–4 times | head-down, no phone |
| Leave and come back | 3–4 times | absent |

⚠️ **Sit normally for the first 15 seconds.** That is the posture calibration
window, and a hunched calibration means head-down never triggers.

⚠️ **Crop the footage to 53.5°** to match the real camera (`RPIZ-CAM-15`).
Your phone is much wider. If your head falls outside a 53.5° crop at your
real desk distance, the camera mount has to go higher — and you need to know
that before Week 4 restyles the shell.

`detect.py --crop` does this for you — no ffmpeg, no re-encode, no second
copy of the file. See Step 2.

### ⚠️ Measured: head-down does not work, and the crop makes everything worse

First real recording — 10.8 min, 2 FPS, hand-labelled — scored like this:

| | uncropped | `--crop 0.72` (53.5°) |
|---|---|---|
| overall accuracy | **0.838** | 0.696 |
| phone precision | **0.897** | 0.233 |
| phone recall | **0.321** | 0.086 |
| head-down precision | 0.000 | 0.039 |
| false strikes while working | 11.4% | 27.5% |

Two things follow, and both are now in the code:

- **head-down is off as a firing offence** (`HEAD_DOWN_CAN_FIRE` in
  `brain/mood.py`). Zero true positives at the framing the robot will use. A
  bounding box cannot separate "bowed over a phone" from "leaning toward a
  monitor" — both shorten the box identically, and the second is what working
  looks like. It still escalates to WARNING, so the robot gets suspicious and
  taunts; it just may not shoot. **With it off, false strikes fall to 0.3%.**
- **53.5° costs more than it saves at a normal desk.** Everything got worse
  under the crop, phone precision most of all. The lens is not the problem —
  the framing is. Raise the camera and sit further back before concluding the
  camera choice was wrong.

**Which phone the crop threw away is the useful part.** Watching the footage:
a phone lying on the desk stayed inside the 53.5° crop, and a phone *held in
the hand* fell outside it — raised, off to one side, straight through the
crop boundary. So the narrow lens kept the phone that must never fire and
discarded the one that must. That inverts the framing requirement:

> The camera has to see **the zone where hands hold a phone**, not just the
> head and torso. Same zone BEHAVIOURS.md already aims the water at — the
> hands on the desk, never the torso.

**And head-down failed for a reason no threshold reaches.** The calibration
window caught a straighter posture than the real working one, so every
working frame sat below baseline. For this desk, "working" and "head down"
are the same box shape. That is not a constant that needs moving; it is a
signal that is not there.

Re-measure both after the mount goes higher. If head-down earns its precision
back, flip the constant and put both numbers in the writeup.

## Step 2 — run the detector (10 min)

```bash
python3 detect.py desk.mp4 --fps 2 --crop 0.72 -o detections.jsonl
```

`--crop 0.72` centre-crops each frame before inference, which takes a typical
~70° phone camera down to the 53.5° the robot will have:

```
crop = tan(53.5/2) / tan(70/2) = 0.504 / 0.700 = 0.72
```

Substitute your phone's real horizontal FOV if you know it. The script prints
the resulting angle so you can check it against 53.5. The crop is centred, so
the boxes it writes are already in cropped coordinates and `scene.py` needs no
adjustment — and `replay.py` reads the frame size back out of the detections
and crops the video to match, so the overlay lines up either way.

Run it uncropped the first time if you like. Numbers measured through a wider
lens are still real numbers, and you can re-run with `--crop` in a minute to
see what the narrower lens costs you.

The first run downloads `yolov8n.pt` (~6 MB). `--fps 2` samples every 15th
frame of 30 FPS footage — **that is deliberate**. A Pi Zero 2 W gives 1–2 FPS,
and thresholds tuned against 30 FPS laptop footage fall apart on the robot.

Add `--show` to watch it work. The script prints its inference speed and
reminds you the Pi will be 10–20× slower.

## Step 3 — label it (20 min, boring, essential)

```bash
python3 label.py desk.mp4 -o labels.csv
```

It plays at 4× and you hold down a key for what you were doing:
**w**orking · **p**hone · hea**d** down · **g**one. `SPACE` pauses, arrows
skip 5 s, `q` saves.

It writes one row per *change*, so 20 minutes is ~40 rows and you can fix
mistakes in a text editor.

This step is what separates having opinions about your detector from having
numbers about it.

## Step 4 — get your numbers (1 min)

```bash
python3 evaluate.py detections.jsonl labels.csv
```

Confusion matrix, precision/recall, and the figure that decides everything:

```
  FALSE POSITIVES while working: 3 / 412 frames = 0.7%
```

Read it like this:

| Rate | What to do |
|---|---|
| **0%** | Check the `phone` recall too — a detector that never fires also scores 0% |
| **< 2%** | Good. `PHONE_DWELL = 3.0s` will absorb isolated bad frames |
| **2–10%** | Raise `CONF_PHONE` in `scene.py` or `PHONE_DWELL` in `brain/mood.py`, re-run |
| **> 10%** | Fix this before building anything else. This robot would squirt you while you work |

Missed phones matter much less — the mood machine needs only 4–5 good frames
out of a 3-second dwell, so 30% missed still fires on time.

## Step 5 — watch the whole robot think (2 min)

```bash
python3 replay.py detections.jsonl --video desk.mp4 --out annotated.mp4
```

Real footage → YOLO → `Scene` → `brain/mood.py` → *would it have fired*.
Every shot it reports is a shot the real robot would have taken.

```
  20.0s  CHILL       phone      below notice threshold
  21.0s  SUSPICIOUS  phone      noticed
  23.0s  WARNING     phone      escalating
  26.0s  STRIKE      phone      FIRE
SHOTS FIRED: 1  at 26.0s
```

`annotated.mp4` burns the mood onto the frames. Bring it to the competition —
it is the best thing to show while the robot is between demos.

---

## The rules in `scene.py`, and why

**The phone must be near the person.** A phone charging on the far side of
the desk is not an offence. Without this test the robot fires at you while
you work, which is the exact failure that gets a device like this unplugged.
Tuned by `PHONE_NEAR_PAD`.

**`CONF_PHONE` (0.25) is looser than `CONF_PERSON` (0.40).** Phones are
small, motion-blurred and half-occluded by a hand. Being strict here builds a
detector that never fires; the dwell timers in `brain/mood.py` are what throw
away the noise, and they already have tests.

**Head-down uses aspect ratio, not the top edge.** Height/width is
scale-invariant, so rolling your chair back doesn't read as slouching — with
a raw top-edge test it would. There is a test for exactly that.

**Head-down is calibrated to you.** There is no universal "head down" number;
it depends on your chair, your desk and where the camera sits. The first 30
frames set a personal baseline (median, so one clipped box can't move it),
and head-down is always `False` while calibrating.

## When the Pi arrives

Only `detect.py` changes:

```bash
yolo export model=yolov8n.pt format=ncnn imgsz=320   # NCNN, not PyTorch
```

`scene.py`, `evaluate.py`, `replay.py` and `brain/` are untouched — they never
knew where the boxes came from. Then measure the real frame rate and feed it
back into `CLEAR_GRACE`.
