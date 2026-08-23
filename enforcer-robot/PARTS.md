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
| 6 | **Bambu Lab 14500, 7.4V 800mAh Li-ion** + its **XH2.54 charger** | 1 (buy 2 packs) | Buy this exact pair. The pack has a BMS and a **2-pin** XH2.54 plug — so it needs a plain 8.4V charger, **not** a balance charger. Bare-LiPo balance chargers physically cannot connect to it |
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

### The brain — rides on the robot

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 13 | **Raspberry Pi Zero 2 W** | 1 | 19,40 (22,10 with headers) | 65×30mm, **11g**, ~2W. Quad A53 @ 1GHz, 512MB. The largest brain that fits Sesame's weight and power budget |
| 14 | **Camera for Pi Zero** | 1 | 15,90 | Comes with the narrow Zero-format ribbon |
| 15 | **CSI adapter, 15-pin → Zero** | 1 | 1,10 | ⚠️ Only if you use a full-size camera module. The Zero's connector is *narrower* than a standard Pi's — a normal camera cable will not fit |
| 16 | microSD 32GB | 1 (+1 spare) | 15,60 ea | The spare is real advice; cards die at the worst moment |
| 17 | Buck converter 5V | 1 | 4,90 | Feeds the Pi Zero from Sesame's 7.4V pack |

**Why not a Pi 5.** It's 85 × 56mm and draws ~6W — physically bigger than
Sesame and far past what an 800mAh pack supports. The Pi Zero 2 W is a
quarter the weight and a third the power. See README "Architecture" for what
that costs you in frame rate.

**If 512MB proves too tight**, a *Radxa Zero 3W* or *Orange Pi Zero 2W* is the
same footprint with up to 4GB. Weaker software support, so only reach for it
if the Pi Zero actually fails.

### The water rig — the signature

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 18 | **Mini water pump, 3–6V** | 1 (+1 spare) | 3–8 | Submersible ones sit *inside* the bottle; self-priming ones sit beside it. Affects the bracket — decide before printing |
| 19 | **Logic-level MOSFET** (IRLZ44N) | 3 | 0,70 ea | Your wristband's transistor driver, scaled up for the pump's current |
| 20 | **Flyback diode** (1N4007) | 5 | 0,05 ea | Across the pump. Same role as the 1N4148 on your vibration motor |
| 21 | Silicone tubing + narrow nozzle | — | 3 | Aquarium airline tubing is ideal. Narrow nozzle = focused squirt at low flow |
| 22 | **Wide-mouth bottle, ~60 ml** | 1 | 3 | Opening ≥26mm so the 23.5mm pump drops in. **Fill to 30ml**, not 60 — that's 29mm of depth in a 36mm bottle, enough to keep the intake covered at only 30g |
| 22b | **Electrolytic capacitor, 1000µF+ 16V** | 2 | 0,50 ea | Bulk capacitance across the servo rail. Needed for the motion engine — see README "Making it move like a creature" — and the standard fix for pump inrush |

⚠️ **Do not run the pump off Sesame's battery without testing.** The firmware
already staggers servo moves by 20ms because all-at-once browns out the board.
A pump is exactly that kind of load. Give it a separate cell, or a fat
capacitor, and re-test.

### Sensors

Both of these are **reflex** sensors read by the ESP32, not the Pi — see
[`BEHAVIOURS.md`](BEHAVIOURS.md) for why that split is not negotiable.

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 23 | **TCRT5000 down-facing IR** (cliff) | 4 | 0,30 ea | Mandatory before any autonomous walking |
| 24 | **VL53L0X ToF**, forward-facing | **2** (1 + spare) | 3–19 | **Required, and it does two jobs**: measures range so the robot only fires inside its calibrated band, *and* is the proximity trip for Warden. Vision at 1–2 FPS cannot catch a reaching hand. You already know this sensor from the wristband |

### Voice (optional layer — see [`LLM_VOICE.md`](LLM_VOICE.md))

| # | Item | Qty | ~€ | Notes |
|---|---|---|---|---|
| 25 | **MAX98357A I2S amp** + small 8Ω speaker | 1 | ~8 | Taunt clips. Pre-recorded clips need no LLM and no mic |
| 26 | **INMP441 I2S MEMS microphone** | 1 | ~4 | Only if you want it to *hear*. Shares the I2S bus with the amp |

