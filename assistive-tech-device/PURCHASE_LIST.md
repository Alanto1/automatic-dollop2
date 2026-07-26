# Purchase list — Almaty, walk-in only

No shipping, no delivery. Real physical stores you can walk into today,
checked **2026-07-25** (re-checked same day after Arduino Parts, the
original primary recommendation, turned out to be temporarily closed —
see "Arduino Parts" below). Prices in KZT (тг) are what each store's own
website lists — **confirm in person**, since a physical component shop's
shelf stock and a website catalog don't always agree, and small parts
(resistors, diodes) often aren't priced online at all.

## Where to go

**Primary: Alash Electronics** — ул. Кыз Жибек 104/1, Кок-Тобе 2 м-н,
Медеуский район, Алматы 050020 · self-pickup Пн-Сб 12:00-20:00 · +7 700
900 17 90 · catalog: alash-electronics.kz (browse before going, don't
order online). Confirmed in stock: the VL53L0X sensor, a Type-C Nano
clone, TP4056, an 18650 battery, and the 2N2222 transistor - covers
almost the whole electronics list in one trip, and on several items
(TP4056, battery, sensor) is actually cheaper than the original
Arduino Parts list was.

**Secondary: RadioBazar** — ТД Тастак (Tastak trade center), ул. Толе-би
266, бутик 37, этаж 2, павильон 3, Алматы · +7 (747) 721-21-68 · 4.6/5
from 47 reviews. Worth a stop specifically for its Nano clone (cheapest
found, see below) - checked directly and its own "Arduino modules and
sensors" category does **not** currently list a VL53L0X or similar
sensor, so don't count on it for that part specifically.

**Arduino Parts** — ул. Толе би 189д, офис 310, Алматы — **temporarily
closed** as of this check. Its earlier confirmed pricing (VL53L0X 2,800
тг, Nano USB-C 2,300 тг, motor 250 тг, TP4056, an 18650 cell) is kept
below for reference/comparison and in case it reopens - don't plan a trip
there until you've confirmed it's open again.

**Tertiary: Alash Electronics doubles as this too** - the separate "Alash
Electronics" tertiary-for-one-item entry from the previous version of this
list is gone since it's now the primary.

## The sensor situation (this changes the firmware, not just the list)

**No store checked stocks a VL53L1X (4m range)** — that part appears to be
online-order-only in Kazakhstan right now. What's actually on shelves in
Almaty is the VL53L0X (2m range). `HapticMapper.h`'s far-zone threshold is
set to **1800mm** (not 2000mm) to keep real margin under that 2m ceiling -
see the code comment there. Tests re-run and still pass (14/14); the
browser simulator matches. If a VL53L1X shows up locally later, that
threshold can move back up.

