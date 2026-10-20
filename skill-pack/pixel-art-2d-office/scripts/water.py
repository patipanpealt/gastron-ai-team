"""Sprite 04 — water dispenser with an 18 L bottle on top, 4 directions (32x64 each).
32px grid, top-down 3/4, light from the top-left.

Direction = the way the TAPS face:
  cooler_front.png  taps face the viewer (south): red hot tap + blue cold tap, drip tray, cabinet door
  cooler_back.png   taps face away (north): rear panel with condenser coil, vents, power cord
  cooler_left.png   taps face left (west): side panel, taps + drip tray poke out on the west edge
  cooler_right.png  taps face right (east)
Footprint is 1 tile; anchor by the bottom-centre (the feet).
Outputs in ./water/: the four PNGs + cooler-preview.png
"""
from pathlib import Path

from PIL import Image

from kit import GREEN, KEY, METAL, PLASTIC, RED, Sprite, preview

OUT = Path(__file__).parent / "water"
OUT.mkdir(exist_ok=True)
W, H = 32, 64
BODY = KEY                                                   # warm white plastic ramp
BOTTLE = ["#e4f6fc", "#b4e2f4", "#86cbe8", "#5aa6cc", "#3d7f98"]
BLUE = ["#8fc8f0", "#3f7fc8", "#2a5a96"]                     # cold tap
BX0, BX1 = 6, 26                                             # body (20 wide)
# Same steep top-down camera as the desk: depth x0.8, heights x~0.4, so the top face is big
# and the bottle reads as a squat cylinder whose round top we can see.
TOP0, TOP1 = 24, 40                                          # top face (16 deep)
FR1 = 58                                                     # bottom of the front face (18 tall)
FEET = 60
CX = 16                                                      # bottle axis
SEAT_Y = 32                                                  # where the bottle stands on the top face

IDENT = lambda a, b: (a, b)                                  # noqa: E731
MIRROR = lambda a, b: (W - b, W - a)                         # noqa: E731


def bottle(s):
    """Upturned 18 L bottle seen from above: round base (now facing up) as an ellipse,
    a short cylinder side with moulded ridges, shoulders tapering into the neck."""
    rx, ry = 8, 6
    top_y = SEAT_Y - 21                                      # ellipse centre of the bottle's upper end (tall 18 L bottle)
    # cylinder side (front half only is visible): left lit, right in shade
    for y in range(top_y, SEAT_Y - 2):
        taper = max(0, y - (SEAT_Y - 7))                     # shoulders narrow towards the neck
        x0, x1 = CX - rx + taper, CX + rx - taper
        s.hline(x0, x1, y, BOTTLE[2])
        s.hline(x0 + 1, x1 - 3, y, BOTTLE[1])
        s.hline(x0 + 1, x0 + 3, y, BOTTLE[0])                # gloss band
        s.hline(x1 - 2, x1, y, BOTTLE[3])
    for ry_off in (5, 10, 15):                                    # ridges curve down in the middle (lower half of an ellipse)
        y = top_y + ry_off
        s.hline(CX - 5, CX + 5, y + 1, BOTTLE[3])
        s.hline(CX - 5, CX + 5, y + 2, BOTTLE[0])
        for x in (CX - 8, CX - 7, CX - 6, CX + 5, CX + 6, CX + 7):
            s.px(x, y, BOTTLE[3])
    for y in range(top_y + 6, top_y + 13):
        s.px(CX - 6, y, "#ffffff")                           # long gloss streak
    for bx, by in ((CX + 2, top_y + 7), (CX - 1, top_y + 13), (CX + 3, top_y + 17)):   # bubbles
        s.px(bx, by, BOTTLE[0])
    # neck + collar going into the seat
    s.rect(CX - 3, SEAT_Y - 3, CX + 3, SEAT_Y + 1, BOTTLE[3])
    s.hline(CX - 3, CX + 3, SEAT_Y - 3, BOTTLE[2])
    s.rect(CX - 4, SEAT_Y, CX + 4, SEAT_Y + 2, BOTTLE[4])
    # the round end on top: rim, recessed base, crescent highlight
    s.disc(CX - 0.5, top_y, rx, ry, BOTTLE[2])
    s.disc(CX - 0.5, top_y, rx - 1, ry - 1, BOTTLE[1])
    s.disc(CX - 0.5, top_y + 0.5, rx - 3, ry - 2.5, BOTTLE[2])   # recessed centre
    s.disc(CX - 0.5, top_y + 1, rx - 4, ry - 3.5, BOTTLE[1])
    for x, y in ((CX - 6, top_y - 2), (CX - 5, top_y - 3), (CX - 4, top_y - 4), (CX - 3, top_y - 4)):
        s.px(x, y, "#ffffff")                                # crescent glint on the rim
    s.hline(CX - 4, CX + 4, top_y + ry - 1, BOTTLE[3])       # near rim edge


