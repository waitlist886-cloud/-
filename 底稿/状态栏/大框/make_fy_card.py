#!/usr/bin/env python3
# 风月导出的底卡换上大框状态栏，介绍页同步成日里发布卡那一份。记法、提示词的改法跟日里发布卡（make_pub_card.py）一样，下面这几处照风月的平台改：
# - 风月的提示词分在 pre_pt 和五条常驻世界书里，改的地方落在各条；触发是一条 RE2 正则（key），不是词表。
# - 正则脚本（regex_rp）只认 g 一个标记：m 标记换成前后顾，只换第一处的规则在后面接一段吃到尾巴。
# - 历史消息只走「仅渲染」的规则，新生成的回复存库前走不带「仅渲染」的规则：旧回复转记录这一组放两份，一份管存库（新回复写混了也存成记录），一份管显示（库里的旧回复）。
# - 消息里的 <style> 被平台拿掉，行内 style 的小写自定义属性被改坏，这两样见 make_fy_css.py。分支点了填不进输入框（平台没有这个动作），规则不带 data-action。
# 用法（仓库根上）：python -I -X utf8 底稿/状态栏/大框/make_fy_card.py <风月导出.json> <日里发布卡.json> <输出目录>   要 PIL
import base64
import copy
import io
import json
import os
import re
import sys

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fy_names  # noqa: E402
import make_fy_css  # noqa: E402

PUB = os.path.join(HERE, '发布')
ART = os.path.join(HERE, '..', 'comfy', 'out', '四方_11-03', 'art_fu_ab')
OUTNAME = '奥尔德兰_风月底卡_迷宫纪大框.json'
IMAGES = {
    'maze_left': (1400, 80), 'maze_right': (1400, 80), 'maze_top': (None, 84), 'maze_bottom': (3750, 74),
    'items': (None, 66), 'doll': (None, 80),
    'boss_yanzuo1': (None, 62), 'boss_yanzuo2d': (None, 62), 'boss_yanzuo3d': (None, 62),
}
# 跟日里发布卡一样，只留迷宫纪这一纪
DROP = re.compile(r'^(?:月银记号|纷争记号|字眼·|纪元·era-(?:moon|strife|bronze|pre)$|面板·传唱·|面板·战报·|(?:背包·钱|面板·旅印)·(?:金币|金)$|私产·(?:金币|银币|铜币|金|银|铜)$|敌情·兽档$)')
# 行内 style 里的自定义属性要大写，风月的 react-markdown 才不改坏（--v 会变成 -V）
UPVAR = re.compile(r'(?<![\w-])--(v|m|h|n|a[1-6])(?![\w-])')


def read(*p):
    return open(os.path.join(*p), encoding='utf-8', newline='').read().replace('\r\n', '\n')


def once(s, a, b, what=''):
    assert s.count(a) == 1, ('对不上', what, s.count(a), a[:70])
    return s.replace(a, b)


def upvar(s):
    return UPVAR.sub(lambda m: '--' + m.group(1).upper(), s)


# ---- 规则：日里的 /pat/flags 换成风月只认 g 的写法 ----
def scan(p):
    """一个一个字走：出 (字, 在字符类里, 被转义)"""
    i, in_cls = 0, False
    while i < len(p):
        c = p[i]
        if c == '\\':
            yield i, p[i:i + 2], in_cls, True
            i += 2
            continue
        if in_cls:
            if c == ']':
                in_cls = False
        elif c == '[':
            in_cls = True
            yield i, c, False, False
            i += 1
            continue
        yield i, c, in_cls, False
        i += 1


def groups(p):
    n = 0
    for i, c, cls, esc in scan(p):
        if c == '(' and not cls and not esc:
            if p[i + 1:i + 2] != '?' or p[i + 1:i + 3] == '?<' and p[i + 3:i + 4] not in ('=', '!'):
                n += 1
    return n


