# Speech, hearing, and an LLM

You already have **see**, **sense** and **walk**. This file is the other three:
**speak**, **hear**, and **think in words** — what they cost, where they can
physically run, and the one place they must never go.

Behaviour and safety: [`BEHAVIOURS.md`](BEHAVIOURS.md). Architecture:
[`README.md`](README.md).

---

## The constraint that decides everything

A Pi Zero 2 W has **512 MB**, and about **422 MB** usable after a headless
boot. Here is what the pieces cost:

```
component                                         RAM     note
  YOLOv8n @320 (NCNN) + camera + OpenCV          200MB    your perception today
  openWakeWord / Porcupine wake word              40MB    listens for a trigger
  whisper.cpp tiny.en (Q5)                       180MB    speech -> text
  Piper TTS (small voice)                        120MB    text -> speech
  Qwen2.5-0.5B-Instruct Q4 (smallest useful LLM) 400MB    the LLM itself

available: 422 MB
  vision only (today)                 200MB  FITS
  vision + wake word + TTS            360MB  FITS
  vision + wake word + STT + TTS      540MB  DOES NOT FIT (over by 118 MB)
  ...all of that + a 0.5B LLM         940MB  DOES NOT FIT (over by 518 MB)
```

And even if it fitted, four A53 cores at 1 GHz give roughly **1–3 tokens per
second** — a 40-token reply would take **15–40 seconds**.

**So the LLM does not run on the robot.** That isn't a budget problem you can
buy your way out of on this chassis: the Pi 5 + AI HAT+ that *could* run one
is physically larger than Sesame and eats ~10 W (see PARTS.md, "What to skip").

## The split that works

The robot keeps the **cheap ends** of audio. The expensive thinking happens on
a laptop on your desk.

```
  ROBOT (Pi Zero 2 W)                    COMPANION (your laptop)
  ─────────────────────                  ────────────────────────
  camera → YOLO → scene ──────────────►  Whisper  (speech → text)
  mic → wake word (local, 40MB)          Ollama   (the LLM, local)
  speaker ← audio                        Piper    (text → speech)
  ESP32 → legs, face                          │
        ▲                                     │
        └──────────── WiFi ───────────────────┘
```

Round trip is roughly **2–4 seconds**, which is about a natural conversational
pause.

**Run the LLM locally with Ollama, not a cloud API.** No internet needed at a
competition — just your own hotspot or travel router, which
`BUILD_CHECKLIST.md` already tells you to bring. A cloud API dies on venue
WiFi, and "our robot needs the internet" is a bad answer to a judge.

---

## 🔴 The LLM must never be able to fire the pump

Non-negotiable, and worth stating explicitly in your writeup.

```
  scene → STATE MACHINE → walk / aim / FIRE     ← 5 interlocks, no LLM here
                       └→ LLM → taunt → speaker ← words only, never actions
```

The mood state machine decides what the robot *does*. The LLM only decides
what it *says*. A language model with authority over a water pump aimed at a
person is exactly the demo that ends badly, and exactly the design a jury will
attack. Keep the wire between them one-directional: scene facts go **to** the
LLM, and only audio comes **back**.

The five firing interlocks in `BEHAVIOURS.md` stay where they are, in
firmware, with no LLM in the path.

---

## Hardware to add: one part

| Item | ~€ | Note |
|---|---|---|
| **INMP441 I2S MEMS microphone** | ~4 | Shares the I2S bus with the MAX98357A you already have — mic on receive, amp on transmit, same clock lines. Known-good Pi configuration |

~2 g, negligible power, nothing else needed. You already own the amp and the
8 Ω speaker.

---

## Make the LLM earn its place

Plain chat — *"hello robot, how are you"* — is the weak version. It's a
commodity in 2026 and adds nothing to your technical claim. A jury has seen it.

The strong version: **feed the LLM the scene, not just the speech.**

```
  person present · phone visible 4m12s · 23:40 · 3rd offence tonight
       ↓
  "Fourth time tonight. It's almost midnight. Put it down."
```

Now the LLM is generating **context-aware, personalised** taunts out of your
own perception system. That ties straight into the commitment-device thesis,
uses work you already did, and is far more interesting than a chatbot bolted
to a robot.

Same pipeline, same hardware — much better story.

---

## What it costs

**+2–3 weeks** on a plan that is already 14: audio hardware bring-up, wake
word, the streaming pipeline, latency tuning.

And an honest trade-off worth naming out loud. A talking robot impresses a
**room**; it does much less for a **jury**, because calling an LLM is
something anyone can do now. Your distinctive content is the autonomy, the
motion engine, and the experiment. So this is a **layer on top of a working
robot — never a substitute for one.**

In the scope ladder this sits **below Warden**. Cut it before you cut the
motion engine or the experiment.

## How to phase it

1. **Pre-recorded taunt clips** — already Week 7. Costs nothing, needs no mic,
   and gets you most of the "it talks!" effect on a demo table.
2. **Mic + wake word** once the core loop works. Now it *hears*.
3. **LLM-generated taunts** — same speaker, same pipeline, better words. This
   is the version worth writing up.
4. **Free-form conversation** last, if there is time left.

Do not start at 4.
