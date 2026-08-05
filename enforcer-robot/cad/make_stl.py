#!/usr/bin/env python3
"""
The Enforcer — printable part generator.

Emits binary STL for every printed part of the quadruped, plus a posed
assembly preview. Pure standard library: no numpy, no OpenSCAD, no CAD kernel.

Parts are built as unions of extruded 2D profiles with holes. Profiles are
triangulated by hole-bridging + ear clipping, then walled. Every emitted solid
is checked watertight (each directed edge used exactly once, each edge paired
with its reverse) before it is written -- see self_test().

    python3 make_stl.py            # write stl/*.stl
    python3 make_stl.py --test     # run the geometry self-tests only

All dimensions in millimetres. Z is up, +X is forward, +Y is left.
"""

from __future__ import annotations

import math
import os
import struct
import sys

# --------------------------------------------------------------------------
# Hardware the geometry has to fit
# --------------------------------------------------------------------------

# MG90S metal-gear servo, the one part every bracket is dimensioned around.
SERVO_BODY_L = 22.8
SERVO_BODY_W = 12.2
SERVO_BODY_H = 22.5
SERVO_FLANGE_L = 32.2       # tip to tip across the mounting ears
SERVO_HOLE_SPAN = 27.8      # centre-to-centre of the two mounting holes
SERVO_HOLE_D = 2.2          # M2 clearance
SERVO_SHAFT_FROM_END = 6.0  # output shaft inset from the body end

FIT = 0.6                   # printed-pocket clearance, total across a slot
POCKET_L = SERVO_BODY_L + FIT
POCKET_W = SERVO_BODY_W + FIT

PLATE_T = 3.0               # standard printed plate thickness
HORN_SCREW_D = 1.8          # self-tapping into a servo horn
M2 = 2.2
M25 = 2.7

# Link geometry. These three numbers are the robot's kinematics -- the leg IK
# simulator must use exactly these.
COXA_LEN = 28.0             # vertical hip axis -> femur axis
FEMUR_LEN = 50.0            # femur axis -> knee axis
TIBIA_LEN = 55.0            # knee axis -> foot tip
STAND_H = 70.0              # design ride height, foot below the femur axis
STAND_REACH = 10.0          # foot's horizontal offset out from the femur axis

BODY_L = 130.0
BODY_W = 95.0
HIP_X = 46.0                # hip positions, +-HIP_X by +-HIP_Y
HIP_Y = 32.0

PI5_HOLES = (58.0, 49.0)    # Raspberry Pi 5 mounting hole pattern

SEG = 24                    # facets per full circle

# --------------------------------------------------------------------------
# 2D profile helpers. A profile is a list of (x, y); outer rings CCW, holes CW.
# --------------------------------------------------------------------------


def circle(cx: float, cy: float, d: float, seg: int = SEG, cw: bool = True):
    r = d / 2.0
    pts = [
        (cx + r * math.cos(2 * math.pi * i / seg), cy + r * math.sin(2 * math.pi * i / seg))
        for i in range(seg)
    ]
    return pts[::-1] if cw else pts


def rect(cx: float, cy: float, w: float, h: float, angle: float = 0.0, cw: bool = False):
    """Rectangle centred on (cx, cy), rotated `angle` degrees CCW."""
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    corners = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    pts = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in corners]
    return pts[::-1] if cw else pts


def rounded_rect(cx, cy, w, h, r, seg_q: int = 6, cw: bool = False):
    """Rectangle with radiused corners."""
    r = min(r, w / 2, h / 2)
    pts = []
    quads = [
        (cx + w / 2 - r, cy + h / 2 - r, 0.0),
        (cx - w / 2 + r, cy + h / 2 - r, 90.0),
        (cx - w / 2 + r, cy - h / 2 + r, 180.0),
        (cx + w / 2 - r, cy - h / 2 + r, 270.0),
    ]
    for qx, qy, base in quads:
        for i in range(seg_q + 1):
            a = math.radians(base + 90.0 * i / seg_q)
            pts.append((qx + r * math.cos(a), qy + r * math.sin(a)))
    return pts[::-1] if cw else pts