def no_m(p):
    out, last = [], 0
    for i, c, cls, esc in scan(p):
        if cls or esc:
            continue
        if c == '^':
            out += [p[last:i], r'(?<![^\n])']
            last = i + 1
        elif c == '$':
            out += [p[last:i], r'(?![^\n])']
            last = i + 1
    out.append(p[last:])
    return ''.join(out)


def port(r, render_only):
    m = re.match(r'^/([\s\S]*)/([^/]*)$', r['regex'])
    assert m, r['regex'][:60]
    pat, flags = m.group(1), m.group(2)
    assert set(flags) <= set('gm'), flags
    rep = r['replaceString']
    if 'm' in flags:
        pat = no_m(pat)
    if 'g' not in flags:
        # 只换第一处：从字符串头懒惰地找到第一处，尾巴接在后面。头上锚死，g 也只会中这一回（一段能匹配空的规则在末尾不会再中一回）
        n = groups(pat)
        assert n + 2 < 100, (r['name'], n)
        rep = re.sub(r'\$(\d{1,2})', lambda x: '$%d' % (int(x.group(1)) + 1) if 1 <= int(x.group(1)) <= n else x.group(0), rep)
        pat = '^([\\s\\S]*?)(?:' + pat + ')([\\s\\S]*)$'
        rep = '$1' + rep + '$%d' % (n + 2)
    return {'title': r['name'], 'match_regex': pat, 'replace_text': rep, 'scope': 1, 'is_enable': True, 'is_only_render': render_only}


src, pubcard, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
base = json.load(open(src, encoding='utf-8'))
pub = json.load(open(pubcard, encoding='utf-8'))
card = copy.deepcopy(base)
wb = card['world_bk']


def head(i, want):
    assert wb[i]['value'].lstrip('# ').startswith(want), (i, wb[i]['value'][:40])


# ---- 提示词：pre_pt 和常驻五条 ----
card['pre_pt'] = once(card['pre_pt'], '每条写成 `<div class="f mem"><b>类别</b>内容</div>`，顺序：修正→短期→未结因果→长期→核心，最后一行是已完成（`f done`）；空类写一行「无」。',
                      '每条写成一行 `§记忆｜类别｜内容`，顺序：修正→短期→未结因果→长期→核心，最后是已完成（`§记忆｜已完成｜…`，一件一行）；空类写一行 `§记忆｜类别｜无`。', '记忆区')
head(1, '统一运行驱动')
wb[1]['value'] = once(wb[1]['value'], '「体态数据」照抄进 look 行', '「体态数据」照抄进容貌行', '容貌行')
head(2, '输出驱动·骨架')
skeleton = fy_names.apply(read(PUB, '骨架.md').strip())
# 风月上分支点不了，玩家照着写或者自己改
skeleton = once(skeleton, '玩家点一下就填进输入框，所以写成他会说的那句话', '玩家照着说或者自己改，所以写成他会说的那句话', '分支')
wb[2]['value'] = skeleton
head(6, '单轮协议')
v = wb[6]['value']
v = once(v, '卡序、类名、行数与骨架不符｜缺卡（⑥成长与伟业最容易漏：默认折叠、几乎不变，也照写九行；角色卡第二部分同理）｜',
         '写了 HTML 标签或代码围栏｜名目、次序、栏序与骨架不符｜缺行（⑥成长与伟业、⑦背包、⑧角色第二部分最容易漏：几乎不变，也每轮照写）｜', '失败输出')
v = once(v, '战斗栏位置错、正文容器内留空行｜', '战斗栏位置错｜', '失败输出')
v = once(v, '折叠与展开写反｜', '', '失败输出')
v = once(v, '六维或队友属性行不用 ats 跨度｜', '六维或队友属性行写法不对｜', '失败输出')
wb[6]['value'] = v
head(7, '正文输出档位')
wb[7]['value'] = once(wb[7]['value'], '当前档位写在推演底座摘要行 `hud-meta` 那一段（`… · 防抢话 开 · 档位 很长`），不占环境格，之后每轮以它为准：',
                      '当前档位写在 §底座 那一行（`… · 防抢话 开 · 档位 很长`），之后每轮以它为准：', '档位')
