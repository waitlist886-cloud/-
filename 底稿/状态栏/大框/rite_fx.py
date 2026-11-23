# 战斗特效加一层（11-22，用户：“现在的战斗特效，我想要更精美一些，最好加一些合适的动态效果来更有沉浸感，比如施法展开的魔法阵，锤击引发震动之类的”）。
# 接在 rite_css（超凡演出）后头，不动它原来的东西，只往起手框和横幅里各添一层：
# - 起手框 .sz-rite 里的 .rt-mc（三圈）：咏唱、祷告、演算这几路是一座展开的魔法阵，三圈一圈一圈转着放大落定，外圈顺着转、里圈逆着转；
#   靠身体的几路（剑、枪、锤、呼吸……）是脚下一圈一圈荡开的气劲。只给 Active、Special，Art 和 Skill 不出。
# - 横幅 .sz-waza 里的 .wz-x（四层）：照横幅底纹那个字分手法。斩是一道斜着划过去的光和一线残光；突是一排横着冲过去的线和尽头一点穿透的光；
#   打是从左边荡开的震波、裂纹，整页手札跟着震一下；射是准星收拢、一道箭光；守是六角的壁一格一格亮起来；咏是法阵炸开、一圈光芒；
#   祷是从上头落下来的一道光柱。第四层认元素：火星、霜、电光、风痕、水纹、碎石、落叶、光、暗。
# 规则那一头（make_rules_frame.py 的「技」「起手」四条）替换串里各添了一个空壳元素，认字的事照旧归 rite_css 的 KINDS。
# 减少动画的设置下全停。Skill 那种细条不出特效。
import sys
import os
import math

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rite_svg as RS
import rite_css as RC
import rite_tier as RT

R = '.rili-markdown-renderer:has(.sz-hud)'
P = R + ' '


def _pts(r, n, rot=0):
    return [(50 + r * math.sin(2 * math.pi * k / n + rot), 50 - r * math.cos(2 * math.pi * k / n + rot)) for k in range(n)]


# ---- 法阵三圈（遮罩，颜色在样式里给）----
# 遮罩的图只在样式头上写一回（--fx-…），各路子的那一包变量里引它，不然五十几条路子一条抄一遍，样式要大二十万字
RAW = {}
RAW['M1'] = RS.svg("<circle cx='50' cy='50' r='48' stroke-width='1.2'/><circle cx='50' cy='50' r='43.5' stroke-width='.8'/>" + RS.ticks(43.5, 48, 48, .7)
            + ''.join("<circle cx='%.1f' cy='%.1f' r='2.2' fill='%%23000'/>" % p for p in _pts(45.8, 6)))
RAW['M2'] = RS.svg("<circle cx='50' cy='50' r='38' stroke-width='.8'/>" + RS.poly(38, 3) + RS.poly(38, 3, math.pi)
            + ''.join("<circle cx='%.1f' cy='%.1f' r='3' stroke-width='1'/>" % p for p in _pts(38, 6)))
RAW['M3'] = RS.svg("<circle cx='50' cy='50' r='27' stroke-width='2.4' stroke-dasharray='2.5 4.2'/><circle cx='50' cy='50' r='21' stroke-width='.8'/>" + RS.poly(21, 4, math.pi / 4)
            + RS.poly(21, 4) + "<circle cx='50' cy='50' r='6' stroke-width='1'/>")
# 气劲两圈
RAW['A1'] = RS.svg("<circle cx='50' cy='50' r='47' stroke-width='2.2'/><circle cx='50' cy='50' r='41' stroke-width='.7'/>")
RAW['A2'] = RS.svg("<circle cx='50' cy='50' r='44' stroke-width='1.4' stroke-dasharray='10 7'/>")
# 横幅上的：法阵合成一张、准星、六角壁、裂纹、电光
RAW['MC'] = RS.svg("<circle cx='50' cy='50' r='47' stroke-width='1.6'/><circle cx='50' cy='50' r='41' stroke-width='.8'/>" + RS.ticks(41, 47, 36, .8) + RS.poly(41, 3) + RS.poly(41, 3, math.pi)
            + "<circle cx='50' cy='50' r='18' stroke-width='1.2' stroke-dasharray='3 3'/>")
