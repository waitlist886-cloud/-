#!/usr/bin/env python3
# 目录条（11-25，本地干跑报告第 2 条）：四纪条目的触发是「纪元那一支」加「话题那一支」同时满足、不跨消息，
# 玩家第二轮以后问的事当轮叫不醒，靠模型在回复里写 §预载、下一轮醒；可模型不知道卡里（尤其 DLC 里）有哪些条目、该写哪几个字。
# 这一支照打好的卡里的条目名单和触发，一纪出一条本体的目录条、一包一纪出一条 DLC 的目录条，跟着纪元常驻，只列名目和往 §预载 里写的字。
#
#   python -I -X utf8 底稿/DLC/tools/make_index.py [卡.json] [--dry] [--show]
#     卡：默认 out/发布卡_四纪大框/ 下带 _全本 的那一张（本体加各包 DLC；切包以前的整卡也行）。
#     --dry  只印各条的字数和要写的文件，不写盘。   --show  把各条正文印出来。
#   写出（都是生成的，别直接改；添了条目、改了触发，打一回卡以后拿新卡重跑这一支，再打一回）：
#     月银纪补卷/目录条.md、纷争纪/补卷/补卷_目录条.md、山铜纪/补卷/补卷_目录条.md、迷宫纪前传/补卷/补卷_目录条.md
#         一纪一份：本体一条（文件夹 42），DLC 一包一条（落在那一包自己的文件夹号里，make_dlc.py 照文件夹切走，装了才有）。
#         前传那一份里另有 1001 年的 DLC 目录条（律法志、风物志、谱系志写 1001 年的那一截，触发带 1001 年以后的年份正则）。
#     底卡新条目_四纪大框/目录条_1001.md      1001 年那一局本体的目录条（general_entries.apply_1001_new 收，只进四纪大框）。
#     通用条目/大图书馆_目录条.md            大图书馆那一包的目录条，五条（四纪各一条加 1001 年），标题「大图书馆｜」打头，照标题切进那一包。
#   四纪大框打卡时 底稿/状态栏/大框/gate_1125.py 拿同一套算法对一遍卡里的目录条，跟现在该出的不一样就提醒重跑。
#
# 一条目录条怎么来的：
#   · 名单：照文件夹挑（见下面 BODY_GROUPS、PACKS）。每条条目拿「这一纪的底座加一行 §预载｜字」去试它的触发和黑名单（slim_card 的算法），
#     试得醒的字才写进目录。字先从条目标题里找，标题里的字叫不醒的，从话题那一支正则里拆出一个叫得醒的（先挑条目正文里出现过的）。
#   · 标题里的字叫得醒的只写那几个字；叫不醒的写成「名目（写 字）」。同一个名目几个年份窗的只列一回，条目自己的黑名单挑年份。
#   · 羁绊篇、支线扩展、神谱三包条目太多（一纪几十上百条），不逐条列，写怎么叫醒：羁绊写「名字的羁绊」，支线写标题、全单在总则那一条，
#     神谱照主提示词不往预载里写神名、正文里写出神号就醒。大图书馆一厅列一本成书最早的，写了书名那一厅就醒。
#   · 真龙志（文件夹 64）：卡里有了这一包的条目，PACKS 里那一行就会出目录条（通用的列法）；条目多到列不下，照羁绊篇那样在 special 里写一支。
import collections
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', '大框'))
import slim_card as SL          # noqa: E402  _hit：触发和黑名单的算法

try:
    import re._parser as SRE    # 3.11 以后
