# 《大旻长夜》日里版：紧凑记录行展开成“大框”版的显示正则（11-03 用户定：浮雕加界面加页签，纯 SVG）。
# 用法：python3 -I -X utf8 make_rules_frame_dm.py 输出.json
# 跟 make_rules_dm.py 同一套记录行，展开成：一条推演细条（点开是玄枢推演）、一页行卷（含天机验算）、一块行止抉择，
# 几页模块（玉牒、群英、照影、风闻、经纬、藏卷）平时收着，回复末尾一排页签，点哪页那页顶替行卷。
# 路子照 rili-statusbar-regex-expansion：只动带 § 记录的回复；先在消息末尾打帧记号 ⓩ，
# 预处理（去回车、行首空白、半角竖线和尖括号），再按记录行的连排自动插面板头 ⓟ 和分节头 ⓢ，
# 一条规则只吃自己那一行、行尾留 ⓔ，最后把 ⓔ 连同后面的空白一起拿掉，并成一整块 HTML。
# 面板之间靠 CLOSE 收口：多出来的收尾符在最外层会被忽略。所有面板、行卷都是最外层的兄弟。
import json, sys

R = []
def rule(name, rx, rep):
    R.append({"name": name, "regex": rx, "replaceString": rep, "enabled": True,
              "messageRole": "assistant", "applyMode": "front-end"})

G = r'(?=[\s\S]*[ⓩⓨ])'
REC = '枢卷验身命技赋缘私物业事详项简铭讯向策限雷候州近经因刻档存评示'
CLOSE = '</div></section></div></section></article></details>'
F = '([^｜\\n]*)'          # 一栏
REST = '([^\\n]*)'         # 余下整行

# ---- 预处理 ----
rule('帧记号·叙事轮', r'/^(?=[\s\S]*§卷｜)([\s\S]*)$/', '$1\nⓩ')
rule('帧记号·功能轮', r'/^(?![\s\S]*ⓩ)(?=[\s\S]*§[%s]｜)([\s\S]*)$/' % REC, '$1\nⓨ')
rule('去回车', r'/\r/g', '')
rule('去行首空白', r'/^[ \t　]+' + G + '/gm', '')
rule('半角竖线', r'/\|' + G + '/g', '｜')
rule('尖括号左', r'/<' + G + '/g', '＜')
rule('尖括号右', r'/>' + G + '/g', '＞')
rule('半角双引号', r'/"' + G + '/g', '＂')
rule('记录名后的冒号', r'/^§([%s])[:：]/gm' % REC, '§$1｜')

# ---- 连排：面板头 ⓟ（一组记名的头一行前面插一行）----
PANELS = [('枢', '枢'), ('玉牒', '身命技赋缘私物业事'), ('群英', '详项简'), ('照影', '铭'),
          ('风闻', '讯向'), ('行策', '策'), ('经纬', '限雷候州'), ('藏卷', '近经因刻')]
for name, chars in PANELS:
    rule('面板头·%s·开头' % name, r'/^(?=§[%s]｜)/' % chars, 'ⓟ%s\n' % name)
    rule('面板头·%s' % name, r'/^((?!§[%s]｜)[^\n]*)\n(?=§[%s]｜)/gm' % (chars, chars), '$1\nⓟ%s\n' % name)
# ---- 连排：分节头 ⓢ（同一个记名连着的头一行前面插一行）----
SECS = '身命技赋缘私物业事简讯向策限雷候州近经因刻'
for c in SECS:
    rule('分节头·' + c, r'/^((?!§%s｜)[^\n]*)\n(?=§%s｜)/gm' % (c, c), '$1\nⓢ%s\n' % c)

# ---- 正文：不是记录、不是记号的行，一行一段 ----
rule('正文段落', r'/^(?!§|ⓟ|ⓢ|ⓩ|ⓨ)([^\n]+)$' + G + '/gm', '<p>$1</p>ⓔ')

# ---- 面板头展开：推演是顶上一条细条（点开是十二行）；模块一页一页，平时收着；行策跟着行卷 ----
BACK = '<label class="dm-x"><input type="radio" name="dm-tab">返回行卷</label>'
rule('推演细条', r'/^ⓟ枢$/m',
     CLOSE + '<details class="dm-hud"><summary class="dm-head"><span class="dm-hk"><i>枢</i><b>玄枢推演</b></span><span class="dm-bars">ⓐⓒⓓ</span><span class="dm-more">裁分</span></summary>'
     '<div class="dm-pb"><section class="dm-s dm-s0"><div class="dm-sb">ⓔ')
