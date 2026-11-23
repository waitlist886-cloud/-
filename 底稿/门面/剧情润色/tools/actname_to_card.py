#!/usr/bin/env python3
# 门面剧情润色的幕名进卡：读 底稿/门面/剧情润色/<纪>/*.json，在卡的源稿和拼好的页里找同一条主线，逐幕按 tag 换幕名。
#   python -I -X utf8 底稿/门面/剧情润色/tools/actname_to_card.py . [--apply] [--json out.json]（11-23，备注在 备注/幕名进卡.md）
#   改了分段源稿以后照旧重拼：assemble_strife.sh N、assemble_shantong_pN.py、assemble_maze.py . N。
import glob
import json
import os
import re
import sys

ROOT = sys.argv[1]
APPLY = '--apply' in sys.argv
JOUT = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
DRAFT = os.path.join(ROOT, '底稿', '门面', '剧情润色')
JI = {'月银纪': '月银纪', '纷争纪': '纷争纪', '山铜纪': '山铜纪', '迷宫纪': '迷宫纪'}
FILES = {
    '月银纪': ['月银纪史诗/第*歌_*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md'],
    '纷争纪': ['纷争纪/parts*/*.md', '纷争纪/纷争纪时段_*.md'],
    '山铜纪': ['山铜纪/parts[1-6]/*.md', '山铜纪/山铜纪时段_*.md'],
    '迷宫纪': ['迷宫纪前传/parts[1-6]/*.md', '迷宫纪前传/迷宫纪前传时段_*.md'],
}
TAGS = ('一幕', '二幕', '三幕', '四幕', '五幕', '六幕', '幕间', '收束')
ACT = re.compile(r'^(%s)｜(.*)$' % '|'.join(TAGS))
HEAD = re.compile(r'^## (月银纪|纷争纪|山铜纪|迷宫纪)·主线｜(.+?)(（[^）]*）)?\s*$')


def split_name(rest):
    dot = rest.find('。')
    if dot < 0:
        return None, rest
    nm, tail = rest[:dot], rest[dot + 1:]
    if not tail.strip():
        return None, rest
    return nm, tail


drafts = {}
for ji in JI:
    for f in sorted(glob.glob(os.path.join(DRAFT, ji, '*.json'))):
        for k, v in json.load(open(f, encoding='utf-8')).items():
            drafts[(ji, k)] = (os.path.basename(f)[:-5], v['acts'])

# 找卡里的主线条目
found = {}  # (ji,key) -> [(file, start_line_idx, act_line_idxs)]
texts = {}
for ji, pats in FILES.items():
    fs = []
    for p in pats:
        fs += glob.glob(os.path.join(ROOT, p))
    for fp in sorted(set(fs)):
        rel = os.path.relpath(fp, ROOT).replace('\\', '/')
        if '检查稿' in rel or '旧版' in rel:
            continue
        L = open(fp, encoding='utf-8').read().split('\n')
        texts[rel] = L
        i = 0
        while i < len(L):
            m = HEAD.match(L[i])
            if m and m.group(1) == ji:
                key = m.group(2)
                j = i + 1
                acts = []
                while j < len(L) and not L[j].startswith('## '):
                    if ACT.match(L[j]):
                        acts.append(j)
                    j += 1
                found.setdefault((ji, key), []).append((rel, i, acts))
                i = j
                continue
            i += 1

rep = {'ok': [], 'miss_line': [], 'card_only': [], 'tag_mismatch': [], 'noname': [], 'long_old': [], 'changes': []}
for (ji, key), (eid, dacts) in drafts.items():
    locs = found.get((ji, key))
    if not locs:
        rep['miss_line'].append([ji, eid, key])
        continue
    for rel, hi, aidx in locs:
        L = texts[rel]
        ctags = [ACT.match(L[j]).group(1) for j in aidx]
        dtags = [a['tag'] for a in dacts]
        if ctags != dtags:
            rep['tag_mismatch'].append([ji, eid, key, rel, ctags, dtags])
            continue
        for j, a in zip(aidx, dacts):
            m = ACT.match(L[j])
            tag, rest = m.group(1), m.group(2)
            old, tail = split_name(rest)
            if old is not None and re.match(r'^[0-9]+年', old):   # 收束｜11034年霜降月末到归寂月末。…、收束｜1000年冬。… 是年份不是名字
                old = None
            if old is None:
                rep['noname'].append([ji, eid, key, rel, tag, L[j], a['name']])
                continue
            if len(old) > 12:
                rep['long_old'].append([ji, eid, key, rel, tag, old, a['name']])
            new = a['name']
            nl = '%s｜%s。%s' % (tag, new, tail)
            if nl != L[j]:
                rep['changes'].append([ji, eid, key, rel, j + 1, tag, old, new])
                L[j] = nl
            rep['ok'].append([ji, eid, key, rel, tag, old, new])
for (ji, key) in found:
    if (ji, key) not in drafts:
        rep['card_only'].append([ji, key, [x[0] for x in found[(ji, key)]]])

if APPLY:
    touched = sorted({c[3] for c in rep['changes']})
    for rel in touched:
        open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='\n').write('\n'.join(texts[rel]))
    print('写了', len(touched), '个文件')
for k, v in rep.items():
    print(k, len(v))
if JOUT:
    json.dump(rep, open(JOUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
