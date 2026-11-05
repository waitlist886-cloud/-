#!/usr/bin/env python3
# 山铜纪两扇（11-05，第五稿）。用户看了叠人那一版说贴上去的效果也怪：“保留巴尔缇娜那个，其他你自己看着改吧，就一个底图”。所以一扇一张画：右扇 r12a，左扇 l5，都是 GPT 一次画完的（gpt_bronze.py）。
# 这里只做三件事：接上外侧，贴回局部重画的几小块（举剑那只手、芙莉莲的后脑勺），左扇把她们俩贴回去。她们俩用户点名留头一稿的动作，像素从 plate_l 来（left3_fixed 的头发缝里透着旧的人），遮罩拿 plate_l 和 plate_l2 相减。
#   python bronze_collage.py gen [r12a]      右扇外侧接着画，写 fix/r12a_out（左扇接着用 fix/left3_out，巨神的位置没变）
#   python bronze_collage.py [right r12a]    写 right_r12a.png、left5.png（放大过的，连外侧）
# 要 PIL、numpy、scipy，用 ComfyUI 那个 venv 的 python。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.join(HERE, 'out', '山铜纪_11-04')
FIX = os.path.join(ROOT, 'fix')
K = 1.5
SW, SH = 1049, 1500                 # 两扇原图的尺寸
L_OUT, R_OUT = 300, 220             # 外侧接出去多少，跟 bronze_frame.py 一样
SEA_BOX, BELL_BOX = (770, 660, 1049, 912), (70, 1120, 340, 1330)     # 跟 gpt_bronze.py 一样
R_NAME = 'r12a'                     # 右扇现行那一张（gpt_bronze.py 出的）
# 局部重画贴回去：举剑那只手照用户的照片单画的一块，芙莉莲的后脑勺，军礼服那一版的右袖。框跟 gpt_bronze.py 的一样
HAND_BOX, FR_BOX, SLEEVE_BOX = (325, 305, 445, 425), (705, 1190, 865, 1350), (500, 470, 640, 690)
R_PATCH = {'r12a': [('hand2_a1', HAND_BOX), ('fr_a', FR_BOX)], 'r11b': [('hand2_b1', HAND_BOX), ('fr_b', FR_BOX), ('sleeve_b', SLEEVE_BOX)]}
ERASE = [(800, 950, 1000, 1080), (130, 1284, 300, 1375)]              # 两个小人原来的地方，第二块的上沿紧贴新画的那个小人的脚底下
PAIR_POLY = [(120, 1500), (120, 1400), (210, 1200), (440, 1020), (700, 880), (1049, 880), (1049, 1500)]


def wide_plate(name, out_name, out_px, side):
    """画放大，外侧接上 GPT 接着画的那一条。回 (图, 图的 x=0 在哪)。"""
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
    # 披风和底图颜色相近的地方减不出来，是一个个窟窿，透出后头的小人。窟窿填上，外缘不动
    filled = ndimage.binary_erosion(ndimage.binary_fill_holes(m > .5), iterations=2)
    m = np.maximum(m, ndimage.gaussian_filter(filled.astype(np.float32), 1.0))
    poly = Image.new('L', a.size, 0)
    ImageDraw.Draw(poly).polygon([(p[0] * K, p[1] * K) for p in PAIR_POLY], fill=255)     # 只在她们那一带
    m = np.minimum(m, np.asarray(poly.filter(ImageFilter.GaussianBlur(6))) / 255.0)
    return Image.fromarray(np.uint8(m * 255))


def right(name=None):
    name = name or R_NAME
    base, _ = wide_plate(name, name + '_out', R_OUT, 'right')
    for job, (x1, y1, x2, y2) in R_PATCH.get(name, ()):
        p = os.path.join(ROOT, job + '.png')
        if os.path.exists(p):
            new = Image.open(p).convert('RGB').resize((int((x2 - x1) * K), int((y2 - y1) * K)), Image.LANCZOS)
            m = Image.new('L', new.size, 0)
            ImageDraw.Draw(m).rectangle((14, 14, new.width - 15, new.height - 15), fill=255)
            base.paste(new, (int(x1 * K), int(y1 * K)), m.filter(ImageFilter.GaussianBlur(6)))
    base.save(os.path.join(ROOT, 'right_%s.png' % name))
    print('right', name, base.size)


