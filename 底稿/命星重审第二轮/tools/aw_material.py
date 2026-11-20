#!/usr/bin/env python3
# 技艺铺开（11-20）：给写手的材料，一页一份，写 材料/写_<页>.md。
#   python -I -X utf8 底稿/命星重审第二轮/tools/aw_material.py
# 在 艺_<页>.md 每一门的【技艺】行后头插筛表那一行（统一、拦下以后的 技艺筛表.tsv）。
# 并回：母门在这一页上的，这一门不写，母门的材料里加一句“把它收成一招”；母门不在的，照换名写，新名是母门的名字。
import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, '..'))
MAT = os.path.join(W, '材料')
SEP = '=' * 20 + '\n'


def main():
    idx = json.load(open(os.path.join(MAT, '艺_索引.json'), encoding='utf-8'))
    rows = {(r['页'], r['技艺']): r for r in csv.DictReader(open(os.path.join(W, '技艺筛表.tsv'), encoding='utf-8'), delimiter='\t')}
    for key, v in idx.items():
        t = open(os.path.join(MAT, '艺_%s.md' % key), encoding='utf-8').read()
        head, *items = t.split(SEP)
        absorb = {}
        for nm in v['arts']:
            r = rows[(key, nm)]
            if r['判'] == '并回':
                p = re.sub(r'（.*?）', '', r['并入']).strip()
                if p in v['arts']:
                    absorb.setdefault(p, []).append('%s（%s）' % (nm, r['方向']))
        out = []
        for it in items:
            nm = re.match(r'【技艺】(\S+)｜', it).group(1)
            r = rows[(key, nm)]
            j, name = r['判'], r['拟名'] or nm
            note = ''
            if j == '并回':
                p = re.sub(r'（.*?）', '', r['并入']).strip()
                if p in v['arts']:
                    note = '这一门并进同页的%s，不写，交一行（并回，不写）。' % p
                else:
                    j, name = '换名', p
                    note = '母门%s页上没有，照换名写，新名就是%s，这一门的东西做成它里头的一招或一科。' % (p, p)
            line = '【筛表】判 %s｜拟名 %s｜拟档 %s｜行当 %s｜为什么 %s｜方向 %s' % (j, name, r['拟档'], r['行当'], r['为什么'], r['方向'])
            if note:
                line += '｜' + note
            if nm in absorb:
                line += '｜同页并进来的：' + '；'.join(absorb[nm]) + '，把它收成这一门里的一招或一科。'
            first, rest = it.split('\n', 1)
            out.append(first + '\n' + line + '\n' + rest)
        open(os.path.join(MAT, '写_%s.md' % key), 'w', encoding='utf-8', newline='\n').write(head + SEP + SEP.join(out))
    print('写了', len(idx), '页')


if __name__ == '__main__':
    main()
