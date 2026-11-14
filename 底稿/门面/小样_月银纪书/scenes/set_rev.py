# 重画过、已经发过的图在 cg_table.json 里记 rev，备图时换一个文件名（<键>_rN.webp），浏览器不拿旧图。
# merge_scenes.py 重并时会把表里已有的 rev 留着。
#   python -I -X utf8 set_rev.py N 键 键 …
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BOOK = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
tp = os.path.join(BOOK, 'cg_table.json')
n, keys = int(sys.argv[1]), sys.argv[2:]
table = json.load(open(tp, encoding='utf-8'))
for k in keys:
    assert k in table, k
    table[k]['rev'] = n
out = '{\n' + ',\n'.join('  %s: %s' % (json.dumps(k), json.dumps(v, ensure_ascii=False)) for k, v in table.items()) + '\n}\n'
open(tp, 'w', encoding='utf-8', newline='\n').write(out)
print('记了 rev', n, '：', len(keys), '幅')
