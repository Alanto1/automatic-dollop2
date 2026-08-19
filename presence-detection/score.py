#!/usr/bin/env python3
"""
Pass 3 — compare the detector's timeline against what actually happened.

Ground truth is a CSV of intervals, which you write by scrubbing the video in
any player. Per-frame labelling is not worth the hours; intervals are.

    start,end,label
    0,125,working
    125,180,on_phone
    180,240,gone

    python score.py states.csv truth.csv

The number that matters most is the on_phone FALSE POSITIVE rate: how often
the system would nag you while you were actually working. A device that is
wrong in that direction gets switched off and thrown in a drawer.
"""
import argparse, csv
from state import STATES, WORKING, ON_PHONE, GONE


def load_truth(path):
    spans = []
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            label = r["label"].strip()
            if label not in STATES:
                raise SystemExit(f"unknown label {label!r}; expected one of {STATES}")
            spans.append((float(r["start"]), float(r["end"]), label))
    spans.sort()
    for (s1, e1, _), (s2, _, _) in zip(spans, spans[1:]):
        if e1 > s2:
            raise SystemExit(f"ground truth intervals overlap at t={s2}")
    return spans


def truth_at(spans, t):
    for s, e, label in spans:
        if s <= t < e:
            return label
    return None            # outside any labelled interval — excluded from scoring


def confusion(pairs):
    """pairs of (truth, predicted) -> nested dict."""
    m = {a: {b: 0 for b in STATES} for a in STATES}
    for t, p in pairs:
        m[t][p] += 1
    return m


def report(pairs):
    if not pairs:
        raise SystemExit("no samples fell inside a labelled interval")
    m = confusion(pairs)
    n = len(pairs)
    correct = sum(m[s][s] for s in STATES)

    w = max(len(s) for s in STATES)
    print(f"\n{n} labelled samples, accuracy {100*correct/n:.1f}%\n")
    print("confusion matrix — rows = truth, cols = predicted")
    print(" " * (w + 2) + "".join(f"{s:>10s}" for s in STATES))
    for a in STATES:
        print(f"{a:>{w}s}  " + "".join(f"{m[a][b]:10d}" for b in STATES))

    print(f"\n{'class':>{w}s}  {'prec':>7s} {'recall':>7s} {'F1':>7s} {'support':>8s}")
    for s in STATES:
        tp = m[s][s]
        fp = sum(m[a][s] for a in STATES if a != s)
        fn = sum(m[s][b] for b in STATES if b != s)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec  = tp / (tp + fn) if tp + fn else 0.0
        f1   = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        print(f"{s:>{w}s}  {prec:7.3f} {rec:7.3f} {f1:7.3f} {tp+fn:8d}")

    # The headline number.
    not_phone = sum(sum(m[a][b] for b in STATES) for a in STATES if a != ON_PHONE)
    false_alarms = sum(m[a][ON_PHONE] for a in STATES if a != ON_PHONE)
    rate = false_alarms / not_phone if not_phone else 0.0
    print(f"\non_phone false positives: {false_alarms}/{not_phone} = {100*rate:.1f}%")
    print("  (samples where you were NOT on your phone but it thought you were)")
    if rate > 0.10:
        print("  >10% — it would nag you constantly. Raise --head-drop or --commit.")
    return rate


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("states", nargs="?", default="states.csv")
    ap.add_argument("truth",  nargs="?", default="truth.csv")
    ap.add_argument("--column", default="state", choices=["state", "raw"],
                    help="score the smoothed timeline (default) or the raw one")
    args = ap.parse_args()

    spans = load_truth(args.truth)
    pairs = []
    with open(args.states, newline="") as fh:
        for r in csv.DictReader(fh):
            gt = truth_at(spans, float(r["t"]))
            if gt is not None:
                pairs.append((gt, r[args.column]))
    report(pairs)


if __name__ == "__main__":
    main()