PH = {'玉牒': ('ming', '命主玉牒', '身世·命关·神通·家业'), '群英': ('jian', '群英照鉴', '核心详牒·现场简牒'),
      '照影': ('zhao', '万里照影', '超程铭刻·离场推衍'), '风闻': ('wen', '天下风闻', '山河暗潮·四野勘舆'),
      '经纬': ('li', '天时经纬', '刻限·风雷·夜潮·诸州'), '藏卷': ('cang', '光阴藏卷', '近事·经年·因果·命铭')}
for name, (key, title, sub) in PH.items():
    rule('模块页·' + name, r'/^ⓟ%s$/m' % name,
         CLOSE + '<section class="dm-pane p-%s"><div class="dm-pane-head"><i></i><b>%s</b><small>%s</small>%s</div>'
         '<div class="dm-pb"><section class="dm-s dm-s0"><div class="dm-sb">ⓔ' % (key, title, sub, BACK))
rule('行策块', r'/^ⓟ行策$/m', CLOSE + '<section class="dm-acts-box"><div class="dm-pb"><section class="dm-s dm-s0"><div class="dm-sb">ⓔ')
# 推演细条上的三条：从玉牒“生命状态”那一行读（气血、理性、疯狂），没有就不画
BAR = '<span class="dm-bar %s" style="--v:%s;--m:%s"><b>%s</b><em>%s</em><span class="dm-trk"></span></span>'
rule('三条·气血', r'/ⓐ(?=[\s\S]*\n§命｜生命状态｜[^\n]*气血\s?(\d{1,5})\s?\/\s?(\d{1,5}))/', BAR % ('xue', '$1', '$2', '气血', '$1/$2'))
rule('三条·理性', r'/ⓒ(?=[\s\S]*\n§命｜生命状态｜[^\n]*理性\s?(\d{1,3}))/', BAR % ('li', '$1', '100', '理性', '$1'))
rule('三条·疯狂', r'/ⓓ(?=[\s\S]*\n§命｜生命状态｜[^\n]*疯狂\s?(\d{1,3}))/', BAR % ('kuang', '$1', '100', '疯狂', '$1'))
rule('三条·没有', r'/[ⓐⓒⓓ]/g', '')

# ---- 分节头展开 ----
TH = lambda cells: '<div class="dm-tr dm-th">' + ''.join('<span>%s</span>' % c for c in cells) + '</div>'
SH = {'身': ('profile', '身世名牒', ''), '命': ('realm', '命关天衡', ''), '技': ('skill', '武藏真传', ''),
      '赋': ('ability', '天赋神通', ''), '缘': ('relation', '红尘因果', TH(['人物', '人际关系', '情感状态', '因果与债', '未决事项'])),
      '私': ('romance', '风月私牒', ''), '物': ('inventory', '随身百宝', ''), '业': ('assets', '家业金契', ''),
      '事': ('affairs', '今朝牵系', ''), '简': ('brief', '现场简牒', ''), '讯': ('news', '山河风信', ''),
      '向': ('compass', '四野勘舆', ''), '策': ('actions', '行止抉择', ''), '限': ('deadline', '大势刻限', ''),
      '雷': ('mainline', '当境风雷', ''), '候': ('longnight', '夜潮体感', ''),
      '州': ('regions', '诸州回响', TH(['区域', '州郡风雷', '自然起势', '当前幕次', '最近确报', '与当前因果'])),
      '近': ('near', '近事手札', ''), '经': ('long', '经年纪要', ''), '因': ('open', '未结因果', ''), '刻': ('core', '命途铭刻', '')}
for c, (cls, title, extra) in SH.items():
    rule('分节·' + title, r'/^ⓢ%s$/m' % c,
         '</div></section><section class="dm-s dm-sec-%s"><h3>%s</h3><div class="dm-sb">%sⓔ' % (cls, title, extra))

# ---- 行卷 ----
rule('行卷头', r'/^§卷｜%s｜%s｜%s｜%s｜%s$/m' % (F, F, F, F, REST),
     CLOSE + '<article class="dm-page dm-scroll"><header class="dm-sh"><span class="dm-kicker">$1</span><h2>$2</h2>'
     '<p class="dm-meta"><span class="dm-loc">$3</span><span class="dm-wx">$4</span><span class="dm-cf">$5</span></p></header>'
     '<div class="dm-pb"><section class="dm-s dm-prose"><div class="dm-sb">ⓔ')
