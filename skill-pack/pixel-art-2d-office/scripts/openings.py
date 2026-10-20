"""Sprite 15 — door + windows for the wall face (front view only), target style:
chunky readable shapes, few colours, full dark outline, lit horizontal ledges (door header,
window sill) as the 'top' bands, short shadow on the wall.

  door.png           36x60  wood door in a dark casing: glass vision panel, raised panel,
                            chrome lever, kick plate, threshold, small Gastron room plate
  window.png         52x36  white frame, 4 panes, sky + distant skyline, glints, deep sill
  window_blinds.png  52x36  same window with the blinds half lowered
Outputs in ./openings/ + openings-preview.png (on the wall with the posters + clock)
"""
from pathlib import Path

from PIL import Image

from kit import GREEN, RED, WOOD, WOOD_F, Sprite
from wallitems import wall_bg

OUT = Path(__file__).parent / "openings"
OUT.mkdir(exist_ok=True)
WHITE = ["#ffffff", "#eef0f2", "#d3d8df", "#a9b0bb"]
SKY = ["#d4f0fa", "#a8dcf0", "#7cc4e4", "#5aa6cc"]
CITY = ["#9cc0d4", "#86aec4", "#7099b0"]
CHROME = ["#ffffff", "#c9ced6", "#7d8590"]


def glass(s, x0, y0, x1, y1, skyline=True):
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        s.hline(x0, x1, y, SKY[0] if t < 0.3 else SKY[1] if t < 0.65 else SKY[2])
    if skyline:
        x, k = x0, 0
        while x < x1:
            bw = 3 + (k * 5) % 4
            bh = 3 + (k * 7) % 6
            s.rect(x, y1 - bh, min(x1, x + bw), y1, CITY[k % 3])
            if bh > 4:
                s.px(x + 1, y1 - bh + 2, "#d4f0fa")              # a lit window in the tower
            x += bw + 1
            k += 1
    for g in range(3):                                          # diagonal glints
        s.px(x0 + 2 + g, y0 + 4 - g, "#ffffff")
        s.px(x0 + 5 + g, y0 + 5 - g, "#ffffff")


# ================================================================= door ===
def draw_door():
    s = Sprite(36, 60)
    # casing (frame) with a lit header band on top
    s.rect(2, 4, 34, 58, WOOD_F[2])
    s.rect(2, 2, 34, 5, WOOD[1])                                # header ledge seen from above
    s.hline(2, 34, 2, WOOD[0])
    s.hline(2, 34, 4, WOOD_F[1])
    s.vline(2, 5, 58, WOOD_F[1])
    # door slab
    x0, x1, y0, y1 = 5, 31, 6, 56
    s.rect(x0, y0, x1, y1, WOOD[1])
    s.vline(x0, y0, y1, WOOD[0])
    s.vline(x1 - 1, y0, y1, WOOD[2])
    s.hline(x0, x1, y0, WOOD[0])
    # glass vision panel (upper) + raised panel (lower)
    s.rect(x0 + 4, y0 + 4, x1 - 4, y0 + 18, WOOD_F[1])
    glass(s, x0 + 5, y0 + 5, x1 - 5, y0 + 17, skyline=False)
    s.rect(x0 + 4, y0 + 22, x1 - 4, y1 - 9, WOOD[2])
    s.hline(x0 + 4, x1 - 4, y0 + 22, WOOD_F[1])                 # top edge of the recess (in shade)
    s.vline(x0 + 4, y0 + 22, y1 - 9, WOOD_F[1])
    s.rect(x0 + 6, y0 + 24, x1 - 6, y1 - 11, WOOD[1])           # the raised panel
    s.hline(x0 + 6, x1 - 6, y0 + 24, WOOD[0])
    # chrome lever handle + lock
    s.rect(x1 - 6, y0 + 20, x1 - 4, y0 + 24, CHROME[2])         # rose
    s.rect(x1 - 10, y0 + 21, x1 - 5, y0 + 23, CHROME[1])        # lever
    s.hline(x1 - 10, x1 - 5, y0 + 21, CHROME[0])
    s.px(x1 - 5, y0 + 26, CHROME[2])                            # keyhole
    # kick plate
    s.rect(x0 + 1, y1 - 6, x1 - 1, y1 - 1, CHROME[1])
    s.hline(x0 + 1, x1 - 1, y1 - 6, CHROME[0])
    s.hline(x0 + 1, x1 - 1, y1 - 2, CHROME[2])
    # room plate on the glass rail: red dot = Gastron
    s.rect(x0 + 9, y0 + 1, x1 - 9, y0 + 3, "#f4f1ea")
    s.px(x0 + 10, y0 + 2, RED[1])
    s.hline(x0 + 12, x1 - 10, y0 + 2, "#7d8590")
    # threshold strip
    s.rect(3, 56, 33, 58, "#7d8590")
    s.hline(3, 33, 56, "#a9b0bb")
    s.finish(shadow=False, full_outline=True, rim=0)
    return s.wall_shadow()