RAW['RET'] = RS.svg("<circle cx='50' cy='50' r='44' stroke-width='1.6' stroke-dasharray='52 17'/><circle cx='50' cy='50' r='26' stroke-width='1'/>"
             "<path d='M50 2v18M50 80v18M2 50h18M80 50h18' stroke-width='2'/><circle cx='50' cy='50' r='2.4' fill='%23000'/>")


def _hex(cx, cy, r):
    return "<polygon points='%s'/>" % ' '.join('%.1f,%.1f' % (cx + r * math.cos(math.pi / 3 * k), cy + r * math.sin(math.pi / 3 * k)) for k in range(6))


RAW['HEX'] = RS.svg(''.join(_hex(x, y, 9.6) for x, y in [(15, 9), (15, 26), (30, 0.5), (30, 17.5), (30, 34.5), (0, 0.5), (0, 17.5), (0, 34.5)]), '0 0 30 34')
RAW['CRACK'] = RS.svg("<path d='M4 50L22 44l10 9 16-12 9 6 20-14 8 4 11-9' stroke-width='1.6'/><path d='M22 44l-3-16 9-8M48 41l4-17 10-6M77 33l2-14M32 53l3 15-8 10M57 47l6 16 12 5M85 37l8 12' stroke-width='1.1'/>"
               "<path d='M4 50l12 10 3 14M4 50l9-14-2-12' stroke-width='1.3'/>", '0 0 100 100')
RAW['BOLT'] = RS.svg("<path d='M0 30l14 6-5 9 20 4-7 10 24 3-6 8 22 5-8 7 26 2-5 6 25 6' stroke-width='2.2'/><path d='M29 49l6 14M52 62l10-12M74 74l4 12' stroke-width='1.2'/>", '0 0 100 100')

M1, M2, M3, A1, A2, MC, RET, HEX, CRACK, BOLT = ['var(--fx-%s)' % k.lower() for k in ['M1', 'M2', 'M3', 'A1', 'A2', 'MC', 'RET', 'HEX', 'CRACK', 'BOLT']]
VARS = ['b', 'm', 'a', 'i', 'o']   # 一层五样：底、遮罩、动画、位置、转动的心


def _layer(n, b='none', m='none', a='none', i='0', o='50% 50%'):
    return {'--x%d-b' % n: b, '--x%d-m' % n: m, '--x%d-a' % n: a, '--x%d-i' % n: i, '--x%d-o' % n: o}


def _bundle(*layers):
    d = {}
    for n in (1, 2, 3):
        d.update(_layer(n))
    for l in layers:
        d.update(l)
    return ';'.join('%s:%s' % kv for kv in d.items())


W = 'color-mix(in srgb, var(--wc) 70%, #fff)'
GLY = '40px 50%'   # 横幅左边那个底纹字的心

