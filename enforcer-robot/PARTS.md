# Parts list — The Enforcer

Budget target: **€250–350** for the hexapod, **~€180–250** for the quadruped
version. Both include spares.

## Read this first

**These are specifications, not verified local stock.** Unlike your wristband
`PURCHASE_LIST.md` (which was walked into real Almaty shops on a real date),
nothing here is confirmed on a Berlin shelf yet. Treat it as "what to look
for," then do a sourcing pass: German electronics retailers (Reichelt,
Conrad, BerryBase, Berlin's maker/electronics shops), plus AliExpress for the
generic mechanical parts. **Order once, early, with spares** — shipping is the
long pole.

## Core electronics

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 1 | **MG90S metal-gear servo** | 18 (+3 spare) / 12 for quad | 55 / 38 | Metal gear is not optional — plastic SG90s strip under leg load. Buy spares. |
| 2 | **PCA9685 16-ch PWM driver** | 2 (1 for quad) | 8 | Chainable over I2C. 2 boards = 32 channels (18 legs + 2 head + spare). |
| 3 | **Raspberry Pi 5 (4GB)** | 1 | 65 | Runs the camera + a small detector in real time. Pi 4 works, saves ~€20. |
| 4 | microSD 32GB A2 | 1 (+1 spare) | 14 | The spare is real advice; cards die at the worst moment. |
| 5 | **Camera** (Pi Camera Module 3 or USB webcam) | 1 | 15–25 | Module 3 has autofocus; USB is simpler on a moving robot. |
| 6 | **GC9A01 round SPI LCD** (the eye) | 1 | 8 | Highest personality-per-euro part in the build. |
| 7 | Pan/tilt bracket + 2 servos | 1 | 10 | Carries the camera **and** the nozzle so aiming = centering. |

## The water rig (the signature)

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 8 | **Mini diaphragm water pump, 3–6V** | 1 (+1 spare) | 8 | Small self-priming pump. Draws ~200–500mA — needs a MOSFET, not a GPIO. |
| 9 | **Logic-level MOSFET** (e.g. IRLZ44N) | 2 | 2 | Your wristband's transistor+diode motor driver, scaled up for the pump's current. |
| 10 | **Flyback diode** (1N4007) | 2 | 1 | Across the pump, same role as the 1N4148 on your vibration motor. |
| 11 | Silicone tubing + nozzle | — | 3 | A narrow nozzle = a focused squirt at low flow. |
| 12 | Water reservoir (~100–250ml) | 1 | 3 | Small bottle; mount at the front, low. |

## Sensing & audio

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 13 | **Cliff sensors** (TCRT5000 down-facing IR) | 4 | 4 | Mandatory for Warden mode. Detect the desk edge before a leg goes over it. |
| 14 | **VL53L0X ToF** (proximity/obstacle) | 1–2 | 8 | You already know this sensor and its library from the wristband. |
| 15 | MAX98357A I2S amp + small speaker | 1 | 8 | For taunts. Or any small USB speaker. |

## Power (get this right or nothing works)

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 16 | **2S LiPo 7.4V, 2200mAh+, XT60** | 1 | 22 | The servo rail. Capacity = demo runtime. |
| 17 | **UBEC 5–6V, 6A+** | 1 | 8 | Regulates the servo rail. Do NOT run servos off the Pi. |
| 18 | Buck converter 5V/5A | 1 | 6 | Separate logic rail for the Pi. **Common ground** with the servo rail. |
| 19 | LiPo balance charger + LiPo-safe bag | 1 | 18 | Non-negotiable safety. |
| 20 | Switch + inline fuse (10A) | 1 | 3 | The fuse stands between a shorted servo lead and a fire. |

## Structure & consumables

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 21 | PLA/PETG filament OR kit chassis | — | 20–60 | See "printer" note below. |
| 22 | M2/M3 screws + standoffs | 1 set | 8 | You'll use more than you think. |
| 23 | Silicone wire (18AWG servo rail, 22AWG logic), JST, heatshrink | — | 8 | |

**Rough total:** hexapod ~€320, quadruped ~€230 (before printer/chassis
choice).

## Optional accelerator

- **Coral USB / Hailo accelerator (~€60–70)** — only if on-device detection is
  too slow on the Pi 5. Try without it first.

## Power wiring (one place, get it right in week 4)

```
2S LiPo ──┬── fuse ── switch ──┬── UBEC 6V/6A ──► PCA9685 V+ ──► leg + head servos
          │                    │
          │                    └── buck 5V/5A ──► Raspberry Pi ──► Pi GPIO ─► MOSFET ─► pump
          │
          └── balance lead ──► charger (when off the robot)

   servo GND ──┬── Pi GND ──┬── pump/MOSFET GND     ← single common ground
```

Two rails, one ground, one fuse. The pump and servos on the battery side; the
Pi on its own regulated rail. The MOSFET gate is driven by a Pi GPIO, source to
common ground, pump between V+ and drain, flyback diode across the pump.

## The 3D printer situation

Your printer is broken — diagnose it in the first 48 hours, because the fix
may need a part with the same shipping lead time as everything else, and it
should ride in the same order.

- **Mechanical fault** (nozzle, belts, bed, PTFE): cheap, fix locally this week.
- **Electronic fault** (driver, thermistor, board): order the part in the
  week-0 order.
- **Hard gate:** if it isn't printing dimensionally-accurate parts by end of
  week 2, **buy a kit chassis** (a "12/18-DOF quadruped/hexapod frame,"
  ~€30–60, sometimes bundled with servos — check they're metal-gear). Buying
  the frame is not defeat; it moves your effort to the AI and the water rig,
  which is where the originality is.

## What to skip

- **IMU/gyro** — unnecessary with a statically-stable gait (three feet always
  down). Add only if you attempt a dynamic trot later.
- **Smart serial servos** — nicer, ~3× the price. Not at this budget.
- **Local LLM** — you don't need conversation. The personality is the state
  machine, not a chatbot.
