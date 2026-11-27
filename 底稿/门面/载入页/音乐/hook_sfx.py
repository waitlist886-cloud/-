#!/usr/bin/env python3
# 五本书里接交互音效（11-26 夜）：在翻页（换时代页）、档案展开、档案合上、换衣着、剧透开关这几处加一句 SFX('名')。
# SFX 是外壳装书时塞进书里的那一小段给的（shell.js 的 preamble），只认真人点出来的那一下，书自己初始化、原地重画不响；书单独打开（没有外壳）时没有 SFX，这几句什么也不做。
#   python -I -X utf8 底稿/门面/载入页/音乐/hook_sfx.py          加（加过的跳过，认 /*sfx*/ 这个记号）
#   python -I -X utf8 底稿/门面/载入页/音乐/hook_sfx.py --check  只看每一处找不找得到
import os
import sys

FRONT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
S = "window.SFX && SFX('%s'); /*sfx*/ "
OLD4 = [   # 月银纪、纷争纪、山铜纪、迷宫纪：几个函数是同一套写法（照锚点前头或者后头插）
    ('before', '  const e = ERAS[PI], c = e.cast', "  if (!profOpen) " + S % 'arch_open' + "\n", 'openProf'),
    ('after', 'function closeProf() {\n  if (!profOpen) return;\n', "  " + S % 'arch_close' + "\n", 'closeProf（几行的写法）'),
    ('after', 'function closeProf() { if (!profOpen) return;', ' ' + S % 'arch_close', 'closeProf（一行的写法）'),
    ('before', "pfSpr.style.backgroundPosition = (+o.dataset.o * 100 / 3) + '% 0';", S % 'cloth', '换衣着'),
]
BOOKS = {
    '小样_月银纪书': OLD4 + [('after', 'function setSpoil(v) {\n', "  if (!!v !== !!SPOIL) " + S % 'spoil' + "\n", 'setSpoil'),
                        ('after', 'function openEra(i, keep) {\n', "  if (!keep && i !== pageOpen) " + S % 'page' + "\n", 'openEra')],
    '小样_纷争纪书': OLD4 + [('after', "function setSpoil(v, splY) {          // splY：从档案里点的开关，那时候它在屏幕上多高\n", "  if (!!v !== !!SPOIL) " + S % 'spoil' + "\n", 'setSpoil'),
                        ('after', 'function openEra(i, keep) {          // keep：同一页原地重画（剧透开关切了、地图的数据后到了），滚到哪里、哪几条主线摊开着都留着\n', "  if (!keep && i !== pageOpen) " + S % 'page' + "\n", 'openEra')],
    '小样_山铜纪书': OLD4 + [('after', 'function setSpoil(v) {\n', "  if (!!v !== !!SPOIL) " + S % 'spoil' + "\n", 'setSpoil'),
                        ('after', 'function openEra(i, keep) {\n', "  if (!keep && i !== pageOpen) " + S % 'page' + "\n", 'openEra')],
    '小样_迷宫纪书': OLD4 + [('after', 'function setSpoil(v) {', ' if (!!v !== !!SPOIL) ' + S % 'spoil', 'setSpoil'),
                        ('after', 'function openEra(i, li) {\n', "  if (i !== pageOpen) " + S % 'page' + "\n", 'openEra')],
    '小样_此刻书': [('after', '  function openProf(name) {\n', "    " + S % 'arch_open' + "\n", 'openProf'),
                  ('after', '  function closeDlg(el) {', " if (el.id === 'pf' && el.classList.contains('on')) " + S % 'arch_close', 'closeDlg（档案）'),
                  ('after', '  function setOutfit(k) {          // 0 是艺术照，1 到 4 是四套衣着（拼图横排四格）\n', "    " + S % 'cloth' + "\n", 'setOutfit'),
                  ('after', '  function setSpoil(v) {', ' if (!!v !== !!SPOIL) ' + S % 'spoil', 'setSpoil'),
                  ('after', '  function openLine(id) {\n', "    " + S % 'page' + "\n", 'openLine'),
                  ('after', '  function showLand(i, ph) {\n', "    if (i !== curL) " + S % 'page' + "\n", 'showLand')],
}


def main():
    check = '--check' in sys.argv
    for d, hooks in BOOKS.items():
        p = os.path.join(FRONT, d, 'index.html')
        s = open(p, encoding='utf-8').read()
        n0 = s.count('/*sfx*/')
        for how, anchor, ins, name in hooks:
            c = s.count(anchor)
            if c == 0:
                if not name.endswith('写法）'):
                    print('  找不到', d, name)
                continue
            if c > 1:
                print('  不止一处', d, name, c)
                continue
            i = s.index(anchor)
            near = s[max(0, i - 120): i + len(anchor) + 120]
            if '/*sfx*/' in near and ins.strip()[:20] in near:
                continue
            if check:
                print('  会加', d, name)
                continue
            s = s[:i] + anchor + ins + s[i + len(anchor):] if how == 'after' else s[:i] + ins + s[i:]
        if not check:
            open(p, 'w', encoding='utf-8', newline='\n').write(s)
        print(d, '音效记号', n0, '→', s.count('/*sfx*/'))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