HAND = {
    # 斩：一道斜着划过去的光，过后留一线残光
    'slash': _bundle(
        _layer(1, b='linear-gradient(112deg, transparent 44%%, %s 48.6%%, #fff 50%%, %s 51.4%%, transparent 56%%)' % (W, W), a='sz-fx-slash .5s cubic-bezier(.2,.8,.2,1) .22s both', i='-40% -30%'),
        _layer(2, b='linear-gradient(112deg, transparent 49.4%%, %s 50%%, transparent 50.6%%)' % W, a='sz-fx-glint 1.8s ease-out .5s both', i='-40% 0'),
        _layer(3, b='linear-gradient(68deg, transparent 47%%, %s 49.6%%, #fff 50%%, transparent 53%%)' % W, a='var(--x3-hi, none)', i='-40% -30%')),
    # 突：一排线横着冲过去，尽头一点十字的光
    'thrust': _bundle(
        _layer(1, b='repeating-linear-gradient(180deg, transparent 0 8px, %s 8px 9px, transparent 9px 21px)' % W, m='linear-gradient(90deg, transparent, #000 35%, #000 65%, transparent)',
               a='sz-fx-rush .42s cubic-bezier(.3,.7,.2,1) .2s both'),
        _layer(2, b='radial-gradient(ellipse 50% 6% at 50% 50%, #fff, transparent 72%), radial-gradient(ellipse 6% 50% at 50% 50%, #fff, transparent 72%), radial-gradient(circle, ' + W + ' 0, transparent 34%)',
               a='sz-fx-spark .55s ease-out .5s both', i='calc(50% - 60px) 6% auto auto', o='50% 50%')),
    # 打：震波从左边荡开，裂纹炸出来慢慢暗下去
    'smash': _bundle(
        _layer(1, b='radial-gradient(circle, transparent 52%%, %s 57%%, #fff 60%%, transparent 66%%)' % W, a='sz-fx-shock .65s cubic-bezier(.1,.7,.3,1) .26s both', i='calc(50% - 170px) auto auto -130px'),
        _layer(2, b=W, m=CRACK + ' left center/78% 220% no-repeat', a='sz-fx-crack 2.6s ease-out .3s both'),
        _layer(3, b='radial-gradient(circle, transparent 56%%, %s 60%%, transparent 66%%)' % W, a='sz-fx-shock .8s cubic-bezier(.1,.7,.3,1) .42s both', i='calc(50% - 170px) auto auto -130px')),
    # 射：准星转着收拢，一道箭光过去，尽头一点光
    'shoot': _bundle(
        _layer(1, b=W, m=RET + ' center/contain no-repeat', a='sz-fx-lock .6s cubic-bezier(.2,.8,.2,1) .12s both', i='calc(50% - 46px) auto auto -6px'),
        _layer(2, b='linear-gradient(90deg, transparent, %s 55%%, #fff 92%%, transparent)' % W, a='sz-fx-arrow .3s cubic-bezier(.5,0,.2,1) .62s both', i='calc(50% - 1px) 0 auto 0'),
        _layer(3, b='radial-gradient(ellipse 50% 6% at 50% 50%, #fff, transparent 72%), radial-gradient(ellipse 6% 50% at 50% 50%, #fff, transparent 72%)', a='sz-fx-spark .5s ease-out .84s both',
               i='calc(50% - 50px) 5% auto auto')),
    # 守：六角的壁从左往右一格一格亮起来，一圈光荡开
    'guard': _bundle(
        _layer(1, b=W, m=HEX + ' 0 0/30px 34px', a='sz-fx-hex 1.6s ease-out .2s both'),
        _layer(2, b='radial-gradient(circle, transparent 54%%, %s 58%%, transparent 64%%)' % W, a='sz-fx-shock 1s ease-out .25s both', i='calc(50% - 170px) auto auto -130px')),
    # 咏：法阵在底纹字那里炸开、慢慢转，一圈光芒
    'magic': _bundle(
        _layer(1, b=W, m=MC + ' center/contain no-repeat', a='sz-fx-burst .9s cubic-bezier(.2,.8,.2,1) .2s both, sz-rt-spin 30s linear 1.1s infinite', i='calc(50% - 75px) auto auto -35px'),
        _layer(2, b='repeating-conic-gradient(from 0deg at 40px 50%%, color-mix(in srgb, var(--wc) 46%%, transparent) 0 3deg, transparent 3deg 18deg)', m='radial-gradient(circle at 40px 50%, #000 0, transparent 62%)',
               a='sz-fx-rays 1.2s ease-out .3s both', o=GLY)),
    # 祷：一道光柱从上头落下来，光点往上飘
    'pray': _bundle(
        _layer(1, b='linear-gradient(180deg, #fff, %s 30%%, transparent 96%%)' % W, m='linear-gradient(90deg, transparent, #000 30%, #000 70%, transparent)', a='sz-fx-pillar 1.5s ease-out .2s both',
               i='0 auto 0 8px', o='50% 0'),
        _layer(2, b='radial-gradient(circle at 20%% 80%%, %s 0 1.2px, transparent 2px), radial-gradient(circle at 70%% 30%%, #fff 0 1px, transparent 1.8px), radial-gradient(circle at 45%% 55%%, %s 0 1px, transparent 1.8px)' % (W, W),
               a='sz-fx-rise 3.2s linear infinite', i='0 auto 0 0')),
    # 龙：一声吼，两圈震波
    'roar': _bundle(
        _layer(1, b='radial-gradient(circle, transparent 52%%, %s 57%%, transparent 64%%)' % W, a='sz-fx-shock .8s ease-out .2s both', i='calc(50% - 170px) auto auto -130px'),
        _layer(3, b='radial-gradient(circle, transparent 56%%, %s 60%%, transparent 66%%)' % W, a='sz-fx-shock 1s ease-out .4s both', i='calc(50% - 170px) auto auto -130px')),
    'none': _bundle(),
}
S340, AUTO = ('340px', '340px'), 'auto'
SIZE = {'thrust': {2: ('120px', '120px')}, 'smash': {1: S340, 3: S340}, 'shoot': {1: ('92px', '92px'), 2: (AUTO, '2px'), 3: ('100px', '100px')}, 'guard': {2: S340}, 'magic': {1: ('150px', '150px')},
        'pray': {1: ('64px', AUTO), 2: ('120px', AUTO)}, 'roar': {1: S340, 3: S340}}
