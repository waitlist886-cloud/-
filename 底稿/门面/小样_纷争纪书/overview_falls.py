#!/usr/bin/env python3
# “传奇之陨”原画的总览：照 cg_table.json 里 fall 那些行的先后，一页十二幅（三列四行），每幅底下写 第几张｜谁｜图名｜时候。
# 要带 PIL 的 Python（ComfyUI 那一个）。还没出图的那一格留空、写“还没出”。
#   python overview_falls.py <输出目录> [前缀]
import io
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', '..', '状态栏', 'comfy', 'out', '门面_原画_纷争纪'))
out_dir = sys.argv[1]
prefix = sys.argv[2] if len(sys.argv) > 2 else '传奇之陨'
table = json.load(open(os.path.join(HERE, 'cg_table.json'), encoding='utf-8'))
rows = [(k, t) for k, t in table.items() if t.get('fall')]
CW, CH, CAP, COLS, PER = 640, 427, 58, 3, 12
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
os.makedirs(out_dir, exist_ok=True)
for page in range(0, len(rows), PER):
    part = rows[page:page + PER]
    n_rows = (len(part) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * CW, n_rows * (CH + CAP)), (12, 13, 18))
    dr = ImageDraw.Draw(sheet)
    for i, (k, t) in enumerate(part):
        x, y = i % COLS * CW, i // COLS * (CH + CAP)
        p = os.path.join(SRC, k + '.png')
        if os.path.exists(p):
            sheet.paste(Image.open(p).convert('RGB').resize((CW, CH), Image.LANCZOS), (x, y))
        else:
            dr.text((x + 24, y + 24), '还没出', font=font, fill=(160, 120, 110))
        dr.text((x + 12, y + CH + 5), '第%d张　%s　「%s」' % (int(k[1:3]), t['fall'], t.get('name', '')), font=font, fill=(240, 228, 206))
        dr.text((x + 12, y + CH + 33), (t.get('label', '') + '　' if t.get('label') else '') + t.get('when', '') + '　' + t.get('where', ''), font=small, fill=(150, 146, 138))
    dst = os.path.join(out_dir, '%s_%d.jpg' % (prefix, page // PER + 1))
    sheet.save(dst, quality=88)
    print(dst, len(part), '幅')
