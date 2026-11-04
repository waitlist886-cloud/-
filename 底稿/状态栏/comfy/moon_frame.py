#!/usr/bin/env python3
# 月银纪四方的拼法（11-04），照 maze1001_frame_pv.py 的路子。要 PIL 和 numpy，用 ComfyUI 那个 venv 的 python。
#   python gpt_moon.py                     出图，写 out/月银纪_11-04/
#   python moon_frame.py crop              裁靠窗那一条要抠的地方，写 crop/
#   python cut_cpu.py <crop> <cut>         抠，写 cut/
#   python moon_frame.py                   拼，写 art/（moon_left、moon_right、moon_top、moon_bottom.webp）
# 尺寸的账跟迷宫纪一样：两扇画布 1400×2000，LINE 是框线；楣 3000×720（样式里 1250×300，框上沿 y=240）；座 6000×677（样式里 2500×282，框下沿离底 341）。
# 一双手不进座，拆成两张（moon_hl、moon_hr），样式里各贴一个屏幕下角，大小跟着视口高（make_css_frame.py 的 --fm-hx）。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import numpy as np
from PIL import Image, ImageFilter
import frame_comp as F
from maze1001_frame_gpt import dim_outer, soft

ROOT = os.path.join(HERE, 'out', '月银纪_11-04')
ART = os.path.join(ROOT, 'art')
W, H, LINE = F.W, F.H, F.LINE
FILL = (20, 27, 40)      # 样式里的 --fm-pl、--fm-pr，超宽屏外侧补的底色
LEFT_UP = 110            # 左扇整张往上提，焚原的头别叫座和手盖住；顶上一成本来就是空天
# 左扇靠窗那一条要留的东西，框是 left.png 的像素（1024×1536）：飞龙的头，白鹿的角，鲸的尾，焚原的头和爪
LEFT_BOXES = [('l_flier', (780, 300, 1024, 410)), ('l_antler', (740, 470, 1024, 720)), ('l_whale', (800, 750, 1024, 880)), ('l_dragon', (640, 1120, 1024, 1536))]
RIGHT_SRC, RIGHT_CUT = 'right2', 'r_full2'
BOT_H = 677               # 座的画布高，样式里 282（--fm-both）
WIN_HALF = 912            # 窗口一半宽的画布像素（样式 380）
HANDS_SRC, HANDS_SPLIT, HANDS_TOP, HANDS_TONE = 'hands2', 1086, 205, (0.86, 0.89, 0.96)   # 两只手指尖相接的那一列；拇指尖上头裁到哪一行；手的颜色
RIGHT_K, RIGHT_TOP = 0.88, 150   # 右扇再缩一点往下放：巨枪尖落到框线一带，别叫顶栏压住；希尔妲的火在座上面。空出来的外侧和上下照边上的画接


def rgba(name):
    return Image.open(os.path.join(ROOT, name + '.png')).convert('RGBA')


def solid(im, low=120, high=225):
    a = np.asarray(im).astype(np.float32)
    a[..., 3] = np.clip((a[..., 3] - low) / (high - low), 0, 1) * 255
    return Image.fromarray(np.uint8(a), 'RGBA')


def tight(im, thr=40):
    return im.crop(im.getchannel('A').point(lambda v: 255 if v > thr else 0).getbbox())


def to_fill(im, side, width=240):
    a = np.asarray(im).astype(np.float32)
    x = np.arange(W, dtype=np.float32)
    k = np.clip(((W - 1 - x) if side == 'right' else x) / width, 0, 1)[None, :, None]
    a[..., :3] = a[..., :3] * k + np.array(FILL, np.float32) * (1 - k)
    return Image.fromarray(np.uint8(a), 'RGBA')


def shifted(im, down):
    c = Image.new(im.mode, im.size)
    c.paste(im, (0, down))
    c.paste(im.crop((0, 0, im.width, 8)).transpose(Image.FLIP_TOP_BOTTOM).resize((im.width, down), Image.BICUBIC), (0, 0))
    return c


