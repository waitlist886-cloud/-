"""命星名配额检查（10-25，照 底卡洗稿与命名重审_方向稿_第三版.md 第三节第6条和写作口径「起名」）。

用法：
  python3 -I -X utf8 tools/namelint.py 页.md ...
  python3 -I -X utf8 tools/namelint.py --map 对照表.md [--map 另一份.md] 页.md ...

不给页就扫全部四十五页。给了 --map，先照对照表把星名换掉再数，换名以前拿它预演。
对照表是 markdown 表格，表头里要有「现名」和「改成」两栏，改成写新名字，写「不动」或空着就是不改。
同一个现名在几张表里出现，以最后读到的为准，前后不一样会报出来。

数的东西：
  Art：正名（四个字以上）和俗名（两三个字）各几成，俗名里不带门类字的几个，
       同一个收尾字最多几颗，剑律是不是只有斩风剑律、黎明剑律、命烛剑律。
  Special：四个字的几颗，别的长度几颗，X之Y 几颗，同一个后两字最多几颗。
  Passive：同一种收尾（后两字）最多几颗，X之Y 几颗。
  名字里有没有禁词、月相字、之术。
  传奇之名那一行收在的那一个上的有几行。
  全卷：两颗不同的星改成同一个名字、改成了别的星现在的名字，报错。改成了底卡命星的名字，列出来看一眼。
只是报数，不改文件。警告合计是 0 不一定就好，数字给人看。
"""
import re, sys, glob, os, json, collections, math

PAGES = ['月银纪史诗/第*歌_*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md',
         '纷争纪/纷争纪时段_*.md', '山铜纪/山铜纪时段_*.md', '迷宫纪前传/迷宫纪前传时段_*.md']
HEAD = re.compile(r'^### (.+?) \((Art|Special|Passive|Active)\s*\|\s*(\w+)\)\s*$')
HAN = re.compile(r'[一-鿿]')
CATEGORY = set('术法律式谣调颂歌曲祷咏剑舞技阵')
SWORD_LAW_OK = {'斩风剑律', '黎明剑律', '命烛剑律'}
BANNED = ['仪轨', '时辰', '修为', '功法', '宗门', '长老', '威压', '一丝', '一抹', '系统', '坐标', '能量',
          '量子', '频率', '熵', '新月', '满月', '残月', '月牙', '弦月', '月亮', '月光', '之术', '宗师', '宗匠']


def hanlen(s):
    return len(HAN.findall(s))


def read_maps(paths):
    m, src, clash = {}, {}, []
    for p in paths:
        rows = [l.rstrip('\n') for l in open(p, encoding='utf-8')]
        cols = None
        for ln in rows:
            if not ln.startswith('|'):
                cols = None
                continue
            cells = [c.strip() for c in ln.strip().strip('|').split('|')]
            if cols is None:
                if '现名' in cells and '改成' in cells:
                    cols = (cells.index('现名'), cells.index('改成'))
                continue
            if set(''.join(cells)) <= set('-: '):
                continue
            if max(cols) >= len(cells):
                continue
            old = re.sub(r'（.*?）|\(.*?\)', '', cells[cols[0]]).strip()
            new = cells[cols[1]].strip()
            new = re.split(r'[，,（(]', new)[0].strip()
            if not old:
                continue
            if new in ('', '不动', '照旧', '—', '-'):
                new = old
            if old in m and m[old] != new:
                clash.append((old, m[old], new, src[old], p))
            m[old] = new
            src[old] = p
    return m, clash


def base_star_names(root):
    path = os.path.join(root, 'src', 'rili_v7.json')
    if not os.path.exists(path):
        return set()
    card = json.load(open(path, encoding='utf-8'))

    def find(c):
        if isinstance(c, dict):
            for v in c.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and 'content' in v[0]:
                    return v
                r = find(v)
                if r:
                    return r
    wb = find(card) or []
    names = set()
    rx = re.compile(r'^## (.+?) \((?:Art|Special|Passive|Active)\s*\|', re.M)
    for e in wb:
        for mm in rx.finditer(e['content']):
            names.add(mm.group(1).strip())
    return names


