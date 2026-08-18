# Theory plan — mechatronics / electrical / computer engineering

A self-study curriculum for the theory side of the three fields, built
around one idea: **every piece of theory here gets attached to something
you have already touched on the wristband build** (`../assistive-tech-device/`).

You have already done a lot of real engineering — you debugged an I2C bus
that was lying to you, you found a 4C charge-rate hazard by reading a
datasheet, you wrote unit-testable firmware with the hardware dependency
sliced off. What you don't have yet is the vocabulary and the models that
let you *predict* those things instead of discovering them. That is what
this plan is for.

---

## Read this part before anything else

**1. Theory is not "the reading you do before building."** It is a set of
models that turn surprises into predictions. You spent a session
discovering that a GY-53 doesn't respond on I2C. Digital-logic theory
would not have told you about the `PS` pin — but the *habit* it teaches
(a pin is a node with a defined logic level, and "unconnected" is not a
level) is exactly the habit that gets you to check it in ten minutes
instead of a day.

**2. The order matters more than the content.** Almost every self-taught
engineer stalls in the same place: they try to learn control theory, hit
Laplace transforms, discover Laplace needs calculus and differential
equations, and quit. This plan makes every dependency explicit. If a
module says you need Calculus I, you need Calculus I. Skipping it doesn't
save time, it just moves the wall.

**3. This is a two-year plan at ~8 hours a week, not a summer.** Getting
through Phase 3 (control theory and DSP) properly is roughly the theory
content of the first two-and-a-half years of an EE degree. Every phase is
built to be useful on its own, so if you stop after Phase 2 you have still
gained real capability. But don't let anyone — including me — tell you
this is a twelve-week thing.

**4. The output of a study session is a worked problem, not a highlighted
page.** If you finish a session and haven't computed something, drawn
something, simulated something, or measured something, the session
probably didn't stick. Every module below has a "Do this" section for
exactly this reason.

---

## Assumptions I made about you

Stated openly so you can correct them:

- You're school-age or early university, self-taught on the practical
  side, aiming at an EE/CE/mechatronics degree or equivalent depth.
- Comfortable math: algebra, some trig. Calculus: not assumed.
- You can program (C++ well enough to write a testable header, JS, some
  build tooling). This is a genuine head start — it means Phase 1's
  computer-engineering track will feel easy and you can spend the
  freed-up time on the analog side, which is where the real gap is.
- Budget matters and shipping to Almaty is slow, so **every required
  resource here is free**, and every lab either runs in a simulator or
  uses parts you already own.

If any of those is wrong, the fix is in the placement test below, not in
rewriting the plan.

---

## The dependency map

This is the whole plan on one screen. Arrows mean "you genuinely cannot
do the right-hand thing without the left-hand thing."

```
                        ┌─ Algebra + Trig ─┐
                        │                  │
        ┌───────────────┘                  └──────────────┐
        ▼                                                 ▼
  [01] DC circuits                             Boolean algebra
  Ohm, KCL/KVL, Thevenin,                             │
  dividers, power                                     ▼
        │                                   [03] Digital logic
        │                                   gates, FSM, flip-flops
        ▼                                             │
   Calculus I  (derivatives)                          ▼
        │                                   Computer architecture
        ├──────────────┐                    datapath, memory, ISA
        ▼              ▼                              │
  Capacitors      [06] Kinematics                     ▼
  & inductors     & dynamics                  Embedded systems
  i = C dv/dt     F = ma, τ = Iα              timers, interrupts,
        │              │                      ADC, I2C/SPI/UART
        ▼              │                              │
  Calculus II          │                              │
  (integrals, RMS)     │                              │
        │              │                              │
        ▼              ▼                              │
  Complex numbers → [02] AC circuits                  │
  & phasors          impedance, RLC,                  │
        │            resonance, op-amps               │
        │                    │                        │
        ▼                    │                        │
  Differential ◄─────────────┘                        │
  equations                                           │
        │                                             │
        ▼                                             │
  Laplace transform ──────► [04] Signals & systems ◄──┘
  Fourier transform          LTI, convolution, H(s),
        │                    Bode, sampling, filters
        │                              │
        ▼                              ▼
  Linear algebra ──────────► [05] Control theory
                              PID, poles, stability,
                              root locus, state space
                                       │
                                       ▼
                            [06] Motors, sensors,
                            estimation, real mechatronics
```

