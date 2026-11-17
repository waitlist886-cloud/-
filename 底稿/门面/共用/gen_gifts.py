#!/usr/bin/env python3
# 建档第二版第九步：身穿的人从若娜瓦手里拿的赐物（11-17）。
#   python -I -X utf8 底稿/门面/共用/gen_gifts.py      写 底稿/门面/小样_外壳/data/gifts.json
# 1001 年那一池（old1001.html 的 ronavaGifts 和 ronavaRelics）照搬；遗物那一半只给原主在开局以前已经死了的：
# 原主几时死照打包补丁 进卡补丁_rili_v12.py 的 RELIC_OWNER_BL（原主在世、还没出世的那几年挡掉遗物条的那张表），
# 那张表里没有的遗物（原主活在迷宫纪1001年，或者没写原主）四纪都不给。
import ast
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OLD = os.path.join(HERE, '..', '小样_外壳', 'old1001.html')
PATCH = os.path.join(R, 'out', '进卡_v12', 'tools', '进卡补丁_rili_v12.py')
OUT = os.path.join(HERE, '..', '小样_外壳', 'data', 'gifts.json')
ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪']
BOOK = {'月银纪': 'moon', '纷争纪': 'strife', '山铜纪': 'bronze', '迷宫纪': 'maze'}

s = open(OLD, encoding='utf-8').read()


def arr(key):
    i = s.find(key + '=')
    j = s.find('[', i)
    depth, k = 0, j
    while True:
        c = s[k]
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                break
        elif c == '"':
            k = s.find('"', k + 1)
            while s[k - 1] == '\\':
                k = s.find('"', k + 1)
        k += 1
    return json.loads(s[j:k + 1])


def obj(key):
    i = s.find(key + '=')
    j = s.find('{', i)
    depth, k = 0, j
    while True:
        c = s[k]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        elif c == '"':
            k = s.find('"', k + 1)
            while s[k - 1] == '\\':
                k = s.find('"', k + 1)
        k += 1
    return json.loads(s[j:k + 1])


gifts = arr('ronavaGifts')[:-1]
# 若娜瓦自己给的那几样，挂在后世才有的东西上的写明（★）
GIFT_ERA = {
    '旅印的破例': {'avail': {'maze': 420}, 'note': '旅印分七阶是前传420年以后的事，那以前没有这一件。'},
    '一袋沉甸甸的钱': {'note': '钱照开局那一年当地的币写，同样够体面活一年。索恩、巴尔是迷宫纪246年三币圣约以后才有的名字。'},
    '名匠遗作': {'note': '月银纪没有命路，照你挑的兵器打；纷争纪命路还没名字的，照你那一路的打法打。'},
    '旧日术式集': {'note': '月银纪照你的法门给三门基础的术。'},
    '旧识的引荐信': {'note': '收信的是开局那一年已经有的势力、行会或学院。'},
    '不会迷路的罗盘': {'note': '迷宫里的那一半，四纪只有前传用得上。'},
}
for g in gifts:
    g.update(GIFT_ERA.get(g['n'], {}))
relics = arr('ronavaRelics')
eff = obj('RELIC_EFFECTS')

src = open(PATCH, encoding='utf-8').read()
i = src.find('RELIC_OWNER_BL = {')
j = src.find('\n}\n', i)
table = ast.literal_eval(src[i + len('RELIC_OWNER_BL = '): j + 2])
owner = {}
for idx, (title, wins) in table.items():
    m = re.search(r'「([^」]+)」|《([^》]+)》', title)
    nm = (m.group(1) or m.group(2)) if m else title.split('｜')[-1].strip()
    # 最晚的那一段挡到哪一年：那一纪那一年以后才给，更早的纪都不给
    last = max(wins, key=lambda w: (ERAS.index(w[0]), w[2]))
    owner[nm] = (last[0], last[2] + 1, title)

out_relics, miss = [], []
for g in relics:
    o = owner.get(g['n'])
    if not o:
        miss.append(g['n'])
        continue
    era, y, title = o
    av = {}
    for e in ERAS:
        if ERAS.index(e) > ERAS.index(era):
            av[BOOK[e]] = 1
        elif e == era:
            av[BOOK[e]] = y
    out_relics.append(dict(n=g['n'], r=g['r'], d=g['d'], e=eff.get(g['n'], ''), relic=title, avail=av))

D = {'about': '建档第二版第九步，身穿的人拿若娜瓦的赐物。gifts 是她自己给的，四纪都给；relics 只给原主在开局以前已经死了的，avail 写哪一纪从哪一年起给。gen_gifts.py 出的，别手改。',
     'rates': '照 1001：每回抽五件，Legend 三抽以内保一件，Unique 八抽以内保一件。',
     'gifts': gifts, 'relics': out_relics, 'not_given': miss}
json.dump(D, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('gifts', len(gifts), 'relics', len(out_relics), '四纪不给的', len(miss))
for e in ('moon', 'strife', 'bronze', 'maze'):
    print(e, sum(1 for x in out_relics if e in x['avail']))
