#!/usr/bin/env python3
# 命星池收旅伴的生来星（11-24，用户：“special和passive跟着纪元走，越往后越多，不提前出现”，看了只多五颗以后回“洗”）。
# 从四纪各页抽 Special、Passive 的星条，一页记一个起始年（这一页那一段在建档里的 from），同名的只留头一回出现的那一页，
# 已经在命星池里的名字（1001 年名和各纪名）跳过。出 材料/<份>.json，给子任务洗。
#   python -I -X utf8 tools/extract.py
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(WORK, '..', '..', '..', '..', '..'))
STARS = os.path.join(ROOT, '底稿', '门面', '小样_外壳', 'data', 'stars.json')

# 页 → (纪, 这一页在建档里的起始年, 份)
PAGES = []
for f in sorted(os.listdir(os.path.join(ROOT, '月银纪史诗'))):
    if re.match(r'第.+歌_.+\.md$', f):
        PAGES.append(('月银纪史诗/' + f, 'moon', 1001, 'moon'))
for f, y in [('一_晨祷', 3001), ('二_午祷上', 3001), ('三_午祷下', 3001), ('四_晚祷上', 3001), ('五_晚祷下', 3001), ('六_夜祷', 3001)]:
    PAGES.append(('诸国期/诸国期时段_%s.md' % f, 'moon', y, 'moon'))
for f, y in [('一_崛起上', 6007), ('二_崛起下', 6600), ('三_帝国', 8081), ('四_魔族之世', 9100), ('五_末年上', 9900), ('六_末年下', 9900)]:
    PAGES.append(('萨尔维斯/萨尔维斯时段_%s.md' % f, 'moon', y, 'moon'))
for f, y in [('一_灰的年月', 1), ('二_白石的年月', 121), ('三_灯的年月', 301), ('四_炮的年月', 1051), ('五_浮塔的年月', 4501), ('六_铁狼的年月', 8801), ('七_号角的年月', 10801)]:
    PAGES.append(('纷争纪/纷争纪时段_%s.md' % f, 'strife', y, 'strife'))
for f, y in [('一_犁的年月', 2), ('二_长夜的年月', 301), ('三_白鸦的年月', 580), ('四_黎明的年月', 661), ('五_七城的年月', 742), ('六_麦的年月', 862)]:
    PAGES.append(('山铜纪/山铜纪时段_%s.md' % f, 'bronze', y, 'bronze'))
for f, y in [('一_探井的年月', 2), ('二_共约的年月', 101), ('三_繁荣的年月', 318), ('四_深井的年月', 600), ('五_黑潮的年月', 850), ('六_垂暮的年月', 971)]:
    PAGES.append(('迷宫纪前传/迷宫纪前传时段_%s.md' % f, 'maze', y, 'maze'))

HEAD = re.compile(r'^### (.+?) \((Special|Passive) \| (Normal|Rare|Epic|Legend|Unique)\)\s*$')


def main():
    pool = json.load(open(STARS, encoding='utf-8'))['stars']
    have = set()
    for s in pool:
        have.add(s['name'])
        for e in (s.get('eras') or {}).values():
            for v in (e if isinstance(e, list) else [e]):
                if v and v.get('name'):
                    have.add(v['name'])
    seen, out, dup, skip = {}, {}, 0, 0
    for rel, era, y, part in PAGES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            raise SystemExit('没有这一页：' + rel)
        L = open(p, encoding='utf-8').read().split('\n')
        i = 0
        while i < len(L):
            m = HEAD.match(L[i])
            if not m:
                i += 1
                continue
            j = i + 1
            while j < len(L) and not L[j].startswith('### ') and not L[j].startswith('## '):
                j += 1
            name, typ, tier = m.group(1).strip(), m.group(2), m.group(3)
            body = '\n'.join(x for x in L[i + 1:j] if not x.startswith('条目设置')).strip()
            i = j
            if name in have:
                skip += 1
                continue
            if name in seen:
                seen[name]['also'].append(rel.split('/')[-1][:-3])
                dup += 1
                continue
            rec = {'name': name, 'type': typ, 'tier': tier, 'era': era, 'from': y, 'page': rel.split('/')[-1][:-3], 'also': [], 'text': body}
            seen[name] = rec
            out.setdefault(part, []).append(rec)
    os.makedirs(os.path.join(WORK, '材料'), exist_ok=True)
    for part, recs in out.items():
        json.dump(recs, open(os.path.join(WORK, '材料', part + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(part, len(recs), '颗', sum(1 for r in recs if r['type'] == 'Special'), 'Special', sum(1 for r in recs if r['tier'] == 'Unique'), 'Unique')
    print('合计', sum(len(v) for v in out.values()), '；同名后出现的', dup, '；池子里已有的', skip)


main()
