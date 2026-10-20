"""Sprite 16 — room tiles on the 32 px grid (all seamless where they repeat).

Wall tiles are 32 wide and 64 tall: the wall's TOP (its thickness seen from above) as a thick
cap band, then the plaster face, a wood wainscot with a lit chair rail, a dark baseboard.
They repeat left-right without seams.

  wall.png         32x64  plain wall
  wall_switch.png  32x64  plain wall + double light switch plate
  wall_pillar.png  32x72  a square pillar standing proud of the wall: its own (bigger, lighter)
                          cap, a lit front face, a base, and it steps 8 px out onto the floor
  floor_a.png      32x32  warm wood planks, staggered joints (tiles in both directions)
  floor_b.png      32x32  same planks with different joints/grain, mix with floor_a to break repeats
Outputs in ./tiles/ + tiles-preview.png (a little room built from them, with furniture)
"""
from pathlib import Path

import numpy as np
from PIL import Image

from kit import OL, SHADOW, WOOD, WOOD_F, Sprite, hx

OUT = Path(__file__).parent / "tiles"
OUT.mkdir(exist_ok=True)
T = 32
CAP = ["#6a5a62", "#54464e", "#3e3239", "#2c2229"]          # wall top (thickness)
PLASTER = ["#f0e7cf", "#e6dbc0", "#d9ccae", "#c8b996"]
FLOOR = ["#dcc296", "#d2b78c", "#cbaf84", "#b8996f", "#9c805c"]   # plank tones kept close so no stripes show when tiled


def H(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2246822519 + 1013904223) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFFFFFF) / 4294967296


CAP1, FACE1, RAIL, WAIN1, BASE1 = 9, 38, 40, 56, 62          # band boundaries (y)


def wall_strip(s, x0=0, x1=T):
    """One seamless wall column x0..x1 (x positions wrap mod 32 so tiles join cleanly)."""
    # cap: top of the wall seen from above (thick band, lit near edge, dark outline on top)
    s.rect(x0, 0, x1, CAP1, CAP[1])
    s.hline(x0, x1, 0, OL)
    s.hline(x0, x1, 1, CAP[0])
    for x in range(x0, x1):
        if H(x % T, 3, 1) < 0.18:
            s.px(x, 4 + int(H(x % T, 4, 2) * 3), CAP[2])           # speckle
    s.hline(x0, x1, CAP1 - 2, CAP[0])                            # front edge of the wall top
    s.hline(x0, x1, CAP1 - 1, CAP[3])
    # plaster face with soft vertical trowel marks
    s.rect(x0, CAP1, x1, FACE1, PLASTER[1])
    s.hline(x0, x1, CAP1, PLASTER[3])                            # shade right under the cap
    s.hline(x0, x1, CAP1 + 1, PLASTER[2])
    for x in range(x0, x1):
        if H(x % T, 9, 3) < 0.12:                                 # very soft plaster texture
            y0 = CAP1 + 4 + int(H(x % T, 10, 4) * 18)
            s.vline(x, y0, min(FACE1 - 1, y0 + 2 + int(H(x % T, 11, 5) * 3)), "#e0d4b7")
        if H(x % T, 12, 6) < 0.08:
            s.px(x, CAP1 + 4 + int(H(x % T, 13, 7) * 20), PLASTER[0])
    # chair rail (a little ledge: lit top) + wood wainscot panels
    s.rect(x0, FACE1, x1, RAIL + 1, WOOD[1])
    s.hline(x0, x1, FACE1, WOOD[0])
    s.hline(x0, x1, RAIL, WOOD_F[1])
    s.rect(x0, RAIL + 1, x1, WAIN1, WOOD_F[1])
    for x in range(x0, x1):
        if x % 16 == 0:
            s.vline(x, RAIL + 1, WAIN1, WOOD_F[3])               # panel joints every half tile
        elif x % 16 == 1:
            s.vline(x, RAIL + 1, WAIN1, WOOD_F[0])
    for x in range(x0, x1):
        if H(x % T, 20, 8) < 0.3:
            s.px(x, RAIL + 4 + int(H(x % T, 21, 9) * 10), WOOD_F[2])
    # baseboard
    s.rect(x0, WAIN1, x1, BASE1, WOOD_F[3])
    s.hline(x0, x1, WAIN1, WOOD_F[2])
    s.rect(x0, BASE1, x1, 64, "#1f160f")                         # contact line with the floor


