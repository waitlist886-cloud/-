#!/usr/bin/env python3
# 1001年版切片（11-08）：用户“将新的内容提取制作覆盖风月版与rili版底卡的1001年版切片”。
# 四纪大框那一张（make_four_era_card.py）里属于迷宫纪1001年那一局的新东西，搬回只有1001年的发布卡：
#   - 世界书：底卡 1397 条的正文换成 v12 洗过稿的（成年线、生日、神名、几处设定的补丁都在洗稿层和三路补丁里），末尾「前传的局」那一节切掉；
#     设置照发布卡（v12 给四纪添的年份黑名单不要），v12 添了新名字的八条触发照 v12，发布卡添的触发照发布卡；驱动条目照发布卡那几处再改一遍。
#   - 主提示词、后置词：发布卡的，添 §话 和〔〕、衣着、岁数、在办、不打仗不写战斗栏（four_era_prompt.py 的 1001 那几条），四纪的那几句不进。
#   - 显示正则：转换那一组照旧，展开那一组只留迷宫纪（对话框、名词小卡、衣着、名牌认立绘、空战斗行、身份那一栏放宽都在），四纪字眼那一层拆回迷宫纪的字。
#   - 样式：底卡原来的样式照留，接只有迷宫纪的大框；四方和1001年的六十八位立绘、表情走图床，样式里不放 data:。
#   - 介绍页：v12 的（年表、成年线），发布卡改的八处照套，版本说明添一条人物有了脸。
# 风月版照旧拿这一张当日里发布卡，跑 make_fy_card.py。
# 用法（仓库根上）：python -I -X utf8 底稿/状态栏/大框/make_1001_slice.py <发布卡.json> <v12卡.json> <输出目录>
import ast
import copy
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import history_far as HF          # noqa: E402
import four_era_prompt as FP      # noqa: E402
import four_era_art as FA         # noqa: E402
LIMIT = 2097152
OUTNAME = '奥尔德兰_底卡_迷宫纪大框.json'


def read(*p):
    return open(os.path.join(*p), encoding='utf-8', newline='').read().replace('\r\n', '\n')


def once(s, a, b, what=''):
    assert s.count(a) == 1, ('对不上', what, s.count(a), a[:70])
    return s.replace(a, b)


ERA_SECTIONS = [(r'\n### 前传的局｜', 3), (r'\n## 山铜纪的局', 2)]   # v12 给底卡接的别纪那一节（patch_bronze 的 append、前传凝名那一轮）


def cut_pre(c):
    """切掉「前传的局」「山铜纪的局」那几节（到下一个同级以上的标题为止）。正文里零星一句「纷争纪的局里……」照留，只是条件句"""
    for pat, level in ERA_SECTIONS:
        while True:
            m = re.search(pat, c)
            if not m:
                break
            n = re.search(r'\n#{1,%d} ' % level, c[m.end():])
            end = m.end() + n.start() if n else len(c)
            c = c[:m.start()].rstrip() + c[end:]
    return c.rstrip()


pub_p, v12_p, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
P = json.load(open(pub_p, encoding='utf-8'))
V = json.load(open(v12_p, encoding='utf-8'))
S = json.load(open(os.path.join(ROOT, 'src', 'rili_v7.json'), encoding='utf-8'))
card = copy.deepcopy(P)
pr = card['prompt']
sl, pl, vl = S['prompt']['lorebook'], P['prompt']['lorebook'], V['prompt']['lorebook']
NB = len(sl)
assert len(pl) == NB

# ---------------- 世界书 ----------------
lb = pr['lorebook']
n_cut = n_trig = 0
for i in range(NB):
    c = cut_pre(vl[i]['content'])
    n_cut += c != vl[i]['content']
    lb[i]['content'] = c
    if vl[i]['triggerWords'] != sl[i]['triggerWords']:
        assert pl[i]['triggerWords'] == sl[i]['triggerWords'], ('两边都改了触发', i)
        lb[i]['triggerWords'] = copy.deepcopy(vl[i]['triggerWords'])
        n_trig += 1
lb[5]['content'] = pl[5]['content']
lb[1396]['content'] = pl[1396]['content']
for i, edits in FP.driver_edits(four=False).items():
    c = lb[i]['content']
    for what, a, b in edits:
        c = once(c, a, b, '#%d %s' % (i, what))
    lb[i]['content'] = c