def main(argv):
    maps, pages = [], []
    i = 0
    while i < len(argv):
        if argv[i] == '--map':
            maps.append(argv[i + 1]); i += 2
        else:
            pages.append(argv[i]); i += 1
    root = '.'
    if not pages:
        for pat in PAGES:
            pages += sorted(glob.glob(pat))
    allpages = []
    for pat in PAGES:
        allpages += sorted(glob.glob(pat))
    mapping, clash = read_maps(maps) if maps else ({}, [])
    base = base_star_names(root)

    # 全卷现有的星名，查改名撞车用
    defined = collections.defaultdict(set)
    for f in allpages:
        for ln in open(f, encoding='utf-8'):
            mm = HEAD.match(ln.rstrip('\n'))
            if mm:
                defined[mm.group(1)].add(f)

    total_warn = 0
    errors = []
    for old, a, b, pa, pb in clash:
        errors.append(f'对照表前后不一：{old} 在 {os.path.basename(pa)} 改 {a}，在 {os.path.basename(pb)} 改 {b}')
    newname_from = collections.defaultdict(set)
    for old, new in mapping.items():
        if new != old:
            newname_from[new].add(old)
    for new, olds in newname_from.items():
        if len(olds) > 1:
            errors.append(f'几颗星改成了同一个名字：{new} ← {"、".join(sorted(olds))}')
        if new in defined and new not in olds and mapping.get(new, new) == new:
            errors.append(f'改成了另一颗现有的星的名字：{new} ← {"、".join(sorted(olds))}')
    base_hits = sorted({new for new, olds in newname_from.items() if new in base})
    unknown = sorted(k for k in mapping if k not in defined)

    for f in pages:
        stars = []
        legend_tic = 0
        for ln in open(f, encoding='utf-8'):
            mm = HEAD.match(ln.rstrip('\n'))
            if mm:
                name = mapping.get(mm.group(1), mm.group(1))
                stars.append((name, mm.group(2), mm.group(3)))
            if ('传奇之名：' in ln or '传奇之名:' in ln) and ('的那一个' in ln or '的那个' in ln):
                legend_tic += 1
        warns = []
        arts = [s for s in stars if s[1] == 'Art']
        sps = [s for s in stars if s[1] == 'Special']
        pas = [s for s in stars if s[1] == 'Passive']
        n = len(arts)
        short = [a for a in arts if hanlen(a[0]) <= 3]
        short_nocat = [a for a in short if a[0][-1] not in CATEGORY]
        ends = collections.Counter(a[0][-1] for a in arts if a[0])
        top_end = ends.most_common(1)[0] if ends else ('', 0)
        limit_end = max(2, round(0.2 * n))
        if n >= 5:
            share = len(short) / n
            if share < 0.2:
                warns.append(f'俗名只占 {share:.0%}（{len(short)}/{n}），往三到四成补')
            elif share > 0.45:
                warns.append(f'俗名占 {share:.0%}（{len(short)}/{n}），正名该占六到七成')
        if short and len(short_nocat) * 2 < len(short):
            warns.append(f'俗名里不带门类字的只有 {len(short_nocat)}/{len(short)}：{"、".join(a[0] for a in short)}')
        for ch, c in ends.items():
            if c > limit_end:
                warns.append(f'Art 收在「{ch}」上的 {c} 颗，一页至多 {limit_end}：{"、".join(a[0] for a in arts if a[0].endswith(ch))}')
        for a in arts:
            if '剑律' in a[0] and a[0] not in SWORD_LAW_OK:
                warns.append(f'剑律全卷只留三门：{a[0]}')
        sp4 = [s for s in sps if hanlen(s[0]) == 4]
        sp_zhi = [s for s in sps + pas if hanlen(s[0]) == 4 and s[0][2] == '之']
        if len(sp_zhi) > 2:
            warns.append(f'Special、Passive 里 X之Y {len(sp_zhi)} 颗，一页至多两颗：{"、".join(s[0] for s in sp_zhi)}')
        tail2 = collections.Counter(s[0][-2:] for s in sps if hanlen(s[0]) >= 3)
        for t, c in tail2.items():
            if c > 2:
                warns.append(f'Special 后两字「{t}」{c} 颗，一页至多两颗')
        ptail = collections.Counter(s[0][-2:] for s in pas if hanlen(s[0]) >= 3)
        for t, c in ptail.items():
            if c > 3:
                warns.append(f'Passive 收尾「{t}」{c} 颗，一页至多三颗')
        for s in stars:
            for w in BANNED:
                if w in s[0]:
                    warns.append(f'名字里有「{w}」：{s[0]}')
        if legend_tic:
            warns.append(f'传奇之名那一行收在的那一个上的 {legend_tic} 行')
        total_warn += len(warns)
        print(f'== {os.path.basename(f)} | Art {n}（正名 {n - len(short)}，俗名 {len(short)}，其中不带门类字 {len(short_nocat)}，收尾最多「{top_end[0]}」{top_end[1]}）'
              f' | Special {len(sps)}（四字 {len(sp4)}，别的 {len(sps) - len(sp4)}） | Passive {len(pas)} | X之Y {len(sp_zhi)} | 警告 {len(warns)}')
        for w in warns:
            print('  - ' + w)
    if maps:
        print(f'对照表：读到 {len(mapping)} 行，改名 {sum(1 for k, v in mapping.items() if k != v)} 颗')
        if unknown:
            print('  对照表里有、页上找不到的现名：' + '、'.join(unknown[:40]) + ('……' if len(unknown) > 40 else ''))
        if base_hits:
            print('  改成了底卡命星的名字（照底卡接的看一眼对不对）：' + '、'.join(base_hits))
    for e in errors:
        print('错误：' + e)
    print(f'合计 警告 {total_warn} 错误 {len(errors)}')


if __name__ == '__main__':
    main(sys.argv[1:])
