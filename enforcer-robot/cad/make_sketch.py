#!/usr/bin/env python3
"""
Draw SKETCH.svg -- dimensioned views of The Enforcer.

Every coordinate comes from the constants in make_stl.py, so the drawing
cannot drift away from the STLs it documents. Regenerate after any dimension
change:

    python3 make_sketch.py
"""

import math
import os

import make_stl as E

S = 2.3          # px per mm
PAD = 34


def mm(v):
    return v * S


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Draw:
    def __init__(self):
        self.o = []

    def add(self, s):
        self.o.append(s)

    def poly(self, pts, cls="part", close=True):
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        tag = "polygon" if close else "polyline"
        self.add(f'<{tag} class="{cls}" points="{d}"/>')

    def circ(self, x, y, r, cls="cut"):
        self.add(f'<circle class="{cls}" cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}"/>')

    def line(self, x1, y1, x2, y2, cls="dim"):
        self.add(
            f'<line class="{cls}" x1="{x1:.2f}" y1="{y1:.2f}" '
            f'x2="{x2:.2f}" y2="{y2:.2f}"/>'
        )

    def text(self, x, y, s, cls="lbl", anchor="middle"):
        self.add(
            f'<text class="{cls}" x="{x:.2f}" y="{y:.2f}" '
            f'text-anchor="{anchor}">{esc(s)}</text>'
        )

    def title(self, x, y, s, sub=""):
        self.add(f'<text class="ttl" x="{x:.2f}" y="{y:.2f}">{esc(s)}</text>')
        if sub:
            self.add(f'<text class="sub" x="{x:.2f}" y="{y + 15:.2f}">{esc(sub)}</text>')

    # horizontal dimension with arrow ticks
    def dim_h(self, x1, x2, y, label):
        self.line(x1, y, x2, y, "dim")
        for x in (x1, x2):
            self.line(x, y - 4, x, y + 4, "dim")
        self.text((x1 + x2) / 2, y - 6, label, "dimtxt")

    def dim_v(self, y1, y2, x, label):
        self.line(x, y1, x, y2, "dim")
        for y in (y1, y2):
            self.line(x - 4, y, x + 4, y, "dim")
        self.add(
            f'<text class="dimtxt" x="{x - 7:.2f}" y="{(y1 + y2) / 2:.2f}" '
            f'text-anchor="middle" transform="rotate(-90 {x - 7:.2f} '
            f'{(y1 + y2) / 2:.2f})">{esc(label)}</text>'
        )


def panel_top(d, ox, oy):
    """Chassis plate, true scale, looking down."""
    d.title(ox - mm(E.BODY_L / 2), oy - mm(E.BODY_W / 2) - 26,
            "TOP — chassis plate",
            f"{E.BODY_L:.0f} x {E.BODY_W:.0f} x {E.PLATE_T:.0f} mm, printed flat")

    def T(p):
        return (ox + mm(p[0]), oy - mm(p[1]))

    d.poly([T(p) for p in E.rounded_rect(0, 0, E.BODY_L, E.BODY_W, 8.0)], "part")

    for hx, hy, ang in E.hip_positions():
        for ring in E.servo_pocket(hx, hy, ang):
            d.poly([T(p) for p in ring], "cut")
        d.circ(*T((hx, hy)), 3.0, "axis")
        d.text(*[v for v in T((hx, hy - 17))], "coxa", "tiny")

    px, py = E.PI5_HOLES[0] / 2, E.PI5_HOLES[1] / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            d.circ(*T((sx * px, sy * py)), mm(E.M25 / 2), "cut")
    d.poly([T(p) for p in E.rounded_rect(0, 0, *E.PI5_HOLES, 2)], "ghost")
    d.text(ox, oy + 5, "Raspberry Pi", "tiny")
    d.text(ox, oy + 18, "(PCA9685 stacks above)", "tiny")

    for sy in (-1, 1):
        d.poly([T(p) for p in E.rounded_rect(0, sy * 38.0, 30.0, 6.0, 3.0)], "cut")

    d.dim_h(ox - mm(E.BODY_L / 2), ox + mm(E.BODY_L / 2),
            oy + mm(E.BODY_W / 2) + 30, f"{E.BODY_L:.0f}")
    d.dim_v(oy - mm(E.BODY_W / 2), oy + mm(E.BODY_W / 2),
            ox - mm(E.BODY_L / 2) - 22, f"{E.BODY_W:.0f}")
    d.dim_h(ox - mm(E.HIP_X), ox + mm(E.HIP_X),
            oy - mm(E.BODY_W / 2) - 8, f"hips {2 * E.HIP_X:.0f}")


