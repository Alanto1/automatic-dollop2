# Assistive Tech Device — project context for Claude Code

Read this first in any new session working in this directory. It's a
handoff summary of everything decided and built so far, written so a fresh
session (no memory of prior conversations) can pick up exactly where things
left off.

## Session log — 2026-07-27: flat LiPo 502030 found, Kaspi.kz added as a sourcing option

Seventh pass. The user asked specifically "what about the flat lipo" -
prior passes had repeatedly claimed no flat pouch cell was available
anywhere, based on searches that only tried generic terms ("18650",
"battery"). Searching by the actual size-code convention pouch cells use
("502030", "601148") turned up real listings this time - the earlier
claim was corrected, not silently changed:

- **Confirmed: a flat 502030 LiPo pouch (3.7V, 250mAh, nominal
  5x20x30mm) on Kaspi.kz** - Li-Pol chemistry, built-in
  overcharge/overcurrent protection, 2-pin connector. Re-verified live
  via WebFetch this pass (not just carried over from an earlier search).
  This is a close match for `enclosure.scad`'s original flat-pouch
  cavity, so the cavity's placeholder dimensions were updated to
  30x20x5mm (was 25x20x6mm) to track this specific part, with the
  comment rewritten to say so - still flagged as needing real caliper
  confirmation once the part is in hand, not treated as final.
- **VL53L0X also confirmed listed on Kaspi.kz** (same GY-53 module
  already sourced at Alash Electronics) - added as an alternative
  sourcing option, not a replacement for the walk-in listing.
- **Kaspi.kz added to `PURCHASE_LIST.md` and `PURCHASE_LIST_almaty.html`**
  as a named online option specifically for these two parts, alongside
  the existing walk-in-only framing (Alash/RadioBazar/Ba3ar.kz stay
  primary for everything else) - this is *not* a full switch to
  Kaspi-first sourcing, just folding in the two parts the user asked
  about. Kaspi prices render client-side and can't be fetched
  programmatically, so listings are linked without a pinned price, same
  handling as everywhere else in this project when that's come up.
- **README.md's battery note rewritten** to present the 502030 pouch and
  the 18650 as two real, current options (capacity vs. enclosure-fit
  tradeoff) instead of stating the 18650 as the only one available.
- Files touched: `PURCHASE_LIST.md`, `PURCHASE_LIST_almaty.html`
  (re-tested in headless Chromium after edits), `README.md`,
  `enclosure/enclosure.scad`, this file. `HapticMapper.h` and the
  firmware were not touched - this pass is sourcing/docs only, sensor
  choice and thresholds are unchanged.

## Session log — 2026-07-25, follow-up 4: Arduino Parts closed, PR workflow note

Fifth pass, same day. Two unrelated threads:

**PR workflow**: the PR opened at the end of the tutorial pass (#2) was
merged by the repo owner within a minute of opening. When new work
started after that, `claude/follow-this-yo7wgl` had to be treated as a
fresh branch per this project's git instructions (never stack new commits
on already-merged history) - but since GitHub hadn't deleted the branch
and nothing else had merged to `main` in between, the branch's content
was already identical to `main`, so continuing to commit on it directly
and pushing normally (no force, no reset) landed the same result a
from-scratch branch reset would have. A literal `git checkout -B ... origin/main`
was attempted first and got blocked by the environment's permission
classifier (looked destructive); the content-equivalence check via
`git diff origin/main origin/claude/follow-this-yo7wgl` is what confirmed
the simpler path was safe. Worth knowing for next time: check for
divergence before assuming a reset is required.

**Arduino Parts (the primary store from the previous pass) is now
temporarily closed** (per the user, who would know - not something this
session could verify remotely). Re-researched walk-in options:

- **Alash Electronics** (ул. Кыз Жибек 104/1, Алматы, self-pickup
  Пн-Сб 12:00-20:00, +7 700 900 17 90) is the new primary - confirmed
  in stock: VL53L0X/GY-53 sensor (2,750 тг, cheaper than Arduino Parts'
  2,800), a Type-C Nano clone (2,250 тг, 23 units), TP4056 (200 тг,
  cheapest found anywhere in this project), an 18650 LiitoKala cell
  (3400mAh, 2,500 тг), 2N2222 transistor (50 тг, already known from an
  earlier pass).