Numbers in brackets are the module files in this directory.

---

## The four phases

| Phase | Duration @ 8h/wk | Math | Electrical | Computer | Mechanical |
|---|---|---|---|---|---|
| **1 — Foundations** | ~4 months | Algebra/trig repair, Calculus I | DC circuits, first semiconductors | Digital logic, number systems | Statics, kinematics |
| **2 — The core** | ~5 months | Calculus II, complex numbers, ODEs | AC/impedance, transients, op-amps | Computer architecture, MCU internals | Dynamics, DC motor model |
| **3 — Systems** | ~6 months | Laplace, Fourier, linear algebra | Filters, noise, signal conditioning | RTOS, real-time constraints | Control theory, estimation |
| **4 — Depth** | ongoing | as needed | pick a specialization | pick a specialization | pick a specialization |

**Phase-end deliverable.** Each phase ends with a build that could not
have been done at the start of it — see [`PROJECTS.md`](PROJECTS.md).
That project is the real exam. If you can't build it, you didn't learn
the phase, regardless of how many videos you watched.

---

## Placement test — do this first (60–90 minutes)

Work these on paper. No searching, no calculator beyond arithmetic. The
point is to find your actual starting line, not to score well. Answers
are at the bottom of this file.

**Tier A — gates Phase 1**

1. Solve for `R`: `V = IR`. Then solve `3x + 12 = 5(x − 2)`.
2. A 5V supply drives a 220Ω resistor in series with an LED that drops
   2.0V. What current flows?
3. Give `sin 30°`, `cos 60°`, `tan 45°`. What is the period of
   `sin(2πft)`?
4. A 10kΩ and a 4.7kΩ resistor are in series across 5V. What voltage
   appears across the 4.7kΩ?

**Tier B — gates Phase 2**

5. Differentiate `x³ − 5x + e^(2x)`.
6. What is `j`? Compute `(1 + j)/(1 − j)`.
7. Write the current–voltage relationship for a capacitor.
8. `R = 10kΩ`, `C = 1µF`. What is the time constant, and how long until
   the capacitor reaches ~63% of its final voltage?
9. Write −5 as an 8-bit two's-complement number.

**Tier C — gates Phase 3**

10. Solve `y'' + 3y' + 2y = 0` with `y(0) = 1`, `y'(0) = 0`.
11. What is the impedance of a capacitor at angular frequency ω?
12. A system has a pole at `s = −5`. What does that tell you about how
    it responds in time?
13. You sample a signal at 100 Hz. What is the highest frequency you can
    faithfully represent, and what happens to anything above it?
14. What is an eigenvector of a matrix, in one sentence?

**Tier D — you are past this plan's core**

15. For `L(s) = K / (s(s+2)(s+5))` in a unity-feedback loop, find the `K`
    at which the closed loop becomes marginally stable.
16. Sketch, in code, a discrete PID controller with anti-windup running
    on a fixed 10 ms tick. Say why derivative-on-measurement beats
    derivative-on-error.

**Scoring.**

- Struggled with Tier A → start at [`00-math-backbone.md`](00-math-backbone.md)
  §1, and do it properly. This is the highest-leverage month you will
  spend. Nothing downstream works without it.
- Tier A fine, Tier B shaky → start Phase 1 at full speed; you'll clear
  it in half the listed time.
- Tier A+B fine → start Phase 2 directly. Skim Module 01 as review.
- Tier C mostly fine → start Phase 3. Use Modules 01–03 as reference,
  not as coursework.
- Tier D fine → this plan is below you; go to Phase 4 and pick a
  specialization.

---

## How to study one module

The same loop every time. It takes about a week per section at 8h/wk.

1. **Read the module file here first.** It gives you the spine — the
   handful of ideas that make the textbook chapter readable. 30 minutes.
2. **Then read the real source** (textbook chapter or lecture). You now
   know what you're looking for, so this goes 2–3× faster than reading
   cold.
3. **Do the "Do this" lab.** Simulate it, build it, or compute it.
   Non-negotiable. This is where the learning actually happens.
