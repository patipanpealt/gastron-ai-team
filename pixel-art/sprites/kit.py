"""Shared sprite kit for the Gastron virtual office — 32px grid, top-down 3/4 view (not isometric).

Style contract (every sprite follows this):
  * camera looks down at ~3/4: objects show a lit TOP face and a darker FRONT face
  * light comes from the top-left; 1px dark outline (OL) around every silhouette
  * v2 (after ko.dll): dark outline only on the shade side; long sheared cast shadow to the right
  * 4-step colour ramps: [highlight, base, shade, deep]
"""
from pathlib import Path

import numpy as np
from PIL import Image

GRID = 32

# ------------------------------------------------------------- palette ----
OL = "#2b2230"
SHADOW = (40, 24, 30)
WOOD = ["#e2ad6c", "#c38646", "#a46a36", "#7a4a26"]          # desk top (lit plane, kept bright)
LIP = "#f6d8a4"                                              # cream highlight on the edge that faces the light
WOOD_F = ["#6e4226", "#58331c", "#432514", "#2c170b"]        # front faces: much darker than the top
METAL = ["#8a919e", "#6b7280", "#4f5562", "#363a44"]
PLASTIC = ["#4e5466", "#3d4252", "#2e323e", "#22252e"]       # monitor bezel, chair
FABRIC = ["#5a6072", "#474c5c", "#383c49", "#2a2d37"]        # chair cushion
SCREEN = ["#d7f1f6", "#9fd6e0", "#6ab4c8", "#3d7f98"]
KEY = ["#f2efe8", "#e2ddd2", "#c9c3b6", "#a8a193"]
RED = ["#ff4d5a", "#D70010", "#a8000c", "#78000a"]           # Gastron CI red
GREEN = ["#3fc47a", "#009143", "#006e33", "#004d24"]          # Gastron CI green
FLOOR = ["#d6bb90", "#ccb087", "#c3a67c", "#a98c64"]         # preview background only


def hx(c):
    return c if isinstance(c, tuple) else tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


class Sprite:
    """Transparent pixel canvas with helpers. Draw, then .finish() adds outline + shadow."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.uint8)
        self.casts = []                                           # floor footprints that throw shadow

    def cast(self, x0, y0, x1, y1, height):
        """Register a floor footprint (screen rect where the object meets the floor) and the
        object's height above it. finish() sweeps it toward the upper-right (light from the
        front-left) — so a long desk throws a long shadow along its whole depth."""
        self.casts.append((x0, y0, x1, y1, height))

    # ---- primitives
    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[int(y), int(x)] = list(hx(c)[:3]) + [255]

    def rect(self, x0, y0, x1, y1, c):
        """Filled rect, x1/y1 exclusive."""
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(self.w, x1), min(self.h, y1)
        if x1 > x0 and y1 > y0:
            self.a[y0:y1, x0:x1] = list(hx(c)[:3]) + [255]

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y + 1, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x + 1, y1, c)

    def rrect(self, x0, y0, x1, y1, c, r=1):
        """Rect with corners clipped by r pixels (pixel-art rounded corner)."""
        for y in range(y0, y1):
            inset = 0
            dy = min(y - y0, y1 - 1 - y)
            if dy < r:
                inset = r - dy
            self.rect(x0 + inset, y, x1 - inset, y + 1, c)

    def disc(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                    self.px(x, y, c)

    def paste(self, other, ox, oy):
        """Alpha-over another sprite's pixels (already finished or raw)."""
        src = other.a
        h, w = src.shape[:2]
        for y in range(h):
            for x in range(w):
                tx, ty = ox + x, oy + y
                if not (0 <= tx < self.w and 0 <= ty < self.h):
                    continue
                sa = src[y, x, 3] / 255
                if sa == 0:
                    continue
                da = self.a[ty, tx, 3] / 255
                oa = sa + da * (1 - sa)
                rgb = (src[y, x, :3] * sa + self.a[ty, tx, :3] * da * (1 - sa)) / max(oa, 1e-6)
                self.a[ty, tx] = list(rgb.astype(np.uint8)) + [int(oa * 255)]

    # ---- finishing
    def finish(self, outline=True, shadow=True, shear=0.6, max_shift=14, rim=0.16, full_outline=False):
        """v2 finishing pass (style study of ko.dll's desk):
        * SELECTIVE OUTLINE — dark OL only on the bottom / right edges (the shade side);
          the top / left edges facing the light get no dark line, just a lightened rim pixel.
        * LONG CAST SHADOW — the silhouette sheared to the right in proportion to its height
          above the floor line (light from the upper-left), flat semi-transparent colour.
          The canvas grows to the right by up to `max_shift` px to hold it; the object itself
          keeps its position, so anchor sprites by their top-left / object bottom as before.
        """
        m = self.a[..., 3] == 255
        if outline:
            up = np.zeros_like(m); up[1:, :] = m[:-1, :]          # inside pixel directly above
            dn = np.zeros_like(m); dn[:-1, :] = m[1:, :]          # inside pixel directly below
            lf = np.zeros_like(m); lf[:, 1:] = m[:, :-1]
            rt = np.zeros_like(m); rt[:, :-1] = m[:, 1:]
            ring = (up | dn | lf | rt) & ~m
            lit_side = ring & (dn | rt) & ~(up | lf)              # sits above / left of the shape
            if rim:                                               # brighten the shape's lit edge instead
                edge = m & (~np.roll(m, 1, 0) | ~np.roll(m, 1, 1))
                edge[0, :] |= m[0, :]
                edge[:, 0] |= m[:, 0]
                rgb = self.a[edge, :3].astype(float)
                self.a[edge, :3] = (rgb + (255 - rgb) * rim).astype(np.uint8)
            self.a[ring if full_outline else ring & ~lit_side] = list(hx(OL)) + [255]
            m = self.a[..., 3] == 255
        if shadow and self.casts:
            kx, ky = shear, shear * 0.75
            pad = int(max(h for *_, h in self.casts) * kx) + 1
            big = np.zeros((self.h, self.w + pad, 4), np.uint8)
            big[:, :self.w] = self.a
            sh = np.zeros(big.shape[:2], bool)
            for x0, y0, x1, y1, hgt in self.casts:
                for t in range(hgt + 1):                          # sweep the footprint up to the object's height
                    dx, dy = int(round(t * kx)), int(round(t * ky))
                    ya, yb = max(0, y0 - dy), max(0, y1 - dy)
                    sh[ya:yb, max(0, x0 + dx):x1 + dx] = True
            sh &= big[..., 3] == 0
            big[sh] = list(SHADOW) + [int(255 * 0.30)]
            self.a, self.w = big, self.w + pad
        elif shadow:
            rows = np.where(m.any(axis=1))[0]
            floor = rows.max() if len(rows) else self.h - 1
            pad = max_shift
            big = np.zeros((self.h, self.w + pad, 4), np.uint8)
            big[:, :self.w] = self.a
            mb = np.zeros((self.h, self.w + pad), bool)
            mb[:, :self.w] = m
            sh = np.zeros_like(mb)
            for y in range(self.h):
                k = int(round((floor - y) * shear))
                if k > max_shift:                                 # tall parts (monitor, bottle) would
                    continue                                      # throw shadow onto thin air: cut it off
                if k > 0:
                    sh[y, k:] = mb[y, :-k]
                elif k == 0:
                    sh[y] = mb[y]
            sh &= big[..., 3] == 0
            big[sh] = list(SHADOW) + [int(255 * 0.30)]
            self.a, self.w = big, self.w + pad
        return self

    def wall_shadow(self, dx=1, dy=2, alpha=0.32):
        """Short drop shadow for things hung on a wall (style target: no long cast shadows)."""
        m = self.a[..., 3] == 255
        sh = np.zeros_like(m)
        sh[dy:, dx:] = m[:-dy, :-dx]
        sh &= self.a[..., 3] == 0
        self.a[sh] = list(SHADOW) + [int(255 * alpha)]
        return self

    def image(self):
        return Image.fromarray(self.a, "RGBA")

    def save(self, path, preview_scale=8):
        path = Path(path)
        self.image().save(path)
        preview(self.image(), path.with_name(path.stem + "-preview.png"), preview_scale)


