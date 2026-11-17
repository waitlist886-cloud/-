#!/usr/bin/env python3
# 世界之书四纪卷的地图（11-15）：底图转 webp，各纪时代页“这一带”的地名照地点谱的坐标落点，写 共用/data/map_<卷>.json。
#   带 PIL 的 Python 跑：python prep_maps.py [moon strife bronze maze]   （不写就四卷都出）
# 从 小样_月银纪书/prep_map.py 改出来的，月银纪那三个年代照旧。底图是 底稿/地图/azgaar/ 的 build_moon_codex.sh、build_codex_three.sh 出的不带字的几张，收在 底稿/地图/样张/。
# 一纪分几个年代，一个年代一张底图；这一纪缺的那几个年代先借最近的一张顶着（方向稿第四节第4件），图下那一行写明借的是哪一年的。
# 迷宫纪卷多一个“1001 年今天”，点是状态栏地图页那一百四十一处地标（底稿/状态栏/大框/map_data.json，介绍页那一张地图的百分数，跟 Azgaar 整图同一个框）。
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
IMGS = {'moon_base': '月银纪_底图_地形.jpg', 'moon_salvis': '月银纪_底图_萨尔维斯末年_无字.jpg',
        'strife_mid': '纷争纪_底图_炮的年月_无字.jpg', 'strife_futa': '纷争纪_底图_浮塔的年月_无字.jpg',
        'bronze': '山铜纪_底图_麦的年月_无字.jpg', 'maze1001': '迷宫纪_底图_1001_无字.jpg'}
W0, H0 = 2200, 1400          # 地点谱的坐标是 Azgaar 地图坐标
S = lambda p, a, b: ['%s%02d' % (p, i) for i in range(a, b + 1)]
VOLS = {
    'moon': {'book': ('小样_月银纪书', 'moon.json'), 'ji': '月银纪', 'periods': [
        {'id': 'dawn', 'name': '天亮以前', 'sub': '祭火与万兽　1 年至 3000 年', 'img': 'moon_base', 'night': 1, 'eras': S('m', 1, 15)},
        {'id': 'day', 'name': '天亮以后', 'sub': '诸国期　3001 年至 6006 年', 'img': 'moon_base', 'night': 0, 'eras': S('m', 16, 21)},
        {'id': 'lamp', 'name': '天黑以前', 'sub': '萨尔维斯　6007 年至 10081 年', 'img': 'moon_salvis', 'night': 0, 'eras': S('m', 22, 27)}]},
    'strife': {'book': ('小样_纷争纪书', 'strife.json'), 'ji': '纷争纪', 'periods': [
        {'id': 'early', 'name': '墙立起来', 'sub': '灰、白石、灯的年月　元年至 1050 年', 'img': 'strife_mid', 'borrow': '底图借的是约 3600 年那一张，1088 年以前盐海那一片还是盐原', 'eras': S('s', 1, 10)},
        {'id': 'pao', 'name': '炮的年月', 'sub': '1051 年至 4500 年', 'img': 'strife_mid', 'eras': S('s', 11, 13)},
        {'id': 'futa', 'name': '浮塔的年月', 'sub': '4501 年至 8800 年', 'img': 'strife_futa', 'eras': S('s', 14, 16)},
        {'id': 'late', 'name': '铁狼与号角', 'sub': '8801 年至 11034 年', 'img': 'strife_futa', 'borrow': '底图借的是约 7000 年那一张', 'eras': S('s', 17, 21)}]},
    'bronze': {'book': ('小样_山铜纪书', 'bronze.json'), 'ji': '山铜纪', 'periods': [
        {'id': 'one', 'name': '一条路', 'sub': '犁、长夜、白鸦的年月　2 年至 660 年', 'img': 'bronze', 'borrow': '底图借的是约 900 年那一张，往西的路、七城和黑耀都是 661 年以后的事', 'eras': ['p1', 'p2', 'p3']},
        {'id': 'two', 'name': '两条路', 'sub': '黎明、七城的年月　661 年至 861 年', 'img': 'bronze', 'borrow': '底图借的是约 900 年那一张，黑耀 862 年才立', 'eras': ['p4', 'p5']},
        {'id': 'wheat', 'name': '麦的年月', 'sub': '862 年至 947 年', 'img': 'bronze', 'eras': ['p6']}]},
    'maze': {'book': ('小样_迷宫纪书', 'maze.json'), 'ji': '迷宫纪前传', 'periods': [
        {'id': 'early', 'name': '探井到繁荣', 'sub': '2 年至 599 年', 'img': 'maze1001', 'borrow': '底图借的是 1001 年那一张', 'eras': ['q1', 'q2', 'q3']},
        {'id': 'late', 'name': '深井到垂暮', 'sub': '600 年至 1000 年', 'img': 'maze1001', 'borrow': '底图借的是 1001 年那一张', 'eras': ['q4', 'q5', 'q6']},
        {'id': 'today', 'name': '1001 年今天', 'sub': '一百四十一处地标', 'img': 'maze1001', 'eras': [], 'lands': True}]},
}
ALIAS = {}       # 时代页的地名和地点谱写法不一样的，在这里对上：(卷, 页上的名字) → 地点谱的名字


