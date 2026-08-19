# Engineering & Programming Roadmap

A personal roadmap, written 2026-08-11, built from the actual evidence in
this repository rather than from a generic "learn to code" template.

---

## What this is built from

Not a questionnaire — the record. Everything below is inferred from things
that are checked into this repo and dated:

- `assistive-tech-device/CLAUDE.md` — ten session logs, 2026-07-25 to
  2026-07-31, including two real hardware bring-up sessions.
- `assistive-tech-device/README.md` — current build status, honest about
  what is and isn't done.
- `.HTML` + `file.CSS` at the repo root — an Algoritmika course exercise
  ("BitMarket"), the only code in this repo written without assistance.
- The git history — 8 merged PRs, and a recurring workflow problem the
  logs themselves flag four separate times.

Where this roadmap makes a claim about your skill level, it points at the
evidence. Where it guesses, it says so.

---

## Part 1 — Where you actually are

### What you can genuinely do (evidence, not flattery)

**Real embedded hardware.** This is the strongest thing in the repo and
it's not close.

- You brought a VL53L0X up over I2C on real hardware (2026-07-28) and a
  transistor-driven vibration motor under PWM control (2026-07-30). Both
  phases pass.
- You solved the **GY-53 `PS` pin** problem. This deserves its own
  paragraph: the module has an onboard MCU that defaults to UART mode with
  I2C disabled, and *every single symptom of getting it wrong impersonates
  a wiring fault* — `init()` fails, a bus scan finds nothing, SDA/SCL
  flicker like a loose connection. Beginners lose weeks here or quit and
  blame the sensor. You found it and wrote it down so nobody repeats it.
  That is the actual skill of embedded work.
- You soldered a LiPo pouch to a TP4056 and confirmed charging.
- You spotted that a **stock TP4056 charges a 250mAh cell at 1A (~4C)** and
  correctly called it a safety problem needing an `R3` change. Reading a
  charge rate against a cell's capacity and concluding "this is wrong" is
  electrical engineering judgment, not following a tutorial.

**Parametric CAD.** `enclosure.scad` is genuinely parametric — three
modules driven off one measurement block — and you found a real geometry
bug in it: strap lug tunnels overlapping by 0.4mm and silently merging into
a single slot, which defeated the entire reason the two-slot design was
chosen. It still rendered as valid manifold geometry. Catching a bug that
*passes its own validity check* is a level above catching a crash.

**Sourcing under hard constraints.** No shipping, one city, a fixed budget.
You re-planned the BOM twice (VL53L1X → VL53L0X, 18650 → 502030 pouch) when
reality contradicted the plan, instead of stalling.

**Documentation discipline.** Ten dated session logs that distinguish
"verified in this session" from "inherited, not re-checked." Most
professional engineers do not do this. Keep it — it is rarer and more
valuable than you think.

**Web basics.** HTML/CSS at Algoritmika-course level: flexbox, classes,
semantic tags.

### What you cannot do yet (the honest half)

**You have not written a non-trivial program by yourself.**
`HapticMapper.h`, the 14 unit tests, `haptic_simulator.html`,
`enclosure.scad`, every published artifact — I wrote those. You directed,
reviewed, tested and corrected them, which is real work and builds real
judgment. It does not build the ability to sit in front of an empty file
and produce working code. Those are different skills and only one of them
is on your résumé right now.

**Your one piece of unassisted code has three beginner bugs.** Open
`.HTML`:

1. The filename starts with a dot — on Linux/macOS that makes it a *hidden
   file*, and it has no `index.html` name, so no web server will serve it
   as a page. It should be `index.html`.
2. Line 1 is `html>` — the opening `<` is missing, and there's no
   `<!DOCTYPE html>`.
3. `.info { width: 1100px; }` — fixed pixel width. On a phone this page
   breaks. Every image also carries hardcoded `width`/`height` attributes.

None of these are hard. That's the point: they're the exact gaps that only
close by writing code yourself and having it fail.

**No JavaScript, no Python, no algorithms.** There is no code in this repo
that stores data, loops over a collection, or makes a decision more complex
than a threshold comparison — except in the files I wrote.

