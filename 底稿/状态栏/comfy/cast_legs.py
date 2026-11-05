#!/usr/bin/env python3
# 把成年女性立绘的膝盖往上挪（用户说膝盖过低、小腿过短，像鸟腿）。量的结果：姬子、阿格莱雅官方站姿的膝盖在身高约三分之二，膝盖以下约是大腿的 1.4 倍；我们的在 73% 上下，只有 1.1 倍。
# 只竖着挪像素，不过模型：胯到膝压短，膝到脚底拉长，平滑过渡，上身和总高不变。
#   from cast_legs import lift_knee
#   lift_knee(图, 胯y, 膝y, 新膝y, 脚底y)
import numpy as np
from PIL import Image
from scipy.interpolate import PchipInterpolator


def lift_knee(im, crotch, knee, knee_new, sole):
    """回一张同样大小的图。行号 y 从 新图 映射回 旧图，单调三次插值，折点处没有硬折。"""
    im = im.convert('RGBA')
    a = np.asarray(im).astype(np.float32)
    # 先把颜色乘上透明度再插值，透明边不出黑边
    a[..., :3] *= a[..., 3:4] / 255
    h = a.shape[0]
    src = PchipInterpolator([0, crotch - 90, crotch, knee_new, sole, h - 1], [0, crotch - 90, crotch, knee, sole, h - 1])(np.arange(h))
    y0 = np.clip(np.floor(src).astype(int), 0, h - 1)
    y1 = np.clip(y0 + 1, 0, h - 1)
    t = (src - y0)[:, None, None]
    out = a[y0] * (1 - t) + a[y1] * t
    al = out[..., 3:4]
    out[..., :3] = np.where(al > 0, out[..., :3] * 255 / np.maximum(al, 1), 0)
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8), 'RGBA')
