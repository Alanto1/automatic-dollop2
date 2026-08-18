# Build checklist — The Enforcer

One rule, same as your wristband: **never be in a state where nothing works.**
Every phase ends in something you could demo that day. If you run out of time,
you still have a show.

Concept and architecture: [`README.md`](README.md). How each behaviour works
end to end: [`BEHAVIOURS.md`](BEHAVIOURS.md). What to buy:
[`PARTS.md`](PARTS.md) and [`PURCHASE_LIST.md`](PURCHASE_LIST.md). What to do
before parts arrive: [`START_HERE.md`](START_HERE.md).

**Order of attack:** get **Sesame walking on stock firmware** first, then the
**motion engine** (this is what stops it looking stiff), then **Squirt mode**
end-to-end, then Warden.

Stock first is not optional: it's how you know a later fault is yours and not
an assembly error.

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
- [x] ~~Pi 5 2GB vs 4GB~~ — **neither: Pi Zero 2 W**, which is the largest
      brain that fits Sesame's weight and power budget
- [ ] Place the **AliExpress** order FIRST (ESP32-S2 Mini, SSD1306, M2 screws,
      tubing) — longest lead time, smallest cost
- [ ] Place **roboter-bausatz** (10× MG90S — nobody else in Germany stocks them)
- [ ] Place **BerryBase** (buck ×2, pump, TCRT5000 ×4, filament)
- [ ] Place **Reichelt** (Pi Zero 2 **WH** `RASP PI ZERO2 WH` €22.10, MOSFETs,
      diodes) — ⚠️ BerryBase is out of the Zero, the A1 SD card and the Zero
      camera. All three are Week 6 parts, so none of them block anything.
      Substitutes in [`START_HERE.md`](START_HERE.md#if-berrybase-is-out-of-stock)
- [ ] Place **Bambu Lab EU** — 2× 14500 pack + the **XH2.54 charger** (€4.49).
      A balance charger cannot charge this pack; see PURCHASE_LIST
- [ ] Walk in to **Segor** (Kaiserin-Augusta-Allee 94; closed 13:30–14:30)

Meanwhile, zero hardware:

- [x] ~~**Mood state machine**~~ — [`brain/mood.py`](brain/README.md). Scene →
      CHILL → SUSPICIOUS → WARNING → STRIKE → SMUG, pure logic, injected clock
- [x] ~~**Test it**~~ — `brain/tests/run_tests.sh`, **19/19**. Covers: below
      notice → ignored; the full ladder; one shot per episode; a dropped frame
      doesn't reset escalation; putting the phone away de-escalates cleanly;
      an empty chair can never fire; a refused shot stays angry
- [x] ~~Browser visualiser~~ — `brain/simulator/mood_simulator.html`, with a
      frame-dropping switch and sliders for all six timings
- [ ] **Tune the timings** in the simulator until it feels right, then copy
      them into `mood.py` and re-run the tests

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

## Week 3 — The motion engine (this is what makes it feel alive)

The single highest-impact week in the plan, and it's the thing that separates
"3D print that twitches" from "creature." See README "Making it move like a
creature". Runs on the **ESP32**, not the Pi — smooth motion needs steady
timing.

- [ ] **Characterise the 20ms stagger.** Ramp all 8 servos in ~1° steps at
      50 Hz with no stagger. Does the board reset? Write down the rate and
      step size where it starts to
- [ ] If it browns out: **1000µF+ bulk capacitance** across the servo rail,
      then retest. Cheaper than a bigger battery
- [ ] **Easing** — cubic or sine ease-in-out between poses at 30–50 Hz,
      instead of commanding the target angle directly
- [ ] **All joints over one time window**, small per-joint phase offsets
- [ ] **Idle breathing** — ±2–3° at ~0.2 Hz. Biggest "alive" cue for the least
      work. Do this one first
- [ ] **Anticipation + follow-through** on the lunge and the victory bounce
- [ ] **Jitter timings ±15%** so it never loops identically
- [ ] Film it before and after. That comparison belongs in the writeup

**Demoable:** it breathes, creeps, and lunges like something alive — with no
AI attached yet.

## Week 4 — Restyle the shell (make it a spider)

- [ ] ⚠️ **Weigh the robot, set `SESAME_MASS_G`, re-run `make_stl.py --test`**
      for your real torque budget before changing anything
- [ ] Open Sesame's Fusion 360 sources. **Change the shell, not the frame or
      the leg pivots**
- [ ] Keep the foot within the computed reach limit (~48mm at 507g). Get the
      spider from *shape* — angular shell, low body, knees-up — not from
      longer legs, which the servos cannot pay for
- [ ] Spider eyes on the OLED instead of dog eyes. Free identity
- [ ] Re-print, re-assemble, confirm it still walks

**Demoable:** it's recognisably *your* robot now.

## Week 5 — Weigh it, then decide the payload

Do this **before** designing anything around the reservoir.

- [ ] Weigh the finished Sesame
- [ ] The Enforcer payload is **~127g**: water 61g, printed parts 30g, Pi Zero
      11g, camera 5g, pump + tubing 20g (`make_stl.py --test` prints this)
- [ ] Tape that much dead weight to it. Does it still walk? Then try **30ml**
      of water (the budgeted figure) and 50ml
- [ ] **Decide reservoir size from that measurement**, not from hope
- [ ] Measure the bottle's internal diameter, set `BOTTLE_D`, re-run the test
- [ ] If it can't walk loaded → Squirt mode goes stationary (scope ladder),
      and that's a fine project
- [ ] Wire the pump via **MOSFET + flyback diode**; fire it dry, then wet
- [ ] ⚠️ **Range calibration.** Fire a 200ms pulse at 30/40/50/60cm onto paper
      laid on the desk; mark each landing point. Theory says a 20–56cm band.
      Set `PUMP_HEAD_M` from what you measure, then hard-code
      `RANGE_MIN`/`RANGE_MAX`. Fixed +20° means distance *is* the vertical
      aim, and the target is the **hands on the desk**, never the torso
      (BEHAVIOURS.md)
- [ ] ⚠️ **Brownout test:** pump + all servos moving at once. Sesame's firmware
      already staggers servos by 20ms because of this. If it browns out, give
      the pump its own cell

**Demoable:** it squirts on command.

## Week 6 — Perception

- [ ] Pi Zero 2 W on the payload deck; camera on its mount, forward-facing
- [ ] Camera streaming into OpenCV on the Pi Zero
- [ ] Person + `cell_phone` detection (YOLOv8n, 320×320, NCNN or ONNX)
- [ ] Head-down from bounding-box geometry — **not** MediaPipe Pose, which is
      likely too heavy for 512MB alongside the detector
- [ ] Measure your real frame rate. 1–2 FPS is expected and is enough
- [ ] Wrap it all into one `scene` object the state machine reads
- [ ] **Tune against false positives.** It must NOT fire while you work

**Demoable:** on screen, correct labels for "working" / "on phone" / "gone."

## Week 7 — Wire the brain to the body

- [ ] Python client for Sesame's JSON API: `stand`, `walk`, `turn`, `face`
- [ ] Mood → face expression mapping (Sesame ships faces; add your own)
- [ ] Mood → body language: perk-up, creep-in, victory bounce, cooldown
      settle — authored in **Sesame Studio**, played through *your* motion
      engine so they come out smooth rather than staccato
- [ ] Randomise timing so it never loops identically
- [ ] Speaker + a handful of pre-recorded taunt clips (MAX98357A + 8Ω).
      **No mic and no LLM needed for this** — it gets most of the "it talks"
      effect for free. See [`LLM_VOICE.md`](LLM_VOICE.md)

**Demoable:** it *reacts* with attitude to what it sees — no squirt needed.

## Week 8 — Squirt mode, end to end

- [ ] Calibrate **degrees per pixel** — put a marker at a known angle, see
      which pixel it lands on. Every aiming decision scales by this constant
- [ ] Aiming: turn until horizontal error is inside a ~5° deadband for **two
      consecutive frames**. Vertical is fixed at +20° — nothing to tune
- [ ] Full loop: detect slacking → escalate through moods → aim → fire
- [ ] **The five firing interlocks, in firmware** (BEHAVIOURS.md): person
      detected · state is STRIKE · range inside the calibrated band · command
      <1s old · hardware disable switch closed
- [ ] Add the **hardware disable** — a physical switch in series with the pump

**Demoable: the flagship works.** This alone is a complete project.

## Week 9 — Autonomous walking

- [ ] **The arbitration stack first** (BEHAVIOURS.md): cliff reflex > flee >
      Pi intent > idle breathing. Cliff must pre-empt *everything*
- [ ] **Cliff sensors** on the ESP32, polled fast — a 1–2 FPS brain cannot
      catch a fall. Calibrate on your actual desk; a dark matte surface is the
      classic false trigger
- [ ] Walk toward a target under closed-loop control from the onboard camera
- [ ] Tune until it crosses a desk without stumbling
- [ ] Note: 2 DOF per leg — it turns by differential gait, no strafing

**Demoable:** it walks to you, *then* squirts you.

## Week 10 — Warden mode (guard-and-block)

The robot **does not carry the phone** — settled by the torque numbers, not
by experiment. A phone is ~180g against Sesame's ~380g, which busts the
budget at any walkable stance. The phone stays on the desk and the robot
defends it. See BEHAVIOURS.md.

- [ ] **VL53L0X proximity trip on the ESP32** — anything inside ~15cm is a
      reaching hand. This is a reflex; vision is far too slow to dodge
- [ ] Back away from the hand **while staying between it and the phone**
- [ ] Escalate face → taunt → squirt if the hand persists
- [ ] ⚠️ **Cliff outranks flee.** Backing away from a hand is exactly how a
      robot reverses off a table. If they disagree, it stops and stands its
      ground. Losing the phone is recoverable; a fall is not
- [ ] Session timer state machine (locked until time's up)
- [ ] Optional, for video only: the fleeing shot with an **empty tray or a
      light dummy** — and say so in the writeup

**Demoable:** put your phone down, try to take it back, get squirted.

---

## Week 11 — Harden it

- [ ] One-hour continuous run; log and fix every crash
- [ ] Servo temperature after sustained walking
- [ ] Watchdog: a hung subsystem recovers instead of freezing mid-demo
- [ ] **Link failure behaviour** — if the Pi Zero → ESP32 link drops, the robot
      **stops and stands**, never last-command-forever
- [ ] Walk the whole failure table in BEHAVIOURS.md: empty reservoir, person
      lost mid-escalation, robot picked up mid-strike, dark-desk false cliff
- [ ] Water-safety recheck; cable strain relief
- [ ] Battery runtime measured and written down

## Optional — voice and an LLM (only after the core works)

Slot this in wherever there's slack, and **cut it first** if there isn't. It
adds 2–3 weeks. Full design in [`LLM_VOICE.md`](LLM_VOICE.md).

- [ ] INMP441 mic on the I2S bus alongside the MAX98357A
- [ ] Wake word on the Pi (openWakeWord, ~40MB — this part *does* fit)
- [ ] Whisper + Ollama + Piper on your laptop; robot streams audio over WiFi
- [ ] ⚠️ **The LLM writes taunts only. It must never reach the pump.** Scene
      facts go to it; only audio comes back. The five firing interlocks stay
      in firmware
- [ ] Feed it the *scene* ("phone visible 4m12s, 23:40, 3rd offence") so the
      taunts are specific — that's the version worth writing up

**Demoable:** it insults you, personally, about what it just saw.

## Week 12 — The experiment

- [ ] Run it: 8–15 volunteers, timer-vs-Enforcer, counterbalanced, written
      consent (see README "The experiment")
- [ ] Log phone pickups, on-task minutes, questionnaire
- [ ] Analyse; write up honestly, including the acceptability trade-off

## Week 13 — Rehearsal

- [ ] Demo to 5 people who aren't you; fix what confuses them
- [ ] Rehearse failures: someone works normally (no false squirt), WiFi off,
      a stranger tries to fool it
- [ ] Charge spare battery; flash + test spare SD card
- [ ] Photos + video of it working, taken **before** demo day

## Week 14 — Buffer + submit

- [ ] Whatever broke in week 13
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
- **If the Pi↔ESP32 link is still WiFi, bring your own** (phone hotspot or a
  travel router) and never trust venue WiFi. Moving that link to UART before
  demo day removes the whole risk.
- Bring a **towel** and a target cup. Obvious, and everyone forgets.
