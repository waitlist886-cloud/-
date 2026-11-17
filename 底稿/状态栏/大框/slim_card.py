#!/usr/bin/env python3
# 四纪大框的机械瘦身（11-17，用户问“还有别的可以精炼压大小的地方吗”，回“就做1吧”）。只动触发词和黑名单，正文一个字不动。
#   一、时段钥匙里抄着的开局口令：每个时段条目的触发里都抄着这一段所有的主线名、任务名、篇名、自己报年份的那一支，
#       只为开局那一轮（还没有底座）醒得过来。11-17 起外壳出的凭证头一行写成“纪元：山铜纪668年｜开局时段：黎明篡位”，
#       钥匙认年份那一支就醒了，所以带年份那一支的触发词里，开头就是“开局时段：”的支都拿掉。主线条目（文件夹 时段主线）自己认开局的照留，
#       “纪元：迷宫纪｜开局时段：”这种认纪元的照留（凭证没写年份的时候常驻还醒得了）。
#   二、认旧 HTML 状态栏的锚：(?:<br>|hud-meta">|纪元：) 换成 纪元：，最外层只认旧 HTML 的支（日期</b><br>…、潮汐<\/b><br>…、层级</b>…）拿掉，
#       黑名单和触发里只认旧 HTML 的纯词也拿掉（OR 的才拿，拿完还得剩东西）。四纪大框有转换那一组，旧回复先转成记录再扫世界书（11-10 探针量过），这些用不着了。
# make_four_era_card.py 最后一步套 apply，再拿 check 逐条主线比改前改后（凭证开局、回复里的底座、1001 年的凭证），叫不醒的就停。
import json
import os
import re

ERA_ANCHOR = '(?:<br>|hud-meta">|纪元：)'
HTML = re.compile(r'</b>|<\\/b>|<br>|hud-meta|hud-|arc-')
BOOKS = {'moon': ('小样_月银纪书', '月银纪'), 'strife': ('小样_纷争纪书', '纷争纪'), 'bronze': ('小样_山铜纪书', '山铜纪'), 'maze': ('小样_迷宫纪书', '迷宫纪')}


def parse(w):
    m = re.match(r'^/(.*)/([imsg]*)$', w, re.S)
    return (m.group(1), m.group(2)) if m else None


def top_alts(body):
    """按最外层的 | 切开（括号、方括号里的不切）。"""
    out, depth, cur, i = [], 0, '', 0
    while i < len(body):
        c = body[i]
        if c == '\\' and i + 1 < len(body):
            cur += body[i:i + 2]
            i += 2
            continue
        if c == '[':
            j = body.find(']', i + 2 if body[i + 1:i + 2] in ('^', ']') else i + 1)
            j = len(body) - 1 if j < 0 else j
            cur += body[i:j + 1]
            i = j + 1
            continue
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        if c == '|' and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += c
        i += 1
    out.append(cur)
    return out


def depth0(alt):
    """一支里括号外头的字（括号、方括号里的不算）。"""
    out, depth, i = '', 0, 0
    while i < len(alt):
        c = alt[i]
        if c == '\\' and i + 1 < len(alt):
            if depth == 0:
                out += alt[i:i + 2]
            i += 2
            continue
        if c == '[':
            j = alt.find(']', i + 2 if alt[i + 1:i + 2] in ('^', ']') else i + 1)
            j = len(alt) - 1 if j < 0 else j
            if depth == 0:
                out += alt[i:j + 1]
            i = j + 1
            continue
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif depth == 0:
            out += c
        i += 1
    return out


def has_year(a):
    return '纪元：' in a and '年' in a


def slim_word(w, strip_open):
    p = parse(w)
    if not p:
        return w
    body, fl = p
    body = body.replace(ERA_ANCHOR, '纪元：')
    alts = top_alts(body)
    keep = [a for a in alts if not HTML.search(depth0(a))] or alts
    if strip_open and any(has_year(a) for a in keep):
        k2 = [a for a in keep if not depth0(a).startswith('开局时段：')]
        keep = k2 or keep
    out = []
    for a in keep:          # 去重（拆掉旧锚以后有的支一模一样了）
        if a not in out:
            out.append(a)
    return '/%s/%s' % ('|'.join(out), fl)


