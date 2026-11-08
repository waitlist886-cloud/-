# 把 a.svg 里用户画的 aulOverlay 那一组塞进试验脚本的 'AUL_SVG' 占位。用法：python embed_aul.py a.svg 脚本.js 输出.js
import re
import sys

a = open(sys.argv[1], encoding='utf8').read()
i = a.find('<g id="aulOverlay"')
depth = 0
j = None
for m in re.finditer(r'<g[\s>]|</g>', a[i:]):
    if m.group().startswith('</'):
        depth -= 1
        if depth == 0:
            j = i + m.end()
            break
    else:
        depth += 1
g = a[i:j]
inner = g[g.find('>') + 1:-4]
inner = re.sub(r'\s+', ' ', inner).replace('\\', '\\\\').replace("'", "\\'")
s = open(sys.argv[2], encoding='utf8').read()
assert s.count("'AUL_SVG'") == 1
open(sys.argv[3], 'w', encoding='utf8').write(s.replace("'AUL_SVG'", "'" + inner + "'"))
print('ok', len(inner))
