# 四纪主线按幕拆条目（11-10，用户：“主线按幕拆吧”）。只在打四纪大框的最后一步套，v12 照旧一条主线一条。
#
# 一条主线拆成：
#   骨架（原条目，触发、设置一样不动）：标题、【调用】、题、篇或章、钩子、开局、世道、各段的标题、默认收束、玩家能改、碰得上的人、裁定锁。
#   各段一条（一幕、二幕、三幕、收束，有幕间小节的另一条幕间）：这一段的拍，末尾带下一段的标题和头两拍。
# 叫醒：潮汐格写「时段·主线·一幕」那一类（四纪常驻定的写法，幕与幕之间写幕间，主线了结写收束），
#   各段认自己那一个；一幕另认开局口令（开局那一轮潮汐格还没写）。扫描深度 4，换幕以后上一段还跟一两轮，不断档。
# 设置照骨架（文件夹、黑名单、优先级、范围），只改触发和深度；新条目接在世界书末尾，前面按下标找条目的模块不受影响。
import copy
import re

SEG = re.compile(r'^(一幕|二幕|三幕|幕间|收束)[｜：]')      # 黑翼天塔那一条的收束写成「收束：」
TAIL = re.compile(r'^(?:默认收束：|玩家能改：|碰得上的人：|## 裁定锁)')
BEAT = re.compile(r'^- ')
DEPTH = 4
PREVIEW = 2


def top_alts(rx):
    """把 /a|b|c/ 按最外层的 | 切开。"""
    assert rx.startswith('/') and rx.endswith('/'), rx[:40]
    body = rx[1:-1]
    out, depth, cur, i = [], 0, '', 0
    while i < len(body):
        c = body[i]
        if c == '\\' and i + 1 < len(body):
            cur += body[i:i + 2]
            i += 2
            continue
        if c == '[':
            j = body.index(']', i + 1)
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


def parse(content):
    """切成 head（第一段以前）、segs [(名, 行列表)]、tail（默认收束起）。"""
    lines = content.split('\n')
    first = next((i for i, l in enumerate(lines) if SEG.match(l)), None)
    last = next((i for i, l in enumerate(lines) if TAIL.match(l)), None)
    if first is None or last is None or last < first:
        return None
    head, body, tail = lines[:first], lines[first:last], lines[last:]
    segs = []
    for l in body:
        m = SEG.match(l)
        if m:
            segs.append([m.group(1), [l]])
        else:
            segs[-1][1].append(l)
    for s in segs:
        while s[1] and not s[1][-1].strip():
            s[1].pop()
    return head, segs, tail


def build(e):
    """返回 (新骨架正文, [(段名, 正文, 触发正则)])，拆不了返回 None。"""
    c = e['content']
    p = parse(c)
    if not p:
        return None
    head, segs, tail = p
    # 开局那一段只在一幕要，挪进一幕那一条；玩家能改里写明哪一幕的那几条，挪进那一段
    opening = [l for l in head if l.startswith('开局：')]
    head = [l for l in head if not l.startswith('开局：')]
    per_seg = {}
    ti = next((k for k, l in enumerate(tail) if l.startswith('玩家能改：')), None)
    if ti is not None:
        tj = next((k for k in range(ti + 1, len(tail)) if not tail[k].startswith('- ')), len(tail))
        keep = []
        for l in tail[ti + 1:tj]:
            m = re.match(r'^- (一幕|二幕|三幕|幕间|收束)', l)
            if m:
                per_seg.setdefault(m.group(1), []).append(l)
            else:
                keep.append(l)
        moved = sum(len(v) for v in per_seg.values())
        if moved:
            label = tail[ti] if tail[ti] != '玩家能改：' else '玩家能改：'
            note = '各段能改的写在那一段的条目里，下面是整条主线都算的。' if keep else '各段能改的写在那一段的条目里。'
            tail = tail[:ti] + [label + note if label == '玩家能改：' else label] + keep + tail[tj:]
    names = [s[0] for s in segs]
    assert names.count('一幕') == 1 and names.count('收束') == 1, names
    title = head[0]
    assert title.startswith('# ') and '·主线｜' in title, title[:40]
    qname = title[2:].split('｜', 1)[1]          # 时段·主线 或 页名·主线名
    tw = e['triggerWords']
    assert tw and all(w.startswith('/') and w.endswith('/') for w in tw), tw
    alts = [a for w in tw for a in top_alts(w)]      # 改过名的主线留着旧钥匙（三川会盟、灯台初升），一并认
    keys = [a for a in alts if a.endswith('·')]
    opens = [a for a in alts if a.startswith('开局时段：')]
    assert keys and len(keys) + len(opens) == len(alts), alts
    K = keys[0] if len(keys) == 1 else '(?:%s)' % '|'.join(keys)
    out = []
    for k, (nm, ls) in enumerate(segs):
        body = (opening + [''] if nm == '一幕' and opening else []) + list(ls)
        if per_seg.get(nm):
            body += ['', '这一段能改的：'] + per_seg[nm]
        if k + 1 < len(segs):
            nx = segs[k + 1][1]
            beats = [l for l in nx[1:] if BEAT.match(l)][:PREVIEW]
            body += ['', '下一段的开头：', nx[0]] + beats
        call = '【调用】潮汐格写%s·%s的回合用%s。这一条是%s那一条主线的%s，题、世道、默认收束、碰得上的人、裁定锁在主线那一条里。' % (
            qname, nm, '，开局那一轮也用' if nm == '一幕' else '', qname, nm)
        txt = '\n'.join(['# %s·%s' % (title[2:], nm), call, ''] + body)
        act = nm if nm in ('幕间', '收束') else '(?:第)?' + nm
        rx = '/%s%s%s/' % (K, act, ''.join('|' + o for o in opens) if nm == '一幕' else '')
        out.append((nm, txt, rx))
    table = ['各段：'] + [s[1][0] for s in segs] + [
        '各段的拍不在这一条里。潮汐格写到哪一段，那一段连同下一段的开头另有一条跟着进来，开局那一轮照一幕走。']
    core = '\n'.join(head + table + [''] + tail)
    return core, out


