"""Gastron office scene (v2) — warm, chunky top-down pixel art after Ref/c40ce0...jpg.

Procedural: planks, checker sand aisle, raised grass planters with soil cliffs,
round bushes, wooden desks with cyan-glow monitors. No clouds.
Run:  python3 scene.py   ->  office-scene.png (480x320, 1x) + office-scene-x3.png
"""
from pathlib import Path
from PIL import Image, ImageDraw

W, H = 480, 320
OUT = Path(__file__).parent
im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
d = ImageDraw.Draw(im)


def hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def Hh(x, y, s=0):
    n = ((x * 374761393) + (y * 668265263) + (s * 2246822519) + 1013904223) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFFFFFF) / 4294967296


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        im.putpixel((int(x), int(y)), hx(c) + (255,) if isinstance(c, str) else c)


def rect(x0, y0, x1, y1, c):  # inclusive-exclusive
    d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=hx(c))


def blend(x, y, c, a):
    if 0 <= x < W and 0 <= y < H:
        r, g, b, _ = im.getpixel((x, y))
        cr, cg, cb = hx(c)
        im.putpixel((x, y), (int(r + (cr - r) * a), int(g + (cg - g) * a), int(b + (cb - b) * a), 255))


def shade(x0, y0, x1, y1, c, a):
    for y in range(y0, y1):
        for x in range(x0, x1):
            blend(x, y, c, a)


# ------------------------------------------------------------- palette ----
OL = "#3a2620"                     # warm dark outline
WOOD = ["#a8672f", "#bb7a3a", "#c98a4a", "#d89c58"]
WOOD_GAP = "#7c4a26"
SAND = ["#f3d98e", "#ecc774", "#e2b45e"]
SAND_HI = "#fcefc0"
GRASS = ["#3f7d22", "#5a9a28", "#74b02e", "#92c63c"]
SOIL = ["#8a6240", "#6c4a32", "#4a3226"]
PLASTER = ["#efdcae", "#e3c88f", "#cfae78"]
TIMBER = ["#9a6234", "#7a4a28", "#563320"]
SKY = ["#8fe0e4", "#62ccd6", "#42b0c4"]
CYAN = ["#5ee1f0", "#9af4fa", "#c8fbff"]


# --------------------------------------------------------------- floor ----
def planks(x0, y0, x1, y1):
    for y in range(y0, y1):
        row = (y - y0) // 8
        for x in range(x0, x1):
            off = int(Hh(row, 7) * 32)
            seg = (x - x0 + off) // 32
            base = WOOD[int(Hh(row, seg, 3) * 3)]
            if (y - y0) % 8 == 7:
                base = WOOD_GAP
            elif (x - x0 + off) % 32 == 0:
                base = WOOD_GAP
            elif (y - y0) % 8 == 0:
                base = WOOD[min(3, WOOD.index(base) + 1)]
            elif Hh(x, y, 11) < 0.07:
                base = WOOD[min(3, WOOD.index(base) + 1)] if Hh(x, y, 12) < 0.5 else WOOD[max(0, WOOD.index(base) - 1)]
            px(x, y, base)


def checker(x0, y0, x1, y1):
    for y in range(y0, y1):
        for x in range(x0, x1):
            cx, cy = (x - x0) // 8, (y - y0) // 8
            c = SAND[(cx + cy) % 2]
            lx, ly = (x - x0) % 8, (y - y0) % 8
            if lx == 0 or ly == 0:
                c = SAND[2] if (cx + cy) % 2 == 0 else SAND[1]
            if Hh(cx, cy, 5) < 0.16 and 2 <= lx <= 5 and 2 <= ly <= 5:
                c = SAND_HI
            elif Hh(x, y, 9) < 0.02:
                c = SAND_HI
            px(x, y, c)
    for x in range(x0, x1):  # soft edge shadow at both aisle borders
        for k in (0, 1):
            blend(x0 + k if False else x, y0, "#b88840", 0)  # placeholder keeps API simple
    for y in range(y0, y1):
        for k, a in ((0, 0.35), (1, 0.15)):
            blend(x0 + k, y, "#7c4a26", a)
            blend(x1 - 1 - k, y, "#7c4a26", a)


