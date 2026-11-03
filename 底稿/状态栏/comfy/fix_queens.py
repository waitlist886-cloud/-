#!/usr/bin/env python3
# 把双王的头从 pv/right_a.png 原样移植到右扇（用户 11-03 发了 right_a 双王那一段，说照这个修正容貌）。AI 重画一遍脸总会走样，所以直接搬像素。
# 底图 pv/right_f5.png（GPT 在 f3 上把头的大小和位置往 right_a 靠过，别的没动），放大到画布 1400×2000 再贴，脸不被放大一遍糊掉。写 pv/right_f6.png。
# 轮廓是照放大的网格手描的，坐标都是 right_a 的像素；BiRefNet 抠不准（王冠和耳坠丢了，巴尔缇娜和身后的披风分不开）。
#   python fix_queens.py        出 pv/right_f6.png，再跑 gpt_prepare.py pv_ab、cut_cpu.py（前缀 r_f6）、maze1001_frame_pv.py
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

P = os.path.join(HERE, 'out', '四方_11-03', 'pv')
W, H = 1400, 2000
BASE_W, BASE_H = 1049, 1500
CX, CY = W / BASE_W, H / BASE_H


def poly_mask(size, pts, blur):
    S = 2
    m = Image.new('L', (size[0] * S, size[1] * S), 0)
    ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in pts], fill=255)
    m = m.resize(size, Image.LANCZOS)
    return m.filter(ImageFilter.GaussianBlur(blur)) if blur else m


def background_of(keyed, protect):
    """keyed 是发丝缝里露出来的 right_a 的紫底。贴到新地方底色不一样，要去掉。眼白这类同色的在 protect 里不动；一两像素宽的细线是头发的线条，也不动。"""
    keyed = keyed & ~protect
    opened = ndimage.binary_opening(keyed, iterations=1)
    lab, n = ndimage.label(keyed)
    return np.isin(lab, np.unique(lab[opened]))


def harmonic_fill(arr, mask, iters=600):
    """旧头露在新头外面的边角抹掉：拿四周的颜色往里渗。只用在很小的地方。"""
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return arr
    y0, y1, x0, x1 = max(ys.min() - 3, 0), ys.max() + 4, max(xs.min() - 3, 0), xs.max() + 4
    out = arr.astype(np.float32).copy()
    sub = out[y0:y1, x0:x1]
    m = mask[y0:y1, x0:x1]
    k = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], np.float32) / 4
    for c in range(3):
        v = sub[..., c]
        v[m] = v[~m].mean()
        for _ in range(iters):
            nv = ndimage.convolve(v, k, mode='nearest')
            v[m] = nv[m]
    return np.uint8(np.clip(out, 0, 255))


# ---- 索恩薇娅
S_HARD = [(22, 1200), (12, 1172), (7, 1145), (9, 1122), (16, 1097), (31, 1070), (49, 1046), (74, 1025), (86, 1017), (92, 998),
          (101, 996), (89, 965), (106, 976),              # 王冠从左数第一根
          (104, 928), (126, 958),                         # 第二根
          (125, 899), (157, 948), (164, 962),             # 第三根
          (169, 943), (184, 898), (200, 940), (204, 966),  # 第四根
          (216, 955), (230, 924), (237, 965),             # 第五根
          (261, 945), (252, 974),                         # 第六根
          (275, 978), (300, 988), (320, 1006), (326, 1003), (340, 1010), (356, 1018), (375, 1021), (398, 1040), (405, 1070), (408, 1081),   # 头顶到发髻
          (402, 1100), (402, 1125), (403, 1172), (393, 1184), (376, 1202), (360, 1212), (345, 1211), (329, 1203), (320, 1214), (300, 1224), (276, 1242), (256, 1258),
          (246, 1266), (225, 1272), (208, 1274), (208, 1292), (165, 1292), (152, 1248),   # 脖子、侧发
          (120, 1258), (86, 1269), (74, 1226), (54, 1191), (52, 1207), (40, 1200)]        # 下颌、脸、鼻尖
