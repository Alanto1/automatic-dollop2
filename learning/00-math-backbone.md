# Module 00 — The math backbone

**Time:** 6–10 months of the total plan, running *in parallel* with the
engineering modules, never as a separate blocking phase.
**Unlocks:** everything.

---

## The one thing to understand about engineering math

You are not learning math to be a mathematician. You are learning a
specific, surprisingly small set of tools, each of which exists to answer
a specific engineering question. Learn each tool attached to its
question and it sticks. Learn it as abstract manipulation and it
evaporates.

Here is the whole backbone, with the question each piece answers:

| Math | The engineering question it answers |
|---|---|
| Algebra | What value must this component be? |
| Trigonometry | How do I describe something that oscillates? |
| Complex numbers | How do I handle amplitude and phase at the same time? |
| Derivatives | How fast is this changing right now? |
| Integrals | How much accumulated over time? |
| Differential equations | Given the physics, what does the signal actually do? |
| Laplace transform | How do I turn a differential equation into algebra? |
| Fourier transform | What frequencies is this signal made of? |
| Linear algebra | How do I handle many coupled variables at once? |
| Probability | How wrong is my sensor, and how do I fight it? |

That's it. That is the list. It is not endless.

---

## §1 — Algebra and trigonometry repair

**Time:** 3–5 weeks if rusty, skip if the placement test Tier A was easy.

Do not skip this if you were shaky. Every single downstream failure I
have seen in self-taught engineers traces back to algebra that was
"mostly fine."

**What you need, specifically:**

- Rearranging equations fluently, including when the unknown appears on
  both sides or in a denominator. `V = IR` is trivial; solving
  `I_bat = 1200 · V_prog / R_prog` for `R_prog` given a target current is
  the same skill and it is the one you actually used on the TP4056.
- Exponentials and logarithms. `e^x`, `ln`, `log₁₀`, and the laws.
  **Non-negotiable** — decibels, RC decay, diode equations, and Bode
  plots are all built on these.
- Why decibels exist: `dB = 20·log₁₀(V_out/V_in)` for voltage,
  `10·log₁₀(P_out/P_in)` for power. The factor of 2 difference trips up
  everyone once; it's because power goes as voltage squared.
- Trig: the unit circle, `sin`/`cos`/`tan`, the identity
  `sin²θ + cos²θ = 1`, and the angle-sum formulas.
- **The single most important trig fact in all of EE:** a sinusoid is
  described by three numbers — amplitude, frequency, phase —
  `v(t) = A·sin(2πft + φ)`. Adding two sinusoids *of the same frequency*
  always gives another sinusoid of that same frequency, with a different
  amplitude and phase. Nothing new is created. This is why AC circuit
  analysis is possible at all.

**Do this:** derive, without looking it up, the resistor value needed to
set a TP4056 to charge your 250 mAh cell at 0.5C (125 mA). The datasheet
relation is `I_BAT = 1200 · (V_PROG / R_PROG)` with `V_PROG = 1.0 V`.
Then check it against the ~10 kΩ figure in your `PURCHASE_LIST.md`. You
should get 9.6 kΩ, and now you know *why* 10 kΩ is the right nearest
standard value and what current it actually gives.

**Resource:** Khan Academy Algebra II + Trigonometry. Fast, free, and it
tests you rather than lecturing at you.

---

## §2 — Calculus I: derivatives

**Time:** 6–8 weeks.
**Unlocks:** capacitors, inductors, velocity/acceleration, every rate.

**The idea in one sentence:** the derivative is the instantaneous rate of
change — the slope of the tangent line — and it is what you get when you
take a difference quotient and shrink the interval to zero.

**Why an engineer cares:** because two of the five basic circuit
components are *defined* by derivatives.

```
Capacitor:   i = C · dv/dt     current flows only when voltage changes
Inductor:    v = L · di/dt     voltage appears only when current changes
```

Read those two lines until they feel obvious. They explain, with no
further theory:

- **Why a capacitor blocks DC.** DC means `dv/dt = 0`, so `i = 0`.
- **Why a capacitor "smooths" a supply.** To change its voltage quickly
  you'd need enormous current, so it resists voltage change.
- **Why your motor needs a flyback diode.** When the transistor switches
  off, the motor's inductance wants to keep current flowing. `di/dt` goes
  hugely negative over a switching time of nanoseconds, so `v = L·di/dt`
  produces a large reverse spike — tens of volts from a 5V circuit. That
  spike is what kills the transistor. The 1N4148 in your BOM gives the
  current a path so `di/dt` stays finite. **This is the single clearest
  example in your whole build of theory predicting a component.**