**The LLM does not run on the robot** — 512MB can't hold a model, and the
smallest useful one needs 400MB on its own. It runs on a laptop over WiFi.
`LLM_VOICE.md` has the full RAM budget and the rule that keeps the LLM out of
the firing path.

### Tools you actually need

Not parts, but the build stalls without them. Easy to forget when costing a
project.

| Item | ~€ | Why it's not optional |
|---|---|---|
| **Digital caliper** | ~5 | `DECK_L`/`DECK_W` from Sesame's top cover, `BOTTLE_D` from your reservoir, and checking the 20mm calibration cube — three blocking measurements |
| **Multimeter** | ~25 | The week-3 brownout test, checking both rails, continuity on the harness. You cannot debug power without one |
| Temperature-controlled soldering iron | ~38 | ~40 servo/harness joints |
| Solder, flux, desoldering braid | ~15 | |
| Hot glue gun | ~12 | Strain relief — moving legs eat wires |
| **Small desk or USB fan** | ~10 | ⚠️ Not optional either — see below |

### Soldering in a bedroom

Yes, you can. The open window is not the part that makes it safe, though.

**What you're actually breathing is flux, not lead.** Lead boils at 1749°C
and your iron runs at ~350°C, so essentially no lead becomes airborne. The
white smoke is decomposing **rosin/colophony flux**, and colophony is a
recognised cause of occupational asthma. Sensitisation is cumulative and
permanent — you don't get to un-sensitise later.

**An open window alone does not help much**, because you lean over the joint
and the plume rises straight through your breathing zone before the room air
ever moves it. The window is the exhaust path, not the ventilation.

The fix costs about €10:

- **Put a small fan beside the work, blowing sideways across the joint**
  toward the open window. Across, not at you — a fan pointed at the board
  blows the plume into your face.
- **Keep your head out of the plume.** 30cm back and off to one side. If you
  need to be closer, use a magnifier, not your nose.
- Fume extractors with activated-carbon pads (~€25) work, but a fan plus an
  open window moves far more air for less money.

**Lead is a hands problem, not a lungs problem.** It transfers from solder to
fingers to your phone, food and face. So: **wash your hands with soap
afterwards**, and don't eat or drink at the bench. That is the entire lead
precaution and it matters more than any mask.

Note that **lead-free solder is not automatically safer here** — it needs a
higher tip temperature, which produces *more* flux fume. Leaded 60/40 at a
lower temperature with good extraction is a defensible choice for hobby work.

The rest is ordinary bench sense: the iron is 350°C and goes in its stand
*every* time, nothing flammable on the desk, don't solder on a bed or carpet,
and keep the isopropyl alcohol you clean flux with well away from the tip.

In a Berlin winter you will not want the window open. That is exactly when
the fan matters most — crack the window, run the fan, and work in short
sessions.

### Flux residue: clean it or leave it?

Small correction to the question first — flux doesn't need *drying*. Rosin
isn't wet; it cools from liquid to a hard, tacky solid the moment the iron
leaves. The real question is **remove or leave**, and the answer depends
entirely on which flux you used.

| Flux type | Where you meet it | Must you clean? |
|---|---|---|
| **Rosin core** (R / RMA) | Inside standard 60/40 solder wire | **No.** Residue is non-conductive and non-corrosive once cool. Electrically inert |
| **Rosin, activated** (RA) | Some flux pastes | Preferably yes — activators can be mildly corrosive |
| **No-clean** | Most modern flux pens and pastes | No — designed to stay. ⚠️ But clean it *fully or not at all*; a half-hearted wipe smears activators around and is worse than leaving it |
| **Water-soluble / organic acid** (OA) | Some paste fluxes | **Always, within hours.** Actively corrosive and hygroscopic — it will eat traces over months |
| **Acid / plumbing flux** | Hardware shops | Never use this on electronics at all |

⚠️ **Check the label on the KELLYSHUN flux before first use.** If it says
water-soluble or organic acid, cleaning becomes mandatory rather than
optional. If it says no-clean or rosin, it isn't.

**On this robot, clean it anyway.** Not for the electrical reason — for the
project-specific one: **this machine carries water and sprays it.** Flux
residue is tacky, so it collects dust, and dust plus a stray droplet is a
leakage path across a board that would otherwise be fine. A robot with a pump
on it is the wrong place to leave sticky residue.

