# Module 05 — Control theory

**Prereqs:** Module 04. Specifically Laplace (§6), transfer functions,
poles, and Bode plots. Linear algebra (§8) for the state-space half.
**Time:** ~14 weeks.
**Unlocks:** robotics, motor control, process control, and the ability to
make something track a target instead of just responding to one.

This is the crown jewel of mechatronics. It is also the module people
most often try to start with, and it is genuinely not possible without
Module 04. If you skipped ahead to here, go back.

---

## Why this matters for your wristband

Your device is **open-loop**: sensor in, motor out, no feedback about
whether the output achieved anything. That's the right choice for v1.

But look at the whole system including the wearer, and you have a
closed loop: obstacle distance → sensor → haptic output → human
perception → human action → obstacle distance. The human is the
controller. And that framing immediately raises control-theoretic
questions that are real for your project:

- **Human reaction time is a transport delay** of roughly 200–300 ms.
  Delay is the most destabilising thing you can put in a feedback loop —
  it eats phase margin without touching gain. This is a rigorous reason
  why the alert has to fire far enough ahead, and §5.9 lets you compute
  how far.
- **Gain too high causes oscillation.** A wearer who over-corrects on
  every buzz will weave down a corridor. That is a high-gain loop
  oscillating, and it's a tuning problem, not a user problem.
- **Every millisecond of filtering delay (Module 04 §4.9) is added
  directly to that loop's delay.** The 314 mm lag we computed is not
  just staleness — it is phase lag in a loop containing a human.

You aren't going to design a controller for a human. But you will design
one for the motor in your Phase 3 project, and the vocabulary changes how
you think about the wristband too.

---

## 5.1 Open loop versus closed loop

**Open loop:** compute an output from the input and hope. Simple, always
stable, and completely at the mercy of disturbances and modelling error.
A toaster. Your wristband.

**Closed loop:** measure the output, compare to the target, act on the
error.

```
r ──►(+)──► e ──► C(s) ──► u ──► P(s) ──┬──► y
      ▲−                                 │
      └──────────── H(s) ◄───────────────┘
```

- `r` reference (what you want), `y` output (what you got)
- `e = r − y` error, `u` control effort
- `C(s)` controller, `P(s)` plant, `H(s)` sensor

**What feedback buys you:** rejection of disturbances, tolerance of a bad
plant model, and reduced sensitivity to component variation. You can
build a precise system from imprecise parts. That is a genuinely
remarkable thing and it is why feedback is everywhere.

**What feedback costs you:** the possibility of instability. An open-loop
system cannot oscillate itself to destruction; a closed-loop one can.
Everything from §5.5 onward is about managing that.

## 5.2 Block diagram algebra

The one formula you must know cold:

```
Closed-loop transfer function:   T(s) = G(s) / (1 + G(s)·H(s))
```

where `G = C·P` is the forward path and `G·H` is the **loop gain**.

Read the denominator carefully, because it's the whole subject:

- The roots of `1 + G·H = 0` are the **closed-loop poles**.
- Those roots — not the open-loop poles — determine stability.
- **Feedback moves poles.** Design *is* choosing where to move them.
- If `G·H = −1` at some frequency, the denominator is zero, the gain is
  infinite, and the system oscillates. That condition — magnitude 1,
  phase −180° — is the seed of every stability criterion in §5.6.

## 5.3 Performance specifications

For a second-order system with natural frequency `ω_n` and damping
ratio `ζ`, the standard step-response specs:

```
Overshoot:      %OS = 100 · exp(−ζπ / √(1−ζ²))
Settling (2%):  t_s ≈ 4 / (ζ·ω_n)
Peak time:      t_p = π / (ω_n·√(1−ζ²))
Rise time:      t_r ≈ 1.8 / ω_n
```

Useful reference points:

| ζ | %OS |
|---|---|
| 0.4 | 25% |
| 0.5 | 16% |
| 0.6 | 9.5% |
| **0.707** | **4.3%** |
| 0.8 | 1.5% |
| 1.0 | 0% |

`ζ = 0.707` is the usual default — fast, with only slight overshoot.

**And notice the structure:** `ζ` alone sets overshoot; `ω_n` alone sets
speed. They're independent knobs, which is exactly why pole placement is
a sensible design method. Read those two numbers off any second-order
system and you know how it will behave, before simulating anything.

## 5.4 PID control

The controller that runs most of the industrial world.

```
u(t) = Kp·e(t) + Ki·∫e dt + Kd·de/dt
```

