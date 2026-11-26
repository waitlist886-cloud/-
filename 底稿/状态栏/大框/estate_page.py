# 家业页和魔宠坐骑的小卡（11-23 状态栏第三轮，方向稿 状态栏第三轮与势力经营_方向稿.md 第三节、第四节第 2 条）。
# 用户：“状态栏可以更多的显示比如魔宠，坐骑，产业，据点信息，玩家加入的势力相关玩法（比如如果玩家加入了联邦或者帝国，受封了什么领地爵位之类的，
# 或者关于自己建立或加入了冒险团的相关发展和信息）”“极致的堆料，给玩家顶级的体验与惊艳感”。
#
# 记录（骨架要添的原话在 第三轮/备注_家业页.md）：
#   §家业｜势力｜晨曦帝国·金鸢骑士团｜侍从→受封骑士*→旗骑士→男爵→伯爵｜功勋 340/600｜薪饷 每旬 8 索恩｜权限 …｜欠着 …
#   §家业｜冒险团｜长夜将尽·团长｜见习→营火*→风路→月桂→界钥｜名声 …｜成员 5/6 缺一名治疗｜团产 …｜对头 …｜合击 …
#   §家业｜据点｜晚灯酒馆阁楼·长期房间·二级｜设施 炉台、药柜、工作台、空、空｜住着 …｜这一旬 …
#   §家业｜产业｜下城面包坊·三成股｜进项 +12 索恩｜看店 …｜风险 …
#   §家业｜领地｜灰篱堡·灰篱男爵领｜人口 312｜粮 61/100｜治安 44/100｜工事 30/100｜设施 磨坊、瞭望塔、空｜这一季 …
#   §宠｜打嗝｜风暴亚龙·幼体｜魔宠·同行｜HP 86/120 MP 40/60 SP 50/80 架势 30/80｜羁绊 3/5 同调｜会 喷一口霜、放哨｜此刻 蹲在你肩上
#
# 做法：
# - 一张卡一条规则只认头两栏（类、名·副名），后头的栏不分势力还是领地，一律拆成一栏一行（§业 栏名 值），再照样子认：
#   带箭头的是阶梯（拆成一格一格，星号是所在的那一格），「设施」拆成格子，「栏名 数/数」是一条进度，别的是一格字。
#   所以栏多了少了、换了栏名都画得出来；各纪各势力的栏名由模型照规则写，页上照写的显示。
# - 家业页是新的一页（p-estate），页签 t-estate 排在背包后头。没有 §家业 的回复里，收卷那一条带一页空的（一句“还没有家业”），页签是灰的。
# - 魔宠和坐骑一只一行 §宠，写在 §角色 各组后头，同行页里排在队友底下一只一张小卡；队友浮栏抄 §角色 那一段时把它们一起抄了去，状态写同行的进浮栏。
# - 规则分三处插（apply_rules 里写明），另改三条现成规则的字（收卷添页签和空页，同行开页、浮栏·抄 认 §宠）。
# - 接进卡的时候 mod_page.py 的 KNOWN 要添 家业、宠，不然这两种行会被当成 MOD 的记录收进扩展页（第三轮/备注_家业页.md 第二节）。
# 用法：python -I -X utf8 estate_page.py 出规则.json 出样式.css [合并试的规则.json]
import sys
import os
import json
from urllib.parse import quote

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
R = '.rili-markdown-renderer:has(.sz-hud)'
ROW = 'div[style*="contain: layout"]'
# 11-26：@L@ 不再认行（行的 style 平台一直在改，认它整页重算），跟 make_css_frame.py 的 L 一样认每一条回复，权重照旧 (0,3,2)
L = '.rili-markdown-renderer.rili-markdown-renderer:has(.sz-hud):not(span):not(p)'
RM = '.rili-markdown-renderer:has(.era-moon)'
RS = '.rili-markdown-renderer:has(.era-strife)'
RB = '.rili-markdown-renderer:has(.era-bronze)'
RP = '.rili-markdown-renderer:has(.era-pre)'


# ---------------- 字眼：一处字写齐四纪的说法（照 make_rules_frame.py 的 LW） ----------------
def lw(w0, wm, ws, wb):
    return '<span class="lw"><span class="w0">%s</span><span class="wm">%s</span><span class="ws">%s</span><span class="wb">%s</span></span>' % (w0, wm, ws, wb)


# 迷宫纪（前传、1001 年）、月银纪、纷争纪、山铜纪
TAB_W = ('家业', '家火', '防区', '旗下')
TITLE_W = ('家业与名位', '你守着的那一堆火', '名下的防区与家当', '旗下的团与家当')
NONE_W = ('还没有家业。入了哪一方的门、拉起了自己的团、有了落脚的屋子和进项，往后都记在这一页。',
          '还没有自己的火。向哪一位王跪过、跟哪一伙人同猎、在哪里有一间屋子，往后都记在这一页。',
          '军册上还只有你一个人的名字。编进了哪一部、带着哪一队、守着哪一段，往后都记在这一页。',
          '旗下还空着。入了哪一家行会、挂起了哪一面团旗、盘下了哪一处买卖，往后都记在这一页。')
# 卡头上那个小字（类）。记录里五个类名四纪一样，页上照这一纪换
KIND_W = {
    '势力': ('势力', '效忠', '军籍', '行会与城'),
    '冒险团': ('冒险团', '猎团', '小队', '佣兵团'),
    '据点': ('据点', '落脚处', '驻地', '驻地'),
    '产业': ('产业', '生计', '私产', '买卖'),
    '领地': ('领地', '封土', '防区', '领地'),
}
KINDS = '|'.join(KIND_W)
BACK = '<label class="sz-x"><input type="radio" name="sz-tab">' + lw('返回手札', '返回长歌', '返回战记', '返回碑记') + '</label>'
CLOSE = '</ol></details></div></div></div></div></section>'
HEAD = '<div class="sz-pane-head"><i></i><b>' + lw(*TITLE_W) + '</b>' + BACK + '</div>'
PAGE_OPEN = CLOSE + '<section class="sz-page sz-pane p-estate">' + HEAD + '<div class="sz-pane-body">'
# 没有家业的回复：收卷时带一页空的（有了 .sz-es 这一页就藏）
PAGE_NONE = '<section class="sz-page sz-pane p-estate p-es0">' + HEAD + '<div class="sz-pane-body"><p class="es-none">' + lw(*NONE_W) + '</p></div></section>'
TAB = '<label class="sz-tab t-estate"><input type="radio" name="sz-tab"><i></i><b>' + lw(*TAB_W) + '</b></label>'

# ---------------- 规则 ----------------
V = r'[^｜\n"<>]'
ARROW = r'(?:→|⇒|->|＞|>|»|›)'
CARD = ('<div class="sz-es" data-k="%s"><div class="es-h"><i class="es-ic" data-n="%s"></i><small class="es-k">%s</small><b class="es-n">%s</b><em class="es-s" data-v="%s">%s</em></div>'
        '<ul class="es-b">ⓔ\n§业 %s\n</ul></div>ⓔ')
# 魔宠、坐骑：同行页里一只一张。前头收掉上一位队友（或者页头那一对空壳），后头再留一对空壳给下一位队友收
PET_OPEN = '</div></div><div class="sz-pet" data-s="$2" data-r="$3" data-w="$4"><i class="pt-a" data-n="$1"><u></u></i><div class="pt-h"><b>$1</b><small>$2</small><em class="pt-r">$3</em><em class="pt-w" data-v="$4">$4</em></div>'
PET_CLOSE = '</div><div class="sz-pz"><div>ⓔ'
PB = '<span class="sz-bar %s" style="--v:$%d;--m:$%d"><b>%s</b><em>$%d / $%d</em><span class="sz-trk"></span></span>'
PET_BARS = '<div class="pt-bars sz-res-bars">' + PB % ('hp', 5, 6, 'HP', 5, 6) + PB % ('mp', 7, 8, 'MP', 7, 8) + PB % ('sp', 9, 10, 'SP', 9, 10) + PB % ('st', 11, 12, '架势', 11, 12) + '</div>'
PET_HEAD = r'｜([^｜\n·"<>]{1,12})｜(' + V + r'{1,24})｜([^｜\n·"<>]{1,6})(?:·(' + V + r'{1,8})|)'
PET_ST = r'｜HP (\d{1,6})\/(\d{1,6}) MP (\d{1,6})\/(\d{1,6}) SP (\d{1,6})\/(\d{1,6}) 架势 (\d{1,6})\/(\d{1,6}) ?'
FB = '<i class="%s" style="--v:$%d;--m:$%d"></i>'
FNUM = '<span class="k-r"><b>%s</b><em>$%d / $%d</em></span>'
PET_FLOAT = ('</span></label><label class="sz-pfc sz-pfp" data-pet="$2" style="--hv:$5;--hm:$6"><input type="checkbox"><i class="sz-pfa" data-n="$1"></i><b class="sz-pfn">$1</b>'
             '<span class="sz-pfb">' + FB % ('hp', 5, 6) + FB % ('mp', 7, 8) + FB % ('st', 11, 12) + '</span><span class="sz-pfi"></span>'
             '<span class="sz-pfk"><b class="k-n">$1</b><u class="sz-pfm" data-v="$4"></u><small class="k-lv" data-v="$2">$2 · $3</small>'
             '<span class="k-rs">' + FNUM % ('HP', 5, 6) + FNUM % ('MP', 7, 8) + FNUM % ('SP', 9, 10) + FNUM % ('架势', 11, 12) + '</span>'
             '<span class="k-act" data-v="$13"><b>此刻</b>$13</span>ⓔ')

