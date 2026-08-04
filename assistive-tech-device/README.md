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
VL53L0X (ToF sensor, I2C) --distance_mm--> HapticMapper --zone+PWM--> vibration motor
```

`HapticMapper` (see `firmware/obstacle_haptic/HapticMapper.h`) buckets the
live distance reading into one of four zones and turns that into a motor
on/off + PWM-duty pattern:

| Zone | Distance | Motor behavior | Duty |
|---|---|---|---|
| Far | ≥ 1000mm (or an invalid/near-zero reading) | off | — |
| Medium | 600–999mm | slow pulse (120ms on / 400ms off) | 140/255 |
| Near | 250–599mm | faster pulse (120ms on / 150ms off) | 200/255 |
| Critical | 10–249mm | continuous | 255/255 |

Those thresholds and timings are starting points, not measured-good
values — tune them with `firmware/simulator/haptic_simulator.html` (or the
published copy at
https://claude.ai/code/artifact/11fad495-b365-421a-8ad3-479ae7244d1e)
before trusting them on a wrist.

## Status

- [ ] **Week 0 — outreach.** Drafted (`outreach/`), not sent.
- [~] **Weeks 1-2 — breadboard prototype.** Firmware logic is written and
  desktop-unit-tested (14/14 passing, see `firmware/tests/` — actually run
  in this environment, not just claimed). On real hardware as of
  2026-07-30: **Phase 2 (sensor) and Phase 3 (motor driver) both pass** —
  live distance readings over I2C, and the motor buzzing under firmware
  control. The 10×3mm motor and the flat 502030 LiPo are both in hand, and
  the battery is soldered to a TP4056 with charging confirmed.
  **Outstanding safety item: that TP4056 is stock, charging a 250mAh cell
  at 1A (~4C) — `R3` needs changing to ~10kΩ, see `PURCHASE_LIST.md`.**
  Phase 4 (combined firmware on hardware) and Phase 5 (running off
  battery) are not done, and `obstacle_haptic.ino` has still never been
  flashed to the board.
- [~] **Weeks 3-4 — wearable enclosure.** `enclosure.scad` is modelled to
  the builder's sketch — a 67 × 30 × 50mm box on a strap plinth — and
  render-verifies cleanly (headless OpenSCAD; base, lid, belt-clip and
  switch coupon all export as valid manifold geometry, with each cutout
  checked against its expected coordinates in the exported STL — see the
  file header). Most dimensions are now real caliper numbers; the switch
  actuator size and USB connector body margin are still guesses. Nothing
  has been printed yet.
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
[`PURCHASE_LIST.md`](PURCHASE_LIST.md) — currently the **Almaty, walk-in
edition**: real physical component shops, no shipping/delivery, re-checked
2026-07-25 after the shipping-based version turned out not to fit (see that
file's own history for why it changed twice in one day). For shopping on a
phone, [`PURCHASE_LIST_almaty.html`](PURCHASE_LIST_almaty.html) is the same
list as a self-contained, offline-capable checklist — tap to check items
off, live running total, tap-to-call links for the two stores (open the
file directly, or https://claude.ai/code/artifact/38b6a57a-ecb2-4fa0-bc9a-2c3fd3c63a42
for a link instead of a download). Summary:

| Part | Purpose |
|---|---|
| Arduino Nano (CH340 clone, USB-C) | microcontroller |
| VL53L0X time-of-flight sensor | forward-facing distance sensing (up to ~2m — see sensor note below) |
| Vibration motor (10mm coin type) | haptic output |
| 2N2222 NPN transistor + 1N4148 flyback diode + resistor (220Ω-1k both work) | motor driver (a GPIO pin can't source a motor's current directly) |
| Li-ion cell (flat 502030 pouch or 18650) + TP4056 charge module | power (see battery note below - a flat pouch option is confirmed again, via Kaspi.kz) |
| Wristband strap | mounting |
| Breadboard + jumper wires | prototyping (breadboard phase only) |

`PURCHASE_LIST.md`'s parts list skips a 5V boost converter (wires the
battery straight to 5V) to keep cost/complexity down - a common enough
shortcut for battery-powered Nano clones, flagged there as worth watching
for flaky behavior rather than treated as wrong.

A **power switch** was originally skipped on the same reasoning - just
unplug the battery. That reasoning only holds while the battery is
unplugabble, so it's now listed as **required**: once the cell is soldered
to the TP4056, "off" would otherwise mean desoldering it. A small SPST
slide switch goes in series on the TP4056's `OUT+` line, which cuts the
load while leaving the charging path intact. `enclosure.scad` now cuts a
slot for it in the pod's back wall, sized from the real switch body —
though the actuator nub itself is still a guess, which is what
`switch_test_coupon` exists to settle.

### Sensor note

No walk-in Almaty store stocks a VL53L1X (4m range) as of this pass - only
the VL53L0X (2m range) is actually on shelves, so that's what this project
now targets. `HapticMapper.h`'s `kFarThresholdMm` is set to **1000mm**,
well inside that sensor's capability. It was originally 1800mm, chosen to
leave margin under the VL53L0X's 2000mm ceiling; it's since been tightened
further so the wristband stays silent until something is within about
arm's reach, rather than reacting to the far end of a corridor.
`kFarThresholdMm` is the knob to turn if you want it to react earlier or
later - see that constant's comment. The same VL53L0X/GY-53 module is also
confirmed listed on Kaspi.kz, as an alternative to the walk-in stores -
see `PURCHASE_LIST.md`'s sensor table for the link.

**If your board is a GY-53, `PS` must be wired to GND.** A GY-53 is not a
bare VL53L0X breakout - the giveaway is its extra `TX` / `RX` / `PWM` /
`PS` pins, which exist because it carries its own onboard microcontroller
between you and the sensor chip. `PS` selects that MCU's mode: pulled high
(the factory default) is UART/serial mode, in which **I2C is entirely
disabled** and no amount of correct VIN/GND/SDA/SCL wiring will let the
Pololu library find the sensor. Tying `PS` to GND switches it to I2C mode,
where the MCU steps back and you address the VL53L0X directly. Either GND
pin on the module works - they're the same net.

This one is worth knowing about in advance because every symptom of
getting it wrong impersonates a wiring fault: `init()` fails, an I2C bus
scan reports no devices at any address, and probing SDA/SCL shows them
flickering apparently at random. That flicker is not a loose connection -
it's the onboard MCU running its own I2C conversation with the sensor
chip. Confirmed against the GY-53 manual, which states the module
"defaults to serial port mode... PS port is pulled high".

**Range configuration.** The sensor runs on its **default** measurement
profile, which reliably reaches about 1.2m - comfortably past the 1000mm
far threshold, with margin. The default is also the more accurate and
noise-immune profile, which is what you want on a wrist.

An earlier revision enabled the Pololu long-range preset here, because
the far threshold was then 1800mm and the default profile simply couldn't
see that far - the medium zone would have read as empty. Now that the
thresholds are tighter, that preset would buy reach nobody needs in
exchange for more spurious readings, so it's gone. **If
`kFarThresholdMm` ever goes back above ~1100mm, restore it** - sensor
config and thresholds have to move together, or the far zone quietly
becomes "the sensor can't see that far" rather than "nothing is there".
See `obstacle_haptic.ino`'s `setup()` for the exact calls.

### Battery note

Two real options now, not just the 18650:

- **Flat LiPo pouch, 502030 (3.7V, 250mAh, nominal 5×20×30mm)** -
  confirmed on Kaspi.kz, Li-Pol chemistry with built-in
  overcharge/overcurrent protection. `enclosure/enclosure.scad`'s battery
  cavity is now sized for this cell - no enclosure redesign needed if
  it's the one you use. 250mAh is modest; expect shorter runtime than the
  18650 below.
- **Cylindrical 18650, 3400mAh (LiitoKala)** - confirmed in stock at Alash
  Electronics, walk-in. About 13x the capacity of the 502030, but it's a
  tube (18mm dia. × 65mm long) - `enclosure/enclosure.scad` would need a
  cylindrical battery bay to fit this one instead, a real design change
  not made in this pass.

See `PURCHASE_LIST.md`'s battery note for links, prices, and the full
reasoning either way.

## Wiring

```
VL53L0X          Arduino Nano
  VIN  -------------- 5V
  GND  -------------- GND
  SDA  -------------- A4
  SCL  -------------- A5
  PS   -------------- GND      <-- REQUIRED on a GY-53, see sensor note

