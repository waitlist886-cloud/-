# 手札版的展开正则（状态栏方向稿第三版的样张，不进卡）。用法：python3 -I -X utf8 make_rules_shouzha.py 输出.json
# 跟第二版那三十五条同一个路子：只认 §底座 打头的回复，一条规则只吃自己那一行，行尾留 ⓔ，最后并成一整块。
# 不同的是展开成新类名（sz-），旧样式碰不到；各栏收成页签：开头是标题、地点年份和三条，中间是手札正文和分支，底下一排页签，
# 点哪一个，那一栏在页签上方展开，一次只开一栏。整条回复第一个字就是 <details，Markdown 认它是一整块 HTML。
import json, sys
R = []
def rule(name, rx, rep):
    R.append({"name": name, "regex": rx, "replaceString": rep, "enabled": True, "messageRole": "assistant", "applyMode": "front-end"})
G = r'(?=[\s\S]*ⓩ)'
X = '<label class="sz-x"><input type="radio" name="sz-tab">收起</label>'
# ---- 预处理（同第二版）----
rule('帧记号', r'/^(\s*§底座｜[\s\S]*)$/', '$1\nⓩ')
rule('去回车', r'/\r/g', '')
rule('去行首空白', r'/^[ \t　]+' + G + '/gm', '')
rule('记录行的半角竖线', r'/^(§[^\n|]{1,12})\|' + G + '/gm', '$1｜')
rule('记录行的尖括号', r'/^(§[^\n<]{0,400})<' + G + '/gm', '$1＜')
# ---- 手札的头：标题、地点和纪年、三条（ⓑ 是三条的位置）；点开是推演底座 ----
HEAD = ('<details class="sz-hud"><summary class="sz-head"><b class="sz-title"><span></span></b>'
        '<span class="sz-sub"><span class="sz-place">%s</span><span class="sz-year">%s</span>%s</span>ⓑ<span class="sz-more">推演</span></summary>'
        '<div class="sz-hud-body">')
rule('底座加环境',
     r'/^§底座｜纪元：((([^\s·\n]{3,14})(·[^\s\n]{1,40}|)) · (\d{1,2}[:：]\d{2})\s?([^\n·]{0,20})· ([^\s\n]{1,40}) · ([^\s\n]{1,40}) · 防抢话 (开|关) · 档位 ([^\s\n]{1,6}))\s*\n§环境｜([^｜\n]{1,60})｜([^\n]{0,80})$/m',
     HEAD % ('$7', '$3', '<span class="sz-time">$5</span>') +
     '<div class="sz-grid"><div><b>日期</b>$2</div><div><b>时辰</b>$5 $6 · $12</div><div><b>天气</b>$11</div><div><b>地点</b>$7</div><div><b>潮汐</b>$8</div><div><b>档位</b>$10 · 防抢话 $9</div></div>ⓔ')
rule('底座单行', r'/^§底座｜纪元：([^\n]{4,160})$/m', HEAD % ('$1', '', '') + 'ⓔ')
# 纪元（认头上的纪年；纷争纪末月写山铜纪元年归纷争纪，山铜纪末月写迷宫纪元年归山铜纪，迷宫纪2到1000年是前传）
for cls, rx in [('era-moon', '月银纪\\d'), ('era-strife', '(?:纷争纪\\d|山铜纪元年)'), ('era-bronze', '(?:山铜纪\\d|迷宫纪元年)'),
                ('era-pre', '迷宫纪(?:[2-9]|[1-9]\\d|[1-9]\\d\\d|1000)年'), ('era-maze', '迷宫纪(?:100[1-9]|10[1-9]\\d|1[1-9]\\d\\d|[2-9]\\d{3})年')]:
    rule('纪元·' + cls, r'/(<summary class="sz-head">)(?=[^\n]{0,600}<span class="sz-year">%s)/' % rx, '$1<i class="sz-era %s"></i>' % cls)
# 钟点进整页变量（整页跟着最新一条），顺带开总开关
rule('钟点', r'/(<summary class="sz-head">)(?=[^\n]{0,700}<span class="sz-time">(\d{1,2})[:：](\d{2}))/',
     '$1<style>.custom-styles{--sz-on:1;--sz-h:$2;--sz-m:$3}</style>')
