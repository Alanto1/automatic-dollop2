# Pwnagotchi

> A Raspberry Pi that wears an e-ink "face" and learns to collect WiFi
> handshakes — a Tamagotchi-styled WiFi research pet. DIY, open-source, and a
> brilliant way to learn WiFi security and reinforcement-learning basics.

![role: WiFi handshake collector] ![skill: DIY / intermediate]

## Overview
Pwnagotchi is open-source software you install on a **Raspberry Pi Zero W / Zero
2 W** (or similar). It uses the Pi's WiFi in monitor mode to passively and
actively encourage nearby **802.11 WPA/WPA2 handshakes and PMKIDs** to be
captured, saving them for **offline** password-cracking analysis. Its gimmick is
a cute e-ink face whose mood reflects how "well" it's doing, and an A2C
reinforcement-learning agent that tunes its channel-hopping/attack parameters
over time. It's as much a learning project about WiFi and ML as a tool.

## Characteristics
- **Platform:** Raspberry Pi Zero W / Zero 2 W (BYO hardware) + microSD + battery.
- **Display:** small **e-ink/e-paper** "face" (various supported panels).
- **Interface:** headless; manage over USB-gadget/BLE or SSH; optional web UI.
- **Radio:** the Pi's on-board **2.4 GHz** WiFi (monitor mode); can pair with plugins.
- **Software:** open-source, plugin ecosystem; captures stored as **.pcap** files.
- **"AI":** an actor-critic (A2C) agent that adapts its own capture strategy.

## Capabilities & possibilities
- **Passive handshake / PMKID harvesting** into pcap files for later analysis.
- **Reinforcement learning demo:** watch parameters self-tune as it "gains XP."
- **Plugins:** GPS logging/wardriving, web dashboard, auto-upload to cracking
  services, display customisation, bettercap integration.
- **Peer awareness:** multiple units can recognise each other ("friends").
- **Teaching tool:** hands-on way to understand the WPA 4-way handshake, monitor
  mode, and why weak passphrases fail.

## Legitimate uses
- Learning WiFi security and the WPA handshake on **your own** networks.
- Auditing the resilience of **your own** WiFi passphrases (capture → crack →
  confirm they're strong enough).
- A friendly on-ramp to reinforcement learning and Linux/RF hacking.
- Authorised wireless assessments where passive collection is in scope.

## Limits & the law
- **Capturing handshakes is only for networks you own or are authorised to
  audit.** Passively collecting other people's handshakes and cracking them is
  illegal in most jurisdictions — this is the whole legal crux of the device.
- It **captures**; the actual cracking happens **offline** (e.g. hashcat) and
  only succeeds against weak passphrases — strong/random passwords defeat it.
- **2.4 GHz only** via the Pi's radio; limited range/throughput.
- WPA3 (SAE) is not vulnerable to the classic handshake-crack workflow.
- DIY: you assemble the Pi, screen, battery, and deal with driver/monitor-mode quirks.

## Getting started
1. Flash the Pwnagotchi image to a Pi Zero W/Zero 2 W; attach a supported e-ink panel.
2. Connect over USB-gadget and reach the web UI / SSH.
3. Point it at **your own** WiFi, capture a handshake, then crack it yourself to
   confirm your passphrase is strong.
4. Explore plugins (GPS, dashboard) once the basics work.

## See also
- Broader WiFi tooling: [categories/wifi-network.md](../categories/wifi-network.md)
- Compare: [M5Stick](m5stick.md) (smaller, ESP32) · a plain laptop + [Alfa adapter](../categories/wifi-network.md) is more capable for real assessments.