# ---------------------------------------------------------------- wall ----
def wall():
    for y in range(0, 62):
        for x in range(W):
            t = 0 if y < 40 else 1
            c = PLASTER[t]
            if Hh(x, y, 2) < 0.05:
                c = PLASTER[min(2, t + 1)] if Hh(x, y, 3) < 0.6 else PLASTER[0]
            px(x, y, c)
    # timber beams (vertical posts every 80px, horizontal rail at top)
    rect(0, 0, W, 6, TIMBER[1])
    for y in range(0, 6):
        for x in range(W):
            if y == 0:
                px(x, y, TIMBER[0])
            elif y == 5:
                px(x, y, TIMBER[2])
            elif Hh(x // 3, y, 4) < 0.18:
                px(x, y, TIMBER[0])
    for bx in range(0, W + 1, 80):
        rect(bx - 3, 6, bx + 3, 62, TIMBER[1])
        rect(bx - 3, 6, bx - 2, 62, TIMBER[0])
        rect(bx + 2, 6, bx + 3, 62, TIMBER[2])
    # wainscot
    for y in range(46, 64):
        for x in range(W):
            c = TIMBER[1] if (x // 8) % 2 == 0 else "#855230"
            if y == 46:
                c = TIMBER[0]
            if (x % 8) == 7:
                c = TIMBER[2]
            px(x, y, c)
    rect(0, 62, W, 64, TIMBER[2])
    shade(0, 64, W, 70, "#3a2620", 0.28)
    shade(0, 70, W, 74, "#3a2620", 0.12)


def window(x, y, w=44, h=34):
    rect(x - 3, y - 3, x + w + 3, y + h + 5, TIMBER[2])
    rect(x - 2, y - 2, x + w + 2, y + h + 3, TIMBER[0])
    for yy in range(h):
        for xx in range(w):
            t = yy / h
            c = SKY[0] if t < 0.35 else SKY[1] if t < 0.7 else SKY[2]
            px(x + xx, y + yy, c)
    # distant green hills + trees (no clouds)
    for xx in range(w):
        hill = int(h * 0.62 + 4 * ((xx * 0.21) % 2.2 - 1.1) ** 2 - 2 * (xx % 7 == 0))
        for yy in range(hill, h):
            px(x + xx, y + yy, GRASS[2] if yy == hill else GRASS[1] if yy < hill + 5 else GRASS[0])
    for tx in (6, 17, 31, 38):
        ty = int(h * 0.62) - 1
        rect(x + tx, y + ty - 6, x + tx + 6, y + ty, GRASS[0])
        rect(x + tx + 1, y + ty - 8, x + tx + 5, y + ty - 6, GRASS[1])
        px(x + tx + 1, y + ty - 7, GRASS[3])
    rect(x + w // 2 - 1, y, x + w // 2 + 1, y + h, TIMBER[1])  # mullion
    rect(x, y + h // 2 - 1, x + w, y + h // 2 + 1, TIMBER[1])
    rect(x - 4, y + h + 3, x + w + 4, y + h + 6, TIMBER[0])  # sill
    rect(x - 4, y + h + 5, x + w + 4, y + h + 6, TIMBER[2])
    # glass glint
    for k in range(6):
        px(x + 3 + k, y + 9 - k, "#ffffff")
        px(x + 3 + k + 1, y + 9 - k, "#d6fbff")


def sunbeam(x, y, w=44, length=70):
    for yy in range(length):
        sk = int(yy * 0.55)
        a = 0.16 * (1 - yy / length)
        for xx in range(w):
            blend(x + xx + sk, y + yy, "#fff3c0", a)


# ------------------------------------------------------- Gastron signage --
FONT = {
    "G": ["###", "#..", "#.#", "#.#", "###"], "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "S": ["###", "#..", "###", "..#", "###"], "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"], "O": ["###", "#.#", "#.#", "#.#", "###"],
    "N": ["#..#", "##.#", "####", "#.##", "#..#"],
}


def text(x, y, s, c, scale=2):
    for ch in s:
        for r, row in enumerate(FONT[ch]):
            for k, v in enumerate(row):
                if v == "#":
                    rect(x + k * scale, y + r * scale, x + (k + 1) * scale, y + (r + 1) * scale, c)
        x += (len(FONT[ch][0]) + 1) * scale


def sign(cx, y):
    w, h = 124, 30
    x = cx - w // 2
    rect(x - 2, y - 2, x + w + 2, y + h + 2, OL)
    rect(x, y, x + w, y + h, "#d70010")
    rect(x, y, x + w, y + 3, "#ee2a38")
    rect(x, y + h - 3, x + w, y + h, "#a8000c")
    # flame icon in Gastron green plate
    rect(x + 6, y + 5, x + 26, y + 25, "#009143")
    rect(x + 6, y + 5, x + 26, y + 7, "#16b05c")
    fl = ["..#..", ".###.", "#####", "#####", ".###."]
    for r, row in enumerate(fl):
        for k, v in enumerate(row):
            if v == "#":
                rect(x + 11 + k * 2, y + 9 + r * 3, x + 13 + k * 2, y + 12 + r * 3, "#fff3c0" if r > 2 else "#ffd04a")
    text(x + 31, y + 10, "GASTRON", "#fff6e8", 2)
    for xx in (x + 4, x + w - 5):  # rivets
        px(xx, y + h - 6, "#ffb0b6")


def frame_pic(x, y, kind):
    rect(x - 1, y - 1, x + 21, y + 17, OL)
    rect(x, y, x + 20, y + 16, TIMBER[0])
    rect(x + 2, y + 2, x + 18, y + 14, "#f6ecd2")
    if kind == 0:  # bar chart
        for i, hgt in enumerate((4, 7, 5, 9)):
            rect(x + 4 + i * 3, y + 13 - hgt, x + 6 + i * 3, y + 13, "#009143" if i % 2 else "#d70010")
    else:  # target
        for r, c in ((6, "#d70010"), (4, "#f6ecd2"), (2, "#009143")):
            for yy in range(-r, r + 1):
                for xx in range(-r, r + 1):
                    if xx * xx + yy * yy <= r * r:
                        px(x + 10 + xx, y + 8 + yy, c)


# ------------------------------------------------------------- greenery ---
def bush(cx, cy, r, flowers=True):
    shade(cx - r, cy + r - 3, cx + r + 4, cy + r + 3, OL, 0.0)
    for yy in range(-r, r + 1):
        for xx in range(-r, r + 1):
            dist = xx * xx + (yy * 1.1) ** 2
            if dist <= r * r:
                lit = (-xx - yy) / (2 * r)
                n = Hh(cx + xx, cy + yy, 21)
                tone = 3 if lit > 0.35 and n < 0.7 else 2 if lit > 0.0 and n < 0.8 else 1 if lit > -0.35 else 0
                if dist > (r - 1.4) ** 2:
                    tone = 0
                px(cx + xx, cy + yy, GRASS[tone])
    for k in range(3):
        px(cx - r // 2 + k, cy - r // 2 - 1 + k, GRASS[3])
    if flowers:
        for k in range(4):
            fx, fy = cx + int((Hh(cx, k, 31) - 0.5) * r * 1.3), cy + int((Hh(cy, k, 32) - 0.5) * r * 1.3)
            px(fx, fy, ["#ff7a8a", "#ffd04a", "#ffffff", "#ff9c4a"][k % 4])


def planter(x0, y0, x1, y1):
    """Raised grass bed with a soil cliff edge (like the tiered grass in the reference)."""
    shade(x0 + 2, y1 + 4, x1 + 3, y1 + 9, "#3a2620", 0.30)
    for y in range(y0, y1):
        for x in range(x0, x1):
            n = Hh(x // 2, y // 2, 40)
            t = 1 + (n > 0.55) + (n > 0.88) - (n < 0.18)
            if y == y0:
                t = 3
            elif y == y0 + 1:
                t = max(t, 2)
            if (x - x0) % 8 == 3 and (y - y0) % 6 == 2 and Hh(x, y, 41) < 0.6:
                t = 3 if t < 3 else 2
            px(x, y, GRASS[max(0, min(3, t))])
    cliff = 7
    for y in range(y1, y1 + cliff):
        for x in range(x0, x1):
            dep = y - y1
            n = Hh(x, y, 42)
            c = SOIL[0] if dep < 2 else SOIL[1] if dep < 5 else SOIL[2]
            if n < 0.12:
                c = SOIL[min(2, SOIL.index(c) + 1)]
            if dep >= 5 and n < 0.5:  # dithered dark base
                c = OL if (x + y) % 2 == 0 else SOIL[2]
            px(x, y, c)
    for x in range(x0, x1):  # grass overhang
        if Hh(x, 0, 43) < 0.5:
            px(x, y1, GRASS[0])
    for x in range(x0 + 4, x1 - 4, 11):  # small stones
        rect(x, y1 + 1, x + 2, y1 + 3, "#b09a82")
    for y in range(y0, y1 + cliff):
        px(x0 - 1, y, OL)
        px(x1, y, OL)
    for x in range(x0 - 1, x1 + 1):
        px(x, y0 - 1, OL)


def potted_plant(x, y):
    shade(x - 8, y + 12, x + 10, y + 16, OL, 0.0)
    rect(x - 6, y + 4, x + 6, y + 14, "#b8532d")
    rect(x - 6, y + 4, x + 6, y + 6, "#d46a3c")
    rect(x - 5, y + 12, x + 5, y + 14, "#8a3a1e")
    rect(x - 7, y + 3, x + 7, y + 5, "#d46a3c")
    bush(x, y - 3, 8, False)
    shade(x - 8, y + 14, x + 12, y + 18, "#3a2620", 0.22)


# --------------------------------------------------------- furniture ------
def desk(x, y, seed=0, glow=True):
    """48 wide workstation: partition + two monitors + desk + chair (back to viewer)."""
    w = 48
    shade(x + 2, y + 44, x + w + 3, y + 50, "#3a2620", 0.30)
    # partition board with cyan glow rim
    rect(x, y, x + w, y + 10, "#5a4a62")
    rect(x, y, x + w, y + 2, CYAN[0])
    rect(x, y + 2, x + w, y + 3, "#3aa9bc")
    rect(x, y + 9, x + w, y + 10, "#3c2f46")
    for xx in range(x + 2, x + w - 2, 5):
        px(xx, y + 5, "#6e5c78")
    # monitors
    for mx in (x + 4, x + 26):
        rect(mx - 1, y + 3, mx + 19, y + 21, "#1f2236")
        rect(mx, y + 4, mx + 18, y + 19, CYAN[0])
        rect(mx, y + 4, mx + 18, y + 6, CYAN[1])
        for r in range(3):  # fake UI lines
            wl = 6 + int(Hh(seed + r, mx, 50) * 8)
            rect(mx + 2, y + 8 + r * 3, mx + 2 + wl, y + 9 + r * 3, "#2a8aa0")
        px(mx + 1, y + 4, CYAN[2])
        rect(mx + 7, y + 19, mx + 12, y + 22, "#2a2c40")
    if glow:
        shade(x - 2, y + 20, x + w + 2, y + 27, "#5ee1f0", 0.10)
    # desk top
    rect(x, y + 22, x + w, y + 34, WOOD[3])
    rect(x, y + 22, x + w, y + 24, "#ecb06c")
    rect(x, y + 34, x + w, y + 38, WOOD[0])
    rect(x, y + 37, x + w, y + 38, WOOD_GAP)
    for xx in range(x + 2, x + w - 2, 6):
        px(xx, y + 28 + int(Hh(xx, y, 51) * 3), WOOD[2])
    for xx in range(x, x + w):
        px(xx, y + 21, OL)
    px(x - 1, y + 22, OL)
    # keyboard + mug + paper
    rect(x + 10, y + 27, x + 24, y + 31, "#d8d4e0")
    rect(x + 10, y + 30, x + 24, y + 31, "#a8a4b8")
    rect(x + 38, y + 25, x + 42, y + 30, "#f6ecd2")
    px(x + 40, y + 27, "#d70010")
    rect(x + 2, y + 26, x + 6, y + 31, "#ffffff")
    # desk legs/drawer
    rect(x + 2, y + 38, x + 6, y + 44, WOOD_GAP)
    rect(x + w - 6, y + 38, x + w - 2, y + 44, WOOD_GAP)


def chair(cx, y, color="#3c4a78"):
    rect(cx - 7, y, cx + 7, y + 4, "#2a2a3c")      # backrest top
    rect(cx - 8, y + 4, cx + 8, y + 14, color)
    rect(cx - 8, y + 4, cx + 8, y + 6, "#5a6ca0")
    rect(cx - 8, y + 12, cx + 8, y + 14, "#27314f")
    rect(cx - 1, y + 14, cx + 1, y + 17, "#2a2a3c")
    rect(cx - 7, y + 17, cx + 7, y + 18, "#2a2a3c")
    shade(cx - 8, y + 18, cx + 10, y + 22, "#3a2620", 0.25)


def rug(x0, y0, x1, y1, c1="#d94a3a", c2="#f0c860", c3="#cf4030"):
    for y in range(y0, y1):
        for x in range(x0, x1):
            edge = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
            c = c2 if edge in (2, 3) else (c1 if edge > 3 else "#8a2a22")
            if edge > 5 and (((x - x0) // 6) + ((y - y0) // 6)) % 2 == 0:
                c = c3
            if edge < 2 and (x + y) % 2 == 0:
                c = c2
            px(x, y, c)


def sofa(x, y):
    shade(x + 2, y + 24, x + 62, y + 30, "#3a2620", 0.28)
    rect(x, y, x + 60, y + 12, "#2d6a8a")
    rect(x, y, x + 60, y + 2, "#4a8cac")
    rect(x, y + 12, x + 60, y + 24, "#3a7fa0")
    rect(x + 4, y + 12, x + 30, y + 20, "#4a96b8")
    rect(x + 31, y + 12, x + 57, y + 20, "#4a96b8")
    rect(x + 4, y + 12, x + 30, y + 13, "#68b4d0")
    rect(x + 31, y + 12, x + 57, y + 13, "#68b4d0")
    rect(x - 4, y + 4, x + 4, y + 24, "#27607e")
    rect(x + 56, y + 4, x + 64, y + 24, "#27607e")
    rect(x - 4, y + 4, x + 4, y + 6, "#4a8cac")
    rect(x + 56, y + 4, x + 64, y + 6, "#4a8cac")
    rect(x, y + 22, x + 60, y + 24, "#1f4a62")
    rect(x + 8, y + 7, x + 18, y + 14, "#f0c860")


def round_table(cx, cy, r=26):
    shade(cx - r + 2, cy + 4, cx + r + 4, cy + r + 8, "#3a2620", 0.0)
    for yy in range(-r // 2 - 6, r // 2 + 10):
        for xx in range(-r - 2, r + 3):
            top = (xx / (r + 1)) ** 2 + (yy / (r * 0.55)) ** 2 <= 1
            if top:
                c = WOOD[3] if (-xx - yy) > -4 else WOOD[2]
                if (xx / (r - 1)) ** 2 + (yy / (r * 0.55 - 1)) ** 2 > 1:
                    c = "#ecb06c"
                if int(Hh(xx, yy, 70) * 20) == 0:
                    c = WOOD[1]
                px(cx + xx, cy + yy, c)
    for xx in range(-r - 1, r + 2):  # thickness
        e = int((r * 0.55) * (1 - (xx / (r + 1)) ** 2) ** 0.5) if abs(xx) <= r else 0
        for k in range(0, 5):
            px(cx + xx, cy + e + k, WOOD[0] if k < 3 else WOOD_GAP)
    # laptop + papers on table
    rect(cx - 8, cy - 5, cx + 3, cy, "#d8d4e0")
    rect(cx - 7, cy - 4, cx + 2, cy - 1, CYAN[0])
    rect(cx + 8, cy - 4, cx + 15, cy + 1, "#f6ecd2")
    rect(cx - 16, cy + 1, cx - 10, cy + 5, "#ffffff")


def stool(cx, cy):
    rect(cx - 6, cy, cx + 6, cy + 4, "#3c4a78")
    rect(cx - 6, cy, cx + 6, cy + 1, "#5a6ca0")
    rect(cx - 5, cy + 4, cx + 5, cy + 6, "#27314f")
    rect(cx - 1, cy + 6, cx + 1, cy + 10, "#2a2a3c")
    shade(cx - 6, cy + 10, cx + 8, cy + 13, "#3a2620", 0.25)


def bookshelf(x, y):
    w, h = 40, 44
    shade(x + 2, y + h, x + w + 3, y + h + 5, "#3a2620", 0.28)
    rect(x, y, x + w, y + h, TIMBER[2])
    rect(x + 2, y + 2, x + w - 2, y + h - 2, "#4a2c1a")
    cols = ["#d70010", "#009143", "#f0c860", "#5a8cc8", "#f6ecd2", "#b8532d"]
    for sh in range(3):
        yy = y + 3 + sh * 13
        xx = x + 3
        i = 0
        while xx < x + w - 5:
            bw = 2 + int(Hh(sh, i, 80) * 3)
            bh = 7 + int(Hh(sh, i, 81) * 4)
            rect(xx, yy + 11 - bh, xx + bw, yy + 11, cols[int(Hh(sh, i, 82) * 6)])
            px(xx, yy + 11 - bh, "#ffffff")
            xx += bw + 1
            i += 1
        rect(x + 2, yy + 11, x + w - 2, yy + 13, TIMBER[0])
    rect(x, y, x + w, y + 2, TIMBER[0])


def cooler(x, y):
    shade(x - 2, y + 30, x + 18, y + 35, "#3a2620", 0.28)
    rect(x, y + 12, x + 16, y + 32, "#e8e4d8")
    rect(x, y + 12, x + 16, y + 14, "#ffffff")
    rect(x + 14, y + 14, x + 16, y + 32, "#b8b4a8")
    rect(x + 2, y + 18, x + 5, y + 21, "#d70010")
    rect(x + 8, y + 18, x + 11, y + 21, "#42b0c4")
    rect(x + 2, y + 27, x + 14, y + 29, "#9a968a")
    rect(x + 1, y, x + 15, y + 12, "#8fe0e4")
    rect(x + 1, y, x + 15, y + 3, "#c8fbff")
    rect(x + 1, y + 10, x + 15, y + 12, "#42b0c4")
    px(x + 3, y + 4, "#ffffff")
    rect(x + 2, y - 2, x + 14, y, "#6aa8c0")


def printer(x, y):
    shade(x - 2, y + 22, x + 30, y + 27, "#3a2620", 0.28)
    rect(x, y + 8, x + 28, y + 22, "#d8d4e0")
    rect(x, y + 8, x + 28, y + 10, "#f6f2fa")
    rect(x, y + 20, x + 28, y + 22, "#9a96a8")
    rect(x + 4, y + 12, x + 24, y + 15, "#3a3a50")
    rect(x + 19, y + 17, x + 22, y + 19, "#16b05c")
    rect(x + 5, y + 2, x + 23, y + 8, "#ffffff")
    rect(x + 6, y + 4, x + 20, y + 5, "#c8c4d0")


def doormat(x, y):
    rect(x, y, x + 40, y + 12, "#4a3226")
    rect(x + 2, y + 2, x + 38, y + 10, "#6c4a32")
    for xx in range(x + 4, x + 36, 4):
        rect(xx, y + 4, xx + 2, y + 8, "#8a6240")
    shade(x + 2, y + 12, x + 40, y + 15, "#3a2620", 0.25)


def fence(x0, x1, y):
    """Low wooden rail like the ones in the reference, drawn along the front edge."""
    for x in range(x0, x1):
        px(x, y + 8, TIMBER[2])
        px(x, y + 9, WOOD[1])
        px(x, y + 10, WOOD[2])
        px(x, y + 11, WOOD_GAP)
    for x in range(x0, x1, 32):
        rect(x, y, x + 5, y + 16, WOOD[1])
        rect(x, y, x + 5, y + 2, WOOD[3])
        rect(x + 4, y, x + 5, y + 16, WOOD_GAP)


# =============================================================== BUILD ====
def build():
    planks(0, 64, W, H)
    wall()
    checker(208, 64, 272, H)                     # centre aisle
    # planter beds divide the desk zone from the lounge
    planter(16, 210, 112, 218)
    planter(128, 210, 192, 218)
    planter(288, 210, 352, 218)
    planter(368, 210, 464, 218)
    # windows + sun
    for wx in (28, 120, 316, 408):
        window(wx, 12)
    for wx in (28, 120, 316, 408):
        sunbeam(wx + 6, 70, 38, 78)
    sign(240, 12)
    frame_pic(86, 24, 0)
    frame_pic(374, 24, 1)
    # desk rows (6 per side) — facing the viewer, chairs below
    for row, y0 in enumerate((70, 140)):
        for k, x0 in enumerate((16, 80, 144)):
            desk(x0, y0, seed=row * 3 + k)
            chair(x0 + 24, y0 + 40)
        for k, x0 in enumerate((288, 352, 416)):
            desk(x0, y0, seed=10 + row * 3 + k)
            chair(x0 + 24, y0 + 40)
    # bushes + flowers on the planters
    for bx, by, r in ((30, 210, 8), (50, 208, 10), (74, 211, 7), (96, 209, 9),
                      (140, 210, 9), (165, 208, 10), (186, 211, 7),
                      (302, 210, 8), (325, 208, 10), (344, 211, 7),
                      (382, 209, 9), (410, 207, 11), (438, 210, 8), (456, 211, 6)):
        bush(bx, by, r)
    # lounge (bottom-left) and meeting (bottom-right)
    rug(40, 238, 168, 300)
    sofa(62, 246)
    stool(138, 276)
    rug(300, 236, 440, 300, "#3a7fa0", "#f0c860", "#3274a0")
    round_table(370, 264)
    for sx, sy in ((328, 262), (412, 262), (370, 290)):
        stool(sx, sy)
    bookshelf(14, 236)
    cooler(180, 240)
    printer(224 + 52, 232)
    potted_plant(24, 292)
    potted_plant(190, 290)
    potted_plant(456, 292)
    doormat(220, 296)
    fence(0, 208, 304)
    fence(272, W, 304)
    # vignette for depth
    for y in range(H):
        for x in range(W):
            e = min(x, W - 1 - x, y, H - 1 - y)
            if e < 8:
                blend(x, y, "#1c1420", (8 - e) * 0.025)


if __name__ == "__main__":
    build()
    im.convert("RGB").save(OUT / "office-scene.png")
    im.convert("RGB").resize((W * 3, H * 3), Image.NEAREST).save(OUT / "office-scene-x3.png")
    print("ok")