**Proportional** — act in proportion to the current error.
More `Kp` = faster and stiffer. Too much = oscillation. **On its own, P
control leaves a steady-state error**, because if the error were zero the
output would be zero, and something has to hold the actuator up against
gravity, friction, or load.

**Integral** — accumulate error over time.
This is what drives steady-state error to *exactly* zero: as long as any
error persists, the integrator keeps growing and keeps pushing. The
costs: it adds phase lag (destabilising), it slows response, and it
**winds up**.

> **Integrator windup** is the classic bug. If the actuator saturates —
> your PWM is already at 255 and the target still isn't reached — the
> error stays positive and the integrator keeps accumulating into a huge
> number. When the target is finally reached, the controller has to
> "unwind" all of that before it can back off, producing a massive
> overshoot. Every practical implementation needs anti-windup. See §5.7.

**Derivative** — respond to the *rate* of error change.
Anticipates, adds damping, allows higher `Kp`. The cost: **derivative
amplifies noise**, badly, because differentiation is a high-pass
operation and noise is high-frequency. A raw D term on a noisy sensor is
worse than no D term. It must be low-pass filtered, always.

**Two implementation details that separate working PID from textbook
PID:**

1. **Derivative on measurement, not on error.** A step change in the
   setpoint makes `de/dt` momentarily infinite, and the controller slams
   the actuator — "derivative kick." Differentiating the *measurement*
   instead (with a sign flip) gives identical disturbance rejection with
   no kick, because the measurement doesn't step when the setpoint does.
2. **Filter the derivative.** Use `Kd·s/(1 + s·τ)` rather than `Kd·s`,
   with `τ` typically `Kd/(8..20·Kp)`.

### Tuning

**Ziegler–Nichols (closed loop):** raise `Kp` with I and D off until the
output oscillates steadily. Record that gain as `Ku` and the oscillation
period as `Tu`. Then:

| Controller | Kp | Ti | Td |
|---|---|---|---|
| P | 0.5·Ku | — | — |
| PI | 0.45·Ku | Tu/1.2 | — |
| PID | 0.6·Ku | Tu/2 | Tu/8 |

Z-N is aggressive — it targets about 25% overshoot — and it's a starting
point, not an answer. Know it, because everyone references it, and then
tune from there.

**Manual tuning that actually works:**
1. All gains to zero.
2. Raise `Kp` until it oscillates, then back off to about half.
3. Raise `Ki` until steady-state error is gone; back off if it rings.
4. Raise `Kd` to damp overshoot; back off as soon as noise appears in
   the control signal.

Watch the *control signal*, not just the output. A controller that looks
fine at the output while the actuator thrashes is about to destroy
something.

## 5.5 Stability

**The definition:** all closed-loop poles strictly in the left half
plane.

**Routh–Hurwitz** determines stability from the characteristic
polynomial's coefficients without finding the roots. Build the array;
the system is stable if and only if every entry in the first column has
the same sign, and the number of sign changes equals the number of
right-half-plane poles.

Worked, because this is placement question 15. For
`L(s) = K/(s(s+2)(s+5))` with unity feedback, `1 + L = 0` gives:

```
s³ + 7s² + 10s + K = 0

s³ │   1        10
s² │   7         K
s¹ │ (70−K)/7    0
s⁰ │   K
```

Stability needs `(70−K)/7 > 0` and `K > 0`, so `0 < K < 70`, and
**`K = 70` is marginal stability** — the point where the poles sit
exactly on the imaginary axis and the system oscillates forever.

## 5.6 Root locus, Bode margins, Nyquist

Three views of the same question: how does the loop behave as gain
changes?

**Root locus** — plot the closed-loop poles as `K` sweeps from 0 to ∞.
The rules (branches start at open-loop poles, end at zeros or infinity;
real-axis segments lie to the left of an odd count of poles and zeros;
asymptote angles `(2k+1)·180°/(n−m)`) let you sketch it by hand, and the
sketch tells you instantly whether more gain helps or destabilises.
Learn to draw these by hand even though software does it — the hand
sketch is what builds intuition.

**Bode margins** — the practical engineer's tool.
- **Gain margin:** how much more gain before instability, measured where
  the phase crosses −180°.
- **Phase margin:** how much more phase lag before instability, measured
  where the magnitude crosses 0 dB.

Design targets: gain margin > 6 dB, phase margin 45°–60°. The handy rule
of thumb `PM ≈ 100·ζ` (for `ζ < 0.7`) connects a frequency-domain
measurement to a time-domain overshoot, which is why phase margin is the
number practising engineers quote.

