#!/usr/bin/env python3
# 片头样片的素材：把出好的图存成 webp，各配一张很小的「远近图」（给镜头挪的时候各层错开用），再把暖色的点（火）在哪报出来。
#   python prep_pv.py            （用带 PIL、numpy、scipy 的那个 Python：ComfyUI 的 venv）
# 第一歌六幅：底稿/状态栏/comfy/out/门面_片头_11-12/pv1_a…f.png（gpt_front.py 的 pv1_*）。
# 另外三处先拿四纪主画顶着（小样_牌桌/assets/era_1…3.webp），牌背用小牌背 back_0…3.webp。
# 远近图怎么来的：这套画是一层压一层的浅色剪影，没有真的景深。拿「越靠下越近」垫底，掺一点亮度（浅的剪影在天上、算远），
# 抹得很糊，只要一片一片地缓缓变。幅度很小，看着是纸层在轻轻错开。
import os
import shutil

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', '..', '状态栏', 'comfy', 'out', '门面_片头_11-12'))
TABLE = os.path.normpath(os.path.join(HERE, '..', '小样_牌桌', 'assets'))
OUT = os.path.join(HERE, 'assets')
os.makedirs(OUT, exist_ok=True)


def depth(im):
    a = np.asarray(im.convert('RGB').resize((192, 128), Image.LANCZOS)).astype(np.float32) / 255
    lum = a @ np.array([.299, .587, .114], np.float32)
    h, w = lum.shape
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None] * np.ones((1, w), np.float32)
    d = .62 * y + .38 * (1 - lum)            # 1 是近
    d = ndimage.gaussian_filter(d, 5)
    d = (d - d.min()) / max(1e-6, d.max() - d.min())
    return Image.fromarray((d * 255).astype(np.uint8), 'L').convert('RGB')


def warm_spots(im, name):
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (r > 190) & (r - b > 70) & (g > 90) & (r - g > 20)
    lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=3))
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(xs) < 40:
            continue
        out.append((len(xs), xs.mean() / im.width, ys.mean() / im.height, (xs.max() - xs.min()) / im.width))
    out.sort(reverse=True)
    print('  暖色的点', name, ' '.join('(%.3f,%.3f 宽%.3f 面积%d)' % (x, y, w, n) for n, x, y, w in out[:10]) or '没有')


def put(src, name):
    im = Image.open(src).convert('RGB')
    if im.size != (1536, 1024):
        im = im.resize((1536, 1024), Image.LANCZOS)
    im.save(os.path.join(OUT, name + '.webp'), quality=86, method=6)
    depth(im).save(os.path.join(OUT, name + '_d.webp'), quality=80, method=6)
    print(name, os.path.getsize(os.path.join(OUT, name + '.webp')) // 1024, 'KB')
    warm_spots(im, name)


for k in 'abcdef':
    put(os.path.join(SRC, 'pv1_%s.png' % k), 'pv1_' + k)
for i in (1, 2, 3):
    put(os.path.join(TABLE, 'era_%d.webp' % i), 'era_%d' % i)
for i in range(4):
    shutil.copy(os.path.join(TABLE, 'back_%d.webp' % i), os.path.join(OUT, 'back_%d.webp' % i))
print('好了', OUT)
