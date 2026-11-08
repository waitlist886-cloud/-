# 山铜纪与迷宫纪合篇（11-08 照倾向写入）：支线七十条、委托二十三张添题那一行，名单是子任务起的 底稿/旅印合篇/支线委托题名.tsv。
# 支线：【调用】那一段底下空一行写题（照主线的位置，没有章那一行）。委托：单头那一条底下添一条「- 题：【…】名称」，委托第一版和各页 p0_head 里那一份都添。
# 用法：python -I -X utf8 底稿/旅印合篇/插支线委托题.py . [--apply]   已经有题的跳过；改完重拼前传各页。
import csv, glob, os, re, sys

ROOT = sys.argv[1]
APPLY = '--apply' in sys.argv
rows = list(csv.reader(open(os.path.join(ROOT, '底稿', '旅印合篇', '支线委托题名.tsv'), encoding='utf-8'), delimiter='\t'))
head, rows = rows[0], [r for r in rows[1:] if len(r) >= 3 and r[0].strip()]
print('名单', len(rows), '行')
changed = {}


def text(p):
    return changed.get(p) or open(p, encoding='utf-8').read()


def put_sideline(p, title, line):
    L = text(p).split('\n')
    i = next((k for k, l in enumerate(L) if l.strip() == '## ' + title), None)
    if i is None:
        return '没找到条目'
    end = next((k for k in range(i + 1, len(L)) if L[k].startswith('## ')), len(L))
    if any(L[k].startswith('题：') for k in range(i + 1, end)):
        return '已有题'
    j = next((k for k in range(i + 1, end) if L[k].startswith('【调用】')), None)
    if j is None:
        return '没有【调用】'
    if j + 1 < len(L) and L[j + 1].strip() == '':
        L[j + 2:j + 2] = [line, '']
    else:
        L[j + 1:j + 1] = ['', line, '']
    changed[p] = '\n'.join(L)
    return 'ok'


def put_commission(p, title, line):
    L = text(p).split('\n')
    i = next((k for k, l in enumerate(L) if l.strip() == '## ' + title), None)
    if i is None:
        return '没找到条目'
    end = next((k for k in range(i + 1, len(L)) if L[k].startswith('## ')), len(L))
    if any(L[k].startswith('- 题：') for k in range(i + 1, end)):
        return '已有题'
    j = next((k for k in range(i + 1, end) if L[k].startswith('- 单头：')), None)
    if j is None:
        return '没有单头'
    L[j + 1:j + 1] = ['- ' + line]
    changed[p] = '\n'.join(L)
    return 'ok'


bad = []
for r in rows:
    f, title, line = r[0].strip(), r[1].strip(), r[2].strip()
    assert line.startswith('题：'), line
    p = os.path.join(ROOT, f)
    if '委托' in title.split('｜', 1)[0]:
        res = put_commission(p, title, line)
        if res != 'ok':
            bad.append((f, title, res))
        for q in sorted(glob.glob(os.path.join(ROOT, '迷宫纪前传', 'parts*', 'p0_head.md'))):
            if ('## ' + title) in text(q):
                res2 = put_commission(q, title, line)
                if res2 not in ('ok',):
                    bad.append((q, title, res2))
    else:
        res = put_sideline(p, title, line)
        if res != 'ok':
            bad.append((f, title, res))
print('没添上的', bad)
if APPLY:
    for p, s in changed.items():
        open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('改了的文件', len(changed), '（' + ('写了' if APPLY else '没写，加 --apply') + '）')
