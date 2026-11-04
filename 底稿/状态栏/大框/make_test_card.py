#!/usr/bin/env python3
# 大框的真页面测试卡：只有样式、显示正则和一台回声器，不带世界书，导进平台开一局就能看框在真页面上的样子。
# 月银纪、纷争纪、山铜纪和迷宫纪 1001 做进同一张卡，看换纪元切不切得过去。时间不倒流，只照先后往下切，切不回来。图还没上图床，写成 data: 地址放进样式（样式里的 data: 平台不拦，上限 2097152 字），
# 四纪的图一起装不下，这里按 SHRINK 压小。正在看的这一纪给得多，看过的压得狠。正式卡走图床，不用压。没画四方的前传只留材质。
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
ART_STRIFE = os.path.join(HERE, '..', 'comfy', 'out', '纷争纪_11-04', 'art')
ART_BRONZE = os.path.join(HERE, '..', 'comfy', 'out', '山铜纪_11-04', 'art')
OUT = os.path.join(ROOT, 'out', '状态栏测试卡')
LIMIT = 2097152
# 名字：（宽，质量）。宽写 None 的不缩，只压质量
SHRINK = {
    'maze_left': (640, 50), 'maze_right': (640, 50), 'maze_top': (1000, 56), 'maze_bottom': (2000, 42),
    'moon_left': (640, 50), 'moon_right': (640, 50), 'moon_top': (1000, 56), 'moon_bottom': (2000, 42), 'moon_hl': (560, 50), 'moon_hr': (560, 50), 'moon_lance': (240, 60),
    'strife_left': (640, 54), 'strife_right': (640, 54), 'strife_top': (1000, 58), 'strife_bottom': (2000, 46),
    'bronze_left': (900, 62), 'bronze_right': (900, 62), 'bronze_top': (1400, 70), 'bronze_bottom': (2800, 56),
    'items': (None, 46), 'doll': (None, 66),
    # 样本里用得上的那几阶，别的不带
    'boss_yanzuo1': (360, 44), 'boss_fenyuan2': (360, 44), 'boss_yamon2': (360, 44), 'boss_gemoen1': (440, 50), 'boss_gemoen2': (440, 50),
}


def read(*p):
    return open(os.path.join(*p), encoding='utf-8', newline='').read().replace('\r\n', '\n').strip()


css = read(HERE, 'frame.css')
total = 0
for n, (wd, q) in SHRINK.items():
    im = Image.open(os.path.join(ART_MOON if n.startswith(('moon', 'boss_fenyuan')) else ART_STRIFE if n.startswith(('strife', 'boss_yamon')) else ART_BRONZE if n.startswith(('bronze', 'boss_gemoen')) else ART, n + '.webp'))
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

# 照时间先后排：月银纪，纷争纪，山铜纪，迷宫纪
SAMPLES = [('样本_月银纪_焚原.txt', '月银河滩'), ('样本_月银纪_焚原_史诗.txt', '月银焚原'), ('样本_纷争纪_墙前.txt', '纷争墙前'), ('样本_纷争纪_亚蒙.txt', '纷争亚蒙'), ('样本_山铜纪_长阶.txt', '山铜长阶'), ('样本_山铜纪_葛摩恩.txt', '山铜矿坑'), ('样本_新手.txt', '迷宫新手'), ('样本_史诗战_一阶.txt', '迷宫史诗')]
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
<h1>测试 · 状态栏大框（月银纪、纷争纪、山铜纪、迷宫纪）</h1>
<p>这张卡只用来看框在真页面上的样子，不讲故事，没有世界书。AI 只会把写好的回复原样抄一遍。测完就可以删。</p>
<h2>怎么测换纪元</h2>
<ol>
<li>导入成一张新的私有卡，保存。别覆盖奥尔德兰那张。</li>
<li>开一局。点输入框上头的预设发送，等它写完再发下一条。</li>
<li>这一回主要看山铜纪：先发纷争亚蒙，再发山铜长阶、山铜矿坑，最后发迷宫新手。每发一条，看整页是不是跟着新回复换了。</li>
</ol>
<div class="btns">
<button type="button" onclick="fill('4')">纷争亚蒙</button>
<button type="button" onclick="fill('5')">山铜长阶</button>
<button type="button" onclick="fill('6')">山铜矿坑</button>
<button type="button" onclick="fill('7')">迷宫新手</button>
</div>
<h2>山铜纪的四方看什么</h2>
<ul>
<li>右扇：一道剑光把天切成半夜和黎明。索恩薇娅拿挽昼从底下往上斩，王座削了顶，王冠断成两半。大阶上是苇棚区的火把。底下是东陆的传奇：艾瑟莉娅、白鸦五人（薇丝塔扛那面难看的旗）、布洛姆加、芙莉莲、霍布。</li>
<li>左扇：巴尔缇娜落下王棋，薇瑟兰从背后抱着她，一身伤，正在散成灰和光。七魔神将站在黑白棋盘上，上头三尊死了的魔神正被拆开，七条光落到七个人手里。</li>
<li>楣：恶神的爪扣住框的两个角，正中爪子攥着一座倒悬的螺旋塔，那是大迷宫的虚影。</li>
<li>座：灰雨城的废墟。左边南门的门洞，刻满道的门柱，篮子和一小堆火。右边书屋那一面墙，南坡的小坟和木签，碑脚下一杆断枪。</li>
<li>这一纪两扇不对打，各是各的群像。</li>
</ul>
<h2>山铜纪的各页看什么</h2>
<ul>
<li>页签：碑记、名字、刻碑、鞍袋、团里、号墙、记忆、战斗。</li>
<li>名字：页头是碑匠问你背面怎么刻。没有旅印，写团名、行会档次、碑背面刻过几块。</li>
<li>刻碑：一条路到传奇为止，节点下头写这一纪怎么看这一档，传奇是碑的正面。</li>
<li>号墙：碑和传唱是一块黑底白字的拓片，公所的信，酒馆里的话，号墙上的活钉在灰石墙上。</li>
<li>战斗：山铜长阶是普通战斗。山铜矿坑是史诗战，看葛摩恩的立绘，第二段叫自己的环锁住，看身后的路、谁背得动人那几张。</li>
</ul>
<p class="n">四纪的图都写在样式里，塞不下原图，压小了不少，山铜纪以外的压得更狠，比正式的糊。正式卡会放图床，不会这样。这张卡有两兆上下，开局时可能慢一两秒。</p>
<script>
function fill(v){try{window.parent.postMessage({type:'rili-set-input',value:v},'*')}catch(e){}}
</script>
</body></html>'''

card = {
    'title': '测试·状态栏大框（四纪）',
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
        [(lb, str(i + 1)) for i, (_, lb) in enumerate(SAMPLES)])]},
    'cardsTags': [{'tag': {'name': '测试'}}],
    'cardsVoices': [],
}
os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, '奥尔德兰_大框测试卡_四纪.json')
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', path, os.path.getsize(path) // 1024, 'KB', '样式', len(css), '字', '正则', len(rules), '条', '回声词', len(SYSTEM), '字')
