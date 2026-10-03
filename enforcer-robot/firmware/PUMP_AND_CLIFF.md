# Pump driver and cliff sensors — build and test

Both go on the perfboard **at the same time as the ESP32 goes into the body**,
so the robot only gets opened once. Build each one, prove it on its own bench
sketch, and only then use it from `walk/walk.ino`.

| Sketch | What it is for |
|---|---|
| `pump_test/` | prove the pump driver; size the series resistor |
| `cliff_test/` | see the four sensors; calibrate them on **your** desk |
| `walk/` | the real thing: `#` arms the pump, `!` fires, `l` shows the sensors, and the cliff reflex runs on every step |

Pins, from `PARTS.md` "The ESP32-S2 pin budget": pump gate **GPIO 11**, cliff
sensors **GPIO 3 5 7 9** (ADC1 only — ADC2 is unusable while WiFi is on).

---

## Part 1 — the pump driver

### Parts (all already bought)

| Part | Qty | From |
|---|---|---|
| IRLZ44N MOSFET | 1 | BOM #19 |
| 1N4007 diode | 1 | BOM #20 |
| 47 Ω resistor | 2 | resistor kit — in parallel = **23.5 Ω** |
| 100 Ω resistor | 1 | resistor kit — gate resistor |
| 10 kΩ resistor | 1 | resistor kit — gate pull-down |
| 1000 µF 16 V capacitor | 1 | BOM #22b — across the 5 V rail |
| 2 header pins + a dupont jumper wire | 1 | the **disable jumper** |

### The circuit

```
 5V rail ──[ disable jumper ]──[ 47Ω ║ 47Ω ]──┬───────── pump +
                                               │   ┌──┐
                                       1N4007  │   │  │  pump in water
                                  stripe ──────┘   │  │
                                  (cathode) up     └──┘
                                       other end ──┬───── pump −
                                                   │
                                                 DRAIN
 GPIO 11 ──[100Ω]──┬──────────────── GATE   IRLZ44N
                   │                         SOURCE
                [10kΩ]                          │
                   │                            │
 GND rail ─────────┴────────────────────────────┘

 1000µF: + leg to 5V rail, − leg (striped side) to GND rail
```

**IRLZ44N pins** — hold it with the printed side facing you, legs down:
**G  D  S**, left to right. The metal tab is also the drain.

**1N4007** — the **stripe is the cathode**. Stripe goes to the **pump +**
side. Fitted the wrong way round it is a dead short across the pump the moment
the MOSFET turns on.

What each part is for:

- **47 Ω ║ 47 Ω** drops the 5.1 V rail to about the pump's rated 3 V. All 8
  PWM channels are servos, so a resistor is the only way to lower the voltage.
- **1N4007** — the pump is a motor. When it switches off it kicks back a voltage
  spike; the diode gives that spike somewhere harmless to go.
- **100 Ω** limits the current into the gate as it switches.
- **10 kΩ** holds the gate at 0 V while the ESP32 boots, so the pump cannot
  twitch on at power-up before the code takes control of the pin.
- **1000 µF** — a pump starting draws a burst of current. The capacitor
  supplies it so the servos and the ESP32 do not see the rail dip.
- **Disable jumper** — pull it and the pump is physically disconnected, whatever
  the software does. This is interlock 5 in `BEHAVIOURS.md`.

### Step by step

1. **Solder it on the perfboard** next to the 5 V and GND rails, following the
   circuit above. Keep the pump's two wires long enough to reach the payload
   deck later.
2. **Check before power:** meter on Ω, power off. GPIO 11 pad to GND should read
   about **10 kΩ** (the pull-down). Pump + to pump − should **not** read near
   0 Ω — if it does, the diode is in backwards.
3. **Put the pump in a cup of water**, tube into a sink or a second cup.
   ⚠️ **Never run it dry.** The water cools and lubricates it.
4. **Fit the disable jumper.** Flash `pump_test`, open the Serial Monitor at
   115200.
5. Type **`a`** → `ARMED`. Type **`f`** → it fires for 200 ms. You should see a
   squirt.
   - Nothing at all → pull the jumper, check the MOSFET is G-D-S the right way
     round and that GPIO 11 really goes to the gate.
   - The ESP32 resets when it fires → the rail is dipping. Check the 1000 µF is
     fitted the right way round.
