# Build Checklist

Parts and tools needed, grouped by the phase you'll need them in. No
prices/links here on purpose - see [`PURCHASE_LIST.md`](PURCHASE_LIST.md)
for real store links, prices, and quantities (2026-07-25 snapshot).

## Week 0 — Outreach

- [ ] Fill in placeholders in `outreach/outreach_email_verband.md` (name,
      parent/guardian co-signer, contact email)
- [ ] Fill in placeholders in `outreach/outreach_email_schule.md`
- [ ] Parent/guardian has read and agreed to co-sign both
- [ ] Send both emails
- [ ] Nothing else in this checklist blocks on a reply - keep building in
      parallel while waiting

## Weeks 1-2 — Breadboard prototype

Parts:
- [ ] Arduino Nano (CH340 clone, USB-C)
- [ ] USB-C cable (data-capable, not charge-only)
- [ ] VL53L0X time-of-flight sensor breakout (GY-53 or similar - no
      walk-in Almaty store stocks a VL53L1X as of this writing, see
      PURCHASE_LIST.md)
- [x] Vibration motor (10×3mm "pancake" type) - ACQUIRED, working. Its
      leads are too thin for a breadboard; solder each to a cut-in-half
      jumper wire first (see tutorial.md Phase 3)
- [ ] 2N2222 NPN transistor
- [ ] 1N4148 diode (flyback protection)
- [ ] Resistor, 220Ω-1k (either works as the transistor base resistor)
- [x] LiPo battery - ACQUIRED: flat 502030 pouch, `YS 502030 3.7V 250mAh
      0.925Wh`. **Charge current must be reduced before routine use** -
      stock TP4056 charges it at ~4C, see PURCHASE_LIST.md's battery note
- [x] TP4056 Li-ion charge module - ACQUIRED, battery soldered to B+/B-,
      charging confirmed
- [ ] **Replace the TP4056's `R3` with ~10kΩ** to bring charge current
      down to ~120mA. Highest-priority open item; supervise all charging
      until done
- [ ] (optional) 5V boost converter module - see PURCHASE_LIST.md's power
      note; the current list skips this and wires the LiPo straight to 5V
- [x] **Power switch — ACQUIRED**: 6 slide switches (3 types, 50 тг each)
      from an Almaty counter, uncatalogued online. **Use the 4-pin type**
      — smallest body; the 6- and 8-pin ones are multi-pole and bigger.
      Wire it in series on the TP4056's **OUT+** line, between OUT+ and
      the Nano's 5V pin, so switching off cuts the load while the battery
      still charges over USB.
- [ ] **Identify which two switch pins make/break** with the D2→D3
      continuity sketch, and confirm the slider LATCHES rather than
      springing back. See PURCHASE_LIST.md's power-switch note
- [ ] **Print `part="switch_test_coupon"`** from enclosure.scad and find
      the smallest slot the actuator travels freely in — that sets
      switch_slot_length/width without needing to measure the nub
- [ ] Solderless breadboard
- [ ] Jumper wire kit (male-male at minimum)

Tools/software:
- [ ] Computer with Arduino IDE (or arduino-cli) installed
- [ ] "VL53L0X" Arduino library by Pololu, installed via Library Manager
      (not the VL53L1X one - different chip, different library)
- [ ] A C++ compiler for desktop unit tests - `g++` is enough
      (`firmware/tests/run_tests.sh` expects it on PATH)

Steps:
- [ ] Run `firmware/tests/run_tests.sh`, confirm `14/14 tests passed`
      before touching hardware
- [ ] Wire the breadboard per `README.md`'s wiring diagram
- [ ] Flash `firmware/obstacle_haptic/obstacle_haptic.ino`
- [ ] Set `DEBUG_SERIAL 1` in the `.ino`, confirm sane distance readings
      over serial at 115200 baud before trusting the motor output
- [ ] Cross-check thresholds against `firmware/simulator/haptic_simulator.html`
      side by side with the real sensor

## Weeks 3-4 — Wearable enclosure