# 甲：排在「拆行·去句尾」前头（这时候 §家业、§宠 都还是原样的记录行）
RULES_A = [
    ('家业·无', r'/^§(?:家业|宠)｜(?:无|暂无|没有|还没有)[^｜\n]{0,12}(?:\n|$)/gm', ''),
    ('家业开页', r'/^§家业｜/m', PAGE_OPEN + 'ⓔ\n§家业｜'),
    # 一张卡：类｜名·副名｜后头几栏。类只认这五个字，写漏了类的走下一条（名字当题，不分类）
    ('家业·卡', r'/^§家业｜(' + KINDS + r')｜([^｜\n·"<>]{1,20})(?:·(' + V + r'{1,30})|)(?:｜([^\n]*)|)$/gm', CARD % ('$1', '$2', '$1', '$2', '$3', '$3', '$4')),
    ('家业·卡·没类', r'/^§家业｜([^｜\n·"<>]{1,20})(?:·(' + V + r'{1,30})|)(?:｜([^\n]*)|)$/gm', CARD % ('', '$1', '', '$1', '$2', '$2', '$3')),
    ('家业·卡·别的', r'/^§家业｜([^\n]*)$/gm', '<div class="sz-es" data-k=""><ul class="es-b">ⓔ\n§业 $1\n</ul></div>ⓔ'),
    # 魔宠、坐骑：名｜种类｜魔宠·同行｜HP a/b MP a/b SP a/b 架势 a/b｜后头几栏。状态那一栏写歪了的走第二条（没有四条，那一栏照字出）
    # 不认行首：只有魔宠没有队友的时候，同行开页那一条把页头接在头一行 §宠 前头，它就不在行首了
    ('宠', r'/§宠' + PET_HEAD + PET_ST + r'(?:｜([^\n]*)|)$/gm', PET_OPEN + PET_BARS + '<ul class="es-b">ⓔ\n§业 $13\n</ul>' + PET_CLOSE),
    ('宠·没条', r'/§宠' + PET_HEAD + r'(?:｜([^\n]*)|)$/gm', PET_OPEN + '<ul class="es-b">ⓔ\n§业 $5\n</ul>' + PET_CLOSE),
    ('宠·别的', r'/§宠｜([^\n]*)$/gm', '</div></div><div class="sz-pet" data-s="" data-r="" data-w=""><ul class="es-b">ⓔ\n§业 $1\n</ul>' + PET_CLOSE),
    # 后头几栏一栏一行（只认紧挨着 </ul> 的那一行，括号里的竖线不拆）
    ('业·拆', r'/ ?｜ ?(?![^（\n]*）)(?=[^\n]*\n<\/ul>)/g', '\n§业 '),
    # 阶梯：头一格后头紧跟一个箭头的那一行。格与格之间拿箭头隔（顿号、逗号也认），所在的那一格带星号
    ('业·阶梯', r'/^§业 (?:(?:阶梯|团阶|位阶|军阶|爵阶|位次|阶)[ ：:]|)([^ ｜\n"<→⇒＞>»›-]{1,16} ?' + ARROW + r' ?[^｜\n"<]{1,160})$/gm', '<li class="es-lad">ⓔ\n§阶 $1ⓝ阶\n</li>ⓔ'),
    ('业·设施', r'/^§业 (设施|设施格|房间|工坊|营地设施)[ ：:](' + V + r'{1,240})$/gm', '<li class="es-fac" data-k="$1"><small>$1</small><span class="es-fg">ⓔ\n§格 $2ⓝ格\n</span></li>ⓔ'),
    # 阶梯和设施那两行接着拆：箭头、逗号在这里拆，顿号由现成的「拆行·顿号」拆，行尾的记号由「拆行·去记号」拿掉
    ('阶格·拆', r'/ ?(?:→|⇒|->|＞|>|»|›|，|,) ?(?=[^\n]*ⓝ([阶格])$)/gm', '\n§$1 '),
    ('业·进度', r'/^§业 ([^ \d（(：:｜\n"<>\/]{1,8})[ ：:]?(\d{1,7}) ?[\/／] ?(\d{1,7})(' + V + r'{0,40})$/gm',
     '<li class="es-g" data-k="$1" data-m="$3" style="--v:$2;--m:$3"><small>$1</small><b>$2<i> / $3</i></b><em>$4</em><span class="es-trk"></span></li>ⓔ'),
    ('业·栏', r'/^§业 ([^ ：:｜\n"<>，。、,.；;！？]{1,8})[ ：:](?=(' + V + r'{1,8}))(' + V + r'{1,300})$/gm', '<li class="es-r" data-k="$1" data-v="$2"><small>$1</small><span>$3</span></li>ⓔ'),
    ('业·一句', r'/^§业 ?(?=([^｜\n"<>]{0,4}))([^\n]*)$/gm', '<li class="es-r nl" data-v="$1"><span>$2</span></li>ⓔ'),
]
# 乙：排在「记录兜底」前头（「拆行」那一组已经把顿号拆开、记号拿掉了）
RULES_B = [
    ('阶', r'/^§阶 ?([*＊★✦☆]?)([^*＊★✦☆\n"<>]{1,20})([*＊★✦☆]?) *$/gm', '<i data-a="$1$3"><b>$2</b></i>ⓔ'),
    ('阶·别的', r'/^§阶 ?([^\n]*)$/gm', '<i data-a=""><b>$1</b></i>ⓔ'),
    ('格·空', r'/^§格 ?(?:空一格|空着|空格|空位|空|无|待建|) *$/gm', '<i class="e"></i>ⓔ'),
    ('格', r'/^§格 ?([^\n"<>]{1,16})$/gm', '<i data-n="$1"><b>$1</b></i>ⓔ'),
    ('格·别的', r'/^§格 ?([^\n]*)$/gm', '<i data-n=""><b>$1</b></i>ⓔ'),
]
# 丙：排在「浮栏·别的行」前头（浮栏把 §角色 那一段抄到手札页头上，§宠 跟着抄了过去；改名以后认不出的由「浮栏·别的行」删掉）
RULES_C = [
    ('宠·浮·改名', r'/^§宠(?=[\s\S]*\nⓟ终)/gm', '§浮宠'),
    ('宠·浮', r'/^§浮宠' + PET_HEAD + PET_ST + r'(?=[^\n]*｜ ?此刻[ ：:](' + V + r'{1,40})|)[^\n]*$/gm', PET_FLOAT),
]
RULES = RULES_A + RULES_B + RULES_C

# 现成规则里要改的字（apply_rules 做；规则照名字找，卡里的规则没有名字就照正则找）
PARTY_OPEN_RX = r'/^§角色｜/m'                  # 同行开页：§宠 打头也开这一页（只有魔宠没有队友的时候）
PARTY_OPEN_RX_NEW = r'/^§(角色|宠)｜/m'
FLOAT_COPY_OLD = r'\n(§角色｜[\s\S]*?)\n§(?:见闻|MOD|记忆)｜'   # 浮栏·抄：从头一个 §角色 或者 §宠 抄起，到 §家业 也停
# 11-26 格式崩坏核对（底稿/收尾_11-26/格式崩坏_反馈核对.md）：原来从头一个 §角色 一直抄到 §见闻，中间夹着别的记录（打完仗写在角色后头的战斗栏、
# 战利品的 §物品、又抄了一遍的面板、一段正文）也一起抄进手札页头上，那几种行的「开页」认的是头一个，就在浮栏里开了页，整页正文和分支跟着掉进战斗、背包那一页，
# 手札页上一个字也不剩。改成只抄连着的那一串 §角色、§宠 行（中间空行不算断），碰到别的行就停；后头照旧要有 §见闻、MOD、§记忆 或 §家业（写到一半的时候先不抄）
FLOAT_COPY_NEW = r'\n(§(?:角色|宠)｜[\s\S]*?)(?=\n(?!§(?:角色|宠)|\n))[\s\S]*?\n§(?:见闻|MOD|记忆|家业)｜'
ANCHOR_A = r'/[。；\s]+(?=ⓜ)/g'                # 拆行·去句尾
ANCHOR_B = r'/^§([^｜\s]{1,8})｜([^\n]*)$(?=[\s\S]*ⓩ)/gm'   # 记录兜底
ANCHOR_C = r'/^§浮[^\n]*\n?/gm'                # 浮栏·别的行


def _rule(n, rx, rep, keep_name=True):
    r = {"name": n, "regex": rx, "replaceString": rep, "enabled": True, "messageRole": "assistant", "applyMode": "front-end"}
    if not keep_name:
        r.pop('name')
    return r


def rules():
    """这一份的二十二条，照甲、乙、丙的次序。插在哪见 apply_rules"""
    return [_rule(*x) for x in RULES]


def _find(rs, regex):
    idx = [i for i, r in enumerate(rs) if r['regex'] == regex]
    assert len(idx) == 1, ('规则对不上', regex[:60], idx)
    return idx[0]


def apply_rules(rs):
    """在整张规则表上打（rules_frame.json 那一份，或者卡里转换那一组加展开那一组）。打过的再打会停。返回 (添了几条, 改了几条)"""
    keep = 'name' in rs[0]
    assert not any(r['regex'] == RULES_A[1][1] for r in rs), '已经打过了'
    for group, anchor in ((RULES_C, ANCHOR_C), (RULES_A, ANCHOR_A), (RULES_B, ANCHOR_B)):
        i = _find(rs, anchor)
        rs[i:i] = [_rule(n, rx, rep, keep) for n, rx, rep in group]
    changed = 0
    # 收卷：背包那一枚页签后头添家业；页签前头带一页空的
    nav = [i for i, r in enumerate(rs) if '<nav class="sz-tabs">' in r['replaceString']]
    assert len(nav) == 1, nav
    s = rs[nav[0]]['replaceString']
    assert 't-estate' not in s
    a = s.index('<label class="sz-tab t-bag">')
    b = s.index('</label>', a) + len('</label>')
    s = s[:b] + TAB + s[b:]
    rs[nav[0]]['replaceString'] = s.replace('<nav class="sz-tabs">', PAGE_NONE + '<nav class="sz-tabs">')
    changed += 1
    # 同行开页：§宠 打头也开
    i = _find(rs, PARTY_OPEN_RX)
    assert rs[i]['replaceString'].endswith('<div hidden><div>§角色｜'), rs[i]['replaceString'][-60:]
    rs[i]['regex'] = PARTY_OPEN_RX_NEW
    rs[i]['replaceString'] = rs[i]['replaceString'][:-len('§角色｜')] + '§$1｜'
    changed += 1
    # 浮栏·抄
    hit = [r for r in rs if FLOAT_COPY_OLD in r['regex']]
    assert len(hit) == 1, len(hit)
    hit[0]['regex'] = hit[0]['regex'].replace(FLOAT_COPY_OLD, FLOAT_COPY_NEW)
    changed += 1
    return len(RULES), changed