# 三条：往后看面板的资源那一行，数照写，条由样式按数算
BAR = '<span class="sz-bar %s" style="--v:$%d;--m:$%d"><i></i><b>%s</b><em>$%d / $%d</em><span class="sz-trk"></span></span>'
rule('三条', r'/ⓑ(?=[\s\S]*§面板｜资源｜HP (\d{1,6})\/(\d{1,6}) MP (\d{1,6})\/(\d{1,6}) SP (\d{1,6})\/(\d{1,6}))/',
     '<span class="sz-bars">' + BAR % ('hp', 1, 2, 'HP', 1, 2) + BAR % ('mp', 3, 4, 'MP', 3, 4) + BAR % ('sp', 5, 6, 'SP', 5, 6) + '</span>')
rule('三条·没有', r'/ⓑ/', '')
rule('推演九行', r'/^§推演｜(\d)｜([^｜\n]{1,8})｜([^\n]*)$/gm', '<div class="sz-f d"><b>$1｜$2</b><span>$3</span></div>ⓔ')
rule('功能命令', r'/^§功能｜([^\n]{1,30})$/m', '<div class="sz-f d"><b>功能命令</b><span>$1</span></div>ⓔ')
# ---- 手札正文 ----
rule('正文开卷', r'/^§正文｜([^\n]{1,40})$/m', '</div></details><div class="sz-prose"><div class="sz-sec"><span></span></div><div class="sz-scene">$1</div>ⓔ')
rule('篇章题', r'/(<div class="sz-scene">[^<\n]{1,40}<\/div>ⓔ\s*)([^\n<§｜]{2,10})｜([^\n<§｜]{4,14})\n+([^\n<§｜]{8,80})\n/',
     '$1<div class="sz-qc"><span class="qc-pian">$2</span><b class="qc-ml">$3</b><span class="qc-desc">$4</span></div>ⓔ\n')
rule('段落', r'/^(?!§|<|ⓔ|ⓩ)([^\n]+)$' + G + '/gm', '<p>$1</p>ⓔ')
rule('分支开头', r'/^§分支｜/m', '<div class="sz-choices"><ol>§分支｜')
rule('分支·自定义', r'/§分支｜(自定义行动[^\n]{0,80})/g', '<li class="sz-free"><span>$1</span></li>ⓔ')
rule('分支·可点', r'/^§分支｜([^\n"<]{1,300})$/gm', '<li data-action="set-textinput" data-value="$1"><span>$1</span></li>ⓔ')
rule('分支·带引号', r'/§分支｜([^\n]{1,300})/g', '<li><span>$1</span></li>ⓔ')
# ---- 各栏：开栏时先收上一栏（多出来的收尾符平台会忽略），一行一条 ----
CLOSE = '</ol></details></div></div></div></div></section>'
PANES = [('面板', 'panel', '冒险者面板'), ('伟业', 'deed', '成长与伟业'), ('背包', 'bag', '背包'),
         ('见闻', 'news', '冒险见闻'), ('记忆', 'mem', '记忆')]
for name, key, title in PANES:
    rule(name + '开栏', r'/^§%s｜/m' % name,
         CLOSE + '<section class="sz-pane p-%s"><div class="sz-pane-head"><i></i><b>%s</b>%s</div><div class="sz-pane-body">§%s｜' % (key, title, X, name))
    rule(name + '各行', r'/§%s｜([^｜\n]{1,8})｜([^\n]*)/g' % name, '<div class="sz-f" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
# 同行（角色卡）：§角色｜名｜种族/年龄/性别｜立绘:短名 或 名牌 或 路人
rule('同行开栏', r'/^§角色｜/m',
     CLOSE + '<section class="sz-pane p-party"><div class="sz-pane-head"><i></i><b>同行与在场</b>%s</div><div class="sz-pane-body"><div class="sz-npcs"><div hidden><div>§角色｜' % X)
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
# ---- 收尾：收最后一栏，底下一排页签，去掉行尾记号并成一块 ----
TABS = [('panel', '面板'), ('deed', '伟业'), ('bag', '背包'), ('party', '同行'), ('news', '见闻'), ('mem', '记忆'), ('war', '战斗')]
NAV = '<nav class="sz-tabs">' + ''.join('<label class="sz-tab t-%s"><input type="radio" name="sz-tab"><i></i><b>%s</b></label>' % t for t in TABS) + '</nav>'
rule('收卷', r'/\s*ⓩ\s*$/', CLOSE + NAV)
rule('并块', r'/ⓔ\s*/g', '')
json.dump(R, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(R))
