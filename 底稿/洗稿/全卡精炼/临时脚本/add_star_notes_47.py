#!/usr/bin/env python3
# 11-16 纷争纪第四到七页的 Special 接了半句以后，往各页的备注分段里添一节（t8_notes、u8_notes、v8_notes、w8_notes），接完要重拼。
#   python -I -X utf8 底稿/洗稿/全卡精炼/临时脚本/add_star_notes_47.py [--apply]
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
APPLY = '--apply' in sys.argv
MD = '底稿/洗稿/全卡精炼/命星表/纷争纪_四到七_拟改.md'
STRIFE = {'纷争纪/parts4': '纷争纪/parts4/t8_notes.md', '纷争纪/parts5': '纷争纪/parts5/u8_notes.md',
          '纷争纪/parts6': '纷争纪/parts6/v8_notes.md', '纷争纪/parts7': '纷争纪/parts7/w8_notes.md'}
HEAD = '### 11-16 命星照命运：Special 的头一段接了半句'


def parse(md):
    t = open(md, encoding='utf-8').read().replace('\r', '')
    out = []
    for ln in t.split('\n'):
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
    for d, notes in STRIFE.items():
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
    print('%s｜%d 颗｜%s' % (os.path.basename(path), len(lst), 'CRLF' if nl == '\r\n' else 'LF'))
    if HEAD in t:
        print('   已经有这一节，跳过')
        continue
    sec = [
        '',
        HEAD,
        '',
        '- 用户 11-16 定：命星映照出的应该是这个人的命运、宿命。月银纪和纷争纪头三页的表用户回了“照表改”，这一页照同一路子做：Special 名字不换，只在头一段那句“谁家常有”的话后头接半句扣着这个人的命的老话，新接的句子在星条里标着★。接了的是：' + names + '。表在 底稿/洗稿/全卡精炼/命星表/纷争纪_四到七_拟改.md，发给了用户，不要的那几句说一声就拿掉。',
        '- Special 的头一段洗稿不动。往后别拿 还原星头.py 照标签 详本_11-15 还原这一页的星，会把接上的半句冲掉。',
    ]
    if path.endswith('w8_notes.md'):
        sec.append('- 芙莉莲的小咒收藏没接：她的命落在银露古法那一支送葬的长咏上，写在凡世至强那一条里，这一颗是有意跟它对着的。')
    if not t.endswith(nl):
        t += nl
    t += nl.join(sec) + nl
    n += 1
    if APPLY:
        open(path, 'wb').write(t.encode('utf-8'))
print('%s %d 个备注文件' % ('写了' if APPLY else '（没写）要写', n))
