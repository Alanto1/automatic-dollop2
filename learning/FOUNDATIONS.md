# Foundations — the ground floor

**This is the layer beneath everything else in `learning/`.** Physics,
math, trigonometry, a little chemistry, and calculus — the general
science background that the six engineering modules assume you already
have.

**Time:** ~9–12 months at 8 h/week for all of it. See "The fast path"
below if you don't want to wait that long to touch a circuit — you
don't have to, and you shouldn't.

---

## How this relates to the rest of the plan

There's deliberate overlap, so here's the map:

| File | What it is |
|---|---|
| **This file** | The ground floor. General science, taught as science. Covers physics and chemistry, which nothing else here does. |
| `00-math-backbone.md` | The *same math*, re-sequenced by what it unlocks in electrical engineering — plus the advanced math this file never reaches (Laplace, Fourier, linear algebra, probability). |
| `01`–`06` | The engineering modules proper. |

**If you're starting from scratch:** work through this file. Then
`00-math-backbone.md` §1–§3 becomes review you can move through quickly,
and §4 onward (complex numbers, ODEs, Laplace, Fourier, linear algebra,
probability) is genuinely new.

**One thing not to do twice:** Physics 2's circuits chapter *is*
Module 01 Part A. Same content, same equations. Do Module 01 — it's
better targeted and it's tied to hardware you own.

---

## The order — and why it isn't the order you listed

You asked for physics, math, trig, chemistry, calculus. The teaching
order has to be different, because of what depends on what:

```
  1. MATH CORE ─────┬──► 2. TRIGONOMETRY ──┐
                    │                       │
                    │                       ▼
                    │              3. PHYSICS I — mechanics
                    │                       │
                    └──► 5. CALCULUS ◄──────┘
                              │
                              ▼
                    6. PHYSICS II — electricity & magnetism

  4. CHEMISTRY (tiny) — standalone, drop it in anywhere
```

**Two things worth noticing.**

**Physics splits in two.** Mechanics needs only algebra, trig and
vectors, so you can do it early. Electricity and magnetism needs
calculus to be worth doing — Faraday's law is a derivative, capacitance
is a derivative, and the algebra-only version of E&M is a collection of
memorised formulas that explain nothing. So mechanics goes before
calculus and E&M goes after.

**Chemistry is genuinely tiny** and depends on nothing. One to two
weeks, not a course. §4 says exactly what to take and what to leave.

---

# 1 — Math core

**Time:** 6–8 weeks · **Prereqs:** none

Algebra fluency. Not "having seen it" — fluency, meaning you do it
without stopping to think. Everything downstream is bottlenecked here,
and this is the single most common place self-taught engineers have a
quiet hole they keep falling into.

### What to cover

- **Rearranging equations.** The number one skill. Including when the
  unknown is in a denominator, or on both sides.
- **Fractions and ratios.** Unglamorous and genuinely the most common
  stumbling block in engineering algebra. Parallel resistors are a
  reciprocal sum; get sloppy here and every parallel combination is a
  coin flip.
- **Exponents and scientific notation.** You already use this daily in
  nF, kΩ, mA — formalise it.
- **Logarithms.** `log`, `ln`, and the laws. Non-negotiable: decibels,
  Bode plots and RC decay all live here.
- **Linear equations and graphing.** Slope, intercept, and reading a
  straight line off a graph.
- **Systems of equations.** 2×2 and 3×3 by substitution and
  elimination. Circuit analysis generates these constantly.
- **Quadratics.** Factoring, completing the square, the quadratic
  formula. Finding poles is solving quadratics.
- **Rational expressions.** Adding, simplifying, and finding common
  denominators. This is what partial fractions will be built on.
- **Functions and notation.** `f(x)`, domain, range, composition,
  inverses.

### The topic nobody teaches as a topic — units and dimensional analysis

**Treat this as its own week.** It is the most useful single habit in
all of engineering and almost no course teaches it explicitly.

The rule: **every equation must balance dimensionally.** If the left
side is in amps, the right side is in amps. Check this on every formula
you write, always, and you will catch a large fraction of your own
errors before they cost you anything.

Worked on your own hardware — the TP4056 relation:

```
I_BAT = 1200 × (V_PROG / R_PROG)

volts / ohms = amps  ✓   and 1200 is a dimensionless multiplier
so the right side is amps, matching the left. The equation is sane.
```

