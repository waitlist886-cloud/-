#!/usr/bin/env python3
# 史诗战阶段名号拆成一阶一条（11-07）。读 底稿/立绘/史诗战名号/ 六份全文（另一个会话写的，不进卡），
# 写 comfy/epic/阶段表.json：一个阶段一条，带这一纪、这一块（对手，带场次）、名号栏、本体、第几阶、整段名号、这一阶的样子和在干什么、出处行号。
# 拆法照 tools/立绘清单/拼名号清单.py（那边拼总表的脚本），所以条数跟 总表.md 对得上（278 个对手、687 个阶段名号）。
#   python epic_rows.py            写 epic/阶段表.json，打印各份的数
#   python epic_rows.py --check    只数，不写
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, '底稿', '立绘', '史诗战名号')
OUT = os.path.join(HERE, 'epic', '阶段表.json')
PARTS = [('moon', '月银纪', '月银纪.md'), ('strife_god1', '纷争纪', '纷争纪_魔神_离弦负山翻页.md'),
         ('strife_god2', '纷争纪', '纷争纪_魔神_返青立边静光不退.md'), ('strife_other', '纷争纪', '纷争纪_其余对手.md'),
         ('bronze', '山铜纪', '山铜纪.md'), ('maze', '迷宫纪前传', '迷宫纪前传.md')]
PH = re.compile(r'^\s*-\s*(?:\*\*)?(?:隐藏·[^，,【]{1,12}[，,]\s*)?(?:隐藏)?([一二三四五六七八九十]+阶(?:（[^）]*）)?)(?:\*\*)?\s*【([^【】]+)】')
NUM = {c: i + 1 for i, c in enumerate('一二三四五六七八九十')}


def phase_no(s):
    m = re.match(r'([一二三四五六七八九十]+)阶', s)
    return NUM.get(m.group(1), 0) if m else 0


def rows_of(key, era, fname):
    lines = open(os.path.join(SRC, fname), encoding='utf-8').read().split('\n')
    out = []
    hdr = base = tag = body = None
    for ln, line in enumerate(lines, 1):
        if line.startswith('## '):
            hdr = base = tag = body = None
            continue
        if line.startswith('### '):
            hdr = line[4:].strip(); base = hdr; tag = body = None
            continue
        if line.startswith('#### ') and hdr:
            hdr = re.sub(r'（.*$', '', base) + '·' + line[5:].strip(); tag = None
            continue
        mh = re.match(r'^\s*-\s*(?:\*\*)?隐藏(?:\*\*)?[，,：:\s]*([^（。，,：:\s【一二三四五六七八九十]+)', line)
        ms = re.match(r'^\s{2,}-\s*([^\s。（，【]{1,14})(?:（[^）]*）)?。本体', line)
        mb = re.match(r'^\s*-\s*本体（隐藏）', line)
        if hdr and (mh or ms or mb):
            tag = None
            hdr = re.sub(r'（.*$', '', base) + ('·隐藏 ' + mh.group(1) if mh else '·' + ms.group(1) if ms else '·隐藏')
        if hdr is None:
            continue
        m = re.match(r'^\s*-\s*名号栏[：:]\s*([^。（，\s]+)', line)
        if m:
            tag = m.group(1)
        m = re.match(r'^\s*-\s*本体(?:（隐藏）)?[：:]\s*(.*)$', line)
        if m:
            body = m.group(1).strip()
        mi = re.match(r'^\s*-\s*([^\s。（，【]{1,16})(?:（[^）]*）)?。本体', line)
        if mi and not PH.match(line) and '【' in line and not line.lstrip().startswith(('- 本体', '- 依据')):
            rest = line.split('本体', 1)[1]
            found = re.findall(r'【([^【】]+)】', rest)
            if found:
                blk = re.sub(r'（.*$', '', base) + '·' + mi.group(1)
                for n in found:
                    out.append(dict(part=key, era=era, file=fname, line=ln, block=blk, tag=tag, body=rest.strip(), phase='一阶', no=1, name=n, look=rest.strip()))
                continue
        mhd = re.match(r'^\s*-\s*隐藏·([^，,【]{1,12})[，,]\s*[一二三四五六七八九十]+阶', line)
        if mhd:
            lab = re.sub(r'（.*$', '', base) + '·隐藏 ' + mhd.group(1)
            if hdr != lab:
                hdr = lab; tag = None
        m = PH.match(line)
        if m:
            out.append(dict(part=key, era=era, file=fname, line=ln, block=hdr, tag=tag, body=body, phase=m.group(1), no=phase_no(m.group(1)), name=m.group(2), look=line[m.end():].lstrip('：: ').strip()))
            for m2 in re.finditer(r'([一二三四五六七八九十]+阶)【([^【】]+)】', line[m.end():]):
                out.append(dict(part=key, era=era, file=fname, line=ln, block=hdr, tag=tag, body=body, phase=m2.group(1), no=phase_no(m2.group(1)), name=m2.group(2), look=line[m.end():].strip()))
    return out


