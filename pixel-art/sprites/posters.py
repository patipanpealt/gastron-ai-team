"""Sprite 14 — cartoon wall posters (front view only), original characters, target style:
bold readable shapes, few colours, full dark outline, washi tape on the top corners,
a slightly lifted bottom corner, short drop shadow on the wall.

  poster_flame.png / poster_pig.png              22x28  wall-scale versions (use these in the room)
  poster_flame_large.png  34x44  'Flamey' — a happy Gastron flame mascot giving a thumbs-up, sunburst, SAFE banner
  poster_pig_large.png    34x44  the office's pink piglet plush waving, hearts, HI! banner
Outputs in ./posters/ + posters-preview.png (on the wall with the clock + calendar)
"""
import math
from pathlib import Path

from PIL import Image

from kit import GREEN, RED, Sprite
from wallitems import wall_bg

OUT = Path(__file__).parent / "posters"
OUT.mkdir(exist_ok=True)
INK = "#262a35"
CREAM = ["#fffaf0", "#f6eedb", "#e2d6bb", "#c4b593"]
TAPE = ["#cfe8ee", "#a9d2dc"]
PINK = ["#ffe1ea", "#f9bfd0", "#ee9db7", "#d27a98", "#a85776"]
FLAME = ["#fff3a0", "#ffd23f", "#ff9a2e", "#f0561f", RED[1], RED[3]]

FONT = {
    "S": [".##", "#..", ".#.", "..#", "##."],
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "F": ["###", "#..", "##.", "#..", "#.."],
    "E": ["###", "#..", "##.", "#..", "###"],
    "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "!": ["#", "#", "#", ".", "#"],
}


def text(s, x, y, word, c):
    for ch in word:
        g = FONT[ch]
        for r, row in enumerate(g):
            for k, v in enumerate(row):
                if v == "#":
                    s.px(x + k, y + r, c)
        x += len(g[0]) + 1


def text_w(word):
    return sum(len(FONT[c][0]) + 1 for c in word) - 1


def paper(s, x0, y0, x1, y1, bg):
    s.rect(x0, y0, x1, y1, bg)
    s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, bg)


