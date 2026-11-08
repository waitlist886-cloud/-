#!/usr/bin/env python3
# 对话框、名词提示、衣着差分的测试卡（11-05）。只带迷宫纪 1001：三条样本，三位有新图（埃莉诺、蒂法、莱恩哈特），别的人留影子。没有世界书，回声器照抄样本，看真页面上的样子。
# 图还没上图床，写成 data: 放进样式，所以压小了。正式卡走图床。
# 用法（仓库根上）：python3 -I -X utf8 底稿/状态栏/大框/make_test_card_talk.py   写 out/状态栏测试卡/，要 PIL
import base64
import io
import json
import os
import re
import sys

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ART = os.path.join(HERE, '..', 'comfy', 'out', '四方_11-03', 'art_fu_ab')
CAST = os.path.join(HERE, '..', 'comfy', 'out', '立绘_v3', 'art')
# 11-07：立绘和表情上了 ImgBB（comfy/imgbb_up.py，清单 comfy/out/图床/imgbb_1001.json，文件名 → url），样式里直接写图床地址；
# 清单里没有的那几张照旧写 data:（压小），哪张都没有的留影子。四方的框图照旧 data:。
HOSTED = os.path.join(HERE, '..', 'comfy', 'out', '图床', 'imgbb_1001.json')
URLS = {k: v['url'] for k, v in json.load(open(HOSTED, encoding='utf-8')).items()} if os.path.exists(HOSTED) else {}
OUT = os.path.join(ROOT, 'out', '状态栏测试卡')
LIMIT = 2097152
# 名字：（宽，质量）
SHRINK = {'maze_left': (800, 58), 'maze_right': (800, 58), 'maze_top': (1400, 66), 'maze_bottom': (2400, 52), 'items': (None, 46), 'doll': (None, 66)}
for en in set(json.load(open(os.path.join(HERE, 'roster.json'), encoding='utf-8')).values()):
    for pre, wq in (('por_', (1920, 74)), ('face_', (600, 78))):
        if pre + en + '.webp' not in URLS and os.path.exists(os.path.join(CAST, pre + en + '.webp')):
            SHRINK[pre + en] = wq


def read(*p):
    return open(os.path.join(*p), encoding='utf-8', newline='').read().replace('\r\n', '\n').strip()


css = read(HERE, 'frame.css')
total = 0
for n, (wd, q) in SHRINK.items():
    im = Image.open(os.path.join(CAST if n.startswith(('por_', 'face_')) else ART, n + '.webp'))
    if wd and im.width > wd:
        im = im.resize((wd, round(im.height * wd / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=q, method=6, alpha_quality=80)
    total += buf.tell()
    print('  %-16s %s %4d KB' % (n, im.size, buf.tell() // 1024))
    css = css.replace('__ART__/%s.webp' % n, 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode())
print('  图一共', total // 1024, 'KB')
hosted = 0
for fn, u in URLS.items():
    if '__ART__/%s' % fn in css:
        css = css.replace('__ART__/%s' % fn, u)
        hosted += 1
print('  图床地址', hosted, '张')
css = re.sub(r'url\("__ART__/[^"]*"\)', 'none', css)
assert '__ART__' not in css and len(css) <= LIMIT, len(css)

rules = json.loads(read(HERE, 'rules_frame.json'))
for r in rules:
    r.pop('name', None)

SAMPLES = [('样本_对话_开印日.txt', '开印日'), ('样本_对话_打烊.txt', '打烊以后'), ('样本_对话_坡口.txt', '坡口外溢')]
TEXTS = [read(HERE, f) for f, _ in SAMPLES]
CN = '一二三四五六七八九'
SYSTEM = '''你是一台回声器，只用来检查聊天页的显示。不讲故事，不扮演任何人，不回答问题。

每轮只看玩家这句话的第一个数字，把下面对应那一条样本两条分隔线之间的全部内容原样输出：
%s- 没有数字：按 1 处理。

原样的意思是一个字、一个符号、一个换行都不改，不省略，不翻译，不放进代码块，前后不加任何别的字。分隔线本身不输出。

%s''' % (''.join('- 是 %d：样本%s。\n' % (i + 1, CN[i]) for i in range(len(TEXTS))), ''.join('样本%s\n=====\n%s\n=====\n\n' % (CN[i], t) for i, t in enumerate(TEXTS)))

INTRO = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;padding:20px 16px 32px;background:#0d0d2a;color:#ebe5d6;font:15px/1.75 "Noto Sans CJK SC","PingFang SC",system-ui,sans-serif}
h1{font-size:21px;margin:0 0 6px;color:#f2e2b6}h2{font-size:16px;margin:22px 0 6px;color:#d6b26a}
p,li{margin:6px 0}ol,ul{padding-left:22px;margin:6px 0}
.btns{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
button{background:#1b1a48;color:#f2e2b6;border:1px solid #c9a75e;border-radius:8px;padding:9px 14px;font:inherit;cursor:pointer}
.n{color:#b3ad9f;font-size:13px}
</style></head><body>
<h1>测试 · 对话框、名词提示、衣着差分（迷宫纪）</h1>
<p>这张卡只用来看样子，不讲故事，没有世界书。AI 只会把写好的回复原样抄一遍。测完就可以删。</p>
<h2>怎么测</h2>
<ol>
<li>导入成一张新的私有卡，保存。别覆盖奥尔德兰那张。</li>
<li>开一局，点输入框上头的预设发送，等它写完再发下一条。</li>
</ol>
<div class="btns">
<button type="button" onclick="fill('1')">开印日</button>
<button type="button" onclick="fill('2')">打烊以后</button>
<button type="button" onclick="fill('3')">坡口外溢</button>
</div>
<h2>看什么</h2>
<ul>
<li>对话框：人物开口单独一块，头像、名牌、一句话。同一个人说不同的话，表情跟着变。</li>
<li>名词提示：正文里带虚线的词，鼠标移上去或者手指点一下出一张小卡。点名册那一个是 AI 现编的，别的是表里的。</li>
<li>衣着：点页签「同行」，上头小头像点谁看谁。开印日是常服（莱恩哈特是正装），打烊以后是私服，坡口是战斗装。鼠标移到立绘上看全身。</li>
</ul>
<p class="n">迷宫纪 1001 年的六十八位都有图了，立绘和表情走 ImgBB 图床（i.ibb.co），头一回打开要等图下载。四方的框图还是写在样式里压小的。样本里只写到几位，别的人要在「同行」页点到才看得见。</p>
<script>
function fill(v){try{window.parent.postMessage({type:'rili-set-input',value:v},'*')}catch(e){}}
</script>
</body></html>'''

card = {
    'title': '测试·对话框与衣着差分（迷宫纪）',
    'description': '测试卡：看对话框、名词提示和衣着差分在真页面上的样子。不讲故事，没有世界书，测完即删。',
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
        [(lb, str(i + 1)) for i, (_, lb) in enumerate(SAMPLES)])]},
    'cardsTags': [{'tag': {'name': '测试'}}],
    'cardsVoices': [],
}
os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, '奥尔德兰_对话框测试卡_迷宫纪_图床.json' if URLS else '奥尔德兰_对话框测试卡_迷宫纪.json')
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', path, os.path.getsize(path) // 1024, 'KB', '样式', len(css), '字', '正则', len(rules), '条', '回声词', len(SYSTEM), '字')