assert lb[1385]['content'].startswith(HF.INSCRIBE_HEAD)
lb[1385]['content'] = lb[1385]['content'].rstrip() + HF.INSCRIBE_ADD
for i in range(NB):
    assert not any(re.search(p, lb[i]['content']) for p, _ in ERA_SECTIONS), ('还有别纪那一节', i)
    if '生于' in pl[i]['content']:
        for m in re.findall(r'生于(?:月银纪|纷争纪|山铜纪|迷宫纪)\d+年[^｜\n]{0,14}', pl[i]['content']):
            assert m in lb[i]['content'], ('生日对不上', i, m)
print('世界书 %d 条：正文换成 v12 洗过稿的，切掉前传的局 %d 条，触发照 v12 的 %d 条' % (NB, n_cut, n_trig))

# ---------------- 提示词 ----------------
pr['systemPrompt'] = FP.system_1001(P['prompt']['systemPrompt'])
pr['rearPrompt'] = FP.rear_1001(P['prompt']['rearPrompt'])

# ---------------- 介绍页 ----------------
t = V['introPage']
src = read(HERE, 'make_pub_card.py')
blk = src[src.index("t = card['introPage']"):src.index("card['introPage'] = t")]
n_intro = 0
for node in ast.walk(ast.parse(blk)):
    if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'once':
        t = once(t, node.args[1].value, node.args[2].value, '介绍页')
        n_intro += 1
assert n_intro == 8, n_intro
import pc_portrait as PC   # noqa: E402  11-10 主角立绘
card['introPage'] = PC.intro(FP.intro_1001(t))

# ---------------- 显示正则：只留迷宫纪 ----------------
DROP = re.compile(r'^(?:月银记号|纷争记号|山铜记号|字眼·|纪元·era-(?:moon|strife|bronze|pre)$|面板·传唱·|面板·战报·|面板·碑·|(?:背包·钱|面板·旅印)·(?:金币|金)$|私产·(?:金币|银币|铜币|金|银|铜)$|敌情·兽档$)')
LW = re.compile(r'<span class="lw"><span class="w0">([^<]*)</span><span class="wm">[^<]*</span><span class="ws">[^<]*</span><span class="wb">[^<]*</span></span>')
convert = json.loads(read(HERE, 'rules_convert.json'))
frame = json.loads(read(HERE, 'rules_frame.json'))
kept, dropped = [], []
for r in frame:
    if DROP.match(r['name']):
        dropped.append(r['name'])
        continue
    r = dict(r)
    if r['name'] == '纪元·era-maze':
        r['regex'] = '/(<summary class="sz-head">)/'      # 这张卡只有一纪，日期写歪了也认它
        r['replaceString'] = re.sub(r' data-y="[^"]*"', '', r['replaceString'])
    r['replaceString'] = LW.sub(r'\1', r['replaceString'])
    assert 'class="lw"' not in r['replaceString'], r['name']
    kept.append(r)
rules = []
for r in convert + kept:
    r = dict(r)
    r.pop('name', None)
    rules.append(r)
card['assistantRegexReplace'] = rules
assert len(rules) <= 500, len(rules)
print('正则 %d 条（转换 %d，展开 %d，丢了别的纪的 %d 条）' % (len(rules), len(convert), len(kept), len(dropped)))

# ---------------- 样式：只留迷宫纪 ----------------
st = P['injectStyles']
old = st[:st.index('/* ==== 大框')]
lines = []
for ln in read(HERE, 'frame.css').split('\n'):
    if re.match(r'^:root:has\(#conversation\)\{--(?:moon|strife|bronze|pre)-', ln):
        continue
    if re.search(r'era-(?:moon|strife|bronze|pre)\b|\.sz-troop|\.lw[>{ ]', ln):
        continue
    if FA.DROP_LINE.search(ln):
        continue
    lines.append(ln)
css = '\n'.join(lines)
for fn, u in FA.URL.items():
    css = css.replace('__ART__/' + fn, u)
left = sorted(set(re.findall(r'__ART__/([^")]+)', css)))
assert not left, ('图床上没有的图', left[:20])
add = ['/* ==== 1001年的立绘和表情（four_era_art.py，只这一纪） ==== */']
roster = json.load(open(os.path.join(HERE, 'roster.json'), encoding='utf-8'))
for k, en in sorted(roster.items(), key=lambda x: (len(x[0]), x[0])):
    add.append('%s %s{%s}' % (FA.R, FA.keysel([k]), FA.por_vals(en)))
_dlog = []
print('真龙原形', FA.dragons_css(add.append, _dlog, eras_ok=['maze']), '头', _dlog)
css = css + '\n' + '\n'.join(add)
card['injectStyles'] = old.rstrip() + '\n' + css + '\n' + '\n'.join(PC.css_lines())
assert 'data:image/webp' not in css and len(card['injectStyles']) <= LIMIT, len(card['injectStyles'])

