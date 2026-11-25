#!/usr/bin/env python3
# 风月版门控转换（11-25）：日里一条条目的“触发词表、触发方式、黑名单”转成风月的一条 RE2 钥匙。
# 日里的判法（slim_card._hit）：一条消息里 触发成立（OR 任一、AND 全中）而且 黑名单一个不中。风月一条只有一个正则，没有黑名单、没有前后顾。
#
# 做法（细目见同目录 说明.md）：
#   1. 每个触发词、黑名单词按最外层的 | 拆成支，分四类：
#        锚   认 §底座／凭证头一行“纪元：某纪N年”的（纪元、年份窗、旧凭证“纪元：某纪｜开局时段：”）
#        日期 锚后头还带季、月、旬的（山铜纪、迷宫纪二十来条）
#        开局 “开局时段：…”（泛的、某一条主线的、自己报年份的）
#        题   别的（话题词、潮汐里的页名主线名、§预载 那一行）
#   2. 锚拿这张卡里会出现的全部纪元年份（Ctx.U）逐个试，变成年份集合；黑名单里的年份从集合里减掉，
#      集合再写回一条紧凑的年份正则（gate）。集合等于整张卡的全集就是恒真，拿掉。
#   3. 黑名单里行内的东西（开局时段、潮汐里某条主线的幕、日期）写成“这一行从年份往后不含这几样”（avoid_line、not_prefix）。
#   4. “同时满足甲和乙”写成两支：甲[\s\S]*乙|乙[\s\S]*甲。
#   5. 只认玩家裸打的那一支（^(?!…§底座…)…）风月分不出消息是谁说的，拆成两条：一条只扫玩家认话题，一条只扫回复认 §预载 行。
#   6. 没有锚要求、可又带年份黑名单的（迷宫纪卡里底卡条目挡前传）写成“整段里没有不许的那种锚”（safe_src）。
#   7. 题里的前后顾只有落在一支末尾的才改写（X(?!Y) → X 后头是结尾或者不是 Y 开头），别的列进清单。
# 钥匙出来以后过 re2_problems（前后顾、反向引用、过一千的重复、RE2 不认的转义），不过的不进卡、列清单。
import bisect
import collections
import os
import re
import re._constants as _C
import re._parser as _P
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', '大框'))
import slim_card as SL   # noqa: E402  parse、top_alts、_hit、cases、year_text

ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪']
# 每张卡里会出现的锚：(纪, 记号)。记号 '∅' 是旧凭证（纪元：某纪｜开局时段：，不带年份；只有迷宫纪那一张认，前传的常驻自己写着认它），
# '元' 是元年，数是年份。纷争纪的局末尾会写到山铜纪元年，山铜纪的局末尾会写到迷宫纪元年（那一个月归山铜纪），
# 迷宫纪卡从 2 年起（前传）到 1001 年以后（底卡那一局）。年份只试到 ymax，集合碰到 ymax 就当“往上都算”，正则写到五位数。
CARDS = collections.OrderedDict([
    ('maze', dict(name='迷宫纪', book='maze', ymax=2500, years=(2, 2500), yuan=False, null=True, extra=[])),
    ('moon', dict(name='月银纪', book='moon', ymax=12000, years=(1, 12000), yuan=False, null=False, extra=[])),
    ('strife', dict(name='纷争纪', book='strife', ymax=12000, years=(1, 12000), yuan=True, null=False, extra=[('山铜纪', '元')])),
    ('bronze', dict(name='山铜纪', book='bronze', ymax=2000, years=(1, 2000), yuan=False, null=False, extra=[('迷宫纪', '元')])),
])
ALWAYS = '[\\s\\S]+'
LONG_GATE = 260
SPECIAL = set('\\^$.|?*+()[]{}/')
NOT_REPLY = re.compile(r'^\^\(\?!\[\\s\\S\]\{0,4000\}\(\?:§底座\|§推演\|hud-meta\|<details\)\)\[\\s\\S\]\{0,3000\}\(\?:(.*)\)$', re.S)
CRED_NEG = re.compile(r'^\^\(\?!\[\\s\\S\]\*(.+?)\)\[\\s\\S\]\*(.+)$', re.S)
BOOK_ALT = re.compile(r'^\(\?=\[\\s\\S\]\*(.+)\)\[\\s\\S\]\*\(\?:(.*)\)$', re.S)
ANCH_HEADS = ('纪元：', '(?:<br>|hud-meta">|纪元：|§底座｜)')
BARE_DATE = re.compile(r'^(?:月银纪|纷争纪|山铜纪|迷宫纪)\d+年·')


class Unsupported(Exception):
    pass


def esc(w):
    """纯词 → 正则里的字面（只转 ASCII 元字符，RE2 不认转义的汉字）。"""
    return ''.join('\\' + ch if ch in SPECIAL else ch for ch in w)


def cesc(ch):
    """方括号里的一个字。"""
    return '\\' + ch if ch in '\\]^-[' else ch


def group_end(s, i):
    """s[i] 是 '('，返回配对的 ')' 的下标。"""
    d, k = 0, i
    while k < len(s):
        c = s[k]
        if c == '\\':
            k += 2
            continue
        if c == '[':
            k = class_end(s, k) + 1
            continue
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
            if d == 0:
                return k
        k += 1
    raise Unsupported('括号不配：' + s[i:i + 40])


def class_end(s, i):
    j = i + 1
    if s[j:j + 1] == '^':
        j += 1
    if s[j:j + 1] == ']':
        j += 1
    while j < len(s) and s[j] != ']':
        j += 2 if s[j] == '\\' else 1
    if j >= len(s):
        raise Unsupported('方括号不配：' + s[i:i + 40])
    return j


def wrap(src):
    """要当一个整体接在别的东西前后时，带最外层 | 的包一层。"""
    return '(?:%s)' % src if len(SL.top_alts(src)) > 1 else src


