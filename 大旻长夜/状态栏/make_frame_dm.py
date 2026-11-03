# 《大旻长夜》日里版 · 大框样式（11-03 用户定：照奥尔德兰第四版那种浮雕加界面加页签，浮雕全用 SVG 画）。
# 用法：python3 -I -X utf8 make_frame_dm.py 输出.css
# 宽屏：整列一个大框钉在屏幕上，对话在框正中那扇窗后面滚；框压在对话上面、不挡点击。照卡自己的样子画：玄色底、淡网格、两头淡去的金线、
#   一点青色灵光和炉火。左右两扇是玄铁屏，刻线浮雕两张图（左一座符压炉，右一架浑天仪），外侧一根立柱带细管和压力表，靠窗一道窄框一串铆钉；
#   顶上一道檐（回纹、金线、正中一块小匾一点炉火）｜底下一道座｜四角细线包角｜右边一枚方孔铜钱跟着滚动走。
# 框里：顶上一条推演细条（点开是玄枢推演），一页行卷，一块行止抉择；最新一条底下一排页签，点哪页先暗下去转一枚炉火徽，再亮起那一页。
# 旧回复只留行卷。手机不挂两扇，框只留一圈细边，上下各一道回纹。
# 11-03 第一稿是朱漆宫门、金门钉、铜管、神炉、如意云头咬进窗里，用户说用力过猛、不合整卡的样子，这一稿照卡的介绍页和原状态栏收回来。
import sys, os
from urllib.parse import quote
HERE = os.path.dirname(os.path.abspath(__file__))

def svg(body, vb, extra=''):
    s = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='%s'%s>%s</svg>" % (vb, extra, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' -.,()")
GOLD, GOLD2, GOLD3 = '#d8b35d', '#ffe6a6', '#8f6330'
CYAN, EMBER, RED = '#77d7e8', '#ff8a3c', '#c4543c'
import math

# ---------- 共用：玄色底、淡网格、两头淡去的金线、青色灵光、炉火 ----------
DEFS = ("<defs>"
        "<linearGradient id='slate' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#0b0f15'/><stop offset='.5' stop-color='#10151d'/><stop offset='1' stop-color='#080a0e'/></linearGradient>"
        "<linearGradient id='slateH' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#07090d'/><stop offset='1' stop-color='#111720'/></linearGradient>"
        "<linearGradient id='hairH' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='GOLD' stop-opacity='0'/><stop offset='.5' stop-color='GOLD' stop-opacity='.8'/><stop offset='1' stop-color='GOLD' stop-opacity='0'/></linearGradient>"
        "<radialGradient id='cy'><stop offset='0' stop-color='CYAN' stop-opacity='.4'/><stop offset='.5' stop-color='CYAN' stop-opacity='.09'/><stop offset='1' stop-color='CYAN' stop-opacity='0'/></radialGradient>"
        "<radialGradient id='em'><stop offset='0' stop-color='EMBER' stop-opacity='.38'/><stop offset='1' stop-color='EMBER' stop-opacity='0'/></radialGradient>"
        "<pattern id='grid' width='24' height='24' patternUnits='userSpaceOnUse'><path d='M24 0H0V24' fill='none' stroke='#fff' stroke-opacity='.03' stroke-width='1'/></pattern>"
        "</defs>").replace('GOLD', GOLD).replace('CYAN', CYAN).replace('EMBER', EMBER)

def emb(el, a=.2, w=1.3, col=GOLD):
    """刻线：先一道暗线错开一点，再一道淡金线，像刻进去又被光擦过。el 里的形状不带描边属性。"""
    return ("<g fill='none' stroke='#000' stroke-opacity='.75' stroke-width='%s' transform='translate(1 1.2)' stroke-linecap='round' stroke-linejoin='round'>%s</g>"
            "<g fill='none' stroke='%s' stroke-opacity='%s' stroke-width='%s' stroke-linecap='round' stroke-linejoin='round'>%s</g>") % (w, el, col, a, w, el)

def meander_d(x0, y0, n, w=17, h=9):   # 回纹一行（路径）
    d = ''
    for i in range(n):
        x = x0 + i * w
        d += 'M%d %dv-%dh%dv%dh-%dv-%d' % (x, y0 + h, h, w - 4, h - 3, w - 9, h - 6)
    return d

def ticks(cx, cy, r1, r2, n, a0=0, a1=360):
    d = ''
    for i in range(n):
        t = math.radians(a0 + (a1 - a0) * i / n)
        d += 'M%.1f %.1fL%.1f %.1f' % (cx + r1 * math.cos(t), cy + r1 * math.sin(t), cx + r2 * math.cos(t), cy + r2 * math.sin(t))
    return d

