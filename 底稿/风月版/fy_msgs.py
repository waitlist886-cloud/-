#!/usr/bin/env python3
# 风月版：切卡和对账共用的“消息”。一张卡的局里会出现的凭证、回复底座，和逐年扫的那一串。
#   凭证的写法全从 slim_card.cases 来（外壳 shell.js 的 credential() 照它写），本体改了凭证的样子这里跟着变。
#   回复的底座照骨架写全：§底座｜纪元：某纪N年·季·月·旬日 · 钟点 · 地点 · 潮汐 · 防抢话 开 · 档位 长。
import bisect
import os
import re
import sys

sys.dont_write_bytecode = True
import fy_gate as G   # noqa: E402

SL = G.SL
ROOT = G.ROOT
REPLY = '§底座｜纪元：%s%s·春·花信月·中旬三日 · 21:40 夜里 · %s · %s · 防抢话 开 · 档位 长\n§环境｜晴\n§正文｜某地\n正文。'
REST = '\n\n命途已确认，请记录我的《奥尔德兰》角色建档：\n\n【一·灵魂形态】\n降临之魂 · 身穿（连人带身跌入）\n\n开始游戏。'
ACTS = ('一幕', '二幕', '三幕', '幕间', '收束')
SWEEP = dict(moon=(1, 10100), strife=(1, 11050), bronze=(2, 960), pre=(2, 1000), now=None)    # 此刻那一张只扫 1001 年那一段（MAZE_1001）
MAZE_1001 = (1001, 1030)
_YR = re.compile(r'纪元：\S+?纪(元|\d+)年')


def title_of(e):
    c = e.get('content') or ((e.get('contents') or [{}])[0].get('content') or '')
    return c.lstrip().split('\n', 1)[0][:60]


def literals(e):
    """条目触发词里能直接写进一句话的字，去掉认纪元、开局、年份的。照 make_dlc.literals，添了一样：
    一支摊得成字面的（机兵(?:回炉|进炉)）拿摊开的整串（机兵回炉、机兵进炉），摊不成的照旧拆到元字符为止。"""
    out = []
    for w in e.get('triggerWords') or []:
        p = SL.parse(w)
        if not p:
            runs = [w]
        else:
            runs = []
            for alt in SL.top_alts(p[0]):
                try:
                    full = G.expand_literals(alt)
                    if len(full) > 12:
                        raise G.Unsupported('太多')
                    runs.extend(full)
                except G.Unsupported:
                    body = re.sub(r'\\.', '\x01', alt)
                    runs.extend(re.split(r'[\\^$.|?*+()\[\]{}/\x01]', body))
        for r in runs:
            r = r.strip()
            if len(r) >= 2 and re.search(r'[一-鿿]', r) and not re.search('纪元|开局|年份|底座|§推演|§预载', r):
                out.append(r)
    seen, res = set(), []
    for r in sorted(out, key=len, reverse=True):
        if r not in seen:
            seen.add(r)
            res.append(r)
    return res[:40]


def samples(e):
    """摊不成字面、中间隔着 .{0,N} 的支（这一段旅伴之间：两个人名挨着），拼几句真配得上的话（甲和乙）。
    对账时另起一行接在消息后头；不拿去写底座的地点那一格（两个人名挨着的句子不会写在地点里）。"""
    out = []
    for w in e.get('triggerWords') or []:
        p = SL.parse(w)
        if not p:
            continue
        for alt in SL.top_alts(p[0]):
            if '.{0,' not in alt:
                continue
            try:
                G.expand_literals(alt)
                continue
            except G.Unsupported:
                pass
            s = re.sub(r'\(\?![^()]*\)', '', alt)
            s = re.sub(r'\(\?:\^\|\[\^[^\]]*\]\)', '', s)
            s = re.sub(r'\.\{0,\d+\}', '和', s)
            try:
                full = G.expand_literals(s)
            except G.Unsupported:
                continue
            out.extend(x for x in full[1:5] + full[-1:] if SL._hit([w], 'OR', x))
    return list(dict.fromkeys(out))


def topic_words(e):
    """对账时拿哪几个词里的字：“同时满足”的条目只拿不带锚的那个词（带锚那个词里别的支是潮汐的页名主线名，真消息里只会出现在底座上），别的条目全拿。"""
    ws = e.get('triggerWords') or []
    if (e.get('triggerWordsType') or 'OR') == 'AND' and len(ws) == 2:
        a, b = ('纪元：' in ws[0]), ('纪元：' in ws[1])
        if a != b:
            return [ws[1] if a else ws[0]]
    return ws


def topic_literals(e):
    """对账时往消息里接的字。"""
    return literals(dict(triggerWords=topic_words(e)))


