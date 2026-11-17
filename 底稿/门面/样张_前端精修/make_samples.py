# -*- coding: utf-8 -*-
"""前端精修样张：照现有数据出四页静态 HTML，只做样子，不是成品。
  wb_moon.html      世界之书·月银纪卷（对开，手机单页）
  atlas_bronze.html 图鉴·山铜纪《拓本》，黎明的年月（#boss 是强敌那一栏）
  build_act1.html   建档第一幕·死之神殿·血
  build_act2.html   建档第二幕·落地·段城的兵册（#seal 是盖印那一下）
用法：在仓库根上，用带 PIL 的 Python 跑
  python -I -X utf8 底稿/门面/样张_前端精修/make_samples.py
图都引用本地现成的文件。主角预设的立绘在 底稿/状态栏/comfy/out/立绘_主角/，不进库。"""
import json, os, glob, html
from urllib.parse import quote
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.dirname(HERE)                     # 底稿/门面
R = os.path.dirname(os.path.dirname(F))       # 仓库根


def J(*p):
    return json.load(open(os.path.join(F, *p), encoding='utf-8'))


def esc(s):
    return html.escape(s or '', quote=True)


def svg_url(svg):
    return "url('data:image/svg+xml;utf8," + quote(svg, safe='') + "')"


def fill(tpl, **kw):
    for k, v in kw.items():
        tpl = tpl.replace('{{' + k + '}}', v)
    assert '{{' not in tpl, tpl[tpl.index('{{'):tpl.index('{{') + 40]
    return tpl


