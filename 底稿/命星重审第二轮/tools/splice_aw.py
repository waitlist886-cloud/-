#!/usr/bin/env python3
# 技艺铺开（11-20）：把 交稿/aw_*.md 里重写的技艺星条换回源稿。
#   python -I -X utf8 底稿/命星重审第二轮/tools/splice_aw.py          只报
#   python -I -X utf8 底稿/命星重审第二轮/tools/splice_aw.py --apply  写盘，另写 收稿/技艺改名表.md、收稿/技艺改档.json
# 旧块从「### 旧名 (Art | 档)」到它后面第一个「### 」「## 」「> 条目设置」以前。新块按名字对：改写、放大的是原名，换名的是拟名，
# 母门不在页上的并回是母门名。母门在页上的并回，旧块删掉，引用改成母门。
# 【调用】行把旧名换成新名以后要跟原来一字不差，对不上的印出来不换。源稿找法照 splice_rare.py。
import csv
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from splice_rare import sources, ROOT, W  # noqa: E402

NEWB = re.compile(r'^### (\S+) \(Art \| (\w+)\)\n.*?(?=^### |\Z)', re.S | re.M)


def oldre(name):
    return re.compile(r'^### ' + re.escape(name) + r' \(Art \| \w+\)\n.*?(?=^### |^## |^> 条目设置|\Z)', re.S | re.M)


def plan():
    rows = list(csv.DictReader(open(os.path.join(W, '技艺筛表.tsv'), encoding='utf-8'), delimiter='\t'))
    idx = json.load(open(os.path.join(W, '材料', '艺_索引.json'), encoding='utf-8'))
    exp, drop, ren = {}, {}, {}
    newnames = {}
    for r in rows:
        if r['判'] != '并回':
            newnames.setdefault(r['页'], set()).add(r['拟名'] if r['判'] == '换名' else r['技艺'])
    for r in rows:
        key, old = r['页'], r['技艺']
        new = r['拟名'] if r['判'] == '换名' else old
        if r['判'] == '并回':
            p = re.sub(r'（.*?）', '', r['并入']).strip()
            if p in idx[key]['arts'] or p in newnames.get(key, ()):
                drop.setdefault(key, []).append((old, p))
                ren[old] = p
                continue
            new = p
        exp.setdefault(key, {})[new] = (old, r['拟档'])
        if new != old:
            ren[old] = new
    return idx, exp, drop, ren


def main(apply):
    idx, exp, drop, ren = plan()
    got = {}
    for f in glob.glob(os.path.join(W, '交稿', 'aw_*.md')):
        key = re.match(r'aw_(.+)_\d+[a-f]?\.md$', os.path.basename(f)).group(1)
        for m in NEWB.finditer(open(f, encoding='utf-8').read().replace('\r\n', '\n')):
            got.setdefault(key, {})[m.group(1)] = (m.group(2), m.group(0).rstrip('\n') + '\n\n')
    files, done, bad, miss, tiers = {}, 0, [], [], {}

    def load(src):
        if src not in files:
            files[src] = open(src, encoding='utf-8', newline='').read()
        return files[src]

    for key, want in exp.items():
        for new, (old, tier) in want.items():
            g = got.get(key, {}).get(new)
            if not g:
                miss.append('%s %s（旧名 %s）' % (key, new, old))
                continue
            gt, blk = g
            if gt != tier:
                bad.append('%s %s：档写成 %s，筛表是 %s（照写手的收）' % (key, new, gt, tier))
            hit = 0
            for src in sources(key, idx[key]['file']):
                t = load(src)
                crlf = '\r\n' in t
                tn = t.replace('\r\n', '\n')
                om = oldre(old).search(tn)
                if not om:
                    continue
                o = om.group(0)
                co = re.search(r'^【调用】.*$', o, re.M)
                cn = re.search(r'^【调用】.*$', blk, re.M)
                if co and (not cn or co.group(0).replace(old, new) != cn.group(0)):
                    if not cn:
                        bad.append('%s %s：没有【调用】行，没换' % (key, new))
                        break
                    bad.append('%s %s：【调用】行改了（照换）｜原 %s｜新 %s' % (key, new, co.group(0)[:80], cn.group(0)[:80]))
                rep = blk if o.endswith('\n\n') else blk.rstrip('\n') + '\n'
                tn = tn[:om.start()] + rep + tn[om.end():]
                files[src] = tn.replace('\n', '\r\n') if crlf else tn
                hit += 1
            if hit:
                done += 1
                tiers[new] = gt
            elif not any(x.startswith('%s %s：【调用】' % (key, new)) for x in bad):
                miss.append('%s %s：源稿里找不到旧块 %s' % (key, new, old))
    for key, lst in drop.items():
        for old, p in lst:
            for src in sources(key, idx[key]['file']):
                t = load(src)
                crlf = '\r\n' in t
                tn = t.replace('\r\n', '\n')
                om = oldre(old).search(tn)
                if om:
                    tn = tn[:om.start()] + tn[om.end():]
                    files[src] = tn.replace('\n', '\r\n') if crlf else tn
                    done += 1
    print('换了 %d 门（含删掉的并回）' % done)
    for x in miss:
        print('  缺：', x)
    for x in bad:
        print('  看：', x)
    if apply:
        n = 0
        for src, t in files.items():
            if open(src, encoding='utf-8', newline='').read() != t:
                open(src, 'w', encoding='utf-8', newline='').write(t)
                n += 1
        R = os.path.join(W, '收稿')
        with open(os.path.join(R, '技艺改名表.md'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write('# 技艺铺开改名表（全卷换）\n\n| 现名 | 改成 |\n|---|---|\n')
            for o, nw in sorted(ren.items()):
                fh.write('| %s | %s |\n' % (o, nw))
        json.dump(tiers, open(os.path.join(R, '技艺改档.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('写了 %d 个文件，改名 %d 个' % (n, len(ren)))


if __name__ == '__main__':
    main('--apply' in sys.argv)
