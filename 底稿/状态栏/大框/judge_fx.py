# 检定对抗演出（11-23，状态栏第三轮。方向稿 状态栏第三轮与势力经营_方向稿.md 第四节第 1 条，样张 样张_第三轮/m1.png）。
# 用户看了样张又补的一句：“检定演出可以多加一些其他纬度的考量，比如dv pv atk 抗性，相关的skill，ability， 装备，专长加成这些影响因素。
# 然后美化层面能多做的更加精美，如果你需要美术资源也可以跑图片。同时注意兼顾已有的美化风格”。
#
# 记录（正文里单独一行，一轮至多两行）：
#   §判｜类·事｜出手方 位阶·能级 LVL n｜出手方的几项｜应对方 位阶·能级 LVL n｜应对方的几项｜定档｜第几颗 n｜结果｜一句后果
#   几项：一项写成「类 名或数」，顿号隔开，末尾带 ↑（这一下里帮了他）或 ↓（拖了他），持平不带记号。
# 规矩照主提示词「检定与命运骰」：先定档再看骰，骰把结果挪一格。面板不算两边的总分，只把两边拿来比的各项亮出来；
# 档位尺上定的那一格、骰子挪到的那一格、骰旁那一句（好一档、坏一档、照定的）都由样式照定档和骰点算，模型不用写，也写不歪。
#
# 规则五条（RULES），插在 make_rules_frame.py 的「技·没写完」后头、「话·冒号」「段落」前头：
#   判        十栏对得上的，展开成整张面板。两边的几项先各放进一个壳（<s>、<del>），前头留一个记号 ⓗ
#   判·简      栏对不上的（少了一边、多了一栏），只认开头的事和末尾的定档、骰、结果、后果，出一张简版
#   判·主项    ⓗ 往后看两个壳：出手方的主项属性、应对方的主项属性（两个大数），出手方的 ATK 或 MAG 对应对方的 PV（一条对冲的条）。换成 ⓘ
#   判·对      ⓘ 往后看两个壳：出手方的 Skill 对应对方的 DV，出手方的元素对应对方的抗性（两对并排的牌）
#   判·拆      两个壳里的几项一项一项拆成小标
#   判·主角    11-25 添的第六条：主角那一边挂上 jg-pc，带上种族、性别、预设的族属（有主角立绘出立绘，没有出一枚剪影，见下头「主角那一边的剪影」）
# 再对不上的 §判 行落到大框原有的「记录兜底」上，原样一行字。
# 11-25 兜底那一轮（第三轮/备注_兜底_11-25.md）：尾巴放宽（骰那一栏没写、后果没写、结果没写、末尾多一栏，见 TAIL、TAIL_S 上头的话）；
#   行首记号漏了或写成别的、半角竖线、包在反引号引号代码围栏里的，在这一组前头由 robust_rules.FRAME_REC3 那三条理顺。
# 「谁出手谁写在前头」：矛总在左、盾总在右，往后看只用认一个方向。两个壳挨着放在记号后头（样式再用格子摆到两边），往后看才不用越过别的标签。
# 「判·拆」认的是 </s>、</del> 前头还没拆的顿号，所以这一组要排在队友浮栏那一组（它也用这两个壳）后头。
# 试：python -I -X utf8 judge_fx.py [整套规则写到哪]  →  第三轮/检定演出_rules.json、第三轮/检定演出.css，印各条的量词数
# 样式：材质、线、字取 --fm- 变量，四纪自动换皮；骰子、徽记、框角、绶带是出的图（judge_art.py，一纪一套六样，out/第三轮_检定演出/art/），
#   纪元照回复里的 .era-x 认（跟 rite_css 一样），认不出的照迷宫纪，前传借山铜纪那一套。
import json
import os
import re
import sys
from urllib.parse import quote

sys.dont_write_bytecode = True
R = '.rili-markdown-renderer:has(.sz-hud)'
ERA_SEL = {'moon': '.rili-markdown-renderer:has(.era-moon)', 'strife': '.rili-markdown-renderer:has(.era-strife)',
           'bronze': '.rili-markdown-renderer:has(.era-bronze)', 'pre': '.rili-markdown-renderer:has(.era-pre)', 'maze': '.rili-markdown-renderer:has(.era-maze)'}

# ---------------- 规则 ----------------
F = r'[^｜\n"<>]'                                   # 一栏里的字
TIER = '(稳|有利|五五|不利|几乎不可能)'
MK = r'[↑↓▲▼+＋\-－−=＝]'                            # 一项末尾的记号
ATTR = '(STR|DEX|MANA|MIND|VGR|FTH)'
WHO = r' ?((' + r'[^｜\n"<> ·・]{1,12})[^｜\n"<> ]{0,16})(?: (' + F + r'{0,36})|)'    # 全名、短名（头像认它）、位阶和等级
# 11-25 尾巴放宽（栏数不够、多了的兜底，原来这几种都落成原样一行）。组号没变：定档、骰前头的字、骰点、骰后头的字、结果、后果。
#   骰那一栏整个没写、定档后头直接是结果词的：当没掷骰（样式里跟写「无」一样，出“照实力直接判”）；
#   后果那一栏没写的：照常出整张，底下不出那一句（流式写到结果那一栏时面板就出来了，样子跟写完一样，只是早一栏）；
#   简版另认两样：结果那一栏没写、骰后头直接是一句十个字以上的后果的（不出绶带）；末尾多出来的栏并进后果那一句。
# 定档认不出、只写了半截的照旧落到「记录兜底」。流式写到一半时这几样都对不上（骰那一栏不会是结果词，结果词不会过十个字），不会先闪一张简版。
RW = '大成功|大失手|大失败|暴击|打实|擦中|落空|成了|险成|差一点|没成|大成|砸了|成功|失败|命中|未中'
DICE = r'｜[ 骰：:]{0,3}(' + F + r'{0,14}?)(\d{1,2}|)([^｜\n\d"<>]{0,10})'
TAIL = (r'｜[ 定档：:]{0,4}' + TIER + F + r'{0,4}(?:' + DICE + r'|(?=｜(?:' + RW + r')(?:｜|$)))｜(' + F + r'{1,10})(?:｜(' + F + r'{1,160})|)$')
TAIL_S = (TIER + F + r'{0,4}(?:' + DICE + r'|(?=｜ ?(?:' + RW + r')' + F + r'{0,2}｜))(?:｜(' + F + r'{1,10})|(?=｜' + F + r'{11}))｜(' + F + r'{1,160}(?:｜[^\n"<>]{0,200}|))$')
HEAD = r'^§判｜ ?(?:([^｜\n·・"<>]{1,6})[·・]|)(' + F + r'{1,40})'

SHELL_L, SHELL_R = '<s class="jg-f">', '<del class="jg-f">'
CORNERS = '<i class="jg-fl"></i><i class="jg-co a"></i><i class="jg-co b"></i><i class="jg-co c"></i><i class="jg-co d"></i>'


def _tail(k):
    """档位尺、骰子、骰旁那一句、绶带、后果。k：定档那一组的组号"""
    g = lambda i: '$%d' % (k + i)
    return ('<span class="jg-tr"><i class="t1"></i><i class="t2"></i><i class="t3"></i><i class="t4"></i><i class="t5"></i><i class="jg-pt"></i></span>'
            '<span class="jg-di"><i class="jg-d20"><b>%s</b></i></span>'
            '<span class="jg-dn"><em>%s</em><u>%s</u><em>%s</em></span>'
            '<span class="jg-rb"><b>%s</b></span><span class="jg-ou">%s</span></div>ⓔ' % (g(2), g(1), g(2), g(3), g(4), g(5)))


def _who(side, k):
    return ('<span class="jg-w %s" data-portrait="$%d"><i class="jg-av" data-n="$%d"></i><b>$%d</b><small>$%d</small></span>' % (side, k + 1, k + 1, k, k + 2))


# 往后看：壳里找一项。L 是出手方那个壳，R 要先越过出手方那个壳
SEE_L = r'(?=' + SHELL_L + r'[^<\n]{0,240}?[、，,]%s|)'
SEE_R = r'(?=' + SHELL_L + r'[^<\n]{0,240}<\/s>' + SHELL_R + r'[^<\n]{0,240}?[、，,]%s|)'
NUM = r'[ ：:]?(\d{1,6})(' + MK + '?)'
TXT = r'[ ：:]?([^、，,<\n↑↓▲▼+＋－−ⓕ]{1,24})(' + MK + '?)'

