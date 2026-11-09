# 照这一处在的年份，写条目设置里的年份黑名单（挡掉不在的那些年份的底座），再逐年试一遍
# 用法：python -I -X utf8 tools/yearbl.py 纪 起-止 [起-止 …]
#   纪：月银纪、纷争纪、山铜纪、前传（迷宫纪前传、迷宫纪也认）
#   起-止：这一处在（或者这一条要管）的年份，几段用空格隔开；只写一个数就是那一年；写 全纪 就是不挡，打印 无
#   纷争纪的 1 年写 1（叙述里叫元年，黑名单两样都挡）；山铜纪从 2 年起，947 年归寂月那一个月底座写迷宫纪元年，
#   窗口不含 947 的连迷宫纪元年一起挡；前传从迷宫纪 2 年到 1000 年
# 加 --test 文件.md：把文件里每一条 条目设置 的黑名单逐年试，列出挡下的年份段（看跟你写的窗口对不对得上）
import re
import sys

PRE = '(?:<br>|hud-meta">|纪元：)'
ERAS = {
    '月银纪': dict(lo=1, hi=99999, end=10081),
    '纷争纪': dict(lo=1, hi=99999, end=11034),
    '山铜纪': dict(lo=2, hi=947, end=947),
    '前传': dict(lo=2, hi=1000, end=1000),
}
ALIAS = {'迷宫纪前传': '前传', '迷宫纪': '前传'}


def _same_len(a, b):
    if a == b:
        return [a]
    i = 0
    while a[i] == b[i]:
        i += 1
    pre, a, b = a[:i], a[i:], b[i:]
    if len(a) == 1:
        return [pre + '[%s-%s]' % (a, b)]
    out, n = [], len(a) - 1
    lo_first = int(a[0]) if a[1:] == '0' * n else int(a[0]) + 1
    if a[1:] != '0' * n:
        out += [pre + x for x in _same_len(a, a[0] + '9' * n)]
    hi_first = int(b[0]) if b[1:] == '9' * n else int(b[0]) - 1
    if lo_first <= hi_first:
        out.append(pre + ('%d' % lo_first if lo_first == hi_first else '[%d-%d]' % (lo_first, hi_first)) + '\\d' * n)
    if b[1:] != '9' * n:
        out += [pre + x for x in _same_len(b[0] + '0' * n, b)]
    return out


def range_alts(lo, hi):
    out = []
    for n in range(len(str(lo)), len(str(hi)) + 1):
        a, b = max(lo, 10 ** (n - 1)), min(hi, 10 ** n - 1)
        if a <= b:
            out += _same_len(str(a), str(b))
    return out


def tidy(alts):
    # [1-9]、[1-9]\d、[1-9]\d\d 这一类收短一点，平台不在乎，人看着省事
    return ['\\d' if a == '[0-9]' else a for a in alts]


def complement(era, wins):
    e = ERAS[era]
    keep = set()
    for a, b in wins:
        keep.update(range(max(a, e['lo']), min(b, e['hi']) + 1))
    out, cur = [], None
    for y in range(e['lo'], e['hi'] + 1):
        if y in keep:
            if cur:
                out.append(tuple(cur))
                cur = None
        elif cur is None:
            cur = [y, y]
        else:
            cur[1] = y
    if cur:
        out.append(tuple(cur))
    return out


def blacklist(era, wins):
    era = ALIAS.get(era, era)
    comp = complement(era, wins)
    if not comp:
        return '无'
    alts = []
    for a, b in comp:
        alts += range_alts(a, b)
    alts = tidy(alts)
    if era == '月银纪':
        return '/%s月银纪(?:%s)年/' % (PRE, '|'.join(alts))
    if era == '纷争纪':
        if comp[0][0] == 1:
            alts = ['元'] + alts
        a = '|'.join(alts)
        return '/%s纷争纪(?:%s)年|开局时段：第二十二张｜年份：(?:%s)(?!\\d)/' % (PRE, a, a)
    if era == '山铜纪':
        a = '|'.join(alts)
        tail = '|迷宫纪元年' if comp[-1][1] == 947 else ''
        if tail:
            return '/%s(?:山铜纪(?:%s)年%s)|开局时段：无字碑｜年份：(?:%s)(?!\\d)/' % (PRE, a, tail, a)
        return '/%s山铜纪(?:%s)年|开局时段：无字碑｜年份：(?:%s)(?!\\d)/' % (PRE, a, a)
    a = '|'.join(alts)
    return '/%s迷宫纪(?:%s)年|开局时段：空白委托｜年份：(?:%s)(?!\\d)/' % (PRE, a, a)


