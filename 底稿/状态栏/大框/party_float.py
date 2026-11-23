# 队友浮栏（11-22，用户：“现在想要查看旅伴的状态必须一个个点进去他们的栏位，我想做一个在对话边上可以悬浮的，显示当前对话中队友状态的浮栏——
# 队友的侧脸头像，血条蓝条架势条，以及一个 hover 上去可以看 buff 和 debuff 以及当前状态（art 使用中，active 预备中，施法中，蓄力中）这种类似信息的小 icon 栏”）。
#
# 做法：
# - 记录不多写：同行者照旧每轮写 §角色、§角色签、§角色行｜状态。新添一行可选的 `§角色行｜此刻｜动作 X｜增益 甲、乙｜减益 丙`（骨架 ⑧），
#   打仗的时候和身上挂着东西的时候才写。同行页里它照「角色行」那条兜底的规则出一行，浮栏另抄一份。
# - 规则（RULES，接在「正文开卷」前头）：把 §角色 那一整段抄一份放到 §正文 那一行后头（两个 ⓟ 记号夹着），改名 §浮，只留名字、相遇状态、状态、此刻四样，
#   别的行删掉，拼成 .sz-pf 一排 label。平台的消息行带 contain: layout，钉不到屏幕上，所以浮栏放在手札那一页里，靠 sticky 跟着滚。
# - 两扇浮雕压在对话上面，框外头的东西会被盖住，每条回复的内框横向又是裁掉的，所以浮栏放在内框里头靠右一列（正文让出 78px），手机上改成正文顶上一横排。
# - 只有相遇状态写着同行的人出（样式里筛），旧回复里的不出（只看最新一条）。
import sys
import os
from urllib.parse import quote

sys.dont_write_bytecode = True
R = '.rili-markdown-renderer:has(.sz-hud)'
ROW = 'div[style*="contain: layout"]'
OLD = ROW + ':has(.sz-hud):has(~ div .sz-hud)'

# ---------------- 规则 ----------------
NAME = r'(([^｜\n·"<>]{1,12})[^｜\n"<>]{0,20})'
# 头像底下那三条和小标一排要在卡片外头（悬上去出卡片的时候它们不动），所以开一位的那条规则往后看，把这个人的状态和此刻先取过来；
# 往后看不越过下一位（(?!\n§浮｜)），这个人没写的就是空的
SEE_ST = r'(?=(?:(?!\n§浮｜)[\s\S]){0,3000}?\n§浮行｜状态｜HP (\d{1,6})\/(\d{1,6}) MP (\d{1,6})\/(\d{1,6}) SP [^ ｜\n]{1,14} 架势 (\d{1,6})\/(\d{1,6})|)'
# 量词数平台有上限（二十五个），动作、增益、减益后头的分隔要正好一个字（空格或冒号）
SEE_NOW = r'(?=(?:(?!\n§浮｜)[\s\S]){0,3000}?\n§浮行｜此刻｜(?:动作[ ：:]|)([^｜\n"<>]{0,30})(?:｜ ?增益[ ：:]([^｜\n"<>]{0,90})|)(?:｜ ?减益[ ：:]([^｜\n"<>]{0,90})|)|)'


def opener(por, k):
    """k：往后看的头一个组号"""
    g = lambda i: '$%d' % (k + i)
    bar = '<i class="%s" style="--v:%s;--m:%s"></i>'
    return ('</span></label><label class="sz-pfc" data-portrait="%s" style="--hv:%s;--hm:%s"><input type="checkbox"><i class="sz-pfa" data-n="$1"></i><b class="sz-pfn">$2</b>' % (por, g(0), g(1))
            + '<span class="sz-pfb">' + bar % ('hp', g(0), g(1)) + bar % ('mp', g(2), g(3)) + bar % ('st', g(4), g(5)) + '</span>'
            + '<span class="sz-pfi"><i class="a" data-v="%s" title="%s"></i><s>、%s</s><del>、%s</del></span>' % (g(6), g(6), g(7), g(8))
            + '<span class="sz-pfk"><b class="k-n">$1</b>ⓔ')


