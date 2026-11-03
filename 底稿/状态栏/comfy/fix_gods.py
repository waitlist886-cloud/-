#!/usr/bin/env python3
# 修右扇四位七神（用户 11-03：朱亚、库米罗妮、艾赫卡托尔、欧巴德斯）。长相照底卡 #87、#89、#90、#91 的显相和神器，底卡没写的照 Elona 官方立绘。
# 一位一张：从 pv/right_f6.png 裁这一位那一块，放大，叫 GPT 只改这一位，别的照旧，输出在 pv/gods/。贴回去的事在 compose 里，双王的头还是最后才盖。
#   python fix_gods.py gen [名字…]     出图，已有的不重出
#   python fix_gods.py                 拼 pv/right_f7.png，再跑 gpt_prepare.py pv_ab、cut_cpu.py（前缀 r_f7）、maze1001_frame_pv.py
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8')
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage, optimize
import gpt_gen
import fix_queens

P = os.path.join(HERE, 'out', '四方_11-03', 'pv')
G = os.path.join(P, 'gods')

COMMON = ('Image 1 is a crop from a finished illustration: a crowd of gods in side profile facing left, overlapping in layers like a relief. Repaint image 1 with aspect ratio {ratio}, same framing, keeping everything exactly as it is, in the same place and at the same size: the other figures and their faces, hands, weapons, hair, wings, the ribbons, the clouds and the background. Change only the one figure described here. ')
KEEP_STYLE = (' Draw the new parts in the drawing style of image 1: flat cut-paper shapes with smooth colour, fine parallel hatching and dry-brush chalk grain inside the colour areas, thin pale or coloured outlines, matte, with the same soft violet light over everything. '
              'Draw the face the way the other faces in image 1 are drawn: slender almond eye with fine lashes, thin eyebrow, small straight nose, tiny mouth, soft jaw. '
              'No glossy shading, no sparkles, no floating gold dust, no 3D look, no black outlines, no text, no logo, no frame, no crescents, no moon phases.')

