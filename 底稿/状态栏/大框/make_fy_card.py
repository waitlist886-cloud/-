#!/usr/bin/env python3
# 风月导出的底卡换上大框状态栏，提示词、世界书、介绍页、快捷键都同步成日里发布卡那一份（只留一处不搬，见 FY_HEAD）。下面这几处照风月的平台改：
# - 风月的提示词分在 pre_pt 和五条常驻世界书里，照日里主提示词的节切开放回去；触发是一条 RE2 正则（key），不是词表，风月的正则留着，日里多的词接在后面。
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
import make_fy_css  # noqa: E402

ART = os.path.join(HERE, '..', 'comfy', 'out', '四方_11-03', 'art_fu_ab')
OUTNAME = '奥尔德兰_风月底卡_迷宫纪大框.json'
IMAGES = {
    'maze_left': (1400, 80), 'maze_right': (1400, 80), 'maze_top': (None, 84), 'maze_bottom': (3750, 74),
    'items': (None, 66), 'doll': (None, 80),
    'boss_yanzuo1': (None, 62), 'boss_yanzuo2d': (None, 62), 'boss_yanzuo3d': (None, 62),
}
# 跟日里发布卡一样，只留迷宫纪这一纪
DROP = re.compile(r'^(?:月银记号|纷争记号|山铜记号|字眼·|纪元·era-(?:moon|strife|bronze|pre)$|面板·传唱·|面板·战报·|面板·碑·|(?:背包·钱|面板·旅印)·(?:金币|金)$|私产·(?:金币|银币|铜币|金|银|铜)$|敌情·兽档$)')
# 行内 style 里的自定义属性要大写，风月的 react-markdown 才不改坏（--v 会变成 -V）
UPVAR = re.compile(r'(?<![\w-])--(v|m|h|n|a[1-6])(?![\w-])')


def read(*p):
    return open(os.path.join(*p), encoding='utf-8', newline='').read().replace('\r\n', '\n')


def once(s, a, b, what=''):
    assert s.count(a) == 1, ('对不上', what, s.count(a), a[:70])
    return s.replace(a, b)


# 风月保存时扫屏蔽词，命中就自动下架（11-04 客服回的：命中屏蔽词 rili 扣扣）。rili 是字母组合，大小写不论，图片编码里碰巧拼出来的也算。
# 后面三个是别的平台的名字，一直不留。汉字的日里平台不管（用户 11-04 说的），平日里、节日里这种普通词照留
BAN_RE = re.compile('rili|扣扣|日历|风月|fengyue', re.I)


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


# ---- 提示词和世界书：都照日里发布卡（11-04 用户：都照着日历版的来，与日历版同步）。风月的提示词分在 pre_pt 和五条常驻世界书里，照日里主提示词的节切开放回去 ----
sp = pub['prompt']['systemPrompt']
CONST = [(1, '# 统一运行驱动'), (2, '# 输出驱动·骨架（常驻·内部规格）'), (6, '# 单轮协议（承接·口径）'), (7, '# 正文输出档位（常驻·三档）'), (10, '# 名录与固定名词（常驻·只给名字与名词')]
pos = [sp.index(h) for _, h in CONST] + [len(sp)]
assert pos == sorted(pos)
# 日里主提示词开头那一段（叫模型无视安全提示、不限成人描写、声明所有角色都已成年）不搬，卡里有十七岁的旅伴。风月这一段留原来的写法，只同步卡型和不出现规则标签那几句
FY_HEAD = ('# 角色声明\n你是《JRPG日式西幻大世界：奥尔德兰的旅印》的叙事引擎与世界裁定者。卡型：开放世界JRPG＋数值成长＋角色羁绊与感情成长＋队伍冒险＋世界自转，核心是剑与魔法的冒险感。感情线照 JRPG 的写法写，到牵手、拥抱、亲吻为止，不写性描写，不写裸露，不写带性暗示的身体特写。'
           '不用「作为AI」「这只是游戏」一类元叙述；正文里不出现规则、档位表、条目名、【】标签和任何括号批注。你必须完整输出所有内容。')
card['pre_pt'] = FY_HEAD + '\n\n' + sp[sp.index('## 玩家主权与防抢话'):pos[0]].strip()
for k, (i, h) in enumerate(CONST):
    head(i, h.lstrip('# '))
    wb[i]['value'] = sp[pos[k]:pos[k + 1]].strip()
# 风月上分支点不了，玩家照着写或者自己改
wb[2]['value'] = once(wb[2]['value'], '玩家点一下就填进输入框，所以写成他会说的那句话', '玩家照着说或者自己改，所以写成他会说的那句话', '分支')
TAGS = re.compile(r'<div|<details|<span|class=|data-arc|arc-(?:hud|prose|panel|boss|npc|memory|daily|bag|deed)|hud-meta')
for name, t in [('pre_pt', card['pre_pt'])] + [(str(i), wb[i]['value']) for i, _ in CONST]:
    t = t.replace('`<details class="arc-…">`', '')
    assert not TAGS.search(t), ('常驻里还有旧写法', name, TAGS.search(t).group(0))
