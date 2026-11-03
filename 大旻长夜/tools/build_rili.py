# -*- coding: utf-8 -*-
"""《大旻长夜》风月卡 → 日里原生导入 JSON（两种版本）＋报告。
用法：python3 -I -X utf8 大旻长夜/tools/build_rili.py <风月原卡.json> <输出目录> [--mode base|compact|both]

base     底本：照搬，AI 照旧写 HTML 骨架；只做日里非改不可的事（常驻并进主提示词、两条过不了安全检查的钥匙改黑名单、
         深度和优先级落到日里的范围、样式去掉风月平台壳、介绍页加“填进对话框”）。
compact  紧凑版：状态栏改一行一条的 § 记录，显示正则展开（状态栏/rules_frame_dm.json），样式 状态栏/frame_dm.css（大框，make_frame_dm.py 生成）；
         世界书触发照日里实测重写（见 TRIG 那一段）、长夜十候按日期拆十条、三类条目的重复套话并进主提示词。
脚本只做搬运和替换，替换的文字都写在本文件或 状态栏/ 下，手写，逐处可查。"""
import json, re, sys, os, argparse, copy, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SB = os.path.join(ROOT, '状态栏')

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('outdir')
ap.add_argument('--mode', default='both', choices=['base', 'compact', 'both'])
A = ap.parse_args()
card = json.load(open(A.src, encoding='utf-8'))
WB = card['world_book']
os.makedirs(A.outdir, exist_ok=True)

def must_replace(text, old, new, where):
    n = text.count(old)
    if n != 1:
        raise SystemExit('替换没对上（%s）：出现 %d 次：%s' % (where, n, old[:60]))
    return text.replace(old, new)

# ---------------------------------------------------------------- 样式：去风月平台壳
def component_css(css):
    """只留第二层作品组件层（§A 起），去掉 §P（风月建档页留白），@supports 拆壳（日里会整段丢掉 @supports）。"""
    i = css.index('/* ===== 第二层：作品组件层 ===== */')
    body = css[i:]
    p0 = body.index('/* ===== §P ')
    p1 = body.index('/* ===== §Q ')
    body = body[:p0] + body[p1:]
    m = re.search(r'@supports[^{]*\{', body)
    while m:
        j, depth = m.end(), 1
        while depth:
            if body[j] == '{': depth += 1
            elif body[j] == '}': depth -= 1
            j += 1
        body = body[:m.start()] + body[m.end():j - 1] + body[j:]
        m = re.search(r'@supports[^{]*\{', body)
    head = ('/* 超维武仙：大旻长夜 · 玄铁朱墙（日里版）\n'
            '   原卡 builtInCss 的作品组件层（§A—§O、§Q），风月平台壳层（§0—§13）和建档页留白（§P）不用；'
            '@supports 拆了壳，日里会把整段 @supports 丢掉。 */\n')
    return head + body

# ---------------------------------------------------------------- 介绍页：复制以外加“填进对话框”
def patch_intro(html):
    html = must_replace(html, '<button class="primary" type="button" onclick="copyFinalTicket()">复制开局文本</button>',
                        '<button type="button" onclick="copyFinalTicket()">复制开局文本</button>'
                        '<button class="primary" type="button" onclick="fillFinalTicket()">填进对话框</button>', '介绍页按钮')
    html = must_replace(html, '.ticket-preview-actions{display:grid;grid-template-columns:minmax(0,.72fr) minmax(0,1.28fr);',
                        '.ticket-preview-actions{display:grid;grid-template-columns:minmax(0,.7fr) minmax(0,1fr) minmax(0,1.2fr);', '介绍页按钮列')
    html = must_replace(html, 'function copyFinalTicket(){',
                        "function fillFinalTicket(){\n"
                        "  const preview=document.getElementById('ticketPreviewText');\n"
                        "  const t=(preview&&preview.textContent.trim())||buildFinalTicket();if(!t)return;\n"
                        "  const state=document.getElementById('ticketCopyState');\n"
                        "  try{window.parent.postMessage({type:'rili-set-input',value:t},'*');if(state)state.textContent='已填进下方对话框，核对后发送即可。';}\n"
                        "  catch(e){if(state)state.textContent='填入没有成功，请改用复制。';}\n"
                        "}\nfunction copyFinalTicket(){", '介绍页函数')
    html = must_replace(html, 'function copyStart(){if(startIndex<0)selectStart(0);navigator.clipboard&&navigator.clipboard.writeText(starts[startIndex]);}',
                        "function copyStart(){if(startIndex<0)selectStart(0);try{window.parent.postMessage({type:'rili-set-input',value:starts[startIndex]},'*');}catch(e){}"
                        "navigator.clipboard&&navigator.clipboard.writeText(starts[startIndex]).catch(()=>{});}", '介绍页快开')
    return html

# ---------------------------------------------------------------- 世界书：通用搬运
def strip_prefix(k):
    if k.startswith('_and_'): return k[5:], 'AND'
    if k.startswith('_or_'): return k[4:], 'OR'
    return k, 'OR'

TAIL = {9000: 8166, 9001: 8167}
for n in range(14): TAIL[9100 + n] = 8168 + n
for n in range(10): TAIL[9200 + n] = 8182 + n
def prio(sort):
    s = int(sort or 0)
    return TAIL.get(s, min(max(s, 0), 8192))

def base_item(e):
    k, typ = strip_prefix(e['key'] or '')
    words = ['/' + w + '/i' for w in k.split('@wb@') if w]
    rng = []
    kr = e.get('key_region') or 2
    if kr & 2: rng.append('user')
    if kr & 4: rng.append('assistant')     # 本卡只有常驻那一条带 4，它并进主提示词
    if not rng: rng = ['user']
    return {'enabled': e.get('enable', True) is not False, 'triggerWords': words, 'triggerWordsType': typ,
            'blackListWords': [], 'blackListWordsType': 'OR', 'folder': e.get('group') or '',
            'priority': prio(e.get('sort')), 'probability': int(e.get('probability') or 100) or 100,
            'scanDepth': min(max(int(e.get('depth') or 1), 1), 30), 'triggerRange': rng,
            'impactRange': ['system'], 'contentMethod': 'single', 'content': e.get('value') or ''}

