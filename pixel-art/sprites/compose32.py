"""Character kit v5 — compose one animation frame from the layers (body, bottom, top, face, hair).

Draw order per cell:  hair back -> body -> bottom -> top -> face -> hair front
Hair is rendered once per (style, view) at head offset 0 and shifted by the frame's head bob (hy).
Where an arm is drawn in front of the head (waving), the hair is cut away under the arm so the hand
stays on top.
"""
import numpy as np
from PIL import Image

import hair32_front as H0
import hair32_rig as HR
import outfit32_rig as O
import rig32 as R

W, H = R.W, R.H
_hair_cache = {}


def hair_layers(style, view, skin_mask, color="black"):
    key = (style, view, color)
    if key not in _hair_cache:
        _hair_cache[key] = HR.render_style(style, view, skin_mask, H0.COLORS[color])
    return _hair_cache[key]


def shifted(im, dy):
    if dy == 0 or im is None:
        return im
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(im, (0, dy)) if dy > 0 else out.alpha_composite(im.crop((0, -dy, im.width, im.height)), (0, 0))
    return out


def cut_alpha(im, mask):
    a = np.array(im)
    a[mask] = 0
    return Image.fromarray(a)


def frame_layers(view, anim, f, hair, top, bottom, skin="medium", hair_color="black"):
    """All layers of one frame as a dict of RGBA images + the pose."""
    pose = R.pose_for(anim, f, view)
    body = R.render_body(view, pose, skin)
    rest = R.render_body(view, R.pose_for("idle", 0, view), skin)
    layers = {"pose": pose, "body": body["img"], "face": body["face"]}
    layers["bottom"] = O.render_garment("bottom", bottom, view, pose, body) if bottom else None
    layers["top"] = O.render_garment("top", top, view, pose, body) if top else None
    if hair:
        hf, hb = hair_layers(hair, view, rest["tone"] >= 0, hair_color)
        hy = pose["hy"]
        hf, hb = shifted(hf, hy), shifted(hb, hy)
        if pose["arm_front"]:
            grp, rank = body["grp"], body["rank"]
            head_rank = rank[grp == "head"].max()
            hf = cut_alpha(hf, (grp == "arm") & (rank > head_rank))
        layers["hair_front"], layers["hair_back"] = hf, hb
    return layers


def composite(layers):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for k in ("hair_back", "body", "bottom", "top", "face", "hair_front"):
        if layers.get(k) is not None:
            im.alpha_composite(layers[k])
    return im
