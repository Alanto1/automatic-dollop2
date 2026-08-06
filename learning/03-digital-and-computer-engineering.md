# Module 03 — Digital logic and computer engineering

**Prereqs:** algebra (§1). Nothing else — this track is independent of
calculus, which is why it can run in parallel from day one.
**Time:** ~14 weeks across the three parts.
**Unlocks:** embedded systems, FPGA work, and understanding what your
Nano is actually doing.

---

## Why this matters for your wristband

You already write firmware that works. This module is about the layer
underneath it — and it will change how you write that firmware.

Three things in your existing code that this module explains:

1. **`HapticMapper` is a finite state machine.** Not "sort of like" one —
   it literally is one. State is (zone, pulse-phase), transitions are
   driven by distance and time, output is the motor command. Once you
   have the FSM vocabulary you'll draw it as a state diagram, spot the
   transitions you didn't test, and design the next one deliberately.
2. **`now - lastDebugPrintMs >= kDebugPrintIntervalMs`** is a
   number-representation trick that survives timer rollover. Most people
   write it without knowing why it works. §3.2 explains it.
3. **`while (true) {}` on sensor init failure** is a fail-safe design
   decision with a hardware alternative (a watchdog timer) that you
   currently don't use. §3.14 covers when each is right.

---

## Part A — Digital logic

### 3.1 Boolean algebra and gates

Boolean algebra is algebra over `{0, 1}` with AND, OR, NOT. Learn:

- The basic identities, distribution, and absorption.
- **De Morgan's laws** — `NOT(A AND B) = NOT A OR NOT B`, and the dual.
  These get used constantly, both in hardware and in refactoring
  conditionals in C++.
- **Functional completeness:** NAND alone can build every other gate.
  So can NOR. This is why real chips are built from NAND gates, and it's
  the premise of the Nand2Tetris course.
- Truth tables → sum-of-products → simplification with Karnaugh maps.
  K-maps stop being practical above about 5 variables, at which point
  synthesis tools take over — but doing them by hand for a few weeks
  builds the intuition that reading synthesised logic never will.

### 3.2 Number representation

More important than it looks, and the source of a large fraction of real
embedded bugs.

- Binary, hex, and fluent conversion. Hex exists because one hex digit
  is exactly four bits.
- **Two's complement** for signed integers: negate by inverting all bits
  and adding one. The reason it's universal is that *the same adder
  circuit works for signed and unsigned numbers* — no separate hardware.
- **Overflow and wraparound.** Adding 1 to `0xFF` in eight bits gives
  `0x00`. Unsigned arithmetic in C is defined to wrap modulo 2ⁿ.

**Your millis() idiom, explained.** `millis()` returns a `uint32_t` that
overflows after 2³² ms ≈ **49.7 days**. The naive check
`if (now > last + interval)` breaks catastrophically at that rollover.
But your code writes:

```cpp
if (now - lastDebugPrintMs >= kDebugPrintIntervalMs)
```

Unsigned subtraction wraps modulo 2³² too, so `now - last` gives the
correct *elapsed* time even when `now` has wrapped past zero and `last`
hasn't. The two errors cancel exactly. It's a genuinely elegant piece of
modular arithmetic, it's the correct idiom, and you should be able to
explain why on demand — because the day you write the other version, it
will work perfectly for seven weeks and then fail once.

- **Fixed point vs floating point.** The ATmega328P has no floating-point
  unit; every `float` operation is emulated in software and costs
  hundreds of cycles. Fixed-point arithmetic (integers with an implied
  binary point) is how embedded code does fractional math fast. Your
  `HapticMapper` sensibly uses integer millimetres throughout — that's a
  fixed-point decision, whether or not it was framed that way.

### 3.3 Combinational logic

Circuits whose output depends only on the current inputs.

Build up: multiplexers, decoders, encoders, comparators, half adder →
full adder → ripple-carry adder → carry-lookahead adder → ALU.

