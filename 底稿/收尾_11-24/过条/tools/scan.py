#!/usr/bin/env python3
# 过条底子（11-24）：清点人物条（相遇）和凡世至强条（传奇）里的能力行，写 清点.json、清点.md、分份.json。
#   python -I -X utf8 底稿/收尾_11-24/过条/tools/scan.py
# 只读卡的文件。看的是拼好的页（月银纪史诗、诸国期、萨尔维斯、纷争纪、山铜纪、迷宫纪前传四十七页）和五纪补卷；
# 有分段源稿的页，照条目标题那一行找回分段文件（交稿换回的是分段）。旅伴条 11-20 过过了，不算。
# 一人一条：凡世至强一条一人；人物条里写成「- 名｜本事。……」的小条，一个名字一人，别的整条算一人。
# 「能力行」认带 天赋【 被动【 技艺【 Special【 Passive【 Art【 的行（凡世至强只认【能力｜】那一块里「- 天赋【」这样起头的行）。
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (NL, ROOT, W, JIE, MARK, ERA_GROUP, ERA_ORDER, rd, rel, pages, part_files, supp_files,  # noqa: E402
                    entries, entry_kind, default_who, segs, tier_of, star_index, lineage, companions)

LEG_LINE = re.compile(r'^- (?:天赋|被动|技艺|兼修)')
SUB = re.compile(r'^- ([^｜：。，、\s（]{1,12})｜')
LO, HI = 20, 40


def zs_re(who, single):
    """技艺走势那一行：单人的条「技艺走势：」或「- 技艺走势：」，几人合写的条要「- 名｜技艺走势。」。"""
    nm = re.escape(who.split('·')[0])
    return (r'^(?:- )?(?:' + nm + r'｜)?技艺走势[：。]') if single else (r'^- ' + nm + r'｜技艺走势[：。]')


def person_lines(e, kind, h):
    """[(人, 行)]。"""
    who0 = default_who(h, kind)
    out = []
    for l in e.split(NL):
        if l.startswith('> 条目设置') or l.startswith('【调用】') or l.startswith('## '):
            continue
        if not MARK.search(l) and not (kind == '凡世至强' and l.startswith('- 兼修')):
            continue
        if kind == '凡世至强':
            if not LEG_LINE.match(l):
                continue
            out.append((who0, l))
            continue
        m = SUB.match(l)
        who = m.group(1) if (m and m.group(1) in h) else who0
        out.append((who, l))
    return out


