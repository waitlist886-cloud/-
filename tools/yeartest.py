import sys, re
# 从「条目设置」行里取出所有 /.../ 正则，只测含「纷争纪(?:」的；逐年 1..11099 拼成「纪元：纷争纪N年」，列出命中的年段
s = open(sys.argv[1], encoding='utf-8').read()
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
        if '纷争纪(?:' not in pat: continue
        pj = pat.replace('(?<', '(?<')
        try: rx = re.compile(pj)
        except re.error as e: print(ln, 'BAD', e); continue
        hit = [y for y in range(1, 11100) if rx.search('纪元：纷争纪%d年' % y)]
        yuan = bool(rx.search('纪元：纷争纪元年'))
        kind = '黑名单' if ('黑名单 `/' + pat) in line else '触发'
        print('L%d %s 命中: %s%s' % (ln, kind, ('元年, ' if yuan else ''), ranges(hit)))
