#!/usr/bin/env python3
# 载入页的图：从出好的稿（gen_gate.py，会话临时目录里）挑定了的那一张，压成外壳要的 webp（小样_外壳/assets/gate/），
# 定稿的原图另存一份 png 在 载入页/图/（不进外壳，留着往后重压用），写 载入页/src/gate_img.json（门的宽高比和门轴、石头在精灵图上的框）。
#   python -I -X utf8 底稿/门面/载入页/tools/prep_gate_img.py
# 门：品红平底抠成透明，照 DOOR 里量的门扉那一块（拱顶、起拱线、门脚）切成三层：门框（门扉那一块挖空）、左扇、右扇，三张一样大，叠起来就是原图。
# 石头：品红平底抠透明，四列三行十二块，整张当精灵图，各块的框照透明度量。
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(GATE, '..', '..', '..'))
DRAFT = os.environ.get('GATE_OUT') or os.path.join(os.environ.get('TEMP', HERE), 'claude', '85a810c2c0993c77', '5db2a7b9-8873-4e56-8761-1fd2a1d38fa6', 'scratchpad', '载入页', '稿')
MASTER = os.path.join(GATE, '图')
DST = os.path.join(ROOT, '底稿', '门面', '小样_外壳', 'assets', 'gate')
PICK = json.load(open(os.path.join(GATE, 'src', 'pick.json'), encoding='utf-8'))   # 哪一稿定了：{"sky": "sky_v1", …, "door_box": {...}}


def key(im):
    a = np.array(im.convert('RGBA')).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = np.minimum(r, b) - g
    alpha = np.clip(1 - (m - 40) / 140, 0, 1)
    alpha[(r < 110) | (b < 110)] = 1
    over = np.clip(np.minimum(r, b) - g, 0, None) * (1 - alpha)
    a[..., 0] = np.clip(r - over, 0, 255)
    a[..., 2] = np.clip(b - over, 0, 255)
    a[..., 3] = alpha * 255
    return Image.fromarray(a.astype('uint8'), 'RGBA')


def webp(im, name, q, size=None):
    if size:
        im = im.resize(size, Image.LANCZOS)
    p = os.path.join(DST, name + '.webp')
    im.save(p, 'WEBP', quality=q, method=6)
    return os.path.getsize(p)


