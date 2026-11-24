#!/usr/bin/env python3
# 过条底子（11-24）：照 分份.json 一份一份出材料，写 材料/<份>.md。先跑 scan.py。
#   python -I -X utf8 底稿/收尾_11-24/过条/tools/material.py            全部
#   python -I -X utf8 底稿/收尾_11-24/过条/tools/material.py 过_纷争纪_2  只出这几份
# 页头：这一纪的公共技艺清单（兼修先从这里挑），这一份涉及的几页上现成的技艺（名、档）。
# 每人：编号、类别、文件、条目标题，条目里给判阶用的几行（凡世至强是调用、固定锚定、位阶与职责、凝名纪年、能力那一块、传奇之名；
# 人物条单人的是整条，几人合写的是标题、调用和他自己那几行），能力行逐行编字母（交稿照字母换整行），
# 主修那一门的星条（构成、阶、传承三行）和全谱那一行，生来星的星条档，当过旅伴的那几页的能力行和兼修，同一人别的条，scan 报的要改的几样。
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NL, ROOT, W, OLD, ERA_GROUP, rd, star_index, star_blocks, load_json  # noqa: E402

LETTERS = 'abcdefghijklmnopqrstuvwxyz'
PUB = {'月银纪': '月银纪', '纷争纪': '纷争纪', '山铜纪': '山铜纪', '迷宫纪前传': '迷宫纪'}
LEG_KEEP = ('【调用】', '固定锚定', '位阶与职责', '凝名纪年', '- 传奇之名', '- 天赋', '- 被动', '- 技艺', '- 兼修', '- 随身', '技艺走势')


def cut(s, n):
    return s if len(s) <= n else s[:n] + '……（截断，全文看源稿）'


def find_entry(src, head):
    t = rd(os.path.join(ROOT, src))
    m = re.search(r'(?m)^' + re.escape('## ' + head) + r'\s*\n.*?(?=^## (?!裁定锁)|\Z)', t, re.S)
    return m.group(0) if m else ''


def sub_block(blk, lab):
    m = re.search(r'^- ' + lab + r'：.*?(?=^- (?!\S+（)|\Z)', blk, re.S | re.M)
    return m.group(0).strip() if m else ''


def person_text(r, e):
    if not e:
        return ['（源稿里没找到这一条，scan 以后源稿改过？）']
    lines = e.rstrip().split(NL)
    body = [l for l in lines[1:] if not l.startswith('> 条目设置')]
    if r['类别'] == '凡世至强':
        out = []
        for l in body:
            if l.startswith(LEG_KEEP):
                out.append(cut(l, 600))
        return out
    group = len([x for x in r.get('_entry_people', [])]) > 1
    if not group:
        return [cut(l, 900) for l in body if l.strip()]
    call = [cut(l, 300) for l in body if l.startswith('【调用】')]
    short = r['人'].split('·')[0]
    mine = [cut(l, 900) for l in body if l.startswith('- %s｜' % short)]
    return call + mine


