# -*- coding: utf-8 -*-
"""铺开·看单：把一张套改单子（JSON）印成一条一行的旧串、新串，好过目。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/看单.py 单子.json [--cut 字数] [--from N] [--to M]"""
import io, os, sys, json, difflib

p = sys.argv[1]
cut = int(sys.argv[sys.argv.index('--cut') + 1]) if '--cut' in sys.argv else 150
a0 = int(sys.argv[sys.argv.index('--from') + 1]) if '--from' in sys.argv else 1
b0 = int(sys.argv[sys.argv.index('--to') + 1]) if '--to' in sys.argv else 10 ** 6
lst = json.load(io.open(p, encoding='utf-8'))
print('%s｜%d 条' % (os.path.basename(p), len(lst)))
for k, it in enumerate(lst, 1):
    if k < a0 or k > b0:
        continue
    f, a, b = it[0], it[1], it[2]
    n = it[3] if len(it) > 3 else 1
    # 只印不一样的那一截，前后各留几个字
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    blocks = sm.get_matching_blocks()
    pre = 0
    while pre < min(len(a), len(b)) and a[pre] == b[pre]:
        pre += 1
    suf = 0
    while suf < min(len(a), len(b)) - pre and a[-1 - suf] == b[-1 - suf]:
        suf += 1
    s0 = max(0, pre - 12)
    ao = a[s0:len(a) - suf + min(suf, 8)]
    bo = b[s0:len(b) - suf + min(suf, 8)]
    print('%d｜%s%s\n   旧：%s\n   新：%s' % (k, os.path.basename(f), '×%d' % n if n != 1 else '', ao[:cut] + ('…' if len(ao) > cut else ''), bo[:cut * 2] + ('…' if len(bo) > cut * 2 else '')))