def crop():
    os.makedirs(os.path.join(ROOT, 'crop'), exist_ok=True)
    Image.open(os.path.join(ROOT, RIGHT_SRC + '.png')).convert('RGB').save(os.path.join(ROOT, 'crop', RIGHT_CUT + '.png'))
    L = Image.open(os.path.join(ROOT, 'left.png')).convert('RGB')
    for name, box in LEFT_BOXES:
        c = L.crop(box)
        c.resize((c.width * 2, c.height * 2), Image.LANCZOS).save(os.path.join(ROOT, 'crop', name + '.png'))
    print('ok')


def left_panel():
    src = Image.open(os.path.join(ROOT, 'left.png')).convert('RGB')
    k = H / src.height
    s = src.resize((int(src.width * k + 0.5), H), Image.LANCZOS)
    x0 = W - s.width
    full = Image.new('RGB', (W, H))
    full.paste(s.crop((0, 0, x0, H)).transpose(Image.FLIP_LEFT_RIGHT), (0, -LEFT_UP))
    full.paste(s, (x0, -LEFT_UP))
    # 底下空出来的一条拿最下面几行拉开补，这一条在座后头
    full.paste(full.crop((0, H - LEFT_UP - 8, W, H - LEFT_UP)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, LEFT_UP), Image.BICUBIC), (0, H - LEFT_UP))
    a = np.dstack([np.asarray(full).astype(np.float32), np.full((H, W), 255, np.float32)])
    a = dim_outer(a, 'left')
    mk = Image.new('L', src.size, 0)
    for name, box in LEFT_BOXES:
        c = Image.open(os.path.join(ROOT, 'cut', name + '.png')).getchannel('A').resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS)
        mk.paste(c.point(lambda t: 255 if t > 90 else 0), box[:2])
    mk = mk.resize(s.size, Image.LANCZOS)
    full_m = Image.new('L', (W, H), 0)
    full_m.paste(mk, (x0, -LEFT_UP))
    a[:, W - LINE:, 3] = np.asarray(soft(full_m)).astype(np.float32)[:, W - LINE:]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def right_place(im):
    """缩到 RIGHT_K 贴在 x=0、y=RIGHT_TOP；外侧照画接一截镜像，上下拉开最边上几行。"""
    w, h = int(W * RIGHT_K), int(H * RIGHT_K)
    s = im.resize((w, h), Image.LANCZOS)
    c = Image.new(im.mode, (W, H))
    c.paste(s, (0, RIGHT_TOP))
    c.paste(s.crop((w - (W - w), 0, w, h)).transpose(Image.FLIP_LEFT_RIGHT), (w, RIGHT_TOP))
    c.paste(c.crop((0, RIGHT_TOP, W, RIGHT_TOP + 8)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, RIGHT_TOP), Image.BICUBIC), (0, 0))
    end = RIGHT_TOP + h
    if end < H:
        c.paste(c.crop((0, end - 8, W, end)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, H - end), Image.BICUBIC), (0, end))
    return c


def right_cut():
    cut0 = Image.open(os.path.join(ROOT, 'cut', RIGHT_CUT + '.png')).getchannel('A').resize((int(W * RIGHT_K), int(H * RIGHT_K)), Image.LANCZOS)
    cut = Image.new('L', (W, H), 0)
    cut.paste(cut0, (0, RIGHT_TOP))
    return cut