GODS = {
    # 底卡 #87：半身不朽的石躯，翼硬得像山脉一层叠一层的鳞，神器大地之锤，温和又好战。Elona：黑长发，赤膊。Elin：红铁色的眼
    'opatos': dict(box=(430, 0, 1330, 600), ratio='3:2', faces=True, prompt=(
        'The figure to change is the huge man in the middle, in side profile facing left, whose whole body and wing are now drawn as faceted pale stone polygons. Redraw him as the god of earth: a giant, broad and heavy, at the same size and position, in the same side profile facing left, with the same gold collar and round gold ring on his chest. '
        'Face: a living human face with warm bronze skin and a small calm confident smile, gentle and ready for a fight at the same time. Image 2 is a sheet of close-ups of other faces from the same picture: draw his face by the same hand, a handsome Japanese fantasy game face with long slender eyes in red-iron colour, fine lashes, a thin straight nose and a clean soft jawline, strong but not angular, never a western comic book face. '
        'Hair: long, thick, wild black hair with a dark blue sheen, in big sweeping ribbon shapes streaming to the right behind him, instead of the spiky stone hair. '
        'Body: bare-chested and muscular. The front half of his chest and his neck are warm bronze skin. The rest of his torso, his shoulder and his upper arm are rough immortal granite, grey violet, with thin ember-gold seams in the cracks. The border between skin and stone is one jagged irregular line running from under his jaw, down his neck and across his chest. '
        'Wing: one huge wing at his back, in the same place and as large as the present wing, rising up and to the right. It is hard, with no feathers: rows of overlapping slate scales, the upper edge of every row a jagged mountain ridge, like mountain ranges layered one above another, large near the shoulder and tapering to sharp tips, in umber and slate grey with pale gold along the ridge lines. '
        'Hammer: over his shoulder rests a colossal war hammer, the great earth hammer. His huge hand grips the long dark shaft bound with gold rings low in front of his chest, the shaft runs up past his shoulder, and the massive square head of dark iron stone with gold bands sits behind his neck, in front of the wing. '
        'Keep unchanged: the archer with her white feathered wing at the left, the long blonde hair strands that flow across the lower part of his body, the large pale disc behind him, the long ribbons crossing the sky and the clouds.')),
    # 底卡 #90：猫影、金铃、一枚带笑的硬币，神器幸运之首（底卡没写样子，照 Elona 的幸运匕首画把小匕首），神仆黑猫，轻快爱开玩笑。Elona：金色波浪长发，蓝眼，白裙
    'ehekatl': dict(box=(420, 690, 880, 1150), ratio='1:1', prompt=(
        'The figure to change is the woman with long blonde hair in the middle, with the small black cat on her shoulder. Keep her position, her size, her side profile facing left and her long flowing hair. Redraw her as the goddess of luck, light and mischievous. '
        'Face: a sly cheerful closed-mouth smile with the corner of the mouth turned up, one thin eyebrow lifted, big bright sky blue eyes instead of amber. '
        'Hair: long wavy pale golden hair as now. Remove the big flower. Instead a small black ribbon with one small round gold bell is tied at the side of her head. '
        'Cat: the same small black cat sits on her shoulder in the same place, now with a small round gold bell on its collar, looking up at the coin. '
        'Hand and coin: her front hand comes up in front of her chest with the thumb just flicked, and one large gold coin spins in the air above the hand, right in front of her face, tilted toward us so that we see a simple engraved smiling face on it, just two dots and a curve. The coin is big and clear, as wide as the distance from her eye to her chin. She is watching it. '
        'Dress: replace the stiff faceted white and gold armour-like drape with a soft light white dress with thin gold trim, in big flowing cut-paper shapes, with a slim gold-hilted dagger tucked into her sash at the waist. '
        'Keep unchanged: the faceted blue ice-crystal wing behind her, the crimson coat at the left, the white hooded figure at the right, the green-haired woman at the lower left and the big pale ribbon across the lower right.')),
    # 底卡 #89：一百四十二公分，幼小的鹿角，藤叶缠身，头顶一圈种子的光，神器库米罗妮的镰刀，样子小、说话不幼稚，不写成卖萌的幼女神
    'kumiromi': dict(box=(10, 880, 490, 1360), ratio='1:1', prompt=(
        'The figure to change is the goddess holding the wheat sheaf, with brown hair, flowers and big antlers. Redraw her as the goddess of harvest: a small slight person, the smallest figure in the picture, but still close in scale to the green-haired woman beside her: her head is about nine tenths of its present size and the top of her hair is about one fifth of the way down the picture, with her shoulders a little lower than now, in the same side profile facing left. She fills the space between the wheat and the green-haired woman. She is not a cute child: a young face with a quiet, old, kind gaze. '
        'Hair: short wheat-gold hair, chin length, with one small braid. Remove the flowers and the big bun. '
        'Antlers: a pair of small young antlers, short and just budding, one small fork each, pale like new wood. Remove the big branching antlers completely. '
        'Above her head: one thin flat ring of about a dozen small softly glowing golden seeds, floating like a halo. '
        'Clothes: a simple moss green tunic over a pale linen shift. Living green vines with small leaves wrap around her arms, her shoulders and her waist. '
        'Scythe: a long slender shaft wound with a green vine leans against her far shoulder, slanting up and to the left behind her head; at its top, above her head and above the ring of seeds, a pale steel curved scythe blade with a thin gold edge sweeps forward to the left, clear of her face and clear of the wheat. '
        'Keep the wheat sheaf and the raised hand holding it exactly as they are, in the same place and at the same size. '
        'Keep unchanged: the gold staff behind the wheat, the black gloved hand and gold sword hilt at the lower left, the crimson coat behind her, the orange flames at the top left, the green-haired woman at the right with her praying hands.')),
    # 底卡 #91：一百五十一公分，翠玉色的眼，头顶一对细小的羽翼，落下来的羽毛当圣物，神器圣枪，温柔也坚定。Elona：绿色波浪长发，粉白长袍
    'jure': dict(box=(250, 930, 770, 1450), ratio='1:1', prompt=(
        'The figure to change is the green-haired woman with praying hands in the middle. Keep her position, her size, her side profile facing left and her praying hands in the same place. Redraw her as the goddess of healing, gentle and firm. '
        'Eyes: clear jade green eyes, calm, lifted a little. '
        'Hair: long soft wavy spring green hair, falling behind her shoulders to her waist in big smooth ribbon shapes, instead of the short curls. '
        'Head wings: on the very top of her head a pair of tiny white feathered wings rises from her hair, each no bigger than her hand, small living wings, not an ornament and not gold. Remove the orange leaf ornament at the side of her head. '
        'Clothes: the long robe and the wide cape are white and soft rose pink, in the same big flat fan-shaped folds as the present cape, with the sage green stripes turned to rose pink. Keep the gold four-pointed star on the cape. '
        'Lance: her two praying hands close around the slim shaft of a holy lance held upright just in front of her face: a long thin white and rose-gold shaft rising straight up past her forehead to a leaf-shaped rose-gold spearhead at the top, and going down behind her hands into the cape. It is thin and does not hide her face. '
        'Feathers: five or six small white feathers drift down around her, past her hands and over the cape. '
        'Keep unchanged: the small woman behind at the left, the blonde woman behind at the upper right, the silver-haired queen at the lower right with her bangs, braid, pointed ear and forehead mark, the gold crown at the bottom and the red crystal scepter.')),
}