**The lesson in the ripple-carry adder:** each bit's carry has to
propagate through the one below it, so an n-bit add takes n gate delays.
That delay is what caps your clock frequency. Carry-lookahead trades
gates for speed by computing the carries in parallel. **This
speed-versus-area tradeoff is the central tension of all digital
design**, and meeting it in the adder is the cleanest possible
introduction.

### 3.4 Sequential logic

Circuits with memory. The whole subject rests on one device.

- **Latch → flip-flop.** A latch is level-sensitive, a flip-flop is
  edge-triggered. The D flip-flop is the workhorse: on the clock edge,
  copy D to Q, then hold it.
- **Registers and counters** are just flip-flops in parallel or in a
  chain.
- **Setup and hold time.** Data must be stable for a window before the
  clock edge (setup) and after it (hold). Violate them and the flip-flop
  goes **metastable** — its output sits between valid levels for an
  unbounded time. This is not a theoretical concern; it's why crossing a
  signal between two clock domains requires a synchroniser, and why the
  button on your breadboard needs debouncing.
- **Maximum clock frequency** follows directly:

  ```
  T_clock ≥ T_clk-to-Q + T_logic + T_setup
  ```

  That inequality is the reason CPUs have a maximum clock speed. It's
  the whole story, at the level that matters.

### 3.5 Finite state machines

An FSM is: a set of states, a transition rule, and an output rule.

- **Moore machine** — output depends only on the current state.
- **Mealy machine** — output depends on state *and* current input. Fewer
  states, but outputs can glitch on input changes.

**Redraw `HapticMapper` as a state diagram before you read further.**
You'll find states `{Far, Medium, Near, Critical}` × `{pulse-on,
pulse-off}`, transitions on distance thresholds and on elapsed time, and
outputs `(motorOn, pwmDuty)`. It's a Moore machine.

Doing this exercise will surface design questions you haven't asked yet:

- What happens on a transition *mid-pulse*? Does the pulse timer reset,
  or continue? (Read your own code and find out — then ask which
  behaviour you actually want on a wrist.)
- Is there hysteresis at the zone boundaries? A reading oscillating
  around exactly 1000 mm will chatter between Far and Medium. **Adding
  hysteresis (different thresholds for entering and leaving a zone) is
  the standard fix**, it's four lines of code, and it's the kind of
  thing an FSM diagram makes obvious and a pile of `if` statements
  hides.

That right there is the practical value of theory: not new capability,
but a lens that makes an existing bug visible.

### 3.6 Hardware description languages

Learn enough Verilog or VHDL to describe combinational and sequential
logic and simulate it. You do not need an FPGA board to start — Icarus
Verilog plus GTKWave, or Verilator, both free, let you write and
simulate on a laptop.

**The mental shift that trips up programmers:** HDL is not sequential
code. `always @(posedge clk)` blocks describe *hardware that exists
simultaneously*, not statements that run in order. Everything happens at
once, every clock cycle. Coming from C++ this feels wrong for about two
weeks and then clicks permanently.

---

## Part B — Computer architecture

### 3.7 The stored-program computer

- **Von Neumann:** one memory holding both instructions and data.
- **Harvard:** separate memories for each.
- **Your Nano is modified Harvard.** The ATmega328P has 32 KB of flash
  for program and 2 KB of SRAM for data, in *separate address spaces*.

That architectural fact has a direct consequence you've probably already
hit: **this is why `PROGMEM` exists.** A string literal normally gets
copied from flash into SRAM at startup, because the CPU's ordinary load
instructions can only address SRAM. On a 2 KB machine, a handful of
debug strings can eat your entire RAM. `PROGMEM` plus `pgm_read_byte()`
uses the special `LPM` instruction to read flash directly, keeping the
data out of SRAM.

Look at your `#if DEBUG_SERIAL` blocks with that in mind: those literal
strings cost you SRAM whenever debug is enabled. Compiling them out is
one solution; `F()` / `PROGMEM` is the other.

