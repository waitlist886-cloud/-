# 拼对照图：一张图几格，每格一张截图加一行字。
# 用法：python sheet.py 输出.jpg 总宽 列数 "标题" 图1.png "说明1" 图2.png "说明2" ...
import sys
from PIL import Image, ImageDraw, ImageFont

out, W, cols, title = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
items = list(zip(sys.argv[5::2], sys.argv[6::2]))
FONT = 'C:/Windows/Fonts/msyh.ttc'
pad, cap_h, title_h = 24, 64, 90
cell_w = (W - pad * (cols + 1)) // cols
rows = []
for k in range(0, len(items), cols):
    row = []
    for path, cap in items[k:k + cols]:
        im = Image.open(path).convert('RGB')
        h = round(im.height * cell_w / im.width)
        row.append((im.resize((cell_w, h), Image.LANCZOS), cap))
    rows.append(row)
H = title_h + sum(max(im.height for im, _ in r) + cap_h + pad for r in rows) + pad
sheet = Image.new('RGB', (W, H), (246, 242, 233))
d = ImageDraw.Draw(sheet)
ft = ImageFont.truetype(FONT, 44)
fc = ImageFont.truetype(FONT, 30)
d.text((pad, 22), title, font=ft, fill=(44, 38, 31))
y = title_h
for r in rows:
    rh = max(im.height for im, _ in r)
    for j, (im, cap) in enumerate(r):
        x = pad + j * (cell_w + pad)
        sheet.paste(im, (x, y))
        d.rectangle([x - 1, y - 1, x + im.width, y + im.height], outline=(150, 140, 120))
        d.text((x + 4, y + im.height + 12), cap, font=fc, fill=(60, 52, 42))
    y += rh + cap_h + pad
sheet.save(out, quality=88)
print('ok', out, sheet.size)