def main():
    os.makedirs(DST, exist_ok=True)
    os.makedirs(MASTER, exist_ok=True)
    src = lambda k: Image.open(os.path.join(DRAFT, PICK[k] + '.png'))
    sizes, meta = {}, {}
    for k in [k for k in ('sky', 'past_a', 'past_b', 'fut_a', 'fut_b', 'fog1', 'fog2', 'door', 'stones') if k in PICK]:
        src(k).save(os.path.join(MASTER, k + '.png'))
    for k, q in [x for x in (('sky', 66), ('past_a', 74), ('past_b', 68), ('fut_a', 74), ('fut_b', 68)) if x[0] in PICK]:
        sizes[k] = webp(src(k).convert('RGB'), k, q, (1536, 1024))
    for k in [k for k in ('fog1', 'fog2') if k in PICK]:
        sizes[k] = webp(src(k).convert('RGB'), k, 50, (1024, 683))
    # 门
    d = key(src('door'))
    bb = d.getchannel('A').point(lambda v: 255 if v > 16 else 0).getbbox()
    d = d.crop(bb)
    H = 1100
    d = d.resize((round(d.width * H / d.height), H), Image.LANCZOS)
    W = d.width
    box = PICK['door_box']     # 门扉那一块：在原稿（1024×1536）上量的像素，换算到裁过、缩过的这一张
    sx = lambda x: (x - bb[0]) * H / (bb[3] - bb[1])
    sy = lambda y: (y - bb[1]) * H / (bb[3] - bb[1])
    x0, x1, ya, ys, yb = sx(box['x0']), sx(box['x1']), sy(box['apex']), sy(box['spring']), sy(box['foot'])
    pts = [(x0, yb), (x0, ys)]
    cx = (x0 + x1) / 2
    for i in range(1, 25):      # 尖拱：两段二次曲线
        t = i / 24
        pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * x0 + t * t * cx, (1 - t) ** 2 * ys + 2 * (1 - t) * t * (ya + (ys - ya) * .18) + t * t * ya))
    for i in range(1, 25):
        t = i / 24
        pts.append(((1 - t) ** 2 * cx + 2 * (1 - t) * t * x1 + t * t * x1, (1 - t) ** 2 * ya + 2 * (1 - t) * t * (ya + (ys - ya) * .18) + t * t * ys))
    pts.append((x1, yb))
    mask = Image.new('L', d.size, 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    A = np.array(d.getchannel('A')).astype(float)
    M = np.array(mask).astype(float) / 255
    half = np.zeros_like(M)
    half[:, :int(round(cx))] = 1
    def part(alpha):
        o = d.copy()
        o.putalpha(Image.fromarray(np.clip(alpha, 0, 255).astype('uint8')))
        return o
    sizes['door_f'] = webp(part(A * (1 - M)), 'door_f', 70)
    sizes['door_l'] = webp(part(A * M * half), 'door_l', 70)
    sizes['door_r'] = webp(part(A * M * (1 - half)), 'door_r', 70)
    meta['doorAspect'] = round(W / H, 4)
    meta['hingeL'] = round(x0 / W, 4)
    meta['hingeR'] = round(x1 / W, 4)
    # 石头（第一版用的，第二版不用了）
    s = key(src('stones')) if 'stones' in PICK else None
    if s is None:
        rects = []
    else:
        s = s
        s = s.resize((1152, 768), Image.LANCZOS)
        a = np.array(s.getchannel('A'))
        rects = []
        for row in range(3):
            for col in range(4):
                cx0, cy0, cw, ch = col * 288, row * 256, 288, 256
                cell = a[cy0:cy0 + ch, cx0:cx0 + cw] > 40
                ys_, xs_ = np.nonzero(cell)
                rects.append([int(cx0 + xs_.min()), int(cy0 + ys_.min()), int(xs_.max() - xs_.min() + 1), int(ys_.max() - ys_.min() + 1)])
        sizes['stones'] = webp(s, 'stones', 72)
        meta['sheet'] = [1152, 768]
        meta['rects'] = rects
    # 第二版（11-26 夜）：路面纹理（竖着能接上：底下那一截跟顶上那一截叠化，裁掉底下那一截）、两侧掠过的十二幅景
    if PICK.get('road'):
        r = np.array(src('road').convert('RGB').resize((768, 1152), Image.LANCZOS)).astype(float)
        src('road').save(os.path.join(MASTER, 'road.png'))
        Hh = r.shape[0]; b = int(Hh * .18)
        w = (np.arange(b) / b)[:, None, None]
        top = r[:b] * w + r[Hh - b:] * (1 - w)
        tile = np.concatenate([top, r[b:Hh - b]], 0)
        sizes['road'] = webp(Image.fromarray(tile.clip(0, 255).astype('uint8')), 'road', 70)
        meta['roadAspect'] = round(tile.shape[0] / tile.shape[1], 4)
    os.makedirs(os.path.join(DST, 'sh'), exist_ok=True)
    os.makedirs(os.path.join(MASTER, 'sh'), exist_ok=True)
    for k in [k for k in PICK if k.startswith('sh_')]:
        im = src(k)
        im.save(os.path.join(MASTER, 'sh', k[3:] + '.png'))
        p = os.path.join(DST, 'sh', k[3:] + '.webp')
        im.convert('RGB').resize((1152, 768), Image.LANCZOS).save(p, 'WEBP', quality=68, method=6)
        sizes[k] = os.path.getsize(p)
    json.dump(meta, open(os.path.join(GATE, 'src', 'gate_img.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    tot = sum(sizes.values())
    for k, v in sizes.items():
        print('%-8s %6.1f KB' % (k, v / 1024))
    print('合计 %.2f MB' % (tot / 1048576))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
