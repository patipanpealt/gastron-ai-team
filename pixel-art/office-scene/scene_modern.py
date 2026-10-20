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
        im.putpixel((int(x), int(y)), (hx(c) if isinstance(c, str) else tuple(c)) + (255,))


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


# ------------------------------------------------- rounded shapes + gradients
def mix(a, b, t):
    a = hx(a) if isinstance(a, str) else a
    b = hx(b) if isinstance(b, str) else b
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vg(top, bot):
    """vertical gradient colour function"""
    return lambda x, y, u, v: mix(top, bot, v)


def cyl(light, mid, dark, hl=0.2):
    """cylinder-style horizontal shading: lit left, soft middle, shaded right"""
    def f(x, y, u, v):
        if u < 0.28:
            c = mix(light, mid, u / 0.28)
        elif u < 0.66:
            c = mid if isinstance(mid, tuple) else hx(mid)
        else:
            c = mix(mid, dark, (u - 0.66) / 0.34)
        return mix(c, (255, 255, 255), hl * (1 - v) * 0.5) if hl else c
    return f


def shp(x0, y0, x1, y1, col, r=2, rt=None, rb=None):
    """Rounded rectangle filled by col(x, y, u, v). r = all corners, rt/rb = top/bottom radii."""
    rt = r if rt is None else rt
    rb = r if rb is None else rb
    cw, ch = max(1, x1 - x0 - 1), max(1, y1 - y0 - 1)
    for y in range(y0, y1):
        for x in range(x0, x1):
            rr = rt if y < y0 + rt else rb if y >= y1 - rb else 0
            if rr:
                dx = (x0 + rr - x - 0.5) if x < x0 + rr else (x - (x1 - rr) + 0.5) if x >= x1 - rr else 0
                dy = (y0 + rt - y - 0.5) if y < y0 + rt else (y - (y1 - rb) + 0.5)
                if dx > 0 and dy > 0 and dx * dx + dy * dy > rr * rr:
                    continue
            c = col(x, y, (x - x0) / cw, (y - y0) / ch) if callable(col) else col
            px(x, y, c)


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
            c = "#dadde3" if (tx + ty) % 2 == 0 else "#d5d9df"
            if x % 32 == 0 or (y - 72) % 32 == 0:
                c = "#c9cdd5"
            elif x % 32 == 1 or (y - 72) % 32 == 1:
                c = "#e4e6ea"
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
    def f(x, y, u, v):
        c = base if ((x - x0) // 12 + (y - y0) // 12) % 2 == 0 else alt
        if (x - x0) % 12 == 0 or (y - y0) % 12 == 0:
            c = alt
        if Hh(x, y, 2) < 0.12:
            r, g, b = hx(c)
            c = "#%02x%02x%02x" % (min(255, r + 6), min(255, g + 6), min(255, b + 7))
        ed = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
        if ed < 2:
            return mix(c, "#2a2e38", 0.34 if ed == 0 else 0.16)
        return c
    shp(x0, y0, x1, y1, f, 7)


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
    shp(x, y, x + w, y + h, vg(GR[3], GR[5]), 5)
    shp(x + 6, y + 6, x + 26, y + 26, vg("#f03a48", "#b80010"), 4)   # Gastron red tile
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
# Everyday-office look: single monitor, plain black mid-tower, mesh task chair.
# All volumes are rounded (shp) and shaded like cylinders (cyl) instead of flat boxes.

def keyboard(x, y):
    shp(x, y, x + 22, y + 6, vg(WH[0], WH[3]), 2)
    rect(x + 2, y + 5, x + 20, y + 6, WH[4])
    for ry in (1, 3):
        for kx in range(2, 20, 2):
            px(x + kx, y + ry, WH[3])
            px(x + kx, y + ry + 1, WH[2])
    rect(x + 6, y + 4, x + 16, y + 5, WH[3])


def mouse(x, y):
    shp(x - 3, y - 1, x + 9, y + 9, vg(GR[3], GR[4]), 3)            # pad
    shp(x + 1, y + 1, x + 6, y + 8, cyl(WH[0], WH[1], WH[4]), 2)    # mouse
    px(x + 3, y + 2, GR[1])
    px(x + 3, y + 3, GR[1])
    px(x + 3, y + 8, GR[4])


def monitor(x, y, seed):
    """Plain 22-inch office monitor, light-theme desktop on screen."""
    w, h = 34, 22
    shp(x, y, x + w, y + h, cyl(GR[3], GR[4], GR[5], 0.18), 3, 3, 3)           # bezel
    shp(x + 2, y + 2, x + w - 2, y + h - 4, desktop(seed), 1)                   # screen
    # glass glare
    for k in range(9):
        for j in range(3):
            blend(x + 6 + k + j, y + 3 + (8 - k), "#ffffff", 0.22)
    px(x + w // 2, y + h - 2, GR[1])                                              # power LED / logo
    # neck + oval base
    shp(x + 14, y + h - 1, x + 20, y + h + 4, cyl(GR[1], GR[3], GR[5]), 1)
    shp(x + 9, y + h + 3, x + 25, y + h + 6, cyl(GR[1], GR[3], GR[5]), 2)
    rect(x + 11, y + h + 3, x + 22, y + h + 4, GR[0])


def desktop(seed):
    def f(x, y, u, v):
        if v > 0.88:                                       # taskbar
            return mix(GR[4], GR[5], 0.5) if abs(u - 0.5) > 0.2 else mix(GR[3], GR[4], 0.4)
        base = mix("#7aa3c6", "#c2d7e8", v)               # calm blue wallpaper
        # a document window
        if 0.14 < u < 0.86 and 0.14 < v < 0.8:
            if v < 0.26:
                return mix("#d6dbe3", "#aab2bf", (v - 0.14) / 0.12)   # title bar
            if u < 0.34:
                return "#e6eaf0"                                       # side list
            if int(v * 24) % 3 == 1 and u < 0.34 + 0.15 + 0.4 * Hh(int(v * 24), seed, 3):
                return "#aeb6c4"                                       # text lines
            return "#fbfcfe"
        return base
    return f


def pc_tower(x, y):
    w, h = 14, 28
    shp(x, y, x + w, y + h, cyl(GR[2], GR[4], GR[5], 0.22), 3, 3, 1)
    shp(x + 3, y + 3, x + w - 2, y + h - 2, cyl(GR[4], GR[5], GR[5], 0.2), 1)   # front panel
    rect(x + 4, y + 4, x + w - 3, y + 6, GR[3])                                  # optical bay
    rect(x + 4, y + 5, x + w - 3, y + 6, GR[1])
    for vy in range(y + 11, y + h - 6, 2):
        for vx in range(x + 4, x + w - 3):
            if (vx + vy) % 2 == 0:
                px(vx, vy, GR[3])
    shp(x + 5, y + h - 6, x + 10, y + h - 2, cyl(GR[0], GR[1], GR[3]), 2)        # round power button
    px(x + 7, y + h - 5, WH[1])
    px(x + 10, y + 8, "#4fd18b")
    rect(x + 1, y + 2, x + 2, y + h - 3, GR[1])                                   # lit left edge
    shp(x + 2, y + h, x + 4, y + h + 2, vg(GR[4], GR[5]), 1)
    shp(x + w - 4, y + h, x + w - 2, y + h + 2, vg(GR[4], GR[5]), 1)


def desk(x, y, seed):
    """56-wide white laminate desk with rounded corners. (x, y) = top of the monitor."""
    w = 56
    # shadowed knee space
    shp(x + 3, y + 34, x + w - 3, y + 54, vg(mix(GR[0], "#000000", 0.35), mix(GR[0], "#000000", 0.15)), 2)
    # worktop: rounded surface + thick front edge + side face
    shp(x, y + 20, x + w, y + 34, vg(WH[0], WH[2]), 4, 4, 2)
    rect(x + 2, y + 21, x + w - 2, y + 22, WH[0])                       # specular line on the far edge
    shp(x, y + 31, x + w, y + 36, vg(WH[1], WH[4]), 1, 1, 3)           # front edge thickness
    rect(x + 2, y + 31, x + w - 2, y + 32, WH[0])
    poly([(x + w, y + 24), (x + w + 3, y + 26), (x + w + 3, y + 36), (x + w, y + 35)], WH[3])
    # drawer pedestal (left) with pill handles
    shp(x + 3, y + 35, x + 22, y + 54, cyl(WH[0], WH[1], WH[3], 0.2), 1, 1, 3)
    for dy in (37, 43, 49):
        shp(x + 5, y + dy, x + 20, y + dy + 5, vg(WH[1], WH[3]), 1)
        rect(x + 6, y + dy, x + 19, y + dy + 1, WH[0])
        shp(x + 9, y + dy + 2, x + 16, y + dy + 4, vg(GR[1], GR[3]), 1)
    # right leg + modesty panel
    shp(x + w - 6, y + 35, x + w - 2, y + 54, cyl(WH[1], WH[2], WH[4], 0.3), 1, 1, 2)
    shp(x + 23, y + 36, x + w - 6, y + 45, vg(WH[2], WH[3]), 1)
    rect(x + 23, y + 44, x + w - 6, y + 45, GR[1])
    # equipment
    monitor(x + 11, y, seed)
    keyboard(x + 15, y + 27)
    mouse(x + 41, y + 26)
    # mug, pens, papers
    shp(x + 3, y + 22, x + 9, y + 30, cyl(WH[0], WH[1], WH[4], 0.3), 2)
    rect(x + 3, y + 22, x + 9, y + 24, GR[3])
    rect(x + 4, y + 22, x + 8, y + 23, "#6f4a30")
    shp(x + 8, y + 25, x + 11, y + 28, vg(WH[3], WH[4]), 1)
    shp(x + 47, y + 24, x + 54, y + 31, vg("#fbf9ee", "#e9e5d2"), 1)    # notepad
    rect(x + 48, y + 26, x + 53, y + 27, "#b9b49c")
    rect(x + 48, y + 28, x + 52, y + 29, "#b9b49c")
    shp(x + 48, y + 22, x + 53, y + 25, vg("#ffe27a", "#e0c040"), 1)   # sticky note
    # PC beside the desk
    pc_tower(x + w + 5, y + 27)


def chair(cx, y):
    """Mesh task chair from behind (back to viewer), rounded and lit from the left."""
    # backrest: tapered rounded mesh panel
    def mesh(px_, py_, u, v):
        base = [GR[2], GR[3], GR[4]][0 if u < 0.22 else 1 if u < 0.7 else 2]
        if (px_ + py_) % 2 == 0:
            base = mix(base, GR[5], 0.35)
        if 0.45 < v < 0.8 and 0.28 < u < 0.72:
            base = mix(base, GR[5], 0.3)                         # lumbar pad
        if v < 0.07:
            base = GR[1]                                         # lit top rail
        return base
    shp(cx - 12, y - 1, cx + 12, y + 22, mesh, 7, 7, 4)
    shp(cx - 12, y + 14, cx - 10, y + 22, vg(GR[1], GR[3]), 1)
    # armrests (rounded pads on thin posts)
    for sx in (-1, 1):
        ax = cx + sx * 15
        shp(ax - 1, y + 14, ax + 1, y + 24, cyl(GR[1], GR[3], GR[5]), 1)
        shp(ax - 4, y + 10, ax + 4, y + 14, vg(GR[1], GR[4]), 2)
    # seat cushion
    shp(cx - 13, y + 21, cx + 13, y + 30, vg(GR[2], GR[5]), 4, 4, 4)
    rect(cx - 10, y + 22, cx + 10, y + 23, GR[1])
    # gas lift
    shp(cx - 2, y + 30, cx + 2, y + 36, cyl(GR[0], GR[2], GR[5]), 1)
    # star base + casters
    shp(cx - 13, y + 35, cx + 13, y + 38, vg(GR[3], GR[5]), 1)
    for ax in (cx - 13, cx - 6, cx + 4, cx + 11):
        shp(ax, y + 37, ax + 3, y + 41, cyl(GR[1], GR[4], GR[5], 0.4), 1)


def water_dispenser(x, y):
    w = 22
    # rounded water bottle
    def bottle(px_, py_, u, v):
        if v > 0.55 and u > 0.12 and u < 0.88:
            return mix("#9fd0ea", "#6fb2d8", v) if u > 0.35 else "#d4edf9"
        return "#f2fbff" if u < 0.3 else "#cfe6f2" if u < 0.75 else "#a8cde0"
    shp(x + 3, y + 2, x + w - 3, y + 15, bottle, 6, 6, 1)
    shp(x + 7, y - 2, x + 15, y + 3, vg(GR[2], GR[4]), 2)                 # cap
    rect(x + 8, y - 1, x + 11, y, GR[0])
    # body
    shp(x, y + 15, x + w, y + 51, cyl(WH[0], WH[1], WH[4], 0.22), 3, 3, 4)
    poly([(x + w, y + 20), (x + w + 3, y + 22), (x + w + 3, y + 50), (x + w, y + 51)], WH[4])
    shp(x + 3, y + 19, x + w - 3, y + 33, vg(GR[3], GR[5]), 3)           # control panel
    shp(x + 5, y + 22, x + 10, y + 27, vg("#9ccdf5", "#3f8fdc"), 2)        # cold tap
    shp(x + 12, y + 22, x + 17, y + 27, vg("#f2a29b", "#d6453d"), 2)       # hot tap
    px(x + 6, y + 30, "#4fd1e8")
    px(x + 16, y + 30, "#d6453d")
    shp(x + 4, y + 35, x + w - 4, y + 37, vg(GR[2], GR[4]), 1)             # cup rest
    shp(x + 3, y + 39, x + w - 3, y + 46, vg(GR[3], GR[5]), 2)             # drip tray
    for gx in range(x + 5, x + w - 5, 2):
        rect(gx, y + 40, gx + 1, y + 45, GR[5])
    shp(x + 2, y + 48, x + w - 2, y + 51, vg(GR[2], GR[5]), 1)


def copier(x, y):
    w = 34
    shp(x + 4, y - 3, x + 21, y + 2, vg("#ffffff", "#e6e9ee"), 1)         # paper on tray
    shp(x, y + 1, x + w, y + 11, vg(WH[0], WH[2]), 4, 4, 1)               # lid / top
    rect(x + 3, y + 2, x + w - 3, y + 3, "#ffffff")
    shp(x, y + 10, x + w, y + 33, cyl(WH[0], WH[1], WH[4], 0.2), 1, 1, 4)  # body
    poly([(x + w, y + 4), (x + w + 3, y + 6), (x + w + 3, y + 33), (x + w, y + 33)], WH[4])
    shp(x + 19, y + 13, x + 31, y + 20, vg(GR[3], GR[5]), 2)              # control panel
    shp(x + 20, y + 14, x + 26, y + 18, vg("#bfe3f5", "#7fb6d6"), 1)       # display
    px(x + 28, y + 15, "#4fd18b")
    px(x + 29, y + 15, "#e6b83a")
    shp(x + 3, y + 13, x + 16, y + 18, vg(GR[3], GR[5]), 1)               # scan slot
    for dy in (21, 26):
        shp(x + 2, y + dy, x + w - 2, y + dy + 4, vg(WH[1], WH[3]), 1)
        rect(x + 3, y + dy, x + w - 3, y + dy + 1, WH[0])
        shp(x + 13, y + dy + 2, x + 21, y + dy + 3, vg(GR[1], GR[3]), 1)
    shp(x + 1, y + 31, x + w - 1, y + 33, vg(GR[2], GR[5]), 1)


def bin_(x, y, c):
    ramp = {"g": (GR[1], GR[2], GR[4]), "k": (GR[2], GR[4], GR[5]), "w": (WH[0], WH[2], WH[4])}[c]
    lid = {"g": GR[4], "k": GR[5], "w": WH[4]}[c]
    shp(x, y + 2, x + 12, y + 19, cyl(*ramp, 0.25), 2, 2, 3)               # cylindrical body
    shp(x - 1, y, x + 13, y + 5, cyl(mix(lid, "#ffffff", 0.3), lid, mix(lid, "#000000", 0.3)), 2)   # lid
    shp(x + 3, y + 1, x + 9, y + 3, vg(GR[5], GR[4]), 1)                    # opening
    shp(x + 4, y + 9, x + 8, y + 14, vg("#8de0b0", "#2aa862") if c == "g" else
        vg("#ffe27a", "#e0b020") if c == "k" else vg("#9ccdf5", "#3f8fdc"), 1)


def dept_sign(x, y, label):
    w = text_w(label, 1) + 14
    shade(x + 2, y + 3, x + w + 3, y + 14, "#1c2030", 0.22)
    shp(x, y, x + w, y + 11, vg(GR[3], GR[5]), 3)
    shp(x + 3, y + 3, x + 5, y + 8, vg("#ffffff", "#d6dae0"), 1)
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
            shp(px_, y - 1, px_ + 3, y + h, cyl(WH[0], WH[2], GR[0], 0.1), 1)


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
        shp(x - 1, a, x + 6, a + 4, vg(WH[0], WH[2]), 2)           # rounded end posts
        shp(x - 1, b - 4, x + 6, b, vg(WH[3], GR[1]), 2)


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
    logo_plaque(320, 16)
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
