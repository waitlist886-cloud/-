#!/usr/bin/env python3
# 时代页按主线细分（11-20）：把生卒那一批（底稿/命星重审第二轮/交稿/life_*.md）并成一张表，拷进四本书的 data/life.json。
#   python -I -X utf8 底稿/门面/共用/build_life.py          写四本书的 data/life.json，报合并时对不上的
# 年份一律换成总的纪年：月银纪 Y 是 Y，月银纪前 N 是 1-N，纷争纪 N 是 10080+N，山铜纪 N 是 21113+N，迷宫纪 N 是 22059+N。
# 一个人在几页都有（旅伴跨页、年轻时一条老了一条），合成一个：生年取最早写到的，卒年取写了的那一个（几页不一样的列出来），
# 位阶节点并起来、同一阶取最早那一年，成色并起来。
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, '底稿', '命星重审第二轮', '交稿')
OFF = {'月银纪': 0, '纷争纪': 10080, '山铜纪': 21113, '迷宫纪': 22059}
RANKS = ['启源', '共鸣', '灵格', '极境', '英雄', '传奇']
QUALS = ['寻常', '稳', '漂亮', '极品']


def year(s):
    s = (s or '').strip()
    m = re.search(r'(月银纪|纷争纪|山铜纪|迷宫纪)(前)?(元|\d+)', s)
    if not m:
        return None
    n = 1 if m.group(3) == '元' else int(m.group(3))
    if m.group(2):
        return 1 - n
    return OFF[m.group(1)] + n


def parse(line):
    f = [x.strip() for x in line.split('｜')]
    if len(f) < 3 or f[0] != '人':
        return None
    d = {'name': f[1], 'r': f[2]}
    for x in f[3:]:
        k, _, v = x.partition('：')
        if k == '生':
            d['b'] = year(v)
        elif k == '卒':
            d['d'] = year(v)
        elif k == '死法':
            d['h'] = v
        elif k == '凝名':
            d['n'] = year(v)
        elif k == '传奇':
            d['l'] = year(v)
        elif k == '位阶':
            ks = []
            for seg in re.split(r'[;；]', v):
                m = re.match(r'\s*(.+?)[:：]\s*(启源|共鸣|灵格|极境|英雄|传奇)', seg)
                if m and year(m.group(1)) is not None:
                    ks.append([year(m.group(1)), m.group(2)])
            d['k'] = ks
        elif k == '成色':
            q = {}
            for seg in re.split(r'[;；]', v):
                m = re.match(r'\s*(启源|共鸣|灵格|极境|英雄|传奇)[:：]\s*(寻常|稳|漂亮|极品)', seg)
                if m and m.group(2) != '寻常':
                    q[m.group(1)] = m.group(2)
            d['q'] = q
        elif k == '天生':
            m = re.search(r'\d+', v)
            d['s'] = int(m.group(0)) if m else None
    return d


BOOK = {'月银纪': '月银纪', '诸国期': '月银纪', '萨尔维斯': '月银纪', '纷争纪': '纷争纪', '山铜纪': '山铜纪', '迷宫纪前传': '迷宫纪'}


def main():
    for b in ('月银纪', '纷争纪', '山铜纪', '迷宫纪'):
        one(b)


def one(book):
    people, clash, n = {}, [], 0
    for f in sorted(glob.glob(os.path.join(SRC, 'life_*.md'))):
        if BOOK[re.match(r'life_(.+)_\d+_\d+\.md', os.path.basename(f)).group(1)] != book:
            continue
        for line in open(f, encoding='utf-8'):
            d = parse(line.strip())
            if not d:
                continue
            n += 1
            nm = d.pop('name')
            o = people.get(nm)
            if not o:
                people[nm] = {k: v for k, v in d.items() if v not in (None, '', [], {})}
                continue
            if d.get('b') is not None and (o.get('b') is None or d['b'] < o['b']):
                o['b'] = d['b']
            if d.get('d') is not None:
                if o.get('d') is not None and o['d'] != d['d']:
                    clash.append('%s 卒年 %s / %s' % (nm, o['d'], d['d']))
                o['d'] = max(o.get('d') or d['d'], d['d'])
                o['h'] = d.get('h') or o.get('h')
            for k in ('n', 'l', 's'):
                if d.get(k) is not None and o.get(k) is None:
                    o[k] = d[k]
            ks = {r: y for y, r in o.get('k', [])}
            for y, r in d.get('k', []):
                ks[r] = min(ks.get(r, y), y)
            o['k'] = sorted([[y, r] for r, y in ks.items()], key=lambda x: (x[0], RANKS.index(x[1])))
            q = dict(o.get('q', {}))
            q.update(d.get('q', {}))
            if q:
                o['q'] = q
    alias, dup = {}, set()
    for nm in people:
        s = nm.split('·')[0]
        if s != nm:
            if s in alias and alias[s] != nm:
                dup.add(s)
            alias[s] = nm
    for s in dup:
        alias.pop(s, None)
    out = {'people': people, 'alias': alias}
    p = os.path.join(HERE, '..', '小样_%s书' % book, 'data', 'life.json')
    json.dump(out, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, separators=(',', ':'))
    print('==', book)
    have = lambda k: sum(1 for v in people.values() if v.get(k) is not None)
    print('行 %d，人 %d（有生年 %d，有卒年 %d，凝名 %d，到传奇 %d，有位阶节点 %d），简称 %d，简称撞了 %d' % (
        n, len(people), have('b'), have('d'), have('n'), have('l'), sum(1 for v in people.values() if v.get('k')), len(alias), len(dup)))
    print('卒年对不上', len(clash))
    for c in clash[:40]:
        print('  ', c)


if __name__ == '__main__':
    main()
