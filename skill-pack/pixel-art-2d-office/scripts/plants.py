"""Sprite 06 — potted plants, 3 kinds. Same steep top-down camera (pots show an elliptical rim + soil).
Plants look the same from every side, so each kind is a single sprite (no 4-direction set).

  plant_big.png      32x48  floor plant: leafy canopy over a white ceramic pot with a Gastron-red band
  plant_snake.png    32x48  snake plant: upright striped blades in a terracotta pot
  plant_desk.png     16x20  small succulent rosette for desks / shelves / the meeting table
Anchor by the bottom-centre of the pot.
Outputs in ./plants/: the PNGs + plants-preview.png (with the desk for scale)
"""
import math
from pathlib import Path

from PIL import Image

from kit import KEY, RED, Sprite, preview

OUT = Path(__file__).parent / "plants"
OUT.mkdir(exist_ok=True)

LEAF = ["#a6dc72", "#78bf55", "#549f42", "#3a7f35", "#265c27"]
TERRA = ["#e09a6a", "#c97a4a", "#a65e38", "#7e4428"]
SOIL = ["#6a4a30", "#4a3220"]


def leaf(s, cx, cy, ang, length, width, light=0):
    """Pointed leaf from (cx, cy) along `ang` (radians, 0 = right, y squashed x0.8 for the camera).
    Upper/left half lit, lower/right half shaded, darker rim, pale midrib. light shifts the ramp."""
    dx, dy = math.cos(ang), math.sin(ang) * 0.8
    nx, ny = -dy, dx
    r = int(length + width) + 2
    for y in range(int(cy) - r, int(cy) + r + 1):
        for x in range(int(cx) - r, int(cx) + r + 1):
            px_, py_ = x - cx, y - cy
            u = (px_ * dx + py_ * dy) / (dx * dx + dy * dy)          # along the leaf, 0..length
            v = px_ * nx + py_ * ny                                   # across
            if u < 0 or u > length:
                continue
            half = width * math.sin(math.pi * min(1, u / length)) ** 0.8 / 2
            if abs(v) > half:
                continue
            edge = abs(v) > half - 1
            lit_side = (v * (nx + ny)) < 0                            # side facing the top-left light
            i = 1 if lit_side else 2
            if edge:
                i = 3
            i = max(0, min(4, i - light))
            c = LEAF[i]
            if abs(v) < 0.5 and 1 < u < length - 1:
                c = LEAF[max(0, i - 1)]                               # midrib
            s.px(x, y, c)


def pot(s, cx, top, rx, h, ramp, band=None):
    """Cylindrical pot seen from above: tapered body (lit left, dark right), rim ellipse, soil."""
    ry = rx * 0.45
    for y in range(int(top), int(top + h)):
        t = (y - top) / h
        w = rx - t * 1.5
        x0, x1 = int(round(cx - w)), int(round(cx + w))
        s.hline(x0, x1, y, ramp[1])
        s.hline(x0, x0 + 2, y, ramp[0])
        s.hline(x1 - 3, x1, y, ramp[2])
    s.hline(int(cx - rx + 2), int(cx + rx - 2), int(top + h) - 1, ramp[3])
    if band:
        for y in (int(top + 3), int(top + 4)):
            w = rx - (y - top) / h * 1.5
            s.hline(int(round(cx - w)), int(round(cx + w)), y, band[1] if y == int(top + 3) else band[2])
    s.disc(cx - 0.5, top, rx, ry, ramp[0])                           # rim
    s.disc(cx - 0.5, top + 0.3, rx - 1.5, ry - 1, SOIL[0])           # soil
    s.disc(cx + 0.5, top + 0.8, rx - 3, max(1, ry - 1.8), SOIL[1])


# ================================================================== big ===
def draw_big():
    s = Sprite(32, 48)
    pot(s, 16, 34, 8, 12, KEY, RED)
    cx, cy = 16, 25
    # back leaves first (pointing up / away), then sides, then the ones leaning toward us
    for ang, ln, wd, lt in ((-1.57, 15, 8, -1), (-2.3, 14, 7, -1), (-0.85, 14, 7, -1),
                            (-2.9, 13, 7, 0), (-0.25, 13, 7, 0), (3.0, 12, 6, 0), (0.15, 12, 6, 0),
                            (-1.9, 11, 7, 1), (-1.2, 11, 7, 1)):
        leaf(s, cx, cy, ang, ln, wd, lt)
    for ang, ln, wd in ((2.4, 10, 6), (0.75, 10, 6), (1.57, 9, 6)):  # front leaves drape over the pot rim
        leaf(s, cx, cy + 2, ang, ln, wd, 1)
    s.disc(cx, cy, 2.5, 2, LEAF[3])                                  # crown
    s.cast(8, 38, 24, 46, 18)
    return s.finish()


# ================================================================ snake ===
def blade(s, x, base, h, w, lean):
    """Upright sword leaf with lighter cross-bands and a yellow margin."""
    for k in range(h):
        y = base - k
        t = k / h
        hw = w * (1 - t ** 1.6) / 2
        xc = x + lean * t * t * 3
        x0, x1 = int(round(xc - hw)), int(round(xc + hw))
        if x1 <= x0:
            x1 = x0 + 1
        s.hline(x0, x1, y, LEAF[3] if (k // 3) % 2 else LEAF[2])
        if x1 - x0 >= 3:
            s.px(x0, y, "#d8c84a")                                   # yellow margins
            s.px(x1 - 1, y, "#b8a63a")
        if k % 6 == 1 and x1 - x0 >= 3:
            s.hline(x0 + 1, x1 - 1, y, LEAF[1])                      # pale banding


def draw_snake():
    s = Sprite(32, 48)
    pot(s, 16, 34, 8, 12, TERRA)
    for x, h, w, lean in ((11, 22, 4, -1), (20, 24, 4, 1), (14, 30, 5, -0.3), (18, 27, 5, 0.4),
                          (16, 33, 5, 0), (12, 18, 4, -1.4), (21, 19, 4, 1.4)):
        blade(s, x, 35, h, w, lean)
    s.cast(8, 38, 24, 46, 22)
    return s.finish()


# ================================================================= desk ===
def draw_desk_plant():
    s = Sprite(16, 20)
    pot(s, 8, 13, 4.5, 6, TERRA)
    cx, cy = 8, 9
    for i in range(8):                                               # outer ring of fat leaves
        leaf(s, cx, cy, i * math.pi / 4 + 0.2, 5, 4, 0 if i < 4 else 1)
    for i in range(5):                                               # inner ring, lighter
        leaf(s, cx, cy, i * 2 * math.pi / 5, 3, 3, 1)
    s.px(cx, cy, LEAF[0])
    s.cast(4, 15, 12, 19, 6)
    return s.finish()


if __name__ == "__main__":
    big, snake, small = draw_big(), draw_snake(), draw_desk_plant()
    big.image().save(OUT / "plant_big.png")
    snake.image().save(OUT / "plant_snake.png")
    small.image().save(OUT / "plant_desk.png")
    desk = Image.open(Path(__file__).parent / "desk" / "desk_front.png").copy()
    desk.alpha_composite(small.image(), (3, 18))                     # succulent on the desk corner
    items = [big.image(), snake.image(), small.image(), desk]
    gap = 8
    h = max(i.height for i in items)
    sheet = Image.new("RGBA", (sum(i.width for i in items) + gap * 3, h), (0, 0, 0, 0))
    x = 0
    for im in items:
        sheet.alpha_composite(im, (x, h - im.height))
        x += im.width + gap
    preview(sheet, OUT / "plants-preview.png", 8, grid=False)
    print("ok")
