#!/usr/bin/env python3
# 假人（11-04）：用户说山铜纪最大的问题是姿势、人体和比例。叫 GPT 自己定比例，它总把头画小、把手脚拉长，修补也修不掉，所以这两样这边定死：
# 照骨长搭一个立体的假人，投影成图给它当底稿，它只管穿衣服和上色。方向写三维向量：x 往图的右，y 往上，z 朝看的人。骨长是固定的，朝着人伸的胳膊自然就短了。
# 用户看了头一版说假人还是怪：手脚全摊在一个平面上，像纸娃娃。所以加了镜头 cam=dict(pitch=镜头压低多少度, yaw=转多少度, roll=歪多少度, D=镜头离多远，头高为单位)，近的手脚自然大、远的小。
#   from mannequin import draw
#   im, joints = draw(canvas, [dict(kind='woman', root=(x, y), u=头高的像素, spine=(下段, 上段), hips=, shoulders=, neck=, head=, face=,
#                                   arm_a=(上臂, 前臂, 手), arm_b=, leg_a=(大腿, 小腿, 脚), leg_b=, props=[(起点关节, 方向, 往后, 往前, 粗, 颜色)])])
# arm_a、leg_a 在 shoulders、hips 那个向量指的那一头（看图的时候是蓝的），arm_b、leg_b 在另一头（橙的）。
# 要 numpy、PIL。
import math
import numpy as np
from PIL import Image, ImageDraw

# 长度都以头高为一。全身：woman 约 6.6 头，man 约 7 头，youth 约 6.4 头，stocky（矮壮的女人）约 6 头，dwarf 约 4.6 头，giant（魁梧的男人）约 7.2 头
BODY = {
    'woman': dict(neck=.25, chest=1.3, waist=.7, sh=.68, hip=.38, upper=1.18, fore=1.02, hand=.7, thigh=1.62, shin=1.55, foot=.85,
                  w_upper=(.40, .30), w_fore=(.30, .19), w_hand=.24, w_thigh=(.62, .38), w_shin=(.40, .22), w_foot=.26, w_waist=.40, w_hip=.62, w_neck=.26),
    'man': dict(neck=.3, chest=1.45, waist=.7, sh=.92, hip=.42, upper=1.3, fore=1.12, hand=.75, thigh=1.75, shin=1.65, foot=.95,
                w_upper=(.50, .38), w_fore=(.38, .24), w_hand=.28, w_thigh=(.72, .46), w_shin=(.50, .26), w_foot=.3, w_waist=.55, w_hip=.66, w_neck=.36),
    'youth': dict(neck=.28, chest=1.3, waist=.65, sh=.8, hip=.4, upper=1.2, fore=1.05, hand=.72, thigh=1.62, shin=1.52, foot=.88,
                  w_upper=(.44, .34), w_fore=(.34, .22), w_hand=.26, w_thigh=(.64, .42), w_shin=(.44, .24), w_foot=.28, w_waist=.48, w_hip=.58, w_neck=.3),
    'stocky': dict(neck=.2, chest=1.2, waist=.62, sh=.86, hip=.44, upper=1.08, fore=.94, hand=.68, thigh=1.36, shin=1.28, foot=.8,
                   w_upper=(.50, .38), w_fore=(.38, .24), w_hand=.28, w_thigh=(.70, .44), w_shin=(.46, .26), w_foot=.28, w_waist=.52, w_hip=.68, w_neck=.32),
    'giant': dict(neck=.28, chest=1.6, waist=.72, sh=1.28, hip=.52, upper=1.42, fore=1.22, hand=.82, thigh=1.72, shin=1.62, foot=1.0,
                  w_upper=(.72, .56), w_fore=(.56, .36), w_hand=.38, w_thigh=(.9, .6), w_shin=(.64, .36), w_foot=.38, w_waist=.72, w_hip=.82, w_neck=.5),
    'dwarf': dict(neck=.12, chest=1.25, waist=.5, sh=1.2, hip=.5, upper=.98, fore=.9, hand=.8, thigh=.85, shin=.72, foot=.8,
                  w_upper=(.72, .60), w_fore=(.60, .42), w_hand=.44, w_thigh=(.85, .62), w_shin=(.62, .42), w_foot=.42, w_waist=.85, w_hip=.85, w_neck=.5),
}
COL = dict(a=(64, 110, 214), a2=(104, 150, 232), b=(218, 92, 56), b2=(236, 142, 104), chest=(206, 204, 196), pelvis=(170, 168, 160), neck=(226, 204, 176), head=(246, 222, 190), joint=(40, 40, 46))
BG = (244, 242, 238)
SS = 2      # 先画两倍大再缩，边顺


