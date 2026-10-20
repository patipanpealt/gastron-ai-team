"""Sprite 03 — big meeting table for 12 (5 per long side + 1 at each head). 32px grid, top-down 3/4.

The table is symmetric, so two sprites cover all four directions:
  meeting_h.png   192x80   long axis left-right   (front view == back view)
  meeting_v.png    72x208  long axis up-down      (left view == right view)
Slab legs at both ends (no corner legs), edge-banded top with rounded corners, otherwise bare —
just a flush power grommet (sockets + USB) in the middle of the table.

  meeting/seats.json         chair top-left + which chair sprite to use, per seat, relative to the table
  meeting-preview.png        both tables, bare (x5)
  meeting-set-preview.png    both tables with the approved chairs pulled up (x4)
Drawing order on the map: north/side chairs -> table -> south chairs (they stand in front of the edge).
"""
import json
from pathlib import Path

from PIL import Image

from kit import GREEN, LIP, METAL, PLASTIC, SHADOW, WOOD, WOOD_F, Sprite, preview

OUT = Path(__file__).parent / "meeting"
OUT.mkdir(exist_ok=True)
CHAIRS = Path(__file__).parent / "chair"


def shadow_fill(s, x0, y0, x1, y1, alpha):
    s.a[y0:y1, x0:x1] = list(SHADOW) + [int(255 * alpha)]


# ---------------------------------------------------------------- props ---
def power_slot(s, cx, cy, vertical=False):
    """Flush power grommet in the middle of the table: brushed-metal frame, recessed dark slot,
    3 power sockets + 2 USB ports, hinged lid edge on the far side."""
    def r(x0, y0, x1, y1, c):                       # rect in slot-local coords (u along, v across)
        if vertical:
            s.rect(cx + y0, cy + x0, cx + y1, cy + x1, c)
        else:
            s.rect(cx + x0, cy + y0, cx + x1, cy + y1, c)
    r(-16, -4, 16, 4, METAL[1])                      # frame
    r(-16, -4, 16, -3, METAL[0])                     # lid edge catches the light
    r(-16, 3, 16, 4, METAL[3])
    r(-15, -2, 15, 3, "#1d1f26")                     # recessed slot
    for u in (-12, -6, 0):                           # power sockets
        r(u, -1, u + 4, 2, PLASTIC[1])
        r(u + 1, 0, u + 2, 1, "#1d1f26")
        r(u + 2, 0, u + 3, 1, "#1d1f26")
    for u in (7, 11):                                # USB ports
        r(u, -1, u + 3, 1, METAL[0])
        r(u, 1, u + 3, 2, PLASTIC[2])
    r(13, 0, 14, 1, GREEN[0])                        # power LED



def wood_top(s, x0, y0, x1, y1, grain_vertical):
    """Edge-banded top face with rounded corners, grain along the long axis."""
    s.rrect(x0, y0, x1, y1, WOOD[2], 4)                               # banding (outer ring)
    s.rrect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, WOOD[1], 3)               # main surface
    s.hline(x0 + 4, x1 - 4, y0, WOOD[0])                              # far edge catches the light
    s.vline(x0, y0 + 4, y1 - 4, WOOD[0])
    s.hline(x0 + 4, x1 - 4, y1 - 1, LIP)                              # near edge catches the light
    s.vline(x1 - 1, y0 + 4, y1 - 4, WOOD[3])
    n = 0
    if grain_vertical:
        for x in range(x0 + 6, x1 - 6, 7):
            a = y0 + 6 + (n * 29) % max(1, (y1 - y0 - 40))
            s.vline(x, a, a + 18 + (n * 7) % 14, WOOD[2])
            n += 1
    else:
        for y in range(y0 + 5, y1 - 4, 4):
            a = x0 + 8 + (n * 37) % max(1, (x1 - x0 - 60))
            s.hline(a, a + 26 + (n * 11) % 20, y, WOOD[2])
            if n % 3 == 0:
                s.hline(a + 3, a + 8, y - 1, WOOD[0])
            n += 1


# ============================================================ horizontal ===
HW, HH = 192, 80
HX0, HX1 = 8, 184          # 176 long
HT0, HT1 = 8, 56           # 48 deep
HEDGE = 60                 # thick table-top edge
HFLOOR = 71
SEAT_XS = [32, 64, 96, 128, 160]   # seat centres along the long sides