**Git workflow.** Your own log flags it four times: *"commits were pushed
correctly but sat invisible because the previous PR had merged and no new
one was opened. Pushing is not delivering."*

---

## Part 2 — The one thing that will decide how far you get

You have been operating as an **engineering director** — deciding what to
build, judging whether it's right, catching errors, managing constraints —
while an AI does the typing. You are unusually good at it for your age.

The risk is specific and worth naming plainly: **directing skill and
building skill look identical from the outside until the moment you're
alone with an empty file.** In a Jugend forscht interview, a technical
school admission, or a paid job, someone will ask you to explain or modify
code on the spot. If the honest answer is "Claude wrote that part," the
whole project's credibility drops — including the parts you genuinely did.

The fix is not to stop working with AI. It's to be **deliberate about which
mode you're in**:

> **The rule: for anything you want to claim as a skill, write the first
> version yourself, badly, before asking for help.** Then ask me to review
> it. You keep the learning *and* the quality. For anything that is a means
> to an end (a build script, a one-off checklist), delegate freely and
> don't feel guilty.

Everything in Phase 1 below assumes you type it.

---

## Part 3 — Phase 0: Finish the wristband (next 4 weeks)

**Do this before starting anything new.** You are roughly 80% done on a
project that is already more impressive than most first-year university
work. An unfinished 80% is worth far less than a finished 100% — for
competitions, for admissions, and for your own sense of whether you finish
things.

Four things stand between you and a working device:

| # | Task | Why it's blocking | Est. |
|---|---|---|---|
| 1 | **`R3` rework on the TP4056** (2000 тг, ~30 min, shop quoted) | Safety. 4C into a 250mAh pouch. Do not run the device on battery until this is done. | 1 afternoon |
| 2 | **Flash `obstacle_haptic.ino`** | It has *never been flashed*. Sensor and motor each work alone; combined firmware is unproven. | 1 evening |
| 3 | **Caliper-measure parts → update `enclosure.scad`** | Every dimension in `[MEASURE YOUR PARTS]` is still a guess. Print the `switch_test_coupon` first. | 2 evenings |
| 4 | **Send the outreach emails** | Longest lead time in the project, drafted since July, still unsent. Fill the `[PLATZHALTER]` fields, get a parent to co-sign, send. | 30 minutes |

**Task 4 is the one to do tonight.** It costs half an hour, it's been
blocked on nothing but sending, and everything downstream (the feedback
session, the ethical basis for presenting this at all, the writeup) waits on
a reply that hasn't started arriving yet. The README is right that this is
non-optional — a device for low-vision users, validated only by a sighted
person wearing a blindfold, cannot honestly be presented as what it claims
to be.

---

## Part 4 — Phase 1: Learn to write code unaided (months 1–4)

Goal: **go from "I can review code" to "I can write code."** One language,
typed by you, until it's boring.

### Which language: C++ first, then Python

Not the usual advice, and here's why it's right *for you specifically*:
you already have a working C++ codebase you understand the purpose of, a
test suite that tells you instantly whether you broke something, and real
hardware that makes the code do something physical. That is a far better
learning environment than a generic Python tutorial about a fictional
to-do list. Use it.

### The exercise ladder (do these in order, typed by you)

Each one is small. Each one has a definition of done you can check
yourself. Do not ask me for the code — ask me to *review* it after.

**Rung 1 — read and modify what exists.**
1. Change `kFarThresholdMm` in `HapticMapper.h` to 800mm. Run
   `firmware/tests/run_tests.sh`. Watch tests fail. Understand *which*
   ones and why. Change it back.
2. Add a fifth zone (e.g. "very far," 1000–1400mm, a very slow pulse).
   Write the test for it **first**, watch it fail, then make it pass.
   *Done when: 15+/15+ tests pass and you can explain every line you added.*

**Rung 2 — the missing safety feature, written by you.**
3. The README names a real gap: a sensor fault currently produces silence,
   indistinguishable from "nothing ahead." Implement a distinct
   **fault pattern** (e.g. three rapid pulses, pause, repeat). Test-first.
   *Done when: unplugging the sensor produces a pattern you can feel and
   distinguish from every proximity zone.*

