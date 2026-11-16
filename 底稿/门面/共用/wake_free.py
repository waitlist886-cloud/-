#!/usr/bin/env python3
# 自己报年份的三种开局（纷争纪第二十二张、山铜纪无字碑、迷宫纪空白委托）和黄金裔，凭证头一行在卡里叫醒了什么（11-15）。
#   python -I -X utf8 底稿/门面/共用/wake_free.py <卡.json>
# 判法同 wake_open.py：只看范围里有用户的条目，一条消息单独判。每种开局列出叫醒的常驻、时段总纲、入口那一条，和一共醒了多少条、多少字。
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from wake_open import hit  # noqa: E402    （wake_open 一进来就把输出换成 utf-8 的了，这里不再包一层）

CASES = [
    ('纷争纪 第二十二张 3600年', '纪元：纷争纪｜开局时段：第二十二张｜年份：3600'),
    ('纷争纪 第二十二张 元年', '纪元：纷争纪｜开局时段：第二十二张｜年份：元'),
    ('纷争纪 第二十二张 10990年', '纪元：纷争纪｜开局时段：第二十二张｜年份：10990'),
    ('山铜纪 无字碑 700年', '纪元：山铜纪｜开局时段：无字碑｜年份：700'),
    ('山铜纪 无字碑 2年', '纪元：山铜纪｜开局时段：无字碑｜年份：2'),
    ('迷宫纪 空白委托 500年', '纪元：迷宫纪｜开局时段：空白委托｜年份：500'),
    ('迷宫纪 空白委托 990年', '纪元：迷宫纪｜开局时段：空白委托｜年份：990'),
    ('山铜纪 雨城清查 黄金裔', '纪元：山铜纪｜开局时段：雨城清查｜出身：黄金裔'),
    ('月银纪 万兽·焚原 黄金裔', '纪元：月银纪｜开局时段：万兽·焚原｜出身：黄金裔'),
]


def main():
    card = json.load(open(sys.argv[1], encoding='utf-8'))
    lb = [e for e in card['prompt']['lorebook'] if e.get('enabled', True) and 'user' in (e.get('triggerRange') or [])]
    build = json.load(open(os.path.join(HERE, '..', '小样_外壳', 'data', 'build.json'), encoding='utf-8'))
    head = build['format']['head']
    for name, first in CASES:
        msg = first + '\n\n' + head + '\n\n【一·灵魂形态】\n降临之魂 · 身穿（连人带身跌入）'
        woke = [x for x in lb if hit(x.get('triggerWords'), x.get('triggerWordsType', 'OR'), msg) and not hit(x.get('blackListWords'), x.get('blackListWordsType', 'OR'), msg)]
        titles = [((x.get('folder') or '')[:12], (x.get('content') or '').strip().split('\n', 1)[0][:44]) for x in woke]
        era = first.split('｜')[0].replace('纪元：', '')
        other = [t for f, t in titles if re.search(r'月银纪|纷争纪|山铜纪|迷宫纪', f + t) and era not in f + t]
        key = [t for f, t in titles if re.search(r'时段[｜|]|常驻|纪元钟|第二十二张|无字碑|空白委托|建档的种族|首轮入局|主线[｜|]', t)]
        print('==', name, '｜醒', len(woke), '条', sum(len(x.get('content') or '') for x in woke), '字｜别纪的', len(other))
        for t in key[:14]:
            print('     ', t)
        for t in other[:6]:
            print('      ✗ 别纪：', t)


if __name__ == '__main__':
    main()
