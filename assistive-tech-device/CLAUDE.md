# Assistive Tech Device — project context for Claude Code

Read this first in any new session working in this directory. It's a
handoff summary of everything decided and built so far, written so a fresh
session (no memory of prior conversations) can pick up exactly where things
left off.

## Session log — 2026-07-25 scaffolding pass

This entire directory was built in one pass by Claude Code, inside the
`automatic-dollop2` GitHub repo (which previously held an unrelated static
HTML/CSS page and had no connection to this project). The only input was a
handoff-style summary document describing a project that, as far as this
repo's git history shows, had no prior source tree anywhere accessible to
this session — so "scaffolded from a summary" here means genuinely
written from scratch this session, not recovered.

Where the summary described earlier work as already verified, that
verification was **redone from scratch in this pass**, and this file
reports what's actually true now rather than repeating the summary's
claims uncritically:

- **Firmware tests**: written and actually compiled+run with `g++` in
  this environment. 14/14 pass. (The summary's Windows-built
  `test_haptic_mapper.exe` doesn't exist here and isn't reproduced —
  `run_tests.sh` builds a fresh local binary instead, and that binary is
  gitignored rather than committed.)
- **Enclosure**: `openscad` was installed into this sandbox specifically
  to check `enclosure.scad`. All three modules (base, lid, belt-clip
  back) export as valid manifold geometry with no warnings, and headless
  preview renders look like a sane hinged box + lid + clip. That confirms
  the CSG is well-formed, not that it fits real parts — every dimension
  in the file's "[MEASURE YOUR PARTS]" block is still an unmeasured guess.
- **Purchase list pricing**: `PURCHASE_LIST.md` was built from live
  AmperMarket.kz / ChipDip.kz / Kaspi.kz lookups done in this pass (dated
  2026-07-25), not carried over unverified. It happens to corroborate the
  original gotchas below closely (Nano CH340 USB-C at 2,700 тг, Mini-USB
  at 3,900 тг, genuine Nano at 26,500 тг) — see that file for the full
  list and what's still unconfirmed.
- **Simulator**: built, tested in a real headless-Chromium browser
  (screenshots checked across dark/light theme, mobile width, and live
  interaction — sweep, sound toggle, threshold drag), and published; see
  its entry in the directory map below for the live URL.
- **Outreach emails, `.ino`, hardware purchase/assembly**: still exactly
  what the roadmap below says — drafted-but-unsent, reviewed-but-unflashed,
  and not-yet-bought/assembled, respectively. Nothing in this pass
  changed that.

Everything below this point is the original handoff content (lightly
updated where it referred to now-superseded state, e.g. the simulator's
URL and the roadmap checkboxes).

## What this is

A haptic obstacle-detection wearable for low-vision navigation, built as a
**hobby/school project** (good fit for Jugend forscht or an
accessibility-track hackathon down the line). v1 is deliberately minimal:
one forward-facing time-of-flight distance sensor on a wristband, driving
a vibration motor whose pulse rate/strength encodes how close an obstacle
is.

## The one constraint that overrides everything else

**This cannot be ethically shipped or publicized as "helping blind/low-vision
people navigate" without real feedback from an actual low-vision test user.**
Blindfolded self-testing by a sighted person is not sufficient — obstacle
detectors have real failure modes (narrow field of view, missed low/overhead
obstacles, false confidence), and overstating what a hobby prototype does to
a vulnerable audience is a genuine harm, not just a credibility risk.

Two outreach email drafts exist for this (see `outreach/`) and are the
**longest-lead-time item in the whole project** — they should be sent early,
in parallel with the build, not after. As of this handoff they are still
unsent drafts waiting on the builder to fill in placeholders (name, parent
co-signer) and actually send them.

Before any public writeup, demo, or competition submission: get explicit
consent before naming or showing any test user.

## Roadmap / current status

