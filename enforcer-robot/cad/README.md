# CAD — The Enforcer

Printable parts for the 12-servo quadruped, dimensioned around the **MG90S**
servo. Everything here is generated; nothing is hand-drawn.

| File | What it is |
|---|---|
| `SKETCH.svg` | Dimensioned top / leg / front views |
| `stl/*.stl` | Ready to slice |
| `enforcer.scad` | Parametric OpenSCAD source — edit dimensions here |
| `make_stl.py` | Generates the STLs without OpenSCAD installed |
| `make_sketch.py` | Generates `SKETCH.svg` from the same constants |

```sh
python3 make_stl.py --test    # geometry self-tests only
python3 make_stl.py           # regenerate stl/
python3 make_sketch.py        # regenerate SKETCH.svg
```

`make_stl.py` needs **only the Python standard library** — no numpy, no CAD
kernel — so it runs anywhere, including on a laptop you haven't set up yet.
It refuses to write an STL whose geometry fails the self-tests.

## Print list

| Part | Qty | Notes |
|---|---|---|
| `chassis_plate` | 1 | 130 × 95 × 3 mm. The one part that needs a bed ≥ 140 mm |
| `coxa_bracket` | 4 | L-shaped; print with the wall flat on the bed |
| `femur` | 4 | |
| `tibia` | 4 | |
| `face_bezel` | 1 | Window sized for a ~1.3" rectangular SPI display |

`assembly_preview.stl` is the whole posed robot — **for looking at, not for
printing.** Open it to check the stance before you commit to a print.

Print **one leg's worth first** (1 coxa bracket, 1 femur, 1 tibia) and test-fit
a real servo before running the other three. A pocket that's 0.3 mm tight
costs you one part to discover and four parts to ignore.

## Suggested print settings

PLA or PETG, 0.2 mm layers, **4 perimeters**, 40–60% infill. These are
structural parts under servo torque; the usual 2-perimeter/15% profile will
flex at the joints and your gait tuning will chase a problem that is really
just a bendy femur.

The servo pockets carry **0.6 mm total clearance** (`FIT` in `make_stl.py`).
If your printer runs tight, raise it to 0.8 and regenerate rather than filing
the parts.

## The numbers that matter elsewhere

These three link lengths are the robot's kinematics. **The leg-IK simulator
must use exactly these**, or the sim will lie to you:

| | mm |
|---|---|
| Coxa — vertical hip axis to femur axis | 28 |
| Femur — femur axis to knee axis | 50 |
| Tibia — knee axis to foot tip | 55 |
| Design ride height | 70 |

Standing pose comes out at **femur 31° below horizontal, knee folded 95°**,
using 71 mm of the leg's 105 mm reach. That margin is deliberate: a leg
standing at full stretch has no travel left to lift with, and the gait needs
both directions. `make_stl.py` has `leg_ik()` and `leg_fk()` already written
and round-trip tested — port them, don't rewrite them.

## Assembly order

1. **Centre every servo before bolting on a single horn.** Drive all 12 to
   90° first. Skip this and you will fight offsets for the rest of the build.
2. Coxa servos drop through the chassis plate from below, flanges on top.
3. `coxa_bracket` bolts to the coxa horn; the femur servo sits in its wall.
4. `femur` bolts to the femur horn; the knee servo sits in its far pocket.
5. `tibia` bolts to the knee horn.
6. Repeat ×4, then record each servo's real min/max/centre in one config file.

## Known simplifications

Honest list of what this geometry does *not* yet include, so nothing is a
surprise at assembly:

- **No pan/tilt head mount.** The camera + nozzle head is still a bought
  bracket in `PARTS.md`; only the face bezel is modelled.
- **No cliff-sensor mounts.** Four TCRT5000s need small brackets under the
  plate corners — add once you have the sensors and can measure them.
- **No reservoir or pump mount.** Depends on which pump arrives; the
  submersible one sits *inside* the bottle, which changes the bracket.
- **No cable management.** Two pass-through slots exist; moving legs eat
  wires, so plan strain relief before the one-hour endurance run.