This one matters — it's a genuine safety improvement to a real device, it's
yours, and it's a good story in an interview.

**Rung 3 — leave the nest.**
4. Fix `.HTML`: rename to `index.html`, add the doctype, fix line 1,
   replace `width: 1100px` with something fluid (`max-width` + `flex-wrap`,
   which you already use), drop the hardcoded image dimensions.
   *Done when: it looks right on your phone.*
5. Add JavaScript to it for the first time — make the "Скидки" button
   actually filter the article cards. ~20 lines. Your first real JS.

**Rung 4 — build something from an empty file.**
6. A serial-plotter web page: Arduino prints distance over USB serial, a
   browser page reads it via Web Serial API and draws a live graph.
   *Done when: you wave your hand at the sensor and see the line move.*

Rung 4 is the graduation exercise. When you can do that, you can write
code.

### Alongside: fix the git habit permanently

Your log flags it four times, so it's a system problem, not a memory
problem. Adopt one rule:

> **Never push without immediately checking whether an open PR exists for
> the branch. If not, open one. Work isn't delivered until it's visible.**

Consider adding it to `CLAUDE.md` as a standing instruction so it survives
into future sessions.

---

## Part 5 — Phase 2: Pick a depth (months 4–12)

By month 4 you'll have finished a device and can write code. Now specialize.
Two honest paths — the evidence in this repo points hard at the first.

### Path A — Embedded / hardware (recommended)

You have unusual momentum here, and the field is far less crowded than web
development. Most people who "learn to code" never touch a soldering iron.

Progression:
1. **Graduate the Nano** → ESP32 (WiFi/Bluetooth, far more capable, cheap
   and available in Almaty).
2. **Learn to read a datasheet properly** — not just pinouts. Timing
   diagrams, electrical characteristics, absolute maximum ratings. The
   TP4056 `R3` insight was you doing this instinctively; do it deliberately.
3. **KiCad** — move from breadboard to a real PCB. Getting a board
   manufactured and having it work is a milestone that changes how people
   see your work.
4. **Second device, harder**: something with wireless, a display, or
   multiple sensors. Design it so the firmware is testable on a desktop
   like `HapticMapper.h` is — that architecture choice was correct and you
   should repeat it.

### Path B — Software / web

If you find you prefer screens to soldering: JavaScript → TypeScript →
React → a backend (Node or Python) → databases → deployment. Build things
people actually use. Faster to earn from (see Part 7), more competition.

**You don't have to choose today.** Rung 4's serial-plotter project sits
exactly on the boundary. Notice which half you enjoy more, and let that
decide.

---

## Part 6 — Phase 3: Turn work into leverage (months 6–18)

- **Jugend forscht / Schüler experimentieren.** The wristband is a strong
  entry *if* it's finished, honestly scoped, and validated with real
  low-vision feedback. Your README's ethical framing is genuinely a
  competitive advantage: judges respond well to a project that states its
  own limitations precisely. Find the German-school deadline early.
- **Clean up your GitHub.** It is your résumé. Rename `automatic-dollop2`
  to something meaningful. Write a repo-root README explaining what the
  wristband is. Fix or delete the stray root files.
- **Write the build up publicly** — the GY-53 `PS` discovery alone is worth
  a post. People search for that exact symptom and find nothing. Publish in
  English; it's the best-indexed language for that search.
- **Keep every session log.** In two years this is a documented, dated
  record of your engineering growth. Almost no student has that.

---

## Part 7 — Short-term money

You asked for this specifically, so here it is in full — and it starts with
the part most advice skips.

### First: the honest framing

**Programming does not pay quickly at the start.** Anyone promising a
teenager a remote dev job in three months is selling something. Realistic
timeline from your current level to paid programming work is roughly 12–24
months of steady building.

But that is not the same as "you can't earn money now." **You already have
scarce, sellable skills — they're just not the ones you're thinking of.**
You can solder, read a circuit, model parts in CAD, and debug hardware
patiently. Very few people in any city can do all four. That is what to
sell in the short term.

