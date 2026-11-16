#!/usr/bin/env python3
# 改前改后并排的对照图（11-16）。一行一幅：左边 <键>_a0.png（改前），右边 <键>.png（改后）。
#   <带 PIL 的 python> -X utf8 底稿/门面/小样_纷争纪书/scenes/查图/pair_sheet.py <输出.jpg> <键…> [--w 768] [--single]
#   --single：不并排，只排改后的（没有 _a0 的也行），一行三幅，给主会话最后扫一遍用。
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
IMG = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'out', '门面_原画_纷争纪')


def font(n):
    for f in ('C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simhei.ttf'):
        if os.path.exists(f):
            return ImageFont.truetype(f, n)
    return ImageFont.load_default()


def main():
    args = sys.argv[1:]
    w = 768
    if '--w' in args:
        k = args.index('--w')
        w = int(args[k + 1])
        args = args[:k] + args[k + 2:]
    single = '--single' in args
    args = [a for a in args if not a.startswith('--')]
    out, keys = args[0], args[1:]
    h = w * 2 // 3
    ft = font(22)
    if single:
        cols = 3
        rows = (len(keys) + cols - 1) // cols
        sheet = Image.new('RGB', (w * cols, h * rows), (20, 20, 24))
        d = ImageDraw.Draw(sheet)
        for i, k in enumerate(keys):
            p = os.path.join(IMG, k + '.png')
            if not os.path.exists(p):
                continue
            x, y = (i % cols) * w, (i // cols) * h
            sheet.paste(Image.open(p).convert('RGB').resize((w, h), Image.LANCZOS), (x, y))
            d.rectangle([x, y, x + 12 * len(k) + 14, y + 30], fill=(0, 0, 0))
            d.text((x + 6, y + 2), k, fill=(255, 220, 150), font=ft)
    else:
        sheet = Image.new('RGB', (w * 2, h * len(keys)), (20, 20, 24))
        d = ImageDraw.Draw(sheet)
        for i, k in enumerate(keys):
            for j, suf in enumerate(('_a0', '')):
                p = os.path.join(IMG, k + suf + '.png')
                if not os.path.exists(p):
                    continue
                sheet.paste(Image.open(p).convert('RGB').resize((w, h), Image.LANCZOS), (j * w, i * h))
            d.rectangle([0, i * h, 12 * len(k) + 80, i * h + 30], fill=(0, 0, 0))
            d.text((6, i * h + 2), k + ' 改前', fill=(255, 220, 150), font=ft)
            d.rectangle([w, i * h, w + 70, i * h + 30], fill=(0, 0, 0))
            d.text((w + 6, i * h + 2), '改后', fill=(160, 255, 170), font=ft)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    sheet.save(out, quality=88)
    print(out, sheet.size)


if __name__ == '__main__':
    main()
