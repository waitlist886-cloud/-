#!/usr/bin/env python3
# 山铜纪四方的拼法（11-04），照 strife_frame.py 的路子。要 PIL、numpy、scipy，用 ComfyUI 那个 venv 的 python。
#   python gpt_bronze.py [名字…]                 出图，写 out/山铜纪_11-04/
#   python bronze_collage.py                     接外侧、贴回局部重画和她们俩，写 right_r13a2.png、left5.png（连外侧）
#   python bronze_frame.py fix [名字…]            局部重画，写 fix/
#   python bronze_frame.py bake left3             把局部重画贴回去存一张 left3_fixed.png（她们俩的像素从这里来）
#   python bronze_frame.py ruin                  座外头那两段接着画，写 fix/ruin_lo、fix/ruin_ro
#   python bronze_frame.py                       拼，写 art/（bronze_left、bronze_right、bronze_top、bronze_bottom.webp）
# 尺寸的账跟迷宫纪一样：两扇画布 1400×2000，LINE 是框线；楣 3000×720（样式里 1250×300，框上沿 y=240）；座 6000×677（样式里 2500×282，框下沿离底 341）。
# 这一纪两扇不对打，各是各的群像：人不朝对面举东西，只有右扇那一道剑光和左扇散开的灰和光伸进窗里。现行的来源是 left5、right_r13a2（第六稿，见 README 第十八回末尾）。
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
ART = os.environ.get('BRONZE_ART', os.path.join(ROOT, 'art'))     # 比候选时另写一处，别盖现行的
FIX = os.path.join(ROOT, 'fix')
W, H, LINE = F.W, F.H, F.LINE
BOT_H, WIN_HALF = 677, 912
RUIN_SHIFT, RUIN_KEEP = 288, 0.34      # 座左半边往外让多少（样式 120 像素），外头那两段的图上留多少里头那一段
RUIN_R = 'ruin_r_b' if os.path.exists(os.path.join(HERE, 'out', '山铜纪_11-04', 'ruin_r_b.png')) else 'ruin_r'
K = 1.5                                # 放大 1.5 倍再缩到画布上，细节留得住
LEFT_SRC, RIGHT_SRC = 'left5', os.environ.get('BRONZE_RIGHT', 'right_r13a2')     # 第五稿：一扇一张画，bronze_collage.py 接外侧、把她们俩贴回去。更早的 left*、right* 留在 out/ 不用
FILL_L, FILL_R = (17, 18, 22), (30, 24, 52)   # 样式里的 --fm-pl、--fm-pr，超宽屏外侧补的底色
L_OUT, R_OUT = 300, 220                # 两扇外侧接出去多少（图的像素）
L_SCALE, L_TOP, L_IN = 1.08, 50, 30    # 左扇：图的 1 像素是画布多少，图顶在画布哪一行，图往外让多少（薇瑟兰的肩膀不叫框线切掉）。她的手和那枚棋要露在座上头
R_SCALE, R_TOP, R_X = 1.15, 44, 62     # 右扇：图的 x=0 在画布 R_X，王座不叫框线切掉
LIGHT = (90, 0.56)                     # 右扇那一道剑光：图的 x=0 时的 y、斜率


