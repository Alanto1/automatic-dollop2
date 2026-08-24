# Proxmark 3 (RDV4)

> The reference platform for RFID/NFC research. If you're serious about access
> control, this is the tool the pros reach for. *Lab401 RDV4.01: ~€219–414.*

![role: RFID/NFC] ![skill: intermediate-advanced]

## Overview
The Proxmark 3 is a dedicated RFID/NFC research device that can talk to both
**low-frequency (125/134 kHz)** and **high-frequency (13.56 MHz)** cards. Unlike
a general multi-tool, it exposes the raw card protocol, implements the published
attacks against weak RFID schemes, and lets researchers sniff the conversation
between a real card and a real reader. The **RDV4** revision adds a stronger
antenna design, a Bluetooth/battery add-on ("Blueshark"), and SIM/SAM slots.

## Characteristics
- **Dual frequency:** LF (125/134 kHz) **and** HF (13.56 MHz) with swappable antennas.
- **Modes:** reader, tag emulator, and **sniffer** (capture card↔reader traffic).
- **Firmware:** open-source, community-driven (Iceman fork is the de-facto standard).
- **RDV4 extras:** high-Q LF/HF antennas, Blueshark BLE + LiPo module, SIM/SAM.
- **Control:** USB to a host running the Proxmark client CLI; standalone modes too.
- **Portable variants:** the **iCopy-XS** is a screen-driven cloner built on the
  same platform for one-button HF/LF copying without the CLI.

## Capabilities & possibilities
- **Read / identify** virtually any LF and HF card type and report its tech.
- **Attack weak schemes** that are known-broken: e.g. **MIFARE Classic**
  (nested/darkside/hardnested key-recovery), EM4x, HID Prox, T5577 writing.
- **Emulate** cards the device has keys for; **write** to blank/"magic" cards.
- **Sniff** a live badge-to-reader exchange to study a protocol.
- **Research/diagnostics:** measure antenna tuning, brute/dictionary keys,
  script complex flows in the client.

## Legitimate uses
- Auditing an organisation's **own** access-control estate (with authorisation).
- Migrating/duplicating **your own** building fobs onto compatible blanks.
- Academic RFID research and teaching how access control fails.
- Verifying whether deployed credentials use secure vs. legacy tech.

## Limits & the law
- **Modern secure cards resist it:** MIFARE **DESFire EV2/EV3**, **iCLASS
  SE/SEOS**, and properly-configured DESFire use strong crypto and diversified
  keys — the Proxmark reads their presence but won't magically clone them.
- Long-range capture and cloning of **other people's** credentials is illegal.
- Steeper learning curve than a Flipper; the power is in the CLI and knowing
  which attack applies to which card.
- Antenna choice matters — LF and HF need the right coil for good range.

## Getting started
1. Flash the Iceman firmware; launch the Proxmark client.
2. `hf search` / `lf search` on **your own** cards to identify their type.
3. Learn one attack end-to-end (e.g. MIFARE Classic key recovery on a test card).
4. Practice writing to a T5577 (LF) or "magic" HF card you own.

## See also
- Category overview & alternatives (Chameleon Ultra, iCopy-XS, magic cards,
  long-range readers): [categories/rfid-nfc.md](../categories/rfid-nfc.md)
- Lighter/cheaper option: [Flipper Zero](flipper-zero.md) (fine for legacy cards)
