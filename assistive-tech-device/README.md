# Assistive Tech Device — Obstacle-Detection Wristband

A haptic obstacle-detection wearable for low-vision navigation: one
forward-facing time-of-flight distance sensor on a wristband, driving a
vibration motor whose pulse rate and strength encode how close an obstacle
is. Built as a hobby/school project (Jugend forscht or an accessibility-track
hackathon are plausible next steps). v1 is deliberately minimal — one
sensor, one motor, no display, no multi-obstacle mapping.

## Before you read any further

**This cannot be ethically presented as "helping blind/low-vision people
navigate" without real feedback from an actual low-vision test user.**
Sighted, blindfolded self-testing is not sufficient — obstacle detectors
have real failure modes (narrow field of view, missed low/overhead
obstacles, false confidence from a device that "usually" works), and
overstating what a hobby prototype does to a vulnerable audience is a
genuine harm, not just a credibility risk.

The `outreach/` drafts are the **longest-lead-time item in this whole
project** and should go out early, in parallel with the build, not after.
Before any public writeup, demo, or competition submission: get explicit
consent before naming or showing any test user.

## How it works

```
VL53L1X (ToF sensor, I2C) --distance_mm--> HapticMapper --zone+PWM--> vibration motor
```

`HapticMapper` (see `firmware/obstacle_haptic/HapticMapper.h`) buckets the
live distance reading into one of four zones and turns that into a motor
on/off + PWM-duty pattern:

| Zone | Distance | Motor behavior | Duty |
|---|---|---|---|
| Far | ≥ 2000mm (or an invalid/near-zero reading) | off | — |
| Medium | 1000–1999mm | slow pulse (120ms on / 400ms off) | 140/255 |
| Near | 400–999mm | faster pulse (120ms on / 150ms off) | 200/255 |
| Critical | 10–399mm | continuous | 255/255 |

