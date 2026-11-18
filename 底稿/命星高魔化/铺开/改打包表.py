# -*- coding: utf-8 -*-
"""铺开·改打包表：out/进卡_v12/tools/batch_edits_v12.py 里 STAR_GATE 往后那几张表写着的星名，照全谱这一轮的改名换成新名。
只换带引号的整个名字（'旧名' 或 '旧名@页'），旧名 → 新名照全谱.tsv 的 旧名、原技艺 两栏。一个旧名在几页对着不同新名的，带页的照页换，不带页的列出来手看。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/改打包表.py [--apply]"""
import io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 搭活 as D

F = os.path.join(D.ROOT, 'out', '进卡_v12', 'tools', 'batch_edits_v12.py')
NUM = '一二三四五六七'
bypage = {}
byname = collections.defaultdict(set)
for r in D.read_tsv('全谱.tsv'):
    new = (r.get('技艺') or '').strip()
    for a in re.split('[、，,]', (r.get('旧名') or '') + '、' + (r.get('原技艺') or '')):
        a = a.strip()
        if a and new and a != new:
            bypage[(r['页'], a)] = new
            byname[a].add(new)


def page_of(key):
    # 山铜纪时段_三_白鸦的年月 → 山铜纪_三；第七歌_焚原断刃 → 第七歌；诸国期时段_二_午祷上 → 诸国期_二；迷宫纪前传时段_四_… → 迷宫纪前传_四
    m = re.match(r'(纷争纪|山铜纪|迷宫纪前传|诸国期|萨尔维斯)时段_(.)', key)
    if m:
        return m.group(1) + '_' + m.group(2)
    m = re.match(r'(第.{1,2}歌)', key)
    return m.group(1) if m else key


s = io.open(F, encoding='utf-8', newline='').read()
i0 = s.index('STAR_GATE = {')
head, body = s[:i0], s[i0:]
n, todo = 0, []


def rep(m):
    global n
    q, name, at, page = m.group(1), m.group(2), m.group(3), m.group(4)
    if at:
        new = bypage.get((page_of(page), name))
        if new:
            n += 1
            print('  %s@%s → %s' % (name, page_of(page), new))
            return q + new + '@' + page + q
        return m.group(0)
    if name in byname:
        if len(byname[name]) == 1:
            new = list(byname[name])[0]
            n += 1
            print('  %s → %s' % (name, new))
            return q + new + q
        todo.append('%s 对着几个新名：%s' % (name, '、'.join(sorted(byname[name]))))
    return m.group(0)


body2 = re.sub(r"(['\"])([^'\"@\n]{2,24})(@([^'\"\n]{3,40}))?\1", rep, body)
print('换 %d 处' % n)
for t in sorted(set(todo)):
    print('手看｜' + t)
if '--apply' in sys.argv:
    D.safe_write(F, head + body2)
    print('写了')
