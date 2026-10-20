"""Sprite 12 — 2-seat lounge sofa, 4 directions. Steep top-down camera, desk scale
(150 cm wide = 72 px, 85 cm deep = 33 px, seat 9 px / arms 12 px / back 16 px high).

Every part is placed by its floor footprint + height (screen y = floor y - height), so the
geometry stays consistent: lit horizontal tops (seat cushions, arm tops, backrest top) are the
big bright shapes, vertical faces are darker, nearer parts overlap farther ones.

Direction = the way the SEAT faces:
  sofa_front.png  80x60  seat faces the viewer: cushions, backrest behind, two throw pillows
  sofa_back.png   80x60  backrest's rear faces the viewer, seat tops peek over it
  sofa_left.png   52x80  seat faces left (west)  — backrest along the east side
  sofa_right.png  52x80  seat faces right (east) — backrest along the west side
Anchor by the bottom-centre. Outputs in ./sofa/ + sofa-preview.png (plush + desk for scale)
"""
from pathlib import Path

from PIL import Image

from kit import RED, Sprite, floor_bg

OUT = Path(__file__).parent / "sofa"
OUT.mkdir(exist_ok=True)
SOFA = ["#8fd0c4", "#6fb8ab", "#56a094", "#43857a", "#2f6058"]   # teal fabric
LEG = ["#7a4a26", "#4a2c16"]
CREAM = ["#fbf6ea", "#ece3cc", "#d4c8aa"]
REDP = [RED[0], RED[1], RED[2]]


def block(s, x0, x1, y0, y1, h, top=True, front=True, r=1):
    """Box from floor footprint (x0..x1, y0..y1 = far..near) and height h.
    Draws its front (vertical, darker) face and its lit top face."""
    if front:
        s.rect(x0, y1 - h, x1, y1, SOFA[3])
        s.vline(x0, y1 - h, y1, SOFA[2])
        s.hline(x0, x1, y1 - 1, SOFA[4])
    if top:
        s.rrect(x0, y0 - h, x1, y1 - h, SOFA[1], r)
        s.hline(x0 + r, x1 - r, y0 - h, SOFA[0])
        s.vline(x0, y0 - h + r, y1 - h - r, SOFA[0])
        s.hline(x0 + 1, x1 - 1, y1 - h - 1, "#e6f5f1")              # front edge catches the light


def cushion(s, x0, x1, y0, y1):
    """Puffy seat cushion top: lighter centre, darker seam ring."""
    s.rrect(x0, y0, x1, y1, SOFA[1], 2)
    s.rrect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, SOFA[0], 2)
    s.rrect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, "#9fd8cc", 2)
    s.hline(x0 + 4, x0 + 10, y0 + 4, "#c9eee6")


