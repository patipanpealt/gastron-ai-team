"""Character kit v3 — ANIMATION sheets for the 16x32 chibi base body (character16.py).

The body is assembled per frame from parts (legs, torso, hands, head) drawn as fill-only templates;
the dark outline is added automatically around the union silhouette, and hands/legs that overlap the
body are "stamped" with their own outline ring so they read on top of it. Light from the upper-left.

Animations (4 directions — S front, N back, W left, E = W mirrored):
  idle  2 frames   breathing: head + torso sink 1 px
  walk  4 frames   step L · pass · step R · pass, body rises 1 px on the lifted-leg frames
  sit   1 frame    seated still (hands resting forward on the desk); S/N/W/E to match the desk + chair
  talk  2 frames   gesture hand + open mouth (face layer)
  wave  2 frames   one hand raised beside the head, waving

Outputs in ./character/anim/:
  body16_anim.png / body16_anim_<tone>.png   sheet: one row per (anim, dir), 4 columns of 16x32 cells
  face16_anim.png                            face layer aligned to every frame (eyes, blush, talk mouth)
  body16_anim.json                           cell rects, frame durations, loop flags, and per-frame
                                             head/body offsets so hair + outfit layers can follow the bob
  body16_anim_x2.png                         default sheet pixel-doubled (32 px furniture grid)
  preview/*.gif + body16_anim-preview.png    animated previews on the floor + the whole sheet at 8x
"""
import json
from pathlib import Path

from PIL import Image

from kit import OL, floor_bg, hx

OUT = Path(__file__).parent / "character" / "anim"
(OUT / "preview").mkdir(parents=True, exist_ok=True)
W, H = 16, 32
TONES = {  # same 4 tones as character16.py
    "light":  ["#fff4e8", "#fde3cc", "#ecc6a6", "#d6a886"],
    "medium": ["#ffe6cc", "#f6cba4", "#dea982", "#c48a64"],
    "tan":    ["#f3c896", "#dca772", "#bc8656", "#9c6a40"],
    "deep":   ["#c08c64", "#a06e4a", "#7e5234", "#5e3a22"],
}
DEFAULT = "medium"
EYE, BLUSH, MOUTH = "#2b2230", "#f2a0b4", "#8a3a4a"

# ---- part templates (fill only: 1 light, 2 base, 3 shade, 4 deep; o = forced interior line) ----
HEAD_FRONT = [  # y = 11..22, identical silhouette to character16.BODY
    "....11122222....",
    "...1111222222...",
    "..111122222223..",
    "..112222222223..",
    "..122222222233..",
    ".31222222222233.",  # 16 ear bumps
    ".32222222222333.",
    "..222222222333..",
    "..322222223334..",
    "...3222223334...",
    "....33333444....",
    "......3333......",  # 22 chin / neck
]
HEAD_BACK = [  # back of the head: same skull, no jaw contour — rounder, darker nape
    "....11122222....",
    "...1111222222...",
    "..111122222223..",
    "..112222222223..",
    "..122222222233..",
    ".31222222222233.",
    ".32222222222333.",
    "..222222222333..",
    "..222222222334..",
    "...3222223334...",
    "....33333444....",
    "......3333......",
]
HEAD_SIDE = [  # facing W: face on the left, skull extends back (right), single ear mid-right
    "....11122222....",
    "...1111222222...",
    "..111122222223..",
    "..112222222223..",
    "..1222222222233.",
    "..1222222222333.",
    "..2222222222333.",
    "..222222222333..",
    "..222222223334..",
    "...22222223334..",
    "....22333444....",
    "......3333......",
]
SIDE_EAR = {(10, 16): "3", (9, 17): "3", (10, 17): "4", (9, 18): "3", (10, 18): "4", (10, 19): "3"}  # soft, no outline

TORSO_FRONT = [  # y = 23..27 (core only; hands/shoulders are separate parts)
    ".....122223.....",
    ".....322223.....",
    ".....222222.....",
    ".....222222.....",
    ".....333333.....",
]
TORSO_BACK = [
    ".....122223.....",
    ".....222223.....",
    ".....222223.....",
    ".....322233.....",
    ".....333333.....",
]
TORSO_SIDE = [  # side profile, slight belly forward (left)
    "......12223.....",
    "......22223.....",
    ".....222223.....",
    ".....222233.....",
    "......33333.....",
]
SIDES_HAND = ((1, 0), (-1, 0), (0, 1))  # hands over the body: outline left/right/below only

FACE_S = {(5, 18): "e", (5, 19): "e", (10, 18): "e", (10, 19): "e", (3, 19): "b", (12, 19): "b"}
FACE_W = {(4, 18): "e", (4, 19): "e", (3, 20): "b"}
MOUTH_S = [(7, 20), (8, 20)]
MOUTH_W = [(3, 21)]

