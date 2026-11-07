# -*- coding: utf-8 -*-
"""收稿检查：从各份输出里抽【…】名号和新起名字，查卡面口径、长度、段数、撞名、收尾字。
用法：python3 -I -X utf8 check_names.py 仓库根 份1.md 份2.md ..."""
import sys, re, json, collections, os
root = sys.argv[1]; files = sys.argv[2:]
BAN_PUNCT = ['——', '—', '；', '…', '！', '...', '"', "'", '｜', ':', '：', '|']
MOON = ['新月', '满月', '残月', '月牙', '弦月', '月亮', '月光']
BAN_WORDS = '学宫 客栈 朝廷 门客 时辰 掌柜 百官 丫头 宗门 长老 功法 镖局 一丝 一抹 不禁 威压 修为 登记 军令 条例 晋升 量子 熵 坐标 频率 能量 系统'.split()
VACUOUS = ['终焉', '无上', '万古']
XIAN = ['宗', '尊', '帝君', '魔尊', '仙', '真人', '道君', '天尊', '大能']
NAME_RE = re.compile(r'【([^【】\n]{2,80})】')
# 底卡里的整段名号
card = json.load(open(os.path.join(root, 'src/rili_v7.json'), encoding='utf-8'))
lb = card.get('prompt', card).get('lorebook') if isinstance(card.get('prompt'), dict) else card.get('lorebook')
base_segs = collections.Counter()
for e in lb or []:
    txt = e.get('content') or ''
    for m in NAME_RE.finditer(txt):
        s = m.group(1)
        if '，' in s:
            for seg in s.split('，'):
                seg = seg.strip()
                if 2 <= len(seg) <= 12: base_segs[seg] += 1
allnames = collections.defaultdict(list)
allsegs = collections.defaultdict(list)
newnames = collections.defaultdict(list)
for f in files:
    tag = os.path.basename(f).replace('.md', '')
    text = open(f, encoding='utf-8').read()
    # 只看总表那一节到锁改写清单之前，粗略：所有带【】的表格行
    tails = collections.Counter()
    probs = []
    seen = set()
    for ln, line in enumerate(text.split('\n'), 1):
        mnew = re.match(r'^- ([^｜\s]{1,12})｜(.+?)｜namegrep[：:]\s*(.*)$', line.strip())
        if mnew:
            newnames[mnew.group(1)].append((tag, ln, mnew.group(3)[:30]))
        if not (line.startswith('|') or re.match(r'^\s*-\s*(?:\*\*)?[一二三四五六七八九十]+阶', line)): continue
        if '润色记录' in line: continue
        for m in NAME_RE.finditer(line):
            s = m.group(1)
            if '，' not in s and len(s) < 4: continue
            if s in seen: continue
            seen.add(s)
            allnames[s].append((tag, ln))
            segs = [x.strip() for x in s.split('，')]
            for seg in segs:
                allsegs[seg].append((tag, ln))
                tails[seg[-2:]] += 1
            L = len(s.replace('，', ''))
            if L > 40: probs.append(f'L{ln} 超长{L}：{s}')
            if len(segs) > 4: probs.append(f'L{ln} 段数{len(segs)}：{s}')
            for seg in segs:
                if len(seg) > 10: probs.append(f'L{ln} 段长{len(seg)}：{seg}')
                if len(seg) < 2: probs.append(f'L{ln} 段太短：{seg}')
            for p in BAN_PUNCT:
                if p in s: probs.append(f'L{ln} 标点{p}：{s}')
            for w in MOON + BAN_WORDS + VACUOUS:
                if w in s: probs.append(f'L{ln} 禁{w}：{s}')
            for w in XIAN:
                if w in s: probs.append(f'L{ln} 中式?{w}：{s}')
            for seg in segs:
                if seg in base_segs: probs.append(f'L{ln} 撞底卡名号段「{seg}」：{s}')
    print(f'===== {tag}：名号 {len(seen)} 个')
    for p in probs: print('  ', p)
    common = [(t, n) for t, n in tails.most_common(12) if n >= 4]
    print('   收尾两字多的：', '、'.join(f'{t}×{n}' for t, n in common))
print('===== 跨份同一整段名号')
for s, where in allnames.items():
    tags = {t for t, _ in where}
    if len(tags) > 1: print('  ', s, where)
print('===== 跨份同一段（4字以上）')
for seg, where in sorted(allsegs.items(), key=lambda x: -len(x[1])):
    tags = {t for t, _ in where}
    if len(seg) >= 4 and len(where) > 1:
        print('  ', seg, len(where), sorted(tags))
print('===== 新起名字重名')
for n, where in newnames.items():
    if len(where) > 1: print('  ', n, where)
print('新起名字总数', len(newnames))
json.dump(sorted(newnames), open(os.path.join(os.path.dirname(files[0]), 'newnames.json'), 'w', encoding='utf-8'), ensure_ascii=False)
