# 11-25 兜底那一轮的体检：照 make_four_era_card.py 的次序把卡里的显示正则拼出来（不打卡），造一张歪法单，交给 check_兜底.mjs 试。
#   python -I -X utf8 底稿/状态栏/大框/第三轮/兜底_体检.py [临时目录] [改前的 rules_frame.json]
# 拼法：rules_convert.json 里“稳”那四十三条 + rules_frame.json + 认不出纪元算迷宫纪那一条 + mod_page 的五条（卡里末尾另有 css_cdn 插样式的一条，这里不带）。
# 给了改前的 rules_frame.json（比如 git show HEAD:… 存出来的一份），再比一遍现成的样本改前改后展开出来差在哪。
# 歪法单：判、家业、宠 各几十种写歪的（行首记号、竖线、包着、栏数、名目写错），一种一行，换进 样本_四样同屏.txt 里头一条那种记录的位置；
#   expect 是展开以后该有的数（整张面板原来四张、家业卡七张、宠卡两张）。名目写错的（§判定、§魔宠、§势力）和 §【判】 照旧由 mod_page 收进扩展页，不算错。
import io
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
sys.path.insert(0, UP)
sys.dont_write_bytecode = True
TMP = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix='doudi_')
os.makedirs(TMP, exist_ok=True)