NB4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


class Frame:
    def __init__(self):
        self.px = {}  # (x, y) -> template char
        self.lab = {}     # (x, y) -> body part that drew the pixel: leg / torso / arm / hand / head
        self.cur = ""     # part currently being drawn
        self.top = set()  # hand pixels (+ their ring) that must stay above hair / outfit layers

    def put(self, x, y, ch):
        if 0 <= x < W and 0 <= y < H:
            self.px[(x, y)] = ch
            self.lab[(x, y)] = self.cur

    def grid(self, rows, y0, dx=0, dy=0):
        for j, r in enumerate(rows):
            assert len(r) == W, (j, r)
            for i, ch in enumerate(r):
                if ch != ".":
                    self.put(i + dx, y0 + j + dy, ch)

    def stamp(self, cells, sides=NB4, top=False):
        """Draw cells on top and ring them with outline wherever they sit over existing fill."""
        for (x, y), ch in cells.items():
            self.put(x, y, ch)
        for (x, y) in cells:
            for ox, oy in sides:
                n = (x + ox, y + oy)
                if n not in cells and self.px.get(n, "o") != "o":
                    self.px[n] = "o"
                    self.lab[n] = "o"
        if top:
            self.top |= {(x + ox, y + oy) for x, y in cells for ox, oy in NB4 + ((0, 0),)}

    def outline(self):
        for (x, y), ch in list(self.px.items()):
            if ch == "o":
                continue
            for ox, oy in NB4:
                n = (x + ox, y + oy)
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in self.px:
                    self.px[n] = "o"
                    self.lab[n] = "o"


def hand(x, y, light):
    """2x2 round hand blob, top-left at (x, y)."""
    a, b, c, d = ("1", "1", "1", "2") if light else ("2", "3", "3", "3")
    return {(x, y): a, (x + 1, y): b, (x, y + 1): c, (x + 1, y + 1): d}


def leg(x, top, bottom, near=True):
    cells = {}
    for y in range(top, bottom + 1):
        last = y == bottom
        cells[(x, y)] = ("2" if near else "3") if last else "3"
        cells[(x + 1, y)] = "3" if near else "4"
    return cells


# ---- frame builders: each returns (Frame, face cells, offsets) ----------------------------------
def front(back=False, dy=0, lift=None, hl=0, hr=0, legs="stand", hands="side", wave=None, mouth=False):
    """S / N view. dy = head+torso offset, lift = 'L'/'R' leg raised, hl/hr = hand y offsets."""
    f = Frame()
    f.cur = "leg"
    # legs (anchored to the floor at row 29 unless seated)
    for side, x in (("L", 5), ("R", 9)):
        if legs == "sit":  # thighs toward the viewer: short stubs ending at row 30
            for y in range(28 + dy, 31):
                f.put(x, y, "3"); f.put(x + 1, y, "3")
            f.put(x, 30, "2")
        else:
            f.stamp(leg(x, 28 + dy, 28 if lift == side else 29))
    f.cur = "torso"
    f.grid(TORSO_BACK if back else TORSO_FRONT, 23, dy=dy)
    f.cur = "arm"
    if hands == "side":
        f.put(4, 24 + dy, "1"); f.put(11, 24 + dy, "2")
        f.cur = "hand"
        f.stamp(hand(2, 25 + dy + hl, True), top=True)
        if wave is None:
            f.stamp(hand(12, 25 + dy + hr, False), top=True)
    elif hands == "type":  # seated, hands forward on the keyboard
        f.cur = "hand"
        if back:  # back view: elbows out, hands hidden in front of the body
            f.stamp({(4, 25 + dy + hl): "1", (4, 26 + dy + hl): "2"})
            f.stamp({(11, 25 + dy + hr): "3", (11, 26 + dy + hr): "3"})
        else:
            f.stamp(hand(4, 27 + dy + hl, True), top=True)
            f.stamp(hand(10, 27 + dy + hr, False), top=True)
    if wave is not None:  # right hand raised beside the head
        f.cur = "arm"
        f.put(11, 23 + dy, "2"); f.put(12, 23 + dy, "2"); f.put(12, 22 + dy, "3")
    f.cur = "head"
    f.grid(HEAD_BACK if back else HEAD_FRONT, 11, dy=dy)
    if wave is not None:
        f.cur = "hand"
        f.stamp(hand(13, 20 + dy + wave, False), top=True)
    face = {} if back else {(x, y + dy): k for (x, y), k in FACE_S.items()}
    if mouth and not back:
        face.update({(x, y + dy): "m" for x, y in MOUTH_S})
    return f, face


