#!/usr/bin/env python3
# 身穿降临者的落点句（小样_外壳/data/land.json）对四本书的主线清单查一遍（11-25）。
#   python -I -X utf8 底稿/门面/第二轮/建档/tools/land_check.py [--list]
# 查：四本书每一条主线都有一句、没有多出来的键（书里主线改了名就会报）；句子以 落在 起头、句号收尾、八十个字以内；
#     不带卡面不用的标点、月相字和几样口径词。--list 把句子照书里的次序印出来（书｜年份｜主线｜句子）。
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
BOOKS = [('moon', '月银纪', '小样_月银纪书'), ('strife', '纷争纪', '小样_纷争纪书'), ('bronze', '山铜纪', '小样_山铜纪书'), ('maze', '迷宫纪', '小样_迷宫纪书')]
BAD_PUNCT = '——…！；—–「」『』:;!?,()'
BAD_WORD = ['新月', '满月', '残月', '月牙', '弦月', '月亮', '月光', '客栈', '掌柜', '朝廷', '时辰', '登记', '一丝', '一抹', '不禁', '威压', '修为', '系统', '坐标', '爹', '娘亲', '银子', '铜钱']

L = json.load(open(os.path.join(FRONT, '小样_外壳', 'data', 'land.json'), encoding='utf-8'))
bad = 0
rows = []
for b, era, folder in BOOKS:
    D = json.load(open(os.path.join(FRONT, folder, 'data', b + '.json'), encoding='utf-8'))
    eras = D['eras'] if isinstance(D, dict) and 'eras' in D else D
    names = [(l['name'], l.get('year')) for pg in eras for l in pg.get('lines', [])]
    T = (L.get('eras') or {}).get(b) or {}
    lack = [n for n, _ in names if n not in T]
    extra = [k for k in T if k not in {n for n, _ in names}]
    if lack:
        bad += len(lack)
        print(era, '少了', len(lack), '条：', '、'.join(lack))
    if extra:
        bad += len(extra)
        print(era, '多出来（书里没有这一条主线）', len(extra), '条：', '、'.join(extra))
    for n, y in names:
        s = T.get(n)
        if s is None:
            continue
        why = []
        if not s.startswith('落在'):
            why.append('不是 落在 起头')
        if not s.endswith('。'):
            why.append('不是句号收尾')
        if len(s) > 80:
            why.append('%d 个字，过了八十' % len(s))
        p = [c for c in BAD_PUNCT if c in s]
        if p:
            why.append('标点 ' + ' '.join(p))
        w = [x for x in BAD_WORD if x in s]
        if w:
            why.append('口径词 ' + '、'.join(w))
        if re.search(r'\s', s):
            why.append('带空白')
        if why:
            bad += 1
            print(era, n, '｜', '；'.join(why), '｜', s)
        rows.append((era, y, n, s))
    ls = [len(T[n]) for n, _ in names if n in T]
    print('%s　主线 %d 条，有句子 %d 条，最短 %d 字，最长 %d 字，平均 %.0f 字' % (era, len(names), len(ls), min(ls or [0]), max(ls or [0]), sum(ls) / max(1, len(ls))))
fb = L.get('fallback') or ''
if not fb.startswith('落在') or not fb.endswith('。'):
    bad += 1
    print('fallback 那一句不对：', fb)
print('对不上', bad, '处')
if '--list' in sys.argv:
    for era, y, n, s in rows:
        print('%s｜%s｜%s｜%s' % (era, y, n, s))
sys.exit(1 if bad else 0)