Now do it the other way. If someone hands you `τ = RC`, check it:
ohms × farads. An ohm is V/A, a farad is C/V, a coulomb is A·s. So
`(V/A)·(A·s/V) = s`. **Seconds.** The RC time constant is a *time*, and
you just proved it from the units rather than taking it on trust.

Learn the SI prefixes cold: p, n, µ, m, k, M, G.

### Do this

1. Rearrange `I = 1200·V/R` to solve for `R`, then compute the resistor
   for 0.5C charging of your 250 mAh cell. You should get 9.6 kΩ.
2. **Convert your battery three ways.** 250 mAh → coulombs → joules.
   (`0.25 A × 3600 s = 900 C`; `900 C × 3.7 V = 3330 J`.) Then convert
   to watt-hours and check it against the cell's own marking —
   `3.7 × 0.25 = 0.925 Wh`, and the label says `0.925Wh`. **The
   marking on your battery is a units conversion you can now do
   yourself.**
3. Dimensionally check five formulas from `01-circuits.md`. Find the
   one that surprises you.

### Resources

Khan Academy **Algebra 1** → **Algebra 2** (see the earlier
unit-by-unit triage). Paul's Online Math Notes has an Algebra section
for reference.

---

# 2 — Trigonometry

**Time:** 3–4 weeks · **Prereqs:** §1

The part most people learn as triangle geometry, when the part
engineering needs is **oscillation**.

### What to cover

- **Right-triangle trig.** SOH-CAH-TOA. You probably have this.
- **The unit circle.** Sine and cosine as coordinates of a point going
  around a circle. This is the mental model that makes everything else
  work — not triangles.
- **Radians.** `2π` radians in a full turn. Learn to *think* in radians,
  not to convert into them. `ω = 2πf` is in rad/s and appears in
  literally every AC formula you will ever write.
- **Sinusoids as functions of time.** `v(t) = A·sin(2πft + φ)` — three
  numbers: amplitude, frequency, phase. **This is the single most
  important object in electrical engineering.**
- **The Pythagorean identity** `sin²θ + cos²θ = 1`, and angle-sum
  formulas (lightly).
- **Inverse trig** — `arctan` especially, because that's how you get a
  phase angle out of a complex number later.
- **Law of sines and cosines** — lightly, for non-right-triangle force
  problems.
- **Polar vs rectangular coordinates.** `(x, y)` ↔ `(r, θ)`. Do this
  properly, because it is *exactly* the same conversion you'll do on
  complex numbers, and getting it here means complex numbers cost you
  half as much later.

### The one fact to carry forward

**Adding two sinusoids of the same frequency always gives another
sinusoid of that same frequency**, with a different amplitude and
phase. Nothing new is created. That single property is why AC circuit
analysis is possible at all.

### Do this

1. In **Desmos**, plot `y = A·sin(2πf·x + φ)` with sliders on all three.
   Spend twenty minutes changing each one and watching. This builds more
   intuition than a chapter of reading.
2. Add two sine waves of the same frequency but different phase in
   Desmos. Confirm the sum is still a sine wave of that frequency.
3. Then add two of *different* frequencies and watch it stop being a
   sine wave. You've just seen why the same-frequency rule matters.
4. Your PWM runs at 490 Hz. Give its period in ms, its angular frequency
   in rad/s, and how many radians elapse during one 120 ms haptic pulse.

### Resources

Khan Academy **Trigonometry** course, or Algebra 2 Unit 11 plus the
Precalculus trig units. **Desmos** for every plot.

---

# 3 — Physics I: mechanics

**Time:** 8–10 weeks · **Prereqs:** §1, §2

Where math becomes physical. Also where you learn the habit that
carries into every engineering discipline: draw the diagram before you
write the equation.

### What to cover

- **Units and measurement.** SI base units, dimensional analysis again
  (it matters that much), significant figures, estimation.
- **Vectors.** Components, addition, magnitude and direction, the dot
  product. The bridge from trig to physics.
- **Kinematics.** Position, velocity, acceleration. The equations of
  motion for constant acceleration. Projectile motion.
- **Newton's three laws.** `F = ma` and what the other two actually say.
- **Forces.** Gravity, normal force, friction (static vs kinetic),
  tension, and the spring force `F = −kx`.
- **Free-body diagrams.** *A discipline, not a technique.* Isolate the
  body, draw every force on it, then solve. Eighty percent of getting
  mechanics right is drawing these properly, and it transfers directly
  to `06-mechanics-motors-sensors.md` §6.1.
