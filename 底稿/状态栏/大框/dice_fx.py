# 命运骰先掷、掷骰的骰盘、等待那几秒的包装（11-27，备注_命运骰与等待_11-27.md）。用户原话：
#   “现在卡内每次我发送输入的时候，模型收到了我的输入后会先有一个输出框，然后开始思考过程，然后再输出内容。我想做的：
#    1. 包装一下这个还没有开始正式输出的思考过程，类似命运的丝线正在编织之类的
#    2. 在一切任何推演底座与输出开始之前，先掷下随机的命运骰作为后续检定的判定，比如第一个检定就用第一个命运骰的结果，第二个用第二个。
#    3. 单独给命运骰做一个掷出的美化”
#
# 记录：§环境 下一行一行 `§骰｜a b c d e f`（六颗，照平台这一轮抽给模型的「本轮第一颗命运骰：n」到第六颗原样抄）。§底座 前头不放 § 行，
#   显示层一大串规则认的是「§底座 前头没有别的 § 行」；§骰 紧跟 §环境，流式输出时底座、环境两行一过就是它，看着就是先掷骰。
# 规则三条（TRAY_RULES 两条排在 make_rules_frame.py「三条·没有」后头、「推演九行」前头；LIT_RULES 一条排在检定演出那一组后头）：
#   骰盘      往后看 §骰 那一行，在 <details class="sz-hud"> 前头放一块骰盘：六颗二十面骰（图是检定面板那一套 --jg-die，一纪一套），
#             下头一排小字 一 到 六。顺手放一段 <style>：「后写的盖先写的」，页上挂着的几条回复里只有最靠后的那一条骰盘 --dz-skip 是 0，
#             别的都是 -60s（动画的延迟拨到负六十秒，挂上去就是落定的样子），这就是“只有最新一条掷，旧的只摆结果”。风月的回复里不能带
#             <style>，fy_shell_rules 拿掉它，风月那边照「最后一对问答是外壳的直接内容」认最新（fy_css）。
#   骰·收     §骰 那一行拿掉（功能轮、写歪了没认出骰盘的也拿掉，不落到「记录兜底」上）。
#   骰·用到   检定面板（§判，judge_fx.py）写了第几颗的，面板上挂 data-dk="二"（或 2），样式照它把骰盘上那一颗点亮、别的压暗。
#             同一条回复里用 .rili-markdown-renderer:has(.sz-judge[data-dk=…]) 认，主语就是这一条回复，不挂祖先。
# 等待：日里那一份写进 platform_chrome.css（卡的样式格里，介绍页、头一条回复以前也在），风月那一份接在 fy_shell_css.build 末尾。
#   python -I -X utf8 dice_fx.py            印三条规则的量词数
#   python -I -X utf8 dice_fx.py --chrome   把日里等待那一段写回 platform_chrome.css（两行记号之间）
import os
import re
import sys
from urllib.parse import quote

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
R = '.rili-markdown-renderer:has(.sz-hud)'
REND = '.rili-markdown-renderer'
NUM = '一二三四五六'

# ---------------- 规则 ----------------
# 数与数之间：空格、顿号、逗号都认；模型写成「第1颗 7」的，「第1颗」整个当隔开的字
SEP = r'(?:第[1-6]颗|[^\d\n]){1,10}'
LEAD = r'(?:第[1-6]颗|[^\d\n]){0,12}'
D = r'(\d{1,2})'
STAMP = '$2-$3-$4-$5-$6-$7'
_DIE = '<i class="dz dz%d" data-v="$%d"><i class="dz-r"><i class="dz-f"></i><b>$%d</b></i><small>%s</small></i>'
TRAY = ('<div class="sz-dice" data-s="%s"><style>.sz-dice.sz-dice{--dz-skip:-60s}.sz-dice[data-s="%s"]{--dz-skip:0s}</style>'
        '<span class="dz-hd"><b>命运骰</b></span><span class="dz-row">%s</span></div>$1'
        % (STAMP, STAMP, ''.join(_DIE % (k + 1, k + 2, k + 2, NUM[k]) for k in range(6))))
