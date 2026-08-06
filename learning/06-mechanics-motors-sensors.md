# Module 06 — Mechanics, actuators, sensors

**Prereqs:** derivatives (§2) and integrals (§3) for dynamics; ODEs (§5)
for the motor model; Module 05 to close a loop around any of it.
**Time:** ~12 weeks.
**Unlocks:** the "mecha" in mechatronics. Everything that moves.

---

## Why this matters for your wristband

Three parts of your build are pure mechanical/actuator engineering and
you've been treating them as black boxes:

1. **The vibration motor.** It's an *eccentric rotating mass* motor, and
   its output force goes as the **square** of its speed. Your PWM duties
   of 140 / 200 / 255 therefore do **not** map linearly to felt
   intensity, and there's a minimum duty below which it doesn't spin at
   all. §6.5 makes this precise, and it directly affects your
   `HapticMapper` tuning.
2. **The enclosure.** A 3D print is an anisotropic material with a weak
   axis along the layer lines, and your strap-tunnel corners are stress
   concentrators. §6.2 says what to do about it.
3. **The ToF sensor.** Measuring 1 m of range means timing a 6.7 ns
   round trip. §6.7 explains how a $3 part manages that, and what
   failure modes fall out of the method.

---

## Part A — Mechanics

### 6.1 Statics

The study of things that aren't accelerating. `ΣF = 0` and `ΣM = 0`.

- **Free-body diagrams.** Isolate the body, draw every force acting on
  it, solve. This is a *discipline*, not a technique, and drawing them
  properly is 80% of getting statics problems right.
- Moments and torque: `M = F × d`. The perpendicular distance is what
  counts.
- Types of support and the reactions each produces.
- Trusses (method of joints, method of sections), friction, centroids.

### 6.2 Materials and strength

What you need to not have parts break.

- **Stress** `σ = F/A`, **strain** `ε = ΔL/L`, and Hooke's law
  `σ = E·ε` with `E` the Young's modulus.
- Yield strength vs ultimate strength; elastic vs plastic deformation.
- **Factor of safety** = ultimate strength / working stress. Pick it
  deliberately, and pick it higher for anything worn on a body.
- Beam bending, second moment of area, and why an I-beam is shaped that
  way (material far from the neutral axis contributes as the square of
  the distance).
- **Stress concentration at corners.** A sharp internal corner
  multiplies local stress by a factor of 2–3 or more. **Fillets are not
  cosmetic.**

**Applied to `enclosure.scad`:** your strap-tunnel openings are internal
corners in a part that will be repeatedly loaded by a wrist strap. Two
concrete actions: add fillets to the tunnel corners, and orient the
print so the layer lines don't run parallel to the tension direction.

**3D printing specifically:** FDM parts are strongly **anisotropic** —
typically 20–50% weaker across layers than along them, because
layer-to-layer bonding is thermal fusion rather than bulk material. The
design rule is: *identify the direction of maximum tensile stress, then
orient the print so layers are perpendicular to it.* Getting this wrong
is the single most common reason a printed part snaps.

### 6.3 Kinematics and dynamics

**Kinematics** — motion without asking what caused it. Position,
velocity, acceleration, and their rotational counterparts (θ, ω, α).
This is just Module 00 §2–§3 applied to motion.

**Dynamics** — motion and its causes.

```
Linear:      F = m·a
Rotational:  τ = J·α          (J = moment of inertia)
```

- **Moment of inertia** is rotational mass — it depends on how mass is
  *distributed*, not just how much there is. `J = ∫r² dm`. For a solid
  disc, `J = ½mr²`.
- **Energy methods:** kinetic `½mv²` and `½Jω²`, potential `mgh`,
  work-energy theorem. Often much faster than force analysis.
- **Momentum and impulse**, especially for impacts.
- **Vibration:** the mass-spring-damper `m·ẍ + c·ẋ + k·x = F`. Natural
  frequency `ω_n = √(k/m)`, damping ratio `ζ = c/(2√(km))`.

**Notice what just happened.** That mass-spring-damper equation is
*identical in form* to the RLC circuit from Module 01 §1.10 and to the
generic second-order system from Module 05 §5.3. Mass ↔ inductance,
damping ↔ resistance, spring ↔ 1/capacitance. **This is why one
mathematical toolkit serves all three of your fields**, and it's the
best argument there is for learning the math properly once instead of
learning three sets of special cases.

---

## Part B — Actuators

### 6.4 The DC motor model — the most useful model in mechatronics

A brushed DC motor is an electrical system and a mechanical system
coupled through two constants:

```
Electrical:  V = i·R + L·(di/dt) + K_e·ω        ← K_e·ω is the back-EMF
Mechanical:  J·(dω/dt) = K_t·i − b·ω − τ_load
```

