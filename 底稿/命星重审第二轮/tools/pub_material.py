#!/usr/bin/env python3
# 公共技艺（11-20）：一纪一份材料，写 材料/公_<纪>.md。
#   python -I -X utf8 底稿/命星重审第二轮/tools/pub_material.py
# 材料：这一纪分几段、页上已有的技艺（名、档、行当，照 技艺筛表.tsv）、学艺与传承那一条、二十三条命路、底卡技艺池子的名字。
import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
W = os.path.join(ROOT, '底稿', '命星重审第二轮')
ERAS = {
    '月银纪': {'pages': ('月银纪', '诸国期', '萨尔维斯'), 're': '月银纪·正则', 'learn': '月银纪补卷/规则_学艺与传承.md',
             'span': '月银纪分三段：万兽史诗那十五歌（祭火、万兽，凡人在火边和兽口下活，没有学校，师从家里、部落、猎营），诸国期（七王与各国，王都、骑士、圣所、行会兴起），萨尔维斯（帝国，术式兵团、学派、辉塔，到帝国末年魔族之世）。一门公共技艺写明是哪一段的。'},
    '纷争纪': {'pages': ('纷争纪',), 're': '纷争纪·正则', 'learn': '纷争纪/补卷/补卷_88_学艺与传承.md',
             'span': '纷争纪是长垒的几千年，两块大陆隔着长垒打，人这一边有段城、学院（977年开门）、术式兵团、骑士团，魔族那一边有诸部。命路这时候开始成形，前一千年还没有路名。'},
    '山铜纪': {'pages': ('山铜纪',), 're': '山铜纪·正则', 'learn': '山铜纪/补卷/补卷_55_学艺与传承.md',
             'span': '山铜纪 2 到 947 年，止戈以后，两大帝国（巴尔缇娜的黑耀、索恩薇娅的晨曦一边），佣兵和行会、奥法协会、铳枪、学派、白烛圣所。'},
    '迷宫纪': {'pages': ('迷宫纪前传',), 're': '迷宫纪前传·正则', 'learn': '迷宫纪前传/补卷/补卷_60_学艺与传承.md',
             'span': '迷宫纪前传 2 到 1000 年，冒险者公会、大迷宫、星坠冒险者学院（约 450 年起）、420 年面板与旅印七阶、850 到 970 年黑潮。'},
}


def main():
    rows = list(csv.DictReader(open(os.path.join(W, '技艺筛表.tsv'), encoding='utf-8'), delimiter='\t'))
    pool = open(os.path.join(W, '材料', '命路表.md'), encoding='utf-8').read()
    base = []
    raw = open(os.path.join(ROOT, 'src', 'rili_v7.json'), encoding='utf-8').read()
    base = sorted(set(re.findall(r'## (\S+) \(Art \| (\w+)\)', raw)))
    for era, v in ERAS.items():
        mine = [r for r in rows if r['页'].startswith(v['pages'])]
        seen, lines = set(), []
        for r in mine:
            nm = r['拟名'] if r['判'] == '换名' else r['技艺']
            if nm in seen:
                continue
            seen.add(nm)
            lines.append('- %s（%s，%s）｜%s' % (nm, r['拟档'], r['页'], r['行当']))
        learn = open(os.path.join(ROOT, v['learn']), encoding='utf-8').read()
        out = ['# %s 公共技艺材料' % era, '', '纪名写「%s」，正则写〔%s〕。' % (era, v['re']), '', '## 这一纪分几段', '', v['span'], '',
               '## 这一纪页上已经有的技艺（名、档、出处页、行当）', ''] + lines + ['', '## 学艺与传承', '', learn.strip(), '', pool.strip(), '',
               '## 底卡技艺池子的名字（不许撞）', '', '、'.join('%s(%s)' % x for x in base), '']
        open(os.path.join(W, '材料', '公_%s.md' % era), 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
        print(era, len(lines), '门已有')


if __name__ == '__main__':
    main()
