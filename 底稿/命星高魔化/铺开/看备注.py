# -*- coding: utf-8 -*-
"""铺开·看备注：只印各份备注里要主会话拿主意的那几节（拿不准、跟任务不一样、任务以外要跟着改、对不上）。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/看备注.py 份名… [--all] [--max 字数]"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 搭活 as D

KEYS = ('拿不准', '任务以外', '不一样', '对不上', '主会话', '没改')
if '--key' in sys.argv:
    KEYS = tuple(sys.argv[sys.argv.index('--key') + 1].split(','))
names = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and not a.isdigit() and sys.argv[i - 1] not in ('--key', '--max')]
mx = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 900
for n in names:
    p = os.path.join(D.WORK, n, '备注.md')
    if not os.path.exists(p):
        print('== %s｜没有备注.md' % n)
        continue
    s = io.open(p, encoding='utf-8').read().replace('\r', '')
    if '--all' in sys.argv:
        print('== %s\n%s' % (n, s[:mx * 3]))
        continue
    # 照标题切节；没有标题的照“某某：”起头的行切
    parts = re.split(r'(?m)^(?=#{1,4} |\*\*[^*\n]{2,20}\*\*|[^\n：:]{2,16}[：:]\s*$)', s)
    out = []
    for part in parts:
        head = part.strip().split('\n', 1)[0]
        if any(k in head for k in KEYS):
            out.append(part.strip())
    txt = '\n'.join(out) if out else s
    print('== %s%s\n%s' % (n, '' if out else '（没切出节，印开头）', txt[:mx] + ('…' if len(txt) > mx else '')))
