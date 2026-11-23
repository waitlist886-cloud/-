#!/usr/bin/env python3
# 书架样张的图从 out/门面第二轮/书架/ 抠底、切开、转 webp，写进样张的 img/。用 ComfyUI 自带的 python 跑（要 scipy）：
#   <ComfyUI 的 python> -X utf8 cut_shelf.py [书脊那一张的名字] [封面那一张的名字]     缺省 spines、cover_guild
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '图标', 'tools'))
sys.stdout.reconfigure(encoding='utf-8')
SRC = os.path.join(ROOT, 'out', '门面第二轮', '书架')
IMG = os.path.normpath(os.path.join(HERE, '..', 'img'))

import numpy as np
from PIL import Image
from scipy import ndimage
from gpt_generic import key


def parts(im, minpx=4000):
    """透明图里一块一块的东西，照左右排好，回裁好的图。"""
    a = np.array(im)[..., 3] > 40
    lab, n = ndimage.label(ndimage.binary_dilation(a, iterations=4))
    sizes = ndimage.sum_labels(np.ones_like(lab), lab, index=range(1, n + 1))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        if sizes[i] < minpx:
            continue
        m = (lab[sl] == i + 1)
        c = np.array(im.crop((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)))
        c[..., 3] = np.where(m, c[..., 3], 0)
        out.append((sl[1].start, Image.fromarray(c, 'RGBA')))
    return [c for x, c in sorted(out, key=lambda t: t[0])]


def save(im, name, h=None, q=88):
    if h and im.height != h:
        im = im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)
    p = os.path.join(IMG, name + '.webp')
    im.save(p, 'WEBP', quality=q, method=6)
    print(name, im.size, os.path.getsize(p) // 1024, 'KB')


def main():
    sp = sys.argv[1] if len(sys.argv) > 1 else 'spines'
    cv = sys.argv[2] if len(sys.argv) > 2 else 'cover_guild'
    os.makedirs(IMG, exist_ok=True)
    # 主画
    m = Image.open(os.path.join(SRC, 'shelf_main.png')).convert('RGB')
    save(m.resize((2048, round(2048 * m.height / m.width)), Image.LANCZOS), 'shelf_main', q=84)
    # 一排书脊
    ps = parts(key(os.path.join(SRC, sp + '.png')))
    print(sp, '切出', len(ps), '块')
    for i, c in enumerate(ps[:9]):
        save(c, 'spine_%d' % i, h=720)
    # 封面和书脊
    pc = parts(key(os.path.join(SRC, cv + '.png')))
    print(cv, '切出', len(pc), '块')
    save(pc[0], 'guild_spine', h=900)
    save(pc[-1], 'guild_cover', h=1000)
    # 藏书票
    bp = key(os.path.join(SRC, 'bookplate.png'))
    bb = bp.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
    save(bp.crop(bb), 'bookplate', h=640)
    # 纸：取大框里头没有印线的那一块当底纹
    pp = Image.open(os.path.join(SRC, 'paper_slip.png')).convert('RGB')
    W, H = pp.size
    save(pp.crop((int(W * .07), int(H * .17), int(W * .93), int(H * .88))).resize((900, 1200), Image.LANCZOS), 'paper', q=82)
    save(pp.resize((680, round(680 * H / W)), Image.LANCZOS), 'paper_form', q=82)


main()
