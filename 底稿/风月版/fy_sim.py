#!/usr/bin/env python3
# 风月版对账：同一段文字，日里的判法（触发加黑名单，slim_card._hit）和风月的判法（一条 RE2 钥匙）醒的结果一条一条比。
# 用法（仓库根上，先跑过 fy_lore.py）：
#   python -I -X utf8 底稿/风月版/fy_sim.py <纪…> [--step N] [--src 全本.json]
#     --step N  逐年扫的时候每 N 年取一年（默认 1，一年不落；调试时放大）
# 拿什么比：
#   零 原样的凭证和回复，什么都不接（11-25 添的）。靠底座那一行自己醒的条目归它管：话题就是潮汐里的主线名、页名的（碑、史诗、遗迹、这一段旅伴之间）。
#   甲 这一纪四本书里每条主线的凭证（slim_card.cases）、五种幕的回复底座，自己报年份的凭证，迷宫纪另加 1001 年的两种凭证和回复；
#      后头接条目自己触发词里的字，一个字一回；回复再接一行 §预载。
#   地 话题写在底座那一行的地点那一格里、正文不再提（11-25 添的）：每条主线的一幕和收束、每一页的自由，一个字一回。
#   乙 逐年扫：每一年一条回复（潮汐写这一年所在那一页的自由）、一条自己报年份的凭证，原样比一回，后头接这一条全部的字再比一回。认年份的条目一年不落，不认年份的每隔一段取一年。
#   丙 玩家裸打的一句（没有底座、没有凭证），只有条目自己的字。
#   条目的字里是潮汐一截的（页·主线·，见 fy_msgs.is_tide）不当话题接：潮汐只写在回复的底座上，玩家不会单打它，另起一行接在别的主线的凭证后头是造不出来的消息。它由“零”那一组比。
# 钥匙先过 fy_gate.re2_problems（RE2 不认的写法），再拿 Python 的 re 跑。
# 结果分三样：
#   带锚的消息（甲、乙）上不一样：是毛病，逐条列。
#   裸打的一句上日里不醒、风月醒：纪元钥匙拿掉的条目本来就该这样（日里要等回复里写到才醒，慢一轮），只记数。
#   裸打的一句上别的不一样：逐条列。
# 另查一遍切卡：没带进这张卡的条目，照日里的判法在这张卡带锚的消息里醒不醒得了（醒得了又没带的，除了底卡 --base 以外的文件夹，都列出来）。
import collections
import datetime
import json
import os
import re
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fy_gate as G     # noqa: E402
import fy_msgs as M     # noqa: E402
import fy_lore as L     # noqa: E402

ROOT = G.ROOT
ROLE_BIT = {'user': 2, 'assistant': 4}


def fy_woke(pieces, text, role):
    b = ROLE_BIT[role]
    return any((r & b) and rx.search(text) for rx, r in pieces)


