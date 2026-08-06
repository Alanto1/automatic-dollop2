# The project ladder

Theory you can't use isn't theory, it's trivia. Each phase of the plan
ends with a build that would have been impossible at the start of it.
**These are the real exams.** If you can't build the project, you didn't
learn the phase — regardless of how many lectures you watched or
problems you solved.

Everything here is chosen against three constraints: parts obtainable in
Almaty (see `../assistive-tech-device/PURCHASE_LIST.md` for the shops
you've already mapped), total cost under a few thousand tenge per
project, and no test equipment beyond a multimeter — with notes where a
scope or logic analyser would help.

---

## Track A — the phase gates

### Project 1 — Component curve tracer
**Gate for Phase 1** · after Module 01 Part A + Module 03 Part A

Build an instrument that plots a component's current-voltage curve.

**How it works.** Use PWM through an RC low-pass as a crude DAC to sweep
a voltage from 0 to 5 V. Put the device under test in series with a
known sense resistor. Measure the voltage on both sides of the sense
resistor with two ADC channels; the difference over the resistance gives
current, and one of the readings gives the device's voltage. Print
pairs over serial, plot in Python.

**BOM:** Nano (have it), a handful of resistors, 1 µF capacitor, and
whatever you want to test — a resistor, an LED, a 1N4148, the
base-emitter junction of your 2N2222.

**Theory it proves:**
- Ohm's law and the voltage divider, used to *measure* rather than to
  set (Module 01 §1.3)
- Thevenin — you must reason about the ADC loading your divider
  (§1.4)
- RC as a low-pass and as an averager (§1.8, and Module 03 §3.12)
- ADC resolution as a real limit on what you can see (Module 06 §6.11)
- The diode's exponential I-V, observed with your own hardware
  (Module 02 §2.2)

**You're done when:** you've plotted a resistor's curve and it's a
straight line whose slope equals `1/R`; you've plotted a 1N4148's curve
and it's the Shockley exponential; and you can state your instrument's
measurement resolution in millivolts and milliamps *and explain what
sets each*.

---

### Project 2 — Power and driver board for the wristband
**Gate for Phase 2** · after Module 02 + Module 03 Part C

Design and build the power stage your wristband is currently missing.
**This closes real open items on your actual project**, which is the
best possible motivation.

**What it does:**
1. Boost the 3.7 V cell to a solid 5 V, so the ATmega328P isn't running
   at 16 MHz outside its guaranteed voltage range (Module 02 §2.6 —
   this is a live, unresolved issue on your build).
2. Drive the motor from a logic-level MOSFET instead of the 2N2222,
   with a properly sized gate resistor and flyback diode.
3. Monitor battery voltage through a divider into an ADC channel, and
   fire a distinct haptic pattern below a threshold — which also forces
   you to design that pattern into `HapticMapper` as a new state.
4. Add bulk and decoupling capacitance sized for the motor's switching
   transient (§2.7).

**BOM:** MT3608 or similar boost module (or build one), a logic-level
MOSFET (2N7000 for this current, or an IRLZ44N), 1N4148, resistors, a
100 nF ceramic and a 100 µF electrolytic.

**Theory it proves:** MOSFET gate drive and why logic-level matters
(§2.3); switching versus linear regulation and dropout (§2.6); flyback
and inductive kick (§2.2); ADC scaling and divider design (Module 06
§6.11); decoupling and supply transients (§2.7).

**You're done when:** the wristband runs from the battery with a stable
5 V rail; you can show with a multimeter that the rail doesn't sag more
than a specified amount when the motor kicks in; and you've measured
your actual runtime and compared it to the figure you calculate from
average current (Module 00 §3 — battery life is an integral).

**Write it up in `PURCHASE_LIST.md` and `README.md`.** This is real work
on the real device, not a practice exercise.

---

### Project 3a — PID temperature controller
**Gate for Phase 3, part one** · after Module 05

The best first control project there is, because the dynamics are slow
enough to *watch*.

**What it is:** a resistor or small heater element, a thermistor or
DS18B20, and PWM through a MOSFET. Hold a setpoint temperature.

**Why it's the right first one:** the plant is roughly first-order with
dead time, the time constants are seconds to minutes so you can see
every effect happening in real time on a serial plot, and nothing moves
fast enough to break.

**Do all of this, in order:**
1. **Model it first.** Apply a step of PWM, log the response, fit a
   first-order-plus-dead-time model. You now have `K`, `τ`, and `L` for
   a real physical object.
2. **P only.** Observe the steady-state error. *Measure* it and check
   it against the theory (Module 05 §5.4).
3. **Add I.** Watch the error go to zero. Then deliberately cause
   windup by setting an unreachable setpoint, and watch the overshoot
   when you bring it back. Then add the clamping from §5.7 and confirm
   it's gone.
4. **Add D.** Watch it damp the response — and watch it amplify sensor
   noise. Add the derivative filter and confirm.
5. **Tune with Ziegler–Nichols**, then tune by hand, and compare.

**You're done when:** you can produce a plot of setpoint versus
measurement showing overshoot and settling time, and read `ζ` and `ω_n`
off it that match your tuning.

### Project 3b — Closed-loop motor speed controller
**Gate for Phase 3, part two**

The same loop with fast dynamics, which is a genuinely different
engineering problem.

**What it is:** a small DC motor, a quadrature encoder (or an IR
reflective sensor and a striped disc as a cheap tachometer), a MOSFET or
H-bridge, PID at a fixed timer tick.

**The new problems fast dynamics bring:**
- Sample rate now matters (Module 05 §5.7). Run it too slow and watch
  the phase margin vanish.
- Encoder counting must be interrupt-driven, with `volatile` and atomic
  access on a multi-byte counter (Module 03 §3.13).
- The derivative term now has real noise to amplify.
- Load disturbance rejection becomes testable: pinch the shaft and
  watch the controller fight back.

**You're done when:** the motor holds a commanded speed under a load
disturbance you apply by hand; you can plot the step response and
identify overshoot, settling time, and steady-state error; and you can
show the difference between P, PI, and PID on the same plot.

---

### Project 4 — pick a specialisation
**Phase 4** · one of:

- **PCB design.** Take the Project 2 power board into KiCad, route it,
  and get it made. Learn schematic capture, footprints, design rules,
  ground planes, and why trace width matters (it's a current-density and
  thermal question you can now calculate).
- **FPGA.** An iCEBreaker or TinyFPGA with the open Yosys/nextpnr
  toolchain. Implement a UART, then a VGA generator, then a small CPU.
  This is Module 03 Part A made physical.
- **RTOS.** Port the wristband firmware to FreeRTOS on an ESP32 or
  STM32. Sensor task, haptics task, battery task, proper priorities.
  You'll meet priority inversion for real.
- **DSP.** Real-time FFT on an STM32 or ESP32: audio in, spectrum out.
  Module 04 made physical.
- **Robot arm.** Three or four servos, forward and inverse kinematics,
  trajectory planning. Module 06 plus linear algebra.
- **Analog design.** A discrete-transistor audio amplifier, designed from
  the biasing up rather than copied. Harder than it sounds and it will
  teach you more about Module 02 than any amount of reading.

---

## Track B — improvements to the wristband, as theory unlocks them

Your existing project is a live testbed. Each of these is a small,
committable change that a specific module makes possible. Do them as you
go — they keep the theory attached to something real.

| After | Change | Why the theory is needed |
|---|---|---|
| Module 03 §3.5 | **Hysteresis at zone boundaries.** Different thresholds for entering and leaving a zone. | An FSM diagram makes the chattering transition obvious. A reading hovering at exactly 1000 mm currently oscillates between Far and Medium. |
| Module 04 §4.9 | **Median-of-3 outlier filter**, and an explicit decision *not* to use a heavy EMA. | You need the lag calculation to know that α = 0.2 costs 314 mm of position — wider than the whole Critical zone. |
| Module 06 §6.5 | **Re-pick the three PWM duty values** for perceptual evenness, and add a startup kick. | Felt intensity goes as duty *squared*, and there's a minimum starting duty that's higher on battery than on USB. |
| Module 03 §3.12 | **Move PWM to ~31 kHz.** | Out of the audible band, and you can show it doesn't disturb `millis()` because it's Timer1, not Timer0. |
| Module 01 §1.9 | **Fix the I2C pull-ups**, or drop to 100 kHz. | Rise-time budget at 400 kHz with real bus capacitance. |
| Module 02 §2.6 | **Resolve the `R3` charge-current item.** | You already know it's wrong; after §2.6 you know *mechanistically* why 4C is a fire risk and not just wear. |
| Module 06 §6.10 | **Document the sensor's real failure modes** in `README.md`: cone field of view, dark-target range loss, ambient IR outdoors. | These follow from how SPAD histogramming works, and they are safety-relevant for the actual users. |
| Module 05 §5.9 | **Compute the reaction-time margin** and check the Near threshold against it. | Human reaction time plus sampling plus filter lag is a transport delay, and at 1.4 m/s it consumes most of the 600 mm Near zone. |

Every row is a commit. Several of them are things you'd want to be able
to explain at a Jugend forscht table, and "I computed the lag budget and
chose a median filter over an EMA because the EMA cost more positional
error than my entire critical zone" is a much stronger answer than "I
added some smoothing."

---

## Track C — the capstone

Once Phase 3 is done, build something that needs **all three** fields at
once. Candidates in rising order of difficulty:

1. **Self-balancing two-wheel robot.** IMU + complementary filter +
   cascaded PID (angle loop inside a position loop) + motor drivers.
   Uses every module here.
2. **Reaction-wheel inverted pendulum.** Harder control, simpler
   mechanics. A genuinely impressive demo.
3. **Ball-and-beam.** The classic control-lab plant. Needs your ToF
   sensor — which you already own — as the position feedback.
4. **A v2 of the wristband** with multiple sensors, sensor fusion, an
   LRA driven properly, a designed PCB, and a real power budget. The
   version you'd build if you'd known all this at the start.

Number 4 is the one to aim at. It closes the loop on the whole plan:
the same project, rebuilt with two years of theory behind it, and the
difference between the two versions is the clearest possible measure of
what you learned.

---

## How to document a project

Get in the habit now; it's what turns a build into evidence you can show
a competition judge or an admissions committee.

For each project keep, in the repo:

1. **The question.** What did you not know how to do before this?
2. **The model.** The equations you used, with your actual numbers.
3. **The prediction.** What the theory said would happen, written down
   *before* you tested.
4. **The measurement.** What actually happened, with data.
5. **The discrepancy.** Where prediction and measurement disagreed, and
   why. **This is the most valuable section and the one everyone
   skips.** Your existing `CLAUDE.md` session log already does this
   well — the GY-53 `PS` writeup is exactly the right form. Keep it up.
6. **What you'd do differently.**