There is a second reason worth naming: judges look at the build. A clean board
photographs well and signals care, and that costs you twenty minutes.

**How:**

1. **99% isopropyl alcohol** — not 70%. The water in 70% leaves its own
   residue and dries far more slowly. ~€6 for 500ml.
2. Scrub with a stiff brush — an old toothbrush is fine.
3. Blot with kitchen roll, or flood and let it run off.
4. **Let it evaporate completely before powering up.** 10–15 minutes in air.
   IPA carrying dissolved flux is not something you want across a live rail.

⚠️ **IPA is flammable** — iron in its stand and cooling before the bottle
comes out, and keep the fan from the section above running.

⚠️ **Don't flood modules.** IPA wicks under components and can get inside
switches, connectors and the OLED, and it lifts some screen printing. Brush
the joints on the perfboard; don't dunk the SSD1306 or the ESP32 module.


### What to skip

- **PCA9685** — not needed. The ESP32 drives all 8 servos directly; that's
  what Sesame's firmware does. (The old 12-servo design needed one.)
- **Pan/tilt bracket** — not needed. The robot yaws to aim, and the vertical
  angle is fixed once in the printed mounts. See README "Aiming is yaw-only".
- **UBEC / big second rail** — one small buck converter off Sesame's pack
  feeds the Pi Zero. 8 servos and a 2W board don't need the power engineering
  an 18-servo hexapod did.
- **IMU/gyro** — Sesame doesn't use one. Don't add complexity it doesn't need.
- **Coral/Hailo accelerator** — try the Pi alone first. ~€60–70 for a problem
  you may not have.
- **Local LLM** — you don't need conversation. The personality is the state
  machine, not a chatbot.

## Rough total

| | € |
|---|---|
| A. Sesame body | ~60–75 |
| B. Brain (Pi Zero 2 W + camera + cards + buck) | ~73 |
| B. Water rig + sensors | ~20 |
| **Total** | **~155–170** |

For what was actually bought, what was wrong with it and why, see
[`PURCHASE_LIST.md`](PURCHASE_LIST.md).

Against the original 12-servo, Pi-5-on-board design at **~€450**. Two
decisions did that: building Sesame instead of a body, and picking a brain
sized to the robot instead of one that needed a bigger robot to carry it.

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

### If you end up buying one

Prices checked **2026-08-18**, German retailers. What this project actually
needs is narrow, so most of a printer spec sheet is irrelevant:

| The robot needs | The robot does **not** need |
|---|---|
| Dimensional accuracy — servo splines, M2 screw bosses | A big bed. The largest Sesame part is small |
| Reliability — the printer is not the project | An enclosure. This is a **PLA** build throughout |
| Fast iteration — you'll reprint the shell several times in Week 4 | A hardened nozzle. No carbon fill, no abrasives |
| Auto bed levelling — the thing your Kobra just broke on | Multi-colour. Nice for a two-tone spider, not needed |
| Quiet — it runs in your room, next to you | 600 mm/s. Small parts are acceleration-bound, not speed-bound |

#### The candidates

| Printer | € | Build volume | Kinematics | Its actual weakness |
|---|---|---|---|---|
| **Bambu A1 mini** | 189 | 180³ | bed-slinger | Bed may be too small for Sesame's largest part — **verify in a slicer first** |
| **Bambu A1** | 259 | 256³ | bed-slinger | 2024 heatbed-cable recall (resolved on current units) |
| **Anycubic Kobra 3** | 199 | 250×250×250 | bed-slinger | QC lottery; ACE Pro multicolour unit jams constantly |
| **Anycubic Kobra S1 Combo** | 399 | ~220³ enclosed | CoreXY | Same ecosystem problems, 2× the price of a Kobra 3 |
| **Bambu A2L** | 379 | 330×320×325 | bed-slinger | **Wrong tool.** A 330mm bed for 60mm parts, louder, eats your desk |
| **Bambu P1S** | 389 | 256³ enclosed | CoreXY | The enclosure serves ABS/ASA, which this build never uses |
| Anycubic Kobra 3 Max | ~460 | 420×420×500 | bed-slinger | Same, more so |

#### Speed — mostly a marketing number

