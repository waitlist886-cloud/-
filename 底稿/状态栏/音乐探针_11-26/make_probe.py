#!/usr/bin/env python3
# 11-26 音乐探针：聊天里放背景音乐（每轮 AI 在底座里挑一首，显示正则变成播放器）以前，先探平台留不留得住播放器、响不响、叠不叠、重不重放。
# 出两张卡，日里一张、风月一张，规则和样式同一套：
#   AI 每轮头一行写  §底座｜曲 X｜位 P｜测N｜轮 R   末一行写  §曲尾｜曲 X｜位 P｜测N｜轮 R
#   X 甲乙丙（玩家说平常、战斗、羁绊），P 首或尾（播放器放在回复开头还是末尾），N 零到七（八种写法），R 第几轮。
#   位 首 时头一行变成播放器，位 尾 时末一行变成播放器，另一行只印一行灰字。末一行前头另插一块折着的“体检”，报平台留下了哪些标签和属性。
#   每个播放器上印着它是哪一种写法、第几轮，还有一盏状态灯（浏览器认 :playing 才亮）和这一种写的属性留没留下。
# 测试音在图床 bgm_probe 分支（push_bgm.py 推的，清单 bgm_manifest.json）。
# 用法（仓库根上）：python -I -X utf8 底稿/状态栏/音乐探针_11-26/make_probe.py
import copy
import json
import os
import shutil
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, 'out', '探针_音乐_11-26')
man = json.load(open(os.path.join(HERE, 'bgm_manifest.json'), encoding='utf-8'))
MIR = man['mirrors']
U = lambda f, m='cdn': MIR[m] + f

TRACKS = [('甲', 'bgm_a.mp3', '低音长鸣', '平常'), ('乙', 'bgm_b.mp3', '鼓点', '战斗'), ('丙', 'bgm_c.mp3', '三音琶音', '羁绊')]
POS = {'首': '放在回复开头', '尾': '放在回复末尾'}

# 每一种写法：说明、播放器本体（照曲目地址生成）、要核的属性（标签, 选择器）
A, S, AU, LP, CT = ('audio', 'audio'), ('src', ':is(audio,video,source,embed)[src]'), ('autoplay', '[autoplay]'), ('loop', '[loop]'), ('controls', '[controls]')
BOX = lambda u, auto: ('<div class="music-player-standalone"><div class="music-info"><span class="music-icon">🎶</span><span class="music-title">__T__</span></div>'
                       '<audio class="audio-control" src="%s" controls loop preload="metadata" playsinline controlslist="nodownload"%s></audio></div>') % (u, ' autoplay' if auto else '')
MODES = [
    ('一', 'audio 自动播放·循环·看不见（没有控件）',
     lambda f: '<audio src="%s" autoplay loop preload="auto"></audio>' % U(f), [A, S, AU, LP]),
    ('二', '照“西幻音乐盒”原样：audio 控件·循环·手点才放',
     lambda f: BOX(U(f), False), [A, S, CT, LP, ('preload', '[preload]'), ('playsinline', '[playsinline]'), ('controlslist', '[controlslist]')]),
    ('三', '“西幻音乐盒”那一版加 autoplay：控件·自动播放·循环',
     lambda f: BOX(U(f), True), [A, S, CT, AU, LP, ('playsinline', '[playsinline]')]),
    ('四', 'video 只放声：控件·自动播放·循环',
     lambda f: '<video src="%s" autoplay loop playsinline controls preload="auto"></video>' % U(f), [('video', 'video'), S, AU, LP, CT]),
    ('五', 'audio 控件·自动播放·循环，里头四个 source 镜像兜底',
     lambda f: '<audio controls autoplay loop playsinline preload="auto">%s</audio>' % ''.join(
         '<source src="%s" type="audio/mpeg">' % U(f, m) for m in ('fastly', 'testingcf', 'gcore', 'cdn')),
     [A, ('source', 'audio > source[src]'), AU, LP, CT]),
    ('六', '♪ 钮：data-action audio-once，手点放一次',
     lambda f: '<span class="bgmp-btn" data-action="audio-once" data-value="%s">♪ 点这里放一次</span>' % U(f), [('data-action', '[data-action="audio-once"]')]),
    ('七', 'embed、object、iframe srcdoc 三样（自动播放）',
     lambda f: ('<div class="bgmp-sub">embed：<embed src="%s" type="audio/mpeg" width="320" height="44"></div>'
                '<div class="bgmp-sub">object：<object data="%s" type="audio/mpeg" width="320" height="44"></object></div>'
                '<div class="bgmp-sub">iframe srcdoc：<iframe width="340" height="64" srcdoc="&lt;audio src=&quot;%s&quot; autoplay loop controls&gt;&lt;/audio&gt;"></iframe></div>') % (U(f), U(f), U(f)),
     [('embed', 'embed'), ('object', 'object'), ('iframe', 'iframe'), ('srcdoc', 'iframe[srcdoc]')]),
]
NUMS = '零一二三四五六七'

