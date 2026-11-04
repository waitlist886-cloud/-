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
import json, sys
R = []
def rule(name, rx, rep):
    R.append({"name": name, "regex": rx, "replaceString": rep, "enabled": True, "messageRole": "assistant", "applyMode": "front-end"})
G = r'(?=[\s\S]*ⓩ)'
BACK = '<label class="sz-x"><input type="radio" name="sz-tab">返回手札</label>'
# ---- 预处理（同第二版）----
rule('帧记号', r'/^(\s*§底座｜[\s\S]*)$/', '$1\nⓩ')
rule('去回车', r'/\r/g', '')
rule('去行首空白', r'/^[ \t　]+' + G + '/gm', '')
rule('记录行的半角竖线', r'/^(§[^\n|]{1,12})\|' + G + '/gm', '$1｜')
rule('记录行的尖括号', r'/^(§[^\n<]{0,400})<' + G + '/gm', '$1＜')
# 记忆页的统计：计数器只认排在被数的东西后面的元素，所以这一行放在页尾，样式再挪到页头
rule('记忆尾', r'/^(§记忆｜[^\n]*)$(?![\s\S]*^§记忆｜)/m', '$1\n§记忆统计')
# ---- 头：一行地点、纪年、钟点，三条（ⓑ 是三条的位置，只在最新一条露出来）；点开是推演底座 ----
HEAD = ('<details class="sz-hud"><summary class="sz-head"><span class="sz-sub"><span class="sz-place">%s</span>'
        '<span class="sz-year">%s</span>%s</span>ⓑ<span class="sz-more">推演</span></summary><div class="sz-hud-body">')
rule('底座加环境',
     r'/^§底座｜纪元：((([^\s·\n]{3,14})(·[^\s\n]{1,40}|)) · (\d{1,2}[:：]\d{2})\s?([^\n·]{0,20})· ([^\s\n]{1,40}) · ([^\s\n]{1,40}) · 防抢话 (开|关) · 档位 ([^\s\n]{1,6}))\s*\n§环境｜([^｜\n]{1,60})｜([^\n]{0,80})$/m',
     HEAD % ('$7', '$3', '<span class="sz-time">$5</span>') +
     '<div class="sz-grid"><div><b>日期</b>$2</div><div><b>时辰</b>$5 $6 · $12</div><div><b>天气</b>$11</div><div><b>地点</b>$7</div><div><b>潮汐</b>$8</div><div><b>档位</b>$10 · 防抢话 $9</div></div>ⓔ')
rule('底座单行', r'/^§底座｜纪元：([^\n]{4,160})$/m', HEAD % ('$1', '', '') + 'ⓔ')
for cls, rx in [('era-moon', '月银纪\\d'), ('era-strife', '(?:纷争纪\\d|山铜纪元年)'), ('era-bronze', '(?:山铜纪\\d|迷宫纪元年)'),
                ('era-pre', '迷宫纪(?:[2-9]|[1-9]\\d|[1-9]\\d\\d|1000)年'), ('era-maze', '迷宫纪(?:100[1-9]|10[1-9]\\d|1[1-9]\\d\\d|[2-9]\\d{3})年')]:
    rule('纪元·' + cls, r'/(<summary class="sz-head">)(?=[^\n]{0,600}<span class="sz-year">%s)/' % rx, '$1<i class="sz-era %s"></i>' % cls)
rule('钟点', r'/(<summary class="sz-head">)(?=[^\n]{0,700}<span class="sz-time">(\d{1,2})[:：](\d{2}))/',
     '$1<style>.custom-styles{--sz-on:1;--sz-h:$2;--sz-m:$3}</style>')
BAR = '<span class="sz-bar %s" style="--v:$%d;--m:%s"><i></i><b>%s</b><em>%s</em><span class="sz-trk"></span></span>'
rule('三条', r'/ⓑ(?=[\s\S]*§面板｜资源｜HP (\d{1,6})\/(\d{1,6}) MP (\d{1,6})\/(\d{1,6}) SP (\d{1,6})\/(\d{1,6}))/',
     '<span class="sz-bars">' + BAR % ('hp', 1, '$2', 'HP', '$1 / $2') + BAR % ('mp', 3, '$4', 'MP', '$3 / $4') + BAR % ('sp', 5, '$6', 'SP', '$5 / $6') + '</span>')