def right_panel():
    r = right_place(Image.open(os.path.join(ROOT, RIGHT_SRC + '.png')).convert('RGB'))
    a = np.dstack([np.asarray(r).astype(np.float32), np.full((H, W), 255, np.float32)])
    a = dim_outer(a, 'right', amount=0.35)
    a[..., :3] *= (0.5 + 0.5 * np.clip((np.arange(H, dtype=np.float32) - 60) / 90, 0, 1))[:, None, None]
    m = F.attached_only(np.asarray(right_cut().point(lambda t: 255 if t > 90 else 0)), LINE, 0, LINE + 1)
    a[:, :LINE, 3] = np.asarray(soft(Image.fromarray(m))).astype(np.float32)[:, :LINE]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def lance_layer(right):
    """右扇靠窗上头那一块（枪、握枪的手、翅膀和马头）单裁一层，压在楣右肩的花边上。跟右扇同一张图同一个比例，样式里照右扇的位置和大小贴（--fm-lance）。
    画里枪尖到图边就断了，顺着两条刃线往窗里补出尖来（★）：x=0 这一列往左，纹路照 x>0 这边翻过来，上下按刃宽收拢。"""
    from scipy import ndimage
    X1, Y0, Y1, E = 280, 120, 620, 100      # 样式里的数跟着这四个：auto 25dvh、top 6dvh、left calc(50% + 窗宽一半)
    SKY = np.array((38, 54, 104), np.float32)
    top = lambda x: 186 + 0.4 * x           # 刃的上下两条线（画布坐标），在 x=-90 相交
    bot = lambda x: 222 + 0.8 * x
    rgb = np.asarray(right.convert('RGB')).astype(np.float32)[:, :X1]
    # 抠图的边偏胖，带一圈天的颜色，压在浅色的花边上会露一道深边：边上那一圈按跟天差多少给透明度
    cut = np.asarray(right_cut())[:, :X1]
    core = ndimage.binary_erosion(cut > 140, iterations=4)
    near = ndimage.binary_dilation(cut > 90, iterations=2)
    al = np.where(core, 1.0, near * np.clip((np.sqrt(((rgb - SKY) ** 2).sum(-1)) - 28) / 40, 0, 1))
    ext = np.zeros((H, E, 3), np.float32)
    ext_al = np.zeros((H, E), np.float32)
    ys = np.arange(H, dtype=np.float32)
    for i in range(E):
        x = i - E + 0.5
        if x < -90:
            continue
        t, b = top(x), bot(x)
        v = (ys - t) / max(b - t, 0.01)
        sx = -x * 0.3
        sy = top(sx) + v * (bot(sx) - top(sx))
        for ch in range(3):
            ext[:, i, ch] = ndimage.map_coordinates(rgb[..., ch], [sy, np.full(H, sx)], order=1, mode='nearest')
        ext_al[:, i] = np.clip(np.minimum(ys - t, b - ys) + 0.5, 0, 1)
    a = np.dstack([np.concatenate([ext, rgb], axis=1), np.concatenate([ext_al, al], axis=1) * 255])
    a[..., 3] = ndimage.gaussian_filter(a[..., 3], 0.7)
    a = a[Y0:Y1]
    a[..., 3] *= np.clip((a.shape[1] - 1 - np.arange(a.shape[1], dtype=np.float32)) / 30, 0, 1)[None, :]
    a[..., 3] *= np.clip((a.shape[0] - 1 - np.arange(a.shape[0], dtype=np.float32)) / 30, 0, 1)[:, None]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def strip(w, h, top=(26, 35, 52), bot=(17, 23, 35), fade=90):
    """楣和座的底：一条暗的天，两头淡掉，跟两扇接上。"""
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    a = np.array(top, np.float32) * (1 - t) + np.array(bot, np.float32) * t
    rng = np.random.default_rng(3)
    a = a * np.ones((h, w, 3), np.float32) + rng.normal(0, 2.2, (h, w, 1))
    al = np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / fade, 0, 1)[None, :] * 255 * np.ones((h, w), np.float32)
    return Image.fromarray(np.uint8(np.clip(np.dstack([a, al]), 0, 255)), 'RGBA')


