#!/usr/bin/env python3
# 抠图体检（11-06）：扫各纪的四格和表情图，半透明像素占比高的多半是背景没抠干净（灰云、白光晕、带场景）。
#   python scan_cells.py [阈值，默认 0.12] [纪 …]   纪写 v3、前传、山铜纪……，不写就全扫
import glob
import os
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
th = 0.12
if args and args[0].replace('.', '').isdigit():
    th = float(args.pop(0))
sets = args or ['v3', '前传', '山铜纪', '纷争纪', '萨尔维斯', '诸国期', '月银纪史诗']
rows = []
for s in sets:
    root = os.path.join(HERE, 'out', '立绘_' + s)
    for d in sorted(glob.glob(os.path.join(root, '*'))):
        if not os.path.isdir(d):
            continue
        for n in ('cell_casual', 'cell_private', 'cell_battle', 'cell_formal', 'faces'):
            p = os.path.join(d, n + '.png')
            if not os.path.exists(p):
                continue
            try:
                a = np.asarray(Image.open(p).convert('RGBA').getchannel('A'))
            except Exception as e:
                rows.append((9.0, s, os.path.basename(d), n, 'read error'))
                continue
            semi = ((a > 20) & (a < 235)).sum()
            solid = (a >= 235).sum()
            r = semi / max(1, solid)
            rows.append((r, s, os.path.basename(d), n, '%d %d' % (semi, solid)))
rows.sort(reverse=True)
print('张数', len(rows))
vals = np.array([r[0] for r in rows])
print('中位 %.3f  90%% %.3f  99%% %.3f' % (np.median(vals), np.percentile(vals, 90), np.percentile(vals, 99)))
for r in rows:
    if r[0] < th:
        break
    print('%.3f %s %s %s' % (r[0], r[1], r[2], r[3]))
