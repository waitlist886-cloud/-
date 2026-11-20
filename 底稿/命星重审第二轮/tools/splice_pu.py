#!/usr/bin/env python3
# 命星重审第二轮·铺开收稿（11-20）。交稿在 交稿/pu_*.md，格式照 派活说明_铺开.md 第七节。
#   python -I -X utf8 底稿/命星重审第二轮/tools/splice_pu.py parse          解析交稿，写 收稿/记录.json 和 收稿/改名表.md，报缺的、撞的
#   （中间一步照改名表跑 tools/rename_stars.py --map 收稿/改名表.md --apply --extra …，全卷换名）
#   python -I -X utf8 底稿/命星重审第二轮/tools/splice_pu.py blocks [--apply] 按新名把星条整块换上（所有源稿里同名的块一起换）
#   python -I -X utf8 底稿/命星重审第二轮/tools/splice_pu.py lines [--apply]  换旅伴条的能力行，添或换技艺走势
# 换回以后照各页的拼法重拼。
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
W = os.path.join(ROOT, '底稿', '命星重审第二轮')
OUTD = os.path.join(W, '收稿')
SRC = ['月银纪史诗/第*歌_*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md',
       '纷争纪/parts/*.md', '纷争纪/parts[2-7]/*.md', '山铜纪/parts[1-6]/*.md', '迷宫纪前传/parts[1-6]/*.md',
       '山铜纪/补卷/*.md', '迷宫纪前传/补卷/*.md', '纷争纪/补卷/*.md', '月银纪补卷/*.md', '萨尔维斯/补卷/*.md']
BLK = r'^### %s \((Special|Passive) \| \w+\)\n.*?(?=^### |^## |^> 条目设置|\Z)'


def files():
    out = []
    for p in SRC:
        out += glob.glob(os.path.join(ROOT, p))
    return sorted(set(out))


def page_sources(key):
    idx = json.load(open(os.path.join(W, '材料', '索引.json'), encoding='utf-8'))
    era, n = key.rsplit('_', 1)
    n = int(n)
    d = {'纷争纪': '纷争纪/parts' if n == 1 else '纷争纪/parts%d' % n, '山铜纪': '山铜纪/parts%d' % n, '迷宫纪前传': '迷宫纪前传/parts%d' % n}.get(era)
    return sorted(glob.glob(os.path.join(ROOT, d, '*.md'))) if d else [os.path.join(ROOT, idx[key]['file'])]


