"""命星换名（10-25，照 底卡洗稿与命名重审_方向稿_第三版.md 第五节第4步）。

用法：
  python3 -I -X utf8 tools/rename_stars.py --map 表1.md --map 表2.md ... [--report 报告.md]
  python3 -I -X utf8 tools/rename_stars.py --map ... --apply [--only-bracket 名1、名2] [--extra 文件 ...]
  python3 -I -X utf8 tools/rename_stars.py --map ... --preview 目录   换过的文件照原路径写进目录，拿 diff 看
  python3 -I -X utf8 tools/rename_stars.py --map ... --leftover 拼好的页.md ...

对照表照 tools/namelint.py 的读法，表头里有「现名」「改成」两栏，改成写「不动」就是不改。

不加 --apply 只报：每个旧名在哪些文件、什么位置各出现几回（星标题、【】、条目设置、正文、设计备注），
两三个字的旧名在正文里出现的原句列出来，看是不是当寻常话用的，要的话放进 --only-bracket。

加 --apply 照表改文件：
  改现行的源稿：月银纪十五歌、诸国期六页、萨尔维斯六页（整页），纷争纪、山铜纪、前传的分段稿（改完照各页的拼法重拼），
  各纪的补卷、碑、委托、二十二张、三批旧条目，Art传承表_定稿.md、纷争纪总表，--extra 给的文件（进卡脚本的星名表）。
  记录、方向稿、底稿、旧版、说明、CLAUDE.md 不在里头，旧名留着。
  设计备注里写着改名经过的那一行（有改成、改名、旧名、原名、改叫、换成、→、作废 的）不改，别的照改。
  --only-bracket 列的名字只改星标题、【】、条目设置里的，正文和备注里当寻常话用的不动。
  天赋、被动、技艺那一行名字长了、冒号标签过八个字的，冒号换成｜。
  进过卡的纪（月银纪、诸国期、萨尔维斯、纷争纪、山铜纪），条目设置里反引号围起来的触发正则，旧名换成 (?:新名|旧名)，
  v9 里玩过的局提旧名还醒得过来；前传没进过卡，旧名不留。命星那一节「星名加持有人的名字」是打包脚本拼的，
  旧名要在打包脚本里照对照表补（v10 的 STAR_OLD_NAMES），这个脚本不管。
  一遍换，换上去的新名字不会再被别的旧名换一回；没改名的星名也放进去占位，长的先认，短旧名不会咬进长名字里。
改完把要重拼的页列出来。

--leftover 查拼好的页里还剩哪些旧名（改名经过的行、--only-bracket 的正文不算）。
"""
import re, sys, glob, os, json, collections, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('namelint', os.path.join(HERE, 'namelint.py'))
namelint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(namelint)

SOURCES = [
    '月银纪史诗/第*歌_*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md',
    '纷争纪/parts/*.md', '纷争纪/parts[2-7]/*.md',
    '山铜纪/parts[1-6]/*.md', '迷宫纪前传/parts[1-5]/*.md',
    '月银纪补卷/*.md', '萨尔维斯/补卷/帝国史_*.md', '萨尔维斯/补卷/月银纪_*.md',
    '纷争纪/补卷/补卷_*.md', '山铜纪/补卷/第一项_*.md', '山铜纪/补卷/补卷_*.md', '迷宫纪前传/补卷/第一项_*.md',
    '山铜纪/山铜纪_碑_第一版.md', '迷宫纪前传/迷宫纪前传_委托_第一版.md', '纷争纪/天黑以后_二十二张_第六版.md',
    'moon/batch1/*.md', 'moon/batch2/*.md', 'moon/batch3/*.md',
    'Art传承表_定稿.md', '纷争纪/纷争纪_旅伴与传奇总表.md', '迷宫纪前传/起名簿.md',
]
# 进过卡的纪（v9 以前），条目设置的触发正则里旧名留着并列，写成 (?:新名|旧名)
IN_CARD = ('月银纪史诗/', '诸国期/', '萨尔维斯/', '纷争纪/', '山铜纪/', '月银纪补卷/', 'moon/')
ASSEMBLED = ['纷争纪/纷争纪时段_*.md', '山铜纪/山铜纪时段_*.md', '迷宫纪前传/迷宫纪前传时段_*.md']
HEAD = re.compile(r'^### (.+?) \((Art|Special|Passive|Active|Ability)\s*\|\s*(\w+)\)\s*$')
NOTE_HEAD = re.compile(r'^(#{1,3}) .*(设计备注|不进卡)')
ANY_HEAD = re.compile(r'^(#{1,3}) ')
HIST = re.compile(r'改成|改名|旧名|原名|原叫|改叫|换成|→|作废|先起的|原先|原来叫')
ABIL = re.compile(r'^- (天赋|被动|技艺|主动)【([^】]+)】：')
HAN = re.compile(r'[一-鿿]')


