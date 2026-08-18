# Ethics, Authorisation & the Law

Security-research hardware is legal to own in most countries. **Using it against
systems you don't own or aren't authorised to test is not.** This page is the
non-negotiable framing for everything else in this repo. It is guidance, not
legal advice — laws vary by country, state, and even venue.

---

## 1. The golden rule: authorisation first

Before you point any of these tools at anything, you need **one** of:

1. **Ownership** — it's your device, your card, your network, your car.
2. **Explicit written permission** — a signed scope/authorisation, a bug-bounty
   program's rules, or a penetration-test *Rules of Engagement* (RoE) document.
3. **A controlled lab** — hardware you bought specifically to attack, air-gapped
   or RF-shielded so you don't leak onto other people's systems.
4. **A sanctioned event** — a CTF, a hardware-hacking village, a training range.

If you can't point to one of those four, stop.

### A minimal authorisation checklist
- [ ] Written scope: exact targets (IPs, SSIDs, badge IDs, buildings, hours).
- [ ] Named authoriser who actually owns/controls the target.
- [ ] Explicit list of **out-of-scope** systems and **prohibited** techniques.
- [ ] Emergency contact + a "stop" signal.
- [ ] Data-handling rules (what you may capture, how you store/destroy it).
- [ ] Get it **before** the engagement, keep a copy, don't exceed it.

---

## 2. Radio law (this is where people get in trouble)

Software-defined radios, Sub-GHz tools, and RFID long-range readers **transmit**.
Transmitting is far more regulated than listening.

- **Receiving** is broadly legal in many countries, but **acting on** the
  contents of communications you're not a party to often is **not** (e.g. it's
  illegal to intercept and use others' communications).
- **Transmitting** on licensed/allocated bands (cellular, aviation, GPS,
  emergency services, most of the spectrum) without authorisation is illegal
  and dangerous. **Never** transmit on:
  - Aviation, marine, or emergency-services frequencies.
  - GPS/GNSS bands (jamming/spoofing navigation is a serious offence).
  - Cellular bands (running a fake base station without a licence is a crime).
- Even "harmless" replay of a Sub-GHz remote can be illegal if it's not your gate.
- Region matters: allowed bands/power differ between **EU (ETSI)**, **US (FCC)**,
  and elsewhere. A tool legal to transmit with in one country may not be in another.
- **Amateur radio licence** legitimises a lot of experimentation on ham bands —
  worth getting if you're serious about RF.

**Default posture: receive/observe freely in a lab; do not transmit unless you
know the band is legal for you and you own the target.**

---

## 3. Things that are almost always illegal

- Cloning someone else's access badge / car key / hotel key without permission.
- Skimming payment cards or RFID credentials from people in public.
- Jamming (WiFi deauth floods, GPS jammers, RF jammers) — jamming is illegal in
  most countries even on your own premises.
- Keystroke-injection or implants placed on machines you don't control.
- Intercepting, decrypting, or replaying communications you aren't party to.
- Bypassing locks on property that isn't yours.

Owning a Flipper or a HackRF is fine. Using it to open your neighbour's garage,
clone a colleague's badge, or sniff café WiFi is a crime. Intent and
authorisation are what separate research from an offence.

---

## 4. Responsible disclosure

If your **authorised** testing finds a real vulnerability in a product or system:

1. Report it privately to the vendor/owner first.
2. Give reasonable time to fix (commonly 90 days).
3. Don't exploit it beyond what's needed to prove it.
4. Don't publish working attacks against systems still in the wild without
   coordination.
5. Follow the program's disclosure policy if there is one.

---

## 5. Data handling

Captures from these tools often contain **personal data** (MACs, badge IDs,
handshakes, traffic). Treat it as sensitive:

- Collect the minimum needed for the objective in scope.
- Store encrypted; delete when the engagement ends.
- Never post raw captures containing others' identifiers publicly.

---

## 6. Personal safety & device safety

- Some tools (USBKill, HV glitchers) can **destroy hardware** — know before you plug in.
- Implantable RFID chips are a medical decision; use reputable suppliers.
- LiPo batteries in these gadgets can be a fire risk — don't puncture/overcharge.

---

*Bottom line: these are professional instruments. Used with authorisation they
make systems safer. Used without it they make you a defendant.*
