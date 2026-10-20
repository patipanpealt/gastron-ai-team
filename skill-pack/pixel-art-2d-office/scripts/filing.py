"""Sprite 10 — 4-drawer steel filing cabinet, 4 directions. Steep top-down camera, desk scale
(45 cm wide = 22 px, 60 cm deep = 19 px top face, 130 cm tall = 26 px front).

Top-down cues: big lit top with an in-tray of papers + a stapler on it; each drawer front has a
lit top lip; the 2nd drawer is pulled OUT, so we look down into it and see the hanging-folder tabs.

Direction = the way the DRAWERS face:
  filing_front.png  28x52  drawer fronts face the viewer
  filing_back.png   28x52  plain back panel
  filing_left.png   36x48  drawers face left (west): side panel, the open drawer pokes out west
  filing_right.png  36x48  drawers face right (east)
Anchor by the bottom-centre. Outputs in ./filing/ + filing-preview.png (desk for scale)
"""
from pathlib import Path

from PIL import Image

from kit import GREEN, PLASTIC, RED, Sprite, floor_bg

OUT = Path(__file__).parent / "filing"
OUT.mkdir(exist_ok=True)
STEEL = ["#e3e7ec", "#c4cad3", "#a3abb7", "#7e8693", "#5d6470"]
CHROME = ["#ffffff", "#c9ced6", "#7d8590"]
TABS = ["#f6d04d", RED[1], "#3f7fc8", GREEN[1], "#f59ab0"]


def in_tray(s, x, y):
    """Desk tray with paper (seen from above) + a stapler beside it."""
    s.rect(x, y, x + 10, y + 7, "#3a3e4b")
    s.rect(x + 1, y + 1, x + 9, y + 6, "#f4f1ea")
    s.hline(x + 1, x + 9, y + 1, "#ffffff")
    for k in (3, 5):
        s.hline(x + 2, x + 7, y + k, "#c9c4b8")
    s.rect(x, y + 7, x + 10, y + 8, "#262a35")                 # tray lip
    s.rect(x + 12, y + 2, x + 15, y + 7, RED[1])              # stapler
    s.vline(x + 12, y + 2, y + 7, RED[0])
    s.px(x + 13, y + 3, "#ffffff")


def top_face(s, x0, x1, y0, y1, tray_at):
    s.rect(x0, y0, x1, y1, STEEL[0])
    s.hline(x0, x1, y0, "#ffffff")
    s.vline(x0, y0, y1, "#ffffff")
    s.vline(x1 - 1, y0 + 1, y1, STEEL[1])
    s.hline(x0, x1, y1 - 1, "#ffffff")                        # near edge catches the light
    if tray_at:
        in_tray(s, *tray_at)


def handle(s, cx, y):
    s.rect(cx - 2, y - 2, cx + 2, y, "#f4f1ea")               # label card holder
    s.hline(cx - 2, cx + 2, y - 2, STEEL[3])
    s.rect(cx - 3, y + 1, cx + 3, y + 2, CHROME[1])           # pull handle
    s.hline(cx - 3, cx + 3, y + 2, CHROME[2])


# ================================================================ front ===
X0, X1 = 2, 24
TOP0, TOP1 = 4, 23
FR1 = 49
DRAWERS = [23, 29, 35, 41]                                    # drawer tops; each 6 px tall


def draw_front():
    s = Sprite(28, 52)
    s.rect(X0, TOP1, X1, FR1, STEEL[2])                       # cabinet front (vertical, in shade)
    s.vline(X0, TOP1, FR1, STEEL[1])
    s.vline(X1 - 1, TOP1, FR1, STEEL[4])
    s.rect(X0 + 1, FR1 - 2, X1 - 1, FR1, STEEL[4])            # plinth
    cx = (X0 + X1) // 2
    for i, y in enumerate(DRAWERS):
        if i == 1:
            continue
        s.hline(X0 + 1, X1 - 1, y, STEEL[1])                  # drawer's lit top lip
        s.hline(X0 + 1, X1 - 1, y + 5, STEEL[3])              # gap under it
        handle(s, cx, y + 3)
    top_face(s, X0, X1, TOP0, TOP1, (X0 + 2, TOP0 + 4))
    # the open drawer: pulled 6 px toward us — top (folders, seen from above) + its own front
    y = DRAWERS[1]
    s.rect(X0 + 1, y, X1 - 1, y + 6, STEEL[3])                # dark slot behind it
    s.rect(X0 + 1, y + 1, X1 - 1, y + 7, STEEL[4])            # drawer side walls / inside
    s.rect(X0 + 2, y + 1, X1 - 2, y + 7, "#e8e2d4")           # hanging folders, top view
    for k, tx in enumerate(range(X0 + 3, X1 - 3, 3)):
        s.vline(tx, y + 1, y + 7, "#c9c4b8")                  # folder edges
        s.rect(tx, y + 1 + (k % 2), tx + 2, y + 2 + (k % 2), TABS[k % len(TABS)])  # tabs
    s.rect(X0, y + 7, X1, y + 13, STEEL[1])                   # open drawer front (nearer -> lower)
    s.hline(X0, X1, y + 7, STEEL[0])                          # its lit top lip
    s.hline(X0, X1, y + 12, STEEL[4])
    handle(s, cx, y + 10)
    s.cast(X0, TOP0 + (FR1 - TOP1), X1, FR1, FR1 - TOP1)
    return s.finish()


