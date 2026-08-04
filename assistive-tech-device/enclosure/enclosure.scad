// enclosure.scad
//
// Parametric OpenSCAD enclosure for the obstacle-detection wristband pod.
//
// Render-verified headlessly (openscad CLI, 2021.01) on 2026-08-03: base,
// lid, belt_clip_back and switch_test_coupon all export as valid manifold
// geometry ("Simple: yes") with no warnings, and every cutout was checked
// against its expected coordinates in the exported STL rather than taken
// on trust - because this file has twice produced a clean render where a
// cutout had silently landed inside another opening and removed nothing.
//
// That confirms the CSG is well-formed. It does NOT confirm fit: the
// switch actuator size and the USB connector body margin in the
// "[MEASURE YOUR PARTS]" block are still guesses, not caliper
// measurements. Re-render after updating them, and before printing.
//
// Orientation convention used throughout this file:
//   X axis - the pod's 67mm length, lying ALONG the arm.
//   Y axis - the pod's 30mm width, so a 30mm end face looks forward, in
//            the direction of travel. The strap runs this way too, around
//            the wrist, and the strap tunnel bores through in Y.
//   Z axis - up. The lid (+Z) lifts off the top, away from the skin; a
//            seam on the underside would press into the wrist. The base
//            (-Z) sits against the arm.
//
// Face assignments:
//   -X front  : sensor window, looking in the direction of travel
//   +X back   : power switch slot
//   base underside : ONE 20mm strap tunnel, in a plinth BELOW the box
//   lid top   : both USB openings, pointing straight up
//
// HEIGHTS, since three different numbers all get called "the height":
//   box_outer_height  50    the open-topped box that holds the electronics
//   base_height       57.2  what actually prints, box + strap plinth
//   assembled         59.4  base_height + the lid's plate on top
//   cavity_height     44.8  what a board hanging from the lid can use
//
// The strap plinth is EXTRA height under the box, not a slice taken out
// of it. An earlier revision did it the other way - tunnel through the
// box's own floor - and the cavity paid 7mm for it.
//
// STRAP MOUNT - changed 2026-08-03, and the tradeoff is deliberate.
//
// This file used to cut TWO lug tunnels through the long walls near each
// X end, like a watch's spring bars, and its own comments explicitly
// rejected a single slot on the grounds that one wrap point lets the pod
// pivot instead of sitting flat. The builder has asked for the single
// channel anyway, so that is what is modelled now.
//
// The pivot concern has not gone away, it has been accepted: with one
// 20mm passage the pod can rock about the strap's axis, and the sensor
// aims wherever the pod happens to be pointing. Three things reduce it in
// practice - the channel is a full tunnel rather than a pair of skids, so
// the strap is captured on all four sides; the plinth is the pod's whole
// 67 x 30 footprint, so the pod beds down on a wide flat face rather than
// balancing on a narrow pedestal; and that footprint is long enough to
// settle against the arm. If it turns out to
// wander in real use, the fix is to widen the channel's X span so it grips
// more strap length, or to go back to two tunnels.
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
// LAYOUT CONSTRAINT this imposes: ALL THREE BOARDS HANG VERTICALLY FROM
// THE LID, and the two that carry connectors hang connector-end UP, so
// both ports point straight out through the top face. Lift the lid and
// the whole electronics stack comes with it - the pod is serviceable
// rather than a sealed box you have to dig into.
//
// The openings therefore live in the LID, not in a wall. That is the one
// arrangement where "hangs from the lid" and "port is reachable" are the
// same statement; a port on a flank would need the board turned sideways,
// at which point it no longer hangs.
//
// COST OF THIS, and it is a real one: the lid is wall_thickness + lip =
// 5.2mm thick where the ports pass through, and a plug has to reach the
// receptacle through all of it. The counterbore below is what makes that
// work - see usb_ports().
//
// MEASURED 2026-08-02.
usb_charge_width  = 8.86;  // TP4056 Type-C receptacle, across
usb_charge_height = 4.14;
usb_data_width    = 7.5;   // Nano mini-USB receptacle, across
usb_data_height   = 6.33;
// How much bigger the connector's BODY is than its mouth, all round. The
// lip is pocketed by this much so the connector can nest up inside it and
// present its mouth close to the outer face, instead of sitting 5.2mm
// down a shaft no plug can reach.
//
// A GUESS, not a measurement - 2mm is typical for the metal shell and
// solder tabs around a mini-USB or Type-C receptacle. Check it against the
// real boards before printing: too small and the connector won't nest, and
// the port becomes unusable without anyone noticing until assembly.
usb_body_margin   = 2;
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
// sensor_window_z is derived below - centred in the cavity.

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

