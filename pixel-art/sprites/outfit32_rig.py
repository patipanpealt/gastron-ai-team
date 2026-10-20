"""Character kit v5 — TOPS and BOTTOMS for every view and pose of the 32x64 rig.

The garments are built exactly like the approved front versions (clothes32_front.py / bottoms32_front.py):
pieces made from inflated copies of the body's own volumes (torso ellipsoid, arm and leg tubes), shaded
by the same light and 5-tone hue-shifted ramps. The difference is that the volumes now come from the
pose rig, so sleeves follow the arms, trousers follow the legs, and the same garment is drawn for the
front (S), back (N) and side (W; E = W mirrored).

  - the front view with the idle pose reproduces the approved tops / bottoms exactly
  - arms (or hands) that are in front of the torso are cut out of the torso pieces so a hand never
    disappears under a shirt, and sleeves are drawn over them
  - hems follow the body bob (ty); trouser hems follow lifted feet
"""
import numpy as np

import character32_front as B
import clothes32_front as C
import hair32_front as HAIR
import rig32 as R
from clothes32_front import Piece, both, ell, minus, poly
import bottoms32_front as BF
from bottoms32_front import cyl_normal, pleat_normal

W, H, PX, PY = B.W, B.H, B.PX, B.PY
FLAT = C.flat_normal


class Ctx:
    """Geometry shared by all garments for one (view, pose) frame."""

    def __init__(self, view, pose, body):
        self.view, self.pose, self.dy = view, pose, pose["ty"]
        self.rx = 6.3 if view == "W" else 7.4
        self.arm2d = {s: [R.proj(view, *p)[:2] for p in pose["arms"][s]] for s in "LR"}
        self.leg2d = {s: [R.proj(view, *p)[:2] for p in pose["legs"][s]] for s in "LR"}
        # arms (or hands) in front of the torso must not be painted over by torso pieces
        self.E = None
        if view == "W" or pose["overlap"]:
            self.E = self._arm_mask(body)
        self.exclude = self.E is not None

    def _arm_mask(self, body):
        grp, rank = body["grp"], body["rank"]
        torso_rank = rank[grp == "torso"].max() if (grp == "torso").any() else -1
        return (grp == "arm") & (rank > torso_rank)

    # -- shapes ------------------------------------------------------------------------------------------
    def torso(self, pad=0.55):
        return B.ellipsoid(15.5, 51.2 + self.dy, self.rx + pad, 6.6 + pad * 0.8, depth=0.9)

    def Y(self, y):
        return y + self.dy

    def ell(self, cx, cy, rx, ry):
        return ell(cx, cy + self.dy, rx, ry)

    def poly(self, *pts):
        return poly(*[(x, y + self.dy) for x, y in pts])

    def hem(self, y):
        yy = y + self.dy
        return lambda x, yv: yv < yy

    def below(self, y):
        yy = y + self.dy
        return lambda x, yv: yv > yy

    def neck(self):
        return {"S": self.ell(15.5, 45.6, 3.4, 2.4), "N": self.ell(15.5, 44.9, 3.2, 1.6),
                "W": self.ell(15.5, 45.8, 2.8, 2.4)}[self.view]

    def cut(self, region):
        """Remove the in-front arm pixels from a torso-type region."""
        if not self.exclude:
            return region
        E = self.E

        def f(x, y):
            xi = np.clip(x.astype(int), 0, W - 1)
            yi = np.clip(y.astype(int), 0, H - 1)
            return region(x, y) & ~E[yi, xi]
        return f

    def body_piece(self, pal, region, pad=0.55, **kw):
        inside, normal = self.torso(pad)
        return Piece(self.cut(both(inside, region)), normal, pal, **kw)

    def sleeve(self, side, u_max, pad=0.55):
        a, b = self.arm2d[side]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        st = HAIR.strand(a, mid, b, 2.5 + pad, 2.9 + pad)
        return (lambda x, y: st.inside(x, y) & (st.u(x, y) < u_max)), st.normal, st.u

    def sleeves(self, pal, u_max, pad=0.55, **kw):
        out = []
        for s in self.order_arms():
            inside, normal, u = self.sleeve(s, u_max, pad)
            out.append(Piece(inside, normal, pal, u=u, sep_ymin=(0 if self.view == "W" else 49.5 + self.dy), **kw))
        return out

    def cuffs(self, pal, u0, u1, pad=0.7, shift=-1):
        out = []
        for s in self.order_arms():
            inside, normal, u = self.sleeve(s, u1, pad)
            out.append(Piece(lambda x, y, i=inside, uu=u: i(x, y) & (uu(x, y) > u0), normal, pal,
                             shift=shift, u=u, sep_ymin=0))
        return out

    def order_arms(self):
        """Far arm first (W view: the arm at X=9.6 is the far one)."""
        return ["L", "R"]

    def details(self, items):
        out = []
        for (x, y), t, pk in items:
            yy = y + self.dy
            if self.exclude and self.E[min(max(yy, 0), H - 1), min(max(x, 0), W - 1)]:
                continue
            out.append(((x, yy), t, pk))
        return out