RULES = [
    ('判', r'/' + HEAD + '｜' + WHO + '｜ ?(' + F + '{0,200})｜' + WHO + '｜ ?(' + F + '{0,200})' + TAIL + '/gm',
     '<div class="sz-judge" data-c="$1" data-t="$11" data-d="$13" data-o="$15">' + CORNERS
     + '<span class="jg-hd"><b>$1</b><span>$2</span></span>' + _who('l', 3) + '<i class="jg-vs"></i>' + _who('r', 7)
     + 'ⓗ' + SHELL_L + '、$6ⓕ</s>' + SHELL_R + '、$10ⓕ</del>' + _tail(11)),
    ('判·简', r'/' + HEAD + r'｜(?:[^\n"<>]{0,600}?｜|)[ 定档：:]{0,4}' + TAIL_S + '/gm',
     '<div class="sz-judge jg-s" data-c="$1" data-t="$3" data-d="$5" data-o="$7">' + CORNERS + '<span class="jg-hd"><b>$1</b><span>$2</span></span>' + _tail(3)),
    ('判·主项', r'/ⓗ(?=' + SHELL_L + ')' + SEE_L % (ATTR + NUM) + SEE_R % (ATTR + NUM) + SEE_L % ('(ATK|MAG)' + NUM) + SEE_R % ('PV' + NUM) + '/g',
     '<span class="jg-ma l" data-k="$1" data-m="$3"><b>$1</b>$2</span><span class="jg-ma r" data-k="$4" data-m="$6"><b>$4</b>$5</span>'
     '<span class="jg-x x1" data-k="$7" data-a="$8" data-b="$10" data-ma="$9" data-mb="$11" style="--a:$8;--b:$10"><b>$7 $8</b><i></i><b>PV $10</b></span>ⓘ'),
    ('判·对', r'/ⓘ(?=' + SHELL_L + ')' + SEE_L % ('(?:Skill|技能)' + TXT) + SEE_R % ('DV' + NUM) + SEE_L % ('元素' + TXT) + SEE_R % ('抗[性 ：:]{0,2}' + TXT[6:]) + '/g',
     '<span class="jg-x x2" data-a="$1" data-b="$3" data-ma="$2" data-mb="$4"><b>Skill $1</b><i></i><b>DV $3</b></span>'
     '<span class="jg-x x3" data-a="$5" data-b="$7" data-ma="$6" data-mb="$8"><b>元素 $5</b><i></i><b>抗 $7</b></span>'),
    # 一项：「类 名或数」加记号。没写类的（先手↑、站在台阶上↑）整个当名。
    # 壳的末尾有一个记号 ⓕ，只拆后头跟着它的顿号（别的模块也拿 <s>、<del> 当壳，不碰它们的）；ⓕ 自己走第二支，换成一枚空的小标（样式里不显）
    ('判·拆', r'/(?:[、，,] ?(?:([^ 、，,\n"<>：:↑↓▲▼ⓕ]{1,8})[ ：:]|)([^、，,\n"<>ⓕ]{1,40}?)(' + MK + r'?)(?=(?:[、，,][^<\n]{0,400}|)ⓕ<\/)|ⓕ(?=<\/(?:s|del)>))/g',
     '<i class="jg-c" data-k="$1" data-v="$2" data-m="$3"><b>$1</b>$2</i>'),
    # 11-25 主角那一边：名字「·」前头那一段跟 §面板｜身份 的姓名对得上的（或者那一边写的是 你、我、主角、玩家），挂上 jg-pc，
    # 种族、性别照身份那一行抄到 data-r、data-g，立绘那一行写了预设的把族属抄到 data-e。
    # 有主角立绘的（make_rules_frame.py「主角·立绘」那三条往回复里放的样式，认 .jg-w.jg-pc）出立绘的头像；没有的照种族和性别出一枚剪影，不再是名字头一个字。
    # 这时候 §面板 那几行还没展开（面板的规则排在后头），往后看认得到原文。
    ('判·主角', r'/(<span class="jg-w [lr])(" data-portrait="(?:(?:你|我|主角|玩家)"(?=[\s\S]*\n§面板｜身份｜[^｜\n]{1,30}｜([^｜\n"<>]{0,12})｜[^｜\n]{0,12}｜([^｜\n"<>]{0,6}))'
     r'|([^"]{1,12})"(?=[\s\S]*\n§面板｜身份｜\5(?:[·・（( ][^｜\n]{0,20}|)｜([^｜\n"<>]{0,12})｜[^｜\n]{0,12}｜([^｜\n"<>]{0,6}))))'
     r'(?=[\s\S]*\n§面板｜立绘｜预设·([^｜\n·<>"\s;:{}]{1,8})|)/g',
     '$1 jg-pc$2 data-r="$3$6" data-g="$4$7" data-e="$8"'),
]


def rules():
    return [{"name": n, "regex": rx, "replaceString": rep, "enabled": True, "messageRole": "assistant", "applyMode": "front-end"} for n, rx, rep in RULES]


def check():
    """量词数（平台上限二十五，惰性的那个问号也算一个）、量词套量词，照 tools/rili_bench/check_card.mjs 的数法"""
    def nested(src):
        st, i = [False], 0
        isq = lambda k: k < len(src) and (src[k] in '*+?' or (src[k] == '{' and re.match(r'\{\d', src[k:])))
        while i < len(src):
            c = src[i]
            if c == '\\':
                i += 2
                if isq(i):
                    st[-1] = True
                continue
            if c == '[':
                i += 1
                if src[i] == '^':
                    i += 1
                if src[i] == ']':
                    i += 1
                while src[i] != ']':
                    if src[i] == '\\':
                        i += 1
                    i += 1
                i += 1
                if isq(i):
                    st[-1] = True
                continue
            if c == '(':
                st.append(False)
                i += 1
                if i < len(src) and src[i] == '?':
                    i += 2
                continue
            if c == ')':
                g = st.pop()
                i += 1
                if isq(i):
                    if g:
                        return True
                    st[-1] = True
                elif g:
                    st[-1] = True
                continue
            if isq(i):
                st[-1] = True
                if src[i] == '{':
                    while src[i] != '}':
                        i += 1
                i += 1
                continue
            i += 1
        return False
    out = []
    for n, rx, rep in RULES:
        body = re.match(r'^/([\s\S]*)/([^/]*)$', rx).group(1)
        q = len(re.findall(r'[*+?]|\{\d', re.sub(r'\[(?:\\.|[^\]])*\]', 'x', body).replace('(?', '(')))
        out.append((n, q, nested(body)))
    return out


# ---------------- 样式 ----------------
def _mask(body, vb='0 0 24 24', sw='2'):
    s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" fill="none" stroke="black" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % (vb, sw, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' ")


HEART = '<path d="M12 21s-8-5-8-11a4.5 4.5 0 018-2.8A4.5 4.5 0 0120 10c0 6-8 11-8 11z"/>'
EYE = '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>'
SHIELD = '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>'
IC = {
    'gen': '<path d="M12 3l9 9-9 9-9-9z"/><path d="M12 8l4 4-4 4-4-4z" fill="black"/>',
    'str': '<path d="M3 9v6M6.5 6v12M17.5 6v12M21 9v6M6.5 12h11"/>',
    'dex': '<path d="M20 4c-7 0-12 4-13 11l-3 5M7 15c5 1 9-1 11-5M11 9v5h5"/>',
    'mana': '<path d="M12 2.5c4 5 6.5 8.5 6.5 12a6.5 6.5 0 01-13 0c0-3.5 2.5-7 6.5-12z"/><path d="M12 10.5l1.1 2.9 2.9 1.1-2.9 1.1-1.1 2.9-1.1-2.9-2.9-1.1 2.9-1.1z" fill="black"/>',
    'mind': EYE,
    'vgr': HEART,
    'fth': '<circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
    'atk': '<path d="M21 3l-1 6L9.5 19.5l-5-5L15 4z"/><path d="M4 20l3-3M3.5 13.5l7 7"/>',
    'mag': '<path d="M4 20L13.5 10.5"/><path d="M17 2.5l1.3 3.7L22 7.5l-3.7 1.3L17 12.5l-1.3-3.7L12 7.5l3.7-1.3z"/><path d="M6 5v3M4.5 6.5h3"/>',
    'pv': SHIELD + '<path d="M12 7.5v9M8 11.5h8"/>',
    'dv': '<path d="M3 8h7M2 12h5M4 16h6"/><path d="M13 6l7 6-7 6"/>',
    'res': SHIELD + '<path d="M12 8.5c1.8 2.2 2.6 3.4 2.6 4.6a2.6 2.6 0 01-5.2 0c0-1.2.8-2.4 2.6-4.6z" fill="black"/>',
    'skill': '<path d="M12 6c-2-1.5-5-2-8-1.5V18c3-.5 6 0 8 1.5 2-1.5 5-2 8-1.5V4.5C17 4 14 4.5 12 6zM12 6v13.5"/>',
    'art': '<path d="M7 4h10a2 2 0 012 2v12a2 2 0 01-2 2H7zM7 4a2 2 0 00-2 2v2h2M10.5 9h5.5M10.5 13h5.5"/>',
    'active': '<path d="M13 2L5 14h6l-1 8 8-12h-6z" fill="black"/>',
    'passive': '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="3.2" fill="black"/>',
    'star': '<path d="M12 2l2.6 6.5L21 9l-5 4.4L17.5 20 12 16.4 6.5 20 8 13.4 3 9l6.4-.5z"/>',
    'gear': '<path d="M5 13a7 7 0 0114 0v6h-5v-5h-4v5H5z"/><path d="M12 6V3M9 10h6"/>',
    'feat': '<circle cx="12" cy="9" r="5"/><path d="M9 13.5L7.5 21l4.5-2.5 4.5 2.5-1.5-7.5"/>',
    'crown': '<path d="M4 17h16l1.5-9-5 4L12 5l-4.5 7-5-4z"/><path d="M4 20.5h16"/>',
    'state': '<path d="M8 20V5M4 9l4-4 4 4M16 4v15M12 15l4 4 4-4"/>',
    'wound': HEART + '<path d="M13 8l-2.5 4h3L11 16"/>',
    'land': '<path d="M2 20l7-12 4 6 2.5-3.5L22 20z"/>',
    'prep': '<path d="M6 3h12M6 21h12M7 3c0 5 10 5 10 9s-10 4-10 9M17 3c0 5-10 5-10 9s10 4 10 9"/>',
    'rank': '<path d="M6 13l6-6 6 6M6 19l6-6 6 6"/>',
    'first': '<path d="M5 21V4M5 4h12l-3 4 3 4H5"/>',
    'crowd': '<circle cx="8" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M2.5 20c0-4 2.5-6 5.5-6s5.5 2 5.5 6M15 14.5c3.5-.5 6.5 1.5 6.5 5.5"/>',
    # 徽记里的字形（别的类）
    'talk': '<path d="M4 5h11v8H9l-4 3.5V13H4z"/><path d="M18 9h2v8h-1v3l-3.5-3H12"/>',
    'sneak': EYE + '<path d="M4 20L20 4"/>',
    'spell': '<circle cx="12" cy="12" r="9"/><path d="M12 3l7.8 13.5H4.2z"/><path d="M12 21L4.2 7.5h15.6z"/>',
    'chase': '<path d="M4 6l6 6-6 6M12 6l6 6-6 6"/>',
    'lock': '<circle cx="8" cy="8" r="4.5"/><path d="M11.2 11.2L20 20M16 16l2.5-2.5M18.5 18.5L21 16"/>',
    'will': '<path d="M12 2c1 4 6 6 6 12a6 6 0 01-12 0c0-3 2-4 3-7 1 2 2 3 3 3 0-3-1-5 0-8z"/>',
    'craft': '<path d="M14 4l6 6-3 3-6-6zM12.5 8.5L4 17l3 3 8.5-8.5"/>',
}
# 小标照「类」那个词认图形（先整词，再照字眼）；没写类的照名里的字眼
KEY_EQ = [('STR', 'str'), ('DEX', 'dex'), ('MANA', 'mana'), ('MIND', 'mind'), ('VGR', 'vgr'), ('FTH', 'fth'), ('ATK', 'atk'), ('MAG', 'mag'), ('PV', 'pv'), ('DV', 'dv'),
          ('Skill', 'skill'), ('技能', 'skill'), ('Art', 'art'), ('技艺', 'art'), ('Active', 'active'), ('主动', 'active'), ('Passive', 'passive'), ('被动', 'passive'),
          ('Special', 'star'), ('命星', 'star'), ('LVL', 'rank')]
