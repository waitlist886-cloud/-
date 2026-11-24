#!/usr/bin/env python3
# DLC 切包的引用扫描（11-24）。只读，不改卡、不改源稿。
#   python -I -X utf8 底稿/DLC/tools/refscan.py <卡.json> <包名>[+<包名>…] [<包名>…] [--out 报告.json] [--show 20]
#   python -I -X utf8 底稿/DLC/tools/refscan.py <卡.json> --folder '^57·' --title '^大图书馆｜'
# 包名照同目录 packs.json；用 + 连起来的几个包算一回切出去（比方 羁绊+支线+神谱+大图书馆），空格隔开的各扫各的。
#
# 拿“切出去的那一堆”（下称 DLC）跟“本体剩下的”（本体＝卡里别的条目，加主提示词、前置词、后置词）对一遍：
#   硬引用（会落空的）：本体正文里
#     · 「X」，X 是 DLC 条目的全名、去掉纪名的名字（类｜名）、或｜后头那一截（三个字以上）；
#     · ……X那一条（照X那一条、见X那一条），X 的某个后缀是上面那几样；
#     · 正文里直接写出 DLC 条目的全名（不带括号）；
#     · 本体条目的触发词、黑名单里写着 DLC 条目的名字（§预载 那种枚举）。
#     同一个名字本体里也有条目（同名的另一条）的不算落空。
#   软提及（不落空，但模型只拿到一个名字）：DLC 条目名里的专名（羁绊的“X之章”、支线｜后头那一截、书名《X》、神名……）
#     出现在本体正文里、本体又没有以它为题的条目。专属羁绊那一行、人物条的著作那一行都在这里。
#   反向：DLC 条目引到同一回别的包里的条目（跨包依赖）；DLC 里有没有常亮条目（触发 /^/ 这一类）；靠 §预载 叫醒的条数。
import collections
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
MB = 1000 * 1000
ERA_HEAD = re.compile(r'^(?:月银纪|纷争纪|山铜纪|迷宫纪)·')
STOP = set('一条 那一条 总则 规则 羁绊 支线 神谱'.split())


def text_of(e):
    if e.get('contentMethod') == 'weighted':
        return '\n'.join(x.get('content', '') for x in e.get('contents') or [])
    return e.get('content') or ''


def title_of(e):
    for l in text_of(e).split('\n'):
        if l.strip():
            return l.strip().lstrip('#').strip()
    return ''


def nbytes(e):
    return len(json.dumps(e, ensure_ascii=False, separators=(',', ':')).encode('utf-8')) + 1


def names_of(t):
    """一条标题能被别处叫的几种名字：全名、去掉纪名的（类｜名）、｜后头那一截。"""
    out = {t}
    t2 = ERA_HEAD.sub('', t)
    out.add(t2)
    if '｜' in t:
        tail = t.split('｜', 1)[1]
        if len(tail) >= 3 and tail not in STOP:
            out.add(tail)
        # 遗物·纷争纪｜剑「半拍长歌」这种，别处叫它“遗物半拍长歌”“半拍长歌”
        for x in re.findall(r'「([^」]{2,30})」', tail):
            out.add(x)
            out.add(t.split('·', 1)[0] + x)
    return {n for n in out if len(n) >= 2}


def soft_names(t, txt):
    """DLC 条目里的专名：｜后头那一截按 · 拆开的每一节（四个字以上，或带“之章”），书名《X》。"""
    out = set()
    if t.startswith('大图书馆｜'):
        # 书名只认带书名号的写法（《X》），不然“天亮以前”“传奇之名”这类寻常字会刷屏
        return {'《%s》' % m for m in re.findall(r'《([^》\n]{2,30})》', txt)}
    if '｜' in t:
        tail = t.split('｜', 1)[1]
        parts = [p.strip() for p in re.split(r'[·，、]', tail)]
        if any(p.endswith('之章') for p in parts):
            # 羁绊：只认章名，章后头的题多是寻常话
            out |= {p for p in parts if p.endswith('之章')}
        elif len(parts) == 1:
            out.add(parts[0])                       # 神名、书名这类一整截的
        else:
            out |= {p for p in parts[1:] if len(p) >= 5}   # 支线：地名·事名，只认事名，五个字以上
    return {n for n in out if n not in STOP and len(n) >= 3}


def load_packs():
    return json.load(open(os.path.join(HERE, 'packs.json'), encoding='utf-8'))


def select(lb, spec):
    """spec: dict(folders=[…], titles=[…], keep_titles=[…])。返回命中的下标集合。"""
    fo = [re.compile(x) for x in spec.get('folders') or []]
    ti = [re.compile(x) for x in spec.get('titles') or []]
    kp = [re.compile(x) for x in spec.get('keep_titles') or []]
    hit = set()
    for i, e in enumerate(lb):
        t = title_of(e)
        if any(r.search(e.get('folder') or '') for r in fo) or any(r.search(t) for r in ti):
            if not any(r.search(t) for r in kp):
                hit.add(i)
    return hit


def always_on(e):
    tw = e.get('triggerWords') or []
    return any(w in ('/^/', '/[\\s\\S]/', '/./', '/[\\s\\S]*/') for w in tw)


