#!/usr/bin/env python3
# 山铜纪四方的拼法（11-04），照 strife_frame.py 的路子。要 PIL、numpy、scipy，用 ComfyUI 那个 venv 的 python。
#   python gpt_bronze.py [名字…]                 出图，写 out/山铜纪_11-04/
#   python bronze_frame.py gen                   两扇外侧接着画，写 fix/left_out、fix/right_out
#   python bronze_frame.py fix [名字…]            局部重画（王座、杖头、棋子顶、莫尔图斯的脸），写 fix/
#   python bronze_frame.py ruin                  座外头那两段接着画，写 fix/ruin_lo、fix/ruin_ro
#   python bronze_frame.py                       拼，写 art/（bronze_left、bronze_right、bronze_top、bronze_bottom.webp）
# 尺寸的账跟迷宫纪一样：两扇画布 1400×2000，LINE 是框线；楣 3000×720（样式里 1250×300，框上沿 y=240）；座 6000×677（样式里 2500×282，框下沿离底 341）。
# 这一纪两扇不对打，各是各的群像：人不朝对面举东西，只有右扇那一道剑光和左扇散开的灰和光伸进窗里。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frame_comp as F
from maze1001_frame_gpt import dim_outer, soft

ROOT = os.path.join(HERE, 'out', '山铜纪_11-04')
ART = os.path.join(ROOT, 'art')
FIX = os.path.join(ROOT, 'fix')
W, H, LINE = F.W, F.H, F.LINE
BOT_H, WIN_HALF = 677, 912
RUIN_SHIFT, RUIN_KEEP = 288, 0.34      # 座左半边往外让多少（样式 120 像素），外头那两段的图上留多少里头那一段
RUIN_R = 'ruin_r_b' if os.path.exists(os.path.join(HERE, 'out', '山铜纪_11-04', 'ruin_r_b.png')) else 'ruin_r'
K = 1.5                                # 放大 1.5 倍再缩到画布上，细节留得住
LEFT_SRC, RIGHT_SRC = 'left', 'right'
FILL_L, FILL_R = (17, 18, 22), (30, 24, 52)   # 样式里的 --fm-pl、--fm-pr，超宽屏外侧补的底色
L_OUT, R_OUT = 300, 220                # 两扇外侧接出去多少（图的像素）
L_SCALE, L_TOP, L_IN = 1.08, 50, 70    # 左扇：图的 1 像素是画布多少，图顶在画布哪一行，图往外让多少（薇瑟兰的肩膀不叫框线切掉）。她的手和那枚棋要露在座上头
R_SCALE, R_TOP, R_X = 1.15, 44, 62     # 右扇：图的 x=0 在画布 R_X，王座不叫框线切掉


