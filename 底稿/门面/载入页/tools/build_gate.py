#!/usr/bin/env python3
# 载入页接进外壳（11-26）：把 载入页/src/ 的第一拍（gate0.css、gate0.html）、后几拍（gate.css、gate.js）、传说（lore.json）、
# 图的单子（gate_img.json）和第零层的单子拼成一段，写进 小样_外壳/index.html 最前头那两行标记之间（没有标记就插在字体那一行后头）。
#   python -I -X utf8 底稿/门面/载入页/tools/build_gate.py           写外壳
#   python -I -X utf8 底稿/门面/载入页/tools/build_gate.py --check   只看会写多少字
# 薄壳那一截（第一拍）由 共用/make_thin.py 调这里的 gate0() 拿同一份，两边一个字不差。往后改载入页改 src/，再跑这一支和 make_thin。
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.normpath(os.path.join(HERE, '..'))
SRC = os.path.join(GATE, 'src')
SHELL = os.path.normpath(os.path.join(GATE, '..', '小样_外壳'))
START, END = '<!--gate:start', '<!--gate:end-->'
# 第零层：门口必须有的（外壳的脚本、样式，牌桌的图，四纪的牌背和牌面、第五张牌）。脚本和样式在 index.html 里 onload 报到，图载入页自己取
L0_CODE = ['common/codex.css', 'common/library.css', 'shell.css', 'common/codex.js', 'common/library.js', 'shell.js']
L0_IMG = ['assets/table.webp', 'assets/hand9_open.webp', 'assets/hand9_take.webp'] + ['assets/%s_%d.webp' % (k, i) for i in range(4) for k in ('era', 'back', 'bb')] + ['assets/now_card.webp']


# 第一层：五本书的页面和开书那几份数据（跟 shell.js 的 BOOT 一样），按大小加权进度
BOOT = {'moon': ('小样_月银纪书', ['moon', 'cards', 'cg', 'have', 'pa', 'tiles', 'atlas']),
        'strife': ('小样_纷争纪书', ['strife', 'card', 'cards', 'cg', 'have', 'pa', 'road', 'roadc', 'atlas']),
        'bronze': ('小样_山铜纪书', ['bronze', 'road', 'cards', 'cg', 'have', 'pa', 'props', 'sky', 'stele', 'tex', 'walk', 'atlas']),
        'maze': ('小样_迷宫纪书', ['maze', 'cards', 'have', 'mural', 'pa', 'atlas']),
        'now': ('小样_此刻书', ['now', 'atlas'])}
# 第二层（第二版添的）：门后头一眼、外壳这一页自己会用到的。书是沙箱里另一格，跟外壳不共用浏览器缓存，书里的图在这里载了也省不下，不放
L2_JSON = ['data/build.json', 'data/stars.json', 'data/gold.json', 'data/gifts.json', 'data/life.json', 'data/land.json', 'data/bx_art.json',
           'common/data/lib/index.json', 'common/data/plates_cdn.json', 'common/data/wb.json',
           'common/data/map_moon.json', 'common/data/map_strife.json', 'common/data/map_bronze.json', 'common/data/map_maze.json']
L2_IMG_GLOB = ['assets/ronova.webp', 'common/assets/ui/*.webp', 'common/assets/lib/hall_*.webp', 'common/assets/lib/card.webp', 'common/assets/lib/plate.webp',
               'common/assets/lib/seal.webp', 'common/assets/lib/spine_yuan_*.webp', 'common/assets/wb/general_*.webp', 'assets/bx/*.webp']
CARDS = [('m1', 0), ('m2', None), ('m3', None), ('s1', 1), ('s2', None), ('b1', 2), ('b2', None), ('p1', 3), ('p2', None), ('n1', 4), ('n2', None), ('n3', None)]


def bookw():
    out = {}
    for k, (d, fs) in BOOT.items():
        base = os.path.join(SHELL, '..', d)
        n = os.path.getsize(os.path.join(base, 'index.html')) + sum(os.path.getsize(os.path.join(base, 'data', f + '.json')) for f in fs if os.path.exists(os.path.join(base, 'data', f + '.json')))
        out[k] = max(1, round(n / 1024))
    return out


