# Lesson 1 — Charge, current, voltage, resistance

**Worked through:** 2026-09-28 → 2026-09-30
**Prereqs:** algebra (rearranging equations), SI prefixes
**Next:** Lesson 2 — Kirchhoff's laws

Everything in circuits is built on the four quantities in the title. This
file has the full theory, a record of the mistakes made the first time
through (the useful part on review), a large graded practice set with
worked answers, and simulations to check every answer against.

---

# PART 1 — THEORY

## 1.1 Charge — what's actually moving

Electric charge comes in a fixed smallest lump, carried by an electron:

```
charge of one electron = −1.602 × 10⁻¹⁹ coulombs
```

The **coulomb (C)** is the unit of charge. Inverting that number, one
coulomb is about **6.24 × 10¹⁸ electrons** — six billion billion. It's a
large unit for a very small thing.

In a metal, the electrons free to move are the loose valence electrons
(`../FOUNDATIONS.md` §4) — the ones metals hold onto weakly. In a
semiconductor they're the doped-in extras. In a battery's electrolyte
the carriers are *ions*, not electrons, which is worth remembering:
"current" doesn't always mean electrons.

## 1.2 Current — the rate of flow

**Current is charge per unit time.**

```
I = Q / t          1 ampere = 1 coulomb per second
```

### Current is the same everywhere in a series loop

The single most important thing in this lesson, and the most common
wrong model.

Current is **not** used up as it goes round. The 90 mA leaving your
battery's + terminal is the same 90 mA arriving at the − terminal.

Think of a **bicycle chain**: push it anywhere and the whole loop moves
at once. Nothing is consumed — the chain goes round. What *is* consumed
is **energy**, which is voltage's job (§1.3).

The rigorous reason: **there is nowhere for charge to accumulate.** A
wire has no storage. Whatever enters a point must leave it. That is
Kirchhoff's Current Law, and it's Lesson 2.

If you catch yourself thinking "the current is weaker after the
resistor" — stop. That's the error.

### The electrons are slow; the signal is fast

A detail that surprises people and clears up a lot of confusion.

In a 1 mm² copper wire carrying 1 A, the average **drift velocity** of
an electron is about **0.07 mm/s**. Slower than a snail. It would take
an electron hours to travel the length of your workbench.

Yet a lamp lights the instant you close the switch. Why? Because the
**electric field** that pushes the electrons propagates through the wire
at a large fraction of the speed of light. The field arrives almost
instantly and *every* electron in the whole wire starts drifting at
once — including the ones already next to the lamp.

The water pipe is the right picture: the pipe is already full. Push at
one end and water comes out the other immediately, even though no
individual molecule travelled the distance.

### Conventional current — a historical annoyance

Benjamin Franklin assumed the moving charges were positive. He was
wrong: in metals it's electrons, which are negative and therefore flow
from − to +.

By the time this was known, every convention was set. So we still draw
**conventional current from + to −**, opposite to the actual electrons.

Does it matter? **No.** Every equation gives the same answer. Use
conventional current like everyone else and just know why the arrows
look backwards.

## 1.3 Voltage — energy per charge

The definition almost nobody is given:

```
V = E / Q          1 volt = 1 joule per coulomb
```

**Voltage is energy per unit charge.** A 3.7 V cell hands **3.7 joules
to every coulomb** that passes through it. That's what a volt *is*.

### Voltage is a difference. Always.

There is no such thing as "the voltage at a point" — only the voltage
**between two points**.

"5 V at that pin" is shorthand for "5 V between that pin and the node we
agreed to call ground." **Ground is a choice**: you pick a reference node
and define it as zero.

Consequences you meet immediately:

- **A bird on a 10 kV line is unharmed.** Both feet touch the same
  conductor, so the potential difference between them is ~0 V. No
  difference, no current. It's the *difference* that is dangerous —
  which is why one hand on the line and one on a pole is lethal.
- **Two circuits with separate grounds cannot exchange signals** until
  their grounds are connected. That's why every wiring diagram in
  `../../assistive-tech-device/README.md` pairs a GND with every
  signal — the GND is what makes the signal voltage *mean* anything.
- **A floating pin has no defined voltage.** Not 0, not 5 — whatever
  stray fields and leakage currents make it. This is the general
  principle behind the GY-53 `PS` pin: an undriven mode-select pin is
  not "off."

