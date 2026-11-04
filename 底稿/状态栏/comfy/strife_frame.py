#!/usr/bin/env python3
# 纷争纪四方的拼法（11-04），照 moon_frame.py 的路子。要 PIL、numpy、scipy，用 ComfyUI 那个 venv 的 python。
#   python gpt_strife.py [名字…]                                        出图，写 out/纷争纪_11-04/。现行的是第五稿 left5、right5b、wall_b5、wall_g5 和第四稿 crown4、strip4、corner4
#     一稿一稿接着改的：left、right 头一稿（用户说往中式飘），left2、right2 换人物和神（用户说脏），left3、right3 洗干净（像普通动画），left4、right4 拿迷宫纪、月银纪锁回画法（用户说全蓝不行），left5、right5 换成血战的色
#   python strife_frame.py gen                                           右扇左边接一条、辛美尔的剑接长，写 fix/right_ext
#   python strife_frame.py crop                                          两扇放大写 left_fix、right_fix，裁靠窗要抠的地方，写 crop/
#   python cut_cpu.py <crop> <cut>                                       抠，写 cut/
#   python strife_frame.py                                               拼，写 art/（strife_left、strife_right、strife_top、strife_bottom.webp）
# 尺寸的账跟迷宫纪一样：两扇画布 1400×2000，LINE 是框线；楣 3000×720（样式里 1250×300，框上沿 y=240）；座 6000×677（样式里 2500×282，框下沿离底 341）。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
import frame_comp as F
from maze1001_frame_gpt import dim_outer, soft

ROOT = os.path.join(HERE, 'out', '纷争纪_11-04')
ART = os.path.join(ROOT, 'art')
FIX = os.path.join(ROOT, 'fix')
W, H, LINE = F.W, F.H, F.LINE
FILL = (21, 21, 29)       # 样式里的 --fm-pl、--fm-pr，超宽屏外侧补的底色
BOT_H, WIN_HALF = 677, 912
L_OUT, R_OUT = 330, 190          # 两扇外侧接出去多少（图的像素），left_out、right_out
TROOP_H, TROOP_X = 300, 4830     # 军士那一排的高和左边（座的画布）
K = 1.5                   # 修图和抠图都在放大 1.5 倍的底上做
L_SCALE, L_TOP = 1.05, 112      # 左扇：图的 1 像素是画布多少，图顶在画布哪一行。五尊魔神的头刚好露在顶栏底下
R_SCALE, R_TOP, R_EXT = 1.05, 112, 124   # 右扇：R_EXT 是图左边接出去多少（图的像素），用户说辛美尔的剑短，他的手离窗太近，整张往外挪，空出来的地方叫 GPT 接着画，剑也接长（fix/right_ext）。墙垛正好接上长垒的垛
LEFT_SRC, RIGHT_SRC, FACE_SRC, WALL_L, WALL_R = 'left5', 'right5b', 'right3', 'wall_b5', 'wall_g5'
# 左扇靠窗伸进窗里的东西，框是 left5.png 的像素：勒莱耶的弓，三叉戟
LEFT_BOXES = [('l_bow', (900, 60, 1024, 350)), ('l_tri', (880, 1080, 1024, 1200))]
# 右扇靠窗只有这一段（y 范围，图的像素）伸进窗里：辛美尔的剑和斗篷。背景的高架桥和城不进窗
RIGHT_BANDS = [(880, 955), (1060, 1536)]
# 接长的剑从 right_ext2 上取的范围（图的像素，x 可以是负的）：辛美尔的剑（用户说该是双手剑的大小，横着摆不下，斜着举起来），诗蔻蒂的剑
SWORD_BOXES = [(-124, 1076, 318, 1536), (-124, 880, 300, 955)]