def left():
    base, x0 = wide_plate('l5', 'left3_out', L_OUT, 'left')
    def patch(im, box, edge=24, blur=10):
        """一小块贴回去，边上淡开。"""
        x1, y1, x2, y2 = box
        new = im.resize((int((x2 - x1) * K), int((y2 - y1) * K)), Image.LANCZOS)
        m = Image.new('L', new.size, 0)
        ImageDraw.Draw(m).rectangle((edge, edge, new.width - edge - 1, new.height - edge - 1), fill=255)
        base.paste(new, (x0 + int(x1 * K), int(y1 * K)), m.filter(ImageFilter.GaussianBlur(blur)))
    # 海里和摇钟那两个小人叫她们挡住了：sea、bell 是 l5 这一块加了人重画的，旧的拿没有小人的 plate_l2 盖掉。bell 那一块也带着旧的那个小人的头，要后盖
    for name, box in (('sea', SEA_BOX), ('bell', BELL_BOX)):
        p = os.path.join(ROOT, name + '.png')
        if os.path.exists(p):
            patch(Image.open(p).convert('RGB'), box)
    clean = Image.open(os.path.join(ROOT, 'plate_l2.png')).convert('RGB')
    for box in ERASE:
        patch(clean.crop(box), box, edge=10, blur=6)
    c = base.convert('RGBA')
    src = Image.open(os.path.join(ROOT, 'plate_l.png')).convert('RGB').resize((int(SW * K), int(SH * K)), Image.LANCZOS)
    m = pair_mask()
    m.save(os.path.join(ROOT, 'ref', 'pair_mask.png'))
    layer = Image.new('RGBA', c.size, (0, 0, 0, 0))
    layer.paste(src, (x0, 0))
    al = Image.new('L', c.size, 0)
    al.paste(m, (x0, 0))
    layer.putalpha(al)
    c.alpha_composite(layer)
    c.convert('RGB').save(os.path.join(ROOT, 'left5.png'))
    print('left5', c.size)


def gen(name=None):
    """右扇外侧叫 GPT 接着画，超宽屏上不用镜像。图往左挪，空出来的灰条画满，只取那一条。"""
    import gpt_gen
    name = name or R_NAME
    r = Image.open(os.path.join(ROOT, name + '.png')).convert('RGB').resize((SW, SH), Image.LANCZOS)
    c = Image.new('RGB', r.size, (205, 205, 205))
    c.paste(r, (-R_OUT, 0))
    p = os.path.join(FIX, name + '_out_in.png')
    c.save(p)
    print(gpt_gen.gen(os.path.join(FIX, name + '_out'), 'Image 1 is a finished illustration with an empty flat light grey vertical strip on its right side. Repaint image 1 with the same aspect ratio and the same framing, keeping everything that is already painted exactly as it is, in the same place and at the same size, in the same painting style: big graphic masses of flat colour with rough dry-brush and grunge texture and vertical drips of paint. Fill the grey strip by continuing the picture outward, simply and calmly, with nothing important in it and no people: the deep ultramarine-violet night, almost black at the top, with vertical drips and a few small stars; a few more black spires of the far city, getting lower and ending; the big dark violet stairs with their broken edges of gold light going on to the right; and at the bottom edge the dark rocks of the foreground. No text, no logo, no frame, no crescents, no grey left over.', refs=[p]))


if __name__ == '__main__':
    if sys.argv[1:2] == ['gen']:
        gen(*sys.argv[2:3])
    elif sys.argv[1:2] == ['right']:
        right(*sys.argv[2:3])
    elif sys.argv[1:2] == ['left']:
        left()
    else:
        right()
        left()