### EMF, terminal voltage, and internal resistance

A real battery is not an ideal voltage source. Model it as an ideal
source (its **EMF**) in series with a small **internal resistance**:

```
V_terminal = EMF − I · R_internal
```

This is why your cell reads 3.9 V unloaded and sags when the motor
kicks in. The sag is `I · R_internal`, and it's a real effect on your
build — a plausible cause of brownouts once you run from battery.

## 1.4 Resistance and Ohm's law

**Resistance** is opposition to current flow.

```
R = V / I          1 ohm = 1 volt per amp
```

Rearranged into the form you will write ten thousand times:

```
V = I · R
```

### Ohm's law is not a law of nature

It is the **defining property of a resistor** — an empirical
relationship that holds for resistive materials under normal conditions.

Things that **do not** obey it:

| Component | What it does instead |
|---|---|
| **Diodes, LEDs** | Current is *exponential* in voltage |
| **Transistors** | A third terminal controls the current |
| **Incandescent bulbs** | Filament resistance rises ~10× when hot |
| **Motors** | Generate a back-EMF opposing the supply (§1.7) |
| **Thermistors** | Resistance is the *point* — it varies with temperature |

Treating everything as a resistor is the beginner error that produces
confidently wrong answers. **Ask first: is this thing actually a
resistor?**

### What sets a resistor's value

```
R = ρ · L / A
```

- `ρ` (rho) is **resistivity**, a material property. Copper is
  1.68 × 10⁻⁸ Ω·m.
- `L` is length — **longer means more resistance**.
- `A` is cross-sectional area — **thinner means more resistance**.

Directly useful to you: this is why the motor's hair-thin leads were a
problem, why long jumper wires misbehave, and why high-current wiring is
thick. It's also why a resistor's value is a manufacturing choice about
geometry and material, not magic.

**Temperature:** for metals, resistance *rises* with temperature. For
semiconductors it usually *falls*. That sign difference matters — it's
behind thermal runaway in transistors.

## 1.5 Power

**Power is energy per unit time**, in watts (1 W = 1 J/s).

Let the units derive the formula for you:

```
V is joules per coulomb   [J/C]
I is coulombs per second  [C/s]

V × I → (J/C)(C/s) = J/s = watts  ✓
```

```
P = V · I
P = I² · R        (substituting V = IR)
P = V² / R        (substituting I = V/R)
```

All three are the same equation. Use whichever matches what you know.

**Why you care:** every resistor turns its power into heat, and every
resistor has a limit. Common through-hole parts are **0.25 W**. Exceed
it and you have a small heater, then smoke.

**Reading the rating correctly:** 0.25 W is a *power* rating — about
heat. Resistors also have a maximum voltage, but for small resistances
the power limit binds first. For a 220 Ω 0.25 W part:

```
V at max power = √(P · R) = √(0.25 × 220) = 7.4 V
```

## 1.6 Series and parallel

**Series** — same current through each, voltages add:

```
R_total = R₁ + R₂ + R₃ + …
```

**Parallel** — same voltage across each, currents add:

```
1/R_total = 1/R₁ + 1/R₂ + …

for exactly two:  R_total = R₁R₂ / (R₁ + R₂)
```

**The parallel guardrail:** the result is *always smaller than the
smallest resistor in the group*. You've given current an extra path, so
it's easier to push through, not harder. If your answer comes out
bigger, you've flipped a fraction.

**A useful asymmetry:** 1 kΩ ∥ 10 kΩ = 909 Ω. The 10 kΩ barely matters —
a resistor ten times larger contributes almost nothing in parallel.
Conversely, in *series* it's the large one that dominates.

## 1.7 The voltage divider

The most-used circuit in electronics.

```
        V_in ──┬──
               │
            [ R₁ ]
               │
               ├──── V_out
            [ R₂ ]
               │
        GND ───┴──

V_out = V_in × R₂ / (R₁ + R₂)
```

**Sanity check built in: the bigger resistor always gets the bigger
share of the voltage.** Same current through both, so more resistance
means more volts dropped. If you compute a divider and the big resistor
got the small voltage, you flipped the fraction.