def capsule(x0, y0, x1, y1, w, seg_q: int = 8, cw: bool = False):
    """Rounded slot between two points -- the natural shape for a link."""
    r = w / 2.0
    ang = math.atan2(y1 - y0, x1 - x0)
    pts = []
    for i in range(seg_q + 1):
        a = ang - math.pi / 2 + math.pi * i / seg_q
        pts.append((x1 + r * math.cos(a), y1 + r * math.sin(a)))
    for i in range(seg_q + 1):
        a = ang + math.pi / 2 + math.pi * i / seg_q
        pts.append((x0 + r * math.cos(a), y0 + r * math.sin(a)))
    return pts[::-1] if cw else pts


def _clean_ring(ring, want_ccw: bool, eps: float = 1e-9):
    """Drop repeated points and force a winding direction.

    Repeated points are easy to produce by accident -- a rounded rectangle
    whose corner radius equals half its height has zero-length straight
    sides, for instance -- and they wedge the ear clipper: a zero-area
    triangle is never a valid ear, so the two vertices either side of it can
    never be removed. Both the triangulator and the wall builder must clean
    rings the same way, or the walls will not match the faces.
    """
    out = []
    for p in ring:
        if not out or math.dist(p, out[-1]) > eps:
            out.append(tuple(p))
    while len(out) > 1 and math.dist(out[0], out[-1]) < eps:
        out.pop()
    if (signed_area(out) > 0) != want_ccw:
        out.reverse()
    return out


def signed_area(poly) -> float:
    s = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        s += x0 * y1 - x1 * y0
    return s / 2.0


def servo_pocket(cx, cy, angle):
    """Body cutout + the two mounting holes, for a servo dropped through a plate."""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    off = SERVO_HOLE_SPAN / 2.0
    return [
        rect(cx, cy, POCKET_L, POCKET_W, angle, cw=True),
        circle(cx + ux * off, cy + uy * off, SERVO_HOLE_D),
        circle(cx - ux * off, cy - uy * off, SERVO_HOLE_D),
    ]


def horn_holes(cx, cy, r=7.0, n=4, d=HORN_SCREW_D):
    """Bolt circle matching a round servo horn, plus the central shaft clearance."""
    out = [circle(cx, cy, 8.0)]
    for i in range(n):
        a = 2 * math.pi * i / n
        out.append(circle(cx + r * math.cos(a), cy + r * math.sin(a), d))
    return out


# --------------------------------------------------------------------------
# Triangulation: bridge holes into the outer ring, then ear-clip.
# --------------------------------------------------------------------------


def _tri_area2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _blocks_ear(p, a, b, c, eps: float = 1e-9) -> bool:
    """Does vertex p prevent (a, b, c) from being clipped as an ear?

    Inside *or on the boundary* of the triangle blocks it. Testing only the
    strict interior is not enough: clipping an ear whose edge passes exactly
    through another vertex leaves a self-overlapping remainder, and the clip
    then stalls a few dozen vertices later with no ear anywhere.

    The exception is a vertex that coincides with one of the ear's own
    corners. Hole bridging deliberately duplicates vertices, so those
    coordinate-identical twins are always present and must never block.
    """
    if (
        math.dist(p, a) < 1e-7
        or math.dist(p, b) < 1e-7
        or math.dist(p, c) < 1e-7
    ):
        return False
    return (
        _tri_area2(a, b, p) >= -eps
        and _tri_area2(b, c, p) >= -eps
        and _tri_area2(c, a, p) >= -eps
    )


