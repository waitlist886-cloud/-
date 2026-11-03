#!/usr/bin/env python3
# 迷宫纪 1001 年那一套：把 maze1001_parts.py 出的零件拼成四张带透明的图（左、右、楣、座），写 out/四方_11-03/art/。
# 右扇：靠窗那一头在左（x 小），人人朝左，朝着正中的对话。左扇：靠窗那一头在右。楣和座跟窗口一样按固定像素放，画布 3000 宽，样式里缩到 1250。
# 1536×1024 的屏幕上两扇只露靠窗 850 像素（画布坐标），要紧的人都放在这里面，再往外的宽屏才看得见。
#   python maze1001_frame.py [right left top bottom]
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frame_comp as F

ROOT = os.path.join(HERE, 'out', '四方_11-03')
P = os.path.join(ROOT, 'parts')
CUT = os.path.join(P, 'cut')
ART = os.path.join(ROOT, 'art')
os.makedirs(ART, exist_ok=True)
NIGHT = (22, 30, 74)
VIOLET = (40, 22, 74)
W, H, LINE = F.W, F.H, F.LINE


def fig(name, thin=True):
    """抠好的一张：细东西补回来，毛边收一收，边上的颜色往里借。"""
    im = Image.open(os.path.join(CUT, name + '.png')).convert('RGBA')
    if thin:
        im = F.keep_thin(im)
    return F.clean_edges(F.trim_alpha(im))


