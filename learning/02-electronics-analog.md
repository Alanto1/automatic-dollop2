# Module 02 — Semiconductors and analog electronics

**Prereqs:** Module 01 Part A. Derivatives (§2) for the reactive parts,
exponentials/logs (§1) for the diode equation.
**Time:** ~10 weeks.
**Unlocks:** every active circuit. This is where "electronics" starts as
distinct from "circuits."

---

## Why this matters for your wristband

Your motor driver — `Nano D9 → resistor → 2N2222 base`, motor in the
collector path, 1N4148 across the motor — is a complete lesson in this
module. Right now you have it from a schematic someone handed you. By
the end of this module you will be able to derive every value in it,
explain what breaks if you change each one, and choose a MOSFET
alternative on purpose rather than by copying.

The TP4056 charge-current hazard is the other half: a linear charger's
behaviour, why `R3` sets current the way it does, and why 1 A into a
250 mAh cell is a real hazard rather than just "a bit fast" — all of that
is in here.

---

## 2.1 What a semiconductor actually is

You need enough solid-state physics to reason, not enough to design
chips. That's about two weeks.

- **Doping.** Pure silicon is a poor conductor. Add a pentavalent
  impurity (phosphorus) → spare electrons → **n-type**. Add a trivalent
  one (boron) → spare "holes" → **p-type**. Holes aren't real particles;
  they're a bookkeeping device for the absence of an electron, and they
  behave like positive charge carriers.
- **The PN junction.** Join p and n. Carriers diffuse across, leaving a
  **depletion region** with a built-in field that opposes further
  diffusion. That field is the whole reason a diode is one-way.
- **Forward bias** shrinks the depletion region → current flows.
  **Reverse bias** widens it → almost none does.
- **Temperature matters, a lot.** Semiconductor behaviour is
  exponential in temperature. This is behind thermal runaway, behind
  why `V_BE` drifts about −2 mV/°C, and behind why power devices need
  heatsinks and current-sharing resistors.

Don't go deeper than this yet. Band diagrams and carrier transport
equations are a second pass, not a first.

---

## 2.2 The diode

**The real equation** (Shockley):

```
I = I_S · (e^(V/(n·V_T)) − 1)      V_T = kT/q ≈ 25.7 mV at 25 °C
```

Note what this says: current is **exponential** in voltage. A 60 mV
increase multiplies current by roughly 10×. That exponential steepness is
why the "0.7 V drop" model works at all — over any current range you care
about, the voltage barely moves.

**The three models, and when to use each:**

| Model | Says | Use when |
|---|---|---|
| Ideal | short forwards, open backwards | sketching topology |
| Constant drop | 0.7 V (Si) / 0.3 V (Schottky) / 2 V (LED) | 95% of hand analysis |
| Shockley | the exponential above | temperature effects, log amps, precise references |

**Key diode types you'll meet:**

- **Schottky** — lower forward drop (~0.3 V), much faster recovery. Used
  where drop or speed matters.
- **Zener** — deliberately operated in reverse breakdown at a known
  voltage. A crude voltage reference.
- **LED** — forward drop set by the band gap, so it varies by colour
  (red ~1.8 V, blue/white ~3.2 V). **This is why you never drive an LED
  without a series resistor**: the exponential I-V means a tiny voltage
  overshoot becomes a huge current overshoot. The resistor turns a
  voltage-controlled exponential into a well-behaved current.

### Your flyback diode, derived

Your motor is an inductor. When the transistor turns off, the inductor's
current cannot change instantly, and `v = L·di/dt` means forcing it to
change fast generates a large reverse voltage — routinely tens of volts
in a 5 V circuit. That spike appears across the transistor's
collector-emitter junction and exceeds its rating.

The 1N4148 across the motor, **cathode to the positive lead**, is
reverse-biased during normal operation (invisible) and forward-biased by
the spike (conducting). It gives the collapsing current a loop to
circulate in, so `di/dt` is set by the diode's forward drop rather than
by the transistor's switching speed. The spike is clamped to roughly one
diode drop above the supply.

**Two things worth knowing that the schematic doesn't tell you:**

1. The 1N4148 is rated for a couple of hundred milliamps average — check
   your specific datasheet. Your vibration motor draws well under that,
   so it's fine here, but the same circuit driving a bigger motor needs a
   bigger diode. The diode must handle the motor's *full running
   current*, because that's the current it inherits at switch-off.
2. A flyback diode slows the motor's current decay, which slightly slows
   how fast the motor stops. For a haptic buzzer this is irrelevant. For
   a PWM speed controller at high frequency it can matter, which is why
   fast-recovery or Schottky diodes get used there.

---