def draw_h():
    s = Sprite(HW, HH)
    # under the table
    shadow_fill(s, HX0 + 6, HEDGE, HX1 - 6, HFLOOR, 0.68)
    for lx in (HX0 + 12, HX1 - 16):                                   # far slab legs, further back + darker
        s.rect(lx, HEDGE, lx + 4, HFLOOR - 6, WOOD_F[3])
        s.vline(lx, HEDGE, HFLOOR - 6, WOOD_F[2])
    # top + its thick front edge
    wood_top(s, HX0, HT0, HX1, HT1, False)
    s.rect(HX0 + 3, HT1, HX1 - 3, HEDGE, WOOD_F[1])
    s.rect(HX0 + 1, HT1, HX0 + 3, HEDGE - 1, WOOD_F[1])               # rounded corners follow down
    s.rect(HX1 - 3, HT1, HX1 - 1, HEDGE - 1, WOOD_F[2])
    s.hline(HX0 + 3, HX1 - 3, HT1, WOOD_F[0])
    s.hline(HX0 + 3, HX1 - 3, HEDGE - 1, WOOD_F[3])
    # slab legs at both ends
    for lx in (HX0 + 4, HX1 - 12):
        s.rect(lx, HEDGE, lx + 8, HFLOOR, WOOD_F[1])
        s.vline(lx, HEDGE, HFLOOR, WOOD_F[0])
        s.vline(lx + 7, HEDGE, HFLOOR, WOOD_F[2])
        s.vline(lx + 3, HEDGE + 2, HFLOOR - 2, WOOD_F[2])             # groove
        s.hline(lx - 1, lx + 9, HFLOOR - 1, WOOD_F[3])                # foot
    power_slot(s, (HX0 + HX1) // 2, (HT0 + HT1) // 2)
    s.cast(HX0, HT0 + (HFLOOR - HT1), HX1, HFLOOR, HFLOOR - HT1)
    return s.finish()


# ============================================================== vertical ===
VW, VH = 72, 208
VX0, VX1 = 4, 64           # 60 wide (the table's depth, unforeshortened)
VT0, VT1 = 6, 182          # 176 long: kept unforeshortened so side chairs get a full 32px each
VEDGE = 186
VFLOOR = 197
SEAT_YS = [30, 62, 94, 126, 158]


def draw_v():
    s = Sprite(VW, VH)
    wood_top(s, VX0, VT0, VX1, VT1, True)
    s.rect(VX0 + 3, VT1, VX1 - 3, VEDGE, WOOD_F[1])
    s.hline(VX0 + 3, VX1 - 3, VT1, WOOD_F[0])
    s.hline(VX0 + 3, VX1 - 3, VEDGE - 1, WOOD_F[3])
    # near slab leg seen face-on: a wide end panel
    lx0, lx1 = VX0 + 6, VX1 - 6
    s.rect(lx0, VEDGE, lx1, VFLOOR, WOOD_F[1])
    s.vline(lx0, VEDGE, VFLOOR, WOOD_F[0])
    s.vline(lx1 - 1, VEDGE, VFLOOR, WOOD_F[2])
    s.rect(lx0 + 4, VEDGE + 2, lx1 - 4, VFLOOR - 3, WOOD_F[2])        # recessed panel
    s.hline(lx0 + 4, lx1 - 4, VEDGE + 2, WOOD_F[3])
    s.hline(lx0 + 4, lx1 - 4, VFLOOR - 4, WOOD_F[1])
    s.hline(lx0 - 1, lx1 + 1, VFLOOR - 1, WOOD_F[3])
    power_slot(s, (VX0 + VX1) // 2, (VT0 + VT1) // 2, vertical=True)
    s.cast(VX0, VT0 + (VFLOOR - VT1), VX1, VFLOOR, VFLOOR - VT1)       # long footprint along the table
    return s.finish()


# ================================================================ seats ===
CHAIR_DY = 6   # chair sprites carry 6 px of headroom above the backrest (see chair.py DY)


def seats():
    """Chair top-left (relative to the table sprite) + chair sprite name, per seat.
    'layer': 'behind' = draw before the table, 'front' = draw after it."""
    h = []
    for i, cx in enumerate(SEAT_XS):
        h.append(dict(id=f"N{i + 1}", chair="chair_front", x=cx - 16, y=HT0 - 24 - 6, layer="behind"))
    for i, cx in enumerate(SEAT_XS):
        h.append(dict(id=f"S{i + 1}", chair="chair_back", x=cx - 16, y=HT1 + 3 - 6, layer="front"))
    h.append(dict(id="W", chair="chair_right", x=HX0 - 24, y=HT0 + 6 - 6, layer="behind"))
    h.append(dict(id="E", chair="chair_left", x=HX1 - 8, y=HT0 + 6 - 6, layer="behind"))
    v = []
    for i, cy in enumerate(SEAT_YS):
        v.append(dict(id=f"W{i + 1}", chair="chair_right", x=VX0 - 24, y=cy - 20 - 6, layer="behind"))
    for i, cy in enumerate(SEAT_YS):
        v.append(dict(id=f"E{i + 1}", chair="chair_left", x=VX1 - 8, y=cy - 20 - 6, layer="behind"))
    v.append(dict(id="N", chair="chair_front", x=(VX0 + VX1) // 2 - 16, y=VT0 - 24 - 6, layer="behind"))
    v.append(dict(id="S", chair="chair_back", x=(VX0 + VX1) // 2 - 16, y=VT1 + 3 - 6, layer="front"))
    return {"meeting_h": h, "meeting_v": v}


def compose(table, seat_list, pad=32):
    """Table + chairs into one canvas, honouring the layer order."""
    ch = {n: Image.open(CHAIRS / f"{n}.png") for n in ("chair_front", "chair_back", "chair_left", "chair_right")}
    out = Image.new("RGBA", (table.width + pad * 2, table.height + pad * 2), (0, 0, 0, 0))
    behind = sorted((q for q in seat_list if q["layer"] == "behind"), key=lambda q: q["y"])
    front = sorted((q for q in seat_list if q["layer"] == "front"), key=lambda q: q["y"])
    for q in behind:
        out.alpha_composite(ch[q["chair"]], (q["x"] + pad, q["y"] + pad))
    out.alpha_composite(table, (pad, pad))
    for q in front:
        out.alpha_composite(ch[q["chair"]], (q["x"] + pad, q["y"] + pad))
    return out


def side_by_side(imgs, gap=10):
    w = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    h = max(i.height for i in imgs)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for im in imgs:
        out.alpha_composite(im, (x, (h - im.height) // 2))
        x += im.width + gap
    return out


if __name__ == "__main__":
    th, tv = draw_h().image(), draw_v().image()
    th.save(OUT / "meeting_h.png")
    tv.save(OUT / "meeting_v.png")
    st = seats()
    (OUT / "seats.json").write_text(json.dumps(st, indent=2))
    preview(side_by_side([th, tv]), OUT / "meeting-preview.png", 5, grid=False)
    preview(side_by_side([compose(th, st["meeting_h"]), compose(tv, st["meeting_v"])]),
            OUT / "meeting-set-preview.png", 4, grid=False)
    print("ok")
