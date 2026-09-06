# sesame-motor-tester — upstream's own, unmodified

Sesame's motor tester, vendored from
[dorianborian/sesame-robot](https://github.com/dorianborian/sesame-robot)
(`firmware/debugging-firmware/`), Apache 2.0. See [`NOTICE`](NOTICE).

**Needs the `ESP32Servo` library** — Library Manager, by Kevin Harrington.

If that library will not resolve, use [`../motor_test/`](../motor_test/)
instead: same commands, same pins, same pulse widths, no library. A sketchbook
under OneDrive or on a non-ASCII path is enough to stop ESP32Servo being
found, and there is nothing to be gained from fighting it.

## Why this is its own folder

The Arduino IDE compiles **every `.ino` in a folder as one program**. Two
sketches in one folder means two `setup()`s and two `loop()`s, and it will not
build. One sketch per folder, always.

## Use

Serial monitor at 115200, line ending **"New Line"**.

| command | does |
|---|---|
| `all,90` | every motor to 90° |
| `0,90` | motor 0 only |
| `stop` | detach all |

Send `all,90` **first**, then plug motors in **one at a time**. The map and
the cautions are in [`../motor_test/README.md`](../motor_test/README.md).
