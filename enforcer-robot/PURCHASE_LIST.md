# Purchase list — Berlin / Germany, quadruped build

> **If you are buying from Kazakhstan, read
> [`START_HERE_KAZAKHSTAN.md`](START_HERE_KAZAKHSTAN.md) instead.** This file
> prices the build against German retailers and is only the right list if you
> are competing in Germany. Two findings here still transfer: the Raspberry Pi
> RAM price surge, and the fact that no rectangular face display was in stock
> anywhere — which is an argument for the AliExpress route either way.

Sourcing pass against `PARTS.md`, checked **2026-08-01**. Decision taken:
**quadruped (12 servos)**, so everything below is costed for 12 legs + 2 head
servos, not 18.

Prices are what each retailer's own site listed on that date, VAT included.
Stock counts are what the shop showed — several are in single digits, and
that's called out where it matters. Unlike the Almaty `PURCHASE_LIST.md` for
the wristband, this is **mail-order-first**: Germany's maker retailers ship
in 1–3 days, and only the passives are worth a walk-in trip (see
[Walk-in](#walk-in-segor-berlin-charlottenburg)).

---

## Headline: the budget in PARTS.md is about half of the real cost

`PARTS.md` estimates **~€230** for the quadruped. The verified cart comes to
**~€300 for the parts that could be priced**, and a realistic all-in total is
**~€445**. One line item causes most of the gap.

| | PARTS.md | Actual (2026-08-01) | Δ |
|---|---|---|---|
| Raspberry Pi 5, 4GB | €65 | **€118.50** | **+€53.50** |
| 12× MG90S + 3 spare | €38 | €62.40 | +€24.40 |
| microSD 32GB ×2 | €14 | €31.20 | +€17.20 |
| Camera | €15–25 | €28.90 | +€4 |
| Face display | €8 | €12.80 | +€4.80 |
| VL53L0X | €8 | €8.50–19.95 | +€0.50–12 |
| TCRT5000 ×4 | €4 | €1.20 | **−€2.80** |
| MOSFET + diode | €3 | €2.35 | −€0.65 |
| MAX98357A | €8 | €7.60 | −€0.40 |
| Water pump | €8 | €3.30 | **−€4.70** |

**Why the Pi tripled the damage:** memory prices. Reichelt's own Pi 5 ladder
on the same day reads €49.20 (1GB) → €69.50 (2GB) → **€118.50 (4GB)** →
€187.50 (8GB) → €309.50 (16GB). That is not a normal Pi price curve — it's
RAM cost passed straight through. Verified independently at **two**
retailers (BerryBase €118.50, Reichelt €118.50), so it is not a scraping
error or one shop's markup.

**The Pi 4 fallback in PARTS.md no longer works.** It claims a Pi 4 "saves
~€20." Reichelt: Pi 4 4GB = **€108.40** vs Pi 5 4GB = €118.50. You'd save
€10 and give up most of your detection headroom. Buy the Pi 5.

**The real lever is RAM, not generation.** Pi 5 **2GB at €69.50** saves
**€49** — and 2GB genuinely runs YOLOv8n + MediaPipe at the frame rates this
project needs, because the model is small and there's no desktop. See
[Decisions this forces](#decisions-this-forces).

---

## Order 1 — BerryBase (berrybase.de) · €218.60

The backbone order. Every line except the face display was showing **"Sofort
verfügbar · 1-3 Tage"** on 2026-08-01; the display is the one item with no
stocked option, and is excluded from the total — budget ~€8 for it elsewhere.

| Item | Qty | Unit | Sum | Stock shown | Link |
|---|---|---|---|---|---|
| Raspberry Pi 5, 4GB RAM | 1 | 118,50 | 118,50 | 100+ | [link](https://www.berrybase.de/raspberry-pi-5-4gb-ram) |
| Raspberry Pi Camera Module 3, 12MP | 1 | 28,90 | 28,90 | 100+ | [link](https://www.berrybase.de/raspberry-pi-camera-module-3-12mp) |
| BerryBase 16-Kanal PWM Servo Treiber (PCA9685) | 2 | 6,50 | 13,00 | **only 4** | [link](https://www.berrybase.de/berrybase-16-kanal-pwm-servo-treiber-board-pca9685-i2c-12bit-1-6khz-3-3-5v) |
| Face display — **rectangular wanted, none in stock**, see note | 1 | 7,90–17,20 | — | **0** | see note below |
| SparkFun I2S Audio Breakout, MAX98357A | 1 | 7,60 | 7,60 | 9 | [link](https://www.berrybase.de/sparkfun-i2s-audio-breakout-max98357a) |
| TCRT5000 IR Sensor — cliff sensors | 4 | 0,30 | 1,20 | 90 | [link](https://www.berrybase.de/tcrt5000-infrarot-sensor-lichtschranke) |
| Adafruit tauchbare 3V DC-Wasserpumpe, 1m Kabel | 1 | 3,30 | 3,30 | 16 | [link](https://www.berrybase.de/adafruit-tauchbare-3v-dc-wasserpumpe-mit-1-meter-kabel-horizontal) |
| SanDisk Ultra microSDHC A1 32GB + Adapter | 2 | 15,60 | 31,20 | 100+ | [link](https://www.berrybase.de/sandisk-ultra-microsdhc-a1-120mb-s-class-10-speicherkarte-adapter-32gb) |
| Anycubic PLA Filament 1,75mm 1kg (schwarz) | 1 | 14,90 | 14,90 | 5 | [link](https://www.berrybase.de/anycubic-pla-filament-1-75mm-1kg/farbe-schwarz) |
| | | | **218,60** | | |

**Two stock warnings, both real:**

- **PCA9685 — only 4 in stock.** This is the one part with no substitute in
  the design and a thin shelf. A quadruped needs 12 leg + 2 head = 14
  channels, so **one board is electrically enough** — the second is a spare,
  and at €6.50 it's the cheapest insurance in this whole build. Order both,
  now, before someone else clears the shelf.
- **Face display — every rectangular option is out of stock.** The design
  calls for a rectangle (two eyes side by side = a face). At BerryBase on
  2026-08-01, *all* of them were `Artikel aktuell nicht lieferbar`: the 1.3"
  240×240 (€7,90), the 1,83" 240×280 (€10,90), the Adafruit 1,69" 280×240
  (€17,20), the 1,14" 240×135 (€5,90). The only stocked SPI display is the
  **round** 1.28" at €12,80 — and it dropped from 5 units to **3** between two
  checks the same day, so it is moving.
  **Three ways out**, in order of preference: (1) buy it on AliExpress, where
  a 1.3" ST7789 is ~$4 and always in stock — you're ordering there anyway for
  the buck converter and pan/tilt; (2) wait for BerryBase restock, which risks
  your schedule for a €8 part; (3) take the round one as a fallback and run a
  one-eye face. Option 3 works, it just gives up the two-eye read that makes
  the reference build's face land.

**Two deliberate substitutions:**

- **Pump: Adafruit submersible 3V, €3.30** instead of the specified mini
  diaphragm pump. Cheaper and in stock, but it is **submersible, not
  self-priming** — it must sit *inside* the reservoir, not beside it. That
  actually simplifies the plumbing (pump in the bottle, one tube out to the
  nozzle) but it does constrain where the reservoir mounts: bottle upright at
  the front, pump at its bottom. Still a MOSFET load, still needs the flyback
  diode.
- **microSD: SanDisk Ultra A1, not A2.** No A2 32GB was in stock at a sane
  price; NAND is caught in the same price surge as the DRAM. A1 is fine for
  this workload — the detector loads once at boot and then runs from RAM.

## Order 2 — roboter-bausatz.de · €62.40

The servos. Nobody in the German maker-shop tier stocks MG90S — searched
BerryBase (0 hits) and Reichelt (0 hits for the part number). Anzado
GmbH / roboter-bausatz.de is the cheapest confirmed German source with
quantity tiers.

| Item | Qty | Unit | Sum | Link |
|---|---|---|---|---|
| MG90S Micro Servo Motor (metal gear) | 15 | 4,16 | 62,40 | [link](https://www.roboter-bausatz.de/p/mg90s-micro-servo-motor) |

Quantity tiers as listed: 1–4 €4.38 · **5–19 €4.16** · 20+ €4.05. Stock:
"Sofort verfügbar, Lieferzeit 1-3 Tage."

**15 = 12 legs + 3 spares.** `PARTS.md` is right that spares are not
optional — you will strip or burn at least one during gait tuning, and a
dead servo mid-week-3 costs you a week of shipping. Note that 12 legs + 2
head = 14, so the head servos usually come with the pan/tilt bracket; if
yours doesn't, bump this to 17 and you cross into no useful tier change
(still €4.16).

## Order 3 — Reichelt (reichelt.de) · €2.35

The two semiconductors, at prices no maker shop can touch.

| Item | Order no. | Qty | Unit | Sum |
|---|---|---|---|---|
| IRLZ 44N — MOSFET, N-Ch 55V 47A, TO-220AB | `IRLZ 44N` | 3 | 0,70 | 2,10 |
| 1N 4007 — Gleichrichterdiode 1000V 1A, DO-41 | `1N 4007` | 5 | 0,05 | 0,25 |
| | | | | **2,35** |

This is a €2.35 order and Reichelt's shipping will exceed it. **Don't place
it** — buy both parts over the counter at Segor instead, or fold them into
whichever order you're already paying shipping on. They're listed separately
only to pin the reference prices.

---

## Walk-in: Segor, Berlin-Charlottenburg

The one shop worth a trip rather than a parcel. Same role Alash Electronics
played in Almaty.

**SEGOR-electronics GmbH** — Kaiserin-Augusta-Allee 94, 10589 Berlin-Charlottenburg
· Mo–Fr **10:00–13:30** and **14:30–18:00** (closed for lunch 13:30–14:30),
Sa **10:00–13:00** · U7 Mierendorffplatz, bus M27 · segor.de · trading since 1978.

Go here for the things that are absurd to mail-order and that you will
otherwise wait a week for:

- IRLZ44N + 1N4007 (see Order 3 — buy them here instead)
- Inline fuse holder + 10A fuses, and the main power switch
- Silicone wire (18AWG servo rail, 22AWG logic), JST connectors, heatshrink
- M2/M3 screws and standoffs
- Perfboard, headers, and the odd resistor you didn't know you needed

Budget **~€25–35** for that whole bag. Check the lunch closure before you
travel — 13:30–14:30 catches people out.

---

## Still unpriced: the power block, chassis, and plumbing

Everything above is verified. This block is **not** — it's the part of
`PARTS.md` that German maker retailers simply don't serve, and it needs its
own decision before you can order.

| Item | Est. | Where | Note |
|---|---|---|---|
| 2S LiPo 7,4V 2200mAh+ XT60 | ~25 | RC retailer | Not stocked by BerryBase/Reichelt |
| UBEC 5–6V, 5–6A | ~16 | Lindinger.at | Hobbywing BEC 5A V2-Air, €16,30 — see below |
| Buck converter 5V/5A (Pi rail) | ~8 | AliExpress | Reichelt's are ≤1.25A, far too small |
| LiPo balance charger + LiPo-safe bag | ~25 | RC retailer | Non-negotiable, per PARTS.md |
| Pan/tilt bracket + 2 servos | ~10–20 | AliExpress | Reichelt `RPI SHD PAN-TILT` = €19,50 |
| Quadruped chassis kit (12-DOF frame) | ~40 | AliExpress | Only if the printer gate fails |
| Silicone tubing + nozzle + reservoir | ~10 | Hardware/aquarium shop | Aquarium airline tubing is ideal |
| | **~124–134** | | |

**Why this block resisted pricing.** Conrad, Amazon.de, eBay.de and
Eckstein all refused automated access (403/503), so nothing from them is
quoted here. Lindinger.at was readable, and what it showed is instructive:
German/Austrian RC shops sell **ESCs with a BEC built in** (€16–75), not
standalone UBECs. The closest clean match found was **Hobbywing BEC 5A
V2-Air, 6V, €16,30**.

**5A vs the 6A in PARTS.md — fine, and here's why.** The 6A figure was sized
for a *hexapod's* 18 servos. You chose the quadruped: 12 servos. MG90S stall
current is ~700mA, but statically-stable walking never stalls all twelve at
once — typical draw is ~150–250mA each, so ~2–3A continuous with headroom for
transients. **5A is adequate for 12 servos.** Do not read this as permission
to skip the week-4 brownout test; it makes that test more important, not
less.

**Do the AliExpress items in one order, and do it first.** Buck converter,
pan/tilt, and (if needed) chassis all ship from the same place with the same
2–4 week lead time. That is now the long pole in your Week 0, longer than
anything German. Order it the same day you decide the chassis question.

---

## Realistic total

| Block | € |
|---|---|
| Order 1 — BerryBase | 218,60 |
| Order 2 — roboter-bausatz (servos) | 62,40 |
| Order 3 — semiconductors (buy at Segor) | 2,35 |
| Segor walk-in bag (wire, fuse, switch, screws) | ~30 |
| Power / chassis / plumbing (unpriced) | ~124–134 |
| **Total** | **~450** |

Against `PARTS.md`'s €230 quadruped estimate. Shipping is on top: figure
~€5–7 each for BerryBase and roboter-bausatz.

---

## Decisions this forces

The sourcing pass turned one of `PARTS.md`'s "open decisions" into a live
budget question. Take these before placing Order 1.

1. **Pi 5 4GB (€118,50) or 2GB (€69,50)?** This is now the single biggest
   line in the build. 2GB saves **€49** — more than a fifth of the original
   whole-project budget. YOLOv8n plus MediaPipe Pose on a headless Pi OS Lite
   fits in 2GB with room to spare; the models are tens of MB, and there is no
   desktop competing for RAM. The 4GB is insurance against a future where you
   want a bigger model or a desktop for debugging. **Recommendation: 2GB**,
   and put the €49 toward the power block, which is the part that can
   actually sink the project.
2. **Camera Module 3 (€28,90) or a USB webcam (~€10)?** `PARTS.md` already
   flags that "USB is simpler on a moving robot" — no ribbon cable to fatigue
   where the head pans. Module 3's autofocus is genuinely nice for a desk
   robot at 40–80cm. **Recommendation: Module 3**, but this is the easiest
   €19 to give back if you take the 4GB Pi.
3. **Print the chassis or buy the kit?** Unchanged from `PARTS.md` — but note
   the chassis kit is an AliExpress item on a 2–4 week lead time, so the
   week-2 printer gate is effectively a **week-0** decision if you want the
   kit to arrive in time. If the printer diagnosis in the next 48h looks at
   all bad, order the kit as insurance; €40 is cheap against losing three
   weeks.

Both cost-reduction options together (2GB Pi + USB webcam) bring the total to
**~€380**.

## Confidence

- **High** — every price in Orders 1–3 was read from the retailer's own
  product listing on 2026-08-01, with stock counts. The Pi 5 4GB price was
  cross-checked at two independent retailers and matched exactly.
- **Medium** — the Segor address and hours (from the shop's own site and two
  directories, consistent). Its *stock* is not verified per-item; a walk-in
  shop's shelf and its catalog never quite agree. Call before travelling if a
  specific part is critical.
- **Low / unverified** — the entire power-and-chassis block. Those are
  estimates, not quotes. Nothing there is confirmed on a shelf.
