import json, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, ".")
from kit import floor_bg
D = Path("character/sheets16")
SC = "/private/tmp/claude-501/-Volumes-ALT-04-Freelance-Work-Gastron-00-Asset--GASTRON--Digital-Marketing-AI-Team/5212fcad-7e8e-4262-8429-08a6067c4155/scratchpad/"
meta = json.load(open(D / "character16.json"))
L = {}
def layer(n):
    if n not in L: L[n] = Image.open(D / f"{n}.png").convert("RGBA")
    return L[n]
def cell(name, anim, d, i):
    fr = meta["animations"][anim]["directions"][d]["frames"][i]
    return layer(name).crop((fr["x"], fr["y"], fr["x"] + 16, fr["y"] + 32))
def dressed(h, t, b, anim, d, i, tone="medium"):
    im = Image.new("RGBA", (16, 32), (0, 0, 0, 0))
    names = [f"hair_{h}_back", f"body_{tone}"] + ([f"bottom_{b}"] if b else []) + ([f"top_{t}"] if t else []) + ["face", f"hair_{h}"]
    for n in names: im.alpha_composite(cell(n, anim, d, i))
    return im
outfits = [("neat", "shirt", "slacks"), ("up", "tee", "jeans"), ("hime", "dress", None), ("ponytail", "tank", "shorts"), ("short", "suit", "pencil"), ("sidepart", "tee", "pleated")]
frames = [("idle", "S", 0), ("idle", "N", 0), ("idle", "W", 0), ("walk", "S", 0), ("walk", "W", 0), ("sit", "S", 0), ("sit", "W", 0), ("talk", "S", 1), ("wave", "S", 0), ("wave", "W", 1)]
gap = 2
bg = floor_bg(gap + len(frames) * 17, gap + len(outfits) * 34)
for r, (h, t, b) in enumerate(outfits):
    for c, (a, d, i) in enumerate(frames):
        bg.alpha_composite(dressed(h, t, b, a, d, i), (gap + c * 17, gap + r * 34))
bg.resize((bg.width * 7, bg.height * 7), Image.NEAREST).convert("RGB").save(SC + "qa16.png")
print(bg.size)
