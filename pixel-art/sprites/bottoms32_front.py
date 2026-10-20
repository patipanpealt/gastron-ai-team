"""Character kit v4 — BOTTOMS for the 32x64 chibi, FRONT view only (design review, no sheets yet).

Five pieces: office slacks, jeans, shorts, pencil skirt, pleated skirt. Built exactly like the tops
(clothes32_front.py): pieces on the body's own leg tubes / torso ellipsoid, same light, same 5-tone
ramps with hue-shifted shadows, selective outline.

Only ~5 px of the body sits below a top's hem, so each bottom is designed to read in that strip:
crease line, hem cuffs, fade highlights, pleat ridges (the pleats are real ripples in the normal map,
so they shade smoothly instead of being drawn as stripes).

Draw order per cell: hair back -> body -> BOTTOM -> TOP -> face -> hair front

  character32/clothes/bottom32_<name>_front.png
  character32/clothes/bottoms32-front-review.png   bottoms alone + styled outfits with hair
"""
from pathlib import Path

import numpy as np
from PIL import Image

import character32_front as B
import clothes32_front as C
import hair32_front as HAIR
from clothes32_front import Piece, both, ell, minus, poly, torso
from kit import floor_bg, hx

OUT = C.OUT
W, H, PX, PY = B.W, B.H, B.PX, B.PY

C.PALETTES.update({  # highlight, light, base, shade, deep, outline
    "slacks": ["#8e94ae", "#666c88", "#4a4f6a", "#363a54", "#262944", "#0f1020"],
    "jeans":  ["#b0d0f2", "#76a0d6", "#5280ba", "#3b629f", "#294a80", "#101c3c"],
    "khaki":  ["#fff2cc", "#eed59e", "#d4b678", "#ac8c54", "#836a3a", "#3a2a10"],
    "wine":   ["#e89aa8", "#bc5870", "#92354f", "#6e2339", "#4e172a", "#220913"],
})

LEG_Y0, LEG_Y1, LEG_R = 53.0, 59.6, 2.9
LEGS = [(12.6, B.capsule(12.6, LEG_Y0, 12.6, LEG_Y1, LEG_R + 0.45, LEG_R + 0.45)),
        (19.4, B.capsule(19.4, LEG_Y0, 19.4, LEG_Y1, LEG_R + 0.45, LEG_R + 0.45))]
BELOW = lambda y0: (lambda x, y: y > y0)  # noqa: E731
ABOVE = lambda y0: (lambda x, y: y < y0)  # noqa: E731


