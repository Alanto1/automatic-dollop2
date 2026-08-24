# Glossary

Quick definitions for the acronyms that appear throughout this repo.

## Radio & RFID
- **LF (Low Frequency)** — 125/134 kHz RFID (old access cards, EM4100, HID Prox, pet chips).
- **HF (High Frequency)** — 13.56 MHz RFID/NFC (MIFARE, DESFire, iCLASS, contactless payment).
- **UHF** — ~860–960 MHz RFID (inventory/logistics tags, long-range asset tags).
- **NFC (Near-Field Communication)** — short-range 13.56 MHz subset used by phones, transit, payment.
- **Sub-GHz** — sub-1 GHz ISM bands (315/433/868/915 MHz): garage doors, remotes, sensors, IoT.
- **SDR (Software-Defined Radio)** — radio whose demod/mod is done in software; one box, many protocols.
- **TX / RX** — Transmit / Receive. **Half-duplex** = one at a time; **full-duplex** = both at once.
- **ISM band** — Industrial/Scientific/Medical unlicensed bands (still power/duty-cycle limited).
- **Rolling code** — remote-control scheme where the code changes each press (harder to replay).
- **Fixed code** — static code; trivially replayable (older/cheap remotes).
- **Wiegand** — legacy wiring protocol between an RFID reader and a door controller.

## Signal-analysis instruments
- **Spectrum analyser** — shows power vs. frequency; find what's transmitting (e.g. tinySA).
- **VNA (Vector Network Analyser)** — measures/optimises antennas & RF components (e.g. NanoVNA).
- **Beam-forming / RDF** — direction-finding: locate where a signal comes from (e.g. KrakenSDR).

## Attack techniques / concepts
- **BadUSB / HID injection** — a device pretends to be a keyboard and "types" a payload fast.
- **MITM (Man-in-the-Middle)** — sit between two parties and relay/alter traffic.
- **Deauth** — WiFi management-frame attack that knocks clients off (illegal jamming in many places).
- **Handshake capture** — grabbing the WPA(2) 4-way handshake to attempt offline password cracking.
- **Replay attack** — recording a legitimate signal/transmission and re-sending it.
- **Relay attack** — extending the range between a token and reader in real time (e.g. keyless cars).
- **Side-channel analysis (SCA)** — inferring secrets from power/EM/timing leakage.
- **Fault injection / glitching** — voltage/clock/EM/laser glitches to skip security checks (e.g. EMFI).
- **Firmware dumping** — extracting a chip's flash to reverse-engineer it.

## Buses & hardware
- **UART / SPI / I²C / JTAG / SWD** — common embedded serial/debug interfaces you'll probe.
- **GPIO** — general-purpose I/O pins for wiring to targets/sensors.
- **CAN bus** — the vehicle network ECUs talk over (diagnostics via OBD-II).
- **iButton / 1-Wire** — contact-based memory keys (intercoms, some access systems).
