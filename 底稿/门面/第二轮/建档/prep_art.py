#!/usr/bin/env python3
# 建档升级（门面第二轮，11-24）的图：原图（gen_art.py 出在 底稿/状态栏/comfy/out/门面_建档/）处理成外壳用的 webp。
#   python 底稿/门面/第二轮/建档/prep_art.py
# 写 小样_外壳/assets/bx/*.webp 和 小样_外壳/data/bx_art.json（有哪几张、手的牌在图上的位置）。
#   牌（魂、种族、誓心、星牌）照 2:3 裁正；身份牌框同样；前半生小画照 3:2；
#   命路纹章两张、位阶徽记一张是一格一枚的整张，照格子切开，平底抠成透明；
#   手：抠掉纯绿的占位（牌或骰子）、转半圈（手臂从上边伸下来）、暗部提亮，记下占位在图上的位置，页面照它把牌塞到指尖下。
import json
import os
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'out', '门面_建档')
SHELL = os.path.join(ROOT, '底稿', '门面', '小样_外壳')
AS = os.path.join(SHELL, 'assets', 'bx')
os.makedirs(AS, exist_ok=True)
have = []

PATHS = [['cuifeng', 'feixue', 'rongxin', 'hongliu', 'zhenli', 'beimin', 'duanzui', 'wuxing', 'jueying', 'guiren', 'jingxian', 'xinglie'],
         ['mosuo', 'yuanlei', 'siwu', 'zhenjian', 'jiguang', 'tianping', 'dinghuo', 'qianchui', 'kurong', 'tielv', 'jiegou', 'custom']]


def src(k):
    p = os.path.join(SRC, k + '.png')
    return p if os.path.exists(p) else None


