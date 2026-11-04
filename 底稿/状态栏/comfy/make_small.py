#!/usr/bin/env python3
# 测试卡的图都写在样式里（上限两百万字），座换小一号腾地方；顺手把 Boss 各阶转成 webp。正式卡上图床以后用不着。
#   python make_small.py    要 PIL，用 ComfyUI 那个 venv 的 python
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import gpt_boss

ART = gpt_boss.ART
im = Image.open(os.path.join(ART, 'maze_bottom.webp')).convert('RGBA')
im = im.resize((2900, round(im.height * 2900 / im.width)), Image.LANCZOS)
p = os.path.join(ART, 'maze_bottom_small.webp')
im.save(p, quality=66, method=6, alpha_quality=70)
print('maze_bottom_small', im.size, os.path.getsize(p) // 1024, 'KB')
for n in ('yanzuo1', 'yanzuo2d', 'yanzuo3d'):
    gpt_boss.webp(n)