**The catch that catches everyone:** that formula is only correct if
nothing draws current from `V_out`. Connect a load and it sits in
parallel with `R₂`, and the output sags. How much is a Thevenin
question — `01-circuits.md` §1.4.

## 1.8 Short circuits and open circuits

- **Short circuit** — a path of ~0 Ω. By `I = V/R`, current tries to go
  to infinity; what actually limits it is the source's internal
  resistance. This is how batteries catch fire.
- **Open circuit** — an infinite-resistance path. No current flows,
  anywhere in that loop. A cut wire means *nothing* flows, not "less
  flows."

There's no electrical equivalent of a puddle on the floor. Charge needs
a complete loop back to the source.

---

# PART 2 — MISTAKES MADE THE FIRST TIME

Kept deliberately. On review this is more useful than the theory.

## Mistake 1 — using the wrong component's voltage (made 3×)

The dominant error of this lesson. It appeared three times in different
disguises:

| Problem | What was done | What it should be |
|---|---|---|
| LED + resistor from 5 V, LED drops 2 V | `2.0 / 0.020 = 100 Ω` | `(5 − 2.0) / 0.020 = 150 Ω` |
| 1 kΩ base resistor, base at 0.7 V | `0.7 / 1000 = 0.7 mA` | `(5 − 0.7) / 1000 = 4.3 mA` |
| TP4056: 5 V in, 3.7 V cell, 1 A | `3.7 × 1 = 3.7 W` | `(5 − 3.7) × 1 = 1.3 W` |

**The fix, permanently:** before writing `V = IR` or `P = VI`, ask
**"what voltage does *this specific component* see?"** In a series loop
the supply is shared out; each part gets what's left after the others
take their share. The other parts' voltages are never yours.

In the TP4056 case, note that `3.7 W` is a *real* quantity — the power
delivered into the battery. Just not the one asked for:

```
from USB:      5.0 V × 1 A = 5.0 W
into the cell: 3.7 V × 1 A = 3.7 W
burnt as heat: 1.3 V × 1 A = 1.3 W      ← the chip
                             ───────
                   3.7 + 1.3 = 5.0 ✓
```

## Mistake 2 — a check that passed while the answer was wrong

For 330 Ω + 470 Ω in series across 9 V, the answers given were 4.1625 V
and 4.8375 V. **They sum to exactly 9.0000 V** — the check passed.

They were still wrong. The correct values are 3.7125 V and 5.2875 V.

**Why the check missed it:** sum-to-supply tests only one property, and
two wrong numbers can still add to the right total. The check that
catches it is **the current must be identical through both**:

```
4.1625 / 330 = 12.6 mA
4.8375 / 470 = 10.3 mA     ← must match. They don't. Impossible in series.
```

**Habit:** verify with a *second, different* property. Sum-to-supply and
same-current-everywhere test different things.

## Mistake 3 — rounding in the middle

`9 / 800 = 0.01125 A` was written as `0.01 A`, an 11% error carried into
everything after it.

**Carry full precision through, round only at the end.**

## Mistake 4 — misreading a power rating as a voltage rating

0.114 W in a 0.25 W resistor was judged unsafe "since it would be too
much volts." The rating is **watts**, about heat. 0.114 < 0.25, so it's
fine — running at 45% of rating.

## Mistake 5 — mAh conversion, dropping the current

`250 mAh → coulombs` was answered `3600 C`. The 3600 is seconds per
hour; the current was left out.

**Read the unit as the recipe: mAh is literally milliamps × hours.**
Convert mA→A and h→s, then multiply. `0.250 × 3600 = 900 C`.

---

# PART 3 — SIMULATIONS

All free, all checked 2026-09-30. Use these to verify every numeric
answer in Part 4 — **predict first, then simulate.**

## Start here

| Sim | Link | Best for |
|---|---|---|
| **PhET — Ohm's Law** | phet.colorado.edu/en/simulations/ohms-law | Two sliders, one equation, watching V/I/R move together. Ten minutes, then never again. |
| **PhET — Circuit Construction Kit: DC** | phet.colorado.edu/en/simulations/circuit-construction-kit-dc | Drag-and-drop with realistic parts. **The best place to do Sets C, D and E.** Grab the voltmeter and ammeter from the toolbox and probe the circuit like real bench gear. |
| **PhET — CCK: DC Virtual Lab** | phet.colorado.edu/en/simulations/circuit-construction-kit-dc-virtual-lab | Same, but no on-screen readouts — you *must* use the meters. Better practice once the basic version is easy. |
| **PhET — Resistance in a Wire** | phet.colorado.edu/en/simulations/resistance-in-a-wire | `R = ρL/A` made visual. Stretch and thin the wire, watch R change. Do this after §1.4. |
| **PhET — Battery Voltage** | phet.colorado.edu/en/simulations/battery-voltage | What's physically happening inside a cell. |

