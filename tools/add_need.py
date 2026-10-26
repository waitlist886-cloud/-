"""给寻常字眼的命星名加「X那一条要同时出现持有人」（10-26，第4步换名以后跑）。

用法：python3 -I -X utf8 tools/add_need.py 名单.md [--apply]
名单是一份 .md，「## 名单」那一节底下的星名，顿号或者换行隔开；「## 持有人」那一节写能力行里找不到持有人的，一行一个「星名：持有人」。

为什么：打包时命星的触发是「星名或持有人」加这一段的时段钥匙，两个字的俗名（压火、同声、记路、分水）
在叙述里是寻常话，写到就叫醒那一颗星。条目设置里写了「X那一条要同时出现Y」的，打包脚本不拿星名当触发，
只认持有人（底卡第七歌赤足那一条就是这么写的），寻常话叫不醒它。

做法：在拼好的页里找命星那一节的条目设置，照旅伴条的能力行（能力：…【星名】…）找持有人，找不到的再看这颗星的
【调用】里点了哪个旅伴；在「星名加持有人的名字」后头（已有的几条后头）添「X那一条要同时出现Y」，Y 写持有人的名
（·前头那一截）。那一行在哪个源文件里就改哪个：月银纪、诸国期、萨尔维斯直接改页，分段写的找分段稿里一字一样的那一行。
不加 --apply 只报。改完照报告末尾的命令重拼。
"""
import re, sys, glob, os, collections

PAGES = sorted(glob.glob('月银纪史诗/第*歌_*.md')) + sorted(glob.glob('诸国期/诸国期时段_*.md')) + \
    sorted(glob.glob('萨尔维斯/萨尔维斯时段_*.md')) + sorted(glob.glob('纷争纪/纷争纪时段_*.md')) + \
    sorted(glob.glob('山铜纪/山铜纪时段_*.md')) + sorted(glob.glob('迷宫纪前传/迷宫纪前传时段_*.md'))
WHOLE = ('月银纪史诗/', '诸国期/', '萨尔维斯/')
STAR_HEAD = re.compile(r'^### (.+?) \((?:Special|Passive|Art|Ability) \| \w+\)\s*$')
COMP = re.compile(r'^## (?:旅途同行：(.+?)（|凡世至强：.+? · (.+?)（)')
SETTING_TAIL = re.compile(r'星名加持有人的名字((?:，[^，]+?那一条要同时出现[^，]+)*)')
CN = '一二三四五六七八九'


def parts_dir(page):
    m = re.match(r'纷争纪/纷争纪时段_(.)_', page)
    if m:
        n = CN.index(m.group(1)) + 1
        return '纷争纪/parts' if n == 1 else '纷争纪/parts%d' % n
    m = re.match(r'(山铜纪|迷宫纪前传)/\1时段_(.)_', page)
    if m:
        return '%s/parts%d' % (m.group(1), CN.index(m.group(2)) + 1)
    return None


def reassemble(page):
    m = re.match(r'纷争纪/纷争纪时段_(.)_', page)
    if m:
        return 'bash tools/assemble_strife.sh %d' % (CN.index(m.group(1)) + 1)
    m = re.match(r'山铜纪/山铜纪时段_(.)_', page)
    if m:
        return 'python3 -I -X utf8 tools/assemble_shantong_p%d.py .' % (CN.index(m.group(1)) + 1)
    m = re.match(r'迷宫纪前传/迷宫纪前传时段_(.)_', page)
    if m:
        n = CN.index(m.group(1)) + 1
        return 'python3 -I -X utf8 tools/assemble_maze_p1.py .' if n == 1 else 'python3 -I -X utf8 tools/assemble_maze.py . %d' % n
    return None


