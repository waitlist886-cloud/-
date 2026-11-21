#!/usr/bin/env python3
# 卡里有名有品阶的器物清单（11-21，背包图标那一轮）：从打好的四纪大框里抽。
#   python -I -X utf8 底稿/图标/tools/item_inventory.py [卡.json]   写 底稿/图标/器物清单.tsv，印各档各类的数
# 认三种写法：
#   一、底卡遗物和遗物套装：正文里「## 剑·半拍长歌｜Legend」这样的小标题（类·名｜阶）。
#   二、四纪「装备与名器」：标题「# 纷争纪·名器｜莫菈的骨铃」，阶照正文判（传奇神器→Legend，英雄兵装→Epic，写了 Unique 的→Unique）。
#   三、别的条里「【品阶判据】Epic」这一类写法的，取标题。
import collections
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
card = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框.json')
lb = json.load(open(card, encoding='utf-8'))['prompt']['lorebook']
TIERS = ['Normal', 'Rare', 'Epic', 'Legend', 'Unique']
ERA = lambda f, h: next((e for e in ['月银纪', '纷争纪', '山铜纪', '迷宫纪'] if e in (h + f)), '底卡')


def txt(x):
    return x.get('content') or '\n'.join(c.get('content', '') for c in (x.get('contents') or []))


rows, seen = [], set()
for x in lb:
    t = txt(x)
    head = t.split('\n', 1)[0].lstrip('# ').strip()
    folder = x.get('folder', '')
    for m in re.finditer(r'(?m)^## ([^\n·｜#]{1,6})·([^\n｜]{1,16})｜(Normal|Rare|Epic|Legend|Unique)\s*$', t):
        kind, name, tier = m.groups()
        if name not in seen:
            seen.add(name)
            rows.append((name, kind, tier, ERA(folder, head), head))
    m = re.match(r'(\S+?)·名器｜(\S+)', head)
    if m and m.group(2) not in seen:
        tier = 'Unique' if 'Unique' in t[:1500] else 'Legend' if re.search(r'传奇神器|Legend', t[:1500]) else 'Epic'
        seen.add(m.group(2))
        rows.append((m.group(2), '', tier, m.group(1), head))
    m = re.search(r'【品阶判据】\s*(Normal|Rare|Epic|Legend|Unique)', t)
    if m:
        nm = re.search(r'「([^」]{1,16})」', head)
        name = nm.group(1) if nm else head.split('｜')[-1]
        if name not in seen:
            seen.add(name)
            kind = re.search(r'｜(\S{1,4})「', head)
            rows.append((name, kind.group(1) if kind else '', m.group(1), ERA(folder, head), head))
out = os.path.join(ROOT, '底稿', '图标', '器物清单.tsv')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write('名字\t形制\t品阶\t纪\t出处条目\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')
print('一共 %d 件，写了 %s' % (len(rows), out))
print('品阶', collections.Counter(r[2] for r in rows))
print('纪', collections.Counter(r[3] for r in rows))
print('形制', collections.Counter(r[1] for r in rows).most_common(30))
