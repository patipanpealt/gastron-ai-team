"""Sprite 08 — whiteboard. Steep top-down camera, same scale as the desk (1.2 m wide = ~60 px).

Top-down reading: the board itself is a vertical panel, so it is short (heights x0.4) and the
lit horizontal bits carry the depth — the frame's top edge, the marker tray (seen from above,
markers lying on it) and the stand's feet, which run front-to-back on the floor.

Mobile board on castors, direction = the way the WRITING SIDE faces:
  wb_front.png  64x48  writing side faces the viewer: campaign plan, sticky notes, red trend line
  wb_back.png   64x48  back panel faces the viewer
  wb_left.png   32x84  writing side faces left (west) — the panel is seen edge-on
  wb_right.png  32x84  writing side faces right (east)
Wall-mounted version for the room's wall face:
  wb_wall.png   64x28  board + tray only (no stand, no floor shadow)
Outputs in ./whiteboard/ + whiteboard-preview.png (next to the desk for scale)
"""
from pathlib import Path

from PIL import Image

from kit import GREEN, PLASTIC, RED, Sprite, floor_bg

OUT = Path(__file__).parent / "whiteboard"
OUT.mkdir(exist_ok=True)
ALU = ["#f2f4f7", "#c9ced6", "#a3aab6", "#7d8590"]           # aluminium frame
BOARD = ["#ffffff", "#f4f5f2", "#e2e4df"]
BACKP = ["#9aa1ad", "#848b98", "#6d7482"]                    # back panel
STICKY = ["#f6d04d", "#f59ab0", "#8fd3a8", "#9cc8f0"]
INK = "#3a4150"
MARKERS = [RED[1], GREEN[1], "#3f7fc8", "#2b2230"]


def line(s, pts, c):
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(by - ay), 1)
        for t in range(n + 1):
            s.px(round(ax + (bx - ax) * t / n), round(ay + (by - ay) * t / n), c)


