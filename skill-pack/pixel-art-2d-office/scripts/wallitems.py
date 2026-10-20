"""Sprite 13 — wall clock + wall calendar (front view only, they hang on the wall face).

Drawn in the user's target style (Ref/style-target-vending.jpg): chunky, bold readable shapes,
few colours, a full 1px dark outline around the silhouette, a lit 'top' band showing the
object's thickness, and only a short drop shadow on the wall.

  clock.png        18x19  wall-scale clock (use this one in the room)
  clock_large.png  28x30  big version: Gastron-red rim, cream face, bold 12/3/6/9 marks, hands at 10:10
  calendar.png  28x36  nail + dark binding with spiral rings, red month header, day grid,
                       today circled in red, bottom corner curling up
Outputs in ./wall/ + wall-preview.png (on a wall strip, next to the wall whiteboard for scale)
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image

from kit import GREEN, RED, Sprite

OUT = Path(__file__).parent / "wall"
OUT.mkdir(exist_ok=True)
NAVY = ["#3a4256", "#2a3142", "#1f2433"]
CREAM = ["#fffaf0", "#f6eedb", "#e2d6bb", "#c4b593"]
INK = "#262a35"

FONT = {
    "O": [".#.", "#.#", "#.#", "#.#", ".#."],
    "C": [".##", "#..", "#..", "#..", ".##"],
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
}


def text(s, x, y, word, c):
    for ch in word:
        for r, row in enumerate(FONT[ch]):
            for k, v in enumerate(row):
                if v == "#":
                    s.px(x + k, y + r, c)
        x += 4


def thick_line(s, x0, y0, x1, y1, c, w=2):
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for t in range(n + 1):
        x = x0 + (x1 - x0) * t / n
        y = y0 + (y1 - y0) * t / n
        for dx in range(w):
            for dy in range(w):
                s.px(int(round(x - (w - 1) / 2)) + dx, int(round(y - (w - 1) / 2)) + dy, c)


# ================================================================ clock ===
def draw_clock():
    s = Sprite(28, 30)
    cx, cy, r = 13.5, 14.5, 12
    s.disc(cx, cy + 1, r, r, RED[3])                         # rim's side (thickness), in shade
    s.disc(cx, cy, r, r, RED[1])                             # rim face
    for a in range(200, 341, 4):                             # lit top band = the rim seen from above
        x = cx + math.cos(math.radians(a)) * (r - 0.6)
        y = cy + math.sin(math.radians(a)) * (r - 0.6)
        s.px(round(x), round(y), RED[0])
    s.disc(cx, cy, r - 2.5, r - 2.5, CREAM[1])               # dial
    for a in range(200, 341, 5):                             # the rim's shadow inside the dial top
        x = cx + math.cos(math.radians(a)) * (r - 3)
        y = cy + math.sin(math.radians(a)) * (r - 3)
        s.px(round(x), round(y), CREAM[3])
    s.disc(cx - 3, cy - 3, 3, 2, CREAM[0])                   # glass glint
    for h in range(12):                                      # bold quarter marks, dots between
        a = math.radians(h * 30 - 90)
        x, y = cx + math.cos(a) * (r - 4.5), cy + math.sin(a) * (r - 4.5)
        if h % 3 == 0:
            s.rect(int(round(x - 1)), int(round(y - 1)), int(round(x + 1)), int(round(y + 1)), INK)
        else:
            s.px(round(x), round(y), CREAM[3])
    thick_line(s, cx, cy, cx - 4.2, cy - 2.4, INK)           # hour hand (10)
    thick_line(s, cx, cy, cx + 5.6, cy - 3.6, INK)           # minute hand (2)
    thick_line(s, cx, cy, cx - 1.5, cy + 6.5, RED[1], 1)     # second hand
    s.rect(int(cx), int(cy), int(cx) + 2, int(cy) + 2, INK)      # small centre cap
    s.px(int(cx), int(cy), RED[0])
    s.px(int(cx) + 1, int(cy) + 5, GREEN[1])                 # tiny Gastron-green brand dot
    s.finish(shadow=False, full_outline=True, rim=0)
    return s.wall_shadow()


def draw_clock_small():
    """Wall-scale clock (16 px dial) — redrawn, not shrunk, so it stays crisp."""
    s = Sprite(18, 19)
    cx, cy, r = 8.5, 8.5, 7
    s.disc(cx, cy + 1, r, r, RED[3])                         # rim side
    s.disc(cx, cy, r, r, RED[1])                             # rim
    for a in range(205, 336, 8):                             # lit top of the rim
        s.px(round(cx + math.cos(math.radians(a)) * (r - 0.5)), round(cy + math.sin(math.radians(a)) * (r - 0.5)), RED[0])
    s.disc(cx, cy, r - 1.6, r - 1.6, CREAM[1])               # dial
    s.hline(int(cx - 3), int(cx + 3), int(cy - 5), CREAM[3])  # rim's shadow on the dial top
    s.px(int(cx - 3), int(cy - 3), CREAM[0])                 # glint
    for dx, dy in ((0, -4), (4, 0), (0, 4), (-4, 0)):        # 12 / 3 / 6 / 9
        s.px(int(cx + dx), int(cy + dy), INK)
    thick_line(s, cx, cy, cx - 2.6, cy - 1.4, INK, 1)        # hour hand (10)
    thick_line(s, cx, cy, cx + 3.2, cy - 2.2, INK, 1)        # minute hand (2)
    s.px(int(cx), int(cy) + 2, RED[1])                       # second hand stub
    s.px(int(cx), int(cy), RED[2])
    s.finish(shadow=False, full_outline=True, rim=0)
    return s.wall_shadow(1, 1)


# ============================================================= calendar ===
def draw_calendar():
    s = Sprite(28, 36)
    x0, x1 = 2, 25
    s.rect(x0, 9, x1, 33, CREAM[2])                          # page stack edge under the sheet
    s.rect(x0, 9, x1, 32, CREAM[1])                          # the sheet
    s.hline(x0, x1, 32, CREAM[3])
    # red month header with OCT
    s.rect(x0, 7, x1, 14, RED[1])
    s.hline(x0, x1, 7, RED[0])
    s.hline(x0, x1, 13, RED[2])
    text(s, x0 + 6, 8, "OCT", CREAM[0])
    # day grid: 7 columns x 4 rows, Sunday column in red, today circled
    for row in range(4):
        for col in range(7):
            gx, gy = x0 + 2 + col * 3, 16 + row * 4
            c = RED[1] if col == 0 else "#7d8590"
            s.hline(gx, gx + 2, gy, c)
    tx, ty = x0 + 2 + 4 * 3, 16 + 2 * 4                      # today
    s.rect(tx - 1, ty - 2, tx + 3, ty - 1, RED[1])
    s.rect(tx - 1, ty + 1, tx + 3, ty + 2, RED[1])
    s.px(tx - 2, ty, RED[1])
    s.px(tx + 3, ty, RED[1])
    s.rect(x0 + 2, 29, x0 + 9, 31, "#f6d04d")                # little sticky reminder
    # bottom-right corner curling up (lighter underside)
    for k in range(4):
        for j in range(k + 1):
            s.px(x1 - 1 - j, 29 + k, CREAM[0] if j < k else CREAM[3])
    # dark binding band with spiral rings (the calendar's 'top' band) + nail
    s.rect(x0, 3, x1, 8, NAVY[1])
    s.hline(x0, x1, 3, NAVY[0])
    for rx in range(x0 + 2, x1 - 1, 4):
        s.rect(rx, 2, rx + 2, 5, "#c9ced6")                  # rings
        s.px(rx, 2, "#ffffff")
        s.px(rx + 1, 6, NAVY[2])                             # punched holes
    s.rect(13, 0, 15, 2, "#7d8590")                          # nail
    s.finish(shadow=False, full_outline=True, rim=0)
    return s.wall_shadow()


def wall_bg(w, h):
    """Wall strip for the preview: plaster, subtle texture, wood wainscot at the bottom."""
    a = np.zeros((h, w, 4), np.uint8)
    a[...] = (227, 216, 189, 255)
    for x in range(0, w, 3):
        a[:h - 10, x] = (222, 210, 182, 255)
    a[h - 10:h - 2] = (107, 66, 48, 255)
    a[h - 10] = (125, 79, 54, 255)
    a[h - 2:] = (54, 31, 20, 255)
    return Image.fromarray(a)


if __name__ == "__main__":
    clock, cal = draw_clock(), draw_calendar()
    clock.image().save(OUT / "clock_large.png")
    small = draw_clock_small()
    small.image().save(OUT / "clock.png")                     # wall-scale version used in the room
    cal.image().save(OUT / "calendar.png")
    wb = Image.open(Path(__file__).parent / "whiteboard" / "wb_wall.png")
    W, H = 150, 56
    bg = wall_bg(W, H)
    bg.alpha_composite(wb, (6, 10))
    bg.alpha_composite(clock.image(), (80, 6))
    bg.alpha_composite(cal.image(), (116, 6))
    big = bg.convert("RGB").resize((W * 6, H * 6), Image.NEAREST)
    z = 10
    zc = Image.alpha_composite(wall_bg(clock.w, 36).crop((0, 0, clock.w, 30)), clock.image()).resize((clock.w * z, 30 * z), Image.NEAREST)
    zk = Image.alpha_composite(wall_bg(cal.w, 36), cal.image()).resize((cal.w * z, 36 * z), Image.NEAREST)
    sheet = Image.new("RGB", (max(big.width, zc.width + zk.width + 40), big.height + 30 + zk.height), (38, 36, 48))
    sheet.paste(big, (0, 0))
    sheet.paste(zc.convert("RGB"), (0, big.height + 30))
    sheet.paste(zk.convert("RGB"), (zc.width + 40, big.height + 30))
    sheet.save(OUT / "wall-preview.png")
    print("ok")