head(10, '名录与固定名词')
v = wb[10]['value']
v = once(v, '面板 class 对应 `yj-novice`(见习)／`yj-campfire`(营火)／`yj-windroad`(风路)／`yj-laurel`(月桂)／`yj-worldkey`(界钥)／`yj-starchart`(星图)／`yj-hymn`(圣歌)／`yj-deep`(深印)／`yj-war`(战印)；无印写 `yj-none`。', '', '旅印')
v = once(v, '本人登场时写进 `data-arc-portrait`）', '本人登场时写进 §角色 的 `立绘:短名`）', '短名')
wb[10]['value'] = v
TAGS = re.compile(r'<div|<details|<span|class=|data-arc|arc-(?:hud|prose|panel|boss|npc|memory|daily|bag|deed)|hud-meta')
for name, t in [('pre_pt', card['pre_pt'])] + [(str(i), wb[i]['value']) for i in (1, 2, 6, 7, 10)]:
    t = t.replace('`<details class="arc-…">`', '')
    assert not TAGS.search(t), ('常驻里还有旧写法', name, TAGS.search(t).group(0))
card['posttxt'] = ('只写纯文本记录，不写任何 HTML 标签和代码围栏（存档的代码块除外）。从第一行到最后一行都是记录，§面板、§装备、§能力、§伟业、§物品、§背包、§角色、§见闻、§记忆 也一样，不许写到一半换回带标签的版面，历史里带标签的旧回复也不要照抄。第一个字是 §底座：日期·HH:MM·地点·潮汐·防抢话·档位，时间以分钟记账，接 §环境 和 §推演九行。'
                   '除正文段落外一行一条记录，栏用全角｜分开，名目和栏序照骨架。次序：底座、环境、推演、正文、分支、战斗栏或史诗战、面板、装备、能力、伟业、物品、背包、角色、见闻、记忆，每轮写全，没变的照抄。'
                   '记忆先数上一轮短期条数再落笔，7条压长期。正文段与段之间空一行，分支在正文之后。界面不入戏，角色只知自己所见所闻。主角面板禁写「未知」「同上」。')

# ---- 世界书正文 ----
head(9, '输出模板·完整版')
wb[9]['value'] = fy_names.apply(read(PUB, '条目_输出模板.md').strip())

head(1400, '功能命令｜格式刷新')
wb[1400]['value'] = fy_names.apply(read(PUB, '条目_格式刷新.md').strip())
wb[1400]['key'] = wb[1400]['key'] + '|接档|旧档转换'

head(1092, '战斗栏｜普通战斗的敌情卡')
c = wb[1092]['value']
i, j = c.index('普通战斗（不是楼层主'), c.index('- **LVL**')
c = c[:i] + ('普通战斗（不是楼层主、不是史诗战）从开战那一轮出到战斗结束那一轮，紧跟在 §分支 之后、§面板 之前；结束那轮把敌人标成已倒下/已逃/投降，下一轮起不再出。Boss 轮改出史诗战卡，两张不同时出。\n\n'
             '头一行：`§战斗｜遭遇名｜交战中`\n\n'
             '每类敌人一行（同类合写，倒下或逃走的写"已倒下×n""已逃×n"），其后固定弱点、注意两行：\n'
             '`§敌情｜敌名 ×数量｜LVL n｜轻伤·70｜动摇·40｜相当｜此刻在做什么`\n'
             '`§战况｜弱点｜已查明的弱点；确实没人知道的写"未识别"`\n'
             '`§战况｜注意｜前摇、特殊能力、增援、地形、要护住的人、撤退线`\n\n') + c[j:]