# ---------------- 样式 ----------------
def _mask(body, vb='0 0 24 24', sw='1.8'):
    s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" fill="none" stroke="black" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % (vb, sw, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' ")


def _fill(body, vb='0 0 32 32'):
    s = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='%s'>%s</svg>" % (vb, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' -.,()")


TAB_ICON = _fill("<path d='M5 29V13h3V9h4v4h8V9h4v4h3v16h-8v-7a3 3 0 0 0-6 0v7z'/><path d='M15 9V1.500h8l-2.200 2.600L23 6.700h-6V9z'/>")
# 卡头的小徽：势力（盾里一颗星）、据点（屋）、产业（天平）、领地（堡）
KIND_IC = {
    '势力': '<path d="M12 2.500l8 3v6c0 5-3.500 8.500-8 10-4.500-1.500-8-5-8-10v-6z"/><path d="M12 7.500l1.300 2.700 3 .4-2.200 2.100.6 3-2.700-1.500-2.700 1.500.6-3-2.200-2.100 3-.4z" fill="black"/>',
    '据点': '<path d="M3 11.500l9-7.500 9 7.500M5.500 9.800V20h13V9.800M10 20v-6h4v6M16 5.500V3.500h2v3.600"/>',
    '产业': '<path d="M12 4v16M7.500 20h9M5 7h14M5 7l-3 7a3 3 0 006 0zM19 7l-3 7a3 3 0 006 0z"/><circle cx="12" cy="4" r="1.200" fill="black"/>',
    '领地': '<path d="M3 21V11h3V8h3v3h6V8h3v3h3v10zM10 21v-4a2 2 0 014 0v4M12 8V2.500h5l-1.500 1.800L17 6h-5"/>',
    '': '<path d="M12 3l9 9-9 9-9-9z"/>',
}
# 设施格里的小图标：照字眼认（后写的盖先写的，泛的在前）
SWORDS = '<path d="M4 4l11 11M4 4v3.500M4 4h3.500M13 17l4-4M15.500 18.500l3 3M20 4L9 15M20 4v3.500M20 4h-3.500M11 17l-4-4M8.500 18.500l-3 3"/>'
FAC = [
    ('炉|灶|火塘|壁炉|篝火', '<path d="M12 3c1 4 6 6 6 11a6 6 0 01-12 0c0-3 2-4 3-7 1 2 2 3 3 3 0-3-1-5 0-7z"/>'),
    ('药|医|疗|净化|担架|伤兵', '<path d="M9 3h6M10 3v6l-5 9a2 2 0 002 3h10a2 2 0 002-3l-5-9V3M7.500 15h9"/>'),
    ('工作台|工坊|作坊|缝|木工|工台|机关', '<path d="M14 4l6 6-3 3-6-6zM12.500 8.500L4 17l3 3 8.500-8.500"/>'),
    ('仓|库|窖|货架|封印箱|箱|粮', '<path d="M3 8l9-4 9 4v9l-9 4-9-4zM3 8l9 4 9-4M12 12v9"/>'),
    ('床|卧|宿|客房|房间|铺位|通铺|帐', '<path d="M3 18V7M3 13h18v5M21 18v-5a3 3 0 00-3-3h-7v3"/><circle cx="7" cy="10" r="1.600"/>'),
    ('书|资料|地图|桌|档案|议事|账', '<path d="M4 5a2 2 0 012-2h13v15H6a2 2 0 00-2 2zM4 20a2 2 0 002 2h13v-4M9 7h6"/>'),
    ('训练|靶|木桩|校场|演武', '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.200" fill="black"/>'),
    ('厩|兽栏|栏|巢|鹫塔', '<path d="M6 20V11a6 6 0 0112 0v9h-3v-9a3 3 0 00-6 0v9z"/>'),
    ('磨|风车|水车', '<path d="M12 12l7-7M12 12l-7 7M12 12l7 7M12 12L5 5M9 21l1-9h4l1 9z"/>'),
    ('塔|瞭望|哨|烽', '<path d="M7 21V9l-1-1V4h3v2h2V4h2v2h2V4h3v4l-1 1v12zM11 21v-4a1 1 0 012 0v4"/>'),
    ('墙|栅|垒|壕|门楼|城门|工事', '<path d="M3 20V9h3V6h3v3h6V6h3v3h3v11zM3 14h18M9 14v6M15 14v6M12 9v5"/>'),
    ('田|圃|园|垦|牧|麦|果', '<path d="M12 21v-9M12 12c0-4-3-6-7-6 0 4 3 6 7 6zM12 14c0-3 2.500-5 7-5 0 3-2.500 5-7 5z"/>'),
    ('井|水|浴|渠|泉', '<path d="M12 3c4 5 6 8 6 11a6 6 0 01-12 0c0-3 2-6 6-11z"/>'),
    ('坛|神|祭|圣|礼拜|烛', '<path d="M12 2l2.200 6.800H21l-5.600 4.100 2.100 6.900L12 15.600 6.500 19.800l2.100-6.900L3 8.800h6.800z"/>'),
    ('锻|铁匠|铸|砧', '<path d="M4 7h13a4 4 0 004-1v2a5 5 0 01-5 4h-1l1 5h3v3H7v-3h3l1-5C8 12 5 10 4 7z"/>'),
    ('酒|厨|炊|餐|饭|炉台', '<path d="M5 6h11v12a2 2 0 01-2 2H7a2 2 0 01-2-2zM16 9h2a2 2 0 012 2v3a2 2 0 01-2 2h-2M8 10v6M12 10v6"/>'),
    ('市集|集市|铺子|铺面|商铺|店|柜台|摊|钱|渡口|驿', '<circle cx="12" cy="12" r="9"/><path d="M12 7v10M15 9.500c-.6-1-1.700-1.500-3-1.500-1.700 0-3 .8-3 2s1.300 1.800 3 2 3 .8 3 2-1.300 2-3 2c-1.300 0-2.400-.5-3-1.500"/>'),
    ('锁|暗格|结界|符|警铃|后门|密', '<path d="M6 11h12v9H6zM8.500 11V8a3.500 3.500 0 017 0v3"/><circle cx="12" cy="15.500" r="1.200" fill="black"/>'),
    ('码头|船|港|栈桥', '<circle cx="12" cy="5" r="2"/><path d="M12 7v14M5 13c0 4 3 7 7 8 4-1 7-4 7-8M8 11h8"/>'),
    ('矿|坑道|采石', '<path d="M4 9c5-5 11-5 16 0M12 6v15"/>'),
    ('旗|厅|接待|会客|陈列|留言', '<path d="M6 21V4M6 5h11l-2.500 3.500L17 12H6"/>'),
    ('弩|炮|铳|军械|武器|兵器|武备|箭', SWORDS),
    ('传送|锚点|法阵|魔导', '<circle cx="12" cy="12" r="9"/><path d="M12 3l7.800 13.500H4.200z"/><path d="M12 21L4.200 7.500h15.600z"/>'),
]
PAW = '<circle cx="6.500" cy="10" r="2" fill="black"/><circle cx="10" cy="6" r="2" fill="black"/><circle cx="14" cy="6" r="2" fill="black"/><circle cx="17.500" cy="10" r="2" fill="black"/><path d="M12 11c3 0 5.500 3 5.500 5.500 0 2-1.500 3-3 3-1 0-1.700-.5-2.500-.5s-1.500.5-2.500.5c-1.500 0-3-1-3-3C6.500 14 9 11 12 11z" fill="black"/>'
STAR4 = '<path d="M12 2l2.400 7.600L22 12l-7.600 2.400L12 22l-2.400-7.600L2 12l7.600-2.400z" fill="black"/>'
KEY = '<circle cx="8" cy="12" r="4"/><path d="M12 12h9M17 12v3.500M20 12v2.500"/>'
SEAL = '<path d="M12 3a5 5 0 015 5c0 2-1 3-2 4v2h3v3H6v-3h3v-2c-1-1-2-2-2-4a5 5 0 015-5zM5 21h14"/>'
WARN = '<path d="M12 3.500l9.500 16.500h-19zM12 10v5"/><circle cx="12" cy="17.500" r=".8" fill="black"/>'
PEOPLE = '<circle cx="8.500" cy="8" r="3"/><path d="M2.500 20c.3-4 2.700-6.500 6-6.500s5.700 2.500 6 6.500"/><circle cx="17" cy="9" r="2.400"/><path d="M16 14c3 0 5 2 5.500 5.500"/>'
# 魔宠、坐骑的头像：一张 4×4 的拼图（__ART__/pets.webp，一格 128），照种类里的字认；认不出的是一枚爪印加名字头一个字
PETS = [   # (认哪些字, 列, 行)，泛的在前、细的在后
    ('马|驹|骓', 2, 1), ('龙|蜥|亚龙|飞龙|翼龙', 1, 0), ('地行|陆行|骑蜥|驮蜥|地龙', 1, 3), ('鹿|麋|麟', 2, 0), ('狼', 3, 0),
    ('鹰|隼|雕|鹞', 0, 1), ('猫|豹|狸|猞猁', 1, 1), ('驮兽|机关|铁骡|机兵', 3, 1), ('犬|狗|獒|猎犬', 0, 2), ('海|鲸|鳐|潮', 1, 2),
    ('枭|鸮|猫头鹰', 2, 2), ('狐', 3, 2), ('熊|罴', 0, 3), ('鸦|鸫|鹊|乌', 2, 3), ('羊|羚|岩羊|山羊', 3, 3), ('狮鹫|鹫', 0, 0),
]

