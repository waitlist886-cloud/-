#!/usr/bin/env python3
# 四纪大框（11-08）：以发布卡（线上那一张，修格式、内框、远讯、成年线、生日都在）为底，并进 v12 的四纪全卷，四纪的大框和图一起进卡。
# 用户 11-08：“以当前的底卡为基底（功能性与bug修复已到位），按照v12新增的内容补全为完整的四纪元大框，世界书到位后着手修改优化主提示词与底层驱动世界书适配四纪元，并安排美术资源入卡”
# 计划和定数见同目录 四纪大框_进卡计划.md。替换对不上就停。
# 用法（仓库根上）：python -I -X utf8 底稿/状态栏/大框/make_four_era_card.py <发布卡.json> <v12卡.json> <输出目录>
#   v12卡：python -I -X utf8 out/进卡_v12/tools/build_v12.py . . <目录> --fast 打的那一张
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
import four_era_prompt as FP      # noqa: E402  主提示词、后置词、驱动条目四纪适配
import four_era_art as FA         # noqa: E402  图床地址、立绘、Boss 图
import preload as PL              # noqa: E402  11-08 底层推演加强：§预载 叫醒下一轮要用的条目
LIMIT = 2097152
OUTNAME = '奥尔德兰_四纪大框.json'


def read(*p):
    return open(os.path.join(*p), encoding='utf-8', newline='').read().replace('\r\n', '\n')


def once(s, a, b, what=''):
    assert s.count(a) == 1, ('对不上', what, s.count(a), a[:70])
    return s.replace(a, b)


pub_p, v12_p, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
P = json.load(open(pub_p, encoding='utf-8'))
V = json.load(open(v12_p, encoding='utf-8'))
S = json.load(open(os.path.join(ROOT, 'src', 'rili_v7.json'), encoding='utf-8'))
card = copy.deepcopy(P)
pr = card['prompt']
sl, pl, vl = S['prompt']['lorebook'], P['prompt']['lorebook'], V['prompt']['lorebook']
NB = len(sl)
assert len(pl) == NB and len(vl) > NB, (len(pl), len(vl))

# ---------------- 世界书 ----------------
lb = copy.deepcopy(vl)
# 1. 触发：发布卡添的词（层级｜X、§评定、§战斗、接档……）接上；两边改触发的条目不重叠
n_trig = 0
for i in range(NB):
    if pl[i]['triggerWords'] != sl[i]['triggerWords']:
        assert vl[i]['triggerWords'] == sl[i]['triggerWords'], ('v12 也改了这一条的触发', i)
        lb[i]['triggerWords'] = copy.deepcopy(pl[i]['triggerWords'])
        n_trig += 1
    # 别的设置发布卡没动过，照 v12（四纪的黑名单在这里）
    assert {k: v for k, v in pl[i].items() if k not in ('content', 'triggerWords')} == {k: v for k, v in sl[i].items() if k not in ('content', 'triggerWords')}, i
# 2. 正文：发布卡整条换过的两条照发布卡；改过几处的六条在 v12（洗过稿）的正文上再改一遍；超程铭刻添第 7 条
lb[5]['content'] = pl[5]['content']
lb[1396]['content'] = pl[1396]['content']
for i, edits in FP.DRIVER_EDITS.items():
    c = lb[i]['content']
    for what, a, b in edits:
        c = once(c, a, b, '#%d %s' % (i, what))
    lb[i]['content'] = c
assert lb[1385]['content'].startswith(HF.INSCRIBE_HEAD), lb[1385]['content'][:30]
lb[1385]['content'] = lb[1385]['content'].rstrip() + HF.INSCRIBE_ADD
# 成年线、生日那几十条 v12 本来就有（洗稿层），核一下
for i in range(NB):
    if pl[i]['content'] != sl[i]['content'] and i not in (5, 1396, 1385) and i not in FP.DRIVER_EDITS:
        if '生于' in pl[i]['content']:
            for m in re.findall(r'生于[^｜\n]{4,30}', pl[i]['content']):
                assert m in lb[i]['content'], ('生日对不上', i, m)