def l2():
    import glob
    out = [{'k': k, 'w': max(1, round(os.path.getsize(os.path.join(SHELL, k)) / 1024)), 'j': 1} for k in L2_JSON if os.path.exists(os.path.join(SHELL, k))]
    for g in L2_IMG_GLOB:
        for p in sorted(glob.glob(os.path.join(SHELL, g))):
            out.append({'k': os.path.relpath(p, SHELL).replace(os.sep, '/'), 'w': max(1, round(os.path.getsize(p) / 1024))})
    return out


def rd(name):
    return open(os.path.join(SRC, name), encoding='utf-8').read()


def mincss(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    s = re.sub(r'\s*\n\s*', '', s)
    s = re.sub(r'\s*([{};,])\s*', r'\1', s)
    return s.replace(';}', '}').strip()


def gate0():
    """第一拍：（压过的样式，标记）。薄壳和外壳都用这一份。"""
    return mincss(rd('gate0.css')), rd('gate0.html').strip()


def items():
    out = []
    for k in L0_CODE + L0_IMG:
        p = os.path.join(SHELL, k)
        w = max(1, round(os.path.getsize(p) / 1024)) if os.path.exists(p) else 20
        o = {'k': k, 'w': w}
        if k in L0_IMG:
            o['img'] = 1
        out.append(o)
    return out


def block():
    css0, html0 = gate0()
    js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    meta = json.load(open(os.path.join(SRC, 'gate_img.json'), encoding='utf-8'))
    im = {k: 'assets/gate/%s.webp' % k for k in ('sky', 'road', 'door_f', 'door_l', 'door_r')}
    im.update({k: meta[k] for k in ('doorAspect', 'hingeL', 'hingeR')})
    im['dir'] = 'assets/gate/sh/'
    seen = set()
    im['cards'] = []
    for k, era in CARDS:
        c = {'k': k}
        if era is not None:
            c['era'] = era
            if era not in seen:
                c['first'] = 1
                seen.add(era)
        im['cards'].append(c)
    lore = json.load(open(os.path.join(SRC, 'lore.json'), encoding='utf-8'))['lines']
    g = rd('gate.js').replace('__LORE__', js(lore)).replace('__ITEMS__', js(items())).replace('__IMG__', js(im)).replace('__BOOKW__', js(bookw())).replace('__L2__', js(l2()))
    assert all(x not in g for x in ('__LORE__', '__ITEMS__', '__IMG__', '__BOOKW__', '__L2__'))
    tot = sum(i['w'] for i in items()) + sum(bookw().values()) + sum(i['w'] for i in l2())
    print('预载：第零层 %.1f MB，第一层 %.1f MB，第二层 %.1f MB（%d 个），合计 %.1f MB（载入页自己的图另算）' % (
        sum(i['w'] for i in items()) / 1024, sum(bookw().values()) / 1024, sum(i['w'] for i in l2()) / 1024, len(l2()), tot / 1024))
    assert '</script' not in g.lower()
    return (START + ' 载入页：底稿/门面/载入页/ 的 tools/build_gate.py 写进来的，别在这里改-->\n'
            + '<style id="gate0">' + css0 + '</style>\n<style id="gate1">' + mincss(rd('gate.css')) + '</style>\n'
            + html0 + '\n<script>' + g + '</script>\n' + END)


def main():
    b = block()
    p = os.path.join(SHELL, 'index.html')
    s = open(p, encoding='utf-8').read()
    if START in s:
        i, j = s.index(START), s.index(END) + len(END)
        s2 = s[:i] + b + s[j:]
    else:
        anchor = "onload=\"this.media='all'\">\n"
        assert s.count(anchor) == 1, '找不到字体那一行'
        s2 = s.replace(anchor, anchor + b + '\n', 1)
    print('载入页那一段 %d 字（%.1f KB）' % (len(b), len(b.encode('utf-8')) / 1024))
    if '--check' in sys.argv:
        return
    open(p, 'w', encoding='utf-8', newline='\n').write(s2)
    print('写了', p)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
