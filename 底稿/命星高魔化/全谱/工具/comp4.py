# -*- coding: utf-8 -*-
"""旅伴条摘要：名、主线、底座、能力行、正史里的下场。
用法：python -I -X utf8 comp4.py <拼好的页.md> [--full]
"""
import re, sys, io

def sections(text):
    # 按 ## 标题切
    parts = re.split(r'(?m)^(?=## )', text)
    for p in parts:
        m = re.match(r'## 旅途同行：(.+?)\n', p)
        if m:
            yield m.group(1).strip(), p

def grab(body, pat, n=400):
    m = re.search(pat, body, re.S)
    if not m:
        return ''
    return re.sub(r'\s+', ' ', m.group(1)).strip()[:n]

def main():
    path = sys.argv[1]
    full = '--full' in sys.argv
    names = None
    tail = 0
    for a in sys.argv[2:]:
        if a.startswith('--names='):
            names = a.split('=', 1)[1].split(',')
        if a.startswith('--tail='):
            tail = int(a.split('=', 1)[1])
    text = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
    n = 0
    for title, body in sections(text):
        if names is not None:
            if not any(title.startswith(x) for x in names):
                continue
            if re.search(r'的背景|旅伴之间', title):
                continue
            xc = grab(body, r'### 正史里的下场\n+(.+?)(?:\n\n|\n###|\n【|\Z)', 4000)
            print('■ %s\n  下场尾：…%s' % (title, xc[-tail:] if tail else xc))
            continue
        if '背景' in title.split('（')[0][-3:]:
            continue
        if re.search(r'的背景|旅伴之间', title):
            continue
        n += 1
        dz = grab(body, r'(?m)^底座：(.+?)$', 260)
        nl = grab(body, r'(?m)^能力：(.+?)$', 300)
        xc = grab(body, r'### 正史里的下场\n+(.+?)(?:\n\n|\n###|\n【|\Z)', 420 if full else 260)
        sf = grab(body, r'(?m)^身份：(.+?)$', 160)
        print('■ %d %s' % (n, title))
        print('  底座：' + dz)
        if full:
            print('  身份：' + sf)
            print('  能力：' + nl)
        print('  下场：' + xc)

if __name__ == '__main__':
    main()