def torso_hem(c, y=57.4):
    return c.hem(y)


# ============================================ tops ===================================================
def top_tee(c):
    v = c.view
    neck = c.neck()
    pieces = [c.body_piece("tee", minus(torso_hem(c), neck))]
    if v == "S":
        pieces.append(Piece(both(minus(c.ell(15.5, 45.8, 4.3, 3.0), neck), c.below(45.4)), c.torso()[1], "tee", shift=1))
        det = [((11, 53), 4, "tee"), ((12, 54), 4, "tee"), ((20, 53), 4, "tee"), ((19, 54), 4, "tee"),
               ((15, 55), 3, "tee"), ((16, 56), 3, "tee")]
    elif v == "N":
        pieces.append(Piece(both(minus(c.ell(15.5, 45.2, 4.2, 2.2), neck), c.below(44.8)), c.torso()[1], "tee", shift=1))
        det = [((12, 53), 4, "tee"), ((19, 53), 4, "tee"), ((15, 55), 3, "tee"), ((16, 55), 3, "tee")]
    else:
        pieces.append(Piece(both(minus(c.ell(15.3, 45.9, 4.0, 2.9), neck), c.below(45.4)), c.torso()[1], "tee", shift=1))
        det = [((12, 54), 4, "tee"), ((13, 55), 4, "tee"), ((17, 53), 3, "tee")]
    pieces += c.sleeves("tee", 0.48, pad=0.75) + c.cuffs("tee", 0.38, 0.48, pad=0.85, shift=1)
    return {"pieces": pieces, "details": c.details(det)}


def top_shirt(c):
    v = c.view
    if v == "S":
        notch = c.poly((13.9, 44.6), (17.1, 44.6), (15.5, 47.6))
    elif v == "N":
        notch = c.poly((13.9, 44.0), (17.1, 44.0), (15.5, 45.4))
    else:
        notch = c.poly((13.4, 44.4), (17.4, 44.4), (16.6, 47.2), (13.6, 47.2))
    pieces = [c.body_piece("shirt", minus(torso_hem(c, 57.6), notch))]
    pieces += c.sleeves("shirt", 0.8) + c.cuffs("shirt", 0.66, 0.8, pad=0.75)
    tn = c.torso()[1]
    if v == "S":
        pieces += [Piece(c.poly((12.2, 44.4), (15.2, 47.9), (12.6, 48.8), (11.4, 46.0)), tn, "shirt", shift=-1),
                   Piece(c.poly((18.8, 44.4), (15.8, 47.9), (18.4, 48.8), (19.6, 46.0)), tn, "shirt", shift=-1)]
        det = [*[((15, y), 4, "shirt") for y in range(48, 57)], *[((16, y), 0, "shirt") for y in (49, 52, 55)],
               *[((16, y + 1), 4, "shirt") for y in (49, 52, 55)], *[((x, 49), 3, "shirt") for x in (18, 19, 20)],
               ((18, 50), 3, "shirt"), ((20, 50), 3, "shirt"), ((19, 51), 3, "shirt")]
    elif v == "N":
        pieces.append(Piece(both(minus(c.ell(15.5, 45.2, 4.8, 2.8), c.neck()), c.below(44.5)), tn, "shirt", shift=-1))
        det = [*[((x, 49), 3, "shirt") for x in range(10, 22)], *[((15, y), 3, "shirt") for y in range(51, 57)]]
    else:
        pieces.append(Piece(c.poly((12.0, 44.6), (16.6, 44.4), (15.4, 48.2), (11.6, 47.0)), tn, "shirt", shift=-1))
        det = [*[((11, y), 4, "shirt") for y in range(48, 57)], *[((12, y), 0, "shirt") for y in (49, 52, 55)]]
    return {"pieces": pieces, "details": c.details(det)}