def topic_samples(e):
    return samples(dict(triggerWords=topic_words(e)))


_TIDES = None


def is_tide(l):
    """这个字是不是潮汐里的一截（页·主线·、页·主线、页·）：四张卡里哪一条主线的潮汐以它开头。
    潮汐只写在回复底座那一行上（凭证里是“主线「页·主线」”），玩家不会单打它，对账的时候不拿它当话题另起一行接在消息后头；
    它醒不醒由“原样的凭证和回复”那一组来比。"""
    global _TIDES
    if _TIDES is None:
        _TIDES = sorted({t for c in G.CARDS for t in Msgs(c).tides()})
    s = l.rstrip('·')
    return '·' in l and bool(s) and any(t.startswith(s) for t in _TIDES)


_PAGES = None
_ACT_END = re.compile(r'·第?(?:一幕|二幕|三幕|幕间|收束|自由)$')


def tide_like(l):
    """比 is_tide 宽一层（11-25 拆迷宫纪两张时添的，只给 can_wake 用）：触发词里写的潮汐常带着变体（探井的年月·寻人·第一幕、垂暮和平·自由），
    is_tide 认不全。头一截是四张卡里哪一页的页名，或者末尾是“·某幕”“·收束”“·自由”的，都算潮汐。“名·姓”那种不算（头一截不是页名）。"""
    global _PAGES
    if _PAGES is None:
        _PAGES = {t.split('·')[0] for c in G.CARDS for t in Msgs(c).tides()}
    return is_tide(l) or ('·' in l and (l.split('·')[0] in _PAGES or bool(_ACT_END.search(l))))


def rili_woke(e, text, role):
    """日里的判法：这一条消息在扫的范围里，触发成立，黑名单一个不中。"""
    if role not in (e.get('triggerRange') or []):
        return False
    return SL._hit(e.get('triggerWords'), e.get('triggerWordsType'), text) and not SL._hit(e.get('blackListWords'), e.get('blackListWordsType'), text)


def year_dep(e):
    """触发或黑名单里有没有认年份的。"""
    for w in (e.get('triggerWords') or []) + (e.get('blackListWords') or []):
        if re.search(r'(?:纪元：|年份：)[^|/]*?(?:\d|\\d|元)', w):
            return True
    return False


