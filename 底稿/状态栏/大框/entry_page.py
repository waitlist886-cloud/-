# 11-26d 入局那一条包装（用户：“关于第0轮，我觉得可以包装得漂亮一点”）。说明 底稿/收尾_11-26/入局包装.md。
# 记录写法不改：模型照 #0 写 §底座、§环境、§功能｜入局，空一行接片头一段、前半生几段（若娜瓦的话在“”里）、“这一页是你的旅印……”一行、
#   ```text 代码块的主控锚点、“回 推开门扉……”一行。这里的显示正则只认这几样的位置，拼成一张入局页：
#   殿门题头（死之神殿的画，纪名、地点、潮汐一行）→ 片头（暗底居中，一句一行，最新那一条一句一句淡入）→ 前半生（一页账：格线、页边一枚印、首字放大，
#   祂的话和旁白分开）→ 旅印（封了蜡的一张笺，标题“旅印 · 名字”，代码块照旧在里头，底下一个钮把锚点填进输入框）→ 门扉（一扇门做的大钮“推开门扉”，
#   一个次一点的“哪里不对，我说给你听”）。
# 写歪了的：没写片头、§话 写的台词、多写了面板和推演、锚点没包代码块、代码块没收尾、没写门扉那一行、整条没有底座，都接得住（各条的注释）。
# 要一份新锚点的 §功能｜旅印 也走旅印那张笺（没有题头和门）。
# 包法靠 rehype-raw：一个 HTML 块开 <div>、空一行接 Markdown、再一个 HTML 块收 </div>，平台照嵌套接起来（复刻台用 unified 那一套实测过）。
# make_rules_frame.py 把 RULES 插在「功能轮」前头；make_css_frame.py 接 css()；风月那一头 fy_shell_rules.py 调 fy_rep() 拿掉点击、门扉退成一行字。
# 记号用 Ⓡ 加一个字（Ⓡ始 Ⓡ末 Ⓡ句 Ⓡ填 Ⓡ讫 Ⓡ话），末一条收干净。

GO = '推开门扉'
FIX = '前半生里有一处不对：'
_META = '<span class="rj-hd-m"><em>$2</em><em>$3</em><em>$4</em></span>'
BANNER = '<div class="rj-hd"><i class="rj-art"></i><div class="rj-hd-t"><small>死之神殿</small><b>入　局</b>%s</div></div>'
LED = '<div class="rj-led"><i class="rj-stamp"></i><div class="rj-led-h">前半生</div>\n\n'
DOOR = ('<div class="rj-door"><span class="rj-go" data-action="set-textinput" data-value="%s"><i class="rj-lf"></i><i class="rj-rt"></i><b>推开门扉</b><small>进第一幕</small></span>'
        '<span class="rj-fix" data-action="set-textinput" data-value="%s">哪里不对，我说给你听</span><small class="rj-tip">点一下填进输入框，再按发送</small></div>') % (GO, FIX)
SEAL = ('\n\n</div>\n\n<div class="rj-seal"><i class="rj-wax"></i><div class="rj-seal-h"><b class="rj-seal-t">旅印</b><em>$2</em></div>'
        '<small class="rj-seal-s">复制下来，贴进你自己那边的提示词，往后每一轮都认得你</small>\n\n```text\n$1```\n\nⓇ填$1Ⓡ讫\n\n</div>\n\n<div class="rj-aft">\n\n')
FILL = '<div class="rj-fill"><span data-action="set-textinput" data-value="$1">填进输入框</span><small>手机上在输入框里长按全选、复制更顺手</small></div>'
# 平台照 safe-regex 验规则：量词不套量词（断言里的量词也算），所以下面一律不写“带量词的组再加量词”，要排除某些行就用逐字的否定断言
_DZ = r'§底座｜(?:纪元：)?([^\s·\n]{2,16})[^\s\n]{0,60} · (?:(?! · )[^\n]){0,30} · ((?:(?! · )[^\n]){1,60}) · ((?:(?! · )[^\n]){1,60})[^\n]*\n'
_IS_RJ = r'(?=[\s\S]*\n§功能｜入局)'
_END = r'\s*[ⓂⓈⒷ]?ⓩ?\s*$'

