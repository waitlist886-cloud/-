"""纷争纪新料的黑名单：照年份挡的那几条，补上第二十二张开局的年份写法（开局时段：第二十二张｜年份：N）。
用法：python -I -X utf8 bl22.py <仓库根> [--apply]"""
import glob, io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = sys.argv[1]
APPLY = '--apply' in sys.argv
D = os.path.join(ROOT, '底稿', 'DLC', '新料')
FILES = [os.path.join(D, '样稿三条.md'), os.path.join(D, '第一拨.md')]
for sub, pat in (('律法志', 'L*.md'), ('风物志', 'F*.md'), ('谱系志', 'G*.md'), ('谱系志', 'C*.md')):
    FILES += sorted(glob.glob(os.path.join(D, sub, pat)))
HEAD = '(?:<br>|hud-meta">|纪元：)'
PAT = re.compile(r'^' + re.escape(HEAD) + r'纷争纪\(\?:(.+)\)年$')
n = 0
odd = 0
for f in FILES:
    L = open(f, encoding='utf-8').read().split('\n')
    title = ''
    changed = False
    for i, ln in enumerate(L):
        if ln.startswith('## '):
            title = ln[3:].strip()
        if not ln.startswith('> 条目设置：') or '纷争纪' not in title:
            continue
        k = ln.find('黑名单')
        if k < 0:
            continue
        m = re.match(r'黑名单 `/(.+?)/`', ln[k:])
        if not m:
            continue
        rx = m.group(1)
        if '第二十二张' in rx or '纷争纪(' not in rx:
            continue
        mm = PAT.match(rx)
        if not mm:
            odd += 1
            print('认不出的写法：', os.path.basename(f), '｜', title, '｜', rx[:150])
            continue
        years = mm.group(1)
        parts = years.split('|')          # 本体的写法里元也留着
        new = rx + '|开局时段：第二十二张｜年份：(?:' + '|'.join(parts) + r')(?!\d)'
        re.compile(new)
        n += 1
        print('补：', os.path.basename(f), '｜', title, '｜', '|'.join(parts)[:80])
        if APPLY:
            L[i] = ln[:k] + ln[k:].replace('`/' + rx + '/`', '`/' + new + '/`', 1)
            changed = True
    if changed:
        open(f, 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
print('要补的', n, '条；认不出的', odd, '条')