class Scan:
    def __init__(self, card):
        self.card = card
        self.lb = card['prompt']['lorebook']
        self.titles = [title_of(e) for e in self.lb]
        self.texts = [text_of(e) for e in self.lb]

    def name_index(self, idx):
        d = collections.defaultdict(set)
        for i in idx:
            for n in names_of(self.titles[i]):
                d[n].add(i)
        return d

    def run(self, cut, others=None):
        """cut：切出去的下标；others：同一回切出去的别的包 {包名: 下标集合}（查跨包）。"""
        lb, T = self.lb, self.titles
        body = [i for i in range(len(lb)) if i not in cut]
        cut_names = self.name_index(cut)
        body_names = self.name_index(body)
        # 整个文件夹都切出去的，文件夹名（「27·人物羁绊剧情」、去掉编号的“人物羁绊剧情”）也算 DLC 的名字
        fold_all = collections.defaultdict(lambda: [0, 0])
        for i, e in enumerate(lb):
            fold_all[e.get('folder') or ''][1 if i in cut else 0] += 1
        for f, (nb, nc) in fold_all.items():
            if f and nc and not nb:
                for n in (f, re.sub(r'^\d+·', '', f)):
                    if len(n) >= 4:
                        cut_names[n].add(-1)
        dangling = {n: v for n, v in cut_names.items() if n not in body_names}
        heads = sorted({m.group(0) for i in cut for m in [re.match(r'^[^｜\n]{1,16}｜', T[i])] if m}, key=len, reverse=True)
        head_re = re.compile('|'.join(re.escape(h) for h in heads)) if heads else None
        by_head = collections.defaultdict(list)
        for i in cut:
            m = re.match(r'^[^｜\n]{1,16}｜', T[i])
            if m and T[i] in dangling:
                by_head[m.group(0)].append(T[i])
        for h in by_head:
            by_head[h].sort(key=len, reverse=True)

        hard = []          # (来源, 方式, 引到的名字, 片段)
        seen = set()

        def add(src, how, name, ctx):
            k = (src, name)
            if k in seen:
                return
            seen.add(k)
            hard.append((src, how, name, ctx))

        def scan_text(src, s):
            for m in re.finditer(r'「([^」\n]{1,60})」', s):
                x = m.group(1)
                for j in range(len(x)):
                    suf = x[j:]
                    if suf in body_names:
                        break
                    if suf in dangling:
                        add(src, '「」', suf, s[max(0, m.start() - 20):m.end() + 10])
                        break
            for m in re.finditer(r'([^，。；、\n「」（）：]{2,80}?)那一条', s):
                x = m.group(1)
                for j in range(len(x)):
                    suf = x[j:]
                    if suf in body_names:
                        break
                    if suf in dangling:
                        add(src, '那一条', suf, s[max(0, m.start() - 10):m.end() + 5])
                        break
            if head_re:
                for m in head_re.finditer(s):
                    for t in by_head.get(m.group(0), ()):
                        if s.startswith(t, m.start()):
                            add(src, '全名', t, s[max(0, m.start() - 20):m.start() + len(t) + 10])
                            break

        for k in ('systemPrompt', 'headPrompt', 'rearPrompt'):
            scan_text('〔%s〕' % k, self.card['prompt'].get(k) or '')
        for i in body:
            scan_text(i, self.texts[i])

        # 触发、黑名单里写着 DLC 条目的名字
        trig = []
        long_names = [n for n in dangling if len(n) >= 4]
        for i in body:
            e = lb[i]
            ws = '\n'.join((e.get('triggerWords') or []) + (e.get('blackListWords') or []))
            for n in long_names:
                if n in ws:
                    trig.append((i, n))
                    break

        # 软提及
        body_title_blob = '\n'.join(T[i] for i in body)
        body_trig_blob = '\n'.join('\n'.join(lb[i].get('triggerWords') or []) for i in body)
        soft_src = collections.defaultdict(set)   # 名字 → DLC 里哪几条有它
        for i in cut:
            for n in soft_names(T[i], self.texts[i]):
                soft_src[n].add(i)
        blob = '\x00'.join(self.texts[i] for i in body)
        starts = []
        pos = 0
        for i in body:
            starts.append(pos)
            pos += len(self.texts[i]) + 1
        import bisect
        soft = collections.Counter()      # 名字 → 本体里提到它的条数
        soft_ex = {}
        covered = 0
        for n in soft_src:
            if n in body_title_blob:
                covered += 1
                continue
            p = blob.find(n)
            hits = set()
            while p >= 0:
                k = bisect.bisect_right(starts, p) - 1
                hits.add(body[k])
                p = blob.find(n, p + 1)
            if hits:
                soft[n] = len(hits)
                k0 = min(hits)
                q = self.texts[k0].find(n)
                soft_ex[n] = (k0, self.texts[k0][max(0, q - 20):q + len(n) + 15])

        # 反向：DLC 引到同一回别的包
        cross = []
        if others:
            for pname, idx in others.items():
                if not idx:
                    continue
                o_names = self.name_index(idx)
                for i in cut:
                    s = self.texts[i]
                    for m in re.finditer(r'「([^」\n]{1,60})」|([^，。；、\n「」（）：]{2,80}?)那一条', s):
                        x = m.group(1) or m.group(2)
                        for j in range(len(x)):
                            if x[j:] in body_names and x[j:] not in o_names:
                                break
                            if x[j:] in o_names and x[j:] not in cut_names:
                                cross.append((i, pname, x[j:]))
                                break
        return dict(body=body, hard=hard, trig=trig, soft=soft, soft_ex=soft_ex, soft_total=len(soft_src),
                    soft_covered=covered, cross=cross,
                    always=[i for i in cut if always_on(lb[i])],
                    preload=sum(1 for i in cut if any('§预载' in w for w in lb[i].get('triggerWords') or [])),
                    count=len(cut), bytes=sum(nbytes(lb[i]) for i in cut))


