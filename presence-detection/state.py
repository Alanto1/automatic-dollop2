#!/usr/bin/env python3
"""
Pass 2 — turn raw detections into a state timeline: working / on_phone / gone.

Pure stdlib. No model, no video, no numpy. That is the point: this file holds
all the decisions worth arguing about, so it can be unit-tested in
milliseconds (see test_logic.py) and re-tuned without re-running the detector.

    python state.py detections.csv --out states.csv
"""
import argparse, csv
from dataclasses import dataclass

PERSON, LAPTOP, CELL_PHONE, BOOK = 0, 63, 67, 73
NO_DETECTION = -1

WORKING, ON_PHONE, GONE = "working", "on_phone", "gone"
STATES = (WORKING, ON_PHONE, GONE)


@dataclass
class Box:
    cls: int; conf: float
    x1: float; y1: float; x2: float; y2: float

    @property
    def w(self):  return self.x2 - self.x1
    @property
    def h(self):  return self.y2 - self.y1
    @property
    def cx(self): return (self.x1 + self.x2) / 2
    @property
    def cy(self): return (self.y1 + self.y2) / 2


@dataclass
class Sample:
    frame: int; t: float
    person: "Box|None" = None
    phone:  "Box|None" = None


@dataclass
class Config:
    person_conf: float = 0.40
    phone_conf:  float = 0.30

    # "Head down" without pose estimation: the top of the person box drops
    # relative to that person's own upright baseline. Expressed as a fraction
    # of baseline body height so it survives the camera being moved.
    head_drop_frac: float = 0.10

    # A phone only counts if it is near the person — a phone lying on the desk
    # in shot all day is not "on phone". Person box is expanded by this
    # fraction before testing whether the phone centre falls inside.
    phone_pad_frac: float = 0.15

    # Hysteresis. A raw state must persist this many consecutive samples
    # before it is committed. Single-frame detector glitches are extremely
    # common and without this the timeline is unusable confetti.
    # Cost: transitions are reported (commit-1) samples late.
    commit_samples: int = 4
    gone_samples:   int = 6     # disappearing needs more evidence than the rest


def percentile(values, p):
    """p in 0..1. Linear interpolation, stdlib only."""
    if not values:
        raise ValueError("empty")
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def load_samples(path, cfg):
    """Group CSV rows into one Sample per frame, keeping the best box per class."""
    by_frame = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            f = int(r["frame"])
            s = by_frame.setdefault(f, Sample(frame=f, t=float(r["t"])))
            cls = int(r["cls"])
            if cls == NO_DETECTION:
                continue
            b = Box(cls, float(r["conf"]),
                    float(r["x1"]), float(r["y1"]), float(r["x2"]), float(r["y2"]))
            if cls == PERSON and b.conf >= cfg.person_conf:
                if s.person is None or b.conf > s.person.conf:
                    s.person = b
            elif cls == CELL_PHONE and b.conf >= cfg.phone_conf:
                if s.phone is None or b.conf > s.phone.conf:
                    s.phone = b
    return [by_frame[f] for f in sorted(by_frame)]


def compute_baseline(samples):
    """
    Upright reference for this recording.

    y1 is the TOP of the person box (image y grows downward), so the smallest
    y1 values are the head-up frames. Taking the 20th percentile rather than
    the median means a session spent largely head-down does not drag the
    baseline down with it and hide the very thing we are detecting.

    Returns (baseline_y1, baseline_h) or None if nobody was ever seen.
    """
    tops    = [s.person.y1 for s in samples if s.person]
    heights = [s.person.h  for s in samples if s.person]
    if not tops:
        return None
    return percentile(tops, 0.20), percentile(heights, 0.50)


def phone_near_person(phone, person, pad_frac):
    pad_x, pad_y = person.w * pad_frac, person.h * pad_frac
    return (person.x1 - pad_x <= phone.cx <= person.x2 + pad_x and
            person.y1 - pad_y <= phone.cy <= person.y2 + pad_y)


def classify(sample, baseline, cfg):
    """Single-sample decision, before any smoothing."""
    if sample.person is None:
        return GONE
    if sample.phone is not None and phone_near_person(sample.phone, sample.person,
                                                      cfg.phone_pad_frac):
        return ON_PHONE
    if baseline is not None:
        base_y1, base_h = baseline
        if base_h > 0 and (sample.person.y1 - base_y1) / base_h > cfg.head_drop_frac:
            return ON_PHONE
    return WORKING


def smooth(raw, cfg):
    """
    Debounce the raw per-sample states.

    Identical in spirit to debouncing a button, or the hysteresis on the
    photoresistor threshold: require sustained evidence before committing to
    a change, so one noisy sample cannot flip the output.
    """
    if not raw:
        return []
    current = raw[0]
    pending, run = None, 0
    out = []
    for s in raw:
        if s == current:
            pending, run = None, 0
        else:
            if s == pending:
                run += 1
            else:
                pending, run = s, 1
            need = cfg.gone_samples if s == GONE else cfg.commit_samples
            if run >= need:
                current, pending, run = s, None, 0
        out.append(current)
    return out


def run(samples, cfg):
    baseline = compute_baseline(samples)
    raw = [classify(s, baseline, cfg) for s in samples]
    return raw, smooth(raw, cfg), baseline


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("detections", nargs="?", default="detections.csv")
    ap.add_argument("--out", default="states.csv")
    ap.add_argument("--head-drop", type=float, default=Config.head_drop_frac)
    ap.add_argument("--commit", type=int, default=Config.commit_samples)
    ap.add_argument("--person-conf", type=float, default=Config.person_conf)
    args = ap.parse_args()

    cfg = Config(head_drop_frac=args.head_drop, commit_samples=args.commit,
                 person_conf=args.person_conf)
    samples = load_samples(args.detections, cfg)
    if not samples:
        raise SystemExit("no samples found — did detect.py write anything?")

    raw, smoothed, baseline = run(samples, cfg)

    with open(args.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["frame", "t", "raw", "state"])
        for s, r, sm in zip(samples, raw, smoothed):
            w.writerow([s.frame, f"{s.t:.3f}", r, sm])

    print(f"{len(samples)} samples -> {args.out}")
    if baseline:
        print(f"baseline: head top y={baseline[0]:.0f}px, body height={baseline[1]:.0f}px")
    else:
        print("baseline: NO PERSON EVER DETECTED — check the video and --person-conf")
    for st in STATES:
        n = smoothed.count(st)
        print(f"  {st:9s} {n:5d} samples  {100*n/len(smoothed):5.1f}%")
    flips = sum(1 for a, b in zip(smoothed, smoothed[1:]) if a != b)
    print(f"  transitions: {flips} (raw would have been "
          f"{sum(1 for a,b in zip(raw, raw[1:]) if a!=b)})")


if __name__ == "__main__":
    main()
