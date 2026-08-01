# Parts list — AI quadruped

Budget target: **$150–300**. The build below lands around **$230** with
spares, leaving headroom for the things you always forget (wire, screws,
a second SD card, a servo you destroy).

## Read this before ordering

**These are specifications, not verified local stock.** Unlike
`assistive-tech-device/PURCHASE_LIST.md` — which was walked into real
Almaty shops and checked on a real date — nothing here has been confirmed
on a shelf or a site. Treat it as "what to look for," then do a sourcing
pass the way you did for the wristband: Alash Electronics and the Тастак
shops (RadioBazar бутик 37, Ba3ar.kz бутик 22) for anything generic,
Kaspi.kz for the bigger items, AliExpress for whatever's missing.

**Order once, in week 1, and order spares.** Almaty lead times ran 3–6
weeks on the last project. A stripped servo in week 6 should cost you an
evening, not a month.

## The order

| # | Item | Qty | ~USD | Notes |
|---|---|---|---|---|
| 1 | **MG90S metal-gear servo** | 12 + 3 spare | 45 | Metal gear is not optional — plastic-gear SG90s strip under leg loads. Buy the spares. |
| 2 | **PCA9685 16-ch PWM driver** | 1 | 4 | I2C. 16 channels covers 12 legs + 2 spare for a head/tail later. |
| 3 | **Raspberry Pi 5, 4GB** | 1 | 65 | Pi 4 (2GB) works and saves ~$20 if needed. Pi Zero 2 W is too weak once camera + audio + streaming run together. |
| 4 | microSD, 32GB A2 | 1 + 1 spare | 14 | The spare is real advice. Cards die and they die at the worst time. |
| 5 | **GC9A01 1.28" round SPI LCD** | 1 (or 2) | 8–16 | The eye. Highest impact-per-dollar item in the whole list. Two eyes if you want it uncanny. |
| 6 | USB webcam (720p+) | 1 | 12 | Simpler than the Pi Camera ribbon for a moving robot, and OpenCV-friendly. Pi Camera Module 3 (~$25) if you want autofocus. |
| 7 | USB microphone | 1 | 15 | A small USB conference mic beats a cheap electret module by a wide margin. Audio quality is most of your speech-recognition accuracy. |
| 8 | MAX98357A I2S amp + 3W speaker | 1 | 8 | Or any small powered speaker on the 3.5mm/USB. Louder than you think you need — demo halls are loud. |
| 9 | **2S LiPo, 7.4V 2200mAh+, XT60** | 1 | 22 | The servo rail. Capacity here is demo runtime. |
| 10 | **UBEC 5–6V, 6A+** | 1 | 8 | Servo rail regulator. Do not run servos off the Pi. |
| 11 | Buck converter 5V/5A | 1 | 6 | Separate logic rail for the Pi. **Common ground with the servo rail.** |
| 12 | LiPo charger (2S balance) | 1 | 15 | Plus a LiPo-safe charging bag. Non-negotiable. |
| 13 | Power switch + inline fuse (10A) | 1 | 3 | The fuse is what stands between a shorted servo lead and a fire. |
| 14 | M2/M3 screw + standoff assortment | 1 | 8 | You will use more than you expect. |
| 15 | Silicone wire, JST connectors, heatshrink | — | 8 | 22AWG for logic, 18AWG for the servo rail. |
| 16 | PLA/PETG filament | 1kg | 20 | PETG if the robot will ever sit in a hot car or window. |
| | **Total** | | **~230** | |

## If the printer stays broken

Skip line 16 and add a **kit chassis**: a laser-cut acrylic or aluminium
quadruped frame, roughly $30–60, usually sold as a "12 DOF quadruped
robot frame" and often bundled with servos (check which servos — some
bundles ship plastic-gear ones, which puts you back at line 1).

Bundled kits can bring the total down rather than up. Buying the frame is
not a defeat; it moves your effort to the part of this project that's
actually original.

## Printer repair parts — decide in the first 48 hours

Diagnose before you order anything else, so that any printer part rides
along in the same shipment:

- **Mechanical** (clogged nozzle, belt tension, bed level, worn PTFE
  tube): cheap, locally available, fix it this week. Add a spare nozzle
  set (~$5) and a PTFE tube (~$3) regardless — they're consumables.
- **Electronic** (dead stepper driver, bad thermistor, fried mainboard):
  order the replacement **now**, in the week-1 order. Discovering this in
  week 4 costs you the schedule.

## What to skip

- **IMU / gyro.** Tempting, and unnecessary if you use a statically
  stable crawl gait (three feet down at all times). Add it only if you go
  for a dynamic trot later.
- **Servo feedback / smart serial servos.** Much nicer, roughly triple
  the price. Not worth it at this budget.
- **Local LLM on the Pi.** Painful and slow. Use a cloud API with a
  hotspot, and keep hard-coded fallbacks for when the network dies.
- **LiDAR.** Costs more than the rest of the robot and adds nothing to
  the demo.

## Power wiring, in one place

```
2S LiPo ──┬── fuse ── switch ──┬── UBEC 6V/6A ──► PCA9685 V+ ──► 12 servos
          │                    │
          │                    └── buck 5V/5A ──► Raspberry Pi
          │
          └── balance lead ──► charger (when off the robot)

                 servo GND ──┬── Pi GND      ← common ground, single point
```

Two rails, one ground, one fuse. Get this right in week 4 and the rest of
the project stops being mysterious.
