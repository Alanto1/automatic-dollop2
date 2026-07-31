# Purchase list — Almaty, walk-in-first

Real physical stores you can walk into today, checked **2026-07-25**.
Prices in KZT (тг) are what each store's own website lists — **confirm in
person**, since a physical component shop's shelf stock and a website
catalog don't always agree, and small parts (resistors, diodes) often
aren't priced online at all. Two parts are also confirmed on **Kaspi.kz**
(checked **2026-07-27**) as a genuine online alternative, called out where
relevant below: the VL53L0X sensor and a flat 502030 LiPo battery. Kaspi
itself renders prices client-side, so its listings here don't carry a
pinned price - open the link to check current price/delivery time.

## Where to go

**Primary: Alash Electronics** — ул. Кыз Жибек 104/1, Кок-Тобе 2 м-н,
Медеуский район, Алматы 050020 · self-pickup Пн-Сб 12:00-20:00 · +7 700
900 17 90 · catalog: alash-electronics.kz (browse before going, don't
order online). Confirmed in stock: the VL53L0X sensor, a Type-C Nano
clone, TP4056, an 18650 battery, and the 2N2222 transistor - covers
almost the whole electronics list in one trip.

**Secondary: RadioBazar** — ТД Тастак (Tastak trade center), ул. Толе-би
266, бутик 37, этаж 2, павильон 3, Алматы · +7 (747) 721-21-68 · 4.6/5
from 47 reviews. Worth a stop specifically for its Nano clone (cheapest
found, see below) - checked directly and its own "Arduino modules and
sensors" category does **not** currently list a VL53L0X or similar
sensor, so don't count on it for that part specifically.

**Tertiary: Ba3ar.kz** — same building as RadioBazar: ТД Тастак, ул.
Толе-би 266, 2 этаж, **бутик 22** (RadioBazar is бутик 37, same floor -
worth visiting both on one trip) · +7 (701) 305-89-78 · catalog:
ba3ar.kz. Confirmed in stock: TP4056 with protection, Type-C (300 тг, 454
units - a backup if Alash is out). Its own VL53L0X listing (2,600 тг,
cheapest found) is currently **out of stock, pre-order only** - same gap
as everywhere else, see the sensor table below. Also carries a
GP2Y0A21YK0F infrared distance sensor (2,500 тг) as a different-technology
option - analog output, not I2C, so it's not a drop-in for the current
firmware without code changes.

**Also: Kaspi.kz** — no walk-in trip needed for two specific parts:
the VL53L0X sensor and a flat 502030 LiPo battery are both confirmed
listed (see the sensor table and battery note below for links). Useful if
you're doing a hybrid order - buy what's on Kaspi online, walk in for the
rest. Delivery takes days, not a same-day pickup, so plan around that if
you're on a deadline.

## The sensor situation (this changes the firmware, not just the list)

**No store checked stocks a VL53L1X (4m range)** — that part appears to be
online-order-only in Kazakhstan right now. What's actually on shelves in
Almaty is the VL53L0X (2m range) - and even that is currently harder to
find in-stock than expected: confirmed available at Alash Electronics,
but out of stock at Ba3ar.kz (pre-order), and not listed at all at
RadioBazar. `HapticMapper.h`'s far-zone threshold is set to **1800mm**
(not 2000mm) to keep real margin under the VL53L0X's 2m ceiling either
way - see the code comment there. Tests re-run and still pass (14/14);
the browser simulator matches. If a VL53L1X shows up locally later, that
threshold can move back up.