# 用户说 right3 的五官神情好一些，GPT 重画一回脸就走样（right6，脸变圆变幼），所以照修双王的办法，脸不过模型：right3 和 right5b 几乎对得上，头那一块整块搬过来，只调颜色。
# 多边形写在图的像素上；bg 是 right3 里头边上的底色（这块不搬）
DARK_BLUE = lambda a: (a[..., 2].astype(np.int32) - a[..., 0] > 22) & (a.max(axis=2) < 150)
HEADS = [
    dict(n='乌尔德', poly=[(772, 582), (800, 577), (835, 584), (868, 604), (873, 640), (852, 668), (800, 672), (770, 672), (764, 630)], blur=5),
    dict(n='诗蔻蒂', poly=[(430, 722), (470, 714), (500, 728), (507, 765), (492, 790), (450, 796), (427, 786), (428, 750)], blur=4),
    dict(n='薇儿丹蒂', poly=[(532, 836), (566, 826), (605, 840), (612, 880), (596, 899), (560, 903), (540, 897), (530, 872)], blur=4),
    dict(n='辛美尔', poly=[(190, 992), (240, 984), (286, 995), (299, 1030), (281, 1058), (250, 1070), (222, 1072), (200, 1056), (186, 1030)], blur=4, bg=DARK_BLUE),
    dict(n='芙莉莲', poly=[(370, 1098), (420, 1091), (446, 1100), (462, 1112), (462, 1126), (442, 1136), (430, 1150), (394, 1160), (378, 1140), (370, 1120)], blur=3, bg=DARK_BLUE),
    dict(n='海塔', poly=[(696, 1002), (735, 997), (769, 1020), (761, 1058), (730, 1064), (710, 1062), (692, 1042), (686, 1020)], blur=3, bg=DARK_BLUE),
    dict(n='艾冯', poly=[(816, 1060), (866, 1056), (872, 1084), (860, 1100), (826, 1102), (812, 1086)], blur=4),
    dict(n='精灵弓手', poly=[(630, 1368), (664, 1362), (670, 1400), (642, 1407), (626, 1396)], blur=3),
    dict(n='披毛皮的兵', poly=[(774, 1350), (812, 1345), (816, 1386), (786, 1396), (768, 1378)], blur=3),
]


def transplant(base, donor, ox=0):
    """base 和 donor 是放大 1.5 倍的 RGB，ox 是图的 x=0 在它们上头的位置（图的像素）。回 base 贴好脸的样子。"""
    b = np.asarray(base).astype(np.float32).copy()
    d = np.asarray(donor).astype(np.float32)
    du8 = np.asarray(donor)
    H_, W_ = b.shape[:2]
    for h in HEADS:
        m = Image.new('L', (W_, H_), 0)
        ImageDraw.Draw(m).polygon([((x + ox) * K, y * K) for x, y in h['poly']], fill=255)
        hard = np.asarray(m) > 127
        key = h['bg'](du8) & hard if 'bg' in h else np.zeros_like(hard)
        if key.any():
            key = ndimage.binary_opening(key, iterations=1)
        soft_p = np.asarray(m.filter(ImageFilter.GaussianBlur(h['blur'] * K))).astype(np.float32) / 255
        # 模糊以后边上一半透明，往里收一点，头的中间满格
        soft_p = np.clip(soft_p * 2 - 1, 0, 1)
        keep = np.asarray(Image.fromarray(np.uint8(~key * 255)).filter(ImageFilter.GaussianBlur(0.9))).astype(np.float32) / 255
        al = (soft_p * keep)[..., None]
        # 颜色：right3 的冷光压成这一版的暖光，头这一块一个通道一条直线
        ys, xs = np.nonzero(hard & ~key)
        out = d.copy()
        bb = ndimage.gaussian_filter(b, (3, 3, 0))
        db = ndimage.gaussian_filter(d, (3, 3, 0))
        for c in range(3):
            a1, a0 = np.polyfit(db[ys, xs, c], bb[ys, xs, c], 1)
            a1 = float(np.clip(a1, 0.75, 1.25))
            out[..., c] = np.where(hard | (soft_p > 0), d[..., c] * a1 + (np.median(bb[ys, xs, c]) - a1 * np.median(db[ys, xs, c])), d[..., c])
        # 老脸露在新脸外面：底色那一块里，base 上不像底色的抹掉（拿四周的颜色往里渗）
        if key.any():
            from fix_queens import harmonic_fill
            near = ndimage.binary_dilation(key, iterations=3) & hard
            base_bg = (b[..., 0] < 200) & ((b[..., 0] - b[..., 2]) < 90) & (b.max(axis=2) < 150)
            old = near & ~base_bg
            if old.any():
                b = harmonic_fill(np.uint8(np.clip(b, 0, 255)), old, iters=200).astype(np.float32)
        b = b * (1 - al) + out * al
    return Image.fromarray(np.uint8(np.clip(b, 0, 255)))


