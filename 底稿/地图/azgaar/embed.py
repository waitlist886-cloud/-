# 把一个文本文件的内容塞进脚本里的 '占位'（单引号括着的那个词），写成另一份可以直接跑的脚本。
# 用法：python -I embed.py 脚本.js 占位 文件 输出.js     例：python -I embed.py az_biwan.js BAY_D 碧湾_月银纪.path.txt az_biwan_run.js
import sys

src, key, data, out = sys.argv[1:5]
s = open(src, encoding='utf8').read()
d = open(data, encoding='utf8').read().strip().replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')
ph = "'" + key + "'"
assert s.count(ph) == 1, f'{ph} 在 {src} 里不是正好一处'
open(out, 'w', encoding='utf8').write(s.replace(ph, "'" + d + "'"))
print('ok', out, len(d))
