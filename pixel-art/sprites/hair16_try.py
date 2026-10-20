import canvas16  # must come first
import sys
import numpy as np
from PIL import Image
import character32_front as B
import hair32_front as H0
import hair32_rig as HR
from kit import floor_bg

SC = "/private/tmp/claude-501/-Volumes-ALT-04-Freelance-Work-Gastron-00-Asset--GASTRON--Digital-Marketing-AI-Team/5212fcad-7e8e-4262-8429-08a6067c4155/scratchpad/"
body = Image.open("character/anim/body16_anim.png").convert("RGBA")
face = Image.open("character/anim/face16_anim.png").convert("RGBA")
ROW = {"S": 0, "N": 1, "W": 2}   # idle rows: S, N, W, E
def cell(sheet, row, col=0):
    return sheet.crop((col * 16, row * 32, col * 16 + 16, row * 32 + 32))
for st in HR.STYLES.values():
    for k in ("front", "back"):
        for it in st.get(k, []):
            if it[0] == "shell":
                it[1]["rx"] = min(it[1]["rx"], 13.0)
pal = H0.COLORS["black"]
gap = 2
bg = floor_bg(gap + 6 * 3 * 18, 36)
for i, s in enumerate(HR.STYLES):
    for j, v in enumerate(("S", "N", "W")):
        b = cell(body, ROW[v]); fc = cell(face, ROW[v])
        skin = np.array(b)[..., 3] == 255
        f, bk = HR.render_style(s, v, skin, pal)
        im = Image.new("RGBA", (16, 32), (0, 0, 0, 0))
        if bk is not None: im.alpha_composite(bk)
        im.alpha_composite(b); im.alpha_composite(fc); im.alpha_composite(f)
        bg.alpha_composite(im, (gap + (i * 3 + j) * 18, 2))
bg.resize((bg.width * 7, bg.height * 7), Image.NEAREST).convert("RGB").save(SC + "h16_try.png")
print(bg.size)