def draw_back():
    s = Sprite(28, 52)
    s.rect(X0, TOP1, X1, FR1, STEEL[2])
    s.vline(X0, TOP1, FR1, STEEL[1])
    s.vline(X1 - 1, TOP1, FR1, STEEL[4])
    for y in range(TOP1 + 4, FR1 - 4, 5):                     # pressed stiffening ribs
        s.hline(X0 + 3, X1 - 3, y, STEEL[3])
    s.rect(X0 + 1, FR1 - 2, X1 - 1, FR1, STEEL[4])
    s.rect(X1 - 9, TOP1 + 3, X1 - 3, TOP1 + 7, "#f4f1ea")     # spec sticker
    s.px(X1 - 8, TOP1 + 4, RED[1])
    top_face(s, X0, X1, TOP0, TOP1, (X1 - 18, TOP0 + 4))
    s.cast(X0, TOP0 + (FR1 - TOP1), X1, FR1, FR1 - TOP1)
    return s.finish()


# ================================================================= side ===
SX0, SX1 = 5, 31                                              # 26 px: the cabinet depth (room either side for the open drawer)
STOP0, STOP1 = 4, 22                                          # 18 px: its width x0.8
SFR1 = 48


def draw_side(drawers_east):
    s = Sprite(36, 48)
    X = (lambda a, b: (a, b)) if drawers_east else (lambda a, b: (SX0 + SX1 - b, SX0 + SX1 - a))
    s.rect(SX0, STOP1, SX1, SFR1, STEEL[2])                   # side panel
    s.vline(SX0, STOP1, SFR1, STEEL[1])
    s.vline(SX1 - 1, STOP1, SFR1, STEEL[4])
    pa, pb = X(SX0 + 4, SX1 - 8)
    for y in range(STOP1 + 5, SFR1 - 4, 7):                   # pressed panel lines
        s.hline(pa, pb, y, STEEL[3])
    s.rect(SX0 + 1, SFR1 - 2, SX1 - 1, SFR1, STEEL[4])
    ea, eb = X(SX1 - 2, SX1)                                  # drawer fronts seen edge-on
    s.rect(ea, STOP1, eb, SFR1 - 2, STEEL[1])
    for y in DRAWERS[2:] + [DRAWERS[0]]:
        s.hline(ea, eb, y - 1, STEEL[4])
    top_face(s, SX0, SX1, STOP0, STOP1, None)
    ta = X(SX0 + 5, SX0 + 15)[0]
    in_tray(s, ta, STOP0 + 5)
    # open drawer sticking out of the drawer side
    oa, ob = X(SX1, SX1 + 4)
    s.rect(oa, 28, ob, 30, "#e8e2d4")                         # folders seen from above
    for k, x in enumerate(range(oa, ob)):
        s.px(x, 28, TABS[k % len(TABS)])
    s.rect(oa, 30, ob, 35, STEEL[1])                          # drawer side wall
    s.hline(oa, ob, 30, STEEL[0])
    s.hline(oa, ob, 34, STEEL[4])
    s.cast(SX0, STOP0 + (SFR1 - STOP1), SX1, SFR1, SFR1 - STOP1)
    return s.finish()


if __name__ == "__main__":
    views = {"front": draw_front(), "back": draw_back(), "left": draw_side(False), "right": draw_side(True)}
    for k, v in views.items():
        v.image().save(OUT / f"filing_{k}.png")
    desk = Image.open(Path(__file__).parent / "desk" / "desk_front.png")
    items = [views[k].image() for k in ("front", "back", "left", "right")] + [desk]
    gap = 8
    H = max(i.height for i in items) + 2 * gap
    W = sum(i.width for i in items) + gap * (len(items) + 1)
    scene = floor_bg(W, H)
    x = gap
    for im in items:
        scene.alpha_composite(im, (x, H - gap - im.height))
        x += im.width + gap
    scene.convert("RGB").resize((W * 7, H * 7), Image.NEAREST).save(OUT / "filing-preview.png")
    print("ok")
