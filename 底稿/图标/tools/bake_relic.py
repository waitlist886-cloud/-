#!/usr/bin/env python3
# 抠好的器物原画烘成 webp（11-21）：原画长边 768（详情和图鉴用），图标 128 的方格（背包格子用，透明底居中）。
#   <ComfyUI 的 python> 底稿/图标/tools/bake_relic.py   读 out/图标_原画/抠/*.png，写 out/图标_原画/webp/art_<键>.webp、icon_<键>.webp
import glob
import os

from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SRC = os.path.join(ROOT, 'out', '图标_原画', '抠')
DST = os.path.join(ROOT, 'out', '图标_原画', 'webp')
os.makedirs(DST, exist_ok=True)
tot = 0
for p in sorted(glob.glob(os.path.join(SRC, 'r*.png'))):
    k = os.path.basename(p)[:-4]
    im = Image.open(p).convert('RGBA')
    a = im.copy()
    a.thumbnail((768, 768), Image.LANCZOS)
    a.save(os.path.join(DST, 'art_%s.webp' % k), 'WEBP', quality=86, method=6)
    ic = im.copy()
    ic.thumbnail((116, 116), Image.LANCZOS)
    cell = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    cell.alpha_composite(ic, ((128 - ic.width) // 2, (128 - ic.height) // 2))
    cell.save(os.path.join(DST, 'icon_%s.webp' % k), 'WEBP', quality=90, method=6)
    tot += 1
print('烘了 %d 件，%.1f MB' % (tot, sum(os.path.getsize(f) for f in glob.glob(os.path.join(DST, '*.webp'))) / 1e6))
