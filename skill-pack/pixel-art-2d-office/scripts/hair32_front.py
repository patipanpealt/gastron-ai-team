"""Character kit v4 — HAIR for the 32x64 chibi, FRONT view only (design review, no sheets yet).

Everyday office hairstyles (3 men, 3 women). Each is a set of CLUMPS (tapered curved locks + a cap
that hugs the skull), shaded as its own little tube blended with the overall head sphere, so every lock
gets a lit upper-left edge and a darker underside. Shading follows the style reference:

  - a long, gently stepped ramp (8 tones incl. outline) instead of a few hard bands; the light field is
    softened across lock boundaries before banding, so tones roll smoothly over the head
  - glossy highlight = thin streak down the lit side of each lock, with a one-tone halo so it fades in
  - shadows shift cool (blue / violet), the hair darkens toward the lower right and toward lock tips
  - selective outline: dark outline only on the outer silhouette; on the face / over another lock the
    edge is a darker hair tone; the fringe casts a soft translucent shadow onto the forehead
  - long styles get a BACK layer drawn behind the body

Review stage: only BLACK is rendered for now (other colours come after the shapes are approved).

  character32/hair/hair32_<style>_front.png       front layer
  character32/hair/hair32_<style>_front_back.png  back layer (styles with hair behind the body)
  character32/hair/hair32-front-review.png        6 styles on the body, 8x
"""
from pathlib import Path

import numpy as np
from PIL import Image

import character32_front as B
from kit import floor_bg, hx

OUT = B.OUT / "hair"
OUT.mkdir(parents=True, exist_ok=True)
W, H, PX, PY = B.W, B.H, B.PX, B.PY

# 0 gloss, 1 highlight, 2 light, 3 base, 4 mid, 5 shade, 6 deep, 7 outline — blue-black, cool shadows
COLORS = {
    "black": ["#a7b0d2", "#6b7096", "#4c5072", "#393c5a", "#2d2f4a", "#23243c", "#1a1a2e", "#0d0b16"],
}
CUTS = [0.62, 0.42, 0.2, -0.02, -0.24, -0.46]  # light value -> tones 1..6 (small even steps)
HEAD_C = np.array([15.5, 31.0])  # centre of the hair volume


class Prim:
    def __init__(self, inside, normal, u=None, kind="blob"):
        self.inside, self.normal = inside, normal
        self.u = u or (lambda x, y: np.zeros_like(x))
        self.kind = kind


def blob(cx, cy, rx, ry, ymax=None, arch=0.0):
    """Ellipsoid; ymax clips the bottom, arch bends that clip into a hairline (lower at the temples)."""
    inside, normal = B.ellipsoid(cx, cy, rx, ry)
    if ymax is None:
        return Prim(inside, normal)
    return Prim(lambda x, y: inside(x, y) & (y < ymax + arch * (x - cx) ** 2), normal)


def strand(p0, p1, p2, r0, r1, n=10):
    """Curved tapered lock: quadratic bezier p0 (root) -> p2 (tip) via p1, radius r0 -> r1."""
    t = np.linspace(0, 1, n + 1)
    pts = ((1 - t) ** 2)[:, None] * np.array(p0) + (2 * (1 - t) * t)[:, None] * np.array(p1) \
        + (t ** 2)[:, None] * np.array(p2)
    rad = r0 + (r1 - r0) * t ** 0.85
    segs = [(pts[i], pts[i + 1], rad[i], rad[i + 1], t[i], t[i + 1]) for i in range(n)]

    def nearest(x, y):
        best = np.full(x.shape, np.inf)
        out = [np.zeros_like(x) for _ in range(4)]  # qx, qy, r, u
        for a, b, ra, rb, ta, tb in segs:
            ab = b - a
            L2 = max(ab @ ab, 1e-9)
            s = np.clip(((x - a[0]) * ab[0] + (y - a[1]) * ab[1]) / L2, 0, 1)
            qx, qy, r = a[0] + s * ab[0], a[1] + s * ab[1], ra + (rb - ra) * s
            d = np.hypot(x - qx, y - qy) / r
            m = d < best
            best = np.where(m, d, best)
            for o, v in zip(out, (qx, qy, r, ta + (tb - ta) * s)):
                o[m] = v[m]
        return best, out

    def inside(x, y):
        return nearest(x, y)[0] < 1

    def normal(x, y):
        _, (qx, qy, r, _) = nearest(x, y)
        nx, ny = (x - qx) / r, (y - qy) / r
        nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        n_ = np.stack([nx, ny, nz], -1)
        return n_ / np.linalg.norm(n_, axis=-1, keepdims=True).clip(1e-6)

    return Prim(inside, normal, u=lambda x, y: nearest(x, y)[1][3], kind="strand")