# ---------- 两扇：玄铁屏上刻的两张图，左边一座符压炉，右边一架浑天仪 ----------
def boiler():
    cap = 'M138 470A75 75 0 0 1 288 470V1130A75 75 0 0 1 138 1130Z'
    b = "<circle cx='213' cy='806' r='130' fill='url(#cy)' opacity='.7'/>"
    b += "<path d='%s' fill='#0a0e14' fill-opacity='.55'/>" % cap
    b += emb("<path d='%s'/>" % cap, .3, 1.4)
    b += emb("<path d='M150 476A63 63 0 0 1 276 476V1124A63 63 0 0 1 150 1124Z'/>", .1, 1)
    b += emb("<path d='M138 640H288M138 652H288M138 960H288M138 972H288'/>", .2, 1.1)
    b += emb("<circle cx='213' cy='806' r='64'/><circle cx='213' cy='806' r='48'/><path d='%s'/>" % ticks(213, 806, 64, 71, 36), .26, 1.2)
    b += "<circle cx='213' cy='806' r='32' fill='url(#cy)'/>"
    b += "<circle cx='213' cy='806' r='12' fill='none' stroke='%s' stroke-opacity='.55' stroke-width='1.3'/><circle cx='213' cy='806' r='3' fill='%s' fill-opacity='.75'/>" % (CYAN, CYAN)
    b += "<circle cx='213' cy='548' r='22' fill='#080a0e'/>"
    b += emb("<circle cx='213' cy='548' r='22'/><path d='%s'/>" % ticks(213, 548, 15, 19, 11, 150, 390), .34, 1.1)
    b += "<path d='M213 548l12 -9' stroke='%s' stroke-opacity='.8' stroke-width='1.6' stroke-linecap='round'/>" % RED
    b += emb("<path d='M203 395V0M223 395V0'/><rect x='196' y='296' width='34' height='8' rx='1.5'/><rect x='196' y='118' width='34' height='8' rx='1.5'/>", .2, 1.1)
    b += "<path d='M213 70c-16 -18 12 -30 -2 -52' fill='none' stroke='#fff' stroke-opacity='.05' stroke-width='9' stroke-linecap='round'/>"
    b += emb("<path d='M288 1060H330M330 1060H354M342 1048V1072'/><circle cx='342' cy='1060' r='12'/>", .24, 1.1)
    b += emb("<path d='M160 1200L140 1262M266 1200L286 1262M118 1262H308M128 1272H298'/>", .2, 1.1)
    b += ''.join("<circle cx='%d' cy='%d' r='1.9' fill='%s' fill-opacity='.3'/>" % (x, y, GOLD) for x in (138, 288) for y in range(500, 1110, 40))
    return b

def armillary():
    b = "<circle cx='213' cy='780' r='160' fill='url(#cy)' opacity='.6'/>"
    b += emb("<circle cx='213' cy='780' r='128'/><circle cx='213' cy='780' r='116'/><path d='%s'/>" % ticks(213, 780, 128, 135, 48), .26, 1.2)
    b += emb("<ellipse cx='213' cy='780' rx='128' ry='38' transform='rotate(-18 213 780)'/><ellipse cx='213' cy='780' rx='128' ry='54' transform='rotate(30 213 780)'/>"
             "<ellipse cx='213' cy='780' rx='42' ry='128' transform='rotate(-18 213 780)'/>", .19, 1.1)
    b += emb("<path d='M165 634L261 926'/>", .24, 1.1)
    b += "<circle cx='213' cy='780' r='26' fill='url(#cy)'/><circle cx='213' cy='780' r='9' fill='none' stroke='%s' stroke-opacity='.55' stroke-width='1.3'/><circle cx='213' cy='780' r='2.6' fill='%s' fill-opacity='.75'/>" % (CYAN, CYAN)
    b += emb("<path d='M213 908V1092M213 1092C183 1092 158 1110 146 1146M213 1092C243 1092 268 1110 280 1146M118 1150H308M130 1160H296'/>", .2, 1.1)
    b += emb("<circle cx='213' cy='1262' r='34'/><circle cx='213' cy='1262' r='12'/><path d='%s'/><path d='M213 1160V1228'/>" % ticks(213, 1262, 34, 41, 24), .2, 1.1)
    st = [(126, 312), (176, 268), (238, 296), (292, 254), (322, 338), (108, 420), (300, 450)]
    b += emb("<path d='M126 312L176 268L238 296L292 254M238 296L322 338'/>", .12, .9)
    b += ''.join("<circle cx='%d' cy='%d' r='%s' fill='%s' fill-opacity='.5'/>" % (x, y, 2.2 if n % 3 == 0 else 1.5, GOLD2) for n, (x, y) in enumerate(st))
    return b

def wing(kind, mirror=False):
    b = DEFS + "<radialGradient id='lw' cx='1' cy='.06' r='.95'><stop offset='0' stop-color='%s' stop-opacity='.07'/><stop offset='1' stop-color='%s' stop-opacity='0'/></radialGradient>" % (GOLD, GOLD)
    b += "<rect width='400' height='1600' fill='url(#slate)'/><rect width='400' height='1600' fill='url(#grid)'/><rect width='400' height='1600' fill='url(#lw)'/>"
    # 外侧一根立柱，柱上一根细管、几道法兰、一只压力表
    b += "<rect width='56' height='1600' fill='#0a0d12'/><rect x='56' width='1' height='1600' fill='%s' fill-opacity='.24'/>" % GOLD
    b += emb("<path d='M22 0V1600M34 0V1600'/>", .13, 1.1)
    b += emb(''.join("<rect x='15' y='%d' width='26' height='9' rx='1.5'/>" % y for y in range(150, 1600, 270)), .2, 1.1)
    b += "<circle cx='28' cy='760' r='15' fill='#080a0e'/>"
    b += emb("<circle cx='28' cy='760' r='15'/><path d='%s'/>" % ticks(28, 760, 10, 13, 9, 150, 390), .34, 1.1)
    b += "<path d='M28 760l8 -6' stroke='%s' stroke-opacity='.8' stroke-width='1.5' stroke-linecap='round'/>" % RED
    b += boiler() if kind == 'lu' else armillary()
    for y in (150, 1440):
        b += emb("<path d='M78 %dH356M78 %dH356'/>" % (y - 22, y + 26), .18, 1)
        b += emb("<path d='%s'/>" % meander_d(84, y - 5, 16, 17, 9), .14, 1.05)
    # 靠窗一边：一道窄框，内外两道金线，一串铆钉
    b += "<rect x='364' width='36' height='1600' fill='#0a0d12'/><rect x='364' width='1' height='1600' fill='%s' fill-opacity='.3'/><rect x='397' width='3' height='1600' fill='%s' fill-opacity='.5'/>" % (GOLD, GOLD)
    b += ''.join("<circle cx='381' cy='%d' r='2.1' fill='%s' fill-opacity='.4'/>" % (y, GOLD) for y in range(40, 1600, 80))
    if mirror:
        b = "<g transform='translate(400 0) scale(-1 1)'>%s</g>" % b
    return svg(b, '0 0 400 1600')

