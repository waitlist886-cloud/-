#!/usr/bin/env python3
# 命星重审第二轮（11-19 夜）：把交稿里改过的 Rare 技艺星条换回源稿。
#   python -I -X utf8 底稿/命星重审第二轮/tools/splice_rare.py [--apply]
# 一块从「### 名 (Art | Rare)」换到它后面第一个「### 」或「## 」以前。标题行、【调用】行要跟原来一字不差，对不上的印出来不换。
# 源稿：纷争纪、山铜纪、迷宫纪前传在 partsN/ 里（换完照各自的拼页脚本重拼），月银纪史诗、诸国期、萨尔维斯直接是页。
# 同一页里同一个标题出现在几份分段里（没拼进页的旧份也算），几份一起换。
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
W = os.path.join(ROOT, '底稿', '命星重审第二轮')
BLOCK = re.compile(r'^### (\S+) \(Art \| Rare\)\n.*?(?=^### |^## |^> 条目设置|\Z)', re.S | re.M)


def sources(key, page):
    era, n = key.rsplit('_', 1)
    n = int(n)
    if era == '纷争纪':
        d = os.path.join(ROOT, '纷争纪', 'parts' if n == 1 else 'parts%d' % n)
    elif era == '山铜纪':
        d = os.path.join(ROOT, '山铜纪', 'parts%d' % n)
    elif era == '迷宫纪前传':
        d = os.path.join(ROOT, '迷宫纪前传', 'parts%d' % n)
    else:
        return [os.path.join(ROOT, page)]
    return sorted(glob.glob(os.path.join(d, '*.md')))


def main(apply):
    idx = json.load(open(os.path.join(W, '材料', '索引.json'), encoding='utf-8'))
    done, miss, bad, files = 0, [], [], {}
    for f in sorted(glob.glob(os.path.join(W, '交稿', 'rare_*.md'))):
        key = re.match(r'rare_(.+)_\d+\.md', os.path.basename(f)).group(1)
        new = open(f, encoding='utf-8').read().replace('\r\n', '\n')
        for m in BLOCK.finditer(new):
            name, blk = m.group(1), m.group(0).rstrip('\n') + '\n\n'
            hit = 0
            for src in sources(key, idx[key]['file']):
                t = files.get(src)
                if t is None:
                    raw = open(src, encoding='utf-8', newline='').read()
                    t = files[src] = raw
                crlf = '\r\n' in t
                tn = t.replace('\r\n', '\n')
                om = re.search(r'^### ' + re.escape(name) + r' \(Art \| Rare\)\n.*?(?=^### |^## |^> 条目设置|\Z)', tn, re.S | re.M)
                if not om:
                    continue
                old = om.group(0)
                call_o = re.search(r'^【调用】.*$', old, re.M)
                call_n = re.search(r'^【调用】.*$', blk, re.M)
                if (call_o and call_n and call_o.group(0) != call_n.group(0)) or (call_o and not call_n):
                    bad.append('%s %s：【调用】行变了' % (key, name))
                    continue
                tail = '' if old.endswith('\n\n') or om.end() == len(tn) else ''
                rep = blk if old.endswith('\n\n') else blk.rstrip('\n') + '\n'
                tn = tn[:om.start()] + rep + tn[om.end():]
                files[src] = tn.replace('\n', '\r\n') if crlf else tn
                hit += 1
            if hit:
                done += 1
            else:
                miss.append('%s %s' % (key, name))
    print('换了', done, '门')
    for x in miss:
        print('  找不到源：', x)
    for x in bad:
        print('  没换：', x)
    if apply:
        n = 0
        for src, t in files.items():
            if open(src, encoding='utf-8', newline='').read() != t:
                open(src, 'w', encoding='utf-8', newline='').write(t)
                n += 1
        print('写了', n, '个文件')


if __name__ == '__main__':
    main('--apply' in sys.argv)
