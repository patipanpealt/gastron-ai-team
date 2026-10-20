"""Sprite 07 — trash bins, seen from ABOVE (steep top-down, same scale as the desk/chair).

Top-down rules used here: the round opening / lid is the dominant shape (a big ellipse),
the body below it is short (heights x0.4), the inside of an open bin is visible.

  bin_office.png  24x24  open wastebasket: rim, liner folded over, the inner far wall,
                         crumpled paper + a red sticky note inside. Round → one sprite fits all sides.
  bin_pedal.png   32x36  pantry pedal bin: Gastron-red domed lid, brushed-steel body,
                         pedal at the front (south). Turn-independent enough to use one sprite.
Anchor by the bottom-centre.
Outputs in ./trash/: the PNGs + trash-preview.png (next to the desk + chair for scale)
"""
from pathlib import Path

from PIL import Image

from kit import PLASTIC, RED, Sprite, floor_bg

OUT = Path(__file__).parent / "trash"
OUT.mkdir(exist_ok=True)
STEEL = ["#eef1f5", "#d3d8df", "#b3bac5", "#8e96a3"]
BINC = ["#5d6577", "#474e5f", "#363c4a", "#262a35"]          # dark plastic bin
PAPER = ["#ffffff", "#ecebe4", "#cfccc0", "#a9a598"]


def in_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1


def cylinder(s, cx, top, rx, ry, h, ramp, taper=0.0, ribs=0):
    """Body of an upright cylinder below its top ellipse: front half only, lit left, dark right."""
    bottom = top + h
    for y in range(int(top), int(bottom + ry) + 1):
        t = min(1, max(0, (y - top) / h))
        r = rx - taper * t
        if y <= bottom:
            half = r
        else:                                                         # lower half of the bottom ellipse
            dy = (y - bottom) / ry
            if dy > 1:
                continue
            half = r * (1 - dy * dy) ** 0.5
        x0, x1 = int(round(cx - half)), int(round(cx + half))
        for x in range(x0, x1):
            u = (x - (cx - half)) / max(1, 2 * half)                 # 0 = left edge, 1 = right
            c = ramp[0] if u < 0.18 else ramp[1] if u < 0.62 else ramp[2] if u < 0.88 else ramp[3]
            if ribs and int(x - x0) % ribs == 0 and 0.1 < u < 0.92 and y < bottom:
                c = ramp[min(3, ramp.index(c) + 1)]
            s.px(x, y, c)


def paper_ball(s, cx, cy, r):
    s.disc(cx, cy, r, r * 0.85, PAPER[2])
    s.disc(cx - 0.4, cy - 0.4, r - 0.8, r * 0.85 - 0.8, PAPER[1])
    s.px(int(cx - r / 2), int(cy - r / 2), PAPER[0])
    s.px(int(cx), int(cy), PAPER[3])                                  # crumple crease
    s.px(int(cx + 1), int(cy - 1), PAPER[2])


