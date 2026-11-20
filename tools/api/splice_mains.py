#!/usr/bin/env python3
# 把交稿里的主线换回迷宫纪前传各页的分段源稿（11-19 剧情铺开第二拨）。
# 一条主线从「## 迷宫纪·主线｜…」那一行换到它的「> 条目设置：」那一行为止，标题必须跟原来一字不差。
#   python -I -X utf8 tools/api/splice_mains.py 页号 交稿文件…      不加 --apply 只报
import glob
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


def mains(text):
    text = text.replace('\r\n', '\n')
    i = text.find('## 设计备注')
    if i >= 0:
        text = text[:i]
    out = {}
    for m in re.finditer(r'(?m)^## 迷宫纪·主线｜[^\n]*$', text):
        rest = text[m.start():]
        e = re.search(r'(?m)^> 条目设置：[^\n]*$', rest)
        out[m.group(0).strip()] = rest[:e.end()]
    return out


def main():
    apply = '--apply' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--apply']
    page, files = int(args[0]), args[1:]
    new = {}
    for f in files:
        new.update(mains(open(f, encoding='utf-8').read()))
    parts = glob.glob(os.path.join(ROOT, '迷宫纪前传', 'parts%d' % page, '*.md'))
    added = []
    for title, body in new.items():
        hit = 0
        for f in parts:
            raw = open(f, encoding='utf-8', newline='').read()
            crlf = '\r\n' in raw
            s = raw.replace('\r\n', '\n')
            k = s.find(title + '\n')
            if k < 0:
                continue
            e = re.search(r'(?m)^> 条目设置：[^\n]*$', s[k:])
            s2 = s[:k] + body + s[k + e.end():]
            hit += 1
            if apply:
                open(f, 'w', encoding='utf-8', newline='').write(s2.replace('\n', '\r\n') if crlf else s2)
            print('换', os.path.basename(f), title[12:])
        if hit == 0:
            added.append(title)
        assert hit <= 1, title
    for t in added:
        print('原稿里没有，新条：', t[12:])
    return added


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
