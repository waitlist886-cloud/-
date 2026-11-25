#!/usr/bin/env python3
"""真龙志进源稿（11-25）。做法照 底稿/DLC/tools/place_xinliao.py：真龙志的源稿在 底稿/真龙/稿/Z*.md，改字改那里；
这一支把它们照纪拼成各纪补卷里的生成文件，build_v12 的补卷 glob 就收得到，make_dlc.py 再照文件夹号 64 切成「真龙志」那一包。

  python -I -X utf8 底稿/真龙/tools/place_zhenlong.py            只报：几条、各纪几条、重名、格式不对的、分份表里的标题缺哪几条
  python -I -X utf8 底稿/真龙/tools/place_zhenlong.py --apply    写盘（先删掉上一回生成的，再写）
  python -I -X utf8 底稿/真龙/tools/place_zhenlong.py --sample   拿 样稿.md 当源试一遍（稿子还没交的时候看脚本通不通），不许跟 --apply 一起用

源：底稿/真龙/稿/Z*.md（八份，样稿那五条由各份抄进去，样稿.md 本身不收）。
出：月银纪补卷/真龙志.md，纷争纪/补卷/补卷_110_真龙志.md，山铜纪/补卷/补卷_76_真龙志.md，迷宫纪前传/补卷/补卷_93_真龙志.md
（前传和 1001 年的条都放前传补卷，1001 年的条自己带着年份正则当门控）。
号是 11-25 看过没被占才定的；写盘的时候那个号要是叫别的文件占了（同号不同名），停下不写。
"""
import collections, glob, io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SRC = os.path.join(ROOT, '底稿', '真龙')
NUM, PACK, FOLDER = '64', '真龙志', '真龙志'
OUT = collections.OrderedDict([
    ('月银纪', (os.path.join(ROOT, '月银纪补卷'), '真龙志.md', None)),
    ('纷争纪', (os.path.join(ROOT, '纷争纪', '补卷'), '补卷_110_真龙志.md', '补卷_110_')),
    ('山铜纪', (os.path.join(ROOT, '山铜纪', '补卷'), '补卷_76_真龙志.md', '补卷_76_')),
    ('迷宫纪', (os.path.join(ROOT, '迷宫纪前传', '补卷'), '补卷_93_真龙志.md', '补卷_93_')),
])
HEAD = '''# %s世界书补卷｜DLC·真龙志

> 这一节是说明，不进卡。这一份是 `底稿/真龙/tools/place_zhenlong.py` 从 `底稿/真龙/稿/` 下八份拼出来的，别直接改这里，改那边的源稿再重跑。文件夹 64·%s｜真龙志，打卡以后由 `底稿/DLC/tools/make_dlc.py` 切进「真龙志」那一包。定数在 `底稿/真龙/定数.md`。
'''


def sources(sample):
    if sample:
        return [os.path.join(SRC, '样稿.md')]
    return sorted(glob.glob(os.path.join(SRC, '稿', 'Z*.md')))


def entries(path):
    lines = open(path, encoding='utf-8').read().replace('\r', '').split('\n')
    out, cur = [], None
    for ln in lines:
        if ln.startswith('## 设计备注'):
            break
        m = re.match(r'^## ((月银纪|纷争纪|山铜纪|迷宫纪)·.+)$', ln)
        if m:
            if cur:
                out.append(cur)
            cur = {'title': m.group(1).strip(), 'era': m.group(2), 'lines': [ln], 'src': os.path.relpath(path, ROOT).replace('\\', '/')}
            continue
        if ln.startswith('## ') or ln.startswith('# '):
            if cur:
                out.append(cur)
            cur = None
            continue
        if cur is not None:
            cur['lines'].append(ln)
    if cur:
        out.append(cur)
    return out


def planned_titles():
    """分份.md 各表头一栏里的标题，拿来对有没有缺条、有没有改了标题。"""
    p = os.path.join(SRC, '分份.md')
    if not os.path.isfile(p):
        return []
    ts = []
    for ln in open(p, encoding='utf-8').read().replace('\r', '').split('\n'):
        m = re.match(r'^\| ((?:月银纪|纷争纪|山铜纪|迷宫纪)·真龙｜[^|]+?) \|', ln)
        if m:
            ts.append(m.group(1).strip())
    return ts


