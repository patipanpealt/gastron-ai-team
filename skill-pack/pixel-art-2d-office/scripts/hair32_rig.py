"""Character kit v5 — HAIR in 3D, seen from the front (S), back (N) and side (W; E = W mirrored).

The six approved front styles (hair32_front.py) are re-expressed as 3D: each style is a SHELL (the
skull cap, with a hairline that wraps around the head), a set of locks (3D curved strokes) and, for long
styles, hair that hangs behind the body. The front view is rendered with the very same 2D primitives and
the same shading code as before, so the approved look is preserved; the back and side views come from
projecting the same 3D description, so every lock stays where it belongs.

  Shell   an ellipsoid whose cross-section morphs from the front-cap ellipse (top of the head) to the
          head ellipse (back / nape); a hairline height that depends on the angle around the head
          (forehead -> temple -> nape) clips it.
  Lock    quadratic curve with 3D control points; front-view (x, y) are the approved 2D points and z is
          lifted onto the skull so side views place them on the head surface.
  Layers  front = drawn over the body / face; back = drawn behind the body (hair hanging behind).

All hair is rendered at head offset 0; the sheet builder shifts the finished layer with the head bob.
"""
import numpy as np
from PIL import Image

import character32_front as B
import hair32_front as H0
from hair32_front import Prim

W, H, PX, PY = B.W, B.H, B.PX, B.PY
CX = 15.5
RZ = 0.93  # head depth / width ratio of the hair shell