def body_shell(s):
    """Top face + front face block shared by every view."""
    s.rect(BX0, TOP0, BX1, TOP1, BODY[1])                    # top face
    s.hline(BX0, BX1, TOP0, BODY[0])
    s.vline(BX0, TOP0, TOP1, BODY[0])
    s.vline(BX1 - 1, TOP0 + 1, TOP1, BODY[2])
    s.rect(BX0 + 2, TOP0 + 2, BX1 - 2, TOP1 - 2, BODY[0])    # slightly raised lid panel
    s.rect(BX0 + 3, TOP0 + 3, BX1 - 2, TOP1 - 2, BODY[1])
    s.hline(BX0 + 2, BX1 - 2, TOP1 - 2, BODY[2])
    s.hline(BX0, BX1, TOP1 - 1, "#ffffff")                  # front edge catches the light
    s.rect(BX0, TOP1, BX1, FR1, BODY[2])                     # front face: in shade, darker than the top
    s.vline(BX0, TOP1, FR1, BODY[1])
    s.vline(BX1 - 1, TOP1, FR1, BODY[3])
    s.hline(BX0, BX1, FR1 - 1, BODY[3])
    s.rect(BX0 + 1, FR1, BX1 - 1, FEET, PLASTIC[2])          # plinth
    s.hline(BX0 + 1, BX1 - 1, FEET - 1, PLASTIC[3])
    for fx in (BX0 + 1, BX1 - 4):                            # feet
        s.rect(fx, FEET, fx + 3, FEET + 1, PLASTIC[3])


def bottle_seat(s):
    """Round bottle seat on the top face (an ellipse, since we look down on it)."""
    s.disc(CX - 0.5, SEAT_Y + 1, 7, 4, BODY[2])
    s.disc(CX - 0.5, SEAT_Y + 1, 6, 3, BODY[0])
    s.hline(CX - 4, CX + 4, SEAT_Y + 4, BODY[3])


# ================================================================ front ===
def draw_front():
    s = Sprite(W, H)
    body_shell(s)
    bottle_seat(s)
    # status lights above the alcove
    s.px(12, 41, RED[0])
    s.px(15, 41, GREEN[0])
    s.px(18, 41, BLUE[0])
    # dispensing alcove
    s.rect(BX0 + 3, 43, BX1 - 3, 52, BODY[3])
    s.rect(BX0 + 4, 44, BX1 - 4, 52, "#8d8678")
    s.hline(BX0 + 4, BX1 - 4, 44, "#6f695e")                 # deep shadow under the lip
    for tx, c in ((11, RED), (19, BLUE)):                    # taps: hot (Gastron red) + cold (blue)
        s.rect(tx - 1, 45, tx + 3, 47, c[1])
        s.hline(tx - 1, tx + 3, 45, c[0])
        s.rect(tx, 47, tx + 2, 49, METAL[1])                 # spout
        s.px(tx, 47, METAL[0])
    s.px(20, 49, BLUE[0])                                    # a drop falling from the cold tap
    s.rect(BX0 + 4, 50, BX1 - 4, 52, METAL[1])               # drip tray grill
    for gx in range(BX0 + 5, BX1 - 4, 2):
        s.px(gx, 50, METAL[3])
    s.hline(BX0 + 3, BX1 - 3, 52, METAL[2])                  # tray lip
    # cabinet door
    s.rect(BX0 + 3, 53, BX1 - 3, FR1 - 1, BODY[1])
    s.hline(BX0 + 3, BX1 - 3, 53, BODY[2])
    s.vline(BX0 + 3, 53, FR1 - 1, BODY[2])
    s.vline(BX1 - 4, 53, FR1 - 1, BODY[3])
    s.rect(BX1 - 7, 54, BX1 - 5, 56, METAL[1])               # handle
    s.px(BX1 - 7, 54, METAL[0])
    bottle(s)
    s.cast(BX0, TOP0 + (FEET - TOP1), BX1, FEET, 22)
    return s.finish()


