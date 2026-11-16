#!/usr/bin/env python3
# 一份活里还没洗的节（稿/ 里跟 原/ 一字不差的 `## ` 节），挑头 K 节印出来，给分块洗用。
#   python -I -X utf8 unwashed.py <份名> <K> <派过的单子.txt>
# 印出来的一行一节：稿/文件名｜节标题。同时把这几节记进“派过的单子”，派过一回还没变的节下一回不再派
# （洗稿的看了觉得不用动的短节，别一遍一遍派给它）。冻住不洗的节、节首不算，太短的节（不到 80 个汉字）不算。
# 一节也没有就什么都不印。加 --count 只印还剩几节（不记单子）。
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
FROZEN = re.compile(r'设计备注|凡世至强|^这一代的命星$|^这一代的人物$')
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
args = [a for a in sys.argv[1:] if not a.startswith('--')]
job = args[0]
K = int(args[1]) if len(args) > 1 else 4
ledger = args[2] if len(args) > 2 else ''
d = '%s/%s' % (BASE, job)


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


done = set()
if ledger and os.path.exists(os.path.join(d, ledger)):
    done = set(l.strip() for l in open(os.path.join(d, ledger), encoding='utf-8') if l.strip())
left = []
for fn in json.load(open(d + '/job.json', encoding='utf-8'))['files']:
    fn = os.path.basename(fn)
    o, n = secs('%s/原/%s' % (d, fn)), dict(secs('%s/稿/%s' % (d, fn)))
    for t, body in o:
        if FROZEN.search(t) or han(body) < 80:
            continue
        if n.get(t) == body:
            key = '稿/%s｜%s' % (fn, t)
            if key not in done:
                left.append((key, han(body)))
if '--count' in sys.argv:
    print(len(left))
    sys.exit(0)
# 一回至多 K 节，合起来不过七千个汉字上下（一节就过了的照样单给它一节）
pick, tot = [], 0
for key, h in left:
    if pick and (len(pick) >= K or tot + h > 7000):
        break
    pick.append(key)
    tot += h
if pick and ledger:
    open(os.path.join(d, ledger), 'a', encoding='utf-8', newline='\n').write('\n'.join(pick) + '\n')
for p in pick:
    print(p)
