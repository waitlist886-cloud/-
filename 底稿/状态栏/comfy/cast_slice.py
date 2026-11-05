#!/usr/bin/env python3
# 切四套衣服的设定图（1536×1024）：不靠竖直的缝，按连通区域认人，零碎的小块归最近的人，一人一格 640×960，脚踩格子底。
# 没有碰在一起的话四个人就是四个最大的连通区域；碰上了 figures() 返回的块数不够，这张重出，别硬切。
#   python cast_slice.py 设定图.png 输出目录
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ni

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
CELL = (640, 960)


def clean(im):
    im = im.convert('RGBA')
    a = im.getchannel('A').point(lambda v: 0 if v < 72 else min(255, int((v - 72) * 255 / 138)))
    im.putalpha(a)
    return im


def figures(im, n=4):
    """回 n 张和原图同大的 RGBA，一人一张，从左到右；分不开回 None。"""
    arr = np.array(im)
    solid = arr[..., 3] > 40
    lab, cnt = ni.label(solid, structure=np.ones((3, 3)))
    sizes = ni.sum(solid, lab, range(1, cnt + 1))
    order = np.argsort(sizes)[::-1]
    big = [int(i) + 1 for i in order[:n]]
    if len(big) < n or sizes[order[n - 1]] < solid.sum() * 0.08:
        return None
    big.sort(key=lambda i: np.where(lab == i)[1].mean())
    # 每个像素归最近的那个人（小块、半透明的发梢都跟着走）
    dist = np.stack([ni.distance_transform_edt(lab != i) for i in big])
    owner = dist.argmin(0)
    out = []
    for k in range(n):
        a = arr.copy()
        a[..., 3] = np.where(owner == k, a[..., 3], 0)
        out.append(Image.fromarray(a, 'RGBA'))
    return out


def cell(fig):
    bb = fig.getchannel('A').getbbox()
    c = fig.crop(bb)
    s = min(CELL[1] / c.height, CELL[0] / c.width)
    r = c.resize((round(c.width * s), round(c.height * s)), Image.LANCZOS)
    o = Image.new('RGBA', CELL, (0, 0, 0, 0))
    o.alpha_composite(r, ((CELL[0] - r.width) // 2, CELL[1] - r.height))
    return o, c.size, s


def head_x(fig):
    """头的横向中心：只看人最上面八分之一的透明通道（披风、头发甩到一边也不影响）。"""
    bb = fig.getchannel('A').getbbox()
    a = fig.getchannel('A').crop((bb[0], bb[1], bb[2], bb[1] + (bb[3] - bb[1]) // 8))
    x0, _, x1, _ = a.getbbox()
    return bb[0] + (x0 + x1) / 2


def cells(figs):
    """差分用：四格同一个比例，脚踩格子底，头对准格子正中，来回切时人不跳。放不下才整体缩一点。"""
    boxes = [f.getchannel('A').getbbox() for f in figs]
    hx = [head_x(f) for f in figs]
    s = CELL[1] / max(b[3] - b[1] for b in boxes)
    for b, x in zip(boxes, hx):   # 头放正中以后左右最宽能占多少
        half = max(x - b[0], b[2] - x)
        s = min(s, (CELL[0] / 2) / half)
    out = []
    for f, b, x in zip(figs, boxes, hx):
        c = f.crop(b)
        r = c.resize((round(c.width * s), round(c.height * s)), Image.LANCZOS)
        o = Image.new('RGBA', CELL, (0, 0, 0, 0))
        o.alpha_composite(r, (max(0, min(CELL[0] - r.width, round(CELL[0] / 2 - (x - b[0]) * s))), CELL[1] - r.height))
        out.append(o)
    return out, s


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    figs = figures(clean(Image.open(src)))
    if figs is None:
        print('分不开', src)
        sys.exit(1)
    for name, f in zip(('casual', 'private', 'battle', 'formal'), figs):
        c, size, s = cell(f)
        c.save(os.path.join(out, name + '.png'))
        print(name, '人', size, '缩放 %.2f' % s)
