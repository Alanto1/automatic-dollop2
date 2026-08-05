# Parts — The Enforcer

Two shopping lists, because this is two projects stacked:

- **A. Sesame** — the body. Buy exactly what
  [its BOM](https://github.com/dorianborian/sesame-robot/blob/main/hardware/bom/README.md)
  says. Don't improvise here; it's a known-good design and substitutions are
  how you end up debugging someone else's robot.
- **B. The Enforcer layer** — the brain, the eyes, and the water. This is
  your project.

Verified German prices and stock: [`PURCHASE_LIST.md`](PURCHASE_LIST.md).

---

## A. Sesame (the body) — ~$50–60 / ~€60–75

From the upstream BOM, checked 2026-08-05:

| # | Item | Qty | Notes |
|---|---|---|---|
| 1 | **MG90S all-metal micro servo, 180°** | **8** (+2 spare) | The hip/leg actuators. Metal gear is not optional — plastic SG90s strip under leg load |
| 2 | **SSD1306 OLED, 0.96", 128×64, I2C** | 1 | The face. Monochrome is fine and actually *helps* — two crisp eyes read better than a fuzzy colour blob |
| 3 | **Lolin/WeMos ESP32-S2 Mini** | 1 | Or the custom *Sesame Distro Board V3* PCB (cleaner, needs fabbing) |
| 4 | Small protoboard + 3-pin headers | 1 set | For the hand-wired harness (Option A) |
| 5 | **Buck converter, 5V/3A** | 1 | |
| 6 | **7.4V Li-ion pack, ~800mAh** + matching charger | 1 | Upstream specifies a Bambu Lab 14500. Any 2S pack of that size works — check it physically fits the undercarriage |
| 7 | XH2.54 female pigtail | 1 | Battery connector |
| 8 | KCD1 rocker power switch, panel mount | 1 | |
| 9 | 22AWG + 30AWG silicone wire, heat-shrink, zip ties | — | |
| 10 | **M2 × 5mm self-threading screws** | ~40 | Buy 60. You will lose some |
| 11 | M2.5 × 5mm machine screws | 10 | |
| 12 | PLA filament | ~1 kg | 11 printed parts, "minimal supports" |

**Two parts German maker shops don't stock** (checked BerryBase + Reichelt):
the **ESP32-S2 Mini** and the **0.96" SSD1306**. Both are routine, cheap
AliExpress/Amazon items. See `PURCHASE_LIST.md` for what *is* stocked and the
substitutions that work.

## B. The Enforcer layer (yours)

### The brain — lives on the desk, not on the robot

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 13 | **Raspberry Pi 5** | 1 | 69,50 (2GB) / 118,50 (4GB) | Runs YOLOv8n + MediaPipe + the state machine. **Not** on the robot — see README architecture |
| 14 | **Camera** (Pi Camera Module 3 or USB webcam) | 1 | 15–29 | Sees you *and* the robot. A fixed desk camera can use the ribbon happily — no cable fatigue, since it doesn't move |
| 15 | microSD 32GB | 1 (+1 spare) | 15,60 ea | The spare is real advice; cards die at the worst moment |
| 16 | Pi PSU (USB-C) | 1 | 12 | It's on a desk — mains is fine here, unlike on the robot |

Because the Pi is stationary and mains-powered, **it needs none of the power
engineering the robot does.** That deletes the UBEC, the second rail, the
common-ground problem, and the brownout risk from the original design. This
is the single biggest simplification in the whole rework.

### The water rig — the signature

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 17 | **Mini water pump, 3–6V** | 1 (+1 spare) | 3–8 | Submersible ones sit *inside* the bottle; self-priming ones sit beside it. Affects the bracket — decide before printing |
| 18 | **Logic-level MOSFET** (IRLZ44N) | 3 | 0,70 ea | Your wristband's transistor driver, scaled up for the pump's current |
| 19 | **Flyback diode** (1N4007) | 5 | 0,05 ea | Across the pump. Same role as the 1N4148 on your vibration motor |
| 20 | Silicone tubing + narrow nozzle | — | 3 | Aquarium airline tubing is ideal. Narrow nozzle = focused squirt at low flow |
| 21 | Small reservoir, 50–100 ml | 1 | 3 | **Start at 50ml.** Water is 1g/ml and Sesame is small — see README "Honest hard parts" |

⚠️ **Do not run the pump off Sesame's battery without testing.** The firmware
already staggers servo moves by 20ms because all-at-once browns out the board.
A pump is exactly that kind of load. Give it a separate cell, or a fat
capacitor, and re-test.

### Sensors

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 22 | **TCRT5000 down-facing IR** (cliff) | 4 | 0,30 ea | Mandatory before any autonomous walking |
| 23 | **VL53L0X ToF** | 1–2 | 8–19 | Optional. You know this sensor and its library from the wristband |

### What to skip

- **PCA9685** — not needed. The ESP32 drives all 8 servos directly; that's
  what Sesame's firmware does. (The old 12-servo design needed one.)
- **Pan/tilt bracket** — not needed. Aiming is turning the robot, commanded
  from the desk camera. See README.
- **UBEC / second power rail** — not needed once the Pi is off-board.
- **IMU/gyro** — Sesame doesn't use one. Don't add complexity it doesn't need.
- **Coral/Hailo accelerator** — try the Pi alone first. ~€60–70 for a problem
  you may not have.
- **Local LLM** — you don't need conversation. The personality is the state
  machine, not a chatbot.

## Rough total

| | € |
|---|---|
| A. Sesame body | ~60–75 |
| B. Brain (Pi 2GB + camera + cards) | ~115–135 |
| B. Water rig + sensors | ~20 |
| **Total** | **~195–230** |

With the 4GB Pi instead: **~245–280**.

Compare against the previous 12-servo, Pi-on-board design, which came out at
**~€450**. Adopting Sesame roughly **halves the build cost** — mostly by
deleting the power engineering and the parts that existed to carry a Pi
around.

## The 3D printer situation

Sesame is **11 printed parts** in PLA with minimal supports, and its parts are
deliberately oriented to print without support material. That's the good news.

Your printer is broken — diagnose it in the first 48 hours:

- **Mechanical** (nozzle, belts, bed, PTFE): cheap, fix locally this week.
- **Electronic** (driver, thermistor, board): order the part in the same
  order as everything else, or shipping serialises your whole schedule.
- **Hard gate:** if it isn't printing dimensionally-accurate parts by end of
  week 2, pay a print service. Sesame's parts are small; a print shop quote
  for 11 parts is cheap against losing three weeks. Print a 20mm calibration
  cube first — if it's not within ~0.3mm, the printer isn't ready for parts
  that have to hold servo splines.
