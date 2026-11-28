#!/usr/bin/env python3
"""宝物志进源稿（11-28）。照 底稿/真龙/tools/place_zhenlong.py：源稿在 底稿/宝物志/稿/*.md，改字改那里，
这一支照纪拼成各纪补卷里的生成文件，规则那几条（奥尔德兰·规则｜宝物·…）拼成 通用条目/宝物志_规则.md。
make_dlc.py 照文件夹号 65 和规则标题切成「宝物志」那一包。

  python -I -X utf8 底稿/宝物志/tools/place_baowu.py            只报
  python -I -X utf8 底稿/宝物志/tools/place_baowu.py --apply    写盘（先删上一回生成的）
"""
import collections, glob, io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SRC = os.path.join(ROOT, '底稿', '宝物志')
NUM, FOLDER = '65', '宝物志'
RULE_FOLDER = '10·货币、装备与制作'
OUT = collections.OrderedDict([
    ('月银纪', (os.path.join(ROOT, '月银纪补卷'), '宝物志.md', None)),
    ('纷争纪', (os.path.join(ROOT, '纷争纪', '补卷'), '补卷_111_宝物志.md', '补卷_111_')),
    ('山铜纪', (os.path.join(ROOT, '山铜纪', '补卷'), '补卷_78_宝物志.md', '补卷_78_')),
    ('迷宫纪', (os.path.join(ROOT, '迷宫纪前传', '补卷'), '补卷_94_宝物志.md', '补卷_94_')),
    ('奥尔德兰', (os.path.join(ROOT, '通用条目'), '宝物志_规则.md', None)),
])
HEAD = '''# %s｜DLC·宝物志

> 这一节是说明，不进卡。这一份是 `底稿/宝物志/tools/place_baowu.py` 从 `底稿/宝物志/稿/` 拼出来的，别直接改这里，改那边的源稿再重跑。文件夹 65（规则那几条挂 10·货币、装备与制作，照标题切包）。
'''
TITLE = re.compile(r'^## ((月银纪|纷争纪|山铜纪|迷宫纪|奥尔德兰)·.+)$')


def entries(path):
    lines = open(path, encoding='utf-8').read().replace('\r', '').split('\n')
    out, cur = [], None
    for ln in lines:
        if ln.startswith('## 设计备注'):
            break
        m = TITLE.match(ln)
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


def main():
    apply = '--apply' in sys.argv
    bad = 0
    seen = {}
    groups = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(SRC, '稿', '*.md'))):
        for e in entries(f):
            sets = [l for l in e['lines'] if l.startswith('> 条目设置：')]
            if len(sets) != 1:
                bad += 1; print('错｜%s｜%s 条目设置 %d 行' % (e['src'], e['title'], len(sets))); continue
            if e['era'] == '奥尔德兰':
                if not e['title'].startswith('奥尔德兰·规则｜宝物·'):
                    bad += 1; print('错｜%s｜%s 规则标题该是「奥尔德兰·规则｜宝物·…」' % (e['src'], e['title']))
                if RULE_FOLDER not in sets[0]:
                    bad += 1; print('错｜%s｜%s 规则的文件夹该是 %s' % (e['src'], e['title'], RULE_FOLDER))
            else:
                m = re.search(r'文件夹 (\d\d)·(月银纪|纷争纪|山铜纪|迷宫纪)｜([^，]+)，', sets[0])
                if not m or m.group(1) != NUM or m.group(3) != FOLDER:
                    bad += 1; print('错｜%s｜%s 文件夹该是 65·%s｜宝物志：%s' % (e['src'], e['title'], e['era'], sets[0][6:40])); continue
                if m.group(2) != e['era']:
                    bad += 1; print('错｜%s｜%s 文件夹的纪跟标题对不上' % (e['src'], e['title']))
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
    print('宝物志 %d 条，格式问题 %d 处' % (total, bad))
    print('  ' + '，'.join('%s %d' % (era, len(groups.get(era, []))) for era in OUT))
    print('  汉字约 %d' % sum(len(re.findall(r'[一-鿿]', '\n'.join(e['lines']))) for v in groups.values() for e in v))
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
        txt = HEAD % ('通用条目' if era == '奥尔德兰' else era + '世界书补卷')
        for e in es:
            txt += '\n' + '\n'.join(e['lines']).rstrip('\n') + '\n'
        p = os.path.join(d, name)
        open(p, 'w', encoding='utf-8', newline='\n').write(txt)
        print('写 %s（%d 条）' % (os.path.relpath(p, ROOT).replace('\\', '/'), len(es)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
