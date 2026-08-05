# The Enforcer — an AI layer that holds you accountable, on a Sesame body

A four-legged desk robot with a face, a camera watching you, and
consequences. Slack off — pick up your phone, wander away — and it doesn't
beep politely. It notices, gives you attitude, stalks toward you, and
**squirts you with water**. Get back on task and it backs off, smug.

One robot, two "personalities" (modes):

| Mode | Detects | What it does |
|---|---|---|
| **Squirt** (flagship) | phone in your hand / head down / you left the desk | escalates, then squirts you |
| **Warden** | you reaching for your phone during a focus session | walks off with your phone so you can't cheat |

Both share one body, one camera, one brain. They differ only in *what counts
as bad behavior* and *what the robot does about it*. Design a **Mode** as a
small object with `should_trigger(scene)` and `respond()`, and adding a third
later is ~30 lines, not a rewrite.

---

## The most important decision in this project: don't build the body

**Build [Sesame](https://github.com/dorianborian/sesame-robot) and put your
effort on top of it.**

Sesame is an open-source mini quadruped — 8× MG90S servos (2 per leg), an
ESP32-S2, an OLED face — that walks, poses, and emotes for **$50–60**. It's
**Apache 2.0 licensed**, with all CAD, STLs, firmware, wiring guide and BOM
published. Its creator spent **four months** designing it.

You do not have four months, and body design is not where your project's
originality lives. Sesame gives you a walking, expressive creature in ~2
weeks of printing and assembly. Everything that makes this *The Enforcer* —
the perception, the mood state machine, the water rig, the experiment — is
still entirely yours to build.

This is the same reasoning `PARTS.md` already applies to the chassis: *"Buying
the frame is not defeat; it moves your effort to the AI and the water rig,
which is where the originality is."* Sesame is that argument taken to its
conclusion — and it's better than a kit chassis, because it comes with tested
gaits and an animation tool.

### What's Sesame's, and what's yours

The Week 12 checklist asks you to write down exactly this. Have the answer
from day one — a jury respects a clean line far more than a blurry one.

| | Sesame (Apache 2.0, credit it) | **Yours** |
|---|---|---|
| Body, legs, 3D printed parts | ✅ | |
| Walking gaits, poses, animations | ✅ | |
| OLED face rendering | ✅ | |
| WiFi control page + JSON API | ✅ | |
| **Person + phone detection** | | ✅ |
| **Mood state machine** (the personality) | | ✅ |
| **The water rig** | | ✅ |
| **Autonomy** — Sesame is remote-controlled; yours decides for itself | | ✅ |
| **The focus experiment** | | ✅ |

That last row is the real intellectual claim. **Sesame is a puppet — a human
presses buttons on a web page. The Enforcer is an agent.** Turning a
teleoperated toy into something that watches, judges, and acts on its own is
a genuine contribution, and it's a much cleaner story than "I designed some
brackets."

---

## Architecture — everything rides on the robot

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
- The **legs** are justified because it comes to find you and (in Warden
  mode) *runs away* — a wheeled robot falls off the desk.

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

1. **Payload.** Sesame is small and runs 8 MG90S servos off an 800mAh pack.
   Water is heavy — 100ml is 100g. **Weigh your build and test with a full
   reservoir early.** If it can't walk loaded, drop to a 50ml reservoir or
   run Squirt mode stationary (see the scope ladder). Decide this in week 3,
   not week 10.
2. **"On-task vs slacking" detection** that doesn't false-fire — a robot that
   squirts you while you're working is a *bad* robot. Hysteresis and time
   thresholds.
3. **Brownout.** Sesame's firmware already staggers servo moves by 20ms
   because driving all of them at once browns out the board. **Adding a pump
   to the same battery is exactly the kind of load that breaks this.** Give
   the pump its own supply or a large capacitor, and re-test.
4. **2 DOF per leg, not 3.** Sesame's legs move in a plane. It turns by
   differential gait, not by swivelling a hip. Fine for stalking and fleeing,
   but don't plan motions that need a third joint.

## Scope ladder (so a bad week never leaves you with nothing)

| If… | Ship this instead |
|---|---|
| Sesame isn't walking reliably | **Stationary Squirt sniper** — Sesame poses and emotes, doesn't walk. Still complete |
| The pump browns out the ESP32 | Separate pump battery, or a solenoid + gravity feed |
| Payload fails | Guard-and-block Warden (no carrying), or a smaller reservoir |
| Behind at week 10 | Cut Warden; polish Squirt + run the experiment |

The floor is "a robot that catches you on your phone and squirts you, with a
focus experiment." That alone wins a room.

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
- `cad/` — the Enforcer's *additional* printed parts (Sesame provides the body)

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
