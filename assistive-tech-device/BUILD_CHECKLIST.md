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
- [ ] VL53L1X time-of-flight sensor breakout
- [ ] Vibration motor (10×3mm "pancake" type)
- [ ] 2N2222 NPN transistor
- [ ] 1N4148 diode (flyback protection)
- [ ] 220Ω resistor
- [ ] LiPo battery (~350-500mAh)
- [ ] TP4056 Li-ion charge module
- [ ] 5V boost converter module
- [ ] Slide or toggle switch
- [ ] Solderless breadboard
- [ ] Jumper wire kit (male-male at minimum)

Tools/software:
- [ ] Computer with Arduino IDE (or arduino-cli) installed
- [ ] "VL53L1X" Arduino library by Pololu, installed via Library Manager
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
- [ ] Wristband strap (width matches `strap_width` in `enclosure.scad`)
- [ ] PLA (or similar) filament for 3D printing
- [ ] Small glue gun + glue sticks (securing components inside the pod,
      not structural - the enclosure itself shouldn't need glue to hold
      together)

Tools:
- [ ] Calipers (for measuring real part dimensions - do this before
      touching `enclosure.scad`'s placeholder numbers)
- [ ] OpenSCAD installed
- [ ] Access to a 3D printer (own, school, library, print service)

Steps:
- [ ] Measure Nano, VL53L1X breakout, motor, and battery with calipers
- [ ] Update the "[MEASURE YOUR PARTS]" block at the top of
      `enclosure/enclosure.scad` with real numbers
- [ ] Re-render in OpenSCAD (F5 preview, then F6 for a full render) and
      re-check `part = "all"` looks sane before exporting STLs
- [ ] Print `wristband_back` + `lid` first; treat `belt_clip_back` as a
      separate print-and-test iteration, not a guaranteed-good part
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
