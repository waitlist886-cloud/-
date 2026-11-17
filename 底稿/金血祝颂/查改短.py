#!/usr/bin/env python3
# 金血祝颂改短那一轮的收稿检查（11-17 晚）：照 改短_派活说明.md 逐颗查格式、字数、名字、祝颂和箴言的架子、六维，
# 再把七十九个名字放一起看撞不撞、构词挤不挤。
#   python -I -X utf8 底稿/金血祝颂/查改短.py [稿目录]        默认 底稿/金血祝颂/稿_改短
# 六维对照原稿（稿_改短前/ 有就用它，没有就用 稿/）。
import csv
import glob
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
NEW = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '稿_改短')
OLD = os.path.join(HERE, '稿_改短前') if os.path.isdir(os.path.join(HERE, '稿_改短前')) else os.path.join(HERE, '稿')

ROWS = list(csv.DictReader(open(os.path.join(HERE, '名单.tsv'), encoding='utf-8'), delimiter='\t'))
GODS = sorted({r['神'] for r in ROWS} | {r['倒影的魔神'] for r in ROWS if r['倒影的魔神']}, key=len, reverse=True)
ERA_ONLY = ['魔神', '长垒', '段城', '联军', '军册', '萨尔维斯', '辉塔', '星冠圣城', '白烛', '客星城', '浮空塔', '机兵',
            '炮', '列车', '命路', '面板', '旅印', '公会']
SEVEN_BAN = ['公会', '旅印', '委托', '黑耀', '灰之魔女']
BAD_PUNCT = ['——', '—', '；', '…', '！', '...', '「', '」']
MOON = ['新月', '满月', '残月', '月牙', '弦月', '月亮', '月光']
EMPTY = ['命运', '荣耀', '宿命', '羁绊', '永恒']
STAT = re.compile(r'(STR|DEX|MANA|MIND|VGR|FTH)／(STR|DEX|MANA|MIND|VGR|FTH) \+30%。?$')


def parse(p):
    s = open(p, encoding='utf-8').read().replace('\r', '')
    s = re.split(r'\n## 备注', s)[0]
    out = []
    heads = list(re.finditer(r'(?m)^### (.+?) \(Passive \| Legend\)\s*$', s))
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(s)
        body = s[m.end():end]
        f = {}
        for ln in body.split('\n'):
            ln = ln.strip()
            mm = re.match(r'^(?:- |> )?(祝颂|箴言|被动|限制|只给 AI|前传的局|修行关联|世界反应)[：，](.*)$', ln)
            if mm:
                f[mm.group(1)] = mm.group(2).strip()
            elif ln.startswith('【调用】'):
                f['调用'] = ln[len('【调用】'):].strip()
        out.append((m.group(1).strip(), f, body))
    return out


def han(t):
    return len(re.findall(r'[一-鿿]', t))


old_stat = {}
for p in sorted(glob.glob(os.path.join(OLD, '份*.md'))):
    fen = re.match(r'(份\d)', os.path.basename(p)).group(1)
    names = [r['神'] for r in ROWS if r['份'] == fen]
    for god, (nm, f, _) in zip(names, parse(p)):
        m = STAT.search(f.get('被动', ''))
        old_stat[(fen, god)] = m.group(0).rstrip('。') if m else ''

