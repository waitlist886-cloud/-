# 次要地点与活事件铺开：照地点谱合表，列某一纪还没有自己条目的地点，按地区分组
# 用法：python -I -X utf8 底稿/地图/铺开/名单.py 纪 [--md 输出.md] [--json 输出.json]
#   纪：月银纪、纷争纪、山铜纪、迷宫纪前传
# 有没有自己的条目：这一纪的稿子里有没有 ## X纪·(地点|城邦|城区|遗迹|迷宫|迷宫城|险地)｜ 标题，或者月银纪最早那三批
#   （moon/batch1 到 3）的 === 名字 加 文件夹：4x，标题拆开「与」「和」以后有一截跟这个名字对得上（去掉括号）。
#   对不上又确实有条目的，写在同目录 认条目.tsv（纪、名字、条目标题），先查它。条目标题写 无 就是认定没有。
# 地区照坐标分（地区表在下面 REGIONS，一处只落一个区，先到先得）；不进图的（路、井下各层）单列。
import csv
import glob
import json
import os
import re
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
ERA = sys.argv[1]
args = sys.argv[2:]
T = os.path.join(ROOT, '底稿', '地图', '地点谱', '合表.tsv')
SEG = {
    '月银纪': [('祭火', 1, 1000), ('万兽', 1001, 3000), ('诸国期', 3001, 6006), ('萨尔维斯', 6007, 10081)],
    '纷争纪': [('灰的年月', 1, 120), ('白石的年月', 121, 300), ('灯的年月', 301, 1050), ('炮的年月', 1051, 4500),
            ('浮塔的年月', 4501, 8800), ('铁狼的年月', 8801, 10800), ('号角的年月', 10801, 11034)],
    '山铜纪': [('犁的年月', 2, 300), ('长夜的年月', 301, 579), ('白鸦的年月', 580, 660), ('黎明的年月', 661, 741),
            ('七城的年月', 742, 861), ('麦的年月', 862, 947)],
    '迷宫纪前传': [('探井的年月', 2, 100), ('共约的年月', 101, 317), ('繁荣的年月', 318, 599), ('深井的年月', 600, 849),
              ('黑潮的年月', 850, 970), ('垂暮的年月', 971, 1000)],
}
START = {'月银纪': 1, '纷争纪': 1, '山铜纪': 2, '迷宫纪前传': 2}
END = {'月银纪': 10081, '纷争纪': 11034, '山铜纪': 947, '迷宫纪前传': 1000}
DIRS = {'月银纪': ['月银纪补卷', '月银纪史诗', '诸国期', '萨尔维斯', 'moon/batch1', 'moon/batch2', 'moon/batch3'],
        '纷争纪': ['纷争纪'], '山铜纪': ['山铜纪'], '迷宫纪前传': ['迷宫纪前传']}
TITLE_ERA = {'月银纪': '月银纪', '纷争纪': '纷争纪', '山铜纪': '山铜纪', '迷宫纪前传': '迷宫纪'}
# 地图坐标（2200×1400）。照月银纪那一张样张的地貌分，四纪通用：大陆的形状四纪没大动
REGIONS = [
    ('北方雪原与天脊', lambda x, y: y < 330 and x >= 780),
    ('西北·镜湖与黑石高地', lambda x, y: x < 1000 and y < 600),
    ('环山与帝畿', lambda x, y: x < 1000 and y < 900 and x >= 380),
    ('西海岸与珠湾', lambda x, y: x < 380 and y < 1050),
    ('西南·火山带、盐原、碧湾', lambda x, y: x < 1000),
    ('星坑盆地', lambda x, y: x < 1300 and y < 950),
    ('东北·原初之森与星湖', lambda x, y: x >= 1450 and y < 640),
    ('东·白石平原与风铃高原', lambda x, y: y < 1000),
    ('南原', lambda x, y: x < 1450),
    ('东南·炉城与蜜酒丘陵', lambda x, y: True),
]
NOMAP_KIND = ('路',)
ENTRY_RE = re.compile(r'^## (\S.*)$')
OLD_RE = re.compile(r'^=== (\S.*)$')


def region(x, y):
    for n, f in REGIONS:
        if f(x, y):
            return n
    return '?'


def span(s):
    ys = [int(v) for v in re.findall(r'(?<!\d)(\d{1,5})(?=\s*年|\s*到|\s*起|\)|，|$)', s)]
    ys = [v for v in ys if START[ERA] <= v <= END[ERA]]
    if not ys:
        return None
    lo, hi = min(ys), max(ys)
    if re.search(r'(一直|往后|到今天|至今|纪末|以后|到1001)', s):
        hi = END[ERA]
    return lo, hi