CMD = ('查看命箓状态|查看大旻疆域与当前位置|查看当前势力、官署、江湖与万国暗流|查看当前人物与暗流|查看山河进程|存档|生成完整存档|保存世界线|'
       '读档|读取存档|执行：核心记忆归纳协议|核心记忆归纳|压缩记忆|防抢话状态|防抢话：开启|防抢话：关闭|查看超程铭刻|【查看超程铭刻】|'
       '开始|开始游戏|直接开局|进入游戏|开局|创建角色|角色创建|开局建档')
AUTOROT_BL = ['/^\\s*【差评[^】\\n]*】\\s*$/', '/^\\s*差评[:：]/', '/^\\s*(?:' + CMD + ')\\s*$/',
              '/^\\s*【?(?:解除)?超程铭刻[:：]/', '/^\\s*【(?:超维入局凭证|大旻长夜·立命入世凭证)】/']

def convert_common(report):
    lore, merged = [], []
    for i, e in enumerate(WB):
        if i == 1:                              # 常驻：并进主提示词
            merged.append(e['value'].strip()); continue
        it = base_item(e); it['_i'] = i
        if i in (1144, 1145):                   # 负前瞻套量词，日里会悄悄丢掉：改成“有字就醒、命令进黑名单”
            it['triggerWords'] = ['/\\S/']
            it['blackListWords'] = list(AUTOROT_BL)
            report.append('#%d %s：钥匙过不了平台的安全检查（量词套量词），改成任何一句话都醒、功能命令进黑名单。' % (i, e['value'].split('\n')[0][2:]))
        lore.append(it)
    return lore, merged

# ---------------------------------------------------------------- 紧凑版：提示词改写
def compact_prompt(sp):
    a = sp.index('## 六｜HTML输出总规'); b = sp.index('## 八｜功能命令分流')
    new67 = open(os.path.join(SB, 'prompt_compact_67.md'), encoding='utf-8').read().rstrip() + '\n\n'
    sp = sp[:a] + new67 + sp[b:]
    sp = must_replace(sp, '1. pre_prompt只负责始终执行的发动机、状态继承、时间推进、HTML输出结构与功能命令。人物、地点、势力、道途、命格、历史、剧情链和专业规则由world_book按需注入。',
                      '1. 主提示词只负责始终执行的发动机、状态继承、时间推进、记录行输出结构与功能命令。人物、地点、势力、道途、命格、历史、剧情链和专业规则由世界书按需注入。', '二.1')
    sp = must_replace(sp, '功能轮可以省略无关面板，但必须保持顶格HTML和标签完整。', '功能轮可以省略无关面板，照旧只写顶格的记录行。', '八.3')
    return sp

HEAD_C = ('【运行协议：深度现实主义与反神化｜防透剧与信息权限｜NPC独立模拟｜神州叙事】严格继承存档、入局凭证与已发生事实；按需调用世界书。'
          '严格将我的输入视为玩家扮演角色的行为、观察、对话、选择或自由指令，作出直接回应。玩家未明确输入的台词、心理、行动、承诺、消耗与突破不得代写。'
          '所有可见输出只写顶格的记录行和行卷正文，不写HTML。')
REAR_C = ('依次输出：十三行“§枢”（末一行写正文档位）；一行“§卷”加山河行卷（照当前正文档位：长约1500字、很长约1800字、小说约2000字，默认长）；命主玉牒（§身、§命、§技、§赋、§缘、§私、§物、§业、§事）；'
          '群英照鉴（§详、§项、§简）；有铭刻时万里照影（§铭）；天下风闻（§讯、§向、四行§策）；天时经纬（§限、§雷、§候、§州）；光阴藏卷（§近、§经、§因、§刻）。'
          '记录行一行一条、顶格、全角“｜”分栏，不写HTML、Markdown和代码围栏。'
          '命主玉牒必须逐字承接最近一次完整版本：§技与§赋的行数、卡名及静态栏不得减少、改写或缩短；仅当前反馈与有明确事件依据的变化可以更新。'
          '若检测到短版，先调用对应世界书恢复完整卡再输出。')