def era_name(vol, e):
    if vol == 'moon':
        return e['label'] + '　' + e['title']
    if vol == 'strife':
        return e['label'] + '　' + e['title']
    return e['title'] + '　' + e.get('years', '').replace(' ', '')


def first_sentence(t, n=70):
    t = (t or '').strip().split('\n')[0]
    m = re.match(r'(.{8,%d}?[。！？])' % n, t)
    return m.group(1) if m else t[:n]


def prep_imgs(need):
    os.makedirs(os.path.join(HERE, 'assets', 'map'), exist_ok=True)
    for k in need:
        src = os.path.join(SRC, IMGS[k])
        if not os.path.exists(src):
            print('没有底图', src)
            continue
        dst = os.path.join(HERE, 'assets', 'map', k + '.webp')
        if os.path.exists(dst) and os.path.getmtime(dst) > os.path.getmtime(src):
            continue
        im = Image.open(src).convert('RGB')
        im = im.resize((3072, round(3072 * im.height / im.width)), Image.LANCZOS)
        im.save(dst, quality=80, method=6)
        print('底图', k, im.size, os.path.getsize(dst) // 1024, 'KB')


def build(vol):
    V = VOLS[vol]
    d, f = V['book']
    allrows = list(csv.DictReader(open(os.path.join(ROOT, '底稿', '地图', '地点谱', '合表.tsv'), encoding='utf-8'), delimiter='\t'))
    by, by_other = {}, {}
    for r in allrows:
        if not re.fullmatch(r'[\d.]+', r['地图x'] or '') or not re.fullmatch(r'[\d.]+', r['地图y'] or ''):
            continue          # 地点谱里坐标写“?”的那几处（位置没定），不落点
        names = [r['名字']] + [x for x in re.split(r'[、，；/]', r.get('别纪的叫法') or '') if x and '·' not in x and len(x) <= 8]
        for n in names:
            (by if r['纪'] == V['ji'] else by_other).setdefault(n.strip(), r)
    # 这一纪的地点谱里坐标写“?”、别的纪里同一处有坐标的（纷争纪南七段、前传吟河），借别的纪那一行的坐标
    for n, r in by_other.items():
        by.setdefault(n, r)
    D = json.load(open(os.path.join(ROOT, '底稿', '门面', d, 'data', f), encoding='utf-8'))
    eras = {e['id']: e for e in D['eras']}
    out = {'w': W0, 'h': H0, 'periods': [], 'names': {k: era_name(vol, e) for k, e in eras.items()}}
    # 每个时代页的年份起止（11-17，建档自己报年份时照它滤点）
    sys.path.insert(0, HERE)
    import build_atlas as _BA
    out['years'] = {e['id']: list(r) for e, r in zip(D['eras'], _BA.era_ranges(vol, D['eras']))}
    miss = []
    for p in V['periods']:
        pins = {}
        if p.get('lands'):
            L = json.load(open(os.path.join(ROOT, '底稿', '状态栏', '大框', 'map_data.json'), encoding='utf-8'))['lands']
            for q in L:
                pins[q['n']] = {'name': q['n'], 'x': round(q['x'], 2), 'y': round(q['y'], 2), 'kind': (q.get('lv') or ''), 'main': q.get('t') == 0,
                                'where': first_sentence(q.get('d')), 'later': '', 'eras': []}
        for eid in p['eras']:
            for pl in eras[eid].get('places', []):
                n = pl['name']
                r = by.get(ALIAS.get((vol, n), n))
                if not r:
                    miss.append((eid, n))
                    continue
                q = pins.setdefault(n, {'name': n, 'x': round(float(r['地图x']) / W0 * 100, 2), 'y': round(float(r['地图y']) / H0 * 100, 2),
                                        'kind': (pl.get('kind') or '').split('（')[0], 'main': bool(pl.get('main')), 'where': pl.get('where', ''), 'later': pl.get('later', ''), 'eras': []})
                if eid not in q['eras']:
                    q['eras'].append(eid)
        out['periods'].append({k: v for k, v in p.items() if k not in ('eras', 'lands')} | {'eras': p['eras'], 'pins': sorted(pins.values(), key=lambda x: (not x['main'], x['name']))})
    os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, 'data', 'map_%s.json' % vol), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(vol, '各年代的点', [len(p['pins']) for p in out['periods']], '对不上', len(miss))
    for m in miss:
        print('  对不上', *m)
    return {p['img'] for p in V['periods']}


if __name__ == '__main__':
    todo = sys.argv[1:] or list(VOLS)
    need = set()
    for v in todo:
        need |= build(v)
    prep_imgs(sorted(need))
