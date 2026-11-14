#!/usr/bin/env python3
# 给人看的总览三张：二十二张牌面，十一段长卷，二十一幅时代原画。图用 assets/ 里发布的那一份。要带 PIL 的 Python。
#   python overview_art.py 输出目录 [前缀]
import io
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BG, INK, GOLD = (14, 15, 20), (236, 229, 214), (214, 180, 110)
F = lambda n, bold=False: ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc', n)
PAD, BAR, TOP = 8, 34, 64


def grid(out, name, title, items, cols, w, h):
    """items: [(图, 底下的字)]"""
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new('RGB', (PAD + (w + PAD) * cols, TOP + (h + BAR + PAD) * rows + PAD), BG)
    d = ImageDraw.Draw(sheet)
    d.text((PAD + 4, 14), title, font=F(30, True), fill=GOLD)
    for i, (src, text) in enumerate(items):
        x, y = PAD + i % cols * (w + PAD), TOP + i // cols * (h + BAR + PAD)
        im = Image.open(os.path.join(HERE, src)).convert('RGBA').resize((w, h), Image.LANCZOS)      # 牌面是带透明的拱窗形，垫在底色上
        sheet.paste(im, (x, y), im)
        d.text((x + 4, y + h + 3), text, font=F(21), fill=INK)
    dst = os.path.join(out, name)
    sheet.save(dst, quality=86)
    print(dst, sheet.size, '%.1fMB' % (os.path.getsize(dst) / 1e6))


def main():
    out, pre = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else '总览')
    os.makedirs(out, exist_ok=True)
    data = json.load(open(os.path.join(HERE, 'data', 'strife.json'), encoding='utf-8'))
    cg = json.load(open(os.path.join(HERE, 'data', 'cg.json'), encoding='utf-8'))
    eras = data['eras']
    cards = [('assets/card/c%02d.webp' % (i + 1), '%s　%s' % (e['no'], e['title'])) for i, e in enumerate(eras)] + [('assets/card/c22.webp', 'XXII　没有年岁')]
    grid(out, pre + '_牌面_上.jpg', '纷争纪的书　二十二张牌面（一至十一）', cards[:11], 6, 400, 600)
    grid(out, pre + '_牌面_下.jpg', '纷争纪的书　二十二张牌面（十二至二十二），末一格是牌背', cards[11:] + [('assets/card/back.webp', '牌背')], 6, 400, 600)
    grid(out, pre + '_长卷.jpg', '纷争纪的书　路的长卷十一段', [('assets/road/r%02d.webp' % k, '第 %d 段' % k) for k in range(1, 12)], 3, 640, 427)
    era = [(cg[e['id']]['key']['src'], '%s　%s　%s' % (e['no'], e['title'], e['years'])) for e in eras if cg.get(e['id'], {}).get('key')]
    grid(out, pre + '_时代原画.jpg', '纷争纪的书　二十一幅时代原画', era, 3, 640, 427)


if __name__ == '__main__':
    main()
