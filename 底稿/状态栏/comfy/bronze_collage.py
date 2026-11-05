#!/usr/bin/env python3
# 山铜纪两扇一层一层拼（11-05）。用户说最大的问题是姿势、人体和比例，修补修不掉，所以拆开：底图上没有人（plate7、plate_l2），人一张图只画一个，抠好的透明图贴上来，不再过模型。
# 人有两路：m_* 照假人画（bronze_poses.py），照骨盆对位；d_* 不用假人，文字写清镜头和姿势（gpt_bronze.py 的 DYN，照用户发的抽卡立绘的做法），照外框放（PLACE）。用户看了假人说姿势还是怪，张力靠 d_*。
# 索恩薇娅是严格照白厄那张的镜像（t3），腿改过一回（t4）。她和老师（巴尔缇娜、薇瑟兰）用户点名留头一稿的动作，像素从 left3_fixed 来，遮罩拿 plate_l 和 plate_l2 相减。
#   python bronze_collage.py gen     接两扇外侧，写 fix/plate7_out
#   python bronze_collage.py         写 right8.png、left4.png（放大过的，连外侧）
# 要 PIL、numpy、scipy，用 ComfyUI 那个 venv 的 python。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frame_comp as F
from bronze_poses import RIGHT, LEFT, HERO

ROOT = os.path.join(HERE, 'out', '山铜纪_11-04')
FIX = os.path.join(ROOT, 'fix')
K = 1.5
SW, SH = 1049, 1500                 # 两扇原图的尺寸
L_OUT, R_OUT = 300, 220             # 外侧接出去多少，跟 bronze_frame.py 一样
HAND = (473, 476)                   # t3、t4 手的位置
# 排版微调：名字 -> (往右挪, 往下挪, 放大)，单位是原图的像素。先按 bronze_poses.py 的 root、u 放，这里只管最后几下
NUDGE = {
    'vesta': (115, -30, .96), 'brom': (105, -65, .85), 'valdrak': (-60, 8, .92),
}
# 从后往前
RIGHT_ORDER = ['hero', 'd_aes', 'flag', 'd_karn', 'd_lisel', 'vesta', 'brom', 'd_frieren', 'd_hodd', 'd_hob']
LEFT_ORDER = ['d_selephien', 'valdrak', 'd_nephra', 'd_sirentia', 'd_grom', 'd_lysia', 'd_mortus']
# d_* 的位置：名字 -> (外框正中 x, 外框正中 y, 外框高)，原图的像素
PLACE = {
    'd_aes': (150, 900, 540), 'd_karn': (855, 925, 310), 'd_lisel': (1135, 1190, 400), 'd_hodd': (828, 1168, 285),
    'd_hob': (862, 1345, 320), 'd_frieren': (548, 1305, 400),
    'd_selephien': (455, 170, 280), 'd_nephra': (235, 480, 350), 'd_sirentia': (885, 790, 340), 'd_grom': (540, 780, 430),
    'd_lysia': (250, 840, 330), 'd_mortus': (255, 1165, 300),
}
SHADOW = dict(off=(5, 8), blur=7, col=(34, 20, 50), op=.34)


def load(name):
    return Image.open(os.path.join(ROOT, name + '.png')).convert('RGBA')


def clean(im):
    """抠图边上往里收一点，白边不留。"""
    r, g, b, a = F.clean_edges(im).split()
    return Image.merge('RGBA', (r, g, b, a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.6))))


def put(c, im, x, y, shadow=SHADOW):
    """im 贴到 c 的 (x, y)，底下一层纸影。"""
    x, y = int(round(x)), int(round(y))
    if shadow:
        a = Image.new('L', c.size, 0)
        a.paste(im.getchannel('A'), (x + shadow['off'][0], y + shadow['off'][1]))
        a = a.filter(ImageFilter.GaussianBlur(shadow['blur'])).point(lambda v: int(v * shadow['op']))
        col = shadow['col']
        c.alpha_composite(Image.merge('RGBA', (Image.new('L', c.size, col[0]), Image.new('L', c.size, col[1]), Image.new('L', c.size, col[2]), a)))
    layer = Image.new('RGBA', c.size, (0, 0, 0, 0))
    layer.paste(im, (x, y))
    c.alpha_composite(layer)


# 名字 -> (多边形，写在抠出来以前的图的比例上，0 到 1)。里头偏金黄的颜色换成石灰色，手和皮肤不动
RECOLOR = {'d_grom': ([(.70, .0), (1.0, .0), (1.0, .10), (.86, .34), (.70, .60), (.52, .76), (.40, .74), (.52, .50), (.62, .28)],)}