# 功能条目里写 HTML 的地方，换成记录行的说法（逐处手写，对不上就停）
FUNC = {
 0: [('首轮建立玄熙四十七年八月十八日的具体时辰、地点、天气、现场人物、可见矛盾和完整HTML“命主玉牒”与现场“群英照鉴”',
      '首轮建立玄熙四十七年八月十八日的具体时辰、地点、天气、现场人物、可见矛盾和完整的命主玉牒记录（§身至§事）与现场群英照鉴记录（§详、§项、§简）'),
     ('首轮同样遵守顶格HTML格式；若信息尚未确认，先用最少问题确认，不得伪造完整状态栏。',
      '首轮同样只写顶格的记录行；若信息尚未确认，先用最少问题确认，不得伪造完整状态栏。')],
 5: [('冻结世界线，输出HTML存档面板，并在`<pre class="cw-save-code">`内生成可复制的纯文本存档。',
      '冻结世界线，先写一行“§档｜存档标题”，再把可复制的纯文本存档逐行写成“§存｜……”，第一行写“§存｜【超维武仙存档】”，空行写“§存｜”。'),
     ('禁止“同上/略/保持不变/详见前文”。所有HTML行顶格。', '禁止“同上/略/保持不变/详见前文”。每行顶格。')],
 6: [('先用HTML成功提示确认世界线已接续，再用300—600字重建当前场景并给出四项行策加一项自定其途，不强行触发新危机。所有HTML行顶格。',
      '先写一行“§示｜世界线已接续：……”确认，再用一行“§卷”加300—600字重建当前场景，照常写四行“§策”，不强行触发新危机。每行顶格。')],
 8: [('输出顶格HTML，不重复抄写原文', '只写光阴藏卷的记录行（§近、§经、§因、§刻），不重复抄写原文')],
 9: [('只输出HTML“命主玉牒”并保持默认折叠', '只输出命主玉牒的记录行（§身至§事）'),
     ('所有HTML行顶格。 ', '每行顶格。 ')],
 10: [('使用HTML“天下风闻”面板输出', '用天下风闻的记录行（§讯、§向）输出'), ('所有HTML行顶格。', '每行顶格。')],
 11: [('使用HTML“天下风闻”面板，依据', '用天下风闻的记录行（一类一行“§讯”），依据'), ('所有HTML行顶格。', '每行顶格。')],
 12: [('输出HTML“群英照鉴”与“天下风闻”', '输出群英照鉴（§详、§项、§简）与天下风闻（§讯）的记录行'), ('所有HTML行顶格。', '每行顶格。')],
 13: [('只输出HTML“天时经纬”面板', '只输出天时经纬的记录行（§限、§雷、§候、§州）'), ('所有HTML行顶格。', '每行顶格。')],
 14: [('高于默认文风、节奏、HTML模板细节、', '高于默认文风、节奏、状态栏格式细节、'),
      ('6. 受理回复使用顶格HTML，仅输出一个默认展开的`cw-feedback`面板。具体差评确认时列出“已识别问题、禁止重复、后续采用、适用范围”；无具体内容时只列出填写提示。',
       '6. 受理回复只写一行：具体差评写“§评｜已识别问题｜禁止重复｜后续采用｜适用范围”；无具体内容时写“§评｜请写明不满意之处、期望修正方式与适用范围”。')],
 1274: [('于“群英照鉴”之后输出默认折叠的“万里照影”面板', '于群英照鉴之后输出万里照影记录（每名对象一行“§铭”）'),
        ('7. 功能回复使用顶格HTML。锚定或解除时输出一个`cw-remote`面板确认对象、依据与当前可知状态；查看时按“万里照影”格式列出全部铭刻对象。',
         '7. 功能回复只写记录行。锚定或解除时写一行“§铭”确认对象、依据与当前可知状态（解除时在铭刻状态一栏写“已解除”）；查看时按万里照影格式，一人一行“§铭”。')],
}

# ---------------------------------------------------------------- 紧凑版：触发优化
EXCL_REC = '\\n§'
def userish(orig):
    """玩家的话（或者没写记录行的回复）：整条消息里没有以 § 起头的行，原钥匙照旧认。"""
    return '/^(?![\\s\\S]*' + EXCL_REC + ')[\\s\\S]*?(?:' + orig + ')/i'

def lits(orig):
    """钥匙最外层的纯字面备选项。"""
    m = re.fullmatch(r'\(\?:(.*)\)', orig)
    body = m.group(1) if m else orig
    out, depth, cur = [], 0, ''
    for ch in body:
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if ch == '|' and depth == 0: out.append(cur); cur = ''
        else: cur += ch
    out.append(cur)
    return [x for x in out if x and not re.search(r'[\\.*+?{}\[\]()^$|]', x)]

CN = '零一二三四五六七八九'
def cnum(n):
    if n < 10: return CN[n]
    t, u = divmod(n, 10)
    return (CN[t] if t > 1 else '') + '十' + (CN[u] if u else '')
MONTHS = ['(?:正月|一月)', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '(?:冬月|十一月)', '(?:腊月|十二月)']
def date_range_rx(y0, m0, y1, m1):
    """玄熙 y0 年 m0 月 至 y1 年 m1 月（含两头的月份），拼成 §卷 头一栏的正则片段。"""
    alts = []
    for y in range(y0, y1 + 1):
        a = m0 if y == y0 else 1
        b = m1 if y == y1 else 12
        if a == 1 and b == 12: alts.append('%s年' % cnum(y))
        else: alts.append('%s年(?:%s)' % (cnum(y), '|'.join(MONTHS[a - 1:b])))
    return '(?:' + '|'.join(alts) + ')'

HOU = [(47, 8, 48, 4), (48, 4, 50, 9), (50, 9, 52, 3), (52, 3, 54, 9), (54, 9, 56, 10), (56, 10, 59, 10),
       (59, 10, 62, 11), (62, 11, 65, 5), (65, 5, 67, 11), (67, 11, 99, 12)]

