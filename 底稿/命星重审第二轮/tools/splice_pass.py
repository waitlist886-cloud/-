#!/usr/bin/env python3
# 旅伴过条（11-20）：把 交稿/pass_*.md 换回源稿。
#   python -I -X utf8 底稿/命星重审第二轮/tools/splice_pass.py          只报
#   python -I -X utf8 底稿/命星重审第二轮/tools/splice_pass.py --apply  写盘，另写 收稿/过条记录.json
# 每位旅伴：「## 旅途同行：名（」那一条里（所有源稿里对得上的都换），能力行整行换；能力行后头插一行兼修（无就不插）；
# 技艺走势那一行末尾接走势补。
# 核：新能力行跟原来比，Art 名字和次序要一样（挪进兼修的那一门可以从能力行里拿掉）；Special、Passive 同一位置换了名字的，
# 当改名（跟【并星】一样处理），这个人的旅伴条和背景条里【旧】换成【新】。
# 【星条】：照标题名字整块换。页上没有这个名字的，是改名改出来的：旧名这一页还有人用就把新块插在旧块前头，没人用就顶掉旧块。
# 改名以后旧名这一页没人用了，旧块删掉。
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
CRLF = chr(13) + chr(10)


def block_re(name):
    return re.compile(r'^### ' + re.escape(name) + r' \((?:Special|Passive) \| \w+\)\n.*?(?=^### |^## |^> 条目设置|\Z)', re.S | re.M)


