# -*- coding: utf-8 -*-
"""看一门技艺现在的星条和持有人那几行。仓库根上跑：
  python -I -X utf8 底稿/命星高魔化/铺开/看.py 现在的名字或旧名 …   [--full] [--comp]
--comp 连持有人的旅伴条整条印出来。读的是仓库里现在的源稿。"""
import io, os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import 搭活 as D

jobs = json.load(io.open(os.path.join(HERE, '分份.json'), encoding='utf-8'))
want = [a for a in sys.argv[1:] if not a.startswith('--')]
full = '--full' in sys.argv
comp = '--comp' in sys.argv
for w in want:
    for j in jobs:
        for a in j['arts']:
            if w not in (a['new'], a['old'], a['row']['旧名']):
                continue
            r = a['row']
            print('=' * 30, j['name'], j['page'], a['new'], '(%s→%s)' % (a['old_tier'], a['tier']), '｜', '、'.join(a['holders']))
            print('归门 %s｜卷 %s｜法门 %s｜并进 %s｜补法 %s %s' % (r['归门'], r['卷'], r['法门'], r['并进'], r['补法'], r['原技艺']))
            print('缺：', r['缺什么或做到头的'])
            print('显相：', r['显相'])
            print('凭：', r['凭什么'])
            L = D.read_lines(os.path.join(ROOT, a['file']))
            sb = D.star_block(L, a['old'])
            blk = [D.bare(x) for x in L[sb[0]:sb[1]]]
            for x in blk:
                print(x if full else x[:260])
            for f in j['files']:
                LL = D.read_lines(os.path.join(ROOT, f))
                for name, (s, e) in D.comp_blocks(LL).items():
                    if not any(D.same_person(name, h) for h in a['holders']):
                        continue
                    print('--- 旅伴条', name, os.path.basename(f))
                    for x in LL[s:e]:
                        x = D.bare(x)
                        if comp or x.startswith(('底座：', '能力：', '固定锚定：', '身份：')) or (a['old'] in x and x.startswith('- ')):
                            print(x if full else x[:300])