def _prepare(outer, holes):
    """Clean the rings and pre-split every edge that a bridge will land on.

    Bridging inserts a vertex where the ray meets the boundary. If that
    insertion happens only inside the merged polygon, the extruded side walls
    -- which are built from the original rings -- come out one vertex short
    and the solid is no longer watertight. So the split is done here, on the
    rings themselves, and both the faces and the walls use the result.

    Processing holes right-to-left guarantees each one bridges to a ring that
    is already connected to the outer boundary: any point to the right of a
    hole's rightmost vertex belongs to a ring with a larger maximum x, which
    has therefore already been handled. That rules out a bridge cycle among
    holes that never reaches the outer ring.
    """
    rings = [_clean_ring(outer, want_ccw=True)]
    rings += [_clean_ring(h, want_ccw=False) for h in holes]
    order = sorted(range(1, len(rings)), key=lambda i: -max(p[0] for p in rings[i]))

    bridges = []
    for hi in order:
        hole = rings[hi]
        m_i = max(range(len(hole)), key=lambda k: hole[k][0])
        m = hole[m_i]

        best_x, best_ring, best_edge = float("inf"), None, None
        for ri, ring in enumerate(rings):
            if ri == hi:
                continue
            n = len(ring)
            for e in range(n):
                a, b = ring[e], ring[(e + 1) % n]
                if (a[1] > m[1]) == (b[1] > m[1]):
                    continue
                t = (m[1] - a[1]) / (b[1] - a[1])
                x = a[0] + t * (b[0] - a[0])
                if x >= m[0] - 1e-9 and x < best_x:
                    best_x, best_ring, best_edge = x, ri, e
        if best_ring is None:
            raise ValueError("hole is not inside the outer ring")

        inter = (best_x, m[1])
        ring = rings[best_ring]
        n = len(ring)
        a_idx, b_idx = best_edge, (best_edge + 1) % n
        if math.dist(inter, ring[a_idx]) < 1e-7:
            tgt = a_idx
        elif math.dist(inter, ring[b_idx]) < 1e-7:
            tgt = b_idx
        else:
            rings[best_ring] = ring[: best_edge + 1] + [inter] + ring[best_edge + 1 :]
            tgt = best_edge + 1
            # Everything already recorded against this ring shifts by one.
            bridges = [
                (
                    h,
                    mi + 1 if h == best_ring and mi > best_edge else mi,
                    r,
                    ti + 1 if r == best_ring and ti > best_edge else ti,
                )
                for (h, mi, r, ti) in bridges
            ]
            if hi == best_ring and m_i > best_edge:
                m_i += 1
        bridges.append((hi, m_i, best_ring, tgt))

    return rings, bridges


def _merge(rings, bridges):
    """Splice every hole into the outer ring, following the recorded bridges."""
    merged = [(0, i) for i in range(len(rings[0]))]
    for hi, m_i, ri, ti in bridges:
        pos = merged.index((ri, ti))
        n = len(rings[hi])
        loop = [(hi, (m_i + j) % n) for j in range(n + 1)]
        merged = merged[: pos + 1] + loop + [(ri, ti)] + merged[pos + 1 :]
    return [rings[r][i] for r, i in merged]


def triangulate(outer, holes=()):
    """Triangulate a CCW outer ring containing CW holes. Returns CCW triangles."""
    rings, bridges = _prepare(outer, holes)
    return _earclip(_merge(rings, bridges))


def _earclip(poly):
    """Ear-clip a simple CCW polygon (holes already bridged in)."""
    poly = list(poly)
    tris = []
    guard = 0
    while len(poly) > 3:
        n = len(poly)
        guard += 1
        if guard > 4 * n * n + 1000:
            raise RuntimeError("ear clipping stalled")
        clipped = False
        for i in range(n):
            a, b, c = poly[(i - 1) % n], poly[i], poly[(i + 1) % n]
            if _tri_area2(a, b, c) <= 1e-9:
                continue  # reflex, collinear or degenerate
            # Compare by index, never by coordinate: bridging duplicates
            # vertices, so identical coordinates appear at several indices.
            blocked = False
            for j in range(n):
                if j in ((i - 1) % n, i, (i + 1) % n):
                    continue
                if _blocks_ear(poly[j], a, b, c):
                    blocked = True
                    break
            if blocked:
                continue
            tris.append((a, b, c))
            del poly[i]
            clipped = True
            break
        if not clipped:
            raise RuntimeError("no ear found -- self-intersecting profile?")
    tris.append(tuple(poly))
    return tris


# --------------------------------------------------------------------------
# Extrusion and transforms
# --------------------------------------------------------------------------


