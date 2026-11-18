# -*- coding: utf-8 -*-
"""铺开·全卷核：各页的能力行、底座的法门、凡世至强的技艺行里写的技艺，跟星条的标题和档对不对得上。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/全卷核.py [页…] [--fix]

报四样：
  旧名   能力行里还写着改名以前的名字（改名.tsv、补艺.tsv 里的旧名）
  档     能力行里写的档跟这一页（或者它出处那一页）星条标题上的档不一样
  借     这一页没有这颗星的星条，是从别的页借来的，列出来看一眼出处的档
  无     哪一页都找不到这颗星的星条
--fix 只改最稳的一种：同一个人、旧名能唯一对到新名的能力行和底座，名字和档照出处那一页的星条换，括号里的一句话照出处那一页那个人的能力行抄。
"""
import io, os, re, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import 搭活 as D

SEG = re.compile(r'Art【([^】]+)】\s*[（(]\s*(Normal|Rare|Epic|Legend|Unique)\s*[，,]([^｜]*?)[)）]\s*(?=｜|。|、|，|$)')
SEG_LOOSE = re.compile(r'Art【([^】]+)】')


def all_pages():
    arts = D.read_tsv('全谱.tsv')
    comps = D.read_tsv('旅伴表.tsv')
    pages = []
    for r in arts + comps:
        if r['页'] not in pages:
            pages.append(r['页'])
    return pages, arts


