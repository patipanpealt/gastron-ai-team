"""Sprite 11 — giant piglet plush (an original design: pink piglet sitting on the floor,
Gastron-red ribbon bow). Steep top-down camera: the round head top is the brightest, biggest
shape; the face sits on the lower front of the head; stubby feet poke out toward the viewer.

  plush_front.png / plush_back.png / plush_left.png / plush_right.png  48x52 each
  (direction = the way the face looks; about 1 m tall sitting, at desk scale)
Anchor by the bottom-centre. Outputs in ./plush/ + plush-preview.png (chair + desk for scale)
"""
from pathlib import Path

from PIL import Image

from kit import RED, Sprite, floor_bg

OUT = Path(__file__).parent / "plush"
OUT.mkdir(exist_ok=True)
PINK = ["#ffe1ea", "#f9bfd0", "#ee9db7", "#d27a98", "#a85776"]
DARK = "#3a2230"


def shaded_blob(s, cx, cy, rx, ry, ramp, light=(-0.45, -0.55)):
    """Soft round form lit from the upper-left: lighter toward the light, darker on the far side."""
    lx, ly = light
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            u, v = (x - cx) / rx, (y - cy) / ry
            d = u * u + v * v
            if d > 1:
                continue
            k = u * lx + v * ly                                    # +1 facing the light, -1 away
            rim = d > 0.82
            i = 1 if k > 0.35 else 2 if k > -0.25 else 3
            if rim and k < 0:
                i = 4 if k < -0.3 else 3
            if k > 0.62 and d < 0.5:
                i = 0
            s.px(x, y, ramp[i])


def draw_piglet():
    s = Sprite(48, 52)
    cx = 24
    # body (sitting, seen from above-front) + stubby arms
    shaded_blob(s, cx, 36, 13, 10, PINK)
    shaded_blob(s, cx - 13, 35, 3.5, 4.5, PINK)                   # arms
    shaded_blob(s, cx + 13, 35, 3.5, 4.5, PINK)
    s.px(cx - 15, 38, PINK[3])
    s.px(cx + 12, 38, PINK[3])
    s.vline(cx, 38, 45, PINK[3])                                   # tummy seam (stitched)
    for y in range(39, 45, 2):
        s.px(cx - 1, y, PINK[4])
    # feet poking toward us, soles darker
    for fx in (cx - 7, cx + 7):
        shaded_blob(s, fx, 45, 4.5, 3.6, PINK)
        s.disc(fx + 0.5, 46.5, 2.6, 1.6, PINK[3])                  # sole pad
        s.px(fx, 46, PINK[4])
    # ears behind the head first (they sit on top, pointing up-out, inner side darker)
    for side in (-1, 1):
        ex = cx + side * 10
        shaded_blob(s, ex, 7, 5, 5.5, PINK)
        s.disc(ex + side * 0.5, 7.5, 2.6, 3, PINK[3])              # inner ear
        s.disc(ex + side * 0.5, 8.5, 1.6, 2, PINK[4])
    # big round head: the lit top dominates
    shaded_blob(s, cx, 17, 15, 12, PINK)
    s.disc(cx - 6, 10, 4, 2.2, PINK[0])                            # soft highlight on the crown
    s.disc(cx - 7, 9.5, 2, 1, "#ffffff")
    # red ribbon bow at the neck
    s.disc(cx - 4, 28.5, 3.2, 2.2, RED[1])
    s.disc(cx + 4, 28.5, 3.2, 2.2, RED[1])
    s.disc(cx - 4.5, 28, 1.6, 1, RED[0])
    s.disc(cx + 3.5, 28, 1.6, 1, RED[0])
    s.rect(cx - 1, 27, cx + 2, 30, RED[2])                         # knot
    s.px(cx, 27, RED[0])
    s.vline(cx - 3, 30, 34, RED[2])                                 # ribbon tails
    s.vline(cx + 3, 30, 33, RED[2])
    # face on the lower front of the head
    for ex in (cx - 6, cx + 5):                                    # eyes with a glint
        s.rect(ex, 18, ex + 2, 21, DARK)
        s.px(ex, 18, "#ffffff")
    s.disc(cx - 0.5, 23, 4.5, 3.2, PINK[1])                        # snout
    s.disc(cx - 1.5, 22, 2.5, 1.5, PINK[0])
    s.hline(cx - 4, cx + 4, 25, PINK[3])                           # snout underside
    s.rect(cx - 2, 22, cx - 1, 24, PINK[4])                        # nostrils
    s.rect(cx + 1, 22, cx + 2, 24, PINK[4])
    s.disc(cx - 10, 22.5, 2, 1.2, "#f58fae")                       # blush
    s.disc(cx + 9, 22.5, 2, 1.2, "#f58fae")
    # plush tag on the side
    s.rect(cx + 11, 40, cx + 14, 44, "#f4f1ea")
    s.px(cx + 12, 41, RED[1])
    s.cast(cx - 15, 38, cx + 15, 50, 16)
    return s.finish()


def curl_tail(s, x, y, flip=1):
    """Little curly tail: a pink spiral of 1-px dots."""
    for dx, dy in ((0, 0), (1, -1), (2, 0), (2, 1), (1, 2), (0, 1), (-1, 0)):
        s.px(x + dx * flip, y + dy, PINK[3])
    s.px(x + flip, y, PINK[1])


