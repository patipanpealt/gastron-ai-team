"""Character kit, layer 0 — the bare BODY (skin only, no face), front view.
Every outfit / hair / face piece will be drawn as a separate transparent layer on the same
32x48 canvas and stacked on top of this, so the body defines the anchor boxes they use.

Proportions: friendly cartoon human (head ~1/3 of the height) with organic shapes — rounded
skull + tapering jaw, neck, sloped shoulders, waist and hips, arms hanging from the shoulders,
legs tapering through the knee to the ankle, feet planted on a short contact shadow. Top-down cue: the crown of the
head is the brightest band; light from the upper-left, full dark outline.

  body_front.png              32x48  default skin tone
  body_front_<tone>.png       32x48  the same body in 4 skin tones (light / medium / tan / deep)
  body_layout.json            anchor boxes per body part (for building clothes/hair/face layers)
Outputs in ./character/ + body-preview.png (tones + next to the chair and desk for scale)
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

from kit import Sprite, floor_bg, hx

OUT = Path(__file__).parent / "character"
OUT.mkdir(exist_ok=True)
W, H = 32, 48
TONES = {
    "light":  ["#ffeede", "#fbd9bd", "#efc09c", "#d9a27c", "#b47e5a"],
    "medium": ["#ffe2c4", "#f5c9a0", "#e0a87c", "#c4865c", "#9c6440"],
    "tan":    ["#f6c99c", "#dfa877", "#c68a5a", "#a66e44", "#7e5032"],
    "deep":   ["#c8916a", "#a8714c", "#8c5a3a", "#6e432a", "#4e2e1c"],
}
DEFAULT = "medium"

# Hand-placed silhouette: per body part, the inner pixel span (x0..x1 inclusive) of every row.
# Clean, gradual edges + flat 4-tone shading = a smooth body (no stray dots / lumps).
SPANS = {
    "head":  {2: (12, 19), 3: (10, 21), **{y: (9, 22) for y in range(4, 13)}, 13: (10, 21), 14: (11, 20), 15: (13, 18)},
    "ears":  {y: [(7, 8), (23, 24)] for y in range(8, 12)},
    "neck":  {16: (14, 18), 17: (14, 18)},
    "torso": {18: (12, 20), 19: (10, 22), 20: (9, 23), 21: (8, 24),
              **{y: (11, 21) for y in range(22, 26)}, **{y: (12, 20) for y in range(26, 29)},
              **{y: (11, 21) for y in range(29, 33)}},
    "arms":  {y: [(7, 9), (23, 25)] for y in range(22, 31)},
    "hands": {31: [(6, 9), (23, 26)], 32: [(6, 9), (23, 26)], 33: [(7, 9), (23, 25)]},
    "legs":  {**{y: [(12, 15), (17, 20)] for y in range(33, 41)}, **{y: [(13, 15), (17, 19)] for y in range(41, 44)}},
    "feet":  {44: [(11, 15), (17, 21)], 45: [(11, 15), (17, 21)]},
}


def bbox(part):
    xs, ys = [], []
    for y, sp in SPANS[part].items():
        for a, b in (sp if isinstance(sp, list) else [sp]):
            xs += [a, b]
            ys.append(y)
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


LAYOUT = {k: bbox(k) for k in SPANS}
LAYOUT["face"] = (10, 7, 22, 15)


def fill_span(s, y, a, b, sk, lit_row=False, dark_row=False):
    w = b - a + 1
    for x in range(a, b + 1):
        i = x - a
        c = sk[1]
        if i == 0 and w > 2:
            c = sk[0]
        if i == w - 1:
            c = sk[3]
        elif i == w - 2 and w > 4:
            c = sk[2]
        if lit_row and i < w - 2:
            c = sk[0]
        if dark_row:
            c = sk[2] if i < w - 1 else sk[3]
        s.px(x, y, c)


def draw_body(sk):
    s = Sprite(W, H)
    s.a[46:48, 10:23] = list(hx("#28181e")) + [70]           # short contact shadow under the feet
    order = ["legs", "feet", "arms", "hands", "torso", "neck", "ears", "head"]
    for part in order:
        for y, sp in SPANS[part].items():
            for a, b in (sp if isinstance(sp, list) else [sp]):
                lit = (part == "head" and y <= 5) or (part == "torso" and y <= 19) or (part == "feet" and y == 44)
                dark = (part == "neck") or (part == "head" and y == 15) or (part == "ears")
                fill_span(s, y, a, b, sk, lit_row=lit, dark_row=dark)
    s.px(11, 3, "#ffffff")                                   # sheen on the crown
    s.hline(14, 19, 16, sk[3])                               # shadow under the chin
    s.finish(shadow=False, full_outline=True, rim=0)
    return s


if __name__ == "__main__":
    bodies = {t: draw_body(p) for t, p in TONES.items()}
    for t, b in bodies.items():
        b.image().save(OUT / f"body_front_{t}.png")
    bodies[DEFAULT].image().save(OUT / "body_front.png")
    (OUT / "body_layout.json").write_text(json.dumps(
        {"canvas": [W, H], "anchor_feet": [16, 46], "parts": LAYOUT,
         "note": "Draw each clothing / hair / face layer on its own 32x48 transparent canvas and stack it on top."},
        indent=2))
    # preview: 4 tones, then the default body beside the chair + desk for scale
    root = Path(__file__).parent
    items = [bodies[t].image() for t in TONES] + [Image.open(root / "chair" / "chair_front.png"),
                                                  Image.open(root / "desk" / "desk_front.png")]
    gap = 8
    Hh = max(i.height for i in items) + 2 * gap
    Ww = sum(i.width for i in items) + gap * (len(items) + 1)
    scene = floor_bg(Ww, Hh)
    x = gap
    for im in items:
        scene.alpha_composite(im, (x, Hh - gap - im.height))
        x += im.width + gap
    big = scene.convert("RGB").resize((Ww * 6, Hh * 6), Image.NEAREST)
    # close-up with the anchor boxes drawn faintly
    z = 12
    zoom = Image.alpha_composite(floor_bg(W, H), bodies[DEFAULT].image()).resize((W * z, H * z), Image.NEAREST)
    g = np.array(zoom).astype(float)
    for name, box in LAYOUT.items():
        for (a, b, c, d) in (box if isinstance(box, list) else [box]):
            for xx in (a * z, c * z - 1):
                g[b * z:d * z, xx, :3] = g[b * z:d * z, xx, :3] * 0.5 + np.array([60, 140, 255]) * 0.5
            for yy in (b * z, d * z - 1):
                g[yy, a * z:c * z, :3] = g[yy, a * z:c * z, :3] * 0.5 + np.array([60, 140, 255]) * 0.5
    zoom = Image.fromarray(g.astype(np.uint8))
    sheet = Image.new("RGB", (big.width + zoom.width + 30, max(big.height, zoom.height)), (38, 36, 48))
    sheet.paste(big, (0, 0))
    sheet.paste(zoom.convert("RGB"), (big.width + 30, 0))
    sheet.save(OUT / "body-preview.png")
    print("ok")
