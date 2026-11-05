#!/usr/bin/env python3
# 角色立绘（第二版，崩铁光锥画风）。用户要立绘和表情差分跟前端用的艺术照是同一只手，差别只在光影、神情、姿态，并且要跟平台上清一色的 GPT 默认画风拉开。
# 写法定在第七轮用户挑的那一张（立绘试验/test7.py 的 n3，out/立绘_v2/eleanor/casual.png），研究和弯路见 立绘画法.md。
# 一位六张，先后不能乱：
#   casual   常服全身立绘：这张定下这个人的脸、发型和颜色，不拿别的图当底，参考只有光锥和官方全身图
#   art      艺术照：参考是官方艺术卡加这位的 casual，紧贴的胸像、硬边影子、前景虚化
#   private、battle、formal   别的三套：参考是两张光锥图加这位的 casual
#   faces    九格表情：参考是这位的 casual
# 体型按人分档（资料里的 tier），不定死：woman、man、burly、girl、small。写的头身数比出来的少一个上下，GPT 听不准数字。
# 资料在 cast/cast_*.json（一人一条），图写 out/立绘_v2/<en>/，已有的不重出，缺哪张补哪张。
#   python gpt_cast.py eleanor tifa        出这几位缺的全部，casual 一批，再出别的
#   python gpt_cast.py eleanor_battle ...  只出指定的几张
#   python gpt_cast.py --all               全员
#   python gpt_cast.py --list              列谁缺什么
# 环境变量 CAST_WORKERS 改同时跑几张，默认 3。
# 未成年的十位（tier girl、minor true）参考只用不露肤的那几张，全部穿戴整齐，艺术照到肩膀，也不拿旧立绘当参考。
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
REF = os.path.join(ROOT, '语料', '人物参考_11-04')   # 用户给的官方图裁掉边框、水印和版权条，不进库
LC_REF = os.path.join(REF, 'hsr_lc')
CARD_REF = os.path.join(REF, 'hsr', 'crop')
EXTRA = {   # 这几位另有用户定下的长相，当 casual 的参考
    'baltina': [os.path.join(HERE, 'refs', '巴尔缇娜_用户_11-03.webp')],
    'thornevia': [os.path.join(HERE, 'refs', '索恩薇娅_用户_11-03.webp')],
    'ariya': [os.path.join(REF, 'old', 'ariya_head.png')],   # 只裁头：现有立绘的身子是往成人画的，她 16 岁，身子不进参考，衣服写成字
}


def lc(*n):
    return [os.path.join(LC_REF, x + '.png') for x in n]


def card(*n):
    return [os.path.join(CARD_REF, x + '.png') for x in n]