GREEN, RED = '#2a7a4a', '#b03030'
css = ['.bgmp,.bgmk,.bgml{font:13px/1.65 system-ui,"PingFang SC","Microsoft YaHei",sans-serif}',
       '.bgmp{margin:10px 0;padding:10px 12px;border:2px solid #4a7bd0;border-radius:10px;background:#eef3fb;color:#1a2233}',
       '.bgmp-h{margin-bottom:6px}.bgmp-h b{color:#1d4f9e}',
       '.bgmp audio,.bgmp video{display:block;width:100%;max-width:440px;margin:6px 0}.bgmp video{height:56px;background:#222;border-radius:6px}',
       '.bgmp .music-player-standalone{padding:6px 8px;border:1px dashed #8aa6d6;border-radius:8px;background:#fff}.bgmp .music-icon{margin-right:6px}',
       '.bgmp-sub{margin:4px 0}',
       '.bgmp-btn{display:inline-block;padding:6px 16px;border-radius:16px;background:#c9a45c;color:#1a1408;cursor:pointer;font-weight:700;user-select:none}',
       '.bgml{margin:6px 0;padding:3px 10px;border-left:3px solid #999;color:#555;background:#f1f1f1;font-size:12px}',
       '.kk{display:inline-block;margin-right:12px;font-size:12px}',
       '.bgmp-st{margin-left:8px;font-weight:700}',
       '.bgmp-st::after{content:"（状态灯不亮：这个浏览器不认，靠耳朵）";color:#888;font-weight:400}',
       '.bgmp:has(:paused) .bgmp-st::after{content:"■ 停着";color:%s;font-weight:700}' % RED,
       '.bgmp:has(:playing) .bgmp-st::after{content:"▶ 在响";color:%s;font-weight:700}' % GREEN,
       '.bgmk{margin:8px 0;padding:6px 10px;border:1px dashed #999;border-radius:8px;background:#fafafa;color:#222}',
       '.bgmk summary{cursor:pointer;font-weight:700}.bgmk .r{margin:1px 0}.bgmk .r i{font-style:normal;font-weight:700}',
       '.bgmk .r i::after{content:"✗ 没了";color:%s}' % RED]
for i, (n, desc, body, keys) in enumerate(MODES, 1):
    for k, (lab, sel) in enumerate(keys):
        css.append('.bgmp.m%d .k%d::after{content:"%s ✗";color:%s}' % (i, k, lab, RED))
        css.append('.bgmp.m%d:has(%s) .k%d::after{content:"%s ✓";color:%s}' % (i, sel, k, lab, GREEN))

