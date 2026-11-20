#!/usr/bin/env python3
# 技艺铺开（11-20）：全卷换名以前，把新星条里自己的旧名（首段里当俗名写的那个）先遮起来，换完再放回去。
#   python -I -X utf8 底稿/命星重审第二轮/tools/mask_self.py mask
#   python -I -X utf8 tools/rename_stars.py --map 底稿/命星重审第二轮/收稿/技艺改名表.md --apply ...
#   python -I -X utf8 底稿/命星重审第二轮/tools/mask_self.py unmask
# 遮的只是「### 新名 (Art | 档)」那一块里出现的它自己的旧名，别的旧名照常换。遮法记在 收稿/遮名.json。
import glob
import importlib.util
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
R = os.path.join(ROOT, '底稿', '命星重审第二轮', '收稿')
spec = importlib.util.spec_from_file_location('rs', os.path.join(ROOT, 'tools', 'rename_stars.py'))


def sources():
    src = open(os.path.join(ROOT, 'tools', 'rename_stars.py'), encoding='utf-8').read()
    i = src.index('SOURCES = [')
    pats = re.findall(r"'([^']+\.md)'", src[i:src.index(chr(10) + ']', i)])
    out = []
    for p in pats:
        out += glob.glob(os.path.join(ROOT, p))
    return sorted(set(out))


def mask():
    mp = re.findall(r'^\| (\S+) \| (\S+) \|$', open(os.path.join(R, '技艺改名表.md'), encoding='utf-8').read(), re.M)[1:]
    inv = {n: o for o, n in mp}
    rec, k = {}, 0
    for f in sources():
        raw = open(f, encoding='utf-8', newline='').read()
        t = raw
        for m in list(re.finditer(r'^### (\S+) \(Art \| \w+\)\r?\n.*?(?=^### |^## |^> 条目设置|\Z)', t, re.S | re.M))[::-1]:
            new = m.group(1)
            old = inv.get(new)
            if not old or old not in m.group(0):
                continue
            tok = '⟦M%04d⟧' % k
            k += 1
            rec[tok] = old
            t = t[:m.start()] + m.group(0).replace(old, tok) + t[m.end():]
        if t != raw:
            open(f, 'w', encoding='utf-8', newline='').write(t)
    json.dump(rec, open(os.path.join(R, '遮名.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('遮了', len(rec), '处')


def unmask():
    rec = json.load(open(os.path.join(R, '遮名.json'), encoding='utf-8'))
    n = 0
    for f in sources() + glob.glob(os.path.join(ROOT, 'out', '进卡_v12', 'tools', '*.py')):
        raw = open(f, encoding='utf-8', newline='').read()
        if '⟦M' not in raw:
            continue
        t = re.sub(r'⟦M\d{4}⟧', lambda m: rec[m.group(0)], raw)
        open(f, 'w', encoding='utf-8', newline='').write(t)
        n += 1
    left = [f for f in sources() if '⟦M' in open(f, encoding='utf-8').read()]
    print('放回', n, '个文件，还剩', len(left))


if __name__ == '__main__':
    {'mask': mask, 'unmask': unmask}[sys.argv[1]]()
