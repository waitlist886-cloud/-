#!/usr/bin/env python3
# 把 交稿/*.md 里的整块（## #序号 … 到收尾的四个反引号）换进 底卡洗稿/ 里同序号的那一块；
# 洗稿层里还没有这一块的，接到含它前后序号的那一份批次文件末尾。
#   python -I -X utf8 底稿/收尾_11-24/1001大敌线/tools/splice_wash.py [--apply] 交稿文件…
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
WASH = os.path.join(ROOT, '底卡洗稿')
HEAD = re.compile(r'^## #(\d+)\b', re.M)


def blocks(text):
    """切成 {序号: 整块文本}，整块从 ## #N 到下一个 ## # 之前（去掉尾部空行）。"""
    out = {}
    ms = list(HEAD.finditer(text))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        out[int(m.group(1))] = (m.start(), end, text[m.start():end].rstrip('\n'))
    return out


def main():
    apply = '--apply' in sys.argv
    subs = [a for a in sys.argv[1:] if not a.startswith('--')]
    want = {}
    for f in subs:
        t = io.open(f, encoding='utf-8').read()
        for n, (_, _, b) in blocks(t).items():
            if n in want:
                raise SystemExit('两份交稿都写了 #%d：%s' % (n, f))
            if '````' not in b:
                raise SystemExit('#%d 没有正文围栏：%s' % (n, f))
            want[n] = b
    files = sorted(os.path.join(WASH, x) for x in os.listdir(WASH) if x.endswith('.md'))
    texts = {p: io.open(p, encoding='utf-8', newline='').read() for p in files}
    where = {}
    for p, t in texts.items():
        for n in blocks(t):
            where.setdefault(n, []).append(p)
    done = []
    for n, b in sorted(want.items()):
        ps = where.get(n, [])
        if len(ps) > 1:
            raise SystemExit('#%d 在几份批次里都有：%s' % (n, ps))
        if ps:
            p = ps[0]
            t = texts[p]
            s, e, old = blocks(t)[n]
            tail = t[s:e][len(t[s:e].rstrip('\n')):]
            texts[p] = t[:s] + b + tail + t[e:]
            done.append('换 #%d  %s' % (n, os.path.basename(p)))
        else:
            # 找序号最近的那一份
            near = min(where, key=lambda k: abs(k - n))
            p = where[near][0]
            texts[p] = texts[p].rstrip('\n') + '\n\n' + b + '\n'
            done.append('添 #%d  %s（挨着 #%d）' % (n, os.path.basename(p), near))
    for d in done:
        print(d)
    if apply:
        for p in set(x for x in files):
            io.open(p, 'w', encoding='utf-8', newline='').write(texts[p])
        print('写了')


main()
