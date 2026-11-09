# 底卡世界书触发修订（11-08）：用户“先修复底卡，把底卡切片一次性改好”，看了切片又“一起改”（风月、四纪大框、v12 跟着）。
# 体检（会话临时目录 base_audit.py，拿 1001 年那一局 41 条样本和试写回复模拟）查出来的，一次改齐：
#   1. 勾了 AI 回复、扫描深度 1 的条目：日里实测深度 1 只看玩家刚发的那一句，AI 那一侧等于没设。
#      其中拿「名（」当触发的七十八条走 name_paren.py（括号认全角半角、凛的短词守住）；别的四百八十八条一律改深度 2。
#      模拟：改了以后四百五十条在样本回复里一回不醒，三十五条偶尔醒（打仗时醒战斗规则、名字出现时醒旅伴、在办的兆醒兆），
#      每轮都醒的三条里「兆一」是该醒的、「世界自转」本来就是每轮低概率，「层与层之间」是被面板里「下一层 LVL 40」叫醒的，下面守住。
#   2. 扫描深度 0 的十二条（存档、读档、格式刷新、校准、差评、开关这些一次性的命令）：实测 0 会往回看到上一条玩家消息，
#      发完命令的下一轮条目还会再进来一回。改成 1；命令说的「此后」都靠 AI 自己记，不靠条目再进来。
#      防抢话开关例外（SPECIAL）：它是两档的细处（动笔前先认准这一轮是开是关），状态每轮写在底座里，照风月那一张的做法
#      添「防抢话 关」，底座写着关的时候醒，深度 2。
#   3. 深度 2 以后 AI 的旁白也扫得到，几个常用词会叫醒不相干的条目，换成只认记录行或者特定说法的写法（GUARD）：
#      名字是常用词的命星只认记录行里「｜X｜」和正文里「【X】」（回复里命星照骨架写成 §能力｜Passive｜警觉｜Rare｜…），
#      装备换算那一条的「换上」「卸下」只认后头跟着装备的，「层与层之间」的「下一层」不认面板里的「下一层 LVL」，节庆那一条的「轻松」不认「轻松地」。
#      风月的触发是一整条正则，照 FY_GUARD 换那一段（只用 RE2 认的写法，不用前瞻）。
# 只动底卡那一千三百九十七条（四纪的条目不动）。
import re

import name_paren as NP

GUARD = {  # 条目头一行 → {原词: 换成的词（None 是拿掉，另一个词已经并进去了）}
    '## 装备换算｜面板攻防与一次出手': {
        '换上': '/(?:换上|卸下)[^。\\n｜]{0,8}(?:甲|铠|剑|刀|枪|斧|锤|弓|盾|杖|装备|武器|护手|头盔|靴)/',
        '卸下': None,
    },
    '# 层与层之间｜雾门、层碑，和「还要不要再下一层」': {'下一层': '/下一层(?! ?LVL)/'},
    '# 节庆·轻的那一半（**平衡条·优先级高**）': {'轻松': '/轻松(?!地)/'},
    '## 鹰眼 (Passive | Rare)': {'鹰眼': '/｜鹰眼｜|【鹰眼】/'},
    '## 夜视 (Passive | Rare)': {'夜视': '/｜夜视｜|【夜视】/'},
    '## 铁胃 (Passive | Rare)': {'铁胃': '/｜铁胃｜|【铁胃】/'},
    '## 警觉 (Passive | Rare)': {'警觉': '/｜警觉｜|【警觉】/'},
    '## 风纹认路法 (Art | Epic)': {'算水': '/｜算水｜|【算水】/'},
    '## 共祷法 (Art | Legend)': {'配齐': '/｜配齐｜|【配齐】/'},
    '## 护道列舰法 (Art | Legend)': {'护道': '/｜护道|【护道/'},
    '## 花雨剑舞 (Art | Legend)': {'花雨': '/｜花雨|【花雨/'},
    '## Special Unique｜圣剑': {'圣剑': '/｜圣剑｜|【圣剑】/'},
}
# 风月：同一张表，换成 RE2 认的写法（风月的触发正则不认前瞻）
FY_GUARD = {}
for _h, _ws in GUARD.items():
    FY_GUARD[_h] = {}
    for _w, _n in _ws.items():
        if _n is None:
            FY_GUARD[_h][_w] = None
        elif '(?!' in _n:
            FY_GUARD[_h][_w] = {'下一层': '下一层(?:$|[^ L]| [^L])', '轻松': '轻松(?:[^地]|$)'}[_w]
        else:
            FY_GUARD[_h][_w] = _n[1:-1]