KEY_HAS = [('抗', 'res'), ('元素', 'mana'), ('装备|主手|副手|武器|兵器|甲|盾|饰品|遗物|名器', 'gear'), ('专长', 'feat'), ('传奇', 'crown'), ('神域|权柄', 'crown'),
           ('状态|增益|减益|异常|污染', 'state'), ('伤|血|疲', 'wound'), ('地形|地势|天气|光|视野|距离', 'land'), ('准备|埋伏|情报|布置', 'prep'), ('位阶|等级|能级', 'rank'),
           ('先手|偷袭|突袭', 'first'), ('人数|队友|援|围', 'crowd'), ('职业', 'feat')]
VAL_HAS = [('先手|偷袭|突袭', 'first'), ('台阶|高处|地形|狭|雨|雪|雾|暗|夜|泥|水', 'land'), ('伤|血|疲|痛', 'wound'), ('高出|低于|位阶|等级', 'rank'), ('准备|埋伏|备好', 'prep'), ('人多|围|援', 'crowd')]
# 徽记：攻防类用剑压着盾的那一枚，别的类用空心的那一枚，里头放一个字形
CAT = [('交涉|谈判|说服|讲价|欺瞒|威吓|交易|审问', 'talk'), ('潜行|隐匿|偷|尾随|伪装', 'sneak'), ('察觉|侦查|搜索|识破|追踪|鉴', 'mind'), ('术|施法|仪式|失控|祷|咏', 'spell'),
       ('追|逃|脱身|甩', 'chase'), ('锁|机关|陷阱|拆', 'lock'), ('攀|跳|游|泅|体能|负重|角力', 'land'), ('意志|抵抗|恐|污染|诱|忍', 'will'), ('制作|锻|炼金|烹|修', 'craft')]
UP = ['↑', '▲', '+', '＋']
DN = ['↓', '▼', '-', '－', '−']
# 结果词分六等（战斗一套、别的一套），认字眼
OUT = {'gold': ['大成功', '大成'], 'hi': ['暴击', '成了', '成功'], 'mid': ['打实', '险成', '命中'], 'lo': ['擦中', '差一点'], 'no': ['落空', '没成', '失败', '未中'], 'bad': ['大失手', '大失败', '砸了']}
TIERS = ['几乎不可能', '不利', '五五', '有利', '稳']
D_UP = [str(n) for n in range(16, 21)]
D_DN = [str(n) for n in range(1, 6)]
D_MID = [''] + [str(n) for n in range(6, 16)] + ['0%d' % n for n in range(6, 10)]

RAYS = 'repeating-conic-gradient(from 0deg, color-mix(in srgb, var(--fm-glow, #f0d48c) 55%, transparent) 0 4deg, transparent 4deg 20deg)'

ERA = {
    # 图用哪一套、骰面上的数、绶带上的字、面板上叠的一层
    'maze': dict(art='maze', num='#fff4cf', nsh='0 0 9px #8fbcff, 0 1px 2px #050d36', rbt='#f8e8b0', rbs='0 1px 2px #06103a, 0 0 10px rgb(240 212 140 / .45)', rbf='#1c2f8a',
                 ov='radial-gradient(120% 60% at 50% 0%, rgb(124 124 220 / .22), transparent 70%), radial-gradient(1.2px 1.2px at 12% 20%, rgb(255 240 200 / .85), transparent), '
                    'radial-gradient(1px 1px at 84% 13%, rgb(255 240 200 / .7), transparent), radial-gradient(1.4px 1.4px at 70% 80%, rgb(255 240 200 / .6), transparent), radial-gradient(1px 1px at 27% 90%, rgb(255 240 200 / .6), transparent)'),
    'moon': dict(art='moon', num='#f4f8ff', nsh='0 0 9px #b8d0ff, 0 1px 2px #000', rbt='#1d2532', rbs='0 1px 0 rgb(255 255 255 / .55)', rbf='#c4c9d2',
                 ov='radial-gradient(1px 1px at 18% 26%, rgb(255 255 255 / .75), transparent), radial-gradient(1px 1px at 72% 62%, rgb(255 255 255 / .55), transparent), radial-gradient(1.3px 1.3px at 44% 88%, rgb(255 255 255 / .6), transparent), '
                    'radial-gradient(1px 1px at 90% 20%, rgb(255 255 255 / .6), transparent), linear-gradient(160deg, rgb(200 216 240 / .12), transparent 55%)'),
    'strife': dict(art='strife', num='#f8e6c8', nsh='0 0 7px #e0452e, 0 1px 1px #000', rbt='#6a1512', rbs='0 1px 0 rgb(255 250 235 / .5)', rbf='#e8d9b4',
                   ov='linear-gradient(90deg, transparent 13px, rgb(150 32 28 / .7) 13px, rgb(150 32 28 / .7) 14.5px, transparent 14.5px), linear-gradient(180deg, rgb(126 24 20 / .22), transparent 28%), '
                      'repeating-linear-gradient(0deg, rgb(255 255 255 / .02) 0 1px, transparent 1px 3px)'),
    'bronze': dict(art='bronze', num='#4c3012', nsh='0 1px 0 rgb(255 255 255 / .6)', rbt='#5b3a14', rbs='0 1px 0 rgb(255 255 255 / .6)', rbf='#efe6d2',
                   ov='linear-gradient(90deg, #2a2b30, #a8906e 50%, #d2ccbb) 0 0/100% 3px no-repeat, linear-gradient(90deg, #2a2b30, #a8906e 50%, #d2ccbb) 0 100%/100% 3px no-repeat, '
                      'repeating-linear-gradient(101deg, transparent 0 46px, rgb(255 255 255 / .022) 46px 47px), radial-gradient(90% 50% at 50% 0%, rgb(240 214 170 / .09), transparent 70%)'),
    'pre': dict(art='bronze', num='#4c3012', nsh='0 1px 0 rgb(255 255 255 / .6)', rbt='#5b3a14', rbs='0 1px 0 rgb(255 255 255 / .6)', rbf='#efe6d2',
                ov='repeating-linear-gradient(115deg, rgb(60 40 20 / .07) 0 1px, transparent 1px 5px), radial-gradient(90% 50% at 50% 0%, rgb(255 252 240 / .5), transparent 70%)'),
}

