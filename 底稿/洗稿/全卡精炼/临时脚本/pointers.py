#!/usr/bin/env python3
# 找洗后稿里“指到别的条目去”的句子（设计备注以前）：python -I -X utf8 pointers.py <份名…> [--repo 文件…]
# 一句一行，带行号、所在的栏、原稿同一节里有没有这句话。
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = 'C:/Users/waitl/codex_work/wash_1115'
PAT = re.compile(r'写在[^。，；\n]{0,10}背景条?里|见背景条|照[^。，；\n]{0,8}背景条|写在[^。，；\n]{0,12}那一条里|另见|详见|见主线|写在主线里|写在[^。，；\n]{0,8}旅伴条里|背景条里(?:有|写|讲)')


def scan(path, orig=None):
    t = open(path, encoding='utf-8').read().replace('\r', '')
    m = re.search(r'^## [^\n]*设计备注', t, re.M)
    body = t[:m.start()] if m else t
    o = open(orig, encoding='utf-8').read().replace('\r', '') if orig and os.path.exists(orig) else ''
    n = 0
    for i, line in enumerate(body.split('\n'), 1):
        for s in re.split(r'(?<=[。？])', line):
            if PAT.search(s):
                lab = re.match(r'^(?:- |\*\*)?([^：\n]{1,10})：', line)
                inorig = '原稿有' if s.strip() and s.strip() in o else '原稿无'
                print('  %d｜%s｜%s｜%s' % (i, lab.group(1) if lab else '-', inorig, s.strip()[:120]))
                n += 1
    return n


args = sys.argv[1:]
if '--repo' in args:
    for f in args[args.index('--repo') + 1:]:
        print('==', f)
        print('  共', scan(f), '句')
else:
    for job in args:
        d = ROOT + '/' + job
        for fn in sorted(os.listdir(d + '/稿')):
            if fn.endswith('.md'):
                print('==', job, fn)
                print('  共', scan(d + '/稿/' + fn, d + '/原/' + fn), '句')