rule('三条·百分', r'/ⓑ(?=[\s\S]*§面板｜资源｜HP (\d{1,3})% MP (\d{1,3})% SP (\d{1,3})%)/',
     '<span class="sz-bars">' + BAR % ('hp', 1, '100', 'HP', '$1%') + BAR % ('mp', 2, '100', 'MP', '$2%') + BAR % ('sp', 3, '100', 'SP', '$3%') + '</span>')
rule('三条·没有', r'/ⓑ/', '')
rule('推演九行', r'/^§推演｜(\d)｜([^｜\n]{1,8})｜([^\n]*)$/gm', '<div class="sz-f d"><b><i>$1</i>$2</b><span class="sz-dl">ⓔ\n§条 $3ⓛ条\n</span></div>ⓔ')
rule('评定', r'/^§评定｜([^\n]{1,300})$/m', '<div class="sz-f d"><b>评定</b><span>$1</span></div>ⓔ')
rule('功能命令', r'/^§功能｜([^\n]{1,30})$/m', '<div class="sz-f d"><b>功能命令</b><span>$1</span></div>ⓔ')
# ---- 手札这一页 ----
rule('正文开卷', r'/^§正文｜([^\n]{1,40})$/m', '</div></details><div class="sz-page sz-prose"><div class="sz-sec"><span>$1</span></div>ⓔ')
rule('篇章题', r'/(<div class="sz-sec"><span>[^<\n]{1,40}<\/span><\/div>ⓔ\s*)([^\n<§｜]{2,10})｜([^\n<§｜]{4,14})\n+([^\n<§｜]{8,80})\n/',
     '$1<div class="sz-qc"><span class="qc-pian">$2</span><b class="qc-ml">$3</b><span class="qc-desc">$4</span></div>ⓔ\n')
rule('段落', r'/^(?!§|<|ⓔ|ⓩ)([^\n]+)$' + G + '/gm', '<p>$1</p>ⓔ')
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
DEEDTOP = ('<div class="sz-path">' + ''.join('<i data-t="%s"><b>%s</b></i>' % (t, t) for t in TIERS) + '</div>ⓖ<div class="sz-gridit sz-abs">' +
           ''.join('<b class="sz-cat" data-c="%s">%s</b>' % (c, c) for c in ABC))
opener('战斗', 'war', '交战')
opener('首领', 'war', '史诗战')
opener('面板', 'panel', '冒险者面板', DOLL)
opener(['伟业', '能力'], 'deed', '成长与伟业', DEEDTOP)
opener(['背包', '物品'], 'bag', '背包与仓库', BAGTOP)
opener('见闻', 'news', '冒险见闻')
opener('记忆', 'mem', '记忆')
rule('同行开页', r'/^§角色｜/m',
     CLOSE + '<section class="sz-page sz-pane p-party"><div class="sz-pane-head"><i></i><b>同行与在场</b>%s</div><div class="sz-pane-body"><div class="sz-npcs"><div hidden><div>§角色｜' % BACK)
# 背包页头的钱和负重在面板那一行，趁它还没展开先抄过去
COINS = '<span class="sz-coins"><i class="c-b"><b>巴尔</b>$2</i><i class="c-s"><b>索恩</b>$3</i><i class="c-p"><b>便士</b>$4</i></span>'
rule('背包·钱', r'/(§面板｜旅印｜[^｜\n]{0,20}｜巴尔 (\d{1,9}) 索恩 (\d{1,9}) 便士 (\d{1,9})[\s\S]*)ⓒ/', '$1' + COINS)
rule('背包·钱没有', r'/ⓒ/', '')
rule('背包·负重', r'/(§面板｜资源｜[^\n]{0,80}负重 (\d{1,6})\/(\d{1,6}) ?kg[\s\S]*)ⓦ/', '$1<span class="sz-bar wt" style="--v:$2;--m:$3"><b>负重</b><em>$2 / $3 kg</em><span class="sz-trk"></span></span>')
rule('背包·负重没有', r'/ⓦ/', '')
# 伟业页头那一块目标也在页里，放到路径底下
GOAL = ('<div class="sz-goal" data-t="$2"><span class="g-to"><small>下一境</small><b>$2</b></span><span><small>门槛</small><b>$3</b></span><span><small>命路</small><b>$4</b></span>'
        '<span><small>蓄势</small><b>$5</b></span><span><small>伟业簿</small><b>$6</b></span><span><small>冠名</small><b>$7</b></span><span><small>候选称号</small><b>$8</b></span></div>')