def draw_wall():
    s = Sprite(T, 64)
    wall_strip(s)
    return s


def draw_switch():
    s = draw_wall()
    x0, y0 = 12, 22
    s.rect(x0 + 1, y0 + 1, x0 + 9, y0 + 12, "#b9aa86")           # plate's shadow on the wall
    s.rect(x0, y0, x0 + 8, y0 + 11, "#f7f4ec")                   # plate
    s.hline(x0, x0 + 8, y0, "#ffffff")
    s.vline(x0 + 7, y0, y0 + 11, "#d3cfc4")
    s.hline(x0, x0 + 8, y0 + 10, "#c9c4b8")
    for rx in (x0 + 1, x0 + 4):                                  # two rockers
        s.rect(rx, y0 + 2, rx + 3, y0 + 9, "#e6e2da")
        s.hline(rx, rx + 3, y0 + 2, "#ffffff")                   # upper half pressed in (lit)
        s.rect(rx, y0 + 6, rx + 3, y0 + 9, "#d3cfc4")
        s.px(rx + 1, y0 + 4, "#3fc47a")                          # little 'on' indicator
    m = np.zeros((64, T), bool)                                  # thin outline round the plate
    m[y0:y0 + 11, x0:x0 + 8] = True
    ring = np.zeros_like(m)
    ring[1:, :] |= m[:-1, :]; ring[:-1, :] |= m[1:, :]; ring[:, 1:] |= m[:, :-1]; ring[:, :-1] |= m[:, 1:]
    ring &= ~m
    s.a[ring] = list(hx("#8d8678")) + [255]
    return s


def draw_pillar():
    s = Sprite(T, 72)
    wall_strip(s)
    px0, px1 = 5, 27                                             # pillar width
    # the pillar's shadow on the wall to its right (light from the upper-left)
    s.rect(px1, CAP1, min(T, px1 + 3), BASE1, PLASTER[3])
    # its cap: lighter & bigger than the wall's, sticks out 8 px toward us
    s.rect(px0 - 1, 0, px1 + 1, CAP1 + 8, PLASTER[0])
    s.hline(px0 - 1, px1 + 1, 0, "#ffffff")
    s.rect(px0 - 1, CAP1 + 6, px1 + 1, CAP1 + 9, PLASTER[2])    # cap's front edge (moulding)
    s.hline(px0 - 1, px1 + 1, CAP1 + 6, PLASTER[1])
    # front face, lit left edge, darker right edge
    s.rect(px0, CAP1 + 9, px1, 64, PLASTER[1])
    s.vline(px0, CAP1 + 9, 64, PLASTER[0])
    s.vline(px0 + 1, CAP1 + 9, 64, PLASTER[0])
    s.vline(px1 - 1, CAP1 + 9, 64, PLASTER[3])
    s.vline(px1 - 2, CAP1 + 9, 64, PLASTER[2])
    for y in range(CAP1 + 12, 58, 9):                            # faint stone-block joints
        s.hline(px0 + 2, px1 - 2, y, PLASTER[2])
    # base plinth stepping onto the floor
    s.rect(px0 - 1, 62, px1 + 1, 70, WOOD_F[2])
    s.hline(px0 - 1, px1 + 1, 62, WOOD_F[1])
    s.hline(px0 - 1, px1 + 1, 69, WOOD_F[3])
    # outline the pillar silhouette (full outline, target style)
    m = np.zeros((72, T), bool)
    m[0:CAP1 + 9, px0 - 1:px1 + 1] = True
    m[CAP1 + 9:62, px0:px1] = True
    m[62:70, px0 - 1:px1 + 1] = True
    ring = np.zeros_like(m)
    ring[1:, :] |= m[:-1, :]; ring[:-1, :] |= m[1:, :]; ring[:, 1:] |= m[:, :-1]; ring[:, :-1] |= m[:, 1:]
    ring &= ~m
    s.a[ring] = list(hx(OL)) + [255]
    s.a[70:72, px1 + 1:min(T, px1 + 4)] = list(SHADOW) + [80]   # small contact shadow on the floor
    return s