**What to actually learn:**

- Limits (conceptually — you don't need epsilon-delta rigour)
- Power rule, product rule, quotient rule, chain rule
- Derivatives of `e^x`, `ln x`, `sin`, `cos`
- Implicit differentiation (light)
- Maxima/minima — this is how you find the operating point that maximises
  power transfer, efficiency, or torque

**Do this:** In Falstad's circuit simulator, build a 10 kΩ resistor in
series with a 1 µF capacitor across a 5 V step source. Watch the voltage
curve. Then *predict on paper* the voltage at t = 10 ms, 20 ms, 30 ms
using `v(t) = 5(1 − e^(−t/RC))`, and check the simulator agrees. When it
does, you have just verified that the differential equation describing
the circuit and the exponential you memorised are the same object.

**Resource:** Paul's Online Math Notes (Calculus I) — complete, free,
worked examples, better than most paid textbooks. Watch 3Blue1Brown's
*Essence of Calculus* alongside it for intuition, but do not use 3B1B
alone: it builds understanding without building fluency, and you need
both.

---

## §3 — Calculus II: integrals

**Time:** 5–7 weeks.
**Unlocks:** RMS, energy, charge, average power, convolution.

**The idea:** the integral accumulates. It is the inverse of the
derivative (that's the Fundamental Theorem of Calculus, and it is
genuinely the punchline of the whole subject).

**Why an engineer cares:**

- **Charge:** `Q = ∫i dt`. Your 250 mAh battery rating is literally an
  integral — 250 mA flowing for one hour, or 25 mA for ten hours.
  Battery-life estimation is integration and nothing more.
- **Energy:** `E = ∫p dt`. Capacitor energy `E = ½CV²`, inductor energy
  `E = ½LI²` — both fall out of integrating power.
- **RMS:** `V_rms = √( (1/T)∫v² dt )`. This is *why* a sine wave's RMS
  is `V_peak/√2` — it's not a magic constant, it's that integral
  evaluated. RMS is defined the way it is because it's the DC voltage
  that would deliver the same heating power.
- **Average value:** what a PWM signal's average is, and therefore what
  your motor actually "sees."

**What to learn:** the fundamental theorem, substitution, integration by
parts, definite integrals, and improper integrals (lightly — you need
them for the Fourier and Laplace transforms).

**Do this:** compute, by hand, the average value of your motor's drive
waveform in the Near zone: PWM duty 200/255 at 490 Hz, gated on for
120 ms then off for 150 ms. First find the average during an "on" burst
(`5 V × 200/255 = 3.92 V`), then average that over the full 270 ms pulse
cycle (`3.92 × 120/270 = 1.74 V`). You have just computed a nested
average — an integral of an integral — and you now know the actual mean
voltage your motor sees in that zone. That number is what determines
battery drain.

**Resource:** Paul's Online Math Notes (Calculus II).

---

## §4 — Complex numbers and phasors

**Time:** 2–3 weeks. Short, and enormously high leverage.
**Unlocks:** all of AC analysis. Do this before Module 01's AC half.

Most students meet complex numbers as an algebraic curiosity and never
see the point. Here is the point.

**The problem they solve.** In an AC circuit, everything oscillates at
the same frequency, but different components shift the *phase*. To track
a signal you need two numbers — amplitude and phase — and doing algebra
on (amplitude, phase) pairs with trig identities is miserable. Complex
numbers package both into one object where the miserable trig becomes
ordinary multiplication.

**Euler's formula is the whole trick:**

```
e^(jθ) = cos θ + j·sin θ
```

A rotating vector of length `A` at angular frequency `ω` is `A·e^(jωt)`.
Its real part is the actual physical signal. Multiplying by `e^(jφ)`
rotates it by φ — that is, shifts its phase. So "shift phase by 90°"
becomes "multiply by `j`". That's it. That's the entire reason complex
numbers are in electrical engineering.

**Then impedance falls out for free:**

```
Resistor:   Z = R              phase shift 0°
Capacitor:  Z = 1/(jωC)        current leads voltage by 90°
Inductor:   Z = jωL            current lags voltage by 90°
```

And now **every DC technique you learned works unchanged on AC** — series
and parallel combination, voltage dividers, Thevenin, KCL/KVL — just with
complex `Z` instead of real `R`. That is an enormous payoff for two
weeks of work.

**What to learn:** rectangular ↔ polar form, magnitude and argument,
multiplication and division in polar form (multiply magnitudes, add
angles), the complex conjugate, and Euler's formula.

**Do this:** compute the impedance of a 100 nF capacitor at 490 Hz (your
PWM frequency) and at 400 kHz (your I2C clock). You should get about
−j3.2 kΩ and −j4.0 Ω. Now you understand at a gut level why stray
capacitance is irrelevant at audio frequencies and dominant at bus
speeds — and why your I2C rise-time problem is a capacitance problem.

---

## §5 — Ordinary differential equations

**Time:** 8–10 weeks.
**Unlocks:** transient analysis, system dynamics, all of control theory.

**The idea:** an ODE relates a function to its own derivatives. Circuits
and mechanical systems produce them automatically, because capacitors,
inductors, masses and springs are all defined by derivative
relationships. Solving the ODE tells you what the system *does over
time*.

**The two you must be able to solve cold:**

**First order:** `τ·dy/dt + y = K·u`
Solution: exponential approach to the final value with time constant τ.
This is an RC circuit, an RL circuit, a thermal system, and a motor's
electrical dynamics — all the same equation.

**Second order:** `d²y/dt² + 2ζω_n·dy/dt + ω_n²·y = ω_n²·u`
Solution depends entirely on the damping ratio ζ:

| ζ | Behaviour | Name |
|---|---|---|
| `ζ = 0` | oscillates forever | undamped |
| `0 < ζ < 1` | overshoots, rings, settles | underdamped |
| `ζ = 1` | fastest approach with no overshoot | critically damped |
| `ζ > 1` | slow, no overshoot | overdamped |

This one equation describes an RLC circuit, a mass-spring-damper, a
suspension, a servo loop, and a PID-controlled motor. **Learning to read
ζ and ω_n off a system is one of the most transferable skills in all of
engineering.** When you get to control theory, essentially the whole
subject is "place the poles so ζ and ω_n are what you want."

**What to learn:** separable equations, first-order linear equations with
integrating factors, second-order linear constant-coefficient equations
(characteristic equation, the three damping cases), and forced response
with step and sinusoidal inputs. You can skip series solutions and
most of the exotic methods; engineering uses Laplace instead.

**Do this:** derive the RC step response `v(t) = V(1 − e^(−t/RC))` from
`i = C·dv/dt` and KVL, on paper, without looking it up. Then do the same
for an RL circuit. When you can do both from scratch you understand
first-order systems, which is most of what you'll ever need.

**Resource:** Paul's Online Math Notes (Differential Equations), or MIT
OCW 18.03. MIT's is harder and better.

---

## §6 — Laplace transform

**Time:** 3–4 weeks (it's a technique, not a subject).
**Unlocks:** transfer functions, and therefore control theory.

**The idea:** the Laplace transform converts a function of time into a
function of a complex variable `s`, and — this is the whole point — it
converts **differentiation into multiplication**:

```
L{ df/dt } = s·F(s) − f(0)
```

So a differential equation becomes an algebraic equation. You solve the
algebra, then transform back. Engineers use this constantly and rarely
compute a transform from the integral definition; you use a table.

**The table you actually need is about eight lines long:**

| `f(t)` | `F(s)` |
|---|---|
| `δ(t)` (impulse) | `1` |
| `1` (unit step) | `1/s` |
| `t` | `1/s²` |
| `e^(−at)` | `1/(s+a)` |
| `sin ωt` | `ω/(s² + ω²)` |
| `cos ωt` | `s/(s² + ω²)` |
| `e^(−at)·sin ωt` | `ω/((s+a)² + ω²)` |
| `df/dt` | `sF(s) − f(0)` |

**The payoff — transfer functions.** For a linear system, define
`H(s) = Y(s)/X(s)`, output over input in the `s` domain. `H(s)` captures
the *entire* behaviour of the system in one algebraic expression. Its
denominator's roots are the **poles**, and the poles tell you everything
about stability and speed:

- Pole at `s = −a` (real, negative) → mode `e^(−at)`, decays, stable.
  Time constant `1/a`.
- Pole at `s = +a` (real, positive) → mode `e^(+at)`, **blows up**.
- Complex pair `s = −σ ± jω` → `e^(−σt)·cos(ωt)`, damped oscillation.
  Real part sets decay, imaginary part sets ringing frequency.

**The rule that the whole of stability theory reduces to: all poles in
the left half of the complex plane = stable.** Everything in Module 05 is
an elaboration of that sentence.

**What to learn:** the transform table, partial fraction expansion (the
main mechanical skill — practice it until it's boring), the initial and
final value theorems, and inverse transforms.

---

## §7 — Fourier series and transforms

**Time:** 4–5 weeks. Do alongside or just after Laplace.
**Unlocks:** frequency response, filters, DSP, spectra.

**The idea:** any periodic signal can be written as a sum of sinusoids at
integer multiples of its fundamental frequency (Fourier series). Any
signal at all, periodic or not, can be written as a continuous
superposition of sinusoids (Fourier transform).

**The question everyone asks and few get answered: why sinusoids?** Not
because they're pretty. Because sinusoids (really, complex exponentials
`e^(jωt)`) are the **eigenfunctions of linear time-invariant systems**.
Put a sinusoid into any LTI system and you get out *the same frequency*,
only scaled and phase-shifted. No other family of functions does this.
That property is what makes frequency-domain analysis work at all, and
it is the deepest single idea in Module 04.

**Concretely, for you:** your PWM signal at 490 Hz is not a "1.74 V
signal." It's a square-ish wave whose Fourier series is a 490 Hz
fundamental plus odd harmonics at 1470 Hz, 2450 Hz, and so on. The motor
responds to the DC term and ignores the rest — because the motor is a
low-pass filter with a corner frequency far below 490 Hz. That's why PWM
works. It's a frequency-domain argument, and once you see it you can
answer questions like "would 100 Hz PWM still work?" (partly — you'd
start to feel the pulsing) instead of guessing.

**What to learn:** Fourier series (trig and exponential forms), the
Fourier transform and its properties (linearity, time shift, convolution
theorem), the spectrum of common signals, and the relationship between
Fourier and Laplace (Fourier is Laplace evaluated on the `jω` axis).

---

## §8 — Linear algebra

**Time:** 6–8 weeks.
**Unlocks:** state-space control, robotics kinematics, sensor fusion,
and every numerical method you'll ever use.

**The idea:** a matrix is a linear transformation. Everything else is
consequence.

**Why an engineer cares:**

- **State space** — modern control represents a system as
  `ẋ = Ax + Bu`, `y = Cx + Du`. This handles many coupled variables at
  once, where transfer functions handle only one input and one output.
  The **eigenvalues of `A` are exactly the poles** of the transfer
  function; the two views are the same physics.
- **Robot kinematics** — rotations and translations are matrices, and
  chaining joints is matrix multiplication.
- **Sensor fusion** — the Kalman filter is linear algebra plus
  probability, and nothing else.
- **Least squares** — fitting a calibration curve to your ToF sensor's
  readings is `x = (AᵀA)⁻¹Aᵀb`.

**What to learn:** vectors and vector spaces, matrix multiplication as
composition of transformations, determinants, inverses, rank, solving
`Ax = b`, eigenvalues and eigenvectors (the important part), and
diagonalisation.

**Resource:** MIT OCW 18.06 with Gilbert Strang's lectures — widely
considered the best linear algebra course ever recorded, and free. Watch
3Blue1Brown's *Essence of Linear Algebra* first, in one sitting, for the
geometric picture. Then do Strang for the mechanics.

---

## §9 — Probability and statistics

**Time:** 4–5 weeks. Can come last.
**Unlocks:** noise analysis, estimation, Kalman filtering, tolerances.

**Why an engineer cares:** because every measurement is wrong, and the
question is only *how* wrong and what you can do about it.

**What to learn:** random variables, mean and variance, the Gaussian
distribution, the central limit theorem, covariance, and Bayes' rule.

**The result you will use most:** averaging `N` independent measurements
reduces the standard deviation of the noise by `√N`. Ten samples cut your
noise by 3.16×, not 10×. This is why the classic "just average more" fix
gives diminishing returns, and why it costs you response time — a
tradeoff you will meet directly when you filter your ToF readings.

**Bayes' rule is the seed of the Kalman filter:** combine a prediction
(from a model) with a measurement (from a noisy sensor), weighted by how
much you trust each. That one sentence, made precise, is sensor fusion.

---

## Pacing this alongside the engineering modules

Do not do all the math first. Interleave it — you need the motivation
that comes from immediately using each tool:

| Months | Math | Run alongside |
|---|---|---|
| 1–2 | §1 algebra/trig | Module 01 DC, Module 03 logic |
| 2–4 | §2 derivatives | Module 01 transients, Module 02 diodes/BJTs |
| 4–6 | §3 integrals, §4 complex | Module 01 AC, Module 02 op-amps |
| 6–9 | §5 ODEs | Module 06 dynamics, Module 02 filters |
| 9–12 | §6 Laplace, §7 Fourier | Module 04 signals & systems |
| 12–15 | §8 linear algebra | Module 05 control theory |
| 15–18 | §9 probability | Module 06 estimation, Kalman |
