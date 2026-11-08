# 11-07 晚，玩家烤鹅反馈「看不了上一轮的状态栏」「超程铭刻是不是没适配」以后添的。用户原话几回：
#   “做一下可以看到之前输出轮次的状态栏吧，超程铭刻做成被铭刻的角色在角色栏那里常驻，备注一下是远讯”
#   “直接做成往上滚动看到的每一轮的样子都是一样的，或者做成每一个输出都是一个独立的内框。现在最新一轮状态栏ui常驻底部的设计会与查看前一轮ui往上滚动冲突。
#    同时移除掉加载动画，改成滑动过渡”，又说“推演框会在每次往上滑动时在有美化与无美化之间来回跳转”，看了页签贴顶那一稿说“我觉得保留在下方好一点”。
# 一、每条回复一个内框，新旧一个样子（第三稿，替掉第一稿给旧回复另配淡页签、第二稿页签贴顶的做法）：
#     原来样式靠「后面还有没有带状态栏的回复」认最新一条（@L@），平台的对话列表只把屏幕附近的几条放在页面上，往上滑，最新那一条被拿掉，
#     上一条就被认成最新，地名牌、三条、页签在完整和精简之间来回跳。现在不分新旧：@L@ 换成每一条（只认最里头那一层行），旧回复藏死的两条去掉，
#     每条回复都是一个内框：地名牌和三条、正文和分支、末尾一排页签，都一个样子。页签留在每一条的末尾，不钉在屏幕上。
#     手札和各页叠在同一格里（排成三行：地名牌，手札和各页，页签）：点了页签，那一页从右边滑进来盖在正文上，底边贴着页签，正文淡下去垫在底下，
#     这一格的高至少是正文那么高，所以页签点完原地不动，不会被甩出屏幕；那一页比正文长就往下撑开。回手札从左边滑回来。
#     认不出排三行的那一层（平台要是在外头多包了一层），就照原样一个接一个排：那一页落在正文和页签中间，页签往下让，也不会往上跳。
#     去掉暗下去转徽记的那一段；战斗页签不再一闪一闪。页签全页同一组单选钮，一次只开一页。
# 二、超程铭刻（底卡 #1385）的人常驻同行页：不在身边的时候也每轮写一组，相遇状态写 远讯，最近收到的消息写一行
#     `§角色行｜远讯｜消息 ｜ 渠道·路上多久 ｜ 可信度 ｜ 发生 日期 → 收到 日期`。同行页里这一组的头像和立绘淡一层、
#     头像角上挂一个「远」字，点开先看到那一封（不藏在小页签里），底下是好感和关系。只写玩家已经收到的。
# 发布卡（patch_pub_1107b.py）和往后的测试卡、发布卡（make_rules_frame.py、make_css_frame.py、make_pub_card.py）都从这里取，一处改。
# 规则照平台的规矩：不用后顾、惰性量词，量词不套量词，一条不超过 25 个量词。

F = '([^｜\\n]*)'


def _r(name, rx, rep):
    return {"name": name, "regex": rx, "replaceString": rep, "enabled": True, "messageRole": "assistant", "applyMode": "front-end"}


# ---- 远讯那一行：插在通用的「角色行」那一条前头，不然它会落进关系那一页 ----
FAR = ('<div class="sz-nc sz-far" data-t="形象" data-k="远讯"><b class="sz-ht">远讯</b><span class="sz-far-m">%s</span>'
       '<span class="sz-far-x"><i class="far-w">%s</i><i class="far-c" data-v="%s">%s</i><i class="far-d">%s</i></span></div>ⓔ')
FAR_RULES = [
    _r('角色·远讯', '/§角色行｜远讯｜' + F + '｜' + F + '｜' + F + '｜([^\\n]*)/g', FAR % ('$1', '$2', '$3', '$3', '$4')),
    _r('角色·远讯·三栏', '/§角色行｜远讯｜' + F + '｜' + F + '｜([^\\n]*)/g', FAR % ('$1', '$2', '$3', '$3', '')),
    _r('角色·远讯·一句', '/§角色行｜远讯｜([^\\n]*)/g', FAR % ('$1', '', '', '', '')),
]
GENERIC_ROW = '/§角色行｜([^｜\\n]{1,8})｜([^\\n]*)/g'   # 通用的那一条，FAR_RULES 排在它前头

