# 用户想一张设定图把差分都出了再切（11-05，换了 Pro）。埃莉诺试三种，另出一张新腿部提示词的常服，都写 out/立绘_v2/eleanor/候选/。
#   sheet_base  四套衣服一张，拿现有常服当同一个人的参考
#   sheet_zero  四套衣服一张，不拿常服，从零一次定下这个人
#   sheet_all   四套衣服加九个表情全在一张
#   casual_legs 新的 BODY['woman']，单张常服，看膝盖和小腿
import os
import sys
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.insert(0, 'E:/aldran_art/底稿/状态栏/comfy')
import gpt_cast as G
import gpt_gen

KEY = 'eleanor'
c = G.CAST[KEY]
OUT = os.path.join(G.OUT, KEY, '候选')
spec = G.BODY['woman'] + G.HAIR + G.FACE['woman'] + G.REST + c['who'] + ' '
OUTFITS = ('From left to right: 1) ' + c['casual'] + ' 2) ' + c['private'] + ' 3) ' + c['battle'] + ' 4) ' + c['formal'] + ' ')
SHEET = ('A character design sheet: FOUR full-body standing figures of this one character side by side in a single horizontal row, in four different outfits. All four are exactly the same person: the same face, the same eyes, the same height and build, the same head size, the same drawing style. '
         'Every figure stands separately with clear empty space between it and its neighbours, nothing overlapping: keep capes, hair and weapons close to the body so they do not touch the next figure. Every figure is complete from the top of the head to the soles of the feet, the feet all on the same level, the heads all at the same height, filling the full height of the picture. A relaxed three-quarter view, looking at the viewer, even light, no dramatic shadow. '
         'Fully clothed, modest, not sexualized. Transparent background: no floor, no cast shadow. No text, no labels, no numbers, no frame, no dividing lines. Landscape picture, aspect ratio 3:2, at the largest size available. ')
ALL = ('A complete character design sheet of this one character on a single picture. All drawings are exactly the same person: the same face, the same eyes, the same drawing style. '
       'Left two-thirds of the picture: FOUR full-body standing figures side by side in a single row, separated by clear empty space, nothing overlapping, complete from head to soles, the feet on one level. '
       'Right third of the picture: NINE small bust portraits in a regular grid of 3 columns and 3 rows, same clothes as the first figure, same size and angle. Top row: calm; gentle smile; bright laugh with closed eyes. Middle row: serious; angry; sad with teary eyes. Bottom row: surprised; shy and blushing; in pain with one eye shut. '
       'Fully clothed, modest, not sexualized. Transparent background, no floor, no text, no labels, no frame, no dividing lines. Landscape picture, aspect ratio 3:2, at the largest size available. ')
base = G.path(KEY, 'casual')
head = G.head_of(KEY)
JOBS = {
    'sheet_base': (G.LC + G.SAME + spec + OUTFITS + SHEET, G.refs_of(c, 'next') + [base]),
    'sheet_zero': (G.LC + spec + OUTFITS + SHEET, G.refs_of(c, 'casual')[:3]),
    'sheet_all': (G.LC + spec + OUTFITS + ALL, G.refs_of(c, 'casual')[:3]),
    'casual_legs': (G.LC + spec + c['casual'] + ' ' + G.POSE, G.refs_of(c, 'casual')[:4 - len(head)] + head),
}


def run(n):
    p, refs = JOBS[n]
    out = gpt_gen.gen(os.path.join(OUT, n), p, refs=refs, timeout=1200)
    print('好了', n, out, flush=True)


names = sys.argv[1:] or list(JOBS)
with ThreadPoolExecutor(3) as ex:
    for f in [ex.submit(run, n) for n in names]:
        try:
            f.result()
        except Exception as e:
            print('失败', e, flush=True)