rule('伟业·目标', r'/ⓖ([\s\S]*)§伟业｜伟业｜([^｜\n]{1,12})｜([^｜\n]{0,30})｜([^｜\n]{0,16})｜蓄势 ([^｜\n]{0,12})｜伟业簿 ([^｜\n]{0,30})｜破格铸史冠名 ([^｜\n]{0,20})｜候选称号 ([^\n]{0,30})/',
     GOAL + '$1ⓔ')
rule('伟业·目标没有', r'/ⓖ/', '')

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
rule('面板·身份', r'/§面板｜身份｜([^｜\n]{1,20})｜([^｜\n]{0,20})｜([^｜\n]{0,10})｜([^｜\n]{0,8})｜([^｜\n]{0,30})｜([^\n]{0,40})/',
     '<div class="sz-f sz-idc" data-k="身份"><b class="sz-who">$1</b><span class="sz-tags"><i>$2</i><i>$3</i><i>$4</i><i class="vow">$5</i><i>$6</i></span></div>ⓔ')
rule('面板·着装', r'/§面板｜着装｜([^｜\n"]{0,40})｜([^｜\n"]{0,40})｜([^｜\n"]{0,40})｜([^｜\n"]{0,40})｜([^\n]{0,60})/',
     ''.join(slot(p, '着装', '$%d' % k, p + ' · 着装', '', '', ' sz-cl') for p, k in [('外层', 1), ('内层', 2), ('足', 3), ('配饰', 4)]) + 'ⓔ')
rule('装备', r'/§装备｜([^｜\n"]{1,6})｜([^｜\n"]{1,30})｜([^｜\n"]{0,8})｜([^｜\n]{0,50})｜([^\n]{0,120})/g',
     slot('$1', '$3', '$2', '$1 · $3', '$4', '$5') + 'ⓔ')
rule('装备·空', r'/§装备｜[^\n]*/g', 'ⓔ')
BX = '<span class="sz-bar %s" style="--v:$%d;--m:$%d"><b>%s</b><em>$%d / $%d</em><span class="sz-trk"></span></span>'
LVB = '<div class="sz-f sz-lv" data-k="位阶"><span class="sz-lvl"><small>LVL</small><b>$1</b></span><span class="sz-lvm"><b class="sz-tier">$2</b>' + BX % ('ex', 3, 4, 'EXP', 3, 4)
rule('面板·位阶', r'/§面板｜位阶｜LVL (\d{1,3}) ([^｜\n]{1,20})｜EXP (?:EXP )?(\d{1,9})\/(\d{1,9})｜蓄势 (\d{1,6})\/(\d{1,6})[^\n]{0,20}/',
     LVB + BX % ('xu', 5, 6, '蓄势', 5, 6) + '</span></div>ⓔ')
rule('面板·位阶·别的', r'/§面板｜位阶｜LVL (\d{1,3}) ([^｜\n]{1,20})｜EXP (?:EXP )?(\d{1,9})\/(\d{1,9})｜([^\n]{0,40})/',
     LVB + '<small class="sz-note">$5</small></span></div>ⓔ')
CH4 = '<span class="sz-chips"><i>$%d</i><i>$%d</i><i>$%d</i><i>$%d</i></span>'
F4 = '｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^\n]{0,20})'
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
rule('面板·攻防', r'/§面板｜攻防｜ATK (\d{1,6}) · MAG (\d{1,6}) · PV (\d{1,6}) · DV (\d{1,6})｜([^\n]*)/',
     '<div class="sz-f sz-atk" data-k="攻防"><span class="sz-atks"><i data-a="atk"><b>ATK</b><strong>$1</strong></i><i data-a="mag"><b>MAG</b><strong>$2</strong></i><i data-a="pv"><b>PV</b><strong>$3</strong></i><i data-a="dv"><b>DV</b><strong>$4</strong></i></span><small class="sz-resist">$5</small></div>ⓔ')
rule('面板·命路', r'/§面板｜命路｜([^｜\n]{0,20})｜(?:职业 )?([^｜\n]{0,20})｜(?:命星 )?([^\n]{0,30})/',
     '<div class="sz-f sz-road" data-k="命路"><span><small>命路</small><b>$1</b></span><span><small>职业</small><b>$2</b></span><span><small>命星</small><b>$3</b></span></div>ⓔ')