- [ ] **Week 0 — outreach.** Drafted, not sent. See `outreach/`.
- [~] **Weeks 1-2 — breadboard prototype.** Firmware logic is written and
  unit-tested (desktop-side, no hardware needed yet — 14/14 passing, see
  "Session log" above). Hardware itself has not been purchased or
  assembled — see `PURCHASE_LIST.md`. Blindfolded course test (with
  sighted spotter) not yet possible until hardware exists.
- [~] **Weeks 3-4 — wearable enclosure.** `enclosure.scad` render-verifies
  cleanly (base/lid/clip all confirmed via headless OpenSCAD in this
  pass — see "Session log"). Every dimension is still a placeholder —
  needs real caliper measurements once parts arrive, then re-render
  before printing.
- [ ] **Weeks 4-6 — real feedback session** with whoever responds to the
  Week 0 outreach. Not started (outreach not sent yet).
- [ ] **Writeup + consent**, after the above.

## Directory map

```
assistive-tech-device/
├── CLAUDE.md                          this file
├── README.md                          project overview, BOM, wiring, roadmap, failure modes
├── BUILD_CHECKLIST.md                 checklist of every part/tool needed, by build phase
├── PURCHASE_LIST.md                   the checklist above, but with real Astana store links, prices, quantities
├── outreach/
│   ├── outreach_email_verband.md      draft email to a local Blinden- und Sehbehindertenverband chapter
│   └── outreach_email_schule.md       draft email to a school accessibility/inclusion coordinator (parallel path)
├── firmware/
│   ├── obstacle_haptic/
│   │   ├── HapticMapper.h             the actual distance→vibration logic. Pure C++, ZERO Arduino/sensor
│   │   │                              dependencies — this is deliberate, so it's unit-testable on a desktop
│   │   │                              compiler and reusable by the browser simulator. This is the file to
│   │   │                              read/edit if the mapping behavior needs to change.
│   │   └── obstacle_haptic.ino        thin hardware glue: polls VL53L1X over I2C at ~16Hz, hands the
│   │                                  reading to HapticMapper, drives the PWM pin. DEBUG_SERIAL flag for
│   │                                  tuning. Needs the "VL53L1X" Arduino library by Pololu. NOT YET
│   │                                  COMPILED OR FLASHED — no Arduino toolchain in this environment.
│   ├── tests/
│   │   ├── test_haptic_mapper.cpp     14 desktop unit tests for HapticMapper (zone boundaries, pulse timing)
│   │   └── run_tests.sh               g++ build+run script (bash) — actually run in this session, 14/14
│   │                                  passing. Builds a local binary (gitignored, not committed) rather
│   │                                  than shipping a prebuilt one - re-run this yourself, don't trust a
│   │                                  stale binary.
│   └── simulator/
│       └── haptic_simulator.html      interactive browser tool — ports HapticMapper's exact logic to JS.
│                                      Drag a virtual obstacle or hit "Simulate approach", see the motor's
│                                      on/off state, hear a Web Audio buzz, tune thresholds live. No
│                                      hardware needed. Published as a claude.ai Artifact in this session:
│                                      https://claude.ai/code/artifact/11fad495-b365-421a-8ad3-479ae7244d1e
│                                      (republish from this file if that link ever goes stale).
└── enclosure/
    └── enclosure.scad                 parametric OpenSCAD enclosure. Wristband strap-slot mount is the v1
                                       primary (two slots, front+back, like watch lugs — a single-slot
                                       version was considered and rejected because it'd let the pod pivot
                                       around one wrap point instead of sitting flat). A belt-clip
                                       alternative back is also modeled but explicitly flagged as needing
                                       print-and-test iteration, not trusted as-is. ALL dimensions in the
                                       "[MEASURE YOUR PARTS]" section at the top are placeholders — update
                                       from real caliper measurements before printing anything for real.
                                       Render-verified headlessly in this session (see "Session log") —
                                       that checks the geometry is well-formed, not that it fits real parts.
```

## Key decisions and gotchas from this session (don't rediscover these)