def optimize(lore, report):
    by_group = collections.defaultdict(list)
    for it in lore: by_group[it['folder']].append(it)
    stat = collections.Counter()
    def add_anchor(it, anchors, depth=2):
        orig = it['triggerWords'][0][1:-2]           # 去掉 /…/i
        it['triggerWords'] = [userish(orig)] + anchors
        it['triggerRange'] = ['user', 'assistant']
        it['scanDepth'] = max(it['scanDepth'], depth)
    # 人物灵魂档案：玩家提到、或者上一条回复的正文与群英照鉴（§详、§简）里写到，就醒
    for it in by_group['超维·40人物灵魂档案']:
        L = lits(it['triggerWords'][0][1:-2])
        if not L: continue
        add_anchor(it, ['/^(?:§[详简]｜|(?!§))[^\\n]*?(?:' + '|'.join(L) + ')/m'], 2)
        stat['人物·正文与照鉴'] += 1
    # 疆域、次级区域、场景、地图地标：行卷头那一栏地点里有它，或者当境风雷的所在区域是它
    for g in ['超维·41大旻疆域定位', '超维·42新增区域次级定位', '超维·36神州场景地点补完', '超维·03蒸汽神州地图']:
        for it in by_group[g]:
            L = lits(it['triggerWords'][0][1:-2])
            if not L or it['_i'] == 1061: continue
            N = '|'.join(L)
            add_anchor(it, ['/^§卷｜[^｜\\n]*｜[^｜\\n]*｜[^｜\\n]*?(?:' + N + ')/m', '/^§雷｜所在区域｜[^\\n]*?(?:' + N + ')/m'], 2)
            stat['地点·行卷头'] += 1
    # 势力：在场人物（§详、§简）的身份栏写着它
    for g in ['超维·04势力与官署', '超维·26万国组织与学派']:
        for it in by_group[g]:
            L = [x for x in lits(it['triggerWords'][0][1:-2]) if len(x) >= 3]
            if not L: continue
            add_anchor(it, ['/^§[详简]｜[^｜\\n]*｜[^\\n]*?(?:' + '|'.join(L) + ')/m'], 2)
            stat['势力·在场人物'] += 1
    # 命主自己的武功术法、命格：玉牒里“§技”“§赋”那一行的名字栏
    for g, rec in [('超维·39武功术法库', '技'), ('超维·09命格库', '赋')]:
        for it in by_group[g]:
            L = lits(it['triggerWords'][0][1:-2])
            L = [re.sub(r'命格$', '', x) for x in L]
            if not L: continue
            add_anchor(it, ['/^§%s｜[^｜\\n]*?(?:%s)/m' % (rec, '|'.join(sorted(set(L), key=len, reverse=True)))], 2)
            stat['命主·%s' % rec] += 1
    # 道途总纲、道途执念：玉牒“当前境界”那一行
    for g in ['超维·37九重天阙道途总纲', '超维·08道途执念']:
        for it in by_group[g]:
            if it['_i'] in (598, 599): continue
            k = it['triggerWords'][0][1:-2]
            if g.endswith('道途执念'):
                L = lits(k)
            else:
                m = re.search(r'\(\?:\(\?:[^)]*\)\.\{0,5\}\(\?:([^)]*)\)', k) or re.match(r'\(\?:([^|]+\|[^|]+)\|', k)
                if not m: continue
                L = [re.sub(r'道途$', '', x) for x in m.group(1).split('|') if not re.search(r'[\\.*+?{}\[\]()/]', x)][:3]
            if not L: continue
            add_anchor(it, ['/^§命｜(?:当前境界|晋升条件)｜[^；\\n]*?(?:' + '|'.join(L) + ')/m'], 2)   # 只认头一句（晋升条件后头的“需……”会提到别的道途）
            stat['道途·当前境界'] += 1
    # 九重天阙逐序列：当前境界或晋升条件那一行同时写着道途和这一序列的称谓
    for it in by_group['超维·38九重天阙逐序列']:
        k = it['triggerWords'][0][1:-2]
        m = re.match(r'\(\?:\(([^)]*)\)\.\{0,8\}\(([^)]*)\)\|([^.]+)\.\{0,5\}', k)
        if not m: continue
        path, title = m.group(1), m.group(3)
        add_anchor(it, ['/^§命｜(?:当前境界|晋升条件)｜[^；\\n]*?(?:%s)[^；\\n]*?%s/m' % (path, title)], 2)
        stat['序列·境界与晋升'] += 1
    # 时代节点：行卷头的年份到了那一年
    for it in by_group['超维·45玄熙四十七年至六十七年时代节点']:
        m = re.match(r'\(\?:(玄熙[^|]{2,6}年)\|', it['triggerWords'][0][1:-2])
        if not m: continue
        add_anchor(it, ['/^§卷｜%s/m' % m.group(1)], 2)
        stat['时代节点·年份'] += 1
    # 道途总纲和逐序列：凭证里“联动：武夫、仕途……”和执行要求里“边界；造化”这类字会把别的道途叫醒，凭证那一条不算
    TICKET = '/【(?:大旻长夜·立命入世凭证|超维入局凭证)】/'
    for g in ['超维·37九重天阙道途总纲', '超维·38九重天阙逐序列']:
        for it in by_group[g]:
            if it['_i'] in (598, 599): continue
            it['blackListWords'] = it['blackListWords'] + [TICKET]
            stat['凭证不叫醒别的道途'] += 1
    report.append('触发重写：' + '、'.join('%s %d 条' % kv for kv in stat.items()))
    return stat

def split_longnight(lore, report):
    """长夜十候一条两千四百字，按日期拆成十条：行卷头的年月落在哪一候，醒哪一候。原条留着给玩家问起时用。"""
    it = next(x for x in lore if x['_i'] == 1127)
    text = it['content']
    head, *parts = re.split(r'\n(?=## [一二三四五六七八九十]候·)', text)
    if len(parts) != 10: raise SystemExit('长夜十候没拆成十段')
    new = []
    for n, (p, (y0, m0, y1, m1)) in enumerate(zip(parts, HOU)):
        t = p.split('\n')[0][3:]
        c = '# 长夜十候｜当前一候（按日期）\n' + head.split('\n', 1)[1].strip() + '\n\n' + p.strip()
        new.append({**copy.deepcopy(it), '_i': 1127 * 100 + n, 'content': c,
                    'triggerWords': ['/^§卷｜玄熙' + date_range_rx(y0, m0, y1, m1) + '/m'],
                    'triggerRange': ['assistant'], 'scanDepth': 2, 'priority': it['priority']})
    new[0]['triggerWords'].append('/【(?:大旻长夜·立命入世凭证|超维入局凭证)】/')   # 首轮：凭证默认从八月十八开局，落在一候
    new[0]['triggerRange'] = ['user', 'assistant']
    idx = lore.index(it)
    lore[idx + 1:idx + 1] = new
    report.append('长夜十候按日期拆成十条（只认上一条回复的行卷头年月），原条照旧给玩家问起时用。')