6. **Size the resistor.** Meter on **V⎓**, probes across the two pump
   terminals. Type **`m`** — the pump runs for 2 seconds, long enough to read.

   | Volts across the pump | Do this |
   |---|---|
   | **2.7 – 3.3 V** | ✅ done, keep the two 47 Ω |
   | above 3.3 V | not enough drop → use **one** 47 Ω alone |
   | below 2.7 V | too much drop → add a **third** 47 Ω in parallel (15.7 Ω) |

7. **Pull the jumper and type `f` again.** Nothing should happen. That proves
   the jumper works — the one safety you never want to discover is broken.

---

## Part 2 — the cliff sensors

The robot walks on a desk. Right now nothing stops it walking off the edge.
These four sensors look straight down; when one stops seeing desk, the robot
stops and backs away. That reflex outranks every command.

### Parts

| Part | Qty |
|---|---|
| TCRT5000 (bare sensor) | 4 |
| 100 Ω resistor | 4 — one per sensor, for its IR LED |
| 10 kΩ resistor | 4 — one per sensor, pull-up for its output |
| `cliff_bracket` (printed) | 4 |

### Which sensor goes where

| GPIO | Corner |
|---|---|
| 3 | **front-left** |
| 5 | **front-right** |
| 7 | **back-left** |
| 9 | **back-right** |

Front is the **R1 / L1** end. Left and right as seen from **behind** the robot.

### The circuit — one sensor, built four times

```
  3V3 ──[100Ω]──── LED +            the IR LED, always on
                   LED − ───── GND

  3V3 ──[10kΩ]──┬── C              the light sensor
                │
           GPIO 3/5/7/9       E ── GND
```

⚠️ **3.3 V, never 5 V.** The ESP32's analogue inputs are not 5 V tolerant, and
the moment a sensor sees an edge its output rises to whatever the pull-up is
connected to.

**Put the resistors on the perfboard**, not at the sensor. Then each sensor
needs only **3 wires** out to its corner: LED feed, signal, GND.

### Telling the sensor's pins apart — without guessing

Each TCRT5000 has two halves: a **blue or clear** lens (the IR LED) and a
**black** lens (the light sensor). Two pins under each.

1. Wire the LED half first. Look at it **through your phone's camera** — most
   phone cameras show infrared as a faint purple glow.
   **No glow → swap its two wires.** Backwards does no harm through 100 Ω.
2. Wire the black half. In `cliff_test`, cover the sensor with your hand, then
   take your hand away. The number should change a lot.
   **No change → swap its two wires.** Also harmless.

### Step by step

1. **Wire ONE sensor** to GPIO 3 first. Flash `cliff_test`. The live view prints
   all four; watch **front-left**. Hold a piece of paper about 5 mm under it,
   then take it away: low with paper, high without. That is the whole idea.
2. **Wire the other three**, same way, to GPIO 5, 7, 9. Check each the same way.
3. **Mount them** in the four `cliff_bracket`s at the corners, facing **straight
   down**, about **2–5 mm** above the desk. They must stick out **past where the
   feet land**, or a foot goes over the edge before a sensor sees it.
4. **Calibrate on your actual desk:**
   - robot standing on the desk → type **`d`**
   - lift it about 10 cm (or hold each sensor out past the edge) → type **`e`**
   - type **`p`** → it prints a line like
     ```
     static const int   CLIFF_THRESH[4] = {1830, 1795, 1902, 1850};
     ```
   If a sensor says **TOO CLOSE**, it cannot tell desk from edge — lower it
   nearer the desk, or suspect a dark matte desk (test on white paper).
5. **Paste that line into `walk/walk.ino`**, over the `{0, 0, 0, 0}` line.
   While it is all zeros the reflex is **off**, and the robot says so at boot.
6. **Test the reflex, carefully.** Flash `walk`. Type `l` to see all four read
   `desk`. Then walk it **slowly** toward the desk edge — `w`, with your hand
   ready to catch it. When a front sensor passes the edge it should print
   `CLIFF: front-left` (or right), stop, and back away one step.

   Test the back too: walk it backward (`r`) toward the edge.

---

## Using them from walk.ino

| Key | Does |
|---|---|
| `#` | arm / disarm the pump — starts **disarmed** every boot |
| `!` | fire 200 ms (armed, and at least 2 s since the last shot) |
| `l` | print the four cliff readings, threshold, and `desk` / `EDGE` |

The cliff reflex needs no key: once `CLIFF_THRESH` holds real numbers it runs
before every single step. If an edge appears at the front it backs away; at
the back it steps forward; on more than one side it stops and waits for you.

What is **not** here yet: the other three firing interlocks (a person seen,
STRIKE state, target inside the range band). They need the Pi, and arrive
with the Pi ↔ ESP32 link.