- **Gap found, not papered over**: the specific vibration motor
  (10×3mm "tablet" type) is out of stock at Alash Electronics
  (pre-order only) and wasn't found listed at RadioBazar either -
  currently the one part without a confirmed in-stock walk-in source.
  `PURCHASE_LIST.md` suggests calling ahead and, as a genuine
  alternative, checking a phone-repair stall (Tastak has several) -
  this exact motor type is what's inside most phones.
- RadioBazar's own "Arduino modules, sensors" category was checked
  directly this pass (not just assumed from its category name) and
  currently lists only a Nano and an ESP32 - no distance sensor. Keeping
  it as secondary specifically for its cheap Nano (2,000 тг, Mini-USB)
  and general soldering/tools categories, not for the sensor.
- Arduino Parts' info was kept in both `PURCHASE_LIST.md` and
  `PURCHASE_LIST_almaty.html` at the end of this pass, marked closed
  rather than deleted. **Superseded the same day** - see the next entry
  below: the user asked for it to be removed entirely rather than kept as
  a reference, so it's now fully gone from both files.

## Session log — 2026-07-25, follow-up 5: Arduino Parts fully removed, third store added

Sixth pass, same day. The user wanted Arduino Parts gone completely (not
just marked closed) and asked for additional store options beyond Alash
Electronics/RadioBazar, given the previous pass had already turned up one
supply gap (the vibration motor) that neither of those two could fill.

- **All Arduino Parts references removed** from `PURCHASE_LIST.md` and
  `PURCHASE_LIST_almaty.html` - no address, phone, links, or pricing data
  remains in either file. (It's still mentioned in this CLAUDE.md's
  session log, as history of why the primary store changed - that's a
  changelog, not a current recommendation, so it stays factual rather
  than scrubbed.)
