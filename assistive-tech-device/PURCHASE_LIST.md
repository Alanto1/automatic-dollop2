# Purchase List

Real store links and prices, checked **2026-07-25** from Astana/Kazakhstan.
Prices move - confirm on the actual page before ordering, especially
anything more than a few weeks old by the time you read this. Items marked
**[unconfirmed]** had a real product/category page found but the price
didn't come through the fetch (likely rendered client-side) - check the
link directly.

Store baseline: most parts come from **AmperMarket.kz**, which has a
physical pickup point in Astana (проспект Абая, 95) as well as delivery.
A few things (glue gun, calipers, wristband strap) are sourced from
**Kaspi.kz** instead. The one part neither carries - the VL53L1X - comes
from **ChipDip.kz**.

## Weeks 1-2 — Breadboard prototype

| Part | Store | Price | Link |
|---|---|---|---|
| Arduino Nano (CH340 clone, **USB-C**) | AmperMarket.kz | 2,700 тг | https://ampermarket.kz/arduino/nano-ch340-type-c/ |
| VL53L1X ToF sensor, up to 4m (Waveshare) | ChipDip.kz | 17,000 тг (16,200 тг for 5+) | https://www.chipdip.kz/product/vl53l1x-distance-sensor-datchik-dalnosti-tof-waveshare-9000791743 |
| Vibration motor, 10×3mm, 3V/70mA | AmperMarket.kz | 250 тг | https://ampermarket.kz/motors/collector/vibromotor-10x3-mm/ |
| 2N2222 NPN transistor | AmperMarket.kz | 30 тг | https://ampermarket.kz/details/transistors/bipolar/2n2222a/ |
| 1N4148 diode | AmperMarket.kz | 10 тг | https://ampermarket.kz/details/diodes/1n4148/ |
| 220Ω resistor | AmperMarket.kz | a few tens of тг | https://ampermarket.kz/details/resistors/ (browse - exact SKU not picked) |
| LiPo battery, 3.7V 380mAh, 11×48×6mm | AmperMarket.kz | 1,300 тг | https://ampermarket.kz/supplies/battery/lipo-601148-380mah/ |
| TP4056 Li-ion charger w/ protection, Type-C | AmperMarket.kz | 380 тг | https://ampermarket.kz/supplies/chargers/tp4056-1a-li-ion-charger-protect-type-c/ |
| 5V USB boost converter (2-5V in → 5V/1A out) | AmperMarket.kz | 950 тг | https://ampermarket.kz/supplies/power-adapters/usb-boost-converter/ |
| Slide switch, SS12D00G4 | AmperMarket.kz | 30 тг | https://ampermarket.kz/inputs/switch-ss12d00g4-1p2t/ |
| Solderless breadboard, 400 points | AmperMarket.kz | 600 тг | https://ampermarket.kz/breadboards/solderless/breadboard-400-pin/ |
| Jumper wire kit (140 wires) | AmperMarket.kz | 880 тг | https://ampermarket.kz/wires/breadboard-jumpers-kit/ |
| USB-C cable (data-capable) | AmperMarket.kz / Kaspi.kz | varies | check either store - many "charge-only" cables won't work for flashing |

Breadboard-phase subtotal (excluding cable): **~24,130 тг** (≈ real,
summed from the confirmed prices above; add the resistor and cable on
top).

### Why USB-C, why the clone, why ChipDip for the sensor

- **Clone vs genuine Nano**: AmperMarket's genuine Arduino-brand Nano is
  26,500 тг and was **out of stock** as of this check
  (https://ampermarket.kz/boards/arduino/original-arduino-nano/). The
  CH340 clone at 2,700 тг is functionally identical for this project.
- **USB-C vs Mini-USB**: the USB-C clone (2,700 тг) is cheaper than the
  Mini-USB clone (3,900 тг,
  https://ampermarket.kz/arduino/analog-arduino-nano-ch340/) at the same
  store - USB-C wins on both cost and connector convenience. Buy a USB-C
  cable to match, not Mini-USB.
- **VL53L1X from ChipDip, not AmperMarket**: AmperMarket only stocks the
  VL53L0X (2m max range - e.g. the GY-53 board, 2,800 тг,
  https://ampermarket.kz/sensors/proximity/laser-range-sensor-gy53-vl53l0x/).
  `HapticMapper.h`'s far threshold sits exactly at 2000mm, so a 2m-max
  sensor has zero margin - see README's "Sensor substitution warning."
  ChipDip.kz has the real VL53L1X (4m range) but at roughly 6× the price
  of a VL53L0X board, and per the ChipDip listing, in-store pickup is in
  Almaty, not Astana - budget for courier/Kazpost shipping (roughly
  2,200-2,500 тг extra per the listing) or a CDEK pickup point instead.

## Weeks 3-4 — Enclosure

| Part | Store | Price | Link |
|---|---|---|---|
| Calipers (vernier, plastic, 150mm) | Kaspi.kz | **[unconfirmed]** | https://kaspi.kz/shop/p/sibrteh-noniusnyi-plastikovyi-31621-150-mm-113753225/ |
| Glue gun (REXANT, 200W, 11mm) | Kaspi.kz | **[unconfirmed]** | https://kaspi.kz/shop/p/rexant-pistolet-kleevoi-200-vt-11-mm-112244498/ |
| Wristband strap, ~20mm width | Kaspi.kz | varies | https://kaspi.kz/shop/c/watch%20straps%20and%20bracelets/ (no single generic product surfaced - browse and match `strap_width`/`strap_thickness` in `enclosure.scad`) |
| PLA filament | AmperMarket.kz / Kaspi.kz | varies | whatever's compatible with the printer being used |

If a digital caliper is preferred over vernier, AmperMarket also carries
digital ones (e.g. "Штангенциркуль Цифровой ООК52") - not priced here,
worth comparing against the Kaspi options above.

## Open gap: LiPo charging safety

No fireproof LiPo charging pouch was found at either store during this
pass. Until one is sourced: charge on a non-flammable surface, supervised,
never unattended overnight (see README's "Safety notes").

## Total (breadboard phase, confirmed prices only)

Arduino Nano 2,700 + VL53L1X 17,000 + motor 250 + transistor 30 + diode 10
+ LiPo 1,300 + TP4056 380 + boost 950 + switch 30 + breadboard 600 +
jumpers 880 = **24,130 тг** (~$45-50 USD equivalent, order of magnitude -
convert at the current rate, don't trust a fixed number here). Add the
resistor, USB-C cable, and enclosure-phase items on top.
