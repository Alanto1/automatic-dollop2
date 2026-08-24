# ESP32 Firmware Guide (T-Embed CC1101 & friends)

The "most powerful" firmwares for ESP32-S3 multi-tools like the **LilyGo
T-Embed CC1101**, how they compare, and how to run more than one. Everything
here is for use on hardware **you own** — see [../ETHICS_AND_LEGAL.md](../ETHICS_AND_LEGAL.md).

> ⚠️ **Flipper Zero firmware does NOT run on the T-Embed.** Flipper firmwares
> (Unleashed, RogueMaster, Momentum) target the Flipper's **STM32** chip. The
> T-Embed is an **ESP32-S3** — different hardware. Use the ESP32 firmwares below.

## The firmwares, ranked for the T-Embed

| Firmware | Power | Focus | Link |
|---|---|---|---|
| **Bruce** | 🔥🔥🔥 best all-rounder | Sub-GHz + WiFi + BLE + NFC + IR + BadUSB | https://github.com/pr3y/Bruce |
| **CapibaraZero** | 🔥🔥 | closest "Flipper clone" feel; WiFi/BLE/NFC/Sub-GHz/IR/BadUSB | https://capibarazero.com |
| **ESP32 Marauder** | 🔥🔥🔥 (WiFi/BLE only) | deep WiFi/BLE recon, sniffing, PCAP | — |
| **M5Stick Launcher** | multi-boot | hold several firmwares, pick at boot | — |

**Recommendation:** flash **Bruce** first — it's the most complete for this board.
Add **Marauder** later if you want more WiFi depth.

## Flashing (easiest way)
- One-click browser flasher: **https://flash.pingequa.com/devices/t-embed-bruce**
- Needs: desktop + Chrome/Edge + a USB-C **data** cable.
- Stuck connecting? Hold **BOOT**, tap **RESET**, release **BOOT**, retry.

Full first-time walkthrough: [t-embed-cc1101-setup.md](t-embed-cc1101-setup.md).

## Can I install multiple firmwares?
An ESP32 runs **one firmware at a time**, but you have two options:

**Way 1 — Just re-flash to switch (easiest, recommended for beginners).**
The browser flasher takes ~3 minutes, so reflash Bruce → Marauder → CapibaraZero
whenever you want. SD-card files stay put. Downside: one at a time.

**Way 2 — Multi-boot with a Launcher.**
A launcher stores multiple firmware images in separate **OTA partitions** on the
16 MB flash and shows a boot menu — no PC needed to switch.
- **M5Stick Launcher** (supports T-Embed-class boards)
- **ESP32-Flocker** — bundles several binaries + launcher into one file: https://github.com/tobozo/ESP32-Flocker
- Espressif's method: https://developer.espressif.com/blog/switch-between-firmware-binaries/

Caveats: more advanced (partition tables), big firmwares like Bruce are large so
you may fit only **2–3** together, and a bad flash is always recoverable via the
browser flasher.

## The legal line (applies to every firmware)
These unlock **region-unlocked TX, Sub-GHz jamming, WiFi deauth, BLE spam**.
Owning them is fine; **using** those against anything you don't own is a crime
almost everywhere. Stick to your own devices, cards, and networks.
