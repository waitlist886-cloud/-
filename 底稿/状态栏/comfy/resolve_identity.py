#!/usr/bin/env python3
# 立绘铺开（11-05）：资料里写了 same_as（这个人的中文名）的，换成这个人时间上最近的后一版的头，填进 identity。
# 时间从后往前：1001 那一套 → 前传 q6…q1 → 山铜纪 s6…s1 → 纷争纪 z7…z1 → 萨尔维斯 sa6…sa1 → 诸国期 zg6…zg1 → 月银纪史诗 ge15…ge1。
# 后一版的图还没出的照样填（出图按这个次序走，轮到它时图已经在了），只是报一声。认名字：先认全名，再认去掉姓的名字（只认得一个人的时候）。
#   python resolve_identity.py           只报
#   python resolve_identity.py --apply   写回
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, 'cast')
OUT = os.path.join(HERE, 'out')
CN = '一二三四五六七八九十'


def page_rank(set_, fn):
    m = re.match(r'[a-z]+(\d+)', os.path.basename(fn))
    return -int(m.group(1)) if m else 0


SETS = ['前传', '山铜纪', '纷争纪', '萨尔维斯', '诸国期', '月银纪史诗']
versions = []   # (时间位次, 名字, identity 路径, 文件, 键)
for f in ['cast_0', 'cast_B', 'cast_C', 'cast_D', 'cast_E', 'cast_Y']:
    p = os.path.join(C, f + '.json')
    if os.path.exists(p):
        for c in json.load(open(p, encoding='utf-8')):
            versions.append(((0, 0), c['name'], '立绘_v3/%s/head.png' % c['en'], p, c['en']))
for i, s in enumerate(SETS):
    for p in glob.glob(os.path.join(C, s, '*.json')):
        for c in json.load(open(p, encoding='utf-8')):
            versions.append(((i + 1, page_rank(s, p)), c['name'], '立绘_%s/%s/head.png' % (s, c['en']), p, c['en']))


def given(n):
    return re.split(r'[·・]', n)[0]


apply = '--apply' in sys.argv
for i, s in enumerate(SETS):
    for p in sorted(glob.glob(os.path.join(C, s, '*.json'))):
        data = json.load(open(p, encoding='utf-8'))
        me = (i + 1, page_rank(s, p))
        changed = False
        for c in data:
            want = c.get('same_as')
            if not want or c.get('identity'):
                continue
            later = [v for v in versions if v[0] < me]
            hit = [v for v in later if v[1] == want]
            if not hit:
                g = [v for v in later if given(v[1]) == given(want)]
                if len({v[1] for v in g}) == 1:
                    hit = g
            if not hit:
                print('认不出', os.path.basename(p), c['en'], want)
                continue
            v = max(hit, key=lambda v: v[0])   # 时间上离这一版最近的后一版
            c['identity'] = v[2]
            changed = True
            print('%s %s → %s%s' % (os.path.basename(p), c['en'], v[2], '' if os.path.exists(os.path.join(OUT, v[2])) else '（图还没出）'))
        if changed and apply:
            open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
