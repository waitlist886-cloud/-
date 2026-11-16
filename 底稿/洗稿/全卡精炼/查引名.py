#!/usr/bin/env python3
# 查洗稿把条目名改坏的地方：洗稿人拿脚本成批把“那一X、这一X”换成“那X、这X”（11-16 夜前传第四页有两位这样做），
# 正文里引到的条目名（## 标题，或者标题里｜后头那一截）带着“那一”“这一”的，就跟标题对不上了。
#   python -I -X utf8 底稿/洗稿/全卡精炼/查引名.py [<份名…>] [--dir 稿] [--repo <文件…>]
# 不给份名就查活的文件夹里所有带 稿/ 的份。--repo 查仓库里的文件。只报不改。
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
BASE = 'C:/Users/waitl/codex_work/wash_1115'
SKIP = {'.git', '底稿', 'out', '语料', 'tools', 'skills', '.claude', '交接存档', 'node_modules', 'src', 'canon', 'work'}

args = sys.argv[1:]
DIR = '稿'
if '--dir' in args:
    i = args.index('--dir'); DIR = args[i + 1]; del args[i:i + 2]
repo_files = []
if '--repo' in args:
    i = args.index('--repo'); repo_files = args[i + 1:]; args = args[:i]
jobs = [a for a in args if not a.startswith('--')]


def headings():
    out = set()
    for dp, dns, fns in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT).split(os.sep)[0]
        if rel in SKIP:
            dns[:] = []
            continue
        for fn in fns:
            if not fn.endswith('.md'):
                continue
            try:
                for ln in open(os.path.join(dp, fn), encoding='utf-8'):
                    if ln.startswith('## '):
                        out.add(ln[3:].strip())
            except Exception:
                pass
    return out


pairs = {}
for t in headings():
    parts = [t]
    if '｜' in t:
        tail = t.split('｜', 1)[1]
        parts.append(tail)
        parts.append(re.sub(r'（[^（）]*）$', '', tail))
    for c in parts:
        if len(c) < 4 or ('那一' not in c and '这一' not in c):
            continue
        c2 = c.replace('那一', '那').replace('这一', '这')
        if c2 != c:
            pairs[c2] = c

targets = []
if repo_files:
    targets = [(p, None) for p in repo_files]
else:
    if not jobs:
        jobs = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob('%s/*/%s' % (BASE, DIR)))
    for job in jobs:
        for p in sorted(glob.glob('%s/%s/%s/*.md' % (BASE, job, DIR))):
            targets.append((p, job))

tot = 0
for p, job in targets:
    try:
        lines = open(p, encoding='utf-8').read().split('\n')
    except Exception:
        continue
    for i, ln in enumerate(lines, 1):
        for bad, good in pairs.items():
            if bad in ln and good not in ln:
                tot += 1
                name = ('%s/%s' % (job, os.path.basename(p))) if job else p
                print('%s:%d｜“%s”该是“%s”｜%s' % (name, i, bad, good, ln.strip()[:80]))
print('一共 %d 处（只报不改；照“该是”那一截手改回去）' % tot)