# 3. 四纪适配：驱动条目和四纪常驻
FP.adapt_lore(lb, NB)
# 4. 底层推演加强（11-08）：底卡只扫玩家的世界条目照丙改成两边扫（回复那一侧只认 §预载 那一行），两边扫的大城添一支预载；拿条目名写进预载模拟一遍
n_pre1, n_pre2 = PL.apply(lb, NB)
pre_checked, pre_miss, pre_leak = PL.simulate(lb, NB)
assert not pre_leak, ('预载出岔子', pre_leak[:5])
print('预载：只扫玩家改成两边扫', n_pre1, '条，两边扫的添一支预载', n_pre2, '条；核了', pre_checked, '条，条目名写进预载叫不醒的', len(pre_miss), '条（规则类照甲不动，单子写进 预载叫不醒.txt）')
pr['lorebook'] = lb
print('世界书', len(lb), '条（底卡', NB, '）；发布卡的触发接上', n_trig, '条')

# ---------------- 提示词 ----------------
pr['systemPrompt'] = FP.system(P['prompt']['systemPrompt'])
pr['rearPrompt'] = FP.rear(P['prompt']['rearPrompt'])

# ---------------- 介绍页：v12 的（年表、成年线），发布卡改的八处照套 ----------------
t = V['introPage']
src = read(HERE, 'make_pub_card.py')
blk = src[src.index("t = card['introPage']"):src.index("card['introPage'] = t")]
import ast   # noqa: E402
n_intro = 0
for node in ast.walk(ast.parse(blk)):
    if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'once':
        t = once(t, node.args[1].value, node.args[2].value, '介绍页')
        n_intro += 1
assert n_intro == 8, n_intro
import pc_portrait as PC   # noqa: E402  11-10 主角立绘
card['introPage'] = PC.intro(FP.intro(t))

# ---------------- 显示正则：转换那一组 + 四纪的展开 ----------------
convert = json.loads(read(HERE, 'rules_convert.json'))
frame = json.loads(read(HERE, 'rules_frame.json'))
assert all(P['assistantRegexReplace'][k]['regex'] == convert[k]['regex'] for k in range(len(convert))), '转换那一组跟发布卡的不一样'
rules = []
for r in convert + frame:
    r = dict(r)
    r.pop('name', None)
    rules.append(r)
# 认纪元：日期写歪了、哪一纪都没认出来的，算迷宫纪（发布卡那一条的意思），排在认纪元那几条后头
k = max(i for i, r in enumerate(rules) if '<i class="sz-era era-' in r['replaceString']) + 1
maze = next(r for r in rules if '<i class="sz-era era-maze"' in r['replaceString'])
rules.insert(k, dict(maze, regex='/(<summary class="sz-head">)(?!<i class="sz-era)/',
                     replaceString=re.sub(r' data-y="[^"]*"', ' data-y=""', maze['replaceString'])))
rules = FA.rules(rules)
card['assistantRegexReplace'] = rules
assert len(rules) <= 500, len(rules)

# ---------------- 样式：底卡原来的样式（旧对话要用）＋四纪大框，图走图床 ----------------
st = P['injectStyles']
old = st[:st.index('/* ==== 大框')]
css = FA.css(read(HERE, 'frame.css'))
assert '__ART__' not in css, re.findall(r'__ART__/[^"]*', css)[:5]
# 11-10 清样式：底卡原来那一段里认旧 HTML 状态栏（arc-* 那一套）和介绍页类名的样式，旧回复都经转换那一组变成新的了，用不上，删掉（old_css_trim.py）
import old_css_trim as OT   # noqa: E402
pc_css = '\n'.join(PC.css_lines())
old, n_old, c_old = OT.for_card(old, rules, css + '\n' + pc_css)
print('底卡原来的样式删了 %d 条（%d 字），留 %d 字' % (n_old, c_old, len(old)))
card['injectStyles'] = old.rstrip() + '\n' + css + '\n' + pc_css
assert len(card['injectStyles']) <= LIMIT, len(card['injectStyles'])