except ImportError:             # pragma: no cover
    import sre_parse as SRE

ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪']
# 纪 → (文件, 条目设置里的纪元钥匙, 本体目录条落的文件夹, 试的年份)
ERA_CFG = collections.OrderedDict([
    ('月银纪', dict(file='月银纪补卷/目录条.md', gate='〔月银纪·正则〕', folder='42·月银纪｜规则补丁', head='# 月银纪世界书补卷｜目录条',
                 years=[2, 500, 1000, 1001, 1690, 2500, 3000, 3001, 3600, 4300, 5000, 5800, 6599, 6600, 7000, 7600, 8200, 8201, 9000, 9500, 10000, 10081])),
    ('纷争纪', dict(file='纷争纪/补卷/补卷_目录条.md', gate='〔纷争纪·正则〕', folder='42·纷争纪｜规则补丁', head='# 纷争纪世界书补卷｜目录条',
                 years=[2, 60, 120, 121, 240, 300, 301, 700, 1020, 1050, 1051, 2000, 3000, 4500, 4501, 6000, 8000, 8001, 9000, 10500, 10501, 10950, 11034])),
    ('山铜纪', dict(file='山铜纪/补卷/补卷_目录条.md', gate='〔山铜纪·正则〕', folder='42·山铜纪｜规则', head='# 山铜纪世界书补卷｜目录条',
                 years=[2, 30, 100, 300, 301, 450, 579, 580, 620, 660, 661, 668, 700, 741, 742, 800, 861, 862, 900, 947])),
    ('迷宫纪', dict(file='迷宫纪前传/补卷/补卷_目录条.md', gate='〔迷宫纪前传·正则〕', folder='42·迷宫纪｜规则', head='# 迷宫纪前传世界书补卷｜目录条',
                 years=[2, 3, 20, 50, 100, 101, 246, 317, 318, 420, 500, 599, 600, 700, 849, 850, 900, 970, 971, 990, 1000])),
])
Y1001 = [1001, 1002]
RX_1001 = '/(?:<br>|hud-meta">|纪元：)迷宫纪(?:100[1-9]|10[1-9]\\d|1[1-9]\\d\\d)年/'     # 跟新料里写 1001 年的条同一支（build_v12 的 maze_check 认它）
ALSO = '/§底座｜|命途已确认/'       # 第二支：回复的底座，或者建档凭证。只有头一行的开局口令（build_v12 的模拟）不醒
FILE_1001 = '底卡新条目_四纪大框/目录条_1001.md'
FILE_LIB = '通用条目/大图书馆_目录条.md'
FOLDER_1001 = '00·核心运行'
FOLDER_LIB = '02·公开历史与纪年'
BUDGET = 500            # 一条正文的字数线（过了就在备注里提醒，不拦）
INDEX_MARK = '目录｜'    # 目录条自己的标题里都有这三个字，挑名单时跳过（大图书馆那几条是「大图书馆｜目录·X」，见 is_index）

# 本体目录条：这一纪「问了才用」的条目，一组一行。组名 → 文件夹号
BODY_GROUPS = [('规则', '42'), ('风土', '54')]
# DLC：包名 → (文件夹号, 列法)。列法：list 逐条列；bond、side、gods 是太多列不下的三包，各写各的
PACKS = collections.OrderedDict([
    ('羁绊篇', ('57', 'bond')),
    ('支线扩展', ('56', 'side')),
    ('神谱', ('58', 'gods')),
    ('律法志', ('61', 'list')),
    ('风物志', ('62', 'list')),
    ('谱系志', ('63', 'list')),
    ('真龙志', ('64', 'list')),
    ('宝物志', ('65', 'list')),
])
# 1001 年本体目录条：底卡侧只在 1001 年醒的新条目（触发里带 1001 年以后的年份正则），照标题开头分组；另加底卡几条要靠预载的
# (组名, 标题的正则, 组里是不是只写字)：阶衔、封地、对头团三组名目长，组名已经说了是什么，只写往预载里写的字
LAND = '封地|开拓地|没人要的地'
GROUPS_1001 = [
    ('产业', r'^产业｜', False),
    ('阶衔', r'^势力｜阶衔·', True),
    ('封地', r'^势力｜[^｜]*(?:%s)' % LAND, True),
    ('对头团', r'^势力｜对头团', True),
    ('势力', r'^势力｜(?!阶衔·|对头团)(?![^｜]*(?:%s))|^规则｜这一纪的势力与家业' % LAND, False),
    ('地和路', r'^路程｜|^据点｜|^地点｜海路|^规则｜领地', False),
    ('别的', r'^日用器物｜|^规则｜渊染传奇|^规则｜觉醒照出魔族的血', False),
]
BASE_1001 = [('委托', r'^委托·'), ('史诗战', r'^史诗Boss战统一引擎')]      # 底卡里认 §预载 的几条；战斗栏那一行四纪和 1001 年都带（fight_line）
# 状态栏每轮照抄的栏名：拿它当预载的字没有用（那一条本来就每轮在），别的会话正在把这些词从话题那一支里拿掉
FIXED_WORDS = set('委托 羁绊 命路 位阶 旅印 伟业 层级 装备 背包 见闻 记忆 日报 活事件 面板 资源 六维 攻防 能力 物品 家业 角色 预载 分支 正文 环境 底座 推演 战斗 状态 容貌 着装 姿态 身份 立绘 泉眼'.split())


