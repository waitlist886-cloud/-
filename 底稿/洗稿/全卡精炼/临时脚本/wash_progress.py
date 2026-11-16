#!/usr/bin/env python3
# 看几份活洗到哪了：稿/ 里跟 原/ 不一样的节算洗过的。Gemini 是一节一节换的，跑着的时候拿这个看进度。
#   python -I -X utf8 底稿/洗稿/全卡精炼/临时脚本/wash_progress.py <份名…>
import io
import json
import os
import re
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
FROZEN = re.compile(r'设计备注|凡世至强')
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))


def secs(p):
    t = open(p, encoding='utf-8', errors='replace').read().replace('\r', '')
    out, cur = [], None
    for ln in t.split('\n'):
        if ln.startswith('## '):
            cur = [ln[3:].strip(), []]
            out.append(cur)
        elif cur:
            cur[1].append(ln)
    return [(a, '\n'.join(b)) for a, b in out]


for job in sys.argv[1:]:
    d = '%s/%s' % (BASE, job)
    tot = done = ho = hn = 0
    bad = ''
    for fn in json.load(open(d + '/job.json', encoding='utf-8'))['files']:
        fn = os.path.basename(fn)
        o, n = secs('%s/原/%s' % (d, fn)), secs('%s/稿/%s' % (d, fn))
        if [a for a, _ in o] != [a for a, _ in n]:
            bad = '｜！%s 的节标题跟原稿对不上（%d 对 %d）' % (fn, len(o), len(n))
        for (a, x), (b, y) in zip(o, n):
            if FROZEN.search(a):
                continue
            tot += 1
            ho += han(x)
            hn += han(y)
            if x != y:
                done += 1
    logs = sorted(f for f in os.listdir(d) if f.startswith('agy_第'))
    last = max((os.path.getmtime(os.path.join(d, f)) for f in logs), default=0)
    res = ''
    if os.path.exists(d + '/自查_收稿.txt'):
        res = '｜自查 ' + open(d + '/自查_收稿.txt', encoding='utf-8', errors='replace').read().strip().split('\n')[-1][:20]
    print('%s｜洗了 %d/%d 节｜汉字 %d → %d（%d%%）｜agy %d 遍，%d 秒前有动静%s%s' % (
        job, done, tot, ho, hn, 100 * hn / max(1, ho), len(logs), time.time() - last if last else -1, res, bad))
