# Build checklist — The Enforcer

One rule, same as your wristband: **never be in a state where nothing works.**
Every phase ends in something you could demo that day. If you run out of time,
you still have a show.

Specs/prices: [`PARTS.md`](PARTS.md). Concept, safety, experiment:
[`README.md`](README.md).

Order of attack: get **Squirt mode working stationary first** (detect →
escalate → aim → fire), then add walking, then the other two modes.

---

## Days 1–2 — Diagnose the printer

- [ ] Mechanical or electronic fault? (see PARTS.md)
- [ ] Electronic → add the replacement part to the Week 0 order
- [ ] Print a 20mm calibration cube; if not within ~0.3mm, the printer isn't
      ready for structural parts
- [ ] Sticky-note the gate: *no accurate parts by end of week 2 → buy the chassis*

## Week 0 — Order everything, build the simulator

Procurement is the long pole. Nothing else matters until the order is placed.

- [ ] Sourcing pass (Reichelt / Conrad / BerryBase / local Berlin shops / AliExpress)
- [ ] Place **one** order with spares (3 servos, 2nd SD card, 2nd pump) + any
      printer part
- [ ] Note the delivery window somewhere visible
- [ ] Decide: hexapod vs quadruped (see README "Open decisions")

Meanwhile, zero hardware:

- [ ] **Leg IK simulator** in the browser or Python — drag a foot target,
      watch the 3 joint angles solve
- [ ] **Unit-test the IK** (known target → known angles; unreachable case)
- [ ] **Mood state-machine simulator** — feed it fake "scene" events
      (phone/head-down/absent) and watch it walk CHILL → SUSPICIOUS →
      WARNING → STRIKE → SMUG, with the hysteresis/timers tuned. Test it.

This is the `HapticMapper` + `haptic_simulator.html` move again: debug the
logic before hardware exists.

**Demoable:** the two simulators.

---

## Weeks 2–3 — One leg, then the body

- [ ] Assemble one leg (3 servos); Pi set up (SSH, Wi-Fi, servo library)
- [ ] PCA9685 over I2C, one servo sweeping
- [ ] **Center every servo before bolting on horns** (or you fight offsets forever)
- [ ] Port IK from the sim; verify against the same test cases
- [ ] Per-servo min/max/center offsets in one config file
- [ ] Remaining legs assembled + calibrated

**Demoable:** a foot traces a circle; the body stands and shifts its weight.

---

## Week 4 — Power (the make-or-break week)

- [ ] Build both rails: UBEC (servos) + buck (Pi), **common ground**, inline fuse
- [ ] **Brownout test:** drive all servos to a stall pose — the Pi must NOT reboot
- [ ] Wire the **pump via MOSFET + flyback diode** off a GPIO; fire it dry, then wet
- [ ] Measure battery runtime; write it down

**Demoable:** it stands on its own power and squirts on command.

---

## Week 5 — Perception (the AI)

- [ ] Camera streaming into OpenCV
- [ ] Person + `cell_phone` detection (YOLOv8n / MobileNet-SSD / MediaPipe)
- [ ] Head-pitch (looking down) via MediaPipe Face/Pose
- [ ] "No person at desk" detection
- [ ] Wrap all of it into a single `scene` object the state machine reads
- [ ] **Tune against false positives** — it must NOT fire while you're working.
      Add hysteresis + time thresholds (e.g. phone visible > 3s)

**Demoable:** on a screen, it correctly labels "working" vs "on phone" vs "gone."

---

## Week 6 — Personality

- [ ] GC9A01 eye: chill / suspicious / alarmed / smug expressions
- [ ] Body language on the legs: perk-up, creep-in, victory bounce, cooldown settle
- [ ] Speaker + a handful of pre-recorded taunt clips
- [ ] Wire the state machine's mood → eye + body + sound; randomize timing

**Demoable:** it *reacts* with attitude to what it sees — still no squirt needed to impress.

---

## Week 7 — Squirt mode, end to end

- [ ] Camera + nozzle on the pan/tilt head
- [ ] **Visual servoing:** PID on pan/tilt to center the target; fire when
      centered + in STRIKE
- [ ] Full loop: detect slacking → escalate through moods → aim → pulse pump
- [ ] Safety pass: nozzle aims outward/down, never face; consent framing ready

**Demoable: the flagship works.** This is already a complete, room-stopping project.

---

## Week 8 — Posture Sheriff mode

- [ ] Neck/torso angle from a side view (MediaPipe Pose)
- [ ] Slouch threshold + hold time → escalate → respond
- [ ] Add it as a **Mode** object alongside Squirt (shared pipeline)

**Demoable:** slouch → it busts you; sit up → it approves.

---

## Week 9 — Warden / run-away mode

- [ ] **Cliff sensors** first — it must refuse to step off the desk edge
- [ ] Reactive avoidance: hand approaches → walk away from it
- [ ] Phone-on-tray test; if payload fails, switch to guard-and-block (README)
- [ ] Session timer state machine (locked until time's up)

**Demoable:** hand off phone, try to grab it back, chase the fleeing spider.

---

## Week 10 — Harden it

- [ ] One-hour continuous run; log and fix every crash
- [ ] Servo temperature after sustained walking
- [ ] Watchdog: a hung subsystem recovers instead of freezing mid-demo
- [ ] Water-safety recheck; cable strain relief (moving legs eat wires)
- [ ] Threadlock / recheck every mechanical joint

---

## Week 11 — The experiment + rehearsal

- [ ] Run the focus study: 8–15 volunteers, timer-vs-Enforcer, counterbalanced
      (see README "The experiment"); written consent
- [ ] Log phone pickups, on-task minutes, questionnaire
- [ ] Analyze; write up honestly (including acceptability trade-off)
- [ ] Demo it to 5 people who aren't you; fix what confuses them
- [ ] Rehearse failures: someone works normally (no false squirt), network off,
      a stranger tries to fool it
- [ ] Charge spare battery; flash + test spare SD card

---

## Week 12 — Buffer + submit

- [ ] Whatever broke in week 11
- [ ] Writeup: what's yours, what's a kit/library, what it can't do
- [ ] Photos + video of it working, taken **before** demo day
- [ ] **Jugend forscht registration** (confirm the deadline early!)

---

## Demo-day rules (both audiences)

- The room wants **comedy**: a volunteer sneaks a phone, gets soaked. Let people
  try to beat it.
- The jury wants **rigor**: have the live detection view on a screen, and your
  experiment's numbers ready.
- **Phone hotspot** if any cloud is involved; hard-code offline behavior so it's
  never mute/frozen.
- Bring a **towel** and a target cup. Obvious, and everyone forgets.
