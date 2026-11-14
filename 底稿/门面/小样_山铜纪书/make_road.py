#!/usr/bin/env python3
# 路上的碑位表（data/road.json）：一块碑一个 z（沿着路往前的远近）和它立在哪儿（左右、高低），
# 再加几样跟着年份走的事：路照年份往前（每一页从哪儿到哪儿、年份怎么换算成 z），巴尔缇娜和索恩薇娅哪一年换哪一身，
# 头一回见面在哪儿，灰雨之夜路从哪儿分开，947 年两条路在哪儿合到塌门那道豁口。
#   python -I -X utf8 make_road.py        先跑 build_data.py；改了间距、换装年份，重跑这一支
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

S = 34            # 同一页里两块碑隔多远
LEAD = {1: 40, 4: 52}      # 一页开头到头一块碑：头一页要走出门洞，黎明的年月开头是灰雨之夜路分开的那一段
LEAD0 = 30
TAIL = 22         # 一页最后一块碑到下一页
END_GAP = 62      # 最后一块碑到塌门豁口（两条路在这里合到一处）
SPLIT_YEAR = 661  # 灰雨之夜：路从火里分开
MEET_YEAR = 607   # 废弃水闸那一回头一次见面（山铜纪第三页，三顿饭那一条）

# 碑立在哪儿（x 是离长垒当中线多远，墙西是负的；y 是碑脚的高度）。
# 灰雨以前路只有一条，在墙东边，墙在路左手：墙西的事立在墙脚，墙上的事贴着墙，墙东的事立在路右边。
# 灰雨以后墙在当中、两边各一条路：墙西的事立在左边那条路外侧，墙东的事立在右边那条路外侧（镜头在墙上方偏西，
# 右边那条路和墙之间那一溜地叫墙挡着），墙上的事立在墙脚：照碑文写的地方，在墙东的立在墙东墙脚，在墙西的立在墙西墙脚（WALL_FOOT，没写的立在墙西）。
# 原来立在墙头上，碑比墙还宽，像架在墙上，11-14 用户说怪，挪下来了。
LANES_BEFORE = {'west': ('墙脚', 2.3, 0.0), 'wall': ('贴着墙', 1.22, 0.0), 'east': ('路右边', 10.0, 0.0)}
LANES_AFTER = {'west': ('左边那条路旁', -10.6, 0.0), 'east': ('右边那条路旁', 10.6, 0.0)}
FOOT = {1: ('墙东墙脚', 2.7, 0.0), -1: ('墙西墙脚', -2.7, 0.0)}
WALL_FOOT = {'界碑': -1, '烧麦': -1}      # 刀桥段城墙脚往西一箭之地；燕巢段城南门往西一箭之地、界碑往南两步
# 11-14 碑照事件做成不同的样子，有大有小（stele_forms.json）。图在世界里多高照大小档和横竖（竖 2:3，横 3:2），宽跟着算；
# 离路多远照宽窄：灰雨以前路在墙东（路心 6，半宽 2.4），墙东的碑立在路右边外头，墙西和墙上的事立在墙和路当中那一溜（右边离路 0.3），
# 那一溜只有两步半宽，宽过 2.5 的收小；灰雨以后两条路在 ±7，碑立在各自那条路外头 0.8；灰雨之夜照碑文在灰雨城南门外的坡上，立东边那条路外头（★）。
FORMS = {k: v for k, v in json.load(open(os.path.join(HERE, 'stele_forms.json'), encoding='utf-8')).items() if not k.startswith('_')}
SIZE_H = {('s', 't'): 3.2, ('m', 't'): 4.6, ('l', 't'): 8.5, ('x', 't'): 13.0, ('s', 'w'): 2.0, ('m', 'w'): 3.0, ('l', 'w'): 5.0, ('x', 'w'): 8.0}
STRIP_W = 2.5      # 灰雨以前墙和路当中那一溜放得下多宽：墙面在 0.8，路边在 3.6，离路留 0.3


def dims(name, cap=None):
    f = FORMS[name]
    h = SIZE_H[(f['size'], f['o'])]
    w = h * (2 / 3 if f['o'] == 't' else 1.5)
    if cap and w > cap:
        h, w = h * cap / w, cap
    return round(w, 2), round(h, 2)

# 两个人照年份换的那一身（立牌的图在 comfy/out/门面_原画_山铜纪/ 的 w_bal_*、w_sor_*，立绘资料定的年份）
BAL = [[2, 'w_bal_1', '小时候'], [60, 'w_bal_2', '灰衣少女'], [661, 'w_bal_2b', '黑衣少女'], [742, 'w_bal_3', '成年']]
SOR = [[MEET_YEAR, 'w_sor_1', '少年兵'], [615, 'w_sor_2', '军官'], [668, 'w_sor_3', '白衣']]
HEIGHT = {'w_bal_1': 1.12, 'w_bal_2': 1.56, 'w_bal_2b': 1.56, 'w_bal_3': 1.68, 'w_sor_1': 1.70, 'w_sor_2': 1.74, 'w_sor_3': 1.74}