# 局部重画：一块一张，裁下来放大叫 GPT 只改这一样，贴回去只贴多边形里那一块，边上淡开。多边形写在图的像素上。
LOCAL = 'Image 1 is a crop from a finished illustration: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. Repaint image 1 with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size, in the same drawing style and colours, except for this one change. '
LOCAL_END = ' No text, no logo, no frame, no crescents, no moon phases.'
FIXES = {
    # 第二稿左扇。饥渊者照人物条嘴朝下；瓦尔德拉克要看得见脸和两只角（立绘 p_valdrak）；浪不要浮世绘那种爪子；薇瑟兰照山铜纪那一条是短发
    'left2': [
        dict(n='skull2', box=(0, 0, 300, 240), poly=[(40, 0), (280, 0), (290, 110), (250, 190), (160, 230), (60, 220), (20, 120)], prompt=(
            'Change only the screaming skull of the giant at the top: its head now hangs forward and down on a long thin neck of bone, bowed so low that we look at the crown and the empty eye sockets from above, and its long gaping jaw, wide open, points straight down at the ribs below it. It no longer screams upward at the sky. Same yellowed bone colour and the same flat ribbon-like layered shapes as the rest of the skeleton. Keep the rain, the ribs and the dark sky.')),
        dict(n='valdrak2', box=(590, 80, 1000, 430), refs=('p_valdrak.png',), poly=[(610, 90), (990, 90), (990, 240), (860, 300), (800, 400), (640, 400), (600, 300)], prompt=(
            'Change only the man crouching on the stone arm, using image 2 as the design of this character: his head is raised and turned toward us in three-quarter view so we can clearly see a fierce handsome face with deep grey skin like volcanic ash, a few burn scars, burning molten gold eyes and a snarl; long wild black hair blown up and back. On his head, as in image 2, one huge curving glossy black horn on one side, and on the other side a horn broken off short with glowing molten red cracks. He has just driven his long-hafted heavy blade straight down into the stone arm with both hands, shoulders hunched over it with all his weight, one knee bent high and the other leg thrust back; his black and crimson greatcoat flies upward around him like flames. Draw him in the flat style of image 1, not in the glossy style of image 2. Keep the blade in the same place, the blue-white flames along it, the stone arm, the chains and the cracked oval gold plate exactly as they are.')),
        dict(n='sea2', box=(640, 620, 1049, 1010), poly=[(640, 760), (800, 660), (1049, 640), (1049, 1010), (900, 1000), (700, 900)], prompt=(
            'Change only the sea around the woman. The water must not look like a Japanese woodblock print at all: no curling claw-shaped foam, no fingers of spray, no breaking wave with hooks. Instead the sea rises around her in huge smooth swells of deep blue water, big overlapping curved layers like painted flats on a stage, each with one thin pale line along its top edge, and a few round droplets thrown off the crests. Keep the woman exactly as she is: her face, her raised arm, her blue hair, her pearl gown, the blood and the grain of salt. Keep the rain and the grey sky.')),
    ],
    # 现行的左扇、右扇（换回头一稿动作以后）的局部修补
    'left3': [
        # 棋子顶上的十字这个世界没有
        dict(n='king2', box=(290, 1290, 440, 1480), poly=[(338, 1362), (388, 1362), (392, 1404), (334, 1404)], prompt=(
            'Change only the very top of the black chess king under the gloved fingers: remove the small cross on top of it. In its place the piece is topped by a small plain crown of dull gold with five low points, about the same size as the cross was. Keep the gloved fingers, the rest of the piece, the crimson cloth and the floor exactly as they are.')),
        # 浪底下还剩一截浮世绘的爪子
        dict(n='sea3', box=(540, 860, 820, 1050), poly=[(556, 878), (800, 878), (770, 922), (748, 948), (700, 990), (650, 1004), (580, 1004)], prompt=(
            'Change only the blue water with curling white foam: there is no curling foam at all any more. The deep blue water is one smooth swell with a thin pale line along its top edge, and at its lower left it sinks smoothly into the flat grey mist. Keep the grey stone slab, the silver hair, the brown hair and the faces exactly as they are.')),
    ],
}

# 打磨：一个人一张。crop 从哪张图裁（src），人物的立绘是 refs。贴回去的先后就是列表的先后，后贴的压先贴的
POLISH = ('Polish this one figure to a higher finish, the way a lead artist corrects an assistant\'s drawing. Keep what the figure is doing, the direction of the pose, its place in the picture and the flat cut-paper style with very fine hatching and thin coloured outlines. '
          'Correct the anatomy: a natural head size for a Japanese fantasy game character, about one sixth to one seventh of the full height, never small-headed; a real neck; shoulders that connect properly to the arms; arms of natural length and thickness with the elbow and wrist in the right places, never long thin noodles; hands drawn with care, with five clearly separated fingers gripping what they hold; a body with weight and a clear waist and pelvis; legs with knees and feet wherever they can be seen, and clothes that fall over that body. '
          'Add finer detail to the face and costume: clear eyes with iris and highlight, seams, buckles, layered cloth. Keep everything else in the crop exactly as it is, in the same place and at the same size. ')
