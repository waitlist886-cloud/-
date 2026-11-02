# 手札版的样式（状态栏方向稿第三版的样张，不进卡）。用法：python3 -I -X utf8 make_css.py 输出.css
# 小图（框角、徽记、页签图标、三条的图标）都是手画的 SVG，写进样式；两侧的整幅画写 __ART__/x.webp，打包时换成图床地址。
# 只认展开以后的新类名（sz-），旧回复照旧用旧样式。
import sys
from urllib.parse import quote

def svg(body, vb='0 0 32 32'):
    s = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='%s'>%s</svg>" % (vb, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' -.,()")

ICON = {
    # 页签七个（单色，拿来当遮罩，颜色跟着字色走）
    'panel': "<circle cx='16' cy='10.5' r='6.2'/><path d='M4.5 29.5c.6-7.4 5.4-11.6 11.5-11.6s10.9 4.2 11.5 11.6z'/>",
    'deed': "<path d='M16 5.5l2.3 6.6 6.6 2.3-6.6 2.3L16 23.3l-2.3-6.6-6.6-2.3 6.6-2.3z'/>"
            "<g fill='none' stroke='#000' stroke-width='1.5' stroke-linecap='round'><path d='M8.2 26.8C3.4 22.8 2.4 15.6 5.4 9.6'/><path d='M23.8 26.8c4.8-4 5.8-11.2 2.8-17.2'/></g>"
            "<ellipse cx='3.9' cy='14' rx='1.2' ry='2.5' transform='rotate(-18 3.9 14)'/><ellipse cx='4.4' cy='19.5' rx='1.2' ry='2.5' transform='rotate(-40 4.4 19.5)'/><ellipse cx='7' cy='24.2' rx='1.2' ry='2.5' transform='rotate(-62 7 24.2)'/>"
            "<ellipse cx='28.1' cy='14' rx='1.2' ry='2.5' transform='rotate(18 28.1 14)'/><ellipse cx='27.6' cy='19.5' rx='1.2' ry='2.5' transform='rotate(40 27.6 19.5)'/><ellipse cx='25' cy='24.2' rx='1.2' ry='2.5' transform='rotate(62 25 24.2)'/>"
            "<path d='M12.5 28.5h7' stroke='#000' stroke-width='1.6' stroke-linecap='round'/>",
    'bag': "<path d='M11.5 9.5V8a4.5 4.5 0 0 1 9 0v1.5' fill='none' stroke='#000' stroke-width='2.2'/>"
           "<path fill-rule='evenodd' d='M8 9.5h16a3.5 3.5 0 0 1 3.5 3.5v12.5A3.5 3.5 0 0 1 24 29H8a3.5 3.5 0 0 1-3.5-3.5V13A3.5 3.5 0 0 1 8 9.5zM5.8 15.2v1.6h20.4v-1.6zM13.4 14.2h5.2v5.4h-5.2z'/>",
    'party': "<defs><mask id='m'><rect width='32' height='32' fill='#fff'/><circle cx='11.5' cy='12' r='7.6' fill='#000'/><path d='M-.5 31.5c.6-7.6 5.4-12.4 12-12.4s11.4 4.8 12 12.4z' fill='#000'/></mask></defs>"
             "<g mask='url(#m)'><circle cx='21.5' cy='9.6' r='5'/><path d='M12.6 27c.7-6 4.3-9.4 8.9-9.4s8.2 3.4 8.9 9.4z'/></g>"
             "<circle cx='11.5' cy='12' r='5.6'/><path d='M1.4 29.5c.6-6.6 4.6-10.4 10.1-10.4s9.5 3.8 10.1 10.4z'/>",
    'news': "<path d='M2.5 12c4.8-1.6 9.1-1 12.5 1.6v16c-3.4-2.4-7.7-3-12.5-1.6zM29.5 12c-4.8-1.6-9.1-1-12.5 1.6v16c3.4-2.4 7.7-3 12.5-1.6z'/>"
            "<path d='M16 1.2l1.3 3.6 3.6 1.3-3.6 1.3L16 11l-1.3-3.6L11.1 6.1l3.6-1.3z'/>",
    'mem': "<path d='M23.5 2.2C15.8 3.4 9.9 9.3 8.2 17.4L6.2 26l1.6.6 2.3-6.4c7.4-2 12.8-8.4 13.4-18z'/>"
           "<path fill-rule='evenodd' d='M23.5 16.4a7.1 7.1 0 1 1 0 14.2a7.1 7.1 0 1 1 0-14.2zm-1 2.6v5.3l3.8 2.3 1-1.6-2.8-1.7V19z'/>",
    'war': "<g stroke='#000' stroke-linecap='round'><path d='M5.5 4.5l15.8 15.8M26.5 4.5L10.7 20.3' stroke-width='2.6'/>"
           "<path d='M18.6 25.4l6.8-6.8M6.6 18.6l6.8 6.8' stroke-width='2.4'/><path d='M23.4 23.4l4.4 4.4M8.6 23.4l-4.4 4.4' stroke-width='3.2'/></g>",
    # 三条
    'hp': "<path d='M16 28s-10-6.1-12.8-12.2C1.2 11.2 3.9 6 8.8 6c2.9 0 4.8 1.7 7.2 4.3C18.4 7.7 20.3 6 23.2 6c4.9 0 7.6 5.2 5.6 9.8C26 21.9 16 28 16 28z'/>",
    'mp': "<path fill-rule='evenodd' d='M16 2l8 10-8 18-8-18zM16 6.2L11.2 12h9.6z'/>",
    'sp': "<path d='M16 2l3.4 10.6L30 16l-10.6 3.4L16 30l-3.4-10.6L2 16l10.6-3.4z'/>",
    # 手札的羽毛笔、分支前的小星
    'quill': "<path d='M28.5 3C19 4.4 11.6 11.4 9.4 21.2L7 29.5l1.7.6 2.7-7.8c9.1-2.4 15.8-10 17.1-19.3zM11.9 21.2c1.2-4.4 3.5-8.2 6.6-10.9-2.1 3.2-3.8 6.8-4.8 10.5z'/>",
    'star4': "<path d='M16 3l3 10 10 3-10 3-3 10-3-10-10-3 10-3z'/>",
}
TINT = {'hp': '#5aa883', 'mp': '#5f92d6', 'sp': '#d4a94c'}

