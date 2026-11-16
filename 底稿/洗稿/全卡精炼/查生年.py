#!/usr/bin/env python3
# 查旅伴条里正文写的生年跟固定锚定的“生于某纪某年”对不对得上（11-16 山铜纪审稿人报出来的）。
# 来路：11-08 生日那一轮照“这一页开局那个月他几岁”倒推生日，生日落在开局那个月以后的，生年就比正文里“某年生”早一年。
# 四纪扫下来只有山铜纪有（七十来处，正文都是正好晚一年），前传第一页跟着山铜纪带过去两个人。
# 固定锚定是算岁数的底，也跟登记表（底稿/生日/登记_*.tsv）对着，所以正文照固定锚定改。
#   python -I -X utf8 底稿/洗稿/全卡精炼/查生年.py <文件或通配…>          只报
#   python -I -X utf8 底稿/洗稿/全卡精炼/查生年.py <文件或通配…> --fix    正文正好晚一年的改成固定锚定那一年（别的差法只报不改）
# 报的是同一节（## 到下一个 ##）里，固定锚定以外的行写着“N年生”“N年他生在”“N年出生”而 N 跟固定锚定的年份不一样的。
# 改的是分段稿，改完要重拼那一页。派出去还没收回来的活别改（收稿时仓库里的文件变过就不收）。
import glob
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
FIX = '--fix' in sys.argv
ANCHOR = re.compile(r'生于(月银纪前|月银纪|纷争纪|山铜纪|迷宫纪)?(\d{1,5})年')
# 一个年份只算一回：N年出生、N年他生在、N年她生在、N年降生、N年生（后头不是意日活长病）
PROSE = re.compile(r'(\d{1,5})(?=年(?:出生|他生在|她生在|降生|生(?![意日活长病])))')
files = []
for a in sys.argv[1:]:
    if a.startswith('--'):
        continue
    files += sorted(glob.glob(a)) or [a]
tot = fixed = 0
for f in files:
    raw = open(f, 'rb').read().decode('utf-8')
    nl = '\r\n' if '\r\n' in raw else '\n'
    lines = raw.split(nl)
    anc = None
    title = ''
    changed = False
    for i, ln in enumerate(lines):
        if ln.startswith('## '):
            title = ln[3:].strip()
            anc = None
            # 这一节的固定锚定在标题以后、下一个 ## 以前
            for nx in lines[i + 1:]:
                if nx.startswith('## '):
                    break
                if nx.startswith('固定锚定'):
                    m = ANCHOR.search(nx)
                    if m:
                        anc = (m.group(1) or '', int(m.group(2)))
                    break
            continue
        if not anc or ln.startswith('固定锚定') or ln.startswith('> 条目设置'):
            continue

        def rep(m):
            global tot, fixed
            y = int(m.group(1))
            if y == anc[1] or abs(y - anc[1]) > 3:
                return m.group(1)
            tot += 1
            s = max(0, m.start() - 14)
            print('%s｜%s｜固定锚定 %s%d年｜正文 %d年｜…%s…' % (f.replace(chr(92), '/').split('/')[-1], title[:22], anc[0], anc[1], y, ln[s:m.end() + 12]))
            if FIX and y == anc[1] + 1:
                fixed += 1
                return str(anc[1])
            return m.group(1)

        new = PROSE.sub(rep, ln)
        if new != ln:
            lines[i] = new
            changed = True
    if FIX and changed:
        open(f, 'wb').write(nl.join(lines).encode('utf-8'))
print('对不上的 %d 处%s' % (tot, '，改了 %d 处' % fixed if FIX else ''))