| Item | Qty | Store & link | Price | Confidence |
|---|---|---|---|---|
| VL53L0X laser distance sensor (GY-53) | 1 | [Alash Electronics](https://alash-electronics.kz/product/lazernyy-datchik-rasstoyaniya-gy-53-na-vl53l0x) | 2,750 тг | **Confirmed in stock** |
| — alternative to ask about | 1 | Alash Electronics (WCMCU-531) | 3,000 тг | Confirmed listed, a different breakout for the same/similar sensor - ask in store which is easier to wire |
| — fallback if neither is in stock: ultrasonic | 1 | check Alash Electronics or RadioBazar for HC-SR04 | ~750 тг range | Not confirmed at either store this pass, and **not a drop-in swap** either way - wider beam, would need its own look at `HapticMapper.h`'s thresholds |

## Electronics (BOM)

| Item | Qty | Store & link | Price | Confidence |
|---|---|---|---|---|
| Arduino Nano clone (CH340, **Type-C**) | 1 | [Alash Electronics](https://alash-electronics.satu.kz/p122739713-arduino-nano-v30.html) | 2,250 тг | **Confirmed in stock (23 units)** |
| — cheaper, but **Mini-USB not Type-C** | 1 | [RadioBazar](https://radiobazar.kz/g7735493-arduino-moduli-datchiki) | 2,000 тг | Confirmed in stock |
| VL53L0X sensor | — | see sensor table above | 2,750 тг | Confirmed |
| Vibration motor, "tablet" style, 3V, 10×3mm | 1 | [Alash Electronics](https://alash-electronics.kz/product/mikro-dc-vibratsionnyy-dvigatel-ploskiy) | 250 тг | **Currently OUT OF STOCK (pre-order only)** - see note below |
| 2N2222 NPN transistor | 3 (1 needed + spares) | [Alash Electronics](https://alash-electronics.kz/product/tranzistor-2n2222) | 50 тг each | Confirmed listed |
| 1N4148 flyback diode | 3 (1 needed + spares) | Alash Electronics (electronic components section) | not pinned down | Category confirmed, nearly free either way |
| Resistor, 220Ω-1k (either works) | 5 (1 needed + spares) | [Alash Electronics](https://alash-electronics.kz/collection/rezistory) | not pinned down | Category confirmed |
| Li-ion battery, 18650, 3400mAh (LiitoKala) | 1 | [Alash Electronics](https://alash-electronics.kz/product/originalnyy-akkumulyator-liitokala-18650-nadezhnyy-litiy-ionnyy-element-dlya-vysokoproizvoditelnyh-ustroystv) | 2,500 тг | **Confirmed in stock** - still an 18650 cylindrical cell, see the battery note below |
| TP4056 charge module, with protection, Type-C | 1 | [Alash Electronics](https://alash-electronics.kz/collection/zaryadnye-ustroystva/product/modul-zaryadki-li-ion-akkumulyatorov-na-tp4056-1-a-type-c) | 200 тг | **Confirmed in stock** |
| USB-C cable | 1 | Either store | not pinned down | Any electronics shop has these |

### Vibration motor gap — the one part actually hard to get right now

The exact part used throughout this project (3V, 10×3mm "tablet" vibration
motor) shows **out of stock** at Alash Electronics as of this check
(pre-order available, no ETA given), and wasn't found listed at RadioBazar
at all. Before making a special trip for just this part:

- **Call Alash Electronics first** (+7 700 900 17 90) - online "out of
  stock" at small component shops doesn't always match what's actually on
  a shelf, and it's worth asking whether a pre-order has a real timeline.
- **A phone-repair stall is a legitimate alternative source.** This exact
  type of motor (a tiny coin/tablet vibration motor) is the same part used
  in almost every phone - any phone-repair counter (Tastak market has
  several) likely has one pulled from repair stock or sold as a spare
  part, often cheaper than an electronics-hobby store. Bring the
  dimensions (10×3mm) or a reference photo.
- Failing both, RadioBazar's "моторы и приводы" (motors and drivers)
  category is confirmed to exist even though a specific vibration motor
  wasn't confirmed in it - worth a look in person.

### Battery note — read before buying

The battery confirmed in stock (at both Alash Electronics and the earlier
Arduino Parts check) is a cylindrical **18650 cell**, not the flat LiPo
pouch cell the original enclosure design assumed. This matters for more
than just capacity:

- **It's a different shape.** 18650 is a tube, roughly 18mm diameter ×
  65mm long. `enclosure/enclosure.scad`'s placeholder battery dimensions
  (25×20×6mm) assume a flat pouch cell - an 18650 won't fit that cavity,
  the enclosure would need a cylindrical battery bay, which is a real
  design change, not done in this pass.
- **No built-in protection circuit** on the bare cell - charging it
  through the TP4056-with-protection module above covers over-charge/
  over-discharge during charging, but double check the cell's own
  discharge behavior before wiring it in.
- **Still worth asking in person** whether either store has a flat pouch
  LiPo instead - two separate checks now (Arduino Parts, then Alash
  Electronics) have both only turned up 18650s online, which is decent
  evidence it's genuinely the more available format locally, not just a
  search-indexing gap.

## Prototyping, soldering & wiring, tools

Not re-checked store-by-store this pass - Alash Electronics' broader
catalog (microcontrollers, resistors, cables/adapters, BMS/charging
boards) strongly suggests it carries general prototyping and soldering
supplies too, consistent with what RadioBazar was already confirmed to
carry:

| Item | Qty | Where | Confidence |
|---|---|---|---|
| Breadboard | 1 | Alash Electronics or RadioBazar | Not re-confirmed this pass - was confirmed at Arduino Parts before it closed, both alternatives are full-catalog component shops so likely carry it too |
| Jumper wires (M-M and M-F) | a few packs | Either store | Universally stocked |
| Soldering iron (+ multimeter if bundled) | 1 | RadioBazar ("паяльное оборудование" category, confirmed) | Category confirmed at RadioBazar; check Alash Electronics too |
| Solder wire, wire stripper, screwdriver set, hookup wire, heat-shrink, "third hand" stand, crocodile clips | 1 each | RadioBazar | Category confirmed ("паяльное оборудование"), individual items not itemized |

## Enclosure assembly

Unchanged from before - general hardware/craft items, not specialty
electronics:

| Item | Qty | Where |
|---|---|---|
| Hot glue gun | 1 | Any hardware/craft store |
| Calipers | 1 | Any hardware store, or ask at Alash Electronics/RadioBazar |
| 20mm wristband/watch strap | 1 | A watch/accessories stall - Tastak market has these too |
| 3D printing (base + lid + clip) | 1 job | Check a school makerspace first, or ask at Alash Electronics/RadioBazar |

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
prices than the Arduino Parts version did, precisely because that version
had more time to get specific confirmations before it had to be redone.
