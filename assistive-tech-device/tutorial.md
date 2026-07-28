# Build tutorial — one part at a time

This walks through assembling the device in the order that makes problems
easiest to find: bring up one part, prove it works on its own, then add
the next part. If something breaks, you'll know exactly which addition
caused it, instead of staring at six wires wondering which one is wrong.

Each phase says what to have ready, how to wire it, what to upload, and
what success looks like.

A note before you start: this reflects the project's current state as of
2026-07-25 (VL53L0X sensor, not the VL53L1X earlier drafts assumed - see
`PURCHASE_LIST.md` and `CLAUDE.md`'s session log for why - and an 18650
battery, not a flat LiPo pouch). If you're reading this later and the BOM
has changed again, `README.md` is the source of truth for current parts;
update this file's specifics to match rather than trusting a stale phase.

## Phase 0 — software setup (do this before any hardware arrives)

- [ ] Install the Arduino IDE (arduino.cc).
- [ ] In the IDE: Tools → Manage Libraries, search "**VL53L0X**", install
      the one by Pololu. (Not VL53L1X - different library, matches the
      sensor this project actually uses now.)
- [ ] If you haven't already: OpenSCAD and a C++ compiler (w64devkit) -
      see `CLAUDE.md`'s "Environment notes" for where things ended up
      installed on the builder's machine.

## Phase 1 — the board, alone

