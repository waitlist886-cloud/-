#!/usr/bin/env python3
# 洗前洗后合计：python -I -X utf8 tally.py <仓库里的文件…>（洗前取标签 详本_11-15）
import io
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
FROZEN = re.compile(r'史诗|传唱|设计备注|传奇表|凡世至强')
TICS = ['那一', '这一', '往后', '头一', '照旧']


def wash(t):
    idx = [m.start() for m in re.finditer(r'^## ', t, re.M)] + [len(t)]
    return ''.join(t[a:b] for a, b in zip(idx, idx[1:]) if not FROZEN.search(t[a:t.index('\n', a)]))


def han(s):
    return len(re.findall(r'[一-鿿]', s))


tot = {'o': 0, 'n': 0, 'fo': 0, 'fn': 0}
co = {k: 0 for k in TICS}
cn = {k: 0 for k in TICS}
files = sys.argv[1:]
for f in files:
    new = open(f, encoding='utf-8').read().replace('\r', '')
    old = subprocess.run(['git', 'show', '详本_11-15:' + f], capture_output=True).stdout.decode('utf-8').replace('\r', '')
    wo, wn = wash(old), wash(new)
    tot['o'] += han(wo)
    tot['n'] += han(wn)
    tot['fo'] += han(old)
    tot['fn'] += han(new)
    for k in TICS:
        co[k] += wo.count(k)
        cn[k] += wn.count(k)
print('页数', len(files))
print('全文汉字 %d → %d（留 %d%%）｜可洗的各节 %d → %d（留 %d%%）' % (
    tot['fo'], tot['fn'], 100 * tot['fn'] / max(1, tot['fo']), tot['o'], tot['n'], 100 * tot['n'] / max(1, tot['o'])))
for k in TICS:
    print('  %s 每万字 %.1f → %.1f' % (k, co[k] * 10000 / max(1, tot['o']), cn[k] * 10000 / max(1, tot['n'])))