# ---------------- 把简单的正则摊开成一串一串的字 ----------------
def expand_simple(s, limit=4000):
    """只认字面、转义、[…]、(?:…|…)、单个 ?。返回 [tuple(记号)]，记号 ('l', 字)｜('c', 方括号里的字)｜('e', 'd')。"""
    def seq(i, end):
        res, cur = [], [()]
        while i < end:
            c = s[i]
            if c == '|':
                res.extend(cur)
                cur = [()]
                i += 1
                continue
            if c == '(':
                j = group_end(s, i)
                if s.startswith('(?:', i):
                    sub = seq(i + 3, j)
                elif s.startswith('(?', i):
                    raise Unsupported('组：' + s[i:i + 12])
                else:
                    sub = seq(i + 1, j)
                i = j + 1
            elif c == '[':
                j = class_end(s, i)
                body = s[i + 1:j]
                if body.startswith('^'):
                    raise Unsupported('否定类')
                sub = [(('c', body),)]
                i = j + 1
            elif c == '\\':
                x = s[i + 1]
                if x in 'dsw':
                    sub = [(('e', x),)]
                elif x.isalnum():
                    raise Unsupported('转义 \\' + x)
                else:
                    sub = [(('l', x),)]
                i += 2
            elif c in '.^$*+{)':
                raise Unsupported('元字符 ' + c)
            else:
                sub = [(('l', c),)]
                i += 1
            if i < end and s[i] == '?':
                sub = sub + [()]
                i += 1
            elif i < end and s[i] in '*+{':
                raise Unsupported('量词')
            cur = [a + b for a in cur for b in sub]
            if len(cur) + len(res) > limit:
                raise Unsupported('摊开太多')
        res.extend(cur)
        return res
    return seq(0, len(s))


def class_chars(body):
    out, i = [], 0
    while i < len(body):
        c = body[i]
        if c == '\\':
            if body[i + 1].isalnum():
                raise Unsupported('类里的 \\' + body[i + 1])
            c = body[i + 1]
            i += 1
        if i + 2 < len(body) and body[i + 1] == '-':
            a, b = ord(c), ord(body[i + 2])
            if b - a > 60:
                raise Unsupported('类的范围太宽')
            out.extend(chr(x) for x in range(a, b + 1))
            i += 3
            continue
        out.append(c)
        i += 1
    return out


def expand_literals(s):
    """摊成字面的串（方括号逐字摊开）。"""
    out = []
    for q in expand_simple(s):
        strs = ['']
        for t in q:
            if t[0] == 'l':
                strs = [x + t[1] for x in strs]
            elif t[0] == 'c':
                cs = class_chars(t[1])
                strs = [x + c for x in strs for c in cs]
            else:
                raise Unsupported('\\' + t[1])
            if len(strs) > 4000:
                raise Unsupported('摊开太多')
        out.extend(strs)
    return list(dict.fromkeys(out))


def _tok_src(t):
    return esc(t[1]) if t[0] == 'l' else ('[%s]' % t[1] if t[0] == 'c' else '\\' + t[1])


def _tok_cls(t):
    return cesc(t[1]) if t[0] == 'l' else (t[1] if t[0] == 'c' else '\\' + t[1])


def not_prefix(seqs):
    """“后头不是这几样开头”的 RE2 写法（X(?!Y) 里的 Y 摊开以后传进来）。Y 能配空的返回 None（恒不成立）。"""
    if any(len(q) == 0 for q in seqs):
        return None
    root = {}
    for q in sorted(set(seqs), key=len):
        n = root
        for k, t in enumerate(q):
            if n.get(t, 0) is None:      # 更短的一样已经到头了
                break
            if k == len(q) - 1:
                n[t] = None
            else:
                n = n.setdefault(t, {})

    def build(n):
        lits = {t[1] for t in n if t[0] == 'l'}
        for t in n:
            if t[0] != 'l' and len(n) > 1:
                rx = re.compile('[%s]' % t[1] if t[0] == 'c' else '\\' + t[1])
                if any(rx.match(c) for c in lits):
                    raise Unsupported('前后顾里的支互相盖着')
        alts = ['$', '[^%s]' % ''.join(_tok_cls(t) for t in n)]
        for t, c in n.items():
            if c is not None:
                alts.append(_tok_src(t) + build(c))
        return '(?:%s)' % '|'.join(alts)
    return build(root)


def avoid_line(lits):
    """一行里（到换行为止）不含这几个字面串的 RE2 写法。靠“每个串的头一个字不在任何串的后头出现”这一条成立，
    不成立就把头一个字是它的那些串从前头削掉一个字再试（削过的串比原来短，挡得略宽）。返回 (正则, 实际挡的串)。"""
    keep = []
    for l in sorted(set(lits), key=len):
        if l and not any(k in l for k in keep):
            keep.append(l)
    if not keep:
        raise Unsupported('没有可挡的串')
    for _ in range(60):
        F = {l[0] for l in keep}
        clash = {ch for l in keep for ch in l[1:] if ch in F}
        if not clash:
            break
        nxt = []
        for l in keep:
            if l[0] in clash:
                if len(l) <= 3:
                    raise Unsupported('削不动：' + l)
                l = l[1:]
            nxt.append(l)
        keep = []
        for l in sorted(set(nxt), key=len):
            if not any(k in l for k in keep):
                keep.append(l)
    else:
        raise Unsupported('头字总是撞')
    F = sorted({l[0] for l in keep})
    trie = {}
    for l in keep:
        n = trie
        for k, ch in enumerate(l):
            if k == len(l) - 1:
                n[ch] = None
            else:
                n = n.setdefault(ch, {})
    fcls = ''.join(cesc(c) for c in F)
    free = '[^%s\\n]' % fcls

    def node(n):
        excl = fcls + ''.join(cesc(c) for c in n if c not in F)
        alts = ['[^%s\\n]%s*' % (excl, free)]
        for ch, sub in n.items():
            if sub is not None:
                alts.append(esc(ch) + node(sub))
        return '(?:%s)?' % '|'.join(alts)
    tops = [esc(c) + node(trie[c]) for c in F if trie[c] is not None]
    src = free + '*' + ('(?:%s)*' % '|'.join(tops) if tops else '')
    return src, keep


