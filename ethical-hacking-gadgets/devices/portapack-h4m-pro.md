# PortaPack H4M Pro (HackRF-based handheld)

> A HackRF crammed into a standalone, touchscreen handheld running the Mayhem
> firmware — no laptop required. All the wideband SDR reach of a HackRF Pro, in a
> pocket device you drive with a wheel and buttons. *Lab401 price: ~€280 (from €395).*

![role: portable SDR] ![skill: beginner-to-intermediate]

## Overview
A "PortaPack" is an add-on board + firmware that turns a HackRF into a
self-contained radio you operate without a PC. The **H4M Pro** is a modern,
integrated build: it packages the **latest HackRF Pro** SDR hardware together
with a screen, controls, battery, and antennas, pre-flashed with the
open-source **Mayhem** firmware. The result is the "grab-and-go" version of the
[HackRF](hackrf.md) — you lose some of the deep PC-tool workflow but gain
instant, field-usable capture/analyse/replay with dozens of built-in apps.

## Characteristics
- **SDR core:** built on the **HackRF Pro** framework — increased operating
  frequency, memory and precision, improved shielding, and an on-board **FPGA**.
- **Frequency range:** **100 kHz – 6 GHz** (native).
- **Duplex / bits:** half-duplex, 8-bit (HackRF lineage) — RX *or* TX, not both.
- **Clocking:** integrated **TCXO**; dual SMA connectors allow external clock sync.
- **Display/controls:** LCD **touchscreen** + arrow keys, **rotary wheel**, select buttons.
- **Audio:** 3.5 mm headphone/mic jack.
- **Power:** replaceable **18650 Li-ion** (9250 mWh) + internal coin cell for RTC/settings.
- **In the box:** two telescopic antennas (75 MHz–1 GHz and 40 MHz–6 GHz), USB-C cable.
- **Firmware:** **Mayhem** — open-source, big community app catalogue, OTA-updatable.

## Capabilities & possibilities
Because it's a full HackRF with a standalone UI, it does most of what an SDR
does — untethered. Mayhem ships **dozens of apps**:

- **Receive/decode:** ADS-B (aircraft), AIS (ships), POCSAG pagers, TPMS (tyre
  sensors), ERT utility meters, radiosonde, analog TV, SSTV, Bluetooth/NRF24
  sniffing, broadcast audio (AM/FM/SSB), spectrum/waterfall analysis.
- **Transmit (where legal, on your own gear):** OOK/key-fob replay, APRS, POCSAG,
  Morse, SSTV, RDS, signal generation.
- **Analyse:** real-time spectrum monitor, signal detection, frequency scanning —
  a field spectrum tool in its own right.
- **Field workflow:** find → capture → replay a Sub-GHz signal without a PC;
  ideal for demos, site surveys, and CTFs.

## PortaPack H4M Pro vs. a bare HackRF
| | HackRF One/Pro + PC | PortaPack H4M Pro |
|---|---|---|
| Standalone (no laptop) | ✗ | ✅ |
| Deep analysis (GNU Radio, URH) | ✅ best | limited (Mayhem apps) |
| Field capture/replay | clumsy | ✅ excellent |
| Same RF core (100 kHz–6 GHz) | ✅ | ✅ |
| Battery + screen included | ✗ | ✅ |

Pick the PortaPack for portable, button-driven work; keep a PC-tethered HackRF
for serious protocol reverse-engineering. Many people own both — same radio, two
workflows.

## Legitimate uses
- Receiving public/unencrypted signals in the field (aviation, weather, AIS, pagers).
- Auditing **your own** Sub-GHz remotes, IoT, and sensors, untethered.
- Spectrum surveys and signal-hunting on-site.
- CTF radio challenges, training, and amateur-radio experimentation.

## Limits & the law
- **Half-duplex, 8-bit** — same fidelity ceiling as any HackRF; not for weak-signal
  work near strong signals or full-duplex protocols (use a bladeRF for that).
- **TX is heavily regulated.** Never transmit on aviation, GPS, cellular, or
  emergency bands; jamming/GPS spoofing are serious crimes. Replaying a remote
  that isn't yours is illegal. See [../ETHICS_AND_LEGAL.md](../ETHICS_AND_LEGAL.md).
- Some Mayhem apps can transmit at a tap — know the band's legality first.

## Getting started
1. Charge the 18650, power on, update Mayhem to the latest release.
2. Start **RX-only**: try ADS-B (1090 MHz) or a weather/AIS receiver.
3. Learn the spectrum/waterfall app to *see* signals before touching TX.
4. Only replay/transmit on your own gear on a band you're authorised to use.

## See also
- The PC-tethered sibling: [HackRF One / Pro](hackrf.md)
- Category context & alternatives: [categories/sdr.md](../categories/sdr.md)
