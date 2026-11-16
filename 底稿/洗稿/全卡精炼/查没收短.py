#!/usr/bin/env python3
# 洗稿把一节改写了、可是没收短（留九成三以上，有的反倒比原稿长）：这种节只担了改字的风险，没有收短的好处。
# 11-16 Gemini 3.8 Flash 洗的稿子里有：自查报了电报腔，叫它自己改，它往每一句里添“的、了、着”凑数，一节从 1624 字改成 1726 字，
# 顺手还把“半天”改成了“大半天”、丢了一个画面。这样的节整节退回原稿最稳妥（`还原节.py`），往后有人再洗。
#   python -I -X utf8 底稿/洗稿/全卡精炼/查没收短.py <份名…> [--min 0.93] [--dir 稿|稿_Codex原样] [--apply]
# --apply：把列出来的节在 稿/ 里整节退回 原/ 的样子（只动 --dir 稿）。冻住不洗的节（设计备注、凡世至强）和节首不算。
# 背景条（旅途同行·背景：X）不算：洗稿照规矩把来历从旅伴条挪进背景条，背景条本来就该不短、甚至变长（Codex 洗的也这样）。
# 11-16 的用法：`--min 1.0 --apply` 只退回比原稿还长的节，九成三到十成之间的留给审稿人看。
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
FROZEN = re.compile(r'设计备注|凡世至强|^这一代的命星$|^这一代的人物$|^旅途同行·背景')
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
args = sys.argv[1:]
MIN = 0.93
DIR = '稿'
APPLY = '--apply' in args
jobs = []
i = 0
while i < len(args):
    a = args[i]
    if a == '--min':
        MIN = float(args[i + 1]); i += 2; continue
    if a == '--dir':
        DIR = args[i + 1]; i += 2; continue
    if not a.startswith('--'):
        jobs.append(a)
    i += 1


def split(t):
    out, cur = [], ['', []]
    for ln in t.split('\n'):
        if ln.startswith('## '):
            out.append(cur)
            cur = [ln, []]
        else:
            cur[1].append(ln)
    out.append(cur)
    return out


total = 0
for job in jobs:
    d = '%s/%s' % (BASE, job)
    for fn in json.load(open(d + '/job.json', encoding='utf-8'))['files']:
        fn = os.path.basename(fn)
        pn, po = '%s/%s/%s' % (d, DIR, fn), '%s/原/%s' % (d, fn)
        if not os.path.exists(pn):
            continue
        raw = open(pn, 'rb').read().decode('utf-8')
        nl = '\r\n' if '\r\n' in raw else '\n'
        new = split(raw.replace('\r\n', '\n'))
        old = split(open(po, 'rb').read().decode('utf-8').replace('\r\n', '\n'))
        oi = {s[0]: s for s in old}
        hit = False
        for s in new:
            h = s[0]
            if not h or FROZEN.search(h[3:].strip()) or h not in oi:
                continue
            a, c = han('\n'.join(oi[h][1])), han('\n'.join(s[1]))
            if s[1] == oi[h][1] or a < 300:
                continue
            if c >= MIN * a:
                total += 1
                print('%s｜%s｜%s｜%d → %d（%d%%）%s' % (job, fn, h[3:40], a, c, 100 * c / a, '｜退回原稿' if APPLY and DIR == '稿' else ''))
                if APPLY and DIR == '稿':
                    s[1] = list(oi[h][1])
                    hit = True
        if hit:
            lines = []
            for k, s in enumerate(new):
                if k > 0:
                    lines.append(s[0])
                lines.extend(s[1])
            open(pn, 'wb').write('\n'.join(lines).replace('\n', nl).encode('utf-8'))
print('改写了却没收短的节（留 %d%% 以上）：%d 节' % (MIN * 100, total))
