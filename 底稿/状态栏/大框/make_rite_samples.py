# 超凡演出的样本：拿各纪现成的样本，在正文头一段后头插几行 §起手 和 §技，写到输出目录
# 第一个参数是 json：{纪: [行, …]}，纪可以带后缀（maze_tiers 照迷宫纪的样本），前传照迷宫纪的样本、底座年份挪到640年
# 用法：python -I -X utf8 底稿/状态栏/大框/make_rite_samples.py 底稿/状态栏/大框/超凡演出_样本行.json <输出目录>
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = {'maze': '样本_中期_交战.txt', 'pre': '样本_中期_交战.txt', 'bronze': '样本_山铜纪_葛摩恩.txt', 'strife': '样本_纷争纪_墙前.txt', 'moon': '样本_月银纪_焚原.txt'}
lines = json.load(open(sys.argv[1], encoding='utf-8'))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
for era, ls in lines.items():
    base = era.split('_')[0]
    t = open(os.path.join(BASE, SRC[base]), encoding='utf-8').read().replace('\r\n', '\n')
    if base == 'pre':
        t2 = re.sub(r'纪元：迷宫纪1001年', '纪元：迷宫纪640年', t, count=1)
        assert t2 != t, '前传的年份没换上'
        t = t2
    i = t.find('§正文｜')
    assert i >= 0, era
    j = t.find('\n\n', t.find('\n', i) + 1)
    t = t[:j] + '\n\n' + '\n\n'.join(ls) + t[j:]
    open(os.path.join(out, '演出_%s.txt' % era), 'w', encoding='utf-8', newline='\n').write(t)
    print(era, len(ls))
