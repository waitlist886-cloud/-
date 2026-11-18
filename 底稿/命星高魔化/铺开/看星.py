# -*- coding: utf-8 -*-
"""铺开·看星：一门技艺现在的星条（首段和法门、战法、练法、限制、传承几行，各截一截），和各页里「技艺【名】」那一类行的全文。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/看星.py 名字… [--cut 字数] [--full]"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 搭活 as D

names = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] != '--cut']
cut = int(sys.argv[sys.argv.index('--cut') + 1]) if '--cut' in sys.argv else 170
full = '--full' in sys.argv
pages = []
for r in D.read_tsv('全谱.tsv') + D.read_tsv('旅伴表.tsv'):
    if r['页'] not in pages:
        pages.append(r['页'])
rows = D.read_tsv('全谱.tsv')
for n in names:
    print('=' * 20, n)
    for r in rows:
        if r['技艺'] == n:
            print('全谱｜%s｜%s→%s｜%s｜卷 %s｜法门 %s｜缺 %s｜凭 %s' % (r['页'], r['现阶'], r['新档'], r['持有人'], r['卷'], r['法门'], r['缺什么或做到头的'][:60], r['凭什么'][:40]))
    for p in pages:
        for f in D.page_files(p):
            base = os.path.basename(f)
            if base in D.DUP:
                continue
            L = D.read_lines(f)
            for i, raw in enumerate(L):
                l = D.bare(raw)
                m = D.STAR.match(l)
                if m and m.group(1).strip() == n:
                    print('星条｜%s｜%s:%d｜%s' % (p, base, i + 1, l))
                    j = i + 1
                    while j < len(L) and not D.bare(L[j]).startswith('### ') and not D.bare(L[j]).startswith('## ') and not D.bare(L[j]).startswith('> 条目设置'):
                        t = D.bare(L[j]).strip()
                        if t:
                            print('    ' + (t if full else t[:cut] + ('…' if len(t) > cut else '')))
                        j += 1
                elif ('技艺【%s】' % n) in l and 'Art【' not in l[:max(0, l.find('技艺【%s】' % n))][-4:]:
                    if not re.search(r'Art\s*技艺', l):
                        print('技艺行｜%s｜%s:%d｜%s' % (p, base, i + 1, l))