def big(name):
    """放大 1.5 倍，缩到画布上的时候细节留得住。"""
    src = Image.open(os.path.join(ROOT, name + '.png')).convert('RGB')
    return src.resize((int(src.width * K), int(src.height * K)), Image.LANCZOS)


def gen():
    """把 right5b 往右挪 R_EXT，左边留一条灰，叫 GPT 接着画满，辛美尔的剑顺手接长。别的不要，只取左边那一条和那把剑。"""
    import gpt_gen
    os.makedirs(FIX, exist_ok=True)
    src = Image.open(os.path.join(ROOT, RIGHT_SRC + '.png')).convert('RGB')
    c = Image.new('RGB', src.size, (205, 205, 205))
    c.paste(src, (R_EXT, 0))
    p = os.path.join(FIX, 'right_ext_in.png')
    c.save(p)
    prompt = ('Image 1 is a finished illustration whose left side has an empty flat light grey vertical strip. Repaint image 1 with aspect ratio 2:3, the same framing, keeping everything that is already painted exactly as it is, in the same place and at the same size, in the same drawing style: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. '
              'Fill the grey strip by continuing the picture to the left: the same dark oxblood red ground, the viaduct continuing to the left with its dark arches, the volleys of black arrows and the streaks of falling fire continuing to the left, with complete arrows. Nothing important in the strip. Complete the torn edge of the cream cloak of the blue-haired young man at the lower left so that it ends in natural tattered points inside the strip. '
              'Two changes to the swords. First, the sword of the blue-haired young man at the lower left is far too short. Give him a sword the size of a two-handed greatsword: a long, broad, straight steel blade with a thin central line, as long as from his waist to the top of his head and more, with his gold crossguard with one small blue stone. Keep his hand where it is, and raise the sword so that the blade points up and to the left at about thirty degrees above horizontal, crossing the empty red ground and ending in a sharp point just inside the left edge of the picture, below the swords of the two women above him. '
              'Second, the slim sword of the queen with red hair and roses is too short. Keep her hand and crossguard exactly where they are and continue the same straight slim blade to the left in the same direction, about half as long again, ending in a sharp point just inside the left edge of the picture. '
              'No other changes at all. No text, no logo, no frame, no grey left over.')
    print(gpt_gen.gen(os.path.join(FIX, 'right_ext2'), prompt, refs=[p]))
    # 外侧也接着画，超宽屏上不用镜像（用户的屏幕 3125 宽，镜像看得出来）
    OUTER = ('Image 1 is a finished illustration with an empty flat light grey vertical strip on one side. Repaint image 1 with aspect ratio 2:3, the same framing, keeping everything that is already painted exactly as it is, in the same place and at the same size, in the same drawing style: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. '
             'Fill the grey strip by continuing the picture outward, simply and calmly, with nothing important in it and no new faces: %s No text, no logo, no frame, no grey left over.')
    l = Image.open(os.path.join(ROOT, LEFT_SRC + '.png')).convert('RGB')
    c = Image.new('RGB', l.size, (205, 205, 205))
    c.paste(l, (L_OUT, 0))
    p = os.path.join(FIX, 'left_out_in.png')
    c.save(p)
    print(gpt_gen.gen(os.path.join(FIX, 'left_out'), OUTER % 'the dark oxblood red sky with falling fire at the top, flat layers of dark crimson and charcoal smoke, the long dark red cloaks and the storm wave continuing to the left and ending, then only smoke and dark silhouettes of the demon host, fading darker toward the left edge.', refs=[p]))
    r = Image.open(os.path.join(ROOT, RIGHT_SRC + '.png')).convert('RGB')
    c = Image.new('RGB', r.size, (205, 205, 205))
    c.paste(r, (-R_OUT, 0))
    p = os.path.join(FIX, 'right_out_in.png')
    c.save(p)
    print(gpt_gen.gen(os.path.join(FIX, 'right_out'), OUTER % 'the oxblood red sky and red hills, the dark viaduct and the white mantle and banners continuing to the right and ending, the pale stone battlement continuing to the right at the bottom, then only dark red ground, fading darker toward the right edge.', refs=[p]))