Also worth knowing before you start: **your repo already contains a real
market rate.** A repair shop quoted **2000 тг for ~30 minutes** of SMD
rework on the TP4056. That's roughly **4000 тг/hour for exactly the class
of skill you're building.** Remember that number — it's your pricing anchor
and it's better evidence than anything I could look up.

### The rules that apply to you (Kazakhstan, school student)

Check these against your own situation with a parent — they change what's
available:

- **Employment:** a labour contract can normally be signed from **16**.
  From **14–15**, an employment contract is possible with the **written
  consent of a parent or guardian**, for light work outside school hours
  that doesn't harm health or interfere with study. Hour caps apply: **24
  h/week for 14–16**, **36 h/week for 16–18**.
- **Getting paid:** from **16** you can open your own Kaspi Gold in the
  Kaspi.kz app. **Under 16**, it's a Kaspi Junior card attached to a
  parent's account — meaning **a parent has to be involved in receiving
  money**, so bring them in from the start rather than after the first
  payment arrives.
- **Freelance platforms:** **Upwork is 18+ with no parental-consent
  exception** — don't build a plan around it. **Fiverr allows under-18s
  only through an account owned and supervised by a parent or guardian.**
  Faking your age gets accounts and earnings frozen, so don't.

*(Sources listed at the end. Rules change — verify before acting.)*

### Tier 1 — money this month, with skills you have today

**1. Tutoring — the highest hourly rate available to you, with zero capital.**

You went through Algoritmika. That means you can teach exactly what it
teaches — Scratch, HTML/CSS basics — to kids two to five years younger.
Tutoring pays better per hour than almost anything else a student can do,
needs no equipment, and is completely legal at your age with a parent
handling payment.

How to get the first three students in a week:
- Ask your school — a German-language school with younger grades is full of
  parents who want their kids in extra tech classes.
- Ask the Algoritmika branch you attended whether they need a teaching
  assistant. Former students are exactly who they hire.
- Your building's and your parents' Telegram/WhatsApp chats. In Kazakhstan
  these are how local services actually get found — far more effective than
  a website.
- Price by checking what local tutoring centres charge per hour, then
  starting at roughly half. Raise after three students.

**2. Electronics repair and soldering micro-jobs.**

You own a soldering iron, a multimeter, and — as of last month — real
practice. Start with through-hole and mechanical work, which is where the
volume is and where you can't do much damage: headphone jacks, broken
charging cables, LED strips, loose connectors, replacing switches, battery
swaps in cheap devices.

- **Price anchor: that 2000 тг / 30 min quote.** Charge less while you're
  learning, and be straightforward that you're a student — people accept a
  lower rate for that and it sets expectations honestly.
- **Never take a job you can't afford to replace.** Not phones, not
  laptops, not anything irreplaceable, until you're much more experienced.
  A destroyed device you must pay for wipes out weeks of earnings.
- Find work through the same channels as tutoring, plus OLX.

**3. CAD / 3D-print design.**

You can write parametric OpenSCAD. Most people who own a 3D printer
**cannot model** — they only download and print existing files. That's the
gap you sell into: custom brackets, replacement knobs, phone stands, mounts
for specific devices.

Approach a local print shop or a maker with a printer and offer a split:
you design, they print, you share the fee. Or charge design-only and let
the customer print.

**4. The one only you can sell: Almaty electronics sourcing.**

This is the most interesting option in this list and it comes straight out
of your own session logs. **You have twice concluded a part was unavailable
in Almaty when a shop had a drawer full of them.** Catalogue searches fail
here; small passives, switches and connectors are routinely uncatalogued;
the answer is asking at a counter.

That means you now hold knowledge almost nobody has written down: which
Almaty shops actually stock what, what things really cost, and which
catalogue listings are fiction. Every student, hobbyist and Jugend
forscht entrant in this city hits the same wall you did.

Sell it as: a sourcing run (someone sends a parts list, you shop and mark
up your time), or simply publish the guide free and let it become your
reputation. Free may be worth more than the fee — it makes you the person
locals ask, and that's how the paid work finds you.

### Tier 2 — money in 2–4 months, with a little more building

**5. One-page websites for small local businesses.** You can nearly do this
today — but finish Rung 3 first. A site that breaks on a phone can't be
sold, and `width: 1100px` breaks on every phone. Target: barbers, cafés,
tutors, small repair shops. Charge a flat fee per site, plus a small
maintenance fee for updates.

