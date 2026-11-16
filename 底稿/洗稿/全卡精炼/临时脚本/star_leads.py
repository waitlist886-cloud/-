#!/usr/bin/env python3
# 把若干颗星的头一段印出来（写命星拟改以前看原句用）。
#   python -I -X utf8 底稿/洗稿/全卡精炼/临时脚本/star_leads.py <文件> <星名,星名…> [<文件> <星名,…> …]
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
args = sys.argv[1:]
for f, names in zip(args[0::2], args[1::2]):
    t = open(f, encoding='utf-8').read().replace('\r\n', '\n')
    for n in names.split(','):
        m = re.search(r'^### ' + re.escape(n) + r'[^\n]*\n(.*?)(?=^### |^## |\Z)', t, re.M | re.S)
        if not m:
            print('!! 没找到', f, n)
            continue
        lines = [x for x in m.group(1).split('\n') if x.strip()]
        lead = [x for x in lines if not x.startswith('【调用】') and not x.startswith('- ') and not x.startswith('>')]
        print('== %s｜%s' % (f.replace(chr(92), '/').split('/')[-1], n))
        for x in lead[:2]:
            print('   ' + x)
