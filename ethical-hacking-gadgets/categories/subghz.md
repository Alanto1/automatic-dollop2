# Sub-GHz / RF Remote Tools

Tools focused on the sub-1 GHz ISM bands (**315 / 433 / 868 / 915 MHz**) where
garage doors, gates, car remotes, doorbells, weather stations, alarm sensors,
and a lot of IoT live. Capture, analyse, decrypt, and (where legal) replay.

> ⚠️ Transmitting on Sub-GHz bands is regulated, and replaying a remote that
> isn't yours is illegal. Rolling-code cloning against others' vehicles/gates is
> a crime. See [../ETHICS_AND_LEGAL.md](../ETHICS_AND_LEGAL.md).

## Fixed code vs. rolling code (the key concept)
- **Fixed code** (older/cheap remotes): the same code every press → trivially
  captured and replayed. Many cheap gates/doorbells.
- **Rolling code** (KeeLoq and friends): the code changes each press, so a naive
  replay fails. Some tools/licences target weaknesses in specific schemes — this
  is advanced, region-sensitive, and legally fraught.

## The landscape (Lab401 & wider)
| Device | Approx price | What it does |
|---|---|---|
| **PandwaRF Rogue Pro** | ~€449 | all-in-one capture/decrypt/transmit; fixed & rolling systems |
| **PandwaRF Marauder** | ~€790 | autonomous covert RF capture + decryption/generation |
| **PandwaRF Kaiju (licence)** | ~€290+ | software to decrypt rolling-code captures & compute future codes |
| **Flipper Zero** | ~€182+ | built-in CC1101 Sub-GHz capture/replay/analyse → [device](../devices/flipper-zero.md) |
| **Feberis Pro** | ~€90 | Flipper RF add-on, ~10× range over stock modules |
| **Flux Capacitor** | ~€65 | Flipper WiFi/IoT connectivity module |
| **Minino: IoT Multitool** | ~€65 | BLE, Zigbee, Thread, Matter detect/sniff/manipulate |
| **tinySA Ultra+** | ~€163 | spectrum analyser — locate the target signal first |
| **KIISU** | ~€79 | credit-card-sized Flipper-compatible alternative |
| **LilyGo T-Embed CC1101** | ~€40–60 | ESP32-S3 + CC1101 + NFC + WiFi/BLE; great with Bruce → [device](../devices/lilygo-t-embed-cc1101.md) |
| **HackRF / PortaPack** | ~€280+ | full SDR approach to Sub-GHz → [SDR category](sdr.md) |

## Capabilities & possibilities
- **Survey** a band with a spectrum analyser (tinySA) to find the target frequency.
- **Capture** a transmission and **decode** the modulation (OOK/FSK) and bits.
- **Replay** *your own* fixed-code remote to prove insecurity in a demo.
- **Analyse rolling-code** schemes for research (advanced; legality varies).
- **IoT protocol work:** BLE/Zigbee/Thread/Matter reconnaissance (Minino).
- **Extend a Flipper** into a serious RF tool with add-on antennas/modules.

## Legitimate uses
- Auditing **your own** garage/gate/doorbell/alarm and IoT sensors.
- Demonstrating why fixed-code remotes should be replaced with rolling code.
- IoT-protocol security research on your own devices.
- CTF/RF challenges and RF-fundamentals learning.

## Limits & the law
- **Never transmit** on a band you're not allowed to, and never replay a remote
  you don't own — that includes "just testing" a neighbour's gate.
- Rolling-code systems resist naive replay; attacking them is advanced and often
  illegal outside a lab you own.
- Region rules (EU ETSI vs US FCC) change what's legal to transmit and at what power.

## Workflow (lab, on your own gear)
1. **Find** the frequency with a spectrum analyser or the device's scanner.
2. **Capture** several presses of your own remote.
3. **Analyse** the protocol/bits (Flipper analyser, URH on an SDR).
4. **Replay** only against your own receiver to confirm the finding.
