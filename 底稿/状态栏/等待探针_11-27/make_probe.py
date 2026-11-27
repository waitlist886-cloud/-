#!/usr/bin/env python3
# 11-27 等待探针（日里）：发出一句以后、模型出字以前那几秒，日里页面上到底挂了什么（占位格、思考过程、转圈、停止钮）。
# 卡里没有脚本，只能靠样式看：
#   一、透视：最后两行消息（玩家那一条和 AI 正在生成的那一条）、虚拟列表外头的东西、输入栏，每个元素描一道粉框，
#       头上印一行小字「‹标签#id .类名 状态属性›」。截图就看得出结构。
#   二、检查板：页面右上角钉一块黑底小板，十几样东西认不认得到（✓／✗），等待、思考、出字、完了各截一张。
#   三、试样：最后一行里回复本体还是空的时候，在里头印一行金字“命运的丝线正在编织（试样）”，看这个选择器在等待时认不认得到。
# 用法（仓库根上）：python -I -X utf8 底稿/状态栏/等待探针_11-27/make_probe.py
import json
import os
import shutil
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, 'out', '探针_等待_11-27')

ROW = '#conversation [style*="contain: layout"]'
L = ROW + ':last-child'                      # 最新一行
L2 = ROW + ':nth-last-child(-n+2)'            # 最新两行
OUTSIDE = ['#conversation [style*="contain: size"] ~ *', '#conversation ~ *']  # 虚拟列表外头、输入栏

TAGS = ['div', 'span', 'p', 'button', 'details', 'summary', 'section', 'article', 'ul', 'ol', 'li', 'pre', 'code',
        'label', 'form', 'a', 'i', 'b', 'em', 'strong', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'header', 'footer', 'aside']
SKIP = ':not(.rili-markdown-renderer p, .rili-markdown-renderer p *, .xr, .xr *)'

css = []
# 一、透视
LAB = ('{content:"‹%s#" attr(id) " ." attr(class) " " attr(data-state) attr(data-status) attr(aria-busy) attr(role) attr(aria-label) "›";'
       'display:inline;font:9px/1.25 ui-monospace,Consolas,monospace;color:#ff3fae;background:rgba(0,0,0,.72);'
       'padding:0 2px;margin:0 2px 0 0;word-break:break-all;white-space:normal;letter-spacing:0;text-transform:none;'
       'position:static;width:auto;height:auto;opacity:1;visibility:visible;transform:none;border:0;border-radius:0}')
# 第四版：满屏透视在手机上读不了（窄的格子里字竖着排），拿掉。只标几处、标签整行横排：
#   AI 那一格（.is-assistant）描金框；它底下前三层的每个元素（气泡、space-y-3、renderer 和它的兄弟）各印一行；
#   renderer 里头的直接孩子印一行短的（看思考过程是不是写在正文里，比如 blockquote、details）；
#   整页凡是类名带 think、reason、load、animate- 的，描红框印一行，一闪的那一下截得到就看得出是谁。
BLK = ('{content:"%s" attr(class) " " attr(data-state) attr(data-status) attr(role) attr(aria-label);'
       'display:block;font:10px/1.3 ui-monospace,Consolas,monospace;color:%s;background:rgba(0,0,0,.8);'
       'padding:1px 4px;margin:0 0 2px;word-break:break-all;white-space:normal;letter-spacing:0;text-transform:none;'
       'position:static;width:auto;max-width:100%%;height:auto;opacity:1;visibility:visible;transform:none;border:0;border-radius:3px;'
       'writing-mode:horizontal-tb;flex:none;align-self:stretch;min-height:0}')
AI = '#conversation .is-assistant'
css.append(AI + '{outline:2px solid #e9c56a!important;outline-offset:2px}')
css.append(AI + '::before' + BLK % ('AI格 .', '#e9c56a'))
css.append(AI + ' > *::before' + BLK % ('┗1 .', '#ffb3de'))
css.append(AI + ' > * > *::before' + BLK % ('　┗2 .', '#ffb3de'))
css.append(AI + ' > * > * > *:not(.rili-markdown-renderer *)::before' + BLK % ('　　┗3 .', '#ffb3de'))
css.append(AI + ' .rili-markdown-renderer > :not(p,.xr)::before' + BLK % ('　　　正文里的块 .', '#9fe0ff'))
# 第五版：等待那几秒 AI 气泡里冒出来的、不是 renderer 的那一块（11-27 录屏里出现过两秒多），单独标橙色，往下两层也标
W = '#conversation .is-assistant .space-y-3 > :not(.rili-markdown-renderer)'
css.append(W + '{outline:3px solid #ff9a3c!important;outline-offset:1px}')
css.append(W + '::before' + BLK % ('★等待块 .', '#ffb36b'))
css.append(W + ' > *::before' + BLK % ('　★┗ .', '#ffb36b'))
css.append(W + ' > * > *::before' + BLK % ('　　★┗ .', '#ffb36b'))
HOT = ','.join('#conversation [class*="%s" i]' % k for k in ('think', 'reason', 'load', 'animate-', 'spin', 'typing', 'pulse'))
css.append(':is(%s){outline:2px solid #ff4d4d!important;outline-offset:1px}' % HOT)
css.append(':is(%s)::after' % HOT + BLK % ('◆ 带动画或思考类名 .', '#ff8080'))