## Then move up

| Sim | Link | Notes |
|---|---|---|
| **Falstad CircuitJS** | falstad.com/circuit | The workhorse. Current shown as moving dots — the bicycle chain made visible. Denser and faster than PhET once you're past beginner stage. |
| **Multisim Live** | multisim.com | Browser SPICE, free tier. A step toward real simulation. |
| **Tinkercad Circuits** | tinkercad.com/circuits | Breadboard view + Arduino. Where Set G belongs. |
| **DCACLab** | dcaclab.com | Photo-realistic bench with a real-looking multimeter. Good for practising *measurement technique*, not just theory. |
| **EveryCircuit** | everycircuit.com/app | Beautiful animated voltage/current. Free tier is limited; worth a look, not worth paying for yet. |

## The one drill that builds fluency fastest

In **Falstad**:

1. Build the circuit.
2. **Write your predicted current and voltages on paper.**
3. Hover over each component and read the actual values.
4. If they disagree, find out why *before* moving on.

Predict → verify → explain the gap. That loop is the whole method, and
it's what `../PROJECTS.md` asks you to document for real builds.

---

# PART 4 — PRACTICE

Work them on paper. Answers with full working in Part 5 — don't look
until you've attempted a whole set.

**Target for fluency: Sets A–E with no errors and no calculator
hesitation.**

## Set A — Ohm's law drills

Find the missing quantity.

| # | Given | Find |
|---|---|---|
| A1 | 9 V across 470 Ω | I |
| A2 | 3.3 V across 1 kΩ | I |
| A3 | 12 V across 2.2 kΩ | I |
| A4 | 25 mA through 180 Ω | V |
| A5 | 2 mA through 4.7 kΩ | V |
| A6 | 5 V, 40 mA | R |
| A7 | 3.7 V, 90 mA | R |
| A8 | 1.5 V across 68 Ω | I |
| A9 | 150 mA through 10 Ω | V |
| A10 | 24 V, 0.5 A | R |
| A11 | 0.7 V across 220 Ω | I |
| A12 | 100 µA through 1 MΩ | V |

## Set B — Power

**B1.** 9 V across 470 Ω. Power?
**B2.** 100 mA through 10 Ω. Power?
**B3.** 5 V at 20 mA. Power?
**B4.** 12 V across 1 kΩ. Power? Is a 0.25 W part safe?
**B5.** 3.3 V across 100 Ω. Power? Is a 0.25 W part safe?
**B6.** A 0.25 W, 1 kΩ resistor. What's the maximum voltage you may put
across it, and the maximum current through it?
**B7.** 5 V across 47 Ω. Power? What rating do you need?
**B8.** Your motor at 3.7 V drawing 90 mA. Power?

## Set C — Series

**C1.** 100 Ω + 220 Ω + 470 Ω across 9 V. Find R_total, the current, and
the voltage across each. Check both ways (sum of voltages, and same
current everywhere).
**C2.** Two 1 kΩ across 5 V. Current and voltage across each.
**C3.** Three 220 Ω across 12 V. R_total, current, voltage across each.
**C4.** 330 Ω + 680 Ω across 3.3 V. Current and both voltages.

## Set D — Parallel

**D1.** 1 kΩ ∥ 1 kΩ
**D2.** 470 Ω ∥ 470 Ω ∥ 470 Ω
**D3.** 2.2 kΩ ∥ 4.7 kΩ
**D4.** 100 Ω ∥ 220 Ω
**D5.** 1 kΩ ∥ 10 kΩ — and comment on how much the 10 kΩ changed things.
**D6.** What resistor in parallel with 1 kΩ gives exactly 500 Ω?
**D7.** Four 10 Ω in parallel.

## Set E — Voltage dividers