Every one of these advertises 300–600 mm/s. **None of them reach it on parts
this size.** Sesame's pieces are small and detailed, so print time is
dominated by *acceleration* and cooling, not top speed. Expect roughly
30–60 min per joint and 2–4 h for a cover on any machine here — the spread
between the cheapest and the dearest is maybe 20%.

What actually costs you days is **failed prints and downtime**, not mm/s.
Which is a reliability question, not a speed question.

#### Noise — trust nobody's dB figure

Manufacturer numbers (Bambu "<48 dB", Anycubic "55–60 dB") are quoted at
unstated distances in *silent mode*, which throttles speed. Useful ordering,
not useful absolutes:

- **A1 mini** is the quietest here — least mass to fling, active motor noise
  cancellation, small fans.
- **A1 / A2L** get louder as the bed gets bigger and heavier.
- **P1S / Kobra S1** are *enclosed*, which muffles motor whine but adds an
  aux part-cooling fan and an exhaust fan. Enclosed does **not** mean quiet.
- Bed-slingers make a low-frequency thump through the desk. Put any of them
  on a paving slab or a concrete tile, not on the desk you work at.

#### Long-term cost — smaller than either brand wants you to think

| | Bambu | Anycubic |
|---|---|---|
| Filament | any 1.75mm PLA; own-brand ~€20–25/kg | any 1.75mm PLA; own-brand ~€15–20/kg |
| Nozzle/hotend | whole assembly swap, ~€15–25 | ~€5–15 |
| Build plate | ~€20–30 | ~€20 |

Over this project you will use **~1 kg of filament and zero nozzles.** The
consumable difference across every machine in this table is **under €30 for
the whole build.** Anyone arguing brand on running costs is arguing about
noise-level money.

The real long-term cost is *failure rate × your time*, and there the gap is
large.

#### Brutal on Bambu

- **They lock the ecosystem down, and it is getting worse.** January 2025
  firmware added mandatory "Authorization Control"; September 2025 escalated
  it, gating third-party slicers and accessories. OrcaSlicer's developer
  publicly refused to adopt Bambu Connect. Third-party firmware (X1Plus) was
  blocked, then permitted only via a "one-way ticket" that **voids your
  warranty**.
- **Cloud-first.** LAN-only mode exists and costs you features.
- **Proprietary consumables** at a premium, and hotends swap as whole units.
- **AMS purge waste is real** — multi-colour can waste more filament than the
  part weighs.
- Buying one is buying a **product**, not a machine you own outright. For a
  14-week project that is a fine trade. As a matter of principle it is not.

#### Brutal on Anycubic

- **QC is a lottery.** One reviewer tested six Kobra 3 Max units and found
  wide unit-to-unit variance and firmware instability. A four-month Kobra 3 V2
  test concluded single-colour prints are genuinely good and the multicolour
  ACE Pro "is a mess" — it clogs, jams and tangles.
- **Support is inconsistent and spare parts are slow.** You are living this
  right now with a levelling module.
- **Security record is poor.** In 2024 an MQTT API flaw let attackers push
  commands to printers worldwide; researchers say three emails over two
  months went unanswered before it was exploited publicly.
- **In its favour:** genuinely cheapest, more open, and you already know the
  ecosystem. A Kobra 3 at €199 will print these parts fine *if you get a
  good unit*.

#### Verdict for this project

1. **Fix the Kobra 2 Pro first.** €0–30, and the diagnosis is above.
2. **If it's dead: Bambu A1, €259.** Not for speed and not for the brand —
   for the hours you don't spend calibrating. You have 14 weeks and the
   printer is not the project.
3. **A1 mini at €189** if €70 matters, *after* checking the biggest STL fits
   in 180mm.
4. **Not the A2L, not the P1S, not the Kobra 3 Max.** You would be paying
   €120–200 for build volume and an enclosure this robot has no use for.
5. **Kobra 3 at €199** only if you specifically want to stay off Bambu's
   ecosystem, and accept the QC lottery. That is a values choice, and a
   legitimate one — just make it knowingly.

#### If it's a long-term machine, not a project machine

Different question, different answer — and it **eliminates the A1 above.**

For one robot, the criterion is reliability. For a decade of engineering
projects, the criteria become **materials** and **repairability**, and those
two rule out every open-frame printer on this page.