def card_rules(frame_path, out_path):
    import importlib
    convert = json.load(io.open(os.path.join(UP, 'rules_convert.json'), encoding='utf-8'))
    frame = json.load(io.open(frame_path, encoding='utf-8'))
    rules = [dict(r) for r in convert if not (r.get('name') or '').startswith('转')] + [dict(r) for r in frame]
    k = max(i for i, r in enumerate(rules) if '<i class="sz-era era-' in r['replaceString']) + 1
    maze = next(r for r in rules if '<i class="sz-era era-maze"' in r['replaceString'])
    rules.insert(k, dict(maze, name='纪元·认不出算迷宫纪', regex='/(<summary class="sz-head">)(?!<i class="sz-era)/', replaceString=re.sub(r' data-y="[^"]*"', ' data-y=""', maze['replaceString'])))
    MP = importlib.import_module('mod_page')
    MP.apply_rules(rules)
    json.dump(rules, io.open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return len(rules)


def probes():
    L = io.open(os.path.join(HERE, '样本_四样同屏.txt'), encoding='utf-8').read().replace('\r', '').split('\n')
    J = [l for l in L if l.startswith('§判｜')]
    ES = [l for l in L if l.startswith('§家业｜')]
    E, P = ES[0], next(l for l in L if l.startswith('§宠｜'))
    J, J2 = J[0], J[1]
    half = lambda s: s.replace('｜', '|')
    c = J.split('｜')          # §判、类·事、出手方、出手方几项、应对方、应对方几项、定档、骰、结果、后果
    BT = '`'
    F3 = BT * 3
    out = []

    def add(kind, name, lines, note='', **expect):
        out.append({'kind': kind, 'name': kind + '·' + name, 'lines': lines if isinstance(lines, list) else [lines], 'expect': expect, 'note': note})

    FULL = dict(整张=4, 简版=0, 判落兜底=0, 剩半角竖线=0, 剩反引号=0, 剩记号=0, MOD卡=0)
    SIMPLE = dict(整张=3, 简版=1, 判落兜底=0, 剩半角竖线=0, 剩反引号=0, 剩记号=0, MOD卡=0)
    ROW = dict(整张=3, 简版=0, 判落兜底=1, 剩记号=0)
    MOD = dict(MOD卡=1, 剩记号=0)
    add('判', '原样', J, **FULL)
    # 竖线
    add('判', '半角竖线', half(J), **FULL)
    add('判', '半角竖线带空格', J.replace('｜', ' | '), **FULL)
    add('判', '名目后全角里头半角', '§判｜' + half(J[3:]), **FULL)
    add('判', '混着写', '｜'.join(c[:4]) + '|' + '|'.join(c[4:7]) + '｜' + '｜'.join(c[7:]), **FULL)
    add('判', '竖线写成丨', J.replace('｜', '丨'), **FULL)
    add('判', '全角竖线两边带空格', J.replace('｜', ' ｜ '), **FULL)
    # 行首记号
    add('判', '漏了行首记号', J[1:], **FULL)
    add('判', '漏了行首记号又半角', half(J[1:]), **FULL)
    for mk in ['＃', '#', '$', '＄', '※', '§§', '¶', '◆', '▶', '·', '§ ', '§　']:
        add('判', '行首写成' + mk.replace(' ', '空格').replace('　', '全角空格'), mk + J[1:], **FULL)
    add('判', '名目带方括号', '【判】' + J[2:], **FULL)
    add('判', '名目带方括号后头没竖线', '【判】' + J[3:], **FULL)
    add('判', '名目带半角方括号半角竖线', '[判]' + half(J[2:]), **FULL)
    add('判', '名目带方括号和记号', '§【判】' + J[2:], '转换那一组先把它当成认不出的记录收进了扩展页', **MOD)
    add('判', '名目后头冒号', '§判：' + J[3:], **FULL)
    add('判', '漏记号名目后头冒号', '判：' + J[3:], **FULL)
    add('判', '列表号', '- ' + J, **FULL)
    add('判', '引用号', '> ' + J, **FULL)
    add('判', '列表号又漏记号', '- ' + J[1:], **FULL)
    add('判', '整行加粗', '**' + J + '**', **FULL)
    add('判', '行首空格', '  ' + J, **FULL)
    # 包着
    add('判', '行内反引号', BT + J + BT, **FULL)
    add('判', '行内三反引号', F3 + J + F3, **FULL)
    add('判', '代码围栏', [F3, J, F3], **FULL)
    add('判', '代码围栏带语言', [F3 + 'text', J, F3], **FULL)
    add('判', '波浪围栏', ['~~~', J, '~~~'], **FULL)
    add('判', '围栏里两行', [F3, J, J2.replace('交涉·劝', '交涉·再劝'), F3], 整张=5, 简版=0, 判落兜底=0, 剩反引号=0, 剩记号=0)
    add('判', '围栏加半角加漏记号', [F3, half(J[1:]), F3], **FULL)
    add('判', '引用号加反引号', '> ' + BT + J + BT, **FULL)
    add('判', '中文引号', '“' + J + '”', **FULL)
    add('判', '直角引号', '「' + J + '」', **FULL)
    add('判', '直引号', '"' + J + '"', **FULL)
    add('判', '单引号', "'" + J + "'", **FULL)
    add('判', '圆括号', '（' + J + '）', **FULL)
    add('判', '方括号包整行', '【' + J + '】', **FULL)
    add('判', '引号包着半角竖线', '“' + half(J) + '”', **FULL)
    add('判', '后果里自己带引号', J + '，她喊了一声“退”', **FULL)
    add('判', '引号包着且后果末尾带引号', '“' + J + '，她喊了一声“退””', **FULL)
    add('判', '末尾多一个竖线', J + '｜', **FULL)
    add('判', '末尾多一个半角竖线', half(J) + '|', **FULL)
    add('判', '表格式两头竖线', '|' + half(J) + '|', **FULL)
    add('判', '行尾空格句号', J + '。 ', **FULL)
    # 栏数
    add('判', '少应对方几项九栏', '｜'.join(c[:5] + c[6:]), **SIMPLE)
    add('判', '少两边几项八栏', '｜'.join(c[:3] + [c[4]] + c[6:]), **SIMPLE)
    add('判', '只有事和尾巴六栏', '｜'.join(c[:2] + c[6:]), **SIMPLE)
    add('判', '少类事那一栏', '｜'.join([c[0]] + c[2:]), **SIMPLE)
    add('判', '少骰那一栏', '｜'.join(c[:7] + c[8:]), '照常出整张，当没掷骰', **FULL)
    add('判', '少后果那一栏', '｜'.join(c[:9]), '照常出整张，底下不出那一句', **FULL)
    add('判', '少骰又少后果', '｜'.join(c[:7] + c[8:9]), **FULL)
    add('判', '少结果那一栏', '｜'.join(c[:8] + c[9:]), '出简版，不出绶带', **SIMPLE)
    add('判', '多一栏在末尾', J + '｜备注：这一下很要紧', '出简版，多出来的并进后果', **SIMPLE)
    add('判', '多一栏在中间', '｜'.join(c[:6] + ['环境 枪阵封路'] + c[6:]), **SIMPLE)
    add('判', '位阶另占一栏十二栏', '｜'.join([c[0], c[1], '洛恩·维斯特', '共鸣·凝华 LVL 38', c[3], '骸骨枪卫', '共鸣·圆满 LVL 34'] + c[5:]), **SIMPLE)
    add('判', '简版少骰那一栏', '｜'.join(c[:2] + [c[6]] + c[8:]), **SIMPLE)
    add('判', '少定档那一栏', '｜'.join(c[:6] + c[7:]), '定档认不出，照旧原样一行', **ROW)
    add('判', '定档写了别的词', '｜'.join(c[:6] + ['还行'] + c[7:]), '照旧原样一行', **ROW)
    add('判', '只写了半截', '｜'.join(c[:4]), '照旧原样一行（流式写到一半也是这样）', **ROW)
    add('判', '写到定档为止', '｜'.join(c[:7]), '流式写到这里还是原样一行，不先闪一张简版', **ROW)
    add('判', '写到骰为止', '｜'.join(c[:8]), '同上', **ROW)
    add('判', '名目写成判定', '§判定' + J[2:], '收进扩展页', **MOD)
    add('判', '名目写成检定', '§检定' + J[2:], '收进扩展页', **MOD)

    EST = dict(家业卡=7, 没类的卡=0, 剩半角竖线=0, 剩反引号=0, 剩记号=0, MOD卡=0)
    add('家业', '原样', E, **EST)
    add('家业', '半角竖线', half(E), **EST)
    add('家业', '半角竖线带空格', E.replace('｜', ' | '), **EST)
    add('家业', '漏了行首记号', E[1:], **EST)
    add('家业', '漏了行首记号又半角', half(E[1:]), **EST)
    for mk in ['＃', '#', '※', '§§']:
        add('家业', '行首写成' + mk, mk + E[1:], **EST)
    add('家业', '名目带方括号', '【家业】' + E[3:], **EST)
    add('家业', '行内反引号', BT + E + BT, **EST)
    add('家业', '代码围栏包一行', [F3, E, F3], **EST)
    add('家业', '代码围栏包七行', [F3] + ES + [F3], 家业卡=13, 没类的卡=0, 剩反引号=0, 剩记号=0)
    add('家业', '中文引号', '“' + E + '”', **EST)
    add('家业', '直角引号', '「' + E + '」', **EST)
    add('家业', '整行加粗', '**' + E + '**', **EST)
    add('家业', '列表号', '- ' + E, **EST)
    add('家业', '末尾多一个竖线', E + '｜', **EST)
    add('家业', '只有类和名', '｜'.join(E.split('｜')[:3]), **EST)
    add('家业', '漏记号只有类和名', half('｜'.join(E.split('｜')[:3]))[1:], **EST)
    add('家业', '多两栏', E + '｜驻地 北门营房｜同袍 三十来人', **EST)
    add('家业', '漏了类', '｜'.join(E.split('｜')[:1] + E.split('｜')[2:]), '出一张没有类的卡', 家业卡=7, 没类的卡=1, 剩记号=0)
    add('家业', '名目写成势力', '§' + E[4:], '收进扩展页', 家业卡=6, MOD卡=1, 剩记号=0)
    add('家业', '括号里带竖线', E.replace('欠着 秋猎要随驾', '欠着 秋猎要随驾（甲|乙两路）'), 家业卡=7, 没类的卡=0, 剩半角竖线=0, 剩记号=0)

    PET = dict(宠卡=2, 没头的宠=0, 浮栏宠=2, 剩半角竖线=0, 剩反引号=0, 剩记号=0, MOD卡=0)
    add('宠', '原样', P, **PET)
    add('宠', '半角竖线', half(P), **PET)
    add('宠', '半角竖线带空格', P.replace('｜', ' | '), **PET)
    add('宠', '漏了行首记号', P[1:], **PET)
    add('宠', '漏了行首记号又半角', half(P[1:]), **PET)
    for mk in ['＃', '#', '※', '§§']:
        add('宠', '行首写成' + mk, mk + P[1:], **PET)
    add('宠', '名目带方括号', '【宠】' + P[2:], **PET)
    add('宠', '行内反引号', BT + P + BT, **PET)
    add('宠', '代码围栏', [F3, P, F3], **PET)
    add('宠', '中文引号', '“' + P + '”', **PET)
    add('宠', '整行加粗', '**' + P + '**', **PET)
    add('宠', '列表号', '- ' + P, **PET)
    add('宠', '末尾多一个竖线', P + '｜', **PET)
    add('宠', '多一栏', P + '｜口粮 每日两条鱼', **PET)
    add('宠', '少状态那一栏', '｜'.join(P.split('｜')[:4] + P.split('｜')[5:]), '出一张没有四条的小卡，不进浮栏', 宠卡=2, 没头的宠=0, 浮栏宠=1, 剩记号=0)
    add('宠', '只有名和种类', '｜'.join(P.split('｜')[:3]), '出一张只有一行字的小卡', 宠卡=2, 没头的宠=1, 剩记号=0)
    add('宠', '名目写成魔宠', '§魔宠' + P[2:], '收进扩展页', 宠卡=1, MOD卡=1, 剩记号=0)
    add('宠', '名目写成坐骑', '§坐骑' + P[2:], '收进扩展页', 宠卡=1, MOD卡=1, 剩记号=0)
    return out


n = card_rules(os.path.join(UP, 'rules_frame.json'), os.path.join(TMP, 'card_rules.json'))
ps = probes()
json.dump(ps, io.open(os.path.join(TMP, 'probes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
args = ['node', os.path.join(HERE, 'check_兜底.mjs'), os.path.join(TMP, 'card_rules.json'), os.path.join(TMP, 'probes.json')]
if len(sys.argv) > 2:
    card_rules(sys.argv[2], os.path.join(TMP, 'card_rules_改前.json'))
    args.append(os.path.join(TMP, 'card_rules_改前.json'))
print('卡里次序的规则', n, '条 →', os.path.join(TMP, 'card_rules.json'), '；歪法', len(ps), '种')
sys.stdout.flush()
sys.exit(subprocess.run(args).returncode)
