#!/usr/bin/env python3
# 成对替换，行尾照原样留（按字节读写）：python -I -X utf8 rep_keep.py 文件 "旧1" "新1" ["旧2" "新2" …]
# 每个旧串必须正好出现一次，对不上就停，一个字不写。
import sys

p = sys.argv[1]
b = open(p, 'rb').read()
t = b.decode('utf-8')
args = sys.argv[2:]
for i in range(0, len(args), 2):
    a, n = args[i], args[i + 1]
    c = t.count(a)
    if c != 1:
        raise SystemExit('count %d: %s' % (c, a[:40].encode('unicode_escape').decode('ascii')))
    t = t.replace(a, n)
open(p, 'wb').write(t.encode('utf-8'))
print('ok', len(args) // 2)