## 2.3 The bipolar junction transistor (BJT)

**The model:** a BJT is current-controlled. A small base current controls
a much larger collector current.

**Three regions of operation:**

| Region | Condition | Behaviour |
|---|---|---|
| Cut-off | `V_BE < ~0.6 V` | no current, transistor is an open switch |
| Active | `V_BE ≈ 0.7 V`, `V_CE` large | `I_C = β · I_B` — an amplifier |
| Saturation | base overdriven | `V_CE ≈ 0.2 V`, `I_C` set by the external circuit, **not** by β — a closed switch |

**The distinction that matters most for you: an amplifier lives in the
active region, a switch lives in saturation.** They're the same device
used two completely different ways, and confusing them is the classic
error.

### Deriving your own base resistor

Say your 10×3 mm vibration motor draws about 90 mA at 5 V — measure
yours, but that's the right order. You want the 2N2222 **saturated**, so
it acts as a closed switch with only ~0.2 V wasted across it.

The design rule for a saturated switch is to **force** the base current
well above what β would require. A forced gain of 10 is the standard
choice:

```
I_B = I_C / 10 = 9 mA
R_B = (V_pin − V_BE) / I_B = (5.0 − 0.7) / 0.009 ≈ 480 Ω
```

So ~470 Ω is the theoretically clean value. Now check the two endpoints
your `README.md` says both work:

- **220 Ω** → `I_B = 19.5 mA`. Saturates hard, definitely works — but
  that's a lot of current out of one AVR pin. The ATmega328P's absolute
  maximum per I/O pin is 40 mA, and there are per-port and whole-package
  limits below that. 19.5 mA is legal but uncomfortably close to the
  edge of what you'd want to run continuously.
- **1 kΩ** → `I_B = 4.3 mA`, a forced gain of about 21. A 2N2222's β at
  100 mA is comfortably above that, so it still saturates. Gentler on
  the pin.

**Conclusion you can now defend:** both work, 1 kΩ is the safer of the
two given the pin-current limit, and 470 Ω is the textbook answer.
That's a real design decision you just made from theory, not from a
forum post.

### Why not a MOSFET?

You could use one, and for a bigger load you should. A MOSFET is
**voltage**-controlled: it needs essentially no continuous gate current,
only a brief pulse to charge the gate capacitance. That makes it more
efficient and easier on your I/O pin.

**The trap:** most MOSFETs need 10 V on the gate to turn on fully. Drive
an IRF540 from a 5 V pin and it half-turns-on, dissipates heat, and you
conclude MOSFETs are unreliable. You need a **logic-level** MOSFET
(IRLZ44N, or a 2N7000 for small loads) whose threshold is low enough for
5 V — or even 3.3 V — drive. Check `V_GS(th)` and, more importantly, the
`R_DS(on)` **specified at your actual gate voltage**. A part quoting
`R_DS(on) at V_GS = 10 V` is telling you it isn't a logic-level part.

---

## 2.4 Amplifiers and the small-signal idea

This is the conceptual leap of analog electronics, so take it slowly.

