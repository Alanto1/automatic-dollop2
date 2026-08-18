# Ethical Hacking Gadgets — Field Reference

A curated, vendor-neutral reference to the hardware that security researchers,
red teamers, penetration testers, and hobbyists use for **authorised** testing,
learning, and CTF work. Every device below is documented with its
characteristics, capabilities, legitimate use cases, and the boundaries you must
respect when using it.

> Product landscape and pricing cross-checked against **[Lab401](https://lab401.com/)**,
> a well-known European retailer of security-research hardware. This repo is not
> affiliated with Lab401 — it just uses their catalogue as a survey of what exists.

---

## ⚖️ Read this first

These tools are **dual-use**. The same radio that lets you audit your own garage
door can, in the wrong hands, break the law. This repository documents them for
**legal, authorised, defensive, and educational purposes only**:

- Test only systems **you own** or have **explicit written permission** to test.
- Radio transmit (TX) power and frequencies are **regulated** — many bands are
  illegal to transmit on without a licence (see [`ETHICS_AND_LEGAL.md`](ETHICS_AND_LEGAL.md)).
- Intercepting communications you're not a party to is a crime in most jurisdictions.
- "It was just a demo" is not a legal defence. Get authorisation in writing.

Full guidance: **[ETHICS_AND_LEGAL.md](ETHICS_AND_LEGAL.md)**

---

## 📇 Device index

### Flagship multi-tools & radios
| Device | What it is | Deep dive |
|---|---|---|
| **Flipper Zero** | Pocket multi-tool: Sub-GHz, NFC/RFID, IR, GPIO, iButton, BadUSB | [devices/flipper-zero.md](devices/flipper-zero.md) |
| **HackRF One / HackRF Pro** | Wide-band software-defined radio (1 MHz–6 GHz), half-duplex TX/RX | [devices/hackrf.md](devices/hackrf.md) |
| **PortaPack H4M Pro** | Standalone HackRF-Pro handheld (100 kHz–6 GHz) running Mayhem — no PC | [devices/portapack-h4m-pro.md](devices/portapack-h4m-pro.md) |
| **Proxmark 3 (RDV4)** | The reference RFID/NFC research platform (LF + HF) | [devices/proxmark3.md](devices/proxmark3.md) |
| **M5Stick / M5StickC Plus2** | ESP32 dev-brick; WiFi/BLE tooling, Bruce/M5 firmwares | [devices/m5stick.md](devices/m5stick.md) |
| **LilyGo T-Embed CC1101** | ESP32-S3 handheld: Sub-GHz + NFC + WiFi/BLE, great with Bruce | [devices/lilygo-t-embed-cc1101.md](devices/lilygo-t-embed-cc1101.md) |
| **Pwnagotchi** | AI-flavoured Raspberry Pi WiFi handshake collector | [devices/pwnagotchi.md](devices/pwnagotchi.md) |

### Category guides (many products each)
| Category | Covers | Guide |
|---|---|---|
| **Software-Defined Radio** | HackRF, bladeRF, KrakenSDR, PortaPack, RTL-SDR, tinySA, NanoVNA | [categories/sdr.md](categories/sdr.md) |
| **RFID / NFC** | Proxmark, Chameleon Ultra, iCopy-XS, magic cards, long-range readers | [categories/rfid-nfc.md](categories/rfid-nfc.md) |
| **Sub-GHz / RF remotes** | PandwaRF, Feberis, Flux Capacitor, Minino IoT | [categories/subghz.md](categories/subghz.md) |
| **WiFi / network attack** | WiFi Pineapple, Alfa adapters, Shark Jack, LAN Turtle, Packet Squirrel | [categories/wifi-network.md](categories/wifi-network.md) |
| **USB / HID implants** | Rubber Ducky, Bash Bunny, O.MG Cable, Screen Crab, USBKill | [categories/usb-hid-implants.md](categories/usb-hid-implants.md) |
| **Hardware / firmware audit** | ChipWhisperer, Bus Pirate, GreatFET, Cynthion, Faulty Cat, glitching | [categories/hardware-firmware.md](categories/hardware-firmware.md) |
| **Physical security** | Lockpicks, bypass tools, bump keys, disc-detainer picks | [categories/physical-security.md](categories/physical-security.md) |

---

## 🎯 "Which tool for which job?"

| I want to learn… | Start with |
|---|---|
| Radio / signal analysis | RTL-SDR (cheap) → HackRF One → bladeRF |
| RFID/NFC access control | Proxmark 3 RDV4 or Chameleon Ultra |
| A bit of everything, pocket-sized | Flipper Zero |
| WiFi security | Alfa AWUS036ACHM adapter + a laptop; then WiFi Pineapple |
| Embedded / firmware extraction | Bus Pirate 5 → GreatFET → ChipWhisperer |
| USB attack surfaces | Rubber Ducky → Bash Bunny → O.MG Cable |
| A cheap, open Flipper-style multi-tool | LilyGo T-Embed CC1101 (flash Bruce) |
| Field SDR with no laptop | PortaPack H4M Pro |
| Cheap, hackable, DIY | M5StickC Plus2 or a Raspberry Pi (Pwnagotchi) |

---

## 🗂 Repository layout

```
ethical-hacking-gadgets/
├── README.md                 ← you are here
├── ETHICS_AND_LEGAL.md       ← authorisation, RF law, responsible disclosure
├── GLOSSARY.md               ← LF/HF/UHF, SDR, HID, glitching, etc.
├── devices/                  ← one file per flagship device
└── categories/               ← one file per product category
```

## Contributing

Add a device by copying the section shape used in `devices/*.md`
(**Overview → Characteristics → Capabilities → Legitimate uses → Limits & law →
Getting started**). Keep it factual, keep it legal, cite a source.
