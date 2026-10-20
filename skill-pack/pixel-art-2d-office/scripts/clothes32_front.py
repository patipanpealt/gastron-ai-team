"""Character kit v4 — TOPS for the 32x64 chibi, FRONT view only (design review, no sheets yet).

Five garments: T-shirt, button shirt, suit (jacket + shirt + Gastron-red tie), dress, tank top.
Each garment is a stack of PIECES (body, sleeves, collar, lapels, tie, skirt…) built on the body's own
volumes — the torso ellipsoid and arm tubes, slightly inflated so cloth sits over skin — so the cloth
shades with the same round, curvature-following light as the body and hair:

  - 5 hue-shifted fabric tones + outline per material, light softened across piece seams before banding
  - shadow under the head/chin, darker toward the lower right
  - outline on the outer silhouette; a darker fabric tone where one piece overlaps another
    (collar over shirt, lapel over shirt, sleeve over body below the shoulder)
  - small details on top: placket + buttons, pocket, cuffs, rib edges, skirt pleats

Draw order per cell: hair back -> body -> CLOTHES -> face -> hair front

  character32/clothes/top32_<name>_front.png   one layer per garment
  character32/clothes/clothes32-front-review.png   every top on the body, without and with hair
"""
from pathlib import Path

import numpy as np
from PIL import Image

import character32_front as B
import hair32_front as HAIR
from kit import floor_bg, hx

OUT = B.OUT / "clothes"
OUT.mkdir(parents=True, exist_ok=True)
W, H, PX, PY = B.W, B.H, B.PX, B.PY

PALETTES = {  # highlight, light, base, shade, deep, outline (shadows cooler, highlights warmer)
    "tee":    ["#a8e6bc", "#66c893", "#34a86c", "#218458", "#176046", "#0b2c22"],   # Gastron-ish green
    "shirt":  ["#f2f8ff", "#d4e5fa", "#adc9ee", "#86a7d8", "#6080b6", "#1e2848"],   # light office blue
    "white":  ["#ffffff", "#f3f4f9", "#dfe2ee", "#bfc4d8", "#979fba", "#2a2c44"],
    "navy":   ["#7083b4", "#4f6192", "#384672", "#293455", "#1d253e", "#0b0f1e"],
    "red":    ["#ff7a82", "#e8202e", "#b8000f", "#84000c", "#5a0008", "#2a0006"],   # Gastron red tie
    "rose":   ["#ffd8e0", "#f8a8ba", "#e67f98", "#c65e7c", "#9c4562", "#40182a"],
    "cream":  ["#fffaf0", "#fbefd8", "#f0dcb8", "#d8bc92", "#b4966c", "#3c2e20"],
    "heather": ["#ffffff", "#eef0f3", "#d6d9e0", "#b2b7c3", "#8b91a1", "#262a36"],
}
CUTS = [0.6, 0.28, -0.06, -0.4]

TORSO = (15.5, 51.2, 7.4, 6.6)
ARMS = [((9.6, 48.0), (7.0, 52.6), 2.5, 2.9), ((21.4, 48.0), (24.0, 52.6), 2.5, 2.9)]


# ---- shape helpers --------------------------------------------------------------------------------
def poly(*pts):
    pts = np.array(pts, float)

    def inside(x, y):
        res = np.zeros(x.shape, bool)
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            cross = ((yi > y) != (yj > y)) & (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi)
            res ^= cross
            j = i
        return res
    return inside


def ell(cx, cy, rx, ry):
    return lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1


def both(*fs):
    return lambda x, y: np.logical_and.reduce([f(x, y) for f in fs])


def minus(f, *gs):
    return lambda x, y: f(x, y) & ~np.logical_or.reduce([g(x, y) for g in gs])


def torso(pad=0.55):
    cx, cy, rx, ry = TORSO
    return B.ellipsoid(cx, cy, rx + pad, ry + pad * 0.8, depth=0.9)


