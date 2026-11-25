#!/usr/bin/env python3
"""DLC 新料：同一纪里几条共用的触发词（11-24）。一句话把东陆、西陆两条一起拉醒，是白醒。
把各条条目设置里触发正则的顶层分支拆开，同一纪里出现在两条以上的分支列出来。

  python -I -X utf8 底稿/DLC/tools/trig_overlap.py [目录或文件…]     默认扫 底稿/DLC/新料/ 下三包
只报，不改。年份窗不重叠的两条（同一国前后两窗）共用触发词是对的，报出来自己判。
"""
import collections, glob, io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SRC = os.path.join(ROOT, '底稿', 'DLC', '新料')


def split_top(rx):
    out, depth, cur, esc, cls = [], 0, '', False, False
    for ch in rx:
        if esc:
            cur += ch; esc = False; continue
        if ch == '\\':
            cur += ch; esc = True; continue
        if cls:
            cur += ch
            if ch == ']':
                cls = False
            continue
        if ch == '[':
            cls = True; cur += ch; continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == '|' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return [x for x in out if x]


def entries(path):
    s = open(path, encoding='utf-8').read().replace('\r', '')
    s = s.split('\n## 设计备注')[0]
    for m in re.finditer(r'(?m)^## ((月银纪|纷争纪|山铜纪|迷宫纪)·[^\n]+)\n(.*?)^> 条目设置：([^\n]+)$', s, re.S):
        title, era, line = m.group(1).strip(), m.group(2), m.group(4)
        rxs = re.findall(r'`/(.+?)/`', line.split('黑名单')[0])
        gate = [r for r in rxs if r.startswith('(?:<br>')]
        words = [r for r in rxs if not r.startswith('(?:<br>')]
        is1001 = any('100[1-9]' in g for g in gate)
        key = era + ('1001' if is1001 else ('前传' if '迷宫纪前传' in line else ''))
        toks = set()
        for w in words:
            toks.update(split_top(w))
        yield key, title, toks, os.path.basename(path)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    files = []
    if args:
        for a in args:
            files += sorted(glob.glob(os.path.join(a, '*.md'))) if os.path.isdir(a) else [a]
    else:
        files = [os.path.join(SRC, '样稿三条.md'), os.path.join(SRC, '第一拨.md')]
        for sub in ('律法志', '风物志', '谱系志'):
            files += sorted(glob.glob(os.path.join(SRC, sub, '[LFGC]*.md')))
    skip = {'迷宫纪·风物｜书写与衣食·西陆', '迷宫纪·风物｜书写与衣食·东陆', '迷宫纪·风物｜书写与衣食·阿卡迪亚'}
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    n = 0
    for f in files:
        if not os.path.isfile(f):
            continue
        for key, title, toks, fn in entries(f):
            if title in skip:
                continue
            n += 1
            for t in toks:
                by[key][t].append(title)
    tot = 0
    for key in sorted(by):
        rows = [(t, ts) for t, ts in by[key].items() if len(set(ts)) >= 2]
        if not rows:
            continue
        print('== %s：%d 个共用的分支' % (key, len(rows)))
        for t, ts in sorted(rows, key=lambda r: -len(r[1])):
            tot += 1
            print('  %s  ←  %s' % (t, '；'.join(sorted(set(x.split('·', 1)[1] for x in ts)))))
    print('扫了 %d 条，同纪共用的触发分支 %d 个' % (n, tot))


if __name__ == '__main__':
    main()
