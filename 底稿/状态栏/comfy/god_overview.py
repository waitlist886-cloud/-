#!/usr/bin/env python3
# 神的立绘总图（11-08）：行走人世一位一格放设定图（三套）和艺术照，神座放正装和艺术照；透明图铺灰底，一页十二位，发手机看。
#   python god_overview.py <输出目录>
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(HERE, 'out', '立绘_神明')
OUTD = sys.argv[1]
os.makedirs(OUTD, exist_ok=True)
F = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
H = 420


def flat(p):
    im = Image.open(p).convert('RGBA')
    bg = Image.new('RGBA', im.size, (92, 92, 98, 255))
    bg.alpha_composite(im)
    im = bg.convert('RGB')
    return im.resize((round(im.width * H / im.height), H), Image.LANCZOS)


for name, fn in (('行走人世', ['行走_上.json', '行走_下.json']), ('神座', ['神座.json'])):
    people = [c for f in fn for c in json.load(open(os.path.join(HERE, 'cast', '神明', f), encoding='utf-8'))]
    tiles = []
    for c in people:
        d = os.path.join(V, c['en'])
        parts = [flat(os.path.join(d, n)) for n in ('sheet.png', 'art.png') if os.path.exists(os.path.join(d, n))]
        if not parts:
            continue
        w = sum(p.width for p in parts) + 8 * (len(parts) - 1)
        t = Image.new('RGB', (w, H + 34), (24, 24, 30))
        ImageDraw.Draw(t).text((4, 4), (c.get('name') or c['en'])[:24], fill=(240, 220, 170), font=F)
        x = 0
        for p in parts:
            t.paste(p, (x, 34))
            x += p.width + 8
        tiles.append(t)
    per = 12 if name == '神座' else 8
    for n in range(0, len(tiles), per):
        page = tiles[n:n + per]
        cols = 4 if name == '神座' else 2
        rows = [page[i:i + cols] for i in range(0, len(page), cols)]
        W = max(sum(t.width for t in r) + 12 * (len(r) + 1) for r in rows)
        s = Image.new('RGB', (W, len(rows) * (H + 46) + 12), (14, 14, 20))
        y = 12
        for r in rows:
            x = 12
            for t in r:
                s.paste(t, (x, y))
                x += t.width + 12
            y += H + 46
        p = os.path.join(OUTD, '神_%s_%d.jpg' % (name, n // per + 1))
        s.save(p, quality=82)
        print(p, s.size)
