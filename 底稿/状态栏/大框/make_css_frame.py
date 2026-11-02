# 大框版的样式（状态栏方向稿第四版的样张，不进卡）。用法：python3 -I -X utf8 make_css_frame.py 输出.css
# 整列一个大框：页面外壳上挂四样，左右两侧的浮雕（压在对话下面），框里一纪一种材质（对话滚动容器的背景，钉着不动），
# 框（金线、铁、石的边，压在对话上面、不挡点击），上下两条（顶上的浮雕和托着框的底，压在对话上面）。
# 框里一条回复是一页手札，最新一条底下一排页签，点哪个先暗下去转一枚这一纪的徽记，再亮起那一页（面板、背包……）。
# 页签图标照第三版那一份（../手札/make_css.py 的 ICON），读过来用。两侧的画写 __ART__/x，打包时换成图床地址。
import os, sys
from urllib.parse import quote
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, '..', '手札', 'make_css.py'), encoding='utf-8').read()
_ns = {}
exec(_src[_src.index('ICON = {'):_src.index('TINT = ')], _ns)
ICON = _ns['ICON']

def svg(body, vb='0 0 32 32'):
    s = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='%s'>%s</svg>" % (vb, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' -.,()")
def ic(k):
    return svg(ICON[k])
def noise(alpha, r, g, b, freq='.8'):
    s = ("<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='%s' numOctaves='3' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 %s 0 0 0 0 %s 0 0 0 0 %s 0 0 0 %s 0'/></filter><rect width='100%%' height='100%%' filter='url(#n)'/></svg>") % (freq, r, g, b, alpha)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' -.,()")

# ---- 五枚徽记（转场时转的那一枚；外面一圈刻度，里面这一纪的东西）----
def ring(c):
    ticks = ''.join("<path d='M60 4v7' transform='rotate(%d 60 60)'/>" % a for a in range(0, 360, 30))
    return ("<circle cx='60' cy='60' r='55' fill='none' stroke='%s' stroke-width='2'/><circle cx='60' cy='60' r='47' fill='none' stroke='%s' stroke-width='1' stroke-dasharray='1.5 5'/>"
            "<g stroke='%s' stroke-width='2' stroke-linecap='round'>%s</g>") % (c, c, c, ticks)
EMBLEM = {
    'moon': ring('#d9e2ef') + "<path d='M60 22L98 60L60 98L22 60Z' fill='none' stroke='#d9e2ef' stroke-width='2.4'/>"
            "<path d='M60 36C70 50 74 59 68 71C65 77 62 80 60 80C57 80 53 77 51 71C47 60 54 52 58 44C59 51 62 54 65 54C65 47 63 41 60 36Z' fill='#f4f7fb'/>",
    'strife': ring('#c9a27a') + "<path d='M38 94V50l6-6h32l6 6v44z' fill='#2a2725' stroke='#c9a27a' stroke-width='2.4'/>"
              "<path d='M44 44v-8h7v8M56.5 44v-8h7v8M69 44v-8h7v8' fill='none' stroke='#c9a27a' stroke-width='2.4'/>"
              "<path d='M51 94V74a9 9 0 0 1 18 0v20z' fill='#e0754a'/><path d='M30 28L92 98' stroke='#e0754a' stroke-width='3' stroke-linecap='round'/>",
    'bronze': ring('#d8d4cc') + "<path d='M60 22Q40 22 40 42V98H60Z' fill='#18191c' stroke='#d8d4cc' stroke-width='1.6'/>"
              "<path d='M60 22Q80 22 80 42V98H60Z' fill='#ecebe6' stroke='#d8d4cc' stroke-width='1.6'/>"
              "<g fill='#b88a52'><circle cx='60' cy='42' r='3'/><circle cx='60' cy='62' r='3'/><circle cx='60' cy='82' r='3'/></g>",
    'pre': ring('#d29a62') + "<circle cx='60' cy='60' r='30' fill='none' stroke='#d29a62' stroke-width='3'/>"
           "<path d='M60 36l5.5 18.5L84 60l-18.5 5.5L60 84l-5.5-18.5L36 60l18.5-5.5z' fill='#f0c08a'/>"
           "<circle cx='60' cy='60' r='4' fill='#3a2818'/>",
    'maze': ring('#e2c27c') + "<circle cx='60' cy='60' r='20' fill='#14213b' stroke='#e2c27c' stroke-width='1.6'/>"
            "<path d='M60 14l5 39 39 7-39 7-5 39-5-39-39-7 39-7z' fill='#f0d79a' stroke='#a8843f' stroke-width='.8'/>"
            "<path d='M60 38l2 18 18 4-18 4-2 18-2-18-18-4 18-4z' fill='#fff6dc' opacity='.85' transform='rotate(45 60 60)'/>",
}
def emblem(k):
    return svg(EMBLEM[k], '0 0 120 120')
def sep(c):
    return svg("<g stroke='%s' stroke-width='1' fill='none' opacity='.75'><path d='M8 12H100M140 12H232'/></g>"
               "<g fill='%s'><path d='M104 12l4-4 4 4-4 4z'/><path d='M128 12l4-4 4 4-4 4z'/><circle cx='96' cy='12' r='1.5'/><circle cx='144' cy='12' r='1.5'/></g>"
               "<path d='M120 2l2.6 7.4L130 12l-7.4 2.6L120 22l-2.6-7.4L110 12l7.4-2.6z' fill='%s'/>" % (c, c, c), '0 0 240 24')