CSS = r'''
/* ==== 家业页和魔宠坐骑（estate_page.py，11-23 状态栏第三轮） ==== */
@R@ :is(.t-estate,.p-estate){--ic:@TABIC@}
@L@:has(.t-estate input:checked) .p-estate{display:block}
@L@:has(.t-estate input:checked) .sz-prose{display:none}
@R@:has(.t-estate input:checked) .sz-page.sz-prose{display:block!important;opacity:.14;pointer-events:none;user-select:none}
@L@:has(.sz-es) .p-es0{display:none!important}
@R@:not(:has(.sz-es)) .t-estate{opacity:.42}
@R@ .es-none{margin:26px auto 30px!important;max-width:30em;padding:22px 20px;text-align:center;font-family:var(--fm-serif);font-size:14.5px;line-height:1.9;color:var(--fm-ink2);border-block:1px solid var(--fm-line);background:radial-gradient(60% 100% at 50% 0%, color-mix(in srgb, var(--fm-acc) 9%, transparent), transparent)}
@R@ .es-none::before{content:"";display:block;width:34px;height:34px;margin:0 auto 10px;opacity:.6;background:var(--fm-acc);-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}
@R@ .p-estate .sz-pane-body{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;align-items:start;grid-auto-flow:dense}
/* 两处以上的产业：据点占两行，产业在它旁边一张一张叠着，不留空当 */
@R@ .p-estate .sz-pane-body:has(.sz-es[data-k="产业"] ~ .sz-es[data-k="产业"]) .sz-es[data-k="据点"]{grid-row:span 2}

/* ---------- 一张卡：四角压一道这一纪的线，头上一枚小徽、类、名字、副名 ---------- */
@R@ .sz-es{--ec:var(--fm-acc);position:relative;grid-column:1 / -1;min-width:0;padding:16px 18px 15px;border-radius:12px;isolation:isolate;
  background:linear-gradient(150deg, color-mix(in srgb, var(--ec) 13%, transparent), transparent 44%), var(--fm-panel);
  box-shadow:inset 0 0 0 1px var(--fm-line), 0 10px 24px rgb(0 0 0 / .2);animation:es-in .4s ease-out both}
@R@ .sz-es{transition:transform .18s ease}
@R@ .sz-es:hover{transform:translateY(-2px)}
@R@ .sz-es:nth-child(2){animation-delay:.05s}
@R@ .sz-es:nth-child(3){animation-delay:.1s}
@R@ .sz-es:nth-child(n+4){animation-delay:.15s}
@keyframes es-in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@R@ .sz-es::before{content:"";position:absolute;inset:5px;z-index:-1;pointer-events:none;border-radius:8px;--l:color-mix(in srgb, var(--ec) 62%, transparent);
  background:linear-gradient(var(--l),var(--l)) left top/20px 1px no-repeat, linear-gradient(var(--l),var(--l)) left top/1px 20px no-repeat,
    linear-gradient(var(--l),var(--l)) right top/20px 1px no-repeat, linear-gradient(var(--l),var(--l)) right top/1px 20px no-repeat,
    linear-gradient(var(--l),var(--l)) left bottom/20px 1px no-repeat, linear-gradient(var(--l),var(--l)) left bottom/1px 20px no-repeat,
    linear-gradient(var(--l),var(--l)) right bottom/20px 1px no-repeat, linear-gradient(var(--l),var(--l)) right bottom/1px 20px no-repeat}
@R@ .sz-es:is([data-k="据点"],[data-k="产业"]){grid-column:auto}
@R@ .es-h{display:grid;grid-template-columns:auto minmax(0,1fr) auto;grid-template-rows:auto auto;column-gap:12px;align-items:center;margin:0 0 13px}
@R@ .es-ic{grid-row:1 / 3;position:relative;display:grid;place-items:center;width:44px;height:44px;border-radius:50%;font-style:normal;
  background:radial-gradient(circle at 50% 30%, color-mix(in srgb, var(--ec) 34%, transparent), color-mix(in srgb, var(--ec) 8%, transparent) 72%);
  box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--ec) 70%, transparent), 0 0 0 3px color-mix(in srgb, var(--ec) 12%, transparent)}
@R@ .es-ic::after{content:"";position:absolute;inset:10px;background:var(--fm-acc2);-webkit-mask:var(--g) center/contain no-repeat;mask:var(--g) center/contain no-repeat}
@R@ .es-k{grid-column:2;align-self:end;font-size:10.5px!important;letter-spacing:.24em;color:var(--ec)}
@R@ .es-n{grid-column:2;align-self:start;min-width:0;font-family:var(--fm-serif);font-size:19px!important;font-weight:700!important;line-height:1.3;letter-spacing:.08em;color:var(--fm-head)!important;overflow-wrap:anywhere}
@R@ .es-s{grid-column:3;grid-row:1 / 3;align-self:center;max-width:15em;padding:3px 12px;border-radius:999px;font-style:normal;font-size:12px;line-height:1.5;letter-spacing:.06em;text-align:center;
  color:var(--fm-head);background:color-mix(in srgb, var(--ec) 16%, transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--ec) 50%, transparent)}
@R@ .es-s[data-v=""],@R@ .sz-es[data-k=""] .es-k{display:none}
@R@ .sz-es:not(:has(.es-h))>.es-b{grid-template-columns:minmax(0,1fr)}
@R@ .sz-es:is([data-k="据点"],[data-k="产业"]) .es-h{grid-template-columns:auto minmax(0,1fr);grid-template-rows:auto auto auto}
@R@ .sz-es:is([data-k="据点"],[data-k="产业"]) .es-s{grid-column:2;grid-row:3;justify-self:start;margin-top:6px;max-width:100%}
@R@ .sz-es:is([data-k="据点"],[data-k="产业"]) .es-ic{align-self:start}

/* ---------- 卡里的栏：一栏一格，栏名在上；没栏名的一句占一整行 ---------- */
@R@ ul.es-b{list-style:none!important;margin:0!important;padding:0!important;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px 20px}
@R@ ul.es-b>li{list-style:none!important;margin:0!important;padding:0;min-width:0}
@R@ ul.es-b>li::marker{content:none}
@R@ .es-r{position:relative;font-size:13.5px;line-height:1.65;color:var(--fm-ink)}
@R@ :is(.es-r,.es-g,.es-fac)>small{display:block;margin-bottom:1px;font-size:10.5px!important;letter-spacing:.16em;color:var(--fm-acc);opacity:.92}
@R@ .es-r>span{display:block;overflow-wrap:anywhere}
@R@ .es-r.nl{grid-column:1 / -1;color:var(--fm-ink2)}
@R@ .es-r.nl[data-v=""]{display:none}
/* 这一轮只写了个「不变」：留一句话，细目在上一回写全的那一轮 */
@R@ .es-r.nl:is([data-v="不变"],[data-v="同上"],[data-v="无变化"],[data-v="未变"])>span{font-size:0}
@R@ .es-r.nl:is([data-v="不变"],[data-v="同上"],[data-v="无变化"],[data-v="未变"])>span::after{content:"这一轮没有变动，细目在上一回写全的那一轮";font-size:12.5px;letter-spacing:.04em;font-style:italic}
:is(@RM@,@RS@,@RB@) .es-r.nl:is([data-v="不变"],[data-v="同上"],[data-v="无变化"],[data-v="未变"])>span::after{content:"这一轮没有变动"}
@R@ .sz-es:is([data-k="据点"],[data-k="产业"])>ul.es-b{grid-template-columns:minmax(0,1fr)}
/* 欠着的：一枚火漆；权限：一把钥匙；风险、隐患：一枚警示；对头：两把交叉的剑；合击：一颗星 */
@R@ .es-r:is([data-k^="欠"],[data-k="义务"],[data-k^="权"],[data-k^="风险"],[data-k^="隐患"],[data-k^="对头"],[data-k^="合击"],[data-k^="成员"],[data-k^="住着"],[data-k^="看店"],[data-k^="驻守"]){padding-left:25px}
@R@ .es-r:is([data-k^="欠"],[data-k="义务"],[data-k^="权"],[data-k^="风险"],[data-k^="隐患"],[data-k^="对头"],[data-k^="合击"],[data-k^="成员"],[data-k^="住着"],[data-k^="看店"],[data-k^="驻守"])::before{content:"";position:absolute;left:0;top:3px;width:17px;height:17px;background:var(--rc, var(--fm-acc));-webkit-mask:var(--g) center/contain no-repeat;mask:var(--g) center/contain no-repeat}
@R@ .es-r:is([data-k^="欠"],[data-k="义务"]){--rc:#e0705c;--g:@SEAL@}
@R@ .es-r:is([data-k^="欠"],[data-k="义务"])>small{color:#e89a8a}
@R@ .es-r[data-k^="权"]{--g:@KEY@}
@R@ .es-r:is([data-k^="风险"],[data-k^="隐患"]){--rc:#e9b65a;--g:@WARN@}
@R@ .es-r:is([data-k^="风险"],[data-k^="隐患"])>small{color:#e9b65a}
@R@ .es-r:is([data-v^="无"],[data-v^="暂无"]):is([data-k^="风险"],[data-k^="隐患"],[data-k^="欠"],[data-k^="对头"]){opacity:.55}
@R@ .es-r[data-k^="对头"]{--rc:#e0705c;--g:@SWORDS@}
@R@ .es-r[data-k^="对头"]>small{color:#e89a8a}
@R@ .es-r[data-k^="合击"]{--rc:var(--fm-acc2);--g:@STAR4@}
@R@ .es-r[data-k^="合击"]>span{font-family:var(--fm-serif);font-weight:700;letter-spacing:.06em;color:var(--fm-head)}
@R@ .es-r:is([data-k^="成员"],[data-k^="住着"],[data-k^="看店"],[data-k^="驻守"]){--g:@PEOPLE@}
/* 这一旬、这一季出的事：一张压在卡底的小笺 */
@R@ .es-r:is([data-k^="这一"],[data-k="本旬"],[data-k="本季"],[data-k^="本旬的"],[data-k^="本季的"],[data-k="近事"],[data-k="在建"]){grid-column:1 / -1;margin-top:2px;padding:9px 14px 10px 16px;border-radius:3px 10px 10px 3px;border-left:3px solid var(--ec);font-family:var(--fm-serif);line-height:1.75;
  background:linear-gradient(100deg, color-mix(in srgb, var(--ec) 13%, transparent), transparent 88%)}
/* 进项：正的绿、负的红，数大一号 */
@R@ .es-r[data-k*="进项"]>span{font-size:19px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.35;color:var(--fm-head)}
@R@ .es-r[data-k*="进项"]:is([data-v^="+"],[data-v^="＋"])>span{color:#7fd9a0}
@R@ .es-r[data-k*="进项"]:is([data-v^="-"],[data-v^="−"],[data-v^="－"],[data-v^="亏"],[data-v^="负"])>span{color:#f0786a}
@R@ .es-r[data-k*="进项"]:is([data-v^="+"],[data-v^="＋"])>span::before{content:"▲";margin-right:6px;font-size:11px;vertical-align:2px}
@R@ .es-r[data-k*="进项"]:is([data-v^="-"],[data-v^="−"],[data-v^="－"],[data-v^="亏"],[data-v^="负"])>span::before{content:"▼";margin-right:6px;font-size:11px;vertical-align:2px}
@RP@ .es-r[data-k*="进项"]:is([data-v^="+"],[data-v^="＋"])>span{color:#2f8a54}
@RP@ .es-r[data-k*="进项"]:is([data-v^="-"],[data-v^="−"],[data-v^="－"],[data-v^="亏"],[data-v^="负"])>span{color:#b8412f}

/* ---------- 阶梯：一排节点连成一线，走过的亮、所在的发光、没到的灰 ---------- */
@R@ .es-lad{grid-column:1 / -1;display:flex!important;align-items:flex-start;margin:2px 0 4px!important;padding:6px 0 0!important}
@R@ .es-lad>i{position:relative;flex:1 1 0;min-width:0;display:grid;justify-items:center;align-content:start;row-gap:8px;font-style:normal;text-align:center;opacity:.5}
@R@ .es-lad>i::before{content:"";position:absolute;right:50%;top:8px;width:100%;height:2px;z-index:-1;background:repeating-linear-gradient(90deg, color-mix(in srgb, var(--fm-ink2) 55%, transparent) 0 5px, transparent 5px 9px)}
@R@ .es-lad>i:first-child::before{display:none}
@R@ .es-lad>i::after{content:"";order:-1;width:12px;height:12px;margin:3px 0;transform:rotate(45deg);border-radius:2px;background:var(--fm-band2, #111);box-shadow:inset 0 0 0 1.5px color-mix(in srgb, var(--fm-ink2) 80%, transparent)}
@R@ .es-lad>i>b{max-width:100%;padding:0 3px;font-size:12px!important;font-weight:500!important;line-height:1.35;letter-spacing:.04em;color:var(--fm-ink)!important;overflow-wrap:anywhere}
/* 走过的 */
@R@ .es-lad>i:has(~ i:not([data-a=""])){opacity:1}
@R@ .es-lad>i:has(~ i:not([data-a=""]))::after{background:var(--ec);box-shadow:0 0 0 1.5px color-mix(in srgb, var(--fm-acc2) 70%, transparent)}
@R@ .es-lad>i:has(~ i:not([data-a=""]))::before,@R@ .es-lad>i:not([data-a=""])::before{background:linear-gradient(90deg, color-mix(in srgb, var(--ec) 70%, transparent), var(--fm-acc2))}
@R@ .es-lad>i:has(~ i:not([data-a=""]))>b{color:var(--fm-ink2)!important}
/* 所在的 */
@R@ .es-lad>i:is(:not([data-a=""]),:only-child){opacity:1}
@R@ .es-lad>i:is(:not([data-a=""]),:only-child)::after{width:18px;height:18px;margin:0;border-radius:3px;background:linear-gradient(135deg, #fff, var(--fm-acc2) 55%, var(--ec));box-shadow:0 0 0 2px color-mix(in srgb, var(--fm-band2, #111) 80%, transparent), 0 0 0 3.5px var(--fm-acc2), 0 0 16px 2px color-mix(in srgb, var(--fm-acc2) 75%, transparent)}
@R@ .es-lad>i:is(:not([data-a=""]),:only-child)>b{padding:2px 10px;border-radius:999px;font-family:var(--fm-serif);font-size:13.5px!important;font-weight:700!important;color:var(--fm-head)!important;background:color-mix(in srgb, var(--ec) 22%, transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc2) 60%, transparent)}
@R@ .es-lad>i:is(:not([data-a=""]),:only-child)>b::before{content:"";position:absolute;left:50%;top:-5px;width:28px;height:28px;margin-left:-14px;border-radius:50%;border:1px solid var(--fm-acc2);pointer-events:none;animation:es-ping 2.6s ease-out infinite}
@keyframes es-grow{from{transform:scaleX(0)}}
@keyframes es-ping{0%{opacity:.85;transform:scale(.55)}70%,100%{opacity:0;transform:scale(1.5)}}
/* 一个也没标：都照平常的亮度 */
@R@ .es-lad:not(:has(i:not([data-a=""])))>i{opacity:.88}

/* ---------- 进度：一条；分母不过十的画成一格一格 ---------- */
@R@ .es-g{grid-column:1 / -1;display:grid!important;grid-template-columns:auto minmax(0,1fr) auto;align-items:baseline;column-gap:10px;row-gap:5px;--p:calc(min(var(--v), var(--m)) / max(var(--m), 1))}
@R@ .es-g>small{margin:0!important}
@R@ .es-g>b{grid-column:3;font-size:15px!important;font-weight:700!important;font-variant-numeric:tabular-nums;color:var(--fm-head)!important}
@R@ .es-g>b>i{font-style:normal;font-size:12px;font-weight:400;color:var(--fm-ink2)}
@R@ .es-g>em{grid-column:2;grid-row:1;min-width:0;font-style:normal;font-size:12px;color:var(--fm-ink2);overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
@R@ .es-trk{grid-column:1 / -1;position:relative;height:7px;border-radius:4px;overflow:hidden;background:color-mix(in srgb, var(--fm-ink) 13%, transparent);box-shadow:inset 0 0 0 1px rgb(0 0 0 / .18)}
@R@ .es-trk::after{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(var(--p) * 100%);border-radius:4px;transform-origin:0 50%;animation:es-grow .8s cubic-bezier(.2,.7,.3,1) both;background:linear-gradient(90deg, color-mix(in srgb, var(--ec) 55%, transparent), var(--fm-acc2));box-shadow:0 0 10px color-mix(in srgb, var(--fm-acc2) 60%, transparent)}
@R@ .es-g:is([data-m="2"],[data-m="3"],[data-m="4"],[data-m="5"],[data-m="6"],[data-m="7"],[data-m="8"],[data-m="9"],[data-m="10"]) .es-trk{height:9px;border-radius:2px;background:none;box-shadow:none;
  -webkit-mask:repeating-linear-gradient(90deg, #000 0 calc(100% / var(--m) - 4px), transparent calc(100% / var(--m) - 4px) calc(100% / var(--m))) 0 0/calc(100% + 4px) 100%;mask:repeating-linear-gradient(90deg, #000 0 calc(100% / var(--m) - 4px), transparent calc(100% / var(--m) - 4px) calc(100% / var(--m))) 0 0/calc(100% + 4px) 100%}
@R@ .es-g:is([data-m="2"],[data-m="3"],[data-m="4"],[data-m="5"],[data-m="6"],[data-m="7"],[data-m="8"],[data-m="9"],[data-m="10"]) .es-trk::before{content:"";position:absolute;inset:0;background:color-mix(in srgb, var(--fm-ink) 16%, transparent)}
@R@ .es-g:is([data-m="2"],[data-m="3"],[data-m="4"],[data-m="5"],[data-m="6"],[data-m="7"],[data-m="8"],[data-m="9"],[data-m="10"]) .es-trk::after{border-radius:0;z-index:1}

/* ---------- 设施格：一格一个小方块，空着的是虚线 ---------- */
@R@ .es-fac{grid-column:1 / -1}
@R@ .es-fg{display:grid;grid-template-columns:repeat(auto-fill,minmax(62px,1fr));gap:8px;margin-top:6px}
@R@ .es-fg>i{position:relative;display:grid;align-content:end;justify-items:center;aspect-ratio:1;min-width:0;padding:0 3px 7px;border-radius:9px;font-style:normal;
  background:linear-gradient(160deg, color-mix(in srgb, var(--ec) 16%, transparent), transparent 70%), var(--fm-slot);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--ec) 38%, transparent), 0 3px 8px rgb(0 0 0 / .18);transition:transform .16s}
@R@ .es-fg>i:hover{transform:translateY(-2px)}
@R@ .es-fg>i::before{content:"";position:absolute;left:50%;top:16%;width:40%;height:40%;margin-left:-20%;background:var(--fm-acc2);-webkit-mask:var(--g, @DIAMOND@) center/contain no-repeat;mask:var(--g, @DIAMOND@) center/contain no-repeat;filter:drop-shadow(0 1px 2px rgb(0 0 0 / .4))}
@R@ .es-fg>i>b{max-width:100%;font-size:11px!important;font-weight:500!important;line-height:1.25;letter-spacing:.02em;color:var(--fm-ink)!important;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@R@ .es-fg>i.e{background:none;box-shadow:none;border:1.5px dashed color-mix(in srgb, var(--fm-ink2) 46%, transparent);opacity:.7}
@R@ .es-fg>i.e::before{top:50%;left:50%;width:14px;height:14px;margin:-7px 0 0 -7px;-webkit-mask:none;mask:none;filter:none;opacity:.55;
  background:linear-gradient(var(--fm-ink2),var(--fm-ink2)) center/100% 1.5px no-repeat, linear-gradient(var(--fm-ink2),var(--fm-ink2)) center/1.5px 100% no-repeat}
@FAC@

/* ---------- 势力：盾徽；冒险团：一面团徽和大名字 ---------- */
@KINDIC@
@R@ .sz-es[data-k="冒险团"]{--ec:var(--fm-acc2);padding-top:18px;background:radial-gradient(120% 90% at 0% 0%, color-mix(in srgb, var(--ec) 20%, transparent), transparent 60%), linear-gradient(180deg, color-mix(in srgb, var(--ec) 7%, transparent), transparent), var(--fm-panel)}
@R@ .sz-es[data-k="冒险团"] .es-h{column-gap:16px;margin-bottom:15px}
@R@ .sz-es[data-k="冒险团"] .es-ic{width:56px;height:66px;border-radius:0;box-shadow:none;background:none;filter:drop-shadow(0 4px 8px rgb(0 0 0 / .45))}
@R@ .sz-es[data-k="冒险团"] .es-ic::before{content:"";position:absolute;inset:0;clip-path:polygon(0 0,100% 0,100% 62%,50% 100%,0 62%);background:linear-gradient(160deg, var(--fm-acc2), var(--fm-acc) 45%, color-mix(in srgb, var(--fm-acc) 45%, #000))}
@R@ .sz-es[data-k="冒险团"] .es-ic::after{content:attr(data-n);inset:3px;display:grid;place-items:start center;padding-top:9px;overflow:hidden;-webkit-mask:none;mask:none;clip-path:polygon(0 0,100% 0,100% 61%,50% 100%,0 61%);
  background:radial-gradient(circle at 50% 20%, color-mix(in srgb, var(--fm-band, #222) 78%, var(--fm-acc)), var(--fm-band2, #111));font-family:var(--fm-serif);font-size:27px;font-weight:700;line-height:1.2;letter-spacing:1em;text-indent:.5em;white-space:nowrap;color:var(--fm-acc2);text-shadow:0 0 10px color-mix(in srgb, var(--fm-acc2) 60%, transparent)}
@R@ .sz-es[data-k="冒险团"] .es-n{font-size:25px!important;letter-spacing:.2em;line-height:1.25;text-shadow:0 0 18px color-mix(in srgb, var(--fm-acc2) 45%, transparent)}
@R@ .sz-es[data-k="冒险团"] .es-n::after{content:"";display:block;width:min(100%, 260px);height:8px;margin-top:5px;background:linear-gradient(90deg, var(--fm-acc2), transparent) left center/100% 1px no-repeat, linear-gradient(90deg, var(--fm-acc2) 0 7px, transparent 7px) left center/100% 100% no-repeat;clip-path:polygon(0 50%,4px 0,8px 50%,100% 40%,100% 60%,8px 50%,4px 100%)}
@R@ .sz-es[data-k="冒险团"] .es-s{padding:4px 16px;font-family:var(--fm-serif);font-size:13.5px;font-weight:700;letter-spacing:.2em;text-indent:.2em}

/* ---------- 产业：几成股画成一圈 ---------- */
@R@ .sz-es[data-k="产业"]{--ec:color-mix(in srgb, var(--fm-acc) 70%, #7fd9a0)}
@R@ .sz-es[data-k="产业"] .es-s{position:relative;padding-left:34px}
@R@ .sz-es[data-k="产业"] .es-s::before{content:"";position:absolute;left:7px;top:50%;width:20px;height:20px;margin-top:-10px;border-radius:50%;background:conic-gradient(var(--fm-acc2) calc(var(--sh, 0) * 36deg), color-mix(in srgb, var(--fm-ink) 18%, transparent) 0);-webkit-mask:radial-gradient(circle, transparent 5px, #000 5.5px);mask:radial-gradient(circle, transparent 5px, #000 5.5px)}
@SHARES@

/* ---------- 据点 ---------- */
@R@ .sz-es[data-k="据点"]{--ec:color-mix(in srgb, var(--fm-acc) 60%, #8fc0ff)}

/* ---------- 领地：最大的一张。头上一幅地，名字压在画上；人口一个大数，粮、治安、工事各一枚刻度 ---------- */
@R@ .sz-es[data-k="领地"]{padding:0 0 16px;overflow:hidden;background:linear-gradient(180deg, color-mix(in srgb, var(--ec) 10%, transparent), transparent 50%), var(--fm-panel);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--ec) 55%, transparent), 0 14px 32px rgb(0 0 0 / .32)}
@R@ .sz-es[data-k="领地"]::before{inset:4px;z-index:1}
@R@ .sz-es[data-k="领地"] .es-h{position:relative;display:flex;flex-wrap:wrap;align-items:flex-end;align-content:flex-end;gap:2px 14px;min-height:168px;margin:0 0 16px;padding:14px 20px 14px;
  background:linear-gradient(180deg, rgb(0 0 0 / .05) 30%, color-mix(in srgb, var(--fm-band2, #111) 92%, transparent) 96%), var(--es-land, @LAND@) center 40%/cover no-repeat, linear-gradient(180deg, color-mix(in srgb, var(--fm-band, #223) 60%, var(--ec)), var(--fm-band2, #111))}
@R@ .sz-es[data-k="领地"] .es-h::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:linear-gradient(90deg, transparent, var(--fm-acc2) 20%, var(--fm-acc2) 80%, transparent)}
@R@ .sz-es[data-k="领地"] .es-ic{position:absolute;right:16px;top:14px;width:38px;height:38px;background:color-mix(in srgb, var(--fm-band2, #111) 70%, transparent);backdrop-filter:blur(3px)}
@R@ .sz-es[data-k="领地"] .es-ic::after{inset:8px}
@R@ .sz-es[data-k="领地"] .es-k{flex:1 1 100%;color:#f6e7c2;letter-spacing:.4em;text-shadow:0 1px 4px #000}
@R@ .sz-es[data-k="领地"] .es-n{font-size:28px!important;letter-spacing:.18em;line-height:1.2;color:#fff6df!important;text-shadow:0 2px 10px rgb(0 0 0 / .85), 0 0 24px rgb(0 0 0 / .6)}
@R@ .sz-es[data-k="领地"] .es-s{margin-bottom:5px;max-width:none;padding:3px 16px 3px 14px;border-radius:2px;font-family:var(--fm-serif);font-size:13px;font-weight:700;letter-spacing:.14em;color:#2a1c0c;background:linear-gradient(180deg, #f3dfa6, #cfa858);box-shadow:0 2px 6px rgb(0 0 0 / .5);clip-path:polygon(0 0,100% 0,calc(100% - 7px) 50%,100% 100%,0 100%)}
@R@ .sz-es[data-k="领地"]>ul.es-b{grid-template-columns:repeat(4,minmax(0,1fr));gap:14px 12px;margin:0 20px!important}
@R@ .sz-es[data-k="领地"] :is(.es-r,.es-fac,.es-lad){grid-column:1 / -1}
@R@ .sz-es[data-k="领地"] .es-r:is([data-k^="人口"],[data-k^="户"],[data-k^="守备"],[data-k^="兵"]),@R@ .sz-es[data-k="领地"] .es-g{grid-column:auto;display:grid!important;grid-template-columns:minmax(0,1fr);justify-items:center;align-content:start;row-gap:2px;padding:12px 6px 10px;border-radius:10px;text-align:center;background:var(--fm-slot);box-shadow:inset 0 0 0 1px var(--fm-line)}
@R@ .sz-es[data-k="领地"] .es-r:is([data-k^="人口"],[data-k^="户"],[data-k^="守备"],[data-k^="兵"])>small{order:3;margin:4px 0 0}
@R@ .sz-es[data-k="领地"] .es-r:is([data-k^="人口"],[data-k^="户"],[data-k^="守备"],[data-k^="兵"])>span{display:grid;place-items:center;min-height:50px;font-family:var(--fm-serif);font-size:25px;font-weight:700;line-height:1.15;font-variant-numeric:tabular-nums;color:var(--fm-head)}
@R@ .sz-es[data-k="领地"] .es-r:is([data-k^="人口"],[data-k^="户"],[data-k^="守备"],[data-k^="兵"])::before{content:"";width:16px;height:16px;background:var(--fm-acc);-webkit-mask:@PEOPLE@ center/contain no-repeat;mask:@PEOPLE@ center/contain no-repeat}
@R@ .sz-es[data-k="领地"] .es-g{--gc:hsl(calc(4 + var(--p) * 132) 62% 62%)}
@R@ .sz-es[data-k="领地"] .es-g>*{grid-column:1}
@R@ .sz-es[data-k="领地"] .es-g>small{order:3;margin-top:3px!important}
@R@ .sz-es[data-k="领地"] .es-g>b{order:2;grid-row:auto;margin-top:-24px;font-family:var(--fm-serif);font-size:21px!important;line-height:1.1}
@R@ .sz-es[data-k="领地"] .es-g>b>i{display:none}
@R@ .sz-es[data-k="领地"] .es-g>em{order:4;grid-row:auto;max-width:100%;font-size:11px}
@R@ .sz-es[data-k="领地"] .es-g>em:empty{display:none}
@R@ .sz-es[data-k="领地"] .es-g .es-trk{order:1;width:88px;height:44px;border-radius:0;overflow:visible;background:none;box-shadow:none;-webkit-mask:none;mask:none}
@R@ .sz-es[data-k="领地"] .es-g .es-trk::before{content:"";position:absolute;inset:0;border-radius:44px 44px 0 0;
  background:repeating-conic-gradient(from -90deg at 50% 100%, transparent 0 16.800deg, color-mix(in srgb, var(--fm-band2, #111) 85%, transparent) 16.800deg 18deg), conic-gradient(from -90deg at 50% 100%, var(--gc) calc(var(--p) * 180deg), color-mix(in srgb, var(--fm-ink) 16%, transparent) 0 180deg, transparent 0);
  -webkit-mask:radial-gradient(circle at 50% 100%, transparent 31px, #000 32px 43.500px, transparent 44px);mask:radial-gradient(circle at 50% 100%, transparent 31px, #000 32px 43.500px, transparent 44px);filter:drop-shadow(0 0 5px color-mix(in srgb, var(--gc) 50%, transparent))}
@R@ .sz-es[data-k="领地"] .es-g .es-trk::after{left:50%;top:auto;bottom:-5px;width:38px;height:10px;margin:0;border-radius:0;background:radial-gradient(circle at calc(100% - 0.5px) 50%, #fff 0 2px, var(--gc) 2.500px 4px, transparent 4.500px);box-shadow:none;filter:drop-shadow(0 0 4px var(--gc));transform-origin:0 50%;transform:rotate(calc(-180deg + var(--p) * 180deg));animation:es-needle .9s cubic-bezier(.2,.8,.3,1.1) both}
@keyframes es-needle{from{transform:rotate(-180deg)}}
@R@ .sz-es[data-k="领地"] .es-fg{grid-template-columns:repeat(auto-fill,minmax(70px,1fr))}
@LANDS@

/* ---------- 四纪的口气：卡头那个小字照这一纪换 ---------- */
@KINDW@

/* ---------- 魔宠和坐骑：同行页里排在队友底下，一只一张 ---------- */
@R@ .sz-pz{display:none}
@R@ .sz-npcs:not(:has(.sz-av input:checked)) .sz-pz + .sz-npc:not(.sz-npc ~ .sz-npc)>.sz-npc-b{display:grid}
@R@ .sz-pet{--ec:var(--fm-acc);grid-column:1 / -1;position:relative;display:grid;grid-template-columns:64px minmax(0,1fr) minmax(0,1.15fr);grid-template-rows:auto auto;column-gap:16px;row-gap:8px;align-items:center;min-width:0;margin-top:12px;padding:13px 18px 13px 14px;border-radius:38px 14px 14px 38px;
  background:linear-gradient(100deg, color-mix(in srgb, var(--ec) 17%, transparent), transparent 62%), var(--fm-panel);box-shadow:inset 0 0 0 1px var(--fm-line), 0 8px 20px rgb(0 0 0 / .2);animation:es-in .4s ease-out both}
@R@ .sz-npc ~ .sz-pet:not(.sz-pet ~ .sz-pet){margin-top:22px}
@R@ .sz-npc ~ .sz-pet:not(.sz-pet ~ .sz-pet)::before{content:"";position:absolute;left:0;right:0;top:-12px;height:1px;background:linear-gradient(90deg, transparent, var(--fm-line) 20%, var(--fm-line) 80%, transparent)}
@R@ .sz-pet[data-r*="坐骑"]{--ec:color-mix(in srgb, var(--fm-acc) 50%, #8fc0ff)}
@R@ .pt-a{grid-row:1 / 3;position:relative;display:grid;place-items:center;width:64px;height:64px;border-radius:50%;overflow:hidden;font-style:normal;
  background:radial-gradient(circle at 50% 28%, color-mix(in srgb, var(--ec) 30%, var(--fm-por1)), var(--fm-por2));
  box-shadow:0 0 0 1.5px var(--fm-acc), 0 0 0 4px color-mix(in srgb, var(--fm-band2, #111) 70%, transparent), 0 0 0 5px color-mix(in srgb, var(--ec) 45%, transparent), 0 6px 14px rgb(0 0 0 / .45)}
@R@ .pt-a::before{content:"";position:absolute;inset:14px;opacity:var(--paw, .34);background:var(--fm-acc);-webkit-mask:@PAW@ center/contain no-repeat;mask:@PAW@ center/contain no-repeat}
@R@ .pt-a>u{position:absolute;left:6%;right:6%;bottom:0;height:88%;background:var(--pet, none) var(--px, 0) var(--py, 0)/400% 400% no-repeat;filter:drop-shadow(0 2px 3px rgb(0 0 0 / .45))}
@R@ .pt-a::after{content:attr(data-n);position:relative;display:var(--init, block);width:1em;overflow:hidden;white-space:nowrap;font-family:var(--fm-serif);font-size:24px;line-height:1.2;color:var(--fm-head);text-shadow:0 1px 4px rgb(0 0 0 / .6)}
@R@ .pt-h{grid-column:2;grid-row:1;display:flex;flex-wrap:wrap;align-items:baseline;gap:3px 10px;min-width:0}
@R@ .pt-h>b{font-family:var(--fm-serif);font-size:20px!important;font-weight:700!important;letter-spacing:.08em;color:var(--fm-head)!important}
@R@ .pt-h>small{font-size:12px!important;color:var(--fm-ink2)}
@R@ .pt-h>em{font-style:normal;font-size:11.5px;line-height:20px;padding:0 9px;border-radius:10px;color:var(--fm-head);background:color-mix(in srgb, var(--ec) 20%, transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--ec) 50%, transparent)}
@R@ .pt-h>em:is(:empty,[data-v=""]){display:none}
@R@ .pt-h>.pt-w{color:var(--fm-ink2);background:color-mix(in srgb, var(--fm-ink) 9%, transparent);box-shadow:none}
@R@ .pt-h>.pt-w[data-v="同行"]{color:#bfeccf;background:rgb(80 170 120 / .2)}
@RP@ .pt-h>.pt-w[data-v="同行"]{color:#27653f}
@R@ .pt-bars{grid-column:2;grid-row:2;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px 12px}
@R@ .pt-bars .sz-bar{grid-template-columns:auto 1fr!important;grid-template-rows:auto 5px!important;row-gap:2px!important;font-size:11px!important}
@R@ .pt-bars .sz-bar>b{font-size:10.5px!important}
@R@ .pt-bars .sz-bar .sz-trk{height:5px!important}
@R@ .pt-bars .sz-bar .sz-trk::after{width:calc(min(var(--v), var(--m)) / max(var(--m), 1) * 100%)}
@R@ .sz-pet>ul.es-b{grid-column:3;grid-row:1 / 3;grid-template-columns:minmax(0,1fr);gap:6px;align-self:center;padding-left:16px!important;border-left:1px solid var(--fm-line)}
@R@ .sz-pet:not(:has(.pt-bars))>.pt-h{grid-row:1 / 3}
@R@ .sz-pet:not(:has(.pt-a)){grid-template-columns:minmax(0,1fr);border-radius:14px}
@R@ .sz-pet:not(:has(.pt-a))>ul.es-b{grid-column:1;border:0;padding:0!important}
@R@ .sz-pet .es-r{display:grid;grid-template-columns:2.6em minmax(0,1fr);column-gap:8px;font-size:13px;line-height:1.6}
@R@ .sz-pet .es-r.nl{grid-template-columns:minmax(0,1fr)}
@R@ .sz-pet .es-r>small{margin:0;line-height:21px;letter-spacing:.1em}
@R@ .sz-pet .es-g{grid-template-columns:2.6em auto minmax(0,1fr);column-gap:8px;row-gap:3px;align-items:center}
@R@ .sz-pet .es-g>small{grid-column:1}
@R@ .sz-pet .es-g>b{grid-column:2;font-size:13px!important}
@R@ .sz-pet .es-g>em{grid-column:3;font-family:var(--fm-serif);font-size:13px;font-weight:700;color:var(--fm-head)}
@R@ .sz-pet .es-g .es-trk{grid-column:2 / -1;max-width:150px}
@R@ .sz-pet .es-g[data-k^="羁绊"]{--ec:#e58fb0}
@R@ .sz-pet .es-g[data-k^="羁绊"] .es-trk::after{background:linear-gradient(90deg, #d86a96, #f6b3cc);box-shadow:none}
@PETS@
/* 进队友浮栏：状态写同行（或者没写）的那几只 */
@R@ .sz-pfc.sz-pfp:has(>.sz-pfk>.sz-pfm:is([data-v=""],[data-v="同行"])){display:grid}
@media (min-width:901px){@R@ .sz-page.sz-prose:has(.sz-pfp .sz-pfm:is([data-v=""],[data-v="同行"])){padding-right:78px}}
@R@ .sz-pfp .sz-pfa{overflow:hidden;background:radial-gradient(circle at 50% 28%, var(--fm-por1), var(--fm-por2));box-shadow:0 0 0 1.5px color-mix(in srgb, var(--fm-acc) 60%, #8fc0ff), 0 0 0 4px color-mix(in srgb, var(--fm-base, #0d0d2a) 80%, transparent), 0 6px 14px rgb(0 0 0 / .5)}
@R@ .sz-pfp .sz-pfa{width:40px;height:40px;margin:4px 0}
@R@ .sz-pfp .sz-pfa::after{content:"";position:absolute;left:6%;right:6%;bottom:0;height:88%;background:var(--pet, none) var(--px, 0) var(--py, 0)/400% 400% no-repeat}
@R@ .sz-pfp .sz-pfa::before{font-size:17px}
@R@ .sz-pfp .sz-pfk .k-lv{display:block}

/* ---------- 前传：页是深底，卡做成一张一张贴在上头的浅色委托单 ---------- */
@RP@ :is(.sz-es,.sz-pet){background:linear-gradient(150deg, color-mix(in srgb, var(--ec) 13%, transparent), transparent 44%), linear-gradient(180deg, #f3ead3, #e6d8b8);box-shadow:inset 0 0 0 1px rgb(120 80 40 / .38), 0 10px 22px rgb(0 0 0 / .4)}
@RP@ .sz-es[data-k="领地"]{background:linear-gradient(180deg, #f3ead3, #e6d8b8)}
@RP@ .sz-es[data-k="冒险团"]{background:radial-gradient(120% 90% at 0% 0%, color-mix(in srgb, var(--ec) 24%, transparent), transparent 60%), linear-gradient(180deg, #f3ead3, #e6d8b8)}
@RP@ .p-estate .sz-pane-head b{color:#f3e6cc!important}
@RP@ .p-estate .sz-x,@RP@ .es-none{color:#d9c8a6}
@RP@ .es-ic::after,@RP@ .es-fg>i::before{background:var(--fm-acc)}
@RP@ .es-lad>i::after{background:#f3ead3}
@RP@ .es-lad>i:is(:not([data-a=""]),:only-child)::after{box-shadow:0 0 0 2px #f3ead3, 0 0 0 3.500px var(--fm-acc), 0 0 14px 2px color-mix(in srgb, var(--fm-acc2) 75%, transparent)}
@RP@ .es-r:is([data-k^="欠"],[data-k="义务"],[data-k^="对头"]){--rc:#b8412f}
@RP@ .es-r:is([data-k^="欠"],[data-k="义务"],[data-k^="对头"])>small{color:#b8412f}
@RP@ .es-r:is([data-k^="风险"],[data-k^="隐患"]){--rc:#9a6a12}
@RP@ .es-r:is([data-k^="风险"],[data-k^="隐患"])>small{color:#9a6a12}
@RP@ .sz-es[data-k="领地"] .es-g{--gc:hsl(calc(4 + var(--p) * 132) 58% 42%)}
@RP@ .sz-es[data-k="冒险团"] .es-n{text-shadow:none}
@RP@ .pt-a{box-shadow:0 0 0 1.500px var(--fm-acc), 0 0 0 4px #f3ead3, 0 0 0 5px color-mix(in srgb, var(--ec) 45%, transparent), 0 6px 14px rgb(0 0 0 / .3)}

/* ---------- 手机 ---------- */
@media (max-width:639px){
  @R@ .p-estate .sz-pane-body{grid-template-columns:minmax(0,1fr);gap:12px}
  @R@ .p-estate .sz-pane-body .sz-es[data-k="据点"]{grid-row:auto!important}
  @R@ .sz-es{padding:14px 13px 13px}
  @R@ ul.es-b{gap:10px 14px}
  @R@ .es-n{font-size:17px!important}
  @R@ .es-s{grid-column:2 / -1;grid-row:3;justify-self:start;margin-top:5px;max-width:100%}
  @R@ .es-ic{grid-row:1 / 3}
  @R@ .es-lad>i>b{font-size:11px!important;padding:0 1px}
  @R@ .es-lad>i:is(:not([data-a=""]),:only-child)>b{font-size:12px!important;padding:2px 6px}
  @R@ .es-lad:has(>i:nth-child(6))>i:not(:is(:not([data-a=""]),:only-child))>b{font-size:10.5px!important;writing-mode:vertical-rl;letter-spacing:.08em}
  @R@ .sz-es[data-k="冒险团"] .es-n{font-size:21px!important;letter-spacing:.14em}
  @R@ .sz-es[data-k="冒险团"] .es-ic{width:46px;height:56px}
  @R@ .sz-es[data-k="冒险团"] .es-ic::after{font-size:22px;padding-top:7px}
  @R@ .sz-es[data-k="领地"] .es-h{min-height:136px;padding:12px 14px}
  @R@ .sz-es[data-k="领地"] .es-n{font-size:23px!important}
  @R@ .sz-es[data-k="领地"] .es-s{grid-row:auto}
  @R@ .sz-es[data-k="领地"]>ul.es-b{grid-template-columns:repeat(2,minmax(0,1fr));margin:0 13px!important;gap:10px}
  @R@ .es-fg{grid-template-columns:repeat(auto-fill,minmax(56px,1fr));gap:7px}
  @R@ .sz-pet{grid-template-columns:52px minmax(0,1fr);column-gap:12px;padding:12px 13px 12px 11px;border-radius:32px 14px 14px 14px}
  @R@ .pt-a{width:52px;height:52px;grid-row:1 / 3;align-self:start}
  @R@ .pt-h>b{font-size:18px!important}
  @R@ .sz-pet>ul.es-b{grid-column:1 / -1;grid-row:3;padding:9px 0 0!important;border-left:0;border-top:1px solid var(--fm-line)}
  @R@ .sz-pfp .sz-pfa{width:30px;height:30px;margin:0}
  @R@ .sz-pfp .sz-pfa::before{font-size:14px}
}
/* 同行页在窄屏上是横着滑的一排头像，魔宠那几张跟队友的那一栏一样钉在左边、占满一屏宽 */
@media (max-width:899px){@R@ .sz-npcs>.sz-pet{position:sticky;left:0;width:100cqw;max-width:calc(100vw - 44px)}}
@media (prefers-reduced-motion:reduce){@R@ :is(.sz-es,.sz-pet,.es-lad>i>b::before,.es-trk::after){animation:none!important;transition:none!important}}
'''

