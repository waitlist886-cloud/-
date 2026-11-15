# 从各份备注里抽地点谱份表（第六节那一块 ``` 围起来、头一行以「名字」起头的 TSV），写成同目录 份表/<份>.tsv
# 用法：python -I -X utf8 底稿/迷宫纪前传/补完/extract_fenbiao.py 丙一 丙二 …
# 抽出来以后：python -I -X utf8 底稿/地图/铺开/并进地点谱.py 迷宫纪前传 底稿/迷宫纪前传/补完/份表/丙一.tsv … --tag "11-14 迷宫补完" [--apply]
# 再到 底稿/地图/地点谱/ 下跑 python -I -X utf8 合表.py
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '份表')
os.makedirs(OUT, exist_ok=True)
for name in sys.argv[1:]:
    t = open(os.path.join(HERE, name + '_备注.md'), encoding='utf-8').read().replace('\r\n', '\n')
    blocks = re.findall(r'```[a-z]*\n(名字\t.*?)\n```', t, re.S)
    if not blocks:
        print(name, '没找到份表')
        continue
    lines = [l for l in blocks[-1].split('\n') if l.strip()]
    head = lines[0].split('\t')
    bad = [i for i, l in enumerate(lines[1:], 2) if len(l.split('\t')) != len(head)]
    p = os.path.join(OUT, name + '.tsv')
    open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines) + '\n')
    print(name, '%d 行，%d 栏' % (len(lines) - 1, len(head)), '栏数不对的行：%s' % bad if bad else '', '→', p)