- `K_e` (V·s/rad) — **back-EMF constant**. A spinning motor generates
  voltage opposing the supply. This is the motor being a generator, and
  it's what limits its own speed.
- `K_t` (N·m/A) — **torque constant**. Torque is proportional to current,
  not to voltage. Say that back to yourself; it's the fact people get
  wrong most often.
- **In SI units, `K_t = K_e` numerically.** Not a coincidence — it falls
  out of energy conservation.

**Two consequences worth internalising:**

1. **Current means torque.** If you want to control force, control
   current. This is why serious motor drivers have current sensing and
   why "torque mode" exists.
2. **A stalled motor draws stall current**, because `ω = 0` means no
   back-EMF, so only `R` limits it. Stall current can be 5–10× running
   current, and it's the number that sizes your driver, your fuse, and
   your battery — never the running current.

**The torque-speed curve.** In steady state, ignoring `L` and friction:

```
τ = τ_stall · (1 − ω/ω_no-load)

τ_stall = K_t·V/R          ω_no-load = V/K_e
```

A straight line from stall torque at zero speed to no-load speed at zero
torque. **Maximum mechanical power occurs at exactly half of each**,
where `P_max = τ_stall · ω_no-load / 4`. That single fact tells you where
to operate a motor and is worth more than any amount of datasheet
browsing.

### 6.5 Your vibration motor, properly

Your 10×3 mm motor is an **ERM** — eccentric rotating mass. A small
off-centre weight spins, and the resulting centripetal force shakes the
housing:

```
F = m · e · ω²
```

where `m` is the eccentric mass, `e` its offset, `ω` the rotation rate.

**Three consequences that matter for `HapticMapper`:**

1. **Force goes as ω², not ω.** Since speed is roughly proportional to
   average applied voltage (above the startup threshold), **felt
   intensity is roughly proportional to duty squared.** Your duties of
   140 / 200 / 255 are ratios of 0.55 / 0.78 / 1.00 in voltage, but
   roughly **0.30 / 0.62 / 1.00 in force**. The perceived steps between
   your zones are much less even than the duty numbers suggest — the
   Medium zone is far weaker relative to Critical than 140-vs-255 looks.
   If you want perceptually even steps, take square roots.
2. **There is a minimum startup duty.** Static friction means the motor
   needs meaningfully more voltage to *start* than to keep running.
   Below that, it silently does nothing — and your Medium zone at duty
   140 is a plausible candidate for being near that edge, especially at
   3.7 V from a battery rather than 5 V from USB. **Measure your motor's
   startup duty on battery power.** A common firmware trick is a brief
   full-duty "kick" at the start of every pulse, then dropping to the
   target duty.
3. **Frequency and amplitude are coupled and cannot be set
   independently.** In an ERM, one knob (speed) sets both. This is a
   genuine design limitation of the actuator, and it's exactly why your
   design encodes information in *pulse patterns* rather than in
   amplitude alone — which was the right call, and now you know why.

*(The alternative actuator, an LRA — linear resonant actuator — runs at
a fixed resonant frequency with independently controllable amplitude and
much faster rise time. It needs an AC drive rather than PWM. Worth
knowing about if you ever revise the haptics.)*

### 6.6 Other actuators

- **Stepper motors** — move in discrete steps, open-loop positioning with
  no encoder. Full/half/microstepping. **They lose steps silently under
  overload**, which is their defining failure mode.
- **Hobby servos** — a DC motor, gearbox, potentiometer and closed-loop
  controller in one box, commanded by a pulse width (1–2 ms in a 20 ms
  frame). A complete closed-loop control system you can buy for a dollar,
  and worth dissecting once you've done Module 05.
- **BLDC** — brushless, needs electronic commutation and rotor position
  sensing (Hall sensors or sensorless back-EMF detection). Higher power
  density, longer life.
- **H-bridges** — four switches to drive a motor in both directions.
  Understand **shoot-through** (both switches on one side conducting at
  once, shorting the supply) and why dead-time insertion exists.

**Actuator sizing** is its own skill: compute the required torque
including acceleration (`τ = J·α`), friction, and gravity; add margin;
then check the *thermal* limit, because continuous torque is usually
limited by heat rather than by magnetics.

### 6.7 Gearing

```
τ_out = N · τ_in · η        (η = efficiency)
ω_out = ω_in / N
J_reflected = J_load / N²   (load inertia seen at the motor shaft)
```

That last line is the one people miss and the one that matters most for
control. **A gearbox divides the reflected load inertia by N².** A 50:1
gearbox makes the load 2500× easier for the motor to accelerate, which
is why geared motors are so much easier to control than direct-drive
ones.