# 横幅底纹字 → 手法
KJ = {'斩': 'slash', '影': 'slash', '阵': 'slash', '舞': 'slash', '突': 'thrust', '梭': 'thrust', '打': 'smash', '破': 'smash', '锤': 'smash', '熔': 'smash',
      '射': 'shoot', '弦': 'shoot', '猎': 'shoot', '铳': 'shoot', '守': 'guard', '垒': 'guard',
      '咏': 'magic', '术': 'magic', '曜': 'magic', '环': 'magic', '思': 'magic', '流': 'magic', '理': 'magic', '匣': 'magic', '解': 'magic', '念': 'magic', '辉': 'magic',
      '祷': 'pray', '迹': 'pray', '言': 'pray', '歌': 'pray', '悯': 'pray', '龙': 'roar'}
# 起手框里那三圈：演法 → 法阵还是气劲
RITE_MODE = {'verse': 'circle', 'pray': 'circle', 'calc': 'circle', 'oath': 'circle', 'body': 'aura', 'shadow': 'aura', 'feast': 'none'}
MC_CIRCLE = ('--mc-d:block;--mc-tf:none;--mc-s:230px;--m1:%s;--m2:%s;--m3:%s;'
             '--m1-a:sz-fx-unfold .95s cubic-bezier(.2,.85,.25,1) .1s both, sz-rt-spin 46s linear 1.05s infinite;'
             '--m2-a:sz-fx-unfold2 1s cubic-bezier(.2,.85,.25,1) .26s both, sz-fx-spinr 34s linear 1.26s infinite;'
             '--m3-a:sz-fx-unfold .8s cubic-bezier(.2,.85,.25,1) .46s both, sz-fx-throb 2.6s ease-in-out 1.3s infinite;--m1-o:.5;--m2-o:.42;--m3-o:.7') % (M1, M2, M3)
MC_AURA = ('--mc-d:block;--mc-tf:translateY(34px) rotateX(68deg);--mc-s:210px;--m1:%s;--m2:%s;--m3:none;'
           '--m1-a:sz-fx-ripple 2.4s cubic-bezier(.2,.7,.3,1) .2s infinite;--m2-a:sz-fx-ripple 2.4s cubic-bezier(.2,.7,.3,1) 1.4s infinite;--m3-a:none;--m1-o:.8;--m2-o:.7;--m3-o:0') % (A1, A2)
