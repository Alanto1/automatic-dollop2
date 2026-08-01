# Build checklist — 12 weeks

One rule: **never be in a state where nothing works.** Every phase below
ends in something you could demo that day. If you run out of time at any
point, you still have a show.

Specs and prices live in [`PARTS.md`](PARTS.md). Scope, architecture, and
the de-scope ladder live in [`README.md`](README.md).

---

## Days 1–2 — Diagnose the printer

Before anything else, because the answer changes your order.

- [ ] Identify the fault. Mechanical (nozzle, belts, bed, PTFE) or
      electronic (driver, thermistor, mainboard)?
- [ ] Mechanical → source locally, fix this week
- [ ] Electronic → **add the replacement part to the week-1 order**
- [ ] Print a 20mm calibration cube. Measure it. If it's not within
      ~0.3mm on all axes, the printer is not ready for structural parts
- [ ] Write the gate on a sticky note: *no accurate parts by end of week
      2 → buy the chassis*

---

## Week 1 — Order everything, build the simulator

Procurement week. Nothing else matters until the order is placed.

- [ ] Sourcing pass: Alash Electronics / Тастак shops / Kaspi / AliExpress
- [ ] Place **one** order, including spares (3 extra servos, 2nd SD card,
      spare nozzle) and any printer repair part
- [ ] Note the expected delivery window somewhere visible

Meanwhile, with zero hardware:

- [ ] Browser simulator for one leg's **inverse kinematics** — drag a
      target point, watch the three joint angles solve
- [ ] Unit-test the IK: known target → known angles, plus the
      unreachable-target case
- [ ] Extend the sim to four legs and step through a **crawl gait**
      (one foot moves at a time, three always down — statically stable,
      no balance control needed)

This is the same move as `haptic_simulator.html` and the `HapticMapper`
tests on the wristband: debug the math in a day instead of blaming
servos for two weeks. It's the strongest habit you already have.

**Demoable:** the simulator itself.

---

## Weeks 2–3 — One leg

Parts are in transit for most of this. Build what you can.

- [ ] Frame: print leg segments (or assemble the kit chassis)
- [ ] Assemble **one** leg, three servos
- [ ] Pi set up: SSH, Wi-Fi, `adafruit-circuitpython-servokit`
- [ ] PCA9685 talking over I2C, one servo sweeping
- [ ] **Set every servo to its centre position before bolting on horns** —
      otherwise your range is offset and you'll fight it for weeks
- [ ] Port the IK from the simulator, verify against the same test cases
- [ ] Calibrate: per-servo min/max/centre offsets in one config file

**Demoable:** the foot traces a circle in the air on command.

---

## Weeks 4–5 — It walks

- [ ] Remaining three legs assembled and calibrated
- [ ] **Power rails built properly** — separate UBEC and buck, common
      ground, inline fuse (see PARTS.md wiring diagram)
- [ ] Brownout test: all 12 servos to a stall position, confirm the Pi
      does not reboot. Fix this now, not in week 11
- [ ] Crawl gait: forward, backward, turn in place, stop
- [ ] Body pose control (lean, height, tilt) — cheap to add, and it's
      most of what makes the idle behaviour convincing later
- [ ] Battery runtime measured, written down

**Demoable: it walks.** People already care at this point.

---

## Week 6 — It's alive

The cheapest personality you will ever buy.

- [ ] GC9A01 eye display wired over SPI, rendering
- [ ] Eye animations: blink, saccade, look-toward-a-direction, and a
      **thinking** state (you'll need it in week 7)
- [ ] Camera + face detection running at a usable frame rate
- [ ] Body turns to face whoever it detects
- [ ] **Idle behaviour loop**: when nothing is happening, shift weight,
      look around, occasionally stretch a leg. Randomised timing — a
      fixed loop reads as a machine

**Demoable: it notices you.** This is a bigger jump than it sounds.

---

## Weeks 7–8 — It talks

- [ ] Audio in/out working on the Pi (test both before writing any logic)
- [ ] Push-to-talk button first. Wake-word only if there's time left over
- [ ] Speech-to-text, **streaming**
- [ ] LLM call with **tool/function calling**; tools are named intents:
      `walk_forward`, `turn_to`, `look_at`, `wave`, `sit`, `stop`
- [ ] Text-to-speech, **streaming** — first audio out before the sentence
      is finished
- [ ] Eye shows the thinking animation during the gap
- [ ] **Measure end-of-speech → first-audio latency. Target under 1.5s**
- [ ] Hard-coded offline fallback answers for 5–10 likely questions
- [ ] `stop` intent works *while* it is speaking or walking

**Demoable: talk to it, it answers and acts.**

---

## Week 9 — It perceives

The moment the whole project is built around.

- [ ] Camera frame → vision model, wired in as another LLM tool
- [ ] "What am I holding?" → **it turns to look first**, then answers.
      The turn is the demo; do not let it answer without moving
- [ ] "Which of us is wearing red?" → scans the group, then points a leg
- [ ] Graceful failure text for when the model is unsure — never a
      confident wrong answer delivered flatly

**Demoable: the moment.**

---

## Week 10 — Harden it

The gap between "works in my room" and "works in a hall full of
strangers" is entirely in this week.

- [ ] One-hour continuous run. Log every crash and fix each one
- [ ] Servo temperature after sustained walking — they get hot, and hot
      servos drift and die
- [ ] Watchdog: if a subsystem hangs, the robot recovers instead of
      freezing mid-demo
- [ ] Network-loss path: pull the hotspot, confirm fallback answers fire
- [ ] Cable strain relief everywhere. Moving legs eat wires
- [ ] Everything mechanical threadlocked or double-checked

---

## Week 11 — Rehearse the failures

- [ ] Demo it to **5 real people who aren't you.** Watch where they get
      confused and fix that, not what you think is weak
- [ ] Deliberately: kill the network mid-demo; talk over it; interrupt it
      mid-sentence; let a stranger give it a nonsense command
- [ ] Full presentation slot on a single battery charge
- [ ] Demo script written: what you say, what you ask it, in what order
- [ ] Opening line that survives a noisy room, delivered while it's
      already idling and looking around — never start with a frozen robot
- [ ] Spare battery charged. Spare SD card flashed and tested

---

## Week 12 — Buffer

Not padding. A servo will die, a print will warp, an ordered part will be
the wrong voltage. Projects that plan to finish on the last day finish
after it.

- [ ] Whatever broke in week 11
- [ ] Writeup: what's yours, what's the kit/open design, what it can't do
- [ ] Photos and video of it working, taken **before** demo day