- **Ba3ar.kz added as a third store** - genuinely convenient find: it's
  in the exact same building as RadioBazar (ТД Тастак, ул. Толе-би 266,
  2 этаж), just a different boutique (22 vs RadioBazar's 37), so visiting
  both costs no extra travel. Confirmed in stock: TP4056 with protection,
  Type-C (300 тг, 454 units - a real backup to Alash's 200 тг one). Its
  own VL53L0X listing (2,600 тг, cheapest found) is out of stock,
  pre-order only - same gap pattern as Alash's motor, not this pass's
  fault, just genuinely tight local stock on a couple of specific parts
  right now. Also carries a GP2Y0A21YK0F analog IR distance sensor as a
  different-technology option, flagged as not a drop-in (would need
  `HapticMapper.h`/`obstacle_haptic.ino` changes to read an analog signal
  instead of I2C).
- **iArduino.kz checked and ruled out** - despite the name suggesting an
  Arduino-focused KZ store, it's based in Pavlodar, a different city
  entirely. Not included anywhere.
- Net effect on the sensor situation: of three stores now checked for
  VL53L0X specifically, only Alash Electronics has one in stock (2,750
  тг). Worth knowing if Alash is ever out too - Ba3ar.kz's pre-order and
  the analog IR alternative are the fallback paths documented in
  `PURCHASE_LIST.md`.

## Session log — 2026-07-25, follow-up 3: build tutorial

Fourth pass, same day: the user supplied a full draft build tutorial
(phases 0-10, board bring-up through final assembly) and asked for it to
be written to `tutorial.md` and reconciled with the project's actual
current state. It referenced two hardware bring-up sketches that didn't
exist yet (`firmware/hardware_tests/01_sensor_only/`,
`.../02_motor_only/`) - written for real this pass, not just described.
Corrections made against the draft while writing it up: VL53L1X → VL53L0X
throughout (per the prior session's sensor swap), the actual zone
thresholds (1800/1000/400mm, not the draft's rounder 2m/0.5m guesses),
battery wiring goes to the board's **5V pin** not VIN (VIN's onboard
regulator needs more voltage than a single-cell battery provides - this
project deliberately skips a boost converter, see README's power note),
and the 18650-vs-flat-LiPo battery caveat carried through to the 3D-print
phase. `enclosure.scad`'s part-selector variable is near the **top** of
the file (the draft said "near the bottom"), and its actual variable
names are `fit_clearance` and `lid_lip_height`/`lid_lip_clearance` (the
draft used placeholder names `FIT_GAP`/`LID_LIP` that don't exist in the
file) - `lid_lip_clearance` specifically needed a direction correction
too: **increasing** it loosens the lid fit (shrinks the lip), which is
the opposite of what the draft's "smaller if it won't go on" guidance
said. Verified by re-reading `lid()`'s actual geometry math, not guessed.

## Session log — 2026-07-25, follow-up 2: walk-in only, sensor swap

Same day, third pass: the user rejected the shipping-based Almaty list
outright ("ampermarket ships things too long... an actual technology
store", "chipdip is kind of bad") and asked for real walk-in Almaty stores
only. Research found **no walk-in Almaty store stocks a VL53L1X** (4m) -
the whole premise of every earlier version of this project. What's
actually on shelves is the VL53L0X (2m). Rather than leave the shopping
list and the firmware disagreeing with each other, this pass changed both
together:

- `HapticMapper.h`'s `kFarThresholdMm` moved from 2000 to **1800mm** (real
  margin under the VL53L0X's 2m ceiling instead of sitting exactly at it).
  Tests re-run, still 14/14 - they reference the constant symbolically, not
  as a hardcoded literal, so nothing else needed to change there.
- `obstacle_haptic.ino` was rewritten for the Pololu **VL53L0X** library,
  not VL53L1X - different chip, meaningfully different API (no distance
  modes; the continuous-read call blocks instead of offering a separate
  non-blocking check), so this wasn't a find-and-replace, the polling loop
  logic actually changed shape.
- `firmware/simulator/haptic_simulator.html`'s JS mirror updated to match
  (1800mm default), re-verified in headless Chromium.
- New primary sourcing: **Arduino Parts** (ул. Толе би 189д, офис 310,
  Алматы, +7 705 174-59-75) - real walk-in component shop, confirmed
  in-stock: VL53L0X (GY-53, 2,800 тг), Nano CH340 USB-C (2,300 тг),
  vibration motor (250 тг), TP4056, an 18650 Li-ion cell. **RadioBazar**
  (ТД Тастак market, ул. Толе-би 266) as backup/price-comparison. Both
  verified as real physical locations via multiple independent sources
  (2GIS, Yandex Maps, review sites), not just a store's own claims.
- **Battery form-factor gap surfaced, not resolved**: the only battery
  confirmed walk-in is an 18650 cylindrical cell, not the flat LiPo pouch
  `enclosure.scad` was designed around. Flagged in three places
  (PURCHASE_LIST.md, README.md, enclosure.scad's battery comment) rather
  than silently redesigning the enclosure to match - that's real remaining
  work, not done here.

## Session log — 2026-07-25, follow-up: Almaty purchase list + mobile checklist

A later session that day replaced `PURCHASE_LIST.md` with a more detailed
Almaty-based version (the user supplied a different, more complete draft
list - soldering/wiring tools, spare-part quantities - and asked for it to
be re-based on Almaty instead of Astana, with a mobile-downloadable copy).
Real research this time: AmperMarket.kz turns out to have **no Almaty
pickup point** (Astana-only; Almaty orders ship via Kazpost, 1,600
тг/shipment), while ChipDip.kz has a real Almaty office with **free
pickup** - the opposite framing from the original Astana-based list, where
ChipDip was the "ships in" store. `PURCHASE_LIST_almaty.html` is a
self-contained, offline-capable checklist version of the same list
(checkboxes persisted locally, live remaining-total, tap-through links) -
also published as an Artifact, see the directory map below. This pass also
noticed and flagged (but deliberately did not silently fix) two things the
new parts list omits versus the original BOM: a 5V boost converter and a
power switch - see `PURCHASE_LIST.md`'s "Power note" and README's wiring
section.

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
├── PURCHASE_LIST.md                   the checklist above, but with real store links, prices, quantities -
│                                      currently the Almaty walk-in edition (real physical shops, no
│                                      shipping), see its own header before trusting it for a different city
├── PURCHASE_LIST_almaty.html          same list, mobile-first standalone checklist (tap to check off, live
│                                      running total, localStorage-persisted, works offline once opened).
│                                      Published: https://claude.ai/code/artifact/38b6a57a-ecb2-4fa0-bc9a-2c3fd3c63a42
├── tutorial.md                        phase-by-phase build/bring-up tutorial (board alone -> sensor -> motor
│                                      -> combined firmware -> power -> solder -> enclosure -> assembly ->
│                                      blindfolded test -> outreach reminder). Read this alongside
│                                      firmware/hardware_tests/ - the tutorial's Phase 2/3 reference those
│                                      sketches directly.
├── outreach/
│   ├── outreach_email_verband.md      draft email to a local Blinden- und Sehbehindertenverband chapter
│   └── outreach_email_schule.md       draft email to a school accessibility/inclusion coordinator (parallel path)
├── firmware/
│   ├── obstacle_haptic/
│   │   ├── HapticMapper.h             the actual distance→vibration logic. Pure C++, ZERO Arduino/sensor
│   │   │                              dependencies — this is deliberate, so it's unit-testable on a desktop
│   │   │                              compiler and reusable by the browser simulator. This is the file to
│   │   │                              read/edit if the mapping behavior needs to change.
│   │   └── obstacle_haptic.ino        thin hardware glue: polls VL53L0X over I2C, hands the reading to
│   │                                  HapticMapper, drives the PWM pin. DEBUG_SERIAL flag for tuning.
│   │                                  Needs the "VL53L0X" Arduino library by Pololu (not VL53L1X - see
│   │                                  the second follow-up session log entry above for why). NOT YET
│   │                                  COMPILED OR FLASHED — no Arduino toolchain in this environment.
│   ├── hardware_tests/                 disposable bring-up sketches for tutorial.md's Phase 2/3 - each
│   │   ├── 01_sensor_only/             isolates one subsystem so a wiring mistake shows up without the
│   │   │   └── 01_sensor_only.ino      rest of the circuit as a confounder. Not part of the final device -
│   │   └── 02_motor_only/              obstacle_haptic.ino (below) is what actually ships. NOT YET
│   │       └── 02_motor_only.ino       COMPILED OR FLASHED, same as everything else firmware-side.
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

- **VL53L1X vs VL53L0X**: originally the plan here was "order the real
  VL53L1X online since a 2m-max VL53L0X has zero margin against
  `HapticMapper.h`'s far threshold." **Superseded later the same day** -
  see the second follow-up session log entry near the top of this file.
  Once "no shipping at all" became the actual constraint, no walk-in
  Almaty store turned out to stock a VL53L1X anyway, so the project now
  targets the VL53L0X on purpose, with the firmware's margin problem
  solved by lowering the threshold (1800mm) instead of by sourcing a
  bigger sensor. Left the original reasoning here for the record, but
  don't act on "order a VL53L1X" - that's the stale part.
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
   open item, ideally in parallel with the steps below, not after.
2. Work through `PURCHASE_LIST.md` and actually buy the parts - either
   the flat 502030 LiPo pouch via Kaspi.kz or an 18650 in person at Alash
   Electronics, see the battery note for the tradeoff.
3. Follow `tutorial.md` phase by phase, starting from Phase 0 - it covers
   board bring-up, sensor, motor, combined firmware, power, soldering,
   the enclosure fit-and-reprint loop, final assembly, and the blindfolded
   test, in the order that makes problems easiest to isolate. Don't skip
   ahead to soldering or printing before the corresponding breadboard
   phase actually passes.
