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
rule('推演九行', r'/^§推演｜(\d)｜([^｜\n]{1,8})｜([^\n]*)$/gm', '<div class="sz-f d"><b>$1｜$2</b><span>$3</span></div>ⓔ')
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
DOLL = ('<div class="sz-doll"><i class="sz-doll-ring"></i><i class="sz-doll-fig"></i>' +
        ''.join('<span class="sz-sk" data-s="%s"><i class="sz-ic"></i><small>%s</small></span>' % (s, s) for s in SLOTS) +
        '</div><label class="sz-arch-t"><input type="checkbox"><span>档案 · 容貌与姿态</span></label>')
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
# ---- 面板 ----
rule('面板·身份', r'/§面板｜身份｜([^｜\n]{1,20})｜([^｜\n]{0,20})｜([^｜\n]{0,10})｜([^｜\n]{0,8})｜([^｜\n]{0,30})｜([^\n]{0,40})/',
     '<div class="sz-f sz-idc" data-k="身份"><b class="sz-who">$1</b><span class="sz-tags"><i>$2</i><i>$3</i><i>$4</i><i class="vow">$5</i><i>$6</i></span></div>ⓔ')
rule('面板·容貌', r'/§面板｜容貌｜([^\n]*)/', '<div class="sz-f sz-more" data-k="容貌"><b>容貌</b><span>$1</span></div>ⓔ')
rule('面板·姿态', r'/§面板｜姿态｜([^\n]*)/', '<div class="sz-f sz-more" data-k="姿态"><b>姿态</b><span>$1</span></div>ⓔ')
rule('面板·着装', r'/§面板｜着装｜([^｜\n"]{0,40})｜([^｜\n"]{0,40})｜([^｜\n"]{0,40})｜([^｜\n"]{0,40})｜([^\n]{0,60})/',
     ''.join(slot(p, '着装', '$%d' % k, p + ' · 着装', '', '', ' sz-cl') for p, k in [('外层', 1), ('内层', 2), ('足', 3), ('配饰', 4)]) +
     '<div class="sz-f sz-more" data-k="此刻"><b>此刻</b><span>$5</span></div>ⓔ')
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
OUT = ''.join('<i tabindex="0"><b>$%d</b><strong>$%d</strong><small>$%d</small></i>' % (3 * k + 1, 3 * k + 2, 3 * k + 3) for k in range(6))
AV = ';'.join('--a%d:$%d' % (k + 1, 3 * k + 2) for k in range(6))
rule('面板·六维', r'/§面板｜六维｜' + '｜'.join([CELL] * 6) + '/',
     '<div class="sz-f sz-six" data-k="六维" style="%s"><span class="sz-radar"><i class="r-g"></i><i class="r-v"></i></span><span class="sz-cells">%s</span></div>ⓔ' % (AV, OUT))
rule('面板·攻防', r'/§面板｜攻防｜ATK (\d{1,6}) · MAG (\d{1,6}) · PV (\d{1,6}) · DV (\d{1,6})｜([^\n]*)/',
     '<div class="sz-f sz-atk" data-k="攻防"><span class="sz-atks"><i data-a="atk"><b>ATK</b><strong>$1</strong></i><i data-a="mag"><b>MAG</b><strong>$2</strong></i><i data-a="pv"><b>PV</b><strong>$3</strong></i><i data-a="dv"><b>DV</b><strong>$4</strong></i></span><small class="sz-resist">$5</small></div>ⓔ')
rule('面板·命路', r'/§面板｜命路｜([^｜\n]{0,20})｜(?:职业 )?([^｜\n]{0,20})｜(?:命星 )?([^\n]{0,30})/',
     '<div class="sz-f sz-road" data-k="命路"><span><small>命路</small><b>$1</b></span><span><small>职业</small><b>$2</b></span><span><small>命星</small><b>$3</b></span></div>ⓔ')
rule('面板·旅印', r'/§面板｜旅印｜([^｜\n]{0,20})｜巴尔 (\d{1,9}) 索恩 (\d{1,9}) 便士 (\d{1,9})｜([^｜\n]{0,20})｜([^\n]{0,40})/',
     '<div class="sz-f sz-seal" data-k="旅印"><span class="sz-sealb"><i></i><b>$1</b></span>' + COINS + '<span class="sz-tags"><i>$5</i><i>$6</i></span></div>ⓔ')
