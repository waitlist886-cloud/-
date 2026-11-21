#!/usr/bin/env python3
# 立绘铺开（11-20 夜）：山铜纪缺立绘的人，一页一份出图资料的材料，交 batch_cast.py 起稿。
#   python -I -X utf8 底稿/立绘/tools/cast_material.py <por_cover.json> [纪=山铜纪]
# 写 底稿/立绘/铺开_11-20/材料/<页>.md：这一页要画的人的名单，每人条目里讲长相、衣着、年纪、身份、位阶的那几行。
# 名单照 por_cover.py 出的“没有图”的人，整群的（某某家、那一路人、那几个孩子）先拿掉，写手照写资料说明再判一回画不画。
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, '底稿', '立绘', '铺开_11-20', '材料')
PAGES = {'p1': '山铜纪时段_一_犁的年月', 'p2': '山铜纪时段_二_长夜的年月', 'p3': '山铜纪时段_三_白鸦的年月',
         'p4': '山铜纪时段_四_黎明的年月', 'p5': '山铜纪时段_五_七城的年月', 'p6': '山铜纪时段_六_麦的年月'}
GROUP = re.compile(r'(家$|那一路|那几家|那几个|那一班|两岸的人|十四家|十二家)')
KEEP = re.compile(r'^(固定锚定|身份|外貌|容貌评价|体态数据|装束|底座|位阶|类别|【调用】|- [^｜：]{1,12}[｜：])')
NL = chr(10)


def entries(t):
    pos = [m.start() for m in re.finditer(r'(?m)^## (?!裁定锁)', t)]
    return [t[s:(pos[i + 1] if i + 1 < len(pos) else len(t))] for i, s in enumerate(pos)]


def main():
    cover = json.load(open(sys.argv[1], encoding='utf-8'))['山铜纪']
    os.makedirs(OUT, exist_ok=True)
    tot = 0
    for pg, fn in PAGES.items():
        t = open(os.path.join(ROOT, '山铜纪', fn + '.md'), encoding='utf-8').read().replace(chr(13) + NL, NL)
        es = entries(t)
        names = [n for n, x in cover.items() if not x.get('have') and x['roles'] and x['roles'][0][0] == pg and not GROUP.search(n)]
        parts = []
        for n in names:
            short = n.split('·')[0]
            hit = [e for e in es if short in e.split(NL, 1)[0]]
            if not hit:
                hit = [e for e in es if re.search(r'^- ' + re.escape(short) + r'[｜：·（]', e, re.M) or ('（人物）' in e.split(NL, 1)[0] and short in e)]
            role = cover[n]['roles'][0][1]
            body = []
            for e in hit[:3]:
                h = e.split(NL, 1)[0]
                body.append(h)
                lines = [l for l in e.split(NL)[1:] if KEEP.match(l.strip())]
                if '（人物）' in h or '凡世至强' in h:
                    lines = [l for l in e.split(NL)[1:] if l.strip() and not l.startswith('>')]
                body += [l[:600] for l in lines]
                ln = t[:t.index(e)].count(NL) + 1
                body.append('（源稿行号 山铜纪/%s.md:%d）' % (fn, ln))
            txt = NL.join(body)[:6000]
            parts.append('=' * 20 + NL + '【要画】%s｜%s｜%s' % (n, role, pg) + NL + (txt or '（页上没找到条目，写手判一回画不画）'))
            tot += 1
        open(os.path.join(OUT, '%s.md' % pg), 'w', encoding='utf-8', newline=NL).write(
            '# 山铜纪 %s（%s）：%d 人' % (pg, fn, len(names)) + NL + NL.join(parts) + NL)
        print(pg, len(names), '人')
    print('合计', tot)


if __name__ == '__main__':
    main()