### 3.8 Instruction set architecture

- The ISA is the contract between hardware and software.
- **RISC vs CISC** — and why the distinction has blurred.
- Instruction formats, addressing modes, the register file.
- **The instruction cycle:** fetch, decode, execute, memory, write-back.

Pick one ISA and learn it properly. **RISC-V** is the best choice today:
it's clean, free, thoroughly documented, and it's what modern textbooks
teach. AVR assembly is a good secondary target since you can run it on
hardware you own — and reading the compiler's assembly output for your
own `HapticMapper` is an excellent exercise (`avr-objdump -d`).

### 3.9 Datapath, control, and pipelining

- Building a single-cycle CPU: ALU, register file, memory, control unit.
- **Pipelining:** overlap fetch/decode/execute so a new instruction
  starts each cycle. Throughput improves, latency doesn't.
- **Hazards** — the price of pipelining:
  - *Structural*: two stages want the same resource.
  - *Data*: an instruction needs a result that isn't ready. Solved by
    forwarding, or by stalling.
  - *Control*: a branch means you don't know what to fetch next. Solved
    by branch prediction, and mispredictions cost you the pipeline.

This is where "why is my code slow" stops being mysterious.

### 3.10 Memory hierarchy

Registers → L1 → L2 → L3 → DRAM → flash/disk, each ~10× bigger and
~10× slower than the one above.