def corner(c, c2):
    body = ("<g fill='none' stroke='%s' stroke-linecap='round'><path d='M3 58V20C3 10 10 3 20 3H58' stroke-width='1.8'/>"
            "<path d='M10 58V23C10 15 15 10 23 10H58' stroke-width='1'/><path d='M18 40C18 27 27 18 40 18' stroke-width='1.1'/></g>"
            "<path d='M12 2l2.2 7.8L22 12l-7.8 2.2L12 22l-2.2-7.8L2 12l7.8-2.2z' fill='%s'/>") % (c, c2)
    return [svg("<g transform='%s'>%s</g>" % (t, body), '0 0 60 60') for t in
            ['', 'translate(60 0) scale(-1 1)', 'translate(0 60) scale(1 -1)', 'translate(60 60) scale(-1 -1)']]
def band_top(c):   # 顶上那一条的占位（迷宫纪）：一道金线，正中一枚星，两边几颗点
    return svg("<g stroke='%s' fill='none'><path d='M40 70H330M470 70H760' stroke-width='1.4'/><path d='M120 82H330M470 82H680' stroke-width='.8'/></g>"
               "<g fill='%s'><circle cx='340' cy='70' r='3'/><circle cx='460' cy='70' r='3'/><circle cx='300' cy='56' r='2'/><circle cx='500' cy='56' r='2'/></g>"
               "<path d='M400 18l9 43 43 9-43 9-9 43-9-43-43-9 43-9z' fill='%s' stroke='#7a5e2a' stroke-width='1'/>" % (c, c, c), '0 0 800 140')
def band_bot(c, fill):   # 底下那一条的占位（迷宫纪）：一层云
    clouds = ''.join("<circle cx='%d' cy='%d' r='%d'/>" % (x, y, r) for x, y, r in
                     [(60, 120, 60), (150, 100, 55), (240, 118, 50), (330, 105, 40), (470, 105, 40), (560, 118, 50), (650, 100, 55), (740, 120, 60)])
    return svg("<g fill='%s' stroke='%s' stroke-width='2'>%s</g><rect y='130' width='800' height='30' fill='%s'/>" % (fill, c, clouds, fill), '0 0 800 160')

# ---- 一纪一种材质（框里的底、字、线、页签带、转场的幕）----
ERA = {
 'maze': dict(base='linear-gradient(180deg, #0b1224, #070c18)',
              mat=('radial-gradient(90%% 45%% at 50%% 0%%, rgb(96 128 196 / .24), transparent 70%%), radial-gradient(80%% 40%% at 50%% 100%%, rgb(214 178 106 / .10), transparent 70%%), %s, linear-gradient(180deg, #172440, #111b31 60%%, #0e172b)' % noise('.10', '.8', '.85', '1')),
              ink='#ebe5d6', ink2='#b3ad9f', head='#f2e2b6', acc='#d6b26a', acc2='#f0d48c', line='rgb(214 178 106 / .32)',
              band='#0e1830', band2='#0a1122', panel='rgb(255 255 255 / .035)', slot='rgb(255 255 255 / .05)', veil='rgb(6 10 22 / .93)', glow='#f0d48c',
              edge='#c9a75e', edge2='rgb(201 167 94 / .55)', relf='saturate(1)',
              l='url("__ART__/maze_left.webp")', r='url("__ART__/maze_right.webp")', top=band_top('#d6b26a'), bot=band_bot('#c9a75e', '#0e1830'), por1='#22355c', por2='#121d36'),
 'moon': dict(base='linear-gradient(180deg, #1b1d22, #111215)',
              mat=('radial-gradient(90%% 45%% at 50%% 0%%, rgb(220 230 245 / .10), transparent 70%%), %s, linear-gradient(180deg, #3c4048, #31353c 55%%, #2a2d33)' % noise('.16', '.95', '.95', '.95', '.65')),
              ink='#ece8df', ink2='#b6b2aa', head='#f6f2e8', acc='#c9d4e4', acc2='#ffffff', line='rgb(201 212 228 / .28)',
              band='#1e2128', band2='#15171c', panel='rgb(255 255 255 / .035)', slot='rgb(255 255 255 / .05)', veil='rgb(14 15 18 / .94)', glow='#dfe8f6',
              edge='#8e97a4', edge2='rgb(201 212 228 / .45)', relf='sepia(.22) saturate(.55) brightness(.92)',
              l='url("__ART__/moon_wing_l.svg")', r='url("__ART__/moon_wing_r.svg")', top='url("__ART__/moon_lintel.svg")', bot='url("__ART__/moon_base.svg")', por1='#4a4f58', por2='#2b2e34'),
 'strife': dict(base='linear-gradient(180deg, #1d1715, #120e0d)',
              mat=('linear-gradient(90deg, transparent 30px, rgb(150 50 30 / .32) 30px, rgb(150 50 30 / .32) 31.5px, transparent 31.5px), %s, radial-gradient(90%% 50%% at 50%% 0%%, rgb(255 248 230 / .5), transparent 70%%), linear-gradient(180deg, #e3d5b8, #d6c49f 60%%, #cab58b)' % noise('.14', '.35', '.25', '.12')),
              ink='#2b221d', ink2='#5d5047', head='#3a1d17', acc='#8f3a26', acc2='#e0754a', line='rgb(90 60 40 / .32)',
              band='#2c2826', band2='#1c1a19', panel='rgb(255 250 238 / .42)', slot='rgb(255 250 238 / .55)', veil='rgb(20 14 12 / .93)', glow='#ff8a4a',
              edge='#4a4542', edge2='rgb(143 58 38 / .6)', relf='saturate(1)', l='none', r='none', top='none', bot='none', por1='#d9c7a4', por2='#bfa982'),
 'bronze': dict(base='linear-gradient(90deg, #0d0e10 50%, #2a2b2e 50%)',
              mat=('%s, radial-gradient(90%% 50%% at 50%% 0%%, rgb(255 255 255 / .5), transparent 70%%), linear-gradient(180deg, #e9e7e2, #dcd9d1)' % noise('.12', '.2', '.2', '.22')),
              ink='#1f2023', ink2='#54565b', head='#121316', acc='#3c3f45', acc2='#9a7a4e', line='rgb(30 32 36 / .26)',
              band='#17181b', band2='#0e0f11', panel='rgb(255 255 255 / .5)', slot='rgb(255 255 255 / .62)', veil='rgb(12 12 14 / .94)', glow='#ffffff',
              edge='#18191c', edge2='rgb(184 138 82 / .7)', relf='saturate(1)', l='none', r='none', top='none', bot='none', por1='#d5d2ca', por2='#b9b5ab'),
 'pre': dict(base='linear-gradient(180deg, #1e1710, #130e09)',
              mat=('%s, radial-gradient(90%% 50%% at 50%% 0%%, rgb(255 252 240 / .55), transparent 70%%), linear-gradient(180deg, #f1e7cf, #e6d8b8 60%%, #ddcca8)' % noise('.13', '.4', '.28', '.12')),
              ink='#2b2620', ink2='#6b5d4c', head='#3b2a18', acc='#a5683a', acc2='#d29a62', line='rgb(120 80 40 / .30)',
              band='#33261a', band2='#24190f', panel='rgb(255 252 244 / .5)', slot='rgb(255 252 244 / .62)', veil='rgb(26 18 10 / .93)', glow='#f2b26a',
              edge='#8a5a32', edge2='rgb(165 104 58 / .6)', relf='saturate(1)', l='none', r='none', top='none', bot='none', por1='#e7d6b2', por2='#cdb88f'),
}
CORNERC = {'maze': ('#c9a75e', '#f0d79a'), 'moon': ('#9aa4b2', '#e8eef6'), 'strife': ('#5a5450', '#c96a40'), 'bronze': ('#b88a52', '#e9d3a8'), 'pre': ('#8a5a32', '#e2a86c')}