- **Work, energy, power.** Kinetic and potential energy, conservation of
  energy, `P = dE/dt`.
- **Momentum** and collisions.
- **Rotation.** Angular position/velocity/acceleration, torque
  `τ = F × d`, moment of inertia, `τ = Jα`. Everything linear has a
  rotational twin.
- **Simple harmonic motion.** Mass on a spring: `ω = √(k/m)`. Pendulum:
  `T = 2π√(L/g)`. Damping and resonance.

### Why simple harmonic motion is the punchline

SHM is the bridge to the entire rest of the plan. The mass-spring-damper
equation

```
m·ẍ + c·ẋ + k·x = F
```

is **the same equation** as an RLC circuit (`01-circuits.md` §1.10) and
as the generic second-order system that all of control theory is built
on (`05-control-theory.md` §5.3). Mass ↔ inductance, damping ↔
resistance, spring ↔ 1/capacitance.

Learn SHM properly here and you have pre-learned a third of control
theory without knowing it.

### Do this

1. **Free-body diagram of your own device.** The wristband pod, held
   against a wrist by a strap under tension. Draw every force. Write the
   equilibrium equations. This is `06 §6.1` done a year early.
2. **Measure `g`.** Drop something, time it with your phone's slow-motion
   camera, compute `g` from `d = ½gt²`. Compare to 9.81. Then work out
   how far off your timing had to be to explain your error — that's
   error analysis, and it's a real skill.
3. **Pendulum.** String, weight, ruler. Measure the period for three
   lengths, plot `T²` against `L`, and confirm it's a straight line with
   slope `4π²/g`. You've just measured `g` a second, better way.
4. **Energy budget for your device.** Your cell holds 3330 J. At the
   average current you measured in Module 02's lab, how many hours does
   that give? Compare to your observed runtime.
5. **PhET simulations** — Forces and Motion, Energy Skate Park, Masses
   and Springs. Free, and excellent for the concepts that are hard to
   picture.

### Resources

- **OpenStax College Physics 2e** — free, peer-reviewed, complete, with
  problem sets. https://openstax.org/details/books/college-physics-2e
  (Use **University Physics Volume 1** instead if you want the
  calculus-based version and have done §5.)
- **Khan Academy Physics** — https://www.khanacademy.org/science/physics
- **PhET** — https://phet.colorado.edu/en/simulations/filter?subjects=physics
- **Michel van Biezen** on YouTube — an enormous library of worked
  problems, which is exactly what's missing from most video courses.

---

# 4 — Chemistry (the tiny bit)

**Time:** 1–2 weeks · **Prereqs:** none

Be honest about the scope here: electrical engineering needs a very
small, very specific slice of chemistry. Taking a full chemistry course
for this would waste two months.

### Take this

- **Atomic structure.** Protons, neutrons, electrons. Nucleus and shells.
- **Valence electrons.** The outermost shell. **This is the one concept
  that matters**, because electrical conduction is entirely a story
  about what the valence electrons are doing.
- **The periodic table's structure.** Groups, and why a group number
  tells you the valence count. Specifically:
  - **Group 14** — silicon, germanium. Four valence electrons, all
    committed to bonds. That's a semiconductor.
  - **Group 15** — phosphorus. Five valence electrons. Doping silicon
    with it leaves a spare → **n-type**.
  - **Group 13** — boron. Three. Doping leaves a hole → **p-type**.
- **Bonding.** Ionic vs covalent, and metallic bonding — where the
  "sea of electrons" is exactly why metals conduct.
- **Conductors, insulators, semiconductors**, explained by what the
  valence electrons can do.
- **Oxidation and reduction.** Electrons moving between species. This
  is how every battery works: a chemical reaction that pushes electrons
  around an external circuit.
- **Lithium, specifically.** Group 1, one valence electron it gives up
  readily — which is why lithium chemistry has the energy density it
  does, and equally why it is the most hazardous common cell chemistry.

### Leave this

Moles and stoichiometry, gas laws, acid–base chemistry, thermodynamics
of reactions, organic chemistry. All real chemistry, none of it in your
path. **You will never use Avogadro's number in circuit analysis.**

### Do this

1. Draw a silicon atom's valence shell. Then draw it doped with
   phosphorus, and again with boron. Mark the spare electron and the
   hole. You've just drawn the physical basis of every transistor you
   will ever use — and `02-electronics-analog.md` §2.1 will read like
   review.