MC_NONE = '--mc-d:none'

# 第四层：元素。认 data-k 里「·」后头那个字（跟 rite_css 的 ELEM 一样认）
D = lambda c, x, y, r=1.4: 'radial-gradient(circle at %s%% %s%%, %s 0 %spx, transparent %spx)' % (x, y, c, r, r + .9)
ELEM_FX = [
    ('火|炎|焰|灼|熔', dict(b=', '.join([D('#ffd08a', 12, 80), D('#ff9a52', 34, 40, 1.8), D('#ffe2a8', 58, 90), D('#ff7a45', 76, 55, 1.6), D('#ffd08a', 90, 20)]) + ';background-size:140px 90px',
                       m='linear-gradient(0deg, #000 20%, transparent)', a='sz-fx-ember 2.4s linear infinite')),
    ('水|潮|浪|海', dict(b='repeating-radial-gradient(circle at 18% 130%, transparent 0 16px, rgb(140 205 255 / .34) 16px 17.5px, transparent 17.5px 30px)', a='sz-fx-ripple2 2.8s ease-out .2s infinite')),
    ('冰|霜|雪|寒', dict(b='linear-gradient(125deg, rgb(215 245 255 / .7), transparent 20%), linear-gradient(305deg, rgb(215 245 255 / .6), transparent 18%), '
                        'repeating-linear-gradient(60deg, transparent 0 7px, rgb(215 245 255 / .28) 7px 8px), repeating-linear-gradient(120deg, transparent 0 9px, rgb(215 245 255 / .22) 9px 10px)',
                       m='linear-gradient(90deg, #000, transparent 24%, transparent 76%, #000)', a='sz-fx-frost 1.4s ease-out .3s both')),
    ('雷|电|霆', dict(b='linear-gradient(90deg, #fff, #d9c2ff)', m=BOLT + ' center/100% 100% no-repeat', a='sz-fx-bolt 1.1s linear .28s both')),
    ('土|岩|石|地|砂', dict(b=', '.join(['linear-gradient(#cdb48a, #cdb48a) 12% 0/5px 5px no-repeat', 'linear-gradient(#b89a6a, #b89a6a) 38% 0/7px 6px no-repeat', 'linear-gradient(#d8c39c, #d8c39c) 63% 0/4px 4px no-repeat',
                                    'linear-gradient(#b89a6a, #b89a6a) 84% 0/6px 5px no-repeat']), a='sz-fx-debris .9s cubic-bezier(.3,0,.6,1) .34s both')),
    ('风|岚|气', dict(b='repeating-linear-gradient(174deg, transparent 0 13px, rgb(190 255 232 / .4) 13px 14px, transparent 14px 31px)', m='linear-gradient(90deg, transparent, #000 40%, #000 60%, transparent)',
                    a='sz-fx-rush 1.1s ease-in-out .2s infinite')),
    ('草|木|叶|藤|生|花', dict(b=', '.join([D('#a5e38a', 15, 20, 2), D('#7dcf6a', 42, 70, 2.4), D('#c8f0a8', 66, 30, 1.8), D('#7dcf6a', 88, 80, 2.2)]) + ';background-size:150px 70px', a='sz-fx-leaf 3.6s linear infinite')),
    ('光|圣|辉|晨|曦|日', dict(b='repeating-conic-gradient(from -20deg at 100% 0, rgb(255 236 170 / .4) 0 2.5deg, transparent 2.5deg 11deg)', m='radial-gradient(circle at 100% 0, #000, transparent 70%)',
                           a='sz-fx-throb 2.8s ease-in-out infinite')),
    ('暗|影|夜|冥|蚀', dict(b='radial-gradient(ellipse at 50% 50%, transparent 30%, rgb(40 16 80 / .6) 100%)', a='sz-fx-throb 3.2s ease-in-out infinite')),
]

