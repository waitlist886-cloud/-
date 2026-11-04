# 大框搬到风月：frame.css 里的模块样式照用，选择器换成风月的页面结构，外壳那一层（框、两扇、楣、座、输入栏）照风月的版面重写。
# 风月和日里不一样的地方（照风月前端代码，11-04）：
# - 样式每条选择器前加 #installedBuiltInCss，:root 不认，消息里的 <style> 被平台拿掉，所以这一纪的变量直接写在外壳上，钟点靠回复里一个带 data-h 的空记号读进外壳。
# - 行内 style 的小写自定义属性会被 react-markdown 改坏（--v 变成 -V），规则和样式里 --v --m --h --n --a1… 都换成大写（make_fy_card.py 的 UPVAR）。
# - 顶栏在外壳里头（占版面），滚动容器从顶栏底下开始；平台给外壳写了 padding-bottom：输入栏高度 + 55。所以滚动容器的底跟着输入栏走，下沿 = 输入栏顶 + 顶栏高 - 55。
#   页签的 sticky 不用量输入栏多高；框的下沿直接画在输入栏（footer）上，输入栏变高，框跟着抬。
# - 只有最后一对问答是外壳的直接内容，前面的在 Virtuoso 的行里（[data-item-index]，带 contain: layout style paint）。
import re

import era_vars

# 选择器的权重要跟日里那一份一样，不然同一页里没带 R 的规则就压不过带 R 的（书页里的技能就是这样不见的）。回复那一层认 .markdown-body，不认 id
MD = '.markdown-body'
SH = 'div.relative.h-full:has(> .chat-container)'
ON = SH + ':has(.sz-hud)'
FT = ON + ' > .bg-gradient-to-t'
FI = FT + ' > .relative'
HD = ON + ' > .sticky.top-0'
SC = ON + ' > .chat-container'
CO = SC + ' > .pt-24'
AN = '#customized-answer'
LP = AN + ':not([data-item-index] *):has(.sz-hud):not(:has(~ #customized-answer .sz-hud))'
LV = '.chat-container:not(:has(> .pt-24 > #customized-answer .sz-hud)) [data-item-index]:has(.sz-hud):not(:has(~ [data-item-index] .sz-hud))'
# 日里的最新一条、旧的那两个选择器权重都是 (0,3,2)，这里用 :where 认人、前头几个空的 :not 凑够
W32 = 'div:not(x-x):not(.x1):not(.x2):not(.x3)'
L = W32 + ':where(%s,%s)' % (LP, LV)
O = W32 + ':where(%s:has(.sz-hud):not(%s):not(%s #customized-answer))' % (AN, LP, LV)
R_OLD = 'div[style*="contain: layout"]:has(.sz-hud):not(:has(~ div .sz-hud))'
O_OLD = 'div[style*="contain: layout"]:has(.sz-hud):has(~ div .sz-hud)'
SH_OLD = ':root:has(#conversation)'
# 座的下沿比输入栏顶低多少（默认那一屏差不多到屏幕底，输入栏高一点露一截底色，矮一点切掉一截）。画里窗口下沿那道线离图底 142、图高 282、宽 2500。
# 只往高里拉（宽不动，正中那块底才不比窗口宽出太多，宽出来的地方盖在两扇上是一道硬边）
KB = 156
BOTH = 310

# 页面外壳照主题变量改成这一纪的深色（平台的钮、分页、弹层都读这些），浅色主题下也是深色
THEME = ('--background:242 55% 15%;--foreground:42 44% 88%;--card:242 55% 15%;--card-foreground:42 44% 88%;--popover:242 55% 15%;--popover-foreground:42 44% 88%;'
         '--secondary:242 42% 22%;--secondary-foreground:42 44% 88%;--muted:242 42% 22%;--muted-foreground:42 30% 76%;--accent:242 42% 22%;--accent-foreground:42 44% 88%;'
         '--text-main:42 44% 88%;--text-secondary:42 18% 68%;--text-tertiary:42 44% 88%;--input-placeholder:42 20% 66%;--border:41 44% 42%;--input:41 44% 42%;--primary-secondary:41 56% 60% / .16')


