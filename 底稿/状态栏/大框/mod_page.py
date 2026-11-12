#!/usr/bin/env python3
# 11-12 玩家反馈：加了 MOD（身体部位、领地建设这一类）以后新栏目界面不显示。量出来的（线上那张卡的规则，六种写法）：
#   照骨架写的 §MOD 行显示得出来，可落在见闻页最底下，不好找；自造的记录名（§领地｜…）落成兜底的一行，塞在记忆页末尾；
#   角色卡里自造的一栏（§角色行｜身体部位｜…）进了「关系」小页签，默认看不见；MOD 模板里的 HTML 被拆散成一串字。
# 这一份给 MOD 单开一页（页签叫扩展，有 MOD 才出），把认不出的记录归进这一页：
#   - 转换那一组（发给模型的也走）：认不出的 § 记录转成 §MOD 行；旧版式回复里带栏名的散行转成 §MOD｜记录。
#   - 展开那一组：头一条 §MOD 前开「扩展」页；收卷的页签添一枚；角色卡里认不出的栏放进「形象」（默认那一页）。
#   - 样式：扩展页的格子、页签的图标、没有 MOD 的回复藏页签。
# 规则照正则的原文认（线上那张卡的规则没有名字），每一处必须正好命中一条。patch_pub_1112.py 和生成脚本都用这一份。

# 骨架里有的、显示层认得的记录名（1001 年那一张和四纪大框合起来）。不在这里头的就是 MOD 或者模型自造的
KNOWN = ('底座|环境|推演|评定|功能|正文|分支|话|技|起手|咏唱|战斗|敌情|战况|首领|史诗势|史诗况|史诗|面板|状态|伟业|装备|物品|能力|背包|'
         '角色签|角色话|角色行|角色细|角色攻防|角色|见闻|记忆统计|记忆|预载|MOD')
NOT_KNOWN = r'(?!(?:' + KNOWN + r')(?:｜|\n|$))'


def _r(regex, rep, mode, name):
    return {'enabled': True, 'applyMode': mode, 'messageRole': 'assistant', 'regex': regex, 'replaceString': rep, 'name': name}


# 转换那一组：排在「MOD 并行、挪到见闻后」那几条前头
CONVERT_UNKNOWN = [
    _r(r'/^§' + NOT_KNOWN + r'([^｜\s§<>]{1,12})｜([^｜\n]{1,20})｜([^\n]*)$/gm', '§MOD｜$1｜$2｜$3', 'all', 'MOD·认不出的记录·多栏'),
    _r(r'/^§' + NOT_KNOWN + r'([^｜\s§<>]{1,12})｜([^\n]*)$/gm', '§MOD｜扩展｜$1｜$2', 'all', 'MOD·认不出的记录·一栏'),
]
ANCHOR_MOVE = r'/(§MOD｜[^\n]*)\n{1,4}(?=§MOD｜)/g'            # 稳·MOD并行（转换那一组）
# 散在几处的 MOD 行并到头一处：排在「挪到见闻后」那几条以后、「拆行」以前，一条挪一处，放两条
_GATHER = r'/^([\s\S]*\n§MOD｜[^\n]*)\n((?:(?!§MOD｜)[\s\S]){1,30000})\n(§MOD｜[^\n]*)(?=\n|$)/'
CONVERT_GATHER = [
    _r(_GATHER, '$1\n$3\n$2', 'all', 'MOD·并到头一处'),
    _r(_GATHER, '$1\n$3\n$2', 'all', 'MOD·并到头一处·二'),
]
ANCHOR_SPLIT = r'/Ⓚ/g'                                         # 稳·MOD拆行（转换那一组里排在并行后头的头一条）
# 旧版式回复里带栏名的散行（MOD 的模板）：排在「转·没栏名的行」后头、「剩下的标签都拿掉」前头
CONVERT_HTML = [
    _r(r'/<div[^<>]{0,120}>\s*(?:Ⓛ|<b>)([^Ⓛ<\n]{1,20})(?:Ⓛ|<\/b>)\s*(?:<span[^<>]{0,80}>|)([^<\n]{1,600})(?:<\/span>|)\s*<\/div>(?=[\s\S]*Ⓗ)/g',
       '\n§MOD｜记录｜$1｜$2\n', 'all', 'MOD·旧版式的散行'),
]
ANCHOR_STRIP = r'/<\/?[a-zA-Z][^<>]{0,400}>(?=[\s\S]*Ⓗ)/g'    # 转·剩下的标签

BACK = '<label class="sz-x"><input type="radio" name="sz-tab">返回手札</label>'
CLOSE = '</ol></details></div></div></div></div></section>'
FRAME_OPEN = [
    _r(r'/^§MOD｜/m', CLOSE + '<section class="sz-page sz-pane p-mod"><div class="sz-pane-head"><i></i><b>扩展</b>' + BACK
       + '</div><div class="sz-pane-body">ⓔ\n§MOD｜', 'front-end', 'MOD开页'),   # §MOD 另起一行，后头「成块」那一条才认得出行首
]
ANCHOR_WRAP = r'/(§MOD｜[^\n]*)\n(?=§MOD｜)/g'                 # 稳·MOD成块·并（展开那一组）
# 成块改成一个 MOD 一块：只并 MOD 名一样的相邻几行，各块各有各的题（原来几个 MOD 挨着会并成一块、题只写头一个）
WRAP_SAME = r'/(§MOD｜([^｜\n]{1,12})｜[^\n]*)\n(?=§MOD｜\2｜)/g'

