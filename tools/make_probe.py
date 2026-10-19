# -*- coding: utf-8 -*-
"""Build the era-gate probe card (Rili native JSON)."""
import json, re, sys

SEAL = '纪元印·月银'

system_prompt = '''你是一台测试回声器，只用来检查世界书条目有没有注入。不讲故事，不扮演任何人。

每轮只输出下面两行，不加别的字：
第一行：玩家消息开头【】里的编号，原样照抄，例如「测4」。
第二行：「标记：」后面列出你在本轮系统提示里看到的全部探针标记（形如 ◆A◆ 的记号），按字母顺序连写；一个都没看到就写「标记：无」。只列真的出现在系统提示里的标记，不要猜，不要补。

另有两条：
- 玩家消息里有「盖印」二字时，在第二行之后另起一行，只写：纪元印·月银
- 工作记忆里的「纪元」一格：玩家消息里有「盖印」就改成「纪元印·月银」，有「撤印」就改成「纪元印·迷宫」，其余时候不动。
'''

rear_prompt = '只输出两行：编号一行，标记一行；有「盖印」时多一行纪元印·月银。'

def entry(tag, words, typ, black, rng, depth, note):
    return {
        'enabled': True,
        'triggerWords': words, 'triggerWordsType': typ,
        'blackListWords': black, 'blackListWordsType': 'OR',
        'folder': '探针',
        'priority': 100, 'probability': 100, 'scanDepth': depth,
        'triggerRange': rng, 'impactRange': ['system'],
        'contentMethod': 'single',
        'content': f'探针标记 ◆{tag}◆（{note}）',
    }

lore = [
    entry('P', ['公会'], 'OR', [], ['user'], 1, '基线：玩家这一条提到了公会'),
    entry('A', [SEAL, '/萨尔维斯|浮空塔/i'], 'AND', [], ['user', 'assistant'], 2, '同时满足：纪元印加一个正则词'),
    entry('B', ['公会'], 'OR', [SEAL], ['user', 'assistant'], 2, '黑名单，触发范围用户加助手，深度2'),
    entry('E', ['公会'], 'OR', [SEAL], ['user'], 1, '黑名单，触发范围只有用户，深度1'),
    entry('W', ['公会'], 'OR', [SEAL], ['user', 'working-memory'], 1, '黑名单，触发范围用户加工作记忆，深度1'),
]

schema = {
    'type': 'object',
    'properties': {
        '纪元': {
            'type': 'string',
            'enum': ['纪元印·迷宫', SEAL],
            'description': '玩家消息里有「盖印」就改成纪元印·月银，有「撤印」就改成纪元印·迷宫，其余时候不动。',
        }
    },
    'required': ['纪元'],
    'additionalProperties': False,
}

tests = [
    ('测1 基线', '【测1】公会在哪？'),
    ('测2 同一条里有印', '【测2】纪元印·月银 公会在哪？'),
    ('测3 盖印', '【测3】盖印。'),
    ('测4 印在上一条回复里', '【测4】公会在哪？'),
    ('测5 同时满足', '【测5】纪元印·月银 我想去萨尔维斯的浮空塔。'),
    ('测6 只有正则词', '【测6】我想去萨尔维斯。'),
    ('测7 撤印', '【测7】撤印。'),
]

intro = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{margin:0;padding:20px 16px;background:#14161a;color:#e8e4da;font:15px/1.7 "Noto Sans CJK SC",system-ui,sans-serif}
h1{font-size:20px;margin:0 0 8px}p{margin:6px 0}table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}
td,th{border:1px solid #3a3e46;padding:6px 8px;text-align:left;vertical-align:top}th{background:#22262d}
code{background:#22262d;padding:1px 5px;border-radius:4px}.n{color:#9aa3ad;font-size:13px}</style></head><body>
<h1>探针 · 纪元门控</h1>
<p>这张卡只用来验世界书的两件事，不讲故事。从输入框的预设按钮里按顺序点「测1」到「测7」，每次发送，记下回复第二行的「标记」。</p>
<p class="n">建议用平时跑奥尔德兰的模型。测3 之后先看一眼工作记忆面板，「纪元」应当变成纪元印·月银。</p>
<table><tr><th>测</th><th>发的是</th><th>一定会有</th><th>要看的</th></tr>
<tr><td>1</td><td>公会在哪？</td><td>P</td><td>B、E、W 也应当在（这时哪儿都没有印）</td></tr>
<tr><td>2</td><td>纪元印·月银 公会在哪？</td><td>P</td><td>B、E、W 应当都不在（印就在这一条里）</td></tr>
<tr><td>3</td><td>盖印。</td><td></td><td>回复多一行「纪元印·月银」，工作记忆变成月银</td></tr>
<tr><td>4</td><td>公会在哪？</td><td>P</td><td>关键一条：B、E、W 各在不在</td></tr>
<tr><td>5</td><td>纪元印·月银 我想去萨尔维斯的浮空塔。</td><td></td><td>A 在不在</td></tr>
<tr><td>6</td><td>我想去萨尔维斯。</td><td></td><td>A 应当不在</td></tr>
<tr><td>7</td><td>撤印。</td><td></td><td>工作记忆变回迷宫</td></tr></table>
<p>把七轮的「标记」行抄给我就行，例如「测4：◆B◆◆P◆」。</p></body></html>'''

card = {
    'title': '探针·纪元门控（测试用）',
    'description': '测试卡：验证世界书「同时满足」里夹正则词，以及黑名单扫哪一段文字。不讲故事。',
    'language': 'zh',
    'containsNSFW': False, 'publicAccess': False, 'isAnonymous': False, 'enableSafeguard': False,
    'prompt': {
        'systemPrompt': system_prompt,
        'headPrompt': '',
        'rearPrompt': rear_prompt,
        'lorebook': lore,
    },
    'introPage': intro,
    'enableMemorySchema': True,
    'memorySchema': json.dumps(schema, ensure_ascii=False),
    'options': {'items': [{'order': i, 'label': lab, 'type': 'SET-INPUT', 'value': val} for i, (lab, val) in enumerate(tests)]},
    'cardsTags': [{'tag': {'name': '测试'}}],
    'cardsVoices': [],
}

out = sys.argv[1]
json.dump(card, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# checks
for e in lore:
    assert 1 <= len(e['triggerWords']) <= 20
    for w in e['triggerWords']:
        if w.startswith('/'):
            m = re.match(r'^/(.*)/([imsg]*)$', w)
            assert m, w
            re.compile(m.group(1))
            assert not re.search(r'\(\?<', m.group(1)) and not re.search(r'[+*?}]\?', m.group(1))
    assert 0 <= e['priority'] <= 8192 and 0 <= e['scanDepth'] <= 30
    assert e['triggerRange'] and e['impactRange']
assert all(len(o['label']) <= 128 and len(o['value']) <= 1024 for o in card['options']['items'])
assert len(card['description']) <= 1024
json.loads(card['memorySchema'])
print('ok', out, len(json.dumps(card, ensure_ascii=False)))