The costs: **backlash** (lost motion on direction reversal, which
produces limit cycles in a position loop and is a genuine control
problem) and reduced efficiency.

---

## Part C — Sensors and measurement

### 6.8 Sensor characteristics — the vocabulary

Learn these precisely; they're what datasheets are written in.

| Term | Meaning |
|---|---|
| Range | min to max measurable |
| Resolution | smallest detectable change |
| **Accuracy** | closeness to the true value |
| **Precision** | repeatability — *not* the same as accuracy |
| Sensitivity | output change per input change |
| Linearity | deviation from a straight-line fit |
| Hysteresis | different reading approaching from above vs below |
| Drift | slow change over time or temperature |
| Bandwidth | how fast a change it can follow |

**Accuracy versus precision is the distinction to get right.** A sensor
reading 1050 mm every time for a 1000 mm target is precise but
inaccurate — and that error is *systematic*, so it can be calibrated
out. A sensor scattering 950–1050 mm randomly is accurate on average but
imprecise, and only averaging helps. **Different problems, different
fixes**, and confusing them wastes weeks.

### 6.9 Common sensor types

- **Potentiometers** — a voltage divider driven by position. Simple,
  absolute, wears out.
- **Encoders** — quadrature A/B channels; the phase relationship gives
  direction, and counting all four edges of both channels ("×4
  decoding") quadruples resolution. Incremental encoders need a homing
  move; absolute encoders don't.
- **Strain gauges** — resistance changes with strain. The change is tiny
  (parts in 10⁴), so they're read with a **Wheatstone bridge**, which
  nulls out the large baseline and leaves the small difference to be
  amplified. Bridges also cancel temperature drift when the arms are
  matched — an elegant piece of analog design worth studying for its own
  sake.
- **IMUs** — accelerometers (measure specific force, so they read gravity
  too) and gyroscopes (measure angular rate, so they drift when
  integrated). Their errors are complementary, which sets up §6.11.
- **Distance sensors** — ultrasonic (cheap, wide beam, fooled by soft
  surfaces), IR triangulation (nonlinear output, ambient-light
  sensitive), and time-of-flight.

### 6.10 How your ToF sensor actually works

Light travels at `3 × 10⁸ m/s`. A target at 1 m means a 2 m round trip:

```
t = 2 m / 3×10⁸ m/s = 6.7 ns
```

To resolve 10 mm you need to time to about **67 picoseconds**. No cheap
microcontroller can do that with a stopwatch.

**So the VL53L0X doesn't.** It uses an array of SPADs (single-photon
avalanche diodes), fires many pulses, and builds a *histogram* of photon
arrival times, extracting the peak statistically. Precision comes from
averaging over thousands of photons, not from a single fast measurement.

**Every quirk you've met follows directly from that method:**

- **More integration time = better range and precision, worse update
  rate.** That's the entire content of the "long range preset vs default
  profile" tradeoff documented in your `.ino` — more photons per
  measurement, fewer measurements per second, and more susceptibility to
  ambient photons.
- **Ambient IR is the noise floor.** Sunlight is full of exactly the
  photons the sensor counts, which is why ToF sensors degrade badly
  outdoors — a real failure mode for a navigation aid, and one that
  belongs in your `README.md` failure-modes list if it isn't there.
- **Target reflectivity changes effective range**, because it changes
  how many photons come back. A dark cloth wall reflects far less than a
  white one and will read as "nothing there."
- **The signal rate limit** (`setSignalRateLimit`) is a confidence
  threshold on the histogram: raise it and you reject weak/uncertain
  returns, lower it and you accept more distant/darker targets at the
  cost of spurious readings. That's why the long-range preset lowers it
  to 0.1, and why it makes readings jumpier.
- **Field of view is a cone, not a ray** (~25° for the VL53L0X). It
  returns the *strongest* return in that cone, not necessarily the
  nearest object. **For a navigation aid this is a safety-relevant
  limitation** — a thin pole or a table edge inside a wide cone
  containing a strong wall return can be missed entirely.

That last point is the kind of thing that belongs in your outreach
conversations and any competition writeup, and it comes straight out of
understanding the measurement principle rather than the API.

### 6.11 Signal conditioning and estimation

**Getting a signal into a microcontroller cleanly:**

- **Amplification** to use the ADC's full range. An instrumentation
  amplifier for differential/bridge signals.
- **Anti-alias filtering** — in analog, before the ADC, always
  (Module 04 §4.7).
- **ADC resolution.** Your Nano's 10-bit ADC over a 5 V reference gives
  `5/1024 = 4.88 mV` per count. Nothing you do in software recovers
  detail below that. Using a lower `AREF` improves resolution
  proportionally when your signal is small.