# 体检：一行一样，标签或属性留下了就变绿
CHECK = [('r1', 'audio 标签', 'audio.t1'), ('r2', 'audio 的 src', 'audio.t1[src]'), ('r3', 'audio 的 loop', 'audio.t1[loop]'),
         ('r4', 'audio 的 controls', 'audio.t1[controls]'), ('r5', 'audio 的 preload', 'audio.t1[preload]'),
         ('r6', 'audio 的 playsinline', 'audio.t1[playsinline]'), ('r7', 'audio 的 controlslist', 'audio.t1[controlslist]'),
         ('r8', 'audio 的 autoplay', 'audio.t2[autoplay]'), ('r9', 'audio 的 muted（日里是 React 只设属性值，这一格在日里看不准）', 'audio.t3[muted]'),
         ('r10', 'video 标签', 'video.t4'), ('r11', 'audio 里的 source', 'audio.t5 > source[src]'),
         ('r12', 'embed', 'embed'), ('r13', 'object', 'object'), ('r14', 'iframe', 'iframe'), ('r15', 'iframe 的 srcdoc', 'iframe[srcdoc]'),
         ('r16', 'data-action', '[data-action="audio-once"]'), ('r17', 'img 的 onerror（行内脚本属性）', 'img[onerror]')]
for r, lab, sel in CHECK:
    css.append('.bgmk:has(%s) .%s i::after{content:"✓ 留下了";color:%s}' % (sel, r, GREEN))
css.append('.bgmk.js-ran .r18 i::after{content:"✓ 跑了";color:%s}' % GREEN)
css.append('.bgmk.js-ran2 .r19 i::after{content:"✓ 跑了";color:%s}' % GREEN)
CSS = '\n'.join(css) + '\n'

nope = U('nope.png')  # 图床上没有这个文件，取不到就会触发 onerror
TIJIAN = ('<details class="bgmk"><summary>体检：平台留下了哪些标签和属性（点开看，截图发回）</summary>'
          + ''.join('<div class="r %s">%s：<i></i></div>' % (r, lab) for r, lab, _ in CHECK)
          + '<div class="r r18">行内脚本属性跑没跑（img onerror）：<i></i></div><div class="r r19">script 标签跑没跑：<i></i></div>'
          + '<div class="r r20">回复里的 style 标签：<i></i></div>'
          + '<audio class="t1" src="%s" loop controls playsinline controlslist="nodownload" preload="none" hidden></audio>' % U('bgm_a.mp3')
          + '<audio class="t2" autoplay hidden></audio><audio class="t3" muted hidden></audio><video class="t4" hidden></video>'
          + '<audio class="t5" preload="none" hidden><source src="%s" type="audio/mpeg"></audio>' % U('bgm_a.mp3')
          + '<embed class="t6" type="text/plain" hidden><object class="t7" hidden></object><iframe class="t8" hidden srcdoc="&lt;b&gt;x&lt;/b&gt;"></iframe>'
          + '<span hidden data-action="audio-once" data-value="x"></span>'
          + '<img hidden alt="" src="%s" onerror="this.closest(\'details\').classList.add(\'js-ran\')">' % nope
          + '<script>document.querySelectorAll(".bgmk").forEach(function(e){e.classList.add("js-ran2")})</script>'
          + '<style>.bgmk .r20 i::after{content:"✓ 生效了"!important;color:%s!important}</style>' % GREEN
          + '</details>')

SP = r'\s*'
def line(tag, x, p, n):
    return r'(^|\n)§%s｜%s曲%s%s%s｜%s位%s%s%s｜%s测%s%s%s｜%s轮%s(\d{1,3})[^\n]*' % (tag, SP, SP, x, SP, SP, SP, p, SP, SP, SP, n, SP, SP, SP)

RULES = []  # (标题, 正则, 替换)
RULES.append(('体检', r'\n(?=§曲尾｜)', '\n' + TIJIAN + '\n\n'))
for i, (n, desc, body, keys) in enumerate(MODES, 1):
    for x, f, nm, _ in TRACKS:
        for p, tag in (('首', '底座'), ('尾', '曲尾')):
            head = ('<div class="bgmp m%d"><div class="bgmp-h"><b>【测%s】%s</b>｜%s｜曲 %s·%s｜第 $2 轮<span class="bgmp-st"></span></div>'
                    % (i, n, desc, POS[p], x, nm))
            kk = '<div class="bgmp-k">' + ''.join('<span class="kk k%d"></span>' % k for k in range(len(keys))) + '</div>'
            rep = '$1' + head + body(f).replace('__T__', '曲 %s·%s' % (x, nm)) + kk + '</div>\n'
            RULES.append(('测%s·%s·%s' % (n, x, p), line(tag, x, p, n), rep))
