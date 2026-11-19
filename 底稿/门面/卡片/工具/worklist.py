# -*- coding: utf-8 -*-
"""门面卡片跟新数据对一遍，出一张要改什么的单子（写 worklist.json，屏幕上只印数和名单）。
一，分类变了的（旅伴改相遇、相遇改旅伴），书里新有的人没卡片，卡片里书里没有了的人。
二，照旧是旅伴的：卡片上的星跟档案对不对（名字、类、档），岁数、位阶对不对。
11-18 门面卡片跟上那一轮写的。源稿改了旅伴、星以后先重跑各本的 build_data.py，再跑它看卡片差在哪。
  python -I -X utf8 底稿/门面/卡片/工具/worklist.py [单子写到哪.json]
11-18 收完以后还剩的是有意留的：岁数 3（珊瑟、霍德·断崖、伦佐·晴凿，卡片写的是外表或另一年的岁数），位阶 9。"""
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
F = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')).replace('\\', '/') + '/'
BOOK = {'月银纪': ('小样_月银纪书', 'moon.json'), '纷争纪': ('小样_纷争纪书', 'strife.json'),
        '山铜纪': ('小样_山铜纪书', 'bronze.json'), '迷宫纪': ('小样_迷宫纪书', 'maze.json')}
out = {}
tot = {'旅伴改相遇': 0, '相遇改旅伴': 0, '新人没卡片': 0, '卡片多出来': 0, '星对不上': 0, '岁数对不上': 0, '位阶对不上': 0}
for ji, (d, f) in BOOK.items():
    D = json.load(open(F + d + '/data/' + f, encoding='utf-8'))
    for e in D['eras']:
        i = e['id']
        fp = F + '卡片/' + ji + '/' + i + '.json'
        if not os.path.exists(fp):
            continue
        C = json.load(open(fp, encoding='utf-8'))
        pf = F + d + '/data/prof/' + i + '.json'
        P = json.load(open(pf, encoding='utf-8')) if os.path.exists(pf) else {}
        cast = {c['name']: c for c in e['cast']}
        meet = {m['name']: m for m in (e.get('meet') or [])}
        ppl = C.get('people', {})
        w = {'to_meet': [], 'to_cast': [], 'new': [], 'gone': [], 'stars': [], 'age': [], 'rank': []}
        for n in cast:
            if n not in ppl:
                w['new'].append((n, 'cast'))
            elif ppl[n].get('kind') != 'cast':
                w['to_cast'].append(n)
        for n in meet:
            if n not in ppl:
                w['new'].append((n, 'meet'))
            elif ppl[n].get('kind') != 'meet':
                w['to_meet'].append(n)
        for n in ppl:
            if n not in cast and n not in meet:
                w['gone'].append(n)
        for n, c in cast.items():
            if n not in ppl or ppl[n].get('kind') != 'cast':
                continue
            p = P.get(n) or {}
            ps = {s['name']: s for s in p.get('stars', [])}
            for s in ppl[n].get('stars', []):
                t = ps.get(s['name'])
                if not t:
                    w['stars'].append({'who': n, 'card': s, 'prof': [(x['name'], x['kind'], x['tier'], x['text']) for x in p.get('stars', [])]})
                elif t['tier'] != s.get('tier') or t['kind'] != s.get('kind'):
                    w['stars'].append({'who': n, 'card': s, 'fix': (t['kind'], t['tier'])})
            age = c.get('age')
            h = ' '.join(ppl[n].get('head', []))
            m = re.search(r'(\d+)\s*岁', h)
            if age is not None and m and abs(int(m.group(1)) - age) > 1 and '外表' not in h:
                w['age'].append((n, h, age))
            rk = p.get('rank', '')
            tg = ' '.join(ppl[n].get('tags', []))
            m1 = re.search(r'(启源|共鸣|灵格|极境|英雄|传奇)', rk)
            m2 = re.search(r'(启源|共鸣|灵格|极境|英雄|传奇)', tg)
            if m1 and m2 and m1.group(1) != m2.group(1):
                w['rank'].append((n, tg, rk))
        if any(w.values()):
            out[ji + ' ' + i] = w
        tot['旅伴改相遇'] += len(w['to_meet']); tot['相遇改旅伴'] += len(w['to_cast']); tot['新人没卡片'] += len(w['new'])
        tot['卡片多出来'] += len(w['gone']); tot['星对不上'] += len(w['stars']); tot['岁数对不上'] += len(w['age']); tot['位阶对不上'] += len(w['rank'])
if len(sys.argv) > 1:
    json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(tot)
for k, w in out.items():
    bits = []
    if w['to_meet']: bits.append('改相遇 ' + '、'.join(w['to_meet']))
    if w['to_cast']: bits.append('改旅伴 ' + '、'.join(w['to_cast']))
    if w['new']: bits.append('新 ' + '、'.join('%s(%s)' % x for x in w['new']))
    if w['gone']: bits.append('多 ' + '、'.join(w['gone']))
    if w['stars']: bits.append('星 %d' % len(w['stars']))
    if w['age']: bits.append('岁 ' + '、'.join('%s 卡[%s] 书%s' % x for x in w['age']))
    if w['rank']: bits.append('阶 ' + '、'.join('%s 卡[%s] 书[%s]' % x for x in w['rank']))
    print(k, '｜', '｜'.join(bits))
