# Build checklist — The Enforcer

One rule, same as your wristband: **never be in a state where nothing works.**
Every phase ends in something you could demo that day. If you run out of time,
you still have a show.

Concept and architecture: [`README.md`](README.md). What to buy:
[`PARTS.md`](PARTS.md) and [`PURCHASE_LIST.md`](PURCHASE_LIST.md). What to do
before parts arrive: [`START_HERE.md`](START_HERE.md).

**Order of attack:** get **Sesame walking on stock firmware** first, then
**Squirt mode stationary** end-to-end, then combine, then Warden.

The plan is shorter than it used to be, because you're no longer designing a
body. Weeks 0–4 of the old plan (leg IK, one leg, all legs, power rails) are
now "build Sesame as documented."

---

## Days 1–2 — Printer + upstream repo

- [ ] Read <https://github.com/dorianborian/sesame-robot> — build guide, BOM,
      printing notes
- [ ] Print a 20mm calibration cube; not within ~0.3mm → printer isn't ready
- [ ] Mechanical or electronic fault? Electronic → the part rides in this
      week's order
- [ ] Gate: *no accurate parts by end of week 2 → pay a print service*

## Week 0 — Order everything, start the state machine

- [x] ~~Sourcing pass~~ — done, see [`PURCHASE_LIST.md`](PURCHASE_LIST.md)
- [x] ~~Hexapod vs quadruped~~ — **quadruped**
- [x] ~~Design the body~~ — **no: build Sesame** (8 servos, 2 per leg)
- [ ] Decide **Pi 5 2GB (€69,50) vs 4GB (€118,50)** — gates the BerryBase order
- [ ] Place the **AliExpress** order FIRST (ESP32-S2 Mini, SSD1306, M2 screws,
      tubing) — longest lead time, smallest cost
- [ ] Place **roboter-bausatz** (10× MG90S — nobody else in Germany stocks them)
- [ ] Place **BerryBase** (Pi, camera, SD ×2, pump, cliff sensors, filament, PSU)
- [ ] Walk in to **Segor** (Kaiserin-Augusta-Allee 94; closed 13:30–14:30)
- [ ] Check the battery physically fits Sesame's undercarriage before buying

Meanwhile, zero hardware:

- [ ] **Mood state machine** — fake `scene` events (phone / head-down /
      absent) → CHILL → SUSPICIOUS → WARNING → STRIKE → SMUG
- [ ] **Test it**: 2s phone → no fire; 4s → escalate; person returns
      mid-escalation → de-escalates cleanly, never stuck
- [ ] Browser visualiser, like `haptic_simulator.html`

**Demoable:** the state machine, on screen, with attitude.

---

## Weeks 1–2 — Print and assemble Sesame

Follow the upstream build guide. Don't improvise.

- [ ] Print the 11-part set in PLA
- [ ] **Centre every servo before installing a single horn** — upstream says
      it, your old checklist said it, and it's still the #1 way to lose a day
- [ ] Hand-wire the ESP32-S2 Mini harness (skip the custom PCB for now)
- [ ] Install OLED + power switch in the top cover
- [ ] Main assembly, route wires into the underside channels
- [ ] Flash stock firmware; run the motor tester; fix any wrong-slot motors
- [ ] Calibrate

**Demoable:** it walks, poses, and pulls faces, driven from the web page.
That's already a robot on a table.

---

## Week 3 — Weigh it, then decide the water rig

Do this **before** designing anything around the reservoir.

- [ ] Weigh the finished Sesame
- [ ] Tape a 50ml water bottle to it. Does it still walk? Now 100ml?
- [ ] **Decide reservoir size from that measurement**, not from hope
- [ ] If it can't walk loaded → Squirt mode goes stationary (scope ladder),
      and that's a fine project
- [ ] Wire the pump via **MOSFET + flyback diode**; fire it dry, then wet
- [ ] ⚠️ **Brownout test:** pump + all servos moving at once. Sesame's firmware
      already staggers servos by 20ms because of this. If it browns out, give
      the pump its own cell

**Demoable:** it squirts on command.

