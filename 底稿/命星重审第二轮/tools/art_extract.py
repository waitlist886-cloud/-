#!/usr/bin/env python3
# 技艺重洗·筛表（11-20）：从四纪拼好的页里抽每一门 Art 的星条和持有人，一页一份，写 材料/艺_<页>.md。
#   python -I -X utf8 底稿/命星重审第二轮/tools/art_extract.py
# 持有人：能力行、命星行、底座法门、技艺走势里出现【X】或“法门 X”的条目（旅伴、人物、凡世至强都算），带命路倾向、身份、底座、能力、技艺走势。
# 名字锁：底卡技艺池子里现成的名字、门面真名层（star_true.json 的 arts）里的名字，标“名字不动”。
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
from extract import GROUPS, order  # noqa: E402

OUT = os.path.join(ROOT, '底稿', '命星重审第二轮', '材料')
STAR = re.compile(r'^### (\S+) \(Art \| (\w+)\)\n.*?(?=^### |^## |^> 条目设置|\Z)', re.S | re.M)
NL = chr(10)


def walk(o):
    if isinstance(o, dict):
        if isinstance(o.get('content'), str):
            yield o['content']
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def entries(t):
    pos = [m.start() for m in re.finditer(r'(?m)^## (?!裁定锁)', t)]
    return [t[s:(pos[i + 1] if i + 1 < len(pos) else len(t))] for i, s in enumerate(pos)]


def cut(s, n):
    return s if len(s) <= n else s[:n] + '……（截）'


def holder_lines(e):
    head = e.split(NL, 1)[0][3:].strip()
    out = ['持有人｜' + head]
    for lab in ('固定锚定', '身份', '底座', '能力', '技艺走势', '- 命星', '- 技艺走势', '位阶', '传奇之名'):
        m = re.search(r'^' + re.escape(lab) + r'[：｜](.*)$', e, re.M)
        if m:
            v = m.group(1)
            if lab == '固定锚定':
                r = re.search(r'命路倾向【[^】]+】', v)
                v = r.group(0) if r else ''
                if not v:
                    continue
            out.append('  %s｜%s' % (lab.lstrip('- '), cut(v, 500 if '走势' in lab else 300)))
    return out


def main():
    base = set()
    for c in walk(json.load(open(os.path.join(ROOT, 'src', 'rili_v7.json'), encoding='utf-8'))):
        base |= set(re.findall(r'^## (\S+) \(Art \|', c, re.M))
    tn = {a['tn'] for a in json.load(open(os.path.join(ROOT, '底稿', '门面', '共用', 'data', 'star_true.json'), encoding='utf-8'))['arts']}
    idx, tot = {}, 0
    for era, pat in GROUPS:
        for f in sorted(glob.glob(os.path.join(ROOT, pat)), key=order):
            t = open(f, encoding='utf-8').read().replace('\r\n', '\n')
            arts = {}
            for m in STAR.finditer(t):
                arts.setdefault(m.group(1), (m.group(2), m.group(0).rstrip()))
            if not arts:
                continue
            ents = [e for e in entries(t) if not e.startswith('## 设计备注') and not re.search(r'^### \S+ \((?:Art|Special|Passive) \|', e, re.M)]
            key = '%s_%02d' % (era, order(f))
            parts = []
            for nm, (tier, blk) in arts.items():
                seg = ['=' * 20, '【技艺】%s｜现档 %s' % (nm, tier)]
                if nm in base:
                    seg.append('【名字不动】底卡技艺池子里现成的名字，只看效果和写法。')
                elif nm in tn:
                    seg.append('【名字不动】迷宫纪1001年的卡里认这个名字（真名层），只看效果和写法。')
                hs = [e for e in ents if ('【%s】' % nm) in e or ('法门 %s' % nm) in e]
                for e in hs[:4]:
                    seg += holder_lines(e)
                if not hs:
                    seg.append('持有人｜（页上找不到，看星条正文）')
                seg.append(blk)
                parts.append(NL.join(seg))
            open(os.path.join(OUT, '艺_%s.md' % key), 'w', encoding='utf-8', newline='\n').write(
                '# %s 第%s%s：技艺 %d 门\n\n' % (era, order(f), '歌' if era == '月银纪' else '页', len(arts)) + (NL * 2).join(parts) + NL)
            idx[key] = {'file': os.path.relpath(f, ROOT).replace('\\', '/'), 'arts': list(arts)}
            tot += len(arts)
            print('%-10s 技艺 %3d' % (key, len(arts)))
    json.dump(idx, open(os.path.join(OUT, '艺_索引.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('合计', tot)


if __name__ == '__main__':
    main()
