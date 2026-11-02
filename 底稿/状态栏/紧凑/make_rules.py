# 紧凑记法展开成卷面的显示正则（方向稿第二版的样张，不进卡）。用法：python3 -I -X utf8 make_rules.py 输出.json
# 只认 §底座 打头的回复；一条规则只吃自己那一行，行尾留 ⓔ，最后一条把 ⓔ 连同后面的空白一起拿掉，并成一整块 HTML。
import json, sys
R = []
def rule(name, rx, rep):
    R.append({"name": name, "regex": rx, "replaceString": rep, "enabled": True, "messageRole": "assistant", "applyMode": "front-end"})
G = r'(?=[\s\S]*ⓩ)'      # 只动打了帧记号的回复
# ---- 预处理 ----
rule('帧记号', r'/^(\s*§底座｜[\s\S]*)$/', '$1\nⓩ')
rule('去回车', r'/\r/g', '')
rule('去行首空白', r'/^[ \t　]+' + G + '/gm', '')
rule('记录行的半角竖线', r'/^(§[^\n|]{1,12})\|' + G + '/gm', '$1｜')
rule('记录行的尖括号', r'/^(§[^\n<]{0,400})<' + G + '/gm', '$1＜')
# ---- 推演底座：底座一行加环境一行，摘要和六格一起出 ----
rule('底座加环境',
     r'/^§底座｜纪元：(([^\s\n]{4,40}) · (\d{1,2}[:：]\d{2})\s?([^\n·]{0,20})· ([^\s\n]{1,40}) · ([^\s\n]{1,40}) · 防抢话 (开|关) · 档位 ([^\s\n]{1,6}))\s*\n§环境｜([^｜\n]{1,60})｜([^\n]{0,80})$/m',
     '<details class="arc-hud-details"><summary class="arc-hud-summary"><div class="hud-summary-inner"><span class="hud-title-icon">✦</span><b>推演底座</b><span class="hud-meta">$1</span></div></summary><div class="detail-body arc-hud-body"><div class="hud-grid"><div><b>日期</b><br>$2</div><div><b>时辰</b><br>$3 · $10</div><div><b>天气</b><br>$9</div><div><b>地点</b><br>$5</div><div><b>潮汐</b><br>$6</div><div><b>防抢话</b><br>$7</div></div><div class="ap">ⓔ')
rule('底座单行', r'/^§底座｜纪元：([^\n]{4,160})$/m',
     '<details class="arc-hud-details"><summary class="arc-hud-summary"><div class="hud-summary-inner"><span class="hud-title-icon">✦</span><b>推演底座</b><span class="hud-meta">$1</span></div></summary><div class="detail-body arc-hud-body"><div class="ap">ⓔ')
rule('推演九行', r'/^§推演｜(\d)｜([^｜\n]{1,8})｜([^\n]*)$/gm', '<div class="f d"><b>$1｜$2</b>$3</div>ⓔ')
rule('功能命令', r'/^§功能｜([^\n]{1,30})$/m', '<div class="f d"><b>功能命令</b>$1</div>ⓔ')
# ---- 正文 ----
rule('正文开卷', r'/^§正文｜([^\n]{1,40})$/m', '</div></div></details><div class="arc-prose"><div class="arc-prose-head"><span>$1</span></div>ⓔ')
rule('篇章题', r'/(<div class="arc-prose-head"><span>[^<\n]{1,40}<\/span><\/div>ⓔ\s*)([^\n<§｜]{2,10})｜([^\n<§｜]{4,14})\n+([^\n<§｜]{8,80})\n/',
     '$1<div class="qc"><span class="qc-pian">$2</span><b class="qc-ml">$3</b><span class="qc-desc">$4</span></div>ⓔ\n')
