# 照时代地图方向稿第十二节那五件（11-08 用户回“照倾向”）挪四份地点谱里估的那一批坐标：
#   长垒照用户在 .map 里画的那一道（../参考/长垒_用户画.tsv，北头 1036,384，南头 944,972）
#     山铜纪那一份是照自己连的墙线放的：按在那条线上走了几成，挪到用户那道墙上同样的几成（分塌门南北两截），离墙的远近照留
#     最南头那道门往南的一串（南沼、三口泉、道头、圣土、擎天级）跟着墙的南头整块平移
#     纷争纪、前传落在墙上的段城、水门挪到墙线上最近那一点
#   灰雨城画在墙东（墙线往东 22 格）
#   赤原在墙南段西边、灰烬高原那一带
#   东陆北境照山铜纪那一份的框补上月银纪写了 ? 的几处
# 挪过的行在“要说明的”末尾记一句原来的坐标。用法：python -I -X utf8 挪坐标.py（在 底稿/地图/地点谱/ 下跑，跑完再跑 合表.py）
import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WALL = [tuple(map(float, l.split('\t'))) for l in open(os.path.join(HERE, '..', '参考', '长垒_用户画.tsv'), encoding='utf8').read().split('\n')[1:] if l.strip()]
SHAN_LINE = [(950, 420), (975, 500), (1003, 689), (1006, 705), (1021, 751), (1035, 830), (1065, 890), (1160, 1020)]


def cum(pl):
    out = [0.0]
    for a, b in zip(pl, pl[1:]):
        out.append(out[-1] + math.dist(a, b))
    return out


def project(pl, p):
    """最近点：返回 (沿线距离, 有符号的离线距离)"""
    cs = cum(pl)
    best = None
    for k, (a, b) in enumerate(zip(pl, pl[1:])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy or 1
        t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
        q = (a[0] + t * dx, a[1] + t * dy)
        d = math.dist(p, q)
        if best is None or d < best[0]:
            cross = dx * (p[1] - a[1]) - dy * (p[0] - a[0])
            best = (d, cs[k] + t * math.sqrt(L2), math.copysign(d, cross))
    return best[1], best[2]


def at(pl, s, off=0.0):
    cs = cum(pl)
    s = max(0, min(cs[-1], s))
    for k in range(len(pl) - 1):
        if cs[k + 1] >= s:
            a, b = pl[k], pl[k + 1]
            L = cs[k + 1] - cs[k] or 1
            t = (s - cs[k]) / L
            x, y = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
            nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
            return x + nx * off, y + ny * off
    return pl[-1]


def wall_x(y):
    for a, b in zip(WALL, WALL[1:]):
        if (a[1] - y) * (b[1] - y) <= 0 and a[1] != b[1]:
            return a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])
    return None


# 两条线各自在塌门那一点分成南北两截
TA = (1021, 751)
s_shan_ta, _ = project(SHAN_LINE, TA)
s_wall_ta, _ = project(WALL, TA)
L_shan, L_wall = cum(SHAN_LINE)[-1], cum(WALL)[-1]


def map_shan(p):
    s, off = project(SHAN_LINE, p)
    if s <= s_shan_ta:
        s2 = s / s_shan_ta * s_wall_ta
    else:
        s2 = s_wall_ta + (s - s_shan_ta) / (L_shan - s_shan_ta) * (L_wall - s_wall_ta)
    return at(WALL, s2, max(-25, min(25, off)))


SOUTH_GROUP = ['南沼', '东泉', '中泉', '西泉', '道头', '圣土', '擎天级']
WALL_KW = ['段城', '段起点', '四十七骑门', '水门', '七柱碑', '盾碑', '南七段', '白杉口', '白杉堡', '最南头那道门', '刀桥', '坛心岛', '九十三号', '麦棚村', '下堰村', '桥西村', '水磨村', '麦口村', '学院城', '堰口', '轰狱营', '墙后的大道', '神陨地']
NORTH_MOON = {'霜河': (1100, 512), '霜渡': (1088, 512), '红枝厅': (1095, 484), '跪牛坡': (1095, 470), '北境三座平顶的山': (1120, 462)}
HUIYU = (round(wall_x(784) + 22, 1), 784)
CHIYUAN = (800, 880)
moved = []