def parse(t):
    t = t.replace(CRLF, NL)
    people, stars, merges, kept = [], [], [], []
    body, sep, tail = t.partition('【星条】')
    if not sep:
        m = re.search(r'^【(并星|没改)】', t, re.M)
        body, tail = (t[:m.start()], t[m.start():]) if m else (t, '')
    for seg in re.split(r'^={4,}\s*$', body, flags=re.M):
        m = re.search(r'^【旅伴】(.+)$', seg, re.M)
        if not m:
            continue

        def g(lab):
            mm = re.search(r'^' + lab + r'：(.*)$', seg, re.M)
            return mm.group(1).strip() if mm else ''
        people.append({'who': m.group(1).strip(), 'ab': g('能力'), 'jx': g('兼修'), 'zs': g('走势补')})
    # 11-20 修：原来的先行断言是 ^【，碰到正文头一行【调用】就停了，星条只剩标题（fill_empty.py 补回）
    for m in re.finditer(r'^### (\S+) \((Special|Passive) \| (\w+)\)\n.*?(?=^### |^【(?:并星|没改|星条|旅伴)】|^={4,}|\Z)', tail, re.S | re.M):
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

    def text(src):
        return load(src).replace(CRLF, NL)

    def save(src, tn, crlf):
        files[src] = tn.replace(NL, CRLF) if crlf else tn

    bykey = {}
    for f in sorted(glob.glob(os.path.join(W, '交稿', 'pass_*.md'))):
        key = re.match(r'pass_(.+)_\d+[a-f]?\.md$', os.path.basename(f)).group(1)
        parts = parse(open(f, encoding='utf-8').read())
        b = bykey.setdefault(key, [[], [], [], []])
        for i, x in enumerate(parts):
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
            hit = matched = False
            new_ab = p['ab'] if p['ab'].startswith('能力：') else '能力：' + p['ab']
            n = names(new_ab)
            for src in srcs:
                raw = load(src)
                crlf = CRLF in raw
                tn = raw.replace(CRLF, NL)
                em = re.search(r'^## 旅途同行：' + re.escape(short) + r'[·（][^\n]*\n.*?(?=^## (?!裁定锁)|\Z)', tn, re.S | re.M)
                if not em:
                    continue
                e = em.group(0)
                om = re.search(r'^能力：.*$', e, re.M)
                if not om:
                    continue
                hit = True
                old_ab = om.group(0)
                o = names(old_ab)
                ren = dict(mg_by.get(short, []))
                o2 = [(k, ren.get(x, x), x) for k, x in o
                      if not (k == 'Art' and ('【%s】' % x) in p['jx'] and ('【%s】' % x) not in new_ab)]
                if len(o2) != len(n) or any((a[0] == 'Art') != (b[0] == 'Art') or (a[0] == 'Art' and a[1] != b[1]) for a, b in zip(o2, n)):
                    continue
                for (k, x, orig), (_, y) in zip(o2, n):
                    if x != y and (orig, y) not in mg_by.get(short, []):
                        mg_by.setdefault(short, []).append((orig, y))
                        log['merge'].append('%s｜%s｜%s→%s｜同一位置换了名字' % (key, p['who'], orig, y))
                if not re.search(r'Art【[^】]+】\(\w+·[一二三四五]阶', new_ab):
                    warn.append('%s %s：Art 没带阶' % (key, p['who']))
                rep = new_ab
                if p['jx'] and not p['jx'].startswith('无'):
                    rep += NL + '兼修：' + p['jx']
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
                if not matched:
                    log['people'] += 1
                    if p['jx'] and not p['jx'].startswith('无'):
                        log['jx'] += 1
                matched = True
            if not hit:
                warn.append('%s %s：源稿里找不到旅伴条' % (key, p['who']))
            elif not matched:
                warn.append('%s %s：能力行的星名对不上，没换｜新 %s' % (key, p['who'], [x for _, x in n]))
        renames = [(o_, n_) for lst in mg_by.values() for o_, n_ in lst]

        def held(name):
            return any(re.search(r'^能力：.*【' + re.escape(name) + r'】', text(s2), re.M) for s2 in srcs)

        for nm, blk in stars:
            done = False
            for src in srcs:
                raw = load(src)
                crlf = CRLF in raw
                tn = raw.replace(CRLF, NL)
                om = block_re(nm).search(tn)
                if not om:
                    continue
                o = om.group(0)
                tn = tn[:om.start()] + (blk if o.endswith(NL + NL) else blk.rstrip(NL) + NL) + tn[om.end():]
                save(src, tn, crlf)
                done = True
            if not done:
                for old in [o_ for o_, n_ in renames if n_ == nm]:
                    keep_old = held(old)
                    for src in srcs:
                        raw = load(src)
                        crlf = CRLF in raw
                        tn = raw.replace(CRLF, NL)
                        om = block_re(old).search(tn)
                        if not om:
                            continue
                        o = om.group(0)
                        body = blk if o.endswith(NL + NL) else blk.rstrip(NL) + NL
                        tn = tn[:om.start()] + (body + o if keep_old else body) + tn[om.end():]
                        save(src, tn, crlf)
                        done = True
                    if done:
                        break
            if not done:
                for old in [o_ for o_, n_ in renames if n_ == nm]:
                    owner = [w for w, lst in mg_by.items() if (old, nm) in lst]
                    for src in srcs:
                        raw = load(src)
                        crlf = CRLF in raw
                        tn = raw.replace(CRLF, NL)
                        em = re.search(r'^## 旅途同行：' + re.escape(owner[0]) + r'[·（][^\n]*\n.*?^能力：(.*)$', tn, re.S | re.M) if owner else None
                        if not em:
                            continue
                        for other in re.findall(r'(?:Special|Passive)【([^】]+)】', em.group(1)):
                            om = block_re(other).search(tn) if other != nm else None
                            if om:
                                tn = tn[:om.start()] + blk + tn[om.start():]
                                save(src, tn, crlf)
                                done = True
                                warn.append('%s【%s】：旧星 %s 页上没有块（底卡的），新块插在 %s 前头' % (key, nm, old, other))
                                break
                        if done:
                            break
                    if done:
                        break
            if not done:
                owner = [p['who'].split('·')[0] for p in people if ('【%s】' % nm) in p['ab']]
                for src in srcs:
                    raw = load(src)
                    crlf = CRLF in raw
                    tn = raw.replace(CRLF, NL)
                    em = re.search(r'^## 旅途同行：' + re.escape(owner[0]) + r'[·（][^\n]*\n.*?^能力：(.*)$', tn, re.S | re.M) if owner else None
                    if not em:
                        continue
                    for other in re.findall(r'(?:Special|Passive|Art)【([^】]+)】', em.group(1)):
                        om = re.search(r'^### ' + re.escape(other) + r' \((?:Special|Passive|Art) \| \w+\)\n', tn, re.M) if other != nm else None
                        if om:
                            tn = tn[:om.start()] + blk + tn[om.start():]
                            save(src, tn, crlf)
                            done = True
                            warn.append('%s【%s】：页上原来没有块（底卡池子的），给 %s 添了一块，插在 %s 前头' % (key, nm, owner[0], other))
                            break
                    if done:
                        break
            if done:
                log['stars'] += 1
            else:
                warn.append('%s【%s】：源稿里找不到这颗星的旧块，也不是谁改名改出来的' % (key, nm))
        for old, new in renames:
            if held(old):
                continue
            for src in srcs:
                raw = load(src)
                crlf = CRLF in raw
                tn = raw.replace(CRLF, NL)
                om = block_re(old).search(tn)
                if om:
                    tn = tn[:om.start()] + tn[om.end():]
                    save(src, tn, crlf)
            if not any(block_re(new).search(text(s2)) for s2 in srcs):
                warn.append('%s：%s 改成 %s，页上没有【%s】的星条（底卡里有就不碍事）' % (key, old, new, new))
    print('换了 %d 位，兼修 %d 行，星条 %d 块，并星和改名 %d，没改 %d' % (log['people'], log['jx'], log['stars'], len(log['merge']), len(log['kept'])))
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
