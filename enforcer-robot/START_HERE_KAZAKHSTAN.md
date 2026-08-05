# Start here — what to do from Kazakhstan, right now

You have no parts and nothing built. That is fine: **the next four weeks of
this project don't need hardware.** They need three things you can do today —
design, software, and getting an order moving. This file is the plan for that
window.

Checked **2026-08-05**. Prices in ₸ are what each shop's own site listed;
confirm before you buy.

---

## First, a flag worth resolving

The project is written toward **Jugend forscht**, which is a German
competition — entrants normally need school or residence in Germany.
`PURCHASE_LIST.md` prices the whole build against Berlin retailers for that
reason. If you're competing from Kazakhstan, that entry route probably
doesn't apply and you should target a Kazakh or international fair instead.

**This changes nothing about what you build.** The robot, the experiment, and
the writeup are the same either way. It changes two things only: where you buy
(this file) and which deadline you work back from. Sort it out this week,
because the deadline sets your whole schedule — don't let it block the work
below, which is identical under either answer.

---

## The one thing that matters this week

**Get the slow order moving.** From Kazakhstan, AliExpress is **2–5 weeks**,
sometimes longer. Everything else — design, code, planning — can happen while
those boxes are in the air, but nothing can compress the shipping. An order
placed this week arrives around week 3–5; an order placed in week 3 arrives
around week 6–8 and eats your build.

So: place the AliExpress order **before** you write a line of code.

---

## Where to buy, from Kazakhstan

Three tiers. Use all three — the split matters more than any single price.

### Tier 1 — Almaty walk-in (same day)

| Shop | Address | Good for |
|---|---|---|
| **Arduino Parts** | Толе Би 189д (уг. Гагарина), 3 этаж, офис 310 | MG90S servos, Arduino/Pi bits |
| **ChipDip.kz** | пр. Абылай Хана 18, Жетысуский р-н | MG90S, general components |
| **Alash Electronics** | ул. Кыз Жибек 104/1, Кок-Тобе 2 | Sensors, batteries, Pi 5 — your wristband shop |

⚠️ **Alash lists the SG90, which is the plastic-gear version.** `PARTS.md` is
blunt that metal gears are not optional — plastic SG90s strip under leg load,
and you'd be replacing them mid-gait-tuning. Buy **MG90S** specifically, and
check the box says metal gear.

### Tier 2 — Kazakh online (days)

| Item | Shop | Price | Note |
|---|---|---|---|
| **MG90S servo** | AmperMarket.kz | **1 950 ₸** | 43 in stock when checked — buy **15** |
| **Raspberry Pi 5, 4GB** | Alash Electronics | **75 000 ₸** | Also on Kaspi.kz as a Starter Kit |
| microSD, cables, power | Kaspi.kz | — | Fast, and you already know it |

15 × MG90S ≈ **29 250 ₸**. Worth noting: that's *cheaper than Germany*, where
the same 15 servos come to €62.40. Servos are the one line where being in
Kazakhstan helps you.

### Tier 3 — AliExpress (2–5 weeks — order first!)

Everything small, generic, and unstocked locally. One order, with spares:

- PCA9685 16-channel PWM driver **×2**
- **Rectangular** SPI display, 1.3" ST7789 240×240 (~$4) — the face. This is
  the part that was *out of stock everywhere in Germany*; on AliExpress it's
  trivial. One of the few places the KZ route wins outright.
- TCRT5000 IR sensors ×4 (cliff detection)
- VL53L0X ToF ×2 — you already know this sensor from the wristband
- MAX98357A I2S amp + small speaker
- Mini water pump 3–6V ×2, silicone tubing, nozzle
- IRLZ44N MOSFETs ×5, 1N4007 diodes ×10
- UBEC 5–6V/5A, buck converter 5V/5A
- Pan/tilt bracket + 2 servos
- 2S LiPo 7.4V 2200mAh + XT60, balance charger, **LiPo-safe bag**

⚠️ **LiPo batteries often can't ship internationally by air.** Plan to buy the
battery, charger, and LiPo bag **locally in Almaty** — check Kaspi and the RC
/ modelling shops. Don't discover this when the rest of the order lands.

