# -*- coding: utf-8 -*-
"""铺开·核至强：各页人物条、凡世至强、主线正文里说到技艺的地方，跟全谱的名字和档对不对得上。全卷核只管能力行，这一支管别处。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/核至强.py [页…] [--all-lines]

报三样（都只报，不改）：
  技艺行   「技艺【名】」起头的那一类（凡世至强、人物条），名字是旧名的、行里写的档跟全谱不一样的
  档句     正文里一句话点了某一门的名字（新名、旧名都算），又写着 Legend、补完，而全谱里这一门不是 Legend
  撤       行里带着这一轮撤掉的技艺名（带【】的）
设计备注、节首给作者看的话不查。"""
import io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 搭活 as D

TIER = re.compile(r'Normal|Rare|Epic|Legend|Unique')
JI = re.compile(r'(?<!Art)技艺\s*【([^】]+)】')
LEG = re.compile(r'补完到\s*Legend|到了?\s*Legend|Legend\s*那一版|Legend\s*版|是\s*Legend|成了?\s*Legend|承\s*Legend|传\s*Legend')


def main():
    arts = D.read_tsv('全谱.tsv')
    pages = []
    for r in arts + D.read_tsv('旅伴表.tsv'):
        if r['页'] not in pages:
            pages.append(r['页'])
    want = [a for a in sys.argv[1:] if not a.startswith('--')]
    tier = collections.defaultdict(set)      # 新名 → {档}
    old2new = collections.defaultdict(set)   # 旧名 → {新名}
    gone = set()                             # 撤掉、没有同名顶替的
    for r in arts:
        tier[r['技艺']].add(r['新档'] or r['现阶'])
        o = r['原技艺'] or r['旧名']
        if o and o != r['技艺']:
            if r['补法'] in ('新起', '同门'):
                gone.add(o)
            else:
                old2new[o].add(r['技艺'])
    gone -= set(tier)
    names = sorted(set(tier) | set(old2new), key=len, reverse=True)
    names = [n for n in names if len(n) >= 3]
    nm = re.compile('|'.join(re.escape(n) for n in names))
    cnt = collections.Counter()
    for p in pages:
        if want and p not in want:
            continue
        out = []
        for f in D.page_files(p):
            base = os.path.basename(f)
            if 'notes' in base or base in D.DUP:
                continue
            skip = False
            for i, raw in enumerate(D.read_lines(f), 1):
                l = D.bare(raw)
                if l.startswith('## ') or l.startswith('# '):
                    skip = ('设计备注' in l) or ('备注' in l and '羁绊' not in l and '旅途' not in l)
                if skip or l.startswith('> 条目设置') or l.startswith('### '):
                    continue
                for m in JI.finditer(l):
                    n = m.group(1)
                    said = set(TIER.findall(l[m.start():m.start() + 260]))
                    if n in old2new:
                        out.append('技艺行｜%s:%d｜旧名 %s → %s（%s）｜%s' % (base, i, n, '、'.join(sorted(old2new[n])),
                                   '、'.join(sorted(set().union(*[tier[x] for x in old2new[n]]))), l[max(0, m.start() - 8):m.start() + 150]))
                        cnt['旧名'] += 1
                    elif n in tier:
                        if said and not (said & (tier[n] | {'Unique'})):
                            out.append('技艺行｜%s:%d｜%s 全谱 %s，行里写 %s｜%s' % (base, i, n, '、'.join(sorted(tier[n])), '、'.join(sorted(said)), l[max(0, m.start() - 8):m.start() + 190]))
                            cnt['档'] += 1
                        elif 'Legend' in said and 'Legend' not in tier[n]:
                            out.append('技艺行｜%s:%d｜%s 全谱 %s，行里另写 Legend｜%s' % (base, i, n, '、'.join(sorted(tier[n])), l[max(0, m.start() - 8):m.start() + 190]))
                            cnt['档'] += 1
                    if n in gone:
                        out.append('撤｜%s:%d｜%s 这一轮撤了｜%s' % (base, i, n, l[max(0, m.start() - 8):m.start() + 120]))
                        cnt['撤'] += 1
                if '--all-lines' in sys.argv or LEG.search(l):
                    for m in LEG.finditer(l):
                        a, b = max(0, m.start() - 60), min(len(l), m.end() + 20)
                        seg = l[a:b]
                        hit = [x.group(0) for x in nm.finditer(seg)]
                        for n in hit:
                            ts = tier[n] if n in tier else set().union(*[tier[x] for x in old2new[n]])
                            if 'Legend' not in ts and not JI.search(l[max(0, a - 4):b]):
                                out.append('档句｜%s:%d｜%s 全谱 %s｜…%s…' % (base, i, n, '、'.join(sorted(ts)), seg))
                                cnt['档句'] += 1
                for g in gone:
                    if '【%s】' % g in l and not JI.search(l):
                        out.append('撤｜%s:%d｜【%s】｜%s' % (base, i, g, l[:110]))
                        cnt['撤'] += 1
        if out:
            print('== %s' % p)
            seen = set()
            for o in out:
                if o not in seen:
                    seen.add(o)
                    print('  ' + o)
    print('合计', dict(cnt))


if __name__ == '__main__':
    main()
