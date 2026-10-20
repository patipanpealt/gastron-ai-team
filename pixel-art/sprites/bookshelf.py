"""Sprite 09 — bookshelf, 4 directions. Steep top-down camera, desk scale
(90 cm wide = 44 px, 35 cm deep = 14 px top face, 180 cm tall = 36 px front face).

Top-down cues: a big lit TOP face with things lying on it (flat books, a little plant),
every shelf board shows a thin lit top edge, and every book shows a lit pixel on its top.

Direction = the way the OPEN side faces:
  shelf_front.png  48x58  shelves + books face the viewer
  shelf_back.png   48x58  plain back panel faces the viewer
  shelf_left.png   24x78  open side faces left (west): side panel, book ends peek at the open edge
  shelf_right.png  24x78  open side faces right (east)
Anchor by the bottom-centre. Outputs in ./bookshelf/ + bookshelf-preview.png (desk for scale)
"""
import random
from pathlib import Path

from PIL import Image

from kit import GREEN, LIP, RED, WOOD, WOOD_F, Sprite, floor_bg

OUT = Path(__file__).parent / "bookshelf"
OUT.mkdir(exist_ok=True)
BOOKS = ["#b0473a", "#3f6f8f", "#d8b44a", "#4f8f5c", "#e8e2d4", "#7a4f8f", "#c96a3a", "#2f4f6f", RED[1], GREEN[1]]
INSIDE = "#24140a"                                            # shadowed back of the shelves


def lighter(c, t=0.3):
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(v + (255 - v) * t) for v in (r, g, b))


def darker(c, t=0.3):
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(v * (1 - t)) for v in (r, g, b))


def top_face(s, x0, x1, y0, y1, items, mirror=False):
    """Lit top of the cabinet + what lies on it (positions mirror for the back view)."""
    s.rect(x0, y0, x1, y1, WOOD[1])
    s.hline(x0, x1, y0, WOOD[0])
    s.vline(x0, y0, y1, WOOD[0])
    s.vline(x1 - 1, y0 + 1, y1, WOOD[2])
    for y in range(y0 + 3, y1 - 2, 4):                        # grain along the long side
        s.hline(x0 + 3 + (y * 7) % 9, x0 + 12 + (y * 7) % 9, y, WOOD[2])
    s.hline(x0, x1, y1 - 1, LIP)                              # near edge catches the light
    if not items:
        return
    w = x1 - x0
    fx = (lambda a: x1 - (a - x0) - 1) if mirror else (lambda a: a)
    # two books lying flat (we see their covers) + a small potted plant
    bx = fx(x0 + 4) - (6 if mirror else 0)
    s.rect(bx, y0 + 4, bx + 7, y0 + 9, BOOKS[1])
    s.hline(bx, bx + 7, y0 + 4, lighter(BOOKS[1]))
    s.rect(bx + 1, y0 + 2, bx + 8, y0 + 6, RED[1])            # second one on top, slightly turned
    s.hline(bx + 1, bx + 8, y0 + 2, RED[0])
    s.vline(bx + 7, y0 + 3, y0 + 6, "#f4f1ea")                # page edge
    px_ = fx(x0 + w - 9) - (4 if mirror else 0)
    s.rect(px_, y0 + 6, px_ + 5, y0 + 10, "#c97a4a")          # plant pot
    s.disc(px_ + 2.5, y0 + 5.5, 2.5, 1.2, "#e09a6a")          # pot rim
    s.disc(px_ + 2.5, y0 + 3.5, 3.5, 3, "#549f42")            # leaves seen from above
    s.disc(px_ + 1.5, y0 + 2.5, 2, 1.6, "#78bf55")
    s.px(px_ + 1, y0 + 2, "#a6dc72")