def extrude(outer, holes=(), z0=0.0, z1=PLATE_T):
    """Extrude a profile into a closed solid. Returns a triangle list."""
    # One _prepare call feeds both the faces and the walls, so they agree
    # vertex for vertex -- which is what makes the result watertight.
    rings, bridges = _prepare(outer, holes)
    poly = _merge(rings, bridges)

    tris = []
    for a, b, c in _earclip(poly):
        tris.append(((a[0], a[1], z1), (b[0], b[1], z1), (c[0], c[1], z1)))
        tris.append(((a[0], a[1], z0), (c[0], c[1], z0), (b[0], b[1], z0)))

    for ring in rings:
        n = len(ring)
        for i in range(n):
            px, py = ring[i]
            qx, qy = ring[(i + 1) % n]
            tris.append(((px, py, z0), (qx, qy, z0), (qx, qy, z1)))
            tris.append(((px, py, z0), (qx, qy, z1), (px, py, z1)))
    return tris


def _matmul(m, v):
    return tuple(sum(m[r][c] * v[c] for c in range(3)) for r in range(3))


def rot(axis: str, deg: float):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    if axis == "x":
        return ((1, 0, 0), (0, c, -s), (0, s, c))
    if axis == "y":
        return ((c, 0, s), (0, 1, 0), (-s, 0, c))
    return ((c, -s, 0), (s, c, 0), (0, 0, 1))


def transform(tris, rots=(), move=(0.0, 0.0, 0.0)):
    """Apply rotations in order, then translate."""
    out = []
    for tri in tris:
        new = []
        for p in tri:
            for axis, deg in rots:
                p = _matmul(rot(axis, deg), p)
            new.append((p[0] + move[0], p[1] + move[1], p[2] + move[2]))
        out.append(tuple(new))
    return out


# --------------------------------------------------------------------------
# STL output
# --------------------------------------------------------------------------


def _normal(tri):
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = tri
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    m = math.sqrt(nx * nx + ny * ny + nz * nz)
    return (0.0, 0.0, 0.0) if m < 1e-12 else (nx / m, ny / m, nz / m)


def write_stl(path, tris, name="part"):
    with open(path, "wb") as f:
        f.write(name.encode().ljust(80, b"\0")[:80])
        f.write(struct.pack("<I", len(tris)))
        for tri in tris:
            f.write(struct.pack("<3f", *_normal(tri)))
            for p in tri:
                f.write(struct.pack("<3f", *p))
            f.write(struct.pack("<H", 0))
    return len(tris)


def is_watertight(tris, tol=5):
    """Every directed edge used exactly once, and paired with its reverse."""
    edges = {}
    for tri in tris:
        for i in range(3):
            a = tuple(round(v, tol) for v in tri[i])
            b = tuple(round(v, tol) for v in tri[(i + 1) % 3])
            if a == b:
                return False, "degenerate edge"
            key = (a, b)
            if key in edges:
                return False, f"edge used twice: {key}"
            edges[key] = True
    for a, b in edges:
        if (b, a) not in edges:
            return False, f"unpaired edge: {(a, b)}"
    return True, "ok"


# --------------------------------------------------------------------------
# The parts
# --------------------------------------------------------------------------


def hip_positions():
    return [
        (HIP_X, HIP_Y, 45.0),    # front-left
        (HIP_X, -HIP_Y, -45.0),  # front-right
        (-HIP_X, HIP_Y, 135.0),  # rear-left
        (-HIP_X, -HIP_Y, -135.0),
    ]


def chassis_plate():
    """Main body plate: four coxa servos drop through it, Pi bolts on top."""
    outer = rounded_rect(0, 0, BODY_L, BODY_W, 8.0)
    holes = []
    for hx, hy, ang in hip_positions():
        holes += servo_pocket(hx, hy, ang)
    px, py = PI5_HOLES[0] / 2, PI5_HOLES[1] / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            holes.append(circle(sx * px, sy * py, M25))
    # Cable pass-throughs fore and aft of the electronics.
    holes.append(rounded_rect(0, 38.0, 30.0, 6.0, 3.0, cw=True))
    holes.append(rounded_rect(0, -38.0, 30.0, 6.0, 3.0, cw=True))
    return extrude(outer, holes, 0, PLATE_T)