TRAY_RULES = [
    ('骰盘', '/(<details class="sz-hud">)(?=[\\s\\S]{0,6000}\\n§骰｜' + LEAD + D + ''.join('(?:' + SEP + D + '|)' for _ in range(5)) + ')/', TRAY),
    ('骰·收', '/^§骰｜[^\\n]*\\n?/gm', ''),
]
LIT_RULES = [
    ('骰·用到', '/(<div class="sz-judge(?: jg-s|)")(?=[^\\n]{0,9000}<span class="jg-dn"><em>[^<\\n]{0,10}第([一二三四五六1-6])颗)/g', '$1 data-dk="$2"'),
]
RULES = TRAY_RULES + LIT_RULES


def check():
    import judge_fx
    saved = judge_fx.RULES
    judge_fx.RULES = RULES
    try:
        return judge_fx.check()
    finally:
        judge_fx.RULES = saved


# ---------------- 骰盘的样式（进 frame.css，风月照 fy_shell_css 换选择器） ----------------
def _svg(body, vb):
    s = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='%s'>%s</svg>" % (vb, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' -.,()")


# 没有图的时候（图床取不到）垫底的一颗：正二十面体正面看过去是一个六边形，中间一个朝上的三角，六个角各连到三角上
_HEX = '50,6 88,28 88,72 50,94 12,72 12,28'
_TRI = '50,22 76,66 24,66'
D20 = _svg("<polygon points='%s' fill='rgb(30,28,70)' fill-opacity='.92' stroke='rgb(214,178,106)' stroke-width='3'/>"
           "<polygon points='%s' fill='rgb(255,255,255)' fill-opacity='.08' stroke='rgb(214,178,106)' stroke-width='2'/>"
           "<g stroke='rgb(214,178,106)' stroke-width='1.6' stroke-opacity='.8'><path d='M50 6L50 22M88 28L76 66M12 28L24 66M50 94L76 66M50 94L24 66M88 72L76 66M12 72L24 66M88 28L50 22M12 28L50 22'/></g>" % (_HEX, _TRI),
           '0 0 100 100')

