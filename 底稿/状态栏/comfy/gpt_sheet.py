#!/usr/bin/env python3
# 角色立绘（第三版，设定图）。用户 11-05 定的：四套衣服一张图一次出，切开用，人才是同一个；表情另出一张。写法试出来的经过见 立绘画法.md 第十三节。
# 这是卡里来回切换的差分，不是设定稿。用户定的：面相、镜头、身形基本一样，都看镜头；姿势和手里的东西随衣服轻微变，私服放松，战斗装持自己的武器、绷紧，正装端庄。
# 一位三张，先后不能乱：
#   sheet  四套衣服（常服、私服、战斗、正装）横版一张，切成 cell_casual/private/battle/formal.png，一格 640×960（cast_slice.py）
#   art    艺术照，参考是官方艺术卡加切好的常服
#   faces  九格表情，参考是切好的常服和放大的头
# 这个人有第二版的常服（out/立绘_v2/<en>/casual.png），拿它当最后一张参考定手法和长相，腿不照它；没有就用现有立绘裁的头。
# 四个人碰在一起切不开的话换个说法重出一回，再不行报失败，不硬切。
# 图写 out/立绘_v3/<en>/，已有的不重出。未成年那一档（minor）不在这里出，资料里写了 young_ok 的除外（希尔妲、芙莉莲，看着十五到十七的老传奇）：
#   参考只用不露肤的几张，不写身段，穿戴整齐，艺术照只到头肩。
#   python gpt_sheet.py eleanor kamelika   出这几位缺的
#   python gpt_sheet.py --all              全员
#   python gpt_sheet.py --list             列谁缺什么
# 环境变量 CAST_WORKERS 改同时跑几张，默认 3。
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cast_slice as CS
import gpt_cast as G
import gpt_gen
from PIL import Image

OUT = os.environ.get('SHEET_OUT') or os.path.join(HERE, 'out', '立绘_v3')   # SHEET_OUT 改输出目录，SHEET_ONLY=1 只出设定图，SHEET_STRICT=1 双臂下垂、手里不拿东西
LEGS = {
    'woman': ("LEGS, the most important point, follow the standing adult woman in the first attached picture: a high waist and a short torso; measured from the top of the head to the sole, the crotch sits at 47 percent of the height, so the legs are longer than the head and torso together; the knee at 68 percent; the lower leg clearly longer than the thigh. Even under a long skirt the hips sit that high. The legs are NOT crossed; the weight on one leg, the other knee a little relaxed. Tall boots stop a hand below the knee. "),
    'man': ("LEGS: long legs and a short torso: measured from the top of the head to the sole, the crotch sits at 48 percent of the height and the knee at 69 percent. The legs are NOT crossed; the weight on one leg. "),
    'small': '',
}
LEGS['burly'] = LEGS['man']
LEGS['girl'] = ''   # 年少模样的不写腿和身段
LEGS['youth'] = LEGS['man']
# 十九岁模样、软乎乎不习武的年轻男人（霍布）
G.BODY['youth'] = ('BODY: a young man of about nineteen with the proportions of the younger adult male characters of that game: about 7 heads tall, a little short and soft, rounded relaxed shoulders, NOT muscular and NOT trained, but clearly a grown young man and NOT a child. A lazy, easy stance, the weight sunk on one leg; hands drawn with care. ')
YOUNG = ' The character looks like a teenager: draw a youthful, wholesome, fully covered look, nothing about the body emphasised, nothing suggestive.'
SHEET = ('A character design sheet on one wide picture: FOUR full-body standing figures of this one character in a single horizontal row, in four different outfits. All four are exactly the same person: the same face, the same eyes, the same height and build, the same head size. '
         'Draw each figure as its own finished character sprite, with the same care as a full-page illustration: a crisp thin line, sharp almond eyes, every lock of hair a clean ribbon shape, never a mass of small wavy strands, even at this size. '
         'These are outfit variations of one game sprite for a visual novel, swapped in the same spot on screen, so the face and camera stay the same: in all four the same very slight three-quarter turn of the body, the same head size and height, the face toward the viewer and the eyes looking straight into the camera, the same overall build. Within that, the body language changes a little to suit each outfit, a slight adjustment and not a new pose: '
         '1) the everyday outfit: this character\'s natural, easy standing pose, holding their usual small item if they have one. '
         '2) the private outfit: more relaxed, the shoulders loose and lowered, the weight settled on one leg, a soft expression, the hands loosely holding a small personal object or simply at rest. '
         '3) the battle outfit: tense and ready, the shoulders squared, the feet a little wider and planted, a firm expression, gripping this character\'s own weapon in the hand or hands, kept close to the body. '
         '4) the formal outfit: dignified and very upright, the back straight, the feet close together, the hands composed in front or at the sides, a serene expression. '
         'Everyone stands: no chair, no throne, no furniture. Nothing rises higher than the top of the head: a long staff or spear is held low or at an angle. '
         'The air is almost still: the hair and loose cloth hang naturally with a slight lift, staying inside each figure\'s own quarter of the picture and never touching the neighbouring figure: there is always a clear empty gap between figures. '
         'Every figure is complete from the top of the head to the soles of the feet, the feet all on one level, the heads all at one height, filling the full height of the picture. Even light, no dramatic shadow. '
         'Fully clothed, modest, not sexualized. Transparent background: no floor, no cast shadow. No text, no labels, no numbers, no frame, no dividing lines. Landscape picture, aspect ratio 3:2. ')
