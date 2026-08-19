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
what Sesame can actually carry. The **WH** (headers pre-soldered) is the
convenient variant; you need GPIO for the pump MOSFET and for the link to the
ESP32. Read the next section before ordering it, though.

### 🔴 The Pi Zero 2 W is sold out across Europe

Checked **2026-08-18**. This is not a BerryBase problem, it's a global one:

| Shop | Zero 2 W / WH |
|---|---|
| BerryBase | sold out |
| Reichelt (both `W` and `WH`) | *temporarily unavailable* |
| Technik-LPE | backorder — stock level **−156** |
| buyzero.de, Pimoroni, The Pi Hut | sold out |
| **Farnell DE** | orderable — **deliveries begin 10 March 2027** |

**✅ Resolved 2026-08-18: restock date is 25 September 2026.** That is five
weeks out, and Week 6 (perception) is the first week that needs the board — so
it lands just in time. **Do not pay a scalper.** Instead:

1. **Get in the queue now** — back-order or set the back-in-stock alert at
   BerryBase *and* Reichelt (their page has a "Message if back in stock"
   button). Order from two shops and cancel the loser; a €19 board ordered
   twice is a €19 risk, and restock dates slip.
2. **Pull the perception work forward** into Weeks 1–5, where it needs only
   your laptop and recorded video. See `BUILD_CHECKLIST.md`. This is the
   actual fix: it converts the delay into zero schedule impact.
3. **Decision gate: if the board has not shipped by 10 October**, stop waiting
   and take option 2 or 3 below. Don't let a slipping restock date eat Week 7.

If the date slips or you want the board sooner, the options below still stand.

Waiting past the competition is not a plan. Three options, best first:

1. **Buy one at a markup.** eBay.de / Amazon.de marketplace, roughly €35–50
   against a €22 list price. Costs ~€25 extra and **changes nothing else** —
   same pinout, same OS, same `picamera2`, same everything already written
   down here. For a one-board project this is almost certainly right.
2. **Radxa Zero 3W.** Same 65×30mm footprint, Pi-compatible 40-pin header,
   quad Cortex-A55, real Debian, and **1–8 GB of RAM** instead of 512 MB —
   the 4 GB version would even let the LLM run on the robot, which
   [`LLM_VOICE.md`](LLM_VOICE.md) currently proves impossible. Costs: the
   camera stack is not Raspberry Pi's, so plan on a **USB webcam** rather than
   a CSI module, and budget extra time in Week 6. ~€95 for 4 GB/32 GB in
   Germany; the small variants are much cheaper where you can find them.
3. **Second-hand.** Plenty of Zero 2 Ws sit unused in finished projects.

**Do not buy a Pi Zero W (no "2").** One ARM11 core instead of four — already
documented as a wrong buy in [`PURCHASE_LIST.md`](PURCHASE_LIST.md).

### The SD card and the camera — both still in stock

| Item | € | Verdict |
|---|---|---|
| **SanDisk Extreme Pro microSDHC A1 U3 32 GB + adapter** | 26.90 | ✅ **buy it.** A1 / V30 / UHS-I U3, 100 MB/s, SD adapter included. Works with any of the three brains above, so it's safe to order before the Pi is settled |
| **Camera for Raspberry Pi Zero, 15 cm** (`RPIZ-CAM-15`) | 17.50 | ✅ the right camera — 53.5° |
| ~~Camera, adjustable focus, 160° FOV~~ (`RPIZ-CAM-VF`) | 18.90 | ❌ the fisheye — see below |
| ~~Camera cable adapter Zero > standard camera~~ (`RPIC-ZSAD`) | 1.20 | ❌ **not needed**, and it runs the other way |

**The adapter is the opposite of what it sounds like.** `RPIC-ZSAD` lets a
*Zero* camera plug into a *standard* Pi. Both cameras above already ship with
the narrow Zero cable, so on a Pi Zero you need nothing extra.

**Why not the 160° fisheye.** Wide angle sounds better and is a trap. The
detector has to find a **phone**, and a phone is small:

```
  phone ~7cm wide, seen from 60cm away  =  6.7 degrees of view
  YOLOv8n input is 320px wide

  53.5 deg lens (RPIZ-CAM-15)   320/53.5 = 6.0 px/deg  ->  40 px on the phone
  170 deg lens (RPIZ-CAM-VF)    320/170  = 1.9 px/deg  ->  13 px on the phone
```

Both use the same 5 MP OV5647 sensor — the fisheye just spreads it over three
times the angle, putting **~3× fewer pixels on the one thing you must detect**.
13 px is at YOLOv8n's floor before you even add the barrel distortion, which
YOLO was never trained on. Take the 53.5°.

⚠️ But 53.5° *is* narrow: at 60 cm it frames about 60 cm across. Check this
during the recorded-video work in Step 3 — crop your phone footage to 53.5°
and confirm the head is still in shot, because "head down" needs the head. If
it isn't, raise the camera mount rather than widening the lens.

**Order sequence:** SD card now (works with anything) → **Pi next**, it's the
long pole → **camera last**, since its interface depends on which brain wins.

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

### ✅ Detection, on video files — tooling written

All five tools are in [`perception/`](perception/README.md) with a
step-by-step guide. `./tests/run_tests.sh` → 18/18. What's left is yours:
record the footage, label it, read your numbers.

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

### ✅ Prototype the motion engine in a browser — built

[`motion/leg_simulator.html`](motion/README.md) — open it, click **lunge**,
watch the plot. Exports the tuned constants as a C header for the ESP32.

The thing that stops it looking stiff, and it needs no hardware. Draw a
2-DOF leg on a canvas and animate it:

- Compare a hard step to target vs a **cubic ease-in-out** ramp — you'll see
  the difference instantly.
- Add **idle breathing** (±2–3° at ~0.2 Hz) and watch it come alive.
- Add anticipation before a lunge, overshoot-and-settle after.

Same trick as `haptic_simulator.html`: get the feel right on screen, then port
the curves to the ESP32. See README "Making it move like a creature".

### ✅ Learn Sesame's JSON API — client written

[`client/sesame.py`](client/README.md) — `stand/walk/turn/face` over a
swappable transport, 13/13 tests against a fake robot that only logs.

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
