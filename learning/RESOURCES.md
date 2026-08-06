# Resources — annotated

Not a link dump. Each entry says what it's good at and what it's bad at,
because picking the wrong resource for where you are is the main way
self-study stalls.

**Link-check status:** every URL below was fetched on 2026-08-06 from
this session. Results are marked `[✓]` verified reachable,
`[!]` returned 403 to an automated fetch — these are real, well-known
sites that block bots, so open them in a browser, and `[?]` unreachable
from this network, verify yourself. Nothing here is a link I merely
remembered.

---

## The short list

If you only use five things, use these.

1. **Paul's Online Math Notes** `[✓]` — https://tutorial.math.lamar.edu/
   Complete, free, worked-example-driven notes for Calculus I/II/III and
   Differential Equations. Better structured than most paid textbooks.
   *Good at:* fluency, worked examples, being complete.
   *Bad at:* motivation — it won't tell you why you care.
2. **Falstad Circuit Simulator** `[✓]` — https://www.falstad.com/circuit/
   Browser-based, instant, shows current as moving dots.
   *Good at:* intuition, fast experiments, seeing what a circuit does.
   *Bad at:* accuracy — it's idealised. Move to LTspice for real
   semiconductor behaviour.
3. **Nand2Tetris** `[✓]` — https://www.nand2tetris.org/
   Build a working computer from NAND gates upward. Free, project-based.
   *Good at:* making digital logic and architecture concrete and
   permanent.
   *Bad at:* analog anything, and it stops before real CPU design.
4. **Brian Douglas's control lectures** — search "Brian Douglas control
   systems" on YouTube.
   *Good at:* the best control-theory intuition available anywhere,
   free.
   *Bad at:* problem-solving mechanics — pair it with Nise.
5. **The Scientist and Engineer's Guide to DSP** `[✓]` —
   https://www.dspguide.com/
   Steven Smith's book, free in full online.
   *Good at:* practical DSP explained without hiding behind notation.
   *Bad at:* rigour, if you need the proofs.

---

## Math

| Resource | Link | Notes |
|---|---|---|
| Khan Academy | khanacademy.org | Algebra/trig repair. Fast, tests you. Start here if placement Tier A was hard. |
| Paul's Online Math Notes | `[✓]` tutorial.math.lamar.edu | Calc I/II/III + ODEs. The workhorse. |
| 3Blue1Brown — *Essence of Calculus* | `[✓]` 3blue1brown.com/topics/calculus | Intuition. **Watch alongside, never instead of.** It builds understanding without fluency, and you need both. |
| 3Blue1Brown — *Essence of Linear Algebra* | 3blue1brown.com | Watch the whole series in one sitting before Strang. |
| MIT OCW 18.06 Linear Algebra (Strang) | `[✓]` ocw.mit.edu | Widely considered the best recorded linear algebra course. Free. |
| MIT OCW 18.03 Differential Equations | ocw.mit.edu | Harder and better than Paul's. Do it second. |

---

## Circuits and analog electronics

| Resource | Link | Notes |
|---|---|---|
| All About Circuits textbook | `[!]` allaboutcircuits.com/textbook | Free, complete, Vols I–III (DC, AC, semiconductors). The right first pass. |
| MIT OCW 6.002 Circuits and Electronics | `[✓]` ocw.mit.edu | Real problem sets. Do after All About Circuits. |
| Razavi, *Fundamentals of Microelectronics* + his lecture series | search YouTube | The clearest explanation of semiconductor devices in existence. |
| Sedra & Smith, *Microelectronic Circuits* | book | The standard reference. Dense — use as lookup, not as a first read. |
| Horowitz & Hill, *The Art of Electronics* | book | Not a first textbook. The reference you keep for twenty years, full of judgement calls textbooks omit. Buy it eventually. |
| SparkFun tutorials | `[✓]` learn.sparkfun.com/tutorials | Practical, correct, well-illustrated. Good for filling specific gaps. |

---

## Digital and computer engineering

| Resource | Link | Notes |
|---|---|---|
| Nand2Tetris | `[✓]` nand2tetris.org | Do it. Projects 1–5 minimum. |
| Harris & Harris, *Digital Design and Computer Architecture* (RISC-V ed.) | book | Transistor to working CPU in one book. **The best single text for this module.** |
| Patterson & Hennessy, *Computer Organization and Design* | book | Deeper on pipelining and memory hierarchy. |
| Bryant & O'Hallaron, *CS:APP* | book | The bridge from "I can program" to "I know what the machine does." Ideal given your background. |
| Elecia White, *Making Embedded Systems* | book | Written by someone who ships firmware. Practical and opinionated. |
| ATmega328P datasheet | `[!]` microchip.com | Read the timer and electrical-characteristics chapters. Datasheet-reading is the actual skill. |
| Logisim Evolution | `[!]` github.com/logisim-evolution | Free graphical logic simulator. Good before committing to HDL. |
| Icarus Verilog + GTKWave | iverilog.icarus.com | Free HDL simulation, no FPGA board needed. |

---

## Signals, systems, and DSP