card['changelog'] = (FP.CHANGELOG_1001 + P['changelog'])[:2048]
# ---- 核对：字段只动这几个 ----
diff = sorted(k for k in P if P[k] != card[k])
assert diff == ['assistantRegexReplace', 'changelog', 'injectStyles', 'introPage', 'prompt'], diff
assert [k for k in P['prompt'] if P['prompt'][k] != pr[k]] == ['systemPrompt', 'rearPrompt', 'lorebook']
for i in range(NB):
    assert {k: v for k, v in lb[i].items() if k not in ('content', 'triggerWords')} == {k: v for k, v in pl[i].items() if k not in ('content', 'triggerWords')}, i
# 底卡触发修订（base_triggers.py，用户 11-08：“先修复底卡，把底卡切片一次性改好”）：「名（」那七十八条（name_paren.py），
# 勾了 AI 回复、深度 1 的改 2，深度 0 的命令改 1，几个常用词守住。上面核对设置跟发布卡一样，所以放在核对以后
import base_triggers as BT  # noqa: E402
_bt = BT.apply(card['prompt']['lorebook'])
print('底卡触发修订：「名（」%d 条，深度 1 改 2 的 %d 条，深度 0 改 1 的 %d 条，守住的词 %d 个，防抢话开关 %d 条' % (len(_bt['名（']), len(_bt['深度1改2']), len(_bt['深度0改1']), len(_bt['守住的词']), len(_bt['防抢话开关'])))
assert (len(_bt['名（']), len(_bt['深度1改2']), len(_bt['深度0改1']), len(_bt['防抢话开关'])) == (78, 488, 11, 1), _bt
# 守住的词：build_v12.py 末尾也套 base_triggers，v12 里已经守过的触发照 v12 拿过来，这里就不再数（11-09 起是 0），改成看结果
assert len(_bt['守住的词']) in (0, 13), _bt['守住的词']
_hd = {}
for _i, _e in enumerate(card['prompt']['lorebook']):
    _hd.setdefault(BT.head_of(_e), []).append(_i)
for _h, _ws in BT.GUARD.items():
    _tw = card['prompt']['lorebook'][_hd[_h][0]]['triggerWords']
    for _w, _n in _ws.items():
        assert _w not in _tw and (_n is None or _n in _tw), ('守住的词没守住', _h, _w, _tw)
# 11-10 照《命定之诗》对照加的功能（features_1110.py）：命运骰、种子、三个开关、几节提示词、存读档两条、菜单。新条目接在底卡后头
import features_1110 as FT  # noqa: E402
_nf = FT.apply(card, four=False)
card['options'] = PC.options(card['options'])   # 11-10 输入框菜单添「主角立绘」
print('11-10 新功能：新条目 %d 条（命运骰、种子、开关），菜单 %d 项' % (_nf, len(card['options']['items'])))
# 11-10 起底卡新条目（仓库根上 底卡新条目/*.md：路程、产业……），只进1001年那一局，接在世界书末尾
import new_base as NB  # noqa: E402
_nb = NB.apply(card, 1397)
print('底卡新条目 %d 条' % _nb)
# 11-12 玩家反馈那一轮（fix_1112.py、mod_page.py）：迷雾、人不围着主角转、好感知情才记和上限、推演的要知做和不在场、远讯、文风、MOD 的扩展页。
# 新条目三份（日用器物、知识变现、领地）在 底卡新条目/，上面 NB.apply 已经收了
import fix_1112 as FX      # noqa: E402
import mod_page as MP      # noqa: E402
_fx = FX.apply(card, four=False)
_mp = MP.apply_rules(card['assistantRegexReplace'])
assert len(card['assistantRegexReplace']) <= 500, len(card['assistantRegexReplace'])
card['injectStyles'] = card['injectStyles'].rstrip() + '\n' + MP.css(MP.L_PUB, MP.R_PUB) + '\n'
assert MP.L_PUB + ':has(.t-news input:checked) .p-news{display:block}' in card['injectStyles'], '扩展页的样式前缀跟这一张对不上'
assert len(card['injectStyles']) <= LIMIT, len(card['injectStyles'])
print('11-12 修复：世界书改 %d 处，显示规则添 %d 改 %d' % ((_fx,) + _mp))
os.makedirs(outdir, exist_ok=True)
path = os.path.join(outdir, OUTNAME)
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', path, os.path.getsize(path) // 1024, 'KB；样式', len(card['injectStyles']), '字（旧样式', len(old), '）；主提示词', len(pr['systemPrompt']), '字')
