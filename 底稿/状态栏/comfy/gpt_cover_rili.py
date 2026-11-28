#!/usr/bin/env python3
# 日里版封面（11-28，用户挑了“传火的手”）：一张竖版 2:3 封面，一张横版背景。
# 简介末尾“火传了两万三千年。现在，它在你的手里。”五只不同时代的手从下往上一只接一只托着同一簇火，最上面一只手空着、伸向看图的人。
# 画法照风月五张那一对光锥参考（gpt_cover.STYLE），护栏照 gpt_cg5（不画十字、月牙、字）。
#   python gpt_cover_rili.py cover cover cover     竖版出三稿（rili_cover_vN.png）
#   python gpt_cover_rili.py bg                    横版出一稿（rili_bg_vN.png，3:2，定稿时裁 16:9）
#   python gpt_cover_rili.py --final rili_cover_v2 rili_bg_v1 [背景顶上裁的像素]   写到 out/发布卡_四纪大框/封面/
#   CG_DRY=1 只打提示词。要带 PIL 的 Python（ComfyUI 那一个）。
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_cover as GC  # noqa: E402
import gpt_cg as G  # noqa: E402
import gpt_cg5 as C5  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = GC.ROOT
OUT = os.environ.get('COVER_OUT') or os.path.join(os.path.dirname(GC.OUT), '日里封面')
FINAL = os.path.join(ROOT, 'out', '发布卡_四纪大框', '封面')

LEAD = ("Draw in the rendering of the attached official Light Cone illustrations from Honkai: Star Rail (the first %d attached pictures), for style only: do not copy their characters, costumes, props or composition. "
        "This is the cover key visual of a Japanese fantasy role-playing game that spans five ages of one world over twenty-three thousand years, the picture on the game's card in a store list: "
        "bold, clear and striking even when shown small, painted with the full finish of that game's Light Cone art, saturated colour, dense detail, strong light. ")

HANDS = ("The subject is hands passing one fire down the ages. Five hands rise one above another from the bottom of the picture toward the top, each from a different age, each holding or cupping the same small warm golden flame "
         "as it is passed upward from hand to hand, so the picture reads as one rising chain of light. Only hands and forearms are shown, each coming in from the side or from below, the sleeves telling the age; no faces, no bodies, no heads anywhere. "
         "From bottom to top: "
         "first, at the very bottom, a hunter's hand from the first age of endless night: chapped and red with cold, a sleeve of rough fox fur bound with hemp cord, holding a small smoke-blackened clay pot with one glowing ember in it; "
         "second, a little higher and to the other side, a wall guard's hand from the age of the great white wall: a worn steel gauntlet with a white cloth wrapped round the wrist, holding a short iron torch lit from that ember; "
         "third, higher again, a knight's hand from the age of the twin queens: a plain brown leather glove, a weathered dark officer's cuff with a copper button, holding a small iron lantern whose flame is the same fire; "
         "fourth, near the top, an adventurer's bare hand from the age of the labyrinth: a hemp rope wound round the wrist with a tiny bronze bell, a faint dark handprint-shaped seal on the back of the hand, the palm cupped round the flame as it passes up; "
         "fifth, at the top of the chain, just below the title band, one more open hand, bare and empty, reaching out toward us with the palm turned up, its sleeve a plain dark travelling cloak, the little flame just landing above its palm: "
         "this last hand is the player's, waiting to receive the fire. "
         "The flame is the brightest and warmest thing in the picture and is clearly the same small flame all the way up. ")

BACKDROP = ("Behind the chain of hands, the five ages rise as one tall blended panorama, each faint and far, melting into the next through smoke, starlight and drifting embers, from the bottom of the picture to the top: "
            "at the bottom an endless frozen night plain with colossal pale beasts on the horizon (a great dragon with bat-like wings, a giant stag with branching antlers) and tiny campfires; "
            "above it an immense wall of white stone running to the horizon under a blood-red sky with beacon fires on its towers; "
            "above that a grey field with fresh plough furrows and rows of colossal rusted clockwork soldier-machines kneeling far away; "
            "above that the mouth of an enormous round pit stepping down ring below ring with tiny lantern lights; "
            "and near the top a vast city of domes and spires at dawn, with steam trains on stone viaducts and two wooden airships with sails in the sky, and a pair of great arched doors standing open with gold light pouring out. "
            "The backdrop is soft and atmospheric so the hands and the flame stay the clear subject. ")