POLISH_L = [
    dict(n='fine_selephien', src='left3', refs=('p_selephien.png',), box=(220, 20, 720, 310), poly=[(230, 300), (340, 60), (620, 20), (720, 40), (690, 140), (560, 250), (420, 280)], prompt=(
        'The figure is the winged man diving at the top: image 2 is his character design: keep its sharp handsome face, dark blue short wind-cut hair, teal eyes and black high-collared coat, in the style of image 1. He is a lean, strong young man, drawn about a fifth larger than now, diving head first in a straight line with one arm stretched forward, his body and both legs clearly readable behind him. Six uneven wings spread back from his shoulders, three on each side, dark as smoked glass at the root and turning to streaming teal light and wind at the tips. A copper bell flies from his belt. Keep the ribs and the shards.')),
    dict(n='fine_valdrak', src='left3', refs=('p_valdrak.png',), box=(570, 80, 1000, 430), poly=[(590, 90), (990, 90), (990, 240), (860, 300), (810, 410), (640, 410), (580, 300)], prompt=(
        'The figure is the man on the stone arm: image 2 is his character design: keep its fierce long face, deep grey skin, burning eyes, long wild black hair, and the horns, one huge curving glossy black horn and one broken short with glowing molten red cracks, in the style of image 1. A broad heavy man. He has come down kneeling on one knee on the stone arm with the other leg bent high, both legs clearly readable, shoulders hunched over a long-hafted heavy blade that he drives straight down with both hands, with all his weight. His black and crimson greatcoat flies upward. Keep the blade in the same place with its blue-white flames, the chains and the cracked oval gold plate.')),
    dict(n='fine_nephra', src='left3', refs=('p_nephra.png',), box=(100, 300, 410, 610), poly=[(110, 320), (240, 305), (400, 400), (400, 580), (200, 600), (110, 500)], prompt=(
        'The figure is the woman falling into the ribs, thrusting up a hand mirror: image 2 is her character design: keep its gentle face, violet eyes, long deep violet hair whose ends turn into stardust and its black and violet dress with fine chains, in the style of image 1, with no crescents. A slight adult woman; her raised arm was too long and thin. Layered veils stream around her, and the mirror bursts into long sharp shards of cold light.')),
    dict(n='fine_grom', src='left3', refs=('p_grom.png',), box=(290, 530, 790, 930), poly=[(300, 620), (390, 545), (520, 560), (640, 560), (760, 770), (780, 880), (560, 900), (420, 920), (340, 800)], prompt=(
        'The figure is the giant hauling on the chain: image 2 is his character design: keep its fierce broad face, heavy beard, wild black hair, huge bull horns with heavy metal rings and its bare chest wrapped in chains, in the style of image 1, with bronze skin crawling with bright violet lightning scars. His head was too small for his body: make it larger, roaring in three-quarter view. A mountain of a man leaning back at full strength with both feet braced on the tilted slab, both hands hauling on the chain with the chain over his shoulder. Dark purple and gold heavy plate on his arms and legs, with orichalcum chains. Keep the chain leading up to the giant pincer hand.')),
    dict(n='fine_sirentia', src='left3', refs=('p_sirentia.png',), box=(760, 600, 1049, 940), poly=[(780, 760), (840, 610), (940, 610), (1049, 660), (1049, 900), (940, 930), (820, 900)], prompt=(
        'The figure is the woman rising from the sea with one arm raised: image 2 is her character design: keep its calm beautiful face, deep blue eyes, wet deep-blue hair and coral ornament, in the style of image 1, with iridescent scales along her cheekbone and neck. Her raised arm was too long and thin: give it natural length, the palm cut open with an arc of blood going down into the water and a shining grain of salt in it. Her pearl-coloured gown is opaque, not see-through, with strings of pearls. Keep the smooth blue swells around her.')),
    dict(n='fine_lysia', src='left3', refs=('p_lysia.png',), box=(100, 650, 440, 1030), poly=[(120, 690), (200, 660), (400, 700), (430, 860), (430, 1030), (300, 1000), (180, 880), (120, 800)], prompt=(
        'The figure is the woman in crimson whirling in the air: image 2 is her character design: keep its sly smiling face, crimson eyes, long silver-white hair with a black ribbon and thorns, pointed ears and black lace gloves, in the style of image 1. Her crimson gown has a clear waist and hips under it and flares around her. Both arms are of natural length and both gloved hands grip the long thread of blood-red thorns she has stitched round the grey column. Keep the thorns, the column of cloth and the blank wax tablet.')),
    dict(n='fine_mortus', src='left3', refs=('p_mortus.png',), box=(30, 960, 450, 1370), poly=[(35, 965), (180, 960), (340, 975), (450, 1110), (400, 1200), (260, 1250), (170, 1370), (70, 1370), (120, 1180), (35, 1110)], prompt=(
        'The figure is the young man swinging the bell: image 2 is his character design: keep its gaunt handsome face, very pale skin, short black hair, amber gold eyes and black high-collared coat over white, in the style of image 1. He strides forward on a broken slab, both feet planted, and swings a heavy bronze bell on a short chain in a huge arc; his arms are of natural length. Keep the pale flakes streaming toward the bell.')),
]
# 她和老师的动作是用户点名留的，这一张只补细节：脸、头发和姿势一点不动
POLISH_L.append(dict(n='fine_pair', src='left3', box=(310, 950, 1049, 1499), poly=[(330, 1499), (320, 1290), (440, 1180), (610, 1010), (730, 950), (950, 950), (1049, 1060), (1049, 1499)], prompt=(
    'The figures are the two women at the lower right. Do not change their poses, their faces, their expressions, the fall of their hair or the size of anything: they stay exactly as they are. Only finish them more carefully: the long black glove and its five clearly separated fingers resting on the chess piece, the arm inside its sleeve with a natural elbow, the dull gold corset, chains and the crimson half-cape with its folds; the taller woman\'s scarred bare forearm and her hand with five natural fingers resting on the crimson cloth, the washed-white old army greatcoat with its burnt edges, and the flakes of pale ash and gold light drifting away from her. The chess king is topped by a small plain crown of dull gold with five low points, with no cross.')))
