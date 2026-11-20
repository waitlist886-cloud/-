#!/usr/bin/env python3
# 命星重审第二轮（11-19 夜）：把筛表各份（交稿/screen_*.md）合成一张。
#   python -I -X utf8 底稿/命星重审第二轮/tools/merge_screen.py
# 写 底稿/命星重审第二轮/筛表_第一版.md（给用户看）和 筛表.tsv（往后派活用）。
# 同一个人同一颗星在几页都出现的（跨页的旅伴），只留头一页那一行，后几页记在“又见”里。
import collections
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
W = os.path.join(ROOT, '底稿', '命星重审第二轮')
ERAS = ['月银纪', '诸国期', '萨尔维斯', '纷争纪', '山铜纪', '迷宫纪前传']
TITLE = {'月银纪': '月银纪·万兽史诗', '诸国期': '月银纪·诸国期', '萨尔维斯': '月银纪·萨尔维斯', '纷争纪': '纷争纪', '山铜纪': '山铜纪', '迷宫纪前传': '迷宫纪前传'}


def keyorder(name):
    m = re.match(r'screen_(.+)_(\d+)_(\d+)\.md', os.path.basename(name))
    return ERAS.index(m.group(1)), int(m.group(2)), int(m.group(3))


def main():
    idx = json.load(open(os.path.join(W, '材料', '索引.json'), encoding='utf-8'))
    rows, uniq, seen = [], collections.OrderedDict(), {}
    for f in sorted(glob.glob(os.path.join(W, '交稿', 'screen_*.md')), key=keyorder):
        era_i, pg, _ = keyorder(f)
        era = ERAS[era_i]
        key = '%s_%02d' % (era, pg)
        t = open(f, encoding='utf-8').read()
        for l in t.splitlines():
            if not l.startswith('|') or l.startswith('|---'):
                continue
            c = [x.strip() for x in l.strip().strip('|').split('|')]
            if len(c) < 8 or c[0] == '旅伴':
                continue
            who, cat, star, cur, verdict, why, tier, way = c[:8]
            k = (who.split('·')[0], re.sub(r'^(Special|Passive)', '', star))
            if k in seen:
                seen[k]['again'].append(key)
                continue
            r = dict(era=era, page=key, who=who, cat=cat, star=star, cur=cur, v=verdict, why=why, tier=tier, way=way, again=[])
            seen[k] = r
            rows.append(r)
        u = re.search(r'### Unique 候选\n(.*?)(?=\n### |\Z)', t, re.S)
        if u:
            for l in u.group(1).splitlines():
                if l.startswith('- ') and '没有' not in l[:6]:
                    uniq.setdefault(key, []).append(l[2:].strip())
    # tsv
    with open(os.path.join(W, '筛表.tsv'), 'w', encoding='utf-8', newline='\n') as o:
        o.write('页\t旅伴\t类别\t星\t现档\t判\t为什么\t拟档\t方向\t又见\n')
        for r in rows:
            o.write('\t'.join([r['page'], r['who'], r['cat'], r['star'], r['cur'], r['v'], r['why'], r['tier'], r['way'], '、'.join(r['again'])]) + '\n')
    # 统计
    out = ['# 命星重审第二轮·筛表第一版（11-19 夜）', '',
           '四纪各页旅伴生来的两颗星（Special、Passive），每颗判一档：对（照留）、轻改（出身对，补魔法或调档）、重写（射箭画靶或只是习惯）、真名层（活到 1001 年，名字和档不动）。'
           '拟档照样稿第二版的口径。跨页的同一个人只记头一页。判和拟档是审稿人（Opus）照口径给的，等你过目。', '']
    out += ['## 一、总账', '', '| 纪 | 星 | 对 | 轻改 | 重写 | 真名层 |', '|---|---|---|---|---|---|']
    for era in ERAS:
        rs = [r for r in rows if r['era'] == era]
        if not rs:
            continue
        cnt = collections.Counter(r['v'] for r in rs)
        out.append('| %s | %d | %d | %d | %d | %d |' % (TITLE[era], len(rs), cnt['对'], cnt['轻改'], cnt['重写'], cnt['真名层']))
    out += ['', '品级搭配（Special+Passive，一位旅伴一个），现在和拟的：', '', '| 纪 | 现在 | 拟的 |', '|---|---|---|']
    for era in ERAS:
        cur, new = collections.Counter(), collections.Counter()
        by = collections.OrderedDict()
        for r in rows:
            if r['era'] != era:
                continue
            by.setdefault((r['page'], r['who']), {})[r['star'][:2]] = r
        for (pg, who), d in by.items():
            if 'Sp' in d and 'Pa' in d:
                cur[d['Sp']['cur'] + '+' + d['Pa']['cur']] += 1
                new[d['Sp']['tier'] + '+' + d['Pa']['tier']] += 1
        if cur:
            f = lambda c: '，'.join('%s %d' % (k, v) for k, v in c.most_common(6))
            out.append('| %s | %s | %s |' % (TITLE[era], f(cur), f(new)))
    out += ['', '## 二、Unique 候选（每页审稿人拟的，等你定）', '']
    for key, us in uniq.items():
        out.append('**%s**（%s）' % (key, os.path.basename(idx[key]['file'])))
        out += ['- ' + u for u in us]
        out.append('')
    out += ['## 三、逐页', '']
    for key in idx:
        rs = [r for r in rows if r['page'] == key]
        if not rs:
            continue
        out += ['### %s（%s）' % (key, os.path.basename(idx[key]['file'])), '',
                '| 旅伴 | 类别 | 星 | 现档 | 判 | 为什么 | 拟档 | 方向 |', '|---|---|---|---|---|---|---|---|']
        for r in rs:
            ag = '（又见 %s）' % '、'.join(r['again']) if r['again'] else ''
            out.append('| %s%s | %s | %s | %s | %s | %s | %s | %s |' % (r['who'], ag, r['cat'], r['star'], r['cur'], r['v'], r['why'], r['tier'], r['way']))
        out.append('')
    open(os.path.join(W, '筛表_第一版.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
    print('合了', len(rows), '颗星，Unique 候选', sum(len(v) for v in uniq.values()), '条')


if __name__ == '__main__':
    main()
