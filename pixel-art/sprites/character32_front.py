"""Character kit v4 — 32x64 chibi BODY, front view (review stage: front only, no sheets yet).

Same chibi proportions as the 16x32 base (character16.py) at twice the resolution, rebuilt so the
shading follows real curvature: every part is an analytic volume (sphere / ellipsoid / capsule), its
surface normal is lit from the upper-left-front, and the light value is banded into 5 skin tones.
That gives round, curved tone bands instead of stepped blocks. Parts overlap back-to-front and get an
outline only where a front part crosses another (hands over the body, chin over the neck).

Shared helpers here (LIGHT, shade(), tones()) are reused by hair32_front.py.

  character32/body32_front.png        32x64 body (default tone), no face
  character32/body32_front_<tone>.png 4 skin tones
  character32/face32_front.png        face layer (eyes with catch-light, brows-free, blush, mouth)
  character32/body32-preview.png      tones + face, on the floor, 8x
"""
from pathlib import Path

import numpy as np
from PIL import Image

from kit import OL, floor_bg, hx

OUT = Path(__file__).parent / "character32"
OUT.mkdir(exist_ok=True)
W, H = 32, 64
SS = 4  # supersampling for clean, round silhouettes

LIGHT = np.array([-0.45, -0.70, 0.55])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

TONES = {  # highlight, light, base, shade, deep
    "light":  ["#fff6ec", "#ffe6d2", "#f9d2b6", "#e8b292", "#c98f70"],
    "medium": ["#fff0dc", "#ffdcbc", "#f5c49e", "#dea27c", "#bb7e5c"],
    "tan":    ["#fbdcb4", "#ecbc8a", "#d69e6c", "#b8804e", "#8e5e38"],
    "deep":   ["#d8a47a", "#b98258", "#9c6844", "#7c4e30", "#5a3620"],
}
DEFAULT = "medium"

# pixel-centre grid and supersampled grid
PY, PX = np.mgrid[0:H, 0:W] + 0.5
SY, SX = (np.mgrid[0:H * SS, 0:W * SS] + 0.5) / SS


def coverage(fn):
    """Fraction of each pixel inside the shape (fn takes x, y arrays, returns bool)."""
    return fn(SX, SY).reshape(H, SS, W, SS).mean(axis=(1, 3))


# ---- analytic volumes: inside test + surface normal ---------------------------------------------
def ellipsoid(cx, cy, rx, ry, depth=1.0, squash_bottom=0.0):
    """Ellipse silhouette with an ellipsoid normal. squash_bottom narrows the lower half (a chin)."""
    def rxy(y):
        k = np.clip((y - cy) / ry, 0, 1)
        return rx * (1 - squash_bottom * k * k)

    def inside(x, y):
        return ((x - cx) / rxy(y)) ** 2 + ((y - cy) / ry) ** 2 < 1

    def normal(x, y):
        nx, ny = (x - cx) / rxy(y), (y - cy) / ry
        nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1)) * depth
        n = np.stack([nx, ny, nz], -1)
        return n / np.linalg.norm(n, axis=-1, keepdims=True).clip(1e-6)
    return inside, normal


def capsule(x0, y0, x1, y1, r0, r1=None):
    """Tapered capsule from (x0,y0) radius r0 to (x1,y1) radius r1 — arms, legs, hair strands."""
    r1 = r0 if r1 is None else r1
    a, b = np.array([x0, y0], float), np.array([x1, y1], float)
    ab = b - a
    L2 = max(ab @ ab, 1e-9)

    def closest(x, y):
        u = np.clip(((x - a[0]) * ab[0] + (y - a[1]) * ab[1]) / L2, 0, 1)
        return u, a[0] + u * ab[0], a[1] + u * ab[1], r0 + (r1 - r0) * u

    def inside(x, y):
        u, qx, qy, r = closest(x, y)
        return (x - qx) ** 2 + (y - qy) ** 2 < r * r

    def normal(x, y):
        u, qx, qy, r = closest(x, y)
        nx, ny = (x - qx) / r, (y - qy) / r
        nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        n = np.stack([nx, ny, nz], -1)
        return n / np.linalg.norm(n, axis=-1, keepdims=True).clip(1e-6)
    return inside, normal


def lambert(n):
    return np.clip(n @ LIGHT, -1, 1)


def band(v, cuts):
    """Light value -> tone index (0 = brightest) using descending cut points."""
    idx = np.full(v.shape, len(cuts), int)
    for i, c in reversed(list(enumerate(cuts))):
        idx[v > c] = i
    return idx


def despeckle(idx, mask, passes=2):
    """Remove lone pixels whose 4 neighbours all agree on another tone (keeps bands smooth)."""
    idx = idx.copy()
    for _ in range(passes):
        p = np.pad(idx, 1, mode="edge")
        nb = np.stack([p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]])
        same = (nb == nb[0]).all(0) & (nb[0] != idx) & mask
        idx[same] = nb[0][same]
    return idx


def edge(mask):
    """Pixels of mask that touch a non-mask pixel (4-neighbourhood) — the outline ring, inside."""
    p = np.pad(mask, 1)
    out = ~p[:-2, 1:-1] | ~p[2:, 1:-1] | ~p[1:-1, :-2] | ~p[1:-1, 2:]
    return mask & out


