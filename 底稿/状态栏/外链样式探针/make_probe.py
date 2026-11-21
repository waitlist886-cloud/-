#!/usr/bin/env python3
# 11-21 外链样式探针卡：卡里的样式（injectStyles，四纪大框里 1.46MB）能不能挪到图床，卡里只留几行 @import。
# 测的几路（每一路一行色块，没生效是红的「没生效」，生效了变绿「通」）：
#   0 卡的样式格里直接写的规则（对照，应当通）
#   1 卡的样式格里 @import（rili-chat-frontend §1.2 说平台会拿掉，这一行确认一下，应当红）
#   2-5 回复里显示正则插 <link rel=stylesheet>，四个镜像各一行（fastly、testingcf、gcore、cdn）
#   6 回复里插 <style>@import …</style>（§10 第 3 条，没测过）
#   7 回复里插内嵌 <style>（对照，应当通）
#   8 外链样式里用相对地址的图（棋盘格小图出没出来）
#   9 现行四纪大框那一整份样式，照平台的规矩加好 .custom-styles 作用域（scopeCss），挪上图床，回复里 <link> 它（1.6MB）
# 色块下面再画一块真的状态栏（样本_山铜纪_长阶），用正式卡那一整套显示正则，卡的样式格里没有状态栏样式，全靠第 9 路。
# 用法：python -I -X utf8 make_probe.py [输出.json]
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
man = json.load(open(os.path.join(HERE, 'ext_manifest.json'), encoding='utf-8'))
P = man['path']          # /gh/…@提交号/
U = lambda host, f: 'https://%s.jsdelivr.net%s%s' % (host, P, f)
card0 = json.load(open(os.path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框.json'), encoding='utf-8'))
sample = open(os.path.join(ROOT, '底稿', '状态栏', '大框', '样本_山铜纪_长阶.txt'), encoding='utf-8').read().strip()

ROWS = [('t0', '卡的样式格，直接写的规则（对照）'),
        ('t1', '卡的样式格 @import（应当被平台拿掉）'),
        ('t2', '回复里插 link，fastly 镜像'),
        ('t3', '回复里插 link，testingcf 镜像'),
        ('t4', '回复里插 link，gcore 镜像'),
        ('t5', '回复里插 link，cdn 镜像'),
        ('t6', '回复里插 style 加 @import'),
        ('t7', '回复里插内嵌 style（对照）'),
        ('t8', '外链样式里用相对地址的图'),
        ('t9', '整份 1.6MB 样式挪上图床')]


def row(c, label):
    pic = '<span class="pic" style="display:inline-block;width:40px;height:40px;margin-left:10px;vertical-align:middle;border:1px solid #888"></span>' if c == 't8' else ''
    return ('<div class="t %s" style="margin:4px 0;padding:8px 12px;border-radius:6px;background:#7a2222;color:#fff;font:15px/1.5 system-ui,sans-serif">'
            '%s　<b><span class="no">没生效</span><span class="ok" style="display:none">通</span></b>%s</div>') % (c, label, pic)


ok = lambda c: '.%s .no{display:none!important}.%s .ok{display:inline!important}.%s{background:#1f6b3a!important}' % (c, c, c)
LINKS = ''.join('<link rel="stylesheet" href="%s">' % U(h, f) for h, f in
                [('fastly', 'b.css'), ('testingcf', 'c.css'), ('gcore', 'd.css'), ('cdn', 'e.css'), ('cdn', 'g.css'), ('cdn', 'full.css')])
PANEL = (LINKS
         + '<style>@import url("%s");%s</style>' % (U('cdn', 'f.css'), ok('t7'))
         + '<div class="probe11" style="margin:8px 0;padding:10px;border:1px solid #666;border-radius:8px">'
         + '<div style="font:bold 16px system-ui,sans-serif;margin-bottom:6px">外链样式探针 11-21</div>'
         + ''.join(row(c, l) for c, l in ROWS) + '</div>')

css = '@import url("%s");\n%s' % (U('cdn', 'a.css'), ok('t0'))

rules = [{'enabled': True, 'applyMode': 'all', 'messageRole': 'assistant', 'regex': '/〔样式探针〕/g', 'replaceString': PANEL},
         {'enabled': True, 'applyMode': 'all', 'messageRole': 'assistant', 'regex': '/〔状态栏样本〕/g', 'replaceString': sample.replace('$', '$$')}]
rules += card0['assistantRegexReplace']

SYS = '每一轮只输出下面两行，一个字也不多：\n〔样式探针〕\n〔状态栏样本〕'

INTRO = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:18px;font:15px/1.8 system-ui,sans-serif;background:#16181d;color:#e8e4da">
<h2 style="margin:0 0 10px">外链样式探针 11-21</h2>
<p>这张卡不讲故事，只测聊天页肯不肯从图床载样式。测完删掉就行。</p>
<ol>
<li>开一局，随便发一句，比如「测」。</li>
<li>回复里先是十行色块，红的写「没生效」，变绿写「通」。截一张图。</li>
<li>色块下面是一块山铜纪的状态栏，样式全从图床载。看它跟正式卡里的样子像不像，截一张图。</li>
<li>手机上再开一回，同样截两张。刷新一下页面、隔一会儿再看一回，看绿的会不会变回红的。</li>
</ol>
<button style="margin-top:12px;padding:10px 18px;font-size:15px;border-radius:8px;border:0;background:#c9a45c;color:#1a1408"
 onclick="window.parent.postMessage({type:'rili-set-input', value:'测'},'*')">填入「测」</button>
</body></html>'''

card = {
    'title': '奥尔德兰外链样式探针_11-21',
    'description': '测平台用的小卡，不讲故事：卡的样式能不能挪到图床，卡里只留 @import。测完删。',
    'language': 'zh', 'containsNSFW': False, 'publicAccess': False, 'isAnonymous': False, 'enableSafeguard': False,
    'prompt': {'systemPrompt': SYS, 'headPrompt': '', 'rearPrompt': '', 'suggestionsPrompt': '', 'lorebook': []},
    'assistantRegexReplace': rules,
    'injectStyles': css,
    'introPage': INTRO,
    'enableMemorySchema': False,
    'options': {'items': [{'order': 0, 'label': '测', 'type': 'SET-INPUT', 'value': '测'}]},
    'cardsTags': [],
    'cardsVoices': [],
}
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', '探针_11-21', '奥尔德兰外链样式探针_11-21.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False, indent=1)
print('写了', out, os.path.getsize(out), '字节；样式格', len(css.encode()), '字节；显示正则', len(rules), '条')