RULES.append(('底座·灰字', r'(^|\n)§底座｜([^\n]{0,120})', '$1<div class="bgml">底座这一行：$2</div>\n'))
RULES.append(('曲尾·灰字', r'(^|\n)§曲尾｜([^\n]{0,120})', '$1<div class="bgml">曲尾这一行：$2</div>\n'))

SYS = '''这是测平台用的小卡，不讲故事，也不扮演谁。每一轮只照下面的格式输出，不多不少。

第一行：§底座｜曲 X｜位 P｜测N｜轮 R
中间：写一段五百字上下的平常景物描写，分五六段（一间旅店的屋子、窗外的街、天气、炉火，随便写，每轮换点东西，不写对白，不写人名）。
最后一行：§曲尾｜曲 X｜位 P｜测N｜轮 R

X 是 甲、乙、丙 之一：玩家的话里有“平常”写甲，有“战斗”写乙，有“羁绊”写丙；都没有就照上一轮，头一轮写甲。
N 是 零、一、二、三、四、五、六、七 之一：玩家打“测一”就写一，打“测五”就写五，以此类推；没打就照上一轮，头一轮写零。
P 是 首 或 尾：玩家的话里有“尾”写尾，有“首”写首；都没有就照上一轮，头一轮写首。
R 是这是第几轮回复，从 1 数起，每轮加一。

两行的样子一字不差照抄，用全角竖线｜，测和N之间不空格，例如：
§底座｜曲 乙｜位 首｜测三｜轮 4
§曲尾｜曲 乙｜位 首｜测三｜轮 4
第一行和最后一行的内容完全一样，只有开头的 §底座 和 §曲尾 不同。除了这两行和中间的描写，什么都不写。'''
REAR = '提醒：第一行 §底座｜曲 X｜位 P｜测N｜轮 R，最后一行 §曲尾｜曲 X｜位 P｜测N｜轮 R，中间五百字上下景物描写。照玩家这一句换 X、P、N，没说的照上一轮。'
CHIPS = ['测零', '测一', '测二', '测三', '测四', '测五', '测六', '测七', '平常', '战斗', '羁绊', '首', '尾']

