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

# Sesame provides the body. These are the dimensions of the *add-on* parts.
#
# !!! MEASURE YOUR PRINTED SESAME AND SET THESE TWO !!!
# Everything bolts to one payload deck, so the top cover footprint is the
# only upstream dimension this file depends on. One unknown, not ten.
DECK_L = 90.0               # along the robot's spine
DECK_W = 60.0               # across

PLATE_T = 3.0               # standard printed plate thickness
M2 = 2.2                    # clearance holes
M25 = 2.7
M3 = 3.2

GRID_PITCH = 12.0           # mounting grid on the deck
GRID_COLS = 5
GRID_ROWS = 3

BOTTLE_D = 36.0             # reservoir diameter -- measure your bottle
TUBE_D = 4.5                # silicone tubing OD
TCRT_W = 10.6               # TCRT5000 module body
TCRT_H = 6.2

PIZERO_HOLES = (58.0, 23.0)  # Raspberry Pi Zero 2 W mounting pattern
CAM_HOLES = (21.0, 12.5)     # Raspberry Pi camera module mounting pattern

# Camera and nozzle both point this far above horizontal. They must match:
# the robot yaws to aim, so horizontal centring is the only closed loop, and
# the vertical angle is a mechanical decision made once, here.
#
# The robot stands ~10cm tall on a desk and the target is a seated person's
# torso, so the aim is slightly *up*. Never level with a face -- see the
# safety section of README.md.
NOZZLE_TILT = 20.0

# Torque budget for restyling the legs. MG90S is rated 1.8 kg-cm at 4.8V and
# 2.2 at 6V; derate hard, because a servo held at its rating cooks and a
# quadruped holds a pose continuously rather than in bursts.
MG90S_STALL_KGCM = 2.2
SERVO_DERATE = 0.55         # usable fraction of stall for a sustained hold

# !!! ESTIMATE -- WEIGH YOUR SESAME AND REPLACE !!!
SESAME_MASS_G = 380.0
# Worst case during a crawl gait: the body shifts its weight to free a leg,
# so one leg momentarily carries roughly half the machine.
WORST_LEG_SHARE = 0.5

PHONE_G = 180.0             # a typical phone -- roughly half of Sesame again

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
#
# Sesame supplies the body, the legs, and the face. These are the pieces it
# does not have, because it was never meant to carry water: a payload deck
# that straps to its top cover, and the Enforcer hardware that bolts to that
# deck. Nothing here modifies a Sesame part, so its build guide stays valid
# and you never have to re-print an upstream component.
# --------------------------------------------------------------------------


def joint_torque_kgcm(mass_g: float, reach_mm: float,
                     share: float = WORST_LEG_SHARE) -> float:
    """Peak sustained torque at one hip, in kg-cm.

    Torque is force times lever arm, and the lever arm is the *horizontal*
    distance from the joint to the foot -- which is what changes when you
    restyle the legs longer or splay them wider for a spider stance. Both
    cost torque linearly, and MG90S has very little to give.
    """
    return (mass_g * share / 1000.0) * (reach_mm / 10.0)


def max_reach_mm(mass_g: float, share: float = WORST_LEG_SHARE) -> float:
    """How far out a foot may sit before MG90S runs out of derated torque."""
    budget = MG90S_STALL_KGCM * SERVO_DERATE
    return budget / (mass_g * share / 1000.0) * 10.0


def payload_cases():
    """Loaded mass and reach limit for each way the robot can be configured.

    This is the table that decides whether Warden can carry a phone. It
    cannot: a phone is ~half of Sesame's own mass, and the torque needed at
    any usable stance is past what MG90S can hold. See BEHAVIOURS.md.
    """
    deck_pi_cam = 30.0 + 11.0 + 5.0     # printed parts, Pi Zero, camera
    rig = 20.0                          # pump + tubing
    water = lambda ml: float(ml)        # 1 g/ml
    return [
        ("bare Sesame", 0.0),
        ("+ deck, Pi Zero, camera", deck_pi_cam),
        ("+ water rig, 50ml", deck_pi_cam + rig + water(50)),
        ("+ water rig, 100ml", deck_pi_cam + rig + water(100)),
        ("Warden CARRYING a phone", deck_pi_cam + PHONE_G),
        ("Warden carrying phone + 50ml", deck_pi_cam + rig + water(50) + PHONE_G),
    ]


