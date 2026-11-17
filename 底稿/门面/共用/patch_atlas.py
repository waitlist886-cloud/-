# -*- coding: utf-8 -*-
"""给四本书接上图鉴（11-17）：右上角世界之书旁边添一枚“图鉴”钮，载 common/atlas.css、atlas.js，
从图鉴里点人借那一段的名单开档案（档案盖在图鉴上面），剧透开关两边一起动。

    python -I -X utf8 底稿/门面/共用/patch_atlas.py          改四本书的 index.html（改过的跳过）
    python -I -X utf8 底稿/门面/共用/patch_atlas.py --dry    只报
每一处旧串对不上就停，不半截写盘。
"""
import os, re, sys

F = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GO = {
    '小样_月银纪书': ("'moon'", "(id) => { const i = ERAS.findIndex((x) => x.id === id); if (i >= 0) { closeProf(); openEra(i); } }"),
    '小样_纷争纪书': ("'strife'", "(id) => { closeProf(); openAt(id); }"),
    '小样_山铜纪书': ('VOL', "(id) => { const i = ERAS.findIndex((x) => x.id === id); if (i >= 0) gotoEra(i); }"),
    '小样_迷宫纪书': ("'maze'", "(id) => { closeProf(); jumpTo(id); }"),
}
MARK = '/* ---------- 图鉴（11-17）'
ICON = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'><g fill='none' stroke='%23f1e9d6' stroke-width='2.2' stroke-linejoin='round'>"
        "<rect x='12' y='10' width='27' height='37' rx='2' transform='rotate(-9 25 28)' opacity='.55'/><rect x='20' y='12' width='27' height='37' rx='2' fill='%23161820'/>"
        "<circle cx='33.5' cy='25' r='5.4'/><path d='M24.5 44.5 C26 36.5 41 36.5 42.5 44.5'/><path d='M23 16.5 H44' opacity='.5'/></g></svg>\")")
CSS = ('#atBtn{all:unset;position:absolute;right:calc(max(14px,env(safe-area-inset-right)) + 86px);top:max(8px,env(safe-area-inset-top));z-index:3;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:1px;text-shadow:0 1px 8px rgba(0,0,0,.95);transition:opacity .4s}\n'
       '#atBtn i{width:60px;height:60px;background:' + ICON + ' center/86% no-repeat;filter:drop-shadow(0 6px 14px rgba(0,0,0,.65));transition:transform .35s}\n'
       '#atBtn:hover i{transform:translateY(-2px) rotate(4deg)}\n'
       '#atBtn span{font-size:11.5px;letter-spacing:.32em;text-indent:.32em;color:var(--pale,#ece5d6)}\n'
       '#atBtn:focus-visible{outline:1px solid rgb(var(--ember,255,176,104));outline-offset:4px}\n'
       '#atBtn[hidden]{display:none}\n'
       '@media (max-width:520px),(max-height:500px){#atBtn i{width:46px;height:46px}}\n'
       '#prof.over{z-index:9}#prof.over .cgb{display:none}\n')
BTN = '<button id="atBtn" type="button" aria-label="打开图鉴"><i></i><span>图鉴</span></button>'
INC = "document.write('<link rel=\"stylesheet\" href=\"' + A('common/atlas.css') + '\"><script src=\"' + A('common/atlas.js') + '\"><\\/script>');"


def initjs(vol, go):
    return (MARK + '：common/atlas.js，一纪一本，人物点开借那一段的名单开档案 ---------- */\n'
            'function openProfAt(id, name) {      // 图鉴里点人：不开时代页，档案盖在图鉴上面\n'
            '  const i = ERAS.findIndex((x) => x.id === id); if (i < 0) return;\n'
            "  profEra = i; prof.classList.add('over'); openProf(name);\n"
            '}\n'
            "const atBtn = $('#atBtn');\n"
            'function atPos() {            // 摆在世界之书那一枚的左手边\n'
            "  const w = $('#wbBtn'), r = w ? w.getBoundingClientRect() : null, v = view.getBoundingClientRect();\n"
            "  if (r && r.width) atBtn.style.right = Math.round(v.right - r.left + 16) + 'px';\n"
            '}\n'
            'if (window.Atlas) {\n'
            '  Atlas.init({\n'
            '    vol: ' + vol + ', host: view, A: window.A,\n'
            '    spoil: () => SPOIL, setSpoil: (v) => setSpoil(v),\n'
            '    curEra: () => (pageOpen >= 0 ? ERAS[pageOpen].id : null),\n'
            '    openPerson: (id, name) => openProfAt(id, name),\n'
            '    goEra: ' + go + ',\n'
            '  }).then((a) => { if (a.missing) atBtn.hidden = true; });\n'
            "  atBtn.addEventListener('click', () => { if (typeof touched === 'function') touched(); Atlas.open(); });\n"
            "  window.addEventListener('resize', atPos); atPos(); setTimeout(atPos, 600);\n"
            '} else atBtn.hidden = true;\n')