def flip_x(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


def sparkle_layer(size, seed, n=60, box=None, color=(255, 236, 190), avoid=()):
    """四角星和金粉，压在最上面，把一层一层的东西连起来。avoid 是不放的方框（人脸）。"""
    rng = np.random.default_rng(seed)
    S = 2
    lay = Image.new('RGBA', (size[0] * S, size[1] * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = box or (0, 0, size[0], size[1])
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.choice([3, 4, 5, 7, 11, 16])
        al = int(rng.uniform(120, 255))
        if any(a <= x <= c and b <= y <= e for a, b, c, e in avoid):
            continue
        x, y, r = x * S, y * S, r * S
        if r >= 7 * S:
            k = r * 0.13
            d.polygon([(x, y - r), (x + k, y - k), (x + r, y), (x + k, y + k), (x, y + r), (x - k, y + k), (x - r, y), (x - k, y - k)], fill=color + (al,))
        else:
            d.ellipse((x - r / 3, y - r / 3, x + r / 3, y + r / 3), fill=color + (al,))
    lay = lay.resize(size, Image.LANCZOS)
    glow = lay.filter(ImageFilter.GaussianBlur(5))
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(lay)
    return out


def light_from_window(canvas, side, color=(255, 226, 170), strength=0.20, reach=620):
    """靠窗那一边压一层暖光，只落在画上。"""
    a = np.asarray(canvas).astype(np.float32)
    x = np.arange(W, dtype=np.float32)
    d = x if side == 'right' else (W - 1 - x)
    k = np.clip(1 - d / reach, 0, 1)[None, :, None] ** 2 * strength
    c = np.array(color, dtype=np.float32)
    a[..., :3] = 255 - (255 - a[..., :3]) * (1 - k * c / 255.0)
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def dim_outer(c, side, amount=0.45, start=620):
    """底图往外侧压暗（只压底，人不压），亮云别抢戏。"""
    a = np.asarray(c).astype(np.float32)
    x = np.arange(W, dtype=np.float32)
    d = x if side == 'right' else (W - 1 - x)
    k = 1 - np.clip((d - start) / (W - start), 0, 1)[None, :, None] * amount
    a[..., :3] *= k
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def erase(im, box):
    """零件上多出来的东西抹掉（续画偶尔多长一只手）。"""
    im = im.copy()
    ImageDraw.Draw(im).rectangle(box, fill=(0, 0, 0, 0))
    return im


def right_panel():
    c = F.base_canvas(os.path.join(P, 'bg_right_42.png'), 'right')
    c = dim_outer(c, 'right')
    back = dict(tint_to=NIGHT, rim_dir=(3, 0), rim_strength=0.55)
    near = dict(rim_dir=(4, 0), rim_strength=0.8)
    wide = dict(shadow_kw=dict(blur=18, offset=(6, 12), opacity=0.5))
    # 从后往前：欧巴德斯站在后排最高处，七神分几排，一层云隔开，双王在最前。弓、箭、杖、火翼、麦穗、剑都朝窗里伸，顺手盖过框线
    F.place(c, F.fade_side(F.fade_side(fig('opatos2_22'), 'left', 170), 'right', 220), 300, 110, 0.84, tint_amt=0.20, **back, **wide)
    F.place(c, F.fade_side(F.fade_side(fig('lulwyx_1'), 'right', 120), 'bottom', 200), 0, -10, 0.75, tint_amt=0.04, **back, **wide)
    F.place(c, fig('cumulus_52'), 640, 760, 0.62, tint_to=NIGHT, tint_amt=0.42, shadow=False)
    F.place(c, F.fade_side(fig('yevan_21'), 'bottom', 220), 540, 610, 0.56, tint_amt=0.10, **back, **wide)
    itz = F.fade_side(F.fade_side(F.fade_side(fig('itzpaltx_1'), 'left', 50), 'top', 50), 'bottom', 260)
    F.place(c, itz, 10, 470, 0.72, tint_amt=0.05, **back, **wide)
    F.place(c, F.fade_side(fig('ehekatl2_22'), 'bottom', 240), 310, 700, 0.58, tint_amt=0.05, **back, **wide)
    F.place(c, fig('cumulus_53'), 200, 960, 0.8, tint_to=NIGHT, tint_amt=0.36, shadow=False)
    kum = F.fade_side(erase(fig('kumiromix_1'), (0, 240, 170, 560)), 'bottom', 120)
    F.place(c, kum, -10, 720, 0.55, tint_amt=0.02, **near, **wide)
    F.place(c, F.fade_side(fig('jure_21'), 'bottom', 120), 235, 930, 0.44, tint_amt=0.02, **near, **wide)
    F.place(c, F.fade_side(fig('baltcx_1'), 'right', 70), 150, 860, 1.02, **near, **wide)
    F.place(c, fig('cumulus_51'), 760, 1500, 1.0, tint_to=NIGHT, tint_amt=0.30, shadow=False)
    F.place(c, fig('sornz_1'), -60, 1068, 1.0, **near, **wide)
    c = light_from_window(c, 'right')
    faces = [(280, 330, 420, 450), (330, 680, 470, 820), (500, 780, 640, 910), (660, 680, 800, 830), (180, 900, 300, 1020), (340, 960, 450, 1080), (300, 1380, 520, 1600), (520, 1200, 730, 1420)]
    c.alpha_composite(sparkle_layer((W, H), 7, n=64, box=(90, 120, 1250, 1900), avoid=faces))
    return c


def left_canvas(bg_png, shift):
    """左扇的底：整张画左右翻过来再往靠窗那边挪 shift，巨影站到露出来的那一段正中，外侧空出来的一条用镜像补（窄屏看不见，宽屏上压暗了）。"""
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bg = Image.open(os.path.join(P, bg_png)).convert('RGB').transpose(Image.FLIP_LEFT_RIGHT)
    s = H / bg.height
    bg = bg.resize((int(bg.width * s + 0.5), H), Image.LANCZOS)
    full = Image.new('RGB', (W, H))
    full.paste(bg, (shift, 0))
    full.paste(bg.crop((0, 0, shift, H)).transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
    c.paste(full.crop((0, 0, W - LINE, H)), (0, 0))
    return c


def left_panel():
    c = left_canvas('bg_lefa_a55.png', 170)
    wide = dict(shadow_kw=dict(blur=16, offset=(-5, 10), opacity=0.5))
    rim = dict(rim_dir=(-3, 0), rim_strength=0.6)
    # 巨手从巨影肩后伸过来，指尖越过框线；崖石的尖也伸过去，旅人站在上面举杖朝窗；紫烟只留几缕
    hand = fig('hand_63')
    al = hand.getchannel('A').filter(ImageFilter.MinFilter(3))   # 深色的手边上那圈白底收掉
    hand.putalpha(al)
    hand = F.fade_side(hand.crop((440, 0, hand.width, hand.height)), 'left', 150)
    F.place(c, hand, 937, 220, 0.68, rim_dir=(-3, 0), rim_strength=0.5, **wide)
    F.place(c, flip_x(fig('smoke_32')), 1090, 760, 0.40, **rim, **wide)
    F.place(c, erase(fig('ledge_32'), (690, 180, 930, 306)), 700, 1250, 0.62, **rim, **wide)   # 崖上原来那个小人抹掉
    F.place(c, fig('traveler_62'), 960, 1075, 0.34, rim_dir=(-3, 0), rim_strength=0.9, **wide)
    c = light_from_window(c, 'left', color=(226, 200, 255), strength=0.12)
    c.alpha_composite(sparkle_layer((W, H), 11, n=40, box=(200, 120, 1300, 1900)))
    return c


def band_sky(width, height, seed_png):
    """楣和座的底：夜空一条，左右对折。"""
    im = Image.open(os.path.join(P, seed_png)).convert('RGB')
    im = im.crop((0, 260, im.width, 260 + int(im.width * height / (width / 2)))).resize((width // 2, height), Image.LANCZOS)
    full = Image.new('RGB', (width, height))
    full.paste(im, (0, 0))
    full.paste(im.transpose(Image.FLIP_LEFT_RIGHT), (width // 2, 0))
    return full.convert('RGBA')


def top_band(ribbon=None, crest=None, rk=0.60, rx=130):
    TW, TH, Y = 3000, 504, 240   # 样式里缩到 1250×210；框上沿在 100 像素，画布上是 240
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    c.paste(band_sky(1880, Y, 'band_sky_41.png'), (560, 0))
    # 正中一枚星和金卷草，下面的光芒收短，别压字；两肩深蓝飘带，尖儿垂进窗角
    crest = crest or fig('crest_31', thin=False)
    crest = F.fade_side(crest.crop((0, 0, crest.width, 500)), 'bottom', 120)
    k = 0.74
    F.place(c, crest, (TW - int(crest.width * k)) // 2, -6, k, shadow_kw=dict(blur=8, offset=(0, 5), opacity=0.5))
    wide = dict(shadow_kw=dict(blur=12, offset=(0, 8), opacity=0.55))
    sh = ribbon or fig('navyribbon_62')
    F.place(c, sh, rx, -6, rk, **wide)
    F.place(c, flip_x(sh), TW - rx - int(sh.width * rk), -6, rk, **wide)
    return c


def safe_zone(c, box, feather=36):
    """这一块不许画压过来（页签、正文），边上软一点。box 外不动。"""
    x0, y0, x1, y1 = box
    m = Image.new('L', c.size, 255)
    ImageDraw.Draw(m).rectangle(box, fill=0)
    m = m.filter(ImageFilter.GaussianBlur(feather))
    a = np.minimum(np.asarray(c.getchannel('A')), np.asarray(m))
    c.putalpha(Image.fromarray(a))
    return c


def bottom_band(city=True, ribbon=None):
    TW, TH, Y = 3000, 552, 336   # 样式里缩到 1250×230；框下沿离底 90 像素，画布上是 336
    c = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    wide = dict(shadow_kw=dict(blur=12, offset=(0, -6), opacity=0.5))
    # 两角一层云海托着框，左边云上是阿卡迪亚；页签那一段不许压
    if city:
        F.place(c, fig('city_31'), 0, -6, 0.56, shadow=False)
    F.place(c, fig('cumulus_53'), -180, 150, 1.0, tint_to=NIGHT, tint_amt=0.40, **wide)
    F.place(c, flip_x(fig('cumulus_53')), TW - 1120 + 180, 150, 1.0, tint_to=NIGHT, tint_amt=0.40, **wide)
    sw = ribbon or fig('navyribbon_63')
    F.place(c, sw, 20, 120, 0.70, **wide)
    F.place(c, flip_x(sw), TW - 20 - int(sw.width * 0.70), 120, 0.70, **wide)
    c = safe_zone(c, (800, 0, TW - 800, Y - 2), feather=10)
    sky = band_sky(1880, TH - Y, 'band_sky_42.png')
    base = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    base.paste(sky, (560, Y))
    base.alpha_composite(c)
    return base


def main():
    want = sys.argv[1:] or ['right', 'left', 'top', 'bottom']
    jobs = dict(right=(right_panel, 'maze_right.webp'), left=(left_panel, 'maze_left.webp'), top=(top_band, 'maze_top.webp'), bottom=(bottom_band, 'maze_bottom.webp'))
    for k in want:
        fn, name = jobs[k]
        c = fn()
        c.save(os.path.join(ROOT, '_%s.png' % k))
        F.save_webp(c, os.path.join(ART, name))
        print(k, 'ok', os.path.getsize(os.path.join(ART, name)) // 1024, 'KB')


if __name__ == '__main__':
    main()