RULES = [
    # 题头：§底座 那一行换成殿门题头，纪名年份、地点、潮汐三格；底座写歪了、拆不出三格的，题头照出、不带那一行
    ('入局·题头', r'/^([^§]{0,400})' + _DZ + _IS_RJ + '/', '$1' + BANNER % _META + '\n'),
    ('入局·题头·底座歪了', r'/^([^§]{0,400})§底座｜[^\n]*\n' + _IS_RJ + '/', '$1' + BANNER % '' + '\n'),
    # 收成一页：§功能｜入局 前头的（题头、§环境）放最上，后头的正文夹在 Ⓡ始、Ⓡ末 中间，末尾一扇门。不带 ⓩ 也认（整条没写底座的）
    ('入局·收', r'/^(?![\s\S]*\n§正文｜)([\s\S]*)§功能｜入局[^\n]*\n?([\s\S]*[^\sⓂⓈⒷⓩ]|)' + _END + '/',
     '<div class="sz-fnh rj-fnh"><i></i><b>入局</b></div>\n\n<div class="rj">\n\n$1\n\nⓇ始\n$2\nⓇ末\n\n' + DOOR + '\n\n</div>'),
    # 半路要一份新锚点：只出旅印那张笺
    ('入局·旅印轮', r'/^(?![\s\S]*\n§正文｜)[\s\S]*§功能｜旅印[^\n]*\n?([\s\S]*[^\sⓂⓈⒷⓩ]|)' + _END + '/',
     '<div class="sz-fnh rj-fnh"><i></i><b>旅印</b></div>\n\n<div class="rj rj-re">\n\n' + LED + '$1\nⓇ末\n\n</div>'),
    # 写成 §话 的台词照祂的话排（带引号的照留，不带的补上）；别的记录行（§环境、多写的 §推演、§面板……）拿掉
    ('入局·话·带引号', r'/^§话｜[^｜\n]{0,24}｜[^｜\n]{0,24}｜(?=[“「])(?=[\s\S]*Ⓡ末)/gm', 'Ⓡ话'),
    ('入局·话', r'/^§话｜[^｜\n]{0,24}｜[^｜\n]{0,24}｜([^\n]{1,800})$(?=[\s\S]*Ⓡ末)/gm', 'Ⓡ话“$1”'),
    ('入局·去记录行', r'/^§[^\n]*\n?(?=[\s\S]*Ⓡ末)/gm', ''),
    # “这一页是你的旅印……”“回 推开门扉……”这两行：笺上和门上都写了，拿掉
    ('入局·去两行', r'/^[^\n“「]{0,20}[“「]?(?:推开门扉|这一页是你的旅印)[^\n]{0,80}\n?(?=[\s\S]*Ⓡ末)/gm', ''),
    # 片头：正文头一段（不是话、不是殿里的旁白、不是锚点），一句一行；后头开账页
    ('入局·片头', r'/Ⓡ始\n+(?![“「【<Ⓡ])(?![^\n]{0,1200}(?:殿里|殿中|殿深|青火|扶手|那只手))([^\n<§]{8,1200})\n/',
     '<div class="rj-op"><p>$1Ⓡ句</p></div>\n\n' + LED),
    ('入局·没有片头', r'/Ⓡ始\n*/', LED),
    ('入局·片头分句', r'/([^。！？\n<>Ⓡ]{1,200}(?:[。！？][”」]?|(?=Ⓡ句)))(?=[^\n<>]*Ⓡ句)/g', '<span>$1</span>'),
    # 锚点：没包代码块的补上开头那一道（上一行不是围栏），没收尾的在末尾补上收尾那一道，再整块换成旅印那张笺（标题取锚点头一行的名字），后头开一格放剩下的字
    ('入局·锚点没包', r'/\n(|[^`~\n][^\n]*)\n(?=【旅印[·・])/', '\n$1\n```text\n'),
    ('入局·锚点没收尾', r'/(\n【旅印[·・][^\n]*)((?:(?!```|~~~|Ⓡ末)[\s\S])*)Ⓡ末/', '$1$2\n```\nⓇ末'),
    # 祂的话（“ 起头的段、§话 改来的）跟旁白分开；只认锚点代码块以前的
    ('入局·祂的话', r'/^(?:Ⓡ话|(?=[“「]))([^\n]+)$(?=(?:(?!```|~~~|Ⓡ末)[\s\S])*(?:(?:```|~~~)[a-zA-Z]{0,8}[ \t]*\n【旅印|Ⓡ末))/gm', '<p class="rj-say">$1</p>'),
    ('入局·旅印笺', r'/\n[ \t]{0,3}(?:```|~~~)[a-zA-Z]{0,8}[ \t]*\n(【旅印[·・]([^】\n]{1,24})】(?:(?!\n```|\n~~~)[\s\S])*\n)(?:```|~~~)[ \t]*(?=\n|$)/', SEAL),
    # 填进输入框：锚点里有半角双引号、尖括号的（进不了属性）不出这个钮，只留代码块
    ('入局·填进输入框', r'/Ⓡ填([^"<>Ⓡ]{10,6000})Ⓡ讫/', FILL),
    ('入局·填不进', r'/Ⓡ填[^Ⓡ]{0,8000}Ⓡ讫/', ''),
    ('入局·收尾', r'/\s*Ⓡ末/', '\n\n</div>'),
    ('入局·去记号', r'/Ⓡ[始末句填讫话]/g', ''),
]