2. Trace what happens in your 502030 lithium cell while charging:
   which electrode gains electrons, which loses them, which way the
   lithium ions move. Then read `02 §2.6`'s explanation of why 4C
   charging causes lithium *plating* — it'll make mechanistic sense
   instead of being a rule you follow.

### Resources

**Khan Academy Chemistry** — https://www.khanacademy.org/science/chemistry
— take only the atomic structure and periodic table units. **OpenStax
Chemistry 2e** — https://openstax.org/details/books/chemistry-2e — for
reference, chapters 2, 6 and 7 only.

---

# 5 — Calculus

**Time:** 12–16 weeks · **Prereqs:** §1, §2

The biggest single item here, and the one that unlocks the most.

### Why an engineer needs it, in one line

Because two of the five basic circuit components are *defined* by
derivatives:

```
Capacitor:   i = C · dv/dt
Inductor:    v = L · di/dt
```

Without calculus those are symbols. With it they're statements you can
reason from — and they explain why a capacitor blocks DC, why your
motor needs a flyback diode, and why an RC circuit settles the way it
does.

### What to cover

**Derivatives (6–8 weeks)**
- Limits — conceptually. You do not need epsilon-delta rigour.
- The derivative as a rate of change and as the slope of a tangent.
- Power rule, product rule, quotient rule, **chain rule**.
- Derivatives of `eˣ`, `ln x`, `sin x`, `cos x`.
- Maxima and minima — how you find a maximum-power operating point.
- Related rates (lightly).

**Integrals (6–8 weeks)**
- The integral as accumulation, and as area under a curve.
- **The Fundamental Theorem of Calculus** — that differentiation and
  integration are inverses. This is the punchline of the whole subject.
- Integration by substitution, and by parts.
- Definite integrals and evaluating them.
- Applications: average value, RMS, total accumulated charge.

**A first look at differential equations (2 weeks)**
- Separable first-order equations.
- Enough to derive `v(t) = V(1 − e^(−t/RC))` from `i = C·dv/dt` and KVL
  yourself. When you can do that from scratch, first-order systems are
  yours.

### Do this

1. **Differentiate your own data.** Take the ToF log from
   `04-signals-and-systems.md`'s lab. Compute the numerical derivative
   (differences between consecutive samples divided by 50 ms). You now
   have *closing speed* in m/s. Plot it next to distance. That's a
   derivative doing something useful on data you generated.
2. **Integrate your own data.** Log the motor's on/off state over a
   minute. Integrate current over time to get charge consumed in
   coulombs. Convert to mAh. Compare with the fraction of your
   battery you'd expect to have used.
3. **Derive the RC step response** from scratch — `i = C·dv/dt` plus
   KVL, separate, integrate, apply the initial condition. Don't look it
   up. When you get `V(1 − e^(−t/RC))` on your own paper, you've
   arrived.

### Resources

- **Paul's Online Math Notes**, Calculus I and II —
  https://tutorial.math.lamar.edu/ — complete, free, worked examples.
  The workhorse.
- **3Blue1Brown, *Essence of Calculus*** —
  https://www.3blue1brown.com/topics/calculus — watch *alongside*, never
  instead of. It builds understanding without fluency; you need both.
- **Khan Academy Calculus** for graded practice.
- **MIT OCW 18.01** if you want it harder.

---

# 6 — Physics II: electricity and magnetism

**Time:** 8–10 weeks · **Prereqs:** §3, §5

The physics underneath everything electrical. **Do this after calculus**
— the algebra-only version is a list of formulas that explain nothing.

### What to cover

- **Charge and Coulomb's law.** `F = kq₁q₂/r²`.
- **Electric field and electric potential.** Voltage *is* potential
  difference per unit charge — this is where "voltage is always between
  two points" stops being a rule and becomes obvious.
- **Capacitance.** Why geometry and dielectric set it, and where
  `E = ½CV²` comes from.
- **Current, resistance, resistivity.** Ohm's law from the physics side.
- **DC circuits** — but see the note below.
- **Magnetic fields.** The Lorentz force `F = qv × B`, and the force on
  a current-carrying wire. **This is where motor torque comes from.**
- **Faraday's law of induction.** `EMF = −dΦ/dt`. A changing magnetic
  flux generates a voltage.
- **Lenz's law** — the minus sign. The induced current opposes the
  change that caused it.