# 框角：左上一只，另三只照它翻
CORNER = ("<g fill='none' stroke='#c9a75e' stroke-linecap='round'><path d='M3 70V22C3 11 11 3 22 3H70' stroke-width='1.6'/>"
          "<path d='M9 70V25C9 16 16 9 25 9H70' stroke-width='1'/><path d='M16 46C16 28 28 16 46 16' stroke-width='1.1'/>"
          "<path d='M23 34c0-6 5-11 11-11' stroke-width='1.1'/></g>"
          "<path d='M14 3.5l2.4 8.1 8.1 2.4-8.1 2.4L14 24.5l-2.4-8.1L3.5 14l8.1-2.4z' fill='#ecd497' stroke='#a8843f' stroke-width='.7'/>"
          "<circle cx='33.5' cy='33.5' r='2.3' fill='#c9a75e'/>")
def corner(t):
    return svg("<g transform='%s'>%s</g>" % (t, CORNER), '0 0 72 72')
C_TL, C_TR, C_BL, C_BR = corner(''), corner('translate(72 0) scale(-1 1)'), corner('translate(0 72) scale(1 -1)'), corner('translate(72 72) scale(-1 -1)')
# 石板正上方那一枚：罗盘星
CREST = svg("<circle cx='40' cy='40' r='17' fill='#1b2947' stroke='#c9a75e' stroke-width='1.8'/><circle cx='40' cy='40' r='12.5' fill='none' stroke='#c9a75e' stroke-width='.7'/>"
            "<path d='M40 4l4.2 31.8L76 40l-31.8 4.2L40 76l-4.2-31.8L4 40l31.8-4.2z' fill='#ecd497' stroke='#a8843f' stroke-width='.8'/>"
            "<path d='M40 22l2 16 16 2-16 2-2 16-2-16-16-2 16-2z' fill='#fff6dc' opacity='.85' transform='rotate(45 40 40)'/>", '0 0 80 80')
# 顶栏正中的一道纹：两头细线、几颗小星
BANNER = svg("<g stroke='#c9a75e' stroke-width='1' fill='none'><path d='M6 20H96M144 20H234'/></g>"
             "<g fill='#c9a75e'><path d='M100 20l3-3 3 3-3 3z'/><path d='M134 20l3-3 3 3-3 3z'/><circle cx='88' cy='20' r='1.6'/><circle cx='152' cy='20' r='1.6'/></g>"
             "<path d='M120 4l3 13 13 3-13 3-3 13-3-13-13-3 13-3z' fill='#ecd497' stroke='#a8843f' stroke-width='.6'/>", '0 0 240 40')
