#!/usr/bin/env python3
# 世界之书月银纪卷的地图（11-15）：底图转 webp，时代页“这一带”的地名照地点谱的坐标落点，写 data/map.json。
#   带 PIL 的 Python 跑：python prep_map.py
# 底图是 底稿/地图/azgaar/build_moon_codex.sh 出的两张（地形，萨尔维斯末年不带字），收在 底稿/地图/样张/。
# 三个年代：天亮以前（第一到十五歌，地形底图压暗成夜里）、天亮以后（诸国期六页，地形底图）、天黑以前（萨尔维斯六页，萨尔维斯末年那一张）。
import csv
import io
import json
import os
import re
import sys
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, '底稿', '地图', '样张')
MAPS = {'moon_base': '月银纪_底图_地形.jpg', 'moon_salvis': '月银纪_底图_萨尔维斯末年_无字.jpg'}
W0, H0 = 2200, 1400          # 地点谱的坐标是 Azgaar 地图坐标
PERIODS = [
    {'id': 'dawn', 'name': '天亮以前', 'sub': '祭火与万兽　1 年至 3000 年', 'img': 'moon_base', 'night': 1, 'eras': ['m%02d' % i for i in range(1, 16)]},
    {'id': 'day', 'name': '天亮以后', 'sub': '诸国期　3001 年至 6006 年', 'img': 'moon_base', 'night': 0, 'eras': ['m%02d' % i for i in range(16, 22)]},
    {'id': 'lamp', 'name': '天黑以前', 'sub': '萨尔维斯　6007 年至 10081 年', 'img': 'moon_salvis', 'night': 0, 'eras': ['m%02d' % i for i in range(22, 28)]},
]
ALIAS = {}       # 时代页的地名和地点谱写法不一样的，在这里对上：页上的名字 → 地点谱的名字


def main():
    os.makedirs(os.path.join(HERE, 'assets', 'map'), exist_ok=True)
    for k, f in MAPS.items():
        im = Image.open(os.path.join(SRC, f)).convert('RGB')
        im = im.resize((3072, round(3072 * im.height / im.width)), Image.LANCZOS)
        im.save(os.path.join(HERE, 'assets', 'map', k + '.webp'), quality=80, method=6)
    rows = [r for r in csv.DictReader(open(os.path.join(ROOT, '底稿', '地图', '地点谱', '合表.tsv'), encoding='utf-8'), delimiter='\t') if r['纪'] == '月银纪']
    by = {}
    for r in rows:
        if not re.fullmatch(r'[\d.]+', r['地图x'] or '') or not re.fullmatch(r'[\d.]+', r['地图y'] or ''):
            continue          # 地点谱里坐标写“?”的那几处（位置没定），不落点
        names = [r['名字']] + [x for x in re.split(r'[、，；/]', r.get('别纪的叫法') or '') if x and '·' not in x and len(x) <= 8]
        for n in names:
            by.setdefault(n.strip(), r)
    D = json.load(open(os.path.join(HERE, 'data', 'moon.json'), encoding='utf-8'))
    eras = {e['id']: e for e in D['eras']}
    out, miss = {'w': W0, 'h': H0, 'periods': [], 'pins': {}}, []
    for p in PERIODS:
        pins = {}
        for eid in p['eras']:
            for pl in eras[eid].get('places', []):
                n = pl['name']
                r = by.get(ALIAS.get(n, n))
                if not r:
                    miss.append((eid, n))
                    continue
                q = pins.setdefault(n, {'name': n, 'x': round(float(r['地图x']) / W0 * 100, 2), 'y': round(float(r['地图y']) / H0 * 100, 2),
                                        'kind': (pl.get('kind') or '').split('（')[0], 'main': bool(pl.get('main')), 'where': pl.get('where', ''), 'later': pl.get('later', ''), 'eras': []})
                if eid not in q['eras']:
                    q['eras'].append(eid)
        out['periods'].append({k: v for k, v in p.items() if k != 'eras'} | {'eras': p['eras'], 'pins': sorted(pins.values(), key=lambda x: (not x['main'], x['name']))})
    json.dump(out, open(os.path.join(HERE, 'data', 'map.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('三个年代的点', [len(p['pins']) for p in out['periods']], '对不上', len(miss))
    for m in miss:
        print('  对不上', *m)


if __name__ == '__main__':
    main()