# 局部重画：一块一张，裁下来放大叫 GPT 只改这一样，贴回去只贴多边形里那一块，边上淡开。多边形写在图的像素上。
LOCAL = 'Image 1 is a crop from a finished illustration: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. Repaint image 1 with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size, in the same drawing style and colours, except for this one change. '
LOCAL_END = ' No text, no logo, no frame, no crescents, no moon phases.'
FIXES = {
    'right': [
        # 用户原话斩落王座。头一稿画成了一座教堂的门面，看不出是椅子
        dict(n='throne', box=(0, 40, 400, 500), poly=[(0, 62), (300, 62), (330, 150), (250, 230), (240, 330), (150, 400), (150, 440), (0, 440)], prompt=(
            'Replace the gothic cathedral building at the upper left with an immense throne, unmistakably a chair, as tall as a cathedral, standing at the head of the white stairs and seen from the front and a little to the side: a broad empty seat of white stone with pale gold inlay, two heavy armrests, a stepped white dais under it, and a very tall pointed gothic back rising above the seat. '
            'The line of light passes straight through the tall back: everything above the line has been sheared off cleanly and is sliding away along the cut, with pieces of white stone falling. '
            'Keep exactly as they are: the sword, the hand holding it and the sleeve, the two falling halves of the crown, the line of light itself, the deep indigo night sky above the line, the white angel statue and the white stairs with the small people at the bottom.')),
        # 这个世界不写月相：杖头改开口的金环，跟纷争纪那一张一样
        dict(n='staff', box=(600, 990, 790, 1180), poly=[(628, 1000), (770, 1000), (770, 1120), (690, 1160), (628, 1120)], prompt=(
            'Change only the head of the red staff in the middle: remove the gold crescent and the round red jewel. Its gold head is now an open ring of plain gold, a nearly closed circle with a small gap at the top, not a crescent, gripping a cloudy old crystal with a faint reddish glow at its centre. Keep the red cord, the gold collar below the head, the red shaft and everything behind it exactly as they are.')),
    ],
    'left': [
        # 棋子顶上的十字这个世界没有，换一圈小冠
        dict(n='king', box=(270, 1290, 430, 1490), poly=[(320, 1316), (372, 1316), (376, 1375), (316, 1375)], prompt=(
            'Change only the very top of the black chess king held by the gloved fingers: remove the cross finial. In its place the piece is topped by a small plain crown of dull gold orichalcum with five low points. Keep the gloved hand, the rest of the piece, the board and everything else exactly as they are.')),
        # 莫尔图斯照底卡是活人，只有左颌露一截水晶似的骨头，不是半张骷髅
        dict(n='mortus', box=(240, 840, 420, 1020), poly=[(278, 868), (376, 868), (384, 930), (362, 972), (318, 982), (284, 950)], prompt=(
            'Change only the face of the thin man with white hair: he is not a skeleton, there are no bare teeth and no skull. He is a living man who looks about thirty-five, gaunt and handsome, with skin so pale it is almost translucent, a straight nose, a closed thin mouth and a calm cold ice-blue eye behind a gold-wire crystal monocle. Only one small sliver of clear white crystal-like bone shows along the edge of his jaw. Keep his white hair, his monocle chain, his hand and bell, his collar and everything else exactly as they are.')),
    ],
}


def gen_fix(names=None):
    import gpt_gen
    os.makedirs(FIX, exist_ok=True)
    for side, items in FIXES.items():
        src = Image.open(os.path.join(ROOT, side + '.png')).convert('RGB')
        for f in items:
            if names and f['n'] not in names:
                continue
            p = os.path.join(FIX, f['n'] + '_in.png')
            c = src.crop(f['box'])
            k = 1024 / max(c.size)
            c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS).save(p)
            print(gpt_gen.gen(os.path.join(FIX, f['n']), LOCAL + f['prompt'] + LOCAL_END, refs=[p]), flush=True)


def big(name):
    src = Image.open(os.path.join(ROOT, name + '.png')).convert('RGB')
    im = src.resize((int(src.width * K), int(src.height * K)), Image.LANCZOS)
    for f in FIXES.get(name, ()):
        p = os.path.join(FIX, f['n'] + '.png')
        if not os.path.exists(p):
            continue
        x0, y0, x1, y1 = f['box']
        new = Image.open(p).convert('RGB').resize((int((x1 - x0) * K), int((y1 - y0) * K)), Image.LANCZOS)
        m = Image.new('L', im.size, 0)
        ImageDraw.Draw(m).polygon([(x * K, y * K) for x, y in f['poly']], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(4))
        layer = im.copy()
        layer.paste(new, (int(x0 * K), int(y0 * K)))
        im = Image.composite(layer, im, m)
    return im


def gen():
    """两扇外侧叫 GPT 接着画，超宽屏上不用镜像。图挪开，空出来的灰条画满，只取那一条。"""
    import gpt_gen
    os.makedirs(FIX, exist_ok=True)
    OUTER = ('Image 1 is a finished illustration with an empty flat light grey vertical strip on one side. Repaint image 1 with the same aspect ratio and the same framing, keeping everything that is already painted exactly as it is, in the same place and at the same size, in the same drawing style: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. '
             'Fill the grey strip by continuing the picture outward, simply and calmly, with nothing important in it and no new faces: %s No text, no logo, no frame, no grey left over.')
    l = Image.open(os.path.join(ROOT, LEFT_SRC + '.png')).convert('RGB')
    c = Image.new('RGB', l.size, (205, 205, 205))
    c.paste(l, (L_OUT, 0))
    p = os.path.join(FIX, 'left_out_in.png')
    c.save(p)
    print(gpt_gen.gen(os.path.join(FIX, 'left_out'), OUTER % 'the charcoal sky and the grey rain, the flat layers of ash-grey mist, the chains of the giant and the black and white chessboard continuing to the left, fading darker toward the left edge.', refs=[p]))
    r = Image.open(os.path.join(ROOT, RIGHT_SRC + '.png')).convert('RGB')
    c = Image.new('RGB', r.size, (205, 205, 205))
    c.paste(r, (-R_OUT, 0))
    p = os.path.join(FIX, 'right_out_in.png')
    c.save(p)
    print(gpt_gen.gen(os.path.join(FIX, 'right_out'), OUTER % 'the indigo night sky with a few small stars above, the line of light continuing straight on to the edge, the rose and gold dawn below it with soft hills, the pale spires and white stairs continuing to the right, the long pale cloth ending in soft points, then calm dark rose ground.', refs=[p]))