def fmt_src(sc, s):
    if isinstance(s, int):
        return '%s／%s' % (sc.lb[s].get('folder'), sc.titles[s][:40])
    return s


def main():
    argv = sys.argv[1:]
    out = None
    show = 20
    if '--out' in argv:
        k = argv.index('--out'); out = argv[k + 1]; del argv[k:k + 2]
    if '--show' in argv:
        k = argv.index('--show'); show = int(argv[k + 1]); del argv[k:k + 2]
    adhoc = dict(folders=[], titles=[])
    while '--folder' in argv:
        k = argv.index('--folder'); adhoc['folders'].append(argv[k + 1]); del argv[k:k + 2]
    while '--title' in argv:
        k = argv.index('--title'); adhoc['titles'].append(argv[k + 1]); del argv[k:k + 2]
    card = json.load(open(argv[0], encoding='utf-8'))
    packs = load_packs()
    sc = Scan(card)
    lb = sc.lb
    total_b = sum(nbytes(e) for e in lb)
    runs = []
    if adhoc['folders'] or adhoc['titles']:
        runs.append(('临时', ['临时'], {'临时': select(lb, adhoc)}))
    for a in argv[1:]:
        names = a.split('+')
        runs.append((a, names, {n: select(lb, packs[n]) for n in names}))
    report = {}
    print('卡 %s：世界书 %d 条，条目合计 %.2f MB' % (os.path.basename(argv[0]), len(lb), total_b / MB))
    for label, names, sel in runs:
        cut = set().union(*sel.values())
        r = sc.run(cut, others=sel if len(sel) > 1 else None)
        print('\n=== %s：%d 条，%.3f MB（占世界书 %.1f%%）' % (label, r['count'], r['bytes'] / MB, 100 * r['bytes'] / total_b))
        for n in names:
            if len(names) > 1:
                print('    %s %d 条 %.3f MB' % (n, len(sel[n]), sum(nbytes(lb[i]) for i in sel[n]) / MB))
        print('  硬引用（会落空）%d 处，来自 %d 条本体条目' % (len(r['hard']), len({h[0] for h in r['hard']})))
        by_how = collections.Counter(h[1] for h in r['hard'])
        if by_how:
            print('    按写法：', dict(by_how))
        by_fold = collections.Counter((lb[h[0]].get('folder') if isinstance(h[0], int) else h[0]) for h in r['hard'])
        if by_fold:
            print('    按来源文件夹：', dict(by_fold.most_common(12)))
        for h in r['hard'][:show]:
            print('    · %s ←%s→ %s ｜%s' % (fmt_src(sc, h[0]), h[1], h[2], h[3].replace('\n', '⏎')))
        print('  本体触发、黑名单里写着它们的名字：%d 条' % len(r['trig']))
        for i, n in r['trig'][:min(show, 8)]:
            print('    · %s ：%s' % (fmt_src(sc, i), n))
        print('  软提及：专名 %d 个，本体有同名条目的 %d 个，本体正文里只剩名字的 %d 个（共 %d 处条目）' % (
            r['soft_total'], r['soft_covered'], len(r['soft']), sum(r['soft'].values())))
        for n, c in r['soft'].most_common(min(show, 10)):
            k0, ctx = r['soft_ex'][n]
            print('    · %s ×%d 例 %s ｜%s' % (n, c, fmt_src(sc, k0), ctx.replace('\n', '⏎')))
        print('  DLC 里常亮的条目 %d 条；触发里认 §预载 的 %d 条' % (len(r['always']), r['preload']))
        if r['cross']:
            print('  跨包引用 %d 处：' % len(r['cross']))
            for i, p, n in r['cross'][:show]:
                print('    · %s → 〔%s〕%s' % (fmt_src(sc, i), p, n))
        report[label] = dict(count=r['count'], bytes=r['bytes'], hard=[[fmt_src(sc, h[0]), h[1], h[2], h[3]] for h in r['hard']],
                             trig=[[fmt_src(sc, i), n] for i, n in r['trig']], soft=dict(r['soft']),
                             cross=[[fmt_src(sc, i), p, n] for i, p, n in r['cross']], always=len(r['always']), preload=r['preload'])
    if out:
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
        print('\n明细写在', out)


if __name__ == '__main__':
    main()
