#!/usr/bin/env python3
# 门面剧情润色（11-21）：查交稿。
#   python -I -X utf8 底稿/门面/剧情润色/tools/check.py [纪 …]        查 底稿/门面/剧情润色/<纪>/*.json
#   python -I -X utf8 底稿/门面/剧情润色/tools/check.py --file X.json   只查一份
# 查：主线名对得上门面数据、幕数和幕的标签跟现在的幕行一一对上、标点禁词、长度、同一纪里幕名重复。
import glob
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
FRONT = os.path.join(ROOT, '底稿', '门面')
OUT = os.path.join(FRONT, '剧情润色')
BOOK = {'月银纪': ('小样_月银纪书', 'moon.json'), '纷争纪': ('小样_纷争纪书', 'strife.json'),
        '山铜纪': ('小样_山铜纪书', 'bronze.json'), '迷宫纪': ('小样_迷宫纪书', 'maze.json')}
sys.path.insert(0, os.path.join(ROOT, 'tools'))
BAN_P = ['——', '—', '；', '…', '！', '...', '!', ';', '：', ':', '｜', '「', '」', '~', '～']
BAN_W = ['学宫', '客栈', '朝廷', '门客', '时辰', '掌柜', '客官', '百官', '丫头', '宗门', '长老', '功法', '镖局',
         '一丝', '一抹', '不禁', '威压', '修为', '登记', '军令', '条例', '晋升',
         '新月', '满月', '残月', '月牙', '弦月', '月亮', '月光', '量子', '坐标', '频率', '能量', '系统',
         '龛', '灶', '长明灯', '仪轨', '会盟', '诸侯', '城主', '诏书', '学塾', '驿卒', '官道', '佃户', '师门', '长衫', '庄子',
         '伙计', '街坊', '太爷爷', '卖饼', '爹', '娘亲', '俺', '啥', '甭', '晌午', '汉子', '后生', '媳妇', '闺女', '江湖', '武功',
         '内力', '银子', '铜钱', '磕头', '师父', '徒弟', '剑客', '米色', '米白', '茶色', '营寨', '营帐', '军帐',
         '玩家', 'AI', '厄洛伽', '★', '（', '）', '(', ')']
# 娘：新娘、姑娘照留
NIANG = re.compile(r'(?<![新姑])娘')
# 11-21 第五稿：数至多一处（幕名一条主线至多一个带数的；介绍、每句描述至多一处）
NUM = re.compile(r'[0-9]+|第[零一二三四五六七八九十百千万两]+|(?<![几两二三四五六七八九十百千万])[两二三四五六七八九十百千万]+[个次道年天夜人座枚块根条只张层回步句声件匹头支份家具杯碗户袋里斤列台下行]')


def load_book(ji):
    d, f = BOOK[ji]
    D = json.load(open(os.path.join(FRONT, d, 'data', f), encoding='utf-8'))
    return {e['id']: {l['name']: l for l in e.get('lines', [])} for e in D['eras']}


def check_text(where, t, probs):
    for p in BAN_P:
        if p in t:
            probs.append('%s 标点 %s｜%s' % (where, p, t))
    for w in BAN_W:
        if w in t:
            probs.append('%s 禁词 %s｜%s' % (where, w, t))
    if NIANG.search(t):
        probs.append('%s 禁词 娘｜%s' % (where, t))
    if '"' in t or "'" in t:
        probs.append('%s 半角引号｜%s' % (where, t))
    if t.count('“') != t.count('”'):
        probs.append('%s 引号不成对｜%s' % (where, t))


def tag_of(a):
    return a.split('｜', 1)[0]


