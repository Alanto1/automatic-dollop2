# Start here — the first two weeks

You have no parts and nothing built. That's fine: **most of the next month
doesn't need hardware.** This is the order to do things in.

---

## Step 0 — Read the upstream repo (30 minutes, do it today)

<https://github.com/dorianborian/sesame-robot> — Apache 2.0.

Read `docs/build-guide/`, `hardware/bom/`, and `hardware/printing/`. You are
building this robot, so its documentation is now your documentation. Two
things to check while you're in there, because they change what you buy:

- **The battery.** The BOM specifies a Bambu Lab 14500 (7.4V, 800mAh). The
  internal frame is printed around it. If you substitute, verify the physical
  size first — this is the one part where guessing costs you a re-print.
- **ESP32-S2 Mini vs the Sesame Distro Board.** Start with the hand-wired
  S2 Mini. The custom PCB is nicer, but fabbing it adds a lead time and a
  failure mode on your critical path. Treat it as a v2 upgrade.
- **Grab the Fusion 360 sources**, not just the STLs. You're going to restyle
  the shell into a spider (week 4), and you want the editable files.

Then star the repo and note the license. You'll cite it in the writeup, and
"what's mine vs what's upstream" is a question you *will* be asked.

Then read [`BEHAVIOURS.md`](BEHAVIOURS.md) — what the robot actually does,
and what the state machine you're about to write has to drive.

## Step 1 — Place the orders (this week)

Full cart with prices and stock: [`PURCHASE_LIST.md`](PURCHASE_LIST.md).

Order in this sequence, because lead times differ:

1. **AliExpress first** — ESP32-S2 Mini, SSD1306 OLED, **2× VL53L0X**, M2
   screws, tubing, 1000µF caps. Longest lead time, smallest cost. Order it
   before anything else.
2. **roboter-bausatz** — 10× MG90S. Nobody else in Germany stocks them.
3. **BerryBase** — Zero camera, SD cards, buck converters, pump, filament,
   cliff sensors.
4. **Reichelt** — Pi Zero 2 WH, MOSFETs, diodes.
5. **Segor walk-in** — wire, heat-shrink, connectors, spare screws.

**The brain is a Raspberry Pi Zero 2 W**, not a Pi 5 — 11g and ~2W, which is
what Sesame can actually carry. Take the **WH** (headers pre-soldered, €22.10
at Reichelt); you need GPIO for the pump MOSFET and for the link to the ESP32.

### If BerryBase is out of stock

Three items went out of stock during ordering. **None of them are on the
critical path** — all three are Week 6 (perception), and Weeks 0–5 are the
state machine, the printed body, and the water rig.

| Out of stock | Buy instead |
|---|---|
| Pi Zero 2 **WH** | **Reichelt**, order code `RASP PI ZERO2 WH`, €22.10 |
| SanDisk Ultra A1 32GB | Any A1 32GB card, anywhere. Or BerryBase's **Extreme Pro A1 32GB**, €26.90 |
| Camera for Pi **Zero** | Any Pi camera module + a **Zero ribbon adapter** (Reichelt `RPIZ CAM ADAPTER`, €1.10) — the Zero's connector is the narrow one, that cable is the only difference |

## Step 2 — Diagnose the printer (first 48 hours)

Sesame is 11 printed parts. If your printer isn't printing accurately, you
have no robot.

- Print a **20mm calibration cube**. Not within ~0.3mm → not ready for parts
  that hold servo splines.
- **Mechanical fault** (nozzle, belts, bed, PTFE) → fix locally this week.
- **Electronic fault** (driver, thermistor, board) → the replacement part has
  to ride in this week's order, or shipping serialises your whole schedule.
- **Hard gate:** no accurate parts by end of week 2 → pay a print service.
  Sesame's parts are small; a shop quote for 11 parts is cheap against losing
  three weeks.

### Kobra 2 Pro — *"The module is abnormal"*

This is the **auto-levelling strain-gauge module** under the bed, not the
nozzle. The printer taps the nozzle onto it to find Z; when it can't read a
clean tap it throws this. Anycubic's own order of causes, cheapest first:

1. **Stuck buttons.** Press the module's buttons by hand — they must spring
   back. If one is stuck, loosen the screws behind the module slightly
   (M2.0 Allen). Over-tightened screws bind them.
2. **Nozzle isn't over the module.** *Tools → Control → Module Calibration →
   Position Calibration.* The nozzle must land on the module's **centre**.
   Nudge it in the interface, **Save**, then re-level.