// ONE strap channel, through the underside of the base, centred along X.
// Width here is along X (the strap's own width); height is the clear gap
// the strap slides through.
strap_channel_width  = strap_width + 1.5;    // 21.5 for a 20mm strap
strap_channel_height = strap_thickness + 2;  // 5 for a 3mm strap

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
//
// INERT RIGHT NOW, and that matters: box_outer_length/width/height below
// are all set to real numbers from the builder's sketch, and those win.
// Changing the three values here will render an identical part and look
// like the edit did nothing. To size the pod from the bundle again, zero
// out the box_outer_* overrides first.
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

// Direct outer-size override. Set these when you've decided the box's
// external dimensions rather than deriving them from what's inside -
// which is what happens once you've sketched a box and want it built to
// that size. 0 = derive as before.
//
// box_outer_height is the BOX ALONE - the open-topped part that holds the
// electronics, measured from the top of the strap compartment upward. The
// strap compartment is extra height BELOW it, not a slice out of it, so
// the printed base comes out taller than this number. See base_height.
box_outer_length = 67;
box_outer_width  = 30;
box_outer_height = 50;

outer_length = box_outer_length > 0
    ? box_outer_length
    : internal_length + wall_thickness * 2;

outer_width  = box_outer_width  > 0 ? box_outer_width  : internal_width + wall_thickness * 2;
box_height   = box_outer_height > 0 ? box_outer_height : internal_height + wall_thickness + lid_lip_height;

// Strap compartment, centred along the pod's length, boring through in Y
// so the strap runs around the wrist while the pod's 67mm length lies
// along the arm.
//
// It is a PLINTH UNDER THE BOX, not a tunnel through the box's floor.
// That is the whole point: it costs the interior nothing. The earlier
// revision put the tunnel inside the 50mm and the cavity paid for it,
// dropping usable height to 37.6mm; this way the cavity keeps its full
// 44.8mm and the pod just stands ~7mm further off the wrist.
//
// Full footprint rather than a pedestal under the middle only. A pedestal
// would save a little material and shorten the contact patch, but the
// box's floor would then overhang it at 71 degrees from vertical - a
// support-or-fail overhang - and the ramp needed to bring that back to a
// printable 45 degrees would reach almost to the pod's ends anyway.
strap_plinth_height = wall_thickness + strap_channel_height;  // 2.2 + 5
strap_channel_x     = (outer_length - strap_channel_width) / 2;

// Everything above the plinth. box_z0 is the underside of the 50mm box.
box_z0      = strap_plinth_height;
base_height = box_z0 + box_height;   // total printed height of the base

assert(strap_channel_width + wall_thickness * 4 <= outer_length,
       "Strap channel leaves too little material at the pod's ends.");

// Switch slot, cut into the +X END wall - the short face at the far end
// from the sensor.
//
// It started on a long side wall, which was wrong: back then the strap
// tunnels bored straight through both long walls, so a side slot landed
// inside an existing opening and cut nothing. Putting it at the end
// opposite the sensor also means a finger reaching for the switch never
// passes in front of the sensor window - which is why it stays here even
// now that the long walls are clear.
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
// Cavity reference planes, used by every cutout below. All in absolute Z
// with the printed base's underside at 0, so the layers stack:
//
//   0    -> 2.2   bottom skin, the face against the wrist
//   2.2  -> 7.2   strap tunnel (5mm clear)         } the plinth
//   7.2  -> 9.4   the box's own floor
//   9.4  -> 54.2  cavity, 44.8mm of usable interior
//   54.2 -> 57.2  seat the lid's lip plugs into
//   57.2 -> 59.4  lid plate, once closed
//
// The tunnel's roof and the box's floor are separate 2.2mm layers rather
// than one shared skin, so neither is doing two jobs. The floor bridges
// the 21.5mm of tunnel below it - print with supports, or accept some
// droop; nothing structural rests on it, since the boards hang from the
// lid.
cavity_floor  = box_z0 + wall_thickness;
lid_underside = base_height - lid_lip_height;
cavity_mid_z  = (cavity_floor + lid_underside) / 2;

