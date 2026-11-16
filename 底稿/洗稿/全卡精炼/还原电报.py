#!/usr/bin/env python3
# 把洗成电报的块整块退回原稿。块照 `## ` 和 `### ` 标题切（跟 自查.py 量电报腔的切法一样）。
# 量法也跟自查一样：一块里“的了着是在就也还把这那他她它”占汉字的比例，洗后掉到原稿的七成以下就是电报。
# 11-16 夜 Gemini 3.8 Flash 有一份（渊月长廊）被催着收短，把十几块压成了“仅、则、仍”连成的短语，虚字一个不剩。
# 这种块叫它自己改它会往句子里添字凑数，叫审稿人写回白话等于让审稿人重写一遍，都不如整块退回原稿、往后有人洗的时候补洗。
#   python -I -X utf8 底稿/洗稿/全卡精炼/还原电报.py <份名…> [--min 0.70] [--apply]
# 不加 --apply 只报。只动 稿/。冻住不洗的节不管。受保护的行本来就该跟原稿一样，退回以后也一样。
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
FROZEN = re.compile(r'设计备注|凡世至强')
PART = set('的了着是在就也还把这那他她它')
PROT = re.compile(r'^(?:#{2,3} |> 条目设置|固定锚定|底座：|体态数据|题：|篇：|章：|- 题：)')
args = sys.argv[1:]
APPLY = '--apply' in args
MIN = 0.70
jobs = []
i = 0
while i < len(args):
    if args[i] == '--min':
        MIN = float(args[i + 1]); i += 2; continue
    if not args[i].startswith('--'):
        jobs.append(args[i])
    i += 1


def split(text):
    """回 [(顶上那一节的标题, 小标题或空, [这一块的行，连标题行])]，页头那一截标题都空。"""
    out, top, sub, buf = [], '', '', []
    for l in text.split('\n'):
        if l.startswith('## ') or l.startswith('### '):
            out.append((top, sub, buf))
            if l.startswith('## '):
                top, sub = l[3:].strip(), ''
            else:
                sub = l[4:].strip()
            buf = [l]
        else:
            buf.append(l)
    out.append((top, sub, buf))
    return out


def dens(lines):
    t = '\n'.join(l for l in lines if not PROT.match(l) and not l.startswith('> '))
    h = re.findall(r'[\u4e00-\u9fff]', t)
    if not h:
        return None
    return len(h), 100.0 * sum(1 for c in h if c in PART) / len(h)


total = 0
for job in jobs:
    d = '%s/%s' % (BASE, job)
    for fn in json.load(open(d + '/job.json', encoding='utf-8'))['files']:
        fn = os.path.basename(fn)
        pn, po = '%s/稿/%s' % (d, fn), '%s/原/%s' % (d, fn)
        raw = open(pn, 'rb').read().decode('utf-8')
        nl = '\r\n' if '\r\n' in raw else '\n'
        new = split(raw.replace('\r\n', '\n'))
        old = split(open(po, 'rb').read().decode('utf-8').replace('\r\n', '\n'))
        oi = {}
        for top, sub, buf in old:
            oi.setdefault((top, sub), buf)
        hit = False
        for k, (top, sub, buf) in enumerate(new):
            if not top or FROZEN.search(top) or (top, sub) not in oi:
                continue
            ob = oi[(top, sub)]
            if ob == buf:
                continue
            a, c = dens(ob), dens(buf)
            if not a or not c or a[0] < 250 or c[0] < 120 or a[1] < 6:
                continue
            r = c[1] / a[1]
            if r < MIN:
                total += 1
                print('%s｜%s｜%s%s｜虚字的比例是原稿的 %d%%（%d → %d 字）%s' % (
                    job, fn, top[:22], ('｜' + sub[:22]) if sub else '', r * 100, a[0], c[0], '｜退回原稿' if APPLY else ''))
                if APPLY:
                    new[k] = (top, sub, list(ob))
                    hit = True
        if hit:
            lines = []
            for top, sub, buf in new:
                lines.extend(buf)
            open(pn, 'wb').write('\n'.join(lines).replace('\n', nl).encode('utf-8'))
print('洗成电报的块（虚字的比例不到原稿的 %d%%）：%d 块%s' % (MIN * 100, total, '，都退回了原稿' if APPLY and total else ''))