- **Inductance**, self and mutual. Transformers.
- **Maxwell's equations** — meet them, appreciate what each says, do not
  try to derive anything. That's a later course.

### The two payoffs

**Faraday plus Lenz is where back-EMF comes from.** A spinning motor is
a generator; the voltage it generates opposes the supply. That's `K_e`
in `06 §6.4`, and it's why a motor has a top speed at all.

**And it's why your flyback diode exists.** Interrupting the current
through an inductor means a large `dΦ/dt`, which by Faraday means a
large induced voltage, which by Lenz points the wrong way for your
transistor. `02 §2.2` states this as a rule; this section is the reason.

### Don't do this twice

**Physics II's DC circuits chapter is `01-circuits.md` Part A.** Same
Ohm's law, same Kirchhoff's laws, same divider. Skim it here and do
Module 01 properly instead — Module 01 is targeted at engineering
practice and tied to hardware you own.

### Do this

1. **Measure back-EMF on your own motor.** Disconnect it from the
   circuit, put a multimeter across its leads on DC volts, and spin the
   shaft by hand — or press it against another spinning motor. **The
   meter reads volts.** That voltage is `K_e·ω`, generated by a motor
   nobody is driving. Nothing makes back-EMF undeniable faster.
2. **Faraday by hand.** Wind 50 turns of wire around a pencil, connect
   a multimeter on its most sensitive DC range, and move a magnet
   through it. Note that the voltage appears only while the magnet is
   *moving*, and reverses when you reverse direction. That's
   `EMF = −dΦ/dt` and Lenz's minus sign, on a bench, for free.
3. **PhET** — Faraday's Law, Generator, Capacitor Lab.

### Resources

- **OpenStax University Physics Volume 2** —
  https://openstax.org/details/books/university-physics-volume-2 — free,
  calculus-based, the right level.
- **Khan Academy Physics**, the electricity and magnetism units.
- **PhET** electromagnetism simulations.

---

## The fast path — don't wait a year to touch a circuit

You do **not** need all of this before starting engineering work, and
waiting would be a mistake. The minimum to begin `01-circuits.md`
Part A productively:

- §1 Math core: rearranging equations, exponents, scientific notation,
  systems of equations, units and dimensional analysis
- §2 Trigonometry: radians, and `A·sin(2πft + φ)`

**That's roughly 6 weeks, not 12 months.** Start Module 01 then, and run
the rest of this file in parallel. You'll reach AC analysis right about
when trig and complex numbers land, which is the correct order and far
more motivating than a year of prerequisites with no payoff.

Sequence that actually works:

| Months | Foundations | Engineering, in parallel |
|---|---|---|
| 1–2 | §1 Math core, §2 Trig | — |
| 2–4 | §3 Physics I, §4 Chemistry | `01` Part A, `03` Part A |
| 4–8 | §5 Calculus | `01` Part B, `02` |
| 8–11 | §6 Physics II | `03` Parts B–C, `06` Part A |
| 11+ | done — move to `00-math-backbone.md` §4 onward | `04`, `05` |

---

## Self-check — are the foundations actually in place?

Closed book. If you can do all of these, you're ready for
`00-math-backbone.md` §4 and the engineering modules proper.

1. Rearrange `P = V²/R` for `V`.
2. Show by units alone that `RC` has dimensions of time.
3. Convert 250 mAh at 3.7 V into joules.
4. Convert 135° into radians without a calculator.
5. A sine wave has period 2 ms. Give `f` in Hz and `ω` in rad/s.
6. Draw a free-body diagram for a block on an incline with friction.
7. State the work-energy theorem.
8. A mass on a spring: what sets its natural frequency, and what does
   adding damping do to the motion?
9. Why does doping silicon with phosphorus make it n-type?
10. Differentiate `3x⁴ − 2eˣ + sin x`.
11. Evaluate `∫₀² 3x² dx`.
12. State the Fundamental Theorem of Calculus in your own words.
13. State Faraday's law and explain what the minus sign is doing.
14. Explain back-EMF and why it gives a DC motor a maximum speed.

---

## Everything here is free

Nothing in this file costs money. OpenStax textbooks are free PDFs and
genuinely peer-reviewed — they are not a budget compromise, they're
what a lot of universities actually assign. Khan Academy is free. PhET
and Desmos are free. Paul's Notes are free.

Link-check: every URL in this file was fetched and returned 200 on
2026-09-12.