# ---------------- 快捷键、更新说明 ----------------
card['options'] = FP.options(P['options'])
card['changelog'] = FP.CHANGELOG + P['changelog']
card['changelog'] = card['changelog'][:2048]

os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir, '预载叫不醒.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('# 底卡两边扫的条目，拿条目名写进一行 §预载 叫不醒的（多半是题目写成一句话的规则条，照方向稿丙不动）\n')
    for i, fd, t in pre_miss:
        f.write('#%d\t%s\t%s\n' % (i, fd, t))
# 底卡触发修订（base_triggers.py，含 name_paren 那七十八条；用户 11-08“一起改”）。v12 打包时已经套过，这里再套一回只是兜底，正常改 0 条
import base_triggers as BT  # noqa: E402
_bt = BT.apply(card['prompt']['lorebook'], NB)
print('底卡触发修订（v12 里已经改过的不算）：「名（」%d 条，深度 1 改 2 的 %d 条，深度 0 改 1 的 %d 条，守住的词 %d 个，防抢话开关 %d 条' % (len(_bt['名（']), len(_bt['深度1改2']), len(_bt['深度0改1']), len(_bt['守住的词']), len(_bt['防抢话开关'])))
# 11-10 照《命定之诗》对照加的功能（features_1110.py）：命运骰、种子、三个开关、几节提示词、存读档两条、菜单。新条目接在世界书末尾
import features_1110 as FT  # noqa: E402
_nf = FT.apply(card, four=True)
card['options'] = PC.options(card['options'])   # 11-10 输入框菜单添「主角立绘」
print('11-10 新功能：新条目 %d 条，菜单 %d 项' % (_nf, len(card['options']['items'])))
# 11-10 基本算式（用户回“甲，其余也都按倾向来”）：通用两条（说话咏唱与动作、价钱怎么算），1001 年的路程和产业挡别纪接上，四纪主要地点添「从这里出发」
import general_entries as GE  # noqa: E402
import route_blocks as RB     # noqa: E402
_g = GE.apply_general(card)
_n1 = GE.apply_1001_new(card)
_rb, _rbm = RB.apply(card['prompt']['lorebook'], NB)
assert not _rbm, ('从这里出发对不上条目', _rbm[:5])
print('11-10 基本算式：通用条目 %d 条，1001 年路程产业 %d 条（同时满足1001年以后的底座），从这里出发 %d 处' % (_g, _n1, _rb))
# 11-10 主线按幕拆（split_acts.py，用户：“主线按幕拆吧”）：一条主线拆成骨架和各段，潮汐格写到哪一段叫醒哪一段，新条目接在末尾。最后一步套，前面按下标找条目的模块不受影响
import split_acts as SA  # noqa: E402
_sa = SA.apply(card['prompt']['lorebook'])
_sp, _ns, _nc = SA.simulate(card['prompt']['lorebook'])
assert not _sp, ('主线按幕拆模拟出岔子', _sp[:5])
assert not _sa['没拆'], ('有主线拆不了', _sa['没拆'])
_mid = sorted(_sa['每轮多半'])[len(_sa['每轮多半']) // 2]
_mid0 = sorted(_sa['每轮原来'])[len(_sa['每轮原来']) // 2]
print('主线按幕拆：%d 条主线，新添段 %d 条（世界书 %d 条）；一轮醒的主线字数中位 %d → %d（骨架加最大一段）；模拟 %d 段 %d 条骨架，问题 0' % (
    _sa['拆了'], _sa['新条目'], len(card['prompt']['lorebook']), _mid0, _mid, _ns, _nc))
path = os.path.join(outdir, OUTNAME)
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False, separators=(',', ':'))
print('ok', path, os.path.getsize(path) // 1024, 'KB；正则', len(rules), '条；样式', len(card['injectStyles']), '字；主提示词', len(pr['systemPrompt']), '字')
