# Purchase list — Germany

The cart for a **Sesame body + Enforcer layer** build. Prices are what each
retailer's own site listed, VAT included; German maker retailers ship in 1–3
days. BerryBase and Reichelt checked **2026-08-01**, the Sesame-specific parts
**2026-08-05**.

Stock counts are what the shop showed. Several are in single digits and are
called out where it matters.

---

## Headline: ~€197, and the brain is now sized to the robot

The original 12-servo design with a Pi 5 riding on it came to **~€450**. This
lands at **~€197**. Two decisions did it:

| Deleted | Why | Saved |
|---|---|---|
| The whole custom body | Build Sesame instead — 8 servos, not 12+3 | ~€29 servos |
| PCA9685 ×2 | ESP32 drives the servos directly | €13 |
| **Pi 5 → Pi Zero 2 W** | 11g and ~2W instead of 46g and ~6W. A Pi 5 is physically larger than Sesame | **~€99** |
| UBEC, 5A buck, LiPo, charger, LiPo bag | One small buck off Sesame's pack feeds a 2W board | ~€70 |
| Pan/tilt bracket + 2 servos | The robot yaws to aim; vertical is fixed in the printed mounts | ~€20 |

**The Pi 5 RAM surge no longer matters to this build**, because you're not
buying one. (For the record, it was real and verified at two retailers: the
Pi 5 ladder ran €49.20 / €69.50 / €118.50 / €187.50 / €309.50 across 1–16GB
on 2026-08-01. If you ever fall back to a desk-mounted Pi 5, buy the 2GB.)

**What the Pi Zero costs you** is frame rate, not capability — ~1–2 FPS and
512MB. Every trigger here is a multi-second threshold, so that's enough. See
README "Architecture".

---

## Order 1 — BerryBase (berrybase.de) · €76.30

