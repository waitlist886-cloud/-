# 用户定走设定图，要调到有单图那种效果。第 12 轮写了“披风头发收近”“腿笔直”，人才站成一排，这一轮换掉：
#   每个人自己的姿势，头发披风放开但不出自己那四分之一，四个人都当一张完整的立绘来画。
#   tuned    埃莉诺，只改提示词
#   tuned_b  同上，再拿 n3 常服当最后一张参考定手法（腿不照它）
#   redraw   设定图切出来的常服，整张重画成 1024×1536，看能不能两步走：设定图定人，单张定清晰度
#   另外三位：selephen（普通男性）、reinhardt（魁梧）、bromgar（矮人）
import os
import sys
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.insert(0, 'E:/aldran_art/底稿/状态栏/comfy')
import gpt_cast as G
import gpt_gen

LEGS = {
    'woman': ("LEGS, the most important point, follow the standing adult woman in the first attached picture: a high waist and a short torso; measured from the top of the head to the sole, the crotch sits at 47 percent of the height, so the legs are longer than the head and torso together; the knee at 68 percent; the lower leg clearly longer than the thigh. Even under a long skirt the hips sit that high. The legs are NOT crossed; the weight on one leg, the other knee a little relaxed. Tall boots stop a hand below the knee. "),
    'man': ("LEGS: long legs and a short torso: measured from the top of the head to the sole, the crotch sits at 48 percent of the height and the knee at 69 percent. The legs are NOT crossed; the weight on one leg. "),
    'small': '',
}
LEGS['burly'] = LEGS['man']
TUNED = ('A character design sheet on one wide picture: FOUR full-body figures of this one character in a single horizontal row, in four different outfits. All four are exactly the same person: the same face, the same eyes, the same height and build, the same head size. '
         'Draw each figure as its own finished character sprite, with the same care as a full-page illustration: a crisp thin line, sharp almond eyes, every lock of hair a clean ribbon shape, never a mass of small wavy strands, even at this size. '
         'Each figure has its OWN lively pose suited to its outfit, turned differently, with a clear line of action: the weight on one leg, hips and shoulders tilted in opposite directions, the hands doing something. NOT standing at attention, NOT symmetrical, NOT four copies of one pose. '
         'A light wind lifts the hair and all loose cloth upward and to the same side in all four figures; long hair, capes and skirts may flare out boldly, but each stays inside its own quarter of the picture and never touches the neighbouring figure: there is always a clear empty gap between figures. '
         'Every figure is complete from the top of the head to the soles of the feet, the feet all on one level, the heads all at one height, filling the full height of the picture. Even light, no dramatic shadow. '
         'Fully clothed, modest, not sexualized. Transparent background: no floor, no cast shadow. No text, no labels, no numbers, no frame, no dividing lines. Landscape picture, aspect ratio 3:2. ')
CUT = 'C:/Users/waitl/AppData/Local/Temp/claude/85a810c2c0993c77/e22307d9-b63e-4d31-ad24-f0ffb0fc6126/scratchpad/hsr/sheet/cut_eleanor/casual.png'


def spec_of(k):
    c = G.CAST[k]
    t = c.get('tier') or ('man' if c.get('sex') == 'm' else 'woman')
    return c, t, G.BODY[t] + LEGS[t] + G.HAIR + G.FACE['man' if c.get('sex') == 'm' else t] + G.REST + c['who'] + ' '


def outfits(c):
    return 'From left to right: 1) ' + c['casual'] + ' 2) ' + c['private'] + ' 3) ' + c['battle'] + ' 4) ' + c['formal'] + ' '


def refs_for(k, t):
    if t == 'woman':
        return G.lc('himeko_stand', 'aglaea_stand', 'guinaifen')
    return G.lc('jingyuan', 'anaxa', 'lance_full')


JOBS = {}
c, t, s = spec_of('eleanor')
JOBS['eleanor/v13_tuned'] = (G.LC + s + outfits(c) + TUNED, refs_for('eleanor', t) + G.head_of('eleanor')[:1])
JOBS['eleanor/v13_tuned_b'] = (G.LC + 'The LAST attached picture shows this exact character: copy its face, eyes, hair colour and way of drawing, but NOT its leg proportions. ' + s + outfits(c) + TUNED, refs_for('eleanor', t) + [G.path('eleanor', 'casual')])
JOBS['eleanor/v13_redraw'] = (G.LC + 'The LAST attached picture is this exact character, cut from a small design sheet. Redraw that figure as a full-page sprite: keep exactly the same pose, the same proportions and leg length, the same clothes, the same face. Only the finish changes: a crisp thin line, sharp eyes, every lock of hair a clean ribbon shape, a little more lift in the hair and cape. ' + s + c['casual'] + ' ' + G.POSE, G.lc('himeko_stand', 'guinaifen') + [CUT])
for k in ('selephen', 'reinhardt', 'bromgar'):
    c, t, s = spec_of(k)
    base = G.path(k, 'casual')
    extra = G.head_of(k)[:1] or ([base] if os.path.exists(base) else [])
    lead = 'The LAST attached picture shows this exact character: keep the face, hair and eye colour, ignore its rendering. ' if extra else ''
    JOBS[k + '/v13_tuned'] = (G.LC + lead + s + outfits(c) + TUNED, refs_for(k, t) + extra)


def run(n):
    k, stem = n.split('/')
    p, refs = JOBS[n]
    out = gpt_gen.gen(os.path.join(G.OUT, k, '候选', stem), p, refs=refs, timeout=1200)
    print('好了', n, out, flush=True)


names = sys.argv[1:] or list(JOBS)
with ThreadPoolExecutor(3) as ex:
    futs = {n: ex.submit(run, n) for n in names}
    for n, f in futs.items():
        try:
            f.result()
        except Exception as e:
            print('失败', n, e, flush=True)
