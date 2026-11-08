# 大框版的展开正则（状态栏方向稿第四版的样张，不进卡）。用法：python3 -I -X utf8 make_rules_frame.py 输出.json
# 路子同第二版：只认 §底座 打头的回复，一条规则只吃自己那一行，行尾留 ⓔ，最后并成一整块 HTML（头一个字是 <details）。
# 第四版的结构：一条回复里有一页手札（正文和分支）和七页模块（面板、伟业、背包、同行、见闻、记忆、战斗），
# 末尾一排页签（手札加七个）。页签是全页同一组单选钮，开哪一页由样式决定；只有最新一条回复的页签露出来。
# 11-04 用户要各模块像游戏界面：面板看得到每个部位的装备、悬停看属性，背包每样东西悬停看详情。记法改了三样，一件一行，才有东西写进悬停里：
#   §装备｜部位｜名｜品阶｜类型·修正·词条｜一句       空的部位写 §装备｜副手｜空置
#   §物品｜类别｜名×数｜品阶｜类型｜一句（是什么、效果与数）
#   §能力｜类｜名｜稀有度｜阶·修正·数｜一句
# 悬停和点一下是同一张卡：一件东西一颗单选钮，点了留着，手机上靠点；有 hover 的设备上悬停就出。
# 另外：§面板｜旅印 从原来的 §面板｜装备 分出来（旅印｜巴尔 n 索恩 n 便士 n｜信用｜权限），§伟业｜装备 不要了，着装每轮写全五栏（部位的卡读它）。
# 11-04 第二回：页上不留竖线隔开的一串字。AI 写的还是竖线（记法不变），展开时一格一格拆开：
#   一行几段的（可接、线索、日报、装备、命星……）先包一层、写成 §字 内容+行尾记号，下面「拆行」那两条一次拆成几行（记号 ⓛ 认竖线，ⓚ 认带空格的竖线，
#   ⓜ 还认分号和句号，ⓝ 认顿号；括号里的不拆），再一行一条规则。漏网的竖线最后换成中点。
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
import era_vars
MAP = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'map_data.json'), encoding='utf-8'))
R = []
def rule(name, rx, rep):
    R.append({"name": name, "regex": rx, "replaceString": rep, "enabled": True, "messageRole": "assistant", "applyMode": "front-end"})
G = r'(?=[\s\S]*ⓩ)'
BACK = '<label class="sz-x"><input type="radio" name="sz-tab">返回手札</label>'
# ---- 预处理（同第二版）----
# 模型偶尔把整条回复包进代码围栏，拆掉。§底座 前头多写的字（迁移轮那一行 ✅）照常排成段，不算写坏
rule('去外层围栏', r'/^\s*```[a-zA-Z]*\s*\n(§底座｜[\s\S]*)\n```\s*$/', '$1')
rule('去外层围栏·没收尾', r'/^\s*```[a-zA-Z]*\s*\n(§底座｜)/', '$1')
# 11-08 底层推演加强：回复最后一行 §预载 是给世界书看的钥匙，玩家不用看，显示时拿掉（发给模型、存库的照旧留着）
rule('预载藏起来', r'/^§预载｜[^\n]*\n?/gm', '')
rule('帧记号', r'/^([^§]*§底座｜[\s\S]*)$/', '$1\nⓩ')
# 月银纪的局：末尾留一个记号，最后那一批字眼照这一纪换（ERA_LABELS），换完拿掉
rule('月银记号', r'/^([^§]*§底座｜纪元：月银纪\d[\s\S]*)ⓩ\s*$/', '$1Ⓜⓩ')
rule('纷争记号', r'/^([^§]*§底座｜纪元：(?:纷争纪(?:\d|元年)|山铜纪元年)[\s\S]*)ⓩ\s*$/', '$1Ⓢⓩ')   # 11-08 纷争纪元年（那一夜所在的归寂月，常驻叫模型这么写）也认
rule('山铜记号', r'/^([^§]*§底座｜纪元：(?:山铜纪\d|迷宫纪元年)[\s\S]*)ⓩ\s*$/', '$1Ⓑⓩ')
# 功能命令轮（存档、差评、校准……）：只留一道小题，底下原样交给 Markdown，存档的代码块才复制得了。不带 sz-hud，上一条回复的页签和整页照旧；帧记号拿掉，往下的段落规则就不碰它
rule('功能轮', r'/^(?![\s\S]*\n§正文｜)[^§]*§底座｜[\s\S]*\n§功能｜([^\n]{1,30})\n?([\s\S]*)\n[ⓂⓈⒷ]?ⓩ\s*$/', '<div class="sz-fnh"><i></i><b>$1</b></div>\n\n$2')
# ---- 地图页（只有迷宫纪）：放在最后一页之后，开页先收上一页，末尾由「收卷」收。平台不跑脚本，缩放、点位、移动全靠单选钮：
#   sz-mz 三档倍数；sz-mp 一组里有地标和一张 10×6 的底格，点地标出卡片并移到中间，点空白处把那一格移到中间，「我在哪」回到玩家身上。底图写在样式里，翻到这一页才下载
MAP_CELL = '<label><input type="radio" name="sz-mp"></label>'
MAP_PIN = ''.join('<label class="m" data-l="%s"><input type="radio" name="sz-mp"></label>' % l['n'] for l in MAP['lands'])
MAP_ZB = ''.join('<label class="mzb mz-%d"><input type="radio" name="sz-mz"><b>%s</b></label>' % (i + 1, t) for i, t in enumerate(['全图', '放大', '细看']))
MAP_LEG = ''.join('<span data-z="%s"><i></i>%s</span>' % z for z in [('center', '中央'), ('east', '东陆'), ('west', '西陆'), ('old', '古老种族'), ('polar', '极地沙海'), ('town', '迷宫城与镇'), ('geo', '山川水系')])
MAP_HTML = ('</ol></details></div></div></div></div></section><section class="sz-page sz-pane p-map"><div class="sz-pane-head"><i></i><b>大陆全图</b>' + BACK + '</div><div class="sz-pane-body">'
            '<div class="sz-map" data-loc="$2"><div class="mwhere"><small>此刻在</small><b>$2</b></div>'
            '<div class="mv"><div class="mi"><div class="mg">' + MAP_CELL * 60 + '</div>' + MAP_PIN + '<i class="mhere"><b>你在这里</b></i></div>'
            '<div class="mz">' + MAP_ZB + '<label class="mzb mme"><input type="radio" name="sz-mp"><b>我在哪</b></label></div></div>'
            '<div class="ml">' + MAP_LEG + '</div>'
            '<div class="mc"><i class="mc-a"></i><span class="mc-t"><b class="mc-n"></b><small class="mc-r"></small><em class="mc-lv"></em><span class="mc-d"></span></span></div></div>')
rule('地图页', r'/^([^§]*§底座｜(?:纪元：)?迷宫纪[^\s\n]{0,44} · \d{1,2}[:：]\d{2}\s?[^\n·]{0,20}· ((?:[^\s"]| (?!· )){1,60}) · [\s\S]*)\n[ⓂⓈ]?ⓩ\s*$/', '$1\n' + MAP_HTML + 'ⓔ\nⓩ')
rule('去回车', r'/\r/g', '')
rule('去行首空白', r'/^[ \t　]+' + G + '/gm', '')
rule('记录行的半角竖线', r'/^(§[^\n|]{1,12})\|' + G + '/gm', '$1｜')
R.append({'name': '战斗·空行', 'regex': r'/^§(?:战斗|首领|史诗|史诗势|史诗况|敌情|战况)｜(?:无|暂无|没有|不出|未开战|无战斗|非战斗)[ 。]*$\n?/gm', 'replaceString': '', 'enabled': True, 'messageRole': 'assistant', 'applyMode': 'all'})
rule('记录行的尖括号', r'/^(§[^\n<]{0,400})<' + G + '/gm', '$1＜')
# 记忆页的统计：计数器只认排在被数的东西后面的元素，所以这一行放在页尾，样式再挪到页头
rule('记忆尾', r'/^(§记忆｜[^\n]*)$(?![\s\S]*^§记忆｜)/m', '$1\n§记忆统计')
# ---- 头：一块地名牌。钟盘（一圈二十四时，亮点走到几点，正中是钟点）、地名一段一段、纪年、季节、月日、时段；
# 最新一条底下还有主线（ⓠ，读见闻的在办）、Boss 条（ⓨ，史诗战才有）、三条（ⓑ）。旧回复只留一行。点开是推演底座 ----
HEAD = ('<details class="sz-hud"><summary class="sz-head"><i class="sz-dial"><i></i>%s</i><span class="sz-sub"><span class="sz-place"><b>%s</b></span>'
        '<span class="sz-dl1"><span class="sz-year">%s</span>%s</span>ⓠ</span>ⓨⓑ<span class="sz-more">推演</span></summary><div class="sz-hud-body">')
rule('底座加环境',
     r'/^§底座｜(?:纪元：)?((([^\s·\n]{3,14})(·[^\s\n]{1,40}|)) · (\d{1,2}[:：]\d{2})\s?([^\n·]{0,20})· ((?:[^\s]| (?!· )){1,60}) · ((?:[^\s]| (?!· )){1,60}) · 防抢话[ ：:]*(开|关)[^\s·]{0,2} · 档位[ ：:]*([^\s\n]{1,6}))\s*\n§环境｜([^｜\n]{1,60})｜?([^\n]*)$/m',
     HEAD % ('<span class="sz-time">$5</span>', '$7', '$3', '<span class="sz-date">$4</span><span class="sz-tod">$6</span>') +
     '<div class="sz-grid"><div><b>日期</b>$2</div><div><b>时辰</b>$5 $6 · $12</div><div><b>天气</b>$11</div><div><b>地点</b>$7</div><div><b>潮汐</b>$8</div><div><b>档位</b>$10 · 防抢话 $9</div></div>ⓔ')
rule('底座单行', r'/^§底座｜(?:纪元：)?([^\n]{4,160})$/m', HEAD % ('', '$1', '', '') + 'ⓔ')
rule('钟点', r'/(<summary class="sz-head">)(?=[^\n]{0,700}<span class="sz-time">(\d{1,2})[:：](\d{2}))/',
     '$1<style>.custom-styles{--sz-on:1;--sz-h:$2;--sz-m:$3}</style>')
# 11-08 四纪进卡：年份也记在记号上（data-y），立绘同一个名字一纪里几页样子不一样的、史诗战同一个对手几场仗不一样的，样式照年份挑。
# 属性选择器比不了大小，所以按位数写：五位数写在 a 后头，四位数写在 b 后头……一位数写在 e 后头，1690 写成 ab1690cde，样式拿前缀认一段年份（four_era_art.py）
Y5 = '(?:(\\d{5})|(\\d{4})|(\\d{3})|(\\d{2})|(\\d))年'
YA = 'a$2b$3c$4d$5e$6'
for cls, rx, ya in [('era-moon', '月银纪' + Y5, YA), ('era-strife', '(?:纷争纪' + Y5 + '|纷争纪元年|山铜纪元年)', YA), ('era-bronze', '(?:山铜纪' + Y5 + '|迷宫纪元年)', YA),
                    ('era-pre', '迷宫纪(?:(1000)|([1-9]\\d\\d)|([1-9]\\d)|([2-9]))年', 'ab$2c$3d$4e$5'),
                    ('era-maze', '迷宫纪(?:([1-9]\\d{4})|(100[1-9]|10[1-9]\\d|1[1-9]\\d\\d|[2-9]\\d{3}))年', 'a$2b$3cde')]:
    rule('纪元·' + cls, r'/(<summary class="sz-head">)(?=[^\n]{0,600}<span class="sz-year">%s)/' % rx, '$1<i class="sz-era %s" data-y="%s"></i><style>%s</style>' % (cls, ya, era_vars.sheet(cls[4:])))
