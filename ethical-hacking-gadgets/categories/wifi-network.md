# WiFi & Network Attack Tools

Hardware for auditing wireless and wired networks — from a USB WiFi adapter that
turns your laptop into an assessment platform, to drop-boxes you leave on a LAN
during an authorised engagement.

> ⚠️ Only test networks you own or are explicitly authorised to test. **Deauth /
> jamming is illegal** in most countries. Man-in-the-middle and traffic capture
> on others' networks is a crime. See [../ETHICS_AND_LEGAL.md](../ETHICS_AND_LEGAL.md).

## WiFi assessment
| Device | Approx price | What it does |
|---|---|---|
| **Alfa AWUS036ACHM** | ~€59 | high-sensitivity Linux WiFi adapter (monitor mode/injection) — the workhorse |
| **WiFi Pineapple Mark VII** | ~€355–470 | classic WiFi MITM / rogue-AP assessment platform |
| **Hak5 WiFi Pineapple Pager** | ~€299–395 | portable tri-band auditing with payloads & DuckyScript |
| **AWOK Dual C5 Touch** | ~€175 | WiFi 6 + BLE wardriving accessory (touchscreen) for Flipper |
| **GhostBoard** | — | WiFi 6 / BLE 5 audit board (GhostESP suite) |
| **M5StickC + Marauder/Bruce** | ~€25 | budget 2.4 GHz recon → [device page](../devices/m5stick.md) |
| **Pwnagotchi** | DIY | Pi-based handshake collector → [device page](../devices/pwnagotchi.md) |

### Pineapple modules (Glytch)
- **GPS Module** (~€79) — wardriving / location-aware recon.
- **Mesh Module** (~€79) — LoRa messaging.
- **Ethernet Module** (~€59) — wired connectivity for the Pager.

## Wired network drop-boxes & taps
| Device | Approx price | Role |
|---|---|---|
| **Shark Jack** | ~€150–160 | pocket Ethernet recon with automated payloads |
| **Shark Jack Display** | ~€185 | Ethernet auditing with OLED menu |
| **LAN Turtle** | ~€120 | covert LAN implant, optional 3G remote access |
| **Packet Squirrel Mark II** | ~€180 | inline MITM/payload drop-box |
| **Plunder Bug** | ~€195 | USB-C LAN-tapping device (passive + active) |
| **PiKVM v4 Plus** | ~€359 | hardware remote KVM/RAT with 3/4/5G for red teams |

## Capabilities & possibilities
- **WiFi:** channel survey, discover APs/clients, capture WPA/WPA2 handshakes &
  PMKIDs (for offline cracking of **your** networks), rogue-AP / evil-twin
  assessment, captive-portal testing, wardriving with GPS.
- **Wired:** passive traffic capture, inline MITM, VLAN/segmentation testing,
  remote persistence during authorised engagements.
- **Remote access:** out-of-band KVM/console for testing physical-access controls.

## Legitimate uses
- Authorised WiFi and network penetration tests (with a signed RoE).
- Verifying **your own** WiFi passphrase strength and segmentation.
- Blue-team detection engineering (generate the traffic you must detect).
- Training, labs, and CTF network challenges.

## Limits & the law
- **Deauthentication floods = jamming = illegal** almost everywhere. Don't.
- Capturing/injecting on networks you don't own or aren't scoped for is a crime.
- WPA3 (SAE) resists the classic handshake-crack workflow; strong passphrases
  defeat offline cracking even on WPA2.
- Drop-boxes on a client LAN must be inside an authorised scope and removed after.

## Starter path
1. A laptop + **Alfa AWUS036ACHM** + a Linux distro is the most capable, cheapest start.
2. Learn monitor mode, `aircrack-ng`/`hcxdumptool`, then crack **your own** handshake.
3. Add a WiFi Pineapple for repeatable rogue-AP assessments once you understand the basics.
