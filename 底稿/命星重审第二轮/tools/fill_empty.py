#!/usr/bin/env python3
# 旅伴过条（11-20）补漏：splice_pass 的 parse 取交稿星条时停在正文头一行【调用】，换回去的星条只剩标题。
# 这一支照交稿把空的星条补回正文。
#   python -I -X utf8 底稿/命星重审第二轮/tools/fill_empty.py          只报
#   python -I -X utf8 底稿/命星重审第二轮/tools/fill_empty.py --apply  写盘（源稿），写完照常重拼各页
# 空星条：标题下面直到下一个 ###、## 或条目设置之间没有字。先在同一页键的交稿里找同名的块，标题的档要一样；
# 找不到的列出来手看。
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from splice_rare import sources, W  # noqa: E402
from splice_pass import parse  # noqa: E402

NL = chr(10)
CRLF = chr(13) + chr(10)
EMPTY = re.compile(r'^(### (\S+) \((Special|Passive|Art) \| (\w+)\))\n(\s*)(?=^### |^## |^> 条目设置|\Z)', re.M)


def main(apply):
    idx = json.load(open(os.path.join(W, '材料', '索引.json'), encoding='utf-8'))
    got = {}
    for f in sorted(glob.glob(os.path.join(W, '交稿', 'pass_*.md'))):
        key = re.match(r'pass_(.+)_\d+\.md', os.path.basename(f)).group(1)
        _, stars, _, _ = parse(open(f, encoding='utf-8').read())
        for name, blk in stars:
            got.setdefault(key, {}).setdefault(name, []).append(blk)
    filled, left = 0, []
    for key, v in idx.items():
        for src in sources(key, v['file']):
            raw = open(src, encoding='utf-8', newline='').read()
            crlf = CRLF in raw
            t = raw.replace(CRLF, NL)
            out, pos = [], 0
            for m in EMPTY.finditer(t):
                name, head = m.group(2), m.group(1)
                cands = [b for b in got.get(key, {}).get(name, []) if b.split(NL, 1)[0].strip() == head]
                if not cands:
                    cands = got.get(key, {}).get(name, [])
                if not cands:
                    left.append('%s｜%s' % (os.path.relpath(src, os.path.join(W, '..', '..')), head))
                    continue
                blk = cands[-1]
                if blk.split(NL, 1)[0].strip() != head:
                    left.append('%s｜%s（交稿标题是 %s，没补）' % (os.path.relpath(src, os.path.join(W, '..', '..')), head, blk.split(NL, 1)[0]))
                    continue
                out.append(t[pos:m.start()])
                out.append(blk.rstrip(NL) + NL + NL)
                pos = m.end()
                filled += 1
            if pos:
                out.append(t[pos:])
                nt = ''.join(out)
                if apply:
                    open(src, 'w', encoding='utf-8', newline='').write(nt.replace(NL, CRLF) if crlf else nt)
    print('补了', filled, '块，没补上', len(left))
    for x in left:
        print('  ', x)


if __name__ == '__main__':
    main('--apply' in sys.argv)
