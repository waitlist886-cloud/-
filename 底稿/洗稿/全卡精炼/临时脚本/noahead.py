#!/usr/bin/env python3
# 羁绊补卷里【调用】那一段的“……不提前说”这类锁：逐章印原稿和审后稿各自的那一句，看洗掉的是通用的还是这一章自己的。
#   python -I -X utf8 noahead.py <份名…>
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
PAT = re.compile(r'不提前说|不预告|不提前讲|不提前给')


def chapters(t):
    t = t.replace('\r\n', '\n')
    out = {}
    for m in re.finditer(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)', t, re.M | re.S):
        out[m.group(1).strip()] = m.group(2)
    return out


def sents(body):
    res = []
    for ln in body.split('\n'):
        if not ln.startswith('【调用】'):
            continue
        for s in re.split(r'(?<=。)', ln):
            if PAT.search(s):
                res.append(s.strip())
    return res


tot_o = tot_n = 0
for job in sys.argv[1:]:
    d = '%s/%s' % (BASE, job)
    for fn in sorted(os.listdir(d + '/稿')):
        if not fn.endswith('.md'):
            continue
        o = chapters(open('%s/原/%s' % (d, fn), encoding='utf-8').read())
        n = chapters(open('%s/稿/%s' % (d, fn), encoding='utf-8').read())
        for k in o:
            so, sn = sents(o[k]), sents(n.get(k, ''))
            tot_o += len(so)
            tot_n += len(sn)
            if so and not sn:
                print('%s｜%s｜%s' % (job, fn[:6], k[-14:]))
                for s in so:
                    print('    原：' + s[:90])
print('调用里带这类锁的句子：原稿 %d 句，审后 %d 句' % (tot_o, tot_n))
