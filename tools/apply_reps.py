# 用法：python3 -I apply_reps.py 目标文件 替换表.py
# 替换表是一个 Python 文件，里面定义 REPS = [(旧, 新), ...]；每个旧串必须恰好出现一次，否则一处也不改。
import sys, runpy
path, reps_path = sys.argv[1], sys.argv[2]
s = open(path, encoding='utf-8').read()
REPS = runpy.run_path(reps_path)['REPS']
bad = [(i, o[:40], s.count(o)) for i, (o, n) in enumerate(REPS) if s.count(o) != 1]
if bad:
    for b in bad: print('不唯一或找不到：', b)
    sys.exit(1)
for o, n in REPS:
    s = s.replace(o, n)
open(path, 'w', encoding='utf-8').write(s)
print('改了', len(REPS), '处')