LC = ("Draw an official full-body character illustration from the Japanese anime game Honkai: Star Rail, in the same hand as its Light Cone card art and official character art. The attached pictures show that hand; they are style references only: do not copy their characters, costumes, props or composition. ")
BODY = {
    'woman': ("BODY: a grown woman, not a girl: about 7 heads tall, the head a little larger than life but clearly an adult's, a slender neck, real shoulders, a defined waist, long legs with natural thickness at the thigh and calf; NOT a stick-thin fashion figure and NOT a small girl. A clear line of action: the weight on one leg, hips and shoulders tilted in opposite directions; long fingers drawn with care. "),
    'man': ("BODY: a grown man with the proportions of the adult male characters of that game: about 7 heads tall, broad straight shoulders tapering to a lean waist, a strong neck, long legs, large hands with visible knuckles; lean and trained; NOT a thin boy and NOT a bulky Western superhero. A clear line of action: the weight on one leg, hips and shoulders tilted in opposite directions; fingers drawn with care. "),
    'burly': ("BODY: a tall, heavily built man with the proportions of the adult male characters of that game: about 7 heads tall, the head in natural proportion and clearly readable, very broad shoulders, a deep chest, thick strong forearms and legs, the arms hanging naturally with believable anatomy, NOT inflated balloon muscles, NOT a Western superhero, NOT a tiny head on a huge body. A settled, weighty stance; large hands with visible knuckles, drawn with care. "),
    'girl': ("BODY: a teenage girl: about 6 heads tall, a relatively large head, narrow shoulders, slim limbs, a slender youthful build, fully covered by her clothes, nothing about the body emphasised. A light natural stance, the weight on one leg; fingers drawn with care. "),
    'small': ("BODY: a small adult of a short-statured folk: about 4.5 heads tall, with the proportions, hands and face of a grown-up, not of a child; compact and well balanced. Fingers drawn with care. "),
}
HAIR = ("HAIR: NO thin wavy strands and NO glossy plastic stripes. About 8 to 12 thick, smooth, ribbon-like locks, each one a clean bold shape with a crisp edge, swelling in the middle and tapering to a sharp hook at the end. A smooth rounded mass over the skull, the volume close around the head and shoulders. Soft low-contrast shading: a broad, pale, feathered band of highlight across the crown, not shiny; a soft hue shift from root to tip; a few crisp shadow shapes under the locks; fine lines only near the tips. ")
FACE_F = ("FACE, as in the references: medium-large, sharp, gently slanted almond eyes, NOT big round doll eyes; a thin tapering dark-brown upper lash line and a fine eyelid crease, no thick black lashes; the iris a soft luminous gradient with a small highlight; thin eyebrows partly hidden by the fringe; a short distance from the eyes to the mouth; a tiny nose, only a faint shadow; a small thin mouth; a soft cheek tapering to a neat pointed chin, %s. Pale clean skin with very little shading and only the faintest blush; skin shadows are a soft warm pink-orange, hard-edged under the fringe and under the chin. ")
FACE = {
    'woman': FACE_F % 'grown-up rather than childish',
    'girl': FACE_F % 'youthful and bright',
    'small': FACE_F % 'grown-up rather than childish',
    'man': ("FACE, as in the references: medium, sharp, narrow almond eyes, a thin tapering dark-brown upper lash line and a fine eyelid crease; the iris a soft luminous gradient with a small highlight; straight, slightly thicker eyebrows; a straight nose shown by a faint shadow and a small highlight, not large; a firm small mouth; a clean angular jaw. Clean skin with very little shading; skin shadows are a soft warm tone, hard-edged under the fringe and under the chin. "),
}
FACE['burly'] = FACE['man']
REST = ("LINE: a fine thin warm-brown line, never black, tapering away inside the shapes. "
        "COLOUR: a sophisticated, slightly muted palette with soft transitions, the way the references handle plum, teal and silver; tinted whites; the darkest tones are plum or deep slate, not black; one small saturated accent. "
        "LIGHT: a gentle key light from the upper left; shadows tinted with a soft cool hue such as violet or slate blue; soft ambient occlusion where layers meet; a thin pale rim along one edge. "
        "CLOTHES: drawn lightly, not heavy and dark: every large piece of cloth carries a visible soft gradient of hue, the folds are a few crisp elegant shadow shapes radiating from tension points, hems flip over to show a contrasting lining. Materials differ: leather with long soft highlights and stitched edges, metal fittings with small crisp reflections, fine embroidery kept small and quiet along an edge. Detail gathers at the chest, waist and hands; the legs and hems stay calm. "
        "Avoid: the look of a Western animated film, the look of an old moe anime, big round eyes, black outlines, saturated yellow hair, glossy hair stripes, thin wavy strands, clip-art embroidery, stick-thin legs, flat fills, a stiff stance, beige cast, grain, glitter, a glow around the figure. ")
POSE = ("A relaxed three-quarter view, a light wind lifting the hair and any loose cloth to one side, looking at the viewer. The plain, regular version of the character: even light, no dramatic shadow across the face, no blur, no particles. The whole figure from the top of the head to the soles of the feet, filling the height of the picture. Fully clothed, modest, not sexualized. Transparent background: nothing behind the figure, no floor, no cast shadow. No text, no logo, no frame. Portrait picture, aspect ratio 2:3. ")
SAME = ("The LAST attached picture is this exact character in the regular sprite: keep exactly the same face, the same eyes, the same hair colour and the same way of drawing, the same line and colour treatment, the same height and build. Only the clothes, the hairstyle if mentioned, the pose and the expression change, as described here. ")
ART = ("Draw in the exact rendering style of the attached reference pictures, which are official key art from the game Honkai: Star Rail, style references only: do not copy their characters, costumes, flowers or composition. Thin crisp line art in a darker tint of each local colour; luminous colour with razor-sharp shadow shapes; big clean flowing hair shapes ending in long tapered points. The LAST attached picture shows this exact character: keep the face, the eyes, the hair colour and the costume. "
       "A dramatic promotional art portrait of this character, the same kind of picture as the references: a tight bust close-up, the camera tilted, the figure filling the frame and cut off by its edges. A strong single-direction coloured light: a large hard-edged shadow falls across part of the face, the skin takes on the hue of the light, the highlights bloom to pure white. The whole picture is built from one hue family: %s. Soft out-of-focus shapes in the foreground for depth. Fully clothed, not sexualized. No text, no logo, no frame, no column. Portrait picture, aspect ratio 2:3. ")
