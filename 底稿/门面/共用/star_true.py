#!/usr/bin/env python3
# 命星的俗称和真名（11-19 夜）。
#
# 迷宫纪 420 年以前没有面板，世人只叫得出一颗星露出来的那一头的俗称（泥中之握），它在世界那里的真名（万夜一晓）
# 写在卡里，四纪页上那一条只给 AI 的话接过去。介绍页的档案剧透关着照旧显示俗称，剧透开了显示真名。
#
#   python -I -X utf8 底稿/门面/共用/star_true.py make     读四纪各页和打好的卡，写 共用/data/star_true.json
#   python -I -X utf8 底稿/门面/共用/star_true.py apply    把对照套进四本书的 data/prof/*.json、data/cards.json
#
# 各本书 build_data.py、prep_cards.py 重跑以后，这一步要跟着再跑一回（apply 只添 tn、tx、gr、lin 四个字段，跑几回都一样）。
# 字段：tn 真名，tx 真名那一句（卡里那颗星的说明，“头一点……那时候叫……”那一截拿掉），
#       gr 只挂在 Art 上，1001 年卡里这个人手里那一门，lin 为真是卡里那一门的传承写明从这一门长成。
import glob
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
CARD = os.path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框.json')
OUT = os.path.join(HERE, 'data', 'star_true.json')
BOOKS = ['小样_月银纪书', '小样_纷争纪书', '小样_山铜纪书', '小样_迷宫纪书']
PAGES = ['山铜纪/山铜纪时段_*.md', '迷宫纪前传/迷宫纪前传时段_*.md', '纷争纪/纷争纪时段*.md']
SEC = re.compile(r'^### (\S+) \((Special|Passive|Art) \| (\w+)\)\n(.*?)(?=^### |^## |\Z)', re.S | re.M)
LINK = re.compile(r'生来的?【([^】]+)】|往后长成的就是【([^】]+)】|长成后还(?:叫|是)【([^】]+)】|后来长成【([^】]+)】')
LEG = re.compile(r'^- (Special|Passive|Art)：【([^】]+)】\((\w+)\)[^｜]*｜([^｜\n]*)(.*)$', re.M)


def walk(o):
    if isinstance(o, dict):
        if isinstance(o.get('content'), str):
            yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def gist(desc):
    """卡里那颗星的头一段，拿掉“头一点是……那时候叫……”那一截。"""
    out = []
    for sent in [s for s in desc.split('。') if s.strip()]:
        parts = sent.split('，')
        cut = next((i for i, p in enumerate(parts) if '头一点' in p or '那时候叫' in p or '当时只叫' in p), None)
        if cut is not None:
            if cut:
                out.append('，'.join(parts[:cut]))
            break
        out.append(sent)
    return '。'.join(out).strip() + '。' if out else ''


def legends():
    """卡里凡世至强（和魔王）那几条：人名 → {kind: (名, 阶, 说明, 整行)}。"""
    card = json.load(open(CARD, encoding='utf-8'))
    out = {}
    for e in walk(card):
        c = e['content']
        head = c.split('\n', 1)[0]
        if not (head.startswith('## 凡世至强：') or head.startswith('## 七神与魔王模块')):
            continue
        who = re.sub(r'（.*$', '', head.split('·')[-1] if '·' in head else head).strip()
        if '·' in head:
            segs = [s.strip() for s in re.sub(r'（[^）]*）', '', head.split('：', 1)[1]).split('·')]
            who = '·'.join(segs[-2:]) if len(segs) >= 3 and len(segs[-1]) <= 3 else segs[-1]
            who = who.replace('魔王', '').strip()
        d = out.setdefault(who, {})
        for m in LEG.finditer(c):
            kind, name, tier, desc, rest = m.groups()
            d.setdefault(kind, (name, tier, desc, rest))
    return out


def short(name):
    return re.sub(r'^(教皇|大审判官|首席医官|大祭司|游侠将军|影舞宗师|大宗匠|重装大将|界门归还者|深井绘界师|残响缝星者|流浪女佣兵|隐居学者|真龙)', '', name).split('·')[0].strip()