4. **Do 5–10 textbook problems.** Not 50. Ten problems done carefully,
   with the answer checked, beats fifty skimmed.
5. **Take the self-check.** Closed book. If you can't answer, you don't
   move on — go back to step 2 for the specific thing you missed.
6. **Write it into your own words**, three sentences, in
   [`progress.html`](progress.html) or a notebook. If you can't compress
   it, you don't have it yet.

**A weekly rhythm that works:**

| | |
|---|---|
| 2 sessions × 90 min | new theory (steps 1–2) |
| 1 session × 120 min | problems + lab (steps 3–4) |
| 1 session × 60 min | review last week + self-check (steps 5–6) |

Spaced review is the single highest-return habit here. Every Friday,
re-derive one result from three weeks ago from scratch. It will feel
wasteful and it is not.

---

## Files in this directory

| File | What it is |
|---|---|
| [`00-math-backbone.md`](00-math-backbone.md) | The math track, sequenced by what it unlocks. Start here if the placement test says so. |
| [`01-circuits.md`](01-circuits.md) | DC and AC circuit theory. Ohm → KCL/KVL → Thevenin → impedance → resonance. |
| [`02-electronics-analog.md`](02-electronics-analog.md) | Semiconductors, diodes, BJTs/MOSFETs, op-amps, power. Your motor driver lives here. |
| [`03-digital-and-computer-engineering.md`](03-digital-and-computer-engineering.md) | Boolean algebra → logic → CPU architecture → embedded systems → protocols. |
| [`04-signals-and-systems.md`](04-signals-and-systems.md) | LTI systems, convolution, Fourier, Laplace, sampling, filters. The intellectual centre of EE. |
| [`05-control-theory.md`](05-control-theory.md) | Feedback, PID, stability, root locus, Bode, state space. |
| [`06-mechanics-motors-sensors.md`](06-mechanics-motors-sensors.md) | Statics, dynamics, the DC motor model, sensors, signal conditioning, estimation. |
| [`PROJECTS.md`](PROJECTS.md) | The project ladder — one build per phase that proves you learned it. |
| [`RESOURCES.md`](RESOURCES.md) | Annotated resources with what each is good and bad at, and link-check status. |
| [`progress.html`](progress.html) | Offline progress tracker. Open in a browser; state saves locally. |

---

## Placement test answers

1. `R = V/I`. — `3x + 12 = 5x − 10` → `22 = 2x` → `x = 11`.
2. `(5 − 2)/220 = 13.6 mA`. (The LED is not a resistor; you subtract its
   drop first. Module 02 explains why.)
3. `sin 30° = 0.5`, `cos 60° = 0.5`, `tan 45° = 1`. Period `= 1/f`.
4. `5 × 4.7/(10 + 4.7) = 1.60 V`.
5. `3x² − 5 + 2e^(2x)`.
6. `j = √(−1)`. `(1+j)/(1−j) = (1+j)²/((1−j)(1+j)) = (2j)/2 = j`.
7. `i = C · dv/dt`. (Current flows only when voltage is *changing*.)
8. `τ = RC = 10 ms`. 63% is reached at exactly one `τ` = 10 ms.
9. `5 = 00000101` → invert `11111010` → +1 → **`11111011`**.
10. Roots of `s² + 3s + 2` are `−1, −2`, so `y = Ae^(−t) + Be^(−2t)`.
    Applying the conditions: `A = 2`, `B = −1` → `y = 2e^(−t) − e^(−2t)`.
11. `Z_C = 1/(jωC)`.
12. A decaying exponential mode `e^(−5t)`, time constant `0.2 s`,
    essentially gone after ~1 s. Stable, non-oscillatory.
13. 50 Hz (Nyquist). Anything above folds back down and masquerades as a
    lower frequency — aliasing. It is unrecoverable after sampling,
    which is why anti-alias filtering happens *before* the ADC.
14. A vector the matrix only stretches, without rotating it.
15. Characteristic equation `s³ + 7s² + 10s + K = 0`. Routh array gives
    the `s¹` row as `(70 − K)/7`, so marginal stability at **`K = 70`**.
16. See [`05-control-theory.md`](05-control-theory.md) §5.7 — that
    section is the answer in full.
