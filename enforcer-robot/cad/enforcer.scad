// The Enforcer -- parametric source for every printed part.
//
// This is the editable authority on the robot's geometry. make_stl.py holds
// the same numbers and generates the STLs in stl/ without needing OpenSCAD
// installed; if you change a dimension here, change it there too (the
// constants block at the top of the file is deliberately identical).
//
// Render one part at a time:
//     openscad -o stl/chassis_plate.stl -D 'part="chassis_plate"' enforcer.scad
// or set `part` below and hit F5 to preview.

part = "assembly";  // chassis_plate | coxa_bracket | femur | tibia | face_bezel | assembly

$fn = 48;

// ---------------------------------------------------------------- hardware
// MG90S metal-gear servo -- every bracket is dimensioned around this part.
servo_body_l   = 22.8;
servo_body_w   = 12.2;
servo_body_h   = 22.5;
servo_hole_span= 27.8;   // centre-to-centre of the mounting ears
servo_hole_d   = 2.2;    // M2 clearance
servo_shaft_off= 6.0;    // output shaft inset from the body end

fit      = 0.6;          // total clearance across a printed pocket
pocket_l = servo_body_l + fit;
pocket_w = servo_body_w + fit;

plate_t     = 3.0;
horn_screw_d= 1.8;
M2  = 2.2;
M25 = 2.7;

// ------------------------------------------------------------- kinematics
// The leg IK simulator must use exactly these three lengths.
coxa_len  = 28.0;   // vertical hip axis -> femur axis
femur_len = 50.0;   // femur axis -> knee axis
tibia_len = 55.0;   // knee axis -> foot tip

stand_h     = 70.0; // design ride height (foot below the femur axis)
stand_reach = 10.0; // foot's horizontal offset out from the femur axis

body_l = 130.0;
body_w = 95.0;
hip_x  = 46.0;
hip_y  = 32.0;

coxa_wall_h = 40.0; // set by servo screw spacing, not by coxa_len
shaft_off   = pocket_l / 2 - servo_shaft_off;

pi5_holes = [58.0, 49.0];

// ------------------------------------------------------------------ 2D ops
module servo_pocket_2d(angle = 0) {
    rotate([0, 0, angle]) {
        square([pocket_l, pocket_w], center = true);
        for (s = [-1, 1])
            translate([s * servo_hole_span / 2, 0])
                circle(d = servo_hole_d);
    }
}

module horn_holes_2d(r = 7.0, n = 4) {
    circle(d = 8.0);
    for (i = [0 : n - 1])
        rotate([0, 0, i * 360 / n])
            translate([r, 0]) circle(d = horn_screw_d);
}

module rrect(w, h, r) {
    offset(r = r) offset(r = -r) square([w, h], center = true);
}

module capsule2d(len, w) {
    hull() {
        circle(d = w);
        translate([len, 0]) circle(d = w);
    }
}

// ------------------------------------------------------------------ parts

// Four coxa servos drop through this plate; the Pi bolts on top of it, and
// the PCA9685 stacks on standoffs above the Pi.
module chassis_plate() {
    linear_extrude(plate_t)
    difference() {
        rrect(body_l, body_w, 8);
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * hip_x, sy * hip_y])
                servo_pocket_2d(sx * sy > 0 ? 45 : -45);
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * pi5_holes[0] / 2, sy * pi5_holes[1] / 2])
                circle(d = M25);
        for (sy = [-1, 1])
            translate([0, sy * 38]) rrect(30, 6, 3);
    }
}

// L-bracket: bolts to the coxa horn, carries the femur servo standing up.
module coxa_bracket() {
    linear_extrude(plate_t)
    difference() {
        rrect(30, 26, 4);
        horn_holes_2d();
    }
    // Wall along the -Y edge, overlapping the base so the two fuse.
    translate([0, -13 + 1.5, 0])
    rotate([90, 0, 0])
    translate([0, coxa_wall_h / 2, -plate_t])
    linear_extrude(plate_t)
    difference() {
        rrect(30, coxa_wall_h, 4);
        translate([0, (coxa_len - coxa_wall_h / 2) - shaft_off])
            servo_pocket_2d(90);
    }
}

// Thigh: femur horn at one end, knee servo pocket at the other.
module femur() {
    linear_extrude(plate_t)
    difference() {
        capsule2d(femur_len, 24);
        horn_holes_2d();
        translate([femur_len - servo_shaft_off + 2, 0]) servo_pocket_2d(0);
    }
}

// Shin: knee horn at the top, lightening slot, rounded foot.
module tibia() {
    linear_extrude(plate_t)
    difference() {
        capsule2d(tibia_len, 20);
        horn_holes_2d();
        translate([22, 0]) capsule2d(tibia_len - 38, 7);
    }
}

// Front panel: window for the rectangular face display.
module face_bezel() {
    linear_extrude(plate_t)
    difference() {
        rrect(52, 38, 4);
        rrect(30, 22, 2);
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * 22, sy * 15]) circle(d = M2);
    }
}

// --------------------------------------------------------------- assembly

// Two-link IK, matching leg_ik() in make_stl.py.
function _d()   = sqrt(stand_reach * stand_reach + stand_h * stand_h);
function _knee()= 180 - acos((femur_len * femur_len + tibia_len * tibia_len - _d() * _d())
                             / (2 * femur_len * tibia_len));
function _femur()= atan2(stand_h, stand_reach)
                 - acos((femur_len * femur_len + _d() * _d() - tibia_len * tibia_len)
                        / (2 * femur_len * _d()));

module leg() {
    coxa_bracket();
    translate([coxa_len, 0, coxa_len]) {
        rotate([0, _femur(), 0]) femur();
        translate([femur_len * cos(_femur()), 0, -femur_len * sin(_femur())])
            rotate([0, _femur() + _knee(), 0]) tibia();
    }
}

module assembly() {
    chassis_plate();
    for (sx = [-1, 1], sy = [-1, 1])
        translate([sx * hip_x, sy * hip_y, plate_t])
            rotate([0, 0, sx > 0 ? (sy > 0 ? 45 : -45) : (sy > 0 ? 135 : -135)])
                leg();
    translate([body_l / 2 - 4, 0, 22]) rotate([90, 0, 90]) face_bezel();
}

// ------------------------------------------------------------------ render
if      (part == "chassis_plate") chassis_plate();
else if (part == "coxa_bracket")  coxa_bracket();
else if (part == "femur")         femur();
else if (part == "tibia")         tibia();
else if (part == "face_bezel")    face_bezel();
else                              assembly();
