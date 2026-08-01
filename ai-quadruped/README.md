# AI Quadruped — a small walking robot you can talk to

A 12-servo quadruped with an animated eye, a camera, and a voice loop
wired to an LLM whose "tools" are the robot's own movements. You talk to
it; it looks at you, answers, and *does something about it*.

Target: a working public demo in **12 weeks**, on a **$150–300** parts
budget.

## What actually makes this worth building

Nothing in that first paragraph is impressive on its own. Every phone in
the room already answers questions, and a talking robot is 2026's least
surprising object. If all this does is chat, people will politely watch
and then walk away.

The whole project lives or dies on one thing: **the language has to be
grounded in the robot's own body and senses.**

- *"What am I holding?"* → it **turns to look**, then answers. The
  turning is the moment, not the answer.
- *"Come here."* → it walks to you.
- *"Which of us is wearing red?"* → it scans the group, then points a leg.
- Nobody's talking to it → it idles. Shifts weight, the eye looks around,
  it stretches a leg.

That last one costs almost nothing and does more work than any other
feature. **Idle behaviour is what makes it read as alive.** A robot that
freezes between commands reads as a broken appliance; the same robot with
three seconds of aimless fidgeting reads as a creature.

## Why a quadruped and not a hexapod

The reference for this project was a six-legged robot. Four legs is the
better build at this budget:

- 12 servos instead of 18 — roughly 60% of the cost, and dramatically
  less power drama (18 servos stalling simultaneously can pull 20A+).
- Gaits are simpler and the failure modes are gentler.
- It reads as a creature *just as strongly*. Arguably more, because
  people project "dog" onto it without being asked to.

Nothing here is hexapod-specific. If the budget grows later, the same
software drives six legs with a longer leg list and a different gait
table.

## Architecture

```
                    ┌──────────────── Raspberry Pi ────────────────┐
  USB mic  ────────►│  speech-to-text ──► LLM (tool calling) ──► TTS├────► speaker
  camera   ────────►│  face detect / vision                        │
                    │        │                                     │
                    │        ▼                                     │
                    │  behaviour loop ──► gait engine ──► IK       │
                    └──────────┬──────────────────────┬────────────┘
                               │ SPI                  │ I2C
                               ▼                      ▼
                         eye display            PCA9685 ──► 12 servos
                         (GC9A01)              (own power rail)
```

The LLM does not drive the servos. It calls **named intents** —
`walk_forward`, `turn_to`, `look_at`, `wave`, `sit` — and the behaviour
loop decides how to execute them. Keep that boundary clean: it's what
lets you demo the robot with the network down.

## The two things that will actually bite you

Not the AI. Not the inverse kinematics. These:

**1. Power.** Servos get their own high-current rail (2S LiPo → UBEC),
logic gets its own, common ground. If the Pi shares a rail with 12
servos, it will reboot the first time the robot takes weight — usually
mid-sentence, in front of people. Budget a real battery pack, not a phone
power bank.

**2. Latency.** If it takes six seconds to answer, the room goes cold and
never comes back. Stream the speech-to-text and stream the text-to-speech
so it starts talking before the sentence is finished, and put a
"thinking" animation on the eye to cover the gap. A robot that *visibly
thinks* for 1.5s feels alive; one that sits frozen for 1.5s feels broken.
Same delay, opposite reading.

Target: **under 1.5s** from end-of-speech to first audio out.

## Honest scope

- This is a **demo robot**, not a product. It walks on flat indoor floors
  at low speed. It will not handle carpet edges, stairs, or being picked
  up mid-gait.
- The vision answers come from a general vision model and **will be
  confidently wrong sometimes**. Don't present it as recognition you can
  rely on. "It usually gets this right" is the honest claim, and it's
  still a good demo.
- The chassis is derived from an existing open design (or a bought kit).
  Say which parts are yours and which aren't, in the writeup and out loud.
  That reads as confidence, not weakness — real robotics work is built on
  platforms.

## De-scope ladder

Decided in advance, while calm, so a bad week is a decision instead of a
panic:

| Trigger | Response |
|---|---|
| Printer not producing accurate parts by **end of week 2** | Buy a kit chassis. Do not repair a printer instead of building a robot. |
| Not walking reliably by **end of week 5** | Bolt it to a stand. A stationary robot that tracks your face and talks is still a full project. |
| Voice loop flaky by **end of week 8** | Ship push-to-talk instead of wake-word. Nobody in the audience cares, and it removes the biggest live-failure source. |
| Behind at **week 10** | Cut Phase 4 (vision grounding) without hesitation. Phases 0–3 are already a complete project. |

The point of the ladder is that the worst realistic outcome is still a
working demo.

## Demo-day rules

- **Phone hotspot.** Venue Wi-Fi will fail you. Assume it.
- **Hard-code offline fallback answers** for 5–10 likely questions, so it
  is never mute in front of a crowd.
- **Rehearse the failures**, not the happy path: unplug the network
  mid-demo, have someone talk over you, let a stranger interrupt it
  mid-sentence, run the whole presentation slot on one battery charge.
  Every one of those will happen.

## Layout

```
ai-quadruped/
├── README.md            this file
├── PARTS.md             what to buy, what it costs, what to buy spares of
└── BUILD_CHECKLIST.md   12-week plan, one demoable milestone per phase
```
