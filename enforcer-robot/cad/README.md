# CAD — the Enforcer add-on parts

**The body is not here.** Sesame supplies the chassis, legs, covers and face
mount — 11 printed parts, in
[its repo](https://github.com/dorianborian/sesame-robot/tree/main/hardware).
Print those from upstream.

What's here is what Sesame doesn't have, because it was never meant to carry
water: a **payload deck** that straps to its top cover, and the Enforcer
hardware that bolts to the deck.

Nothing here modifies a Sesame part. Its build guide stays valid, and you
never have to re-print an upstream component when your own design changes.

| Part | Qty | What it does |
|---|---|---|
| `payload_deck` | 1 | Straps to Sesame's top cover. 5×3 M3 grid at 12mm pitch |
| `reservoir_cradle` | 2 | Bottle drops in from above, zip-ties down |
| `nozzle_mount` | 1 | Aims the tubing forward and slightly down |
| `cliff_bracket` | 4 | Holds a TCRT5000 facing down past the deck edge |
| `phone_tray` | 1 | Warden mode, with a lip at each end |

```sh
python3 make_stl.py --test    # geometry self-tests only
python3 make_stl.py           # regenerate stl/
```

Standard library only — no numpy, no CAD kernel — so it runs anywhere. It
refuses to write an STL whose geometry fails the self-tests, and every solid
is checked watertight before it's written.

---

## ⚠️ Before you print: measure your Sesame

`DECK_L` and `DECK_W` at the top of `make_stl.py` default to **90 × 60 mm**,
which is an *estimate* of Sesame's top cover. **It has not been verified
against a real build.**

Measure your printed top cover, set those two constants, and regenerate.
Everything else is derived from them, so the deck is the only part that
depends on an upstream dimension — one unknown to get right instead of ten.

Same applies to `BOTTLE_D` (default 36mm). Measure the bottle you actually
bought.

## Why a deck at all

Sesame's own assembly uses zip ties and underside cable channels, so strapping
a deck to it matches how the robot already goes together, and needs no screws
into upstream parts. The alternative — bolting brackets directly onto Sesame's
covers — means editing its CAD, re-printing its parts, and losing the ability
to take upstream fixes. The deck is one part; a fork is forever.

The M3 grid exists so the reservoir can **move fore and aft** after you weigh
the robot. Balance point is something you measure on the real thing, not
something you predict.

## Print settings

PLA or PETG, 0.2mm layers, **4 perimeters**, 40–60% infill. The deck carries a
water bottle on a walking robot; a 2-perimeter/15% profile will flex.

Print the **payload deck first, on its own**, and check it actually straps to
your Sesame before printing anything else. Everything downstream assumes it
fits.

## Weight budget — read this before choosing a bottle

Water is 1 g/ml. The self-test reports the fill weight for your `BOTTLE_D`:
the 36mm default over 60mm of fill is **61g**.

Sesame is a small robot on 8 MG90S servos and an 800mAh pack. 61g of water
plus the deck plus the pump is a real fraction of its payload. **Weigh your
build and walk it with a full reservoir in week 3** — before you commit to
plumbing. `BUILD_CHECKLIST.md` has this as an explicit step, and the scope
ladder in `README.md` has the answer if it fails: Squirt mode goes stationary,
which is still a complete project.

## Known gaps

Honest list, so nothing is a surprise:

- **Deck dimensions unverified** against a real Sesame — see above.
- **No pump bracket.** Depends on which pump you get: the submersible one in
  `PURCHASE_LIST.md` sits *inside* the bottle and needs no bracket at all;
  a self-priming one would.
- **The cliff brackets assume a bare TCRT5000** (10.6 × 6.2mm). Breakout
  boards with the comparator on them are bigger — measure yours and set
  `TCRT_W` / `TCRT_H`.
- **No strain relief** modelled. Moving legs eat wires; plan it before the
  one-hour endurance run.