def one(name, dry):
    p = os.path.join(F, name, 'index.html')
    s = open(p, encoding='utf-8').read()
    if MARK in s:
        print('%s 已经接过，跳过' % name)
        return
    vol, go = GO[name]

    def rep(old, new, cnt=1, where=None):
        nonlocal s
        n = s.count(old)
        if n < 1:
            raise SystemExit('%s 对不上：%s' % (name, old[:60]))
        s = s.replace(old, new, cnt)

    # 一、载 atlas.css、atlas.js
    line = re.search(r"(?m)^document\.write\('<link rel=\"stylesheet\" href=\"' \+ A\('common/codex\.css'\).*$", s)
    if not line:
        raise SystemExit(name + ' 找不到载 codex 的那一行')
    s = s[:line.end()] + '\n' + INC + s[line.end():]
    # 二、样子：接在“时代页开着就把世界之书那一枚藏起来”那一条后头，另抄一条管图鉴那一枚
    hide = re.search(r'(?m)^#view:has\(#page\.on\) #wbBtn.*$', s)
    if not hide:
        raise SystemExit(name + ' 找不到藏世界之书钮的那一条')
    s = s[:hide.end()] + '\n' + CSS + hide.group(0).replace('#wbBtn', '#atBtn') + s[hide.end():]
    # 三、钮
    b = re.search(r'<button id="wbBtn"[^>]*>.*?</button>', s, re.S)
    if not b:
        raise SystemExit(name + ' 找不到世界之书那一枚钮')
    s = s[:b.end()] + '\n  ' + BTN + s[b.end():]
    # 四、开档案：认 profEra（图鉴借的那一段）
    k = s.find('function openProf(name')
    if k < 0:
        raise SystemExit(name + ' 找不到 openProf')
    s = s[:k] + 'let profEra = -1;          // 图鉴里点开的档案：借哪一段的名单（-1 是照开着的时代页）\n' + s[k:]
    rep('  if (pageOpen < 0) return;\n  const e = ERAS[pageOpen],', '  const PI = profEra >= 0 ? profEra : pageOpen;\n  if (PI < 0) return;\n  const e = ERAS[PI],')
    rep('if (!p || pageOpen < 0 || ERAS[pageOpen] !== e) return;', 'if (!p || (profEra < 0 && (pageOpen < 0 || ERAS[pageOpen] !== e))) return;')
    c = s.find('function closeProf()')
    seg_end = s.find('\n}', c) if s[c:c + 400].count('\n') > 1 else s.find('\n', c)
    seg = s[c:seg_end]
    if "prof.classList.remove('on');" not in seg or 'if (!profOpen) prof.hidden = true;' not in seg:
        raise SystemExit(name + ' closeProf 对不上')
    seg2 = seg.replace("profOpen = false; prof.classList.remove('on');", "profOpen = false; profEra = -1; prof.classList.remove('on');", 1) \
              .replace('if (!profOpen) prof.hidden = true;', "if (!profOpen) { prof.hidden = true; prof.classList.remove('over'); }", 1)
    s = s[:c] + seg2 + s[seg_end:]
    # 五、剧透开关：图鉴跟着切
    m = re.search(r'function setSpoil\([^)]*\)\s*\{[\s\S]{0,400}?(?:if \(window\.Codex\) )?Codex\.syncSpoil\(\);', s)
    if not m:
        raise SystemExit(name + ' 找不到 setSpoil 里的 Codex.syncSpoil')
    s = s[:m.end()] + ' if (window.Atlas) Atlas.syncSpoil();' + s[m.end():]
    # 六、接上：放在主脚本最后
    e = s.rfind('</script>')          # 主脚本整段包在一个函数里（数据载齐了才跑），接在它最后那个括号里头
    if not s[:e].endswith('}
'):
        raise SystemExit(name + ' 主脚本结尾不是一个括号')
    s = s[:e - 2] + initjs(vol, go) + '}
' + s[e:]
    if dry:
        print('%s 能接（试过，没写）' % name)
        return
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print('%s 接好了' % name)


if __name__ == '__main__':
    dry = '--dry' in sys.argv
    for n in GO:
        one(n, dry)