T = r'''
@keyframes sz-jg-enter{from{opacity:0;transform:translateY(12px) scale(.97)}to{opacity:1;transform:none}}
@keyframes sz-jg-fade{from{opacity:0}to{opacity:1}}
@keyframes sz-jg-out{from{opacity:1}to{opacity:0}}
@keyframes sz-jg-inl{from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:none}}
@keyframes sz-jg-inr{from{opacity:0;transform:translateX(26px)}to{opacity:1;transform:none}}
@keyframes sz-jg-stamp{0%{opacity:0;transform:scale(1.9) rotate(-24deg)}62%{opacity:1;transform:scale(.93) rotate(3deg)}100%{opacity:1;transform:none}}
@keyframes sz-jg-ring{0%{opacity:.95;transform:scale(.7)}100%{opacity:0;transform:scale(1.9)}}
@keyframes sz-jg-grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes sz-jg-pop{0%{opacity:0;transform:scale(.6)}100%{opacity:1;transform:none}}
@keyframes sz-jg-roll{0%{opacity:0;transform:translate(-64px,-52px) rotate(-760deg) scale(.5)}14%{opacity:1}52%{transform:translate(9px,7px) rotate(-150deg) scale(1.13)}70%{transform:translate(-4px,-9px) rotate(-40deg) scale(.96)}86%{transform:translate(1px,2px) rotate(8deg) scale(1.03)}100%{opacity:1;transform:none}}
@keyframes sz-jg-num{0%{opacity:0;transform:scale(2.2)}100%{opacity:1;transform:none}}
@keyframes sz-jg-slide{from{transform:translateX(calc((var(--t) - var(--f)) * (100% + 4px)))}to{transform:none}}
@keyframes sz-jg-unfurl{0%{opacity:0;transform:scaleX(.08) scaleY(.7)}60%{opacity:1;transform:scaleX(1.06)}100%{opacity:1;transform:none}}
@keyframes sz-jg-sweep{0%{opacity:0;transform:translateX(-130%) skewX(-18deg)}15%{opacity:1}85%{opacity:1}100%{opacity:0;transform:translateX(130%) skewX(-18deg)}}
@keyframes sz-jg-halo{0%{opacity:0;transform:scale(.3) rotate(0)}30%{opacity:.9}100%{opacity:.34;transform:scale(1) rotate(40deg)}}
@keyframes sz-jg-spin{to{transform:rotate(360deg)}}
@keyframes sz-jg-dark{0%{opacity:0}12%{opacity:1}100%{opacity:.42}}
@keyframes sz-jg-shake{0%,100%{transform:none}12%{transform:translate(-5px,2px)}28%{transform:translate(5px,-2px)}44%{transform:translate(-4px,-1px)}62%{transform:translate(3px,1px)}80%{transform:translate(-1px,0)}}
@keyframes sz-jg-glow{0%,100%{opacity:.55}50%{opacity:1}}
/* ---- 面板 ---- */
@R@ .sz-judge{--jl:var(--fm-acc2, #f0d48c);--jr:#9cc4ee;--jup:#f6d680;--jdn:#ee7362;--t:3;--s:0;--f:clamp(1, calc(var(--t) + var(--s)), 5);
position:relative;isolation:isolate;display:grid;grid-template-columns:minmax(0,1fr) 88px minmax(0,1fr);column-gap:10px;
grid-template-areas:"hd hd hd" "wl vs wr" "ml vs mr" "x1 x1 x1" "x2 x2 x2" "x3 x3 x3" "cl di cr" "tr tr tr" "dn dn dn" "rb rb rb" "ou ou ou";
max-width:600px;margin:24px auto;padding:20px 24px 16px;border-radius:12px;font-size:13px;line-height:1.5;text-indent:0;text-align:left;color:var(--fm-ink);
background:var(--jg-ov, none), linear-gradient(180deg, rgb(255 255 255 / .045), transparent 38%, rgb(0 0 0 / .16)), var(--fm-matc, #191842);
box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc) 80%, transparent), inset 0 0 0 5px rgb(0 0 0 / .16), inset 0 0 0 6px color-mix(in srgb, var(--fm-acc) 32%, transparent), 0 12px 30px rgb(0 0 0 / .42);
animation:sz-jg-enter .5s cubic-bezier(.2,.9,.3,1) both}
@R@ .sz-judge>*{position:relative;z-index:1}
@R@ .sz-judge :is(i,em,u){font-style:normal;text-decoration:none}
@R@ .jg-fl{position:absolute!important;inset:0;z-index:3!important;border-radius:12px;overflow:hidden;pointer-events:none}
@R@ .jg-fl::before,@R@ .jg-fl::after{content:"";position:absolute;inset:0;opacity:0}
@R@ .jg-co{position:absolute!important;z-index:4!important;width:72px;height:75px;background:var(--jg-cor, none) left top/contain no-repeat;pointer-events:none;filter:drop-shadow(0 2px 3px rgb(0 0 0 / .45));animation:sz-jg-fade .5s ease-out .2s both}
@R@ .jg-co.a{left:-7px;top:-7px}
@R@ .jg-co.b{right:-7px;top:-7px;transform:scaleX(-1)}
@R@ .jg-co.c{left:-7px;bottom:-7px;transform:scaleY(-1)}
@R@ .jg-co.d{right:-7px;bottom:-7px;transform:scale(-1,-1)}
/* 题：类的签，事 */
@R@ .jg-hd{grid-area:hd;display:flex;align-items:center;justify-content:center;gap:10px;min-width:0;margin:0 44px 12px}
@R@ .jg-hd::before,@R@ .jg-hd::after{content:"";flex:1;min-width:10px;height:1px;background:linear-gradient(90deg, transparent, var(--fm-acc))}
@R@ .jg-hd::after{background:linear-gradient(270deg, transparent, var(--fm-acc))}
@R@ .jg-hd b{flex:none;padding:1px 9px 1px 11px;border-radius:999px;font-size:11px!important;font-weight:700!important;line-height:18px;letter-spacing:.2em;color:var(--fm-matc, #191842)!important;background:linear-gradient(180deg, var(--fm-acc2), var(--fm-acc));box-shadow:0 0 10px color-mix(in srgb, var(--fm-glow) 40%, transparent)}
@R@ .jg-hd b:empty{display:none}
@R@ .jg-hd span{min-width:0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-family:var(--fm-serif);font-size:16px;font-weight:700;letter-spacing:.12em;color:var(--fm-head)}
/* 两边是谁 */
@R@ .jg-w{display:grid;grid-template-columns:44px minmax(0,1fr);grid-template-rows:auto auto;column-gap:10px;align-content:center;min-width:0}
@R@ .jg-w.l{grid-area:wl;--jg-sc:var(--jl);animation:sz-jg-inl .45s cubic-bezier(.2,.9,.3,1) .12s both}
@R@ .jg-w.r{grid-area:wr;--jg-sc:var(--jr);grid-template-columns:minmax(0,1fr) 44px;text-align:right;animation:sz-jg-inr .45s cubic-bezier(.2,.9,.3,1) .12s both}
@R@ .jg-av{grid-row:1 / span 2;grid-column:1;position:relative;display:grid;place-items:center;width:44px;height:44px;border-radius:50%;
background:var(--face, none) calc(var(--fx, 0) * 50%) calc(var(--fy, 0) * 50%)/var(--fsz, 300% 300%) no-repeat, radial-gradient(circle at 50% 28%, var(--fm-por1, #2a2a64), var(--fm-por2, #17163e));
box-shadow:0 0 0 1.5px var(--jg-sc), 0 0 0 4px color-mix(in srgb, var(--jg-sc) 20%, transparent), 0 4px 10px rgb(0 0 0 / .45)}
@R@ .jg-av::before{content:attr(data-n);display:var(--init, block);overflow:hidden;width:1em;height:1.2em;font-family:var(--fm-serif);font-size:19px;line-height:1.2;text-align:center;color:var(--fm-head)}
@R@ .jg-w.r .jg-av{grid-column:2}
@R@ .jg-w b{grid-row:1;grid-column:2;align-self:end;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-family:var(--fm-serif);font-size:16.5px!important;font-weight:700!important;line-height:1.4;letter-spacing:.06em;color:var(--fm-head)!important}
@R@ .jg-w small{grid-row:2;grid-column:2;align-self:start;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-size:11.5px;letter-spacing:.04em;color:var(--fm-ink2)}
@R@ .jg-w.r :is(b,small){grid-column:1}
/* 正中的徽记 */
@R@ .jg-vs{grid-area:vs;align-self:center;justify-self:center;width:88px;height:88px;background:var(--jg-vs, var(--jg-duel, none)) center/contain no-repeat, radial-gradient(closest-side, var(--fm-por2, #17163e) 68%, var(--fm-acc) 70% 76%, transparent 78%);
filter:drop-shadow(0 5px 10px rgb(0 0 0 / .5));animation:sz-jg-stamp .5s cubic-bezier(.2,1.4,.4,1) .3s both}
@R@ .jg-vs::before{content:"";position:absolute;inset:4px;border-radius:50%;border:2px solid var(--fm-glow, #f0d48c);opacity:0;animation:sz-jg-ring .8s ease-out .6s both}
@R@ .jg-vs::after{content:none;position:absolute;inset:27%;background:var(--fm-acc2);-webkit-mask:var(--jg-g) center/contain no-repeat;mask:var(--jg-g) center/contain no-repeat}
/* 主项：两个大数 */
@R@ .jg-ma{display:flex;align-items:baseline;gap:7px;margin-top:8px;font-family:var(--fm-serif);font-size:29px;font-weight:800;line-height:1;font-variant-numeric:lining-nums tabular-nums;color:var(--jg-sc);
text-shadow:0 0 16px color-mix(in srgb, var(--jg-sc) 50%, transparent), 0 1px 2px rgb(0 0 0 / .5);animation:sz-jg-fade .4s ease-out .4s both}
@R@ .jg-ma b{font-size:13px!important;font-weight:700!important;letter-spacing:.16em;color:color-mix(in srgb, var(--jg-sc) 70%, var(--fm-ink))!important}
@R@ .jg-ma.l{grid-area:ml;--jg-sc:var(--jl);justify-self:start}
@R@ .jg-ma.r{grid-area:mr;--jg-sc:var(--jr);justify-self:end}
@R@ .jg-ma[data-k=""]{display:none}
@R@ .jg-ma::after{content:none;align-self:center;font-family:sans-serif;font-size:11px;text-shadow:none}
/* 矛对盾：一条对冲的条；命中对闪避、元素对抗性：一对并排的牌 */
@R@ .jg-x{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);align-items:center;column-gap:10px;margin-top:9px;font-variant-numeric:tabular-nums;animation:sz-jg-fade .4s ease-out .5s both}
@R@ .jg-x:is([data-a=""],[data-b=""]){display:none}
@R@ .jg-x b{min-width:0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-size:13px!important;font-weight:700!important;letter-spacing:.04em;color:var(--jl)!important}
@R@ .jg-x b:last-child{text-align:right;color:var(--jr)!important}
@R@ .jg-x b::after{content:none;margin-left:4px;font-size:9px;vertical-align:1px}
@R@ .jg-x.x1{grid-area:x1;grid-template-columns:auto minmax(0,1fr) auto;--w:calc(var(--a) / (var(--a) + var(--b)))}
@R@ .jg-x.x1::before{content:"矛　对　盾";grid-column:1 / -1;margin-bottom:3px;text-align:center;font-size:10.5px;letter-spacing:.2em;color:var(--fm-ink2)}
@R@ .jg-x.x1 i{position:relative;height:10px;border-radius:5px;background:linear-gradient(180deg, color-mix(in srgb, var(--jr) 55%, #0c1018), color-mix(in srgb, var(--jr) 80%, #0c1018));box-shadow:inset 0 0 0 1px rgb(255 255 255 / .18), 0 0 10px color-mix(in srgb, var(--jr) 25%, transparent)}
@R@ .jg-x.x1 i::before{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(var(--w) * 100%);border-radius:5px 0 0 5px;background:linear-gradient(180deg, color-mix(in srgb, var(--jl) 70%, #fff), color-mix(in srgb, var(--jl) 78%, #3a1a00));
box-shadow:inset 0 0 0 1px rgb(255 255 255 / .3), 0 0 12px color-mix(in srgb, var(--jl) 45%, transparent);transform-origin:left center;animation:sz-jg-grow .6s cubic-bezier(.2,.8,.2,1) .6s both}
@R@ .jg-x.x1 i::after{content:"";position:absolute;left:calc(var(--w) * 100%);top:50%;width:13px;height:13px;margin:-6.5px 0 0 -6.5px;background:#fff;box-shadow:0 0 10px #fff, 0 0 18px var(--fm-glow, #f0d48c);transform:rotate(45deg);animation:sz-jg-fade .2s ease-out 1.15s both}
@R@ .jg-x.x2{grid-area:x2}
@R@ .jg-x.x3{grid-area:x3}
@R@ .jg-x:is(.x2,.x3) b{justify-self:start;max-width:100%;padding:2px 10px;border-radius:5px;font-size:12px!important;background:color-mix(in srgb, var(--jl) 12%, transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--jl) 45%, transparent)}
@R@ .jg-x:is(.x2,.x3) b:last-child{justify-self:end;background:color-mix(in srgb, var(--jr) 12%, transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--jr) 45%, transparent)}
@R@ .jg-x:is(.x2,.x3) i{font-size:10px;letter-spacing:.14em;white-space:nowrap;color:var(--fm-ink2)}
@R@ .jg-x.x2 i::before{content:"命中 ◆ 闪避"}
@R@ .jg-x.x3 i::before{content:"属性 ◆ 抗性"}
/* 两边的几项：小标 */
@R@ .jg-f{display:flex;flex-wrap:wrap;align-content:flex-start;gap:5px;min-width:0;margin-top:13px;font-size:0;line-height:0;text-decoration:none;color:transparent}
@R@ s.jg-f{grid-area:cl;justify-content:flex-start}
@R@ del.jg-f{grid-area:cr;justify-content:flex-end}
@R@ .jg-c{--jg-cc:var(--fm-ink2);display:inline-flex;align-items:center;gap:4px;max-width:100%;padding:2px 8px 2px 5px;border-radius:999px;font-size:11.5px;line-height:17px;letter-spacing:.02em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
color:var(--fm-ink);background:linear-gradient(0deg, var(--jg-rq, transparent), transparent 55%), var(--jg-cb, var(--fm-slot, rgb(255 255 255 / .05)));box-shadow:inset 0 0 0 1px var(--jg-cl, var(--fm-line, rgb(214 178 106 / .32)));animation:sz-jg-pop .3s cubic-bezier(.2,1.5,.4,1) .55s both}
@R@ .jg-c::before{content:"";flex:none;width:14px;height:14px;background:var(--jg-cc);-webkit-mask:var(--jg-g, @GEN@) center/contain no-repeat;mask:var(--jg-g, @GEN@) center/contain no-repeat}
@R@ .jg-c b{font-size:10.5px!important;font-weight:700!important;letter-spacing:.04em;color:var(--jg-cc)!important}
@R@ .jg-c b:empty{display:none}
@R@ .jg-c::after{content:none;flex:none;margin-left:1px;font-size:8.5px;color:var(--jg-cc)}
@R@ .jg-c:is([data-v=""],[data-v="无"],[data-v="暂无"],[data-v="—"],[data-v="-"]){display:none}
@R@ .jg-c:nth-child(2){animation-delay:.62s}
@R@ .jg-c:nth-child(3){animation-delay:.69s}
@R@ .jg-c:nth-child(4){animation-delay:.76s}
@R@ .jg-c:nth-child(5){animation-delay:.83s}
@R@ .jg-c:nth-child(6){animation-delay:.9s}
@R@ .jg-c:nth-child(n+7){animation-delay:.97s}
/* 档位尺 */
@R@ .jg-tr{grid-area:tr;display:grid;grid-template-columns:repeat(5, minmax(0,1fr));gap:4px;margin-top:20px;--jg-cw:calc((100% - 16px) / 5);animation:sz-jg-fade .4s ease-out .7s both}
@R@ .jg-tr::before{content:"定档";position:absolute;z-index:3;top:-9px;left:calc((var(--t) - 1) * (var(--jg-cw) + 4px) + 6px);padding:0 6px;border-radius:3px;font-size:9.5px;font-weight:700;line-height:15px;letter-spacing:.14em;color:var(--fm-matc, #191842);background:var(--fm-acc)}
@R@ .jg-tr>i:not(.jg-pt){position:relative;display:grid;place-items:center;height:30px;border-radius:6px;font-size:11.5px;letter-spacing:.06em;white-space:nowrap;color:var(--fm-ink2);
background:var(--fm-slot, rgb(255 255 255 / .05));box-shadow:inset 0 0 0 1px var(--fm-line, rgb(214 178 106 / .32)), inset 0 -2px 0 color-mix(in srgb, var(--jg-tc) 75%, transparent)}
@R@ .jg-tr>i:not(.jg-pt)::after{position:absolute;inset:0;display:grid;place-items:center;border-radius:6px;font-weight:700;color:var(--fm-head);
background:linear-gradient(180deg, color-mix(in srgb, var(--fm-acc2) 34%, var(--fm-matc, #191842)), color-mix(in srgb, var(--fm-acc) 16%, var(--fm-matc, #191842)));box-shadow:inset 0 -2px 0 var(--jg-tc);opacity:0;animation:sz-jg-fade .25s ease-out 2.05s both}
@R@ .jg-pt{position:absolute!important;z-index:2!important;top:-4px;bottom:-4px;left:calc((var(--f) - 1) * (var(--jg-cw) + 4px));width:var(--jg-cw);border-radius:9px;pointer-events:none;
box-shadow:0 0 0 2px var(--fm-acc2), 0 0 16px color-mix(in srgb, var(--fm-glow, #f0d48c) 70%, transparent), inset 0 0 12px color-mix(in srgb, var(--fm-glow, #f0d48c) 30%, transparent);animation:sz-jg-slide .42s cubic-bezier(.3,1.35,.5,1) 1.75s both}
@R@ .jg-pt::after{content:"";position:absolute;left:50%;bottom:-11px;margin-left:-6px;border:6px solid transparent;border-bottom-color:var(--fm-acc2)}
/* 骰子 */
@R@ .jg-di{grid-area:di;align-self:center;justify-self:center;width:86px;height:86px;margin-top:14px}
@R@ .jg-di::before{content:"";position:absolute;left:10%;right:10%;bottom:-8px;height:16px;border-radius:50%;background:radial-gradient(closest-side, rgb(0 0 0 / .55), transparent);animation:sz-jg-fade .3s ease-out 1.3s both}
@R@ .jg-di::after{content:none;position:absolute;inset:-34%;z-index:-1;border-radius:50%;background:@RAYS@;-webkit-mask:radial-gradient(closest-side, #000 30%, transparent 96%);mask:radial-gradient(closest-side, #000 30%, transparent 96%);opacity:0}
@R@ .jg-d20{position:absolute;inset:0;display:grid;place-items:center;animation:sz-jg-roll 1s cubic-bezier(.3,.1,.3,1) .7s both}
@R@ .jg-d20::before,@R@ .jg-d20::after{content:"";position:absolute;inset:0;background:var(--jg-die, none) center/contain no-repeat, radial-gradient(closest-side, var(--fm-por1, #2a2a64) 60%, var(--fm-acc) 62% 68%, transparent 70%);filter:drop-shadow(0 3px 6px rgb(0 0 0 / .5))}
@R@ .jg-d20::after{content:none;background:var(--jg-crk, none) center/contain no-repeat;opacity:0;animation:sz-jg-fade .08s linear 1.64s both}
@R@ .jg-d20 b{position:relative;z-index:1;top:-2px;font-family:var(--fm-serif);font-size:26px!important;font-weight:800!important;line-height:1;font-variant-numeric:lining-nums;letter-spacing:-.02em;color:var(--jg-num, #fff4cf)!important;text-shadow:var(--jg-nsh, 0 1px 2px #000);animation:sz-jg-num .32s cubic-bezier(.2,1.6,.4,1) 1.66s both}
@R@ .jg-dn{grid-area:dn;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:2px 7px;margin-top:16px;font-size:11.5px;letter-spacing:.06em;color:var(--fm-ink2);animation:sz-jg-fade .3s ease-out 1.8s both}
@R@ .jg-dn::before{content:"命运骰";letter-spacing:.14em}
@R@ .jg-dn em:last-of-type,@R@ .jg-dn em:empty{display:none}
@R@ .jg-dn u{font-family:var(--fm-serif);font-size:14px;font-weight:800;color:var(--jl)}
@R@ .jg-dn::after{content:"照定的那一档";padding:0 9px;border-radius:999px;line-height:18px;color:var(--jg-dc, var(--fm-ink2));box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--jg-dc, var(--fm-ink2)) 60%, transparent);background:color-mix(in srgb, var(--jg-dc, var(--fm-ink2)) 10%, transparent)}
/* 绶带和后果 */
@R@ .jg-rb{grid-area:rb;justify-self:center;display:grid;place-items:center;width:min(100%, 330px);aspect-ratio:480 / 106;margin-top:12px;
background:var(--jg-rib, none) center/contain no-repeat, linear-gradient(var(--jg-rbf, #1c2f8a), var(--jg-rbf, #1c2f8a)) 50% 40%/64% 54% no-repeat;filter:var(--jg-rf, drop-shadow(0 4px 8px rgb(0 0 0 / .45)));animation:sz-jg-unfurl .45s cubic-bezier(.2,1.2,.4,1) 2.05s both}
@R@ .jg-rb b{padding:0 0 9% .42em;font-family:var(--fm-serif);font-size:21px!important;font-weight:800!important;line-height:1;letter-spacing:.42em;white-space:nowrap;color:var(--jg-rt, var(--jg-rbt, #f8e8b0))!important;text-shadow:var(--jg-rbs, 0 1px 2px #000)}
@R@ .jg-ou{grid-area:ou;display:block;margin-top:8px;padding:10px 4px 0;text-align:center;font-family:var(--fm-serif);font-size:14.5px;line-height:1.75;text-wrap:balance;color:var(--fm-ink);
background:linear-gradient(90deg, transparent, var(--fm-line, rgb(214 178 106 / .32)) 30%, var(--fm-line, rgb(214 178 106 / .32)) 70%, transparent) 50% 0/100% 1px no-repeat;animation:sz-jg-fade .4s ease-out 2.3s both}
@R@ .jg-ou:empty{display:none}
@R@ .sz-judge[data-o=""] .jg-rb{display:none}
/* 简版：栏对不上的时候只有事、档位尺、骰、结果、后果 */
@R@ .sz-judge.jg-s{grid-template-columns:minmax(0,1fr) 96px;grid-template-areas:"hd hd" "tr di" "dn di" "rb rb" "ou ou";max-width:520px}
@R@ .sz-judge.jg-s .jg-di{margin-top:8px}
@R@ .sz-judge.jg-s .jg-dn{margin-top:14px}
/* 没掷骰的（六颗用完、照实力直接判）：不出骰子 */
@R@ .sz-judge[data-d=""] :is(.jg-di,.jg-dn u,.jg-dn em){display:none}
@R@ .sz-judge[data-d=""] .jg-dn::before{content:"没有掷骰"}
@R@ .sz-judge[data-d=""] .jg-dn::after{content:"照实力直接判"}
'''


