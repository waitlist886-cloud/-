#!/usr/bin/env python3
# 主角预设的二十三身命路战斗装（11-10，用户定了走甲：一条命路一身）。照 底稿/立绘/主角预设/命路战斗装.json 那张总表，
# 一个人一张设定图画四身（二十三身分六张，最后一张三身），切成 out/立绘_主角/<en>/cell_b_<代号>.png。
# 参考是这个人设定图切好的常服和放大的头（先跑 gpt_sheet.py 出本人那一张），脸、身子、头发照它，衣服和兵器照总表，族的讲究照资料里的 battle_note。
# 换族属（same_person）的人不出，战斗装照本人。
#   CAST_SET=主角 python gpt_battles.py --all      全员缺的
#   CAST_SET=主角 python gpt_battles.py pc_e_gd_f2  这几位
#   CAST_SET=主角 python gpt_battles.py --list     谁缺几张
import json
import os
import sys
import time

os.environ.setdefault('CAST_SET', '主角')
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_sheet as S
import cast_slice as CS
import gpt_gen
from PIL import Image

TABLE = json.load(open(os.path.join(HERE, '..', '..', '立绘', '主角预设', '命路战斗装.json'), encoding='utf-8'))
CODES = list(TABLE)
assert len(CODES) == 23, len(CODES)
CHUNKS = [CODES[i:i + 4] for i in range(0, len(CODES), 4)]   # 4、4、4、4、4、3

_WORD = {3: 'three', 4: 'four'}
_P1 = S.SHEET.index('1) the everyday outfit')
_P2 = S.SHEET.index('Everyone stands')


def sheet_b(n):
    head = S.SHEET[:_P1]
    for a, b in (('FOUR full-body standing figures', '%s full-body standing figures' % _WORD[n].upper()),
                 ('in four different outfits', 'in %s different battle outfits, one for each fighting style described' % _WORD[n]),
                 ('All four are exactly', 'All %s are exactly' % _WORD[n]), ('in all four the same', 'in all %s the same' % _WORD[n])):
        assert a in head, a
        head = head.replace(a, b)
    mid = ('In every figure the stance is tense and ready: the shoulders squared, the feet a little wider and planted, a firm expression, '
           'each figure gripping the weapon of its own outfit as described, kept close to the body; the outfits and weapons are clearly different from one another, '
           'each a newly qualified adventurer\'s first gear, good but plain, not legendary. ')
    tail = S.SHEET[_P2:]
    if n == 3:
        tail = tail.replace("own quarter of the picture", "own third of the picture")
    return head + mid + tail


def spec_of(c):
    t = S.tier(c)
    face = c.get('face') or S.G.FACE[t if t in ('boy', 'child') else ('man' if c.get('sex') == 'm' else t)]
    if S.halfling(c):
        face = (c.get('face') or S.HALF_FACE) + c.get('face_extra', '')
    if c.get('ya') and not c.get('face'):
        face = S.G.FACE_F % "fresh and clear, a young adult's, no longer childish"
    return S.body(c, t) + S.legs(c, t) + c.get('build', '') + S.G.HAIR + face + S.G.REST + c['who'] + ' '


def outfits(c, codes):
    sx = 'm' if c.get('sex') == 'm' else 'f'
    parts = []
    for i, x in enumerate(codes):
        e = TABLE[x]
        parts.append('%d) %s Colours: %s. %s.' % (i + 1, e[sx].rstrip(), e['palette'], e['pose'].rstrip(' .')))
    note = (' For every figure: ' + c['battle_note'].strip()) if c.get('battle_note', '').strip() else ''
    return 'From left to right: ' + ' '.join(parts) + note + ' '


def prompt(k, i, extra=''):
    c = S.G.CAST[k]
    codes = CHUNKS[i]
    last = [os.path.join(S.d(k), 'cell_casual.png'), os.path.join(S.d(k), 'head.png')]
    p = (S.G.LC + S.SAME_LEAD + spec_of(c) + outfits(c, codes) + sheet_b(len(codes)) + S.guard_of(c) + extra
         + (S.ytail(c) if (S.young(c) or c.get('ya')) else ''))
    return p, S.style_refs(c) + last


def cell(k, x):
    return os.path.join(S.d(k), 'cell_b_%s.png' % x)


def missing(k):
    return [i for i, codes in enumerate(CHUNKS) if not all(os.path.exists(cell(k, x)) for x in codes)]


def slice_into(k, i, src):
    codes = CHUNKS[i]
    figs = CS.figures(CS.clean(Image.open(src)), len(codes))
    if figs is None:
        return False
    for x, f in zip(codes, CS.cells(figs)[0]):
        f.save(cell(k, x))
    return True


def do_battle(job):
    k, kind = job
    i = int(kind.split('_')[1])
    if not missing(k) or i not in missing(k):
        return
    if not os.path.exists(os.path.join(S.d(k), 'head.png')):
        raise RuntimeError(k + ' 本人的设定图还没出')
    stem = os.path.join(S.d(k), kind)
    t0 = time.time()
    p, refs = prompt(k, i)
    gpt_gen.gen(stem, p, refs=refs, timeout=1200)
    if slice_into(k, i, stem + '.png'):
        print('  好了 %s %s %ds' % (k, kind, time.time() - t0), flush=True)
        return
    print('  切不开，重出一回', k, kind, flush=True)
    os.replace(stem + '.png', stem + '_切不开.png')
    p, refs = prompt(k, i, S.RETRY)
    gpt_gen.gen(stem, p, refs=refs, timeout=1200)
    if not slice_into(k, i, stem + '.png'):
        raise RuntimeError(k + ' ' + kind + ' 两回都切不开')
    print('  好了 %s %s（重出） %ds' % (k, kind, time.time() - t0), flush=True)


def bases():
    return [k for k, c in S.G.CAST.items() if not c.get('same_person')]


if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['--list']:
        n = 0
        for k in bases():
            m = missing(k)
            n += len(m)
            print(k, S.G.CAST[k]['name'], '齐' if not m else '缺 %d 张' % len(m))
        print('合计缺', n, '张')
        sys.exit()
    if args == ['--prompt']:   # 看一眼头一个人头一张的提示词
        k = bases()[0]
        print(prompt(k, 0)[0])
        sys.exit()
    keys = bases() if args == ['--all'] else args
    S.pool(do_battle, [(k, 'battle_%d' % i) for k in keys if os.path.exists(os.path.join(S.d(k), 'head.png')) for i in missing(k)])
