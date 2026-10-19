# 用法：python3 -I apply_pairs.py 目标文件 替换对.json
# 替换对是 [[旧, 新], ...]，每个旧串必须在文件里恰好出现一次，否则一处也不改。
import json, sys
path, pairs_path = sys.argv[1], sys.argv[2]
s = open(path, encoding='utf-8').read()
pairs = json.load(open(pairs_path, encoding='utf-8'))
bad = [(i, s.count(o)) for i, (o, n) in enumerate(pairs) if s.count(o) != 1]
if bad:
    print('不唯一或找不到：', bad); sys.exit(1)
for o, n in pairs:
    s = s.replace(o, n)
open(path, 'w', encoding='utf-8').write(s)
print('改了', len(pairs), '处')