def safe_src(era, year_src, allow_null):
    """整段文字里，“纪元：<era>”只许跟着 year_src 里的年份（allow_null 再许旧凭证那一种），别的这一纪的锚一个也没有。"""
    e0, e1 = era[0], era[1]
    ns = '(?:[^纪元][^纪]*|元(?:[^纪：][^纪]*|：(?:[^纪%s][^纪]*)?)?)?' % e0
    ok = (['(?:%s)年' % year_src] if year_src else []) + (['｜'] if allow_null else [])
    seg = '(?:元：%s%s纪%s[^纪]*|%s)' % (e0, e1, ok[0] if len(ok) == 1 else '(?:%s)' % '|'.join(ok), ns) if ok else ns
    return '[^纪]*(?:纪%s)*' % seg


# ---------------- 年份集合 ↔ 正则 ----------------
def _split_ranges(lo, hi):
    stops = {hi}
    n = 1
    stop = int(str(lo)[:-n] + '9' * n) if len(str(lo)) >= n else hi + 1
    while lo <= stop <= hi:
        stops.add(stop)
        n += 1
        stop = int((str(lo)[:-n] if len(str(lo)) > n else '') + '9' * n)
    z = 1
    stop = (hi + 1) - (hi + 1) % (10 ** z) - 1
    while lo < stop <= hi:
        stops.add(stop)
        z += 1
        stop = (hi + 1) - (hi + 1) % (10 ** z) - 1
    return sorted(stops)


def _range_pat(a, b):
    sa, sb = str(a), str(b)
    assert len(sa) == len(sb), (a, b)
    pat, nd = '', 0
    for x, y in zip(sa, sb):
        if x == y:
            pat += x
        elif x != '0' or y != '9':
            pat += '[%s-%s]' % (x, y) if int(y) - int(x) > 1 else '[%s%s]' % (x, y)
        else:
            nd += 1
    return pat + ('' if not nd else ('\\d' if nd == 1 else '\\d{%d}' % nd))


def range_alts(lo, hi):
    out, start = [], lo
    for stop in _split_ranges(lo, hi):
        out.append(_range_pat(start, stop))
        start = stop + 1
    return out


_DIG = re.compile(r'^(.*?)((?:\\d(?:\{(\d+)\})?)?)$')


def ranges_src(ranges):
    alts = []
    for lo, hi in ranges:
        alts.extend(range_alts(lo, hi))
    # 同一个前缀、后头的 \d 个数连着的并成一支：[1-9]\d|[1-9]\d{2}|[1-9]\d{3} → [1-9]\d{1,3}
    out, i = [], 0
    while i < len(alts):
        m = _DIG.match(alts[i])
        pre, n = m.group(1), (0 if not m.group(2) else int(m.group(3) or 1))
        j, hi_n = i + 1, n
        while j < len(alts):
            m2 = _DIG.match(alts[j])
            n2 = 0 if not m2.group(2) else int(m2.group(3) or 1)
            if m2.group(1) != pre or n2 != hi_n + 1 or not pre:
                break
            hi_n = n2
            j += 1
        if j - i >= 2:
            out.append(pre + ('\\d?' if (n, hi_n) == (0, 1) else '\\d{%d,%d}' % (n, hi_n)))
        else:
            out.append(alts[i])
        i = j
    return '|'.join(out)


# ---------------- RE2 合不合法 ----------------
def re2_problems(pat):
    """Python 的 re 比 RE2 宽：这里拦掉 RE2 不认的写法。返回问题的单子，空的就是过了。"""
    out = []
    for m in re.finditer(r'\\(.)', pat, re.S):
        c = m.group(1)
        if ord(c) > 127:
            out.append('转义了非 ASCII 的字 \\' + c)
        elif c.isalnum() and c not in 'dDsSwWbBAznrtfvpPQEx0123456789':
            out.append('RE2 不认的转义 \\' + c)
        elif c in 'bB':
            out.append('\\b 在 RE2 里只认 ASCII 的词界')
        elif c in '123456789':
            out.append('反向引用')
    if '(?<' in pat or '(?P=' in pat or '(?#' in pat or '(?(' in pat:
        out.append('RE2 不认的组')
    if '[[' in pat or '\\u' in pat:
        out.append('可疑的类或 \\u')
    try:
        tree = _P.parse(pat)
    except Exception as ex:
        return out + ['编不过：%s' % ex]

    def walk(items):
        for op, av in items:
            if op in (_C.ASSERT, _C.ASSERT_NOT):
                out.append('前后顾')
                walk(av[1])
            elif op in (_C.GROUPREF, _C.GROUPREF_EXISTS):
                out.append('反向引用')
            elif op in (_C.MAX_REPEAT, _C.MIN_REPEAT, _C.POSSESSIVE_REPEAT):
                lo, hi, sub = av
                if op is _C.POSSESSIVE_REPEAT:
                    out.append('占有量词')
                if lo > 1000 or (hi is not _C.MAXREPEAT and hi > 1000):
                    out.append('重复过一千')
                walk(sub)
            elif op is _C.SUBPATTERN:
                walk(av[3])
            elif op is _C.BRANCH:
                for b in av[1]:
                    walk(b)
            elif op is _C.ATOMIC_GROUP:
                out.append('原子组')
                walk(av)
    walk(tree)
    return list(dict.fromkeys(out))


# ---------------- 题里的前后顾 ----------------
def _skip_group_close(s, i):
    d, k = 0, i
    while k < len(s):
        c = s[k]
        if c == '\\':
            k += 2
            continue
        if c == '[':
            k = class_end(s, k) + 1
            continue
        if c == '(':
            d += 1
        elif c == ')':
            if d == 0:
                return k
            d -= 1
        k += 1
    return len(s)


def _is_tail(s, q):
    i = q
    while i < len(s):
        c = s[i]
        if c == ')':
            i += 1
            if s[i:i + 1] in ('?', '*', '+', '{'):
                return False
            continue
        if c == '|':
            i = _skip_group_close(s, i)
            continue
        return False
    return True


