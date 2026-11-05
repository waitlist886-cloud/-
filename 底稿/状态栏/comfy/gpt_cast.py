#!/usr/bin/env python3
# （11-04 夜：下面 RENDER、SAMEHAND 这几段还是平涂那一版，已知不对，批量也停了，定了画风照 立绘画法.md 和 立绘试验/ 换了再跑。）
# 角色立绘（第二版，崩铁画风）。用户要立绘和表情差分跟前端用的艺术照是同一只手，差别只在光影、神情、姿态，并且要跟平台上清一色的 GPT 默认画风拉开。
# 一位六张，先后不能乱：
#   art      艺术照：四张崩铁的官方图只当画法参考，紧贴的胸像、硬边影子、前景虚化。这张定下这个人的脸、发色和画法
#   casual   常服全身立绘：参考图是四张崩铁的图加这位的 art，光是平的，写明不要艺术照那些光影
#   private、battle、formal   别的三套：参考图是两张崩铁的图加 art 加 casual
#   faces    九格表情：参考图是 art 和 casual
# 资料在 cast/cast_*.json（一人一条），图写 out/立绘_v2/<en>/，已有的不重出，缺哪张补哪张。
#   python gpt_cast.py eleanor tifa        出这几位缺的全部，art 一批、casual 一批，再出别的
#   python gpt_cast.py eleanor_battle ...  只出指定的几张
#   python gpt_cast.py --all               全员
#   python gpt_cast.py --list              列谁缺什么
# 环境变量 CAST_WORKERS 改同时跑几张，默认 3。
# 未成年的十位（minor）画法参考只用不露肤的那几张，全部穿戴整齐，也不拿旧立绘当参考。
import glob
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_gen

OUT = os.path.join(HERE, 'out', '立绘_v2')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
HSR = os.path.join(ROOT, '语料', '人物参考_11-04', 'hsr', 'crop')   # 用户给的官方图裁掉边框和版权条，不进库
EXTRA = {   # 这几位另有用户定下的长相，当艺术照的参考
    'baltina': [os.path.join(HERE, 'refs', '巴尔缇娜_用户_11-03.webp')],
    'thornevia': [os.path.join(HERE, 'refs', '索恩薇娅_用户_11-03.webp')],
}
STYLE_F = ['kelvdela', 'fengjin', 'changyeyue', 'haiseyin']
STYLE_M = ['baie', 'nakexia', 'wandi', 'danheng']
STYLE_Y = ['fengjin', 'saifei', 'tibao', 'baie']   # 未成年的用这一组

RENDER = ("Draw in the exact rendering style of the attached reference pictures, which are official key art from the game Honkai: Star Rail. They are style references only: do not copy their characters, costumes, flowers or composition. "
          "Copy how they are drawn: thin, crisp, even line art in a darker tint of each local colour, never black; flat, luminous cel colour with razor-sharp two-step and three-step shadow shapes, no airbrushing and no soft painterly blending; hair drawn as big clean flowing masses that end in long tapered points, with a colour gradient along the length, hard-edged highlight bands and a few single thin hairline strokes; large jewel-like eyes with a layered radial iris, a bright gradient, one small sharp catchlight and thin coloured eyeliner; a small sharp nose shown by a tiny triangular shadow, a small thin mouth, a slim V-shaped jaw; smooth flawless skin in a clean flat tone; saturated, clear, high-key colours and pure whites. "
          "Avoid the look of a generic AI anime picture: no beige or sepia cast, no muted dusty colours, no soft airbrushed shading, no watercolour or oil-paint feel, no canvas or paper grain, no fabric weave or wear textures, no scratches or grime, no noisy micro-detail, no thick dark outlines, no rounded generic face. ")
ART = ("A dramatic promotional art portrait of this character, the same kind of picture as the references: a tight bust close-up, the camera tilted, the figure filling the frame and cut off by its edges. A strong single-direction coloured light: a large hard-edged shadow falls across part of the face, the skin takes on the hue of the light, the highlights bloom to pure white. The whole picture is built from one hue family: %s. Soft out-of-focus shapes in the foreground for depth. Fully clothed, not sexualized. No text, no logo, no frame, no column. Portrait picture, aspect ratio 2:3. ")
SAMEHAND = ("The LAST attached picture is the target: this exact character, drawn by the artist whose hand you must match. Keep exactly the face shape, the eyes, the hair colour and the way the hair, skin, metal and cloth are rendered in that picture. Any other attached pictures are official Honkai: Star Rail art, for the same line and colour treatment only; do not copy their characters. "
            "Rendering: thin crisp line art in a darker tint of each local colour, never black; luminous cel colour with razor-sharp shadow shapes in two or three steps, the shadows tinted and saturated rather than grey; hair with rich depth, a deep saturated shade under every lock, big clean flowing masses ending in long tapered points, hard-edged highlight bands and a few single thin hairline strokes; large jewel-like eyes with a layered iris and a sharp catchlight; a small sharp nose shown by a tiny triangular shadow, a small thin mouth, a slim V-shaped jaw. Cloth in clean flat colour with crisp fold shadows; metal with sharp bright specular bands. No beige or sepia cast, no airbrushing, no paper grain, no fabric texture, no thick dark outlines. ")
