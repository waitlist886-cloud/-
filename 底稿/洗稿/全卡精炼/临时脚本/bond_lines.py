#!/usr/bin/env python3
# 羁绊文件：每一章紧跟标题的两行（“某某之章：【题】”和“【人名】……·位阶·强弱”那一行）洗后跟原稿是不是一字不差。
#   python -I -X utf8 bond_lines.py <份名…> [--fix]     --fix 把这两行照原稿改回（写 稿/）
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = 'C:/Users/waitl/codex_work/wash_1115'
fix = '--fix' in sys.argv


def chapters(t):
    idx = [m.start() for m in re.finditer(r'^## ', t, re.M)] + [len(t)]
    out = {}
    for a, b in zip(idx, idx[1:]):
        head = t[a:t.index('\n', a)]
        out[head] = (a, b)
    return out


def keylines(sec):
    """章里头两种要紧的行：X之章：【题】；【人名】开头、带“·”的人物行。"""
    res = []
    for ln in sec.split('\n'):
        if re.match(r'^[^\s【】：]{1,8}之章：【[^】]+】\s*$', ln) or (re.match(r'^【[^】]{1,12}】', ln) and '·' in ln and not ln.startswith('【调用】')):
            res.append(ln)
    return res


tot = 0
for job in ([] if '--repo' in sys.argv else [a for a in sys.argv[1:] if not a.startswith('--')]):
    d = ROOT + '/' + job
    for fn in sorted(os.listdir(d + '/稿')):
        if not fn.endswith('.md'):
            continue
        ob = open('%s/原/%s' % (d, fn), 'rb').read().decode('utf-8')
        nb = open('%s/稿/%s' % (d, fn), 'rb').read().decode('utf-8')
        o, n = ob.replace('\r', ''), nb.replace('\r', '')
        co, cn = chapters(o), chapters(n)
        changed = 0
        for head, (a, b) in co.items():
            if head not in cn or '羁绊｜' not in head:
                continue
            ko, kn = keylines(o[a:b]), keylines(n[cn[head][0]:cn[head][1]])
            if ko == kn:
                continue
            for x, y in zip(ko, kn):
                if x != y:
                    changed += 1
                    tot += 1
                    print('%s｜%s｜%s' % (job, fn, head[3:30]))
                    print('    原：', x[:150])
                    print('    稿：', y[:150])
                    if fix and n.count(y) == 1:
                        n = n.replace(y, x)
            if len(ko) != len(kn):
                tot += 1
                print('%s｜%s｜%s：这两种行原稿 %d 行、洗后 %d 行' % (job, fn, head[3:30], len(ko), len(kn)))
        if fix and changed:
            crlf = nb.count('\r\n') > 10
            open('%s/稿/%s' % (d, fn), 'wb').write((n.replace('\n', '\r\n') if crlf else n).encode('utf-8'))
            print('  改回了', fn)
print('对不上', tot, '处')

# --repo <仓库里的文件…>：拿标签 详本_11-15 当原稿，直接改仓库里的文件（加 --fix 才写）
if '--repo' in sys.argv:
    import subprocess
    for f in sys.argv[sys.argv.index('--repo') + 1:]:
        if f.startswith('--'):
            continue
        ob = subprocess.run(['git', 'show', '详本_11-15:' + f], capture_output=True).stdout.decode('utf-8')
        nb = open(f, 'rb').read().decode('utf-8')
        o, n = ob.replace('\r', ''), nb.replace('\r', '')
        co, cn = chapters(o), chapters(n)
        k = 0
        for head, (a, b) in co.items():
            if head not in cn or '羁绊｜' not in head:
                continue
            ko, kn = keylines(o[a:b]), keylines(n[cn[head][0]:cn[head][1]])
            for x, y in zip(ko, kn):
                if x != y:
                    k += 1
                    print(f, '｜', head[3:26])
                    print('    原：', x[:140])
                    print('    稿：', y[:140])
                    if fix and n.count(y) == 1:
                        n = n.replace(y, x)
        if fix and k:
            crlf = nb.count('\r\n') > 10
            open(f, 'wb').write((n.replace('\n', '\r\n') if crlf else n).encode('utf-8'))
        print(f, '对不上', k, '处', '（改回了）' if fix and k else '')
