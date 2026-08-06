# Module 04 — Signals and systems

**Prereqs:** derivatives (§2), integrals (§3), complex numbers (§4),
ODEs (§5). Laplace (§6) and Fourier (§7) are developed alongside.
**Time:** ~12 weeks.
**Unlocks:** control theory, DSP, communications, filtering — and a way
of thinking that applies to every field on this list.

---

## Why this matters for your wristband

Your device samples a distance every 50 ms and turns it into a motor
command. That single sentence contains a sampling rate, a Nyquist limit,
a noise problem, and a latency-versus-smoothness tradeoff — four things
this module makes precise.

Right now, if your ToF readings come back jumpy, your options are "try a
moving average" and "try changing the sensor preset." By the end of this
module you will be able to compute how much smoothing you can afford
before the lag makes the device *less* safe, which is a question your
project genuinely needs answered and cannot answer today.

---

## 4.1 The two properties that make everything work

A system is **linear** if scaling the input scales the output, and if
the response to a sum of inputs is the sum of the responses
(superposition). It is **time-invariant** if delaying the input just
delays the output, unchanged.

A system with both properties is **LTI**, and LTI systems have a
property so useful that essentially all of engineering analysis is built
on it:

**An LTI system is completely characterised by its response to a single
impulse.**

Know the impulse response `h(t)` and you know the output for *any*
input, via convolution:

```
y(t) = ∫ x(τ)·h(t − τ) dτ        written  y = x * h
```

Take that in. One measurement — kick the system and record what it does —
tells you everything it will ever do. That is a remarkable claim and it
is exactly true for LTI systems.

**Why we care so much about linearity:** almost nothing in the real world
is truly linear. A motor saturates. An op-amp clips. A transistor is
exponential. But over a limited operating range they're close enough,
and the payoff for treating them as linear is this entire toolkit. When
you linearise a plant model in Module 05, this is the payoff you're
buying.

## 4.2 Convolution — building the intuition

The integral above looks opaque until you see what it does: flip `h`,
slide it across `x`, and at every position compute the overlap area.

**The intuition that makes it click:** decompose the input into a train
of scaled impulses. Each one produces a scaled, delayed copy of `h`.
Sum them all. That sum *is* the convolution. Convolution isn't a
formula, it's bookkeeping for superposition.

Do it in discrete time first — it's just a weighted sum, and you can
compute one by hand in five minutes:

```
y[n] = Σ x[k]·h[n − k]
```

Then the continuous version stops being frightening.

## 4.3 Why sinusoids, and the eigenfunction property

Here is the fact that organises the whole subject:

**Feed a complex exponential `e^(jωt)` into any LTI system and the output
is the same complex exponential, only scaled by a complex constant.**

```
input e^(jωt)  →  output H(jω)·e^(jωt)
```

The frequency doesn't change. The shape doesn't change. Only the
amplitude and phase, both packaged into the single complex number
`H(jω)`.

No other family of signals does this. This is *why* engineers decompose
everything into sinusoids: because sinusoids pass through LTI systems
without changing identity, so if you know what the system does to each
frequency, you know what it does to any signal built from them.

Everything downstream — Fourier analysis, Bode plots, filter design,
frequency-domain control — is a consequence of this one property.

## 4.4 Fourier: the frequency domain

- **Fourier series** — any periodic signal is a sum of sinusoids at
  integer multiples of the fundamental.
- **Fourier transform** — any signal at all is a continuous
  superposition of sinusoids.
- **The magnitude spectrum** is what's usually plotted; the **phase
  spectrum** is what's usually ignored and often matters more.

**Properties worth memorising, because they do real work:**

| Property | Meaning |
|---|---|
| Linearity | transform of a sum is the sum of transforms |
| Time shift | delay ⇒ phase ramp, magnitude unchanged |
| **Convolution theorem** | convolution in time = **multiplication** in frequency |
| Duality | narrow in time ⇔ wide in frequency, and vice versa |

The convolution theorem is the reason the frequency domain is worth the
trouble: it converts the hardest operation in the time domain into
ordinary multiplication.

**Duality, made concrete for you:** a short pulse has a wide spectrum.
Your PWM signal has fast edges, and fast edges mean high-frequency
content, and high-frequency content is what radiates and couples into
neighbouring wires. This is why switching circuits cause interference
and why slowing an edge deliberately is a real EMI technique.

## 4.5 Laplace and transfer functions

Fourier handles steady-state sinusoids. Laplace generalises to include
growth and decay, and handles initial conditions — which is what you
need for transients and stability.

```
H(s) = Y(s) / X(s)
```

- The roots of the numerator are **zeros**.
- The roots of the denominator are **poles**.
- **Poles are the system's natural modes.** Each pole contributes a term
  to the time response:

| Pole location | Time-domain contribution |
|---|---|
| `s = −a` (real, LHP) | `e^(−at)` — decays, τ = 1/a |
| `s = +a` (real, RHP) | `e^(+at)` — **unstable** |
| `s = −σ ± jω` | `e^(−σt)·cos(ωt)` — damped oscillation |
| `s = ±jω` (on axis) | pure oscillation, marginally stable |