def main(only):
    recs = load_json('清点.json')
    fen = load_json('分份.json')
    byid = {r['id']: r for r in recs}
    entry_people = {}
    for r in recs:
        entry_people.setdefault((r['文件'][0] if r['文件'] else '', r['条目']), []).append(r['id'])
    for r in recs:
        r['_entry_people'] = entry_people[(r['文件'][0] if r['文件'] else '', r['条目'])]
    sidx = star_index()
    sblk = star_blocks()
    pubs = {}
    for f in glob.glob(os.path.join(OLD, '交稿', 'pub_*.md')):
        pubs[os.path.basename(f)[4:-3]] = [l for l in rd(f).split(NL) if l.startswith('清单｜')]
    os.makedirs(os.path.join(W, '材料'), exist_ok=True)
    raw = rd(os.path.join(ROOT, 'src', 'rili_v7.json'))
    pool = sorted(set(re.findall(r'## (\S+) \(Art \| (\w+)\)', raw)))
    open(os.path.join(W, '材料', '底卡技艺池子.md'), 'w', encoding='utf-8', newline=NL).write(
        '# 底卡技艺池子（迷宫纪1001年那一套，%d 门；迷宫纪前传可以借，早几纪只借有来历的）\n\n' % len(pool) + '、'.join('%s(%s)' % x for x in pool) + NL)
    for name, s in fen.items():
        if only and name not in only:
            continue
        people = [byid[i] for i in s['人']]
        keys = []
        for r in people:
            if r['页'] not in keys:
                keys.append(r['页'])
        arts = {}
        for n, lst in sidx.items():
            for k, kind, tr, _ in lst:
                if kind == 'Art' and k in keys:
                    arts.setdefault(k, []).append('%s(%s)' % (n, tr))
        head = ['# %s：%d 人（凡世至强 %d，人物 %d）' % (name, len(people), sum(1 for r in people if r['类别'] == '凡世至强'),
                                                   sum(1 for r in people if r['类别'] == '人物')), '',
                '文件：' + '、'.join(s['文件']), '',
                '## 这一纪的公共技艺（兼修先从这里挑）', ''] + pubs.get(PUB[s['纪']], ['（没有）']) + [
                '', '## 这几页上现成的技艺（名、档；别页的写全名也行）', '']
        for k in keys:
            head.append('- %s：%s' % (k, '、'.join(arts.get(k, [])) or '（这一页没有技艺星条）'))
        parts = []
        for r in people:
            e = find_entry(r['文件'][0], r['条目']) if r['文件'] else ''
            seg = ['=' * 20, '【人】%s｜%s｜%s' % (r['id'], r['类别'], r['人']),
                   '文件：%s' % '、'.join(r['文件']), '条目：## %s' % r['条目']]
            if len(r['_entry_people']) > 1:
                seg.append('这一条几个人合写：%s，只改他自己那几行。' % '、'.join('%s %s' % (i, byid[i]['人']) for i in r['_entry_people']))
            seg.append('')
            seg.append('〔条目里判阶用的几行〕')
            seg += person_text(r, e)
            seg.append('')
            seg.append('〔能力行，交稿照字母换整行〕')
            for i, l in enumerate(r['行']):
                seg.append('【行 %s】%s' % (LETTERS[i], l))
            seg.append('')
            for a in r['技艺']:
                seg.append('主修【%s】：行里写的档 %s，阶 %s。全谱：%s。' % (a['名'], a['档'] or '没写', a['阶'] or '没写', a.get('全谱', '没有这一行')))
                bl = [(k, b) for k, b in sblk.get(a['名'], []) if '(Art |' in b.split(NL, 1)[0]]
                bl.sort(key=lambda kb: 0 if kb[0] == r['页'] else 1)
                if bl:
                    k, b = bl[0]
                    seg.append('  星条在：%s' % k)
                    seg.append('  星条标题：' + b.split(NL, 1)[0])
                    for lab in ('构成', '阶', '传承'):
                        x = sub_block(b, lab)
                        if x:
                            seg.append('  ' + cut(x.replace(NL, NL + '  '), 1200))
                else:
                    seg.append('  没有星条（这一门 11-20 技艺重洗没过，没有构成和阶那一行），阶照派活说明第三节第 2 条判。')
            for g in r['生来']:
                seg.append('生来%s【%s】：行里写的档 %s；星条 %s。' % (g['类'], g['名'], g['档'] or '没写', '、'.join(g.get('星条', [])) or '没有'))
            for c in r['旅伴']:
                seg.append('当过旅伴（%s）：%s' % (c['页'], c['能力']))
                if c['兼修']:
                    seg.append('  ' + c['兼修'])
                if c['对不上']:
                    seg.append('  这一条里的【%s】旅伴条里没有，照旅伴条改名或写明是后来多出来的。' % '】【'.join(c['对不上']))
            if r['同一人']:
                seg.append('同一人别的条：' + '；'.join('%s（%s，%s，%s）' % (i, byid[i]['页'], byid[i]['份'], '、'.join(byid[i]['文件'])) for i in r['同一人']) + '。阶只升不降，兼修只添不丢，生来星名字和档一样。')
            seg.append('有技艺走势那一行：%s' % ('有，可以交【走势补】' if r['有走势'] else '没有，【走势补】写无'))
            seg.append('scan 报的要改：' + ('；'.join(r['要改']) or '无'))
            parts.append(NL.join(seg))
        out = os.path.join(W, '材料', name + '.md')
        open(out, 'w', encoding='utf-8', newline=NL).write(NL.join(head) + NL * 2 + (NL * 2).join(parts) + NL)
        print(name, len(people), '人', os.path.getsize(out) // 1024, 'KB')


if __name__ == '__main__':
    main(sys.argv[1:])
