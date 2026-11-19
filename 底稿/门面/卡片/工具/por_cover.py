# -*- coding: utf-8 -*-
"""四本书里谁有立绘、谁没有：照各本 data/<书>.json 的名单和 data/have.json（档案页有图的键）、data/pa.json（时代页人像拼图）。
出 por_cover.json：{纪: {名字: {roles:[(时代,类)], key, pset, have}}}，并印各纪的数。
11-18 立绘预留那一轮写的，底稿/立绘/没有立绘的人_11-18.tsv 就是照它出的。
  python -I -X utf8 底稿/门面/卡片/工具/por_cover.py [写到哪.json]     不给就写到系统临时目录的 aldran_por_cover.json，por_need.py 从那里读"""
import io, json, os, sys, collections, tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
F = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')).replace('\\', '/') + '/'
BOOK = {'月银纪': ('小样_月银纪书', 'moon.json'), '纷争纪': ('小样_纷争纪书', 'strife.json'),
        '山铜纪': ('小样_山铜纪书', 'bronze.json'), '迷宫纪': ('小样_迷宫纪书', 'maze.json')}
OUT = {}
for ji, (d, f) in BOOK.items():
    D = json.load(open(F + d + '/data/' + f, encoding='utf-8'))
    hp = F + d + '/data/have.json'
    have = set(json.load(open(hp, encoding='utf-8')).get('ps', [])) if os.path.exists(hp) else None
    pa = json.load(open(F + d + '/data/pa.json', encoding='utf-8')) if os.path.exists(F + d + '/data/pa.json') else {}
    pakeys = set()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (dict, list)):
                    walk(v)
                pakeys.add(k)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(pa)
    P = {}
    for e in D['eras']:
        for kind, lab in (('cast', '旅伴'), ('meet', '相遇'), ('legends', '传奇')):
            for c in e.get(kind) or []:
                r = P.setdefault(c['name'], {'roles': [], 'key': None, 'pset': None, 'have': False})
                r['roles'].append([e['id'], lab])
                if c.get('key'):
                    r['key'], r['pset'] = c['key'], c.get('pset')
                    if have is not None and c['key'] in have:
                        r['have'] = True
                    elif have is None and (c['key'] in pakeys):
                        r['have'] = True
    OUT[ji] = P
    cnt = collections.Counter()
    for n, r in P.items():
        labs = {x[1] for x in r['roles']}
        lab = '旅伴' if '旅伴' in labs else '传奇' if '传奇' in labs else '相遇'
        cnt[(lab, '有图' if r['have'] else ('有键没图' if r['key'] else '没有键'))] += 1
    print(ji, '一共', len(P), '人', 'have.json' if have is not None else '（没有 have.json，照 pa.json 的键）')
    for k in sorted(cnt):
        print('   ', k[0], k[1], cnt[k])
dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), 'aldran_por_cover.json')
json.dump(OUT, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('写了', dst)
