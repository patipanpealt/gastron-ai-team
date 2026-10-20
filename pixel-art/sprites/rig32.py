"""Character kit v5 — POSE RIG for the 32x64 chibi: body from the front (S), back (N) and side (W; E = W mirrored).

The character is a small set of 3D parts (head, ears, torso, 2 arms, 2 legs). A pose places the limbs
in 3D; each view projects the parts onto the screen and renders them with exactly the same lit-volume
shading as the approved front body (character32_front.py), so S / N / W look like one character.

  3D axes: X right, Y down, Z toward the viewer in the front view; the character faces +Z.
  S : screen (X, Y + k*Z)        depth  Z       (k = slight top-down pitch, limbs only)
  N : screen (31 - X, Y - k*Z)   depth -Z
  W : screen (15.5 - Z, Y)       depth  X-15.5  (character faces screen-left, near side = +X)

Pose rest frame (idle, frame 0, view S) reproduces the approved front sprite pixel for pixel.
"""
import numpy as np
from PIL import Image

import character32_front as B
import hair32_front as HAIR
from kit import OL, hx

W, H, PX, PY = B.W, B.H, B.PX, B.PY
CX = 15.5
PITCH = 0.35
VIEWS = ("S", "N", "W")


def proj(view, X, Y, Z, pitch=True):
    """3D point -> (screen x, screen y, view depth). Pitch only nudges limbs (head/torso stay straight-on)."""
    k = PITCH if pitch else 0.0
    if view == "S":
        return X, Y + k * Z, Z
    if view == "N":
        return 31.0 - X, Y - k * Z, -Z
    return CX - Z, Y, X - CX


# ---- poses ----------------------------------------------------------------------------------------
LEG_X = {"L": 12.6, "R": 19.4}
ARM_X = {"L": 9.6, "R": 21.4}
HIP_Y, FOOT_Y, SHOULDER_Y = 55.0, 59.4, 48.0
HAND_REST = {"L": (7.0, 52.6), "R": (24.0, 52.6)}


def pose_for(anim, f, view):
    """Everything a frame needs: head / torso offsets, leg + arm polylines (3D points), mouth, draw-order flag."""
    p = {"anim": anim, "hy": 0, "ty": 0, "arm_front": False, "mouth": False, "legs": {}, "arms": {}, "overlap": False}
    sl = sr = 0.0       # leg swing (-1 back .. +1 forward)
    liftL = liftR = 0.0

    if anim == "idle":
        if f == 1:
            p["hy"] = p["ty"] = 1
    elif anim == "walk":
        s_l, s_r, ll, lr, dy = [(1, -1, 0, 0, 0), (0, 0, 0, 1.6, -1), (-1, 1, 0, 0, 0), (0, 0, 1.6, 0, -1)][f]
        amp = 3.4 if view == "W" else 5.2     # front / back: the stride shows as feet rising and falling
        sl, sr, liftL, liftR = amp * s_l, amp * s_r, ll, lr
        p["hy"] = p["ty"] = dy
    elif anim == "sit":
        p["hy"] = p["ty"] = 2
    elif anim == "talk":
        p["mouth"] = f == 1
    elif anim == "wave":
        p["mouth"] = True
        p["arm_front"] = True

    p["overlap"] = anim in ("sit", "wave") or (anim == "talk" and f == 1)
    ty = p["ty"]
    # legs ------------------------------------------------------------------------------------------
    zoff = {"L": 0.0, "R": 0.0}
    if view == "W":
        zoff = {"L": 0.9, "R": -0.9}   # side view: far leg a little ahead, near leg a little behind
    for side, swing, lift in (("L", sl, liftL), ("R", sr, liftR)):
        x = LEG_X[side]
        if anim == "sit":
            if view == "W":
                pts = [(x, 56.4, 0), (x, 57.2, 6.0), (x, 59.8, 6.6)]
            else:
                pts = [(x, 56.4, 0), (x, 57.6, 3.4), (x, 59.6, 4.4)]
        else:
            pts = [(x, HIP_Y + ty, 0), (x, FOOT_Y - lift, swing + zoff[side])]
        p["legs"][side] = pts
    # arms ------------------------------------------------------------------------------------------
    for side, swing_z in (("L", -sl * 0.8), ("R", -sr * 0.8)):
        sx_, sy_ = ARM_X[side], SHOULDER_Y + ty
        hx_, hy_ = HAND_REST[side]
        hz = swing_z - (1.8 if view == "W" else 0.0)   # side view: arms hang a little behind the torso's mid-plane
        if anim == "sit":
            sy_ = 50.0
            hx_, hy_, hz = (11.2 if side == "L" else 19.8), 54.0, 4.6
            if view == "W":
                hz = 5.4
        elif anim == "talk" and side == "R":
            if f == 1:
                hx_, hy_, hz = 24.2, 46.0, 3.8
            else:
                hy_ += 0
        elif anim == "wave" and side == "R":
            hx_, hy_ = (25.2, 41.6) if f == 0 else (27.0, 42.6)
            hz = 1.5 if view != "W" else (3.0 if f == 0 else 5.4)
        p["arms"][side] = [(sx_, sy_, -0.8 if (view == "W" and anim not in ("sit", "talk", "wave")) else 0), (hx_, hy_ + (ty if anim not in ("sit", "talk", "wave") else 0), hz)]
    return p