def unit(v):
    v = np.array(v, float)
    return v / np.linalg.norm(v)


def two_bone(s0, target, L1, L2, pole):
    """两节骨头够到一个点，胳膊肘（膝盖）往 pole 那边弯。够不到就伸直。回两节的方向。"""
    d = target - s0
    dist = np.linalg.norm(d)
    dn = d / dist
    dist = min(dist, (L1 + L2) * .995)
    a = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(L1 * L1 - a * a, 0))
    p = unit(pole)
    p = unit(p - dn * p.dot(dn))
    j = s0 + dn * a + p * h
    return unit(j - s0), unit(s0 + dn * dist - j)


def bones(f):
    """算关节，回 {名字: 三维坐标}，单位是头高，原点在骨盆正中。"""
    B = BODY[f.get('kind', 'woman')]
    s = dict(root=np.zeros(3))
    sp = f.get('spine', ((0, 1, 0), (0, 1, 0)))
    s['waist'] = s['root'] + unit(sp[0]) * B['waist']
    s['nb'] = s['waist'] + unit(sp[1]) * B['chest']                     # 脖子根
    sc = s['nb'] - unit(sp[1]) * .16
    ls, lh = unit(f.get('shoulders', (1, 0, 0))), unit(f.get('hips', (1, 0, 0)))
    s['sa'], s['sb'] = sc + ls * B['sh'], sc - ls * B['sh']
    s['ha'], s['hb'] = lh * B['hip'], -lh * B['hip']
    s['hbase'] = s['nb'] + unit(f.get('neck', (0, 1, 0))) * B['neck']    # 下巴那一圈
    s['crown'] = s['hbase'] + unit(f.get('head', (0, 1, 0)))
    lr, lu = f.get('lroot', f['root']), f.get('lu', f['u'])

    def to3(q):           # to 写的是排版时图上的像素 (x, y) 和 z（头高）
        return np.array([(q[0] - lr[0]) / lu, (lr[1] - q[1]) / lu, q[2] if len(q) > 2 else 0.0])

    for side in 'ab':
        arm = f.get('arm_' + side, ((0, -1, 0), (0, -1, 0), (0, -1, 0)))
        if isinstance(arm, dict):
            u, fo = two_bone(s['s' + side], to3(arm['to']), B['upper'], B['fore'], arm.get('pole', (0, -1, 0)))
            h = arm.get('hand', fo)
        else:
            u, fo, h = arm
        s['el' + side] = s['s' + side] + unit(u) * B['upper']
        s['wr' + side] = s['el' + side] + unit(fo) * B['fore']
        s['ft' + side] = s['wr' + side] + unit(h) * B['hand']
        leg = f.get('leg_' + side, ((0, -1, 0), (0, -1, 0), (0, 0, 1)))
        if isinstance(leg, dict):
            t, sh = two_bone(s['h' + side], to3(leg['to']), B['thigh'], B['shin'], leg.get('pole', (0, 0, 1)))
            ft = leg.get('foot', (0, 0, 1))
        else:
            t, sh, ft = leg
        s['kn' + side] = s['h' + side] + unit(t) * B['thigh']
        s['an' + side] = s['kn' + side] + unit(sh) * B['shin']
        s['to' + side] = s['an' + side] + unit(ft) * B['foot']
    return s, B


