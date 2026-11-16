#!/usr/bin/env python3
# 一份命星拟改接进分段稿以后，往各页的备注分段（p9_notes.md 这一类）里添一节，记这一页哪几颗 Special 接了半句。接完要重拼。
#   python -I -X utf8 底稿/洗稿/全卡精炼/临时脚本/add_star_notes_dir.py <拟改.md> <分段目录>=<备注文件> [<分段目录>=<备注文件> …] [--apply]
#   例：… 命星表/山铜纪_一二_拟改.md 山铜纪/parts1=山铜纪/parts1/p9_notes.md 山铜纪/parts2=山铜纪/parts2/p9_notes.md --apply
# 句子当中不带冒号（有的页备注挂在会被人物检查扫到的节底下）。
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
APPLY = '--apply' in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith('--')]
MD = args[0]
MAP = dict(a.split('=', 1) for a in args[1:])
HEAD = '### 11-16 命星照命运，Special 的头一段接了半句'


def parse(md):
    out = []
    for ln in open(md, encoding='utf-8').read().replace('\r', '').split('\n'):
        m = re.match(r'^- \*\*([^｜*]+)｜([^*]+)\*\*：(.*)$', ln)
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def has_star(path, star):
    t = open(path, 'rb').read().decode('utf-8')
    return re.search(r'^### ' + re.escape(star) + r' \(Special', t, re.M) is not None


targets = {}
for who, star in parse(MD):
    hit = None
    for d, notes in MAP.items():
        for p in sorted(glob.glob(d + '/*.md')):
            if has_star(p, star):
                hit = notes
    if not hit:
        raise SystemExit('找不到 %s｜%s' % (who, star))
    targets.setdefault(hit, []).append((who, star))

n = 0
for path, lst in targets.items():
    t = open(path, 'rb').read().decode('utf-8')
    nl = '\r\n' if '\r\n' in t else '\n'
    names = '、'.join('%s的%s' % (w, s) for w, s in lst)
    print('%s｜%d 颗｜%s' % (path, len(lst), 'CRLF' if nl == '\r\n' else 'LF'))
    if HEAD in t:
        print('   已经有这一节，跳过')
        continue
    sec = [
        '',
        HEAD,
        '',
        '- 用户 11-16 定了一条，命星映照出的应该是这个人的命运、宿命。月银纪和纷争纪头三页的表用户回了“照表改”，这一页照同一路子做，Special 名字不换，只在头一段那句“谁家常有”的话后头接半句扣着这个人的命的老话，新接的句子在星条里标着★。接了的有' + names + '。表在 ' + MD.replace(chr(92), '/') + '，发给了用户，不要的那几句说一声就拿掉。',
        '- Special 的头一段洗稿不动。往后别拿 还原星头.py 照标签 详本_11-15 还原这一页的星，会把接上的半句冲掉。',
    ]
    if not t.endswith(nl):
        t += nl
    t += nl.join(sec) + nl
    n += 1
    if APPLY:
        open(path, 'wb').write(t.encode('utf-8'))
print('%s %d 个备注文件' % ('写了' if APPLY else '（没写）要写', n))
