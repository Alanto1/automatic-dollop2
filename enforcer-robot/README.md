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

## Architecture

The one hard constraint: **an ESP32-S2 cannot run computer vision.** So the
brain is a Raspberry Pi, and it talks to Sesame over the WiFi JSON API that
Sesame already has.

```
   ┌─────────── on your desk ────────────┐        ┌──── the robot (Sesame) ────┐
   │  Raspberry Pi 5 + camera            │        │  ESP32-S2                  │
   │                                     │        │                            │
   │  perception:                        │        │   ┌── 8 × MG90S servos     │
   │   • person + phone (YOLOv8n)        │  WiFi  │   ├── SSD1306 OLED face    │
   │   • head pose / presence (MediaPipe)│ ─JSON─►│   └── GPIO ─► MOSFET ─► 💦 │
   │            │                        │        │                            │
   │            ▼                        │        │  runs stock Sesame         │
   │   MOOD STATE MACHINE                │        │  firmware + one added      │
   │   CHILL→SUSPICIOUS→WARNING→         │        │  endpoint for the pump     │
   │        STRIKE→SMUG                  │        └────────────────────────────┘
   │            │                        │
   │            └─► "turn left", "creep", │
   │                "face", "FIRE"        │
   └─────────────────────────────────────┘
```

**Why the Pi sits on the desk rather than on the robot.** Sesame is a small
robot on an 800mAh battery. A Pi 5 plus its power draw would wreck both its
weight budget and its runtime, and you'd be redesigning the body you just
decided not to design. Keeping the Pi off-board means **Sesame stays exactly
as documented** — no modifications, no fork, no re-print.

It also fixes the aiming problem more cleanly than the original plan did. A
desk camera sees **both you and the robot**, third-person. So "aim" becomes
"turn the robot until it's pointing at the target," commanded from outside —
no pan/tilt head, no onboard camera, no visual servoing loop on a
microcontroller. One camera also gives you the footage the *experiment* needs
for counting phone pickups.

**The honest cost of this choice:** the robot is not self-contained, and a
jury may ask about that. The answer is that a commitment device for desk work
lives on the desk by definition — and that the Pi can move onboard later
without changing a line of the state machine, because the seam is the JSON
API. Say it before they ask.

---

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
4. **Pi 5 4GB (€118.50) or 2GB (€69.50)?** Open, and it gates the order.
   See `PURCHASE_LIST.md`.
5. **Reservoir size** — decide after you weigh the build.