def card(k, w=480, ratio=1.5, q=84):
    p = src(k)
    if not p:
        return
    im = Image.open(p).convert('RGB')
    W, H = im.size
    if ratio >= 1:          # 竖的 2:3
        tw = min(W, round(H / ratio)); th = round(tw * ratio)
    else:                   # 横的 3:2
        th = min(H, round(W * ratio)); tw = round(th / ratio)
    im = im.crop(((W - tw) // 2, (H - th) // 2, (W - tw) // 2 + tw, (H - th) // 2 + th)).resize((w, round(w * ratio)), Image.LANCZOS)
    im.save(os.path.join(AS, k + '.webp'), 'WEBP', quality=q, method=6)
    have.append(k)


def keyed(im):
    """平底抠成透明：拿四角的颜色当底，离底越远越不透明。"""
    a = np.array(im.convert('RGB')).astype(np.float32)
    h, w = a.shape[:2]
    c = np.concatenate([a[:8, :8].reshape(-1, 3), a[:8, -8:].reshape(-1, 3), a[-8:, :8].reshape(-1, 3), a[-8:, -8:].reshape(-1, 3)]).mean(0)
    d = np.sqrt(((a - c) ** 2).sum(-1))
    al = np.clip((d - 14) / 34, 0, 1) * 255
    out = np.dstack([a, al]).astype('uint8')
    return Image.fromarray(out, 'RGBA')


def sheet(k, cols, rows, names, size):
    p = src(k)
    if not p:
        return
    im = Image.open(p).convert('RGB')
    W, H = im.size
    cw, ch = W / cols, H / rows
    for i, n in enumerate(names):
        if not n:
            continue
        x, y = i % cols, i // cols
        cell = im.crop((round(x * cw), round(y * ch), round((x + 1) * cw), round((y + 1) * ch)))
        k2 = keyed(cell)
        al = np.array(k2)[..., 3]
        ys, xs = np.where(al > 40)
        if not len(xs):
            print('空格', k, i)
            continue
        l, t, r, b = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        cx, cy, s = (l + r) / 2, (t + b) / 2, max(r - l, b - t) * 1.04
        box = (round(cx - s / 2), round(cy - s / 2), round(cx + s / 2), round(cy + s / 2))
        k2.crop(box).resize((size, size), Image.LANCZOS).save(os.path.join(AS, n + '.webp'), 'WEBP', quality=88, method=6)
        have.append(n)


def hand(k):
    p = src(k)
    if not p:
        return None
    im = Image.open(p).convert('RGBA')
    a = np.array(im).astype(np.float32)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    spill = g - np.maximum(r, b)
    card = (spill > 90) & (al > 128)
    geo = None
    if card.sum() < 300:
        print(k, '没找到绿占位')
    else:
        ys, xs = np.where(card)
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
        if k == 'hand_dice':          # 两颗骰子：宽按一颗算，角度不算
            geo['ang'] = 0.0
            geo['w'] = geo['w'] / 2.2
    keep = np.clip(1 - (spill - 25) / 70, 0, 1)
    al = al * keep
    a[..., 1] = np.where(spill > 0, np.maximum(r, b), g)
    a[..., 3] = al
    rgb = a[..., :3] / 255
    a[..., :3] = np.clip(np.power(rgb, .8) * 255, 0, 255)
    a[a[..., 3] < 20] = 0
    out = Image.fromarray(a.astype('uint8'), 'RGBA').rotate(180)
    W, H = out.size
    if geo:
        geo['c'] = np.array([W - geo['c'][0], H - geo['c'][1]])
    arr = np.array(out)
    ys, xs = np.where(arr[..., 3] > 24)
    l, t, rr, bb = int(xs.min()), 0, int(xs.max()) + 1, int(ys.max()) + 1
    out = out.crop((l, t, rr, bb))
    if geo:
        geo['c'] = geo['c'] - np.array([l, t])
    s = 520 / out.width
    out = out.resize((520, round(out.height * s)), Image.LANCZOS)
    out.save(os.path.join(AS, k + '.webp'), 'WEBP', quality=88, method=6)
    w, h = out.size
    info = {'w': w, 'h': h}
    if geo:
        info.update({'c': [round(geo['c'][0] * s / w, 4), round(geo['c'][1] * s / h, 4)], 'cw': round(geo['w'] * s / w, 4), 'ch': round(geo['h'] * s / w, 4), 'ang': round(geo['ang'], 2)})
    have.append(k)
    print(k, info)
    return info


for k in ['soul_native', 'soul_reborn', 'soul_isekai']:
    card(k, 480)
for k in ['race_human', 'race_highelf', 'race_dwarf', 'race_demon', 'race_halfling', 'race_beastkin', 'race_halforc', 'race_dragonborn',
          'race_truedragon', 'race_tiefling', 'race_merfolk', 'race_custom']:
    card(k, 400)
for k in ['oath_lg', 'oath_ng', 'oath_cg', 'oath_ln', 'oath_tn', 'oath_cn', 'oath_le', 'oath_ne', 'oath_ce']:
    card(k, 400)
for k in ['star_normal', 'star_rare', 'star_epic', 'star_legend', 'star_unique', 'star_back']:
    card(k, 400)
for k in ['id_moon', 'id_strife', 'id_bronze', 'id_maze', 'id_now']:
    card(k, 540, q=86)
for k in ['life_bones', 'life_birth', 'life_home', 'life_child', 'life_youth', 'life_path', 'life_depart', 'life_end']:
    card(k, 720, ratio=2 / 3, q=82)
sheet('emb_a', 4, 3, ['path_' + n for n in PATHS[0]], 160)
sheet('emb_b', 4, 3, ['path_' + n for n in PATHS[1]], 160)
sheet('tier_sheet', 3, 2, ['tier_0', 'tier_1', 'tier_2', 'tier_3', 'tier_4', 'tier_5'], 200)

hands = {}
for k in ('hand_push', 'hand_flip', 'hand_tap', 'hand_dice'):
    i = hand(k)
    if i:
        hands[k] = i

# 身份牌框上龛和几行字的位置（占整张的比例）：照山铜纪那一张量的，别的框照 gen_art 的写法同一个排法，有偏的在 FRAME 里改
FRAME = {
    'bronze': {'nl': .205, 'nt': .135, 'nw': .59, 'nh': .43, 'rows': [.636, .736, .789, .841]},
}
out = {'about': 'prep_art.py 出的，别手改', 'have': sorted(set(have)), 'hands': hands, 'frame': FRAME}
json.dump(out, open(os.path.join(SHELL, 'data', 'bx_art.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('图', len(set(have)), '手', list(hands))
