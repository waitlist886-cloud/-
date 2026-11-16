#!/usr/bin/env python3
# 把各份审稿人交的命星表并成一张，顺手对一遍页上的星标题。
#   python -I -X utf8 底稿/洗稿/全卡精炼/并命星表.py <输出.tsv> <页所在的目录> <份名…>
# 例：python -I -X utf8 底稿/洗稿/全卡精炼/并命星表.py 底稿/洗稿/全卡精炼/命星表/月银纪_萨尔维斯.tsv 萨尔维斯 萨1 萨2 萨3 萨4 萨5 萨6
# 做的事：
#   1. 读 C:/Users/waitl/codex_work/wash_1115/<份名>/命星表_*.tsv。
#   2. 持有人、星名两栏填反了的换回来（拿页上的 ### 星标题认）。
#   3. 类、档照页上的星标题核，对不上的照页改，印出来。
#   4. 页上有、表里没有的星印出来（要补），表里有、页上没有的印出来（多半是名字写错）。
#   5. 写出并好的表，印 Special 里映着、沾边、没映各几颗，白话名几颗。
# 分段稿的活（纷争纪、山铜纪、前传）：表的文件名对不上页（命星表_<份名>[_第几位].tsv），就照表里“文件”那一栏
# 去找分段稿，<页所在的目录> 可以写几个，逗号隔开：
#   python -I -X utf8 底稿/洗稿/全卡精炼/并命星表.py 底稿/洗稿/全卡精炼/命星表/纷争纪_一到三.tsv 纷争纪/parts,纷争纪/parts2,纷争纪/parts3 纷1 纷2乙 纷3乙
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = 'C:/Users/waitl/codex_work/wash_1115'
HEAD = ['文件', '持有人', '星名', '类', '档', '它是什么', '这个人的命', '映不映', '白话名', '备注']
TITLE = re.compile(r'^### ([^\n(（]+?) \((Special|Passive|Art|Active) \| (\w+)[^)\n]*\)', re.M)

out, pagedir, jobs = sys.argv[1], sys.argv[2], sys.argv[3:]
DIRS = pagedir.split(',')


def find(fn):
    for d in DIRS:
        p = os.path.join(d, fn)
        if os.path.exists(p):
            return p
    return None


def titles_of(path):
    t = open(path, encoding='utf-8').read().replace('\r', '')
    return {m.group(1): (m.group(2), m.group(3)) for m in TITLE.finditer(t)}


rows = []
for job in jobs:
    fs = sorted(glob.glob('%s/%s/命星表_*.tsv' % (ROOT, job)))
    if not fs:
        print('！%s 没有命星表' % job)
        continue
    for f in fs:
        page = os.path.basename(f)[len('命星表_'):-len('.tsv')] + '.md'
        pp = find(page)
        lines = [x for x in open(f, encoding='utf-8-sig').read().replace('\r', '').split('\n') if x.strip()]
        tcache, seen = {}, {}
        if pp:
            tcache[page] = titles_of(pp)
        for ln in lines:
            c = ln.split('\t')
            if c[0] == '文件' or len(c) < 5:
                continue
            c += [''] * (len(HEAD) - len(c))
            c = c[:len(HEAD)]
            fn = page if pp else c[0].strip()
            if fn not in tcache:
                q = find(fn)
                if not q:
                    print('！%s｜找不到文件 %s' % (job, fn))
                    tcache[fn] = {}
                else:
                    tcache[fn] = titles_of(q)
            titles = tcache[fn]
            c[0] = fn
            if c[1] in titles and c[2] not in titles:
                c[1], c[2] = c[2], c[1]
            star = c[2]
            if star not in titles:
                print('！%s｜表里的星「%s」页上没有这个标题（持有人 %s）' % (fn, star, c[1]))
            else:
                k, tier = titles[star]
                if c[3] != k or c[4] != tier:
                    print('  %s｜%s 的类档照页改：%s %s → %s %s' % (fn, star, c[3], c[4], k, tier))
                    c[3], c[4] = k, tier
                seen.setdefault(fn, set()).add(star)
            rows.append(c)
        for fn, titles in tcache.items():
            for s in titles:
                if s not in seen.get(fn, set()):
                    print('！%s｜页上的星「%s」(%s | %s) 表里没有' % (fn, s, titles[s][0], titles[s][1]))
            print('%s｜%s：页上 %d 颗，表里 %d 颗' % (job, fn, len(titles), len(seen.get(fn, set()))))

os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8', newline='\n') as w:
    w.write('\t'.join(HEAD) + '\n')
    for c in rows:
        w.write('\t'.join(c) + '\n')
sp = [c for c in rows if c[3] == 'Special']
cnt = {}
for c in sp:
    cnt[c[7] or '（空）'] = cnt.get(c[7] or '（空）', 0) + 1
print()
print('并了 %d 颗｜Special %d 颗：%s｜白话名 %d 颗' % (
    len(rows), len(sp), '，'.join('%s %d' % kv for kv in sorted(cnt.items(), key=lambda x: -x[1])),
    sum(1 for c in rows if c[8].strip() in ('是', '白话'))))
print('写到', out)