def top_suit(c):
    v = c.view
    tn = c.torso()[1]
    pieces = []
    if v == "S":
        pieces += [c.body_piece("white", minus(torso_hem(c, 57.6), c.poly((14.4, 44.6), (16.6, 44.6), (15.5, 46.6)))),
                   Piece(c.poly((14.2, 46.2), (16.8, 46.2), (16.3, 48.0), (14.7, 48.0)), FLAT(), "red", shift=1),
                   Piece(c.poly((14.6, 47.6), (16.4, 47.6), (17.4, 54.2), (15.5, 56.2), (13.6, 54.2)), tn, "red", shift=1),
                   c.body_piece("navy", minus(torso_hem(c, 58.2), c.poly((12.0, 44.0), (19.0, 44.0), (15.5, 54.4))), pad=0.75),
                   Piece(c.poly((12.0, 44.4), (15.4, 54.2), (13.6, 52.0), (11.2, 48.6), (12.8, 47.6), (10.8, 46.2)), tn, "navy", shift=-1),
                   Piece(c.poly((19.0, 44.4), (15.6, 54.2), (17.4, 52.0), (19.8, 48.6), (18.2, 47.6), (20.2, 46.2)), tn, "navy", shift=-1)]
        det = [((15, 56), 0, "navy"), ((16, 56), 1, "navy"), ((15, 57), 4, "navy"), ((16, 57), 4, "navy"),
               ((19, 50), 1, "white"), ((20, 50), 0, "white")]
    elif v == "N":
        pieces += [c.body_piece("navy", minus(torso_hem(c, 58.2), c.neck()), pad=0.75),
                   Piece(both(minus(c.ell(15.5, 45.0, 3.8, 1.8), c.neck()), c.below(44.2)), tn, "white"),
                   Piece(both(minus(c.ell(15.5, 45.5, 5.4, 2.8), c.neck()), c.below(44.9)), tn, "navy", shift=-1)]
        det = [*[((15, y), 4, "navy") for y in range(52, 58)], *[((16, y), 3, "navy") for y in range(54, 58)]]
    else:
        pieces += [c.body_piece("navy", minus(torso_hem(c, 58.2), c.neck()), pad=0.75),
                   Piece(both(minus(c.ell(15.2, 45.7, 3.6, 1.8), c.neck()), c.below(44.9)), tn, "white"),
                   Piece(c.poly((9.6, 46.2), (14.4, 47.4), (11.2, 54.0), (9.2, 51.4)), tn, "navy", shift=-1),
                   Piece(c.poly((9.8, 47.2), (11.6, 47.4), (12.0, 54.0), (10.6, 55.8), (9.4, 54.0)), tn, "red", shift=1)]
        det = [((11, 56), 0, "navy"), ((11, 57), 4, "navy")]
    pieces += c.sleeves("navy", 0.72, pad=0.8) + c.cuffs("white", 0.68, 0.8, pad=0.6, shift=0)
    return {"pieces": pieces, "details": c.details(det)}


