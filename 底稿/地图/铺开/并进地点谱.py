# 把一纪各份的份表并进地点谱：python -I -X utf8 底稿/地图/铺开/并进地点谱.py 纪 份表.tsv [份表.tsv …] [--apply]
#   纪：月银纪、纷争纪、山铜纪、迷宫纪前传（地点谱 底稿/地图/地点谱/<纪>.tsv）
#   份表的前十一栏跟地点谱一样，另有 在的年份、条目 两栏（计划第六节）。
#   地点谱里有这个名字的行：出处添上条目标题（已有就不添），坐标变了的照份表改，要说明的末尾记原来的坐标；
#   没有的：照份表的前十一栏添一行，要说明的末尾记「11-08 铺开新添」。
#   同目录 挪坐标.tsv（纪、名字、地图x、地图y、缘故）里的行一并改（不在份表里的点，比如收稿时查出落在水里的）。
#   不加 --apply 只报不写。写完照提示重跑 合表.py。
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
ERA = sys.argv[1]
args = sys.argv[2:]
apply = '--apply' in args
parts = [a for a in args if a != '--apply']
P = os.path.join(ROOT, '底稿', '地图', '地点谱', ERA + '.tsv')
COLS = ['名字', '时段与年份', '类', '主要还是次要', '1001年叫什么', '别纪的叫法', '位置', '地图x', '地图y', '出处', '要说明的']

rows = list(csv.DictReader(open(P, encoding='utf-8'), delimiter='\t'))
head = list(rows[0].keys())
assert head[:len(COLS)] == COLS, head
by = {r['名字']: r for r in rows}
log = []


def note(r, s):
    r['要说明的'] = (r['要说明的'].rstrip('；') + '；' + s) if r['要说明的'] else s


for pt in parts:
    for q in csv.DictReader(open(pt, encoding='utf-8'), delimiter='\t'):
        nm = q['名字'].strip()
        t = q.get('条目', '').strip()
        if nm in by:
            r = by[nm]
            if t and t not in r['出处']:
                r['出处'] = (r['出处'] + '、' + t) if r['出处'] else t
                log.append('出处 %s ＋ %s' % (nm, t))
            if (q['地图x'], q['地图y']) != (r['地图x'], r['地图y']) and q['地图x'] not in ('', '?'):
                note(r, '11-08 铺开挪过，原来 %s,%s' % (r['地图x'], r['地图y']))
                log.append('坐标 %s %s,%s → %s,%s' % (nm, r['地图x'], r['地图y'], q['地图x'], q['地图y']))
                r['地图x'], r['地图y'] = q['地图x'], q['地图y']
                if q['位置'].strip() and q['位置'] != r['位置']:
                    r['位置'] = q['位置']
        else:
            r = {c: q.get(c, '').strip() for c in head}
            note(r, '11-08 铺开新添（%s）' % os.path.basename(pt))
            rows.append(r)
            by[nm] = r
            log.append('新添 %s（%s,%s）' % (nm, r['地图x'], r['地图y']))
mv = os.path.join(HERE, '挪坐标.tsv')
if os.path.exists(mv):
    for q in csv.DictReader(open(mv, encoding='utf-8'), delimiter='\t'):
        if q['纪'] != ERA:
            continue
        r = by.get(q['名字'])
        if not r:
            raise SystemExit('挪坐标.tsv 里的 %s 地点谱里没有' % q['名字'])
        if (r['地图x'], r['地图y']) != (q['地图x'], q['地图y']):
            note(r, '11-08 铺开挪过（%s），原来 %s,%s' % (q['缘故'], r['地图x'], r['地图y']))
            log.append('坐标 %s %s,%s → %s,%s（%s）' % (q['名字'], r['地图x'], r['地图y'], q['地图x'], q['地图y'], q['缘故']))
            r['地图x'], r['地图y'] = q['地图x'], q['地图y']
for s in log:
    print(s)
print('改 %d 处' % len(log))
if apply:
    w = csv.DictWriter(open(P, 'w', encoding='utf-8', newline=''), fieldnames=head, delimiter='\t', lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    print('写回 %s，接着在 底稿/地图/地点谱/ 下跑 python -I -X utf8 合表.py' % P)
else:
    print('没写盘，加 --apply 写')
