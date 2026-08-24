# LilyGo T-Embed CC1101

> An ESP32-S3 handheld with a Sub-GHz radio and NFC built in — a low-cost,
> open, Flipper-style multi-tool that shines when flashed with **Bruce**
> firmware. The "DIY Flipper alternative" with a proper rotary UI. *~€40–60.*

![role: multi-tool dev-board] ![skill: beginner-DIY]

## Overview
The T-Embed CC1101 is LilyGo's compact development board that combines an
**ESP32-S3** (WiFi + BLE), a **CC1101 Sub-GHz transceiver**, and a **PN532
NFC/RFID** module behind a colour IPS screen and a clickable rotary encoder. On
its own it's an embedded-dev board; flashed with community offensive-security
firmware like **Bruce**, it becomes a pocket multi-tool covering Sub-GHz, IR,
RFID/NFC, WiFi, BLE, and BadUSB — conceptually similar to a [Flipper Zero](flipper-zero.md)
but cheaper, more open, and with on-board 2.4 GHz WiFi/BLE the Flipper lacks
natively. A **T-Embed CC1101 Plus** revision also exists.

## Characteristics
- **MCU:** ESP32-S3 (dual-core LX7) with on-chip **2.4 GHz WiFi + Bluetooth LE**.
- **Memory:** 16 MB flash, 8 MB PSRAM.
- **Sub-GHz radio:** **CC1101** — 300–348, 387–464, 779–928 MHz.
- **NFC/RFID:** **PN532** (13.56 MHz read/write/emulate).
- **IR:** on-board IR transmit **and** receive.
- **Display/UI:** 1.9" IPS TFT LCD + **rotary encoder** with push-select.
- **Power:** built-in ~1300 mAh LiPo; USB-C; battery-voltage sensing; reset/boot buttons.
- **Open:** fully hackable; Arduino/ESP-IDF/MicroPython, plus flashable firmwares.

### Firmware options
- **Bruce** — the popular open-source ESP32 offensive/red-team multi-tool
  firmware; supports both the standard and CC1101 hardware variants.
- **CapibaraZero**, M5Launcher-style menus, and other community builds.

## Capabilities & possibilities (with Bruce)
- **Sub-GHz (CC1101):** scan 300–928 MHz, raw capture, **replay**, signal
  analysis (and jamming features some firmwares include — see limits).
- **RFID/NFC (PN532):** read, clone, and emulate 13.56 MHz cards (subject to card
  security — legacy/insecure only).
- **IR:** learn and replay infrared — universal-remote style.
- **WiFi (2.4 GHz):** scan, recon, and (firmware-dependent) captive-portal/rogue-AP
  and handshake features for **your own** networks.
- **BLE:** scan and enumerate nearby BLE devices; BLE experiments.
- **BadUSB:** act as a USB HID keyboard to run keystroke-injection payloads.
- **DIY:** write your own apps; it's a full ESP32-S3 dev board underneath.

## T-Embed CC1101 vs. Flipper vs. M5Stick
| | Flipper Zero | **T-Embed CC1101** | M5StickC Plus2 |
|---|---|---|---|
| Sub-GHz | ✅ CC1101 | ✅ CC1101 | ✗ (needs add-on) |
| 13.56 MHz NFC | ✅ | ✅ PN532 | ✗ |
| WiFi / BLE | BLE only (WiFi via add-on) | ✅ **native 2.4 GHz WiFi + BLE** | ✅ WiFi + BLE |
| IR | ✅ | ✅ | ✅ |
| 125 kHz LF RFID | ✅ | ✗ (HF only) | ✗ |
| Polish / ecosystem | ✅ highest | community (Bruce) | community |
| Price | ~€182+ | **~€40–60** | ~€25 |

**Takeaway:** the T-Embed is the sweet spot for someone who wants Flipper-like
Sub-GHz + NFC + native WiFi/BLE in one cheap, open device — at the cost of
Flipper's polish and 125 kHz LF support.

## Legitimate uses
- A cheap, capable on-ramp to Sub-GHz, NFC, WiFi/BLE and embedded security.
- Auditing **your own** remotes, NFC tags, IoT, and WiFi.
- Learning to build ESP32 tools; CTF/lab hardware; a "sacrificial" hackable device.

## Limits & the law
- **HF NFC only** (13.56 MHz) — no 125 kHz LF like the Flipper/Proxmark.
- **2.4 GHz WiFi only** (no 5 GHz), and the ESP32 is far weaker than a dedicated
  adapter for real WiFi work.
- Community firmwares may include **jamming/deauth/Sub-GHz jam** features —
  using those against anything you don't own is illegal in most countries. Don't.
- Won't clone secure cards (DESFire, iCLASS SE/SEOS) or defeat rolling-code
  remotes — it's for legacy/insecure targets and learning.
- DIY caveats: you flash it yourself and deal with firmware quirks.

## Getting started
1. Flash **Bruce** with a browser/web flasher (pick the **CC1101** variant).
2. Explore the menus on **your own** NFC tag, IR remote, and Sub-GHz remote.
3. Scan **your own** WiFi/BLE to learn the recon tools.
4. Try a BadUSB payload on a machine you own; then start writing your own ESP32 apps.

## See also
- Compare: [Flipper Zero](flipper-zero.md) · [M5Stick](m5stick.md)
- Categories: [Sub-GHz](../categories/subghz.md) · [RFID/NFC](../categories/rfid-nfc.md) · [WiFi/network](../categories/wifi-network.md)