Parts:
- [x] Wristband strap - 20mm, matches `strap_width` in `enclosure.scad`
- [ ] PLA (or similar) filament for 3D printing
- [ ] Small glue gun + glue sticks. The enclosure itself doesn't need glue
      to hold together, but the current design *does* rely on it for
      assembly: all three boards are glued to the lid's underside, the
      switch body is glued behind its slot, and the motor is glued to an
      inside wall

Tools:
- [ ] Calipers (for measuring real part dimensions - do this before
      touching `enclosure.scad`'s remaining placeholder numbers)
- [ ] OpenSCAD installed
- [ ] Access to a 3D printer (own, school, library, print service)

The model is built to the sketched box: **72mm long (along the arm) × 34mm
wide × 52mm tall**, on a 7.2mm strap plinth underneath. Sensor window in
the front wall, switch slot in the back wall, both USB ports in the lid,
one 20mm strap tunnel through the plinth. The base prints 59.2mm tall and
the assembled pod is 61.4mm.

Everything inside is located by a printed feature and held by glue: board
pockets hang from the lid, the sensor gets a frame on the front wall, the
motor gets a ring on the floor.

Measure before printing:
- [ ] **Print `part="switch_test_coupon"` first.** Two minutes, a few
      grams, and it settles `switch_actuator_length`/`_width` - the
      largest remaining guess in the file - without measuring a 2mm nub
- [ ] Measure how far the USB connector *bodies* stand proud of their
      boards, and set `usb_body_margin` from that. The lid counterbore is
      what lets a plug reach the receptacle through 5.2mm of lid; guess it
      too small and both ports are unusable, which won't be obvious until
      the print is in your hand
- [ ] **Measure the TP4056 board** - `tp4056_length/width/stack_height`
      are placeholders. The numbers taken on 2026-08-02 were its
      connector, not the board
- [ ] **Measure where the VL53L0X's lens sits relative to the centre of
      its breakout**, and set `tof_lens_offset_y/z`. Both default to 0,
      i.e. "chip is centred", and on a GY-53 it isn't. Get this wrong and
      the sensor looks at the inside of the wall and reads a permanent
      obstacle - the device would work, it would just always buzz
- [ ] Measure the Nano's stack height with its headers soldered on - it
      sets how wide the Nano's pocket is
- [ ] Update the "[MEASURE YOUR PARTS]" block at the top of
      `enclosure/enclosure.scad` with all of the above
- [ ] Re-render in OpenSCAD (F5 preview, then F6 for a full render) and
      re-check `part = "all"` looks sane before exporting STLs

Printing:
- [ ] Print `lid` **plate-down on the bed** - the pockets and the lip both
      stand up off it, so nothing overhangs and no supports are needed
- [ ] Print the base **open-side-up, with supports** (or accept some
      droop): the box floor bridges 21.5mm over the strap tunnel
- [ ] Treat `belt_clip_back` as a separate print-and-test iteration, not a
      guaranteed-good part

Assembly:
- [ ] Dry-fit every board in its pocket before any glue
- [ ] **Glue the boards with the lid upside down on the bench.** The
      pockets become open-topped cups, each board drops in connector-end
      first, and gravity holds it while the glue sets
- [ ] Check both plugs actually seat in the lid's holes *before* gluing
      the second board - if the counterbore is too shallow you want to
      find out with one board in, not three
- [ ] Sensor into its cradle last, pushed flat against the front wall
- [ ] Lower the lid onto the base with the wires tucked in

## Weeks 4-6 — Real feedback session

- [ ] Fully assembled, working prototype (breadboard is fine, doesn't
      need to be in the final enclosure yet)
- [ ] Sighted spotter arranged for any mobility test
- [ ] Simple test course planned (start with a stationary-obstacle
      hallway, not a dynamic/crowded space)
- [ ] Parent/guardian available to accompany any in-person meeting
- [ ] Consent conversation had with the test user *before* any test,
      covering: what the device is, what it isn't (see README's "before
      you read any further"), and what will/won't be shared afterward

## Writeup + consent

- [ ] Explicit written consent obtained before naming or showing any test
      user in a writeup, demo, or competition submission
- [ ] Writeup honestly represents what was and wasn't tested - see
      README's "Status" and "Safety notes" sections for the current, real
      state (not the idealized one)
- [ ] Photos/video of the test user only with separate, explicit
      permission - consent to participate is not consent to be filmed