TACHIE = ("Now draw this character as a full-body standing character sprite for the character screen of a Japanese fantasy RPG: the whole figure from the top of the head to the soles of the feet, centred, filling the height of the picture with a small margin, the body turned slightly to the viewer's left, an elegant natural stance, natural proportions (about 1 to 7.5 heads for an adult of normal size), hands drawn carefully with the correct number of fingers. Soft key light from the upper left with clean cel shadows and a thin bright rim of light along one side, the face looking at the viewer. This is the plain, regular version of the character: no dramatic shadow across the face, no dappled light, no blur, no floating particles. Fully clothed, modest, not sexualized. Transparent background: nothing behind the figure, no floor, no cast shadow. No text, no logo, no frame. Portrait picture, aspect ratio 2:3. ")
OUTFIT_NEXT = ("Same character, same height and build, same framing from the top of the head to the soles of the feet as in the regular sprite (the second to last attached picture is the art portrait, the last is the regular sprite). Only the clothes, the hairstyle if mentioned, the pose and the expression change, as described here. ")
FACES = ("Character expression sheet for the dialogue box of a Japanese RPG. The attached pictures show this character: keep exactly the same face, eyes, hair colour and the same drawing style as the sprite, thin crisp coloured line art, luminous cel colour, razor-sharp shadow shapes. "
         "Draw NINE bust portraits of this character on one square picture, in a perfectly regular grid of 3 columns and 3 rows, every cell the same size, with generous empty space between the cells. Every cell shows the head, neck and the top of the shoulders in the same clothes as the sprite, the same size, from the same slightly turned camera angle, the eyes at the same height, the whole head including all the hair inside the cell. "
         "Top row, left to right: calm and neutral; a gentle closed-mouth smile; a bright open-mouthed laugh with the eyes closed in happiness. "
         "Middle row, left to right: serious and determined; angry, with furrowed brows and bared teeth; sad, with teary eyes and lowered brows. "
         "Bottom row, left to right: surprised, wide eyes and a small open mouth; shy, blushing, the eyes looking away; in pain, one eye shut, teeth clenched, a drop of sweat. "
         "Transparent background, no lines between the cells, no text, no labels, no frame, no sparkles. Fully clothed, modest. ")
KINDS = ['art', 'casual', 'private', 'battle', 'formal', 'faces']
ORDER = {'art': 0, 'casual': 1, 'private': 2, 'battle': 2, 'formal': 2, 'faces': 2}


def load():
    cast = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'cast', 'cast_*.json'))):
        for c in json.load(open(f, encoding='utf-8')):
            cast[c['en']] = c
    return cast


CAST = load()


def hsr(*names):
    return [os.path.join(HSR, n + '.png') for n in names]


def style_of(c):
    if c.get('minor'):
        return STYLE_Y
    return STYLE_M if c.get('sex') == 'm' else STYLE_F


def path(k, kind):
    return os.path.join(OUT, k, kind + '.png')


def job(name):
    k, kind = name.rsplit('_', 1)
    c = CAST[k]
    stem = os.path.join(OUT, k, kind)
    style = style_of(c)
    art, base = path(k, 'art'), path(k, 'casual')
    if kind == 'art':
        extra = EXTRA.get(k, [])
        refs = hsr(*style[:4 - len(extra)]) + extra
        lead = 'The last attached picture shows this exact character: keep the face, hair colour and eye colour. ' if extra else ''
        p = RENDER + lead + c['who'] + ' ' + (ART % c['palette']) + c['art']
    elif kind == 'casual':
        refs = hsr(*style) + [art]
        p = SAMEHAND + TACHIE + c['who'] + ' ' + c['casual']
    elif kind == 'faces':
        refs = [art, base]
        p = FACES + c['who']
    else:
        refs = hsr(*style[:2]) + [art, base]
        p = SAMEHAND + TACHIE + OUTFIT_NEXT + c['who'] + ' ' + c[kind]
    if c.get('minor'):
        p += ' The character is a teenager: draw a youthful, wholesome, fully covered look, nothing suggestive.'
    print('  开始', name, flush=True)
    t = time.time()
    last = None
    for attempt in range(3):
        try:
            out = gpt_gen.gen(stem, p, refs=refs, timeout=1200)
            print('  好了 %s %ds' % (name, time.time() - t), flush=True)
            return out
        except Exception as e:
            last = e
            print('  重试 %s（%s）' % (name, str(e)[:80]), flush=True)
            time.sleep(20 * (attempt + 1))
    raise RuntimeError('%s 出不来：%s' % (name, last))


def missing(keys):
    out = []
    for k in keys:
        for kind in KINDS:
            if not os.path.exists(path(k, kind)):
                out.append(k + '_' + kind)
    return out


def run(jobs):
    workers = int(os.environ.get('CAST_WORKERS', '3'))
    for stage in (0, 1, 2):
        batch = [j for j in jobs if ORDER[j.rsplit('_', 1)[1]] == stage]
        if not batch:
            continue
        print('第 %d 批，%d 张' % (stage, len(batch)), flush=True)
        with ThreadPoolExecutor(workers) as ex:
            for f in [ex.submit(job, j) for j in batch]:
                try:
                    f.result()
                except Exception as e:
                    print('  失败', e, flush=True)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['--list']:
        for k in CAST:
            m = [j.rsplit('_', 1)[1] for j in missing([k])]
            print(k, CAST[k]['name'], '齐' if not m else '缺 ' + ' '.join(m))
        sys.exit()
    if args == ['--all']:
        run(missing(list(CAST)))
        sys.exit()
    jobs = []
    for a in args:
        if a in CAST:
            jobs += missing([a])
        else:
            jobs.append(a)
    run(jobs)