# ---- 11-25 主角那一边的剪影（没有主角立绘的时候出，「判·主角」挂的 jg-pc、data-r 种族、data-g 性别、data-e 预设的族属）----
# 一枚胸像，两层遮罩叠着：底下一层照性别（男宽肩短发、女长发垂肩、没写的齐耳发），矮人和半身人另有自己的身形；
# 上头一层照种族添一样认得出来的东西（精灵的长耳、兽耳、角、翼、鳍耳、顶髻）。画在 48 见方里，头像是圆的，角尖耳尖都收在圆里头。
# 种族认字眼（身份那一行的种族，加上预设立绘的族属），认不出的、人类各族属只有底下那一层。魔族各系照主角预设的资料（comfy/cast/主角/魔族_一.md、_二.md）：
# 帝都、炎角是往后掠的角，轰狱是往前弯的粗角，夜翼是背后的翼（不画角），深潮是鳍耳加短角，绯宴、梦魇和没写哪一系的是一对小角，白骸、长生不画角；龙裔的远裔不画角。
def _sil(body):
    s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" fill="black">%s</svg>' % body
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' ")


def _mirror(d):
    """一侧的图形照正中那条竖线翻到另一侧（外头套一层翻转）"""
    return d + '<g transform="matrix(-1 0 0 1 48 0)">' + d + '</g>'