def re2ify(src):
    """一支题里的前后顾改成 RE2 的写法。只改落在这一支末尾的；改不了抛 Unsupported。返回 (新写法, 改了几处)。"""
    if '(?<' in src:
        raise Unsupported('后顾')
    n, i, out = 0, 0, ''
    while True:
        m = re.search(r'\(\?[=!]', src[i:])
        if not m:
            return out + src[i:], n
        # 跳过落在转义、方括号里的假前后顾
        j = i + m.start()
        k = i
        inside = False
        while k < j:
            c = src[k]
            if c == '\\':
                k += 2
                continue
            if c == '[':
                e = class_end(src, k)
                if e >= j:
                    inside = True
                    break
                k = e + 1
                continue
            k += 1
        if inside or k > j:
            out += src[i:j + 3]
            i = j + 3
            continue
        e = group_end(src, j)
        body = src[j + 3:e]
        if not _is_tail(src, e + 1):
            raise Unsupported('前后顾不在一支的末尾')
        if src[j + 2] == '=':
            rep = '(?:%s)' % body
        else:
            rep = not_prefix(expand_simple(body))
            if rep is None:
                raise Unsupported('前后顾恒不成立')
        out += src[i:j] + rep
        i = e + 1
        n += 1


# ---------------- 一张卡的全集 ----------------
class Ctx:
    def __init__(self, card):
        self.card = card
        C = CARDS[card]
        self.era = C['name']
        self.cfg = C
        U = ([(self.era, '∅')] if C['null'] else []) + ([(self.era, '元')] if C['yuan'] else [])
        U += [(self.era, y) for y in range(C['years'][0], C['years'][1] + 1)]
        U += list(C['extra'])
        self.U = U
        self.ALL = frozenset(range(len(U)))
        self.idx = {u: i for i, u in enumerate(U)}
        lines = [('纪元：%s｜开局时段：' % e) if t == '∅' else ('纪元：%s%s年' % (e, t)) for e, t in U]
        self._starts, pos = [], 0
        for ln in lines:
            self._starts.append(pos)
            pos += len(ln) + 1
        self._text = '\n'.join(lines) + '\n'
        prim = [(i, t) for i, (e, t) in enumerate(U) if e == self.era and t not in ('∅',)]
        self._fstarts, pos = [], 0
        flines = []
        for i, t in prim:
            self._fstarts.append((pos, i))
            ln = '年份：%s' % t
            flines.append(ln)
            pos += len(ln) + 1
        self._ftext = '\n'.join(flines) + '\n'
        self._cache = {}
        self.null = frozenset(i for i, (e, t) in enumerate(U) if t == '∅')
        self.prim = frozenset(i for i, (e, t) in enumerate(U) if e == self.era)
        self.years = frozenset(i for i in self.prim if i not in self.null)

    known_tides = None      # fy_lore 填：这张卡里每条主线各幕的潮汐写法（主线名·幕）和各页的自由
    known_opens = None      # fy_lore 填：凭证“开局时段：”后头会写的东西

    def _tags_ok(self, used, lits):
        """削过的字面没有多挡：这张卡里含它的潮汐，都含原来要挡的某一个。"""
        K = self.known_tides or []
        return all(any(l in k for l in lits) for u in used for k in K if u in k)

    def short_tags(self, lits):
        """潮汐里要挡的几个字面（多半是同一条主线的几种幕），从它们共同的开头里往后挪起点，削成最短：
        起点那个字不在后头再出现（avoid_line 要这一条），这张卡里别的潮汐也不含削出来的这一截。"""
        K = self.known_tides
        if not K or not lits:
            return lits
        lcp = os.path.commonprefix(lits)
        for s in range(len(lcp) - 1, 0, -1):
            cand = [l[s:] for l in lits]
            if min(len(c) for c in cand) < 4 or any(lcp[s] in c[1:] for c in cand):
                continue
            if self._tags_ok(cand, lits):
                return cand
        return lits

    def avoid_tags(self, lits):
        """一行里不含这几样潮汐。先试削短的，削出来多挡了别的潮汐就照原样的字面建；还不成抛 Unsupported。"""
        last = None
        for cand in (self.short_tags(lits), lits):
            try:
                av, used = avoid_line(cand)
            except Unsupported as ex:
                last = ex
                continue
            if self.known_tides is None or self._tags_ok(used, lits):
                return av
            last = Unsupported('削短以后会多挡别的主线')
        raise last

    def short_open(self, l):
        """凭证里要挡的开局时段，削成最短的开头。"""
        K = self.known_opens
        if not K:
            return l
        for n in range(3, len(l)):
            t = l[:n]
            if all((not k.startswith(t)) or k.startswith(l) for k in K):
                return t
        return l

    def eval_anchor(self, src):
        """一支认锚的正则，在全集里中哪些。"""
        key = ('a', src)
        if key not in self._cache:
            rx = re.compile(src)
            hit = set()
            for m in rx.finditer(self._text):
                hit.add(bisect.bisect_right(self._starts, m.start()) - 1)
            self._cache[key] = frozenset(hit)
        return self._cache[key]

    def eval_free(self, src):
        """“年份：(…)(?!\\d)”那一截，中哪些年份（凭证里年份那一格跟纪元的年份是同一个数）。"""
        key = ('f', src)
        if key not in self._cache:
            rx = re.compile(src)
            ps = [p for p, _ in self._fstarts]
            hit = set()
            for m in rx.finditer(self._ftext):
                hit.add(self._fstarts[bisect.bisect_right(ps, m.start()) - 1][1])
            self._cache[key] = frozenset(hit)
        return self._cache[key]

    # ---- 集合写回正则 ----
    def years_src(self, S):
        """S 里这一纪带年份的那些 → 年份那一截的正则（不带“年”）。碰到 ymax 的那一段当“往上都算”，写到五位数。全都在就写 \\d+。"""
        toks = [self.U[i][1] for i in sorted(S & self.years)]
        if not toks:
            return ''
        yuan = ['元'] if '元' in toks else []
        if len(toks) == len(self.years):
            return '|'.join(yuan + ['\\d+'])
        ranges = []
        for y in (t for t in toks if isinstance(t, int)):
            if ranges and ranges[-1][1] == y - 1:
                ranges[-1][1] = y
            else:
                ranges.append([y, y])
        if ranges and ranges[-1][1] == self.cfg['ymax']:
            ranges[-1][1] = 99999
        return '|'.join(yuan + ([ranges_src(ranges)] if ranges else []))

    def _extra_segs(self, S):
        return ['%s%s年' % self.U[i] for i in sorted(S - self.prim)]

    def gate(self, S, neg=None):
        """集合 S（加上行内的否定 neg）写成认锚的正则。S 是全集而且没有否定，返回 None（恒真）。返回 (正则或 None, 提醒单子)。
        neg：og 不许是凭证（黑名单里有泛的“开局时段：”）；lits 这一行不许有的字面（“开局时段：某条主线”只管凭证，别的是潮汐里的主线和幕，只管回复）；
        date {下标: [年后头不许接的字]}。锚那一行的样子：回复是“纪元：某纪N年·季…· 潮汐 ·…”，凭证是“纪元：某纪N年｜开局时段：…”。"""
        notes = []
        neg = neg or {}
        og, lits, dates = bool(neg.get('og')), list(neg.get('lits') or []), {i: s for i, s in (neg.get('date') or {}).items() if i in S}
        if S == self.ALL and not og and not lits and not dates:
            return None, notes
        e = self.era
        null = bool(S & self.null)
        if not og and not lits and not dates:
            segs = []
            if S >= self.prim:
                segs.append(e)
            else:
                ysrc = self.years_src(S)
                if ysrc and null:
                    segs.append('%s(?:(?:%s)年|｜开局时段：)' % (e, ysrc))
                elif ysrc:
                    segs.append('%s%s年' % (e, wrap(ysrc)))
                elif null:
                    segs.append('%s｜开局时段：' % e)
            segs += self._extra_segs(S)
            if not segs:
                return '', notes
            src = '纪元：' + (segs[0] if len(segs) == 1 else '(?:%s)' % '|'.join(segs))
            if self.eval_anchor(src) != S:
                notes.append('年份正则写回去对不上集合')
            return src, notes
        tags = list(dict.fromkeys(l for l in lits if not l.startswith('开局时段：')))
        opens = list(dict.fromkeys(self.short_open(l[len('开局时段：'):]) for l in lits if l.startswith('开局时段：') and len(l) > len('开局时段：')))
        open_np = ''
        if opens:
            try:
                open_np = not_prefix([tuple(('l', ch) for ch in s) for s in opens])
            except Unsupported as ex:
                notes.append('凭证里某条主线的黑名单没建成（%s），没挡' % ex)
        av = None
        if tags:
            try:
                av = self.avoid_tags(tags)
            except Unsupported as ex:
                notes.append('潮汐里某条主线的黑名单没建成（%s），只留年份' % ex)
        # “年”后头分两路：凭证（紧跟着 ｜）和回复。日期的否定只管回复（凭证上没有日期），而且不许它把 ｜ 吃掉
        cred = None if og else ('｜' + ('开局时段：' + open_np if open_np else ''))
        rest = ('(?:[^｜\\n]%s)?(?:\\n|$)' % av) if av is not None else ('(?:[^｜]|$)' if (og or opens or tags) else '')

        def tail(np_date):
            if np_date is None and not (og or opens or tags):
                return ''
            r = (np_date or '') + rest
            return r if cred is None else '(?:%s|%s)' % (r, cred)
        year_segs = []
        ysrc = self.years_src(frozenset(i for i in S if i not in dates))
        if ysrc:
            year_segs.append('%s%s年%s' % (e, wrap(ysrc), tail(None)))
        for i, sfx in dates.items():
            try:
                np_ = not_prefix([tuple(('l', ch) for ch in x) for x in sfx] + [(('l', '｜'),)])
            except Unsupported as ex:
                np_ = None
                notes.append('日期的黑名单没建成（%s），整年不醒' % ex)
            if np_:
                year_segs.append('%s%s年%s' % (e, self.U[i][1], tail(np_)))
        year_segs += [x + tail(None) for x in self._extra_segs(S)]
        alts = []
        if year_segs:
            alts.append('纪元：' + (year_segs[0] if len(year_segs) == 1 else '(?:%s)' % '|'.join(year_segs)))
        if null and not og:
            alts.append('纪元：%s｜开局时段：%s' % (e, open_np))
        return '|'.join(alts), notes

    @staticmethod
    def alts_of(w):
        """一个词拆成支：[(是不是正则, 支)]。“开局时段：(?:甲|乙)”再拆成“开局时段：甲”“开局时段：乙”，里头自己报年份的那一支才认得出来。"""
        p = SL.parse(w)
        if not p:
            return [(False, w)]
        out = []
        for a in SL.top_alts(p[0]):
            h = '开局时段：(?:'
            m = re.match(r'^(纪元：[^(\\\[|]+纪)\(\?:', a)
            if a.startswith(h) and '｜年份：' in a and group_end(a, len(h) - 3) == len(a) - 1:
                out.extend((True, '开局时段：' + x) for x in SL.top_alts(a[len(h):-1]))
            elif m and '年·' in a and group_end(a, m.end() - 3) == len(a) - 1:
                out.extend((True, m.group(1) + x) for x in SL.top_alts(a[m.end():-1]))
            else:
                out.append((True, a))
        return out

    # ---- 一支归哪一类 ----
    def classify(self, is_re, a):
        src = a if is_re else esc(a)
        if is_re and BARE_DATE.match(a):
            # 源稿里漏了“纪元：”的带日期的锚（山铜纪661年·(?:春|夏|秋)）：照带头的算
            return ('D', src, self._parse_date('纪元：' + a))
        if a.startswith(ANCH_HEADS):
            if '年·' in a:
                return ('D', src, self._parse_date(a))
            return ('A', src, self.eval_anchor(src))
        if a.startswith('开局时段：'):
            if a == '开局时段：':
                return ('OG', src, None)
            if '｜年份：' in a:
                k = src.index('年份：')
                return ('OF', src, self.eval_free(src[k:]))
            return ('OS', src, None)
        return ('P', src, None)

    def _parse_date(self, a):
        """带日期的锚摊开：[(全集里的下标 或 None, 年后头的字)]。摊不开返回 None。"""
        head = next(h for h in ANCH_HEADS if a.startswith(h))
        try:
            lits = expand_literals(a[len(head):])
        except Unsupported:
            return None
        out = []
        for s in lits:
            m = re.match(r'^(.+?纪)(元|\d+)年(.*)$', s, re.S)
            if not m:
                return None
            tok = m.group(2) if m.group(2) == '元' else int(m.group(2))
            out.append((self.idx.get((m.group(1), tok)), m.group(3)))
        return out

    # ---- 一条条目 ----
    def convert(self, e, foreign=False):
        """返回 ([(钥匙, 范围位), …], info)。info：kinds（用到哪几样改法）、flags（要人看的）、skip（没进卡的缘故）。"""
        info = dict(kinds=set(), flags=[], skip=None)
        if e.get('contentMethod') == 'weighted' or 'content' not in e:
            info['skip'] = '加权条目（风月没有对应的写法）'
            return [], info
        words = [w for w in e.get('triggerWords') or [] if w]
        if not words:
            info['skip'] = '没有触发词'
            return [], info
        typ = e.get('triggerWordsType') or 'OR'
        bl = [w for w in e.get('blackListWords') or [] if w]
        rng = e.get('triggerRange') or []
        full = (2 if 'user' in rng else 0) | (4 if 'assistant' in rng else 0)
        parsed = [SL.parse(w) for w in words]
        nr = [bool(p and NOT_REPLY.match(p[0])) for p in parsed]
        jobs = []
        if any(nr):
            if typ != 'OR':
                info['skip'] = '只认玩家那一支落在“同时满足”里，拆不了'
                return [], info
            info['kinds'].add('拆两条')
            uw = [('/' + NOT_REPLY.match(p[0]).group(1) + '/') if f else w for w, p, f in zip(words, parsed, nr)]
            aw = [w for w, f in zip(words, nr) if not f]
            if full & 2:
                jobs.append((2, uw))
            if full & 4 and aw:
                jobs.append((4, aw))
        else:
            jobs.append((full, words))
        outs = []
        for region, ws in jobs:
            try:
                key = self._key(ws, typ, bl, info, foreign)
            except Unsupported as ex:
                info['skip'] = '转不了：%s' % ex
                return [], info
            if key is None:
                continue
            bad = re2_problems(key)
            if bad:
                info['skip'] = 'RE2 不认：' + '、'.join(bad)
                return [], info
            outs.append((key, region))
        if not outs and not info['skip']:
            info['skip'] = '这张卡里醒不了（年份窗空了）'
        return outs, info

    def _bl(self, bl, info):
        BA, neg, vac = set(), dict(og=False, lits=[], date={}), []
        for w in bl:
            for is_re, a in self.alts_of(w):
                m = CRED_NEG.match(a) if is_re else None
                if m:
                    vac.append((m.group(1), m.group(2)))
                    continue
                k, src, v = self.classify(is_re, a)
                if k == 'A':
                    BA |= v
                elif k == 'OF':
                    BA |= v
                    info['kinds'].add('自报年份并进年份窗')
                elif k == 'OG':
                    neg['og'] = True
                elif k in ('OS', 'P'):
                    try:
                        neg['lits'].extend(expand_literals(src))
                    except Unsupported as ex:
                        info['flags'].append('黑名单这一支摊不开，没挡（%s）：%s' % (ex, a[:60]))
                elif k == 'D':
                    if v is None:
                        info['flags'].append('带日期的黑名单摊不开，没挡：%s' % a[:60])
                        continue
                    for i, sfx in v:
                        if i is None:
                            continue
                        if sfx == '':
                            BA.add(i)
                        else:
                            neg['date'].setdefault(i, []).append(sfx)
        neg['date'] = {i: s for i, s in neg['date'].items() if i not in BA}
        return frozenset(BA), neg, vac

    def _word(self, w, info):
        """一个触发词 → (锚的集合 或 None, [题的正则…], [(集合, 书名的正则)…])。"""
        p = SL.parse(w)
        A, Ps, books = None, [], []
        if p and p[0].startswith('^(?:(?=[\\s\\S]*'):
            inner = p[0][len('^(?:'):-1]
            for alt in SL.top_alts(inner):
                m = BOOK_ALT.match(alt)
                if not m:
                    raise Unsupported('书目那一种写法里有一支不认得')
                books.append((self.eval_anchor(m.group(1)), m.group(2)))
            info['kinds'].add('书目')
            return A, Ps, books
        for is_re, a in self.alts_of(w):
            k, src, v = self.classify(is_re, a)
            if k == 'A':
                A = v if A is None else (A | v)
            else:
                if k == 'D':
                    info['kinds'].add('带日期的触发')
                s2, n = re2ify(src)
                if n:
                    info['kinds'].add('末尾的前后顾')
                Ps.append(s2)
        return A, list(dict.fromkeys(Ps)), books

    def _both(self, g, p, info=None):
        if len(g) > LONG_GATE and len(p) > LONG_GATE:
            g, p = (g, p) if g.startswith('纪元：') or '纪元：' in g[:12] else (p, g)
        if len(g) > LONG_GATE:
            # 锚那一截带着一长串行内的否定，写两遍太长：只写“锚在前、题在后”。锚在一条消息的头一行（§底座、凭证头一行），一条消息之内题总在它后头
            if info is not None:
                info['kinds'].add('只写锚在前那一支')
            return '%s[\\s\\S]*%s' % (wrap(g), wrap(p))
        return '%s[\\s\\S]*%s|%s[\\s\\S]*%s' % (wrap(g), wrap(p), wrap(p), wrap(g))

    def _key(self, words, typ, bl, info, foreign=False):
        # foreign：文件夹是别纪的条目。认得到这张卡的锚才带（活过纪元交界的人），认不到的返回 None
        BA, neg, vac = self._bl(bl, info)
        has_neg = bool(neg['og'] or neg['lits'] or neg['date'])
        W = [self._word(w, info) for w in words]
        okU = self.ALL - BA
        og_only = dict(og=True, lits=[], date={}) if neg['og'] else None

        def gate(S, ng='full'):
            g, notes = self.gate(frozenset(S), (neg if has_neg else None) if ng == 'full' else og_only)
            info['flags'].extend(notes)
            if g:
                info['kinds'].add('年份窗')
                if has_neg and ng == 'full':
                    info['kinds'].add('行内否定')
            return g

        def tagged(P, anchored_side):
            """潮汐里的页名、主线名这一类题（跟锚在同一行、在年份后头）过一遍黑名单：前头接上“黑名单以外的年份”。黑名单管不着就原样。"""
            if not P or not (BA or has_neg):
                return list(P)
            self_anch = [x for x in P if x.startswith(ANCH_HEADS)]      # 自己带着“纪元：”的（带日期的触发）
            tags = [x for x in P if x not in self_anch]
            out = list(self_anch)
            if tags:
                nlits = [l for l in neg['lits'] if not l.startswith('开局时段：')]
                loose = bool(neg['date'])
                if nlits:
                    try:
                        tl = list(dict.fromkeys(x for t in tags for x in expand_literals(t)))
                        rel = [n for n in nlits if any(n.startswith(t) for t in tl)]
                        if len(rel) < len(nlits) and any(t in n for n in nlits if n not in rel for t in tl):
                            raise Unsupported('黑名单的潮汐夹着它')
                        loose = loose or len(rel) < len(nlits)
                        new = []
                        for t in tl:
                            sfx = [n[len(t):] for n in rel if n.startswith(t)]
                            if any(x == '' for x in sfx):
                                continue            # 这个潮汐整个在黑名单里
                            new.append(esc(t) + (not_prefix([tuple(('l', ch) for ch in x) for x in sfx]) if sfx else ''))
                        tags = new
                        info['kinds'].add('潮汐那一路照延长挡')
                    except Unsupported:
                        loose = True
                if loose:
                    info['kinds'].add('潮汐那一路只过年份和凭证的黑名单')
                if not tags:
                    return out
                g = gate(okU - frozenset(neg['date']), 'og')
                if g is None:
                    out.extend(tags)
                elif g:
                    out.append('%s%s%s' % (wrap(g), '[^\\n]*' if anchored_side else '[\\s\\S]*', wrap('|'.join(tags))))
                    if not anchored_side:
                        info['flags'].append('没有锚的词带着年份黑名单：只认“锚在前、题在后”')
            return out

        def overlap(tags, topics):
            """题落在潮汐的字里头的（主线名里带着人名）：两个词中的是同一处，“甲在前乙在后”两支都认不到，把那个潮汐单列一支。"""
            T, Pl = [], []
            for src, dst in ((tags, T), (topics, Pl)):
                for a in src:
                    try:
                        dst.extend(expand_literals(a))
                    except Unsupported:
                        pass
            return [esc(t) for t in dict.fromkeys(T) if any(p and p in t for p in Pl)]

        for x, y in vac:
            # “没有某纪的锚、又有某词”的黑名单：这张卡里带锚的消息都有这一纪的锚，挡不到；只有玩家裸打的那一句碰得上
            if self.eval_anchor(x) != self.ALL and self.card != 'maze':
                info['flags'].append('“没有某纪的锚又有某词”的黑名单没处放：%s／%s' % (x[:30], y[:20]))

        alts, always = [], False
        if typ == 'AND':
            if len(W) != 2:
                raise Unsupported('同时满足不是两个词')
            (A1, P1, B1), (A2, P2, B2) = W
            if B1 or B2:
                raise Unsupported('书目写法落在同时满足里')
            if foreign and not ((A1 is not None and (A1 - BA)) or (A2 is not None and (A2 - BA))):
                return None
            g1 = gate(A1 - BA) if A1 is not None and (A1 - BA) else ''
            g2 = gate(A2 - BA) if A2 is not None and (A2 - BA) else ''
            t1, t2 = g1 is None, g2 is None
            if A1 is not None and A2 is not None and ((A1 & A2) - BA):
                g12 = gate((A1 & A2) - BA)
                if g12 is None:
                    always = True
                elif g12:
                    alts.append(g12)
            if t1 and t2:
                always = True
            elif t1:
                # 头一个词在这张卡里恒真（认这一纪的那一把钥匙）：只剩第二个词
                alts.extend(([g2] if g2 else []) + P2)
                info['kinds'].add('纪元钥匙拿掉')
            elif t2:
                alts.extend(([g1] if g1 else []) + P1)
                info['kinds'].add('纪元钥匙拿掉')
            else:
                # (g1 ∨ P1) ∧ (g2 ∨ P2)：g1∧g2 上面写过了；g1∧P2、P1∧P2 并成 (g1|P1')∧P2；P1∧g2 另写
                k = 0 if (A1 is not None or A2 is None) else 1          # 带锚的那个词，它的题是潮汐里的东西
                Pa, Pb = (P1, P2) if k == 0 else (P2, P1)
                ga, gb = (g1, g2) if k == 0 else (g2, g1)
                left = ([ga] if ga else []) + tagged(Pa, (A1 if k == 0 else A2) is not None)
                if left and Pb:
                    alts.append(self._both('|'.join(left), '|'.join(Pb), info))
                    info['kinds'].add('两支')
                ov = overlap(Pa, Pb)
                if ov:
                    alts.extend(tagged(ov, (A1 if k == 0 else A2) is not None))
                    info['kinds'].add('题落在潮汐里的单列一支')
                if gb and Pa:
                    alts.append(self._both(gb, '|'.join(Pa), info))
                    info['kinds'].add('两支')
        else:
            A, P, books = None, [], []
            for a, p, b in W:
                if a is not None:
                    A = a if A is None else (A | a)
                P.extend(p)
                books.extend(b)
            P = list(dict.fromkeys(P))
            if foreign and not (A is not None and (A - BA)) and not any(S - BA for S, _ in books):
                return None
            if A is not None and (A - BA):
                g = gate(A - BA)
                if g is None:
                    always = True
                elif g:
                    alts.append(g)
            bygate = collections.OrderedDict()
            for S, titles in books:
                if S - BA:
                    bygate.setdefault(gate(S - BA), []).append(titles)
            for g, ts in bygate.items():
                t = '|'.join(ts)
                if g is None:
                    alts.append(t)
                    info['kinds'].add('纪元钥匙拿掉')
                elif g:
                    alts.append(self._both(g, t, info))
                    info['kinds'].add('两支')
            if P:
                psrc = '|'.join(P)
                if not (BA & self.prim) and not has_neg:
                    alts.append(psrc)
                    if BA:
                        info['flags'].append('黑名单里纪元交界那一个月的锚（%s）没挡' % '、'.join('%s%s年' % self.U[i] for i in sorted(BA - self.prim)))
                elif not (self.prim - BA):
                    pass        # 这张卡里的锚全在黑名单里：带锚的消息里醒不了，不带（日里那边只有玩家裸打那一句漏得进来）
                elif has_neg and A is not None:
                    # 这个词自己带着锚，别的支是潮汐里的页名主线名：照同一行处理
                    alts.extend(tagged(P, True))
                elif not has_neg:
                    if BA - self.prim:
                        info['flags'].append('黑名单里纪元交界那一个月的锚（%s）没挡' % '、'.join('%s%s年' % self.U[i] for i in sorted(BA - self.prim)))
                    S = self.prim - BA
                    ysrc, nul = self.years_src(S), bool(S & self.null)
                    sf = safe_src(self.era, ysrc, nul)
                    # 题本身就是这一纪的名字的（“迷宫纪”）：它会去配“纪元：”后头那三个字，把不许的锚拆散了混过去。
                    # 这样的题前头不许紧挨着“：”；许的那种锚里的它，另列一支（整个锚算一支）。
                    P2, stole = [], False
                    for x in P:
                        if re.match(x, self.era + '5年｜开局时段：'):
                            P2.append('(?:^|[^：])' + wrap(x))
                            stole = True
                        else:
                            P2.append(x)
                    if stole and ysrc:
                        P2.append('纪元：%s(?:%s)年' % (self.era, ysrc))
                    alts.append('^%s(?:%s)%s$' % (sf, '|'.join(P2), sf))
                    info['kinds'].add('整段没有不许的锚')
                else:
                    g = gate(okU)
                    if g:
                        alts.append(self._both(g, psrc, info))
                    info['flags'].append('没有锚要求的题带着行内黑名单：只在带锚的消息里醒')
        if always:
            info['kinds'].add('恒醒')
            return ALWAYS
        alts = list(dict.fromkeys(a for a in alts if a))
        if not alts:
            return None
        return '|'.join(alts)


