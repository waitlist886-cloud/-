import sys, re
# 用法：python3 -I yeartest_era.py 文件 纪名 最大年份（月银纪 10081，纷争纪 11099）。
# 从「条目设置」行里取出所有含「纪名(?:」的 /.../ 正则，逐年拼成「纪元：纪名N年」，列出命中的年段。
s = open(sys.argv[1], encoding='utf-8').read()
era = sys.argv[2]; top = int(sys.argv[3])
def ranges(ys):
    out = []; st = None; pv = None
    for y in ys:
        if st is None: st = pv = y
        elif y == pv + 1: pv = y
        else: out.append((st, pv)); st = pv = y
    if st is not None: out.append((st, pv))
    return ', '.join('%d' % a if a == b else '%d-%d' % (a, b) for a, b in out)
for ln, line in enumerate(s.split('\n'), 1):
    if '条目设置' not in line: continue
    for m in re.finditer(r'`/(.+?)/`', line):
        pat = m.group(1)
        if era + '(?:' not in pat: continue
        try: rx = re.compile(pat)
        except re.error as e: print(ln, 'BAD', e); continue
        hit = [y for y in range(1, top + 1) if rx.search('纪元：%s%d年' % (era, y))]
        yuan = bool(rx.search('纪元：%s元年' % era))
        kind = '黑名单' if ('黑名单 `/' + pat) in line else '触发'
        print('L%d %s 命中: %s%s' % (ln, kind, ('元年, ' if yuan else ''), ranges(hit)))
