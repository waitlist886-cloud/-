#!/usr/bin/env python3
# 主会话审二十一份场面稿以后改的（2026-11-12）。跑过一回旧串就没了，再跑会停。
#   python -I -X utf8 review_1112.py
# 改了什么：
#   三处图名一纪之内重了：s13_b1 盐圈（跟 s20_n2 重）改水环，s15_a3 角火（跟 s03_n1 重）改分火，s13_c1 铜铃（跟阿芙那一幅重）改车头的铃。
#   s02_n2 木牌：路边木桩上不画吊着的人，改成空的绳圈和木牌。
#   s13_d_nasta 尝水：院子里不画一排躺着像睡着的人，改成几个裹着毯子坐着的人；这一幅没有要照实画的伤，raw 去掉。
#   s15_d_tiona 袖上名：缇奥娜看着十六七岁，照未成年的规矩画（minor），身后那一群孩子拿掉。
#   s17_d_iro 白石线：伊萝看着十六岁，照未成年的规矩画（minor）。
#   s10_n3 盾前：康斯坦策这一年六十岁，立绘换成老年那一套。
#   s17_a3 横戟：岑瓦这时是成年的样子，手上只有他十岁那一套立绘，不拿它当参考，照字画；画里有孩子，照未成年的规矩画（young）。
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))


def edit(era, key, fn):
    p = os.path.join(HERE, era + '.json')
    d = json.load(open(p, encoding='utf-8'))
    hit = [s for s in d.get('nodes', []) + d.get('deaths', []) if s['key'] == key]
    assert len(hit) == 1, (era, key, len(hit))
    fn(hit[0])
    json.dump(d, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('改了', key)


def rep(s, a, b):
    assert s['text'].count(a) == 1, (s['key'], a[:50], s['text'].count(a))
    s['text'] = s['text'].replace(a, b)


def rename(old, new):
    def f(s):
        assert s['name'] == old, (s['key'], s['name'])
        s['name'] = new
    return f


def s02_n2(s):
    rep(s, "stand tall wooden posts, each with a dark hanging shape on a short rope and a small wooden board on a cord below it with a few marks scratched on it; the shapes are far and small and show no detail, only their outlines against the pale sky.",
        "stand tall wooden posts, each with an empty loop of rope hanging from its crossbeam and a small wooden board on a cord below it with a few marks scratched on it; nothing hangs in the loops, and the posts are far and small against the pale sky.")


def nasta(s):
    rep(s, "Across the courtyard behind her other people lie dusted white in the salt against stretchers and the long shed, as though asleep, and on the wall the priest of the White Candle kneels with a hand on a stretcher.",
        "Across the courtyard behind her a few people sit wrapped in blankets against the long shed, dusted white with salt, watching her, and on the wall the priest of the White Candle kneels in prayer.")
    s.pop('raw', None)


def tiona(s):
    rep(s, " A few paces behind her stands a small group of grey-haired children, hand in hand, one of them a thin boy with grey-white hair, his left cuff already stitched.", "")
    s['minor'] = True
    s.pop('raw', None)


def iro(s):
    s['minor'] = True
    s.pop('raw', None)


def konst(s):
    who = s.get('who') or s.get('row')
    n = 0
    for x in who:
        if x[0] == 'z3_konstanze':
            x[0] = 'z3_konstanze_old'
            n += 1
    assert n == 1, s['key']


def cenwa(s):
    assert [x[0] for x in s.get('who', [])] == ['z5a_cenwa'], s.get('who')
    s.pop('who')
    s['young'] = True


edit('s13', 's13_b1', rename('盐圈', '水环'))
edit('s15', 's15_a3', rename('角火', '分火'))
edit('s13', 's13_c1', rename('铜铃', '车头的铃'))
edit('s02', 's02_n2', s02_n2)
edit('s13', 's13_d_nasta', nasta)
edit('s15', 's15_d_tiona', tiona)
edit('s17', 's17_d_iro', iro)
edit('s10', 's10_n3', konst)
edit('s17', 's17_a3', cenwa)
