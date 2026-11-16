#!/usr/bin/env python3
# 一本书的短卡片并成 data/cards.json（11-15 拼装那一轮）：python -I -X utf8 prep_cards.py [月银纪 纷争纪 山铜纪 迷宫纪]
#   底稿/门面/卡片/<纪>/<时代 id>.json（子任务写、主会话审过的）→ 小样_<纪>书/data/cards.json（{时代 id: {lines, people}}）。
# 月银纪那一本原来走 小样_月银纪书/prep_codex.py cards，出来的东西一样。卡片的写法在 底稿/门面/卡片/写法.md，查稿用 check_cards.py。
import glob
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.normpath(os.path.join(HERE, '..'))
BOOK = {'月银纪': ('小样_月银纪书', 'moon.json'), '纷争纪': ('小样_纷争纪书', 'strife.json'), '山铜纪': ('小样_山铜纪书', 'bronze.json'), '迷宫纪': ('小样_迷宫纪书', 'maze.json')}


def build(ji):
    d, f = BOOK[ji]
    eras = [e['id'] for e in json.load(open(os.path.join(FRONT, d, 'data', f), encoding='utf-8'))['eras']]
    out = {}
    for fp in sorted(glob.glob(os.path.join(FRONT, '卡片', ji, '*.json'))):
        k = os.path.basename(fp)[:-5]
        if k in eras:
            out[k] = json.load(open(fp, encoding='utf-8'))
    json.dump(out, open(os.path.join(FRONT, d, 'data', 'cards.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    n_line = sum(len(v.get('lines', {})) for v in out.values())
    n_ppl = sum(len(v.get('people', {})) for v in out.values())
    print(ji, 'cards.json', '%d/%d 个时代' % (len(out), len(eras)), n_line, '条主线', n_ppl, '个人', '缺 ' + ' '.join(k for k in eras if k not in out) if len(out) < len(eras) else '')


if __name__ == '__main__':
    for ji in (sys.argv[1:] or list(BOOK)):
        build(ji)
