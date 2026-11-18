# -*- coding: utf-8 -*-
"""看一份活改成了什么样：新的星条整块印出来，旅伴条只印改了的行（- 是原来的，+ 是现在的），再印备注。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/看稿.py 份名 [--nostar] [--nocomp] [--only 名字]"""
import io, os, sys, json, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 搭活 as D

name = sys.argv[1]
only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
d = os.path.join(D.WORK, name)
J = json.load(io.open(os.path.join(d, '任务.json'), encoding='utf-8'))


def rl(p):
    return [x.rstrip('\r') for x in io.open(p, encoding='utf-8', newline='').read().split('\n')]


O = {os.path.basename(f): rl(os.path.join(d, '原', os.path.basename(f))) for f in J['files']}
G = {os.path.basename(f): rl(os.path.join(d, '稿', os.path.basename(f))) for f in J['files']}
if '--nostar' not in sys.argv:
    for a in J['arts']:
        if only and only not in (a['new'], a['old']):
            continue
        b = os.path.basename(a['file'])
        sg = D.star_block(G[b], a['new'])
        print('#' * 6, '%s (%s→%s)｜%s｜%s %s｜%s' % (a['new'], a['old_tier'], a['tier'], '、'.join(a['holders']), a['row']['归门'], a['row']['卷'], a.get('share') or ''))
        if not sg:
            print('  （稿里没有这一条%s）' % ('，共用别人的' if a.get('share') == '从' else ''))
            continue
        for l in G[b][sg[0]:sg[1]]:
            if l.strip():
                print(l)
        print()
if '--nocomp' not in sys.argv:
    for c in J['comps']:
        if only and only not in c['name']:
            continue
        b = os.path.basename(c['file'])
        bo, bg = D.comp_blocks(O[b]).get(c['name']), D.comp_blocks(G[b]).get(c['name'])
        if not bo or not bg:
            print('#' * 6, c['name'], '（块找不到）')
            continue
        lo, lg = O[b][bo[0]:bo[1]], G[b][bg[0]:bg[1]]
        df = [x for x in difflib.unified_diff(lo, lg, lineterm='', n=0) if x[:1] in '+-' and x[:3] not in ('+++', '---')]
        r = c['row']
        print('#' * 6, '%s｜%s｜年:%s｜走:%s｜添:%s｜升:%s' % (c['name'], r['去留'], r['年纪调整'][:30], r['位阶走势'][:30], r['下场添一句'][:30], r['升传奇'][:20]))
        for x in df:
            print('  ' + (x if len(x) < 700 else x[:700] + '…'))
        print()
p = os.path.join(d, '备注.md')
if os.path.exists(p) and not only:
    print('#' * 6, '备注')
    print(io.open(p, encoding='utf-8').read())
