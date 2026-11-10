#!/usr/bin/env python3
# 11-10 探针卡：上新功能以前，拿一张不讲故事的小卡在日里正式对话里测四件事（对照稿第三、七节要先测的）。
#   一、加权条目是不是每一轮都重新抽（命运骰靠它）：两颗测试骰，各二十段、各 5%，触发 /^/。
#   二、「应用到全部」的正则改了 AI 的话以后，世界书扫的是改过的还是原文（状态栏瘦身要靠这个）：
#       模型每轮照抄一句「丙叁记号 丁肆记号」，一条正则把丙叁记号换掉，丙那一条认丙叁记号、丁那一条认丁肆记号，都只扫 AI，深度 2。
#       下一轮丙醒了，扫的是原文；不醒，扫的是改过的。丁是对照，该醒。
#   三、工作记忆怎么更新：schema 只有计数和上一句，模型每轮报计数；另一条只扫工作记忆，计数到 2 以上该醒。
#   四、后续建议：填了 suggestionsPrompt，看输入框上头出不出三个按钮。
# 用法：python -I -X utf8 make_probe_1110.py 输出.json
import json
import sys

SYS = '''你是测试器，不讲故事，不加解释。每一轮只输出下面五行，照实填写：
第1行：把本轮系统提示里所有带◆的标记照原样抄下来，用顿号隔开，一个也没有就写 无
第2行：把本轮系统提示里写着测试骰的数字抄下来，写成 甲=几 乙=几，看不到写 无
第3行：照抄这一句：丙叁记号 丁肆记号
第4行：工作记忆里计数现在是几，看不到写 看不到
第5行：照抄玩家这一轮说的话
只输出这五行。'''


def ent(name, trig, rng, depth, content=None, contents=None):
    e = {'enabled': True, 'triggerWords': trig, 'triggerWordsType': 'OR', 'blackListWords': [], 'blackListWordsType': 'OR',
         'folder': '探针', 'priority': 0, 'probability': 100, 'scanDepth': depth, 'triggerRange': rng, 'impactRange': ['system']}
    if contents:
        e['contentMethod'] = 'weighted'
        e['contents'] = [{'content': c, 'probability': p} for c, p in contents]
    else:
        e['contentMethod'] = 'single'
        e['content'] = content
    return e


lore = [
    ent('骰甲', ['/^/'], ['user'], 1, contents=[('测试骰甲=%d' % n, 5) for n in range(1, 21)]),
    ent('骰乙', ['/^/'], ['user'], 1, contents=[('测试骰乙=%d' % n, 5) for n in range(1, 21)]),
    ent('丙', ['丙叁记号'], ['assistant'], 2, '探针标记 ◆丙◆'),
    ent('丁', ['丁肆记号'], ['assistant'], 2, '探针标记 ◆丁◆'),
    ent('记', ['/"计数": ?[2-9]/', '/计数[^0-9\\n]{0,6}[2-9]/'], ['working-memory'], 1, '探针标记 ◆记◆'),
]
schema = {'type': 'object', 'properties': {
    '计数': {'type': 'integer', 'description': '从 0 起，每一轮加一'},
    '上一句': {'type': 'string', 'description': '玩家上一轮说了什么，照抄'}}, 'required': ['计数']}

INTRO = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:18px;font:15px/1.8 system-ui,sans-serif;background:#16181d;color:#e8e4da">
<h2 style="margin:0 0 10px">奥尔德兰探针 11-10</h2>
<p>这张卡不讲故事，只测平台。测完删掉就行。</p>
<ol>
<li>开一局，点输入框菜单里的「第一轮」发出去，再依次发「第二轮」「第三轮」。</li>
<li>每一轮回复是五行，三轮都截图或者复制下来。</li>
<li>另外看两样：输入框上头有没有出三个建议按钮；聊天页的「上下文」面板里计数是几。</li>
</ol>
<p>要看的：</p>
<ul>
<li>第2行三轮的数字是不是在变（命运骰能不能用）。</li>
<li>第1行第二、三轮有没有 ◆丙◆（有，就是世界书扫的是原文；没有，扫的是正则改过的字）。◆丁◆ 应当有，是对照。</li>
<li>第4行计数是不是一轮一轮往上走；第三轮第1行有没有 ◆记◆（工作记忆能不能叫醒条目）。</li>
</ul>
<button style="margin-top:12px;padding:10px 18px;font-size:15px;border-radius:8px;border:0;background:#c9a45c;color:#1a1408"
 onclick="window.parent.postMessage({type:'rili-set-input', value:'第一轮'},'*')">填入「第一轮」</button>
</body></html>'''

card = {
    'title': '奥尔德兰探针_11-10',
    'description': '测平台用的小卡，不讲故事：加权条目每轮重抽、正则和世界书扫描谁先、工作记忆、后续建议。测完删。',
    'language': 'zh', 'containsNSFW': False, 'publicAccess': False, 'isAnonymous': False, 'enableSafeguard': False,
    'prompt': {'systemPrompt': SYS, 'headPrompt': '', 'rearPrompt': '',
               'suggestionsPrompt': '你是行动选项生成器，不推进剧情。随便给三个短选项，每个不超过十个字。只输出 {"suggestions": ["选项一", "选项二", "选项三"]}',
               'lorebook': lore},
    'assistantRegexReplace': [{'enabled': True, 'applyMode': 'all', 'messageRole': 'assistant', 'regex': '/丙叁记号/g', 'replaceString': '丙已换'}],
    'injectStyles': '',
    'introPage': INTRO,
    'enableMemorySchema': True,
    'memorySchema': json.dumps(schema, ensure_ascii=False),
    'options': {'items': [{'order': i, 'label': t, 'type': 'SET-INPUT', 'value': t} for i, t in enumerate(['第一轮', '第二轮', '第三轮'])]},
    'cardsTags': [],
    'cardsVoices': [],
}
with open(sys.argv[1], 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False, indent=1)
print('ok', sys.argv[1])