FIXES['left3'] = [f for f in FIXES['left3'] if f['n'] == 'sea3'] + POLISH_L


def gen_fix(names=None):
    import gpt_gen
    os.makedirs(FIX, exist_ok=True)
    for side, items in FIXES.items():
        for f in items:
            if names and f['n'] not in names:
                continue
            p = os.path.join(FIX, f['n'] + '_in.png')
            whole = Image.open(os.path.join(ROOT, f.get('src', side) + '.png')).convert('RGB')
            c = whole.crop(tuple(int(v * K) for v in f['box'])) if whole.width > 1200 else whole.crop(f['box'])   # 贴过的图已经放大过
            k = 1024 / max(c.size)
            c = c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS)
            if f.get('guide'):                   # 红线给 GPT 指位置，写在图的像素上
                x0, y0 = f['box'][:2]
                ImageDraw.Draw(c).line([((x - x0) * k, (y - y0) * k) for x, y in f['guide']], fill=(230, 30, 30), width=4)
            c.save(p)
            prompt = (POLISH + f['prompt']) if f['n'].startswith('fine_') else f['prompt']
            head = 'Image 1 is a crop from a finished illustration: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. Repaint image 1 with the same aspect ratio and the same framing. ' if f['n'].startswith('fine') else LOCAL
            print(gpt_gen.gen(os.path.join(FIX, f['n']), head + prompt + LOCAL_END, refs=[p] + [os.path.join(ROOT, 'ref', r) for r in f.get('refs', ())]), flush=True)


def big(name):
    src = Image.open(os.path.join(ROOT, name + '.png')).convert('RGB')
    im = src if src.width > 1200 else src.resize((int(src.width * K), int(src.height * K)), Image.LANCZOS)
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
    if body.width >= int((1049 + L_OUT) * K):     # bronze_collage.py 已经接好了
        return body
    out = Image.new('RGB', (body.width + E, body.height))
    out.paste(body, (E, 0))
    p = os.path.join(FIX, LEFT_SRC + '_out.png')
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
    if body.width >= int((1049 + R_OUT) * K):     # bronze_collage.py 已经接好了
        return body
    wide = Image.new('RGB', (body.width + O, body.height))
    wide.paste(body, (0, 0))
    p = os.path.join(FIX, RIGHT_SRC + '_out.png')
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
    # 伸进窗里的只有那一道剑光：照画上那条线的方向接着画，越往窗里越淡（LIGHT 是图的像素：x=0 时的 y、斜率）
    xs = np.arange(LINE, dtype=np.float32)
    ys = R_TOP + R_SCALE * (LIGHT[0] + LIGHT[1] * (xs - R_X) / R_SCALE)
    dist = np.abs(np.arange(H, dtype=np.float32)[:, None] - ys[None, :])
    core = np.clip(1 - dist / 5, 0, 1)
    glow = np.clip(1 - dist / 15, 0, 1) ** 2
    fade = np.clip(xs / LINE, 0, 1)[None, :]
    k = core[..., None]
    a[:, :LINE, :3] = k * np.array((255, 240, 196), np.float32) + (1 - k) * np.array((255, 150, 44), np.float32)
    a[:, :LINE, 3] = np.maximum(core, glow * 0.7) * fade * 255
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
    blend('ruin_lo', x0 - (wide - keep), wide - keep + 70, 'left')      # 到里头那一段的边上还是满的，从那里才淡开，不然那条边露出来是一道竖线
    r = put(RUIN_R, left=TW // 2)
    blend('ruin_ro', r[1] - keep, keep - 70, 'right')
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
    if sys.argv[1:2] == ['fix']:
        gen_fix(sys.argv[2:])
    elif sys.argv[1:2] == ['bake']:          # 把局部重画贴回去存一张，给下一步当底：bake left3 写 left3_fixed.png
        big(sys.argv[2]).save(os.path.join(ROOT, sys.argv[2] + '_fixed.png'))
    elif sys.argv[1:2] == ['ruin']:
        gen_ruin()
    else:
        write(to_fill(left_panel(), 'left', FILL_L), to_fill(right_panel(), 'right', FILL_R), top_band(), bottom_band())
