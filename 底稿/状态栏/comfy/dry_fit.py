# 换进正式目录以前先算：哪些人的新格子放不下（兵器举过头、人站得太宽），四套要一起缩多少。不写任何文件。
#   CAST_SET=前传 python dry_fit.py 任务单.json
import json, os, sys
os.chdir(r'E:\aldran_art\底稿\状态栏\comfy')
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding='utf-8')
import fix_cell as F
from PIL import Image
jobs = json.load(open(sys.argv[1], encoding='utf-8'))
by = {}
for j in jobs:
    p = os.path.join(F.WORK, j['en'], j['cell'] + '_fig.png')
    if os.path.exists(p):
        by.setdefault(j['en'], []).append(j['cell'])
    else:
        print('缺', j)
out = []
for k, cells in by.items():
    f = 1.0; who = None
    for c in cells:
        o = Image.open(os.path.join(F.WORK, k, c + '_fig.png')).convert('RGBA')
        bb = o.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
        dy = (F.OY + F.CH) - bb[3]
        top = bb[1] + dy - F.OY
        left, right = bb[0] - F.OX, bb[2] - F.OX
        g = 1.0
        if top < 0:
            g = min(g, F.CH / (F.CH - top))
        half = max(320 - left, right - 320)
        if half > 320:
            g = min(g, 320 / half)
        if g < f:
            f = g; who = c
    out.append((round(f, 3), k, who))
out.sort()
print('共', len(out), '位，要缩的', sum(1 for x in out if x[0] < 1))
for x in out:
    if x[0] < 0.97:
        print(x)
