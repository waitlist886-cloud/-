#!/usr/bin/env python3
# 大框的真页面测试卡：只有样式、显示正则和一台回声器，不带世界书，导进平台开一局就能看框在真页面上的样子。
# 图还没上图床，迷宫纪四幅写成 data: 地址放进样式（样式里的 data: 平台不拦，上限 2097152 字）。别的四纪没有图，只留材质。
# 用法（仓库根上）：python3 -I -X utf8 底稿/状态栏/大框/make_test_card.py   写 out/状态栏测试卡/
import base64
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ART = os.path.join(HERE, '..', 'comfy', 'out', '四方_11-03', 'art_fu_ab')
OUT = os.path.join(ROOT, 'out', '状态栏测试卡')
LIMIT = 2097152


def read(*p):
    return open(os.path.join(*p), encoding='utf-8', newline='').read().replace('\r\n', '\n').strip()


css = read(HERE, 'frame.css')
for n in ('left', 'right', 'top', 'bottom'):
    b = open(os.path.join(ART, 'maze_%s.webp' % n), 'rb').read()
    css = css.replace('__ART__/maze_%s.webp' % n, 'data:image/webp;base64,' + base64.b64encode(b).decode())
css = re.sub(r'url\("__ART__/[^"]*"\)', 'none', css)
assert '__ART__' not in css and len(css) <= LIMIT, len(css)

rules = json.loads(read(HERE, 'rules_frame.json'))
for r in rules:
    r.pop('name', None)

S1 = read(HERE, '..', '手札', '样本_迷宫纪1001_构想.txt')
S2 = read(HERE, '..', '紧凑', '样本_迷宫纪1001_紧凑.txt')
SYSTEM = '''你是一台回声器，只用来检查聊天页的显示。不讲故事，不扮演任何人，不回答问题。

每轮只看玩家这句话的第一个数字：
- 是 1：把下面「样本一」两条分隔线之间的全部内容原样输出。
- 是 2：把下面「样本二」两条分隔线之间的全部内容原样输出。
- 没有数字：按 1 处理。

原样的意思是一个字、一个符号、一个换行都不改，不省略，不翻译，不放进代码块，前后不加任何别的字。分隔线本身不输出。

样本一
=====
%s
=====

样本二
=====
%s
=====
''' % (S1, S2)

INTRO = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;padding:20px 16px 32px;background:#0d0d2a;color:#ebe5d6;font:15px/1.75 "Noto Sans CJK SC","PingFang SC",system-ui,sans-serif}
h1{font-size:21px;margin:0 0 6px;color:#f2e2b6}h2{font-size:16px;margin:22px 0 6px;color:#d6b26a}
p,li{margin:6px 0}ol,ul{padding-left:22px;margin:6px 0}
.btns{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
button{background:#1b1a48;color:#f2e2b6;border:1px solid #c9a75e;border-radius:8px;padding:9px 14px;font:inherit;cursor:pointer}
.n{color:#b3ad9f;font-size:13px}
</style></head><body>
<h1>测试 · 状态栏大框（迷宫纪 1001）</h1>
<p>这张卡只用来看框在真页面上的样子，不讲故事，没有世界书。AI 只会把写好的两条回复原样抄一遍。测完就可以删。</p>
<h2>怎么测</h2>
<ol>
<li>导入成一张新的私有卡，保存。别覆盖奥尔德兰那张。</li>
<li>开一局。点输入框上头的「样本一」发送，等它写完，再点「样本二」发送。</li>
<li>照下面看一遍，电脑和手机各看一次，截图发回来。</li>
</ol>
<div class="btns">
<button type="button" onclick="fill('1')">样本一</button>
<button type="button" onclick="fill('2')">样本二</button>
</div>
<h2>电脑上看什么</h2>
<ul>
<li>框的下沿和输入框上头那排小签有没有撞上，中间空多少。</li>
<li>最新一条底下那排页签（手札、面板……）贴在框底，有没有被那排小签压住，也没有隔得太远。</li>
<li>滚到最底，最新一条末尾有没有一大块空。</li>
<li>回复外头还有没有平台的灰底和边框。</li>
<li>输入框是深色金线吗，字看得清吗。</li>
<li>点一下面板、背包：先暗下去转徽记，再进那一页。</li>
<li>打开、收起左边的侧栏，两扇画和框有没有错位。</li>
<li>右边框上那颗小菱形，滚动时跟着走吗。</li>
</ul>
<h2>手机上看什么</h2>
<ul>
<li>不挂两扇画，框只留一圈细边，页签有没有被输入框压住。</li>
</ul>
<p class="n">图都写在样式里，这张卡有两兆上下，开局时可能慢一两秒。正式卡会放图床，不会这样。</p>
<script>
function fill(v){try{window.parent.postMessage({type:'rili-set-input',value:v},'*')}catch(e){}}
</script>
</body></html>'''

card = {
    'title': '测试·状态栏大框（迷宫纪1001）',
    'description': '测试卡：看状态栏大框在真页面上的样子。不讲故事，没有世界书，测完即删。',
    'language': 'zh',
    'containsNSFW': False,
    'publicAccess': False,
    'isAnonymous': False,
    'enableSafeguard': False,
    'prompt': {
        'systemPrompt': SYSTEM,
        'headPrompt': '',
        'rearPrompt': '只输出样本原文，不加别的字。',
        'suggestionsPrompt': '',
        'lorebook': [],
    },
    'assistantRegexReplace': rules,
    'injectStyles': css,
    'introPage': INTRO,
    'enableMemorySchema': False,
    'options': {'items': [{'order': n, 'label': l, 'type': 'SET-INPUT', 'value': v} for n, (l, v) in enumerate(
        [('样本一', '1'), ('样本二', '2'), ('超程铭刻', '【超程铭刻：你想要记住的npc】'), ('防抢话', '【防抢话：开启/关闭】')])]},
    'cardsTags': [{'tag': {'name': '测试'}}],
    'cardsVoices': [],
}
os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, '奥尔德兰_大框测试卡_迷宫纪1001.json')
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', path, os.path.getsize(path) // 1024, 'KB', '样式', len(css), '字', '正则', len(rules), '条', '回声词', len(SYSTEM), '字')