# Coxa bracket wall. Height is set by the servo's screw spacing, not by the
# link length: the holes sit +-13.9mm from the pocket centre, so anything
# under ~34mm tall pushes a mounting hole off the edge of the part.
COXA_WALL_H = 40.0
_SHAFT_OFF = POCKET_L / 2 - SERVO_SHAFT_FROM_END  # pocket centre -> output shaft


def coxa_bracket():
    """L-bracket: bolts to the coxa horn, carries the femur servo vertically."""
    base = extrude(rounded_rect(0, 0, 30.0, 26.0, 4.0), horn_holes(0, 0), 0, PLATE_T)

    # In wall-local coordinates +y becomes +z once stood up, so place the
    # pocket such that the femur servo's shaft lands COXA_LEN above the base.
    pocket_cy = (COXA_LEN - COXA_WALL_H / 2) - _SHAFT_OFF
    wall = extrude(
        rounded_rect(0, 0, 30.0, COXA_WALL_H, 4.0),
        servo_pocket(0, pocket_cy, 90.0),
        0,
        PLATE_T,
    )
    # Stand it along the -Y edge, overlapping the base by 1.5mm so the two
    # prisms fuse into one solid at slice time instead of merely touching.
    wall = transform(
        wall, rots=[("x", 90.0)], move=(0.0, -13.0 + 1.5, COXA_WALL_H / 2)
    )
    return base + wall


def femur():
    """Thigh: femur horn at one end, knee servo pocket at the other."""
    outer = capsule(0, 0, FEMUR_LEN, 0, 24.0)
    holes = horn_holes(0, 0)
    holes += servo_pocket(FEMUR_LEN - SERVO_SHAFT_FROM_END + 2.0, 0, 0.0)
    return extrude(outer, holes, 0, PLATE_T)


def tibia():
    """Shin: knee horn at the top, tapering to a foot."""
    outer = capsule(0, 0, TIBIA_LEN, 0, 20.0)
    holes = horn_holes(0, 0)
    # Lightening slot down the middle of the shin.
    holes.append(capsule(22.0, 0, TIBIA_LEN - 16.0, 0, 7.0, cw=True))
    return extrude(outer, holes, 0, PLATE_T)


def face_bezel():
    """Front panel: window for the rectangular display, two camera-side slots."""
    outer = rounded_rect(0, 0, 52.0, 38.0, 4.0)
    holes = [rounded_rect(0, 0, 30.0, 22.0, 2.0, cw=True)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            holes.append(circle(sx * 22.0, sy * 15.0, M2))
    return extrude(outer, holes, 0, PLATE_T)


PARTS = {
    "chassis_plate": (chassis_plate, 1),
    "coxa_bracket": (coxa_bracket, 4),
    "femur": (femur, 4),
    "tibia": (tibia, 4),
    "face_bezel": (face_bezel, 1),
}


def leg_ik(reach: float, drop: float, l1: float = FEMUR_LEN, l2: float = TIBIA_LEN):
    """Two-link IK in the vertical plane of one leg.

    `reach` is the foot's horizontal distance out from the femur axis and
    `drop` is how far it sits below that axis. Returns (femur, knee) in
    degrees, both measured downward: femur below horizontal, knee as the
    angle the tibia is folded back from the femur's line.

    This is the same solve the walking gait needs, so the leg-IK simulator
    should be checked against it -- and against the same three link lengths.
    """
    d = math.hypot(reach, drop)
    if d > l1 + l2:
        raise ValueError(f"foot {d:.1f}mm away exceeds leg reach {l1 + l2:.1f}mm")
    if d < abs(l1 - l2):
        raise ValueError(f"foot {d:.1f}mm away is inside the leg's dead zone")
    clamp = lambda v: max(-1.0, min(1.0, v))
    knee_inner = math.acos(clamp((l1 * l1 + l2 * l2 - d * d) / (2 * l1 * l2)))
    off = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)))
    femur = math.atan2(drop, reach) - off
    return math.degrees(femur), math.degrees(math.pi - knee_inner)


def leg_fk(femur_deg: float, knee_deg: float, l1: float = FEMUR_LEN, l2: float = TIBIA_LEN):
    """Foot position (reach, drop) from joint angles -- the inverse of leg_ik."""
    a1 = math.radians(femur_deg)
    a2 = math.radians(femur_deg + knee_deg)
    return (l1 * math.cos(a1) + l2 * math.cos(a2), l1 * math.sin(a1) + l2 * math.sin(a2))