def check_file(ji, fp, eras, names_seen, probs):
    eid = os.path.basename(fp)[:-5]
    try:
        J = json.load(open(fp, encoding='utf-8'))
    except Exception as ex:
        probs.append('%s 读不了 %s' % (fp, ex))
        return 0
    lines = eras.get(eid)
    if lines is None:
        probs.append('%s 没有这个时代 %s' % (fp, eid))
        return 0
    for nm in lines:
        if nm not in J:
            probs.append('%s 缺主线 %s' % (eid, nm))
    n = 0
    for nm, v in J.items():
        if nm not in lines:
            probs.append('%s 多出来的主线名 %s' % (eid, nm))
            continue
        n += 1
        l = lines[nm]
        w = '%s %s' % (eid, nm)
        intro = v.get('intro', '')
        if not intro:
            probs.append('%s 没有介绍' % w)
        check_text(w + ' 介绍', intro, probs)
        k = len(re.findall(r'[一-鿿]', intro))
        if not 35 <= k <= 140:
            probs.append('%s 介绍 %d 字（35 到 140）' % (w, k))
        if len(NUM.findall(intro)) > 1:
            probs.append('%s 介绍里的数 %d 处（至多一处）｜%s' % (w, len(NUM.findall(intro)), '、'.join(NUM.findall(intro))))
        nn = [a.get('name', '') for a in v.get('acts', []) if NUM.search(a.get('name', ''))]
        if len(nn) > 1:
            probs.append('%s 带数的幕名 %d 个（至多一个）｜%s' % (w, len(nn), '、'.join(nn)))
        if 'task' in v:
            if not l.get('task'):
                probs.append('%s 月银纪、纷争纪不改题' % w)
            check_text(w + ' 任务名', v['task'], probs)
        want = [tag_of(a) for a in l.get('acts', [])]
        got = v.get('acts', [])
        if [a.get('tag') for a in got] != want:
            probs.append('%s 幕的标签对不上｜要 %s｜交的 %s' % (w, want, [a.get('tag') for a in got]))
        for a in got:
            an, ad = a.get('name', ''), a.get('desc', '')
            check_text('%s %s 幕名' % (w, a.get('tag')), an, probs)
            check_text('%s %s 描述' % (w, a.get('tag')), ad, probs)
            if re.search(r'[。]$', an):
                probs.append('%s %s 幕名不收句号｜%s' % (w, a.get('tag'), an))
            k = len(re.findall(r'[一-鿿0-9]', an))
            if not 2 <= k <= 16:
                probs.append('%s %s 幕名 %d 字（2 到 16）｜%s' % (w, a.get('tag'), k, an))
            k = len(re.findall(r'[一-鿿]', ad))
            if not 10 <= k <= 75:
                probs.append('%s %s 描述 %d 字（10 到 75）｜%s' % (w, a.get('tag'), k, ad))
            if len(NUM.findall(ad)) > 1:
                probs.append('%s %s 描述里的数 %d 处（至多一处）｜%s' % (w, a.get('tag'), len(NUM.findall(ad)), ad))
            if an in names_seen:
                probs.append('%s %s 幕名跟 %s 重了｜%s' % (w, a.get('tag'), names_seen[an], an))
            names_seen.setdefault(an, w)
    return n


def main():
    probs = []
    if len(sys.argv) > 2 and sys.argv[1] == '--file':
        fp = os.path.abspath(sys.argv[2])
        ji = os.path.basename(os.path.dirname(fp))
        n = check_file(ji, fp, load_book(ji), {}, probs)
        print('%s %d 条' % (fp, n))
    else:
        for ji in (sys.argv[1:] or list(BOOK)):
            eras = load_book(ji)
            seen, tot = {}, 0
            fs = sorted(glob.glob(os.path.join(OUT, ji, '*.json')))
            for fp in fs:
                tot += check_file(ji, fp, eras, seen, probs)
            print('%s %d 份 %d 条（全纪 %d 条）' % (ji, len(fs), tot, sum(len(v) for v in eras.values())))
    for p in probs:
        print(p)
    print('问题 %d' % len(probs))


if __name__ == '__main__':
    main()
