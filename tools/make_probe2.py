# -*- coding: utf-8 -*-
"""Probe 2: scan order across messages (lookahead) + working-memory scanning."""
import json, re, sys

SEAL = '纪元印·月银'

system_prompt = '''你是一台测试回声器，只用来检查世界书条目有没有注入。不讲故事，不扮演任何人。

每轮按顺序输出下面几行，不加别的字：
第一行：玩家消息开头【】里的编号，原样照抄，例如「测4」。
第二行：「标记：」后面列出你在本轮系统提示里看到的全部探针标记（形如 ◆X◆ 的记号），按字母顺序连写；一个都没看到就写「标记：无」。只列真的出现在系统提示里的，不要猜，不要补。
第三行：「记忆：」后面写工作记忆里「纪元」这一格现在是什么，只写「月银」或「迷宫」两个字；看不到工作记忆就写「记忆：看不到」。

另有四条，只在玩家消息里出现对应的字时才做：
- 有「盖印」：把工作记忆的「纪元」改成「纪元印·月银」。
- 有「撤印」：把工作记忆的「纪元」改成「纪元印·迷宫」。
- 有「写甲」：在第三行之后另起一行，只写：探甲
- 有「落款」：整条回复的最后一行只写：§收

除了上面这几种情况，回复里不要出现「探甲」「§收」「纪元印」这些字。
'''

rear_prompt = '照格式输出：编号、标记、记忆三行；只有玩家写了「写甲」「落款」时才加对应的那一行。'

def entry(tag, words, typ, black, rng, depth, note):
    return {
        'enabled': True,
        'triggerWords': words, 'triggerWordsType': typ,
        'blackListWords': black, 'blackListWordsType': 'OR',
        'folder': '探针二',
        'priority': 100, 'probability': 100, 'scanDepth': depth,
        'triggerRange': rng, 'impactRange': ['system'],
        'contentMethod': 'single',
        'content': f'探针标记 ◆{tag}◆（{note}）',
    }

lore = [
    entry('P', ['公会'], 'OR', [], ['user'], 1, '基线：玩家这一条提到了公会'),
    entry('M', [SEAL], 'OR', [], ['working-memory'], 1, '只扫工作记忆，认纪元印·月银'),
    entry('W', ['公会'], 'OR', [SEAL], ['user', 'working-memory'], 1, '黑名单纪元印·月银，范围用户加工作记忆'),
    entry('X', ['/探甲(?![\\s\\S]*§收)/'], 'OR', [], ['user', 'assistant'], 2, '探甲后面不再出现§收'),
    entry('Y', ['/探甲(?=[\\s\\S]*§收)/'], 'OR', [], ['user', 'assistant'], 2, '探甲后面还会出现§收'),
    entry('Z', ['探甲'], 'OR', [], ['user', 'assistant'], 2, '探甲，不加条件'),
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
    ('测1 盖印', '【测1】盖印。'),
    ('测2 记忆里有印', '【测2】公会在哪？'),
    ('测3 写甲并落款', '【测3】写甲，并落款。'),
    ('测4 上一条里甲在收前', '【测4】你好。'),
    ('测5 只落款', '【测5】落款。'),
    ('测6 甲在这一条', '【测6】探甲'),
    ('测7 撤印', '【测7】撤印。'),
    ('测8 记忆里没印', '【测8】公会在哪？'),
]

rows = [
    ('1', '盖印。', '无', '记忆变成月银（这一轮报的可能还是旧值）'),
    ('2', '公会在哪？', 'P', 'M 在不在；W 在不在；记忆报的是什么'),
    ('3', '写甲，并落款。', '无', '回复多出「探甲」和最后一行「§收」'),
    ('4', '你好。', 'Z', 'X、Y 各在不在（应当只有 Y）'),
    ('5', '落款。', '无', '回复最后一行是「§收」'),
    ('6', '探甲', 'Z', '关键一条：X 在还是 Y 在'),
    ('7', '撤印。', '无', '记忆变回迷宫'),
    ('8', '公会在哪？', 'P', 'M 应当不在，W 应当在'),
]
trs = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in rows)

intro = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{{margin:0;padding:20px 16px;background:#14161a;color:#e8e4da;font:15px/1.7 "Noto Sans CJK SC",system-ui,sans-serif}}
h1{{font-size:20px;margin:0 0 8px}}p{{margin:6px 0}}table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}}
td,th{{border:1px solid #3a3e46;padding:6px 8px;text-align:left;vertical-align:top}}th{{background:#22262d}}.n{{color:#9aa3ad;font-size:13px}}</style></head><body>
<h1>探针二 · 扫描先后与工作记忆</h1>
<p>验两件事：世界书扫描时，上一条回复和你这一条是按什么先后拼起来的；世界书扫不扫得到工作记忆。从输入框的预设按钮里按顺序点「测1」到「测8」，每次发送。</p>
<p class="n">每轮回复三行：编号、标记、记忆。把八轮的「标记」和「记忆」两行抄给我就行。测1 之后也顺手看一眼工作记忆面板。</p>
<table><tr><th>测</th><th>发的是</th><th>一定会有</th><th>要看的</th></tr>{trs}</table>
</body></html>'''

card = {
    'title': '探针二·扫描先后与工作记忆（测试用）',
    'description': '测试卡：验证世界书扫描时多条消息的先后，以及工作记忆能否被扫描。不讲故事。',
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
open(sys.argv[2], 'w', encoding='utf-8').write(intro)

# checks
for e in lore:
    for w in e['triggerWords']:
        if w.startswith('/'):
            m = re.match(r'^/(.*)/([imsg]*)$', w)
            assert m, w
            re.compile(m.group(1))
            assert not re.search(r'\(\?<', m.group(1)) and not re.search(r'[+*?}]\?', m.group(1)), w
assert all(len(o['label']) <= 128 and len(o['value']) <= 1024 for o in card['options']['items'])
json.loads(card['memorySchema'])

# simulate both concatenation orders for X/Y on test 4 and test 6
X = re.compile(r'探甲(?![\s\S]*§收)'); Y = re.compile(r'探甲(?=[\s\S]*§收)')
r3 = '测3\n标记：无\n记忆：月银\n探甲\n§收'; r5 = '测5\n标记：无\n记忆：月银\n§收'
for name, prev, user in [('测4', r3, '【测4】你好。'), ('测6', r5, '【测6】探甲')]:
    for order, text in [('先回复后玩家', prev + '\n' + user), ('先玩家后回复', user + '\n' + prev)]:
        print(name, order, 'X' if X.search(text) else '-', 'Y' if Y.search(text) else '-')
print('ok', out)