def main():
    apply = '--apply' in sys.argv
    sample = '--sample' in sys.argv
    if apply and sample:
        print('--sample 只试不写'); return 1
    bad = 0
    seen = {}
    groups = collections.defaultdict(list)
    srcs = sources(sample)
    if not srcs:
        print('底稿/真龙/稿/ 下还没有 Z*.md'); return 1
    for f in srcs:
        for e in entries(f):
            sets = [l for l in e['lines'] if l.startswith('> 条目设置：')]
            if len(sets) != 1:
                bad += 1; print('错｜%s｜%s 条目设置 %d 行' % (e['src'], e['title'], len(sets))); continue
            m = re.search(r'文件夹 (\d\d)·(月银纪|纷争纪|山铜纪|迷宫纪)｜([^，]+)，', sets[0])
            if not m or m.group(1) != NUM:
                bad += 1; print('错｜%s｜%s 文件夹不是 64：%s' % (e['src'], e['title'], sets[0][6:40])); continue
            if m.group(2) != e['era']:
                bad += 1; print('错｜%s｜%s 文件夹的纪跟标题对不上' % (e['src'], e['title']))
            if m.group(3) != FOLDER:
                bad += 1; print('错｜%s｜%s 文件夹名该是 64·%s｜真龙志，写的是 %s' % (e['src'], e['title'], e['era'], m.group(3)))
            if not re.match(r'^(?:月银纪|纷争纪|山铜纪|迷宫纪)·真龙｜', e['title']):
                bad += 1; print('错｜%s｜%s 标题不是「X纪·真龙｜…」' % (e['src'], e['title']))
            if e['title'] in seen:
                bad += 1; print('错｜重名｜%s（%s 和 %s）' % (e['title'], seen[e['title']], e['src']))
            seen[e['title']] = e['src']
            i = e['lines'].index(sets[0])
            tail = [l for l in e['lines'][i + 1:] if l.strip() and l.strip() != '---']
            if tail:
                bad += 1; print('错｜%s｜%s 条目设置后头还有字：%s' % (e['src'], e['title'], tail[0][:30]))
            e['lines'] = e['lines'][:i + 1]
            groups[e['era']].append(e)
    total = sum(len(v) for v in groups.values())
    print('真龙志 %d 条，格式问题 %d 处' % (total, bad))
    print('  ' + '，'.join('%s %d' % (era, len(groups.get(era, []))) for era in OUT))
    chars = sum(len(re.findall(r'[一-鿿]', '\n'.join(e['lines']))) for v in groups.values() for e in v)
    print('  汉字约 %d' % chars)
    plan = planned_titles()
    if plan and not sample:
        miss = [t for t in plan if t not in seen]
        extra = [t for t in seen if t not in plan]
        print('  分份表 %d 条，缺 %d 条，表外 %d 条' % (len(plan), len(miss), len(extra)))
        for t in miss:
            print('    缺｜' + t)
        for t in extra:
            print('    表外｜%s（%s）' % (t, seen[t]))
        if miss or extra:
            bad += 1
    if not apply:
        return 1 if bad else 0
    if bad:
        print('有问题，没写盘'); return 1
    for era, (d, name, prefix) in OUT.items():
        if prefix:
            clash = [f for f in os.listdir(d) if f.startswith(prefix) and f != name]
            if clash:
                print('号叫占了，没写盘：%s 下已经有 %s' % (os.path.relpath(d, ROOT).replace('\\', '/'), clash[0])); return 1
    for era, (d, name, prefix) in OUT.items():
        p = os.path.join(d, name)
        if os.path.isfile(p):
            os.remove(p)
    for era, es in groups.items():
        d, name, prefix = OUT[era]
        txt = HEAD % (era, era)
        for e in es:
            txt += '\n' + '\n'.join(e['lines']).rstrip('\n') + '\n'
        p = os.path.join(d, name)
        open(p, 'w', encoding='utf-8', newline='\n').write(txt)
        print('写 %s（%d 条）' % (os.path.relpath(p, ROOT).replace('\\', '/'), len(es)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
