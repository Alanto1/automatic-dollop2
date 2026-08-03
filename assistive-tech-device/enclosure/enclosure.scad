// enclosure.scad
//
// Parametric OpenSCAD enclosure for the obstacle-detection wristband pod.
//
// Render-verified headlessly (openscad CLI, 2021.01) on 2026-07-25: base,
// lid, and belt_clip_back all export as valid manifold geometry ("Simple:
// yes") with no warnings, and preview renders look like a sane hinged
// box + lid + clip. That confirms the CSG is well-formed - it does NOT
// confirm fit, since every dimension in the "[MEASURE YOUR PARTS]" block
// below is still a guess, not a caliper measurement. Re-render after
// updating that block, and before printing anything for real.
//
// Orientation convention used throughout this file:
//   X axis - the long axis of the pod, aligned with the wristband strap's
//            direction of travel around the wrist. The two strap lugs
//            (tunnels) sit near the two X ends of the pod.
//   Y axis - each lug's tunnel bore runs along Y, across the pod - like a
//            watch's spring-bar tunnel, perpendicular to the strap's
//            overall direction of travel. This is the "front/back, like
//            watch lugs" mount from the project handoff: a single-slot
//            design (one tunnel, strap folded back through it) was
//            considered and rejected because it would let the pod pivot
//            around that one wrap point instead of sitting flat.
//   Z axis - up. The lid (+Z) lifts off the top, away from the skin; a
//            seam on the underside would press into the wrist. The base
//            (-Z) sits against the arm.
//
// Face assignments, all on the base:
//   -X front  : sensor window, looking in the direction of travel
//   +X back   : power switch slot
//   +Y flank  : both USB openings, stacked vertically
//   both Y    : strap tunnels bore through here
//
// Which part to render: set `part` below, or override from the command
// line, e.g.:
//   openscad -D 'part="base"' -o base.stl enclosure.scad

part = "all";  // "base" | "lid" | "wristband_back" | "belt_clip_back" | "all"

// ============================================================
// [MEASURE YOUR PARTS] -- every value below is a PLACEHOLDER,
// guessed from typical part sizes, not measured. Update these
// from real calipers before printing anything for real - see
// BUILD_CHECKLIST.md / PURCHASE_LIST.md for sourcing calipers.
// ============================================================

nano_length       = 45;  // Arduino Nano clone, long edge
nano_width        = 18;  // short edge
nano_stack_height = 8;   // PCB + header pins + USB-C connector, stacked

tof_length       = 14;  // VL53L0X breakout board (e.g. GY-53) - see
tof_width        = 8;   // PURCHASE_LIST.md, no walk-in Almaty store had a
tof_stack_height = 4;   // VL53L1X in stock as of this writing
tof_window_dia   = 5;   // clear aperture needed in front of the sensor lens

motor_dia       = 10;  // vibration motor (10x3mm "pancake" type)
motor_thickness = 3;

// LiPo pouch cell dimensions - sized for the 502030 flat pouch cell
// confirmed on Kaspi.kz (3.7V, 250mAh, nominal 5x20x30mm size code =
// thickness x width x length; see PURCHASE_LIST.md's battery note for the
// link). The walk-in-confirmed alternative, an 18650 cylindrical cell
// (18mm dia x 65mm long), is a different shape entirely and won't fit
// this rectangular cavity - that battery needs a real redesign (a
// cylindrical bay), not just new numbers here. Still confirm with real
// calipers once a part is in hand - pouch cells commonly run a little
// oversize versus their nominal code, and the connector/leads need their
// own clearance beyond this cavity.
battery_length    = 30;  // LiPo pouch cell (502030: 5x20x30mm nominal)
battery_width     = 20;
battery_thickness = 5;

strap_width     = 20;  // wristband strap
strap_thickness = 3;