def side(dy=0, stride=0, near_lift=False, far_lift=False, hand_x=7, hand_y=0, legs="stand",
         hands="side", wave=None, mouth=False):
    """W view. stride: 0 legs under the hips, +1 near leg forward, -1 near leg back."""
    f = Frame()
    top = 28 + dy
    f.cur = "leg"
    if legs == "sit":  # thighs forward (left) on the seat, lower legs dangling
        f.cur = "torso"
        f.grid(TORSO_SIDE, 23, dy=dy)
        f.cur = "leg"
        for x in range(3, 9):
            f.put(x, top, "3"); f.put(x, top + 1, "2" if x < 6 else "3")
        if top + 2 <= 30:  # room for dangling feet above the canvas edge
            f.put(3, top + 2, "2"); f.put(4, top + 2, "3")
    else:
        fwd = lambda dark: {(5, top): "3", (6, top): "4" if dark else "3",
                            (4, 29): "3" if dark else "2", (5, 29): "4" if dark else "3"}
        back = lambda dark: {(9, top): "3", (10, top): "4" if dark else "3",
                             (10, 29): "3" if dark else "2", (11, 29): "4" if dark else "3"}
        if stride == 1:
            far, near = back(True), fwd(False)
        elif stride == -1:
            far, near = fwd(True), back(False)
        else:
            far = leg(9, top, 28 if far_lift else 29, near=False)
            near = leg(6, top, 28 if near_lift else 29)
        f.stamp(far)
        f.cur = "torso"
        f.grid(TORSO_SIDE, 23, dy=dy)
        f.cur = "leg"
        f.stamp(near)
    f.cur = "head"
    f.grid(HEAD_SIDE, 11, dy=dy)
    for (x, y), c in SIDE_EAR.items():
        f.put(x, y + dy, c)
    if wave is not None:  # hand raised in front of the face, waving forward/back
        hx_, hy_ = (2, 21) if wave == 0 else (1, 20)
        f.cur = "arm"
        for c in ((4, 22), (4, 23), (5, 23)) + (((3, 22),) if wave else ()):
            f.put(c[0], c[1] + dy, "2")
        f.cur = "hand"
        f.stamp(hand(hx_, hy_ + dy, True), top=True)
    elif hands == "type":
        f.cur = "hand"
        f.stamp(hand(2, 25 + dy + hand_y, True), sides=SIDES_HAND, top=True)
    else:
        f.cur = "hand"
        f.stamp(hand(hand_x, 25 + dy + hand_y, True), sides=SIDES_HAND, top=True)
    face = {(x, y + dy): k for (x, y), k in FACE_W.items()}
    if mouth:
        face.update({(x, y + dy): "m" for x, y in MOUTH_W})
    return f, face


ANIMS = {  # name -> (ms per frame, loop, {dir: [frame specs]})
    "idle": (500, True, {
        "S": [dict(), dict(dy=1, hl=0)],
        "N": [dict(back=True), dict(back=True, dy=1)],
        "W": [dict(), dict(dy=1)],
    }),
    "walk": (140, True, {
        "S": [dict(dy=-1, lift="L", hl=1, hr=-1), dict(), dict(dy=-1, lift="R", hl=-1, hr=1), dict()],
        "N": [dict(back=True, dy=-1, lift="L", hl=1, hr=-1), dict(back=True),
              dict(back=True, dy=-1, lift="R", hl=-1, hr=1), dict(back=True)],
        "W": [dict(stride=1, hand_x=9), dict(dy=-1, far_lift=True, hand_x=7),
              dict(stride=-1, hand_x=4), dict(dy=-1, near_lift=True, hand_x=7)],
    }),
    "sit": (1000, False, {  # seated still: one held frame, no hand / foot movement
        "S": [dict(dy=2, legs="sit", hands="type")],
        "N": [dict(back=True, dy=2, legs="sit", hands="type")],
        "W": [dict(dy=1, legs="sit", hands="type")],
    }),
    "talk": (220, True, {
        "S": [dict(), dict(hr=-2, hl=-1, mouth=True)],
        "N": [dict(back=True), dict(back=True, hr=-2, hl=-1)],
        "W": [dict(), dict(hand_x=4, hand_y=-2, mouth=True)],
    }),
    "wave": (200, True, {
        "S": [dict(wave=0, mouth=True), dict(wave=1, mouth=True)],
        "N": [dict(back=True, wave=0), dict(back=True, wave=1)],
        "W": [dict(wave=0, mouth=True), dict(wave=1, mouth=True)],
    }),
}
DIRS = ["S", "N", "W", "E"]
COLS = max(len(fs) for _, _, d in ANIMS.values() for fs in d.values())


def build(d, spec):
    spec = dict(spec)
    if d in ("S", "N"):
        f, face = front(**spec)
    else:
        f, face = side(**spec)
    f.outline()
    dy = spec.get("dy", 0)
    return f, face, dy


