#!/usr/bin/env python3
# 门面第四本书（迷宫纪）用的图，都出在 out/门面_原画_迷宫纪/（不进库）。
# 这一本是一口往下的井：一个年代一圈拱廊，最外一圈是地开那一夜，往下是前传六页，一条主线在它那一圈的墙上挂一幅壁画。
#   mural  壁画（q0_a 地开那一夜，q1_a..q6_c 一条主线一幅），横幅 3:2。画风照门面主画迷宫纪那一张（k4）和画风定稿样（t2），
#          场面照 底稿/门面/小样_迷宫纪书/scenes/qN.json（子任务起稿、主会话审），一页配一句这一圈的光（ERA_LIGHT）。
#   python gpt_cg4.py mural          出全部（出过的跳过）
#   python gpt_cg4.py q3 q0_a        出第三页那几幅，加地开那一夜
#   python gpt_cg4.py --left         还缺哪几幅
#   CG_DRY=1 只打提示词和参考图，不出图；CG_WORKERS=4 并着出
import glob
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_front as F  # noqa: E402
from gpt_gen import gen  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(HERE, 'out', '门面_原画_迷宫纪')
K4 = os.path.join(HERE, 'out', '门面_主画_11-10', 'k4.png')            # 迷宫纪主画：往下的井、拱廊、绳、底下的暖光
T2 = os.path.join(ROOT, '底稿', '门面', '画风定稿样_t2.png')             # 门面的画风定稿样
SCENES = os.path.join(ROOT, '底稿', '门面', '小样_迷宫纪书', 'scenes')

NO_MOON = ' There is no moon and no crescent anywhere in the picture.'
NO_ARC = (' Nothing pale and curved may stand alone against the sky where it could be read as a crescent: horns are short and straight or branching, '
          'and no bow, blade or arc of light is drawn as a single pale curve in the sky.')
PEOPLE = (' Any people are small and simple, with natural human proportions, each with exactly two arms and two legs; no close-ups and no faces in detail. '
          'Where the scene gives a number of people, draw exactly that many.')
GRAIN = 'a fine paper grain over everything'

MURAL_LEAD = ("Draw one wide 3:2 landscape picture: one painted panel from a long series of murals that hang along the arched galleries of a vast round well "
              "going down into the earth, ring below ring; each panel tells one moment from the thousand years of the people who went down that well. ")
MURAL_STYLE = (" Drawing manner: the FIRST attached picture is the approved main plate of this book and the SECOND is the approved style plate of the whole series; "
               "the new panel must look as if the same hand had painted it for the same book: large calm flat colour shapes layered like cut paper, "
               "thin lighter echo lines along the edges, soft inner gradients only, simplified forms with few details, " + GRAIN + ". "
               "Colours: deep indigo, slate blue and soft lavender stone for the cool world; warm amber and gold only for lamps, fire, the glow rising from far below "
               "and the few warm things the scene names. Huge things are drawn as layered pale silhouettes, like the great reliefs in the first plate. "
               "Take only the drawing manner and the colours from the attached pictures, never their composition, figures or architecture.")
MURAL_ROOM = (" Layout: the picture fills the whole rectangle edge to edge, with no painted border, frame or arch of its own; the book frames it later with a "
              "round-topped arch that hides the two upper corners, so keep everything important in the lower two thirds and the middle of the width, "
              "with calm open sky or dark space toward the upper corners.")
VIEW = (" Keep exactly the viewpoint the scene gives, what is near and what is far, the left-right placement, and the direction each figure faces "
        "(toward the viewer or away from it) as described.")

# 一页一句这一圈的光（照方向：往下就是往后，越往下越暗，黑潮最黑，垂暮是黄昏，底下是1001年的暖光）
ERA_LIGHT = {
    'q0': "The light of this ring: the last night of the year just before dawn, deep blue-black night, torches and a few lanterns in warm amber, pale dust hanging in the air. ",
    'q1': "The light of this ring: a dark new shaft of cold indigo stone, lit only by small warm points of lanterns and torches. ",
    'q2': "The light of this ring: cool blue stone with the first pale daylight falling from high above, warm amber lamps and a little dawn gold. ",
    'q3': "The light of this ring: the brightest age of the well, soft lavender and pale blue stone lit by clear crystal-white light, with warm festive lamps. ",
    'q4': "The light of this ring: deep indigo and cold blue-white, pale white fog lying low, cold light and very few warm points. ",
    'q5': "The light of this ring: the darkest age, black-blue gloom and smoke, with ember red-orange fire as the only warm colour. ",
    'q6': "The light of this ring: dusk, long low amber light falling soft over cool slate stone, quiet. ",
}

