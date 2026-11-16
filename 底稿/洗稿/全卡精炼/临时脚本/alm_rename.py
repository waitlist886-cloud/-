#!/usr/bin/env python3
# 11-16 用户回“照表改”：阿尔姆的 Special 长风投掷改名随弦之臂（照 命星表/月银纪_万兽_拟改.md）。
# 每个旧串必须正好出现一次，对不上就停，一个字不写。行尾照原样留（按字节读写）。
#   python -I -X utf8 alm_rename.py [--apply]
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
APPLY = '--apply' in sys.argv

PAGE = '月银纪史诗/第一歌_灰桥初火.md'
MAP = '底稿/洗稿/命名对照表_月银纪.md'

OLD_LEAD_HEAD = '【长风投掷】是一条看得见就够得着的胳膊。灰桥猎户家的孩子里，偶尔有一个生来就是这样，'
NEW_LEAD_HEAD = ('【随弦之臂】是一条看得见就够得着的胳膊。灰桥猎户家的孩子里，偶尔有一个生来就是这样，'
                 '猎户的老话说，这样的胳膊是给一张弓配的，弦往哪里响，矛就往哪里落，哪一天弦不响了，胳膊也就停在那一天（★）。')
OLD_LEAD_MID = '十一岁那一冬头一回跟着哥哥出猎，一矛扎透了冰面（★）。矛出了他的手像带着一阵长风'
NEW_LEAD_MID = '十一岁那一冬头一回跟着哥哥出猎，哥哥的箭刚离弦，他的矛已经扎透了冰面。矛出了他的手像带着一阵长风'
OLD_LIMIT = '矛还是木头和骨头，扎不透的照样扎不透。一捆投完，他还得自己削。'
NEW_LIMIT = OLD_LIMIT + '这条胳膊这辈子只跟过一张弓（★）。'

PAGE_REPS = [
    ('Special【长风投掷】(Epic，', 'Special【随弦之臂】(Epic，'),
    ('- 长风投掷追的是出手时眼里那头叫出名字的兽', '- 随弦之臂追的是出手时眼里那头叫出名字的兽'),
    ('### 长风投掷 (Special | Epic)', '### 随弦之臂 (Special | Epic)'),
    (OLD_LEAD_HEAD, NEW_LEAD_HEAD),
    (OLD_LEAD_MID, NEW_LEAD_MID),
    (OLD_LIMIT, NEW_LIMIT),
]

ROW_ANCHOR = '| 目及之矛 | Special | Epic | 阿尔姆 | 长风投掷 |'
NEW_ROW = ('| 长风投掷 | Special | Epic | 阿尔姆 | 随弦之臂 | 四字 | 11-16 用户定命星要映照这个人的命，'
           '阿尔姆的矛一辈子追着哥哥的箭走，哥哥的弦不响了，他就停在极境，这一颗照这个改名，用户回了照表改。旧名留在触发里 | '
           '生来给一张弓配的胳膊，看得见就够得着，弦往哪里响矛就往哪里落，照页上随弦之臂那一条 |')


def load(p):
    b = open(p, 'rb').read()
    return b.decode('utf-8')


def save(p, t):
    open(p, 'wb').write(t.encode('utf-8'))


t = load(PAGE)
for a, n in PAGE_REPS:
    c = t.count(a)
    if c != 1:
        raise SystemExit('页上 count %d：%s' % (c, a[:30]))
    t = t.replace(a, n)
left = t.count('长风投掷')
print('页上换了 %d 处，换完还剩“长风投掷” %d 处' % (len(PAGE_REPS), left))

m = load(MAP)
nl = '\r\n' if '\r\n' in m else '\n'
lines = m.split(nl)
idx = [i for i, ln in enumerate(lines) if ln.startswith(ROW_ANCHOR)]
if len(idx) != 1:
    raise SystemExit('对照表里那一行找到 %d 处' % len(idx))
if any(ln.startswith('| 长风投掷 | Special') for ln in lines):
    print('对照表里已经有长风投掷那一行，不再添')
else:
    lines.insert(idx[0] + 1, NEW_ROW)
    print('对照表在第 %d 行后头添一行' % (idx[0] + 1))
m2 = nl.join(lines)

if APPLY:
    save(PAGE, t)
    save(MAP, m2)
    print('写了', PAGE, MAP)
else:
    print('只试，没写')