card['ptx'] = pub['prompt']['headPrompt']
# 比日里多半句：风月库里的旧回复发给模型还是 HTML（日里连发给模型的那一路也转了）
card['posttxt'] = once(pub['prompt']['rearPrompt'], '不许写到一半换回带标签的版面。', '不许写到一半换回带标签的版面，历史里带标签的旧回复也不要照抄。', '后置词')

# 世界书一条对一条：正文跟日里底卡一字不差的直接对上，日里改过名、改过字的四十一条照这张表（风月下标: 日里下标）
RENAMED = {80: 75, 85: 80, 102: 97, 104: 99, 156: 151, 216: 211, 226: 221, 316: 311, 354: 349, 355: 350, 356: 351, 466: 471, 472: 464, 474: 467, 475: 468, 476: 469,
           818: 813, 820: 815, 823: 825, 824: 826, 825: 827, 826: 828, 827: 829, 828: 831, 829: 832, 830: 833, 831: 834, 832: 835, 926: 921, 927: 922, 932: 927,
           1018: 1014, 1021: 1017, 1183: 1179, 1307: 1303, 1316: 1312, 1318: 1314, 1319: 1315, 1320: 1316, 1367: 1363, 1368: 1364}
rili0 = json.load(open(os.path.join(HERE, '..', '..', '..', 'src', 'rili_v7.json'), encoding='utf-8'))['prompt']['lorebook']
lp = pub['prompt']['lorebook']
assert len(rili0) == len(lp)
byc = {}
for j, e in enumerate(rili0):
    byc.setdefault(e['content'], []).append(j)
pairs = dict(RENAMED)
for i, e in enumerate(base['world_bk']):
    if i in pairs or i in dict(CONST):
        continue
    assert byc.get(e['value']), ('对不上日里的条目', i, e['value'][:30])
    pairs[i] = byc[e['value']].pop(0)
extra = sorted(set(range(len(lp))) - set(pairs.values()))
assert extra == [930], extra
RG = {'system': 1, 'user': 2, 'assistant': 4}
RV = {'system': 1, 'headPrompt': 2, 'rearPrompt': 4}
added = 0
for i, j in pairs.items():
    a, b = wb[i], lp[j]
    assert (a['sort'], a['depth'], a['group'], a['enable'], a['probability'], a['key_region'], a['value_region']) == (b['priority'], b['scanDepth'], b.get('folder'), b['enabled'], b['probability'], sum(RG[x] for x in b['triggerRange']), sum(RV[x] for x in b['impactRange'])), (i, j)
    if i in RENAMED:
        # 触发：风月的正则留着，日里的词它认不到的接在后面（日里改名以后新名字旧名字都认，旧档还醒得过来）
        rx = re.compile(a['key'])
        more = [re.escape(w) for w in b['triggerWords'] if not w.startswith('/') and not rx.search(w)]
        if more:
            a['key'] = a['key'] + '|' + '|'.join(more)
            added += 1
        assert len(a['key'].encode('utf-8')) <= 600, (i, len(a['key'].encode('utf-8')), a['key'][:80])
    a['value'] = b['content']
print('改名那几条添触发的', added, '条')

# 认记录行的触发：风月的触发是一条正则，跟日里那几个词一个意思，旧词都留着
head(1400, '功能命令｜格式刷新')
wb[1400]['key'] = wb[1400]['key'] + '|接档|旧档转换'
head(1092, '战斗栏｜普通战斗的敌情卡')
wb[1092]['key'] = '§战斗｜|' + wb[1092]['key']   # arc-battle 留着，旧回复还醒得过来
head(559, '就职、转职与位阶节点')
wb[559]['key'] = '§评定｜(?:就职|转职)评定|' + wb[559]['key']
# 地点锚。旧的回复里地点格写在「地点」或「层级」后头，新的记录 §底座 那一行没有「地点」两个字，地点在钟点后头。§面板｜层级 照旧中
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

# 日里多的一条（纷争纪传奇：辛美尔），风月原来没有。照它的优先级插进那个文件夹
e = lp[930]
assert not e.get('blackListWords') and e['triggerWordsType'] == 'OR'
new_entry = {'group': e['folder'], 'match_type': 3, 'key': '|'.join(re.escape(w) for w in e['triggerWords']), 'key_region': sum(RG[x] for x in e['triggerRange']), 'value_type': 0, 'value': e['content'], 'value_configs': [],
             'value_region': sum(RV[x] for x in e['impactRange']), 'sort': e['priority'], 'depth': e['scanDepth'], 'probability': e['probability'], 'enable': e['enabled']}
wb.insert(next(i for i, x in enumerate(wb) if x['group'] == new_entry['group'] and x['sort'] > new_entry['sort']), new_entry)

# ---- 快捷键：跟日里一样这四个 ----
card['short_cmds'] = [{'label': o['label'], 'command_text': o['value']} for o in pub['options']['items']]

# ---- 介绍页：跟日里发布卡一份 ----
intro = once(pub['introPage'], '<style id="rili-local-icon-compat">', '<style id="local-icon-compat">', '介绍页 样式 id')   # 卡里不留别的平台的名字
intro = once(intro, '衣扣扣到一半', '衣扣系到一半', '介绍页 屏蔽词')
assert 'postMessage' not in intro
card['descr'] = intro