BOILER = [
 ('超维·40人物灵魂档案', '【固定人物硬锚】本条命中后，姓名、身份、性别、年龄、外貌、服饰、性格、所属与道途必须逐项服从本档案，严禁与其他角色互换、拼接或临场改写。\n'),
 ('超维·40人物灵魂档案', '- **能力边界**：只能在既定道途、序列、经验、身体状态、组织权限、装备和现实资源范围内行动；不得因剧情需要突然全知全能。\n'),
 ('超维·40人物灵魂档案', '- **一致性要求**：出场至少体现生平伤口、当前目标、底线、关系变化或说话习惯中的两项。秘密必须通过互动、调查、证据或关系推进揭露，不能无故直接告知玩家。人物会因事件永久改变立场、职位、伤势与关系。'),
 ('超维·39武功术法库', '\n初始抽取裁定：抽中本术法可获得完整传承载体、可信口诀与可修炼的入门部分；完整威能必须逐层修炼。叙事中必须按当前序列、六维、先天、资源、训练时间与掌握程度逐层结算；已经完成的训练、领悟与阶段解锁必须进入状态和存档，不得无故遗忘或回退。'),
 ('超维·09命格库', '\n裁定规则：命格是角色开局最核心的正向改变之一，符合情境时必须给予清晰、可感知、可持续的奖励反馈，不得以“平衡”为名擅自削弱。造化与无上造化不附带强制负面代价，不得用等价灾祸、寿命折损、人格污染、必然仇敌或强制反噬抵消其价值。命格不会替玩家自动完成必须由行动完成的现实目标，但应显著提升机会、成长效率、容错、上限或成果质量。'),
]
RULES9 = """## 九｜世界书条目通则（原来每条都抄一遍，并到这里）
1. 人物灵魂档案：【固定人物硬锚】本条命中后，姓名、身份、性别、年龄、外貌、服饰、性格、所属与道途必须逐项服从本档案，严禁与其他角色互换、拼接或临场改写。档案里没写能力边界的，照这一句：只能在既定道途、序列、经验、身体状态、组织权限、装备和现实资源范围内行动；不得因剧情需要突然全知全能。没写一致性要求的，照这一句：出场至少体现生平伤口、当前目标、底线、关系变化或说话习惯中的两项。秘密必须通过互动、调查、证据或关系推进揭露，不能无故直接告知玩家。人物会因事件永久改变立场、职位、伤势与关系。
2. 武功术法：抽中某门术法可获得完整传承载体、可信口诀与可修炼的入门部分；完整威能必须逐层修炼。叙事中必须按当前序列、六维、先天、资源、训练时间与掌握程度逐层结算；已经完成的训练、领悟与阶段解锁必须进入状态和存档，不得无故遗忘或回退。
3. 命格：命格是角色开局最核心的正向改变之一，符合情境时必须给予清晰、可感知、可持续的奖励反馈，不得以“平衡”为名擅自削弱。造化与无上造化不附带强制负面代价，不得用等价灾祸、寿命折损、人格污染、必然仇敌或强制反噬抵消其价值。命格不会替玩家自动完成必须由行动完成的现实目标，但应显著提升机会、成长效率、容错、上限或成果质量。
"""
def dedupe(lore, report):
    n = collections.Counter(); saved = 0
    for it in lore:
        for g, s in BOILER:
            if it['folder'] == g and s in it['content']:
                it['content'] = it['content'].replace(s, '', 1); n[g] += 1; saved += len(s)
    for it in lore:
        it['content'] = re.sub(r'\n### 语言与出场\n(- \*\*说话方式\*\*：[^\n]*)\n?$', r'\n### 语言与出场\n\1', it['content'])
    report.append('重复套话并进主提示词第九节：' + '、'.join('%s %d 条' % kv for kv in n.items()) + '，世界书少 %d 字。' % saved)

def func_entries(lore, report):
    for it in lore:
        i = it['_i']
        if i in FUNC:
            for old, new in FUNC[i]:
                it['content'] = must_replace(it['content'], old, new, '功能条目 #%d' % i)
        if i in (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 1274):
            it['impactRange'] = ['rearPrompt']
    left = [it['_i'] for it in lore if 'HTML' in it['content'] or 'cw-' in it['content']]
    report.append('功能条目里写 HTML 的地方换成记录行：%d 条；功能命令的影响范围改到后置词：11 条。还提到 HTML 的条目：%s' % (len(FUNC), left or '无'))

# ---------------------------------------------------------------- 补充条目与补丁（大旻长夜/补充/*.md）
sys.path.insert(0, HERE)
from overlay import parse as parse_overlay
def load_overlays():
    items = []
    d = os.path.join(ROOT, '补充')
    for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not fn.endswith('.md') or '派活说明' in fn or '备注' in fn: continue
        for kind, cfg, body in parse_overlay(open(os.path.join(d, fn), encoding='utf-8').read()):
            items.append((fn, kind, cfg, body))
    return items
# 原卡世界书里几处代词、字面错（11-03 洗稿各份对着性别栏查出来的），紧凑版改，底本照搬
FIXES = [(981, '十八岁论剑夺魁后，他主动担任巡盟使。', '十八岁论剑夺魁后，她主动担任巡盟使。'),   # 宋照霜，女
         (1051, '她只答：', '他只答：'),                                                       # 李归鸿，男
         (849, '他的语气会格外客气', '她的语气会格外客气'),                                     # 拓跋长缨，女
         (889, '复姓姒，', '姓姒，')]                                                            # 姒是单姓
def apply_fixes(lore, report):
    by_i = {it['_i']: it for it in lore}
    for i, a, b in FIXES:
        by_i[i]['content'] = must_replace(by_i[i]['content'], a, b, '#%d 字面' % i)
    report.append('原卡世界书改字面 %d 处（代词对上性别栏、复姓姒）' % len(FIXES))
def apply_patches(lore, items, report):
    by_i = {it['_i']: it for it in lore}
    n = 0
    for fn, kind, cfg, body in items:
        if kind != '补丁': continue
        it = by_i[cfg['i']]
        if cfg['op'] == 'append':
            it['content'] = it['content'].rstrip() + '\n\n' + body.strip()
        elif cfg['op'] == 'houlines':
            head, *parts = re.split(r'\n(?=## [一二三四五六七八九十]候·)', it['content'])
            if len(parts) != len(cfg['lines']): raise SystemExit('海外回声的行数对不上十候')
            parts = [p.rstrip() + '\n- **海外回声**：' + line for p, line in zip(parts, cfg['lines'])]
            it['content'] = '\n'.join([head] + parts)
        n += 1
    report.append('原卡条目添补丁 %d 处（万国吞旻总纲、终史测算、外敌压力、入局时间锚、观测团、圣金联、欢愉秘教、长夜十候添海外回声）' % n)
