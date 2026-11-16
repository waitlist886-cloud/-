#!/usr/bin/env python3
# 把 <稿目录> 里每个文件的换行符、BOM、文件末尾的换行归成跟 <原目录> 里同名文件一样（Gemini 写回来的文件换行符不一定照旧）。
#   python -I -X utf8 eol_like.py <稿目录> <原目录>
import os
import sys

a, b = sys.argv[1], sys.argv[2]
for fn in sorted(os.listdir(a)):
    pa, pb = os.path.join(a, fn), os.path.join(b, fn)
    if not os.path.isfile(pa) or not os.path.isfile(pb):
        continue
    ref = open(pb, 'rb').read()
    cur = open(pa, 'rb').read()
    if cur.startswith(b'\xef\xbb\xbf') and not ref.startswith(b'\xef\xbb\xbf'):
        cur = cur[3:]
    crlf = b'\r\n' in ref
    t = cur.replace(b'\r\n', b'\n')
    # 行尾多出来的空格不动，只管换行符；文件末尾照原稿有没有换行
    t = t.rstrip(b'\n') + (b'\n' if ref.endswith(b'\n') else b'')
    if crlf:
        t = t.replace(b'\n', b'\r\n')
    if t != cur:
        open(pa, 'wb').write(t)
