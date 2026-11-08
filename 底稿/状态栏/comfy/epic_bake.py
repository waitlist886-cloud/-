#!/usr/bin/env python3
# 11-08：史诗战分阶段立绘和神明显像烘成 webp，好推到图床（gh_img_up.py 的 epic、godsx 两套）。
# 只烘提示词里有的键（out/史诗战/<份>/<键>.png、out/神明显像/<键>.png），备选目录不碰；原尺寸 1024×1536，q82，一张一百七十 KB 上下。
#   python epic_bake.py            → out/史诗战_art/（史诗战六份）、out/神明显像_art/（正神、魔神）
#   源图比烘好的新才重烘
import json
import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
PR = os.path.join(HERE, 'epic', 'prompts')
OUT = {'epic': os.path.join(HERE, 'out', '史诗战_art'), 'gods': os.path.join(HERE, 'out', '神明显像_art')}
done = skip = miss = 0
for part in ['moon', 'strife_god1', 'strife_god2', 'strife_other', 'bronze', 'maze', 'gods_zheng', 'gods_mo']:
    data = json.load(open(os.path.join(PR, part + '.json'), encoding='utf-8'))
    if part.startswith('gods_'):
        keys, src_dir, dst_dir = [g['key'] for g in data], os.path.join(HERE, 'out', '神明显像'), OUT['gods']
    else:
        keys, src_dir, dst_dir = [p['key'] for b in data for p in b['phases']], os.path.join(HERE, 'out', '史诗战', part), OUT['epic']
    os.makedirs(dst_dir, exist_ok=True)
    for k in keys:
        src, dst = os.path.join(src_dir, k + '.png'), os.path.join(dst_dir, k + '.webp')
        if not os.path.exists(src):
            miss += 1
            print('缺', part, k)
            continue
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            skip += 1
            continue
        Image.open(src).convert('RGB').save(dst, 'WEBP', quality=82, method=6)
        done += 1
print('烘了 %d 张，没变跳过 %d 张，缺 %d 张' % (done, skip, miss))