Motor circuit (D9 is PWM-capable):
  Nano D9 --[220ohm-1k, either works]--> transistor base (2N2222)
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

Two published references cover this visually:

- **Full circuit schematic** — sensor, motor driver and power on one
  diagram, colour-coded by net:
  https://claude.ai/code/artifact/c69dd337-6c56-415d-b2a7-4d0eb66433ad
- **Soldering plan** — what the breadboard's power rails become once the
  build goes permanent (two star joints), plus five staged assembly steps
  each with a test gate:
  https://claude.ai/code/artifact/8f43ca79-bcd2-4351-913a-767ca58c930c

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
│   │   └── obstacle_haptic.ino        hardware glue: VL53L0X polling + motor PWM
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

`enclosure/enclosure.scad` is parametric: four printable modules
(`wristband_back` / `lid` / `belt_clip_back` / `switch_test_coupon`) built
from a block of measurements at the top of the file. Most of that block is
now real caliper data; the two that are still guesses — the switch
actuator's size and the USB connector body margin — are labelled as such,
and both are worth checking before a real print.

**Built to the builder's sketch.** The pod lies with its **67mm length
along the arm**, so a 30mm end face looks forward in the direction of
travel. Layout:

| Feature | Where |
| --- | --- |
| Sensor window (6mm) | −X front wall, mid-height, looking where you walk |
| Power switch slot | +X back wall, mid-height |
| USB-C (charge) + mini-USB (data) | **in the lid**, side by side, pointing up |
| Strap tunnel (20mm) | in a plinth **under** the box, centred, boring across |
| Vibration motor | glued to an inside wall — no cutout needed |

