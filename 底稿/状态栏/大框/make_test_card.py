#!/usr/bin/env python3
# 大框的真页面测试卡：只有样式、显示正则和一台回声器，不带世界书，导进平台开一局就能看框在真页面上的样子。
# 月银纪、纷争纪和迷宫纪 1001 做进同一张卡，看换纪元切不切得过去。时间不倒流，只照先后往下切，切不回来。图还没上图床，写成 data: 地址放进样式（样式里的 data: 平台不拦，上限 2097152 字），
# 三纪的图一起装不下，这里按 SHRINK 压小一号。正式卡走图床，不用压。没画四方的两纪只留材质。
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
OUT = os.path.join(ROOT, 'out', '状态栏测试卡')
LIMIT = 2097152
# 名字：（宽，质量）。宽写 None 的不缩，只压质量
SHRINK = {
    'maze_left': (840, 56), 'maze_right': (840, 56), 'maze_top': (1250, 62), 'maze_bottom': (2500, 48),
    'moon_left': (840, 56), 'moon_right': (840, 56), 'moon_top': (1250, 62), 'moon_bottom': (2500, 48), 'moon_hl': (720, 58), 'moon_hr': (720, 58), 'moon_lance': (300, 68),
    'strife_left': (840, 62), 'strife_right': (840, 62), 'strife_top': (1250, 66), 'strife_bottom': (2500, 58),
    'items': (None, 48), 'doll': (None, 70),
    'boss_yanzuo1': (400, 48), 'boss_yanzuo2d': (400, 48), 'boss_yanzuo3d': (400, 48), 'boss_fenyuan1': (400, 48), 'boss_fenyuan2': (400, 48), 'boss_yamon1': (400, 48), 'boss_yamon2': (400, 48),
}


def read(*p):
    return open(os.path.join(*p), encoding='utf-8', newline='').read().replace('\r\n', '\n').strip()


css = read(HERE, 'frame.css')
total = 0
for n, (wd, q) in SHRINK.items():
    im = Image.open(os.path.join(ART_MOON if n.startswith(('moon', 'boss_fenyuan')) else ART_STRIFE if n.startswith(('strife', 'boss_yamon')) else ART, n + '.webp'))
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

# 照时间先后排：月银纪，纷争纪，迷宫纪
SAMPLES = [('样本_月银纪_焚原.txt', '月银河滩'), ('样本_月银纪_焚原_史诗.txt', '月银焚原'), ('样本_纷争纪_墙前.txt', '纷争墙前'), ('样本_纷争纪_亚蒙.txt', '纷争亚蒙'), ('样本_新手.txt', '迷宫新手'), ('样本_史诗战_一阶.txt', '迷宫史诗')]
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
<h1>测试 · 状态栏大框（月银纪、纷争纪、迷宫纪）</h1>
<p>这张卡只用来看框在真页面上的样子，不讲故事，没有世界书。AI 只会把写好的回复原样抄一遍。测完就可以删。</p>
<h2>怎么测换纪元</h2>
<ol>
<li>导入成一张新的私有卡，保存。别覆盖奥尔德兰那张。</li>
<li>开一局。点输入框上头的预设发送，等它写完再发下一条。</li>
<li>照时间先后发一遍：月银河滩 → 月银焚原 → 纷争墙前 → 纷争亚蒙 → 迷宫新手 → 迷宫史诗。时间不倒流，不用往回发。每发一条，看整页是不是跟着新回复换了。</li>
</ol>
<div class="btns">
<button type="button" onclick="fill('1')">月银河滩</button>
<button type="button" onclick="fill('3')">纷争墙前</button>
<button type="button" onclick="fill('5')">迷宫新手</button>
</div>
<h2>纷争纪的四方看什么</h2>
<ul>
<li>左扇：左上五尊魔神（戴兜帽胸口透白光的绝后者亚蒙、一身兽群的噬群者、骨头折反的错骨者、断角胸口烧着东门之火的拆墙者、一身烂疮的箭不愈者），底下魔族的传奇和各营，后头会走的攻城神殿。</li>
<li>右扇：右上五位正神（持塔盾的举盾者、蒙黑纱骑黑马的立誓者、肩上积雪的擎山者、红铜短发的挽弓者、落在最后的断后者），诺伦骑白马，三位女王，辛美尔的小队，后头星纱列车和擎天巨神兵，右下各族军士和机兵。</li>
<li>楣：断开的桂冠和交织的兵刃。座：白石长垒，左边破口和发光的盾，右边城门和圈环的结界。</li>
<li>窗口换成了烟熏过的深色军册皮，左边一道红线。</li>
</ul>
<h2>纷争纪的各页看什么</h2>
<ul>
<li>页签：战记、军册、军功、军需、同袍、战报、记忆、战斗。</li>
<li>军册：无印，战报写过几回；没有旅印和公会那些东西。</li>
<li>军功：一条路到传奇为止，节点下头写新兵、寻常的兵、老兵、一方镇将、改写一场会战、战报留名；挡下过谁；技能书。</li>
<li>战报：军册上撕下来的一页，红线和火漆；段城门口的赏格钉在白石墙上。</li>
<li>战斗：墙前那一条报成群、成队、镇将；纷争亚蒙是史诗战，看亚蒙的立绘，第二阶叫银白的字缠住了腿，看殿光、出墙的门、担架那几张。</li>
<li>在办那一张卡（上一版月银纪竖着排的那个）在各纪都看一眼。</li>
</ul>
<p class="n">三纪的图都写在样式里，塞不下原图，压小了不少，比正式的糊。正式卡会放图床，不会这样。这张卡有两兆上下，开局时可能慢一两秒。</p>
<script>
function fill(v){try{window.parent.postMessage({type:'rili-set-input',value:v},'*')}catch(e){}}
</script>
</body></html>'''

card = {
    'title': '测试·状态栏大框（三纪）',
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
path = os.path.join(OUT, '奥尔德兰_大框测试卡_三纪.json')
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', path, os.path.getsize(path) // 1024, 'KB', '样式', len(css), '字', '正则', len(rules), '条', '回声词', len(SYSTEM), '字')
