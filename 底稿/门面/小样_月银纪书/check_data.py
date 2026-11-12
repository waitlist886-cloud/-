#!/usr/bin/env python3
# 时代页的数据抽出来以后查一遍：给作者和模型看的话、不该点的名、只给 AI 的那一层，有没有漏到玩家看得见的字里。
#   python -I -X utf8 check_data.py          报可疑的句子（哪个时代、哪一栏、哪一句）
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'data', 'moon.json'), encoding='utf-8'))
# 给作者和模型看的话
META = re.compile(r'玩家|AI|★|裁定|底座|底卡|照原条|潮汐格|凭证|真相层|只给|不点破|不裁定|条目|这一页|设计备注|主持')
# 不该点的名：那一位恶神、四位执政
NAMES = re.compile(r'厄洛伽|若娜瓦|伊斯塔露|纳贝里士|阿斯莫代|法涅斯')
# 神在凡人中间走的那一层（约 3000 年以前没有人知道），和魔族、深渊那一层：出现了就列出来人看一眼
GODS = re.compile(r'祂|神名|其实是|真身|真名|化身|深渊|染渊|黄金裔|金血')
MARK = re.compile(r'[—…！；]|\.\.\.')


def walk(e):
    yield '史诗', ' '.join(e['epic']['text']) if e['epic'] else ''
    for l in e['lines']:
        yield l['name'] + '·钩子', ' '.join(l['hooks'])
        yield l['name'] + '·睁眼', l['open']
        yield l['name'] + '·幕', ' '.join(l['acts'])
        yield l['name'] + '·没有你', l['ending']
    for c in e['cast']:
        yield c['name'] + '·身份', c['who']
    for b in e['beasts']:
        yield b['name'] + '·兽', b['where'] + ' ' + b['size']
    for p in e['places']:
        yield p['name'] + '·地', p['where'] + ' ' + p['later']


n = {'meta': 0, 'names': 0, 'gods': 0}
for e in d['eras']:
    for where, text in walk(e):
        for s in re.split(r'(?<=[。？])', text):
            if META.search(s):
                n['meta'] += 1
                print('【作者的话】', e['id'], where, '｜', s.strip()[:120])
            if NAMES.search(s):
                n['names'] += 1
                print('【不该点的名】', e['id'], where, '｜', s.strip()[:120])
            if GODS.search(s) and '史诗' not in where and '钩子' not in where:
                n['gods'] += 1
                print('〔看一眼〕', e['id'], where, '｜', s.strip()[:150])
print(n)

# 档案页的数据（data/prof/时代.json）：同样三样，另数一数还剩多少个祂。是谁不点破的那几位（veil）里出现神名的单列。
import glob
np_ = {'meta': 0, 'names': 0, 'gods': 0, 'veil_god': 0}
GODNAME = re.compile(r'库米罗妮|欧巴德斯|璐璐薇|伊兹帕鲁特|朱亚|艾赫卡托尔|耶万|卡尔德隆|格蕾诺|女神|男神|之神')
show = '--prof' in sys.argv
for f in sorted(glob.glob(os.path.join(HERE, 'data', 'prof', '*.json'))):
    eid = os.path.basename(f)[:-5]
    for name, p in json.load(open(f, encoding='utf-8')).items():
        texts = [(s['h'], s['t']) for s in p.get('sec', [])] + [('下场', p.get('fate', '')), ('来路', p.get('past', '')), ('最怕', p.get('fear', '')), ('性格', p.get('trait', ''))]
        texts += [('平日', ' '.join(p.get('life', [])))] + [('星', s.get('text', '')) for s in p.get('stars', [])]
        for where, text in texts:
            for s in re.split(r'(?<=[。？])', text or ''):
                if META.search(s):
                    np_['meta'] += 1
                    print('【作者的话】', eid, name, where, '｜', s.strip()[:120])
                if NAMES.search(s):
                    np_['names'] += 1
                    print('【不该点的名】', eid, name, where, '｜', s.strip()[:120])
                if p.get('veil') and (GODNAME.search(s) or '祂' in s):
                    np_['veil_god'] += 1
                    print('〔不点破的人〕', eid, name, where, '｜', s.strip()[:150])
                elif GODS.search(s):
                    np_['gods'] += 1
                    if show:
                        print('〔看一眼〕', eid, name, where, '｜', s.strip()[:150])
print('档案', np_, '（〔看一眼〕那一类要逐句看的话加 --prof）')