def panel_leg(d, ox, oy):
    """One leg in its own vertical plane -- true lengths and joint angles."""
    a1, a2 = E.leg_ik(E.STAND_REACH, E.STAND_H)
    d.title(ox - 30, oy - mm(E.COXA_LEN) - 66,
            "LEG — true lengths, standing pose",
            f"3 joints x 4 legs = 12 x MG90S")

    hip = (ox, oy)
    fem = (ox + mm(E.COXA_LEN), oy - mm(E.COXA_LEN))
    knee = (fem[0] + mm(E.FEMUR_LEN * math.cos(math.radians(a1))),
            fem[1] + mm(E.FEMUR_LEN * math.sin(math.radians(a1))))
    foot = (knee[0] + mm(E.TIBIA_LEN * math.cos(math.radians(a1 + a2))),
            knee[1] + mm(E.TIBIA_LEN * math.sin(math.radians(a1 + a2))))

    # ground and body
    d.line(ox - 60, foot[1], ox + 250, foot[1], "ground")
    d.text(ox - 60, foot[1] + 18, "desk", "tiny", "start")
    d.poly([(ox - 60, oy), (ox + 20, oy), (ox + 20, oy - mm(E.PLATE_T)),
            (ox - 60, oy - mm(E.PLATE_T))], "part")
    d.text(ox - 34, oy - 12, "body", "tiny")

    for a, b, cls in ((hip, fem, "link"), (fem, knee, "link"), (knee, foot, "link")):
        d.line(a[0], a[1], b[0], b[1], cls)

    for p, name in ((hip, "coxa"), (fem, "femur"), (knee, "knee")):
        d.circ(p[0], p[1], 7, "joint")
    d.circ(foot[0], foot[1], 4, "axis")

    d.text(hip[0] - 22, hip[1] + 6, "coxa", "tiny", "end")
    d.text(hip[0] - 22, hip[1] + 19, "(yaw)", "tiny", "end")
    d.text(fem[0] + 4, fem[1] - 14, "femur (pitch)", "tiny", "start")
    d.text(knee[0] + 12, knee[1] - 8, "knee", "tiny", "start")
    d.text(foot[0], foot[1] + 20, "foot", "tiny")

    mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    m = mid(hip, fem)
    d.text(m[0] - 16, m[1] - 6, f"{E.COXA_LEN:.0f}", "len", "end")
    m = mid(fem, knee)
    d.text(m[0], m[1] - 12, f"{E.FEMUR_LEN:.0f}", "len")
    m = mid(knee, foot)
    d.text(m[0] + 20, m[1], f"{E.TIBIA_LEN:.0f}", "len", "start")

    d.dim_v(oy, foot[1], ox + 250, f"ride height {E.STAND_H:.0f}")
    d.text(ox + 120, foot[1] + 40,
           f"femur {a1:.0f}° below horizontal, knee folded {a2:.0f}°", "tiny")
    d.text(ox + 120, foot[1] + 56,
           f"reach {E.FEMUR_LEN + E.TIBIA_LEN:.0f} mm — stance uses "
           f"{math.hypot(E.STAND_REACH, E.STAND_H):.0f}", "tiny")


