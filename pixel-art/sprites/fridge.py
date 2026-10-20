"""Sprite 05 — two-door fridge (freezer on top), brushed steel, 4 directions (32x80 each).
32px grid, same steep top-down camera as the desk / water cooler: big top face, shorter front.

Direction = the way the DOORS face:
  fridge_front.png  doors face the viewer: freezer + fridge doors, chrome handles, magnets, temp display
  fridge_back.png   doors face away: rear panel with condenser coil, compressor box, power cord
  fridge_left.png   doors face left (west): side panel; door edges + handles stick out on the west
  fridge_right.png  doors face right (east)
Footprint is 1 tile; anchor by the bottom-centre (the feet).
Outputs in ./fridge/: the four PNGs + fridge-preview.png
"""
from pathlib import Path

from PIL import Image

from kit import GREEN, METAL, PLASTIC, RED, Sprite, preview

OUT = Path(__file__).parent / "fridge"
OUT.mkdir(exist_ok=True)
W, H = 32, 80
STEEL = ["#eef1f5", "#d3d8df", "#b3bac5", "#8e96a3"]          # brushed steel ramp
CHROME = ["#ffffff", "#c9ced6", "#7d8590"]
BX0, BX1 = 3, 27                                             # body (24 wide)
TOP0, TOP1 = 8, 34                                           # top face (26 deep) — big lid sells the top-down view
SPLIT = 47                                                   # gap between freezer and fridge door
FR1 = 74                                                     # bottom of the front face (40 tall: a full-height fridge)
FEET = 76

IDENT = lambda a, b: (a, b)                                  # noqa: E731
MIRROR = lambda a, b: (BX0 + BX1 - b, BX0 + BX1 - a)         # mirror about the body's centre  # noqa: E731


def shell(s):
    """Top face + front face + plinth, shared by every view."""
    s.rect(BX0, TOP0, BX1, TOP1, STEEL[0])                   # top face: lit, the brightest plane
    s.hline(BX0, BX1, TOP0, "#ffffff")
    s.vline(BX0, TOP0, TOP1, "#ffffff")
    s.vline(BX1 - 1, TOP0 + 1, TOP1, STEEL[1])
    for x, c in ((BX0 + 5, "#ffffff"), (BX0 + 6, "#ffffff"), (BX0 + 15, STEEL[1])):   # soft brushed sheen
        s.vline(x, TOP0 + 3, TOP1 - 3, c)
    s.rect(BX0 + 3, TOP0 + 2, BX1 - 3, TOP0 + 4, STEEL[2])   # rear vent strip on the lid
    for x in range(BX0 + 4, BX1 - 3, 2):
        s.px(x, TOP0 + 3, STEEL[3])
    s.hline(BX0, BX1, TOP1 - 2, STEEL[1])                    # rounded front lip
    s.hline(BX0, BX1, TOP1 - 1, "#ffffff")                  # front edge catches the light
    s.rect(BX0, TOP1, BX1, FR1, STEEL[2])                    # front face: in shade, darker than the lid
    s.vline(BX0, TOP1, FR1, STEEL[1])
    s.vline(BX1 - 1, TOP1, FR1, STEEL[3])
    s.hline(BX0, BX1, FR1 - 1, STEEL[3])
    s.rect(BX0 + 1, FR1, BX1 - 1, FEET, PLASTIC[2])          # plinth
    s.hline(BX0 + 1, BX1 - 1, FEET - 1, PLASTIC[3])
    for fx in (BX0 + 1, BX1 - 4):
        s.rect(fx, FEET, fx + 3, FEET + 1, PLASTIC[3])