def trouser_normal(x, y):
    """Two leg cylinders joined at the hips: each leg shades round about its own centre line."""
    cx = np.where(x < 16.0, 12.6, 19.4)
    nx = np.clip((x - cx) / 3.5, -1, 1)
    n = np.stack([nx, np.full_like(x, 0.22), np.sqrt(np.clip(1 - nx * nx, 0.05, 1))], -1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def trouser_region(y0, y1, notch_from=59.2):
    """Hips + both legs between y0 and y1; a 1 px gap between the legs below `notch_from`."""
    hip = torso(0.5)[0]
    l1, l2 = LEGS[0][1][0], LEGS[1][1][0]
    return lambda x, y: ((hip(x, y) | l1(x, y) | l2(x, y)) & (y > y0) & (y < y1)
                         & ~((y > notch_from) & (np.abs(x - 16.0) < 0.55)))


def leg_pieces(pal, hem, **kw):
    """Trousers from the waist (y 53.4) to `hem`, one smooth piece."""
    return [Piece(trouser_region(53.4, hem), trouser_normal, pal, **kw)]


def hip_piece(pal, y0=53.2, y1=58.4):
    return None


def hem_band(pal, y0, y1, shift=1):
    return [Piece(trouser_region(y0, y1), trouser_normal, pal, shift=shift)]


def cyl_normal(cx, hw, tilt=0.25):
    def normal(x, y):
        nx = np.clip((x - cx) / hw, -1, 1)
        n = np.stack([nx, np.full_like(x, tilt), np.sqrt(np.clip(1 - nx * nx, 0.05, 1))], -1)
        return n / np.linalg.norm(n, axis=-1, keepdims=True)
    return normal


def pleat_normal(cx, hw, period=3.3, amp=0.55):
    """A-line skirt whose surface ripples in pleats — shading comes from the normals."""
    def normal(x, y):
        base_nx = np.clip((x - cx) / hw, -1, 1)
        ridge = amp * np.sin(2 * np.pi * (x - cx) / period)
        nx = np.clip(base_nx * 0.7 + ridge, -0.95, 0.95)
        n = np.stack([nx, np.full_like(x, 0.3), np.sqrt(np.clip(1 - nx * nx, 0.05, 1))], -1)
        return n / np.linalg.norm(n, axis=-1, keepdims=True)
    return normal


FLAT = C.flat_normal

BOTTOMS = {
    "slacks": {"name": "Office Slacks", "pieces": [
        *leg_pieces("slacks", 61.2),
        *hem_band("slacks", 60.0, 61.2, shift=-1),                              # hem turned under
    ], "details": [*[((12, y), 3, "slacks") for y in range(56, 60)],           # front crease, left leg
                   *[((19, y), 3, "slacks") for y in range(56, 60)],           # front crease, right leg
                   ((11, 55), 0, "slacks"), ((20, 55), 0, "slacks")]},
    "jeans": {"name": "Jeans", "pieces": [
        *leg_pieces("jeans", 61.6),
        *hem_band("jeans", 59.6, 61.6, shift=1),                                # rolled cuff
    ], "details": [((11, 56), 0, "jeans"), ((12, 56), 1, "jeans"), ((11, 57), 1, "jeans"),   # knee fade
                   ((19, 56), 0, "jeans"), ((20, 56), 1, "jeans"), ((20, 57), 1, "jeans"),
                   *[((x, 59), 4, "jeans") for x in (10, 11, 12, 13, 18, 19, 20, 21)],       # cuff stitch
                   ((15, 55), 3, "jeans"), ((16, 55), 3, "jeans"), ((15, 56), 4, "jeans"), ((16, 56), 4, "jeans")]},
    "shorts": {"name": "Shorts", "pieces": [
        *leg_pieces("khaki", 58.6),
        *hem_band("khaki", 57.4, 58.6, shift=1),                                # folded hem
    ], "details": [((11, 55), 0, "khaki"), ((20, 55), 0, "khaki"),
                   ((15, 55), 3, "khaki"), ((16, 55), 3, "khaki")]},
    "pencil": {"name": "Pencil Skirt", "pieces": [
        Piece(poly((8.6, 53.6), (22.4, 53.6), (21.0, 60.8), (10.0, 60.8)), cyl_normal(15.5, 7.4), "navy"),
        Piece(poly((9.6, 59.6), (21.4, 59.6), (21.0, 60.8), (10.0, 60.8)), cyl_normal(15.5, 7.4), "navy", shift=-1),
    ], "details": [*[((15, y), 4, "navy") for y in (56, 57, 58)], ((16, 58), 4, "navy"),   # centre seam
                   ((12, 55), 0, "navy"), ((19, 56), 1, "navy")]},
    "pleated": {"name": "Pleated Skirt", "pieces": [
        Piece(poly((8.6, 53.6), (22.4, 53.6), (25.4, 60.4), (5.6, 60.4)), pleat_normal(15.5, 10.0), "wine"),
        Piece(poly((6.0, 59.0), (25.0, 59.0), (25.4, 60.4), (5.6, 60.4)), pleat_normal(15.5, 10.0), "wine", shift=-1),
    ], "details": []},
}


if __name__ == "__main__":
    tone, head, owner = B.build_body()
    skin = tone >= 0
    body_img = B.paint(tone, B.TONES[B.DEFAULT])
    face = B.face_layer()
    layers = {}
    for name, bot in BOTTOMS.items():
        layers[name] = C.render(bot, skin)
        layers[name].save(OUT / f"bottom32_{name}_front.png")
    tops = {n: Image.open(OUT / f"top32_{n}_front.png") for n in C.TOPS}

    def hair_layers(style):
        st = HAIR.STYLES[style]
        hf, _ = HAIR.render(st["front"], HAIR.COLORS["black"], skin)
        hb = HAIR.render(st["back"], HAIR.COLORS["black"], skin, back=True)[0] if "back" in st else None
        return hf, hb

    outfits = [("slacks", "shirt", "neat"), ("jeans", "tee", "up"), ("shorts", "tank", "short"),
               ("pencil", "suit", "hime"), ("pleated", "tee", "ponytail")]

    def compose(bottom, top, hair):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        hf, hb = hair_layers(hair) if hair else (None, None)
        if hb is not None:
            im.alpha_composite(hb)
        parts = [body_img]
        if bottom:
            parts.append(layers[bottom])
        if top:
            parts.append(tops[top])
        parts.append(face)
        if hf is not None:
            parts.append(hf)
        for l in parts:
            im.alpha_composite(l)
        return im

    gap = 6
    names = list(BOTTOMS)
    sheet = floor_bg(gap + len(names) * (W + gap), gap + 2 * (H + gap))
    for i, n in enumerate(names):
        sheet.alpha_composite(compose(n, None, None), (gap + i * (W + gap), gap))
    for i, (b, t, h) in enumerate(outfits):
        sheet.alpha_composite(compose(b, t, h), (gap + i * (W + gap), gap + H + gap))
    sheet.resize((sheet.width * 7, sheet.height * 7), Image.NEAREST).convert("RGB").save(
        OUT / "bottoms32-front-review.png")
    print("ok")
