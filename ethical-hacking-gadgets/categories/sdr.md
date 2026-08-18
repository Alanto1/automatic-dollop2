# Software-Defined Radio (SDR)

Radios whose modulation/demodulation happens in software. You capture raw I/Q
samples over USB and let a PC (or built-in firmware) decode dozens of protocols.
The category to master if you want to *understand* wireless rather than just push
buttons.

> ⚠️ **Receiving public signals is broadly fine; transmitting is heavily
> regulated.** Never TX on aviation, GPS, cellular, or emergency bands. See
> [../ETHICS_AND_LEGAL.md](../ETHICS_AND_LEGAL.md).

## The landscape (Lab401 & the wider market)

| Device | Freq range | Duplex / bits | Approx price | Best for |
|---|---|---|---|---|
| **RTL-SDR (dongle)** | ~24 MHz–1.7 GHz | RX only, 8-bit | ~€30 | cheapest entry; ADS-B, weather, scanning |
| **HackRF One / Pro** | 1 MHz–6 GHz | half-duplex, 8-bit | ~€300–400 | best all-round learner; can TX → [device](../devices/hackrf.md) |
| **PortaPack H4M Pro** | 100 kHz–6 GHz | half-duplex | ~€280 | HackRF + touchscreen, standalone (no PC), Mayhem → [device](../devices/portapack-h4m-pro.md) |
| **bladeRF 2.0 micro xA4** | 47 MHz–6 GHz | **full-duplex**, 12-bit | ~€649–949 | GSM/GPS research, better dynamic range |
| **SignalSDR Pro** | wide | high-end | ~€1,100 | 5G base-station auditing; emulates USRP/PLUTO |
| **KrakenSDR** | 100 MHz–1 GHz+ | 5× coherent RX | ~€799 | **direction finding** / beam-forming / signal hunting |

### Companion instruments (not radios, but essential)
| Device | Type | Approx price | Use |
|---|---|---|---|
| **tinySA Ultra+** | spectrum analyser | ~€163 | *find* what's transmitting; identify target signals |
| **NanoVNA-F** | vector network analyser | ~€110 | measure/tune antennas & RF components |
| **Opera Cake** | antenna switch for HackRF | ~€190 | multiplex up to 8 antennas / 4 filters for auto-scanning |

## What SDRs let you do (legally)
- **Observe & survey** the spectrum: see everything transmitting near you.
- **Receive public/unencrypted signals:** ADS-B aircraft, AIS ships, NOAA
  weather satellites, pagers, ISM sensors, broadcast, telemetry.
- **Capture → decode** unknown signals (Universal Radio Hacker, GNU Radio,
  Inspectrum) to learn a protocol's bits.
- **Antenna/RF experimentation** with a VNA + spectrum analyser.
- **Transmit only** on bands you're licensed/authorised for, against targets you
  own — great for CTFs and controlled labs.

## Choosing one
- **Just starting / on a budget:** RTL-SDR, RX only. You'll learn a ton.
- **Want to transmit & do everything:** HackRF One/Pro (or a PortaPack for
  standalone field use).
- **Full-duplex / GSM / GPS / better fidelity:** bladeRF 2.0.
- **Locate a transmitter (RDF):** KrakenSDR.
- **Always also buy:** decent antennas per band, and ideally a tinSA + NanoVNA.

## Software to pair with them
- **SDR++ / GQRX / SDRangel** — general receivers/waterfalls.
- **GNU Radio** — build signal-processing flowgraphs.
- **Universal Radio Hacker (URH)** — capture/analyse/replay digital signals.
- **dump1090** (ADS-B), **WSJT-X** (weak-signal ham), **satdump** (satellites).

## Legal reminders specific to SDR
- Intercepting communications you're not a party to can be illegal even if you
  can technically receive them.
- **Jamming and GPS spoofing are serious crimes** — never do them.
- TX power, spurious emissions, and allowed bands differ by region (FCC vs ETSI).