def lid_box(s, x, y):
    """Small cardboard box resting on the lid (top face + front face), tape across the top."""
    s.rect(x + 1, y + 10, x + 12, y + 12, STEEL[2])          # contact shadow on the lid (down-right)
    s.rect(x + 10, y + 2, x + 12, y + 10, STEEL[2])
    s.rect(x, y, x + 10, y + 6, "#d9a866")
    s.hline(x, x + 10, y, "#e8bf82")
    s.vline(x + 4, y, y + 6, "#e8e2d4")                      # packing tape
    s.rect(x, y + 6, x + 10, y + 10, "#b9844a")
    s.hline(x, x + 10, y + 9, "#8f6236")
    s.px(x + 7, y + 7, RED[1])                               # Gastron logo sticker


def handle(s, x, y0, y1):
    """Vertical chrome bar handle standing off the door."""
    s.rect(x, y0, x + 2, y1, CHROME[1])
    s.vline(x, y0, y1, CHROME[0])
    s.vline(x + 1, y0 + 1, y1, CHROME[2])
    s.vline(x + 2, y0 + 1, y1 + 1, STEEL[3])                 # handle's little cast shadow on the door
    s.px(x, y0 - 1, CHROME[2])                               # stand-off brackets
    s.px(x, y1, CHROME[2])


# ================================================================ front ===
def draw_front():
    s = Sprite(W, H)
    shell(s)
    lid_box(s, BX0 + 3, TOP0 + 9)
    # door split + door bevels
    s.hline(BX0, BX1, SPLIT, STEEL[3])
    s.hline(BX0, BX1, SPLIT + 1, "#5d6470")
    for y0, y1 in ((TOP1 + 1, SPLIT), (SPLIT + 2, FR1 - 4)):
        s.vline(BX0 + 1, y0, y1, STEEL[1])
        s.hline(BX0 + 1, BX1 - 1, y0, STEEL[1])
    for x in (BX0 + 6, BX0 + 13):                            # vertical brushed sheen
        s.vline(x, TOP1 + 2, SPLIT - 1, STEEL[1])
        s.vline(x, SPLIT + 3, FR1 - 5, STEEL[1])
    handle(s, BX1 - 5, TOP1 + 2, SPLIT - 1)                  # freezer handle
    handle(s, BX1 - 5, SPLIT + 3, SPLIT + 17)                # fridge handle
    # magnets + notes on the freezer door
    s.rect(BX0 + 4, TOP1 + 2, BX0 + 9, TOP1 + 7, "#f6d04d")  # sticky note
    s.hline(BX0 + 5, BX0 + 8, TOP1 + 4, "#c9a83a")
    s.px(BX0 + 6, TOP1 + 2, RED[1])                          # red Gastron magnet pinning it
    s.px(BX0 + 7, TOP1 + 2, RED[1])
    s.rect(BX0 + 11, TOP1 + 2, BX0 + 16, TOP1 + 7, "#f4f1ea")    # photo
    s.rect(BX0 + 12, TOP1 + 3, BX0 + 15, TOP1 + 5, "#8fcde4")
    s.rect(BX0 + 12, TOP1 + 5, BX0 + 15, TOP1 + 6, GREEN[1])
    # temperature display on the fridge door
    s.rect(BX0 + 4, SPLIT + 3, BX0 + 11, SPLIT + 7, "#1d1f26")
    s.hline(BX0 + 5, BX0 + 7, SPLIT + 4, GREEN[0])
    s.px(BX0 + 9, SPLIT + 4, "#8fcde4")
    s.hline(BX0 + 5, BX0 + 10, SPLIT + 6, PLASTIC[1])
    # door bottom edge + kick grille
    s.hline(BX0, BX1, FR1 - 4, STEEL[3])
    s.rect(BX0 + 2, FR1 - 3, BX1 - 2, FR1 - 1, "#3a3e4b")
    for x in range(BX0 + 3, BX1 - 2, 2):
        s.px(x, FR1 - 2, "#5a6170")
    s.cast(BX0, TOP0 + (FEET - TOP1), BX1, FEET, 30)
    return s.finish()