**Stability rule: all poles strictly in the left half plane.** That
sentence is the foundation of Module 05.

And the link back: `H(jω)`, the frequency response, is just `H(s)`
evaluated on the imaginary axis. Fourier is Laplace restricted to
`s = jω`. Two tools, one object.

## 4.6 Frequency response and Bode plots

A Bode plot is `|H(jω)|` in decibels and `∠H(jω)` in degrees, both
against log frequency. Log-log axes turn multiplication into addition,
so a complicated transfer function becomes a sum of simple straight-line
pieces you can sketch by hand.

**The asymptotic rules, which are all you need to sketch anything:**

- Each **pole**: magnitude breaks downward at the corner frequency,
  −20 dB/decade after it. Phase goes from 0° to −90°, passing −45° at
  the corner.
- Each **zero**: the mirror image. +20 dB/decade, phase 0° to +90°.
- Corner frequency for a pole at `s = −a` is `ω = a`.

Learn to sketch these by hand before you let a computer draw them. The
hand sketch is what builds the instinct that lets you look at a plot and
immediately say "that's a two-pole rolloff with a resonance."

## 4.7 Sampling and the Nyquist theorem

The bridge between continuous and digital, and the most practically
consequential result in the module.

**Nyquist–Shannon:** to reconstruct a signal exactly, you must sample at
more than **twice** its highest frequency component.

```
f_s > 2·f_max
```

Sample too slowly and high-frequency content **aliases**: it folds down
and appears as a lower frequency, indistinguishable from a real signal
at that frequency. Aliasing is **not recoverable after the fact**. Once
sampled, the information is gone.

**Which is why anti-alias filtering happens before the ADC, in analog.**
This is the single most common design error in beginner data acquisition:
sampling a signal without first band-limiting it, then trying to filter
the mess digitally. It cannot work.

### Your sensor's numbers

`kSensorPeriodMs = 50` means you sample at **20 Hz**, so your Nyquist
limit is **10 Hz**. Any real change in obstacle distance faster than
10 Hz is aliased.

Is that enough? Walking is roughly 1.4 m/s, and your wrist moves faster
than your body — arm swing is on the order of 1 Hz with harmonics.
20 Hz sampling is defensible, but it's a *decision*, and you can now
state its consequence: **you have 50 ms of quantisation on top of the
sensor's own measurement time, and a distance change happening in less
than 100 ms is not reliably represented.** At 1.4 m/s, 50 ms is 70 mm of
travel. Your Critical zone is only 240 mm wide. Those numbers are in the
same ballpark, and that is worth knowing.

## 4.8 Filters

**Passive:** the RC low-pass from Module 01 §1.8. First order,
−20 dB/decade, corner at `1/(2πRC)`. Cheap, always stable, limited.

**Active:** op-amps let you build higher-order filters with gain and no
inductors. Sallen-Key is the standard second-order building block.

**Filter families**, all tradeoffs against each other:

| Family | Gets you | Costs you |
|---|---|---|
| Butterworth | maximally flat passband | gentle rolloff |
| Chebyshev | steeper rolloff | passband ripple |
| Elliptic | steepest rolloff | ripple in both bands |
| Bessel | linear phase (no shape distortion) | shallowest rolloff |

**Order** sets the rolloff: `−20n dB/decade` for `n` poles.

**The universal filter tradeoff, which you should carry everywhere:**
sharper frequency selectivity ⇒ longer time-domain response ⇒ more
delay. You cannot escape it. It's the duality property of §4.4 wearing
different clothes. Every time someone asks for a filter that removes
noise without adding lag, this is the answer.

## 4.9 Digital filters — and a concrete improvement to your firmware

**FIR** (finite impulse response): output is a weighted sum of past
inputs. Always stable, can have exactly linear phase, needs more taps.

**IIR** (infinite impulse response): output feeds back. Far cheaper for a
given sharpness, can be unstable, nonlinear phase.

### The moving average

```
y[n] = (1/N)·Σ x[n−k]     for k = 0..N−1
```

- Reduces uncorrelated noise by `√N` (from §9 of the math backbone).
- Costs `(N−1)/2` samples of **lag**.
- Needs `N` samples of storage — a real cost on a 2 KB MCU.

### The exponential moving average (EMA)

```
y[n] = α·x[n] + (1−α)·y[n−1]
```

One multiply, one add, **one variable of state**. This is the workhorse
of embedded filtering, and it's a first-order IIR low-pass — the digital
twin of your RC circuit.

Its equivalent time constant, given sample period `T`:

```
τ = −T / ln(1−α)
```

### Working the tradeoff for your device — do this calculation

At `T = 50 ms`:

| α | τ | Corner freq | Lag at 1.4 m/s walking |
|---|---|---|---|
| 0.1 | 475 ms | 0.34 Hz | **665 mm** |
| 0.2 | 224 ms | 0.71 Hz | **314 mm** |
| 0.5 | 72 ms | 2.2 Hz | 101 mm |
| 0.8 | 31 ms | 5.1 Hz | 44 mm |

