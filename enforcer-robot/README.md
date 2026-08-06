# The Enforcer — an AI spider robot that holds you accountable

A four-legged desk robot with a face, a camera watching you, and
consequences. Built on [Sesame](https://github.com/dorianborian/sesame-robot)'s
proven skeleton, with your shell, your motion, and your brain on top. Slack off — pick up your phone, wander away — and it doesn't
beep politely. It notices, gives you attitude, stalks toward you, and
**squirts you with water**. Get back on task and it backs off, smug.

One robot, two "personalities" (modes):

| Mode | Detects | What it does |
|---|---|---|
| **Squirt** (flagship) | phone in your hand / head down / you left the desk | escalates, then squirts you |
| **Warden** | you reaching for your phone during a focus session | stands over it, backs off the hand, and squirts you |

Both share one body, one camera, one brain. They differ only in *what counts
as bad behavior* and *what the robot does about it*. Design a **Mode** as a
small object with `should_trigger(scene)` and `respond()`, and adding a third
later is ~30 lines, not a rewrite.

---

## Sesame is the foundation, not the destination

**Fork the skin. Keep the skeleton.**

[Sesame](https://github.com/dorianborian/sesame-robot) is an open-source mini
quadruped — 8× MG90S (2 per leg), an ESP32-S2, an OLED face — that walks and
emotes for **$50–60**. Apache 2.0, all CAD/STL/firmware/BOM published, Fusion
360 sources included. Its author spent **four months** on it, and says
outright that it's *"a foundation for making your own awesome version"* — the
repo and video show mods with wheels, cat ears, different faces and different
shells.

So this is **not** "build Sesame and bolt a tank on it." It's Sesame's proven
skeleton carrying your robot.

| Keep from Sesame (it's proven, and hard) | Make it yours (it's easy, and it's the identity) |
|---|---|
| Internal frame, motor mounts, leg pivot geometry | **Outer shell** — the spider look |
| Working 2-DOF-per-leg kinematics | **Stance and proportions** (within the torque budget below) |
| Servo driving, the 8-channel harness | **Face** — spider eyes, not dog eyes |
| Base firmware, the JSON API | **Motion engine** — see below. This is the big one |

What you must **not** casually change is the leg pivot geometry and the frame:
that's the part that took four months to get walking, and every hour you spend
re-deriving it is an hour not spent on the thing that's actually yours.

### What's Sesame's, and what's yours

Have this answer from day one — a jury respects a clean line far more than a
blurry one, and the Week 12 checklist asks for exactly this.

| | Sesame (Apache 2.0, credit it) | **Yours** |
|---|---|---|
| Internal frame, leg kinematics, harness | ✅ | |
| Base firmware, servo driving, JSON API | ✅ | |
| Stock gaits and poses | ✅ | |
| **Shell, stance, spider identity** | | ✅ |
| **Motion engine** — easing, breathing, anticipation | | ✅ |
| **Person + phone detection** | | ✅ |
| **Mood state machine** (the personality) | | ✅ |
| **The water rig** | | ✅ |
| **Autonomy** — Sesame is remote-controlled; yours decides for itself | | ✅ |
| **The focus experiment** | | ✅ |

**Sesame is a puppet — a human presses buttons on a web page. The Enforcer is
an agent.** Turning a teleoperated toy into something that watches, judges,
moves like a creature, and acts on its own is the real contribution.

---

## Making it move like a creature, not a machine

This is the difference between "cool 3D print" and "that thing is alive," and
it is almost entirely **software you write**. It also deserves to be a headline
result in the writeup, not a footnote.

### Why a servo robot looks stiff

Four causes, all fixable:

1. **A servo told "go to 90°" slews at full speed and stops dead.** No
   acceleration, no deceleration. That single fact is most of the stiffness.
2. **Keyframe animation is staccato** — a list of angles played back is a
   series of lurches, not a movement.
3. **Sesame's firmware staggers servo writes by 20ms** to avoid brownout, so
   joints *start at different times* and the motion reads as mechanical.
4. **Perfect stillness between moves reads as dead.** Nothing alive is ever
   completely still.

### The fix: an interpolation layer, on the ESP32

Between "what pose do I want" and "write the servo," insert a motion engine:

- **Easing.** Don't command the target — command a stream of intermediate
  setpoints along a cubic or sine ease-in-out curve at 30–50 Hz. The servo
  then *tracks a ramp* instead of slamming. This alone transforms it.
- **Move all joints over one time window**, with small per-joint phase
  offsets. Coordinated, not sequential.
- **Idle breathing.** A slow ±2–3° body-height oscillation at ~0.2 Hz, plus
  tiny random drift. **The single biggest "alive" cue, and nearly free.**
- **Anticipation and follow-through.** Before a lunge, pull back slightly;
  after a strike, overshoot ~5–10% and settle. Straight out of classic
  animation, and it reads as *intent*.
- **Jitter timings ±15%** so it never loops identically. Fixed cadence reads
  as a machine.

**This runs on the ESP32, not the Pi Zero.** Smooth motion needs steady 30–50
Hz timing, and a 1–2 FPS brain across a network hop cannot provide it. So the
split is: **the Pi decides, the ESP32 performs.** The Pi sends "creep forward,
suspicious"; the ESP32 renders that into motion.

That does mean modifying Sesame's firmware — which is fine, and is exactly the
kind of contribution worth writing up. Get it walking stock *first*, so you
know any new fault is yours.

### The obstacle you will hit, and how to attack it

Interpolating at 30 Hz across 8 servos is 240 servo updates per second. At
Sesame's 20ms stagger that's 4.8 seconds of staggering per second of motion —
impossible. So the stagger has to go, and you need to understand *why* it's
there before removing it.

It exists to limit **inrush current**: eight servos starting from rest and
slewing a long way, all at once, is a current spike that browns out the board.
But **interpolated steps are tiny** — a degree or two — so the per-step current
is far lower. That's a testable hypothesis, and testing it is real engineering:

1. Ramp all 8 servos in ~1° steps at 50 Hz with **no** stagger. Does it reset?
2. If yes, add **bulk capacitance** (1000 µF+ across the servo rail). This is
   the standard fix for inrush and is far cheaper than a bigger battery.
3. Still resetting? Drop to 20–25 Hz, and/or cap how many joints move at once.

Characterising that limit and replacing a fixed 20ms stagger with a real
motion system is a genuinely good result — measure it, plot it, put it in the
writeup.

---

## Architecture — everything rides on the robot

> Behaviour-level detail — the arbitration stack, the firing interlocks, the
> range calibration — lives in [`BEHAVIOURS.md`](BEHAVIOURS.md).

The robot has to carry its own eyes. A camera on a tripod driving a puppet is
not an embodied agent, it breaks the moment the robot walks out of frame, and
it throws away the best idea in the design: **camera and nozzle point the same
way, so centring the target *is* aiming.**

The real constraint isn't "onboard vs off-board", it's **which brain fits**. A
Pi 5 is 85 × 56mm and ~6W — physically larger than Sesame and far past its
power budget. A **Pi Zero 2 W** is 65 × 30mm, **11g**, and ~2W. That fits.

```
        ┌──────────────────── the robot ────────────────────┐
        │                                                   │
        │  ┌─ Pi Zero 2 W (on the payload deck) ─────────┐   │
        │  │  camera ─► YOLOv8n: person + cell_phone     │   │
        │  │              │                              │   │
        │  │              ▼                              │   │
        │  │   MOOD STATE MACHINE                        │   │
        │  │   CHILL→SUSPICIOUS→WARNING→STRIKE→SMUG      │   │
        │  │       │                        │            │   │
        │  └───────┼────────────────────────┼────────────┘   │
        │          │ UART / WiFi            │ GPIO           │
        │          ▼                        ▼                │
        │  ┌─ ESP32-S2 (stock Sesame) ─┐   MOSFET ─► pump ─► │💦
        │  │  8 × MG90S · OLED face    │                     │
        │  │  gaits, poses, animations │   camera + nozzle   │
        │  └───────────────────────────┘   share one tilt    │
        └───────────────────────────────────────────────────┘
```

**Two brains, one job each.** The ESP32 keeps running stock Sesame firmware —
servos, face, gaits — so you never fork it. The Pi Zero does the thinking and
fires the pump. Start the link over **WiFi** (Sesame's JSON API already exists,
zero firmware change); move to **UART** if it's flaky. They're 5cm apart, so
UART is the better end state.

### Aiming is yaw-only, and that simplifies everything

Sesame can turn but it can't tilt. So there is exactly **one** closed loop:
turn until the target is horizontally centred in frame, then fire. The
**vertical** angle is a mechanical decision made once — both camera and nozzle
are fixed at **+20° above horizontal** on their printed mounts, aimed at a
seated person's torso from desk height.

That's why `cad/make_stl.py` derives both mounts from a single `NOZZLE_TILT`
and has a test asserting they match. If those two angles drift apart, the
robot aims high or low by exactly the difference, and no amount of software
will find it.

### What this costs you, honestly

- **~1–2 FPS.** YOLOv8n on a Pi Zero 2 W is slow. It's *enough*: every trigger
  in this project is a multi-second threshold ("phone visible > 3s"), so 4–5
  frames of evidence is plenty. It also matches the actuation rate — Sesame
  turns in discrete steps of roughly a second, so a faster camera would just
  wait on the legs.
- **512MB RAM.** Tight. Headless Pi OS Lite, YOLOv8n via NCNN or ONNX at
  320×320. **Plan on the detector only** — MediaPipe Pose on top is likely too
  much, so derive "head down" from bounding-box geometry rather than full pose.
  If 512MB genuinely bites, a Radxa Zero 3W or Orange Pi Zero 2W is the same
  size with up to 4GB.
- **Runtime.** The Pi Zero adds ~2W to an 800mAh pack. Measure it, and expect
  to want a larger battery than stock Sesame ships with.

If the onboard route fails outright, the fallback is a Pi 5 on the desk
driving the robot over the same API — the seam doesn't move. But try onboard
first: it's the version that's actually a robot.

## Why this isn't "ChatGPT on legs"

The intelligence shows up as **behavior, not conversation.** The robot never
needs to hold a chat to be impressive — it hunts, taunts, and strikes:

- The **AI** has to actually understand the scene (are you working or on your
  phone? are you even there?) — real computer vision, not a scripted toy.
- The **legs** are justified because it comes to find you, and because it has
  to hold ground and back off a reaching hand on a cluttered desk — a wheeled
  robot falls off the edge.

## The serious backbone (this is what makes it a *project*, not a gag)

1. **Commitment device** (behavioral economics): people voluntarily let
   something impose a consequence on them so they actually follow through —
   like apps that donate your money to a cause you hate if you skip the gym.
   Your robot is the physical, embodied, un-ignorable version. This also
   handles consent: the user *opts in* to being enforced.
2. **The embodiment effect**: people engage with, and can't ignore, a
   physical creature stalking toward them in a way they *can* ignore a phone
   notification. Well documented in human-robot interaction research.

Together they give the research question that turns a water gag into an
entry:

> **Does an embodied enforcer with real consequences improve focus more than
> a passive phone timer — and will people actually tolerate it?**

A negative or mixed result still publishes — the mark of a well-chosen
question.

## The personality

Personality = **moods expressed through motion, a face, and sound**, driven by
the state machine. No dialogue required.

- **Face** — Sesame's SSD1306 OLED already renders faces, and the firmware
  ships with a set. You add the *mapping* from mood to face, and any new
  expressions you want (images → byte arrays → firmware).
- **Body language** — Sesame's animation system already does poses and
  movement, and **Sesame Studio** (its Python animation composer) is how you
  author new ones. Build: perk-up, creep-in, victory bounce, cooldown settle.
- **Sound** — short pre-recorded taunt clips. More reliable on stage than TTS.
- **Randomized timing** so it never loops identically. A fixed cadence reads
  as a machine; jitter reads as a creature.

## The experiment

Within-subjects, counterbalanced, ~8–15 volunteers:

1. Two ~20-minute study sessions each: one with a **plain phone timer**, one
   with **the Enforcer** (randomize the order).
2. Measure: phone pickups, minutes on-task, and a short questionnaire
   (motivation 1–5, annoyance 1–5, "would you use this?").
3. Compare. Report honestly, including the acceptability trade-off — does it
   help *because* people hate it, or do they actually like it?

Consent in writing, and anyone can stop any time.

## Safety & ethics (non-negotiable)

- **Water + electronics.** Keep the reservoir and nozzle at the front firing
  *outward and slightly down*, battery only (never mains), and keep water
  lines physically away from the ESP32 and the servo wiring.
- **Aim.** Torso/desk only — **never** the face or eyes. Short pulses, low
  pressure. It's a squirt, not a jet.
- **Consent.** It's a commitment device: the user opts in. For public demos,
  only squirt a volunteer who agreed, or a target cup.
- **Don't let it fall.** Cliff sensors before any autonomous walking — a robot
  going off the desk edge is the obvious failure.
- **Battery safety.** Charge in a safe bag, never unattended.

## Honest hard parts

1. **Torque is the hard limit on the spider look.** `cad/make_stl.py --test`
   computes it: at ~507g loaded, **a foot can sit only ~48mm out from its
   hip** before MG90S runs out of derated torque. 50mm is already over.
   Torque scales linearly with how far out the foot sits, so **long legs and
   a wide splayed stance are both expensive** — and payload eats the same
   budget, at roughly **1.2mm of reach per 10g**.
   **So get the spider from shape, not size:** angular shell, low body,
   knees-up silhouette, spider eyes. Not longer legs. Re-run that test with
   your *measured* mass before you restyle anything.
2. **Payload.** Water is heavy — 100ml is 100g, and it costs you ~12mm of
   reach. **Weigh your build and walk it loaded early.** If it can't, drop to
   a 30–50ml reservoir or run Squirt stationary. Week 5, not week 12.
3. **"On-task vs slacking" detection** that doesn't false-fire — a robot that
   squirts you while you're working is a *bad* robot. Hysteresis and time
   thresholds.
4. **Brownout.** Sesame's firmware already staggers servo moves by 20ms
   because driving all of them at once browns out the board. **Adding a pump
   to the same battery is exactly the kind of load that breaks this.** Give
   the pump its own supply or a large capacitor, and re-test.
5. **2 DOF per leg, not 3.** Sesame's legs move in a plane. It turns by
   differential gait, not by swivelling a hip. Fine for stalking and fleeing,
   but don't plan motions that need a third joint.

## Scope ladder (so a bad week never leaves you with nothing)

| If… | Ship this instead |
|---|---|
| Sesame isn't walking reliably | **Stationary Squirt sniper** — it poses, breathes and emotes, doesn't walk. Still complete |
| The pump browns out the ESP32 | Separate pump battery, or a solenoid + gravity feed |
| 100ml is too heavy to walk with | 50ml reservoir — 496g still fits the torque budget |
| The shell restyle is eating weeks | Ship Sesame's stock shell + your face and motion. Identity mostly lives in *how it moves* anyway |
| Behind at week 11 | Cut Warden. Polish Squirt, keep the motion engine, run the experiment |

**Cut Warden before you cut the motion engine.** A robot that moves like a
creature and does one thing beats a stiff robot that does two — on a demo
table and in a writeup.

The floor is "a robot that breathes, catches you on your phone, and squirts
you, with a focus experiment." That alone wins a room.

## What carries over from your wristband

- **Sensor → decision → actuator** is your whole wristband; same loop, bigger.
- **The pump driver is your motor driver, scaled up** — transistor + flyback
  diode becomes a logic-level **MOSFET** + flyback for more current.
- **Simulate + unit-test before hardware** — build the mood state machine in a
  sim with tests first, exactly like `HapticMapper` and
  `haptic_simulator.html`. Your strongest habit; use it.
- **Ethics/consent discipline** — you already do this well. Keep it.

## Files in this project

- `README.md` — this overview
- `START_HERE.md` — **what to do right now**, with no parts and nothing built
- `PARTS.md` — what to buy and why, Sesame BOM + the Enforcer additions
- `PURCHASE_LIST.md` — the German cart with verified prices and stock
- `BUILD_CHECKLIST.md` — week-by-week plan
- `BEHAVIOURS.md` — **how it moves, shoots and defends the phone**, end to end
- `cad/` — the Enforcer's *additional* printed parts, and the torque budget
  that constrains how far you can restyle the legs

## Open decisions

1. ~~Hexapod or quadruped?~~ **Quadruped** — Sesame, 8 servos, 2 per leg.
2. ~~Three modes?~~ **Two** — Squirt and Warden.
3. ~~Design the body?~~ **No — build Sesame.**
4. ~~Pi 5 4GB or 2GB?~~ **Neither — Pi Zero 2 W**, onboard. It's the largest
   brain that fits Sesame's weight and power budget.
5. **Reservoir size** — decide after you weigh the build. The payload is
   ~127g at a 36mm bottle; `cad/make_stl.py --test` prints the breakdown.
6. **Pi ↔ ESP32 link: WiFi or UART?** Start WiFi (no firmware change), move to
   UART once it works. They end up 5cm apart.
