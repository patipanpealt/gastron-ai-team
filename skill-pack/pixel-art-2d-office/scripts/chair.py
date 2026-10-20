"""Sprite 02 — office chair, 4 directions (32x46 each, 32px grid, top-down 3/4, light from the top-left).

Direction = the way the SEAT faces (the way the sitter looks):
  chair_front.png  seat faces the viewer (south)   — we see cushion + backrest front
  chair_back.png   seat faces away (north)         — we see the backrest's rear shell
  chair_left.png   seat faces left (west)          — profile, backrest on the east side
  chair_right.png  seat faces right (east)         — profile, backrest on the west side
Pairs with the desk (the chair faces the screen):
  desk_front + chair_back   (chair south of the desk)
  desk_back  + chair_front  (chair north of the desk, drawn before the desk)
  desk_left  + chair_right  (chair west of the desk)
  desk_right + chair_left   (chair east of the desk)
Outputs in ./chair/: the four PNGs, chair-preview.png, desk-chair-pairs.png
"""
from pathlib import Path

from PIL import Image

from kit import FABRIC, METAL, PLASTIC, RED, Sprite, preview  # noqa: F401

OUT = Path(__file__).parent / "chair"
W, H = 32, 46
DY = 6                                 # extra headroom on top for the taller backrest


class ChairSprite(Sprite):
    """Sprite whose drawing coords are shifted down by DY, so y can go to -DY for the backrest."""

    def px(self, x, y, c):
        super().px(x, y + DY, c)

    def rect(self, x0, y0, x1, y1, c):
        super().rect(x0, y0 + DY, x1, y1 + DY, c)

    def cast(self, x0, y0, x1, y1, height):
        super().cast(x0, y0 + DY, x1, y1 + DY, height)


# Top-down camera rules for the chair (same as the desk):
#   * horizontal surfaces (seat, armrest tops, base star) are seen almost flat-on and are the
#     BRIGHTEST planes; vertical surfaces (backrest faces, seat edge) are darker
#   * every part shows a thin lit top edge, and nearer parts overlap farther ones
SEAT_T = ["#7a8196", "#666d82", "#555b6e"]                            # seat top: lit fabric
FRONT = [FABRIC[1], FABRIC[2], FABRIC[3]]                              # vertical fabric faces
IDENT = lambda a, b: (a, b)                                           # noqa: E731
MIRROR = lambda a, b: (W - b, W - a)                                  # noqa: E731