**E1.** 10 kΩ over 10 kΩ from 5 V. Output?
**E2.** 10 kΩ over 2.2 kΩ from 5 V, output taken across the 2.2 kΩ.
**E3.** You want 3.3 V out of 12 V. Using 3.3 kΩ as the bottom resistor,
what's the top one?
**E4.** **Battery monitor for your device.** You want to read a cell that
reaches 4.2 V using the AVR's 1.1 V internal reference. With 10 kΩ as
the bottom resistor, what top resistor do you need? Then: the nearest
standard values are 27 kΩ and 30 kΩ. **Which one must you pick, and
why?** (Compute the output with each.)
**E5.** Take E1's 10 kΩ/10 kΩ divider and connect a 10 kΩ load across the
output. What is the output now?
**E6.** For a 4.7 kΩ / 4.7 kΩ divider on 5 V, find the Thevenin
equivalent — `V_th` and `R_th`.

## Set F — "Which voltage?" (targeted)

This set exists because of Mistake 1. Ask the question every time.

**F1.** A blue LED (3.2 V drop) at 20 mA from 5 V. Series resistor?
**F2.** A red LED (1.8 V drop) at 10 mA from 3.3 V. Series resistor?
**F3.** *Two* LEDs in series (2.0 V each) at 20 mA from 9 V. Resistor?
**F4.** A base resistor from a 3.3 V pin, base at 0.7 V, wanting 5 mA.
**F5.** In F4, how much power does the *resistor* dissipate, and how much
does the *base junction* dissipate?
**F6.** A 5.1 V zener from a 12 V supply, at 10 mA. Series resistor?
**F7.** A TP4056 charging at 500 mA from 5 V USB into a 3.9 V cell. Power
dissipated *in the chip*?
**F8.** A linear regulator making 5 V from 12 V at 300 mA. Power
dissipated in the regulator?

## Set G — Your own hardware

**G1.** Your 250 mAh cell. At a 22 mA average draw, runtime?
**G2.** How many joules of energy does that cell hold at 3.7 V?
**G3.** If you set the TP4056's `R3` to 5 kΩ, what charge current do you
get? (`I = 1200 / R`.)
**G4.** What `R3` gives 0.3C charging (75 mA) for your 250 mAh cell?
**G5.** Your motor driven at PWM duty 200/255 from 5 V. Average voltage?
**G6.** An I2C line with a 4.7 kΩ pull-up to 5 V, held low by a device.
How much current flows through the pull-up while it's low?
**G7.** Nano 20 mA + sensor 20 mA + motor 90 mA. Total draw, and runtime
from a 250 mAh cell if everything ran continuously.
**G8.** Your device's *average* draw is much lower than G7 because the
motor only pulses. If the motor is on 30% of the time, what's the
average total, and the runtime?

## Set H — Concepts, in words

**H1.** Why is the current leaving a battery equal to the current
returning to it, even though the circuit "uses power"? What *is*
consumed?
**H2.** Why does a bird on a high-voltage line survive?
**H3.** Why do electrons drift at ~0.07 mm/s yet a lamp lights
instantly?
**H4.** Give three components that don't obey Ohm's law and say what
each does instead.
**H5.** Why must a parallel combination always be smaller than its
smallest member?
**H6.** Why does a battery's terminal voltage drop when you connect a
load?
**H7.** A voltage divider's formula assumes something. What, and what
happens when it isn't true?
**H8.** Why is "the voltage at this point" technically meaningless?

## Set I — Challenge

**I1.** A 1 kΩ in series with (2.2 kΩ ∥ 4.7 kΩ), all across 9 V. Find the
total resistance, the total current, the voltage across the 1 kΩ, the
voltage across the parallel pair, and the current through *each* of the
parallel resistors. Check that the two branch currents sum to the total.
**I2.** A divider from 5 V has 10 kΩ on top and outputs 1.5 V. What's the
bottom resistor?
**I3.** Two 100 Ω in parallel across 5 V. Total power, and power in each?
**I4.** From 12 V you need exactly 40 mA through a 100 Ω load. What
total additional series resistance do you need?

---

# PART 5 — ANSWERS

## Set A