# ---- the body -------------------------------------------------------------------------------------
HEAD_C = (15.5, 33.0)
HEAD_R = (12.6, 11.8)
PARTS = [  # (group, volume) — drawn back to front
    ("leg",   capsule(12.6, 55.0, 12.6, 59.4, 2.9, 2.9)),
    ("leg",   capsule(19.4, 55.0, 19.4, 59.4, 2.9, 2.9)),
    ("torso", capsule(15.5, 45.5, 15.5, 47.0, 2.8)),                       # neck
    ("torso", ellipsoid(15.5, 51.2, 7.4, 6.6, depth=0.9)),                 # little round body
    ("arm",   capsule(9.6, 48.0, 7.0, 52.6, 2.5, 2.9)),                    # stubby arm, round hand end
    ("arm",   capsule(21.4, 48.0, 24.0, 52.6, 2.5, 2.9)),
    ("ear",   ellipsoid(3.4, 35.2, 2.7, 3.3)),
    ("ear",   ellipsoid(27.6, 35.2, 2.7, 3.3)),
    ("head",  ellipsoid(*HEAD_C, *HEAD_R, depth=0.95, squash_bottom=0.18)),
]
FRONT_OF = {"hand": {"torso", "leg", "arm"}, "head": {"torso", "ear"}, "arm": {"torso"}, "leg": set(),
            "torso": {"leg"}, "ear": set()}


def build_body():
    """Returns per-pixel tone index (-1 empty, 5 = outline) plus the head mask (for hair)."""
    idx = np.full((H, W), -1, int)
    owner = np.full((H, W), "", object)
    light = np.zeros((H, W))
    for group, (inside, normal) in PARTS:
        m = coverage(inside) >= 0.5
        n = normal(PX, PY)
        v = lambert(n)
        if group == "torso":
            v = v - 0.12  # sits in the head's shadow
        light[m] = v[m]
        owner[m] = group
        idx[m] = 0
    mask = idx >= 0
    # ambient occlusion: chin shadow on the neck/upper body, crease under the head
    hy = PY - HEAD_C[1]
    light[(owner == "torso") & (PY < 49.5)] -= 0.35
    tone = band(light, [0.78, 0.5, 0.12, -0.3])
    tone = despeckle(tone, mask)
    tone[~mask] = -1
    # outline: outer silhouette + where a front part overlaps a part it sits in front of
    out = edge(mask)
    p = np.pad(owner, 1, constant_values="")
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nb = p[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
        for g, behind in FRONT_OF.items():
            sel = (owner == g) & np.isin(nb, list(behind))
            if g == "arm":  # shoulders blend into the body — only outline the lower arm
                sel &= PY > 49.5
            out |= sel
    tone[out] = 5
    head = coverage(PARTS[-1][1][0]) >= 0.5
    ears = (owner == "ear")
    return tone, head | ears, owner


def paint(tone, pal):
    im = np.zeros((H, W, 4), np.uint8)
    cols = [hx(c) for c in pal] + [hx(OL)]
    for i, c in enumerate(cols):
        im[tone == i] = list(c) + [255]
    img = Image.fromarray(im)
    for x in range(10, 22):  # soft contact shadow
        if tone[63, x] < 0:
            img.putpixel((x, 63), (40, 24, 30, 70))
    return img


FACE = {
    # eyes: 2x4 dark ovals with a white catch-light top-left and a softer lower lid pixel
    "eye": [(10, 35), (11, 35), (10, 36), (11, 36), (10, 37), (11, 37), (10, 38), (11, 38),
            (20, 35), (21, 35), (20, 36), (21, 36), (20, 37), (21, 37), (20, 38), (21, 38)],
    "glint": [(10, 35), (20, 35)],
    "lid": [(11, 38), (21, 38)],
    "blush": [(6, 40), (7, 40), (8, 40), (23, 40), (24, 40), (25, 40)],
    "blush2": [(7, 41), (24, 41)],
    "mouth": [(15, 41), (16, 41)],
}


def face_layer():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    col = {"eye": "#2b2230", "glint": "#ffffff", "lid": "#5a4458", "blush": "#f7a7b8",
           "blush2": "#f4b9c4", "mouth": "#9a4a56"}
    for k in ("eye", "glint", "lid", "blush", "blush2", "mouth"):
        for p in FACE[k]:
            im.putpixel(p, hx(col[k]) + (255,))
    return im


if __name__ == "__main__":
    tone, head, _ = build_body()
    bodies = {t: paint(tone, p) for t, p in TONES.items()}
    for t, im in bodies.items():
        im.save(OUT / f"body32_front_{t}.png")
    bodies[DEFAULT].save(OUT / "body32_front.png")
    face = face_layer()
    face.save(OUT / "face32_front.png")
    gap = 6
    items = list(bodies.values())
    wf = bodies[DEFAULT].copy()
    wf.alpha_composite(face)
    items.append(wf)
    bg = floor_bg(len(items) * (W + gap) + gap, H + 2 * gap)
    for i, im in enumerate(items):
        bg.alpha_composite(im, (gap + i * (W + gap), gap))
    bg.resize((bg.width * 8, bg.height * 8), Image.NEAREST).convert("RGB").save(OUT / "body32-preview.png")
    print("ok")