# ---------- 顶上一道檐：玄色一条、回纹、金线，正中一块小匾里一点炉火 ----------
def lintel():
    b = DEFS
    b += "<rect width='1200' height='48' fill='url(#slateH)'/><rect y='46.5' width='1200' height='1.5' fill='url(#hairH)'/><rect y='3' width='1200' height='.8' fill='url(#hairH)' opacity='.4'/>"
    b += emb("<path d='%s'/>" % meander_d(124, 19, 56), .15, 1)
    b += "<rect x='532' y='30' width='136' height='44' rx='3' fill='#0a0d12' stroke='%s' stroke-opacity='.6' stroke-width='1.2'/>" % GOLD
    b += "<rect x='537' y='35' width='126' height='34' rx='2' fill='none' stroke='%s' stroke-opacity='.2' stroke-width='1'/>" % GOLD
    b += "<circle cx='600' cy='52' r='17' fill='url(#em)'/><circle cx='600' cy='52' r='11' fill='none' stroke='%s' stroke-opacity='.85' stroke-width='1.2'/>" % GOLD
    b += "<path d='M600 44c5 5 7 9 3.5 14-1 1.6-2.4 2.4-3.5 2.4s-2.6-.8-3.6-2.4c-2.6-5 .8-9 3.6-14z' fill='%s'/>" % EMBER
    b += "<path d='M552 52H584M616 52H648' stroke='%s' stroke-opacity='.5' stroke-width='1'/><path d='M549 52l3-3 3 3-3 3zM645 52l3-3 3 3-3 3z' fill='%s' fill-opacity='.7'/>" % (GOLD, GOLD)
    return svg(b, '0 0 1200 86')

# ---------- 底下一道座：一样的玄色、金线、回纹 ----------
def base():
    b = DEFS
    b += "<rect width='1200' height='96' fill='url(#slateH)' transform='matrix(1 0 0 -1 0 96)'/><rect width='1200' height='1.5' fill='url(#hairH)'/>"
    b += emb("<path d='%s'/>" % meander_d(124, 14, 56), .12, 1)
    b += "<rect y='34' width='1200' height='.8' fill='url(#hairH)' opacity='.35'/>"
    return svg(b, '0 0 1200 96')

def corner(i):
    body = ("<path d='M3 28V10Q3 3 10 3H28' fill='none' stroke='%s' stroke-opacity='.8' stroke-width='1.6'/>"
            "<path d='M9 22V13Q9 9 13 9H22' fill='none' stroke='%s' stroke-opacity='.35' stroke-width='1'/>"
            "<path d='M3 33v4M33 3h4' stroke='%s' stroke-opacity='.5' stroke-width='1.6'/>"
            "<rect x='12.5' y='12.5' width='4' height='4' transform='rotate(45 14.5 14.5)' fill='%s' fill-opacity='.8'/>") % (GOLD, GOLD, GOLD, GOLD)
    t = ['', 'translate(40 0) scale(-1 1)', 'translate(0 40) scale(1 -1)', 'translate(40 40) scale(-1 -1)'][i]
    return svg("<g transform='%s'>%s</g>" % (t, body), '0 0 40 40')
COIN = svg("<circle cx='9' cy='9' r='7.6' fill='#0b0e13' stroke='%s' stroke-opacity='.85' stroke-width='1.3'/>"
           "<rect x='6.6' y='6.6' width='4.8' height='4.8' fill='none' stroke='%s' stroke-opacity='.75' stroke-width='1'/>" % (GOLD, GOLD), '0 0 18 18')
EMBLEM = svg(DEFS + "<circle cx='60' cy='60' r='40' fill='url(#em)'/>"
             "<path d='%s' stroke='%s' stroke-opacity='.75' stroke-width='1.2'/>" % (ticks(60, 60, 52, 57, 60), GOLD) +
             "<path d='%s' stroke='%s' stroke-width='2'/>" % (ticks(60, 60, 50, 59, 12), GOLD) +
             "<circle cx='60' cy='60' r='46' fill='#0a0d12' fill-opacity='.85' stroke='%s' stroke-width='1.4'/>" % GOLD +
             "<circle cx='60' cy='60' r='38' fill='none' stroke='%s' stroke-opacity='.4' stroke-width='1' stroke-dasharray='4 3'/>" % GOLD +
             "<path d='M60 34C72 46 77 55 72 69C69 76 65 80 60 80C55 80 50 76 48 69C44 58 51 49 56 42C57 51 61 55 64 55C65 48 63 41 60 34Z' fill='%s'/>" % EMBER +
             "<path d='M60 54C65 59 67 64 64 69C63 72 61 73 60 73C58 73 57 72 56 69C54 64 57 59 60 54Z' fill='%s'/>" % GOLD2 +
             "<path d='M42 88H78' stroke='%s' stroke-width='1.4' stroke-linecap='round'/>" % GOLD, '0 0 120 120')