CSS = r'''
/* ==== 11-27 命运骰先掷（dice_fx.py）：回复最上头一块骰盘，六颗二十面骰；最新一条掷出来，旧的只摆结果；§判 用到哪一颗哪一颗亮 ==== */
@R@ .sz-dice{position:relative;display:flex;align-items:center;justify-content:center;gap:10px;max-width:560px;margin:0 auto 12px;padding:2px 0 0;font-style:normal}
@R@ .sz-dice>style{display:none}
/* 回复那一层有了手札以后是三行的格子（history_far：推演、页、页签各占一行），骰盘不在那三行里，自动排就落到页签后头。
   写成「止于第 1 条线、跨一行」，格子会在最前头添一行给它，不用认别的东西 */
:is(@R@,@R@ *):has(> .sz-page.sz-prose)>.sz-dice{grid-row:span 1 / 1}
@R@ .sz-dice::before,@R@ .sz-dice::after{content:"";flex:1 1 0;min-width:14px;height:1px;background:linear-gradient(90deg, transparent, var(--fm-line, rgb(214 178 106 / .32)))}
@R@ .sz-dice::after{background:linear-gradient(270deg, transparent, var(--fm-line, rgb(214 178 106 / .32)))}
@R@ .dz-hd{flex:none;display:flex;align-items:center;writing-mode:vertical-rl;padding:2px 0 12px;font-family:var(--fm-serif);font-size:11.5px;line-height:1;letter-spacing:.32em;color:var(--fm-ink2)}
@R@ .dz-hd b{font-weight:600!important;color:inherit!important}
@R@ .dz-row{flex:none;display:flex;align-items:flex-start;gap:7px;perspective:420px}
/* 一颗：上头是滚的那一块（骰面加点数，图是检定面板那一套，一纪一套），下头一个小字 一 到 六，落定了才出来。
   滚只动 transform，点亮用 translate、scale 两个单独的属性，压暗用 filter，互不相盖 */
@R@ .dz{position:relative;display:grid;justify-items:center;width:46px;font-style:normal;transition:filter .35s ease}
@R@ .dz2{--dz-d:.34s}@R@ .dz3{--dz-d:.58s}@R@ .dz4{--dz-d:.82s}@R@ .dz5{--dz-d:1.06s}@R@ .dz6{--dz-d:1.3s}
@R@ .dz[data-v=""]{display:none}
@R@ .dz-r{position:relative;isolation:isolate;display:block;font-style:normal;width:46px;height:46px;transform-origin:50% 50%;
  animation:sz-dz-roll .85s cubic-bezier(.2,.75,.3,1) calc(var(--dz-skip, -60s) + var(--dz-d, .1s)) both;transition:translate .35s ease, scale .35s ease}
@R@ .dz-f{position:absolute;inset:0;display:block;background:var(--jg-die, none) center/contain no-repeat, @D20@ center/88% no-repeat;
  filter:drop-shadow(0 3px 4px rgb(0 0 0 / .45));
  animation:sz-dz-tumble .85s cubic-bezier(.12,.62,.25,1) calc(var(--dz-skip, -60s) + var(--dz-d, .1s)) both}
@R@ .dz-r>b{position:absolute;left:0;right:0;top:54%;transform:translateY(-50%);text-align:center;font-family:var(--fm-serif);font-size:17px!important;font-weight:800!important;line-height:1;
  font-variant-numeric:lining-nums tabular-nums;letter-spacing:-.03em;color:var(--jg-num, #fff4cf)!important;text-shadow:var(--jg-nsh, 0 1px 2px #000);pointer-events:none;
  animation:sz-dz-pop .3s cubic-bezier(.2,1.6,.4,1) calc(var(--dz-skip, -60s) + var(--dz-d, .1s) + .78s) both}
/* 滚的时候骰面上一串数乱跳，落定那一下换成真的 */
@R@ .dz-r::after{content:"";position:absolute;left:0;right:0;top:54%;transform:translateY(-50%);text-align:center;font-family:var(--fm-serif);font-size:15px;font-weight:700;line-height:1;
  color:var(--jg-num, #fff4cf);opacity:.85;pointer-events:none;
  animation:sz-dz-flick .78s steps(1, end) calc(var(--dz-skip, -60s) + var(--dz-d, .1s)) both, sz-dz-hide .1s linear calc(var(--dz-skip, -60s) + var(--dz-d, .1s) + .72s) both}
@R@ .dz>small{display:block;margin-top:3px;font-size:10px;line-height:12px;letter-spacing:.1em;color:var(--fm-ink2);opacity:.75;
  animation:sz-dz-label .3s ease-out calc(var(--dz-skip, -60s) + var(--dz-d, .1s) + .75s) both}
/* 二十：骰面后头一圈金光、一圈光芒，数发光 */
@R@ .dz[data-v="20"] .dz-f{filter:drop-shadow(0 0 6px #ffd36e) drop-shadow(0 0 2px #fff3c4)}
@R@ .dz[data-v="20"] .dz-r>b{color:#fff8dc!important;text-shadow:0 0 10px #ffd36e, 0 0 4px #fff6d0, 0 1px 2px #3a2400}
@R@ .dz[data-v="20"] .dz-r::before{content:"";position:absolute;left:50%;top:50%;width:84px;height:84px;margin:-42px 0 0 -42px;z-index:-1;border-radius:50%;pointer-events:none;
  background:radial-gradient(closest-side, rgb(255 236 170 / .85), rgb(255 210 110 / .35) 45%, transparent 72%), repeating-conic-gradient(from 0deg, rgb(255 214 120 / .55) 0 5deg, transparent 5deg 24deg);
  -webkit-mask:radial-gradient(closest-side, #000 35%, transparent 98%);mask:radial-gradient(closest-side, #000 35%, transparent 98%);
  animation:sz-dz-halo 1.1s ease-out calc(var(--dz-skip, -60s) + var(--dz-d, .1s) + .8s) both}
@R@ .dz[data-v="20"]>small{color:#ffd98a;opacity:1}
/* 一：落定那一下骰面裂开（检定面板那一套裂开的图），暗红，抖一下 */
@R@ .dz:is([data-v="1"],[data-v="01"]) .dz-f::after{content:"";position:absolute;inset:0;background:var(--jg-crk, none) center/contain no-repeat;opacity:0;
  animation:sz-dz-show .08s linear calc(var(--dz-skip, -60s) + var(--dz-d, .1s) + .8s) both}
@R@ .dz:is([data-v="1"],[data-v="01"]) .dz-f{filter:drop-shadow(0 0 6px rgb(200 30 20 / .85)) drop-shadow(0 2px 3px rgb(0 0 0 / .6)) saturate(.7) brightness(.82);
  animation:sz-dz-tumble .85s cubic-bezier(.12,.62,.25,1) calc(var(--dz-skip, -60s) + var(--dz-d, .1s)) both, sz-dz-shake .4s linear calc(var(--dz-skip, -60s) + var(--dz-d, .1s) + .8s) both}
@R@ .dz:is([data-v="1"],[data-v="01"]) .dz-r>b{color:var(--jg-n1, #ffc4b8)!important;text-shadow:var(--jg-n1s, 0 0 8px #d8281c, 0 1px 2px #000)}
@R@ .dz:is([data-v="1"],[data-v="01"])>small{color:#e0685a;opacity:1}
/* §判 用到的那一颗：抬起来、亮一圈，下头的小字换成金的、底下一颗金点（横线会把“一”看成“二”）；同一条回复里有用到的，别的几颗压暗一点 */
@R@:has(.sz-judge[data-dk]) .dz{filter:brightness(.6) saturate(.5)}
@LIT@{filter:none}
@LITR@{translate:0 -4px;scale:1.1}
@LITF@{filter:drop-shadow(0 0 5px var(--fm-glow, #f0d48c)) drop-shadow(0 0 2px #fff6d0) drop-shadow(0 3px 4px rgb(0 0 0 / .45));
  animation:sz-dz-tumble .85s cubic-bezier(.12,.62,.25,1) calc(var(--dz-skip, -60s) + var(--dz-d, .1s)) both, sz-dz-glow 1.1s ease-out calc(var(--dz-skip, -60s) + 1.6s) both}
@LITF1@{filter:drop-shadow(0 0 7px rgb(220 40 28 / .95)) drop-shadow(0 0 2px #ffd0c4) drop-shadow(0 3px 4px rgb(0 0 0 / .6)) saturate(.8);
  animation:sz-dz-tumble .85s cubic-bezier(.12,.62,.25,1) calc(var(--dz-skip, -60s) + var(--dz-d, .1s)) both, sz-dz-glow1 1.1s ease-out calc(var(--dz-skip, -60s) + 1.6s) both}
@LITS@{color:var(--fm-acc2, #f0d48c);opacity:1;font-weight:700}
@LITS@::after{content:"";display:block;width:4px;height:4px;margin:3px auto 0;border-radius:50%;background:var(--fm-acc2, #f0d48c);box-shadow:0 0 6px var(--fm-glow, #f0d48c)}
@keyframes sz-dz-roll{0%{opacity:0;transform:translate(-40px,-30px) rotate(-400deg) scale(.5)}12%{opacity:1}48%{transform:translate(7px,4px) rotate(22deg) scale(1.1)}66%{transform:translate(-3px,-4px) rotate(-9deg) scale(.97)}82%{transform:translate(1px,1px) rotate(3deg) scale(1.02)}100%{opacity:1;transform:none}}
@keyframes sz-dz-tumble{0%{transform:perspective(160px) rotateX(0) rotateY(0)}100%{transform:perspective(160px) rotateX(720deg) rotateY(360deg)}}
@keyframes sz-dz-pop{0%{opacity:0;scale:2}100%{opacity:1;scale:1}}
@keyframes sz-dz-flick{0%{content:"7"}9%{content:"15"}18%{content:"3"}27%{content:"18"}36%{content:"11"}45%{content:"2"}54%{content:"19"}63%{content:"9"}72%{content:"14"}81%{content:"6"}90%{content:"12"}100%{content:""}}
@keyframes sz-dz-hide{from{opacity:.85}to{opacity:0}}
@keyframes sz-dz-show{from{opacity:0}to{opacity:1}}
@keyframes sz-dz-label{from{opacity:0;transform:translateY(-3px)}}
@keyframes sz-dz-halo{0%{opacity:0;transform:scale(.3) rotate(0)}35%{opacity:1}100%{opacity:.55;transform:scale(1) rotate(40deg)}}
@keyframes sz-dz-shake{0%,100%{translate:0 0}15%{translate:-3px 1px}30%{translate:3px -1px}45%{translate:-2px 0}60%{translate:2px 1px}80%{translate:-1px 0}}
@keyframes sz-dz-glow1{0%{filter:drop-shadow(0 0 0 transparent) drop-shadow(0 3px 4px rgb(0 0 0 / .6)) saturate(.8)}35%{filter:drop-shadow(0 0 14px rgb(255 90 70)) drop-shadow(0 0 5px #ffd0c4) saturate(.8)}100%{filter:drop-shadow(0 0 7px rgb(220 40 28 / .95)) drop-shadow(0 0 2px #ffd0c4) drop-shadow(0 3px 4px rgb(0 0 0 / .6)) saturate(.8)}}
@keyframes sz-dz-glow{0%{filter:drop-shadow(0 0 0 transparent) drop-shadow(0 3px 4px rgb(0 0 0 / .45))}35%{filter:drop-shadow(0 0 14px #fff3c4) drop-shadow(0 0 6px var(--fm-glow, #f0d48c))}100%{filter:drop-shadow(0 0 5px var(--fm-glow, #f0d48c)) drop-shadow(0 0 2px #fff6d0) drop-shadow(0 3px 4px rgb(0 0 0 / .45))}}
/* 前传是浅色的委托单：线和小字照深墨 */
@R@:has(.era-pre) .dz>small{opacity:.9}
@media (max-width:639px){
  @R@ .sz-dice{gap:6px;margin-bottom:10px}
  @R@ .dz-row{gap:4px}
  @R@ .dz,@R@ .dz-r{width:38px}
  @R@ .dz-r{height:38px}
  @R@ .dz-r>b{font-size:14.5px!important}
  @R@ .dz-r::after{font-size:13px}
  @R@ .dz[data-v="20"] .dz-r::before{width:70px;height:70px;margin:-35px 0 0 -35px}
  @R@ .dz-hd{font-size:10.5px;letter-spacing:.24em;padding-bottom:10px}
}
@media (prefers-reduced-motion:reduce){
  @R@ .sz-dice *,@R@ .sz-dice *::before,@R@ .sz-dice *::after{animation:none!important}
  @R@ .dz-r::after{content:none}
  @R@ .dz:is([data-v="1"],[data-v="01"]) .dz-f::after{opacity:1}
}
'''


