"""Character kit v3 — HAIR layers for the 16x32 chibi (character16.py / character16_anim.py).

6 styles (3 men, 3 women), each drawn for the front (S), back (N) and side (W) head; E = W mirrored.
Hair is drawn at head offset 0, then shifted by every frame's headDy so it rides the idle / walk /
sit bob exactly. Long styles also have a BACK layer that sits behind the body (strands behind the
shoulders). Hands are cut out of the front layer so a waving / typing hand always reads above hair.

Outline rule: the dark ring goes around the hair silhouette and under the fringe, but NOT along the
sides where hair lies on the face (there the hair colour vs skin is the edge) — keeps blush + eyes clear.

Draw order per cell:  hair back  ->  body  ->  face  ->  hair front

Outputs in ./character/hair/:
  hair16_<style>_<color>.png        front layer, same 4x20 cell layout as body16_anim.png
  hair16_<style>_<color>_back.png   back layer (long hair only)
  hair16.json                       styles, gender, colors, layers, draw order
  hair16-preview.png                every style x 4 directions on the body
  hair16-colors.png                 every style in every colour
  preview/<anim>.gif                each animation with all 6 styles
"""
import json
from pathlib import Path

from PIL import Image

import character16_anim as body
from kit import OL, floor_bg, hx

OUT = Path(__file__).parent / "character" / "hair"
(OUT / "preview").mkdir(parents=True, exist_ok=True)
W, H = body.W, body.H

COLORS = {  # 4 tones: highlight, base, shade, deep
    "black":  ["#6c6890", "#4a4668", "#35324f", "#24223a"],
    "brown":  ["#b07a50", "#8a5634", "#683e22", "#4a2a16"],
    "blonde": ["#fff0b0", "#f4cc70", "#d8a44c", "#b07e34"],
    "auburn": ["#e8805a", "#bc5232", "#923822", "#682416"],
    "pink":   ["#ffd0e0", "#f79cbc", "#dc7298", "#b45276"],
}
TIE = ["#ff4d5a", "#D70010"]  # bun hair-tie in Gastron red

