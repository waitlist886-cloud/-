#!/usr/bin/env python3
# 建档第二版第五步“金血”用的资料（11-17）：各纪挑得到哪几位神亲，祂落在血里的那一颗金血祝颂。
#   python -I -X utf8 底稿/门面/共用/gen_gold.py      写 底稿/门面/小样_外壳/data/gold.json
# 神的聚成、倒下年份、神明显像照 build_atlas.load_gods()（两纪神谱和神名表）；祝颂照 底稿/金血祝颂/稿/ 八份，
# 一份里的次序就是 名单.tsv 里那一份的次序。月银纪、纷争纪用份1 到份7 那七十二颗，山铜纪、前传用份8 七神那一版。
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_atlas as BA  # noqa: E402

R = BA.R
G = os.path.join(R, '底稿', '金血祝颂')
OUT = os.path.join(HERE, '..', '小样_外壳', 'data', 'gold.json')


def parse_share(p):
    s = open(p, encoding='utf-8').read().replace('\r', '')
    s = s.split('\n## 备注')[0]
    out = []
    for m in re.finditer(r'(?m)^### (.+?) \(Passive \| Legend\)\s*$', s):
        end = s.find('\n### ', m.end())
        body = s[m.end(): end if end > 0 else len(s)]
        body = body.split('\n> 条目设置')[0]
        g = lambda rx: (re.search(rx, body, re.M).group(1).strip() if re.search(rx, body, re.M) else '')
        out.append(dict(star=m.group(1).strip(), bless=g(r'^(?:> |- )祝颂：(.+)$'), motto=g(r'^- 箴言：(.+)$'),
                        desc=g(r'^【' + re.escape(m.group(1).strip()) + r'】(.+)$'),
                        eff=g(r'^- 被动：(.+)$'), lim=g(r'^- 限制：(.+)$'), ai=g(r'^- 只给 AI[：，](.+)$'),
                        old=g(r'^- 前传的局[：，](.+)$')))
    return out


rows = list(csv.DictReader(open(os.path.join(G, '名单.tsv'), encoding='utf-8'), delimiter='\t'))
stars = {}
for p in sorted(glob.glob(os.path.join(G, '稿', '份*.md'))):
    fen = re.match(r'(份\d)', os.path.basename(p)).group(1)
    names = [r['神'] for r in rows if r['份'] == fen]
    got = parse_share(p)
    if len(got) != len(names):
        sys.exit('%s 有 %d 颗，名单 %d 位' % (p, len(got), len(names)))
    for n, x in zip(names, got):
        stars[(fen == '份8', n)] = x

gods = {g['n']: g for g in BA.load_gods() if g['side'] in ('正', '柱')}
fam = {(r['份'] == '份8', r['神']): r for r in rows}


def entry(n, seven):
    g, r, x = gods.get(n, {}), fam[(seven, n)], stars[(seven, n)]
    e = dict(n=n, tag=r['神号'], grp=r['组'], pillar=r['柱或正'] == '柱', img=g.get('img', ''), rule=re.sub(r'（★）|★', '', g.get('rule', '')))
    if not seven:
        if g.get('since', 1) > 1:
            e['since'] = g['since']
        if g.get('fell'):
            e['fell'] = g['fell']
    e.update({k: re.sub(r'（★）|★', '', v).strip() for k, v in x.items() if v})          # 建档页上给玩家看的，设计记号拿掉
    return e


two = [entry(r['神'], False) for r in rows if r['份'] != '份8']
seven = [entry(r['神'], True) for r in rows if r['份'] == '份8']
D = {
    'about': '建档第二版第五步“金血”，生在这一纪的人才有，可以跳过。一位正神一颗 Legend 的 Passive。gen_gold.py 出的，别手改。',
    'know': ['知道是谁的血', '不知道，往后自己认出来'],
    'eras': {
        'moon': {'note': '你出生那一年已经聚成的神。', 'gods': two},
        'strife': {'note': '你出生那一年还在世的正神，倒下了的灰着、标哪一年倒下。止戈以后只剩七位。', 'gods': two},
        'bronze': {'note': '七神里的一位。', 'gods': seven},
        'maze': {'note': '七神本人迷宫纪不现身，生不出孩子。祖上是山铜纪七神的孩子，血隔了几代在你身上醒过来。', 'gods': seven, 'skip_gen': True},
    },
}
json.dump(D, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('gold.json', len(two), '+', len(seven), '颗；月银纪开纪就在的', sum(1 for e in two if 'since' not in e),
      '；纷争纪倒下的', sum(1 for e in two if 'fell' in e))
