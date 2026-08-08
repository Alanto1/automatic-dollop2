# Purchase list — what's actually bought

Verified against the real listings, **2026-08-08**. This is no longer a
proposed cart: it's what's in the basket, what was wrong with it, and what's
still missing.

Design rationale for each part: [`PARTS.md`](PARTS.md).

---

## ✅ Bought and verified correct

### The body (Sesame)

| Item | Qty | Note |
|---|---|---|
| **MG90S metal-gear servo** — roboter-bausatz.de | 10 | 8 + 2 spares, €4.16 in the 5–19 tier. Nobody else in Germany stocks MG90S |
| **XTVTX ESP32-S2 Mini, 4MB flash / 2MB PSRAM** | 3 | Correct board for Sesame's frame, with spares |
| **APKLVSR 0.96" OLED, I2C, 128×64** | 3 | Right resolution. This was out of stock at every German retailer — good catch getting three |
| **Bambu Lab 14500, 7.4V 800mAh Li-ion** | 1 | The exact pack Sesame's BOM names. XH2.54 2-pin, BMS inside, fits the printed bay |
| KCD1 rocker switches, 10A | 8 | |
| Lyeteung JST XH 2.54 2-pin + 150mm 22AWG | 30 prs | Matches the BOM's XH2.54 pigtail |
| GTIWUNG JST 2.0 PH 2-pin + 80mm wire | 20 prs | |
| SCHDRA **22 AWG** silicone wire, 6 colours, 4m ea | 1 | Power wiring, per BOM |
| Fermerry **30 AWG** silicone wire, 6 colours | 1 | Signal wiring, per BOM |
| Self-tapping screws M2/M2.3/M2.6/M3 | 500 | ⚠️ confirm the set actually contains **M2 × 5mm** — Sesame needs ~40 |
| ALAHUGYEF machine screws M2/M2.5/M3 | 500 | |
| TASKTACKER zip ties, 100–300mm | 200 | |
| VooGenzek PCB kit — perfboard, headers, standoffs | 46 pc | |
| 2.54mm breakaway header strips, 40-pin | 20 | |
| Anycubic PLA 1.75mm 1kg, white | 1 | Colour is taste; 1kg is plenty for 11 parts |

### The brain and sensors

| Item | Qty | Note |
|---|---|---|
| **Raspberry Pi Zero 2 WH** (pre-ordered) | 1 | ✅ the **2** matters — see the correction below |
| Camera for Raspberry Pi Zero — BerryBase, €15.90 | 1 | Ships with the narrow Zero ribbon, so **no CSI adapter needed**. Was down to 3 in stock |
| SanDisk Ultra microSDHC A1 32GB | 2 | A1 is fine — the detector loads once at boot |
| Waveshare DC-DC Buck Mini, 4A, 5–36V→5V | 2 | One for Sesame's rail, **one dedicated to the Pi Zero** |
| **TCRT5000 bare sensor** — BerryBase, €0.30 | 4 | Bare, not the module — this is what `cliff_bracket` is cut for. Threshold in software beats a trim pot |
| **AZDelivery VL53L0X ToF** | 1 | Range band **and** the Warden proximity trip |

### The water rig

| Item | Qty | Note |
|---|---|---|
| Adafruit submersible 3V pump, 100mA | 1 | ~30–50cm of head → a **20–56cm** firing band. Enough; the robot walks closer |
| **iMeistek silicone 6mm ID × 9mm OD, 6m** | 1 | Main line. 6mm ID is what Adafruit pairs with this pump |
| iMeistek silicone 2mm ID × 4mm OD, 4m | 1 | **The nozzle tip** — slides inside the 6mm line as a free reducer. A narrow orifice is what turns a weak pump into a jet |
| **UMETASS 60ml HDPE wide-mouth bottles** | 5 | Wide mouth so the 23.5mm pump drops in. **Run 30ml**, not 60 |
| IRLZ44N logic-level MOSFET | 10 | Overkill for 100mA, fine at this price |
| AUKENIEN 1N4007 diode | 200 | ⚠️ **you ordered this twice** — cancel one |
| Innfeeltech 1000µF 16V electrolytic | 50 | Bulk capacitance for the motion engine *and* pump inrush |
| BOJACK resistor kit, 25 values | 1000 | Pull-ups for the bare TCRT5000s |

### Voice + tools