_HEAD = '<ellipse cx="24" cy="20" rx="7.5" ry="9"/>'
_NECK = '<path d="M20.5 26h7v8h-7z"/>'
SIL_BASE = {
    'm': _HEAD + _NECK + '<path d="M4 48c0-7.5 5.5-12.200 14-13.700l6 2.200 6-2.200c8.500 1.500 14 6.200 14 13.700z"/>',
    # 女：长发从头顶垂到肩，往下略略散开
    'f': '<path d="M14.200 22c0-7.500 4.100-12.500 9.800-12.500s9.800 5 9.800 12.500c0 5 1 9 2.700 12.300-2.800 1.600-6.200 1.700-8.700.4h-7.600c-2.500 1.300-5.900 1.200-8.700-.4 1.700-3.300 2.700-7.300 2.700-12.300z"/>'
         '<path d="M8 48c0-6.500 4.500-10.800 11-12.300l5 1.800 5-1.800c6.500 1.500 11 5.800 11 12.300z"/>',
    # 没写性别：齐耳的短发
    'n': _HEAD + _NECK + '<path d="M15.300 21c0-6.500 3.800-10.700 8.700-10.700s8.700 4.200 8.700 10.700c0 2.800-.5 5.200-1.500 7.200H16.800c-1-2-1.500-4.400-1.500-7.200z"/><path d="M6 48c0-7 5-11.500 12.500-13l5.500 2 5.500-2C37 36.500 42 41 42 48z"/>',
}
_DWS = '<path d="M2 48c0-5.500 4-9.500 10-11h24c6 1.500 10 5.500 10 11z"/>'
# 矮人男：一把比脸还宽、垂到胸口收成尖的大胡子，脸和胡子之间留一圈缝（挖空的那一圈），看得出是胡子围着脸
SIL_BASE['dm'] = (_DWS + '<ellipse cx="24" cy="18.500" rx="7.500" ry="8"/>'
                  '<path fill-rule="evenodd" d="M13.800 17.500L8.800 31.500c3 6 8.300 10.800 15.200 14 6.900-3.200 12.200-8 15.200-14L34.200 17.500zM15 18.500a9 9.600 0 1018 0a9 9.600 0 10-18 0z"/>')
# 矮人女：两鬓各盘一个圆髻
SIL_BASE['df'] = _DWS + '<ellipse cx="24" cy="20" rx="8.500" ry="9.300"/>' + _NECK + _mirror('<circle cx="14.300" cy="18.500" r="4.600"/>')
_CURL = ''.join('<circle cx="%s" cy="%s" r="3.300"/>' % c for c in [(17.3, 16.5), (19.8, 12.6), (24, 11.200), (28.200, 12.6), (30.7, 16.5)])
_SMALL = '<g transform="translate(5.300 10.500) scale(.78)">%s</g>'
SIL_BASE['hm'] = _SMALL % (SIL_BASE['m'] + _CURL)                                   # 半身人：小一号。男一头卷发
SIL_BASE['hf'] = _SMALL % (SIL_BASE['f'] + '<circle cx="24" cy="8.300" r="4.200"/>')   # 女头顶一个圆发髻
_HORN_S = _mirror('<path d="M19 12.500L16 5.500l5.800 4.700z"/>')
_HORN_B = _mirror('<path d="M18.500 13.500c-4-1-6.500-4.200-6.800-8.500 2 2.800 4.800 4.200 8.600 4.800z"/>')
SIL_FEAT = {
    'elf': _mirror('<path d="M17.200 18L7 12.500l9.500 11.500z"/>'),
    'beast': _mirror('<path d="M16.500 15.500L15 4.500l8.500 6z"/>'),
    'horn': _HORN_S,
    'hornb': _HORN_B,
    'bull': _mirror('<path d="M17 16c-5 .8-9-1.500-10-6.500 1.800 2 4.500 2.800 7.500 2.300 1.300-.2 2.500.5 3 1.500z"/>'),
    'wing': _mirror('<path d="M3.500 44c-1-8 .5-16 4.500-22 .8 5 3 8.500 7 11l-2.500 11z"/>'),
    'fin': _mirror('<path d="M17 17.500l-7.500-3 1.800 3.200-2.800 1.600 2.800 1.200-1.300 3 7-2.500z"/>') + _HORN_S,
    'dragon': _HORN_B + _mirror('<path d="M16.700 21.500l-4.700.8 3.700 2.200-1.700 3 3.500-1.500z"/>'),
    'orc': ('<path d="M21.500 12c-1.300-3-.5-6 2.500-7.500 3 1.500 3.800 4.500 2.500 7.500z"/><path d="M2 48c0-8.500 5.500-14 14-15.500l8 3 8-3c8.500 1.500 14 7 14 15.500z"/>'
            + _mirror('<path d="M17 19l-4.500-2.500 3.800 6z"/>')),
}
# (认哪些字, 上头那一层)，后写的盖先写的：先泛的（魔族、龙），再细的（哪一系、远裔）。'' 是不添东西
SIL_RACE = [
    ('精灵', 'elf'),
    ('兽耳|狐族|狼族|林猎|猫耳|犬耳|兔耳', 'beast'),
    ('半兽人|兽人|赎罪者之后', 'orc'),
    ('提夫林', 'horn'),
    ('魔族|魔裔|绯宴|梦魇', 'horn'), ('帝都魔族|炎角', 'hornb'), ('轰狱', 'bull'), ('夜翼', 'wing'), ('深潮', 'fin'), ('白骸|长生|影魔', ''),
    ('真龙|龙卵|圣域之卵|骨谷孤雏', 'horn'), ('龙裔', 'dragon'), ('远裔', ''),
]


def _pc_css(P):
    o = []
    w = o.append
    PC = P + '.jg-w.jg-pc'
    lay = 'var(--jg-sf, none) 50% 100%/100% 100% no-repeat, var(--jg-sb, ' + _sil(SIL_BASE['n']) + ') 50% 100%/100% 100% no-repeat'
    w(PC + ' .jg-av{overflow:hidden}')
    w(PC + ' .jg-av::before{content:"";width:100%;height:100%;background:color-mix(in srgb, var(--jg-sc) 58%, var(--fm-head));opacity:.9;-webkit-mask:' + lay + ';mask:' + lay + '}')
    w('%s[data-g*="男"]{--jg-sb:%s}%s[data-g*="女"]{--jg-sb:%s}' % (PC, _sil(SIL_BASE['m']), PC, _sil(SIL_BASE['f'])))
    race = lambda words: ':is(%s)' % ','.join('[data-%s*="%s"]' % (a, x) for x in words.split('|') for a in 're')
    for words, k in SIL_RACE:
        w('%s%s{--jg-sf:%s}' % (PC, race(words), _sil(SIL_FEAT[k]) if k else 'none'))
    for words, m, f in [('矮人', 'dm', 'df'), ('半身人', 'hm', 'hf')]:
        w('%s%s{--jg-sb:%s;--jg-sf:none}%s%s[data-g*="女"]{--jg-sb:%s}' % (PC, race(words), _sil(SIL_BASE[m]), PC, race(words), _sil(SIL_BASE[f])))
    return o


def _attr(attr, words, op='*='):
    return ','.join('[%s%s"%s"]' % (attr, op, w) for w in words)