// Power switch - a small PCB-mount SLIDE switch (the ~50 тг counter part,
// not the panel-mount MTS-101 toggle that was the earlier plan). That
// choice matters here: a panel-mount toggle would need only a round hole
// and its own nut would hold it. A slide switch has no threaded bushing,
// so the shell needs a SLOT for the actuator to poke through, and the
// switch body has to be held from inside - glue, or a scrap of perfboard
// glued to the wall. Nothing below secures the body; that's assembly work.
//
// ALL FIVE NUMBERS ARE PLACEHOLDERS. Measure the real switch with
// calipers before printing - see this file's header. The slot is the one
// cutout where being 1mm out is immediately obvious: too tight and the
// slider won't travel, too loose and it rattles or lets dust in.
// MEASURED 2026-08-02: switch body including solder, 10.8 x 2.85 x 3.2mm.
switch_body_length    = 10.8;  // along the slider's travel
switch_body_width     = 2.85;
switch_body_height    = 3.2;
switch_actuator_length = 3;   // the nub itself - still a placeholder
switch_actuator_width  = 2;   // across
// How far the actuator has to stand proud of the outer shell surface to
// be usable with a fingernail. Too flush and you can't work it; too proud
// and it snags, which was the whole reason for preferring a slide switch.
switch_actuator_proud  = 1.2;
// Slot is sized to the actuator's full travel, not just its width: the
// nub sweeps the length of the slot, so the opening must be at least the
// actuator plus the throw, plus clearance at each end.
switch_travel          = 2.5;  // total slider throw end to end

// USB access - TWO openings are needed, and forgetting either one seals
// the pod shut for a whole workflow:
//
//   * TP4056's USB-C     -> charging. Without it the battery can only be
//                           charged by opening the enclosure.
//   * Nano's mini-USB    -> reflashing AND serial debugging. The debug
//                           workflow is: switch OFF (isolating the
//                           battery), plug in USB, read the serial
//                           monitor. That is the only way to diagnose a
//                           fault in an assembled device, and it needs
//                           this port reachable.
//
// LAYOUT CONSTRAINT this imposes: both boards must be oriented so their
// USB connectors face the SAME long side (+Y). Both 30mm end faces are
// spoken for - sensor at the front, switch at the back - so the ports go
// on a flank. Decide this when arranging the stack; it is painful to fix
// after gluing.
//
// MEASURED 2026-08-02.
usb_charge_width  = 8.86;  // TP4056 Type-C receptacle, across
usb_charge_height = 4.14;
usb_data_width    = 7.5;   // Nano mini-USB receptacle, across
usb_data_height   = 6.33;
// STILL PLACEHOLDERS: how far each connector's centre sits above the
// inside floor. With the boards stacked in a 50mm-tall box these depend
// entirely on where each board ends up, so they must be set once the
// stack is arranged. Getting these wrong is the failure mode where the
// opening is the right SIZE but the wrong HEIGHT, and the plug still
// won't reach.
usb_charge_z      = 12;
usb_data_z        = 26;
// 0.5mm all round, per the builder's call. A 3D printer typically
// overshoots into a hole by 0.1-0.3mm on its own, so the 0.1mm originally
// proposed would often have come out negative - the plug simply wouldn't
// enter. 0.5mm stays snug while actually fitting.
usb_clearance     = 0.5;
switch_clearance  = 0.5;

// Sensor window - in the FRONT WALL (-X), not the lid.
//
// It was in the lid originally, pointing up out of the top face. Moved
// here because the front is the direction of travel: a wrist-worn pod
// wants to see what you are about to walk into, not the sky. This is the
// change that makes the device's aim match its purpose.
//
// The two apertures on the VL53L0X - emitter and receiver - must BOTH sit
// inside this opening, and nothing transparent may cover it. A window
// over the sensor reflects the emitter straight back into the receiver
// and it reads a permanent obstacle a few centimetres away.
sensor_window_dia = 6;   // wider than the chip's 4.4mm so the 25 degree
                         // field of view isn't clipped by a setback
sensor_window_z   = 38;  // PLACEHOLDER - height of the sensor's centre
                         // above the inside floor, set once mounted

