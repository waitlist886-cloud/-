# 第 11 轮设定图人是同一个、衣服也对，但量下来腿还是短：胯在身高 54% 到 56%，官方 46% 到 49%。胯太低，光抬膝盖没用。
# 这一轮把胯写进去、腿不交叉，埃莉诺和卡麦莉加（用户点名的四位之一）各出设定图和单张常服。
import os
import sys
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.insert(0, 'E:/aldran_art/底稿/状态栏/comfy')
sys.path.insert(0, 'E:/aldran_art/底稿/状态栏/comfy/立绘试验')
import gpt_cast as G
import gpt_gen

LEGS = ("LEGS, the most important point, follow the standing adult woman in the first attached picture: a high waist and a short torso; measured from the top of the head to the sole, the crotch sits at 47 percent of the height, so the legs are longer than the head and torso together; the knee at 68 percent; the lower leg clearly longer than the thigh. Even under a long skirt the hips sit that high. The legs are straight and NOT crossed, the feet a little apart. Tall boots stop a hand below the knee. ")
SHEET = ('A character design sheet: FOUR full-body standing figures of this one character side by side in a single horizontal row, in four different outfits. All four are exactly the same person: the same face, the same eyes, the same height and build, the same head size, the same drawing style. '
         'Every figure stands separately with clear empty space between it and its neighbours, nothing overlapping: keep capes, hair and weapons close to the body so they do not touch the next figure. Every figure is complete from the top of the head to the soles of the feet, the feet all on the same level, the heads all at the same height, filling the full height of the picture. A relaxed three-quarter view, looking at the viewer, even light, no dramatic shadow. '
         'Fully clothed, modest, not sexualized. Transparent background: no floor, no cast shadow. No text, no labels, no numbers, no frame, no dividing lines. Landscape picture, aspect ratio 3:2, at the largest size available. ')


def jobs(k):
    c = G.CAST[k]
    spec = G.BODY['woman'] + LEGS + G.HAIR + G.FACE['woman'] + G.REST + c['who'] + ' '
    out = 'From left to right: 1) ' + c['casual'] + ' 2) ' + c['private'] + ' 3) ' + c['battle'] + ' 4) ' + c['formal'] + ' '
    head = G.head_of(k)
    refs = G.lc('himeko_stand', 'aglaea_stand', 'guinaifen')
    return {
        k + '_sheet': (G.LC + spec + out + SHEET, refs[:3] + head[:1]),
        k + '_casual': (G.LC + spec + c['casual'] + ' ' + G.POSE, refs[:3] + head[:1]),
    }


JOBS = {}
for k in sys.argv[1:] or ['eleanor', 'kamelika']:
    JOBS.update(jobs(k))


def run(n):
    k = n.rsplit('_', 1)[0]
    p, refs = JOBS[n]
    out = gpt_gen.gen(os.path.join(G.OUT, k, '候选', 'v12_' + n.rsplit('_', 1)[1]), p, refs=refs, timeout=1200)
    print('好了', n, out, flush=True)


with ThreadPoolExecutor(3) as ex:
    for f in [ex.submit(run, n) for n in JOBS]:
        try:
            f.result()
        except Exception as e:
            print('失败', n if False else '', e, flush=True)