**6. Sell the wristband build as content.** Not the device — the *writeup*.
A well-documented build with real photos, the GY-53 discovery, and honest
failure modes is the kind of thing that gets attention, and attention
converts into commissions and referrals. Slower, compounding, and it
doubles as your competition portfolio.

### What to skip

- **Upwork/Toptal** — 18+, no exceptions.
- **Crypto, trading, dropshipping, "passive income"** — the ones aimed at
  teenagers are close to universally scams.
- **Free "portfolio" work for strangers** — do free work only for people
  you know, or for something you'd have built anyway.
- **Anything asking you to pay upfront** for training, equipment, or
  "registration." That's the single most common scam aimed at young people
  in local job chats. Real work pays *you*.

Two more safety rules: **take a deposit** (30–50%) for any job requiring
you to buy parts, and **meet clients in public places** — a café, the
shop, your school — never alone at a stranger's home. Tell a parent where
you're going. This is normal practice, not paranoia.

### The tradeoff, stated plainly

Every hour earning money now is an hour not spent building skills that will
earn far more later. At your age the compounding return on skill is
genuinely enormous, and the wristband is worth more to your future than
several months of repair jobs.

**Suggested cap: 5–8 hours a week on money work.** Enough for real income
and real experience with customers — which is itself a skill worth having —
without stalling Phase 0 and Phase 1.

And prefer the money work that *teaches*: repair work makes you better at
hardware, tutoring makes you better at explaining, and both feed directly
back into the roadmap. Reselling phone cases doesn't.

---

## Part 8 — Rules you already discovered (keep them)

These are yours, from your own logs. They're good enough to keep for a
career:

1. **"Ask at the counter before trusting any catalogue search, including
   mine."** Reality beats documentation. You learned this twice.
2. **"Pushing is not delivering."** Work isn't done until it's visible to
   the person who needs it.
3. **Bring up one part at a time.** `tutorial.md`'s whole structure. It's
   why you found the `PS` pin instead of drowning in six simultaneous
   unknowns.
4. **Separate logic from hardware.** `HapticMapper.h` has zero Arduino
   dependencies, so it's testable on a desktop and reusable in a browser
   simulator. That's a professional-grade architecture decision — repeat it.
5. **Write down what's verified vs. assumed.** Your session logs already
   do this. Most engineers never learn to.
6. **Don't overclaim to vulnerable users.** The README's opening constraint
   is the most mature thing in this repo.

---

## Part 9 — This week

Small, ordered, all finishable:

- [ ] **Tonight:** fill in the `[PLATZHALTER]` fields in
      `outreach/outreach_email_schule.md`, have a parent co-sign, **send
      both outreach emails.** 30 minutes, unblocks a month of waiting.
- [ ] **This week:** book the `R3` rework (2000 тг). Don't run on battery
      until it's done.
- [ ] **This week:** flash `obstacle_haptic.ino` for the first time.
- [ ] **This weekend:** Rung 1, exercises 1–2 — typed by you, not by me.
- [ ] **This weekend:** talk to a parent about the money plan — which Tier
      1 option fits, and how you'd get paid.
- [ ] **Ongoing:** before every `git push`, check whether an open PR exists.

---

## Sources

Rules cited in Part 7, verified 2026-08-11 — these change, so re-check
before relying on them:

- [Employment of students during the summer vacation — eGov.kz](https://egov.kz/cms/en/articles/work4students)
- [Labour Code of the Republic of Kazakhstan — Adilet LIS](https://www.adilet.zan.kz/eng/docs/K070000251_)
- [Kaspi Гид — Kaspi Gold for a child, age conditions](https://guide.kaspi.kz/client/ru/gold_for_parent/conditions/q14902)
- [Fiverr Help Center — Navigating Fiverr as a minor](https://help.fiverr.com/hc/en-us/articles/32567580782609-Navigating-Fiverr-as-a-minor)
- [Upwork/Fiverr/Toptal age requirements — FreelanceMVP](https://freelancemvp.com/are-you-old-enough-to-freelance/)
