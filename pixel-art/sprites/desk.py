"""Sprite 01 — work desk: one centred monitor, detailed keyboard + mouse on a pad,
open underside (no drawers) with a PC tower standing under the user's right side. 32px grid, top-down 3/4.

Direction = the way the SCREEN faces (the user sits on that side, facing the opposite way):
  desk_front.png  64x64  screen faces the viewer (south)   — user sits south, faces north
  desk_back.png   64x64  screen faces away (north)         — we see the monitor + PC rear
  desk_left.png   32x72  screen faces left (west)          — user sits west, faces east
  desk_right.png  32x72  screen faces right (east)         — user sits east, faces west
Anchor every sprite by its bottom-centre (the feet of the legs) when placing it on the map.
  desk-preview.png  all four on the floor, x8, with the 32px grid
"""
from pathlib import Path

from PIL import Image

from kit import GREEN, KEY, LIP, METAL, PLASTIC, RED, SCREEN, SHADOW, WOOD, WOOD_F, Sprite, preview

OUT = Path(__file__).parent / "desk"
OUT.mkdir(exist_ok=True)

X0, X1 = 1, 60            # desk body (outline lands on 0 and 60)
TOP0, TOP1 = 22, 46       # top face
APRON1 = 49               # front apron bottom
LEG1 = 61                 # legs reach the floor here


def shadow_fill(s, x0, y0, x1, y1, alpha):
    """Semi-transparent dark fill (floor shows through) for the space under the desk."""
    s.a[y0:y1, x0:x1] = list(SHADOW) + [int(255 * alpha)]


def desk_body(s):
    # ---- top face
    s.rect(X0, TOP0, X1, TOP1, WOOD[1])
    for y, x0, x1 in ((25, 4, 12), (28, 40, 55), (31, 3, 14), (37, 46, 57), (40, 4, 13), (43, 30, 44)):
        s.hline(x0, x1, y, WOOD[2])                                   # grain streaks
    s.hline(42, 46, 27, WOOD[0])
    s.hline(6, 10, 39, WOOD[0])
    s.hline(X0, X1, TOP0, WOOD[0])                                    # back edge catches the light
    s.vline(X0, TOP0, TOP1, WOOD[0])                                  # left edge (light from top-left)
    s.vline(X1 - 1, TOP0 + 1, TOP1, WOOD[2])
    s.hline(X0, X1, TOP1 - 1, LIP)                                    # front edge catches the light

    # ---- open underside: dark floor between the legs + the two back legs further in
    shadow_fill(s, X0 + 4, APRON1, X1 - 4, LEG1, 0.68)
    for lx in (X0 + 6, X1 - 9):
        s.rect(lx, APRON1, lx + 3, LEG1 - 5, WOOD_F[3])               # back legs: shorter (further away) + darker
        s.vline(lx, APRON1, LEG1 - 5, WOOD_F[2])

    # ---- apron (thin front panel under the top)
    s.rect(X0, TOP1, X1, APRON1, WOOD_F[1])
    s.hline(X0, X1, TOP1, WOOD_F[0])
    s.hline(X0, X1, APRON1 - 1, WOOD_F[3])

    # ---- legs
    for lx in (X0, X1 - 4):
        s.rect(lx, APRON1, lx + 4, LEG1, WOOD_F[1])
        s.vline(lx, APRON1, LEG1, WOOD_F[0])
        s.vline(lx + 3, APRON1, LEG1, WOOD_F[2])
        s.hline(lx, lx + 4, LEG1 - 1, WOOD_F[3])                      # foot


