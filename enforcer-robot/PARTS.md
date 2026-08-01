# Parts list — The Enforcer

Budget target: **€250–350** for the hexapod, **~€180–250** for the quadruped
version. Both include spares.

## Read this first

**These are specifications. For real prices, read
[`PURCHASE_LIST.md`](PURCHASE_LIST.md).** The sourcing pass was done on
**2026-08-01** against German retailers, and it found the budget below to be
roughly **half** the real cost — mostly because of one part. The €-columns
here are kept as the original spec estimates so the gap stays visible; treat
`PURCHASE_LIST.md` as the number that matters.

The short version of what changed:

- **Raspberry Pi 5 4GB is €118.50, not €65** (confirmed at two retailers) —
  a RAM price surge, passed straight through. The **2GB at €69.50** is now
  the sensible buy.
- The **Pi 4 fallback below is void**: Pi 4 4GB is €108.40, so it saves €10,
  not €20, for a much weaker CPU.
- Realistic quadruped total: **~€450**, or ~€380 with the 2GB Pi and a USB
  webcam.

**Order once, early, with spares** — shipping is the long pole, and the
AliExpress items (buck converter, pan/tilt, chassis) are the longest at 2–4
weeks.

## Core electronics

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 1 | **MG90S metal-gear servo** | 18 (+3 spare) / 12 for quad | 55 / 38 | Metal gear is not optional — plastic SG90s strip under leg load. Buy spares. |
| 2 | **PCA9685 16-ch PWM driver** | 2 (1 for quad) | 8 | Chainable over I2C. 2 boards = 32 channels (18 legs + 2 head + spare). |
| 3 | **Raspberry Pi 5 (4GB)** | 1 | ~~65~~ **118,50** | Runs the camera + a small detector in real time. ~~Pi 4 works, saves ~€20.~~ Pi 4 now saves only €10 — don't. Consider the **2GB at €69,50** instead. |
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

**Rough total (original spec estimate):** hexapod ~€320, quadruped ~€230.

**Actual, sourced 2026-08-01:** quadruped **~€450** — or **~€380** with the
2GB Pi and a USB webcam. See [`PURCHASE_LIST.md`](PURCHASE_LIST.md) for the
line-by-line cart, stock counts, and which shop.

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
