#!/usr/bin/env python3
# 命星重审第二轮·铺开（11-20）：新起的星名查撞。
#   python -I -X utf8 底稿/命星重审第二轮/tools/clash.py
# 读 收稿/记录.json（先跑 splice_pu.py parse），写 收稿/撞名.json：
#   一个新名落在两位以上旅伴身上的（头一位留着，后几位要改），
#   新名撞上底卡里现成的星名、或者四纪页上别人没被换掉的星名的（都要改）。
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
W = os.path.join(ROOT, '底稿', '命星重审第二轮')
PAGES = ['月银纪史诗/第*歌_*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md', '纷争纪/纷争纪时段_*.md',
         '山铜纪/山铜纪时段_*.md', '迷宫纪前传/迷宫纪前传时段_*.md']


def walk(o):
    if isinstance(o, dict):
        if isinstance(o.get('content'), str):
            yield o['content']
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def main():
    recs = json.load(open(os.path.join(W, '收稿', '记录.json'), encoding='utf-8'))
    olds = {s['old'] for r in recs for s in r['stars']}
    base = set()
    for c in walk(json.load(open(os.path.join(ROOT, 'src', 'rili_v7.json'), encoding='utf-8'))):
        for m in re.finditer(r'^## (\S+) \((?:Special|Passive|Art|Active)', c, re.M):
            base.add(m.group(1))
    page = set()
    for p in PAGES:
        for f in glob.glob(os.path.join(ROOT, p)):
            for m in re.finditer(r'^### (\S+) \((?:Special|Passive|Art) \|', open(f, encoding='utf-8').read(), re.M):
                page.add(m.group(1))
    keep = page - olds
    owner, out = {}, []
    for r in recs:
        for s in r['stars']:
            who = r['who'].split('·')[0]
            n = s['new']
            why = None
            if n in owner and owner[n] != who:
                why = '跟%s撞了' % owner[n]
            elif n in base and n != s['old']:
                why = '撞上底卡池子里现成的星名'
            elif n in keep and n != s['old']:
                why = '撞上页上别人的星名'
            owner.setdefault(n, who)
            if why:
                out.append({'page': r['page'], 'who': r['who'], 'old': s['old'], 'new': n, 'why': why, 'block': s['block']})
    json.dump(out, open(os.path.join(W, '收稿', '撞名.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('要改名的 %d 颗' % len(out))
    import collections
    print(collections.Counter(x['why'][:6] for x in out))


if __name__ == '__main__':
    main()
