# -*- coding: utf-8 -*-
"""铺开·技艺行冒号：凡世至强、人物条里「- 技艺【名】：」这一类行，名字到了五个字，标签就过了八个字，冒号换成｜（卡面口径）。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/技艺行冒号.py [--apply]"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 搭活 as D

RX = re.compile(r'^(\s*- (?:技艺|天赋|被动)【[^】]{5,}】)[：:]')
pages = []
for r in D.read_tsv('全谱.tsv') + D.read_tsv('旅伴表.tsv'):
    if r['页'] not in pages:
        pages.append(r['页'])
n = 0
seen = set()
for p in pages:
    for f in D.page_files(p):
        if f in seen or os.path.basename(f) in D.DUP:
            continue
        seen.add(f)
        s = io.open(f, encoding='utf-8', newline='').read()
        nl = '\r\n' if '\r\n' in s else '\n'
        out, k = [], 0
        for l in s.split(nl):
            m = RX.match(l)
            if m:
                l = m.group(1) + '｜' + l[m.end():]
                k += 1
            out.append(l)
        if k:
            n += k
            print('%s｜%d 行' % (os.path.relpath(f, D.ROOT), k))
            if '--apply' in sys.argv:
                D.safe_write(f, nl.join(out))
print('合计 %d 行%s' % (n, '' if '--apply' in sys.argv else '（没加 --apply，只报）'))