**Nyquist criterion** — the most general: `Z = N + P`, where `Z` is
closed-loop RHP poles, `N` is clockwise encirclements of −1 by the
`G(jω)H(jω)` plot, and `P` is open-loop RHP poles. Necessary when the
open-loop system is already unstable, where Bode's simpler reading fails.

## 5.7 Digital control — the version you'll actually write

Everything above is continuous. Your implementation is discrete, sampled
at some period `T`.

**Rule of thumb:** sample at 10–20× your closed-loop bandwidth. Too slow
and you lose phase margin (a sampler adds an effective delay of `T/2`,
and delay is phase lag). Too fast and the derivative term amplifies
quantisation noise.

Here is a PID implementation with the things textbooks omit — fixed
timestep, derivative on measurement, filtered derivative, and dynamic
integrator clamping for anti-windup:

```c
typedef struct {
    float kp, ki, kd;
    float tau;                 // derivative low-pass time constant, s
    float out_min, out_max;    // actuator limits
    float dt;                  // fixed sample period, s

    float integrator;
    float differentiator;
    float prev_error;          // for trapezoidal integration
    float prev_measurement;    // for derivative-on-measurement
} PID;

float pid_update(PID *p, float setpoint, float measurement) {
    float error = setpoint - measurement;

    float proportional = p->kp * error;

    /* Trapezoidal integration - more accurate than rectangular,
       same cost. */
    p->integrator += 0.5f * p->ki * p->dt * (error + p->prev_error);

    /* Anti-windup by dynamic clamping: allow the integrator only as
       much range as the proportional term has left before saturation.
       Better than a fixed clamp because the usable range changes with
       operating point. */
    float lim_max_i = (p->out_max > proportional) ? p->out_max - proportional : 0.0f;
    float lim_min_i = (p->out_min < proportional) ? p->out_min - proportional : 0.0f;
    if (p->integrator > lim_max_i)      p->integrator = lim_max_i;
    else if (p->integrator < lim_min_i) p->integrator = lim_min_i;

    /* Derivative on MEASUREMENT (note the sign) so a setpoint step
       produces no derivative kick, low-pass filtered so sensor noise
       isn't amplified. Bilinear-transform discretisation. */
    p->differentiator =
        (-2.0f * p->kd * (measurement - p->prev_measurement)
         + (2.0f * p->tau - p->dt) * p->differentiator)
        / (2.0f * p->tau + p->dt);

    float out = proportional + p->integrator + p->differentiator;
    if (out > p->out_max)      out = p->out_max;
    else if (out < p->out_min) out = p->out_min;

    p->prev_error       = error;
    p->prev_measurement = measurement;
    return out;
}
```

**Call this on a fixed timer tick, never from a free-running loop.** If
`dt` varies, `ki` and `kd` are effectively varying too, and your tuning
means nothing. This is the most common practical PID bug, and it's the
reason the struct carries `dt` rather than measuring elapsed time.

Also learn: the z-transform view of controllers, discretisation methods
(forward/backward Euler, Tustin/bilinear), and how each maps the s-plane
into the z-plane.

## 5.8 State-space control

Transfer functions handle one input and one output. Real systems have
many of both, and state space handles them all at once:

```
ẋ = Ax + Bu
y = Cx + Du
```

`x` is the state vector — the minimum set of variables that, with future
inputs, determines all future behaviour. For a motor: current and speed.
For a pendulum: angle and angular velocity.

**Key results:**

- **The eigenvalues of `A` are the poles.** State space and transfer
  functions describe the same physics. This is where Module 00 §8 pays
  off.
- **Controllability** — can the input reach every state? Check the rank
  of `[B AB A²B …]`.
- **Observability** — can you infer every state from the output? Check
  the rank of `[C; CA; CA²; …]`.
- **Pole placement** — if controllable, `u = −Kx` can put the
  closed-loop poles *anywhere you want*. That's a strictly stronger
  design capability than PID.
- **Observers / state estimators** — you rarely measure every state, so
  estimate the rest from a model plus available measurements. The
  Luenberger observer is the deterministic version; the **Kalman filter**
  is the optimal version when the noise is Gaussian.
- **LQR** — choose `K` by minimising a cost balancing state error
  against control effort. Turns "tune six gains by feel" into "choose two
  weighting matrices," which is a much better-posed problem.

## 5.9 Nonlinearity, delay, and where the theory stops

Everything above assumes linear and time-invariant. Reality doesn't.

