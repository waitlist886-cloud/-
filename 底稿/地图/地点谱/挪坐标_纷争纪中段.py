# 照纷争纪·炮的年月那一张底图（../样张/纷争纪_炮的年月_样张.jpg，11-08）把几处估的坐标对到图上画的地方：
#   盐海：1088年整片盐原塌下去连上碧湾（../azgaar/az_salthai.js），原来照赤盐内海北岸估的几处落进了水里。
#     图上西边留一个岬角（往后盐沼灯镇 286,1076 在岬角尖上），岬角往西那一段北岸是老滩（红晶滩），七座营垒排在滩上，
#     最东那一座在岬角尖上（照前传：盐沼灯镇是七座里靠东那一座）；红滩链从滩上往东南伸进海里；盐沼在南岸；潮宫在湾底（往后的赤盐沉宫）
#   中段墙下的水门：三河在墙下汇流的那一点，跟山铜纪、前传的水门段城对齐
#   星湖城：画在湖北岸，朝湖那一半沉在水里（原来估的点在湖心）
#   月银原：原来估的点落在海里，挪到雪原西头的冰上
# 挪过的行在“要说明的”末尾记一句原来的坐标。用法：python -I -X utf8 挪坐标_纷争纪中段.py（在 底稿/地图/地点谱/ 下跑，跑完再跑 合表.py）
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MOVES = {
    '纷争纪': {
        '中段墙下的水门': (1021, 753),
        '星湖城': (1952, 436),
        '红晶滩（老滩）': (215, 1094),
        '七座营垒': (221, 1089),
        '红滩链与盐垒（盐场）': (300, 1108),
        '盐沼': (330, 1211),
        '潮宫（湾底）': (357, 1075),
    },
    '山铜纪': {'老滩': (215, 1094)},
    '迷宫纪前传': {'北岸红晶滩和旧营垒': (215, 1094)},
    '月银纪': {'月银原': (905, 168)},
}
for era, moves in MOVES.items():
    p = os.path.join(HERE, era + '.tsv')
    rows = list(csv.DictReader(open(p, encoding='utf8'), delimiter='\t'))
    cols = list(rows[0].keys())
    hit = set()
    for r in rows:
        if r['名字'] in moves:
            nx, ny = moves[r['名字']]
            if (r['地图x'], r['地图y']) != (str(nx), str(ny)):
                r['要说明的'] = (r['要说明的'] + '；' if r['要说明的'] else '') + f"11-08 照纷争纪中段那一张底图挪过，原来 {r['地图x']},{r['地图y']}"
                r['地图x'], r['地图y'] = str(nx), str(ny)
            hit.add(r['名字'])
    miss = set(moves) - hit
    assert not miss, (era, miss)
    with open(p, 'w', encoding='utf8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print(era, '挪了', len(hit))
