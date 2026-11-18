# -*- coding: utf-8 -*-
"""铺开·套改：主会话手改的几处，照一份 JSON 单子逐串替换。每个旧串在那个文件里必须正好出现指定的回数（默认 1），对不上的不改、报出来。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/套改.py 单子.json [--dry]
单子是一个数组，一条是 [文件（相对仓库根）, 旧串, 新串] 或者 [文件, 旧串, 新串, 回数]。文件是 CRLF 的，单子里的换行写 \\n 就行，脚本照文件的换行符换。"""
import io, os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 搭活 as D

lst = json.load(io.open(sys.argv[1], encoding='utf-8'))
dry = '--dry' in sys.argv
bad = 0
for it in lst:
    f, a, b = it[0], it[1], it[2]
    n = it[3] if len(it) > 3 else 1
    p = os.path.join(D.ROOT, f)
    s = io.open(p, encoding='utf-8', newline='').read()
    if '\r\n' in s:
        a, b = a.replace('\r\n', '\n').replace('\n', '\r\n'), b.replace('\r\n', '\n').replace('\n', '\r\n')
    k = s.count(a)
    if k != n:
        print('对不上 %d 处（要 %d）｜%s｜%s' % (k, n, f, a[:40].replace('\n', '⏎')))
        bad += 1
        continue
    if not dry:
        D.safe_write(p, s.replace(a, b))
print('%s %d 条，对不上 %d 条' % ('试了' if dry else '改了', len(lst) - bad, bad))
