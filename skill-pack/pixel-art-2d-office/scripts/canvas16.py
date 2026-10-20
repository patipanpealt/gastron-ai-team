"""Render the 32x64 "design space" onto the 16x32 canvas of the approved chibi body.

The approved hair / outfit designs live in a 32x64 coordinate system (character32_front, hair32_rig, ...).
To draw them natively at 16x32 we do not resample finished images. Instead this module re-points the
rasteriser: it replaces character32_front's pixel-centre and supersample grids with the DESIGN-space
coordinates of a 16x32 canvas, so every primitive (shell, lock, ellipsoid ...) is evaluated per 16x32 pixel
(4x4 supersampled coverage, per-pixel light, per-pixel banding and outline). Everything downstream (tone
ramps, outlines, despeckle, hair gloss ...) therefore works on the real 16x32 pixel grid.

Import this module FIRST (before character32_front / hair32_front / hair32_rig), in its own process.

Mapping (design -> canvas), measured on the approved 16x32 body (head x 0..15, rows 10..22):
  x: head width 25.2 design px  ->  16 px        (xc = 7.5 + (xd - 15.5) * KX)
  y: head 21.2 .. 44.8          ->  rows 10 .. 22 (slope KY1), below the chin 0.42 px per design px
"""
import numpy as np

import character32_front as B

W16, H16, SS = 16, 32, 4
KX = 16.0 / 25.2
Y_HEAD_TOP, Y_CHIN = 21.2, 44.8
C_HEAD_TOP, C_CHIN = 10.0, 22.0
KY1 = (C_CHIN - C_HEAD_TOP) / (Y_CHIN - Y_HEAD_TOP)
KY2 = 0.42


def to_design_x(xc):
    return 15.5 + (xc - 7.5) / KX


def to_design_y(yc):
    yc = np.asarray(yc, float)
    return np.where(yc < C_CHIN, Y_HEAD_TOP + (yc - C_HEAD_TOP) / KY1, Y_CHIN + (yc - C_CHIN) / KY2)


def to_canvas_x(xd):
    return 7.5 + (np.asarray(xd, float) - 15.5) * KX


def to_canvas_y(yd):
    yd = np.asarray(yd, float)
    return np.where(yd < Y_CHIN, C_HEAD_TOP + (yd - Y_HEAD_TOP) * KY1, C_CHIN + (yd - Y_CHIN) * KY2)


def install():
    """Point character32_front's grids at the 16x32 canvas (design-space coordinates)."""
    cy, cx = np.mgrid[0:H16, 0:W16] + 0.5
    B.W, B.H, B.SS = W16, H16, SS
    B.PX, B.PY = to_design_x(cx), to_design_y(cy)
    sy, sx = (np.mgrid[0:H16 * SS, 0:W16 * SS] + 0.5) / SS
    B.SX, B.SY = to_design_x(sx), to_design_y(sy)


install()
