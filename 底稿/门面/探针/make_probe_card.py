#!/usr/bin/env python3
# 11-12 门面探针卡：一张不讲故事的小卡，测日里的介绍页能做什么（门面重做_方向稿.md 第七节“没测过的”那几样，加一圈顺手能测的）。
#   一、介绍页让不让从外面载脚本、模块、样式、字体、图、音频、视频，各个镜像通不通；被安全策略拦了的话把策略原文报出来。
#   二、沙箱里有什么：存储、WebGL、外链图当贴图、wasm、worker、样式能力、帧率、权限。
#   三、要手点的：声音、复制、振动、全屏、开新页、rili-set-input（短的、多行的、一万字的）、倾斜感应。
#   四、开聊以后介绍页还在不在：页面上一个四位码、一个计时、一段循环的轻响。
# 结果在页面底下攒成一段字，点一下填进输入框（顺带又测了一回 rili-set-input），用户复制回来。
# 外链的测试桩在图床仓库的 probe 分支（gen_ext.py 现做，push_ext.py 推），地址在 ext_manifest.json。
# 用法：python -I -X utf8 make_probe_card.py [输出目录]        默认 out/探针_11-12/
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', '探针_11-12')
os.makedirs(OUT, exist_ok=True)
VER = '11-12b'        # b：照头一回在真页面上跑回来的结果修了外链样式和帧率两处误报，“填一万字”换成量长度上限的梯子
FONT = 'https://cdn.jsdelivr.net/npm/@fontsource/cinzel@5.0.8/files/cinzel-latin-400-normal.woff2'

man = json.load(open(os.path.join(HERE, 'ext_manifest.json'), encoding='utf-8'))
tpl = open(os.path.join(HERE, 'probe_intro.html'), encoding='utf-8').read()
for a, b in (('__BASE__', man['base']), ('__PATH__', man['path']), ('__RAW__', man['raw']), ('__FONT__', FONT), ('__VER__', VER)):
    assert a in tpl, a
    tpl = tpl.replace(a, b)
assert '__' + 'BASE' not in tpl and '__VER' not in tpl
intro = tpl

SYS = '这是一张测试平台用的探针卡，不讲故事，不加解释。不管玩家发什么，只回复一行：探针回声｜后面接玩家这一句话的前二十个字。只输出这一行。'
card = {
    'title': '奥尔德兰门面探针_' + VER,
    'description': '测平台用的小卡，不讲故事：介绍页能不能从外面载脚本和声音、开聊以后介绍页还在不在、一点就填进输入框的指令。测完删。',
    'language': 'zh', 'containsNSFW': False, 'publicAccess': False, 'isAnonymous': False, 'enableSafeguard': False,
    'prompt': {'systemPrompt': SYS, 'headPrompt': '', 'rearPrompt': '', 'lorebook': []},
    'assistantRegexReplace': [],
    'injectStyles': '',
    'introPage': intro,
    'enableMemorySchema': False,
    'options': {'items': [{'order': 0, 'label': '发一句试试', 'type': 'SET-INPUT', 'value': '探针测试'}]},
    'cardsTags': [],
    'cardsVoices': [],
}
path = os.path.join(OUT, '奥尔德兰门面探针_%s.json' % VER)
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False, indent=1)
# 本地验用的（能重出，不进库）：介绍页单独一份，加两个照日里办法装它的壳，都放 本地验/
LOCAL = os.path.join(OUT, '本地验')
os.makedirs(LOCAL, exist_ok=True)
with open(os.path.join(LOCAL, 'intro.html'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(intro)
host = open(os.path.join(HERE, 'host.html'), encoding='utf-8').read()
assert host.count('<!--CSP-->') == 1
with open(os.path.join(LOCAL, 'host.html'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(host)
CSP = "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self' 'unsafe-inline' data: blob:; img-src 'self' data: blob: https://cdn.jsdelivr.net\">"
with open(os.path.join(LOCAL, 'host_csp.html'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(host.replace('<!--CSP-->', CSP))
print('ok', path, os.path.getsize(path), '字节，介绍页', len(intro), '字')