def run(card, lb, nb, step):
    era = G.CARDS[card]['name']
    d = os.path.join(L.OUT, era)
    conv = json.load(open(os.path.join(d, '世界书_转换.json'), encoding='utf-8'))
    rep_conv = json.load(open(os.path.join(d, '转换报告.json'), encoding='utf-8'))
    by = collections.OrderedDict()
    kinds = {}
    bad_re2 = []
    for x in conv['entries']:
        p = G.re2_problems(x['key'])
        if p:
            bad_re2.append((x['_src'], x['_title'], p))
        by.setdefault(x['_src'], []).append((re.compile(x['key']), x['key_region']))
        kinds[x['_src']] = set(x.get('_kinds') or [])
    msgs = M.Msgs(card)
    main = msgs.main
    creds = [(n, r, t) for n, r, t in main if r == 'user']
    first = [(n, r, t) for n, r, t in main if r == 'assistant' and (n.endswith('·一幕') or n == '回复·1001')]
    rest = [(n, r, t) for n, r, t in main if r == 'assistant' and not (n.endswith('·一幕') or n == '回复·1001')]
    sweep = list(msgs.sweep())
    locs = msgs.loc_replies()
    R = dict(card=card, era=era, made=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), entries=len(by), pieces=len(conv['entries']),
             main_msgs=len(main), sweep_msgs=len(sweep), loc_msgs=len(locs), step=step, tests=0, anchored_diff=[], noanchor_expected=0, bare_noseat=0,
             bare_expected=0, bare_expected_entries=0, bare_diff=[], tide_lits=0,
             re2_bad=[dict(i=i, title=t, why=p) for i, t, p in bad_re2], nolit=0, unpicked_wakeable=[])
    t0 = time.time()
    nd = 0
    for i, pieces in by.items():
        e = lb[i]
        lits = M.topic_literals(e)
        nt = len(lits)
        lits = [l for l in lits if not M.is_tide(l)]        # 潮汐里的一截不当话题接（见 fy_msgs.is_tide），它由“原样的”那一组来比
        R['tide_lits'] += nt - len(lits)
        own = [c for c in lits if G.SL._hit(e.get('triggerWords'), 'OR', c)]       # 单说就中的字（拆出来的半截不算）
        lits = lits + M.topic_samples(e)        # “某某.{0,16}某某”这种正则的题，拼几句真配得上的一起接
        if not lits:
            R['nolit'] += 1
        cands = lits or ['']
        joined = '\n'.join(lits)
        pre = ('\n§预载｜' + '、'.join(lits)) if lits else ''
        diffs = []

        def cmp(label, role, text):
            R['tests'] += 1
            a, b = M.rili_woke(e, text, role), fy_woke(pieces, text, role)
            if a != b:
                if b and '纪元：' not in text and ('纪元钥匙拿掉' in kinds[i] or '恒醒' in kinds[i]):
                    R['noanchor_expected'] += 1     # 1001 年老凭证没有“纪元：”那一行：跟裸打的一句是一回事
                    return
                diffs.append((label, '日里醒、风月不醒' if a else '日里不醒、风月醒'))
        # 零 原样的凭证和回复，什么都不接（靠底座那一行自己醒的条目：潮汐里的主线名、页名就是话题）
        for n, role, t in main:
            cmp(n + '（原样）', role, t)
        for n, role, t in creds + first:
            for c in cands:
                if c:
                    cmp(n + '＋' + c, role, t + '\n' + c)
            if role == 'assistant' and pre:
                cmp(n + '＋预载', role, t + pre)
        for n, role, t in rest:
            if lits:
                cmp(n + '＋全部的字', role, t + '\n' + joined + pre)
        # 话题写在底座那一行的地点那一格里，后头的正文不再提。只拿单说就中的字（拆出来的半截不算话题，“某某.{0,16}某某”里的一个人名之类）
        for n, fmt in locs:
            for c in own:
                cmp(n + '·地点写“' + c + '”', 'assistant', fmt.replace('%s', c, 1))
        yd = M.year_dep(e)
        k = step if yd else max(step, 173)
        for j, (yt, role, t) in enumerate(sweep):
            if j % (2 * k if msgs.free else k) >= (2 if msgs.free else 1) and yt[0].isdigit():
                continue
            lab = '逐年·%s·%s' % (yt, '回复' if role == 'assistant' else '凭证')
            cmp(lab + '（原样）', role, t)
            if lits:
                cmp(lab, role, t + '\n' + joined + (pre if role == 'assistant' else ''))
        if diffs:
            nd += 1
            R['anchored_diff'].append(dict(i=i, folder=e['folder'], title=M.title_of(e), n=len(diffs), first=diffs[:4],
                                           kinds=collections.Counter(x[1] for x in diffs)))
        # 丙：裸打的一句
        bexp, bdiff = 0, []
        for role in ('user', 'assistant'):
            for c in cands + ([joined] if len(lits) > 1 else []):
                if not c:
                    continue
                R['tests'] += 1
                a, b = M.rili_woke(e, c, role), fy_woke(pieces, c, role)
                if a == b:
                    continue
                if b and not a and ('纪元钥匙拿掉' in kinds[i] or '恒醒' in kinds[i]):
                    bexp += 1
                elif a and not b and role == 'assistant' and '拆两条' in kinds[i]:
                    R['bare_noseat'] += 1       # 回复里没有 §底座 的情形：日里那一支“不是回复”认它，风月拆开以后只扫回复的那一条只认 §预载 行
                else:
                    bdiff.append((role, c[:20], '日里醒、风月不醒' if a else '日里不醒、风月醒'))
        if bexp:
            R['bare_expected'] += bexp
            R['bare_expected_entries'] += 1
        if bdiff:
            R['bare_diff'].append(dict(i=i, folder=e['folder'], title=M.title_of(e), n=len(bdiff), first=bdiff[:3], kinds=sorted(kinds[i])))
    R['seconds'] = round(time.time() - t0)
    # 切卡复核：没带的条目，日里在这张卡带锚的消息里醒不醒得了
    left = {x['i'] for x in rep_conv.get('left') or []}
    skipped = {x['i'] for x in rep_conv.get('skipped') or []}
    for i, e in enumerate(lb):
        if i in by or i in left or i in skipped or e.get('contentMethod') == 'weighted':
            continue
        fera = L.era_of(e)
        if (msgs.can_wake_foreign(e, 97) if (fera and fera != era) else msgs.can_wake(e, 97)):
            R['unpicked_wakeable'].append(dict(i=i, folder=e['folder'], title=M.title_of(e)))
    with open(os.path.join(d, '对账报告.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(R, f, ensure_ascii=False, indent=1)
    W = ['# %s 对账（日里的判法对风月的钥匙）' % era, '', '%s，fy_sim.py 自己写的。' % R['made'], '',
         '- 条目 %d 条（风月 %d 条），比了 %d 回；主线的凭证和回复 %d 条（原样比一回、接上话题再比），话题写进底座地点那一格的回复 %d 种，逐年 %d 条（每 %d 年取一年；不认年份的条目每 173 年取一年）' % (
             R['entries'], R['pieces'], R['tests'], R['main_msgs'], R['loc_msgs'], R['sweep_msgs'], step),
         '- 条目的字里是潮汐一截的 %d 个，不当话题接（由原样的回复来比）' % R['tide_lits'],
         '- RE2 不认的钥匙：%d 条' % len(R['re2_bad']),
         '- 带锚的消息上不一样：%d 条条目' % len(R['anchored_diff']),
         '- 玩家裸打的一句：日里不醒、风月醒（纪元钥匙拿掉的条目，本来就该这样）%d 条条目、%d 回；别的不一样 %d 条条目' % (
             R['bare_expected_entries'], R['bare_expected'], len(R['bare_diff'])),
         '- 1001 年老凭证（没有“纪元：”那一行）上日里不醒、风月醒：%d 回（也是纪元钥匙拿掉的条目，同上）' % R['noanchor_expected'],
         '- 没有 §底座 的“回复”里提到话题：拆两条的条目日里醒、风月不醒 %d 回（回复照骨架都有 §底座，这种消息不该有）' % R['bare_noseat'],
         '- 没带进卡、可日里在这张卡的局里醒得了的（底卡 --base 以外的文件夹另算，见转换清单）：%d 条' % len(R['unpicked_wakeable']),
         '- 没有话题字可接的（触发全是锚、潮汐、开局时段，只比原样的消息和逐年）：%d 条' % R['nolit'], '']
    if R['anchored_diff']:
        W += ['## 带锚的消息上不一样', '']
        for x in R['anchored_diff'][:300]:
            W.append('- #%d 〔%s〕%s：%d 回（%s）；头几回：%s' % (x['i'], x['folder'], x['title'], x['n'], '、'.join('%s %d' % kv for kv in x['kinds'].items()),
                                                         '；'.join('%s→%s' % (a.replace('\n', ' '), b) for a, b in x['first'])))
        W.append('')
    if R['bare_diff']:
        W += ['## 裸打的一句上不一样（纪元钥匙拿掉以外的）', '']
        for x in R['bare_diff'][:300]:
            W.append('- #%d 〔%s〕%s：%d 回；%s；改法 %s' % (x['i'], x['folder'], x['title'], x['n'], '；'.join('%s 说“%s”→%s' % t for t in x['first']), '、'.join(x['kinds'])))
        W.append('')
    if R['unpicked_wakeable']:
        W += ['## 没带进卡、可日里醒得了的', ''] + ['- #%(i)d 〔%(folder)s〕%(title)s' % x for x in R['unpicked_wakeable'][:300]] + ['']
    with open(os.path.join(d, '对账.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(W) + '\n')
    print('【%s】比了 %d 回（%d 秒）：RE2 不认 %d；带锚的消息上不一样 %d 条；裸打一句：该当的 %d 条条目，别的不一样 %d 条；没带可醒得了 %d 条' % (
        era, R['tests'], R['seconds'], len(R['re2_bad']), len(R['anchored_diff']), R['bare_expected_entries'], len(R['bare_diff']), len(R['unpicked_wakeable'])))
    return R


def main():
    argv = sys.argv[1:]

    def opt(k, dflt=None):
        if k in argv:
            i = argv.index(k)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return dflt
    src = opt('--src', L.SRC)
    step = int(opt('--step', '1'))
    cards = [a for a in argv if not a.startswith('--')] or list(G.CARDS)
    lb = json.load(open(src, encoding='utf-8'))['prompt']['lorebook']
    nb = L.base_count()
    bad = 0
    for card in cards:
        R = run(card, lb, nb, step)
        bad += len(R['anchored_diff']) + len(R['re2_bad'])
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