rule('行卷头·栏少', r'/^§卷｜%s｜%s$/m' % (F, REST),
     CLOSE + '<article class="dm-page dm-scroll"><header class="dm-sh"><span class="dm-kicker">$1</span><h2>$2</h2></header>'
     '<div class="dm-pb"><section class="dm-s dm-prose"><div class="dm-sb">ⓔ')
rule('天机验算', r'/^§验｜(?:项目[:：])?%s｜(?:有利条件[:：])?%s｜(?:不利条件[:：])?%s｜(?:结果[:：])?%s｜(?:代价与余波[:：])?%s$/m' % (F, F, F, F, REST),
     '</div></section><section class="dm-s dm-check"><h3>天机验算</h3><div class="dm-sb"><div class="dm-cg">'
     '<div><b>项目</b><span>$1</span></div><div><b>有利条件</b><span>$2</span></div><div><b>不利条件</b><span>$3</span></div>'
     '<div class="dm-res" data-r="$4"><b>结果</b><span>$4</span></div></div><p class="dm-cost"><b>代价与余波</b>$5</p>ⓔ')
rule('天机验算·栏少', r'/^§验｜%s$/m' % REST,
     '</div></section><section class="dm-s dm-check"><h3>天机验算</h3><div class="dm-sb"><p>$1</p>ⓔ')

# ---- 玄枢推演 ----
rule('推演', r'/^§枢｜%s｜%s$/gm' % (F, REST), '<div class="dm-row" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')

# ---- 命主玉牒：几行拆成部件，其余照“项｜值”出 ----
CELL = lambda k: '<i><em>%s</em><strong>$%d</strong></i>'
rule('六维', r'/^§命｜六维｜力%s｜体%s｜敏%s｜精%s｜气%s｜神%s$/m' % (F, F, F, F, F, REST),
     '<div class="dm-row dm-six" data-k="六维"><b>六维</b><span class="dm-cells">' +
     ''.join('<i><em>%s</em><strong>$%d</strong></i>' % (k, n + 1) for n, k in enumerate('力体敏精气神')) + '</span></div>ⓔ')
rule('先天', r'/^§命｜先天｜根骨%s｜悟性%s｜资质%s｜魅力%s$/m' % (F, F, F, REST),
     '<div class="dm-row dm-four" data-k="先天"><b>先天</b><span class="dm-cells">' +
     ''.join('<i><em>%s</em><strong>$%d</strong></i>' % (k, n + 1) for n, k in enumerate(['根骨', '悟性', '资质', '魅力'])) + '</span></div>ⓔ')
for k in ['当前境界', '生命状态']:
    rule('拆签·' + k, r'/^§命｜%s｜%s$/m' % (k, REST),
         '<div class="dm-row dm-tagrow" data-k="%s"><b>%s</b><span class="dm-chips"><i>$1</i></span></div>ⓔ' % (k, k))
for n in range(10):
    rule('拆签%d' % (n + 1), r'/(<span class="dm-chips"><i>[^\n]*)｜/g', '$1</i><i>')
for k in ['身上持有', '身上穿戴']:
    rule('拆格·' + k, r'/^§物｜%s｜%s$/m' % (k, REST),
         '<div class="dm-row dm-slotrow" data-k="%s"><b>%s</b><span class="dm-slots"><i>$1</i></span></div>ⓔ' % (k, k))
for n in range(12):
    rule('拆格%d' % (n + 1), r'/(<span class="dm-slots"><i>[^\n]*)、/g', '$1</i><i>')
rule('五幕', r'/^§雷｜州郡主线｜%s｜%s$/m' % (F, REST),
     '<div class="dm-row dm-arc" data-k="州郡主线"><b>州郡主线</b><span><strong>$1</strong><i class="dm-track" data-a="$2"><i></i><i></i><i></i><i></i><i></i></i><em>$2</em></span></div>ⓔ')
