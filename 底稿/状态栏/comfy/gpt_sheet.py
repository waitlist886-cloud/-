#!/usr/bin/env python3
# 角色立绘（第三版，设定图）。用户 11-05 定的：四套衣服一张图一次出，切开用，人才是同一个；表情另出一张。写法试出来的经过见 立绘画法.md 第十三节。
# 这是卡里来回切换的差分，不是设定稿：用户定四套同一个姿势、都看镜头，换的只有衣服和写明了的发型。
# 一位三张，先后不能乱：
#   sheet  四套衣服（常服、私服、战斗、正装）横版一张，切成 cell_casual/private/battle/formal.png，一格 640×960（cast_slice.py）
#   art    艺术照，参考是官方艺术卡加切好的常服
#   faces  九格表情，参考是切好的常服和放大的头
# 这个人有第二版的常服（out/立绘_v2/<en>/casual.png），拿它当最后一张参考定手法和长相，腿不照它；没有就用现有立绘裁的头。
# 四个人碰在一起切不开的话换个说法重出一回，再不行报失败，不硬切。
# 图写 out/立绘_v3/<en>/，已有的不重出。未成年那一档（minor）不在这里出。
#   python gpt_sheet.py eleanor kamelika   出这几位缺的
#   python gpt_sheet.py --all              全员
#   python gpt_sheet.py --list             列谁缺什么
# 环境变量 CAST_WORKERS 改同时跑几张，默认 3。
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
SHEET = ('A character design sheet on one wide picture: FOUR full-body standing figures of this one character in a single horizontal row, in four different outfits. All four are exactly the same person: the same face, the same eyes, the same height and build, the same head size. '
         'Draw each figure as its own finished character sprite, with the same care as a full-page illustration: a crisp thin line, sharp almond eyes, every lock of hair a clean ribbon shape, never a mass of small wavy strands, even at this size. '
         'These are interchangeable game sprites for a visual novel: the four figures must line up so one can be swapped for another. All four have EXACTLY THE SAME POSE and the same camera: the same very slight three-quarter turn of the body, the face toward the viewer and the eyes looking straight into the camera, a calm neutral expression; the head, shoulders, hips and feet in the same position in every figure. Choose one simple, natural standing pose that suits this character: the weight on one leg, a slight tilt of hips and shoulders, the arms relaxed and close to the body. Use that one pose for all four. Any pose or action written in the outfit descriptions is ignored: weapons are worn at the hip or on the back or held lowered in one hand without changing the pose, and nothing rises above the head. Everyone stands: no chair, no throne, no furniture. '
         'Only the clothes change, and the hairstyle where described. The air is almost still: the hair and loose cloth hang naturally with the slightest lift, staying inside each figure\'s own quarter of the picture and never touching the neighbouring figure: there is always a clear empty gap between figures. '
         'Every figure is complete from the top of the head to the soles of the feet, the feet all on one level, the heads all at one height, filling the full height of the picture. Even light, no dramatic shadow. '
         'Fully clothed, modest, not sexualized. Transparent background: no floor, no cast shadow. No text, no labels, no numbers, no frame, no dividing lines. Landscape picture, aspect ratio 3:2. ')
STRICT = ('Stricter still: in all four figures both arms hang straight down, relaxed at the sides, in exactly the same position, the hands empty and open. Nothing is held in the hands: any staff, flower, food, bag, cloak, tool or rope in the descriptions is left out or hung from the belt; a weapon is worn at the hip or carried on the back. Ignore the pose in the LAST attached picture. Laid over one another, the four figures would match at the head, shoulders, arms, hips and feet, and differ only in clothes. ')
RETRY = 'Leave much wider empty gaps between the figures this time and keep every sword, staff, cape and lock of hair well inside its own quarter. '
FACES = G.FACES.replace('The attached picture shows this character:', 'The attached pictures show this character, full figure and a close-up of the head:')
CELLS = ('casual', 'private', 'battle', 'formal')


def d(k):
    return os.path.join(OUT, k)


def tier(c):
    return c.get('tier') or ('man' if c.get('sex') == 'm' else 'woman')


def style_refs(c):
    if c.get('sex') == 'm':
        return G.lc('jingyuan', 'anaxa', 'lance_full')
    return G.lc('himeko_stand', 'aglaea_stand', 'guinaifen')


def sheet_prompt(k, extra=''):
    c = G.CAST[k]
    t = tier(c)
    spec = G.BODY[t] + LEGS[t] + G.HAIR + G.FACE['man' if c.get('sex') == 'm' else t] + G.REST + c['who'] + ' '
    outfits = 'From left to right: 1) ' + c['casual'] + ' 2) ' + c['private'] + ' 3) ' + c['battle'] + ' 4) ' + c['formal'] + ' '
    v2 = G.path(k, 'casual')
    if os.path.exists(v2):
        last = [v2]
        lead = 'The LAST attached picture shows this exact character: copy its face, eyes, hair colour, hair ornaments and way of drawing, but NOT its leg proportions. '
    else:
        last = (G.EXTRA.get(k) or G.head_of(k))[:1]
        lead = 'The LAST attached picture shows this exact character: keep the face shape, hair colour, hair style, eye colour and hair ornaments; ignore its background and its heavy glossy rendering. ' if last else ''
    return G.LC + lead + spec + outfits + SHEET + (STRICT if os.environ.get('SHEET_STRICT') else '') + extra, style_refs(c) + last


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
        refs = G.refs_of(c, 'art')[:3] + [cell]
        p = (G.ART % c['palette']) + c['who'] + ' ' + c['art']
    else:
        refs = [cell, head]
        p = FACES + c['who']
    gpt_gen.gen(os.path.join(d(k), kind), p, refs=refs, timeout=1200)
    print('  好了 %s %s %ds' % (k, kind, time.time() - t0), flush=True)


def eligible(keys):
    out = []
    for k in keys:
        if G.CAST[k].get('minor'):
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
            print(k, G.CAST[k]['name'], '未成年那一档，不出' if G.CAST[k].get('minor') else ('齐' if not missing(k) else '缺 ' + ' '.join(missing(k))))
        sys.exit()
    keys = eligible(list(G.CAST) if args == ['--all'] else args)
    pool(do_sheet, [k for k in keys if 'sheet' in missing(k)])
    if not os.environ.get('SHEET_ONLY'):
        pool(do_next, [(k, kind) for k in keys if os.path.exists(os.path.join(d(k), 'cell_casual.png')) for kind in missing(k) if kind != 'sheet'])