def main():
    sidx = star_index()
    lin = lineage()
    comp = companions()
    recs = []
    no_ab = collections.Counter()
    docs = []
    for key, era, page in pages():
        docs.append((key, era, page, part_files(key)))
    for era, f in supp_files():
        docs.append((rel(f), era, f, None))
    for key, era, page, parts in docs:
        t = rd(page)
        part_text = {p: rd(p) for p in parts} if parts else {}
        for _, e in entries(t):
            h = e.split(NL, 1)[0].rstrip()
            kind = entry_kind(h)
            if kind not in ('人物', '凡世至强'):
                continue
            pl = person_lines(e, kind, h)
            if not pl:
                no_ab[(era, kind)] += 1
                continue
            if parts:
                src = [rel(p) for p, pt in part_text.items() if re.search(r'(?m)^' + re.escape(h) + r'\s*$', pt)]
            else:
                src = [rel(page)]
            by = collections.OrderedDict()
            for who, l in pl:
                by.setdefault(who, []).append(l)
            for who, ls in by.items():
                arts, gens = [], []
                for l in ls:
                    if kind == '凡世至强' and l.startswith('- 兼修'):
                        continue
                    for k, n, sg in segs(l):
                        if k == 'A' and ('兼修' in l[:l.find(sg)] if sg in l else False):
                            continue
                        jie = JIE.search(sg)
                        info = {'名': n, '档': tier_of(sg), '阶': jie.group(0).split('·')[1] if jie else ''}
                        blocks = sidx.get(n, [])
                        same = [b for b in blocks if b[1] == {'A': 'Art', 'S': 'Special', 'P': 'Passive'}[k]]
                        if same:
                            info['星条'] = sorted(set('%s:%s%s' % (b[0], b[2], '·有阶' if b[3] else '') for b in same))
                        if k == 'A':
                            r = lin.get(n)
                            if r:
                                info['全谱'] = '%s｜%s｜新档 %s｜%s' % (r['页'], r['持有人'], r['新档'], r['归门'])
                            arts.append(info)
                        else:
                            info['类'] = '天赋' if k == 'S' else '被动'
                            gens.append(info)
                seen_g = {}
                for g in gens:
                    if g['名'] not in seen_g or (g['档'] and not seen_g[g['名']]['档']):
                        seen_g[g['名']] = g
                gens = list(seen_g.values())
                txt = NL.join(ls)
                has_jx = '兼修' in txt
                todo = []
                if arts and not all(a['阶'] for a in arts):
                    todo.append('开局阶')
                if not has_jx:
                    todo.append('兼修')
                for a in arts:
                    tiers = set(x.split(':')[-1].split('·')[0] for x in a.get('星条', []))
                    if not a['档']:
                        todo.append('技艺没写档【%s】' % a['名'])
                    elif tiers and a['档'] not in tiers:
                        todo.append('技艺档跟星条不一样【%s】行%s／星条%s' % (a['名'], a['档'], '、'.join(sorted(tiers))))
                    if not a.get('星条'):
                        todo.append('技艺没有星条【%s】' % a['名'])
                if not arts:
                    todo.append('没写技艺')
                for g in gens:
                    tiers = set(x.split(':')[-1].split('·')[0] for x in g.get('星条', []))
                    if not g['档']:
                        todo.append('%s没写档【%s】' % (g['类'], g['名']))
                    elif tiers and g['档'] not in tiers:
                        todo.append('%s档跟星条不一样【%s】行%s／星条%s' % (g['类'], g['名'], g['档'], '、'.join(sorted(tiers))))
                # 跟旅伴条对：同一个人在别页（或这一页）当过旅伴
                short = who.split('·')[0]
                cross = []
                gnames = set(g['名'] for g in gens)
                for ck, cg, cab, cjx in comp.get(short, []):
                    cs = set(re.findall(r'(?:Special|Passive)【([^】]+)】', cab))
                    if cs & gnames or cg == ERA_GROUP[era]:
                        miss = sorted(gnames - cs)
                        cross.append({'页': ck, '能力': cab, '兼修': cjx, '对不上': miss})
                if any(c['对不上'] for c in cross) and cross:
                    if all(c['对不上'] for c in cross):
                        todo.append('生来星跟旅伴条不一样')
                zs = bool(re.search(zs_re(who, kind == '凡世至强' or len(by) == 1), e, re.M))
                state = ('新' if (arts and all(a['阶'] for a in arts) and has_jx)
                         else '半' if ((arts and all(a['阶'] for a in arts)) or has_jx) else '旧')
                recs.append({'纪': era, '页': key, '类别': kind, '人': who, '条目': h[3:], '文件': src,
                             '行': ls, '技艺': arts, '生来': gens, '兼修': has_jx, '有走势': zs, '旅伴': cross,
                             '样子': state, '要改': todo})
    order = {e: i for i, e in enumerate(ERA_ORDER)}
    recs.sort(key=lambda r: (order[r['纪']], 0 if not r['页'].endswith('.md') else 1, r['页'], r['文件'][0] if r['文件'] else ''))
    for i, r in enumerate(recs, 1):
        r['id'] = 'G%03d' % i
    same = collections.defaultdict(list)
    for r in recs:
        same[r['人'].split('·')[0]].append(r['id'])
    for r in recs:
        r['同一人'] = [x for x in same[r['人'].split('·')[0]] if x != r['id']]
    # 分份：照文件分，同一个文件不拆；一份二十到四十人，一纪一纪排
    byfile = collections.OrderedDict()
    for r in recs:
        f = r['文件'][0] if r['文件'] else '（找不到源稿）' + r['页']
        byfile.setdefault((r['纪'], f), []).append(r['id'])
    shares, cur, cur_era = [], None, None
    for (era, f), ids in byfile.items():
        g = ERA_GROUP[era]
        if cur is None or g != cur_era or (len(cur['人']) >= LO and len(cur['人']) + len(ids) > HI):
            cur = {'纪': g, '文件': [], '人': []}
            shares.append(cur)
            cur_era = g
        cur['文件'].append(f)
        cur['人'] += ids
    # 一纪末尾不到二十的，并进同纪前一份（并了不过五十）
    merged = []
    for s in shares:
        if merged and merged[-1]['纪'] == s['纪'] and len(s['人']) < LO and len(merged[-1]['人']) + len(s['人']) <= 50:
            merged[-1]['文件'] += s['文件']
            merged[-1]['人'] += s['人']
        else:
            merged.append(s)
    cnt = collections.Counter()
    fen = collections.OrderedDict()
    for s in merged:
        cnt[s['纪']] += 1
        name = '过_%s_%d' % (s['纪'], cnt[s['纪']])
        fen[name] = s
        for r in recs:
            if r['id'] in s['人']:
                r['份'] = name
    json.dump(recs, open(os.path.join(W, '清点.json'), 'w', encoding='utf-8', newline=NL), ensure_ascii=False, indent=1)
    json.dump(fen, open(os.path.join(W, '分份.json'), 'w', encoding='utf-8', newline=NL), ensure_ascii=False, indent=1)
    write_md(recs, fen, no_ab)
    print('人', len(recs), '份', len(fen))


