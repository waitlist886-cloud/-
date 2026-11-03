#!/usr/bin/env python3
# 照用户的 PV 截图画的那一版四方（11-03）。现行右扇是融合版（right_full，图一的姿势和构图、图二的五官和元素神，7:10 铺满画布，双王的头 fix_queens.py 移植）。
# 上一轮的右扇三种：cut 是人物往 PV 收的整张，fig 是拆层的（天空、透明底的人物），first 是 GPT 第一版，外侧都有云挡着。
# 左扇三种意象（a、b、c），靠窗那一条只留抠出来的东西，做法照 maze1001_frame_gpt.py。楣放徽记和两肩的飘带，座是一条横贯全屏的暗色草地，三张图的底连起来。
# 用法写在文件末尾。先跑 gpt_pv.py 出零件、gpt_prepare.py 裁、cut_cpu.py 抠。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import numpy as np
from PIL import Image
import frame_comp as F
from maze1001_frame_gpt import ROOT, VERS, dim_outer, left_panel, right_panel as right_first, soft, star_plate

P = os.path.join(ROOT, 'pv')
W, H, LINE = F.W, F.H, F.LINE
# 顶栏压住靠上那一截（64 像素，768 高的屏幕上约 167 画布像素），人物从这底下开始
FIG_TOP, FIG_H, FIG_X = 170, 1880, 12
SKY_DIM = 0.82
CLOUD_X, CLOUD_Y, CLOUD_H = 790, -60, 2300   # 云图底下约一成贴着图的左边，放大往下压，那一截落到画布外面
FILL = (13, 12, 42)   # 样式里的 --fm-pl、--fm-pr
FIRST_WITH = 'd'      # 右扇另两种配哪张左扇
RIGHT_DOWN = 70       # 融合版右扇往下挪的画布像素


def rgba(name):
    return Image.open(os.path.join(P, name + '.png')).convert('RGBA')


def solid(im, low=120, high=225):
    a = np.asarray(im).astype(np.float32)
    a[..., 3] = np.clip((a[..., 3] - low) / (high - low), 0, 1) * 255
    return Image.fromarray(np.uint8(a), 'RGBA')


def tight(im, thr=40):
    return im.crop(im.getchannel('A').point(lambda v: 255 if v > thr else 0).getbbox())


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    r = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
    x, y = (r.width - w) // 2, (r.height - h) // 2
    return r.crop((x, y, x + w, y + h))


def brush_off(im, side, width, shade=0.0, seed=3):
    """图边裁到人的地方不留直边：照干笔的样子一道一道碎掉，shade 是往外压暗多少。"""
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    rng = np.random.default_rng(seed)
    def blur(v, sigma):
        k = np.exp(-0.5 * (np.arange(-3 * sigma, 3 * sigma + 1) / sigma) ** 2)
        v = np.convolve(v, k / k.sum(), mode='same')
        return (v - v.min()) / (v.max() - v.min())
    streak = 0.6 * blur(rng.random(h), 16) + 0.4 * blur(rng.random(h), 2)   # 一行一个数，上下略糊，就是横着的笔道
    d = np.arange(w, dtype=np.float32) if side == 'left' else (w - 1 - np.arange(w, dtype=np.float32))
    t = d[None, :] / width + rng.normal(0, 0.05, (h, w))
    a[..., 3] *= np.clip((t - streak[:, None] * 0.85) / 0.3, 0, 1)
    if shade:
        a[..., :3] *= (1 - shade * (1 - np.clip(d[None, :] / (width * 2.6), 0, 1)) ** 1.5)[..., None]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def add_cloud(c):
    """云像纸剧场的侧幕，挡在人物外缘前面，压暗一点往后退；窄屏上只露一个角。"""
    cloud = rgba('cloud_wall')
    k = CLOUD_H / cloud.height
    F.place(c, cloud, CLOUD_X, CLOUD_Y, k, tint_to=(24, 20, 70), tint_amt=0.30, shadow_kw=dict(blur=24, offset=(-10, 10), opacity=0.45))


def right_cut():
    """人物往 PV 那种大块剪纸收的那一张，整张不透明：靠窗那一条只留抠出来的，外侧接细星，云挡在外缘前面。"""
    r = brush_off(rgba('right_pv').resize((1000, 2000), Image.LANCZOS), 'right', 80, shade=0.3)
    c = star_plate().convert('RGBA')
    c.alpha_composite(r)
    a = dim_outer(np.asarray(c).astype(np.float32), 'right', amount=0.35)
    a[..., :3] *= (0.42 + 0.58 * np.clip((np.arange(H, dtype=np.float32) - 110) / 130, 0, 1))[:, None, None]
    cut = Image.open(os.path.join(P, 'cut', 'r_pv.png')).getchannel('A').resize((1000, 2000), Image.LANCZOS)
    a[:, :LINE, 3] = np.asarray(soft(cut.point(lambda t: 255 if t > 90 else 0))).astype(np.float32)[:, :LINE]
    c = Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')
    add_cloud(c)
    return c


