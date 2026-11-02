# 大框版的展开正则（状态栏方向稿第四版的样张，不进卡）。用法：python3 -I -X utf8 make_rules_frame.py 输出.json
# 路子同第二版：只认 §底座 打头的回复，一条规则只吃自己那一行，行尾留 ⓔ，最后并成一整块 HTML（头一个字是 <details）。
# 第四版的结构：一条回复里有一页手札（正文和分支）和七页模块（面板、伟业、背包、同行、见闻、记忆、战斗），
# 末尾一排页签（手札加七个）。页签是全页同一组单选钮，开哪一页由样式决定；只有最新一条回复的页签露出来。
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
# ---- 七页模块：开页时先收上一页（多出来的收尾符平台会忽略），一行一条 ----
CLOSE = '</ol></details></div></div></div></div></section>'
def opener(name, key, title, extra=''):
    rule(name + '开页', r'/^§%s｜/m' % name,
         CLOSE + '<section class="sz-page sz-pane p-%s"><div class="sz-pane-head"><i></i><b>%s</b>%s</div><div class="sz-pane-body">%s§%s｜' % (key, title, BACK, extra, name))
opener('面板', 'panel', '冒险者面板')
# 面板里三行拆成部件：位阶（等级章加经验条）、资源（四条）、六维（六格）；对不上的照通用行出
rule('面板·位阶', r'/§面板｜位阶｜LVL (\d{1,3}) ([^｜\n]{1,20})｜EXP (?:EXP )?(\d{1,9})\/(\d{1,9})｜([^\n]{0,40})/',
     '<div class="sz-f sz-lv" data-k="位阶" style="--v:$3;--m:$4"><b>位阶</b><span class="sz-lvl"><small>LVL</small>$1</span><span class="sz-tier">$2</span><em>EXP $3 / $4</em><span class="sz-trk"></span><small class="sz-note">$5</small></div>ⓔ')
RB = '<span class="sz-bar %s" style="--v:$%d;--m:$%d"><b>%s</b><em>$%d / $%d</em><span class="sz-trk"></span></span>'
rule('面板·资源', r'/§面板｜资源｜HP (\d{1,6})\/(\d{1,6}) MP (\d{1,6})\/(\d{1,6}) SP (\d{1,6})\/(\d{1,6}) 架势 (\d{1,6})\/(\d{1,6})｜([^\n]*)/',
     '<div class="sz-f sz-res" data-k="资源"><b>资源</b><span class="sz-res-bars">' + RB % ('hp', 1, 2, 'HP', 1, 2) + RB % ('mp', 3, 4, 'MP', 3, 4) + RB % ('sp', 5, 6, 'SP', 5, 6) + RB % ('st', 7, 8, '架势', 7, 8) + '</span><span class="sz-chips">$9</span></div>ⓔ')
RP = '<span class="sz-bar %s" style="--v:$%d;--m:100"><b>%s</b><em>$%d%%</em><span class="sz-trk"></span></span>'
rule('面板·资源·百分', r'/§面板｜资源｜HP (\d{1,3})% MP (\d{1,3})% SP (\d{1,3})% 架势 (\d{1,3})%｜([^\n]*)/',
     '<div class="sz-f sz-res" data-k="资源"><b>资源</b><span class="sz-res-bars">' + RP % ('hp', 1, 'HP', 1) + RP % ('mp', 2, 'MP', 2) + RP % ('sp', 3, 'SP', 3) + RP % ('st', 4, '架势', 4) + '</span><span class="sz-chips">$5</span></div>ⓔ')
CELL = '([A-Z]{2,4}) (\\d{1,4})([^｜\\n]{0,30})'
OUT = ''.join('<i><b>$%d</b><strong>$%d</strong><small>$%d</small></i>' % (3 * k + 1, 3 * k + 2, 3 * k + 3) for k in range(6))
rule('面板·六维', r'/§面板｜六维｜' + '｜'.join([CELL] * 6) + '/', '<div class="sz-f sz-six" data-k="六维"><b>六维</b><span class="sz-cells">' + OUT + '</span></div>ⓔ')
rule('面板各行', r'/§面板｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-f" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
opener('伟业', 'deed', '成长与伟业')
rule('伟业各行', r'/§伟业｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-f" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
# 背包：一行一类，东西拆成一格一格（顿号或者「 ｜ 」分开，八遍拆八格）
opener('背包', 'bag', '背包与仓库')
rule('背包各行', r'/§背包｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-f sz-bagrow" data-k="$1"><b>$1</b><span class="sz-slots"><i>$2</i></span></div>ⓔ')
for k in range(8):
    rule('背包·拆格%d' % (k + 1), r'/(<span class="sz-slots"><i>[^\n]*)(?:、| ｜ )/g', '$1</i><i>')
opener('见闻', 'news', '冒险见闻')
rule('见闻各行', r'/§见闻｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-f" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
opener('记忆', 'mem', '记忆')
rule('记忆各行', r'/§记忆｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-f" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
# 同行（角色卡）：§角色｜名｜种族/年龄/性别｜立绘:短名 或 名牌 或 路人
rule('同行开页', r'/^§角色｜/m',
     CLOSE + '<section class="sz-page sz-pane p-party"><div class="sz-pane-head"><i></i><b>同行与在场</b>%s</div><div class="sz-pane-body"><div class="sz-npcs"><div hidden><div>§角色｜' % BACK)
NPC = '</details></div></div><div class="sz-npc"%s><div class="sz-npc-av" data-n="$1"></div><div class="sz-npc-main"><div class="sz-npc-name"><b>$1</b><span>$2</span></div>ⓔ'
rule('角色·立绘', r'/§角色｜([^｜\n]{1,20})｜([^｜\n]{1,40})｜立绘[:：]([^｜\n]{1,8})/g', NPC % ' data-portrait="$3"')
rule('角色·名牌', r'/§角色｜([^｜\n]{1,20})｜([^｜\n]{1,40})｜名牌/g', NPC % '')
rule('角色·路人', r'/§角色｜([^｜\n]{1,20})｜([^｜\n]{1,40})(?:｜路人)?$/gm', NPC % ' data-walkon="1"')
rule('角色签', r'/§角色签｜([^｜\n]{0,30})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,12})$/gm',
     '<div class="sz-npc-tags"><span>$1 ｜ $2</span><span>$3</span><span>$4</span><span>$5</span><span>$6</span></div>ⓔ')
rule('角色话', r'/§角色话｜([^\n]{1,200})/g', '<p class="sz-npc-say">“$1”</p>ⓔ')
rule('角色行', r'/§角色行｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-nf" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
rule('角色细·开折', r'/(<div class="sz-nf" data-k="[^"\n]{1,8}"><b>[^<\n]{1,8}<\/b><span>[^\n]*ⓔ\n)(?=§角色细)/g',
     '$1<details class="sz-more2"><summary>装备·能力·职业</summary>')
rule('角色细', r'/§角色细｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="sz-nf more" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
# ---- 收尾：收最后一页，底下一排页签（手札加七个），去掉行尾记号并成一块 ----
TABS = [('prose', '手札'), ('panel', '面板'), ('deed', '伟业'), ('bag', '背包'), ('party', '同行'), ('news', '见闻'), ('mem', '记忆'), ('war', '战斗')]
NAV = '<nav class="sz-tabs">' + ''.join('<label class="sz-tab t-%s"><input type="radio" name="sz-tab"><i></i><b>%s</b></label>' % t for t in TABS) + '</nav>'
rule('收卷', r'/\s*ⓩ\s*$/', CLOSE + NAV)
rule('并块', r'/ⓔ\s*/g', '')
json.dump(R, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(R))