def mirror(*pts):
    return [(31 - p[0], p[1]) for p in pts]


def pair(p0, p1, p2, r0, r1):
    return [strand(p0, p1, p2, r0, r1), strand(*mirror(p0, p1, p2), r0, r1)]


def cap(rx, ry, cy, ymax, arch=0.0):
    """Hair shell hugging the skull (head: centre 15.5,33 radii 12.6 x 11.8)."""
    return blob(15.5, cy, rx, ry, ymax=ymax, arch=arch)


# ---- six everyday office styles (front view). Lists are back -> front. ---------------------------
STYLES = {
    "neat": {"name": "Neat Short", "gender": "male", "front": [
        cap(13.8, 9.9, 29.4, 27.4, arch=0.02),                     # gently arched hairline
        *pair((5.2, 24.5), (3.7, 28), (4.3, 32.3), 2.7, 1.3),       # short, tidy temples
        strand((11, 20.5), (6.8, 21.2), (4.6, 26.5), 3.1, 1.8),     # left of a soft part
        strand((11, 20.2), (18, 18.4), (25.6, 23.4), 3.4, 2.3),     # top combed to the right
        strand((11, 23.0), (18, 21.6), (26.6, 27.4), 3.1, 1.7),
        strand((9.6, 24.6), (10.8, 27.4), (12.0, 29.6), 2.5, 0.9),  # short textured fringe on the forehead
        strand((13.8, 24.4), (15.2, 27.4), (16.4, 29.4), 2.5, 0.9),
        strand((18.0, 24.4), (19.6, 27.0), (20.8, 28.8), 2.3, 0.9),
        strand((22.0, 24.6), (23.6, 26.6), (24.4, 28.4), 2.0, 0.8),
    ]},
    "sidepart": {"name": "Classic Side Part", "gender": "male", "front": [
        cap(14.0, 10.2, 29.2, 26.8, arch=0.024),
        *pair((5.0, 25.5), (3.8, 28.6), (4.4, 32.4), 2.5, 1.1),
        strand((10.2, 20.2), (6.4, 21.8), (4.4, 27.8), 3.0, 1.7),   # small side of the part
        strand((10.6, 19.2), (19, 16.9), (26.8, 23.8), 3.9, 2.5),   # volume swept up and over
        strand((10.6, 22.0), (19, 20.1), (27.4, 28.0), 3.4, 1.7),
        strand((11.0, 23.6), (16.6, 22.2), (21.6, 24.6), 2.2, 1.0),  # lifted front
        strand((10.4, 24.2), (15.6, 26.6), (23.4, 30.8), 3.0, 1.0),  # swoop across the forehead
    ]},
    "up": {"name": "Short Lifted Front", "gender": "male", "front": [
        cap(14.0, 10.4, 29.4, 25.8, arch=0.034),                   # hairline arches up at the centre
        blob(15.5, 22.4, 10.4, 5.0),                                # a little height at the front, round
        # front locks lift off the forehead and sweep up + back to the right; drawn tip -> root so the
        # roots / underside sit darker and the lifted tips catch the light
        strand((9.2, 21.8), (7.4, 24.4), (6.8, 27.4), 1.7, 2.4),
        strand((13.4, 20.2), (10.8, 23.2), (9.8, 26.8), 2.0, 2.8),
        strand((17.6, 19.6), (15.0, 22.6), (13.6, 26.0), 2.2, 3.0),
        strand((21.4, 20.0), (19.2, 22.6), (17.8, 25.8), 2.2, 3.0),
        strand((24.6, 21.2), (23.0, 23.6), (21.8, 26.2), 2.0, 2.8),
        strand((27.0, 23.6), (26.0, 25.4), (25.0, 27.2), 1.5, 2.3),
    ]},
    "short": {"name": "Short Layered", "gender": "female", "front": [
        cap(14.8, 11.6, 29.8, 31.0),                                # round, smooth top
        strand((4.8, 27), (3.0, 32.4), (4.6, 38.0), 3.4, 1.8),      # ear-length sides, tips tuck in
        strand((26.2, 27), (28.0, 32.4), (26.4, 38.0), 3.4, 1.8),
        strand((7.4, 29), (6.4, 33.4), (7.4, 37.0), 2.0, 0.9),
        strand((23.6, 29), (24.6, 33.4), (23.6, 37.0), 2.0, 0.9),
        strand((18.6, 23.6), (13, 24.6), (8.0, 30.6), 3.2, 1.0),    # soft side-swept bangs
        strand((19.6, 24.0), (16.4, 27.0), (13.6, 31.0), 2.6, 0.8),
        strand((20.6, 24.0), (23.4, 26.8), (24.6, 30.6), 2.4, 0.9),
    ]},
    "ponytail": {"name": "Low Ponytail", "gender": "female",
                 "back": [strand((21, 40), (26.5, 45), (25.0, 53.5), 3.2, 1.4)],  # tail over a shoulder
                 "front": [
        cap(14.0, 10.6, 29.4, 25.4, arch=0.06),
        strand((15.5, 19.8), (8.4, 21.0), (4.4, 30.6), 3.4, 2.0),   # centre part, pulled back smooth
        strand((15.5, 19.8), (22.6, 21.0), (26.6, 30.6), 3.4, 2.0),
        strand((15.5, 22.4), (10.0, 23.4), (6.2, 31.0), 2.6, 1.3),
        strand((15.5, 22.4), (21.0, 23.4), (24.8, 31.0), 2.6, 1.3),
    ]},
    "hime": {"name": "Hime Cut", "gender": "female",
             "back": [blob(15.5, 40.0, 14.2, 18.0, ymax=57.4)],            # long straight hair, blunt ends
             "front": [
        cap(14.8, 11.6, 29.8, 31.6),                                # round, smooth top
        strand((4.4, 27.5), (3.8, 35.5), (4.2, 43.4), 3.4, 3.1),    # blunt cheek-length side locks
        strand((26.6, 27.5), (27.2, 35.5), (26.8, 43.4), 3.4, 3.1),
        strand((7.4, 30.0), (7.2, 37.0), (7.4, 43.2), 2.2, 2.0),
        strand((23.6, 30.0), (23.8, 37.0), (23.6, 43.2), 2.2, 2.0),
        *[strand((x, 26.4), (x, 28.8), (x, 31.0), 2.3, 2.1)         # straight blunt fringe at the brow
          for x in (7.6, 11.6, 15.5, 19.4, 23.4)],
    ]},
}

