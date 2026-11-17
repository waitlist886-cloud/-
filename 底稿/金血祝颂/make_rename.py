#!/usr/bin/env python3
# 改短那一轮的改名表（11-17 晚）：照 名单.tsv 的次序把 稿_改短前/ 和 稿/ 两边的名字一颗一颗对上，写 改名表.tsv。
#   python -I -X utf8 底稿/金血祝颂/make_rename.py
# gen_entries.py 拿它把旧名字留在触发里当别名。
import csv
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OLD, NEW = os.path.join(HERE, '稿_改短前'), os.path.join(HERE, '稿')
ROWS = list(csv.DictReader(open(os.path.join(HERE, '名单.tsv'), encoding='utf-8'), delimiter='\t'))


def names(p):
    s = open(p, encoding='utf-8').read().replace('\r', '')
    s = re.split(r'\n## 备注', s)[0]
    return [m.group(1).strip() for m in re.finditer(r'(?m)^### (.+?) \(Passive \| Legend\)\s*$', s)]


out = []
for p in sorted(glob.glob(os.path.join(NEW, '份*.md'))):
    base = os.path.basename(p)
    fen = re.match(r'(份\d)', base).group(1)
    gods = [r['神'] for r in ROWS if r['份'] == fen]
    new, old = names(p), names(os.path.join(OLD, base))
    if not (len(new) == len(old) == len(gods)):
        sys.exit('%s 对不上：新 %d 旧 %d 名单 %d' % (base, len(new), len(old), len(gods)))
    out += [(fen, g, o, n) for g, o, n in zip(gods, old, new)]
with open(os.path.join(HERE, '改名表.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('份\t神\t旧名\t新名\n')
    for r in out:
        f.write('\t'.join(r) + '\n')
print('改名表', len(out), '行，换了名的', sum(1 for r in out if r[2] != r[3]))