# fill templates: 1 light, 2 base, 3 shade, 4 deep, r/R hair tie, . empty — {view: (first row, rows)}
STYLES = {
    # ------------------------------------------------------------------ men
    "short": {"gender": "male", "name": "Short Crop", "default": "black", "views": {
        "S": (8, [
            "....12222222....",
            "...1122222223...",
            "..112222222233..",
            ".11222222222233.",
            ".12222222222333.",
            ".22222222222333.",
            ".23222322232333.",
            ".22.2.....2..33.",
        ]),
        "N": (8, [
            "....12222222....",
            "...1122222223...",
            "..112222222233..",
            ".11222222222233.",
            ".12222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            "..222222222233..",
            "..222222222333..",
            "..322222223333..",
            "...3333333333...",
        ]),
        "W": (8, [
            ".....1222222....",
            "....112222223...",
            "...11222222233..",
            "..1122222222333.",
            "..1222222222333.",
            ".12222222222333.",
            ".22232222222333.",
            "..2..22.2223333.",
            "......2....2333.",
            "...........3333.",
            "...........333..",
            "...........33...",
        ]),
    }},
    "spiky": {"gender": "male", "name": "Spiky", "default": "brown", "views": {
        "S": (5, [
            "....2...2...2...",
            "...12..12..223..",
            "..1122.1222.233.",
            ".11222222222233.",
            ".12222222222233.",
            ".12222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".23223223223333.",
            ".2.2..2..2..3.3.",
        ]),
        "N": (5, [
            "....2...2...2...",
            "...12..12..223..",
            "..1122.1222.233.",
            ".11222222222233.",
            ".12222222222233.",
            ".12222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            "..222222222233..",
            "..222222222333..",
            "..322222223333..",
            "...3.33.33.33...",
        ]),
        "W": (5, [
            "........2...2...",
            ".....2..22..22..",
            "....122.222.233.",
            "...112222222233.",
            "...11222222233..",
            "..1122222222333.",
            "..1222222222333.",
            ".12222222222333.",
            ".22232222222333.",
            ".2.2.22.2223333.",
            "......2....2333.",
            "...........3333.",
            "...........333..",
            "...........3.3..",
        ]),
    }},
    "sidepart": {"gender": "male", "name": "Side Swept", "default": "auburn", "views": {
        "S": (8, [
            "....12222222....",
            "...11222222423..",
            "..112222222433..",
            ".11222222224333.",
            ".12222222222333.",
            ".22222222222333.",
            ".2222222223..33.",
            ".222222.....33..",
            ".2..............",
        ]),
        "N": (8, [
            "....12222222....",
            "...11222222423..",
            "..112222222433..",
            ".11222222224333.",
            ".12222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            "..222222222233..",
            "..222222222333..",
            "..322222223333..",
            "...3333333333...",
        ]),
        "W": (8, [
            ".....1222222....",
            "....112222223...",
            "...11222222233..",
            "..1122222222333.",
            ".11222222222333.",
            ".12222222222333.",
            ".22222222222333.",
            ".22.322.2223333.",
            ".2....2....2333.",
            "...........3333.",
            "...........333..",
            "...........33...",
        ]),
    }},
    # ---------------------------------------------------------------- women
    "bob": {"gender": "female", "name": "Bob", "default": "black", "views": {
        "S": (8, [
            "....12222222....",
            "...1122222223...",
            "..112222222233..",
            ".11222222222233.",
            ".12222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".23333333333333.",
            ".22..........33.",
            ".22..........33.",
            ".22..........33.",
            ".22..........33.",
            ".223........333.",
            "..33........33..",
        ]),
        "N": (8, [
            "....12222222....",
            "...1122222223...",
            "..112222222233..",
            ".11222222222233.",
            ".12222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".23222222222333.",
            "..333333333333..",
        ]),
        "W": (8, [
            ".....1222222....",
            "....112222223...",
            "...11222222233..",
            "..1122222222333.",
            "..1222222222333.",
            ".12222222222333.",
            ".22222222222333.",
            ".2333.222222333.",
            "......222222333.",
            "......222222333.",
            "......222222333.",
            "......22222233..",
            "......32222333..",
            ".......33333....",
        ]),
    }},
    "long": {"gender": "female", "name": "Long Straight", "default": "brown", "views": {
        "S": (8, [
            "....12222222....",
            "...1122222223...",
            "..112222222233..",
            ".11222222222233.",
            ".12222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".2233.....33233.",
            ".22..........33.",
            ".22..........33.",
            ".22..........33.",
            ".22..........33.",
            ".22..........33.",
            ".22..........33.",
            ".22..........33.",
            ".23..........33.",
        ]),
        "S_back": (16, [
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".23222222222333.",
            ".33222222222334.",
            ".33322222223344.",
            "..3.3333333.34..",
        ]),
        "N": (8, [
            "....12222222....",
            "...1122222223...",
            "..112222222233..",
            ".11222222222233.",
            ".12222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            "..222222222233..",
            "...2222222233...",
            "....22222223....",
            "....22222233....",
            "....23222233....",
            "....3.3333.3....",
        ]),
        "W": (8, [
            ".....1222222....",
            "....112222223...",
            "...11222222233..",
            "..1122222222333.",
            "..1222222222333.",
            ".12222222222333.",
            ".22222222222333.",
            ".2333.2...22333.",
            "..........22333.",
            "..........22333.",
            "..........22333.",
            "..........22333.",
            "..........22333.",
            "..........22333.",
            "..........22333.",
        ]),
        "W_back": (18, [
            "..........22333.",
            "..........22333.",
            "..........22333.",
            "..........22333.",
            "..........22333.",
            "..........22333.",
            "..........22333.",
            "..........22334.",
            "..........23334.",
            "..........3.34..",
        ]),
    }},
    "bun": {"gender": "female", "name": "High Bun", "default": "blonde", "views": {
        "S": (3, [
            "......1222......",
            ".....112223.....",
            ".....122233.....",
            "......2333......",
            "......rRRR......",
            "....12222222....",
            "...1122222223...",
            "..112222222233..",
            ".11222222222233.",
            ".12222222222333.",
            ".22222222222333.",
            ".23..........33.",
            ".2............3.",
            ".2............3.",
            ".2............3.",
            ".3............3.",
        ]),
        "N": (3, [
            "......1222......",
            ".....112223.....",
            ".....122233.....",
            "......2333......",
            "......rRRR......",
            "....12222222....",
            "...1122222223...",
            "..112222222233..",
            ".11222222222233.",
            ".12222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            ".22222222222333.",
            "..222222222233..",
            "..222222222333..",
            "..322222223333..",
        ]),
        "W": (3, [
            "..........122...",
            ".........11223..",
            ".........12233..",
            "..........333...",
            ".........rRR....",
            ".....1222222....",
            "....112222223...",
            "...11222222233..",
            "..1122222222333.",
            "..1222222222333.",
            ".12222222222333.",
            ".22232222222333.",
            "..3...2.2223333.",
            "......2....2333.",
            "......3....3333.",
            "...........333..",
            "...........33...",
        ]),
    }},
}
NB4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def head_mask(view):
    rows = {"S": body.HEAD_FRONT, "N": body.HEAD_BACK, "W": body.HEAD_SIDE}[view]
    return {(x, 11 + y) for y, r in enumerate(rows) for x, c in enumerate(r) if c != "."}


