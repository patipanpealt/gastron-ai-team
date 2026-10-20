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