def grid_holes(cols=GRID_COLS, rows=GRID_ROWS, pitch=GRID_PITCH, d=M3):
    """Mounting grid. Every add-on lines up to this, so the reservoir can move
    fore/aft after you weigh the robot and find the balance point."""
    out = []
    for i in range(cols):
        for j in range(rows):
            x = (i - (cols - 1) / 2) * pitch
            y = (j - (rows - 1) / 2) * pitch
            out.append(circle(x, y, d))
    return out


def strap_slots():
    """Zip-tie slots. Sesame's own build uses zip ties and underside channels,
    so strapping the deck on matches how the robot is already assembled --
    and it means no screws into upstream parts."""
    return [
        rounded_rect(sx * 30.0, sy * 26.0, 14.0, 3.5, 1.7, cw=True)
        for sx in (-1, 1)
        for sy in (-1, 1)
    ]


def pi_zero_holes():
    """The brain bolts straight to the deck -- no separate carrier part."""
    px, py = PIZERO_HOLES[0] / 2, PIZERO_HOLES[1] / 2
    return [circle(sx * px, sy * py, M25) for sx in (-1, 1) for sy in (-1, 1)]


def payload_deck():
    """The one part that touches Sesame. Everything else bolts to this."""
    return extrude(
        rounded_rect(0, 0, DECK_L, DECK_W, 5.0),
        grid_holes() + strap_slots() + pi_zero_holes(),
        0,
        PLATE_T,
    )


def _cradle_profile(w, h, bottle_d, seg=20):
    """Rectangle with a semicircular bite out of the top edge, CCW.

    Built as an outline rather than as a hole: the bottle drops in from
    above, so the notch has to be open at the top.
    """
    r = bottle_d / 2.0
    cy = h / 2.0
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2)]
    # arc from the right lip down through the notch and up to the left lip
    for i in range(seg + 1):
        a = 2 * math.pi * (i / seg) * 0.5  # 0 .. pi
        pts.append((r * math.cos(a), cy - r * math.sin(a)))
    pts.append((-w / 2, h / 2))
    return pts


def reservoir_cradle():
    """Print 2. Bottle drops in and gets zip-tied down through the slots."""
    prof = _cradle_profile(50.0, 30.0, BOTTLE_D)
    holes = [circle(sx * 20.0, -8.0, M3) for sx in (-1, 1)]
    return extrude(prof, holes, 0, PLATE_T)


def _wall_normal(tilt: float):
    """Direction a tilted _l_bracket wall faces: forward and `tilt` degrees up."""
    t = math.radians(tilt)
    return (0.0, -math.cos(t), math.sin(t))


def _l_bracket(base_w, base_d, wall_w, wall_h, base_holes, wall_holes, tilt=0.0):
    """Base plate in XY, plus a wall standing along its -Y edge.

    `tilt` leans the wall back so whatever it carries points that many
    degrees above horizontal. Rotating by (90 - tilt) about X puts the wall's
    face normal at (0, -cos t, +sin t) -- forward and up. Use (90 + tilt) and
    it aims at the floor instead.

    The wall overlaps the base by 1.5mm rather than merely touching it, so
    the two prisms fuse into one solid when the slicer unions them.
    """
    tris = extrude(rounded_rect(0, 0, base_w, base_d, 3.0), base_holes, 0, PLATE_T)
    wall = extrude(rounded_rect(0, 0, wall_w, wall_h, 3.0), wall_holes, 0, PLATE_T)
    wall = transform(
        wall,
        rots=[("x", 90.0 - tilt)],
        move=(0.0, -base_d / 2 + 1.5, wall_h / 2),
    )
    return tris + wall


def nozzle_mount():
    """Holds the tubing at NOZZLE_TILT above horizontal, at the deck's front
    edge. Aimed at a seated person's torso -- never at a face."""
    return _l_bracket(
        24.0, 18.0, 24.0, 22.0,
        [circle(sx * 8.0, -4.0, M3) for sx in (-1, 1)],
        [circle(0.0, 2.0, TUBE_D)],
        tilt=NOZZLE_TILT,
    )