def book_row(s, x0, x1, base, hmax, rng):
    """Books standing on a shelf: varied widths/heights, lit top pixel, the odd gap or binder."""
    x = x0
    while x < x1:
        if rng.random() < 0.1 and x + 3 < x1:                 # gap
            x += 2
            continue
        if rng.random() < 0.15 and x + 5 <= x1:               # binder with a white label
            c = rng.choice([RED[1], "#2f4f6f", GREEN[1]])
            s.rect(x, base - hmax, x + 4, base, c)
            s.hline(x, x + 4, base - hmax, lighter(c))
            s.rect(x + 1, base - hmax + 2, x + 3, base - hmax + 3, "#f4f1ea")
            x += 4
            continue
        bw = rng.choice([1, 2, 2, 3])
        if x + bw > x1:
            break
        bh = hmax - rng.choice([0, 0, 1, 2])
        c = rng.choice(BOOKS)
        s.rect(x, base - bh, x + bw, base, c)
        s.hline(x, x + bw, base - bh, lighter(c, 0.4))        # book top seen from above
        if bw > 1:
            s.vline(x + bw - 1, base - bh + 1, base, darker(c, 0.25))
        x += bw


# ================================================================ front ===
X0, X1 = 2, 46
TOP0, TOP1 = 4, 18
FR1 = 54
SHELVES = [18, 26, 34, 42, 50]                                # board tops (y)


def carcass_front(s):
    s.rect(X0, TOP1, X1, FR1, WOOD_F[1])                      # front frame
    s.vline(X0, TOP1, FR1, WOOD_F[0])
    s.vline(X1 - 1, TOP1, FR1, WOOD_F[2])
    s.rect(X0 + 2, TOP1 + 1, X1 - 2, FR1 - 4, INSIDE)         # dark interior
    s.rect(X0 + 1, FR1 - 4, X1 - 1, FR1, WOOD_F[3])           # kick plinth
    s.hline(X0 + 1, X1 - 1, FR1 - 4, WOOD_F[2])


def draw_front():
    s = Sprite(48, 58)
    carcass_front(s)
    rng = random.Random(7)
    for a, b in zip(SHELVES, SHELVES[1:]):
        if b == 34:                                           # one shelf with a trophy + a box
            book_row(s, X0 + 3, X0 + 22, b - 1, 6, rng)
            s.rect(X0 + 26, b - 5, X0 + 29, b - 1, "#d8b44a")  # trophy
            s.hline(X0 + 25, X0 + 30, b - 6, "#f0d27a")
            s.rect(X0 + 27, b - 2, X0 + 28, b - 1, "#a8862a")
            s.rect(X0 + 32, b - 4, X1 - 4, b - 1, "#d9a866")  # storage box
            s.hline(X0 + 32, X1 - 4, b - 4, "#e8bf82")
            s.px(X0 + 35, b - 3, RED[1])
        else:
            book_row(s, X0 + 3, X1 - 3, b - 1, 6, rng)
        s.rect(X0 + 2, b - 1, X1 - 2, b, WOOD[1])             # shelf board: lit top edge
        s.hline(X0 + 2, X1 - 2, b - 1, WOOD[0])
        s.rect(X0 + 2, b, X1 - 2, b + 1, WOOD_F[1])           # ... and its front edge
    top_face(s, X0, X1, TOP0, TOP1, True)
    s.cast(X0, TOP0 + (FR1 - TOP1), X1, FR1, FR1 - TOP1)
    return s.finish()


def draw_back():
    s = Sprite(48, 58)
    s.rect(X0, TOP1, X1, FR1, WOOD_F[1])                      # plain back panel
    s.vline(X0, TOP1, FR1, WOOD_F[0])
    s.vline(X1 - 1, TOP1, FR1, WOOD_F[2])
    for x in range(X0 + 11, X1 - 4, 11):                      # plank seams
        s.vline(x, TOP1 + 1, FR1 - 4, WOOD_F[2])
    s.rect(X0 + 1, FR1 - 4, X1 - 1, FR1, WOOD_F[3])
    s.hline(X0 + 1, X1 - 1, FR1 - 4, WOOD_F[2])
    s.rect(30, 24, 38, 29, "#f4f1ea")                         # assembly label
    s.px(31, 25, RED[1])
    top_face(s, X0, X1, TOP0, TOP1, True, mirror=True)
    s.cast(X0, TOP0 + (FR1 - TOP1), X1, FR1, FR1 - TOP1)
    return s.finish()