- **Saturation** — actuators have limits. This is why anti-windup exists.
- **Backlash and friction** — gear slop and stiction produce limit
  cycles that no linear model predicts.
- **Transport delay** — `e^(−sT)` in the loop. Unity magnitude at every
  frequency, but phase lag growing without bound. **It costs you phase
  margin for free and is the hardest thing to control around.** The Smith
  predictor is the classic remedy.
- **Linearisation** — expand about an operating point and use the linear
  tools locally. The same move as small-signal analysis in Module 02
  §2.4, which is why that section is worth doing properly.
- **Describing functions** for nonlinearities, **Lyapunov** methods for
  nonlinear stability. Both beyond this plan; know the names.

**Back to your wristband:** the wearer's 200–300 ms reaction time is a
transport delay in the human loop. At a walking speed of 1.4 m/s that's
280–420 mm of travel before any response begins — before adding your
50 ms sampling and any filter lag. Your Near zone starts at 600 mm.
**The margin between "alert fires" and "wearer has already arrived" is
thinner than it looks**, and now you can compute it rather than guess.
That is a genuine finding for `README.md`'s failure-modes section, and
it came out of control theory rather than out of testing.

---

## Do this — labs for Module 05

Use Python with `python-control` (`pip install control`), or GNU Octave.
Both free, both do everything MATLAB's Control System Toolbox does for
this material.

1. **Second-order playground.** Define `H(s) = ω_n²/(s² + 2ζω_n s + ω_n²)`
   and plot step responses for `ζ = 0.1, 0.4, 0.707, 1, 2`. Measure the
   overshoot and settling time off each plot and check them against the
   formulas in §5.3.
2. **Root locus by hand, then by computer.** Sketch the locus for
   `K/(s(s+2)(s+5))` on paper. Find the `K` where it crosses the
   imaginary axis. Confirm you get 70, matching the Routh result.
3. **Simulate a real DC motor** using the model from Module 06 §6.4.
   Wrap a P controller around speed, then PI, then PID. Watch P leave a
   steady-state error and I remove it.
4. **Break it on purpose.** Add saturation to that loop and watch
   integrator windup produce a huge overshoot. Then add the clamping
   from §5.7 and watch it disappear. **This is the single most valuable
   control lab on the list** — the failure is dramatic and the fix is
   visible.
5. **Add delay.** Insert 100 ms of transport delay into a stable loop
   and watch the phase margin evaporate. Find the delay that makes it
   oscillate. This is the human-reaction-time effect, made concrete.
6. **Build it in hardware.** A DC motor, an encoder or an IR tachometer,
   an H-bridge, and closed-loop speed control on your Nano. This is
   Project 3 in [`PROJECTS.md`](PROJECTS.md) and it is where control
   theory stops being mathematics.

---

## Self-check — closed book

1. Give one thing feedback buys you and one thing it costs you.
2. Write the closed-loop transfer function and say what its denominator's
   roots are.
3. Why does proportional-only control leave a steady-state error?
4. What is integrator windup, when does it occur, and how do you prevent
   it?
5. Why does the D term amplify noise, and what are the two standard
   mitigations?
6. Why is derivative-on-measurement preferable to derivative-on-error?
7. `ζ = 0.5`, `ω_n = 10 rad/s`. Give overshoot and 2% settling time.
8. Define gain margin and phase margin, and give a target for each.
9. Use Routh–Hurwitz to find the stable range of `K` for
   `s³ + 5s² + 6s + K`.
10. What does controllability mean, and how do you test for it?
11. Why is transport delay harder to control around than a simple lag?
12. Your control loop's `dt` varies between 8 ms and 30 ms depending on
    what else the firmware is doing. Which gains are affected and why?

---

## Resources for this module

- **Brian Douglas's control lectures** — the single best free control
  resource in existence. Genuinely excellent intuition, short videos.
  Watch alongside a textbook for the mechanics.
- **Nise, *Control Systems Engineering*** — the most readable standard
  textbook. Good worked examples.
- **Ogata, *Modern Control Engineering*** — more rigorous, better on
  state space.
- **Åström & Murray, *Feedback Systems*** — free PDF (fbswiki.org),
  rigorous, modern, and written by two of the field's best. Harder than
  Nise; read it second.
- **`python-control`** (python-control.readthedocs.io) — free, mirrors
  MATLAB's control toolbox API closely enough that MATLAB-based textbook
  examples translate directly.
- **GNU Octave** — free MATLAB-compatible alternative if a textbook's
  examples are MATLAB-only.