BAR = '<span class="sz-bar %s" style="--v:$%d;--m:%s"><i></i><b>%s</b><em>%s</em><span class="sz-trk"></span></span>'
rule('钟盘', r'/<i class="sz-dial"><i><\/i><span class="sz-time">(\d{1,2})[:：](\d{2})/', '<i class="sz-dial" style="--h:$1;--m:$2"><i></i><span class="sz-time">$1:$2')
rule('地名分段', r'/·(?=[^<\n]*<\/b><\/span><span class="sz-dl1">)/g', '</b><i class="sz-crumb"></i><b>')
rule('季节', r'/<span class="sz-date">·(春|夏|秋|冬)·/', '<span class="sz-date"><i class="sz-sea" data-s="$1">$1</i>')
rule('月日', r'/<span class="sz-date">·/', '<span class="sz-date">')
# 主线：跟在办的当前任务一样。1001 年那一局写 前缀：【任务名】，四纪写 篇名｜主线名
rule('主线·无', r'/ⓠ(?=[\s\S]*§见闻｜在办｜[^\n]*当前任务[ ：:]*(?:无|暂无) *$)/m', '')
rule('主线·前缀', r'/ⓠ(?=[\s\S]*§见闻｜在办｜当前委托[^｜\n]*｜ ?当前任务[ ：:]*([^：｜\n]{1,16})：【([^】\n]{1,30})】([^\n]*))/', '<span class="sz-quest"><small>$1</small><b>$2$3</b></span>')
rule('主线·篇名', r'/ⓠ(?=[\s\S]*§见闻｜在办｜当前委托[^｜\n]*｜ ?当前任务[ ：:]*([^：｜\n]{1,16})｜([^\n]+))/', '<span class="sz-quest"><small>$1</small><b>$2</b></span>')
rule('主线', r'/ⓠ(?=[\s\S]*§见闻｜在办｜当前委托[^｜\n]*｜ ?当前任务[ ：:]*([^\n]+))/', '<span class="sz-quest"><b>$1</b></span>')
rule('主线·没有', r'/ⓠ/', '')
# 史诗战时头上多一道 Boss 条，翻到哪一页都看得见
PIPS = '<span class="sz-pips" data-p="%s" data-t="%s">' + '<i></i>' * 6 + '</span>'
rule('Boss条', r'/ⓨ(?=[\s\S]*§史诗｜([^｜\n]{1,30})｜(?:阶段)? ?([IVX\d]{1,4})\/([IVX\d]{1,4})[\s\S]*§史诗势｜([^｜\n·]{0,8})·(\d{1,3}))/',
     '<span class="sz-bar sz-bbar" style="--v:$5;--m:100"><b>$1</b>' + PIPS % ('$2', '$3') + '<em>$4</em><span class="sz-trk"></span></span>')
rule('Boss条·没有', r'/ⓨ/', '')
rule('三条', r'/ⓑ(?=[\s\S]*§面板｜资源｜HP (\d{1,6})\/(\d{1,6}) MP (\d{1,6})\/(\d{1,6}) SP (\d{1,6})\/(\d{1,6}))/',
     '<span class="sz-bars">' + BAR % ('hp', 1, '$2', 'HP', '$1 / $2') + BAR % ('mp', 3, '$4', 'MP', '$3 / $4') + BAR % ('sp', 5, '$6', 'SP', '$5 / $6') + '</span>')
rule('三条·百分', r'/ⓑ(?=[\s\S]*§面板｜资源｜HP (\d{1,3})% MP (\d{1,3})% SP (\d{1,3})%)/',
     '<span class="sz-bars">' + BAR % ('hp', 1, '100', 'HP', '$1%') + BAR % ('mp', 2, '100', 'MP', '$2%') + BAR % ('sp', 3, '100', 'SP', '$3%') + '</span>')
rule('三条·没有', r'/ⓑ/', '')
rule('推演九行', r'/^§推演｜(\d)｜([^｜\n]{1,8})｜([^\n]*)$/gm', '<div class="sz-f d"><b><i>$1</i>$2</b><span class="sz-dl">ⓔ\n§条 $3ⓛ条\n</span></div>ⓔ')
rule('评定', r'/^§评定｜([^｜\n]{1,8})｜([^\n]*)$/m', '<div class="sz-f d"><b>$1</b><span class="sz-dl">ⓔ\n§条 $2ⓛ条\n</span></div>ⓔ')
rule('功能命令', r'/^§功能｜([^\n]{1,30})$/m', '<div class="sz-f d"><b>功能命令</b><span>$1</span></div>ⓔ')
# ---- 手札这一页 ----
rule('正文开卷', r'/^§正文｜([^\n]{1,120})$/m', '</div></details><div class="sz-page sz-prose">ⓓ<div class="sz-sec"><span>$1</span></div>ⓔ')
rule('篇章题', r'/(<div class="sz-sec"><span>[^<\n]{1,40}<\/span><\/div>ⓔ\s*)([^\n<§｜]{2,10})｜([^\n<§｜]{4,14})\n+([^\n<§｜]{8,80})\n/',
     '$1<div class="sz-qc"><span class="qc-pian">$2</span><b class="qc-ml">$3</b><span class="qc-desc">$4</span></div>ⓔ\n')
