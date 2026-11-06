#!/usr/bin/env python3
# 精简总览（11-05）：一位只放常服和艺术照，一行六位，透明图铺灰底，一页拼成一两张，发到手机上看。
#   python overview_lite.py <纪> <页文件 json …> <输出前缀>
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SET, JS, PRE = sys.argv[1], sys.argv[2:-1], sys.argv[-1]
V = os.path.join(HERE, 'out', '立绘_' + SET)
F = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
BG = (60, 62, 74, 255)
H = 380
COLS = 6
ROWS = 7


def fit(im):
    im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, BG)
    bg.alpha_composite(im)
    return bg.convert('RGB').resize((round(im.width * H / im.height), H), Image.LANCZOS)


def tile(c):
    d = os.path.join(V, c['en'])
    parts = []
    p = os.path.join(d, 'cell_casual.png')
    if os.path.exists(p):
        im = Image.open(p)
        bb = im.getchannel('A').getbbox()
        parts.append(fit(im.crop((max(0, bb[0] - 10), max(0, bb[1] - 10), min(im.width, bb[2] + 10), im.height))))
    p = os.path.join(d, 'art.png')
    if os.path.exists(p):
        parts.append(fit(Image.open(p)))
    w = sum(t.width for t in parts) + 4 * max(0, len(parts) - 1) or 200
    t = Image.new('RGB', (w, H + 32), (20, 20, 26))
    x = 0
    for im in parts:
        t.paste(im, (x, 32))
        x += im.width + 4
    ImageDraw.Draw(t).text((4, 2), c['name'], font=F, fill=(255, 230, 160))
    return t


cast = []
for j in JS:
    cast += json.load(open(j, encoding='utf-8'))
tiles = [tile(c) for c in cast]
TW = max(t.width for t in tiles)
os.makedirs(os.path.dirname(os.path.abspath(PRE)), exist_ok=True)
per = COLS * ROWS
for n in range(0, len(tiles), per):
    part = tiles[n:n + per]
    rows = (len(part) + COLS - 1) // COLS
    s = Image.new('RGB', (COLS * (TW + 8), rows * (H + 40)), (20, 20, 26))
    for i, t in enumerate(part):
        s.paste(t, ((i % COLS) * (TW + 8), (i // COLS) * (H + 40)))
    if s.width > 3000:
        s = s.resize((3000, round(s.height * 3000 / s.width)), Image.LANCZOS)
    out = '%s_%d.jpg' % (PRE, n // per + 1)
    s.save(out, quality=84)
    print(out, s.size)