def css():
    lit, litf, lits, litr = [], [], [], []
    for k in range(6):
        sel = '%s:has(.sz-judge:is([data-dk="%s"],[data-dk="%d"])) .dz%d' % (R, NUM[k], k + 1, k + 1)
        lit.append(sel)
        litf.append(sel + ' .dz-f')
        litr.append(sel + ' .dz-r')
        lits.append(sel + '>small')
    out = CSS.replace('@LITF1@', ','.join(s.replace(' .dz-f', ':is([data-v="1"],[data-v="01"]) .dz-f') for s in litf)).replace('@LITF@', ','.join(litf)).replace('@LITS@::after', ','.join(s + '::after' for s in lits)).replace('@LITS@', ','.join(lits)).replace('@LITR@', ','.join(litr)).replace('@LIT@', ','.join(lit))
    out = out.replace('@D20@', D20).replace('@R@', R)
    assert '@' not in re.sub(r'@(media|keyframes)', '', out), re.findall(r'@\w+@?', out)[:5]
    return out


# ---------------- 等待那几秒：命运的丝线正在编织 ----------------
# 两侧各三缕金线织向正中，在正中交成一颗二十面骰的纹章，底下一行小字轮着换。只用一个元素的 ::before（线和纹章，一层遮罩从两边往中间揭开）和 ::after（字）。
SAY = ['命运的丝线正在编织', '群星正在各自落位', '经线已张，纬线正在穿梭', '纺锤再转一圈，线头便递到你手里', '骰子还在掌心，尚未落下']
_W = ("<g fill='none' stroke-linecap='round' vector-effect='non-scaling-stroke'>"
      "<path d='M0 20C46 6 82 44 120 30S178 44 200 50' stroke='rgb(240,212,140)' stroke-width='1.4' stroke-opacity='.95' vector-effect='non-scaling-stroke'/>"
      "<path d='M0 50C40 64 84 34 122 54S180 50 200 50' stroke='rgb(214,178,106)' stroke-width='1.1' stroke-opacity='.7' vector-effect='non-scaling-stroke'/>"
      "<path d='M0 82C44 94 80 58 120 70S178 56 200 50' stroke='rgb(255,236,190)' stroke-width='1.2' stroke-opacity='.85' vector-effect='non-scaling-stroke'/>"
      "<path d='M0 36C52 30 90 62 140 46S186 50 200 50' stroke='rgb(214,178,106)' stroke-width='.8' stroke-opacity='.45' vector-effect='non-scaling-stroke'/>"
      "<path d='M0 66C52 74 92 40 142 56S186 50 200 50' stroke='rgb(240,212,140)' stroke-width='.8' stroke-opacity='.45' vector-effect='non-scaling-stroke'/></g>")
