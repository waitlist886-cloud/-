# 用法：python -X utf8 ngram.py 稿子.md 语料文件或目录... —— 报出稿子里和语料相同的 N 字串（只算汉字，不跨标点）
import sys, os, re
N = 6
def clauses(t):
    for c in re.split(r'[^\u4e00-\u9fff]+', t):
        if len(c) >= N: yield c
src = open(sys.argv[1], encoding='utf-8').read()
files = []
for p in sys.argv[2:]:
    if os.path.isdir(p):
        files += [os.path.join(p, f) for f in os.listdir(p) if f.endswith('.md')]
    else:
        files.append(p)
grams = {}
for f in files:
    t = open(f, encoding='utf-8').read()
    for c in clauses(t):
        for i in range(len(c) - N + 1):
            grams.setdefault(c[i:i+N], os.path.basename(f))
hits = {}
for c in clauses(src):
    for i in range(len(c) - N + 1):
        g = c[i:i+N]
        if g in grams: hits.setdefault(g, (grams[g], c))
print('corpus files', len(files), 'grams', len(grams), 'hits', len(hits))
for g, (f, c) in hits.items(): print(g, '|', f, '|', c)