# 风月的「换上」多半已经写在带装备的组里，单独那一段「卸下」照日里拿掉的话风月就没了认卸下的词，风月这一边单独守住，不拿掉
FY_GUARD['## 装备换算｜面板攻防与一次出手']['卸下'] = r'卸下[^。\n｜]{0,8}(?:甲|铠|剑|刀|枪|斧|锤|弓|盾|杖|装备|武器|护手|头盔|靴)'
SPECIAL = {'## 防抢话开关': {'scanDepth': 2, 'add': ['/防抢话[ ：:]{0,2}关/']}}   # 底座照骨架写「防抢话 关」，写歪了中间是冒号的也认


def head_of(e):
    return e['content'].split('\n', 1)[0].strip()


def apply(lorebook, nb=None):
    """底卡那几条改齐，返回各项改了的条目下标。nb：底卡的条数（四纪的卡只动前 nb 条）"""
    lb = lorebook[:nb] if nb else lorebook
    rep = {'名（': NP.fix_rili(lb), '深度0改1': [], '深度1改2': [], '守住的词': [], '防抢话开关': []}
    for i, e in enumerate(lb):
        sp = SPECIAL.get(head_of(e))
        if sp:
            if e.get('scanDepth') != sp['scanDepth'] or any(w not in e['triggerWords'] for w in sp['add']):
                e['scanDepth'] = sp['scanDepth']
                e['triggerWords'] = e['triggerWords'] + [w for w in sp['add'] if w not in e['triggerWords']]
                assert 'assistant' in e['triggerRange'], head_of(e)
                rep['防抢话开关'].append(i)
        elif e.get('scanDepth') == 0:
            e['scanDepth'] = 1
            rep['深度0改1'].append(i)
        elif 'assistant' in (e.get('triggerRange') or []) and e.get('scanDepth') == 1:
            e['scanDepth'] = 2
            rep['深度1改2'].append(i)
    heads = {}
    for i, e in enumerate(lb):
        heads.setdefault(head_of(e), []).append(i)
    for head, ws in GUARD.items():
        assert len(heads.get(head, [])) == 1, ('条目头一行对不上', head, heads.get(head))
        e = lb[heads[head][0]]
        tw = list(e['triggerWords'])
        for w, new in ws.items():
            if w not in tw:
                assert new is None or new in tw, ('触发里没有这个词', head, w)   # 已经改过的不再动
                continue
            k = tw.index(w)
            if new is None:
                del tw[k]
            else:
                tw[k] = new
                re.compile(new[1:-1])
            rep['守住的词'].append((heads[head][0], w))
        assert len(tw) <= 20, (head, len(tw))
        e['triggerWords'] = tw
    return rep


def split_top(s):
    """正则按最外层的 | 切开（括号、方括号里的不切）"""
    parts, depth, cur, i = [], 0, '', 0
    while i < len(s):
        c = s[i]
        if c == '\\' and i + 1 < len(s):
            cur += s[i:i + 2]
            i += 2
            continue
        if c == '[':
            j = i + 1
            if s[j:j + 1] == '^':
                j += 1
            if s[j:j + 1] == ']':
                j += 1
            while j < len(s) and s[j] != ']':
                j += 2 if s[j] == '\\' else 1
            cur += s[i:j + 1]
            i = j + 1
            continue
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        if c == '|' and depth == 0:
            parts.append(cur)
            cur = ''
        else:
            cur += c
        i += 1
    parts.append(cur)
    return parts


def fy_guard(key, head):
    """风月的触发正则：GUARD 那几条里，最外层 | 隔开的那一段正好是原词的，换成 RE2 的守法（括号里的不动，那里多半已经带着上下文）。
    返回 (新正则, 换了的词)"""
    done = []
    rules = FY_GUARD.get(head, {})
    if not rules:
        return key, done
    parts = split_top(key)
    for k, p in enumerate(parts):
        if p in rules and rules[p] is not None:
            parts[k] = rules[p]
            done.append(p)
    key = '|'.join(parts)
    re.compile(key)
    return key, done