WEAVE_L = 'url("data:image/svg+xml,%s")' % quote("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 100' preserveAspectRatio='none'>%s</svg>" % _W, safe="/:=' -.,()")
WEAVE_R = 'url("data:image/svg+xml,%s")' % quote("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 100' preserveAspectRatio='none'><g transform='translate(200 0) scale(-1 1)'>%s</g></svg>" % _W, safe="/:=' -.,()")
SEAL = _svg("<circle cx='50' cy='50' r='47' fill='rgb(255,220,140)' fill-opacity='.10'/>"
            "<polygon points='%s' fill='rgb(18,16,44)' fill-opacity='.85' stroke='rgb(240,212,140)' stroke-width='3'/>"
            "<polygon points='%s' fill='rgb(240,212,140)' fill-opacity='.16' stroke='rgb(255,236,190)' stroke-width='2.4'/>"
            "<g stroke='rgb(240,212,140)' stroke-width='1.6' stroke-opacity='.85'><path d='M50 6L50 22M88 28L76 66M12 28L24 66M50 94L76 66M50 94L24 66M88 72L76 66M12 72L24 66M88 28L50 22M12 28L50 22'/></g>"
            "<path d='M50 34l3 9 9 3-9 3-3 9-3-9-9-3 9-3z' fill='rgb(255,244,210)'/>" % (_HEX, _TRI), '0 0 100 100')