| Item | Qty | Unit | Sum | Stock shown | Link |
|---|---|---|---|---|---|
| Kamera für Raspberry Pi Zero (incl. Zero ribbon) | 1 | 15,90 | 15,90 | **only 3** | [link](https://www.berrybase.de/kamera-fuer-raspberry-pi-zero) |
| SanDisk Ultra microSDHC A1 32GB + Adapter | 2 | 15,60 | 31,20 | 100+ | [link](https://www.berrybase.de/sandisk-ultra-microsdhc-a1-120mb-s-class-10-speicherkarte-adapter-32gb) |
| Waveshare DC-DC Buck Mini, 4A, 5–36V in, 5V out | 2 | 4,90 | 9,80 | 63 | [link](https://www.berrybase.de/waveshare-dc-dc-buck-mini-module-bis-zu-4a-500khz-5-36v-eingang-3-3v-oder-5v-ausgang) |
| TCRT5000 IR Sensor — cliff sensors | 4 | 0,30 | 1,20 | 90 | [link](https://www.berrybase.de/tcrt5000-infrarot-sensor-lichtschranke) |
| Adafruit submersible 3V water pump, 1m cable | 1 | 3,30 | 3,30 | 16 | [link](https://www.berrybase.de/adafruit-tauchbare-3v-dc-wasserpumpe-mit-1-meter-kabel-horizontal) |
| Anycubic PLA Filament 1,75mm 1kg (black) | 1 | 14,90 | 14,90 | 5 | [link](https://www.berrybase.de/anycubic-pla-filament-1-75mm-1kg/farbe-schwarz) |
| | | | **76,30** | | |

⚠️ **The Zero camera showed only 3 in stock.** It's the one that ships with
the *narrow* Zero-format ribbon, which is why it's worth having rather than a
full-size module plus an adapter. If it's gone, buy any Pi camera module plus
Reichelt's `RPIZ CAM ADAPTER` (€1.10) — the Zero's CSI connector is narrower
than a standard Pi's and a normal camera cable **will not fit**.

Two buck converters: one for the Pi Zero, one spare (or for the pump rail).

**On the pump:** it is **submersible, not self-priming** — it sits *inside*
the reservoir, not beside it. That simplifies the plumbing (pump in the
bottle, one tube to the nozzle) but fixes where the reservoir mounts. Decide
this before printing the bracket.

**On the microSD:** A1, not A2. No A2 32GB was stocked at a sane price — NAND
is caught in the same surge as the DRAM. A1 is fine here; the detector loads
once at boot and then runs from RAM.

## Order 2 — roboter-bausatz.de · €41.60

| Item | Qty | Unit | Sum | Link |
|---|---|---|---|---|
| MG90S Micro Servo Motor (metal gear) | **10** | 4,16 | 41,60 | [link](https://www.roboter-bausatz.de/p/mg90s-micro-servo-motor) |

**10 = Sesame's 8 + 2 spares.** Tiers: 1–4 €4.38 · **5–19 €4.16** · 20+ €4.05.
Stock: "Sofort verfügbar, 1-3 Tage."

Nobody in the German maker-shop tier stocks MG90S — BerryBase returns 0 hits,
Reichelt 0 hits on the part number. This shop is the cheapest confirmed German
source with quantity tiers.

**Spares are not optional.** You will strip or burn one during calibration,
and a dead servo mid-build costs you a shipping cycle.

## Order 3 — AliExpress / Amazon · ~€15

The two Sesame parts German maker retailers simply don't carry, plus the
consumables. Order these **first** — they're the longest lead time in the cart.

| Item | Qty | ~€ | Why here |
|---|---|---|---|
| **Lolin/WeMos ESP32-S2 Mini** | 1 (+1 spare) | ~5 ea | Not at BerryBase or Reichelt. Reichelt has an *ESP32-S2-DevKitC-N8* at €10.95, but it's a different board — Sesame's frame is cut for the S2 Mini's footprint |
| **SSD1306 OLED 0.96" 128×64 I2C** | 1 (+1 spare) | ~4 ea | See the stock note below |
| M2 × 5mm self-threading screws | 60 | ~4 | Sesame needs ~40. Buy 60 |
| Silicone tubing + narrow nozzle | — | ~3 | Aquarium airline tubing works |
| XH2.54 pigtails, KCD1 switch, zip ties | — | ~4 | |

⚠️ **The 0.96" SSD1306 was out of stock at BerryBase.** What they had:
0.91" 128×**32** at €6.90 (31 in stock) — *wrong resolution*, half the
vertical pixels, which will break Sesame's face graphics; and a Soldered
0.96" 128×64 SSD1306 at €9.55 that was `nicht lieferbar`. Get the right part
on AliExpress rather than bodging the face — it's the highest
personality-per-euro component in the build.

## Order 4 — Reichelt (reichelt.de) · €24.45

**The brain lives here.** BerryBase had the Pi Zero 2 W listed at €18.90 but
`Artikel aktuell nicht lieferbar` in *every* variant — bare, WH, and all three
starter kits. Reichelt stocks it.

| Item | Order no. | Qty | Unit | Sum |
|---|---|---|---|---|
| **Raspberry Pi Zero 2 WH** (headers pre-soldered) | `RASP PI ZERO2 WH` | 1 | 22,10 | 22,10 |
| IRLZ 44N — MOSFET, N-Ch 55V 47A, TO-220AB | `IRLZ 44N` | 3 | 0,70 | 2,10 |
| 1N 4007 — rectifier diode 1000V 1A, DO-41 | `1N 4007` | 5 | 0,05 | 0,25 |
| | | | | **24,45** |

Take the **WH** (€22.10) over the bare **W** (€19.40). €2.70 buys you
pre-soldered headers, and you need GPIO for the pump MOSFET and the UART link
to the ESP32 — soldering a 40-pin header to a board you can't replace quickly
is a bad trade.

Also on the shelf if you need it: `RPIZ CAM ADAPTER` (15-pin CSI → Zero),
€1.10.

---

## Walk-in: Segor, Berlin-Charlottenburg

**SEGOR-electronics GmbH** — Kaiserin-Augusta-Allee 94, 10589
Berlin-Charlottenburg · Mo–Fr **10:00–13:30** and **14:30–18:00** (closed for
lunch), Sa **10:00–13:00** · U7 Mierendorffplatz, bus M27 · segor.de.

Worth a trip for the things that are absurd to mail-order:

- IRLZ44N + 1N4007 (Order 4 — buy them here instead)
- 22AWG and 30AWG silicone wire, heat-shrink, JST connectors
- M2/M2.5 screws if the AliExpress pack is late
- Perfboard, headers, the odd resistor

Budget **~€20–30**. Mind the 13:30–14:30 lunch closure.

---

## Total

| Block | € |
|---|---|
| Order 1 — BerryBase | 76,30 |
| Order 2 — servos | 41,60 |
| Order 3 — AliExpress | ~15 |
| Order 4 — Reichelt (Pi Zero 2 WH + semiconductors) | 24,45 |
| Segor walk-in bag | ~25 |
| Battery + charger (2S, still to source) | ~15 |
| **Total** | **~197** |

Shipping on top: ~€5–7 each for BerryBase and roboter-bausatz.

## Still to source

- **The battery.** Upstream specifies a Bambu Lab 14500 7.4V 800mAh. Any 2S
  pack of that physical size works, but **check it fits the undercarriage**
  before buying — the frame is printed around it. This is the one part where
  a substitution can cost you a re-print.
- **The Sesame Distro Board PCB**, if you want Option B instead of the
  hand-wired harness. Gerbers are in the repo; a fab run is ~€5–30 plus
  shipping, and adds a lead time. **The hand-wired ESP32-S2 Mini works** —
  start there and treat the PCB as a v2 upgrade.

## Confidence

- **High** — BerryBase and Reichelt prices and stock counts, read from the
  retailers' own listings. The Pi 5 4GB price was cross-checked at two shops
  and matched exactly.
- **High** — the Sesame BOM contents, read from the upstream repo.
- **Medium** — Segor's address and hours (its own site plus two directories,
  consistent). Per-item stock there is not verified; call ahead if something
  is critical.
- **Low** — AliExpress prices (~€ figures are typical, not quotes) and the
  battery line, which is unsourced pending a fit check.