KEYFRAMES = '''@keyframes sz-fx-unfold{0%{opacity:0;transform:scale(.12) rotate(-150deg)}55%{opacity:var(--o, .5);transform:scale(1.08) rotate(8deg)}100%{opacity:var(--o, .5);transform:none}}
@keyframes sz-fx-unfold2{0%{opacity:0;transform:scale(.12) rotate(150deg)}55%{opacity:var(--o, .5);transform:scale(1.08) rotate(-8deg)}100%{opacity:var(--o, .5);transform:none}}
@keyframes sz-fx-spinr{to{transform:rotate(-360deg)}}
@keyframes sz-fx-throb{0%,100%{opacity:var(--o, .7)}50%{opacity:calc(var(--o, .7) * .45)}}
@keyframes sz-fx-ripple{0%{opacity:0;transform:scale(.25)}18%{opacity:var(--o, .8)}100%{opacity:0;transform:scale(1.15)}}
@keyframes sz-fx-slash{0%{opacity:0;transform:translateX(-62%)}22%{opacity:1}78%{opacity:1}100%{opacity:0;transform:translateX(62%)}}
@keyframes sz-fx-glint{0%{opacity:0;transform:scaleX(.3)}12%{opacity:.95;transform:scaleX(1)}100%{opacity:0;transform:scaleX(1.04)}}
@keyframes sz-fx-rush{0%{opacity:0;transform:translateX(-70%)}25%{opacity:.95}75%{opacity:.8}100%{opacity:0;transform:translateX(70%)}}
@keyframes sz-fx-spark{0%{opacity:0;transform:scale(.15) rotate(0)}30%{opacity:1}100%{opacity:0;transform:scale(1.5) rotate(30deg)}}
@keyframes sz-fx-shock{0%{opacity:0;transform:scale(.08)}14%{opacity:1}100%{opacity:0;transform:scale(1.7)}}
@keyframes sz-fx-crack{0%{opacity:0;clip-path:circle(0 at 40px 50%)}9%{opacity:1;clip-path:circle(130% at 40px 50%)}30%{opacity:.85}100%{opacity:0;clip-path:circle(130% at 40px 50%)}}
@keyframes sz-fx-lock{0%{opacity:0;transform:scale(2.4) rotate(120deg)}60%{opacity:1;transform:scale(.94) rotate(-6deg)}80%{opacity:1;transform:none}100%{opacity:.4;transform:none}}
@keyframes sz-fx-arrow{0%{opacity:0;transform:translateX(-100%)}15%{opacity:1}85%{opacity:1}100%{opacity:0;transform:translateX(100%)}}
@keyframes sz-fx-hex{0%{opacity:0;clip-path:inset(0 100% 0 0)}45%{opacity:.6;clip-path:inset(0 0 0 0)}100%{opacity:.16;clip-path:inset(0 0 0 0)}}
@keyframes sz-fx-burst{0%{opacity:0;transform:scale(.3) rotate(-120deg)}45%{opacity:.95;transform:scale(1.3) rotate(20deg)}100%{opacity:.26;transform:none}}
@keyframes sz-fx-rays{0%{opacity:0;transform:rotate(-14deg) scale(.6)}30%{opacity:.8}100%{opacity:0;transform:rotate(22deg) scale(1.15)}}
@keyframes sz-fx-pillar{0%{opacity:0;transform:scaleY(0)}30%{opacity:.9;transform:scaleY(1)}100%{opacity:.28;transform:scaleY(1)}}
@keyframes sz-fx-rise{0%{opacity:0;background-position:0 40px, 30px 60px, 60px 20px}15%{opacity:.9}85%{opacity:.9}100%{opacity:0;background-position:0 -40px, 30px -30px, 60px -70px}}
@keyframes sz-fx-ember{0%{opacity:0;background-position:0 30px}15%{opacity:.9}100%{opacity:0;background-position:-24px -60px}}
@keyframes sz-fx-ripple2{0%{opacity:0;transform:scale(.6)}25%{opacity:.9}100%{opacity:0;transform:scale(1.25)}}
@keyframes sz-fx-frost{0%{opacity:0;clip-path:inset(0 46% 0 46%)}100%{opacity:.9;clip-path:inset(0 0 0 0)}}
@keyframes sz-fx-bolt{0%{opacity:0}4%{opacity:1}9%{opacity:.15}14%{opacity:1}24%{opacity:.2}30%{opacity:.9}100%{opacity:0}}
@keyframes sz-fx-debris{0%{opacity:0;background-position:12% 70%, 38% 80%, 63% 75%, 84% 85%}20%{opacity:1;background-position:10% 8%, 40% 0%, 61% 14%, 87% 4%}100%{opacity:0;background-position:8% 110%, 43% 120%, 59% 115%, 90% 125%}}
@keyframes sz-fx-leaf{0%{opacity:0;background-position:0 -20px}15%{opacity:.85}85%{opacity:.85}100%{opacity:0;background-position:-60px 70px}}
@keyframes sz-fx-quake{0%,100%{transform:none}8%{transform:translate(-5px,3px)}18%{transform:translate(5px,-3px)}30%{transform:translate(-4px,-2px)}44%{transform:translate(3px,2px)}60%{transform:translate(-2px,1px)}78%{transform:translate(1px,-1px)}}
@keyframes sz-fx-quake2{0%,100%{transform:none}6%{transform:translate(-9px,5px) rotate(-.25deg)}15%{transform:translate(8px,-5px) rotate(.2deg)}26%{transform:translate(-7px,-3px)}38%{transform:translate(6px,3px)}52%{transform:translate(-4px,2px)}68%{transform:translate(3px,-1px)}84%{transform:translate(-1px,1px)}}'''


