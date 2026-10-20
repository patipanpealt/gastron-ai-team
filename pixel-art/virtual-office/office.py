"""Gastron Virtual Office — top-down (3/4 RPG view, NOT isometric) pixel office for the 11 AI agents.

Style rules distilled from the Pinterest "2D pixel art office" board:
  * camera looks straight down at the floor; walls on the top edge show their front face,
    side/bottom walls show only a thin dark cap (RPG-Maker / Stardew convention)
  * every object = lit top face + darker front face, 1px dark outline, soft shadow down-right
  * 16px grid, limited warm palette, small clutter (mugs, papers, plants) for life
  * characters are 12x13 chibi sprites: front view above a desk, back view below a desk

Drawn procedurally with PIL. Run:  python3 office.py
  -> office.png / office-x3.png       (with the team seated)
  -> office-bg.png / office-bg-x3.png (empty room, for the app to layer sprites on)
  -> seats.json                       (seat position + facing per agent id)
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

W, H = 384, 272
OUT = Path(__file__).parent
BG = (38, 36, 48, 255)
im = Image.new("RGBA", (W, H), BG)
d = ImageDraw.Draw(im)


# ------------------------------------------------------------- helpers ----
def hx(c):
    return c if isinstance(c, tuple) else tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def Hh(x, y, s=0):
    n = ((int(x) * 374761393) + (int(y) * 668265263) + (s * 2246822519) + 1013904223) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFFFFFF) / 4294967296


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        im.putpixel((int(x), int(y)), hx(c)[:3] + (255,))


def rect(x0, y0, x1, y1, c):
    if x1 > x0 and y1 > y0:
        d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=hx(c)[:3] + (255,))


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def lighten(c, t):
    return mix(c, "#ffffff", t)


def darken(c, t):
    return mix(c, "#000000", t)


def shade(x0, y0, x1, y1, c, a):
    arr = np.array(im).astype(float)
    y0, y1, x0, x1 = max(0, y0), min(H, y1), max(0, x0), min(W, x1)
    arr[y0:y1, x0:x1, :3] = arr[y0:y1, x0:x1, :3] * (1 - a) + np.array(hx(c)) * a
    im.paste(Image.fromarray(arr.astype(np.uint8)), (0, 0))


def disc(cx, cy, rx, ry, c):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                px(x, y, c)


# ------------------------------------------------------------- palette ----
OL = "#2b2230"
WOOD_T = ["#c48446", "#a96a34", "#8e572a"]
WOOD_F = ["#74442a", "#61381f", "#432414"]
DARK_T = ["#7d4f36", "#6b4230", "#583426"]
DARK_F = ["#55331f", "#472a1a", "#361f14"]
TEAL_T = ["#5ea79c", "#4c8f85", "#3c776f"]
TEAL_F = ["#3b6f68", "#2f5c56", "#234642"]
WHITE_T = ["#f2efe8", "#e2ddd2", "#c9c3b6"]
WHITE_F = ["#bdb6a8", "#a8a193", "#8d8678"]
METAL = ["#6b7280", "#4f5562", "#363a44"]
CHAIR = ["#4a4f5e", "#3a3e4b", "#2a2d37"]
FLOOR = ["#d6bb90", "#ccb087", "#c3a67c", "#b89a70"]
FLOOR_GAP = "#a98c64"
CARPET = ["#6f8296", "#667a8e", "#5e7186"]
WALL = ["#ece3cb", "#e3d8bd", "#d6c9ab"]
CAP = ["#4a3c44", "#3a2f37"]
LEAF = ["#2f6b34", "#3f8a3c", "#58a64a", "#7cc35c"]
POT = ["#e8e2d4", "#c9c0ad"]
TERRA = ["#c4673e", "#9c4c2c"]
SKY = ["#bfe6f2", "#8fcde4", "#6ab4d6"]
SCREEN = ["#9fd6e0", "#6ab4c8", "#3d7f98"]
RED = "#D70010"     # Gastron CI
GREEN = "#009143"


# ============================================== layered objects + depth ===
def obj(fn, *a, L=3, outline=True, **k):
    """Draw fn on its own layer -> 1px dark outline -> soft cast shadow (down-right) -> composite."""
    global im, d
    base, bd = im, d
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im, d = layer, ImageDraw.Draw(layer)
    fn(*a, **k)
    im, d = base, bd
    arr = np.array(layer)
    m = arr[..., 3] > 0
    if outline:
        nb = np.zeros_like(m)
        nb[1:, :] |= m[:-1, :]
        nb[:-1, :] |= m[1:, :]
        nb[:, 1:] |= m[:, :-1]
        nb[:, :-1] |= m[:, 1:]
        ring = nb & ~m
        arr[ring] = list(hx(OL)) + [255]
        m = arr[..., 3] > 0
    out = np.array(base).astype(float)
    alpha = np.zeros((H, W))
    for kk in range(1, L + 1):
        sh = np.zeros_like(m)
        sh[kk:, kk:] = m[: H - kk, : W - kk]
        alpha[sh & (alpha == 0)] = 0.34 if kk <= 2 else 0.2
    alpha[m] = 0
    out[..., :3] = out[..., :3] * (1 - alpha[..., None]) + np.array([40, 24, 30]) * alpha[..., None]
    out[m, :3] = arr[m, :3]
    out[..., 3] = 255
    base.paste(Image.fromarray(out.astype(np.uint8)), (0, 0))


def box(x, y, w, dp, h, top=WOOD_T, front=WOOD_F, panels=0, handles=True):
    """Top-down block: top face (w x dp) above a front face (w x h)."""
    rect(x, y, x + w, y + dp, top[1])
    rect(x, y, x + w, y + 1, top[0])
    rect(x, y, x + 1, y + dp, top[0])
    rect(x, y + dp - 1, x + w, y + dp, top[2])
    for i in range(x + 3, x + w - 2, 7):
        if Hh(i, y, 5) < 0.55:
            rect(i, y + 2 + int(Hh(i, y, 7) * max(1, dp - 4)), i + 2 + int(Hh(i, y, 6) * 3), y + 3 + int(Hh(i, y, 7) * max(1, dp - 4)), top[2])
    rect(x, y + dp, x + w, y + dp + h, front[0])
    rect(x, y + dp + h - 1, x + w, y + dp + h, front[2])
    if panels:
        pw = w / panels
        for i in range(panels):
            a, b = int(x + i * pw), int(x + (i + 1) * pw)
            rect(a + 1, y + dp + 1, b - 1, y + dp + h - 2, front[1])
            rect(a + 1, y + dp + 1, b - 1, y + dp + 2, front[0])
            if handles:
                rect((a + b) // 2 - 1, y + dp + 3, (a + b) // 2 + 2, y + dp + 4, "#e0b070")


# ================================================================ props ===
def monitor(x, y, kind=0, w=14, h=9):
    """Front-facing monitor standing on a desk (screen visible)."""
    rect(x, y, x + w, y + h, METAL[2])
    for yy in range(y + 1, y + h - 1):
        rect(x + 1, yy, x + w - 1, yy + 1, mix(SCREEN[0], SCREEN[2], (yy - y) / h))
    if kind == 0:      # code / doc
        for i, yy in enumerate(range(y + 2, y + h - 2, 2)):
            ln = 3 + int(Hh(x, yy, 3) * (w - 6))
            rect(x + 2 + (i % 2), yy, x + 2 + ln, yy + 1, ["#2f5c78", "#e8f6f8", "#f6b066"][i % 3])
    elif kind == 1:    # bar chart
        for i in range(4):
            bh = 2 + int(Hh(x, i, 4) * (h - 5))
            rect(x + 2 + i * 3, y + h - 2 - bh, x + 4 + i * 3, y + h - 2, [GREEN, "#f6b066", RED, "#2f5c78"][i])
    elif kind == 2:    # design palette / image
        rect(x + 2, y + 2, x + 8, y + h - 2, "#f6b066")
        disc(x + 5, y + 4, 1.5, 1.5, "#fff3c4")
        rect(x + 2, y + h - 4, x + 8, y + h - 2, GREEN)
        for i, c in enumerate([RED, "#2f5c78", "#f4f1ea"]):
            rect(x + 10, y + 2 + i * 2, x + 12, y + 3 + i * 2, c)
    elif kind == 3:    # social feed
        for i in range(3):
            rect(x + 2, y + 2 + i * 2, x + 4, y + 3 + i * 2, [RED, "#8e44ad", GREEN][i])
            rect(x + 5, y + 2 + i * 2, x + w - 3, y + 3 + i * 2, "#e8f6f8")
    rect(x + 1, y + 1, x + 4, y + 2, "#e8f6f8")
    rect(x + w // 2 - 1, y + h, x + w // 2 + 1, y + h + 2, METAL[1])
    rect(x + w // 2 - 3, y + h + 2, x + w // 2 + 3, y + h + 3, METAL[0])


def laptop_back(x, y):
    """Open laptop seen from behind (the person faces us)."""
    rect(x, y, x + 12, y + 6, METAL[0])
    rect(x, y, x + 12, y + 1, lighten(METAL[0], 0.3))
    px(x + 6, y + 3, "#d6dae2")
    rect(x - 1, y + 6, x + 13, y + 7, METAL[2])


def keyboard(x, y, w=10):
    rect(x, y, x + w, y + 3, "#e6e2da")
    for k in range(x + 1, x + w - 1, 2):
        px(k, y + 1, "#b8b2a6")
    rect(x, y + 2, x + w, y + 3, "#b8b2a6")


def paper(x, y, w=5, h=4):
    rect(x, y, x + w, y + h, "#f4f1ea")
    rect(x + 1, y + 1, x + w - 1, y + 2, "#c9c4b8")


def mug(x, y, c="#e8e2d4"):
    rect(x, y, x + 3, y + 3, c)
    px(x + 3, y + 1, c)
    px(x + 1, y, "#6a4a30")


def sticky(x, y, c):
    rect(x, y, x + 3, y + 3, c)
    px(x + 2, y + 2, darken(c, 0.15))


def lamp(x, y):
    rect(x + 2, y + 3, x + 3, y + 8, METAL[1])
    rect(x, y + 8, x + 5, y + 9, METAL[2])
    rect(x, y, x + 6, y + 3, "#e8853a")
    rect(x, y, x + 6, y + 1, "#f6b066")


def mini_plant(x, y):
    rect(x, y + 3, x + 4, y + 6, TERRA[0])
    disc(x + 2, y + 2, 2.5, 2, LEAF[1])
    px(x + 1, y + 1, LEAF[3])


def plant(x, y, size=1.0, pot=POT):
    """Potted floor plant; (x, y) = pot top-left."""
    pw = int(10 * size)
    rect(x, y, x + pw, y + int(8 * size), pot[0])
    rect(x, y + int(6 * size), x + pw, y + int(8 * size), pot[1])
    rect(x + 1, y, x + pw - 1, y + 2, "#5a3e2a")
    cx, cy = x + pw / 2, y - 5 * size
    for i in range(9):
        a = i * 0.7
        ox, oy = np.cos(a) * 5 * size, np.sin(a) * 4 * size
        disc(cx + ox, cy + oy, 4 * size, 3.2 * size, LEAF[1 + (i % 2)])
    for i in range(6):
        a = i * 1.1 + 0.4
        disc(cx + np.cos(a) * 3 * size - 1, cy + np.sin(a) * 2.5 * size - 2, 2 * size, 1.6 * size, LEAF[3 if i % 2 else 2])
    disc(cx, cy, 2.5 * size, 2 * size, LEAF[0])
    disc(cx - 1, cy - 1, 1.5, 1.2, LEAF[3])


def books(x, y, w, h, seed):
    cols = ["#b0473a", "#3f6f8f", "#d8b44a", "#4f8f5c", "#e8e2d4", "#7a4f8f", "#c96a3a", "#2f4f6f"]
    xx, i = x, 0
    while xx < x + w:
        bw = 1 + int(Hh(i, seed, 1) * 2)
        bh = h - int(Hh(i, seed, 2) * 3)
        if xx + bw > x + w:
            break
        if Hh(i, seed, 4) > 0.12:
            c = cols[int(Hh(i, seed, 3) * len(cols))]
            rect(xx, y + h - bh, xx + bw, y + h, c)
            rect(xx, y + h - bh, xx + bw, y + h - bh + 1, lighten(c, 0.25))
        xx += bw + (1 if Hh(i, seed, 5) < 0.2 else 0)
        i += 1


# ======================================================= pixel font ===
GLYPHS = {
    "G": [".##", "#..", "#.#", "#.#", ".##"],
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "S": [".##", "#..", ".#.", "..#", "##."],
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "O": [".#.", "#.#", "#.#", "#.#", ".#."],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "I": ["#", "#", "#", "#", "#"],
    "E": ["###", "#..", "##.", "#..", "###"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"],
    " ": ["..", "..", "..", "..", ".."],
}


def text(x, y, s, c):
    for ch in s:
        g = GLYPHS[ch]
        for r, row in enumerate(g):
            for k, v in enumerate(row):
                if v == "#":
                    px(x + k, y + r, c)
        x += len(g[0]) + 1
    return x


def text_w(s):
    return sum(len(GLYPHS[ch][0]) + 1 for ch in s) - 1


# ============================================================ layout ===
# outer room: walls cap 4..10, top wall face 10..44, floor 44..262
TOP_CAP, FACE_Y0, FACE_Y1 = 4, 10, 44
FL_X0, FL_X1, FL_Y0, FL_Y1 = 10, 374, 44, 262
PART_X = 254                     # partition cap 254..260 between open plan and right rooms
RW_Y = 136                       # right rooms horizontal wall: cap 136..140, face 140..156


def floor_wood(x0, y0, x1, y1, seed=0):
    rect(x0, y0, x1, y1, FLOOR[1])
    for row, yy in enumerate(range(y0, y1, 5)):
        xx = x0 - int(Hh(row, seed, 1) * 20)
        while xx < x1:
            ln = 14 + int(Hh(xx, row, seed + 2) * 18)
            c = FLOOR[int(Hh(xx, row, seed + 3) * 4)]
            rect(max(x0, xx), yy, min(x1, xx + ln), min(y1, yy + 4), c)
            if Hh(xx, row, seed + 9) < 0.35:                 # wood knot / grain fleck
                gx = xx + 3 + int(Hh(xx, row, 11) * max(1, ln - 6))
                if x0 <= gx < x1:
                    rect(gx, yy + 1, min(x1, gx + 3), yy + 2, darken(c, 0.06))
            rect(max(x0, xx + ln - 1), yy, min(x1, xx + ln), min(y1, yy + 4), FLOOR_GAP)
            xx += ln
        rect(x0, min(y1, yy + 4), x1, min(y1, yy + 5), FLOOR_GAP)


def floor_carpet(x0, y0, x1, y1):
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            t = ((xx // 8) + (yy // 8)) % 2
            c = CARPET[t]
            if Hh(xx, yy, 21) < 0.08:
                c = CARPET[2]
            px(xx, yy, c)


def wall_face(x0, x1, y0, y1):
    rect(x0, y0, x1, y1, WALL[1])
    rect(x0, y0, x1, y0 + 2, WALL[0])
    for xx in range(x0, x1, 2):                                  # light vertical texture
        if Hh(xx, y0, 31) < 0.25:
            rect(xx, y0 + 3, xx + 1, y1 - 10, WALL[2])
    rect(x0, y1 - 9, x1, y1 - 2, DARK_T[1])                     # wainscot
    rect(x0, y1 - 9, x1, y1 - 8, DARK_T[0])
    for xx in range(x0 + 6, x1, 12):
        rect(xx, y1 - 7, xx + 1, y1 - 3, DARK_T[2])
    rect(x0, y1 - 2, x1, y1, DARK_F[2])                         # baseboard


def window(x, y, w, h):
    rect(x - 1, y - 1, x + w + 1, y + h + 1, OL)
    rect(x, y, x + w, y + h, "#f4efe2")
    for yy in range(y + 2, y + h - 2):
        rect(x + 2, yy, x + w - 2, yy + 1, mix(SKY[0], SKY[2], (yy - y) / h))
    # distant city skyline at the bottom of the glass
    xx = x + 2
    while xx < x + w - 2:
        bw = 3 + int(Hh(xx, y, 41) * 5)
        bh = 3 + int(Hh(xx, y, 42) * (h // 2 - 2))
        rect(xx, y + h - 2 - bh, min(x + w - 2, xx + bw), y + h - 2, mix("#8fb4c8", "#6f97ae", Hh(xx, y, 43)))
        xx += bw + 1
    rect(x + w // 2, y, x + w // 2 + 1, y + h, "#f4efe2")        # mullion
    for g in (4, 7):                                              # glints
        for k in range(4):
            px(x + g + k, y + h - 6 - k, "#ffffff")
    rect(x - 2, y + h + 1, x + w + 2, y + h + 3, WHITE_T[2])     # sill


def sign_gastron(x, y):
    w = 58
    rect(x - 1, y - 1, x + w + 1, y + 15, OL)
    rect(x, y, x + w, y + 14, RED)
    rect(x, y, x + w, y + 1, lighten(RED, 0.3))
    rect(x, y + 13, x + w, y + 14, darken(RED, 0.25))
    # flame mark
    fx, fy = x + 5, y + 2
    for r, row in enumerate(["..#..", ".##..", ".###.", "##.##", "#...#", "#.#.#", ".###."]):
        for k, v in enumerate(row):
            if v == "#":
                px(fx + k, fy + r, "#ffffff")
    tx = x + 15 + (w - 19 - text_w("GASTRON")) // 2
    text(tx, y + 3, "GASTRON", "#ffffff")
    rect(tx, y + 10, tx + text_w("GASTRON"), y + 11, lighten(RED, 0.35))


def whiteboard(x, y, w, h):
    rect(x - 1, y - 1, x + w + 1, y + h + 1, OL)
    rect(x, y, x + w, y + h, METAL[0])
    rect(x + 1, y + 1, x + w - 1, y + h - 1, "#f7f6f2")
    # sticky notes + a trend line = campaign planning board
    for i, c in enumerate(["#f6d04d", "#f59ab0", "#8fd3a8", "#9cc8f0", "#f6d04d", "#f59ab0"]):
        sticky(x + 3 + (i % 3) * 5, y + 3 + (i // 3) * 5, c)
    pts = [(x + 20, y + h - 4), (x + 25, y + h - 7), (x + 29, y + h - 6), (x + 34, y + h - 11), (x + w - 4, y + 4)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(by - ay))
        for t in range(n + 1):
            px(ax + (bx - ax) * t // n, ay + (by - ay) * t // n, RED)
    rect(x + 20, y + 3, x + 30, y + 4, "#5a6170")
    rect(x + 20, y + 6, x + 27, y + 7, "#9aa0ab")
    rect(x + 4, y + h, x + w - 4, y + h + 2, METAL[1])           # marker tray


def clock(x, y):
    disc(x, y, 4.5, 4.5, OL)
    disc(x, y, 3.5, 3.5, "#f7f6f2")
    px(x, y - 1, OL)
    px(x, y - 2, OL)
    px(x + 1, y, OL)
    px(x, y, RED)


def frame(x, y, w, h, kind):
    rect(x - 1, y - 1, x + w + 1, y + h + 1, OL)
    rect(x, y, x + w, y + h, DARK_T[0])
    rect(x + 1, y + 1, x + w - 1, y + h - 1, "#f4efe2")
    if kind == "cert":
        rect(x + 2, y + 2, x + w - 2, y + 3, "#9aa0ab")
        rect(x + 3, y + 4, x + w - 3, y + 5, "#c9c4b8")
        disc(x + w // 2, y + h - 3, 1.5, 1.5, "#d8b44a")
    else:
        rect(x + 2, y + 2, x + w - 2, y + h - 2, SKY[1])
        for k in range(x + 2, x + w - 2):
            hh = int(2 + 3 * Hh(k // 3, y, 51))
            rect(k, y + h - 2 - hh, k + 1, y + h - 2, GREEN)


def tv(x, y, w, h):
    rect(x - 1, y - 1, x + w + 1, y + h + 1, OL)
    rect(x, y, x + w, y + h, "#1d2028")
    rect(x + 1, y + 1, x + w - 1, y + h - 1, "#24364a")
    # presentation slide: title + KPI bars
    rect(x + 3, y + 2, x + 14, y + 3, "#e8f6f8")
    for i in range(5):
        bh = 2 + int(Hh(i, x, 61) * (h - 6))
        rect(x + 4 + i * 4, y + h - 2 - bh, x + 6 + i * 4, y + h - 2, [RED, GREEN, "#f6b066", GREEN, RED][i])
    rect(x + w - 14, y + 3, x + w - 3, y + h - 2, "#f4f1ea")
    disc(x + w - 9, y + 7, 2.5, 2.5, RED)
    px(x + w - 9, y + 5, "#ffffff")


def ac_unit(x, y):
    rect(x - 1, y - 1, x + 27, y + 9, OL)
    rect(x, y, x + 26, y + 8, "#f4f1ea")
    rect(x, y + 5, x + 26, y + 6, "#c9c4b8")
    rect(x + 2, y + 6, x + 24, y + 7, "#9aa0ab")
    px(x + 22, y + 2, GREEN)


# ======================================================= characters ===
SPR_FRONT = [
    "...oooooo...",
    "..ohhHHhho..",
    ".ohhHhhhhho.",
    ".ohhhhhhhho.",
    ".ohssssssho.",
    ".osesssseso.",
    ".osssmmssso.",
    "..oSssssSo..",
    ".occwwwwcco.",
    "ocCccccccCco",
    "ocCccccccCco",
    "osCccccccCso",
    "oooooooooooo",
]
SPR_BACK = [
    "...oooooo...",
    "..ohhHHhho..",
    ".ohhHhhhhho.",
    ".ohhhhhhhho.",
    ".ohhhhhhhho.",
    ".ohhhhhhhho.",
    ".oHhhhhhhho.",
    "..ohhhhhho..",
    ".occSssScco.",
    "ocCccccccCco",
    "ocCccccccCco",
    "ocCccccccCco",
    "oooooooooooo",
]


def person(x, y, look, facing):
    """12x13 seated chibi. (x, y) = sprite top-left. Extra hair/hat rows may go above y."""
    hair, skin, shirt = look["hair"], look["skin"], look["shirt"]
    style, outfit, acc = look["hairStyle"], look["outfit"], look.get("accessory")
    pal = {
        "o": OL, "h": hair, "H": lighten(hair, 0.28), "s": skin, "S": darken(skin, 0.14),
        "e": "#2b2230", "m": darken(skin, 0.1), "c": shirt, "C": darken(shirt, 0.22), "w": "#f4f1ea",
    }
    rows = [list(r) for r in (SPR_FRONT if facing == "S" else SPR_BACK)]
    extra = {}                                       # (col, row) -> colour, row may be negative

    if style == "long":
        for r in range(5, 10) if facing == "S" else range(6, 10):
            for c in (1, 10) if facing == "S" else range(1, 11):
                if facing == "N" and rows[r][c] in "o.":
                    continue
                rows[r][c] = "h"
            rows[r][0] = rows[r][11] = "o"
    elif style == "bun":
        for c, ch in enumerate("....oooo...."):
            if ch == "o":
                extra[(c, -3)] = OL
        for c, ch in enumerate("...ohHho...."):
            if ch != ".":
                extra[(c, -2)] = pal[ch]
        for c, ch in enumerate("...ohhho...."):
            if ch != ".":
                extra[(c, -1)] = pal[ch]
    elif style == "spiky":
        for c in (3, 5, 7):
            extra[(c, -1)] = OL
            extra[(c + 1, -1)] = OL
            rows[0][c + 1] = "h" if facing == "S" else "H"
    elif style == "cap":
        capc = "#2c3e50"
        for r in (1, 2, 3):
            for c in range(12):
                if rows[r][c] in "hH":
                    extra[(c, r)] = capc if (r, c) != (1, 5) else lighten(capc, 0.3)
        if facing == "S":
            for c in range(2, 10):
                extra[(c, 4)] = darken(capc, 0.3)
        px_logo = (5, 2)
        extra[px_logo] = "#e8853a"

    if outfit == "suit":
        rows[8][5] = rows[8][6] = "w" if facing == "S" else rows[8][5]
        if facing == "S":
            extra[(5, 9)] = RED
            extra[(6, 9)] = RED
            extra[(5, 10)] = darken(RED, 0.2)
            for r in (9, 10, 11):
                extra[(4, r)] = darken(shirt, 0.35)
                extra[(7, r)] = darken(shirt, 0.35)
    elif outfit == "hoodie":
        if facing == "S":
            extra[(4, 9)] = "#f4f1ea"
            extra[(7, 9)] = "#f4f1ea"
        else:
            for c in range(3, 9):
                extra[(c, 8)] = darken(shirt, 0.15)
    elif outfit == "sweater":
        for c in range(1, 11):
            if rows[10][c] in "cC":
                extra[(c, 10)] = lighten(shirt, 0.18) if c % 2 else shirt

    if acc == "glasses" and facing == "S":
        for c, col in zip(range(2, 10), ["g", "e", "g", "g", "g", "g", "e", "g"]):
            extra[(c, 5)] = "#2b2230" if col == "g" else "#9fd6e0"
    elif acc == "headphones":
        band = "#3b3f4a"
        for c in range(3, 9):
            extra[(c, 0)] = band
        for r in (4, 5, 6):
            extra[(0, r)] = OL
            extra[(1, r)] = "#e8853a" if r == 5 else band
            extra[(10, r)] = "#e8853a" if r == 5 else band
            extra[(11, r)] = OL
    elif acc == "beret":
        bc = "#2b2230"
        for c, ch in enumerate("..oooooooo.."):
            if ch == "o":
                extra[(c, -1)] = OL
        for c in range(2, 10):
            extra[(c, 0)] = bc
        for c in range(1, 9):
            extra[(c, 1)] = bc if c > 1 else OL
        extra[(9, 1)] = lighten(bc, 0.2)

    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch != ".":
                px(x + c, y + r, pal[ch])
    for (c, r), col in extra.items():
        px(x + c, y + r, col)


def chair_back_view(x, y, accent):
    """Office chair seen from behind the sitter (sitter faces north). 14 wide."""
    rect(x, y, x + 10, y + 8, CHAIR[1])
    rect(x, y, x + 10, y + 1, lighten(CHAIR[1], 0.2))
    rect(x + 2, y + 2, x + 8, y + 3, accent)
    rect(x + 4, y + 8, x + 6, y + 10, METAL[2])
    rect(x + 1, y + 10, x + 9, y + 11, METAL[1])


def chair_top_view(x, y, accent):
    """Office chair behind a south-facing sitter: we see the backrest top + seat edges."""
    rect(x, y, x + 14, y + 5, CHAIR[1])
    rect(x, y, x + 14, y + 1, lighten(CHAIR[1], 0.22))
    rect(x + 2, y + 2, x + 12, y + 3, accent)
    rect(x - 1, y + 7, x + 1, y + 12, CHAIR[2])                  # armrests
    rect(x + 13, y + 7, x + 15, y + 12, CHAIR[2])


def empty_chair_north(x, y):
    """Empty meeting chair, backrest on the north side."""
    rect(x, y, x + 10, y + 3, CHAIR[1])
    rect(x, y, x + 10, y + 1, lighten(CHAIR[1], 0.2))
    rect(x + 1, y + 3, x + 9, y + 9, CHAIR[0])
    rect(x + 1, y + 8, x + 9, y + 9, CHAIR[2])


def empty_chair_south(x, y):
    rect(x + 1, y, x + 9, y + 6, CHAIR[0])
    rect(x + 1, y, x + 9, y + 1, lighten(CHAIR[0], 0.2))
    rect(x, y + 6, x + 10, y + 10, CHAIR[1])
    rect(x, y + 9, x + 10, y + 10, CHAIR[2])


# ============================================================ agents ===
AGENT_LOOKS = {
    "director":   dict(hair="#2b1d16", skin="#f1c27d", shirt="#26324f", hairStyle="short", outfit="suit"),
    "strategist": dict(hair="#8a3b1e", skin="#f3c9a0", shirt="#8e44ad", hairStyle="long", outfit="blouse"),
    "researcher": dict(hair="#1d1d1d", skin="#d9a066", shirt="#16a085", hairStyle="spiky", outfit="shirt", accessory="glasses"),
    "copywriter": dict(hair="#e0a526", skin="#f3c9a0", shirt="#e74c3c", hairStyle="bun", outfit="sweater"),
    "content":    dict(hair="#5b3a29", skin="#c68642", shirt="#f39c12", hairStyle="short", outfit="hoodie", accessory="headphones"),
    "creative":   dict(hair="#ff6fb5", skin="#f1c27d", shirt="#1abc9c", hairStyle="long", outfit="sweater", accessory="beret"),
    "social":     dict(hair="#2c1b10", skin="#e0ac69", shirt="#3498db", hairStyle="bun", outfit="blouse"),
    "ads":        dict(hair="#4a3020", skin="#f5d0a9", shirt="#27ae60", hairStyle="short", outfit="shirt"),
    "seo":        dict(hair="#111111", skin="#c68642", shirt="#7f8c8d", hairStyle="spiky", outfit="hoodie", accessory="glasses"),
    "analyst":    dict(hair="#6d4c41", skin="#f1c27d", shirt="#34495e", hairStyle="long", outfit="sweater", accessory="glasses"),
    "qa":         dict(hair="#3e2723", skin="#e8b48a", shirt="#d35400", hairStyle="cap", outfit="shirt", accessory="headphones"),
}
ROW1 = ["strategist", "researcher", "copywriter", "content", "creative"]       # face the viewer
ROW2 = ["social", "ads", "seo", "analyst", "qa"]                             # backs to viewer
MON_KIND = {"social": 3, "ads": 1, "seo": 0, "analyst": 1, "qa": 0}
DESK_XS = [22, 68, 114, 160, 206]
DESK_W = 38
SEATS = {}


# ============================================================ render ===
def render(with_people):
    global im, d
    im = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(im)
    SEATS.clear()

    # ---------------- floors
    floor_wood(FL_X0, FL_Y0, PART_X, FL_Y1, seed=1)
    floor_wood(PART_X + 6, FL_Y0, FL_X1, RW_Y, seed=4)
    floor_carpet(PART_X + 6, RW_Y + 20, FL_X1, FL_Y1)

    # window light pools on the floor
    for wx, ww in ((20, 44), (196, 46), (304, 44)):
        for k in range(26):
            shade(wx + k // 2, FL_Y0 + k, wx + ww + k // 2, FL_Y0 + k + 1, "#fff6dc", 0.16 * (1 - k / 30))

    # rugs
    def rug(x0, y0, x1, y1, base, border):
        rect(x0, y0, x1, y1, border)
        rect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, base)
        for yy in range(y0 + 4, y1 - 4, 4):
            for xx in range(x0 + 4 + (yy // 4 % 2) * 2, x1 - 4, 4):
                px(xx, yy, lighten(base, 0.12))
        rect(x0 + 3, y0 + 3, x1 - 3, y0 + 4, lighten(border, 0.2))
    rug(18, 196, 104, 250, "#3c776f", "#e0c8a0")                         # lounge rug
    rug(276, 64, 360, 128, "#7a4f36", "#d8b44a")                           # director rug

    # ---------------- top wall
    wall_face(FL_X0, FL_X1, FACE_Y0, FACE_Y1)
    rect(FL_X0 - 6, TOP_CAP, FL_X1 + 6, FACE_Y0, CAP[0])
    rect(FL_X0 - 6, TOP_CAP, FL_X1 + 6, TOP_CAP + 1, lighten(CAP[0], 0.15))
    # decor on the open-plan wall
    window(20, 13, 44, 20)
    sign_gastron(72, 15)
    whiteboard(138, 14, 48, 18)
    window(196, 13, 46, 20)
    # decor on the director's wall
    frame(266, 16, 10, 12, "cert")
    window(304, 13, 44, 20)
    clock(364, 22)
    frame(282, 18, 14, 10, "art")

    # ---------------- partition walls (thin caps seen from above) + right-room wall face
    def vcap(x, y0, y1):
        rect(x, y0, x + 6, y1, CAP[0])
        rect(x, y0, x + 1, y1, lighten(CAP[0], 0.15))
        rect(x + 5, y0, x + 6, y1, CAP[1])
    vcap(PART_X, FL_Y0 - 2, 98)
    vcap(PART_X, 122, 206)
    vcap(PART_X, 230, FL_Y1)
    # doorway thresholds
    rect(PART_X, 98, PART_X + 6, 122, DARK_T[1])
    rect(PART_X, 206, PART_X + 6, 230, DARK_T[1])
    wall_face(PART_X + 6, FL_X1, RW_Y + 4, RW_Y + 20)
    rect(PART_X, RW_Y, FL_X1 + 6, RW_Y + 4, CAP[0])
    rect(PART_X, RW_Y, FL_X1 + 6, RW_Y + 1, lighten(CAP[0], 0.15))

    # outer side + bottom caps
    for x0, x1 in ((FL_X0 - 6, FL_X0), (FL_X1, FL_X1 + 6)):
        rect(x0, TOP_CAP, x1, FL_Y1 + 6, CAP[0])
    rect(FL_X0 - 6, FL_Y1, FL_X1 + 6, FL_Y1 + 6, CAP[0])
    rect(FL_X0 - 6, FL_Y1, FL_X1 + 6, FL_Y1 + 1, lighten(CAP[0], 0.15))
    # front door gap in the bottom wall (open plan)
    rect(226, FL_Y1, 246, FL_Y1 + 6, DARK_T[1])
    rect(228, FL_Y1 + 1, 244, FL_Y1 + 5, "#2f5c56")                      # door mat

    # ---------------- meeting room (carpet, south-east)
    obj(lambda: tv(290, RW_Y + 5, 56, 12), outline=False, L=1)
    for i, cx in enumerate((290, 312, 334)):
        obj(empty_chair_north, cx, 176)
    obj(lambda: box(282, 186, 72, 16, 5, WHITE_T, WHITE_F))
    obj(lambda: (paper(292, 190), paper(318, 192, 6, 5), mug(340, 189, RED), mini_plant(312, 186 - 1)), outline=False, L=0)
    for cx in (290, 312, 334):
        obj(empty_chair_south, cx, 210)
    obj(empty_chair_north, 268, 190)
    obj(empty_chair_north, 358, 190)
    obj(plant, 362, 248, 0.9)
    obj(plant, 266, 248, 0.9)

    # ---------------- director's office (north-east)
    obj(lambda: box(262, 36, 18, 4, 30, DARK_T, DARK_F, panels=0))       # bookshelf against wall
    obj(lambda: books(264, 42, 14, 8, 3), outline=False, L=0)
    obj(lambda: books(264, 53, 14, 8, 7), outline=False, L=0)
    obj(lambda: books(264, 63, 14, 0, 9), outline=False, L=0)
    obj(lambda: box(354, 38, 16, 4, 22, METAL, [METAL[1], METAL[2], METAL[2]], panels=0))
    for k in range(3):
        rect(357, 44 + k * 7, 367, 45 + k * 7, METAL[0])
        rect(360, 46 + k * 7, 364, 47 + k * 7, "#c9c4b8")
    if with_people:
        obj(chair_top_view, 307, 58, RED)
        obj(person, 308, 63, AGENT_LOOKS["director"], "S", L=0)
    SEATS["director"] = dict(x=308, y=63, facing="S", room="director")
    obj(lambda: box(284, 76, 60, 14, 9, DARK_T, DARK_F, panels=3))       # executive desk
    obj(lambda: (laptop_back(325, 74), monitor(288, 70, 2, 12, 8), lamp(338, 70), paper(309, 81, 7, 5), mug(302, 82), sticky(292, 83, "#f6d04d")), outline=False, L=0)
    obj(empty_chair_south, 296, 106)
    obj(empty_chair_south, 324, 106)
    obj(plant, 358, 120, 0.9)
    obj(plant, 264, 120, 0.8, TERRA)

    # ---------------- open plan, row 1 (people face the viewer)
    for i, (dx, aid) in enumerate(zip(DESK_XS, ROW1)):
        if with_people:
            obj(chair_top_view, dx + 12, 52, [RED, GREEN][i % 2])
            obj(person, dx + 13, 57, AGENT_LOOKS[aid], "S", L=0)
        SEATS[aid] = dict(x=dx + 13, y=57, facing="S", room="open")
    for i, dx in enumerate(DESK_XS):
        obj(lambda dx=dx: box(dx, 72, DESK_W, 12, 8, WOOD_T, WOOD_F, panels=2))
        def clutter(dx=dx, i=i):
            laptop_back(dx + 24, 70)
            paper(dx + 14, 76, 6, 4)
            if i % 2 == 0:
                mug(dx + 4, 74, [RED, "#e8e2d4", GREEN][i % 3])
                sticky(dx + 8, 78, "#f6d04d")
            else:
                mini_plant(dx + 3, 70)
                sticky(dx + 9, 77, "#9cc8f0")
        obj(clutter, outline=False, L=0)
    # low teal divider screens between row-1 desks
    for dx in DESK_XS[1:]:
        obj(lambda dx=dx: box(dx - 6, 64, 4, 3, 20, TEAL_T, TEAL_F))

    # ---------------- open plan, row 2 (people show their backs, screens face us)
    for i, dx in enumerate(DESK_XS):
        obj(lambda dx=dx: box(dx, 118, DESK_W, 12, 8, WOOD_T, WOOD_F, panels=2))
    for i, (dx, aid) in enumerate(zip(DESK_XS, ROW2)):
        def setup(dx=dx, i=i, aid=aid):
            monitor(dx + 12, 108, MON_KIND[aid])
            keyboard(dx + 14, 123)
            if aid in ("ads", "analyst"):
                monitor(dx + 27, 110, 0, 9, 7)
            else:
                mug(dx + 30, 121, [GREEN, "#e8e2d4", RED][i % 3])
            paper(dx + 3, 121) if i % 2 else mini_plant(dx + 3, 117)
        obj(setup, outline=False, L=0)
        if with_people:
            obj(person, dx + 13, 127, AGENT_LOOKS[aid], "N", L=0)
            obj(chair_back_view, dx + 14, 141, [RED, GREEN][i % 2])
        SEATS[aid] = dict(x=dx + 13, y=127, facing="N", room="open")
    for dx in DESK_XS[1:]:
        obj(lambda dx=dx: box(dx - 6, 108, 4, 3, 22, TEAL_T, TEAL_F))

    # ---------------- lounge (south-west)
    def sofa(x, y, w):
        rect(x, y, x + w, y + 14, TEAL_T[1])                    # seat cushions (seen from above)
        for k in range(1, 3):
            rect(x + k * w // 3, y + 1, x + k * w // 3 + 1, y + 13, TEAL_T[2])
        rect(x, y, x + w, y + 1, TEAL_T[0])
        rect(x - 6, y + 13, x + w + 6, y + 19, TEAL_T[0])       # backrest top (south side)
        rect(x - 6, y + 19, x + w + 6, y + 24, TEAL_F[0])       # backrest front
        rect(x - 6, y + 23, x + w + 6, y + 24, TEAL_F[2])
        for ax in (x - 6, x + w):                                 # arms
            rect(ax, y - 2, ax + 6, y + 19, TEAL_T[0])
            rect(ax + 1, y - 1, ax + 5, y + 18, TEAL_T[1])
        rect(x + 4, y + 8, x + 14, y + 12, "#f6d04d")             # cushions
        rect(x + w - 14, y + 8, x + w - 4, y + 12, "#f4f1ea")
    obj(sofa, 26, 230, 56)
    obj(lambda: box(36, 210, 34, 10, 5, WOOD_T, WOOD_F))                                # coffee table
    obj(lambda: (mug(42, 212, RED), mug(58, 213), paper(48, 213, 6, 4)), outline=False, L=0)
    obj(lambda: box(20, 198, 12, 8, 6, TEAL_T, TEAL_F))                                 # pouf
    obj(plant, 92, 196, 1.1, TERRA)
    obj(plant, 12, 172, 1.0)

    # ---------------- pantry (south-centre)
    obj(lambda: box(112, 234, 64, 12, 14, WHITE_T, WHITE_F, panels=4))                 # counter
    def pantry():
        # coffee machine
        rect(118, 226, 130, 238, "#3a3e4b")
        rect(118, 226, 130, 227, "#5a6170")
        rect(121, 230, 127, 234, "#1d2028")
        px(128, 228, RED)
        mug(122, 238, "#f4f1ea")
        # microwave
        rect(148, 228, 166, 239, "#d6dae2")
        rect(150, 230, 160, 237, "#2f3a48")
        rect(162, 231, 164, 233, "#5a6170")
        mug(136, 238, RED)
        paper(140, 240, 5, 4)
    obj(pantry, L=0)
    obj(lambda: box(180, 218, 16, 6, 34, WHITE_T, WHITE_F))                             # fridge
    obj(lambda: (rect(182, 232, 194, 233, WHITE_F[2]), rect(192, 236, 193, 242, METAL[1]), rect(192, 226, 193, 230, METAL[1])), outline=False, L=0)
    def cooler():
        rect(202, 240, 212, 252, "#e2ddd2")
        rect(202, 240, 212, 241, "#f4f1ea")
        px(205, 244, RED)
        px(209, 244, "#3d7f98")
        disc(207, 234, 5, 6, "#8fcde4")
        disc(206, 232, 2, 2, "#d4f0fa")
        rect(205, 227, 210, 229, "#3d7f98")
    obj(cooler)

    # ---------------- shared kit (open plan, east)
    obj(lambda: box(212, 170, 30, 10, 10, METAL, [METAL[1], METAL[2], METAL[2]], panels=1))   # printer cabinet
    def printer():
        rect(214, 164, 240, 174, "#e2ddd2")
        rect(214, 164, 240, 165, "#f4f1ea")
        rect(218, 162, 236, 165, "#f4f1ea")
        rect(222, 168, 232, 170, "#2b2230")
        px(237, 167, GREEN)
    obj(printer)
    obj(plant, 240, 236, 0.9)
    obj(plant, 136, 176, 0.9, TERRA)
    obj(lambda: box(150, 174, 40, 10, 6, WOOD_T, WOOD_F))                 # standing table / huddle
    obj(lambda: (paper(156, 177), paper(170, 176, 6, 5), sticky(182, 178, "#f59ab0")), outline=False, L=0)
    obj(lambda: whiteboard(20, 156, 44, 18), L=2)
    obj(lambda: (rect(23, 175, 25, 186, METAL[1]), rect(59, 175, 61, 186, METAL[1])), outline=True, L=1)

    # vignette: darken the very edge of the room a touch
    for k in range(4):
        a = 0.07 * (4 - k)
        shade(FL_X0 + k, FL_Y0, FL_X0 + k + 1, FL_Y1, "#2b2230", a)
        shade(FL_X1 - k - 1, FL_Y0, FL_X1 - k, FL_Y1, "#2b2230", a)
    return im


if __name__ == "__main__":
    for name, people in (("office", True), ("office-bg", False)):
        img = render(people).convert("RGB")
        img.save(OUT / f"{name}.png")
        img.resize((W * 3, H * 3), Image.NEAREST).save(OUT / f"{name}-x3.png")
    (OUT / "seats.json").write_text(json.dumps(
        {"size": [W, H], "sprite": [12, 13], "seats": SEATS}, indent=2))
    print("wrote office.png, office-bg.png, seats.json")