SEP = svg("<g stroke='%s' stroke-width='1' fill='none' opacity='.6'><path d='M8 12H96M144 12H232'/></g>"
          "<g fill='%s' fill-opacity='.8'><path d='M100 12l4-4 4 4-4 4z'/><path d='M132 12l4-4 4 4-4 4z'/></g>"
          "<circle cx='120' cy='12' r='6' fill='none' stroke='%s' stroke-width='1'/><circle cx='120' cy='12' r='2' fill='%s'/>" % (GOLD, GOLD, GOLD, EMBER), '0 0 240 24')
BANNER = svg("<g stroke='%s' stroke-width='1' fill='none' opacity='.8'><path d='M6 20H92M148 20H234'/></g><g fill='%s'><path d='M96 20l3-3 3 3-3 3z'/><path d='M138 20l3-3 3 3-3 3z'/></g>"
             "<circle cx='120' cy='20' r='12' fill='none' stroke='%s' stroke-width='1.2'/><path d='M120 11c5 5 7 9 3.5 14-1 1.6-2.4 2.4-3.5 2.4s-2.6-.8-3.6-2.4c-2.6-5 .8-9 3.6-14z' fill='%s'/>" % (GOLD, GOLD, GOLD, EMBER), '0 0 240 40')
BAND_M = svg("<rect width='160' height='18' fill='#0b0e13'/><path d='%s' fill='none' stroke='%s' stroke-opacity='.35' stroke-width='1.1'/>" % (meander_d(2, 4, 10, 16, 9), GOLD), '0 0 160 18')
ICON = {
 'prose': "<path d='M7 6h18v20H7z' fill='none' stroke='#000' stroke-width='2'/><rect x='4' y='4' width='3.6' height='24' rx='1.8'/><rect x='24.4' y='4' width='3.6' height='24' rx='1.8'/><path d='M11 11h10M11 15h10M11 19h7' stroke='#000' stroke-width='1.8'/>",
 'ming': "<rect x='8' y='3' width='16' height='22' rx='3' fill='none' stroke='#000' stroke-width='2.2'/><circle cx='16' cy='9' r='2.4'/><path d='M12 15h8M12 19h8' stroke='#000' stroke-width='1.8'/><path d='M16 25v4M13 29h6' stroke='#000' stroke-width='2'/>",
 'jian': "<circle cx='11' cy='10' r='4.2'/><path d='M3 26c.5-6 3.6-9 8-9s7.5 3 8 9z'/><circle cx='22' cy='11.5' r='3.6'/><path d='M17 26.5c.6-4.6 2.8-7.2 5.6-7.2 3.6 0 5.8 2.6 6.4 7.2z'/>",
 'wen': "<path d='M16 3c1.4 0 2.4 1 2.4 2.2C23 6.4 25 10 25 15v5l3 3v2H4v-2l3-3v-5c0-5 2-8.6 6.6-9.8C13.6 4 14.6 3 16 3z'/><path d='M12.6 27h6.8c0 2-1.6 3-3.4 3s-3.4-1-3.4-3z'/>",
 'li': "<circle cx='16' cy='16' r='12' fill='none' stroke='#000' stroke-width='2'/><ellipse cx='16' cy='16' rx='12' ry='4.6' fill='none' stroke='#000' stroke-width='1.6'/><ellipse cx='16' cy='16' rx='4.6' ry='12' fill='none' stroke='#000' stroke-width='1.6' transform='rotate(35 16 16)'/><circle cx='16' cy='16' r='2.2'/>",
 'cang': "<rect x='5' y='6' width='22' height='20' rx='2' fill='none' stroke='#000' stroke-width='2.2'/><path d='M5 12h22M10 6v20M15 6v20' stroke='#000' stroke-width='1.6'/><rect x='19' y='15' width='5' height='3' rx='1'/>",
 'zhao': "<circle cx='16' cy='13' r='10' fill='none' stroke='#000' stroke-width='2.4'/><circle cx='16' cy='13' r='5.6' fill='none' stroke='#000' stroke-width='1.4'/><circle cx='16' cy='13' r='1.8'/><path d='M13 23h6l-1 6h-4z'/>",
}
def ic(k): return svg(ICON[k], '0 0 32 32')

R = '.rili-markdown-renderer:has(.dm-run)'
ROW = 'div[style*="contain: layout"]'
# 最新一条认叙事轮（功能轮的 .dm-run 带 .dm-fn，存档、差评以后上一条叙事轮照旧带页签）
L = ROW + ':has(.dm-run:not(.dm-fn)):not(:has(~ div .dm-run:not(.dm-fn)))'
O = ROW + ':has(.dm-run:not(.dm-fn)):has(~ div .dm-run:not(.dm-fn))'
SH = ':root:has(#conversation)'
IN = SH + ' > div:has(#conversation)'
TABS = ['prose', 'ming', 'jian', 'wen', 'li', 'cang', 'zhao']
MODS = TABS[1:]