def _ksel(keys):
    return ','.join('[data-k*="%s"]' % k for k in keys)


def css():
    out = ['/* ==== 11-22 战斗特效加一层（rite_fx.py）：起手框里展开的法阵和气劲，横幅上照手法分的斩、突、打、射、守、咏、祷，元素一层，重击震一下 ==== */', KEYFRAMES]
    w = out.append
    AS = ':is(%s,%s)' % (RT.ACTIVE, RT.SPECIAL)
    w(R + '{' + ';'.join('--fx-%s:%s' % (k.lower(), v) for k, v in RAW.items()) + '}')
    # 起手框里的三圈
    w(P + '.rt-mc{display:none;position:absolute;left:54px;top:50%;z-index:0;width:0;height:0;pointer-events:none;transform:var(--mc-tf, none);filter:drop-shadow(0 0 5px color-mix(in srgb, var(--rc) 70%, transparent))}')
    w(P + '.sz-rite' + AS + ' .rt-mc{display:var(--mc-d, none)}')
    w(P + '.rt-mc i{position:absolute;left:calc(var(--mc-s, 230px) / -2);top:calc(var(--mc-s, 230px) / -2);width:var(--mc-s, 230px);height:var(--mc-s, 230px);opacity:0;'
          'background:color-mix(in srgb, var(--rc) 82%, #fff);-webkit-mask:var(--m) center/contain no-repeat;mask:var(--m) center/contain no-repeat}')
    for k in (1, 2, 3):
        w(P + '.rt-mc .m%d{--m:var(--m%d, none);--o:var(--m%d-o, .5);animation:var(--m%d-a, none)}' % (k, k, k, k))
    w(P + '.rt-mc .m2{width:calc(var(--mc-s, 230px) * .86);height:calc(var(--mc-s, 230px) * .86);left:calc(var(--mc-s, 230px) * -.43);top:calc(var(--mc-s, 230px) * -.43)}')
    w(P + '.rt-mc .m3{width:calc(var(--mc-s, 230px) * .9);height:calc(var(--mc-s, 230px) * .9);left:calc(var(--mc-s, 230px) * -.45);top:calc(var(--mc-s, 230px) * -.45)}')
    w(P + '.sz-rite' + RT.SPECIAL + '{--mc-k:1.22}')
    w(P + '.sz-rite' + RT.SPECIAL + ' .rt-mc{scale:1.22}')
    w(P + '.sz-rite' + RT.HIGH + ' .rt-mc{filter:drop-shadow(0 0 9px color-mix(in srgb, var(--qc, var(--rc)) 80%, transparent)) drop-shadow(0 0 2px #fff)}')
    # 横幅上的四层
    w(P + '.wz-x{display:none;position:absolute;inset:0;z-index:0;pointer-events:none}')
    w(P + '.sz-waza' + AS + ' .wz-x{display:block}')
    w(P + '.wz-x i{position:absolute;display:block;opacity:0;pointer-events:none}')
    for k in (1, 2, 3, 4):
        w(P + '.wz-x .x%d{inset:var(--x%d-i, 0);background:var(--x%d-b, none);-webkit-mask:var(--x%d-m, none);mask:var(--x%d-m, none);animation:var(--x%d-a, none);transform-origin:var(--x%d-o, 50%% 50%%);'
              'width:var(--x%d-w, auto);height:var(--x%d-h, auto)}' % ((k,) * 9))
    w(P + '.sz-waza :is(.wz-who,.wz-n,.wz-k,.wz-d){position:relative;z-index:1}')
    # 高位阶：斩多一道交叉的；别的层亮一点
    w(P + '.sz-waza' + RT.HIGH + '{--x3-hi:sz-fx-slash .5s cubic-bezier(.2,.8,.2,1) .4s both}')
    # 路子：照 rite_css 的 KINDS 一条一条排（后写的盖先写的）
    for keys, motif, label, col, kj, anim, fam in RC.KINDS:
        sel = _ksel(keys)
        mode = RITE_MODE.get(fam, 'none')
        w('%s .sz-rite:is(%s){%s}' % (R, sel, {'circle': MC_CIRCLE, 'aura': MC_AURA, 'none': MC_NONE}[mode]))
        hand = KJ.get(kj, 'none')
        size = ''.join(';--x%d-w:%s;--x%d-h:%s' % ((n,) + (SIZE.get(hand, {}).get(n) or (AUTO, AUTO))[:1] + (n,) + (SIZE.get(hand, {}).get(n) or (AUTO, AUTO))[1:]) for n in (1, 2, 3))
        w('%s .sz-waza:is(%s){%s%s}' % (R, sel, HAND[hand], size))
    # 元素那一层
    for keys, d in ELEM_FX:
        sel = ','.join('[data-k*="·%s"]' % k for k in keys.split('|'))
        b = d['b']
        size = ''
        if ';background-size:' in b:
            b, size = b.split(';background-size:')
        w('%s .sz-waza:is(%s){--x4-b:%s;--x4-m:%s;--x4-a:%s}' % (R, sel, b, d.get('m', 'none'), d['a']))
        if size:
            w('%s .sz-waza:is(%s) .wz-x .x4{background-size:%s}' % (R, sel, size))
    # 重击：整页手札震一下（Active、Special 才震；高位阶震得狠一点）。龙吼轻震
    smash = [k for keys, _, _, _, kj, _, _ in RC.KINDS if KJ.get(kj) == 'smash' for k in keys]
    roar = [k for keys, _, _, _, kj, _, _ in RC.KINDS if KJ.get(kj) == 'roar' for k in keys]
    w('%s .sz-page.sz-prose:has(.sz-waza%s:is(%s)){animation:sz-fx-quake .55s linear .3s 1 both}' % (R, AS, _ksel(smash + roar)))
    w('%s .sz-page.sz-prose:has(.sz-waza%s%s:is(%s)){animation:sz-fx-quake2 .7s linear .3s 1 both}' % (R, AS, RT.HIGH, _ksel(smash)))
    w('@media (max-width:639px){' + P + '.rt-mc{left:41px;scale:.82}}')
    w('@media (prefers-reduced-motion:reduce){' + P + ':is(.rt-mc,.wz-x){display:none!important}' + P + '.sz-page.sz-prose{animation:none!important}}')
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    print(len(css()))
