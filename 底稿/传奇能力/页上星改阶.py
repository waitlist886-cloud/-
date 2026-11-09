#!/usr/bin/env python3
# 页上命星的阶改 Unique（底稿/洗稿/传奇能力与全卡去八股_计划.md 第四节第1件，用户 11-09 回“照这份铺开”）。
# 传奇的 Special、Passive 是生来的 Unique，各纪页上给过他们的那几颗，标题照旧写当时的叫法，阶改成 Unique，
# 条目里添一句只给 AI 的话，说往后读出来是哪一颗、那一页的人只看得见头一点、数照那一页的样子不动。Art 不改（Art 会往上走）。
# 单子从 底稿/传奇能力/份*.md 的「> 页上的星」读，双王那几颗写在下面 EXTRA。
# 用法（在仓库根目录下）：python -I -X utf8 底稿/传奇能力/页上星改阶.py [--apply]，改的是各页的分段稿（parts），改完照报告重拼。
import glob
import os
import re
import runpy
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
C = runpy.run_path(os.path.join(HERE, '查稿.py'), run_name='lib')
NUM = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7}
# 双王（11-09 主会话写的那两条，没有份文件）：页、星名、类、对上的那一颗、谁
EXTRA = [
    ('山铜纪/山铜纪时段_三_白鸦的年月.md', '领名之誓', 'Special', '灰雨之冠', '巴尔缇娜'),
    ('山铜纪/山铜纪时段_三_白鸦的年月.md', '不缚血脉', 'Passive', '不缚血脉', '巴尔缇娜'),
    ('山铜纪/山铜纪时段_四_黎明的年月.md', '灰墨心弦', 'Special', '灰雨之冠', '巴尔缇娜'),
    ('山铜纪/山铜纪时段_三_白鸦的年月.md', '泥中之握', 'Special', '万夜一晓', '索恩薇娅'),
    ('山铜纪/山铜纪时段_三_白鸦的年月.md', '河滩眼', 'Passive', '未明眼', '索恩薇娅'),
]


def todo():
    out = list(EXTRA)
    for f in sorted(glob.glob(os.path.join(HERE, '份*.md'))):
        for b in C['parse'](f):
            who = None
            s = open(f, encoding='utf-8').read()
            m = re.search(r'(?m)^## #%d (\S+)' % b['n'], s)
            who = m.group(1) if m else '?'
            for line in b['stars']:
                p = line[2:].split('｜')
                if len(p) < 4:
                    continue
                page, title, _, target = p[0].strip(), p[1].strip(), p[2], '｜'.join(p[3:])
                tm = re.match(r'### (.+?) \((Special|Passive|Art) \| \w+\)', title)
                if tm:
                    name, typ = tm.group(1), tm.group(2)
                else:
                    tm = re.match(r'### 旅伴条能力行 (Special|Passive|Art)【([^】]+)】', title)
                    if not tm:
                        print('认不出的一行：', line[:60])
                        continue
                    name, typ = tm.group(2), tm.group(1)
                if typ == 'Art':
                    continue
                gm = re.match(r'(Special|Passive)【([^】]+)】', target)
                if not gm:
                    print('不对应，不改：', page, name)
                    continue
                out.append((page, name, typ, gm.group(2), who))
    return out


def parts_dir(page):
    era = os.path.dirname(page)
    m = re.search(r'时段_(.)_', os.path.basename(page))
    return os.path.join(era, 'parts%d' % NUM[m.group(1)]) if era != '纷争纪' else os.path.join(era, 'parts%d' % NUM[m.group(1)])


def note(name, target, who):
    if name == target:
        return '- 只给 AI：%s这一颗是生来的，阶是 Unique，往后长成的就是【%s】那一版，这一页写的是那时候露出来的样子，数照这一页。' % (who, target)
    return '- 只给 AI：这一颗是%s生来的【%s】(Unique)露出来的头一点，那时候的人只看得见这一点，叫它%s，数照这一页。' % (who, target, name)


def main():
    apply = '--apply' in sys.argv
    items = todo()
    files = {}

    def get(p):
        if p not in files:
            raw = open(p, encoding='utf-8', newline='').read()
            files[p] = [raw, raw.replace('\r\n', '\n'), '\r\n' in raw]
        return files[p]

    pages = set()
    for page, name, typ, target, who in items:
        pd = parts_dir(page)
        hit = 0
        for p in sorted(glob.glob(os.path.join(pd, '*.md'))):
            f = get(p)
            s = f[1]
            m = re.search(r'(?m)^### %s \(%s \| (\w+)\)$' % (re.escape(name), typ), s)
            if not m:
                continue
            hit += 1
            if m.group(1) != 'Unique':
                s = s[:m.start()] + '### %s (%s | Unique)' % (name, typ) + s[m.end():]
            # 这一颗星的条目到下一个 ### 或文件尾为止，只给 AI 那一句接在最后一个「- 」行后头
            a = s.index('\n', m.start())
            nxt = re.search(r'(?m)^(### |## |> 条目设置)', s[a:])
            end = a + nxt.start() if nxt else len(s)
            blk = s[a:end]
            if '只给 AI：这一颗' not in blk and '往后长成的就是【' not in blk:
                lines = blk.rstrip('\n').split('\n')
                k = max(i for i, l in enumerate(lines) if l.startswith('- '))
                lines.insert(k + 1, note(name, target, who))
                blk2 = '\n'.join(lines) + blk[len(blk.rstrip('\n')):]
                s = s[:a] + blk2 + s[end:]
            f[1] = s
            pages.add(page)
        # 各纪页上能力行里写着这一颗的，阶跟着改（同一纪的分段稿都扫）
        n_ab = 0
        for p in sorted(glob.glob(os.path.join(os.path.dirname(pd), 'parts*', '*.md'))):
            f = get(p)
            s2, k = re.subn(r'【%s】\((?:Epic|Legend|Rare)(?=[，)、])' % re.escape(name), '【%s】(Unique' % name, f[1])
            if k:
                f[1] = s2
                n_ab += k
                pages.add(os.path.join(os.path.dirname(pd), '?'))
        print('%s｜%s (%s)→【%s】｜星标题 %d 处｜能力行 %d 处' % (os.path.basename(page)[:14], name, typ, target, hit, n_ab))
        if hit == 0 and n_ab == 0:
            print('   找不到，手看：', pd)
    changed = [p for p, f in files.items() if f[1] != f[0].replace('\r\n', '\n')]
    print('\n要改的分段稿', len(changed), '个：')
    for p in changed:
        print(' ', p)
        if apply:
            raw, s, crlf = files[p]
            open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
    eras = sorted({os.path.dirname(os.path.dirname(p)) + '/' + os.path.basename(os.path.dirname(p)) for p in changed})
    print('\n要重拼的：', '、'.join(eras))
    print('写了' if apply else '没加 --apply，什么也没写')


if __name__ == '__main__':
    main()