- **VL53L1X vs VL53L0X**: AmperMarket.kz (the main local Astana store) only
  stocks the VL53L0X (2m max range), not the VL53L1X (4m) the firmware
  assumes. Since `HapticMapper.h`'s far threshold is exactly 2m, a 2m-max
  sensor has zero margin. Recommendation given: order the real VL53L1X from
  ChipDip.kz instead (ships to Astana via courier/Kazpost/CDEK; in-store
  pickup is Almaty-only), rather than substitute. **Confirmed still
  accurate via a live pricing check on 2026-07-25** — see
  `PURCHASE_LIST.md`.
- **Arduino Nano — buy the clone, not genuine**: AmperMarket sells a
  genuine Arduino-brand Nano for 26,500 тг (confirmed 2026-07-25 — also
  currently out of stock) vs a CH340 clone for 2,700-3,900 тг depending on
  connector. Functionally identical for this project.
- **USB-C is actually cheaper than Mini-USB** for the Nano clone at
  AmperMarket (2,700 тг vs 3,900 тг, both confirmed 2026-07-25) — if given
  a choice, USB-C wins on both cost and connector convenience. Just
  remember to also buy a USB-C cable instead of a Mini-USB one.
- **Toolchain gotcha (Windows)**: if the builder is working from a Windows
  machine with a OneDrive path containing Cyrillic characters (e.g.
  `...\Документы\...`), be aware a portable `w64devkit` toolchain's
  bundled busybox shell may not be able to `cd` into that path (encoding
  issue) — PowerShell handles Unicode paths fine, so prepend w64devkit's
  `bin` folder to `$env:PATH` in PowerShell instead. This scaffolding pass
  itself ran in a Linux cloud sandbox (see "Session log"), not Windows, so
  this couldn't be re-verified here — carried forward as inherited
  context, not re-confirmed. If a future session needs to compile
  something on the builder's actual Windows machine, check for an
  existing w64devkit install before assuming a fresh one is needed.
- **Sourcing baseline**: most BOM parts, prototyping supplies, and tools
  come from AmperMarket.kz, which has an actual physical pickup point in
  Astana (проспект Абая, 95) — not just delivery. A few things (glue gun,
  calipers, wristband strap) are sourced from Kaspi.kz instead. Full
  breakdown with links/prices/quantities is in `PURCHASE_LIST.md` — treat
  prices there as a 2026-07-25 snapshot, confirm on the actual page before
  ordering.
- **No fireproof LiPo charging pouch found locally** — flagged as an open
  gap in `PURCHASE_LIST.md` (still open as of the 2026-07-25 re-check),
  with a fallback safety practice (charge on a non-flammable surface,
  supervised) noted in case one can't be sourced.

## Environment notes

- **This repository**: git-tracked, hosted on GitHub as
  `Alanto1/automatic-dollop2`, this directory living alongside an
  unrelated pre-existing static page at the repo root. This scaffolding
  pass ran in a Linux cloud sandbox (g++ 13.3.0, OpenSCAD 2021.01
  installed for the session, no Arduino toolchain, no display —
  screenshots for `haptic_simulator.html` used `xvfb-run` +
  pre-installed Chromium).
- **The builder's own machine** (per the original handoff, not
  re-verified this pass): Windows 11, primary shell PowerShell, Git Bash
  also available. OpenSCAD installed and used successfully. A working
  C++ toolchain (w64devkit) installed — see the toolchain gotcha above
  for its actual location.

## Natural next steps

1. Send the outreach emails (`outreach/`) — still the most time-sensitive
   open item.
2. Work through `PURCHASE_LIST.md` and actually order parts.
3. Once parts arrive: measure them, update `enclosure.scad`'s placeholder
   dimensions, re-render, then breadboard the circuit per the wiring
   diagram in `README.md`.
4. Flash `obstacle_haptic.ino` (needs the Pololu VL53L1X Arduino library),
   tune thresholds using the breadboard + `haptic_simulator.html` side by
   side, then run the blindfolded course test with a sighted spotter.