# ---- 样式里认「哪一条回复」：原来的 @L@ 只认最新一条，换成每一条；只认最里头那一层行，免得外头哪一层也带着 contain: layout ----
L_OLD = 'div[style*="contain: layout"]:has(.sz-hud):not(:has(~ div .sz-hud))'
O_SEL = 'div[style*="contain: layout"]:has(.sz-hud):has(~ div .sz-hud)'
L_NEW = 'div[style*="contain: layout"]:has(.sz-hud):not(:has(div[style*="contain: layout"]))'
O_DROP = ['@O@ .sz-pane{display:none!important}', '@O@ .sz-prose{display:block!important}']   # 旧回复藏死的两条，去掉

MARK = '/* ==== history_far'   # 这一块的头，重打的时候认它整块换掉
OLD_MARK = '/* ==== 11-07 晚：旧回复也能翻那一轮的状态栏'   # 第一稿那一块的头（发出去的第一稿发布卡里有），重打时整块拿掉
ENVELOPE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 5h18v14H3zM5 8.2v8.8h14V8.2l-7 4.9z' "
            "fill='%23000' fill-rule='evenodd'/%3E%3C/svg%3E\")")   # 信封：一圈框、上头一块倒三角的封口
GRID = ':is(@R@,@R@ *):has(> .sz-page.sz-prose)'   # 手札的上一层（一般就是回复那一层），在它里头排三行
PAGES = ','.join('.t-' + t for t in ['panel', 'deed', 'bag', 'party', 'news', 'map', 'mem', 'war'])