TAB = '<label class="sz-tab t-mod"><input type="radio" name="sz-tab"><i></i><b>扩展</b></label>'
ROLE_OLD = '<div class="sz-nc" data-t="关系" data-k="$1"><b class="sz-ht">$1</b>'
ROLE_NEW = '<div class="sz-nc" data-t="形象" data-k="$1"><b class="sz-ht">$1</b>'
ROLE_RX = r'/§角色行｜([^｜\n]{1,8})｜([^\n]*)/g'
ROLE_RX_NEW = r'/§角色行｜([^｜\n]{1,12})｜([^\n]*)/g'          # MOD 的栏名长一点也认

ICON = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cpath d='M4 4h10v10H4zM18 4h10v10H18zM4 18h10v10H4z"
        "M21.5 17h3v4.5H29v3h-4.5V29h-3v-4.5H17v-3h4.5z'/%3E%3C/svg%3E\")")
CSS = '\n'.join([
    '/* ==== 扩展页：MOD 的栏目单开一页（mod_page.py） ==== */',
    '@R@ :is(.t-mod,.p-mod){--ic:' + ICON + '}',
    '@L@:has(.t-mod input:checked) .p-mod{display:block}',
    '@L@:has(.t-mod input:checked) .sz-prose{display:none}',
    '@R@:has(.t-mod input:checked) .sz-page.sz-prose{display:block!important;opacity:.14;pointer-events:none;user-select:none}',
    '@L@:not(:has(.p-mod)) .t-mod{display:none!important}',
    '@R@ .p-mod .sz-pane-body{display:grid;gap:16px;align-items:start}',
    '@R@ .p-mod .sz-mods{margin:0;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}',
    '@R@ .p-mod .sz-mods>.sz-nwt{grid-column:1/-1}',
    '@R@ .p-mod .sz-modn{display:none}',
    '@R@ .p-mod .sz-card .sz-arct{white-space:pre-wrap;overflow-wrap:anywhere}',
    '@media (max-width:639px){@R@ .p-mod .sz-mods{grid-template-columns:minmax(0,1fr)}}',
])


def _find(rules, regex):
    idx = [i for i, r in enumerate(rules) if r['regex'] == regex]
    assert len(idx) == 1, ('规则对不上', regex[:60], idx)
    return idx[0]


def _strip(r, keep_name):
    r = dict(r)
    if not keep_name:
        r.pop('name', None)
    return r


def apply_rules(rules):
    """在整张规则表上打（转换那一组加展开那一组，照卡里的次序）。打过的再打会停。返回添了几条、改了几条"""
    keep_name = 'name' in rules[0]
    assert not any(r['regex'] == FRAME_OPEN[0]['regex'] for r in rules), '已经打过了'
    added = 0
    i = _find(rules, ANCHOR_STRIP)
    rules[i:i] = [_strip(r, keep_name) for r in CONVERT_HTML]
    added += len(CONVERT_HTML)
    i = _find(rules, ANCHOR_MOVE)
    rules[i:i] = [_strip(r, keep_name) for r in CONVERT_UNKNOWN]
    added += len(CONVERT_UNKNOWN)
    j = _find(rules, ANCHOR_MOVE)
    k = next(x for x in range(j, len(rules)) if rules[x]['regex'] == ANCHOR_SPLIT)
    rules[k:k] = [_strip(r, keep_name) for r in CONVERT_GATHER]
    added += len(CONVERT_GATHER)
    i = _find(rules, ANCHOR_WRAP)
    rules[i]['regex'] = WRAP_SAME
    rules[i:i] = [_strip(r, keep_name) for r in FRAME_OPEN]
    added += len(FRAME_OPEN)
    changed = 1
    # 收卷：见闻那一枚页签后头添扩展
    nav = [i for i, r in enumerate(rules) if '<nav class="sz-tabs">' in r['replaceString']]
    assert len(nav) == 1, nav
    s = rules[nav[0]]['replaceString']
    a = s.index('<label class="sz-tab t-news">')
    b = s.index('</label>', a) + len('</label>')
    assert 't-mod' not in s
    rules[nav[0]]['replaceString'] = s[:b] + TAB + s[b:]
    changed += 1
    # 角色卡里认不出的栏：放进默认那一页
    i = _find(rules, ROLE_RX)
    assert rules[i]['replaceString'].count(ROLE_OLD) == 1, rules[i]['replaceString'][:120]
    rules[i]['replaceString'] = rules[i]['replaceString'].replace(ROLE_OLD, ROLE_NEW)
    rules[i]['regex'] = ROLE_RX_NEW
    changed += 1
    return added, changed


def css(L, R):
    return CSS.replace('@L@', L).replace('@R@', R)


# 风月那一张样式里的两个前缀（make_fy_css.py 转出来的）
L_FY = 'div:not(x-x):not(.x1):not(.x2):not(.x3):where(#customized-answer:has(.sz-hud))'
R_FY = '.markdown-body:has(.sz-hud)'
# 线上那张卡（1001 年切片）样式里用的两个前缀
L_PUB = 'div[style*="contain: layout"]:has(.sz-hud):not(:has(div[style*="contain: layout"]))'
R_PUB = '.rili-markdown-renderer:has(.sz-hud)'
