# 各纪路程参考表（11-10 基本算式）：照 底稿/地图/地点谱/合表.tsv 的坐标（一格十九公里），一纪一张两两之间的距离和走路天数。
# 给改锚的人查，也给打包时「从这里出发」那一块用。用法（仓库根上）：python -I -X utf8 底稿/算式/route_ref.py [输出目录]
# 输出：路程参考_<纪>.tsv（A、B、方向、直线公里、走路天数、骑马、驿马），只收统一主次是「主要」的地方。
import csv
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
KM = 19.0
DETOUR = 1.25          # 地上的路比直线绕两成五
WALK = 30.0            # 走路一天三十公里上下（含寻常的歇脚、吃饭、扎营）
MODES = (('走路', 1.0), ('骑马', 2.0), ('驿马', 4.5))
DIR = ['东', '东南', '南', '西南', '西', '西北', '北', '东北']
ERAS = ('月银纪', '纷争纪', '山铜纪', '迷宫纪前传')


def load():
    rows = list(csv.DictReader(open(os.path.join(ROOT, '底稿/地图/地点谱/合表.tsv'), encoding='utf-8'), delimiter='\t'))
    out = {}
    for r in rows:
        try:
            x, y = float(r['地图x']), float(r['地图y'])
        except ValueError:
            continue
        out.setdefault(r['纪'], {})[r['名字']] = {'xy': (x, y), '类': r['类'], '主次': r['统一主次'], '年份': r['时段与年份']}
    return out


def km(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1]) * KM


def direction(a, b):
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))   # 图上 y 往下是南
    return DIR[int(((ang + 22.5) % 360) // 45)]


def walk_days(d):
    return d * DETOUR / WALK


def main():
    P = load()
    for era in ERAS:
        pts = {k: v for k, v in P.get(era, {}).items() if v['主次'] == '主要'}
        names = sorted(pts)
        path = os.path.join(OUT, '路程参考_%s.tsv' % era)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('A\tB\t方向\t直线公里\t走路天数\t骑马天数\t驿马天数\tA的类\tB的类\n')
            for i, a in enumerate(names):
                for b in names[i + 1:]:
                    d = km(pts[a]['xy'], pts[b]['xy'])
                    w = walk_days(d)
                    f.write('%s\t%s\t%s\t%d\t%.1f\t%.1f\t%.1f\t%s\t%s\n' % (a, b, direction(pts[a]['xy'], pts[b]['xy']), d, w, w / 2, w / 4.5, pts[a]['类'], pts[b]['类']))
        print(era, len(names), '处主要地点', path)


if __name__ == '__main__':
    main()
