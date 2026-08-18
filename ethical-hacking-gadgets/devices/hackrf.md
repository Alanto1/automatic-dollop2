# HackRF One / HackRF Pro

> Wide-band, open-source Software-Defined Radio. One board that can observe,
> capture, decode, and (half-duplex) transmit across a huge slice of spectrum.
> The classic teaching SDR from Great Scott Gadgets. *Lab401 HackRF Pro: ~€400;
> PortaPack H4M Pro (HackRF + standalone UI): ~€280.*

![role: SDR] ![skill: intermediate]

## Overview
An SDR moves almost all of the radio into software: the hardware just shifts a
chunk of spectrum to/from your computer as raw I/Q samples, and software does
the demodulation. The HackRF One is the reference "learn everything about RF"
board — enormous frequency coverage, fully open hardware/firmware, and support
in every major SDR toolkit (GNU Radio, GQRX, SDR++, Universal Radio Hacker,
etc.). The **HackRF Pro** is a refreshed variant, and a **PortaPack** turns a
HackRF into a standalone, screen-driven handheld running the Mayhem firmware.

## Characteristics
- **Frequency range:** ~1 MHz – 6 GHz (Pro/PortaPack builds quote 100 kHz–6 GHz).
- **Duplex:** **half-duplex** (transmit *or* receive, not simultaneously).
- **Bandwidth:** up to ~20 MSPS sample rate (≈20 MHz instantaneous view).
- **Resolution:** 8-bit samples (fine for learning; less dynamic range than pricier SDRs).
- **Interface:** USB 2.0 to a host PC; SMA antenna port; expansion header.
- **Open source:** hardware + firmware open; massive documentation and courses.

## Capabilities & possibilities
- **Receive/observe** almost anything in range: ADS-B aircraft, AIS ships,
  pagers, weather satellites (NOAA APT), ISM sensors, Sub-GHz remotes, GSM
  downlink (where legal), broadcast, etc.
- **Spectrum survey:** sweep and see what's transmitting around you.
- **Capture → analyse → decode** unknown signals with tools like Universal Radio
  Hacker; reverse-engineer simple OOK/FSK protocols.
- **Transmit (with care):** replay/generate signals for testing **your own**
  gear on **legal** bands — great for lab work and CTFs.
- **PortaPack/Mayhem:** run standalone (no PC) with a touchscreen — capture,
  analyse, replay in the field.
- **Add-ons:** an antenna switch like **Opera Cake** multiplexes up to 8
  antennas/filters for automated scanning.

## Legitimate uses
- Learning digital signal processing and RF from first principles.
- Receiving public/unencrypted signals (aviation, weather, telemetry).
- Auditing **your own** wireless devices and IoT.
- Antenna and filter experimentation (pair with a NanoVNA/tinySA).
- CTF radio challenges, university labs, amateur-radio experimentation.

## Limits & the law
- **8-bit / half-duplex:** not ideal for full-duplex protocols or weak-signal
  work near strong signals — step up to a bladeRF/USRP for that.
- **Transmit is heavily regulated.** Do **not** transmit on aviation, GPS,
  cellular, emergency, or any band you're not authorised for. Jamming and GPS
  spoofing are serious crimes. See [ETHICS_AND_LEGAL.md](../ETHICS_AND_LEGAL.md).
- Needs a decent antenna per band and (for TX) appropriate filtering to avoid
  spurious emissions.

## Getting started
1. Start **RX-only** with a free tool (SDR++/GQRX) and the stock antenna.
2. Try decoding something legal and public: ADS-B (1090 MHz) or NOAA weather.
3. Explore Universal Radio Hacker to see captured signals as bits.
4. Only transmit once you understand the band's legality and have a target you own.

## Where it sits vs. other SDRs
| | Freq | Duplex | Bits | Note |
|---|---|---|---|---|
| **RTL-SDR** | ~24 MHz–1.7 GHz | RX only | 8 | cheapest way to start |
| **HackRF One/Pro** | 1 MHz–6 GHz | half | 8 | best all-round learner, can TX |
| **bladeRF 2.0** | 47 MHz–6 GHz | **full** | 12 | GSM/GPS work, better fidelity |
| **KrakenSDR** | 100 MHz–1 GHz+ | RX ×5 | 8 | direction-finding / beam-forming |

More detail: [categories/sdr.md](../categories/sdr.md)
