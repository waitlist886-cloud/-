# 把诗篇的本地稿转成上传用的 markdown：一节诗（连续的非空行）合成一个段落，行与行之间用反斜杠硬换行。
# 标题行（#）和引用行（>）原样保留。用法：python3 -I verse2doc.py in.md outdir maxbytes
import sys, os
src, outdir, maxb = sys.argv[1], sys.argv[2], int(sys.argv[3])
lines = open(src, encoding='utf-8').read().split('\n')
blocks, cur = [], []
for ln in lines:
    if not ln.strip():
        if cur: blocks.append(cur); cur = []
        continue
    if ln.startswith('#') or ln.startswith('>'):
        if cur: blocks.append(cur); cur = []
        blocks.append([ln]); continue
    cur.append(ln)
if cur: blocks.append(cur)
paras = []
for b in blocks:
    if len(b) == 1:
        paras.append(b[0])
    else:
        paras.append('\\\n'.join(b))
# 分块：在「## 」标题前切，单块不超过 maxb 字节
chunks, cur, size = [], [], 0
for p in paras:
    sz = len(p.encode('utf-8')) + 2
    if p.startswith('## ') and cur and size + sz > maxb:
        chunks.append(cur); cur, size = [], 0
    cur.append(p); size += sz
if cur: chunks.append(cur)
os.makedirs(outdir, exist_ok=True)
for i, c in enumerate(chunks, 1):
    t = '\n\n'.join(c)
    open(os.path.join(outdir, 'poem_chunk_%d.md' % i), 'w', encoding='utf-8').write(t)
    print(i, len(t.encode('utf-8')), c[0][:20])
print('paragraphs', len(paras))
