#!/usr/bin/env python3
# 命星重审第二轮·铺开（11-20）：给写手的材料，一页一份，写 材料/铺_<页>.md。
#   python -I -X utf8 底稿/命星重审第二轮/tools/pu_material.py
# 每位旅伴：筛表里他那几行（判、拟档、方向）、筛表材料里裁过的旅伴条和背景条、两颗生来的星的星条、能力行里每门 Art 的星条。
# 跨页的同一个人，生来的星只在头一页改（筛表只留了头一页那一行），后几页标“只写技艺走势和能力行”，铺开收稿时把头一页的新星抄过去。
import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
W = os.path.join(ROOT, '底稿', '命星重审第二轮')
MAT = os.path.join(W, '材料')
STAR = re.compile(r'^### (\S+) \((Special|Passive|Art) \| (\w+)\)\n.*?(?=^### |^## |^> 条目设置|\Z)', re.S | re.M)


def main():
    idx = json.load(open(os.path.join(MAT, '索引.json'), encoding='utf-8'))
    rows = list(csv.DictReader(open(os.path.join(W, '筛表.tsv'), encoding='utf-8'), delimiter='\t'))
    tot = 0
    for key, v in idx.items():
        f = os.path.join(MAT, '筛_%s.md' % key)
        if not os.path.exists(f):
            continue
        page = open(os.path.join(ROOT, v['file']), encoding='utf-8').read().replace('\r\n', '\n')
        arts = {m.group(1): m.group(0).rstrip() + '\n' for m in STAR.finditer(page) if m.group(2) == 'Art'}
        head, *items = open(f, encoding='utf-8').read().split('=' * 20 + '\n')
        out = []
        for it in items:
            who = re.search(r'^【旅伴】(.+)$', it, re.M).group(1).strip()
            short = who.split('·')[0]
            mine = [r for r in rows if r['旅伴'].split('·')[0] == short and r['页'] == key]
            later = [r for r in rows if r['旅伴'].split('·')[0] == short and key in r['又见'].split('、')]
            seg = ['=' * 20, '【旅伴】%s' % who]
            if mine:
                seg.append('【筛表】')
                for r in mine:
                    seg.append('- %s｜现档 %s｜判 %s｜为什么：%s｜拟档 %s｜方向：%s' % (r['星'], r['现档'], r['判'], r['为什么'], r['拟档'], r['方向']))
            elif later:
                seg.append('【筛表】这一位的生来的星在%s改，这一页不改星，只写技艺走势和能力行（能力行里 Special、Passive 照原样抄）。' % later[0]['页'])
            else:
                seg.append('【筛表】筛表里没有这一位，生来的星不改，只写技艺走势和能力行。')
            body = it.split('\n', 2)[2] if it.startswith('【旅伴】') else it
            seg.append(body.rstrip())
            ab = re.search(r'^能力：(.*)$', it, re.M)
            for nm in re.findall(r'Art【([^】]+)】', ab.group(1) if ab else ''):
                if nm in arts:
                    seg.append(arts[nm])
            out.append('\n'.join(seg))
            tot += 1
        open(os.path.join(MAT, '铺_%s.md' % key), 'w', encoding='utf-8', newline='\n').write(head + '\n\n'.join(out) + '\n')
    print('写了', tot, '位旅伴的材料')


if __name__ == '__main__':
    main()
