#!/usr/bin/env python3
# 把 gpt_icons.py 出的六张切开，拼成一张雪碧图 items.webp（12 列 6 行，一格 CELL 像素），再出面板正中那个人 doll.webp。写进 art_fu_ab/。
#   python make_icons.py    要 PIL、numpy、scipy，用 ComfyUI 那个 venv 的 python
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = os.path.join(HERE, 'out', '四方_11-03', 'icons')
ART = os.path.join(HERE, 'out', '四方_11-03', 'art_fu_ab')
COLS, ROWS, CELL = 4, 3, 104   # 样式里最大显示 70 像素；图写进样式时上限两百万字，够用就行


def cut(path):
    """一张切十二样：连通块照重心归到最近的格子，一格的块并起来取外框，缩进一个方格里居中。"""
    im = Image.open(path).convert('RGBA')
    px = np.array(im)
    # GPT 的透明底边上有一圈半透明的杂色和零星的小点：淡的压掉，小块整块去掉
    al = px[..., 3].astype(float)
    px[..., 3] = np.clip((al - 40) * 255 / 215, 0, 255).astype('uint8')
    a = px[..., 3] > 14
    W, H = im.size
    lab, n = ndimage.label(ndimage.binary_dilation(a, iterations=2))
    sizes = ndimage.sum_labels(np.ones_like(lab), lab, index=range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i, v in enumerate(sizes) if v >= 200])
    px[..., 3][~keep] = 0
    im = Image.fromarray(px, 'RGBA')
    boxes = [None] * (COLS * ROWS)
    for i, sl in enumerate(ndimage.find_objects(lab)):
        if (lab[sl] == i + 1).sum() < 200:   # 零星的小点不要
            continue
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        k = min(int(cy / (H / ROWS)), ROWS - 1) * COLS + min(int(cx / (W / COLS)), COLS - 1)
        b = boxes[k]
        boxes[k] = (x0, y0, x1, y1) if b is None else (min(b[0], x0), min(b[1], y0), max(b[2], x1), max(b[3], y1))
    out = []
    for k, b in enumerate(boxes):
        if b is None:
            raise RuntimeError('%s 第 %d 格是空的' % (path, k))
        crop = im.crop(b)
        s = (CELL - 8) / max(crop.size)
        c2 = crop.resize((max(1, round(crop.width * s)), max(1, round(crop.height * s))), Image.LANCZOS)
        cell = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
        cell.paste(c2, ((CELL - c2.width) // 2, (CELL - c2.height) // 2))
        out.append(cell)
    return out


def main():
    sheet = Image.new('RGBA', (CELL * 12, CELL * 6), (0, 0, 0, 0))
    for r, n in enumerate('abcdef'):
        for i, c in enumerate(cut(os.path.join(SRC, 'sheet_%s.png' % n))):
            sheet.paste(c, (i * CELL, r * CELL))
    p = os.path.join(ART, 'items.webp')
    sheet.save(p, quality=70, method=6, alpha_quality=80)
    print('items', sheet.size, os.path.getsize(p) // 1024, 'KB')
    d = Image.open(os.path.join(SRC, 'doll.png')).convert('RGBA')
    d = d.crop(d.getchannel('A').point(lambda v: 255 if v > 10 else 0).getbbox())
    d = d.resize((round(d.width * 640 / d.height), 640), Image.LANCZOS)
    p = os.path.join(ART, 'doll.webp')
    d.save(p, quality=84, method=6, alpha_quality=90)
    print('doll', d.size, os.path.getsize(p) // 1024, 'KB')


if __name__ == '__main__':
    main()
