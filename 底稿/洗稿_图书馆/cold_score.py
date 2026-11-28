#!/usr/bin/env python3
# 冷笔密度排表（11-28）：数每本书正文里冷笔的样子，每千字几处，写 冷笔密度表.md。
# 正文只算散文行：跳过元信息、## 标题、〔〕标记行、设计备注以后、表格、引用块。歌诗多的书照数也会低，排表只是挑先后，不是判词。
#   python -I -X utf8 底稿/洗稿_图书馆/cold_score.py
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, '底稿', '门面', '第二轮', '大图书馆', '书稿')
DONE = os.path.join(os.path.dirname(__file__), '重写')
OUT = os.path.join(os.path.dirname(__file__), '冷笔密度表.md')

STAMP = re.compile(r'(立住了|我认了|认了|作数|算数|记下了|收了|就够了|不画|不问|不写|照旧|没说话)[。]')
SHORT_END = re.compile(r'[。？]([^。？\n，、]{1,6}。)\s*$')  # 段末一个六字以内的冷收句
NUM2 = re.compile(r'[一二三四五六七八九十百千万两0-9]+[^。，\n]{0,3}。[^。，\n]{1,4}。')  # 报数加两三个字
NEGSYM = re.compile(r'([^。，\n]{1,6})了，([^。，\n]{1,6})没有。|不[^。，\n]{1,3}。[^。，\n]{0,2}也不[^。，\n]{1,3}。')


def body(text):
    out = []
    for ln in text.split('\n'):
        s = ln.strip()
        if s.startswith('## ') and ('设计备注' in s or '备注' in s and '设计' in s):
            break
        if not s or s.startswith('#') or s.startswith('|') or s.startswith('>') or s.startswith('〔') or s.startswith('- ') or re.match(r'^[^。]{0,12}[：:]', s):
            continue
        out.append(s)
    return out


def score(path):
    t = open(path, encoding='utf-8').read()
    lines = body(t)
    chars = sum(len(x) for x in lines) or 1
    stamp = sum(len(STAMP.findall(x)) for x in lines)
    short = sum(1 for x in lines if SHORT_END.search(x)) + sum(1 for x in lines if 0 < len(x) <= 8 and x.endswith('。'))
    num2 = sum(len(NUM2.findall(x)) for x in lines)
    neg = sum(len(NEGSYM.findall(x)) for x in lines)
    hits = stamp * 2 + short + num2 + neg
    return chars, stamp, short, num2, neg, hits * 1000 / chars


def main():
    done = {f[:-3] for f in os.listdir(DONE) if f.endswith('.md') and not f.endswith('_改动单.md') and f != '第一批收稿.md'}
    rows = []
    for f in sorted(os.listdir(SRC)):
        if not f.endswith('.md'):
            continue
        c, a, b, n, g, d = score(os.path.join(SRC, f))
        rows.append((d, f[:-3], c, a, b, n, g, f[:-3] in done))
    rows.sort(reverse=True)
    with open(OUT, 'w', encoding='utf-8') as w:
        w.write('# 冷笔密度表（cold_score.py 出的，每千字加权处数，盖章词算两处）\n\n')
        w.write('| 次 | 书 | 正文字 | 盖章词 | 段末冷收 | 报数短收 | 否定对称 | 每千字 | 状态 |\n|---|---|---|---|---|---|---|---|---|\n')
        for i, (d, n, c, a, b, nn, g, dn) in enumerate(rows, 1):
            w.write('| %d | %s | %d | %d | %d | %d | %d | %.1f | %s |\n' % (i, n, c, a, b, nn, g, d, '已重写' if dn else ''))
    for i, r in enumerate(rows[:60], 1):
        print(i, r[1], r[2], '%.1f' % r[0], '已' if r[7] else '')


if __name__ == '__main__':
    main()
