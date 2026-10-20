"""Gastron office scene (v4) — modern monochrome office, volumetric objects.

White / black / grey palette. Four glass-partitioned departments (LEAD, CREATIVE,
GROWTH, DATA), white desks with dual monitors, PC towers, keyboards, mice, mesh
office chairs, water dispenser and copier. Light comes from the top-left.
Run:  python3 scene_modern.py  ->  office-modern.png (640x368) + office-modern-x3.png
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

W, H = 640, 368
OUT = Path(__file__).parent
im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
d = ImageDraw.Draw(im)


def hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def Hh(x, y, s=0):
    n = ((int(x) * 374761393) + (int(y) * 668265263) + (s * 2246822519) + 1013904223) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFFFFFF) / 4294967296


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        im.putpixel((int(x), int(y)), hx(c) + (255,))


def rect(x0, y0, x1, y1, c):
    if x1 > x0 and y1 > y0:
        d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=hx(c))


def poly(pts, c):
    d.polygon(pts, fill=hx(c))


def blend(x, y, c, a):
    if 0 <= x < W and 0 <= y < H:
        r, g, b, al = im.getpixel((int(x), int(y)))
        if al == 0:
            return
        cr, cg, cb = hx(c)
        im.putpixel((int(x), int(y)), (int(r + (cr - r) * a), int(g + (cg - g) * a), int(b + (cb - b) * a), 255))


def shade(x0, y0, x1, y1, c, a):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            blend(x, y, c, a)


# ------------------------------------------------------------- palette ----
WH = ["#ffffff", "#f2f4f7", "#e1e5ea", "#c8cdd5", "#a6adb8"]   # white ramp (light -> shade)
GR = ["#8c93a0", "#6c7380", "#4c525d", "#363a44", "#262932", "#16181e"]
SC_BG = "#0f1219"
CY = ["#4fd1e8", "#9be8f5", "#d8f8ff"]


# ----------------------------------------------------------- pixel font ---
FONT = {
    "A": [".#.", "#.#", "###", "#.#", "#.#"], "C": ["###", "#..", "#..", "#..", "###"],
    "D": ["##.", "#.#", "#.#", "#.#", "##."], "E": ["###", "#..", "##.", "#..", "###"],
    "G": ["###", "#..", "#.#", "#.#", "###"], "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"], "L": ["#..", "#..", "#..", "#..", "###"],
    "N": ["#..#", "##.#", "####", "#.##", "#..#"], "O": ["###", "#.#", "#.#", "#.#", "###"],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"], "S": ["###", "#..", "###", "..#", "###"],
    "T": ["###", ".#.", ".#.", ".#.", ".#."], "V": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "W": ["#...#", "#...#", "#.#.#", "#.#.#", ".#.#."],
}


def text_w(s, sc):
    return sum((len(FONT[c][0]) + 1) * sc for c in s) - sc


def text(x, y, s, c, sc=1):
    for ch in s:
        g = FONT[ch]
        for r, row in enumerate(g):
            for k, v in enumerate(row):
                if v == "#":
                    rect(x + k * sc, y + r * sc, x + (k + 1) * sc, y + (r + 1) * sc, c)
        x += (len(g[0]) + 1) * sc


# ============================================== DEPTH: shadows + rim light ===
SHADOW_C = np.array([28, 32, 44], float)


def _shift(m, dx, dy):
    out = np.zeros_like(m)
    out[dy:, dx:] = m[: H - dy, : W - dx]
    return out


def obj(fn, *a, L=5, rim=True, **k):
    """Draw fn on its own layer, cast a soft shadow (light from top-left), add rim
    light on lit edges and underside shading, then composite onto the scene."""
    global im, d
    base, bd = im, d
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im, d = layer, ImageDraw.Draw(layer)
    fn(*a, **k)
    im, d = base, bd
    arr = np.array(layer).astype(float)
    m = arr[..., 3] > 0
    out = np.array(base).astype(float)
    alpha = np.zeros((H, W))
    if L > 0:
        near = np.zeros_like(m)
        far = np.zeros_like(m)
        for kk in range(1, L + 1):
            sh = _shift(m, kk, int(round(kk * 0.65)))
            if kk <= max(1, L // 2):
                near |= sh
            else:
                far |= sh
        alpha[far] = 0.22
        alpha[near] = 0.34
        alpha[_shift(m, 1, 2) | _shift(m, 0, 1) | _shift(m, 2, 1)] = 0.50
    alpha[m] = 0
    out[..., :3] = out[..., :3] * (1 - alpha[..., None]) + SHADOW_C * alpha[..., None]
    if rim:
        up = ~_shift(m, 0, 1)
        left = ~_shift(m, 1, 0)
        dn = ~np.roll(m, -1, axis=0)
        rt = ~np.roll(m, -1, axis=1)
        lit = m & (up | left)
        dark = m & (dn | rt) & ~lit
        arr[lit, :3] = arr[lit, :3] + (255 - arr[lit, :3]) * 0.30
        arr[dark, :3] = arr[dark, :3] * 0.78 + SHADOW_C * 0.22
    out[m, :3] = arr[m, :3]
    out[..., 3] = 255
    base.paste(Image.fromarray(out.astype(np.uint8)), (0, 0))


# --------------------------------------------------------------- floor ----
def floor():
    for y in range(72, H):
        for x in range(W):
            tx, ty = x // 32, (y - 72) // 32
            c = "#d9dce2" if (tx + ty) % 2 == 0 else "#d2d6dd"
            if x % 32 == 0 or (y - 72) % 32 == 0:
                c = "#bfc3cc"
            elif x % 32 == 1 or (y - 72) % 32 == 1:
                c = "#e6e8ec"
            elif Hh(x, y, 1) < 0.015:
                c = "#c6cad3"
            px(x, y, c)
    # glossy ceiling-light reflections
    for gx in (96, 224, 416, 544):
        for gy in (96, 228):
            for yy in range(0, 26):
                for xx in range(0, 60):
                    a = 0.10 * (1 - abs(xx - 30) / 30) * (1 - yy / 26)
                    blend(gx + xx + yy // 2, gy + yy, "#ffffff", max(0, a))


def carpet(x0, y0, x1, y1, base, alt):
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = base if ((x - x0) // 12 + (y - y0) // 12) % 2 == 0 else alt
            if (x - x0) % 12 == 0 or (y - y0) % 12 == 0:
                c = alt
            if Hh(x, y, 2) < 0.12:
                r, g, b = hx(c)
                c = "#%02x%02x%02x" % (min(255, r + 6), min(255, g + 6), min(255, b + 7))
            px(x, y, c)
    for k, a in ((0, 0.35), (1, 0.18)):  # inset border shadow
        for x in range(x0, x1):
            blend(x, y0 + k, "#2a2e38", a)
        for y in range(y0, y1):
            blend(x0 + k, y, "#2a2e38", a)


def aisle(x0, x1):
    for y in range(72, H):
        for x in range(x0, x1):
            ty = (y - 72) // 32
            c = "#a9aeb8" if ((x // 32) + ty) % 2 == 0 else "#a3a8b2"
            if x % 32 == 0 or (y - 72) % 32 == 0:
                c = "#9096a2"
            elif Hh(x, y, 3) < 0.02:
                c = "#b4b9c2"
            px(x, y, c)
    for x in (x0 + 5, x1 - 6):  # guide lines
        rect(x, 72, x + 1, H, "#f2f4f7")
    for y in range(90, H - 14, 46):  # chevrons
        cx = (x0 + x1) // 2
        for k in range(5):
            px(cx - k, y + k, "#f2f4f7")
            px(cx + k, y + k, "#f2f4f7")
            px(cx - k, y + k + 1, "#8c93a0")
            px(cx + k, y + k + 1, "#8c93a0")


# ---------------------------------------------------------------- wall ----
def wall():
    for y in range(0, 66):
        for x in range(W):
            t = y / 66
            r = int(238 - 12 * t)
            c = (r, r + 2, r + 5)
            if x % 80 == 0:
                c = (196, 200, 208)
            elif x % 80 == 1:
                c = (250, 251, 253)
            if y < 3:
                c = (60, 64, 74) if y > 0 else (96, 100, 110)
            px(x, y, "#%02x%02x%02x" % c)
    rect(0, 66, W, 72, GR[3])      # baseboard
    rect(0, 66, W, 67, GR[1])
    rect(0, 71, W, 72, GR[5])
    shade(0, 72, W, 79, "#1c2030", 0.26)
    shade(0, 79, W, 85, "#1c2030", 0.10)


def window(x, y, w=64, h=36):
    rect(x - 3, y - 3, x + w + 3, y + h + 4, GR[4])
    rect(x - 2, y - 2, x + w + 2, y + h + 3, GR[2])
    for yy in range(h):
        t = yy / h
        c = (int(150 + 70 * t), int(172 + 62 * t), int(194 + 52 * t))
        for xx in range(w):
            px(x + xx, y + yy, "#%02x%02x%02x" % c)
    # distant city silhouettes
    for layer, (col, base) in enumerate((("#7f8c9c", 0.55), ("#5b6777", 0.72))):
        xx = 0
        while xx < w:
            bw = 5 + int(Hh(xx, layer, 5) * 8)
            bh = int(h * (1 - base) * (0.5 + Hh(xx, layer, 6) * 0.9)) + 4
            rect(x + xx, y + h - bh, x + min(w, xx + bw), y + h, col)
            for wy in range(y + h - bh + 2, y + h - 2, 4):
                for wx in range(x + xx + 1, x + min(w, xx + bw) - 1, 3):
                    if Hh(wx, wy, 7) < 0.35:
                        px(wx, wy, "#e6eef8" if layer else "#b6c2d0")
            xx += bw + 1
    rect(x + w // 3, y, x + w // 3 + 1, y + h, GR[2])
    rect(x + 2 * w // 3, y, x + 2 * w // 3 + 1, y + h, GR[2])
    for k in range(8):  # glare
        for j in range(3):
            blend(x + 6 + k * 2 + j, y + h - 4 - k * 3, "#ffffff", 0.45)
    rect(x - 4, y + h + 4, x + w + 4, y + h + 7, WH[2])
    rect(x - 4, y + h + 4, x + w + 4, y + h + 5, WH[0])
    rect(x - 4, y + h + 6, x + w + 4, y + h + 7, WH[4])
    shade(x - 2, y + h + 7, x + w + 6, y + h + 12, "#1c2030", 0.18)


def logo_plaque(cx, y):
    w, h = 150, 32
    x = cx - w // 2
    shade(x + 3, y + 4, x + w + 4, y + h + 6, "#1c2030", 0.30)
    rect(x, y, x + w, y + h, GR[5])
    rect(x, y, x + w, y + 1, GR[1])
    rect(x, y, x + 1, y + h, GR[2])
    rect(x + w - 1, y, x + w, y + h, GR[4])
    rect(x, y + h - 1, x + w, y + h, GR[4])
    rect(x + 6, y + 6, x + 26, y + 26, "#d70010")  # Gastron red tile
    rect(x + 6, y + 6, x + 26, y + 8, "#f03a48")
    fl = ["..#..", ".###.", "#####", "#####", ".###."]
    for r, row in enumerate(fl):
        for k, v in enumerate(row):
            if v == "#":
                rect(x + 11 + k * 2, y + 10 + r * 3, x + 13 + k * 2, y + 13 + r * 3, "#ffffff" if r > 2 else "#ffd9dc")
    text(x + 34, y + 11, "GASTRON", "#ffffff", 2)


def wall_clock(cx, cy):
    r = 9
    shade(cx - r + 2, cy - r + 3, cx + r + 3, cy + r + 4, "#1c2030", 0.28)
    for yy in range(-r, r + 1):
        for xx in range(-r, r + 1):
            dd = xx * xx + yy * yy
            if dd <= r * r:
                px(cx + xx, cy + yy, GR[4] if dd > (r - 1) ** 2 else WH[1] if -xx - yy > -4 else WH[2])
    for k in range(12):
        import math
        ax, ay = cx + int(round(math.sin(k * math.pi / 6) * 6.5)), cy - int(round(math.cos(k * math.pi / 6) * 6.5))
        px(ax, ay, GR[3])
    for k in range(5):
        px(cx, cy - k, GR[5])
    for k in range(4):
        px(cx + k, cy + k // 2, GR[5])
    px(cx, cy, "#d70010")


# ----------------------------------------------------------- furniture ----
def keyboard(x, y):
    rect(x, y, x + 20, y + 6, WH[1])
    rect(x, y, x + 20, y + 1, WH[0])
    rect(x, y + 5, x + 20, y + 6, WH[4])
    for ry in (1, 3):
        for kx in range(1, 19, 2):
            px(x + kx, y + ry, WH[3])
            px(x + kx, y + ry + 1, WH[2])
    rect(x + 5, y + 4, x + 14, y + 5, WH[3])


def mouse(x, y):
    rect(x - 2, y - 1, x + 9, y + 9, GR[3])     # pad
    rect(x - 2, y - 1, x + 9, y, GR[1])
    rect(x + 2, y + 1, x + 6, y + 7, WH[0])
    rect(x + 2, y + 1, x + 3, y + 7, WH[2])
    rect(x + 5, y + 1, x + 6, y + 7, WH[4])
    px(x + 4, y + 2, GR[1])
    px(x + 4, y + 3, GR[1])


def monitor(x, y, seed):
    w, h = 25, 17
    rect(x, y, x + w, y + h, GR[5])
    rect(x, y, x + w, y + 1, GR[2])
    rect(x, y, x + 1, y + h, GR[3])
    rect(x + 1, y + 1, x + w - 1, y + h - 3, SC_BG)
    # UI: title bar, sidebar, bars, text lines
    rect(x + 1, y + 1, x + w - 1, y + 3, "#1e2430")
    px(x + 3, y + 2, "#ff6b6b")
    px(x + 5, y + 2, "#ffd24a")
    px(x + 7, y + 2, "#4fd18b")
    rect(x + 2, y + 4, x + 7, y + h - 4, "#171c27")
    for r in range(3):
        rect(x + 3, y + 5 + r * 3, x + 6, y + 6 + r * 3, "#3a4558")
    for r in range(3):
        wl = 5 + int(Hh(seed, r, 9) * 8)
        rect(x + 9, y + 5 + r * 3, x + 9 + wl, y + 6 + r * 3, "#9aa6ba" if r else CY[1])
    for i in range(4):
        bh = 2 + int(Hh(seed, i, 10) * 5)
        rect(x + 15 + i * 2, y + h - 4 - bh, x + 16 + i * 2, y + h - 4, CY[0])
    shade(x + 1, y + 1, x + w - 1, y + h - 3, "#4fd1e8", 0.07)
    for k in range(5):
        px(x + 2 + k, y + 4 + (k > 2), "#ffffff") if False else None
    # chin + stand
    px(x + w // 2, y + h - 2, GR[1])
    rect(x + 10, y + h, x + 15, y + h + 4, GR[3])
    rect(x + 10, y + h, x + 11, y + h + 4, GR[1])
    rect(x + 6, y + h + 4, x + 19, y + h + 6, GR[2])
    rect(x + 6, y + h + 4, x + 19, y + h + 5, GR[0])


def pc_tower(x, y):
    w, h = 13, 28
    rect(x, y, x + w, y + h, GR[4])
    rect(x, y, x + w, y + 2, GR[2])
    rect(x, y, x + 2, y + h, GR[3])
    rect(x + 2, y + 2, x + w - 2, y + h - 2, GR[5])     # front panel
    for vy in range(y + 11, y + h - 5, 2):              # vents
        rect(x + 3, vy, x + w - 3, vy + 1, GR[3])
    rect(x + 3, y + 4, x + w - 3, y + 7, GR[3])         # optical bay
    rect(x + 3, y + 5, x + w - 3, y + 6, GR[1])
    for r in range(-2, 3):                              # power button
        for c in range(-2, 3):
            if r * r + c * c <= 5:
                px(x + 6 + c, y + h - 5 + r, GR[1] if r * r + c * c > 2 else CY[1])
    rect(x + 3, y + 8, x + 5, y + 9, GR[0])
    rect(x + 7, y + 8, x + 9, y + 9, GR[0])
    rect(x + 1, y + 3, x + 2, y + h - 3, CY[0])         # RGB strip
    shade(x, y, x + 2, y + h, "#4fd1e8", 0.0)
    rect(x, y + h - 1, x + w, y + h, GR[5])
    rect(x + 1, y + h, x + 3, y + h + 2, GR[5])
    rect(x + w - 3, y + h, x + w - 1, y + h + 2, GR[5])


def desk(x, y, seed):
    """56-wide white desk. (x, y) = top of the monitors."""
    w = 56
    # under-desk shadow cavity
    rect(x + 3, y + 36, x + w - 3, y + 54, GR[0])
    shade(x + 3, y + 36, x + w - 3, y + 54, "#10121a", 0.38)
    # back edge + desk top (lit surface, gets a soft gradient)
    for yy in range(y + 21, y + 32):
        t = (yy - y - 21) / 11
        c = WH[0] if t < 0.3 else WH[1] if t < 0.7 else WH[2]
        rect(x, yy, x + w, yy + 1, c)
    rect(x, y + 20, x + w, y + 21, WH[3])
    rect(x, y + 32, x + w, y + 34, WH[1])     # front edge thickness
    rect(x, y + 32, x + w, y + 33, WH[0])
    rect(x, y + 34, x + w, y + 35, WH[4])
    rect(x + w, y + 22, x + w + 3, y + 36, WH[4])   # right side face
    rect(x + w, y + 22, x + w + 1, y + 36, WH[3])
    # drawer pedestal (left)
    rect(x + 3, y + 35, x + 21, y + 54, WH[1])
    rect(x + 3, y + 35, x + 4, y + 54, WH[0])
    rect(x + 20, y + 35, x + 21, y + 54, WH[3])
    for i, dy in enumerate((37, 43, 49)):
        rect(x + 5, y + dy, x + 19, y + dy + 5, WH[2])
        rect(x + 5, y + dy, x + 19, y + dy + 1, WH[0])
        rect(x + 5, y + dy + 5, x + 19, y + dy + 6, WH[4])
        rect(x + 10, y + dy + 2, x + 14, y + dy + 3, GR[2])
        px(x + 10, y + dy + 2, GR[0])
    # right leg panel + modesty panel
    rect(x + w - 6, y + 35, x + w - 3, y + 54, WH[2])
    rect(x + w - 6, y + 35, x + w - 5, y + 54, WH[0])
    rect(x + 22, y + 36, x + w - 6, y + 44, WH[2])
    rect(x + 22, y + 36, x + w - 6, y + 37, WH[4])
    rect(x + 22, y + 44, x + w - 6, y + 45, GR[1])
    # monitors (dual) + peripherals + clutter
    monitor(x + 2, y, seed)
    monitor(x + 29, y, seed + 1)
    keyboard(x + 10, y + 25)
    mouse(x + 36, y + 24)
    rect(x + 49, y + 23, x + 53, y + 29, WH[0])   # mug
    rect(x + 49, y + 23, x + 53, y + 24, WH[3])
    rect(x + 52, y + 25, x + 54, y + 27, WH[3])
    rect(x + 3, y + 25, x + 8, y + 30, "#fbf6c8")  # sticky/paper
    rect(x + 3, y + 25, x + 8, y + 26, "#e8d870")
    # floor-standing PC case beside the desk
    pc_tower(x + w + 5, y + 27)


def chair(cx, y):
    """Mesh office chair seen from behind (back to viewer)."""
    # headrest
    rect(cx - 6, y - 4, cx + 6, y, GR[3])
    rect(cx - 6, y - 4, cx + 6, y - 3, GR[1])
    # backrest
    for yy in range(y, y + 22):
        inset = 1 if yy in (y, y + 21) else 0
        for xx in range(cx - 12 + inset, cx + 12 - inset):
            c = GR[4] if (xx + yy) % 2 == 0 else GR[3]
            if yy > y + 12 and abs(xx - cx) < 6:
                c = GR[3] if (xx + yy) % 2 == 0 else GR[2]   # lumbar support
            px(xx, yy, c)
    rect(cx - 12, y, cx - 11, y + 22, GR[1])           # frame lit side
    rect(cx + 11, y, cx + 12, y + 22, GR[5])
    rect(cx - 12, y, cx + 12, y + 1, GR[1])
    rect(cx - 12, y + 21, cx + 12, y + 22, GR[5])
    # armrests + seat edge
    for sx in (-1, 1):
        ax = cx + sx * 14
        rect(ax - 2, y + 11, ax + 2, y + 13, GR[5])
        rect(ax - 1, y + 13, ax + 1, y + 21, GR[3])
        rect(ax - 3, y + 9, ax + 3, y + 11, GR[2])
        rect(ax - 3, y + 9, ax + 3, y + 10, GR[0])
    rect(cx - 11, y + 22, cx + 11, y + 28, GR[2])
    rect(cx - 11, y + 22, cx + 11, y + 23, GR[0])
    rect(cx - 11, y + 27, cx + 11, y + 28, GR[5])
    # gas lift + five-star base with casters
    rect(cx - 1, y + 28, cx + 2, y + 33, GR[0])
    rect(cx - 12, y + 33, cx + 12, y + 35, GR[4])
    rect(cx - 12, y + 33, cx + 12, y + 34, GR[2])
    for ax in (cx - 12, cx - 5, cx + 5, cx + 11):
        rect(ax, y + 35, ax + 2, y + 38, GR[5])
        px(ax, y + 37, GR[3])


def water_dispenser(x, y):
    w = 22
    # bottle
    for yy in range(0, 15):
        inset = 3 if yy < 3 else 1 if yy < 5 else 0
        for xx in range(inset, w - inset):
            c = "#cfe7f4"
            if xx < inset + 3:
                c = "#f2fbff"
            elif xx > w - inset - 4:
                c = "#9fcbe3"
            if yy > 4:
                c = "#8ec6e6" if xx > inset + 3 else "#b8e0f2"
            px(x + xx, y + yy, c)
    rect(x + 8, y - 2, x + 14, y, GR[3])
    rect(x + 5, y + 4, x + w - 5, y + 5, "#e8f6fd")
    # body
    rect(x, y + 15, x + w, y + 50, WH[1])
    rect(x, y + 15, x + 2, y + 50, WH[0])
    rect(x + w - 3, y + 15, x + w, y + 50, WH[3])
    rect(x + w, y + 17, x + w + 3, y + 52, WH[4])      # side face
    rect(x, y + 15, x + w, y + 17, WH[0])
    rect(x + 3, y + 20, x + w - 3, y + 34, GR[4])       # dark control panel
    rect(x + 3, y + 20, x + w - 3, y + 21, GR[1])
    rect(x + 6, y + 24, x + 10, y + 27, "#4a9de0")      # cold tap
    rect(x + 12, y + 24, x + 16, y + 27, "#e0524a")     # hot tap
    rect(x + 6, y + 24, x + 10, y + 25, "#8cc4f2")
    rect(x + 12, y + 24, x + 16, y + 25, "#f0968f")
    px(x + 5, y + 30, CY[0])
    px(x + 17, y + 30, "#e0524a")
    rect(x + 4, y + 36, x + w - 4, y + 38, GR[3])       # cup spot
    rect(x + 3, y + 40, x + w - 3, y + 46, GR[3])       # drip tray grille
    for gx in range(x + 4, x + w - 4, 2):
        rect(gx, y + 41, gx + 1, y + 45, GR[5])
    rect(x + 1, y + 48, x + w - 1, y + 50, GR[2])


def copier(x, y):
    w = 34
    rect(x + 4, y - 3, x + 20, y + 1, "#ffffff")        # paper on output tray
    rect(x + 4, y - 3, x + 20, y - 2, WH[3])
    rect(x, y + 1, x + w, y + 9, WH[0])                  # lit top face
    rect(x, y + 1, x + w, y + 2, "#ffffff")
    rect(x, y + 9, x + w, y + 11, WH[2])
    rect(x, y + 11, x + w, y + 32, WH[1])                # front
    rect(x, y + 11, x + 2, y + 32, WH[0])
    rect(x + w - 3, y + 11, x + w, y + 32, WH[3])
    rect(x + w, y + 3, x + w + 3, y + 34, WH[4])
    rect(x + 20, y + 13, x + 31, y + 19, GR[5])          # control panel
    rect(x + 21, y + 14, x + 26, y + 17, CY[0])
    px(x + 28, y + 15, "#4fd18b")
    px(x + 29, y + 15, "#ffd24a")
    rect(x + 3, y + 13, x + 17, y + 17, GR[4])           # scan slot
    for i, dy in enumerate((20, 25)):
        rect(x + 2, y + dy, x + w - 2, y + dy + 4, WH[2])
        rect(x + 2, y + dy, x + w - 2, y + dy + 1, WH[0])
        rect(x + 2, y + dy + 4, x + w - 2, y + dy + 5, WH[4])
        rect(x + 14, y + dy + 2, x + 20, y + dy + 3, GR[2])
    rect(x + 1, y + 30, x + w - 1, y + 32, GR[2])


def bin_(x, y, c):
    rect(x, y, x + 12, y + 18, GR[2] if c == "g" else GR[5] if c == "k" else WH[2])
    rect(x, y, x + 12, y + 3, GR[4] if c != "w" else WH[4])
    rect(x + 2, y + 1, x + 10, y + 2, GR[5] if c != "w" else GR[1])
    rect(x, y + 3, x + 2, y + 18, GR[1] if c == "g" else GR[3] if c == "k" else WH[0])
    rect(x + 10, y + 3, x + 12, y + 18, GR[4] if c == "g" else GR[5] if c == "k" else WH[4])
    rect(x + 4, y + 8, x + 8, y + 12, "#4fd18b" if c == "g" else "#4a9de0" if c == "w" else "#ffd24a")
    rect(x, y + 17, x + 12, y + 18, GR[5])


def dept_sign(x, y, label):
    w = text_w(label, 1) + 12
    shade(x + 2, y + 3, x + w + 3, y + 14, "#1c2030", 0.22)
    rect(x, y, x + w, y + 11, GR[5])
    rect(x, y, x + w, y + 1, GR[1])
    rect(x + 3, y + 3, x + 5, y + 8, "#ffffff")
    text(x + 8, y + 3, label, "#ffffff", 1)


# --------------------------------------------------------- glass walls ----
def glass_shadow_h(x0, x1, y):
    shade(x0 + 2, y + 14, x1 + 3, y + 20, "#1c2030", 0.16)


def glass_h(x0, x1, y, h=14, gaps=()):
    spans, cur = [], x0
    for g0, g1 in sorted(gaps):
        spans.append((cur, g0))
        cur = g1
    spans.append((cur, x1))
    for a, b in spans:
        if b <= a:
            continue
        shade(a, y + 2, b, y + h - 2, "#9fc3d8", 0.22)       # tinted glass
        for gx in range(a + 6, b, 38):                          # diagonal reflections
            for k in range(h - 4):
                blend(gx + (h - 4 - k) // 2, y + 2 + k, "#ffffff", 0.34)
                blend(gx + 1 + (h - 4 - k) // 2, y + 2 + k, "#ffffff", 0.20)
        rect(a, y, b, y + 2, WH[2])                             # top rail
        rect(a, y, b, y + 1, WH[0])
        rect(a, y + h - 2, b, y + h, GR[1])                     # bottom rail
        rect(a, y + h - 1, b, y + h, GR[3])
    for a, b in spans:                                          # posts at span ends + every 62px
        for px_ in sorted({a, b - 3, *range(a + 62, b - 3, 62)}):
            rect(px_, y, px_ + 3, y + h, WH[2])
            rect(px_, y, px_ + 1, y + h, WH[0])
            rect(px_ + 2, y, px_ + 3, y + h, GR[0])


def glass_v(x, y0, y1, gaps=()):
    spans, cur = [], y0
    for g0, g1 in sorted(gaps):
        spans.append((cur, g0))
        cur = g1
    spans.append((cur, y1))
    for a, b in spans:
        if b <= a:
            continue
        shade(x, a, x + 5, b, "#9fc3d8", 0.30)
        rect(x, a, x + 1, b, WH[0])
        rect(x + 4, a, x + 5, b, GR[1])
        for k in range(a + 4, b - 6, 26):
            blend(x + 2, k, "#ffffff", 0.6)
            blend(x + 2, k + 1, "#ffffff", 0.6)
            blend(x + 2, k + 2, "#ffffff", 0.4)
        rect(x - 1, a, x + 6, a + 3, WH[1])                     # end posts
        rect(x - 1, a, x + 6, a + 1, WH[0])
        rect(x - 1, b - 3, x + 6, b, WH[3])
        rect(x - 1, b - 1, x + 6, b, GR[1])


# =============================================================== BUILD ====
ZONES = {
    "LEAD": (24, 90, 272, 210, "#b4bac4", "#aab0bb"),
    "CREATIVE": (368, 90, 616, 210, "#c2c7cf", "#b8bec7"),
    "GROWTH": (24, 228, 272, 348, "#bdc2cb", "#b3b9c3"),
    "DATA": (368, 228, 616, 348, "#b0b6c1", "#a6adb8"),
}


def build():
    floor()
    wall()
    aisle(272, 368)
    for name, (x0, y0, x1, y1, a, b) in ZONES.items():
        carpet(x0, y0, x1, y1, a, b)
    # wall dressing
    for wx in (28, 124, 412, 508):
        window(wx, 14)
    shade(0, 0, 0, 0, "#000000", 0)
    logo_plaque(320, 16)
    wall_clock(320, 56) if False else None
    # glass-wall shadows on the floor (under the glass, before furniture)
    for name, (x0, y0, x1, y1, a, b) in ZONES.items():
        glass_shadow_h(x0, x1, y0)
        glass_shadow_h(x0, x1, y1 - 14)
        shade(x0 + 5, y0, x0 + 9, y1, "#1c2030", 0.14)
        shade(x1 - 0, y0, x1 + 4, y1, "#1c2030", 0.14)
    # departments: 3 desk units + chairs each
    for name, (x0, y0, x1, y1, a, b) in ZONES.items():
        for i in range(3):
            dx = x0 + 12 + i * 77
            dy = y0 + 26
            obj(desk, dx, dy, i + len(name), L=11)
            obj(chair, dx + 28, dy + 38, L=8)
    # shared amenities in the aisle
    obj(water_dispenser, 284, 94, L=13)
    obj(copier, 322, 106, L=9)
    for i, c in enumerate("gkw"):
        obj(bin_, 292 + i * 16, 300, c, L=5)
    # glass partitions + department labels drawn last (transparent over furniture)
    for name, (x0, y0, x1, y1, a, b) in ZONES.items():
        glass_h(x0, x1, y0, gaps=())
        glass_h(x0, x1, y1 - 14, gaps=((x1 - 70, x1 - 30),) if x0 < 300 else ((x0 + 30, x0 + 70),))
        glass_v(x0, y0, y1)
        if x0 < 300:
            glass_v(x1 - 5, y0, y1, gaps=((y0 + 36, y0 + 84),))
        else:
            glass_v(x0, y0, y1, gaps=((y0 + 36, y0 + 84),))
            glass_v(x1 - 5, y0, y1)
        dept_sign(x0 + 14, y0 + 3, name)
    # global light: bright top-left, softer bottom-right; edge vignette
    arr = np.array(im).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    t = xx / W * 0.55 + yy / H * 0.45
    arr[..., :3] *= (1.05 - 0.13 * t)[..., None]
    e = np.minimum.reduce([xx, W - 1 - xx, yy, H - 1 - yy])
    arr[..., :3] *= (1 - np.clip((10 - e) / 10, 0, 1) * 0.20)[..., None]
    im.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)), (0, 0))


if __name__ == "__main__":
    build()
    im.convert("RGB").save(OUT / "office-modern.png")
    im.convert("RGB").resize((W * 3, H * 3), Image.NEAREST).save(OUT / "office-modern-x3.png")
    print("ok", W, H)