def hanlen(s):
    return len(HAN.findall(s))


def files_of(patterns):
    out = []
    for p in patterns:
        out += sorted(glob.glob(p))
    return [f for f in out if 'backup' not in f]


def all_star_names():
    names = set()
    for f in files_of(namelint.PAGES):
        for ln in open(f, encoding='utf-8'):
            m = HEAD.match(ln.rstrip('\n'))
            if m:
                names.add(m.group(1))
    names |= namelint.base_star_names('.')
    return names


def build_rx(mapping, keep):
    pool = dict((k, k) for k in keep)
    pool.update(mapping)
    keys = sorted(pool, key=len, reverse=True)
    return re.compile('|'.join(re.escape(k) for k in keys)), pool


def note_flags(lines):
    """每一行在不在设计备注、不进卡那一节里。"""
    flags, level = [], None
    for ln in lines:
        m = ANY_HEAD.match(ln)
        if m:
            lv = len(m.group(1))
            if NOTE_HEAD.match(ln):
                if level is None or lv <= level:
                    level = lv
            elif level is not None and lv <= level:
                level = None
        flags.append(level is not None)
    return flags


def scan_file(path, rx, pool, mapping, only_bracket, apply=False, preview=None):
    text = open(path, encoding='utf-8').read()
    lines = text.split('\n')
    notes = note_flags(lines) if path.endswith('.md') else [False] * len(lines)
    in_card = path.startswith(IN_CARD)
    hits = []          # (old, ctx, lineno, line, replaced?)
    out_lines, colon_fix, colon_bad = [], [], []
    for no, ln in enumerate(lines):
        is_head = bool(HEAD.match(ln))
        is_set = ln.startswith('> 条目设置')
        hist = notes[no] and bool(HIST.search(ln))
        changed = False

        def sub(m):
            nonlocal changed
            old = m.group(0)
            new = pool[old]
            if old not in mapping or mapping[old] == old:
                return old
            a, b = m.start(), m.end()
            if is_head:
                ctx = '标题'
            elif a > 0 and ln[a - 1] == '【' and b < len(ln) and ln[b] == '】':
                ctx = '【】'
            elif is_set:
                ctx = '条目设置'
            elif notes[no]:
                ctx = '备注'
            else:
                ctx = '正文'
            do = True
            if hist:
                do = False
                ctx += '·改名经过'
            elif old in only_bracket and ctx in ('正文', '备注'):
                do = False
                ctx += '·当寻常话'
            hits.append((old, ctx, no + 1, ln, do))
            if do:
                changed = True
                if ctx == '条目设置' and in_card and ln[:a].count('`') % 2 == 1:
                    return '(?:%s|%s)' % (new, old)
                return new
            return old

        new_ln = rx.sub(sub, ln)
        if changed:
            m = ABIL.match(new_ln)
            if m and hanlen(m.group(1)) + hanlen(m.group(2)) + 2 > 8:
                rest = new_ln[m.end():]
                if '：' in rest or ':' in rest:
                    colon_bad.append((no + 1, new_ln))
                else:
                    new_ln = new_ln[:m.end() - 1] + '｜' + rest
                    colon_fix.append((no + 1, new_ln))
        out_lines.append(new_ln)
    new_text = '\n'.join(out_lines)
    if apply and new_text != text:
        open(path, 'w', encoding='utf-8').write(new_text)
    if preview and new_text != text:
        dst = os.path.join(preview, path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'w', encoding='utf-8').write(new_text)
    return hits, colon_fix, colon_bad, new_text != text


def page_of(path):
    m = re.match(r'纷争纪/parts(\d?)/', path)
    if m:
        return ('纷争纪', int(m.group(1) or 1))
    m = re.match(r'山铜纪/parts(\d)/', path)
    if m:
        return ('山铜纪', int(m.group(1)))
    m = re.match(r'迷宫纪前传/parts(\d)/', path)
    if m:
        return ('前传', int(m.group(1)))
    return None


def reassemble_cmd(era, n):
    if era == '纷争纪':
        return 'bash tools/assemble_strife.sh %d' % n
    if era == '山铜纪':
        return 'python3 -I -X utf8 tools/assemble_shantong_p%d.py .' % n
    if n == 1:
        return 'python3 -I -X utf8 tools/assemble_maze_p1.py .'
    return 'python3 -I -X utf8 tools/assemble_maze.py . %d' % n