# ---- body parts per view ----------------------------------------------------------------------------
def limb(pts2d, r0, r1):
    """Straight capsule for 2 points; smooth bent limb (curve through the middle point) for 3."""
    if len(pts2d) == 2:
        (x0, y0), (x1, y1) = pts2d
        return B.capsule(x0, y0, x1, y1, r0, r1)
    a, m, b = (np.array(p, float) for p in pts2d)
    ctrl = 2 * m - (a + b) / 2
    st = HAIR.strand(tuple(a), tuple(ctrl), tuple(b), r0, r1)
    return st.inside, st.normal


def body_parts(view, pose):
    """[(group, (inside, normal))] in painter order (far first) for this view."""
    P = lambda pt, pitch=True: proj(view, *pt, pitch=pitch)[:2]  # noqa: E731
    hy, ty = pose["hy"], pose["ty"]
    lr_ = 2.5 if view == "W" else 2.9
    legs = {s: limb([P(p) for p in pose["legs"][s]], lr_, lr_) for s in "LR"}
    arms = {s: limb([P(p) for p in pose["arms"][s]], 2.5, 2.9) for s in "LR"}
    neck = B.capsule(15.5, 45.5 + ty, 15.5, 47.0 + ty, 2.8)
    if view == "W":
        torso = B.ellipsoid(CX, 51.2 + ty, 6.3, 6.6, depth=0.9)
        head = B.ellipsoid(CX, 33.0 + hy, 11.4, 11.8, depth=0.95, squash_bottom=0.18)
        ear_near = B.ellipsoid(CX + 0.8, 35.2 + hy, 2.3, 3.3)
        ears = [("ear", ear_near)]
    else:
        torso = B.ellipsoid(15.5, 51.2 + ty, 7.4, 6.6, depth=0.9)
        head = B.ellipsoid(*B.HEAD_C[:1], B.HEAD_C[1] + hy, *B.HEAD_R, depth=0.95, squash_bottom=0.18)
        ears = [("ear", B.ellipsoid(3.4, 35.2 + hy, 2.7, 3.3)), ("ear", B.ellipsoid(27.6, 35.2 + hy, 2.7, 3.3))]
    body = [("torso", neck), ("torso", torso)]
    if view == "W":
        order = [("leg", legs["L"]), ("arm", arms["L"])] + body + [("leg", legs["R"]), ("head", head)] + ears
        order += [("arm", arms["R"])]
    else:
        order = [("leg", legs["L"]), ("leg", legs["R"])] + body
        if pose["arm_front"]:
            order += ears + [("head", head), ("arm", arms["L"]), ("arm", arms["R"])]
        else:
            order += [("arm", arms["L"]), ("arm", arms["R"])] + ears + [("head", head)]
    return order