def right_full():
    """接好左边那一条和那两把剑、贴好脸的右扇，放大 1.5 倍。图的 x 从 -R_EXT 起。先接再贴脸，脸压在最上头。"""
    body = big(RIGHT_SRC)
    E = int(R_EXT * K)
    ext = Image.open(os.path.join(FIX, 'right_ext2.png')).convert('RGB').resize((body.width, body.height), Image.LANCZOS)     # right_ext2 的 x=R_EXT 是图的 x=0，比例一样
    out = Image.new('RGB', (body.width + E, body.height))
    out.paste(body, (E, 0))
    xs = np.arange(out.width, dtype=np.float32) / K - R_EXT
    ys = np.arange(out.height, dtype=np.float32) / K
    # 左边那一条：x<8 全用 right_ext2，到 x=32 淡回本来的
    al = np.tile(np.clip((32 - xs) / 24, 0, 1), (out.height, 1))
    # 那两把剑：框里全用 right_ext2，四边淡一圈
    for x0, y0, x1, y1 in SWORD_BOXES:
        bx = np.clip(np.minimum(xs - x0, x1 - xs) / 6, 0, 1)
        by = np.clip(np.minimum(ys - y0, y1 - ys) / 6, 0, 1)
        by[ys >= y1 - 6] = np.where(y1 >= 1536, 1, by[ys >= y1 - 6])
        al = np.maximum(al, np.outer(by, bx))
    ext_full = Image.new('RGB', out.size)
    ext_full.paste(ext, (0, 0))
    al[:, ext.width:] = 0                    # right_ext2 只有原来那么宽，超出的部分用本来的
    a = np.asarray(out).astype(np.float32) * (1 - al[..., None]) + np.asarray(ext_full).astype(np.float32) * al[..., None]
    donor = Image.new('RGB', out.size)
    donor.paste(big(FACE_SRC), (E, 0))
    res = transplant(Image.fromarray(np.uint8(np.clip(a, 0, 255))), donor, ox=R_EXT)
    # 外侧：right_out 的 x 比图的 x 小 R_OUT
    O = int(R_OUT * K)
    wide = Image.new('RGB', (res.width + O, res.height))
    wide.paste(res, (0, 0))
    ro = Image.open(os.path.join(FIX, 'right_out2.png')).convert('RGB').resize((body.width, body.height), Image.LANCZOS)
    ro_full = Image.new('RGB', wide.size)
    ro_full.paste(ro, (E + O, 0))
    x = np.arange(wide.width, dtype=np.float32)
    al = np.clip((x - (res.width - 40)) / 40, 0, 1)[None, :, None]
    b = np.asarray(wide).astype(np.float32) * (1 - al) + np.asarray(ro_full).astype(np.float32) * al
    return Image.fromarray(np.uint8(np.clip(b, 0, 255)))


def crop():
    os.makedirs(os.path.join(ROOT, 'crop'), exist_ok=True)
    l, r = big(LEFT_SRC), right_full()
    l.save(os.path.join(ROOT, 'left_fix.png'))
    r.save(os.path.join(ROOT, 'right_fix.png'))
    r.save(os.path.join(ROOT, 'crop', 'r_full.png'))
    for name, box in LEFT_BOXES:
        c = l.crop([int(v * K) for v in box])
        c.resize((c.width * 2, c.height * 2), Image.LANCZOS).save(os.path.join(ROOT, 'crop', name + '.png'))
    print('ok')


def top_dark(a):
    a[..., :3] *= (0.5 + 0.5 * np.clip((np.arange(H, dtype=np.float32) - 60) / 90, 0, 1))[:, None, None]


def outer_left():
    """左扇：图的外侧接上 left_out，放大 1.5 倍。回 (图, 接出去多少)。"""
    body = big(LEFT_SRC)
    E = int(L_OUT * K)
    ext = Image.open(os.path.join(FIX, 'left_out.png')).convert('RGB').resize((body.width, body.height), Image.LANCZOS)
    out = Image.new('RGB', (body.width + E, body.height))
    out.paste(body, (E, 0))
    al = np.clip((E + 40 - np.arange(out.width, dtype=np.float32)) / 40, 0, 1)
    al[ext.width:] = 0
    full = Image.new('RGB', out.size)
    full.paste(ext, (0, 0))
    a = np.asarray(out).astype(np.float32) * (1 - al[None, :, None]) + np.asarray(full).astype(np.float32) * al[None, :, None]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)))