# 几成股：十分之几
SHARES = [('一成', 1), ('两成', 2), ('二成', 2), ('三成', 3), ('四成', 4), ('五成', 5), ('半', 5), ('六成', 6), ('七成', 7), ('八成', 8), ('九成', 9), ('全', 10), ('独', 10), ('十成', 10)]
# 领地头上那幅地：一纪一张（__ART__/land_<纪>.webp），没有图的时候是一道山线
LAND_SVG = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 200' preserveAspectRatio='none'><path d='M0 150L90 96l70 38 96-78 84 62 60-30 90 50 80-70 110 84 120-50V200H0z' fill='rgb(255 255 255 / .07)'/>"
            "<path d='M0 176l120-44 90 26 130-52 100 46 96-30 120 44 144-36V200H0z' fill='rgb(0 0 0 / .28)'/></svg>")
LAND = 'url("data:image/svg+xml,%s")' % quote(LAND_SVG, safe="/:=' -.,()")
LANDS = [(R, 'maze'), (RM, 'moon'), (RS, 'strife'), (RB, 'bronze'), (RP, 'pre')]


def css(art=True):
    """art=False：不引图（魔宠头像、领地的画都用样式顶上）"""
    out = CSS
    fac = []
    for words, body in FAC:
        sel = ','.join('@R@ .es-fg>i[data-n*="%s"]' % w for w in words.split('|'))
        fac.append(sel + '{--g:%s}' % _mask(body))
    kic = ['@R@ .sz-es .es-ic{--g:%s}' % _mask(KIND_IC[''])]
    for k, body in KIND_IC.items():
        if k:
            kic.append('@R@ .sz-es[data-k="%s"] .es-ic{--g:%s}' % (k, _mask(body)))
    shares = ['@R@ .sz-es[data-k="产业"] .es-s[data-v*="%s"]{--sh:%d}' % s for s in SHARES]
    # 类的小字：记录里五个类名四纪一样，页上照这一纪换（把原字缩没，用 ::after 写）
    kw = []
    for k, ws in KIND_W.items():
        for pre, w in zip((RM, RS, RB), ws[1:]):
            if w != ws[0]:
                kw.append('%s .sz-es[data-k="%s"] .es-k{font-size:0!important}' % (pre, k))
                kw.append('%s .sz-es[data-k="%s"] .es-k::after{content:"%s";font-size:10.5px}' % (pre, k, w))
    pets, lands = [], []
    if art:
        pets.append('@R@ :is(.sz-pet,.sz-pfp){--pet-img:url("__ART__/pets.webp")}')
        for words, col, row in PETS:
            ws = words.split('|')
            sel = ','.join(['@R@ .sz-pet[data-s*="%s"] .pt-a' % w for w in ws] + ['@R@ .sz-pfp[data-pet*="%s"] .sz-pfa' % w for w in ws])
            pets.append(sel + '{--pet:var(--pet-img);--px:%s%%;--py:%s%%;--init:none;--paw:0}' % (round(col * 100 / 3, 2), round(row * 100 / 3, 2)))
        for pre, k in LANDS:
            lands.append('%s .sz-es[data-k="领地"]{--es-land:url("__ART__/land_%s.webp")}' % (pre, k))
    for a, b in [('@FAC@', '\n'.join(fac)), ('@KINDIC@', '\n'.join(kic)), ('@SHARES@', '\n'.join(shares)), ('@KINDW@', '\n'.join(kw)), ('@PETS@', '\n'.join(pets)), ('@LANDS@', '\n'.join(lands)),
                 ('@TABIC@', TAB_ICON), ('@DIAMOND@', _mask(KIND_IC[''])), ('@PAW@', _mask(PAW)), ('@SWORDS@', _mask(SWORDS)), ('@STAR4@', _mask(STAR4)), ('@KEY@', _mask(KEY)),
                 ('@SEAL@', _mask(SEAL)), ('@WARN@', _mask(WARN)), ('@PEOPLE@', _mask(PEOPLE)), ('@LAND@', LAND),
                 ('@L@', L), ('@RM@', RM), ('@RS@', RS), ('@RB@', RB), ('@RP@', RP), ('@R@', R)]:
        out = out.replace(a, b)
    assert '@' not in out.replace('@media', '').replace('@keyframes', ''), [x for x in out.split('@')[1:] if not x.startswith(('media', 'keyframes'))][:3]
    return out.strip() + '\n'


if __name__ == '__main__':
    json.dump(rules(), open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    c = css()
    open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(c)
    print(len(RULES), '条规则（甲 %d、乙 %d、丙 %d）' % (len(RULES_A), len(RULES_B), len(RULES_C)), len(c), '字样式')
    if len(sys.argv) > 3:   # 合并试的那一份：在 rules_frame.json 上打
        rs = json.load(open(os.path.join(HERE, 'rules_frame.json'), encoding='utf-8'))
        n = len(rs)
        print('合并：添 %d 条，改 %d 条' % apply_rules(rs), n, '→', len(rs))
        json.dump(rs, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
