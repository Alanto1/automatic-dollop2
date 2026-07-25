# Purchase list — Almaty edition

Links, prices, quantities, pickup/delivery — checked **2026-07-25** in KZT
(тг). **Confirm on the product page before ordering**, prices and stock
change. Quantities below are for building **one** v1 prototype, with cheap
parts bought a couple spares deep since they're easy to fry while learning
to solder.

## The Almaty-specific thing to know before ordering anything

The two stores in this list have **opposite** fulfillment shapes here:

- **ChipDip.kz has a real office in Almaty** (проспект Абылай Хана, 18,
  н.п. 28, Пн–Пт 9:00–18:00, +7 727 338-33-53) with **free pickup** — no
  shipping cost or wait at all for the two ChipDip items below.
- **AmperMarket.kz's only physical pickup point is in Astana** (проспект
  Абая, 95) — there's no Almaty pickup point. Everything from AmperMarket
  ships to Almaty via **Kazpost**: 1,600 тг for the first kg, +200 тг per
  additional kg, 5–7 business days to the nearest Almaty post office
  (2,000 тг instead if you want cash-on-delivery).

Kazpost charges **per shipment, not per item** — so put every AmperMarket
row below into **one checkout**, not three separate orders across
build phases. That alone is the difference between paying 1,600 тг once
and 4,800 тг three times.

## Electronics (BOM)