S_SOFT = [(-60, 840), (460, 840), (460, 1262), (225, 1262), (150, 1272), (140, 1310), (-60, 1310)]   # 只有脖子和侧发的下沿是软的
# ---- 巴尔缇娜
B_HARD = [(445, 1222), (425, 1190), (410, 1163), (402, 1140), (400, 1108), (405, 1085), (414, 1065), (427, 1045), (450, 1000), (482, 966), (487, 964), (515, 955), (525, 950),
          (575, 920), (600, 908), (625, 899), (650, 898), (675, 904), (700, 914), (720, 930), (743, 952), (755, 964), (762, 982), (770, 981), (779, 988), (783, 998), (790, 1010), (790, 1025), (781, 1037), (771, 1042),   # 头顶到辫子结
          (778, 1100), (775, 1180), (757, 1228), (725, 1230), (675, 1241), (625, 1258), (600, 1266), (566, 1276), (552, 1276), (550, 1248),   # 脑后、领子上沿
          (525, 1257), (499, 1268), (481, 1224), (475, 1217), (468, 1227)]                # 下颌、脸
B_SOFT = [(350, 840), (830, 840), (830, 1040), (771, 1044), (768, 1100), (765, 1176), (748, 1220), (725, 1222), (675, 1233), (625, 1250), (600, 1258), (566, 1266), (556, 1268), (545, 1300), (350, 1300)]

# 头：硬边、软边、软边的模糊、right_a 的锚点（鼻尖）、right_f5 的锚点、比例、转角（度，顺时针）
SORN = dict(hard=S_HARD, soft=S_SOFT, soft_blur=4, src=(55, 1191), dst=(213, 1152), scale=0.49, rot=0.0,
            key=lambda a, y, x: (a[..., 2].astype(int) - a[..., 0].astype(int)) > 12,
            protect=[(85, 1095), (175, 1095), (175, 1200), (85, 1200)],   # 眼睛那一块
            fades=[(150, 212, 1236, 1292)])                               # 侧发慢慢接到底图的侧发上
BALT = dict(hard=B_HARD, soft=B_SOFT, soft_blur=7, src=(456.75, 1187.5), dst=(425, 989), scale=0.53, rot=2.0,
            key=lambda a, y, x: (a[..., 0] < 165) & ((a[..., 2].astype(int) - a[..., 0].astype(int)) > 15) & (x < 472) & (y > 1040),
            protect=[], fades=[])
# 贴完以后再盖回底图的地方（right_f5 坐标）：握杖的手和杖在索恩薇娅发髻前面，剑也在头前面
KEEP = [
    [(374, 1040), (390, 1040), (390, 1090), (408, 1098), (410, 1150), (402, 1175), (372, 1175), (366, 1150), (364, 1115), (372, 1093)],
]


# 旧头露在新头外面的地方（right_f5 坐标）
OLD_CROWN = [(220, 1062), (220, 1030), (240, 1010), (272, 1006), (305, 1013), (325, 1030), (325, 1062)]
OLD_BITS = [
    [(286, 1179), (304, 1179), (304, 1193), (286, 1193)],   # 旧耳坠的尖
    [(222, 1168), (262, 1158), (258, 1178), (256, 1186), (232, 1197), (224, 1192)],   # 旧下巴比新的低一点，上半截反正叫新脸盖着
]