# 各族的叫法（照山铜纪那一本 gpt_cg3.py 的 FOLK）
FOLK = {
    'night-wing': "A night-wing is a person of a winged demon-kin people: a man or woman of ordinary human size and shape with a pair of large dark wings growing from the back, most often membranous like a bat's, sometimes feathered; never a dragon, a bat or a bird. ",
    'fire-horn': "A fire-horn is a person of a horned demon-kin people, ordinary human size and shape with horns on the head that may glow or burn like torches; never a beast. ",
    'bone folk': "The bone folk are a tall, pale demon-kin people with bone-white skin; they are living people, not skeletons. ",
}
BOW_RX = re.compile(r'\bbows?\b|bowstring|\barchers?\b|\barrows?\b')
CUT_BOW = (" Archery is drawn correctly: a bow is gripped at its middle; the bowstring is one single string, and on a drawn bow its two halves meet at one point "
           "inside the drawing hand.")

S = {}


def load():
    for p in sorted(glob.glob(os.path.join(SCENES, 'q?.json'))):
        d = json.load(open(p, encoding='utf-8-sig'))
        for m in d.get('murals', []):
            S[m['key']] = dict(kind='mural', page=m['key'].split('_')[0], text=m['text'], light=m.get('light', ''), name=m.get('name', ''), line=m.get('line', ''))


load()


def job(key):
    s = S[key]
    p = MURAL_LEAD + s['text'].strip() + ' ' + ERA_LIGHT.get(s['page'], '') + (s['light'].strip() + ' ' if s['light'] else '')
    p += ''.join(v for k, v in FOLK.items() if k in s['text'])
    p += VIEW + MURAL_STYLE + MURAL_ROOM + PEOPLE
    if BOW_RX.search(s['text']):
        p += CUT_BOW
    # WEST_PLAIN 里龙的角写的是往后掠，这一本角一律短而直（弯角衬着暗处会画成月牙）
    p += F.WEST_PLAIN.replace('swept-back horns', 'short straight horns') + NO_MOON + NO_ARC + F.CLEAN + ' Landscape picture, aspect ratio 3:2.'
    return p, [K4, T2]


# 拿原图（<键>_a0.png）当底只改一处，别的都不动（照 gpt_cg3.py 的 FIX）。原图在的时候走这一路。
_KEEP = ("Edit the attached picture. Keep every person, their faces, poses, clothes and places, the setting, the composition, the camera, the light, "
         "the colours, the rendering and the finish exactly as they are. Change only the following. ")
_TAIL = " There is no moon and no crescent anywhere. No text, no letters, no numbers, no logo, no frame. Landscape picture, aspect ratio 3:2."
FIX = {
    # 11-15 查图：钟台那一幅右边坡上的旧坟画成了一排十字架
    'q5_e': ('q5_e_a0.png', _KEEP +
             "On the hillside on the right, the old graves have grave markers shaped like crosses. Replace every cross-shaped grave marker with a plain low "
             "rounded headstone or a small upright slab with no arms. No cross shapes anywhere in the picture." + _TAIL),
    # 11-15 查图：九尾那一幅地平线上露出半个圆的日头
    'q4_m': ('q4_m_a0.png', _KEEP +
             "On the horizon behind the hills a half disc of the sun shows. Remove the sun disc completely: the sun is still hidden below the hills, and only "
             "a soft warm glow with a few straight rays of dawn light rises from behind the hill line. No round disc anywhere in the sky." + _TAIL),
}


STOP = []


def limited(key):
    try:
        t = open(os.path.join(OUT, key + '.log'), encoding='utf-8', errors='replace').read().lower()
    except OSError:
        return False
    return 'usage_limit' in t or 'usage limit' in t


def one(key):
    if STOP:
        print('没开（撞了出图额度）', key, flush=True)
        return
    try:
        os.makedirs(OUT, exist_ok=True)
        if key in FIX and os.path.exists(os.path.join(OUT, FIX[key][0])):
            out = gen(os.path.join(OUT, key), FIX[key][1], refs=[os.path.join(OUT, FIX[key][0])], timeout=1500)
            print('好了（照原图改）', key, out, flush=True)
            return
        p, refs = job(key)
        out = gen(os.path.join(OUT, key), p, refs=refs, timeout=1500)
        print('好了', key, out, flush=True)
    except Exception as e:
        if not STOP and limited(key):
            STOP.append(key)
            print('== 撞了出图额度，不再开新的', flush=True)
        print('失败', key, str(e)[:200], flush=True)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] == ['--left']:
        left = [k for k in sorted(S) if not os.path.exists(os.path.join(OUT, k + '.png'))]
        print(' '.join(left))
        print('缺', len(left), '／ 场面', len(S))
        sys.exit(0)
    keys = [k for k in sorted(S) if args == ['mural'] or k in args or k.split('_')[0] in args]
    if not keys:
        print('键：', ' '.join(sorted(S)))
        sys.exit(0)
    if os.environ.get('CG_DRY'):
        for k in keys:
            p, refs = job(k)
            print('==', k, len(p), '字', [os.path.basename(r) for r in refs])
            print(p)
        sys.exit(0)
    with ThreadPoolExecutor(int(os.environ.get('CG_WORKERS', '4'))) as ex:
        list(ex.map(one, keys))
