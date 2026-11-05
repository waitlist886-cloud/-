# 透明图铺灰底另存 jpg 再看（看图工具不管透明通道，会把透明处原本的颜色也画出来，11-05 因此误判过一回）
#   python grey.py 输出.jpg 图1 图2 ...   竖着叠
import sys
from PIL import Image
out, fs = sys.argv[1], sys.argv[2:]
W = 1400
tiles = []
for f in fs:
    im = Image.open(f).convert('RGBA')
    bg = Image.new('RGBA', im.size, (60, 62, 74, 255))
    bg.alpha_composite(im)
    im = bg.convert('RGB')
    tiles.append(im.resize((W, round(im.height * W / im.width)), Image.LANCZOS))
s = Image.new('RGB', (W, sum(t.height for t in tiles) + 10 * (len(tiles) - 1)), (0, 0, 0))
y = 0
for t in tiles:
    s.paste(t, (0, y))
    y += t.height + 10
s.save(out, quality=88)
print(out, s.size)
