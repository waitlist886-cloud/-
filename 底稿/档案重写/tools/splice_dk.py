#!/usr/bin/env python3
# 档案重写（11-28）：把交稿里的「## #号 标题」下那一块 ```` 围起来的条目，换进 底卡洗稿/*.md 同一个 #号 下面那一块。
#   python -I -X utf8 底稿/档案重写/tools/splice_dk.py <交稿.md> [<交稿.md> …] [--apply]
# 不加 --apply 只查不写。查的是：标题行、固定锚定、体态数据、专武那一行一字不差；好感那几行里的数（+5～+8 这类）一个不少；「」里的条目名一样。
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
DK = os.path.join(ROOT, '底卡洗稿')
BLK = re.compile(r'^## (#\d+)[^\n]*\n(?:(?!^## #)[\s\S])*?^````\n([\s\S]*?)^````', re.M)
KEEP = ('## ', '固定锚定', '体态数据', '专武')


def blocks(text):
    return {m.group(1): (m.start(2), m.end(2), m.group(2)) for m in BLK.finditer(text)}


def check(old, new):
    bad = []
    ol = [l for l in old.split('\n') if l.startswith(KEEP)]
    nl = [l for l in new.split('\n') if l.startswith(KEEP)]
    if ol != nl:
        bad.append('受保护的行不一样：' + '｜'.join(sorted(set(ol) ^ set(nl)))[:300])
    num = lambda t: sorted(re.findall(r'[+−-]\d+(?:～[+−-]?\d+)?', '\n'.join(l for l in t.split('\n') if l.startswith(('- 加', '- 减')))))
    if num(old) != num(new):
        bad.append('好感的数对不上')
    q = lambda t: sorted(set(re.findall(r'「[^」]+」', t)))
    if q(old) != q(new):
        bad.append('「」条目名对不上：%s / %s' % (q(old), q(new)))
    for p in ('——', '；', '！', '…'):
        if p in new:
            bad.append('有 ' + p)
    return bad


def main():
    apply = '--apply' in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith('--')]
    want = {}
    for f in files:
        for k, (_, _, body) in blocks(open(f, encoding='utf-8').read()).items():
            want[k] = (f, body)
    hit = set()
    for fn in sorted(os.listdir(DK)):
        if not fn.endswith('.md'):
            continue
        p = os.path.join(DK, fn)
        text = open(p, encoding='utf-8').read()
        bs = blocks(text)
        todo = [(k, bs[k]) for k in want if k in bs]
        if not todo:
            continue
        for k, (s, e, old) in sorted(todo, key=lambda x: -x[1][0]):
            new = want[k][1]
            bad = check(old, new)
            hit.add(k)
            print(('✗ ' if bad else '✓ ') + k, fn, len(old), '→', len(new), '；'.join(bad))
            if apply and not bad:
                text = text[:s] + new + text[e:]
        if apply:
            open(p, 'w', encoding='utf-8', newline='\n').write(text)
    for k in want:
        if k not in hit:
            print('✗ 底卡洗稿里没有', k, want[k][0])


if __name__ == '__main__':
    main()