def main():
    D = json.load(open(os.path.join(HERE, 'data', 'bronze.json'), encoding='utf-8'))
    pages, steles, anchors = [], {}, []
    z = 0.0
    for e in D['eras']:
        no = e['no']
        lst = sorted(e['steles'], key=lambda s: (s['year'], s['name']))
        z0 = z
        anchors.append([round(z0, 2), e['y0']])
        zs = z0 + LEAD.get(no, LEAD0)
        for k, s in enumerate(lst):
            sz = zs + S * k
            after = s['year'] >= SPLIT_YEAR
            side = s['side']
            if after and side == 'wall' and s['name'] in WALL_FOOT:
                lane, x, y = FOOT[WALL_FOOT[s['name']]]
                w, h = dims(s['name'], cap=3.0)
            elif after:
                sd = 'west' if side == 'west' else 'east'
                w, h = dims(s['name'])
                lane = LANES_AFTER[sd][0] if side != 'wall' else '右边那条路外头的坡上'
                x, y = (-1 if sd == 'west' else 1) * round(7 + 2.4 + 0.8 + w / 2, 2), 0.0
            elif side == 'east':
                w, h = dims(s['name'])
                lane, x, y = LANES_BEFORE['east'][0], round(6 + 2.4 + 0.8 + w / 2, 2), 0.0
            else:
                w, h = dims(s['name'], cap=STRIP_W)
                lane, x, y = LANES_BEFORE[side][0], round(6 - 2.4 - 0.3 - w / 2, 2), 0.0
            steles[s['name']] = {'z': round(sz, 2), 'x': x, 'y': y, 'w': w, 'h': h, 'o': FORMS[s['name']]['o'], 'lane': lane, 'page': e['id'], 'year': s['year']}
            anchors.append([round(sz, 2), s['year']])
        last = zs + S * (len(lst) - 1)
        z1 = last + (END_GAP if no == len(D['eras']) else TAIL)
        pages.append({'id': e['id'], 'title': e['title'], 'z0': round(z0, 2), 'z1': round(z1, 2), 'y0': e['y0'], 'y1': e['y1']})
        z = z1
    zg = z                          # 塌门豁口：两条路合到这里，再往前地从豁口当中裂开
    anchors.append([round(zg, 2), D['eras'][-1]['y1']])
    end = D['end']
    ew, eh = dims(end['name'])
    steles[end['name']] = {'z': round(zg + 13, 2), 'x': 1.0, 'y': 0.0, 'w': ew, 'h': eh, 'o': FORMS[end['name']]['o'], 'lane': '缝边', 'page': D['eras'][-1]['id'], 'year': D['eras'][-1]['y1'], 'end': True}

    # 同一个 z 上年份重了的（同一年立的两块碑）往后挪一点点，换算的时候单调
    fixed = []
    for zz, yy in anchors:
        if fixed and yy < fixed[-1][1]:
            yy = fixed[-1][1]
        fixed.append([zz, yy])

    def z_of(year):
        for (za, ya), (zb, yb) in zip(fixed, fixed[1:]):
            if ya <= year <= yb and yb > ya:
                return round(za + (zb - za) * (year - ya) / (yb - ya), 2)
            if year == ya:
                return za
        return fixed[-1][0]
    split = [p for p in pages if p['y0'] == SPLIT_YEAR]
    road = {
        'note': '路上的碑位表。z 是沿着路往前的远近（米上下），x 是离长垒当中线多远（墙西是负的），y 是碑脚的高度。'
                '灰雨以前路只有一条，在墙东边，墙在路左手：墙西的事立在墙脚，墙上的事贴着墙，墙东的事立在路右边；'
                '灰雨以后墙在当中、两边各一条路：墙西的事立在左边那条路旁，墙东的事立在右边那条路旁，墙上的事照碑文立在墙东或墙西的墙脚。'
                'years 是年份和 z 的换算（一段一段直线插），bal、sor 是两个人照年份换的那一身。make_road.py 生成，改了重跑。',
        'pages': pages,
        'years': fixed,
        'split': {'year': SPLIT_YEAR, 'z': split[0]['z0'] if split else z_of(SPLIT_YEAR)},
        'meet': {'year': MEET_YEAR, 'z': z_of(MEET_YEAR)},
        'gap': {'year': D['eras'][-1]['y1'], 'z': round(zg, 2)},
        'bal': [[y, k, n, z_of(y), HEIGHT[k]] for y, k, n in BAL],
        'sor': [[y, k, n, z_of(y), HEIGHT[k]] for y, k, n in SOR],
        'steles': steles,
    }
    out = os.path.join(HERE, 'data', 'road.json')
    open(out, 'w', encoding='utf-8', newline='\n').write(json.dumps(road, ensure_ascii=False, indent=1) + '\n')
    for p in pages:
        print(p['id'], p['title'], p['z0'], '→', p['z1'], '年', p['y0'], '→', p['y1'])
    print('灰雨分路 z', road['split']['z'], '头一回见面 z', road['meet']['z'], '塌门 z', road['gap']['z'])
    print('巴尔缇娜', [(b[0], b[1], b[3]) for b in road['bal']])
    print('索恩薇娅', [(b[0], b[1], b[3]) for b in road['sor']])
    print('碑', len(steles), '块，写了', out)


if __name__ == '__main__':
    main()
