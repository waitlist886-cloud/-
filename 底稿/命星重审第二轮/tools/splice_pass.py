#!/usr/bin/env python3
# 旅伴过条（11-20）：把 交稿/pass_*.md 换回源稿。
#   python -I -X utf8 底稿/命星重审第二轮/tools/splice_pass.py          只报
#   python -I -X utf8 底稿/命星重审第二轮/tools/splice_pass.py --apply  写盘，另写 收稿/过条记录.json
# 每位旅伴：「## 旅途同行：名（」那一条里，能力行整行换；能力行后头插一行兼修（无就不插）；技艺走势那一行末尾接走势补。
# 【星条】：照标题名字整块换（Special、Passive）。【并星】：旧星在这一页没人再用了就删旧块，这个人的旅伴条和背景条里【旧】换成【新】。
# 核：新能力行里 Special、Passive、Art 的名字跟原来比，只许并星那几处不同；Art 名字必须一样。
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from splice_rare import sources, W  # noqa: E402

NL = chr(10)


def parse(t):
    t = t.replace('\r\n', NL)
    people, stars, merges, kept = [], [], [], []
    body, _, tail = t.partition('【星条】')
    if not _:
        m = re.search(r'^【(并星|没改)】', t, re.M)
        body, tail = (t[:m.start()], t[m.start():]) if m else (t, '')
    for seg in re.split(r'^={4,}\s*$', body, flags=re.M):
        m = re.search(r'^【旅伴】(.+)$', seg, re.M)
        if not m:
            continue
        g = lambda lab: (re.search(r'^' + lab + r'：(.*)$', seg, re.M) or [None, ''])[1].strip()
        people.append({'who': m.group(1).strip(), 'ab': g('能力'), 'jx': g('兼修'), 'zs': g('走势补')})
    for m in re.finditer(r'^### (\S+) \((Special|Passive) \| (\w+)\)\n.*?(?=^### |^【|\Z)', tail, re.S | re.M):
        stars.append((m.group(1), m.group(0).rstrip() + NL + NL))
    for m in re.finditer(r'^【并星】(.+?)｜(.+?)→(.+?)｜(.*)$', tail, re.M):
        merges.append(tuple(x.strip() for x in m.groups()))
    for m in re.finditer(r'^【没改】(.*)$', tail, re.M):
        kept.append(m.group(1))
    return people, stars, merges, kept


def names(ab):
    return re.findall(r'(Special|Passive|Art)【([^】]+)】', ab)