def write(name, text):
    with open(os.path.join(HERE, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('写了', name, len(text))


# ---------- 共用的纹理和花饰 ----------
def noise(r, g, b, a, freq='.9', oct_='3', size=220, seed=2):
    return svg_url("<svg xmlns='http://www.w3.org/2000/svg' width='%d' height='%d'><filter id='n'>"
                   "<feTurbulence type='fractalNoise' baseFrequency='%s' numOctaves='%s' seed='%d' stitchTiles='stitch'/>"
                   "<feColorMatrix values='0 0 0 0 %s 0 0 0 0 %s 0 0 0 0 %s 0 0 0 %s 0'/></filter>"
                   "<rect width='100%%' height='100%%' filter='url(#n)'/></svg>" % (size, size, freq, oct_, seed, r, g, b, a))


def flourish(color, w=300):
    half = ("<path d='M162 15 C190 15 210 9 236 13 C252 15.5 268 15.5 296 15' fill='none' stroke='{c}' stroke-width='1.1' stroke-linecap='round'/>"
            "<path d='M162 15 C170 5.5 184.5 5.5 186.5 12.5 C188 18 181.5 20.5 178.6 16.6' fill='none' stroke='{c}' stroke-width='1.1' stroke-linecap='round'/>"
            "<path d='M200 12.6 C206.5 6 214.5 5.6 219 8.6 C213 10.2 206.5 11.6 200 12.6 Z' fill='{c}'/>"
            "<path d='M214 15.6 C219 20.6 226 21 230 18.6 C225 17.4 219.5 16.4 214 15.6 Z' fill='{c}' opacity='.75'/>"
            "<circle cx='248' cy='14.4' r='1.7' fill='{c}'/><circle cx='264' cy='15' r='1.1' fill='{c}'/>").format(c=color)
    return svg_url("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 30' width='%d' height='%d'>" % (w, w // 10) + half
                   + "<g transform='translate(300 0) scale(-1 1)'>" + half + "</g>"
                   + "<path d='M150 6 L158 15 L150 24 L142 15 Z' fill='none' stroke='%s' stroke-width='1.1'/>" % color
                   + "<path d='M150 10.6 L154 15 L150 19.4 L146 15 Z' fill='%s'/></svg>" % color)


def corner(color, sw=1.3):
    return svg_url("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60' width='60' height='60'>"
                   "<g fill='none' stroke='%s' stroke-linecap='round'>"
                   "<path d='M4 58 V20 C4 10 10 4 20 4 H58' stroke-width='%s'/>"
                   "<path d='M10 58 V25 C10 16 16 10 25 10 H58' stroke-width='.7' opacity='.7'/>"
                   "<path d='M4 36 C14 36 18.5 30 16.5 23.5 C15 19 10 20 10.6 24' stroke-width='1'/>"
                   "<path d='M36 4 C36 14 30 18.5 23.5 16.5 C19 15 20 10 24 10.6' stroke-width='1'/></g>"
                   "<path d='M4 0.6 L7.4 4 L4 7.4 L0.6 4 Z' fill='%s'/></svg>" % (color, sw, color))


PROGRESS = ['来路', '血', '身子', '面容', '册子', '本事', '誓心', '初心']


def progress_html(cur, done):
    out = []
    for i, lab in enumerate(PROGRESS):
        st = 'done' if i < done else ('cur' if i == cur else 'todo')
        out.append('<li class="pg %s"><i></i><span>%s</span></li>' % (st, lab))
    return '<ol class="prog">' + ''.join(out) + '</ol>'


# =====================================================================
# 一、世界之书·月银纪卷
# =====================================================================
WB_TPL = r'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>样张·世界之书·月银纪卷</title>
<style>
:root{--serif:'Noto Serif SC','Songti SC','STSong','SimSun',serif;--ink:#2a2520;--ink2:#655a4e;--moon:#2c4672;--moon2:#5d7cab;--paper:#f3ebd9}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{background:#05070c;color:var(--ink);font-family:var(--serif);overflow:hidden;-webkit-font-smoothing:antialiased}
.bgart{position:fixed;inset:-60px;background:url(../小样_牌桌/assets/era_0.webp) center/cover;filter:blur(22px) brightness(.34) saturate(.85)}
.bgvig{position:fixed;inset:0;background:radial-gradient(ellipse 72% 64% at 50% 46%,rgba(5,7,12,0) 0,rgba(5,7,12,.5) 68%,rgba(2,3,6,.92) 100%)}
.top{position:fixed;left:30px;top:26px;display:flex;flex-direction:column;gap:14px;z-index:5}
.btn{display:inline-flex;align-items:center;gap:8px;height:34px;padding:0 14px;border-radius:17px;font-size:13px;letter-spacing:.18em;color:#dfe6f2;background:rgba(18,24,38,.55);box-shadow:0 0 0 1px rgba(201,211,227,.28) inset;backdrop-filter:blur(6px)}
.btn b{font-weight:400;font-size:15px;letter-spacing:0}
.top .vol{color:#c9d3e3;font-size:12px;letter-spacing:.32em;margin-left:4px;opacity:.85}
.turn{position:fixed;top:50%;width:54px;height:54px;margin-top:-27px;border-radius:50%;display:grid;place-items:center;color:#dfe6f2;font-size:26px;background:rgba(18,24,38,.45);box-shadow:0 0 0 1px rgba(201,211,227,.22) inset;z-index:5}
.turn.l{left:calc(50% - 820px)}.turn.r{right:calc(50% - 820px)}
.stage{position:relative;height:100%;display:grid;place-items:center}
.book{position:relative;width:1480px;height:870px}
.cover{position:absolute;inset:0;border-radius:16px;
 background:{{CLOTH}},linear-gradient(158deg,#5a6f97 0%,#3a4f78 38%,#273a60 100%);
 box-shadow:0 40px 90px rgba(0,0,0,.7),0 0 0 1px rgba(255,255,255,.07) inset,0 2px 0 rgba(255,255,255,.14) inset,0 -3px 0 rgba(0,0,0,.35) inset}
.cover::before{content:'';position:absolute;inset:9px;border:1.6px dashed rgba(220,229,244,.5);border-radius:10px}
.cover::after{content:'';position:absolute;inset:0;border-radius:16px;background:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 1px,transparent 1px 3px),repeating-linear-gradient(90deg,rgba(0,0,0,.07) 0 1px,transparent 1px 3px)}
.ck{position:absolute;width:64px;height:64px;background:{{CORNER_SILVER}} center/contain no-repeat;z-index:3;filter:drop-shadow(0 1px 1px rgba(0,0,0,.5))}
.ck.tl{left:2px;top:2px}.ck.tr{right:2px;top:2px;transform:scaleX(-1)}.ck.bl{left:2px;bottom:2px;transform:scaleY(-1)}.ck.br{right:2px;bottom:2px;transform:scale(-1,-1)}
.pages{position:absolute;inset:24px 28px 26px;display:grid;grid-template-columns:1fr 1fr;z-index:2}
.page{position:relative;overflow:hidden;padding:40px 70px 58px 62px}
.page.left{border-radius:7px 2px 2px 7px;padding:40px 58px 58px 74px;
 background:{{FIBER}},{{GRAIN}},linear-gradient(90deg,#d9cdb0 0,#ece3cd 3.5%,#f4ecdb 14%,#f4ecda 82%,#e8dcc3 93%,#d2c3a2 100%);
 box-shadow:-2px 1px 0 #e9dfc8,-4px 2px 0 #d9ccb0,-6px 3px 0 #cbbb9b,-8px 4px 0 #b9a885}
.page.right{border-radius:2px 7px 7px 2px;padding:40px 74px 58px 58px;
 background:{{FIBER}},{{GRAIN}},linear-gradient(270deg,#d9cdb0 0,#ece3cd 3.5%,#f4ecdb 14%,#f4ecda 82%,#e8dcc3 93%,#d2c3a2 100%);
 box-shadow:2px 1px 0 #e9dfc8,4px 2px 0 #d9ccb0,6px 3px 0 #cbbb9b,8px 4px 0 #b9a885}
.gutter{position:absolute;top:24px;bottom:26px;left:50%;width:110px;margin-left:-55px;z-index:3;pointer-events:none;
 background:linear-gradient(90deg,rgba(90,66,30,0) 0,rgba(90,66,30,.16) 34%,rgba(48,32,12,.42) 49.6%,rgba(255,250,236,.22) 50.4%,rgba(90,66,30,.16) 66%,rgba(90,66,30,0) 100%)}
.runhead{display:flex;align-items:center;gap:14px;font-size:12px;letter-spacing:.46em;color:var(--moon2)}
.runhead::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(93,124,171,.6),rgba(93,124,171,0))}
.right .runhead{flex-direction:row-reverse}.right .runhead::after{background:linear-gradient(270deg,rgba(93,124,171,.6),rgba(93,124,171,0))}
.toc{position:absolute;left:74px;right:58px;bottom:58px;padding-top:12px;border-top:1px solid rgba(93,124,171,.32)}
.toc h4{font-weight:400;font-size:11.5px;letter-spacing:.56em;color:var(--moon2);margin-bottom:6px}
.toc ol{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:3px 30px}
.toc li{display:flex;align-items:baseline;gap:10px;font-size:13.5px;letter-spacing:.08em;color:var(--ink2);white-space:nowrap}
.toc li i{font-style:normal;font-size:12px;color:var(--moon2);width:1.4em}
.toc li::after{content:'';flex:1;border-bottom:1px dotted rgba(93,124,171,.38)}
.toc li.on{color:var(--moon);font-weight:600}
.banner{position:relative;height:176px;margin:14px 0 0;border-radius:3px;background:url(../小样_牌桌/assets/era_0.webp) center 46%/cover;
 box-shadow:0 0 0 1px rgba(44,70,114,.5),0 0 0 4px #f4ecdb,0 0 0 5px rgba(44,70,114,.35),0 10px 18px rgba(60,40,10,.22)}
.banner::before{content:'';position:absolute;inset:7px;border:1px solid rgba(240,244,252,.6)}
.banner .bc{position:absolute;width:36px;height:36px;background:{{CORNER_WHITE}} center/contain no-repeat}
.bc.tl{left:3px;top:3px}.bc.tr{right:3px;top:3px;transform:scaleX(-1)}.bc.bl{left:3px;bottom:3px;transform:scaleY(-1)}.bc.br{right:3px;bottom:3px;transform:scale(-1,-1)}
.chno{margin-top:16px;text-align:center;font-size:12.5px;letter-spacing:.7em;color:var(--moon2);text-indent:.7em}
.chno::before,.chno::after{content:'';display:inline-block;width:5px;height:5px;transform:rotate(45deg);border:1px solid var(--moon2);vertical-align:3px;margin:0 1.1em}
h1{font-size:44px;font-weight:600;letter-spacing:.32em;text-indent:.32em;text-align:center;color:var(--moon);margin-top:6px;line-height:1.25}
.sub{text-align:center;color:var(--ink2);font-size:14.5px;letter-spacing:.24em;margin-top:6px}
.epi{margin:12px auto 0;width:82%;text-align:center}
.epi::before,.epi::after{content:'';display:block;height:16px;background:{{FLOURISH}} center/240px 16px no-repeat;opacity:.9}
.epi p{font-size:19px;letter-spacing:.16em;color:#34405a;margin:9px 0 2px}
.epi cite{display:block;font-style:normal;font-size:11.5px;letter-spacing:.38em;color:var(--moon2);margin-bottom:9px}
.sec{margin-top:16px}
h3{font-size:18px;font-weight:600;letter-spacing:.14em;color:var(--moon);margin-bottom:7px}
h3::before{content:'';display:inline-block;width:6px;height:6px;transform:rotate(45deg);border:1px solid var(--moon2);background:rgba(93,124,171,.25);margin-right:11px;vertical-align:4px}
.txt{font-size:15.5px;line-height:1.98;text-align:justify;color:var(--ink);letter-spacing:.02em}
.dc::first-letter{float:left;font-size:54px;line-height:1;padding:8px 12px 6px;margin:5px 14px 0 0;color:var(--moon);font-weight:600;
 border:1px solid rgba(44,70,114,.5);background:linear-gradient(135deg,rgba(93,124,171,.2),rgba(93,124,171,.05));box-shadow:inset 0 0 0 3px #f4ecdb,inset 0 0 0 4px rgba(44,70,114,.32)}
.term{color:var(--moon);border-bottom:1px dotted var(--moon2);position:relative;white-space:nowrap}
.term.open{background:rgba(93,124,171,.16);border-bottom-style:solid}
.tip{position:absolute;left:-8px;bottom:calc(100% + 14px);width:262px;padding:14px 16px 12px;border-radius:6px;white-space:normal;text-align:left;
 background:linear-gradient(160deg,#25324d,#18213a);color:#e6ecf6;font-size:13.5px;line-height:1.78;letter-spacing:.03em;
 box-shadow:0 0 0 1px rgba(201,211,227,.4) inset,0 14px 30px rgba(10,14,28,.45);z-index:9}
.tip::after{content:'';position:absolute;left:24px;bottom:-7px;width:12px;height:12px;background:#19223b;transform:rotate(45deg);box-shadow:1px 1px 0 rgba(201,211,227,.4)}
.tip b{display:block;font-size:15px;letter-spacing:.2em;color:#fff;font-weight:600;margin-bottom:2px}
.tip em{display:block;font-style:normal;font-size:11px;letter-spacing:.3em;color:#9fb3d6;margin-bottom:6px}
.tip a{display:block;margin-top:8px;font-size:12px;letter-spacing:.24em;color:#c9d6ee;text-decoration:none;text-align:right}
.tri{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:16px 4px 2px}
.tri figure{text-align:center}
.tri .im{aspect-ratio:4/3;background-size:cover;background-position:center;border-radius:2px;
 box-shadow:0 0 0 1px rgba(44,70,114,.42),0 0 0 4px #f4ecdb,0 0 0 5px rgba(44,70,114,.26),0 8px 14px rgba(60,40,10,.2)}
.tri figcaption{margin-top:10px;font-size:13.5px;letter-spacing:.28em;color:var(--moon)}
.tri figcaption small{display:block;font-size:11.5px;letter-spacing:.12em;color:var(--ink2);margin-top:1px}
.div{height:18px;margin:14px auto 4px;width:250px;background:{{FLOURISH}} center/250px 18px no-repeat}
.mn{position:absolute;writing-mode:vertical-rl;font-size:12.5px;letter-spacing:.32em;color:var(--moon2);line-height:1.5}
.mn::before{content:'';display:block;width:1px;height:26px;margin:0 auto 10px;background:linear-gradient(rgba(93,124,171,0),rgba(93,124,171,.7))}
.left .mn{left:30px}.right .mn{right:30px}
.folio{position:absolute;left:0;right:0;bottom:20px;display:flex;align-items:center;justify-content:center;gap:12px;font-size:12.5px;letter-spacing:.3em;color:var(--moon2)}
.folio::before,.folio::after{content:'';width:46px;height:9px;background:{{FLOURISH}} center/150px 15px no-repeat;opacity:.8}
.ribbons{position:absolute;right:-138px;top:84px;display:flex;flex-direction:column;gap:12px;z-index:1}
.rb{position:relative;width:170px;height:46px;display:flex;align-items:center;gap:10px;padding-left:48px;color:#f4f1ea;font-size:13px;letter-spacing:.26em;
 clip-path:polygon(0 0,100% 0,90% 50%,100% 100%,0 100%);text-shadow:0 1px 2px rgba(0,0,0,.45)}
.rb::before{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,.32) 0,rgba(255,255,255,0) 34%,rgba(0,0,0,.08) 70%,rgba(0,0,0,.28) 100%)}
.rb img{position:relative;height:34px;width:auto;filter:drop-shadow(0 1px 2px rgba(0,0,0,.5))}
.rb span{position:relative}
.rb.gen{background:#6e4a2a}.rb.moon{background:#5876a8;width:206px;box-shadow:0 0 18px rgba(150,180,230,.5)}
.rb.strife{background:#7b1e25}.rb.bronze{background:linear-gradient(180deg,#e6e1d4 0 3px,#17171b 3px calc(100% - 3px),#e6e1d4 calc(100% - 3px))}
.rb.maze{background:linear-gradient(180deg,#caa652 0 2px,#1d2f5c 2px calc(100% - 2px),#caa652 calc(100% - 2px))}
.rb.moon span::after{content:'';display:inline-block;width:6px;height:6px;border-radius:50%;background:#e9f0ff;margin-left:8px;vertical-align:2px;box-shadow:0 0 8px #fff}
.phonebar,.pager{display:none}
@media (max-width:640px){
 body{overflow:auto;background:#0a0d15}
 .bgart,.bgvig,.top,.turn,.ribbons,.gutter,.page.right,.ck,.toc{display:none}
 .stage{display:block;height:auto}
 .phonebar{display:flex;position:sticky;top:0;z-index:20;gap:6px;padding:10px 10px 8px;background:linear-gradient(#0a0d15 70%,rgba(10,13,21,0));overflow-x:auto}
 .phonebar a{flex:none;display:flex;align-items:center;gap:5px;height:32px;padding:0 10px 0 6px;border-radius:16px;font-size:12px;letter-spacing:.14em;color:#d7deea;background:rgba(255,255,255,.06);text-decoration:none}
 .phonebar a img{height:22px}
 .phonebar a.on{background:#3d5788;color:#fff;box-shadow:0 0 0 1px rgba(220,230,250,.5) inset}
 .book{width:auto;height:auto;margin:0 8px}
 .cover{position:relative;padding:8px;border-radius:12px}
 .cover::before{inset:4px;border-radius:9px}
 .pages{position:relative;inset:auto;display:block}
 .page.left{padding:24px 20px 64px;border-radius:6px;box-shadow:none}
 .banner{height:150px}
 h1{font-size:34px}.sub{font-size:13px;letter-spacing:.14em}
 .epi{width:100%}.epi p{font-size:16.5px;letter-spacing:.08em}
 .txt{font-size:15px;line-height:1.95}
 .mn{position:static;writing-mode:horizontal-tb;display:inline-block;margin:10px 0 0;padding:3px 10px;border-radius:12px;background:rgba(93,124,171,.12);font-size:11.5px;letter-spacing:.2em}
 .mn::before{display:none}
 .folio{bottom:16px}
 .pager{display:flex;justify-content:space-between;align-items:center;margin:10px 8px 24px;color:#cfd8e8;font-size:12.5px;letter-spacing:.2em}
 .pager i{font-style:normal;display:inline-grid;place-items:center;width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,.07);font-size:20px}
}
</style></head>
<body>
<div class="bgart"></div><div class="bgvig"></div>
<div class="top"><span class="btn"><b>✕</b>合上</span><span class="vol">世界之书 · 月银纪卷</span></div>
<span class="turn l">‹</span><span class="turn r">›</span>
<nav class="phonebar">{{PHONEBAR}}</nav>
<main class="stage"><div class="book">
 <nav class="ribbons">{{RIBBONS}}</nav>
 <div class="cover"><i class="ck tl"></i><i class="ck tr"></i><i class="ck bl"></i><i class="ck br"></i>
  <div class="pages">
   <section class="page left">
    <div class="runhead">月银纪卷</div>
    <div class="banner"><i class="bc tl"></i><i class="bc tr"></i><i class="bc bl"></i><i class="bc br"></i></div>
    <div class="chno">第一章</div>
    <h1>{{TITLE}}</h1>
    <div class="sub">{{SUB}}</div>
    <div class="epi"><p>长夜啊，把春天还给灰桥。</p><cite>题诗 · 第一行</cite></div>
    <div class="sec"><h3>{{H0}}</h3><p class="txt dc">{{T0}}</p></div>
    <div class="mn" style="top:300px">{{VOLSUB}}</div>
    <div class="toc"><h4>本卷八章</h4><ol>{{TOC}}</ol></div>
    <div class="folio">一</div>
   </section>
   <section class="page right">
    <div class="runhead">这一纪</div>
    <div class="sec" style="margin-top:20px"><h3>{{H1}}</h3><p class="txt">{{T1}}</p></div>
    <div class="tri">
     <figure><div class="im" style="background-image:url(../小样_月银纪书/assets/cg/m01_era.webp)"></div><figcaption>天亮以前<small>十五支歌</small></figcaption></figure>
     <figure><div class="im" style="background-image:url(../小样_月银纪书/assets/cg/m16_era.webp)"></div><figcaption>天亮以后<small>诸国期 · 六段</small></figcaption></figure>
     <figure><div class="im" style="background-image:url(../小样_月银纪书/assets/cg/m27_era.webp)"></div><figcaption>天黑以前<small>萨尔维斯 · 六段</small></figcaption></figure>
    </div>
    <div class="div"></div>
    <div class="sec"><h3>{{H2}}</h3><p class="txt">{{T2}}</p></div>
    <div class="mn" style="top:470px">唱到第几个国</div>
    <div class="sec"><h3>{{H3}}</h3><p class="txt">{{T3}}</p></div>
    <div class="sec"><h3>{{H4}}</h3><p class="txt">{{T4}}</p></div>
    <div class="folio">二</div>
   </section>
  </div>
  <div class="gutter"></div>
 </div>
</div>
<div class="pager"><i>‹</i><span>第一章 · 一 / 二</span><i>›</i></div>
</main>
</body></html>
'''


def page_wb():
    wb = J('共用', 'data', 'wb.json')
    vol = next(v for v in wb['volumes'] if v['id'] == 'moon')
    s = vol['pages'][0]['sections']
    tip = ('<span class="tip"><b>黄金裔</b><em>称呼 · 月银纪</em>'
           '生在这一纪，跟着凡人那一头的父亲或母亲长大，血是金色的。<a>在图鉴里看 ›</a></span>')
    t3 = esc(s[3]['t']).replace('黄金裔', '<span class="term open">黄金裔' + tip + '</span>', 1)
    t0 = esc(s[0]['t']).replace('辉塔', '<span class="term">辉塔</span>', 1)
    t4 = esc(s[4]['t']).replace('辉塔', '<span class="term">辉塔</span>', 1)
    vols = [('gen', '通用', '../共用/assets/ui/wb_cover.webp'), ('moon', '月银纪', '../共用/assets/ui/emblem_moon.webp'),
            ('strife', '纷争纪', '../共用/assets/ui/emblem_strife.webp'), ('bronze', '山铜纪', '../共用/assets/ui/emblem_bronze.webp'),
            ('maze', '迷宫纪', '../共用/assets/ui/emblem_maze.webp')]
    ribbons = ''.join('<div class="rb %s"><img src="%s" alt=""><span>%s</span></div>' % (k, im, t) for k, t, im in vols)
    phonebar = ''.join('<a class="%s"><img src="%s" alt="">%s</a>' % ('on' if k == 'moon' else '', im, t) for k, t, im in vols)
    nums = '一二三四五六七八九十'
    toc = ''.join('<li class="%s"><i>%s</i>%s</li>' % ('on' if i == 0 else '', nums[i], esc(p['title'])) for i, p in enumerate(vol['pages']))
    return fill(WB_TPL, TOC=toc,
                CLOTH=noise('.85', '.9', '1', '.16', freq='1.4', oct_='2', size=180),
                FIBER=noise('.45', '.36', '.2', '.10', freq='.012', oct_='3', size=600, seed=7),
                GRAIN=noise('.4', '.32', '.2', '.20', freq='.9', oct_='3', size=220),
                CORNER_SILVER=corner('#dfe7f4', 1.6), CORNER_WHITE=corner('#ffffff', 1.4),
                FLOURISH=flourish('#5d7cab'),
                RIBBONS=ribbons, PHONEBAR=phonebar,
                TITLE=esc(vol['pages'][0]['title']), SUB=esc(vol['pages'][0]['sub']),
                VOLSUB=esc(vol['sub'].split('　')[0]),
                H0=esc(s[0]['h']), T0=t0, H1=esc(s[1]['h']), T1=esc(s[1]['t']),
                H2=esc(s[2]['h']), T2=esc(s[2]['t']), H3=esc(s[3]['h']), T3=t3, H4=esc(s[4]['h']), T4=t4)


# =====================================================================
# 二、图鉴·山铜纪《拓本》
# =====================================================================
ATLAS_TPL = r'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>样张·图鉴·山铜纪</title>
<style>
:root{--serif:'Noto Serif SC','Songti SC','STSong','SimSun',serif;--bone:#e8e3d6;--bone2:#a9a497;--line:rgba(232,227,214,.16);--obs:#101014}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{font-family:var(--serif);color:var(--bone);overflow:hidden;-webkit-font-smoothing:antialiased;
 background:{{RUB}},radial-gradient(ellipse 80% 60% at 50% 0,#22232a 0,#121216 60%,#0b0b0e 100%)}
.sky{position:fixed;left:0;right:0;top:0;height:330px;background:url(../小样_山铜纪书/assets/cg/e4.webp) center 30%/cover;opacity:.26;filter:saturate(.6) blur(1px);
 -webkit-mask-image:linear-gradient(#000 20%,transparent 100%)}
.wrap{position:relative;height:100%;display:grid;grid-template-rows:auto auto auto 1fr}
header{display:flex;align-items:center;gap:18px;padding:22px 44px 0}
header img{height:64px;filter:drop-shadow(0 3px 6px rgba(0,0,0,.6))}
header h1{font-size:34px;font-weight:600;letter-spacing:.4em;color:#f3efe4;text-shadow:0 2px 12px rgba(0,0,0,.6)}
header h1 small{font-size:13px;letter-spacing:.32em;color:var(--bone2);font-weight:400;margin-left:14px}
header .sp{flex:1}
.tog{display:flex;align-items:center;gap:10px;font-size:13px;letter-spacing:.2em;color:var(--bone2)}
.tog i{width:38px;height:20px;border-radius:10px;background:#2a2b31;box-shadow:0 0 0 1px var(--line) inset;position:relative}
.tog i::after{content:'';position:absolute;left:3px;top:3px;width:14px;height:14px;border-radius:50%;background:#8b877c}
.x{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;background:rgba(255,255,255,.06);box-shadow:0 0 0 1px var(--line) inset;color:var(--bone)}
.axis{position:relative;margin:18px 44px 0;height:118px;display:flex;align-items:flex-start;gap:0}
.axis::before{content:'';position:absolute;left:0;right:0;top:36px;height:8px;border-radius:2px;
 background:linear-gradient(90deg,#0d0d10 0,#2b2b31 49.8%,#d9d4c7 50.2%,#b9b3a5 100%);box-shadow:0 1px 0 rgba(255,255,255,.12),0 0 0 1px rgba(0,0,0,.6)}
.stop{position:relative;flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;color:var(--bone2);font-size:13px;letter-spacing:.16em}
.stop.all{flex:.55}
.stop .dot{width:80px;height:80px;border-radius:50%;background-size:cover;background-position:center;box-shadow:0 0 0 2px #0c0c0f,0 0 0 3px rgba(232,227,214,.35);filter:grayscale(.6) brightness(.62)}
.stop.all .dot{background:radial-gradient(circle,#2a2b31,#121216);display:grid;place-items:center;font-size:12px;letter-spacing:.2em;color:var(--bone2);filter:none}
.stop small{font-size:11px;letter-spacing:.08em;opacity:.8}
.stop.on{color:#fff}
.stop.on .dot{filter:none;box-shadow:0 0 0 2px #0c0c0f,0 0 0 4px #f1ede2,0 0 22px rgba(255,248,226,.55)}
.stop.on::after{content:'';position:absolute;bottom:-10px;width:9px;height:9px;transform:rotate(45deg);background:#f1ede2}
.bar{display:flex;align-items:flex-end;gap:30px;margin:14px 44px 0;border-bottom:1px solid var(--line);padding:0 4px}
.tab{position:relative;padding:10px 2px 12px;font-size:17px;letter-spacing:.3em;color:var(--bone2)}
.tab sup{font-size:11px;letter-spacing:.05em;margin-left:2px;opacity:.8;vertical-align:4px}
input[name=tab]{display:none}
#t-cast:checked~.wrap .tab.cast,#t-boss:checked~.wrap .tab.boss{color:#fff}
#t-cast:checked~.wrap .tab.cast::after,#t-boss:checked~.wrap .tab.boss::after{content:'';position:absolute;left:0;right:0;bottom:-1px;height:2px;background:linear-gradient(90deg,#0f0f12 50%,#f1ede2 50%)}
.bar .sp{flex:1}
.chips{display:flex;gap:8px;padding-bottom:10px}
.chip{padding:5px 12px;border-radius:14px;font-size:12px;letter-spacing:.16em;color:var(--bone2);box-shadow:0 0 0 1px var(--line) inset}
.chip.on{color:#111;background:#e8e3d6}
.main{display:grid;grid-template-columns:1fr 452px;gap:28px;padding:16px 44px 0;min-height:0}
.list{overflow:hidden;min-height:0}
.grp{display:flex;align-items:baseline;gap:12px;margin:4px 0 10px;font-size:14px;letter-spacing:.32em;color:#f1ede2}
.grp small{font-size:12px;letter-spacing:.12em;color:var(--bone2)}
.grp a{margin-left:auto;font-size:12px;letter-spacing:.18em;color:var(--bone2)}
.grid{display:grid;grid-template-columns:repeat(8,155px);gap:16px 14px;margin-bottom:18px}
.card{position:relative;width:155px}
.frame{position:relative;padding:6px;border-radius:3px;background:linear-gradient(90deg,#040405 0,#1b1b20 28%,#3a3a43 49.6%,#f6f2e8 50.4%,#d9d3c5 72%,#aea898 100%);
 box-shadow:0 8px 16px rgba(0,0,0,.55)}
.frame::before,.frame::after{content:'';position:absolute;left:50%;width:9px;height:9px;margin-left:-4.5px;border-radius:50%;z-index:2;
 background:radial-gradient(circle at 35% 35%,#fff,#9a958a 55%,#4a4740);box-shadow:0 1px 2px rgba(0,0,0,.6)}
.frame::before{top:-2px}.frame::after{bottom:-2px}
.img{height:207px;background-color:#1c1c21;background-repeat:no-repeat;border-radius:1px;box-shadow:0 0 0 1px rgba(0,0,0,.6) inset}
.img.none{display:grid;place-items:center;background:{{RUB}},linear-gradient(#24252b,#17171b)}
.img.none::before{content:'';width:70px;height:96px;background:radial-gradient(circle at 50% 24%,#3a3a42 0 17px,transparent 18px),radial-gradient(ellipse 34px 46px at 50% 92%,#3a3a42 0 98%,transparent 100%)}
.card.sel .frame{box-shadow:0 0 0 2px #f1ede2,0 0 24px rgba(255,248,226,.45),0 8px 16px rgba(0,0,0,.55)}
.nm{margin-top:9px;font-size:15px;letter-spacing:.08em;color:#f3efe4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.who{margin-top:2px;font-size:11.5px;line-height:1.5;color:var(--bone2);height:34px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.tags{display:flex;gap:4px;margin-top:6px;flex-wrap:wrap}
.tg{font-size:10.5px;letter-spacing:.1em;padding:1px 7px;border-radius:2px;color:#d9d4c7;box-shadow:0 0 0 1px rgba(232,227,214,.28) inset}
.tg.lg{color:#141414;background:#e8e3d6;box-shadow:none}
.tg.lock{color:#77736a}
.panel{position:relative;border-radius:6px;overflow:hidden;background:linear-gradient(180deg,rgba(28,29,35,.92),rgba(14,14,18,.96));box-shadow:0 0 0 1px var(--line) inset,0 20px 40px rgba(0,0,0,.5);
 display:flex;flex-direction:column;min-height:0;max-height:100%}
.hero{position:relative;height:320px;flex:none;background:linear-gradient(180deg,rgba(0,0,0,0) 55%,#141418 100%),url(../小样_山铜纪书/assets/cg/e4.webp) center 40%/cover}
.hero::before{content:'';position:absolute;inset:0;background:linear-gradient(90deg,rgba(10,10,12,.72),rgba(10,10,12,.25) 50%,rgba(10,10,12,.72))}
.hero .fig{position:absolute;left:50%;bottom:0;width:220px;height:316px;margin-left:-110px;background-repeat:no-repeat;filter:drop-shadow(0 10px 18px rgba(0,0,0,.7))}
.hero .k{position:absolute;left:18px;top:16px;font-size:11.5px;letter-spacing:.3em;color:var(--bone2)}
.pb{padding:0 24px 20px;overflow:hidden}
.pb h2{font-size:26px;font-weight:600;letter-spacing:.14em;color:#fff;margin-top:-6px}
.pb .meta{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 10px}
.pb p{font-size:14px;line-height:1.8;color:#ddd8cb}
.row{display:grid;grid-template-columns:76px 1fr;gap:10px;margin-top:8px;font-size:13px;line-height:1.7}
.row b{font-weight:400;letter-spacing:.24em;color:var(--bone2)}
.row span{color:#e7e2d5}
.row.lock span{color:#77736a}
.outs{display:flex;gap:8px;margin-top:12px;align-items:center}
.outs::before{content:'四套';font-size:12px;letter-spacing:.3em;color:var(--bone2);width:76px}
.outs i{width:44px;height:64px;border-radius:2px;background-repeat:no-repeat;background-color:#1e1f25;box-shadow:0 0 0 1px var(--line) inset}
.outs i.on{box-shadow:0 0 0 1px #f1ede2 inset}
.btns{display:flex;gap:10px;margin-top:14px}
.bt{flex:1;height:40px;border-radius:3px;display:grid;place-items:center;font-size:13.5px;letter-spacing:.3em;color:#e8e3d6;box-shadow:0 0 0 1px rgba(232,227,214,.35) inset}
.bt.pri{color:#121214;background:linear-gradient(90deg,#f2eee4,#cfc9bb);box-shadow:none}
.view-boss{display:none}
#t-boss:checked~.wrap .view-cast{display:none}
#t-boss:checked~.wrap .view-boss{display:block}
#t-boss:checked~.wrap .main{grid-template-columns:1fr 452px}
.bgrid{display:grid;grid-template-columns:repeat(5,236px);gap:18px}
.card.bc{width:236px}
.bc .img{height:344px}
.bc .yr{margin-top:3px;font-size:12px;letter-spacing:.14em;color:var(--bone2)}
.ph{display:flex;gap:4px;margin-top:6px}
.ph i{flex:1;height:3px;background:rgba(232,227,214,.25)}.ph i.on{background:#e8e3d6}
.phs{display:grid;grid-template-columns:repeat(3,100px);justify-content:space-between;gap:10px;margin-top:10px}
.phs div{font-size:11.5px;line-height:1.5;color:#d9d4c7;text-align:center}
.phs i{display:block;width:100px;height:150px;margin-bottom:6px;border-radius:2px;background-repeat:no-repeat;box-shadow:0 0 0 1px var(--line) inset}
.phs div:first-child i{box-shadow:0 0 0 1px #f1ede2}
.godline{display:flex;gap:12px;align-items:center;margin-top:12px;padding:8px 10px;border-radius:4px;background:rgba(255,255,255,.04);box-shadow:0 0 0 1px var(--line) inset}
.godline i{width:46px;height:66px;flex:none;background:url(../小样_山铜纪书/assets/god/god_m_fushan_01.webp) center 20%/cover;border-radius:2px}
.godline span{font-size:12.5px;line-height:1.6;color:#d9d4c7}
.godline b{display:block;font-weight:400;font-size:13.5px;letter-spacing:.14em;color:#fff}
@media (max-width:640px){
 body{overflow:auto}
 .wrap{display:block}
 header{padding:14px 16px 0;gap:10px}header img{height:42px}header h1{font-size:24px;letter-spacing:.26em}header h1 small{display:block;margin:4px 0 0;font-size:11px}
 .tog span{display:none}
 .axis{margin:12px 0 0;padding:0 16px;height:96px;overflow-x:auto;gap:8px}
 .axis::before{left:16px;right:-200px;top:28px}
 .stop{flex:none;width:76px;font-size:11.5px;letter-spacing:.06em}.stop.all{width:56px}
 .stop .dot{width:62px;height:62px}
 .bar{margin:10px 16px 0;gap:18px}.tab{font-size:15px;letter-spacing:.2em}
 .chips{display:none}
 .main{display:block;padding:12px 16px}
 .grid{grid-template-columns:repeat(3,1fr);gap:12px 10px}
 .card{width:auto}
 .img{height:142px}
 .nm{font-size:13.5px}.who{display:none}
 .panel{display:none}
}
</style></head>
<body>
<input type="radio" name="tab" id="t-cast" checked><input type="radio" name="tab" id="t-boss">
<div class="sky"></div>
<div class="wrap">
 <header><img src="../共用/assets/ui/emblem_bronze.webp" alt=""><h1>拓本<small>山铜纪图鉴 · 碑匠拓下来的人、兽与神</small></h1><span class="sp"></span>
  <span class="tog"><span>剧透</span><i></i></span><span class="x">✕</span></header>
 <div class="axis">{{AXIS}}</div>
 <div class="bar"><label class="tab cast" for="t-cast">人物<sup>{{N_CAST}}</sup></label><label class="tab boss" for="t-boss">强敌<sup>{{N_BOSS}}</sup></label>
  <span class="tab">神<sup>{{N_GOD}}</sup></span><span class="tab">生物<sup>待补</sup></span><span class="sp"></span>
  <div class="chips view-cast"><span class="chip on">全部</span><span class="chip">旅伴 {{N_A}}</span><span class="chip">相遇 {{N_B}}</span><span class="chip">传奇 {{N_C}}</span></div></div>
 <div class="main">
  <div class="list">
   <div class="view-cast">{{CAST}}</div>
   <div class="view-boss"><div class="bgrid">{{BOSSES}}</div></div>
  </div>
  <aside class="panel view-cast">{{PANEL}}</aside>
  <aside class="panel view-boss">{{BPANEL}}</aside>
 </div>
</div>
<script>if(location.hash==='#boss')document.getElementById('t-boss').checked=true;
var ax=document.querySelector('.axis'),on=ax.querySelector('.stop.on');if(ax.scrollWidth>ax.clientWidth)ax.scrollLeft=on.offsetLeft-ax.clientWidth/2+on.offsetWidth/2;</script>
</body></html>
'''


def atlas_pos(pa, key, w, h):
    """在 pa 拼图里取一格，返回 (图名, css)。拼图一格 2:3，框 w×h，按宽缩放，从格子顶上取。"""
    for name, a in pa.items():
        if key in a['k']:
            i = a['k'].index(key)
            c, r = a['c'], a.get('r') or (len(a['k']) + a['c'] - 1) // a['c']
            col, row = i % c, i // c
            cw = w
            ch = w * 1.5
            return name, ('background-image:url(../小样_山铜纪书/assets/pa/%s.webp);background-size:%dpx %dpx;background-position:%dpx %dpx'
                          % (name, c * cw, round(r * ch), -col * cw, -round(row * ch)))
    return None, ''


def boss_css(key, i, w, h):
    p = os.path.join(F, '小样_山铜纪书', 'assets', 'boss', key + '.webp')
    W, H = Image.open(p).size
    return W, H


def page_atlas():
    b = J('小样_山铜纪书', 'data', 'bronze.json')
    pa = J('小样_山铜纪书', 'data', 'pa.json')
    eras = b['eras'] if isinstance(b, dict) and 'eras' in b else b
    e = eras[3]
    axis = ['<div class="stop all"><div class="dot">全纪</div><small>2 — 947</small></div>']
    for i, x in enumerate(eras):
        axis.append('<div class="stop%s"><div class="dot" style="background-image:url(../小样_山铜纪书/assets/cg/e%d.webp)"></div>%s<small>%s</small></div>'
                    % (' on' if i == 3 else '', i + 1, esc(x['title']), esc(x['years'].replace(' ', ''))))

    def card(x, kind, extra_tags=(), sel=False):
        name, css = atlas_pos(pa, x.get('key') or '', 155, 207) if x.get('key') else (None, '')
        img = '<div class="img" style="%s"></div>' % css if name else '<div class="img none"></div>'
        tags = ['<span class="tg">%s</span>' % kind] + list(extra_tags)
        who = x.get('who') or x.get('tag') or ''
        return ('<div class="card%s"><div class="frame">%s</div><div class="nm">%s</div><div class="who">%s</div><div class="tags">%s</div></div>'
                % (' sel' if sel else '', img, esc(x['name']), esc(who), ''.join(tags)))

    cast = e['cast']
    th = next(x for x in cast if x['name'].startswith('索恩薇娅'))
    order = [th] + [x for x in cast if x is not th]
    a_cards = ''.join(card(x, '旅伴', sel=(x is th)) for x in order[:8])
    meets = [x for x in e['meet'] if x.get('key')][:6] + [x for x in e['meet'] if not x.get('key')][:2]
    b_cards = ''.join(card(x, '相遇') for x in meets)
    leg = [x for x in e['legends']]
    c_cards = ''.join(card(x, '传奇', ['<span class="tg lg">%s</span>' % esc(x['title'])] if x.get('title') else []) for x in leg[:8])
    cast_html = ('<div class="grp">旅伴<small>这八十一年最有天分的年轻人</small><a>全部 %d ›</a></div><div class="grid">%s</div>'
                 '<div class="grp">相遇<small>大人和老人，故事的配角</small><a>全部 %d ›</a></div><div class="grid">%s</div>'
                 '<div class="grp">传奇<small>此刻在世的至强</small><a>全部 %d ›</a></div><div class="grid">%s</div>'
                 % (len(cast), a_cards, len(e['meet']), b_cards, len(leg), c_cards))

    # 详情：索恩薇娅，四套衣服取档案那一张拼图的上半
    ps = 'background-image:url(../小样_山铜纪书/assets/ps/%s.webp);' % th['key']
    fig = ps + 'background-size:880px auto;background-position:0 0'
    outs = ''.join('<i class="%s" style="%sbackground-size:176px auto;background-position:%dpx 0"></i>' % ('on' if k == 0 else '', ps, -k * 44) for k in range(4))
    segs = '、'.join(th.get('seg') or [])
    panel = ('<div class="hero"><span class="k">旅伴 · 黎明的年月</span><div class="fig" style="%s"></div></div>'
             '<div class="pb"><h2>%s</h2><div class="meta"><span class="tg">%s</span><span class="tg">旅伴</span><span class="tg lock">往后 · 剧透关着</span></div>'
             '<p>%s</p>'
             '<div class="row"><b>在这一段</b><span>%s</span></div>'
             '<div class="row lock"><b>往后</b><span>剧透开关关着，不露往后的事。</span></div>'
             '<div class="outs">%s</div>'
             '<div class="btns"><span class="bt pri">看档案</span><span class="bt">去那一段</span></div></div>'
             % (fig, esc(th['name']), esc(th.get('race') or ''), esc(th.get('who') or ''), esc(segs), outs))

    # 强敌
    def bimg(key, i, n, w, h):
        p = os.path.join(F, '小样_山铜纪书', 'assets', 'boss', key + '.webp')
        W, H = Image.open(p).size
        s = h / H
        cw = W / n * s
        x = -(i * cw) - (cw - w) / 2
        return ('background-image:url(../小样_山铜纪书/assets/boss/%s.webp);background-size:%dpx %dpx;background-position:%dpx 0'
                % (key, round(W * s), h, round(x)))

    bosses = e['bosses']
    bh = []
    for k, x in enumerate(bosses):
        n = len(x['imgs'])
        key = x['imgs'][0]
        bh.append('<div class="card bc%s"><div class="frame"><div class="img" style="%s"></div></div><div class="nm">%s</div>'
                  '<div class="yr">%s年 · %d 阶</div><div class="ph">%s</div></div>'
                  % (' sel' if x['name'] == '葛摩恩' else '', bimg(key, 0, n, 224, 344), esc(x['name']), x.get('year', ''), n,
                     ''.join('<i class="%s"></i>' % ('on' if j == 0 else '') for j in range(n))))
    gm = next(x for x in bosses if x['name'] == '葛摩恩')
    n = len(gm['imgs'])
    phs = ''.join('<div><i style="%s"></i>%s</div>' % (bimg(gm['imgs'][0], j, n, 100, 150), esc(ph)) for j, ph in enumerate(gm['phases']))
    god = next(g for g in e['gods'] if g.get('key'))
    W0, H0 = Image.open(os.path.join(F, '小样_山铜纪书', 'assets', 'boss', gm['imgs'][0] + '.webp')).size
    s0 = 452 / (W0 / n)
    hero_bg = ('url(../小样_山铜纪书/assets/boss/%s.webp) %dpx %dpx/%dpx %dpx no-repeat'
               % (gm['imgs'][0], round(-1 * 452), round(-(H0 * s0 - 230) * 0.42), round(W0 * s0), round(H0 * s0)))
    bpanel = ('<div class="hero" style="height:230px;background:linear-gradient(180deg,rgba(0,0,0,0) 45%%,#141418 100%%),%s"><span class="k">强敌 · %s年</span></div>'
              '<div class="pb"><h2>%s</h2><div class="meta"><span class="tg">史诗战</span><span class="tg">%d 阶</span><span class="tg lock">出在哪一条主线 · 剧透关着</span></div>'
              '<p>%s</p><div class="phs">%s</div>'
              '<div class="godline"><i></i><span><b>%s</b>%s · 神明显像</span></div>'
              '<div class="btns"><span class="bt pri">看各阶</span><span class="bt">去那一段</span></div></div>'
              % (hero_bg, gm.get('year', ''), esc(gm['name']), n, esc(gm.get('what') or ''), phs, esc(god['name']), esc(god.get('tag') or '')))
    return fill(ATLAS_TPL, RUB=noise('.9', '.88', '.82', '.07', freq='.75', oct_='3', size=260, seed=5),
                AXIS=''.join(axis), N_CAST=str(len(cast) + len(e['meet']) + len(leg)), N_BOSS=str(len(bosses)), N_GOD=str(len(e['gods'])),
                N_A=str(len(cast)), N_B=str(len(e['meet'])), N_C=str(len(leg)), CAST=cast_html, PANEL=panel,
                BOSSES=''.join(bh), BPANEL=bpanel)


# =====================================================================
# 三、建档第一幕·死之神殿·血
# =====================================================================
ACT1_TPL = r'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>样张·建档第一幕·血</title>
<style>
:root{--serif:'Noto Serif SC','Songti SC','STSong','SimSun',serif;--teal:#7fe0d0;--gold:#d8b46a;--ivory:#efe9dc}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{font-family:var(--serif);color:var(--ivory);overflow:hidden;background:#030507;-webkit-font-smoothing:antialiased}
.scene{position:fixed;inset:0;overflow:hidden}
.table{position:absolute;left:50%;top:330px;width:1700px;height:1700px;margin-left:-950px;border-radius:50%;
 background:url(../小样_牌桌/assets/table.webp) center/cover;filter:brightness(.5) saturate(.9)}
.glow{position:absolute;inset:0;background:radial-gradient(ellipse 46% 34% at 40% 70%,rgba(80,220,200,.16),rgba(0,0,0,0) 70%),radial-gradient(ellipse 90% 70% at 50% 40%,rgba(0,0,0,0) 40%,rgba(1,2,4,.85) 100%)}
.mist{position:absolute;inset:0;background:radial-gradient(ellipse 30% 10% at 30% 88%,rgba(140,230,215,.08),transparent 70%),radial-gradient(ellipse 26% 9% at 70% 84%,rgba(140,230,215,.07),transparent 70%)}
.hand{position:absolute;left:1262px;top:-306px;width:236px;height:598px;background:url(../小样_牌桌/assets/hand9_open.webp) center/contain no-repeat;transform:rotate(-8deg);filter:drop-shadow(0 0 10px rgba(127,224,208,.28)) drop-shadow(0 18px 24px rgba(0,0,0,.7));opacity:.96}
.era{position:absolute;left:34px;top:28px;display:flex;align-items:center;gap:12px}
.era i{width:34px;height:51px;border-radius:3px;background:url(../小样_牌桌/assets/bb_2.webp) center/cover;box-shadow:0 0 0 1px rgba(216,180,106,.5)}
.era span{font-size:12.5px;letter-spacing:.26em;color:#c8c2b4;line-height:1.6}
.era b{display:block;font-weight:400;font-size:14px;letter-spacing:.3em;color:#efe9dc}
.back{position:absolute;right:34px;top:30px;height:34px;padding:0 14px;border-radius:17px;display:flex;align-items:center;font-size:12.5px;letter-spacing:.2em;color:#c8c2b4;box-shadow:0 0 0 1px rgba(239,233,220,.22) inset}
.say{position:absolute;left:0;right:0;top:92px;text-align:center}
.say small{display:block;font-size:12.5px;letter-spacing:.6em;color:var(--teal);opacity:.85;text-indent:.6em}
.say p{margin-top:12px;font-size:25px;letter-spacing:.14em;color:#f5f1e8;text-shadow:0 0 18px rgba(127,224,208,.35),0 2px 6px rgba(0,0,0,.8)}
.fan{position:absolute;left:0;top:0;width:100%;height:100%}
.rc{position:absolute;width:132px;height:198px;margin:-99px 0 0 -66px;border-radius:8px;transform-origin:50% 50%}
.face{position:absolute;inset:0;border-radius:8px;overflow:hidden;
 background:radial-gradient(ellipse 90% 60% at 50% 30%,rgba(60,120,120,.35),rgba(0,0,0,0) 70%),linear-gradient(180deg,#14242a,#0a1216 70%,#070b0e);
 box-shadow:0 0 0 1px rgba(216,180,106,.75),0 0 0 4px #0b1114,0 0 0 5px rgba(216,180,106,.35),0 14px 22px rgba(0,0,0,.6)}
.face .pt{position:absolute;inset:6px 4px 30px;background-repeat:no-repeat;background-size:150% auto;background-position:50% 4%}
.face .nm{position:absolute;left:0;right:0;bottom:0;height:30px;display:flex;align-items:center;padding-left:12px;font-size:13px;letter-spacing:.22em;color:#f3e7c7;
 background:linear-gradient(180deg,rgba(7,11,14,0),rgba(7,11,14,.95) 40%);border-top:1px solid rgba(216,180,106,.35)}
.face::after{content:'';position:absolute;inset:3px;border-radius:6px;border:1px solid rgba(216,180,106,.22);pointer-events:none}
.rc.empty .face{background:none;box-shadow:0 0 0 1px rgba(127,224,208,.6),0 0 22px rgba(127,224,208,.35) inset,0 0 18px rgba(127,224,208,.25)}
.rc.empty .face::after{display:none}
.glyph{position:absolute;inset:26px 18px 44px;opacity:.85}
.swipe{display:none}
.pick{position:absolute;left:1118px;top:262px;width:236px;height:354px;transform:rotate(-4deg)}
.pick .face{box-shadow:0 0 0 1.5px rgba(232,200,128,.95),0 0 0 6px #0b1114,0 0 0 7px rgba(216,180,106,.45),0 0 40px rgba(127,224,208,.35),0 24px 40px rgba(0,0,0,.7)}
.pick .face .pt{inset:10px 8px 42px}
.pick .face .nm{height:42px;font-size:19px;justify-content:center;padding-left:0;letter-spacing:.4em;text-indent:.4em}
.pick::before{content:'';position:absolute;inset:-30px;border-radius:30px;background:radial-gradient(ellipse at 50% 50%,rgba(127,224,208,.22),rgba(0,0,0,0) 70%);z-index:-1}
.info{position:absolute;left:1400px;top:206px;width:470px;padding:24px 26px 22px;border-radius:8px;
 background:linear-gradient(170deg,rgba(14,24,28,.9),rgba(6,10,13,.92));box-shadow:0 0 0 1px rgba(216,180,106,.3) inset,0 20px 50px rgba(0,0,0,.6);backdrop-filter:blur(4px)}
.info h2{font-size:30px;font-weight:600;letter-spacing:.36em;color:#f6e8c4}
.info .note{margin-top:6px;font-size:14px;line-height:1.8;color:#d9d3c6}
.info .arr{margin-top:10px;padding-left:12px;border-left:2px solid rgba(127,224,208,.5);font-size:13px;line-height:1.85;color:#bfc9c6}
.subs{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px}
.sb{padding:9px 12px;border-radius:4px;box-shadow:0 0 0 1px rgba(239,233,220,.16) inset;background:rgba(255,255,255,.025)}
.sb b{display:block;font-weight:400;font-size:14.5px;letter-spacing:.24em;color:#f1ead9}
.sb span{font-size:12px;letter-spacing:.06em;color:#aaa496}
.sb.on{box-shadow:0 0 0 1px rgba(232,200,128,.9) inset;background:rgba(216,180,106,.1)}
.sb.off{opacity:.42}
.sb.off span{color:#8d8778}
.pn{margin-top:14px;font-size:12.5px;line-height:1.8;color:#9fb1ad}
.pn b{font-weight:400;color:var(--teal);letter-spacing:.2em;margin-right:6px}
.btns{display:flex;gap:10px;margin-top:18px}
.bt{flex:1;height:42px;border-radius:21px;display:grid;place-items:center;font-size:14px;letter-spacing:.3em;color:#e9e3d6;box-shadow:0 0 0 1px rgba(239,233,220,.3) inset}
.bt.pri{color:#1b1406;background:linear-gradient(180deg,#f0d491,#c99e4c);box-shadow:0 0 18px rgba(216,180,106,.35)}
.prog{position:absolute;left:0;right:0;bottom:22px;display:flex;justify-content:center;gap:26px;list-style:none}
.pg{display:flex;flex-direction:column;align-items:center;gap:7px;font-size:12px;letter-spacing:.24em;color:#8f8a7e}
.pg i{width:36px;height:54px;border-radius:4px;background:url(../小样_牌桌/assets/back_2.webp) center/cover;box-shadow:0 0 0 1px rgba(216,180,106,.35);filter:brightness(.55)}
.pg.done i{background:linear-gradient(180deg,#1c2c30,#0c1416);box-shadow:0 0 0 1px rgba(216,180,106,.8);filter:none}
.pg.done i::before{content:'✓';display:grid;place-items:center;height:100%;color:#e8c886;font-style:normal;font-size:16px}
.pg.done{color:#d6cfbf}
.pg.cur{color:#f4ecd8}
.pg.cur i{filter:none;box-shadow:0 0 0 1.5px var(--teal),0 0 16px rgba(127,224,208,.6);transform:translateY(-6px)}
@media (max-width:640px){
 body{overflow:auto}
 .scene{position:fixed}
 .table{left:50%;top:420px;width:900px;height:900px;margin-left:-450px}
 html,body{overflow-x:hidden}
 .hand{left:auto;right:6px;top:-176px;width:132px;height:340px;transform:none}
 .era{left:14px;top:62px}.era i{width:24px;height:36px}.era span{font-size:11px}.era b{font-size:12.5px}
 .back{display:none}
 .prog{position:fixed;top:0;bottom:auto;left:0;right:0;gap:6px;padding:10px 12px 8px;background:linear-gradient(#030507 75%,rgba(3,5,7,0));z-index:9}
 .pg{font-size:9.5px;letter-spacing:.1em;gap:3px}
 .pg i{width:22px;height:33px;border-radius:3px}
 .pg.done i::before{font-size:11px}
 .pg.cur i{transform:none}
 .say{position:relative;top:auto;padding:118px 18px 0}
 .say p{font-size:17px;letter-spacing:.06em;line-height:1.7}
 .fan{position:relative;height:350px;margin-top:6px}
 .rc{display:none}
 .rc.near,.rc.pick{display:block}
 .swipe{display:block;position:absolute;left:0;right:0;bottom:-2px;text-align:center;font-size:12px;letter-spacing:.3em;color:#8fb9b2}
 .pick{left:50%;top:22px;width:190px;height:285px;margin:0 0 0 -95px;transform:none}
 .info{position:relative;left:auto;top:auto;width:auto;margin:6px 12px 90px;padding:18px 18px 16px;backdrop-filter:none}
 .info h2{font-size:24px}
 .subs{grid-template-columns:1fr 1fr}
 .btns{position:fixed;left:12px;right:12px;bottom:12px;margin:0;z-index:9}
 .btns .bt:not(.pri){display:none}
}
</style></head>
<body>
<div class="scene"><div class="table"></div><div class="glow"></div><div class="mist"></div></div>
<div class="hand"></div>
<div class="era"><i></i><span><b>山铜纪 · 黎明的年月</b>661 — 741</span></div>
<span class="back">回到牌桌</span>
<div class="say"><small>第二张 · 血</small><p>{{LINE}}</p></div>
<div class="fan">{{FAN}}
 <div class="swipe">‹ 左右滑，十二张血 ›</div>
 <div class="rc pick"><div class="face"><div class="pt" style="background-image:url({{PICK_IMG}})"></div><div class="nm">{{PICK_NAME}}</div></div></div>
</div>
<div class="info">
 <h2>{{RACE}}</h2>
 <div class="note">{{NOTE}}</div>
 <div class="arr">{{ARRIVE}}</div>
 <div class="subs">{{SUBS}}</div>
 <div class="pn"><b>这一段</b>{{PNOTE}}</div>
 <div class="btns"><span class="bt">再看看</span><span class="bt pri">就是这一副血</span></div>
</div>
{{PROG}}
</body></html>
'''

PICK = {'human': ('人类_晨曦_样张.json', 'pc_h_cx_f1'), 'elf': ('精灵.json', 'pc_e_gd_f1'), 'dwarf': ('矮人.json', 'pc_d_lm_m1'),
        'halfling': ('半身人.json', 'pc_hf_ql_f1'), 'beastkin': ('兽耳族.json', 'pc_k_lw_f1'), 'halforc': ('半兽人.json', 'pc_o_ls_m1'),
        'dragonborn': ('龙裔.json', 'pc_dr_tj_f1'), 'truedragon': ('真龙幼体.json', 'pc_td_sy_m1'), 'demon': ('魔族_一.json', 'pc_dm_dd_f1'),
        'tiefling': ('提夫林.json', 'pc_t_lc_f1')}
PC_OUT = os.path.join(R, '底稿', '状态栏', 'comfy', 'out', '立绘_主角')
WAVE = ("<svg viewBox='0 0 100 140' xmlns='http://www.w3.org/2000/svg'><g fill='none' stroke='#7fe0d0' stroke-width='2.2' stroke-linecap='round'>"
        "<path d='M14 64 C26 50 38 50 46 62 C54 74 66 74 78 60 C84 53 90 52 94 56'/><path d='M8 86 C22 72 36 72 46 84 C56 96 70 96 84 82'/>"
        "<path d='M18 108 C30 98 42 98 50 106 C58 114 70 114 82 104' opacity='.6'/><circle cx='50' cy='34' r='10' opacity='.75'/></g></svg>")
QUILL = ("<svg viewBox='0 0 100 140' xmlns='http://www.w3.org/2000/svg'><g fill='none' stroke='#d8b46a' stroke-width='2' stroke-linecap='round'>"
         "<path d='M70 22 C46 40 34 68 30 110'/><path d='M70 22 C76 46 66 74 34 100'/><path d='M70 22 C54 34 46 52 44 74' opacity='.6'/>"
         "<path d='M24 118 H78' stroke-dasharray='3 6'/></g></svg>")


def pc_img(race):
    f, k = PICK[race]
    p = os.path.join(PC_OUT, k, 'cell_casual.png')
    if not os.path.exists(p):
        d = json.load(open(os.path.join(R, '底稿', '状态栏', 'comfy', 'cast', '主角', f), encoding='utf-8'))
        items = d if isinstance(d, list) else (d.get('cast') or [v for v in d.values() if isinstance(v, dict)])
        for x in items:
            q = os.path.join(PC_OUT, x['en'], 'cell_casual.png')
            if os.path.exists(q):
                k, p = x['en'], q
                break
    return '../../状态栏/comfy/out/立绘_主角/%s/cell_casual.png' % k


def page_act1():
    import math
    B = J('小样_外壳', 'data', 'build.json')
    E = B['eras']['bronze']
    P = next(p for p in E['periods'] if p['id'] == 'liming')
    races = P['races']
    line = next(l['line'] for l in B['ronova']['lines'] if l['use'] == '样子和立绘')
    cards = []
    n = len(races)
    races = [r for r in races if r != 'human']
    races.insert(5, 'human')
    cx, pivot, R_ = 712, 1760, 1180
    for i, rk in enumerate(races):
        a = (i - (n - 1) / 2) * 5.0
        x = cx + R_ * math.sin(math.radians(a))
        y = pivot - R_ * math.cos(math.radians(a))
        name = E['races'][rk]['name']
        near = ' near' if False else ''
        if rk == 'human':
            cards.append('<div class="rc empty" style="left:%dpx;top:%dpx;transform:rotate(%.1fdeg)"><div class="face"></div></div>' % (x, y, a))
            continue
        if rk in PICK:
            inner = '<div class="pt" style="background-image:url(%s)"></div>' % pc_img(rk)
        else:
            inner = '<div class="glyph" style="background:%s center/contain no-repeat"></div>' % svg_url(WAVE if rk == 'merfolk' else QUILL)
        cards.append('<div class="rc%s" style="left:%dpx;top:%dpx;transform:rotate(%.1fdeg)"><div class="face">%s<div class="nm">%s</div></div></div>'
                     % (near, x, y, a, inner, esc(name)))
    hu = E['races']['human']
    subs = []
    for s in hu['subs']:
        off = s.get('from') and s['from'] > P['to']
        subs.append('<div class="sb%s"><b>%s</b><span>%s</span></div>'
                    % (' off' if off else (' on' if s['name'] == '晨曦' else ''), esc(s['name']), esc(s.get('when') if off else s['note'])))
    return fill(ACT1_TPL, LINE=esc(line), FAN=''.join(cards), PICK_IMG=pc_img('human'), PICK_NAME=esc(hu['name']),
                RACE=esc(hu['name']), NOTE=esc(hu['note']) + '。', ARRIVE=esc(hu['arrive']), SUBS=''.join(subs),
                PNOTE=esc(P['race_notes']['human']), PROG=progress_html(1, 1))


# =====================================================================
# 四、建档第二幕·落地·段城的兵册
# =====================================================================
ACT2_TPL = r'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>样张·建档第二幕·兵册</title>
<style>
:root{--serif:'Noto Serif SC','Songti SC','STSong','SimSun',serif;--kai:'KaiTi','STKaiti','Noto Serif SC',serif;--ink:#1f1d1a;--paper:#e9e2cf}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{font-family:var(--serif);color:#efe9dc;overflow:hidden;background:#07080b;-webkit-font-smoothing:antialiased}
.bg{position:fixed;inset:0;background:url(../小样_山铜纪书/assets/cg/e4.webp) 64% 40%/cover;filter:saturate(.95)}
.shade{position:fixed;inset:0;background:linear-gradient(90deg,rgba(6,7,10,.9) 0,rgba(6,7,10,.78) 30%,rgba(6,7,10,.18) 58%,rgba(6,7,10,.35) 100%),linear-gradient(0deg,rgba(6,7,10,.88) 0,rgba(6,7,10,0) 30%)}
.era{position:absolute;left:64px;top:44px;font-size:12.5px;letter-spacing:.3em;color:#bdb6a6;line-height:1.7}
.era b{display:block;font-weight:400;font-size:15px;letter-spacing:.34em;color:#f1ebdd}
.clerk{position:absolute;left:64px;top:170px;width:560px}
.clerk small{display:flex;align-items:center;gap:10px;font-size:12.5px;letter-spacing:.5em;color:#cbbf9f}
.clerk small::before{content:'';width:26px;height:1px;background:#cbbf9f}
.clerk p{margin-top:16px;font-size:30px;line-height:1.6;letter-spacing:.1em;color:#fbf6ea;text-shadow:0 2px 10px rgba(0,0,0,.7)}
.rules{margin-top:34px;padding:16px 18px;border-radius:4px;background:rgba(255,255,255,.04);box-shadow:0 0 0 1px rgba(239,233,220,.14) inset}
.rules h4{font-weight:400;font-size:12.5px;letter-spacing:.42em;color:#cbbf9f;margin-bottom:8px}
.rules li{list-style:none;font-size:13.5px;line-height:1.85;color:#d6d0c2;padding-left:16px;position:relative}
.rules li::before{content:'';position:absolute;left:2px;top:.85em;width:5px;height:5px;transform:rotate(45deg);background:#a99b78}
.rules li b{font-weight:400;color:#f1ebdd;letter-spacing:.12em}
.ledger{position:absolute;left:760px;top:120px;width:1080px;height:640px;transform:rotate(-1.4deg);border-radius:4px;
 background:{{FIBER}},{{GRAIN}},linear-gradient(180deg,#ece5d2,#e3dac3 70%,#d8cdb2);color:var(--ink);
 box-shadow:0 0 0 1px rgba(60,48,30,.35),0 30px 60px rgba(0,0,0,.65),0 4px 0 #cfc3a6,0 7px 0 #bdb093}
.ledger::before{content:'';position:absolute;left:0;right:0;top:0;height:30px;background:linear-gradient(180deg,#2b2a2f,#16161a);border-radius:4px 4px 0 0;box-shadow:0 2px 0 #0a0a0c}
.ledger::after{content:'';position:absolute;left:24px;right:24px;top:14px;height:2px;background:repeating-linear-gradient(90deg,#d9d2bf 0 10px,transparent 10px 22px);opacity:.75}
.lh{position:absolute;left:0;right:0;top:46px;text-align:center}
.lh b{font-family:var(--kai);font-size:30px;letter-spacing:.5em;text-indent:.5em;font-weight:700;color:#1b1a18}
.lh span{display:block;margin-top:4px;font-size:12px;letter-spacing:.42em;color:#6d6455}
.tbl{position:absolute;left:46px;right:46px;top:128px;border-collapse:collapse;width:calc(100% - 92px);table-layout:fixed}
.tbl th{font-weight:400;font-size:13px;letter-spacing:.4em;color:#5a5142;text-align:left;padding:0 12px 8px;border-bottom:2px solid #3a342b}
.tbl td{height:46px;padding:0 12px;border-bottom:1px solid rgba(58,52,43,.32);font-family:var(--kai);font-size:21px;color:#2a2620;vertical-align:middle}
.tbl td+td,.tbl th+th{border-left:1px solid rgba(58,52,43,.18)}
.tbl td.s{background:{{SCRIBBLE}} 10px 50%/auto 22px no-repeat;opacity:.55}
.tbl td.s2{background:{{SCRIBBLE2}} 10px 50%/auto 20px no-repeat;opacity:.5}
.tbl tr.me td{background:linear-gradient(180deg,rgba(255,236,170,.22),rgba(255,236,170,.08));border-bottom:1px solid #3a342b}
.in{display:flex;align-items:center;gap:2px;height:32px;padding:0 8px;border-radius:2px;box-shadow:0 0 0 1px rgba(90,76,52,.45) inset;background:rgba(255,252,240,.55);font-family:var(--serif);font-size:14px;letter-spacing:.12em;color:#8a7f6c}
.in.cur{box-shadow:0 0 0 1.5px #7a5d24 inset,0 0 0 4px rgba(200,160,80,.18)}
.in.cur::before{content:'';width:1.5px;height:20px;background:#2a2620;margin-right:4px}
.ink{font-family:var(--kai);font-size:21px;color:#1f1c18}
.hint{position:absolute;left:46px;right:220px;top:500px;padding-top:12px;font-size:13.5px;line-height:1.8;color:#6b604e;border-top:1px dashed rgba(90,76,52,.4)}
.hint b{font-weight:400;letter-spacing:.3em;color:#3b342a;margin-right:8px}
.stamp{position:absolute;right:58px;bottom:42px;width:128px;height:128px;border:1.5px dashed rgba(90,76,52,.45);border-radius:6px;display:grid;place-items:center;text-align:center;font-size:11.5px;line-height:1.6;letter-spacing:.2em;color:#8a7f6c}
.seal{display:none;position:absolute;right:46px;bottom:30px;width:150px;height:150px;transform:rotate(-9deg);mix-blend-mode:multiply;opacity:.92;background:{{SEAL}} center/contain no-repeat}
.next{position:absolute;right:80px;bottom:64px;height:46px;padding:0 30px;border-radius:23px;display:flex;align-items:center;gap:10px;font-size:15px;letter-spacing:.34em;color:#16130c;background:linear-gradient(180deg,#f2ead6,#cfc4a6);box-shadow:0 10px 24px rgba(0,0,0,.5)}
.endbtns{display:none;position:absolute;left:760px;right:80px;bottom:52px;justify-content:flex-end;gap:12px}
.endbtns span{height:44px;padding:0 22px;border-radius:22px;display:grid;place-items:center;font-size:14px;letter-spacing:.26em;color:#ece6d8;background:rgba(10,10,14,.55);box-shadow:0 0 0 1px rgba(239,233,220,.3) inset;backdrop-filter:blur(4px)}
.endbtns span.pri{color:#16130c;background:linear-gradient(180deg,#f2ead6,#cfc4a6);box-shadow:0 10px 24px rgba(0,0,0,.5)}
.prog{position:absolute;left:64px;bottom:44px;display:flex;gap:16px;list-style:none}
.pg{display:flex;flex-direction:column;align-items:center;gap:6px;font-size:11.5px;letter-spacing:.2em;color:#8a8478}
.pg i{width:28px;height:42px;border-radius:3px;background:url(../小样_牌桌/assets/back_2.webp) center/cover;box-shadow:0 0 0 1px rgba(216,180,106,.35);filter:brightness(.55)}
.pg.done i{background:linear-gradient(180deg,#22262c,#121418);box-shadow:0 0 0 1px rgba(232,227,214,.75);filter:none}
.pg.done i::before{content:'✓';display:grid;place-items:center;height:100%;color:#ece6d8;font-style:normal;font-size:13px}
.pg.done{color:#cfc9bb}
.pg.cur{color:#fff}
.pg.cur i{filter:none;box-shadow:0 0 0 1.5px #f1ede2,0 0 14px rgba(255,248,226,.6);transform:translateY(-5px)}
body.sealed .stamp,body.sealed .next,body.sealed .tbl tr.me .in,body.sealed .hint,body.sealed .clerk .q{display:none}
body.sealed .seal{display:block}
body.sealed .pg i{background:linear-gradient(180deg,#22262c,#121418);box-shadow:0 0 0 1px rgba(232,227,214,.75);filter:none;transform:none}
body.sealed .pg i::before{content:'✓';display:grid;place-items:center;height:100%;color:#ece6d8;font-style:normal;font-size:13px}
body.sealed .pg{color:#cfc9bb}
body.sealed .endbtns{display:flex}
.fill{display:none}
body.sealed .fill{display:inline}
.clerk .n{display:none}
body.sealed .clerk .n{display:block}
@media (max-width:640px){
 body{overflow:auto}
 .bg{background-position:58% 30%;height:340px;bottom:auto}
 .shade{background:linear-gradient(180deg,rgba(6,7,10,.35) 0,rgba(6,7,10,.6) 30%,#07080b 46%)}
 .prog{position:fixed;left:0;right:0;top:0;bottom:auto;gap:6px;justify-content:center;padding:10px 0 8px;background:linear-gradient(#07080b 75%,rgba(7,8,11,0));z-index:9}
 .pg{font-size:9.5px;letter-spacing:.08em;gap:3px}.pg i{width:22px;height:33px}.pg.cur i{transform:none}
 .era{left:18px;top:66px;font-size:11px}.era b{font-size:13px}
 .clerk{position:relative;left:auto;top:auto;width:auto;padding:150px 18px 0}
 .clerk p{font-size:21px}
 .rules{display:none}
 .ledger{position:relative;left:auto;top:auto;width:auto;height:auto;margin:20px 12px 0;padding:44px 16px 18px;transform:none}
 .lh{position:static}.lh b{font-size:22px}
 .tbl{position:static;width:100%;margin-top:14px}
 .tbl thead,.tbl tr:not(.me){display:none}
 .tbl tr.me{display:flex;flex-direction:column;gap:12px}
 .tbl tr.me td{display:block;height:auto;padding:0;border:0;background:none}
 .tbl tr.me td::before{content:attr(data-k);display:block;font-family:var(--serif);font-size:12px;letter-spacing:.36em;color:#6d6455;margin-bottom:5px}
 .in{height:44px;font-size:15px}
 .hint{position:static;margin-top:16px}
 .stamp{display:none}
 .next{position:fixed;left:12px;right:12px;bottom:12px;justify-content:center;z-index:9}
}
</style></head>
<body>
<div class="bg"></div><div class="shade"></div>
<div class="era"><b>山铜纪 · 黎明的年月</b>661 — 741 · 你落在长垒南段</div>
<div class="clerk"><small>{{WHO}}</small><p class="q">{{ASK}}</p><p class="n">{{NARR}}</p>
 <div class="rules"><h4>这一年的规矩</h4><ul>{{RULES}}</ul></div></div>
<div class="ledger">
 <div class="lh"><b>{{TITLE}}</b><span>双井段城 · 第四页</span></div>
 <table class="tbl"><thead><tr>{{TH}}</tr></thead><tbody>{{ROWS}}
  <tr class="me">
   <td data-k="名字"><span class="in cur">写下你的名字</span><span class="fill ink">诺拉</span></td>
   <td data-k="姓或家"><span class="in">报不出就空着</span><span class="fill ink" style="color:#8a7f6c;font-size:16px">（无）</span></td>
   <td data-k="族"><span class="ink">人类 · 晨曦</span></td>
   <td data-k="从哪里来"><span class="in">守哪一段墙</span><span class="fill ink" style="font-size:18px">南段 · 双井段城</span></td>
  </tr></tbody></table>
 <div class="hint"><b>报不出的</b>{{BLANK}}</div>
 <div class="stamp">写满这一行<br>碑匠的凿印<br>盖在这里</div>
 <div class="seal"></div>
</div>
<span class="next">下一张 ›</span>
<div class="endbtns"><span>回到牌桌</span><span>回去改</span><span>复制</span><span class="pri">填进输入框</span></div>
{{PROG}}
<script>if(location.hash==='#seal')document.body.classList.add('sealed');</script>
</body></html>
'''

SCRIBBLE = ("<svg xmlns='http://www.w3.org/2000/svg' width='120' height='24' viewBox='0 0 120 24'><path d='M2 15 C8 6 12 6 14 13 C16 19 20 4 25 10 C29 15 31 17 35 9 C38 4 41 18 46 13 "
            "C50 9 52 6 57 12 M66 13 C70 6 74 7 77 13 C80 18 84 5 88 11 C91 15 95 16 99 9' fill='none' stroke='%23231f1a' stroke-width='1.6' stroke-linecap='round'/></svg>")


def page_act2():
    B = J('小样_外壳', 'data', 'build.json')
    E = B['eras']['bronze']
    sh = E['sheet']
    th = ''.join('<th>%s</th>' % esc(c) for c in sh['cols'])
    rows = []
    for i in range(6):
        cls = ['s', 's2', 's2' if i % 2 else 's', 's2']
        rows.append('<tr>' + ''.join('<td class="%s"></td>' % cls[(i + j) % 4] for j in range(4)) + '</tr>')
    more = {m['label']: m['line'] for m in sh.get('more', [])}
    rules = ''.join('<li><b>%s</b>　%s</li>' % (esc(k), esc(more[k])) for k in ('从哪里来', '雨城') if k in more)
    seal = svg_url("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 150 150'><defs>"
                   "<filter id='r'><feTurbulence type='fractalNoise' baseFrequency='.06' numOctaves='2' seed='4'/><feDisplacementMap in='SourceGraphic' scale='6'/></filter>"
                   "<filter id='i'><feTurbulence type='fractalNoise' baseFrequency='.7' numOctaves='2' seed='9' result='t'/>"
                   "<feColorMatrix in='t' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -2.4 1.75' result='m'/><feComposite in='SourceGraphic' in2='m' operator='in'/></filter></defs>"
                   "<g filter='url(#r)'><g filter='url(#i)'>"
                   "<rect x='9' y='9' width='132' height='132' rx='5' fill='none' stroke='#2b2b31' stroke-width='8'/>"
                   "<rect x='22' y='22' width='106' height='106' fill='none' stroke='#2b2b31' stroke-width='2.4'/>"
                   "<path d='M28 28 L44 44 M122 28 L106 44 M28 122 L44 106 M122 122 L106 106' stroke='#2b2b31' stroke-width='2'/>"
                   "<text x='75' y='70' font-size='42' text-anchor='middle' font-family='KaiTi,STKaiti,serif' font-weight='700' fill='#2b2b31'>入</text>"
                   "<text x='75' y='116' font-size='42' text-anchor='middle' font-family='KaiTi,STKaiti,serif' font-weight='700' fill='#2b2b31'>册</text>"
                   "</g></g></svg>")
    return fill(ACT2_TPL, FIBER=noise('.42', '.34', '.2', '.12', freq='.012', oct_='3', size=600, seed=3),
                GRAIN=noise('.36', '.3', '.2', '.22', freq='.85', oct_='3', size=220, seed=6),
                SCRIBBLE='url("data:image/svg+xml;utf8,' + SCRIBBLE.replace("'", "%27").replace(' ', '%20').replace('<', '%3C').replace('>', '%3E') + '")',
                SCRIBBLE2='url("data:image/svg+xml;utf8,' + SCRIBBLE.replace('99 9', '72 12').replace("'", "%27").replace(' ', '%20').replace('<', '%3C').replace('>', '%3E') + '")',
                SEAL=seal, WHO=esc(sh['who']), TITLE=esc(sh['title']), TH=th, ROWS=''.join(rows),
                ASK='报得出姓就报姓。报不出，就报你守哪一段墙。',
                NARR=esc(more.get('碑上的名字', '')), RULES=rules, BLANK=esc(sh['blank']['line']), PROG=progress_html(4, 4))


if __name__ == '__main__':
    write('wb_moon.html', page_wb())
    write('atlas_bronze.html', page_atlas())
    write('build_act1.html', page_act1())
    write('build_act2.html', page_act2())