Now look at that table next to your zone thresholds — Critical is
10–249 mm, Near is 250–599 mm.

**A "gentle" α = 0.2 smoothing introduces 314 mm of positional lag,
which is wider than your entire Critical zone.** The device would report
"Near" while the wearer is already inside Critical. On a device for
someone who cannot see the obstacle, that is not a cosmetic issue.

**This is the whole point of the module.** "Add a bit of smoothing"
sounds harmless and is, on this device, potentially unsafe — and you can
only see that by putting a number on the lag.

### What to do instead

Your ToF sensor's actual noise problem is not Gaussian jitter, it's
**occasional single-sample garbage** — a stray reflection, an ambient-IR
hit, a timeout. That's an outlier problem, and outliers are exactly what
a linear filter handles worst: averaging one bogus 8000 mm reading into
your output corrupts it for several samples.

A **median-of-3 filter** kills single-sample outliers completely, is
nonlinear (so none of the LTI theory above applies to it — which is why
it can beat the tradeoff), costs one sample of lag (**50 ms, 70 mm at
walking speed**), and needs three variables.

**Recommended concrete change to `HapticMapper`:** median-of-3 for
outlier rejection, plus a light EMA (α ≥ 0.5) only if jitter is still
visible after that. Extend `test_haptic_mapper.cpp` with a single-spike
input case to prove the median rejects it. This is a real, small,
theory-derived improvement to your project — the best possible exercise
for this module.

## 4.10 The z-transform

The discrete-time counterpart of Laplace. `z = e^(sT)`.

- The stability region maps from "left half plane" to **"inside the unit
  circle."**
- Difference equations become algebra, exactly as ODEs did under
  Laplace.
- Digital filter design happens here.

You need this for digital control (Module 05) and any serious DSP.

---

## Do this — labs for Module 04

Python with NumPy, SciPy and Matplotlib. All free, and this is exactly
what the tools are for.

1. **Build a square wave from sinusoids.** Add the fundamental, then the
   3rd harmonic, 5th, 7th… Watch it converge, and watch the overshoot at
   the edges refuse to shrink. That overshoot is the **Gibbs
   phenomenon**, it's real, and seeing it beats reading about it.
2. **Convolve by hand, then verify.** Compute a 4-sample convolution on
   paper, then check with `numpy.convolve`.
3. **Alias something on purpose.** Sample a 90 Hz sine at 100 Hz. Plot
   it. Watch a 90 Hz signal appear as 10 Hz. Then try to remove the
   10 Hz artefact by filtering, and confirm you can't.
4. **Bode by hand, then by computer.** Sketch the Bode plot of
   `H(s) = 1/(s+10)` on paper. Then plot it with `scipy.signal.bode`.
   Compare. Repeat until your sketches are close.
5. **Filter your own sensor data.** Log 60 seconds of real ToF readings
   over serial with `DEBUG_SERIAL 1`. Save them. In Python, apply a
   moving average, an EMA at several α, and a median-of-3. **Plot each
   against the raw data on the same axes and measure the lag of each
   directly.** Then implement the winner in `HapticMapper.h` with tests.
   This lab uses hardware you own, data you generated, and produces a
   commit. Do it.

---

## Self-check — closed book

1. Define linearity and time-invariance, and give one real component
   that violates each.
2. Why does knowing the impulse response tell you everything about an
   LTI system?
3. What is special about `e^(jωt)` with respect to LTI systems?
4. State the convolution theorem and say why it's useful.
5. A pole at `s = −2 ± j5`. Describe the time response in words.
6. Sketch the Bode magnitude of `H(s) = 100/((s+1)(s+100))`. What's the
   DC gain in dB? What's the slope past 100 rad/s?
7. You sample at 20 Hz. A 15 Hz component is present. What frequency
   does it appear at, and can you filter it out afterwards?
8. Why must an anti-alias filter be analog?
9. Give the EMA equation and its equivalent time constant.
10. Why does a median filter reject outliers when an averaging filter
    cannot, and why doesn't LTI theory cover it?
11. State the universal tradeoff between filter sharpness and delay,
    and explain why it's unavoidable.

---

## Resources for this module

- **Oppenheim & Willsky, *Signals and Systems*** — the standard text.
  **MIT OCW 6.003** has Oppenheim's own recorded lectures, free.
- **Smith, *The Scientist and Engineer's Guide to DSP*** (dspguide.com) —
  free, complete, and the most practical DSP book written. Read it
  alongside the theory.
- **Lathi, *Signal Processing and Linear Systems*** — a friendlier
  alternative to Oppenheim if you find that one dry.
- **3Blue1Brown's Fourier transform video** — the best available
  intuition for what the transform *is*. Watch before studying, not
  instead of.
- **Python: NumPy / SciPy / Matplotlib** — `scipy.signal` has everything.
  This is the lab bench for this entire module.
