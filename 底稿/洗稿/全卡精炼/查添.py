#!/usr/bin/env python3
# 找洗后“原稿里找不到出处”的句子：一句话里的两字组，在原稿同一个文件里出现过的不到一半，就列出来。
# Gemini 起稿爱添原稿没有的事（11-16 头一回试洗量出来的），这一支给审稿人和主会话当清单逐句核。
# Codex 的稿子也会列出一些（它换了说法的句子），拿它当底数比：同一类文件，列出来的句数占比高出一截的就是添得多。
#   python -I -X utf8 底稿/洗稿/全卡精炼/查添.py <份名…> [--min 0.5] [--dir 稿|稿_Codex原样] [--quiet]
# 不看：受保护的行、条目设置、设计备注一节、标题带凡世至强的节。
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
MIN = float(sys.argv[sys.argv.index('--min') + 1]) if '--min' in sys.argv else 0.5
DIR = sys.argv[sys.argv.index('--dir') + 1] if '--dir' in sys.argv else '稿'
QUIET = '--quiet' in sys.argv
skip = set()
for k in ('--min', '--dir'):
    if k in sys.argv:
        skip.add(sys.argv[sys.argv.index(k) + 1])
jobs = [a for a in sys.argv[1:] if not a.startswith('--') and a not in skip]
HAN = re.compile(r'[\u4e00-\u9fff]')
FROZEN = re.compile(r'设计备注|凡世至强')


def grams(s):
    h = ''.join(HAN.findall(s))
    return [h[i:i + 2] for i in range(len(h) - 1)]


def sents(text):
    out = []
    title = ''
    for ln in text.replace('\r', '').split('\n'):
        if ln.startswith('## '):
            title = ln[3:].strip()
            continue
        if FROZEN.search(title) or ln.startswith(('#', '>', '固定锚定', '底座', '体态数据', '题：', '章：', '篇：')):
            continue
        for s in re.split(r'(?<=[。？])', ln):
            if len(HAN.findall(s)) >= 10:
                out.append((title, s.strip()))
    return out


tot_all = hit_all = 0
for job in jobs:
    d = '%s/%s' % (BASE, job)
    for fn in json.load(open(d + '/job.json', encoding='utf-8'))['files']:
        fn = os.path.basename(fn)
        old = open('%s/原/%s' % (d, fn), encoding='utf-8').read()
        new = open('%s/%s/%s' % (d, DIR, fn), encoding='utf-8').read()
        og = set(grams(old))
        osents = set(s for _, s in sents(old))
        ss = [(t, s) for t, s in sents(new) if s not in osents]
        hits = []
        for t, s in ss:
            g = grams(s)
            if not g:
                continue
            cov = sum(1 for x in g if x in og) / len(g)
            if cov < MIN:
                hits.append((cov, t, s))
        tot_all += len(ss)
        hit_all += len(hits)
        print('== %s｜%s｜改写过的句子 %d，出处不到 %d%% 的 %d 句（%.1f%%）' % (job, fn, len(ss), MIN * 100, len(hits), 100 * len(hits) / max(1, len(ss))))
        if not QUIET:
            for cov, t, s in sorted(hits):
                print('  [%s] %d%%｜%s' % (t[:16], cov * 100, s[:120]))
print('合计：改写过的句子 %d，列出 %d 句（%.1f%%）' % (tot_all, hit_all, 100 * hit_all / max(1, tot_all)))