def assembly(reach: float = STAND_REACH, drop: float = STAND_H):
    """Posed whole robot, standing on its feet. For looking at, not printing."""
    femur_a, knee_a = leg_ik(reach, drop)
    tris = list(chassis_plate())

    for hx, hy, ang in hip_positions():
        leg = list(coxa_bracket())
        # Femur pivots about the axis COXA_LEN out from the hip, at wall height.
        f = transform(femur(), rots=[("y", femur_a)], move=(COXA_LEN, 0.0, COXA_LEN))
        kx = COXA_LEN + FEMUR_LEN * math.cos(math.radians(femur_a))
        kz = COXA_LEN - FEMUR_LEN * math.sin(math.radians(femur_a))
        t = transform(tibia(), rots=[("y", femur_a + knee_a)], move=(kx, 0.0, kz))
        leg += f + t
        tris += transform(leg, rots=[("z", ang)], move=(hx, hy, PLATE_T))

    tris += transform(
        face_bezel(),
        rots=[("x", 90.0), ("z", 90.0)],
        move=(BODY_L / 2 - 4.0, 0.0, 22.0),
    )
    # Drop the whole robot so the feet rest on z = 0.
    low = min(p[2] for tri in tris for p in tri)
    return transform(tris, move=(0.0, 0.0, -low))


# --------------------------------------------------------------------------


def _point_in_ring(p, ring) -> bool:
    inside = False
    n = len(ring)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        if (a[1] > p[1]) != (b[1] > p[1]):
            x = a[0] + (p[1] - a[1]) / (b[1] - a[1]) * (b[0] - a[0])
            if x > p[0]:
                inside = not inside
    return inside


def check_profile(outer, holes, label):
    """Every hole must lie wholly inside the outer ring, and holes must not
    overlap each other. Both are design errors -- a screw hole that runs off
    the edge of a bracket, or two features that merge into one slot -- and
    they surface as an unhelpful triangulation exception if left unchecked."""
    problems = []
    for i, h in enumerate(holes):
        if not all(_point_in_ring(p, outer) for p in h):
            problems.append(f"{label}: hole {i} is not inside the outline")
    for i in range(len(holes)):
        for j in range(i + 1, len(holes)):
            if any(_point_in_ring(p, holes[j]) for p in holes[i]) or any(
                _point_in_ring(p, holes[i]) for p in holes[j]
            ):
                problems.append(f"{label}: holes {i} and {j} overlap")
    return problems


def profile_checks():
    """Design-rule checks on the raw profiles, before any meshing."""
    out = []

    outer = rounded_rect(0, 0, BODY_L, BODY_W, 8.0)
    holes = []
    for hx, hy, ang in hip_positions():
        holes += servo_pocket(hx, hy, ang)
    px, py = PI5_HOLES[0] / 2, PI5_HOLES[1] / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            holes.append(circle(sx * px, sy * py, M25))
    holes.append(rounded_rect(0, 38.0, 30.0, 6.0, 3.0, cw=True))
    holes.append(rounded_rect(0, -38.0, 30.0, 6.0, 3.0, cw=True))
    out += check_profile(outer, holes, "chassis_plate")

    pocket_cy = (COXA_LEN - COXA_WALL_H / 2) - _SHAFT_OFF
    out += check_profile(
        rounded_rect(0, 0, 30.0, COXA_WALL_H, 4.0),
        servo_pocket(0, pocket_cy, 90.0),
        "coxa_bracket wall",
    )
    out += check_profile(
        rounded_rect(0, 0, 30.0, 26.0, 4.0), horn_holes(0, 0), "coxa_bracket base"
    )

    fh = horn_holes(0, 0) + servo_pocket(FEMUR_LEN - SERVO_SHAFT_FROM_END + 2.0, 0, 0.0)
    out += check_profile(capsule(0, 0, FEMUR_LEN, 0, 24.0), fh, "femur")

    th = horn_holes(0, 0) + [capsule(22.0, 0, TIBIA_LEN - 16.0, 0, 7.0, cw=True)]
    out += check_profile(capsule(0, 0, TIBIA_LEN, 0, 20.0), th, "tibia")
    return out