def fy_rep(name, rep):
    """风月没有 data-action：门扉退成一行字，“哪里不对”和“填进输入框”拿掉。返回改过的替换串"""
    if 'data-action' not in rep:
        return rep
    if name == '入局·填进输入框':
        return ''
    assert name == '入局·收', name
    rep = rep.replace(' data-action="set-textinput" data-value="%s"' % GO, '')
    i = rep.index('<span class="rj-fix"')
    j = rep.index('</span>', i) + len('</span>')
    rep = rep[:i] + rep[j:]
    rep = rep.replace('点一下填进输入框，再按发送', '回 推开门扉 就进第一幕，哪里不对直接说')
    assert 'data-action' not in rep
    return rep


# ---------------- 样式 ----------------
# 这一条自己带底色，不靠平台底色：题头和片头是殿里的夜，账页是旧羊皮纸，旅印是封蜡的笺，门是黑石嵌金。深浅两套主题一个样子，外头一圈阴影各自看得清。
# 平台把每个选择器前头加 .custom-styles；@SH@ 是 make_css_frame 的对话区外壳。
ART = '__ART__/rj_temple.webp'
CSS = r'''
/* ==== 11-26d 入局那一条（entry_page.py） ==== */
.rj{--rj-ink:#ece6da;--rj-ink2:#a9a296;--rj-gold:#d4b06a;--rj-gold2:#f0d79a;--rj-teal:#5fe0cf;--rj-red:#9b1d2e;--rj-night:#0b0a10;
  --rj-paper:#efe6d1;--rj-pink:#2b2219;--rj-pink2:#6e5f4c;--rj-serif:"Noto Serif SC","Source Han Serif SC","Songti SC","STSong","Noto Serif CJK SC",serif;
  position:relative;display:block;width:min(100%, 660px);margin:4px auto 10px;border-radius:16px;overflow:hidden;background:var(--rj-night);color:var(--rj-ink);
  font-family:var(--rj-serif);font-size:15px;line-height:1.85;text-align:left;
  border:1px solid rgb(212 176 106 / .42);box-shadow:0 0 0 1px rgb(0 0 0 / .5), 0 14px 40px -8px rgb(0 0 0 / .55), 0 0 30px -10px rgb(95 224 207 / .25)}
.rj *{box-sizing:border-box}
.rj p{margin:0}
.rili-markdown-renderer:has(.rj) .rj-fnh{display:none!important}
@SH@ .is-assistant:has(.rj),@SH@ .is-assistant:has(.rj) div:has(.rili-markdown-renderer){background:transparent!important;border-color:transparent!important;box-shadow:none!important;width:100%!important;max-width:100%!important;padding-left:0!important;padding-right:0!important}
.rili-markdown-renderer:has(.rj){width:100%!important;max-width:100%!important}
/* 题头：殿的画在上（照画的宽高比，王座和那只手不叫字压着），题字压在画底下渐黑的那一截 */
.rj-hd{position:relative;display:block;isolation:isolate}
.rj-hd .rj-art,.rj:not(:has(.rj-hd)):not(.rj-re)::before{content:"";position:relative;display:block;width:100%;aspect-ratio:1280/475;background:url("@ART@") 50% 50%/cover no-repeat}
.rj-hd .rj-art::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg, rgb(11 10 16 / .2) 0, rgb(11 10 16 / 0) 26%, rgb(11 10 16 / 0) 58%, rgb(11 10 16 / .7) 82%, var(--rj-night) 100%)}
.rj:not(:has(.rj-hd)):not(.rj-re)::before{-webkit-mask-image:linear-gradient(#000 62%, transparent);mask-image:linear-gradient(#000 62%, transparent)}
.rj-hd-t{position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;gap:2px;margin-top:-50px;padding:0 16px 6px;text-align:center}
.rj-hd-t small{font-size:11.5px;letter-spacing:.62em;padding-left:.62em;color:var(--rj-gold2);text-shadow:0 1px 6px #000}
.rj-hd-t b{font-size:30px;font-weight:700;letter-spacing:.32em;padding-left:.32em;line-height:1.3;color:#fbf7ee;text-shadow:0 0 18px rgb(95 224 207 / .55), 0 2px 10px #000}
.rj-hd-t b::before,.rj-hd-t b::after{content:"";display:inline-block;width:46px;height:1px;margin:0 14px;vertical-align:middle;background:linear-gradient(90deg, transparent, var(--rj-gold))}
.rj-hd-t b::after{background:linear-gradient(270deg, transparent, var(--rj-gold));margin-left:-.18em}
.rj-hd-m{display:flex;flex-wrap:wrap;justify-content:center;gap:4px 0;margin-top:6px;font-size:12.5px;line-height:1.6;color:var(--rj-ink)}
.rj-hd-m em{font-style:normal;padding:0 10px;text-shadow:0 1px 4px #000}
.rj-hd-m em+em{border-left:1px solid rgb(212 176 106 / .5)}
/* 片头：星空暗底，一句一行，字距宽 */
.rj-op{position:relative;padding:22px 34px 30px;text-align:center;
  background:radial-gradient(1px 1px at 12% 30%, #fff8 50%, transparent), radial-gradient(1px 1px at 78% 18%, #fff6 50%, transparent), radial-gradient(1.5px 1.5px at 64% 72%, #9ff5ea88 50%, transparent),
  radial-gradient(1px 1px at 30% 82%, #fff5 50%, transparent), radial-gradient(1px 1px at 90% 60%, #fff5 50%, transparent), radial-gradient(1.5px 1.5px at 22% 58%, #f0d79a77 50%, transparent),
  radial-gradient(70% 90% at 50% 0%, rgb(95 224 207 / .07), transparent 70%), var(--rj-night)}
.rj-op p{font-size:15.5px;line-height:2.05;letter-spacing:.14em;color:var(--rj-ink)}
.rj-op span{display:block;margin:0 auto 2px;max-width:30em;text-wrap:balance}
.rj-op span:last-child:not(:first-child){margin-top:12px;font-size:17px;color:var(--rj-gold2);letter-spacing:.2em;text-shadow:0 0 14px rgb(240 215 154 / .35)}
.rj-op::after{content:"";display:block;width:120px;height:9px;margin:20px auto 0;background:radial-gradient(circle at 50% 50%, var(--rj-gold) 0 2.5px, transparent 3px), linear-gradient(90deg, transparent, rgb(212 176 106 / .7) 40%, transparent 45%, transparent 55%, rgb(212 176 106 / .7) 60%, transparent) 50% 50%/100% 1px no-repeat}
/* 只在对话里还没有大框的时候（入局是这一局最新的那一条）一句一句淡入；滚走再滚回来、往后翻回来看都不再动 */
@keyframes rjIn{from{opacity:0;transform:translateY(6px);filter:blur(3px)}to{opacity:1;transform:none;filter:none}}
@SH@:not(:has(.sz-hud)) .rj-op span{animation:rjIn 1.3s ease-out both}
@SH@:not(:has(.sz-hud)) .rj-op span:nth-child(2){animation-delay:.9s}@SH@:not(:has(.sz-hud)) .rj-op span:nth-child(3){animation-delay:1.8s}
@SH@:not(:has(.sz-hud)) .rj-op span:nth-child(4){animation-delay:2.7s}@SH@:not(:has(.sz-hud)) .rj-op span:nth-child(5){animation-delay:3.6s}
@SH@:not(:has(.sz-hud)) .rj-op span:nth-child(6){animation-delay:4.5s}@SH@:not(:has(.sz-hud)) .rj-op span:nth-child(n+7){animation-delay:5.4s}
@media (prefers-reduced-motion:reduce){.rj-op span{animation:none!important}}
/* 前半生：一页账。羊皮纸、格线、左边两道红线、右上一枚印；祂的话是墨字，旁白是浅一档的小字 */
.rj-led{position:relative;margin:0 16px 18px;padding:46px 26px 28px 50px;border-radius:3px;color:var(--rj-pink);
  background:linear-gradient(90deg, transparent 33px, rgb(155 29 46 / .45) 33px 34px, transparent 34px 37px, rgb(155 29 46 / .45) 37px 38px, transparent 38px),
  repeating-linear-gradient(180deg, transparent 0 27px, rgb(110 95 76 / .17) 27px 28px) 0 46px/100% calc(100% - 46px) no-repeat,
  radial-gradient(120% 80% at 50% 0%, #f6efdd, var(--rj-paper) 60%, #e2d4b6);
  box-shadow:inset 0 0 0 1px rgb(120 90 50 / .25), inset 0 0 40px rgb(120 90 50 / .18), 0 6px 18px rgb(0 0 0 / .45)}
.rj-led-h{position:absolute;left:50px;top:14px;font-size:12px;letter-spacing:.5em;color:var(--rj-red)}
.rj-led-h::after{content:"";display:inline-block;width:60px;height:1px;margin-left:8px;vertical-align:middle;background:rgb(155 29 46 / .45)}
.rj-stamp{position:absolute;right:14px;top:8px;width:46px;height:46px;border-radius:50%;transform:rotate(-12deg);opacity:.8;
  border:2px solid rgb(155 29 46 / .78);box-shadow:inset 0 0 0 3px transparent, inset 0 0 0 4px rgb(155 29 46 / .55)}
.rj-stamp::before{content:"";position:absolute;left:50%;top:50%;width:16px;height:22px;margin:-12px 0 0 -8px;background:rgb(155 29 46 / .82);
  clip-path:polygon(50% 0, 64% 22%, 80% 38%, 88% 60%, 82% 82%, 64% 98%, 50% 100%, 36% 98%, 18% 82%, 12% 60%, 22% 40%, 34% 52%, 40% 30%)}
.rj-stamp::after{content:"";position:absolute;inset:5px;border-radius:50%;border:1px dashed rgb(155 29 46 / .5)}
.rj-led>p,.rj-led>.rj-say{margin:0 0 28px;font-size:14px;line-height:28px;color:var(--rj-pink2);letter-spacing:.04em}
.rj-led>:is(p,.rj-say):last-child{margin-bottom:0}
.rj-led>.rj-say{font-size:15.5px;color:var(--rj-pink);letter-spacing:.02em}
.rj-led>:is(p,.rj-say):first-of-type::first-letter{float:left;font-size:44px;line-height:52px;margin:2px 6px 0 0;color:var(--rj-red);font-weight:700}
.rj-led :is(h1,h2,h3,h4){font-size:14px;letter-spacing:.3em;color:var(--rj-red);margin:.4em 0}
.rj-led :is(strong,b){color:#5a1018}
.rj-re .rj-led:not(:has(p)){display:none}
.rj-re .rj-led-h,.rj-re .rj-stamp{display:none}
.rj-re .rj-led>:is(p,.rj-say):first-of-type::first-letter{float:none;font-size:inherit;line-height:inherit;margin:0;color:inherit;font-weight:inherit}
.rj-re .rj-led{padding:12px 22px;background:radial-gradient(120% 80% at 50% 0%, #f6efdd, var(--rj-paper) 60%, #e2d4b6)}
.rj-re{padding-top:10px}
/* 旅印：一张封了蜡的笺，代码块照旧在里头（复制、全选都认它），底下一个钮把整块填进输入框 */
.rj-seal{position:relative;margin:26px 16px 16px;padding:34px 18px 16px;border-radius:6px;color:#2b2219;text-align:center;
  background:radial-gradient(90% 60% at 50% 0%, #fbf6ea, #efe4cb 70%, #e3d3b1);
  box-shadow:inset 0 0 0 1px rgb(184 154 94 / .7), inset 0 0 0 5px #f3ead6, inset 0 0 0 6px rgb(184 154 94 / .45), 0 8px 22px rgb(0 0 0 / .5)}
.rj-wax{position:absolute;left:50%;top:-20px;width:44px;height:44px;margin-left:-22px;border-radius:47% 53% 50% 50%/52% 48% 52% 48%;
  background:radial-gradient(circle at 38% 34%, #d45a5f, #9b1d2e 45%, #5e0d18 80%);box-shadow:0 3px 8px rgb(0 0 0 / .45), inset 0 -2px 4px rgb(0 0 0 / .35)}
.rj-wax::before{content:"";position:absolute;inset:9px;border-radius:50%;border:1.5px solid rgb(255 214 200 / .45);box-shadow:inset 0 0 0 4px rgb(94 13 24 / .35)}
.rj-wax::after{content:"";position:absolute;left:50%;top:50%;width:12px;height:12px;margin:-6px 0 0 -6px;background:rgb(255 220 205 / .55);clip-path:polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%)}
.rj-seal-h{display:flex;justify-content:center;align-items:baseline;gap:10px;font-size:19px;letter-spacing:.18em}
.rj-seal-t{font-weight:700;color:var(--rj-red)}
.rj-seal-h em{font-style:normal;font-weight:700;color:#2b2219}
.rj-seal-h em::before{content:"·";margin-right:10px;color:var(--rj-red)}
.rj-seal-s{display:block;margin:2px 0 10px;font-size:12px;letter-spacing:.06em;color:#7a6a52}
.rili-markdown-renderer .rj .rj-seal pre{margin:0;text-align:left;white-space:pre-wrap;word-break:break-word;overflow-wrap:anywhere;max-width:100%;max-height:min(52dvh, 460px);overflow:auto;
  padding:12px 14px;border-radius:4px;background:rgb(255 252 244 / .62);box-shadow:inset 0 0 0 1px rgb(184 154 94 / .55);color:#2b2219;-webkit-user-select:all;user-select:all;
  font-family:var(--rj-serif);font-size:13.5px;line-height:1.8}
/* 对话里已经有大框时，功能轮代码块那几条（@SH@:has(.sz-hud) …:has(.sz-fnh) pre）权重高，这里加 !important 压住 */
.rili-markdown-renderer .rj .rj-seal :is(pre,code){color:#2b2219!important;background-color:transparent!important;font-family:var(--rj-serif)!important;text-shadow:none!important}
.rili-markdown-renderer .rj .rj-seal pre{background:rgb(255 252 244 / .62)!important;box-shadow:inset 0 0 0 1px rgb(184 154 94 / .55)!important;padding:12px 14px!important;border-radius:4px!important}
.rj-fill{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:4px 10px;margin-top:10px}
.rj-fill span{display:inline-block;padding:4px 16px;border-radius:999px;border:1px solid rgb(155 29 46 / .6);color:var(--rj-red);font-size:13px;letter-spacing:.12em;cursor:pointer;background:rgb(255 255 255 / .35);transition:background .15s}
.rj-fill span:hover{background:rgb(155 29 46 / .1)}
.rj-fill small{font-size:11.5px;color:#8a7a62}
.rj-aft:not(:has(*)){display:none}
.rj-aft{margin:0 22px 8px;font-size:13px;color:var(--rj-ink2)}
.rj-aft p{margin:0 0 .4em}
/* 门扉：黑石门框嵌金，两扇门一道缝里透出光；悬上去门往里开一点。次一点的“哪里不对”是一行字钮 */
.rj-door{display:flex;flex-direction:column;align-items:center;gap:8px;padding:18px 16px 22px;
  background:radial-gradient(60% 100% at 50% 100%, rgb(95 224 207 / .1), transparent 70%), linear-gradient(180deg, var(--rj-night), #07070b)}
.rj-go{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;width:min(100%, 216px);height:158px;padding-top:26px;cursor:pointer;
  border-radius:108px 108px 6px 6px/96px 96px 6px 6px;border:2px solid var(--rj-gold);perspective:420px;
  background:radial-gradient(40% 70% at 50% 60%, rgb(240 215 154 / .35), transparent 70%), #f3e9cf;
  box-shadow:0 0 0 4px #15131c, 0 0 0 5px rgb(212 176 106 / .45), 0 0 26px rgb(240 215 154 / .25), inset 0 0 18px rgb(240 215 154 / .7)}
.rj-go i{position:absolute;top:0;bottom:0;width:50%;transition:transform .5s cubic-bezier(.2,.7,.2,1);
  background:repeating-linear-gradient(90deg, transparent 0 22px, rgb(0 0 0 / .22) 22px 23px), linear-gradient(180deg, #2a2230, #17131d);
  box-shadow:inset 0 0 0 1px rgb(212 176 106 / .35), inset 0 0 0 6px rgb(0 0 0 / .25)}
.rj-lf{left:0;border-radius:106px 0 0 4px/94px 0 0 4px;transform-origin:left center}
.rj-rt{right:0;border-radius:0 106px 4px 0/0 94px 4px 0;transform-origin:right center}
.rj-lf::after,.rj-rt::after{content:"";position:absolute;top:76%;width:7px;height:7px;border-radius:50%;background:var(--rj-gold);box-shadow:0 0 6px var(--rj-gold2)}
.rj-lf::after{right:9px}.rj-rt::after{left:9px}
.rj-go b,.rj-go small{position:relative;z-index:1;pointer-events:none;text-shadow:0 1px 6px #000, 0 0 12px rgb(0 0 0 / .7)}
.rj-go b{font-size:21px;font-weight:700;letter-spacing:.3em;padding-left:.3em;color:#fbf3dc}
.rj-go small{font-size:11.5px;letter-spacing:.4em;padding-left:.4em;color:var(--rj-gold2)}
.rj-go:hover .rj-lf,.rj-go:focus-visible .rj-lf{transform:rotateY(38deg)}
.rj-go:hover .rj-rt,.rj-go:focus-visible .rj-rt{transform:rotateY(-38deg)}
.rj-go:active .rj-lf{transform:rotateY(60deg)}.rj-go:active .rj-rt{transform:rotateY(-60deg)}
.rj-fix{font-size:13px;letter-spacing:.12em;color:var(--rj-gold2);border-bottom:1px dashed rgb(212 176 106 / .55);cursor:pointer;padding:2px 2px 1px}
.rj-fix:hover{color:#fff4d6;border-bottom-style:solid}
.rj-tip{font-size:11px;letter-spacing:.08em;color:#8f887c}
@media (hover:none){.rj-lf{transform:rotateY(14deg)}.rj-rt{transform:rotateY(-14deg)}}
@media (max-width:639px){
  .rj{border-radius:12px;font-size:14.5px}
  .rj-hd .rj-art,.rj:not(:has(.rj-hd)):not(.rj-re)::before{aspect-ratio:16/9;background-size:auto 150%;background-position:50% 36%}
  .rj-hd-t{margin-top:-24px}
  .rj-hd-t b{font-size:25px}
  .rj-hd-t b::before,.rj-hd-t b::after{width:26px;margin:0 8px}
  .rj-hd-m{font-size:11.5px}
  .rj-hd-m em{padding:0 7px}
  .rj-op{padding:18px 18px 24px}
  .rj-op p{font-size:14.5px;letter-spacing:.08em;line-height:1.95}
  .rj-led{margin:0 10px 16px;padding:46px 14px 28px 40px}
  .rj-led{background:linear-gradient(90deg, transparent 25px, rgb(155 29 46 / .45) 25px 26px, transparent 26px 29px, rgb(155 29 46 / .45) 29px 30px, transparent 30px),
    repeating-linear-gradient(180deg, transparent 0 27px, rgb(110 95 76 / .17) 27px 28px) 0 46px/100% calc(100% - 46px) no-repeat,
    radial-gradient(120% 80% at 50% 0%, #f6efdd, var(--rj-paper) 60%, #e2d4b6)}
  .rj-led-h{left:40px}
  .rj-stamp{width:48px;height:48px;right:10px}
  .rj-seal{margin:26px 10px 14px;padding:32px 10px 14px}
  .rili-markdown-renderer .rj .rj-seal pre{font-size:13px;padding:10px 10px;max-height:46dvh}
}
'''


def css():
    return CSS.replace('@ART@', ART)
