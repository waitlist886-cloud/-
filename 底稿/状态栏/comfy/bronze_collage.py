#!/usr/bin/env python3
# 山铜纪右扇 right7 一层一层拼（11-04）。用户说索恩薇娅看着怪：叫 GPT 照立绘重画（right4、right5）身子就僵，拼回去收接缝（right6）又把腿拉长。
# 所以她不再过模型：t1 是头一稿的她一根线不动、只换发型和配色，t1_cut 抠出来，外套往下接到底。头一稿好看是因为下半身早早藏进人群，这里放大 SCALE 倍，手对到剑柄上，腰带落到旗子上头一点。
# 从下往上：plate6_fixed（干净的天和台阶，贴好打磨过的人）｜她（t1_cut）｜旗（flag_cut，照 right4 的大小缩回来，只要拳头以上）｜前排的人（还是 plate6_fixed，FRONT 里凡是不像台阶的颜色都算人，压回最上面）。
# 前排本来想叫 GPT 抠（front_cut），它抠的时候人挪了十几二十像素，跟底对不上，透明度一套就起雾，不用。台阶是一片均匀的浅粉，按颜色分比它准。
# 写 right7.png（放大过的，1573×2250）。要 PIL、numpy，用 ComfyUI 那个 venv 的 python。
import os
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, 'out', '山铜纪_11-04')
K = 1.5
HAND = (245, 250)       # 底上剑柄的位置（图的像素）
T1_ORIGIN = (217, 62)   # t1 裁的那一块的左上角在图上的位置（手已经对过）
T1_SIZE = (819, 770)    # 那一块原来多大
SCALE = float(os.environ.get('T_SCALE', '1.15'))     # 她放大多少，绕着手放大
FLAG_TOP = (628, 690)   # 旗杆顶在 flag_cut 里的位置
FLAG_K = 0.72           # flag_cut 比 right4 大了一圈，缩回来
FIST_Y = 925            # 旗杆只要拳头以上，底下是底上那一根
# 前排的人在哪（图的像素），这里头不像台阶的颜色都算人
FRONT = [(0, 640), (300, 640), (452, 760), (400, 815), (660, 795), (700, 850), (840, 795), (920, 795), (1049, 825), (1049, 1500), (0, 1500)]
# 皮肤和浅色的袍子跟台阶颜色太近，按颜色分不出来，这几块直接算人（图的像素）：薇丝塔的脸，艾瑟莉娅的袍子和手，卡尔恩的耳朵
SOLID = [[(403, 866), (462, 856), (482, 900), (472, 948), (430, 962), (398, 930)],
         [(170, 760), (290, 800), (302, 860), (345, 905), (345, 1000), (120, 1000)],
         [(262, 902), (328, 902), (328, 952), (262, 952)],
         [(930, 900), (985, 900), (985, 960), (930, 960)]]
# 披风往右下走，下沿藏到人群后头（图的像素）
HEM = [(180, 0), (1049, 0), (1049, 925), (712, 925), (690, 880), (640, 900), (560, 905), (400, 915), (250, 925), (180, 925)]


def load(name):
    return Image.open(os.path.join(ROOT, name + '.png')).convert('RGBA')


def erode_alpha(im, n=1):
    r, g, b, a = im.split()
    for _ in range(n):
        a = a.filter(ImageFilter.MinFilter(3))
    return Image.merge('RGBA', (r, g, b, a.filter(ImageFilter.GaussianBlur(0.6))))


def main():
    base = load('plate6_fixed')
    W, H = base.size
    # 她
    cut = erode_alpha(load('t1_cut'))
    tw, th = T1_SIZE
    k = K * SCALE
    fig = cut.resize((int(tw * k), int(th * k)), Image.LANCZOS)
    x = K * (HAND[0] + SCALE * (T1_ORIGIN[0] - HAND[0]))
    y = K * (HAND[1] + SCALE * (T1_ORIGIN[1] - HAND[1]))
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    layer.paste(fig, (int(x), int(y)))
    hem = Image.new('L', base.size, 0)
    ImageDraw.Draw(hem).polygon([(p[0] * K, p[1] * K) for p in HEM], fill=255)
    a = np.minimum(np.asarray(layer.getchannel('A')), np.asarray(hem.filter(ImageFilter.GaussianBlur(3))))
    layer.putalpha(Image.fromarray(a))
    out = base.copy()
    out.alpha_composite(layer)
    # 旗
    flag = erode_alpha(load('flag_cut'))
    fw, fh = flag.size
    fk = FLAG_K * K * 1049 / fw
    fl = flag.resize((int(fw * fk), int(fh * fk)), Image.LANCZOS)
    fx = K * FLAG_TOP[0] - FLAG_TOP[0] * (1049 / fw) * FLAG_K * K
    fy = K * FLAG_TOP[1] - FLAG_TOP[1] * (1049 / fw) * FLAG_K * K
    fl_layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    fl_layer.paste(fl, (int(fx), int(fy)))
    a = np.asarray(fl_layer.getchannel('A')).copy()
    a[int(FIST_Y * K):, :] = 0
    fl_layer.putalpha(Image.fromarray(a))
    out.alpha_composite(fl_layer)
    # 前排的人压在最上面
    rgb = np.asarray(base.convert('RGB')).astype(np.float32)
    lum = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
    warm = rgb[..., 0] - rgb[..., 1]
    stair = ((lum > 196) & (warm >= 8)) | (lum >= 232)
    poly = Image.new('L', base.size, 0)
    ImageDraw.Draw(poly).polygon([(p[0] * K, p[1] * K) for p in FRONT], fill=255)
    fg = Image.fromarray(np.uint8(~stair) * 255).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    from scipy import ndimage
    lab, n = ndimage.label(np.asarray(fg) > 127)                   # 台阶上零星的小块不算人
    size = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    keep = np.isin(lab, np.nonzero(size >= 400)[0] + 1)
    fg = Image.fromarray(np.uint8(keep) * 255)
    d = ImageDraw.Draw(fg)
    for sp in SOLID:
        d.polygon([(p[0] * K, p[1] * K) for p in sp], fill=255)
    fg = fg.filter(ImageFilter.GaussianBlur(0.6))
    mask = np.minimum(np.asarray(fg), np.asarray(poly))
    r, g, b, _ = base.split()
    out.alpha_composite(Image.merge('RGBA', (r, g, b, Image.fromarray(mask))))
    Image.fromarray(mask).save(os.path.join(ROOT, 'ref', 'front_mask.png'))
    out.convert('RGB').save(os.path.join(ROOT, 'right7.png'))
    print('ok', out.size)


if __name__ == '__main__':
    main()
