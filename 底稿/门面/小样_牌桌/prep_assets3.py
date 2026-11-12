#!/usr/bin/env python3
# 牌桌小样第四版的素材（11-10 夜）。用户看了第三版：手不要袖子、黑丝手套加指甲；夹牌的那只重画；开场直接是牌桌；四纪各一张专属牌背。
#   python prep_assets3.py            （用 ComfyUI 那个带 PIL、numpy 的 python 跑）
# 读 状态栏/comfy/out/门面_小样_11-10/ 的 h3_open、h3_press（有 h3_press2 用它）、h3_hold（有 h3_hold2 用它）、b_0 到 b_3、table，写 assets/：
#   hand3_open/press/hold/palm.webp  四张手（palm 是夹牌那只的手心一面），裁到有东西的范围（伸进画面的那一头不裁）
#   back_0..3.webp              四纪的牌背，600×900
#   table.webp                  桌面，从正上方看的圆桌，1254 见方
# 尺寸和指尖位置写 assets/info3.json。月银纪那张牌背当中画了八颗星，抹掉最底下一颗剩七颗（七曜）。
import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "状态栏", "comfy", "out", "门面_小样_11-10"))
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)
info = {}


def save(im, name, q=90, **kw):
    p = os.path.join(OUT, name)
    im.save(p, "WEBP", quality=q, method=6, **kw)
    return os.path.getsize(p)


def pick(*names):
    """后写的优先：有重画的那一张就用重画的。命令行里写 press=h3_press 这样可以指定。"""
    for n in names:
        p = os.path.join(SRC, n + ".png")
        if os.path.exists(p):
            return p, n
    return None, None


FORCE = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)

# ---- 手 ----
# palm 是手心那一面（翻牌转过去以后露出来的），11-11 添的
# take 是带拇指的拿牌手（食指中指并着伸直，拇指在一旁），11-11 第十版添的，顶替 hold
# take5 是第十二版整只重画的拿牌手（五根手指都画清楚了：两指细长带关节、拇指从掌侧斜出来、无名指小指收拢），写成 hand5_take.webp，不盖第十、十一版用的那张
CANDS = {"palm": ["h3_palm_b", "h3_palm"], "take": ["h4_take", "h4_take_b"], "take5": ["h5_take_c", "h5_take", "h5_take_b"], "take6": ["h6_take_c", "h6_take_b", "h6_take"], "take8": ["h8_take_cut", "h8_take_b_cut", "h8_take_c_cut"]}
# take6 是第十四版照参考片逐帧量出来的比例重画的（手指是手背的两倍多长、食指中指紧挨着往指尖收、手背短手腕窄、拇指贴在食指左边），写成 hand6_take.webp
# take8 是第十四版用的：真手拿着绿牌画的那一张（h8_take*），绿牌先拿 key_card.py 抠掉（_cut），写成 hand8_take.webp。挑哪一张在命令行里写 take8=h8_take_b_cut
NAMES = {"take5": "hand5_take", "take6": "hand6_take", "take8": "hand8_take", "open8": "hand8_open"}
# open8 是第十五版用的发牌手（h8_open*）：照 take8 那一路的画法重画的张开的手。原图是手指朝上画的（模型画得稳），这里转半圈再用：手臂从上边伸下来，手指朝下，拇指在右
CANDS["open8"] = ["h8_open", "h8_open_b", "h8_open_c"]
# take9、open9 是第十六版用的：两只手照若娜瓦实际的手重画的（哑光黑手套，指尖是又长又尖的爪，手背到小臂几道银白纹），姿势照 take8、open8 没动。
# take9 同样先拿 key_card.py 抠掉绿牌（_cut），open9 同样转半圈
NAMES.update({"take9": "hand9_take", "open9": "hand9_open"})
CANDS["take9"] = ["h9_take_cut", "h9_take_b_cut", "h9_take_c_cut"]
CANDS["open9"] = ["h9_open", "h9_open_b", "h9_open_c"]
ROT180 = {"open8", "open9"}
LIFT = {"take9": .8, "open9": .8}          # 暗部提亮的指数（小于 1 是提亮）
EXTEND = {"take9": (300, 600)}             # 小臂最末 300 行拉成 600 行
for key, top in (("open", False), ("press", False), ("hold", True), ("palm", True), ("take", True), ("take5", True), ("take6", True), ("take8", True), ("open8", False), ("take9", True), ("open9", False)):
    p, used = pick(*([FORCE[key]] if key in FORCE else CANDS.get(key, ["h3_%s2" % key, "h3_%s" % key])))
    if not p:
        print("还没有", key)
        continue
    im = Image.open(p).convert("RGBA")
    if key in ROT180:
        im = im.rotate(180)
    a = np.array(im)
    if key in LIFT:
        # 黑手套画出来贴着黑底看不见：暗部往上提一点（越暗提得越多，白纹和亮边几乎不动），提完还是黑手套
        rgb = a[..., :3].astype(np.float32) / 255
        a[..., :3] = np.clip(np.power(rgb, LIFT[key]) * 255 + .5, 0, 255).astype(np.uint8)
    # 抠出来的边偶尔带一圈很淡的杂点：透明度很低的清成全透明，免得网格把它们也算成“有画”
    a[a[..., 3] < 20] = 0
    im = Image.fromarray(a)
    ys, xs = np.where(a[..., 3] > 24)
    l, t, r, b = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    if top:
        b = im.height      # 从下边伸上来的：下边不裁
    else:
        t = 0              # 从上边伸下来的：上边不裁
    box = (max(0, l - 6), t, min(im.width, r + 6), b)
    im = im.crop(box)
    if key in EXTEND:
        # 小臂不够长：手按在靠下的画带上时，图的那一头（小臂的切口）露在画面里。把最末一截小臂竖着拉长（小臂是一根带三道纹的直筒，拉长看不出来）
        src_rows, dst_rows = EXTEND[key]
        cut = im.height - src_rows
        tail = im.crop((0, cut, im.width, im.height)).resize((im.width, dst_rows), Image.LANCZOS)
        longer = Image.new("RGBA", (im.width, cut + dst_rows), (0, 0, 0, 0))
        longer.paste(im.crop((0, 0, im.width, cut)), (0, 0))
        longer.paste(tail, (0, cut))
        im = longer
    al = np.array(im)[..., 3]
    rows = np.where((al > 128).sum(1) >= 3)[0]
    y = int(rows.min() if top else rows.max())
    band = al[y:y + 10] if top else al[max(0, y - 9):y + 1]
    tipx = int(round(np.where(band > 128)[1].mean()))
    name = NAMES.get(key, "hand3_" + key)
    info[name] = {"from": used, "crop": box, "size": im.size, "tip": [tipx, y], "bytes": save(im, name + ".webp", 92, exact=True)}

