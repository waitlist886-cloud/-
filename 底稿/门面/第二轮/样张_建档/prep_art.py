#!/usr/bin/env python3
# 建档样张的素材和数据（门面第二轮，11-23）。
#   <ComfyUI 的 python> 底稿/门面/第二轮/样张_建档/prep_art.py
# 读 out/门面第二轮/建档/*.png（gen_art.py 出的），写 本目录 assets/*.webp；外壳 assets 里要用的几张照拷；
# 照 小样_外壳/data/build.json、stars.json 写 data.js（山铜纪 2 年雨城清查那一池，种族照 build.json，不自己编）。
# 手：抠掉纯绿的占位牌、转半圈（手臂从上边伸下来）、暗部提亮，记下牌在图上的位置（占整张的比例），页面照它把牌塞到指尖下。
import json
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = os.path.join(ROOT, 'out', '门面第二轮', '建档')
SHELL = os.path.join(ROOT, '底稿', '门面', '小样_外壳')
AS = os.path.join(HERE, 'assets')
os.makedirs(AS, exist_ok=True)
have = {}

for n in ('era_2', 'bb_2', 'hand9_open', 'hand9_take'):
    shutil.copy(os.path.join(SHELL, 'assets', n + '.webp'), os.path.join(AS, n + '.webp'))

CARDS = ['soul_native', 'soul_reborn', 'soul_isekai', 'race_human', 'race_highelf', 'race_dwarf', 'race_demon',
         'star_normal', 'star_rare', 'star_epic', 'star_legend', 'star_unique', 'star_back', 'id_bronze']