rule('段落', r'/^(?!§|<|ⓔ|ⓩ)([^\n]+)$' + G + '/gm', '<p>$1</p>ⓔ')
rule('分支开头', r'/^§分支｜/m', '<div class="choices"><div class="choices-title">行动分支</div><ol>§分支｜')
rule('分支', r'/§分支｜([^\n]{1,300})/g', '<li>$1</li>ⓔ')
# ---- 各张卡：头一行开卡，各行一条；开卡时先收上一张（多出来的收尾符平台会忽略） ----
CARDS = [('面板', 'arc-panel', 'panel', '◈', '冒险者面板', ' open'), ('伟业', 'arc-deed-panel', 'deed', '✦', '成长与伟业', ''),
         ('背包', 'arc-bag', 'bag', '▤', '背包', ' open'), ('见闻', 'arc-daily', 'daily', '☼', '冒险见闻', ' open'),
         ('记忆', 'arc-memory', 'memory', '❖', '记忆', '')]
CLOSE = '</ol></div></div></div></div></details>'
for name, cls, short, icon, title, op in CARDS:
    rule(name + '开卡', r'/^§%s｜/m' % name,
         CLOSE + '<details class="%s"%s><summary class="%s-summary"><div class="%s-summary-inner"><span class="%s-title-icon">%s</span><b>%s</b></div></summary><div class="detail-body %s-body"><div class="ap">§%s｜' % (cls, op, cls, short, short, icon, title, cls, name))
    rule(name + '各行', r'/§%s｜([^｜\n]{1,8})｜([^\n]*)/g' % name, '<div class="f" data-k="$1"><b>$1</b>$2</div>ⓔ')
# 角色：一张卡开头是 §角色｜名｜种族/年龄/性别｜立绘或名牌或路人
rule('角色开卡', r'/^§角色｜/m',
     CLOSE + '<details class="arc-npc-panel" open><summary class="arc-npc-summary"><div class="npc-summary-inner"><span class="npc-title-icon">◈</span><b>当前主要角色</b></div></summary><div class="detail-body arc-npc-body"><div class="arc-npc-list"><div hidden><div>§角色｜')
rule('角色·立绘', r'/§角色｜([^｜\n]{1,20})｜([^｜\n]{1,40})｜立绘[:：]([^｜\n]{1,8})/g',
     '</details></div></div><div class="arc-npc-card" data-arc-portrait="$3"><div class="arc-npc-avatar" aria-label="$3立绘"></div><div class="arc-npc-main"><div class="arc-npc-name"><b>$1</b><span>$2</span></div>ⓔ')
rule('角色·名牌', r'/§角色｜([^｜\n]{1,20})｜([^｜\n]{1,40})｜名牌/g',
     '</details></div></div><div class="arc-npc-card"><div class="arc-npc-avatar" data-n="$1"></div><div class="arc-npc-main"><div class="arc-npc-name"><b>$1</b><span>$2</span></div>ⓔ')
rule('角色·路人', r'/§角色｜([^｜\n]{1,20})｜([^｜\n]{1,40})(?:｜路人)?$/gm',
     '</details></div></div><div class="arc-npc-card"><div class="arc-npc-main"><div class="arc-npc-name"><b>$1</b><span>$2</span></div>ⓔ')
rule('角色签', r'/§角色签｜([^｜\n]{0,30})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,20})｜([^｜\n]{0,12})$/gm',
     '<div class="arc-npc-tags"><span>$1 ｜ $2</span><span>$3</span><span>$4</span><span>$5</span><span>$6</span></div>ⓔ')
rule('角色话', r'/§角色话｜([^\n]{1,200})/g', '<p>“$1”</p>ⓔ')
rule('角色行', r'/§角色行｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="nf" data-k="$1"><b>$1</b>$2</div>ⓔ')
rule('角色细·开折', r'/(<div class="nf" data-k="[^"\n]{1,8}"><b>[^<\n]{1,8}<\/b>[^\n]*ⓔ\n)(?=§角色细)/g', '$1<details class="arc-npc-more"><summary><b>装备·能力·职业</b></summary>')
rule('角色细', r'/§角色细｜([^｜\n]{1,8})｜([^\n]*)/g', '<div class="nf more" data-k="$1"><b>$1</b>$2</div>ⓔ')
# ---- 收尾：最后一张卡收口，去掉行尾记号，并成一块 ----
rule('收卷', r'/\s*ⓩ\s*$/', CLOSE + '</div></div>')
rule('并块', r'/ⓔ\s*/g', '')
json.dump(R, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(R))