R = '.rili-markdown-renderer:has(.sz-hud)'
ROW = 'div[style*="contain: layout"]'
L = ROW + ':has(.sz-hud):not(:has(~ div .sz-hud))'          # 最新一条
O = ROW + ':has(.sz-hud):has(~ div .sz-hud)'                  # 旧的
SH = ':root:has(#conversation)'
IN = SH + ' > div:has(#conversation)'
TABS = ['prose', 'panel', 'deed', 'bag', 'party', 'news', 'mem', 'war']
MODS = TABS[1:]

css = []
w = css.append
w('/* ==== 大框（状态栏方向稿第四版的样张）：整列一个大框，浮雕钉在框外，一纪一种材质，页签暗下去转徽记再进那一页 ==== */')
# 一纪一组变量，挂在外壳上，框里的回复照它
for k, e in ERA.items():
    cl = corner(*CORNERC[k])
    w('%s:has(.era-%s){--fm-base:%s;--fm-mat:%s;--fm-ink:%s;--fm-ink2:%s;--fm-head:%s;--fm-acc:%s;--fm-acc2:%s;--fm-line:%s;'
      '--fm-band:%s;--fm-band2:%s;--fm-panel:%s;--fm-slot:%s;--fm-veil:%s;--fm-glow:%s;--fm-edge:%s;--fm-edge2:%s;--fm-relf:%s;'
      '--fm-l:%s;--fm-r:%s;--fm-top:%s;--fm-bot:%s;--fm-por1:%s;--fm-por2:%s;--fm-emblem:%s;--fm-sep:%s;--fm-c1:%s;--fm-c2:%s;--fm-c3:%s;--fm-c4:%s}'
      % (SH, k, e['base'], e['mat'], e['ink'], e['ink2'], e['head'], e['acc'], e['acc2'], e['line'], e['band'], e['band2'], e['panel'], e['slot'],
         e['veil'], e['glow'], e['edge'], e['edge2'], e['relf'], e['l'], e['r'], e['top'], e['bot'], e['por1'], e['por2'], emblem(k), sep(e['acc']), *cl))