# ---------------- 自测 ----------------
def selftest():
    import random
    rnd = random.Random(7)
    # 年份范围
    for _ in range(3000):
        a = rnd.choice([1, 2, rnd.randint(1, 1200), rnd.randint(1, 99999)])
        b = rnd.choice([a, 99999, rnd.randint(a, min(99999, a * 12 + 5))])
        rx = re.compile('^(?:%s)$' % '|'.join(range_alts(a, b)))
        for y in {a, b, a - 1, b + 1, (a + b) // 2, rnd.randint(1, 99999), rnd.randint(max(1, a - 30), b + 30)}:
            if 1 <= y <= 99999:
                assert bool(rx.match(str(y))) == (a <= y <= b), (a, b, y, rx.pattern)
    # 一行里不含
    for lits in (['开局时段：', '万兽·镜中石瞳·一幕', '万兽·镜中石瞳·二幕', '万兽·镜中石瞳·幕间'], ['七城的年月·开岭·一幕', '开局时段：开岭', '开局时段：门楣'],
                 ['万兽·万神坛前·一幕', '诸国·神渡之盟·三幕'], ['黎明的年月·白杉堡·一幕', '黎明的年月·白杉堡·幕间', '开局时段：白杉堡']):
        src, used = avoid_line(lits)
        assert not re2_problems(src), re2_problems(src)
        rx = re.compile('^(?:%s)$' % src)
        pool = sorted({c for l in lits for c in l} | set('甲乙·｜ a'))
        for _ in range(6000):
            s = ''.join(rnd.choice(pool) for _ in range(rnd.randint(0, 14)))
            if rnd.random() < 0.5:
                k = rnd.randint(0, len(s))
                l = rnd.choice(lits)
                s = s[:k] + l[:rnd.randint(1, len(l))] + s[k:]
            assert bool(rx.match(s)) == (not any(u in s for u in used)), (lits, s, src)
    # 后头不是
    for body in ('银', '\\d', '[<｜：\\s]', '巴尔|纪', '红园|花酒|谷|拱门|的藤', '[：:｜展对]|</', ' ?LVL', '元年'):
        np_ = not_prefix(expand_simple(body))
        assert not re2_problems(np_), (body, np_)
        a, b = re.compile('甲(?!%s)' % body), re.compile('甲' + np_)
        pool = sorted(set(re.sub(r'[\\\[\]|?()]', '', body)) | set('甲乙1 <'))
        for _ in range(4000):
            s = ''.join(rnd.choice(pool) for _ in range(rnd.randint(0, 7)))
            assert bool(a.search(s)) == bool(b.search(s)), (body, s, np_)
    # 整段没有不许的锚
    sf = safe_src('迷宫纪', '100[1-9]|10[1-9]\\d|1[1-9]\\d\\d', False)
    assert not re2_problems('^%s(?:甲)%s$' % (sf, sf))
    rx = re.compile('^%s(?:甲)%s$' % (sf, sf))
    bad = re.compile(r'纪元：迷(?!宫纪(?:100[1-9]|10[1-9]\d|1[1-9]\d\d)年)')
    pool = list('纪元：迷宫年甲乙15｜') + ['纪元：迷宫纪1001年', '纪元：迷宫纪5年', '纪元：迷宫纪｜开局时段：', '纪元：迷宫纪1000年', '纪元：', '纪元：迷宫纪1500年']
    for _ in range(40000):
        s = ''.join(rnd.choice(pool) for _ in range(rnd.randint(0, 9)))
        want = ('甲' in s) and not bad.search(s)
        assert bool(rx.search(s)) == want, (s, want)
    print('fy_gate 自测过了')


if __name__ == '__main__':
    selftest()