def sleeve(side, u_max, pad=0.55):
    (a, b, r0, r1) = ARMS[side]
    st = HAIR.strand(a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b, r0 + pad, r1 + pad)
    return (lambda x, y: st.inside(x, y) & (st.u(x, y) < u_max)), st.normal, st.u


def skirt_normal(x, y):
    """A-line skirt: a cone widening downward — cylinder-like across, tilted slightly toward the floor."""
    t = np.clip((y - 52.6) / 7.6, 0, 1)
    hw = 7.0 + 2.6 * t
    nx = np.clip((x - 15.5) / (hw + 0.6), -1, 1)
    n = np.stack([nx, np.full_like(x, 0.28), np.sqrt(np.clip(1 - nx * nx, 0.05, 1))], -1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


class Piece:
    def __init__(self, inside, normal, pal, shift=0, u=None, sep_ymin=0.0, flat=0.0):
        self.inside, self.normal, self.pal, self.shift = inside, normal, pal, shift
        self.u, self.sep_ymin, self.flat = u, sep_ymin, flat


def body_piece(pal, region, pad=0.55, **kw):
    inside, normal = torso(pad)
    return Piece(both(inside, region), normal, pal, **kw)


def sleeve_pieces(pal, u_max, pad=0.55, **kw):
    out = []
    for s in (0, 1):
        inside, normal, u = sleeve(s, u_max, pad)
        out.append(Piece(inside, normal, pal, u=u, sep_ymin=49.5, **kw))
    return out


def cuffs(pal, u0, u1, pad=0.7, shift=-1):
    out = []
    for s in (0, 1):
        inside, normal, u = sleeve(s, u1, pad)
        out.append(Piece(lambda x, y, i=inside, uu=u: i(x, y) & (uu(x, y) > u0), normal, pal,
                         shift=shift, u=u, sep_ymin=0))
    return out


def flat_normal(z=0.9):
    def normal(x, y):
        n = np.stack([np.zeros_like(x) - 0.1, np.zeros_like(x) - 0.15, np.full_like(x, z)], -1)
        return n / np.linalg.norm(n, axis=-1, keepdims=True)
    return normal


NECK_SKIN = ell(15.5, 45.6, 3.4, 2.4)
HEM = lambda y0: (lambda x, y: y < y0)  # noqa: E731

# ---- the five tops (pieces back -> front; details are (x, y, tone or 'o', pal) overlays) ----------
TOPS = {
    "tee": {"name": "T-Shirt", "pieces": [
        body_piece("tee", minus(HEM(57.4), NECK_SKIN)),
        Piece(both(minus(ell(15.5, 45.8, 4.3, 3.0), NECK_SKIN), lambda x, y: y > 45.4),
              torso()[1], "tee", shift=1),                                       # rib collar
        *sleeve_pieces("tee", 0.48, pad=0.75),
        *cuffs("tee", 0.38, 0.48, pad=0.85, shift=1),                            # sleeve hem band
    ], "details": [((11, 53), 4, "tee"), ((12, 54), 4, "tee"), ((20, 53), 4, "tee"), ((19, 54), 4, "tee"),
                   ((15, 55), 3, "tee"), ((16, 56), 3, "tee")]},
    "shirt": {"name": "Button Shirt", "pieces": [
        body_piece("shirt", minus(HEM(57.6), poly((13.9, 44.6), (17.1, 44.6), (15.5, 47.6)))),
        *sleeve_pieces("shirt", 0.8),
        *cuffs("shirt", 0.66, 0.8, pad=0.75),
        Piece(poly((12.2, 44.4), (15.2, 47.9), (12.6, 48.8), (11.4, 46.0)), torso()[1], "shirt", shift=-1),
        Piece(poly((18.8, 44.4), (15.8, 47.9), (18.4, 48.8), (19.6, 46.0)), torso()[1], "shirt", shift=-1),
    ], "details": [*[((15, y), 4, "shirt") for y in range(48, 57)],             # placket line
                   *[((16, y), 0, "shirt") for y in (49, 52, 55)],                # buttons
                   *[((16, y + 1), 4, "shirt") for y in (49, 52, 55)],
                   *[((x, 49), 3, "shirt") for x in (18, 19, 20)],               # chest pocket
                   ((18, 50), 3, "shirt"), ((20, 50), 3, "shirt"), ((19, 51), 3, "shirt")]},
    "suit": {"name": "Suit", "pieces": [
        body_piece("white", minus(HEM(57.6), poly((14.4, 44.6), (16.6, 44.6), (15.5, 46.6)))),
        Piece(poly((14.2, 46.2), (16.8, 46.2), (16.3, 48.0), (14.7, 48.0)), flat_normal(), "red", shift=1),
        Piece(poly((14.6, 47.6), (16.4, 47.6), (17.4, 54.2), (15.5, 56.2), (13.6, 54.2)), torso()[1], "red", shift=1),
        body_piece("navy", minus(HEM(58.2), poly((12.0, 44.0), (19.0, 44.0), (15.5, 54.4))), pad=0.75),
        Piece(poly((12.0, 44.4), (15.4, 54.2), (13.6, 52.0), (11.2, 48.6), (12.8, 47.6), (10.8, 46.2)),
              torso()[1], "navy", shift=-1),                                      # left lapel (notched)
        Piece(poly((19.0, 44.4), (15.6, 54.2), (17.4, 52.0), (19.8, 48.6), (18.2, 47.6), (20.2, 46.2)),
              torso()[1], "navy", shift=-1),
        *sleeve_pieces("navy", 0.72, pad=0.8),
        *cuffs("white", 0.68, 0.8, pad=0.6, shift=0),                            # shirt cuff peeking out
    ], "details": [((15, 56), 0, "navy"), ((16, 56), 1, "navy"), ((15, 57), 4, "navy"), ((16, 57), 4, "navy"),
                   ((19, 50), 1, "white"), ((20, 50), 0, "white")]},             # pocket square
    "dress": {"name": "Dress", "pieces": [
        Piece(poly((8.4, 52.0), (22.6, 52.0), (25.6, 59.8), (15.5, 60.8), (5.4, 59.8)), skirt_normal, "rose"),
        body_piece("rose", minus(HEM(53.0), ell(15.5, 45.2, 4.2, 2.9))),
        *sleeve_pieces("rose", 0.36, pad=1.0),                                    # little puff sleeves
        body_piece("white", lambda x, y: (y > 51.9) & (y < 53.1), pad=0.75),     # thin waist ribbon
        Piece(poly((16.6, 50.4), (19.6, 52.5), (16.6, 54.6)), flat_normal(), "white", shift=1),   # bow loops
        Piece(poly((22.6, 50.4), (19.6, 52.5), (22.6, 54.6)), flat_normal(), "white", shift=1),
        Piece(ell(19.6, 52.5, 1.1, 1.1), flat_normal(), "white"),
    ], "details": [*[((x + (y - 54) // 3 * (1 if x > 15 else -1), y), 3, "rose")   # skirt pleats
                     for x in (10, 13, 18, 21) for y in range(55, 60)]]},
    "tank": {"name": "Tank Top", "pieces": [
        body_piece("heather", minus(HEM(57.4), ell(15.5, 45.4, 3.6, 2.7), ell(8.0, 47.4, 2.2, 2.7),
                                   ell(23.0, 47.4, 2.2, 2.7))),
    ], "details": [((x, y), 3, "heather") for x in range(10, 22, 2) for y in range(50, 57)], "rib": True},
}

NB4 = ((-1, 0), (1, 0), (0, -1), (0, 1))


def render(top, skin_mask):
    pieces = top["pieces"]
    owner = np.full((H, W), -1, int)
    for i, p in enumerate(pieces):
        owner[B.coverage(p.inside) >= 0.5] = i
    mask = owner >= 0
    v = np.zeros((H, W))
    for i, p in enumerate(pieces):
        m = owner == i
        if m.any():
            v[m] = B.lambert(p.normal(PX, PY))[m]
    v -= np.where(PY < 48.5, 0.3, 0) + np.clip((PY - 50) / 30, 0, 0.18)  # chin shadow, lower body
    v = HAIR.soften(v, mask, 0.4)
    tone = np.full((H, W), -1, int)
    tone[mask] = B.band(v, CUTS)[mask]
    for i, p in enumerate(pieces):
        m = owner == i
        tone[m] = np.clip(tone[m] + p.shift, 0, 4)
    tone = B.despeckle(tone, mask)
    pal = np.full((H, W), "", object)
    for i, p in enumerate(pieces):
        pal[owner == i] = p.pal
    base = tone.copy()
    p_own = np.pad(owner, 1, constant_values=-1)
    for dy, dx in NB4:
        nb = p_own[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
        tone[mask & (nb < 0)] = 5                                    # outer edge -> outline
        for i, p in enumerate(pieces):
            sep = (owner == i) & (nb >= 0) & (nb < i) & (PY >= p.sep_ymin) & (tone < 5)
            nb_pal = np.array([pieces[k].pal if k >= 0 else "" for k in range(len(pieces))] + [""], object)[nb]
            same = nb_pal == p.pal
            tone[sep & same] = np.minimum(base[sep & same] + 2, 4)
            tone[sep & ~same] = 4
    if top.get("rib"):  # tank: 1-px rib binding along the neckline + armholes
        rib = mask & (tone < 5)
        p_m = np.pad(mask, 1)
        touch = np.zeros_like(mask)
        for dy, dx in NB4:
            touch |= ~p_m[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
        inner = np.zeros_like(mask)
        for dy, dx in NB4:
            nb_t = np.pad(tone == 5, 1)[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
            inner |= nb_t
        tone[rib & inner & (PY < 52)] = np.minimum(tone[rib & inner & (PY < 52)] + 1, 4)
    for (x, y), t, pk in top["details"]:
        if 0 <= x < W and 0 <= y < H and mask[y, x] and tone[y, x] != 5:
            tone[y, x], pal[y, x] = t, pk
    im = np.zeros((H, W, 4), np.uint8)
    for k in PALETTES:
        cols = [hx(c) for c in PALETTES[k]]
        for t in range(6):
            im[(pal == k) & (tone == t)] = list(cols[t]) + [255]
    return Image.fromarray(im)


if __name__ == "__main__":
    tone, head, owner = B.build_body()
    skin = tone >= 0
    body_img = B.paint(tone, B.TONES[B.DEFAULT])
    face = B.face_layer()
    hair_for = {"tee": "up", "shirt": "neat", "suit": "sidepart", "dress": "hime", "tank": "short"}
    rows = [[], []]
    for name, top in TOPS.items():
        layer = render(top, skin)
        layer.save(OUT / f"top32_{name}_front.png")
        st = HAIR.STYLES[hair_for[name]]
        hf, _ = HAIR.render(st["front"], HAIR.COLORS["black"], skin)
        hb = HAIR.render(st["back"], HAIR.COLORS["black"], skin, back=True)[0] if "back" in st else None
        for r, with_hair in enumerate((False, True)):
            im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            if with_hair and hb is not None:
                im.alpha_composite(hb)
            for l in (body_img, layer, face) + ((hf,) if with_hair else ()):
                im.alpha_composite(l)
            rows[r].append(im)
    gap = 6
    bg = floor_bg(gap + len(TOPS) * (W + gap), gap + 2 * (H + gap))
    for r, row in enumerate(rows):
        for i, im in enumerate(row):
            bg.alpha_composite(im, (gap + i * (W + gap), gap + r * (H + gap)))
    bg.resize((bg.width * 7, bg.height * 7), Image.NEAREST).convert("RGB").save(OUT / "clothes32-front-review.png")
    print("ok")
