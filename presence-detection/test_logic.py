#!/usr/bin/env python3
"""
Tests for the parts that hold actual decisions. No model, no video, no
dependencies — runs in milliseconds.

    python3 test_logic.py
"""
import sys
from state import (Box, Sample, Config, percentile, compute_baseline,
                   phone_near_person, classify, smooth,
                   WORKING, ON_PHONE, GONE, PERSON, CELL_PHONE)
from score import confusion, truth_at, load_truth

passed = failed = 0

def check(name, got, want):
    global passed, failed
    if got == want:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")

def close(name, got, want, tol=1e-6):
    check(name, abs(got - want) < tol, True)

def person(y1=100, h=400, x1=200, w=200, conf=0.9):
    return Box(PERSON, conf, x1, y1, x1 + w, y1 + h)

def phone(cx=300, cy=300, conf=0.6):
    return Box(CELL_PHONE, conf, cx - 20, cy - 30, cx + 20, cy + 30)

cfg = Config()

# ---- percentile -------------------------------------------------------
close("percentile min",    percentile([1, 2, 3, 4, 5], 0.0), 1)
close("percentile max",    percentile([1, 2, 3, 4, 5], 1.0), 5)
close("percentile median", percentile([1, 2, 3, 4, 5], 0.5), 3)
close("percentile interp", percentile([0, 10], 0.25), 2.5)
close("percentile single", percentile([7], 0.5), 7)

# ---- baseline ---------------------------------------------------------
# 8 upright samples (y1=100) and 12 head-down ones (y1=180). A median would
# be dragged to the head-down value; the 20th percentile must not be.
ups   = [Sample(i, i, person(y1=100)) for i in range(8)]
downs = [Sample(i, i, person(y1=180)) for i in range(8, 20)]
b = compute_baseline(ups + downs)
check("baseline resists a mostly-head-down session", b[0] < 130, True)
close("baseline height", b[1], 400)
check("baseline with nobody", compute_baseline([Sample(0, 0.0)]), None)

# ---- phone proximity --------------------------------------------------
p = person()                                   # box x 200..400, y 100..500
check("phone on lap counts",      phone_near_person(phone(300, 450), p, 0.15), True)
check("phone far away ignored",   phone_near_person(phone(900, 300), p, 0.15), False)
check("phone just outside pad",   phone_near_person(phone(200 - 60, 300), p, 0.15), False)
check("phone just inside pad",    phone_near_person(phone(200 - 20, 300), p, 0.15), True)

# ---- single-sample classification -------------------------------------
base = (100.0, 400.0)
check("no person -> gone",   classify(Sample(0, 0.0), base, cfg), GONE)
check("upright -> working",  classify(Sample(0, 0.0, person(y1=100)), base, cfg), WORKING)
check("head down -> phone",  classify(Sample(0, 0.0, person(y1=160)), base, cfg), ON_PHONE)
check("small droop ignored", classify(Sample(0, 0.0, person(y1=120)), base, cfg), WORKING)
check("phone in hand beats upright posture",
      classify(Sample(0, 0.0, person(y1=100), phone(300, 300)), base, cfg), ON_PHONE)
check("desk phone far from person ignored",
      classify(Sample(0, 0.0, person(y1=100), phone(1200, 300)), base, cfg), WORKING)
check("no baseline -> posture unused, still working",
      classify(Sample(0, 0.0, person(y1=900)), None, cfg), WORKING)

# ---- smoothing / hysteresis -------------------------------------------
c = Config(commit_samples=4, gone_samples=6)

check("constant in, constant out",
      smooth([WORKING] * 10, c), [WORKING] * 10)

# One glitch sample must not flip the output.
check("single-sample glitch absorbed",
      smooth([WORKING, WORKING, ON_PHONE, WORKING, WORKING], c),
      [WORKING] * 5)

# Three is still below the commit threshold of four.
check("3-sample glitch still absorbed",
      smooth([WORKING] * 2 + [ON_PHONE] * 3 + [WORKING] * 2, c),
      [WORKING] * 7)

# Four sustained samples commit, on the 4th.
check("sustained change commits on the Nth sample",
      smooth([WORKING] * 2 + [ON_PHONE] * 5, c),
      [WORKING] * 5 + [ON_PHONE] * 2)

# gone needs 6, not 4 — so 5 is not enough.
check("gone needs more evidence than on_phone",
      smooth([WORKING] * 2 + [GONE] * 5, c),
      [WORKING] * 7)
check("gone commits at 6",
      smooth([WORKING] * 2 + [GONE] * 6, c),
      [WORKING] * 7 + [GONE])

# A run interrupted by a different state restarts the count.
check("interrupted run restarts the counter",
      smooth([WORKING] + [ON_PHONE]*3 + [GONE] + [ON_PHONE]*3, c),
      [WORKING] * 8)

check("empty input", smooth([], c), [])

# ---- scoring ----------------------------------------------------------
m = confusion([(WORKING, WORKING), (WORKING, ON_PHONE), (GONE, GONE)])
check("confusion diagonal", m[WORKING][WORKING], 1)
check("confusion off-diagonal", m[WORKING][ON_PHONE], 1)
check("confusion untouched cell", m[ON_PHONE][GONE], 0)

spans = [(0.0, 10.0, WORKING), (10.0, 20.0, ON_PHONE)]
check("truth lookup start-inclusive", truth_at(spans, 0.0), WORKING)
check("truth lookup end-exclusive",   truth_at(spans, 10.0), ON_PHONE)
check("truth lookup outside",         truth_at(spans, 25.0), None)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