def add_entries(lore, items, report):
    cnt = collections.Counter(); chars = 0
    for fn, kind, cfg, body in items:
        if kind != '条目': continue
        anchors = cfg.get('anchors', [])
        if anchors:
            words = [userish(cfg['user'])] + ['/' + a + '/m' for a in anchors]
            rng = ['user', 'assistant']
        else:
            words = ['/' + cfg['user'] + '/i']
            rng = cfg.get('range', ['user'])
        lore.append({'enabled': True, 'triggerWords': words, 'triggerWordsType': 'OR',
                     'blackListWords': ['/' + b + '/' for b in cfg.get('black', [])], 'blackListWordsType': 'OR',
                     'folder': cfg['folder'], 'priority': int(cfg['priority']), 'probability': 100,
                     'scanDepth': int(cfg.get('depth', 2)), 'triggerRange': rng, 'impactRange': ['system'],
                     'contentMethod': 'single', 'content': body, '_i': 900000 + len(lore)})
        cnt[fn] += 1; chars += len(body)
    lore.sort(key=lambda x: x['priority'])
    report.append('新添条目 %d 条、%d 字：%s' % (sum(cnt.values()), chars, '、'.join('%s %d' % kv for kv in cnt.items())))

# ---------------------------------------------------------------- 洗稿合并（大旻长夜/洗稿/份N_输出.json）
WASH = os.path.join(ROOT, '洗稿')
def wash_parts():
    out = {}
    for n in range(1, 9):
        f = os.path.join(WASH, '份%d_输出.json' % n)
        if os.path.exists(f):
            out.update(json.load(open(f, encoding='utf-8')))
    return out
def wash_regions(lore, report):
    """州郡那组世界书（超维·41大旻疆域定位）跟介绍页州郡页同一份原文：介绍页洗过的字段（份3、份4），原文在这组条目里原样找得到的，照洗过的换，两边一样。"""
    pairs = []
    for n in (3, 4):
        fi, fo = os.path.join(WASH, '份%d_输入.json' % n), os.path.join(WASH, '份%d_输出.json' % n)
        if not (os.path.exists(fi) and os.path.exists(fo)): continue
        src = {x['k']: x['t'] for x in json.load(open(fi, encoding='utf-8'))}
        for k, t in json.load(open(fo, encoding='utf-8')).items():
            if len(src.get(k, '')) >= 16 and src[k] != t: pairs.append((src[k], t))
    pairs = sorted(set(pairs), key=lambda x: -len(x[0]))
    n = 0
    for it in lore:
        if not it.get('folder', '').startswith('超维·41'): continue
        c = it['content']
        for a, b in pairs:
            if a in c: c = c.replace(a, b); n += 1
        it['content'] = c
    report.append('州郡那组世界书照介绍页洗过的州郡页换了 %d 处，两边措辞一样' % n)
def sec_replace(v, name, new):
    return re.sub(r'(^### %s\n)([\s\S]*?)(?=\n### |\Z)' % re.escape(name), lambda m: m.group(1) + new.strip() + '\n', v, count=1, flags=re.M)
def wash_lore(lore, W, report):
    by_i = {it['_i']: it for it in lore}; n = 0
    for k, t in W.items():
        m = re.match(r'wb:(\d+):(性格|灵魂内核)$', k)
        if not m or int(m.group(1)) not in by_i: continue
        it = by_i[int(m.group(1))]
        it['content'] = sec_replace(it['content'], m.group(2), t); n += 1
    report.append('人物灵魂档案洗了性格、灵魂内核 %d 栏' % n)
def wash_intro(html, W, report):
    js_m = re.search(r'(<script[^>]*>)([\s\S]*?)(</script>)', html)
    js = js_m.group(2)
    # 人物两栏：世界书和介绍页同一份
    soul = {}
    for i, e in enumerate(WB):
        if e['group'] != '超维·40人物灵魂档案': continue
        nm = re.search(r'## 人物灵魂档案：(.+)', e['value']).group(1).strip()
        for f, key in (('性格', 'personality'), ('灵魂内核', 'soul')):
            mm = re.search(r'^### %s\n([\s\S]*?)(?=\n### |\Z)' % f, e['value'], re.M)
            if 'wb:%d:%s' % (i, f) in W and mm: soul[(nm, key)] = (mm.group(1).strip(), W['wb:%d:%s' % (i, f)])
    paths = collections.defaultdict(dict)
    for k, t in W.items():
        if k.startswith('['):
            p = json.loads(k)
            paths[p[0]][tuple(p[1:])] = t
    nd = 0
    for name in set(paths) | {'forceData'}:
        if name == 'static': continue
        i = js.find('const %s=' % name); j = i + len('const %s=' % name)
        v, end = json.JSONDecoder().raw_decode(js[j:])
        for path, t in paths.get(name, {}).items():
            o = v
            for p in path[:-1]: o = o[p]
            o[path[-1]] = t; nd += 1
        if name == 'forceData':
            for fk, fv in v.items():
                for pp in fv.get('people', []):
                    for key in ('personality', 'soul'):
                        old_new = soul.get((pp['name'], key))
                        if old_new and pp.get(key, '').strip() == old_new[0]:
                            pp[key] = old_new[1]; nd += 1
        js = js[:j] + json.dumps(v, ensure_ascii=False, separators=(',', ':')) + js[j + end:]
    html = html[:js_m.start(2)] + js + html[js_m.end(2):]
    ns = 0
    for path, t in paths.get('static', {}).items():
        src = STATIC_SRC.get(path[0])
        if src is None: continue
        old = '>' + H.escape(src, quote=False) + '<'
        if html.count(old) >= 1:
            html = html.replace(old, '>' + H.escape(t, quote=False) + '<'); ns += 1
    report.append('介绍页洗稿：数据 %d 处、页面文字 %d 处' % (nd, ns))
    return html
import html as H
def static_src():
    body = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', card['intro'])
    out = []
    for m in re.finditer(r'>([^<>]+)<', body):
        t = H.unescape(m.group(1)).strip()
        if len(re.findall(r'[一-鿿]', t)) >= 6 and t not in out: out.append(t)
    return {n: t for n, t in enumerate(out)}