| # | Working | Answer |
|---|---|---|
| A1 | 9/470 | **19.15 mA** |
| A2 | 3.3/1000 | **3.3 mA** |
| A3 | 12/2200 | **5.45 mA** |
| A4 | 0.025 × 180 | **4.5 V** |
| A5 | 0.002 × 4700 | **9.4 V** |
| A6 | 5/0.04 | **125 Ω** |
| A7 | 3.7/0.09 | **41.1 Ω** |
| A8 | 1.5/68 | **22.06 mA** |
| A9 | 0.15 × 10 | **1.5 V** |
| A10 | 24/0.5 | **48 Ω** |
| A11 | 0.7/220 | **3.18 mA** |
| A12 | 0.0001 × 10⁶ | **100 V** |

## Set B

**B1.** `9²/470` = **172 mW**
**B2.** `0.1² × 10` = **100 mW**
**B3.** `5 × 0.02` = **100 mW**
**B4.** `12²/1000` = **144 mW** — safe in a 0.25 W part (58% of rating).
**B5.** `3.3²/100` = **109 mW** — safe (44%).
**B6.** `V = √(0.25 × 1000)` = **15.8 V**; `I = √(0.25/1000)` =
**15.8 mA**. Note both come from the same limit.
**B7.** `5²/47` = **532 mW** — a 0.25 W part **fails**, and so does a
0.5 W part: 532 mW is already 6% *over* it, with no margin at all. You
need a **1 W** resistor.
**B8.** `3.7 × 0.09` = **333 mW**

## Set C

**C1.** R_total = **790 Ω**; I = 9/790 = **11.39 mA**
V₁₀₀ = **1.139 V**, V₂₂₀ = **2.506 V**, V₄₇₀ = **5.354 V**
Sum = 9.000 ✓ · Each V/R = 11.39 mA ✓
**C2.** I = 5/2000 = **2.5 mA**; **2.5 V** across each.
**C3.** R_total = **660 Ω**; I = **18.18 mA**; **4.0 V** across each.
**C4.** R_total = **1010 Ω**; I = **3.267 mA**;
V₃₃₀ = **1.078 V**, V₆₈₀ = **2.222 V**. Sum = 3.300 ✓

## Set D

**D1.** **500 Ω** — two equal resistors in parallel always halve.
**D2.** **156.7 Ω** — three equal ones give R/3.
**D3.** **1499 Ω**
**D4.** **68.75 Ω**
**D5.** **909 Ω** — the 1 kΩ barely moved. **A resistor 10× larger
contributes almost nothing in parallel**; ignore it in rough work.
**D6.** **1 kΩ.** (Two equal resistors halve.)
**D7.** **2.5 Ω** — four equal give R/4.

## Set E

**E1.** `5 × 10/(10+10)` = **2.5 V**
**E2.** `5 × 2.2/(10+2.2)` = **0.902 V**
**E3.** `R_top = 3300 × (12−3.3)/3.3` = **8.7 kΩ**
**E4.** Exact: `R_top = 10k × (4.2−1.1)/1.1` = **28.18 kΩ**.
- With **27 kΩ**: output = `4.2 × 10/37` = **1.135 V** — **exceeds the
  1.1 V reference.** The ADC saturates at full scale and you lose the
  top of your range.
- With **30 kΩ**: output = `4.2 × 10/40` = **1.05 V** — safely under.

**Pick 30 kΩ.** The rule: when scaling *into* a reference, **round the
top resistor up**, so the maximum input lands below full scale. Going
over doesn't just lose accuracy — it makes a dying battery and a full
one read identically.

**E5.** The 10 kΩ load parallels the bottom 10 kΩ → 5 kΩ. Output =
`5 × 5/(10+5)` = **1.667 V**, not 2.5 V. **The divider sagged 33%
just by being used.**
**E6.** `V_th` = **2.5 V**; `R_th` = 4.7k ∥ 4.7k = **2.35 kΩ**.

## Set F

**F1.** `(5 − 3.2)/0.02` = **90 Ω**
**F2.** `(3.3 − 1.8)/0.01` = **150 Ω**
**F3.** Two LEDs take 4.0 V total. `(9 − 4.0)/0.02` = **250 Ω**
**F4.** `(3.3 − 0.7)/0.005` = **520 Ω**
**F5.** Resistor: `2.6 V × 5 mA` = **13 mW**. Junction:
`0.7 V × 5 mA` = **3.5 mW**. The resistor burns nearly 4× as much —
its whole job is absorbing the excess so the semiconductor doesn't.
**F6.** `(12 − 5.1)/0.01` = **690 Ω**
**F7.** `(5 − 3.9) × 0.5` = **550 mW**
**F8.** `(12 − 5) × 0.3` = **2.1 W** — a genuinely hot part needing a
heatsink. This is why switching regulators exist.

