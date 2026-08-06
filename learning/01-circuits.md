# Module 01 — Circuit theory

**Prereqs:** algebra and trig (§1). The AC half additionally needs
complex numbers (§4) and derivatives (§2).
**Time:** ~10 weeks (6 for DC, 4 for AC).
**Unlocks:** everything electrical. This is the foundation module.

---

## Why this matters for your wristband

Nearly every question you have hit so far on that build is a circuit
question wearing a costume:

- "Which resistor for the transistor base?" — divider and Ohm's law.
- "Why 10 kΩ for the TP4056's `R3`?" — a current-setting relationship
  and a power-dissipation check.
- "Why is I2C flaky at 400 kHz?" — an RC time constant on the bus.
- "Can I power the Nano from a 3.7 V cell through VIN?" — a regulator
  dropout question, which is a circuit question.
- "How long will the battery last?" — average current, which is
  integration over a circuit's operating states.

You have been answering these by lookup and by asking. This module is
how you start answering them by derivation.

---

## Part A — DC circuits

### 1.1 The three things that are actually true

Everything in DC circuit analysis is these three facts plus algebra.

**Charge is conserved (Kirchhoff's Current Law).** The sum of currents
into any node equals the sum out. Charge doesn't pile up at a junction.

**Energy is conserved (Kirchhoff's Voltage Law).** Around any closed
loop, the voltage rises equal the voltage drops. If you walk a loop and
come back to where you started, you're at the same potential you left.

**Ohm's law (`V = IR`) is a property of resistors, not a law of nature.**
This is worth internalising early. Diodes don't obey it. Transistors
don't obey it. LEDs don't obey it — which is exactly why placement-test
question 2 required subtracting the LED's 2 V drop before dividing.
Treating everything as a resistor is the most common beginner error and
it produces confidently wrong answers.

### 1.2 Voltage is a difference — always

There is no such thing as "the voltage at a point." There is only the
voltage *between two points*. When someone says "5 V at that pin," they
mean "5 V between that pin and the node we agreed to call ground."

Consequences you will meet:

- **Ground is a choice, not a physical thing.** You pick a reference node
  and call it 0 V.
- **Two circuits with separate grounds cannot meaningfully exchange
  signals** until you tie their grounds together. This is why every
  wiring diagram in your `README.md` has a GND connection alongside every
  signal — the GND is not a formality, it's what makes the signal voltage
  *mean* anything.
- **Floating pins have no defined voltage.** An unconnected input is not
  0 and not 5; it's whatever nearby fields and leakage currents make it,
  and it will drift and read as noise. This is the general principle
  behind your `PS` pin discovery — a mode-select pin that isn't driven
  isn't "off," and in the GY-53's case it was pulled high on the board.

### 1.3 Series, parallel, and the voltage divider

Series: same current through each, voltages add. `R_total = R₁ + R₂ + …`
Parallel: same voltage across each, currents add.
`1/R_total = 1/R₁ + 1/R₂ + …`

**The voltage divider is the single most-used circuit in electronics:**

```
V_out = V_in · R₂/(R₁ + R₂)
```

You will use this to scale sensor signals into an ADC's range, to bias
transistors, to make reference voltages, and to read resistive sensors.
Learn it so thoroughly that you can see it inside other circuits.

**The catch that catches everyone:** a divider's output voltage is only
correct if nothing is drawing current from it. The moment you connect a
load, the load is in parallel with `R₂` and the output sags. How much it
sags is a Thevenin question, which is next.

### 1.4 Thevenin and Norton — the most useful abstraction in circuits

**Thevenin's theorem:** any network of sources and resistors, seen from
two terminals, behaves *exactly* like a single voltage source `V_th` in
series with a single resistor `R_th`. No exceptions, for linear circuits.

- `V_th` = the open-circuit voltage at the terminals.
- `R_th` = the resistance seen looking in, with all independent voltage
  sources shorted and current sources opened.

**Why this is the big idea:** it lets you replace an entire complicated
subcircuit with two numbers and reason about it as a black box. That
`R_th` is what people mean by **output impedance**, and it is the thing
that determines whether connecting your circuit to something else will
break it.

Worked example with your own hardware: a divider of 10 kΩ / 4.7 kΩ across
5 V has `V_th = 1.60 V` and `R_th = 10k ∥ 4.7k = 3.20 kΩ`. Feed that into
an ATmega328P analog input — fine, the ADC's sample-and-hold wants a
source under about 10 kΩ. Feed the same divider into something drawing
1 mA and the output collapses by 3.2 V. Same divider, completely
different outcome, and `R_th` is what tells you which case you're in.

**Norton** is the same theorem with a current source in parallel with the
same resistor. Use whichever is more convenient.

### 1.5 Power, and why components have ratings

```
P = V·I = I²R = V²/R
```

Every resistor turns its power into heat, and every resistor has a
maximum it can dissipate (the common through-hole ones you'd buy at Alash
are 0.25 W).

**Do this calculation on your own build:** your base resistor sees
roughly `(5 − 0.7) = 4.3 V` across it. At 220 Ω that's
`4.3²/220 = 84 mW` — fine for a 0.25 W part. Now imagine you'd chosen
22 Ω by mistake: `840 mW`, and the resistor becomes a small heater and
eventually smoke. Power ratings are the difference.

### 1.6 Real components are not ideal

A resistor is a resistor **plus** a small series inductance **plus** a
small parallel capacitance. A wire has resistance and inductance. A
battery has internal resistance — which is precisely why its terminal
voltage sags under load, and why your 250 mAh pouch behaves differently
from a bench supply.

At DC and low frequency you can ignore all of this. At 400 kHz on an I2C
bus you cannot. Knowing *when* the ideal model stops working is a large
part of what separates a working design from a mysterious one.

---

## Part B — AC circuits

**Do §4 (complex numbers) before starting this.** Without phasors, AC
analysis is a wall of trig identities; with them, it's the DC analysis
you already know.

### 1.7 Impedance — the key generalisation

Replace resistance `R` with complex impedance `Z`:

```
Resistor:   Z_R = R                    (real; no phase shift)
Capacitor:  Z_C = 1/(jωC)              (current leads voltage by 90°)
Inductor:   Z_L = jωL                  (current lags voltage by 90°)

where ω = 2πf
```

**And now every DC tool works unchanged.** Series impedances add.
Parallel impedances combine reciprocally. Voltage dividers divide.
Thevenin still applies. This is an enormous return on two weeks of
complex-number practice, and it is the reason engineers bother with `j`.

Read the sign of the reactance physically: `Z_C` shrinks as frequency
rises (a capacitor becomes a short at high frequency, an open at DC),
`Z_L` grows (an inductor is a short at DC, an open at high frequency).
Those four facts explain most filter behaviour before you learn any
filter theory.

### 1.8 The RC circuit, in both domains

The RC circuit is the hydrogen atom of electrical engineering — the
simplest thing that shows you everything.

**Time domain (needs derivatives):** charging from a step,
`v(t) = V(1 − e^(−t/τ))` with `τ = RC`.

| t | fraction of final value |
|---|---|
| 1τ | 63.2% |
| 2τ | 86.5% |
| 3τ | 95.0% |
| 5τ | 99.3% |

The "5 time constants ≈ settled" rule of thumb comes from that last row.

**Frequency domain:** it's a divider between `R` and `1/(jωC)`, giving a
low-pass filter with corner frequency

```
f_c = 1/(2πRC)
```

At `f_c` the output is `1/√2` (−3 dB) of the input and lagging by 45°.
Above it, the response falls at 20 dB per decade.

**These are the same circuit.** The time constant and the corner
frequency are the same fact viewed two ways: `f_c = 1/(2πτ)`. Getting
comfortable moving between "how fast does it settle" and "what
frequencies does it pass" is the core skill of Module 04.

### 1.9 Your I2C bus is an RC circuit — worked in full

This is the best example in your build of theory answering a real
question, so work it properly.

I2C lines are **open-drain**: a device can only pull the line *down*.
Nothing drives it up. A pull-up resistor does that, and the line's
stray capacitance (wires, pins, the breadboard) has to charge through
that resistor. So every rising edge is an RC charging curve.

The I2C specification measures rise time from 30% to 70% of `V_DD`, and
for an RC curve that interval is:

```
t_r = τ · ln(0.7/0.3) = 0.847 · R · C
```

The spec allows **1000 ns in standard mode (100 kHz)** and only
**300 ns in fast mode (400 kHz)**. Your `obstacle_haptic.ino` calls
`Wire.setClock(400000)`, so you're in fast mode.

Assume a realistic 100 pF of bus capacitance for breadboard wiring, and
solve for the largest pull-up you can use:

```
R_max = 300 ns / (0.847 × 100 pF) ≈ 3.5 kΩ
```

**A typical 4.7 kΩ pull-up is already too weak for 400 kHz at that
capacitance.** It gives `t_r ≈ 400 ns`, over spec. It will often still
work — I2C is forgiving — but it is the mechanism behind "it works on
short wires and gets flaky when I lengthen them," because longer wires
mean more `C`, which means slower edges.

**Practical conclusions you can now derive rather than look up:**

- Faster bus or longer wires → smaller pull-ups (2.2 kΩ, or 1 kΩ).
- Smaller pull-ups cost more current when the line is held low
  (`5 V / 1 kΩ = 5 mA` per line), which matters on a battery.
- The AVR's *internal* pull-ups (20–50 kΩ, which `Wire.begin()` enables)
  are **far too weak** for reliable fast-mode I2C — the GY-53's own
  on-board pull-ups are what's actually doing the work on your bench.
- If I2C ever misbehaves at 400 kHz, dropping to `Wire.setClock(100000)`
  quadruples the rise-time budget. That's a legitimate first diagnostic,
  and now you know why it works.

### 1.10 Resonance and RLC

Put `L` and `C` together and their reactances cancel at one frequency:

```
f₀ = 1/(2π√(LC))
```

At `f₀` a series RLC has minimum impedance (just `R`) and a parallel RLC
has maximum. The **quality factor** `Q = ω₀L/R` measures how sharp the
peak is — high `Q` means narrow and ringy, low `Q` means broad and
damped.

Resonance is how radios select stations, how oscillators keep time, how
switching supplies filter, and — less happily — how a fast digital edge
into an inductive wire produces the ringing you see on a scope.

Note the connection back to §5 of the math backbone: `Q` and the damping
ratio ζ describe the same thing. `ζ = 1/(2Q)`. An RLC circuit and a
mass-spring-damper are the same differential equation, which is why
electrical and mechanical engineers can talk to each other at all.

---

## Do this — labs for Module 01

All free, all runnable tonight.

1. **Falstad divider sag.** Build a 10 kΩ/10 kΩ divider from 5 V.
   Confirm 2.5 V out. Now hang a 10 kΩ load on the output and watch it
   drop to 1.67 V. Predict that number from Thevenin *before* you run it.
2. **RC step response.** 10 kΩ + 1 µF, 5 V step. Measure the time to
   63% on the simulator's scope. Confirm it's 10 ms.
3. **The same RC, swept in frequency.** Switch the source to AC, sweep,
   and find the −3 dB point. Confirm it's 15.9 Hz — and confirm for
   yourself that `1/(2π · 10k · 1µ)` gives exactly that.
4. **Your actual I2C bus.** Compute the rise time for the pull-up value
   your GY-53 actually has (read the board, or measure resistance from
   SDA to VCC with power off). Decide whether 400 kHz is inside spec on
   your wiring. Then test the prediction: run your sensor sketch at
   400 kHz and at 100 kHz with progressively longer jumper wires and see
   where each one breaks.
5. **Battery internal resistance.** Measure your 502030 cell's open
   circuit voltage, then its voltage under a known load, and compute
   `R_internal = ΔV / I`. You'll get something in the tens-of-milliohms
   to low-ohms range. This number tells you how much your supply will
   sag when the motor kicks in — a real effect on your build, and a
   plausible cause of brownouts once you go to battery in Phase 5.

---

## Self-check — closed book

You should be able to answer all of these without notes before moving
on.

1. State KCL and KVL and say which conservation law each expresses.
2. Why can't you compute LED current with `V/R` using the supply voltage?
3. Compute `V_th` and `R_th` for a 4.7 kΩ / 2.2 kΩ divider on 3.3 V.
4. A capacitor is fully charged and connected to a DC supply. What
   current flows, and which equation tells you so?
5. What is the impedance of a 10 µF capacitor at 50 Hz?
6. An RC low-pass has `R = 1 kΩ`, `C = 100 nF`. Give its corner
   frequency and its time constant, and show they're the same fact.
7. Why do I2C buses need pull-up resistors at all, and what sets the
   maximum usable value?
8. Your motor draws 90 mA from a cell with 0.5 Ω internal resistance.
   How much does the terminal voltage sag when it switches on?

---

## Resources for this module

- **All About Circuits, Volume I (DC) and Volume II (AC)** — free online
  textbook, genuinely good, well-paced for self-study. Start here.
- **MIT OCW 6.002 Circuits and Electronics** — harder, with real problem
  sets. Do this second if you want depth.
- **Falstad Circuit Simulator** (falstad.com/circuit) — the best
  intuition-building tool in existence for this material. Free, in the
  browser, shows current as moving dots. Use it constantly.
- **LTspice** — free from Analog Devices, a real SPICE simulator. Move to
  this once Falstad's approximations start to bother you.
- **The Art of Electronics** (Horowitz & Hill) — not a first textbook,
  but the reference you'll keep for twenty years. Get it eventually.