def draw_floor(seed):
    s = Sprite(T, T)
    s.rect(0, 0, T, T, FLOOR[1])
    for row in range(4):                                         # 4 planks of 8 px per tile
        y = row * 8
        joints = sorted({int(H(row, seed, 1) * T), (int(H(row, seed, 1) * T) + 13 + int(H(row, seed, 2) * 8)) % T})
        bounds = joints + [joints[0] + T]
        for a, b in zip(bounds, bounds[1:]):                     # each plank, wrapping around the tile
            c = FLOOR[1 + int(H(a, row, seed + 3) * 2)]
            for x in range(a, b):
                s.vline(x % T, y, y + 7, c)
            for k in range(2):                                   # grain streaks
                gx = a + 2 + int(H(a, row, seed + 5 + k) * max(1, b - a - 8))
                gy = y + 1 + int(H(a, row, seed + 7 + k) * 5)
                for x in range(gx, gx + 4 + int(H(a, row, seed + 9) * 5)):
                    if x < b - 1:
                        s.px(x % T, gy, FLOOR[2] if c == FLOOR[1] else FLOOR[3])
            s.hline(a % T, a % T + 1, y, FLOOR[0])               # lit plank end
            s.vline(a % T, y, y + 7, FLOOR[4])                   # joint
        s.hline(0, T, y + 7, FLOOR[4])                           # gap between plank rows
    return s


if __name__ == "__main__":
    tiles = {"wall": draw_wall(), "wall_switch": draw_switch(), "wall_pillar": draw_pillar(),
             "floor_a": draw_floor(1), "floor_b": draw_floor(2)}
    for k, v in tiles.items():
        v.image().save(OUT / f"{k}.png")
    root = Path(__file__).parent
    # a little room: 9 tiles wide, wall row + 4 floor rows, with furniture on it
    cols, rows = 9, 4
    room = Image.new("RGBA", (cols * T, 64 + rows * T), (38, 36, 48, 255))
    fa, fb = tiles["floor_a"].image(), tiles["floor_b"].image()
    for r in range(rows):
        for c in range(cols):
            room.alpha_composite(fa if (r * 3 + c) % 2 else fb, (c * T, 64 + r * T))
    walls = ["wall", "wall", "wall_switch", "wall", "wall_pillar", "wall", "wall", "wall", "wall"]
    for c, w in enumerate(walls):
        if w != "wall_pillar":
            room.alpha_composite(tiles[w].image(), (c * T, 0))
    room.alpha_composite(tiles["wall_pillar"].image(), (4 * T, 0))
    room.alpha_composite(Image.open(root / "openings" / "window.png"), (16, 8))
    room.alpha_composite(Image.open(root / "openings" / "door.png"), (6 * T + 6, 4))
    room.alpha_composite(Image.open(root / "wall" / "clock.png"), (3 * T + 7, 14))
    room.alpha_composite(Image.open(root / "posters" / "poster_flame.png"), (5 * T + 5, 10))
    room.alpha_composite(Image.open(root / "posters" / "poster_pig.png"), (7 * T + 14, 10))
    room.alpha_composite(Image.open(root / "plants" / "plant_big.png"), (4 * T + 22, 64))
    room.alpha_composite(Image.open(root / "desk" / "desk_front.png"), (T, 76))
    room.alpha_composite(Image.open(root / "chair" / "chair_back.png"), (T + 15, 120))
    room.alpha_composite(Image.open(root / "sofa" / "sofa_front.png"), (5 * T, 104))
    room.alpha_composite(Image.open(root / "water" / "cooler_front.png"), (8 * T, 52))
    room.convert("RGB").resize((room.width * 3, room.height * 3), Image.NEAREST).save(OUT / "tiles-preview.png")
    # plus a close-up strip of the bare tiles
    strip = Image.new("RGBA", (5 * (T + 8), 72), (38, 36, 48, 255))
    for i, k in enumerate(tiles):
        strip.alpha_composite(tiles[k].image(), (i * (T + 8), 0))
    strip.convert("RGB").resize((strip.width * 6, strip.height * 6), Image.NEAREST).save(OUT / "tiles-closeup.png")
    print("ok")
