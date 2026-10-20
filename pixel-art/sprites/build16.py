"""Character kit v6 — build the native 16x32 sprite sheets: approved body + new hair, tops, bottoms.

Poses idle (2) / walk (4) / sit (1) / talk (2) / wave (2), views S N W (E = W mirrored) -> 20 rows x 4 columns
of 16x32 cells. One transparent sheet per layer; stack them in this order:
    hair_<style>_back -> body_<tone> -> bottom_<name> -> top_<name> -> face -> hair_<style>
Hair is rendered with the 3D hair rig on a 16x32 canvas (canvas16.py), garments with outfit16.py.
Outputs in character/sheets16/ (sheets, character16.json, preview/).
"""
import canvas16  # noqa: F401  (must be first: points the rasteriser at the 16x32 canvas)
import json
from pathlib import Path

import numpy as np
from PIL import Image

import character16_anim as A
import hair32_front as H0
import hair32_rig as HR
import outfit16 as O
from kit import floor_bg

OUT = Path(__file__).parent / "character" / "sheets16"
(OUT / "preview").mkdir(parents=True, exist_ok=True)
W, H = A.W, A.H
COLS = A.COLS
DIRS = A.DIRS
ROWS = [(a, d) for a in A.ANIMS for d in DIRS]
ROW = {r: i for i, r in enumerate(ROWS)}
HAIR_COLOR = "black"

H0.FRINGE_ALPHA = (52, 0)   # at 16x32 one faint row is enough

# the 16-px wide head cannot carry a shell wider than the head
for st in HR.STYLES.values():
    for it in st.get("front", []) + st.get("back", []):
        if it[0] == "shell":
            it[1]["rx"] = min(it[1]["rx"], 13.0)


def blank():
    return Image.new("RGBA", (COLS * W, len(ROWS) * H), (0, 0, 0, 0))


def put(sheet, im, anim, d, i):
    if im is None:
        return
    if d == "E":
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    sheet.alpha_composite(im, (i * W, ROW[(anim, d)] * H))


def shifted(im, dy):
    if im is None or dy == 0:
        return im
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    if dy > 0:
        out.alpha_composite(im, (0, dy))
    else:
        out.alpha_composite(im.crop((0, -dy, im.width, im.height)), (0, 0))
    return out


def cut(im, pixels):
    if im is None:
        return None
    a = np.array(im)
    for (x, y) in pixels:
        if 0 <= x < W and 0 <= y < H:
            a[y, x] = 0
    return Image.fromarray(a)


if __name__ == "__main__":
    sheets = {"face": blank()}
    for t in A.TONES:
        sheets[f"body_{t}"] = blank()
    for s in HR.STYLES:
        sheets[f"hair_{s}"] = blank()
        sheets[f"hair_{s}_back"] = blank()
    for n in O.TOPS:
        sheets[f"top_{n}"] = blank()
    for n in O.BOTTOMS:
        sheets[f"bottom_{n}"] = blank()

    # hair is rendered once per (style, view) on the rest pose, then shifted with the head bob
    hair = {}
    for view in ("S", "N", "W"):
        f0, _, _ = A.build(view, A.ANIMS["idle"][2][view][0])
        skin = np.zeros((H, W), bool)
        for (x, y), c in f0.px.items():
            skin[y, x] = c != "o"
        for s in HR.STYLES:
            hair[(s, view)] = HR.render_style(s, view, skin, H0.COLORS[HAIR_COLOR])

    for anim, (ms, loop, dirs) in A.ANIMS.items():
        for view in ("S", "N", "W"):
            for i, spec in enumerate(dirs[view]):
                f, face, dy = A.build(view, spec)
                for d in ([view] + (["E"] if view == "W" else [])):
                    for t, tone in A.TONES.items():
                        put(sheets[f"body_{t}"], A.paint(f, tone), anim, d, i)
                    put(sheets["face"], A.paint_face(face), anim, d, i)
                    for n in O.TOPS:
                        put(sheets[f"top_{n}"], O.top_layer(n, view, f), anim, d, i)
                    for n in O.BOTTOMS:
                        put(sheets[f"bottom_{n}"], O.bottom_layer(n, view, f), anim, d, i)
                    for s in HR.STYLES:
                        hf, hb = hair[(s, view)]
                        put(sheets[f"hair_{s}"], cut(shifted(hf, dy), f.top), anim, d, i)
                        put(sheets[f"hair_{s}_back"], shifted(hb, dy), anim, d, i)
        print("done", anim, flush=True)

    for name, sh in sheets.items():
        sh.save(OUT / f"{name}.png")
    meta = {"frame": [W, H], "columns": COLS, "anchor": [8, 30],
            "drawOrder": ["hair_<style>_back", "body_<tone>", "bottom_<name>", "top_<name>", "face", "hair_<style>"],
            "note": "E rows are the W rows mirrored; hair is already shifted with the head bob (headDy).",
            "tones": list(A.TONES), "hairStyles": {s: {"name": v["name"], "gender": v["gender"]} for s, v in HR.STYLES.items()},
            "tops": list(O.TOPS), "bottoms": list(O.BOTTOMS), "animations": {}}
    for anim, (ms, loop, dirs) in A.ANIMS.items():
        meta["animations"][anim] = {"msPerFrame": ms, "loop": loop, "directions": {}}
        for d in DIRS:
            src = "W" if d == "E" else d
            frames = []
            for i, spec in enumerate(dirs[src]):
                dy = spec.get("dy", 0)
                frames.append({"x": i * W, "y": ROW[(anim, d)] * H, "w": W, "h": H, "headDy": dy, "bodyDy": dy})
            meta["animations"][anim]["directions"][d] = {"row": ROW[(anim, d)], "frames": frames}
    (OUT / "character16.json").write_text(json.dumps(meta, indent=2))

    def stacked(hair_s, top, bottom, tone="medium"):
        im = blank()
        for layer in ([f"hair_{hair_s}_back", f"body_{tone}"] + ([f"bottom_{bottom}"] if bottom else []) +
                      ([f"top_{top}"] if top else []) + ["face", f"hair_{hair_s}"]):
            im.alpha_composite(sheets[layer])
        return im

    outfits = [stacked("up", "tee", "jeans"), stacked("hime", "dress", None)]
    gap = 4

    def cell(sh, anim, d, i):
        r = ROW[(anim, d)]
        return sh.crop((i * W, r * H, i * W + W, r * H + H))

    for anim, (ms, loop, dirs) in A.ANIMS.items():
        n = max(len(v) for v in dirs.values())
        frames = []
        for i in range(n):
            bg = floor_bg(gap + 4 * (W + gap), gap + 2 * (H + gap))
            for o, sh in enumerate(outfits):
                for k, d in enumerate(DIRS):
                    bg.alpha_composite(cell(sh, anim, d, i), (gap + k * (W + gap), gap + o * (H + gap)))
            frames.append(bg.resize((bg.width * 8, bg.height * 8), Image.NEAREST).convert("RGB"))
        if len(frames) == 1:
            frames[0].save(OUT / "preview" / f"{anim}.gif")
        else:
            frames[0].save(OUT / "preview" / f"{anim}.gif", save_all=True, append_images=frames[1:], duration=ms, loop=0)
    full = outfits[0]
    bg = floor_bg(full.width + 8, full.height + 8)
    bg.alpha_composite(full, (4, 4))
    bg.resize((bg.width * 5, bg.height * 5), Image.NEAREST).convert("RGB").save(OUT / "preview" / "sheet-preview.png")
    print("ok", len(sheets), "sheets")