def pc_tower(s):
    """Tower under the right side of the desk: front panel + a sliver of the left side panel."""
    x0, x1, y0, y1 = 42, 54, APRON1, LEG1
    s.rect(x0 - 2, y0, x0, y1, PLASTIC[2])                            # side panel (in shade)
    s.vline(x0 - 2, y0, y1, PLASTIC[3])
    s.rect(x0, y0, x1, y1, PLASTIC[1])                                # front panel
    s.vline(x0, y0, y1, PLASTIC[0])
    s.vline(x1 - 1, y0, y1, PLASTIC[3])
    s.hline(x0 - 2, x1, y0, PLASTIC[3])                               # top tucked under the apron
    s.rect(x0 + 2, y0 + 2, x1 - 2, y0 + 3, PLASTIC[3])                # drive bay slot
    s.px(x1 - 3, y0 + 2, PLASTIC[0])
    s.px(x0 + 3, y0 + 4, GREEN[0])                                    # power LED
    s.px(x0 + 5, y0 + 4, METAL[0])                                    # power button
    s.px(x0 + 6, y0 + 4, METAL[0])
    for y in range(y0 + 6, y1 - 2, 2):                                # front mesh
        for x in range(x0 + 2 + (y // 2) % 2, x1 - 2, 2):
            s.px(x, y, PLASTIC[3])
    s.vline(x0 + 1, y0 + 6, y1 - 2, RED[1])                           # Gastron-red light strip
    s.px(x0 + 1, y0 + 6, RED[0])
    s.hline(x0 - 2, x1, y1 - 1, PLASTIC[3])                           # feet


def keyboard(s):
    """28x9 keyboard: dark rim, 4 rows of 2px keycaps (lit top + shaded edge), red Esc, wide space bar."""
    x0, x1, y0, y1 = 16, 44, 33, 42
    s.rrect(x0, y0, x1, y1, KEY[2], 1)                                # rim
    s.hline(x0 + 1, x1 - 1, y0, KEY[1])                               # rim catches the light
    s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, "#7d776b")                 # dark deck = gaps between keys

    def key(x, y, w=2, c=KEY[0], edge=KEY[2]):
        s.hline(x, x + w, y, c)
        s.hline(x, x + w, y + 1, edge)

    # row 1: Esc + F-keys
    key(18, 34, 2, RED[0], RED[2])
    for x in range(22, 42, 3):
        key(x, 34)
    # row 2: numbers (staggered against row 1)
    for x in range(20, 41, 3):
        key(x, 36)
    # row 3: tab, letters (staggered again), wide enter
    key(18, 38, 2)
    for x in range(21, 36, 3):
        key(x, 38)
    key(36, 38, 6)
    # row 4: ctrl / alt / space bar / arrows
    key(18, 40, 3)
    key(22, 40, 2)
    key(25, 40, 11)                                   # space bar
    key(37, 40, 2)
    key(40, 40, 2, "#cfe8ee", "#9fc4cc")                                 # arrow key (blue-ish cap)
    s.hline(x0, x1, y1 - 1, KEY[3])                                  # front edge
    s.px(x1 - 3, y0 + 1, GREEN[0])                                    # caps-lock LED


def mouse_and_pad(s):
    # pad
    px0, px1, py0, py1 = 46, 58, 32, 43
    s.rrect(px0, py0, px1, py1, "#2e323e", 1)
    s.rect(px0 + 1, py0 + 1, px1 - 1, py1 - 1, "#3a3f4e")
    s.hline(px0 + 1, px1 - 1, py0 + 1, "#4a5062")
    s.hline(px0 + 1, px1 - 1, py1 - 2, RED[1])                        # red stitched edge
    s.px(px0 + 2, py0 + 3, "#4a5062")
    # mouse (5x7): two buttons, wheel, palm rest, shading
    mx, my = 50, 34
    s.rrect(mx, my, mx + 5, my + 7, KEY[1], 1)
    s.vline(mx, my + 1, my + 6, KEY[0])                               # lit left side
    s.vline(mx + 4, my + 1, my + 6, KEY[2])
    s.hline(mx + 1, mx + 4, my + 6, KEY[3])                           # underside shade
    s.vline(mx + 2, my, my + 3, KEY[3])                               # button split
    s.px(mx + 2, my + 1, "#4a5062")                                   # scroll wheel
    s.px(mx + 1, my, KEY[0])
    s.hline(mx + 1, mx + 4, my + 3, KEY[2])                           # button seam
    s.px(mx + 2, my + 5, RED[1])                                      # tiny logo


def monitor(s):
    s.rect(28, 20, 34, 29, METAL[1])                                  # neck
    s.vline(28, 20, 29, METAL[0])
    s.vline(33, 20, 29, METAL[2])
    s.rrect(23, 28, 39, 32, METAL[1], 1)                              # foot
    s.hline(24, 38, 28, METAL[0])
    s.hline(24, 38, 31, METAL[3])

    BX0, BX1, BY0, BY1 = 14, 48, 3, 23                                # bezel
    s.rect(BX0 + 1, BY0 - 2, BX1 - 1, BY0, "#6b7386")                 # top of the monitor (its thickness, lit)
    s.hline(BX0 + 2, BX1 - 2, BY0 - 2, "#8a93a6")
    s.px(BX1 - 2, BY0 - 1, PLASTIC[2])
    s.rrect(BX0, BY0, BX1, BY1, PLASTIC[1], 1)
    s.hline(BX0 + 1, BX1 - 1, BY0, PLASTIC[0])
    s.vline(BX0, BY0 + 1, BY1 - 1, PLASTIC[0])
    s.rect(BX0 + 1, BY1 - 3, BX1 - 1, BY1, PLASTIC[2])                # chin
    s.hline(BX0 + 1, BX1 - 1, BY1 - 1, PLASTIC[3])
    s.px(BX1 - 4, BY1 - 2, GREEN[0])                                  # power LED

    SX0, SX1, SY0, SY1 = BX0 + 2, BX1 - 2, BY0 + 2, BY1 - 3           # screen 30x15
    for y in range(SY0, SY1):
        s.hline(SX0, SX1, y, SCREEN[1] if (y - SY0) / (SY1 - SY0) < 0.55 else SCREEN[2])
    s.rect(SX0, SY0, SX1, SY0 + 2, SCREEN[3])                         # title bar
    for i, c in enumerate((RED[0], "#f6d04d", GREEN[0])):
        s.px(SX0 + 1 + i * 2, SY0, c)
    s.rect(SX0, SY0 + 2, SX0 + 6, SY1, SCREEN[2])                     # sidebar
    for k in range(3):
        s.hline(SX0 + 1, SX0 + 5, SY0 + 4 + k * 3, SCREEN[0])
    s.hline(SX0 + 8, SX0 + 18, SY0 + 4, "#ffffff")                    # heading + text
    s.hline(SX0 + 8, SX0 + 15, SY0 + 6, SCREEN[3])
    s.hline(SX0 + 8, SX0 + 17, SY0 + 8, SCREEN[3])
    for i, (h, c) in enumerate(((4, RED[1]), (6, GREEN[1]), (3, "#f6b066"), (7, GREEN[1]))):   # KPI bars
        s.rect(SX0 + 20 + i * 2, SY1 - 1 - h, SX0 + 21 + i * 2, SY1 - 1, c)
    s.hline(SX0 + 19, SX1 - 1, SY1 - 1, SCREEN[3])
    for k in range(4):                                                # glare
        s.px(SX1 - 2 - k, SY0 + 3 + k, SCREEN[0])


def draw_desk():
    s = Sprite(64, 64)
    desk_body(s)
    pc_tower(s)
    keyboard(s)
    mouse_and_pad(s)
    monitor(s)
    s.cast(X0, TOP0 + (LEG1 - TOP1), X1, LEG1, LEG1 - TOP1)          # footprint under the top, desk height
    return s.finish()


# ============================================================ back view ===
def pc_tower_rear(s):
    """Tower under the viewer's LEFT (= the user's right when they sit on the far side), seen from behind."""
    x0, x1, y0, y1 = 8, 20, APRON1, LEG1
    s.rect(x1, y0, x1 + 2, y1, PLASTIC[2])                            # side panel sliver (shade side)
    s.vline(x1 + 1, y0, y1, PLASTIC[3])
    s.rect(x0, y0, x1, y1, PLASTIC[2])                                # rear panel
    s.vline(x0, y0, y1, PLASTIC[1])
    s.hline(x0, x1 + 2, y0, PLASTIC[3])
    s.rect(x0 + 2, y0 + 2, x0 + 5, y0 + 7, METAL[1])                  # I/O shield
    for yy in (y0 + 3, y0 + 5):
        s.px(x0 + 3, yy, PLASTIC[3])
    s.px(x0 + 4, y0 + 3, "#3f7fc8")                                   # USB / LAN ports
    s.px(x0 + 4, y0 + 5, GREEN[0])
    s.disc(x0 + 8.5, y0 + 4, 2.4, 2.4, PLASTIC[3])                    # exhaust fan
    s.px(x0 + 8, y0 + 4, PLASTIC[1])
    s.px(x0 + 9, y0 + 3, PLASTIC[1])
    s.rect(x0 + 2, y1 - 4, x1 - 2, y1 - 1, METAL[2])                  # PSU
    s.hline(x0 + 3, x1 - 3, y1 - 3, PLASTIC[3])
    s.px(x1 - 3, y1 - 3, RED[1])                                      # PSU switch
    s.hline(x0, x1 + 2, y1 - 1, PLASTIC[3])
    for k in range(4):                                                # cables drooping to the floor
        s.px(x1 + 3, y0 + 3 + k, "#1d1f26")
    s.px(x1 + 4, y0 + 7, "#1d1f26")


def mouse_pad_back(s):
    """Pad + mouse on the user's right (viewer's left); mouse buttons point south, toward the monitor."""
    px0, px1, py0, py1 = 3, 15, 24, 35
    s.rrect(px0, py0, px1, py1, "#2e323e", 1)
    s.rect(px0 + 1, py0 + 1, px1 - 1, py1 - 1, "#3a3f4e")
    s.hline(px0 + 1, px1 - 1, py0 + 1, RED[1])                        # stitched edge, far from monitor
    mx, my = 7, 26
    s.rrect(mx, my, mx + 5, my + 7, KEY[1], 1)
    s.vline(mx, my + 1, my + 6, KEY[0])
    s.vline(mx + 4, my + 1, my + 6, KEY[2])
    s.vline(mx + 2, my + 4, my + 7, KEY[3])                           # button split (south end)
    s.px(mx + 2, my + 5, "#4a5062")                                   # wheel
    s.hline(mx + 1, mx + 4, my + 3, KEY[2])
    s.hline(mx + 1, mx + 4, my + 6, KEY[3])


def monitor_rear(s):
    BX0, BX1, BY0, BY1 = 14, 48, 14, 36
    s.rect(BX0 + 1, BY0 - 2, BX1 - 1, BY0, "#5a6274")                 # top of the monitor
    s.hline(BX0 + 2, BX1 - 2, BY0 - 2, "#79829a")
    s.rrect(BX0, BY0, BX1, BY1, PLASTIC[2], 1)                        # rear shell
    s.hline(BX0 + 1, BX1 - 1, BY0, PLASTIC[1])
    s.vline(BX0, BY0 + 1, BY1 - 1, PLASTIC[1])
    s.hline(BX0 + 1, BX1 - 1, BY1 - 1, PLASTIC[3])
    s.rrect(22, 18, 40, 31, PLASTIC[1], 2)                            # moulded hump
    s.hline(24, 38, 18, PLASTIC[0])
    s.hline(24, 38, 30, PLASTIC[3])
    for k in range(5):                                                # vent slits
        s.hline(25 + k * 3, 27 + k * 3, 21, PLASTIC[3])
        s.hline(25 + k * 3, 27 + k * 3, 23, PLASTIC[3])
    s.px(BX0 + 3, BY0 + 3, RED[1])                                    # little red brand dot
    s.rect(28, 28, 34, 41, METAL[1])                                  # neck in front of the shell
    s.vline(28, 28, 41, METAL[0])
    s.vline(33, 28, 41, METAL[2])
    s.rect(29, 30, 33, 32, METAL[2])                                  # cable clip
    s.rrect(23, 40, 39, 44, METAL[1], 1)                              # foot
    s.hline(24, 38, 40, METAL[0])
    s.hline(24, 38, 43, METAL[3])
    s.px(30, 36, "#1d1f26")                                           # cable through the clip
    s.px(31, 37, "#1d1f26")


def draw_desk_back():
    s = Sprite(64, 64)
    desk_body(s)
    pc_tower_rear(s)
    mouse_pad_back(s)
    monitor_rear(s)
    s.cast(X0, TOP0 + (LEG1 - TOP1), X1, LEG1, LEG1 - TOP1)
    return s.finish()


# ============================================================ side views ===
SW, SH = 32, 72
SX0, SX1 = 1, 29           # desk end is 28 wide (the desk's depth)
STOP0, STOP1 = 10, 55      # top face: the desk's length, foreshortened
SAPRON = 58
SLEG = 70


def draw_desk_side(screen_west):
    """Desk turned 90 degrees. screen_west=True -> 'left' sprite (screen faces west, user sits west).
    Light stays top-left in both, so the right sprite is drawn, not mirrored."""
    s = Sprite(SW, SH)
    X = (lambda a, b: (a, b)) if screen_west else (lambda a, b: (SX0 + SX1 - b, SX0 + SX1 - a))

    # ---- top face (grain now runs vertically, along the desk's length)
    s.rect(SX0, STOP0, SX1, STOP1, WOOD[1])
    for x, y0, y1 in ((5, 13, 27), (11, 34, 50), (17, 15, 24), (23, 30, 46), (8, 44, 52), (20, 48, 53)):
        s.vline(x, y0, y1, WOOD[2])
    s.vline(18, 25, 29, WOOD[0])
    s.hline(SX0, SX1, STOP0, WOOD[0])
    s.vline(SX0, STOP0, STOP1, WOOD[0])
    s.vline(SX1 - 1, STOP0 + 1, STOP1, WOOD[2])
    s.hline(SX0, SX1, STOP1 - 1, LIP)

    # ---- underside, apron, legs (the desk's short end faces us)
    shadow_fill(s, SX0 + 4, SAPRON, SX1 - 4, SLEG, 0.68)
    for lx in (SX0 + 6, SX1 - 9):
        s.rect(lx, SAPRON, lx + 3, SLEG - 5, WOOD_F[3])
        s.vline(lx, SAPRON, SLEG - 5, WOOD_F[2])
    if screen_west:                                                   # tower sits under the user's right = south end
        tx0, tx1 = 7, 21                                              # its side panel faces us
        s.rect(tx0, SAPRON, tx1, SLEG, PLASTIC[1])
        s.vline(tx0, SAPRON, SLEG, PLASTIC[0])                        # front edge (faces the user, west)
        s.vline(tx1 - 1, SAPRON, SLEG, PLASTIC[3])
        s.hline(tx0, tx1, SAPRON, PLASTIC[3])
        s.rect(tx0 + 3, SAPRON + 2, tx1 - 2, SLEG - 3, "#1d1f26")     # glass window
        s.disc(tx0 + 8, SAPRON + 6, 2.2, 2.2, darken_hex(RED[1]))
        s.px(tx0 + 8, SAPRON + 6, RED[0])
        s.hline(tx0 + 3, tx1 - 2, SLEG - 4, RED[2])                   # red glow line
        s.px(tx0 + 1, SAPRON + 2, GREEN[0])                           # power LED on the front edge
        s.hline(tx0, tx1, SLEG - 1, PLASTIC[3])
    s.rect(SX0, STOP1, SX1, SAPRON, WOOD_F[1])
    s.hline(SX0, SX1, STOP1, WOOD_F[0])
    s.hline(SX0, SX1, SAPRON - 1, WOOD_F[3])
    for lx in (SX0, SX1 - 4):
        s.rect(lx, SAPRON, lx + 4, SLEG, WOOD_F[1])
        s.vline(lx, SAPRON, SLEG, WOOD_F[0])
        s.vline(lx + 3, SAPRON, SLEG, WOOD_F[2])
        s.hline(lx, lx + 4, SLEG - 1, WOOD_F[3])

    # ---- keyboard: 9 wide, 22 long; key rows are columns now.
    # u = position along the keyboard from the user's LEFT end; rows r=0 (Esc row, far) .. 3 (space, near)
    ky0, ky1 = (20, 42) if screen_west else (24, 46)
    kx0, kx1 = X(7, 16)
    s.rrect(kx0, ky0, kx1, ky1, KEY[2], 1)
    s.hline(kx0 + 1, kx1 - 1, ky0, KEY[1])
    s.rect(kx0 + 1, ky0 + 1, kx1 - 1, ky1 - 1, "#7d776b")
    s.hline(kx0, kx1, ky1 - 1, KEY[3])

    def key(r, u0, u1, c=KEY[0], edge=KEY[2]):
        x = X(14 - r * 2, 15 - r * 2)[0]                              # far row sits next to the monitor
        a, b = (ky0 + 1 + u0, ky0 + 1 + u1) if screen_west else (ky1 - 1 - u1, ky1 - 1 - u0)
        s.vline(x, a, b - 1, c)
        s.px(x, b - 1, edge)

    key(0, 0, 2, RED[0], RED[2])                                      # Esc at the user's left end
    for u in range(4, 19, 3):
        key(0, u, u + 2)
    for u in range(1, 19, 3):
        key(1, u, u + 2)
    key(2, 0, 2)
    for u in range(3, 15, 3):
        key(2, u, u + 2)
    key(2, 15, 20)                                                    # enter
    key(3, 0, 3)
    key(3, 4, 6)
    key(3, 7, 16)                                                     # space bar
    key(3, 17, 20, "#cfe8ee", "#9fc4cc")

    # ---- mouse pad + mouse on the user's right
    pya, pyb = (45, 54) if screen_west else (12, 22)
    pxa, pxb = X(5, 16)
    s.rrect(pxa, pya, pxb, pyb, "#2e323e", 1)
    s.rect(pxa + 1, pya + 1, pxb - 1, pyb - 1, "#3a3f4e")
    s.hline(pxa + 1, pxb - 1, pya + 1, "#4a5062")
    ex = X(6, 7)[0]                                                  # stitched edge on the user's side
    s.vline(ex, pya + 1, pyb - 1, RED[1])
    ma, mb = X(8, 14)                                                # mouse: long axis points at the monitor
    my = pya + 3
    s.rrect(ma, my, mb, my + 4, KEY[1], 1)
    s.hline(ma + 1, mb - 1, my, KEY[0])
    s.hline(ma + 1, mb - 1, my + 3, KEY[3])
    s.vline(X(10, 11)[0], my + 1, my + 3, KEY[2])                     # seam between buttons and palm
    s.px(X(12, 13)[0], my + 2, KEY[3])                                # button split
    s.px(X(11, 12)[0], my + 1, "#4a5062")                             # wheel

    # ---- monitor seen edge-on: slim panel, glowing screen edge on the user's side, back hump + stand
    pa, pb = X(19, 24)                                                # panel
    s.rrect(pa, 10, pb, 41, PLASTIC[1], 1)
    s.hline(pa + 1, pb - 1, 10, PLASTIC[0])                           # top edge catches the light
    s.vline(pa, 11, 40, PLASTIC[0])
    s.vline(pb - 1, 11, 40, PLASTIC[3])
    sx = X(19, 20)[0]                                                 # screen edge glow
    for y in range(12, 38):
        s.px(sx, y, SCREEN[1] if y < 25 else SCREEN[2])
    s.px(sx, 13, SCREEN[0])
    s.hline(pa, pb, 39, PLASTIC[2])                                   # chin
    s.hline(pa, pb, 40, PLASTIC[3])
    s.px(sx, 39, GREEN[0])
    ha, hb = X(24, 27)                                                # moulded back hump
    s.rrect(ha, 17, hb, 33, PLASTIC[2], 1)
    s.vline(ha, 18, 32, PLASTIC[1])
    for y in (21, 24, 27):
        s.px(X(25, 26)[0], y, PLASTIC[3])                             # vent slits
    na, nb = X(24, 27)                                                # neck down to the foot
    s.rect(na, 33, nb, 38, METAL[1])
    s.vline(na, 33, 38, METAL[0])
    s.vline(nb - 1, 33, 38, METAL[2])
    fa, fb = X(17, 28)                                                # foot
    s.rrect(fa, 38, fb, 42, METAL[1], 1)
    s.hline(fa + 1, fb - 1, 38, METAL[0])
    s.hline(fa + 1, fb - 1, 41, METAL[3])
    s.cast(SX0, STOP0 + (SLEG - STOP1), SX1, SLEG, SLEG - STOP1)     # long footprint: the desk's full length
    return s.finish()


def darken_hex(c, t=0.35):
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * (1 - t)), int(g * (1 - t)), int(b * (1 - t)))


# ================================================================ main ===
if __name__ == "__main__":
    sprites = {
        "front": draw_desk(),
        "back": draw_desk_back(),
        "left": draw_desk_side(True),
        "right": draw_desk_side(False),
    }
    for name, sp in sprites.items():
        sp.image().save(OUT / f"desk_{name}.png")
    # one preview sheet, all four bottom-aligned on the floor
    gap = 8
    order = ["front", "back", "left", "right"]
    imgs = [sprites[k].image() for k in order]
    sheet = Image.new("RGBA", (sum(i.width for i in imgs) + gap * 3, max(i.height for i in imgs)), (0, 0, 0, 0))
    x = 0
    for im in imgs:
        sheet.alpha_composite(im, (x, sheet.height - im.height))
        x += im.width + gap
    preview(sheet, OUT / "desk-preview.png", 6, grid=False)
    print("ok")
