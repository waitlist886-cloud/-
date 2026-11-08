#!/usr/bin/env python3
# 史诗战、神明显像的总图（11-07）：一个对手一行（几阶并排，标块名和阶名），一页八个对手；神明显像一页十二位。查图和发给用户看用。
#   python epic_sheet.py <份> [--only-new 分钟]     写 out/史诗战_总图/<份>_<页>.jpg；只拼已经出了的
import json
import os
import sys
import time

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
PR = os.path.join(HERE, 'epic', 'prompts')
OUT = os.path.join(HERE, 'out', '史诗战_总图')
FONT = next((f for f in (r'C:/Windows/Fonts/msyh.ttc', r'C:/Windows/Fonts/simhei.ttf') if os.path.exists(f)), None)
H = 420


def font(n):
    return ImageFont.truetype(FONT, n) if FONT else None


def path_of(part, key):
    return os.path.join(HERE, 'out', '神明显像' if part.startswith('gods_') else os.path.join('史诗战', part), key + '.png')


def row(items, title):
    ims = []
    for p, label in items:
        im = Image.open(p).convert('RGB')
        ims.append((im.resize((round(im.width * H / im.height), H), Image.LANCZOS), label))
    pad, top = 10, 64
    W = max(sum(i.width for i, _ in ims) + pad * (len(ims) + 1), 900)
    s = Image.new('RGB', (W, H + top + pad), (18, 18, 22))
    d = ImageDraw.Draw(s)
    d.text((pad, 4), title, fill=(240, 220, 160), font=font(24))
    x = pad
    for im, label in ims:
        s.paste(im, (x, top))
        d.text((x + 2, 36), label[:22], fill=(220, 215, 200), font=font(18))
        x += im.width + pad
    return s


def pages(rows, per):
    for i in range(0, len(rows), per):
        yield i // per + 1, rows[i:i + per]


def main(part, since=None):
    data = json.load(open(os.path.join(PR, part + '.json'), encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)
    fresh = lambda p: os.path.exists(p) and (since is None or os.path.getmtime(p) > time.time() - since * 60)
    rows = []
    if part.startswith('gods_'):
        items = [(path_of(part, g['key']), g['name']) for g in data if fresh(path_of(part, g['key']))]
        for i in range(0, len(items), 4):
            rows.append(row(items[i:i + 4], ''))
        per = 3
    else:
        for b in data:
            items = [(path_of(part, p['key']), '%s %s' % (p['key'].rsplit('_', 1)[1], p['name'])) for p in b['phases'] if fresh(path_of(part, p['key']))]
            if items:
                rows.append(row(items, b['block'][:40]))
        per = 8
    out = []
    for n, rs in pages(rows, per):
        W = max(r.width for r in rs)
        s = Image.new('RGB', (W, sum(r.height for r in rs)), (18, 18, 22))
        y = 0
        for r in rs:
            s.paste(r, (0, y))
            y += r.height
        p = os.path.join(OUT, '%s_%d.jpg' % (part, n))
        s.save(p, quality=82)
        out.append(p)
        print(p, s.size)
    if not out:
        print('还没有出了的图')
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    since = float(a[a.index('--only-new') + 1]) if '--only-new' in a else None
    main(a[0], since)
