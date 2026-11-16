#!/usr/bin/env python3
# 四本书里每一条主线的“从这里进”，凭证头一行（开局口令）在卡里叫不叫得醒那一条主线（11-15，照建档资料说明第八节第 1 条的试法）。
#   python -I -X utf8 底稿/门面/共用/wake_open.py <卡.json>
# 把 “纪元：X纪｜开局时段：Y” 加凭证头一句当玩家的一条消息，照各条的触发词和黑名单判（只看范围里有用户的条目，一条消息单独判）。
# 开局时段那一格怎么取照 小样_外壳/data/build.json 的 eras.<书>.start：line 是整条主线名（月银纪），tail 是头一个「·」后头那一截（另外三纪）。
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.normpath(os.path.join(HERE, '..'))
BOOKS = {'moon': ('小样_月银纪书', '月银纪'), 'strife': ('小样_纷争纪书', '纷争纪'), 'bronze': ('小样_山铜纪书', '山铜纪'), 'maze': ('小样_迷宫纪书', '迷宫纪')}


def rx(t):
    m = re.match(r'^/([\s\S]*)/([a-z]*)$', t)
    if not m:
        return None
    fl = 0
    for c in m.group(2):
        fl |= {'i': re.I, 'm': re.M, 's': re.S}.get(c, 0)
    try:
        return re.compile(m.group(1), fl)
    except re.error:
        return None


def hit(words, typ, msg):
    if not words:
        return False
    res = []
    for w in words:
        r = rx(w)
        res.append(bool(r.search(msg)) if r else (w in msg))
    return all(res) if typ == 'AND' else any(res)


def main():
    card = json.load(open(sys.argv[1], encoding='utf-8'))
    lb = [e for e in card['prompt']['lorebook'] if e.get('enabled', True) and 'user' in (e.get('triggerRange') or [])]
    build = json.load(open(os.path.join(FRONT, '小样_外壳', 'data', 'build.json'), encoding='utf-8'))
    head = build['format']['head']
    bad = 0
    for b, (folder, era) in BOOKS.items():
        D = json.load(open(os.path.join(FRONT, folder, 'data', b + '.json'), encoding='utf-8'))
        eras = D['eras'] if isinstance(D, dict) and 'eras' in D else D
        mode = build['eras'][b].get('start', 'tail')
        n = ok = 0
        for e in eras:
            for l in e.get('lines', []):
                name = l['name']
                start = name if mode == 'line' else (name.split('·', 1)[1] if '·' in name else name)
                msg = '纪元：%s｜开局时段：%s\n\n%s\n\n【一·灵魂形态】\n降临之魂 · 身穿（连人带身跌入）' % (era, start, head)
                woke = [x for x in lb if hit(x.get('triggerWords'), x.get('triggerWordsType', 'OR'), msg) and not hit(x.get('blackListWords'), x.get('blackListWordsType', 'OR'), msg)]
                lines = [x for x in woke if re.search(r'主线[｜|]', (x.get('content') or '')[:120])]
                titles = [(x.get('content') or '').split('\n', 1)[0][:40] for x in lines]
                short = name.split('·', 1)[1] if '·' in name else name
                mine = [t for t in titles if short in t]
                n += 1
                if mine and len({t.split('·一幕')[0] for t in titles}) <= 2:
                    ok += 1
                else:
                    bad += 1
                    print('  ✗', era, name, '→ 开局时段：' + start, '｜醒了的主线条目', titles[:4], '｜一共醒', len(woke))
        print(era, '主线', n, '条，叫得醒自己那一条的', ok)
    print('叫不醒或者串了的', bad)


if __name__ == '__main__':
    main()
