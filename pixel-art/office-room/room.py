"""Gastron office room — cosy top-down pixel office, laid out after Ref/office-room-ref.webp.

Drawn from scratch with PIL (no pixels copied from the reference).
Every piece of furniture = lit top face + darker front face, 1px dark outline,
soft cast shadow. Run:  python3 room.py  ->  office-room.png (240x240) + office-room-x4.png
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

W, H = 240, 240
OUT = Path(__file__).parent
im = Image.new("RGBA", (W, H), (45, 47, 60, 255))
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
        im.putpixel((int(x), int(y)), hx(c) + (255,))


def rect(x0, y0, x1, y1, c):
    if x1 > x0 and y1 > y0:
        d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=hx(c))


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


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


def disc(cx, cy, rx, ry, c):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                px(x, y, c)


# ------------------------------------------------------------- palette ----
OL = "#2b2230"                                                   # outline
WOOD_T = ["#c48446", "#a96a34", "#8e572a"]                       # table tops (light -> dark)
WOOD_F = ["#74442a", "#61381f", "#432414"]                       # fronts
DARK_T = ["#7d4f36", "#6b4230", "#583426"]                       # dark wood (shelves, door)
DARK_F = ["#55331f", "#472a1a", "#361f14"]
TEAL_T = ["#5ea79c", "#4c8f85", "#3c776f"]
TEAL_F = ["#3b6f68", "#2f5c56", "#234642"]
FLOOR = ["#d6bb90", "#ccb087", "#c3a67c", "#b89a70"]
FLOOR_GAP = "#b49870"
WALL = ["#ece3cb", "#e3d8bd", "#d6c9ab"]
LEAF = ["#2f6b34", "#3f8a3c", "#58a64a", "#7cc35c"]
POT = ["#e8e2d4", "#c9c0ad"]
TERRA = ["#c4673e", "#9c4c2c"]
SCREEN = ["#9fd6e0", "#6ab4c8", "#3d7f98"]
METAL = ["#5d6470", "#454b56", "#30343d"]


# ============================================== layered objects + depth ===
def obj(fn, *a, L=4, outline=True, **k):
    """Draw fn on its own layer -> 1px dark outline -> soft cast shadow -> composite."""
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
        sy = int(round(kk * 0.8))
        sh[sy:, kk:] = m[: H - sy, : W - kk]
        alpha[sh & (alpha == 0)] = 0.40 if kk <= L // 2 + 1 else 0.24
    alpha[m] = 0
    out[..., :3] = out[..., :3] * (1 - alpha[..., None]) + np.array([40, 24, 30]) * alpha[..., None]
    out[m, :3] = arr[m, :3]
    out[..., 3] = 255
    base.paste(Image.fromarray(out.astype(np.uint8)), (0, 0))


def box(x, y, w, dp, h, top=WOOD_T, front=WOOD_F, panels=0, gap=None):
    """Top-down furniture block: top face (w x dp) above a front face (w x h)."""
    rect(x, y, x + w, y + dp, top[1])
    rect(x, y, x + w, y + 1, top[0])
    rect(x, y, x + 1, y + dp, top[0])
    rect(x, y + dp - 1, x + w, y + dp, top[2])
    for i in range(x + 3, x + w - 2, 7):                         # subtle grain
        if Hh(i, y, 5) < 0.6:
            rect(i, y + 2, i + 1 + int(Hh(i, y, 6) * 3), y + 3, top[2])
    rect(x, y + dp, x + w, y + dp + h, front[0])
    rect(x, y + dp + h - 1, x + w, y + dp + h, front[2])
    if gap:                                                       # knee space
        g0, g1 = gap
        rect(x + g0, y + dp + 1, x + g1, y + dp + h, front[2])
        rect(x + g0, y + dp + 1, x + g1, y + dp + 2, mix(front[2], "#000000", 0.4))
    if panels:
        pw = w / panels
        for i in range(panels):
            a, b = int(x + i * pw), int(x + (i + 1) * pw)
            if gap and a >= x + gap[0] and b <= x + gap[1]:
                continue
            rect(a + 1, y + dp + 1, b - 1, y + dp + h - 2, front[1])
            rect(a + 1, y + dp + 1, b - 1, y + dp + 2, front[0])
            rect((a + b) // 2 - 1, y + dp + 3, (a + b) // 2 + 2, y + dp + 4, "#e0b070")


# ---------------------------------------------------------------- props ---
def monitor(x, y, w=12, h=8, on=True):
    rect(x, y, x + w, y + h, METAL[2])
    if on:
        for yy in range(y + 1, y + h - 1):
            t = (yy - y) / h
            rect(x + 1, yy, x + w - 1, yy + 1, mix(SCREEN[0], SCREEN[2], t))
        rect(x + 2, y + 2, x + w // 2, y + 3, "#e8f6f8")
        rect(x + 2, y + 4, x + w - 3, y + 5, SCREEN[2])
    else:
        rect(x + 1, y + 1, x + w - 1, y + h - 1, "#3a3f4c")
        rect(x + 2, y + 1, x + 4, y + 3, "#5a6170")
    rect(x + w // 2 - 1, y + h, x + w // 2 + 1, y + h + 2, METAL[1])
    rect(x + w // 2 - 3, y + h + 2, x + w // 2 + 3, y + h + 3, METAL[0])


def keyboard(x, y, w=10):
    rect(x, y, x + w, y + 3, "#e6e2da")
    for k in range(x + 1, x + w - 1, 2):
        px(k, y + 1, "#b8b2a6")
    rect(x, y + 2, x + w, y + 3, "#b8b2a6")


def lamp(x, y):
    rect(x + 2, y + 3, x + 3, y + 9, METAL[1])
    rect(x, y + 9, x + 5, y + 10, METAL[2])
    rect(x, y, x + 6, y + 3, "#e8853a")
    rect(x, y, x + 6, y + 1, "#f6b066")
    rect(x + 1, y + 3, x + 5, y + 4, "#ffe2a0")


def paper(x, y, w=5, h=4):
    rect(x, y, x + w, y + h, "#f4f1ea")
    rect(x + 1, y + 1, x + w - 1, y + 2, "#c9c4b8")


def mug(x, y, c="#e8e2d4"):
    rect(x, y, x + 3, y + 3, c)
    px(x + 3, y + 1, c)
    px(x + 1, y, "#6a4a30")


def books(x, y, w, h, seed):
    cols = ["#b0473a", "#3f6f8f", "#d8b44a", "#4f8f5c", "#e8e2d4", "#7a4f8f", "#c96a3a", "#2f4f6f"]
    xx = x
    i = 0
    while xx < x + w:
        bw = 1 + int(Hh(i, seed, 1) * 2)
        bh = h - int(Hh(i, seed, 2) * 3)
        if xx + bw > x + w:
            break
        if Hh(i, seed, 4) < 0.12:
            xx += bw + 1
            i += 1
            continue
        c = cols[int(Hh(i, seed, 3) * len(cols))]
        rect(xx, y + h - bh, xx + bw, y + h, c)
        px(xx, y + h - bh, mix(c, "#ffffff", 0.35))
        xx += bw
        i += 1


def plant(cx, cy, r, pot="white", pot_h=6):
    pw = max(4, int(r * 0.9))
    pc = POT if pot == "white" else TERRA
    py = cy + int(r * 0.6)
    rect(cx - pw // 2, py, cx + pw // 2 + 1, py + pot_h, pc[0])
    rect(cx + pw // 2 - 1, py, cx + pw // 2 + 1, py + pot_h, pc[1])
    rect(cx - pw // 2 - 1, py, cx + pw // 2 + 2, py + 2, pc[0])
    # leafy crown: overlapping clusters, dark underneath, light on top-left
    blobs = [(0, 0, r)] + [((Hh(i, cx, 7) - 0.5) * r * 1.3, (Hh(i, cy, 8) - 0.7) * r * 1.1, r * 0.55) for i in range(6)]
    for bx, by, br in blobs:
        disc(cx + bx, cy + by, br, br * 0.9, LEAF[1])
    for bx, by, br in blobs:
        disc(cx + bx - br * 0.25, cy + by - br * 0.3, br * 0.6, br * 0.5, LEAF[2])
    for i in range(int(r * 3)):
        lx = cx + (Hh(i, cx, 9) - 0.5) * r * 1.8
        ly = cy + (Hh(i, cy, 10) - 0.6) * r * 1.6
        px(lx, ly, LEAF[3] if Hh(i, 0, 11) < 0.5 else LEAF[0])


# ------------------------------------------------------------- room shell -
def room():
    # floor: staggered horizontal planks
    for y in range(66, 232):
        row = (y - 66) // 8
        for x in range(13, 228):
            off = int(Hh(row, 3) * 28)
            seg = (x + off) // 28
            c = FLOOR[int(Hh(row, seg, 4) * 3)]
            if (y - 66) % 8 == 7 or (x + off) % 28 == 0:
                c = FLOOR_GAP
            elif Hh(x, y, 12) < 0.015:
                c = FLOOR[3]
            px(x, y, c)
    # back wall
    for y in range(9, 66):
        for x in range(13, 228):
            px(x, y, WALL[0] if y < 56 else WALL[1])
    rect(13, 62, 228, 66, "#8a5a38")          # skirting board
    rect(13, 62, 228, 63, "#a8724a")
    rect(13, 65, 228, 66, "#5c3a24")
    shade(13, 66, 228, 70, "#3a2418", 0.22)
    # outer walls (thick dark rim like the reference)
    rect(8, 4, 232, 9, "#e9e0c8")
    rect(8, 4, 232, 5, "#f6efdc")
    rect(8, 4, 13, 236, "#d8ccb0")
    rect(228, 4, 232, 236, "#c9bc9e")
    rect(8, 232, 232, 236, "#5c4a3c")
    rect(9, 9, 13, 232, "#b8aa8c")
    rect(228, 9, 230, 232, "#a8987a")
    for y in range(66, 232):                  # side-wall shadows on the floor
        blend(13, y, "#3a2418", 0.30)
        blend(14, y, "#3a2418", 0.15)
        blend(227, y, "#3a2418", 0.35)
        blend(226, y, "#3a2418", 0.2)


def door(x, y):
    rect(x - 2, y - 2, x + 18, y + 54, "#4a3326")
    rect(x, y, x + 16, y + 54, "#3d2a22")
    rect(x + 1, y + 1, x + 15, y + 54, "#4e3529")
    rect(x + 3, y + 4, x + 8, y + 10, "#8bc4cf")
    rect(x + 3, y + 4, x + 8, y + 5, "#c8eaf0")
    for yy in range(y + 14, y + 52, 9):
        rect(x + 2, yy, x + 14, yy + 1, "#3d2a22")
    rect(x + 12, y + 30, x + 14, y + 32, "#d8b060")


def window(x, y, w, h):
    rect(x - 2, y - 2, x + w + 2, y + h + 3, "#5c4a3c")
    rect(x - 1, y - 1, x + w + 1, y + h + 2, "#e9e2d0")
    for yy in range(y, y + h):
        t = (yy - y) / h
        rect(x, yy, x + w, yy + 1, mix("#6fb3c9", "#a9d9e3", t))
    for k in range(5):                         # glass glints
        px(x + 4 + k, y + h - 3 - k, "#d8f1f5")
        px(x + w - 12 + k, y + h - 3 - k, "#d8f1f5")
    rect(x - 3, y + h + 2, x + w + 3, y + h + 4, "#c9bc9e")


# ------------------------------------------------------------ furniture ---
def back_desk():                                # long desk against the back wall
    box(48, 54, 68, 12, 15, panels=4)
    monitor(66, 44, 13, 9)
    monitor(82, 47, 9, 7, on=False)
    rect(56, 47, 62, 53, METAL[2])              # small PC
    rect(57, 48, 61, 52, METAL[1])
    px(59, 50, "#7cf0a0")
    lamp(102, 44)
    keyboard(68, 59)
    paper(53, 58)
    mug(96, 57)
    rect(90, 56, 93, 60, "#3a3f4c")             # pen cup
    px(90, 55, "#b0473a"); px(92, 54, "#3f6f8f")
    paper(76, 58, 4, 3)
    rect(108, 57, 113, 60, "#3f6f8f")


def filing_cabinet():
    box(120, 22, 18, 3, 44, TEAL_T, TEAL_F)
    for i, yy in enumerate((28, 38, 48)):
        rect(122, yy, 136, yy + 8, TEAL_F[1])
        rect(122, yy, 136, yy + 1, TEAL_T[2])
        rect(126, yy + 3, 132, yy + 4, "#c9d8d0")
    rect(123, 15, 135, 22, TEAL_F[2])          # binders on top
    rect(124, 16, 128, 22, "#d8b44a")
    rect(129, 16, 134, 22, "#b0473a")


def bookshelf():
    box(141, 14, 27, 3, 58, DARK_T, DARK_F)
    for i, yy in enumerate((19, 30, 41, 52)):
        rect(143, yy, 166, yy + 10, "#3a2418")
        books(144, yy + 1, 21, 9, i * 7 + 3)
        rect(143, yy + 10, 166, yy + 11, DARK_T[1])
    rect(143, 63, 166, 70, DARK_F[1])
    rect(150, 66, 159, 67, "#e0b070")


def small_cabinet():                            # stubby cabinet in front of the filing cabinet
    box(122, 54, 15, 4, 12, WOOD_T, WOOD_F, panels=1)
    rect(126, 50, 132, 56, "#b0473a")
    rect(127, 51, 131, 52, "#d86a5a")


def sideboard():
    box(173, 52, 38, 6, 18, DARK_T, DARK_F)
    for xx in range(175, 209, 4):
        rect(xx, 59, xx + 3, 69, DARK_F[1])
        rect(xx, 59, xx + 3, 60, DARK_F[0])


def left_counter():
    box(16, 83, 21, 64, 12, WOOD_T, WOOD_F, panels=2)
    monitor(19, 122, 15, 10, on=False)
    paper(28, 102, 6, 4)
    rect(18, 140, 34, 145, "#e6e2da")
    for k in range(19, 33, 2):
        px(k, 142, "#b8b2a6")
    for yy in range(96, 150, 5):                # wall shelf with binders on the left wall
        rect(38, yy, 41, yy + 4, ["#3f6f8f", "#2f5c56", "#4c8f85"][(yy // 5) % 3])


def armchair(x, y):
    box(x, y, 26, 6, 4, TEAL_T, TEAL_F)         # backrest
    rect(x, y + 6, x + 5, y + 18, TEAL_T[2])    # arms
    rect(x + 21, y + 6, x + 26, y + 18, TEAL_T[2])
    rect(x, y + 6, x + 5, y + 7, TEAL_T[0])
    rect(x + 21, y + 6, x + 26, y + 7, TEAL_T[0])
    rect(x + 5, y + 10, x + 21, y + 17, TEAL_T[1])   # seat cushion
    rect(x + 5, y + 10, x + 21, y + 11, TEAL_T[0])
    rect(x, y + 18, x + 26, y + 21, TEAL_F[1])
    rect(x + 1, y + 21, x + 3, y + 23, "#3a2418")
    rect(x + 23, y + 21, x + 25, y + 23, "#3a2418")


def center_desk():
    box(91, 112, 64, 22, 14, panels=4, gap=(18, 46))
    monitor(116, 106, 18, 12, on=False)
    lamp(97, 104)
    rect(96, 122, 103, 132, "#3a3f4c")          # tablet / organizer
    rect(97, 123, 102, 131, "#5a6170")
    keyboard(114, 126, 14)
    mouse_x, mouse_y = 131, 126
    rect(mouse_x, mouse_y, mouse_x + 2, mouse_y + 3, "#e6e2da")
    rect(136, 109, 144, 116, "#e6e2da")         # desk phone
    rect(137, 110, 143, 112, "#b8b2a6")
    rect(146, 120, 151, 125, "#4f8f5c")         # framed photo
    rect(147, 121, 150, 124, "#f4f1ea")
    paper(140, 127, 6, 4)
    mug(106, 128, "#d8b44a")
    rect(109, 113, 112, 118, "#3a3f4c")         # pencil cup
    px(109, 112, "#d8b44a"); px(111, 111, "#b0473a")
    paper(128, 117, 5, 3)
    rect(150, 128, 154, 133, "#d8b44a")


def left_desk():
    box(50, 129, 30, 16, 14, panels=2)
    monitor(57, 121, 14, 10)
    keyboard(58, 136, 12)
    rect(52, 131, 56, 139, METAL[2])            # speaker
    rect(53, 132, 55, 134, METAL[0])


def teal_cabinet():
    box(46, 156, 13, 3, 20, TEAL_T, TEAL_F)
    for yy in (161, 168):
        rect(48, yy, 57, yy + 5, TEAL_F[1])
        rect(51, yy + 2, 54, yy + 3, "#c9d8d0")


def printer_station():
    box(59, 150, 20, 14, 14, ["#7d8490", "#6a717d", "#575d68"], ["#454b56", "#3a3f48", "#2a2e35"])
    rect(62, 152, 76, 158, "#3a3f48")
    rect(63, 153, 75, 154, "#f4f1ea")
    rect(70, 159, 75, 162, "#b0473a")
    px(64, 160, "#7cf0a0")


def right_desk():
    box(185, 88, 37, 16, 13, panels=2, gap=(10, 27))
    monitor(190, 80, 12, 9)
    monitor(204, 83, 11, 8)
    keyboard(194, 96, 11)
    paper(210, 95, 5, 4)
    rect(214, 90, 219, 94, "#d8b44a")


def tall_shelf():
    box(208, 68, 10, 3, 24, DARK_T, DARK_F)
    for yy in (73, 80, 87):
        rect(209, yy, 217, yy + 6, "#3a2418")
        books(209, yy, 8, 6, yy)


def office_chair(cx, y):
    rect(cx - 7, y, cx + 7, y + 6, "#3a2c30")   # backrest (top-down)
    rect(cx - 7, y, cx + 7, y + 1, "#5a4448")
    rect(cx - 6, y + 6, cx + 6, y + 13, "#6b4a3a")   # seat
    rect(cx - 6, y + 6, cx + 6, y + 7, "#8a6450")
    rect(cx - 8, y + 7, cx - 6, y + 12, "#2a2a30")
    rect(cx + 6, y + 7, cx + 8, y + 12, "#2a2a30")
    rect(cx - 1, y + 13, cx + 1, y + 16, "#2a2a30")
    rect(cx - 6, y + 16, cx + 7, y + 17, "#2a2a30")
    for ax in (cx - 6, cx, cx + 6):
        px(ax, y + 18, "#2a2a30")


def side_desk():                                 # narrow desk, right middle
    box(176, 148, 19, 26, 12, panels=1)
    rect(181, 152, 190, 158, "#e6e2da")         # open laptop
    rect(182, 153, 189, 156, SCREEN[1])
    rect(181, 160, 190, 162, "#b8b2a6")
    paper(178, 165, 5, 4)
    rect(185, 166, 192, 170, "#3f6f8f")


def stool(cx, y):
    disc(cx, y + 3, 8, 4, "#7a4828")
    disc(cx - 1, y + 2, 6, 2.6, "#9a6234")
    rect(cx - 6, y + 6, cx - 4, y + 13, "#5c3420")
    rect(cx + 4, y + 6, cx + 6, y + 13, "#5c3420")


def right_cabinet():
    box(214, 163, 16, 4, 58, WOOD_T, WOOD_F)
    for yy in range(169, 219, 10):
        rect(216, yy, 228, yy + 8, WOOD_F[1])
        rect(216, yy, 228, yy + 1, WOOD_F[0])
        rect(220, yy + 3, 224, yy + 4, "#e0b070")
    rect(216, 158, 224, 164, "#e6e2da")          # box on top
    rect(216, 158, 224, 159, "#ffffff")


def bottom_table():
    box(93, 196, 54, 14, 12, panels=3)
    paper(118, 199, 7, 5)
    mug(132, 201)
    rect(140, 199, 145, 204, "#3f6f8f")
    for cx in (106, 120, 134):                   # stools tucked under the table
        rect(cx - 5, 222, cx + 5, 228, "#6b4a3a")
        rect(cx - 5, 222, cx + 5, 223, "#8a6450")


def bench(x, y):
    box(x, y, 25, 8, 7, WOOD_T, WOOD_F)
    rect(x, y - 4, x + 25, y, "#8a5832")         # backrest
    rect(x, y - 4, x + 25, y - 3, "#a86d3e")
    rect(x + 1, y + 15, x + 3, y + 18, "#5c3420")
    rect(x + 22, y + 15, x + 24, y + 18, "#5c3420")


def copier(x, y):
    box(x, y, 19, 14, 22, ["#8c929c", "#767c88", "#626873"], ["#4e535d", "#41454e", "#2e3138"])
    rect(x + 3, y + 2, x + 16, y + 9, "#3a3f48")
    rect(x + 4, y + 3, x + 15, y + 4, "#f4f1ea")
    for yy in (y + 18, y + 25, y + 31):
        rect(x + 2, yy, x + 17, yy + 5, "#4e535d")
        rect(x + 7, yy + 2, x + 12, yy + 3, "#9aa0aa")


def low_shelf(x, y):
    box(x, y, 12, 3, 20, DARK_T, DARK_F)
    rect(x + 1, y + 6, x + 11, y + 12, "#3a2418")
    books(x + 1, y + 6, 10, 6, x)
    rect(x + 1, y + 14, x + 11, y + 21, "#3a2418")
    books(x + 1, y + 15, 10, 6, x + 9)


def boards(x, y):                                # framed boards leaning on the wall
    rect(x, y, x + 9, y + 24, "#e8e2d4")
    rect(x + 1, y + 1, x + 8, y + 23, "#c9c0ad")
    rect(x + 6, y + 3, x + 15, y + 25, "#7a5a3c")
    rect(x + 7, y + 4, x + 14, y + 24, "#d8cbb0")


def rug(x0, y0, x1, y1):
    for y in range(y0, y1):
        for x in range(x0, x1):
            e = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
            c = "#3f6f8f" if e < 2 else "#d8cbb0" if e < 3 else "#7a5a8a" if ((x + y) // 3) % 2 else "#a07a6a"
            px(x, y, c)
    disc((x0 + x1) / 2, (y0 + y1) / 2, 4, 5, "#d8b44a")


def striped_rug(x0, y0, x1, y1):
    for y in range(y0, y1):
        for x in range(x0, x1):
            px(x, y, "#e8e2d4" if ((x - y) // 2) % 2 == 0 else "#8a8478")


# =============================================================== BUILD ====
def build():
    room()
    door(19, 18)
    window(52, 20, 64, 26)
    window(172, 20, 56, 26)
    rug(156, 195, 175, 222)
    striped_rug(176, 204, 187, 222)
    diag = Image.new("L", (W, H), 0)             # big diagonal shadow across the right half
    ImageDraw.Draw(diag).polygon([(150, 110), (226, 150), (226, 200), (175, 232), (140, 232), (160, 170)], fill=1)
    dm = np.array(diag)
    for y, x in zip(*np.nonzero(dm)):
        blend(x, y, "#3a2418", 0.18)

    obj(back_desk, L=4)
    obj(filing_cabinet, L=5)
    obj(bookshelf, L=6)
    obj(small_cabinet, L=3)
    obj(sideboard, L=4)
    obj(plant, 189, 41, 6, "terra", L=3)
    obj(plant, 205, 42, 5, "white", L=3)
    obj(plant, 220, 54, 10, "white", 8, L=5)
    obj(tall_shelf, L=4)
    obj(left_counter, L=4)
    obj(plant, 25, 97, 10, "white", 7, L=5)
    obj(armchair, 57, 87, L=4)
    obj(right_desk, L=5)
    obj(office_chair, 203, 112, L=4)
    obj(center_desk, L=6)
    obj(left_desk, L=5)
    obj(printer_station, L=5)
    obj(teal_cabinet, L=4)
    obj(side_desk, L=5)
    obj(stool, 186, 189, L=3)
    obj(right_cabinet, L=6)
    obj(plant, 100, 186, 9, "white", 6, L=4)
    obj(bottom_table, L=5)
    obj(bench, 189, 208, L=4)
    obj(copier, 16, 183, L=5)
    obj(plant, 40, 205, 6, "terra", 7, L=4)
    obj(boards, 45, 200, L=3)
    obj(low_shelf, 59, 199, L=4)
    obj(plant, 78, 213, 5, "white", 5, L=3)
    obj(plant, 16, 170, 5, "white", 4, L=3)
    # warm grade + vignette
    arr = np.array(im).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = 1 - np.clip(r - 0.55, 0, 1) * 0.35
    arr[..., 0] *= v * 1.02
    arr[..., 1] *= v * 0.99
    arr[..., 2] *= v * 0.94
    im.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)), (0, 0))


if __name__ == "__main__":
    build()
    im.convert("RGB").save(OUT / "office-room.png")
    im.convert("RGB").resize((W * 4, H * 4), Image.NEAREST).save(OUT / "office-room-x4.png")
    print("ok")
