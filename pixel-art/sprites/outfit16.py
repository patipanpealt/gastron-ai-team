"""Character kit v6 — TOPS and BOTTOMS drawn natively at 16x32 on the approved chibi body.

Garments are painted per animation frame from the body's own part labels (torso / arm / hand / leg, see
character16_anim.Frame.lab), so they fit every pose and view exactly: the torso block gets a small
hand-authored template (a smooth upper-left -> lower-right tone gradient plus the details of the garment:
neckline, collar, placket + buttons, lapels + tie, ribbon, straps ...), sleeves follow the arm pixels, trousers
follow the leg pixels, skirts hang from the waist row and get their own outline.

Rows of the torso block (5 rows, top to bottom):   0-3  top (neckline .. hem)    4  waist  (bottom)
Draw order per cell:  hair back -> body -> BOTTOM -> TOP -> face -> hair front

A template cell is a symbol:  . = nothing (body skin shows)   0-4 = tone of the garment's main palette
and a few letters for a second palette (w white, x white shade, b button, r red tie, R red shade, d deep navy).
"""
from PIL import Image

import character16_anim as A

W, H = A.W, A.H
OLINE = 5

PAL = {  # highlight, light, base, shade, deep, outline   (hue-shifted: cool shadows, warm highlights)
    "tee":     ["#a8e6bc", "#66c893", "#34a86c", "#218458", "#176046", "#0b2c22"],
    "shirt":   ["#f2f8ff", "#d4e5fa", "#adc9ee", "#86a7d8", "#6080b6", "#1e2848"],
    "white":   ["#ffffff", "#f3f4f9", "#dfe2ee", "#bfc4d8", "#979fba", "#2a2c44"],
    "navy":    ["#7083b4", "#4f6192", "#384672", "#293455", "#1d253e", "#0b0f1e"],
    "red":     ["#ff7a82", "#e8202e", "#b8000f", "#84000c", "#5a0008", "#2a0006"],
    "rose":    ["#ffd8e0", "#f8a8ba", "#e67f98", "#c65e7c", "#9c4562", "#40182a"],
    "heather": ["#ffffff", "#eef0f3", "#d6d9e0", "#b2b7c3", "#8b91a1", "#262a36"],
    "slacks":  ["#8e94ae", "#666c88", "#4a4f6a", "#363a54", "#262944", "#0f1020"],
    "jeans":   ["#b0d0f2", "#76a0d6", "#5280ba", "#3b629f", "#294a80", "#101c3c"],
    "khaki":   ["#fff2cc", "#eed59e", "#d4b678", "#ac8c54", "#836a3a", "#3a2a10"],
    "wine":    ["#e89aa8", "#bc5870", "#92354f", "#6e2339", "#4e172a", "#220913"],
}

# ---- top templates: 4 rows (0 = neckline row) x 6 columns (S, N) or 5 columns (W) ------------------------
TOPS = {
    "tee": {"pal": "tee", "sleeve": (2, 3), "S": ["14..43", "112233", "122333", "223334"],
            "N": ["124433", "112233", "122333", "223334"], "W": ["14233", "12233", "22333", "23334"]},
    "shirt": {"pal": "shirt", "sleeve": (2, 3), "S": ["1w..w3", "12wx43", "12bx33", "22wx34"],
              "N": ["1wwww3", "112233", "122333", "223334"], "W": ["w1233", "x1233", "b2233", "x2334"],
              "sym": {"w": ("white", 1), "x": ("white", 3), "b": ("white", 0)}},
    "suit": {"pal": "navy", "sleeve": (2, 3), "S": ["12ww33", "1dwwd3", "1drrd3", "22rr34"],
             "N": ["12ww33", "112233", "12dd33", "22dd34"], "W": ["w1233", "d1233", "r2233", "r2334"],
             "sym": {"w": ("white", 1), "r": ("red", 1), "R": ("red", 2), "d": ("navy", 4)}},
    "dress": {"pal": "rose", "sleeve": (1, 2), "S": ["12..33", "112233", "122333", "wwwwWW"],
              "waist": {"S": "122334", "N": "122334", "W": "12334"},
              "skirt": [("S", 1, "12132434"), ("S", 2, "1213243424")],
              "N": ["122333", "112233", "122333", "wwWWww"], "W": ["12233", "12233", "22333", "wwwwW"],
              "sym": {"w": ("white", 1), "W": ("white", 3)}},
    "tank": {"pal": "heather", "sleeve": None, "S": [".1..3.", ".1233.", "112233", "122334"],
             "N": [".1..3.", ".1233.", "112233", "122334"], "W": ["..2..", ".1233", "12233", "22334"]},
}