rule('面板·委托空', r'/§面板｜委托｜无[ ｜][^\n]*/', 'ⓔ')
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
# ---- 见闻、记忆：一行一种，写「无」的不出 ----
rule('MOD', r'/§MOD｜([^｜\n]{1,12})｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-nw" data-k="MOD"><b>$1 · $2</b><span>$3</span></div>ⓔ')
rule('见闻空', r'/§见闻｜[^｜\n]{1,8}｜(?:无|暂无)$/gm', 'ⓔ')
rule('见闻各行', r'/§见闻｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-nw" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
rule('记忆空', r'/§记忆｜[^｜\n]{1,8}｜(?:无|暂无)$/gm', 'ⓔ')
rule('记忆·短期', r'/§记忆｜(短期|长期|核心)｜\[(\d{1,4})\]（([^）\n]{1,40})）([^\n]*)/g', '<div class="sz-mm" data-k="$1"><i class="m-n">$2</i><time>$3</time><span>$4</span></div>ⓔ')
rule('记忆·因果', r'/§记忆｜未结因果｜\[([^\]\n]{1,20})\]([^\n]*)/g', '<div class="sz-mm" data-k="未结因果"><time>$1</time><span>$2</span></div>ⓔ')
rule('记忆各行', r'/§记忆｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-mm" data-k="$1"><time>$1</time><span>$2</span></div>ⓔ')
# ---- 同行（角色卡）：头像一排，点谁看谁；状态、羁绊拆成条，别的收进档案 ----
NPC = ('</div></div><div class="sz-npc"%s><label class="sz-av"><input type="radio" name="sz-np"><i data-n="$1"></i><b>$1</b></label>'
       '<div class="sz-npc-b"><div class="sz-npc-name"><b>$1</b><span>$2</span><label class="sz-npc-t"><input type="checkbox"><span>档案</span></label></div>ⓔ')
rule('角色·立绘', r'/§角色｜([^｜\n]{1,20})｜([^｜\n]{1,40})｜立绘[:：]([^｜\n]{1,8})/g', NPC % ' data-portrait="$3"')
rule('角色·名牌', r'/§角色｜([^｜\n]{1,20})｜([^｜\n]{1,40})｜名牌/g', NPC % '')
rule('角色·路人', r'/§角色｜([^｜\n]{1,20})｜([^｜\n]{1,40})(?:｜路人)?$/gm', NPC % ' data-walkon="1"')
rule('角色签', r'/§角色签｜([^｜\n]{0,30})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,12})$/gm',
     '<div class="sz-npc-tags"><span class="lv">$3</span><span>$4</span><span>$1</span><span>$2</span><span>$5</span><span class="met">$6</span></div>ⓔ')
rule('角色话', r'/§角色话｜([^\n]{1,200})/g', '<p class="sz-npc-say">$1</p>ⓔ')
NB = '<span class="sz-bar %s" style="--v:$%d;--m:$%d"><b>%s</b><em>$%d / $%d</em><span class="sz-trk"></span></span>'
rule('角色·状态', r'/§角色行｜状态｜HP (\d{1,6})\/(\d{1,6}) MP (\d{1,6})\/(\d{1,6}) SP (\d{1,6})\/(\d{1,6}) 架势 (\d{1,6})\/(\d{1,6})(?: ｜ )?([^\n]{0,60})/g',
     '<div class="sz-npc-st"><span class="sz-res-bars">' + NB % ('hp', 1, 2, 'HP', 1, 2) + NB % ('mp', 3, 4, 'MP', 3, 4) + NB % ('sp', 5, 6, 'SP', 5, 6) + NB % ('st', 7, 8, '架势', 7, 8) + '</span><small>$9</small></div>ⓔ')
rule('角色·羁绊', r'/§角色行｜羁绊｜好感 Lv\.(\d{1,2}) ([^｜\n]{1,20}) (\d{1,5})\/(\d{1,5})(?: ｜ )?([^\n]{0,60})/g',
     '<div class="sz-bond" style="--v:$3;--m:$4"><i></i><b>Lv.$1</b><span>$2</span><em>$3 / $4</em><span class="sz-trk"></span><small>$5</small></div>ⓔ')
rule('角色行', r'/§角色行｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-nf" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
rule('角色细', r'/§角色细｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-nf" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
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
# ---- 收尾：收最后一页，底下一排页签（手札加七个），去掉行尾记号并成一块 ----
TABS = [('prose', '手札'), ('panel', '面板'), ('deed', '伟业'), ('bag', '背包'), ('party', '同行'), ('news', '见闻'), ('mem', '记忆'), ('war', '战斗')]
NAV = '<nav class="sz-tabs">' + ''.join('<label class="sz-tab t-%s"><input type="radio" name="sz-tab"><i></i><b>%s</b></label>' % t for t in TABS) + '</nav>'
rule('收卷', r'/\s*ⓩ\s*$/', CLOSE + NAV)
rule('并块', r'/ⓔ\s*/g', '')
json.dump(R, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(R))
