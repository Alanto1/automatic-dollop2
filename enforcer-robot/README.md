# The Enforcer — an AI spider robot that holds you accountable

A four-legged desk robot with a camera, a face, and consequences. It watches
you work. Slack off — pick up your phone, wander away — and it doesn't beep
politely. It notices, gives you attitude, stalks toward you, and **squirts
you with water**. Get back on task and it backs off, smug.

One robot, two "personalities" (modes):

| Mode | Detects | What it does |
|---|---|---|
| **Squirt** (flagship) | phone in your hand / head down / you left the desk | escalates, then squirts you |
| **Warden** | you reaching for your phone during a focus session | flees across the desk with your phone so you can't cheat |

Both share one body, one camera, one brain. They differ only in *what counts
as bad behavior* and *what the robot does about it*. So this is **one project
with two demo modes**, not two robots.

## What it looks like

The build target is the classic 3-DOF quadruped: a flat chassis plate, four
legs splayed out spider-style, and a **rectangular face display** on the front
of the body. Printed shells in a loud colour over black servo bodies — the
colour is not vanity, it reads as a *creature* on a demo table and photographs
well for the writeup.

See [`cad/SKETCH.svg`](cad/SKETCH.svg) for dimensioned front/side/top views and
the leg-joint diagram, and [`cad/stl/`](cad/stl/) for printable parts.

```
        front view                          side view (one leg)

     ┌──────────────┐                     coxa    femur      tibia
     │  ( ●  ▭  ● ) │  ← face display    ○──────○           knee
     └──────────────┘                     │       \         ○
   ╱─┴─╲          ╱─┴─╲                   │        \       ╱
  ╱     ╲        ╱     ╲                 body       \     ╱
 │       │      │       │                            \   ╱
  ╲     ╱        ╲     ╱                              ╲ ╱
   ▔▔▔▔            ▔▔▔▔                                ▼ foot
```

Three joints per leg × four legs = **12 servos**, all MG90S:

| Joint | Axis | Does |
|---|---|---|
| **Coxa** (hip yaw) | vertical | swings the leg forward/back — this is what walks |
| **Femur** (hip pitch) | horizontal | lifts the leg off the desk |
| **Tibia** (knee) | horizontal | extends/folds the foot, sets body height |

Plus **2 servos** on a pan/tilt head carrying the camera and the water nozzle.
14 servos total, all on one PCA9685 (16 channels).

**One deliberate change from the reference photo:** the face display stays on
the *body*, while the camera and nozzle ride the *pan/tilt head*. Putting the
face on the head would mean it looks away from you at the exact moment it aims
at you — the aiming motion would hide the personality. Splitting them lets it
glare at you while it lines up the shot, which is both funnier and better
engineering.

## Why this isn't "ChatGPT on legs"

The intelligence shows up as **behavior, not conversation.** The robot never
needs to hold a chat to be impressive — it hunts, taunts, dodges, and
strikes. That's the whole point, and it's what makes the AI + the legs both
*essential* instead of decorative:

- The **AI** has to actually understand the scene (are you working or on your
  phone? are you even there?) — real computer vision, not a scripted toy.
- The **legs** are justified because it comes to find you, lines up a shot,
  and (in Warden mode) *runs away* — a wheeled robot falls off the desk.

## The serious backbone (this is what makes it a *project*, not a gag)

Two real ideas hold this up when a jury pushes on it:

1. **Commitment device** (behavioral economics): people voluntarily let
   something impose a consequence on them so they actually follow through —
   like apps that donate your money to a cause you hate if you skip the gym.
   Your robot is the physical, embodied, un-ignorable version. This also
   handles consent: the user *opts in* to being enforced.
2. **The embodiment effect**: people engage with, and can't ignore, a
   physical creature stalking toward them in a way they *can* ignore a phone
   notification. This is well documented in human-robot interaction research.

Together they give you the research question that turns a water gag into a
competition entry:

> **Does an embodied enforcer with real consequences improve focus more than
> a passive phone timer — and will people actually tolerate it?**

