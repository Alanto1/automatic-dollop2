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

Then star the repo and note the license. You'll cite it in the writeup, and
"what's mine vs what's upstream" is a question you *will* be asked.

## Step 1 — Place the orders (this week)

Full cart with prices and stock: [`PURCHASE_LIST.md`](PURCHASE_LIST.md).

Order in this sequence, because lead times differ:

1. **AliExpress first** — ESP32-S2 Mini, SSD1306 OLED, M2 screws, tubing.
   Longest lead time, smallest cost. Order it before anything else.
2. **roboter-bausatz** — 10× MG90S. Nobody else in Germany stocks them.
3. **BerryBase** — Pi, camera, SD cards, pump, filament, cliff sensors.
4. **Segor walk-in** — MOSFETs, diodes, wire, heat-shrink.

**One decision gates the BerryBase order: Pi 5 2GB (€69.50) or 4GB (€118.50).**
Recommendation is 2GB — see `PURCHASE_LIST.md`. It's a desk unit, so a later
upgrade is swapping a board, not re-engineering a robot.

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

---

## Step 3 — Build the software while the parcels fly

None of this needs a single part, and it's the part that's actually yours.
It's also exactly what worked on the wristband: `HapticMapper` and
`haptic_simulator.html` were both debugged before hardware existed.

### The mood state machine (highest value — do this first)

The personality *is* this state machine. CHILL → SUSPICIOUS → WARNING →
STRIKE → SMUG, driven by a `scene` object.

- Feed it **fake** scene events: `phone_visible`, `head_down`, `no_person`.
- Get the **timers and hysteresis** right. This is the hard part, it needs
  zero hardware, and it is the entire difference between "impressive" and
  "annoying." A robot that squirts you while you're working is a bad robot.
- Unit-test it: phone visible 2s → no fire; 4s → escalate; person returns
  mid-escalation → de-escalate cleanly, not stuck in WARNING forever.
- Browser visualiser, like `haptic_simulator.html`, so you can *see* it.

### Detection, on video files

You don't need the Pi or the camera to start. Record 20 minutes of yourself at
a desk on your phone — working, picking up your phone, leaving — and run
YOLOv8n + MediaPipe over it on your laptop.

- Hand-label "working" / "on phone" / "gone", then measure how often the
  detector agrees.
- **This gives you real false-positive numbers before you own a robot**, which
  is the most valuable thing you can carry into the build.

### Learn Sesame's JSON API

The seam between your code and the robot. Read the firmware's API, then write
a thin Python client — `stand()`, `walk(dir)`, `turn(deg)`, `face(mood)` —
against a **fake** robot that just logs. When real hardware arrives you swap
the transport and everything above it already works.

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
| **This week** | Read the Sesame repo. Place all four orders. Diagnose the printer. |
| **Week 1** | Mood state machine + tests + browser visualiser. |
| **Week 2** | Print Sesame's parts. Record desk footage; run detection on it. |
| **Week 3** | Assemble Sesame, calibrate servos, get it walking on stock firmware. |
| **Week 4** | Python client against the JSON API. Consent form, questionnaire, volunteers. |

By the time you're integrating, you have a walking robot, a tested
personality, and real detection numbers. That's the difference between
assembling a robot and assembling a *project*.

---

## What not to do yet

- **Don't modify Sesame's firmware or CAD until it walks stock.** Get the
  known-good design working first, or you won't know whether a fault is yours
  or an assembly error.
- **Don't fab the custom PCB.** Hand-wire the S2 Mini. Add the board later.
- **Don't mount the water rig before the state machine works.** The pump is
  the easy part; knowing *when* to fire is the hard part.
- **Don't buy a Coral/Hailo accelerator.** Try the Pi alone. ~€60–70 for a
  problem you may not have.
- **Don't skip the metal-gear check** on the servos. MG90S, not SG90.
