# 照山铜纪·麦的年月那一张底图（../样张/山铜纪_麦的年月_样张.jpg，11-08）把几处估的坐标对到图上：
#   灰岗、石辙谷、没垒完的攻城神殿、辙口城、南边的群山：条目估的点落进了1088年塌下去的盐海里（盐原整片塌了，见 挪坐标_纷争纪中段.py），
#     图上灰岗放在盐海东岸往东的台地上（高座照纷争纪中段那一张的位置，520,1100），石辙谷往东南，谷口的辙口城挨着南岸；
#     南边的群山照条目“从蓝焰火山带往西一直排到西海边上”，放在盐海南边那一溜岸上
#   前传那两行（石辙谷和辙口城、灰岗）原来没坐标，跟着填上
# 挪过的行在“要说明的”末尾记一句原来的坐标。用法：python -I -X utf8 挪坐标_山铜纪.py（在 底稿/地图/地点谱/ 下跑，跑完再跑 合表.py）
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MOVES = {
    '山铜纪': {'灰岗': (520, 1100), '石辙谷': (530, 1118), '没垒完的攻城神殿': (532, 1122), '辙口城': (545, 1128), '南边的群山': (330, 1228)},
    '迷宫纪前传': {'灰岗': (520, 1100), '石辙谷和辙口城': (545, 1128), '南边的群山': (330, 1228)},
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
                r['要说明的'] = (r['要说明的'] + '；' if r['要说明的'] else '') + f"11-08 照山铜纪那一张底图挪过，原来 {r['地图x']},{r['地图y']}"
                r['地图x'], r['地图y'] = str(nx), str(ny)
            hit.add(r['名字'])
    miss = set(moves) - hit
    assert not miss, (era, miss)
    with open(p, 'w', encoding='utf8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print(era, '挪了', len(hit))
