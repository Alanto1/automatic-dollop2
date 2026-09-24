# brain/ — the personality, as testable code

This is the part of the robot that needed no parts, no printer, and no
soldering iron, so it got built first.

```
brain/
  mood.py                        the state machine. Pure logic, no hardware
  tests/test_mood.py             19 desktop tests
  tests/run_tests.sh             bare python3, no pytest
  simulator/mood_simulator.html  the same machine in JS, in a browser
```

## Run it

```bash
./tests/run_tests.sh                  # 19/19 tests passed
open simulator/mood_simulator.html    # or just double-click it
```

Both work offline, on any laptop, with nothing installed.

## Why it's shaped like this

`mood.py` imports nothing but the standard library and knows nothing about
cameras, servos or clocks. It takes a `Scene` (what perception saw) and a
timestamp, and returns a `Decision` (what mood, and whether to fire). That's
the same split that made `HapticMapper.h` work on the wristband: the
interesting logic is testable on a desktop years before the hardware is
reliable.

Two consequences worth knowing:

- **The caller owns the clock.** `update(scene, now)` never calls
  `time.monotonic()` itself. That's why a 30-second escalation runs in zero
  seconds in the tests, and why the browser simulator can scrub time.
- **The state machine cannot fire the pump.** It only *says* `fire_ms=250`.
  The five interlocks in [`BEHAVIOURS.md`](../BEHAVIOURS.md) live in firmware
  and can refuse. `post_strike()` is deliberately separate, so a refused shot
  leaves the robot angry instead of smugly celebrating a hit it never landed.

## The one number that matters

`CLEAR_GRACE = 1.5` — how long the offence must be *continuously gone* before
the robot calms down.

It is **not** symmetric with the escalation dwells, and that asymmetry is the
whole trick. Perception runs at 1–2 FPS, so a 3-second phone dwell is only 4–5
frames of evidence. YOLO *will* drop a frame when a hand crosses the phone. If
one miss reset the escalation, the robot would never reach STRIKE at all.

1.5s survives two consecutive misses at 1.5 FPS. Turn on **drop frames** in
the simulator to watch that happen, then set it to 0.2 and watch the robot
become impossible to provoke.

Raise it if your measured frame rate is worse. Lower it and the robot starts
forgiving things it shouldn't.

## Tuning without hardware

The simulator's sliders are the six timings. Play with them until the robot
feels right, then copy the numbers into the constants at the top of `mood.py`
and re-run the tests. Some tests assert *relationships* rather than exact
values (head-down is judged slower than phone; `CLEAR_GRACE` survives two
dropped frames at 1.5 FPS), so they'll tell you if a change breaks the design
rather than just the number.

## What isn't here yet

- **Perception** fills in the `Scene`. Next job: YOLOv8n over recorded desk
  video on a laptop, sampled at 1–2 FPS — see `START_HERE.md`.
- **Motion** turns a `Decision` into intents (`turn`, `walk`, `face`, `fire`)
  and then into servo angles on the ESP32.

Both sit on the other side of the `Scene` / `Decision` seam, which is exactly
why this file could be finished before either existed.
