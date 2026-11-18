# -*- coding: utf-8 -*-
"""把 Art传承表_定稿.md 里的各张总表解析出来，按脉数。
用法：python -I -X utf8 mai.py [--rows] [--tsv 输出]
"""
import io, re, sys, collections

text = io.open('Art传承表_定稿.md', encoding='utf-8').read().replace('\r\n', '\n')
rows = []
for line in text.split('\n'):
    if not line.startswith('|'):
        continue
    cells = [c.strip() for c in line.strip().strip('|').split('|')]
    if len(cells) < 7:
        continue
    if not re.match(r'^\d+$', cells[0]):
        continue
    # 编号 名 页 持有人 起头阶 现阶 脉 说明
    num, name, page, who = cells[0], cells[1], cells[2], cells[3]
    t0, t1, mai = cells[4], cells[5], cells[6]
    note = cells[7] if len(cells) > 7 else ''
    rows.append((int(num), name, page, who, t0, t1, mai, note))

print('行数', len(rows))
c = collections.Counter(r[6] for r in rows)
era = lambda p: p.split('·')[0]
print('脉数', len(c))
for k, v in c.most_common():
    eras = collections.Counter(era(r[2]) for r in rows if r[6] == k)
    print('%3d %s  %s' % (v, k, dict(eras)))
if '--rows' in sys.argv:
    for r in rows:
        print('\t'.join(str(x) for x in r[:7]))
if '--tsv' in sys.argv:
    out = sys.argv[sys.argv.index('--tsv') + 1]
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('编号\t名\t页\t持有人\t起头阶\t现阶\t脉\t说明\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