rule('资料行', r'/^§([身命私物业事雷])｜%s｜%s$/gm' % (F, REST), '<div class="dm-row" data-k="$2"><b>$2</b><span>$3</span></div>ⓔ')
rule('武藏真传', r'/^§技｜%s｜%s｜(?:来源与类型[:：])?%s｜(?:掌握与实效[:：])?%s｜(?:消耗、限制与联动[:：])?%s｜(?:当前反馈[:：])?%s$/gm' % (F, F, F, F, F, REST),
     '<article class="dm-card dm-skill"><h4><b>$1</b><em>$2</em></h4><p><b>来源与类型</b>$3</p><p><b>掌握与实效</b>$4</p>'
     '<p><b>消耗、限制与联动</b>$5</p><p class="dm-fb"><b>当前反馈</b>$6</p></article>ⓔ')
rule('天赋神通', r'/^§赋｜%s｜%s｜(?:能力效果[:：])?%s｜(?:触发与使用方式[:：])?%s｜(?:边界与联动[:：])?%s｜(?:当前反馈[:：])?%s$/gm' % (F, F, F, F, F, REST),
     '<article class="dm-card dm-ability"><h4><b>$1</b><em>$2</em></h4><p><b>能力效果</b>$3</p><p><b>触发与使用方式</b>$4</p>'
     '<p><b>边界与联动</b>$5</p><p class="dm-fb"><b>当前反馈</b>$6</p></article>ⓔ')
rule('卡·栏少', r'/^§([技赋])｜%s｜%s$/gm' % (F, REST), '<article class="dm-card"><h4><b>$2</b></h4><p>$3</p></article>ⓔ')
rule('红尘因果', r'/^§缘｜%s｜%s｜%s｜%s｜%s$/gm' % (F, F, F, F, REST),
     '<div class="dm-tr"><b>$1</b><span data-h="人际关系">$2</span><span data-h="情感状态">$3</span>'
     '<span data-h="因果与债">$4</span><span data-h="未决事项">$5</span></div>ⓔ')
rule('红尘因果·栏少', r'/^§缘｜%s｜%s$/gm' % (F, REST), '<div class="dm-tr"><b>$1</b><span>$2</span></div>ⓔ')

# ---- 群英照鉴 ----
rule('核心详牒', r'/^§详｜%s｜%s｜%s$/gm' % (F, F, REST),
     '</div></section><section class="dm-s dm-npc"><header class="dm-npc-h"><h3>$1</h3><span>$2</span><em>$3</em></header><div class="dm-sb">ⓔ')
rule('核心详牒·栏少', r'/^§详｜%s$/gm' % REST,
     '</div></section><section class="dm-s dm-npc"><header class="dm-npc-h"><h3>$1</h3></header><div class="dm-sb">ⓔ')
rule('详牒各项', r'/^§项｜%s｜%s$/gm' % (F, REST), '<div class="dm-row" data-k="$1"><b>$1</b><span>$2</span></div>ⓔ')
rule('现场简牒', r'/^§简｜%s｜%s｜(?:所在[:：])?%s｜(?:立场[:：])?%s｜(?:因果[:：])?%s$/gm' % (F, F, F, F, REST),
     '<article class="dm-brief"><header><b>$1</b><span>$2</span></header><p><b>所在</b>$3</p><p><b>立场</b>$4</p><p><b>因果</b>$5</p></article>ⓔ')
rule('现场简牒·栏少', r'/^§简｜%s｜%s$/gm' % (F, REST), '<article class="dm-brief"><header><b>$1</b></header><p>$2</p></article>ⓔ')

# ---- 万里照影 ----
rule('铭刻', r'/^§铭｜%s｜%s｜(?:最后相见[:：])?%s｜(?:最近确报[:：])?%s｜(?:离场推衍[:：])?%s｜(?:因果牵引[:：])?%s｜(?:下次回响[:：])?%s｜(?:来源[:：])?%s｜(?:可信度[:：])?%s$/gm' % (F, F, F, F, F, F, F, F, REST),
     '<article class="dm-remote"><header><b>$1</b><span>$2</span></header><div class="dm-row"><b>最后相见</b><span>$3</span></div>'
     '<div class="dm-row"><b>最近确报</b><span>$4</span></div><div class="dm-row"><b>离场推衍</b><span>$5</span></div>'
     '<div class="dm-row"><b>因果牵引</b><span>$6</span></div><div class="dm-row"><b>下次回响</b><span>$7</span></div>'
     '<footer>来源：$8｜可信度：$9</footer></article>ⓔ')
