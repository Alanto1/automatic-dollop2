# motion/ — making it move like a creature

```bash
open leg_simulator.html      # or double-click it
```

No hardware. One of Sesame's 2-DOF legs, drawn twice: **left** goes straight
to the target the way naive servo code does, **right** uses the motion engine.
Same target, same duration. Click **lunge** and watch them.

This is the highest-impact week in the plan and it costs nothing but an
afternoon in a browser. A robot that snaps between poses reads as a 3D print
that twitches; the same robot with eased motion reads as alive. Nothing else
in the project changes that perception as cheaply.

## What to try, in order

1. **Click `lunge`.** Watch the plot at the bottom, not just the legs. The
   red line is a straight ramp; the teal one leans out of rest, accelerates,
   and settles. That shape is the entire difference.
2. **Turn off `breathing`.** The robot dies instantly. ±2.5° at 0.2 Hz is all
   it takes — a robot that is perfectly still between commands reads as
   switched off.
3. **Turn off `anticipation`.** Subtler, and worth understanding: winding up
   ~7° *backwards* before a lunge reads as intent. Cats do it.
4. **Turn off `follow-through`.** Now it stops dead on the target. Mass
   doesn't do that.
5. **Drag `MOTION_HZ` down to 10.** The smooth leg turns ugly. This is the
   number that decides whether the ESP32 can actually deliver any of this,
   and it is why the motion engine runs there and not on the Pi — the Pi is
   busy doing YOLO at 1–2 FPS.
6. **Set `JITTER` to 0**, then click `auto-cycle`. Eight joints moving in
   perfect lockstep is the loudest "this is a machine" tell there is.

## Then port it

The bottom panel prints the constants as a C header. Copy it into the Sesame
firmware.

⚠️ **The warning in that panel is real.** Sesame staggers its servo writes by
20 ms to limit inrush current. At 40 Hz you have 25 ms per frame for all
eight joints, so the stagger cannot survive — the two are incompatible by
construction. Fit **1000 µF+ across the servo rail** and characterise the
brown-out *before* removing the stagger. That is Week 3 in
`BUILD_CHECKLIST.md`, and the capacitors are already in the parts list.

Design rationale: README, "Making it move like a creature".
