# 11-10 基本算式（用户回“甲，其余也都按倾向来”）：四纪主要地点的条目添一块「从这里出发」，只给 AI。
# 照命定之诗那张卡的做法（照当前地点取一跳的地方，带走法、天数和方向），日里不跑脚本，打包时照地点谱坐标算好写进条目，地点格写到哪一处、哪一处的条目醒。
# 地点谱 底稿/地图/地点谱/合表.tsv：统一主次是「主要」的、类是城镇港塔这一路的才添；出处里头一个对得上的条目名就是它的条目。
# 一处添最近的五处主要地点（同一纪），走路和骑马几天、往哪个方向；有车、浮舟的年月照那一纪的路程条目。
import csv
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '算式'))
import route_tables as R   # noqa: E402

KINDS = ('巨城', '城', '城邦', '港', '段城', '营城')   # 镇、村、塔、遗迹在图上多半是照文里的天数摆的，不算
MIN_UNITS = 40      # 离得比这近的（不到一个半月的路）当地区里头的，照村镇城的格子和文里写的，不列
CITY_STEMS = ('金鸢', '阿卡迪亚', '星环', '烬灭', '星冠', '银湖', '露玫', '高岚', '炉心', '七芒')
CITY_MAIN = {'晨曦帝都·金鸢城', '迷宫都市·阿卡迪亚', '阿卡迪亚大迷宫', '星环魔导都市', '烬灭之都', '星冠圣城', '月镜王都·银湖城', '蔷薇王都·露玫城', '风铃王都·高岚城', '熔铁炉心'}
SUB_EXTRA = {'曜石审判庭'}   # 金鸢城东北的台地，图上画开了


def _sub_landmarks():
    """1001 年地标里画在巨城边上的城里地标（工坊区、钟楼、总塔这一类），图上画开了，不拿来算距离"""
    out = set(SUB_EXTRA)
    for r in csv.DictReader(open(os.path.join(ROOT, '底稿/地图/参考/1001年地标.tsv'), encoding='utf-8'), delimiter='	'):
        n = r['名字']
        if n not in CITY_MAIN and any(s in n for s in CITY_STEMS):
            out.add(n)
    return out
PLACE_TITLE = re.compile(r'(?:·(?:地点|城邦|城区|遗迹|险地|迷宫|据点|迷宫城)｜|（(?:月银纪|纷争纪|山铜纪|迷宫纪)）$)')
HEAD = '**从这里出发，只给 AI。** 最近的几处大地方，走路和骑马照地图算好了，路况、天气、走法档和路上的耽搁照这一纪的路程那一条乘上去，有车、浮舟、空艇的年月也照那一条。这些地方哪一年才有照它们自己的条目，近处的村镇照村镇城的格子。'


def _year_note(s):
    m = re.match(r'^(?:[^0-9，。（]{0,8})?(\d{2,5})年', s)
    if m and not re.match(r'^(?:月银纪|纷争纪|山铜纪|迷宫纪)?全', s):
        return '（%s年前后起）' % m.group(1)
    return ''


def blocks():
    SUB = _sub_landmarks()
    rows = [r for r in csv.DictReader(open(os.path.join(ROOT, '底稿/地图/地点谱/合表.tsv'), encoding='utf-8'), delimiter='\t')
            if r['统一主次'] == '主要' and r['类'] in KINDS and r['对上的1001地标'] not in SUB]
    by_era = {}
    for r in rows:
        try:
            xy = (float(r['地图x']), float(r['地图y']))
        except ValueError:
            continue
        by_era.setdefault(r['纪'], []).append((r, xy))
    out = []
    for era, lst in by_era.items():
        for r, xy in lst:
            near = sorted(((math.hypot(xy[0] - o[0], xy[1] - o[1]), o2['名字'], o, o2) for o2, o in lst if o2['名字'] != r['名字']), key=lambda x: x[0])
            lines = []
            for d, name, o, o2 in near:
                if d < MIN_UNITS:
                    continue
                km = d * R.KM
                walk = km * 1.25 / 30
                lines.append('- 到%s｜往%s｜走路%s，骑马%s' % (re.sub(r'（.*?）', '', name), R.direction(xy, o), R.say(walk), R.say(walk / 2)))
                if len(lines) == 5:
                    break
            cands = [s.strip() for s in r['出处'].split('、') if s.strip()]
            out.append((era, r['名字'], cands, '%s\n%s' % (HEAD, '\n'.join(lines))))
    return out


def apply(lb, start):
    """lb[start:] 里找条目，照出处的先后认头一个对得上的条目名；一条条目只添一块"""
    titles = {}
    for i in range(start, len(lb)):
        first = (lb[i].get('content') or '').split('\n', 1)[0]
        m = re.match(r'^#{1,2} (.+)$', first)
        if m:
            titles.setdefault(m.group(1).strip(), i)
    done, miss = {}, []
    for era, name, cands, blk in blocks():
        hit = None
        for s in cands:
            if s in titles and (PLACE_TITLE.search(s) or re.sub(r'（.*?）', '', name) in s):
                hit = titles[s]
                break
        if hit is None:
            miss.append((era, name))
            continue
        if hit in done:
            continue
        c = lb[hit]['content']
        k = max(c.find('\n### 裁定锁'), c.find('\n## 裁定锁'))
        k2 = [x for x in (c.find('\n### 裁定锁'), c.find('\n## 裁定锁')) if x > 0]
        if k2:
            k = min(k2)
            lb[hit]['content'] = c[:k].rstrip() + '\n\n' + blk + '\n' + c[k:]
        else:
            lb[hit]['content'] = c.rstrip() + '\n\n' + blk + '\n'
        done[hit] = (era, name)
    return len(done), miss
