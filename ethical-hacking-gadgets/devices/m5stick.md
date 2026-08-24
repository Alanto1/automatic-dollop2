# M5Stick / M5StickC Plus2

> A tiny, cheap, hackable ESP32 "brick" that the security community has adopted
> as a pocket WiFi/BLE tool via firmwares like Bruce, M5Launcher, and Marauder.
> The DIY, budget cousin of the Flipper.

![role: WiFi/BLE dev-brick] ![skill: beginner-DIY]

## Overview
M5Stack's M5Stick line (notably the **M5StickC Plus2**) is a finger-sized
development device: an **ESP32** system-on-chip with a colour LCD, buttons, IMU,
buzzer, IR LED, battery, and a Grove/GPIO connector — all in a case, for around
€20–30. Because the ESP32 has WiFi and Bluetooth LE built in, flashing a
security-focused firmware turns it into a capable, self-contained wireless
tinkering and awareness tool. It's beloved for being cheap enough to mod,
solder, and even destroy while learning.

## Characteristics
- **SoC:** ESP32 (dual-core, **2.4 GHz WiFi + Bluetooth LE** on-chip).
- **I/O:** ~1.14" colour LCD, 2 buttons, RTC, 6-axis IMU, buzzer, IR transmitter.
- **Power:** built-in LiPo + USB-C; PMU for battery management.
- **Expansion:** Grove connector + exposed GPIO; huge M5Stack HAT/module ecosystem.
- **Programmable:** Arduino, ESP-IDF, MicroPython, UIFlow; flashable community firmwares.

### Popular firmwares
- **Bruce** — multi-purpose offensive-security firmware (WiFi, BLE, IR, RF with
  add-ons, sub-menus reminiscent of the Flipper).
- **ESP32 Marauder** — WiFi/BLE recon suite (scan, capture, analysis).
- **M5Launcher / vendor UIFlow** — app launchers and no-code development.

## Capabilities & possibilities
- **WiFi (2.4 GHz):** scan networks/clients, survey channels, capture beacons and
  (on suitable firmware) WPA handshakes for **your own** networks, wardriving with GPS HAT.
- **Bluetooth LE:** scan/enumerate nearby BLE devices; BLE experiments.
- **IR:** learn/replay infrared like a universal remote.
- **Sensors/IMU:** motion, tilt, and environment projects.
- **DIY platform:** write your own tools in Arduino/MicroPython; add HATs
  (ENV sensors, GPS, thermal camera, LoRa, etc.).
- **Add-on RF:** with an external CC1101/NRF module it can reach Sub-GHz/2.4 GHz radios.

## Legitimate uses
- Cheap first step into WiFi/BLE security and embedded programming.
- Auditing and monitoring **your own** wireless environment.
- Wardriving/mapping your own coverage; IoT sensor prototyping.
- Classroom/CTF hardware; a "sacrificial" device to learn soldering and flashing.

## Limits & the law
- **2.4 GHz only** for WiFi/BLE — no 5 GHz, and an ESP32 is far weaker than a
  dedicated adapter (e.g. an Alfa) for serious WiFi work.
- Some community firmwares include **deauth/jamming** features — using those
  against networks you don't own is illegal in most countries. Don't.
- Small antenna, small battery, limited RAM — it's a learner/companion, not a lab tool.
- Handshake capture is only lawful on networks you own or are authorised to test.

## Getting started
1. Flash a known firmware (Bruce or Marauder) with the vendor's web flasher.
2. Scan **your own** WiFi and BLE to learn the menus.
3. Try an IR "universal remote" and a simple MicroPython script.
4. Add a HAT (GPS or ENV sensor) for a first real project.

## See also
- WiFi tooling that outclasses it for real work: [categories/wifi-network.md](../categories/wifi-network.md)
- Compare: [Flipper Zero](flipper-zero.md) (polished, more radios) · [Pwnagotchi](pwnagotchi.md) (Pi-based WiFi collector)