def cells(view_def):
    y0, rows = view_def
    out = {}
    for j, r in enumerate(rows):
        assert len(r) == W, (y0 + j, r, len(r))
        for i, c in enumerate(r):
            if c != ".":
                out[(i, y0 + j)] = c
    return out


def render(fill, color, head, back=False):
    """Fill + outline ring. On the face, only the edge *below* hair (the fringe line) is outlined."""
    px = dict(fill)
    for (x, y) in fill:
        for ox, oy in NB4:
            n = (x + ox, y + oy)
            if n in fill or not (0 <= n[0] < W and 0 <= n[1] < H):
                continue
            if not back and n in head and oy != 1:
                continue  # hair lying on the face at the sides: no dark line
            px[n] = "o"
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pal = {"o": hx(OL), "1": hx(color[0]), "2": hx(color[1]), "3": hx(color[2]), "4": hx(color[3]),
           "r": hx(TIE[0]), "R": hx(TIE[1])}
    for (x, y), c in px.items():
        im.putpixel((x, y), pal[c] + (255,))
    return im


def shifted(im, dy):
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(im, (0, dy)) if dy >= 0 else out.alpha_composite(im.crop((0, -dy, W, H)), (0, 0))
    return out


def cut(im, holes):
    im = im.copy()
    for (x, y) in holes:
        if 0 <= x < W and 0 <= y < H:
            im.putpixel((x, y), (0, 0, 0, 0))
    return im