def read(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n')


def _cardscan_rx():
    """卡面检查那几张词表从 tools/cardscan.py 里取，免得两边对不上。"""
    s = read(os.path.join(ROOT, 'tools', 'cardscan.py'))
    out = []
    for name in ('MOON', 'CN', 'FORBID'):
        m = re.search(r"(?m)^%s = r'([^']+)'" % name, s)
        assert m, name
        out.append(m.group(1))
    return re.compile('|'.join(out) + '|米|——|—|；|…|！|\\.\\.\\.')


BAD_WORD = _cardscan_rx()
OK_KEY = re.compile(r'^[一-鿿A-Za-z0-9·《》]{2,12}$')


def is_index(title):
    return INDEX_MARK in title or title.startswith('大图书馆｜目录·')


def title_of(e):
    for l in (e.get('content') or '').split('\n'):
        if l.strip():
            return l.strip().lstrip('#').strip()
    return ''


def folder_no(e):
    m = re.match(r'(\d+)·', e.get('folder') or '')
    return m.group(1) if m else ''


def era_of(e):
    m = re.search('|'.join(ERAS), e.get('folder') or '')
    return m.group(0) if m and folder_no(e) >= '40' and folder_no(e) < '90' else None


def woke(e, msg, role='assistant'):
    if role not in (e.get('triggerRange') or []):
        return False
    return SL._hit(e.get('triggerWords'), e.get('triggerWordsType'), msg) and not SL._hit(e.get('blackListWords'), e.get('blackListWordsType'), msg)


def base_msg(era, y, key):
    return ('§底座｜纪元：%s%d年·秋·坠叶月·上旬三日 · 18:20 薄暮 · 某地 · 潮汐 · 防抢话 开 · 档位 长\n§环境｜晴｜远处有钟\n§正文｜某地\n她把门带上。\n§预载｜%s\n' % (era, y, key))


# ---------------- 从正则里拆出叫得醒的字 ----------------
def _gen(seq, deep=0):
    """照正则的语法树出一个最短的例子；出不了的回 None。"""
    out = ''
    for op, av in seq:
        op = str(op)
        if op == 'LITERAL':
            out += chr(av)
        elif op in ('AT', 'ASSERT', 'ASSERT_NOT'):
            continue
        elif op in ('MAX_REPEAT', 'MIN_REPEAT', 'POSSESSIVE_REPEAT'):
            lo, hi, sub = av
            if lo == 0:
                continue
            g = _gen(sub, deep + 1)
            if g is None:
                return None
            out += g * lo
        elif op == 'SUBPATTERN':
            g = _gen(av[3], deep + 1)
            if g is None:
                return None
            out += g
        elif op == 'ATOMIC_GROUP':
            g = _gen(av, deep + 1)
            if g is None:
                return None
            out += g
        elif op == 'BRANCH':
            for alt in av[1]:
                g = _gen(alt, deep + 1)
                if g is not None:
                    out += g
                    break
            else:
                return None
        elif op == 'IN':
            neg = any(str(o) == 'NEGATE' for o, _ in av)
            if neg:
                out += '的'
                continue
            for o, v in av:
                o = str(o)
                if o == 'LITERAL':
                    out += chr(v)
                    break
                if o == 'RANGE':
                    out += chr(v[0])
                    break
                if o == 'CATEGORY':
                    out += {'CATEGORY_DIGIT': '1', 'CATEGORY_SPACE': ' ', 'CATEGORY_WORD': '甲'}.get(str(v), '甲')
                    break
            else:
                return None
        elif op == 'ANY':
            out += '的'
        elif op == 'NOT_LITERAL':
            out += '的'
        else:
            return None
    return out


def _alts(seq):
    """最外层的几支（一层括号包着的也拆开）。"""
    if len(seq) == 1:
        op, av = seq[0]
        op = str(op)
        if op == 'BRANCH':
            out = []
            for a in av[1]:
                out += _alts(a)
            return out
        if op == 'SUBPATTERN':
            return _alts(av[3])
    return [seq]


def _opt_variants(seq):
    """一支里「可有可无」的那几处各添上一回，再出一个例子（雷狱(?:的)?锁 → 雷狱锁、雷狱的锁）。"""
    res = [_gen(seq)]
    for k, (op, av) in enumerate(seq):
        if str(op) in ('MAX_REPEAT', 'MIN_REPEAT') and av[0] == 0:
            g = _gen(av[2], 1)
            if g and re.fullmatch(r'[一-鿿]{1,2}', g):
                a, b = _gen(seq[:k]), _gen(seq[k + 1:])
                if a is not None and b is not None:
                    res.append(a + g + b)
    return [r for r in res if r]


def samples(word, limit=80):
    """一条触发词能叫醒它的几个字（正则拆到最外层各支，各出一两个例子；纯词就是它自己）。"""
    p = SL.parse(word)
    if not p:
        return [word]
    body = p[0]
    pre = ''
    m = re.match(r'^§预载｜\[\^\\n\]\{0,\d+\}', body)       # 底卡认 §预载 的那一支：/§预载｜[^\n]{0,400}(?:名|名)/
    if m:
        body = body[m.end():]
    try:
        tree = SRE.parse(body)
    except Exception:
        return []
    out = []
    for alt in _alts(list(tree)):
        for s in _opt_variants(list(alt)):
            s = s.strip()
            if s and s not in out:
                out.append(s)
        if len(out) >= limit:
            break
    return out


def is_gate(w):
    return '纪元：' in w or w.startswith('/^(?![') or '开局时段：' in w


def topic_words(e):
    return [w for w in e.get('triggerWords') or [] if w and not is_gate(w)]


def in_scope(e, era, years):
    """这一条在这一纪这几个年份里有没有可能醒：同时满足的条目，认纪元的那几支得有一年全中（话题和黑名单不看）。回中的那几年。"""
    if (e.get('triggerWordsType') or 'OR') != 'AND':
        return list(years)
    gates = [w for w in e.get('triggerWords') or [] if w and is_gate(w)]
    return [y for y in years if SL._hit(gates, 'AND', base_msg(era, y, '无'))] if gates else list(years)


def cat_of(title):
    m = re.match(r'^(?:月银纪|纷争纪|山铜纪|迷宫纪)·([^｜]+)｜', title)
    return m.group(1) if m else ''


def name_of(title):
    """标题｜后头那一截，去掉末尾的年份窗括号；没有｜的去掉纪名。阶层那几条（东陆、西陆）前头带上类。"""
    t = title.split('｜', 1)[1] if '｜' in title else re.sub(r'^(?:月银纪|纷争纪|山铜纪|迷宫纪)·', '', title)
    while re.search(r'（[^（）]*）$', t):
        t = re.sub(r'（[^（）]*）$', '', t).strip()
    if cat_of(title) == '阶层':
        t = '阶层·%s' % t
    return t


def title_pieces(title):
    """标题里能当预载的字：先·前头那一截（聚落与人口·诸国期 → 聚落与人口，几个年份窗的就并成一项了），再整截，再拆开的。"""
    n = name_of(title)
    first, last = n.split('·')[0], n.split('·')[-1]
    out = ([first] if '·' in n and len(first) >= 3 and first != '阶层' else []) + ([last] if '·' in n and len(last) >= 3 else []) + [n]
    for sep in (r'[·，、]', r'[·，、与和]', r'[·，、与和的]'):
        out += [x for x in re.split(sep, n) if len(x) >= 2]
    return list(dict.fromkeys(x for x in out if x))


def share2(a, b):
    """两个词有没有连着两个字是一样的。"""
    return any(a[k:k + 2] in b for k in range(len(a) - 1))


def ok_key(c):
    return bool(OK_KEY.match(c)) and not BAD_WORD.search(c) and c not in FIXED_WORDS


def _product(lists, cap):
    out = [[]]
    for l in lists:
        out = [a + [b] for a in out for b in l][:cap]
    return out


def work_keys(e, era, years, limit=8, tries=48):
    """这一条写进预载叫得醒的字，照好坏排：先标题里的，再跟标题沾边的，再照话题那一支正则里的先后。
    回 [(字, 是不是标题里的)]；年份窗窄、试的年份都叫黑名单挡了的，不看黑名单再试一遍。"""
    title = title_of(e)
    name = name_of(title)
    pieces = title_pieces(title)
    tws = topic_words(e) or [w for w in e.get('triggerWords') or [] if w]
    AND = (e.get('triggerWordsType') or 'OR') == 'AND'
    if AND and len(tws) > 1:
        per = []
        for w in tws:
            cs = [c for c in samples(w) if ok_key(c)][:6]
            if not cs:
                return []
            per.append(cs)
        cands = ['、'.join(x) for x in _product(per, 24)]
    else:
        cands = []
        for w in tws:
            cands += samples(w)
        cands = [c for c in dict.fromkeys(pieces + cands) if ok_key(c)]
    rank = lambda c: 0 if c in pieces else 1 if share2(c, name) else 2
    cands = sorted(cands, key=rank)[:tries]           # sorted 是稳的，同一档里照原来的先后
    ys = in_scope(e, era, years)
    if not ys:
        return []
    out = []
    for c in cands:
        if any(woke(e, base_msg(era, y, c)) for y in ys):
            out.append((c, c in pieces or (len(c) >= 3 and c in name)))
            if len(out) >= limit:
                break
    if not out:
        for c in cands:
            if any(SL._hit(e.get('triggerWords'), e.get('triggerWordsType'), base_msg(era, y, c)) for y in ys):
                out.append((c, c in pieces or (len(c) >= 3 and c in name)))
                if len(out) >= limit:
                    break
    return out


def short_name(n):
    """括号前头的名目：八个字以内原样；长的挑拆开以后最长的、八个字以内的那一截。"""
    if len(n) <= 8:
        return n
    ps = [x for x in re.split(r'[·，、]', n) if 2 <= len(x) <= 8 and x not in ('阶衔', '对头团')]
    return max(ps, key=len) if ps else n


def show(name, key, in_title):
    """一项怎么写：字就在名目里、或者一看就知道说的是它的，只写字；不然写 名目（写 字）。"""
    if in_title or key == name or name in key or (len(key) >= 4 and share2(key, name)):
        return key
    return '%s（写 %s）' % (short_name(name), key)


def list_items(lb, idx, era, years, bare=False):
    """逐条列：回 (项…, 叫不醒的标题…)。同一个名目几个年份窗的并成一项：有一个字几条都叫得醒就用它，没有就把各条的字都写进括号。
    bare：只写往预载里写的字，不带名目。"""
    groups, miss = collections.OrderedDict(), []
    for i in idx:
        e = lb[i]
        if 'assistant' not in (e.get('triggerRange') or []):
            continue                                   # 只扫玩家的话的（只给 AI、玩家追问才醒的真相条），预载叫不醒，不列
        if not in_scope(e, era, years):
            continue                                   # 不是这几个年份的条目（前传的目录条里写 1001 年的那几条）
        ks = work_keys(e, era, years)
        if not ks:
            miss.append(title_of(e))
            continue
        groups.setdefault(name_of(title_of(e)), []).append(ks)
    items, seen = [], set()
    for name, members in groups.items():
        if bare:
            s = '、'.join(dict.fromkeys(m[0][0] for m in members))
        elif len(members) == 1:
            s = show(name, *members[0][0])
        else:
            common = [k for k, _ in members[0] if all(any(k == k2 for k2, _ in m) for m in members[1:])]
            if common:
                k = common[0]
                s = show(name, k, any(t for kk, t in members[0] if kk == k))
            else:
                keys = list(dict.fromkeys(m[0][0] for m in members))
                s = '%s（写 %s）' % (short_name(name), '、'.join(keys))
        if s not in seen:
            seen.add(s)
            items.append(s)
    return items, miss


# ---------------- 各种目录条的正文 ----------------
def era_word(era, y1001=False):
    return '迷宫纪1001年' if y1001 else ('迷宫纪前传' if era == '迷宫纪' else era)


FIGHT_LINE = '- 打仗｜眼看要动手的那一轮写 %s，敌情和战况那几行照它排。'


def one_key(e, era, years):
    ks = work_keys(e, era, years)
    return ks[0][0] if ks else None


def body_index(lb, era, cfg, notes):
    L = ['【调用】%s的局里每轮都在，是名单不是内容。下面的条目问了才醒。玩家问到、或者下一轮要用哪一样，把那几个字原样写进 §预载，下一轮才到，'
         '带括号的写括号里的字，一回两三样。没到以前照已经知道的答到够用，不编专名和数。' % era_word(era)]
    for gname, fno in BODY_GROUPS:
        idx = [i for i, e in enumerate(lb) if folder_no(e) == fno and era_of(e) == era and not is_index(title_of(e))]
        items, miss = list_items(lb, idx, era, cfg['years'])
        if miss:
            notes.append('%s·%s：%d 条写进预载叫不醒，没列（%s）' % (era, gname, len(miss), '、'.join(miss[:8])))
        if items:
            L.append('- %s｜%s' % (gname, '、'.join(items)))
    L += fight_line(lb, era, cfg['years'][-1], notes)
    return '\n'.join(L)


def base_keys(lb, era, y, rx, notes, where):
    """底卡侧条目（不挡这一纪、认 §预载 的）：标题｜前头那一截里最短的、叫得醒的字。"""
    r = re.compile(rx)
    items = []
    for i, e in enumerate(lb):
        if folder_no(e) >= '40' or not r.search(title_of(e)):
            continue
        head = re.sub(r'（[^）]*）', '', title_of(e).split('｜', 1)[0]).strip()
        cands = [x for x in head.split('·')[1:] if len(x) >= 3] + [head]
        for c in cands:
            if OK_KEY.match(c) and c not in FIXED_WORDS and woke(e, base_msg(era, y, c)):
                items.append(c)
                break
        else:
            notes.append('%s：底卡「%s」写进预载叫不醒，没列' % (where, title_of(e)))
    return list(dict.fromkeys(items))


def fight_line(lb, era, y, notes):
    ks = base_keys(lb, era, y, r'^战斗栏｜', notes, era_word(era, y >= 1001) + '·打仗')
    return [FIGHT_LINE % ks[0]] if ks else []


def pack_list(lb, idx, era, years, pack, y1001, notes):
    items, miss = list_items(lb, idx, era, years)
    if miss:
        notes.append('%s·%s：%d 条写进预载叫不醒，没列（%s）' % (era_word(era, y1001), pack, len(miss), '、'.join(miss[:8])))
    if not items:
        return None
    L = ['【调用】装了%s这一包、%s的局里每轮都在。这是名单，不是内容。玩家问到哪一样，把那几个字原样写进 §预载，那一条下一轮才到，带括号的写括号里的字，有几个就都写。'
         '同一个名目分几个年份的，条目自己照这一局的年份挑。没到以前不编法条、价钱和人名。' % (pack, era_word(era, y1001)),
         '- %s｜%s' % (pack, '、'.join(items))]
    return '\n'.join(L)


def _topic_hit(e, era, y, key):
    """不看年份的黑名单，只看触发（羁绊、支线一条只在几十年的窗里醒，试的那几个年份多半不在窗里）。"""
    return SL._hit(e.get('triggerWords'), e.get('triggerWordsType'), base_msg(era, y, key))


def pack_bond(lb, idx, era, years, notes):
    ch = [i for i in idx if '之章' in title_of(lb[i])]
    rule = [i for i in idx if title_of(lb[i]).endswith('规则｜羁绊')]
    eg, ok = None, 0
    y = years[len(years) // 2]
    for i in ch:
        e = lb[i]
        for s in [x for w in topic_words(e) for x in samples(w)]:
            m = re.match(r'^(.{2,12}?)的?(?:个人线|羁绊|私人请求)$', s)
            if not m:
                continue
            key = m.group(1) + '的羁绊'
            if _topic_hit(e, era, y, key):
                ok += 1
                if eg is None and re.fullmatch(r'[一-鿿]{2,5}', m.group(1)) and not BAD_WORD.search(m.group(1)):
                    eg = key
                break
    if ok < len(ch):
        notes.append('%s·羁绊篇：%d 章里 %d 章写「名字的羁绊」叫不醒（话题那一支不是这个样子了），目录条照通用的写法没动' % (era, len(ch), len(ch) - ok))
    L = ['【调用】装了羁绊篇这一包、%s的局里每轮都在。这是名单，不是内容。' % era_word(era),
         '- 有什么｜这一纪 %d 章专属羁绊，一人一章，旅伴条和凡世至强条里写着专属羁绊那一行的人都有，章名就在那一行。' % len(ch),
         '- 怎么叫｜要开谁的章、或者他自己要开口邀人了，§预载 里写 名字的羁绊%s，或者写章名，下一轮那一章才到。那一章只在那个人在世的年份里醒，条目没到不开章，只当他有一段还没讲的旧事。'
         % ('，比如 ' + eg if eg else '')]
    if rule:
        k = one_key(lb[rule[0]], era, years)
        if k:
            L.append('- 规矩｜章怎么开、一幕怎么推、信物和协战技怎么给，在规则那一条，写 %s。' % k)
    return '\n'.join(L)


def pack_side(lb, idx, era, years, notes):
    gen = [i for i in idx if title_of(lb[i]).endswith('支线｜总则')]
    one = [i for i in idx if '·支线｜' in title_of(lb[i]) and i not in gen]
    y = years[len(years) // 2]
    bad = []
    for i in one:
        t = name_of(title_of(lb[i]))
        tail = t.split('·', 1)[1] if '·' in t else t
        if not _topic_hit(lb[i], era, y, tail):
            bad.append(t)
    if bad:
        notes.append('%s·支线扩展：%d 条里 %d 条写标题叫不醒（话题那一支里没有整句标题：%s）' % (era, len(one), len(bad), '、'.join(bad[:6])))
    L = ['【调用】装了支线扩展这一包、%s的局里每轮都在。这是名单，不是内容。' % era_word(era),
         '- 有什么｜这一纪 %d 条当地事，一条一处地方、几年的窗。' % len(one)]
    if gen:
        k = one_key(lb[gen[0]], era, years)
        if k:
            L.append('- 全单｜哪一年哪一处有哪一条，照年份排在总则那一条里，要看的时候 §预载 写 %s。' % k)
    L.append('- 怎么叫｜玩家走到那一处、问起当地的麻烦，年份又对得上，§预载 里写那一条的标题，地名后头那几个字，下一轮才到。条目没到以前不替它编人名和缘故。')
    return '\n'.join(L)


def pack_gods(lb, idx, era, years, notes):
    gods = [i for i in idx if '·神谱｜' in title_of(lb[i])]
    L = ['【调用】装了神谱这一包、%s的局里每轮都在。这是名单，不是内容。' % era_word(era),
         '- 有什么｜这一纪 %d 位神与魔神各一条，神号、来历、神域栏，祂倒下以后剩什么。' % len(gods),
         '- 怎么叫｜§预载 照旧不写神名。玩家当面问到哪一位、这一场要用到祂的神殿、神迹或者权柄，正文里写出祂的神号或名字，下一轮那一条就到。条目没到以前只说这一纪常驻和总表里有的，不编权柄、神国和死法。']
    return '\n'.join(L)


def lib_index(lb, era, years, y1001, notes):
    """大图书馆：一厅一行，厅里每一条（一段年月一条）列一本，这一纪最早就有的那一本（年份窗最宽）。"""
    halls = collections.OrderedDict()
    for i, e in enumerate(lb):
        t = title_of(e)
        if not t.startswith('大图书馆｜') or is_index(t):
            continue
        books = re.findall(r'(?m)^- 《([^》\n]{1,30})》', e.get('content') or '')
        best = None
        for b in books:
            for form in ('《%s》' % b, b):
                ys = [y for y in years if woke(e, base_msg(era, y, form))]
                if ys:
                    if best is None or ys[0] < best[0]:
                        best = (ys[0], '《%s》' % b)
                    break
        if best:
            n = t.split('｜', 1)[1]
            hall = re.split(r'的书，|，', n)[0]
            halls.setdefault(hall, []).append(best[1])
    if not halls:
        return None
    L = ['【调用】装了大图书馆这一包、%s的局里每轮都在。这是名单，不是内容。一间厅列一两本，要翻书、有人问书里写了什么，把书名连书名号写进 §预载，那一厅的书目下一轮才到，'
         '到了再照书目挑别的本。成书晚于这一局年份的那几本世上还没有。' % era_word(era, y1001),
         '- 厅和书｜%s' % '、'.join('%s %s' % (h, ''.join(bs)) for h, bs in halls.items())]
    return '\n'.join(L)


def index_1001(lb, notes):
    L = ['【调用】迷宫纪1001年的局里每轮都在，是名单不是内容。下面的条目要回复里带着这一年的底座才醒，玩家当轮问到的叫不醒。问到哪一样，'
         '把那几个字原样写进 §预载，下一轮才到，带括号的写括号里的字。没到以前照已经知道的答到够用，不编价钱、阶衔和地名。']
    cand = [i for i, e in enumerate(lb) if folder_no(e) < '40' and any('100[1-9]' in w for w in e.get('triggerWords') or []) and not is_index(title_of(e))]
    for gname, rx, bare in GROUPS_1001:
        r = re.compile(rx)
        idx = [i for i in cand if r.search(title_of(lb[i]))]
        items, miss = list_items(lb, idx, '迷宫纪', Y1001, bare)
        if miss:
            notes.append('迷宫纪1001年·%s：%d 条写进预载叫不醒，没列（%s）' % (gname, len(miss), '、'.join(miss[:8])))
        if items:
            L.append('- %s｜%s' % (gname, '、'.join(items)))
    for gname, rx in BASE_1001:
        ks = base_keys(lb, '迷宫纪', 1001, rx, notes, '迷宫纪1001年·' + gname)
        if ks:
            L.append('- %s｜%s' % (gname, '、'.join(ks)))
    L += fight_line(lb, '迷宫纪', 1001, notes)
    return '\n'.join(L)


# ---------------- 拼文件 ----------------
def setting(folder, gate, rng='用户与助手'):
    return '> 条目设置：文件夹 %s，触发（同时满足）%s、`%s`，黑名单 无，范围 %s，深度 2。' % (folder, gate, ALSO, rng)


NOTE = ('> 这一节是说明，不进卡。生成的，别直接改：`底稿/DLC/tools/make_index.py` 照打好的卡里的条目名单和触发出的，添了条目、改了触发，打一回卡以后拿新卡重跑它，再打一回。'
        '目录条跟着纪元常驻，只列名目和往 §预载 里写的字。来历和量过的字数在 `底稿/收尾_11-25/干跑修/目录条与底卡侧.md`。')


def build(lb):
    """回 ({相对路径: 文本}, [(纪或 1001, 标题, 正文)], 备注)。"""
    files, rows, notes = collections.OrderedDict(), [], []
    for era, cfg in ERA_CFG.items():
        secs = []

        def add(title, folder, gate, body, key):
            rows.append((key, title, body))
            secs.append('## %s\n\n%s\n\n%s\n' % (title, body, setting(folder, gate)))

        add('%s·目录｜规则与风土' % era, cfg['folder'], cfg['gate'], body_index(lb, era, cfg, notes), era)
        for pack, (fno, how) in PACKS.items():
            idx = [i for i, e in enumerate(lb) if folder_no(e) == fno and era_of(e) == era and not is_index(title_of(e))]
            if not idx:
                continue
            folder = lb[idx[0]]['folder']
            if how == 'bond':
                body = pack_bond(lb, idx, era, cfg['years'], notes)
            elif how == 'side':
                body = pack_side(lb, idx, era, cfg['years'], notes)
            elif how == 'gods':
                body = pack_gods(lb, idx, era, cfg['years'], notes)
            else:
                body = pack_list(lb, idx, era, cfg['years'], pack, False, notes)
            if body:
                add('%s·目录｜%s' % (era, pack), folder, cfg['gate'], body, era)
            if era == '迷宫纪' and how == 'list':
                b2 = pack_list(lb, idx, era, Y1001, pack, True, notes)
                if b2:
                    add('迷宫纪·目录｜%s（迷宫纪1001年）' % pack, folder, '`%s`' % RX_1001, b2, '迷宫纪1001年')
        files[cfg['file']] = '%s\n\n%s\n\n%s' % (cfg['head'], NOTE, '\n'.join(secs))
    # 1001 年本体
    b = index_1001(lb, notes)
    rows.append(('迷宫纪1001年', '迷宫纪·目录｜这一年问了才醒的那几样', b))
    files[FILE_1001] = ('# 底卡新条目｜目录条（迷宫纪1001年，只进四纪大框）\n\n%s\n\n## 迷宫纪·目录｜这一年问了才醒的那几样\n\n%s\n\n'
                        '> 条目设置：文件夹 %s，触发 `%s`，黑名单 无，范围 用户与AI，深度 2。\n' % (NOTE, b, FOLDER_1001, ALSO))
    # 大图书馆
    secs = []
    for era, cfg in ERA_CFG.items():
        b = lib_index(lb, era, cfg['years'], False, notes)
        if b:
            t = '大图书馆｜目录·%s' % era_word(era)
            rows.append((era, t, b))
            g = {'月银纪': '纪元：月银纪', '纷争纪': '纪元：(?:纷争纪|山铜纪元年)', '山铜纪': '纪元：(?:山铜纪(?!元年)|迷宫纪元年)',
                 '迷宫纪': '纪元：迷宫纪(?:[2-9]|[1-9]\\d|[1-9]\\d\\d|1000)年'}[era]
            secs.append('## 奥尔德兰·%s\n\n%s\n\n> 条目设置：文件夹 %s，触发 `/^(?=[\\s\\S]*%s)[\\s\\S]*(?:§底座｜|命途已确认)/`，黑名单 无，范围 用户与AI，深度 2。\n' % (t, b, FOLDER_LIB, g))
    b = lib_index(lb, '迷宫纪', Y1001, True, notes)
    if b:
        t = '大图书馆｜目录·迷宫纪1001年'
        rows.append(('迷宫纪1001年', t, b))
        secs.append('## 奥尔德兰·%s\n\n%s\n\n> 条目设置：文件夹 %s，触发 `/^(?=[\\s\\S]*纪元：迷宫纪(?:100[1-9]|10[1-9]\\d|1[1-9]\\d\\d)年)[\\s\\S]*(?:§底座｜|命途已确认)/`，黑名单 无，范围 用户与AI，深度 2。\n' % (t, b, FOLDER_LIB))
    files[FILE_LIB] = '# 通用条目｜大图书馆的目录条\n\n%s\n打包只读「## 奥尔德兰·」起的节，读法在 底稿/状态栏/大框/general_entries.py；标题「大图书馆｜」打头，make_dlc.py 照标题切进大图书馆那一包。\n\n%s' % (NOTE, '\n'.join(secs))
    return files, rows, notes


def expected(lb):
    """{卡里的标题: 正文}，gate_1125 拿它跟卡里现有的目录条比。卡里的标题：四纪的照原样，1001 年本体和大图书馆的去掉纪名。"""
    files, rows, notes = build(lb)
    out = {}
    for key, title, body in rows:
        t = title
        if title == '迷宫纪·目录｜这一年问了才醒的那几样':
            t = title.split('·', 1)[1]
        out[t] = body
    return out


def default_card():
    d = os.path.join(ROOT, 'out', '发布卡_四纪大框')
    for n in ('奥尔德兰_四纪大框_全本.json', '奥尔德兰_四纪大框_原介绍页_全本.json', '奥尔德兰_四纪大框.json'):
        if os.path.exists(os.path.join(d, n)):
            return os.path.join(d, n)
    raise SystemExit('找不到卡，把卡的路径写在命令后头')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    argv = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry, show = '--dry' in sys.argv, '--show' in sys.argv
    path = argv[0] if argv else default_card()
    lb = json.load(open(path, encoding='utf-8'))['prompt']['lorebook']
    # 底卡侧的预载钥匙（战斗栏、委托那一组）是 gate_1125 打卡时添的，旧卡里还没有就先在内存里添上再出名单
    import gate_1125 as G
    G.preload_extra(lb)
    files, rows, notes = build(lb)
    print('卡 %s（世界书 %d 条）' % (os.path.relpath(path, ROOT), len(lb)))
    tot = collections.OrderedDict()
    for key, title, body in rows:
        n = len('# %s\n%s' % (title, body))
        tot.setdefault(key, []).append((title, n))
    for key, lst in tot.items():
        print('%s：%d 条，合 %d 字' % (key, len(lst), sum(n for _, n in lst)))
        for t, n in lst:
            print('    %4d 字%s  %s' % (n, '（过 %d）' % BUDGET if n > BUDGET else '', t))
    if notes:
        print('备注：')
        for x in notes:
            print('  ·', x)
    if show:
        for key, title, body in rows:
            print('\n━━ %s\n%s' % (title, body))
    if dry:
        print('（--dry，没写盘）')
        return
    for rel, text in files.items():
        p = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text.rstrip('\n') + '\n')
        print('写了', rel)


if __name__ == '__main__':
    main()
