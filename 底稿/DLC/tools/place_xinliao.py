#!/usr/bin/env python3
"""DLC 新料进源稿（11-24）。新料的源稿在 底稿/DLC/新料/ 下各份，改字改那里；这一支把它们照纪、照包拼成各纪补卷里的
生成文件，build_v12 的补卷 glob 就收得到，make_dlc.py 再照文件夹号（61 律法志、62 风物志、63 谱系志）切包。

  python -I -X utf8 底稿/DLC/tools/place_xinliao.py            只报：几条、各纪各包几条、重名、格式不对的
  python -I -X utf8 底稿/DLC/tools/place_xinliao.py --apply    写盘（先删掉上一回生成的，再写）

源：样稿三条.md（方向稿第七节样稿一二三，文件夹号改过）、第一拨.md、律法志/L*.md、风物志/F*.md、谱系志/G*.md、谱系志/C*.md。
SKIP 里的标题不收（第一拨 1001 年三条“书写与衣食”合条，风物志下半拆完以后撤）。
出：月银纪补卷/新料_<包>.md，纷争纪/补卷/补卷_107_新料_<包>.md 起三份，山铜纪/补卷/补卷_73 起三份，迷宫纪前传/补卷/补卷_90 起三份
（前传和 1001 年的条都放前传补卷，1001 年的条自己带着年份正则当门控）。
"""
import collections, glob, io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SRC = os.path.join(ROOT, '底稿', 'DLC', '新料')
PACKS = {'61': '律法志', '62': '风物志', '63': '谱系志'}
FOLDER_NAME = {'61': '律法与官', '62': '风物', '63': '谱系'}
OUT = {
    '月银纪': lambda pk: os.path.join(ROOT, '月银纪补卷', '新料_%s.md' % pk),
    '纷争纪': lambda pk: os.path.join(ROOT, '纷争纪', '补卷', '补卷_%d_新料_%s.md' % (107 + list(PACKS.values()).index(pk), pk)),
    '山铜纪': lambda pk: os.path.join(ROOT, '山铜纪', '补卷', '补卷_%d_新料_%s.md' % (73 + list(PACKS.values()).index(pk), pk)),
    '迷宫纪': lambda pk: os.path.join(ROOT, '迷宫纪前传', '补卷', '补卷_%d_新料_%s.md' % (90 + list(PACKS.values()).index(pk), pk)),
}
SKIP = {
    '迷宫纪·风物｜书写与衣食·西陆',
    '迷宫纪·风物｜书写与衣食·东陆',
    '迷宫纪·风物｜书写与衣食·阿卡迪亚',
}
HEAD = '''# %s世界书补卷｜DLC 新料·%s

> 这一节是说明，不进卡。这一份是 `底稿/DLC/tools/place_xinliao.py` 从 `底稿/DLC/新料/` 下各份拼出来的，别直接改这里，改那边的源稿再重跑。文件夹 %s·%s｜%s，打卡以后由 `底稿/DLC/tools/make_dlc.py` 切进「%s」那一包。
'''


def sources():
    fs = [os.path.join(SRC, '样稿三条.md'), os.path.join(SRC, '第一拨.md')]
    for sub, pat in (('律法志', 'L*.md'), ('风物志', 'F*.md'), ('谱系志', 'G*.md'), ('谱系志', 'C*.md')):
        fs += sorted(glob.glob(os.path.join(SRC, sub, pat)))
    return [f for f in fs if os.path.isfile(f)]


def entries(path):
    lines = open(path, encoding='utf-8').read().replace('\r', '').split('\n')
    out, cur = [], None
    for ln in lines:
        if ln.startswith('## 设计备注'):
            break
        m = re.match(r'^## ((月银纪|纷争纪|山铜纪|迷宫纪)·.+)$', ln)
        if m:
            if cur:
                out.append(cur)
            cur = {'title': m.group(1).strip(), 'era': m.group(2), 'lines': [ln], 'src': os.path.relpath(path, ROOT).replace('\\', '/')}
            continue
        if ln.startswith('## ') or ln.startswith('# '):
            if cur:
                out.append(cur)
            cur = None
            continue
        if cur is not None:
            cur['lines'].append(ln)
    if cur:
        out.append(cur)
    return out


def main():
    apply = '--apply' in sys.argv
    bad = 0
    seen = {}
    groups = collections.defaultdict(list)
    for f in sources():
        for e in entries(f):
            if e['title'] in SKIP:
                continue
            sets = [l for l in e['lines'] if l.startswith('> 条目设置：')]
            if len(sets) != 1:
                bad += 1; print('错｜%s｜%s 条目设置 %d 行' % (e['src'], e['title'], len(sets))); continue
            m = re.search(r'文件夹 (\d\d)·(月银纪|纷争纪|山铜纪|迷宫纪)｜([^，]+)，', sets[0])
            if not m or m.group(1) not in PACKS:
                bad += 1; print('错｜%s｜%s 文件夹不是 61 到 63：%s' % (e['src'], e['title'], sets[0][6:40])); continue
            if m.group(2) != e['era']:
                bad += 1; print('错｜%s｜%s 文件夹的纪跟标题对不上' % (e['src'], e['title']))
            if m.group(3) != FOLDER_NAME[m.group(1)]:
                bad += 1; print('错｜%s｜%s 文件夹名该是 %s·%s｜%s，写的是 %s' % (e['src'], e['title'], m.group(1), e['era'], FOLDER_NAME[m.group(1)], m.group(3)))
            if e['title'] in seen:
                bad += 1; print('错｜重名｜%s（%s 和 %s）' % (e['title'], seen[e['title']], e['src']))
            seen[e['title']] = e['src']
            # 条目设置以后不该再有正文
            i = e['lines'].index(sets[0])
            tail = [l for l in e['lines'][i + 1:] if l.strip() and l.strip() != '---']
            if tail:
                bad += 1; print('错｜%s｜%s 条目设置后头还有字：%s' % (e['src'], e['title'], tail[0][:30]))
            e['lines'] = e['lines'][:i + 1]
            groups[(e['era'], PACKS[m.group(1)])].append(e)
    total = sum(len(v) for v in groups.values())
    print('新料 %d 条，格式问题 %d 处' % (total, bad))
    for era in OUT:
        print('  %s：' % era + '，'.join('%s %d' % (pk, len(groups.get((era, pk), []))) for pk in PACKS.values()))
    chars = sum(len(re.findall(r'[一-鿿]', '\n'.join(e['lines']))) for v in groups.values() for e in v)
    print('  汉字约 %d' % chars)
    if not apply:
        return 1 if bad else 0
    if bad:
        print('有格式问题，没写盘'); return 1
    # 删掉上一回生成的
    for era, fn in OUT.items():
        for pk in PACKS.values():
            p = fn(pk)
            if os.path.isfile(p):
                os.remove(p)
    for (era, pk), es in sorted(groups.items()):
        num = [k for k, v in PACKS.items() if v == pk][0]
        txt = HEAD % (era, pk, num, era, FOLDER_NAME[num], pk)
        for e in es:
            body = '\n'.join(e['lines']).rstrip('\n')
            txt += '\n' + body + '\n'
        p = OUT[era](pk)
        open(p, 'w', encoding='utf-8', newline='\n').write(txt)
        print('写 %s（%d 条）' % (os.path.relpath(p, ROOT).replace('\\', '/'), len(es)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
