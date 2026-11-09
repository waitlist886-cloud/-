# 「名（」触发那一批条目的扫描深度（11-08）
# 底卡推演底座第3行要每个在场有名字的人写成「名（锚定源：旅途同行／凡世至强／任务人物／本地角色／新）」，
# 凡世至强、任务人物那七十八条就拿「名（」当触发词（基修亚（、凛（、露希亚（……），人在场才醒。
# 可它们的扫描深度都是 1，日里实测深度 1 只看玩家刚发的那一句，看不到上一条回复，AI 写的那一行扫不到，等于没设。
# 用户 11-08：“改，一起重打”。这里改成深度 2（看得到上一条回复），「名（」换成认全角半角两种括号的正则 /名[（(]/。
# 深度 2 以后上一条回复也扫得到，名字只有一个字、跟常用词撞的几个守一下（「威风凛凛，」「与凛冽的风」不叫醒凛），GUARD 那张表。
# 日里那几张（1001年切片、四纪大框、v12）调 fix_rili；风月照日里改过的那几条对应着调 fy_key 改触发、深度跟着日里。
# 守的写法只用 RE2 也认的（不用前瞻后顾），风月那一边一样用。
import re

NAME_PAREN = re.compile(r'^([^/（()\s][^（()]*)（$')     # 纯词，名字后头跟一个全角左括号
FIXED_WORD = re.compile(r'^/[^/]+\[（\(\]/$')           # 改过的 /名[（(]/
FY_TOKEN = re.compile(r'(^|\|)([^|()（）\[\]\\]+)（(?=\||$)')   # 风月的触发正则里，| 隔开的一段是「名（」
GUARD = {
    '凛，': '(?:^|[^凛])凛，',
    '凛、': '(?:^|[^凛])凛、',
    '与凛': '与凛(?:[^冽]|$)',
    '和凛': '和凛(?:[^冽]|$)',
}
FY_GUARD = re.compile(r'(^|\|)(%s)(?=\||$)' % '|'.join(map(re.escape, GUARD)))


def wants_fix(e):
    """两边扫、深度 1、触发里有「名（」（或者已经换成 /名[（(]/ 但深度还是 1，v12 改过、切片照发布卡拿深度的那一种）"""
    tw = e.get('triggerWords') or []
    return ('assistant' in (e.get('triggerRange') or []) and e.get('scanDepth') == 1
            and any(NAME_PAREN.match(w) or FIXED_WORD.match(w) for w in tw))


def fixed_word(w):
    if w in GUARD:
        return '/%s/' % GUARD[w]
    m = NAME_PAREN.match(w)
    return '/%s[（(]/' % re.escape(m.group(1)) if m else w


def fix_rili(lorebook):
    """日里的世界书：改深度、换触发，返回改了的条目下标。已经改过的（深度不是 1）不再动。"""
    done = []
    for i, e in enumerate(lorebook):
        if not wants_fix(e):
            continue
        e['triggerWords'] = [fixed_word(w) for w in e['triggerWords']]
        e['scanDepth'] = 2
        done.append(i)
    return done


def is_fixed(e):
    """日里这一条是不是改过的（深度 2，触发里有 /名[（(]/）"""
    return e.get('scanDepth') == 2 and any(FIXED_WORD.match(w) for w in (e.get('triggerWords') or []))


def fy_key(k):
    """风月的触发正则：| 隔开的「名（」那一段换成「名[（(]」，GUARD 里那几个短词换成守过的写法"""
    k = FY_TOKEN.sub(lambda m: '%s%s[（(]' % (m.group(1), m.group(2)), k)
    return FY_GUARD.sub(lambda m: m.group(1) + GUARD[m.group(2)], k)
