#!/usr/bin/env python3
# 查 Legend、Unique 的 Art 星头一段洗后还剩多少（11-16 山铜纪第五页查出来的：瓦尔德拉克的烬角破阵法，
# 头一段里“折下右角、角里攒的火压成一线、蓝焰往两边分”那一拍洗没了，只剩一句交代）。
# Special 的头一段洗稿本来就不动，这里只看 Art；Legend、Unique 的头一段写的是这一门做到头的那一件事，要留整句的画面。
#   python -I -X utf8 底稿/洗稿/全卡精炼/查星头.py <份名…>            比 活的文件夹里的 原/ 和 稿/
#   python -I -X utf8 底稿/洗稿/全卡精炼/查星头.py --repo <文件…>     比 标签 详本_11-15 和仓库里的文件
# 留下不到六成的列出来（--all 全列），主会话对着原稿看要不要补回。
import io
import json
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
ALL = '--all' in sys.argv
REPO = '--repo' in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith('--')]
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))


def leads(t):
    out = {}
    t = t.replace('\r', '')
    for m in re.finditer(r'^### ([^\n(]+?) \(Art \| (Legend|Unique)\)[^\n]*\n(.*?)(?=^### |^## |\Z)', t, re.M | re.S):
        lines = [x for x in m.group(3).split('\n') if x.strip()]
        lead = [x for x in lines if not x.startswith('【调用】') and not x.startswith('- ') and not x.startswith('>')]
        out[m.group(1).strip()] = '\n'.join(lead)
    return out


pairs = []
if REPO:
    for f in args:
        old = subprocess.run(['git', 'show', '详本_11-15:' + f], capture_output=True).stdout.decode('utf-8')
        pairs.append((f, old, open(f, encoding='utf-8').read()))
else:
    for j in args:
        d = '%s/%s' % (BASE, j)
        for fn in json.load(open(d + '/job.json', encoding='utf-8'))['files']:
            fn = os.path.basename(fn)
            pairs.append(('%s｜%s' % (j, fn), open('%s/原/%s' % (d, fn), encoding='utf-8').read(), open('%s/稿/%s' % (d, fn), encoding='utf-8').read()))
n = 0
for name, old, new in pairs:
    lo, ln = leads(old), leads(new)
    for star, a in lo.items():
        b = ln.get(star)
        if b is None:
            print('%s｜%s｜洗后找不到这颗星' % (name, star))
            n += 1
            continue
        r = han(b) / max(1, han(a))
        if ALL or r < 0.6:
            n += 1
            print('%s｜%s｜头一段 %d → %d 字（留 %d%%）' % (name, star, han(a), han(b), r * 100))
            print('   原：' + a.replace('\n', ' ')[:400])
            print('   洗：' + b.replace('\n', ' ')[:400])
print('列出 %d 颗' % n)