def left_panel():
    src = outer_left()
    w, h = int((1024 + L_OUT) * L_SCALE), int(1536 * L_SCALE)
    s = src.resize((w, h), Image.LANCZOS)
    x0 = W - w                # 负的，外侧多出来的裁掉
    c = Image.new('RGB', (W, H))
    c.paste(s, (x0, L_TOP))
    c.paste(c.crop((0, L_TOP, W, L_TOP + 8)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, L_TOP), Image.BICUBIC), (0, 0))
    end = L_TOP + h
    if end < H:
        c.paste(c.crop((0, end - 8, W, end)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, H - end), Image.BICUBIC), (0, end))
    a = np.dstack([np.asarray(c).astype(np.float32), np.full((H, W), 255, np.float32)])
    a = dim_outer(a, 'left', amount=0.45)
    top_dark(a)
    m = Image.new('L', (W, H), 0)
    for name, box in LEFT_BOXES:
        if not os.path.exists(os.path.join(ROOT, 'cut', name + '.png')):   # 还没抠完也能先看个样子
            continue
        p = Image.open(os.path.join(ROOT, 'cut', name + '.png')).getchannel('A')
        bw, bh = int((box[2] - box[0]) * L_SCALE), int((box[3] - box[1]) * L_SCALE)
        p = p.resize((bw, bh), Image.LANCZOS).point(lambda t: 255 if t > 90 else 0)
        m.paste(p, (x0 + int((box[0] + L_OUT) * L_SCALE), L_TOP + int(box[1] * L_SCALE)))
    al = np.asarray(soft(m)).astype(np.float32)
    al *= np.clip((W - 1 - np.arange(W, dtype=np.float32)) / 46, 0, 1)[None, :]   # 火到图边就断了，往外淡掉
    a[:, W - LINE:, 3] = al[:, W - LINE:]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def right_panel():
    src = right_full()
    w, h = int((1024 + R_EXT + R_OUT) * R_SCALE), int(1536 * R_SCALE)
    s = src.resize((w, h), Image.LANCZOS)
    c = Image.new('RGB', (W, H), (0, 0, 0))
    c.paste(s, (0, R_TOP))
    c.paste(c.crop((0, R_TOP, W, R_TOP + 8)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, R_TOP), Image.BICUBIC), (0, 0))
    end = R_TOP + h
    if end < H:
        c.paste(c.crop((0, end - 8, W, end)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, H - end), Image.BICUBIC), (0, end))
    a = np.dstack([np.asarray(c).astype(np.float32), np.full((H, W), 255, np.float32)])
    a = dim_outer(a, 'right', amount=0.4)
    top_dark(a)
    # 伸进窗里的只有剑和斗篷：底色是暗红，剑是钢色、斗篷是米色，按颜色就抠得干净，细的剑尖 BiRefNet 反而丢。落火是饱和的橙，不算
    rgb = np.asarray(c).astype(np.float32)
    arr = np.uint8(((rgb.max(axis=2) > 118) & (rgb.max(axis=2) - rgb.min(axis=2) < 78)) * 255)
    keep = np.zeros_like(arr)
    for y0, y1 in RIGHT_BANDS:
        keep[int(R_TOP + y0 * R_SCALE):int(R_TOP + y1 * R_SCALE)] = 255
    arr[keep == 0] = 0
    m = F.attached_only(arr, LINE, 0, LINE + 1)
    al = np.asarray(soft(Image.fromarray(m))).astype(np.float32).copy()
    a[:, :LINE, 3] = al[:, :LINE]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def rgba(name, sub=''):
    return Image.open(os.path.join(ROOT, sub, name + '.png')).convert('RGBA')


def tight(im, thr=40):
    return im.crop(im.getchannel('A').point(lambda v: 255 if v > thr else 0).getbbox())


