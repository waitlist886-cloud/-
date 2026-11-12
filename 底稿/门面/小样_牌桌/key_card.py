# 把“真手拿着一张纯绿的牌”那张图里的绿牌抠掉，只留手（第十四版，h7_take*）。
#   python key_card.py h7_take_b            出 comfy/out/门面_小样_11-10/h7_take_b_cut.png，顺带报绿牌在图上的四个角
# 画手的时候让模型把牌画成纯绿的平板：画里有牌，它才知道手在干什么、手指怎么搭，画出来才是正常人的手；牌是另一层，出图以后抠掉。
# 抠法：绿得越纯越透明（绿减去红蓝里大的那个）；手指边上跟绿混在一起的那一圈按比例半透明，绿色的溢色压掉。
import os
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "状态栏", "comfy", "out", "门面_小样_11-10"))
name = sys.argv[1]
im = Image.open(os.path.join(SRC, name + ".png")).convert("RGBA")
a = np.array(im).astype(np.float32)
r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
spill = g - np.maximum(r, b)                     # 手是灰褐和红，这个数是负的或者零；牌是一两百
card = (spill > 90) & (al > 128)
ys, xs = np.where(card)
print("绿牌像素", int(card.sum()), "范围", int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
# 牌的四个角：凸包上离中心最远的四个方向（拿主轴摆正以后取四个极值角）
pts = np.stack([xs, ys], 1).astype(np.float32)
c = pts.mean(0)
u, s, vt = np.linalg.svd((pts - c)[::7], full_matrices=False)
ax_long = vt[0] if abs(vt[0][1]) > abs(vt[0][0]) else vt[1]      # 长轴（竖着的那一根）
if ax_long[1] > 0:
    ax_long = -ax_long                                              # 朝上
ax_wide = np.array([-ax_long[1], ax_long[0]])                      # 朝右
pl, pw = (pts - c) @ ax_long, (pts - c) @ ax_wide
L0, L1, W0, W1 = np.percentile(pl, .3), np.percentile(pl, 99.7), np.percentile(pw, .3), np.percentile(pw, 99.7)
cen = c + ax_long * (L0 + L1) / 2 + ax_wide * (W0 + W1) / 2
ang = float(np.degrees(np.arctan2(ax_long[0], -ax_long[1])))       # 从朝上顺时针多少度
print("牌心 %.1f,%.1f  长 %.1f  宽 %.1f  长宽比 %.3f  歪 %.2f 度" % (cen[0], cen[1], L1 - L0, W1 - W0, (L1 - L0) / (W1 - W0), ang))
print("近边（靠手那一头）的中点 %.1f,%.1f" % tuple(cen + ax_long * (L0 - (L0 + L1) / 2)))
# 抠
k = np.clip((spill - 14) / 70, 0, 1)             # 绿多少：0 是手，1 是牌
# 牌上手指投下来的影子是暗绿，光看差值抠不干净：再看绿占多少成（暗绿也是十成绿），两样取大的
ratio = np.where(g > 26, spill / np.maximum(g, 1), 0)
k = np.maximum(k, np.clip((ratio - .1) / .4, 0, 1))
al2 = al * (1 - k)
g2 = np.minimum(g, np.maximum(r, b) + 4)          # 压掉溢色
out = np.stack([r, g2, b, al2], -1)
# 抠完以后牌那一片里剩下的零星杂点清掉：离手远的、很淡的
out[(al2 < 26)] = 0
# 画里被牌边切出来的平头：牌另放在别处以后会露出来，修成圆的。只有这一张图要修，位置是放大了打格子量的
if name == "h7_take_b":
    H, W = al2.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    lum = (r + g2 + b) / 3
    # 一、左上角拇指尖：牌的近边把它切成了平头，连着它跟食指之间那一块暗角。拇指尖改成圆头（椭圆心 371,590，横 17 竖 20），圆头以外、食指左边的都去掉
    edge = 420 - .636 * (yy - 556) - 2                           # 食指左边那条线
    zone = (xx < edge) & (yy > 540) & (yy < 606) & (xx > 338)
    inside = ((xx - 371) / 17) ** 2 + ((yy - 590) / 20) ** 2    # 小于 1 在圆头里
    keep = np.where(yy >= 590, (xx <= 388).astype(np.float32), np.clip((1 - inside) * 9 + .5, 0, 1))
    out[..., 3] = np.where(zone, out[..., 3] * keep, out[..., 3])
    # 二、中指和无名指之间的指蹼：顶上被牌边切平了。只动那一块暗色，改成往下凹的一道弧，两边手指的描边不碰
    zone = (xx > 552) & (xx < 600) & (yy > 572) & (yy < 603) & (lum < 78)
    top = 600 - 3 * (1 - ((xx - 576) / 20) ** 2)
    out[..., 3] = np.where(zone, out[..., 3] * np.clip(yy - top + .5, 0, 1), out[..., 3])
res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
p = os.path.join(SRC, name + "_cut.png")
res.save(p)
print(p, res.size, res.getbbox())