- **Caches** exploit locality: temporal (you'll use it again soon) and
  spatial (you'll use its neighbour soon).
- Cache lines, associativity, hit and miss cost.
- **Why array traversal order changes performance by 10×** — this is the
  single most useful practical takeaway for a programmer.
- **Virtual memory**, paging, and the TLB (relevant on Linux, absent on
  your AVR).

Note that your Nano has *no cache at all* — SRAM access is single-cycle.
That's a real simplification, and it's why AVR timing is so predictable,
which is exactly what makes it good for hard real-time work.

---

## Part C — Embedded systems

This is where computer engineering and your project meet most directly.

### 3.11 The microcontroller as a system

An MCU is a CPU plus memory plus **peripherals** on one die. The
peripherals are the point. Learn each one as a state machine you
configure through registers:

- **GPIO** — direction registers, output registers, input registers,
  internal pull-ups.
- **Timers/counters** — the most important peripheral, and the least
  understood. Modes (normal, CTC, fast PWM, phase-correct PWM),
  prescalers, compare match, input capture.
- **PWM generation** — a timer counting up, compared against a threshold.
  Duty cycle is the threshold; frequency is the count period.
- **ADC** — successive approximation, sample-and-hold, reference voltage.
- **Communication peripherals** — UART, SPI, I2C.
- **Watchdog timer** — resets the chip if the firmware stops petting it.

**Read the registers directly at least once.** Write a blink using
`DDRB` and `PORTB` instead of `pinMode`/`digitalWrite`, and time both.
You'll find the direct version is roughly 20–50× faster, and you'll
finally understand what Arduino's abstraction is costing you.

### 3.12 PWM, concretely, on your board

Your `analogWrite(9, duty)` uses **Timer1**. The Arduino core's default
prescaler puts pins 9 and 10 at **490.2 Hz**, while pins 5 and 6 sit on
Timer0 at **976.6 Hz** (Timer0 also drives `millis()`, which is why
changing its prescaler breaks timekeeping).

Things you can now reason about rather than guess:

- **490 Hz is in the audible range.** A PWM-driven motor or coil at
  490 Hz can whine. For a wrist-worn device this may or may not matter,
  but you can now predict it and test for it.
- **Raising the PWM frequency** above ~20 kHz moves the switching noise
  out of hearing. On Timer1 that's a direct register change, and it
  doesn't disturb `millis()`.
- **Duty resolution vs frequency is a tradeoff.** With a 16 MHz clock, an
  8-bit fast-PWM gives you `16 MHz / 256 = 62.5 kHz` at full resolution.
  Want more resolution? Lower frequency. Want higher frequency? Fewer
  usable duty steps. That tradeoff is fundamental to counter-based PWM.

### 3.13 Interrupts

- The vector table, the ISR, and what the hardware saves for you.
- **ISR rules, all of which have bitten someone:** keep it short; never
  block; never call anything that isn't reentrant (no `Serial.print`, no
  `delay`, no `malloc`).
- **`volatile`** on every variable shared between an ISR and main code.
  Without it the compiler may cache the value in a register and never
  see the ISR's update. This produces a bug that vanishes when you add a
  `Serial.print` to debug it — the single most maddening class of
  embedded bug.
- **Atomicity.** On an 8-bit MCU, reading a `uint16_t` takes two
  instructions. If an interrupt lands between them, you get half of the
  old value and half of the new one — a *torn read*. Fix by disabling
  interrupts around the access (`ATOMIC_BLOCK`, or `cli`/`sei`). This
  will matter the moment you move sensor reads into an ISR.

**Applied to your code:** `obstacle_haptic.ino`'s `loop()` blocks inside
`readRangeContinuousMillimeters()` until the sensor has a fresh reading.
For your current design that's fine and arguably good — the loop
naturally paces at the sensor's 50 ms cadence and nothing else needs to
run. But it means the device cannot respond to anything else during that
wait. If you ever add a button, a second sensor, or a battery monitor,
you'll need either interrupt-driven I/O or a cooperative scheduler, and
you'll need to know why.

### 3.14 Real-time systems

- **Hard vs soft real-time.** Hard: a missed deadline is a failure. Soft:
  a missed deadline degrades quality. Your wristband is soft real-time —
  a reading 20 ms late is worse, not fatal.
- **Superloop vs RTOS.** You're running a superloop. An RTOS gives you
  tasks, priorities, and preemption.
- **Scheduling:** rate-monotonic, earliest-deadline-first.
- **Priority inversion** — a low-priority task holds a lock a
  high-priority task needs. It grounded the Mars Pathfinder mission, the
  postmortem is public, and it's the best real-time war story there is.
  Read it.
- **Watchdogs.** Your `while (true) {}` halt on sensor-init failure is a
  deliberate fail-safe: better a dead device than one falsely reporting
  "all clear." A watchdog timer would instead reset the board and retry
  the init — which is better if the failure is transient (a brownout when
  the motor kicked in) and worse if it's permanent (a disconnected
  sensor, where you'd get an endless reset loop). **Neither is
  automatically right.** The design question is whether your failure
  mode is transient or permanent, and that's the kind of judgement this
  module is teaching you to make explicitly.

### 3.15 Communication protocols

You've used two of these and been bitten by the boundary between them.

| | UART | I2C | SPI |
|---|---|---|---|
| Wires | 2 (+GND) | 2 (+GND) | 4 (+GND) |
| Clock | none — both sides agree on baud | shared SCL | shared SCK |
| Speed | ~1 Mbps typical | 100 k / 400 k / 3.4 M | 10s of Mbps |
| Devices | 2 | many, addressed | many, one CS each |
| Duplex | full | half | full |

**UART** is asynchronous: no clock line, so both ends must be configured
to the same baud rate. Mismatch it and you get framing errors and
garbage — which is exactly what a wrong `Serial.begin()` looks like.

**I2C** is open-drain with pull-ups (see Module 01 §1.9 for the rise-time
analysis), 7-bit addressing, START/STOP conditions, per-byte ACK/NACK,
and optional clock stretching by a slow slave.

**SPI** is fast and simple but needs a chip-select per device and has no
acknowledgement — the master can't tell whether anyone is listening.

**Your GY-53 is the perfect case study**, because it is *the same
physical module* speaking either protocol depending on one pin. `PS`
high (the factory default) puts its onboard MCU in charge, streaming
distance over UART. `PS` low steps that MCU aside and exposes the
VL53L0X on I2C. You lost a session to this. With protocol theory in
hand, the diagnostic path shortens dramatically: *if an I2C scan finds
nothing at any address, but the bus shows traffic, then something else
is mastering that bus* — which is a conclusion you can reach from first
principles in minutes.

---

## Do this — labs for Module 03

1. **Nand2Tetris, Projects 1–5.** Build a computer from NAND gates in a
   free simulator: gates → ALU → memory → CPU → assembler. This is the
   single best digital-logic exercise available and it is free. Budget
   6–8 weeks. Nothing else on this list will teach you as much per hour.
2. **Draw `HapticMapper` as a state diagram.** By hand, on paper. Then
   add hysteresis at the zone boundaries and extend
   `test_haptic_mapper.cpp` to cover the chattering case. **This is a
   real improvement to a real project, driven directly by theory** — do
   it and commit it.
3. **Bare-metal blink.** Rewrite `01_sensor_only.ino`'s pin setup using
   `DDRx`/`PORTx` registers instead of Arduino functions. Time a
   toggle loop both ways with a scope or by counting cycles.
4. **Read your own assembly.** Compile `HapticMapper.h` for AVR and run
   `avr-objdump -d`. Find `classify()`. Count the instructions. Then
   look at what a `float` version would have compiled to.
5. **Change the PWM frequency.** Reconfigure Timer1 to run pin 9 at
   ~31 kHz instead of 490 Hz. Confirm the motor still works and that any
   audible whine is gone. Confirm `millis()` is unaffected — and be able
   to explain why it would *not* have been if you'd done this on Timer0.
6. **Protocol scope.** Capture an I2C transaction with a logic analyser
   (an $8 clone works fine, and Sigrok/PulseView is free). Decode the
   START, the address byte, the ACK, the data. Seeing your own bus is
   worth ten chapters of reading.

---

## Self-check — closed book

1. Build XOR from NAND gates only.
2. Why is two's complement used rather than sign-magnitude?
3. Explain why `now - last >= interval` survives `millis()` rollover but
   `now > last + interval` does not.
4. What is metastability and when does it occur?
5. Write the inequality that sets a synchronous circuit's maximum clock
   frequency, and name each term.
6. Moore vs Mealy — one sentence each, and one reason to prefer each.
7. Why does the ATmega328P need `PROGMEM` when a PC doesn't?
8. Name the three pipeline hazard types and one mitigation for each.
9. Why must ISR-shared variables be `volatile`, and why isn't `volatile`
   enough for a 16-bit variable on an 8-bit MCU?
10. Give one situation where a watchdog reset is the right response to a
    sensor failure and one where halting is.
11. What single characteristic makes UART fragile in a way I2C and SPI
    are not?

---

## Resources for this module

- **Nand2Tetris** (nand2tetris.org) — free course and book. Do it.
- **Harris & Harris, *Digital Design and Computer Architecture* (RISC-V
  edition)** — takes you from a transistor to a working CPU in one
  book. The best single text for this whole module.
- **Patterson & Hennessy, *Computer Organization and Design*** — the
  standard architecture text; deeper on pipelining and memory.
- **Bryant & O'Hallaron, *Computer Systems: A Programmer's
  Perspective*** — the bridge between "I can program" and "I know what
  the machine does." Excellent given your background.
- **Elecia White, *Making Embedded Systems*** — the practical embedded
  book, written by someone who ships firmware.
- **The ATmega328P datasheet** — the timer chapter especially. Reading
  datasheets is the actual skill of embedded work.
- **Icarus Verilog + GTKWave**, or **Verilator** — free HDL simulation,
  no board needed.
- **Logisim Evolution** — free graphical logic simulator, good for
  Part A before you commit to HDL.
