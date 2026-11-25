#!/usr/bin/env python3
# 迷宫纪前传四方的拼法（11-25），照 moon_frame.py、strife_frame.py 的路子。要 PIL、numpy、scipy，用 ComfyUI 那个 venv 的 python。
#   python gpt_pre.py [名字…]        出图，写 out/前传_11-25/（left、right、seal、corner、strip、camp）
#   python pre_frame.py gen          两扇外侧各接一条（超宽屏上不用镜像），写 fix/left_out、fix/right_out
#   python pre_frame.py              拼，写 art/（pre_left、pre_right、pre_top、pre_bottom.webp）
# 尺寸的账跟别的四纪一样：两扇画布 1400×2000，LINE 是框线；楣 3000×720（样式里 1250×300，框上沿 y=240）；座 6000×677（样式里 2500×282，框下沿离底 341）。
# 靠窗那 90 像素只留连着框线的东西：左扇是井口的木架、崖边和黑潮的浪头，右扇是提灯的手、飘出去的委托单和衣摆。按颜色认（底是暗的深棕，东西是亮的），不走 BiRefNet。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import numpy as np
from PIL import Image
import frame_comp as F
from maze1001_frame_gpt import dim_outer, soft

ROOT = os.path.join(HERE, 'out', '前传_11-25')
ART = os.path.join(ROOT, 'art')
FIX = os.path.join(ROOT, 'fix')
W, H, LINE = F.W, F.H, F.LINE
FILL = (29, 20, 14)        # 样式里的 --fm-pl、--fm-pr，超宽屏外侧补的底色（make_css_frame.py ERA['pre'] 的 pl、pr）
BOT_H, WIN_HALF = 677, 912
SRC = dict(left='left2', right='right2', seal='seal', corner='corner2', strip='strip', camp='camp')   # 现行：两扇和角是第二稿
OUT_W = 220                # 两扇外侧接出去多少（图的像素）
L_K, L_TOP = 1.25, 60      # 左扇：图的 1 像素是画布多少，图顶在画布哪一行
R_K, R_TOP, R_X0 = 1.25, 60, 60   # 右扇：图的 x=60 落在框线上，举灯的手和飞出去的委托单伸进窗里
THR = 90                   # 左扇比这个亮的算东西（底是 50 上下的深棕）
R_ROWS = [(330, 1250)]     # 右扇靠窗那一条只在这一段里认：飞出去的委托单、举着的灯、外套的下摆


def rgb(name, sub=''):
    return Image.open(os.path.join(ROOT, sub, name + '.png')).convert('RGB')


def rgba(name, sub=''):
    return Image.open(os.path.join(ROOT, sub, name + '.png')).convert('RGBA')


def gen():
    import gpt_gen
    os.makedirs(FIX, exist_ok=True)
    OUTER = ('Image 1 is a finished illustration with an empty flat light grey vertical strip on one side. Repaint image 1 with aspect ratio 2:3, the same framing, keeping everything that is already painted exactly as it is, in the same place and at the same size, in the same drawing style: flat cut-paper shapes, smooth clean colour with very fine parallel hatching and engraved lines, thin coloured outlines, matte. '
             'Fill the grey strip by continuing the picture outward, simply and calmly, with nothing important in it and no new faces: %s No text, no logo, no frame, no grey left over.')
    for side, what in (('left', 'the dark umber sky at the top, the layers of rock and the cut-open strata continuing to the left with the ruined city, the glowing mushrooms, the underground sea and the amber crystals running on and ending in dark rock, and the black tide continuing to the left at the bottom, fading darker toward the left edge.'),
                       ('right', 'the dark umber sky and the old pale stone wall at the top, the timber guild hall and its banners continuing to the right and ending, the green-grey hills, then the cloak and robe of the mage ending in calm folds, the tents, lantern poles and the dim crowd at the bottom, fading darker toward the right edge.')):
        src = rgb(SRC[side])
        c = Image.new('RGB', src.size, (205, 205, 205))
        c.paste(src, (OUT_W, 0) if side == 'left' else (-OUT_W, 0))
        p = os.path.join(FIX, '%s_out_in.png' % side)
        c.save(p)
        print(gpt_gen.gen(os.path.join(FIX, '%s_out' % side), OUTER % what, refs=[p]))


