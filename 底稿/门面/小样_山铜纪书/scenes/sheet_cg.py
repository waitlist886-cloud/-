#!/usr/bin/env python3
# 查图用的总览：把出好的原画拼成几张小图，一格底下写键和名字。要带 PIL 的 Python。
#   python sheet_cg.py 输出目录 p4 p5            这几页出好的
#   python sheet_cg.py 输出目录 p4_a1 p5_d_hakan  这几幅
#   COLS=3 W=640 python sheet_cg.py …              一行几格、一格多宽（默认 3、640）
import glob
import io
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
SRC = os.path.normpath(os.path.join(BOOK, '..', '..', '状态栏', 'comfy', 'out', '门面_原画_山铜纪'))
COLS, W = int(os.environ.get('COLS', '3')), int(os.environ.get('W', '640'))
PER = int(os.environ.get('ROWS', '4')) * COLS


def main():
    out, args = sys.argv[1], sys.argv[2:]
    names = {}
    for p in sorted(glob.glob(os.path.join(HERE, 'p?.json'))):
        d = json.load(open(p, encoding='utf-8'))
        for s in d.get('nodes', []) + d.get('deaths', []):
            if not s.get('same'):
                names[s['key']] = '%s %s %s' % (s.get('act') or '死·' + s.get('death', ''), s['name'], '+'.join(s['style']))
    keys = [k for k in sorted(names) if (k in args or k.split('_')[0] in args) and os.path.exists(os.path.join(SRC, k + '.png'))]
    if not keys:
        print('没有出好的')
        return
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
    H, BAR, PAD = round(W * 2 / 3), 30, 6
    os.makedirs(out, exist_ok=True)
    tag = '_'.join(args)[:40]
    for s in range(0, len(keys), PER):
        part = keys[s:s + PER]
        rows = (len(part) + COLS - 1) // COLS
        sheet = Image.new('RGB', (PAD + (W + PAD) * COLS, PAD + (H + BAR + PAD) * rows), (14, 15, 20))
        d = ImageDraw.Draw(sheet)
        for i, k in enumerate(part):
            im = Image.open(os.path.join(SRC, k + '.png')).convert('RGB').resize((W, H), Image.LANCZOS)
            x, y = PAD + i % COLS * (W + PAD), PAD + i // COLS * (H + BAR + PAD)
            sheet.paste(im, (x, y))
            d.text((x + 4, y + H + 2), k + '　' + names[k], font=font, fill=(236, 229, 214))
        dst = os.path.join(out, 'cg_%s_%d.jpg' % (tag, s // PER + 1))
        sheet.save(dst, quality=85)
        print(dst, sheet.size, len(part), '幅')


if __name__ == '__main__':
    main()