if __name__ == "__main__":
    rows = [(a, d) for a in body.ANIMS for d in body.DIRS]
    frames = {}  # (anim, dir) -> [(top-set, dy)]
    for a, (_, _, dirs) in body.ANIMS.items():
        for d in body.DIRS:
            src = "W" if d == "E" else d
            out = []
            for spec in dirs[src]:
                f, _, dy = body.build(src, spec)
                top = {(W - 1 - x, y) for x, y in f.top} if d == "E" else f.top
                out.append((top, dy))
            frames[(a, d)] = out
    heads = {v: head_mask(v) for v in ("S", "N", "W")}

    def layer(style, color, back):
        """Aligned sheet for one style/colour/layer, or None if the style has no such layer."""
        views = STYLES[style]["views"]
        key = (lambda v: v + "_back") if back else (lambda v: v)
        if back and not any(key(v) in views for v in ("S", "N", "W")):
            return None
        base = {}
        for v in ("S", "N", "W"):
            base[v] = render(cells(views[key(v)]), COLORS[color], heads[v], back) if key(v) in views else None
        sheet = Image.new("RGBA", (body.COLS * W, len(rows) * H), (0, 0, 0, 0))
        for r, (a, d) in enumerate(rows):
            src = base["W" if d == "E" else d]
            if src is None:
                continue
            src = src.transpose(Image.FLIP_LEFT_RIGHT) if d == "E" else src
            for c, (top, dy) in enumerate(frames[(a, d)]):
                cell = shifted(src, dy)
                if not back:
                    cell = cut(cell, top)
                sheet.alpha_composite(cell, (c * W, r * H))
        return sheet

    sheets = {}
    for s in STYLES:
        for col in COLORS:
            for back in (False, True):
                sh = layer(s, col, back)
                if sh is not None:
                    sh.save(OUT / f"hair16_{s}_{col}{'_back' if back else ''}.png")
                    sheets[(s, col, back)] = sh

    meta = {
        "frameLayout": "same cells as character/anim/body16_anim.json (4 columns x 20 rows)",
        "drawOrder": ["hair back", "body", "face", "hair front"],
        "file": "hair16_<style>_<color>.png, back layer: hair16_<style>_<color>_back.png",
        "colors": COLORS,
        "styles": {s: {"name": v["name"], "gender": v["gender"], "defaultColor": v["default"],
                       "hasBack": (s, "black", True) in sheets} for s, v in STYLES.items()},
    }
    (OUT / "hair16.json").write_text(json.dumps(meta, indent=2))

    # ---------------------------------------------------------------- previews
    tone = body.TONES[body.DEFAULT]
    bsheet = Image.open(body.OUT / "body16_anim.png")
    fsheet = Image.open(body.OUT / "face16_anim.png")

    def dressed(style, color, r, c):
        box = (c * W, r * H, c * W + W, r * H + H)
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if (style, color, True) in sheets:
            im.alpha_composite(sheets[(style, color, True)].crop(box))
        im.alpha_composite(bsheet.crop(box))
        im.alpha_composite(fsheet.crop(box))
        im.alpha_composite(sheets[(style, color, False)].crop(box))
        return im

    idle_rows = {d: rows.index(("idle", d)) for d in body.DIRS}
    gap = 4
    names = list(STYLES)
    w = gap + (len(body.DIRS) * (W + 2) + gap) * 3
    bg = floor_bg(w, gap + 2 * (H + gap))
    for i, s in enumerate(names):  # 2 rows (men / women) x 3 styles x 4 directions
        gx = gap + (i % 3) * (len(body.DIRS) * (W + 2) + gap)
        gy = gap + (i // 3) * (H + gap)
        for k, d in enumerate(body.DIRS):
            bg.alpha_composite(dressed(s, STYLES[s]["default"], idle_rows[d], 0), (gx + k * (W + 2), gy))
    bg.resize((bg.width * 6, bg.height * 6), Image.NEAREST).convert("RGB").save(OUT / "hair16-preview.png")

    # colour range: rows = styles, columns = colours (front, idle)
    bg = floor_bg(gap + len(COLORS) * (W + gap), gap + len(names) * (H + gap))
    for i, s in enumerate(names):
        for j, col in enumerate(COLORS):
            bg.alpha_composite(dressed(s, col, idle_rows["S"], 0), (gap + j * (W + gap), gap + i * (H + gap)))
    bg.resize((bg.width * 6, bg.height * 6), Image.NEAREST).convert("RGB").save(OUT / "hair16-colors.png")

    for a, (ms, _, dirs) in body.ANIMS.items():
        n = max(len(v) for v in dirs.values())
        per = []
        for s in names:
            for d in ("S", "W"):
                r = rows.index((a, d))
                per.append([dressed(s, STYLES[s]["default"], r, c) for c in range(len(frames[(a, d)]))])
        body.gif(per, ms, OUT / "preview" / f"{a}.gif", scale=6, gap=3)
    print("ok", len(sheets), "sheets")