def _say_keyframes(name):
    n = len(SAY)
    seg = 100.0 / n
    fr = []
    for i, t in enumerate(SAY):
        a = i * seg
        fr.append('%.2f%%{content:"%s";opacity:0;transform:translateY(4px)}' % (a + (0.01 if i else 0), t))
        fr.append('%.2f%%{content:"%s";opacity:1;transform:none}' % (a + seg * .12, t))
        fr.append('%.2f%%{content:"%s";opacity:1;transform:none}' % (a + seg * .82, t))
        fr.append('%.2f%%{content:"%s";opacity:0;transform:translateY(-3px)}' % (a + seg, t))
    return '@keyframes %s{%s}' % (name, ''.join(fr))


def weave_css(sel, box='', panel=True):
    """sel：等待时那个空着的元素。box：那个元素自己的版面（宽高、外边距），各平台不一样"""
    cyc = 3.6
    o = []
    w = o.append
    w('%s{position:relative;display:block;min-height:124px;%s}' % (sel, box))
    # 底：一块淡淡的夜色，深浅主题上都看得清金线
    if panel:
        w('%s{background:radial-gradient(60%% 80%% at 50%% 42%%, rgb(240 212 140 / .10), transparent 70%%), linear-gradient(180deg, rgb(14 13 34 / .9), rgb(10 10 26 / .86))!important;'
          'border-radius:14px!important;box-shadow:inset 0 0 0 1px rgb(214 178 106 / .28), 0 6px 18px -10px rgb(0 0 0 / .6)!important}' % sel)
    w('%s::before{content:"";position:absolute;left:14px;right:14px;top:8px;height:84px;pointer-events:none;'
      'background:%s center/40px 40px no-repeat, %s left center/50%% 100%% no-repeat, %s right center/50%% 100%% no-repeat;'
      '-webkit-mask:linear-gradient(#000,#000) left center/0%% 100%% no-repeat, linear-gradient(#000,#000) right center/0%% 100%% no-repeat, linear-gradient(#000,#000) center/0 0 no-repeat;'
      'mask:linear-gradient(#000,#000) left center/0%% 100%% no-repeat, linear-gradient(#000,#000) right center/0%% 100%% no-repeat, linear-gradient(#000,#000) center/0 0 no-repeat;'
      'filter:drop-shadow(0 0 4px rgb(240 212 140 / .55));animation:sz-wv-weave %.1fs cubic-bezier(.45,.05,.3,1) infinite}' % (sel, SEAL, WEAVE_L, WEAVE_R, cyc))
    w('%s::after{content:"%s";position:absolute;left:0;right:0;bottom:12px;text-align:center;font-family:"Noto Serif SC","Source Han Serif SC","Songti SC",serif;'
      'font-size:13.5px;line-height:1.4;letter-spacing:.32em;padding-left:.32em;color:#ecd9a8;text-shadow:0 0 10px rgb(240 212 140 / .45), 0 1px 2px rgb(0 0 0 / .7);'
      'white-space:nowrap;pointer-events:none;animation:sz-wv-say %.1fs ease-in-out infinite}' % (sel, SAY[0], cyc * len(SAY)))
    w('@keyframes sz-wv-weave{0%{opacity:0;-webkit-mask-size:0% 100%,0% 100%,0 0;mask-size:0% 100%,0% 100%,0 0}'
      '8%{opacity:1}'
      '46%{-webkit-mask-size:50% 100%,50% 100%,0 0;mask-size:50% 100%,50% 100%,0 0}'
      '58%{-webkit-mask-size:50% 100%,50% 100%,64px 64px;mask-size:50% 100%,50% 100%,64px 64px;filter:drop-shadow(0 0 10px rgb(255 236 190 / .95))}'
      '86%{opacity:1;-webkit-mask-size:50% 100%,50% 100%,64px 64px;mask-size:50% 100%,50% 100%,64px 64px;filter:drop-shadow(0 0 4px rgb(240 212 140 / .55))}'
      '100%{opacity:0;-webkit-mask-size:50% 100%,50% 100%,64px 64px;mask-size:50% 100%,50% 100%,64px 64px}}')
    w(_say_keyframes('sz-wv-say'))
    w('@media (max-width:639px){%s::after{font-size:12.5px;letter-spacing:.18em;padding-left:.18em}}' % sel)
    w('@media (prefers-reduced-motion:reduce){%s::before{animation:none;-webkit-mask:none;mask:none}%s::after{animation:none}}' % (sel, sel))
    return '\n'.join(o) + '\n'


