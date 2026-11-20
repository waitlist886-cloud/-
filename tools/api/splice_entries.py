#!/usr/bin/env python3
# 按标题把交稿里改过的条目换回迷宫纪前传的分段源稿或补卷（11-19 剧情铺开第三拨）。
# 一条从「## 标题」那一行换到它后面第一个「> 条目设置：」那一行为止，标题必须跟原来一字不差。
#   python -I -X utf8 tools/api/splice_entries.py page 页号 交稿文件 [--apply]
#   python -I -X utf8 tools/api/splice_entries.py supp 交稿文件 [--apply]   交稿里每条前面有「〔文件：X〕」
# 找不到原条的印出来，当新条另行处理。
import glob
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


def blocks(text):
    text = text.replace('\r\n', '\n')
    i = text.find('\n## 设计备注')
    if i >= 0:
        text = text[:i]
    out = []
    cur_file = None
    pos = 0
    for m in re.finditer(r'(?m)^(?:〔文件：([^〕]+)〕\s*$|## (?!裁定锁)[^\n]+$)', text):
        if m.start() < pos:
            continue
        if m.group(1):
            cur_file = m.group(1).strip()
            continue
        rest = text[m.start():]
        e = re.search(r'(?m)^> 条目设置：[^\n]*$', rest)
        if not e:
            continue
        body = rest[:e.end()]
        out.append((cur_file, m.group(0).strip(), body))
        pos = m.start() + e.end()
    return out


def replace_in(files, title, body, apply):
    hit = []
    for f in files:
        raw = open(f, encoding='utf-8', newline='').read()
        crlf = '\r\n' in raw
        s = raw.replace('\r\n', '\n')
        k = s.find(title + '\n')
        if k < 0 or (k > 0 and s[k - 1] != '\n'):
            continue
        e = re.search(r'(?m)^> 条目设置：[^\n]*$', s[k:])
        if not e:
            continue
        hit.append(f)
        if apply:
            s2 = s[:k] + body + s[k + e.end():]
            open(f, 'w', encoding='utf-8', newline='').write(s2.replace('\n', '\r\n') if crlf else s2)
    return hit


def main():
    apply = '--apply' in sys.argv
    a = [x for x in sys.argv[1:] if x != '--apply']
    mode = a[0]
    if mode == 'page':
        page, src = int(a[1]), a[2]
        files = glob.glob(os.path.join(ROOT, '迷宫纪前传', 'parts%d' % page, '*.md'))
    else:
        src = a[1]
    new = []
    n = 0
    for fn, title, body in blocks(open(src, encoding='utf-8').read()):
        if mode == 'supp':
            files = glob.glob(os.path.join(ROOT, '迷宫纪前传', '补卷', fn)) + glob.glob(os.path.join(ROOT, '迷宫纪前传', fn))
        hit = replace_in(files, title, body, apply)
        if len(hit) > 1:
            print('！不止一处，没换：', title, [os.path.basename(h) for h in hit])
        elif not hit:
            new.append((fn, title, body))
        else:
            n += 1
    print('换了', n, '条')
    for fn, t, b in new:
        print('原来没有：', fn or '', t)
    return new


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
