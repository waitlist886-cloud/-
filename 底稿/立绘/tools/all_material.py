#!/usr/bin/env python3
# 11-22 四本书剩下没有立绘的人（用户：“四本书都排”），出图资料的材料。
#   python -I -X utf8 底稿/门面/卡片/工具/por_cover.py          先出名单（系统临时目录 aldran_por_cover.json）
#   python -I -X utf8 底稿/立绘/tools/all_material.py [--show]
# 名单照 por_cover 的“没有图”，整群的（某某家、那几个、七姐妹、末代……）拿掉，11-22 对手那一批（铺开_11-22/材料/名单.tsv）拿掉。
# 一个人先在他头一次出场那一页找标题带他名字的条（人物条、凡世至强、旅途同行、歌里的条），找不到再翻这一纪别的页和补卷，
# 再找不到就找写着「- 名字｜」小条的那一条。整条抄进材料，太长的截前四千字。
# 写 底稿/立绘/铺开_11-22/全员材料/<纪>_<页号>.md 和 名单.tsv（名字、纪、页号、出处、cast 文件、找没找到）。
import glob
import json
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, '底稿', '立绘', '铺开_11-22', '全员材料')
NL = chr(10)
CN = '一二三四五六七八九十'
GROUP = re.compile(r'(家$|那一路|那几家|那几个|那一班|两岸的人|十四家|十二家|的十一个|七姐妹|开国之君|末代|、|们$)')
CAP = 4000


def rd(p):
    return open(p, encoding='utf-8').read().replace(chr(13) + NL, NL)


def pages_of(setn):
    """回 [(页号, 文件)]，页号就是 cast 文件名用的前缀。"""
    if setn == '纷争纪':
        fs = glob.glob(os.path.join(ROOT, '纷争纪', '纷争纪时段_*.md'))
        return [('z%d' % (CN.index(os.path.basename(f)[6]) + 1), f) for f in fs]
    if setn == '山铜纪':
        fs = glob.glob(os.path.join(ROOT, '山铜纪', '山铜纪时段_*.md'))
        return [('s%d' % (CN.index(os.path.basename(f)[6]) + 1), f) for f in fs]
    if setn == '前传':
        fs = glob.glob(os.path.join(ROOT, '迷宫纪前传', '迷宫纪前传时段_*.md'))
        return [('q%d' % (CN.index(os.path.basename(f)[8]) + 1), f) for f in fs]
    if setn == '诸国期':
        fs = glob.glob(os.path.join(ROOT, '诸国期', '诸国期时段_*.md'))
        return [('zg%d' % (CN.index(os.path.basename(f)[6]) + 1), f) for f in fs]
    if setn == '萨尔维斯':
        fs = glob.glob(os.path.join(ROOT, '萨尔维斯', '萨尔维斯时段_*.md'))
        return [('sa%d' % (CN.index(os.path.basename(f)[7]) + 1), f) for f in fs]
    if setn == '月银纪史诗':
        out = []
        for f in glob.glob(os.path.join(ROOT, '月银纪史诗', '第*歌_*.md')):
            m = re.match(r'第(.+?)歌', os.path.basename(f))
            s = m.group(1)
            n = 10 + (CN.index(s[1]) + 1 if len(s) == 2 else 0) if s.startswith('十') else CN.index(s) + 1
            out.append(('ge%d' % n, f))
        return out
    return []


SUPP = {'纷争纪': ['纷争纪/补卷/*.md'], '山铜纪': ['山铜纪/补卷/*.md'], '前传': ['迷宫纪前传/补卷/*.md', '迷宫纪前传/迷宫纪前传_委托_第一版.md'],
        '诸国期': ['月银纪补卷/*.md', '诸国期/*.md'], '萨尔维斯': ['萨尔维斯/补卷/*.md', '月银纪补卷/*.md'], '月银纪史诗': ['月银纪补卷/*.md', '月银纪史诗/*.md']}


def page_of(book, eid, setn):
    if book == '纷争纪':
        return None      # 照 part 取，见 main
    if book == '月银纪':
        n = int(eid[1:])
        return 'ge%d' % n if n <= 15 else 'zg%d' % (n - 15) if n <= 21 else 'sa%d' % (n - 21)
    if book == '山铜纪':
        return 's' + eid[1:]
    if book == '迷宫纪':
        return eid
    return None