def camera_mount():
    """Carries the Pi camera at the same tilt as the nozzle.

    Both looking the same way is the whole trick: the robot turns until the
    target is centred in frame, and the nozzle is then pointed at it. Get
    these two angles out of step and the robot aims high or low by exactly
    the difference.
    """
    cx, cy = CAM_HOLES[0] / 2, CAM_HOLES[1] / 2
    return _l_bracket(
        30.0, 18.0, 30.0, 26.0,
        [circle(sx * 11.0, -4.0, M3) for sx in (-1, 1)],
        [circle(sx * cx, sy * cy, M2) for sx in (-1, 1) for sy in (-1, 1)]
        + [rounded_rect(0.0, 0.0, 10.0, 10.0, 1.5, cw=True)],
        tilt=NOZZLE_TILT,
    )


def cliff_bracket():
    """Print 4. Holds a TCRT5000 facing down past the edge of the deck."""
    return _l_bracket(
        18.0, 14.0, 18.0, 16.0,
        [circle(sx * 5.5, -3.5, M2) for sx in (-1, 1)],
        [rounded_rect(0.0, 1.0, TCRT_W, TCRT_H, 1.0, cw=True)],
    )


def phone_tray():
    """Warden mode. A lip at each end so the phone can't slide off when the
    robot walks away with it."""
    tris = extrude(rounded_rect(0, 0, 85.0, 48.0, 4.0), grid_holes(3, 2, 20.0), 0, PLATE_T)
    for sx in (-1, 1):
        lip = extrude(rounded_rect(0, 0, 48.0, 10.0, 2.0), [], 0, PLATE_T)
        lip = transform(
            lip,
            rots=[("x", 90.0), ("z", 90.0)],
            move=(sx * (85.0 / 2 - 1.5), 0.0, 5.0),
        )
        tris += lip
    return tris


PARTS = {
    "payload_deck": (payload_deck, 1),
    "reservoir_cradle": (reservoir_cradle, 2),
    "nozzle_mount": (nozzle_mount, 1),
    "camera_mount": (camera_mount, 1),
    "cliff_bracket": (cliff_bracket, 4),
    "phone_tray": (phone_tray, 1),
}


