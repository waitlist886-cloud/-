#!/usr/bin/env python3
# 11-22 纷争纪这一轮新起的对手（11-21 铺开，三拨交稿里的「（人物）」条）出立绘的材料。
#   python -I -X utf8 底稿/立绘/tools/rival_material.py
# 名单从 底稿/审稿/纷争纪/铺开/3_*.md 和两份样稿里取；在七页里找标题带这个名字的条（人物条、凡世至强、旅伴），整条抄进材料。
# 写 底稿/立绘/铺开_11-22/材料/<页号>.md（z1 到 z7）和 名单.tsv。
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, '底稿', '立绘', '铺开_11-22', '材料')
NL = chr(10)


def rd(p):
    return open(p, encoding='utf-8').read().replace(chr(13) + NL, NL)


names = []
srcs = glob.glob(os.path.join(ROOT, '底稿', '审稿', '纷争纪', '铺开', '3_*.md'))
srcs += [os.path.join(ROOT, '底稿', '审稿', '纷争纪', '样稿_%s.md' % n) for n in ('雨城的星', '无名之柱')]
for f in srcs:
    for m in re.finditer(r'^## 纷争纪·人物｜[^\n]*，([^，\n]+)（人物）', rd(f), re.M):
        if m.group(1) not in names:
            names.append(m.group(1).replace('鸦岭男爵', '罗克兰男爵'))
ORD = '一二三四五六七'
pages = sorted(glob.glob(os.path.join(ROOT, '纷争纪', '纷争纪时段_*.md')), key=lambda f: ORD.index(os.path.basename(f)[6]))
assert len(pages) == 7, pages
os.makedirs(OUT, exist_ok=True)
rows = []
per = {}
for pi, fp in enumerate(pages, 1):
    t = rd(fp)
    pos = [m.start() for m in re.finditer(r'(?m)^## (?!裁定锁)', t)]
    for i, s in enumerate(pos):
        e = t[s:(pos[i + 1] if i + 1 < len(pos) else len(t))]
        head = e.split(NL, 1)[0]
        for n in names:
            short = n.split('·')[0]
            if short in head and ('（人物）' in head or '凡世至强' in head):
                line = t.count(NL, 0, s) + 1
                rel = os.path.relpath(fp, ROOT).replace(os.sep, '/')
                per.setdefault('z%d' % pi, []).append('<!-- %s｜%s:%d -->%s%s' % (n, rel, line, NL, e.rstrip() + NL))
                rows.append((n, 'z%d' % pi, '%s:%d' % (rel, line), head[3:60]))
found = {r[0] for r in rows}
for pg, es in per.items():
    open(os.path.join(OUT, pg + '.md'), 'w', encoding='utf-8').write((NL * 2).join(es))
with open(os.path.join(OUT, '名单.tsv'), 'w', encoding='utf-8') as fh:
    for r in rows:
        fh.write('\t'.join(r) + NL)
print(len(names), '位，找到', len(found), '位，条目', len(rows))
for n in names:
    if n not in found:
        print('没找到', n)
for pg in sorted(per):
    print(pg, len(per[pg]), sum(len(x) for x in per[pg]))