**Why the enclosure stops being optional.** PLA is a prototyping plastic: it
creeps under load, softens around 60°C, and goes brittle in UV. Real
functional parts want ABS, ASA, PC or a glass/carbon-filled nylon — and all
of those warp or delaminate without a still, warm chamber. That is a whole
*class* of materials, not a refinement. It is the single biggest capability
step you can buy, and it is worth more than any brand argument here.

So: **A1, A1 mini, A2L and Kobra 3 are project printers, not career
printers.** Open frame, and no amount of money spent on build volume fixes
that. The A2L in particular is 330mm of bed and no enclosure — the wrong axis
to spend on.

| Long-term candidate | € | Volume | Chamber | Nozzle | The real trade |
|---|---|---|---|---|---|
| **Elegoo Centauri Carbon** | 299 | 256³ | passive | **320°C** hardened | Cheapest sensible enclosed CoreXY. Unproven parts supply in 5 years |
| **Elegoo Centauri Carbon 2** | 329 | 256³ | passive | **350°C** hardened | Quieter, hotter, better vented — and only €30 more. See below |
| **Bambu P1S** | 379 | 256³ | passive | hardened optional | Best-in-class reliability. You are renting the ecosystem |
| **Prusa MK4S** (kit) | 839 | 250×210×220 | none | 290°C | Open and repairable, but **open frame** — skip for this purpose |
| **Prusa CORE One** | 1099–1349 | 250×220×270 | **active, 55°C** | 300°C, 400°C HT option | Buy-once. Actively heated chamber unlocks PC/PPA. 3× the Elegoo |

#### The five-year questions nobody asks at purchase

1. **Can you still buy a hotend for it in 2031?** Prusa: yes, demonstrably —
   they still stock MK3 parts a decade on, from Prague, which is next-day to
   Berlin. Bambu: probably, on their terms. Elegoo/Anycubic: genuinely
   unknown; budget brands discontinue models and the spares evaporate.
2. **Do you control the firmware?** Prusa is open source. Elegoo's Carbon 2
   runs cloud-free. Bambu spent 2025 gating third-party slicers and
   accessories, and third-party firmware voids the warranty. Over 14 weeks
   that is irrelevant. Over ten years it is the whole question.
3. **Which slicer?** PrusaSlicer and OrcaSlicer are open and will outlive any
   of these vendors. Being locked to one company's slicer is a slow-acting
   risk.
4. **Resale.** Prusa holds value unusually well; Bambu holds reasonably;
   budget brands collapse. A CORE One sold in three years costs less to own
   than a €400 printer sold in three years.
5. **Can you fix it yourself?** A Prusa **kit** is not a worse product — for
   someone doing engineering long-term, building it teaches you the machine,
   and you can then repair anything on it. That is a real argument, not a
   consolation prize.

#### What to actually do

- **Value pick — Elegoo Centauri Carbon 2, €329.** Enclosed CoreXY, 256³, a
  350°C hardened nozzle *as standard*, cloud-free. It gets you the entire
  engineering-materials capability for less than the P1S, and less than a
  third of the CORE One. The honest risk is spares in five years.
- **Buy-once — Prusa CORE One, €1,099–1,349.** The only one here with an
  **actively heated chamber**, and the only one you can be confident of
  repairing in 2031. If you are genuinely going to be doing this for years,
  this is the machine that is still on your bench when the others are
  e-waste.
- **P1S, €379** is the pick only if you weight "works with zero effort" above
  everything, and are content that the machine is partly Bambu's. That is a
  defensible trade — just not the one someone asking about *long term* is
  usually making.

#### Centauri Carbon vs Carbon 2 — the gap is €30, not €150

Checked **2026-08-18**. If the two look far apart, you are probably reading
**US** pricing ($300 vs $450) or comparing against the **Combo**. In Germany:

| | 3DJake DE | Elegoo EU | Stock |
|---|---|---|---|
| Centauri Carbon | €299 | €309 | out of stock at 3DJake, in stock at Elegoo |
| Centauri Carbon 2 | €329 | — | **pre-order** |
| Centauri Carbon 2 **Combo** (multicolour) | €379 | — | in stock |

What the €30 buys:

| | Carbon | Carbon 2 |
|---|---|---|
| Build volume | 256³ | 256³ — **same** |
| Speed / acceleration | 500 mm/s · 20,000 mm/s² | **same** |
| Max nozzle temp | 320°C | **350°C** |
| Noise (vendor claim) | ~55 dB | **45 dB** |
| Chamber | enclosed | + auto-opening vents, better filtration |
| Screen | 4.3" | 5" |
| Auto-levelling | baseline | ~14% faster |
| Multicolour | CANVAS (now available for it too) | CANVAS |