# =============================================================== window ===
def window_frame(s):
    x0, x1, y0, y1 = 3, 49, 3, 28
    s.rect(x0, y0, x1, y1, WHITE[2])                            # frame
    s.hline(x0, x1, y0, WHITE[0])
    s.vline(x0, y0, y1, WHITE[1])
    s.vline(x1 - 1, y0, y1, WHITE[3])
    gx0, gx1, gy0, gy1 = x0 + 2, x1 - 2, y0 + 2, y1 - 1
    glass(s, gx0, gy0, gx1, gy1)
    mx = (x0 + x1) // 2
    s.rect(mx - 1, y0, mx + 1, y1, WHITE[1])                    # mullion
    s.vline(mx + 0, y0, y1, WHITE[2])
    s.rect(x0, 14, x1, 16, WHITE[1])                            # transom
    s.hline(x0, x1, 15, WHITE[2])
    s.px(mx + 3, 21, WHITE[3])                                  # latch
    s.px(mx + 4, 21, WHITE[3])
    return x0, x1, y0, y1


def sill(s, y=28):
    """Deep sill: a lit top band (seen from above) sticking out past the frame + dark front."""
    s.rect(1, y, 51, y + 3, WHITE[0])
    s.hline(1, 51, y + 2, WHITE[1])
    s.rect(1, y + 3, 51, y + 5, WHITE[3])
    s.disc(41, y + 1, 2.6, 1.2, "#c97a4a")                      # tiny cactus pot on the sill
    s.rect(40, y - 4, 43, y + 1, GREEN[1])
    s.vline(40, y - 4, y + 1, "#3fc47a")


def draw_window():
    s = Sprite(52, 36)
    window_frame(s)
    sill(s)
    s.finish(shadow=False, full_outline=True, rim=0)
    return s.wall_shadow()


def draw_window_blinds():
    s = Sprite(52, 36)
    x0, x1, y0, y1 = window_frame(s)
    s.rect(x0 + 1, y0 - 1, x1 - 1, y0 + 2, WHITE[3])            # blind head rail
    s.hline(x0 + 1, x1 - 1, y0 - 1, WHITE[1])
    for y in range(y0 + 2, 19, 2):                              # slats, lowered just past halfway
        s.hline(x0 + 2, x1 - 2, y, WHITE[1])
        s.hline(x0 + 2, x1 - 2, y + 1, WHITE[2])
    s.rect(x0 + 2, 19, x1 - 2, 21, WHITE[3])                    # bottom rail
    s.hline(x0 + 2, x1 - 2, 19, WHITE[1])
    s.vline(x1 - 5, y0 + 2, 26, "#7d8590")                       # pull cord
    s.rect(x1 - 6, 26, x1 - 4, 28, RED[1])                       # red cord toggle
    sill(s)
    s.finish(shadow=False, full_outline=True, rim=0)
    return s.wall_shadow()


if __name__ == "__main__":
    door, win, blinds = draw_door(), draw_window(), draw_window_blinds()
    door.image().save(OUT / "door.png")
    win.image().save(OUT / "window.png")
    blinds.image().save(OUT / "window_blinds.png")
    root = Path(__file__).parent
    W, H = 230, 72
    bg = wall_bg(W, H)
    bg.alpha_composite(door.image(), (6, H - 2 - 60 + 2))
    bg.alpha_composite(win.image(), (48, 10))
    bg.alpha_composite(Image.open(root / "posters" / "poster_flame.png"), (104, 10))
    bg.alpha_composite(blinds.image(), (144, 10))
    bg.alpha_composite(Image.open(root / "wall" / "clock.png"), (198, 12))
    bg.convert("RGB").resize((W * 5, H * 5), Image.NEAREST).save(OUT / "openings-preview.png")
    print("ok")