## Set G

**G1.** `250/22` = **11.4 hours**
**G2.** `900 C × 3.7 V` = **3330 J** (= 0.925 Wh, which is exactly what
the cell's label says).
**G3.** `1200/5000` = **240 mA**
**G4.** `1200/0.075` = **16 kΩ**
**G5.** `5 × 200/255` = **3.92 V**
**G6.** `5/4700` = **1.06 mA** per line, continuously, whenever the line
is held low. On two lines that's ~2 mA — worth knowing on a battery.
**G7.** **130 mA** total; `250/130` = **1.92 hours**.
**G8.** Motor contributes `90 × 0.30` = 27 mA average, so total =
`20 + 20 + 27` = **67 mA**; runtime = `250/67` = **3.7 hours**.
**Duty cycle is the difference between a 2-hour and a 4-hour device.**

## Set H

**H1.** Charge is conserved; **energy** is consumed. Each coulomb picks
up energy at the battery, spends it crossing the components, and returns
carrying nothing — but it *returns*. Same charge, less energy. The
rigorous reason the current matches: there is nowhere for charge to
accumulate in a wire.
**H2.** Both feet are on the same conductor, so the potential difference
between them is ~0 V. No difference, no current.
**H3.** The electric field propagates at a large fraction of light
speed, so every electron in the wire — including those already at the
lamp — starts drifting almost simultaneously. The pipe was already full.
**H4.** Diode/LED (exponential I-V); transistor (third terminal controls
current); incandescent bulb (resistance rises ~10× when hot); motor
(back-EMF opposes supply). Any three.
**H5.** Adding a parallel path gives current somewhere extra to go, so
total opposition falls. Formally, adding a positive term to
`1/R₁ + 1/R₂ + …` increases the sum, so its reciprocal decreases.
**H6.** Internal resistance. `V_terminal = EMF − I·R_internal`, so
drawing current drops the terminal voltage by `I·R_internal`.
**H7.** It assumes **nothing draws current from the output**. A load
parallels the bottom resistor and the output sags — see E5, where it
fell from 2.5 V to 1.667 V.
**H8.** Voltage is defined as a *difference* in potential energy per
charge between two points. A single point has no difference. "Voltage at
a point" is shorthand for "relative to the node we called ground."

## Set I

**I1.** 2.2k ∥ 4.7k = **1499 Ω**. R_total = **2499 Ω**.
I_total = 9/2499 = **3.602 mA**.
V across 1 kΩ = **3.602 V**. V across the pair = **5.398 V**.
Branch currents: `5.398/2200` = **2.454 mA**, `5.398/4700` =
**1.148 mA**. Sum = 3.602 mA ✓ (that's KCL, Lesson 2).
Note the smaller resistor takes the larger current — the opposite of
the series case, and worth internalising.
**I2.** `R_bot = 10k × 1.5/(5 − 1.5)` = **4.29 kΩ**
**I3.** R_parallel = 50 Ω. Total power = `5²/50` = **0.5 W**; each
resistor = `5²/100` = **0.25 W**. They add ✓
**I4.** The 100 Ω load drops `0.04 × 100` = 4.0 V, leaving 8.0 V.
`8.0/0.04` = **200 Ω** of additional series resistance.

---

# Fluency checklist

Tick when you can do it cold, no notes, no hesitation:

- [ ] Ohm's law in all three arrangements
- [ ] Power in all three forms, and choosing the convenient one
- [ ] Series and parallel combination, with the "smaller than the
      smallest" guardrail applied automatically
- [ ] Voltage divider, with the "bigger R gets bigger V" check
- [ ] **Asking "what voltage does this component see?" before every
      calculation** ← the one that caused every error in Part 2
- [ ] Verifying with a *second, different* property
- [ ] mAh ↔ coulombs ↔ runtime
- [ ] Explaining charge-conserved / energy-consumed in your own words

When Sets A–E are effortless, go to **Lesson 2 — Kirchhoff's laws**.
