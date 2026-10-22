# 用法：python3 -I check_protected.py <before.md> <after.md>
# 逐行比对受保护的行：条目设置、固定锚定、底座、体态数据、## 标题、### 星标题，以及正文里嵌着的体态数据
import re, sys
a = open(sys.argv[1], encoding='utf-8').read().split('\n')
b = open(sys.argv[2], encoding='utf-8').read().split('\n')
pat = re.compile(r'^(固定锚定|体态数据|底座|> 条目设置|## |### .+ \((Special|Passive|Art|Ability) \| )')
pa = [l for l in a if pat.match(l)]
pb = [l for l in b if pat.match(l)]
emb = lambda ls: sorted(m for l in ls for m in re.findall(r'体态数据｜[^。\n]*', l) if not l.startswith('体态数据'))
ok = pa == pb and emb(a) == emb(b)
print('protected', 'OK' if ok else 'DIFF', len(pa), 'lines,', len(emb(a)), 'embedded')
if not ok:
    import difflib
    for d in difflib.unified_diff(pa + emb(a), pb + emb(b), lineterm='', n=0):
        print(d[:200])
ab = lambda ls: [sorted(re.findall(r'【([^】]+)】', l)) for l in ls if l.startswith('能力：')]
print('能力 stars', 'OK' if ab(a) == ab(b) else 'DIFF %s -> %s' % (ab(a), ab(b)))