def recolor(im, poly):
    a = np.asarray(im).astype(np.float32).copy()
    h, w = a.shape[:2]
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).polygon([(x * w, y * h) for x, y in poly], fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(3))) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # 金黄的色相四十度上下，他那身古铜色的皮肤二十度上下，按色相分
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    hue = 60 * (g - b) / np.maximum(r - b, 1) * (r >= g) + (r < g) * 60
    gold = np.clip((hue - 27) / 6, 0, 1) * np.clip(((mx - mn) / np.maximum(mx, 1) - .16) / .1, 0, 1)
    k = (m * gold)[..., None]
    lum = (r * .3 + g * .59 + b * .11)[..., None] * 1.02
    grey = np.concatenate([lum * 1.0, lum * .98, lum * .94], axis=2)
    a[..., :3] = a[..., :3] * (1 - k) + grey * k
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def fig_d(c, name, x0=0):
    """文字版的人：照抠出来的外框放。"""
    p = os.path.join(ROOT, name + '.png')
    if not os.path.exists(p):
        print('还没有', name)
        return
    im = load(name)
    if name in RECOLOR:
        im = recolor(im, *RECOLOR[name])
    im = clean(im.crop(im.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()))
    cx, cy, h = PLACE[name]
    s = h * K / im.height
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    put(c, im, x0 + cx * K - im.width / 2, cy * K - im.height / 2)


def fig(c, name, table, x0=0):
    """照骨盆对位贴一个人。x0 是图的 x=0 在 c 上的位置。"""
    p = os.path.join(ROOT, 'm_' + name + '.png')
    if not os.path.exists(p):
        print('还没有', name)
        return
    f = table[name]
    im = clean(load('m_' + name))
    dx, dy, dk = NUDGE.get(name, (0, 0, 1))
    k = im.width / f['canvas'][0]
    s = f['u'] * K * dk / (f['cu'] * k)
    w, h = int(im.width * s), int(im.height * s)
    im = im.resize((w, h), Image.LANCZOS)
    put(c, im, x0 + (f['root'][0] + dx) * K - f['croot'][0] * k * s, (f['root'][1] + dy) * K - f['croot'][1] * k * s)


def wide_plate(name, out_name, out_px, side):
    """底图放大，外侧接上 GPT 接着画的那一条。回 (图, 图的 x=0 在哪)。"""
    body = Image.open(os.path.join(ROOT, name + '.png')).convert('RGB').resize((int(SW * K), int(SH * K)), Image.LANCZOS)
    E = int(out_px * K)
    wide = Image.new('RGB', (body.width + E, body.height))
    p = os.path.join(FIX, out_name + '.png')
    ext = Image.open(p).convert('RGB').resize(body.size, Image.LANCZOS) if os.path.exists(p) else None
    if side == 'right':
        wide.paste(body, (0, 0))
        if ext:
            full = Image.new('RGB', wide.size)
            full.paste(ext, (E, 0))
            al = np.clip((np.arange(wide.width, dtype=np.float32) - (body.width - 40)) / 40, 0, 1)[None, :, None]
            return Image.fromarray(np.uint8(np.asarray(wide) * (1 - al) + np.asarray(full) * al)), 0
        wide.paste(body.crop((body.width - 1, 0, body.width, body.height)).resize((E, body.height)), (body.width, 0))
        return wide, 0
    wide.paste(body, (E, 0))
    if ext:
        full = Image.new('RGB', wide.size)
        full.paste(ext, (0, 0))
        al = np.clip((E + 40 - np.arange(wide.width, dtype=np.float32)) / 40, 0, 1)
        al[ext.width:] = 0
        al = al[None, :, None]
        return Image.fromarray(np.uint8(np.asarray(wide) * (1 - al) + np.asarray(full) * al)), E
    wide.paste(body.crop((0, 0, 1, body.height)).resize((E, body.height)), (0, 0))
    return wide, E


def right():
    base, x0 = wide_plate('plate7', 'plate7_out', R_OUT, 'right')
    c = base.convert('RGBA')
    for n in RIGHT_ORDER:
        if n == 'hero':
            t = clean(load('t4'))
            s, hx, hy = HERO
            dx, dy, dk = NUDGE.get('hero', (0, 0, 1))
            s = s * K * dk
            put(c, t.resize((int(t.width * s), int(t.height * s)), Image.LANCZOS), (hx + dx) * K - HAND[0] * s, (hy + dy) * K - HAND[1] * s)
        elif n == 'flag':
            flag(c)
        elif n.startswith('d_'):
            fig_d(c, n)
        else:
            fig(c, n, RIGHT)
    c.convert('RGB').save(os.path.join(ROOT, 'right8.png'))
    print('right8', c.size)


def flag(c):
    """旗接在薇丝塔的旗杆上：假人的旗杆方向和手的位置都算得出来。flag_cut 里旗杆是斜的，转到一样的斜度。"""
    from mannequin import bones
    if not os.path.exists(os.path.join(ROOT, 'flag_cut.png')):
        return
    f = RIGHT['vesta']
    s, _ = bones(f)
    dx, dy, dk = NUDGE.get('vesta', (0, 0, 1))
    wx = f['root'][0] + dx + s['wrb'][0] * f['u'] * dk
    wy = f['root'][1] + dy - s['wrb'][1] * f['u'] * dk
    pole = np.array(f['props'][1][1], float)[:2]
    pole = pole / np.linalg.norm(pole)
    im = clean(load('flag_cut'))
    # flag_cut 上旗杆顶和拳头（图的像素），量的
    top, fist = np.array(FLAG_TOP), np.array(FLAG_FIST)
    v = top - fist
    ang_src = np.degrees(np.arctan2(v[0], -v[1]))
    ang_dst = np.degrees(np.arctan2(pole[0], pole[1]))
    k = (FLAG_LEN * K) / np.linalg.norm(v)
    w, h = int(im.width * k), int(im.height * k)
    sm = im.resize((w, h), Image.LANCZOS)
    pv = fist * k
    canvas = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0))
    ox, oy = w - pv[0], h - pv[1]
    canvas.paste(sm, (int(ox), int(oy)))
    rot = canvas.rotate(ang_src - ang_dst, resample=Image.BICUBIC, center=(w, h))
    # 旗杆只要手以上，手以下是她自己那一根
    a = np.asarray(rot.getchannel('A')).copy()
    a[h - int(FLAG_CUT * K):, :] = 0
    rot.putalpha(Image.fromarray(a))
    put(c, rot, wx * K - w, wy * K - h)


