# 照改动单逐处改仓库里的文件：每一处给「原文」和「改成」，原文要在那个文件里正好出现一次，对不上就停，一个文件也不写。
# 用法：python -I -X utf8 tools/apply_edits.py 改动单.md [改动单.md …] [--apply | --out 目录]
#   不加 --apply 只查不写：每一处找不找得到、是不是正好一处。
#   --out 目录：照仓库里的路径把改完的文件写到这个目录底下（仓库不动），拿来跑检查。
#
# 改动单的写法（一处一块）：
#   ### 编号｜一句话说明
#   文件：月银纪补卷/风土_09_生老病死与记名.md
#   原文：
#   ~~~
#   （原文一字不差，要在文件里正好出现一次；改的是一整段就抄一整段，往后接一句就抄接的那一句做锚）
#   ~~~
#   改成：
#   ~~~
#   （改完的整段，锚也要写回去）
#   ~~~
# 同一个文件的几处照改动单里的先后改，后一处的原文要照前一处改完以后的样子找。块以外的话（说明、备注）不管。
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
args = sys.argv[1:]
apply = '--apply' in args
out = None
if '--out' in args:
    i = args.index('--out')
    out = args[i + 1]
    args = args[:i] + args[i + 2:]
lists = [a for a in args if a != '--apply']

BLOCK = re.compile(r'^### ([^\n]*)\n文件：([^\n]+)\n原文：\n~~~\n(.*?)\n~~~\n改成：\n~~~\n(.*?)\n~~~', re.S | re.M)

edits = []
for p in lists:
    text = open(p, encoding='utf-8').read().replace('\r\n', '\n')
    found = BLOCK.findall(text)
    heads = len(re.findall(r'^### ', text, re.M))
    if heads != len(found):
        print('提醒｜%s 里 ### 开头的块 %d 个，认得出的 %d 个，写法不对的块没算进去' % (p, heads, len(found)))
    for head, f, old, new in found:
        edits.append((p, head.strip(), f.strip().replace('\\', '/'), old, new))

cache = {}
crlf = {}
errs = []
done = 0
for src, head, f, old, new in edits:
    path = os.path.join(ROOT, f)
    if f not in cache:
        if not os.path.exists(path):
            errs.append('%s｜文件不在：%s' % (head, f))
            continue
        raw = open(path, encoding='utf-8', newline='').read()
        crlf[f] = '\r\n' in raw
        cache[f] = raw.replace('\r\n', '\n')
    t = cache[f]
    n = t.count(old)
    if n != 1:
        errs.append('%s｜%s 里原文出现 %d 处（要正好一处）：%s' % (head, f, n, old[:40].replace('\n', '⏎')))
        continue
    if old == new:
        errs.append('%s｜原文和改成一样' % head)
        continue
    cache[f] = t.replace(old, new)
    done += 1

for s in errs:
    print('错｜' + s)
print('改动 %d 处，涉及文件 %d 个，错 %d%s' % (done, len(cache), len(errs), '' if (apply or out) else '（没写盘，加 --apply 写）'))
if out and not errs:
    for f, t in cache.items():
        q = os.path.join(out, f)
        os.makedirs(os.path.dirname(q), exist_ok=True)
        open(q, 'w', encoding='utf-8', newline='\n').write(t)
    print('改完的副本写在 %s 底下：%s' % (out, '、'.join(cache)))
if apply:
    if errs:
        print('有错，一个文件也没写')
        sys.exit(1)
    for f, t in cache.items():
        # 原文件是 CRLF 的照 CRLF 写回，免得整份文件换行都变了
        open(os.path.join(ROOT, f), 'w', encoding='utf-8', newline='\r\n' if crlf.get(f) else '\n').write(t)
    print('写好了：' + '、'.join(cache))
sys.exit(1 if errs else 0)
