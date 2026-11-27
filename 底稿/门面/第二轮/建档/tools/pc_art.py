# 建档“体格与立绘”的预览（11-26）：照状态栏的主角预设清单（gh_pc.json，pc_portrait.presets() 读的那一份）
# 写一份 小样_外壳/data/pc_art.json：{"晨曦人·女·均匀": {"art": 艺术照, "face": 头像, "por": 立绘四格}}。只读状态栏那边，不改。
#   python -I -X utf8 底稿/门面/第二轮/建档/tools/pc_art.py
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', '大框'))
sys.dont_write_bytecode = True
import pc_portrait  # noqa: E402

d = pc_portrait.presets()
out = os.path.join(ROOT, '底稿', '门面', '小样_外壳', 'data', 'pc_art.json')
json.dump({'about': '建档体格与立绘的预览，照状态栏主角预设（gh_pc.json）出的，pc_art.py 写', 'pc': {k: d[k] for k in sorted(d)}}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(d), '个预设 →', out)