NUM = '<span class="k-r"><b>%s</b><em>$%d / $%d</em></span>'
NUMS = '<span class="k-rs">' + NUM % ('HP', 1, 2) + NUM % ('MP', 3, 4) + NUM % ('SP', 5, 6) + NUM % ('架势', 7, 8) + '</span>'
ST = r'§浮行｜状态｜HP (\d{1,6})\/(\d{1,6}) MP (\d{1,6})\/(\d{1,6}) SP (\d{1,6})\/(\d{1,6}) 架势 (\d{1,6})\/(\d{1,6})'
COND = '<span class="k-c" data-k="%s" data-v="$%d"><b>%s</b>$%d</span>'
RULES = [
    # 抄一份：§正文 那一行后头接上 §角色 一整段（到 §见闻、§MOD、§记忆 为止）。没有同行的人、没写见闻的那一轮对不上，就没有浮栏
    ('浮栏·抄', r'/ⓓ(?=[\s\S]*?\n(§角色｜[\s\S]*?)\n§(?:见闻|MOD|记忆)｜)/', 'ⓓ\nⓟ始\n$1\nⓟ终\n'),
    ('浮栏·改名', r'/^§角色(?=[\s\S]*\nⓟ终)/gm', '§浮'),
    ('浮栏·人·立绘', r'/^§浮｜' + NAME + r'｜[^｜\n]{1,40}｜立绘[:：]([^｜\n·"<>]{1,8})[^\n]*$' + SEE_ST + SEE_NOW + '/gm', opener('$3', 4)),
    ('浮栏·人', r'/^§浮｜' + NAME + r'[^\n]*$' + SEE_ST + SEE_NOW + '/gm', opener('$2', 3)),
    # 平台的显示正则至多五百条（split_card 核的），这一组能并的都并了：签和状态各一条，写得不合六栏、没写伤和异常的走空的那一支
    ('浮栏·签', r'/^§浮签｜(?:[^｜\n]{0,60}｜[^｜\n]{0,40}｜([^｜\n"<>]{0,20})｜([^｜\n"<>]{0,30})｜[^｜\n]{0,40}｜|[^\n]*｜)([^｜\n"<>]{0,16})$/gm',
     '<u class="sz-pfm" data-v="$3"></u><small class="k-lv" data-v="$1">$1 · $2</small>ⓔ'),
    ('浮栏·状态', r'/^' + ST + r'(?: ?｜ ?伤 ([^ ｜\n"<>][^｜\n"<>]{0,40}?) ?｜ ?污染 ([^ ｜\n"<>][^｜\n"<>]{0,16}?) ?｜ ?异常 ([^ ｜\n"<>][^｜\n"<>]{0,60}?) *|[^\n]*)$/gm',
     NUMS + '<span class="k-cs">' + COND % ('伤', 9, '伤', 9) + COND % ('污染', 10, '污染', 10) + COND % ('异常', 11, '异常', 11) + '</span>ⓔ'),
    ('浮栏·此刻', r'/^§浮行｜此刻｜(?:动作[ ：:]|)([^｜\n"<>]{0,30})(?:｜ ?增益[ ：:]([^｜\n"<>]{0,90})|)(?:｜ ?减益[ ：:]([^｜\n"<>]{0,90})|)[^\n]*$/gm',
     '<span class="k-act" data-v="$1"><b>此刻</b>$1</span><span class="k-up" data-v="$2"><b>增益</b>$2</span><span class="k-dn" data-v="$3"><b>减益</b>$3</span>ⓔ'),
    # 增益、减益一串（顿号隔开）拆成一颗一颗的小标
    # （开一位的那条规则把两串放在 <s>、甲、乙</s> 和 <del>、丙</del> 里，每一样前头都有一个顿号，后头到收尾的标签之间没有别的标签）
    ('浮栏·增益·拆', r'/[、，,]([^、，,\n"<>]{1,24})(?=[^<\n]{0,200}<\/s>)/g', '<i class="u" data-v="$1" title="$1"></i>'),
    ('浮栏·减益·拆', r'/[、，,]([^、，,\n"<>]{1,24})(?=[^<\n]{0,200}<\/del>)/g', '<i class="d" data-v="$1" title="$1"></i>'),
    ('浮栏·别的行', r'/^§浮[^\n]*\n?/gm', ''),
    ('浮栏·始', r'/^ⓟ始$/m', '<div class="sz-pf"><div class="sz-pf-in"><label hidden><span>ⓔ'),
    ('浮栏·终', r'/^ⓟ终$/m', '</span></label></div></div>ⓔ'),
]


def rules():
    return [{"name": n, "regex": rx, "replaceString": rep, "enabled": True, "messageRole": "assistant", "applyMode": "front-end"} for n, rx, rep in RULES]