# 二、检查板
CHECKS = [
    ('页上有虚拟列表的行 contain: layout', ROW),
    ('页上有带 contain 的元素', '#conversation [style*="contain"]'),
    ('页上有 .is-assistant', '#conversation .is-assistant'),
    ('页上有 .is-user', '#conversation .is-user'),
    ('页上有 renderer', '#conversation .rili-markdown-renderer'),
    ('页上有空的 renderer', '#conversation .rili-markdown-renderer:empty'),
    ('页上有探针正文（第几轮那一行）', '#conversation .xr'),
    ('AI 气泡里有 renderer 以外的东西', '#conversation .is-assistant .space-y-3 > :not(.rili-markdown-renderer)'),
    ('AI 正文里有 blockquote', '#conversation .is-assistant .rili-markdown-renderer > blockquote'),
    ('AI 正文里有 details', '#conversation .is-assistant .rili-markdown-renderer details'),
    ('页上有类名带 load 的', '#conversation [class*="load" i]'),
    ('最后一行有 .is-assistant', L + ' .is-assistant'),
    ('最后一行有 .is-user', L + ' .is-user'),
    ('最后一行有回复本体 renderer', L + ' .rili-markdown-renderer'),
    ('回复本体是空的 :empty', L + ' .rili-markdown-renderer:empty'),
    ('回复本体里有段落 p', L + ' .rili-markdown-renderer p'),
    ('探针正文已到（第几轮那一行）', L + ' .xr'),
    ('最后一行有 think/reason/thought 类', ','.join(L + ' [class*="%s" i]' % k for k in ('think', 'reason', 'thought'))),
    ('最后一行有 details 折叠块', L + ' details'),
    ('最后一行有 animate- 动画类', L + ' [class*="animate-"]'),
    ('最后一行有 load/spin/dot/typing/stream 类', ','.join(L + ' [class*="%s" i]' % k for k in
                                                     ('load', 'spin', 'skeleton', 'typing', 'dot', 'pending', 'stream', 'generat', 'cursor', 'blink', 'pulse'))),
    ('最后一行有 data-state/status/aria-busy', ','.join(L + ' %s' % k for k in ('[data-state]', '[data-status]', '[aria-busy="true"]'))),
    ('最后一行有 svg', L + ' svg'),
    ('列表外头挂了东西', OUTSIDE[0]),
    ('整页有 think/reason 类', ','.join('#conversation [class*="%s" i]' % k for k in ('think', 'reason', 'thought'))),
    ('整页有 animate- 动画类', '#conversation [class*="animate-"]'),
    ('输入栏有 stop 类', '#conversation ~ * [class*="stop" i]'),
    ('输入栏有 animate- 动画类', '#conversation ~ * [class*="animate-"]'),
    ('输入栏按钮 disabled', '#conversation ~ * button:disabled'),
    ('输入框 disabled', '#conversation ~ * textarea:disabled'),
]
# 11-27 用户刚输入那一下“animate- 动画类”打过勾，细分是哪一种、在哪儿
for k in ('pulse', 'spin', 'bounce', 'ping', 'in', 'out'):
    CHECKS.append(('对话区 animate-%s' % k, '#conversation [class*="animate-%s"]' % k))
    CHECKS.append(('输入栏 animate-%s' % k, '#conversation ~ * [class*="animate-%s"]' % k))
# 第三版：只列认得到的（✓）几行，认不到的不占地方；手机上缩成左上角一小块
css.append(':root:has(#conversation){%s}' % ';'.join('--wp%d:""' % i for i in range(len(CHECKS))))
for i, (lab, sel) in enumerate(CHECKS):
    css.append(':root:has(#conversation):has(%s){--wp%d:"✓ %s\\A"}' % (sel, i, lab))
body = ' '.join('var(--wp%d)' % i for i in range(len(CHECKS)))
css.append(':root:has(#conversation)::after{content:"探针五·认得到的：\\A" %s;position:fixed;top:72px;right:8px;z-index:2147483000;'
           'white-space:pre;font:11px/1.45 system-ui,"PingFang SC","Microsoft YaHei",sans-serif;color:#f4f0e6;'
           'background:rgba(0,0,0,.78);border:1px solid #c9a45c;border-radius:8px;padding:5px 8px;pointer-events:none;max-width:60vw;max-height:60vh;overflow:hidden}' % body)