| Item | Note |
|---|---|
| AZDelivery MAX98357A I2S amp | Board only |
| LuluDa mini speaker, 3W **8Ω**, JST-PH2.0 ×4 | 8Ω is the safer load. Amp has screw terminals, so cut the plug or add a socket |
| Preciva 60W soldering station | |
| KELLYSHUN flux + desoldering braid | |
| Solder wire, heat-shrink (2/4/6mm) | already owned |

---

## 🛒 Still to buy

| Item | ~€ | Why |
|---|---|---|
| **Bambu Lab 7.4V charger, XH2.54** ([EU store](https://eu.store.bambulab.com/en/collections/power-supplies)) | **4.49** | The *only* thing that can charge your pack — see below |
| **2nd Bambu 14500 pack** | ~10 | 17 min of walking per charge. One pack is one demo |
| INMP441 I2S microphone | ~4 | Only if you want voice — [`LLM_VOICE.md`](LLM_VOICE.md) |

---

## ❌ Wrong buys, and why

Keep these documented — the reasoning is worth more than the parts.

| Item | Why it's wrong |
|---|---|
| **Raspberry Pi Zero WH** | The original Zero W: **1 core** ARM11 vs the Zero 2's **4** Cortex-A53. YOLO would run at ~0.1–0.3 FPS instead of 1–2. The listing has no "2" in the title — that's the tell |
| **URGENEX B3 charger** | Charges **only** through a 3-pin balance lead, and says *"don't charge Li-ion."* Your pack is Li-ion with a 2-pin plug and a BMS. Nothing to plug in |
| **ENJOY-UNIQUE JST-XH-3P cable** | Same trap: XH2.54 and JST-XH are the same *family*, but **3 pins ≠ 2 pins**. Won't mate |
| **Salomon Soft Flask 250ml** | 250g is 8× the water budget; collapsible so the cradle can't grip it; a submersible pump needs a rigid open container |
| **AOLIKES 18650 2S1P 2600mAh** | ~37×19×65mm and ~100g — won't fit the printed bay, and pushes the robot over its torque budget |
| **Hailege TCRT5000 modules** | Redundant with the bare sensors, and too big for `cliff_bracket` |
| **2nd AUKENIEN 1N4007 pack** | Exact duplicate — 400 diodes for a job needing 1 |
| **24 AWG Temu wire** | Sits between the 22 and 30 AWG you already have, and is *thinner* than your power wire. (Its own listing contradicts itself: "24 gauge" but "0.8mm²", which is 18 AWG — that description is boilerplate shared across all gauge variants) |
| **Raspberry Pi AI HAT+** (26 TOPS, €122.50) | Needs **PCIe** — the Pi Zero has none. Would force a Pi 5, which is larger than Sesame. And 30 FPS for a job needing 1–2 |

## The battery lesson, in one line

**Bare LiPo** → needs a 3-pin **balance lead** and a balance charger.
**Protected pack with a BMS** (yours) → needs only **2 pins**, and a plain
8.4V charger. That single distinction explains every wrong charger above.

⚠️ Sesame's build guide: ***"Never cut the factory battery connector off the
pack."*** Yours is already XH2.54 — nothing to change. Make adapter pigtails
if you ever need a different plug.

---

## Where to buy what

| Shop | For |
|---|---|
| **roboter-bausatz.de** | MG90S — the only German source with quantity tiers |
| **BerryBase** | Zero camera, SD cards, buck converters, TCRT5000, pump, filament |
| **Reichelt** | Pi Zero 2 WH (`RASP PI ZERO2 WH`), IRLZ44N, 1N4007 |
| **Bambu Lab EU store** | Battery + charger |
| **Amazon.de / AliExpress** | ESP32-S2 Mini, SSD1306, screws, wire, tubing, VL53L0X |
| **Segor**, Kaiserin-Augusta-Allee 94, Berlin · Mo–Fr 10:00–13:30 & 14:30–18:00 | Anything you forgot. Mind the lunch closure |

## Confidence

- **High** — every "bought" line was read from the actual listing on
  2026-08-08, and the battery/charger incompatibilities were confirmed from
  the manufacturers' own pages.
- **Medium** — the screw set containing M2×5mm specifically; the exact
  internal diameter of the UMETASS bottles (measure it and set `BOTTLE_D`).
- **Unverified** — one Amazon listing refused to load three times and was
  identified from your description only.
