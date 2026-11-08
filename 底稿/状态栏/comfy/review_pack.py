# 查图总图：一位一张，上面四套衣服（铺灰底），下面立绘的头、艺术照、九格表情（铺灰底）。查的人先看这一张，要细看再裁原图放大。
#   python review_pack.py <纪> <页 json> <输出目录>
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

C = 'E:/aldran_art/底稿/状态栏/comfy/'
SET, J, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
F = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 30)
os.makedirs(OUT, exist_ok=True)


def grey(p):
    im = Image.open(p).convert('RGBA')
    bg = Image.new('RGBA', im.size, (60, 62, 74, 255))
    bg.alpha_composite(im)
    return bg.convert('RGB')


def fit(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


n = 0
JP = C + ('cast/%s' % J if SET == '1001' else 'cast/%s/%s' % (SET, J))   # 1001 那一套：资料 cast/cast_*.json，图 out/立绘_v3
for c in json.load(open(JP, encoding='utf-8')):
    d = C + 'out/立绘_%s/%s/' % ('v3' if SET == '1001' else SET, c['en'])
    if not all(os.path.exists(d + f) for f in ('sheet.png', 'head.png', 'art.png', 'faces.png')):
        print('缺图', c['en'])
        continue
    top = fit(grey(d + 'sheet.png'), 1200)
    row = [fit(grey(d + 'head.png'), 620), fit(Image.open(d + 'art.png').convert('RGB'), 620), fit(grey(d + 'faces.png'), 620)]
    W = max(top.width, sum(i.width for i in row) + 20)
    s = Image.new('RGB', (W, 46 + 1200 + 10 + 620), (20, 20, 26))
    ImageDraw.Draw(s).text((8, 4), '%s  %s　上：常服、私服、战斗、正装　下：立绘的头、艺术照、九格表情' % (c['en'], c['name']), font=F, fill=(255, 230, 160))
    s.paste(top, (0, 46))
    x = 0
    for i in row:
        s.paste(i, (x, 46 + 1200 + 10))
        x += i.width + 10
    s.save(os.path.join(OUT, c['en'] + '.jpg'), quality=86)
    n += 1
print(n, '张')
