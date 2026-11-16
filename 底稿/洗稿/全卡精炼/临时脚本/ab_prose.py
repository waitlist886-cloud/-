#!/usr/bin/env python3
# 把洗前洗后各场景的回复里的正文抽出来（§正文 那一行以后、下一条 § 记录以前），数字数，存成文件。
#   python -I -X utf8 ab_prose.py <场景前缀…>
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/agy_work/ab_1116'
OUT = os.path.dirname(os.path.abspath(__file__))


def prose(t):
    m = re.search(r'^§正文[^\n]*\n([\s\S]*?)(?=^§(?!话|技|起手|咏唱)[^\n]*$)', t, re.M)
    if not m:
        m = re.search(r'class="arc-prose"[^>]*>([\s\S]*?)</div>', t)
    body = m.group(1) if m else ''
    body = re.sub(r'<[^>]+>', '', body)
    return [x.strip() for x in re.split(r'\n\s*\n', body) if x.strip()]


def han(s):
    return len(re.findall(r'[\u4e00-\u9fff]', s))


for name in sys.argv[1:]:
    for side in ('洗前', '洗后'):
        p = '%s/%s_%s/回复.md' % (BASE, name, side)
        if not os.path.exists(p):
            print('没有', p)
            continue
        t = open(p, encoding='utf-8').read()
        ps = prose(t)
        recs = re.findall(r'^§([^｜\n]+)', t, re.M)
        tui = [x for x in re.findall(r'^§推演｜(\d)｜[^\n]*', t, re.M)]
        ren = re.search(r'^§推演｜3｜[^\n]*', t, re.M)
        names = re.findall(r'(?:｜|^)([^｜（\n]{1,8})（锚定源', ren.group(0)) if ren else []
        hua = re.findall(r'^§话｜([^｜\n]+)｜', t, re.M)
        o = '%s/%s_%s_正文.txt' % (OUT, name, side)
        open(o, 'w', encoding='utf-8', newline='\n').write('\n\n'.join(ps))
        print('%s %s｜全文 %d 字｜正文 %d 段 %d 汉字｜推演 %d 行｜推演3 的人 %s｜§话 %d 句（%s）｜记录 %d 行' % (
            name, side, len(t), len(ps), sum(han(x) for x in ps), len(tui), '、'.join(names), len(hua), '、'.join(sorted(set(hua))), len(recs)))