# ============================================================ office bin ===
def draw_office():
    s = Sprite(24, 24)
    cx, top, rx, ry, h = 11.5, 10, 9, 7, 5                           # wide opening, short body
    cylinder(s, cx, top, rx - 0.5, ry, h, BINC, taper=1.0, ribs=3)
    # opening: a clean light rim ring, the inner far wall facing us, dark depth in front
    for y in range(int(top - ry) - 1, int(top + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if not in_ellipse(x, y, cx, top, rx, ry):
                continue
            if not in_ellipse(x, y, cx, top, rx - 1.4, ry - 1.3):
                c = "#8d95a8" if (x < cx + 2 and y < top + 2) else BINC[0]   # rim, brightest top-left
            elif not in_ellipse(x, y, cx, top + 3, rx - 1.4, ry - 1.3):
                c = BINC[2]                                           # inner far wall
            else:
                c = BINC[3]                                           # bottom of the bin, in shadow
            s.px(x, y, c)
    # a little rubbish lying at the bottom
    paper_ball(s, cx - 2.5, top + 2.5, 1.9)
    paper_ball(s, cx + 2.5, top + 3, 1.6)
    s.rect(int(cx), int(top + 1), int(cx + 3), int(top + 3), RED[1])  # red sticky note
    s.px(int(cx + 2), int(top + 2), RED[2])
    s.cast(int(cx - rx), int(top + h - ry + 2), int(cx + rx), int(top + h + ry), h + 2)
    return s.finish()


# ============================================================= pedal bin ===
def draw_pedal():
    s = Sprite(32, 36)
    cx, top, rx, ry, h = 15.5, 12, 10, 7.5, 12
    cylinder(s, cx, top, rx, ry, h, STEEL)
    for x in (int(cx - 6), int(cx - 5)):                              # vertical sheen on the steel
        s.vline(x, int(top + 2), int(top + h + 3), "#ffffff")
    # pedal at the front
    s.rrect(int(cx - 4), int(top + h + ry - 3), int(cx + 4), int(top + h + ry + 1), PLASTIC[1], 1)
    s.hline(int(cx - 3), int(cx + 3), int(top + h + ry - 3), PLASTIC[0])
    # lid: thick red rim band, then the dome seen from above (the biggest, brightest shape)
    cylinder(s, cx, top - 1, rx + 0.5, ry + 0.3, 2, [RED[1], RED[1], RED[2], RED[3]])
    s.disc(cx, top - 1, rx + 0.5, ry + 0.3, RED[2])
    s.disc(cx - 0.3, top - 1.4, rx - 0.5, ry - 0.7, RED[1])
    s.disc(cx - 1.5, top - 2.6, rx - 3.5, ry - 3, "#e8323f")         # dome catches the light
    s.disc(cx - 3.5, top - 4.2, 2.2, 1.4, RED[0])                     # specular hotspot
    s.rect(int(cx - 3), int(top - ry - 1), int(cx + 4), int(top - ry + 1), RED[3])   # hinge at the back
    s.hline(int(cx - 2), int(cx + 3), int(top - ry - 1), RED[2])
    s.cast(int(cx - rx), int(top + h - ry + 2), int(cx + rx), int(top + h + ry), h + 2)
    return s.finish()


if __name__ == "__main__":
    office, pedal = draw_office(), draw_pedal()
    office.image().save(OUT / "bin_office.png")
    pedal.image().save(OUT / "bin_pedal.png")
    root = Path(__file__).parent
    desk = Image.open(root / "desk" / "desk_front.png")
    chair = Image.open(root / "chair" / "chair_back.png")
    # scene for scale: desk + chair, office bin beside the desk, pedal bin on its own
    W, H = desk.width + 34 + pedal.image().width + 24, 112
    scene = floor_bg(W, H)
    scene.alpha_composite(desk, (8, 6))
    scene.alpha_composite(chair, (8 + 15, 6 + 44))
    scene.alpha_composite(office.image(), (8 + 60, 6 + 44))
    scene.alpha_composite(pedal.image(), (desk.width + 44, 40))
    big = scene.resize((W * 7, H * 7), Image.NEAREST)
    z = 10                                                             # close-ups on the right
    oz = Image.alpha_composite(floor_bg(office.w, 24), office.image()).resize((office.w * z, 24 * z), Image.NEAREST)
    pz = Image.alpha_composite(floor_bg(pedal.w, 36), pedal.image()).resize((pedal.w * 7, 36 * 7), Image.NEAREST)
    sheet = Image.new("RGB", (big.width + max(oz.width, pz.width) + 60, max(big.height, oz.height + pz.height + 60)), (38, 36, 48))
    sheet.paste(big.convert("RGB"), (0, 0))
    sheet.paste(oz.convert("RGB"), (big.width + 30, 20))
    sheet.paste(pz.convert("RGB"), (big.width + 30, oz.height + 40))
    sheet.save(OUT / "trash-preview.png")
    print("ok")
