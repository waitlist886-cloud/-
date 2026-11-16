#!/usr/bin/env python3
# 把若干位旅伴“正史里的下场”那一小节印出来（写命星拟改以前看各人的命用）。
#   python -I -X utf8 底稿/洗稿/全卡精炼/临时脚本/fates.py <文件> <人名,人名…> [<文件> <人名,…> …]
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
args = sys.argv[1:]
for f, names in zip(args[0::2], args[1::2]):
    t = open(f, encoding='utf-8').read().replace('\r\n', '\n')
    for n in names.split(','):
        m = re.search(r'^## 旅途同行：' + re.escape(n) + r'[^\n]*\n(.*?)(?=^## |\Z)', t, re.M | re.S)
        if not m:
            print('!! 没找到', f, n)
            continue
        sec = m.group(1)
        k = re.search(r'^### 正史里的下场[^\n]*\n(.*?)(?=^### |\Z)', sec, re.M | re.S)
        print('== %s｜%s' % (f.replace(chr(92), '/').split('/')[-1], n))
        print((k.group(1).strip() if k else '（没有“正史里的下场”小节）')[:900])