def entries(t):
    pos = [m.start() for m in re.finditer(r'(?m)^## (?!裁定锁)', t)]
    return [(t.count(NL, 0, s) + 1, t[s:(pos[i + 1] if i + 1 < len(pos) else len(t))]) for i, s in enumerate(pos)]


_cache = {}


def ents(f):
    if f not in _cache:
        _cache[f] = entries(rd(f))
    return _cache[f]


def find(name, files):
    short = re.split(r'[·（(]', name)[0]
    hits = []
    for f in files:
        for ln, e in ents(f):
            head = e.split(NL, 1)[0]
            if short in head and not head.startswith('## 设计备注'):
                hits.append((f, ln, e))
    if hits:
        return hits[:2], 'head'
    for f in files:
        for ln, e in ents(f):
            if re.search(r'(?m)^- ' + re.escape(short) + r'[｜：·（(，]', e):
                return [(f, ln, e)], 'sub'
    return [], ''


def main():
    cover = json.load(open(os.path.join(tempfile.gettempdir(), 'aldran_por_cover.json'), encoding='utf-8'))
    riv = set(l.split('\t')[0] for l in open(os.path.join(ROOT, '底稿', '立绘', '铺开_11-22', '材料', '名单.tsv'), encoding='utf-8'))
    books = {'月银纪': json.load(open(os.path.join(ROOT, '底稿', '门面', '小样_月银纪书', 'data', 'moon.json'), encoding='utf-8')),
             '纷争纪': json.load(open(os.path.join(ROOT, '底稿', '门面', '小样_纷争纪书', 'data', 'strife.json'), encoding='utf-8')),
             '山铜纪': json.load(open(os.path.join(ROOT, '底稿', '门面', '小样_山铜纪书', 'data', 'bronze.json'), encoding='utf-8')),
             '迷宫纪': json.load(open(os.path.join(ROOT, '底稿', '门面', '小样_迷宫纪书', 'data', 'maze.json'), encoding='utf-8'))}
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '*.md')):
        os.remove(f)
    rows, per, miss = [], {}, []
    for book, people in cover.items():
        era = {e['id']: e for e in books[book]['eras']}
        for name, v in people.items():
            if v.get('have') or GROUP.search(name) or name in riv or not v['roles']:
                continue
            eid, role = v['roles'][0]
            e = era[eid]
            setn = e.get('set')
            pg = 'z%d' % (e['part'] + 1) if book == '纷争纪' else page_of(book, eid, setn)
            pmap = dict(pages_of(setn))
            first = [pmap[pg]] if pg in pmap else []
            rest = [f for p, f in sorted(pmap.items()) if p != pg]
            supp = [f for g in SUPP.get(setn, []) for f in sorted(glob.glob(os.path.join(ROOT, g)))]
            hits, how = find(name, first)
            if not hits:
                hits, how = find(name, rest + supp)
            key = '%s_%s' % (setn, pg)
            if not hits:
                miss.append((name, book, eid, role))
                rows.append((name, book, setn, pg, eid, role, '', '没找到'))
                continue
            for f, ln, body in hits:
                rel = os.path.relpath(f, ROOT).replace(os.sep, '/')
                b = body.rstrip()
                if len(b) > CAP:
                    b = b[:CAP] + NL + '（以下截掉）'
                per.setdefault(key, []).append('<!-- %s｜%s｜%s:%d｜%s -->%s%s%s' % (name, role, rel, ln, how, NL, b, NL))
            rows.append((name, book, setn, pg, eid, role, '%s:%d' % (os.path.relpath(hits[0][0], ROOT).replace(os.sep, '/'), hits[0][1]), how))
    for k, es in per.items():
        open(os.path.join(OUT, k + '.md'), 'w', encoding='utf-8').write((NL * 2).join(es))
    with open(os.path.join(OUT, '名单.tsv'), 'w', encoding='utf-8') as fh:
        for r in rows:
            fh.write('\t'.join(r) + NL)
    from collections import Counter
    print('一共', len(rows), '位，没找到', len(miss))
    for k, n in sorted(Counter('%s_%s' % (r[2], r[3]) for r in rows if r[7]).items()):
        print(' ', k, n, '位', sum(len(x) for x in per.get(k, [])), '字')
    for m in miss:
        print('没找到', *m)


if __name__ == '__main__':
    main()
