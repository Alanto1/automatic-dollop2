# USB / HID Attack Tools & Implants

Devices that abuse the trust computers place in "human interface devices"
(keyboards, mice) and in innocent-looking cables/adapters. The specialty here is
**keystroke injection (BadUSB)** and covert implants used in **authorised**
physical/red-team engagements.

> ⚠️ Placing an implant or running keystroke-injection on a machine you don't
> own/control is unauthorised access — a crime. Scope everything in writing.

## The landscape (Lab401 & Hak5 ecosystem)
| Device | Approx price | What it is |
|---|---|---|
| **USB Rubber Ducky** | ~€150 | the classic keystroke-injection stick; types payloads at machine speed (DuckyScript) |
| **Bash Bunny Mark II** | ~€355 | multi-vector USB attack platform; emulates several trusted devices at once |
| **O.MG Cable** | ~€145–295 | a full wireless payload/keylogger platform hidden inside a normal-looking cable |
| **O.MG Plug / Unblocker / Adapter Elite** | ~€120–295 | O.MG framework inside a USB plug, data-blocker, or A→C adapter |
| **O.MG Cable Programmer** | ~€49 | flashes/configures O.MG cables |
| **Screen Crab** | ~€400 | inline HDMI implant that captures video with remote management |
| **InputStick RAT** | ~€40–45 | wireless keystroke/mouse control from a phone |
| **USBKill V4** | ~€135–305 | delivers high-voltage surges to **destroy** hardware (destructive test tool) |
| **ESP RFID Tool** | ~€30 | tiny Wiegand-logging RFID implant |
| **Flipper Zero (BadUSB)** | ~€182+ | can run HID payloads too → [device page](../devices/flipper-zero.md) |

### Defensive counterparts
- **O.MG Malicious Cable Detector** (~€69) — spot malicious cables/implants.
- **SkimmerGuard** (~€49) — detect skimmers in ATMs/pumps/terminals.

## Capabilities & possibilities
- **Keystroke injection:** the device presents as a keyboard and "types" a
  payload in a fraction of a second — opening a shell, running a script, etc.,
  bypassing controls that trust keyboards.
- **Multi-device emulation:** a Bash Bunny can appear as keyboard + storage +
  network adapter to chain techniques.
- **Cable/adapter implants:** O.MG hides the whole platform in a cable indistinguishable from a normal one, controllable over WiFi.
- **Video capture:** Screen Crab records what's on an HDMI link.
- **Destructive testing:** USBKill validates surge protection / port hardening.
- **Awareness:** the flip side — teaching people not to trust found cables/USBs.

## Legitimate uses
- **Authorised** red-team and physical-security assessments (with scope + RoE).
- **Security-awareness training** ("don't plug in strange USBs/cables").
- Developing and testing **defensive** controls: USB allow-listing, HID-attack
  detection, port security, endpoint hardening.
- Building detection signatures on the blue-team side.

## Limits & the law
- These attack **physical access + user trust**. Using them on machines/people
  you're not authorised to test is unauthorised access and often wiretap/damage
  offences too.
- Endpoint defences (device control / USB allow-listing, screen-lock discipline,
  EDR HID-attack heuristics) blunt many of these — which is the point of testing.
- **USBKill is destructive** — it can permanently kill hardware. Only on gear you
  own and intend to sacrifice.
- Detectors exist; assume a mature target may catch you.

## Defensive takeaways (why this category matters to blue teams)
- Enforce USB/HID device control and disable auto-run.
- Train staff never to plug in unknown cables, drives, or "found" adapters.
- Lock screens; require re-auth; monitor for rapid scripted keystrokes.
- Use data-blockers from trusted sources and cable detectors in sensitive areas.