def write_md(recs, fen, no_ab):
    c = collections.Counter((r['类别'], r['样子']) for r in recs)
    per = collections.Counter((r['纪'], r['类别']) for r in recs)
    todo = collections.Counter()
    for r in recs:
        for x in r['要改']:
            todo[re.sub(r'【.*', '', x)] += 1
    L = ['# 过条底子·清点（11-24，scan.py 出的，别手改，重跑覆盖）', '',
         '看的是拼好的四十七页和五纪补卷里的人物条、凡世至强条，带能力行（天赋【X】、被动【X】、技艺【X】、Special【X】、Passive【X】、Art【X】）的一人一条；旅伴条 11-20 过过了，不算。'
         '有分段源稿的页，文件那一栏是分段（交稿换回分段，再拼页）。逐人的细目在 清点.json。', '',
         '## 一、总数', '',
         '- 要过的一共 %d 人：凡世至强 %d，人物 %d。' % (len(recs), sum(1 for r in recs if r['类别'] == '凡世至强'), sum(1 for r in recs if r['类别'] == '人物')),
         '- 样子：' + '，'.join('%s%s %d' % (k[0], k[1], v) for k, v in sorted(c.items())) + '（新＝技艺带阶又有兼修，半＝只有一样，旧＝都没有）。',
         '- 没有能力行、这一轮不过的条：' + '，'.join('%s%s %d' % (k[0], k[1], v) for k, v in sorted(no_ab.items(), key=lambda x: (ERA_ORDER.index(x[0][0]), x[0][1]))) + '。',
         '', '## 二、各纪', '', '| 纪 | 凡世至强 | 人物 |', '|---|---|---|']
    for e in ERA_ORDER:
        L.append('| %s | %d | %d |' % (e, per[(e, '凡世至强')], per[(e, '人物')]))
    L += ['', '## 三、要改的几样（人次）', '']
    for k, v in todo.most_common():
        L.append('- %s：%d' % (k, v))
    L += ['', '## 四、分份', '']
    for n, s in fen.items():
        L.append('- %s：%d 人，%d 个文件（%s）' % (n, len(s['人']), len(s['文件']), '、'.join(os.path.basename(f) for f in s['文件'])))
    nolin = sum(1 for r in recs for a in r['技艺'] if not a.get('全谱'))
    noblk = sum(1 for r in recs for a in r['技艺'] if not a.get('星条'))
    cross = ['%s %s（%s）' % (r['id'], r['人'], '、'.join(c['页'] for c in r['旅伴'])) for r in recs if '生来星跟旅伴条不一样' in r['要改']]
    multi = collections.OrderedDict()
    for r in recs:
        if r['同一人']:
            multi.setdefault(r['人'].split('·')[0], set()).add(r['份'])
    L += ['', '## 五、看出来的几件', '',
          '1. 能力行都是旧样子：%d 人里没有一个带阶、没有一个有兼修。' % len(recs),
          '2. 主修技艺 %d 门次没有星条（11-20 技艺重洗没过，没有构成和阶那一行），%d 门次全谱里也没有。凡世至强手里的多是补完、跨进去的那一版，页上的星条写的是旅伴手里那一版，档对不上多半是有意的。阶照派活说明第三节第 1 件的尺子判。' % (noblk, nolin),
          '3. 天赋、被动没写档的大半是凡世至强，【能力｜】那一块里只写“传奇档”，没有 Normal 到 Unique 的档。',
          '4. 生来星名字跟旅伴条不一样的 %d 人：%s。多是 11-20 旅伴过条改了名、凡世至强那一条没跟上；塔隆·黑燧多一颗凝名以后露出来的宿火，是有意的。' % (len(cross), '；'.join(cross)),
          '5. 同一人几条：%s。凯撒索恩薇娅九条跨山铜纪、前传两份。' % '；'.join('%s（%s）' % (k, '、'.join(sorted(v))) for k, v in multi.items()),
          '6. 文森特·哈尔特和费伊·拉森在同一条同一行里（剑响处），清点里算一人。',
          '7. 没看的：迷宫纪1001年那一头（底卡的凡世至强、底卡洗稿、底卡新条目/活到今天的旧人.md 等），旅伴条（11-20 过过了），没有能力行的人物条（见第一节）。',
          '', '## 六、逐人', '']
    cur = None
    for r in recs:
        if r['份'] != cur:
            cur = r['份']
            L += ['', '### ' + cur, '']
        L.append('- %s｜%s｜%s｜%s｜%s｜要改：%s' % (r['id'], r['类别'], r['人'], '、'.join(r['文件']) or '找不到源稿', r['样子'], '；'.join(r['要改']) or '无'))
    open(os.path.join(W, '清点.md'), 'w', encoding='utf-8', newline=NL).write(NL.join(L) + NL)


if __name__ == '__main__':
    main()