# ================================================================= back ===
def draw_back():
    s = Sprite(W, H)
    shell(s)
    lid_box(s, BX1 - 13, TOP0 + 9)                           # same box, seen from behind (on the other side)
    s.rect(BX0 + 2, TOP1 + 2, BX1 - 2, FR1 - 8, "#3a3e4b")   # condenser coil
    for y in range(TOP1 + 3, FR1 - 8, 2):
        s.hline(BX0 + 3, BX1 - 3, y, "#5a6170")
    for x in (BX0 + 4, BX1 - 5, (BX0 + BX1) // 2):
        s.vline(x, TOP1 + 2, FR1 - 8, METAL[2])
    s.rect(BX0 + 3, FR1 - 7, BX1 - 3, FR1 - 2, PLASTIC[1])   # compressor box
    s.hline(BX0 + 3, BX1 - 3, FR1 - 7, PLASTIC[0])
    for x in range(BX0 + 5, BX1 - 4, 2):
        s.px(x, FR1 - 4, PLASTIC[3])
    s.rect(BX1 - 8, TOP1 + 2, BX1 - 3, TOP1 + 6, "#f4f1ea")  # rating label
    s.px(BX1 - 7, TOP1 + 3, RED[1])
    for k in range(5):                                       # power cord down the side
        s.px(BX0 - 1, FR1 - 14 + k * 3, "#1d1f26")
    s.cast(BX0, TOP0 + (FEET - TOP1), BX1, FEET, 30)
    return s.finish()


# ================================================================= side ===
def draw_side(doors_east):
    """Plain side panel; door edges + handles poke out past the door-side edge."""
    s = Sprite(W, H)
    X = IDENT if doors_east else MIRROR
    shell(s)
    bx = X(BX0 + 7, BX0 + 17)[0]
    lid_box(s, bx, TOP0 + 9)
    for x in (BX0 + 7, BX0 + 14):                            # brushed sheen on the side panel
        a = X(x, x + 1)[0]
        s.vline(a, TOP1 + 3, FR1 - 5, STEEL[1])
    va, vb = X(BX0 + 2, BX0 + 9)                             # vent near the back
    for y in (FR1 - 6, FR1 - 4):
        s.hline(va, vb, y, STEEL[3])
    # door edges (thickness) along the door side, with the gasket line + split
    da, db = X(BX1 - 3, BX1)
    s.rect(da, TOP1, db, FR1 - 1, STEEL[3])
    s.vline(X(BX1 - 3, BX1 - 2)[0], TOP1, FR1 - 1, "#5d6470")   # gasket
    s.hline(da, db, SPLIT, "#5d6470")
    # handles stand off the doors, so they stick out past the body edge
    ha, hb = X(BX1, BX1 + 2)
    for y0, y1 in ((TOP1 + 2, SPLIT - 1), (SPLIT + 3, SPLIT + 17)):
        s.rect(ha, y0, hb, y1, CHROME[1])
        s.vline(ha, y0, y1, CHROME[0])
        s.vline(hb - 1, y0, y1, CHROME[2])
    s.cast(BX0, TOP0 + (FEET - TOP1), BX1, FEET, 30)
    return s.finish()


if __name__ == "__main__":
    views = {"front": draw_front(), "back": draw_back(), "left": draw_side(False), "right": draw_side(True)}
    for name, sp in views.items():
        sp.image().save(OUT / f"fridge_{name}.png")
    imgs = [views[k].image() for k in ("front", "back", "left", "right")]
    cooler = Image.open(Path(__file__).parent / "water" / "cooler_front.png")
    gap = 6
    allim = imgs + [cooler]                                  # cooler last, for scale
    sheet = Image.new("RGBA", (sum(i.width for i in allim) + gap * 4, H), (0, 0, 0, 0))
    x = 0
    for im in allim:
        sheet.alpha_composite(im, (x, H - im.height))
        x += im.width + gap
    preview(sheet, OUT / "fridge-preview.png", 8, grid=False)
    print("ok")
