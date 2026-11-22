#!/usr/bin/env python3
# 门面名单上认不上立绘的人，照一张手写的对照表挂键（11-22 全员补画那一轮写的）。
#   python -I -X utf8 底稿/门面/共用/cast_map.py [月银纪 纷争纪 山铜纪 迷宫纪]
# 对照表 共用/data/cast_map.json：{书: {时代 id 或 "*": {卡上的名字: "套:键"}}}，套是立绘目录名（月银纪史诗、诸国期、萨尔维斯、纷争纪、
# 山铜纪、前传、神明、1001），写 "-" 是把这张卡原来挂的键拿掉（同名不同人借错了图又没有自己的图）。
# 名字照 fix_lists.py 改过以后的写（它改迷宫纪那一本的名字），所以 fix_lists.py 跑完会自己调这一支；单独跑也行。
# 已有键的卡照样换成表里的（贝内特这种借错的）；表里写了、卡上找不到的名字照报，多半是页上改了名、表要跟着改。
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.dirname(HERE)
BOOK = {'月银纪': ('小样_月银纪书', 'moon.json'), '纷争纪': ('小样_纷争纪书', 'strife.json'),
        '山铜纪': ('小样_山铜纪书', 'bronze.json'), '迷宫纪': ('小样_迷宫纪书', 'maze.json')}
GROUPS = ('cast', 'meet', 'legends')


def apply(books=None, quiet=False):
    table = json.load(open(os.path.join(HERE, 'data', 'cast_map.json'), encoding='utf-8'))
    for ji in books or list(BOOK):
        if ji not in table:
            continue
        d, f = BOOK[ji]
        dp = os.path.join(F, d, 'data', f)
        D = json.load(open(dp, encoding='utf-8'))
        m = table[ji]
        n, hit = 0, set()
        for e in D['eras']:
            rows = dict(m.get('*', {}))
            rows.update(m.get(e['id'], {}))
            for g in GROUPS:
                for c in e.get(g) or []:
                    v = rows.get(c['name'])
                    if v is None:
                        continue
                    hit.add((e['id'] if c['name'] in m.get(e['id'], {}) else '*', c['name']))
                    pset, key = ('', '') if v == '-' else v.split(':', 1)
                    if (c.get('pset') or '', c.get('key') or '') != (pset, key):
                        c['pset'], c['key'] = pset, key
                        n += 1
        miss = [(eid, nm) for eid, rows in m.items() for nm in rows if (eid, nm) not in hit]
        open(dp, 'w', encoding='utf-8', newline='\n').write(json.dumps(D, ensure_ascii=False, separators=(',', ':')) + '\n')
        if not quiet or miss:
            print(ji, '照对照表挂了', n, '处' + ('；表里有、名单上找不到：' + '、'.join('%s %s' % x for x in miss) if miss else ''))


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    apply(sys.argv[1:] or None)