def widened(side):
    """图的外侧接上 fix/<side>_out。回接好的图（外侧多 OUT_W），没出图时外侧照镜像。"""
    body = rgb(SRC[side])
    out = Image.new('RGB', (body.width + OUT_W, body.height))
    p = os.path.join(FIX, '%s_out.png' % side)
    if os.path.exists(p):
        ext = Image.open(p).convert('RGB').resize(body.size, Image.LANCZOS)
    else:
        ext = None
    x = np.arange(out.width, dtype=np.float32)
    if side == 'left':
        out.paste(body, (OUT_W, 0))
        if ext is None:
            out.paste(body.crop((0, 0, OUT_W, body.height)).transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
            return out
        full = Image.new('RGB', out.size)
        full.paste(ext, (0, 0))                      # ext 的 x=OUT_W 是图的 x=0
        al = np.clip((OUT_W + 40 - x) / 40, 0, 1)
        al[ext.width:] = 0
    else:
        out.paste(body, (0, 0))
        if ext is None:
            out.paste(body.crop((body.width - OUT_W, 0, body.width, body.height)).transpose(Image.FLIP_LEFT_RIGHT), (body.width, 0))
            return out
        full = Image.new('RGB', out.size)
        full.paste(ext, (OUT_W, 0))                  # ext 的 x=0 是图的 x=OUT_W
        al = np.clip((x - (body.width - 40)) / 40, 0, 1)
    a = np.asarray(out).astype(np.float32) * (1 - al[None, :, None]) + np.asarray(full).astype(np.float32) * al[None, :, None]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)))


def place(src, k, top, x0):
    """src 缩 k 倍贴在 (x0, top)，上下空的地方拉开最边上几行。"""
    w, h = int(src.width * k), int(src.height * k)
    s = src.resize((w, h), Image.LANCZOS)
    c = Image.new('RGB', (W, H))
    c.paste(s, (x0, top))
    if top > 0:
        c.paste(c.crop((0, top, W, top + 8)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, top), Image.BICUBIC), (0, 0))
    end = top + h
    if end < H:
        c.paste(c.crop((0, end - 8, W, end)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, H - end), Image.BICUBIC), (0, end))
    return c


def top_dark(a):
    a[..., :3] *= (0.5 + 0.5 * np.clip((np.arange(H, dtype=np.float32) - 60) / 90, 0, 1))[:, None, None]


def bite(c, x0, x1, seed, thr=THR, rows=None, close=0):
    """靠窗那一条（x0 到 x1）里只留亮的、连着框线那一列的东西，边上软一点。rows 是画布上的 (y0, y1)，只在这几段里认。"""
    a = np.asarray(c).astype(np.float32)
    on = a.max(axis=2) > thr
    if close:   # 灯的铜架子比纸和火暗，先认亮的，再把中间的空和细缝合上
        from scipy import ndimage
        on = ndimage.binary_fill_holes(ndimage.binary_closing(on, iterations=close))
    on = np.uint8(on * 255)
    if rows:
        band = np.zeros(on.shape[0], bool)
        for y0, y1 in rows:
            band[y0:y1] = True
        on[~band] = 0
    lo, hi = min(x0, seed), max(x1, seed + 1)   # 框线那一列也要算进来，不然连着它的东西认不出来
    keep = np.zeros_like(on)
    keep[:, lo:hi] = on[:, lo:hi]
    m = F.attached_only(keep, seed, lo, hi)
    return np.asarray(soft(Image.fromarray(m), blur=1.0)).astype(np.float32)


