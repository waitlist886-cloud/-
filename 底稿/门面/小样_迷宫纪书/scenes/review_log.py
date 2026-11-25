#!/usr/bin/env python3
# 节点原画的审图记录（11-25）：一行一回，追加在 审图记录_节点.tsv（键、第几稿、结论、看到什么）。
#   python -I -X utf8 review_log.py 键 过|重画|留空 "看到什么"      第几稿照出图目录里 <键>_vN.png 的个数加一
#   python -I -X utf8 review_log.py --sum                              各键眼下的结论，数一数
import glob
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, '审图记录_节点.tsv')
OUT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '状态栏', 'comfy', 'out', '门面_原画_迷宫纪_节点'))


def rows():
    if not os.path.exists(TSV):
        return []
    return [l.rstrip('\n').split('\t') for l in open(TSV, encoding='utf-8') if l.strip() and not l.startswith('键\t')]


if sys.argv[1] == '--sum':
    last = {}
    for r in rows():
        last[r[0]] = r
    n = {}
    for r in last.values():
        n[r[2]] = n.get(r[2], 0) + 1
    print('审过', len(last), '幅：', '，'.join('%s %d' % kv for kv in sorted(n.items())), '；一共看了', len(rows()), '回')
    for k in sorted(last):
        if last[k][2] != '过':
            print(' ', '\t'.join(last[k]))
else:
    key, verdict, note = sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ''
    assert verdict in ('过', '重画', '留空'), verdict
    ver = len(glob.glob(os.path.join(OUT, key + '_v[0-9]*.png'))) + 1
    new = not os.path.exists(TSV)
    with open(TSV, 'a', encoding='utf-8', newline='\n') as f:
        if new:
            f.write('键\t第几稿\t结论\t看到什么\n')
        f.write('%s\t%d\t%s\t%s\n' % (key, ver, verdict, note.replace('\t', ' ').replace('\n', ' ')))
    print(key, ver, verdict)
