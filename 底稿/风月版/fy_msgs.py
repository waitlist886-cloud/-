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
SWEEP = dict(moon=(1, 10100), strife=(1, 11050), bronze=(2, 960), maze=(2, 1000))
MAZE_1001 = (1001, 1030)
_YR = re.compile(r'纪元：\S+?纪(元|\d+)年')


def title_of(e):
    c = e.get('content') or ((e.get('contents') or [{}])[0].get('content') or '')
    return c.lstrip().split('\n', 1)[0][:60]


def literals(e):
    """条目触发词里能直接写进一句话的字（正则拆到元字符为止），去掉认纪元、开局、年份的。照 make_dlc.literals。"""
    out = []
    for w in e.get('triggerWords') or []:
        p = SL.parse(w)
        if not p:
            runs = [w]
        else:
            body = re.sub(r'\\.', '\x01', p[0])
            runs = re.split(r'[\\^$.|?*+()\[\]{}/\x01]', body)
        for r in runs:
            r = r.strip()
            if len(r) >= 2 and re.search(r'[一-鿿]', r) and not re.search('纪元|开局|年份|底座|§推演|§预载', r):
                out.append(r)
    seen, res = set(), []
    for r in sorted(out, key=len, reverse=True):
        if r not in seen:
            seen.add(r)
            res.append(r)
    return res[:24]


def topic_literals(e):
    """对账时往消息里接的字：“同时满足”的条目只拿不带锚的那个词里的字（带锚那个词里别的支是潮汐的页名主线名，真消息里只会出现在底座上），别的条目全拿。"""
    ws = e.get('triggerWords') or []
    if (e.get('triggerWordsType') or 'OR') == 'AND' and len(ws) == 2:
        a, b = ('纪元：' in ws[0]), ('纪元：' in ws[1])
        if a != b:
            return literals(dict(triggerWords=[ws[1] if a else ws[0]]))
    return literals(e)


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
            if cera == era:
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
            elif cera == '迷宫纪1001' and card == 'maze':
                self.main.append(('凭证·1001（没有纪元那一行）', 'user', old))
        if card == 'maze':
            self.main.append(('凭证·1001（带纪元那一行）', 'user', '纪元：迷宫纪1001年｜开局时段：阿卡迪亚' + REST))
            self.main.append(('回复·1001', 'assistant', REPLY % (era, '1001年', '晨曦帝国·金鸢城·外城', '第一兆·魔兽离巢·起潮')))
        self._names = [n for _, n in lines]
        self._opens = [m.group(1) for _, role, t in self.main if role == 'user' for m in [re.match(r'纪元：[^｜\n]*｜开局时段：([^｜\n]+)', t)] if m]
        lines.sort()
        self._ly = [y for y, _ in lines]
        self._lp = [n.split('·')[0] for _, n in lines]
        self.free = free
        self.book = book
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

    def page(self, y):
        k = bisect.bisect_right(self._ly, y) - 1
        return self._lp[max(k, 0)]

    def sweep(self):
        """逐年：[(年份的字, 谁说的, 文字)]。回复的潮汐写这一年所在那一页的自由；有“自己报年份”开局的纪再给一条凭证。"""
        era, card = self.era, self.card
        lo, hi = SWEEP[card]
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
        if card == 'maze':
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
        """照日里的判法，这一条在这张卡的局里（带锚的凭证和回复）醒不醒得了。话题拿条目自己触发词里的字一起接上，回复再接一行 §预载。"""
        lits = literals(e)
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
