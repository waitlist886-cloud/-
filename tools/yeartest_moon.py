import sys, re
# 从「条目设置」行里取出所有含「月银纪(?:」的正则，逐年 1..10081 拼成「纪元：月银纪N年」，列出命中的年段
s = open(sys.argv[1], encoding='utf-8').read()
def ranges(ys):
    out = []; st = None; pv = None
    for y in ys:
        if st is None: st = pv = y
        elif y == pv + 1: pv = y
        else: out.append((st, pv)); st = pv = y
    if st is not None: out.append((st, pv))
    return ', '.join('%d' % a if a == b else '%d-%d' % (a, b) for a, b in out)
title = ''
for ln, line in enumerate(s.split('\n'), 1):
    if line.startswith('## ') and not line.startswith('## 裁定锁'): title = line[3:].strip()
    if '条目设置' not in line: continue
    for m in re.finditer(r'`/(.+?)/`', line):
        pat = m.group(1)
        if '月银纪(?:' not in pat: continue
        try: rx = re.compile(pat)
        except re.error as e: print(ln, 'BAD', e); continue
        hit = [y for y in range(1, 10082) if rx.search('纪元：月银纪%d年' % y) or rx.search('日期</b><br>月银纪%d年·春' % y)]
        kind = '黑名单' if ('黑名单 `/' + pat) in line else '触发'
        print('%s｜%s 命中: %s' % (title, kind, ranges(hit)))
