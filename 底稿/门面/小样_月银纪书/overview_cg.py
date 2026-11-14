#!/usr/bin/env python3
# 给人看的原画总览：照页面用的 data/cg.json 和 data/moon.json，一条主线一行（一幕、二幕、三幕、收束），行头写时代和主线名，图底下写幕和名字；
# 旅伴死的那一刻另拼一张。图用 assets/cg/ 里发布的那一份。要带 PIL 的 Python。
#   python overview_cg.py 输出目录 [前缀] [--skip m07]
# 出 前缀_1万兽上.jpg 这样的几张，一张六七行。
import io
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
COLS, W, H = 4, 480, 320
PAD, BAR, HEAD, TOP = 8, 34, 46, 64
BG, INK, DIM, GOLD = (14, 15, 20), (236, 229, 214), (150, 146, 138), (214, 180, 110)
F = lambda n, bold=False: ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc', n)
SEGS = [('万兽上', ['m01', 'm02', 'm03', 'm04', 'm05', 'm06', 'm07', 'm08']), ('万兽下', ['m09', 'm10', 'm11', 'm12', 'm13', 'm14', 'm15']),
        ('诸国期一', ['m16', 'm17']), ('诸国期二', ['m18', 'm19']), ('诸国期三', ['m20', 'm21']),
        ('萨尔维斯上', ['m22', 'm23', 'm24']), ('萨尔维斯下', ['m25', 'm26', 'm27'])]


def cell(sheet, d, x, y, src, text):
    im = Image.open(os.path.join(HERE, src)).convert('RGB').resize((W, H), Image.LANCZOS)
    sheet.paste(im, (x, y))
    d.text((x + 4, y + H + 3), text, font=F(21), fill=INK)


def save(sheet, out, name):
    dst = os.path.join(out, name)
    sheet.save(dst, quality=86)
    print(dst, sheet.size, '%.1fMB' % (os.path.getsize(dst) / 1e6))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    skip = set(sys.argv[sys.argv.index('--skip') + 1].split(',')) if '--skip' in sys.argv else set()
    out, pre = args[0], (args[1] if len(args) > 1 else '总览')
    args = [a for a in args if a not in skip]
    cg = json.load(open(os.path.join(HERE, 'data', 'cg.json'), encoding='utf-8'))
    moon = json.load(open(os.path.join(HERE, 'data', 'moon.json'), encoding='utf-8'))
    eras = {e['id']: e for e in moon['eras']}
    os.makedirs(out, exist_ok=True)
    width = PAD + (W + PAD) * COLS
    n = 0
    for seg, ids in SEGS:
        rows = []      # (行头, [(src, 字)])，一行至多 COLS 格
        for eid in ids:
            if eid in skip:
                continue
            e = eras[eid]
            for line in e['lines']:
                acts = cg.get(eid, {}).get('nodes', {}).get(line['name'], {})
                cells = []
                for act in ['一幕', '二幕', '三幕', '收束']:
                    v = acts.get(act)
                    for x in (v if isinstance(v, list) else [v] if v else []):
                        cells.append((x['src'], '%s　%s' % (act, x['name'])))
                head = '%s　%s　%s　｜　%s' % (e['label'], e['title'], e['years'], line['name'])
                for i in range(0, len(cells), COLS):
                    rows.append((head if i == 0 else head + '（续）', cells[i:i + COLS]))
        if not rows:
            continue
        n += 1
        sheet = Image.new('RGB', (width, TOP + (HEAD + H + BAR + PAD) * len(rows) + PAD), BG)
        d = ImageDraw.Draw(sheet)
        d.text((PAD + 4, 14), '月银纪的书　节点原画　%s' % seg, font=F(30, True), fill=GOLD)
        y = TOP
        for head, cells in rows:
            d.text((PAD + 4, y + 8), head, font=F(24, True), fill=GOLD)
            for i, (src, text) in enumerate(cells):
                cell(sheet, d, PAD + i * (W + PAD), y + HEAD, src, text)
            y += HEAD + H + BAR + PAD
        save(sheet, out, '%s_%d%s.jpg' % (pre, n, seg))
    # 旅伴死的那一刻
    dead = []
    for eid in sorted(cg):
        if eid in skip:
            continue
        for who, v in cg[eid].get('deaths', {}).items():
            dead.append((v['src'], '%s　%s　%s' % (eras[eid]['label'], who, v['name'])))
    if dead:
        n += 1
        rows = (len(dead) + COLS - 1) // COLS
        sheet = Image.new('RGB', (width, TOP + (H + BAR + PAD) * rows + PAD), BG)
        d = ImageDraw.Draw(sheet)
        d.text((PAD + 4, 14), '月银纪的书　旅伴死的那一刻　%d 幅' % len(dead), font=F(30, True), fill=GOLD)
        for i, (src, text) in enumerate(dead):
            cell(sheet, d, PAD + i % COLS * (W + PAD), TOP + i // COLS * (H + BAR + PAD), src, text)
        save(sheet, out, '%s_%d死的那一刻.jpg' % (pre, n))


if __name__ == '__main__':
    main()