def slim_list(words, typ, strip_open):
    if not words:
        return words
    new = [slim_word(w, strip_open) for w in words]
    if (typ or 'OR') == 'OR':
        plain_html = [w for w in new if not parse(w) and HTML.search(w)]
        rest = [w for w in new if w not in plain_html]
        if plain_html and rest:
            new = rest
    out = []
    for w in new:
        if w not in out:
            out.append(w)
    return out


def size(o):
    return len(json.dumps(o, ensure_ascii=False).encode('utf-8'))


def apply(lb):
    st = {'条目': 0, '触发字节': 0, '黑名单字节': 0}
    for e in lb:
        main = '时段主线' in (e.get('folder') or '')
        t0, b0 = e.get('triggerWords'), e.get('blackListWords')
        t1 = slim_list(t0, e.get('triggerWordsType'), not main)
        b1 = slim_list(b0, e.get('blackListWordsType'), False)
        if t1 != t0 or b1 != b0:
            st['条目'] += 1
            st['触发字节'] += size(t0 or []) - size(t1 or [])
            st['黑名单字节'] += size(b0 or []) - size(b1 or [])
            if t0 is not None:
                e['triggerWords'] = t1
            if b0 is not None:
                e['blackListWords'] = b1
    return st


# ---------------- 核对：改前改后醒的条目比一遍 ----------------
def year_of(s):
    t = re.sub(r'\s', '', str(s or ''))
    m = re.search(r'(\d{1,5})', t)
    return int(m.group(1)) if m else (1 if re.search(r'元年|^元$', t) else None)


def year_text(b, y):
    if y is None:
        return ''
    return '元年' if (y == 1 and b == 'strife') else '%d年' % y


def opening(b, era, y, start):
    """凭证头一行。外壳 shell.js 的 credential() 照这个写，改了两边一起改。"""
    return '纪元：%s%s｜开局时段：%s' % (era, year_text(b, y), start)


def _rx(w, cache={}):
    r = cache.get(w)
    if r is None:
        p = parse(w)
        if p:
            fl = 0
            for c in p[1]:
                fl |= {'i': re.I, 'm': re.M, 's': re.S}.get(c, 0)
            try:
                r = re.compile(p[0], fl)
            except re.error:
                r = False
        else:
            r = w
        cache[w] = r
    return r


def _hit(words, typ, msg):
    if not words:
        return False
    res = []
    for w in words:
        r = _rx(w)
        res.append((w in msg) if isinstance(r, str) else (bool(r.search(msg)) if r else False))
    return all(res) if (typ or 'OR') == 'AND' else any(res)


def wake(lb, msg, rng):
    out = set()
    for i, e in enumerate(lb):
        if not e.get('enabled', True) or rng not in (e.get('triggerRange') or []):
            continue
        if _hit(e.get('triggerWords'), e.get('triggerWordsType'), msg) and not _hit(e.get('blackListWords'), e.get('blackListWordsType'), msg):
            out.add(i)
    return out