def board_face(s, x0, x1, y0, y1):
    """Writing side: marketing plan scribbles."""
    s.rect(x0, y0, x1, y1, BOARD[1])
    s.hline(x0, x1, y0, BOARD[0])
    s.hline(x0, x1, y1 - 1, BOARD[2])
    s.hline(x0 + 2, x0 + 16, y0 + 2, INK)                    # title
    s.hline(x0 + 2, x0 + 10, y0 + 4, "#8a90a0")
    for i, c in enumerate(STICKY + STICKY[:2]):               # sticky-note cluster
        sx, sy = x0 + 2 + (i % 3) * 5, y0 + 7 + (i // 3) * 4
        s.rect(sx, sy, sx + 4, sy + 3, c)
    for k, ln in enumerate((9, 7, 10, 6)):                    # bullet text
        s.px(x0 + 20, y0 + 7 + k * 2, RED[1])
        s.hline(x0 + 22, x0 + 22 + ln, y0 + 7 + k * 2, "#8a90a0")
    ax0, ay1 = x0 + 36, y1 - 3                                # trend chart
    s.vline(ax0, y0 + 2, ay1 + 1, INK)
    s.hline(ax0, x1 - 2, ay1, INK)
    line(s, [(ax0 + 1, ay1 - 2), (ax0 + 5, ay1 - 4), (ax0 + 9, ay1 - 3), (ax0 + 13, ay1 - 8),
             (ax0 + 17, ay1 - 9), (x1 - 3, ay1 - 12)], RED[1])
    s.px(x1 - 3, ay1 - 12, RED[0])                           # arrow head
    s.px(x1 - 4, ay1 - 12, RED[1])
    s.px(x1 - 3, ay1 - 11, RED[1])


def frame(s, x0, x1, y0, y1, top=1):
    """Aluminium frame: lit top edge seen from above + thin sides."""
    s.rect(x0, y0 - top, x1, y0, ALU[0])                      # top edge (horizontal, brightest)
    s.hline(x0 + 1, x1 - 1, y0 - top, "#ffffff")
    s.rect(x0, y0, x0 + 2, y1, ALU[1])
    s.rect(x1 - 2, y0, x1, y1, ALU[2])
    s.hline(x0, x1, y1 - 1, ALU[3])


def tray(s, x0, x1, y, depth=3):
    """Marker tray: a horizontal ledge seen from above, markers lying on it."""
    s.rect(x0, y, x1, y + depth, ALU[1])
    s.hline(x0, x1, y, ALU[0])
    s.rect(x0, y + depth, x1, y + depth + 1, ALU[3])          # its little front face
    for i, c in enumerate(MARKERS):
        mx = x0 + 6 + i * 6
        s.hline(mx, mx + 4, y + 1, c)
        s.px(mx + 4, y + 1, "#f4f1ea")                        # cap
    s.rect(x1 - 12, y + 1, x1 - 6, y + 3, "#3a3e4b")          # eraser
    s.hline(x1 - 12, x1 - 6, y + 1, "#5a6170")


def foot(s, x0, x1, y0, y1):
    """Floor foot running front-to-back (lit top) with a castor at each end."""
    s.rect(x0, y0, x1, y1, ALU[1])
    s.vline(x0, y0, y1, ALU[0])
    s.hline(x0, x1, y1 - 1, ALU[3])
    for cy in (y0 - 1, y1):
        s.disc((x0 + x1) / 2 - 0.5, cy + 0.5, 1.8, 1.3, PLASTIC[3])


# ================================================================ front ===
BX0, BX1, BY0, BY1 = 3, 61, 2, 27                             # board face incl. frame (tall panel)


def stand_front(s):
    for x in (6, 56):
        foot(s, x - 2, x + 4, 32, 46)                         # foot runs front-to-back on the floor
        s.rect(x, BY1, x + 2, 39, ALU[2])                     # upright comes all the way down ...
        s.vline(x, BY1, 39, ALU[1])
        s.rect(x - 1, 38, x + 3, 41, ALU[3])                  # ... and plugs into the middle of the foot
        s.hline(x - 1, x + 3, 38, ALU[2])


def draw_front():
    s = Sprite(64, 48)
    stand_front(s)
    frame(s, BX0, BX1, BY0, BY1)
    board_face(s, BX0 + 2, BX1 - 2, BY0, BY1 - 1)
    tray(s, BX0 + 4, BX1 - 4, BY1 - 1)
    s.cast(BX0, 34, BX1, 46, 26)
    return s.finish()


def draw_back():
    s = Sprite(64, 48)
    stand_front(s)
    frame(s, BX0, BX1, BY0, BY1)
    s.rect(BX0 + 2, BY0, BX1 - 2, BY1 - 1, BACKP[1])         # back panel
    s.hline(BX0 + 2, BX1 - 2, BY0, BACKP[0])
    for x in range(BX0 + 12, BX1 - 8, 12):                   # stiffening ribs
        s.vline(x, BY0 + 1, BY1 - 1, BACKP[2])
    s.rect(30, BY0 + 6, 36, BY0 + 10, "#f4f1ea")              # label
    s.px(31, BY0 + 7, RED[1])
    s.cast(BX0, 34, BX1, 46, 26)
    return s.finish()


# ================================================================= side ===
SW, SH = 32, 84
FY0, FY1 = 34, 78                                             # footprint along the board's width


def draw_side(faces_east):
    """Board seen edge-on: a slim column (the panel's width runs into the screen),
    lit top edge, tray ledge on the writing side, feet crossing it on the floor."""
    s = Sprite(SW, SH)
    X = (lambda a, b: (a, b)) if faces_east else (lambda a, b: (SW - b, SW - a))
    # far foot first, then the panel, then the near foot + post on top
    a, b = X(4, 27)
    s.rect(a, FY0, b, FY0 + 3, ALU[2])
    s.hline(a, b, FY0, ALU[1])
    pa, pb = X(14, 18)                                        # the panel, edge-on
    s.rect(pa, 2, pb, 62, ALU[1])
    s.vline(pa, 2, 62, ALU[0])
    s.vline(pb - 1, 2, 62, ALU[3])
    s.rect(pa, 0, pb, 2, "#ffffff")                           # lit top edge
    fx = X(17, 18)[0]                                         # white writing-surface edge
    s.vline(fx, 3, 61, BOARD[1])
    ta, tb = X(18, 21)                                        # tray ledge on the writing side
    s.rect(ta, 20, tb, 62, ALU[1])
    s.vline(ta, 20, 62, ALU[0])
    for i, c in enumerate(MARKERS):
        s.vline(X(19, 20)[0], 26 + i * 8, 31 + i * 8, c)
    na, nb = X(15, 17)                                        # near upright down to the foot
    s.rect(na, 62, nb, FY1 - 1, ALU[2])
    s.vline(na, 62, FY1 - 1, ALU[1])
    s.rect(a, FY1 - 3, b, FY1, ALU[1])                        # near foot (lit top, runs left-right)
    s.hline(a, b, FY1 - 3, ALU[0])
    s.hline(a, b, FY1 - 1, ALU[3])
    for cx in (a + 1, b - 2):
        s.disc(cx, FY1, 1.6, 1.2, PLASTIC[3])
        s.disc(cx, FY0 + 3, 1.6, 1.2, PLASTIC[3])
    s.cast(a, FY0, b, FY1, 26)
    return s.finish()


# ================================================================= wall ===
def draw_wall():
    s = Sprite(64, 28)
    frame(s, BX0, BX1, 4, 22)
    board_face(s, BX0 + 2, BX1 - 2, 4, 21)
    tray(s, BX0 + 4, BX1 - 4, 21)
    return s.finish(shadow=False)


if __name__ == "__main__":
    views = {"front": draw_front(), "back": draw_back(), "left": draw_side(False), "right": draw_side(True),
             "wall": draw_wall()}
    for k, v in views.items():
        v.image().save(OUT / f"wb_{k}.png")
    desk = Image.open(Path(__file__).parent / "desk" / "desk_front.png")
    items = [views[k].image() for k in ("front", "back", "left", "right", "wall")] + [desk]
    gap = 8
    H = max(i.height for i in items) + 2 * gap
    W = sum(i.width for i in items) + gap * (len(items) + 1)
    scene = floor_bg(W, H)
    x = gap
    for im in items:
        scene.alpha_composite(im, (x, H - gap - im.height))
        x += im.width + gap
    scene.convert("RGB").resize((W * 5, H * 5), Image.NEAREST).save(OUT / "whiteboard-preview.png")
    print("ok")
