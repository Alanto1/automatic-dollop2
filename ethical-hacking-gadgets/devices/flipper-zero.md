# Flipper Zero

> Pocket-sized, open-source multi-tool for exploring and interacting with the
> radios, protocols, and access hardware around you. The Swiss-army-knife entry
> point to the hobby. *Lab401 price: ~€182–285.*

![role: multi-tool] ![skill: beginner-friendly]

## Overview
The Flipper Zero is a handheld device built around an STM32 MCU with a
monochrome LCD, a directional pad, and a cast of radios and interfaces. Its
appeal is breadth: instead of buying a separate Sub-GHz tool, an NFC reader, an
IR remote, and a BadUSB stick, you get all of them behind one playful UI (the
on-screen "cyber-dolphin" that levels up as you use features). A huge community
firmware and app ecosystem extends it far beyond stock.

## Characteristics
- **MCU:** STM32WB55 (ARM Cortex-M4 + M0 for BLE), 256 KB RAM, microSD storage.
- **Display:** 1.4" monochrome LCD, 5-way navigation; ~1–2 week battery (2000 mAh LiPo).
- **Connectivity:** USB-C, Bluetooth LE, microSD, plus a GPIO header.
- **Open source:** firmware and hardware are open; strong DIY/mod culture.

### On-board radios & interfaces
| Subsystem | Frequencies / interface | Typical use |
|---|---|---|
| **Sub-GHz** | 300–348, 387–464, 779–928 MHz (CC1101) | garage/gate remotes, IoT sensors, doorbells |
| **125 kHz RFID (LF)** | EM4100, HID Prox, Indala | old access fobs/cards |
| **13.56 MHz NFC (HF)** | MIFARE Classic/Ultralight, NTAG, etc. | contactless cards, tags |
| **Infrared** | learning IR TX/RX | universal remote, TV-B-Gone style |
| **iButton / 1-Wire** | Dallas keys | intercom keys |
| **GPIO / hardware** | 18 pins (UART, SPI, I²C, 3V3) | wiring to targets, add-on modules |
| **BadUSB** | USB HID | keystroke-injection scripts (DuckyScript) |
| **BLE** | Bluetooth LE | app control, some BLE tinkering |

## Capabilities & possibilities
- **Read / save / emulate** many 125 kHz and 13.56 MHz cards (subject to the
  card's security — see limits).
- **Capture and replay Sub-GHz** signals from *your own* fixed-code remotes;
  analyse protocols; decode common OOK/FSK schemes.
- **Universal IR remote:** learn and replay IR; control screens/AC/TV.
- **BadUSB:** run keystroke-injection payloads for authorised HID testing.
- **GPIO playground:** UART console, SPI/I²C to sensors, logic-level poking,
  hardware bring-up, add-on boards (WiFi devboard, etc.).
- **iButton** read/emulate; **NFC** tag reading/writing; **U2F** second-factor token.
- **Extensibility:** community firmwares (e.g. custom app catalogues) and add-on
  modules (WiFi, GPS, CAN bus, IR blasters) massively widen scope — see the
  [Flipper accessory ecosystem](../categories/subghz.md).

## Legitimate uses
- Auditing **your own** access control, garage remote, and IoT devices.
- Learning RF/RFID/NFC/IR fundamentals cheaply and safely.
- Red-team engagements (with scope) needing a discreet multi-tool.
- Physical-security demos and awareness training.
- Everyday: universal remote, U2F key, GPIO debugging companion.

## Limits & the law
- **Not magic:** it will *not* clone secure, encrypted credentials —
  MIFARE DESFire, iCLASS SE/SEOS, modern rolling-code remotes, EMV payment
  cards are designed to resist it. It shines on *legacy/insecure* systems.
- **Sub-GHz TX is regulated.** Stock firmware region-locks TX for a reason;
  transmitting on the wrong band or on someone else's remote can be illegal.
- Cloning a badge, car key, or gate that isn't yours is a crime regardless of
  how easy the device makes it.
- Some jurisdictions and platforms have restricted sale/import — check locally.

## Getting started
1. Update to the latest stock firmware via the official app (USB-C or BLE).
2. Read your **own** access fob and a saved IR remote to learn the UI.
3. Practice DuckyScript BadUSB on a machine you own.
4. Only then explore community firmware — understand the legal trade-offs first.

## See also
- Category: [Sub-GHz / RF](../categories/subghz.md), [RFID/NFC](../categories/rfid-nfc.md),
  [USB/HID implants](../categories/usb-hid-implants.md)
- Compare with: [M5Stick](m5stick.md) (cheaper, WiFi-focused), [Proxmark 3](proxmark3.md) (serious RFID)