errs, warns, allnames = [], [], []
for p in sorted(glob.glob(os.path.join(NEW, '份*.md'))):
    fen = re.match(r'(份\d)', os.path.basename(p)).group(1)
    gods = [r['神'] for r in ROWS if r['份'] == fen]
    got = parse(p)
    seven = fen == '份8'
    if len(got) != len(gods):
        errs.append('%s 有 %d 颗，名单 %d 位' % (fen, len(got), len(gods)))
        continue
    wish = quote = alt = kid = 0
    for god, (nm, f, body) in zip(gods, got):
        tag = '%s %s【%s】' % (fen, god, nm)
        allnames.append((fen, god, nm))
        if han(nm) != 4 or len(nm) != 4:
            errs.append(tag + ' 名字不是四个字')
        need = ['调用', '祝颂', '箴言', '被动', '限制'] + (['只给 AI', '前传的局'] if seven else [])
        for k in need:
            if not f.get(k):
                errs.append(tag + ' 缺 ' + k)
        for k in ('修行关联', '世界反应'):
            if k in f:
                errs.append(tag + ' 还留着 ' + k)
        if re.search(r'(?m)^【' + re.escape(nm) + '】', body):
            errs.append(tag + ' 还留着“这一颗是什么”那一段')
        L = {k: han(v) for k, v in f.items()}
        lim = {'调用': (12, 48), '祝颂': (36, 72), '箴言': (10, 36), '被动': (40, 130 if seven else 110), '限制': (14, 60)}
        for k, (lo, hi) in lim.items():
            if k in L and not (lo <= L[k] <= hi):
                warns.append('%s %s %d 字（%d 到 %d）' % (tag, k, L[k], lo, hi))
        zs = f.get('祝颂', '')
        if '的黄金裔' not in zs:
            errs.append(tag + ' 祝颂头一截没有“的黄金裔”')
        second = zs.split('的黄金裔', 1)[1] if '的黄金裔' in zs else ''
        if not re.match(r'^[，。]?\s*(你要|启程吧|你可愿|去吧|你可肯|你可敢)', second):
            alt += 1
            warns.append(tag + ' 第二截起法：' + second[:8])
        elif not re.match(r'^[，。]?\s*你要', second):
            alt += 1
        if '“' in zs or '”' in zs:
            errs.append(tag + ' 祝颂里套了引号')
        if '孩子' in zs.split('的黄金裔')[0]:
            kid += 1
        zy = f.get('箴言', '')
        wish += zy.startswith('愿')
        quote += zy.startswith('“')
        st = STAT.search(f.get('被动', ''))
        if not st:
            errs.append(tag + ' 被动末尾没有“XXX／YYY +30%”')
        elif old_stat.get((fen, god)) and st.group(0).rstrip('。') != old_stat[(fen, god)]:
            errs.append(tag + ' 六维跟原稿不一样：%s → %s' % (old_stat[(fen, god)], st.group(0)))
        text = '\n'.join(v for k, v in f.items() if k not in ('只给 AI', '前传的局'))
        for g in GODS:
            if g in text:
                errs.append(tag + ' 卡面点了神名 ' + g)
        if '只给 AI' in f:
            for g in GODS:
                if g in f['只给 AI'] and g not in ('欧巴德斯', '伊兹帕鲁特', '库米罗妮', '艾赫卡托尔', '朱亚', '耶万', '璐璐薇'):
                    errs.append(tag + ' 只给 AI 点了倒下诸神的名字 ' + g)
        for w in (SEVEN_BAN if seven else ERA_ONLY):
            if w in text:
                errs.append(tag + ' 一纪才有的字 ' + w)
        for w in BAD_PUNCT + MOON:
            if w in '\n'.join(f.values()):
                errs.append(tag + ' 禁用 ' + w)
        for w in EMPTY:
            if w in zs + zy:
                warns.append(tag + ' 空词 ' + w)
        for k, v in f.items():
            if '：' in v:
                errs.append(tag + ' %s 那一行里还有冒号' % k)
    if wish > 1:
        warns.append('%s 愿字起头的箴言 %d 颗' % (fen, wish))
    if quote > 2:
        warns.append('%s 引语箴言 %d 颗' % (fen, quote))
    if alt > 2:
        warns.append('%s 第二截不是“你要”的 %d 颗' % (fen, alt))
    if kid > 3:
        warns.append('%s 称呼带“孩子”的 %d 颗' % (fen, kid))

cnt = Counter(n for _, _, n in allnames)
for n, c in cnt.items():
    if c > 1:
        errs.append('名字重了：%s ×%d' % (n, c))
# 两个名字共用两个以上的字，列出来人看
pairs = []
for i, (f1, g1, a) in enumerate(allnames):
    for f2, g2, b in allnames[i + 1:]:
        com = [ch for ch in set(a) if ch in b and ch not in '之而与以于有无的']
        if len(com) >= 2:
            pairs.append('%s（%s）／%s（%s）' % (a, g1, b, g2))

print('名字 %d 个' % len(allnames))
for fen in sorted({f for f, _, _ in allnames}):
    print(fen, '　'.join('%s·%s' % (g, n) for f, g, n in allnames if f == fen))
print('\n== 错 %d' % len(errs))
for e in errs:
    print('  ' + e)
print('\n== 看 %d' % len(warns))
for w in warns:
    print('  ' + w)
print('\n== 共用两个字以上的名字 %d 对' % len(pairs))
for x in pairs:
    print('  ' + x)
