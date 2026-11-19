#!/usr/bin/env python3
# 全卡精炼洗稿：一页太长，一位审稿人读不完，就照 ## 切成几段，一位审稿人一段（11-16）。在仓库根上跑：
#   python -I -X utf8 底稿/洗稿/全卡精炼/分审.py make <份名…> [--cap 24000]     备审以后跑：给每一段拷一份 稿_审N/，写 分审.json，印出各段从哪一节到哪一节
#   python -I -X utf8 底稿/洗稿/全卡精炼/分审.py merge <份名…>                  审稿人都交了以后跑：各段的节从各自那一份里取，并回 稿/
# 审稿人只改自己那一段的节，自查照 `python -I -X utf8 自查.py 稿_审N 原` 跑。并的时候照节的次序认（同一页里“裁定锁”这种标题会重），
# 审稿人动了别的段的节，并的时候不收、印出来。冻住的节（史诗、传唱、设计备注、传奇表、凡世至强）和页首都照 稿/ 里现在的样子。
# 万兽十五歌一页两三万字，一位审稿人一页就够，用不着这一支；诸国期、萨尔维斯一页四万到七万字，要分。
import io
import json
import os
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
FROZEN = re.compile(r'史诗|传唱|设计备注|传奇表|凡世至强')
NO_HEAD = re.compile(r'^(?:裁定锁|旅途同行·背景|这一段旅伴之间)')          # 这几种节不当一段的开头（跟着前头那一节走）


def han(s):
    return len(re.findall(r'[\u4e00-\u9fff]', s))


def cut(text):
    """回 (页首, [(标题, 整节)])。"""
    idx = [m.start() for m in re.finditer(r'^## ', text, re.M)] + [len(text)]
    return text[:idx[0]], [(text[a:text.index('\n', a)][3:].strip(), text[a:b]) for a, b in zip(idx, idx[1:])]


def read(p):
    raw = open(p, encoding='utf-8', newline='').read()
    return raw.replace('\r\n', '\n'), '\r\n' in raw


def make(job, cap):
    """一份活里的几个文件接成一串节，照可洗的字数匀着切成几段，一位审稿人一段（11-16 傍晚改的：
    原来一个文件各切各的，文件多的活里第 1 位审稿人会摊上每个文件的头一段，读不完）。
    分审.json 里 plan[文件] 是一个列表，第 k 项是第 k 位审稿人在这个文件里管的节的序号，可以是空的。"""
    d = BASE + '/' + job
    meta = json.load(open(d + '/job.json', encoding='utf-8'))
    items, secs = [], {}
    for base in meta['files']:
        old, _ = read(d + '/原/' + base)
        new, _ = read(d + '/稿/' + base)
        _, so = cut(old)
        _, sn = cut(new)
        assert [t for t, _ in so] == [t for t, _ in sn], ('原稿和洗后的节对不上', job, base)
        secs[base] = (so, sn)
        # 11-19：job.json 里写了 only（文件 → 要洗的节的序号）的，只切这几节，别的节照冻住算（山铜纪剧情铺开那一轮，页上早先洗过的旧节不再洗）
        only = meta.get('only', {}).get(base)
        for i, (t, s) in enumerate(so):
            if not FROZEN.search(t) and (only is None or i in only):
                items.append((base, i, han(s), t))
    total = sum(h for _, _, h, _ in items)
    n = max(1, -(-total // cap))
    per = total / n
    groups, cur, acc = [], [], 0
    for it in items:
        if cur and acc + it[2] / 2 > per and len(groups) < n - 1 and not NO_HEAD.search(it[3]):
            groups.append(cur)
            cur, acc = [], 0
        cur.append(it)
        acc += it[2]
    groups.append(cur)
    plan = {base: [[i for b, i, _, _ in g if b == base] for g in groups] for base in meta['files']}
    print('== %s｜%d 个文件｜可洗 %d 字，分 %d 段' % (job, len(meta['files']), total, len(groups)))
    for k, g in enumerate(groups, 1):
        files = []
        for b, _, _, _ in g:
            if b not in files:
                files.append(b)
        new_h = sum(han(secs[b][1][i][1]) for b, i, _, _ in g)
        print('  第 %d 段（稿_审%d/）｜%d 节｜原 %d 字 → 洗后 %d 字｜%s｜从「%s」到「%s」' % (
            k, k, len(g), sum(h for _, _, h, _ in g), new_h, '、'.join(files), g[0][3][:30], g[-1][3][:30]))
    n = len(groups)
    for k in range(1, n + 1):
        dst = d + '/稿_审%d' % k
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(d + '/稿', dst)
    json.dump(plan, open(d + '/分审.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def merge(job):
    d = BASE + '/' + job
    plan = json.load(open(d + '/分审.json', encoding='utf-8'))
    for base, parts in plan.items():
        cur, crlf = read(d + '/稿/' + base)
        head, sc = cut(cur)
        out = [s for _, s in sc]
        took, stray = 0, []
        for k, p in enumerate(parts, 1):
            rev, _ = read(d + '/稿_审%d/' % k + base)
            _, sr = cut(rev)
            assert [t for t, _ in sr] == [t for t, _ in sc], ('审稿人那一份的节对不上（标题行被动过）', job, base, k)
            for i, (t, s) in enumerate(sr):
                if s == sc[i][1]:
                    continue
                if i in p:
                    out[i] = s
                    took += 1
                else:
                    stray.append('第 %d 段的审稿人动了别的段的节，没收：%s' % (k, t[:40]))
        text = head + ''.join(out)
        open(d + '/稿/' + base, 'w', encoding='utf-8', newline='').write(text.replace('\n', '\r\n') if crlf else text)
        print('%s｜%s：并了 %d 节' % (job, base, took))
        for s in stray:
            print('  ！' + s)


def main():
    args = [a for a in sys.argv[2:] if not a.startswith('--')]
    cap = 24000
    if '--cap' in sys.argv:
        k = sys.argv[sys.argv.index('--cap') + 1]
        cap = int(k)
        args.remove(k)
    for job in args:
        (make(job, cap) if sys.argv[1] == 'make' else merge(job))


if __name__ == '__main__':
    main()
