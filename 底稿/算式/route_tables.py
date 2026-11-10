# 各纪路程条目里「大地方之间」那张表（11-10 基本算式）：照地点谱坐标（一格十九公里，路比直线绕两成五，车和船另算）出卡面的说法。
# 用法（仓库根上）：python -I -X utf8 底稿/算式/route_tables.py 纪
import csv
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KM = 19.0
CN = '零一两三四五六七八九十'
DIR = ['东', '东南', '南', '西南', '西', '西北', '北', '东北']


def load(era):
    out = {}
    for r in csv.DictReader(open(os.path.join(ROOT, '底稿/地图/地点谱/合表.tsv'), encoding='utf-8'), delimiter='\t'):
        if r['纪'] != era:
            continue
        try:
            out[r['名字']] = (float(r['地图x']), float(r['地图y']))
        except ValueError:
            pass
    return out


def say(t):
    """天数说成卡面上的话：一天以内说钟时，十天以内说几天，往上说一旬、半个月、几个月、几年"""
    if t < 0.75:
        h = max(1, int(round(t * 24)))
        return '%s个钟时' % (CN[h] if h <= 10 else '十几' if h < 15 else '大半天') if h < 18 else '一天'
    if t < 1.3:
        return '一天'
    if t < 1.75:
        return '一天半'
    if t < 10.5:
        return CN[int(round(t))] + '天'
    if t < 13:
        return '十来天'
    if t < 18:
        return '半个月'
    if t < 25:
        return '二十来天'
    if t < 37:
        return '一个月'
    if t < 50:
        return '一个半月'
    m = t / 30
    if m < 11.75:
        h = round(m * 2) / 2
        w = int(h)
        return '%s个%s月' % (CN[w] if w <= 10 else '十一', '半' if h - w else '')
    y = t / 360
    if y < 1.25:
        return '一年上下'
    if y < 1.75:
        return '一年半'
    if y < 2.25:
        return '两年'
    if y < 2.75:
        return '两年半'
    return '%s年' % CN[int(round(y))]


def direction(a, b):
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return DIR[int(((ang + 22.5) % 360) // 45)]


def row(P, a, b, modes, label=None):
    """modes：[(名字, 一天顶走路几天, 路比直线绕几倍)]"""
    d = math.hypot(P[a][0] - P[b][0], P[a][1] - P[b][1]) * KM
    walk = d * 1.25 / 30
    cells = []
    for name, mult, detour in modes:
        days = d * detour / 30 / mult
        cells.append('%s%s' % (name, say(days)))
    return '- %s到%s｜往%s｜%s' % (label[0] if label else a, label[1] if label else b, direction(P[a], P[b]), '，'.join(cells)), walk


if __name__ == '__main__':
    era = sys.argv[1]
    P = load(era)
    for k in sorted(P):
        print(k, P[k])
