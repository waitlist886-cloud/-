#!/usr/bin/env python3
# 把时代页按主线细分（共用/life.js）接进四本书的 index.html（11-20）。跑几回都一样（接过的不再接）。
#   python -I -X utf8 底稿/门面/共用/hook_life.py [月银纪 纷争纪 山铜纪 迷宫纪]
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
VOLS = {'月银纪': ('moon', '月银纪'), '纷争纪': ('strife', '纷争纪'), '山铜纪': ('bronze', '山铜纪'), '迷宫纪': ('maze', '迷宫纪')}


def hook(book):
    vol, era = VOLS[book]
    p = os.path.join(HERE, '..', '小样_%s书' % book, 'index.html')
    t = open(p, encoding='utf-8', newline='').read()
    if 'common/life.js' in t:
        print(book, '接过了')
        return
    R = [
        ("document.write('<link rel=\"stylesheet\" href=\"' + A('common/atlas.css') + '\"><script src=\"' + A('common/atlas.js') + '\"><\\/script>');",
         "document.write('<link rel=\"stylesheet\" href=\"' + A('common/atlas.css') + '\"><script src=\"' + A('common/atlas.js') + '\"><\\/script>');\n"
         "document.write('<link rel=\"stylesheet\" href=\"' + A('common/life.css') + '\"><script src=\"' + A('common/life.js') + '\"><\\/script>');      // 11-20 时代页按主线细分"),
        ("const LIFE_ANCHOR = 0;", "const LIFE_ANCHOR = 0;\n"
         "if (window.Life) { Life.bind(pgBody, () => redrawEra(), () => ERAS[pageOpen]); Life.load('%s', 'data/life.json').then(() => { if (pageOpen >= 0) redrawEra(); }); }      // 11-20 按主线细分：生卒到了再画一回" % vol),
        ("  if (e.cast.length) h += `<h2>旅伴</h2>",
         "  if (window.Life) h += Life.bar(e);      // 11-20 按主线细分：选了某一条，下面四栏照那一年分\n"
         "  const LV = window.Life ? Life.view(e, SPOIL) : null, AG = (c) => (LV ? Life.ageText(c) : '');\n"
         "  const castL = LV ? LV.cast : e.cast, meetL = LV ? LV.meet : (e.meet || []), legL = LV ? LV.legends : (e.legends || []);\n"
         "  if (castL.length) h += `<h2>旅伴</h2>"),
        ("<div class=\"cast\">` + e.cast.map((c) =>", "<div class=\"cast\">` + castL.map((c) =>"),
        ("<span>${esc(raceShow(c.race))}</span><p>${esc(c.who", "<span>${esc(raceShow(c.race))}${AG(c)}</span><p>${esc(c.who"),
        ("  if (e.meet && e.meet.length) h += `<h2>相遇</h2>", "  if (meetL.length) h += `<h2>相遇</h2>"),
        ("<ul class=\"meet\">` + e.meet.map((m) =>", "<ul class=\"meet\">` + meetL.map((m) =>"),
        ("${m.tag ? `<span>${esc(m.tag)}</span>` : ''}", "${m.tag || AG(m) ? `<span>${esc([m.tag, AG(m).replace(' · ', '')].filter(Boolean).join(' · '))}</span>` : ''}"),
        ("  if (e.legends && e.legends.length) h += `<h2>传奇</h2>", "  if (legL.length) h += `<h2>传奇</h2>"),
        ("<div class=\"cast lg\">` + e.legends.map((g) =>", "<div class=\"cast lg\">` + legL.map((g) =>"),
    ]
    import re
    m = re.search(r"^const page = \$\('#page'\), pgBody = \$\('#pg-body'\)[^\n]*\n", t, re.M)
    if m:
        t = t[:m.end()] + 'const LIFE_ANCHOR = 0;\n' + t[m.end():]
    miss = [o[:50] for o, n in R if t.count(o) != 1]
    if miss:
        print(book, '对不上：', miss)
        return
    for o, n in R:
        t = t.replace(o, n)
    # 故去那一栏接在传奇后头（传奇那一行以 + '</div>'; 收尾）
    i = t.index("  if (legL.length) h += `<h2>传奇</h2>")
    j = t.index('\n', i)
    t = t[:j + 1] + "  if (LV) h += Life.goneHTML(LV.gone, (y) => '%s ' + (y - Life.BASE.%s) + ' 年');\n" % (era, vol) + t[j + 1:]
    open(p, 'w', encoding='utf-8', newline='').write(t)
    print(book, '接上了')


if __name__ == '__main__':
    for b in (sys.argv[1:] or list(VOLS)):
        hook(b)
