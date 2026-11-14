#!/usr/bin/env python3
# 查图那一轮改过的节点原画，改前改后并排拼成几张对照图，给用户挑哪几幅要原图。要带 PIL 的 Python。
#   python overview_all_fix.py <输出目录> [一张几行，默认 6]
# 改过的图：出图目录里有 <键>_a0.png 的节点原画和死的那一刻（p1_… 到 p6_…）。改前是 _a0，改后是现行的 <键>.png。
# 裁哪一块：scenes/查图/查N.md 里报到这一幅的框并起来，四周放宽一点；报告里没有的（主会话自己查出来的）用整幅。
import glob
import io
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', '..', '状态栏', 'comfy', 'out', '门面_原画_山铜纪'))
BOX = re.compile(r'(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)')
out = sys.argv[1]
per = int(sys.argv[2]) if len(sys.argv) > 2 else 6
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
CW, CH, CAP, GAP = 760, 470, 40, 10
os.makedirs(out, exist_ok=True)

# 名字：场面稿里的幕和图名
names = {}
for p in sorted(glob.glob(os.path.join(HERE, 'scenes', 'p?.json'))):
    d = json.load(open(p, encoding='utf-8'))
    for s in d.get('nodes', []) + d.get('deaths', []):
        names[s['key']] = (s.get('act') or '死·' + s.get('death', '')) + ' ' + s.get('name', '')

# 报告里的框和毛病
boxes, whats = {}, {}
for r in sorted(glob.glob(os.path.join(HERE, 'scenes', '查图', '查*.md'))):
    for line in open(r, encoding='utf-8'):
        parts = [x.strip() for x in line.strip().split('｜')]
        if len(parts) < 3 or parts[1] == '过':
            continue
        bs = [tuple(int(v) for v in m) for m in BOX.findall('｜'.join(parts[2:]))]
        if not bs:
            continue
        boxes.setdefault(parts[0], []).extend(bs)
        whats.setdefault(parts[0], []).append(parts[2] if parts[1] == '拿不准' else parts[1])

keys = sorted(os.path.basename(p)[:-7] for p in glob.glob(os.path.join(SRC, 'p[1-6]_*_a0.png')))
keys = [k for k in keys if os.path.exists(os.path.join(SRC, k + '.png'))]


def crop(path, box):
    im = Image.open(path).convert('RGB')
    s = im.size[0] / 1280
    c = im.crop(tuple(round(v * s) for v in box))
    m = min(CW / c.size[0], CH / c.size[1])
    c = c.resize((max(1, round(c.size[0] * m)), max(1, round(c.size[1] * m))), Image.LANCZOS)
    bg = Image.new('RGB', (CW, CH), (10, 11, 15))
    bg.paste(c, ((CW - c.size[0]) // 2, (CH - c.size[1]) // 2))
    return bg


rows = []
for k in keys:
    bs = boxes.get(k)
    if bs:
        x0 = min(b[0] for b in bs); y0 = min(b[1] for b in bs); x1 = max(b[2] for b in bs); y1 = max(b[3] for b in bs)
        pad = max(40, round(0.25 * max(x1 - x0, y1 - y0)))
        box = (max(0, x0 - pad), max(0, y0 - pad), min(1280, x1 + pad), min(853, y1 + pad))
    else:
        box = (0, 0, 1280, 853)
    what = '；'.join(dict.fromkeys(whats.get(k, ['主会话查出来的'])))
    rows.append((k, names.get(k, ''), what, box))

n = 0
for i in range(0, len(rows), per):
    part = rows[i:i + per]
    W = CW * 2 + GAP * 3
    H = len(part) * (CAP + CH + GAP) + GAP
    sheet = Image.new('RGB', (W, H), (6, 7, 10))
    d = ImageDraw.Draw(sheet)
    y = GAP
    for k, nm, what, box in part:
        d.text((GAP, y + 6), '%s　%s' % (k, nm), font=font, fill=(236, 220, 180))
        t = what if len(what) <= 52 else what[:51] + '…'
        d.text((GAP + 520, y + 9), t, font=small, fill=(190, 190, 200))
        sheet.paste(crop(os.path.join(SRC, k + '_a0.png'), box), (GAP, y + CAP))
        sheet.paste(crop(os.path.join(SRC, k + '.png'), box), (GAP * 2 + CW, y + CAP))
        d.text((GAP + 8, y + CAP + 6), '改前', font=small, fill=(255, 255, 255))
        d.text((GAP * 2 + CW + 8, y + CAP + 6), '改后', font=small, fill=(255, 255, 255))
        y += CAP + CH + GAP
    n += 1
    p = os.path.join(out, '截图_第一版_人体对照_%02d.jpg' % n)
    sheet.save(p, quality=86)
print('改过的', len(rows), '幅，拼成', n, '张，写在', out)