CSS_ADD = '\n'.join([
    MARK + '（11-07 晚）：每条回复一个内框，新旧一个样子；页签在每一条末尾、不钉在屏幕上；点了页签那一页滑进来盖在正文上；超程铭刻的人标远讯 ==== */',
    # 内框：一条回复一块，框边、淡一层的底；回复之间那道小纹挪到框的上沿正中，像一枚扣
    '@R@{padding:14px 16px 16px!important;margin:22px 0 6px!important;border:1px solid color-mix(in srgb, var(--fm-edge2) 70%, transparent)!important;border-radius:18px;'
    'background:linear-gradient(180deg, color-mix(in srgb, var(--fm-band) 42%, transparent), color-mix(in srgb, var(--fm-band) 16%, transparent))!important;'
    'box-shadow:0 12px 30px rgb(0 0 0 / .28), inset 0 1px 0 rgb(255 255 255 / .05)!important;overflow-x:clip}',
    '@R@::before{position:absolute;left:50%;top:-11px;width:200px;max-width:60%;height:20px;margin:0!important;transform:translateX(-50%);z-index:1}',
    '@media (max-width:639px){@R@{padding:10px 10px 12px!important;border-radius:14px}}',
    # 排三行：地名牌，手札和各页叠在同一格，页签。认不出这一层的话照原样一个接一个排
    GRID + '{display:grid!important;grid-template-columns:minmax(0,1fr);align-items:start}',
    GRID + '>*{grid-column:1;min-width:0}',
    GRID + '>details.sz-hud{grid-row:1}',
    GRID + '>.sz-page{grid-row:2}',
    GRID + '>.sz-tabs{grid-row:3}',
    # 页签：留在每一条的末尾，不钉在屏幕上；去掉暗下去转徽记那一段，战斗页签不再一闪一闪
    '@R@ .sz-tabs{position:relative!important;top:auto!important;bottom:auto!important;z-index:3!important;margin:12px -4px 0!important;transition:none!important}',
    '@R@ .sz-tabs::before,@R@ .sz-tabs::after{content:none!important;animation:none!important}',
    '@R@ .t-war{animation:none!important}',
    # 点了页签：手札淡下去垫在底下（还占着高，页签不动），那一页贴着页签从右边滑进来；那一页比正文长就往下撑开
    '@R@:has(:is(' + PAGES + ') input:checked) .sz-page.sz-prose{display:block!important;opacity:.14;pointer-events:none;user-select:none}',
    '@R@ .sz-page.sz-prose{transition:opacity .22s ease}',
    '@R@ .sz-pane{min-height:0!important}',
    '@R@ .sz-page.sz-pane{align-self:end;position:relative;z-index:2;margin:0 -4px!important;padding:12px 14px 14px!important;border:1px solid color-mix(in srgb, var(--fm-edge2) 80%, transparent);border-radius:14px;'
    'background:linear-gradient(180deg, color-mix(in srgb, var(--fm-band) 95%, transparent), color-mix(in srgb, var(--fm-band2) 95%, transparent));box-shadow:0 -10px 28px rgb(0 0 0 / .35);'
    'animation:sz-slide-in .26s cubic-bezier(.2,.7,.3,1) both}',
    '@media (max-width:639px){@R@ .sz-page.sz-pane{padding:10px 10px 12px!important;margin:0 -2px!important}}',
    '@keyframes sz-slide-in{from{opacity:0;transform:translateX(28px)}to{opacity:1;transform:none}}',
    '@keyframes sz-slide-back{from{opacity:0;transform:translateX(-28px)}to{opacity:1;transform:none}}',
    '@R@:has(:is(.t-prose,.sz-x) input:checked) .sz-page.sz-prose{animation:sz-slide-back .26s cubic-bezier(.2,.7,.3,1) both}',
    '@media (prefers-reduced-motion:reduce){@R@ .sz-page{animation:none!important;transition:none!important}}',
    # 超程铭刻的人常驻同行页。不在身边的那一组相遇状态写 远讯：头像和立绘淡一层、头像角上挂一个「远」字，最近收到的那一封排在一句话底下、好感上头，不藏进小页签
    '@R@ .sz-npc-tags span.met[data-v="远讯"]{color:#d9e7ff;background:rgb(96 140 214 / .26);box-shadow:inset 0 0 0 1px rgb(150 186 240 / .45)}',
    '@R@ .sz-npc:has(.met[data-v="远讯"])>.sz-av i{filter:saturate(.45) brightness(.86)}',
    '@R@ .sz-npc:has(.met[data-v="远讯"])>.sz-av i::after{content:"远";position:absolute;right:-4px;bottom:-4px;display:grid;place-items:center;width:20px;height:20px;border-radius:50%;'
    'font-family:var(--fm-serif);font-size:11px;font-weight:700;line-height:1;color:#12233f;background:#b9d2f6;box-shadow:0 0 0 2px var(--fm-band2), 0 2px 6px rgb(0 0 0 / .45)}',
    '@R@ .sz-npc:has(.met[data-v="远讯"]) .sz-npc-b>.sz-por{filter:saturate(.5) brightness(.9)}',
    '@R@ .sz-nc.sz-far{order:4;display:block!important;position:relative;margin:0 0 14px;padding:11px 16px 12px 18px;border:1px solid rgb(150 186 240 / .32);border-left:3px solid #9fbfee;'
    'border-radius:4px 12px 12px 4px;background:linear-gradient(110deg, rgb(110 150 220 / .15), transparent 85%)}',
    '@R@ .sz-far>.sz-ht{display:flex!important;align-items:center;gap:7px;margin:0 0 6px!important;font-size:12px!important;letter-spacing:.2em;color:#b9d2f6!important}',
    '@R@ .sz-far>.sz-ht::before{content:"";width:15px;height:15px;background:#b9d2f6;-webkit-mask:' + ENVELOPE + ' center/contain no-repeat;mask:' + ENVELOPE + ' center/contain no-repeat}',
    '@R@ .sz-far-m{display:block;font-family:var(--fm-serif);font-size:15px;line-height:1.75;color:var(--fm-ink)}',
    '@R@ .sz-far-x{display:flex;flex-wrap:wrap;gap:5px 6px;margin-top:9px}',
    '@R@ .sz-far-x i{font-style:normal;font-size:11.5px;line-height:21px;padding:0 9px;border-radius:11px;background:rgb(110 150 220 / .16);color:var(--fm-ink2)}',
    '@R@ .sz-far-x i:empty{display:none}',
    '@R@ .sz-far-x i.far-c[data-v*="高"]{color:#c4ecd3;background:rgb(80 170 120 / .2)}',
    '@R@ .sz-far-x i.far-c[data-v*="中"]{color:#f2e3b4;background:rgb(190 150 60 / .2)}',
    '@R@ .sz-far-x i.far-c[data-v*="低"]{color:#f5c9bd;background:rgb(200 84 66 / .2)}',
])