def pillow(s, x0, y0, w, h, ramp):
    """Throw pillow leaning on the backrest: soft square, lit top-left, dented middle."""
    s.rrect(x0, y0, x0 + w, y0 + h, ramp[1], 2)
    s.hline(x0 + 2, x0 + w - 2, y0, ramp[0])
    s.vline(x0, y0 + 2, y0 + h - 2, ramp[0])
    s.rrect(x0 + 2, y0 + h - 3, x0 + w - 1, y0 + h, ramp[2], 1)
    s.px(x0 + w // 2, y0 + h // 2, ramp[2])


def legs(s, xs, y):
    for x in xs:
        s.rect(x, y, x + 2, y + 2, LEG[1])
        s.px(x, y, LEG[0])


# ================================================================ front ===
X0, X1 = 4, 76
F0, F1 = 20, 53                 # floor footprint, far .. near
ARM_W, BACK_D = 8, 8
H_SEAT, H_ARM, H_BACK = 9, 12, 16


def draw_front():
    s = Sprite(80, 60)
    legs(s, (X0 + 1, X1 - 3), F1)
    block(s, X0, X1, F0, F0 + BACK_D, H_BACK, front=True)          # backrest (front face hidden by seat)
    # seat base + two cushions
    sy0, sy1 = F0 + BACK_D - H_SEAT, F1 - H_SEAT
    s.rect(X0 + ARM_W, sy1, X1 - ARM_W, F1, SOFA[3])               # seat front (vertical)
    s.hline(X0 + ARM_W, X1 - ARM_W, sy1, SOFA[2])
    s.vline((X0 + X1) // 2, sy1 + 1, F1 - 1, SOFA[4])              # split between the cushion fronts
    s.hline(X0 + ARM_W, X1 - ARM_W, F1 - 1, SOFA[4])
    mid = (X0 + X1) // 2
    s.rect(X0 + ARM_W, sy0, X1 - ARM_W, sy1, SOFA[2])              # seat deck under the cushions
    cushion(s, X0 + ARM_W, mid, sy0, sy1)
    cushion(s, mid, X1 - ARM_W, sy0, sy1)
    pillow(s, X0 + ARM_W + 3, sy0 - 6, 12, 10, REDP)               # pillows leaning on the back
    pillow(s, X1 - ARM_W - 15, sy0 - 5, 12, 10, CREAM)
    for x0 in (X0, X1 - ARM_W):                                    # arms on top of everything
        block(s, x0, x0 + ARM_W, F0, F1, H_ARM, r=2)
    s.vline(X0 + ARM_W, F0 - H_ARM + 1, F1 - H_ARM, SOFA[4])        # crease where each arm meets the seat
    s.vline(X1 - ARM_W - 1, F0 - H_ARM + 1, F1 - H_ARM, SOFA[3])
    s.cast(X0, F0, X1, F1, H_ARM)
    return s.finish()


def draw_back():
    s = Sprite(80, 60)
    legs(s, (X0 + 1, X1 - 3), F1)
    mid = (X0 + X1) // 2
    sy0, sy1 = F0 - H_SEAT, F1 - BACK_D - H_SEAT                    # seat is further away now
    s.rect(X0 + ARM_W - 1, sy0, X1 - ARM_W + 1, sy1, SOFA[2])      # seat deck: no notches between cushions/arms
    cushion(s, X0 + ARM_W, mid, sy0, sy1)
    cushion(s, mid, X1 - ARM_W, sy0, sy1)
    for x0 in (X0, X1 - ARM_W):
        block(s, x0, x0 + ARM_W, F0, F1, H_ARM, r=2)
    block(s, X0, X1, F1 - BACK_D, F1, H_BACK)                      # backrest, nearest to us
    s.rect(X0 + 2, F1 - H_BACK + 2, X1 - 2, F1 - 2, SOFA[3])       # rear panel
    for x in range(X0 + 12, X1 - 6, 12):                           # piping seams on the back
        s.vline(x, F1 - H_BACK + 1, F1 - 1, SOFA[4])
    s.rect(X1 - 14, F1 - 8, X1 - 9, F1 - 4, "#f4f1ea")             # care label
    s.cast(X0, F0, X1, F1, H_ARM)
    return s.finish()


# ================================================================= side ===
SX0, SX1 = 4, 46               # depth (along x)
SF0, SF1 = 16, 74              # width x0.8 (along y), far .. near
ARM_T = 6                      # arm thickness along y


def draw_side(faces_east):
    s = Sprite(52, 80)
    X = (lambda a, b: (a, b)) if faces_east else (lambda a, b: (SX0 + SX1 - b, SX0 + SX1 - a))
    bx0, bx1 = X(SX0, SX0 + BACK_D)                                # backrest strip
    ax0, ax1 = X(SX0, SX1)                                         # full depth (arms)
    cx0, cx1 = X(SX0 + BACK_D, SX1)                                # seat
    legs(s, (ax0 + 1, ax1 - 3), SF1)
    block(s, ax0, ax1, SF0, SF0 + ARM_T, H_ARM, r=2)               # far arm
    block(s, bx0, bx1, SF0 + ARM_T, SF1 - ARM_T, H_BACK, r=1)   # backrest: long top + its near end face (fills the gap down to the near arm)
    # seat cushions (split along the width)
    sy0, sy1 = SF0 + ARM_T - H_SEAT, SF1 - ARM_T - H_SEAT
    mid = (sy0 + sy1) // 2
    s.rect(cx0, sy0, cx1, sy1, SOFA[2])                            # seat deck under the cushions: no notches between them
    cushion(s, cx0, cx1, sy0, mid)
    cushion(s, cx0, cx1, mid, sy1)
    py = (sy0 + 6, mid + 4)
    pa = X(SX0 + BACK_D, SX0 + BACK_D + 6)[0]                       # pillows seen side-on
    pillow(s, pa, py[0], 6, 11, REDP)
    pillow(s, pa, py[1], 6, 11, CREAM)
    s.hline(cx0, cx1, SF0 + ARM_T - H_ARM, SOFA[4])                # crease under the far arm
    block(s, ax0, ax1, SF1 - ARM_T, SF1, H_ARM, r=2)               # near arm (front face toward us)
    s.hline(ax0 + 2, ax1 - 2, SF1 - ARM_T - H_ARM, SOFA[3])          # crease where it meets the seat
    s.cast(ax0, SF0, ax1, SF1, H_ARM)
    return s.finish()


if __name__ == "__main__":
    views = {"front": draw_front(), "back": draw_back(), "left": draw_side(False), "right": draw_side(True)}
    for k, v in views.items():
        v.image().save(OUT / f"sofa_{k}.png")
    root = Path(__file__).parent
    items = [views[k].image() for k in ("front", "back", "left", "right")]
    items += [Image.open(root / "plush" / "plush_front.png"), Image.open(root / "desk" / "desk_front.png")]
    gap = 8
    H = max(i.height for i in items) + 2 * gap
    W = sum(i.width for i in items) + gap * (len(items) + 1)
    scene = floor_bg(W, H)
    x = gap
    for im in items:
        scene.alpha_composite(im, (x, H - gap - im.height))
        x += im.width + gap
    scene.convert("RGB").resize((W * 4, H * 4), Image.NEAREST).save(OUT / "sofa-preview.png")
    print("ok")