for k in CARDS:
    p = os.path.join(SRC, k + '.png')
    if not os.path.exists(p):
        print('还没有', k)
        continue
    im = Image.open(p).convert('RGB')
    w, h = im.size
    # 照 2:3 裁正（模型偶尔出 1024×1536 以外的尺寸）
    tw = min(w, round(h * 2 / 3))
    th = round(tw * 3 / 2)
    im = im.crop(((w - tw) // 2, (h - th) // 2, (w - tw) // 2 + tw, (h - th) // 2 + th)).resize((600, 900), Image.LANCZOS)
    im.save(os.path.join(AS, k + '.webp'), 'WEBP', quality=86, method=6)
    have[k] = 1


def hand(k):
    p = os.path.join(SRC, k + '.png')
    if not os.path.exists(p):
        print('还没有', k)
        return None
    im = Image.open(p).convert('RGBA')
    a = np.array(im).astype(np.float32)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    spill = g - np.maximum(r, b)
    card = (spill > 90) & (al > 128)
    geo = None
    if card.sum() < 500:
        print(k, '没找到绿牌')
        box = None
    else:
        ys, xs = np.where(card)
        box = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        # 牌的中心、宽、斜着几度：拿主轴摆正，宽那一根轴跟横轴的夹角（图上 y 朝下，跟 CSS rotate 同向）
        pts = np.stack([xs, ys], 1).astype(np.float64)
        c = pts.mean(0)
        _, _, vt = np.linalg.svd((pts - c)[::5], full_matrices=False)
        ax_w = vt[1] if abs(vt[0][1]) > abs(vt[0][0]) else vt[0]
        if ax_w[0] < 0:
            ax_w = -ax_w
        ax_l = np.array([-ax_w[1], ax_w[0]])
        pw, pl = (pts - c) @ ax_w, (pts - c) @ ax_l
        geo = {'c': c, 'w': float(np.percentile(pw, 99.5) - np.percentile(pw, .5)), 'h': float(np.percentile(pl, 99.5) - np.percentile(pl, .5)),
               'ang': float(np.degrees(np.arctan2(ax_w[1], ax_w[0])))}
    # 绿得越纯越透明，边上按比例；溢色压掉
    keep = np.clip(1 - (spill - 25) / 70, 0, 1)
    al = al * keep
    a[..., 1] = np.where(spill > 0, np.maximum(r, b), g)
    a[..., 3] = al
    # 暗部提亮一点（跟 hand9 一样，黑手套贴着暗底看得见）
    rgb = a[..., :3] / 255
    a[..., :3] = np.clip(np.power(rgb, .8) * 255, 0, 255)
    a[a[..., 3] < 20] = 0
    out = Image.fromarray(a.astype('uint8'), 'RGBA').rotate(180)
    W, H = out.size
    if box:
        box = [W - box[2], H - box[3], W - box[0], H - box[1]]
        geo['c'] = np.array([W - geo['c'][0], H - geo['c'][1]])
    arr = np.array(out)
    ys, xs = np.where(arr[..., 3] > 24)
    l, t, rr, bb = int(xs.min()), 0, int(xs.max()) + 1, int(ys.max()) + 1   # 手臂从上边伸下来：上边不裁
    if box:
        l, rr, bb = min(l, box[0]), max(rr, box[2]), max(bb, box[3])
    out = out.crop((l, t, rr, bb))
    if box:
        box = [box[0] - l, box[1] - t, box[2] - l, box[3] - t]
        geo['c'] = geo['c'] - np.array([l, t])
    s = 520 / out.width
    out = out.resize((520, round(out.height * s)), Image.LANCZOS)
    out.save(os.path.join(AS, k + '.webp'), 'WEBP', quality=88, method=6)
    w, h = out.size
    info = {'w': w, 'h': h}
    if geo:
        info.update({'c': [round(geo['c'][0] * s / w, 4), round(geo['c'][1] * s / h, 4)], 'cw': round(geo['w'] * s / w, 4), 'ch': round(geo['h'] * s / w, 4), 'ang': round(geo['ang'], 2)})
    print(k, info)
    return info


hands = {}
for k in ('hand_push', 'hand_flip'):
    i = hand(k)
    if i:
        hands[k] = i
# 没出成就拿牌桌那只张开的手顶上（hand9_open 已经是手臂从上边伸下来的）
if 'hand_push' not in hands:
    im = Image.open(os.path.join(AS, 'hand9_open.webp'))
    hands['hand_push'] = {'w': im.width, 'h': im.height, 'c': [0.5, 0.93], 'cw': 0.8, 'ch': 1.2, 'ang': 0, 'src': 'hand9_open'}

# ---- 数据 ----
B = json.load(open(os.path.join(SHELL, 'data', 'build.json'), encoding='utf-8'))
S = json.load(open(os.path.join(SHELL, 'data', 'stars.json'), encoding='utf-8'))
E = B['eras']['bronze']
YEAR = 2


def clean(s):
    s = str(s or '')
    s = re.sub(r'（★）|★', '', s)
    s = re.sub(r'(\d)\s*[—–]\s*(\d)', r'\1到\2', s)
    s = re.sub(r'——|—|–', '，', s).replace('；', '，')
    s = re.sub(r'…+', '。', s).replace('！', '。')
    return s.strip('， ')


per = next(p for p in E['periods'] if p['from'] <= YEAR <= p['to'])
races = []
for key in per['races']:
    r = E['races'][key]
    subs = []
    for s in r.get('subs', []):
        if s.get('from') and s['from'] > YEAR:
            subs.append({'n': s['name'], 'note': clean(s.get('note')), 'off': '%d年才有' % s['from'], 'alt': clean(s.get('alt'))})
        else:
            subs.append({'n': s['name'], 'note': clean(s.get('note')), 'kin': [k['name'] for k in s.get('kin', [])]})
    races.append({'k': key, 'n': r['name'], 'note': clean(r.get('note')), 'arrive': clean(r.get('arrive')),
                  'pn': clean((per.get('race_notes') or {}).get(key)), 'subs': subs})

pool = []
for s in S['stars']:
    e = (s.get('eras') or {}).get('bronze')
    if e is None:
        continue
    if (e.get('from') is not None and YEAR < e['from']) or (e.get('to') is not None and YEAR > e['to']):
        continue
    pool.append({'id': str(s['id']), 'n': e.get('name') or s['name'], 'type': e.get('type') or s['type'], 'tier': e.get('tier') or s['tier'],
                 'd': clean(e.get('desc') or s['desc']), 'note': clean(e.get('note'))})

data = {'era': E['name'], 'year': YEAR, 'period': per['name'], 'start': '雨城清查', 'sheet': E['sheet']['title'],
        'rates': S['rates'], 'races': races, 'stars': pool, 'hands': hands, 'art': sorted(have),
        'leave': B['ronova']['leave'][0]}
with open(os.path.join(HERE, 'data.js'), 'w', encoding='utf-8') as f:
    f.write('// prep_art.py 出的，别手改\nwindow.BD=' + json.dumps(data, ensure_ascii=False) + ';\n')
print('种族', len(races), '星', len(pool), '图', len(have))