def make():
    legs = legends()
    by_true = {}
    for who, d in legs.items():
        for kind in ('Special', 'Passive'):
            if kind in d:
                by_true.setdefault(d[kind][0], []).append((who, kind))
    stars, seen = [], set()
    for pat in PAGES:
        for p in sorted(glob.glob(os.path.join(ROOT, pat))):
            t = open(p, encoding='utf-8').read()
            for m in SEC.finditer(t):
                name, kind, tier, body = m.groups()
                if kind == 'Art':
                    continue
                ai = [l for l in body.splitlines() if '只给 AI' in l]
                hit = next((LINK.search(l) for l in ai if LINK.search(l)), None)
                if not hit:
                    continue
                tn = next(g for g in hit.groups() if g)
                if tn not in by_true:
                    print('  卡里找不到', tn, '←', name, os.path.basename(p))
                    continue
                for who, k in by_true[tn]:
                    key = (who, name, tn)
                    if key in seen:
                        continue
                    seen.add(key)
                    stars.append({'who': who, 'n': name, 'k': kind, 'tn': tn, 'tx': gist(legs[who][k][2])})
    arts = []
    for who, d in legs.items():
        if 'Art' in d:
            name, tier, desc, rest = d['Art']
            src = re.search(r'传承：([^｜]*)', rest)
            arts.append({'who': who, 'tn': name, 'src': src.group(1) if src else ''})
    json.dump({'stars': stars, 'arts': arts}, open(OUT, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('写了', os.path.relpath(OUT, ROOT), '：俗称', len(stars), '颗，卡里的技艺', len(arts), '门')


def people(o, parent=None):
    """数据里带 stars 的人：(人名, 那一份)。"""
    if isinstance(o, dict):
        if isinstance(o.get('stars'), list) and parent:
            yield parent, o
        for k, v in o.items():
            yield from people(v, k if isinstance(v, dict) else parent)
    elif isinstance(o, list):
        for v in o:
            yield from people(v, parent)


def apply():
    M = json.load(open(OUT, encoding='utf-8'))
    hit, art_hit, files = 0, 0, 0
    for b in BOOKS:
        fs = glob.glob(os.path.join(FRONT, b, 'data', 'prof', '*.json')) + [os.path.join(FRONT, b, 'data', 'cards.json')]
        for f in fs:
            if not os.path.exists(f):
                continue
            D = json.load(open(f, encoding='utf-8'))
            n0 = hit + art_hit
            for name, p in people(D):
                matched, first = set(), {}
                for s in p['stars']:
                    for k in ('tn', 'tx', 'gr', 'lin', 'al', 'dup'):
                        s.pop(k, None)
                    for m in M['stars']:
                        if m['n'] == s.get('name') and short(m['who']) in name:
                            s['tn'], s['tx'] = m['tn'], m['tx']
                            matched.add(m['who'])
                            hit += 1
                            if m['tn'] in first:          # 两颗俗称是同一颗星露出来的两头：剧透开了并成一颗
                                s['dup'] = True
                                f0 = first[m['tn']]
                                al = f0.setdefault('al', [f0['name']] if f0['name'] != m['tn'] else [])
                                if s['name'] != m['tn']:
                                    al.append(s['name'])
                            else:
                                first[m['tn']] = s
                            break
                for a in M['arts']:
                    if a['who'] not in matched:
                        continue
                    names = [s['name'] for s in p['stars']]
                    if a['tn'] in names:
                        continue
                    art = [s for s in p['stars'] if s.get('kind') == 'Art']
                    if not art:
                        continue
                    lin = [s for s in art if s['name'] in a['src']]
                    tgt = lin[-1] if lin else art[-1]
                    tgt['gr'], tgt['lin'] = a['tn'], bool(lin)
                    art_hit += 1
            if hit + art_hit != n0:
                json.dump(D, open(f, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, separators=(',', ':'))
                files += 1
    print('套上了：俗称', hit, '处，技艺', art_hit, '处，改了', files, '个文件')


if __name__ == '__main__':
    {'make': make, 'apply': apply}[sys.argv[1] if len(sys.argv) > 1 else 'make']()