# 出好的图上再改一处：名字 → （底图, 提示词）
EDITS = {
    # a 上的硬币太像表情符号，b 是古币上一张写实的笑脸，太重；c 是一张带笑的猫脸，接猫神和猫影
    'ehekatl_b': ('ehekatl_a', 'Change only the gold coin in the air above the raised hand. Its face must not look like a modern emoji or smiley. Make it a worn antique gold coin with a raised rim of small beads, tilted in the air, struck with a small laughing face in low relief, like the head on an old Greek coin: narrowed merry eyes, round cheeks and an open grin, drawn with fine engraved lines in darker gold. Same size and same place as the present coin.'),
    'ehekatl_c': ('ehekatl_a', 'Change only the gold coin in the air above the raised hand. Its face must not look like a modern emoji or smiley. Make it an old gold coin with a raised rim of small beads, tilted in the air, struck with the simple flat emblem of a grinning cat face: two pointed ears, two narrow curved eyes and one wide curved smile, drawn with a few fine engraved lines in darker gold. Same size and same place as the present coin.'),
}
EDIT_TAIL = ' Same drawing style as image 1, flat cut-paper shapes with fine hatching, matte. No text, no logo, no frame.'
FACES = [(290, 640, 400, 750), (770, 650, 870, 750), (290, 290, 370, 370), (420, 975, 520, 1075)]   # 伊兹帕鲁特、耶万、璐璐薇、朱亚