HAND_RULES = ("Every hand is drawn with correct anatomy: exactly five fingers, a thumb on the correct side, natural knuckles and finger lengths, each finger clearly separate, no extra or fused fingers. "
              "Each hand connects naturally to its wrist and forearm, and each forearm comes in from the edge of the picture or from below; no hand floats without an arm, no arm crosses another in a confusing way. "
              "Every object that is held is truly gripped by its hand. ")

COVER_TAIL = ("Layout: portrait picture, taller than wide, aspect ratio 2:3, the painting filling the whole frame edge to edge. "
              "The top fifth of the picture is a clean title band: quiet dark night sky turning to gold at its lower edge, with nothing important in it, because a title will be laid over it later. "
              "Keep the hands and the flame inside the middle four fifths of the width with a margin on all sides. ")

BG_TAIL = ("Layout: landscape picture, wider than tall, aspect ratio 3:2, the painting filling the whole frame edge to edge. This is a dark background for a chat screen: "
           "keep it dark and calm overall, deep night blue and indigo, low contrast in the middle of the picture where text will sit; "
           "the chain of hands and the flame rise from the lower left corner toward the upper left third, small and glowing; the five ages stretch across the rest of the picture from left to right instead of bottom to top, faint and far. ")

SAFE = ("Nothing is sexualized. No blood and no wounds. "
        "The world is Western high fantasy of swords and magic with medieval Europe as its base, the last age adding brass, steam and arcane engines: no East Asian garments, roofs or motifs, nothing from the real modern world, no firearms. "
        "No real-world religious crosses anywhere. There is no moon, no crescent and no eclipse anywhere in the picture. "
        "No text, no letters, no numbers, no runes that read as writing, no logo, no watermark, no title, no frame, no border, no caption: the picture carries no words at all. ")


def job(kind):
    style = [os.path.join(G.LC, n + '.png') for n in GC.STYLE]
    p = (LEAD % len(style)) + HANDS + BACKDROP + HAND_RULES + SAFE + (COVER_TAIL if kind == 'cover' else BG_TAIL)
    p += ' ' + C5.NO_CROSS
    return p, style


def next_stem(kind):
    n = 1
    while any(os.path.exists(os.path.join(OUT, 'rili_%s_v%d%s' % (kind, n, x))) for x in ('.png', '.log', '.prompt.txt')):
        n += 1
    return os.path.join(OUT, 'rili_%s_v%d' % (kind, n))


_lock = __import__('threading').Lock()


def one(kind):
    p, refs = job(kind)
    with _lock:
        stem = next_stem(kind)
        os.makedirs(OUT, exist_ok=True)
        open(stem + '.prompt.txt', 'w', encoding='utf-8').write(p + '\n\nrefs: ' + ' | '.join(refs) + '\n')
    t0 = time.time()
    try:
        out = C5.gen5(stem, p, refs=refs, timeout=1500)
        print(time.strftime('%H:%M:%S'), '好了', os.path.basename(stem), '%d 秒' % (time.time() - t0), [os.path.basename(o) for o in out], flush=True)
    except Exception as e:
        print(time.strftime('%H:%M:%S'), '失败', os.path.basename(stem), str(e)[:300], flush=True)


def final(cover, bg, top=None):
    os.makedirs(FINAL, exist_ok=True)
    im = Image.open(os.path.join(OUT, cover + '.png')).convert('RGB')
    im.save(os.path.join(FINAL, '日里_封面.png'))
    im.resize((800, 1200), Image.LANCZOS).save(os.path.join(FINAL, '日里_封面.jpg'), quality=88, optimize=True, progressive=True)
    b = Image.open(os.path.join(OUT, bg + '.png')).convert('RGB')
    if b.size != (1536, 1024):
        b = b.resize((1536, 1024), Image.LANCZOS)
    t = 80 if top is None else max(0, min(160, top))
    b = b.crop((0, t, 1536, t + 864)).resize((1920, 1080), Image.LANCZOS)
    b.save(os.path.join(FINAL, '日里_背景.png'))
    b.save(os.path.join(FINAL, '日里_背景.jpg'), quality=88, optimize=True, progressive=True)
    print('定了', cover, bg)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    a = sys.argv[1:]
    if a[:1] == ['--final']:
        final(a[1], a[2], int(a[3]) if len(a) > 3 else None)
        sys.exit(0)
    if os.environ.get('CG_DRY'):
        for k in a:
            p, refs = job(k)
            print('==', k, len(p), '字', [os.path.basename(r) for r in refs]); print(p)
        sys.exit(0)
    with ThreadPoolExecutor(int(os.environ.get('CG_WORKERS', '4'))) as ex:
        list(ex.map(one, a))