# ================================================================= back ===
def draw_back():
    """Same sitting pose seen from behind: back of the head, ears, ribbon band, curly tail."""
    s = Sprite(48, 52)
    cx = 24
    for fx in (cx - 7, cx + 7):                                    # heels peeking out under the body
        shaded_blob(s, fx, 46, 4, 2.6, PINK)
    shaded_blob(s, cx, 36, 13, 10, PINK)
    shaded_blob(s, cx - 13, 35, 3.5, 4.5, PINK)
    shaded_blob(s, cx + 13, 35, 3.5, 4.5, PINK)
    s.vline(cx, 37, 45, PINK[3])                                   # back seam
    curl_tail(s, cx - 1, 41)
    shaded_blob(s, cx, 17, 15, 12, PINK)                           # back of the head
    s.disc(cx - 6, 10, 4, 2.2, PINK[0])
    s.disc(cx - 7, 9.5, 2, 1, "#ffffff")
    s.vline(cx, 9, 26, PINK[2])                                    # seam down the back of the head
    for side in (-1, 1):                                           # ears, back side (no inner pink)
        shaded_blob(s, cx + side * 10, 7, 5, 5.5, PINK)
        s.disc(cx + side * 10.5, 8, 2.4, 2.6, PINK[2])
    s.rect(cx - 9, 28, cx + 10, 30, RED[1])                        # ribbon band round the neck
    s.hline(cx - 9, cx + 10, 28, RED[0])
    s.hline(cx - 9, cx + 10, 29, RED[2])
    s.rect(cx - 15, 40, cx - 12, 44, "#f4f1ea")                    # tag (other side now)
    s.px(cx - 14, 41, RED[1])
    s.cast(cx - 15, 38, cx + 15, 50, 16)
    return s.finish()


# ================================================================= side ===
def draw_side(faces_east):
    """Profile: snout points sideways, one eye, near ear in front, feet stick out toward the face."""
    s = Sprite(48, 52)
    f = 1 if faces_east else -1
    cx = 24
    X = lambda x: cx + (x - cx) * f                                # noqa: E731  mirror about the centre
    shaded_blob(s, X(30), 45, 4.8, 3.2, PINK)                      # far foot
    shaded_blob(s, X(23), 37, 11, 10, PINK)                        # body (a bit deeper than wide)
    curl_tail(s, X(12), 38, -f)
    shaded_blob(s, X(32), 46, 4.8, 3.4, PINK)                      # near foot, sole toward the face
    s.disc(X(35.5), 46.5, 1.4, 2, PINK[3])
    shaded_blob(s, X(20), 7, 4.5, 5.5, PINK)                       # far ear (behind the head)
    shaded_blob(s, X(23), 17, 13, 12, PINK)                        # head
    s.disc(X(19), 10, 4, 2.2, PINK[0])
    s.disc(X(18), 9.5, 2, 1, "#ffffff")
    shaded_blob(s, X(37), 21, 4, 3.6, PINK)                        # snout poking sideways
    s.disc(X(39), 21, 1.6, 2.4, PINK[3])                           # snout disc
    s.px(X(39), 20, PINK[4])                                       # nostril
    s.px(X(39), 22, PINK[4])
    s.rect(min(X(31), X(33)), 17, max(X(31), X(33)), 20, DARK)    # eye
    s.px(min(X(31), X(33)), 17, "#ffffff")
    s.disc(X(31), 23, 2, 1.2, "#f58fae")                           # blush
    s.hline(min(X(32), X(35)), max(X(32), X(35)), 25, PINK[3])     # smile line
    shaded_blob(s, X(26), 6, 4.5, 5.5, PINK)                       # near ear
    s.disc(X(26.5), 7, 2.2, 3, PINK[3])
    shaded_blob(s, X(29), 35, 3.4, 4.5, PINK)                      # near arm
    s.disc(X(27), 28.5, 3, 2, RED[1])                              # bow, side-on
    s.disc(X(31), 28.5, 2.4, 1.8, RED[1])
    s.rect(min(X(28), X(30)), 27, max(X(28), X(30)), 30, RED[2])
    s.rect(min(X(14), X(17)), 28, max(X(14), X(17)), 30, RED[2])   # band going round the back
    s.cast(cx - 13, 38, cx + 14, 50, 16)
    return s.finish()


if __name__ == "__main__":
    views = {"front": draw_piglet(), "back": draw_back(), "left": draw_side(False), "right": draw_side(True)}
    for k, v in views.items():
        v.image().save(OUT / f"plush_{k}.png")
    old = OUT / "plush_piglet.png"
    if old.exists():
        old.unlink()                                               # superseded by plush_front.png
    imgs = [views[k].image() for k in ("front", "back", "left", "right")]
    root = Path(__file__).parent
    chair = Image.open(root / "chair" / "chair_front.png")
    items = imgs + [chair]
    gap = 8
    H = max(i.height for i in items) + 2 * gap
    W = sum(i.width for i in items) + gap * (len(items) + 1)
    scene = floor_bg(W, H)
    x = gap
    for im in items:
        scene.alpha_composite(im, (x, H - gap - im.height))
        x += im.width + gap
    scene.convert("RGB").resize((W * 6, H * 6), Image.NEAREST).save(OUT / "plush-preview.png")
    print("ok")