# ---- 对话框（11-05）：人物开口单独一行 §话｜名｜表情｜台词。头像按名字 · 前头那一段认（表在 roster.json），表情九种，同义词写在样式里，认不出的算平常。没有图的人留名字头一个字。
# 模型偶尔写成「名：“台词”」单占一段，也收进框里；只写半截的时候（流式）先不出。词尾是说、道、问这些的不算名字。
SAY = '<div class="sz-say" data-portrait="$1" data-em="%s"><i class="sz-face" data-n="$1"></i><div class="sz-say-b"><b class="sz-say-n">$1$2</b><p>%s</p></div></div>ⓔ'
SAYN = r'([^｜\n·（("<>]{1,14})([^｜\n"<>]{0,18})'
rule('话·去引号头', r'/^(§话｜[^｜\n]{1,32}｜(?:[^｜\n]{0,8}｜|))[“"「『]/gm', '$1')
rule('话·去引号尾', r'/^(§话｜[^\n]*)[”"」』]$/gm', '$1')
rule('话', r'/^§话｜' + SAYN + r'｜([^｜\n"<>]{0,8})｜([^｜\n][^\n]*)$/gm', SAY % ('$3', '$4'))
rule('话·没写表情', r'/^§话｜' + SAYN + r'｜([^｜\n]+)$/gm', SAY % ('', '$3'))
rule('话·没写完', r'/^§话｜[^\n]*$/gm', '')
rule('话·冒号', r'/^(?![^：:\n]*[说道问答喊叫笑着写念唱吼骂][：:])([^｜\n·：:“”「」（(，。§<"]{1,8})((?:·[^｜\n：:“”「」（(，。"]{1,10}|))[：:] ?[“「]([^”」\n]{1,400})[”」]$' + G + '/gm', SAY % ('', '$3'))
rule('段落', r'/^(?!§|<|ⓔ|ⓩ)([^\n]+)$' + G + '/gm', '<p>$1</p>ⓔ')
# ---- 正文里的专名（11-05）：悬停或点一下出一张小卡。卡里有的词在 glossary.tsv，规则只包一层，字写在样式里，模型不用写，也不会写错；这一局新起的东西模型写成〔名｜一句话〕。
# 只碰段落和对话框里的字：这时候别的记录还没展开，行尾是 </p>ⓔ 的只有这两样；不碰标签里头的字。这一张表是迷宫纪 1001 的，别的纪（行尾带记号）不认。
IN_P = r'(?![^<>\n]*(?:>|<\/span>|<\/b>|<i ))(?=[^\n]*<\/p>(?:<\/div><\/div>)?ⓔ$)'
rule('名词·现编', r'/〔([^｜〔〕\n"<>]{1,16})｜([^〔〕\n"<>]{1,160})〕' + IN_P + '/gm', '<span class="sz-t new" tabindex="0">$1<i class="sz-tip" data-t="$1" data-g="$2"></i></span>')
rule('名词·现编·光名', r'/〔([^｜〔〕\n"<>]{1,16})〕' + IN_P + '/gm', '$1')
GLOSS = sorted((l.rstrip('\r\n').split('\t') for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glossary.tsv'), encoding='utf-8') if l.strip() and not l.startswith('#')), key=lambda g: -len(g[0]))
_terms = [g[0] + (g[3] if len(g) > 3 else '') for g in GLOSS]
_tail = IN_P + r'(?=[\s\S]*\nⓩ)/gm'
while _terms:
    _n = 0
    _len = 0
    while _n < len(_terms) and _len + len(_terms[_n]) + 1 < 3900:
        _len += len(_terms[_n]) + 1
        _n += 1
    rule('名词·表', '/(' + '|'.join(_terms[:_n]) + ')' + _tail, '<span class="sz-t" tabindex="0">$1<i class="sz-tip" data-t="$1"></i></span>')
    _terms = _terms[_n:]
rule('分支开头', r'/^§分支｜/m', '<div class="sz-choices"><ol>§分支｜')
rule('分支·自定义', r'/§分支｜(自定义行动[^\n]{0,80})/g', '<li class="sz-free"><span>$1</span></li>ⓔ')
rule('分支·可点', r'/^§分支｜([^\n"<]{1,300})$/gm', '<li data-action="set-textinput" data-value="$1"><span>$1</span></li>ⓔ')
rule('分支·带引号', r'/§分支｜([^\n]{1,300})/g', '<li><span>$1</span></li>ⓔ')

# ---- 七页模块，先把页开好：开页时收上一页（多出来的收尾符平台会忽略） ----
CLOSE = '</ol></details></div></div></div></div></section>'
def opener(names, key, title, extra=''):
    alt = names if isinstance(names, str) else '(?:' + '|'.join(names) + ')'
    rule(key + '开页', r'/^§(%s)｜/m' % alt,
         CLOSE + '<section class="sz-page sz-pane p-%s"><div class="sz-pane-head"><i></i><b>%s</b>%s</div><div class="sz-pane-body">%s§$1｜' % (key, title, BACK, extra))
SLOTS = ['主手', '甲', '外层', '内层', '副手', '配饰', '饰品', '足']
# 容貌和姿态：点那个人脚下的小牌，右边这一栏换成档案（ⓐ 那里，下面几条把记录挪进来）。在页里排开，不叠在别的东西上
DOLL = ('<div class="sz-doll"><i class="sz-doll-ring"></i><i class="sz-doll-fig"></i>' +
        ''.join('<span class="sz-sk" data-s="%s"><i class="sz-ic"></i><small>%s</small></span>' % (s, s) for s in SLOTS) +
        '<label class="sz-arch-t"><input type="checkbox"><span></span></label></div><div class="sz-arch">ⓐ</div>')
CATS = [('未装备', '备用'), ('消耗', '消耗'), ('贵重', '贵重'), ('材料', '材料'), ('不可丢弃', '绑定')]
BAGTOP = ('<div class="sz-bagtop">ⓒⓦ</div><div class="sz-filter"><label data-f="全部"><input type="radio" name="sz-fc"><i class="sz-ic"></i><b>全部</b></label>' +
          ''.join('<label data-f="%s"><input type="radio" name="sz-fc"><i class="sz-ic"></i><b>%s</b></label>' % c for c in CATS) +
          '</div><div class="sz-gridit">')
TIERS = ['启源', '共鸣', '灵格', '极境', '英雄', '传奇', '凡极']
ABC = ['命星', 'Art', 'Passive', 'Active', 'Skill', '职业能力']
# 伟业：七境一条路、目标、职业，底下一本技能书。上头一排书签，一次翻开一类；左页一枚一枚，右页是选中那一枚
DEEDTOP = ('<div class="sz-path">' + ''.join('<i data-t="%s"><b>%s</b></i>' % (t, t) for t in TIERS) + '</div>ⓖⓡⓙ<div class="sz-book"><div class="sz-marks">' +
           ''.join('<label class="sz-cat" data-c="%s"><input type="radio" name="sz-ac"><i></i><b>%s</b></label>' % (c, c) for c in ABC) +
           '</div><div class="sz-abs"><b class="sz-chap"></b>')
opener('战斗', 'war', '交战')
opener(['首领', '史诗'], 'war', '史诗战')
opener('面板', 'panel', '冒险者面板', DOLL)
opener(['伟业', '能力'], 'deed', '成长与伟业', DEEDTOP)
opener(['背包', '物品'], 'bag', '背包与仓库', BAGTOP)
opener('见闻', 'news', '冒险见闻')
opener('记忆', 'mem', '记忆')
rule('同行开页', r'/^§角色｜/m',
     CLOSE + '<section class="sz-page sz-pane p-party"><div class="sz-pane-head"><i></i><b>同行与在场</b>%s</div><div class="sz-pane-body"><div class="sz-npcs"><div hidden><div>§角色｜' % BACK)
# 背包页头的钱和负重在面板那一行，趁它还没展开先抄过去
# 钱的三格：迷宫纪写巴尔、索恩、便士，月银纪 8081 年以后写金币、银币、铜币，以前世上没有通行的钱，写金、银、铜，是秤上的折算（月银纪·钱与兑那一条）
COIN_NAMES = [('巴尔', '索恩', '便士'), ('金币', '银币', '铜币'), ('金', '银', '铜')]
def coins(n):
    return '<span class="sz-coins"><i class="c-b"><b>%s</b>$2</i><i class="c-s"><b>%s</b>$3</i><i class="c-p"><b>%s</b>$4</i></span>' % n
for n in COIN_NAMES:
    rule('背包·钱·' + n[0], r'/(§面板｜旅印｜[^｜\n]{0,20}｜%s (\d{1,9}) %s (\d{1,9}) %s (\d{1,9})[\s\S]*)ⓒ/' % n, '$1' + coins(n))
rule('背包·钱没有', r'/ⓒ/', '')
rule('背包·负重', r'/(§面板｜资源｜[^\n]{0,80}负重 (\d{1,6})\/(\d{1,6}) ?kg[\s\S]*)ⓦ/', '$1<span class="sz-bar wt" style="--v:$2;--m:$3"><b>负重</b><em>$2 / $3 kg</em><span class="sz-trk"></span></span>')
rule('背包·负重没有', r'/ⓦ/', '')
# 伟业页头那一块目标也在页里，放到路径底下
GOAL = ('<div class="sz-goal" data-t="$2"><span class="g-to"><small>下一境</small><b>$2</b></span><span><small>门槛</small><b>$3</b></span><span><small>命路</small><b>$4</b></span>'
        '<span><small>蓄势</small><b>$5</b></span><span><small>伟业簿</small><b>$6</b></span><span><small>冠名</small><b>$7</b></span><span><small>候选称号</small><b>$8</b></span></div>')
rule('伟业·目标', r'/ⓖ([\s\S]*)§伟业｜伟业｜([^｜\n]{1,16})｜([^｜\n]{0,60})｜([^｜\n]{0,40})｜蓄势 ([^｜\n]{0,20})｜伟业簿 ([^｜\n]*)｜破格铸史冠名 ([^｜\n]{0,60})｜候选称号 ([^\n]*)/',
     GOAL + '$1ⓔ')
rule('伟业·目标没有', r'/ⓖ/', '')
# 月银纪拿兽量人，说一个人厉害，说他斩过什么：§伟业｜斩过｜雷鬃狼（共鸣兽）｜焰鬃狼×7（共鸣兽）
rule('伟业·斩过', r'/ⓡ([\s\S]*)§伟业｜斩过｜([^\n]*)/', '<div class="sz-slain"><small>斩过</small><div class="sz-kills">ⓔ\n§斩 $2ⓛ斩\n</div></div>$1ⓔ')
rule('伟业·斩过没有', r'/ⓡ/', '')
rule('伟业·职业',r'/ⓙ([\s\S]*)§伟业｜职业｜([^｜\n]{0,60})｜([^｜\n]{0,60})｜([^\n]*)/',
     '<div class="sz-f sz-job" data-k="职业"><span><small>职业</small><b>$2</b></span><span><small>评定</small><b>$3</b></span><span><small>进阶</small><b>$4</b></span></div>$1ⓔ')
rule('伟业·职业·简',r'/ⓙ([\s\S]*)§伟业｜职业｜([^｜\n]{0,60})$/m', '<div class="sz-f sz-job" data-k="职业"><span><small>职业</small><b>$2</b></span></div>$1ⓔ')
rule('伟业·职业没有', r'/ⓙ/', '')
# 入场卡：开战那一轮，手札页头上亮一下名号
rule('入场卡', r'/ⓓ([\s\S]*)§首领｜([^｜\n]{1,30})｜([^\n]*)/', '<div class="sz-bintro"><small>BOSS ENCOUNTER</small><b>$2</b><span>$3</span></div>$1ⓔ')
rule('入场卡·没有', r'/ⓓ/', '')

# ---- 一件东西：一格（或一个部位）加一张卡 ----
def tip(name, sub, stat, body, group):
    return ('<span class="sz-tip"><span class="sz-tip-in"><span class="sz-tip-h"><i class="sz-ic"></i><b>%s</b><small>%s</small></span>%s%s'
            '<label class="sz-tip-x"><input type="radio" name="%s"></label></span></span>') % (
        name, sub, '<span class="sz-tip-s">%s</span>' % stat if stat else '', '<span class="sz-tip-b">%s</span>' % body if body else '', group)
def slot(part, q, name, sub, stat, body, cls=''):
    return ('<span class="sz-it sz-sl%s" data-s="%s" data-q="%s" data-n="%s"><label class="sz-face"><input type="radio" name="sz-sl"><i class="sz-ic"></i></label><small class="sz-part">%s</small>%s</span>' %
            (cls, part, q, name, part, tip(name, sub, stat, body, 'sz-sl')))
# 几格小字：格名在上、值在下，w 占满一排
def kv(*cells):
    return '<div class="sz-kv">' + ''.join('<i%s><small>%s</small>%s</i>' % (' class="w"' if w else '', k, v) for k, v, w in cells) + '</div>'
CHARM = '<div class="sz-charm" data-c="%s"><em>%s</em><span>%s</span></div>'
F = '([^｜\\n]*)'
# ---- 面板：档案那一栏 ----
rule('容貌·去空杯', r'/(§面板｜容貌｜[^\n]*) · -(?=｜)/', '$1')
rule('档案·容貌', r'/ⓐ([\s\S]*)§面板｜容貌｜' + '｜'.join([F] * 6) + '｜评＝' + F + '｜魅力＝([^·\\n]{1,4})·([^\\n]*)/',
     '<b class="sz-ht">容貌</b>' + kv(('发', '$2', 0), ('瞳', '$3', 0), ('肤', '$4', 0), ('体型', '$6', 0), ('身材', '$5', 1), ('特征', '$7', 1)) +
     CHARM % ('$9', '$9', '$10') + '<span class="sz-eval">$8</span>ⓐ$1ⓔ')
rule('档案·容貌·别的', r'/ⓐ([\s\S]*)§面板｜容貌｜([^\n]*)/', '<b class="sz-ht">容貌</b><span class="sz-arct">$2</span>ⓐ$1ⓔ')
rule('档案·姿态', r'/ⓐ([\s\S]*)§面板｜姿态｜' + F + '｜' + F + '｜' + F + '｜([^\\n]*)/',
     '<b class="sz-ht">姿态</b>' + kv(('在做', '$2', 1), ('身姿', '$3', 0), ('手里', '$4', 0), ('朝向', '$5', 1)) + 'ⓐ$1ⓔ')
rule('档案·姿态·别的', r'/ⓐ([\s\S]*)§面板｜姿态｜([^\n]*)/', '<b class="sz-ht">姿态</b><span class="sz-arct">$2</span>ⓐ$1ⓔ')
rule('档案·此刻', r'/ⓐ([\s\S]*§面板｜着装｜[^｜\n]*｜[^｜\n]*｜[^｜\n]*｜[^｜\n]*｜)(?:此刻状态)?[(（]?([^)）\n]*)[)）]?$/m',
     kv(('身上', '$2', 1)) + 'ⓐ$1无')
rule('档案·收', r'/ⓐ/', '')
# ---- 面板 ----
rule('面板·身份', r'/§面板｜身份｜([^｜\n]{1,20})｜([^｜\n]{0,30})｜([^｜\n]{0,40})｜([^｜\n]{0,8})｜([^｜\n]{0,60})｜([^\n]*)/',
     '<div class="sz-f sz-idc" data-k="身份"><b class="sz-who">$1</b><span class="sz-tags"><i>$2</i><i>$3</i><i>$4</i><i class="vow">$5</i><i>$6</i></span></div>ⓔ')
rule('面板·着装', r'/§面板｜着装｜([^｜\n"]{0,120})｜([^｜\n"]{0,120})｜([^｜\n"]{0,120})｜([^｜\n"]{0,120})｜([^\n]*)/',
     ''.join(slot(p, '着装', '$%d' % k, p + ' · 着装', '', '', ' sz-cl') for p, k in [('外层', 1), ('内层', 2), ('足', 3), ('配饰', 4)]) + 'ⓔ')
rule('装备', r'/§装备｜([^｜\n"]{1,6})｜([^｜\n"]{1,30})｜([^｜\n"]{0,8})｜([^｜\n]{0,50})｜([^\n]*)/g',
     slot('$1', '$3', '$2', '$1 · $3', '$4', '$5') + 'ⓔ')
rule('装备·四栏', r'/§装备｜([^｜\n"]{1,6})｜([^｜\n"]{1,30})｜([^｜\n"]{0,8})｜([^\n]*)$/gm', slot('$1', '$3', '$2', '$1 · $3', '', '$4') + 'ⓔ')
rule('装备·三栏', r'/§装备｜([^｜\n"]{1,6})｜([^｜\n"]{1,30})｜([^｜\n"]{0,8})$/gm', slot('$1', '$3', '$2', '$1 · $3', '', '') + 'ⓔ')
rule('装备·只有名', r'/§装备｜([^｜\n"]{1,6})｜(?!空置|无|暂无)([^｜\n"]{1,30})$/gm', slot('$1', '', '$2', '$1', '', '') + 'ⓔ')
rule('装备·空', r'/§装备｜[^\n]*/g', 'ⓔ')
BX = '<span class="sz-bar %s" style="--v:$%d;--m:$%d"><b>%s</b><em>$%d / $%d</em><span class="sz-trk"></span></span>'
LVB = '<div class="sz-f sz-lv" data-k="位阶"><span class="sz-lvl"><small>LVL</small><b>$1</b></span><span class="sz-lvm"><b class="sz-tier">$2</b>' + BX % ('ex', 3, 4, 'EXP', 3, 4)
rule('面板·位阶', r'/§面板｜位阶｜LVL (\d{1,3}) ([^｜\n]{1,20})｜EXP (?:EXP )?(\d{1,9})\/(\d{1,9})｜蓄势 (\d{1,6})\/(\d{1,6})[^\n]{0,20}/',
     LVB + BX % ('xu', 5, 6, '蓄势', 5, 6) + '</span></div>ⓔ')
rule('面板·位阶·别的', r'/§面板｜位阶｜LVL (\d{1,3}) ([^｜\n]{1,20})｜EXP (?:EXP )?(\d{1,9})\/(\d{1,9})｜([^\n]{0,40})/',
     LVB + '<small class="sz-lvn">$5</small></span></div>ⓔ')
CH4 = '<span class="sz-chips"><i>$%d</i><i>$%d</i><i>$%d</i><i>$%d</i></span>'
F4 = '｜([^｜\n]{0,40})｜([^｜\n]{0,40})｜([^｜\n]{0,40})｜([^\n]*)'
RB = '<span class="sz-bar %s" style="--v:$%d;--m:$%d"><b>%s</b><em>$%d / $%d</em><span class="sz-trk"></span></span>'
rule('面板·资源', r'/§面板｜资源｜HP (\d{1,6})\/(\d{1,6}) MP (\d{1,6})\/(\d{1,6}) SP (\d{1,6})\/(\d{1,6}) 架势 (\d{1,6})\/(\d{1,6})' + F4 + '/',
     '<div class="sz-f sz-res" data-k="资源"><span class="sz-res-bars">' + RB % ('hp', 1, 2, 'HP', 1, 2) + RB % ('mp', 3, 4, 'MP', 3, 4) + RB % ('sp', 5, 6, 'SP', 5, 6) + RB % ('st', 7, 8, '架势', 7, 8) + '</span>' + CH4 % (9, 10, 11, 12) + '</div>ⓔ')
RP = '<span class="sz-bar %s" style="--v:$%d;--m:100"><b>%s</b><em>$%d%%</em><span class="sz-trk"></span></span>'
rule('面板·资源·百分', r'/§面板｜资源｜HP (\d{1,3})% MP (\d{1,3})% SP (\d{1,3})% 架势 (\d{1,3})%' + F4 + '/',
     '<div class="sz-f sz-res" data-k="资源"><span class="sz-res-bars">' + RP % ('hp', 1, 'HP', 1) + RP % ('mp', 2, 'MP', 2) + RP % ('sp', 3, 'SP', 3) + RP % ('st', 4, '架势', 4) + '</span>' + CH4 % (5, 6, 7, 8) + '</div>ⓔ')
CELL = '([A-Z]{2,4}) (\\d{1,5})([^｜\\n]{0,30})'
def six(base):
    """六维的盘和六个数；base 是第一格前面已经有几组"""
    out = ''.join('<i tabindex="0"><b>$%d</b><strong>$%d</strong><small>$%d</small></i>' % (base + 3 * k + 1, base + 3 * k + 2, base + 3 * k + 3) for k in range(6))
    av = ';'.join('--a%d:$%d' % (k + 1, base + 3 * k + 2) for k in range(6))
    return '<div class="sz-f sz-six" data-k="六维" style="%s"><span class="sz-radar"><i class="r-g"></i><i class="r-v"></i></span><span class="sz-cells">%s</span></div>' % (av, out)
rule('面板·六维', r'/§面板｜六维｜' + '｜'.join([CELL] * 6) + '/', six(0) + 'ⓔ')
rule('面板·攻防', r'/§面板｜攻防｜ATK (\d{1,6}) · MAG ([^ ·｜\n]{1,6}) · PV (\d{1,6}) · DV (\d{1,6})｜([^\n]*)/',
     '<div class="sz-f sz-atk" data-k="攻防"><span class="sz-atks"><i data-a="atk"><b>ATK</b><strong>$1</strong></i><i data-a="mag"><b>MAG</b><strong>$2</strong></i><i data-a="pv"><b>PV</b><strong>$3</strong></i><i data-a="dv"><b>DV</b><strong>$4</strong></i></span><small class="sz-resist">$5</small></div>ⓔ')
rule('面板·攻防·没魔', r'/§面板｜攻防｜ATK (\d{1,6}) · PV (\d{1,6}) · DV (\d{1,6})｜([^\n]*)/',
     '<div class="sz-f sz-atk" data-k="攻防"><span class="sz-atks"><i data-a="atk"><b>ATK</b><strong>$1</strong></i><i data-a="pv"><b>PV</b><strong>$2</strong></i><i data-a="dv"><b>DV</b><strong>$3</strong></i></span><small class="sz-resist">$4</small></div>ⓔ')
rule('面板·命路', r'/§面板｜命路｜(?:命路 )?([^｜\n]{0,40})｜(?:职业 )?([^｜\n]{0,40})(?:｜(?:命星 )?([^\n]*)|)/',
     '<div class="sz-f sz-road" data-k="命路"><span><small>命路</small><b>$1</b></span><span><small>职业</small><b>$2</b></span><span><small>命星</small><b>$3</b></span></div>ⓔ')
# 月银纪没有旅印，名号是诗人唱出来的，唱到第三个国就定了（月银纪·神眷与名望）：旅印一格写无印，后两栏写 传唱 谁在唱｜唱到 第几个国，还没人唱写 传唱 无
for n in COIN_NAMES:
    rule('面板·传唱·' + n[0], r'/§面板｜旅印｜(无印)｜%s (\d{1,9}) %s (\d{1,9}) %s (\d{1,9})｜传唱 ([^｜\n]{0,24})(?:｜唱到 ([^\n]{0,12})|)/' % n,
         '<div class="sz-f sz-seal" data-k="传唱">' + coins(n) + '<span class="sz-song" data-s="$5" data-g="$6"><small>传唱</small><b>$5</b><span class="sz-song-t"><i></i><i></i><i></i></span><em>$6</em></span></div>ⓔ')
# 纷争纪也没有旅印，墙上量一个人，看战报上写过他几回（纷争纪常驻）：后两栏写 战报 哪一段墙的战报｜写过 几回，还没有写 战报 无
for n in COIN_NAMES:
    rule('面板·战报·' + n[0], r'/§面板｜旅印｜(无印)｜%s (\d{1,9}) %s (\d{1,9}) %s (\d{1,9})｜战报 ([^｜\n]{0,24})(?:｜写过 ([^\n]{0,12})|)/' % n,
         '<div class="sz-f sz-seal" data-k="战报">' + coins(n) + '<span class="sz-song sz-disp" data-s="$5"><small>战报</small><b>$5</b><em>写过 $6</em></span></div>ⓔ')
# 山铜纪也没有旅印：行会量一个人看档次，碑上量一个人看他的名字刻在几块碑的背面（山铜纪常驻）。后两栏写 团 团名·档次｜碑 刻过几块，没有团写 团 无，还没有写 碑 一块也没有
for n in COIN_NAMES:
    rule('面板·碑·' + n[0], r'/§面板｜旅印｜(无印)｜%s (\d{1,9}) %s (\d{1,9}) %s (\d{1,9})｜团 ([^｜\n·]{0,24})·?([^｜\n·]{0,8})(?:｜碑 ([^\n]{0,12})|)/' % n,
         '<div class="sz-f sz-seal" data-k="团">' + coins(n) + '<span class="sz-song sz-troop" data-s="$5"><small>团</small><b>$5</b><u>$6</u><em>碑背面 · $7</em></span></div>ⓔ')
for n in COIN_NAMES:
    rule('面板·旅印·' + n[0], r'/§面板｜旅印｜([^｜\n]{0,40})｜%s (\d{1,9}) %s (\d{1,9}) %s (\d{1,9})｜([^｜\n]{0,40})｜([^\n]*)/' % n,
         '<div class="sz-f sz-seal" data-k="旅印"><span class="sz-sealb"><i></i><b>$1</b></span>' + coins(n) + '<span class="sz-tags"><i>$5</i><i>$6</i></span></div>ⓔ')
rule('面板·层级·无', r'/§面板｜层级｜(?:无|暂无)(?=｜|\s*$)[^\n]*/m', 'ⓔ')
rule('面板·层级', r'/§面板｜层级｜([^｜\n]{0,30})｜([^｜\n]{0,30})｜([^｜\n]{0,30})｜([^\n]*)/',
     '<div class="sz-f sz-road sz-floor" data-k="层级"><span><small>所在</small><b>$1</b></span><span><small>层</small><b>$2</b></span><span><small>距安全层</small><b>$3</b></span><span><small>撤离</small><b>$4</b></span></div>ⓔ')
rule('面板·委托空', r'/§面板｜委托｜无[ ｜][^\n]*/', 'ⓔ')
rule('面板·委托', r'/§面板｜委托｜' + F + '｜' + F + '｜' + F + '｜' + F + '｜([^\\n]*)/',
     '<div class="sz-qcard" data-k="在办"><i class="sz-ic"></i><span class="q-n"><small>当前委托</small><b>$1</b></span><em>$2</em>'
     '<span class="q-f"><i><small>风险</small>$3</i><i><small>报酬</small>$4</i><i class="w"><small>失败后果</small>$5</i></span></div>ⓔ')
rule('面板各行', r'/§面板｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-f sz-row" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
# ---- 伟业：能力一个一格，一个一张卡 ----
ABT = ('<span class="sz-it sz-ab" data-c="$1" data-q="$3" data-n="$2"><label class="sz-face"><input type="radio" name="sz-ab"><i class="sz-hx"></i><b class="sz-nm">$2</b></label>%s</span>ⓔ')
rule('能力', r'/§能力｜([^｜\n"]{1,8})｜([^｜\n"]{1,24})｜([^｜\n"]{0,10})｜([^｜\n]{0,40})｜([^\n]*)/g', ABT % tip('$2', '$1 · $3', '$4', '$5', 'sz-ab'))
# 写「无」的不出；少写了一两栏的也落成一枚，别丢
rule('能力·无', r'/§能力｜[^｜\n]{1,8}｜(?:无|暂无|未觉醒)(?=｜|\s*$)[^\n]*/gm', 'ⓔ')
rule('能力·四栏', r'/§能力｜([^｜\n"]{1,8})｜([^｜\n"]{1,24})｜([^｜\n"]{0,10})｜([^｜\n]*)$/gm', ABT % tip('$2', '$1 · $3', '', '$4', 'sz-ab'))
rule('能力·三栏', r'/§能力｜([^｜\n"]{1,8})｜([^｜\n"]{1,24})｜([^｜\n"]{0,10})$/gm', ABT % tip('$2', '$1 · $3', '', '', 'sz-ab'))
rule('能力·空', r'/§能力｜[^\n]*/g', 'ⓔ')
rule('伟业各行', r'/§伟业｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-f sz-row" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
# ---- 背包：一样东西一格 ----
ITT = ('<span class="sz-it sz-cell" data-c="$1" data-q="$%d" data-n="$2"><label class="sz-face"><input type="radio" name="sz-it"><span class="sz-pad"><i class="sz-ic"></i>%s</span><b class="sz-nm">$2</b></label>%s</span>ⓔ')
rule('物品·带数', r'/§物品｜([^｜\n"]{1,8})｜([^｜\n×"]{1,24})×(\d{1,5})｜([^｜\n"]{0,8})｜([^｜\n]{0,24})｜([^\n]*)/g',
     ITT % (4, '<em class="sz-ct">$3</em>', tip('$2', '$4 · $5 · 持有 $3', '', '$6', 'sz-it')))
rule('物品', r'/§物品｜([^｜\n"]{1,8})｜([^｜\n"]{1,24})｜([^｜\n"]{0,8})｜([^｜\n]{0,24})｜([^\n]*)/g',
     ITT % (3, '', tip('$2', '$3 · $4', '', '$5', 'sz-it')))
rule('物品·简', r'/§物品｜[^｜\n]{0,8}｜([^\n]{0,60})/g', '<div class="sz-f sz-row"><span>$1</span></div>ⓔ')
rule('背包各行', r'/§背包｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-f sz-row sz-bagn" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')

# ---- 见闻：一种东西一种样子。写「无」的不出 ----
def nwt(k, title=None):
    return '<b class="sz-nwt"><i class="sz-ic"></i>%s</b>' % (title or k)
rule('MOD', r'/§MOD｜([^｜\n]{1,12})｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-nw sz-card" data-k="MOD"><b class="sz-nwt">$1 · $2</b><span class="sz-arct">$3</span></div>ⓔ')
rule('见闻空', r'/§见闻｜[^｜\n]{1,8}｜(?:无|暂无) *$/gm', 'ⓔ')
rule('在办·都无', r'/§见闻｜在办｜当前委托[ ：:]*(?:无|暂无) ?｜ ?当前任务[ ：:]*(?:无|暂无) *$/m', 'ⓔ')
rule('在办·都无·简', r'/§见闻｜在办｜(?:无|暂无) ?｜ ?(?:无|暂无) *$/m', 'ⓔ')
TKC = '<span class="t-c" data-v="%s"><small>%s</small><b>%s</b></span>'
TKH = '<div class="sz-nw sz-track" data-k="在办"><i class="sz-ic"></i>'
rule('在办·主线', r'/§见闻｜在办｜当前委托[ ：:]*([^｜\n]*)｜ ?当前任务[ ：:]*([^：\n]{1,16})：【([^】\n]{1,30})】([^\n]*)/',
     TKH + TKC % ('$1', '当前委托', '$1') + '<span class="t-c"><small>$2</small><b>$3$4</b></span></div>ⓔ')
rule('在办', r'/§见闻｜在办｜当前委托[ ：:]*([^｜\n]*)｜ ?当前任务[ ：:]*([^\n]*)/', TKH + TKC % ('$1', '当前委托', '$1') + TKC % ('$2', '当前任务', '$2') + '</div>ⓔ')
rule('在办·别的', r'/§见闻｜在办｜([^｜\n]*)｜ ?([^\n]*)/', TKH + TKC % ('$1', '当前委托', '$1') + TKC % ('$2', '当前任务', '$2') + '</div>ⓔ')
rule('日报', r'/§见闻｜日报｜([^：\n]{1,16})：([^\n]*)/', '<div class="sz-nw sz-daily" data-k="日报"><b class="d-t">日报</b>ⓔ\n§报 $2ⓜ报\n<em class="sz-stamp">$1</em></div>ⓔ')
rule('日报·没渠道', r'/§见闻｜日报｜([^\n]*)/', '<div class="sz-nw sz-daily" data-k="日报"><b class="d-t">日报</b>ⓔ\n§报 $1ⓜ报\n</div>ⓔ')
rule('情报', r'/§见闻｜已知情报｜([^\n]*)/', '<div class="sz-nw sz-intel" data-k="已知情报">' + nwt('已知情报') + '<div class="in-b">ⓔ\n§情 $1ⓜ情\n</div></div>ⓔ')
rule('风闻', r'/§见闻｜流言风闻｜([^\n]*)/', '<div class="sz-nw sz-rumor" data-k="流言风闻">' + nwt('流言风闻') + 'ⓔ\n§闻 $1ⓜ闻\n</div>ⓔ')
rule('可接', r'/§见闻｜可接｜([^\n]*)/', '<div class="sz-nw sz-board" data-k="可接">' + nwt('可接', '可接委托') + '<div class="sz-slips">ⓔ\n§接 $1ⓛ接\n</div></div>ⓔ')
rule('线索', r'/§见闻｜线索｜([^\n]*)/', '<div class="sz-nw sz-clue" data-k="线索">' + nwt('线索') + '<div class="sz-notes">ⓔ\n§索 $1ⓜ索\n</div></div>ⓔ')
rule('见闻各行', r'/§见闻｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-nw sz-card" data-k="$1"><b class="sz-nwt">$1</b><span class="sz-arct">$2</span></div>ⓔ')

# ---- 记忆：一类一块、一类一种样子，页头一排数 ----
rule('记忆空', r'/§记忆｜[^｜\n]{1,8}｜(?:无|暂无) *$/gm', 'ⓔ')
rule('记忆空·带箭头', r'/§记忆｜已完成｜(?:无|暂无) → [^\n]*/g', 'ⓔ')
SEP = ' ?[|｜] ?'
rule('记忆·短期', r'/§记忆｜短期｜\[(\d{1,3})\]（([^）\n]{1,60})）([^|｜\n]{0,60})' + SEP + r'(?:核心事件[：:])?([^\n]*)/g',
     '<div class="sz-mm" data-k="短期" style="--n:$1"><i class="m-n">$1</i><span class="m-w"><time>$2</time><small>$3</small></span><span class="m-t">$4</span></div>ⓔ')
rule('记忆·短期·别的', r'/§记忆｜短期｜\[(\d{1,3})\]（([^）\n]{1,60})）([^\n]*)/g',
     '<div class="sz-mm" data-k="短期" style="--n:$1"><i class="m-n">$1</i><span class="m-w"><time>$2</time></span><span class="m-t">$3</span></div>ⓔ')
# 长期和核心一条两三百字，先露三行，点一下展开
rule('记忆·长期核心', r'/§记忆｜(长期|核心)｜\[\d{1,3}\]（([^）\n]{1,60})）([^|｜\n]{0,60})' + SEP + r'([^\n]*)/g',
     '<div class="sz-mm" data-k="$1"><label class="m-fold"><input type="checkbox"><span class="m-w"><time>$2</time><small>$3</small></span><span class="m-t">$4</span></label></div>ⓔ')
rule('记忆·因果', r'/§记忆｜未结因果｜\[([^\]\n]{1,20})\] ?([^|｜\n]{0,30})' + SEP + '([^|｜\\n]{0,120})' + SEP + '([^|｜\\n]{0,40})' + SEP + '([^|｜\\n]{0,20})' + SEP + r'(?:来源事件[：:])?([^\n]*)/g',
     '<div class="sz-mm sz-th" data-k="未结因果"><span class="th-h"><b>$1</b><i>$2</i><em>$5</em></span><span class="m-t">$3</span><span class="th-f"><i><small>期限</small>$4</i><i><small>来源</small>$6</i></span></div>ⓔ')
rule('记忆·修正', r'/§记忆｜修正｜\[([^\]\n]{1,12})\] ?([^|｜\n]{0,30})' + SEP + '([^|｜\\n]{0,80})' + SEP + '([^|｜\\n]{0,60})' + SEP + '([^|｜\\n]{0,80})' + SEP + '([^|｜\\n]{0,30})' + SEP + '([^|｜\\n]{0,30})' + SEP + r'([^\n]{0,16})/g',
     '<div class="sz-mm sz-th" data-k="修正"><span class="th-h"><b>$2</b><i>$1</i><em>$8</em></span><span class="m-t">$3</span><span class="th-f"><i><small>禁止</small>$4</i><i><small>期望写法</small>$5</i><i><small>适用范围</small>$6</i><i><small>来源日期</small>$7</i></span></div>ⓔ')
rule('记忆·已完成', r'/§记忆｜已完成｜([^\n]*)/g', 'ⓔ\n§成 $1ⓚ成')
rule('记忆各行', r'/§记忆｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-mm" data-k="$1"><span class="m-t">$2</span></div>ⓔ')
MTY = ['全部', '核心', '未结因果', '短期', '长期', '已完成', '修正']
rule('记忆统计', r'/^§记忆统计$/m',
     '<div class="sz-mts">' + ''.join('<label class="sz-mt" data-k="%s"><input type="radio" name="sz-mf"><i class="sz-ic"></i><em></em><b>%s</b></label>' % (k, k) for k in MTY) + '</div>' +
     ''.join('<div class="sz-mh" data-k="%s"><i class="sz-ic"></i><b>%s</b><em></em></div>' % (k, k) for k in MTY[1:]) + 'ⓔ')

# ---- 同行：左边一幅立绘（没有图的先留着位子），右边名字、状态、羁绊，底下分页 ----
NT = ['形象', '关系', '属性', '行装', '能力']
NTABS = '<div class="sz-nts">' + ''.join('<label class="sz-nt" data-t="%s"><input type="radio" name="sz-nt"><b>%s</b></label>' % (t, t) for t in NT) + '</div>'
NPC = ('</div></div><div class="sz-npc"%s><label class="sz-av"><input type="radio" name="sz-np"><i data-n="$1"></i><b>$2</b></label>'
       '<div class="sz-npc-b"><div class="sz-por"><i data-n="$1"></i>%s</div><div class="sz-npc-name"><b>$1</b><span>$3</span></div>' + NTABS + 'ⓔ')
WHO = r'/§角色｜(([^｜\n·]{1,12})[^｜\n]{0,20})｜([^｜\n]{1,40})'
# 11-05 立绘换成四套衣着：立绘:短名｜衣着:常服（私服、战斗、正装），样式照 data-o 挪图，认不出的算常服
rule('角色·立绘', WHO + r'｜立绘[:：]([^｜\n·]{1,8})[^｜\n]{0,14}(?:｜衣着[:：]([^｜\n]{1,4})|)/g', NPC % (' data-portrait="$4" data-o="$5"', '<b class="sz-por-t" data-o="$5"></b>'))
rule('角色·名牌', WHO + r'｜名牌(?:｜衣着[:：]([^｜\n]{1,4})|)/g', NPC % (' data-portrait="$2" data-o="$4"', '<b class="sz-por-t" data-o="$4"></b>'))
rule('角色·路人', WHO + r'(?:｜路人)?(?:｜衣着[:：][^｜\n]{1,4}|)$/gm', NPC % (' data-walkon="1"', ''))   # 可选的组里不能有量词，写成带空分支的组
rule('角色签', r'/§角色签｜([^｜\n]{0,60})｜([^｜\n]{0,40})｜([^｜\n]{0,20})｜([^｜\n]{0,30})｜([^｜\n]{0,40})｜([^｜\n]{0,16})$/gm',
     '<div class="sz-npc-tags"><span class="lv" data-v="$3">$3</span><span data-v="$4">$4</span><span data-v="$1">$1</span><span data-v="$2">$2</span><span data-v="$5">$5</span><span class="met" data-v="$6">$6</span></div>ⓔ')
rule('角色话', r'/§角色话｜([^\n]+)/g', '<p class="sz-npc-say">$1</p>ⓔ')
def nc(tab, k, inner):
    return '<div class="sz-nc" data-t="%s" data-k="%s">%s</div>ⓔ' % (tab, k, inner)
# 状态：几条在头上，伤、污染、异常拆成小牌，没有的不出
COND = '<span class="sz-cond">ⓔ\n§况 $%dⓚ况\n</span></div>ⓔ'
NB = '<span class="sz-bar %s" style="--v:$%d;--m:$%d"><b>%s</b><em>$%d / $%d</em><span class="sz-trk"></span></span>'
rule('角色·状态', r'/§角色行｜状态｜HP (\d{1,6})\/(\d{1,6}) MP (\d{1,6})\/(\d{1,6}) SP (\d{1,6})\/(\d{1,6}) 架势 (\d{1,6})\/(\d{1,6}) ?｜? ?([^\n]*)/g',
     '<div class="sz-npc-st"><span class="sz-res-bars">' + NB % ('hp', 1, 2, 'HP', 1, 2) + NB % ('mp', 3, 4, 'MP', 3, 4) + NB % ('sp', 5, 6, 'SP', 5, 6) + NB % ('st', 7, 8, '架势', 7, 8) + '</span>' + COND % 9)
NP = '<span class="sz-bar %s" style="--v:$%d;--m:100"><b>%s</b><em>$%d%%</em><span class="sz-trk"></span></span>'
rule('角色·状态·百分', r'/§角色行｜状态｜HP (\d{1,3})% MP (\d{1,3})% SP (\d{1,3})% 架势 (\d{1,3})% ?｜? ?([^\n]*)/g',
     '<div class="sz-npc-st"><span class="sz-res-bars">' + NP % ('hp', 1, 'HP', 1) + NP % ('mp', 2, 'MP', 2) + NP % ('sp', 3, 'SP', 3) + NP % ('st', 4, '架势', 4) + '</span>' + COND % 5)
# 羁绊：一条粉色的，羁绊任务和协战技两小格
BONDT = '<i></i><b>Lv.$1</b><span>$2</span><em>%s</em><span class="sz-trk"></span><span class="sz-bondx">ⓔ\n§绊 %sⓚ绊\n</span></div>ⓔ'
rule('角色·羁绊', r'/§角色行｜羁绊｜好感 Lv\.(\d{1,2}) ([^｜\n]{1,20}) (\d{1,5})\/(\d{1,5})([^｜\n]{0,12}) ?｜? ?([^\n]*)/g',
     '<div class="sz-bond" style="--v:$3;--m:$4">' + BONDT % ('$3 / $4$5', '$6'))
rule('角色·羁绊·满', r'/§角色行｜羁绊｜好感 Lv\.(\d{1,2}) ([^｜\n]{1,20}) MAX ?｜? ?([^\n]*)/g',
     '<div class="sz-bond" style="--v:1;--m:1">' + BONDT % ('MAX', '$3'))
# 形象页
rule('角色·容貌', r'/§角色行｜容貌｜' + F + '｜' + F + '｜' + F + '｜' + F + r'｜ ?魅力 ([^·\n]{1,4})·([^\n]*)/g',
     nc('形象', '容貌', '<b class="sz-ht">容貌</b>' + kv(('发', '$1', 0), ('瞳', '$2', 0), ('身材', '$3', 1), ('特征', '$4', 1)) + CHARM % ('$5', '$5', '$6')))
rule('角色·着装', r'/§角色行｜着装与姿态｜' + F + '｜' + F + '｜' + F + r'｜([^\n]*)/g',
     nc('形象', '着装', '<b class="sz-ht">此刻</b>' + kv(('穿着', '$1', 1), ('在做', '$2', 1), ('手里', '$3', 0), ('身上', '$4', 0))))
# 属性页：一行里 EXP、六维、攻防连着写，先拆成两行，一条规则放不下这么多量词
rule('角色·属性·拆', r'/(§角色行｜属性｜[^\n]*\))[ ｜]*(ATK [^\n]*)$/gm', '$1\n§角色攻防｜$2')
rule('角色·属性', r'/§角色行｜属性｜EXP (\d{1,9})\/(\d{1,9})｜' + '｜'.join([CELL] * 6) + '/g',
     nc('属性', '六维', '<span class="sz-nexp">' + BX % ('ex', 1, 2, 'EXP', 1, 2) + '</span>' + six(2)))
ATKI = '<i data-a="%s"><b>%s</b><strong>$%d</strong></i>'
rule('角色·攻防', r'/§角色攻防｜ATK (\d{1,6}) · MAG (\d{1,6}) · PV (\d{1,6}) · DV (\d{1,6}) ?｜? ?([^\n]*)/g',
     nc('属性', '攻防', '<span class="sz-atks">' + ATKI % ('atk', 'ATK', 1) + ATKI % ('mag', 'MAG', 2) + ATKI % ('pv', 'PV', 3) + ATKI % ('dv', 'DV', 4) + '</span><small class="sz-resist">$5</small>'))
rule('角色·攻防·没魔', r'/§角色攻防｜ATK (\d{1,6}) · PV (\d{1,6}) · DV (\d{1,6}) ?｜? ?([^\n]*)/g',
     nc('属性', '攻防', '<span class="sz-atks">' + ATKI % ('atk', 'ATK', 1) + ATKI % ('pv', 'PV', 2) + ATKI % ('dv', 'DV', 3) + '</span><small class="sz-resist">$4</small>'))
rule('角色·攻防·别的', r'/§角色攻防｜([^\n]*)/g', nc('属性', '攻防', '<span class="sz-arct">$1</span>'))
# 关系页
rule('角色·因果', r'/§角色行｜关系因果｜([^\n]*)/g', '<div class="sz-nc sz-rels" data-t="关系" data-k="关系因果">ⓔ\n§因 $1ⓚ因\n</div>ⓔ')
# 行装页
rule('角色·私产', r'/§角色行｜私产｜' + F + r'｜ ?([^\n]*)/g',
     '<div class="sz-nc" data-t="行装" data-k="私产"><b class="sz-ht">私产</b><span class="sz-coins sz-purse">$2</span><div class="sz-owns">ⓔ\n§产 $1ⓝ产\n</div></div>ⓔ')
for cn, cl in [('巴尔', 'c-b'), ('索恩', 'c-s'), ('便士', 'c-p'), ('金币', 'c-b'), ('银币', 'c-s'), ('铜币', 'c-p'), ('金', 'c-b'), ('银', 'c-s'), ('铜', 'c-p')]:
    rule('私产·' + cn, r'/(<span class="sz-coins sz-purse">[^\n]*)%s (\d{1,9})/g' % cn, '$1<i class="%s"><b>%s</b>$2</i>' % (cl, cn))
rule('角色·装备', r'/§角色细｜装备｜([^\n]*)/g', '<div class="sz-nc" data-t="行装" data-k="装备"><b class="sz-ht">装备</b><div class="sz-gears">ⓔ\n§装 $1ⓚ装\n</div></div>ⓔ')
# 能力页
rule('角色·能力', r'/§角色细｜命星·能力｜([^\n]*)/g', '<div class="sz-nc" data-t="能力" data-k="命星·能力"><b class="sz-ht">命星与能力</b><div class="sz-gabs">ⓔ\n§能 $1ⓚ能\n</div></div>ⓔ')
rule('角色·职业', r'/§角色细｜职业｜' + F + r'｜ ?([^\n]*)/g', nc('能力', '职业', '<b class="sz-ht">职业</b><span class="sz-jl"><b>$1</b><small>$2</small></span>'))
rule('角色·职业能力·无', r'/§角色细｜职业能力｜(?:无|暂无) *$/gm', 'ⓔ')
rule('角色·职业能力', r'/§角色细｜职业能力｜([^\n]*)/g', nc('能力', '职业能力', '<b class="sz-ht">职业能力</b><span class="sz-arct">$1</span>'))
for k, t in [('容貌', '形象'), ('着装与姿态', '形象'), ('状态', '形象'), ('属性', '属性'), ('私产', '行装'), ('羁绊', '关系')]:   # 写法对不上的，也落在该去的那一页
    rule('角色·%s·别的' % k, r'/§角色行｜%s｜([^\n]*)/g' % k, nc(t, k, '<b class="sz-ht">%s</b><span class="sz-arct">$1</span>' % k))
rule('角色·外观', r'/§角色行｜外观｜([^\n]*)/g', nc('形象', '外观', '<b class="sz-ht">外观</b><span class="sz-arct">$1</span>'))
rule('角色行', r'/§角色行｜([^｜\n]{1,8})｜([^\n]*)/g', nc('关系', '$1', '<b class="sz-ht">$1</b><span class="sz-arct">$2</span>'))
rule('角色细', r'/§角色细｜([^｜\n]{1,8})｜([^\n]*)/g', nc('能力', '$1', '<b class="sz-ht">$1</b><span class="sz-arct">$2</span>'))
# ---- 普通战斗：遭遇题、敌人一张一张、弱点和注意。条只画看得出来的程度，字写状态，不报数（底卡战斗栏那一条） ----
rule('战斗题', r'/§战斗｜([^｜\n]{1,30})｜([^\n]{0,20})/', '<div class="sz-enc"><small>遭遇</small><b>$1</b><span>$2</span></div>ⓔ')
# 月银纪报兽，第二栏写这头兽是哪一档、哪一曜（共鸣兽·赤火），不报数。纷争纪第二栏写寻常、成队、成群、镇将、有名者、传奇、魔神，后头可以接一句是谁的兵（成群·骨匠拼的）。山铜纪照委托分档写寻常、成群、有名有姓、极境、英雄、残火、传奇
rule('敌情·兽档', r'/§敌情｜([^｜\n"]{1,24})｜((?:杂兽|共鸣兽|灵格兽|极境兽|领主|灾祸|寻常|成队|成群|镇将|有名者|有名有姓|极境|英雄|残火|传奇|魔神)[^｜\n]{0,8})｜([^｜\n·]{0,8})·(\d{1,3})｜([^｜\n·]{0,8})·(\d{1,3})｜([^｜\n"]{0,6})｜([^\n]{0,80})/g',
     '<div class="sz-foe" data-th="$7"><div class="f-h"><b>$1</b><small>$2</small><em>$7</em></div>'
     '<span class="sz-bar hp" style="--v:$4;--m:100"><b>伤势</b><em>$3</em><span class="sz-trk"></span></span><span class="sz-bar st" style="--v:$6;--m:100"><b>架势</b><em>$5</em><span class="sz-trk"></span></span><p>$8</p></div>ⓔ')
rule('敌情',r'/§敌情｜([^｜\n"]{1,24})｜(?:LVL )?([^｜\n]{1,8})｜([^｜\n·]{0,8})·(\d{1,3})｜([^｜\n·]{0,8})·(\d{1,3})｜([^｜\n"]{0,6})｜([^\n]*)/g',
     '<div class="sz-foe" data-th="$7"><div class="f-h"><b>$1</b><small>LVL $2</small><em>$7</em></div>'
     '<span class="sz-bar hp" style="--v:$4;--m:100"><b>伤势</b><em>$3</em><span class="sz-trk"></span></span><span class="sz-bar st" style="--v:$6;--m:100"><b>架势</b><em>$5</em><span class="sz-trk"></span></span><p>$8</p></div>ⓔ')
rule('敌情·别的', r'/§敌情｜([^｜\n]{1,24})｜([^\n]*)/g', '<div class="sz-foe"><div class="f-h"><b>$1</b></div><p>$2</p></div>ⓔ')
rule('战况', r'/§战况｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-wn" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
# ---- 史诗战：一整幅 Boss（立绘按名号和第几阶认，表在 boss_art.json，转阶段图跟着换）、第几阶段、阶段名、势条和架势，底下乐章和几张情报 ----
#   §史诗｜名号｜阶段 II/III｜阶段名｜LVL n｜战场     后三栏可以少写两种
#   §史诗势｜势条状态·百分｜架势状态·百分
#   §史诗况｜类｜内容    类是 已识别、未破解、场地、保护、撤退、协战、圣歌、庇护；圣歌照底卡写 乐章《名》｜线：…｜人声：…｜我方：…｜它：…
#   月银纪没有圣歌和庇护（月银纪·规则｜史诗战与生死）：圣歌那一行写 地盘（打在不在它的地上）和 身后的火（最近那一堆有多远），庇护那一行写 抬人（谁抬得动人、抬到哪里去）
#   山铜纪（山铜纪·规则｜史诗战与生死）：圣歌那一行写 身后的路（通不通、上头谁在等），庇护那一行写 谁背得动人（白烛的帐子在哪里）
HERO = ('<div class="sz-boss" data-n="$1" data-p="$2"><i class="sz-boss-art"></i><div class="sz-boss-in"><small class="b-k">BOSS ENCOUNTER</small><b class="b-n">$1</b>%s'
        '<span class="b-ph">' + PIPS % ('$2', '$3') + '<em>第 $2 / $3 阶段</em></span>%sⓧ</div></div>ⓔ')
PN = '<span class="b-pn">$4</span>'
NM = r'/§史诗｜([^｜\n"]{1,30})｜(?:阶段)? ?([IVX\d]{1,4})\/([IVX\d]{1,4})'
rule('史诗·全', NM + r'｜([^｜\n]{0,40})｜([^｜\n]{0,12})｜([^\n]*)/', HERO % ('<span class="b-f"><i>$5</i><i>$6</i></span>', PN))
rule('史诗·阶段名', NM + r'｜([^｜\n]{0,40})/', HERO % ('', PN))
rule('史诗·阶段', NM + r' *$/m', HERO % ('', ''))
rule('史诗·别的', r'/§史诗｜([^｜\n"]{1,30})｜([^\n]{0,30})/', '<div class="sz-boss" data-n="$1"><i class="sz-boss-art"></i><div class="sz-boss-in"><small class="b-k">BOSS ENCOUNTER</small><b class="b-n">$1</b><span class="b-pn">$2</span>ⓧ</div></div>ⓔ')
BB = '<span class="sz-bar %s" style="--v:$%d;--m:100"><b>%s</b><em>$%d</em><span class="sz-trk"></span></span>'
rule('史诗势', r'/ⓧ([\s\S]*)§史诗势｜([^｜\n·]{0,8})·(\d{1,3})｜([^｜\n·]{0,8})·(\d{1,3})/', '<span class="b-bars">' + BB % ('bl', 3, '势', 2) + BB % ('bp', 5, '架势', 4) + '</span>$1ⓔ')
rule('史诗势·一条', r'/ⓧ([\s\S]*)§史诗势｜([^｜\n·]{0,8})·(\d{1,3})/', '<span class="b-bars">' + BB % ('bl', 3, '势', 2) + '</span>$1ⓔ')
rule('史诗势·没有', r'/ⓧ/', '')
BKIND = '已识别|未破解|场地|保护|撤退|协战|圣歌|庇护|地盘|身后的火|抬人|殿光|出墙的门|担架|身后的路|谁背得动人'
rule('史诗况·冒号', r'/§史诗况｜(%s)[：:]/g' % BKIND, '§史诗况｜$1｜')
rule('乐章', r'/§史诗况｜圣歌｜乐章《([^》\n]{0,24})》｜线：([^｜\n]{0,40})｜人声：([^｜\n]{0,8})｜我方：([^｜\n]*)｜它：([^\n]*)/',
     '<div class="sz-canto" data-v="$3"><span class="c-t"><small>乐章</small><b>《$1》</b><span class="c-l">$2</span><em>人声 $3</em></span><span class="c-side"><small>我方</small>$4</span><span class="c-side"><small>它</small>$5</span></div>ⓔ')
rule('乐章·基础', r'/§史诗况｜圣歌｜线：([^｜\n]{0,40})｜人声：([^｜\n]{0,8})｜我方：([^｜\n]*)｜它：([^\n]*)/',
     '<div class="sz-canto" data-v="$2"><span class="c-t"><small>圣歌</small><span class="c-l">$1</span><em>人声 $2</em></span><span class="c-side"><small>我方</small>$3</span><span class="c-side"><small>它</small>$4</span></div>ⓔ')
rule('乐章·别的', r'/§史诗况｜圣歌｜([^\n]*)/', '<div class="sz-canto"><span class="c-t"><small>圣歌</small><span class="c-l">$1</span></span></div>ⓔ')
rule('史诗况·庇护', r'/§史诗况｜庇护｜([^\n]*)/', '<div class="sz-bi sz-ward" data-k="庇护"><b>复活庇护</b><span>$1</span></div>ⓔ')
rule('史诗况·各类', r'/§史诗况｜(已识别|未破解|场地|保护|撤退|协战|地盘|身后的火|抬人|殿光|出墙的门|担架|身后的路|谁背得动人)｜([^\n]*)/g', '<div class="sz-bi" data-k="$1"><b>$1</b>ⓔ\n§势 $2ⓜ势\n</div>ⓔ')
rule('史诗况', r'/§史诗况｜([^\n]{1,200})/g', '<div class="sz-wn"><span>$1</span></div>ⓔ')

# ---- 拆行：一行几段的一次拆开，括号里的竖线不算；行尾记号写着这一段叫什么字 ----
NOPAR = '(?![^（\\n]*）)'
rule('拆行·去句尾', r'/[。；\s]+(?=ⓜ)/g', '')
rule('拆行·竖线', r'/ ?(?:｜| \| ) ?' + NOPAR + r'(?=[^\n]*ⓛ([^\n｜]{1,4})$)/gm', '\n§$1 ')
rule('拆行·带空格的竖线', r'/ (?:｜|\|) ' + NOPAR + r'(?=[^\n]*ⓚ([^\n｜]{1,4})$)/gm', '\n§$1 ')
rule('拆行·连分句', r'/ ?(?:[｜；。]| \| ) ?' + NOPAR + r'(?=[^\n]*ⓜ([^\n｜]{1,4})$)/gm', '\n§$1 ')
rule('拆行·顿号', r'/、(?=[^\n]*ⓝ([^\n｜]{1,4})$)/gm', '\n§$1 ')
rule('拆行·去记号', r'/[ⓛⓚⓜⓝ][^\n｜]{1,4}$/gm', '')
rule('拆行·去空行', r'/^§(?:闻|情|报|索|势) *$/gm', 'ⓔ')   # 句号接竖线，中间拆出来一条空的
# ---- 拆出来的一行一条 ----
rule('推演·键值', r'/^§条 ([^：\n]{1,12})：([^\n]*)$/gm', '<i><b>$1</b>$2</i>ⓔ')
rule('推演·一句', r'/^§条 ([^\n]*)$/gm', '<i>$1</i>ⓔ')
rule('日报·条', r'/^§报 ([^\n]*)$/gm', '<span class="d-i">$1</span>ⓔ')
rule('史诗况·条', r'/^§势 ([^：\n]{1,14})：([^\n]*)$/gm', '<span class="b-i"><b>$1</b>$2</span>ⓔ')
rule('史诗况·一句', r'/^§势 ([^\n]*)$/gm', '<span class="b-i">$1</span>ⓔ')
rule('情报·条', r'/^§情 ([^（\n]*)（(?:来源[：:])?([^，,）\n]{1,24})[，,] ?可信度[：: ]?([^）\n]{1,6})）([^\n]*)$/gm',
     '<div class="in-i" data-c="$3"><span>$1$4</span><small><i class="in-s">$2</i><em><i></i>可信度 $3</em></small></div>ⓔ')
rule('情报·条·别的', r'/^§情 ([^\n]*)$/gm', '<div class="in-i"><span>$1</span></div>ⓔ')
rule('风闻·条', r'/^§闻 ([^\n]*)（([^）\n]{1,18})）$/gm', '<span class="ru-i">$1<small>$2</small></span>ⓔ')
rule('风闻·条·别的', r'/^§闻 ([^\n]*)$/gm', '<span class="ru-i">$1</span>ⓔ')
rule('可接·条', r'/^§接 ([^（\n]{1,30})（([^，,）\n]{1,12})[，,] ?([^）\n]{1,24})） *$/gm', '<span class="sz-slip"><b>$1</b><i>$2</i><em>$3</em></span>ⓔ')
rule('可接·条·别的', r'/^§接 ([^\n]*)$/gm', '<span class="sz-slip"><b>$1</b></span>ⓔ')
rule('线索·条', r'/^§索 ([^\n]*)$/gm', '<span class="sz-note">$1</span>ⓔ')
rule('斩过·条', r'/^§斩 ([^（\n]{1,16})（([^）\n]{1,10})） *$/gm', '<span class="sz-kill" data-g="$2"><i></i><b>$1</b><small>$2</small></span>ⓔ')
rule('斩过·条·别的', r'/^§斩 ([^\n]*)$/gm', '<span class="sz-kill"><i></i><b>$1</b></span>ⓔ')
rule('已完成·条', r'/^§成 ([^→\n]*)→([^→\n]*)→([^\n]*)$/gm','<div class="sz-mm" data-k="已完成"><b>$1</b><span>$2</span><em>$3</em></div>ⓔ')
rule('已完成·条·别的', r'/^§成 ([^\n]*)$/gm', '<div class="sz-mm" data-k="已完成"><b>$1</b></div>ⓔ')
rule('记忆·箭头', r'/ ?(?:->|→) ?(?=[^\n<]*<\/span><\/div>ⓔ$)/gm', '<i class="sz-ar"></i>')
rule('况·无', r'/^§况 [^\s\n]{1,4} (?:无|暂无|0%) *$/gm', 'ⓔ')
rule('况·空', r'/^§况 (?:无|暂无|0%)? *$/gm', 'ⓔ')
rule('况', r'/^§况 (伤|污染|异常) ([^\n]*)$/gm', '<i data-k="$1"><small>$1</small>$2</i>ⓔ')
rule('况·别的', r'/^§况 ([^\n]*)$/gm', '<i>$1</i>ⓔ')
rule('绊·无', r'/^§绊 (?:羁绊任务|协战技) ?(?:无|暂无) *$/gm', 'ⓔ')
rule('绊·空', r'/^§绊 (?:无|暂无)? *$/gm', 'ⓔ')
rule('绊', r'/^§绊 (羁绊任务|协战技) ?([^\n]*)$/gm', '<i><small>$1</small>$2</i>ⓔ')
rule('绊·别的', r'/^§绊 ([^\n]*)$/gm', '<i>$1</i>ⓔ')
rule('因·无', r'/^§因 [^：\n]{1,12}：(?:无|暂无|不变)[ 。]*$/gm', 'ⓔ')
rule('因', r'/^§因 ([^：\n]{1,12})：([^\n]*)$/gm', '<div class="sz-rel" data-k="$1"><small>$1</small><span>$2</span></div>ⓔ')
rule('因·别的', r'/^§因 ([^\n]*)$/gm', '<div class="sz-rel"><span>$1</span></div>ⓔ')
rule('产·无', r'/^§产 (?:无|暂无)? *$/gm', 'ⓔ')
rule('产', r'/^§产 ([^"\n]{1,30})$/gm', '<span class="sz-it sz-own" data-n="$1"><i class="sz-ic"></i><b>$1</b></span>ⓔ')
rule('产·别的', r'/^§产 ([^\n]*)$/gm', '<span class="sz-own"><b>$1</b></span>ⓔ')
GR = '<span class="sz-it sz-gr" data-q="%s" data-n="%s"><i class="sz-ic"></i><span><b>%s</b><small>%s</small>%s</span></span>ⓔ'
rule('装·无', r'/^§装 [^\s\n]{1,6} (?:无|暂无|空置) *$/gm', 'ⓔ')
rule('装·全', r'/^§装 ([^\s\n]{1,6}) ([^〔\n"]{1,30})〔([^〕\n"]{0,40})〕[：:]([^\n]*)$/gm', GR % ('$3', '$2', '$2', '$1 · $3', '<em>$4</em>'))
rule('装', r'/^§装 ([^\s\n]{1,6}) ([^〔\n"]{1,30})〔([^〕\n"]{0,40})〕 *$/gm', GR % ('$3', '$2', '$2', '$1 · $3', ''))
rule('装·简', r'/^§装 ([^\s\n]{1,6}) ([^\n"]{1,40})$/gm', GR % ('$2', '$2', '$2', '$1', ''))
rule('装·别的', r'/^§装 ([^\n]*)$/gm', '<span class="sz-gr"><span><b>$1</b></span></span>ⓔ')
GA = '<span class="sz-it sz-ga" data-c="%s" data-q="%s"><i class="sz-hx"></i><span><b>%s</b><small>%s</small>%s</span></span>ⓔ'
rule('能·全', r'/^§能 ([^(（：\n]{1,20})[(（]([^·)）\n"]{1,10})·([^)）\n"]{1,10})[)）][：:]([^\n]*)$/gm', GA % ('$2', '$3', '$1', '$2 · $3', '<em>$4</em>'))
rule('能', r'/^§能 ([^(（：\n]{1,20})[(（]([^·)）\n"]{1,10})·([^)）\n"]{1,10})[)）] *$/gm', GA % ('$2', '$3', '$1', '$2 · $3', ''))
rule('能·阶', r'/^§能 ([^(（：\n]{1,20})[(（]([^)）\n"]{1,20})[)）] *$/gm', GA % ('Skill', '', '$1', '$2', ''))
rule('能·别的', r'/^§能 ([^\n]*)$/gm', '<span class="sz-ga"><span><em>$1</em></span></span>ⓔ')
# ---- 收尾：写歪了、哪一条都没认的记录，落成一行「栏名 内容」，不露 § 也不丢字 ----
rule('记录兜底', r'/^§([^｜\s]{1,8})｜([^\n]*)$' + G + '/gm', '<div class="sz-f sz-row" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
rule('记录兜底·没栏', r'/^§([^\n]*)$' + G + '/gm', '<div class="sz-f sz-row"><span>$1</span></div>ⓔ')
# 漏网的竖线（只认正文字，不碰属性值）换成中点；收最后一页，底下一排页签（手札加七个），去掉行尾记号并成一块
rule('竖线收尾', r'/ ?(?:｜| \| ) ?(?=[^<>\n]*<)' + G + '/g', ' · ')
TABS = [('prose', '手札'), ('panel', '面板'), ('deed', '伟业'), ('bag', '背包'), ('party', '同行'), ('news', '见闻'), ('map', '地图'), ('mem', '记忆'), ('war', '战斗')]
NAV = '<nav class="sz-tabs">' + ''.join('<label class="sz-tab t-%s"><input type="radio" name="sz-tab"><i></i><b>%s</b></label>' % t for t in TABS) + '</nav>'
rule('收卷', r'/\s*([ⓂⓈⒷ]?)ⓩ\s*$/', CLOSE + NAV + '$1')
# ---- 一纪一套字眼：页上写死的那些字，这一纪没有那样东西的换掉。月银纪照常驻和月银纪·兵器、风格与法门：
# 那时没有冒险者面板、公会、旅印和日报，二十三命路要到纷争纪才成型。生人见面问的是 旅人，你自哪一堆火而来；职业是兵器加风格，身上的底子是法门；
# 活儿从悬赏板上揭，按要斩的兽分；消息和名号都是诗人唱出来的。AI 写的记录行不变，只换页上的字 ----
ERA_LABELS = {'Ⓜ': [
    ('<b>冒险者面板</b>', '<b>旅人，你自哪一堆火而来</b>'), ('<b>成长与伟业</b>', '<b>铸名</b>'), ('<b>背包与仓库</b>', '<b>行囊与家当</b>'), ('<b>同行与在场</b>', '<b>同行的人</b>'), ('<b>冒险见闻</b>', '<b>传唱与见闻</b>'),
    ('返回手札', '返回长歌'),
    ('<i></i><b>手札</b></label>', '<i></i><b>长歌</b></label>'), ('<i></i><b>面板</b></label>', '<i></i><b>旅人</b></label>'), ('<i></i><b>伟业</b></label>', '<i></i><b>铸名</b></label>'),
    ('<i></i><b>背包</b></label>', '<i></i><b>行囊</b></label>'), ('<i></i><b>见闻</b></label>', '<i></i><b>传唱</b></label>'),
    ('<i data-t="凡极"><b>凡极</b></i>', ''),     # 这一纪的人和兽都到天灾为止
    ('<small>命路</small>', '<small>法门</small>'), ('<small>职业</small>', '<small>兵器·风格</small>'), ('<small>评定</small>', '<small>谁认的</small>'), ('<small>进阶</small>', '<small>往后</small>'),
    ('<small>伟业簿</small>', '<small>伟业</small>'), ('<small>候选称号</small>', '<small>诗人叫他</small>'),
    ('<b>职业能力</b>', '<b>风格本事</b>'), ('<small>职业能力 · ', '<small>风格本事 · '), ('<b class="sz-ht">职业</b>', '<b class="sz-ht">兵器·风格</b>'), ('<b class="sz-ht">职业能力</b>', '<b class="sz-ht">风格本事</b>'),
    ('<small>当前委托</small>', '<small>在办</small>'), ('<small>当前任务</small>', '<small>主线</small>'), ('<small>报酬</small>', '<small>赏格</small>'),
    ('<b>绑定</b>', '<b>丢不得</b>'),
    ('<b class="d-t">日报</b>', '<b class="d-t">诗人在唱</b>'), ('</i>已知情报</b>', '</i>打听来的</b>'), ('</i>流言风闻</b>', '</i>火边的闲话</b>'), ('</i>可接委托</b>', '</i>悬赏板</b>'),
    ('<small class="b-k">BOSS ENCOUNTER</small>', '<small class="b-k">过了这道线，它就认得你了</small>'), ('<div class="sz-bintro"><small>BOSS ENCOUNTER</small>', '<div class="sz-bintro"><small>过了这道线，它就认得你了</small>'),
], 'Ⓢ': [
    # 纷争纪照常驻：墙上量一个人，看他守过哪一段，挡下过谁，战报上写过他几回。没有公会、旅印、面板，活儿从段守、军团、白烛、铃尾、车队和按剑会的赏格来，日报记的是战报。守将问的那一句是墙前的早晨里的原话
    ('<b>冒险者面板</b>', '<b>哪一部的，战报上要写</b>'), ('<b>成长与伟业</b>', '<b>守过哪一段，挡下过谁</b>'), ('<b>背包与仓库</b>', '<b>军需与私囊</b>'), ('<b>同行与在场</b>', '<b>同一班的人</b>'), ('<b>冒险见闻</b>', '<b>战报与风声</b>'),
    ('返回手札', '返回战记'),
    ('<i></i><b>手札</b></label>', '<i></i><b>战记</b></label>'), ('<i></i><b>面板</b></label>', '<i></i><b>军册</b></label>'), ('<i></i><b>伟业</b></label>', '<i></i><b>军功</b></label>'),
    ('<i></i><b>背包</b></label>', '<i></i><b>军需</b></label>'), ('<i></i><b>同行</b></label>', '<i></i><b>同袍</b></label>'), ('<i></i><b>见闻</b></label>', '<i></i><b>战报</b></label>'),
    ('<i data-t="凡极"><b>凡极</b></i>', ''),     # 凡极要到迷宫纪 318 年才有人到
    ('<small>职业</small>', '<small>兵器·路子</small>'), ('<small>评定</small>', '<small>谁认的</small>'), ('<small>进阶</small>', '<small>往后</small>'),
    ('<small>伟业簿</small>', '<small>战报写过</small>'), ('<small>候选称号</small>', '<small>墙上叫他</small>'), ('<small>斩过</small>', '<small>挡下过</small>'),
    ('<b>职业能力</b>', '<b>路子上的本事</b>'), ('<small>职业能力 · ', '<small>路子上的本事 · '), ('<b class="sz-ht">职业</b>', '<b class="sz-ht">兵器·路子</b>'), ('<b class="sz-ht">职业能力</b>', '<b class="sz-ht">路子上的本事</b>'),
    ('<small>当前委托</small>', '<small>差遣</small>'), ('<small>当前任务</small>', '<small>主线</small>'), ('<small>报酬</small>', '<small>赏格</small>'),
    ('<b>绑定</b>', '<b>丢不得</b>'),
    ('<b class="d-t">日报</b>', '<b class="d-t">战报</b>'), ('</i>已知情报</b>', '</i>斥候带回来的</b>'), ('</i>流言风闻</b>', '</i>营房里的闲话</b>'), ('</i>可接委托</b>', '</i>段城门口的赏格</b>'),
    ('<small class="b-k">BOSS ENCOUNTER</small>', '<small class="b-k">伤亡册翻开了新的一页</small>'), ('<div class="sz-bintro"><small>BOSS ENCOUNTER</small>', '<div class="sz-bintro"><small>伤亡册翻开了新的一页</small>'),
], 'Ⓑ': [
    # 山铜纪照常驻：没有公会、旅印和面板，活儿钉在行会门口的号墙上，行会的档次量不准一个人，碑上量一个人看他的名字刻在几块碑的背面。事都刻在碑上，碑匠事后来问名字，碑和传唱替了日报
    ('<b>冒险者面板</b>', '<b>碑匠问你，背面怎么刻</b>'), ('<b>成长与伟业</b>', '<b>够刻一块碑的事</b>'), ('<b>背包与仓库</b>', '<b>鞍袋与家当</b>'), ('<b>同行与在场</b>', '<b>团里的人</b>'), ('<b>冒险见闻</b>', '<b>碑、传唱和号墙</b>'),
    ('返回手札', '返回碑记'),
    ('<i></i><b>手札</b></label>', '<i></i><b>碑记</b></label>'), ('<i></i><b>面板</b></label>', '<i></i><b>名字</b></label>'), ('<i></i><b>伟业</b></label>', '<i></i><b>刻碑</b></label>'),
    ('<i></i><b>背包</b></label>', '<i></i><b>鞍袋</b></label>'), ('<i></i><b>同行</b></label>', '<i></i><b>团里</b></label>'), ('<i></i><b>见闻</b></label>', '<i></i><b>号墙</b></label>'),
    ('<i data-t="凡极"><b>凡极</b></i>', ''),     # 凡极要到迷宫纪 318 年才有人到
    ('<small>职业</small>', '<small>兵器·路子</small>'), ('<small>评定</small>', '<small>谁认的</small>'), ('<small>进阶</small>', '<small>往后</small>'),
    ('<small>伟业簿</small>', '<small>做成过</small>'), ('<small>候选称号</small>', '<small>歌里叫他</small>'), ('<small>斩过</small>', '<small>挡下过</small>'),
    ('<b>职业能力</b>', '<b>路子上的本事</b>'), ('<small>职业能力 · ', '<small>路子上的本事 · '), ('<b class="sz-ht">职业</b>', '<b class="sz-ht">兵器·路子</b>'), ('<b class="sz-ht">职业能力</b>', '<b class="sz-ht">路子上的本事</b>'),
    ('<small>当前委托</small>', '<small>接的活</small>'), ('<small>当前任务</small>', '<small>主线</small>'), ('<small>报酬</small>', '<small>给多少</small>'),
    ('<b>绑定</b>', '<b>丢不得</b>'),
    ('<b class="d-t">日报</b>', '<b class="d-t">碑和传唱</b>'), ('</i>已知情报</b>', '</i>公所的信</b>'), ('</i>流言风闻</b>', '</i>酒馆里的话</b>'), ('</i>可接委托</b>', '</i>号墙上的活</b>'),
    ('<small class="b-k">BOSS ENCOUNTER</small>', '<small class="b-k">这一仗往后要立碑</small>'), ('<div class="sz-bintro"><small>BOSS ENCOUNTER</small>', '<div class="sz-bintro"><small>这一仗往后要立碑</small>'),
]}
# 11-08 四纪进同一张卡：一处字一条规则（一百零一条）连转换那一组超了平台的五百条。改成页上那几处字一次写齐四纪的说法，
# 样式照这一条回复的纪露出一个（make_css_frame.py 的「字眼」那一段）。规则在最后包（LW_WRAP），找不到字面的那几处照旧一处一条
rule('字眼·收记号', '/[ⓂⓈⒷ]/g', '')
rule('并块', r'/ⓔ\s*/g', '')
# 11-07：写歪了的 §底座、没写底座、前头带一段写了 § 的话，版面别塌；MOD 卡包成一块（robust_rules.py，发布卡的补丁也用这一份）
import robust_rules as _RR
for _e, _old, _new in _RR.REGEX_EDITS:
    _hit = [r for r in R if _old in r['regex']]
    assert len(_hit) == 1, (_e, len(_hit))
    _hit[0]['regex'] = _hit[0]['regex'].replace(_old, _new)
for _e, _old, _new in _RR.REP_EDITS:
    _hit = [r for r in R if _old in r['replaceString']]
    assert len(_hit) == 1, (_e, len(_hit))
    _hit[0]['replaceString'] = _hit[0]['replaceString'].replace(_old, _new)
for r in R:   # 别的纪的记号那几条，同样认前头带 § 的话
    if r['regex'].startswith('/^([^§]*§底座｜'):
        r['regex'] = '/^((?:[\\s\\S]*\\n|)§底座｜' + r['regex'][len('/^([^§]*§底座｜'):]
_m = next(i for i, r in enumerate(R) if r['name'] == 'MOD')
R[_m:_m] = [dict(r) for r in _RR.FRAME_MOD_WRAP]
_i = next(i for i, r in enumerate(R) if r['name'] == '去外层围栏·没收尾') + 1
R[_i:_i] = [dict(r) for r in _RR.FRAME_PRE]
# 11-07 晚：超程铭刻的人常驻同行页、标远讯，远讯那一行排在通用的「角色行」前头（history_far.py，发布卡的补丁 patch_pub_1107b.py 也用这一份）
import history_far as _HF
_g = next(i for i, r in enumerate(R) if r['regex'] == _HF.GENERIC_ROW)
R[_g:_g] = [dict(r) for r in _HF.FAR_RULES]


# ---- 字眼：一处字写齐四纪的说法 <span class="lw"><span class="w0">迷宫纪</span><span class="wm">月银纪</span><span class="ws">纷争纪</span><span class="wb">山铜纪</span></span> ----
def _lw_text(a):
    """a 里那一段字（标签以外、唯一的一段），返回 (前缀, 字, 后缀)"""
    import re as _re
    runs = [m for m in _re.finditer(r'[^<>]+', a) if m.group(0).strip()]
    runs = [m for m in runs if a[:m.start()].count('<') == a[:m.start()].count('>')]   # 不算属性里的
    assert len(runs) == 1, ('字眼里认不出那一段字', a)
    return a[:runs[0].start()], runs[0].group(0), a[runs[0].end():]


LW = {}      # a -> {era: 字}
LW_DROP = []  # 这一纪没有的，样式藏
for mark, pairs in ERA_LABELS.items():
    for a, b in pairs:
        if b == '':
            LW_DROP.append((mark, a))
            continue
        pre, t0, suf = _lw_text(a)
        assert b.startswith(pre) and b.endswith(suf), ('字眼前后的标签对不上', a, b)
        LW.setdefault(a, {'w0': t0})['w' + {'Ⓜ': 'm', 'Ⓢ': 's', 'Ⓑ': 'b'}[mark]] = b[len(pre):len(b) - len(suf)]


def _in_tag(s, p):
    return s.rfind('<', 0, p) > s.rfind('>', 0, p)


_left = []
for a in sorted(LW, key=len, reverse=True):
    pre, t0, suf = _lw_text(a)
    v = LW[a]
    span = '<span class="lw">' + ''.join('<span class="%s">%s</span>' % (k, v.get(k, t0)) for k in ('w0', 'wm', 'ws', 'wb')) + '</span>'
    hit = 0
    for r in R:
        s = r['replaceString']
        out, k = [], 0
        while True:
            p = s.find(a, k)
            if p < 0:
                break
            if _in_tag(s, p) and not a.startswith('<'):
                out.append(s[k:p + len(a)])
            else:
                out.append(s[k:p] + pre + span + suf)
                hit += 1
            k = p + len(a)
        out.append(s[k:])
        r['replaceString'] = ''.join(out)
    if not hit:
        _left.append(a)
# 规则的字面里找不到的（拼出来的），照旧一处一条，排在收记号前头
_k = next(i for i, r in enumerate(R) if r['name'] == '字眼·收记号')
for a in _left:
    for mark, pairs in ERA_LABELS.items():
        for x, b in pairs:
            if x == a:
                R.insert(_k, {"name": '字眼·' + a, "regex": '/%s(?=[\\s\\S]*%s)/g' % (a.replace('/', '\\/'), mark), "replaceString": b,
                              "enabled": True, "messageRole": "assistant", "applyMode": "front-end"})
                _k += 1
print('字眼包了', len(LW) - len(_left), '处，照旧一处一条的', len(_left), _left, '藏的', LW_DROP)
json.dump(R, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(R))