def gen_ruin():
    """座外头那两段。里头那一段靠外的 RUIN_KEEP 留在图上，空出来的地方叫 GPT 接着画，只取新画的那一段，接缝淡开。"""
    import gpt_gen
    os.makedirs(FIX, exist_ok=True)
    END = ('Keep the fully transparent background: everything above the ruins stays fully transparent, with no sky and no background. Fine grey rain falls in straight slanted lines with flakes of pale ash, the ground is wet black. No people. No crosses. '
           'The foot of the strip sinks into a flat band of dark ash-grey mist at the bottom edge of the picture, the same as in the painted part. Same drawing style and colours: flat cut-paper shapes with fine parallel hatching, matte. No text, no logo, no frame.')
    l = Image.open(os.path.join(ROOT, 'ruin_l.png')).convert('RGBA')
    k = int(l.width * RUIN_KEEP)
    c = Image.new('RGBA', l.size, (0, 0, 0, 0))
    c.alpha_composite(l.crop((0, 0, k, l.height)), (l.width - k, 0))
    p = os.path.join(FIX, 'ruin_lo_in.png')
    c.save(p)
    print(gpt_gen.gen(os.path.join(FIX, 'ruin_lo'), 'Image 1 is a very wide strip of a finished picture on a transparent background. Its right part is painted and its left part is still empty. Repaint it with the same aspect ratio and the same framing, keeping the painted part exactly as it is, in the same place and at the same size, and continue the picture to the left so that everything joins perfectly with no seam: the same colossal rampart of pale white stone with tall blind arches and square buttresses, the same height where it meets the painted part, runs on to the left across the whole empty part, broken in two places with slopes of fallen white blocks and charred beams at its foot, a few small pale flowers. ' + END, refs=[p]))
    r = Image.open(os.path.join(ROOT, RUIN_R + '.png')).convert('RGBA')
    k = int(r.width * RUIN_KEEP)
    c = Image.new('RGBA', r.size, (0, 0, 0, 0))
    c.alpha_composite(r.crop((r.width - k, 0, r.width, r.height)), (0, 0))
    p = os.path.join(FIX, 'ruin_ro_in.png')
    c.save(p)
    print(gpt_gen.gen(os.path.join(FIX, 'ruin_ro'), 'Image 1 is a very wide strip of a finished picture on a transparent background. Its left part is painted and its right part is still empty. Repaint it with the same aspect ratio and the same framing, keeping the painted part exactly as it is, in the same place and at the same size, and continue the picture to the right so that everything joins perfectly with no seam: the same dark wet slope, at the same height where it meets the painted part, runs on to the right across the whole empty part and rises a little: black burnt fields in long wet furrows, a low broken field wall of white stone, a few charred tree stumps, more very small graves each marked with one plain thin wooden stake with no crossbar, a few thin green shoots and small white bell-shaped flowers. ' + END, refs=[p]))


def outer_left():
    """左扇接上外侧。回放大过的图，x=0 是图的 x=-L_OUT。"""
    body = big(LEFT_SRC)
    E = int(L_OUT * K)
    out = Image.new('RGB', (body.width + E, body.height))
    out.paste(body, (E, 0))
    p = os.path.join(FIX, 'left_out.png')
    if os.path.exists(p):
        ext = Image.open(p).convert('RGB').resize((body.width, body.height), Image.LANCZOS)
        al = np.clip((E + 40 - np.arange(out.width, dtype=np.float32)) / 40, 0, 1)
        al[ext.width:] = 0
        full = Image.new('RGB', out.size)
        full.paste(ext, (0, 0))
        a = np.asarray(out).astype(np.float32) * (1 - al[None, :, None]) + np.asarray(full).astype(np.float32) * al[None, :, None]
        return Image.fromarray(np.uint8(np.clip(a, 0, 255)))
    out.paste(body.crop((0, 0, 1, body.height)).resize((E, body.height)), (0, 0))
    return out