def main():
    pages, arts = all_pages()
    want = [a for a in sys.argv[1:] if not a.startswith('--')]
    fix = '--fix' in sys.argv
    # 各页星条：名字 → 档
    titles = {}
    files = {}
    for p in pages:
        files[p] = D.page_files(p)
        t = {}
        for f in files[p]:
            for l in D.read_lines(f):
                m = D.STAR.match(D.bare(l))
                if m:
                    t[m.group(1).strip()] = m.group(3)
        titles[p] = t
    where = collections.defaultdict(list)   # 名字 → [(页, 档)]
    for p in pages:
        for n, t in titles[p].items():
            where[n].append((p, t))
    old2new = collections.defaultdict(set)
    retier = set()          # 这一轮改了档的技艺（新名）
    for r in arts:
        o = r['原技艺'] or r['旧名']
        if o and o != r['技艺']:
            old2new[o].add((r['页'], r['技艺'], r['补法'], r['持有人']))
        # 只算星条自己那一行改了档的。同门、新起的行是别人手里的头几课（骸银结环法莉瑟那一行就是），不能拿它去改借的人的档
        if r['新档'] and r['现阶'] and r['新档'] != r['现阶'] and r['补法'] not in ('同门', '新起'):
            retier.add(r['技艺'])
    # 出处那一页那个人的能力行里的那一段，抄给借的人用
    gloss = {}
    for p in pages:
        for f in files[p]:
            L = D.read_lines(f)
            for name, (s, e) in D.comp_blocks(L).items():
                for l in L[s:e]:
                    l = D.bare(l)
                    if l.startswith('能力：'):
                        for m in SEG.finditer(l):
                            if m.group(1) in titles[p]:
                                gloss[(m.group(1), name.split('·')[0])] = (m.group(2), m.group(3).strip(), p)
    rep = collections.defaultdict(list)
    nfix = 0
    for p in pages:
        if want and p not in want:
            continue
        for f in files[p]:
            L = D.read_lines(f)
            changed = False
            blocks = D.comp_blocks(L)
            owner_of = {}
            for name, (s, e) in blocks.items():
                for i in range(s, e):
                    owner_of[i] = name
            for i, raw in enumerate(L):
                l = D.bare(raw)
                if not (l.startswith('能力：') or l.startswith('底座：') or l.startswith('- 技艺【')):
                    continue
                who = owner_of.get(i, '')
                b = os.path.basename(f)
                if l.startswith('底座：'):
                    m = re.search(r'法门 ([^｜\s]+)\s*$', l)
                    if m:
                        n = m.group(1)
                        if n not in where and n in old2new:
                            cands = [x for x in old2new[n] if D.same_person(who, re.sub(r'（.*?）', '', x[3]).split('、')[0])] or list(old2new[n])
                            news = {x[1] for x in cands}
                            rep[p].append('旧名｜%s｜%s｜底座 法门 %s → %s' % (b, who, n, '／'.join(sorted(news))))
                            if fix and len(news) == 1:
                                L[i] = raw.replace('法门 ' + n, '法门 ' + list(news)[0])
                                changed = True
                                nfix += 1
                    continue
                segs = list(SEG.finditer(l)) if l.startswith('能力：') else []
                names = [m.group(1) for m in segs] if segs else SEG_LOOSE.findall(l) + re.findall(r'^- 技艺【([^】]+)】', l)
                for n in names:
                    seg = next((m for m in segs if m.group(1) == n), None)
                    tier = seg.group(2) if seg else ''
                    if n in titles[p]:
                        if tier and titles[p][n] != tier:
                            rep[p].append('档｜%s｜%s｜%s 能力行写 %s，这一页星条是 %s' % (b, who, n, tier, titles[p][n]))
                        continue
                    if n in where:
                        src = where[n]
                        if tier and all(t != tier for _, t in src):
                            rep[p].append('档｜%s｜%s｜%s 能力行写 %s，出处 %s' % (b, who, n, tier, '、'.join('%s是%s' % (D.short(pp), t) for pp, t in src)))
                            tiers = {t for _, t in src}
                            if fix and seg and n in retier and len(tiers) == 1:
                                g = gloss.get((n, who.split('·')[0]))
                                txt = g[1] if g else seg.group(3).strip()
                                L[i] = L[i].replace(seg.group(0), 'Art【%s】(%s，%s)' % (n, list(tiers)[0], txt))
                                changed = True
                                nfix += 1
                        else:
                            rep[p].append('借｜%s｜%s｜%s（%s）出处 %s' % (b, who, n, tier, '、'.join('%s·%s' % (D.short(pp), t) for pp, t in src)))
                        continue
                    if n in old2new:
                        cands = [x for x in old2new[n] if D.same_person(who, re.sub(r'（.*?）', '', x[3]).split('、')[0])]
                        news = {x[1] for x in (cands or old2new[n])}
                        rep[p].append('旧名｜%s｜%s｜%s → %s%s' % (b, who, n, '／'.join(sorted(news)), '' if cands else '（持有人对不上，手看）'))
                        if fix and len(news) == 1 and seg:
                            new = list(news)[0]
                            g = gloss.get((new, who.split('·')[0]))
                            tiers = {t for _, t in where.get(new, [])}
                            if g:
                                L[i] = L[i].replace(seg.group(0), 'Art【%s】(%s，%s)' % (new, g[0], g[1]))
                                changed = True
                                nfix += 1
                            elif len(tiers) == 1:
                                # 一家人共用的那一门：名字和档照出处换，括号里那一句留他自己的
                                L[i] = L[i].replace(seg.group(0), 'Art【%s】(%s，%s)' % (new, list(tiers)[0], seg.group(3).strip()))
                                changed = True
                                nfix += 1
                        continue
                    rep[p].append('无｜%s｜%s｜%s 哪一页都没有星条' % (b, who, n))
            if fix and changed:
                D.safe_write(f, '\n'.join(L))
    cnt = collections.Counter()
    for p in pages:
        if not rep[p]:
            continue
        print('== %s' % p)
        for x in rep[p]:
            cnt[x.split('｜')[0]] += 1
            if not x.startswith('借') or '--all' in sys.argv:
                print('  ' + x)
    print('合计', dict(cnt), ('改了 %d 处' % nfix) if fix else '')


if __name__ == '__main__':
    main()
