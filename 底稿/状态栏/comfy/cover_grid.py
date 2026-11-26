#!/usr/bin/env python3
# 封面用的“长相表”（11-26）：几位要露脸的人各取艺术照的上半身，拼成一张 3×N 的格子图，当一张参考图喂给出图。
# 格子里不写名字，提示词里用“第几行第几格”对应。
#   python cover_grid.py 输出.png 键1 键2 …     键是 out/立绘_*/<键>/ 的文件夹名
import os
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DIRS = ['立绘_山铜纪', '立绘_前传', '立绘_v3', '立绘_纷争纪', '立绘_月银纪史诗', '立绘_诸国期', '立绘_萨尔维斯', '立绘_神明']
GREY = (126, 128, 136)
CELL = (512, 640)          # 每格：艺术照上部 512×640（头到胸）
COLS = 3
GAP = 24


def find(key):
    for d in DIRS:
        p = os.path.join(HERE, 'out', d, key, 'art.png')
        if os.path.exists(p):
            return p
    raise FileNotFoundError(key)


def cell(key):
    im = Image.open(find(key))
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, GREY + (255,))
    bg.alpha_composite(im)
    im = bg.convert('RGB')
    w = im.width
    h = round(w * CELL[1] / CELL[0])
    return im.crop((0, 0, w, h)).resize(CELL, Image.LANCZOS)


def grid(out, keys):
    rows = (len(keys) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * CELL[0] + (COLS + 1) * GAP, rows * CELL[1] + (rows + 1) * GAP), (30, 30, 34))
    for i, k in enumerate(keys):
        r, c = divmod(i, COLS)
        sheet.paste(cell(k), (GAP + c * (CELL[0] + GAP), GAP + r * (CELL[1] + GAP)))
    sheet.save(out)
    return out


if __name__ == '__main__':
    print(grid(sys.argv[1], sys.argv[2:]))