def self_test():
    ok = True

    problems = profile_checks()
    if problems:
        for p in problems:
            print(f"  FAIL  {p}")
        ok = False
    else:
        print("  ok    all profiles: holes inside outline, no overlaps")

    # Triangulated area must equal outer area minus hole areas.
    outer = rounded_rect(0, 0, 60, 40, 5)
    holes = [circle(-15, 0, 8), circle(15, 0, 8), rect(0, 12, 10, 6, 30, cw=True)]
    want = abs(signed_area(outer)) - sum(abs(signed_area(h)) for h in holes)
    got = sum(abs(_tri_area2(*t)) / 2 for t in triangulate(outer, holes))
    if abs(want - got) > 1e-6 * max(1.0, want):
        print(f"  FAIL  triangulation area {got:.4f} != {want:.4f}")
        ok = False
    else:
        print(f"  ok    triangulation area {got:.2f} mm^2 matches analytic")

    # Every part must be a closed manifold.
    for name, (fn, _) in PARTS.items():
        tris = fn()
        good, why = is_watertight(tris)
        print(f"  {'ok   ' if good else 'FAIL '} {name}: {len(tris)} triangles, {why}")
        ok = ok and good

    # IK must round-trip through FK across the whole working envelope.
    worst = 0.0
    for r in (-20.0, 0.0, 10.0, 30.0, 60.0):
        for d in (30.0, 55.0, 70.0, 90.0):
            try:
                a1, a2 = leg_ik(r, d)
            except ValueError:
                continue
            fr, fd = leg_fk(a1, a2)
            worst = max(worst, math.hypot(fr - r, fd - d))
    if worst > 1e-9:
        print(f"  FAIL  IK/FK round-trip off by {worst:.2e}mm")
        ok = False
    else:
        print(f"  ok    IK/FK round-trip exact over the working envelope")

    # The design stance must be reachable, and not at full stretch -- a leg
    # standing at full extension has no travel left to lift or push with.
    span = FEMUR_LEN + TIBIA_LEN
    need = math.hypot(STAND_REACH, STAND_H)
    if need > 0.92 * span:
        print(f"  FAIL  stance needs {need:.1f}mm of a {span:.0f}mm leg -- too straight")
        ok = False
    else:
        a1, a2 = leg_ik(STAND_REACH, STAND_H)
        print(
            f"  ok    stance {need:.0f}mm of {span:.0f}mm reach "
            f"(femur {a1:.0f}deg, knee {a2:.0f}deg)"
        )

    # Servo pockets must not run off the plate.
    for hx, hy, ang in hip_positions():
        for ring in servo_pocket(hx, hy, ang):
            for x, y in ring:
                if abs(x) > BODY_L / 2 - 1 or abs(y) > BODY_W / 2 - 1:
                    print(f"  FAIL  hip pocket at ({hx},{hy}) runs off the plate")
                    ok = False
                    break
    else:
        print(f"  ok    all four hip pockets inside the {BODY_L:.0f}x{BODY_W:.0f} plate")

    return ok


def main():
    if "--test" in sys.argv:
        sys.exit(0 if self_test() else 1)

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "stl")
    os.makedirs(out, exist_ok=True)

    print("self-test:")
    if not self_test():
        print("\ngeometry self-test failed -- not writing STL")
        sys.exit(1)

    print("\nwriting:")
    total = 0
    for name, (fn, qty) in PARTS.items():
        tris = fn()
        path = os.path.join(out, f"{name}.stl")
        n = write_stl(path, tris, name)
        total += n
        print(f"  {name+'.stl':24} {n:6d} triangles   print {qty}x")

    tris = assembly()
    path = os.path.join(out, "assembly_preview.stl")
    n = write_stl(path, tris, "enforcer assembly")
    print(f"  {'assembly_preview.stl':24} {n:6d} triangles   (view only)")
    print(f"\n{total + n} triangles total in {out}")


if __name__ == "__main__":
    main()
