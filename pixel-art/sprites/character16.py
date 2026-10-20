"""Character kit v3 — 16x32 CHIBI base body (style of the user's Pinterest 16x32 reference, made
cuter on request): very big round head with ear bumps (~60% of the figure), tiny body,
stubby arms with hands at the sides, short legs with a dark gap, little feet.
Hand-drawn as a template grid (not traced).

Letters: o outline, 1 light, 2 base, 3 shade, 4 deep shade, . empty.  Face is a separate layer.

  body16_front.png            16x32  skin only, no face (default tone)
  body16_front_<tone>.png     16x32  4 skin tones
  face16_front.png            16x32  face layer: eyes + blush (stack on top of the body)
  body16_front_x2.png         32x64  the body pixel-doubled, for the 32 px furniture grid
Outputs in ./character/ + body16-preview.png
"""
from pathlib import Path

from PIL import Image

from kit import OL, floor_bg, hx

OUT = Path(__file__).parent / "character"
OUT.mkdir(exist_ok=True)
W, H = 16, 32
TONES = {
    "light":  ["#fff4e8", "#fde3cc", "#ecc6a6", "#d6a886"],
    "medium": ["#ffe6cc", "#f6cba4", "#dea982", "#c48a64"],
    "tan":    ["#f3c896", "#dca772", "#bc8656", "#9c6a40"],
    "deep":   ["#c08c64", "#a06e4a", "#7e5234", "#5e3a22"],
}
DEFAULT = "medium"

BODY = [  # chibi: head ~ 60% of the figure, tiny body, stubby arms + legs
    "................",  # 0-9 free for hair / hats
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "....oooooooo....",  # 10 top of the big head — shaded like a sphere:
    "...o11122222o...",  #    highlight top-left, base, shade crescent right + bottom
    "..o1111222222o..",
    ".o111122222223o.",
    ".o112222222223o.",
    ".o122222222233o.",
    "o31222222222233o",  # 16 ear bumps
    "o32222222222333o",
    ".o222222222333o.",
    ".o322222223334o.",
    "..o3222223334o..",
    "...o33333444o...",  # 21 jaw (darkest at the bottom-right)
    "....oo3333oo....",  # 22 chin shadow
    "....o122223o....",  # 23 tiny shoulders
    "..oo13222232oo..",  # 24 stubby arms
    ".o11o222222o23o.",  # 25 round little hands (2x2 blobs)
    ".o12o222222o33o.",
    "..ooo333333ooo..",  # 27 hips
    "....o33oo33o....",  # 28 short legs
    "....o23oo23o....",  # 29 legs end in soft rounded nubs (no separate feet)
    ".....oo..oo.....",
    "................",  # 31 contact shadow row
]
FACE = {(5, 18): "e", (5, 19): "e", (10, 18): "e", (10, 19): "e",   # eyes: 1x2 dark dashes
        (3, 19): "b", (12, 19): "b"}                                 # blush


def render(rows, sk):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pal = {"o": hx(OL), "1": hx(sk[0]), "2": hx(sk[1]), "3": hx(sk[2]), "4": hx(sk[3])}
    for y, r in enumerate(rows):
        assert len(r) == W, (y, len(r))
        for x, ch in enumerate(r):
            if ch in pal:
                im.putpixel((x, y), pal[ch] + (255,))
    for x in range(4, 12):                                    # short contact shadow under the feet
        im.putpixel((x, 31), (40, 24, 30, 70))
    return im


def render_face():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for (x, y), k in FACE.items():
        im.putpixel((x, y), hx("#2b2230") + (255,) if k == "e" else hx("#f2a0b4") + (255,))
    return im


if __name__ == "__main__":
    bodies = {t: render(BODY, p) for t, p in TONES.items()}
    for t, im in bodies.items():
        im.save(OUT / f"body16_front_{t}.png")
    bodies[DEFAULT].save(OUT / "body16_front.png")
    face = render_face()
    face.save(OUT / "face16_front.png")
    bodies[DEFAULT].resize((W * 2, H * 2), Image.NEAREST).save(OUT / "body16_front_x2.png")

    # preview row 1: native 16x32 — bare body in 4 tones, then body + face
    gap = 6
    items = [bodies[t] for t in TONES]
    withface = bodies[DEFAULT].copy()
    withface.alpha_composite(face)
    items.append(withface)
    w1 = sum(i.width for i in items) + gap * (len(items) + 1)
    row1 = floor_bg(w1, H + 2 * gap)
    x = gap
    for im in items:
        row1.alpha_composite(im, (x, gap))
        x += im.width + gap
    row1 = row1.resize((row1.width * 10, row1.height * 10), Image.NEAREST)
    # preview row 2: the x2 body next to the chair + desk (the office furniture grid)
    root = Path(__file__).parent
    big = withface.resize((W * 2, H * 2), Image.NEAREST)
    stuff = [big, Image.open(root / "chair" / "chair_front.png"), Image.open(root / "desk" / "desk_front.png")]
    h2 = max(i.height for i in stuff) + 2 * gap
    w2 = sum(i.width for i in stuff) + gap * (len(stuff) + 1)
    row2 = floor_bg(w2, h2)
    x = gap
    for im in stuff:
        row2.alpha_composite(im, (x, h2 - gap - im.height))
        x += im.width + gap
    row2 = row2.resize((row2.width * 5, row2.height * 5), Image.NEAREST)
    sheet = Image.new("RGB", (max(row1.width, row2.width), row1.height + row2.height + 30), (38, 36, 48))
    sheet.paste(row1.convert("RGB"), (0, 0))
    sheet.paste(row2.convert("RGB"), (0, row1.height + 30))
    sheet.save(OUT / "body16-preview.png")
    print("ok")
