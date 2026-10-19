# -*- coding: utf-8 -*-
"""探针三：日里世界书的正则触发怎么算。
用法：python3 -I tools/make_probe3.py <repo根目录>
产物：out/探针卡_正则触发.json（私有、无工作记忆、三条预设按钮）
测的事：正则基线与标志、平台会丢掉哪些写法、扫描深度 0、/^/ 常亮、建档凭证黑名单（否定前瞻）、
前置词后置词算不算玩家这一句、系统范围扫什么、助手侧看到的是带标签的原文还是去标签的字、
AND 能不能跨两条消息、黑名单扫不扫上一轮回复、两条消息拼接的先后。
"""
import json, os, re, sys

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, 'out', '探针卡_正则触发.json')

HUD1 = '<div class="hud"><span class="hud-meta">月银纪1690年·秋 · 双桥城</span></div>'
HUD2 = ('<div class="hud"><b>日期</b><br>月银纪1690年·秋·坠叶月</div>'
        '<div class="hud"><b>地点</b><br>西陆·青麦国·双桥城·西门</div>'
        '<div class="hud"><b>回声</b><br>乙贰</div>')

SYSTEM = '''你是一台测试回声器，只用来检查世界书条目有没有注入。不讲故事，不扮演任何人。

每轮只输出下面四行，不加别的字：
第一行：玩家消息开头【】里的编号，原样照抄，例如「测2」；没有【】就写「测?」。
第二行：「标记：」后面列出你在本轮系统提示里看到的全部探针标记，也就是写在「探针标记」后面、两个 ◆ 夹着一个编号的那种记号，照它们在系统提示里出现的先后写，中间空一格；一个都没看到就写「标记：无」。只列本轮系统提示里真的出现的标记，以前回复里写过的不算，不要猜，不要补。
第三行、第四行：把下面两行原样抄一遍，一个字、一个符号都不改，不加空格，不放进代码块。

''' + HUD1 + '\n' + HUD2 + '\n'

HEAD = '（测试暗号：己陆）'
REAR = '（测试暗号：庚柒）只输出四行：编号、标记、两行底座。'

ROUNDS = [
    ('测1 只看玩家这一句', '【测1】甲壹 ABC XYZ 命途已确认 神殿'),
    ('测2 加上上一轮回复', '【测2】丙叁 丁肆'),
    ('测3 凭证里写了纪元', '【测3】纪元：月银纪 命途已确认 神殿'),
]

U, A, S = ['user'], ['assistant'], ['system']
UA = ['user', 'assistant']
CRED_BL = r'/^(?![\s\S]*纪元：月银纪)[\s\S]*命途已确认/'
# (编号, 触发词, AND?, 黑名单, 范围, 深度, 说明)
SPEC = [
    ('R1', ['/甲壹/'], False, [], U, 1, '正则基线'),
    ('R2', ['/abc/i'], False, [], U, 1, '正则的 i 标志，玩家打的是大写'),
    ('R3', ['xyz'], False, [], U, 1, '纯词分不分大小写，玩家打的是大写'),
    ('R4', ['/甲(?=壹)/'], False, [], U, 1, '前瞻'),
    ('R5', ['/(?:甲壹+)+/'], False, [], U, 1, '量词套量词，按说会被平台丢掉'),
    ('R6', ['/甲.*?壹/'], False, [], U, 1, '惰性量词，按说会被平台丢掉'),
    ('R7', ['/(?<=甲)壹/'], False, [], U, 1, '后顾，按说会被平台丢掉'),
    ('R8', ['/' + '甲?' * 26 + '壹/'], False, [], U, 1, '26 个量词，按说会被平台丢掉'),
    ('R9', ['/甲壹/'], False, [], U, 0, '扫描深度 0'),
    ('R10', ['/^/'], False, [], U, 1, '常亮'),
    ('R11', ['神殿'], False, [], U, 1, '纯词对照'),
    ('R12', ['神殿'], False, [CRED_BL], U, 1, '建档凭证黑名单，否定前瞻'),
    ('P1', ['/己陆/'], False, [], U, 1, '前置词里的暗号算不算玩家这一句'),
    ('P2', ['/庚柒/'], False, [], U, 1, '后置词里的暗号算不算玩家这一句'),
    ('S1', ['乙贰'], False, [], S, 1, '系统范围扫不扫主提示词'),
    ('A1', ['乙贰'], False, [], A, 2, '扫上一轮回复'),
    ('A2', ['乙贰'], False, [], A, 1, '深度 1 看不看得见上一轮回复'),
    ('H1', ['地点</b><br>西陆'], False, [], A, 2, '纯词带标签，奥尔德兰现在的写法'),
    ('H2', ['hud-meta">月银纪'], False, [], A, 2, '纯词带属性，奥尔德兰现在的写法'),
    ('H3', [r'/地点<\/b><br>[^<]{0,30}双桥城/'], False, [], A, 2, '正则地点锚'),
    ('H4', [r'/地点\s*西陆/'], False, [], A, 2, '出现就说明扫的是去掉标签的字'),
    ('H5', [r'/日期<\/b><br>月银纪(?:1\d{3}|2\d{3})年/'], False, [], A, 2, '年份窗'),
    ('N1', ['/丙叁/', '/丁肆/'], True, [], UA, 2, '同时满足，两样都在玩家这一句'),
    ('N2', ['/丙叁/', '/乙贰/'], True, [], UA, 2, '同时满足，一样在玩家这一句，一样在上一轮回复'),
    ('N3', ['/丙叁/', '/戊伍/'], True, [], UA, 2, '同时满足的反例'),
    ('B1', ['/丙叁/'], False, ['戊伍'], UA, 2, '黑名单对照'),
    ('B2', ['/丙叁/'], False, ['乙贰'], UA, 2, '黑名单纯词，挡的字只在上一轮回复里'),
    ('B3', ['/丙叁/'], False, ['/乙贰/'], UA, 2, '黑名单正则，挡的字只在上一轮回复里'),
    ('B4', ['/丙叁/'], False, ['丁肆'], UA, 2, '黑名单，挡的字在玩家这一句'),
    ('O1', [r'/乙贰[\s\S]*丙叁/'], False, [], UA, 2, '拼接时上一轮回复在前'),
    ('O2', [r'/丙叁[\s\S]*乙贰/'], False, [], UA, 2, '拼接时玩家这一句在前'),
]