def samples(era, y):
    era = ALIAS.get(era, era)
    if era == '月银纪':
        return ['纪元：月银纪%d年·秋' % y, '<br>月银纪%d年·秋' % y]
    if era == '纷争纪':
        s = ['纪元：纷争纪%d年·秋' % y, '开局时段：第二十二张｜年份：%d' % y]
        if y == 1:
            s += ['纪元：纷争纪元年·秋', '开局时段：第二十二张｜年份：元']
        return s
    if era == '山铜纪':
        s = ['纪元：山铜纪%d年·秋' % y, '开局时段：无字碑｜年份：%d' % y]
        if y == 947:
            s.append('纪元：迷宫纪元年·归寂月')
        return s
    return ['纪元：迷宫纪%d年·秋' % y, '开局时段：空白委托｜年份：%d' % y]


def blocked_years(era, rx):
    era = ALIAS.get(era, era)
    r = re.compile(rx)
    e = ERAS[era]
    hits = []
    for y in range(e['lo'], e['end'] + 1):
        ss = samples(era, y)
        m = [bool(r.search(s)) for s in ss]
        if any(m) and not all(m):
            raise SystemExit('%s %d 年几种写法一挡一不挡：%s' % (era, y, list(zip(ss, m))))
        if all(m):
            hits.append(y)
    return hits


def spans(ys):
    out = []
    for y in ys:
        if out and y == out[-1][1] + 1:
            out[-1][1] = y
        else:
            out.append([y, y])
    return '、'.join('%d' % a if a == b else '%d到%d' % (a, b) for a, b in out) or '（一年也不挡）'


def parse_wins(args):
    wins = []
    for a in args:
        if a == '全纪':
            continue
        m = re.fullmatch(r'(\d+)(?:-(\d+))?', a)
        if not m:
            raise SystemExit('看不懂的年份：%s' % a)
        lo = int(m.group(1))
        hi = int(m.group(2) or lo)
        if hi < lo:
            raise SystemExit('起比止大：%s' % a)
        wins.append((lo, hi))
    return wins


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__ or open(__file__, encoding='utf-8').read().split('\nimport')[0])
        return
    if args[0] == '--test':
        for f in args[1:]:
            era_of = {'月银纪': '月银纪', '纷争纪': '纷争纪', '山铜纪': '山铜纪', '迷宫纪': '前传'}
            for line in open(f, encoding='utf-8'):
                m = re.search(r'条目设置：文件夹 \d+·(\S+?)｜', line)
                if not m:
                    continue
                era = era_of.get(m.group(1))
                bl = re.search(r'黑名单 `/(.+?)/`', line)
                if not era:
                    continue
                if not bl:
                    print('%s｜不挡' % m.group(1))
                    continue
                print('%s｜挡 %s' % (era, spans(blocked_years(era, bl.group(1)))))
        return
    era = ALIAS.get(args[0], args[0])
    if era not in ERAS:
        raise SystemExit('纪写 月银纪、纷争纪、山铜纪、前传')
    if '全纪' in args[1:] or len(args) == 1:
        print('黑名单 无')
        return
    wins = parse_wins(args[1:])
    bl = blacklist(era, wins)
    if bl == '无':
        print('黑名单 无')
        return
    body = bl[1:-1]
    hit = blocked_years(era, body)
    want = [y for y in range(ERAS[era]['lo'], ERAS[era]['end'] + 1) if not any(a <= y <= b for a, b in wins)]
    if hit != want:
        raise SystemExit('生成的黑名单挡的年份对不上，别用：多挡 %s 漏挡 %s' % (
            spans(sorted(set(hit) - set(want))), spans(sorted(set(want) - set(hit)))))
    print('黑名单 `%s`' % bl)
    print('（挡：%s）' % spans(hit))


if __name__ == '__main__':
    main()