// ============================================================
// Derived / design parameters -- reasonable defaults, less
// urgent to re-measure than the block above, but still worth
// checking once parts are in hand.
// ============================================================

wall_thickness    = 2.2;   // ~3-4 perimeters at a typical 0.4mm nozzle
fit_clearance     = 0.6;   // extra room around each component - not a press fit
lid_lip_height    = 3;     // how far the lid's inner lip plugs into the base
lid_lip_clearance = 0.25;  // friction-fit gap - tune per printer/material
corner_radius     = 2.5;   // cosmetic, and softens stress concentration/print artifacts

strap_slot_width  = strap_width + 1.5;   // strap needs to slide through freely
strap_slot_height = strap_thickness + 2;
strap_slot_inset  = 4;  // how far each lug tunnel sits in from the pod's X ends
// Minimum solid material left between the two lug tunnels. Without this
// the two slots can overlap and silently merge into one long opening -
// which is exactly the single-slot design this enclosure rejected, since
// one wrap point lets the pod pivot instead of sitting flat. See the
// outer_length calculation below, which grows the pod if needed to keep
// this web intact.
strap_web = 3;

belt_clip_arm_length = 35;
belt_clip_gap        = 6;    // fits a typical belt/waistband strap
belt_clip_thickness  = 2.5;


// ============================================================
// [MEASURE THE BUNDLE] -- the easier way to size the cavity.
// ============================================================
//
// Once everything is soldered together it stops being separate components
// and becomes one awkward bundle of boards and wire. Measuring each part
// individually then becomes both difficult and beside the point: what has
// to fit in the pod is the whole assembly, wires included, not a tidy sum
// of datasheet dimensions.
//
// So there are two ways to size the cavity, and the second is usually
// easier once you've soldered:
//
//   1. Leave these at 0. The cavity is derived from the individual part
//      dimensions in the [MEASURE YOUR PARTS] block above.
//
//   2. Set them to real numbers. Arrange the soldered assembly exactly as
//      it will sit inside the pod - boards flat, battery beside or under
//      them, wires folded where they'll actually go - then measure the
//      overall block it occupies. Length, width, height of that. Those
//      three numbers replace the derived ones, and fit_clearance is added
//      on top, so measure the bundle relaxed rather than squeezed.
//
// Option 2 is more honest about what actually determines the fit, because
// the folded wire between two boards is often thicker than either board.
// CURRENT VALUES ARE A TARGET, NOT A MEASUREMENT. The assembled bundle
// measured roughly 110 x 75 x 46mm loose - about 30x the volume of the
// components inside it, i.e. almost entirely air and unfolded wire. These
// numbers are a deliberate midpoint between that and the ~60 x 45 x 18mm
// the parts could theoretically pack into: large enough to be reachable
// by folding and bundling the wire, small enough to still be wearable.
// Replace them with a real measurement once the bundle is compacted.
measured_bundle_length = 75;  // 0 = derive from the parts block above
measured_bundle_width  = 50;
measured_bundle_height = 25;

// Internal cavity. When the bundle hasn't been measured, this falls back
// to fitting the tallest component with everything else assumed to sit
// beside it on the floor of the base - a simplified layout, not a
// precision placement.
internal_length = measured_bundle_length > 0
    ? measured_bundle_length + fit_clearance * 2
    : max(nano_length, battery_length) + fit_clearance * 2;

internal_width = measured_bundle_width > 0
    ? measured_bundle_width + fit_clearance * 2
    : nano_width + tof_width + fit_clearance * 3;

internal_height = measured_bundle_height > 0
    ? measured_bundle_height + fit_clearance * 2
    : max(nano_stack_height, tof_stack_height, motor_thickness, battery_thickness)
        + fit_clearance * 2;

// The pod has to be long enough for BOTH the components inside it and the
// two strap tunnels side by side. Sizing it only from the components (the
// obvious approach, and what this file did originally) let the two slots
// overlap by a fraction of a millimetre at the default dimensions and
// merge into a single opening - a silent failure, since it still rendered
// as valid geometry. Taking the max of the two requirements makes the pod
// grow instead.
// Direct outer-size override. Set these when you've decided the box's
// external dimensions rather than deriving them from what's inside -
// which is what happens once you've sketched a box and want it built to
// that size. 0 = derive as before.
box_outer_length = 67;
box_outer_width  = 30;
box_outer_height = 50;