class Msgs:
    def __init__(self, card):
        self.card = card
        C = G.CARDS[card]
        era = self.era = C['name']
        book = C['book']
        self.main = []          # (名, 谁说的, 文字)：每条主线的凭证、五种幕的回复，自己报年份的凭证
        lines, free = [], None
        for cera, name, old, new, reply in SL.cases(ROOT):
            if cera == era and C['lines']:
                m = _YR.search(new)
                y = 1 if m.group(1) == '元' else int(m.group(1))
                self.main.append(('凭证·' + name, 'user', new))
                if reply:
                    lines.append((y, name))
                    yt = SL.year_text(book, y)
                    for act in ACTS:
                        self.main.append(('回复·%s·%s' % (name, act), 'assistant', REPLY % (era, yt, '某地', '%s·%s' % (name, act))))
                    self.main.append(('回复·%s·简' % name, 'assistant', reply))
                else:
                    mm = re.search(r'开局时段：(.+?)｜年份：', new)
                    if mm:
                        free = mm.group(1)
            elif cera == '迷宫纪1001' and C['has1001']:
                self.main.append(('凭证·1001（没有纪元那一行）', 'user', old))
        if C['has1001']:
            self.main.append(('凭证·1001（带纪元那一行）', 'user', '纪元：迷宫纪1001年｜开局时段：阿卡迪亚' + REST))
            self.main.append(('回复·1001', 'assistant', REPLY % (era, '1001年', '晨曦帝国·金鸢城·外城', '第一兆·魔兽离巢·起潮')))
        self._names = [n for _, n in lines]
        self._year = {n: y for y, n in lines}
        self._creds = [(m.group(1), t) for _, role, t in self.main if role == 'user' for m in [re.match(r'纪元：[^｜\n]*｜开局时段：([^｜\n]+)', t)] if m]
        self._opens = [o for o, _ in self._creds]
        lines.sort()
        self._ly = [y for y, _ in lines]
        self._lp = [n.split('·')[0] for _, n in lines]
        self.free = free
        self.book = book
        self.has1001 = C['has1001']
        self._sweep = None

    def tides(self):
        """这张卡里潮汐那一段会写的：每条主线的五种幕，每一页的自由。"""
        out = []
        for name in self._names:
            out += ['%s·%s' % (name, a) for a in ACTS]
        out += ['%s·自由' % p for p in dict.fromkeys(self._lp)]
        return out

    def opens(self):
        return list(self._opens)

    def creds(self):
        """这张卡认得的凭证：[(开局时段, 整份凭证的字)]。"""
        return list(self._creds)

    def loc_replies(self):
        """地点那一格留空的回复：[(名, 写法)]，写法 % 地点 就是一条回复。每条主线的一幕和收束，每一页的自由；迷宫纪另加 1001 年的。"""
        out, pages = [], {}
        for name in self._names:
            yt = SL.year_text(self.book, self._year[name])
            pages.setdefault(name.split('·')[0], yt)
            for act in ('一幕', '收束'):
                out.append(('回复·%s·%s' % (name, act), REPLY % (self.era, yt, '%s', '%s·%s' % (name, act))))
        for p, yt in pages.items():
            out.append(('回复·%s·自由' % p, REPLY % (self.era, yt, '%s', p + '·自由')))
        if self.has1001:
            out.append(('回复·1001', REPLY % (self.era, '1001年', '%s', '第一兆·魔兽离巢·起潮')))
        return out

    def page(self, y):
        k = bisect.bisect_right(self._ly, y) - 1
        return self._lp[max(k, 0)]

    def sweep(self):
        """逐年：[(年份的字, 谁说的, 文字)]。回复的潮汐写这一年所在那一页的自由；有“自己报年份”开局的纪再给一条凭证。"""
        era, card = self.era, self.card
        lo, hi = SWEEP[card] or (1, 0)
        for y in range(lo, hi + 1):
            yt = SL.year_text(self.book, y)
            yield yt, 'assistant', REPLY % (era, yt, '某地', self.page(y) + '·自由')
            if self.free:
                n = '元' if yt == '元年' else str(y)
                yield yt, 'user', '纪元：%s%s｜开局时段：%s｜年份：%s' % (era, yt, self.free, n) + REST
        if card == 'strife':
            yield '山铜纪元年', 'assistant', REPLY % ('山铜纪', '元年', '某地', self._lp[-1] + '·自由')
        if card == 'bronze':
            yield '迷宫纪元年', 'assistant', REPLY % ('迷宫纪', '元年', '某地', self._lp[-1] + '·自由')
        if self.has1001:
            for y in range(MAZE_1001[0], MAZE_1001[1] + 1):
                yield '%d年' % y, 'assistant', REPLY % (era, '%d年' % y, '晨曦帝国·金鸢城·外城', '第一兆·魔兽离巢·起潮')

    def anchored(self):
        """先主线的，再逐年的。"""
        for name, role, text in self.main:
            yield name, role, text
        for yt, role, text in self.sweep():
            yield yt, role, text

    def can_wake_foreign(self, e, step=1):
        """别纪文件夹的条目：它自己的潮汐页名、主线名、开局时段不算话题（这张卡的局里不会有），只拿“同时满足”第二个词里的字试。"""
        e2 = e
        ws = e.get('triggerWords') or []
        lits = literals(dict(triggerWords=ws[1:])) if (e.get('triggerWordsType') == 'AND' and len(ws) == 2) else []
        lits = [l for l in lits if not is_tide(l)]      # 第二个词本身是别纪的潮汐的（这一段旅伴之间｜擎天之心），这张卡的局里也不会有
        tail = '\n' + '\n'.join(lits)
        for name, role, text in self.main:
            if rili_woke(e2, text + tail, role):
                return True
        if self._sweep is None:
            self._sweep = list(self.sweep())
        for j in range(0, len(self._sweep), step):
            yt, role, text = self._sweep[j]
            if rili_woke(e2, text + tail, role):
                return True
        return False

    def can_wake(self, e, step=1):
        """照日里的判法，这一条在这张卡的局里（带锚的凭证和回复）醒不醒得了。话题拿条目自己触发词里的字一起接上，回复再接一行 §预载。
        潮汐里的一截（页·主线·、带变体的写法，见 tide_like）不当话题接（11-25 拆迷宫纪两张时添的）：它只写在回复的底座上，接在别的局的消息后头是造不出来的。"""
        lits = [l for l in literals(e) if not tide_like(l)]
        tail = '\n' + '\n'.join(lits)
        pre = ('\n§预载｜' + '、'.join(lits)) if lits else ''
        for name, role, text in self.main:
            if rili_woke(e, text + tail + (pre if role == 'assistant' else ''), role):
                return True
        if self._sweep is None:
            self._sweep = list(self.sweep())
        for j in range(0, len(self._sweep), step):
            yt, role, text = self._sweep[j]
            if rili_woke(e, text + tail + (pre if role == 'assistant' else ''), role):
                return True
        return False
