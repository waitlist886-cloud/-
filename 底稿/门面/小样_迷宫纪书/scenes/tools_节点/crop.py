#!/usr/bin/env python3
# 审图用：把一张图切成几块放大了看。python crop.py 键 [x0,y0,x1,y1 ...]（坐标是 0 到 1 的比例；不写就切成左、中、右三块）
# 写到 scratchpad/迷宫纪原画/crops/<键>_<n>.jpg
import os
import sys
from PIL import Image

OUT = 'E:/aldran_art/底稿/状态栏/comfy/out/门面_原画_迷宫纪_节点'
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
os.makedirs(DST, exist_ok=True)
key = sys.argv[1]
src = key if os.path.exists(key) else os.path.join(OUT, key + '.png')
im = Image.open(src).convert('RGB')
W, H = im.size
boxes = [tuple(float(v) for v in a.split(',')) for a in sys.argv[2:]] or [(0, 0, 0.4, 1), (0.3, 0, 0.7, 1), (0.6, 0, 1, 1)]
base = os.path.splitext(os.path.basename(src))[0]
for i, (x0, y0, x1, y1) in enumerate(boxes):
    c = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    s = min(3.0, 1500 / max(c.size))
    if s > 1.05:
        c = c.resize((int(c.size[0] * s), int(c.size[1] * s)), Image.LANCZOS)
    p = os.path.join(DST, '%s_%d.jpg' % (base, i + 1))
    c.save(p, quality=90)
    print(p, c.size, '原图', (W, H))
