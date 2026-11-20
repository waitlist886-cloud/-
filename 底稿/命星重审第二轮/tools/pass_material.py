#!/usr/bin/env python3
# 旅伴过条（11-20）：一页一份材料，写 材料/过_<页>.md。
#   python -I -X utf8 底稿/命星重审第二轮/tools/pass_material.py
# 页头：这一页每颗生来的星和持有人，这一页的技艺（名、档、行当），这一页的生来星提醒，这一纪的公共技艺清单。
# 每位旅伴：命路、身份、底座、位阶走势、技艺走势、能力行，主修那一门的「构成」「阶」，生来两颗的星条，11-20 那一轮的换名记录。
# 跨页的同一个人，生来的星只在头一页改（跟 pu_material 一样），后几页写明只做阶和兼修。
import csv
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(W, '..', '..'))
MAT = os.path.join(W, '材料')
STAR = re.compile(r'^### (\S+) \((Special|Passive|Art) \| (\w+)\)\n.*?(?=^### |^## |^> 条目设置|\Z)', re.S | re.M)
ERA = {'月银纪': '月银纪', '诸国期': '月银纪', '萨尔维斯': '月银纪', '纷争纪': '纷争纪', '山铜纪': '山铜纪', '迷宫纪前传': '迷宫纪'}
NL = chr(10)


def entries(t):
    pos = [m.start() for m in re.finditer(r'(?m)^## (?!裁定锁)', t)]
    return [t[s:(pos[i + 1] if i + 1 < len(pos) else len(t))] for i, s in enumerate(pos)]


def field(e, lab):
    m = re.search(r'^' + lab + r'[：｜](.*)$', e, re.M)
    return m.group(1) if m else ''


def main():
    idx = json.load(open(os.path.join(MAT, '索引.json'), encoding='utf-8'))
    rows = list(csv.DictReader(open(os.path.join(W, '技艺筛表.tsv'), encoding='utf-8'), delimiter='\t'))
    recs = json.load(open(os.path.join(W, '收稿', '记录.json'), encoding='utf-8'))
    oldcount = {}
    for r in recs:
        for s in r['stars']:
            oldcount[s['old']] = oldcount.get(s['old'], 0) + 1
    pub = {}
    for f in glob.glob(os.path.join(W, '交稿', 'pub_*.md')):
        era = os.path.basename(f)[4:-3]
        pub[era] = [l for l in open(f, encoding='utf-8').read().splitlines() if l.startswith('清单｜')]
    seen_who = set()
    tot = 0
    for key, v in idx.items():
        era = ERA[key.rsplit('_', 1)[0]]
        t = open(os.path.join(ROOT, v['file']), encoding='utf-8').read().replace('\r\n', NL)
        stars = {}
        for m in STAR.finditer(t):
            stars.setdefault(m.group(1), m.group(0).rstrip() + NL)
        cast = [e for e in entries(t) if e.startswith('## 旅途同行：')]
        if not cast:
            continue
        holders = {}
        for e in cast:
            who = re.match(r'## 旅途同行：([^（\n]+)', e).group(1).strip()
            for k, n, tr in re.findall(r'(Special|Passive)【([^】]+)】\((\w+)', field(e, '能力')):
                holders.setdefault('%s（%s %s）' % (n, k, tr), []).append(who)
        head = ['# %s：旅伴 %d 位' % (key, len(cast)), '',
                '## 这一页生来的星和持有人', ''] + ['- %s｜%s' % (k, '、'.join(w)) for k, w in holders.items()] + [
                '', '## 这一页的技艺（名、档、行当）', ''] + [
                '- %s（%s）｜%s' % (r['拟名'] if r['判'] == '换名' else r['技艺'], r['拟档'], r['行当']) for r in rows if r['页'] == key and r['判'] != '并回'] + [
                '', '## 这一页的生来星提醒（技艺筛表顺带看的）', ''] + [
                '- ' + r['生来星提醒'] for r in rows if r['页'] == key and r['生来星提醒']] + [
                '', '## 这一纪的公共技艺', ''] + pub.get(era, ['（还没有）']) + ['']
        parts = []
        for e in cast:
            who = re.match(r'## 旅途同行：([^（\n]+)', e).group(1).strip()
            short = who.split('·')[0]
            ab = field(e, '能力')
            seg = ['=' * 20, '【旅伴】' + who]
            if short in seen_who:
                seg.append('【这一位跨页】生来的星在前头那一页改，这一页 Special、Passive 照原样，只写能力行的阶、兼修、走势补。')
            seen_who.add(short)
            r = re.search(r'命路倾向【[^】]+】', field(e, '固定锚定'))
            for lab, val in [('命路', r.group(0) if r else ''), ('身份', field(e, '身份')), ('底座', field(e, '底座')),
                             ('位阶走势', field(e, '位阶走势')), ('技艺走势', field(e, '技艺走势')), ('能力', ab)]:
                if val:
                    seg.append('%s：%s' % (lab, val))
            for nm in re.findall(r'Art【([^】]+)】', ab):
                b = stars.get(nm, '')
                for lab in ('构成', '阶'):
                    m = re.search(r'^- ' + lab + r'：.*?(?=^- (?!\S+（)|\Z)', b, re.S | re.M)
                    if m:
                        seg.append('主修【%s】的%s' % (nm, m.group(0).strip()))
            hist = [s for rr in recs if rr['page'] == key and rr['who'].split('·')[0] == short for s in rr['stars']]
            for s in hist:
                if s['old'] != s['new']:
                    seg.append('11-20 换名记录：%s 原来叫【%s】%s' % (s['new'], s['old'], '（这个旧名 11-20 以前有 %d 位旅伴共用）' % oldcount[s['old']] if oldcount[s['old']] > 1 else ''))
            if short not in [x.split('·')[0] for x in []]:
                for k, n in re.findall(r'(Special|Passive)【([^】]+)】', ab):
                    seg.append(stars.get(n, '（这一页没有【%s】的星条）' % n).rstrip())
            parts.append(NL.join(seg))
            tot += 1
        open(os.path.join(MAT, '过_%s.md' % key), 'w', encoding='utf-8', newline=NL).write(NL.join(head) + NL + (NL * 2).join(parts) + NL)
    print('写了', tot, '位')


if __name__ == '__main__':
    main()
