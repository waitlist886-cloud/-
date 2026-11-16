#!/usr/bin/env python3
# Claude 洗稿人（搭分洗.py 派的）都交了以后，一份活往审稿那一步走的几样，一条龙（11-16 夜）：
#   python -I -X utf8 底稿/洗稿/全卡精炼/收洗.py <份名…>
# 1. 看各段洗稿人交没交（改动说明_第N段.md 在不在），没交齐的这一份跳过。
# 2. `分审.py merge` 把各段洗好的节并回 稿/。
# 3. 改动说明_第N段.md、删除单_第N段.md 并成 改动说明.md、删除单.md（搭分审.py 认这两个文件）。
# 4. 把 稿_Codex原样/ 删掉（备审.py 只在没有它的时候留底，这一回要留的是洗稿人交的样子）。
# 4之二. `还原活人层.py --apply`：旅伴条的手写活人层、台词样例、好感，洗稿人删了改了的照原稿补回。
# 5. `备审.py`（拷最新的自查和洗稿说明、留底、还原星头和节首和栏名、跑自查和查栏目）。
# 6. 量一下这一份可洗的各节留了几成、自查最后一行、查添几句，印出来。
# 派审稿人以前还要跑 `分审.py make` 和 `搭分审.py`（这一支不替你跑，好让你先看一眼数）。
import io
import json
import os
import re
import shutil
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
BASE = 'C:/Users/waitl/codex_work/wash_1115'
FROZEN = re.compile(r'史诗|传唱|设计备注|传奇表|凡世至强|^这一代的命星$|^这一代的人物$')
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))


def run(*a, cwd=ROOT):
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', *a], cwd=cwd, capture_output=True)
    return r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')


def secs(p):
    t = open(p, encoding='utf-8', errors='replace').read().replace('\r', '')
    out, cur = [], None
    for ln in t.split('\n'):
        if ln.startswith('## '):
            cur = [ln[3:].strip(), []]
            out.append(cur)
        elif cur:
            cur[1].append(ln)
    return [(a, '\n'.join(b)) for a, b in out]


for job in sys.argv[1:]:
    d = '%s/%s' % (BASE, job)
    plan = json.load(open(d + '/分审.json', encoding='utf-8'))
    tot = max(len(v) for v in plan.values())
    miss = [n for n in range(1, tot + 1) if not os.path.exists('%s/改动说明_第%d段.md' % (d, n))]
    if miss:
        print('%s｜第 %s 段还没交，跳过' % (job, '、'.join(map(str, miss))))
        continue
    out = run(os.path.join(HERE, '分审.py'), 'merge', job)
    print(out.strip())
    for kind in ('改动说明', '删除单'):
        parts = []
        for n in range(1, tot + 1):
            p = '%s/%s_第%d段.md' % (d, kind, n)
            if os.path.exists(p):
                parts.append('# 第 %d 段\n\n%s' % (n, open(p, encoding='utf-8', errors='replace').read().strip()))
        open('%s/%s.md' % (d, kind), 'w', encoding='utf-8', newline='\n').write('\n\n'.join(parts) + '\n')
    if os.path.isdir(d + '/稿_Codex原样'):
        shutil.rmtree(d + '/稿_Codex原样')
    # 旅伴条的活人层、台词样例、好感，洗稿人删了的照原稿补回（洗稿说明第五节：照留）
    out = run(os.path.join(HERE, '还原活人层.py'), job, '--apply')
    for l in out.strip().split('\n'):
        if l.strip() and not l.startswith('一共 0'):
            print('  ' + l)
    out = run(os.path.join(HERE, '备审.py'), job)
    for l in out.strip().split('\n'):
        if l.strip() and '还原了 0 处' not in l:
            print(l)
    ho = hn = 0
    rows = []
    for fn in json.load(open(d + '/job.json', encoding='utf-8'))['files']:
        fn = os.path.basename(fn)
        o, n = secs('%s/原/%s' % (d, fn)), dict(secs('%s/稿/%s' % (d, fn)))
        for t, body in o:
            if FROZEN.search(t):
                continue
            a, c = han(body), han(n.get(t, ''))
            ho += a
            hn += c
            if a >= 400 and body == n.get(t):
                rows.append('没洗：%s｜%s' % (fn, t[:30]))
            elif a >= 400 and c > a:
                rows.append('比原稿长：%s｜%s（%d → %d）' % (fn, t[:30], a, c))
    add = run(os.path.join(HERE, '查添.py'), job, '--min', '0.6', '--quiet')
    m = re.search(r'列出 (\d+) 句', add)
    addn = int(m.group(1)) if m else -1
    last = [l for l in open(d + '/自查_备审.txt', encoding='utf-8', errors='replace').read().split('\n') if l.startswith('错 ')]
    print('%s｜可洗的各节 %d → %d（留 %d%%）｜自查 %s｜查添 %d 句' % (job, ho, hn, 100 * hn / max(1, ho), last[-1] if last else '?', addn))
    for r in rows[:12]:
        print('  ' + r)