def tape(s, x, y, flip=1):
    """A short strip of washi tape stuck diagonally over a corner."""
    for k in range(6):
        for w in range(3):
            s.px(x + k * flip, y + k // 2 + w - 1, TAPE[0] if w else TAPE[1])


def lifted_corner(s, x1, y1, bg_dark):
    """Bottom-right corner peeling off the wall: a lighter fold + a gap."""
    for k in range(4):
        for j in range(k + 1):
            s.px(x1 - 1 - j, y1 - 4 + k, CREAM[0] if j < k else bg_dark)


def banner(s, x0, x1, y, word, c, ink):
    s.rect(x0, y, x1, y + 7, c[0])
    s.hline(x0, x1, y, c[1])
    s.hline(x0, x1, y + 6, c[2])
    for dx in (0, 1):                                         # ribbon notches
        s.px(x0 + dx, y + 3, CREAM[1])
        s.px(x1 - 1 - dx, y + 3, CREAM[1])
    text(s, (x0 + x1 - text_w(word)) // 2, y + 1, word, ink)


# ================================================================ flame ===
def flame_shape(s, cx, tip, cy, r, color, sway=1.5):
    for y in range(int(tip), int(cy + r) + 1):
        if y >= cy:
            half = r * max(0, 1 - ((y - cy) / r) ** 2) ** 0.5
        else:
            t = (y - tip) / (cy - tip)
            half = r * t ** 1.25
        off = math.sin((y - tip) / 4.0) * sway * (1 - max(0, (y - tip) / (cy + r - tip)))
        x0, x1 = int(round(cx - half + off)), int(round(cx + half + off))
        if x1 > x0:
            s.hline(x0, x1, y, color)


def draw_flame():
    s = Sprite(34, 44)
    x0, y0, x1, y1 = 2, 2, 31, 41
    paper(s, x0, y0, x1, y1, CREAM[1])
    cx, cy = 16.5, 21
    for a in range(0, 360, 30):                               # sunburst rays
        for k in range(6, 15):
            px_ = cx + math.cos(math.radians(a)) * k
            py_ = cy + math.sin(math.radians(a)) * k * 0.95
            if x0 + 1 <= px_ < x1 - 1 and y0 + 1 <= py_ < y1 - 9:
                s.px(round(px_), round(py_), "#ffe7a8")
    s.disc(cx, cy + 6, 9, 2.5, CREAM[2])                      # little ground shadow under Flamey
    flame_shape(s, cx, 5, 21, 9, FLAME[4])                    # outer red
    flame_shape(s, cx, 8, 22, 7, FLAME[3], 1.2)
    flame_shape(s, cx, 11, 23, 5.2, FLAME[2], 1.0)
    flame_shape(s, cx, 15, 24, 3.4, FLAME[1], 0.6)            # bright core
    s.disc(cx - 4, 15, 1.4, 2, FLAME[0])                      # shine
    # face
    for ex in (cx - 4, cx + 2):
        s.rect(int(ex), 20, int(ex) + 2, 23, INK)
        s.px(int(ex), 20, "#ffffff")
    s.hline(int(cx - 2), int(cx + 2), 25, INK)                # big smile
    s.px(int(cx - 3), 24, INK)
    s.px(int(cx + 2), 24, INK)
    s.disc(cx - 6, 24, 1.3, 0.9, "#ff7ab0")                   # blush
    s.disc(cx + 5, 24, 1.3, 0.9, "#ff7ab0")
    # arms: thumbs-up on the right, wave on the left
    s.rect(int(cx + 8), 21, int(cx + 11), 23, FLAME[3])
    s.rect(int(cx + 10), 17, int(cx + 12), 21, FLAME[2])      # thumb
    s.rect(int(cx - 11), 22, int(cx - 8), 24, FLAME[3])
    s.px(int(cx - 12), 21, FLAME[2])
    # green check badge = 'gas detected safely'
    s.disc(26, 9, 3.2, 3.2, GREEN[1])
    s.px(25, 9, "#ffffff")
    s.px(26, 10, "#ffffff")
    s.px(27, 9, "#ffffff")
    s.px(28, 8, "#ffffff")
    banner(s, x0 + 3, x1 - 3, y1 - 9, "SAFE", [RED[1], RED[0], RED[2]], CREAM[0])
    tape(s, x0 - 1, y0, 1)
    tape(s, x1 - 1, y0, -1)
    lifted_corner(s, x1, y1, CREAM[3])
    s.finish(shadow=False, full_outline=True, rim=0)
    return s.wall_shadow()


# ================================================================== pig ===
def heart(s, x, y, c):
    for dx, dy in ((0, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (1, 3)):
        s.px(x + dx, y + dy, c)


def draw_pig():
    s = Sprite(34, 44)
    x0, y0, x1, y1 = 2, 2, 31, 41
    paper(s, x0, y0, x1, y1, "#fff3f7")
    for hx_, hy in ((5, 6), (25, 5), (7, 26), (26, 25), (15, 4)):
        heart(s, hx_, hy, "#ff9fbf")
    cx = 16.5
    ln = PINK[4]                                              # dark line round the character so it pops off the pink paper
    s.disc(cx, 30, 9, 6, ln)
    s.disc(cx + 9, 23, 3, 3.6, ln)
    s.disc(cx + 10, 20.5, 2.6, 2.6, ln)
    for side in (-1, 1):
        s.disc(cx + side * 7, 9, 4, 4.4, ln)
    s.disc(cx, 17, 10, 8.5, ln)
    s.disc(cx, 30, 8, 5, PINK[2])                             # body
    s.disc(cx - 1, 29, 6, 3.5, PINK[1])
    s.disc(cx + 9, 23, 2, 2.6, PINK[2])                       # waving arm up
    s.disc(cx + 10, 20.5, 1.6, 1.6, PINK[1])
    for side in (-1, 1):                                      # ears
        s.disc(cx + side * 7, 9, 3, 3.4, PINK[2])
        s.disc(cx + side * 7.3, 9.6, 1.6, 2, PINK[3])
    s.disc(cx, 17, 9, 7.5, PINK[2])                           # head
    s.disc(cx - 1, 15.5, 7.5, 5.8, PINK[1])
    s.disc(cx - 4, 12, 2.2, 1.2, "#ffffff")                   # shine
    for ex in (cx - 4, cx + 3):
        s.rect(int(ex), 16, int(ex) + 2, 19, INK)
        s.px(int(ex), 16, "#ffffff")
    s.disc(cx - 0.5, 21, 3, 2, PINK[0])                       # snout
    s.px(int(cx - 2), 21, PINK[4])
    s.px(int(cx + 1), 21, PINK[4])
    s.disc(cx - 7, 20, 1.5, 1, "#ff7ab0")
    s.disc(cx + 6, 20, 1.5, 1, "#ff7ab0")
    s.disc(cx - 3, 24.5, 2.6, 1.5, RED[1])                    # red bow
    s.disc(cx + 3, 24.5, 2.6, 1.5, RED[1])
    s.rect(int(cx - 1), 24, int(cx + 1), 26, RED[2])
    banner(s, x0 + 5, x1 - 5, y1 - 9, "HI!", [PINK[3], PINK[2], PINK[4]], CREAM[0])
    tape(s, x0 - 1, y0, 1)
    tape(s, x1 - 1, y0, -1)
    lifted_corner(s, x1, y1, PINK[3])
    s.finish(shadow=False, full_outline=True, rim=0)
    return s.wall_shadow()


# ============================================== wall-scale (small) posters ===
SW, SH = 22, 28                                               # fits the plaster band of the wall tile


def small_frame(s, bg):
    x0, y0, x1, y1 = 2, 2, SW - 3, SH - 3
    paper(s, x0, y0, x1, y1, bg)
    return x0, y0, x1, y1


def small_banner(s, x0, x1, y, word, c, ink):
    s.rect(x0, y, x1, y + 7, c[0])
    s.hline(x0, x1, y, c[1])
    s.hline(x0, x1, y + 6, c[2])
    text(s, (x0 + x1 - text_w(word) + 1) // 2, y + 1, word, ink)


def draw_flame_small():
    s = Sprite(SW, SH)
    x0, y0, x1, y1 = small_frame(s, CREAM[1])
    cx = (x0 + x1) / 2
    for a in range(0, 360, 45):                               # a few sunburst rays
        for k in (5, 6, 7):
            s.px(round(cx + math.cos(math.radians(a)) * k), round(11 + math.sin(math.radians(a)) * k), "#ffe7a8")
    flame_shape(s, cx, 4, 12, 5.5, FLAME[4], 0.8)
    flame_shape(s, cx, 6, 13, 4.2, FLAME[3], 0.6)
    flame_shape(s, cx, 9, 14, 2.6, FLAME[1], 0.3)
    s.px(int(cx - 2), 11, INK)                                # eyes
    s.px(int(cx + 1), 11, INK)
    s.hline(int(cx - 1), int(cx + 1), 14, INK)                # smile
    s.px(int(cx - 3), 13, "#ff7ab0")
    s.px(int(cx + 2), 13, "#ff7ab0")
    s.px(x1 - 3, y0 + 2, GREEN[1])                            # green check dot
    s.px(x1 - 4, y0 + 2, GREEN[1])
    small_banner(s, x0 + 1, x1 - 1, y1 - 8, "SAFE", [RED[1], RED[0], RED[2]], CREAM[0])
    tape(s, x0 - 1, y0, 1)
    tape(s, x1 - 1, y0, -1)
    s.finish(shadow=False, full_outline=True, rim=0)
    return s.wall_shadow(1, 1)


def draw_pig_small():
    s = Sprite(SW, SH)
    x0, y0, x1, y1 = small_frame(s, "#fff3f7")
    cx = (x0 + x1) / 2
    heart(s, x0 + 1, y0 + 1, "#ff9fbf")
    ln = PINK[4]
    for side in (-1, 1):
        s.disc(cx + side * 4.5, 6, 2.4, 2.4, ln)
    s.disc(cx, 10, 6, 5, ln)
    for side in (-1, 1):                                      # ears
        s.disc(cx + side * 4.5, 6, 1.6, 1.6, PINK[2])
    s.disc(cx, 10, 5, 4, PINK[2])                             # head
    s.disc(cx - 1, 9, 3.6, 2.6, PINK[1])
    s.px(int(cx - 3), 7, "#ffffff")
    s.px(int(cx - 2), 10, INK)                                # eyes
    s.px(int(cx + 2), 10, INK)
    s.rect(int(cx - 1), 12, int(cx + 2), 14, PINK[0])         # snout
    s.px(int(cx - 1), 13, PINK[4])
    s.px(int(cx + 1), 13, PINK[4])
    s.hline(int(cx - 2), int(cx + 3), 15, RED[1])             # bow
    small_banner(s, x0 + 2, x1 - 2, y1 - 8, "HI!", [PINK[3], PINK[2], PINK[4]], CREAM[0])
    tape(s, x0 - 1, y0, 1)
    tape(s, x1 - 1, y0, -1)
    s.finish(shadow=False, full_outline=True, rim=0)
    return s.wall_shadow(1, 1)


if __name__ == "__main__":
    flame, pig = draw_flame(), draw_pig()
    flame.image().save(OUT / "poster_flame_large.png")
    pig.image().save(OUT / "poster_pig_large.png")
    draw_flame_small().image().save(OUT / "poster_flame.png")    # wall-scale, used in the room
    draw_pig_small().image().save(OUT / "poster_pig.png")
    wall = Path(__file__).parent / "wall"
    W, H = 160, 60
    bg = wall_bg(W, H)
    bg.alpha_composite(flame.image(), (6, 4))
    bg.alpha_composite(pig.image(), (46, 4))
    bg.alpha_composite(Image.open(wall / "clock.png"), (90, 8))
    bg.alpha_composite(Image.open(wall / "calendar.png"), (124, 8))
    big = bg.convert("RGB").resize((W * 6, H * 6), Image.NEAREST)
    z = 9
    zf = Image.alpha_composite(wall_bg(flame.w, 46).crop((0, 0, flame.w, 44)), flame.image()).resize((flame.w * z, 44 * z), Image.NEAREST)
    zp = Image.alpha_composite(wall_bg(pig.w, 46).crop((0, 0, pig.w, 44)), pig.image()).resize((pig.w * z, 44 * z), Image.NEAREST)
    sheet = Image.new("RGB", (max(big.width, zf.width + zp.width + 40), big.height + 30 + zf.height), (38, 36, 48))
    sheet.paste(big, (0, 0))
    sheet.paste(zf.convert("RGB"), (0, big.height + 30))
    sheet.paste(zp.convert("RGB"), (zf.width + 40, big.height + 30))
    sheet.save(OUT / "posters-preview.png")
    print("ok")