def strip(w, h, top=(24, 25, 34), bot=(17, 17, 24), fade=90):
    """楣的底：一条暗的天，两头淡掉，跟两扇接上。"""
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    a = np.array(top, np.float32) * (1 - t) + np.array(bot, np.float32) * t
    rng = np.random.default_rng(3)
    a = a * np.ones((h, w, 3), np.float32) + rng.normal(0, 2.2, (h, w, 1))
    al = np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / fade, 0, 1)[None, :] * 255 * np.ones((h, w), np.float32)
    return Image.fromarray(np.uint8(np.clip(np.dstack([a, al]), 0, 255)), 'RGBA')


def top_band():
    """楣：交织的兵刃和碎了的桂冠。两个肩膀各一朵花边（框角上），一条枝子沿框上沿走，正中一顶断开的桂冠。"""
    TW, TH, Y = 3000, 720, 240
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    c.alpha_composite(strip(2000, Y), ((TW - 2000) // 2, 0))
    shadow = dict(shadow_kw=dict(blur=10, offset=(0, 6), opacity=0.6))
    st = tight(rgba('strip4'))
    k = 1500 / st.width
    F.place(c, st, (TW - 1500) // 2, Y - int(st.height * k * 0.56), k, **shadow)
    co = tight(rgba('corner4'))
    k = 0.35
    x_l, y_t = 508, 150
    F.place(c, co, x_l, y_t, k, **shadow)
    cr_ = tight(rgba('corner_r'))
    k_r = int(co.width * k) / cr_.width     # 跟左肩一样宽
    F.place(c, cr_, TW - x_l - int(cr_.width * k_r), y_t, k_r, **shadow)
    cr = tight(rgba('crown4'))
    k = 128 / cr.height                 # 下沿不过 y=282（样式 118），不压页头的字
    F.place(c, cr, (TW - int(cr.width * k)) // 2, 154, k, **shadow)
    return c


def night(im, keep=205, span=40, gain=0.78):
    """长垒的底色压成夜里的石头，亮的（蜡烛、裂缝里的光、结界）不压。"""
    a = np.asarray(im).astype(np.float32)
    lum = a[..., :3].max(axis=2)
    e = np.clip((lum - keep) / span, 0, 1)[..., None]
    a[..., :3] *= gain + (1 - gain) * e
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def tower_piece(wall):
    """烽火台从 wall_b 上抠出来，单独放：上半身 x 60 到 340，下半身放宽到 50 到 360。"""
    m = Image.new('L', wall.size, 0)
    d = ImageDraw.Draw(m)
    d.polygon([(52, 0), (345, 0), (345, 440), (362, 620), (362, 724), (40, 724), (50, 620), (72, 440), (52, 300)], fill=255)
    a = np.asarray(wall).astype(np.float32)
    a[..., 3] *= np.asarray(m.filter(__import__('PIL.ImageFilter', fromlist=['GaussianBlur']).GaussianBlur(1.2))).astype(np.float32) / 255
    return Image.fromarray(np.uint8(a), 'RGBA').crop((36, 0, 366, 724))


def bottom_band():
    """座：白石长垒。左半边是破口和发光的盾，右半边是城门和圈环的结界，接缝在输入框后头。框下沿离屏幕底 142（样式），折回画布 341。
    窗口那一列框下沿以上不画，框下沿以下压暗，输入框和预设那一排看得清。"""
    TW, TH, Y = 6000, BOT_H, BOT_H - 341
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    wall, gate = rgba(WALL_L), rgba(WALL_R)
    ga = np.asarray(gate).copy()
    ga[:268, 1570:, 3] = 0                  # 城门右边那一段垛口以上
    gate = Image.fromarray(ga, 'RGBA')

    def put(src, sx0, sx1, x, k=1.0):
        p = src.crop((sx0, 0, sx1, src.height))
        if k != 1.0:
            p = p.resize((int(p.width * k), int(p.height * k)), Image.LANCZOS)
        c.alpha_composite(p, (max(x, 0), max(TH - p.height, 0)), (max(-x, 0), max(p.height - TH, 0)))
        return p.width
    # 不翻转（用户说边框那儿不要有镜像），两头接别的墙段：城门那张的平墙和破口那张的平墙换着接。垛口都在屏幕底往上 424 画布
    # 左半边：破口中心放在 x=1560（图的 1130）
    dx = 1560 - 1130
    k = 0.944
    gw = int(gate.width * k)
    put(gate, gate.width - 612, gate.width, 345 + dx - int(600 * k) - int(612 * k), k=k)
    put(gate, 0, 600, 345 + dx - int(600 * k), k=k)
    put(wall, 345, 2172, 345 + dx)
    put(gate, gate.width - 612, gate.width, 2172 + dx, k=k)
    # 右半边：城门中心放在 x=4440（图的 1085），0.944 倍。左边接到窗口正中，右边接破口那张靠右的平墙，垛口以上的小人和旗去掉，军士站在这里
    gx = 4440 - int(1085 * k)
    put(wall, 345, 860, gx - 515)
    put(gate, 0, gate.width, gx, k=k)
    wa = np.asarray(wall).copy()
    wa[:292, 1400:, 3] = 0
    put(Image.fromarray(wa, 'RGBA'), 1400, 2172, gx + gw)
    # 烽火台：左边一座，0.93 倍，火苗不出画布。压在墙前头
    t = tower_piece(wall)
    k = 0.93
    tw = int(t.width * k)
    t = t.resize((tw, int(t.height * k)), Image.LANCZOS)
    c.alpha_composite(t, (790, TH - t.height))
    # 各族军士和机兵站在城门右边的墙头上，压在两扇前头；脚叫垛口挡着，所以先放人再放这一截墙
    tr = tight(rgba('troops'))
    k = TROOP_H / tr.height
    tr = tr.resize((int(tr.width * k), TROOP_H), Image.LANCZOS)
    wall_only = np.asarray(c).copy()
    y_feet = TH - 432 + 30                     # 人的下沿压进垛口里
    layer = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    layer.alpha_composite(tr, (TROOP_X, max(y_feet - TROOP_H, 0)), (0, max(TROOP_H - y_feet, 0)))
    layer_a = np.asarray(layer).astype(np.float32)
    wall_a = wall_only.astype(np.float32)
    # 人在墙后头：墙不透明的地方压住人
    a_w = wall_a[..., 3:4] / 255
    a_l = layer_a[..., 3:4] / 255
    merged = wall_a[..., :3] * a_w + layer_a[..., :3] * a_l * (1 - a_w)
    a_o = a_w + a_l * (1 - a_w)
    c = Image.fromarray(np.uint8(np.clip(np.dstack([merged / np.maximum(a_o, 1e-3), a_o * 255]), 0, 255)), 'RGBA')
    c = night(c)
    a = np.asarray(c).astype(np.float32)
    x = np.arange(TW, dtype=np.float32)
    # 窗口那一列：框下沿以上清掉，以下压暗
    inwin = np.clip((WIN_HALF + 40 - np.abs(x - TW / 2)) / 120, 0, 1)[None, :, None]
    a[..., :3] *= 1 - inwin * 0.66
    a[:Y, TW // 2 - WIN_HALF:TW // 2 + WIN_HALF, 3] = 0
    a[..., 3] *= np.clip(np.minimum(x, TW - 1 - x) / 260.0, 0, 1)[None, :]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def to_fill(im, side, width=240):
    a = np.asarray(im).astype(np.float32)
    x = np.arange(W, dtype=np.float32)
    k = np.clip(((W - 1 - x) if side == 'right' else x) / width, 0, 1)[None, :, None]
    a[..., :3] = a[..., :3] * k + np.array(FILL, np.float32) * (1 - k)
    return Image.fromarray(np.uint8(a), 'RGBA')


def write(l, r, t, b):
    os.makedirs(ART, exist_ok=True)
    for n, im in (('left', l), ('right', r), ('top', t.resize((1875, 450), Image.LANCZOS)), ('bottom', b.resize((3750, int(BOT_H * 3750 / 6000)), Image.LANCZOS))):
        F.save_webp(im, os.path.join(ART, 'strife_%s.webp' % n))
    print('ok', [(n, os.path.getsize(os.path.join(ART, n)) // 1024) for n in sorted(os.listdir(ART))], 'KB')


if __name__ == '__main__':
    if sys.argv[1:2] == ['gen']:
        gen()
    elif sys.argv[1:2] == ['crop']:
        crop()
    else:
        write(to_fill(left_panel(), 'left'), to_fill(right_panel(), 'right'), top_band(), bottom_band())
