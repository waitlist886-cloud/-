#!/usr/bin/env python3
# 大框的真页面测试卡：只有样式、显示正则和一台回声器，不带世界书，导进平台开一局就能看框在真页面上的样子。
# 迷宫纪 1001 和月银纪做进同一张卡，看换纪元切不切得过去、两纪之间打不打架。图还没上图床，写成 data: 地址放进样式（样式里的 data: 平台不拦，上限 2097152 字），
# 两纪的图一起装不下，这里按 SHRINK 压小一号。正式卡走图床，不用压。没画四方的三纪只留材质。
# 用法（仓库根上）：python3 -I -X utf8 底稿/状态栏/大框/make_test_card.py   写 out/状态栏测试卡/，要 PIL
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
ART_MOON = os.path.join(HERE, '..', 'comfy', 'out', '月银纪_11-04', 'art')
OUT = os.path.join(ROOT, 'out', '状态栏测试卡')
LIMIT = 2097152
# 名字：（宽，质量）。宽写 None 的不缩，只压质量
SHRINK = {
    'maze_left': (1100, 68), 'maze_right': (1100, 68), 'maze_top': (1500, 74), 'maze_bottom': (3000, 62),
    'moon_left': (1100, 68), 'moon_right': (1100, 68), 'moon_top': (1500, 74), 'moon_bottom': (3000, 62), 'moon_hl': (900, 70), 'moon_hr': (900, 70), 'moon_lance': (380, 80),
    'items': (None, 60), 'doll': (None, 70),
    'boss_yanzuo1': (480, 58), 'boss_yanzuo2d': (480, 58), 'boss_yanzuo3d': (480, 58), 'boss_fenyuan1': (480, 58), 'boss_fenyuan2': (480, 58),
}


def read(*p):
    return open(os.path.join(*p), encoding='utf-8', newline='').read().replace('\r\n', '\n').strip()


css = read(HERE, 'frame.css')
total = 0
for n, (wd, q) in SHRINK.items():
    im = Image.open(os.path.join(ART_MOON if n.startswith(('moon', 'boss_fenyuan')) else ART, n + '.webp'))
    if wd and im.width > wd:
        im = im.resize((wd, round(im.height * wd / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=q, method=6, alpha_quality=80)
    total += buf.tell()
    print('  %-16s %s %4d KB' % (n, im.size, buf.tell() // 1024))
    css = css.replace('__ART__/%s.webp' % n, 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode())
print('  图一共', total // 1024, 'KB')
css = re.sub(r'url\("__ART__/[^"]*"\)', 'none', css)
assert '__ART__' not in css and len(css) <= LIMIT, len(css)

rules = json.loads(read(HERE, 'rules_frame.json'))
for r in rules:
    r.pop('name', None)

SAMPLES = [('样本_新手.txt', '迷宫新手'), ('样本_中期_交战.txt', '迷宫交战'), ('样本_史诗战_一阶.txt', '迷宫史诗一'), ('样本_史诗战.txt', '迷宫史诗二'), ('样本_史诗战_三阶.txt', '迷宫史诗三'),
           ('样本_月银纪_焚原.txt', '月银河滩'), ('样本_月银纪_焚原_史诗.txt', '月银焚原')]
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
<h1>测试 · 状态栏大框（迷宫纪与月银纪）</h1>
<p>这张卡只用来看框在真页面上的样子，不讲故事，没有世界书。AI 只会把写好的回复原样抄一遍。测完就可以删。</p>
<h2>怎么测换纪元</h2>
<ol>
<li>导入成一张新的私有卡，保存。别覆盖奥尔德兰那张。</li>
<li>开一局。点输入框上头的预设发送，等它写完再发下一条。迷宫新手、迷宫交战是迷宫纪 1001，迷宫史诗一二三是赝作魔王的三阶；月银河滩、月银焚原是月银纪。</li>
<li>照这个次序发一遍：迷宫新手 → 月银河滩 → 迷宫交战 → 月银焚原。每发一条，看整页是不是跟着新回复换了。</li>
<li>往上翻到上一纪的回复，看整页是不是跟着换回那一纪，再滚回底下。</li>
</ol>
<div class="btns">
<button type="button" onclick="fill('1')">迷宫新手</button>
<button type="button" onclick="fill('6')">月银河滩</button>
<button type="button" onclick="fill('2')">迷宫交战</button>
<button type="button" onclick="fill('7')">月银焚原</button>
</div>
<h2>换纪元时看什么</h2>
<ul>
<li>左右两扇、楣、座整套换了没有：迷宫纪是倒悬的螺旋塔和七神，月银纪是巨兽王种和传奇，两角一双手，右上角枪尖压着花边。</li>
<li>换回迷宫纪的时候，月银纪那双手和那杆枪有没有留在画上。</li>
<li>窗口的材质、字色、页签的金色或银灰，顶栏，输入栏，都跟着换了吗。</li>
<li>转场的徽记：迷宫纪是罗盘星，月银纪是菱形里一簇火。</li>
<li>页签的名字：月银纪是长歌、旅人、铸名、行囊、同行、传唱、记忆、战斗，迷宫纪是手札、面板、伟业、背包、同行、见闻、记忆、战斗。旧回复里各是各的字。</li>
</ul>
<h2>月银纪的各页看什么</h2>
<ul>
<li>旅人：法门、兵器·风格、传唱到第几个国；没有旅印、命路和公会那些东西。</li>
<li>铸名：一条路到传奇为止，认兵、成式、名器、冠名；斩过什么；技能书。</li>
<li>行囊：曜核、月银罐、盐砖、烧废的仓签，钱写金银铜。</li>
<li>传唱：诗人在唱是一张歌谱，悬赏板是木板上钉的羊皮纸，按兽分档。</li>
<li>战斗：河滩那一条报兽和曜；月银焚原是史诗战，看焚原的立绘和火冠，看地盘、身后的火、抬人那几张。</li>
</ul>
<p class="n">两纪的图都写在样式里，塞不下原图，压小了一号，比正式的糊一点。正式卡会放图床，不会这样。这张卡有两兆上下，开局时可能慢一两秒。</p>
<script>
function fill(v){try{window.parent.postMessage({type:'rili-set-input',value:v},'*')}catch(e){}}
</script>
</body></html>'''

card = {
    'title': '测试·状态栏大框（两纪）',
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
        [(lb, str(i + 1)) for i, (_, lb) in enumerate(SAMPLES)] + [('超程铭刻', '【超程铭刻：你想要记住的npc】'), ('防抢话', '【防抢话：开启/关闭】')])]},
    'cardsTags': [{'tag': {'name': '测试'}}],
    'cardsVoices': [],
}
os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, '奥尔德兰_大框测试卡_两纪.json')
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', path, os.path.getsize(path) // 1024, 'KB', '样式', len(css), '字', '正则', len(rules), '条', '回声词', len(SYSTEM), '字')
