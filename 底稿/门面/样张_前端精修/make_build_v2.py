# -*- coding: utf-8 -*-
"""建档第二版的样张（11-17）：照 1001 底卡建档的步子，两屏。
  build_v2.html        纷争纪 · 1150 年 · 命路（有名字的亮着，还没有名字的灰着、可以选，选了就是先行者）
  build_v2.html#gold   纷争纪 · 3600 年开局 · 金血祝颂（神亲只从出生那一年还在世的正神里挑）
用法：带 PIL 的 Python 在仓库根上跑 python -I -X utf8 底稿/门面/样张_前端精修/make_build_v2.py
神明显像的图在 底稿/状态栏/comfy/out/神明显像_art/（不进库）。只做样子，金血祝颂那一颗是示例。"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.dirname(HERE)
esc = lambda s: html.escape(s or '', quote=True)
B = json.load(open(os.path.join(F, '小样_外壳', 'data', 'build.json'), encoding='utf-8'))
TYPES = {p['name']: p for p in B['paths']}
SP = B['eras']['strife']['paths']
YEAR = 1150
STEPS = ['魂', '睁眼之前', '胎骨', '金血', '起点', '六维', '命路', '命星', '誓心与出身', '落在哪', '铸印']
GODIMG = '../../状态栏/comfy/out/神明显像_art/%s.webp'
# 纷争纪 3580 年前后（3600 年开局，你二十岁上下）：七位，和七十二位里的几位；倒下的年份照神谱
GODS = [
    ('god_p_lixian', '风之璐璐薇', '风、速度、远行、弓弩与自由', None, True),
    ('god_p_fushan', '大地之欧巴德斯', '大地', None, True),
    ('god_p_fanye', '元素之伊兹帕鲁特', '元素、魔法、知识与术式', None, True),
    ('god_p_fanqing', '收获之库米罗妮', '收获、草木、生命与循环', None, True),
    ('god_p_libian', '幸运之艾赫卡托尔', '幸运、偶然、命运偏折', None, True),
    ('god_p_jingguang', '治愈之朱亚', '治愈、慈悲、救赎', None, True),
    ('god_p_butui', '战祸之耶万', '战争、军略、勇气与胜负', None, True),
    ('god_z_fanye_02', '朝潮夕汐之主乌姆拉', '海与潮', 10903, False),
    ('god_z_lixian_02', '千骑之首瑞恩达尔', '骏马、疾驰与追猎', 4200, False),
    ('god_z_lixian_04', '满帆之手欧希拉', '远航与顺风', 10903, False),
    ('god_z_lixian_05', '未落之箭卡瑟蕾', '弓与射艺', 5933, False),
    ('god_z_fushan_01', '擎山者多尔加恩', '山岳与地基', 10991, False),
    ('god_z_fushan_07', '城门的脊梁贝奥尔', '门与守城', 10769, False),
    ('god_z_jingguang_01', '疫棚里的凉风塞雷娜', '瘟疫止息', 10769, False),
    ('god_z_fushan_05', '百锤之父卡尔德隆', '锻炉与火候', 2104, False),
    ('god_z_fanye_05', '暴雨之王伊斯卡图', '雷霆', 2104, False),
    ('god_z_fanye_04', '灯芯与灰烬的女主人莉薇兰', '灯火', 2104, False),
]

CSS = r'''
:root{--serif:'Noto Serif SC','Songti SC','STSong','SimSun',serif;--gold:#d8b46a;--teal:#7fe0d0;--ivory:#efe9dc;--red:#a3454b}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{font-family:var(--serif);color:var(--ivory);background:#05060a;overflow:hidden;-webkit-font-smoothing:antialiased}
.bg{position:fixed;inset:-40px;background:url(../小样_牌桌/assets/era_1.webp) center/cover;filter:blur(18px) brightness(.28) saturate(.8)}
.vig{position:fixed;inset:0;background:radial-gradient(ellipse 80% 70% at 55% 45%,rgba(5,6,10,.15),rgba(5,6,10,.85))}
.wrap{position:relative;height:100%;display:grid;grid-template-columns:230px 1fr 430px;gap:28px;padding:30px 40px 28px}
.rail{display:flex;flex-direction:column;gap:2px;padding-top:6px}
.rail h4{font-weight:400;font-size:12px;letter-spacing:.42em;color:#a59c88;margin:0 0 4px}
.rail .era{font-size:15px;letter-spacing:.24em;color:#f3ead6;margin-bottom:16px;line-height:1.6}
.rail .era small{display:block;font-size:12px;letter-spacing:.14em;color:#a59c88}
.st{display:flex;align-items:center;gap:12px;padding:7px 0;font-size:14px;letter-spacing:.2em;color:#7f786b}
.st i{width:22px;height:33px;border-radius:3px;flex:none;background:url(../小样_牌桌/assets/back_1.webp) center/cover;box-shadow:0 0 0 1px rgba(216,180,106,.3);filter:brightness(.5)}
.st.done{color:#cfc7b4}.st.done i{background:linear-gradient(180deg,#2a1a1c,#140a0b);filter:none;box-shadow:0 0 0 1px rgba(216,180,106,.75)}
.st.done i::before{content:'✓';display:grid;place-items:center;height:100%;font-style:normal;font-size:12px;color:#e8c886}
.st.cur{color:#fff}.st.cur i{filter:none;box-shadow:0 0 0 1.5px var(--gold),0 0 14px rgba(216,180,106,.55)}
.st.opt{color:#8f7c5a}.st.opt span::after{content:'选';font-size:10px;letter-spacing:0;margin-left:6px;padding:0 5px;border-radius:7px;box-shadow:0 0 0 1px rgba(216,180,106,.5) inset;color:#d8b46a}
.main{min-height:0;display:flex;flex-direction:column}
.hd small{font-size:12.5px;letter-spacing:.5em;color:var(--gold)}
.hd h1{font-size:34px;font-weight:600;letter-spacing:.3em;margin-top:6px;color:#f6ecd4}
.hd p{margin-top:8px;font-size:14.5px;line-height:1.85;color:#cfc7b6;max-width:880px}
.hd p b{font-weight:400;color:var(--gold)}
.grid{margin-top:16px;display:grid;gap:10px;overflow:hidden}
.paths{grid-template-columns:repeat(4,1fr)}
.grp{grid-column:1/-1;font-size:12px;letter-spacing:.4em;color:#a59c88;margin:6px 0 -2px}
.pc{position:relative;padding:10px 12px 10px 14px;border-radius:4px;background:linear-gradient(160deg,rgba(40,24,26,.88),rgba(16,10,11,.92));box-shadow:0 0 0 1px rgba(216,180,106,.45) inset}
.pc b{display:block;font-size:17px;letter-spacing:.24em;font-weight:600;color:#f6ead0}
.pc em{display:block;font-style:normal;font-size:11.5px;letter-spacing:.1em;color:#b9ac90;margin-top:1px}
.pc span{display:block;font-size:12px;line-height:1.6;color:#d8cfbd;margin-top:5px}
.pc .y{position:absolute;right:10px;top:10px;font-size:11px;letter-spacing:.06em;color:var(--gold)}
.pc.grey{background:linear-gradient(160deg,rgba(28,28,32,.75),rgba(14,14,17,.85));box-shadow:0 0 0 1px rgba(200,200,200,.14) inset}
.pc.grey b{color:#a9a49a}.pc.grey em,.pc.grey span{color:#7d796f}
.pc.grey .y{color:#8b8576}
.pc.grey::after{content:'先行者';position:absolute;right:10px;bottom:9px;font-size:10.5px;letter-spacing:.2em;color:#9a9486;padding:1px 6px;border-radius:2px;box-shadow:0 0 0 1px rgba(200,200,200,.22) inset}
.pc.sel{box-shadow:0 0 0 1.5px var(--gold) inset,0 0 18px rgba(216,180,106,.35);background:linear-gradient(160deg,rgba(54,40,24,.92),rgba(22,15,9,.95))}
.pc.sel b{color:#fff}.pc.sel em,.pc.sel span{color:#e2d6bb}
.pc.sel::after{color:#16110a;background:var(--gold);box-shadow:none}
.side{border-radius:6px;padding:22px 24px;background:linear-gradient(170deg,rgba(28,18,19,.92),rgba(10,7,8,.95));box-shadow:0 0 0 1px rgba(216,180,106,.35) inset,0 20px 40px rgba(0,0,0,.5);align-self:start}
.side h2{font-size:28px;font-weight:600;letter-spacing:.3em;color:#f7e9c6}
.side .tag{display:inline-block;margin-top:8px;font-size:12px;letter-spacing:.2em;padding:2px 9px;border-radius:2px;color:#16110a;background:var(--gold)}
.side .tag.g{color:#d8cfbd;background:none;box-shadow:0 0 0 1px rgba(216,207,189,.35) inset;margin-left:6px}
.side h5{font-weight:400;margin-top:16px;font-size:12px;letter-spacing:.38em;color:#a59c88}
.side p{margin-top:6px;font-size:14px;line-height:1.85;color:#e1d8c6}
.side .cred{margin-top:16px;padding:12px 14px;border-radius:3px;font-size:13px;line-height:1.8;color:#e9dcc0;background:rgba(0,0,0,.35);box-shadow:0 0 0 1px rgba(216,180,106,.25) inset;font-family:Consolas,'Noto Serif SC',monospace}
.btns{display:flex;gap:10px;margin-top:18px}
.bt{flex:1;height:42px;border-radius:21px;display:grid;place-items:center;font-size:14px;letter-spacing:.3em;color:#e9e3d6;box-shadow:0 0 0 1px rgba(239,233,220,.3) inset}
.bt.pri{color:#1b1406;background:linear-gradient(180deg,#f0d491,#c99e4c)}
.gods{grid-template-columns:repeat(6,1fr)}
.gc{position:relative;border-radius:4px;overflow:hidden;background:#111;box-shadow:0 0 0 1px rgba(216,180,106,.45)}
.gc i{display:block;aspect-ratio:2/3;background-size:cover;background-position:center 18%}
.gc b{position:absolute;left:0;right:0;bottom:0;padding:18px 8px 7px;font-size:12.5px;line-height:1.45;letter-spacing:.06em;font-weight:400;text-align:center;color:#f6ecd4;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.88) 45%)}
.gc b small{display:block;font-size:10.5px;color:#c8bca0;letter-spacing:.04em}
.gc.pil{box-shadow:0 0 0 1px rgba(127,224,208,.55)}
.gc.pil::before{content:'七位';position:absolute;left:6px;top:6px;z-index:2;font-size:10px;letter-spacing:.2em;padding:1px 6px;border-radius:2px;color:#0c1a18;background:var(--teal)}
.gc.dead i{filter:grayscale(1) brightness(.38)}
.gc.dead b{opacity:.6}
.gc.dead::after{content:attr(data-d);position:absolute;left:0;right:0;top:42%;text-align:center;font-size:13px;letter-spacing:.2em;color:#efe6d2;text-shadow:0 1px 6px #000}
.gc.sel{box-shadow:0 0 0 2px var(--gold),0 0 22px rgba(216,180,106,.55)}
.star{margin-top:14px;padding:14px 16px;border-radius:4px;background:linear-gradient(160deg,rgba(60,44,18,.55),rgba(20,14,6,.6));box-shadow:0 0 0 1px rgba(216,180,106,.5) inset}
.star b{font-size:18px;letter-spacing:.2em;color:#ffe9b8}
.star b small{font-size:11.5px;letter-spacing:.14em;color:var(--gold);margin-left:8px;font-weight:400}
.star p{margin-top:6px;font-size:13.5px;line-height:1.85;color:#eadfc6}
.know{display:flex;gap:8px;margin-top:12px}
.know span{flex:1;text-align:center;padding:7px 0;border-radius:3px;font-size:13px;letter-spacing:.14em;color:#d8cfbd;box-shadow:0 0 0 1px rgba(216,207,189,.3) inset}
.know span.on{color:#16110a;background:var(--gold);box-shadow:none}
.v-gold{display:none}
body.gold .v-path{display:none}
body.gold .v-gold{display:block}
body.gold .grid.v-gold{display:grid}
body.gold .bg{background-image:url(../小样_纷争纪书/assets/cg/s13_era.webp)}
'''


def page():
    # 命路：照炮的年月 1150 年，1104 年以后有名字的亮着
    order = ['战职', '施法', '圣职', '影系', '射术', '技巧', '规则']
    PER = {'pao': '炮的年月', 'futa': '浮塔的年月', 'tielang': '铁狼的年月', 'haojiao': '号角的年月'}
    cards = []
    for g in order:
        for name, p in TYPES.items():
            if not p['type'].startswith(g):
                continue
            s = SP.get(name, {})
            lit = s.get('from') and s['from'] <= YEAR
            cls = 'pc' + ('' if lit else ' grey') + (' sel' if name == '真理' else '')
            if lit:
                y = '%d年 · 有了路册' % s['from']
            elif name == '沸血':
                y = '约9050年越过长垒'
            elif s.get('from'):
                y = '%d年才有路册' % s['from']
            else:
                y = PER.get(s.get('period'), '纪末才给了位置')
            cards.append('<div class="%s"><b>%s</b><em>%s</em><span>%s</span><i class="y">%s</i></div>'
                         % (cls, esc(name), esc(p['type']), esc(p['short']), esc(y)))
    zl = SP['真理']
    side_path = ('<div class="side v-path"><h2>真理</h2><span class="tag">先行者</span><span class="tag g">施法 · 奥法解析</span>'
                 '<h5>这一年</h5><p>1150年，真理还没有名字，也没有路册。奥法研究所还要再过四十四年才在对炉街开门。</p>'
                 '<h5>根</h5><p>%s。</p><h5>往后</h5><p>%s。</p>'
                 '<h5>你走这一路</h5><p>你是头一批走这一路的人。往后订成路册的时候，头一页记着的人里有你一份。墙上的人照旧叫不出这一路的名字，只说你会那一手。</p>'
                 '<div class="cred">【命路】倾向：真理（先行者）<br>这一年还没有名字，叙述照那时候的叫法写</div>'
                 '<div class="btns"><span class="bt">再看看</span><span class="bt pri">走这一路</span></div></div>'
                 % (esc(zl['root']), esc(zl['when'])))
    gods = []
    for key, name, dom, die, pil in GODS:
        dead = die is not None and die < 3580
        cls = 'gc' + (' dead' if dead else '') + (' sel' if '乌姆拉' in name else '')
        gods.append('<div class="%s"%s><i style="background-image:url(%s)"></i><b>%s<small>%s</small></b></div>'
                    % (cls, (' data-d="%d年南去"' % die) if dead else '', GODIMG % (key + '_01' if pil else key), esc(name), esc(dom)))
    side_gold = ('<div class="side v-gold"><h2>乌姆拉</h2><span class="tag">神亲</span><span class="tag g">朝潮夕汐之主 · 海与潮</span>'
                 '<h5>这一年</h5><p>3580年前后，祂还在。在你出生以前倒下的几位，名字灰着。</p>'
                 '<div class="star"><b>随潮呼吸<small>Legend · Passive · 金血祝颂</small></b>'
                 '<p>血里带着潮。在水里呼吸跟在岸上一样。潮起的那几个钟点，伤口收得快，力气长一截。站在海边，听得出下一回潮什么时候到、带不带风暴。离海越远越弱，进了内陆三天以上，只剩水下能呼吸。</p></div>'
                 '<h5>你知不知道</h5><div class="know"><span class="on">知道是谁的血</span><span>不知道，往后自己认出来</span></div>'
                 '<p style="margin-top:10px;font-size:12.5px;color:#a59c88">叙述和旁人不点破。往后的事归剧透开关，关着。</p>'
                 '<div class="btns"><span class="bt">再看看</span><span class="bt pri">就是这一位</span></div></div>')
    rail = lambda cur, done, opt=(): ''.join('<div class="st %s"><i></i><span>%s</span></div>' % ('done' if i < done else ('cur' if i == cur else ('opt' if s in opt else '')), s) for i, s in enumerate(STEPS))
    return ('<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>样张·建档第二版</title><style>%s</style></head><body>'
            '<div class="bg"></div><div class="vig"></div><div class="wrap">'
            '<nav class="rail"><h4>建档</h4><div class="era v-path">纷争纪 · 炮的年月<small>1150 年 · 自己报的年份</small></div><div class="era v-gold">纷争纪 · 炮的年月<small>3600 年开局 · 你生在 3580 年前后</small></div>'
            '<div class="v-path">%s</div><div class="v-gold">%s</div></nav>'
            '<section class="main"><div class="hd v-path"><small>第七步</small><h1>命路</h1><p>命路这个叫法是 <b>1104 年</b>起的。这一年有名字、有路册的只有渊垒。别的路灰着，也能选，选了你就是那一路的<b>先行者</b>。沸血在魔族营里早就有，选魔族的人这一张是亮的。</p></div>'
            '<div class="hd v-gold"><small>第四步 · 生在这一纪的人才有</small><h1>金血祝颂</h1><p>你的血醒着。神亲只能是你<b>出生那一年还在世</b>的正神，倒下了的照神谱灰着。挑一位，祂的祝福落在血里，是一颗 <b>Legend 的 Passive</b>。</p></div>'
            '<div class="grid paths v-path">%s</div><div class="grid gods v-gold">%s</div></section>%s%s</div>'
            '<script>if(location.hash==="#gold")document.body.classList.add("gold");</script></body></html>'
            % (CSS, rail(6, 6), rail(3, 3, ('金血',)), ''.join(cards), ''.join(gods), side_path, side_gold))


if __name__ == '__main__':
    open(os.path.join(HERE, 'build_v2.html'), 'w', encoding='utf-8', newline='\n').write(page())
    print('写了 build_v2.html')