An amplifier works by setting up a **DC bias point** (the "quiescent
point," Q-point) in the active region, then superimposing a small AC
signal on it. The device is nonlinear, but *over a small enough range
around the Q-point* it's approximately linear — so you can analyse the
signal with linear circuit theory while the DC bias holds the device
where it needs to be.

That's the entire trick, and it's a genuinely deep idea: **linearise a
nonlinear system around an operating point.** You will meet the exact
same move again in control theory when linearising a plant model, and
again in numerical methods. Learning it here pays off three times.

Learn: common-emitter, common-collector (emitter follower), and
common-base configurations; input and output impedance of each; gain;
and biasing networks. Understand why the emitter follower has voltage
gain of ~1 and is still enormously useful (it converts a high output
impedance into a low one — a buffer).

---

## 2.5 Operational amplifiers

Op-amps are where analog design becomes pleasant. A high-gain
differential amplifier wrapped in negative feedback behaves according to
the feedback network, almost independently of the amplifier itself.

**The two golden rules** (valid whenever there's negative feedback and
the op-amp isn't saturated):

1. No current flows into either input.
2. The op-amp drives its output to whatever it takes to make `V₊ = V₋`.

From those two rules alone you can derive every standard configuration:

| Circuit | Gain |
|---|---|
| Non-inverting | `1 + R_f/R_in` |
| Inverting | `−R_f/R_in` |
| Voltage follower / buffer | `1` (but converts impedance) |
| Difference amplifier | `(R_f/R_in)(V₊ − V₋)` |
| Integrator | `−1/(R·C) ∫V_in dt` |
| Differentiator | `−R·C · dV_in/dt` |

**Derive each one yourself from the golden rules.** Do not memorise the
table. It takes three lines of algebra per row, and doing it is the
difference between using op-amps and understanding them.

**Where the ideal model breaks** (this is the actually-useful part):

- **Gain-bandwidth product.** Gain × bandwidth is roughly constant. A
  1 MHz GBW op-amp at a gain of 100 gives you 10 kHz of bandwidth, not
  1 MHz. This surprises people constantly.
- **Slew rate.** Maximum `dV/dt` at the output, in V/µs. Independent of
  bandwidth, and it's what limits large fast signals.
- **Input offset voltage.** A few mV of built-in error. Irrelevant for
  audio, fatal for a thermocouple amplifier.
- **Output swing.** A classic 741 or LM358 can't get near its supply
  rails. "Rail-to-rail" parts can, approximately. On a single 3.7 V
  battery this matters enormously.
- **Single supply vs dual.** Most textbook circuits assume ±15 V. Your
  battery gives you 0 V and 3.7 V. Single-supply design needs a
  mid-rail reference, and it's a real skill.

---

## 2.6 Power electronics

### Linear regulators

A linear regulator burns the difference as heat:

```
P_dissipated = (V_in − V_out) × I_load
```

Dropping 12 V to 5 V at 500 mA wastes 3.5 W. That's a hot part.

**Dropout voltage** is the minimum `V_in − V_out` needed to regulate at
all. This is exactly the constraint behind your project's power note:
the Nano's `VIN` pin feeds an onboard linear regulator that needs
roughly 6.5–7 V to produce a stable 5 V. **A 3.7 V cell cannot drive
`VIN`.** That's not a design preference, it's a dropout-voltage fact.

### The 5V-pin question, worked honestly

Your project feeds the battery to the Nano's `5V` pin instead, bypassing
the regulator. That works — but it means the ATmega328P is running at
whatever the cell is, 3.0–4.2 V over a discharge cycle, not at 5 V.

Now go and read the ATmega328P datasheet's speed grades. You'll find
something like: up to 10 MHz guaranteed at 2.7 V, up to 20 MHz at 4.5 V,
with a linear derating between them. Interpolating at 3.7 V gives a
guaranteed maximum around 15.6 MHz — and **your Nano is clocked at
16 MHz.** You are marginally outside the guaranteed operating region,
and further outside it as the cell discharges.

In practice it usually runs fine. But "usually" is doing real work in
that sentence: out-of-spec operation is exactly the kind of thing that
works on the bench at room temperature and fails when the board is cold,
or when the motor kicks in and the supply momentarily sags. **This is a
genuine open item on your build**, and the fix options are: accept and
test at temperature extremes, add a boost converter to a solid 5 V,
switch the board to an 8 MHz bootloader, or move to a 3.3 V-native MCU.
Worth raising in `PURCHASE_LIST.md` alongside the `R3` item.

### Switching regulators

A buck (step-down) or boost (step-up) converter switches an inductor
rapidly and uses `v = L·di/dt` to move energy, rather than burning the
difference. Efficiencies of 85–95% are normal.

Learn: the buck and boost topologies, duty-cycle-to-voltage relationship
(`V_out = D·V_in` for a buck, `V_out = V_in/(1−D)` for a boost),
continuous vs discontinuous conduction, and why switching supplies are
noisy — the fast edges that make them efficient also make them radiate.

### Battery charging, and your 4C hazard

**CC/CV charging** is the standard for lithium cells: constant current
until the cell reaches 4.2 V, then hold 4.2 V constant while the current
tapers, and stop at roughly 10% of the initial rate.

The TP4056 sets the constant-current phase with a single resistor:

```
I_BAT = 1200 × (V_PROG / R_PROG),   V_PROG = 1.0 V
```

So the stock `R3 = 1.2 kΩ` gives **1000 mA**. Your cell is 250 mAh, so
that is **4C** — four times its own capacity per hour. Manufacturer
guidance for pouch cells like yours is 0.5C normal, 1C ceiling.

**What "4C" physically does:** excessive charge current drives lithium
plating on the anode instead of proper intercalation. Plated metallic
lithium forms dendrites, dendrites can bridge the separator, and a
bridged separator is an internal short in a cell containing a flammable
electrolyte. This is not "the battery wears out faster." It is the
actual mechanism of lithium fires.

Solving `1200/R = 0.125` for 0.5C gives `R = 9.6 kΩ`, hence the ~10 kΩ
recommendation already in your notes (10 kΩ gives 120 mA, a hair under
0.5C — a good conservative choice).

**Also learn:** C-rate notation, why lithium chemistries need protection
circuits at all, over-discharge damage (below ~2.5 V a lithium cell is
permanently harmed), and what a protection IC actually protects against.
Your cell reportedly has built-in protection — verify that, because
"protected" pouch cells and bare ones look identical.

---

## 2.7 Noise, grounding, and why real circuits misbehave

The part most courses skip and every practising engineer needs.

- **Noise sources:** thermal (Johnson) noise, shot noise, flicker (1/f)
  noise. Thermal noise sets the floor: `v_n = √(4kTRB)`. A 1 MΩ resistor
  at room temperature over 10 kHz of bandwidth gives ~13 µV RMS — which
  is why high-impedance nodes are noisy nodes.
- **Ground loops.** Two paths to ground at different potentials inject
  the difference into your signal. Star grounding is the usual fix — and
  it's exactly what your soldering plan's "two star joints" for the power
  rails is doing.
- **Decoupling capacitors.** A 100 nF ceramic right at each IC's supply
  pin supplies the fast current transients that the wires from the
  regulator are too inductive to deliver. This is the most-omitted and
  most-important component on a beginner's board. Your Nano has them;
  anything you build on protoboard needs them added deliberately.
- **Bypass vs bulk.** Small ceramics handle fast transients, larger
  electrolytics handle slower bulk demand. You want both. **On your
  build:** the motor switching on is a fast current step from a battery
  with real internal resistance, and that step will pull the whole rail
  down for a moment. A bulk capacitor across the supply near the motor
  driver is the standard fix, and it's worth adding before you blame the
  MCU for resetting.

---

## Do this — labs for Module 02

1. **Diode curve in LTspice.** Sweep a 1N4148's forward voltage from 0
   to 1 V and plot current on a log axis. Confirm the ~60 mV/decade
   slope. You have now seen the Shockley equation with your own eyes.
2. **Your own motor driver, measured.** With your existing hardware:
   measure the actual motor current, measure `V_CE` while the transistor
   is on (should be ~0.2 V if saturated, much higher if not), and try
   each of 220 Ω / 470 Ω / 1 kΩ base resistors. Confirm all three
   saturate and that base current scales as your calculation predicts.
3. **Watch the flyback spike.** If you can borrow an oscilloscope —
   a school lab, a maker space, or a $25 USB scope — look at the
   collector node with and without the 1N4148 fitted. The difference is
   dramatic and you will never forget it. No scope? Simulate it in
   LTspice with a 10 mH inductor as the motor; the spike is just as
   visible.
4. **Op-amp derivations.** On paper, derive the inverting and
   non-inverting gain formulas from the two golden rules. Then build
   both in Falstad and confirm.
5. **The `R3` calculation, end to end.** Compute the charge current for
   1.2 kΩ, for 10 kΩ, and for the resistor that would give exactly
   0.5C. Then compute the TP4056's own power dissipation while charging
   at each rate (`P ≈ (V_in − V_bat) × I_chg`) and notice that the
   4C case is also a thermal problem for the chip, not only for the cell.

---

## Self-check — closed book

1. Why is an LED's current so sensitive to voltage, and what does the
   series resistor actually fix?
2. What distinguishes a BJT in saturation from one in the active region,
   and which do you want for a switch?
3. Size a base resistor for a BJT switching 200 mA from a 3.3 V GPIO.
4. Why does a MOSFET rated `R_DS(on)` at `V_GS = 10 V` behave badly when
   driven from a 5 V pin?
5. State the op-amp golden rules and derive the non-inverting gain.
6. What is gain-bandwidth product, and why does it limit a 1 MHz op-amp
   to 10 kHz at a gain of 100?
7. A linear regulator drops 9 V to 5 V at 300 mA. How much heat?
8. Why can't a 3.7 V cell power the Nano through `VIN`?
9. Explain, mechanistically, why charging a 250 mAh cell at 1 A is
   dangerous rather than merely fast.
10. What is a decoupling capacitor for, and why must it be physically
    close to the chip?

---

## Resources for this module

- **Razavi, *Fundamentals of Microelectronics*** — and his free lecture
  series. The clearest explanation of semiconductor devices available.
- **Sedra & Smith, *Microelectronic Circuits*** — the standard reference.
  Dense; use it as a lookup once Razavi has given you the picture.
- **The Art of Electronics, Ch. 1–4** — practical, opinionated, and full
  of the judgement calls textbooks omit.
- **All About Circuits Volume III (Semiconductors)** — free, and a
  reasonable first pass.
- **LTspice** — essential from here on. Falstad is too idealised for
  semiconductor work.
- **The ATmega328P datasheet** — read the electrical characteristics and
  speed-grade sections specifically. Datasheet-reading is a skill, and
  this is the datasheet you already have a reason to read.
