#!/usr/bin/env python3
# 牌桌小样的素材：把 gpt_front.py 出的四张图（h_bg、h_hands、h_cards、h_eye）切成页面用的小图，写 assets/。
#   python prep_assets.py            （用 ComfyUI 那个带 PIL 的 python 跑）
# 手、牌、眼睛是透明底的一排东西，照透明的空列切开；牌和眼睛各自对齐到同一个尺寸。打印每样的尺寸，页面里的坐标照它填。
import json
import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "状态栏", "comfy", "out", "门面_小样_11-10"))
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)


def runs(im, gap=10, thr=24, min_w=30):
    """透明底的图照竖列切：返回每一块的 (左, 右)。"""
    a = im.getchannel("A")
    w, h = im.size
    px = a.load()
    cols = [any(px[x, y] > thr for y in range(0, h, 2)) for x in range(w)]
    out, start, blank = [], None, 0
    for x, on in enumerate(cols):
        if on:
            if start is None:
                start = x
            blank = 0
        elif start is not None:
            blank += 1
            if blank >= gap:
                out.append((start, x - blank + 1))
                start, blank = None, 0
    if start is not None:
        out.append((start, w))
    return [r for r in out if r[1] - r[0] >= min_w]


def crop_alpha(im):
    box = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    return im.crop(box), box


def save(im, name, q=88):
    p = os.path.join(OUT, name)
    im.save(p, "WEBP", quality=q, method=6)
    return os.path.getsize(p)


info = {}

# 底图
bg = Image.open(os.path.join(SRC, "h_bg.png")).convert("RGB")
bg = bg.resize((1024, 1536), Image.LANCZOS)
info["bg"] = {"size": bg.size, "bytes": save(bg, "bg.webp", 84)}

# 手：左右各一只。上边不裁（胳膊是从上边伸下来的）
hands = Image.open(os.path.join(SRC, "h_hands.png")).convert("RGBA")
print("hands 原图", hands.size, "透明度范围", hands.getchannel("A").getextrema())
rs = runs(hands, gap=40, min_w=80)
print("hands 切出", rs)
rs = sorted(rs, key=lambda r: r[1] - r[0], reverse=True)[:2]
rs.sort()
for name, (l, r) in zip(("hand_l", "hand_r"), rs):
    part = hands.crop((l, 0, r, hands.height))
    bottom = part.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()[3]
    part = part.crop((0, 0, part.width, bottom))
    info[name] = {"size": part.size, "bytes": save(part, name + ".webp", 90)}

# 牌：五张，对齐到同一个尺寸
cards = Image.open(os.path.join(SRC, "h_cards.png")).convert("RGBA")
print("cards 原图", cards.size, "透明度范围", cards.getchannel("A").getextrema())
rs = runs(cards, gap=8, min_w=80)
print("cards 切出", rs)
parts = [crop_alpha(cards.crop((l, 0, r, cards.height)))[0] for l, r in rs]
if parts:
    cw = max(p.width for p in parts)
    ch = max(p.height for p in parts)
    names = ["card_0", "card_1", "card_2", "card_3", "card_back"]
    for name, p in zip(names, parts):
        canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        canvas.paste(p, ((cw - p.width) // 2, ch - p.height))
        info[name] = {"size": canvas.size, "bytes": save(canvas, name + ".webp", 90)}

# 眼睛：三帧，拼成一条
eye = Image.open(os.path.join(SRC, "h_eye.png")).convert("RGBA")
print("eye 原图", eye.size, "透明度范围", eye.getchannel("A").getextrema())
rs = runs(eye, gap=8, min_w=60)
print("eye 切出", rs)
if len(rs) != 3:
    # 三只之间有很淡的影子连着，照竖列切不开：整条的外框三等分，每一格再照高一点的透明度裁
    l0, r0 = rs[0][0], rs[-1][1]
    step = (r0 - l0) / 3
    rs = [(int(l0 + i * step), int(l0 + (i + 1) * step)) for i in range(3)]


def crop_hard(im, thr=90):
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > thr else 0).getbbox())


parts = [crop_hard(eye.crop((l, 0, r, eye.height))) for l, r in rs][:3]
if parts:
    ew = max(p.width for p in parts)
    eh = max(p.height for p in parts)
    strip = Image.new("RGBA", (ew * len(parts), eh), (0, 0, 0, 0))
    for i, p in enumerate(parts):
        strip.paste(p, (i * ew + (ew - p.width) // 2, (eh - p.height) // 2))
    k = 240 / ew if ew > 240 else 1
    strip = strip.resize((int(strip.width * k), int(strip.height * k)), Image.LANCZOS)
    info["eye"] = {"size": strip.size, "frames": len(parts), "bytes": save(strip, "eye.webp", 90)}

json.dump(info, open(os.path.join(OUT, "info.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
for k, v in info.items():
    print(k, v)