def parse():
    os.makedirs(OUTD, exist_ok=True)
    recs, problems = [], []
    for f in sorted(glob.glob(os.path.join(W, '交稿', 'pu_*.md'))):
        key = re.match(r'pu_(.+)_\d+[a-f]?\.md', os.path.basename(f)).group(1)
        t = open(f, encoding='utf-8').read().replace('\r\n', '\n')
        for part in re.split(r'(?m)^=== 旅伴：', t)[1:]:
            who = part.split('\n', 1)[0].strip()
            ab = re.search(r'^能力：.*$', part, re.M)
            zs = re.search(r'^技艺走势：.*$', part, re.M)
            stars = []
            for m in re.finditer(r'(?m)^--- 换：([^\n]+)\n(.*?)(?=^--- 换：|\Z)', part, re.S):
                old = m.group(1).strip().strip('【】')
                blk = m.group(2).strip() + '\n'
                h = re.match(r'### (\S+) \((Special|Passive) \| (\w+)\)', blk)
                if not h:
                    problems.append('%s %s %s：星条标题不对' % (key, who, old))
                    continue
                stars.append({'old': old, 'new': h.group(1), 'kind': h.group(2), 'tier': h.group(3), 'block': blk})
            if not ab or not zs:
                problems.append('%s %s：缺能力行或技艺走势' % (key, who))
            recs.append({'page': key, 'who': who, 'ability': ab.group(0) if ab else '', 'trend': zs.group(0) if zs else '', 'stars': stars})
    # 改名表
    ren, seen = {}, {}
    for r in recs:
        for s in r['stars']:
            if s['old'] != s['new']:
                if s['old'] in ren and ren[s['old']] != s['new']:
                    problems.append('旧名 %s 两处改成不一样：%s、%s' % (s['old'], ren[s['old']], s['new']))
                ren[s['old']] = s['new']
            seen.setdefault(s['new'], set()).add(r['who'].split('·')[0])
    for n, w in seen.items():
        if len(w) > 1:
            problems.append('新名 %s 撞了：%s' % (n, '、'.join(w)))
    json.dump(recs, open(os.path.join(OUTD, '记录.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(os.path.join(OUTD, '改名表.md'), 'w', encoding='utf-8', newline='\n') as o:
        o.write('# 命星重审第二轮·铺开改名表\n\n| 现名 | 改成 |\n|---|---|\n')
        for a, b in ren.items():
            o.write('| %s | %s |\n' % (a, b))
    print('旅伴 %d 位，改星 %d 颗，改名 %d 个' % (len(recs), sum(len(r['stars']) for r in recs), len(ren)))
    for p in problems:
        print('  ', p)


def rw(path, fn, apply):
    raw = open(path, encoding='utf-8', newline='').read()
    crlf = '\r\n' in raw
    t = raw.replace('\r\n', '\n')
    n = fn(t)
    if n != t and apply:
        open(path, 'w', encoding='utf-8', newline='').write(n.replace('\n', '\r\n') if crlf else n)
    return n != t


def blocks(apply):
    recs = json.load(open(os.path.join(OUTD, '记录.json'), encoding='utf-8'))
    new = {}
    for r in recs:
        for s in r['stars']:
            new.setdefault(s['new'], s['block'])
    hit = {k: 0 for k in new}
    changed = 0
    for path in files():
        def fn(t):
            for name, blk in new.items():
                def sub(m):
                    hit[name] += 1
                    old = m.group(0)
                    tail = re.search(r'\n*$', old).group(0)
                    return blk.rstrip('\n') + (tail if tail else '\n')
                t = re.sub(BLK % re.escape(name), sub, t, flags=re.S | re.M)
            return t
        if rw(path, fn, apply):
            changed += 1
    miss = [k for k, v in hit.items() if not v]
    print('换了 %d 个文件；新名 %d 个，没找到块的 %d 个' % (changed, len(new), len(miss)))
    for k in miss:
        print('  没找到：', k)


def shared_olds(recs):
    import collections
    own = collections.defaultdict(set)
    for r in recs:
        for s in r['stars']:
            own[s['old']].add(r['who'].split('·')[0])
    return {o for o, w in own.items() if len(w) > 1}


def blocks2(apply):
    """旧名只有一个人用的：所有源稿里同名的块整块换成新的。共用的旧名（底卡池子里的星）和页上找不到旧块的：在这一页添一块新的，插在他技艺星条前头。"""
    recs = json.load(open(os.path.join(OUTD, '记录.json'), encoding='utf-8'))
    shared = shared_olds(recs)
    allf = files()
    cache = {}

    def get(f):
        if f not in cache:
            raw = open(f, encoding='utf-8', newline='').read()
            cache[f] = [raw.replace('\r\n', '\n'), '\r\n' in raw, raw]
        return cache[f]
    rep = ins = miss = 0
    log = []
    for r in recs:
        arts = re.findall(r'Art【([^】]+)】', r['ability'])
        for s in r['stars']:
            done = False
            if s['old'] not in shared:
                rx = re.compile(BLK % re.escape(s['old']), re.S | re.M)
                for f in allf:
                    c = get(f)
                    if rx.search(c[0]):
                        def sub(m):
                            tail = re.search(r'\n*$', m.group(0)).group(0)
                            return s['block'].rstrip('\n') + (tail or '\n')
                        c[0] = rx.sub(sub, c[0])
                        done = True
                if done:
                    rep += 1
                    continue
            # 添一块新的
            put = False
            for f in page_sources(r['page']):
                c = get(f)
                m = None
                for a in arts:
                    m = re.search(r'^### ' + re.escape(a) + r' \(Art \|', c[0], re.M)
                    if m:
                        break
                if not m:
                    continue
                c[0] = c[0][:m.start()] + s['block'].rstrip('\n') + '\n\n' + c[0][m.start():]
                put = True
                break
            if not put:
                for f in page_sources(r['page']):
                    c = get(f)
                    m = re.search(r'^> 条目设置：[^\n]*文件夹 49', c[0], re.M)
                    if m:
                        c[0] = c[0][:m.start()] + s['block'].rstrip('\n') + '\n\n' + c[0][m.start():]
                        put = True
                        break
            if put:
                ins += 1
                log.append('添：%s %s %s→%s' % (r['page'], r['who'], s['old'], s['new']))
            else:
                miss += 1
                log.append('！放不下：%s %s %s→%s' % (r['page'], r['who'], s['old'], s['new']))
    n = 0
    for f, c in cache.items():
        new = c[0].replace('\n', '\r\n') if c[1] else c[0]
        if new != c[2]:
            n += 1
            if apply:
                open(f, 'w', encoding='utf-8', newline='').write(new)
    print('整块换 %d 颗，添 %d 颗，放不下 %d 颗，改了 %d 个文件' % (rep, ins, miss, n))
    open(os.path.join(OUTD, '换块记录.txt'), 'w', encoding='utf-8').write('\n'.join(log))
    # 改名表（只放旧名只有一个人用的、名字变了的），给 rename_stars.py 全卷换引用
    with open(os.path.join(OUTD, '改名表_全卷.md'), 'w', encoding='utf-8', newline='\n') as o:
        o.write('# 命星重审第二轮·铺开改名表（全卷换）\n\n| 现名 | 改成 |\n|---|---|\n')
        seen = set()
        for r in recs:
            for s in r['stars']:
                if s['old'] not in shared and s['old'] != s['new'] and s['old'] not in seen:
                    seen.add(s['old'])
                    o.write('| %s | %s |\n' % (s['old'], s['new']))


def own_refs(apply):
    """共用旧名：只在这个人自己的旅伴条和背景条里（所有页）把【旧名】换成【新名】。"""
    recs = json.load(open(os.path.join(OUTD, '记录.json'), encoding='utf-8'))
    shared = shared_olds(recs)
    pairs = {}
    for r in recs:
        for s in r['stars']:
            if s['old'] in shared:
                pairs.setdefault(r['who'].split('·')[0], []).append((s['old'], s['new']))
    n = 0
    for f in files():
        def fn(t):
            for who, ps in pairs.items():
                def sub(m):
                    e = m.group(0)
                    for a, b in ps:
                        e = e.replace('【%s】' % a, '【%s】' % b)
                    return e
                t = re.sub(r'(?m)^## 旅途同行(?:·背景)?：' + re.escape(who) + r'[^\n]*\n.*?(?=^## |\Z)', sub, t, flags=re.S)
            return t
        if rw(f, fn, apply):
            n += 1
    print('共用旧名逐人换引用：%d 位，改了 %d 个文件' % (len(pairs), n))


def lines(apply):
    recs = json.load(open(os.path.join(OUTD, '记录.json'), encoding='utf-8'))
    first = {}
    for r in recs:
        segs = dict(re.findall(r'(Special|Passive)(【[^】]+】\([^｜]*?\))(?=｜|$)', r['ability'][3:]))
        if r['stars']:
            first.setdefault(r['who'].split('·')[0], segs)
    done, miss = 0, []
    for r in recs:
        short = r['who'].split('·')[0]
        ab = r['ability']
        if not r['stars'] and short in first:      # 跨页的后几页：Special、Passive 那两段抄头一页的
            for k, seg in first[short].items():
                ab = re.sub(k + r'【[^】]+】\([^｜]*?\)(?=｜|$)', lambda m: k + seg, ab, count=1)
        ok = False
        for path in page_sources(r['page']):
            def fn(t):
                nonlocal ok
                m = re.search(r'(?m)^## 旅途同行：' + re.escape(short) + r'[^\n]*\n.*?(?=^## |\Z)', t, re.S)
                if not m:
                    return t
                ent = m.group(0)
                if not re.search(r'(?m)^能力：', ent):
                    return t
                ent2 = re.sub(r'(?m)^能力：.*$', lambda _: ab, ent, count=1)
                if re.search(r'(?m)^技艺走势：', ent2):
                    ent2 = re.sub(r'(?m)^技艺走势：.*$', lambda _: r['trend'], ent2, count=1)
                else:
                    anchor = re.search(r'(?m)^位阶走势：.*$', ent2) or re.search(r'(?m)^底座：.*$', ent2)
                    ent2 = ent2[:anchor.end()] + '\n' + r['trend'] + ent2[anchor.end():]
                ok = True
                return t[:m.start()] + ent2 + t[m.end():]
            rw(path, fn, apply)
            if ok:
                break
        if ok:
            done += 1
        else:
            miss.append('%s %s' % (r['page'], r['who']))
    print('换了 %d 位旅伴的能力行和技艺走势' % done)
    for x in miss:
        print('  没找到：', x)


if __name__ == '__main__':
    cmd = sys.argv[1]
    {'parse': parse, 'blocks': lambda: blocks('--apply' in sys.argv), 'blocks2': lambda: blocks2('--apply' in sys.argv),
     'own': lambda: own_refs('--apply' in sys.argv), 'lines': lambda: lines('--apply' in sys.argv)}[cmd]()