NB4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
FRINGE_ALPHA = (80, 34)   # soft shadow the fringe casts on the skin below it (row 1, row 2)


def soften(v, mask, k=0.5):
    """Blend each light value with its masked 3x3 neighbourhood — rounder, gentler tone bands."""
    p = np.pad(np.where(mask, v, 0), 1)
    c = np.pad(mask.astype(float), 1)
    s = sum(p[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
    n = sum(c[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
    return np.where(mask, (1 - k) * v + k * s / np.maximum(n, 1), v)


def render(prims, pal, skin_mask, back=False):
    """Returns (RGBA image, hair mask)."""
    owner = np.full((H, W), -1, int)
    for i, p in enumerate(prims):
        owner[B.coverage(p.inside) >= 0.5] = i
    mask = owner >= 0
    sph = np.stack([(PX - HEAD_C[0]) / 15.0, (PY - HEAD_C[1]) / 15.0], -1)
    sph = np.concatenate([sph, np.sqrt(np.clip(1 - (sph ** 2).sum(-1, keepdims=True), 0.05, 1))], -1)
    sph /= np.linalg.norm(sph, axis=-1, keepdims=True)
    v_all = np.zeros((H, W))
    gloss = np.zeros((H, W), bool)
    for i, p in enumerate(prims):
        m = owner == i
        if not m.any():
            continue
        nl = p.normal(PX, PY)
        n = 0.45 * nl + 0.55 * sph if not back else 0.7 * nl + 0.3 * sph
        n /= np.linalg.norm(n, axis=-1, keepdims=True)
        u = p.u(PX, PY)
        v = B.lambert(n) - 0.16 * u                     # locks darken toward the tips
        v_all[m] = v[m]
        lit = B.lambert(nl)
        if p.kind == "strand":  # thin streak down the lit side of the lock, upper part only
            g = (lit > 0.64) & (u > 0.1) & (u < 0.45)
        else:                   # cap: a short arc on the upper-left of the dome
            g = (nl[..., 1] > -0.8) & (nl[..., 1] < -0.56) & (nl[..., 0] > -0.7) & (nl[..., 0] < 0.1)
        gloss |= m & g & (v > 0.18)
    v_all -= np.clip((PY - 33) / 32, 0, 0.32)          # lower hair sits in shadow
    if back:
        v_all -= 0.4
    v_all = soften(soften(v_all, mask), mask)
    tone = np.full((H, W), -1, int)
    tone[mask] = B.band(v_all, CUTS)[mask] + 1         # 1 highlight .. 7 (clamped to 6)
    tone[mask & (tone > 6)] = 6
    if not back:
        halo = np.zeros_like(gloss)
        halo[1:] |= gloss[:-1]; halo[:-1] |= gloss[1:]; halo[:, 1:] |= gloss[:, :-1]; halo[:, :-1] |= gloss[:, 1:]
        tone[mask & halo & (tone > 2)] -= 1             # highlight fades into its surroundings
        tone[gloss] = 0
    tone = B.despeckle(tone, mask)
    # edges: outer silhouette -> outline; on skin -> deep tone; over another lock -> 2 tones darker
    p_own = np.pad(owner, 1, constant_values=-1)
    p_skin = np.pad(skin_mask, 1)
    base = tone.copy()
    for dy, dx in NB4:
        nb_own = p_own[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
        nb_skin = p_skin[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
        out = mask & (nb_own < 0)
        tone[out & ~nb_skin] = 7
        tone[out & nb_skin & (tone != 7)] = 6
        sep = mask & (nb_own >= 0) & (nb_own < owner) & (dy >= 0) & (PY > 23) & (tone < 6)
        tone[sep] = np.minimum(base[sep] + 2, 6)
    im = np.zeros((H, W, 4), np.uint8)
    for k, c in enumerate(pal):
        im[tone == k] = list(hx(c)) + [255]
    if not back:  # the fringe casts a soft shadow onto the skin just below it
        below = np.zeros((H, W), bool)
        below[1:] = mask[:-1]
        below2 = np.zeros((H, W), bool)
        below2[2:] = mask[:-2]
        im[skin_mask & ~mask & below] = [70, 30, 50, FRINGE_ALPHA[0]]
        im[skin_mask & ~mask & ~below & below2 & (PY < 34)] = [70, 30, 50, FRINGE_ALPHA[1]]
    return Image.fromarray(im), mask


if __name__ == "__main__":
    tone, head, owner = B.build_body()
    skin = tone >= 0
    body_img = B.paint(tone, B.TONES[B.DEFAULT])
    face = B.face_layer()
    pal = COLORS["black"]
    looks = []
    for s, st in STYLES.items():
        front, _ = render(st["front"], pal, skin)
        back = render(st["back"], pal, skin, back=True)[0] if "back" in st else None
        front.save(OUT / f"hair32_{s}_front.png")
        if back is not None:
            back.save(OUT / f"hair32_{s}_front_back.png")
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if back is not None:
            im.alpha_composite(back)
        for layer in (body_img, face, front):
            im.alpha_composite(layer)
        looks.append(im)
    gap = 6
    top = floor_bg(gap + len(looks) * (W + gap), gap + H + gap)
    for i, im in enumerate(looks):
        top.alpha_composite(im, (gap + i * (W + gap), gap))
    top.resize((top.width * 8, top.height * 8), Image.NEAREST).convert("RGB").save(OUT / "hair32-front-review.png")
    print("ok")
