# 路程表试算：照 底稿/地图/地点谱/合表.tsv 的坐标（一格十九公里），算一纪几处大地方之间和一处地方周边的走法天数。
# 用法（仓库根上）：python -I -X utf8 底稿/算式/hubgen.py .
import csv
import math
import sys

ROOT = sys.argv[1]
KM = 19.0
rows = list(csv.DictReader(open(ROOT + '/底稿/地图/地点谱/合表.tsv', encoding='utf-8'), delimiter='\t'))


def pts(era):
    out = {}
    for r in rows:
        if r['纪'] != era:
            continue
        try:
            out[r['名字']] = (float(r['地图x']), float(r['地图y']), r['类'], r['统一主次'], r['时段与年份'])
        except ValueError:
            pass
    return out


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1]) * KM


DIR = ['东', '东南', '南', '西南', '西', '西北', '北', '东北']


def direction(a, b):
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))  # y 往下是南
    return DIR[int(((ang + 22.5) % 360) // 45)]


CN = '零一两三四五六七八九十'


def days_txt(t):
    if t < 0.75:
        h = max(1, round(t * 24))
        return '%d个钟时' % h if h < 18 else '一天'
    if t < 1.25:
        return '一天'
    if t < 10.5:
        n = round(t)
        return CN[n] + '天'
    if t < 25:
        return '%s天上下' % ('十几' if t < 17 else '二十来')
    if t < 50:
        return '一个多月' if t < 40 else '一个半月'
    m = t / 30
    if m < 11.5:
        halves = round(m * 2) / 2
        whole = int(halves)
        s = (CN[whole] if whole <= 10 else '十一') + '个月'
        if halves - whole:
            s = (CN[whole] if whole <= 10 else '十一') + '个半月'
        return s.replace('两个月', '两个月')
    y = t / 360
    if y < 1.3:
        return '一年上下'
    if y < 1.75:
        return '一年半'
    if y < 2.4:
        return '两年'
    return '%d年' % round(y)


SPEED = {'走路': (30, 1.25), '骑马': (55, 1.25), '驿马': (130, 1.25), '星纱轨': (1100, 1.2)}

if __name__ == '__main__':
    P = pts('山铜纪')
    hubs = ['金鸢城', '星冠圣城', '炉城', '银湖城', '高岚城', '露玫城', '白鸢骑士城', '金穗王仓城', '银帆', '星环', '灰雨城', '水门段城', '鹰石段城', '石鼓段城', '烬灭之都', '骸钟墓城', '苍焰角城', '血棘红园', '魇镜幻都', '黑翼天塔', '雷狱铁城', '潮门']
    for h in hubs:
        assert h in P, h
    pairs = [('金鸢城', '星冠圣城'), ('金鸢城', '白鸢骑士城'), ('金鸢城', '金穗王仓城'), ('金鸢城', '炉城'), ('金鸢城', '银湖城'), ('金鸢城', '高岚城'),
             ('金鸢城', '露玫城'), ('金鸢城', '银帆'), ('金鸢城', '水门段城'), ('金鸢城', '鹰石段城'), ('金鸢城', '石鼓段城'), ('星冠圣城', '星环'),
             ('鹰石段城', '石鼓段城'), ('水门段城', '灰雨城'), ('水门段城', '烬灭之都'), ('烬灭之都', '苍焰角城'), ('烬灭之都', '血棘红园'), ('烬灭之都', '骸钟墓城'),
             ('烬灭之都', '魇镜幻都'), ('烬灭之都', '雷狱铁城'), ('烬灭之都', '潮门'), ('烬灭之都', '黑翼天塔'), ('金鸢城', '烬灭之都')]
    rail = {'金鸢城', '星环', '水门段城', '鹰石段城', '石鼓段城', '灰雨城'}
    for a, b in pairs:
        d = dist(P[a], P[b])
        cells = []
        for m in ('走路', '骑马', '驿马'):
            v, f = SPEED[m]
            cells.append('%s%s' % (m, days_txt(d * f / v)))
        if a in rail and b in rail:
            v, f = SPEED['星纱轨']
            cells.append('车%s' % days_txt(d * f / v))
        print('%s→%s｜%s｜%d公里｜%s' % (a, b, direction(P[a], P[b]), d, '｜'.join(cells)))
    print()
    # 一处地方周边：灰雨城 600 年前后，最近的八处
    for c in ('灰雨城', '金鸢城'):
        me = P[c]
        near = sorted(((dist(me, v), k) for k, v in P.items() if k != c), key=lambda x: x[0])[:8]
        print('==', c)
        for d, k in near:
            print('  %s｜%s｜%d公里｜走路%s｜骑马%s' % (k[:14], direction(me, P[k]), d, days_txt(d * 1.25 / 30), days_txt(d * 1.25 / 55)))
