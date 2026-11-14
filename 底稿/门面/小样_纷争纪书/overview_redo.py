# 重画前后对照：左边旧图（<键>_a0.png 这一类），右边现行的图，一行一幅、一张三行。
#   python overview_redo.py <输出目录> <前缀> [旧图后缀=_a0] 键 键 …      （要带 PIL 的 Python）
# 图名和传奇的名字照 cg_table.json。
import io
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', '..', '状态栏', 'comfy', 'out', '门面_原画_纷争纪'))
out, pre, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
suf = '_a0'
if rest and rest[0].startswith('_'):
    suf, rest = rest[0], rest[1:]
T = json.load(open(os.path.join(HERE, 'cg_table.json'), encoding='utf-8'))
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 26)
small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
w, h, cap, gap, per = 960, 640, 44, 12, 3
os.makedirs(out, exist_ok=True)
for i in range(0, len(rest), per):
    part = rest[i:i + per]
    sheet = Image.new('RGB', (w * 2 + gap, (h + cap) * len(part)), (10, 11, 15))
    d = ImageDraw.Draw(sheet)
    for j, k in enumerate(part):
        y = j * (h + cap)
        r = T.get(k, {})
        d.text((8, y + 6), '%s　%s' % (r.get('fall') or r.get('death') or r.get('line') or k, r.get('name', '')), font=font, fill=(235, 225, 190))
        d.text((w - 70, y + 12), '改前', font=small, fill=(170, 170, 180))
        d.text((w * 2 + gap - 70, y + 12), '改后', font=small, fill=(170, 170, 180))
        for x, name in ((0, k + suf), (w + gap, k)):
            p = os.path.join(SRC, name + '.png')
            if os.path.exists(p):
                sheet.paste(Image.open(p).convert('RGB').resize((w, h), Image.LANCZOS), (x, y + cap))
            else:
                d.text((x + 20, y + cap + 20), '（没有图）' + name, font=small, fill=(255, 120, 120))
    p = os.path.join(out, '%s_%d.jpg' % (pre, i // per + 1))
    sheet.save(p, quality=86)
    print(p, sheet.size)
