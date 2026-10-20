"""Gastron office scene (v6) — minimal monochrome office with oblique depth.

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
    d.polygon(pts, fill=hx(c) if isinstance(c, str) else tuple(c))


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
    eU, eD = ~np.roll(m, 1, 0), ~np.roll(m, -1, 0)
    eL, eR = ~np.roll(m, 1, 1), ~np.roll(m, -1, 1)
    corner = m & ((eU & eL & ~eR & ~eD) | (eU & eR & ~eL & ~eD) | (eD & eL & ~eR & ~eU) | (eD & eR & ~eL & ~eU))
    arr[corner, 3] = 0                       # chamfer convex corners -> soft silhouettes
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


# ------------------------------------------------ oblique blocks (real depth) ---
# Every volume shows three planes: lit top face, mid front face, shaded right side.
DX, DY = 6, -5          # default depth vector (up-right)


def block(x, y, w, h, dx=DX, dy=DY, front=None, top=None, side=None, r=0):
    """Box whose front face is (x, y, w, h); top face and right side extend by (dx, dy).
    top / side may be a colour or a (light, dark) pair -> shaded gradient across the face."""
    front = front or vg(WH[1], WH[3])
    top = top or WH[0]
    side = side or WH[4]
    n = max(1, -dy)
    for k in range(n + 1):                       # top face, scanline by scanline (back = light)
        off = int(round(dx * k / n))
        c = top if isinstance(top, str) else mix(top[1], top[0], k / n)
        rect(x + off, y - k, x + off + w, y - k + 1, c if isinstance(c, str) else "#%02x%02x%02x" % c)
    for i in range(1, dx + 1):                   # right side face, darker toward the back
        off = int(round(-dy * i / dx)) if dx else 0
        c = side if isinstance(side, str) else mix(side[0], side[1], i / dx)
        rect(x + w + i - 1, y - off, x + w + i, y - off + h, c if isinstance(c, str) else "#%02x%02x%02x" % c)
    shp(x, y, x + w, y + h, front, r)
    for i in range(w):                           # crisp light edge on the top-front edge
        blend(x + i, y, "#ffffff", 0.55)
    for j in range(h):
        blend(x + w, y + j, "#10121a", 0.22)


# --------------------------------------------------------------- floor ----
def floor():
    for y in range(72, H):
        for x in range(W):
            t = (y - 72) / (H - 72)
            v = int(226 - 8 * t)
            c = (v, v + 2, v + 6)
            if x % 64 == 0 or (y - 72) % 64 == 0:
                c = (v - 12, v - 11, v - 8)
            px(x, y, c)
    for gx in (80, 224, 400, 544):                     # soft window light on the floor
        for gy in (84, 224):
            for yy in range(34):
                for xx in range(70):
                    a = 0.10 * (1 - abs(xx - 35) / 35) * (1 - yy / 34)
                    blend(gx + xx + yy // 2, gy + yy, "#ffffff", max(0, a))


def carpet(x0, y0, x1, y1, tone):
    def f(x, y, u, v):
        ed = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
        c = mix(tone, "#ffffff", 0.12 * (1 - v))
        if ed < 2:
            return mix(c, "#2a2e38", 0.22 if ed == 0 else 0.10)
        return c
    shp(x0, y0, x1, y1, f, 8)


def aisle(x0, x1):
    for y in range(72, H):
        for x in range(x0, x1):
            v = 240 - int(10 * (y - 72) / (H - 72))
            c = (v, v + 1, v + 4)
            if x in (x0, x1 - 1):
                c = (v - 16, v - 15, v - 12)
            px(x, y, c)


# ---------------------------------------------------------------- wall ----
def wall():
    for y in range(0, 66):
        for x in range(W):
            v = int(240 - 10 * y / 66)
            px(x, y, (v, v + 2, v + 5))
    rect(0, 0, W, 3, GR[3])
    rect(0, 66, W, 72, WH[3])
    rect(0, 66, W, 67, WH[1])
    rect(0, 71, W, 72, WH[4])
    shade(0, 72, W, 80, "#1c2030", 0.22)
    shade(0, 80, W, 86, "#1c2030", 0.08)


def window(x, y, w=64, h=36):
    shade(x + 2, y + h + 6, x + w + 6, y + h + 12, "#1c2030", 0.16)
    shp(x - 3, y - 3, x + w + 3, y + h + 3, vg(WH[0], WH[3]), 2)
    shp(x, y, x + w, y + h, vg("#c6d6e4", "#eef3f8"), 1)
    rect(x + w // 2, y, x + w // 2 + 1, y + h, WH[3])
    for k in range(7):
        for j in range(3):
            blend(x + 6 + k * 2 + j, y + h - 5 - k * 3, "#ffffff", 0.5)


def logo_plaque(cx, y):
    w, h = 132, 30
    x = cx - w // 2
    shade(x + 3, y + 5, x + w + 4, y + h + 7, "#1c2030", 0.26)
    block(x, y + 4, w, h - 4, 3, -3, vg(GR[3], GR[5]), GR[1], GR[5], 4)
    shp(x + 6, y + 9, x + 24, y + 27, vg("#f03a48", "#b80010"), 4)
    fl = ["..#..", ".###.", "#####", "#####", ".###."]
    for r, row in enumerate(fl):
        for k, v in enumerate(row):
            if v == "#":
                rect(x + 10 + k * 2, y + 12 + r * 3, x + 12 + k * 2, y + 15 + r * 3, "#ffffff" if r > 2 else "#ffd9dc")
    text(x + 32, y + 14, "GASTRON", "#ffffff", 2)


# ----------------------------------------------------------- furniture ----
def monitor(x, y):
    """Plain single monitor: thin slab with depth, light desktop on screen."""
    w, h = 30, 20
    poly([(x + w, y), (x + w + 3, y - 2), (x + w + 3, y + h - 2), (x + w, y + h)], GR[5])   # side
    poly([(x, y), (x + w, y), (x + w + 3, y - 2), (x + 3, y - 2)], GR[2])                    # top edge
    shp(x, y, x + w, y + h, vg(GR[3], GR[5]), 2)                                              # bezel
    def scr(px_, py_, u, v):
        if v > 0.86:
            return GR[4]
        if 0.16 < u < 0.84 and 0.14 < v < 0.74:
            return "#fbfcfe" if v > 0.28 else "#c9d0da"
        return mix("#86aacb", "#c4d8e8", v)
    shp(x + 2, y + 2, x + w - 2, y + h - 3, scr, 1)
    for k in range(7):
        for j in range(2):
            blend(x + 5 + k + j, y + 3 + (6 - k), "#ffffff", 0.2)
    shp(x + 12, y + h - 1, x + 18, y + h + 4, cyl(GR[1], GR[3], GR[5]), 1)
    poly([(x + 7, y + h + 3), (x + 23, y + h + 3), (x + 26, y + h + 1), (x + 10, y + h + 1)], GR[1])
    shp(x + 7, y + h + 3, x + 23, y + h + 5, vg(GR[2], GR[5]), 1)


def keyboard(x, y):
    poly([(x, y), (x + 20, y), (x + 23, y - 2), (x + 3, y - 2)], WH[0])
    shp(x, y, x + 20, y + 4, vg(WH[1], WH[3]), 1)
    for k in range(2, 19, 3):
        px(x + k, y + 1, WH[3])
    rect(x + 4, y + 2, x + 16, y + 3, WH[3])


def mouse(x, y):
    shp(x, y - 1, x + 5, y + 5, cyl(WH[0], WH[1], WH[4]), 2)
    px(x + 2, y, GR[1])


def pc_tower(x, y):
    block(x, y, 13, 28, 5, -4, cyl(GR[2], GR[4], GR[5], 0.2), (GR[1], GR[2]), (GR[3], GR[5]), 0)
    rect(x + 3, y + 5, x + 10, y + 6, GR[3])
    rect(x + 3, y + 8, x + 10, y + 9, GR[3])
    shp(x + 5, y + 22, x + 9, y + 26, cyl(GR[0], GR[1], GR[3]), 2)
    rect(x + 1, y + 28, x + 3, y + 30, GR[5])
    rect(x + 10, y + 28, x + 12, y + 30, GR[5])


def desk(x, y, seed):
    """52-wide white desk. (x, y) = top of the monitor. Slab shows its top surface."""
    w = 52
    sy = y + 33                                                           # front-top edge of the slab
    # knee space
    shp(x + 3, sy + 4, x + w - 2, sy + 22, vg(mix(GR[0], "#000000", 0.45), mix(GR[0], "#000000", 0.2)), 1)
    # slab: wide lit top surface + thin front edge + side face
    block(x, sy, w, 4, 7, -11, vg(WH[1], WH[3]), (WH[0], WH[2]), (WH[3], WH[4]), 1)
    # left drawer pedestal (front + inner side)
    block(x + 3, sy + 4, 17, 18, 4, 0, vg(WH[1], WH[3]), WH[2], WH[4], 0)
    rect(x + 4, sy + 12, x + 19, sy + 13, WH[4])
    # right leg panel
    block(x + w - 4, sy + 4, 3, 18, 3, 0, vg(WH[1], WH[3]), WH[2], WH[4], 0)
    # equipment on the surface
    monitor(x + 11, y)
    keyboard(x + 14, sy - 6)
    mouse(x + 40, sy - 7)
    pc_tower(x + w + 5, sy - 6)


def chair(cx, y):
    """Mesh task chair from behind: thick backrest, seat block, arm pads, star base."""
    # backrest slab with visible thickness
    poly([(cx + 12, y + 4), (cx + 15, y + 2), (cx + 15, y + 18), (cx + 12, y + 20)], GR[5])
    poly([(cx - 9, y), (cx + 9, y), (cx + 12, y - 2), (cx - 6, y - 2)], GR[1])
    shp(cx - 12, y, cx + 12, y + 21, cyl(GR[2], GR[3], GR[5], 0.12), 6, 6, 3)
    shp(cx - 5, y + 11, cx + 6, y + 17, lambda a, b, u, v: mix(GR[3], GR[5], 0.4), 2)   # lumbar
    # arm rests
    for sx in (-1, 1):
        ax = cx + sx * 15
        shp(ax - 1, y + 14, ax + 1, y + 24, cyl(GR[1], GR[3], GR[5]), 1)
        poly([(ax - 3, y + 11), (ax + 3, y + 11), (ax + 5, y + 9), (ax - 1, y + 9)], GR[1])
        shp(ax - 3, y + 11, ax + 3, y + 14, vg(GR[2], GR[5]), 1)
    # seat block
    block(cx - 12, y + 22, 24, 7, 3, -2, vg(GR[2], GR[5]), GR[1], GR[5], 3)
    shp(cx - 2, y + 29, cx + 2, y + 36, cyl(GR[0], GR[2], GR[5]), 1)
    shp(cx - 13, y + 35, cx + 13, y + 38, vg(GR[3], GR[5]), 1)
    for ax in (cx - 13, cx - 6, cx + 4, cx + 11):
        shp(ax, y + 37, ax + 3, y + 41, cyl(GR[1], GR[4], GR[5], 0.4), 1)


def water_dispenser(x, y):
    w = 22
    def bottle(px_, py_, u, v):
        if v > 0.55:
            return mix("#a6d3ea", "#76b6d9", v) if u > 0.3 else "#d6edf8"
        return "#f2fbff" if u < 0.3 else "#cfe6f2" if u < 0.75 else "#a8cde0"
    shp(x + 3, y + 1, x + w - 3, y + 14, bottle, 6, 6, 1)
    shp(x + 7, y - 3, x + 15, y + 2, vg(GR[2], GR[4]), 2)
    block(x, y + 14, w, 36, 5, -4, cyl(WH[0], WH[1], WH[4], 0.2), (WH[0], WH[2]), (WH[3], WH[4]), 3)
    shp(x + 4, y + 20, x + w - 4, y + 30, vg(GR[3], GR[5]), 2)
    shp(x + 6, y + 23, x + 10, y + 27, vg("#9ccdf5", "#3f8fdc"), 1)
    shp(x + 12, y + 23, x + 16, y + 27, vg("#f2a29b", "#d6453d"), 1)
    shp(x + 4, y + 38, x + w - 4, y + 44, vg(GR[3], GR[5]), 2)


def copier(x, y):
    w = 34
    block(x, y + 8, w, 24, 6, -6, cyl(WH[0], WH[1], WH[4], 0.2), (WH[0], WH[2]), (WH[3], WH[4]), 3)
    shp(x + 20, y + 12, x + 31, y + 18, vg(GR[3], GR[5]), 2)
    shp(x + 21, y + 13, x + 26, y + 16, vg("#bfe3f5", "#7fb6d6"), 1)
    rect(x + 3, y + 22, x + w - 3, y + 23, WH[4])
    shp(x + 12, y + 26, x + 22, y + 28, vg(GR[1], GR[3]), 1)
    shp(x + 5, y + 3, x + 22, y + 8, vg("#ffffff", "#e6e9ee"), 1)


def dept_sign(x, y, label):
    w = text_w(label, 1) + 12
    shade(x + 2, y + 3, x + w + 3, y + 14, "#1c2030", 0.2)
    shp(x, y, x + w, y + 11, vg(GR[3], GR[5]), 3)
    text(x + 6, y + 3, label, "#ffffff", 1)


# --------------------------------------------------------- glass walls ----
def glass_shadow_h(x0, x1, y):
    shade(x0 + 3, y + 14, x1 + 4, y + 21, "#1c2030", 0.15)


def glass_h(x0, x1, y, h=14, gaps=()):
    spans, cur = [], x0
    for g0, g1 in sorted(gaps):
        spans.append((cur, g0))
        cur = g1
    spans.append((cur, x1))
    for a, b in spans:
        if b <= a:
            continue
        poly([(a, y), (b, y), (b + 3, y - 3), (a + 3, y - 3)], WH[0])        # top face (thickness)
        shade(a, y + 2, b, y + h - 2, "#9fc3d8", 0.20)                          # glass
        for gx in range(a + 10, b - 8, 70):
            for k in range(h - 4):
                blend(gx + (h - 4 - k) // 2, y + 2 + k, "#ffffff", 0.34)
        rect(a, y, b, y + 2, WH[2])
        rect(a, y, b, y + 1, WH[0])
        rect(a, y + h - 2, b, y + h, GR[1])
        poly([(b, y), (b + 3, y - 3), (b + 3, y + h - 3), (b, y + h)], GR[0])   # end face
    for a, b in spans:
        for px_ in (a, b - 3):
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
        poly([(x, a), (x + 5, a), (x + 8, a - 3), (x + 3, a - 3)], WH[0]) if False else None
        shade(x, a, x + 5, b, "#9fc3d8", 0.30)
        rect(x, a, x + 1, b, WH[0])
        rect(x + 4, a, x + 5, b, GR[1])
        shp(x - 1, a, x + 6, a + 4, vg(WH[0], WH[2]), 2)
        shp(x - 1, b - 4, x + 6, b, vg(WH[3], GR[1]), 2)


# =============================================================== BUILD ====
ZONES = {
    "LEAD": (24, 90, 272, 210, "#c9cdd4"),
    "CREATIVE": (368, 90, 616, 210, "#c9cdd4"),
    "GROWTH": (24, 228, 272, 348, "#c9cdd4"),
    "DATA": (368, 228, 616, 348, "#c9cdd4"),
}


def build():
    floor()
    wall()
    aisle(272, 368)
    for name, (x0, y0, x1, y1, tone) in ZONES.items():
        carpet(x0, y0, x1, y1, tone)
    for wx in (28, 124, 412, 508):
        window(wx, 14)
    logo_plaque(320, 16)
    for name, (x0, y0, x1, y1, tone) in ZONES.items():
        glass_shadow_h(x0, x1, y0)
        glass_shadow_h(x0, x1, y1 - 14)
        shade(x0 + 5, y0, x0 + 10, y1, "#1c2030", 0.12)
        shade(x1, y0, x1 + 5, y1, "#1c2030", 0.12)
    for name, (x0, y0, x1, y1, tone) in ZONES.items():
        for i in range(3):
            dx = x0 + 10 + i * 76
            dy = y0 + 22
            obj(desk, dx, dy, i + len(name), L=13)
            obj(chair, dx + 26, dy + 38, L=9)
    obj(water_dispenser, 286, 96, L=14)
    obj(copier, 322, 104, L=10)
    for name, (x0, y0, x1, y1, tone) in ZONES.items():
        glass_h(x0, x1, y0)
        glass_h(x0, x1, y1 - 14, gaps=((x1 - 70, x1 - 30),) if x0 < 300 else ((x0 + 30, x0 + 70),))
        glass_v(x0, y0, y1)
        if x0 < 300:
            glass_v(x1 - 5, y0, y1, gaps=((y0 + 36, y0 + 84),))
        else:
            glass_v(x0, y0, y1, gaps=((y0 + 36, y0 + 84),))
            glass_v(x1 - 5, y0, y1)
        dept_sign(x0 + 14, y0 + 3, name)
    arr = np.array(im).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    t = xx / W * 0.55 + yy / H * 0.45
    arr[..., :3] *= (1.04 - 0.11 * t)[..., None]
    e = np.minimum.reduce([xx, W - 1 - xx, yy, H - 1 - yy])
    arr[..., :3] *= (1 - np.clip((10 - e) / 10, 0, 1) * 0.18)[..., None]
    im.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)), (0, 0))


if __name__ == "__main__":
    build()
    im.convert("RGB").save(OUT / "office-minimal.png")
    im.convert("RGB").resize((W * 3, H * 3), Image.NEAREST).save(OUT / "office-minimal-x3.png")
    print("ok", W, H)