**Take the Carbon 2.** Not for the temperature — 320°C already covers ABS,
ASA, PETG and PC, and 350°C only matters for PPS-CF and PPA, which you will
probably never buy. Take it for the **10 dB**. That is roughly *half the
perceived loudness*, on a machine that will run for hours in the room you
sleep in. €30 is nothing against that. (Vendor dB claims are still marketing
— treat it as an ordering, not an absolute.)

**Skip the Combo.** €50 more for multicolour sounds cheap, and budget
multicolour units are the least reliable part of every printer in this class
— Anycubic's equivalent was described in a four-month test as jamming,
clogging and tangling. It also purges a lot of filament. Add it later if you
ever actually want two-tone parts.

#### What owners and reviewers actually report (Carbon 2)

Gathered **2026-08-18** from written reviews, forum threads and owner reports.
The pattern is consistent enough to summarise in one line:

> **The hardware is genuinely good. The software is the weak part.**

**Holds up:**

- Print quality is repeatedly described as comparable to a P1S or X1C. One
  owner reports theirs prints "just as good as a friend's X1C with fewer
  fails"; another measured it printing *faster* than their P1S side by side.
- **The noise claim is honest** — independently measured at **44–47 dB**,
  peaking 54 dB, against a 45 dB vendor claim. Almost nobody in this market
  quotes a number that survives measurement. (It does emit a mild constant
  beep when idle.)
- PLA and PETG are clean and consistent out of the box. TPU works with minor
  profile tuning.

**Recurring complaints:**

| Problem | How much it matters here |
|---|---|
| **Elegoo Slicer connectivity** — refuses to connect on Windows, WiFi drops needing a router power-cycle, firmware updates breaking things | The most common complaint by far. **Mitigation: use OrcaSlicer**, which supports it. You do not have to run Elegoo's slicer |
| **Default Z-offset too low** → wavy first layers, needs ~+0.025mm | One-time fix, but you *will* hit it. Budget an evening |
| **ASA warps** even with the chamber hold | ⚠️ See below — this qualifies the "engineering materials" case |
| Inaccurate print-time estimates (~17% out on multicolour) | Cosmetic |
| False spaghetti/clog detection | Annoying, not fatal |
| Clogging — one owner took 3 months to resolve; another needs to clear clogs more often than on their P1S, saying the CC has "less room for error" | The real reliability gap vs Bambu |
| Shipping damage (broken glass doors) and slow RMA | Argues again for an **EU seller** |
| Finicky spool holders, cold plate wants more grip | Minor |

⚠️ **The ASA finding qualifies the case for buying it.** A *passive* enclosure
traps heat but does not control it, so it handles ABS reasonably and ASA
poorly. If ASA and PC are genuinely the goal, that is what an **actively
heated chamber** — the CORE One's 55°C — is actually for. The Centauri is
still a large step up from any open-frame printer; it is not equivalent to
active chamber control, and its own reviewers found the limit.

**Net:** at €329 this is a lot of printer, and the failure mode is *fiddling*,
not *bricking*. If you enjoy tuning a machine, it is excellent value. If you
want to never think about the printer, that is what the extra €50 for a P1S
buys — and the owner reports above say so in almost those words.

#### Final call: Carbon vs Carbon 2 vs P1S

Scored against one specific set of priorities — **(1) not having to worry
about it, (2) speed, (3) noise, (4) quality** — checked 2026-08-18.

| | Carbon €299 | Carbon 2 €329 | **P1S €379** |
|---|---|---|---|
| **1. Don't-worry factor** | fair | fair | **best, clearly** |
| **2. Speed** | 500mm/s · 20k accel | identical | identical |
| **3. Noise** | ~55 dB (vendor claim, unverified) | **44–47 dB measured**, 54 peak | ~45 dB typical, aux fan spikes it |
| **4. Quality** | tie | tie | tie |
| Stock at 3DJake | ❌ out of stock | ⏳ **pre-order** | ✅ in stock |

**Three of the four criteria do not separate these machines.**

