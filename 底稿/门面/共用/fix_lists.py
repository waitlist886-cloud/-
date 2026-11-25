#!/usr/bin/env python3
# 书的名单上要手改的几处（11-15 拼装那一轮）。各本 build_data.py 重跑以后都要再跑这一支（它认得改过的，重跑不出错）：
#   python -I -X utf8 底稿/门面/共用/fix_lists.py [strife bronze maze]
#   1. 藏着的身份：时代页的名单上直接显示 race 和 who，源稿里写着旁人不知道的那几位（化成人形的真龙、藏着的混血），
#      race 写成“…（藏着）”（页面的 raceShow 见了“藏”就不显示），who 换成旁人看得见的那一句。
#   2. 迷宫纪那一本抽歪了的名字：人物条里“- 名｜…”的小条有的写的是“是谁”“什么样”，抽成了人名；有的只抽到职务。改成认得出的叫法，重了的、不是人的拿掉。
# 改三处：小样_<纪>书/data/<书>.json 的 cast、meet，data/prof/<时代>.json 的键，底稿/门面/卡片/<纪>/<时代>.json 的 people 的键。
# 改完跑 共用/prep_cards.py 重出 data/cards.json。
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.normpath(os.path.join(HERE, '..'))
BOOK = {'strife': ('小样_纷争纪书', '纷争纪'), 'bronze': ('小样_山铜纪书', '山铜纪'), 'maze': ('小样_迷宫纪书', '迷宫纪')}
FIX = {
    'strife': {
        's07': {'恩雅': {'race': '真龙（藏着）', 'who': '墙梯口那个灰白头发的高个子女人，空着两只手，一个人扛一整块条石上墙。'}},
    },
    'bronze': {
        'p4': {'桑娜': {'race': '混血（藏着）', 'who': '桑娜，打个结就能感到近处亲人的少女。648年生在灰雨城工匠街尽头那座长屋后头。'}},
        'p5': {'桑娜': {'race': '混血（藏着）', 'who': '桑娜，打个结就能感到近处亲人的绳匠。'},
               '苏薇': {'race': '真龙（藏着）', 'who': '苏薇，斩龙者团里戴旧毡帽的高个子女人。'}},
    },
    'maze': {
        'q1': {'七个是谁': {'name': '封井那几天的七个人'}, '妇人': {'name': '织麻的妇人'}, '公会头一个书记': {'name': '卡塔琳娜·林德纳', 'tag': '公会头一个书记'},
               '费迪南德': {'name': '费迪南德·福格特'}, '豪克': {'name': '豪克·布赫'}},
        'q2': {'署长': {'name': '造币署的署长'}, '夜翼斥候': {'name': '夜不归的斥候'}},
        'q3': {'王': {'name': '德瑞昂·擎灯', 'tag': '无光王庭的王'}, '另外四个': {'name': '守塔的另外四个'}, '静林旬': {'drop': True}, '林市': {'drop': True},
               '那一巡': {'name': '外林守望军那一巡'}, '营官': {'name': '西坡的营官'}, '林老': {'name': '七位林老'}},
        'q4': {'阿蕾缇娅·尼伯莱茵': {'race': '真龙（藏着）', 'who': '上环苦叶汤小店里的常客，问她打哪儿来，她说山上。'},
               '地图室': {'name': '测绘局的地图室'}, '另外六个': {'name': '白昼尽头的另外六个'}, '苍麦': {'name': '伊曼纽·苍麦'}, '鹰巢': {'name': '雅尔玛·鹰巢'},
               '糖罐': {'name': '账房门口的糖罐'}, '崽子': {'name': '市集上的崽子'}},
        'q5': {'传奇': {'name': '还在世的传奇'}, '食堂': {'name': '公会的食堂'}, '副官': {'name': '杜娜·考夫曼', 'tag': '莱恩哈特的副官'},
               '营长': {'name': '灰斗篷的营长'}, '小侍从': {'name': '端水的小侍从'}},
        'q6': {'什么样': {'name': '露希亚', 'tag': ''}, '营里': {'name': '第五十层前沿的营'}, '法丽达': {'drop': True}},
    },
}


def load(p):
    return json.load(open(p, encoding='utf-8'))


def dump(p, d, compact=True):
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        if compact:
            json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
        else:
            json.dump(d, f, ensure_ascii=False, indent=1)


def rekey(d, old, new):
    """字典里把键 old 换成 new，次序不动"""
    return {(new if k == old else k): v for k, v in d.items()}


def main():
    todo = [a for a in sys.argv[1:] if a in BOOK] or list(BOOK)
    for b in todo:
        folder, ji = BOOK[b]
        base = os.path.join(FRONT, folder, 'data')
        dp = os.path.join(base, b + '.json')
        D = load(dp)
        eras = D['eras'] if isinstance(D, dict) and 'eras' in D else D
        n = 0
        for e in eras:
            fx = FIX.get(b, {}).get(e['id'])
            if not fx:
                continue
            pp = os.path.join(base, 'prof', e['id'] + '.json')
            P = load(pp) if os.path.exists(pp) else {}
            cp = os.path.join(FRONT, '卡片', ji, e['id'] + '.json')
            C = load(cp) if os.path.exists(cp) else None
            have = {c['name'] for g in ('cast', 'meet') for c in e.get(g, [])}
            for old, f in fx.items():
                new = f.get('name')
                drop = f.get('drop') or (new and new != old and new in have)      # 改成的名字名单上已经有了：这一条就是重的，拿掉
                for g in ('cast', 'meet'):
                    lst = e.get(g, [])
                    for c in list(lst):
                        if c['name'] != old:
                            continue
                        if drop:
                            lst.remove(c)
                        else:
                            for k in ('race', 'who', 'tag'):
                                if k in f:
                                    c[k] = f[k]
                            if new:
                                c['name'] = new
                        n += 1
                if drop:
                    P.pop(old, None)
                    if C:
                        C['people'].pop(old, None)
                elif new and new != old:
                    if old in P:
                        P = rekey(P, old, new)
                    if C and old in C['people']:
                        C['people'] = rekey(C['people'], old, new)
                    have.discard(old)
                    have.add(new)
            if os.path.exists(pp):
                dump(pp, P)
            if C is not None:
                dump(cp, C, compact=False)
        dump(dp, D)
        print(ji, '名单上改了', n, '处')


if __name__ == '__main__':
    main()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import cast_map             # 11-22：认不上立绘的人照 data/cast_map.json 挂键，名字要用这一支改过以后的，所以接在后头、四本都过
    cast_map.apply()