| Resource | Link | Notes |
|---|---|---|
| MIT OCW 6.003 Signals and Systems | `[✓]` ocw.mit.edu | Oppenheim's own recorded lectures. Free. |
| Oppenheim & Willsky, *Signals and Systems* | book | The standard text. Dry but complete. |
| Lathi, *Signal Processing and Linear Systems* | book | Friendlier alternative if Oppenheim doesn't land. |
| Smith, *The Scientist and Engineer's Guide to DSP* | `[✓]` dspguide.com | Free, practical, excellent. Read alongside the theory. |
| 3Blue1Brown — Fourier transform video | 3blue1brown.com | Best available intuition for what the transform *is*. |

---

## Control theory

| Resource | Link | Notes |
|---|---|---|
| Brian Douglas — control lectures | YouTube | **Start here.** Best intuition anywhere, free. |
| Nise, *Control Systems Engineering* | book | Most readable standard textbook. Good worked examples. |
| Ogata, *Modern Control Engineering* | book | More rigorous, better on state space. |
| Åström & Murray, *Feedback Systems* | `[✓]` fbswiki.org | Free PDF, rigorous and modern. Read second, after Nise. **Note:** the old Caltech `cds.caltech.edu/~murray/amwiki` address no longer resolves; fbswiki.org is the current home. |
| `python-control` | `[✓]` python-control.readthedocs.io | Free. Mirrors MATLAB's Control System Toolbox API closely enough that MATLAB textbook examples translate directly. |
| GNU Octave | `[✓]` octave.org | Free MATLAB-compatible environment for textbook examples that are MATLAB-only. |

---

## Mechatronics, mechanics, robotics

| Resource | Link | Notes |
|---|---|---|
| Alciatore & Histand, *Introduction to Mechatronics and Measurement Systems* | book | Closest thing to a single text for the whole mechatronics module. |
| Hibbeler, *Engineering Mechanics: Statics / Dynamics* | book | Standard mechanics, enormous problem sets. |
| Lynch & Park, *Modern Robotics* | `[✓]` modernrobotics.northwestern.edu | Free book + free video lectures. The right next step for kinematics. |
| ST VL53L0X datasheet and application notes | st.com | You own the hardware; every claim in them is testable on your desk. |
| Pololu motor/encoder tutorials | pololu.com | Practical and correct at exactly this level. |

---

## Tools — install these

All free.

| Tool | Link | For |
|---|---|---|
| **Falstad CircuitJS** | `[✓]` falstad.com/circuit | Circuit intuition. Browser, nothing to install. |
| **LTspice** | `[?]` search analog.com for "LTspice" | Real SPICE. Essential once you reach semiconductors. Windows-native, which suits your machine. |
| **Python + NumPy/SciPy/Matplotlib** | python.org | The lab bench for Modules 04–06. `scipy.signal` has everything. |
| **`python-control`** | `[✓]` python-control.readthedocs.io | `pip install control`. Bode, root locus, step response, state space. |
| **GNU Octave** | `[✓]` octave.org | MATLAB-compatible fallback. |
| **KiCad** | `[✓]` kicad.org | Schematic capture and PCB layout. Free, professional-grade. |
| **Wokwi** | `[✓]` wokwi.com | Browser Arduino/ESP32 simulator. Test firmware with no hardware — including a VL53L0X. |
| **Tinkercad Circuits** | `[✓]` tinkercad.com/circuits | Free breadboard + Arduino simulator. Gentler than Wokwi. |
| **Logisim Evolution** | `[!]` github.com/logisim-evolution | Digital logic, graphical. |
| **Icarus Verilog + GTKWave** | iverilog.icarus.com | HDL simulation. |
| **Sigrok / PulseView** | sigrok.org | Free logic-analyser software. Pair with an ~$8 clone and you can finally *see* your I2C bus. |

**The one piece of hardware worth buying beyond your BOM:** a cheap
8-channel USB logic analyser. They're a few thousand tenge, they work
with PulseView, and being able to see your own I2C and PWM waveforms
would have shortened your GY-53 debugging session dramatically. Higher
value per tenge than anything else you could add.

Second on that list, if the budget stretches: a basic USB oscilloscope
or a cheap benchtop one. Module 02's flyback-spike lab needs one to be
fully convincing.

---

## How to choose when resources conflict

They will. Some rules:

- **Video for intuition, text for fluency.** Videos are excellent at
  "why does this matter" and poor at "now do forty problems." You need
  both, and the second one is what actually builds capability.
- **When two textbooks disagree, check units.** Nine times out of ten
  it's a convention difference (rad/s vs Hz, `j` vs `i`, different sign
  conventions on phase), not a real contradiction.
- **Prefer the resource with problem sets.** A resource you can't test
  yourself against is entertainment.
- **If a text loses you for three pages running, switch texts.** It's
  usually a mismatch of prerequisites or style, not a failure on your
  part. Come back to it later — often it reads easily the second time.
- **Datasheets and standards documents beat tutorials** for anything
  specific to a real part. Tutorials copy each other's errors; the
  GY-53's `PS` pin was in the manual the whole time.