STRICT = ('Stricter still: in all four figures both arms hang straight down, relaxed at the sides, in exactly the same position, the hands empty and open. Nothing is held in the hands: any staff, flower, food, bag, cloak, tool or rope in the descriptions is left out or hung from the belt; a weapon is worn at the hip or carried on the back. Ignore the pose in the LAST attached picture. Laid over one another, the four figures would match at the head, shoulders, arms, hips and feet, and differ only in clothes. ')
RETRY = 'Leave much wider empty gaps between the figures this time and keep every sword, staff, cape and lock of hair well inside its own quarter. '
B3 = "3) the battle outfit: tense and ready, the shoulders squared, the feet a little wider and planted, a firm expression, gripping this character's own weapon in the hand or hands, kept close to the body. "   # 第三格那一句，资料里有 battle_pose 的换掉
assert B3 in SHEET
FACES = G.FACES.replace('The attached picture shows this character:', 'The attached pictures show this character, full figure and a close-up of the head:')
CELLS = ('casual', 'private', 'battle', 'formal')
# 艺术照走过三回（立绘画法.md 第十七节）：头一回整张一个色相、硬影压脸，人认不出；第二回照立绘但素了，用户要回看官方；这一回官方的力度拿回来，眼睛那一块不压影子，颜色是这个人自己的。
ART = ('Draw in the rendering of the attached official key art from Honkai: Star Rail, for style only: do not copy their characters, costumes or props. The LAST attached picture is this exact character: the same face, eye shape, eye colour, hair colour, hairstyle and outfit, instantly recognisable as that sprite. '
       'A dramatic promotional art portrait, the same kind of picture as the references: a close crop with the camera tilted on a diagonal, the face large and off-centre, the figure cut off by the frame, long locks of hair sweeping across the picture in big clean shapes. '
       'Luminous, high-key colour: one strong directional light in %s floods in from one side, the highlights bloom softly toward white on the hair and shoulder, the shadow side of the skin and hair takes a saturated tint of the palette. Razor-sharp shadow shapes cast by foreground things fall across the hair, neck and clothes and the far edge of the cheek, but the whole eye area stays clear, lit and beautifully detailed: the eyes are the brightest focal point, with a glowing gradient iris. '
       'Large out-of-focus foreground shapes that belong to this character drift across the corners of the frame; the background is soft glowing colour and bokeh, not a detailed scene. Thin crisp line art in a darker tint of each local colour, smooth skin with very simple shading. The hair, eye and clothing colours stay recognisably the character\'s own. Fully clothed, not sexualized. No text, no logo, no frame. Portrait picture, aspect ratio 2:3. ')
ART_END = ' Whatever is said above, no shadow crosses the eyes: a shadow on the face stays at the far edge of the cheek or below the eyes.'
# 用户 11-05 和底卡 #490：跨进传奇就不再老了，几千年也还是凝名那时的样子，多出来的是眼神。
OLD_EYES = 'This character has lived for a very long time without ageing: the face stays as it is, and only the eyes carry the weight of those years, calm and deep. '
NOT_LEGEND = ('eleanor', 'tifa', 'kamelika', 'alice', 'sisne')