def outer_right():
    """右扇接上外侧。回放大过的图，x=0 是图的 x=0。"""
    body = big(RIGHT_SRC)
    O = int(R_OUT * K)
    wide = Image.new('RGB', (body.width + O, body.height))
    wide.paste(body, (0, 0))
    p = os.path.join(FIX, 'right_out.png')
    if os.path.exists(p):
        ro = Image.open(p).convert('RGB').resize((body.width, body.height), Image.LANCZOS)
        full = Image.new('RGB', wide.size)
        full.paste(ro, (O, 0))
        x = np.arange(wide.width, dtype=np.float32)
        al = np.clip((x - (body.width - 40)) / 40, 0, 1)[None, :, None]
        b = np.asarray(wide).astype(np.float32) * (1 - al) + np.asarray(full).astype(np.float32) * al
        return Image.fromarray(np.uint8(np.clip(b, 0, 255)))
    wide.paste(body.crop((body.width - 1, 0, body.width, body.height)).resize((O, body.height)), (body.width, 0))
    return wide


def fill_rows(c, top, end, mist=(34, 35, 40)):
    """图上下空出来的地方。上头拿边上几行拉满，在顶栏底下看不见；下头不拉（拉出来是一道一道的竖纹），末一行糊开，淡进灰雨的雾里，座盖在上面。"""
    c.paste(c.crop((0, top, W, top + 8)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, top), Image.BICUBIC), (0, 0))
    if end >= H:
        return
    a = np.asarray(c).astype(np.float32).copy()
    row = a[end - 10:end].mean(axis=0)
    from scipy import ndimage
    row = ndimage.gaussian_filter1d(row, 90, axis=0, mode='nearest')
    t = np.clip((np.arange(H - end + 60, dtype=np.float32)) / 150, 0, 1)[:, None, None]
    fill = row[None, ...] * (1 - t) + np.array(mist, np.float32) * t
    # 接缝往上淡 60 行，末几行的人和衣服淡进雾里
    fade = np.clip(np.arange(60, dtype=np.float32) / 60, 0, 1)[:, None, None]
    a[end - 60:end] = a[end - 60:end] * (1 - fade) + fill[:60] * fade
    a[end:] = fill[60:]
    c.paste(Image.fromarray(np.uint8(np.clip(a, 0, 255))), (0, 0))


def top_dark(a):
    a[..., :3] *= (0.55 + 0.45 * np.clip((np.arange(H, dtype=np.float32) - 60) / 90, 0, 1))[:, None, None]