outer_length_from_parts = internal_length + wall_thickness * 2;
outer_length_for_straps = strap_slot_inset * 2 + strap_slot_width * 2 + strap_web;
outer_length = box_outer_length > 0
    ? box_outer_length
    : max(outer_length_from_parts, outer_length_for_straps);

outer_width  = box_outer_width  > 0 ? box_outer_width  : internal_width + wall_thickness * 2;
outer_height = box_outer_height > 0 ? box_outer_height : internal_height + wall_thickness + lid_lip_height;

assert(outer_length >= outer_length_for_straps,
       "Pod too short for two strap tunnels - they would merge into one slot.");

// Switch slot, cut into the +X END wall - the short face at the far end
// from the sensor.
//
// It started on a long side wall, which was wrong: the strap tunnels bore
// straight through both long walls, so a side slot lands inside an
// existing opening and cuts nothing. The end walls are the only faces the
// strap tunnels don't touch. Putting it at the end opposite the sensor
// also means a finger reaching for the switch never passes in front of
// the sensor window.
//
// The slider therefore travels along Y (across the wrist) rather than
// along the strap. Measure your switch accordingly.
//
// Must stay BELOW the outer_* block: it depends on outer_width, and
// OpenSCAD evaluates file-scope assignments in order, so referencing that
// earlier silently yields undef and the slot never gets cut.
switch_slot_length = switch_actuator_length + switch_travel + switch_clearance * 2;
switch_slot_width  = switch_actuator_width + switch_clearance * 2;
switch_slot_y      = (outer_width - switch_slot_length) / 2;  // centred across the end face
switch_slot_z      = 8;  // PLACEHOLDER - height of the actuator's centre
                         // above the inside floor, set once mounted

assert(switch_slot_length + wall_thickness * 2 <= outer_width,
       "Switch actuator slot is wider than the pod's end face.");
assert(switch_slot_z + switch_slot_width / 2 <= outer_height - lid_lip_height,
       "Switch slot runs past the top of the base and into the lid seam.");

// USB openings moved to the +Y LONG SIDE. Both 30mm end faces are now
// spoken for - sensor at the front, switch at the back - so the ports go
// on a flank. They sit at different heights because the boards they
// belong to are at different levels in the stack.
usb_charge_w = usb_charge_width + usb_clearance;
usb_charge_h = usb_charge_height + usb_clearance;
usb_data_w   = usb_data_width + usb_clearance;
usb_data_h   = usb_data_height + usb_clearance;

// Placed in the solid web BETWEEN the two strap tunnels, which bore
// straight through this wall. Landing a port inside a tunnel would cut
// nothing - the same mistake the switch slot made before it moved to an
// end face.
//
// Side by side they don't fit: the two openings need about 20mm of web
// and there is only 16mm. They are stacked VERTICALLY instead, both
// centred on the same span of X. That works precisely because the two
// boards sit at different heights in the stack, so the openings never
// meet - and it is a reminder that usb_charge_z and usb_data_z must stay
// far enough apart for that to hold.
strap_web_start = strap_slot_inset + strap_slot_width;
strap_web_end   = outer_length - strap_slot_inset - strap_slot_width;
usb_web_centre  = (strap_web_start + strap_web_end) / 2;

usb_charge_x = usb_web_centre - usb_charge_w / 2;
usb_data_x   = usb_web_centre - usb_data_w / 2;

assert(usb_charge_x >= strap_web_start && usb_charge_x + usb_charge_w <= strap_web_end,
       "Charging port overruns a strap tunnel - widen the web between tunnels.");
assert(usb_data_x >= strap_web_start && usb_data_x + usb_data_w <= strap_web_end,
       "Data port overruns a strap tunnel - widen the web between tunnels.");