TOKENS = ['甲壹', '乙贰', '丙叁', '丁肆', '戊伍', '己陆', '庚柒', 'abc', 'xyz', '神殿', '命途已确认',
          '纪元：月银纪', '地点</b>', '日期</b>', 'hud-meta', '双桥城', '西陆']

def entry(i, tag, words, is_and, black, rng, depth, note):
    for t in TOKENS:
        assert t.lower() not in note.lower(), (tag, t)
    return {
        'enabled': True,
        'triggerWords': words, 'triggerWordsType': 'AND' if is_and else 'OR',
        'blackListWords': black, 'blackListWordsType': 'OR',
        'folder': '探针三', 'priority': 10 + i, 'probability': 100, 'scanDepth': depth,
        'triggerRange': rng, 'impactRange': ['system'],
        'contentMethod': 'single',
        'content': '探针标记 ◆%s◆ %s' % (tag, note),
    }

lore = [entry(i, *s) for i, s in enumerate(SPEC)]

def cells(xs):
    return ' '.join(xs)

INTRO_ROWS = [
    ('测1', '甲壹 ABC XYZ 命途已确认 神殿', 'R1 R2 R4 R10 R11',
     'A、H、N、B、O 开头的（这一轮还没有上一轮回复）', 'R3 R5 R6 R7 R8 R9 P1 P2 S1，R12 按说该被挡住'),
    ('测2', '丙叁 丁肆', 'R10 A1 N1 B1', 'R1 到 R8、R11、R12、A2、N3、B4',
     'R9 H1 H2 H3 H4 H5 N2 B2 B3 O1 O2 P1 P2 S1'),
    ('测3', '纪元：月银纪 命途已确认 神殿', 'R10 R11 A1', 'R1 到 R8、A2，以及 N、B、O 开头的',
     'R12 按说这一轮放出来；R9、P1、P2、S1 和 H 开头的跟测2 对一对'),
]