def left_panel():
    src = outer_left()
    w, h = int((1049 + L_OUT) * L_SCALE), int(1500 * L_SCALE)
    s = src.resize((w, h), Image.LANCZOS)
    x0 = W - w - L_IN         # 负的，外侧多出来的裁掉
    c = Image.new('RGB', (W, H))
    c.paste(s, (x0, L_TOP))
    fill_rows(c, L_TOP, L_TOP + h)
    a = np.dstack([np.asarray(c).astype(np.float32), np.full((H, W), 255, np.float32)])
    a = dim_outer(a, 'left', amount=0.45)
    top_dark(a)
    # 伸进窗里的只有她身上散开的光：几十片小金屑，从薇瑟兰的肩膀往窗里飘，越往里越少。图上那些碎片抠出来糊成一片，这里一片一片画
    a[:, W - LINE:, 3] = 0
    rng = np.random.default_rng(11)
    fl = Image.new('RGBA', (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(fl)
    for _ in range(46):
        x = W - LINE - 6 + rng.power(1.0) * 0 + rng.exponential(26)
        if x > W - 8:
            continue
        y = rng.uniform(L_TOP + 800 * L_SCALE, L_TOP + 1330 * L_SCALE)
        r = rng.uniform(2.2, 6.5) * (1 - (x - (W - LINE)) / 150)
        t = rng.uniform(0, np.pi)
        pts = []
        for q, rr in ((0, r), (np.pi / 2, r * 0.42), (np.pi, r * 0.8), (np.pi * 1.5, r * 0.42)):
            pts.append((2 * (x + np.cos(t + q) * rr), 2 * (y + np.sin(t + q) * rr)))
        col = (246, 226, 170) if rng.random() < 0.7 else (238, 232, 216)
        d.polygon(pts, fill=col + (int(rng.uniform(170, 245)),))
    fl = fl.resize((W, H), Image.LANCZOS)
    glow = fl.filter(ImageFilter.GaussianBlur(3))
    fa = np.asarray(fl).astype(np.float32)
    ga = np.asarray(glow).astype(np.float32)
    al = np.maximum(fa[..., 3], ga[..., 3] * 0.8)
    pre = (fa[..., :3] * fa[..., 3:4] + ga[..., :3] * ga[..., 3:4]) / np.maximum(fa[..., 3:4] + ga[..., 3:4], 1)
    a[:, W - LINE:, :3] = pre[:, W - LINE:]
    a[:, W - LINE:, 3] = al[:, W - LINE:]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def right_panel():
    src = outer_right()
    w, h = int((1049 + R_OUT) * R_SCALE), int(1500 * R_SCALE)
    s = src.resize((w, h), Image.LANCZOS)
    c = Image.new('RGB', (W, H))
    c.paste(s.crop((0, 0, W - R_X, h)), (R_X, R_TOP))
    # 图左边让出来的那一条（窗里，看不见）
    c.paste(s.crop((0, 0, 1, h)).resize((R_X, h)), (0, R_TOP))
    fill_rows(c, R_TOP, R_TOP + h)
    a = np.dstack([np.asarray(c).astype(np.float32), np.full((H, W), 255, np.float32)])
    a = dim_outer(a, 'right', amount=0.4)
    top_dark(a)
    # 伸进窗里的只有那一道剑光和剑尖：多边形写在图的像素上（x 可以是负的，剑光顺着往窗里走）
    def P(pts):
        return [(R_X + x * R_SCALE, R_TOP + y * R_SCALE) for x, y in pts]
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    d.polygon(P([(-60, 62), (60, 108), (60, 132), (-60, 92)]), fill=255)
    al = np.asarray(soft(m, blur=2)).astype(np.float32).copy()
    a[:, :LINE, 3] = al[:, :LINE]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def rgba(name, sub=''):
    return Image.open(os.path.join(ROOT, sub, name + '.png')).convert('RGBA')


def tight(im, thr=40):
    return im.crop(im.getchannel('A').point(lambda v: 255 if v > thr else 0).getbbox())


def strip(w, h, top=(18, 18, 22), bot=(13, 13, 16), fade=90):
    """楣的底：一条暗的天，两头淡掉，跟两扇接上。"""
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    a = np.array(top, np.float32) * (1 - t) + np.array(bot, np.float32) * t
    rng = np.random.default_rng(5)
    a = a * np.ones((h, w, 3), np.float32) + rng.normal(0, 2.0, (h, w, 1))
    al = np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / fade, 0, 1)[None, :] * 255 * np.ones((h, w), np.float32)
    return Image.fromarray(np.uint8(np.clip(np.dstack([a, al]), 0, 255)), 'RGBA')


def top_band():
    """楣：恶神的爪和大迷宫的虚影。两个肩膀上爪子扣住框角，一条爪和虚影的线沿框上沿走，正中爪子攥着一座倒悬的螺旋塔。"""
    TW, TH, Y = 3000, 720, 240
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    c.alpha_composite(strip(2000, Y), ((TW - 2000) // 2, 0))
    shadow = dict(shadow_kw=dict(blur=10, offset=(0, 6), opacity=0.6))
    if os.path.exists(os.path.join(ROOT, 'strip.png')):
        st = tight(rgba('strip'))
        k = 1500 / st.width
        F.place(c, st, (TW - 1500) // 2, Y - int(st.height * k * 0.56), k, **shadow)
    if os.path.exists(os.path.join(ROOT, 'corner_l.png')):
        co = tight(rgba('corner_l'))
        k = 520 / co.width
        F.place(c, co, 470, 112, k, **shadow)
        cr_ = tight(rgba('corner_r'))
        k_r = 520 / cr_.width
        F.place(c, cr_, TW - 470 - 520, 112, k_r, **shadow)
    if os.path.exists(os.path.join(ROOT, 'crest.png')):
        cr = tight(rgba('crest'))
        k = 196 / cr.height                 # 上头的爪藏到顶栏底下，塔尖只露到窗口最上头那一道小纹
        F.place(c, cr, (TW - int(cr.width * k)) // 2, 110, k, **shadow)
    return c


def bottom_band():
    """座：灰雨城的废墟。左半边南门和门洞，右半边南坡的碑和书屋，接缝在输入框后头。框下沿离屏幕底 148（样式），折回画布 341。
    窗口那一列框下沿以上不画，框下沿以下压暗，输入框和预设那一排看得清。不翻转。"""
    TW, TH, Y = 6000, BOT_H, BOT_H - 341
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))

    def put(name, right=None, left=None):
        p = os.path.join(ROOT, name + '.png')
        if not os.path.exists(p):
            return None
        im = Image.open(p).convert('RGBA')
        k = TH * 1.0 / im.height
        im = im.resize((int(im.width * k), TH), Image.LANCZOS)
        x = left if left is not None else right - im.width
        c.alpha_composite(im, (max(x, 0), 0), (max(-x, 0), 0, min(im.width, TW - x), TH))
        return x, x + im.width
    # 左边往外让 RUIN_SHIFT：门洞和塔楼不压她的手和那枚棋。外头那两段的图有 RUIN_KEEP 是里头那一段（接着画的），对齐放，只取新画的，接缝淡开，不翻转
    def blend(name, x, fade_at, side):
        p = os.path.join(FIX, name + '.png')
        if not os.path.exists(p):
            return
        im = Image.open(p).convert('RGBA')
        k = TH * 1.0 / im.height
        im = im.resize((int(im.width * k), TH), Image.LANCZOS)
        a = np.asarray(im).astype(np.float32).copy()
        xs = np.arange(im.width, dtype=np.float32)
        ramp = np.clip((fade_at - xs) / 70, 0, 1) if side == 'left' else np.clip((xs - fade_at) / 70, 0, 1)
        a[..., 3] *= ramp[None, :]
        c.alpha_composite(Image.fromarray(np.uint8(a), 'RGBA'), (max(x, 0), 0), (max(-x, 0), 0, min(im.width, TW - x), TH))
    x0, x1 = put('ruin_l', right=TW // 2 - RUIN_SHIFT)
    wide = x1 - x0
    keep = int(wide * RUIN_KEEP)
    blend('ruin_lo', x0 - (wide - keep), wide - keep + 35, 'left')
    r = put(RUIN_R, left=TW // 2)
    blend('ruin_ro', r[1] - keep, keep - 35, 'right')
    a = np.asarray(c).astype(np.float32)
    x = np.arange(TW, dtype=np.float32)
    inwin = np.clip((WIN_HALF + 40 - np.abs(x - TW / 2)) / 120, 0, 1)[None, :, None]
    a[..., :3] *= 1 - inwin * 0.66
    a[:Y, TW // 2 - WIN_HALF:TW // 2 + WIN_HALF, 3] = 0
    a[..., 3] *= np.clip(np.minimum(x, TW - 1 - x) / 260.0, 0, 1)[None, :]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def to_fill(im, side, fill, width=240):
    a = np.asarray(im).astype(np.float32)
    x = np.arange(W, dtype=np.float32)
    k = np.clip(((W - 1 - x) if side == 'right' else x) / width, 0, 1)[None, :, None]
    a[..., :3] = a[..., :3] * k + np.array(fill, np.float32) * (1 - k)
    return Image.fromarray(np.uint8(a), 'RGBA')


def write(l, r, t, b):
    os.makedirs(ART, exist_ok=True)
    for n, im in (('left', l), ('right', r), ('top', t.resize((1875, 450), Image.LANCZOS)), ('bottom', b.resize((3750, int(BOT_H * 3750 / 6000)), Image.LANCZOS))):
        F.save_webp(im, os.path.join(ART, 'bronze_%s.webp' % n))
    print('ok', [(n, os.path.getsize(os.path.join(ART, n)) // 1024) for n in sorted(os.listdir(ART))], 'KB')


if __name__ == '__main__':
    if sys.argv[1:2] == ['gen']:
        gen()
    elif sys.argv[1:2] == ['fix']:
        gen_fix(sys.argv[2:])
    elif sys.argv[1:2] == ['ruin']:
        gen_ruin()
    else:
        write(to_fill(left_panel(), 'left', FILL_L), to_fill(right_panel(), 'right', FILL_R), top_band(), bottom_band())
