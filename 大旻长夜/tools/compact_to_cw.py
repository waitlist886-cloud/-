# 把紧凑样本照原卡的 cw- HTML 骨架写回去，只为比一比同一条回复两种写法各多长（不进卡）。
# 用法：python3 -I -X utf8 compact_to_cw.py 样本.txt > 样本.cw.html
import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
SEC = {'身': ('cw-sec-profile', '身世名牒', 'dl'), '命': ('cw-sec-realm', '命关天衡', 'dl'), '技': ('cw-sec-skill', '武藏真传', 'cards'),
       '赋': ('cw-sec-ability', '天赋神通', 'cards'), '缘': ('cw-sec-relation', '红尘因果', 'table'), '私': ('cw-sec-romance', '风月私牒', 'dl'),
       '物': ('cw-sec-inventory', '随身百宝', 'dl'), '业': ('cw-sec-assets', '家业金契', 'dl'), '事': ('cw-sec-affairs', '今朝牵系', 'dl')}
out, cur, panel = ['<div class="cw-runtime">'], None, None
def close_sec():
    global cur
    if cur: out.append({'dl': '</dl>', 'cards': '</div>', 'table': '</tbody>\n</table>\n</div>'}[cur] + '\n</section>'); cur = None
def open_panel(p, cls, ico, title, sub, op=''):
    global panel
    close_sec()
    if panel: out.append('</div>\n</details>')
    panel = p
    out.append('<details class="cw-panel %s"%s>\n<summary><span class="cw-summary-icon">%s</span><span>%s</span><small>%s</small></summary>\n<div class="cw-panel-body">' % (cls, op, ico, title, sub))
prose = False
for l in L:
    m = re.match(r'^§(.)｜(.*)$', l)
    if not m:
        if l.strip() and prose: out.append('<p>%s</p>' % l.strip())
        continue
    k, v = m.group(1), m.group(2).split('｜')
    if k == '枢':
        if panel != '枢': open_panel('枢', 'cw-thought', '枢', '玄枢推演', '玄机裁分·结论可见'); out.append('<div class="cw-thought-grid">')
        out.append('<div class="cw-thought-item"><b>%s</b><span>%s</span></div>' % (v[0], '｜'.join(v[1:])))
    elif k == '卷':
        out.append('</div>\n</div>\n</details>'); panel = None
        out.append('<article class="cw-story">\n<header class="cw-story-head">\n<span class="cw-kicker">%s</span>\n<h2>%s</h2>\n<p>%s</p>\n</header>\n<div class="cw-prose">' % (v[0], v[1], '｜'.join(v[2:])))
        prose = True
    elif k == '验':
        out.append('</div>\n<section class="cw-check-card">\n<h3>天机验算</h3>\n<div class="cw-check-grid">\n' + '\n'.join('<div><b>%s</b><span>%s</span></div>' % (a, b) for a, b in zip(['项目', '有利条件', '不利条件', '结果'], v[:4])) + '\n</div>\n<p><b>代价与余波：</b>%s</p>\n</section>\n</article>' % v[4]); prose = 'done'
    elif k in SEC:
        if prose is True: out.append('</div>\n</article>'); prose = 'done'
        if panel != '玉牒': open_panel('玉牒', 'cw-player', '命', '命主玉牒', '身世·命关·神通·家业')
        cls, title, typ = SEC[k]
        if cur != typ + k:
            close_sec(); cur = typ
            out.append('<section class="cw-section %s">\n<h3>%s</h3>' % (cls, title) + {'dl': '\n<dl class="cw-dl">', 'cards': '\n<div class="cw-card-list">', 'table': '\n<div class="cw-table-wrap">\n<table class="cw-table cw-relation-table">\n<thead><tr><th>人物</th><th>人际关系</th><th>情感状态</th><th>因果与债</th><th>未决事项</th></tr></thead>\n<tbody>'}[typ])
            cur = typ; cur_k = k
        if typ == 'dl': out.append('<div class="cw-row"><dt>%s</dt><dd>%s</dd></div>' % (v[0], '｜'.join(v[1:])))
        elif typ == 'cards':
            lab = ['来源与类型', '掌握与实效', '消耗、限制与联动', '当前反馈'] if k == '技' else ['能力效果', '触发与使用方式', '边界与联动', '当前反馈']
            out.append('<article class="cw-%s-card"><h4>%s｜%s</h4>%s</article>' % ('skill' if k == '技' else 'ability', v[0], v[1], ''.join('<p><b>%s：</b>%s</p>' % (a, b) for a, b in zip(lab, v[2:]))))
        else: out.append('<tr>' + ''.join('<td>%s</td>' % x for x in v) + '</tr>')
    elif k in '详项简':
        if panel != '群英': open_panel('群英', 'cw-characters', '鉴', '群英照鉴', '核心详牒·现场简牒')
        if k == '详': out.append('<article class="cw-npc-card">\n<header class="cw-npc-head"><h3>%s</h3><span>%s</span></header>' % (v[0], '｜'.join(v[1:])))
        elif k == '项': out.append('<section class="cw-section"><h4>%s</h4><p>%s</p></section>' % (v[0], '｜'.join(v[1:])))
        else: out.append('</article>\n<div class="cw-npc-brief-grid">\n<article class="cw-npc-brief-card">\n<header><h4>%s</h4><span>%s</span></header>\n<p><b>所在</b>%s</p>\n<p><b>立场</b>%s</p>\n<p><b>因果</b>%s</p>\n</article>\n</div>' % tuple((v + [''] * 5)[:5]))
    elif k in '讯向策':
        if panel != '风闻': open_panel('风闻', 'cw-world', '闻', '天下风闻', '山河暗潮·四野勘舆·行止抉择', ' open')
        if k == '讯': out.append('<article class="cw-info-card"><h4>%s</h4><ul><li>%s</li></ul></article>' % (v[0], '</li><li>'.join('｜'.join(v[1:]).split('；'))))
        elif k == '向': out.append('<article class="cw-direction"><b>%s</b><p>%s</p></article>' % (v[0], '｜'.join(v[1:])))
        else: out.append('<li><b>行策：</b>%s</li>' % '｜'.join(v))
    elif k in '限雷候州':
        if panel != '经纬': open_panel('经纬', 'cw-chronicle', '历', '天时经纬', '刻限·风雷·夜潮·诸州', ' open')
        if k == '限': out.append('<article class="cw-deadline-card cw-deadline-active">\n<header><b>%s</b><time>%s</time></header>\n<p>%s</p>\n<small>%s</small>\n</article>' % tuple((v[1:] + [''] * 4)[:4]))
        elif k == '雷': out.append('<div class="cw-row"><dt>%s</dt><dd>%s</dd></div>' % (v[0], '｜'.join(v[1:])))
        elif k == '候': out.append('<div class="cw-longnight-grid">' + ''.join('<article><b>%s</b><span>%s</span></article>' % (a, b) for a, b in zip(['当前一候', '民间可感', '官面说法', '证据所指'], v)) + '</div>')
        else: out.append('<tr>' + ''.join('<td>%s</td>' % x for x in v) + '</tr>')
    elif k in '近经因刻':
        if panel != '藏卷': open_panel('藏卷', 'cw-memory', '藏', '光阴藏卷', '近事·经年·因果·命铭')
        out.append('<li><time>%s</time><span>%s</span></li>' % (v[0], '｜'.join(v[1:])))
close_sec()
if panel: out.append('</div>\n</details>')
out.append('</div>')
print('\n'.join(out))