def faces_sheet():
    out = os.path.join(G, '_faces.png')
    src = Image.open(os.path.join(P, 'right_f6.png')).convert('RGB')
    C = 500
    s = Image.new('RGB', (C * 2 + 8, C * 2 + 8), (24, 22, 56))
    for i, b in enumerate(FACES):
        im = src.crop(b)
        im = im.resize((C, round(im.height * C / im.width)), Image.LANCZOS)
        s.paste(im, (i % 2 * (C + 8), i // 2 * (C + 8)))
    s.save(out)
    return out


def crop(name):
    """这一位那一块放大到一千二上下，给 GPT 看。"""
    x0, y0, x1, y1 = GODS[name]['box']
    out = os.path.join(G, f'crop_{name}.png')
    c = Image.open(os.path.join(P, 'right_f6.png')).convert('RGB').crop((x0, y0, x1, y1))
    k = 1254 / max(c.size)
    c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS).save(out)
    return out


def gen_one(stem, name):
    if stem in EDITS:
        base, what = EDITS[stem]
        return gpt_gen.gen(os.path.join(G, stem), 'Image 1 is a finished picture. Repaint it with aspect ratio 1:1, keeping everything exactly the same: every figure, face, hand, hair strand, colour and the whole layout. ' + what + EDIT_TAIL, refs=[os.path.join(G, base + '.png')])
    g = GODS[name]
    refs = [crop(name)] + ([faces_sheet()] if g.get('faces') else [])
    return gpt_gen.gen(os.path.join(G, stem), COMMON.format(ratio=g['ratio']) + g['prompt'] + KEEP_STYLE, refs=refs)


def fit(name, ver):
    """GPT 出的图对回画布：只看没改的地方，搜缩放和平移，再把色调拉回去。回和裁框一样大的 RGB（画布比例）。"""
    x0, y0, x1, y1 = GODS[name]['box']
    w, h = x1 - x0, y1 - y0
    ref = np.asarray(Image.open(os.path.join(P, 'right_f6.png')).convert('RGB').crop((x0, y0, x1, y1))).astype(np.float32)
    src = Image.open(os.path.join(G, f'{name}_{ver}.png')).convert('RGB')
    S = 2   # 先留两倍，变换完再缩，线条不发虚
    big = np.asarray(src.resize((w * S, h * S), Image.LANCZOS)).astype(np.float32)
    small = ndimage.gaussian_filter(big.mean(axis=2), 2)[::S * 2, ::S * 2]
    target = ndimage.gaussian_filter(ref.mean(axis=2), 1)[::2, ::2]
    target = target[:small.shape[0], :small.shape[1]]
    small = small[:target.shape[0], :target.shape[1]]

    def warp(v):
        ax, ay, bx, by = v
        return ndimage.affine_transform(small, (ay, ax), offset=(by, bx), order=1, mode='nearest')

    def cost(v):
        return float(np.minimum(np.abs(warp(v) - target), 22).mean())   # 改过的地方差多大都按同一个数算，不牵着走

    best = min(((cost((1, 1, dx, dy)), dx, dy) for dx in range(-8, 9, 2) for dy in range(-8, 9, 2)))
    r = optimize.minimize(cost, (1, 1, best[1], best[2]), method='Powell', options={'xtol': 1e-3, 'ftol': 1e-4})
    ax, ay, bx, by = r.x
    # small 的一格是画布两像素：换算到 S 倍的大图
    mat = (ay, ax)
    off = (by * S * 2 * 1.0, bx * S * 2 * 1.0)
    chans = [ndimage.affine_transform(big[..., c], mat, offset=off, order=3, mode='nearest') for c in range(3)]
    im = Image.fromarray(np.uint8(np.clip(np.dstack(chans), 0, 255))).resize((w, h), Image.LANCZOS)
    out = np.asarray(im).astype(np.float32)
    same = np.abs(out - ref).sum(axis=2) < 36
    tone = []
    for c in range(3):
        k, b = np.polyfit(out[..., c][same], ref[..., c][same], 1)
        out[..., c] = out[..., c] * k + b
        tone.append((round(float(k), 3), round(float(b), 1)))
    print(name, ver, 'fit', [round(float(x), 4) for x in r.x], 'cost', round(cost(r.x), 2), 'same', round(float(same.mean()), 3), 'tone', tone, flush=True)
    return Image.fromarray(np.uint8(np.clip(out, 0, 255)))


# 贴回去。GPT 没动的地方跟 f6 几乎逐像素一样，所以这一位的范围直接按“哪里变了”算，交界落在没变的地方就看不出来。
# 坐标都是画布的。within：变了的地方只认这里头，take：这里头整块用新图（take_blur 是边上的软度），fade：同 take，边上很软、不出 within，over：这里头换成另一张的，tint：这里头偏暗的像素乘一个色。
# 先后是从后往前：欧巴德斯、艾赫卡托尔、库米罗妮、朱亚，双王的头最后盖。
# 用的哪一张：欧巴德斯 b（a 的脸太硬，像西方漫画），库米罗妮 a（b 的眼睛大，偏幼），艾赫卡托尔 a 加 c 的硬币，朱亚 a。
LAYERS = [
    # 天上的色调两张差一点，不框住会连着远处的天一起换
    dict(name='opatos', ver='b',
         within=[[(520, 90), (800, 40), (1060, 90), (1240, 260), (1240, 420), (1000, 520), (800, 570), (640, 600), (500, 600), (490, 350)]],
         tint=[((0.8, 0.45, 0.4), [(568, 212), (575, 211), (576, 218), (569, 219)])]),   # Elin 写的红铁色的眼，新图画成了琥珀色
    dict(name='ehekatl', ver='a',
         over=[('c', [(470, 800), (482, 793), (500, 800), (516, 828), (514, 846), (500, 848), (486, 838), (472, 815)])]),   # 硬币照 c
    # 麦穗到朱亚之间整块用新图，新图里这一片的紫跟 f6 不是一个深浅；朱亚的手和披风的白边两边一样，交界落在那上头
    dict(name='kumiromi', ver='a',
         take=[[(12, 905), (395, 905), (398, 960), (402, 1040), (398, 1100), (378, 1130), (372, 1170), (358, 1178), (338, 1208), (315, 1252), (300, 1272), (268, 1312), (222, 1342), (186, 1360), (178, 1330), (165, 1290), (150, 1240), (130, 1150), (70, 1090), (12, 1090)]],
         take_blur=2.5),
    # 朱亚这张是在旧的库米罗妮前头画的：左边照旧头发和裙子的边切开，那颗落在旧裙子上的羽毛不要。脸前那一条紫整块用这张，旧脸的位置比新脸靠左下
    dict(name='jure', ver='a',
         within=[[(378, 925), (378, 955), (374, 970), (369, 989), (375, 1007), (370, 1013), (370, 1018), (375, 1023), (375, 1030), (347, 1030), (345, 1054), (375, 1054), (375, 1100), (366, 1108), (360, 1135), (359, 1165), (361, 1170), (341, 1192), (324, 1212), (308, 1235), (296, 1253), (285, 1268), (285, 1450), (770, 1450), (770, 930)]],
         take=[[(374, 945), (374, 990), (366, 1004), (362, 1020), (362, 1045), (368, 1060), (375, 1068), (376, 1094), (377, 1108), (392, 1108), (405, 1040), (398, 985), (420, 950)]],
         take_blur=1.5,
         fade=[(14, [(300, 1290), (420, 1200), (600, 1180), (600, 1415), (300, 1415)])]),   # 披风下摆的浅紫两张深浅不一，按“变了”切会一块一块的，这一片慢慢过渡
]
HI, LO, MIN = 42, 22, 60


def changed(new, ref):
    """new、ref 是一样大的 RGB 数组。回 bool：这一位变过的地方。细的东西（枪杆、藤、刀尖）从大块上长出去。"""
    d = ndimage.gaussian_filter(np.abs(new - ref).max(axis=2), 0.8)
    core = ndimage.binary_opening(d > HI, iterations=2)
    lab, n = ndimage.label(core)
    if n:
        sizes = ndimage.sum(core, lab, np.arange(1, n + 1))
        core = np.isin(lab, 1 + np.nonzero(sizes >= MIN)[0])
    grown = ndimage.binary_propagation(core, mask=d > LO)
    grown = ndimage.binary_closing(grown, iterations=4)
    return ndimage.binary_fill_holes(grown)


def poly(size, polys):
    S = 2
    m = Image.new('L', (size[0] * S, size[1] * S), 0)
    dr = ImageDraw.Draw(m)
    for pts in polys:
        dr.polygon([(x * S, y * S) for x, y in pts], fill=255)
    return np.asarray(m.resize(size, Image.LANCZOS)) > 127


def soft(size, polys, blur):
    m = poly(size, polys).astype(np.float32)
    return ndimage.gaussian_filter(m, blur) if blur else m


def layer(L):
    name = L['name']
    x0, y0, x1, y1 = GODS[name]['box']
    w, h = x1 - x0, y1 - y0
    shift = lambda polys: [[(px - x0, py - y0) for px, py in pts] for pts in polys]
    new = fit(name, L['ver'])
    ref = Image.open(os.path.join(P, 'right_f6.png')).convert('RGB').crop((x0, y0, x1, y1))
    a, b = np.asarray(new).astype(np.float32), np.asarray(ref).astype(np.float32)
    m = changed(a, b)
    if L.get('within'):
        m &= poly((w, h), shift(L['within']))
    al = ndimage.gaussian_filter(m.astype(np.float32), 0.9)
    if L.get('take'):
        al = np.maximum(al, soft((w, h), shift(L['take']), L.get('take_blur', 1)))
    for blur, pts in L.get('fade', []):
        al = np.maximum(al, soft((w, h), shift([pts]), blur) * soft((w, h), shift(L['within']), 0.9))
    for ver, pts in L.get('over', []):
        o = np.asarray(fit(name, ver)).astype(np.float32)
        k = soft((w, h), shift([pts]), 1.2)[..., None]
        a = a * (1 - k) + o * k
    for gain, pts in L.get('tint', []):
        k = soft((w, h), shift([pts]), 0.8) * np.clip((160 - a[..., 1]) / 30, 0, 1)   # 只染瞳孔，皮肤和眼白比它亮
        a = a * (1 - k[..., None]) + a * np.array(gain, np.float32) * k[..., None]
    rgba = np.dstack([a, al * 255])
    out = Image.new('RGBA', (fix_queens.W, fix_queens.H), (0, 0, 0, 0))
    out.paste(Image.fromarray(np.uint8(np.clip(rgba, 0, 255)), 'RGBA'), (x0, y0))
    return out


def apply_gods(base):
    for L in LAYERS:
        base.alpha_composite(layer(L))
    return base


if __name__ == '__main__':
    os.makedirs(G, exist_ok=True)
    if sys.argv[1:2] == ['gen']:
        # 名字后头可以带版本：opatos、opatos:b。出 pv/gods/opatos_a.png、opatos_b.png
        jobs = [(a.split(':') + ['a'])[:2] for a in (sys.argv[2:] or GODS)]
        with ThreadPoolExecutor(4) as ex:
            fs = {f'{n}_{v}': ex.submit(gen_one, f'{n}_{v}', n) for n, v in jobs}
            for k, f in fs.items():
                print(k, f.result(), flush=True)
        print('done')
    else:
        c = fix_queens.compose(under=apply_gods)
        c.save(os.path.join(P, 'right_f7.png'))
        print('ok', c.size)
