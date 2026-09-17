# motor_test — drive all eight servos from the serial monitor

Two sketches, same commands, same pins, same pulse widths. Flash whichever
compiles.

| sketch | needs | notes |
|---|---|---|
| **`motor_test/`** ← this one | nothing | Drives LEDC directly, same way `board_test` and `servo_test` already do on this machine |
| [`../sesame-motor-tester/`](../sesame-motor-tester/) | **ESP32Servo** library | Sesame's own, Apache 2.0. The canonical one, and what its build guide refers to |

Use upstream's if `ESP32Servo` installs cleanly. Use this one if it does not —
a sketchbook on a non-ASCII path, or inside OneDrive, is enough to stop the
library resolving, and there is nothing to be gained from fighting it.

⚠️ **They are in separate folders on purpose.** The Arduino IDE compiles every
`.ino` in a folder as one program, so two complete sketches side by side gives
two `setup()`s and two `loop()`s and a build that cannot succeed. One sketch
per folder, always.

## Before you flash anything

⚠️ **Every motor shaft must spin freely.** If the hip joints are already
pressed onto their shafts and the M2.5 centre screws are not in, pull them
off first. Upstream flags this as a caution, not a tip: a joint that cannot
reach the commanded angle stalls the servo, and a stalled MG90S strips its
gears in seconds.

## Use

Serial monitor at **115200**, line ending **"New Line"** — with "No Line
Ending" nothing you type ever reaches the sketch.

| command | does |
|---|---|
| `all,90` | every motor to 90° |
| `0,90` | motor 0 only |
| `stop` | detach all, shafts go limp |
| `list` | what is attached and where *(this version only)* |

**The order matters:**

1. Flash it. Nothing moves — motors stay limp until commanded
2. Send `all,90`
3. **Now** plug in motor 0. It should whir to position and hold
4. Plug in motors 1–7 **one at a time**, watching each land

Plugging them in one at a time is the whole point. A servo in the wrong slot,
or one fighting its own end stop, is obvious when it is the only thing that
just moved and invisible when eight move together.

> *"99% of the time, if your motor is moving in the wrong direction, crashing,
> or being sporadic, the motor is plugged into the wrong slot."* — upstream

⚠️ A servo that buzzes without settling, or moves then immediately fights
back, is hitting a limit. **Unplug it.**

## The map

| motor | joint | GPIO | |
|---|---|---|---|
| 0 | `R1` | 1 | right hip |
| 1 | `R2` | 2 | right hip |
| 2 | `L1` | 4 | left hip |
| 3 | `L2` | 6 | left hip |
| 4 | `R4` | 8 | right lower leg |
| 5 | `R3` | 10 | right lower leg |
| 6 | `L3` | 13 | left lower leg |
| 7 | `L4` | 14 | left lower leg |

**The legs are not in alphabetical order** — `R4` is motor 4 and `R3` is
motor 5. Reading the pattern instead of the table puts two servos in the
wrong slots.

## Why 90° is 1830 µs and not 1500

Sesame's pulse band is 732–2929 µs, whose midpoint is 1830. That is not the
servo convention and it is not a mistake — matching the production firmware
matters more than matching the convention, because a horn aligned against a
different centre is aligned against nothing.

Both sketches use the same constants for exactly this reason.