// Height available to a board hanging from the lid's underside. Worth
// checking against a real board: an Arduino Nano is 45mm on its long
// edge, and 44.8mm is 0.2mm short of that - so the Nano has to hang
// 18mm-edge-down, or box_outer_height has to go up by a millimetre.
cavity_height = lid_underside - cavity_floor;

assert(cavity_height > 10,
       "Cavity is too shallow - raise box_outer_height.");

// Switch and sensor sit mid-height. Neither is forced to a particular
// height - the switch just needs a finger, the sensor an unobstructed
// view - so centring leaves the most material around each opening.
switch_slot_z   = cavity_mid_z;
sensor_window_z = cavity_mid_z;

assert(switch_slot_length + wall_thickness * 2 <= outer_width,
       "Switch actuator slot is wider than the pod's end face.");
assert(switch_slot_z + switch_slot_width / 2 <= lid_underside,
       "Switch slot runs past the top of the base and into the lid seam.");
assert(switch_slot_z - switch_slot_width / 2 >= cavity_floor,
       "Switch slot runs below the cavity floor and into the strap compartment.");
assert(sensor_window_z - sensor_window_dia / 2 >= cavity_floor,
       "Sensor window runs below the cavity floor and into the strap compartment.");

// USB openings are in the LID, pointing straight up (+Z), because the
// boards hang vertically from the lid with their connector ends at the
// top. So these are X-Y positions in the lid plane, not X-Z positions on
// a wall - the receptacle's "width" runs along X, its "height" along Y.
usb_charge_w = usb_charge_width + usb_clearance;
usb_charge_d = usb_charge_height + usb_clearance;   // along Y now
usb_data_w   = usb_data_width + usb_clearance;
usb_data_d   = usb_data_height + usb_clearance;

// Side by side along the lid's length, centred as a pair.
//
// The gap is measured between the MOUTHS, but what has to stay solid is
// the material between the COUNTERBORES, which are usb_body_margin wider
// on each facing side. A flat 4mm gap left exactly 0mm of wall between
// the two pockets - they abutted at a plane, CGAL still called the result
// simple, and the lid would have printed with the two pockets merged into
// one trench. Derive it instead so the two can't touch.
usb_gap      = usb_body_margin * 2 + 2;
usb_total_w  = usb_charge_w + usb_gap + usb_data_w;
usb_charge_x = (outer_length - usb_total_w) / 2;
usb_data_x   = usb_charge_x + usb_charge_w + usb_gap;

// Both centred across the width, which assumes the two boards hang in the
// SAME plane. If they end up hanging as parallel plates at different Y
// depths instead, split these two values by the board-to-board pitch -
// that is the one edit this layout is likely to need, so it's a separate
// parameter per port rather than one shared centre line.
usb_charge_y = (outer_width - usb_charge_d) / 2;
usb_data_y   = (outer_width - usb_data_d) / 2;

// The lid's lip is inset from its edge, and the counterbore is cut into
// that lip - so a port too close to the edge would break out of the side
// of the lip and hold nothing. Check against the lip footprint, not the
// lid's outer rectangle.
lip_inset = wall_thickness + lid_lip_clearance;

assert(usb_gap > usb_body_margin * 2,
       "USB counterbores touch or overlap - the two pockets would merge into one trench.");
assert(usb_charge_x - usb_body_margin >= lip_inset
       && usb_data_x + usb_data_w + usb_body_margin <= outer_length - lip_inset,
       "A USB counterbore runs off the end of the lid's lip.");
assert(usb_charge_y - usb_body_margin >= lip_inset
       && usb_charge_y + usb_charge_d + usb_body_margin <= outer_width - lip_inset,
       "The charging port's counterbore runs off the side of the lid's lip.");
assert(usb_data_y - usb_body_margin >= lip_inset
       && usb_data_y + usb_data_d + usb_body_margin <= outer_width - lip_inset,
       "The data port's counterbore runs off the side of the lid's lip.");
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

