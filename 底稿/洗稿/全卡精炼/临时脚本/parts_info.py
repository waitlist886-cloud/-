#!/usr/bin/env python3
# 给审稿人的分段清单：python -I -X utf8 parts_info.py <份名…>
# 每一段列出各节的标题和它在 稿_审N、原 里的行号，写进活的文件夹 分段_第N段.md，也打印出来。
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = 'C:/Users/waitl/codex_work/wash_1115'


def heads(path):
    out = []
    for i, line in enumerate(open(path, encoding='utf-8').read().replace('\r', '').split('\n'), 1):
        if line.startswith('## '):
            out.append((i, line[3:].strip()))
    return out


for job in sys.argv[1:]:
    d = ROOT + '/' + job
    plan = json.load(open(d + '/分审.json', encoding='utf-8'))
    for fn, parts in plan.items():
        ho = heads(d + '/原/' + fn)
        for n, idxs in enumerate(parts, 1):
            hn = heads('%s/稿_审%d/%s' % (d, n, fn))
            lines = ['# %s｜%s｜第 %d 段（共 %d 段）' % (job, fn, n, len(parts)), '',
                     '你要审、要改的是 `稿_审%d/%s`，只改下面这几节。行号是这一节 `## ` 标题所在的行。' % (n, fn), '',
                     '| 节的序号 | 标题 | 稿_审%d 里的行 | 原 里的行 |' % n, '|---|---|---|---|']
            for k in idxs:
                # 序号是 ## 标题从 0 数起的第几个
                t = hn[k][1] if k < len(hn) else '?'
                a = hn[k][0] if k < len(hn) else 0
                # 原稿里同名同序的节
                b = ho[k][0] if k < len(ho) and ho[k][1] == t else 0
                if not b:
                    cand = [x for x in ho if x[1] == t]
                    b = cand[0][0] if len(cand) == 1 else 0
                lines.append('| %d | %s | %d | %s |' % (k, t, a, b or '自己 Grep'))
            last = idxs[-1]
            end_new = hn[last + 1][0] - 1 if last + 1 < len(hn) else '文件末尾'
            lines += ['', '这一段在 稿_审%d 里到第 %s 行为止。别的节是另一位在审，或者是冻住不洗的，一个字也别动。' % (n, end_new)]
            txt = '\n'.join(lines) + '\n'
            open('%s/分段_第%d段.md' % (d, n), 'w', encoding='utf-8', newline='\n').write(txt)
            print(txt)