T = r'''
/* ---------- 整页：外壳的底、框里的材质（滚动容器的背景，钉着不动） ---------- */
@SH@:has(.sz-hud){
  isolation:isolate;--fm-dock:96px;--fm-topband:46px;--fm-colw:672px;
  --sz-t:calc(var(--sz-h, 12) + var(--sz-m, 0) / 60);
  --sz-day:clamp(0, sin(calc((var(--sz-t) - 6) * 15deg)), 1);
  background:var(--fm-base)!important;
}
@SH@:has(.sz-hud) #conversation{background:var(--fm-mat);background-size:var(--fm-colw) 100%;background-position:center top;background-repeat:no-repeat}
header>div:nth-child(2)::before{content:"";width:200px;height:30px;opacity:var(--sz-on, 0);background:@BANNER@ center/contain no-repeat}

/* ---------- 框里：一条回复是一页手札，不另加卡 ---------- */
@R@{background:none!important;color:var(--fm-ink)!important;width:min(640px, calc(100vw - 36px));padding:4px 4px 6px!important;margin:6px 0 4px!important;border:0!important;box-shadow:none!important;position:relative}
@R@::before{content:"";display:block;height:20px;width:240px;max-width:70%;margin:0 auto 10px;background:var(--fm-sep) center/contain no-repeat}
@R@ details.sz-hud{margin:0 0 6px!important;padding:0!important;border:0!important;background:none!important;box-shadow:none!important}
@R@ details.sz-hud>summary.sz-head{display:block!important;min-height:0!important;padding:0 64px 0 0!important;margin:0!important;border:0!important;background:none!important;cursor:pointer;list-style:none;position:relative;text-align:left}
@R@ details.sz-hud>summary.sz-head::-webkit-details-marker{display:none}
@R@ details.sz-hud>summary.sz-head::after{content:none!important}
@R@ .sz-sub{display:flex;flex-wrap:wrap;align-items:center;gap:4px 14px;font-size:12.5px;color:var(--fm-ink2);letter-spacing:.06em}
@R@ .sz-sub>span{display:inline-flex;align-items:center;gap:7px}
@R@ .sz-place::before{content:"";width:9px;height:9px;background:var(--fm-acc);-webkit-mask:@STAR@ center/contain no-repeat;mask:@STAR@ center/contain no-repeat}
@R@ .sz-year{padding-left:14px;border-left:1px solid var(--fm-line)}
@R@ .sz-year:empty{display:none!important}
@R@ .sz-time{opacity:.8}
@R@ .sz-time::before{content:"·";margin-right:-2px}
@R@ .sz-more{position:absolute;right:0;top:-1px;font-size:11px;color:var(--fm-ink2);letter-spacing:.1em;border:1px solid var(--fm-line);border-radius:10px;padding:0 8px 0 9px}
@R@ .sz-more::after{content:" ▾"}
@R@ details.sz-hud[open] .sz-more::after{content:" ▴"}
@R@ .sz-hud-body{margin:10px 0 6px;padding:10px 12px;border:1px solid var(--fm-line);border-radius:10px;background:var(--fm-panel);font-size:12.5px;line-height:1.6;color:var(--fm-ink2)}
@R@ .sz-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px 12px;margin-bottom:8px}
@R@ .sz-grid b{display:block;font-size:11px;color:var(--fm-acc);font-weight:600}
@R@ .sz-f.d{display:grid;grid-template-columns:5.6em 1fr;gap:8px;padding:4px 0;border-top:1px dashed var(--fm-line)}
@R@ .sz-f.d b{color:var(--fm-acc);font-weight:600;font-size:12px}
/* 三条：只在最新一条 */
@R@ .sz-bars{display:none;grid-template-columns:repeat(3,1fr);gap:8px 20px;margin:12px 0 2px}
@L@ .sz-bars{display:grid}
@R@ .sz-bar{display:grid;grid-template-columns:20px auto 1fr;grid-template-rows:auto 6px;align-items:center;column-gap:6px;row-gap:4px;font-size:12px;color:var(--fm-ink2)}
@R@ .sz-bar>i{grid-row:1/3;width:20px;height:20px;background:var(--c);-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}
@R@ .sz-bar b{font-weight:700!important;color:var(--fm-ink)!important;font-size:12px!important;display:inline!important}
@R@ .sz-bar em{font-style:normal;font-variant-numeric:tabular-nums}
@R@ .sz-bar .sz-trk{grid-column:2/4;height:6px;border-radius:3px;background:rgb(128 128 128 / .22);position:relative;overflow:hidden}
@R@ .sz-bar .sz-trk::after{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(min(var(--v), var(--m)) / var(--m) * 100%);border-radius:3px;background:linear-gradient(90deg, color-mix(in srgb, var(--c) 65%, #fff), var(--c))}
@R@ .sz-bar.hp{--c:#5aa883;--ic:@HP@}
@R@ .sz-bar.mp{--c:#5f92d6;--ic:@MP@}
@R@ .sz-bar.sp{--c:#d4a94c;--ic:@SP@}
@R@ .sz-bar.st{--c:#b0745a}

/* ---------- 手札这一页 ---------- */
@R@ .sz-page{position:relative}
@R@ .sz-sec{display:flex;align-items:center;gap:14px;margin:14px 0 14px}
@R@ .sz-sec::before,@R@ .sz-sec::after{content:"";flex:1;height:1px;background:linear-gradient(90deg, transparent, var(--fm-acc))}
@R@ .sz-sec::after{background:linear-gradient(270deg, transparent, var(--fm-acc))}
@R@ .sz-sec span{font-family:var(--fm-serif);font-size:17px;font-weight:700;letter-spacing:.14em;color:var(--fm-head);text-align:center}
@R@ .sz-prose p{margin:0 0 16px!important;font-family:var(--fm-serif);font-size:16.5px;line-height:1.95;color:var(--fm-ink);text-indent:0}
@R@ .sz-qc{display:flex;flex-direction:column;align-items:center;gap:2px;margin:0 0 16px;padding:10px 0;border-top:1px solid var(--fm-line);border-bottom:1px solid var(--fm-line)}
@R@ .sz-qc .qc-pian{font-size:12px;color:var(--fm-acc);letter-spacing:.2em}
@R@ .sz-qc .qc-ml{font-family:var(--fm-serif);font-size:19px;color:var(--fm-head)}
@R@ .sz-qc .qc-desc{font-size:12.5px;color:var(--fm-ink2)}
@R@{--fm-serif:"Noto Serif SC","Source Han Serif SC","Songti SC","STSong","Noto Serif CJK SC",serif}
/* 分支：只在最新一条；短的并排，长的一行，自定义那一条只写自行决定 */
@R@ .sz-choices{display:none}
@L@ .sz-choices{display:block}
@R@ .sz-choices ol{list-style:none!important;display:flex;flex-wrap:wrap;align-items:center;gap:10px 12px;margin:6px 0 18px!important;padding:0!important}
@R@ .sz-choices li{display:inline-flex!important;align-items:center;gap:10px;max-width:100%;margin:0!important;padding:9px 20px 9px 14px;border-radius:10px;border:1px solid var(--fm-edge2);
  background:linear-gradient(color-mix(in srgb, var(--fm-acc) 10%, transparent), color-mix(in srgb, var(--fm-acc) 4%, transparent));color:var(--fm-ink);font-size:14.5px;line-height:1.55!important;cursor:pointer;transition:background .15s, border-color .15s}
@R@ .sz-choices li::before{content:"";flex:none;width:11px;height:11px;background:var(--fm-acc);-webkit-mask:@STAR@ center/contain no-repeat;mask:@STAR@ center/contain no-repeat}
@R@ .sz-choices li:hover{border-color:var(--fm-acc);background:color-mix(in srgb, var(--fm-acc) 18%, transparent)}
@R@ .sz-choices li.sz-free{margin-left:auto!important;padding:6px 2px 4px;border:0;border-bottom:1px solid var(--fm-line);border-radius:0;background:none;cursor:default}
@R@ .sz-choices li.sz-free::before,@R@ .sz-choices li.sz-free span{display:none}
@R@ .sz-choices li.sz-free::after{content:"自行决定  ›";letter-spacing:.08em;font-size:14px;color:var(--fm-ink2)}

/* ---------- 页签：只在最新一条，贴在框底；点哪一页，那一页顶替手札 ---------- */
@R@ .sz-tabs{display:none}
@L@ .sz-tabs{display:flex;align-items:stretch;margin:6px -4px 0;padding:10px 8px 8px;position:sticky;bottom:calc(var(--fm-dock) + 6px);z-index:4;
  background:linear-gradient(var(--fm-band), var(--fm-band2));border:1px solid var(--fm-edge2);border-radius:14px;box-shadow:0 8px 24px rgb(0 0 0 / .35)}
@R@ .sz-tab{flex:1;display:flex!important;flex-direction:column;align-items:center;gap:4px;color:#e9e2cf;cursor:pointer;position:relative;padding-bottom:6px;user-select:none}
@R@ .sz-tab input,@R@ .sz-x input{display:none!important}
@R@ .sz-tab i{width:26px;height:26px;background:currentColor;-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}
@R@ .sz-tab b{font-size:12px!important;font-weight:500!important;letter-spacing:.1em;color:inherit!important;display:block!important}
@R@ .sz-tab+.sz-tab::before{content:"";position:absolute;left:0;top:16px;width:4px;height:4px;transform:translateX(-50%) rotate(45deg);background:var(--fm-edge2)}
@R@ .sz-tab:hover{color:#fff}
@L@ .sz-tab:has(input:checked),@L@:not(:has(.sz-tab input:checked)) .t-prose{color:var(--fm-acc2)}
@L@ .sz-tab:has(input:checked)::after,@L@:not(:has(.sz-tab input:checked)) .t-prose::after{content:"";position:absolute;bottom:0;left:26%;right:26%;height:2px;border-radius:2px;background:var(--fm-acc2);box-shadow:0 0 8px var(--fm-acc2)}
@R@:not(:has(.p-war)) .t-war{opacity:.32;pointer-events:none}
@ICONS@
/* 几页：平时只露手札；最新一条点了页签，那一页顶上来，手札收起 */
@R@ .sz-pane{display:none}
@SHOW@
@L@:has(:is(@MODSEL@) input:checked) .sz-prose{display:none}
@O@ .sz-pane{display:none!important}
@O@ .sz-prose{display:block!important}
@L@ .sz-pane{min-height:calc(100dvh - var(--fm-dock) - 250px)}
@L@ .rili-markdown-renderer{padding-bottom:calc(var(--fm-dock) + 18px)!important}

/* ---------- 转场：先暗下去，正中转一枚这一纪的徽记，再亮起那一页 ---------- */
@L@ .sz-tabs::before{content:"";position:absolute;left:-1px;right:-1px;bottom:calc(100% + 1px);height:calc(100dvh - var(--fm-dock) - 190px);border-radius:14px 14px 0 0;background:var(--fm-veil);opacity:0;pointer-events:none}
@L@ .sz-tabs::after{content:"";position:absolute;left:50%;width:108px;height:108px;margin-left:-54px;bottom:calc(100% + (100dvh - var(--fm-dock) - 190px) / 2 - 54px);background:var(--fm-emblem) center/contain no-repeat;opacity:0;pointer-events:none;filter:drop-shadow(0 0 14px var(--fm-glow))}
@ANIM@
@KEYS@
@media (prefers-reduced-motion:reduce){@L@ .sz-tabs::before,@L@ .sz-tabs::after{animation:none!important}}

/* ---------- 各页的样子：像游戏里打开角色、背包那样的一屏 ---------- */
@R@ .sz-pane{padding:14px 16px 16px;border-radius:14px;background:var(--fm-panel);border:1px solid var(--fm-line);box-shadow:inset 0 0 0 3px color-mix(in srgb, var(--fm-acc) 6%, transparent)}
@R@ .sz-pane-head{display:flex;align-items:center;gap:10px;margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid var(--fm-line)}
@R@ .sz-pane-head i{width:22px;height:22px;background:var(--fm-acc);-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}
@R@ .sz-pane-head b{font-family:var(--fm-serif);font-size:18px!important;font-weight:700!important;letter-spacing:.14em;color:var(--fm-head)!important}
@R@ .sz-x{margin-left:auto;font-size:12px;color:var(--fm-ink2);cursor:pointer;border:1px solid var(--fm-line);border-radius:10px;padding:2px 12px}
@R@ .sz-x:hover{color:var(--fm-ink);border-color:var(--fm-acc)}
@R@ .sz-f:not(.d){display:grid;grid-template-columns:4.8em 1fr;gap:10px;padding:7px 0;border-bottom:1px dashed var(--fm-line);font-size:13.5px;line-height:1.65}
@R@ .sz-f:not(.d)>b{color:var(--fm-acc);font-weight:600}
/* 面板：左边一格立绘，右边身份、等级、四条，底下六维，再往下各行 */
@R@ .p-panel .sz-pane-body{display:grid;grid-template-columns:150px 1fr;column-gap:18px}
@R@ .p-panel .sz-pane-body::before{content:"";grid-column:1;grid-row:1 / span 3;min-height:190px;border-radius:12px;border:1px solid var(--fm-edge2);
  background:@BUST@ center 78%/78% no-repeat, radial-gradient(circle at 50% 32%, var(--fm-por1), var(--fm-por2))}
@R@ .p-panel .sz-f{grid-column:1 / -1}
@R@ .p-panel .sz-f[data-k="身份"]{grid-column:2;grid-row:1;grid-template-columns:1fr;font-size:15px;border:0;padding-top:2px}
@R@ .p-panel .sz-f[data-k="身份"]>b{display:none}
@R@ .p-panel .sz-lv{grid-column:2;grid-row:2;grid-template-columns:auto auto 1fr!important;align-items:center;border:0!important}
@R@ .p-panel .sz-res{grid-column:2;grid-row:3;grid-template-columns:1fr!important;border:0!important}
@R@ .p-panel .sz-six{grid-row:4;grid-template-columns:1fr!important}
@R@ .sz-lv>b,@R@ .sz-res>b,@R@ .sz-six>b{display:none}
@R@ .sz-lvl{display:inline-flex;align-items:baseline;gap:4px;padding:2px 12px;border-radius:999px;border:1px solid var(--fm-acc);font-family:var(--fm-serif);font-size:22px;font-weight:700;color:var(--fm-head)}
@R@ .sz-lvl small{font-size:11px;color:var(--fm-acc);letter-spacing:.1em}
@R@ .sz-tier{color:var(--fm-ink2);font-size:13px}
@R@ .sz-lv em{grid-column:1 / -1;font-style:normal;font-size:12px;color:var(--fm-ink2)}
@R@ .sz-lv .sz-trk{grid-column:1 / -1;height:5px;border-radius:3px;background:rgb(128 128 128 / .22);position:relative;overflow:hidden}
@R@ .sz-lv .sz-trk::after{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(min(var(--v), var(--m)) / var(--m) * 100%);background:var(--fm-acc)}
@R@ .sz-lv .sz-note{grid-column:1 / -1;font-size:11.5px;color:var(--fm-ink2)}
@R@ .sz-res-bars{display:grid;grid-template-columns:1fr 1fr;gap:8px 16px}
@R@ .sz-res .sz-bar{grid-template-columns:auto 1fr}
@R@ .sz-res .sz-bar .sz-trk{grid-column:1 / -1}
@R@ .sz-chips{font-size:12px;color:var(--fm-ink2);margin-top:6px}
@R@ .sz-cells{display:grid;grid-template-columns:repeat(6,1fr);gap:8px}
@R@ .sz-cells>i{font-style:normal;display:flex;flex-direction:column;align-items:center;padding:8px 4px 6px;border-radius:10px;border:1px solid var(--fm-line);background:var(--fm-slot)}
@R@ .sz-cells>i>b{font-size:11px;color:var(--fm-acc);letter-spacing:.08em}
@R@ .sz-cells>i>strong{font-family:var(--fm-serif);font-size:24px;line-height:1.2;color:var(--fm-head)}
@R@ .sz-cells>i>small{font-size:10px;color:var(--fm-ink2);text-align:center;line-height:1.3}
/* 背包：一类一排，东西一格一格 */
@R@ .sz-bagrow{display:block!important;border-bottom:0!important}
@R@ .sz-bagrow>b{display:block;margin-bottom:6px;font-size:12.5px;letter-spacing:.1em}
@R@ .sz-slots{display:grid;grid-template-columns:repeat(auto-fill, minmax(118px, 1fr));gap:8px}
@R@ .sz-slots>i{font-style:normal;position:relative;display:flex;align-items:flex-end;min-height:66px;padding:26px 10px 8px;border-radius:10px;border:1px solid var(--fm-line);background:var(--fm-slot);font-size:12.5px;line-height:1.45;color:var(--fm-ink)}
@R@ .sz-slots>i::before{content:"";position:absolute;top:8px;left:10px;width:14px;height:14px;background:var(--fm-acc);-webkit-mask:@STAR@ center/contain no-repeat;mask:@STAR@ center/contain no-repeat;opacity:.8}
/* 同行：一人一张 */
@R@ .sz-npc{display:grid;grid-template-columns:64px 1fr;gap:12px;padding:8px 0}
@R@ .sz-npc-av{width:64px;height:64px;border-radius:50%;border:2px solid var(--fm-edge2);background:radial-gradient(circle at 50% 35%, var(--fm-por1), var(--fm-por2));display:grid;place-items:center;font-family:var(--fm-serif);font-size:24px;color:var(--fm-head)}
@R@ .sz-npc-av::before{content:attr(data-n);display:block;width:1em;overflow:hidden;white-space:nowrap}
@R@ .sz-npc-name b{font-family:var(--fm-serif);font-size:17px!important;color:var(--fm-head)!important;margin-right:10px}
@R@ .sz-npc-name span{font-size:12px;color:var(--fm-ink2)}
@R@ .sz-npc-tags{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
@R@ .sz-npc-tags span{font-size:11.5px;padding:1px 8px;border-radius:9px;background:color-mix(in srgb, var(--fm-acc) 18%, transparent);color:var(--fm-ink)}
@R@ .sz-npc-tags span:empty{display:none}
@R@ p.sz-npc-say{margin:4px 0 8px!important;font-family:var(--fm-serif);font-size:14.5px;color:var(--fm-ink)}
@R@ .sz-nf{display:grid;grid-template-columns:5.2em 1fr;gap:8px;padding:4px 0;font-size:12.5px;line-height:1.6;border-top:1px dashed var(--fm-line)}
@R@ .sz-nf b{color:var(--fm-acc);font-weight:600}
@R@ details.sz-more2>summary{min-height:0!important;padding:4px 0!important;font-size:12px;color:var(--fm-ink2);background:none!important;border:0!important}
/* 玩家说的话：一道细线，不另起一块 */
:root:has(.sz-hud) .is-user .bubble{background:color-mix(in srgb, var(--fm-acc) 14%, transparent)!important;border:1px solid color-mix(in srgb, var(--fm-acc) 40%, transparent);color:var(--fm-ink)}

/* ---------- 宽屏：框外挂浮雕，框和上下两条压在对话上面（不挡点击） ---------- */
@media (min-width:1100px){
  @IN@::before,@IN@::after{content:"";position:absolute;top:-64px;bottom:0;width:calc(50% - 344px);z-index:-1;pointer-events:none;background-repeat:no-repeat;background-size:cover;
    filter:var(--fm-relf) brightness(calc(.55 + .45 * var(--sz-day)))}
  @IN@::before{left:0;background-image:var(--fm-l);background-position:right center}
  @IN@::after{right:0;background-image:var(--fm-r);background-position:left center}
  @SH@:has(.sz-hud)::after{content:"";position:absolute;left:calc(50% - 346px);width:692px;top:calc(var(--fm-topband) - 10px);bottom:calc(var(--fm-dock) - 6px);z-index:2;pointer-events:none;
    border:2px solid var(--fm-edge);border-radius:16px;box-shadow:inset 0 0 0 4px color-mix(in srgb, var(--fm-band) 80%, transparent), inset 0 0 0 5px var(--fm-edge2), 0 0 0 1px rgb(0 0 0 / .45), 0 0 30px rgb(0 0 0 / .55);
    background:var(--fm-c1) left 2px top 2px/54px no-repeat, var(--fm-c2) right 2px top 2px/54px no-repeat, var(--fm-c3) left 2px bottom 2px/54px no-repeat, var(--fm-c4) right 2px bottom 2px/54px no-repeat}
  @SH@:has(.sz-hud)::before{content:"";position:absolute;left:0;right:0;top:-64px;bottom:0;z-index:3;pointer-events:none;
    background:var(--fm-top) center top/auto calc(64px + var(--fm-topband) + 20px) no-repeat, var(--fm-bot) center bottom/auto calc(var(--fm-dock) + 30px) no-repeat,
      linear-gradient(var(--fm-band2), var(--fm-band2)) center top/700px calc(64px + var(--fm-topband) - 10px) no-repeat,
      linear-gradient(var(--fm-band2), var(--fm-band2)) center bottom/700px calc(var(--fm-dock) - 6px) no-repeat}
}
@SH@:has(.era-bronze)::after{border-image:linear-gradient(90deg, #111214 50%, #ecebe6 50%) 1!important;border-width:4px!important}
/* ---------- 手机：不挂浮雕，框只留一圈细边，上下各一道窄纹 ---------- */
@media (max-width:1099px){
  @SH@:has(.sz-hud){--fm-dock:84px;--fm-colw:100%}
  @SH@:has(.sz-hud)::after{content:"";position:absolute;left:5px;right:5px;top:4px;bottom:calc(var(--fm-dock) - 4px);z-index:2;pointer-events:none;border:1.5px solid var(--fm-edge);border-radius:12px;box-shadow:inset 0 0 0 3px color-mix(in srgb, var(--fm-band) 70%, transparent), inset 0 0 0 4px var(--fm-edge2);
    background:var(--fm-sep) center top 4px/150px 14px no-repeat, var(--fm-sep) center bottom 4px/150px 14px no-repeat}
  @SH@:has(.sz-hud)::before{content:"";position:absolute;left:0;right:0;top:-64px;bottom:0;z-index:3;pointer-events:none;
    background:linear-gradient(var(--fm-band2), var(--fm-band2)) center top/100% 68px no-repeat, linear-gradient(var(--fm-band2), var(--fm-band2)) center bottom/100% calc(var(--fm-dock) - 4px) no-repeat}
  @R@{width:calc(100vw - 30px)}
  @R@ .sz-prose p{font-size:15.5px;line-height:1.9}
  @R@ .sz-bars{gap:8px 10px}
  @R@ .sz-bars .sz-bar{grid-template-columns:16px auto;font-size:11px}
  @R@ .sz-bars .sz-bar>i{width:16px;height:16px;grid-row:1}
  @R@ .sz-bars .sz-bar b{display:none!important}
  @R@ .sz-bars .sz-bar .sz-trk{grid-column:1/3}
  @R@ .sz-tab i{width:22px;height:22px}
  @R@ .sz-tab b{font-size:10.5px!important;letter-spacing:.04em}
  @R@ .sz-tab+.sz-tab::before{top:13px;width:3px;height:3px}
  @L@ .sz-tabs{padding:8px 2px 6px}
  @R@ .p-panel .sz-pane-body{grid-template-columns:96px 1fr;column-gap:12px}
  @R@ .p-panel .sz-pane-body::before{min-height:130px}
  @R@ .sz-cells{grid-template-columns:repeat(3,1fr)}
  @R@ .sz-res-bars{grid-template-columns:1fr}
  @R@ .sz-grid{grid-template-columns:repeat(2,1fr)}
}
'''
ANIM, KEYS = [], []
for n, k in enumerate(TABS):
    sel = '%s:has(.t-%s input:checked)' % (L, k)
    if k == 'prose':
        sel = '%s:has(.t-prose input:checked),%s:has(.sz-x input:checked)' % (L, L)
    ANIM.append('%s .sz-tabs::before{animation:fm-v%d .95s ease-out}' % (sel.replace(',', ' .sz-tabs::before,') if k == 'prose' else sel, n))
    ANIM.append('%s .sz-tabs::after{animation:fm-e%d .95s ease-out}' % (sel.replace(',', ' .sz-tabs::after,') if k == 'prose' else sel, n))
    KEYS.append('@keyframes fm-v%d{0%%{opacity:.96}52%%{opacity:.96}100%%{opacity:0}}' % n)
    KEYS.append('@keyframes fm-e%d{0%%{opacity:1;transform:rotate(-200deg) scale(.55)}55%%{opacity:1;transform:rotate(0deg) scale(1)}100%%{opacity:0;transform:rotate(50deg) scale(1.3)}}' % n)
