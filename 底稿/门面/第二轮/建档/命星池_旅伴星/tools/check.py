#!/usr/bin/env python3
# 查交稿：python -I -X utf8 tools/check.py <份名>（moon_a、strife_b……），不带参数查全部交了的。
# 每一颗要对上材料（名字、类、阶一个不差，一颗不漏），desc 照规矩，标点禁词月相字作者记号都是 0。
import importlib.util
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(WORK, '..', '..', '..', '..', '..'))
spec = importlib.util.spec_from_file_location('cp', os.path.join(ROOT, 'tools', 'check_people_v7.py'))
src = open(os.path.join(ROOT, 'tools', 'check_people_v7.py'), encoding='utf-8').read()
BAN_P = eval(re.search(r'^BAN_P = (\[.*?\])', src, re.M).group(1))
BAN_W = eval(re.search(r'^BAN_W = (\[.*?\])', src, re.M | re.S).group(1))
MOON = ['新月', '满月', '残月', '月牙', '弦月', '月亮', '月光']
TECH = ['量子', '熵', '坐标', '频率', '能量', '系统']
MARK = ['★', '【调用】', '这一页', '那一页', '第一歌', '本页']
NAMES = re.compile(r'[A-Za-z]{3,}')


def check(part):
    mat = json.load(open(os.path.join(WORK, '材料', part + '.json'), encoding='utf-8'))
    p = os.path.join(WORK, '交稿', part + '.json')
    if not os.path.exists(p):
        return None
    got = json.load(open(p, encoding='utf-8'))
    bad = []
    by = {g.get('name'): g for g in got}
    if len(got) != len(mat):
        bad.append('条数 %d，材料 %d' % (len(got), len(mat)))
    for m in mat:
        g = by.get(m['name'])
        if not g:
            bad.append('漏了 ' + m['name'])
            continue
        if g.get('type') != m['type']:
            bad.append('%s 类不对' % m['name'])
        if not isinstance(g.get('keep'), bool):
            bad.append('%s 没写 keep' % m['name'])
            continue
        if not g['keep']:
            if not g.get('why'):
                bad.append('%s 不收却没写 why' % m['name'])
            continue
        if g.get('tier') not in ('Normal', 'Rare', 'Epic', 'Legend'):
            bad.append('%s 阶 %s' % (m['name'], g.get('tier')))
        d = g.get('desc') or ''
        if not d.startswith(m['type'] + '。'):
            bad.append('%s desc 开头要写“%s。”' % (m['name'], m['type']))
        n = len(re.sub(r'[\sA-Za-z0-9%+/×.:]', '', d))
        if n < 50 or n > 230:
            bad.append('%s desc %d 字' % (m['name'], n))
        for w in BAN_P + BAN_W + MOON + TECH + MARK:
            if w in d or w in (g.get('note') or ''):
                bad.append('%s 带了“%s”' % (m['name'], w))
        le = g.get('last_era')
        if le is not None and le not in ('moon', 'strife', 'bronze', 'maze'):
            bad.append('%s last_era 不对' % m['name'])
    return got, bad


def main():
    parts = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(os.path.join(WORK, '材料')) if '_' in f)
    for part in parts:
        r = check(part)
        if r is None:
            print(part, '还没交')
            continue
        got, bad = r
        k = sum(1 for g in got if g.get('keep'))
        print('%s：收 %d／%d，问题 %d' % (part, k, len(got), len(bad)))
        for b in bad[:60]:
            print('  ', b)


main()