def read_list(path):
    text = open(path, encoding='utf-8').read()
    m = re.search(r'^## 名单\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    body = m.group(1) if m else text
    body = '\n'.join(l for l in body.split('\n') if not l.startswith('>'))
    names = [x.strip() for x in re.split(r'[、\n，,]', body) if x.strip() and not x.strip().startswith('#')]
    # 「## 持有人」那一节：能力行里找不到持有人的，一行一个「星名：持有人」
    over = {}
    m = re.search(r'^## 持有人\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    if m:
        for l in m.group(1).split('\n'):
            if '：' in l and not l.startswith('>'):
                a, b = l.split('：', 1)
                over[a.strip()] = b.strip()
    return names, over


def scan_page(page, names, over):
    lines = open(page, encoding='utf-8').read().split('\n')
    holder = collections.OrderedDict()
    comp = None
    for ln in lines:
        if ln.startswith('## 设计备注'):
            break
        m = COMP.match(ln)
        if m:
            comp = (m.group(1) or m.group(2)).strip()
        elif ln.startswith('## '):
            comp = None
        if comp and ln.startswith('能力：'):
            for s in re.findall(r'【([^】]+)】', ln):
                holder.setdefault(s, [])
                if comp not in holder[s]:
                    holder[s].append(comp)
    comps = [c for hs in holder.values() for c in hs]
    out = []                         # (设置行号, 星名, 持有人)
    stars, in_sec = [], False
    for no, ln in enumerate(lines):
        if ln.startswith('## 设计备注'):
            break
        if ln.startswith('## '):
            in_sec = ln.startswith('## 这一代的命星')
            stars = []
            continue
        if not in_sec:
            continue
        m = STAR_HEAD.match(ln)
        if m:
            stars.append([m.group(1).strip(), None])
            continue
        if ln.startswith('【调用】') and stars and stars[-1][1] is None:
            stars[-1][1] = ln
        if ln.startswith('> 条目设置：'):
            for name, call in stars:
                if name not in names:
                    continue
                hs = holder.get(name) or ([over[name]] if name in over else []) or \
                    [c for c in dict.fromkeys(comps) if call and c.split('·')[0] in call]
                out.append((no, name, hs[0].split('·')[0] if hs else None))
            stars, in_sec = [], False
    return lines, out


def main(argv):
    apply = '--apply' in argv
    args = [a for a in argv if a != '--apply']
    names, over = read_list(args[0])
    names = set(names)
    print('名单 %d 个' % len(names))
    found = collections.Counter()
    edits = collections.defaultdict(list)     # 源文件 → [(旧行, 新行)]
    redo, miss = [], []
    for page in PAGES:
        lines, hits = scan_page(page, names, over)
        if not hits:
            continue
        by_line = collections.defaultdict(list)
        for no, name, h in hits:
            found[name] += 1
            if not h:
                miss.append('%s【%s】找不到持有人' % (page, name)); continue
            by_line[no].append((name, h))
        for no, adds in by_line.items():
            old = lines[no]
            m = SETTING_TAIL.search(old)
            if not m:
                miss.append('%s:%d 条目设置里没有「星名加持有人的名字」：%s' % (page, no + 1, old[:50])); continue
            have = set(re.findall(r'，([^，]+?)那一条要同时出现', m.group(1)))
            add = ''.join('，%s那一条要同时出现%s' % (n, h) for n, h in adds if n not in have)
            if not add:
                continue
            new = old[:m.end()] + add + old[m.end():]
            if page.startswith(WHOLE):
                src = page
            else:
                pd = parts_dir(page)
                cands = [f for f in sorted(glob.glob(pd + '/*.md')) if old in open(f, encoding='utf-8').read().split('\n')]
                if len(cands) != 1:
                    miss.append('%s:%d 这一行在分段稿里找到 %d 处：%s' % (page, no + 1, len(cands), '、'.join(cands)))
                    continue
                src = cands[0]
                if reassemble(page) not in redo:
                    redo.append(reassemble(page))
            edits[src].append((old, new))
            print('%s ← %s' % (src, '、'.join('%s要%s' % (n, h) for n, h in adds if n not in have)))
    for n in sorted(names - set(found)):
        miss.append('名单里的「%s」哪一页的命星那一节里都没有（换名以前跑的？）' % n)
    for x in miss:
        print('  ' + x)
    if apply:
        for src, pairs in edits.items():
            t = open(src, encoding='utf-8').read()
            for old, new in pairs:
                if t.split('\n').count(old) != 1:
                    print('  %s 里这一行不止一处，没改：%s' % (src, old[:40])); continue
                t = t.replace(old, new, 1)
            open(src, 'w', encoding='utf-8').write(t)
    print('合计 改 %d 个文件，%d 颗星，找不到的 %d 处%s' % (len(edits), sum(found.values()), len(miss), '' if apply else '（只报，加 --apply 才写）'))
    if redo:
        print('重拼：')
        for c in redo:
            print('  ' + c)


if __name__ == '__main__':
    main(sys.argv[1:])
