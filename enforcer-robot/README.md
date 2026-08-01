# The Enforcer — an AI spider robot that holds you accountable

A six-legged desk robot with a camera, a personality, and consequences. It
watches you work. Slack off — pick up your phone, slouch, wander away — and
it doesn't beep politely. It notices, gives you attitude, stalks toward you,
and **squirts you with water**. Get back on task and it backs off, smug.

One robot, three "personalities" (modes):

| Mode | Detects | What it does |
|---|---|---|
| **Squirt** (flagship) | phone in your hand / head down / you left the desk | escalates, then squirts you |
| **Warden** | you reaching for your phone during a focus session | flees across the desk with your phone so you can't cheat |
| **Posture Sheriff** | you slouching / "tech neck" | sasses and escalates until you sit up |

All three share one body, one camera, one brain. They differ only in *what
counts as bad behavior* and *what the robot does about it*. So this is **one
project with three demo modes**, not three robots.

## Why this isn't "ChatGPT on legs"

The intelligence shows up as **behavior, not conversation.** The robot never
needs to hold a chat to be impressive — it hunts, taunts, dodges, and
strikes. That's the whole point, and it's what makes the AI + the legs both
*essential* instead of decorative:

- The **AI** has to actually understand the scene (are you working or on your
  phone? are you slouching?) — real computer vision, not a scripted toy.
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
Jugend-forscht entry:

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
                         │   • pose / head angle (MediaPipe)             │
                         │            │                                  │
                         │            ▼                                  │
                         │   MOOD STATE MACHINE  (the personality)       │
                         │   CHILL → SUSPICIOUS → WARNING → STRIKE → SMUG│
                         │       │              │            │           │
                         │       ▼              ▼            ▼           │
                         │  eye display     body language   fire!        │
                         └───────┬───────────────┬───────────┬──────────┘
                                 │ SPI           │ I2C        │ GPIO
                                 ▼               ▼            ▼
                            eye (GC9A01)   PCA9685 ×2 ──► 18 leg servos
                                                    └──► 2 head servos (pan/tilt)
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

## The three modes, in engineering terms

They're the same pipeline with a different **trigger** and **response**:

- **Squirt** — trigger: `cell_phone` detected near the person's hands, OR head
  pitched down for > N seconds, OR no person at the desk for > N seconds.
  Response: escalate through moods, then pulse the pump.
- **Posture Sheriff** — trigger: neck/torso angle past a threshold (from a
  side view) held for > N seconds. Response: escalate, then squirt (or a
  gentler nudge — your call).
- **Warden** — the phone rides on a tray on the robot's back. Trigger: a hand
  approaching the robot/phone during a locked focus session. Response: walk
  away from the hand (reactive avoidance) while avoiding desk edges.

Design the software so a **Mode** is a small object with
`should_trigger(scene)` and `respond()` — then adding a mode is ~30 lines,
not a rewrite.

## The personality — how "attitude" is actually built

Personality here = **moods expressed through motion, an eye, and sound**, driven
by the state machine. No dialogue required.

- **Eye display** (round LCD): narrow/suspicious, wide/alarmed, a smug
  half-lid. One cheap part does most of the "it's alive" work.
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

1. **Walking reliably** — not the AI. Budget real time for gait tuning.
2. **Power** — 18 servos can brown out the Pi. Separate rails, common ground,
   a fuse. Solve this in week 4, not week 11.
3. **"On-task vs slacking" detection** that doesn't false-fire — a robot that
   squirts you while you're working is a *bad* robot. Tune with hysteresis.
4. **Warden payload** — a phone (~180g) is heavy for a small hexapod. If it
   can't carry it and still flee, fall back to "guards the phone on a pad and
   blocks/squirts you" instead of carrying it. Decide after you measure your
   build's payload.

## Scope ladder (so a bad week never leaves you with nothing)

| If… | Ship this instead |
|---|---|
| Walking isn't reliable by week 5 | **Stationary Squirt sniper** — bolted down, pan/tilt aims, still hilarious and complete |
| Only one mode comes together | Squirt mode alone is a full project |
| Warden payload fails | Guard-and-block version (no carrying) |
| Behind at week 10 | Cut Posture + Warden; polish Squirt + run the experiment |

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
- `PARTS.md` — bill of materials, wiring, and what each part is for
- `PURCHASE_LIST.md` — **the real cart**: verified 2026-08-01 prices, stock
  counts, which shop, and the budget corrections
- `BUILD_CHECKLIST.md` — week-by-week plan to the Jugend forscht window

## How to start (in your next session)

1. Open a new session in this repo and read these three files.
2. Make the **two decisions** in "Open decisions" below.
3. Start at **Week 0** in `BUILD_CHECKLIST.md`: place one parts order
   (with spares), fix or replace the 3D printer, and build the leg-IK +
   state-machine simulator while parts ship.

## Open decisions to make first

1. ~~**Hexapod (18 servos) or quadruped (12)?**~~ **DECIDED: quadruped
   (12 servos).** Less power drama, cheaper, reads as a creature just as
   well, and the software is identical either way.
   [`PURCHASE_LIST.md`](PURCHASE_LIST.md) is costed for 12 legs + 2 head
   servos.
2. **Which mode first?** Recommendation: **Squirt**, stationary, end-to-end
   (detect → escalate → aim → fire) before you add walking. Earliest complete
   demo.
3. **Detection on-device or phone-offloaded?** Start on-device on a Pi 5 with
   a small model; only offload if it's too slow.

## Timeline anchor

Today is early August. Jugend forscht registration is typically **~30
November**, with Berlin regional competitions Feb–March (confirm current
dates). A ~12–13 week build starting now lands you at registration with
results and a rehearsed demo. Week 0 is procurement — that's the long pole
because of shipping, so do it first.