T = r'''
/* ==== 大旻长夜 · 大框（浮雕是框的一部分，对话在框的窗口后面滚；全部 SVG） ==== */
@SH@:has(.dm-run){
  isolation:isolate;--fm-dock:96px;--fm-topband:46px;--fm-colw:672px;
  --dm-t:calc(var(--dm-h, 12) + 0);--dm-day:clamp(0, sin(calc((var(--dm-t) - 6) * 15deg)), 1);
  --fm-edge:rgb(216 179 93 / .55);--fm-edge2:rgb(216 179 93 / .3);--fm-band:#0d1118;--fm-band2:#090c11;--fm-veil:rgb(6 8 11 / .93);
  background:#07090d!important;
}
/* 框里的底照卡的介绍页：玄色、淡网格、顶上一点炉火、左上一点青光 */
@SH@:has(.dm-run) #conversation{background:
  radial-gradient(circle at 50% -10%, rgb(172 77 38 / .16), transparent 34%) center top/var(--fm-colw) 100% no-repeat,
  radial-gradient(circle at 14% 16%, rgb(119 215 232 / .07), transparent 30%) center top/var(--fm-colw) 100% no-repeat,
  linear-gradient(rgb(255 255 255 / .022) 1px, transparent 1px) center top/28px 28px,
  linear-gradient(90deg, rgb(255 255 255 / .015) 1px, transparent 1px) center top/28px 28px,
  linear-gradient(180deg, #0f141c, #0a0d12) center top/var(--fm-colw) 100% no-repeat}

/* ---------- 框里：一条回复不另加卡，回复之间一道云头小纹 ---------- */
@R@{background:none!important;width:min(640px, calc(100vw - 36px));padding:4px 2px 6px!important;margin:6px 0 4px!important;border:0!important;box-shadow:none!important;position:relative}
@R@::before{content:"";display:block;height:20px;width:240px;max-width:70%;margin:0 auto 10px;background:@SEP@ center/contain no-repeat}
/* 行卷不再一条一张卡，字直接落在框里的底上；卷头做成一块题签 */
@R@ .dm-scroll{margin:2px 0 10px;background:none;border:0;border-radius:0;box-shadow:none;overflow:visible}
@R@ .dm-scroll::after{display:none}
@R@ .dm-sh{padding:6px 8px 14px;text-align:center;border-bottom:0}
@R@ .dm-sh::after{content:"";display:block;height:14px;margin:12px auto 0;width:min(420px, 80%);background:@SEP@ center/contain no-repeat;opacity:.8}
@R@ .dm-kicker{background:none;color:@GOLD@;box-shadow:none;border:1px solid rgb(217 180 106 / .45);border-radius:2px;padding:1px 12px;font-size:12px;letter-spacing:.18em}
@R@ .dm-sh h2{margin:10px 0 6px;font-size:24px;letter-spacing:.14em;color:#f0dcaa;text-shadow:0 1px 0 #000, 0 0 14px rgb(255 160 80 / .18)}
@R@ .dm-meta{justify-content:center}
@R@ .dm-prose .dm-sb{padding:6px 6px 4px}
@R@ .dm-check{margin:4px 2px 14px}
/* 推演细条：只在最新一条；点开是十二行裁分 */
@R@ details.dm-hud{display:none;margin:0 0 8px;border:1px solid rgb(217 180 106 / .22);border-radius:10px;background:rgb(255 255 255 / .025)}
@L@ details.dm-hud{display:block}
@R@ details.dm-hud>summary{display:flex;align-items:center;gap:14px;padding:7px 12px;cursor:pointer;list-style:none;user-select:none}
@R@ details.dm-hud>summary::-webkit-details-marker{display:none}
@R@ .dm-hk{display:inline-flex;align-items:center;gap:7px;flex:none}
@R@ .dm-hk i{font-style:normal;display:grid;place-items:center;width:20px;height:20px;border-radius:3px;background:#9583b8;color:#f6efe0;font-family:var(--serif);font-size:12px;font-weight:700;transform:rotate(-3deg)}
@R@ .dm-hk b{font-family:var(--serif);font-size:13px;letter-spacing:.14em;color:#cfc2e6;font-weight:600}
@R@ .dm-more{margin-left:auto;flex:none;font-size:11px;color:#9a8f7c;border:1px solid rgb(217 180 106 / .3);border-radius:10px;padding:0 8px}
@R@ .dm-more::after{content:" ▾"}
@R@ details.dm-hud[open] .dm-more::after{content:" ▴"}
@R@ details.dm-hud .dm-pb{padding:2px 12px 10px}
@R@ details.dm-hud .dm-sb{display:grid;grid-template-columns:1fr 1fr;column-gap:18px}
@R@ details.dm-hud .dm-row>b{color:#b7a7d8}
@R@ .dm-bars{display:flex;flex:1;gap:14px;min-width:0}
@R@ .dm-bar{flex:1;display:grid;grid-template-columns:auto 1fr;grid-template-rows:auto 5px;align-items:center;column-gap:6px;row-gap:3px;font-size:11.5px;color:#a99e88;min-width:0}
@R@ .dm-bar b{font-weight:600;color:#e6dcc6;font-size:11.5px}
@R@ .dm-bar em{font-style:normal;justify-self:end;font-variant-numeric:tabular-nums}
@R@ .dm-bar .dm-trk{grid-column:1/3;height:5px;border-radius:3px;background:rgb(128 128 128 / .22);position:relative;overflow:hidden}
@R@ .dm-bar .dm-trk::after{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(min(var(--v), var(--m)) / var(--m) * 100%);border-radius:3px;background:linear-gradient(90deg, color-mix(in srgb, var(--c) 60%, #fff), var(--c))}
@R@ .dm-bar.xue{--c:#c4543c}
@R@ .dm-bar.li{--c:#5f9fa0}
@R@ .dm-bar.kuang{--c:#9a6ad0}

/* 行止抉择：行卷底下那一块，只在最新一条 */
@R@ .dm-acts-box{display:none;margin:0 0 12px}
@L@ .dm-acts-box{display:block}
@R@ .dm-acts-box .dm-s>h3{margin-top:4px}

/* ---------- 模块页：平时收着；最新一条点了页签，那一页顶替行卷 ---------- */
@R@ .dm-pane{display:none;margin:2px 0 12px;padding:12px 14px 14px;border-radius:12px;background:linear-gradient(180deg, rgb(24 31 42 / .9), rgb(9 11 15 / .94));border:1px solid rgb(216 179 93 / .28);box-shadow:0 12px 30px rgb(0 0 0 / .35)}
@R@ .dm-pane-head{display:flex;align-items:center;gap:10px;margin-bottom:8px;padding-bottom:10px;border-bottom:1px solid rgb(217 180 106 / .2)}
@R@ .dm-pane-head i{width:24px;height:24px;background:var(--ac, @GOLD@);-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}
@R@ .dm-pane-head b{font-family:var(--serif);font-size:18px;letter-spacing:.16em;color:#f0e2bd;font-weight:700}
@R@ .dm-pane-head small{font-size:11.5px;color:#8f846f;letter-spacing:.06em}
@R@ .dm-x{margin-left:auto;font-size:12px;color:#a99e88;cursor:pointer;border:1px solid rgb(217 180 106 / .3);border-radius:10px;padding:2px 12px}
@R@ .dm-x:hover{color:#f0e2bd;border-color:@GOLD@}
@R@ .dm-tab input,@R@ .dm-x input{display:none!important}
@R@ .dm-pane .dm-pb{padding:0}
@R@ .p-ming{--ac:@GOLD@}
@R@ .p-jian{--ac:#5f9fa0}
@R@ .p-zhao{--ac:#7f8fa6}
@R@ .p-wen{--ac:#c4543c}
@R@ .p-li{--ac:#c08a4a}
@R@ .p-cang{--ac:#6fa88c}
@R@ .dm-pane .dm-s>h3{color:var(--ac)}
@SHOW@
@L@:has(:is(@MODSEL@) input:checked) :is(.dm-scroll,.dm-acts-box){display:none}
@L@ .dm-pane{min-height:calc(100dvh - var(--fm-dock) - 260px)}
@L@:not(:has(~ div .dm-run)) .rili-markdown-renderer{padding-bottom:calc(var(--fm-dock) + 18px)!important}
@O@ :is(.dm-pane,.dm-acts-box,details.dm-hud,.dm-tabs){display:none!important}

/* ---------- 页签：只在最新一条，贴在框底 ---------- */
@R@ .dm-tabs{display:none}
@L@ .dm-tabs{display:flex;align-items:stretch;margin:6px -2px 0;padding:10px 6px 8px;position:sticky;bottom:calc(var(--fm-dock) + 10px);z-index:4;
  background:linear-gradient(180deg, rgb(24 31 42 / .97), rgb(9 11 15 / .98));border:1px solid rgb(216 179 93 / .34);border-radius:12px;box-shadow:0 10px 26px rgb(0 0 0 / .45), inset 0 1px 0 rgb(255 255 255 / .04)}
@R@ .dm-tab{flex:1;display:flex!important;flex-direction:column;align-items:center;gap:4px;color:#d8cfbf;cursor:pointer;position:relative;padding-bottom:6px;user-select:none}
@R@ .dm-tab i{width:26px;height:26px;background:currentColor;-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}
@R@ .dm-tab b{font-size:12px;font-weight:500;letter-spacing:.12em;color:inherit}
@R@ .dm-tab+.dm-tab::before{content:"";position:absolute;left:0;top:16px;width:4px;height:4px;transform:translateX(-50%) rotate(45deg);background:var(--fm-edge2)}
@R@ .dm-tab:hover{color:#fff4dc}
@L@ .dm-tab:has(input:checked),@L@:not(:has(.dm-tab input:checked)) .t-prose{color:@GOLD2@}
@L@ .dm-tab:has(input:checked)::after,@L@:not(:has(.dm-tab input:checked)) .t-prose::after{content:"";position:absolute;bottom:0;left:24%;right:24%;height:2px;border-radius:2px;background:@GOLD2@;box-shadow:0 0 8px rgb(255 179 92 / .7)}
@R@:not(:has(.p-zhao)) .t-zhao{opacity:.3;pointer-events:none}
@ICONS@

/* ---------- 转场：暗下去，正中转一枚神炉徽，再亮起那一页 ---------- */
@L@ .dm-tabs::before{content:"";position:absolute;left:-1px;right:-1px;bottom:calc(100% + 1px);height:calc(100dvh - var(--fm-dock) - 190px);border-radius:14px 14px 0 0;background:var(--fm-veil);opacity:0;pointer-events:none}
@L@ .dm-tabs::after{content:"";position:absolute;left:50%;width:112px;height:112px;margin-left:-56px;bottom:calc(100% + (100dvh - var(--fm-dock) - 190px) / 2 - 56px);background:@EMBLEM@ center/contain no-repeat;opacity:0;pointer-events:none;filter:drop-shadow(0 0 14px rgb(255 138 60 / .55))}
@ANIM@
@KEYS@
@media (prefers-reduced-motion:reduce){@L@ .dm-tabs::before,@L@ .dm-tabs::after{animation:none!important}}

/* ---------- 宽屏：框是浮雕刻成的，对话压在最底下，在正中那扇窗后面滚 ---------- */
@media (min-width:1100px){
  @SH@:has(.dm-run){--fm-win:760px;--fm-colw:var(--fm-win);--fm-ftop:calc(var(--fm-topband) - 10px);timeline-scope:--fm-scroll}
  @SH@:has(.dm-run) #conversation{scroll-timeline:--fm-scroll y}
  @SH@:has(.dm-run)::after{content:"";position:absolute;left:calc(50% - var(--fm-win) / 2);width:var(--fm-win);top:var(--fm-ftop);bottom:calc(var(--fm-dock) - 6px);z-index:2;pointer-events:none;
    border:1.5px solid var(--fm-edge);border-radius:6px;
    box-shadow:inset 0 0 0 1px rgb(0 0 0 / .55), inset 0 0 0 4px rgb(10 13 18 / .92), inset 0 0 0 5px rgb(216 179 93 / .14), inset 0 16px 22px -12px rgb(0 0 0 / .55),
      0 -60px 0 48px var(--fm-band2), 0 50px 0 48px var(--fm-band2);
    background:linear-gradient(rgb(216 179 93 / .22), rgb(216 179 93 / .22)) center bottom 13px/calc(100% - 12px) 1px no-repeat,
      linear-gradient(#0a0d12, #0a0d12) center bottom/100% 14px no-repeat,
      linear-gradient(90deg, rgb(0 0 0 / .3), transparent 20px), linear-gradient(270deg, rgb(0 0 0 / .3), transparent 20px)}
  @IN@::before,@IN@::after{content:"";position:absolute;top:-64px;bottom:0;width:calc(50% - var(--fm-win) / 2);z-index:3;pointer-events:none;background-color:#0a0d12;
    background-repeat:repeat, no-repeat, no-repeat;filter:brightness(calc(.72 + .28 * var(--dm-day)))}
  @IN@::before{left:0;background-image:@RAIN@, linear-gradient(90deg, rgb(0 0 0 / .5), transparent 45%), @WINGL@;
    background-size:calc(var(--dm-rain, 0) * 140px) 300px, auto, cover;background-position:0 0, 0 0, right center}
  @IN@::after{right:0;background-image:@RAIN@, linear-gradient(270deg, rgb(0 0 0 / .5), transparent 45%), @WINGR@;
    background-size:calc(var(--dm-rain, 0) * 140px) 300px, auto, cover;background-position:0 0, 0 0, left center}
  @SH@:has(.dm-run)::before{content:"";position:absolute;left:0;right:0;top:-64px;bottom:0;z-index:4;pointer-events:none;
    background:@TOPLAYERS@;
    animation:fm-coin linear both;animation-timeline:--fm-scroll}
}
@keyframes fm-coin{from{background-position:@COINFROM@}to{background-position:@COINTO@}}
/* ---------- 手机：不挂浮雕，框只留一圈细边，上下各一道回纹 ---------- */
@media (max-width:1099px){
  @SH@:has(.dm-run){--fm-dock:84px;--fm-colw:100%}
  header>div:nth-child(2)::before{content:"";width:200px;height:30px;opacity:var(--dm-on, 0);background:@BANNER@ center/contain no-repeat}
  @SH@:has(.dm-run)::after{content:"";position:absolute;left:5px;right:5px;top:4px;bottom:calc(var(--fm-dock) - 4px);z-index:2;pointer-events:none;border:1.5px solid var(--fm-edge);border-radius:12px;
    box-shadow:inset 0 0 0 3px rgb(10 13 18 / .7), inset 0 0 0 4px rgb(216 179 93 / .14);
    background:@BANDM@ center top 5px/160px 18px repeat-x, @BANDM@ center bottom 5px/160px 18px repeat-x}
  @SH@:has(.dm-run)::before{content:"";position:absolute;left:0;right:0;top:-64px;bottom:0;z-index:3;pointer-events:none;
    background:linear-gradient(var(--fm-band2), var(--fm-band2)) center top/100% 68px no-repeat, linear-gradient(var(--fm-band2), var(--fm-band2)) center bottom/100% calc(var(--fm-dock) - 4px) no-repeat}
  @R@{width:calc(100vw - 30px)}
  @R@ details.dm-hud .dm-sb{grid-template-columns:1fr}
  @R@ .dm-bars{gap:8px}
  @R@ .dm-bar b{display:none}
  @R@ .dm-tab i{width:22px;height:22px}
  @R@ .dm-tab b{font-size:10.5px;letter-spacing:.04em}
  @R@ .dm-tab+.dm-tab::before{top:13px;width:3px;height:3px}
  @L@ .dm-tabs{padding:8px 2px 6px}
  @R@ .dm-pane{padding:10px 10px 12px}
}
'''
ANIM, KEYS = [], []
for n, k in enumerate(TABS):
    if k == 'prose':
        sel_b = '%s:has(.t-prose input:checked) .dm-tabs::before,%s:has(.dm-x input:checked) .dm-tabs::before' % (L, L)
        sel_a = sel_b.replace('::before', '::after')
    else:
        sel_b = '%s:has(.t-%s input:checked) .dm-tabs::before' % (L, k)
        sel_a = '%s:has(.t-%s input:checked) .dm-tabs::after' % (L, k)
    ANIM.append('%s{animation:fm-v%d .95s ease-out}' % (sel_b, n))
    ANIM.append('%s{animation:fm-e%d .95s ease-out}' % (sel_a, n))
    KEYS.append('@keyframes fm-v%d{0%%{opacity:.96}52%%{opacity:.96}100%%{opacity:0}}' % n)
    KEYS.append('@keyframes fm-e%d{0%%{opacity:1;transform:rotate(-200deg) scale(.55)}55%%{opacity:1;transform:rotate(0deg) scale(1)}100%%{opacity:0;transform:rotate(50deg) scale(1.3)}}' % n)
