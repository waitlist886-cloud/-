#!/usr/bin/env python3
# 此刻那一本用的图（11-24）。要 PIL。先跑 build_data.py（人像拼图的名单读 data/pa_keys.json）。
#   python prep_assets.py            都做
#   python prep_assets.py art        首屏、牌面、路上的画、大陆全图、票根、街灯（原图在 底稿/状态栏/comfy/out/门面_此刻/，样张那四张在 out/门面第二轮/此刻/）
#   python prep_assets.py por        图鉴的人像拼图（assets/pa/c、m、l.webp，一格 300×450，八列），档案的大像（assets/art/键.webp，600×900）
import io
import json
import os
import sys

from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
SRC = os.path.join(COMFY, 'out', '门面_此刻')
SAMPLE = os.path.join(ROOT, 'out', '门面第二轮', '此刻')
V3 = os.path.join(COMFY, 'out', '立绘_v3', 'art')
A = os.path.join(HERE, 'assets')


def fresh(dst, *srcs):
    return os.path.exists(dst) and all(os.path.getmtime(dst) >= os.path.getmtime(s) for s in srcs)


def save(im, dst, q=82):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, 'WEBP', quality=q, method=6)
    print('  ', os.path.relpath(dst, HERE), im.size, os.path.getsize(dst) // 1024, 'KB')


def art():
    jobs = [('card', SAMPLE, 'card', (800, 1200), 86), ('main', SAMPLE, 'main', (2048, 1365), 80), ('main_m', SAMPLE, 'main', (1100, 733), 80),
            ('r1', SAMPLE, 'r1', (1400, 933), 80), ('r2', SAMPLE, 'r2', (1400, 933), 80)]
    jobs += [(k, SRC, k, (1400, 933), 80) for k in ('r3', 'r4', 'r5', 'r6')]
    jobs += [('lamp', SRC, 'lamp', (360, 540), 84)]
    for name, d, k, size, q in jobs:
        src = os.path.join(d, k + '.png')
        dst = os.path.join(A, name + '.webp')
        if not os.path.exists(src):
            print('没有', src)
            continue
        if fresh(dst, src):
            continue
        save(Image.open(src).convert('RGB').resize(size, Image.LANCZOS), dst, q)
    # 票根：裁到票面，四角的深蓝底抠成透明（票面自己是象牙白，跟底色差得远）
    src = os.path.join(SRC, 'ticket.png')
    dst = os.path.join(A, 'ticket.webp')
    if os.path.exists(src) and not fresh(dst, src):
        import numpy as np
        im = Image.open(src).convert('RGB')
        a = np.asarray(im).astype(int)
        d = np.abs(a - np.array(im.getpixel((5, 5)))).sum(2)
        ys, xs = np.where(d > 60)
        alpha = np.clip((d - 40) * 255 // 70, 0, 255).astype('uint8')
        rgba = Image.fromarray(np.dstack([a.astype('uint8'), alpha]), 'RGBA').crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        save(rgba.resize((960, round(960 * rgba.height / rgba.width)), Image.LANCZOS), dst, 86)
    # 大陆全图：出图时上下各补了一条海凑成 3:2，这里照同样的比例裁回旧底图的框（3520×2240 → 2200×1400），地标的百分数照旧
    src = os.path.join(SRC, 'map.png')
    dst = os.path.join(A, 'map.webp')
    if os.path.exists(src) and not fresh(dst, src):
        im = Image.open(src).convert('RGB')
        w, h = im.size
        keep = h * (2240 / (3520 * 2 / 3))
        top = (h - keep) / 2
        im = im.crop((0, round(top), w, round(top + keep))).resize((2200, 1400), Image.LANCZOS)
        save(im, dst, 82)
        save(im.resize((1100, 700), Image.LANCZOS), os.path.join(A, 'map_s.webp'), 80)


PW, PH, PCOLS = 300, 450, 8


def por():
    keys = json.load(open(os.path.join(HERE, 'data', 'pa_keys.json'), encoding='utf-8'))['pa']
    allk = []
    for sk, ks in keys.items():
        cols = min(PCOLS, len(ks))
        rows = (len(ks) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * PW, rows * PH), (12, 18, 40))
        for i, k in enumerate(ks):
            src = os.path.join(V3, 'art_' + k + '.webp')
            sheet.paste(Image.open(src).convert('RGB').resize((PW, PH), Image.LANCZOS), (i % cols * PW, i // cols * PH))
            allk.append(k)
        save(sheet, os.path.join(A, 'pa', sk + '.webp'), 80)
    for k in allk + ['baltina']:
        src = os.path.join(V3, 'art_' + k + '.webp')
        dst = os.path.join(A, 'art', k + '.webp')
        if not fresh(dst, src):
            Image.open(src).convert('RGB').resize((600, 900), Image.LANCZOS).save(dst, 'WEBP', quality=82, method=6) if os.makedirs(os.path.dirname(dst), exist_ok=True) is None else None
    print('档案大像', len(set(allk + ['baltina'])), '张')


if __name__ == '__main__':
    what = sys.argv[1:] or ['art', 'por']
    if 'art' in what:
        art()
    if 'por' in what:
        por()