# 日里改名以前的那些名字，正文和介绍页里不留（触发里留着）
OLD = ['修拜因奥古', '洛克哈特', '盖恩斯巴勒', '第七天堂', '神罗', '塔克斯', '扎克斯', '巴雷特', '玛琳', '赞甘', '塞特拉', '伊法娜', '贡加加', '尼布尔', '艾尔米娜', '伟大福音', '大地之息', '七重天', '终极天堂', '破坏剑']
for t in OLD:
    hit = [x['value'][:20] for x in wb if t in x['value']] + [n2 for n2, v in (('pre_pt', card['pre_pt']), ('descr', intro), ('posttxt', card['posttxt'])) if t in v]
    assert not hit, ('还有改名以前的名字', t, hit[:5])

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
    if '.era-moon' in ln or '.era-strife' in ln or '.era-bronze' in ln or '.era-pre' in ln or '.sz-troop' in ln:
        return True
    if re.search(r'\.sz-boss\[data-n\*="(?:焚原|亚蒙|葛摩恩)"\]', ln):
        return True
    return False


frame_css = read(HERE, 'frame.css')
m = re.search(r'header>div:nth-child\(2\)::before\{[^}]*background:(url\("[^"]*"\))', frame_css)
css = make_fy_css.build(frame_css, drop_line, m.group(1))
css = re.sub(r'/\*[\s\S]*?\*/', '', upvar(css))   # 新接的这一段不留注释（样式是公开的，注释只给这里的人看）
total = 0
for name, (wd, q) in IMAGES.items():
    im = Image.open(os.path.join(ART, name + '.webp'))
    if wd and im.width > wd:
        im = im.resize((wd, round(im.height * wd / im.width)), Image.LANCZOS)
    # 图的编码里碰巧拼出屏蔽词就换相邻的质量重新压，直到干净。透明通道排在文件最前面，画面质量动不到它，所以两个一起换
    for dq, da in [(0, 0), (-1, -1), (1, 1), (-2, -2), (2, 2), (-1, 1), (1, -1), (-2, 2), (2, -2), (-3, -3), (3, 3)]:
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=q + dq, method=6, alpha_quality=85 + da)
        b64 = base64.b64encode(buf.getvalue()).decode()
        if not BAN_RE.search(b64):
            break
    else:
        raise SystemExit('图 %s 的编码洗不干净' % name)
    if dq or da:
        print('  图 %s 画面质量 %d 改 %d，透明通道 85 改 %d' % (name, q, q + dq, 85 + da))
    total += buf.tell()
    tag = '__ART__/%s.webp' % name
    assert tag in css, name
    css = css.replace(tag, 'data:image/webp;base64,' + b64)
print('图一共', total // 1024, 'KB')
assert '__ART__' not in css, re.findall(r'__ART__/[^"]*', css)[:5]
card['built_in_css'] = old.rstrip() + '\n' + css

# ---- 核对：字段只动这几个；世界书除了多一条，别的栏（范围、深度、优先级、文件夹）都没动 ----
diff = sorted(k for k in base if base[k] != card[k])
print('改了的字段', diff)
assert diff == ['built_in_css', 'descr', 'posttxt', 'pre_pt', 'ptx', 'regex_rp', 'short_cmds', 'world_bk'], diff
assert list(base.keys()) == list(card.keys())
now = [x for x in wb if x is not new_entry]
assert len(now) == len(base['world_bk'])
body = [i for i, (a, b) in enumerate(zip(base['world_bk'], now)) if a['value'] != b['value']]
keys = [i for i, (a, b) in enumerate(zip(base['world_bk'], now)) if a['key'] != b['key']]
other = [i for i, (a, b) in enumerate(zip(base['world_bk'], now)) if {k: v for k, v in a.items() if k not in ('value', 'key')} != {k: v for k, v in b.items() if k not in ('value', 'key')}]
print('世界书改正文的', len(body), '条，改触发的', len(keys), '条，新添 1 条，别的栏', other)
assert set(body) >= {i for i, _ in CONST} | {9, 11, 560, 837, 1092, 1102, 1390, 1400} and not other
assert len(body) == len(CONST) + 8 + sum(1 for i in RENAMED)
# 正文跟日里发布卡一字不差（常驻和骨架那一句除外）
for i, j in pairs.items():
    assert now[i]['value'] == lp[j]['content'], (i, j)
# 整份文件一个字符一个字符查，图的编码也算
text = json.dumps(card, ensure_ascii=False)
hit = BAN_RE.search(text)
assert not hit, ('卡里还有', text[max(0, hit.start() - 30):hit.end() + 30])
assert '日里' not in re.sub('[一-鿿]日里', '', text), '日里当平台的名字出现了'
os.makedirs(outdir, exist_ok=True)
path = os.path.join(outdir, OUTNAME)
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', path, os.path.getsize(path) // 1024, 'KB', '样式', len(card['built_in_css']), '字（旧样式', len(old), '）', '介绍页', len(intro), '字')