- **Speed is a genuine tie.** All three run 500 mm/s and 20,000 mm/s², and
  parts this size are acceleration- and cooling-bound anyway. One owner
  measured their Centauri printing *faster* than their P1S. Call it even.
- **Quality is a tie.** Owners put the Centauri level with an X1C.
- **Noise is closer than it looks.** The Carbon 2's 44–47 dB is *measured*,
  which is worth something; the P1S sits around 45 dB typical but its aux and
  chamber fans push it up, and owners report turning the aux fan down because
  it is "way too loud". One reviewer's summary — *"fine in a workshop; in a
  home office or bedroom it is a real consideration"* — applies to both. The
  Carbon 2 also beeps continuously when idle. Effectively a wash.

**So criterion 1 decides it, and criterion 1 is the one with a real gap.**

The owner reports are unusually direct about this. Centauri owners comparing
the two say the machine has *"less room for error than the P1S"* and that
they *"adjust and fix clogs more often"*. One took three months to resolve a
clogging problem. Add the Elegoo Slicer connectivity failures, the low
default Z-offset, firmware updates breaking things, and reports of slow RMAs.

None of that is fatal — the failure mode is **fiddling, not bricking** — but
"fiddling" is exactly the thing being ranked first.

> **Buy the P1S, €379.** You are paying €50 over the Carbon 2 for the
> criterion you said matters most, and the other three are ties.

Two supporting reasons, both practical rather than technical:

- **It is the only one in stock.** The Carbon is out of stock and the Carbon 2
  is pre-order. You have a robot to build and a printer that is already
  broken.
- **You have already lost time to a printer this month.** That is the whole
  argument in one line.

⚠️ **The P1S costs you something real, and it is not money.** Everything in
"Brutal on Bambu" above still applies: the 2025 authorization firmware,
cloud-first defaults, third-party firmware voiding the warranty. You are
buying the least-hassle machine by accepting that you do not fully own it.
If that trade bothers you more than an evening of tuning does, buy the
**Carbon 2 at €329**, run **OrcaSlicer** from day one, and expect to fix the
Z-offset yourself. That is a legitimate choice — just not the one that
follows from ranking "don't want to worry" first.

#### Warranty — the manufacturer's terms are not the ones that protect you

**Elegoo EU: 24 months** on the printer itself, for the whole Centauri
series — so Carbon and Carbon 2 are the same here. Calculated from the date
you received the order.

⚠️ **But the wear parts have *no warranty at all.*** Elegoo lists these as
consumables and excludes them outright:

> PEI platform plate · build plate · nozzle (kit) · PTFE tube · heater ·
> thermistor · **hot end** · tools

The hotend is on that list, and the hotend is the part that actually fails.
Budget accordingly — a spare hotend is a consumable, not a warranty claim.

**The protection that matters is statutory, and it comes from the seller, not
Elegoo.** Under EU Directive 2019/771 — in Germany §438 BGB — anything bought
from an **EU seller** carries a **2-year legal conformity guarantee**, and for
the first 12 months the burden of proof sits with the *seller*: they must show
the fault was not there at delivery, not the other way round.

That gives one concrete rule:

> **Buy from an EU seller** — 3DJake, Elegoo's EU store, a German retailer.
> Not from AliExpress or a Chinese direct listing, however cheap.

Cross-border direct orders leave you relying on the manufacturer's goodwill,
international shipping for RMAs, and possibly customs charges on the
replacement. On a €300 machine that difference is worth far more than any
€20 price gap between shops. This is also the exact difference between your
Kobra situation being "annoying" and being "unrecoverable".

⚠️ **None of this should touch the 14-week schedule.** Fix the Kobra, build
the robot on it, and buy the long-term machine when you actually need ABS.
A €1,100 purchase in Week 0 delays the build and answers a question you do
not have yet. A fixed Kobra 2 Pro is a perfectly good PLA printer, and
keeping it as the PLA workhorse alongside an enclosed machine later is the
normal end state, not a compromise.

### Settings for Sesame's parts

Upstream specifies **PLA / PLA+, 8–10% infill, 2 wall loops, honeycomb**, and
only the top cover needs supports. Follow that for the 11 upstream parts.

⚠️ For **our** parts in `cad/stl/` — payload deck, nozzle mount, reservoir
cradle — go to **4 walls and 25% infill**. Those carry the pump, the water and
the aiming load; upstream's numbers are tuned for a shell that carries only
itself.
