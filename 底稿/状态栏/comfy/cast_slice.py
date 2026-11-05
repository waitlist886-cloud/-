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