def top_band():
    TW, TH, Y = 3000, 720, 240
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    c.alpha_composite(strip(2000, Y), ((TW - 2000) // 2, 0))
    src = rgba('tower')
    sw = src.width
    # 左右两道弧上的人（原图 1536×1024，塔在 x=620 到 916）
    arc = tight(src.crop((0, 400, 640, 720)))
    k = 0.46
    aw, ah = int(arc.width * k), int(arc.height * k)
    shadow = dict(shadow_kw=dict(blur=6, offset=(0, 4), opacity=0.5))
    gap = 118     # 弧的里头一端离中线
    y = 244 - int(ah * 0.86)   # 弧底差不多压在框线上
    F.place(c, arc, TW // 2 - gap - aw, y, k, **shadow)
    r_arc = tight(src.crop((sw - 640, 400, sw, 720)))
    F.place(c, r_arc, TW // 2 + gap, y, k, **shadow)
    t = tight(src.crop((620, 30, 916, 960)))
    k = 0.30
    F.place(c, t, (TW - int(t.width * k)) // 2, 340 - int(t.height * k), k, shadow_kw=dict(blur=8, offset=(0, 5), opacity=0.5))
    rib = tight(solid(rgba('ribbon')))
    k = 500 / rib.width
    wide = dict(shadow_kw=dict(blur=12, offset=(0, 8), opacity=0.55))
    F.place(c, rib, 470, 150, k, **wide)
    # 右肩也是同一条花边。楣这一层盖在两扇上，枪会被压住，所以枪另有一层再压回来（lance_layer）
    F.place(c, rib, TW - 470 - int(rib.width * k), 150, k, flip=True, **wide)
    return c


def bottom_band():
    """座只有一条暗的地和远处的篝火。框下沿离屏幕底 142（样式），折回画布 341。
    ground 两头高、当中低，手挪到两角以后框两边露出一块空，所以左右对调：高的地方接到框的两个下角（竖着拉一点，好够到框下沿），接缝在输入框后头，那一段不画；窗口里框下沿以上也不画。"""
    TW, TH = 6000, BOT_H
    Y = TH - 341
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    c.alpha_composite(strip(WIN_HALF * 2, TH - Y), (TW // 2 - WIN_HALF, Y))
    g = rgba('ground')
    g = g.resize((TW, int(g.height * TW / g.width * 1.12)), Image.LANCZOS)
    t = np.roll(np.asarray(g), TW // 2, axis=1).astype(np.float32)
    t[..., 3] *= np.clip((np.abs(np.arange(TW) - TW // 2) - 720) / 72, 0, 1)[None, :]
    g = Image.fromarray(np.uint8(t), 'RGBA')
    c.alpha_composite(g, (0, TH - min(g.height, TH)), (0, max(0, g.height - TH)))
    a = np.asarray(c).astype(np.float32)
    a[:Y, TW // 2 - WIN_HALF:TW // 2 + WIN_HALF, 3] = 0
    a[..., 3] *= np.clip(np.minimum(np.arange(TW), TW - 1 - np.arange(TW)) / 260.0, 0, 1)[None, :]
    return Image.fromarray(np.uint8(a), 'RGBA')


def hand_layers():
    """一双手拆成两只。透明底上带一点碎屑，只留每只手最大的那一块。袖子那一头淡掉，超宽屏上露得出来。"""
    from scipy import ndimage
    a = np.asarray(rgba(HANDS_SRC)).astype(np.float32)
    a[..., :3] *= np.array(HANDS_TONE, np.float32)   # 大理石白太抢眼，往银灰压一点
    out = []
    for x0, x1 in ((0, HANDS_SPLIT), (HANDS_SPLIT, a.shape[1])):
        b = a[HANDS_TOP:, x0:x1].copy()
        lab, n = ndimage.label(b[..., 3] > 40)
        big = 1 + int(np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))))
        b[..., 3] *= ndimage.binary_dilation(lab == big, iterations=3)
        fade = np.clip(np.arange(b.shape[1], dtype=np.float32) / 140, 0, 1)
        b[..., 3] *= fade if x0 == 0 else fade[::-1]
        out.append(Image.fromarray(np.uint8(np.clip(b, 0, 255)), 'RGBA'))
    return out


def write(l, r, t, b, hl, hr):
    os.makedirs(ART, exist_ok=True)
    for n, im in (('left', l), ('right', r), ('top', t.resize((1875, 450), Image.LANCZOS)), ('bottom', b.resize((3750, int(BOT_H * 3750 / 6000)), Image.LANCZOS)), ('hl', hl), ('hr', hr), ('lance', lance_layer(r))):
        F.save_webp(im, os.path.join(ART, 'moon_%s.webp' % n))
    print('ok', [(n, os.path.getsize(os.path.join(ART, n)) // 1024) for n in sorted(os.listdir(ART))], 'KB')


if __name__ == '__main__':
    if sys.argv[1:2] == ['crop']:
        crop()
    else:
        write(to_fill(left_panel(), 'left'), to_fill(right_panel(), 'right'), top_band(), bottom_band(), *hand_layers())