def cases(root):
    front = os.path.join(root, '底稿', '门面')
    build = json.load(open(os.path.join(front, '小样_外壳', 'data', 'build.json'), encoding='utf-8'))
    head = build['format']['head']
    out = []
    for b, (folder, era) in BOOKS.items():
        D = json.load(open(os.path.join(front, folder, 'data', b + '.json'), encoding='utf-8'))
        eras = D['eras'] if isinstance(D, dict) and 'eras' in D else D
        E = build['eras'][b]
        mode = E.get('start', 'tail')
        for pg in eras:
            for l in pg.get('lines', []):
                name = l['name']
                start = name if mode == 'line' else (name.split('·', 1)[1] if '·' in name else name)
                y = year_of(l.get('year'))
                rest = '\n\n%s\n\n【一·灵魂形态】\n降临之魂 · 身穿（连人带身跌入）\n\n【七·现在何处】\n现在所在：%s%s，%s，主线「%s」的开局\n\n开始游戏。' % (
                    head, era, year_text(b, y), pg.get('title') or '', name)
                old = '纪元：%s｜开局时段：%s' % (era, start) + rest
                new = opening(b, era, y, start) + rest
                reply = '§底座｜纪元：%s%s · 黄昏 · 某地 · %s·一幕 · 防抢话 开 · 档位 长\n正文。' % (era, year_text(b, y), name)
                out.append((era, name, old, new, reply))
        FR = E.get('free')
        if FR:
            ys = sorted({FR['from'], FR['to']} | {y for pg in eras for y in (year_of(pg.get('y0') or (pg.get('years') or '').split('—')[0]),) if y} |
                        {y for pg in eras for y in (year_of(pg.get('y1') or (pg.get('years') or '').split('—')[-1]),) if y})
            ys = [y for y in ys if FR['from'] <= y <= FR['to']]
            for y in ys:
                cmd = FR['cmd'].replace('{year}', '元' if (y == 1 and b == 'strife') else str(y))
                rest = '\n\n%s\n\n现在所在：%s%d年（%s，照那一年的时段总纲和地点起头）\n\n开始游戏。' % (head, era, y, FR['label'])
                old = '纪元：%s｜开局时段：%s' % (era, cmd) + rest
                new = opening(b, era, y, cmd) + rest
                out.append((era, '%s %d年' % (FR['label'], y), old, new, None))
    out.append(('迷宫纪1001', '1001 年的凭证', head + '\n\n【一·灵魂形态】\n本地之魂（生于此世）\n\n【七·现在何处】\n现在所在：阿卡迪亚\n\n开始游戏。', None, None))
    return out


def why(lb, i, msg):
    """少醒的那一条为什么不醒：触发还中、叫黑名单挡了（凭证带上年份以后，那一年不该有的条目挡下来，是对的），还是触发不中了（这才是毛病）。"""
    e = lb[i]
    if not _hit(e.get('triggerWords'), e.get('triggerWordsType'), msg):
        return '触发不中'
    return '黑名单挡年份'


def check(old_lb, new_lb, root):
    """返回 {'lost': [(凭证, 条目, 缘故)], 'mixed_lost': [...], 'gained': n, 'reply_diff': [...], 'cases': n}。
    lost：旧卡加旧凭证醒、新卡加新凭证不醒的条目；mixed_lost：旧卡加新凭证（外壳先推、卡还没重导的那几天）比旧卡加旧凭证少醒的。"""
    title = lambda lb, i: (lb[i].get('content') or '').split('\n', 1)[0][:40]
    rep = {'lost': [], 'mixed_lost': [], 'gained': 0, 'reply_diff': [], 'cases': 0}
    for era, name, old, new, reply in cases(root):
        rep['cases'] += 1
        a = wake(old_lb, old, 'user')
        if new is None:
            b = wake(new_lb, old, 'user')
            if a != b:
                rep['lost'] += [(name, title(old_lb, i), why(new_lb, i, old)) for i in sorted(a - b)]
                rep['gained'] += len(b - a)
            continue
        b = wake(new_lb, new, 'user')
        c = wake(old_lb, new, 'user')
        rep['lost'] += [(name, title(old_lb, i), why(new_lb, i, new)) for i in sorted(a - b)]
        rep['mixed_lost'] += [(name, title(old_lb, i), why(old_lb, i, new)) for i in sorted(a - c)]
        rep['gained'] += len(b - a)
        if reply:
            ra, rb = wake(old_lb, reply, 'assistant'), wake(new_lb, reply, 'assistant')
            if ra != rb:
                rep['reply_diff'].append((name, [title(old_lb, i) for i in sorted(ra - rb)], [title(new_lb, i) for i in sorted(rb - ra)]))
    return rep