# ---------------- 样式 ----------------
def _mask(body, vb='0 0 24 24'):
    s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % (vb, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' ")


IC = {
    # 动作
    'cast': '<circle cx="12" cy="12" r="9"/><path d="M12 3l7.8 13.5H4.2z"/><path d="M12 21L4.2 7.5h15.6z"/>',
    'charge': '<circle cx="12" cy="12" r="3" fill="black"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4M5 5l2.8 2.8M16.2 16.2L19 19M19 5l-2.8 2.8M7.8 16.2L5 19"/>',
    'art': '<path d="M4 20L18 6M14 4h6v6M4 14l6 6"/>',
    'ready': '<path d="M6 3h12M6 21h12M7 3c0 5 10 5 10 9s-10 4-10 9M17 3c0 5-10 5-10 9s10 4 10 9"/>',
    'guard': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
    'down': '<circle cx="12" cy="10" r="7"/><circle cx="9.5" cy="9.5" r="1.2" fill="black"/><circle cx="14.5" cy="9.5" r="1.2" fill="black"/><path d="M9 17v4M12 17v4M15 17v4"/>',
    'act': '<path d="M13 2L5 14h6l-1 8 8-12h-6z" fill="black"/>',
    # 增益
    'up': '<path d="M6 14l6-6 6 6M6 20l6-6 6 6"/>',
    'shield': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    'haste': '<path d="M3 8h9M5 12h11M3 16h9M15 6l6 6-6 6"/>',
    'might': '<path d="M14 3l7 7-9 9-4 1 1-4zM4 20l3-3"/>',
    'heal': '<path d="M12 21s-8-5-8-11a4.5 4.5 0 018-2.8A4.5 4.5 0 0120 10c0 6-8 11-8 11z"/><path d="M12 9v6M9 12h6"/>',
    'bless': '<path d="M12 2l2.6 6.5L21 9l-5 4.4L17.5 20 12 16.4 6.5 20 8 13.4 3 9l6.4-.5z"/>',
    # 减益
    'dn': '<path d="M6 4l6 6 6-6M6 10l6 6 6-6"/>',
    'poison': '<path d="M12 3c4 5 6 8 6 11a6 6 0 01-12 0c0-3 2-6 6-11z"/><circle cx="10" cy="14" r="1" fill="black"/><circle cx="14" cy="12" r="1" fill="black"/>',
    'bleed': '<path d="M12 3c4 5 6 8 6 11a6 6 0 01-12 0c0-3 2-6 6-11z" fill="black"/>',
    'burn': '<path d="M12 2c1 4 6 6 6 12a6 6 0 01-12 0c0-3 2-4 3-7 1 2 2 3 3 3 0-3-1-5 0-8z"/>',
    'slow': '<path d="M12 2v20M3.3 7l17.4 10M20.7 7L3.3 17M12 6l-2-2M12 6l2-2M12 18l-2 2M12 18l2 2"/>',
    'stun': '<path d="M4 12c0-5 4-8 8-8s7 2.5 7 6-2.5 5-5 5-4-1.5-4-3.5 1.5-3 3-3"/>',
    'fear': '<circle cx="12" cy="12" r="9"/><circle cx="9" cy="10" r="1.2" fill="black"/><circle cx="15" cy="10" r="1.2" fill="black"/><ellipse cx="12" cy="16" rx="2" ry="2.6"/>',
    'curse': '<path d="M12 3a9 9 0 100 18 7 7 0 010-14 4 4 0 010 8 2 2 0 010-4"/>',
}
ACT = [('施法|咏唱|吟|念|祷', 'cast'), ('蓄', 'charge'), ('Art|技艺|架式|架势|使用中', 'art'), ('预备|待发|备好', 'ready'), ('防御|格挡|举盾|守', 'guard'),
       ('倒地|昏|濒死|不能动', 'down')]
UP = [('盾|护|守|甲|垒|庇', 'shield'), ('速|疾|迅|风|轻', 'haste'), ('力|攻|锋|刃|怒|勇', 'might'), ('愈|疗|回|复|生', 'heal'), ('祝|赐福|圣|歌|誓', 'bless')]
DN = [('毒|蚀|腐', 'poison'), ('血|创|裂', 'bleed'), ('燃|灼|烧|焚', 'burn'), ('缓|冻|冰|霜|锁|缚|困', 'slow'), ('眩|晕|乱|盲', 'stun'), ('恐|惧|怕|畏|慌', 'fear'),
      ('咒|诅|染|痛|疲|见底', 'curse')]


def _sel(cls, words):
    return ','.join('.sz-pfi i.%s[data-v*="%s"]' % (cls, w) for w in words.split('|'))


def css():
    o = []
    w = o.append
    P = R + ' '
    w(':is(.sz-npc,.sz-say,.sz-pfc):not([data-portrait]){}')   # 占位：立绘表的选择器在 modules_css、four_era_art 里添了 .sz-pfc
    w(R + ' .sz-page.sz-prose{position:relative}')
    # 每条回复那个内框横向是裁掉的（history_far），框外头那一道空又叫两扇浮雕盖着一半，所以浮栏放在内框里头靠右一列，有同行的人时正文让出这一列
    w('@media (min-width:901px){' + R + ' .sz-page.sz-prose:has(.sz-pfm[data-v="同行"]){padding-right:78px}}')
    # 电脑：贴在框里右边那一道空里，跟着滚
    w(P + '.sz-pf{position:absolute;z-index:6;top:0;bottom:0;right:0;width:64px;pointer-events:none}')
    w(P + '.sz-pf-in{position:sticky;top:132px;display:flex;flex-direction:column;gap:12px;width:64px;pointer-events:auto;animation:sz-pf-in .5s ease-out both}')
    w(P + '.sz-pfc{position:relative;display:grid;justify-items:center;gap:3px;cursor:pointer;-webkit-tap-highlight-color:transparent}')
    w(P + '.sz-pfc:not(:has(>.sz-pfk>.sz-pfm[data-v="同行"])){display:none}')
    w(P + '.sz-pfc{--p:calc(var(--hv) / max(var(--hm), 1))}')
    w(P + '.sz-pfc>input{position:absolute;opacity:0;pointer-events:none}')
    # 头像：九格表情的头一格，外头一圈照这一纪的金线，血少了转红、一下一下亮
    w(P + '.sz-pfa{position:relative;display:grid;place-items:center;width:48px;height:48px;border-radius:50%;font-style:normal;'
          'background:var(--face, none) 0 0/var(--fsz, 300% 300%) no-repeat, radial-gradient(circle at 50% 28%, var(--fm-por1), var(--fm-por2));'
          'box-shadow:0 0 0 1.5px var(--fm-acc), 0 0 0 4px color-mix(in srgb, var(--fm-base, #0d0d2a) 80%, transparent), 0 6px 14px rgb(0 0 0 / .5);transition:transform .16s, box-shadow .16s}')
    w(P + '.sz-pfa::before{content:attr(data-n);position:absolute;inset:0;display:var(--init, grid);place-items:center;overflow:hidden;width:1em;margin:auto;height:1.2em;'
          'font-family:var(--fm-serif);font-size:20px;line-height:1.2;color:var(--fm-head)}')
    w(P + '.sz-pfc:hover .sz-pfa,' + P + '.sz-pfc:has(>input:checked) .sz-pfa{transform:scale(1.07);box-shadow:0 0 0 2px var(--fm-acc2), 0 0 0 4px color-mix(in srgb, var(--fm-base, #0d0d2a) 80%, transparent), 0 0 18px color-mix(in srgb, var(--fm-acc2) 60%, transparent)}')
    w(P + '.sz-pfn{max-width:64px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-family:var(--fm-serif);font-size:11.5px!important;font-weight:600!important;letter-spacing:.04em;'
          'color:var(--fm-head)!important;text-shadow:0 1px 3px rgb(0 0 0 / .8)}')
    # 三条：血、蓝、架势
    w(P + '.sz-pfk{display:none}')
    w(P + '.sz-pfb{display:grid;gap:2px;width:50px}')
    w(P + '.sz-pfb i{position:relative;height:4px;border-radius:2px;background:rgb(0 0 0 / .55);box-shadow:0 0 0 .5px rgb(255 255 255 / .14);overflow:hidden}')
    w(P + '.sz-pfb i::after{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(min(var(--v), var(--m)) / max(var(--m), 1) * 100%);border-radius:2px;background:var(--c);transition:width .4s}')
    w(P + '.sz-pfb .hp{--c:linear-gradient(90deg, #58c08a, #9fe3a8);height:5px}')
    w(P + '.sz-pfb .mp{--c:linear-gradient(90deg, #4f8fe0, #8fc0ff)}')
    w(P + '.sz-pfb .st{--c:linear-gradient(90deg, #d9a441, #f4d58a)}')
    w(P + '.sz-pfb .hp[style*="--v:0;"]::after{background:#e25a4e}')
    # 小标一排：动作一颗，增益、减益一颗一颗
    w(P + '.sz-pfi{display:flex;flex-wrap:wrap;justify-content:center;gap:3px;max-width:64px;min-height:0}')
    w(P + '.sz-pfi :is(s,del){display:contents;font-size:0;text-decoration:none}')   # 两串的壳：里头剩下的顿号不显
    w(P + '.sz-pfk .k-lv[data-v=""]{display:none}')
    w(P + '.sz-pfi i{width:15px;height:15px;border-radius:4px;background:color-mix(in srgb, var(--c) 26%, rgb(8 8 20 / .8));box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--c) 70%, transparent);position:relative}')
    w(P + '.sz-pfi i::after{content:"";position:absolute;inset:2px;background:var(--c);-webkit-mask:var(--g) center/contain no-repeat;mask:var(--g) center/contain no-repeat}')
    w(P + '.sz-pfi i:is([data-v=""],[data-v="无"],[data-v="暂无"],[data-v="待机"]){display:none}')
    w(P + '.sz-pfi i.a{--c:#f2d79a;--g:%s;width:18px;height:18px;border-radius:50%%}' % _mask(IC['act']))
    w(P + '.sz-pfi i.u{--c:#7fd9a0;--g:%s}' % _mask(IC['up']))
    w(P + '.sz-pfi i.d{--c:#f0786a;--g:%s}' % _mask(IC['dn']))
    for words, k in ACT:
        w(_sel('a', words).replace('.sz-pfi', P + '.sz-pfi') + '{--g:%s}' % _mask(IC[k]))
    for words, k in UP:
        w(_sel('u', words).replace('.sz-pfi', P + '.sz-pfi') + '{--g:%s}' % _mask(IC[k]))
    for words, k in DN:
        w(_sel('d', words).replace('.sz-pfi', P + '.sz-pfi') + '{--g:%s}' % _mask(IC[k]))
    w(P + '.sz-pfi i.a:is([data-v*="施法"],[data-v*="咏唱"],[data-v*="吟"],[data-v*="祷"])::after{animation:sz-pf-spin 6s linear infinite}')
    w(P + '.sz-pfi i.a[data-v*="蓄"]{animation:sz-pf-pulse 1.1s ease-in-out infinite}')
    w(P + '.sz-pfi i.a:is([data-v*="倒地"],[data-v*="濒死"],[data-v*="昏"]){--c:#f0786a}')
    # 悬上去（触屏点一下）出一张小卡：名字、等级、四条的数、此刻、增益、减益、伤和异常
    w(P + '.sz-pfc:is(:hover,:has(>input:checked)) .sz-pfk{display:grid;position:absolute;z-index:8;right:calc(100% + 12px);top:-6px;width:248px;gap:7px;padding:13px 15px;border-radius:12px;'
          'background:linear-gradient(180deg, rgb(255 255 255 / .05), transparent 60%), var(--fm-matc, #15153a);'
          'box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc) 55%, transparent), 0 14px 34px rgb(0 0 0 / .6);cursor:default;animation:sz-pf-card .16s ease-out both;text-align:left}')
    w(P + '.sz-pfk>.sz-pfm{display:none}')
    w(P + '.sz-pfk>:is(.k-act,.k-up,.k-dn):is([data-v=""],[data-v="无"],[data-v="暂无"]){display:none}')
    w(P + '.sz-pfk .k-n{font-family:var(--fm-serif);font-size:16px!important;font-weight:700!important;letter-spacing:.06em;color:var(--fm-head)!important}')
    w(P + '.sz-pfk .k-lv{margin-top:-4px;font-size:11.5px;letter-spacing:.04em;color:var(--fm-ink2)}')
    w(P + '.sz-pfk .k-rs{display:grid!important;grid-template-columns:1fr 1fr;gap:4px 12px;padding:8px 0;border-block:1px solid color-mix(in srgb, var(--fm-acc) 22%, transparent)}')
    w(P + '.sz-pfk .k-r{display:flex;justify-content:space-between;align-items:baseline;font-size:12px;font-variant-numeric:tabular-nums;color:var(--fm-ink)}')
    w(P + '.sz-pfk .k-r b{font-size:11px!important;font-weight:600!important;letter-spacing:.06em;color:var(--fm-acc)!important}')
    w(P + '.sz-pfk .k-r em{font-style:normal}')
    w(P + '.sz-pfk :is(.k-act,.k-up,.k-dn){font-size:12.5px;line-height:1.6;color:var(--fm-ink)}')
    w(P + '.sz-pfk :is(.k-act,.k-up,.k-dn,.k-c)>b{display:inline-block;margin-right:8px;padding:0 6px;border-radius:3px;font-size:10.5px!important;font-weight:600!important;line-height:17px;letter-spacing:.1em;'
          'color:#141428!important;background:var(--fm-acc)}')
    w(P + '.sz-pfk .k-up>b{background:#7fd9a0}')
    w(P + '.sz-pfk .k-dn>b{background:#f0786a}')
    w(P + '.sz-pfk .k-cs{display:flex!important;flex-wrap:wrap;gap:4px 12px;font-size:12px;color:var(--fm-ink2)}')
    w(P + '.sz-pfk .k-c:is([data-v=""],[data-v="无"],[data-v="暂无"],[data-v="0%"]){display:none}')
    w(P + '.sz-pfk .k-c>b{background:color-mix(in srgb, var(--fm-ink2) 80%, transparent)}')
    # 旧回复里不出
    w(OLD + ' .sz-pf{display:none}')
    w('@keyframes sz-pf-in{from{opacity:0;transform:translateX(10px)}to{opacity:1;transform:none}}')
    w('@keyframes sz-pf-card{from{opacity:0;transform:translateX(6px)}to{opacity:1;transform:none}}')
    w('@keyframes sz-pf-spin{to{transform:rotate(360deg)}}')
    w('@keyframes sz-pf-pulse{0%,100%{box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--c) 70%, transparent), 0 0 0 0 color-mix(in srgb, var(--c) 60%, transparent)}50%{box-shadow:inset 0 0 0 1px var(--c), 0 0 0 4px transparent}}')
    # 手机和窄窗：框里右边没有那一道空，改成正文顶上一横排，贴着楣底下跟着滚
    w('@media (max-width:900px){'
      + P + '.sz-pf{position:sticky;top:54px;right:auto;bottom:auto;width:auto;z-index:6;margin:0 0 6px}'
      + P + '.sz-pf:not(:has(.sz-pfm[data-v="同行"])){display:none}'
      + P + '.sz-pf-in{position:static;flex-direction:row;flex-wrap:wrap;justify-content:center;gap:6px;width:auto;margin:0}'
      + P + '.sz-pfc{position:static;grid-template-columns:30px auto;grid-template-rows:auto auto;align-items:center;justify-items:start;column-gap:5px;row-gap:1px;padding:3px 7px 3px 3px;border-radius:18px;'
            'background:color-mix(in srgb, var(--fm-matc, #15153a) 92%, transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc) 40%, transparent), 0 4px 10px rgb(0 0 0 / .4)}'
      + P + '.sz-pfa{grid-row:1 / span 2;width:30px;height:30px;box-shadow:0 0 0 1px var(--fm-acc)}'
      + P + '.sz-pfa::before{font-size:14px}'
      + P + '.sz-pfn{display:none}'
      + P + '.sz-pfb{width:34px}'
      + P + '.sz-pfb i{height:3px}' + P + '.sz-pfb .hp{height:4px}'
      + P + '.sz-pfi{justify-content:flex-start;gap:2px;max-width:40px;flex-wrap:nowrap;overflow:hidden}'
      + P + '.sz-pfi i{width:11px;height:11px;border-radius:3px}' + P + '.sz-pfi i.a{width:12px;height:12px}'
      + P + '.sz-pfi i::after{inset:1.5px}'
      + P + '.sz-pfc:is(:hover,:has(>input:checked)) .sz-pfk{left:0;right:0;top:calc(100% + 6px);width:auto}'
      + '}')
    w('@media (prefers-reduced-motion:reduce){' + P + '.sz-pf-in,' + P + '.sz-pfi i,' + P + '.sz-pfi i::after{animation:none!important}}')
    return '\n'.join(o) + '\n'


if __name__ == '__main__':
    import json
    json.dump(rules(), open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if len(sys.argv) > 2:
        open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(css())
    print(len(RULES), '条规则', len(css()), '字样式')