def paint(f, tone, mirror=False):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pal = {"o": hx(OL), "1": hx(tone[0]), "2": hx(tone[1]), "3": hx(tone[2]), "4": hx(tone[3])}
    for (x, y), ch in f.px.items():
        im.putpixel((x, y), pal[ch] + (255,))
    for x in range(4, 12):  # contact shadow
        if (x, 31) not in f.px:
            im.putpixel((x, 31), (40, 24, 30, 70))
    return im.transpose(Image.FLIP_LEFT_RIGHT) if mirror else im


def paint_face(face, mirror=False):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    col = {"e": hx(EYE), "b": hx(BLUSH), "m": hx(MOUTH)}
    for (x, y), k in face.items():
        im.putpixel((x, y), col[k] + (255,))
    return im.transpose(Image.FLIP_LEFT_RIGHT) if mirror else im


def gif(frames_by_row, ms, path, scale=8, gap=4):
    """frames_by_row: list of frame lists (one per direction) -> one animated GIF on the floor."""
    n = max(len(r) for r in frames_by_row)
    w = len(frames_by_row) * (W + gap) + gap
    h = H + 2 * gap
    out = []
    for i in range(n):
        bg = floor_bg(w, h)
        for c, row in enumerate(frames_by_row):
            bg.alpha_composite(row[i % len(row)], (gap + c * (W + gap), gap))
        out.append(bg.resize((w * scale, h * scale), Image.NEAREST).convert("RGB"))
    out[0].save(path, save_all=True, append_images=out[1:], duration=ms, loop=0, disposal=2)


if __name__ == "__main__":
    rows = [(a, d) for a in ANIMS for d in DIRS]
    built = {}
    for a, (ms, loop, dirs) in ANIMS.items():
        for d in DIRS:
            src = "W" if d == "E" else d
            built[(a, d)] = [build(src, s) for s in dirs[src]]

    meta = {"frame": [W, H], "columns": COLS, "anchor": [8, 30],
            "note": "anchor = feet centre (x, y) inside a cell; headDy/bodyDy = how far the head/torso moved "
                    "this frame — offset hair/outfit layers by the same amount. E rows are W mirrored.",
            "animations": {}}
    for r, (a, d) in enumerate(rows):
        ms, loop, _ = ANIMS[a]
        meta["animations"].setdefault(a, {"msPerFrame": ms, "loop": loop, "directions": {}})
        meta["animations"][a]["directions"][d] = {
            "row": r,
            "frames": [{"x": c * W, "y": r * H, "w": W, "h": H, "headDy": dy, "bodyDy": dy}
                       for c, (_, _, dy) in enumerate(built[(a, d)])],
        }

    sheets = {}
    for t, tone in TONES.items():
        sheet = Image.new("RGBA", (COLS * W, len(rows) * H), (0, 0, 0, 0))
        for r, (a, d) in enumerate(rows):
            for c, (f, _, _) in enumerate(built[(a, d)]):
                sheet.alpha_composite(paint(f, tone, d == "E"), (c * W, r * H))
        sheet.save(OUT / f"body16_anim_{t}.png")
        sheets[t] = sheet
    sheets[DEFAULT].save(OUT / "body16_anim.png")
    sheets[DEFAULT].resize((COLS * W * 2, len(rows) * H * 2), Image.NEAREST).save(OUT / "body16_anim_x2.png")

    face_sheet = Image.new("RGBA", sheets[DEFAULT].size, (0, 0, 0, 0))
    for r, (a, d) in enumerate(rows):
        for c, (_, face, _) in enumerate(built[(a, d)]):
            face_sheet.alpha_composite(paint_face(face, d == "E"), (c * W, r * H))
    face_sheet.save(OUT / "face16_anim.png")
    (OUT / "body16_anim.json").write_text(json.dumps(meta, indent=2))

    # previews: one GIF per animation (S N W E side by side), plus the full labelled sheet
    tone = TONES[DEFAULT]
    for a, (ms, _, _) in ANIMS.items():
        per_dir = []
        for d in DIRS:
            fr = []
            for f, face, _ in built[(a, d)]:
                im = paint(f, tone, d == "E")
                im.alpha_composite(paint_face(face, d == "E"))
                fr.append(im)
            per_dir.append(fr)
        gif(per_dir, ms, OUT / "preview" / f"{a}.gif")

    full = sheets[DEFAULT].copy()
    full.alpha_composite(face_sheet)
    bg = floor_bg(full.width + 8, full.height + 8)
    bg.alpha_composite(full, (4, 4))
    bg.resize((bg.width * 8, bg.height * 8), Image.NEAREST).convert("RGB").save(OUT / "body16_anim-preview.png")
    print("ok", len(rows), "rows x", COLS, "cols")
