#!/usr/bin/env python3
# 介绍页收尾（11-15）：把卡片、世界之书、界面图备进这一本书。带 PIL 的 Python 跑：python prep_codex.py [cards] [wb] [ui]，不写就全做。
#   cards：底稿/门面/卡片/月银纪/mNN.json 并成 data/cards.json（{mNN: {...}}），一个时代一份，子任务写、主会话审过的。
#   wb：底稿/门面/卡片/世界之书.json 拷成 data/wb.json（压成一行）。
#   ui：底稿/状态栏/comfy/out/门面_世界之书/ 的 emblem_moon、wb_cover 裁到不透明的那一块，存 assets/ui/*.webp。
# 卡片和世界之书的字照 底稿/门面/卡片/写法.md，查稿用 底稿/门面/卡片/check_cards.py。
import glob
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
CARDS = os.path.join(ROOT, '底稿', '门面', '卡片')
UI_SRC = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'out', '门面_世界之书')
UI = {'emblem_moon': 192, 'wb_cover': 240}       # 这一本用到的两张，长边多少像素（页面上画 60、88 像素，留三倍给高分屏）


def cards():
    out = {}
    for f in sorted(glob.glob(os.path.join(CARDS, '月银纪', 'm[0-9][0-9].json'))):
        k = os.path.basename(f)[:-5]
        out[k] = json.load(open(f, encoding='utf-8'))
    json.dump(out, open(os.path.join(HERE, 'data', 'cards.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    n_line = sum(len(v.get('lines', {})) for v in out.values())
    n_ppl = sum(len(v.get('people', {})) for v in out.values())
    print('cards.json', len(out), '个时代', n_line, '条主线', n_ppl, '个人')


def wb():
    src = os.path.join(CARDS, '世界之书.json')
    if not os.path.exists(src):
        print('没有', src)
        return
    D = json.load(open(src, encoding='utf-8'))
    json.dump(D, open(os.path.join(HERE, 'data', 'wb.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('wb.json', [(v['id'], len(v['pages'])) for v in D.get('volumes', [])])


def ui():
    from PIL import Image
    os.makedirs(os.path.join(HERE, 'assets', 'ui'), exist_ok=True)
    for k, side in UI.items():
        im = Image.open(os.path.join(UI_SRC, k + '.png')).convert('RGBA')
        a = im.split()[3].point(lambda v: 255 if v > 8 else 0)
        im = im.crop(a.getbbox())
        im.thumbnail((side, side), Image.LANCZOS)
        im.save(os.path.join(HERE, 'assets', 'ui', k + '.webp'), quality=88, method=6)
        print('ui', k, im.size)


if __name__ == '__main__':
    todo = sys.argv[1:] or ['cards', 'wb', 'ui']
    os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)
    for t in todo:
        {'cards': cards, 'wb': wb, 'ui': ui}[t]()
