#!/usr/bin/env python3
# 把 gpt_cast.py 出的图烘成卡里用的两张（11-05）：por_英文名.webp 四套衣着排成一行（常服、私服、战斗、正装，一格 2:3），face_英文名.webp 九格表情（3×3）。
#   python cast_bake.py [英文名…]   写 out/立绘_11-05/art/，要 PIL、scipy（ComfyUI 那个 venv 的 python）
# 立绘：去掉碎屑，按透明通道的外框等比放进格子，头顶对齐，几套衣着的头才不跳。
# 表情：九格之间是透明的，按透明通道切开；一格里按皮肤的颜色找脸，脸放在格子正中偏上，圆头像才裁得到脸。
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out', '立绘_11-05')
ART = os.path.join(OUT, 'art')
ORDER = ['casual', 'private', 'battle', 'formal']
CW, CH = 640, 960      # 一套衣着一格
FS = 256               # 一格表情
TOP = 0.012            # 头顶离格子上沿
FACE_K = {'reinhardt': 0.74}   # 一格表情裁多大，相对这一格的外框宽；留脸和一点头发。没写的 0.8


def clean(im):
    """去掉透明底上的碎屑：只留够大的连通块。"""
    im = im.convert('RGBA')
    a = np.array(im.getchannel('A'))
    lab, n = ndimage.label(a > 24)
    if n > 1:
        sizes = ndimage.sum(a > 24, lab, range(1, n + 1))
        keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= sizes.max() * 0.01])
        a = np.where(keep, a, 0)
        im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im


def por(k):
    sheet = Image.new('RGBA', (CW * len(ORDER), CH), (0, 0, 0, 0))
    for i, o in enumerate(ORDER):
        im = clean(Image.open(os.path.join(OUT, k, o + '.png')))
        box = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
        fig = im.crop(box)
        s = min(CH * (1 - TOP * 2) / fig.height, CW * 0.98 / fig.width)
        fig = fig.resize((round(fig.width * s), round(fig.height * s)), Image.LANCZOS)
        sheet.alpha_composite(fig, (i * CW + (CW - fig.width) // 2, round(CH * TOP)))
    p = os.path.join(ART, 'por_%s.webp' % k)
    sheet.save(p, 'WEBP', quality=84, method=6, alpha_quality=90)
    print(' ', os.path.basename(p), sheet.size, os.path.getsize(p) // 1024, 'KB')


def cells(a):
    """按透明的缝把一张表切成 3×3，回九个 (x0,y0,x1,y1)。行和列都找投影上最宽的两道缝。"""
    def cuts(prof, n=3):
        empty = prof < 3
        lab, m = ndimage.label(empty)
        gaps = []
        for j in range(1, m + 1):
            idx = np.where(lab == j)[0]
            if idx[0] == 0 or idx[-1] == len(prof) - 1:
                continue
            gaps.append((len(idx), (idx[0] + idx[-1]) // 2))
        gaps = sorted(sorted(gaps, reverse=True)[:n - 1], key=lambda g: g[1])
        pts = [0] + [g[1] for g in gaps] + [len(prof)]
        return pts
    ys = cuts((a > 24).sum(axis=1))
    out = []
    for r in range(3):
        band = a[ys[r]:ys[r + 1]]
        xs = cuts((band > 24).sum(axis=0))
        for c in range(3):
            out.append((xs[c], ys[r], xs[c + 1], ys[r + 1]))
    return out


def face(k):
    im = Image.open(os.path.join(OUT, k, 'faces.png')).convert('RGBA')
    arr = np.array(im)
    a = arr[..., 3]
    sheet = Image.new('RGBA', (FS * 3, FS * 3), (0, 0, 0, 0))
    centres = []
    for n, (x0, y0, x1, y1) in enumerate(cells(a)):
        ca = a[y0:y1, x0:x1]
        ys, xs = np.where(ca > 24)
        bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
        rgb = arr[y0:y1, x0:x1, :3].astype(int)
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        skin = (ca > 200) & (r > 205) & (r - b > 26) & (r - b < 85) & (g - b < 50)
        skin[int(by0 + (by1 - by0) * 0.66):, :] = False
        sy, sx = np.where(skin)
        fx, fy = (np.median(sx), np.median(sy)) if len(sx) > 200 else ((bx0 + bx1) / 2, by0 + (by1 - by0) * 0.42)
        centres.append((fx, fy))
        side = (bx1 - bx0) * FACE_K.get(k, 0.8)
        crop = im.crop((round(x0 + fx - side / 2), round(y0 + fy - side * 0.46), round(x0 + fx + side / 2), round(y0 + fy + side * 0.54)))
        sheet.alpha_composite(crop.resize((FS, FS), Image.LANCZOS), ((n % 3) * FS, (n // 3) * FS))
    p = os.path.join(ART, 'face_%s.webp' % k)
    sheet.save(p, 'WEBP', quality=84, method=6, alpha_quality=90)
    print(' ', os.path.basename(p), sheet.size, os.path.getsize(p) // 1024, 'KB')


if __name__ == '__main__':
    os.makedirs(ART, exist_ok=True)
    names = sys.argv[1:] or [d for d in os.listdir(OUT) if os.path.exists(os.path.join(OUT, d, 'casual.png'))]
    for k in names:
        print(k)
        por(k)
        face(k)
