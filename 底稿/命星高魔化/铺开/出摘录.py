# -*- coding: utf-8 -*-
"""铺开·出摘录：从并回仓库的一页里抄几门技艺的星条和几位旅伴改了的行，给用户看样子用。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/出摘录.py 页 输出.md --art 名字,名字 --comp 名字,名字"""
import io, os, sys, json, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 搭活 as D


def arg(k):
    return sys.argv[sys.argv.index(k) + 1].split(',') if k in sys.argv else []


page, outp = sys.argv[1], sys.argv[2]
arts, comps = arg('--art'), arg('--comp')
jobs = [j for j in json.load(io.open(os.path.join(HERE, '分份.json'), encoding='utf-8')) if j['page'] == page]
out = ['# %s 改后的样子（摘录）' % D.short(page), '',
       '从并回仓库的页里原样抄的。技艺的星条整条抄，旅伴条只抄这一轮改了的行（减号是原来的，加号是现在的）。', '']
out += ['## 技艺', '']
for name in arts:
    hit = None
    for j in jobs:
        for a in j['arts']:
            if a['new'] == name:
                hit = (j, a)
    if not hit:
        out += ['（找不到 %s）' % name, '']
        continue
    j, a = hit
    L = [x.rstrip('\r') for x in D.read_lines(os.path.join(D.ROOT, a['file']))]
    sb = D.star_block(L, name)
    r = a['row']
    out += ['**%s**　原来 %s（%s）　现在 %s　持有人 %s　%s %s' % (name, a['old'], a['old_tier'], a['tier'], '、'.join(a['holders']) or '不是旅伴', r['归门'], r['卷']), '']
    out += ['```'] + [x for x in L[sb[0]:sb[1]] if x.strip()] + ['```', '']
out += ['## 旅伴条改了的行', '']
for name in comps:
    hit = None
    for j in jobs:
        for c in j['comps']:
            if name in c['name']:
                hit = (j, c)
    if not hit:
        out += ['（找不到 %s）' % name, '']
        continue
    j, c = hit
    b = os.path.basename(c['file'])
    O = [x.rstrip('\r') for x in io.open(os.path.join(D.WORK, j['name'], '原', b), encoding='utf-8', newline='').read().split('\n')]
    R = [x.rstrip('\r') for x in D.read_lines(os.path.join(D.ROOT, c['file']))]
    bo, br = D.comp_blocks(O).get(c['name']), D.comp_blocks(R).get(c['name'])
    df = [x for x in difflib.unified_diff(O[bo[0]:bo[1]], R[br[0]:br[1]], lineterm='', n=0) if x[:1] in '+-' and x[:3] not in ('+++', '---')]
    r = c['row']
    out += ['**%s**　%s' % (c['name'], r['去留']), '', '```'] + [(x if len(x) < 520 else x[:260] + ' …… ' + x[-240:]) for x in df] + ['```', '']
io.open(outp, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('写了', outp, len('\n'.join(out)))