css.append('@media (max-width:639px){:root:has(#conversation)::after{top:52px;right:auto;left:4px;font-size:9px;line-height:1.3;padding:2px 5px;'
           'max-width:58vw;max-height:45vh;background:rgba(0,0,0,.6)}}')

# 三、试样
css.append('%s .rili-markdown-renderer:empty::before{content:"✦ 命运的丝线正在编织（试样：空回复认得到）";display:block;'
           'color:#e9c56a;font:14px/1.8 serif;letter-spacing:.12em;outline:none}' % L)
css.append('%s .is-assistant::after{content:"［试样：AI 行认得到］";display:block;color:#7fd1a8;font:10px/1.4 system-ui}' % L)
css.append('.xr{margin:4px 0 10px;padding:3px 10px;border-left:3px solid #c9a45c;color:#c9a45c;font:12px/1.6 system-ui}')
CSS = '\n'.join(css) + '\n'

RX = r'(^|\n)§探针｜\s*轮\s*(\d{1,3})[^\n]*'
REP = '$1<div class="xr">等待探针·第 $2 轮（这一行到了，就是正文开始出字了）</div>\n'

SYS = '''这是测平台用的小卡，不讲故事，也不扮演谁。

每一轮回答以前，先认真想一会儿：把这一轮要写的那间屋子、窗外、天气、炉火、桌上的东西五样，一样一样在心里排好、换着写法试一遍，再动笔。会思考的模型就多想一阵。

然后只照下面的格式输出，不多不少：
第一行：§探针｜轮 R
后面：一段八百字上下的平常景物描写，分七八段（一间旅店的屋子、窗外的街、天气、炉火，每轮换点东西，不写对白，不写人名）。

R 是这是第几轮回复，从 1 数起，每轮加一。第一行用全角竖线｜，一字不差照抄，例如：
§探针｜轮 3'''
REAR = '提醒：先想一会儿再写。第一行 §探针｜轮 R，后面八百字上下景物描写。'
CHIPS = ['开始', '再来一轮', '短一点']

INTRO = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:18px;font:15px/1.8 system-ui,sans-serif;background:#16181d;color:#e8e4da">
<h2 style="margin:0 0 10px">等待探针 11-27（日里）</h2>
<p>这张卡不讲故事，只看发出一句以后、模型出字以前那几秒，页面上挂了什么。照 <b>测法.md</b> 打，截图发回。测完删掉。</p>
<p>模型挑一个会思考的（带思考过程的那种），这样等待那一段长一点。</p>
<button style="margin-top:12px;padding:10px 18px;font-size:15px;border-radius:8px;border:0;background:#c9a45c;color:#1a1408"
 onclick="window.parent.postMessage({type:'rili-set-input', value:'开始'},'*')">填入「开始」</button>
</body></html>'''


def card():
    return {
        'title': '奥尔德兰等待探针_11-27',
        'description': '测平台用的小卡，不讲故事：发出一句以后、模型出字以前，页面上挂了什么。照测法打，截图发回。测完删。',
        'language': 'zh', 'containsNSFW': False, 'publicAccess': False, 'isAnonymous': False, 'enableSafeguard': False,
        'prompt': {'systemPrompt': SYS, 'headPrompt': '', 'rearPrompt': REAR, 'suggestionsPrompt': '', 'lorebook': []},
        'assistantRegexReplace': [{'enabled': True, 'applyMode': 'front-end', 'messageRole': 'assistant', 'regex': '/%s/g' % RX, 'replaceString': REP}],
        'injectStyles': CSS,
        'introPage': INTRO,
        'enableMemorySchema': False,
        'options': {'items': [{'order': k, 'label': c, 'type': 'SET-INPUT', 'value': c} for k, c in enumerate(CHIPS)]},
        'cardsTags': [],
        'cardsVoices': [],
    }


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    name = '奥尔德兰等待探针_日里_11-27.json'
    p = os.path.join(OUT, name)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(card(), f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, 'probe.css'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(CSS)
    print('写了', name, '%.1f KB' % (os.path.getsize(p) / 1024), '样式 %d 字' % len(CSS), '检查 %d 样' % len(CHECKS))
    shutil.copyfile(os.path.join(HERE, '测法.md'), os.path.join(OUT, '测法.md'))
    with zipfile.ZipFile(os.path.join(OUT, '等待探针_日里_11-27.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for n in (name, '测法.md'):
            z.write(os.path.join(OUT, n), n)
    print('zip 好了')