ART_MINOR = ("A bright, wholesome character portrait, the head and shoulders only, the collar and clothes fully covering the shoulders and chest, an earnest, lively expression. ")
FACES = ("Character expression sheet for the dialogue box of a Japanese RPG. The attached picture shows this character: keep exactly the same face, eyes, hair colour and the same drawing style, thin warm-brown line, soft muted colour, crisp shadow shapes, half of the rendering is smooth gradient. "
         "Draw NINE bust portraits of this character on one square picture, in a perfectly regular grid of 3 columns and 3 rows, every cell the same size, with generous empty space between the cells. Every cell shows the head, neck and the top of the shoulders in the same clothes as the sprite, the same size, from the same slightly turned camera angle, the eyes at the same height, the whole head including all the hair inside the cell. "
         "Top row, left to right: calm and neutral; a gentle closed-mouth smile; a bright open-mouthed laugh with the eyes closed in happiness. "
         "Middle row, left to right: serious and determined; angry, with furrowed brows and bared teeth; sad, with teary eyes and lowered brows. "
         "Bottom row, left to right: surprised, wide eyes and a small open mouth; shy, blushing, the eyes looking away; in pain, one eye shut, teeth clenched, a drop of sweat. "
         "Transparent background, no lines between the cells, no text, no labels, no frame, no sparkles. Fully clothed, modest. ")
KINDS = ['casual', 'art', 'private', 'battle', 'formal', 'faces']
ORDER = {'casual': 0, 'art': 1, 'private': 1, 'battle': 1, 'formal': 1, 'faces': 1}


def load():
    cast = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'cast', 'cast_*.json'))):
        for c in json.load(open(f, encoding='utf-8')):
            cast[c['en']] = c
    return cast


CAST = load()


def refs_of(c, kind):
    t = c.get('tier') or ('man' if c.get('sex') == 'm' else 'woman')
    if t == 'girl' or c.get('minor'):   # 不露肤的几张
        return {'casual': card('saifei', 'fengjin', 'baie') + lc('firefly_top'), 'next': card('saifei') + lc('firefly_top'), 'art': card('saifei', 'fengjin', 'baie')}[kind]
    if t in ('man', 'burly'):
        return {'casual': lc('jingyuan', 'anaxa', 'lance_full', 'firefly_full'), 'next': lc('jingyuan', 'anaxa'), 'art': card('baie', 'nakexia', 'wandi', 'danheng')}[kind]
    return {'casual': lc('firefly_full', 'guinaifen', 'lance_full', 'jingyuan'), 'next': lc('firefly_full', 'guinaifen'), 'art': card('nakexia', 'kelvdela', 'baie', 'fengjin')}[kind]


def path(k, kind):
    return os.path.join(OUT, k, kind + '.png')


def job(name):
    k, kind = name.rsplit('_', 1)
    c = CAST[k]
    stem = os.path.join(OUT, k, kind)
    t = c.get('tier') or ('man' if c.get('sex') == 'm' else 'woman')
    base = path(k, 'casual')
    spec = BODY[t] + HAIR + FACE[t] + REST + c['who'] + ' '
    if kind == 'casual':
        extra = EXTRA.get(k, [])
        refs = refs_of(c, 'casual')[:4 - len(extra)] + extra
        lead = 'The last attached picture shows this exact character: keep her face shape, hair colour, hair style, eye colour, hair ornament and her cool expression; ignore its dark background and its heavy glossy rendering, and draw her in the clean hand of the other references. ' if extra else ''
        p = LC + lead + spec + c['casual'] + ' ' + POSE
    elif kind == 'art':
        refs = refs_of(c, 'art') + [base]
        p = (ART % c['palette']) + c['who'] + ' ' + c['art']
        if c.get('minor'):
            p = (ART % c['palette']).replace('a tight bust close-up', 'a close-up of the head and shoulders') + ART_MINOR + c['who'] + ' ' + c['art']
    elif kind == 'faces':
        refs = [base]
        p = FACES + c['who']
    else:
        refs = refs_of(c, 'next') + [base]
        p = LC + SAME + spec + c[kind] + ' ' + POSE
    if c.get('minor'):
        p += ' The character is a teenager: draw a youthful, wholesome, fully covered look, nothing suggestive.'
    print('  开始', name, flush=True)
    t0 = time.time()
    last = None
    for attempt in range(3):
        try:
            out = gpt_gen.gen(stem, p, refs=refs, timeout=1200)
            print('  好了 %s %ds' % (name, time.time() - t0), flush=True)
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
    for stage in (0, 1):
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
