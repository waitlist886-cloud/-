# 分块截整张图再拼起来：python stitch.py 输出 倍数 列 行 [质量]
# 先用 cdp.mjs clip 截 tile_<r>_<c>.png 到输出同一个目录（脚本自己调 node），再拼成一张，输出 .png 或 .jpg/.webp
import os
import subprocess
import sys
from PIL import Image

out, sc, cols, rows = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
q = int(sys.argv[5]) if len(sys.argv) > 5 else 90
W, H = 2200, 1400
here = os.path.dirname(os.path.abspath(__file__))
tmp = os.path.join(os.path.dirname(os.path.abspath(out)), '_tiles')
os.makedirs(tmp, exist_ok=True)
tw, th = W / cols, H / rows
big = Image.new('RGB', (round(W * sc), round(H * sc)))
for r in range(rows):
    for c in range(cols):
        p = os.path.join(tmp, f'tile_{r}_{c}.png')
        subprocess.run(['node', os.path.join(here, 'cdp.mjs'), 'clip', p, str(c * tw), str(r * th), str(tw), str(th), str(sc)], check=True, cwd=here, capture_output=True)
        im = Image.open(p).convert('RGB')
        big.paste(im, (round(c * tw * sc), round(r * th * sc)))
if out.lower().endswith('.png'):
    big.save(out)
else:
    big.save(out, quality=q)
print('ok', out, big.size)