| Item | Qty | Store & link | Price | Confidence |
|---|---|---|---|---|
| VL53L0X laser distance sensor (GY-53) | 1 | [Alash Electronics](https://alash-electronics.kz/product/lazernyy-datchik-rasstoyaniya-gy-53-na-vl53l0x) | 2,750 тг | **Confirmed in stock** |
| — alternative to ask about | 1 | Alash Electronics (WCMCU-531) | 3,000 тг | Confirmed listed, a different breakout for the same/similar sensor - ask in store which is easier to wire |
| — online option, no walk-in needed | 1 | [Kaspi.kz](https://kaspi.kz/shop/p/datchik-rasstojanija-arduparts-kz-lazernyi-vl53l0x-gy-53-3024--130877379/) | renders client-side - check the page | Confirmed listed - same VL53L0X/GY-53 module (I2C, TTL and PWM output all confirmed on the listing). Worth bundling into the same order as the flat LiPo below if buying via Kaspi anyway |
| — same part, currently unavailable | 1 | [Ba3ar.kz](https://ba3ar.kz/product/vl53l0x-miniatyurnyj-modul-datchika-rasstoyaniya-i-raspoznavaniya-zhestov/) | 2,600 тг | Out of stock, pre-order only - cheapest price found if it comes back |
| — different tech, not a drop-in | 1 | Ba3ar.kz (GP2Y0A21YK0F, infrared) | 2,500 тг | Confirmed listed; analog output, would need `HapticMapper.h`/`obstacle_haptic.ino` changes to use |
| — fallback if nothing else is in stock: ultrasonic | 1 | check any of the three stores for HC-SR04 | ~750 тг range | Not confirmed at any store this pass, and **not a drop-in swap** either way - wider beam, would need its own look at `HapticMapper.h`'s thresholds |

## Electronics (BOM)

| Item | Qty | Store & link | Price | Confidence |
|---|---|---|---|---|
| Arduino Nano clone (CH340, **Type-C**) | 1 | [Alash Electronics](https://alash-electronics.satu.kz/p122739713-arduino-nano-v30.html) | 2,250 тг | **Confirmed in stock (23 units)** |
| — cheaper, but **Mini-USB not Type-C** | 1 | [RadioBazar](https://radiobazar.kz/g7735493-arduino-moduli-datchiki) | 2,000 тг | Confirmed in stock |
| VL53L0X sensor | — | see sensor table above | 2,750 тг | Confirmed (at Alash) |
| Vibration motor, "tablet" style, 3V, 10×3mm | 1 | [Alash Electronics](https://alash-electronics.kz/product/mikro-dc-vibratsionnyy-dvigatel-ploskiy) | 250 тг | **ACQUIRED 2026-07-30** - the builder has this part in hand and working. The listing showed out-of-stock/pre-order during earlier research; that gap is closed |
| 2N2222 NPN transistor | 3 (1 needed + spares) | [Alash Electronics](https://alash-electronics.kz/product/tranzistor-2n2222) | 50 тг each | Confirmed listed |
| 1N4148 flyback diode | 3 (1 needed + spares) | Alash Electronics (electronic components section) | not pinned down | Category confirmed, nearly free either way |
| Resistor, 220Ω-1k (either works) | 5 (1 needed + spares) | [Alash Electronics](https://alash-electronics.kz/collection/rezistory) | not pinned down | Category confirmed |
| Li-ion battery, 18650, 3400mAh (LiitoKala) | 1 | [Alash Electronics](https://alash-electronics.kz/product/originalnyy-akkumulyator-liitokala-18650-nadezhnyy-litiy-ionnyy-element-dlya-vysokoproizvoditelnyh-ustroystv) | 2,500 тг | **Confirmed in stock** - still an 18650 cylindrical cell, see the battery note below |
| TP4056 charge module, with protection, Type-C | 1 | [Alash Electronics](https://alash-electronics.kz/collection/zaryadnye-ustroystva/product/modul-zaryadki-li-ion-akkumulyatorov-na-tp4056-1-a-type-c) | 200 тг | **Confirmed in stock**. Backup: [Ba3ar.kz](https://ba3ar.kz/product/modul-zaryadki-liio-lipo-s-zashhitoj-tp4056-type-c/), 300 тг, confirmed in stock (454 units) |
| USB-C cable | 1 | Either store | not pinned down | Any electronics shop has these |
| **Power switch** (latching, any small SPST) | 1 | [Alash Electronics, KCD1 21×15mm, 2 contacts](https://alash-electronics.kz/product/kcd1-2115-krasnyy-2-kontakta) | 100 тг | **Confirmed in stock.** Simplest option electrically - 2 contacts is a plain on/off. But 21×15mm is chunky for a wristband; read the note below before buying |
| — smaller alternative | 1 | [Alash Electronics, KCD11 round rocker, 3 contacts](https://alash-electronics.kz/product/kcd11-3-kontakta-chernyy-o1) | 450 тг | Confirmed in stock. Round rocker, smaller footprint than the KCD1 |
| **★ ACQUIRED: slide switch, local counter** (SKU `BtnSS208`/`209`/`210`) | 6 bought (3 types × 2) | An Almaty component counter — **not catalogued online anywhere** | **50 тг each** | **Use the 4-pin type** — smallest body of the three, and only two contacts are needed. The 6-pin and 8-pin types are multi-pole: more switch than the job needs, in bigger packages. Which two pins make/break is found with the D2/D3 continuity sketch, which also confirms it latches rather than springing back |
| — ~~KLS L-KLS7-SS12F44-G5~~ | — | ChipDip.kz, *DIP-переключатели* | 103 тг, 10 days | Superseded. Was the best catalogue option before the counter purchase; keep as a reorder path if the local ones run out |
| — ~~MTS-101 A-2 toggle~~ | — | [ChipDip.kz](https://www.chipdip.kz/product/mts-101-a-2-mikrotumbler-on-off-spst-2p-jietong-switch-9000213601) | 362 тг | Superseded. In stock and 3A-rated, but the ~13mm lever protrudes off the pod. Only worth revisiting if the local slide switches turn out not to latch |

### Power switch — needed once the battery is soldered in

Earlier revisions of this list called a switch optional, on the reasoning
that you can just unplug the battery to turn the device off. That holds
for a breadboard prototype and stops holding the moment the battery is
soldered to the TP4056 for a permanent build - at that point "off" would
mean desoldering, which is not an off button.

- **What to get:** any small **latching** switch (slide, rocker, or
  toggle - anything that stays where you put it; a tactile pushbutton is
  momentary and will not work as a power switch). Electrically this is
  undemanding - the whole device draws well under 200mA, far below what
  even the smallest switch handles - so **choose on physical size**, not
  on ratings.
**Resolved by walking into a shop.** Six slide switches, three types, **50
тг each** — cheaper and faster than every catalogue option, and available
the same day.

**This is the second time in this project that a part concluded
"unavailable" from online research turned out to be sitting in a drawer
at a counter.** Two full search passes said no slide switch was
obtainable in Almaty; the answer was to ask. For generic parts —
switches, small passives, connectors — ask in person *before* trusting a
catalogue search. Shops routinely don't list them.

**Use the 4-pin type.** Of the three bought (4, 6 and 8 pins), the 4-pin
has the smallest body, and the job needs only two contacts. The 6- and
8-pin types are multi-pole: more switch than required, in larger
packages, with more pins to bridge accidentally.

**Finding the right two pins** — works whatever the internal
configuration, which is worth doing empirically rather than assuming:

1. Number the pins and mark one end so the orientation doesn't get lost.
2. Run the D2→D3 continuity sketch (`pinMode(3, INPUT_PULLUP)`, D2 LOW,
   read D3 — "closed" means current flows).
3. Work through all six pairs: 1-2, 1-3, 1-4, 2-3, 2-4, 3-4.
4. **You want a pair that reads closed in one slider position and open in
   the other.** That's the switch. A pair closed in both is a mounting
   lug or internal link; open in both isn't connected.
5. **Then let go of the slider and check it stays put.** If it springs
   back it's momentary and unusable as a power switch — go back for the
   MTS-101 toggle instead.

A DPST will give two working pairs doing the same thing; either is fine,
pick whichever pins are easier to reach with an iron.

**Soldering to pins this small:** snip the unused pins flush first — that
removes the bridging risk and doubles the working room. Use only a few
strands of wire rather than a whole jumper, tin both sides separately,
and join with a brief touch rather than feeding fresh solder in. Watch
the heat: these bodies are plastic, and softening one shifts the internal
contacts and kills the switch with no visible damage.

**Check the pin pitch before soldering at all.** If it's 2.54mm the
switch pushes straight into a breadboard, and the whole continuity test
and Phase 5 wiring can be done with no soldering.

Superseded catalogue options, kept as reorder paths: the KLS
`L-KLS7-SS12F44-G5` (ChipDip, 103 тг, 10 days) and the
[MTS-101 A-2 toggle](https://www.chipdip.kz/product/mts-101-a-2-mikrotumbler-on-off-spst-2p-jietong-switch-9000213601)
(362 тг, in stock, 3A — bulkier but the fallback if the local switches
turn out not to latch).
- **Decide the switch before finalising the enclosure.** Its footprint
  drives the cutout in `enclosure.scad`, and swapping a 21×15mm rocker for
  a 13mm toggle after printing means reprinting.

### Where to get `R3` changed — the shop said no

Alash has no SMD components and doesn't do surface-mount rework. That
rules out the obvious route, but **any phone/laptop repair counter does
micro-soldering every day** and this is a five-minute job for them.
Options found in Almaty (2026-07-30):

- **A phone-repair stall at ТД Тастак** - the same building as RadioBazar
  (бутик 37) and Ba3ar.kz (бутик 22), so it costs no extra trip. Best
  first try: informal, cheap, and they have hot-air stations.
- **[FixPC.KZ](https://fixpc.kz/remont-i-pajka-plat-almaty.html)** -
  advertises board- and chip-level soldering in Almaty.
- **Electron Service** - ул. Грибоедова 80, офис 316/329. Industrial
  electronics repair, 20+ years.
- **[OLX.kz «пайка» listings](https://www.olx.kz/uslugi/remont-i-obsluzhivanie-tehniki/alma-ata/q-%D0%BF%D0%B0%D0%B9%D0%BA%D0%B0/)**
  - independent repair people, usually the cheapest for a job this small.

Bring the module, the battery, and a 10kΩ resistor with you. **ChipDip
also stocks resistors**, so one trip there can cover the switch and the
10kΩ together - ask for both an SMD 0805 10kΩ (if you want it done
properly by a repair shop) and a through-hole one (if you'd rather do the
bridge yourself).
- **Where it goes:** in series on the **OUT+** line, between the TP4056's
  `OUT+` pad and the Nano's `5V` pin. Switching off then disconnects the
  load while leaving the charging path intact, so the battery still
  charges over USB with the device switched off.
- **Enclosure consequence, not yet done:** `enclosure/enclosure.scad` has
  no switch cutout, and no dimensions for one. Add that before printing a
  final shell, or the switch ends up unreachable inside a sealed pod.

### Vibration motor — RESOLVED, gap closed

**The builder acquired the 10×3mm motor and it is confirmed working on the
breadboard as of 2026-07-30.** This section is kept as history of what the
sourcing looked like when the part was hard to find; it is no longer an
open problem.

One practical thing learned from actually using it, worth knowing before
you wire one up: **the motor's leads are far too thin for a breadboard to
grip.** See `tutorial.md`'s Phase 3 callout - solder each lead to a
cut-in-half jumper wire first, or you get an intermittent connection that
convincingly imitates a broken transistor circuit.

The original sourcing notes follow. The exact part showed **out of stock**
at Alash Electronics during earlier research (pre-order, no ETA), and
wasn't found listed at RadioBazar or Ba3ar.kz either. If you ever need a
replacement:

- **Call Alash Electronics first** (+7 700 900 17 90) - online "out of
  stock" at small component shops doesn't always match what's actually on
  a shelf, and it's worth asking whether a pre-order has a real timeline.
- **A phone-repair stall is a legitimate alternative source.** This exact
  type of motor (a tiny coin/tablet vibration motor) is the same part used
  in almost every phone - any phone-repair counter (Tastak market has
  several, and both RadioBazar and Ba3ar.kz are already in that same
  building) likely has one pulled from repair stock or sold as a spare
  part, often cheaper than an electronics-hobby store. Bring the
  dimensions (10×3mm) or a reference photo.
- Failing both, RadioBazar's "моторы и приводы" (motors and drivers)
  category is confirmed to exist even though a specific vibration motor
  wasn't confirmed in it - worth a look in person while you're at Tastak
  for Ba3ar.kz anyway.

### Battery note — read before buying

Two real options now - pick based on what you're building:

| Item | Qty | Store & link | Price | Confidence |
|---|---|---|---|---|
| Flat LiPo pouch, 502030 (3.7V, 250mAh, 5×20×30mm) | 1 | [Kaspi.kz](https://kaspi.kz/shop/p/akkumuljator-502030-1-sht-117959645/) | renders client-side - check the page | **ACQUIRED 2026-07-30.** Actual cell markings: `YS 502030 3.7V 250mAh 0.925Wh`. Soldered to a TP4056 and charging confirmed. **Read the charge-current warning below before charging it again** |
| Li-ion 18650, 3400mAh (LiitoKala) | 1 | [Alash Electronics](https://alash-electronics.kz/product/originalnyy-akkumulyator-liitokala-18650-nadezhnyy-litiy-ionnyy-element-dlya-vysokoproizvoditelnyh-ustroystv) | 2,500 тг | **Confirmed in stock**, walk-in |

- **Flat 502030 pouch** - fits `enclosure/enclosure.scad`'s battery cavity
  as-is (the cavity is now sized for this exact part - see the file's
  comment). 250mAh is modest capacity; expect shorter runtime and more
  frequent charging than the 18650 below. Only available via Kaspi in
  this research pass, not confirmed at any walk-in store.
- **18650 cylindrical, 3400mAh** - confirmed in stock at Alash
  Electronics, no waiting on delivery. About 13x the 502030's capacity,
  but it's a tube (18mm diameter × 65mm long) - `enclosure/enclosure.scad`
  would need a real redesign (a cylindrical battery bay) to fit this one
  instead of the pouch cavity.
- **Either way**, the bare cell's own protection (the 502030 lists its
  own overcharge/overcurrent protection; double-check the 18650 listing
  for the same) is separate from charging safety - route charging through
  a TP4056-with-protection module (Alash or Ba3ar.kz, both confirmed
  above) regardless of which cell you pick.

#### Charge current — a stock TP4056 is set far too high for the 502030

**This is the one open safety item in the project.** A stock TP4056
module is configured for **1000mA** charge current, set by the small
surface-mount resistor marked `R3` (usually printed `122`, meaning
1.2kΩ). The chip's relationship is:

> charge current (A) = 1200 ÷ R3 (Ω)

For a **250mAh** cell that stock 1A works out to roughly **4C**. Typical
manufacturer guidance for pouch cells like this is 0.5C for normal
charging and 1C as the absolute ceiling - so 125mA normal, 250mA maximum.
The stock setting is about four times past the ceiling. It will charge
without complaining, which is exactly what makes it easy to leave alone.

Target roughly **10kΩ** (marked `103`) for ~120mA, or 5kΩ for ~240mA if
you want 1C.

**Asking a shop to do it was tried and did not work** - the store had no
SMD components and doesn't do surface-mount rework (checked 2026-07-30).
So this is a DIY job, and the key realisation is that **you do not need an
SMD resistor at all**: remove the existing R3 and bridge an ordinary
through-hole 10kΩ across its two pads. Through-hole resistors are a
standard stocked part everywhere (Alash has a Резисторы subcategory).

Procedure:

1. **Buy a spare TP4056 first** (~200-300 тг). Cheap insurance - if a pad
   lifts, you have not lost the project.
2. **Remove R3.** Without hot air: flow a generous blob of solder so it
   bridges *both* ends of the tiny resistor at once. That blob carries
   heat to both terminals simultaneously, so with the iron keeping it
   molten you can nudge the part off sideways with tweezers. Don't pull -
   ripping a cold part off takes the pad with it.
3. **Clean the pads** with desoldering braid, or by wiping the hot iron
   across them.
4. **Fit the 10kΩ.** Trim its legs to ~3-4mm, tin both pads, then tack one
   leg down and the other. The body will stand above the board; secure it
   with a dab of hot glue so it can't flex and tear a pad later.

Until it's changed: charge supervised, on a non-flammable surface, and
stop immediately if the pouch warms up or stops being perfectly flat.
Swelling means stop permanently. At 1A a 250mAh cell fills in roughly
15-20 minutes, so supervising it is not a big ask.

## Prototyping, soldering & wiring, tools

Not re-checked store-by-store this pass - Alash Electronics' broader
catalog (microcontrollers, resistors, cables/adapters, BMS/charging
boards) and Ba3ar.kz's ("Прототипирование" / prototyping category
confirmed to exist) both strongly suggest they carry general prototyping
and soldering supplies too, consistent with what RadioBazar was already
confirmed to carry:

| Item | Qty | Where | Confidence |
|---|---|---|---|
| Breadboard | 1 | Alash Electronics, RadioBazar, or Ba3ar.kz (has a "Прототипирование" category) | Not itemized this pass - all three are full-catalog component shops, likely to carry it |
| Jumper wires (M-M and M-F) | a few packs | Any of the three | Universally stocked |
| Soldering iron (+ multimeter if bundled) | 1 | RadioBazar ("паяльное оборудование" category, confirmed) | Category confirmed at RadioBazar; check the other two too |
| Solder wire, wire stripper, screwdriver set, hookup wire, heat-shrink, "third hand" stand, crocodile clips | 1 each | RadioBazar | Category confirmed ("паяльное оборудование"), individual items not itemized |

## Enclosure assembly

Unchanged from before - general hardware/craft items, not specialty
electronics:

| Item | Qty | Where |
|---|---|---|
| Hot glue gun | 1 | Any hardware/craft store |
| Calipers | 1 | Any hardware store, or ask at Alash Electronics/RadioBazar/Ba3ar.kz |
| 20mm wristband/watch strap | 1 | A watch/accessories stall - Tastak market has these too |
| 3D printing (base + lid + clip) | 1 job | Check a school makerspace first, or ask at any of the three stores |

## Safety

Same open gap as before: no fireproof LiPo charging pouch confirmed
available anywhere in this pass. Until sourced, charge on a non-flammable
surface, supervised, never unattended.

## Totals

**Confirmed core total** (Nano + VL53L0X + transistor - the motor is
excluded since it's currently out of stock, not a real price to plan
around): 2,250 + 2,750 + 50 = **5,050 тг**. Add TP4056 (200 тг) and the
18650 battery (2,500 тг), both confirmed: **7,750 тг** for those five
items. Everything else - diode, resistors, cable, prototyping and
soldering supplies - is real and available based on confirmed store
categories, but budget loosely; this list leans on fewer pinned-down
prices than usual, precisely because two of its three stores' most
important items (the sensor at Ba3ar.kz, the motor at Alash) turned out
to be out of stock mid-research rather than simply unconfirmed.