def left_panel():
    src = widened('left')
    x0 = W - int(src.width * L_K)
    c = place(src, L_K, L_TOP, x0)
    a = np.dstack([np.asarray(c).astype(np.float32), np.full((H, W), 255, np.float32)])
    a = dim_outer(a, 'left', amount=0.45)
    top_dark(a)
    al = bite(c, W - LINE, W, W - LINE - 1)
    a[:, W - LINE:, 3] = al[:, W - LINE:]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def right_panel():
    src = widened('right')
    x0 = LINE - int(R_X0 * R_K)
    c = place(src, R_K, R_TOP, x0)
    a = np.dstack([np.asarray(c).astype(np.float32), np.full((H, W), 255, np.float32)])
    a = dim_outer(a, 'right', amount=0.4)
    top_dark(a)
    # 右扇的底是 80 到 160 的灰褐（城墙、灯晕），委托单、灯火、外套是 180 往上；底下那一片雾也亮，所以只认 R_ROWS 那一段（图的 y）
    al = bite(c, 0, LINE, LINE, thr=178, close=6, rows=[(R_TOP + int(y0 * R_K), R_TOP + int(y1 * R_K)) for y0, y1 in R_ROWS])
    a[:, :LINE, 3] = al[:, :LINE]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def to_fill(im, side, width=240):
    a = np.asarray(im).astype(np.float32)
    x = np.arange(W, dtype=np.float32)
    k = np.clip(((W - 1 - x) if side == 'right' else x) / width, 0, 1)[None, :, None]
    a[..., :3] = a[..., :3] * k + np.array(FILL, np.float32) * (1 - k)
    return Image.fromarray(np.uint8(a), 'RGBA')


def solid(im, low=90, high=200):
    a = np.asarray(im).astype(np.float32)
    a[..., 3] = np.clip((a[..., 3] - low) / (high - low), 0, 1) * 255
    return Image.fromarray(np.uint8(a), 'RGBA')


def tight(im, thr=40):
    return im.crop(im.getchannel('A').point(lambda v: 255 if v > thr else 0).getbbox())


def strip_bg(w, h, top=(36, 26, 19), bot=(25, 18, 12), fade=90):
    """楣的底：一条暗的天，两头淡掉，跟两扇接上。"""
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    a = np.array(top, np.float32) * (1 - t) + np.array(bot, np.float32) * t
    rng = np.random.default_rng(3)
    a = a * np.ones((h, w, 3), np.float32) + rng.normal(0, 2.2, (h, w, 1))
    al = np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / fade, 0, 1)[None, :] * 255 * np.ones((h, w), np.float32)
    return Image.fromarray(np.uint8(np.clip(np.dstack([a, al]), 0, 255)), 'RGBA')


TOP = dict(strip_w=1500, strip_top=135, corner_k=0.35, corner_x=508, corner_y=150, seal_h=132, seal_y=150)   # 绳在框线上头九十来像素（藏在顶栏底下），委托单的下沿刚过框线；旅印照纷争纪的桂冠放在顶栏和框线中间露出来的那一截里，下沿不过 y=282（样式 118），不压页头的字


