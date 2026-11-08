# 四纪地点谱合表：python -I -X utf8 合表.py  （在 底稿/地图/地点谱/ 下跑，读 月银纪/纷争纪/山铜纪/迷宫纪前传.tsv，缺的跳过）
# 写三样：
#   合表.tsv        四纪所有行加一栏纪，坐标照 1001 年地标表统一（1001年叫什么 对得上地标表的，坐标抄地标表）
#   主要地点谱.md   照 1001 年的名字归组：同一个位置在各纪叫什么、哪几年、什么类，一处一节
#   坐标对不上.tsv  同一个 1001 年名字、表里写的坐标跟地标表差出 40 以上的行
import csv
import os
import re
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪前传']
REF = os.path.join(HERE, '..', '参考', '1001年地标.tsv')

ref = {}
with open(REF, encoding='utf8') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        ref[r['名字']] = (float(r['地图x']), float(r['地图y']))


def norm(s):
    return re.sub(r'\s+', '', s or '')


def find_ref(name1001):
    """1001年叫什么 那一栏可能是 名字（全名）、几个名字、或者带括号的说明，挑出地标表里有的那一个。"""
    s = norm(name1001)
    if not s or s.startswith('无'):
        return None
    cands = [s] + re.split(r'[、，,；;（）()／/]', s)
    for c in cands:
        c = c.strip()
        if c in ref:
            return c
    for c in cands:
        c = c.strip()
        if len(c) < 2:
            continue
        for k in ref:
            if c in k or (len(k) >= 3 and k in c):
                return k
    return None


rows = []
for era in ERAS:
    p = os.path.join(HERE, era + '.tsv')
    if not os.path.exists(p):
        print('跳过（还没有）', era)
        continue
    with open(p, encoding='utf8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            r = {k: (v or '').strip() for k, v in r.items() if k}
            r['纪'] = era
            r['对上的1001地标'] = find_ref(r.get('1001年叫什么', '')) or ''
            rows.append(r)

bad = []
for r in rows:
    k = r['对上的1001地标']
    if not k:
        continue
    rx, ry = ref[k]
    try:
        x, y = float(r['地图x']), float(r['地图y'])
        d = ((x - rx) ** 2 + (y - ry) ** 2) ** 0.5
    except ValueError:
        d = None
    if d is not None and d > 40:
        bad.append((r['纪'], r['名字'], k, r['地图x'], r['地图y'], rx, ry, round(d)))

# 统一主次：同一个位置（对上同一处 1001 年地标）在月银纪、纷争纪、山铜纪、前传、1001 年五段里出现三段以上算主要；
# 对不上地标的照这一行自己的 别纪的叫法 数，连自己三纪以上算主要，别的次要
eras_of = defaultdict(set)
for r in rows:
    if r['对上的1001地标']:
        eras_of[r['对上的1001地标']].add(r['纪'])
for r in rows:
    k = r['对上的1001地标']
    if k:
        n = len(eras_of[k]) + 1
    else:
        other = {m.split('·')[0] for m in re.split(r'[、，,；;]', r.get('别纪的叫法', '')) if '·' in m}
        other.discard(r['纪'])
        n = 1 + len(other)
    r['统一主次'] = '主要' if n >= 3 else '次要'

cols = ['纪', '名字', '统一主次', '时段与年份', '类', '主要还是次要', '1001年叫什么', '对上的1001地标', '别纪的叫法', '位置', '地图x', '地图y', '出处', '要说明的']
with open(os.path.join(HERE, '合表.tsv'), 'w', encoding='utf8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerow(cols)
    for r in rows:
        w.writerow([r.get(c, '') for c in cols])

with open(os.path.join(HERE, '坐标对不上.tsv'), 'w', encoding='utf8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerow(['纪', '名字', '对上的1001地标', '表里x', '表里y', '地标x', '地标y', '差'])
    for b in sorted(bad, key=lambda t: -t[-1]):
        w.writerow(b)

groups = OrderedDict()
for r in rows:
    k = r['对上的1001地标']
    if k:
        groups.setdefault(k, []).append(r)
order = sorted(groups, key=lambda k: (-len({r['纪'] for r in groups[k]}), k))
cnt = defaultdict(int)
with open(os.path.join(HERE, '主要地点谱.md'), 'w', encoding='utf8') as f:
    f.write('# 主要地点谱（四纪地点谱合表，脚本生成）\n\n')
    f.write('照 1001 年的地标归组，一处一节：同一个位置在各纪叫什么、哪几年、什么类。几纪都有的排前头。坐标是 1001 年地标表的。\n\n')
    for k in order:
        g = groups[k]
        eras = [e for e in ERAS if any(r['纪'] == e for r in g)]
        cnt[len(eras)] += 1
        x, y = ref[k]
        f.write(f'## {k}（{x:g},{y:g}）｜{"、".join(eras)}\n\n')
        for e in ERAS:
            for r in g:
                if r['纪'] != e:
                    continue
                f.write(f'- {e}·{r["名字"]}｜{r["类"]}｜{r["时段与年份"]}\n')
        f.write('\n')
per = defaultdict(lambda: [0, 0, 0])
for r in rows:
    per[r['纪']][0 if r['统一主次'] == '主要' else 1] += 1
    if r.get('地图x', '') in ('', '?') or r.get('地图y', '') in ('', '?'):
        per[r['纪']][2] += 1
print('各纪 主要/次要/没坐标', dict(per))
print('行', len(rows), '对上地标', sum(1 for r in rows if r['对上的1001地标']), '组', len(groups), '几纪', dict(cnt), '坐标差出40的', len(bad))