| Item | Qty | Store & link | Price | Fulfillment |
|---|---|---|---|---|
| Arduino Nano clone (CH340, **Mini-USB**, pins soldered) | 1 | [AmperMarket.kz](https://ampermarket.kz/arduino/analog-arduino-nano-ch340/) | 3,900 тг | Kazpost to Almaty (combine order — see above) |
| — **if you want USB-C instead**, buy this one instead of the row above | 1 | [AmperMarket.kz](https://ampermarket.kz/arduino/nano-ch340-type-c/) | 2,700 тг (cheaper, too) | Kazpost to Almaty |
| — **skip this one**: genuine Arduino-brand Nano | — | [AmperMarket.kz](https://ampermarket.kz/boards/arduino/original-arduino-nano/) | 26,500 тг | Not worth it for a hobby build — the clone works identically |
| VL53L1X ToF sensor (4m range — what the firmware assumes) | 1 | [ChipDip.kz](https://www.chipdip.kz/product/vl53l1x-distance-sensor-datchik-dalnosti-tof-waveshare-9000791743) | 17,000 тг (16,200 тг for 5+) | **Free pickup at ChipDip's Almaty office** |
| Vibration motor, 10mm flat coin type | 1 | [ChipDip.kz](https://www.chipdip.kz/product/mtr-vibrating) | 790 тг (640 тг for 5+) | **Free pickup, same Almaty office** — bundle with the VL53L1X so it's one trip |
| NPN transistor 2N2222A | 3 (1 needed + 2 spares — cheap insurance against frying one) | [AmperMarket.kz](https://ampermarket.kz/details/transistors/bipolar/2n2222a/) | 30 тг each | Kazpost to Almaty |
| Flyback diode 1N4148 | 3 (1 needed + spares) | [AmperMarket.kz](https://ampermarket.kz/details/diodes/1n4148/) | 10 тг each | Kazpost to Almaty |
| 1k resistor | 5 (1 needed + spares — they're nearly free) | [AmperMarket.kz](https://ampermarket.kz/details/resistors/perm/resistors-1w-1/) | ~40 тг each (approx — exact SKU/value variant not pinned down) | Kazpost to Almaty |
| LiPo battery, 3.7V 800mAh (802535) | 1 | [AmperMarket.kz](https://ampermarket.kz/supplies/acc/lipo-802535-800mah/) | 1,350 тг | Kazpost to Almaty |
| TP4056 charge module **with protection** | 1 | [AmperMarket.kz](https://ampermarket.kz/supplies/chargers/tp4056-1a-li-ion-charger-protect/) | 350 тг | Kazpost to Almaty |
| USB cable, **Mini-USB** (only if you bought the Mini-USB Nano above) | 1 | [AmperMarket.kz](https://ampermarket.kz/cables/usb/usb-cable-a-mini-30-cm/) | 300 тг | Kazpost to Almaty |
| USB cable, **USB-C** (only if you bought the USB-C Nano above) | 1 | [AmperMarket.kz](https://ampermarket.kz/cables/usb/usb-cable-a-type-c-x4/) | 450 тг | Kazpost to Almaty |

**On the USB-C swap**: the USB-C Nano clone is actually 1,200 тг *cheaper*
than the Mini-USB one (2,700 vs 3,900 тг), so there's no downside — buy
that row instead, and get the USB-C cable instead of the Mini-USB one. The
firmware and wiring are identical either way; only the connector on the
board (and the cable you plug into it) changes.

**Flag**: AmperMarket only stocks the VL53L0X (2m max range), not the VL53L1X
(4m) the firmware is built around — since the "far" threshold in
`HapticMapper.h` is exactly 2m, a 2m-max sensor would be right at its own
limit with no margin. As an Almaty buyer this is an even easier call than
it looks in most write-ups of this project: the real VL53L1X ships free
from ChipDip's own Almaty office, so there's no shipping-cost tradeoff
weighing against it — just order the real sensor.

**Power note (worth a second look, not in scope of this pass to redesign)**:
this list wires the LiPo/TP4056 straight to the Nano's 5V pin with no
boost converter in between. That's a common shortcut for battery-powered
Nano clones and usually works, but it means running the board's 16MHz
crystal below the ~4.5V Atmel's datasheet recommends for that speed, and
there's no on/off switch in this list either (disconnect the battery to
power down). Neither is a defect in this list specifically — just flagging
both in case either turns into flaky behavior on the breadboard. A 5V
boost module and a slide switch are both cheap (AmperMarket, a few hundred
тг each) if you want to add them back.

## Prototyping (breadboard phase)

| Item | Qty | Store & link | Price | Fulfillment |
|---|---|---|---|---|
| Breadboard, 830-point | 1 | [AmperMarket.kz](https://ampermarket.kz/breadboards/solderless/breadboard-830-pin/) | 950 тг | Kazpost to Almaty |
| Jumper wires, male-male (65 pcs/pack) | 1 pack | [AmperMarket.kz](https://ampermarket.kz/wires/65-wires-set/) | 750 тг | Kazpost to Almaty |
| Jumper wires, male-female (10 pcs/pack, 20cm) | 1 pack (only need ~4, for the sensor's VCC/GND/SDA/SCL pins) | [AmperMarket.kz](https://ampermarket.kz/wires/mama-papa-20cm/) | 175 тг | Kazpost to Almaty |

## Soldering & wiring (permanent build)

| Item | Qty | Store & link | Price | Fulfillment |
|---|---|---|---|---|
| Soldering iron + multimeter bundle (830LN) | 1 | [AmperMarket.kz](https://ampermarket.kz/soldering/iron/soldering-kit-with-830ln/) | 13,500 тг | Kazpost to Almaty |
| Solder wire, 0.6mm with flux (55g) | 1 spool (lasts many projects) | [AmperMarket.kz](https://ampermarket.kz/soldering/consumables/hx-t100-06mm-55g/) | 2,600 тг | Kazpost to Almaty |
| Wire stripper (mini knife-style) | 1 | [AmperMarket.kz](https://ampermarket.kz/materials/instruments/portable-stripper/) | 200 тг | Kazpost to Almaty |
| Small screwdriver/repair tool set | 1 | [AmperMarket.kz](https://ampermarket.kz/materials/instruments/assist-repair-tool-kit/) | 1,900 тг | Kazpost to Almaty |
| Hookup wire, silicone 20AWG | 2-3m total (e.g. 1m each of 2-3 colors, for motor + battery leads) | [AmperMarket.kz](https://ampermarket.kz/cables/mounting/silicon-wire-20awg/) | 250 тг/m | Kazpost to Almaty |
| Heat-shrink tubing, assorted diameters (11 sizes, 580 pcs) | 1 kit | [AmperMarket.kz](https://ampermarket.kz/soldering/insulators/heat-shrink-tubing-kit/) | 2,900 тг | Kazpost to Almaty — the assortment avoids guessing a single diameter; you mainly want the 2-3mm sizes for the motor leads and 20AWG hookup wire, with a couple larger ones on hand for bulkier splices |
| "Third hand" soldering stand (arm + 2 crocodile clips + lens) | 1 | [AmperMarket.kz](https://ampermarket.kz/soldering/equipment/third-hand/) | 2,900 тг | Kazpost to Almaty — holds a board or wires steady while you solder with both hands |
| Loose crocodile clips (for multimeter testing, or as a heatsink on heat-sensitive leads while soldering) | 4-5 | [AmperMarket.kz — 28mm insulated](https://ampermarket.kz/plugs/alligator-connectors/crocodile-clip-28-mm/) | 50 тг each | Kazpost to Almaty |

Everything in **Electronics + Prototyping + Soldering & wiring** is the
same store (AmperMarket) — put it all in one cart. See the callout at the
top: Kazpost bills per shipment, so one combined order is meaningfully
cheaper than checking out per section.

## Enclosure assembly

| Item | Qty | Store & link | Price | Fulfillment |
|---|---|---|---|---|
| Hot glue gun | 1 | [Kaspi.kz — REXANT 200W](https://kaspi.kz/shop/p/rexant-pistolet-kleevoi-200-vt-11-mm-112244498/) | ~4,442 тг | Kaspi delivery/pickup in Almaty (varies by seller) — or the [full category](https://kaspi.kz/shop/c/glue%20guns/) for cheaper options (basic ones start ~200 тг) |
| Calipers | 1 | [Kaspi.kz calipers category](https://kaspi.kz/shop/c/calipers/) | varies | Kaspi listings here already default to Almaty — basic plastic ones are fine |
| 20mm wristband/watch strap | 1 | [Kaspi.kz watch straps category](https://kaspi.kz/shop/c/watch%20straps%20and%20bracelets/) | varies | Search "ремешок для часов 20мм" if the category link doesn't filter well |
| 3D printing (base + lid + clip, one print job) | 1 job | Check your school's makerspace first | — | Otherwise search "3D печать Алматы" on Kaspi.kz or 2GIS |

## Safety

| Item | Qty | Store & link | Price | Fulfillment |
|---|---|---|---|---|
| Fireproof LiPo charging pouch | 1 | **Not confirmed available locally** — search "сумка для зарядки LiPo аккумуляторов" on Kaspi.kz, or an RC-hobby specialty store | — | If you can't source one in time: charge on a non-flammable surface, away from anything flammable, never unattended |

## Totals

Math shown so you can check it yourself — nothing here is a single opaque
number.

| Group | Subtotal |
|---|---|
| Electronics (USB-C Nano, qty as listed, excl. the two skip/optional rows) | 5,170 тг |
| Prototyping | 1,875 тг |
| Soldering & wiring | 24,875 тг |
| **AmperMarket items subtotal** | **31,920 тг** |
| + Kazpost shipping, one combined order | +1,600 тг (up to +1,800 тг if the iron kit's weight tips the package into the 2nd kg) |
| ChipDip items (VL53L1X + motor), Almaty pickup | 17,790 тг (free pickup, no shipping) |
| Glue gun (Kaspi) | 4,442 тг |
| **Grand total** (excl. calipers/strap/3D-print/LiPo-pouch — all "varies") | **≈ 55,750–55,950 тг** (~$104-110 USD equivalent, order of magnitude — convert at the current rate) |

If you already own basic soldering tools and only need the electronics +
prototyping + ChipDip parts: **≈ 26,435 тг** (5,170 + 1,875 + 1,600 Kazpost
+ 17,790 ChipDip).