# 日里：11-27 用户拿等待探针在手机上录了两回屏（探针在 底稿/状态栏/等待探针_11-27/），真页面上是这样：
#   一、点了发送，头两秒多对话区什么都不加，只有输入栏的发送钮换成一个 animate-spin 的圈（平台的，不动它）；
#   二、接着助手那一行出来，气泡里 .space-y-3 底下除了 .rili-markdown-renderer 还多一块（里头是几颗细长的小点，
#       类名带 aspect-square、bg-primary、rounded-full，就是平台的“三点在跳”），持续两秒多，出第一个字就拿掉了；
#   线和字挂在那一块上，里头的小点藏起来。思考过程的块这一回没见到（deepseek-v4.1-flash 不出思考），下面第二条照旧是推的。
# 11-28 玩家反馈：点了正文的编辑，平台把正文那一格换成一个带输入框的编辑块，原来“renderer 以外的那一块”把它也认成了等待，骰子盖在编辑框上。
#   改成两头认：里头有那几颗圆点（rounded-full），而且没有输入框、没有可编辑的块，才是等待那一块。
RILI_WAIT_SEL = ('.is-assistant .space-y-3 > :not(.rili-markdown-renderer):has([class*="rounded-full"])'
                 ':not(:has(textarea, input, [contenteditable="true"], [contenteditable=""]))')
RILI_THINK_SEL = '.is-assistant :is([class*="reasoning" i],[class*="thinking" i])'
CHROME_BEGIN = '/* ==== 11-27 等待那几秒（dice_fx.py --chrome 写的，改 dice_fx.py 再跑）'
CHROME_END = '/* ==== 等待那几秒 完 ==== */'