c = once(c, '架势 稳固/动摇/濒破/已破；条宽用骨架档位。', '架势 稳固/动摇/濒破/已破；点后头的数只是条的长度（0 到 100），玩家看见的是字和条。', '战斗栏')
wb[1092]['value'] = c
wb[1092]['key'] = '§战斗｜|' + wb[1092]['key']   # arc-battle 留着，旧回复还醒得过来

head(1102, '史诗Boss战统一引擎')
c = wb[1102]['value']
c = once(c, '使用：\n`<div class="arc-boss-intro"><span class="arc-boss-kicker">BOSS ENCOUNTER</span><b>Boss正式名号</b><small>阶段与战场</small></div>`',
         '开战那一轮在史诗战卡最前头写一行：\n`§首领｜Boss正式名号｜阶段与战场`', '史诗 入场')
c = once(c, 'Boss战期间，在正文后、冒险者面板前输出`<details class="arc-boss-panel" open>`，显示：',
         'Boss战期间，紧跟在 §分支 之后、§面板 之前写这几行（一类一行，这一类没有就不写）：\n'
         '`§史诗｜Boss名号｜阶段 II/III｜阶段名｜LVL n｜战场`\n'
         '`§史诗势｜动摇·70｜濒破·35`（势条状态·条长，架势状态·条长；状态写 完整/动摇/崩解/濒危、稳固/动摇/濒破/已破，点后头的数只是条的长度）\n'
         '`§史诗况｜已识别｜…`，`§史诗况｜未破解｜…`，`§史诗况｜场地｜…`，`§史诗况｜保护｜…`，`§史诗况｜撤退｜…`，`§史诗况｜协战｜…`\n'
         '`§史诗况｜圣歌｜乐章《名》｜线：〇之〇〇【〇〇】｜人声：无／有｜我方：…｜它：…`\n'
         '`§史诗况｜庇护｜首次复活庇护可用或已用`\n'
         '这几行要显示：', '史诗 八')
wb[1102]['value'] = c

head(560, '就职评定｜装置读的是什么')
c = wb[560]['value']
c = once(c, '`<div class="f d"><b>就职评定</b>谁：名｜', '`§评定｜就职评定｜谁：名｜', '就职')
c = once(c, '｜查谱：职业谱·命路名、职业谱·流派名｜阶段：评定</div>`', '｜查谱：职业谱·命路名、职业谱·流派名｜阶段：评定`', '就职')
c = once(c, '转职写 `<b>转职评定</b>`，节点写', '转职写 `§评定｜转职评定｜…`，节点写', '就职')
wb[560]['value'] = c

head(559, '就职、转职与位阶节点')
wb[559]['key'] = '§评定｜(?:就职|转职)评定|' + wb[559]['key']

head(837, '双子协战｜路西艾拉与莉安娜')
wb[837]['value'] = once(wb[837]['value'], '状态栏卡写 `data-arc-portrait="路西艾拉"` / `data-arc-portrait="莉安娜"`（短名「路西」「莉安」同样可用）',
                        '§角色 末栏写 `立绘:路西艾拉` / `立绘:莉安娜`（短名「路西」「莉安」同样可用）', '双子')

head(11, '承接跨版本迁移凭证')
c = wb[11]['value']
c = once(c, '## 五、首轮怎么输出\n1. 先输出一行', '## 五、首轮怎么输出\n照骨架从 §底座 写起，下面 1 到 4 都写在 §正文 底下，5 写成 §分支。\n1. 先输出一行', '迁移')
c = once(c, '成长与伟业九行／队友卡两部分（七行＋折叠四行）', '成长与伟业各行／队友卡两部分（七行＋四行）', '迁移')
wb[11]['value'] = c

head(1390, '完整存档协议')
c = wb[1390]['value']
c = once(c, '**纯文本，一个代码块，整份存档都在里面。不出 HTML 面板。**存档是拿去复制粘贴的东西；带标签的版面在代码块里只会变成源码。',
         '**§底座、§环境、§功能 三行写在最前头，空一行，下面一个代码块，整份存档都在代码块里。不出面板。**存档是拿去复制粘贴的东西；代码块里照下面的字段写，不写 § 开头的记录。', '存档')
