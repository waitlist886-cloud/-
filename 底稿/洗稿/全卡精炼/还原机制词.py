#!/usr/bin/env python3
# 全卡精炼洗稿：机制用语照原稿。洗稿爱把“判定获得优势”写成“判定有优势”“判定占优”，
# 底卡通篇用的是“获得优势”（洗稿层里 86 处对 3 处），四纪照它。在仓库根上跑：
#   python -I -X utf8 底稿/洗稿/全卡精炼/还原机制词.py --repo <仓库里的文件…> [--fix]   原稿取标签 详本_11-15
#   python -I -X utf8 底稿/洗稿/全卡精炼/还原机制词.py <份名…> [--fix]                   活的文件夹里 稿/ 对 原/
# 只在“原稿这个文件里一处这种写法也没有”的时候才改（原稿自己就写“有优势”的不动）。
# 不加 --fix 只报。按字节读写，行尾照原样。
import io
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = 'C:/Users/waitl/codex_work/wash_1115'
VAR = re.compile(r'判定(?:上)?(?:有|占|得|具有|带)(优势|劣势)')
VAR2 = re.compile(r'判定占优(?!势)')
CANON = re.compile(r'判定获得(?:优势|劣势)')
fix = '--fix' in sys.argv


def one(label, old, path):
    b = open(path, 'rb').read()
    t = b.decode('utf-8')
    n_old_var = len(VAR.findall(old)) + len(VAR2.findall(old))
    n_new_var = len(VAR.findall(t)) + len(VAR2.findall(t))
    if not n_new_var:
        return 0
    if n_old_var:
        print('  %s｜原稿自己有 %d 处这种写法，洗后 %d 处，不动' % (label, n_old_var, n_new_var))
        return 0
    t2 = VAR.sub(lambda m: '判定获得' + m.group(1), t)
    t2 = VAR2.sub('判定获得优势', t2)
    co, cn = len(CANON.findall(old)), len(CANON.findall(t2))
    note = '' if cn <= co else '（改完“判定获得优势”%d 处，比原稿 %d 处多，看一眼）' % (cn, co)
    print('  %s｜%d 处%s%s' % (label, n_new_var, '，改回了' if fix else '', note))
    if fix:
        open(path, 'wb').write(t2.encode('utf-8'))
    return n_new_var


tot = 0
args = [a for a in sys.argv[1:] if not a.startswith('--')]
if '--repo' in sys.argv:
    for f in args:
        old = subprocess.run(['git', 'show', '详本_11-15:' + f], capture_output=True).stdout.decode('utf-8', 'replace')
        if not old:
            continue
        tot += one(f, old, f)
else:
    for job in args:
        d = '%s/%s' % (ROOT, job)
        for fn in sorted(os.listdir(d + '/稿')):
            if fn.endswith('.md') and os.path.exists('%s/原/%s' % (d, fn)):
                old = open('%s/原/%s' % (d, fn), 'rb').read().decode('utf-8')
                tot += one('%s｜%s' % (job, fn), old, '%s/稿/%s' % (d, fn))
print('合计 %d 处%s' % (tot, '' if fix else '（没写，加 --fix 才改）'))