rule('铭刻·栏少', r'/^§铭｜%s｜%s$/gm' % (F, REST), '<article class="dm-remote"><header><b>$1</b></header><p>$2</p></article>ⓔ')

# ---- 天下风闻 ----
rule('风信', r'/^§讯｜%s｜%s$/gm' % (F, REST), '<article class="dm-news" data-k="$1"><h4>$1</h4><ul class="dm-ul"><li>$2</li></ul></article>ⓔ')
for n in range(6):
    rule('风信拆条%d' % (n + 1), r'/(<ul class="dm-ul"><li>[^\n]*)；/g', '$1</li><li>')
rule('四野', r'/^§向｜%s｜%s$/gm' % (F, REST), '<article class="dm-dir" data-k="$1"><b>$1</b><p>$2</p></article>ⓔ')
rule('四野拆项', r'/(<article class="dm-dir" data-k="[^"\n]{1,6}"><b>[^<\n]{1,6}<\/b><p>)([^｜<\n]*)｜/g', '$1<em>$2</em>｜')
rule('行策', r'/^§策｜%s｜(?:主要收益[:：]|收益[:：])?%s｜(?:明显风险[:：]|风险[:：])?%s｜(?:预计耗时[:：]|耗时[:：])?%s$/gm' % (F, F, F, REST),
     '<div class="dm-act" data-action="set-textinput" data-value="$1"><b>$1</b><span><em>收益</em>$2</span><span><em>风险</em>$3</span><span><em>耗时</em>$4</span></div>ⓔ')
rule('行策·栏少', r'/^§策｜%s$/gm' % REST, '<div class="dm-act" data-action="set-textinput" data-value="$1"><b>$1</b></div>ⓔ')

# ---- 天时经纬 ----
LV = {'急': 'urgent', '近': 'active', '远': 'distant', '未': 'card'}
for k, v in LV.items():
    rule('刻限·' + k, r'/^§限｜%s[^｜\n]{0,3}｜%s｜%s｜%s｜%s$/gm' % (k, F, F, F, REST),
         '<article class="dm-dl dm-dl-%s"><header><i>%s</i><b>$1</b><time>$2</time></header><p>$3</p><small>$4</small></article>ⓔ' % (v, k))
rule('刻限·其他', r'/^§限｜%s｜%s$/gm' % (F, REST), '<article class="dm-dl dm-dl-card"><header><b>$1</b></header><p>$2</p></article>ⓔ')
rule('夜潮', r'/^§候｜%s｜(?:民间可感[:：])?%s｜(?:官面说法[:：])?%s｜(?:证据所指[:：])?%s$/gm' % (F, F, F, REST),
     '<div class="dm-hou"><div class="dm-hou-n"><b>当前一候</b><span>$1</span></div><div><b>民间可感</b><span>$2</span></div>'
     '<div><b>官面说法</b><span>$3</span></div><div><b>证据所指</b><span>$4</span></div></div>ⓔ')
rule('诸州', r'/^§州｜%s｜%s｜%s｜%s｜%s｜%s$/gm' % (F, F, F, F, F, REST),
     '<div class="dm-tr"><b>$1</b><span data-h="州郡风雷">$2</span><span data-h="自然起势">$3</span><span data-h="当前幕次">$4</span>'
     '<span data-h="最近确报">$5</span><span data-h="与当前因果">$6</span></div>ⓔ')
rule('诸州·栏少', r'/^§州｜%s｜%s$/gm' % (F, REST), '<div class="dm-tr"><b>$1</b><span>$2</span></div>ⓔ')

# ---- 光阴藏卷 ----
rule('近事', r'/^§近｜%s｜%s｜%s$/gm' % (F, F, REST), '<div class="dm-mem"><time>$1｜$2</time><span>$3</span></div>ⓔ')
rule('经年', r'/^§经｜%s｜%s｜%s$/gm' % (F, F, REST), '<div class="dm-mem dm-mem-l"><time>$1｜$2</time><span>$3</span></div>ⓔ')
rule('未结', r'/^§因｜%s｜%s｜%s｜%s｜%s｜%s$/gm' % (F, F, F, F, F, REST),
     '<div class="dm-cause"><header><i>$1</i><b>$2</b><em>$5</em></header><p>$3</p><small><span>$4</span><span>来源：$6</span></small></div>ⓔ')
