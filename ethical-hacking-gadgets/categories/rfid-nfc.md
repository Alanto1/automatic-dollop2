# RFID / NFC Tools

Everything for reading, writing, emulating, cloning, and analysing contactless
cards and tags. Split by frequency: **LF (125/134 kHz)**, **HF/NFC (13.56 MHz)**,
and **UHF (~900 MHz)**. This is the world of building-access badges, transit
cards, hotel keys, pet chips, and inventory tags.

> ⚠️ Cloning, skimming, or emulating **someone else's** credential is illegal.
> Use only on cards/systems you own or are authorised to test.

## Core research & cloning tools
| Device | Freq | Role | Approx price | Notes |
|---|---|---|---|---|
| **Proxmark 3 RDV4** | LF + HF | read/write/emulate/**sniff**, run attacks | ~€219–414 | the reference platform → [device page](../devices/proxmark3.md) |
| **iCopy-XS** | LF + HF | one-button portable cloner (Proxmark-based) | ~€280–529 | screen-driven, no CLI needed |
| **Chameleon Ultra** | LF + HF | world's smallest emulator + cracking | ~€129 | keychain-sized card emulation |
| **Chameleon Lite** | HF | low-cost MIFARE emulation | budget | HF/MIFARE focus |
| **Flipper Zero** | LF + HF | casual read/emulate legacy cards | ~€182+ | fine for weak cards → [device page](../devices/flipper-zero.md) |
| **Keysy** | LF (125 kHz) | pocket duplicator/emulator | budget | quick fob copies |
| **LilyGo T-Embed CC1101** | HF | ESP32-S3 handheld with PN532 NFC (Bruce) | ~€40–60 | HF only → [device](../devices/lilygo-t-embed-cc1101.md) |

## Readers / writers / diagnostics
| Device | Freq | Use |
|---|---|---|
| **DL533N USB Reader/Writer** | HF (13.56 MHz) | LibNFC read/write/crack |
| **DL533N XL (long-range)** | HF | ISO 14443A/B up to ~18 cm |
| **Industrial Handheld UHF Reader** | UHF | inventory/asset UHF tags |
| **RFID Field Detector Ultra** | LF/HF/UHF | tri-band: detect which RFID field a reader uses |
| **13.56 MHz Field-Strength Meter** | HF | ISO-calibrated antenna diagnostics |

## Long-range capture & specialised (professional / red-team)
| Device | Range | Purpose |
|---|---|---|
| **Long-range iCLASS capture system** | up to ~45 cm | authorised badge-capture assessments |
| **MaxiProx 5375 (125 kHz)** | up to ~60 cm | LF long-range capture |
| **Stealth Decoy Reader** | on-contact | credential/PIN collection during red-team ops |
| **Dual-mode Paxton long-range reader** | long | Paxton-system assessments |
| **ESP RFID Tool** | — | Wiegand logging/replay implant |
| **iCS Decoder (iCLASS SE/SEOS)** | — | specialised SE/SEOS work |

## "Magic" cards & blanks (the writable media)
- **Magic MIFARE cards** (Gen1a/Gen2/CUID/UFUID) — have a writable UID block so a
  read card can be copied onto them (for **your own** cards / lab use).
- **T5577** — writable LF card, the standard blank for 125 kHz cloning.
- **NTAG / MIFARE Ultralight blanks** — general HF/NFC tags for projects.

## What's easy vs. what's hard (the security reality)
| Card tech | Freq | Status |
|---|---|---|
| EM4100, HID Prox, Indala | LF | **legacy / trivially cloned** |
| MIFARE **Classic** | HF | broken crypto (Crypto-1); key-recoverable |
| MIFARE **Ultralight / NTAG** | HF | often no real access crypto |
| MIFARE **DESFire EV2/EV3** | HF | **strong** (AES, diversified keys) — resists cloning |
| **iCLASS SE / SEOS** | HF | **strong**, needs specialised tooling |
| EMV payment cards | HF | strong crypto; **not** clonable by these toys |

**Takeaway:** these tools are devastating against *legacy* access control and a
teaching aid against modern secure cards — which is exactly why organisations
should migrate off LF Prox and MIFARE Classic.

## Antennas & range boosters
Range depends on the coil. Options include Proxmark long-range LF/HF antenna
packs, NFC range extenders/booster antennas for the Flipper, and injectable
biochip antennas (ProxRF) for implant work.

## Legitimate uses
- Auditing an organisation's own badge estate (authorised).
- Duplicating your own building/gym fob onto a compatible blank.
- Teaching how and why access control fails; RFID academic research.
- Verifying whether deployed credentials use secure vs. legacy technology.