CITE = re.compile(r'（[^（）]*?(?:[:：]\s*\d|补\d|p\d|第[一二三四五六七八九十]+歌|帝国史|支线_|只给 AI)[^（）]*）')


def strip(s):
    """去掉出处括号（文件:行），留下样子和在干什么。"""
    s = CITE.sub('', s or '')
    s = re.sub(r'（\s*）', '', s)
    return re.sub(r'\s{2,}', ' ', s).strip()


def block_id(b):
    m = re.match(r'^([A-Za-z]*\d+[A-Za-z]?(?:[-·][A-Za-z0-9\-]+)?)', b)
    return m.group(1) if m else b[:8]


def split_parts(allrows):
    """一份一个输入文件 epic/in/<份>.json：按对手分组，一阶一个键（份_块序号_第几阶），缺本体的场次拿同号主块的本体补。"""
    os.makedirs(os.path.join(HERE, 'epic', 'in'), exist_ok=True)
    for key, era, fname in PARTS:
        rows = [r for r in allrows if r['part'] == key]
        blocks = list(dict.fromkeys(r['block'] for r in rows))
        bodies = {}
        for r in rows:
            if r['body']:
                bodies.setdefault(r['block'], r['body'])
        base_body = {}
        for b in blocks:
            bid = block_id(b).split('·')[0]
            if b in bodies:
                base_body.setdefault(bid, bodies[b])
        out = []
        for i, b in enumerate(blocks, 1):
            rs = [r for r in rows if r['block'] == b]
            body = bodies.get(b) or base_body.get(block_id(b).split('·')[0]) or ''
            seen = {}
            phases = []
            for r in rs:
                n = r['no'] or 1
                seen[n] = seen.get(n, 0) + 1
                k = '%s_%03d_%d' % (key, i, n) + ('' if seen[n] == 1 else chr(ord('a') + seen[n] - 1))
                phases.append({'key': k, 'no': n, 'name': r['name'], 'look': strip(r['look'])})
            out.append({'block': b, 'tag': rs[0]['tag'], 'body': strip(body), 'body_from_base': b not in bodies, 'phases': phases})
        p = os.path.join(HERE, 'epic', 'in', key + '.json')
        json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('写了', p, len(out), '块', sum(len(x['phases']) for x in out), '阶')


if __name__ == '__main__':
    allrows = []
    for key, era, fname in PARTS:
        r = rows_of(key, era, fname)
        blocks = list(dict.fromkeys(x['block'] for x in r))
        nobody = sorted({x['block'] for x in r if not x['body']})
        print('%s %s：%d 个对手，%d 个阶段%s' % (era, fname, len(blocks), len(r), ('；没有本体那一行的 %d 块' % len(nobody)) if nobody else ''))
        allrows += r
    print('合计 %d 个对手，%d 个阶段' % (len(list(dict.fromkeys((x['part'], x['block']) for x in allrows))), len(allrows)))
    if '--check' not in sys.argv:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(allrows, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('写了', OUT)
        split_parts(allrows)