FLAG_TOP, FLAG_FIST = (628, 690), (536, 1217)     # flag_cut 上旗杆顶、杆底，量的
FLAG_LEN = 410                                    # 手到旗杆顶多长（原图的像素）
FLAG_CUT = 90                                     # 手往上这么长一段用她自己画的那根


def pair_mask():
    """她们俩的遮罩：有她们的 plate_l 减掉没有她们的 plate_l2。头发丝这样也留得住。"""
    from scipy import ndimage
    a = Image.open(os.path.join(ROOT, 'plate_l.png')).convert('RGB').resize((int(SW * K), int(SH * K)), Image.LANCZOS)
    b = Image.open(os.path.join(ROOT, 'plate_l2.png')).convert('RGB').resize(a.size, Image.LANCZOS)
    d = np.abs(np.asarray(a).astype(np.float32) - np.asarray(b).astype(np.float32)).max(axis=2)
    m = np.clip((ndimage.gaussian_filter(d, 1.2) - 16) / 22, 0, 1)
    lab, n = ndimage.label(m > .5)
    size = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    keep = np.isin(lab, np.nonzero(size >= 300)[0] + 1)
    m = m * ndimage.binary_dilation(keep, iterations=3)
    # 只在她们那一带
    poly = Image.new('L', a.size, 0)
    ImageDraw.Draw(poly).polygon([(p[0] * K, p[1] * K) for p in PAIR_POLY], fill=255)
    m = np.minimum(m, np.asarray(poly.filter(ImageFilter.GaussianBlur(6))) / 255.0)
    return Image.fromarray(np.uint8(m * 255))


PAIR_POLY = [(120, 1500), (120, 1400), (210, 1200), (440, 1020), (700, 880), (1049, 880), (1049, 1500)]


def left():
    base_name = 'plate_l2' if os.path.exists(os.path.join(ROOT, 'plate_l2.png')) else 'plate_l'
    base, x0 = wide_plate(base_name, 'left3_out', L_OUT, 'left')
    c = base.convert('RGBA')
    for n in LEFT_ORDER:
        if n.startswith('d_'):
            fig_d(c, n, x0)
        else:
            fig(c, n, LEFT, x0)
    if base_name == 'plate_l2':
        src = Image.open(os.path.join(ROOT, 'left3_fixed.png')).convert('RGB').resize((int(SW * K), int(SH * K)), Image.LANCZOS)
        m = pair_mask()
        m.save(os.path.join(ROOT, 'ref', 'pair_mask.png'))
        layer = Image.new('RGBA', c.size, (0, 0, 0, 0))
        layer.paste(src, (x0, 0))
        al = Image.new('L', c.size, 0)
        al.paste(m, (x0, 0))
        layer.putalpha(al)
        c.alpha_composite(layer)
    c.convert('RGB').save(os.path.join(ROOT, 'left4.png'))
    print('left4', c.size)


def gen():
    """右扇外侧叫 GPT 接着画，超宽屏上不用镜像。图往左挪，空出来的灰条画满，只取那一条。"""
    import gpt_gen
    r = Image.open(os.path.join(ROOT, 'plate7.png')).convert('RGB')
    c = Image.new('RGB', r.size, (205, 205, 205))
    c.paste(r, (-R_OUT, 0))
    p = os.path.join(FIX, 'plate7_out_in.png')
    c.save(p)
    print(gpt_gen.gen(os.path.join(FIX, 'plate7_out'), 'Image 1 is a finished illustration with an empty flat light grey vertical strip on its right side. Repaint image 1 with the same aspect ratio and the same framing, keeping everything that is already painted exactly as it is, in the same place and at the same size, in the same drawing style: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. Fill the grey strip by continuing the picture outward, simply and calmly, with nothing important in it and no people: the flat deep indigo night sky with a few small stars above, the distant pale city with a few lower spires ending, and the wide pale stairs with their even step lines continuing to the right all the way down to the bottom edge. No text, no logo, no frame, no grey left over.', refs=[p]))


if __name__ == '__main__':
    if sys.argv[1:2] == ['gen']:
        gen()
    elif sys.argv[1:2] == ['right']:
        right()
    elif sys.argv[1:2] == ['left']:
        left()
    else:
        right()
        left()