# cast/覆盖.json：按人补的。who 换整段；face 换掉通用的脸（要看现有立绘和原型的人，比如爱丽丝）；ref_head 用现有立绘的头当最后一张参考，不用第二版常服；build 是档案有体态数据的成年人的身材（只有五位）；art_close 艺术照只到头肩
for _k, _v in json.load(open(os.path.join(HERE, 'cast', '覆盖.json'), encoding='utf-8')).items():
    G.CAST[_k].update(_v)


def d(k):
    return os.path.join(OUT, k)


def tier(c):
    return c.get('tier') or ('man' if c.get('sex') == 'm' else 'woman')


def young(c):
    return c.get('tier') == 'girl' or bool(c.get('minor'))


def style_refs(c):
    if young(c):   # 不露肤的几张
        return G.lc('firefly_top', 'huohuo') + G.card('saifei')
    if c.get('sex') == 'm':
        return G.lc('jingyuan', 'anaxa', 'lance_full')
    return G.lc('himeko_stand', 'aglaea_stand', 'guinaifen')


def sheet_prompt(k, extra=''):
    c = G.CAST[k]
    t = tier(c)
    face = c.get('face') or G.FACE['man' if c.get('sex') == 'm' else t]
    spec = G.BODY[t] + LEGS[t] + c.get('build', '') + G.HAIR + face + G.REST + c['who'] + ' '
    outfits = 'From left to right: 1) ' + c['casual'] + ' 2) ' + c['private'] + ' 3) ' + c['battle'] + ' 4) ' + c['formal'] + ' '
    v2 = G.path(k, 'casual')
    # anchor：没有自己旧图的新人，垫一张同一套画法的成品（别人的常服），只取画法，画法稳一些；体型差得远的别垫，会被带过去（霍布垫卢米安被带高带瘦，11-05）
    anc = [os.path.join(os.path.dirname(OUT), c['anchor'])] if c.get('anchor') else []
    anc_lead = ('The %s attached picture is a finished sprite from this same set, of a DIFFERENT character: match its rendering exactly, the thin warm-brown line, the clean colouring with soft gradients, the light shading and the transparent background, but take nothing else from it: not the face, hair, eyes, body, clothes or pose. ')
    if c.get('refs'):   # 用户给了这个人的图，就照用户的图
        last = [os.path.join(G.REF, 'old', r) for r in c['refs']]
        lead = 'The LAST %d attached pictures show this exact character: follow their face, build, hair and clothing design closely; ignore their rendering and background. ' % len(last)
        return G.LC + lead + G.BODY[t] + LEGS[t] + c.get('build', '') + G.HAIR + face + G.REST + c['who'] + ' ' + outfits + SHEET + (STRICT if os.environ.get('SHEET_STRICT') else '') + extra + (YOUNG if young(c) else ''), style_refs(c)[:2] + last
    if os.path.exists(v2) and not c.get('ref_head'):
        last = [v2]
        lead = 'The LAST attached picture shows this exact character: copy its face, eyes, hair colour, hair ornaments and way of drawing, but NOT its leg proportions. '
    else:
        last = (G.EXTRA.get(k) or G.head_of(k))[:1]
        lead = 'The LAST attached picture shows this exact character: keep the face shape, hair colour, hair style, eye colour and hair ornaments; ignore its background and its heavy glossy rendering. ' if last else ''
        if anc:
            lead = anc_lead % ('second-to-last' if last else 'LAST') + lead
            last = anc + last
    sheet = SHEET.replace('sharp almond eyes, ', 'the eyes exactly as described, ') if c.get('face') else SHEET
    if c.get('battle_pose'):   # 第三格换一句：霍布不打仗、扛粮不拿兵器，希尔妲握短火把
        sheet = sheet.replace(B3, c['battle_pose'])
    tail = YOUNG if young(c) else ''
    return G.LC + lead + spec + outfits + sheet + (STRICT if os.environ.get('SHEET_STRICT') else '') + extra + tail, style_refs(c) + last