def css(art=True):
    P = R + ' '
    o = ['/* ==== 11-23 检定对抗演出（judge_fx.py）：两边对垒、矛对盾、各项小标、五格档位尺、二十面骰、结果绶带；四纪换皮靠 --fm- 变量和一纪一套图 ==== */']
    w = o.append
    w(T.replace('@R@', R).replace('@GEN@', _mask(IC['gen'])).replace('@RAYS@', RAYS).strip())
    # 主角那一边没有立绘时的剪影（11-25）
    o.extend(_pc_css(P))
    # 小标的图形
    for k, g in KEY_EQ:
        w('%s.jg-c[data-k="%s"]{--jg-g:%s}' % (P, k, _mask(IC[g])))
    for words, g in VAL_HAS:
        w('%s.jg-c[data-k=""]:is(%s){--jg-g:%s}' % (P, _attr('data-v', words.split('|')), _mask(IC[g])))
    for words, g in KEY_HAS:
        w('%s.jg-c:is(%s){--jg-g:%s}' % (P, _attr('data-k', words.split('|')), _mask(IC[g])))
    # 品阶的颜色（装备、Ability 后头写了稀有度的）
    for names, col in [(['Rare', '稀有'], '#6fa8ec'), (['Epic', '史诗'], '#b98af0'), (['Legend', '传说'], '#f0b64e'), (['Unique', '唯一'], '#f07464')]:
        w('%s.jg-c:is(%s){--jg-rq:color-mix(in srgb, %s 46%%, transparent);--jg-cl:color-mix(in srgb, %s 60%%, transparent)}' % (P, _attr('data-v', names), col, col))
    # 加分、减分
    up, dn = _attr('data-m', UP, '='), _attr('data-m', DN, '=')
    w('%s.jg-c:is(%s){--jg-cc:var(--jup);--jg-cb:color-mix(in srgb, var(--jup) 13%%, transparent);--jg-cl:color-mix(in srgb, var(--jup) 70%%, transparent);color:var(--fm-head);filter:drop-shadow(0 0 4px color-mix(in srgb, var(--jup) 30%%, transparent))}' % (P, up))
    w('%s.jg-c:is(%s){--jg-cc:var(--jdn);--jg-cb:color-mix(in srgb, var(--jdn) 12%%, transparent);--jg-cl:color-mix(in srgb, var(--jdn) 62%%, transparent)}' % (P, dn))
    w('%s:is(.jg-c,.jg-ma):is(%s)::after{content:"▲";color:var(--jup)}' % (P, up))
    w('%s:is(.jg-c,.jg-ma):is(%s)::after{content:"▼";color:var(--jdn)}' % (P, dn))
    for side, sel in [('ma', 'b:first-child'), ('mb', 'b:last-child')]:
        w('%s.jg-x:is(%s) %s::after{content:"▲";color:var(--jup)}' % (P, _attr('data-' + side, UP, '='), sel))
        w('%s.jg-x:is(%s) %s::after{content:"▼";color:var(--jdn)}' % (P, _attr('data-' + side, DN, '='), sel))
    # 进了大数和对冲条的那几项，小标里不再出一回
    for k in ['STR', 'DEX', 'MANA', 'MIND', 'VGR', 'FTH']:
        w('%s.sz-judge:has(.jg-ma.l[data-k="%s"]) s.jg-f .jg-c[data-k="%s"],%s.sz-judge:has(.jg-ma.r[data-k="%s"]) del.jg-f .jg-c[data-k="%s"]{display:none}' % (P, k, k, P, k, k))
    ok = ':not([data-a=""]):not([data-b=""])'
    w('%s.sz-judge:has(.x1%s) :is(s.jg-f .jg-c:is([data-k="ATK"],[data-k="MAG"]),del.jg-f .jg-c[data-k="PV"]){display:none}' % (P, ok))
    w('%s.sz-judge:has(.x2%s) :is(s.jg-f .jg-c:is([data-k="Skill"],[data-k="技能"]),del.jg-f .jg-c[data-k="DV"]){display:none}' % (P, ok))
    w('%s.sz-judge:has(.x3%s) :is(s.jg-f .jg-c[data-k="元素"],del.jg-f .jg-c[data-k^="抗"]){display:none}' % (P, ok))
    w('%s.jg-x.x1[data-k="MAG"]::before{content:"术　对　盾"}' % P)
    # 徽记：别的类换空心的那一枚，里头一个字形
    for words, g in CAT:
        sel = _attr('data-c', words.split('|'))
        w('%s.sz-judge:is(%s) .jg-vs{--jg-vs:var(--jg-ring, none)}' % (P, sel))
        w('%s.sz-judge:is(%s) .jg-vs::after{content:"";--jg-g:%s}' % (P, sel, _mask(IC[g], sw='1.7')))
    # 档位尺：五格的字、底下一道颜色；定的那一档；骰子挪到的那一格
    TC = ['#c8554c', '#cf8f58', 'var(--fm-acc)', '#9fc66e', '#6fd6a0']
    for i, name in enumerate(TIERS):
        w('%s.jg-tr .t%d{--jg-tc:%s}%s.jg-tr .t%d::before{content:"%s"}' % (P, i + 1, TC[i], P, i + 1, name))
        w('%s.sz-judge[data-t="%s"]{--t:%d}' % (P, name, i + 1))
    w('%s.sz-judge:is(%s){--s:1;--jg-dc:var(--jup)}' % (P, _attr('data-d', D_UP, '=')))
    w('%s.sz-judge:is(%s){--s:-1;--jg-dc:var(--jdn)}' % (P, _attr('data-d', D_DN + ['0%d' % n for n in range(1, 6)], '=')))
    w('%s.sz-judge:is(%s) .jg-dn::after{content:"好一档"}' % (P, _attr('data-d', D_UP[:-1], '=')))
    w('%s.sz-judge:is(%s) .jg-dn::after{content:"坏一档"}' % (P, _attr('data-d', D_DN[1:] + ['0%d' % n for n in range(2, 6)], '=')))
    w('%s.sz-judge[data-d="20"] .jg-dn::after{content:"大成功 · 好一档，再添一样好处"}' % P)
    w('%s.sz-judge:is([data-d="1"],[data-d="01"]) .jg-dn::after{content:"大失手 · 坏一档，再添一样麻烦"}' % P)
    up_d, dn_d, mid_d = _attr('data-d', D_UP, '='), _attr('data-d', D_DN + ['0%d' % n for n in range(1, 6)], '='), _attr('data-d', D_MID, '=')
    for f in range(1, 6):
        sels = []
        for t in range(1, 6):
            for s, grp in ((1, up_d), (-1, dn_d), (0, mid_d)):
                if min(5, max(1, t + s)) == f:
                    sels.append('.sz-judge[data-t="%s"]:is(%s) .jg-tr .t%d::after' % (TIERS[t - 1], grp, f))
        w(','.join(P + s for s in sels) + '{content:"%s"}' % TIERS[f - 1])
    # 结果词六等：绶带的光和字
    o_sel = {k: _attr('data-o', v) for k, v in OUT.items()}
    w('%s.sz-judge:is(%s){--jg-rf:drop-shadow(0 0 14px color-mix(in srgb, var(--fm-glow, #f0d48c) 85%%, transparent)) drop-shadow(0 4px 8px rgb(0 0 0 / .45)) brightness(1.12) saturate(1.15)}' % (P, o_sel['gold']))
    w('%s.sz-judge:is(%s) .jg-rb{width:min(100%%, 370px)}' % (P, o_sel['gold']))
    w('%s.sz-judge:is(%s) .jg-rb b{font-size:24px!important}' % (P, o_sel['gold']))
    w('%s.sz-judge:is(%s){--jg-rf:drop-shadow(0 0 9px color-mix(in srgb, var(--fm-glow, #f0d48c) 60%%, transparent)) drop-shadow(0 4px 8px rgb(0 0 0 / .45))}' % (P, o_sel['hi']))
    w('%s.sz-judge:is(%s){--jg-rf:drop-shadow(0 4px 8px rgb(0 0 0 / .45)) saturate(.6) brightness(.92)}' % (P, o_sel['lo']))
    w('%s.sz-judge:is(%s){--jg-rf:drop-shadow(0 4px 8px rgb(0 0 0 / .45)) grayscale(.8) brightness(.72)}' % (P, o_sel['no']))
    w('%s.sz-judge:is(%s){--jg-rf:drop-shadow(0 0 10px rgb(170 30 20 / .6)) drop-shadow(0 4px 8px rgb(0 0 0 / .5)) grayscale(.6) brightness(var(--jg-rbb, .62))}' % (P, o_sel['bad']))
    w('%s.sz-judge:is(%s) .jg-rb b{--jg-rt:var(--jg-rtb, #ffd9cf);text-shadow:var(--jg-rtbs, 0 1px 2px #000, 0 0 10px #c8281c)}' % (P, o_sel['bad']))
    # 好一档：一道淡光扫过去
    w('%s.sz-judge:is(%s) .jg-fl::before{inset:0 30%%;background:linear-gradient(90deg, transparent, color-mix(in srgb, var(--fm-glow, #f0d48c) 30%%, transparent), transparent);animation:sz-jg-sweep .8s ease-out 1.9s both}' % (P, _attr('data-d', D_UP, '=')))
    # 二十：整张面板过一道金光，骰子后头一圈光芒，边上一圈金，绶带大一号
    C20 = P + '.sz-judge[data-d="20"] '
    w(C20 + '.jg-fl::before{inset:0 22%;background:linear-gradient(90deg, transparent, rgb(255 240 190 / .16) 20%, rgb(255 246 214 / .7) 50%, rgb(255 240 190 / .16) 80%, transparent);animation:sz-jg-sweep .95s cubic-bezier(.3,0,.3,1) 1.72s both}')
    w(C20 + '.jg-fl::after{box-shadow:inset 0 0 0 2px #ffe9a8, inset 0 0 34px rgb(255 214 110 / .5);border-radius:12px;animation:sz-jg-fade .4s ease-out 1.7s both, sz-jg-glow 2.6s ease-in-out 2.1s infinite}')
    w(C20 + '.jg-di::after{content:"";animation:sz-jg-halo 1.1s ease-out 1.66s both, sz-jg-spin 26s linear 2.76s infinite}')
    w(C20 + '.jg-d20 b{text-shadow:0 0 12px #ffd36e, 0 0 5px #fff6d0, var(--jg-nsh, 0 1px 2px #000)}')
    w(C20 + '.jg-pt::before{content:"";position:absolute;inset:0;border-radius:9px;box-shadow:0 0 0 2px #ffe9a8, 0 0 22px #ffd36e, inset 0 0 14px rgb(255 214 110 / .5);opacity:0;animation:sz-jg-fade .25s ease-out 1.75s both}')
    # 一：骰面裂开，面板暗一下、留一圈暗红，震一下，一道裂纹
    C1 = P + '.sz-judge:is([data-d="1"],[data-d="01"]) '
    w(P + '.sz-judge:is([data-d="1"],[data-d="01"]){animation:sz-jg-enter .5s cubic-bezier(.2,.9,.3,1) both, sz-jg-shake .42s linear 1.64s}')
    w(C1 + '.jg-d20::before{animation:sz-jg-out .08s linear 1.64s both}')
    w(C1 + '.jg-d20::after{content:""}')
    w(C1 + '.jg-d20 b{color:var(--jg-n1, #ffd0c4)!important;text-shadow:var(--jg-n1s, 0 0 8px #d8281c, 0 1px 2px #000)}')
    w(C1 + '.jg-fl::before{background:radial-gradient(ellipse at 50% 55%, rgb(20 0 0 / .1) 20%, rgb(70 6 4 / .82));animation:sz-jg-dark 1.3s ease-out 1.64s both}')
    w(C1 + '.jg-fl::after{border-radius:12px;box-shadow:inset 0 0 0 2px rgb(196 52 40 / .85), inset 0 0 30px rgb(150 20 12 / .55);animation:sz-jg-fade .2s ease-out 1.66s both}')
    w(C1 + '.jg-pt::before{content:"";position:absolute;inset:0;border-radius:9px;box-shadow:0 0 0 2px #e0685a, 0 0 16px rgb(216 40 28 / .7), inset 0 0 12px rgb(216 40 28 / .35);opacity:0;animation:sz-jg-fade .25s ease-out 1.75s both}')
    # 纪元：一纪一套图
    def era_vars(e):
        d = ERA[e]
        v = (['--jg-n1:#9c1c12', '--jg-n1s:0 1px 0 rgb(255 255 255 / .5)'] if d['art'] == 'bronze' else ['--jg-n1:#ffd0c4', '--jg-n1s:0 0 8px #d8281c, 0 1px 2px #000'])
        v += (['--jg-rtb:#ffd9cf', '--jg-rtbs:0 1px 2px #000, 0 0 10px #c8281c', '--jg-rbb:.62'] if e == 'maze' else ['--jg-rtb:#6e120b', '--jg-rtbs:0 1px 0 rgb(255 255 255 / .35)', '--jg-rbb:.8'])
        v += ['--jg-ov:' + d['ov'], '--jg-num:' + d['num'], '--jg-nsh:' + d['nsh'], '--jg-rbt:' + d['rbt'], '--jg-rbs:' + d['rbs'], '--jg-rbf:' + d['rbf']]
        if art:
            v += ['--jg-%s:url("__ART__/judge_%s_%s.webp")' % (k, d['art'], part) for k, part in [('die', 'die'), ('crk', 'crack'), ('duel', 'duel'), ('ring', 'ring'), ('cor', 'corner'), ('rib', 'ribbon')]]
        return ';'.join(v)
    w('%s{%s}' % (R, era_vars('maze')))
    for e in ['moon', 'strife', 'bronze', 'pre', 'maze']:
        w('%s{%s}' % (ERA_SEL[e], era_vars(e)))
    w(ERA_SEL['strife'] + ' .jg-rb b{padding-left:calc(.42em + 9%)}')                 # 战报纸左头有一枚火漆
    w(ERA_SEL['strife'] + ' .sz-judge{--jr:#b9c4d2}')
    w(ERA_SEL['moon'] + ' .sz-judge{--jl:#f4cf94;--jr:#a9c8f0}')
    w(ERA_SEL['pre'] + ' .sz-judge{--jl:#a5521e;--jr:#2f5f8e;--jup:#9a6a10;--jdn:#b03a26}')   # 羊皮纸上的字要深
    w(ERA_SEL['pre'] + ' .jg-c:is(%s){color:var(--fm-ink)}' % up)
    w(ERA_SEL['pre'] + ' .jg-ma{text-shadow:none}')
    # 写歪了、落到大框「记录兜底」上的那一行：收成一条细条
    w(P + '.sz-prose .sz-row[data-k="判"]{max-width:600px;margin:14px auto;padding:8px 14px;border-radius:8px;font-size:12.5px;line-height:1.7;color:var(--fm-ink2);background:var(--fm-slot, rgb(255 255 255 / .05));box-shadow:inset 0 0 0 1px var(--fm-line, rgb(214 178 106 / .32))}')
    # 手机：两边变窄，小标折行，档位尺一行，骰子和那一句在下头一行
    w('@media (max-width:639px){'
      + P + '.sz-judge{grid-template-columns:minmax(0,1fr) 56px minmax(0,1fr);column-gap:6px;padding:16px 12px 12px;margin:18px 0;'
            'grid-template-areas:"hd hd hd" "wl vs wr" "ml vs mr" "x1 x1 x1" "x2 x2 x2" "x3 x3 x3" "cl . cr" "tr tr tr" "di dn dn" "rb rb rb" "ou ou ou"}'
      + P + '.jg-co{width:50px;height:52px}'
      + P + '.jg-hd{margin:0 26px 10px}' + P + '.jg-hd span{font-size:14.5px}'
      + P + '.jg-w{grid-template-columns:32px minmax(0,1fr);column-gap:6px}' + P + '.jg-w.r{grid-template-columns:minmax(0,1fr) 32px}'
      + P + '.jg-av{width:32px;height:32px}' + P + '.jg-av::before{font-size:15px}'
      + P + '.jg-w b{font-size:14px!important}' + P + '.jg-w small{font-size:10.5px;white-space:normal;line-height:1.3}'
      + P + '.jg-vs{width:60px;height:60px;margin:0 -2px}'
      + P + '.jg-ma{font-size:24px}' + P + '.jg-ma b{font-size:11.5px!important}'
      + P + '.jg-x{column-gap:7px}' + P + '.jg-x b{font-size:12px!important}' + P + '.jg-x:is(.x2,.x3) b{font-size:11px!important;padding:2px 7px}'
      + P + 's.jg-f{margin-right:-29px}' + P + 'del.jg-f{margin-left:-29px}'
      + P + '.jg-c{font-size:11px;padding:1px 7px 1px 4px}'
      + P + '.jg-tr{gap:3px;--jg-cw:calc((100% - 12px) / 5)}' + P + '.jg-tr>i:not(.jg-pt){height:28px;font-size:10.5px;letter-spacing:0}'
      + P + '.jg-tr::before{left:calc((var(--t) - 1) * (var(--jg-cw) + 3px) + 4px)}'
      + P + '.jg-pt{left:calc((var(--f) - 1) * (var(--jg-cw) + 3px))}'
      + P + '.jg-di{width:62px;height:62px;margin-top:16px;justify-self:end;margin-right:6px}' + P + '.jg-d20 b{font-size:19px!important}'
      + P + '.jg-dn{justify-content:flex-start;margin-top:16px;padding-left:4px}'
      + P + '.jg-rb b{font-size:18px!important}' + P + '.jg-ou{font-size:13.5px}'
      + P + '.sz-judge.jg-s{grid-template-columns:minmax(0,1fr) 56px minmax(0,1fr);grid-template-areas:"hd hd hd" "tr tr tr" "di dn dn" "rb rb rb" "ou ou ou"}'
      + '}')
    w('@keyframes sz-jg-slide-m{from{transform:translateX(calc((var(--t) - var(--f)) * (100% + 3px)))}to{transform:none}}')
    w('@media (max-width:639px){' + P + '.jg-pt{animation-name:sz-jg-slide-m}}')
    # 减少动画：全停，停在落定的样子
    w('@media (prefers-reduced-motion:reduce){' + P + '.sz-judge,' + P + '.sz-judge *,' + P + '.sz-judge *::before,' + P + '.sz-judge *::after{animation:none!important}'
      + P + '.jg-tr>i:not(.jg-pt)::after{opacity:1}' + C1 + '.jg-d20::after{opacity:1}' + C1 + '.jg-d20::before{opacity:0}' + C1 + '.jg-fl::before{opacity:.42}' + C1 + '.jg-fl::after{opacity:1}' + P + '.sz-judge .jg-pt::before{opacity:1}'
      + C20 + '.jg-fl::after{opacity:1}' + C20 + '.jg-di::after{opacity:.34}}')
    return '\n'.join(o) + '\n'


def merged(frame_rules, after='技·没写完'):
    """试的时候用：把这五条插进大框规则里「技·没写完」后头"""
    out = []
    for r in frame_rules:
        out.append(r)
        if r['name'] == after:
            out.extend(rules())
    assert len(out) == len(frame_rules) + len(RULES), '没找到「%s」' % after
    return out


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    d3 = os.path.join(here, '第三轮')
    json.dump(rules(), open(os.path.join(d3, '检定演出_rules.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    c = css()
    open(os.path.join(d3, '检定演出.css'), 'w', encoding='utf-8', newline='\n').write(c)
    for n, q, nest in check():
        print('%-8s 量词 %2d%s%s' % (n, q, '  过二十五了' if q > 25 else '', '  量词套量词' if nest else ''))
    print(len(RULES), '条规则', len(c), '字样式')
    if len(sys.argv) > 1:   # 再写一份插好了的整套规则，复刻台直接用
        fr = json.load(open(os.path.join(here, 'rules_frame.json'), encoding='utf-8'))
        json.dump(merged(fr), open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False)
        print('整套', len(fr) + len(RULES), '条 →', sys.argv[1])
