#!/usr/bin/env python3
# 把品红平底（#FF00FF）的器物原画抠成透明底（11-21）。已经是透明底的（四角透明）照原样只裁边。
#   <ComfyUI 的 python> 底稿/图标/tools/key_relic.py [键…]   读 out/图标_原画/<键>.png，写 out/图标_原画/抠/<键>.png
import glob
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SRC = os.path.join(ROOT, 'out', '图标_原画')
DST = os.path.join(SRC, '抠')


def key(path):
    im = np.array(Image.open(path).convert('RGBA')).astype(float)
    r, g, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    corners = a[[0, 0, -1, -1], [0, -1, 0, -1]]
    if corners.max() > 200:          # 品红底：照“红蓝都高、绿低”的程度算透明度
        m = np.minimum(r, b) - g
        alpha = np.clip(1 - (m - 40) / 140, 0, 1)
        alpha[(r < 110) | (b < 110)] = 1
        # 半透明的边上去品红：红蓝里多出来的那一截照透明度压回去
        over = np.clip(np.minimum(r, b) - g, 0, None) * (1 - alpha)
        im[..., 0] = np.clip(r - over, 0, 255)
        im[..., 2] = np.clip(b - over, 0, 255)
        im[..., 3] = alpha * 255
    out = Image.fromarray(im.astype('uint8'), 'RGBA')
    bb = out.getchannel('A').point(lambda v: 255 if v > 16 else 0).getbbox()
    return out.crop(bb) if bb else out


if __name__ == '__main__':
    os.makedirs(DST, exist_ok=True)
    keys = sys.argv[1:] or [os.path.basename(p)[:-4] for p in glob.glob(os.path.join(SRC, '*.png'))]
    for k in keys:
        key(os.path.join(SRC, k + '.png')).save(os.path.join(DST, k + '.png'))
        print(k)
