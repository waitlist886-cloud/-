#!/usr/bin/env python3
# 旅伴过条（11-20）：跨页的同一个人，生来的星（Special、Passive）名字和档各页要一致。
#   python -I -X utf8 底稿/命星重审第二轮/tools/xpage_check.py          只报
#   python -I -X utf8 底稿/命星重审第二轮/tools/xpage_check.py --apply  后几页照头一页改能力行和那颗星的标题档
# 头一页照 材料/索引.json 的次序。只动能力行里 (Special|Passive)【X】(档 的档、星条标题里的档；名字不一样的只报，手改。
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from splice_rare import sources, W  # noqa: E402

NL = chr(10)


def main(apply):
    idx = json.load(open(os.path.join(W, '材料', '索引.json'), encoding='utf-8'))
    first, rep, fix = {}, [], []
    for key, v in idx.items():
        for src in sources(key, v['file']):
            t = open(src, encoding='utf-8').read()
            for m in re.finditer(r'^## 旅途同行：([^（\n·]+)[^\n]*\n.*?(?=^## (?!裁定锁)|\Z)', t, re.S | re.M):
                who = m.group(1).strip()
                ab = re.search(r'^能力：.*$', m.group(0), re.M)
                if not ab:
                    continue
                gen = re.findall(r'(Special|Passive)【([^】]+)】\((\w+)', ab.group(0))
                if who not in first:
                    first[who] = (key, gen)
                    continue
                k0, g0 = first[who]
                if k0 == key:
                    continue
                if [(a, b) for a, b, _ in g0] != [(a, b) for a, b, _ in gen]:
                    rep.append('%s：%s 是 %s，%s 是 %s（名字不一样，手看）' % (who, k0, g0, key, gen))
                elif g0 != gen:
                    fix.append((key, src, who, g0, gen))
    print('名字不一样 %d，档不一样 %d' % (len(rep), len(fix)))
    for x in rep:
        print('  ', x)
    for key, src, who, g0, gen in fix:
        print('   %s %s：%s → %s' % (key, who, [(b, c) for _, b, c in gen], [(b, c) for _, b, c in g0]))
    if apply:
        for key, src, who, g0, gen in fix:
            raw = open(src, encoding='utf-8', newline='').read()
            t = raw
            for (k, n, t0), (_, _, t1) in zip(g0, gen):
                if t0 == t1:
                    continue
                t = re.sub(r'(' + k + r'【' + re.escape(n) + r'】\()' + t1, lambda m: m.group(1) + t0, t)
                t = re.sub(r'(^### ' + re.escape(n) + r' \(' + k + r' \| )' + t1 + r'\)', lambda m: m.group(1) + t0 + ')', t, flags=re.M)
            if t != raw:
                open(src, 'w', encoding='utf-8', newline='').write(t)
        print('改了', len(fix), '处')


if __name__ == '__main__':
    main('--apply' in sys.argv)