## Week 4 — Perception

- [ ] Camera on the desk, streaming into OpenCV on the Pi
- [ ] Person + `cell_phone` detection (YOLOv8n)
- [ ] Head-pitch / presence via MediaPipe
- [ ] Detect the **robot** in frame too — you need its position to aim it
- [ ] Wrap it all into one `scene` object the state machine reads
- [ ] **Tune against false positives.** It must NOT fire while you work

**Demoable:** on screen, correct labels for "working" / "on phone" / "gone."

## Week 5 — Wire the brain to the body

- [ ] Python client for Sesame's JSON API: `stand`, `walk`, `turn`, `face`
- [ ] Mood → face expression mapping (Sesame ships faces; add your own)
- [ ] Mood → body language via **Sesame Studio**: perk-up, creep-in, victory
      bounce, cooldown settle
- [ ] Randomise timing so it never loops identically
- [ ] Speaker + a handful of pre-recorded taunt clips

**Demoable:** it *reacts* with attitude to what it sees — no squirt needed.

## Week 6 — Squirt mode, end to end

- [ ] Aiming: from the desk camera, turn the robot until it faces the target
- [ ] Full loop: detect slacking → escalate through moods → aim → fire
- [ ] Safety pass: nozzle outward and slightly down, **never** the face;
      consent framing ready
- [ ] Add a hardware disable — a switch that makes it physically unable to fire

**Demoable: the flagship works.** This alone is a complete project.

## Week 7 — Autonomous walking

- [ ] **Cliff sensors first** — it must refuse to step off the desk edge
- [ ] Walk toward a target under closed-loop control from the desk camera
- [ ] Tune until it crosses a desk without stumbling
- [ ] Note: 2 DOF per leg — it turns by differential gait, not by hip swivel

**Demoable:** it walks to you, *then* squirts you.

## Week 8 — Warden mode

- [ ] Phone-on-tray test; if payload fails, switch to guard-and-block
- [ ] Reactive avoidance: hand approaches → walk away from it
- [ ] Session timer state machine (locked until time's up)

**Demoable:** hand over your phone, try to grab it back, chase the robot.

---

## Week 9 — Harden it

- [ ] One-hour continuous run; log and fix every crash
- [ ] Servo temperature after sustained walking
- [ ] Watchdog: a hung subsystem recovers instead of freezing mid-demo
- [ ] **WiFi failure behaviour** — new risk in this architecture. The robot
      must fail *safe and still*, not last-command-forever, if the Pi drops off
- [ ] Water-safety recheck; cable strain relief
- [ ] Battery runtime measured and written down

## Week 10 — The experiment

- [ ] Run it: 8–15 volunteers, timer-vs-Enforcer, counterbalanced, written
      consent (see README "The experiment")
- [ ] Log phone pickups, on-task minutes, questionnaire
- [ ] Analyse; write up honestly, including the acceptability trade-off

## Week 11 — Rehearsal

- [ ] Demo to 5 people who aren't you; fix what confuses them
- [ ] Rehearse failures: someone works normally (no false squirt), WiFi off,
      a stranger tries to fool it
- [ ] Charge spare battery; flash + test spare SD card
- [ ] Photos + video of it working, taken **before** demo day

## Week 12 — Buffer + submit

- [ ] Whatever broke in week 11
- [ ] **Writeup: what's Sesame's, what's yours, what it can't do.** The table
      in README is the answer — have it on a slide
- [ ] Credit Sesame (Apache 2.0) clearly, in the writeup *and* on the poster
- [ ] Competition registration (confirm which fair and its real deadline)

---

## Demo-day rules

- The room wants **comedy**: a volunteer sneaks a phone, gets soaked. Let
  people try to beat it.
- The jury wants **rigor**: live detection view on a screen, experiment
  numbers ready, and a clean answer to "what did you actually build?"
- **Bring your own WiFi** (phone hotspot or a travel router). The whole
  architecture depends on the Pi reaching the robot — do not trust venue WiFi.
- Bring a **towel** and a target cup. Obvious, and everyone forgets.
