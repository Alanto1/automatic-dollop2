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
//   Z axis - up. The lid (+Z) carries the sensor window and faces
//            outward, away from the skin. The base (-Z) sits against
//            the wrist.
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

belt_clip_arm_length = 35;
belt_clip_gap        = 6;    // fits a typical belt/waistband strap
belt_clip_thickness  = 2.5;

// Internal cavity sized to fit the tallest component, with everything
// else assumed to sit beside it on the floor of the base - this is a
// simplified layout, not a precision placement, which isn't meaningful
// until the [MEASURE YOUR PARTS] block above holds real numbers anyway.
internal_length = max(nano_length, battery_length) + fit_clearance * 2;
internal_width  = nano_width + tof_width + fit_clearance * 3;
internal_height = max(nano_stack_height, tof_stack_height, motor_thickness, battery_thickness)
                   + fit_clearance * 2;

outer_length = internal_length + wall_thickness * 2;
outer_width  = internal_width + wall_thickness * 2;
outer_height = internal_height + wall_thickness + lid_lip_height;

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

module base() {
    difference() {
        rounded_box([outer_length, outer_width, outer_height - lid_lip_height], corner_radius);

        translate([wall_thickness, wall_thickness, wall_thickness])
            rounded_box(
                [outer_length - wall_thickness * 2, outer_width - wall_thickness * 2, outer_height],
                max(corner_radius - wall_thickness, 0.5)
            );

        wristband_slots();
    }
}

module lid() {
    difference() {
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

        // Sensor window, centered over where the ToF sensor sits near one
        // end (X) - see README.md's wiring diagram for which end faces
        // forward when worn.
        translate([strap_slot_inset + tof_length / 2, outer_width / 2, -1])
            cylinder(d = tof_window_dia, h = wall_thickness + 2);
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

module render_all() {
    wristband_back();
    translate([0, outer_width + 5, 0]) lid();
    translate([0, -(outer_width + 5), 0]) belt_clip_back();
}

if (part == "base" || part == "wristband_back") wristband_back();
else if (part == "lid") lid();
else if (part == "belt_clip_back") belt_clip_back();
else render_all();