def shifted(im, down):
    """整张往下挪，上面空出来的一条拿最上面几行拉开补，这一条在平台顶栏底下。"""
    c = Image.new(im.mode, im.size)
    c.paste(im, (0, down))
    c.paste(im.crop((0, 0, im.width, 8)).transpose(Image.FLIP_TOP_BOTTOM).resize((im.width, down), Image.BICUBIC), (0, 0))
    return c


def right_full(name, rcut):
    """融合版：图是 7:10，正好铺满画布，外侧也是画，不用再接星空、碎边和云。靠窗那一条只留连着人物的；整张下移，矮屏上石神的头别叫顶栏压住；顶上压暗，大圆别从平台顶栏的毛玻璃后头透出一团亮。"""
    r = shifted(Image.open(os.path.join(P, name + '.png')).convert('RGB').resize((W, H), Image.LANCZOS), RIGHT_DOWN)
    a = np.dstack([np.asarray(r).astype(np.float32), np.full((H, W), 255, np.float32)])
    a = dim_outer(a, 'right', amount=0.35)
    a[..., :3] *= (0.25 + 0.75 * np.clip((np.arange(H, dtype=np.float32) - 110) / 130, 0, 1))[:, None, None]
    cut = shifted(Image.open(os.path.join(P, 'cut', rcut + '.png')).getchannel('A').resize((W, H), Image.LANCZOS), RIGHT_DOWN)
    m = F.attached_only(np.asarray(cut.point(lambda t: 255 if t > 90 else 0)), LINE, 0, LINE + 1)
    a[:, :LINE, 3] = np.asarray(soft(Image.fromarray(m))).astype(np.float32)[:, :LINE]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def right_layers():
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sky = cover(Image.open(os.path.join(P, 'sky_right.png')).convert('RGB').transpose(Image.FLIP_LEFT_RIGHT), W - LINE, H)
    sky = Image.fromarray(np.uint8(np.asarray(sky).astype(np.float32) * SKY_DIM))
    c.paste(sky, (LINE, 0))
    c = Image.fromarray(np.uint8(np.clip(dim_outer(np.asarray(c).astype(np.float32), 'right', amount=0.35), 0, 255)), 'RGBA')
    fig = tight(rgba('right_fig'))
    k = FIG_H / fig.height
    fig = fig.resize((int(fig.width * k), FIG_H), Image.LANCZOS)
    # 外侧压暗再碎掉，人从暗里走出来，光从窗口那边来；靠窗那边只有披风贴着图边，碎一点就够
    fig = brush_off(brush_off(fig, 'right', 150, shade=0.6), 'left', 44, seed=5)
    F.place(c, fig, FIG_X, FIG_TOP, 1.0, shadow_kw=dict(blur=20, offset=(8, 14), opacity=0.5))
    add_cloud(c)
    return c


def to_fill(im, side, width=240):
    """最外侧渐到底色。超宽屏上图不够宽，外面是样式补的底色，这样接得上。"""
    a = np.asarray(im).astype(np.float32)
    x = np.arange(W, dtype=np.float32)
    k = np.clip(((W - 1 - x) if side == 'right' else x) / width, 0, 1)[None, :, None]
    a[..., :3] = a[..., :3] * k + np.array(FILL, np.float32) * (1 - k)
    return Image.fromarray(np.uint8(a), 'RGBA')


def strip(w, h):
    """楣和座的底：一条天空，两头淡掉，跟两扇接上。"""
    a = np.dstack([np.asarray(cover(Image.open(os.path.join(P, 'sky_right.png')).convert('RGB'), w, h)).astype(np.float32) * SKY_DIM, np.full((h, w), 255, np.float32)])
    a[..., 3] *= np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / 90.0, 0, 1)[None, :]
    return Image.fromarray(np.uint8(a), 'RGBA')