def build_body(parts, ty=0, leg_outline=False, ear_shade=False):
    """Same shading pipeline as character32_front.build_body, for any part list in painter order.

    Returns (tone, group map, rank map): tone is -1 empty / 0..4 skin / 5 outline."""
    idx = np.full((H, W), -1, int)
    grp = np.full((H, W), "", object)
    rank = np.full((H, W), -1, int)
    light = np.zeros((H, W))
    for r, (g, (inside, normal)) in enumerate(parts):
        m = B.coverage(inside) >= 0.5
        v = B.lambert(normal(PX, PY))
        if g == "torso":
            v = v - 0.12
        light[m] = v[m]
        grp[m] = g
        rank[m] = r
        idx[m] = 0
    mask = idx >= 0
    light[(grp == "torso") & (PY < 49.5 + ty)] -= 0.35
    tone = B.band(light, [0.78, 0.5, 0.12, -0.3])
    tone = B.despeckle(tone, mask)
    tone[~mask] = -1
    out = B.edge(mask)
    pg = np.pad(grp, 1, constant_values="")
    pr = np.pad(rank, 1, constant_values=-1)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        ng = pg[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
        nr = pr[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
        sel = mask & (nr >= 0) & (nr < rank) & (ng != grp)
        if leg_outline:   # side view: the near leg overlaps the far leg
            sel |= mask & (nr >= 0) & (nr < rank) & (grp == "leg") & (ng == "leg")
        sel &= ~((grp == "arm") & (ng == "torso") & (PY <= 49.5 + ty))    # shoulders blend into the body
        sel &= ~((grp == "torso") & (ng == "arm"))
        out |= sel
    tone[out] = 5
    if ear_shade:
        e = (grp == "ear") & (tone >= 0) & (tone < 4)
        tone[e] = tone[e] + 1
    return tone, grp, rank


# ---- face layers ----------------------------------------------------------------------------------------
FACE_W = {  # side view (facing screen-left): near eye, blush, mouth
    "eye": [(8, 35), (9, 35), (8, 36), (9, 36), (8, 37), (9, 37), (8, 38), (9, 38)],
    "glint": [(8, 35)],
    "lid": [(9, 38)],
    "blush": [(11, 40), (12, 40), (13, 40)],
    "blush2": [(12, 41)],
    "mouth": [(10, 42)],
}
MOUTH_OPEN = {"S": [(15, 41), (16, 41), (15, 42), (16, 42)], "W": [(10, 42), (10, 43)]}


def face_layer(view, mouth_open=False, dy=0):
    if view == "N":
        return Image.new("RGBA", (W, H), (0, 0, 0, 0))
    spec = B.FACE if view == "S" else FACE_W
    col = {"eye": "#2b2230", "glint": "#ffffff", "lid": "#5a4458", "blush": "#f7a7b8",
           "blush2": "#f4b9c4", "mouth": "#9a4a56"}
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for k in ("eye", "glint", "lid", "blush", "blush2", "mouth"):
        if mouth_open and k == "mouth":
            continue
        for (x, y) in spec[k]:
            if 0 <= y + dy < H:
                im.putpixel((x, y + dy), hx(col[k]) + (255,))
    if mouth_open:
        for i, (x, y) in enumerate(MOUTH_OPEN[view]):
            top = i < len(MOUTH_OPEN[view]) // 2 if view == "S" else i == 0
            im.putpixel((x, y + dy), hx("#6a2434" if top else "#4a1624") + (255,))
    return im


def paint_body(tone, tone_pal):
    return B.paint(tone, tone_pal)


def render_body(view, pose, skin="medium"):
    """Returns dict: image (RGBA), tone, grp, rank, face (RGBA) for one frame."""
    parts = body_parts(view, pose)
    tone, grp, rank = build_body(parts, pose["ty"], leg_outline=(view == "W"), ear_shade=(view == "W"))
    return {"tone": tone, "grp": grp, "rank": rank,
            "img": B.paint(tone, B.TONES[skin]),
            "face": face_layer(view, pose["mouth"], pose["hy"])}


ANIMS = {  # name -> (ms per frame, loop, frames)
    "idle": (500, True, 2),
    "walk": (140, True, 4),
    "sit": (1000, False, 1),
    "talk": (220, True, 2),
    "wave": (200, True, 2),
}
