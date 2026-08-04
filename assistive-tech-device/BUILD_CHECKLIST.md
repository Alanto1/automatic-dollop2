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

The model is built to the sketched box: **67mm long (along the arm) × 30mm
wide × 50mm tall**, on a 7.2mm strap plinth underneath. Sensor window in
the front wall, switch slot in the back wall, both USB ports in the lid,
one 20mm strap tunnel through the plinth. The base prints 57.2mm tall and
the assembled pod is 59.4mm.

Steps:
- [ ] **Print `part="switch_test_coupon"` first.** Two minutes, a few
      grams, and it settles `switch_actuator_length`/`_width` - the
      largest remaining guess in the file - without measuring a 2mm nub
- [ ] Measure how far the USB connector *bodies* stand proud of their
      boards, and set `usb_body_margin` from that. The lid counterbore is
      what lets a plug reach the receptacle through 5.2mm of lid; guess it
      too small and both ports are unusable, which won't be obvious until
      the print is in your hand
- [ ] Decide how the Nano hangs. The cavity is 44.8mm and the Nano's long
      edge is 45mm - 0.2mm short - so either hang it 18mm-edge-down, or
      raise `box_outer_height` to 51
- [ ] Update the "[MEASURE YOUR PARTS]" block at the top of
      `enclosure/enclosure.scad` with those numbers
- [ ] Re-render in OpenSCAD (F5 preview, then F6 for a full render) and
      re-check `part = "all"` looks sane before exporting STLs
- [ ] Print `wristband_back` + `lid` next; treat `belt_clip_back` as a
      separate print-and-test iteration, not a guaranteed-good part
- [ ] Print the base open-side-up, with supports (or accept some droop):
      the box floor bridges 21.5mm over the strap tunnel
- [ ] Dry-fit all components before gluing anything down

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