assert(abs(usb_charge_z - usb_data_z) > (usb_charge_h + usb_data_h) / 2,
       "The two USB openings overlap vertically - separate usb_charge_z and usb_data_z.");

$fn = 48;

module rounded_box(size, radius) {
    x = size[0]; y = size[1]; z = size[2];
    hull() {
        for (dx = [radius, x - radius])
            for (dy = [radius, y - radius])
                translate([dx, dy, 0])
                    cylinder(r = radius, h = z);
    }
}

module wristband_slots() {
    // Two lug tunnels, positioned near each end of the pod (X), boring
    // through in Y so the strap can pass side to side. Low enough (Z)
    // that they don't reach into the lid's seam.
    slot_z = wall_thickness + fit_clearance;
    for (slot_x = [strap_slot_inset, outer_length - strap_slot_inset - strap_slot_width])
        translate([slot_x, -1, slot_z])
            cube([strap_slot_width, outer_width + 2, strap_slot_height]);
}

module switch_slot() {
    // Rectangular opening through the +X end wall for the slide switch's
    // actuator. Sits partway up the wall so the switch body can rest
    // against the inside face with its pins pointing inward.
    //
    // Deliberately only the opening - the body is NOT captured by any
    // printed feature. Retaining it is an assembly step (glue, or a scrap
    // of perfboard glued to the inner wall). Modelling a press-fit pocket
    // would need real caliper numbers first, and guessing one that ends up
    // too tight is worse than leaving it out.
    translate([outer_length - wall_thickness - 1,
               switch_slot_y,
               switch_slot_z - switch_slot_width / 2])
        cube([wall_thickness + 2, switch_slot_length, switch_slot_width]);
}

module usb_ports() {
    // Both openings pierce the +Y long side wall. Deliberately plain
    // rectangles: no recess or funnel, because either would need the
    // connector's exact setback from its board edge, which isn't known
    // until the boards are positioned. Slightly oversize instead - a plug
    // that goes in easily beats a neat hole that doesn't reach.
    translate([usb_charge_x, outer_width - wall_thickness - 1, usb_charge_z - usb_charge_h / 2])
        cube([usb_charge_w, wall_thickness + 2, usb_charge_h]);

    translate([usb_data_x, outer_width - wall_thickness - 1, usb_data_z - usb_data_h / 2])
        cube([usb_data_w, wall_thickness + 2, usb_data_h]);
}

module sensor_window() {
    // Bored through the -X FRONT wall, along X, so the sensor looks in
    // the direction of travel. Centred across the width.
    translate([-1, outer_width / 2, sensor_window_z])
        rotate([0, 90, 0])
            cylinder(d = sensor_window_dia, h = wall_thickness + 2);
}

module base() {
    difference() {
        rounded_box([outer_length, outer_width, outer_height - lid_lip_height], corner_radius);

        translate([wall_thickness, wall_thickness, wall_thickness])
            rounded_box(
                [outer_length - wall_thickness * 2, outer_width - wall_thickness * 2, outer_height],
                max(corner_radius - wall_thickness, 0.5)
            );

        wristband_slots();
        switch_slot();
        usb_ports();
        sensor_window();
    }
}

module lid() {
    // Plain cover now - the sensor window moved to the front wall of the
    // base, so nothing pierces the lid. It lifts off the TOP, which is the
    // face away from the arm; a seam on the underside would press against
    // the wrist all day.
    union() {
        rounded_box([outer_length, outer_width, wall_thickness], corner_radius);

        // Inner lip that plugs into the base for a friction-fit close.
        translate([wall_thickness + lid_lip_clearance, wall_thickness + lid_lip_clearance, -lid_lip_height])
            rounded_box(
                [outer_length - (wall_thickness + lid_lip_clearance) * 2,
                 outer_width - (wall_thickness + lid_lip_clearance) * 2,
                 lid_lip_height],
                max(corner_radius - wall_thickness, 0.5)
            );
    }
}