def make_cells(k, src):
    figs = CS.figures(CS.clean(Image.open(src)))
    if figs is None:
        return False
    for name, f in zip(CELLS, CS.cells(figs)[0]):
        f.save(os.path.join(d(k), 'cell_' + name + '.png'))
    cell = Image.open(os.path.join(d(k), 'cell_casual.png'))
    bb = cell.getchannel('A').getbbox()
    h = bb[3] - bb[1]
    # 放大的头给表情当参考：竖着取上面 22%，横着按头的位置取透明通道最靠上那一段的中心
    a = cell.getchannel('A').crop((0, bb[1], cell.width, bb[1] + h // 8))
    x0, _, x1, _ = a.getbbox()
    cx = (x0 + x1) // 2
    w = h * 22 // 100
    crop = cell.crop((max(0, cx - w // 2), bb[1], min(cell.width, cx + w // 2), bb[1] + w))
    bg = Image.new('RGBA', crop.size, (255, 255, 255, 255))
    bg.alpha_composite(crop)
    bg.convert('RGB').resize((crop.width * 4, crop.height * 4), Image.LANCZOS).save(os.path.join(d(k), 'head.png'))
    return True


def do_sheet(k):
    os.makedirs(d(k), exist_ok=True)
    if os.path.exists(os.path.join(d(k), 'cell_casual.png')):
        return
    stem = os.path.join(d(k), 'sheet')
    p, refs = sheet_prompt(k)
    t0 = time.time()
    gpt_gen.gen(stem, p, refs=refs, timeout=1200)
    if make_cells(k, stem + '.png'):
        print('  好了 %s sheet %ds' % (k, time.time() - t0), flush=True)
        return
    print('  切不开，重出一回', k, flush=True)
    os.replace(stem + '.png', stem + '_切不开.png')
    p, refs = sheet_prompt(k, RETRY)
    gpt_gen.gen(stem, p, refs=refs, timeout=1200)
    if not make_cells(k, stem + '.png'):
        raise RuntimeError(k + ' 设定图两回都切不开')
    print('  好了 %s sheet（重出） %ds' % (k, time.time() - t0), flush=True)


def do_next(job):
    k, kind = job
    c = G.CAST[k]
    cell = os.path.join(d(k), 'cell_casual.png')
    head = os.path.join(d(k), 'head.png')
    t0 = time.time()
    if kind == 'art':
        refs = G.refs_of(c, 'art')[:3] + [head, cell]
        eyes = '' if k in NOT_LEGEND else OLD_EYES
        p = (ART % c['palette']) + eyes + c.get('face', '') + c['who'] + ' ' + c['art'] + ' ' + c.get('art_extra', '') + ART_END
        if c.get('art_close'):   # 外表容易显小的成年人和年少模样的，艺术照只到头肩
            p = p.replace('head and upper body', 'head and shoulders only') + ' Only the head and shoulders are in the picture.'
        if young(c):
            p += ' The collar and clothes fully cover the shoulders and chest.' + YOUNG
    else:
        refs = [cell, head] + (G.head_of(k)[:1] if c.get('ref_head') else [])
        p = FACES + c.get('face', '') + c['who'] + (YOUNG if young(c) else '')
    gpt_gen.gen(os.path.join(d(k), kind), p, refs=refs, timeout=1200)
    print('  好了 %s %s %ds' % (k, kind, time.time() - t0), flush=True)


def eligible(keys):
    out = []
    for k in keys:
        if G.CAST[k].get('minor') and not G.CAST[k].get('young_ok'):
            print('跳过（未成年那一档）', k, G.CAST[k]['name'], flush=True)
        else:
            out.append(k)
    return out


def missing(k):
    m = []
    if not os.path.exists(os.path.join(d(k), 'cell_casual.png')):
        m.append('sheet')
    for kind in ('art', 'faces'):
        if not os.path.exists(os.path.join(d(k), kind + '.png')):
            m.append(kind)
    return m


def pool(fn, items):
    with ThreadPoolExecutor(int(os.environ.get('CAST_WORKERS', '3'))) as ex:
        futs = {str(i): ex.submit(fn, i) for i in items}
        for n, f in futs.items():
            try:
                f.result()
            except Exception as e:
                print('  失败', n, str(e)[:200], flush=True)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['--list']:
        for k in G.CAST:
            print(k, G.CAST[k]['name'], '未成年那一档，不出' if G.CAST[k].get('minor') and not G.CAST[k].get('young_ok') else ('齐' if not missing(k) else '缺 ' + ' '.join(missing(k))))
        sys.exit()
    keys = eligible(list(G.CAST) if args == ['--all'] else args)
    pool(do_sheet, [k for k in keys if 'sheet' in missing(k)])
    if not os.environ.get('SHEET_ONLY'):
        pool(do_next, [(k, kind) for k in keys if os.path.exists(os.path.join(d(k), 'cell_casual.png')) for kind in missing(k) if kind != 'sheet'])