def hours(sel_any, sel_last):
    """钟点：回复里那个空记号（.sz-hh[data-h=时]）读进外壳。最新一对问答优先，功能轮那种最新一对没有状态栏的，认行里的"""
    a, b = [], []
    for h in range(25):
        vals = [str(h)] + (['%02d' % h] if h < 10 else [])
        hit = ','.join('.sz-hh[data-h="%s"]' % v for v in vals)
        a.append('%s:has(%s :is(%s)){--sz-h:%d}' % (SH, sel_any, hit, h))
        b.append('%s:has(%s :is(%s)){--sz-h:%d}' % (SH, sel_last, hit, h))
    return '\n'.join(a + b)


def shell():
    """外壳这一层。从下往上：对话｜框边（外壳 ::after，z2）｜输入栏这一整层（z3：底色、两扇、座、输入框）｜楣和滚动那一颗（外壳 ::before，z4）｜顶栏（z20）"""
    return r'''
/* ---------- 页面：外壳的底、窗里的材质、内容列 ---------- */
@ON@{isolation:isolate;--sz-on:1;--fm-topband:46px;--fm-hdr:48px;--fm-dock:150px;--fm-colw:672px;--fm-stk:calc(var(--fm-hdr) - 37px);
  --sz-t:var(--sz-h, 12);--sz-day:clamp(0, sin(calc((var(--sz-t) - 6) * 15deg)), 1);
  background:var(--fm-base)!important;@THEME@}
@media (min-width:768px){@ON@{--fm-hdr:64px}}
@SC@{background:var(--fm-mat);background-size:var(--fm-colw) 100%;background-position:center top;background-repeat:no-repeat}
@CO@{max-width:672px!important;padding:76px 16px 0!important}
/* 平台的气泡：灰底、圆角、内边距都不要，一层一层撑满；头像、气泡顶上那道装饰线收起来，内容列正好在窗口正中 */
@AN@:is(:has(.sz-hud),:has(.sz-fnh)) :is(#customized-answer-container,#customized-answer-content-container,#customized-answer-content){background:transparent!important;border-color:transparent!important;box-shadow:none!important;width:100%!important;max-width:100%!important;padding:0!important;margin:0!important;flex:1 1 100%;display:block}
@AN@:is(:has(.sz-hud),:has(.sz-fnh)) :is(#customized-answer-avatar,#customized-answer-content-thinking-line){display:none!important}
@AN@:is(:has(.sz-hud),:has(.sz-fnh)) #customized-answer-content{color:var(--fm-ink2)!important}
/* 回复底下那一行（时间、模型、积分、铅笔那排钮）：字和图标照这一纪的墨色 */
@AN@:is(:has(.sz-hud),:has(.sz-fnh)) :is(#customized-answer-content-created-time,#customized-answer-content-model,#customized-answer-content-model *){color:var(--fm-ink2)!important}
@AN@:is(:has(.sz-hud),:has(.sz-fnh)) #customized-answer-content button{color:var(--fm-ink2)!important;border-color:var(--fm-line)!important}
@AN@:is(:has(.sz-hud),:has(.sz-fnh)) #customized-answer-content button:hover{color:var(--fm-acc2)!important}
/* 玩家说的话：一道细线，不另起一块 */
@ON@ #customized-question-avatar{display:none!important}
@ON@ #customized-question{justify-content:flex-end}
@ON@ #customized-question-content-container{margin:0!important;max-width:100%}
@ON@ #customized-question-content{background:color-mix(in srgb, var(--fm-acc) 14%, transparent)!important;border:1px solid color-mix(in srgb, var(--fm-acc) 40%, transparent);color:var(--fm-ink)!important}
@ON@ #customized-question-content-thinking-line{display:none}
@ON@ #customized-question-content-markdown{background:none!important;color:inherit!important}
/* 分支在风月上点不了（平台不认点击填入），不做成钮的样子 */
@R@ .sz-choices li{cursor:text;user-select:text}
@R@ .sz-choices li:hover{border-color:var(--fm-edge2);background:linear-gradient(color-mix(in srgb, var(--fm-acc) 10%, transparent), color-mix(in srgb, var(--fm-acc) 4%, transparent))}
/* 平台的 markdown 样式：记录展开出来的列表、段落不要它的缩进和外边距 */
@R@ ol,@R@ ul{list-style:none;padding-left:0;margin:0}
@R@ li + li{margin-top:0}
@R@ .sz-hh{display:none}

/* ---------- 顶栏：压成这一纪的底色 ---------- */
@HD@{background-color:color-mix(in srgb, var(--fm-band2) 72%, transparent)!important;border-color:var(--fm-edge2)!important;color:#efe6d2!important}

/* ---------- 输入栏：框的底色、框的线（只动颜色、边和底，不动位置大小）。这一层比框边高，比楣低 ---------- */
@FT@{z-index:3;background:linear-gradient(var(--fm-edge), var(--fm-edge)) center top/min(var(--fm-win, 100%), 100%) 1.5px no-repeat, linear-gradient(var(--fm-band2), var(--fm-band2))!important}
@FI@{z-index:3;width:100%!important;max-width:672px!important}
@ON@ #ai-chat-input{background:transparent!important;color:#efe6d2!important;caret-color:var(--fm-acc)}
@ON@ #ai-chat-input::placeholder{color:rgb(239 230 210 / .5)!important}
@ON@ #customized-ai-input-container{color:#efe6d2}
@ON@ div:has(> #ai-input-content){background-color:var(--fm-band)!important;border-color:var(--fm-edge2)!important}
@ON@ div:has(> #ai-input-content):focus-within{box-shadow:0 0 0 1px var(--fm-edge2), 0 0 22px color-mix(in srgb, var(--fm-glow) 16%, transparent)!important}
@ON@ :is(#ai-input-controls,#ai-input-control-expand-icon){background:transparent!important;backdrop-filter:none!important}
@ON@ #ai-input-control-input-length{background:var(--fm-slot)!important;color:rgb(239 230 210 / .7)!important}
@ON@ #ai-input-controls svg,@ON@ #ai-send-button svg{color:#efe6d2}
@ON@ #ai-mod-button2 button{background:color-mix(in srgb, var(--fm-band) 82%, transparent)!important;border-color:var(--fm-edge2)!important;color:#efe6d2!important}
@ON@ #ai-mod-button2 button:hover{border-color:var(--fm-acc)!important;color:var(--fm-acc2)!important}
@ON@ #customized-pagination,@ON@ #customized-pagination *{color:#efe6d2}

/* ---------- 宽屏：框是浮雕刻成的，对话压在最底下，在正中那扇窗后面滚
   四方是整幅的画。图自带透明，靠窗那一边的轮廓就是画里的东西，平的地方正好贴着框边那道线，伸进窗里的地方盖住线。
   两扇的图高度跟着视口，一张 1400×2000，靠窗那一头 90 像素是伸进窗里的余量，所以伸进去多少按视口高算（4.5dvh）。超宽屏图不够宽，外侧补底色 ---------- */
@media (min-width:1100px){
  @ON@{--fm-win:max(760px, calc(640px + 11dvh));--fm-bite:4.5dvh;--fm-toph:300px;--fm-colw:var(--fm-win);--fm-ftop:calc(var(--fm-topband) - 10px);--fm-stk:calc(var(--fm-hdr) - 49px);timeline-scope:--fm-scroll}
  @SC@{scroll-timeline:--fm-scroll y;scrollbar-gutter:stable both-edges}
  /* 框边：下半截叫输入栏那一层盖住，框的下沿就是输入栏的顶 */
  @ON@::after{content:"";position:absolute;left:calc(50% - var(--fm-win) / 2);width:var(--fm-win);top:calc(var(--fm-hdr) + var(--fm-ftop));bottom:0;z-index:2;pointer-events:none;
    border:var(--fm-bw) solid var(--fm-edge);border-image:var(--fm-bimg);border-radius:16px;
    box-shadow:inset 0 0 0 3px color-mix(in srgb, var(--fm-band) 85%, transparent), inset 0 0 0 4px var(--fm-edge2), inset 0 14px 20px -6px rgb(0 0 0 / .45), 0 0 0 1px rgb(0 0 0 / .5),
      0 -60px 0 48px var(--fm-band2)}
  /* 两扇 */
  @FT@::before,@FT@::after{content:"";position:absolute;bottom:0;height:100dvh;width:calc(50% - var(--fm-win) / 2 + var(--fm-bite));z-index:1;pointer-events:none;
    background-repeat:no-repeat;filter:brightness(calc(.55 + .45 * var(--sz-day))) drop-shadow(0 4px 9px rgb(2 4 12 / .62))}
  @FT@::before{left:0;background-image:linear-gradient(90deg, rgb(0 0 0 / .34), transparent 30%), var(--fm-l), linear-gradient(var(--fm-pl), var(--fm-pl));
    background-size:calc(100% - var(--fm-bite)) 100%, auto 100%, var(--fm-fw) 100%;background-position:left top, right center, left top}
  @FT@::after{right:0;background-image:linear-gradient(270deg, rgb(0 0 0 / .34), transparent 30%), var(--fm-r), linear-gradient(var(--fm-pr), var(--fm-pr));
    background-size:calc(100% - var(--fm-bite)) 100%, auto 100%, var(--fm-fw) 100%;background-position:right top, left center, right top}
  /* 座：挂在输入框那一层底下，下沿跟着输入栏的顶走 */
  @FI@::before{content:"";position:absolute;left:50%;width:6000px;margin-left:-3000px;top:calc(@KB@px - @BOTH@px);height:@BOTH@px;z-index:-1;pointer-events:none;
    background:var(--fm-bot) center bottom/2500px 100% no-repeat;filter:brightness(calc(var(--fm-bb) + (1 - var(--fm-bb)) * var(--sz-day))) drop-shadow(0 3px 7px rgb(2 4 12 / .6))}
  /* 楣和滚动那一颗（替被右边那一扇盖住的滚动条） */
  @ON@::before{content:"";position:absolute;left:0;right:0;top:0;bottom:0;z-index:4;pointer-events:none;
    background:var(--fm-gem) @GEMTO@/16px 16px no-repeat, var(--fm-top) center top/auto var(--fm-toph) no-repeat;
    animation:fm-gem linear both;animation-timeline:--fm-scroll;
    filter:brightness(calc(var(--fm-bb) + (1 - var(--fm-bb)) * var(--sz-day))) drop-shadow(0 3px 7px rgb(2 4 12 / .6))}
  @HD@::before{content:"";position:absolute;left:50%;top:50%;width:200px;height:30px;margin:-15px 0 0 -100px;background:@BANNER@ center/contain no-repeat;pointer-events:none}
}
@keyframes fm-gem{from{background-position:@GEMFROM@, center top}to{background-position:@GEMTO@, center top}}
/* ---------- 窄屏、手机：不挂浮雕，框只留一圈细边，上下各一道窄纹 ---------- */
@media (max-width:1099px){
  @ON@{--fm-colw:100%}
  @CO@{max-width:100%!important;padding:30px 14px 0!important}
  @ON@::after{content:"";position:absolute;left:5px;right:5px;top:calc(var(--fm-hdr) + 4px);bottom:0;z-index:2;pointer-events:none;border:1.5px solid var(--fm-edge);border-image:var(--fm-bimg);border-radius:12px;box-shadow:inset 0 0 0 3px color-mix(in srgb, var(--fm-band) 70%, transparent), inset 0 0 0 4px var(--fm-edge2), 0 0 0 6px var(--fm-band2);
    background:var(--fm-sep) center top 4px/150px 14px no-repeat, linear-gradient(var(--fm-matc) 55%, transparent) center top/100% 24px no-repeat}
  @FT@::before{content:"";position:absolute;left:6px;right:6px;bottom:100%;height:24px;z-index:1;pointer-events:none;background:var(--fm-sep) center bottom 4px/150px 14px no-repeat, linear-gradient(0deg, var(--fm-matc) 55%, transparent)}
  @R@ .sz-prose p{font-size:15.5px;line-height:1.9}
  @R@ .sz-bars{gap:8px 10px}
  @R@ .sz-bars .sz-bar{grid-template-columns:16px auto;font-size:11px}
  @R@ .sz-bars .sz-bar>i{width:16px;height:16px;grid-row:1}
  @R@ .sz-bars .sz-bar b{display:none!important}
  @R@ .sz-bars .sz-bar em{white-space:nowrap;font-size:10.5px}
  @R@ .sz-bars .sz-bar .sz-trk{grid-column:1/3}
  @R@ .sz-tab i{width:22px;height:22px}
  @R@ .sz-tab b{font-size:10.5px!important;letter-spacing:.04em}
  @R@ .sz-tab+.sz-tab::before{top:13px;width:3px;height:3px}
  @L@ .sz-tabs{padding:8px 2px 6px}
  @R@ .sz-grid{grid-template-columns:repeat(2,1fr)}
}
'''