def js_str(s):
    return json.dumps(s, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e')

btns = '\n'.join(
    '<button type="button" onclick=\'fill(%s)\'>%s</button>' % (js_str(v).replace("'", '&#39;'), lab)
    for lab, v in ROUNDS)
rows = '\n'.join(
    '<div class="rd"><div class="rh">%s　发「%s」</div><p><b>一定该有</b>　%s</p><p><b>一定不该有</b>　%s</p><p><b>要看的</b>　%s</p></div>' % r
    for r in INTRO_ROWS)

INTRO = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;padding:20px 16px 32px;background:#14161a;color:#e8e4da;font:15px/1.75 "Noto Sans CJK SC","PingFang SC",system-ui,sans-serif}
h1{font-size:21px;margin:0 0 6px}h2{font-size:16px;margin:22px 0 6px;color:#d9c79a}
p,li{margin:6px 0}ol,ul{padding-left:22px;margin:6px 0}
.rd{border:1px solid #3a3e46;border-radius:8px;padding:8px 12px;margin:10px 0;background:#191c21}
.rh{font-weight:600;color:#e8d9b0;margin-bottom:2px}.rd p{margin:3px 0;font-size:14px}.rd b{color:#9fb6d2;font-weight:600}
code{background:#22262d;padding:1px 5px;border-radius:4px;word-break:break-all}
.btns{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
button{background:#2b3b52;color:#eef2f7;border:1px solid #4a6a92;border-radius:8px;padding:9px 14px;font:inherit;cursor:pointer}
button:active{background:#3a5274}.n{color:#9aa3ad;font-size:13px}
</style></head><body>
<h1>探针 · 正则触发</h1>
<p>这张卡只用来测日里的世界书怎么触发，不讲故事。一共三轮，十分钟以内能测完。</p>

<h2>怎么测</h2>
<ol>
<li>新建一张私有卡，把这份 JSON 导进去，保存。别导进奥尔德兰的草稿里。</li>
<li>开一局，模型用你平时跑卡的那个。从输入框的预设按钮里按顺序点「测1」「测2」「测3」，每点一个就发送一次。下面三个按钮也能填。</li>
<li>每轮回复的第二行是「标记」，三轮的标记行抄给我就行。能打开提示词调试的话，测2 那一轮截一张图，比模型自己报的准。</li>
<li>回复的第三、四行应该显示成「日期 月银纪1690年…」「地点 西陆…」「回声 乙贰」这几块。模型要是没照抄，或者改了样子，告诉我一声。</li>
</ol>
<div class="btns">
''' + btns + '''
</div>

<h2>导入以后先看一眼编辑器</h2>
<p>打开世界书，看 R5、R6、R7、R8 这四条的触发词还是不是原样，有没有被换成 <code>/(?!)/</code> 一类的东西；再看 R9 的扫描深度是不是还是 0。看到什么告诉我。</p>

<h2>每一轮该看什么</h2>
''' + rows + '''
<p class="n">「一定该有」的没出现，多半是模型没照格式报，换个模型再测一轮，或者看提示词调试。</p>

<h2>编号是什么意思</h2>
<ul>
<li><b>R</b>：只看玩家这一句。R1 正则基线；R2 正则的 i 标志；R3 纯词分不分大小写；R4 前瞻；R5 到 R8 是四种按说会被平台丢掉的写法（量词套量词、惰性量词、后顾、超过 25 个量词）；R9 扫描深度写 0；R10 常亮；R11、R12 是建档凭证黑名单，测1 里 R12 该被挡住，测3 里该放出来。</li>
<li><b>P</b>：前置词、后置词里的字算不算玩家这一句。</li>
<li><b>S</b>：「系统」范围扫的是不是主提示词。</li>
<li><b>A、H</b>：扫上一轮回复。H1、H2 是奥尔德兰现在用的带标签纯词，H3 是正则地点锚，H5 是年份窗；H4 出现，说明平台扫的是去掉标签以后的字。</li>
<li><b>N</b>：同时满足（AND）。N2 出现，说明 AND 能把上一轮回复和玩家这一句合起来算。</li>
<li><b>B</b>：黑名单。B2、B3 没出现，说明黑名单也扫上一轮回复。</li>
<li><b>O</b>：两条消息要是拼在一起扫，O1、O2 会出现一个，由此知道谁在前。两个都不出现，说明是一条一条分开扫的。</li>
</ul>
<p>测完把三行标记发回来，我照结果定奥尔德兰的触发词怎么写。这张卡测完就可以删。</p>
<script>
function fill(v){try{window.parent.postMessage({type:'rili-set-input',value:v},'*')}catch(e){}}
</script>
</body></html>'''

card = {
    'title': '探针·正则触发（测试用）',
    'description': '测试卡：验证日里世界书的正则触发、同时满足、黑名单和扫描范围。不讲故事，测完即删。',
    'language': 'zh',
    'containsNSFW': False, 'publicAccess': False, 'isAnonymous': False, 'enableSafeguard': False,
    'prompt': {'systemPrompt': SYSTEM, 'headPrompt': HEAD, 'rearPrompt': REAR,
               'suggestionsPrompt': '', 'lorebook': lore},
    'introPage': INTRO,
    'enableMemorySchema': False,
    'options': {'items': [{'order': i, 'label': lab, 'type': 'SET-INPUT', 'value': v}
                          for i, (lab, v) in enumerate(ROUNDS)]},
    'cardsTags': [{'tag': {'name': '测试'}}],
    'cardsVoices': [],
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(card, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('写出', OUT, '条目', len(lore))
