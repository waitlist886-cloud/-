#!/usr/bin/env python3
# 把八份交稿里收下的旅伴生来星并进命星池（小样_外壳/data/stars.json）。
#   python -I -X utf8 tools/merge.py [--dry]
# 一颗星从它头一回出现的那一页那一纪、那一年起进池子，往后各纪都在（last_era 写了的到那一纪为止）。
# 并进去的星带 "src": "companion"，重跑先拿掉上一回并的，原来那 168 颗一个字不动。
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(WORK, '..', '..', '..', '..', '..'))
STARS = os.path.join(ROOT, '底稿', '门面', '小样_外壳', 'data', 'stars.json')
ORDER = ['moon', 'strife', 'bronze', 'maze']
PARTS = [e + '_' + k for e in ORDER for k in 'ab']
# 种族挡：{星名: ["demon:夜翼", ...]}，长在身子上、别族说不通的才写（shell.js raceFits）
NP = os.path.join(WORK, '种族挡.json')
NEED = json.load(open(NP, encoding='utf-8')) if os.path.exists(NP) else {}


def main():
    dry = '--dry' in sys.argv
    d = json.load(open(STARS, encoding='utf-8'))
    base = [s for s in d['stars'] if s.get('src') != 'companion']
    names = {s['name'] for s in base}
    add, drop, miss = [], 0, []
    for part in PARTS:
        mp = os.path.join(WORK, '材料', part + '.json')
        gp = os.path.join(WORK, '交稿', part + '.json')
        if not os.path.exists(gp):
            miss.append(part)
            continue
        mat = {m['name']: m for m in json.load(open(mp, encoding='utf-8'))}
        for g in json.load(open(gp, encoding='utf-8')):
            if not g.get('keep'):
                drop += 1
                continue
            m = mat[g['name']]
            if g['name'] in names:
                drop += 1
                continue
            names.add(g['name'])
            i0 = ORDER.index(m['era'])
            i1 = ORDER.index(g['last_era']) if g.get('last_era') else len(ORDER) - 1
            eras = {}
            for k in ORDER[i0:i1 + 1]:
                v = {}
                if k == m['era']:
                    v['from'] = m['from']
                if g.get('note'):
                    v['note'] = g['note']
                eras[k] = v
            rec = {'id': 'c_%s_%03d' % (part, len(add) + 1), 'name': g['name'], 'type': m['type'], 'tier': g['tier'],
                   'desc': g['desc'], 'eras': eras, 'src': 'companion', 'from_page': m['page']}
            if NEED.get(g['name']):
                rec['need'] = NEED[g['name']]
            add.append(rec)
    if miss:
        print('还没交：', ' '.join(miss))
    d['stars'] = base + add
    print('原有 %d，并进 %d，不收 %d，合计 %d' % (len(base), len(add), drop, len(d['stars'])))
    # 各纪各年池子多大
    for era, years in [('moon', [1, 1001, 3001, 6007, 9900]), ('strife', [1, 301, 1051, 4501, 8801, 10801]), ('bronze', [2, 580, 862]), ('maze', [2, 600, 971, 1001])]:
        row = []
        for y in years:
            c = {'Special': 0, 'Passive': 0}
            for s in d['stars']:
                if s['type'] not in c:
                    continue
                e = (s.get('eras') or {}).get(era) if s.get('eras') else {}
                if isinstance(e, list):
                    e = [v for v in e if v and (v.get('from') is None or v['from'] <= y)]
                    e = e[-1] if e else None
                if e is None:
                    continue
                if (e.get('from') is not None and y < e['from']) or (e.get('to') is not None and y > e['to']):
                    continue
                c[s['type']] += 1
            row.append('%d年 S%d P%d' % (y, c['Special'], c['Passive']))
        print(' ', era, '｜'.join(row))
    if not dry:
        d['about'] = d['about'].split('（11-24 收旅伴')[0] + '（11-24 收旅伴的生来星：src 为 companion 的 %d 颗是四纪各页旅伴的 Special、Passive 洗成通用的，从头一回出现那一页那一年起进池，往后各纪都在，见 第二轮/建档/命星池_旅伴星/。）' % len(add)
        json.dump(d, open(STARS, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
        print('写了', STARS)


main()