rule('铭刻命途', r'/^§刻｜%s｜%s$/gm' % (F, REST), '<div class="dm-mem dm-mem-c"><time>$1</time><span>$2</span></div>ⓔ')
rule('藏卷·栏少', r'/^§([近经因刻])｜%s$/gm' % REST, '<div class="dm-mem"><span>$2</span></div>ⓔ')

# ---- 功能轮：存档、差评、提示 ----
rule('存档头', r'/^§档｜%s$/m' % REST,
     CLOSE + '<details class="dm-p dm-p-save" open><summary><i class="dm-ico">档</i><b>存档</b><small>$1</small></summary>'
     '<div class="dm-pb"><section class="dm-s dm-s0"><div class="dm-sb dm-save">ⓔ')
rule('存档行', r'/^§存｜%s$/gm' % REST, '<div class="dm-sl">$1</div>ⓔ')
rule('差评', r'/^§评｜%s｜%s｜%s｜%s$/m' % (F, F, F, REST),
     CLOSE + '<details class="dm-p dm-p-ping" open><summary><i class="dm-ico">评</i><b>差评受理</b><small>修正规则已记下</small></summary>'
     '<div class="dm-pb"><section class="dm-s dm-s0"><div class="dm-sb"><div class="dm-row"><b>已识别问题</b><span>$1</span></div>'
     '<div class="dm-row"><b>禁止重复</b><span>$2</span></div><div class="dm-row"><b>后续采用</b><span>$3</span></div>'
     '<div class="dm-row"><b>适用范围</b><span>$4</span></div>ⓔ')
rule('差评·栏少', r'/^§评｜%s$/m' % REST,
     CLOSE + '<details class="dm-p dm-p-ping" open><summary><i class="dm-ico">评</i><b>差评受理</b><small>请写明不满意之处</small></summary>'
     '<div class="dm-pb"><section class="dm-s dm-s0"><div class="dm-sb"><p>$1</p>ⓔ')
rule('提示', r'/^§示｜%s$/gm' % REST, CLOSE + '<div class="dm-tip">$1</div>ⓔ')

# ---- 整页氛围：读行卷头的时辰和天气，写进整页变量（先插的排在后面，所以细的先跑，归零最后跑）----
WX = [('雨', 'rain'), ('雪', 'snow'), ('雾', 'fog')]
for k, v in WX:
    rule('天气·' + k, r'/(<article class="dm-page dm-scroll">)(?=<header class="dm-sh"><span class="dm-kicker">[^<\n]{0,60}<\/span><h2>[^<\n]{0,60}<\/h2><p class="dm-meta"><span class="dm-loc">[^<\n]{0,80}<\/span><span class="dm-wx">[^<\n]{0,30}%s)/' % k,
         '$1<style>.custom-styles{--dm-%s:1}</style>' % v)
HOURS = [('子', 0), ('丑', 2), ('寅', 4), ('卯', 6), ('辰', 8), ('巳', 10), ('午', 12), ('未', 14), ('申', 16), ('酉', 18), ('戌', 20), ('亥', 22)]
for k, h in HOURS:
    rule('时辰·' + k, r'/(<article class="dm-page dm-scroll">)(?=<header class="dm-sh"><span class="dm-kicker">[^<\n]{0,40}·%s)/' % k,
         '$1<style>.custom-styles{--dm-h:%d}</style>' % h)
rule('整页归零', r'/(<article class="dm-page dm-scroll">)/',
     '$1<style>.custom-styles{--dm-on:1;--dm-h:12;--dm-rain:0;--dm-snow:0;--dm-fog:0}</style>')

# ---- 收尾 ----
TABS = [('prose', '行卷'), ('ming', '玉牒'), ('jian', '群英'), ('wen', '风闻'), ('li', '经纬'), ('cang', '藏卷'), ('zhao', '照影')]
NAV = '<nav class="dm-tabs">' + ''.join('<label class="dm-tab t-%s"><input type="radio" name="dm-tab"><i></i><b>%s</b></label>' % t for t in TABS) + '</nav>'
rule('收卷·叙事轮', r'/\s*ⓩ\s*$/', CLOSE + NAV + '<i class="dm-run" hidden></i>')
rule('收卷·功能轮', r'/\s*ⓨ\s*$/', CLOSE + '<i class="dm-run dm-fn" hidden></i>')
rule('并块', r'/ⓔ\s*/g', '')
rule('残余记号', r'/[ⓟⓢ][^\n]{0,4}\n?/g', '')

json.dump(R, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(R))
