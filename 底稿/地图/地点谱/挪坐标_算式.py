# 11-10 基本算式（用户回“甲，其余也都按倾向来”）：灰雨城照纷争纪第七页、山铜纪第四、六页挪到塌门东边的墙脚下（城西那一截墙塌了就是塌门）。
# 11-08 那一回画在墙线往东 22 格，照一格十九公里是四百多公里，文里一律写墙脚下。
# 挪过的行在“要说明的”末尾记一句原来的坐标。用法：python -I -X utf8 挪坐标_算式.py（在 底稿/地图/地点谱/ 下跑，跑完再跑 合表.py）
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MOVES = {
    '纷争纪.tsv': {'灰雨城': (1022.0, 751.0)},
    '山铜纪.tsv': {'灰雨城': (1022.0, 751.0)},
    '迷宫纪前传.tsv': {'灰雨城遗址': (1022.0, 751.0)},
}
for fn, moves in MOVES.items():
    p = os.path.join(HERE, fn)
    with open(p, encoding='utf-8', newline='') as f:
        rows = list(csv.reader(f, delimiter='\t'))
    head = rows[0]
    ix, iy, inote, iname = head.index('地图x'), head.index('地图y'), head.index('要说明的'), head.index('名字')
    done = 0
    for r in rows[1:]:
        if r[iname] in moves:
            x, y = moves[r[iname]]
            old = '%s,%s' % (r[ix], r[iy])
            if old == '%s,%s' % (x, y) or '基本算式' in r[inote]:
                continue
            r[ix], r[iy] = ('%g' % x), ('%g' % y)
            r[inote] = (r[inote] + '；' if r[inote] else '') + '11-10 基本算式照文挪到塌门东边的墙脚下，原来 %s' % old
            done += 1
    with open(p, 'w', encoding='utf-8', newline='') as f:
        csv.writer(f, delimiter='\t', lineterminator='\n').writerows(rows)
    print(fn, '挪了', done)
