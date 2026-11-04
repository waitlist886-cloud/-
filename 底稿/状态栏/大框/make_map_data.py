#!/usr/bin/env python3
# 地图页的数据：从底卡介绍页抄（landmarkData、AUL_MARKERS、AUL_PROSE、AUL_PAINT、AUL_ART），写 map_data.json。规则和样式都读这一份。
# 用法（仓库根上）：python -I -X utf8 底稿/状态栏/大框/make_map_data.py
# 认玩家在哪：显示层拿 §底座 的地点字串比 keys（样式的 [data-loc*="X"]），样式里后写的盖先写的，所以这里排好先后，泛的在前、细的在后。
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
t = json.load(open(os.path.join(ROOT, 'src', 'rili_v7.json'), encoding='utf-8'))['introPage']
dec = json.JSONDecoder()


def grab(name):
    i = t.index(name + '=') + len(name) + 1
    return dec.raw_decode(t[i:])[0]


lands = grab('landmarkData')
marks = grab('AUL_MARKERS')
prose = grab('AUL_PROSE')
paint = grab('AUL_PAINT')
art = grab('AUL_ART')
img = re.search(r'id="mp-img" src="([^"]+)"', t).group(1)
ratio = re.search(r'MP_RATIO=(\d+)/(\d+)', t)


# 介绍页 mpZone、mpMajor 照抄
def zone(l):
    c, s = l.get('cls', ''), l.get('region', '') + ' ' + l.get('name', '')
    if re.search('dungeon|town', c):
        return 'town'
    if re.search('water|river|mountain|natural|route|rail', c):
        return 'geo'
    if re.search('极北|化圣|北极|南极|终北|神陨|沙海|大漠|葬火|封印带|极地', s):
        return 'polar'
    if re.search('原初之森|精灵|矮人|龙眠|霜眠|曜冠|熔铁|碧穹|翠冠|龙脊|龙裔|高天|世界树', s):
        return 'old'
    if re.search('黑耀|烬灭|红莲|渊月|黑曜|西陆|西海|雷狱|赤棘|黯潮|裂影', s):
        return 'west'
    if re.search('晨曦|联邦|王国|曙辉|星冠|月镜|风铃|蔷薇|苍麦|蜜酒|星环|雾镜|金鸢|银镜|风啸|风鸣|白银海|东陆|公国|学院区', s):
        return 'east'
    return 'center'


# 标名字从多大的倍数起露出来：大城和迷宫城全图就露，城 2 倍起，别的细看才露
def tier(l):
    c = l.get('cls', '')
    if re.search('core|capital|dungeon', c):
        return 0
    if re.search('federation|empire-city|holy|academy|port|frontier|fortress|polar', c):
        return 1.5
    return 3


# 手写的别名：玩家嘴里、AI 写地点时常用的叫法（泛的放 low，先写，别的地名一中就盖过它）
LOW = {
    '阿卡迪亚大迷宫': ['大迷宫', '迷宫入口', '浅层', '安全层', '楼层主'],
    '晨曦帝都·金鸢城': ['晨曦帝国', '晨曦帝都', '王道平原'],
    '烬灭之都': ['黑耀帝国', '黑耀帝都', '红莲'],
    '蔷薇王都·露玫城': ['蔷薇王国', '蔷薇王都'],
    '月镜王都·银湖城': ['月镜王国', '月镜王都'],
    '风铃王都·高岚城': ['风铃王国', '风铃王都'],
    '原初之森·碧穹王庭': ['原初之森', '精灵王庭'],
    '星冠圣城': ['星冠', '圣堂'],
    '熔铁炉心': ['矮人王国', '炉城'],
    '白碑长垒': ['长垒'],
    '迷宫都市·阿卡迪亚': ['阿卡迪亚', '迷宫都市', '大迷宫之城'],
}
HIGH = {
    '阿卡迪亚大迷宫': ['大迷宫·第', '大迷宫第', '阿卡迪亚大迷宫', '阿卡迪亚·大迷宫'],
    '蜜酒丘陵与铃尾市集': ['蜜酒丘陵', '铃尾市集'],
    '黑耀帝国自然科学与工程研究院': ['黑耀研究院', '工程研究院'],
    '阿卡迪亚公会以太钟楼': ['以太钟楼'],
    '渊月列车总枢纽': ['渊月列车'],
    '星纱列车东陆总枢纽': ['星纱列车'],
    '白石长垒城防机关阵': ['城防机关阵'],
    '晨曦金鸢工坊区': ['金鸢工坊'],
    '帝国电械义肢医院': ['义肢医院'],
    '银镜湖占星塔群': ['占星塔'],
    '星环奥法总塔': ['奥法总塔'],
    '元素晶匣工坊镇': ['晶匣工坊'],
    '圣堂净化封印院': ['净化封印院'],
    '葛摩恩碎碑矿坑': ['碎碑矿坑'],
    '星坠冒险者学院': ['星坠学院'],
    '翠冠树海迷宫城': ['树海迷宫城'],
    '镜湖未竟城': ['未竟城'],
    '黑潮螺旋城': ['螺旋城'],
    '曜冠空环城': ['空环城'],
    '灰雨城遗址': ['灰雨城'],
}
GENERIC = {'晨曦帝都', '蔷薇王都', '月镜王都', '风铃王都', '迷宫都市', '原初之森', '阿卡迪亚大迷宫'}
# 先后：山川水系最泛，城居中，镇子、设施、迷宫城最细
ORDER = {'water': 1, 'river': 1, 'mountain': 1, 'natural': 1, 'route': 2, 'rail': 2, 'polar': 2, 'frontier': 3, 'federation': 4, 'federation-capital': 4, 'empire-capital': 4, 'empire-city': 5,
         'capital': 4, 'core': 3, 'holy': 5, 'academy': 5, 'port': 5, 'fortress': 5, 'research': 6, 'tech': 6, 'resort': 6, 'town': 7, 'dungeon': 7}

out = []
for l in lands:
    n = l['name']
    x, y = marks.get(n, [l['x'], l['y']])
    parts = paint.get(n) or []
    url = art.get(n + '|' + parts[0]['part'], '') if parts else ''
    keys = [n] + [p for p in n.split('·') if p not in GENERIC]
    out.append({
        'n': n, 'x': round(x, 2), 'y': round(y, 2), 'z': zone(l), 't': tier(l),
        'r': l.get('region', ''), 'lv': (l.get('levelRange') or '').split('｜')[0],
        'd': prose.get(n) or l.get('climate') or l.get('location') or '',
        'art': url, 'o': ORDER.get(l.get('cls', ''), 4),
        'low': LOW.get(n, []), 'keys': list(dict.fromkeys(keys)), 'high': HIGH.get(n, []),
    })
data = {'img': img, 'ratio': [int(ratio.group(1)), int(ratio.group(2))], 'lands': out}
json.dump(data, open(os.path.join(HERE, 'map_data.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(out), '地标', sum(len(o['d']) for o in out), '字说明', sum(1 for o in out if o['art']), '张图', img, data['ratio'])
print('说明最长', max(len(o['d']) for o in out), '没有说明的', [o['n'] for o in out if not o['d']][:8])