def build(frame, drop_line, banner):
    """frame：frame.css 的全文；drop_line：别的纪那些行怎么认（跟日里发布卡同一个）。返回风月的样式，图还写 __ART__/x"""
    a = frame.index('/* ---------- 整页：外壳的底')
    b = frame.index('/* 玩家说的话：一道细线')
    mod = frame[frame.index('.rili-markdown-renderer:has(.sz-hud){background:none!important', a):b]
    head = [ln for ln in frame[:a].split('\n') if not drop_line(ln)]
    body = [ln for ln in mod.split('\n') if not drop_line(ln)]
    # 这一纪的变量：直接写在外壳上（日里是回复里那一段 <style> 指的，风月消息里不能带 <style>）
    fm = '%s{%s}' % (SH, ';'.join('--fm-%s:var(--maze-%s)' % (n, n) for n in era_vars.NAMES))
    out = '\n'.join(head) + '\n' + fm + '\n' + shell() + '\n' + '\n'.join(body)
    # 滚动那一颗的位置
    x = 'calc(50% + var(--fm-win) / 2)'
    gem_from = 'left %s top calc(var(--fm-hdr) + var(--fm-ftop) + 70px)' % x
    gem_to = 'left %s bottom calc(var(--fm-dock) + 64px)' % x
    for k, v in [('@THEME@', THEME), ('@ON@', ON), ('@SC@', SC), ('@CO@', CO), ('@FT@', FT), ('@FI@', FI), ('@HD@', HD), ('@AN@', AN), ('@KB@', str(KB)), ('@BOTH@', str(BOTH)),
                 ('@GEMFROM@', gem_from), ('@GEMTO@', gem_to), ('@BANNER@', banner), ('@R@', '.rili-markdown-renderer:has(.sz-hud)'), ('@L@', R_OLD)]:
        out = out.replace(k, v)
    # 选择器换成风月的
    out = out.replace(R_OLD, L).replace(O_OLD, O)
    out = out.replace('.rili-markdown-renderer', MD)
    out = out.replace(SH_OLD, SH)
    out = out.replace('.is-assistant', AN)
    # 模块里的页签 sticky 不再量输入栏多高
    assert out.count('bottom:calc(var(--fm-dock) + 6px)') == 1
    out = out.replace('bottom:calc(var(--fm-dock) + 6px)', 'bottom:var(--fm-stk)')
    out += '\n' + hours('[data-item-index]', '.chat-container > .pt-24 > #customized-answer') + '\n'
    for bad in [':root', '#conversation', '.is-user', 'rili-markdown', 'contain: layout', 'header>', 'main', 'custom-styles']:
        hit = [m.start() for m in re.finditer(re.escape(bad), re.sub(r'url\("data:[^"]*"\)', '', out))]
        assert not hit or bad == 'main', (bad, len(hit), out[hit[0] - 60:hit[0] + 60])
    return out