c = once(c, '成长与伟业九行', '成长与伟业各行', '存档')
wb[1390]['value'] = c

# 触发：地点锚。旧的回复里地点格写在「地点」或「层级」后头，新的记录 §底座 那一行没有「地点」两个字，地点在钟点后头。§面板｜层级 照旧中
PLACE_OLD = '(?:地点|层级)[\\s\\S]{0,24}'
PLACE_NEW = '(?:地点|层级|:\\d\\d[^·\\n]{0,12}·)[\\s\\S]{0,24}'
n = 0
for e in wb:
    if PLACE_OLD in e['key'] and e['key_region'] & 4:
        k = e['key'].replace(PLACE_OLD, PLACE_NEW)
        assert len(k.encode('utf-8')) <= 600, (len(k.encode('utf-8')), k[:80])
        e['key'] = k
        n += 1
print('地点触发添了', n, '条')
head(13, '防抢话开关')
wb[13]['key'] = wb[13]['key'] + '|防抢话 关'   # 旧的环境格写 防抢话</b>…关，记录写在 §底座 那一行

# ---- 快捷键：平台上限十个（编辑器「已达到最大数量限制（10个）」），旧档转换顶掉读取迁移凭证（手打【读取迁移凭证】、贴迁移凭证照旧认）----
cmds = card['short_cmds']
assert len(cmds) == 10 and cmds[8]['label'] == '读取迁移凭证', cmds[8]
cmds[8] = {'label': '旧档转换', 'command_text': '【旧档转换】'}

# ---- 介绍页：跟日里发布卡一份。日里版改过名的那几位，字面换回风月世界书里的名字 ----
intro = fy_names.apply(pub['introPage'])
for bad in ['塞弗林', '黑袖', '科伦德', '多兰', '洛蒂', '冷杉村', '晚灯', '井鼠', '走根', '望火台', '诺薇', '满园春', '经年一息', '七重拍', '梅多斯', '坦纳', '留灯之章', '桑托', '葛蕾塔', '伯格', '藤溪村']:
    assert bad not in intro, ('介绍页还有日里版的名字', bad)
    assert not any(bad in wb[i]['value'] for i in (2, 9, 1400)), ('骨架还有日里版的名字', bad)
for bad in ['postMessage', 'rilichat', 'rili-set-input', '风月']:
    assert bad not in intro, bad
card['descr'] = intro

# ---- 规则 ----
convert = json.loads(read(HERE, 'rules_convert.json'))
frame = json.loads(read(HERE, 'rules_frame.json'))
kept = []
for r in frame:
    if DROP.match(r['name']):
        continue
    if r['name'] == '纪元·era-maze':
        r['regex'] = '/(<summary class="sz-head">)/'     # 这张卡只有一纪，日期写歪了也认它
        r['replaceString'] = '$1<i class="sz-era era-maze"></i>'
    elif r['name'] == '钟点':
        r['replaceString'] = '$1<i class="sz-hh" data-h="$2"></i>'
    elif r['name'] == '分支·可点':
        r['replaceString'] = once(r['replaceString'], ' data-action="set-textinput" data-value="$1"', '', '分支')
    assert '<style' not in r['replaceString'] and 'data-action' not in r['replaceString'], r['name']
    r['regex'] = upvar(r['regex'])
    r['replaceString'] = upvar(r['replaceString'])
    kept.append(r)
TAG_OK = set('a abbr address area article aside audio b base bdi bdo blockquote body br button canvas caption cite code col colgroup data datalist dd del details dfn dialog div dl dt em embed fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 head header hgroup hr html i iframe img input ins kbd label legend li link main map mark meta meter nav noscript object ol optgroup option output p param picture pre progress q rp rt ruby s samp script section select slot small source span strong style sub summary sup table tbody td template textarea tfoot th thead time title tr track u ul var video wbr'.split())
STRIP = set('script iframe object embed applet link meta base html head body form style'.split())
for r in kept:
    for t in re.findall(r'</?([a-zA-Z][\w-]*)', r['replaceString']):
        assert t.lower() in TAG_OK and t.lower() not in STRIP, ('平台认不得或者会拿掉的标签', t, r['name'])
