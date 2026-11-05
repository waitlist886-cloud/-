#!/usr/bin/env python3
# 核对 cast/cast_*.json：字段齐不齐、en 撞没撞、tier 对不对、有没有不该写的词。用法：python cast_check.py
# 不该写的词：身材和露肤（全员都穿戴整齐）、东方服饰、现代衣服、月相和十字、作品名。
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ['name', 'en', 'minor', 'sex', 'who', 'palette', 'casual', 'private', 'battle', 'formal', 'art']
TIERS = {'woman', 'man', 'burly', 'girl', 'small'}
BAD = {
    '身材露肤': r'\b(cleavage|busty|breasts?|curvy|curvaceous|voluptuous|sexy|seductive|sultry|alluring|sensual|provocative|lingerie|bare (?:chest|back|shoulders?|midriff|thighs?|legs?)|midriff|thigh-high slit|low[- ]cut|plunging|skin-?tight|hourglass|navel)\b',
    '东方': r'\b(kimono|hanfu|qipao|cheongsam|yukata|hakama|obi|mandarin collar|frog buttons?|samurai|ninja|taoist|chinese|japanese)\b',
    '现代': r'\b(hoodie|jeans|denim|t-?shirt|sneakers?|necktie|business suit|blazer)\b',
    '月相十字': r'\b(crescents?|moon|lunar|crosses|crucifix|cross-shaped)\b',
    '作品名': r'\b(honkai|star rail|genshin|final fantasy|frieren|fate)\b',
}
cast, seen, problems = [], {}, 0
for f in sorted(glob.glob(os.path.join(HERE, 'cast', 'cast_*.json'))):
    for c in json.load(open(f, encoding='utf-8')):
        cast.append(c)
        where = os.path.basename(f) + ' ' + c.get('name', '?')
        for k in FIELDS:
            if k not in c or c[k] in ('', None):
                print('缺', where, k)
                problems += 1
        t = c.get('tier')
        if t not in TIERS:
            print('tier', where, t)
            problems += 1
        if not re.fullmatch(r'[a-z]+', c.get('en', '')):
            print('en', where, c.get('en'))
            problems += 1
        if c.get('en') in seen:
            print('撞 en', where, seen[c['en']])
            problems += 1
        seen[c.get('en')] = where
        for k in ['who', 'palette', 'casual', 'private', 'battle', 'formal', 'art']:
            for label, rx in BAD.items():
                for m in re.finditer(rx, c.get(k, ''), re.I):
                    print(label, where, k, repr(c[k][max(0, m.start() - 30):m.end() + 20]))
                    problems += 1
print('一共', len(cast), '位', '问题', problems)
print('tier', {t: sum(1 for c in cast if c.get('tier') == t) for t in TIERS})