def draw(canvas, figs, bg=BG):
    """canvas=(宽, 高)。回 (图, [每个人的 {关节: 图上的像素}])。"""
    W, H = canvas
    im = Image.new('RGB', (W * SS, H * SS), bg)
    d = ImageDraw.Draw(im)
    allj = []
    for f in figs:
        s, B = bones(f)
        rx, ry, u = f['root'][0], f['root'][1], f['u']
        cam = f.get('cam', {})
        R = camera(cam.get('pitch', 0), cam.get('yaw', 0), cam.get('roll', 0))
        D = cam.get('D', 0)

        def view(p):
            q = R @ np.array(p, float)
            k = D / max(D - q[2], .5) if D else 1.0
            return q, k

        def px(p):
            q, k = view(p)
            return np.array([(rx + q[0] * k * u) * SS, (ry - q[1] * k * u) * SS])

        def zk(p):
            return view(p)[1]

        def zz(p):
            return view(p)[0][2]

        items = []     # (平均 z, 画法)

        def caps(a, b, ra, rb, col):
            items.append(((zz(s[a]) + zz(s[b])) / 2, ('c', px(s[a]), px(s[b]), ra * zk(s[a]) * u * SS / 2, rb * zk(s[b]) * u * SS / 2, col)))

        for side, c1, c2 in (('a', COL['a'], COL['a2']), ('b', COL['b'], COL['b2'])):
            caps('s' + side, 'el' + side, *B['w_upper'], c1)
            caps('el' + side, 'wr' + side, *B['w_fore'], c1)
            caps('wr' + side, 'ft' + side, B['w_hand'] * .9, B['w_hand'] * 1.15, c1)
            caps('h' + side, 'kn' + side, *B['w_thigh'], c2)
            caps('kn' + side, 'an' + side, *B['w_shin'], c2)
            caps('an' + side, 'to' + side, B['w_foot'] * 1.0, B['w_foot'] * .8, c2)
        # 躯干：肩到腰、腰到胯，一块一块
        lh = unit(f.get('hips', (1, 0, 0)))
        ls = unit(f.get('shoulders', (1, 0, 0)))
        lw = unit(lh + ls)
        wa, wb = s['waist'] + lw * B['w_waist'], s['waist'] - lw * B['w_waist']
        ha, hb = s['ha'] + lh * (B['w_hip'] - B['hip']), s['hb'] - lh * (B['w_hip'] - B['hip'])
        items.append(((zz(s['sa']) + zz(s['sb']) + zz(s['waist'])) / 3, ('p', [px(s['sa'] + ls * .12), px(s['nb']), px(s['sb'] - ls * .12), px(wb), px(wa)], COL['chest'])))
        items.append(((zz(s['waist']) + zz(s['root'])) / 2, ('p', [px(wa), px(wb), px(hb), px(s['root'] + np.array([0, -.42, 0])), px(ha)], COL['pelvis'])))
        wd = B['w_waist'] * 1.7
        items.append(((zz(s['waist']) + zz(s['nb'])) / 2 - .01, ('c', px(s['waist']), px(s['nb'] - unit(s['nb'] - s['waist']) * .25), wd * zk(s['waist']) * u * SS / 2, wd * 1.2 * zk(s['nb']) * u * SS / 2, COL['chest'])))
        items.append(((zz(s['waist']) + zz(s['root'])) / 2 - .01, ('c', px(s['root']), px(s['waist']), B['w_hip'] * 1.3 * u * SS / 2, wd * zk(s['waist']) * u * SS / 2, COL['pelvis'])))
        caps('nb', 'hbase', B['w_neck'], B['w_neck'], COL['neck'])
        # 头
        up = unit(s['crown'] - s['hbase'])
        fc = np.array(f.get('face', (0, 0, 1)), float)
        fc = unit(fc - up * fc.dot(up))
        rt = np.cross(up, fc)
        c = (s['crown'] + s['hbase']) / 2
        items.append((zz(c), ('h', c, up, fc, rt)))
        # 兵器：从某个关节穿过去的一根直线
        for pr in f.get('props', ()):
            j, dr, back, fore, w, col = pr
            dr = unit(dr)
            a, b = s[j] - dr * back, s[j] + dr * fore
            items.append(((zz(a) + zz(b)) / 2 + float(f.get('prop_z', 0)), ('l', px(a), px(b), w * zk(a) * u * SS / 2, w * zk(b) * u * SS / 2, col)))
        items.sort(key=lambda t: t[0])
        for _, it in items:
            if it[0] == 'c':
                _caps(d, *it[1:])
            elif it[0] == 'p':
                d.polygon([tuple(p) for p in it[1]], fill=it[2], outline=(60, 60, 66), width=2 * SS)
            elif it[0] == 'l':
                _caps(d, it[1], it[2], it[3], it[4], it[5])
            else:
                _head(d, px, u * zk(it[1]), R, *it[1:])
        for j in ('ela', 'elb', 'wra', 'wrb', 'kna', 'knb', 'ana', 'anb', 'sa', 'sb'):
            p = px(s[j])
            r = .05 * zk(s[j]) * u * SS
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=COL['joint'])
        allj.append({k: tuple(px(v) / SS) for k, v in s.items()})
    return im.resize((W, H), Image.LANCZOS), allj