def panel_front(d, ox, oy):
    """Front elevation: stance width, ride height, where the face sits."""
    a1, a2 = E.leg_ik(E.STAND_REACH, E.STAND_H)
    k = math.sin(math.radians(45.0))  # legs splay at 45deg, so foreshorten in Y

    d.title(ox - 210, oy - 150, "FRONT — stance",
            "legs splay 45°, so widths here are foreshortened")

    ground = oy
    plate_top = ground - mm(E.STAND_H * 0.72)

    d.line(ox - 250, ground, ox + 250, ground, "ground")
    d.poly([(ox - mm(E.BODY_W / 2), plate_top),
            (ox + mm(E.BODY_W / 2), plate_top),
            (ox + mm(E.BODY_W / 2), plate_top + mm(E.PLATE_T)),
            (ox - mm(E.BODY_W / 2), plate_top + mm(E.PLATE_T))], "part")

    # face display, sitting on the body front
    fw, fh = 52.0, 38.0
    d.poly([(ox - mm(fw / 2), plate_top - mm(fh)),
            (ox + mm(fw / 2), plate_top - mm(fh)),
            (ox + mm(fw / 2), plate_top),
            (ox - mm(fw / 2), plate_top)], "part")
    d.poly([(ox - mm(15), plate_top - mm(30)), (ox + mm(15), plate_top - mm(30)),
            (ox + mm(15), plate_top - mm(8)), (ox - mm(15), plate_top - mm(8))], "screen")
    for sx in (-1, 1):
        d.circ(ox + sx * mm(8), plate_top - mm(19), mm(3.4), "eye")
    d.text(ox, plate_top - mm(46), "face display", "tiny")

    for side in (-1, 1):
        hipy = side * mm(E.HIP_Y)
        fy = hipy + side * mm(E.COXA_LEN * k)
        fz = plate_top - mm(E.COXA_LEN)
        ky = fy + side * mm(E.FEMUR_LEN * math.cos(math.radians(a1)) * k)
        kz = fz + mm(E.FEMUR_LEN * math.sin(math.radians(a1)))
        ty = ky + side * mm(E.TIBIA_LEN * math.cos(math.radians(a1 + a2)) * k)
        tz = kz + mm(E.TIBIA_LEN * math.sin(math.radians(a1 + a2)))
        pts = [(ox + hipy, plate_top), (ox + fy, fz), (ox + ky, kz), (ox + ty, tz)]
        for i in range(3):
            d.line(*pts[i], *pts[i + 1], "link")
        for p in pts[:3]:
            d.circ(p[0], p[1], 6, "joint")
        d.circ(ox + ty, tz, 4, "axis")

    d.dim_v(plate_top, ground, ox - 250, "ride height")


def main():
    W, H = 1000, 1240
    d = Draw()
    d.add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
          f'width="100%" style="max-width:{W}px;height:auto">')
    d.add("""<style>
      .part   { fill:none; stroke:var(--ink); stroke-width:2.1; }
      .cut    { fill:var(--void); stroke:var(--ink); stroke-width:1.2; }
      .ghost  { fill:none; stroke:var(--faint); stroke-width:1.1;
                stroke-dasharray:5 4; }
      .link   { stroke:var(--accent); stroke-width:6; stroke-linecap:round; }
      .joint  { fill:var(--bg); stroke:var(--accent); stroke-width:2.6; }
      .axis   { fill:var(--accent); stroke:none; }
      .ground { stroke:var(--faint); stroke-width:2; stroke-dasharray:7 5; }
      .screen { fill:var(--screen); stroke:var(--ink); stroke-width:1.4; }
      .eye    { fill:var(--accent); stroke:none; }
      .dim    { stroke:var(--faint); stroke-width:1.1; }
      text    { font-family:ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;
                fill:var(--ink); }
      .ttl    { font-size:19px; font-weight:650; }
      .sub    { font-size:13px; fill:var(--faint); }
      .lbl    { font-size:13px; }
      .tiny   { font-size:12px; fill:var(--faint); }
      .len    { font-size:14px; font-weight:600; fill:var(--accent); }
      .dimtxt { font-size:12px; fill:var(--faint); }
      svg { --ink:#1c1c1f; --faint:#8a8a94; --accent:#d2691e; --bg:#ffffff;
            --void:#ececf0; --screen:#20222b; }
      @media (prefers-color-scheme: dark) {
        svg { --ink:#e9e9ee; --faint:#83838f; --accent:#ff9d4d; --bg:#16161a;
              --void:#26262c; --screen:#0e0f14; }
      }
      :root[data-theme="dark"] svg {
        --ink:#e9e9ee; --faint:#83838f; --accent:#ff9d4d; --bg:#16161a;
        --void:#26262c; --screen:#0e0f14;
      }
      :root[data-theme="light"] svg {
        --ink:#1c1c1f; --faint:#8a8a94; --accent:#d2691e; --bg:#ffffff;
        --void:#ececf0; --screen:#20222b;
      }
    </style>""")

    d.add(f'<text class="ttl" x="{PAD}" y="34" style="font-size:23px">'
          f'The Enforcer — quadruped, 12 servos</text>')
    d.add(f'<text class="sub" x="{PAD}" y="55">All dimensions mm. '
          f'Generated from make_stl.py — do not edit by hand.</text>')

    panel_top(d, W / 2, 250)
    panel_leg(d, 210, 660)
    panel_front(d, W / 2, 1180)

    d.add("</svg>")

    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "SKETCH.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(d.o))
    print(f"wrote {path}  ({len(d.o)} elements)")


if __name__ == "__main__":
    main()
