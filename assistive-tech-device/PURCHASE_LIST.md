# Purchase list — Almaty, walk-in only

No shipping, no delivery, no ChipDip. Real physical stores you can walk
into today, checked **2026-07-25**. Prices in KZT (тг) are what each
store's own website lists — **confirm in person**, since a physical
component shop's shelf stock and a website catalog don't always agree,
and small parts (resistors, diodes) often aren't priced online at all.

## Where to go

**Primary: Arduino Parts** — ул. Толе би 189д (угол ул. Гагарина), 3 этаж,
офис 310, Алматы · +7 (705) 174-59-75 · catalog: arduparts.kz (browse
before going, don't order online). A real Arduino/component shop, not a
general electronics chain — carries the sensor, motor, batteries, basic
components, breadboards, and soldering supplies. This covers almost the
whole list in one trip.

**Backup / price check: RadioBazar** — ТД Тастак (Tastak trade center),
ул. Толе-би 266, бутик 37, этаж 2, павильон 3, Алматы · +7 (747) 721-21-68
· 4.6/5 from 47 reviews. Also on Толе би, a few blocks from Arduino Parts
(house numbers 189 vs 266 — same street, haven't confirmed exact walking
distance). Has its own Nano clone cheaper than Arduino Parts, and stocks
overlapping categories (soldering gear, motors, sensors, batteries, tools)
worth comparing if Arduino Parts is out of something.

**Tertiary: Alash Electronics** — ул. Кыз Жибек 104/1, Алматы, self-pickup
confirmed. Mentioned here mainly for one specific item below (cheapest
2N2222 found) — not a first stop.

**Why not the other two stores from the last list**: AmperMarket.kz has no
Almaty pickup point at all (Astana-only) — every item ships, which is the
thing you asked to avoid. ChipDip.kz does have a real Almaty office, but
you've said it's not a good fit either way, so it's dropped regardless of
that.

## The sensor situation (this changes the firmware, not just the list)

**No store above stocks a VL53L1X (4m range)** — that part appears to be
online-order-only in Kazakhstan right now. What's actually on shelves in
Almaty is the VL53L0X (2m range). Rather than block on a part nobody
walk-in sells, `HapticMapper.h`'s far-zone threshold has been lowered from
2000mm to **1800mm** (see the code comment there) — that gives 200mm of
real margin under the VL53L0X's 2m ceiling instead of sitting exactly at
it, where a reading is indistinguishable from "no data." Tests
re-run and still pass (14/14); the browser simulator was updated to match.
If a VL53L1X shows up locally later, that threshold can move back up.

| Item | Qty | Store & link | Price | Confidence |
|---|---|---|---|---|
| VL53L0X laser distance sensor (GY-53) | 1 | [Arduino Parts](https://arduparts.kz/g8559329-datchiki-prostranstva) | 2,800 тг | **Confirmed in stock** |
| — cheaper alternative, ask about this one too | 1 | Arduino Parts, same page (GY-530 / VL53LDK) | 2,000 тг | Confirmed listed, didn't confirm it's the same chip as GY-53 - ask in store |
| — fallback if neither is in stock: ultrasonic | 1 | Arduino Parts, same page (HC-SR04) | 750 тг | Confirmed in stock, but **not a drop-in swap** - wider ~15° beam and different read behavior than a laser spot would need its own look at `HapticMapper.h`'s thresholds, not covered by this pass |

## Electronics (BOM)

| Item | Qty | Store & link | Price | Confidence |
|---|---|---|---|---|
| Arduino Nano clone (CH340, **USB-C**) | 1 | [Arduino Parts](https://arduparts.kz/p103784105-nano-v30-type.html) | 2,300 тг | Confirmed in stock |
| — cheaper, but **Mini-USB not USB-C** | 1 | [RadioBazar](https://radiobazar.kz/g7735493-arduino-moduli-datchiki) | 2,000 тг | Confirmed in stock |
| VL53L0X sensor | — | see sensor table above | 2,800 тг | Confirmed |
| Vibration motor, "tablet" style, 3V, 10×10×3mm | 1 | [Arduino Parts](https://arduparts.kz/g8411965-dvigateli) | 250 тг | **Confirmed in stock** |
| 2N2222 NPN transistor | 3 (1 needed + spares) | [Alash Electronics](https://alash-electronics.kz/product/tranzistor-2n2222) | 50 тг each | Confirmed listed - Arduino Parts/RadioBazar likely carry it too, worth asking first since it's a one-stop convenience if so |
| 1N4148 flyback diode | 3 (1 needed + spares) | Arduino Parts (electronic components section) | not pinned down | Category confirmed, exact item/price not - nearly free either way |
| Resistor, 220Ω-1k (either works) | 5 (1 needed + spares) | Arduino Parts (electronic components section) | not pinned down | Category confirmed, exact item/price not |
| Li-ion battery, 18650, 3000mAh (LiitoKala HG2) | 1 | [Arduino Parts](https://arduparts.kz/p112715575-akkumulyator-liitokala-hg2.html) | not pinned down | **Confirmed in stock - but read the battery note below before buying this** |
| TP4056 charge module, with protection, Type-C | 1 | [Arduino Parts](https://arduparts.kz/p114791182-modul-zaryada-ion.html) | not pinned down | Confirmed in stock |
| USB-C cable | 1 | Either store | not pinned down | Any electronics shop has these |

### Battery note — read before buying

The only battery **confirmed in stock** at a walk-in Almaty store is an
**18650 cylindrical cell** (LiitoKala HG2, 3000mAh) - not the flat LiPo
pouch cell the original design assumed. This matters for more than just
capacity:

- **It's a different shape.** 18650 is a tube, roughly 18mm diameter ×
  65mm long. `enclosure/enclosure.scad`'s placeholder battery dimensions
  (25×20×6mm) assume a flat pouch cell sitting beside the other
  components. An 18650 won't fit that cavity - the enclosure would need a
  cylindrical battery bay, which is a real design change, not done in this
  pass.
- **No built-in protection circuit.** Pouch LiPos sometimes ship with a
  protection PCB attached; this 18650 explicitly doesn't. Charging it
  through the TP4056-with-protection module above covers over-charge/
  over-discharge during charging, but double check the cell's own
  discharge behavior before wiring it in.
- **Worth asking anyway**: ask Arduino Parts or RadioBazar in person
  whether they carry a flat pouch LiPo (search terms didn't surface one
  online, which doesn't mean the shelf doesn't have one - physical
  component shops often stock more than their website lists). If they do,
  prefer it - it'll actually fit the current enclosure design.

## Prototyping, soldering & wiring, tools

Categories are confirmed at both Arduino Parts and RadioBazar; specific
items/prices mostly weren't pinned down online (normal for a physical
component shop - ask when you're there):

| Item | Qty | Where | Confidence |
|---|---|---|---|
| Breadboard | 1 | [Arduino Parts](https://arduparts.kz/g8771321-maketnye-platy) | Category confirmed |
| Jumper wires (M-M and M-F) | a few packs | Either store | Universally stocked, not pinned down |
| Soldering iron (+ multimeter if bundled) | 1 | [Arduino Parts](https://arduparts.kz/g8412071-vse-dlya-pajki) or [RadioBazar](https://radiobazar.kz/g7735489-izmeritelnye-pribory) | Category confirmed at both - compare in person |
| Solder wire, wire stripper, screwdriver set, hookup wire, heat-shrink, "third hand" stand, crocodile clips | 1 each | Arduino Parts ("Всё для пайки") or RadioBazar ("паяльное оборудование") | Categories confirmed, individual items not itemized |

## Enclosure assembly

Not researched this pass - these are general hardware/craft items, not
specialty electronics, so "an actual technology store" doesn't
particularly apply to them. Any hardware store, craft shop, or the Tastak
market itself (which has more than just electronics stalls) should carry:

| Item | Qty | Where |
|---|---|---|
| Hot glue gun | 1 | Any hardware/craft store |
| Calipers | 1 | Any hardware store or Arduino Parts/RadioBazar (electronics shops sometimes stock basic measuring tools) |
| 20mm wristband/watch strap | 1 | A watch/accessories stall - Tastak has these too |
| 3D printing (base + lid + clip) | 1 job | Check a school makerspace first, or ask at Arduino Parts/RadioBazar - shops like these sometimes know a local printing contact |

## Safety

Same open gap as before: no fireproof LiPo charging pouch confirmed
available anywhere in this pass. Until sourced, charge on a non-flammable
surface, supervised, never unattended - this matters somewhat less with
the 18650 cell (no bare pouch to puncture) but the charging precaution
still applies.

## What this list can't give you that the online version could

Exact, verified prices for every line item. Physical component shops
don't always publish per-part pricing for things like individual
resistors and diodes, and this pass didn't call either store to ask.
**Confirmed core total** (Nano + VL53L0X + motor + transistor, the four
prices actually pinned down): **5,400 тг**. Everything else - the
remaining electronics, prototyping supplies, soldering tools - is real and
available at these stores based on their confirmed catalog categories, but
budget loosely rather than trusting a single grand-total number this time.
If you want one anyway as a rough sanity check: comparable parts ran
about **31,900 тг** for electronics+prototyping+soldering in the
online/AmperMarket version of this list - walk-in prices at Arduino
Parts/RadioBazar look similar or slightly cheaper where compared directly
(Nano: 2,300 vs 2,700 тг; motor: 250 тг both places; VL53L0X: 2,800 тг
both places), so that's a reasonable ballpark, not a promise.