# ---- 提示词：(字段, 原来的一段, 换成)；打补丁的时候每一处都要正好命中一次 ----
FAR_SKEL = ('超程铭刻的人（至多三位，见【超程铭刻】）不在身边也每轮各留一组，排在在场的人后头，只写这几行：§角色（末栏照他是谁写 `立绘:短名` 或 `名牌`）、'
            '§角色签（相遇状态写 远讯）、§角色话（他最近一封信或口信里的一句原话，还没来过消息写 还没有消息）、'
            '`§角色行｜远讯｜最近收到的消息，一两句 ｜ 渠道·路上走了多久 ｜ 可信度 高/中/低 ｜ 发生 日期 → 收到 日期`、§角色行｜羁绊，关系因果有就写；'
            '容貌、着装与姿态、状态、属性、私产和第二部分不写。远讯那一行只写玩家已经收到的；还在路上的消息、他那边真在发生的事照【超程铭刻】在思维链里推，不进状态栏；'
            '没有新消息的轮次照抄上一轮。人回到身边就照在场的写，相遇状态照实；解除铭刻那一轮起不再写。')
SYS_EDITS = [
    ('⑧ 远讯一组', '说了话或做了要紧事的才算。**立绘只给预设短名本人**', '说了话或做了要紧事的才算。' + FAR_SKEL + '**立绘只给预设短名本人**'),
    ('相遇状态五档', '（相遇状态四档：未遇／已识／同行／暂离）', '（相遇状态五档：未遇／已识／同行／暂离／远讯，远讯只给超程铭刻了、不在身边的人）'),
]
REAR_EDITS = [
    ('后置词 远讯', '主角面板禁写「未知」「同上」。', '主角面板禁写「未知」「同上」。超程铭刻的人不在身边也每轮在角色里留一组，相遇状态写 远讯，最近收到的消息写在 §角色行｜远讯。'),
]
INSCRIBE_HEAD = '# 旅印远讯·超程铭刻'
INSCRIBE_ADD = ('\n7. 状态栏里常驻：被铭刻的人每轮都在 ⑧角色 留一组；不在身边时相遇状态写 远讯，最近收到的一封写在 '
                '`§角色行｜远讯｜内容 ｜ 渠道·路上多久 ｜ 可信度 ｜ 发生 日期 → 收到 日期`（写法见骨架⑧），新消息到了才改这一行，没到就照抄上一轮，日期不跟着当天走。'
                '【超程铭刻：名】那一轮照功能命令轮回报铭刻成了没有，下一轮起他就在角色里；【解除超程铭刻：名】那一轮起不再写；'
                '【查看超程铭刻】照功能命令轮列三人最近收到的远讯和眼下够格被铭刻的人。')
CHANGELOG_V1 = ('11-07 晚：旧回复底下也有一排小页签，点开就能翻那一轮的状态栏；超程铭刻的人不在身边也常驻在同行页，'
                '头像角上挂一个「远」字，最近收到的消息、渠道、可信度和日期写在卡上。')
CHANGELOG = ('11-07 晚：每条回复都是一个独立的内框，往上翻看到的每一轮都跟最新一条一个样子，往上滑不再跳；页签在每一条的末尾，不再钉在屏幕底下；'
             '点了页签，那一页从右边滑进来盖在正文上，页签原地不动，不再暗下去转徽记。超程铭刻的人不在身边也常驻在同行页，头像角上挂一个「远」字，最近收到的消息、渠道、可信度和日期写在卡上。')
