#!/usr/bin/env python3
# 一纪一页的立绘总览（11-05 铺开各纪）：一位一行，四套差分、艺术照、表情，透明图铺灰底。
#   python overview_set.py <纪> <页文件 json> <输出前缀>     比如 python overview_set.py 前传 cast/前传/q6.json out/总览/前传_q6
# 三位一张图，输出 <前缀>_1.jpg、_2.jpg ……
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SET, JS, PRE = sys.argv[1], sys.argv[2], sys.argv[3]
V = os.path.join(HERE, 'out', '立绘_' + SET)
F = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 26)
FS = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
BG = (60, 62, 74, 255)
H = int(os.environ.get('OV_H', '640'))   # OV_H 行高，OV_N 一张几位（发到手机上看用小一点的）
N = int(os.environ.get('OV_N', '3'))
LAB = (('cell_casual', '常服'), ('cell_private', '私服'), ('cell_battle', '战斗'), ('cell_formal', '正装'), ('art', '艺术照'), ('faces', '表情'))


def fit(im):
    im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, BG)
    bg.alpha_composite(im)
    return bg.convert('RGB').resize((round(im.width * H / im.height), H), Image.LANCZOS)


def row(c):
    tiles = []
    for f, lab in LAB:
        p = os.path.join(V, c['en'], f + '.png')
        if os.path.exists(p):
            im = Image.open(p)
            if f.startswith('cell'):
                bb = im.getchannel('A').getbbox()
                im = im.crop((max(0, bb[0] - 16), max(0, bb[1] - 16), min(im.width, bb[2] + 16), im.height))
            t = fit(im)
        else:
            t = Image.new('RGB', (260, H), (40, 40, 48))
        cell = Image.new('RGB', (t.width, H + 28), (20, 20, 26))
        cell.paste(t, (0, 28))
        ImageDraw.Draw(cell).text((6, 2), lab, font=FS, fill=(255, 240, 190))
        tiles.append(cell)
    r = Image.new('RGB', (sum(t.width for t in tiles) + 8 * len(tiles), H + 66), (20, 20, 26))
    ImageDraw.Draw(r).text((6, 4), c['name'] + '  ' + c['en'], font=F, fill=(255, 225, 150))
    x = 0
    for t in tiles:
        r.paste(t, (x, 38))
        x += t.width + 8
    return r


cast = json.load(open(JS, encoding='utf-8'))
os.makedirs(os.path.dirname(os.path.abspath(PRE)), exist_ok=True)
rows = [row(c) for c in cast]
for i in range(0, len(rows), N):
    part = rows[i:i + N]
    s = Image.new('RGB', (max(r.width for r in part), sum(r.height for r in part) + 10 * len(part)), (20, 20, 26))
    y = 0
    for r in part:
        s.paste(r, (0, y))
        y += r.height + 10
    if s.width > 3200:
        s = s.resize((3200, round(s.height * 3200 / s.width)), Image.LANCZOS)
    out = '%s_%d.jpg' % (PRE, i // N + 1)
    s.save(out, quality=86)
    print(out, s.size)