def top_band():
    """楣：沿框上沿一条挂委托单的绳，两个肩膀各一朵绳圈加小灯（右肩翻过来），正中旅印。"""
    TW, TH, Y = 3000, 720, 240
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    c.alpha_composite(strip_bg(2000, Y), ((TW - 2000) // 2, 0))
    shadow = dict(shadow_kw=dict(blur=10, offset=(0, 6), opacity=0.6))
    st = tight(rgba(SRC['strip']))
    k = TOP['strip_w'] / st.width
    # 正中旅印那一块让开：绳照留，绳底下挂的委托单拿掉两张（图的像素，绳在顶上 30 行以内）
    from scipy import ndimage
    sa = np.asarray(st).copy()
    cx, half = st.width // 2, int(60 / k)
    lab, n = ndimage.label(sa[30:, :, 3] > 20)
    for i, sl in enumerate(ndimage.find_objects(lab), 1):     # 一张一张整张拿掉，不留半截
        if sl[1].start < cx + half and sl[1].stop > cx - half:
            sa[30:, :, 3][lab == i] = 0
    st = Image.fromarray(sa, 'RGBA')
    F.place(c, st, (TW - TOP['strip_w']) // 2, TOP['strip_top'], k, **shadow)
    co = tight(solid(rgba(SRC['corner'])))   # 透明底上带一层半透明的灰，收掉
    k = TOP['corner_k']
    F.place(c, co, TOP['corner_x'], TOP['corner_y'], k, **shadow)
    F.place(c, co, TW - TOP['corner_x'] - int(co.width * k), TOP['corner_y'], k, flip=True, **shadow)
    se = tight(rgba(SRC['seal']))
    k = TOP['seal_h'] / se.height
    F.place(c, se, (TW - int(se.width * k)) // 2, TOP['seal_y'], k, **shadow)
    return c


# 座上的营地几块：(图上裁哪一块, 缩多少, 放在画布哪个 x)，先放的在后头。框的两个下角在 x=2088、3912
CAMP = [((1300, 0, 2172, 724), 0.7, 778), ((0, 0, 1000, 724), 0.9, 1338),
        ((0, 0, 1000, 724), 0.7, 4632), ((1150, 0, 2172, 724), 0.9, 3762)]


def bottom_band():
    """座：井口边上的营地。两头高的地方接到框的两个下角，窗口那一列框下沿以上不画，以下压暗（输入框和预设那一排看得清）。"""
    TW, TH, Y = 6000, BOT_H, BOT_H - 341
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    camp = rgba(SRC['camp'])
    # 地：一条暗的地从头铺到尾，各块营地压在上头，接缝看不出
    gh = 150
    t = np.linspace(0, 1, gh, dtype=np.float32)[:, None, None]
    ground = (np.array((52, 38, 30), np.float32) * (1 - t) + np.array((30, 22, 17), np.float32) * t) * np.ones((gh, TW, 3), np.float32)
    gal = np.clip(np.arange(gh, dtype=np.float32) / 40, 0, 1)[:, None] * 255 * np.ones((gh, TW), np.float32)
    c.alpha_composite(Image.fromarray(np.uint8(np.dstack([ground, gal])), 'RGBA'), (0, TH - gh))
    # 不镜像（用户说边框那儿不要有镜像）：框的两个下角各放营地高的那一头，再往外放另一头缩小一点当远处
    for box, k, x in CAMP:
        p = camp.crop(box)
        p = p.resize((int(p.width * k), int(p.height * k)), Image.LANCZOS)
        c.alpha_composite(p, (x, TH - p.height + 8))
    a = np.asarray(c).astype(np.float32)
    x = np.arange(TW, dtype=np.float32)
    inwin = np.clip((WIN_HALF + 40 - np.abs(x - TW / 2)) / 120, 0, 1)[None, :, None]
    a[..., :3] *= 1 - inwin * 0.55
    a[:Y, TW // 2 - WIN_HALF:TW // 2 + WIN_HALF, 3] = 0
    a[..., 3] *= np.clip(np.minimum(x, TW - 1 - x) / 260.0, 0, 1)[None, :]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def write(l, r, t, b):
    os.makedirs(ART, exist_ok=True)
    for n, im in (('left', l), ('right', r), ('top', t.resize((1875, 450), Image.LANCZOS)), ('bottom', b.resize((3750, int(BOT_H * 3750 / 6000)), Image.LANCZOS))):
        F.save_webp(im, os.path.join(ART, 'pre_%s.webp' % n))
    print('ok', [(n, os.path.getsize(os.path.join(ART, n)) // 1024) for n in sorted(os.listdir(ART))], 'KB')


if __name__ == '__main__':
    if sys.argv[1:2] == ['gen']:
        gen()
    else:
        write(to_fill(left_panel(), 'left'), to_fill(right_panel(), 'right'), top_band(), bottom_band())