def smooth(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def lift(x, y):
    """Depth (z) of a point on the skull surface seen from the front, with a little hair thickness."""
    d = 1 - ((x - CX) / 13.0) ** 2 - ((y - 32.0) / 12.0) ** 2
    return max(1.2, 11.8 * np.sqrt(max(d, 0.0)) + 0.6)


def view_pt(view, X, Y, Z):
    if view == "S":
        return X, Y, Z
    if view == "N":
        return 31.0 - X, Y, -Z
    return CX - Z, Y, X - CX


# ---- style DSL ------------------------------------------------------------------------------------------
def shell(rx, ry, cy, yf, arch=0.0, ys=34.0, yn=42.5, ear=True):
    return ("shell", dict(rx=rx, ry=ry, cy=cy, yf=yf, arch=arch, ys=ys, yn=yn, ear=ear))


def S(p0, p1, p2, r0, r1, zs=None):
    pts = [p0, p1, p2]
    zs = zs or [lift(*p) for p in pts]
    return ("s3", [(p[0], p[1], z) for p, z in zip(pts, zs)], r0, r1)


def P(p0, p1, p2, r0, r1):
    m = lambda p: (31 - p[0], p[1])  # noqa: E731
    return [S(p0, p1, p2, r0, r1), S(m(p0), m(p1), m(p2), r0, r1)]


def B3(cx, cy, rx, ry, cz=None, rz=None, ymax=None):
    cz = lift(cx, cy) if cz is None else cz
    return ("b3", dict(cx=cx, cy=cy, cz=cz, rx=rx, ry=ry, rz=rx * 0.55 if rz is None else rz, ymax=ymax))


def flat(items):
    out = []
    for it in items:
        out.extend(it if isinstance(it, list) else [it])
    return out


STYLES = {
    "neat": {"name": "Neat Short", "gender": "male", "front": flat([
        shell(13.8, 9.9, 29.4, 27.4, 0.02, ys=33.5, yn=41.5),
        P((5.2, 24.5), (3.7, 28), (4.3, 32.3), 2.7, 1.3),
        S((11, 20.5), (6.8, 21.2), (4.6, 26.5), 3.1, 1.8),
        S((11, 20.2), (18, 18.4), (25.6, 23.4), 3.4, 2.3),
        S((11, 23.0), (18, 21.6), (26.6, 27.4), 3.1, 1.7),
        S((9.6, 24.6), (10.8, 27.4), (12.0, 29.6), 2.5, 0.9),
        S((13.8, 24.4), (15.2, 27.4), (16.4, 29.4), 2.5, 0.9),
        S((18.0, 24.4), (19.6, 27.0), (20.8, 28.8), 2.3, 0.9),
        S((22.0, 24.6), (23.6, 26.6), (24.4, 28.4), 2.0, 0.8),
    ])},
    "sidepart": {"name": "Classic Side Part", "gender": "male", "front": flat([
        shell(14.0, 10.2, 29.2, 26.8, 0.024, ys=33.5, yn=41.5),
        P((5.0, 25.5), (3.8, 28.6), (4.4, 32.4), 2.5, 1.1),
        S((10.2, 20.2), (6.4, 21.8), (4.4, 27.8), 3.0, 1.7),
        S((10.6, 19.2), (19, 16.9), (26.8, 23.8), 3.9, 2.5),
        S((10.6, 22.0), (19, 20.1), (27.4, 28.0), 3.4, 1.7),
        S((11.0, 23.6), (16.6, 22.2), (21.6, 24.6), 2.2, 1.0),
        S((10.4, 24.2), (15.6, 26.6), (23.4, 30.8), 3.0, 1.0),
    ])},
    "up": {"name": "Short Lifted Front", "gender": "male", "front": flat([
        shell(14.0, 10.4, 29.4, 25.8, 0.034, ys=33.5, yn=41.5),
        B3(15.5, 22.4, 10.4, 5.0),
        S((9.2, 21.8), (7.4, 24.4), (6.8, 27.4), 1.7, 2.4),
        S((13.4, 20.2), (10.8, 23.2), (9.8, 26.8), 2.0, 2.8),
        S((17.6, 19.6), (15.0, 22.6), (13.6, 26.0), 2.2, 3.0),
        S((21.4, 20.0), (19.2, 22.6), (17.8, 25.8), 2.2, 3.0),
        S((24.6, 21.2), (23.0, 23.6), (21.8, 26.2), 2.0, 2.8),
        S((27.0, 23.6), (26.0, 25.4), (25.0, 27.2), 1.5, 2.3),
    ])},
    "short": {"name": "Short Layered", "gender": "female", "front": flat([
        shell(14.8, 11.6, 29.8, 31.0, 0.0, ys=40.0, yn=43.0, ear=False),
        S((4.8, 27), (3.0, 32.4), (4.6, 38.0), 3.4, 1.8, zs=[3.0, 1.2, 0.2]),      # side locks hug the sides
        S((26.2, 27), (28.0, 32.4), (26.4, 38.0), 3.4, 1.8, zs=[3.0, 1.2, 0.2]),
        S((7.4, 29), (6.4, 33.4), (7.4, 37.0), 2.0, 0.9, zs=[5.0, 3.0, 1.6]),
        S((23.6, 29), (24.6, 33.4), (23.6, 37.0), 2.0, 0.9, zs=[5.0, 3.0, 1.6]),
        S((18.6, 23.6), (13, 24.6), (8.0, 30.6), 3.2, 1.0),
        S((19.6, 24.0), (16.4, 27.0), (13.6, 31.0), 2.6, 0.8),
        S((20.6, 24.0), (23.4, 26.8), (24.6, 30.6), 2.4, 0.9),
    ])},
    "ponytail": {"name": "Low Ponytail", "gender": "female",
                 "back": [S((21, 40), (26.5, 45), (25.0, 53.5), 3.2, 1.4, zs=[-9.0, -8.2, -6.6])],
                 "front": flat([
        shell(14.0, 10.6, 29.4, 25.4, 0.06, ys=32.0, yn=42.0),
        S((15.5, 19.8), (8.4, 21.0), (4.4, 30.6), 3.4, 2.0),
        S((15.5, 19.8), (22.6, 21.0), (26.6, 30.6), 3.4, 2.0),
        S((15.5, 22.4), (10.0, 23.4), (6.2, 31.0), 2.6, 1.3),
        S((15.5, 22.4), (21.0, 23.4), (24.8, 31.0), 2.6, 1.3),
    ])},
    "hime": {"name": "Hime Cut", "gender": "female",
             "back": [B3(15.5, 40.0, 14.2, 18.0, cz=-9.0, rz=3.4, ymax=57.4)],
             "front": flat([
        shell(14.8, 11.6, 29.8, 31.6, 0.0, ys=42.0, yn=44.0, ear=False),
        S((4.4, 27.5), (3.8, 35.5), (4.2, 43.4), 3.4, 3.1, zs=[3.4, 1.4, 0.6]),
        S((26.6, 27.5), (27.2, 35.5), (26.8, 43.4), 3.4, 3.1, zs=[3.4, 1.4, 0.6]),
        S((7.4, 30.0), (7.2, 37.0), (7.4, 43.2), 2.2, 2.0, zs=[5.6, 3.0, 1.4]),
        S((23.6, 30.0), (23.8, 37.0), (23.6, 43.2), 2.2, 2.0, zs=[5.6, 3.0, 1.4]),
        *[S((x, 26.4), (x, 28.8), (x, 31.0), 2.3, 2.1) for x in (7.6, 11.6, 15.5, 19.4, 23.4)],
    ])},
}


# ---- per-view primitives -----------------------------------------------------------------------------------
def shell_prim(view, sp):
    """Ellipsoid whose cross-section morphs from the front-cap ellipse to the head ellipse, clipped by a
    hairline that wraps the head."""
    cyA, rxA, ryA = sp["cy"], sp["rx"], sp["ry"]
    cyB, rxB, ryB = 33.0, 13.0, 12.0

    def params(y):
        s = smooth((y - 29.5) / 8.5)
        return (cyA + (cyB - cyA) * s, rxA + (rxB - rxA) * s, ryA + (ryB - ryA) * s)

    def geom(sx, sy):
        cyE, rxE, ryE = params(sy)
        sr = rxE * (RZ if view == "W" else 1.0)           # screen half-width
        nx = (sx - CX) / sr
        ny = (sy - cyE) / ryE
        return cyE, rxE, ryE, nx, ny

    def inside(sx, sy):
        _, rxE, _, nx, ny = geom(sx, sy)
        ins = nx * nx + ny * ny < 1
        d = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        if view == "S":
            X, Z = sx, rxE * RZ * d
        elif view == "N":
            X, Z = 31.0 - sx, -rxE * RZ * d
        else:
            X, Z = CX + rxE * d, CX - sx
        dx = X - CX
        fz = np.clip(Z / (rxE * RZ), -1, 1)
        yh_front = sp["yf"] + sp["arch"] * dx * dx
        w = smooth(fz / 0.35)
        yh = np.where(fz >= 0, sp["ys"] + (yh_front - sp["ys"]) * w, sp["ys"] + (sp["yn"] - sp["ys"]) * (-fz))
        keep = sy < yh
        if sp["ear"]:   # leave the ears clear
            keep &= ~((np.abs(dx) > 8.5) & (np.abs(Z + 0.8) < 3.6) & (np.abs(sy - 35.2) < 4.6))
        return ins & keep

    def normal(sx, sy):
        _, _, _, nx, ny = geom(sx, sy)
        nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        n = np.stack([nx, ny, nz], -1)
        return n / np.linalg.norm(n, axis=-1, keepdims=True).clip(1e-6)

    return Prim(inside, normal, kind="blob")


def view_prims(style, view):
    """(front prims, back prims) for one view, each in painter order."""
    spec = STYLES[style]
    front, back = [], []

    def build(items, force_back=False):
        for it in items:
            kind = it[0]
            if kind == "shell":
                (front if not force_back else back).append(shell_prim(view, it[1]))
                continue
            if kind == "s3":
                pts = [view_pt(view, *p) for p in it[1]]
                prim = H0.strand(pts[0][:2], pts[1][:2], pts[2][:2], it[2], it[3])
                zc = np.mean([p[2] for p in it[1]]) if view != "W" else np.mean([p[0] for p in it[1]]) - CX
                zc_world = np.mean([p[2] for p in it[1]])
            else:  # b3
                d = it[1]
                sx, sy, _ = view_pt(view, d["cx"], d["cy"], d["cz"])
                rxv = d["rx"] if view != "W" else d["rz"]
                prim = H0.blob(sx, sy, rxv, d["ry"], ymax=d["ymax"])
                zc = d["cz"] if view != "W" else d["cx"] - CX
                zc_world = d["cz"]
            # which side of the body is it on?
            if view == "S":
                is_back = zc_world < -2.0
            elif view == "N":
                is_back = zc_world > 2.0
            else:
                is_back = zc < -2.0 if zc_world > -2.0 else True
            (back if (is_back or force_back) else front).append(prim)

    build(spec["front"])
    build(spec.get("back", []))
    return front, back


def render_style(style, view, skin_mask, pal):
    """Front-layer and back-layer images (RGBA, head offset 0)."""
    front, back = view_prims(style, view)
    f = H0.render(front, pal, skin_mask)[0] if front else Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b = H0.render(back, pal, skin_mask, back=True)[0] if back else None
    return f, b
