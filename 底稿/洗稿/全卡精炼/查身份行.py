#!/usr/bin/env python3
# 旅伴条“身份”那一行开头的全名：原稿开头报的名字（名·姓），洗后还得在这一行里，模型认人靠它。
# 11-16 查出来的：Gemini 3.8 Flash 常把“维布克·艾希，人族哨兵……”收成“燕巢段城的哨兵……”，Codex 洗的也有零星几处。
#   python -I -X utf8 底稿/洗稿/全卡精炼/查身份行.py                    扫仓库里洗过的各页（对标签 详本_11-15）
#   python -I -X utf8 底稿/洗稿/全卡精炼/查身份行.py <文件…>            只查这几个文件
#   python -I -X utf8 底稿/洗稿/全卡精炼/查身份行.py --fix [<文件…>]    把丢了的名字补回：洗后那一行开头接上“名字，”
# 补回只补名字。种族、行当要不要一起补，看列出来的两行自己定（原稿那一行开头的半句会印出来）。
import glob
import io
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TAG = '详本_11-15'
FIX = '--fix' in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith('--')]
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
os.chdir(ROOT)

if args:
    files = args
else:
    files = []
    for pat in ('月银纪史诗/第*歌_*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md',
                '纷争纪/parts*/*.md', '山铜纪/parts*/*.md', '迷宫纪前传/parts*/*.md'):
        files += sorted(glob.glob(pat))

NAME = re.compile(r'身份：([^，。｜（(\s：]{2,16})')


def secs(text):
    out, cur = {}, None
    for ln in text.split('\n'):
        if ln.startswith('## '):
            cur = ln[3:].strip()
            out.setdefault(cur, [])
        elif cur is not None:
            out[cur].append(ln)
    return out


total = fixed = 0
for f in files:
    f = f.replace('\\', '/')
    r = subprocess.run(['git', 'show', '%s:%s' % (TAG, f)], capture_output=True)
    if r.returncode != 0:
        continue
    old = r.stdout.decode('utf-8', errors='replace').replace('\r\n', '\n')
    raw = open(f, 'rb').read().decode('utf-8')
    nl = '\r\n' if '\r\n' in raw else '\n'
    new = raw.replace('\r\n', '\n')
    so, sn = secs(old), secs(new)
    hits = []
    for t, body in so.items():
        if not t.startswith('旅途同行：') or t.startswith('旅途同行·背景') or t not in sn:
            continue
        lo = [l for l in body if l.startswith('身份：')]
        ln_ = [l for l in sn[t] if l.startswith('身份：')]
        if not lo or not ln_:
            continue
        m = NAME.match(lo[0])
        if not m:
            continue
        name = m.group(1)
        head = name.split('·')[0]
        if head not in t:          # 开头那一截不是标题里的名字，就不是报名字的写法
            continue
        if name in ln_[0] or (('·' not in name) and head in ln_[0][:40]):
            continue
        hits.append((t, name, lo[0], ln_[0]))
    if not hits:
        continue
    print('== %s' % f)
    for t, name, a, b in hits:
        total += 1
        print('  [%s]' % t[:34])
        print('     原｜%s' % a[:70])
        print('     洗｜%s' % b[:70])
    if FIX:
        lines = new.split('\n')
        cur = None
        want = {t: name for t, name, a, b in hits}
        for i, ln in enumerate(lines):
            if ln.startswith('## '):
                cur = ln[3:].strip()
            elif cur in want and ln.startswith('身份：'):
                lines[i] = '身份：%s，%s' % (want[cur], ln[3:])
                del want[cur]
                fixed += 1
        open(f, 'wb').write('\n'.join(lines).replace('\n', nl).encode('utf-8'))
print('身份行开头丢了全名的 %d 处%s' % (total, '，补回名字 %d 处' % fixed if FIX else '（没写，加 --fix 才补）'))