NOISE = 'url("data:image/svg+xml,%s")' % quote("<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .42 0 0 0 0 .32 0 0 0 0 .18 0 0 0 .09 0'/></filter><rect width='100%' height='100%' filter='url(#n)'/></svg>", safe="/:=' -.,()")

def ic(k):
    return svg(ICON[k])

R = '.rili-markdown-renderer:has(.sz-hud)'
css = []
w = css.append
w('/* ==== 手札（状态栏方向稿第三版的样张）：羊皮纸手札、金边框、底下一排页签；宽屏两侧挂整幅画，手机上不挂 ==== */')
w('''
/* ---------- 四纪的色与字（一纪一组变量；__ART__ 是图床） ---------- */
%(R)s{
  --sz-serif:"Noto Serif SC","Source Han Serif SC","Songti SC","STSong","Noto Serif CJK SC",serif;
  --sz-title:"奥尔德兰的旅印";--sz-journal:"旅印手札";
  --sz-band:#1c2b4b;--sz-band2:#131f38;--sz-gold:#c9a75e;--sz-gold2:#ecd497;
  --sz-paper1:#fbf6ea;--sz-paper2:#efe3c8;--sz-ink:#2b2a31;--sz-ink2:#5d5a66;--sz-head:#1f2a46;
}
%(R)s:has(.era-moon){--sz-title:"向长夜索春";--sz-band:#1e2740;--sz-band2:#121829}
%(R)s:has(.era-strife){--sz-title:"向长夜索春";--sz-band:#3a1f22;--sz-band2:#241316;--sz-gold:#c99a5e;--sz-head:#3a2024}
%(R)s:has(.era-bronze){--sz-band:#2a2a2c;--sz-band2:#18181a;--sz-gold:#c4925a;--sz-head:#2d2a27}
%(R)s:has(.era-pre){--sz-band:#173336;--sz-band2:#0e2224;--sz-head:#163235}
''' % {'R': R})
w('''
/* ---------- 一条回复是一本手札：羊皮纸、两道金线夹一道深色带、四角的纹、正上方一枚罗盘星 ---------- */
%(R)s{
  position:relative!important;isolation:isolate;
  width:min(640px, calc(100vw - 40px));
  margin:30px 0 14px!important;padding:26px 28px 0!important;border-radius:16px;
  background:%(NOISE)s, radial-gradient(130%% 70%% at 50%% 0%%, var(--sz-paper1), var(--sz-paper2) 72%%, #e6d6b4)!important;
  color:var(--sz-ink)!important;
  box-shadow:0 0 0 1.5px var(--sz-gold), 0 0 0 7.5px var(--sz-band), 0 0 0 9px var(--sz-gold), 0 26px 60px rgb(0 0 0 / .5);
}
%(R)s::before{
  content:"";position:absolute;inset:-14px;pointer-events:none;z-index:2;
  background:%(TL)s left top/66px no-repeat, %(TR)s right top/66px no-repeat, %(BL)s left bottom/66px no-repeat, %(BR)s right bottom/66px no-repeat;
}
%(R)s::after{
  content:"";position:absolute;left:50%%;top:-34px;width:62px;height:62px;transform:translateX(-50%%);pointer-events:none;z-index:3;
  background:%(CREST)s center/contain no-repeat;filter:drop-shadow(0 3px 6px rgb(0 0 0 / .35));
}
''' % {'R': R, 'NOISE': NOISE, 'TL': C_TL, 'TR': C_TR, 'BL': C_BL, 'BR': C_BR, 'CREST': CREST})
w('''
/* ---------- 头：标题、地点和纪年、三条；点开是推演底座 ---------- */
%(R)s details.sz-hud{margin:0 0 4px!important;padding:0!important;border:0!important;background:none!important;box-shadow:none!important}
%(R)s details.sz-hud>summary.sz-head{display:block!important;min-height:0!important;padding:10px 4px 6px!important;margin:0!important;border:0!important;background:none!important;text-align:center;cursor:pointer;list-style:none;position:relative}
%(R)s details.sz-hud>summary.sz-head::-webkit-details-marker{display:none}
%(R)s details.sz-hud>summary.sz-head::after{content:none!important}
%(R)s .sz-head b.sz-title{display:flex!important;align-items:center;justify-content:center;gap:18px;margin:0;font-family:var(--sz-serif);font-size:31px!important;font-weight:700!important;letter-spacing:.1em!important;color:var(--sz-head)!important;text-shadow:0 1px 0 rgb(255 255 255 / .6)!important}
%(R)s .sz-head b.sz-title::before,%(R)s .sz-head b.sz-title::after{content:"";flex:1;max-width:120px;height:9px;
  background:radial-gradient(circle, var(--sz-gold) 2.2px, transparent 2.6px) right center/9px 9px no-repeat, linear-gradient(90deg, transparent, var(--sz-gold)) left center/calc(100%% - 14px) 1.2px no-repeat}
%(R)s .sz-head b.sz-title::after{transform:scaleX(-1)}
%(R)s .sz-head b.sz-title span::before{content:var(--sz-title)}
%(R)s .sz-sub{display:flex;justify-content:center;align-items:center;flex-wrap:wrap;gap:6px 16px;margin-top:8px;font-size:13px;color:var(--sz-ink2);letter-spacing:.06em}
%(R)s .sz-sub>span{display:inline-flex;align-items:center;gap:8px}
%(R)s .sz-place::before,%(R)s .sz-year::before{content:"";width:10px;height:10px;background:var(--sz-gold);-webkit-mask:%(STAR)s center/contain no-repeat;mask:%(STAR)s center/contain no-repeat}
%(R)s .sz-year{padding-left:16px;border-left:1px solid #cfbd98}
%(R)s .sz-year:empty{display:none!important}
%(R)s .sz-time{color:#8a8576}
%(R)s .sz-time::before{content:"·";margin-right:-2px}
%(R)s .sz-more{position:absolute;right:0;top:12px;font-size:11px;color:#9a8f76;letter-spacing:.1em;border:1px solid #d8c8a4;border-radius:10px;padding:1px 8px 1px 9px}
%(R)s .sz-more::after{content:" ▾"}
%(R)s details.sz-hud[open] .sz-more::after{content:" ▴"}
/* 三条：数照写，长度照数算 */
%(R)s .sz-bars{display:grid;grid-template-columns:repeat(3,1fr);gap:10px 22px;margin:16px 4px 2px;text-align:left}
%(R)s .sz-bar{display:grid;grid-template-columns:24px auto 1fr;grid-template-rows:auto 7px;align-items:center;column-gap:7px;row-gap:5px;font-size:12.5px;color:var(--sz-ink2)}
%(R)s .sz-bar i{grid-row:1/3;width:24px;height:24px;background:var(--c);-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}
%(R)s .sz-bar b{font-weight:700!important;color:#3d3c48!important;font-size:12.5px!important;letter-spacing:.04em;display:inline!important}
%(R)s .sz-bar em{font-style:normal;font-variant-numeric:tabular-nums;color:#4e4c58}
%(R)s .sz-bar .sz-trk{grid-column:2/4;height:7px;border-radius:4px;background:rgb(60 50 30 / .12);box-shadow:inset 0 1px 1px rgb(0 0 0 / .12);position:relative;overflow:hidden}
%(R)s .sz-bar .sz-trk::after{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(min(var(--v), var(--m)) / var(--m) * 100%%);border-radius:4px;background:linear-gradient(90deg, color-mix(in srgb, var(--c) 70%%, #fff), var(--c))}
%(R)s .sz-bar.hp{--c:%(HPc)s;--ic:%(HP)s}
%(R)s .sz-bar.mp{--c:%(MPc)s;--ic:%(MP)s}
%(R)s .sz-bar.sp{--c:%(SPc)s;--ic:%(SP)s}
/* 推演底座（点开的时候）：一张浅格子 */
%(R)s .sz-hud-body{margin:10px 0 6px;padding:10px 12px;border:1px solid #dccaa3;border-radius:10px;background:rgb(255 252 243 / .65);font-size:12.5px;line-height:1.6;color:var(--sz-ink2)}
%(R)s .sz-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px 12px;margin-bottom:8px}
%(R)s .sz-grid b{display:block;font-size:11px;color:#9a7f45;font-weight:600}
%(R)s .sz-f.d{display:grid;grid-template-columns:5.6em 1fr;gap:8px;padding:4px 0;border-top:1px dashed #e2d3b2}
%(R)s .sz-f.d b{color:#8a6f3c;font-weight:600;font-size:12px}
''' % {'R': R, 'STAR': ic('star4'), 'HP': ic('hp'), 'MP': ic('mp'), 'SP': ic('sp'), 'HPc': TINT['hp'], 'MPc': TINT['mp'], 'SPc': TINT['sp']})
w('''
/* ---------- 手札正文 ---------- */
%(R)s .sz-prose{margin-top:6px}
%(R)s .sz-sec{display:flex;align-items:center;gap:14px;margin:10px 0 2px}
%(R)s .sz-sec::before,%(R)s .sz-sec::after{content:"";flex:1;height:1px;background:linear-gradient(90deg, transparent, #c9b07a)}
%(R)s .sz-sec::after{background:linear-gradient(270deg, transparent, #c9b07a)}
%(R)s .sz-sec span{display:inline-flex;align-items:center;gap:10px;font-family:var(--sz-serif);font-size:20px;font-weight:700;letter-spacing:.12em;color:var(--sz-head)}
%(R)s .sz-sec span::before{content:"";width:22px;height:22px;background:var(--sz-gold);-webkit-mask:%(QUILL)s center/contain no-repeat;mask:%(QUILL)s center/contain no-repeat}
%(R)s .sz-sec span::after{content:var(--sz-journal)}
%(R)s .sz-scene{text-align:center;font-size:12px;color:#968e7a;letter-spacing:.14em;margin:2px 0 16px}
%(R)s .sz-prose p{margin:0 0 16px!important;font-family:var(--sz-serif);font-size:16.5px;line-height:1.95;color:var(--sz-ink);text-indent:0}
%(R)s .sz-qc{display:flex;flex-direction:column;align-items:center;gap:2px;margin:0 0 16px;padding:10px 0;border-top:1px solid #dcc9a0;border-bottom:1px solid #dcc9a0}
%(R)s .sz-qc .qc-pian{font-size:12px;color:#9a7f45;letter-spacing:.2em}
%(R)s .sz-qc .qc-ml{font-family:var(--sz-serif);font-size:19px;color:var(--sz-head)}
%(R)s .sz-qc .qc-desc{font-size:12.5px;color:#8a8576}
/* 分支：短的并排成一颗颗签，长的自己占一行；自定义那一条只写自行决定 */
%(R)s .sz-choices ol{list-style:none!important;display:flex;flex-wrap:wrap;align-items:center;gap:12px 14px;margin:6px 0 22px!important;padding:0!important}
%(R)s .sz-choices li{display:inline-flex!important;align-items:center;gap:10px;max-width:100%%;margin:0!important;padding:9px 22px 9px 16px;border-radius:12px;border:1.5px solid var(--sz-gold);
  background:linear-gradient(#fffbf2, #f4e8cd);box-shadow:inset 0 0 0 3px rgb(255 251 240 / .9), 0 2px 6px rgb(90 66 22 / .16);color:#27324f;font-size:14.5px;line-height:1.55!important;cursor:pointer;transition:transform .15s, box-shadow .15s}
%(R)s .sz-choices li::before{content:"";flex:none;width:12px;height:12px;background:var(--sz-band);-webkit-mask:%(STAR)s center/contain no-repeat;mask:%(STAR)s center/contain no-repeat}
%(R)s .sz-choices li:hover{transform:translateY(-1px);box-shadow:inset 0 0 0 3px rgb(255 251 240 / .9), 0 4px 12px rgb(90 66 22 / .25)}
%(R)s .sz-choices li.sz-free{margin-left:auto!important;padding:6px 2px 4px;border:0;border-bottom:1px solid #b9a476;border-radius:0;background:none;box-shadow:none;cursor:default;color:#3a4566}
%(R)s .sz-choices li.sz-free::before{display:none}
%(R)s .sz-choices li.sz-free span{display:none}
%(R)s .sz-choices li.sz-free::after{content:"自行决定  ›";letter-spacing:.08em;font-size:14px}
''' % {'R': R, 'QUILL': ic('quill'), 'STAR': ic('star4')})
TABSEL = ','.join('%s:has(.t-%s input:checked) .p-%s' % (R, k, k) for k in ['panel', 'deed', 'bag', 'party', 'news', 'mem', 'war'])
w('''
/* ---------- 底下一排页签（一次只开一栏，开在页签上方；读长回复时页签贴在输入框上面） ---------- */
%(R)s .sz-tabs{display:flex;align-items:stretch;margin:4px -28px 0;padding:12px 14px 9px;position:sticky;bottom:var(--sz-dock,80px);z-index:4;
  background:linear-gradient(var(--sz-band), var(--sz-band2));border-top:1.5px solid var(--sz-gold);border-radius:0 0 15px 15px;box-shadow:0 -6px 16px rgb(0 0 0 / .18)}
%(R)s .sz-tab{flex:1;display:flex!important;flex-direction:column;align-items:center;gap:5px;color:#ece4d1;cursor:pointer;position:relative;padding-bottom:7px;user-select:none}
%(R)s .sz-tab input,%(R)s .sz-x input{display:none!important}
%(R)s .sz-tab i{width:30px;height:30px;background:currentColor;-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat;filter:drop-shadow(0 1px 1px rgb(0 0 0 / .4))}
%(R)s .sz-tab b{font-size:12.5px!important;font-weight:500!important;letter-spacing:.12em;color:inherit!important;display:block!important}
%(R)s .sz-tab+.sz-tab::before{content:"";position:absolute;left:0;top:19px;width:5px;height:5px;transform:translateX(-50%%) rotate(45deg);background:#8d7a52}
%(R)s .sz-tab:hover{color:#fff3cf}
%(R)s .sz-tab:has(input:checked){color:var(--sz-gold2)}
%(R)s .sz-tab:has(input:checked)::after{content:"";position:absolute;bottom:0;left:24%%;right:24%%;height:2px;border-radius:2px;background:var(--sz-gold2);box-shadow:0 0 8px var(--sz-gold2)}
%(R)s:not(:has(.p-war)) .t-war{opacity:.32;pointer-events:none}
%(TABICONS)s
/* 各栏：平时收着，点了页签才开 */
%(R)s .sz-pane{display:none;margin:2px 0 16px;padding:12px 16px 10px;border:1px solid #d6c39a;border-radius:12px;background:rgb(255 252 244 / .72);box-shadow:inset 0 0 0 3px rgb(255 255 255 / .35)}
%(SEL)s{display:block}
%(R)s .sz-pane-head{display:flex;align-items:center;gap:9px;margin-bottom:6px;padding-bottom:8px;border-bottom:1px solid #e2d3b0}
%(R)s .sz-pane-head i{width:20px;height:20px;background:var(--sz-gold);-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}
%(R)s .sz-pane-head b{font-family:var(--sz-serif);font-size:16px!important;font-weight:700!important;letter-spacing:.1em;color:var(--sz-head)!important}
%(R)s .sz-x{margin-left:auto;font-size:12px;color:#8e815f;cursor:pointer;border:1px solid #d8c8a4;border-radius:10px;padding:1px 10px}
%(R)s .sz-f:not(.d){display:grid;grid-template-columns:4.6em 1fr;gap:10px;padding:6px 0;border-bottom:1px dashed #e4d7ba;font-size:13.5px;line-height:1.65}
%(R)s .sz-f:not(.d):last-child{border-bottom:0}
%(R)s .sz-f:not(.d) b{color:#8a6c35;font-weight:600}
%(R)s .sz-npc{display:grid;grid-template-columns:64px 1fr;gap:12px;padding:8px 0}
%(R)s .sz-npc-av{width:64px;height:64px;border-radius:50%%;border:2px solid var(--sz-gold);background:radial-gradient(circle at 50%% 35%%, #fff8e6, #e8d6ae);display:grid;place-items:center;font-family:var(--sz-serif);font-size:24px;color:var(--sz-head)}
%(R)s .sz-npc-av::before{content:attr(data-n);display:block;width:1em;overflow:hidden;white-space:nowrap}
%(R)s .sz-npc-name b{font-family:var(--sz-serif);font-size:17px!important;color:var(--sz-head)!important;margin-right:10px}
%(R)s .sz-npc-name span{font-size:12px;color:#8a8576}
%(R)s .sz-npc-tags{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
%(R)s .sz-npc-tags span{font-size:11.5px;padding:1px 8px;border-radius:9px;background:rgb(201 167 94 / .16);color:#6d5a33}
%(R)s .sz-npc-tags span:empty{display:none}
%(R)s p.sz-npc-say{margin:4px 0 8px!important;font-family:var(--sz-serif);font-size:14.5px;color:#3d3a45}
%(R)s .sz-nf{display:grid;grid-template-columns:5.2em 1fr;gap:8px;padding:4px 0;font-size:12.5px;line-height:1.6;border-top:1px dashed #e6dac0}
%(R)s .sz-nf b{color:#8a6c35;font-weight:600}
%(R)s details.sz-more2{margin-top:4px}
%(R)s details.sz-more2>summary{min-height:0!important;padding:4px 0!important;font-size:12px;color:#8e815f;background:none!important;border:0!important}
''' % {'R': R, 'SEL': TABSEL, 'TABICONS': '\n'.join('%s :is(.t-%s,.p-%s){--ic:%s}' % (R, k, k, ic(k)) for k in ['panel', 'deed', 'bag', 'party', 'news', 'mem', 'war'])})
w('''
/* ---------- 整页：深色的底，宽屏两侧挂这一纪的整幅画，顶栏正中一道纹（手机上不挂两侧） ---------- */
:root:has(#conversation):has(.sz-hud){
  isolation:isolate;
  --sz-t:calc(var(--sz-h, 12) + var(--sz-m, 0) / 60);
  --sz-day:clamp(0, sin(calc((var(--sz-t) - 6) * 15deg)), 1);
  background-image:radial-gradient(60%% 50%% at 50%% 0%%, rgb(70 92 140 / .35), transparent 70%%), linear-gradient(180deg, #18233d, #0d1426)!important;
}
header>div:nth-child(2)::before{content:"";width:220px;height:36px;opacity:var(--sz-on, 0);background:%(BANNER)s center/contain no-repeat}
@media (min-width:1100px){
  :root:has(#conversation):has(.sz-hud)::before,
  :root:has(#conversation):has(.sz-hud)::after{
    content:"";position:absolute;top:-64px;bottom:0;width:calc(50%% - 322px);z-index:-1;pointer-events:none;
    background-repeat:no-repeat;background-size:cover;
    filter:brightness(calc(.5 + .5 * var(--sz-day)));
  }
  :root:has(#conversation):has(.sz-hud)::before{left:0;background-position:right top}
  :root:has(#conversation):has(.sz-hud)::after{right:0;background-position:left top}
  :root:has(#conversation):has(.era-maze)::before{background-image:url("__ART__/maze_left.webp")}
  :root:has(#conversation):has(.era-maze)::after{background-image:url("__ART__/maze_right.webp")}
}
/* ---------- 手机：不挂两侧，手札收窄一点 ---------- */
@media (max-width:700px){
  %(R)s{width:calc(100vw - 32px);padding:22px 16px 0!important;margin:28px 0 12px!important}
  %(R)s::before{inset:-12px;background-size:52px}
  %(R)s .sz-head b.sz-title{font-size:23px!important;gap:12px}
  %(R)s .sz-head b.sz-title::before,%(R)s .sz-head b.sz-title::after{max-width:56px}
  %(R)s .sz-sub{font-size:12px;gap:4px 12px}
  %(R)s .sz-year{border-left:0;padding-left:0}
  %(R)s .sz-more{position:static;display:inline-block;margin-top:6px}
  %(R)s .sz-bars{gap:8px 12px;margin:12px 0 2px}
  %(R)s .sz-bar{grid-template-columns:18px auto;font-size:11px}
  %(R)s .sz-bar i{width:18px;height:18px;grid-row:1}
  %(R)s .sz-bar em{grid-column:2;font-size:11px}
  %(R)s .sz-bar b{display:none!important}
  %(R)s .sz-bar .sz-trk{grid-column:1/3}
  %(R)s .sz-prose p{font-size:15.5px;line-height:1.9}
  %(R)s .sz-choices li{font-size:14px;padding:8px 16px 8px 13px}
  %(R)s .sz-tabs{margin:4px -16px 0;padding:10px 4px 7px;bottom:var(--sz-dock-m,84px)}
  %(R)s .sz-tab i{width:24px;height:24px}
  %(R)s .sz-tab b{font-size:11px!important;letter-spacing:.06em}
  %(R)s .sz-tab+.sz-tab::before{top:15px;width:4px;height:4px}
  %(R)s .sz-grid{grid-template-columns:repeat(2,1fr)}
}
@media (prefers-reduced-motion:reduce){%(R)s *{transition:none!important}}
''' % {'R': R, 'BANNER': BANNER})
open(sys.argv[1], 'w', encoding='utf-8').write('\n'.join(css))
print(sum(len(x) for x in css))