def leg(s, x0, y0, x1, y1, c):
    """2px-thick straight leg of the five-star base."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for t in range(n + 1):
        x = round(x0 + (x1 - x0) * t / n)
        y = round(y0 + (y1 - y0) * t / n)
        s.px(x, y, c)
        s.px(x, y + 1, PLASTIC[3])


# Steep top-down camera, same scale as the desk (heights x0.4, depth x0.8):
#   seat 22x19 px seen almost flat-on (the dominant, brightest shape), seat height 9 px,
#   backrest only ~10 px tall above it, base star mostly hidden under the seat — only the leg
#   tips + castors poke out. Armrest pads run front-to-back, so they read as long strips.
FLOOR_C = (16, 28)                     # chair centre on the floor
SEAT = (5, 27, 9, 28)                  # seat top face x0, x1, y0, y1


def base(s, X):
    cx, cy = X(FLOOR_C[0], FLOOR_C[0] + 1)[0], FLOOR_C[1]
    for tx, ty in ((3, 27), (29, 27), (7, 35), (25, 35)):
        t = X(tx, tx + 1)[0]
        leg(s, cx, cy, t, ty, PLASTIC[1])
        s.disc(t, ty + 1.5, 1.6, 1.2, PLASTIC[3])                     # castor
        s.px(t - 1, ty + 1, PLASTIC[0])


def seat_top(s, x0, x1, y0, y1):
    s.rrect(x0, y0, x1, y1, SEAT_T[1], 3)
    s.rrect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, SEAT_T[1], 2)
    s.hline(x0 + 3, x1 - 3, y0, SEAT_T[0])
    s.vline(x0, y0 + 3, y1 - 3, SEAT_T[0])
    s.rrect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, SEAT_T[0], 2)            # puffy cushion centre
    s.rrect(x0 + 4, y0 + 4, x1 - 4, y1 - 4, SEAT_T[1], 2)
    s.hline(x0 + 5, x0 + 10, y0 + 5, "#8f97ad")                      # sheen
    s.hline(x0 + 2, x1 - 2, y1 - 1, SEAT_T[2])


def seat_edge(s, x0, x1, y1, h=3):
    s.rrect(x0 + 1, y1, x1 - 1, y1 + h, FRONT[1], 1)                 # cushion thickness (vertical, dark)
    s.hline(x0 + 2, x1 - 2, y1 + h - 1, FRONT[2])


def pad(s, x0, x1, y0, y1, front=2):
    """Armrest pad seen from above (lit) + its short dark front face."""
    s.rrect(x0, y0, x1, y1, PLASTIC[0], 1)
    s.hline(x0 + 1, x1 - 1, y0, "#6e7690")
    s.vline(x1 - 1, y0 + 1, y1 - 1, PLASTIC[1])
    s.rect(x0, y1, x1, y1 + front, PLASTIC[2])
    s.hline(x0, x1, y1 + front - 1, PLASTIC[3])


# ================================================================ front ===
def draw_front():
    """Seat faces us. Backrest stands at the far edge; the seat in front hides its lower part."""
    s = ChairSprite(W, H)
    base(s, IDENT)
    s.rrect(7, -5, 25, -2, SEAT_T[0], 2)                              # backrest top edge
    s.rrect(7, -3, 25, 13, FRONT[0], 2)                               # backrest face (vertical, darker)
    s.rrect(9, -1, 23, 11, FRONT[1], 2)                               # padded panel
    x0, x1, y0, y1 = SEAT
    seat_top(s, x0, x1, y0, y1)
    seat_edge(s, x0, x1, y1)
    pad(s, 2, 6, 10, 20)                                              # armrests run front-to-back
    pad(s, 26, 30, 10, 20)
    s.cast(4, 22, 28, 37, 9)
    return s.finish()


# ================================================================= back ===
def draw_back():
    """Seat faces away. The backrest's rear shell stands at the NEAR edge and hides the seat's front."""
    s = ChairSprite(W, H)
    base(s, IDENT)
    x0, x1, y0, y1 = SEAT
    seat_top(s, x0, x1, y0, y1)
    pad(s, 2, 6, 10, 20)
    pad(s, 26, 30, 10, 20)
    s.rrect(7, 10, 25, 13, SEAT_T[0], 2)                              # backrest top edge
    s.rrect(7, 12, 25, 29, PLASTIC[1], 2)                             # rear shell (vertical, darker)
    s.rrect(9, 14, 23, 27, PLASTIC[2], 1)
    s.hline(8, 24, 28, PLASTIC[3])
    s.cast(4, 22, 28, 37, 9)
    return s.finish()


# ================================================================= side ===
def draw_side(faces_east):
    """Profile from above: seat top is wide, the backrest is a thin upright slab at the back,
    far armrest pad above the seat, near armrest pad in front of it. Highlights stay top-left."""
    s = ChairSprite(W, H)
    X = IDENT if faces_east else MIRROR
    base(s, X)
    na, nb = X(10, 24)
    s.rrect(na, 4, nb, 7, PLASTIC[0], 1)                              # far armrest pad
    s.rect(na, 7, nb, 8, PLASTIC[2])
    a, b = X(7, 28)
    seat_top(s, a, b, 9, 28)
    seat_edge(s, a, b, 28)
    ba, bb = X(4, 9)                                                  # backrest slab, seen edge-on
    s.rrect(ba, -5, bb, 27, FRONT[0], 1)
    s.rect(ba + 1, -5, bb - 1, -3, SEAT_T[0])                         # lit top edge
    s.vline(X(4, 5)[0], -3, 26, PLASTIC[2])                           # rear shell side
    pa, pb = X(11, 25)
    s.rect(X(16, 18)[0], 24, X(16, 18)[1], 28, PLASTIC[2])            # near armrest post
    pad(s, pa, pb, 21, 24)                                            # near armrest pad
    s.cast(4, 22, 28, 37, 9)
    return s.finish()


# ================================================================= main ===
def sheet(items, gap=8):
    """Bottom-align (sprite, x_offset) pieces into one transparent canvas."""
    w = sum(i.width for i in items) + gap * (len(items) - 1)
    h = max(i.height for i in items)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for im in items:
        out.alpha_composite(im, (x, h - im.height))
        x += im.width + gap
    return out


def pair(desk, chair, dx, dy, cx, cy, chair_first):
    w = max(dx + desk.width, cx + chair.width)
    h = max(dy + desk.height, cy + chair.height)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for im, x, y in ((chair, cx, cy), (desk, dx, dy)) if chair_first else ((desk, dx, dy), (chair, cx, cy)):
        out.alpha_composite(im, (x, y))
    return out


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    views = {"front": draw_front(), "back": draw_back(), "left": draw_side(False), "right": draw_side(True)}
    for name, sp in views.items():
        sp.image().save(OUT / f"chair_{name}.png")
    imgs = {k: v.image() for k, v in views.items()}
    preview(sheet([imgs[k] for k in ("front", "back", "left", "right")]), OUT / "chair-preview.png", 8, grid=False)

    import desk as D                                                  # pairing check with the approved desk
    dk = {"front": D.draw_desk().image(), "back": D.draw_desk_back().image(),
          "left": D.draw_desk_side(True).image(), "right": D.draw_desk_side(False).image()}
    pairs = [
        pair(dk["front"], imgs["back"], 0, 0, 15, 50 - DY, False),
        pair(dk["back"], imgs["front"], 0, 14 + DY, 15, 0, True),
        pair(dk["left"], imgs["right"], 22, 0, 0, 30 - DY, True),
        pair(dk["right"], imgs["left"], 0, 0, 22, 30 - DY, True),
    ]
    preview(sheet(pairs, 10), OUT / "desk-chair-pairs.png", 6, grid=False)
    print("ok")
