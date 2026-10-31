"""前传某一页：每一段「这一段旅伴之间」的黑名单里那一组 `/页名·(?:…)·`，换成同页别的所有段名。
usage: python3 -I -X utf8 tools/pairbl.py . N [--apply]（10-31 拼前传各页时用的，N 是页号，不加 --apply 只报）"""
import sys, os, re, glob
root, n = sys.argv[1], int(sys.argv[2]); apply = '--apply' in sys.argv
P = os.path.join(root, '迷宫纪前传', 'parts%d' % n)
forks = []
for f in sorted(glob.glob(os.path.join(P, '*_*.md'))):
    m = re.match(r'([a-o])(\d?)_', os.path.basename(f))
    if not m: continue
    t = open(f, encoding='utf-8').read()
    mm = re.search(r'^## 迷宫纪·主线｜([^·\n]+)·([^\n]+)$', t, re.M)
    if not mm: continue
    forks.append((f, mm.group(1), mm.group(2).strip()))
segs = [s for _, _, s in forks]
print('segments:', '、'.join(segs))
for f, page, seg in forks:
    L = open(f, encoding='utf-8').read().split('\n')
    try:
        i = next(i for i, l in enumerate(L) if l.startswith('## 这一段旅伴之间'))
        j = next(j for j in range(i, len(L)) if L[j].startswith('> 条目设置'))
    except StopIteration:
        print('  无旅伴之间：', os.path.basename(f)); continue
    m = re.search(r'黑名单 `/%s·\(\?:([^)]*)\)·' % re.escape(page), L[j])
    if not m:
        print('  黑名单没有段名那一组：', os.path.basename(f), L[j][:80]); continue
    have = m.group(1).split('|')
    want = [s for s in segs if s != seg]
    keep_extra = [h for h in have if h not in segs]   # 别的叫法照留
    new = want + keep_extra
    if have == new:
        print('  不变：', seg); continue
    print('  %s：%s → %s' % (seg, '|'.join(have), '|'.join(new)))
    L[j] = L[j][:m.start(1)] + '|'.join(new) + L[j][m.end(1):]
    if apply:
        open(f, 'w', encoding='utf-8').write('\n'.join(L))
