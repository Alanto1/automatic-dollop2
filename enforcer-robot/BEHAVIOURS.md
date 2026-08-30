# Behaviours — how it moves, shoots, and defends the phone

The three things the robot actually *does*, end to end: what senses it, what
decides, what moves, and what stops it hurting anyone or falling off a desk.

Concept and architecture: [`README.md`](README.md). Build order:
[`BUILD_CHECKLIST.md`](BUILD_CHECKLIST.md).

---

## The one rule that organises everything

**The Pi decides at 1–2 Hz. The ESP32 performs at 30–50 Hz. Anything that has
to be fast is a reflex on the ESP32.**

A Pi Zero 2 W running YOLOv8n gives you roughly one or two frames a second.
That is plenty for "has this person been on their phone for three seconds" and
hopeless for "stop before that foot goes over the edge." So the split is not
negotiable: **decisions upstairs, reflexes downstairs.**

### The arbitration stack

Highest priority wins. Everything below is pre-empted.

```
1. CLIFF REFLEX        (ESP32)  never step off the desk — overrides all
2. FLEE / BLOCK        (ESP32)  proximity trip → back away from the hand
3. WALK / TURN / FIRE  (Pi)     the mood state machine's intent
4. IDLE BREATHING      (ESP32)  when nothing else runs, stay alive
```

Two consequences worth stating out loud:

- The robot is **never completely still**, because level 4 always runs.
- **No decision from the Pi can talk it off a table.** Level 1 outranks
  level 3 by construction, not by convention. That's the failure you cannot
  recover from on demo day.

---

## 1. Moving — stalking toward you

### Sense (Pi, ~1–2 Hz)

Camera → YOLOv8n at 320×320 → boxes for `person` and `cell_phone`.

Horizontal error is how far the person's box centre sits from image centre.
At roughly 60° horizontal field of view across 320 px, that's about
**0.19° per pixel**.

> **Calibrate this once.** Put a marker at a known angle, see which pixel it
> lands on, and hard-code the real number. Camera modules vary by more than
> you'd guess, and every aiming decision downstream scales by this constant.

### Decide (Pi)

The mood state machine turns evidence into *intent*. It never sends joint
angles — only `turn(deg)`, `walk(steps)`, `pose(name)`, `face(mood)`,
`fire(ms)`.

### Perform (ESP32, 30–50 Hz)