def top_band():
    TW, TH, Y = 3000, 720, 240   # 样式里缩到 1250×300；框上沿在画布的 y=240，窗口左上角 x=588
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    c.alpha_composite(strip(2000, Y), ((TW - 2000) // 2, 0))
    wide = dict(shadow_kw=dict(blur=12, offset=(0, 8), opacity=0.55))
    crest = tight(rgba('orn_crest'))
    k = 720 / crest.width
    F.place(c, crest, (TW - int(crest.width * k)) // 2, 225 - int(crest.height * k) // 2, k, shadow_kw=dict(blur=8, offset=(0, 5), opacity=0.5))
    rib = tight(solid(rgba('orn_ribbon')))
    k = 500 / rib.width
    F.place(c, rib, 470, 150, k, **wide)
    F.place(c, rib.transpose(Image.FLIP_LEFT_RIGHT), TW - 470 - int(rib.width * k), 150, k, **wide)
    return c


def bottom_band():
    TW, TH, Y = 6000, 677, 336   # 样式里缩到 2500×282，横贯全屏；框下沿在画布的 y=336。真页面上输入栏那一块顶到离屏幕底 131，框下沿离屏幕底 142，折回画布是 341
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    c.alpha_composite(strip(2000, TH - Y), ((TW - 2000) // 2, Y))
    m = rgba('orn_meadow')
    mw = m.width
    k = 0.72
    def piece(x0, x1, scale=k, fade=True):
        p = m.crop((int(mw * x0), 0, int(mw * x1), m.height))
        p = F.fade_side(p, 'right', 50)
        if fade:
            p = F.fade_side(p, 'left', 50)
        return p.resize((int(p.width * scale), int(p.height * scale)), Image.LANCZOS)
    low = piece(0.30, 0.70)
    half = Image.new('RGBA', (TW // 2, TH), (0, 0, 0, 0))
    def put(p, x):
        half.alpha_composite(p, (max(x, 0), max(TH - p.height, 0)), (max(-x, 0), max(p.height - TH, 0)))
    def bush(x, scale):
        # 素材的高处贴着图边，有一道切边。两张背靠背，切边藏在中间，高的一丛在 x
        r = piece(0, 0.36, scale, fade=False)
        l = piece(0, 0.36, scale * 0.86, fade=False).transpose(Image.FLIP_LEFT_RIGHT)
        put(l, x - l.width + 24)
        put(r, x - 24)
    for x in range(-200, TW // 2, low.width - 50):
        put(low, x)
    bush(760, 0.60)
    # 窗口左下角在 x=2088。楣和座是固定像素，人跟着屏幕高度缩，这一丛不能高：768 高的屏幕上再高就盖住索恩薇娅的脸
    bush(2020, 0.52)
    c.alpha_composite(half, (0, 0))
    c.alpha_composite(half.transpose(Image.FLIP_LEFT_RIGHT), (TW // 2, 0))
    # 两头淡掉，超宽屏上不留一刀直边
    a = np.asarray(c).astype(np.float32)
    ramp = np.clip(np.minimum(np.arange(TW), TW - 1 - np.arange(TW)) / 260.0, 0, 1)[None, :]
    a[..., 3] *= ramp
    return Image.fromarray(np.uint8(a), 'RGBA')


def write(name, l, r, t, b):
    ART = os.path.join(ROOT, 'art_' + name)
    os.makedirs(ART, exist_ok=True)
    for n, im in (('left', l), ('right', r), ('top', t), ('bottom', b)):
        F.save_webp(im, os.path.join(ART, 'maze_%s.webp' % n))
    print('ok', name, [os.path.getsize(os.path.join(ART, n)) // 1024 for n in sorted(os.listdir(ART))], 'KB')


if __name__ == '__main__':
    # 现行：右扇 right_f7（融合版换上用户选的双王的头、照底卡修过四位七神，fix_gods.py 出的），左扇 ab（甲乙融合）。python maze1001_frame_pv.py [右扇名 抠图名] 写 art_fu_ab。
    # 上一轮那几种（art_pv_*、art_fig_d、art_first_d）：python maze1001_frame_pv.py old a b d
    if sys.argv[1:2] == ['old']:
        which = sys.argv[2:] or ['a', 'b', 'd']
        r, t, b = to_fill(right_cut(), 'right'), top_band(), bottom_band()
        for x in which:
            l = to_fill(left_panel(VERS['pv_' + x]), 'left')
            write('pv_' + x, l, r, t, b)
            if x == FIRST_WITH:   # 右扇另两种，只配这一张左扇
                write('fig_' + x, l, to_fill(right_layers(), 'right'), t, b)
                write('first_' + x, l, to_fill(right_first(VERS['gpt']), 'right'), t, b)
    else:
        name, rcut = (sys.argv[1:3] + ['right_f7', 'r_f7'][len(sys.argv[1:3]):])
        r, t, b = to_fill(right_full(name, rcut), 'right'), top_band(), bottom_band()
        r.save(os.path.join(ROOT, '_fu_right.png'))
        t.save(os.path.join(ROOT, '_pv_top.png'))
        b.save(os.path.join(ROOT, '_pv_bottom.png'))
        for x in ('ab',):   # 用户 11-03 定了甲乙融合；甲、乙的来源还在 VERS 里，要看把 'a'、'b' 加回来
            l = to_fill(left_panel(VERS['pv_' + x]), 'left')
            l.save(os.path.join(ROOT, '_fu_left_%s.png' % x))
            write('fu_' + x, l, r, t, b)