# ================================================================= back ===
def draw_back():
    s = Sprite(W, H)
    body_shell(s)
    bottle_seat(s)
    # vent slots up top
    for y in (42, 44):
        s.hline(BX0 + 4, BX1 - 8, y, BODY[3])
    # condenser coil on two rails
    s.rect(BX0 + 3, 46, BX1 - 3, FR1 - 1, "#3a3e4b")
    for y in range(47, FR1 - 1, 2):
        s.hline(BX0 + 4, BX1 - 4, y, "#5a6170")
    s.vline(BX0 + 4, 46, FR1 - 1, METAL[2])
    s.vline(BX1 - 5, 46, FR1 - 1, METAL[2])
    # power cord + rating sticker
    s.rect(BX0 + 2, 41, BX0 + 4, 43, PLASTIC[2])
    for k in range(5):
        s.px(BX0 - 1, 43 + k * 3, "#1d1f26")                # cord dangling down the side
    s.rect(BX1 - 7, 41, BX1 - 3, 45, "#f4f1ea")
    s.px(BX1 - 6, 42, RED[1])
    bottle(s)
    s.cast(BX0, TOP0 + (FEET - TOP1), BX1, FEET, 22)
    return s.finish()


# ================================================================= side ===
def draw_side(taps_east):
    """Profile: plain side panel; taps + drip tray stick out past the tap-side edge.
    Geometry mirrors for the left sprite, highlights stay on the lower-x edge (light top-left)."""
    s = Sprite(W, H)
    X = IDENT if taps_east else MIRROR
    body_shell(s)
    bottle_seat(s)
    # side panel details: seam + vent grille near the back
    sa, sb = X(BX0 + 3, BX0 + 4)
    s.vline(sa, TOP1 + 2, FR1 - 2, BODY[2])                  # panel seam
    va, vb = X(BX0 + 6, BX0 + 12)
    for y in range(50, FR1 - 1, 2):
        s.hline(va, vb, y, BODY[3])
    # alcove seen from the side: notch in the tap-side edge
    na, nb = X(BX1 - 3, BX1)
    s.rect(na, 43, nb, 52, "#8d8678")
    s.hline(na, nb, 43, "#6f695e")
    # taps sticking out (hot behind cold, so the red tip peeks above the blue)
    ta, tb = X(BX1 - 2, BX1 + 2)
    s.rect(ta, 44, tb, 46, RED[1])
    s.hline(ta, tb, 44, RED[0])
    s.rect(ta, 46, tb, 48, BLUE[1])
    s.hline(ta, tb, 46, BLUE[0])
    pa, pb = X(BX1, BX1 + 2)
    s.rect(pa, 48, pb, 50, METAL[1])                         # spout
    ra, rb = X(BX1 - 3, BX1 + 2)
    s.rect(ra, 50, rb, 52, METAL[1])                         # drip tray lip
    s.hline(ra, rb, 50, METAL[0])
    s.hline(ra, rb, 51, METAL[2])
    s.px(X(BX1 - 2, BX1 - 1)[0], 41, GREEN[0])               # status light on the tap-side corner
    bottle(s)
    s.cast(BX0, TOP0 + (FEET - TOP1), BX1, FEET, 22)
    return s.finish()


if __name__ == "__main__":
    views = {"front": draw_front(), "back": draw_back(), "left": draw_side(False), "right": draw_side(True)}
    for name, sp in views.items():
        sp.image().save(OUT / f"cooler_{name}.png")
    imgs = [views[k].image() for k in ("front", "back", "left", "right")]
    gap = 6
    sheet = Image.new("RGBA", (sum(i.width for i in imgs) + gap * 3, H), (0, 0, 0, 0))
    x = 0
    for im in imgs:
        sheet.alpha_composite(im, (x, 0))
        x += im.width + gap
    preview(sheet, OUT / "cooler-preview.png", 8, grid=False)
    print("ok")
