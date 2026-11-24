#!/usr/bin/env python3
# 过条底子（11-24）：几支脚本共用的东西。只读卡的文件，不写。
#   scan.py      清点 → 清点.json、清点.md、分份.json
#   material.py  照分份出材料 → 材料/<份>.md
#   splice.py    交稿换回源稿（--dry 只报）
import csv
import glob
import json
import os
import re

NL = chr(10)
CRLF = chr(13) + chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, '..'))                     # 底稿/收尾_11-24/过条
ROOT = os.path.normpath(os.path.join(W, '..', '..', '..'))         # 仓库根
OLD = os.path.join(ROOT, '底稿', '命星重审第二轮')                  # 11-20 旅伴过条那一轮
TIER = r'(?:Normal|Rare|Epic|Legend|Unique)'
JIE = re.compile(TIER + r'·(?:[一二三四五]阶|未入阶)')
# 一行里的星：Special【X】、天赋【X】……；技艺、Art 算主修，天赋、被动算生来的
MARK = re.compile(r'(Special|Passive|Art|天赋|被动|技艺)【([^】]+)】')
KIND = {'Special': 'S', '天赋': 'S', 'Passive': 'P', '被动': 'P', 'Art': 'A', '技艺': 'A'}
ERA_GROUP = {'月银纪': '月银纪', '诸国期': '月银纪', '萨尔维斯': '月银纪', '纷争纪': '纷争纪', '山铜纪': '山铜纪', '迷宫纪前传': '迷宫纪前传'}
ERA_ORDER = ['月银纪', '诸国期', '萨尔维斯', '纷争纪', '山铜纪', '迷宫纪前传']
SUPP_DIRS = [('月银纪', '月银纪补卷'), ('萨尔维斯', '萨尔维斯/补卷'), ('纷争纪', '纷争纪/补卷'),
             ('山铜纪', '山铜纪/补卷'), ('迷宫纪前传', '迷宫纪前传/补卷')]


def rd(p):
    return open(p, encoding='utf-8').read().replace(CRLF, NL)


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, '/')


def pages():
    """[(页键, 纪, 拼好的页)]，页键照 11-20 那一轮的 材料/索引.json。"""
    idx = json.load(open(os.path.join(OLD, '材料', '索引.json'), encoding='utf-8'))
    out = []
    for k, v in idx.items():
        out.append((k, k.rsplit('_', 1)[0], os.path.join(ROOT, v['file'])))
    return out


def part_files(key):
    """有分段源稿的页：分段目录里所有 .md（没拼进页的旧份也算，跟 splice_rare 一样）；没有的返回 None。"""
    era, n = key.rsplit('_', 1)
    n = int(n)
    if era == '纷争纪':
        d = os.path.join(ROOT, '纷争纪', 'parts' if n == 1 else 'parts%d' % n)
    elif era == '山铜纪':
        d = os.path.join(ROOT, '山铜纪', 'parts%d' % n)
    elif era == '迷宫纪前传':
        d = os.path.join(ROOT, '迷宫纪前传', 'parts%d' % n)
    else:
        return None
    return sorted(glob.glob(os.path.join(d, '*.md')))


def supp_files():
    out = []
    for era, d in SUPP_DIRS:
        for f in sorted(glob.glob(os.path.join(ROOT, d, '*.md'))):
            if '说明' in os.path.basename(f):
                continue
            out.append((era, f))
    return out


def entries(t):
    """[(起点, 条目全文)]，按「## 」切，「## 裁定锁」不另算。"""
    pos = [m.start() for m in re.finditer(r'(?m)^## (?!裁定锁)', t)]
    return [(s, t[s:(pos[i + 1] if i + 1 < len(pos) else len(t))]) for i, s in enumerate(pos)]


def entry_kind(h):
    if h.startswith('## 旅途同行'):
        return '旅伴'
    if h.startswith('## 凡世至强'):
        return '凡世至强'
    if h.endswith('（人物）') or '·人物｜' in h or h.startswith('## 人物｜'):
        return '人物'
    return ''