rule('面板·旅印', r'/§面板｜旅印｜([^｜\n]{0,20})｜巴尔 (\d{1,9}) 索恩 (\d{1,9}) 便士 (\d{1,9})｜([^｜\n]{0,20})｜([^\n]{0,40})/',
     '<div class="sz-f sz-seal" data-k="旅印"><span class="sz-sealb"><i></i><b>$1</b></span>' + COINS + '<span class="sz-tags"><i>$5</i><i>$6</i></span></div>ⓔ')
rule('面板·委托空', r'/§面板｜委托｜无[ ｜][^\n]*/', 'ⓔ')
rule('面板·委托', r'/§面板｜委托｜' + F + '｜' + F + '｜' + F + '｜' + F + '｜([^\\n]*)/',
     '<div class="sz-qcard" data-k="在办"><i class="sz-ic"></i><span class="q-n"><small>当前委托</small><b>$1</b></span><em>$2</em>'
     '<span class="q-f"><i><small>风险</small>$3</i><i><small>报酬</small>$4</i><i class="w"><small>失败后果</small>$5</i></span></div>ⓔ')
rule('面板各行', r'/§面板｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-f sz-row" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
# ---- 伟业：能力一个一格，一个一张卡 ----
ABT = ('<span class="sz-it sz-ab" data-c="$1" data-q="$3" data-n="$2"><label class="sz-face"><input type="radio" name="sz-ab"><i class="sz-hx"></i><b class="sz-nm">$2</b></label>%s</span>ⓔ')
rule('能力', r'/§能力｜([^｜\n"]{1,8})｜([^｜\n"]{1,24})｜([^｜\n"]{0,10})｜([^｜\n]{0,40})｜([^\n]{0,160})/g', ABT % tip('$2', '$1 · $3', '$4', '$5', 'sz-ab'))
rule('能力·空', r'/§能力｜[^\n]*/g', 'ⓔ')
rule('伟业·职业', r'/§伟业｜职业｜([^｜\n]{0,30})｜([^｜\n]{0,30})｜([^\n]{0,30})/',
     '<div class="sz-f sz-job" data-k="职业"><span><small>职业</small><b>$1</b></span><span><small>评定</small><b>$2</b></span><span><small>进阶</small><b>$3</b></span></div>ⓔ')
rule('伟业各行', r'/§伟业｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-f sz-row" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
# ---- 背包：一样东西一格 ----
ITT = ('<span class="sz-it sz-cell" data-c="$1" data-q="$%d" data-n="$2"><label class="sz-face"><input type="radio" name="sz-it"><span class="sz-pad"><i class="sz-ic"></i>%s</span><b class="sz-nm">$2</b></label>%s</span>ⓔ')
rule('物品·带数', r'/§物品｜([^｜\n"]{1,8})｜([^｜\n×"]{1,24})×(\d{1,5})｜([^｜\n"]{0,8})｜([^｜\n]{0,16})｜([^\n]{0,160})/g',
     ITT % (4, '<em class="sz-ct">$3</em>', tip('$2', '$4 · $5 · 持有 $3', '', '$6', 'sz-it')))
rule('物品', r'/§物品｜([^｜\n"]{1,8})｜([^｜\n"]{1,24})｜([^｜\n"]{0,8})｜([^｜\n]{0,16})｜([^\n]{0,160})/g',
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
rule('记忆·短期', r'/§记忆｜短期｜\[(\d{1,3})\]（([^）\n]{1,40})）([^|｜\n]{0,40})' + SEP + r'(?:核心事件[：:])?([^\n]*)/g',
     '<div class="sz-mm" data-k="短期" style="--n:$1"><i class="m-n">$1</i><span class="m-w"><time>$2</time><small>$3</small></span><span class="m-t">$4</span></div>ⓔ')
rule('记忆·短期·别的', r'/§记忆｜短期｜\[(\d{1,3})\]（([^）\n]{1,40})）([^\n]*)/g',
     '<div class="sz-mm" data-k="短期" style="--n:$1"><i class="m-n">$1</i><span class="m-w"><time>$2</time></span><span class="m-t">$3</span></div>ⓔ')
# 长期和核心一条两三百字，先露三行，点一下展开
rule('记忆·长期核心', r'/§记忆｜(长期|核心)｜\[\d{1,3}\]（([^）\n]{1,40})）([^|｜\n]{0,40})' + SEP + r'([^\n]*)/g',
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
       '<div class="sz-npc-b"><div class="sz-por"><i data-n="$1"></i></div><div class="sz-npc-name"><b>$1</b><span>$3</span></div>' + NTABS + 'ⓔ')
WHO = r'/§角色｜(([^｜\n·]{1,12})[^｜\n]{0,20})｜([^｜\n]{1,40})'
rule('角色·立绘', WHO + r'｜立绘[:：]([^｜\n]{1,8})/g', NPC % ' data-portrait="$4"')
rule('角色·名牌', WHO + r'｜名牌/g', NPC % '')
rule('角色·路人', WHO + r'(?:｜路人)?$/gm', NPC % ' data-walkon="1"')
rule('角色签', r'/§角色签｜([^｜\n]{0,30})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,12})$/gm',
     '<div class="sz-npc-tags"><span class="lv">$3</span><span>$4</span><span>$1</span><span>$2</span><span>$5</span><span class="met">$6</span></div>ⓔ')
rule('角色话', r'/§角色话｜([^\n]{1,200})/g', '<p class="sz-npc-say">$1</p>ⓔ')
def nc(tab, k, inner):
    return '<div class="sz-nc" data-t="%s" data-k="%s">%s</div>ⓔ' % (tab, k, inner)
# 状态：几条在头上，伤、污染、异常拆成小牌，没有的不出
COND = '<span class="sz-cond">ⓔ\n§况 $%dⓚ况\n</span></div>ⓔ'
NB = '<span class="sz-bar %s" style="--v:$%d;--m:$%d"><b>%s</b><em>$%d / $%d</em><span class="sz-trk"></span></span>'
rule('角色·状态', r'/§角色行｜状态｜HP (\d{1,6})\/(\d{1,6}) MP (\d{1,6})\/(\d{1,6}) SP (\d{1,6})\/(\d{1,6}) 架势 (\d{1,6})\/(\d{1,6}) ?｜? ?([^\n]{0,60})/g',
     '<div class="sz-npc-st"><span class="sz-res-bars">' + NB % ('hp', 1, 2, 'HP', 1, 2) + NB % ('mp', 3, 4, 'MP', 3, 4) + NB % ('sp', 5, 6, 'SP', 5, 6) + NB % ('st', 7, 8, '架势', 7, 8) + '</span>' + COND % 9)
NP = '<span class="sz-bar %s" style="--v:$%d;--m:100"><b>%s</b><em>$%d%%</em><span class="sz-trk"></span></span>'
rule('角色·状态·百分', r'/§角色行｜状态｜HP (\d{1,3})% MP (\d{1,3})% SP (\d{1,3})% 架势 (\d{1,3})% ?｜? ?([^\n]{0,60})/g',
     '<div class="sz-npc-st"><span class="sz-res-bars">' + NP % ('hp', 1, 'HP', 1) + NP % ('mp', 2, 'MP', 2) + NP % ('sp', 3, 'SP', 3) + NP % ('st', 4, '架势', 4) + '</span>' + COND % 5)
# 羁绊：一条粉色的，羁绊任务和协战技两小格
BONDT = '<i></i><b>Lv.$1</b><span>$2</span><em>%s</em><span class="sz-trk"></span><span class="sz-bondx">ⓔ\n§绊 %sⓚ绊\n</span></div>ⓔ'
rule('角色·羁绊', r'/§角色行｜羁绊｜好感 Lv\.(\d{1,2}) ([^｜\n]{1,20}) (\d{1,5})\/(\d{1,5})([^｜\n]{0,12}) ?｜? ?([^\n]{0,80})/g',
     '<div class="sz-bond" style="--v:$3;--m:$4">' + BONDT % ('$3 / $4$5', '$6'))
rule('角色·羁绊·满', r'/§角色行｜羁绊｜好感 Lv\.(\d{1,2}) ([^｜\n]{1,20}) MAX ?｜? ?([^\n]{0,80})/g',
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
for cn, cl in [('巴尔', 'c-b'), ('索恩', 'c-s'), ('便士', 'c-p')]:
    rule('私产·' + cn, r'/(<span class="sz-coins sz-purse">[^\n]*)%s (\d{1,9})/g' % cn, '$1<i class="%s"><b>%s</b>$2</i>' % (cl, cn))
rule('角色·装备', r'/§角色细｜装备｜([^\n]*)/g', '<div class="sz-nc" data-t="行装" data-k="装备"><b class="sz-ht">装备</b><div class="sz-gears">ⓔ\n§装 $1ⓚ装\n</div></div>ⓔ')
# 能力页
rule('角色·能力', r'/§角色细｜命星·能力｜([^\n]*)/g', '<div class="sz-nc" data-t="能力" data-k="命星·能力"><b class="sz-ht">命星与能力</b><div class="sz-gabs">ⓔ\n§能 $1ⓚ能\n</div></div>ⓔ')
rule('角色·职业', r'/§角色细｜职业｜' + F + r'｜ ?([^\n]*)/g', nc('能力', '职业', '<b class="sz-ht">职业</b><span class="sz-jl"><b>$1</b><small>$2</small></span>'))
rule('角色·职业能力·无', r'/§角色细｜职业能力｜(?:无|暂无) *$/gm', 'ⓔ')
rule('角色·职业能力', r'/§角色细｜职业能力｜([^\n]*)/g', nc('能力', '职业能力', '<b class="sz-ht">职业能力</b><span class="sz-arct">$1</span>'))
for k, t in [('容貌', '形象'), ('着装与姿态', '形象'), ('状态', '形象'), ('属性', '属性'), ('私产', '行装'), ('羁绊', '关系')]:   # 写法对不上的，也落在该去的那一页
    rule('角色·%s·别的' % k, r'/§角色行｜%s｜([^\n]*)/g' % k, nc(t, k, '<b class="sz-ht">%s</b><span class="sz-arct">$1</span>' % k))
rule('角色行', r'/§角色行｜([^｜\n]{1,8})｜([^\n]*)/g', nc('关系', '$1', '<b class="sz-ht">$1</b><span class="sz-arct">$2</span>'))
rule('角色细', r'/§角色细｜([^｜\n]{1,8})｜([^\n]*)/g', nc('能力', '$1', '<b class="sz-ht">$1</b><span class="sz-arct">$2</span>'))
# ---- 战斗：遭遇题、敌人一张一张、弱点和注意 ----
rule('战斗题', r'/§战斗｜([^｜\n]{1,30})｜([^\n]{0,20})/', '<div class="sz-enc"><b>$1</b><span>$2</span></div>ⓔ')
rule('首领题', r'/§首领｜([^｜\n]{1,30})｜([^\n]{0,40})/', '<div class="sz-enc boss"><b>$1</b><span>$2</span></div>ⓔ')
rule('敌情', r'/§敌情｜([^｜\n"]{1,24})｜(?:LVL )?([^｜\n]{1,8})｜([^｜\n·]{0,8})·(\d{1,3})｜([^｜\n·]{0,8})·(\d{1,3})｜([^｜\n"]{0,6})｜([^\n]{0,80})/g',
     '<div class="sz-foe" data-th="$7"><div class="f-h"><b>$1</b><small>LVL $2</small><em>$7</em></div>'
     '<span class="sz-bar hp" style="--v:$4;--m:100"><b>$3</b><em>$4%</em><span class="sz-trk"></span></span><span class="sz-bar st" style="--v:$6;--m:100"><b>$5</b><em>$6%</em><span class="sz-trk"></span></span><p>$8</p></div>ⓔ')
rule('敌情·别的', r'/§敌情｜([^｜\n]{1,24})｜([^\n]*)/g', '<div class="sz-foe"><div class="f-h"><b>$1</b></div><p>$2</p></div>ⓔ')
rule('史诗', r'/§史诗｜([^｜\n]{1,30})｜([^\n]{0,20})/', '<div class="sz-foe boss" data-th="致命"><div class="f-h"><b>$1</b><em>$2</em></div>ⓔ')
rule('史诗势', r'/§史诗势｜([^｜\n·]{0,8})·(\d{1,3})｜([^｜\n·]{0,8})·(\d{1,3})/',
     '<span class="sz-bar hp" style="--v:$2;--m:100"><b>$1</b><em>$2%</em><span class="sz-trk"></span></span><span class="sz-bar st" style="--v:$4;--m:100"><b>$3</b><em>$4%</em><span class="sz-trk"></span></span></div>ⓔ')
rule('史诗况', r'/§史诗况｜([^\n]{1,200})/g', '<div class="sz-wn"><span>$1</span></div>ⓔ')
rule('战况', r'/§战况｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-wn" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')

# ---- 拆行：一行几段的一次拆开，括号里的竖线不算；行尾记号写着这一段叫什么字 ----
NOPAR = '(?![^（\\n]*）)'
rule('拆行·去句尾', r'/[。；\s]+(?=ⓜ)/g', '')
rule('拆行·竖线', r'/ ?(?:｜| \| ) ?' + NOPAR + r'(?=[^\n]*ⓛ([^\n｜]{1,4})$)/gm', '\n§$1 ')
rule('拆行·带空格的竖线', r'/ (?:｜|\|) ' + NOPAR + r'(?=[^\n]*ⓚ([^\n｜]{1,4})$)/gm', '\n§$1 ')
rule('拆行·连分句', r'/ ?(?:[｜；。]| \| ) ?' + NOPAR + r'(?=[^\n]*ⓜ([^\n｜]{1,4})$)/gm', '\n§$1 ')
rule('拆行·顿号', r'/、(?=[^\n]*ⓝ([^\n｜]{1,4})$)/gm', '\n§$1 ')
rule('拆行·去记号', r'/[ⓛⓚⓜⓝ][^\n｜]{1,4}$/gm', '')
# ---- 拆出来的一行一条 ----
rule('推演·键值', r'/^§条 ([^：\n]{1,12})：([^\n]*)$/gm', '<i><b>$1</b>$2</i>ⓔ')
rule('推演·一句', r'/^§条 ([^\n]*)$/gm', '<i>$1</i>ⓔ')
rule('日报·条', r'/^§报 ([^\n]*)$/gm', '<span class="d-i">$1</span>ⓔ')
rule('情报·条', r'/^§情 ([^（\n]*)（(?:来源[：:])?([^，,）\n]{1,24})[，,] ?可信度[：: ]?([^）\n]{1,6})）([^\n]*)$/gm',
     '<div class="in-i" data-c="$3"><span>$1$4</span><small><i class="in-s">$2</i><em><i></i>可信度 $3</em></small></div>ⓔ')
rule('情报·条·别的', r'/^§情 ([^\n]*)$/gm', '<div class="in-i"><span>$1</span></div>ⓔ')
rule('风闻·条', r'/^§闻 ([^\n]*)（([^）\n]{1,18})）$/gm', '<span class="ru-i">$1<small>$2</small></span>ⓔ')
rule('风闻·条·别的', r'/^§闻 ([^\n]*)$/gm', '<span class="ru-i">$1</span>ⓔ')
rule('可接·条', r'/^§接 ([^（\n]{1,30})（([^，,）\n]{1,12})[，,] ?([^）\n]{1,24})） *$/gm', '<span class="sz-slip"><b>$1</b><i>$2</i><em>$3</em></span>ⓔ')
rule('可接·条·别的', r'/^§接 ([^\n]*)$/gm', '<span class="sz-slip"><b>$1</b></span>ⓔ')
rule('线索·条', r'/^§索 ([^\n]*)$/gm', '<span class="sz-note">$1</span>ⓔ')
rule('已完成·条', r'/^§成 ([^→\n]*)→([^→\n]*)→([^\n]*)$/gm', '<div class="sz-mm" data-k="已完成"><b>$1</b><span>$2</span><em>$3</em></div>ⓔ')
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
# ---- 收尾：漏网的竖线（只认正文字，不碰属性值）换成中点；收最后一页，底下一排页签（手札加七个），去掉行尾记号并成一块 ----
rule('竖线收尾', r'/ ?(?:｜| \| ) ?(?=[^<>\n]*<)' + G + '/g', ' · ')
TABS = [('prose', '手札'), ('panel', '面板'), ('deed', '伟业'), ('bag', '背包'), ('party', '同行'), ('news', '见闻'), ('mem', '记忆'), ('war', '战斗')]
NAV = '<nav class="sz-tabs">' + ''.join('<label class="sz-tab t-%s"><input type="radio" name="sz-tab"><i></i><b>%s</b></label>' % t for t in TABS) + '</nav>'
rule('收卷', r'/\s*ⓩ\s*$/', CLOSE + NAV)
rule('并块', r'/ⓔ\s*/g', '')
json.dump(R, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(R))