# ---- bottoms: waist row (torso row 4), legs, and a skirt hanging from the waist -----------------------------
BOTTOMS = {
    "slacks": {"pal": "slacks", "waist": {"S": "233344", "N": "233344", "W": "23344"}, "legs": "full", "cuff": 0},
    "jeans": {"pal": "jeans", "waist": {"S": "123334", "N": "123334", "W": "12334"}, "legs": "full", "cuff": -1},
    "shorts": {"pal": "khaki", "waist": {"S": "123334", "N": "123334", "W": "12334"}, "legs": "top", "cuff": 0},
    "pencil": {"pal": "navy", "waist": {"S": "123334", "N": "123334", "W": "12334"}, "legs": None,
               "skirt": [("S", 0, "233344")]},
    "pleated": {"pal": "wine", "waist": {"S": "123334", "N": "123334", "W": "12334"}, "legs": None,
                "skirt": [("S", 1, "12132434"), ("S", 2, "1213243424")]},
}
NEIGH = ((1, 0), (-1, 0), (0, 1), (0, -1))


def torso_box(f):
    pts = [p for p, l in f.lab.items() if l == "torso" and f.px[p] != "o"]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


def sym_color(spec, ch, default_pal):
    if ch in ".":
        return None
    if ch.isdigit():
        return (default_pal, int(ch))
    return spec.get("sym", {}).get(ch)


def paint_layer(cells, f, extras_outline=True):
    """cells: {(x,y): (palette key, tone)} -> RGBA image. Outline for garment pixels that stick out of the body."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    solid = set(cells)
    body_fill = {p for p, c in f.px.items() if c != "o"}
    for (x, y), (pk, t) in cells.items():
        im.putpixel((x, y), tuple(int(PAL[pk][t][i:i + 2], 16) for i in (1, 3, 5)) + (255,))
    if extras_outline:
        extra = {p for p in solid if p not in body_fill}
        for (x, y) in extra:
            pk = cells[(x, y)][0]
            for ox, oy in NEIGH:
                n = (x + ox, y + oy)
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in solid and n not in body_fill and f.px.get(n) != "o":
                    im.putpixel(n, tuple(int(PAL[pk][OLINE][i:i + 2], 16) for i in (1, 3, 5)) + (255,))
    return im


def blocked(f):
    """Pixels garments must not overwrite: hands (and the ring around them) stay above everything."""
    return set(f.top)


def add_skirt(cells, spec, view, x0, y0, cols):
    pal = spec["pal"]
    for kind, off, tones in spec.get("skirt", []):
        y = y0 + 4 + off
        n = len(tones)
        sx0 = x0 - (n - cols) // 2
        for i, ch in enumerate(tones):
            cells[(sx0 + i, y)] = (pal, int(ch))


def top_layer(name, view, f, dy=0):
    spec = TOPS[name]
    x0, x1, y0, y1 = torso_box(f)
    cols = 5 if view == "W" else 6
    grid = spec["W" if view == "W" else ("N" if view == "N" else "S")]
    cells = {}
    for (x, y), lab in f.lab.items():
        if lab != "torso" or f.px[(x, y)] == "o":
            continue
        r = min(max(y - y0, 0), 3)
        if y - y0 >= 4:           # row 4 belongs to the bottom
            continue
        c = min(max(x - x0, 0), cols - 1)
        col = sym_color(spec, grid[r][c], spec["pal"])
        if col:
            cells[(x, y)] = col
    if spec["sleeve"]:
        for (x, y), lab in f.lab.items():
            if lab == "arm" and f.px[(x, y)] != "o":
                cells[(x, y)] = (spec["pal"], spec["sleeve"][0] if x < 8 else spec["sleeve"][1])
    if spec.get("waist"):             # a dress also covers the waist row and has a skirt
        waist = spec["waist"]["W" if view == "W" else ("N" if view == "N" else "S")]
        for (x, y), lab in f.lab.items():
            if lab == "torso" and f.px[(x, y)] != "o" and y - y0 >= 4:
                cells[(x, y)] = (spec["pal"], int(waist[min(max(x - x0, 0), cols - 1)]))
        add_skirt(cells, spec, view, x0, y0, cols)
    for p in blocked(f):
        cells.pop(p, None)
    return paint_layer(cells, f, extras_outline=bool(spec.get("skirt")))


def bottom_layer(name, view, f):
    spec = BOTTOMS[name]
    pal = spec["pal"]
    x0, x1, y0, y1 = torso_box(f)
    cols = 5 if view == "W" else 6
    cells = {}
    waist = spec["waist"]["W" if view == "W" else ("N" if view == "N" else "S")]
    for (x, y), lab in f.lab.items():
        if lab == "torso" and f.px[(x, y)] != "o" and y - y0 >= 4:
            c = min(max(x - x0, 0), cols - 1)
            cells[(x, y)] = (pal, int(waist[c]))
    if spec["legs"]:
        legs = {p for p, l in f.lab.items() if l == "leg" and f.px[p] != "o"}
        for (x, y) in legs:
            tone = int(f.px[(x, y)])
            below = (x, y + 1) not in legs
            above = (x, y - 1) not in legs
            if spec["legs"] == "top" and not above:
                pass
            elif spec["legs"] == "top":
                continue
            t = min(max(tone, 1), 4)
            if below and spec.get("cuff"):
                t = min(max(t + spec["cuff"], 0), 4)
            cells[(x, y)] = (pal, t)
    add_skirt(cells, spec, view, x0, y0, cols)
    for p in blocked(f):
        cells.pop(p, None)
    return paint_layer(cells, f, extras_outline=True)