def note(r, x, y):
    r['要说明的'] = (r['要说明的'] + '；' if r['要说明的'] else '') + f'11-08 照五件挪过，原来 {x},{y}'


for era in ['月银纪', '纷争纪', '山铜纪', '迷宫纪前传']:
    p = os.path.join(HERE, era + '.tsv')
    rows = list(csv.DictReader(open(p, encoding='utf8'), delimiter='\t'))
    cols = list(rows[0].keys())
    for r in rows:
        try:
            x, y = float(r['地图x']), float(r['地图y'])
        except ValueError:
            x = y = None
        name = r['名字']
        new = None
        if era == '月银纪' and x is None and name in NORTH_MOON:
            new = NORTH_MOON[name]
        elif x is None:
            continue
        elif '灰雨城' in name and '遗址' not in name and '残响' not in name and abs(x - 968) < 2 and abs(y - 784) < 2:
            new = HUIYU
        elif era == '山铜纪' and name.startswith('往西的路') and abs(x - 968) < 2:
            new = HUIYU
        elif era == '纷争纪' and name == '赤原':
            new = CHIYUAN
        elif era == '山铜纪' and any(k in name for k in SOUTH_GROUP) and 1130 <= x <= 1180 and 1000 <= y <= 1060:
            new = (WALL[-1][0] + (x - 1160), WALL[-1][1] + (y - 1020))
        elif era == '山铜纪' and 930 <= x <= 1180 and 410 <= y <= 1030 and any(k in name for k in WALL_KW) and not (1085 <= x <= 1115 and y <= 512):
            s, off = project(SHAN_LINE, (x, y))
            if abs(off) <= 40:
                new = map_shan((x, y))
        elif era in ('纷争纪', '迷宫纪前传') and r['类'] == '段城' and 930 <= x <= 1180 and 380 <= y <= 1060:
            s, off = project(WALL, (x, y))
            new = at(WALL, s, 0)
        elif era == '迷宫纪前传' and name in ('南沼',):
            new = None
        if new is not None and (x is None or math.dist(new, (x, y)) > 1.5):
            note(r, r['地图x'], r['地图y'])
            r['地图x'], r['地图y'] = f'{new[0]:.0f}', f'{new[1]:.0f}'
            moved.append((era, name, (r['地图x'], r['地图y'])))
    # 前传的红炉段城、南沼跟山铜纪挪过的同一处
    if era == '迷宫纪前传':
        pass
    with open(p, 'w', encoding='utf8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

# 前传的红炉段城、南沼照山铜纪挪过的位置
shan = {r['名字']: r for r in csv.DictReader(open(os.path.join(HERE, '山铜纪.tsv'), encoding='utf8'), delimiter='\t')}
p = os.path.join(HERE, '迷宫纪前传.tsv')
rows = list(csv.DictReader(open(p, encoding='utf8'), delimiter='\t'))
cols = list(rows[0].keys())
for r in rows:
    for nm in ('红炉段城', '南沼'):
        if r['名字'] == nm and nm in shan:
            nx, ny = shan[nm]['地图x'], shan[nm]['地图y']
            if (r['地图x'], r['地图y']) != (nx, ny):
                note(r, r['地图x'], r['地图y'])
                r['地图x'], r['地图y'] = nx, ny
                moved.append(('迷宫纪前传', nm, (nx, ny)))
with open(p, 'w', encoding='utf8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols, delimiter='\t', lineterminator='\n')
    w.writeheader()
    w.writerows(rows)

print('灰雨城挪到', HUIYU, '墙在 784 的 x', round(wall_x(784), 1))
print('挪了', len(moved), '行')
for m in moved:
    print(' ', m)