def top_dress(c):
    v = c.view
    tn = c.torso()[1]
    if v == "W":
        skirt = Piece(c.poly((9.6, 52.0), (21.4, 52.0), (24.2, 60.0), (6.8, 60.0)), pleat_free_normal(15.5, 7.6), "rose")
    else:
        skirt = Piece(c.poly((8.4, 52.0), (22.6, 52.0), (25.6, 59.8), (15.5, 60.8), (5.4, 59.8)), C.skirt_normal, "rose")
    neck_h = {"S": c.ell(15.5, 45.2, 4.2, 2.9), "N": c.ell(15.5, 44.8, 3.6, 1.8), "W": c.ell(15.0, 45.4, 3.2, 2.6)}[v]
    pieces = [skirt, c.body_piece("rose", minus(c.hem(53.0), neck_h))]
    pieces += c.sleeves("rose", 0.36, pad=1.0)
    ribbon = c.body_piece("white", lambda x, y: (y > c.Y(51.9)) & (y < c.Y(53.1)), pad=0.75)
    pieces.append(ribbon)
    if v == "S":
        pieces += [Piece(c.poly((16.6, 50.4), (19.6, 52.5), (16.6, 54.6)), FLAT(), "white", shift=1),
                   Piece(c.poly((22.6, 50.4), (19.6, 52.5), (22.6, 54.6)), FLAT(), "white", shift=1),
                   Piece(c.ell(19.6, 52.5, 1.1, 1.1), FLAT(), "white")]
    elif v == "N":
        pieces += [Piece(c.poly((12.0, 50.4), (15.5, 52.5), (12.0, 54.6)), FLAT(), "white", shift=1),
                   Piece(c.poly((19.0, 50.4), (15.5, 52.5), (19.0, 54.6)), FLAT(), "white", shift=1),
                   Piece(c.poly((14.4, 53.2), (16.6, 53.2), (17.2, 57.2), (13.8, 57.2)), FLAT(), "white", shift=1),
                   Piece(c.ell(15.5, 52.5, 1.2, 1.2), FLAT(), "white")]
    else:
        pieces += [Piece(c.poly((20.0, 50.6), (23.8, 52.5), (20.0, 54.4)), FLAT(), "white", shift=1),
                   Piece(c.ell(20.4, 52.5, 1.1, 1.1), FLAT(), "white")]
    if v == "W":
        det = [((x, y), 3, "rose") for x in (11, 14, 18, 21) for y in range(55, 60)]
    else:
        det = [((x + (y - 54) // 3 * (1 if x > 15 else -1), y), 3, "rose") for x in (10, 13, 18, 21) for y in range(55, 60)]
    det = [((x, y), t, p) for (x, y), t, p in det]
    # skirt details are not shifted with the body bob (the skirt hangs from the waist)
    return {"pieces": pieces, "details": [d for d in det]}


def pleat_free_normal(cx, hw):
    def normal(x, y):
        nx = np.clip((x - cx) / hw, -1, 1)
        n = np.stack([nx, np.full_like(x, 0.28), np.sqrt(np.clip(1 - nx * nx, 0.05, 1))], -1)
        return n / np.linalg.norm(n, axis=-1, keepdims=True)
    return normal


def top_tank(c):
    v = c.view
    if v == "S":
        sub = [c.ell(15.5, 45.4, 3.6, 2.7), c.ell(8.0, 47.4, 2.2, 2.7), c.ell(23.0, 47.4, 2.2, 2.7)]
    elif v == "N":
        sub = [c.ell(15.5, 45.0, 3.6, 2.2), c.ell(8.0, 47.4, 2.2, 2.7), c.ell(23.0, 47.4, 2.2, 2.7)]
    else:
        sub = [c.ell(14.6, 45.6, 3.0, 2.8)]
    pieces = [c.body_piece("heather", minus(torso_hem(c), *sub))]
    det = [((x, y), 3, "heather") for x in range(10, 22, 2) for y in range(50, 57)]
    return {"pieces": pieces, "details": c.details(det), "rib": True}


TOPS = {"tee": top_tee, "shirt": top_shirt, "suit": top_suit, "dress": top_dress, "tank": top_tank}


# =========================================== bottoms =================================================
def leg_capsule(c, side, pad=0.45):
    """Inflated leg tube from 2 px above the hip down the pose's leg line (curved when seated)."""
    pts = c.leg2d[side]
    top = (pts[0][0], pts[0][1] - 2.0)
    chain = [top] + list(pts) if len(pts) == 2 else [top, pts[1], pts[2]]
    if len(chain) == 3 and len(pts) == 2:      # standing: straight line top -> foot
        chain = [top, (pts[1][0], pts[1][1] + 0.2)]
    if len(chain) == 2:
        ins, nrm = B.capsule(chain[0][0], chain[0][1], chain[1][0], chain[1][1], 2.9 + pad, 2.9 + pad)
    else:
        st = HAIR.strand(chain[0], chain[1], chain[2], 2.9 + pad, 2.9 + pad)
        ins, nrm = st.inside, st.normal
    return ins, nrm


def union_normal(normals, insides):
    def f(x, y):
        best = None
        out = np.zeros(x.shape + (3,))
        best_d = np.full(x.shape, np.inf)
        for ins, nm in zip(insides, normals):
            n = nm(x, y)
            # prefer the leg that actually covers the pixel; tie-break by nearest axis (x is enough)
            cover = ins(x, y)
            d = np.where(cover, 0.0, 1.0)
            take = d < best_d
            out[take] = n[take]
            best_d = np.where(take, d, best_d)
        return out
    return f


def standing_front(c):
    """True when this frame is the plain standing legs seen from the front (the approved trousers)."""
    if c.view != "S" or c.dy != 0:
        return False
    return all(len(c.pose["legs"][s]) == 2 and c.pose["legs"][s][1][2] == 0 and c.pose["legs"][s][1][1] == R.FOOT_Y
               for s in "LR")


def trousers(c, pal, hem, band=None, shift=1):
    if standing_front(c):   # reuse the approved front geometry exactly
        pieces = [Piece(c.cut(BF.trouser_region(53.4, hem)), BF.trouser_normal, pal)]
        if band is not None:
            pieces.append(Piece(BF.trouser_region(hem - band, hem), BF.trouser_normal, pal, shift=shift))
        return pieces
    lifts = {s: max(0.0, B_FOOT - c.pose["legs"][s][-1][1]) for s, B_FOOT in (("L", R.FOOT_Y), ("R", R.FOOT_Y))}
    hip_in, hip_n = c.torso(0.5)
    ins, nms, regions = [], [], []
    for s in "LR":
        li, ln = leg_capsule(c, s)
        h = hem - lifts[s] if len(c.pose["legs"][s]) == 2 else hem
        ins.append(li)
        nms.append(ln)
        regions.append((li, h))
    ins.append(hip_in)
    nms.append(hip_n)
    top_y = 53.4 + c.dy
    notch = lambda x, y: (y > 59.2) & (np.abs(x - 16.0) < 0.55) if c.view in ("S", "N") else np.zeros(x.shape, bool)  # noqa: E731

    def inside(x, y):
        res = hip_in(x, y) & (y < min(h for _, h in regions))
        for li, h in regions:
            res |= li(x, y) & (y < h)
        return res & (y > top_y) & ~notch(x, y)
    norm = union_normal(nms, ins)
    pieces = [Piece(c.cut(inside), norm, pal)]
    if band is not None:
        y0 = band

        def bandin(x, y):
            res = np.zeros(x.shape, bool)
            for li, h in regions:
                res |= li(x, y) & (y < h) & (y > h - y0)
            return res
        pieces.append(Piece(bandin, norm, pal, shift=shift))
    return pieces


def bottom_slacks(c):
    pieces = trousers(c, "slacks", 61.2, band=1.2, shift=-1)
    det = [*[((12, y), 3, "slacks") for y in range(56, 60)], *[((19, y), 3, "slacks") for y in range(56, 60)],
           ((11, 55), 0, "slacks"), ((20, 55), 0, "slacks")]
    return {"pieces": pieces, "details": det if c.view == "S" else (det[:8] if c.view == "N" else
            [((13, 57), 3, "slacks"), ((13, 58), 3, "slacks"), ((17, 56), 0, "slacks")])}


def bottom_jeans(c):
    pieces = trousers(c, "jeans", 61.6, band=2.0, shift=1)
    if c.view == "S":
        det = [((11, 56), 0, "jeans"), ((12, 56), 1, "jeans"), ((11, 57), 1, "jeans"), ((19, 56), 0, "jeans"),
               ((20, 56), 1, "jeans"), ((20, 57), 1, "jeans"), *[((x, 59), 4, "jeans") for x in (10, 11, 12, 13, 18, 19, 20, 21)],
               ((15, 55), 3, "jeans"), ((16, 55), 3, "jeans"), ((15, 56), 4, "jeans"), ((16, 56), 4, "jeans")]
    elif c.view == "N":
        det = [((11, 56), 0, "jeans"), ((20, 56), 0, "jeans"), *[((x, 59), 4, "jeans") for x in (10, 11, 12, 13, 18, 19, 20, 21)],
               ((12, 54), 3, "jeans"), ((13, 55), 3, "jeans"), ((18, 54), 3, "jeans"), ((19, 55), 3, "jeans")]
    else:
        det = [((14, 56), 0, "jeans"), ((14, 57), 1, "jeans"), ((13, 58), 3, "jeans")]
    return {"pieces": pieces, "details": det}


def bottom_shorts(c):
    pieces = trousers(c, "khaki", 58.6, band=1.2, shift=1)
    det = [((11, 55), 0, "khaki"), ((20, 55), 0, "khaki"), ((15, 55), 3, "khaki"), ((16, 55), 3, "khaki")]
    return {"pieces": pieces, "details": det if c.view != "W" else [((14, 55), 0, "khaki")]}


def bottom_pencil(c):
    v = c.view
    if v == "W":
        shape = c.poly((9.4, 53.6), (21.6, 53.6), (20.8, 60.8), (10.2, 60.8))
        low = c.poly((10.2, 59.6), (20.8, 59.6), (20.8, 60.8), (10.2, 60.8))
        nrm = cyl_normal(15.5, 6.8)
    else:
        shape = c.poly((8.6, 53.6), (22.4, 53.6), (21.0, 60.8), (10.0, 60.8))
        low = c.poly((9.6, 59.6), (21.4, 59.6), (21.0, 60.8), (10.0, 60.8))
        nrm = cyl_normal(15.5, 7.4)
    pieces = [Piece(c.cut(shape), nrm, "navy"), Piece(low, nrm, "navy", shift=-1)]
    if v == "S":
        det = [*[((15, y), 4, "navy") for y in (56, 57, 58, 59)], ((12, 55), 0, "navy"), ((19, 56), 1, "navy")]
    elif v == "N":
        det = [*[((15, y), 4, "navy") for y in range(55, 60)], ((16, 58), 3, "navy"), ((16, 59), 3, "navy")]
    else:
        det = [((13, 56), 3, "navy"), ((12, 55), 0, "navy")]
    return {"pieces": pieces, "details": det}


def bottom_pleated(c):
    v = c.view
    if v == "W":
        shape = c.poly((9.8, 53.6), (21.2, 53.6), (24.0, 60.4), (7.2, 60.4))
        low = c.poly((7.4, 59.0), (23.8, 59.0), (24.0, 60.4), (7.2, 60.4))
        nrm = pleat_normal(15.5, 8.4)
    else:
        shape = c.poly((8.6, 53.6), (22.4, 53.6), (25.4, 60.4), (5.6, 60.4))
        low = c.poly((6.0, 59.0), (25.0, 59.0), (25.4, 60.4), (5.6, 60.4))
        nrm = pleat_normal(15.5, 10.0)
    pieces = [Piece(c.cut(shape), nrm, "wine"), Piece(low, nrm, "wine", shift=-1)]
    return {"pieces": pieces, "details": []}


BOTTOMS = {"slacks": bottom_slacks, "jeans": bottom_jeans, "shorts": bottom_shorts,
           "pencil": bottom_pencil, "pleated": bottom_pleated}


def render_garment(kind, name, view, pose, body):
    c = Ctx(view, pose, body)
    spec = (TOPS if kind == "top" else BOTTOMS)[name](c)
    return C.render(spec, body["tone"] >= 0)
