# Hardware & Firmware Audit Tools

Bench tools for getting *inside* embedded devices: talking to debug buses,
dumping firmware, reverse-engineering USB, and doing side-channel / fault-
injection research. This is where hardware hacking gets deep.

> ⚠️ Reverse-engineering and firmware extraction should be done on hardware you
> own or are authorised/licensed to analyse. Respect IP and local RE laws.

## Bus / debug / bring-up
| Device | Approx price | What it does |
|---|---|---|
| **Bus Pirate 5** | ~€59–89 | universal bus tool: UART, SPI, I²C, 1-Wire, JTAG-ish poking; the classic first tool |
| **TermDriver 2** | ~€29 | USB-serial adapter with a built-in display for live serial debug |
| **I2CDriver** | ~€35 | dedicated I²C tool with on-screen visual feedback |
| **SPIDriver** | ~€35 | dedicated SPI tool with on-screen feedback |
| **Pocket USB Power Supply** | ~€20 | 0–30 V / 0–2 A bench supply for powering targets |

## USB reverse engineering
| Device | Approx price | What it does |
|---|---|---|
| **Cynthion** | ~€209 | "the Proxmark of USB" — sniff/analyse/emulate USB; MITM USB links |
| **GreatFET One** | ~€90–115 | flexible hardware-hacking/interface board (Great Scott Gadgets) |
| **GreatFET One – Daffodil** | ~€35 | prototyping shield for GreatFET |
| **BugBlat miniSniffer 2** | ~€149 | compact USB protocol analyser |

## Side-channel & fault injection (advanced research)
| Device | Approx price | What it does |
|---|---|---|
| **ChipWhisperer HuskyPlus** | ~€1,195 | industry-standard **side-channel analysis + fault injection** platform |
| **Faulty Cat** | ~€165 | **EMFI** (electromagnetic fault injection) glitcher — firmware extraction / security-check bypass |
| **Project Reboot** | ~€100–125 | progressive learning target board (UART/SPI/I²C challenges) |

## All-in-one / professional platforms
| Device | Approx price | What it does |
|---|---|---|
| **WHIDBoard Pro** | ~€295 | "lab in a box" — forensic & offensive hardware auditing toolkit + software |
| **MACOBOX** | ~€9,700 | complete hardware-pentest platform: firmware dumping/analysis across many interfaces |
| **Minino: IoT Multitool** | ~€65 | BLE/Zigbee/Thread/Matter recon |
| **CANBus module (Flipper)** | ~€39 | vehicle ECU diagnostics; sniff/send/inject CAN, OBD-II |

## Capabilities & possibilities
- **Interface & bring-up:** find and talk to UART/SPI/I²C/JTAG/SWD on a PCB.
- **Firmware dumping:** read a flash chip's contents to reverse-engineer it.
- **USB RE:** capture and emulate USB to understand/modify device behaviour.
- **Side-channel analysis (SCA):** recover keys from power/EM leakage (DPA/CPA).
- **Fault injection / glitching:** voltage/clock/EM glitches to skip a security
  check (e.g. read-out protection, secure boot) — the core of chip security research.
- **Automotive:** read/inject CAN messages for ECU/diagnostics research.
- **Training:** deliberately-vulnerable target boards to practise safely.

## Legitimate uses
- Security assessment of **your own** or client (authorised) embedded products.
- Vendor product-security teams hardening their own firmware/silicon.
- Academic side-channel/fault-injection research.
- Learning embedded RE with training targets and CTF hardware.

## Limits & the law
- **Skill ceiling is high** — SCA/FI need theory (DSP, crypto, electronics).
- Some devices can **damage** the target (glitching, over-voltage) — expect casualties.
- Read-out protection, secure boot, and encrypted flash raise the difficulty a lot.
- Respect IP/anti-circumvention law; do RE on hardware you're allowed to.

## Starter path
1. **Bus Pirate 5** — learn to find and talk to UART/SPI/I²C on cheap gadgets.
2. **GreatFET / Cynthion** — go deeper on USB and flexible interfacing.
3. **Project Reboot** target — practise structured challenges.
4. **ChipWhisperer** — only once you understand the theory of SCA/FI.
