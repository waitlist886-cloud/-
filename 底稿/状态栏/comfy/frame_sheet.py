#!/usr/bin/env python3
# 四张带透明的图拼一张说明图：棋盘格的地方是透明的，能看出靠窗那一边的轮廓是画里的东西。
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, 'out', '四方_11-03')


def checker(w, h, c=14):
    im = Image.new('RGBA', (w, h), (58, 62, 74, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, c):
        for x in range(0, w, c):
            if (x // c + y // c) % 2:
                d.rectangle((x, y, x + c - 1, y + c - 1), fill=(84, 90, 104, 255))
    return im


def on_checker(im, h):
    s = h / im.height
    r = im.resize((int(im.width * s), h), Image.LANCZOS)
    bg = checker(r.width, r.height)
    bg.alpha_composite(r)
    return bg


L = Image.open(os.path.join(ROOT, '_left.png')).convert('RGBA').crop((400, 0, 1400, 2000))
R = Image.open(os.path.join(ROOT, '_right.png')).convert('RGBA').crop((0, 0, 1000, 2000))
T = Image.open(os.path.join(ROOT, '_top.png')).convert('RGBA')
B = Image.open(os.path.join(ROOT, '_bottom.png')).convert('RGBA')
H = 1000
l, r = on_checker(L, H), on_checker(R, H)
mid_w = 900
t = on_checker(T, int(mid_w * T.height / T.width))
b = on_checker(B, int(mid_w * B.height / B.width))
gap = 16
sheet = Image.new('RGBA', (l.width + mid_w + r.width + gap * 4, H + gap * 2), (20, 22, 30, 255))
sheet.alpha_composite(l, (gap, gap))
sheet.alpha_composite(r, (gap * 3 + l.width + mid_w, gap))
sheet.alpha_composite(t, (gap * 2 + l.width, gap + 120))
sheet.alpha_composite(b, (gap * 2 + l.width, gap + H - 120 - b.height))
out = os.path.join(ROOT, '四方四张透明图.jpg')
sheet.convert('RGB').save(out, quality=88)
print(out, sheet.size)
