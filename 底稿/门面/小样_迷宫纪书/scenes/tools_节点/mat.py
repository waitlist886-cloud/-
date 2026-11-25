#!/usr/bin/env python3
# 给写场面稿抽材料：python -I -X utf8 mat.py q3_e [一幕 二幕 收束]
# 打出：这一条主线那几幕的源稿原文（带行号）、头一轮那一幅已经写了的场面、这几幕里提到的有立绘的人（键、岁数、长相头几句）。
import glob
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = 'E:/aldran_art'
BOOK = ROOT + '/底稿/门面/小样_迷宫纪书'
COMFY = ROOT + '/底稿/状态栏/comfy'
PAGES = {'q1': '一_探井的年月', 'q2': '二_共约的年月', 'q3': '三_繁荣的年月', 'q4': '四_深井的年月', 'q5': '五_黑潮的年月', 'q6': '六_垂暮的年月'}
SETS = ['立绘_前传', '立绘_v3', '立绘_山铜纪', '立绘_纷争纪', '立绘_月银纪史诗', '立绘_诸国期', '立绘_萨尔维斯']


def por(key):
    for s in SETS:
        p = os.path.join(COMFY, 'out', s, key)
        if os.path.isdir(p):
            return p
    return None


def main():
    lk = sys.argv[1]
    want = sys.argv[2:] or ['一幕', '二幕', '收束']
    wlen = int(os.environ.get('WHO', '330'))
    data = json.load(open(BOOK + '/data/maze.json', encoding='utf-8'))
    era = [e for e in data['eras'] if e['id'] == lk[:2]][0]
    line = [l for l in era['lines'] if l['mural'] == lk][0]
    print('#', lk, line['name'], '｜', line['year'], '年｜', ' / '.join(line['acts']))
    src = open(ROOT + '/迷宫纪前传/迷宫纪前传时段_%s.md' % PAGES[lk[:2]], encoding='utf-8').read().split('\n')
    start = [i for i, x in enumerate(src) if x.strip() == '## 迷宫纪·主线｜' + line['name']][0]
    end = next(i for i in range(start + 1, len(src)) if src[i].startswith('## '))
    body = src[start:end]
    text = ''
    cur = None
    for off, ln in enumerate(body):
        m = re.match(r'^(一幕|二幕|三幕|四幕|收束|默认收束|玩家能改|碰得上的人|开局|世道)[｜：]', ln)
        if m:
            cur = m.group(1)
        elif ln.startswith('## ') or ln.startswith('> 条目设置') or ln.startswith('【') or ln.startswith('### '):
            if off:
                cur = None
        if cur in want and ln.strip():
            print('%d %s' % (start + off + 1, ln))
            text += ln + '\n'
    # 头一轮那一幅
    n = json.load(open(BOOK + '/scenes/n%s.json' % lk[1], encoding='utf-8'))
    for s in n['nodes']:
        if s['key'].startswith(lk) :
            print('\n== 已写', s['key'], s['act'], s['name'], 'style', s['style'], ('beast ' + s['beast']) if s.get('beast') else '', 'noface' if s.get('noface') else '', 'young' if s.get('young') else '', 'raw' if s.get('raw') else '')
            print('who/row', json.dumps(s.get('who') or s.get('row'), ensure_ascii=False))
            if os.environ.get('FULL'):
                print('light', s['light'])
                print('text', s['text'])
    # 人
    cast = {}
    for f in glob.glob(COMFY + '/cast/**/*.json', recursive=True):
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        for x in (d if isinstance(d, list) else []):
            if isinstance(x, dict) and x.get('en'):
                cast.setdefault(x['en'], x)
    print('\n== 这几幕里提到的人（这一页名单上有键的）')
    seen = set()
    for c in era.get('cast', []) + era.get('meet', []) + era.get('legends', []):
        nm = c.get('name', '')
        first = re.split(r'[·（(，]', nm)[0]
        if not first or first in seen or first not in text:
            continue
        seen.add(first)
        k = c.get('key')
        if not k:
            print('-', nm, '｜没有立绘键｜', (c.get('who') or '')[:60])
            continue
        p = por(k)
        cells = [x for x in ('casual', 'private', 'battle', 'formal') if p and os.path.exists(os.path.join(p, 'cell_%s.png' % x))]
        x = cast.get(k, {})
        print('-', nm, '｜', k, '｜', c.get('race', ''), '｜这一页', c.get('age'), '岁｜', '/'.join(cells) if p else '没有图', '' if (p and os.path.exists(os.path.join(p, 'art.png'))) else '（缺艺术照）')
        w = x.get('who') or ''
        bits = [b.strip() for b in re.split(r'(?<=[.:;])\s+', w) if re.search(r'hair|horn|ears?|scale|eyes|wing|tail|beard|arm', b)]
        print('   ', ' '.join(bits)[:wlen])


main()