def floor_bg(w, h):
    """Wood-plank floor tile used only behind previews, so the sprite is judged in context."""
    bg = np.zeros((h, w, 4), np.uint8)
    for row, y in enumerate(range(0, h, 8)):
        x = -((row * 13) % 24)
        while x < w:
            ln = 24 + ((x * 7 + row * 11) % 3) * 8
            c = hx(FLOOR[(x + row) % 3])
            bg[y:y + 7, max(0, x):max(0, min(w, x + ln - 1))] = list(c) + [255]
            bg[y:y + 7, max(0, min(w, x + ln - 1)):max(0, min(w, x + ln))] = list(hx(FLOOR[3])) + [255]
            x += ln
        bg[min(h, y + 7):min(h, y + 8), :] = list(hx(FLOOR[3])) + [255]
    return Image.fromarray(bg, "RGBA")


def preview(img, out, scale=8, grid=True):
    """Sprite on floor + transparent checker side by side, scaled up, with a faint 32px grid."""
    w, h = img.size
    pad = 8
    sheet = Image.new("RGBA", (w * 2 + pad * 3, h + pad * 2), (38, 36, 48, 255))
    fl = floor_bg(w, h)
    fl.alpha_composite(img)
    sheet.paste(fl, (pad, pad))
    chk = Image.new("RGBA", (w, h))
    for y in range(h):
        for x in range(w):
            chk.putpixel((x, y), (205, 205, 210, 255) if (x // 4 + y // 4) % 2 else (230, 230, 235, 255))
    chk.alpha_composite(img)
    sheet.paste(chk, (w + pad * 2, pad))
    big = sheet.resize((sheet.width * scale, sheet.height * scale), Image.NEAREST)
    if grid:
        g = np.array(big).astype(float)
        line = lambda sl: g.__setitem__(sl, g[sl] * 0.7 + 255 * 0.3)
        for ox in (pad, w + pad * 2):
            for k in range(0, w + 1, GRID):
                X = (ox + k) * scale
                if X < g.shape[1]:
                    line((slice(pad * scale, (pad + h) * scale), X, slice(0, 3)))
            for k in range(0, h + 1, GRID):
                Y = (pad + k) * scale
                if Y < g.shape[0]:
                    line((Y, slice(ox * scale, (ox + w) * scale), slice(0, 3)))
        big = Image.fromarray(g.astype(np.uint8), "RGBA")
    big.convert("RGB").save(out)
