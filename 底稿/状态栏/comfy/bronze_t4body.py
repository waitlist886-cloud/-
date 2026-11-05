#!/usr/bin/env python3
# 山铜纪右扇第八稿的底稿。用户指着 t4 的身子说“你就按这个躯体来”，所以身子就是 t4 的像素，这里只换衣服：
# 红的换成白和浅金，贴上第七稿（t8a1）的胳膊、剑、肩甲、护臂，披风裁成左半甩到左边，露出右边的腰胯和腰带，头缩一点，左脚往前。坐标都写在 1024×1536 的画面上。
#   python bronze_t4body.py 输出.png
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(HERE, 'out', '山铜纪_11-04') + os.sep


def build(path):
    t4 = Image.open(O + 't4.png').convert('RGBA')
    t8 = Image.open(O + 't8a1.png').convert('RGBA')
    SZ = t4.size


    def mask(poly, blur=1.2):
        m = Image.new('L', SZ, 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        return m.filter(ImageFilter.GaussianBlur(blur)) if blur else m


    def clear(im, poly):
        a = np.array(im)
        m = np.array(mask(poly, 0)) > 128
        a[m, 3] = 0
        return Image.fromarray(a, 'RGBA')


    def cut(im, poly, blur=1.2):
        o = im.copy()
        m = np.array(mask(poly, blur)).astype(np.float32) / 255
        a = np.array(o).astype(np.float32)
        a[..., 3] *= m
        return Image.fromarray(a.astype(np.uint8), 'RGBA')


    # 1 红的换掉：上面的小披肩换成白，下面的里子换成浅金
    a = np.array(t4).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 40) & (g / (r + 1) < .46) & (b / (r + 1) < .46) & (a[..., 3] > 20)
    lum = (.3 * r + .59 * g + .11 * b)
    yy = np.arange(SZ[1])[:, None]
    col = np.zeros_like(a[..., :3])
    top = np.array([244, 236, 222], dtype=np.float32)
    low = np.array([230, 196, 124], dtype=np.float32)
    k = np.clip(lum / 62, .55, 1.0)[..., None]
    col = np.where((yy < 860)[..., None], top, low) * k
    a[..., :3] = np.where(red[..., None], col, a[..., :3])
    base = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')

    # 2 下摆左边那几层、抬起的胳膊和剑拿掉
    TAILS = [(0, 760), (440, 760), (470, 835), (548, 860), (500, 960), (456, 1050), (420, 1160), (378, 1300), (340, 1420), (0, 1420)]
    ARM = [(0, 0), (560, 0), (578, 480), (572, 600), (560, 640), (520, 652), (0, 760)]
    SCARF = [(668, 636), (700, 652), (640, 712), (575, 775), (540, 815), (480, 845), (400, 835), (330, 812), (240, 830), (170, 800), (168, 770), (250, 762), (330, 770), (400, 795), (470, 790), (520, 770), (575, 700)]
    scarf = cut(base, SCARF)
    base = clear(base, TAILS)
    base = clear(base, ARM)

    # 3 披风的左半：第七稿那一片顺着右边这条斜边裁下来，贴在躯体后面
    EDGE = [(612, 700), (640, 760), (624, 850), (600, 960), (572, 1060), (550, 1150), (578, 1266)]
    CAPE = [(0, 690), (520, 700), (612, 700)] + EDGE[1:] + [(490, 1244), (409, 1200), (372, 1230), (368, 1420), (0, 1420)]
    cape = cut(t8, CAPE)
    c = Image.new('RGBA', SZ, (0, 0, 0, 0))
    c.alpha_composite(cape)
    d = ImageDraw.Draw(c)
    d.line(EDGE, fill=(214, 172, 88, 255), width=6, joint='curve')
    # 披风压在外套的左边、盖过腰以下的左半，腰带右边那半还露着
    out = base.copy()
    out.alpha_composite(c)
    # 腰带和挂下来的皮带盖回披风上面
    BELT = [(592, 812), (706, 816), (714, 880), (690, 1010), (640, 1032), (600, 1040), (612, 900), (590, 850)]
    out.alpha_composite(cut(base, BELT))
    out.alpha_composite(scarf)

    # 4 抬起的胳膊、拳、剑、左肩甲：第七稿的，位置跟 t4 一样
    LARM = [(0, 0), (560, 0), (578, 480), (572, 600), (560, 636), (602, 655), (616, 692), (574, 738), (516, 736), (470, 690), (0, 690)]
    out.alpha_composite(cut(t8, LARM))

    # 5 右肩甲：顺着肩的斜度转一点
    RP = [(672, 660), (704, 662), (776, 712), (790, 800), (770, 806), (690, 768), (672, 708)]
    rp = cut(t8, RP).rotate(-8, resample=Image.BICUBIC, center=(690, 680))
    out.alpha_composite(rp, (8, 8))

    # 6 右小臂的护臂和手甲
    RF_OLD = [(728, 880), (800, 866), (836, 975), (828, 1016), (782, 1006), (766, 950)]
    out = clear(out, RF_OLD)
    RF = [(708, 868), (795, 840), (842, 955), (840, 1020), (790, 1016), (772, 960)]
    out.alpha_composite(cut(t8, RF))

    # 7 头缩一点：往颈根收
    HEAD = [(586, 470), (650, 465), (712, 490), (726, 570), (706, 618), (655, 628), (604, 628), (582, 600), (578, 530)]
    head = cut(out, HEAD)
    out = clear(out, HEAD)
    K = .86
    hc = (650, 632)
    h2 = head.resize((int(SZ[0] * K), int(SZ[1] * K)), Image.LANCZOS)
    out.alpha_composite(h2, (int(hc[0] - hc[0] * K), int(hc[1] - hc[1] * K)))

    # 8 左脚往前：靴子往上挪，落得高一点
    LB = [(372, 1362), (452, 1362), (452, 1510), (340, 1510)]
    boot = cut(out, LB, .8)
    out = clear(out, [(330, 1356), (470, 1356), (470, 1520), (330, 1520)])
    b2 = boot.resize((int(SZ[0] * .94), int(SZ[1] * .94)), Image.LANCZOS)
    out.alpha_composite(b2, (int(400 - 400 * .94) + 4, int(1370 - 1362 * .94 - 48)))
    # 下摆盖回靴子上面
    HEM = [(360, 1300), (480, 1290), (480, 1356), (378, 1356)]
    out.alpha_composite(cut(base, HEM))
    bg = Image.new('RGBA', SZ, (205, 205, 205, 255))
    bg.alpha_composite(out)
    bg.convert('RGB').save(path)


if __name__ == '__main__':
    build(sys.argv[1])
