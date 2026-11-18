# -*- coding: utf-8 -*-
"""四纪旅伴条：按下场分堆，列出活到页末、年轻、位阶够的候选。
用法：python -I -X utf8 comp5.py [--list]
"""
import re, sys, io, glob, os, collections

PAGES = []
for pat in ['月银纪史诗/第*歌*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md',
            '纷争纪/纷争纪时段_*.md', '山铜纪/山铜纪时段_*.md', '迷宫纪前传/迷宫纪前传时段_*.md']:
    PAGES += sorted(glob.glob(pat))

LONG = ['魔族', '精灵', '矮人', '龙裔', '巨魔', '炎角', '轰狱', '梦魇', '夜翼', '深潮', '绯宴', '白骸', '半精灵', '海族', '歌鲛', '霜精', '真龙', '巨裔', '半兽人', '牛魔']
NAT = re.compile(r'老死|病死|病故|寿终|死在床上|死在家里|死在.{0,8}屋里|睡过去|没有醒')
DEAD = re.compile(r'死|殁|没有回来|没回来|没上来|埋|葬|倒下|沉进|烧成|化成|不知所终|下落')
TIERS = ['启源', '共鸣', '灵格', '极境', '英雄', '传奇']

def grab(body, pat, n=4000):
    m = re.search(pat, body, re.S)
    if not m:
        return ''
    return re.sub(r'\s+', ' ', m.group(1)).strip()[:n]

def main():
    rows = []
    for path in PAGES:
        text = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
        for p in re.split(r'(?m)^(?=## )', text):
            m = re.match(r'## 旅途同行：(.+?)\n', p)
            if not m:
                continue
            title = m.group(1).strip()
            if re.search(r'的背景|旅伴之间', title):
                continue
            dz = grab(p, r'(?m)^底座：(.+?)$', 300)
            if not dz:
                continue
            xc = grab(p, r'### 正史里的下场\n+(.+?)(?:\n\n|\n###|\n【|\Z)')
            race = dz.split('，')[0]
            am = re.search(r'(\d+)岁', dz)
            age = int(am.group(1)) if am else -1
            wm = re.search(r'(?:看着|看上去|外表|样子).{0,6}?(\d+|十[四五六七八九]|二十|三十|四十)', dz + p[:1500])
            tier = next((t for t in TIERS if t in dz), '?')
            lm = re.search(r'LVL ?(\d+)', dz)
            lvl = int(lm.group(1)) if lm else -1
            longl = any(k in race for k in LONG)
            tail = xc[-140:]
            nat = bool(NAT.search(xc))
            dead_tail = bool(DEAD.search(tail))
            rows.append(dict(page=os.path.basename(path)[:-3], title=title, race=race, age=age, tier=tier, lvl=lvl,
                             longl=longl, nat=nat, dead_tail=dead_tail, tail=tail, xc=xc))
    c = collections.Counter()
    for r in rows:
        if r['nat']:
            k = '自然死'
        elif not r['dead_tail']:
            k = '页末还在'
        else:
            k = '事里死或别的'
        c[(k, r['tier'])] += 1
    print('旅伴条', len(rows))
    for k in ['自然死', '页末还在', '事里死或别的']:
        print(k, sum(v for (a, b), v in c.items() if a == k), {b: v for (a, b), v in sorted(c.items()) if a == k})
    if '--list' in sys.argv:
        print('--- 页末还在、灵格以上、长生或三十二岁以下')
        for r in rows:
            young = r['longl'] or (0 <= r['age'] <= 32)
            if (not r['nat']) and (not r['dead_tail']) and r['tier'] in ('灵格', '极境', '英雄') and young:
                print('%s｜%s｜%s %s岁｜%s %s｜…%s' % (r['page'][-10:], r['title'][:22], r['race'][:8], r['age'], r['tier'], r['lvl'], r['tail'][-70:]))
    if '--nat' in sys.argv:
        print('--- 自然死、灵格以上、开局三十二岁以下（短寿）')
        for r in rows:
            if r['nat'] and r['tier'] in ('灵格', '极境', '英雄') and (0 <= r['age'] <= 32) and not r['longl']:
                print('%s｜%s｜%s %s岁｜%s %s｜…%s' % (r['page'][-10:], r['title'][:22], r['race'][:8], r['age'], r['tier'], r['lvl'], r['tail'][-60:]))

if __name__ == '__main__':
    main()