# ================================================================= side ===
SX0, SX1 = 3, 20                                              # 17 px: the shelf's depth
STOP0, STOP1 = 4, 39                                          # 35 px: its width x0.8
SFR1 = 75


def draw_side(open_east):
    s = Sprite(24, 78)
    X = (lambda a, b: (a, b)) if open_east else (lambda a, b: (SX0 + SX1 - b, SX0 + SX1 - a))
    s.rect(SX0, STOP1, SX1, SFR1, WOOD_F[1])                  # side panel
    s.vline(SX0, STOP1, SFR1, WOOD_F[0])
    s.vline(SX1 - 1, STOP1, SFR1, WOOD_F[2])
    for y in range(STOP1 + 5, SFR1 - 6, 7):                   # grain
        s.hline(SX0 + 3, SX1 - 4, y, WOOD_F[2])
    s.rect(SX0 + 1, SFR1 - 4, SX1 - 1, SFR1, WOOD_F[3])
    # open edge: shelf ends + book ends peeking past the carcass edge
    ea, eb = X(SX1 - 3, SX1)
    s.rect(ea, STOP1, eb, SFR1 - 4, WOOD_F[0])
    rng = random.Random(3)
    for i, y in enumerate(range(STOP1 + 1, SFR1 - 5, 8)):
        s.hline(ea, eb, y, WOOD[1])                           # shelf board end (lit)
        for k in range(1, 7):
            if rng.random() < 0.7:
                s.px(X(SX1 - 2, SX1 - 1)[0], y + k, rng.choice(BOOKS))
    # top face (the shelf's width runs into the screen) + items lying on it
    s.rect(SX0, STOP0, SX1, STOP1, WOOD[1])
    s.hline(SX0, SX1, STOP0, WOOD[0])
    s.vline(SX0, STOP0, STOP1, WOOD[0])
    s.vline(SX1 - 1, STOP0 + 1, STOP1, WOOD[2])
    for x in range(SX0 + 3, SX1 - 2, 4):
        s.vline(x, STOP0 + 4 + x % 5, STOP0 + 14 + x % 5, WOOD[2])
    s.hline(SX0, SX1, STOP1 - 1, LIP)
    ba, bb = X(SX0 + 4, SX0 + 10)                             # flat books
    s.rect(ba, STOP0 + 4, bb, STOP0 + 12, BOOKS[1])
    s.rect(ba + 1, STOP0 + 3, bb + 1, STOP0 + 9, RED[1])
    s.hline(ba + 1, bb + 1, STOP0 + 3, RED[0])
    pa = X(SX0 + 6, SX0 + 11)[0]                              # plant near the far end
    s.rect(pa, STOP0 + 26, pa + 5, STOP0 + 30, "#c97a4a")
    s.disc(pa + 2.5, STOP0 + 25.5, 2.5, 1.2, "#e09a6a")
    s.disc(pa + 2.5, STOP0 + 23.5, 3.5, 3, "#549f42")
    s.disc(pa + 1.5, STOP0 + 22.5, 2, 1.6, "#78bf55")
    s.cast(SX0, STOP0 + (SFR1 - STOP1), SX1, SFR1, SFR1 - STOP1)
    return s.finish()


if __name__ == "__main__":
    views = {"front": draw_front(), "back": draw_back(), "left": draw_side(False), "right": draw_side(True)}
    for k, v in views.items():
        v.image().save(OUT / f"shelf_{k}.png")
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
    scene.convert("RGB").resize((W * 6, H * 6), Image.NEAREST).save(OUT / "bookshelf-preview.png")
    print("ok")
