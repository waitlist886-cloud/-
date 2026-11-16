#!/usr/bin/env python3
# 把各份审稿人交的专名表并成一张。
#   python -I -X utf8 底稿/洗稿/全卡精炼/并专名表.py <输出.tsv> <文件所在的目录> <份名…>
# 例：python -I -X utf8 底稿/洗稿/全卡精炼/并专名表.py 底稿/洗稿/全卡精炼/专名表/月银纪_羁绊.tsv 月银纪补卷 月羁甲 月羁乙 …
# 读 C:/Users/waitl/codex_work/wash_1115/<份名>/专名表_*.tsv，照仓库里那个文件的 ## 标题核一遍条目数，
# 印出白话名填“是”的那几行。
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = 'C:/Users/waitl/codex_work/wash_1115'
HEAD = ['文件', '类', '条目名', '题', '是什么', '落点', '白话名', '哪一个', '备注']
FROZEN = re.compile(r'设计备注|传奇表')

out, pagedir, jobs = sys.argv[1], sys.argv[2], sys.argv[3:]
rows = []
for job in jobs:
    fs = sorted(glob.glob('%s/%s/专名表_*.tsv' % (ROOT, job)))
    if not fs:
        print('！%s 没有专名表' % job)
    for f in fs:
        page = os.path.basename(f)[len('专名表_'):-len('.tsv')] + '.md'
        pp = os.path.join(pagedir, page)
        n_titles = 0
        if os.path.exists(pp):
            t = open(pp, encoding='utf-8').read()
            n_titles = sum(1 for m in re.finditer(r'^## ([^\n]+)', t, re.M) if not FROZEN.search(m.group(1)))
        k = 0
        for ln in open(f, encoding='utf-8-sig').read().replace('\r', '').split('\n'):
            if not ln.strip():
                continue
            c = ln.split('\t')
            if c[0] == '文件' or len(c) < 4:
                continue
            c += [''] * (len(HEAD) - len(c))
            c = c[:len(HEAD)]
            c[0] = page
            rows.append(c)
            k += 1
        flag = '' if k == n_titles else '  ！条数对不上'
        print('%s｜%s：页上 %d 条，表里 %d 条%s' % (job, page, n_titles, k, flag))

os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8', newline='\n') as w:
    w.write('\t'.join(HEAD) + '\n')
    for c in rows:
        w.write('\t'.join(c) + '\n')
yes = [c for c in rows if c[6].strip().startswith('是')]
print()
print('并了 %d 条，白话名 %d 条：' % (len(rows), len(yes)))
for c in yes:
    print('  %s｜%s｜%s｜哪一个：%s｜%s' % (c[0][:-3], c[2], c[3], c[7], c[8][:60]))
print('写到', out)