def segs_of(sp):
    if sp is None:
        return []
    return [n for n, a, b in SEG[ERA] if sp[0] <= b and sp[1] >= a]


titles = []
trigs = []
for d in DIRS[ERA]:
    for f in glob.glob(os.path.join(ROOT, d, '**', '*.md'), recursive=True):
        if any(k in f for k in ('旧版', '检查稿', 'parts', '样稿', 'backup')):
            continue
        lines = open(f, encoding='utf-8').read().split('\n')
        cur = None
        for i, line in enumerate(lines):
            m = ENTRY_RE.match(line)
            if m:
                cur = None
                if m.group(1).startswith(TITLE_ERA[ERA] + '·') and \
                        re.search(r'·(地点|城邦|城区|遗迹|迷宫|迷宫城|险地)｜', m.group(1)):
                    cur = m.group(1).strip()
                    titles.append(cur)
                continue
            m = OLD_RE.match(line)
            if m:
                cur = None
                if i + 1 < len(lines) and re.match(r'^文件夹：4[3-5]·', lines[i + 1]):
                    cur = '%s·地点｜%s' % (TITLE_ERA[ERA], m.group(1).replace('（月银纪）', '').strip())
                    titles.append(cur)
                continue
            if cur:
                t = re.search(r'〕、`/(.+?)/`', line) if line.startswith('> 条目设置') else None
                if not t and line.startswith('触发：'):
                    t = re.search(r'/(.+)/\s*$', line)
                if t:
                    try:
                        trigs.append((cur, re.compile(t.group(1))))
                    except re.error:
                        pass
manual = {}
mp = os.path.join(HERE, '认条目.tsv')
if os.path.exists(mp):
    for r in csv.DictReader(open(mp, encoding='utf-8'), delimiter='\t'):
        if r['纪'] == ERA:
            manual[r['名字']] = r['条目标题']


def own(nm):
    if nm in manual:
        return '' if manual[nm] == '无' else manual[nm]
    k = re.sub(r'[（(].*?[）)]', '', nm).strip()
    for t in titles:
        tail = t.split('｜', 1)[1]
        toks = [tail] + [x for x in re.split(r'与|和|、', tail) if len(x) >= 2]
        for tok in toks:
            if k and (k == tok or k in tok or (tok in k and len(tok) >= len(k) - 1)):
                return t
    for t, rx in trigs:
        if k and rx.search(k):
            return t + '（触发认得）'
    return ''


rows = [r for r in csv.DictReader(open(T, encoding='utf-8'), delimiter='\t') if r['纪'] == ERA]
out = OrderedDict((n, []) for n, f in REGIONS)
out['不进图'] = []
out['没有坐标'] = []
for r in rows:
    nm = r['名字']
    o = own(nm)
    try:
        x, y = float(r['地图x']), float(r['地图y'])
    except ValueError:
        x = y = None
    sp = span(r['时段与年份'])
    rec = OrderedDict(名字=nm, 类=r['类'], 主次=r['统一主次'], 条目=o, 段='、'.join(segs_of(sp)) or '?',
                      年份=r['时段与年份'], 位置=r['位置'], x=r['地图x'], y=r['地图y'], 出处=r['出处'])
    if r['类'].startswith(NOMAP_KIND) or '井下' in r['类'] or re.match(r'第[一二三四五六七八九十百\d]+层', nm):
        out['不进图'].append(rec)
    elif x is None:
        out['没有坐标'].append(rec)
    else:
        out[region(x, y)].append(rec)
if '--json' in args:
    json.dump(out, open(args[args.index('--json') + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
lines = ['# %s 地点名单（名单.py 生成，别手改）' % ERA, '']
tot_no = 0
for reg, L in out.items():
    no = [r for r in L if not r['条目']]
    if reg != '不进图':
        tot_no += len(no)
    lines.append('## %s（%d 处，没有自己条目的 %d 处）' % (reg, len(L), len(no)))
    lines.append('')
    for r in L:
        lines.append('- %s %s｜%s｜%s｜%s｜%s｜(%s, %s)%s' % (
            '　' if r['条目'] else '★', r['名字'], r['类'], r['主次'], r['段'], r['年份'][:60], r['x'], r['y'],
            ('｜已有：' + r['条目']) if r['条目'] else ''))
    lines.append('')
lines.insert(1, '没有自己条目的 %d 处（★），不进图的单列。' % tot_no)
if '--md' in args:
    open(args[args.index('--md') + 1], 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
else:
    print('\n'.join(lines))