SHOW = '\n'.join('%s:has(.t-%s input:checked) .p-%s{display:block}' % (L, k, k) for k in MODS)
ICONS = '\n'.join('%s :is(.t-%s,.p-%s){--ic:%s}' % (R, k, k, ic(k)) for k in TABS)
RAIN = svg("<g stroke='rgb(200,214,232)' stroke-opacity='.2' stroke-width='1.1' stroke-linecap='round'>" +
           ''.join("<path d='M%d %d l-6 22'/>" % (x, y) for x, y in [(12, 10), (40, 70), (66, 30), (96, 120), (120, 60), (20, 160), (58, 210), (88, 250), (130, 190), (110, 280), (30, 260), (76, 150)]) + "</g>", '0 0 140 300')

_X1 = 'calc(50% - var(--fm-win) / 2 + 5px)'
_X2 = 'calc(50% + var(--fm-win) / 2 - 39px)'
_YT = 'calc(64px + var(--fm-ftop) + 5px)'
_YB = 'calc(var(--fm-dock) - 1px)'
_TOP_POS = ['left %s top %s' % (_X1, _YT), 'left %s top %s' % (_X2, _YT), 'left %s bottom %s' % (_X1, _YB), 'left %s bottom %s' % (_X2, _YB),
            None, 'center top calc(64px + var(--fm-ftop) - 42px)', 'center bottom 0']
