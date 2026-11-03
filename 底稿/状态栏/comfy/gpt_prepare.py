#!/usr/bin/env python3
# GPT 出的两扇裁出要单独抠的地方，写 out/四方_11-03/<来源>/crop/，等 cut_cpu.py 抠。python gpt_prepare.py [pv_a|pv_b|pv_c|mid|gpt]
# 右扇整张抠（人群对着天，主体很清楚），左扇是整片的城，只裁靠窗那一边伸出去的东西，框在 maze1001_frame_gpt.py 的 VERS 里。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image
from maze1001_frame_gpt import ROOT, VERS

v = VERS[sys.argv[1] if len(sys.argv) > 1 else 'mid']
G = os.path.join(ROOT, v['src'])
os.makedirs(os.path.join(G, 'crop'), exist_ok=True)
Image.open(os.path.join(G, v.get('right', 'right.png'))).convert('RGB').save(os.path.join(G, 'crop', v.get('rcut', 'r_full') + '.png'))
L = Image.open(os.path.join(G, v['left'])).convert('RGB')
for name, box in v['boxes']:
    c = L.crop(box)
    c.resize((c.width * 2, c.height * 2), Image.LANCZOS).save(os.path.join(G, 'crop', name + '.png'))
print('ok', v['src'])