def head_layer(a, h):
    """在 right_a 上算好这颗头的透明度，变换到画布上，回 RGBA 层。"""
    src_h, src_w = a.shape[:2]
    size = (src_w, src_h)
    inside = np.asarray(poly_mask(size, h['hard'], 0)) > 127
    yy, xx = np.mgrid[0:src_h, 0:src_w]
    protect = np.asarray(poly_mask(size, h['protect'], 0)) > 127 if h['protect'] else np.zeros_like(inside)
    key = background_of(h['key'](a, yy, xx) & inside, protect)
    key |= ndimage.binary_dilation(key, iterations=4) & ~ndimage.binary_erosion(inside, iterations=4)   # 去掉的地方挨着轮廓线时接到轮廓外面去，不然两个模糊一乘留一道淡线
    al = np.asarray(poly_mask(size, h['hard'], 0.9)).astype(np.float32) / 255
    al = al * (np.asarray(poly_mask(size, h['soft'], h['soft_blur'])).astype(np.float32) / 255)
    keep = np.asarray(Image.fromarray(np.uint8(~key * 255)).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32) / 255
    al = al * keep
    for x0, x1, y0, y1 in h['fades']:
        r = np.clip((y1 - yy.astype(np.float32)) / (y1 - y0), 0, 1)
        al = np.where((xx >= x0) & (xx <= x1), al * r, al)
    rgba = np.dstack([a[..., :3].astype(np.float32), al * 255])
    im = Image.fromarray(np.uint8(np.clip(rgba, 0, 255)), 'RGBA')
    # 预乘再缩，边上不带出底色
    arr = np.asarray(im).astype(np.float32)
    arr[..., :3] *= arr[..., 3:4] / 255
    f = h['scale'] * CX
    w2, h2 = round(src_w * f), round(src_h * f)
    chans = [Image.fromarray(arr[..., i], 'F').resize((w2, h2), Image.LANCZOS) for i in range(4)]
    th = np.radians(h['rot'])
    cs, sn = np.cos(th), np.sin(th)
    ux, uy = h['src'][0] * w2 / src_w, h['src'][1] * h2 / src_h
    vx, vy = h['dst'][0] * CX, h['dst'][1] * CY
    # 画布坐标 → 缩好的图的坐标
    co = (cs, sn, ux - cs * vx - sn * vy, -sn, cs, uy + sn * vx - cs * vy)
    out = [np.asarray(c.transform((W, H), Image.AFFINE, co, resample=Image.BICUBIC)) for c in chans]
    A = np.clip(out[3], 0, 255)
    RGB = np.dstack(out[:3]) / np.maximum(A[..., None] / 255, 1e-3)
    return Image.fromarray(np.uint8(np.clip(np.dstack([RGB, A]), 0, 255)), 'RGBA')


def compose(under=None):
    """under(base) 在盖头以前改底图，fix_gods.py 用它把四位七神贴进去，头和杖照旧压在上面。"""
    src = np.asarray(Image.open(os.path.join(P, 'right_a.png')).convert('RGB'))
    base = Image.open(os.path.join(P, 'right_f5.png')).convert('RGB').resize((W, H), Image.LANCZOS)
    arr = np.asarray(base)
    # 旧的王冠：框里偏金的都算；别的旧边角整块抹
    box = np.asarray(poly_mask((W, H), [(x * CX, y * CY) for x, y in OLD_CROWN], 0)) > 127
    gold = (arr[..., 0].astype(int) - arr[..., 2].astype(int)) > 28
    mask = ndimage.binary_dilation(box & gold, iterations=3) & box
    for pts in OLD_BITS:
        mask |= np.asarray(poly_mask((W, H), [(x * CX, y * CY) for x, y in pts], 0)) > 127
    base = Image.fromarray(harmonic_fill(arr, mask)).convert('RGBA')
    if under:
        base = under(base)
    c = base.copy()
    c.alpha_composite(head_layer(src, BALT))
    c.alpha_composite(head_layer(src, SORN))
    for pts in KEEP:
        m = poly_mask((W, H), [(x * CX, y * CY) for x, y in pts], 1.2)
        c.paste(base, (0, 0), m)
    return c.convert('RGB')


if __name__ == '__main__':
    c = compose()
    c.save(os.path.join(P, 'right_f6.png'))
    print('ok', c.size)