# --------------------------------------------------------------------------
# Checks
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
    """Every hole must lie wholly inside the outline, and holes must not
    overlap each other. Both are design errors -- a screw hole running off the
    edge of a bracket, or two features merging into one slot -- and they
    otherwise surface as an unhelpful triangulation exception."""
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
    out = []
    out += check_profile(
        rounded_rect(0, 0, DECK_L, DECK_W, 5.0),
        grid_holes() + strap_slots() + pi_zero_holes(),
        "payload_deck",
    )
    out += check_profile(
        _cradle_profile(50.0, 30.0, BOTTLE_D),
        [circle(sx * 20.0, -8.0, M3) for sx in (-1, 1)],
        "reservoir_cradle",
    )
    out += check_profile(
        rounded_rect(0, 0, 24.0, 22.0, 3.0), [circle(0.0, 2.0, TUBE_D)], "nozzle wall"
    )
    cx, cy = CAM_HOLES[0] / 2, CAM_HOLES[1] / 2
    out += check_profile(
        rounded_rect(0, 0, 30.0, 26.0, 3.0),
        [circle(sx * cx, sy * cy, M2) for sx in (-1, 1) for sy in (-1, 1)]
        + [rounded_rect(0.0, 0.0, 10.0, 10.0, 1.5, cw=True)],
        "camera wall",
    )
    out += check_profile(
        rounded_rect(0, 0, 18.0, 16.0, 3.0),
        [rounded_rect(0.0, 1.0, TCRT_W, TCRT_H, 1.0, cw=True)],
        "cliff wall",
    )
    out += check_profile(
        rounded_rect(0, 0, 85.0, 48.0, 4.0), grid_holes(3, 2, 20.0), "phone_tray"
    )
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

    outer = rounded_rect(0, 0, 60, 40, 5)
    holes = [circle(-15, 0, 8), circle(15, 0, 8), rect(0, 12, 10, 6, 30, cw=True)]
    want = abs(signed_area(outer)) - sum(abs(signed_area(h)) for h in holes)
    got = sum(abs(_tri_area2(*t)) / 2 for t in triangulate(outer, holes))
    if abs(want - got) > 1e-6 * max(1.0, want):
        print(f"  FAIL  triangulation area {got:.4f} != {want:.4f}")
        ok = False
    else:
        print(f"  ok    triangulation area {got:.2f} mm^2 matches analytic")

    for name, (fn, _) in PARTS.items():
        tris = fn()
        good, why = is_watertight(tris)
        print(f"  {'ok   ' if good else 'FAIL '} {name}: {len(tris)} triangles, {why}")
        ok = ok and good

    # The deck must not be wider than the robot it straps to.
    if DECK_L > 140 or DECK_W > 100:
        print(f"  FAIL  deck {DECK_L}x{DECK_W} is implausibly large for a mini quadruped")
        ok = False
    else:
        print(f"  ok    deck {DECK_L:.0f}x{DECK_W:.0f}mm (MEASURE your Sesame and confirm)")

    # Camera and nozzle must point the same way, or "centred in frame" stops
    # meaning "aimed". Both come from NOZZLE_TILT, so this guards against
    # someone giving the camera its own angle later.
    cam_n = _wall_normal(NOZZLE_TILT)
    noz_n = _wall_normal(NOZZLE_TILT)
    err = math.degrees(math.acos(max(-1.0, min(1.0, sum(a * b for a, b in zip(cam_n, noz_n))))))
    if err > 1e-9:
        print(f"  FAIL  camera and nozzle differ by {err:.2f}deg")
        ok = False
    elif not 5.0 <= NOZZLE_TILT <= 35.0:
        print(f"  FAIL  nozzle tilt {NOZZLE_TILT}deg is outside the safe 5-35deg band")
        ok = False
    else:
        print(f"  ok    camera and nozzle both +{NOZZLE_TILT:.0f}deg above horizontal")

    # Payload budget. Weigh your Sesame; these are the parts you are adding.
    water_g = math.pi * (BOTTLE_D / 2) ** 2 * 60.0 / 1000.0  # 60mm fill, 1g/ml
    payload = {
        "water": water_g,
        "printed parts": 30.0,
        "Pi Zero 2 W": 11.0,
        "camera + ribbon": 5.0,
        "pump + tubing": 20.0,
    }
    total = sum(payload.values())
    if water_g > 120:
        print(f"  FAIL  {BOTTLE_D:.0f}mm bottle holds {water_g:.0f}g -- too heavy")
        ok = False
    else:
        parts = ", ".join(f"{k} {v:.0f}g" for k, v in payload.items())
        print(f"  ok    payload {total:.0f}g  ({parts})")
        print(f"        WEIGH your Sesame -- this has to walk on 8x MG90S")

    # How much leg restyling the servos will actually tolerate.
    payload_g = sum(payload.values())
    total_g = SESAME_MASS_G + payload_g
    limit = max_reach_mm(total_g)
    print(f"  ok    at {total_g:.0f}g loaded, a foot may sit {limit:.0f}mm out "
          f"from its hip")
    print(f"        (MG90S {MG90S_STALL_KGCM} kg-cm derated to "
          f"{SERVO_DERATE:.0%} for a sustained hold)")
    for reach in (50.0, 60.0, 70.0, 80.0, 90.0):
        t = joint_torque_kgcm(total_g, reach)
        flag = "OK " if reach <= limit else "OVER"
        print(f"        {flag} {reach:.0f}mm reach -> {t:.2f} kg-cm")
    print(f"        SESAME_MASS_G is an ESTIMATE -- weigh yours and re-run")

    # Which configurations the servos can actually hold up.
    budget = MG90S_STALL_KGCM * SERVO_DERATE
    print(f"  --    payload cases (budget {budget:.2f} kg-cm at 48mm reach):")
    warden_carry_fails = False
    for name, extra in payload_cases():
        m = SESAME_MASS_G + extra
        t = joint_torque_kgcm(m, 48.0)
        over = t > budget
        if over and "CARRYING" in name:
            warden_carry_fails = True
        print(f"        {'OVER' if over else 'ok  '} {name:32} {m:5.0f}g  "
              f"reach<={max_reach_mm(m):4.0f}mm  {t:.2f} kg-cm")
    if not warden_carry_fails:
        print("  FAIL  the phone-carrying case is supposed to be over budget --")
        print("        if it now passes, BEHAVIOURS.md's Warden design is stale")
        ok = False
    else:
        print("  ok    phone-carrying is over budget, so Warden is guard-and-block")

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
        n = write_stl(os.path.join(out, f"{name}.stl"), tris, name)
        total += n
        print(f"  {name+'.stl':24} {n:6d} triangles   print {qty}x")
    print(f"\n{total} triangles total in {out}")


if __name__ == "__main__":
    main()
