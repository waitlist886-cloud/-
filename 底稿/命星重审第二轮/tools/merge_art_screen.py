#!/usr/bin/env python3
# 技艺筛表（11-20）：把 交稿/art_*.md 的表合成 技艺筛表.tsv 和 技艺筛表_第一版.md。
#   python -I -X utf8 底稿/命星重审第二轮/tools/merge_art_screen.py
import collections
import csv
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
W = os.path.join(ROOT, '底稿', '命星重审第二轮')
LOCK = {'城卫枪术': '用户 10-20 照原神组织名加枪术的叫法亲自起的', '灰桥传火': '用户点名的神补完三门之一', '桥头孤枪': '用户 10-20 说桥头孤枪到城卫枪术中间补一环时用的名字'}
UNIFY = {'雷皮盾阵': '朝峰雷皮盾术', '长辙铃圈阵': '长辙铜铃车营法', '定沼开路标术': '生角定沼开路法', '叠瓦盾阵': '鹭桥叠瓦盾术', '长垒接号调': '长垒接号调', '审判庭存疑律': '审判庭存疑誊册法'}
COLS = ['页', '技艺', '判', '拟名', '拟档', '行当', '为什么', '方向', '并入', '生来星提醒', '现档']


def main():
    idx = json.load(open(os.path.join(W, '材料', '艺_索引.json'), encoding='utf-8'))
    tiers = {}
    for key in idx:
        t = open(os.path.join(W, '材料', '艺_%s.md' % key), encoding='utf-8').read()
        for nm, tr in re.findall(r'^【技艺】(\S+)｜现档 (\w+)', t, re.M):
            tiers[(key, nm)] = tr
    got = {}
    for f in glob.glob(os.path.join(W, '交稿', 'art_*.md')):
        key = re.match(r'art_(.+)_\d+[a-f]?\.md$', os.path.basename(f)).group(1)
        for ln in open(f, encoding='utf-8').read().splitlines():
            ln = ln.strip().strip('`')
            if not ln.startswith('行｜'):
                continue
            c = ln.split('｜')[1:]
            c += [''] * (9 - len(c))
            got[(key, c[0].strip())] = [key] + [x.strip() for x in c[:9]]
    rows, miss = [], []
    for key, v in idx.items():
        for nm in v['arts']:
            r = got.get((key, nm))
            if not r:
                miss.append('%s %s' % (key, nm))
                continue
            if nm in UNIFY:
                u = UNIFY[nm]
                if u == nm:
                    if r[2] == '换名':
                        r[2], r[3], r[6] = '改写', nm, '跨页同名，统一留名（主会话）。' + r[6]
                elif r[3] != u:
                    r[2], r[3], r[6] = '换名', u, '跨页同名，统一换成' + u + '（主会话）。' + r[6]
            if nm in LOCK and r[2] in ('换名', '并回'):
                r[2], r[3], r[6] = '改写', nm, LOCK[nm] + '（主会话拦下，原判换成' + r[3] + '）'
            rows.append(r + [tiers.get((key, nm), '')])
    extra = [k for k in got if k[1] not in idx.get(k[0], {}).get('arts', [])]
    with open(os.path.join(W, '技艺筛表.tsv'), 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(COLS)
        w.writerows(rows)
    cnt = collections.Counter(r[2] for r in rows)
    shift = collections.Counter('%s→%s' % (r[10], r[4]) for r in rows if r[10] != r[4])
    md = ['# 技艺筛表·第一版（11-20）', '',
          '照 技艺样稿_第二版.md 的口径，Opus 5.5 逐门判的。全表在 技艺筛表.tsv，这里按判分组列出要动名字的和要用户看的。', '',
          '## 〇、总数', '',
          '- 一共 %d 门。' % len(rows) + '，'.join('%s %d' % (k, cnt[k]) for k in ['留', '改写', '放大', '换名', '并回'] if cnt[k]) + '。',
          '- 改档：' + ('，'.join('%s %d' % kv for kv in shift.most_common()) or '没有') + '。', '']
    if miss:
        md += ['- 表里缺的：' + '、'.join(miss), '']
    if extra:
        md += ['- 表里多出来、名字对不上的：' + '、'.join('%s %s' % k for k in extra), '']
    nf = os.path.join(W, '技艺筛表_主会话按语.md')
    if os.path.exists(nf):
        md += [open(nf, encoding='utf-8').read().rstrip(), '']
    for j, title in [('换名', '一、换名'), ('并回', '二、并回'), ('放大', '三、放大'), ('留', '四、留着不动')]:
        rs = [r for r in rows if r[2] == j]
        md += ['## %s（%d）' % (title, len(rs)), '']
        for r in rs:
            if j == '换名':
                md.append('- %s｜%s（%s）→ **%s**（%s）｜%s。%s｜%s' % (r[0], r[1], r[10], r[3], r[4], r[6], r[5], r[7]))
            elif j == '并回':
                md.append('- %s｜%s（%s）→ 并进 **%s**｜%s｜%s' % (r[0], r[1], r[10], r[8], r[6], r[7]))
            elif j == '放大':
                md.append('- %s｜%s（%s→%s）｜%s。%s｜%s' % (r[0], r[1], r[10], r[4], r[6], r[5], r[7]))
            else:
                md.append('- %s｜%s（%s）｜%s' % (r[0], r[1], r[10], r[6]))
        md.append('')
    rs = [r for r in rows if r[9]]
    md += ['## 五、生来星提醒（%d）' % len(rs), '']
    md += ['- %s｜%s' % (r[0], r[9]) for r in rs]
    md.append('')
    open(os.path.join(W, '技艺筛表_第一版.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md))
    print('合了 %d 门，缺 %d，多 %d' % (len(rows), len(miss), len(extra)), dict(cnt))


if __name__ == '__main__':
    main()