def rili_wait_css():
    o = [CHROME_BEGIN + '：模型还没出字的时候，回复那一格里两侧金线织向正中、交成一颗骰子，底下一行小字轮着换。'
         '等待那一块是 11-27 探针在日里真页面上认出来的（气泡里 renderer 以外的那一块）；思考过程那一条还是推的 ==== */']
    o.append(weave_css(RILI_WAIT_SEL, 'width:min(520px, calc(100vw - 96px));margin:2px 0'))   # 带一块夜色底，日里浅色主题里金线也看得清
    o.append('%s > *{display:none!important}' % RILI_WAIT_SEL)   # 平台的三颗跳动小点
    o.append('%s{position:relative;padding-top:22px!important}' % RILI_THINK_SEL)
    o.append('%s::before{content:"命运的丝线正在编织";position:absolute;left:0;right:0;top:0;height:18px;font-size:11.5px;line-height:18px;letter-spacing:.3em;text-align:center;color:#d6b26a;'
             'background:linear-gradient(90deg, transparent, rgb(214 178 106 / .7) 30%%, rgb(255 236 190 / .95) 50%%, rgb(214 178 106 / .7) 70%%, transparent) 0 100%%/200%% 1px no-repeat;'
             'animation:sz-wv-thread 1.8s linear infinite;pointer-events:none}' % RILI_THINK_SEL)
    o.append('@keyframes sz-wv-thread{from{background-position:100% 100%}to{background-position:-100% 100%}}')
    o.append(CHROME_END)
    return '\n'.join(o) + '\n'


# 风月：占位那一格（data-message-id 以 answer-placeholder- 开头的 #customized-answer，内容空着，头像角上三点在闪），
# 模型第一个字到了，整个占位换成正式回复；正式回复里那一条 thinking-line（生成中那条细线）换成一缕会流动的金线，只给最新一对问答
FY_PH = '#customized-answer[data-message-id^="answer-placeholder-"]'
FY_LAST = '.chat-container > .pt-24 > #customized-answer'


def fy_css():
    o = ['/* 11-27 命运骰（dice_fx.py）：风月的回复里不能带 <style>，最新一对问答（外壳的直接内容）里的骰盘才掷，列表里的只摆结果 */',
         '%s .sz-dice{--dz-skip:0s}' % FY_LAST,
         '/* 11-27 等待那几秒：占位那一格换成命运的丝线 */',
         '%s :is(#customized-answer-container,#customized-answer-content-container){background:transparent!important;box-shadow:none!important;border-color:transparent!important;width:100%%!important;max-width:100%%!important;margin:0!important;padding:0!important}' % FY_PH,
         '%s #customized-answer-avatar{display:none!important}' % FY_PH,
         weave_css(FY_PH + ' #customized-answer-content', 'width:100%!important;max-width:100%!important;padding:0!important;margin:4px 0 8px!important;color:transparent!important'),
         '%s #customized-answer-content-thinking-line{height:1px!important;background:linear-gradient(90deg, transparent, rgb(214 178 106 / .75) 30%%, rgb(255 236 190) 50%%, rgb(214 178 106 / .75) 70%%, transparent) 0 0/200%% 100%% no-repeat!important;'
         'box-shadow:0 0 6px rgb(240 212 140 / .6);animation:sz-wv-thread 1.8s linear infinite}' % FY_LAST,
         '@keyframes sz-wv-thread{from{background-position:100% 0}to{background-position:-100% 0}}']
    return '\n'.join(o) + '\n'


def write_chrome():
    p = os.path.join(HERE, 'platform_chrome.css')
    s = open(p, encoding='utf-8', newline='').read()
    blk = rili_wait_css()
    if CHROME_BEGIN in s:
        a = s.index(CHROME_BEGIN)
        b = s.index(CHROME_END) + len(CHROME_END)
        s = s[:a] + blk.rstrip('\n') + s[b:]
    else:
        s = s.rstrip('\n') + '\n\n' + blk
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
    return len(blk)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for n, q, nest in check():
        print('%-6s 量词 %2d%s%s' % (n, q, '  过二十五了' if q > 25 else '', '  量词套量词' if nest else ''))
    print('骰盘样式 %d 字，风月 %d 字，日里等待 %d 字' % (len(css()), len(fy_css()), len(rili_wait_css())))
    if '--chrome' in sys.argv:
        print('platform_chrome.css 写了等待那一段', write_chrome(), '字')