STATIC_SRC = static_src()

# 卷一添两张卡：长夜无国界、域外黑手
CARDS_ADD = ('<article><b>长夜无国界</b><p>雾都的雾吃人名，极北的夜一年长过一年，黑海的船出了海峡，又从背后回到自家港口。洋人有洋人的长夜。他们到神州来，一半为了抢，一半为了逃。</p></article>'
             '<article><b>灾里的买卖</b><p>有人给灵灾定价，把一座城的劫难做成债券卖到海外；有人在灾区发忘忧药、办夜宴，把一城人的怕收进自己身上。每条道途都有正途，也都有吃人的走法。</p></article>')
def add_intro_cards(html):
    m = re.search(r'<article><b>长夜压强</b><p>[^<]*</p></article>', html)
    if not m: raise SystemExit('卷一没找到长夜压强那张卡')
    return html[:m.end()] + CARDS_ADD + html[m.end():]

DESC_C = open(os.path.join(ROOT, '样稿', '简介_改后.txt'), encoding='utf-8').read().strip() if os.path.exists(os.path.join(ROOT, '样稿', '简介_改后.txt')) else None

# 主提示词：世界硬锚第 7 条添长夜无国界和两面；天下风闻添海外消息的写法
HARD7_OLD = '7. 万国组织彼此竞争，但组织战略终点始终是吞食大旻的财政、军事、技术、司法、数据、信仰与历史解释权。个体外国人可成为真正盟友，组织不会因个体善意自动改弦更张。'
HARD7_ADD = ('长夜不分国界：泰西、新洲、沙洲、极北与教廷本部各有各的灵灾，各国官署都在遮掩；万国吞旻既是掠夺，也是拿神州的名册、道路与誓约给本土续命，本土越告急，在神州下手越急。'
             '二十一条道途都有正途与恶途，序列只认成就与承认、不认善恶；资本、欢愉等道途里走恶途的高阶者，会给灵灾定价、借灾转嫁、借灾敛权。每条道途都有正人与恶人，不得写成全是好人或全是坏人。')
NEWS_OLD = '每轮优先填充与当前地区、年份、势力和玩家因果最相关的内容。'
NEWS_ADD = ('每轮优先填充与当前地区、年份、势力和玩家因果最相关的内容。万国来函和四海新报里，隔一两轮带一条海外灵灾的公开说法或确报（外国报刊、电报、侨民、船员、领事告示、保险行情），写明来源和时差，'
            '官方说法和传言分开；海外的真相同样受信息权限约束。')

# ---------------------------------------------------------------- 预设按钮、建议
OPTS = [('存档', '存档'), ('读档', '读档'), ('查看命箓', '查看命箓状态'), ('查看疆域与位置', '查看大旻疆域与当前位置'),
        ('查看势力暗流', '查看当前势力、官署、江湖与万国暗流'), ('查看人物暗流', '查看当前人物与暗流'), ('查看山河进程', '查看山河进程'),
        ('核心记忆归纳', '执行：核心记忆归纳协议'), ('防抢话状态', '防抢话状态'), ('差评', '【差评：】'),
        ('超程铭刻', '【超程铭刻：】'), ('解除铭刻', '【解除超程铭刻：】'), ('查看铭刻', '【查看超程铭刻】')]
# 紧凑版的快捷键只留玩家真用得上的功能（11-03 用户说“查看xxx”这一类没必要，面板上都看得到）
OPTS_C = [('存档', '存档'), ('读档', '读档'), ('输出档位', '【输出档位：长】／【输出档位：很长】／【输出档位：小说】'),
          ('差评', '【差评：】'), ('防抢话', '【防抢话：开启】／【防抢话：关闭】'), ('记忆归纳', '执行：核心记忆归纳协议'),
          ('超程铭刻', '【超程铭刻：】'), ('解除铭刻', '【解除超程铭刻：】')]
# 介绍页快速开局那几段原来叫模型“按世界书以顶格HTML输出”，紧凑版换成记录行和正文档位
INTRO_START_OLD = '按世界书以顶格HTML输出玄枢推演、1000—1400字山河行卷、命主玉牒与群英照鉴、天下风闻、行止抉择和光阴藏卷。'
INTRO_START_NEW = '照记录行写法输出玄枢推演、山河行卷（照正文档位，默认长约1500字）、命主玉牒与群英照鉴、天下风闻、行止抉择和光阴藏卷。'
SUGG_C = """你是《大旻长夜》的行动演算引擎，只负责生成三个行动按钮，不写剧情。
读上一条回复里“§策”开头的四行，按出现的先后取前三行，把每行第一栏（具体行动）原样作为一个选项；第一栏超过四十字的，压成四十字以内，意思不改。
上一条回复没有“§策”行时（功能命令、存档、读档、差评受理），按当前处境自拟三条：一条稳妥、一条打探、一条冒进，每条一句、四十字以内，写成玩家可以直接发出去的行动。
只输出：{"suggestions": ["选项一", "选项二", "选项三"]}"""
SUGG_B = """你是《大旻长夜》的行动演算引擎，只负责生成三个行动按钮，不写剧情。
读上一条回复“行止抉择”里的行策一、行策二、行策三，各取“具体行动”那一段原样作为一个选项；超过四十字的压成四十字以内，意思不改。
上一条回复没有行止抉择时（功能命令、存档、读档、差评受理），按当前处境自拟三条：一条稳妥、一条打探、一条冒进，每条一句、四十字以内。
只输出：{"suggestions": ["选项一", "选项二", "选项三"]}"""