You can measure both halves (see [The experiment](#the-experiment)). A
negative or mixed result still publishes — the mark of a well-chosen
question.

## How it works (system overview)

```
                         ┌──────────────── Raspberry Pi ─────────────────┐
   camera (on the head) ►│  perception:                                  │
                         │   • person + phone detection (YOLO/MobileNet) │
                         │   • head pose / presence (MediaPipe)          │
                         │            │                                  │
                         │            ▼                                  │
                         │   MOOD STATE MACHINE  (the personality)       │
                         │   CHILL → SUSPICIOUS → WARNING → STRIKE → SMUG│
                         │       │              │            │           │
                         │       ▼              ▼            ▼           │
                         │  face display    body language   fire!        │
                         └───────┬───────────────┬───────────┬──────────┘
                                 │ SPI           │ I2C        │ GPIO
                                 ▼               ▼            ▼
                          face display     PCA9685 ──┬──► 12 leg servos
                          (on the body)              └──► 2 head servos (pan/tilt)
                                                           │
                                   camera + water nozzle ride on the head,
                                   so "center the target in frame" == "aimed"
                                                           │
                                 GPIO ─► MOSFET ─► water pump ─► nozzle ─► 💦
                     cliff sensors (down-facing IR) ─► never walk off the desk
```

The clever bit in the aiming: **mount the camera and the water nozzle on the
same pan/tilt head.** Then aiming is just *visual servoing* — turn the head
until the target is centered in the camera image, and the nozzle is now
pointed at them. Fire.

## The two modes, in engineering terms

They're the same pipeline with a different **trigger** and **response**:

- **Squirt** — trigger: `cell_phone` detected near the person's hands, OR head
  pitched down for > N seconds, OR no person at the desk for > N seconds.
  Response: escalate through moods, then pulse the pump.
- **Warden** — the phone rides on a tray on the robot's back. Trigger: a hand
  approaching the robot/phone during a locked focus session. Response: walk
  away from the hand (reactive avoidance) while avoiding desk edges.

Design the software so a **Mode** is a small object with
`should_trigger(scene)` and `respond()` — then adding a mode later is ~30
lines, not a rewrite. (This is also the clean way to bring back a third mode
if you ever want one.)

## The personality — how "attitude" is actually built

Personality here = **moods expressed through motion, a face, and sound**,
driven by the state machine. No dialogue required.

- **Face display** (rectangular LCD on the body front): two eyes that narrow
  when suspicious, go wide when alarmed, and half-lid smugly after a hit. One
  cheap part does most of the "it's alive" work. A rectangle gives you *two*
  eyes side by side, which reads as a face far more directly than a single
  round eye — the reference build is right about this.
- **Body language** (the legs): perk up when suspicious, crouch low and creep
  in warning, a little victory bounce after a strike, a slow "cooldown"
  settle. This is why legs beat a static gadget for personality.
- **Sound**: short taunt clips through a small speaker ("phone. down. now.").
  Pre-recorded clips are more reliable on stage than live TTS.
- **Randomized timing** so it never loops identically — a fixed cadence reads
  as a machine; jitter reads as a creature.

## The experiment

Within-subjects, counterbalanced, ~8–15 volunteers:

1. Each person does two ~20-minute study sessions: one with a **plain phone
   timer**, one with **the Enforcer** (randomize the order).
2. Measure: number of phone pickups, minutes on-task, and a short
   post-session questionnaire (motivation 1–5, annoyance 1–5, "would you use
   this?").
3. Compare. Report honestly, including the acceptability trade-off (does it
   help *because* people hate it, or do they actually like it?).

Consent in writing, and anyone can stop any time — the same care your
wristband README already applies to test users.

## Safety & ethics (non-negotiable)

- **Water + electronics.** Waterproof the body, keep the reservoir and nozzle
  at the front firing *outward and slightly down*, run on **battery only**
  (never mains), and keep the pump/water lines physically away from the Pi and
  drivers.
- **Aim.** Torso/desk only — **never** the face or eyes. Short pulses, low
  pressure. It's a squirt, not a jet.
- **Consent.** It's a commitment device: the user opts in to being squirted.
  For public demos, only squirt a volunteer who agreed, or a target cup.
- **Don't let it fall.** Cliff sensors are mandatory before Warden mode — a
  robot (and someone's phone) going off the desk edge is the obvious failure.
- **LiPo safety.** Charge in a LiPo bag, fuse the battery, never leave
  charging unattended (same rule as your wristband battery note).

## Honest hard parts (where the time actually goes)

1. **Walking reliably** — not the AI. Budget real time for gait tuning. A
   quadruped is *harder* to walk than a hexapod, because it can't keep three
   feet planted at all times; it has to shift its weight before each step.
   This is the trade you accepted for cheaper and simpler power.
2. **Power** — 12 servos can still brown out the Pi. Separate rails, common
   ground, a fuse. Solve this in week 4, not week 11.
3. **"On-task vs slacking" detection** that doesn't false-fire — a robot that
   squirts you while you're working is a *bad* robot. Tune with hysteresis.
4. **Warden payload** — a phone (~180g) is heavy for a small quadruped. If it
   can't carry it and still flee, fall back to "guards the phone on a pad and
   blocks/squirts you" instead of carrying it. Decide after you measure your
   build's payload.

## Scope ladder (so a bad week never leaves you with nothing)

| If… | Ship this instead |
|---|---|
| Walking isn't reliable by week 5 | **Stationary Squirt sniper** — bolted down, pan/tilt aims, still hilarious and complete |
| Only one mode comes together | Squirt mode alone is a full project |
| Warden payload fails | Guard-and-block version (no carrying) |
| Behind at week 10 | Cut Warden; polish Squirt + run the experiment |

The floor of this project is "a stationary robot that catches you on your
phone and squirts you, with a focus experiment." That alone wins a room.

## What carries straight over from your wristband

- **Sensor → decision → actuator** is your whole wristband; this is the same
  loop, bigger.
- **The pump driver is your motor driver, scaled up** — you drove a vibration
  motor with a transistor + flyback diode; the water pump is the same circuit
  with a logic-level **MOSFET** (more current). See PARTS.md.
- **VL53L0X** (your ToF sensor) is a fine choice for the cliff/edge and
  proximity sensing — you already know the library.
- **Simulate + unit-test before hardware** — build the IK and the mood state
  machine in a sim with tests first, exactly like `HapticMapper` and
  `haptic_simulator.html`. This is your strongest habit; use it.
- **Ethics/consent discipline** — you already do this well. Keep it.

## Files in this project

- `README.md` — this overview
- `START_HERE_KAZAKHSTAN.md` — **what to actually do right now**, with no
  parts and nothing built
- `PARTS.md` — bill of materials, wiring, and what each part is for
- `PURCHASE_LIST.md` — sourcing pass with verified prices and stock
- `BUILD_CHECKLIST.md` — week-by-week plan once parts arrive
- `cad/SKETCH.svg` — dimensioned views of the robot
- `cad/enforcer.scad` — parametric source for every printed part
- `cad/stl/` — ready-to-slice STLs
- `cad/make_stl.py` — the generator, if you want to change dimensions

## Open decisions

1. ~~**Hexapod (18 servos) or quadruped (12)?**~~ **DECIDED: quadruped
   (12 servos)**, matching the reference build.
2. ~~**Three modes or fewer?**~~ **DECIDED: two** — Squirt and Warden. The
   slouch-detection mode is dropped; it was the weakest of the three (a
   side-view camera angle it would rarely have, and the least funny payoff).
3. **Which mode first?** Recommendation: **Squirt**, stationary, end-to-end
   (detect → escalate → aim → fire) before you add walking. Earliest complete
   demo.
4. **Pi 5 4GB or 2GB?** Open, and it gates the order — see `PURCHASE_LIST.md`.
5. **Detection on-device or phone-offloaded?** Start on-device with a small
   model; only offload if it's too slow.

## Timeline anchor

A ~12–13 week build. Week 0 is procurement and design — and from Kazakhstan,
shipping is a **3–6 week** long pole, not 1–3 days, so the design and
simulation work has to happen *while* parts are in transit. That's what
`START_HERE_KAZAKHSTAN.md` is for.
