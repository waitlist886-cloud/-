#!/usr/bin/env python3
# 共用那一份（世界之书、地图）拷进各本书和牌桌的目录（11-15 拼装那一轮）。带 PIL 的 Python 跑：python sync.py
#   1. 底稿/门面/卡片/世界之书.json 并上 世界之书_纷争纪/山铜纪/迷宫纪.json（子任务一卷一份写的，审过才并）→ 共用/data/wb.json
#   2. 界面图：合着的书和四纪的入口（底稿/状态栏/comfy/out/门面_世界之书/）裁到不透明的那一块 → 共用/assets/ui/*.webp
#   3. 共用/ 里的 codex.js、codex.css、data/、assets/ 拷到 小样_*书/共用/ 和 小样_牌桌/共用/（单独打开一本书的时候用这一份；这几份是拷出来的，不进库）
# 地图的数据和底图另跑 prep_maps.py。
import io
import json
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
CARDS = os.path.join(FRONT, '卡片')
UI_SRC = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'out', '门面_世界之书')
UI = {'wb_cover': 240, 'emblem_moon': 192, 'emblem_strife': 192, 'emblem_bronze': 192, 'emblem_maze': 192}
DEST = ['小样_月银纪书', '小样_纷争纪书', '小样_山铜纪书', '小样_迷宫纪书', '小样_牌桌', '小样_外壳']
ORDER = ['general', 'moon', 'strife', 'bronze', 'maze']


def wb():
    D = json.load(open(os.path.join(CARDS, '世界之书.json'), encoding='utf-8'))
    vols = {v['id']: v for v in D['volumes']}
    for name in ('纷争纪', '山铜纪', '迷宫纪'):
        f = os.path.join(CARDS, '世界之书_%s.json' % name)
        if os.path.exists(f):
            v = json.load(open(f, encoding='utf-8'))
            vols[v['id']] = v
    out = {'volumes': [vols[k] for k in ORDER if k in vols]}
    os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, 'data', 'wb.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('wb.json', [(v['id'], len(v['pages'])) for v in out['volumes']])


def ui():
    from PIL import Image
    os.makedirs(os.path.join(HERE, 'assets', 'ui'), exist_ok=True)
    for k, side in UI.items():
        src = os.path.join(UI_SRC, k + '.png')
        dst = os.path.join(HERE, 'assets', 'ui', k + '.webp')
        if not os.path.exists(src):
            print('没有', src)
            continue
        if os.path.exists(dst) and os.path.getmtime(dst) > os.path.getmtime(src):
            continue
        im = Image.open(src).convert('RGBA')
        a = im.split()[3].point(lambda v: 255 if v > 8 else 0)
        im = im.crop(a.getbbox())
        im.thumbnail((side, side), Image.LANCZOS)
        im.save(dst, quality=88, method=6)
        print('ui', k, im.size)


def copy():
    for d in DEST:
        base = os.path.join(FRONT, d)
        if not os.path.isdir(base):
            continue
        dst = os.path.join(base, 'common')      # 页面上用 common/ 这个名字（图床和 CDN 上不放中文路径）
        n = 0
        for sub, _, files in os.walk(HERE):
            rel = os.path.relpath(sub, HERE)
            if rel.startswith('__pycache__'):
                continue
            if rel == '.':
                files = [f for f in files if f in ('codex.js', 'codex.css')]      # 顶上只拷页面要载的这两个；脚本、说明、推图床的清单（front*.json）都不拷
            elif rel.split(os.sep)[0] not in ('data', 'assets'):
                continue
            for f in files:
                s = os.path.join(sub, f)
                t = os.path.join(dst, rel, f) if rel != '.' else os.path.join(dst, f)
                os.makedirs(os.path.dirname(t), exist_ok=True)
                if not os.path.exists(t) or os.path.getmtime(t) < os.path.getmtime(s) or os.path.getsize(t) != os.path.getsize(s):
                    shutil.copy2(s, t)
                    n += 1
        print(d, '拷了', n, '个')


if __name__ == '__main__':
    todo = sys.argv[1:] or ['wb', 'ui', 'copy']
    for t in todo:
        {'wb': wb, 'ui': ui, 'copy': copy}[t]()
