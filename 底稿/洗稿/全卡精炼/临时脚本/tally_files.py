#!/usr/bin/env python3
# 仓库里若干文件对标签 详本_11-15 的洗前洗后汉字数。
#   python -I -X utf8 底稿/洗稿/全卡精炼/临时脚本/tally_files.py <文件或通配…>
import glob
import io
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
han = lambda s: len(re.findall(r'[一-鿿]', s))
fs = []
for a in sys.argv[1:]:
    fs += sorted(glob.glob(a)) or [a]
ta = tb = 0
for f in fs:
    f = f.replace(chr(92), '/')
    o = subprocess.run(['git', 'show', '详本_11-15:' + f], capture_output=True).stdout.decode('utf-8')
    n = open(f, encoding='utf-8').read()
    a, b = han(o), han(n)
    ta += a
    tb += b
    print('%s｜%d → %d（留 %d%%）' % (f.split('/')[-1], a, b, round(b * 100 / a) if a else 0))
print('合计 %d 个文件｜%d → %d（留 %d%%）' % (len(fs), ta, tb, round(tb * 100 / ta) if ta else 0))
