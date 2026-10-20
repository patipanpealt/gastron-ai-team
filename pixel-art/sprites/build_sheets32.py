"""Character kit v5 — build the 32x64 SPRITE SHEETS for every pose.

Poses   idle (2) · walk (4) · sit (1, still) · talk (2) · wave (2)
Views   S front · N back · W side · E = W mirrored      -> 20 rows x 4 columns of 32x64 cells

One transparent sheet per LAYER, all with the same cell layout so a game just stacks them
(hair back -> body -> bottom -> top -> face -> hair front):

  character32/sheets/body_<tone>.png      4 skin tones
  character32/sheets/face.png             eyes, blush, mouth (open mouth on talk / wave frames)
  character32/sheets/hair_<style>.png     front layer  (hair over the body)
  character32/sheets/hair_<style>_back.png  back layer (hair behind the body)
  character32/sheets/top_<name>.png       5 tops
  character32/sheets/bottom_<name>.png    5 bottoms
  character32/sheets/character32.json     cell rects, timings, per-frame head / torso offsets, layer order
  character32/sheets/preview/*.gif        each animation, 4 directions, two sample outfits
  character32/sheets/preview/sheet-preview.png   the whole dressed sheet
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

import character32_front as B
import compose32 as K
import hair32_front as H0
import hair32_rig as HR
import outfit32_rig as O
import rig32 as R
from kit import floor_bg

OUT = B.OUT / "sheets"
(OUT / "preview").mkdir(parents=True, exist_ok=True)
W, H = R.W, R.H
COLS = max(n for _, _, n in R.ANIMS.values())
DIRS = ["S", "N", "W", "E"]
ROWS = [(a, d) for a in R.ANIMS for d in DIRS]
ROW = {r: i for i, r in enumerate(ROWS)}


def blank():
    return Image.new("RGBA", (COLS * W, len(ROWS) * H), (0, 0, 0, 0))


def put(sheet, im, anim, d, f):
    if im is None:
        return
    if d == "E":
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    sheet.alpha_composite(im, (f * W, ROW[(anim, d)] * H))


if __name__ == "__main__":
    sheets = {"face": blank()}
    for t in B.TONES:
        sheets[f"body_{t}"] = blank()
    for s in HR.STYLES:
        sheets[f"hair_{s}"] = blank()
        sheets[f"hair_{s}_back"] = blank()
    for n in O.TOPS:
        sheets[f"top_{n}"] = blank()
    for n in O.BOTTOMS:
        sheets[f"bottom_{n}"] = blank()
    meta_frames = {}

    for view in ("S", "N", "W"):
        rest = R.render_body(view, R.pose_for("idle", 0, view))
        rest_skin = rest["tone"] >= 0
        for anim, (ms, loop, n) in R.ANIMS.items():
            for f in range(n):
                pose = R.pose_for(anim, f, view)
                body = R.render_body(view, pose)
                dirs = [view] + (["E"] if view == "W" else [])
                for d in dirs:
                    for t, pal in B.TONES.items():
                        put(sheets[f"body_{t}"], B.paint(body["tone"], pal), anim, d, f)
                    put(sheets["face"], body["face"], anim, d, f)
                    meta_frames[(anim, d, f)] = {"hy": pose["hy"], "ty": pose["ty"], "mouthOpen": bool(pose["mouth"])}
                for nme in O.TOPS:
                    im = O.render_garment("top", nme, view, pose, body)
                    for d in dirs:
                        put(sheets[f"top_{nme}"], im, anim, d, f)
                for nme in O.BOTTOMS:
                    im = O.render_garment("bottom", nme, view, pose, body)
                    for d in dirs:
                        put(sheets[f"bottom_{nme}"], im, anim, d, f)
                for s in HR.STYLES:
                    hf, hb = K.hair_layers(s, view, rest_skin)
                    hy = pose["hy"]
                    hf, hb = K.shifted(hf, hy), K.shifted(hb, hy)
                    if pose["arm_front"]:
                        grp, rank = body["grp"], body["rank"]
                        hf = K.cut_alpha(hf, (grp == "arm") & (rank > rank[grp == "head"].max()))
                    for d in dirs:
                        put(sheets[f"hair_{s}"], hf, anim, d, f)
                        put(sheets[f"hair_{s}_back"], hb, anim, d, f)
            print("done", view, anim, flush=True)

    for name, sh in sheets.items():
        sh.save(OUT / f"{name}.png")

    meta = {
        "frame": [W, H], "columns": COLS, "anchor": [16, 62],
        "drawOrder": ["hair_<style>_back", "body_<tone>", "bottom_<name>", "top_<name>", "face", "hair_<style>"],
        "note": "E rows are the W rows mirrored. hy = head/hair/face offset this frame, ty = torso offset. "
                "All layers are already aligned per cell; just stack them.",
        "tones": list(B.TONES), "hairStyles": {s: {"name": v["name"], "gender": v["gender"]} for s, v in HR.STYLES.items()},
        "tops": list(O.TOPS), "bottoms": list(O.BOTTOMS), "animations": {},
    }
    for anim, (ms, loop, n) in R.ANIMS.items():
        meta["animations"][anim] = {"msPerFrame": ms, "loop": loop, "directions": {}}
        for d in DIRS:
            meta["animations"][anim]["directions"][d] = {
                "row": ROW[(anim, d)],
                "frames": [{"x": f * W, "y": ROW[(anim, d)] * H, "w": W, "h": H, **meta_frames[(anim, d, f)]}
                           for f in range(n)],
            }
    (OUT / "character32.json").write_text(json.dumps(meta, indent=2))

    # ---- previews: stack the layers from the saved sheets (what a game would do) ---------------------------
    def stacked(hair, top, bottom, tone="medium"):
        out = blank()
        for layer in (f"hair_{hair}_back", f"body_{tone}", f"bottom_{bottom}", f"top_{top}", "face", f"hair_{hair}"):
            out.alpha_composite(sheets[layer])
        return out

    outfits = [stacked("up", "tee", "jeans"), stacked("hime", "dress", "pencil")]
    gap = 4

    def cell(sheet, anim, d, f):
        r = ROW[(anim, d)]
        return sheet.crop((f * W, r * H, f * W + W, r * H + H))

    for anim, (ms, loop, n) in R.ANIMS.items():
        frames = []
        for f in range(max(n, 1)):
            bg = floor_bg(gap + 4 * (W + gap), gap + 2 * (H + gap))
            for o, sh in enumerate(outfits):
                for k, d in enumerate(DIRS):
                    bg.alpha_composite(cell(sh, anim, d, f), (gap + k * (W + gap), gap + o * (H + gap)))
            frames.append(bg.resize((bg.width * 5, bg.height * 5), Image.NEAREST).convert("RGB"))
        if len(frames) == 1:
            frames[0].save(OUT / "preview" / f"{anim}.gif")
        else:
            frames[0].save(OUT / "preview" / f"{anim}.gif", save_all=True, append_images=frames[1:], duration=ms, loop=0)

    full = outfits[0]
    bg = floor_bg(full.width + 8, full.height + 8)
    bg.alpha_composite(full, (4, 4))
    bg.resize((bg.width * 3, bg.height * 3), Image.NEAREST).convert("RGB").save(OUT / "preview" / "sheet-preview.png")
    print("ok", len(sheets), "sheets")