### Don't forget the printer

`PARTS.md` says your 3D printer is broken, and you now have STLs to print
(`cad/stl/`). Two moves, both doable this week:

1. **Diagnose it** — mechanical faults (nozzle, belts, bed, PTFE) are cheap and
   fixable locally; electronic faults need a part with the same shipping lead
   time as everything else, so it must ride in *this* order.
2. **Price a local print service.** Almaty has 3D printing shops. Getting one
   leg's worth printed (1 coxa bracket, 1 femur, 1 tibia) is cheap, and it
   test-fits your servo pockets against a real MG90S long before you commit to
   printing all four legs.

---

## What to build while the parcels fly

This is the real work of the next month, and none of it needs a single part.
It is also exactly what worked on the wristband: `HapticMapper` and
`haptic_simulator.html` were both debugged before hardware existed.

### 1. The mood state machine (highest value — do this first)

The personality *is* this state machine. CHILL → SUSPICIOUS → WARNING →
STRIKE → SMUG, driven by a `scene` object.

- Feed it **fake** scene events: `phone_visible`, `head_down`, `no_person`.
- Get the **timers and hysteresis** right. This is the hard part and it needs
  zero hardware. A robot that squirts you while you're working is a bad robot;
  the whole difference between "impressive" and "annoying" lives in these
  thresholds.
- Unit-test it: phone visible 2s → no fire; 4s → escalate; person returns
  mid-escalation → de-escalate cleanly, not stuck.
- Browser visualiser, like `haptic_simulator.html`, so you can *see* it.

### 2. The leg IK simulator

`cad/make_stl.py` already has `leg_ik()` and `leg_fk()` written and
round-trip tested. **Port them; don't rewrite them.** Use the same three link
lengths (coxa 28, femur 50, tibia 55) or the sim will lie to you.

- Drag a foot target, watch three joint angles solve.
- Test the unreachable case — a leg commanded past 105mm reach must fail
  loudly, not silently produce a NaN that shows up as a servo slamming.
- Then the gait: a quadruped must **shift its weight** over three feet before
  lifting the fourth. Simulate that weight shift now; it's the part that
  surprises people in week 8.

### 3. Detection, on video files

You don't need the Pi or the camera to start perception. Record 20 minutes of
yourself at a desk on your phone — working, picking up your phone, leaving —
and run YOLOv8n + MediaPipe over the footage on your laptop.

- Label "working" vs "on phone" vs "gone" by hand, then measure how often the
  detector agrees.
- **This gives you real false-positive numbers before you own a robot**, which
  is the single most valuable thing you can have going into week 5.

### 4. The experiment and the paperwork

Costs nothing, and it's what turns the gag into a project:

- Write the consent form (you already do this well on the wristband).
- Write the questionnaire: motivation 1–5, annoyance 1–5, "would you use this?"
- Decide exactly what you log: phone pickups, on-task minutes.
- Line up 8–15 volunteers now — recruiting always takes longer than expected.
- Pin down which competition, and its real deadline.

---

## Suggested order of the next four weeks

| When | Do |
|---|---|
| **This week** | Resolve the competition question. Place the AliExpress order. Diagnose the printer. Buy 15× MG90S locally. |
| **Week 1** | Mood state machine + tests + browser visualiser. |
| **Week 2** | Leg IK sim; print one leg locally and test-fit a servo. |
| **Week 3** | Record desk footage; run detection on it; measure false positives. |
| **Week 4** | Consent form, questionnaire, volunteer list. Parts start landing. |

By the time the boxes arrive you have: a tested personality, a tested IK, real
detection numbers, and an approved experiment. That's the difference between
assembling a robot and assembling a *project*.

---

## What not to do yet

- **Don't buy the chassis kit yet.** You have printable STLs. Decide after
  the printer diagnosis and one test print.
- **Don't buy a Coral/Hailo accelerator.** `PARTS.md` is right — try the Pi
  alone first. It's ~€60–70 for a problem you may not have.
- **Don't build the water rig before the state machine works.** The pump is
  the easy part; knowing *when* to fire is the hard part.
- **Don't skip the metal-gear check** on the servos. It's the one local
  purchase that's easy to get wrong.