def _caps(d, a, b, ra, rb, col):
    v = b - a
    n = np.array([-v[1], v[0]])
    nn = np.linalg.norm(n)
    if nn < 1e-6:
        return
    n = n / nn
    ol = 2 * SS
    for pad, c in ((ol, (50, 50, 56)), (0, col)):
        pts = [a + n * (ra + pad), b + n * (rb + pad), b - n * (rb + pad), a - n * (ra + pad)]
        d.polygon([tuple(p) for p in pts], fill=c)
        d.ellipse((a[0] - ra - pad, a[1] - ra - pad, a[0] + ra + pad, a[1] + ra + pad), fill=c)
        d.ellipse((b[0] - rb - pad, b[1] - rb - pad, b[0] + rb + pad, b[1] + rb + pad), fill=c)


def camera(pitch, yaw, roll):
    """先转 yaw，再压 pitch（正的是镜头在下面往上看），最后歪 roll。"""
    a, b, c = math.radians(pitch), math.radians(yaw), math.radians(roll)
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(a), math.sin(a)], [0, -math.sin(a), math.cos(a)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Rz @ Rx @ Ry


def _head(d, px, u, R, c, up, fc, rt):
    """头：高一、宽 0.78 的卵形，脸朝哪边就把眼睛和鼻子画在哪边，背过去的时候画发髻的位置。"""
    # 轮廓：头再怎么转，看上去都差不多是高一、宽 0.8 的卵，横轴取屏幕上跟头轴垂直的方向
    pts = []
    cp = px(c)
    ux = px(c + up * .5) - cp
    n = np.linalg.norm(ux)
    if n < 1e-3:
        ux = np.array([0, -1.0])
        n = 1.0
    ux = ux / n
    sx = np.array([-ux[1], ux[0]])
    H = max(n, .3 * u * SS)        # 头轴冲着镜头的时候，看上去是圆的
    for i in range(48):
        t = 2 * math.pi * i / 48
        pp = cp + ux * math.cos(t) * H + sx * math.sin(t) * .4 * u * SS
        pts.append(tuple(pp))
    d.polygon(pts, fill=COL['head'], outline=(50, 50, 56), width=2 * SS)
    for off, r, col in ((up * .08 + rt * .18 + fc * .34, .05, (30, 30, 34)), (up * .08 - rt * .18 + fc * .34, .05, (30, 30, 34)), (-up * .1 + fc * .42, .04, (150, 90, 70)), (-up * .3 + fc * .3, .045, (190, 60, 60))):
        if (R @ off)[2] > -.02:      # 朝着看的人才看得见
            p = px(c + off)
            rr = r * u * SS
            d.ellipse((p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr), fill=col)
