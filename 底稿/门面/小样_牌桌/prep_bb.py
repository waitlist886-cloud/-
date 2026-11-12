#!/usr/bin/env python3
# 四纪的大幅牌背（四条画带上放的那一张）：从 状态栏/comfy/out/门面_小样_11-10/ 挑好的图存成 assets/bb_0..3.webp（1024×1536）。
#   python prep_bb.py 0=bb2_0 1=bb2_1r 2=bb2_2 3=bb2_3      哪一纪用哪一张（不带扩展名）
# 图是 gpt_front.py 的 bb_*（第一稿）、bb2_*（第二稿，华丽的）出的。徽记的心在图高的几成，页面里 BACK_CY 和样式的 --bcy 跟着它填。
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "状态栏", "comfy", "out", "门面_小样_11-10"))
for a in sys.argv[1:]:
    k, name = a.split("=", 1)
    im = Image.open(os.path.join(SRC, name + ".png")).convert("RGB")
    if im.size != (1024, 1536):
        im = im.resize((1024, 1536), Image.LANCZOS)
    out = os.path.join(HERE, "assets", "bb_%s.webp" % k)
    im.save(out, "WEBP", quality=86, method=6)
    print(k, name, im.size, os.path.getsize(out))
