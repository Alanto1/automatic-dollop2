# Testing an ESP32-S2 Mini

Do this on **every board as it arrives**, before soldering anything. You
bought three from a marketplace seller; the point is to find a bad one while
the return window is open, not on a half-built robot in October.

Takes about 10 minutes for the first board, 2 minutes for each after.

---

## Step 0 — no computer needed (30 seconds)

Plug it into any USB-C charger.

- **A power LED comes on** → the regulator works, the board isn't shorted.
- **Nothing** → check the cable is a *data/charge* cable, not charge-only.
  Then try another. A dead board at this stage is a dead board.

⚠️ **Never plug in a board sitting on anything metal or conductive.** The
underside pads are exposed.

## Step 1 — does the computer see it? (2 min)

The S2 has **native USB** — there is no CH340/CP2102 chip on it, so there is
**no driver to install**. That is a difference from most ESP32 boards.

Plug it into your laptop and look for a new serial port:

```bash
ls /dev/tty.usbmodem*     # macOS
ls /dev/ttyACM*           # Linux
# Windows: Device Manager -> Ports (COM & LPT)
```

**Nothing appears?** Put it in bootloader mode by hand:

> **Hold `0` (BOOT) → tap `RST` → release `0`.**

A board in bootloader mode always enumerates, even with broken firmware on
it. If it appears only this way, the board is fine and its firmware is not.

## Step 2 — what chip is actually on it? (2 min)

Before Arduino, before anything. `esptool` talks to the ROM bootloader
directly, so it works even on a board that won't run code:

```bash
pip install esptool
esptool.py --port /dev/ttyACM0 chip_id
esptool.py --port /dev/ttyACM0 flash_id
```

You want to see:

```
Chip is ESP32-S2 (revision v0.0)
Features: WiFi, No Embedded Flash, No Embedded PSRAM, ADC and temperature ...
Crystal is 40MHz
MAC: 7c:df:a1:...
Detected flash size: 4MB
```

- **"Chip is ESP32-S2"** — anything else and you were sent the wrong part.
- **"Detected flash size: 4MB"** — the listing says 4MB. Less is misdescribed.
- *"No Embedded PSRAM" is normal here* — on this board the PSRAM is a
  separate package, not inside the chip. Step 3 is what actually checks it.

## Step 3 — run the acceptance test (5 min)

Open [`board_test.ino`](board_test.ino) in the Arduino IDE.

**Board settings, and two of them are not optional:**

| Setting | Value |
|---|---|
| Board | **LOLIN S2 Mini** |
| **USB CDC On Boot** | **Enabled** ← without this, `Serial` prints *nothing* and the board looks dead |
| **PSRAM** | **Enabled** ← without this, the PSRAM test fails on a good board |
| Upload Speed | 921600 |

Upload, open Serial Monitor at **115200**, and press `RST`.

It checks nine things and prints `PASS`/`FAIL` for each:

1. Chip really is an ESP32-S2, single core, WiFi present
2. Flash ≥ 4MB
3. **PSRAM — allocates 256KB, writes a pattern, reads it back**
4. Onboard LED blinks (watch the board)
5. All 8 servo GPIOs drive high and low
6. **8 LEDC PWM channels attach at once, 1.5ms servo-centre pulse**
7. I2C scan (finds the OLED once it's wired)
8. WiFi scan + MAC address
9. Free heap

Ends with `ALL CHECKS PASSED` or a count of failures.

---

## The two results that actually matter

### PSRAM — this is why you run the test at all

Cheap S2 boards are routinely listed with 2MB PSRAM and shipped without it.
Nothing tells you until something fails months later, long after the return
window closed.

`ESP.getPsramSize()` reporting a number proves nothing, so the test writes
256KB of a known pattern and reads every word back. A board that lies fails
here, on your desk, in week 0.

If it fails: **re-check that PSRAM is Enabled in the IDE first** — that's the
common cause. If it still fails with the setting on, the board is
misdescribed. Return it.

### Eight PWM channels — and there is no ninth

The ESP32-**S2**'s LEDC peripheral has **exactly 8 channels**. The original
ESP32 has 16. Sesame needs exactly 8 servos.

**You have zero spare PWM channels.** That is fine — the plan never needed a
ninth — but it means:

- The pump is a **MOSFET on a plain GPIO**, on/off. It cannot be PWM'd from
  LEDC. (It doesn't need to be; `fire_ms` is a duration, not a speed.)
- No RGB status LED on hardware PWM. Use the OLED face instead, which is
  what the design already does.
- If you ever add a 9th servo, it needs a PCA9685 — the thing PARTS.md
  currently tells you to skip. That advice holds *only* while you stay at 8.

Test 6 attaches all eight at once so you find this out now rather than at
week 3.

---

## When it won't program

| Symptom | Cause |
|---|---|
| No serial port at all | Charge-only USB cable. This is the #1 cause |
| Port appears, upload fails | Not in bootloader mode: hold `0`, tap `RST`, release `0` |
| Uploads fine, Serial Monitor blank | **USB CDC On Boot** is Disabled |
| Port vanishes after upload | Normal — the S2 re-enumerates. Reselect the port |
| Port drops mid-upload | Underpowered hub. Plug straight into the laptop |
| Endless reboot loop | Something is drawing too much from 3V3, or a strapping pin (0, 45, 46) is wired |

## Label the good ones

Write **1**, **2**, **3** on the boards with a marker and note the MAC
address of each from test 8. When one starts misbehaving in week 6 you want
to know whether it is the one that already had a marginal result.

Keep the failures *separate and clearly marked*. A drawer with a dead board
loose in it costs you an afternoon eventually.

## Before it goes on the robot

Two more things the bench test can't cover, both in
[`BUILD_CHECKLIST.md`](../../BUILD_CHECKLIST.md) week 3:

- **Under load with 8 real servos**, the 3V3 rail sags and the board may
  brown out. That's the 1000µF bulk-capacitance test.
- **USB power is not battery power.** Everything above passes on USB and can
  still fail on the 14500 pack through a buck converter. Retest once the
  power chain is real.
