# -*- coding: utf-8 -*-
"""全员羁绊那一轮的收稿脚本（11-01）。在仓库根上跑。
  python3 -I -X utf8 tools/bond_merge.py list [--all]      列四纪所有羁绊章，查一纪之内章名、题、协战、伟业、信物重名，跨纪同章名；--all 逐章列出
  python3 -I -X utf8 tools/bond_merge.py status            各份写到了哪里：完整几章（有条目设置的算写完）、半截几章、名单上还差谁
  python3 -I -X utf8 tools/bond_merge.py lines [--apply] [份号…]
        给交来的章在那一纪的旅伴条（### 裁定锁 前头）和凡世至强条（### 专属羁绊剧情 底下那一行）添「专属羁绊：X之章【题】」，
        不加 --apply 只报；写完照报告重拼纷争纪、山铜纪、前传的页（月银纪三卷直接改页）。
名单读 底稿/羁绊/全员/分份.json（份号、写进的文件、每个人在页上的条目）。"""
import sys, re, json, glob, os, collections
ROOT = os.getcwd()
PARTS = json.load(open(os.path.join(ROOT, '底稿/羁绊/全员/分份.json'), encoding='utf-8'))
def cjk(s): return len(re.findall(r'[一-鿿]', s))

def chapters():
    files = sorted(glob.glob('月银纪补卷/羁绊_*.md')) + sorted(glob.glob('纷争纪/补卷/补卷_*羁绊*.md')) + \
            sorted(glob.glob('山铜纪/补卷/补卷_*羁绊*.md')) + sorted(glob.glob('迷宫纪前传/补卷/补卷_*羁绊*.md'))
    rows = []
    for f in files:
        if '规则' in f: continue
        t = open(f, encoding='utf-8').read()
        for e in re.split(r'\n(?=## )', t):
            m = re.match(r'## (月银纪|纷争纪|山铜纪|迷宫纪)·羁绊｜(.+?)之章·(.+)', e)
            if not m: continue
            era, x, ti = m.groups()
            who = re.search(r'\n【(?!调用)([^】]+)】', e)
            rows.append(dict(era=era, x=x, ti=ti.strip(), who=who.group(1) if who else '?', file=f,
                             n=cjk(e.split('> 条目设置')[0]), done='> 条目设置' in e,
                             co=re.findall(r'协战【([^】]+)】', e), wy=re.findall(r'伟业【([^】]+)】', e),
                             xw=re.findall(r'信物【([^】]+)】', e)))
    return rows

def cmd_list():
    rows = chapters()
    print('章数', dict(collections.Counter(r['era'] for r in rows)))
    for key, label in [('x', '章名'), ('ti', '题'), ('co', '协战'), ('wy', '伟业'), ('xw', '信物')]:
        for era in ['月银纪', '纷争纪', '山铜纪', '迷宫纪']:
            c = collections.defaultdict(list)
            for r in rows:
                if r['era'] != era: continue
                for v in (r[key] if isinstance(r[key], list) else [r[key]]):
                    c[v].append(r['who'][:12] + '@' + r['file'].split('/')[-1])
            for v, ws in c.items():
                if len(ws) > 1: print('  重%s［%s］%s：%s' % (label, era, v, '；'.join(ws)))
    c = collections.defaultdict(set)
    for r in rows: c[r['x']].add(r['era'])
    for v, es in c.items():
        if len(es) > 1: print('  跨纪同章名', v, sorted(es))
    if '--all' in sys.argv:
        for r in rows: print(r['era'], r['x'] + '之章【' + r['ti'] + '】', r['who'][:16], r['n'], r['file'], '' if r['done'] else '半截')

def cmd_status():
    rows = chapters()
    for pt in PARTS:
        mine = [r for r in rows if r['file'] == pt['file']]
        names = [p['name'] for p in pt['people']]
        got = set(n for n in names for r in mine if r['done'] and r['who'].startswith(n))
        half = [r['x'] for r in mine if not r['done']]
        left = [n for n in names if n not in got]
        note = os.path.exists('底稿/羁绊/全员/%s_备注.md' % pt['code'])
        print('%s 完整%d/%d%s%s｜%s' % (pt['code'], len(got), len(names), (' 半截%d' % len(half)) if half else '',
              '' if note else ' 无备注', ('还差 ' + '、'.join(left)) if left else '齐了'))

