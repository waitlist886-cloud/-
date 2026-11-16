#!/usr/bin/env python3
# 11-16 “照表改”以后，往各页的设计备注里添一节，记这一页哪几颗 Special 的头一段接了半句。
#   python -I -X utf8 add_star_notes.py [--apply]
# 月银纪的页直接接在页尾（页尾是设计备注）；纷争纪接在各页的备注分段（p8_notes、q9_notes、r8_notes），接完要重拼。
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
APPLY = '--apply' in sys.argv
D = '底稿/洗稿/全卡精炼/命星表/'
MDS = [D + '月银纪_万兽_拟改.md', D + '月银纪_诸国期_拟改.md', D + '月银纪_萨尔维斯_拟改.md', D + '纷争纪_一到三_拟改.md']
MOON = sorted(glob.glob('月银纪史诗/*.md')) + sorted(glob.glob('诸国期/诸国期时段_*.md')) + sorted(glob.glob('萨尔维斯/萨尔维斯时段_*.md'))
STRIFE = {'纷争纪/parts': '纷争纪/parts/p8_notes.md', '纷争纪/parts2': '纷争纪/parts2/q9_notes.md', '纷争纪/parts3': '纷争纪/parts3/r8_notes.md'}
HEAD = '### 11-16 命星照命运：Special 的头一段接了半句'


def parse(md):
    t = open(md, encoding='utf-8').read().replace('\r', '')
    out = []
    lines = t.split('\n')
    for i, ln in enumerate(lines):
        m = re.match(r'^- \*\*([^｜*]+)｜([^*]+)\*\*：(.*)$', ln)
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
            continue
        m = re.match(r'^### ([^｜]+)｜(.+?)（留名）\s*$', ln)
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def has_star(path, star):
    t = open(path, 'rb').read().decode('utf-8')
    return re.search(r'^### ' + re.escape(star) + r' \(Special', t, re.M) is not None


targets = {}   # 备注要接进去的文件 → [(who, star)]
for md in MDS:
    for who, star in parse(md):
        hit = None
        if '纷争纪' in md:
            for d, notes in STRIFE.items():
                for p in sorted(glob.glob(d + '/*.md')):
                    if has_star(p, star):
                        hit = notes
        else:
            for p in MOON:
                if has_star(p, star):
                    hit = p
        if not hit:
            raise SystemExit('找不到 %s｜%s' % (who, star))
        targets.setdefault(hit, []).append((who, star))

n = 0
for path, lst in targets.items():
    b = open(path, 'rb').read()
    t = b.decode('utf-8')
    nl = '\r\n' if '\r\n' in t else '\n'
    last2 = [m.group(0) for m in re.finditer(r'^## [^\r\n]*', t, re.M)]
    tail_h = last2[-1] if last2 else '（没有 ## 标题）'
    ok = ('备注' in tail_h) or path.endswith('_notes.md')
    names = '、'.join('%s的%s' % (w, s) for w, s in lst)
    print('%s｜%d 颗｜末节：%s｜%s｜%s' % (os.path.basename(path), len(lst), tail_h[:28], 'CRLF' if nl == '\r\n' else 'LF', '可接' if ok else '！末节不是备注'))
    if not ok:
        raise SystemExit('停：' + path)
    if HEAD in t:
        print('   已经有这一节，跳过')
        continue
    sec = [
        '',
        HEAD,
        '',
        '- 用户 11-16 定：命星映照出的应该是这个人的命运、宿命。这一页的 Special 名字不换，只在头一段那句老话后头接半句扣着这个人的命的话，新接的句子在星条里标着★，用户回了“照表改”。接了的是：' + names + '。',
        '- Special 的头一段洗稿不动。往后别拿 还原星头.py 照标签 详本_11-15 还原这一页，会把接上的半句冲掉。',
    ]
    if path.endswith('第一歌_灰桥初火.md'):
        sec.append('- 同一回阿尔姆的长风投掷改名随弦之臂（Epic，本事照旧）：头一段添了猎户的那句老话和“哥哥的箭刚离弦”，限制添了一句这条胳膊这辈子只跟过一张弓（★）。旧名留在触发里，命名对照表添了一行。')
    add = nl.join(sec) + nl
    if not t.endswith('\n'):
        t += nl
    t2 = t + add
    n += 1
    if APPLY:
        open(path, 'wb').write(t2.encode('utf-8'))
print('要添 %d 个文件%s' % (n, '，写了' if APPLY else '，只试没写'))