SHOW = '\n'.join('%s:has(.t-%s input:checked) .p-%s{display:block}' % (L, k, k) for k in MODS)
ICONS = '\n'.join('%s :is(.t-%s,.p-%s){--ic:%s}' % (R, k, k, ic('quill' if k == 'prose' else k)) for k in TABS)
BUST = svg("<circle cx='16' cy='10' r='6.4' fill='rgb(255 255 255 / .22)'/><path d='M3 32c.6-8.6 6-13.4 13-13.4S28.4 23.4 29 32z' fill='rgb(255 255 255 / .22)'/>")
BANNER = svg("<g stroke='#c9a75e' stroke-width='1' fill='none'><path d='M6 20H96M144 20H234'/></g><g fill='#c9a75e'><path d='M100 20l3-3 3 3-3 3z'/><path d='M134 20l3-3 3 3-3 3z'/></g>"
             "<path d='M120 4l3 13 13 3-13 3-3 13-3-13-13-3 13-3z' fill='#ecd497'/>", '0 0 240 40')
out = T
for a, b in [('@ANIM@', '\n'.join(ANIM)), ('@KEYS@', '\n'.join(KEYS)), ('@SHOW@', SHOW), ('@ICONS@', ICONS), ('@BUST@', BUST), ('@BANNER@', BANNER),
             ('@MODSEL@', ','.join('.t-' + k for k in MODS)), ('@STAR@', ic('star4')), ('@HP@', ic('hp')), ('@MP@', ic('mp')), ('@SP@', ic('sp')),
             ('@L@', L), ('@O@', O), ('@IN@', IN), ('@SH@', SH), ('@R@', R)]:
    out = out.replace(a, b)
w(out)
open(sys.argv[1], 'w', encoding='utf-8').write('\n'.join(css))
print(sum(len(x) for x in css))
