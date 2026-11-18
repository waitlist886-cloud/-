# -*- coding: utf-8 -*-
"""铺开·节首注：一页并完、换完名以后，在「这一代的命星」那一节开头（给作者看的那一段，不进卡）末尾接一句，
写明这一轮照全谱重判以后技艺各档的数。再跑一遍只换那一句，不会接两回。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/节首注.py 页… [--apply]
"""
import io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 搭活 as D

MARK = '〔11-17 全谱重判〕'
ANY = re.compile(r'^### (.+?) \((Art|Special|Passive)\s*\|\s*(\w+)\)\s*$')
ERA = {'月银纪': '月银纪', '诸国期': '月银纪', '萨尔维斯': '月银纪', '纷争纪': '纷争纪', '山铜纪': '山铜纪', '前传': '前传'}


def era_of(page):
    for k, v in ERA.items():
        if page.startswith(k):
            return v
    return page.split('_')[0]


def main():
    pages = [a for a in sys.argv[1:] if not a.startswith('--')]
    apply = '--apply' in sys.argv
    for page in pages:
        files = D.page_files(page)
        cnt = collections.Counter()
        heads = []          # (文件, 行号)：## …命星 那一行
        for f in files:
            L = D.read_lines(f)
            for i, raw in enumerate(L):
                l = D.bare(raw)
                m = ANY.match(l)
                if m:
                    cnt[(m.group(2), m.group(3))] += 1
                if l.startswith('## ') and '命星' in l and '旅途' not in l:
                    heads.append((f, i))
        art = {t: n for (k, t), n in cnt.items() if k == 'Art'}
        oth = collections.Counter()
        for (k, t), n in cnt.items():
            if k != 'Art':
                oth[t] += n
        order = ['Unique', 'Legend', 'Epic', 'Rare', 'Normal']
        say = lambda d: '、'.join('%s %d' % (t, d[t]) for t in order if d.get(t))
        note = '%s这一页的技艺照全谱重判过，技艺 %d 门（%s），Special、Passive %d 颗（%s）。技艺的名字、档、归哪一门、缺哪一卷照 底稿/命星高魔化/全谱/全谱_%s.md，这一段上面数的档、列的名字是重判以前的。' % (
            MARK, sum(art.values()), say(art), sum(oth.values()), say(oth), era_of(page))
        # 只往有总说的那一处接：山铜纪、前传是 p6_stars_head.md，别的是那一页自己的星节
        tgt = [h for h in heads if os.path.basename(h[0]).startswith('p6_stars_head')] or heads[:1]
        if not tgt:
            print('%s：找不到「命星」那一节的标题' % page)
            continue
        f, i = tgt[0]
        raw = io.open(f, encoding='utf-8', newline='').read()
        crlf = '\r\n' in raw
        L = [x.rstrip('\r') for x in raw.split('\n')]
        # 节首：标题下一行到头一个 ### 、> 条目设置 或下一个 ## 以前
        j = i + 1
        while j < len(L) and not (L[j].startswith('### ') or L[j].startswith('> 条目设置') or L[j].startswith('## ')):
            j += 1
        body = L[i + 1:j]
        body = [x for x in body if MARK not in x]
        while body and not body[-1].strip():
            body.pop()
        body += ['', note, '']
        L[i + 1:j] = body
        out = ('\r\n' if crlf else '\n').join(L)
        print('%s｜%s｜%s' % (page, os.path.relpath(f, D.ROOT if hasattr(D, 'ROOT') else '.'), note[:80]))
        if apply and out != raw:
            D.safe_write(f, out)


if __name__ == '__main__':
    main()