def era_of(f):
    if f.startswith(('月银纪史诗', '诸国期', '萨尔维斯')): return '月银纪'
    if f.startswith('纷争纪'): return '纷争纪'
    if f.startswith('山铜纪'): return '山铜纪'
    return '迷宫纪'

def cmd_lines():
    apply = '--apply' in sys.argv
    only = [a for a in sys.argv[2:] if not a.startswith('--')]
    SRC = {'月银纪': glob.glob('月银纪史诗/第*歌_*.md') + glob.glob('诸国期/诸国期时段_*.md') + glob.glob('萨尔维斯/萨尔维斯时段_*.md'),
           '纷争纪': glob.glob('纷争纪/parts*/*.md'), '山铜纪': glob.glob('山铜纪/parts*/*.md'), '迷宫纪': glob.glob('迷宫纪前传/parts*/*.md')}
    cache = {}
    def get(f):
        if f not in cache: cache[f] = open(f, encoding='utf-8').read().split('\n')
        return cache[f]
    rows = chapters(); bad = 0; done = 0; touched = set()
    for pt in PARTS:
        if only and pt['code'] not in only: continue
        mine = [r for r in rows if r['file'] == pt['file'] and r['done']]
        for p in pt['people']:
            era = p['era']; names = [p['name']] + p['full']
            cand = [r for r in mine if any(r['who'].startswith(n) for n in names)]
            if not cand: continue
            if len(cand) != 1: print('  一个人对上几章', pt['code'], p['name'], [r['x'] for r in cand]); bad += 1; continue
            r = cand[0]; label = r['x'] + '之章【' + r['ti'] + '】'
            for f, line, typ, head, w in p['pages']:
                if era_of(f) != era: continue
                heading = '## ' + ('凡世至强：' if typ == '传奇' else '旅途同行：') + head
                hs = [(sf, i) for sf in SRC[era] for i, ln in enumerate(get(sf)) if ln == heading]
                if era == '月银纪': hs = [h for h in hs if h[0] == f]
                if len(hs) != 1: print('  标题找到', len(hs), '处', pt['code'], heading); bad += 1; continue
                sf, i = hs[0]; L = get(sf); j = i + 1
                if typ == '传奇':
                    while j < len(L) and not L[j].startswith('## ') and not L[j].startswith('### 专属羁绊剧情'): j += 1
                    if j >= len(L) or not L[j].startswith('### 专属羁绊剧情'): print('  凡世至强没有专属羁绊剧情', heading); bad += 1; continue
                    if L[j + 1].startswith('- 专属羁绊：'): continue
                    if not L[j + 1].startswith('- 《'): print('  专属羁绊剧情下一行不是《》', heading); bad += 1; continue
                    L[j + 1] = '- 专属羁绊：' + label; touched.add(sf); done += 1
                else:
                    while j < len(L) and not L[j].startswith('## ') and not L[j].startswith('### 裁定锁'): j += 1
                    if j >= len(L) or not L[j].startswith('### 裁定锁'): print('  找不到裁定锁', heading); bad += 1; continue
                    if any(x.startswith('专属羁绊：') for x in L[i:j]): continue
                    L[j:j] = ['专属羁绊：' + label, '']; touched.add(sf); done += 1
    print('添了', done, '处，对不上', bad, '，文件', len(touched))
    for f in sorted(touched): print('  ', f)
    if apply and not bad:
        for f in touched: open(f, 'w', encoding='utf-8').write('\n'.join(cache[f]))
        print('写了', len(touched), '个文件，纷争纪 bash tools/assemble_strife.sh N，山铜纪 tools/assemble_shantong_pN.py .，前传 tools/assemble_maze.py . N 重拼')
    elif apply: print('有对不上的，没写')

if __name__ == '__main__':
    {'list': cmd_list, 'status': cmd_status, 'lines': cmd_lines}.get(sys.argv[1] if len(sys.argv) > 1 else '', lambda: print(__doc__))()