INTRO = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:18px;font:15px/1.8 system-ui,sans-serif;background:#16181d;color:#e8e4da">
<h2 style="margin:0 0 10px">音乐探针 11-26（%s）</h2>
<p>这张卡不讲故事，只测聊天里放不放得了背景音乐。照 <b>测法.md</b> 一步一步打，听到什么记进表里。测完删掉。</p>
<p>三段测试音各 20 秒，开头都有一声高音“叮”：甲＝低音长鸣，乙＝咚咚的鼓点，丙＝叮叮叮三个音一组。听到“叮”就是从头放了。</p>
<p>每一轮打一句，比如「测一」「测三 战斗」「测五 尾 羁绊」。没说的照上一轮。</p>
<p>先把电脑音量调小一点。</p>
%s
</body></html>'''
RILI_BTN = '''<button style="margin-top:12px;padding:10px 18px;font-size:15px;border-radius:8px;border:0;background:#c9a45c;color:#1a1408"
 onclick="window.parent.postMessage({type:'rili-set-input', value:'测零'},'*')">填入「测零」</button>'''


def rili_card():
    rules = [{'enabled': True, 'applyMode': 'front-end', 'messageRole': 'assistant', 'regex': '/%s/g' % rx, 'replaceString': rep}
             for _, rx, rep in RULES]
    return {
        'title': '奥尔德兰音乐探针_11-26',
        'description': '测平台用的小卡，不讲故事：聊天里的回复能不能放背景音乐（audio、video、按钮几种写法）。照测法一步一步打。测完删。',
        'language': 'zh', 'containsNSFW': False, 'publicAccess': False, 'isAnonymous': False, 'enableSafeguard': False,
        'prompt': {'systemPrompt': SYS, 'headPrompt': '', 'rearPrompt': REAR, 'suggestionsPrompt': '', 'lorebook': []},
        'assistantRegexReplace': rules,
        'injectStyles': CSS,
        'introPage': INTRO % ('日里', RILI_BTN),
        'enableMemorySchema': False,
        'options': {'items': [{'order': k, 'label': c, 'type': 'SET-INPUT', 'value': c} for k, c in enumerate(CHIPS)]},
        'cardsTags': [],
        'cardsVoices': [],
    }


def fy_card():
    base = json.load(open(os.path.join(ROOT, 'out', '风月探针_11-23', '探针底_小底卡.json'), encoding='utf-8'))
    c = copy.deepcopy(base)
    c['name'] = '【探针】风月：聊天里放背景音乐'
    c['abstract'] = '平台探针，不能玩。测回复里的 audio、video、按钮几种写法留不留得住、响不响、叠不叠、重不重放。照 测法.md 一步一步打。'
    c['descr'] = INTRO % ('风月', '')
    c['pre_pt'] = SYS
    c['posttxt'] = REAR
    c['ptx'] = ''
    c['built_in_css'] = CSS
    c['regex_rp'] = [{'title': '音乐探针·' + t, 'match_regex': rx, 'replace_text': rep, 'scope': 1, 'is_enable': True, 'is_only_render': True}
                     for t, rx, rep in RULES]
    c['world_bk'] = [{'group': '探针', 'match_type': 3, 'key': 'ⓧ音乐探针永不触发', 'key_region': 2, 'value_type': 0, 'value': '（空）',
                      'value_configs': [], 'value_region': 1, 'sort': 1, 'depth': 1, 'probability': 100, 'enable': False}]
    c['short_cmds'] = [{'label': x, 'command_text': x} for x in CHIPS]
    c['preset_chats'] = []
    c['suggest_q'] = []
    return c


os.makedirs(OUT, exist_ok=True)
for name, card in (('奥尔德兰音乐探针_日里_11-26.json', rili_card()), ('奥尔德兰音乐探针_风月_11-26.json', fy_card())):
    p = os.path.join(OUT, name)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(card, f, ensure_ascii=False, indent=1)
    print('写了', name, '%.1f KB' % (os.path.getsize(p) / 1024), '正则', len(card.get('assistantRegexReplace') or card.get('regex_rp')), '条')
shutil.copyfile(os.path.join(HERE, '测法.md'), os.path.join(OUT, '测法.md'))
with zipfile.ZipFile(os.path.join(OUT, '音乐探针_11-26.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for n in ('奥尔德兰音乐探针_日里_11-26.json', '奥尔德兰音乐探针_风月_11-26.json', '测法.md'):
        z.write(os.path.join(OUT, n), n)
print('zip 好了')
# 给复刻台用的样本（一种写法一条，首尾各一）
SMP = os.path.join(HERE, '样本')
os.makedirs(SMP, exist_ok=True)
body = '\n\n'.join(['炉火还亮着，窗外的雨收了一半。'] * 3)
for i, (n, *_ ) in enumerate([('零',)] + [(m[0],) for m in MODES]):
    for k, (x, p) in enumerate((('甲', '首'), ('乙', '尾'))):
        tagline = '曲 %s｜位 %s｜测%s｜轮 %d' % (x, p, n, i * 2 + k + 1)
        with open(os.path.join(SMP, '测%s_%s.txt' % (n, p)), 'w', encoding='utf-8', newline='\n') as f:
            f.write('§底座｜%s\n%s\n§曲尾｜%s\n' % (tagline, body, tagline))
print('样本', len(os.listdir(SMP)), '条')