def main(argv):
    maps, extra, only_bracket, report, leftover, preview = [], [], set(), None, [], None
    apply = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--map':
            maps.append(argv[i + 1]); i += 2
        elif a == '--extra':
            extra.append(argv[i + 1]); i += 2
        elif a == '--only-bracket':
            only_bracket |= set(x for x in re.split(r'[、,，]', argv[i + 1]) if x); i += 2
        elif a == '--report':
            report = argv[i + 1]; i += 2
        elif a == '--preview':
            preview = argv[i + 1]; i += 2
        elif a == '--apply':
            apply = True; i += 1
        elif a == '--leftover':
            leftover = argv[i + 1:]; break
        else:
            print('认不出的参数：' + a); return 2
    mapping, clash = namelint.read_maps(maps)
    if clash:
        for old, x, y, pa, pb in clash:
            print('对照表前后不一：%s 在 %s 改 %s，在 %s 改 %s' % (old, os.path.basename(pa), x, os.path.basename(pb), y))
        return 2
    mapping = {k: v for k, v in mapping.items() if k != v}
    keep = all_star_names()
    rx, pool = build_rx(mapping, keep)
    print('改名 %d 颗，占位的星名 %d 个' % (len(mapping), len(keep)))

    if leftover:
        left = 0
        for f in leftover:
            hits, _, _, _ = scan_file(f, rx, pool, mapping, only_bracket, apply=False)
            for old, ctx, no, ln, do in hits:
                if do:
                    left += 1
                    print('%s:%d 还剩 %s（%s）：%s' % (f, no, old, ctx, ln[:60]))
        print('合计 还剩 %d' % left)
        return 0

    files = files_of(SOURCES) + extra
    per = collections.defaultdict(collections.Counter)
    where = collections.defaultdict(set)
    plain_lines = collections.defaultdict(list)
    changed_files, fixes, bads = [], [], []
    for f in files:
        hits, cf, cb, changed = scan_file(f, rx, pool, mapping, only_bracket, apply=apply, preview=preview)
        for old, ctx, no, ln, do in hits:
            per[old][ctx] += 1
            where[old].add(f)
            if ctx.startswith('正文') and hanlen(old) <= 3:
                plain_lines[old].append('%s:%d %s' % (f, no, ln.strip()[:70]))
        fixes += [(f, n, l) for n, l in cf]
        bads += [(f, n, l) for n, l in cb]
        if changed:
            changed_files.append(f)

    out = []
    out.append('# 换名%s（%d 颗）\n' % ('' if apply else '预演', len(mapping)))
    missing = sorted(k for k in mapping if k not in per)
    out.append('| 旧名 | 新名 | 标题 | 【】 | 条目设置 | 正文 | 备注 | 不改的 | 文件数 |')
    out.append('|---|---|---|---|---|---|---|---|---|')
    for old in sorted(mapping, key=lambda k: -sum(per[k].values())):
        c = per[old]
        skip = sum(v for k, v in c.items() if '·' in k)
        out.append('| %s | %s | %d | %d | %d | %d | %d | %d | %d |' % (
            old, mapping[old], c['标题'], c['【】'], c['条目设置'], c['正文'], c['备注'], skip, len(where[old])))
    if missing:
        out.append('\n源稿里一处也没找到的旧名：' + '、'.join(missing))
    no_head = sorted(k for k in mapping if k in per and per[k]['标题'] == 0)
    if no_head:
        out.append('\n源稿里没有星标题的旧名（只在别处提到，看一眼是不是表写错了）：' + '、'.join(no_head))
    if plain_lines:
        out.append('\n## 两三个字的旧名在正文里的原句\n')
        out.append('当寻常话用的，把名字放进 --only-bracket。')
        for old in sorted(plain_lines):
            out.append('\n### %s → %s（%d 处）\n' % (old, mapping[old], len(plain_lines[old])))
            out += ['- ' + x for x in plain_lines[old][:12]]
            if len(plain_lines[old]) > 12:
                out.append('- ……')
    if fixes:
        out.append('\n## 冒号换成｜的行（%d）\n' % len(fixes))
        out += ['- %s:%d %s' % (f, n, l[:60]) for f, n, l in fixes]
    if bads:
        out.append('\n## 冒号标签过长、行里还有别的冒号，要手改（%d）\n' % len(bads))
        out += ['- %s:%d %s' % (f, n, l[:60]) for f, n, l in bads]
    pages = sorted(set(p for p in (page_of(f) for f in changed_files) if p))
    out.append('\n## %s的文件（%d）\n' % ('改了' if apply else '会改', len(changed_files)))
    out += ['- ' + f for f in changed_files]
    if pages:
        out.append('\n## 要重拼的页\n')
        out += ['- `%s`' % reassemble_cmd(e, n) for e, n in pages]
    text = '\n'.join(out) + '\n'
    if report:
        open(report, 'w', encoding='utf-8').write(text)
        print('报告写到 ' + report)
    else:
        print(text)
    print('旧名 %d，找到的 %d，冒号换｜ %d，要手改 %d，%s文件 %d，要重拼 %d 页' % (
        len(mapping), len(per), len(fixes), len(bads), '改了' if apply else '会改', len(changed_files), len(pages)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