# ---------------------------------------------------------------- 组装
def build(mode):
    report = []
    lore, merged = convert_common(report)
    sp = card['prpt']
    head, rear = card['ptx'], card['post_text']
    css_comp = component_css(card['built_in_css'])
    if mode == 'compact':
        sp = compact_prompt(sp); head, rear = HEAD_C, REAR_C
        sp = must_replace(sp, HARD7_OLD, HARD7_OLD + HARD7_ADD, '硬锚第7条')
        sp = must_replace(sp, NEWS_OLD, NEWS_ADD, '天下风闻')
        OV = load_overlays()
        apply_patches(lore, OV, report)
        apply_fixes(lore, report)
        W = wash_parts()
        wash_lore(lore, W, report)
        wash_regions(lore, report)
        func_entries(lore, report)
        optimize(lore, report)
        split_longnight(lore, report)
        dedupe(lore, report)
        add_entries(lore, OV, report)
        sp = sp.rstrip() + '\n\n' + RULES9
    const = merged[0]
    if mode == 'compact':
        const = must_replace(const, '- HTML状态栏只写已知事实；', '- 状态栏只写已知事实；', '常驻·状态栏')
        const = must_replace(const, '所有HTML行必须顶格，禁止空格或Tab缩进。', '所有记录行必须顶格，禁止空格或Tab缩进。', '常驻·顶格')
        const = must_replace(const, '正文通常为1000—1400字；修炼、休息、疗伤、经营、等待、旅行准备与日常生活轮若无实质冲突，可用600—1000字稳定结算，不得为凑字制造冲突；静态功能命令除外。',
                             '正文照正文输出档位写（长约1500字、很长约1800字、小说约2000字，默认长，细则见输出总规“山河行卷”那一节）；修炼、休息、疗伤、经营、等待、旅行准备与日常生活轮若无实质冲突，可写到档位的三分之二稳定结算，不得为凑字制造冲突；静态功能命令除外。', '常驻·字数')
        style = open(os.path.join(ROOT, '样稿', '文风指令_大旻.md'), encoding='utf-8').read().strip()
        const = must_replace(const, '- 文风简洁、有力、通俗，保留国风高武、蒸汽王朝与长夜将临的厚重感。避免先否定再转折的定义句、递进套话和堆砌式排比。',
                             '- 文风简洁、有力、通俗，保留国风高武、蒸汽王朝与长夜将临的厚重感。避免先否定再转折的定义句、递进套话和堆砌式排比。具体写法：\n' + style, '常驻·文风')
    sp = sp.rstrip() + '\n\n---\n# 常驻规格（每轮生效；原为世界书的常驻条目）\n\n' + const + '\n'
    for it in lore:
        it.pop('_i', None)
    if mode == 'compact':
        css = open(os.path.join(SB, 'frame_dm.css'), encoding='utf-8').read() + '\n\n' + css_comp
        rules = json.load(open(os.path.join(SB, 'rules_frame_dm.json'), encoding='utf-8'))
        for r in rules: r.pop('name', None)
    else:
        css, rules = css_comp, []
    tags = [{'tag': {'name': t['name']}} for t in card.get('tags', [])][:15]
    intro = patch_intro(card['intro'])
    desc = card['abs_txt']
    if mode == 'compact':
        assert intro.count(INTRO_START_OLD) == 2, '介绍页快速开局那两段对不上'
        intro = intro.replace(INTRO_START_OLD, INTRO_START_NEW)
        intro = add_intro_cards(wash_intro(intro, W, report))
        if DESC_C: desc = DESC_C
    out = {'title': card['nm'], 'description': desc[:1024], 'language': 'zh',
           'containsNSFW': False, 'publicAccess': False, 'isAnonymous': False, 'enableSafeguard': False,
           'prompt': {'systemPrompt': sp, 'headPrompt': head, 'rearPrompt': rear,
                      'suggestionsPrompt': SUGG_C if mode == 'compact' else SUGG_B, 'lorebook': lore},
           'assistantRegexReplace': rules, 'injectStyles': css, 'introPage': intro,
           'enableMemorySchema': False,
           'options': {'items': [{'order': n, 'label': l, 'type': 'SET-INPUT', 'value': v} for n, (l, v) in enumerate(OPTS_C if mode == 'compact' else OPTS)]},
           'cardsTags': tags, 'cardsVoices': []}
    return out, report

def check(out):
    probs = []
    for n, it in enumerate(out['prompt']['lorebook']):
        if not (1 <= len(it['triggerWords']) <= 20): probs.append('#%d 触发词 %d 个' % (n, len(it['triggerWords'])))
        if not (0 <= it['priority'] <= 8192): probs.append('#%d 优先级 %d' % (n, it['priority']))
        if not (1 <= it['scanDepth'] <= 30): probs.append('#%d 深度' % n)
        for w in it['triggerWords'] + it['blackListWords']:
            if len(w) > 1024: probs.append('#%d 触发词过长 %d' % (n, len(w)))
    if len(out['description']) > 1024: probs.append('描述过长')
    for k in ('systemPrompt', 'headPrompt', 'rearPrompt'):
        if len(out['prompt'][k]) > 98304: probs.append(k + ' 过长')
    if len(out['injectStyles']) > 2097152: probs.append('样式过长')
    if len(out['assistantRegexReplace']) > 500: probs.append('正则过多')
    return probs

modes = ['base', 'compact'] if A.mode == 'both' else [A.mode]
NAME = {'base': '大旻长夜_日里版_底本.json', 'compact': '大旻长夜_日里版_紧凑.json'}
for mode in modes:
    out, report = build(mode)
    p = os.path.join(A.outdir, NAME[mode])
    json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    lb = out['prompt']['lorebook']
    print('== %s：%s' % (mode, p))
    print('   世界书 %d 条（启用 %d），正则触发词 %d 个，主提示词 %d 字，样式 %d 字，显示正则 %d 条，介绍页 %d 字，文件 %.1f MB'
          % (len(lb), sum(1 for x in lb if x['enabled']), sum(len(x['triggerWords']) for x in lb), len(out['prompt']['systemPrompt']),
             len(out['injectStyles']), len(out['assistantRegexReplace']), len(out['introPage']), os.path.getsize(p) / 1e6))
    for r in report: print('   ' + r)
    pr = check(out)
    print('   体检：' + ('问题 %d 条：%s' % (len(pr), '；'.join(pr[:8])) if pr else '没有问题'))