module strap_channel() {
    // ONE tunnel through the UNDERSIDE of the base, centred along the
    // pod's length and boring through in Y, so the strap passes under the
    // pod rather than through its interior.
    //
    // CLOSED on all four sides, not a groove open to the wrist. An open
    // groove would print more easily and thread more easily, but it can
    // only hold the pod on while the strap is under tension - take the
    // band off and the pod drops out - and its two open edges are what
    // press into the skin. A closed tunnel keeps the underside a
    // continuous face against the wrist and keeps the pod on the strap
    // whether it is worn or not. The strap threads in from one Y side.
    translate([strap_channel_x, -1, wall_thickness])
        cube([strap_channel_width, outer_width + 2, strap_channel_height]);
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

module usb_port_cut(px, py, pw, pd) {
    // One port through the lid, in two stages.
    //
    // Stage 1, through the top plate: the plug's own cross-section. This
    // is the visible opening.
    //
    // Stage 2, a wider pocket through the lip below it: room for the
    // connector's metal shell and solder tabs to nest UP inside the lid.
    // Without it the receptacle sits at the bottom of a 5.2mm shaft and
    // most plugs cannot reach it - the port would look finished and be
    // unusable. This is the whole reason a lid-mounted port works at all.
    translate([px, py, -0.5])
        cube([pw, pd, wall_thickness + 1]);

    translate([px - usb_body_margin, py - usb_body_margin, -lid_lip_height - 1])
        cube([pw + usb_body_margin * 2,
              pd + usb_body_margin * 2,
              lid_lip_height + 1.5]);
}

module usb_ports() {
    // Both openings pierce the LID, pointing up. See the [MEASURE YOUR
    // PARTS] USB block for why they're here and not on a wall.
    usb_port_cut(usb_charge_x, usb_charge_y, usb_charge_w, usb_charge_d);
    usb_port_cut(usb_data_x,   usb_data_y,   usb_data_w,   usb_data_d);
}

module sensor_window() {
    // Bored through the -X FRONT wall, along X, so the sensor looks in
    // the direction of travel. Centred across the width.
    translate([-1, outer_width / 2, sensor_window_z])
        rotate([0, 90, 0])
            cylinder(d = sensor_window_dia, h = wall_thickness + 2);
}

module pod_shell(with_strap = true) {
    // The open-topped box, shared by both back options.
    //
    // It is ONE module on purpose. belt_clip_back() used to duplicate this
    // geometry by hand, and the copy silently never picked up the switch
    // slot or the sensor window - so printing it produced a sealed box
    // with no openings at all. Anything added here now reaches both.
    difference() {
        rounded_box([outer_length, outer_width, base_height], corner_radius);

        // Cavity floor sits on top of the strap plinth, not one wall
        // thickness off the print bed - see cavity_floor.
        translate([wall_thickness, wall_thickness, cavity_floor])
            rounded_box(
                [outer_length - wall_thickness * 2, outer_width - wall_thickness * 2, base_height],
                max(corner_radius - wall_thickness, 0.5)
            );

        if (with_strap) strap_channel();
        switch_slot();
        sensor_window();
    }
}

module base() {
    pod_shell(with_strap = true);
}

module lid() {
    // Lifts off the TOP, which is the face away from the arm; a seam on
    // the underside would press against the wrist all day. Carries both
    // USB openings, because all three boards hang from it and the two
    // with connectors hang connector-end up.
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

        usb_ports();
    }
}

module wristband_back() {
    // v1 primary mount. No extra geometry beyond base() itself - the
    // strap tunnel is already cut into it. This module exists so "which
    // back are you printing" is an explicit choice, matching
    // belt_clip_back() below.
    base();
}

module belt_clip_back() {
    // Alternative mount: cantilevered belt clip instead of a wristband
    // strap. NOT trusted as-is - needs print-and-test iteration. Clip
    // flex/grip depends heavily on printer, material, and layer
    // orientation, none of which is known yet.
    //
    // Same shell as the wristband version, just without the strap tunnel
    // bored through the plinth. The plinth itself stays: it carries the
    // switch slot and sensor window at the same heights, so both backs
    // take the same lid and the same board layout.
    pod_shell(with_strap = false);

    clip_height = base_height * 0.7;

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