module wristband_back() {
    // v1 primary mount. No extra geometry beyond base() itself - the
    // strap lug tunnels are already cut into it. This module exists so
    // "which back are you printing" is an explicit choice, matching
    // belt_clip_back() below.
    base();
}

module belt_clip_back() {
    // Alternative mount: cantilevered belt clip instead of a wristband
    // strap. NOT trusted as-is - needs print-and-test iteration. Clip
    // flex/grip depends heavily on printer, material, and layer
    // orientation, none of which is known yet.
    difference() {
        rounded_box([outer_length, outer_width, outer_height - lid_lip_height], corner_radius);
        translate([wall_thickness, wall_thickness, wall_thickness])
            rounded_box(
                [outer_length - wall_thickness * 2, outer_width - wall_thickness * 2, outer_height],
                max(corner_radius - wall_thickness, 0.5)
            );
    }

    clip_height = outer_height * 0.7;

    // Vertical arm, standing off the back of the pod.
    translate([outer_length / 2 - belt_clip_arm_length / 2, -belt_clip_gap - belt_clip_thickness, 0])
        cube([belt_clip_arm_length, belt_clip_thickness, clip_height]);

    // Return lip at the top of the arm, closing the gap back toward the
    // pod so a belt/waistband is captured between them.
    translate([outer_length / 2 - belt_clip_arm_length / 2, -belt_clip_gap - belt_clip_thickness, clip_height - belt_clip_thickness])
        cube([belt_clip_arm_length, belt_clip_gap + belt_clip_thickness, belt_clip_thickness]);
}

// ============================================================
// Switch fit test coupon - print this BEFORE the real enclosure.
// ============================================================
//
// The switch actuator's dimensions are the hardest numbers in this whole
// model to measure: the nub is a couple of millimetres across, and what
// actually matters isn't its size but how much slot it needs to travel
// freely without rattling. Calipers answer the first question, not the
// second.
//
// So don't measure it - test it. This coupon is a flat plate, printed at
// the real wall_thickness, carrying ten candidate slots:
//   - two rows: 3.0mm wide (upper) and 4.0mm wide (lower)
//   - five columns: 5, 6, 7, 8, 9mm long, left to right
//
// Print it (a few minutes, a few grams), then push the switch's actuator
// through each slot in turn. You want the SMALLEST slot the slider can
// travel end to end in without catching. Note its row and column, set
// switch_slot_length / switch_slot_width from the table above, and the
// real enclosure will fit first time.
//
// Printing this costs one short print and saves the reprint-and-refit
// loop that Phase 7 of tutorial.md warns takes 2-3 attempts.
coupon_widths  = [3.0, 4.0];
coupon_lengths = [5, 6, 7, 8, 9];
coupon_pitch_x = 12;
coupon_pitch_y = 10;
coupon_margin  = 5;

module switch_test_coupon() {
    plate_x = coupon_margin * 2 + coupon_pitch_x * len(coupon_lengths);
    plate_y = coupon_margin * 2 + coupon_pitch_y * len(coupon_widths);

    difference() {
        rounded_box([plate_x, plate_y, wall_thickness], corner_radius);

        for (row = [0 : len(coupon_widths) - 1])
            for (col = [0 : len(coupon_lengths) - 1])
                translate([
                    coupon_margin + coupon_pitch_x * col + (coupon_pitch_x - coupon_lengths[col]) / 2,
                    coupon_margin + coupon_pitch_y * row + (coupon_pitch_y - coupon_widths[row]) / 2,
                    -1
                ])
                    cube([coupon_lengths[col], coupon_widths[row], wall_thickness + 2]);
    }
}

module render_all() {
    wristband_back();
    translate([0, outer_width + 5, 0]) lid();
    translate([0, -(outer_width + 5), 0]) belt_clip_back();
}

if (part == "base" || part == "wristband_back") wristband_back();
else if (part == "lid") lid();
else if (part == "belt_clip_back") belt_clip_back();
else if (part == "switch_test_coupon") switch_test_coupon();
else render_all();