def default_who(h, kind):
    s = h[3:].strip()
    if kind == '凡世至强':
        s = s.split('：', 1)[-1]
        s = s.split(' · ', 1)[-1]
        return re.sub(r'（[^）]*）$', '', s).strip()
    supp = '｜' in s and not s.endswith('（人物）')
    s = re.sub(r'（人物）$', '', s)
    s = s.split('｜', 1)[-1]
    parts = [x.strip() for x in s.split('，')]
    plain = [x for x in parts if '的' not in x and len(x) <= 12]
    if supp and plain:             # 补卷写「X·人物｜描述，名」或「X·人物｜名，描述」：取不带「的」的那一段
        return plain[-1]
    s = parts[-1]                  # 页上写「描述，名（人物）」
    if '的' in s:
        s = s.split('的')[-1]
    return s.strip()


def segs(line):
    """一行里的星切成段：[(类, 名, 段落文字)]。"""
    ms = list(MARK.finditer(line))
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(line)
        out.append((KIND[m.group(1)], m.group(2), line[m.start():end]))
    return out


def tier_of(seg):
    m = re.search(TIER, seg)
    return m.group(0) if m else ''


def star_index():
    """星条：名 → [(页键或文件, 类, 档, 有没有阶那一行)]；底卡技艺池子记作 底卡。"""
    idx = {}
    blk = re.compile(r'^### (\S+) \((Special|Passive|Art) \| (\w+)\)\n(.*?)(?=^### |^## |^> 条目设置|\Z)', re.S | re.M)
    srcs = [(k, p) for k, _, p in pages()] + [(rel(f), f) for _, f in supp_files()]
    for k, p in srcs:
        t = rd(p)
        for m in blk.finditer(t):
            idx.setdefault(m.group(1), []).append((k, m.group(2), m.group(3), bool(re.search(r'^- 阶：', m.group(4), re.M))))
    raw = rd(os.path.join(ROOT, 'src', 'rili_v7.json'))
    for n, tr in set(re.findall(r'## (\S+) \(Art \| (\w+)\)', raw)):
        idx.setdefault(n, []).append(('底卡', 'Art', tr, False))
    return idx


def star_blocks():
    """名 → [(页键或文件, 整块文字)]，出材料用。"""
    out = {}
    blk = re.compile(r'^### (\S+) \((Special|Passive|Art) \| (\w+)\)\n.*?(?=^### |^## |^> 条目设置|\Z)', re.S | re.M)
    srcs = [(k, p) for k, _, p in pages()] + [(rel(f), f) for _, f in supp_files()]
    for k, p in srcs:
        for m in blk.finditer(rd(p)):
            out.setdefault(m.group(1), []).append((k, m.group(0).rstrip()))
    return out


def lineage():
    """全谱：技艺名（含旧名、原技艺）→ 行。"""
    out = {}
    p = os.path.join(ROOT, '底稿', '命星高魔化', '全谱', '全谱.tsv')
    for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
        for k in ('技艺', '旧名', '原技艺'):
            if r.get(k):
                out.setdefault(r[k], r)
    return out


def companions():
    """旅伴：短名 → [(页键, 纪组, 能力行, 兼修行)]。"""
    out = {}
    for k, era, p in pages():
        t = rd(p)
        for _, e in entries(t):
            m = re.match(r'## 旅途同行：([^（\n]+)', e)
            if not m:
                continue
            who = m.group(1).strip()
            ab = re.search(r'^能力：.*$', e, re.M)
            jx = re.search(r'^兼修：.*$', e, re.M)
            out.setdefault(who.split('·')[0], []).append((k, ERA_GROUP[era], ab.group(0) if ab else '', jx.group(0) if jx else ''))
    return out


def load_json(name):
    return json.load(open(os.path.join(W, name), encoding='utf-8'))
