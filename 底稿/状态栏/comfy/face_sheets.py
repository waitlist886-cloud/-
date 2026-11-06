# 查艺术照五官正不正用的小样：一位一格，左边立绘的头（铺灰底），右边艺术照的上半截，一张六位。
#   python face_sheets.py <输出目录> <页 json …>
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

C = 'E:/aldran_art/底稿/状态栏/comfy/'
OUT = sys.argv[1]
SKIP = {'q4b_yesen', 'q6_zlata', 'q6_odette', 'q6_fenya'}
F = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 24)
H = 470
os.makedirs(OUT, exist_ok=True)


def grey(im):
    im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, (60, 62, 74, 255))
    bg.alpha_composite(im)
    return bg.convert('RGB')


cast = []
for j in sys.argv[2:]:
    cast += [c for c in json.load(open(C + 'cast/前传/' + j, encoding='utf-8')) if c['en'] not in SKIP]
tiles = []
for c in cast:
    d = C + 'out/立绘_前传/' + c['en'] + '/'
    if not (os.path.exists(d + 'head.png') and os.path.exists(d + 'art.png')):
        print('缺图', c['en'])
        continue
    h = grey(Image.open(d + 'head.png')).resize((H, H), Image.LANCZOS)
    a = Image.open(d + 'art.png').convert('RGB')
    w, hh = a.size
    a = a.crop((int(w * .08), 0, int(w * .92), int(hh * .58)))
    a = a.resize((round(a.width * H / a.height), H), Image.LANCZOS)
    t = Image.new('RGB', (H + 6 + a.width, H + 36), (20, 20, 26))
    t.paste(h, (0, 36))
    t.paste(a, (H + 6, 36))
    ImageDraw.Draw(t).text((6, 3), c['en'] + '  ' + c['name'] + '  （左：立绘的头　右：艺术照上半截）', font=F, fill=(255, 230, 160))
    tiles.append((c['en'], t))
TW = max(t.width for _, t in tiles)
n = 0
lst = []
for i in range(0, len(tiles), 6):
    part = tiles[i:i + 6]
    s = Image.new('RGB', (2 * TW + 12, 3 * (H + 48)), (0, 0, 0))
    for j, (k, t) in enumerate(part):
        s.paste(t, ((j % 2) * (TW + 12), (j // 2) * (H + 48)))
    n += 1
    p = os.path.join(OUT, '五官_%02d.jpg' % n)
    s.save(p, quality=86)
    lst.append('%s：%s' % (os.path.basename(p), ' '.join(k for k, _ in part)))
open(os.path.join(OUT, '清单.txt'), 'w', encoding='utf-8').write('\n'.join(lst) + '\n')
print(n, '张', len(tiles), '位')
