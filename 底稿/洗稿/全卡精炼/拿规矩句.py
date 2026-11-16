#!/usr/bin/env python3
# 拿掉条目里那一句通用的规矩“玩家在场插手照玩家做的事走”（常驻里有，11-16 写进了四纪常驻；审稿人有时当成本条的锁补回来）。
#   python -I -X utf8 底稿/洗稿/全卡精炼/拿规矩句.py <份名…> [--dir 稿] [--apply]
# 只拿这一个分句，同一句里后头接着写本条自己的事的（“……照玩家做的事走，玩家在墙里站进缺口，影子从他身上穿过去”）留后半句。
# 整行只有这一句的（列表项）整行拿掉。不加 --apply 只报。行尾照原样留。
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
DIR = '稿'
if '--dir' in sys.argv:
    DIR = sys.argv[sys.argv.index('--dir') + 1]
    args = [a for a in args if a != DIR]
APPLY = '--apply' in sys.argv
R = r'玩家在场插手(?:，|的话，)?照(?:着)?玩家做的事走'


def fix(text):
    lines = text.split('\n')
    out = []
    for ln in lines:
        core = ln.rstrip('\r')
        if re.fullmatch(r'\s*-\s*' + R + r'。\s*', core):
            continue  # 整行只有这一句
        s = core
        s = re.sub(r'，' + R + r'。', '。', s)                      # 句尾分句
        s = re.sub(r'(^|(?<=[。：]))(\s*-\s*)?' + R + r'，', lambda m: (m.group(2) or ''), s)   # 句首分句，后头还有话
        s = re.sub(r'(^|(?<=[。]))' + R + r'。', '', s)              # 单独一句
        out.append(s + ('\r' if ln.endswith('\r') else ''))
    return '\n'.join(out)


tot = 0
for job in args:
    for p in sorted(glob.glob('%s/%s/%s/*.md' % (BASE, job, DIR))):
        raw = open(p, encoding='utf-8', newline='').read()
        new = fix(raw)
        n = raw.count('玩家在场插手') - new.count('玩家在场插手')
        if n:
            tot += n
            print('%s/%s｜拿掉 %d 处，还剩 %d 处' % (job, os.path.basename(p), n, new.count('玩家在场插手')))
            if APPLY:
                open(p, 'w', encoding='utf-8', newline='').write(new)
print('一共 %d 处%s' % (tot, '，改了' if APPLY else '（只报，加 --apply 才改）'))
