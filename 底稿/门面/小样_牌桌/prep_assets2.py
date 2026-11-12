#!/usr/bin/env python3
# 牌桌小样第二版的素材（11-10 夜，照崩铁《来自星空的寓言集·上篇》黑天鹅抽牌那一段重做）。
#   python prep_assets2.py            （用 ComfyUI 那个带 PIL 的 python 跑）
# 三只手（gpt_front.py 的 h2_open、h2_press、h2_hold，一只一张竖幅透明底）裁到有东西的范围、量出指尖的位置；
# 四纪主画（横幅 1536×1024）原样压成 webp，牌面和收尾的画都用它。写 assets/，尺寸和指尖位置写 assets/info2.json。
import json
import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
COMFY = os.path.normpath(os.path.join(HERE, "..", "..", "状态栏", "comfy", "out"))
SRC = os.path.join(COMFY, "门面_小样_11-10")
MAIN = os.path.join(COMFY, "门面_主画_11-10")
LOCK = os.path.normpath(os.path.join(HERE, "..", "画风定稿样_t2.png"))
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)
info = {}


def save(im, name, q=90):
    p = os.path.join(OUT, name)
    im.save(p, "WEBP", quality=q, method=6)
    return os.path.getsize(p)


def tip(im, top):
    """指尖：最靠下（top=False）或最靠上（top=True）的那几行不透明像素的横向中点。"""
    a = im.getchannel("A")
    w, h = im.size
    px = a.load()
    rows = range(h) if top else range(h - 1, -1, -1)
    for y in rows:
        xs = [x for x in range(w) if px[x, y] > 128]
        if len(xs) >= 3:
            ys = range(y, min(h, y + 10)) if top else range(max(0, y - 9), y + 1)
            allx = [x for yy in ys for x in range(w) if px[x, yy] > 128]
            return round(sum(allx) / len(allx)), y
    return w // 2, 0 if top else h - 1


# 手
for key, top in (("open", False), ("press", False), ("hold", True)):
    p = os.path.join(SRC, "h2_%s.png" % key)
    if not os.path.exists(p):
        print("还没有", p)
        continue
    im = Image.open(p).convert("RGBA")
    box = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    # 从上边伸下来的两只：上边不裁；从下边伸上来的那只：下边不裁
    l, t, r, b = box
    if top:
        b = im.height
    else:
        t = 0
    im = im.crop((max(0, l - 4), t, min(im.width, r + 4), b))
    ax, ay = tip(im, top)
    info["hand_" + key] = {"size": im.size, "tip": [ax, ay], "bytes": save(im, "hand_%s.webp" % key, 92)}

# 四纪主画
for i, p in enumerate((LOCK, os.path.join(MAIN, "k2.png"), os.path.join(MAIN, "k3b.png"), os.path.join(MAIN, "k4.png"))):
    im = Image.open(p).convert("RGB")
    info["era_%d" % i] = {"size": im.size, "bytes": save(im, "era_%d.webp" % i, 86)}

json.dump(info, open(os.path.join(OUT, "info2.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
for k, v in info.items():
    print(k, v)
