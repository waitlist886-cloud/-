#!/usr/bin/env python3
# 有名有品阶的器物（遗物、神器、名器）的完整原画（11-21 背包图标那一轮）。一件一张，透明底，整件露全；背包图标就从这张缩出来。
#   CODEX_HOME=C:/Users/waitl/.codex_b <ComfyUI 的 python> 底稿/图标/tools/gpt_relic.py [键…]
# 资料在 底稿/图标/relics/*.json（一件一条：key、name、tier、look 英文外观），写 out/图标_原画/<key>.png，已有的不重出。
# 11-21 样张：直接要透明底，模型会画出假棋盘格或者在底上拖一片雾，改成纯品红平底，出完 key_relic.py 抠成透明。
import glob
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', 'comfy'))
sys.stdout.reconfigure(encoding='utf-8')
import gpt_gen  # noqa: E402

OUT = os.path.join(ROOT, 'out', '图标_原画')
STYLE = ('A single treasured item shown alone, like the weapon and artifact showcase art in a high-end Japanese fantasy action RPG: '
         'soft painterly cel shading with fine hand-painted detail, crisp clean silhouette, warm highlights, believable materials (worn metal, polished bone, aged wood, cloth), '
         'three-quarter view on a gentle diagonal, the whole object fully inside the picture with empty margin all around, consistent light from the upper left. ')
TIER = {'Epic': 'It is a storied heroic piece: well made and lovingly worn, with one quiet touch of magic. ',
        'Legend': 'It is a legendary artifact: its own inner light or magic is clearly visible on the object itself, still restrained and elegant. ',
        'Unique': 'It is a one-of-a-kind divine relic: something about it is plainly not of this world, yet it stays small and quiet, never flashy. '}
TAIL = ('Square picture, aspect ratio 1:1. The background is one flat, solid, pure magenta colour (#FF00FF) filling the whole picture edge to edge: no gradient, no checkerboard, no texture, no vignette. '
        'The object itself contains no magenta or pink. No text, no letters, no frame, no border, no pedestal, no hands, no person, no ground shadow, no background scenery, no glow or haze spilling onto the background.')


def load():
    items = {}
    for f in sorted(glob.glob(os.path.join(ROOT, '底稿', '图标', 'relics', '*.json'))):
        for e in json.load(open(f, encoding='utf-8')):
            items[e['key']] = e
    return items


def job(e):
    return gpt_gen.gen(os.path.join(OUT, e['key']), STYLE + TIER.get(e['tier'], '') + 'The object: ' + e['look'] + ' ' + TAIL)


if __name__ == '__main__':
    items = load()
    keys = sys.argv[1:] or list(items)
    with ThreadPoolExecutor(3) as ex:
        for k, r in zip(keys, ex.map(lambda k: job(items[k]), keys)):
            print(k, r, flush=True)