A gait is a parameterised sequence of leg targets; the motion engine
interpolates between them with easing (see README, "Making it move like a
creature"). With **2 DOF per leg**, each leg swings in its own vertical plane:

- **Walk** — crawl gait. Shift the body's weight over three feet, lift and
  swing the fourth, repeat. *The weight shift is the gait*, not a detail.
- **Turn** — differential stride. Left legs take longer steps than right and
  it arcs. Turn in place: left legs stride forward, right legs stride back.
- **No strafing.** Two DOF per leg means no sideways translation. Every
  reposition is some combination of turn and walk.

### Reflex (ESP32, fast)

Four TCRT5000s, one per corner, polled continuously. A corner that stops
seeing floor **aborts the current step and backs off** — the Pi finds out
afterwards. This is level 1 of the stack.

---

## 2. Shooting — the squirt

### The gate

STRIKE is only reachable after **sustained** evidence: phone visible
continuously for >3 s, with hysteresis so a glance can't trigger it. Tuning
this is the entire difference between "impressive" and "a robot that soaks
you while you're working."

### Aiming is yaw-only

The Pi computes horizontal error in degrees and commands `turn(error)` when
it exceeds a **~5° deadband**. Aligned = two consecutive frames inside the
deadband, so one noisy detection can't trigger a shot.

**Vertical is not controlled.** It's fixed at +20° by the printed mounts
(`NOZZLE_TILT` in `cad/make_stl.py`, which drives both the nozzle and camera
mounts and has a test asserting they match).

That has a consequence people miss: a fixed elevation means the water lands
in a **fixed band of distances**. So "aimed" really means *aligned in yaw*
**and** *inside the calibrated range band*.

### The target is the hands and the phone — not the torso

This is settled by ballistics, not preference. From a 12cm nozzle at +20°,
the jet has only risen ~18cm by half a metre, so **a seated person's torso
(~35cm above the desk) is unreachable at any pump pressure**:

```
torso (35cm up) unreachable at +20deg -- correct, we aim at the hands
```

`make_stl.py --test` asserts that, so if anyone raises the tilt the build
fails rather than this document going quietly wrong.

Aiming at the hands is the better target anyway: it's what the offence
actually is, and it is a long way below anyone's face.

### Range calibration (do this once, write it down)

The theory says, for a 3V submersible pump at ~40cm of head:

```
RANGE_MIN 20cm  RANGE_MAX 56cm
head needed vs reach (target = hands at 10cm):
   ok    30cm ->   20cm of head
   ok    40cm ->   27cm of head
   ok    50cm ->   35cm of head
   OVER  60cm ->   43cm of head
   OVER  80cm ->   58cm of head
```

Now measure it, because `PUMP_HEAD_M` is an estimate:

1. Fill the reservoir. Set the robot **30 cm** from a sheet of paper laid on
   the desk. Fire a 200 ms pulse. Mark where it lands.
2. Repeat at **40, 50, 60 cm**.
3. The **usable band** is where it lands on the desk in front of a person —
   on their hands and phone, never above desk level.
4. Set `PUMP_HEAD_M` from what you measured, re-run the test for your real
   band, and hard-code `RANGE_MIN` / `RANGE_MAX`. Outside the band the robot
   **walks closer instead of firing.**

⚠️ **Measure at the pump's rated 3V.** A DC motor's speed follows voltage and
a pump's head follows speed *squared*, so a test at 1.5V reads about a
quarter of the truth — roughly 10cm of head where the real figure is 40. A
whole design decision about how close the robot has to walk can rest on that
factor of four, so get the voltage right before concluding anything.

`RANGE_MIN_M` (20cm) is a **standoff preference, not a ballistic limit** —
the robot should not fire from touching distance. `range_band` drops below it
when the pump cannot reach that far, because a near limit above the far limit
is an empty band, and an empty band means firing interlock 3 never passes and
the pump never runs. A weak pump should make the robot walk closer. It must
not make it mute.

Measure range with the **VL53L0X** pointed forward. Bounding-box height works
as a fallback but needs its own calibration and is much noisier.

### Firing

Pi sends `fire(ms)` → ESP32 pulses a GPIO → MOSFET → pump for **150–300 ms**.
Short pulse, low pressure. It's a squirt, not a jet.

**Five interlocks. All must pass, checked in firmware, not in Python:**

1. a `person` is currently detected,
2. state is STRIKE,
3. measured range is inside `[RANGE_MIN, RANGE_MAX]`,
4. the fire command is **<1 s old** (stale-command guard — if the link drops
   mid-command, nothing fires),
5. the **hardware disable switch** is closed.

That last one is a physical switch in series with the pump. Software you
wrote at 1 a.m. is not what should stand between a demo and someone's face.

Then SMUG: victory bounce, smug face, and a cooldown timer before it can fire
again.

### Safety, non-negotiable

- Nozzle aims at **the desk and the hands only**. Never above desk level.
  `make_stl.py` rejects a tilt outside 5–35° for this reason.
- Consent first — it's a commitment device, the target opts in. In public,
  only a volunteer who agreed, or a target cup.
- Bring a towel. Everyone forgets the towel.

---

## 3. Warden — defending the phone

### Threat detection can't be vision

A hand moves fast. At 1–2 FPS the hand has your phone before the second frame
arrives. COCO has no `hand` class anyway, and MediaPipe Hands won't fit in
512 MB next to the detector.

**Use the VL53L0X as a proximity trip, on the ESP32.** Anything inside ~15 cm
that wasn't there a moment ago is a reaching hand. Reflex, level 2 — no round
trip to the Pi.

One forward-facing VL53L0X therefore does **two** jobs: the firing range band,
and the Warden trip. That's why it moved from optional to required.

### It cannot carry your phone

`cad/make_stl.py --test` computes this, and the numbers are decisive:

```
payload cases (budget 1.21 kg-cm at 48mm reach):
  ok   bare Sesame                  380g  reach<= 64mm  0.91 kg-cm
  ok   + deck, Pi Zero, camera      426g  reach<= 57mm  1.02 kg-cm
  ok   + water rig, 50ml            496g  reach<= 49mm  1.19 kg-cm
  OVER + water rig, 100ml           546g  reach<= 44mm  1.31 kg-cm
  OVER Warden CARRYING a phone      606g  reach<= 40mm  1.45 kg-cm
  OVER Warden carrying phone + 50ml 676g  reach<= 36mm  1.62 kg-cm
```

A phone is ~180 g against Sesame's ~380 g body — **roughly half the robot
again.** Carrying one busts the derated MG90S torque budget at any stance a
quadruped can actually walk in.

There's a self-test asserting the carrying case stays over budget, so if
someone changes the masses and it starts passing, the build fails loudly
instead of this document quietly going wrong.

### So Warden is guard-and-block

Not a fallback — **the design.**

The phone sits on a pad or the `phone_tray`, *on the desk*. The robot stands
over it. A session timer runs. When the proximity trip fires:

1. **Back away from the hand** while staying between it and the phone.
2. **Escalate the face** — alarmed, then furious.
3. **Taunt** through the speaker.
4. If the hand persists and the shot is safe: **squirt it.**

Same demo beat — *you try to grab your phone, the robot defends it* — without
asking MG90S for torque it doesn't have. If you want the fleeing-with-the-
phone shot for video, do it with an **empty tray or a light dummy** and say so
in the writeup.

### The desk edge outranks the phone

Backing away from a hand is exactly how a robot reverses off a table. **Level
1 beats level 2.** If the cliff sensors and the flee reflex disagree, the
cliff sensors win, the robot stops, and it stands its ground instead. Losing
the phone is recoverable; a robot on the floor with a phone under it is not.

---

## What can go wrong, and what it should do

| Failure | Behaviour |
|---|---|
| Pi ↔ ESP32 link drops | Robot **stops and stands**. Never last-command-forever. Stale-command guard covers firing |
| Detector loses the person mid-escalation | De-escalate on a timer — never latch in WARNING |
| Reservoir empty | Pump runs dry harmlessly; it still *poses* the strike. The threat is most of the effect |
| Cliff sensor sees dark desk as an edge | Calibrate on your actual desk surface. A dark matte desk is the classic false trigger |
| Someone picks the robot up mid-strike | Interlock 3 (range band) fails → no fire |
| WiFi congested at a demo | Move the link to UART before demo day; it removes the risk entirely |

---

## Build order for these behaviours

Each is demoable on its own, which is the project's whole rule.

1. **Week 3** — motion engine. It breathes and creeps with no AI attached.
2. **Week 5** — pump fires on command; range calibration table.
3. **Week 6** — perception labels working / on-phone / gone.
4. **Week 8** — Squirt end to end: detect → escalate → aim → fire.
5. **Week 9** — cliff reflex, then autonomous walking.
6. **Week 10** — Warden guard-and-block.
