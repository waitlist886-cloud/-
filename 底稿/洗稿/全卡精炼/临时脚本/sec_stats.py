#!/usr/bin/env python3
# 一份活一节一节留了多少（可洗的各节），收稿时挑着读用。
#   python -I -X utf8 sec_stats.py <份名…> [--all]
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
FROZEN = re.compile(r'史诗|传唱|设计备注|传奇表')
PART = set('的了着是在就也还把这那他她它')


def sections(text):
    out, cur, buf = [], '', []
    for l in text.split('\n'):
        if l.startswith('## '):
            out.append((cur, '\n'.join(buf)))
            cur, buf = l[3:].strip(), [l]
        else:
            buf.append(l)
    out.append((cur, '\n'.join(buf)))
    return out


def dens(t):
    h = re.findall(r'[\u4e00-\u9fff]', t)
    return sum(1 for c in h if c in PART) / max(1, len(h))


show_all = '--all' in sys.argv
for job in [a for a in sys.argv[1:] if not a.startswith('--')]:
    d = BASE + '/' + job
    for f in sorted(os.listdir(d + '/稿')):
        if not f.endswith('.md'):
            continue
        new = open(d + '/稿/' + f, encoding='utf-8').read().replace('\r\n', '\n')
        old = open(d + '/原/' + f, encoding='utf-8').read().replace('\r\n', '\n')
        so, sn = sections(old), dict(sections(new))
        rows, wo, wn, fo = [], 0, 0, 0
        for t, b in so:
            if not t or FROZEN.search(t):
                fo += han(b)
                continue
            nb = sn.get(t, '')
            wo += han(b)
            wn += han(nb)
            rows.append((han(nb) / max(1, han(b)), han(b), han(nb), dens(nb) / max(1e-9, dens(b)), t))
        print('== %s %s｜冻住 %d｜可洗 %d → %d（留 %d%%）｜%d 节' % (job, f, fo, wo, wn, 100 * wn / max(1, wo), len(rows)))
        rows.sort()
        pick = rows if show_all else rows[:4] + rows[-3:]
        for r, a, b, dd, t in pick:
            print('   %3d%%  %5d → %5d  虚字 %3d%%  %s' % (100 * r, a, b, 100 * dd, t[:40]))
