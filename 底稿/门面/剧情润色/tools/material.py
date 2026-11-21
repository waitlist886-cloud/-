#!/usr/bin/env python3
# 门面剧情润色（11-21）：给写手抽材料，一份一组时代。
#   python -I -X utf8 底稿/门面/剧情润色/tools/material.py <输出目录>
# 每份一个 .md：这一组时代里每条主线门面上现在的样子（标题、钩子、睁眼、幕行、没有你的那一版）加页上主线正文全文。
# 分份照 PORTIONS；写手交 底稿/门面/剧情润色/<纪>/<时代 id>.json。
import glob
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
FRONT = os.path.join(ROOT, '底稿', '门面')
BOOK = {'月银纪': ('小样_月银纪书', 'moon.json'), '纷争纪': ('小样_纷争纪书', 'strife.json'),
        '山铜纪': ('小样_山铜纪书', 'bronze.json'), '迷宫纪': ('小样_迷宫纪书', 'maze.json')}
SRC = {'月银纪': ['月银纪史诗/第*歌_*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md'],
       '纷争纪': ['纷争纪/纷争纪时段_*.md'], '山铜纪': ['山铜纪/山铜纪时段_*.md'], '迷宫纪': ['迷宫纪前传/迷宫纪前传时段_*.md']}
PORTIONS = [
    ('月银纪', ['m%02d' % i for i in range(1, 16)]), ('月银纪', ['m16', 'm17', 'm18']), ('月银纪', ['m%02d' % i for i in range(19, 28)]),
    ('纷争纪', ['s%02d' % i for i in range(1, 10)]), ('纷争纪', ['s%02d' % i for i in range(10, 16)]), ('纷争纪', ['s%02d' % i for i in range(16, 22)]),
    ('山铜纪', ['p1', 'p2']), ('山铜纪', ['p3']), ('山铜纪', ['p4']), ('山铜纪', ['p5']), ('山铜纪', ['p6']),
    ('迷宫纪', ['q1', 'q2']), ('迷宫纪', ['q3']), ('迷宫纪', ['q4']), ('迷宫纪', ['q5']), ('迷宫纪', ['q6']),
]


def mainline_texts(ji):
    """页上 ## …主线｜X 那一块，到下一个带｜或：的 ## 标题为止（## 裁定锁 算在主线里）。"""
    out = {}
    for pat in SRC[ji]:
        for fp in sorted(glob.glob(os.path.join(ROOT, pat))):
            lines = open(fp, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
            i = 0
            while i < len(lines):
                ln = lines[i]
                if ln.startswith('## ') and '主线｜' in ln:
                    name = re.sub(r'（[^）]*稿）', '', ln.split('主线｜', 1)[1]).strip()
                    j = i + 1
                    while j < len(lines) and not (lines[j].startswith('## ') and re.search(r'[｜：]', lines[j])):
                        j += 1
                    out.setdefault(name, (os.path.relpath(fp, ROOT).replace('\\', '/'), '\n'.join(lines[i:j]).strip()))
                    i = j
                else:
                    i += 1
    return out


def main():
    od = sys.argv[1]
    os.makedirs(od, exist_ok=True)
    data = {}
    for ji, (d, f) in BOOK.items():
        D = json.load(open(os.path.join(FRONT, d, 'data', f), encoding='utf-8'))
        C = json.load(open(os.path.join(FRONT, d, 'data', 'cards.json'), encoding='utf-8'))
        data[ji] = (D, C, mainline_texts(ji))
    idx = []
    for n, (ji, ids) in enumerate(PORTIONS, 1):
        D, C, MT = data[ji]
        buf = ['# 材料 %02d｜%s %s' % (n, ji, ' '.join(ids)), '']
        nl = 0
        for e in D['eras']:
            if e['id'] not in ids:
                continue
            buf += ['## 时代 %s｜%s %s' % (e['id'], e.get('label') or '', e.get('title') or ''), '']
            if e.get('pian'):
                buf += ['篇｜%s。篇描述｜%s' % (e['pian'], e.get('pianDesc', '')), '']
            if e.get('chapName'):
                buf += ['章｜%s《%s》。章描述｜%s' % (e.get('chap', ''), e['chapName'], e.get('chapDesc', '')), '']
            for l in e.get('lines', []):
                nl += 1
                lc = C.get(e['id'], {}).get('lines', {}).get(l['name'], {})
                buf += ['### 主线｜%s' % l['name'], '']
                if l.get('pian'):
                    buf.append('- 门面标题（不动）：%s｜%s' % (l['pian'], l.get('ti', '')))
                if l.get('task'):
                    buf.append('- 门面标题：【%s】%s（任务名可提议改，见派活说明）' % (l['task'], l['name']))
                    if l.get('chapName') and l['chapName'] != e.get('chapName'):
                        buf.append('- 这一条的章：%s《%s》%s' % (l.get('chap', ''), l['chapName'], l.get('chapDesc', '')))
                buf.append('- 钩子引语：%s' % ((lc.get('hook') if lc else None) or '　'.join(l.get('hooks', []))))
                buf.append('- 睁眼的地方：%s' % ((lc.get('open') if lc else None) or l.get('open', '')))
                buf.append('- 现在的幕行（按这个次序，一行交一个）：')
                for a in l.get('acts', []):
                    buf.append('  - %s' % a)
                if l.get('ending'):
                    buf.append('- 没有你的那一版（剧透，只给你看）：%s' % l['ending'])
                src = MT.get(l['name'])
                buf += ['', '#### 页上主线全文（%s）' % (src[0] if src else '没找到'), '']
                buf += [src[1] if src else '（没找到，照上面写）', '']
        fn = '%02d_%s_%s.md' % (n, ji, ids[0] + ('-' + ids[-1] if len(ids) > 1 else ''))
        open(os.path.join(od, fn), 'w', encoding='utf-8', newline='\n').write('\n'.join(buf))
        idx.append((fn, nl, sum(len(x) for x in buf)))
    for fn, nl, sz in idx:
        print(fn, nl, '条', sz, '字')


if __name__ == '__main__':
    main()