**Have ready**: Arduino Nano clone, USB cable matching its connector.
(Everything downstream of this - pin numbers, the enclosure's dimensions,
the purchase list - assumes a Nano specifically. An ESP32 or other
Arduino-compatible board could probably run this firmware with pin
adjustments, but that path isn't wired through the rest of the project,
so stick to Nano unless you're prepared to redo those parts too.)

1. Plug the board into your computer via USB.
2. In the Arduino IDE: Tools → Board, pick your board (e.g. "Arduino
   Nano"). Tools → Port, pick the port that appeared when you plugged in.
   If using a CH340 clone and it doesn't show up, you may need the CH340
   USB driver - search "CH340 driver" for your OS.
3. Open File → Examples → 01.Basics → Blink and upload it (the arrow
   button, top-left).

**Success looks like**: the board's built-in LED blinks once a second.
That confirms the board, drivers, and IDE setup all work - before you've
wired anything else in, so if something's wrong later, it's not this.

## Phase 2 — add the sensor

**Have ready**: VL53L0X breakout (e.g. a GY-53 board), breadboard, 5
jumper wires.

> **Read this before wiring if you have a GY-53.** A GY-53 is not a bare
> VL53L0X breakout - you can spot the difference instantly by its extra
> pins: `TX`, `RX`, `PWM`, `PS`. Those exist because the board carries its
> own onboard microcontroller sitting between you and the sensor chip, and
> the `PS` pin decides which of two mutually exclusive modes that MCU runs
> in:
>
> | PS pin | What the module does |
> |---|---|
> | **high (pulled up on-board - the factory default)** | UART/serial mode. The onboard MCU owns the sensor and streams distance over TX/RX + PWM. **I2C is completely dead.** |
> | **tied to GND** | I2C mode. The MCU steps back; you address the VL53L0X chip directly - what this project's firmware expects. |
>
> So **`PS → GND` is a required wire**, not an optional extra. Skip it and
> the sketch below reports "Failed to detect" forever, no matter how
> perfect the other four wires are.

1. Wire the sensor to the board (no soldering yet - breadboard only):
   - VL53L0X VIN → board 5V (or 3V3, check your breakout's rating)
   - VL53L0X GND → board GND
   - VL53L0X SDA → board A4 (Nano) / SDA pin
   - VL53L0X SCL → board A5 (Nano) / SCL pin
   - VL53L0X PS → GND (**GY-53 only**, see the box above - either GND pin
     on the module works, they're the same net, and the one on the same
     side as PS is the shortest jumper)
2. Open `firmware/hardware_tests/01_sensor_only/01_sensor_only.ino` and
   upload it.
3. Open Tools → Serial Monitor, set the baud rate to 115200.

**Success looks like**: a stream of `distance_mm=...` numbers that go up
when you move your hand away from the sensor and down when you move it
closer.

**If you see "Failed to detect VL53L0X sensor"**, work through these in
order - the first one is by far the most likely and the least obvious:

1. **`PS` isn't tied to GND** (GY-53 only). See the box above. This looks
   identical to a wiring fault from every angle, which is exactly what
   makes it expensive: an I2C bus scan finds nothing at any address, and
   probing SDA/SCL shows them flickering seemingly at random. That
   flickering is not a loose wire - it's the onboard MCU running its own
   I2C traffic to the sensor chip while in UART mode.
2. **SDA and SCL swapped.** A4 is SDA, A5 is SCL, not the other way round.
3. **A wire that isn't actually in the row you think it is.** Trace each
   one physically, pin to pin, rather than by eye from above.
4. **A cold solder joint** on the module's header - connected-looking but
   electrically open. Reflow anything that looks dull or balled-up.

## Phase 3 — add the motor driver (separately, sensor still connected)

**Have ready**: vibration motor, NPN transistor (2N2222A), a resistor
(220Ω-1k both work as the base resistor), 1N4148 diode, a few more jumper
wires.

1. Leave the sensor wired as-is. Add the motor circuit on the breadboard:
   - Board pin 9 → resistor → transistor base
   - Motor + → board 5V (fine for this bench test; the real device will
     power the motor from the battery instead, later)
   - Motor − → transistor collector
   - Transistor emitter → GND
   - Flyback diode across the motor leads, with the striped end (cathode)
     toward the 5V side
2. Open `firmware/hardware_tests/02_motor_only/02_motor_only.ino` and
   upload it. This test ignores the sensor entirely - it's here to
   isolate motor-circuit problems from sensor problems.

**Success looks like**: the motor ramps from off to full strength and back
down, repeating, with a noticeable buzz at the top of each ramp. If
nothing happens, the most common mistake is a transistor pin swapped
(base / collector / emitter look similar but aren't interchangeable) -
check its datasheet pinout against how you wired it before assuming the
code is wrong.

## Phase 4 — combine: the real firmware

**Have ready**: nothing new - same breadboard wiring as Phase 3 (sensor +
motor both connected).

1. Upload the actual `firmware/obstacle_haptic/obstacle_haptic.ino` (the
   IDE will also need `HapticMapper.h` - keep it in the same folder as
   the `.ino` file, Arduino IDE picks up sibling files automatically).
2. Open Serial Monitor at 115200 baud to watch `distance_mm=` readings
   (the `DEBUG_SERIAL` flag at the top of the file needs to be set to `1`
   for this - it defaults to `0`, so flip it and re-upload if the monitor
   stays silent).

**Success looks like**: the exact behavior from `haptic_simulator.html` -
motor off beyond ~1.8m, slow pulse from 1-1.8m, faster pulse from
0.4-1m, continuous strong vibration under 0.4m (these are
`HapticMapper.h`'s actual current thresholds - `kFarThresholdMm=1800`,
`kMediumThresholdMm=1000`, `kNearThresholdMm=400` - not the older 2m/0.5m
numbers from earlier drafts of this project). Wave your hand toward the
sensor and feel it change zones. If the zones feel off, tune the numbers
at the top of `HapticMapper.h`, re-upload, and compare against the
simulator side by side.

## Phase 5 — add power (battery + charger)

**Have ready**: battery, TP4056 charge module (the protected version).
As of the current `PURCHASE_LIST.md`, the battery actually sourced
walk-in is an **18650 Li-ion cell**, not a flat LiPo pouch - if that's
what you have, this phase works the same way electrically, it's only
`enclosure.scad`'s fit (Phase 7) that's affected. If you found a flat
LiPo instead, even better, same wiring either way.

1. Wire the battery's connector into the TP4056's battery terminals.
2. Charge it fully via the TP4056's USB port before first use - watch for
   its LED to indicate "charged" (check the module's markings/datasheet
   for which color means what, it varies by board).
3. Wire the TP4056's output (B+/B− or OUT+/OUT−, check your module's
   silkscreen) to the board's **5V pin** - not VIN. This project skips a
   boost converter (see `README.md`'s power note), so the board runs on
   the battery's raw ~3.7-4.2V fed straight into 5V, rather than through
   VIN's onboard regulator, which needs a higher input voltage than a
   single-cell battery provides and wouldn't work here at all. Disconnect
   the USB cable once the battery's wired in.

**Success looks like**: everything from Phase 4 still works, now running
untethered off the battery. This is the point where it stops being a
bench setup and starts being an actual wearable.

## Phase 6 — move to permanent soldering

Once the breadboard version reliably passes Phase 4/5 - don't solder
before that, breadboard connections are for finding mistakes cheaply.

1. Re-wire everything from Phase 2-5, but soldered instead of on the
   breadboard: solder wires directly to the motor leads, the transistor
   legs, and the sensor breakout's header pins.
2. Insulate every solder joint with heat-shrink tubing (slide it on
   before soldering that joint - easy to forget, and there's no fixing it
   after without cutting the joint apart again).
3. Re-run the Phase 4 test (upload `obstacle_haptic.ino` again) to
   confirm nothing broke in the transition from breadboard to solder.

## Phase 7 — 3D print the enclosure, then adjust it to fit

This is where `enclosure.scad` stops being a placeholder and starts
matching your actual parts.

1. Measure your real parts with calipers: the board's width/length/height
   (including any tall components like the USB connector), the sensor
   breakout, the motor's diameter and thickness, and the battery. **If
   your battery is the 18650 cell**, stop here first - the "[MEASURE YOUR
   PARTS]" section's `battery_length/width/thickness` variables assume a
   flat pouch cell, and an 18650 (18mm dia. × 65mm long) is a different
   shape entirely, not just different numbers. That's a real redesign of
   the battery bay (a cylindrical pocket instead of a rectangular one),
   not covered by this tutorial - see `enclosure.scad`'s battery comment
   and `PURCHASE_LIST.md`'s battery note before proceeding. If you found a
   flat LiPo instead, measure it and continue normally.
2. Open `enclosure/enclosure.scad` in OpenSCAD and update the numbers in
   the "[MEASURE YOUR PARTS]" section to match what you just measured.
3. Press F5 to preview, F6 to fully render. Check nothing looks wrong -
   the `part` variable near the **top** of the file (just above
   "[MEASURE YOUR PARTS]") controls which piece renders:
   `"wristband_back"` (the v1 base - `"base"` is a synonym for the same
   thing), `"lid"`, `"belt_clip_back"` (the alternative mount), or
   `"all"` to lay out all three side by side, which is the default.
4. File → Export → Export as STL. Set `part = "wristband_back";` and
   export, then set `part = "lid";` and export again. Skip
   `belt_clip_back` for now - the wristband strap slots are the v1 mount.
5. Print the base and lid. Test-fit before gluing anything - place each
   real component into the printed base:
   - **Too loose** (parts slide around)? Increase that part's dimension
     by 1-2mm in the "[MEASURE YOUR PARTS]" section - or just add a bit
     more foam tape/glue to take up the slack, which is often simpler
     than a reprint for a small gap.
   - **Too tight** (part doesn't fit, or the shell looks visibly
     strained)? Increase `fit_clearance` slightly (it's a global
     clearance added around every component pocket), or increase that
     specific part's measured dimension by 1-2mm, then re-render and
     reprint just the base.
   - **Lid won't go on at all** (too tight)? **Increase**
     `lid_lip_clearance` - that variable is the friction-fit gap between
     the lid's inner lip and the base's inner wall, and a bigger value
     means a smaller, looser-fitting lip. (This is the opposite direction
     from what you might guess - worth double-checking against
     `enclosure.scad`'s own comment on that variable if the fit still
     feels wrong after adjusting.)
   - **Lid falls off / too loose**? **Decrease** `lid_lip_clearance`
     instead, for a bigger, tighter-fitting lip. If it's still loose at a
     small `lid_lip_clearance`, check `lid_lip_height` too (how deep the
     lip inserts) and also check that the base's opening wasn't printed
     slightly undersized - a common FDM dimensional-accuracy issue,
     worth measuring the actual printed cavity with calipers rather than
     assuming the model and the print agree.
6. Repeat step 5 until everything sits snugly. It's normal to reprint the
   base 2-3 times while dialing this in - that's expected, not a failure.

## Phase 8 — final assembly

1. Once the fit is right, mount components inside the base using hot glue
   or double-sided foam tape (per the notes in `enclosure.scad` - v1
   doesn't use screws or standoffs).
2. Thread the wristband strap through the two side slots.
3. Snap the lid on.

## Phase 9 — the actual test that matters

With a sighted spotter present (required, this is a safety step, not
optional): walk a short obstacle course blindfolded, guided only by the
vibration feedback. Success = no collision. This is the actual definition
of done for v1, from `README.md`.

## Phase 10 — don't skip this

Once the device works, the project still isn't done - see the "ethical
constraint" section in `CLAUDE.md` (titled "The one constraint that
overrides everything else"). The outreach emails in `outreach/` need to go
out (ideally they went out back in Phase 0-1, in parallel - if they
haven't yet, send them now), and no public writeup or demo should name or
show a real test user without their explicit consent.