rules = [port(dict(r, name='存·' + r['name']), False) for r in convert] + \
        [port(dict(r, name='显·' + r['name']), True) for r in convert] + \
        [port(r, True) for r in kept]
card['regex_rp'] = rules
for r in rules:
    re.compile(r['match_regex'].replace('(?<![^\\n])', '(?<![^\n])'))   # 这里只查括号配不配
print('规则', len(rules), '条（存库', len(convert), '，显示', len(convert), '+', len(kept), '），一共', sum(len(r['match_regex']) + len(r['replace_text']) for r in rules), '字')

# ---- 样式：现卡样式留着，大框接在后面 ----
old = base['built_in_css']
n = old.count('details:not([open])>summary')
old = old.replace('details:not([open])>summary', 'details:not([open],.sz-hud)>summary')
old = once(old, 'details>summary::after{content:"▾"', 'details:not(.sz-hud)>summary::after{content:"▾"', '旧样式')
print('旧样式 details 规则改了', n + 1, '处')


def drop_line(ln):
    if re.match(r'^:root:has\(#conversation\)\{--(?:moon|strife|bronze|pre)-', ln):
        return True
    if '.era-moon' in ln or '.era-strife' in ln or '.era-bronze' in ln or '.era-pre' in ln:
        return True
    if re.search(r'\.sz-boss\[data-n\*="(?:焚原|亚蒙)"\]', ln):
        return True
    return False


frame_css = read(HERE, 'frame.css')
m = re.search(r'header>div:nth-child\(2\)::before\{[^}]*background:(url\("[^"]*"\))', frame_css)
css = make_fy_css.build(frame_css, drop_line, m.group(1))
css = upvar(css)
total = 0
for name, (wd, q) in IMAGES.items():
    im = Image.open(os.path.join(ART, name + '.webp'))
    if wd and im.width > wd:
        im = im.resize((wd, round(im.height * wd / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=q, method=6, alpha_quality=85)
    total += buf.tell()
    tag = '__ART__/%s.webp' % name
    assert tag in css, name
    css = css.replace(tag, 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode())
print('图一共', total // 1024, 'KB')
assert '__ART__' not in css, re.findall(r'__ART__/[^"]*', css)[:5]
card['built_in_css'] = old.rstrip() + '\n' + css

# ---- 核对：字段只动这几个，世界书只动这几条 ----
diff = sorted(k for k in base if base[k] != card[k])
print('改了的字段', diff)
assert diff == ['built_in_css', 'descr', 'posttxt', 'pre_pt', 'regex_rp', 'short_cmds', 'world_bk'], diff
assert list(base.keys()) == list(card.keys())
body = [i for i, (a, b) in enumerate(zip(base['world_bk'], wb)) if a['value'] != b['value']]
keys = [i for i, (a, b) in enumerate(zip(base['world_bk'], wb)) if a['key'] != b['key']]
other = [i for i, (a, b) in enumerate(zip(base['world_bk'], wb)) if {k: v for k, v in a.items() if k not in ('value', 'key')} != {k: v for k, v in b.items() if k not in ('value', 'key')}]
print('世界书改正文的', body, '改触发的', len(keys), '条', '别的栏', other)
assert body == [1, 2, 6, 7, 9, 10, 11, 560, 837, 1092, 1102, 1390, 1400], body
assert not other and len(wb) == len(base['world_bk'])
os.makedirs(outdir, exist_ok=True)
path = os.path.join(outdir, OUTNAME)
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', path, os.path.getsize(path) // 1024, 'KB', '样式', len(card['built_in_css']), '字（旧样式', len(old), '）', '介绍页', len(intro), '字')