def main(apply):
    idx = json.load(open(os.path.join(W, '材料', '索引.json'), encoding='utf-8'))
    files, log, warn = {}, {'people': 0, 'jx': 0, 'stars': 0, 'merge': [], 'kept': []}, []

    def load(src):
        if src not in files:
            files[src] = open(src, encoding='utf-8', newline='').read()
        return files[src]

    def save(src, tn, crlf):
        files[src] = tn.replace(NL, '\r\n') if crlf else tn

    bykey = {}
    for f in sorted(glob.glob(os.path.join(W, '交稿', 'pass_*.md'))):
        key = re.match(r'pass_(.+)_\d+[a-f]?\.md$', os.path.basename(f)).group(1)
        p, s, mg, kp = parse(open(f, encoding='utf-8').read())
        b = bykey.setdefault(key, [[], [], [], []])
        for i, x in enumerate((p, s, mg, kp)):
            b[i] += x
    for key, (people, stars, merges, kept) in bykey.items():
        srcs = sources(key, idx[key]['file'])
        mg_by = {}
        for who, old, new, why in merges:
            mg_by.setdefault(who.split('·')[0], []).append((old, new))
            log['merge'].append('%s｜%s｜%s→%s｜%s' % (key, who, old, new, why))
        log['kept'] += ['%s｜%s' % (key, x) for x in kept]
        for p in people:
            short = p['who'].split('·')[0]
            hit = False
            for src in srcs:
                raw = load(src)
                crlf = '\r\n' in raw
                tn = raw.replace('\r\n', NL)
                em = re.search(r'^## 旅途同行：' + re.escape(short) + r'[·（][^\n]*\n.*?(?=^## (?!裁定锁)|\Z)', tn, re.S | re.M)
                if not em:
                    continue
                e = em.group(0)
                om = re.search(r'^能力：.*$', e, re.M)
                if not om:
                    continue
                old_ab = om.group(0)
                new_ab = p['ab'] if p['ab'].startswith('能力：') else '能力：' + p['ab']
                o, n = names(old_ab), names(new_ab)
                ren = dict(mg_by.get(short, []))
                o2 = [(k, ren.get(x, x)) for k, x in o]
                if [x for _, x in o2] != [x for _, x in n]:
                    warn.append('%s %s：能力行的星名对不上，没换｜原 %s｜新 %s' % (key, p['who'], [x for _, x in o], [x for _, x in n]))
                    hit = True
                    break
                if not re.search(r'Art【[^】]+】\(\w+·[一二三四五]阶', new_ab):
                    warn.append('%s %s：Art 没带阶' % (key, p['who']))
                rep = new_ab
                if p['jx'] and not p['jx'].startswith('无'):
                    rep += NL + '兼修：' + p['jx']
                    log['jx'] += 1
                e2 = e.replace(old_ab, rep, 1)
                if p['zs'] and not p['zs'].startswith('无'):
                    zm = re.search(r'^技艺走势：.*$', e2, re.M)
                    if zm:
                        z = zm.group(0).rstrip()
                        e2 = e2.replace(zm.group(0), z + ('' if z.endswith('。') else '。') + p['zs'], 1)
                    else:
                        warn.append('%s %s：没有技艺走势那一行，走势补没接' % (key, p['who']))
                for old, new in mg_by.get(short, []):
                    e2 = e2.replace('【%s】' % old, '【%s】' % new)
                tn = tn[:em.start()] + e2 + tn[em.end():]
                bm = re.search(r'^## 旅途同行·背景：' + re.escape(short) + r'[^\n]*\n.*?(?=^## (?!裁定锁)|\Z)', tn, re.S | re.M)
                if bm:
                    b2 = bm.group(0)
                    for old, new in mg_by.get(short, []):
                        b2 = b2.replace('【%s】' % old, '【%s】' % new)
                    tn = tn[:bm.start()] + b2 + tn[bm.end():]
                save(src, tn, crlf)
                hit = True
                log['people'] += 1
                break
            if not hit:
                warn.append('%s %s：源稿里找不到旅伴条' % (key, p['who']))
        for nm, blk in stars:
            done = False
            for src in srcs:
                raw = load(src)
                crlf = '\r\n' in raw
                tn = raw.replace('\r\n', NL)
                om = re.search(r'^### ' + re.escape(nm) + r' \((?:Special|Passive) \| \w+\)\n.*?(?=^### |^## |^> 条目设置|\Z)', tn, re.S | re.M)
                if not om:
                    continue
                o = om.group(0)
                tn = tn[:om.start()] + (blk if o.endswith(NL + NL) else blk.rstrip(NL) + NL) + tn[om.end():]
                save(src, tn, crlf)
                done = True
                log['stars'] += 1
            if not done:
                warn.append('%s【%s】：源稿里找不到这颗星的旧块（并星的新星要在页上或底卡里有）' % (key, nm))
        for who, old, new, why in merges:
            still = False
            for src in srcs:
                if re.search(r'^能力：.*【' + re.escape(old) + r'】', load(src).replace('\r\n', NL), re.M):
                    still = True
            if still:
                continue
            for src in srcs:
                raw = load(src)
                crlf = '\r\n' in raw
                tn = raw.replace('\r\n', NL)
                om = re.search(r'^### ' + re.escape(old) + r' \((?:Special|Passive) \| \w+\)\n.*?(?=^### |^## |^> 条目设置|\Z)', tn, re.S | re.M)
                if om:
                    tn = tn[:om.start()] + tn[om.end():]
                    save(src, tn, crlf)
    print('换了 %d 位，兼修 %d 行，星条 %d 块，并星 %d，没改 %d' % (log['people'], log['jx'], log['stars'], len(log['merge']), len(log['kept'])))
    for x in warn:
        print('  看：', x)
    if apply:
        n = 0
        for src, t in files.items():
            if open(src, encoding='utf-8', newline='').read() != t:
                open(src, 'w', encoding='utf-8', newline='').write(t)
                n += 1
        json.dump(log, open(os.path.join(W, '收稿', '过条记录.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('写了 %d 个文件' % n)


if __name__ == '__main__':
    main('--apply' in sys.argv)