# ---- 牌背 ----
for i in range(4):
    p = os.path.join(SRC, "b_%d.png" % i)
    if not os.path.exists(p):
        print("还没有", p)
        continue
    im = Image.open(p).convert("RGB")
    if i == 0:
        # 当中那一圈画成了八颗星，抹掉正下方那一颗：拿四周一圈的颜色按方向填进去，再补上原来的纸纹
        a = np.array(im).astype(np.float32)
        cx, cy, R = 513, 853, 40
        yy, xx = np.mgrid[cy - R - 8:cy + R + 9, cx - R - 8:cx + R + 9]
        d = np.hypot(xx - cx, yy - cy)
        ang = np.arctan2(yy - cy, xx - cx)
        ring = (d > R) & (d <= R + 6)
        fill = np.zeros(d.shape + (3,), np.float32)
        nb = 24
        cols = []
        for k in range(nb):
            m = ring & (np.floor((ang + np.pi) / (2 * np.pi) * nb).astype(int) % nb == k)
            cols.append(a[yy[m], xx[m]].mean(0))
        cols = np.array(cols)
        inside = d <= R
        fa = (ang[inside] + np.pi) / (2 * np.pi) * nb - .5
        k0 = np.floor(fa).astype(int) % nb
        k1 = (k0 + 1) % nb
        w = (fa - np.floor(fa))[:, None]
        edge = cols[k0] * (1 - w) + cols[k1] * w                 # 这个方向上圈边的颜色
        cen = cols.mean(0)
        t = (d[inside] / R)[:, None] ** 1.5
        fill_in = cen * (1 - t) + edge * t
        patch = a[cy - R - 8:cy + R + 9, cx - R - 8:cx + R + 9]
        # 纸纹：量一下圈边那一带的细颗粒有多重，照这个分量撒一层明暗的细噪点
        pim = Image.fromarray(patch.clip(0, 255).astype(np.uint8))
        hp = patch - np.array(pim.filter(ImageFilter.GaussianBlur(3))).astype(np.float32)
        sd = float(hp[ring].std())
        rng = np.random.default_rng(7)
        nz = Image.fromarray((rng.normal(0, 1, d.shape) * 40 + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.7))
        nz = (np.array(nz).astype(np.float32) - 128)
        gpatch = (nz / (nz.std() + 1e-6) * sd)[..., None] * np.ones(3, np.float32)
        soft = np.clip((R - d) / 5, 0, 1)[..., None]             # 边上羽化五个像素
        newp = patch.copy()
        tmp = patch.copy()
        tmp[inside] = fill_in + gpatch[inside]
        newp = patch * (1 - soft) + tmp * soft
        a[cy - R - 8:cy + R + 9, cx - R - 8:cx + R + 9] = newp
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
        im.crop((cx - 220, cy - 260, cx + 220, cy + 120)).save(os.path.join(HERE, "assets", "_b0_check.png"))
    im = im.resize((600, 900), Image.LANCZOS)
    info["back_%d" % i] = {"size": im.size, "bytes": save(im, "back_%d.webp" % i, 88)}

# ---- 桌面 ----
p = os.path.join(SRC, "table.png")
if os.path.exists(p):
    im = Image.open(p).convert("RGB")
    a = np.array(im).astype(np.float32)
    h, w = a.shape[:2]
    # 量一下圆桌在图里的范围（四角是黑的）
    lum = a.mean(2)
    cols = np.where(lum[h // 2] > 24)[0]
    rws = np.where(lum[:, w // 2] > 24)[0]
    info["table"] = {"size": im.size, "x": [int(cols.min()), int(cols.max())], "y": [int(rws.min()), int(rws.max())], "bytes": save(im, "table.webp", 86)}

json.dump(info, open(os.path.join(OUT, "info3.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
for k, v in info.items():
    print(k, v)