_CX = 'calc(50% + var(--fm-win) / 2 - 9px)'
_COIN_FROM = 'left %s top calc(64px + var(--fm-ftop) + 70px)' % _CX
_COIN_TO = 'left %s bottom calc(var(--fm-dock) + 64px)' % _CX
_TOP_IMG = [corner(0), corner(1), corner(2), corner(3), COIN, lintel(), base()]
_TOP_SIZE = ['34px', '34px', '34px', '34px', '18px 18px', 'calc(var(--fm-win) + 300px) auto', 'calc(var(--fm-win) + 330px) auto']
def _pos(g): return [g if p is None else p for p in _TOP_POS]
TOPLAYERS = ', '.join('%s %s/%s no-repeat' % (i, p, z) for i, p, z in zip(_TOP_IMG, _pos(_COIN_TO), _TOP_SIZE))
COINFROM = ', '.join(_pos(_COIN_FROM))
COINTO = ', '.join(_pos(_COIN_TO))
out = T
for a, b in [('@ANIM@', '\n'.join(ANIM)), ('@KEYS@', '\n'.join(KEYS)), ('@SHOW@', SHOW), ('@ICONS@', ICONS), ('@BANNER@', BANNER), ('@SEP@', SEP),
             ('@EMBLEM@', EMBLEM), ('@MODSEL@', ','.join('.t-' + k for k in MODS)),
             ('@WINGL@', wing('lu')), ('@WINGR@', wing('yi', True)),
             ('@RAIN@', RAIN), ('@BANDM@', BAND_M), ('@TOPLAYERS@', TOPLAYERS), ('@COINFROM@', COINFROM), ('@COINTO@', COINTO),
             ('@GOLD@', GOLD), ('@GOLD2@', GOLD2), ('@L@', L), ('@O@', O), ('@IN@', IN), ('@SH@', SH), ('@R@', R)]:
    out = out.replace(a, b)
# 框里各块的底样式沿用 dm.css（色板、行卷字、玉牒、群英、风闻、经纬、藏卷、功能轮），去掉它的旧回复和整页两段
base = open(os.path.join(HERE, 'dm.css'), encoding='utf-8').read()
a, b = base.index('/* ===== 旧回复'), base.index('/* ===== 手机')
base = base[:a] + base[b:]
assert base.count('.dm-scroll,.dm-p,.dm-tip{') == 1
base = base.replace('.dm-scroll,.dm-p,.dm-tip{', '.dm-scroll,.dm-p,.dm-tip,.dm-hud,.dm-pane,.dm-acts-box,.dm-tabs{')
out = base + '\n' + out
open(sys.argv[1], 'w', encoding='utf-8').write(out)
print(len(out))