def apply(lb):
    """拆四纪主线（文件夹 41·X纪｜时段主线），新条目接在末尾。返回统计。"""
    stat = {'拆了': 0, '没拆': [], '新条目': 0, '原字': 0, '骨架字': 0, '各段字': 0, '每轮多半': [], '每轮原来': []}
    add = []
    for i, e in enumerate(lb):
        if '时段主线' not in (e.get('folder') or ''):
            continue
        r = build(e)
        if not r:
            stat['没拆'].append(i)
            continue
        core, segs = r
        stat['拆了'] += 1
        stat['原字'] += len(e['content'])
        stat['每轮原来'].append(len(e['content']))
        stat['骨架字'] += len(core)
        biggest = 0
        for nm, txt, rx in segs:
            ne = copy.deepcopy(e)
            ne['content'] = txt
            ne['triggerWords'] = [rx]
            ne['triggerWordsType'] = 'OR'
            ne['scanDepth'] = DEPTH
            add.append(ne)
            stat['各段字'] += len(txt)
            biggest = max(biggest, len(txt))
        stat['每轮多半'].append(len(core) + biggest)
        e['content'] = core
    lb.extend(add)
    stat['新条目'] = len(add)
    return stat


def js2py(rx):
    m = re.match(r'^/(.*)/([a-z]*)$', rx, re.S)
    flags = re.I if 'i' in m.group(2) else 0
    return re.compile(m.group(1), flags)


def simulate(lb):
    """拿假回复（潮汐格写某一段）和开局口令试：各段只醒自己，别的主线的段一条不醒。返回问题列表。"""
    probs = []
    segs = []          # (主线名, 段名, 正则)
    cores = []         # (主线名, 开局口令列表)
    for e in lb:
        if '时段主线' not in (e.get('folder') or ''):
            continue
        first = e['content'].split('\n', 1)[0]
        m = re.match(r'^# (.+?)·主线｜(.+?)(?:·(一幕|二幕|三幕|幕间|收束))?$', first)
        if not m:
            probs.append('标题认不出：' + first[:40])
            continue
        q = m.group(2)
        rx = js2py(e['triggerWords'][0])
        if m.group(3):
            segs.append((q, m.group(3), rx))
        else:
            alts = [a for w in e['triggerWords'] for a in top_alts(w)]
            cores.append((q, m.group(1), [a for a in alts if a.startswith('开局时段：')]))
    have = {}
    for q, nm, rx in segs:
        have.setdefault(q, set()).add(nm)
    for q, era, opens in cores:
        for nm in sorted(have.get(q, ())):
            reply = '§底座｜纪元：某纪某年 · 夜 · 某地 · %s·%s · 防抢话 开 · 档位 长\n正文。' % (q, nm)
            woke = [(q2, n2) for q2, n2, rx in segs if rx.search(reply)]
            if woke != [(q, nm)]:
                probs.append('潮汐 %s·%s 叫醒了 %s' % (q, nm, woke))
        # 开局口令：凭证里月银纪写开局时段：时段·主线，别的三纪写开局时段：主线名。一幕要醒，别的主线的段一条不醒
        cands = ['开局时段：%s\n' % (q if era == '月银纪' else q.split('·', 1)[1])]
        got = set()
        for u in cands:
            for q2, n2, rx in segs:
                if rx.search(u):
                    got.add((q2, n2))
        if (q, '一幕') not in got:
            probs.append('开局口令叫不醒 %s 的一幕' % q)
        other = sorted(x for x in got if x[0] != q)
        if other:
            probs.append('开局口令 %s 叫醒了别的主线的段 %s' % (q, other))
        if any(n != '一幕' for q2, n in got if q2 == q):
            probs.append('开局口令 %s 叫醒了一幕以外的段' % q)
    # 正则的样子：平台的体检（量词不套量词，量词不过 25 个），一个触发词不过 1024 字
    for e in lb:
        if '时段主线' not in (e.get('folder') or ''):
            continue
        for w in e['triggerWords']:
            s = re.sub(r'\\.', 'x', w)
            s = re.sub(r'\[[^\]]*\]', 'C', s)
            nq = len(re.findall(r'\{\d*,?\d*\}|[*+?](?!:|=|!)', s.replace('(?:', '(').replace('(?=', '(').replace('(?!', '(')))
            if nq > 25:
                probs.append('量词 %d 个：%s' % (nq, w[:60]))
            if re.search(r'\)[*+?{]', s.replace('(?:', '(')) and re.search(r'\([^()]*[*+?][^()]*\)[*+?{]', s.replace('(?:', '(')):
                probs.append('量词套量词：%s' % w[:60])
            if len(w) > 1024:
                probs.append('触发词过 1024 字：%s' % w[:60])
    return probs, len(segs), len(cores)