- **Calibration.** Two-point for offset and gain; polynomial for
  nonlinear sensors. Store the coefficients in EEPROM.

**Sensor fusion:**

- **Complementary filter** — the cheap, excellent solution.
  Low-pass one sensor, high-pass another, add them:

  ```
  angle = α·(angle + gyro·dt) + (1−α)·accel_angle
  ```

  Trust the gyro short-term (accurate but drifts) and the accelerometer
  long-term (noisy but drift-free). Two lines of code, runs on anything,
  and gets you 90% of a Kalman filter's benefit for 5% of the effort.
  **Start here, always.**

- **Kalman filter** — the optimal linear estimator under Gaussian noise.
  Predict the state from a model, then correct with a measurement,
  weighting each by its covariance. It's Bayes' rule (Module 00 §9) plus
  linear algebra (§8), and nothing more mysterious than that. The
  **extended Kalman filter** linearises a nonlinear model at each step —
  the same linearisation move you met in Module 02 §2.4 and Module 05
  §5.9, for the third time.

---

## Do this — labs for Module 06

1. **Torque-speed curve, measured.** Take any small DC motor. Measure
   no-load speed and stall current. Compute `K_e`, `K_t`, and `R`.
   Plot the predicted torque-speed line. This turns the model in §6.4
   from symbols into numbers about a real object on your desk.
2. **Characterise your vibration motor.** Sweep PWM duty from 0 to 255
   in steps. Find: the duty at which it first starts from rest, the duty
   at which it *stops* once running (lower — that's hysteresis, §6.8),
   and the subjective intensity at each step. Do it on 5 V USB and again
   on the 3.7 V battery. **Then use the results to re-pick the three
   duty values in `HapticMapper.h`, compensating for the ω² law.** This
   is a real, testable improvement to your project, and it's the best
   single lab on this page.
3. **Simulate the motor ODEs.** Implement §6.4's two coupled equations
   in Python and plot the step response. Then close a PID loop around
   speed (Module 05 §5.7) and tune it in simulation before touching
   hardware.
4. **Encoder decoding.** Write quadrature decoding on the Nano using pin
   change interrupts. Confirm ×4 counts per cycle and correct direction
   sign. This exercises Module 03 §3.13 (interrupts, `volatile`, atomic
   access on a 16-bit counter) in one small program.
5. **Complementary filter on an IMU.** An MPU6050 is cheap and available
   locally. Fuse accelerometer and gyro into a tilt angle. Plot gyro
   drift over a minute, accel noise, and the fused result. Seeing the
   three traces together is what makes fusion click.
6. **Enclosure stress test.** Print two copies of a strap lug from
   `enclosure.scad` in different orientations. Load both until they
   break. Measure the difference. You will never guess a print
   orientation carelessly again.

---

## Self-check — closed book

1. Draw a free-body diagram for a wrist-worn pod held by a strap under
   tension, and write the equilibrium equations.
2. Why does print orientation change an FDM part's strength, and how do
   you choose it?
3. Why is a sharp internal corner a problem, and what's the fix?
4. What physically produces back-EMF, and what does it limit?
5. Why is motor torque proportional to current rather than voltage?
6. Why is stall current, not running current, what sizes your driver?
7. At what fraction of no-load speed does a DC motor deliver maximum
   power?
8. A 20:1 gearbox: what happens to torque, speed, and reflected inertia?
9. Why is an ERM motor's felt intensity roughly proportional to the
   square of PWM duty?
10. Distinguish accuracy from precision and give the fix for each kind
    of error.
11. Why can't a $3 ToF sensor time a 6.7 ns flight directly, and what
    does it do instead?
12. Name three ways a VL53L0X can report "nothing there" when something
    is there.
13. Write the complementary filter equation and say which sensor is
    trusted at which timescale.

---

## Resources for this module

- **Alciatore & Histand, *Introduction to Mechatronics and Measurement
  Systems*** — the closest thing to a single textbook for this whole
  module.
- **Hibbeler, *Engineering Mechanics: Statics and Dynamics*** — the
  standard mechanics text, with enormous problem sets.
- **Lynch & Park, *Modern Robotics*** — free PDF (modernrobotics.
  northwestern.edu) plus free video lectures. The right next step if
  kinematics and robot arms interest you.
- **The VL53L0X and VL53L1X datasheets and application notes** — ST's
  documentation on ranging profiles and ambient-light performance is
  genuinely good, and you have the hardware to test every claim in it.
- **Pololu's and SparkFun's motor and encoder tutorials** — practical,
  correct, and written for exactly the level this module targets.
