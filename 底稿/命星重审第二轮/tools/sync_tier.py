#!/usr/bin/env python3
# 技艺铺开（11-20）：写手改了档的技艺，同步到同一页能力行里的 Art【X】(档 和技艺走势里的【X】(档)。
#   python -I -X utf8 底稿/命星重审第二轮/tools/sync_tier.py
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from splice_rare import sources, W  # noqa: E402

idx = json.load(open(os.path.join(W, '材料', '艺_索引.json'), encoding='utf-8'))
mp = dict(re.findall(r'^\| (\S+) \| (\S+) \|$', open(os.path.join(W, '收稿', '技艺改名表.md'), encoding='utf-8').read(), re.M)[1:])
oldtier = {}
for key in idx:
    t = open(os.path.join(W, '材料', '艺_%s.md' % key), encoding='utf-8').read()
    for nm, tr in re.findall(r'^【技艺】(\S+)｜现档 (\w+)', t, re.M):
        oldtier[(key, mp.get(nm, nm))] = tr
newtier = {}
for f in glob.glob(os.path.join(W, '交稿', 'aw_*.md')):
    key = re.match(r'aw_(.+)_\d+[a-f]?\.md$', os.path.basename(f)).group(1)
    for nm, tr in re.findall(r'^### (\S+) \(Art \| (\w+)\)', open(f, encoding='utf-8').read(), re.M):
        newtier[(key, nm)] = tr
for k, n, o in [('山铜纪_03', '高台牵袖传声法', '引路声'), ('山铜纪_03', '石饲解缚剑术', '断绳剑'), ('纷争纪_07', '碧穹银露长咏咒法', '银露古法')]:
    if (k, n) in newtier:
        newtier[(k, o)] = newtier.pop((k, n))
ch = [(k, n, oldtier[(k, n)], t) for (k, n), t in newtier.items() if oldtier.get((k, n)) and oldtier[(k, n)] != t]
print('改档', len(ch))
for x in ch:
    print('  ', *x)
tot = 0
for k, n, o, t in ch:
    for src in sources(k, idx[k]['file']):
        raw = open(src, encoding='utf-8', newline='').read()
        new = re.sub(r'(Art【' + re.escape(n) + r'】\()' + o, lambda m: m.group(1) + t, raw)
        new = re.sub(r'(^技艺走势：[^\n]*?【' + re.escape(n) + r'】\()' + o + r'(\))', lambda m: m.group(1) + t + m.group(2), new, flags=re.M)
        if new != raw:
            tot += 1
            open(src, 'w', encoding='utf-8', newline='').write(new)
print('改了文件', tot)