Three numbers all get called "the height", so to be explicit:

| | mm |
| --- | --- |
| The box itself (open-topped, holds the electronics) | 52 |
| What actually prints as the base — box + strap plinth | 59.2 |
| Assembled, with the lid's plate on top | 61.4 |
| Usable interior for a board hanging from the lid | 46.8 |

**The strap compartment is extra height beneath the box, not a slice out
of it.** An earlier revision ran the tunnel through the box's own floor
and the cavity paid ~7mm for it; this way the interior keeps its full
height and the pod just stands a little further off the wrist.

The box is 52mm rather than the sketched 50 because the Nano has to hang
on its long edge — the only orientation that puts its mini-USB where the
lid's hole is — and 50 gave a 44.8mm cavity, 0.2mm short of the Nano's
45mm. An assert enforces it now, so dropping back to 50 fails loudly
instead of quietly producing a box the Nano won't go into.

### Internal mounting

Everything is located by a printed feature and held by glue. Nothing is a
press fit; what the features buy is that each glue joint is made against a
flat surface in a known position.

| Part | Feature |
| --- | --- |
| Nano, TP4056 | four-walled pocket hanging from the lid, connector-end up |
| Battery | same, but **one face left open** — a LiPo pouch swells with age, and a rigid box with no give is a bad place to find that out |
| VL53L0X | picture-frame cradle on the inside of the front wall, centred on the window |
| Motor | raised ring on the cavity floor, front zone |

The three pockets sit front to back down the pod's length: **Nano ·
battery · TP4056**. That order isn't arbitrary — the Nano is nearest the
sensor so the I2C run is short (I2C is what cost this project a multi-hour
debugging session, and long unshielded SDA/SCL is the classic way to make
it flaky), and the TP4056 is nearest the switch it feeds.

**Assembly is meant to happen with the lid upside down on the bench**:
the pockets become open-topped cups, each board drops in connector-end
first, and gravity holds it while the glue sets. Then the lid goes onto
the base with the wires tucked in.

The motor sits on the floor rather than a side wall because the floor is
the surface nearest the skin, with solid plinth beneath it at that end —
the buzz couples into the wrist instead of rattling around inside the
shell.

### Caveats

- The single strap tunnel replaced two watch-style lug tunnels at the
  builder's request: one wrap point lets the pod rock about the strap's
  axis, and the sensor aims wherever the pod happens to point. The
  full-footprint plinth beds the pod down on a wide flat face, which
  helps, but doesn't eliminate it.
- **`tof_lens_offset_y/z` are both 0**, i.e. the cradle assumes the
  VL53L0X chip is centred on its breakout. On a GY-53 it isn't. Get this
  wrong and the sensor spends its life staring at the inside of the wall,
  reading a permanent obstacle — and nothing about the device would *look*
  wrong, it would just always buzz.
- The belt-clip alternative mount remains explicitly unvalidated (needs
  print-and-test iteration on real material and printer).

## Safety notes

- **LiPo charging:** no fireproof charging pouch was identified during
  sourcing (see `PURCHASE_LIST.md`). Fallback practice until one is
  sourced: charge on a non-flammable surface, supervised, never
  unattended overnight.
- **Sensor failure mode:** if the VL53L0X fails to init or times out, the
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
4. Flash `obstacle_haptic.ino` (needs the Pololu **VL53L0X** Arduino
   library), tune thresholds using the breadboard + `haptic_simulator.html`
   side by side, then run a blindfolded course test with a sighted spotter
   as a first-pass sanity check - not a substitute for real low-vision user
   feedback.