Those thresholds and timings are starting points, not measured-good
values — tune them with `firmware/simulator/haptic_simulator.html` (or the
published copy at
https://claude.ai/code/artifact/11fad495-b365-421a-8ad3-479ae7244d1e)
before trusting them on a wrist.

## Status

- [ ] **Week 0 — outreach.** Drafted (`outreach/`), not sent.
- [~] **Weeks 1-2 — breadboard prototype.** Firmware logic is written and
  desktop-unit-tested (14/14 passing, see `firmware/tests/` — actually run
  in this environment, not just claimed). Hardware has not been purchased
  or assembled. `obstacle_haptic.ino` has been reviewed but **not
  compiled or flashed** — there's no Arduino toolchain/board in this
  environment. Treat first flash as a fresh bring-up.
- [~] **Weeks 3-4 — wearable enclosure.** `enclosure.scad` render-verifies
  cleanly (headless OpenSCAD, base/lid/belt-clip all export as valid
  manifold geometry — see the file header for how that was checked). Every
  dimension in its "[MEASURE YOUR PARTS]" section is still a guess, not a
  caliper measurement.
- [ ] **Weeks 4-6 — real feedback session** with whoever responds to
  outreach. Not started.
- [ ] **Writeup + consent**, after the above.

This whole directory was scaffolded by Claude Code from a handoff summary
on 2026-07-25 — there was no prior repo or source tree, only a project
description. Where the summary described work as already verified (tests
passing, OpenSCAD renders confirmed), that verification has been redone
here from scratch and is described accurately above; nothing is carried
forward as true just because an earlier note said so.

## Bill of materials

Full sourcing with real, live-checked store links and prices is in
[`PURCHASE_LIST.md`](PURCHASE_LIST.md) (currently the **Almaty edition** —
re-check that file's header if building from a different city, since pickup
vs. shipping flips between stores depending on where you are). For shopping
on a phone, [`PURCHASE_LIST_almaty.html`](PURCHASE_LIST_almaty.html) is the
same list as a self-contained, offline-capable checklist — tap to check
items off, live running total, no server needed (open the file directly, or
https://claude.ai/code/artifact/38b6a57a-ecb2-4fa0-bc9a-2c3fd3c63a42 for a
link instead of a download). Summary:

| Part | Purpose |
|---|---|
| Arduino Nano (CH340 clone, USB-C) | microcontroller |
| VL53L1X time-of-flight sensor | forward-facing distance sensing (up to ~4m) |
| Vibration motor (10mm coin type) | haptic output |
| 2N2222 NPN transistor + 1N4148 flyback diode + resistor (220Ω-1k both work) | motor driver (a GPIO pin can't source a motor's current directly) |
| LiPo battery (~380-800mAh) + TP4056 charge module | power |
| Wristband strap | mounting |
| Breadboard + jumper wires | prototyping (breadboard phase only) |

`PURCHASE_LIST.md`'s current parts list skips a 5V boost converter and a
power switch (wires the LiPo straight to 5V, disconnect the battery to turn
off) to keep cost/complexity down - a common enough shortcut for
battery-powered Nano clones, flagged there as worth watching for flaky
behavior rather than treated as wrong. Add both back (a few hundred тг
each) if the breadboard prototype turns out to need them.

### Sensor substitution warning

`HapticMapper.h`'s far threshold is exactly 2000mm. The commonly-stocked
VL53L0X (2m max range) has **zero margin** at that threshold — a reading
right at the sensor's ceiling is indistinguishable from "no data." Use a
real VL53L1X (4m range) instead; see `PURCHASE_LIST.md` for where to get
one. If a VL53L0X ends up on the board anyway, lower `kFarThresholdMm`
well below 2000 first.

## Wiring

```
VL53L1X          Arduino Nano
  VIN  -------------- 5V
  GND  -------------- GND
  SDA  -------------- A4
  SCL  -------------- A5

Motor circuit (D9 is PWM-capable):
  Nano D9 --[220ohm]--> transistor base (2N2222)
  Motor(+) -------------------------------- 5V / battery+
  Motor(-) -------------------------------- transistor collector
  transistor emitter ----------------------- GND
  1N4148 flyback diode across motor leads, cathode (banded end) to Motor(+)

Power (as currently purchased - see PURCHASE_LIST.md's power note):
  LiPo -> TP4056 (charge/protect) -> Nano 5V pin + motor circuit's 5V rail
  Common GND across sensor, motor circuit, and Nano.
  Optional, not in the current parts list: a 5V boost converter between
  TP4056 and the 5V rail (keeps the rail at a true regulated 5V instead of
  the raw ~3.7-4.2V battery voltage), and a slide/toggle switch for power
  on/off instead of disconnecting the battery by hand.
```

Draw this into a real schematic before breadboarding — this is a text
description of the connections, not a substitute for checking datasheets
(transistor pinout in particular varies by package/orientation).

## Repository layout

```
assistive-tech-device/
├── CLAUDE.md                          handoff notes for a future Claude Code session
├── README.md                          this file
├── BUILD_CHECKLIST.md                 parts/tools needed, by build phase
├── PURCHASE_LIST.md                   BUILD_CHECKLIST.md with real store links/prices
├── outreach/                          draft outreach emails (unsent)
├── firmware/
│   ├── obstacle_haptic/
│   │   ├── HapticMapper.h             distance -> vibration logic (pure C++, no Arduino deps)
│   │   └── obstacle_haptic.ino        hardware glue: VL53L1X polling + motor PWM
│   ├── tests/                         desktop unit tests for HapticMapper.h
│   └── simulator/
│       └── haptic_simulator.html      browser tool - tune thresholds without hardware
└── enclosure/
    └── enclosure.scad                 parametric OpenSCAD wristband/belt-clip enclosure
```

## Running the firmware tests

No Arduino toolchain needed - `HapticMapper.h` has zero hardware
dependencies on purpose.

```sh
cd firmware/tests
./run_tests.sh
```

Expected: `14/14 tests passed`, exit code 0. Re-run after any
`HapticMapper.h` change.

## Using the simulator

Open `firmware/simulator/haptic_simulator.html` directly in a browser (no
build step, no server, no hardware) - or use the published copy:
https://claude.ai/code/artifact/11fad495-b365-421a-8ad3-479ae7244d1e

Drag the obstacle along the rangefinder, or hit "Simulate approach" to
animate one sweeping past. It ports `HapticMapper.h`'s zone/pulse logic
line-for-line into JS, so tuning thresholds there is representative of
real firmware behavior - not just a rough sketch.

## Enclosure

`enclosure/enclosure.scad` is parametric: three modules (`wristband_back`
/ `lid` / `belt_clip_back`) built from a block of measurements at the top
of the file. **Every dimension in the "[MEASURE YOUR PARTS]" section is a
placeholder** - update it from real calipers once parts are in hand, then
re-render before printing. The belt-clip alternative mount is explicitly
unvalidated (needs print-and-test iteration on real material/printer) -
the wristband strap-slot mount (two lug tunnels, watch-lug style) is v1's
primary, chosen over a single-slot design specifically because one slot
would let the pod pivot around that single wrap point instead of sitting
flat.

## Safety notes

- **LiPo charging:** no fireproof charging pouch was identified during
  sourcing (see `PURCHASE_LIST.md`). Fallback practice until one is
  sourced: charge on a non-flammable surface, supervised, never
  unattended overnight.
- **Sensor failure mode:** if the VL53L1X fails to init or times out, the
  firmware fails toward *no vibration*, not a false alarm (see
  `obstacle_haptic.ino` and `HapticMapper.h` comments). That is a
  deliberate tradeoff, not a safety guarantee — a wristband that goes
  silent on sensor fault gives no positive indication anything is wrong
  either. A distinct "sensor fault" haptic pattern (as opposed to reusing
  the proximity pulses) would close that gap and is a reasonable next
  addition, not yet built.
- **Field of view / blind spots:** a single forward-facing point sensor
  detects obstacles in a narrow cone directly ahead. Low obstacles,
  overhead obstacles, and anything outside that cone will not be
  detected. This is exactly the kind of limitation that makes real
  low-vision user feedback (see top of this file) non-optional before
  this is presented as more than a hobby prototype.

## Roadmap

1. Send the outreach emails (`outreach/`) - still the most time-sensitive
   open item.
2. Work through `PURCHASE_LIST.md` and order parts.
3. Once parts arrive: measure them with calipers, update
   `enclosure.scad`'s placeholder dimensions, re-render, then breadboard
   the circuit per the wiring diagram above.
4. Flash `obstacle_haptic.ino` (needs the Pololu VL53L1X Arduino library),
   tune thresholds using the breadboard + `haptic_simulator.html` side by
   side, then run a blindfolded course test with a sighted spotter as a
   first-pass sanity check - not a substitute for real low-vision user
   feedback.
