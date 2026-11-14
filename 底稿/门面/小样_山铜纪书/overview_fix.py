# 只改一处的图，改前改后的局部对照：左边旧图（<键>_a0.png）裁一块，右边现行的图裁同一块，一行一处、一张四行。
#   python overview_fix.py <输出目录> <前缀> 键:x0,y0,x1,y1:说明 …      坐标照 1280 宽那一版的像素（要带 PIL 的 Python）
#   键后头可以写 @后缀 指定旧图（不写是 _a0），比如 p2_d3:420,0,1160,640:弓弦落在拉弦的手上
import io
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', '..', '状态栏', 'comfy', 'out', '门面_原画_山铜纪'))
out, pre, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
T = json.load(open(os.path.join(HERE, 'cg_table.json'), encoding='utf-8'))
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 26)
small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
CW, CH, cap, gap, per = 940, 600, 44, 12, 4
os.makedirs(out, exist_ok=True)


def cell(path, box):
    im = Image.open(path).convert('RGB')
    s = im.size[0] / 1280
    c = im.crop(tuple(round(v * s) for v in box))
    m = min(CW / c.size[0], CH / c.size[1])
    c = c.resize((round(c.size[0] * m), round(c.size[1] * m)), Image.LANCZOS)
    bg = Image.new('RGB', (CW, CH), (10, 11, 15))
    bg.paste(c, ((CW - c.size[0]) // 2, (CH - c.size[1]) // 2))
    return bg


rows = []
for a in rest:
    k, box, note = a.split(':', 2)
    k, suf = (k.split('@') + ['_a0'])[:2]
    rows.append((k, suf, [int(v) for v in box.split(',')], note))
for i in range(0, len(rows), per):
    part = rows[i:i + per]
    sheet = Image.new('RGB', (CW * 2 + gap, (CH + cap) * len(part)), (10, 11, 15))
    d = ImageDraw.Draw(sheet)
    for j, (k, suf, box, note) in enumerate(part):
        y = j * (CH + cap)
        r = T.get(k, {})
        who = r.get('fall') or r.get('death') or r.get('line') or k
        d.text((8, y + 6), '%s　%s　%s' % (who, r.get('name', ''), note), font=font, fill=(235, 225, 190))
        d.text((CW - 70, y + 12), '改前', font=small, fill=(170, 170, 180))
        d.text((CW * 2 + gap - 70, y + 12), '改后', font=small, fill=(170, 170, 180))
        sheet.paste(cell(os.path.join(SRC, k + suf + '.png'), box), (0, y + cap))
        sheet.paste(cell(os.path.join(SRC, k + '.png'), box), (CW + gap, y + cap))
    p = os.path.join(out, '%s_%d.jpg' % (pre, i // per + 1))
    sheet.save(p, quality=88)
    print(p, sheet.size)