3. **Dirt.** Clean the module face — filament debris on it reads as a bad tap.
4. **Loose wiring** (the usual culprit if 1–3 don't fix it). Power off, then:
   remove the touchscreen cable → unscrew the 2 plastic screws underneath
   (M2.5 Allen) → pry the plastic off → unplug **FAN2** → reseat the
   calibration module's cable at **both** ends: the mainboard, and under the
   heated bed's aluminium plate.
5. **Dead module.** Multimeter on **20V DC**: the module's pins on the
   mainboard should read **3.3 V ± 0.3**. Outside that, the module is faulty —
   claim the warranty.

Tools: M2.5 and M2.0 Allen keys, a Phillips, and the multimeter that's already
on your parts list. Do this **before** ordering more filament — and note that
step 5 is exactly the "electronic fault" case above, where the replacement has
to ride in this week's order.

---

## Step 3 — Build the software while the parcels fly

None of this needs a single part, and it's the part that's actually yours.
It's also exactly what worked on the wristband: `HapticMapper` and
`haptic_simulator.html` were both debugged before hardware existed.

### ✅ The mood state machine — written, tested, in the repo

The personality *is* this state machine. CHILL → SUSPICIOUS → WARNING →
STRIKE → SMUG, driven by a `Scene` object. It's in
[`brain/`](brain/README.md), and it needs nothing you don't already have:

```bash
cd brain
./tests/run_tests.sh                  # 19/19 tests passed
open simulator/mood_simulator.html    # toggle the camera, watch it escalate
```

`mood.py` imports only the standard library — no camera, no servos, no clock
of its own. The caller passes `now` in, which is why a 30-second escalation
runs instantly in the tests and why the browser can scrub time.

**Your job now is tuning, not writing.** Open the simulator, turn on
**drop frames**, and push the sliders around until the robot feels right;
then copy the numbers into the constants at the top of `mood.py` and re-run
the tests. The timings are the entire difference between "impressive" and
"annoying" — a robot that squirts you while you're working is a bad robot,
and this is the one part of that judgement you can make today.

Watch `CLEAR_GRACE` in particular: it's the de-escalation delay, it is
deliberately *not* symmetric with the escalation dwells, and the reason is in
[`brain/README.md`](brain/README.md).

### Detection, on video files

You don't need the Pi or the camera to start. Record 20 minutes of yourself at
a desk on your phone — working, picking up your phone, leaving — and run
YOLOv8n over it on your laptop.

- Hand-label "working" / "on phone" / "gone", then measure how often the
  detector agrees.
- **Test at 1–2 FPS**, not full frame rate. That is what a Pi Zero 2 W will
  actually give you, and you want to know now whether your thresholds survive
  it. Sample every 15th frame or so.
- Derive "head down" from **bounding-box geometry**, not MediaPipe Pose —
  512MB alongside the detector won't take it.
- **This gives you real false-positive numbers before you own a robot**, which
  is the most valuable thing you can carry into the build.

### Prototype the motion engine in a browser

The thing that stops it looking stiff, and it needs no hardware. Draw a
2-DOF leg on a canvas and animate it:

- Compare a hard step to target vs a **cubic ease-in-out** ramp — you'll see
  the difference instantly.
- Add **idle breathing** (±2–3° at ~0.2 Hz) and watch it come alive.
- Add anticipation before a lunge, overshoot-and-settle after.

Same trick as `haptic_simulator.html`: get the feel right on screen, then port
the curves to the ESP32. See README "Making it move like a creature".

### Learn Sesame's JSON API

The seam between your code and the robot. Read the firmware's API, then write
a thin Python client — `stand()`, `walk(dir)`, `turn(deg)`, `face(mood)` —
against a **fake** robot that just logs. When real hardware arrives you swap
the transport and everything above it already works.

Keep the transport behind that seam deliberately: you'll start on WiFi
(no firmware change) and probably move to UART later, since the two boards end
up 5cm apart on the same robot.

### The experiment and the paperwork

Costs nothing, and it's what turns a gag into a project:

- Consent form (you already do this well on the wristband).
- Questionnaire: motivation 1–5, annoyance 1–5, "would you use this?"
- Decide exactly what you log: phone pickups, on-task minutes.
- Line up 8–15 volunteers — recruiting always takes longer than you think.
- Confirm which competition and its real deadline.

---

## Suggested order of the next four weeks

| When | Do |
|---|---|
| **This week** | Read the Sesame repo. Place all five orders. Diagnose the printer. |
| **Week 1** | Mood state machine + tests + browser visualiser. |
| **Week 2** | Print Sesame's parts. Prototype easing + breathing in a browser. |
| **Week 3** | Assemble Sesame, calibrate servos, get it walking on stock firmware. |
| **Week 4** | Python client against the JSON API. Consent form, questionnaire, volunteers. |

By the time you're integrating, you have a walking robot, a tested
personality, and real detection numbers. That's the difference between
assembling a robot and assembling a *project*.

---

## What not to do yet

- **Don't modify Sesame's firmware or CAD until it walks stock.** You *will*
  modify both — the motion engine is firmware, the spider shell is CAD — but
  get the known-good design working first, or you won't know whether a fault
  is yours or an assembly error.
- **Don't touch the internal frame or the leg pivot geometry.** That's the
  part that took its author four months to get walking. Restyle the shell.
- **Don't fab the custom PCB.** Hand-wire the S2 Mini. Add the board later.
- **Don't mount the water rig before the state machine works.** The pump is
  the easy part; knowing *when* to fire is the hard part.
- **Don't buy a Coral/Hailo accelerator.** Try the Pi alone. ~€60–70 for a
  problem you may not have.
- **Don't skip the metal-gear check** on the servos. MG90S, not SG90.
