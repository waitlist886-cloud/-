#!/usr/bin/env python3
# 11-22 新人那一批（cast/<纪>/*x.json、纷争纪 z?r.json）出完以后查图用的拼图：一人一张 jpg，
# 上面设定图，下面艺术照、九格表情，有 identity 的右下角放参考的头像。再把人分成 N 份，写派活用的名单。
#   "<ComfyUI venv python>" -X utf8 底稿/立绘/tools/newcast_sheet.py [份数]
# 写 底稿/状态栏/comfy/out/新人查图_1122/<纪>/<键>.jpg 和 份_<n>.tsv（纪、键、名字、cast 文件、缺哪几样）。
import glob
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
OUT = os.path.join(COMFY, 'out', '新人查图_1122')
SETS = ['前传', '山铜纪', '纷争纪', '萨尔维斯', '诸国期', '月银纪史诗']
FONT = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 34)


def flat(im):
    im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, 'white')
    return Image.alpha_composite(bg, im).convert('RGB')


def fit_h(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def main():
    n_parts = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    rows = []
    for s in SETS:
        fs = sorted(glob.glob(os.path.join(COMFY, 'cast', s, '*x.json')))
        if s == '纷争纪':
            fs += sorted(glob.glob(os.path.join(COMFY, 'cast', s, 'z?r.json')))
        for f in fs:
            for c in json.load(open(f, encoding='utf-8')):
                rows.append((s, c, os.path.relpath(f, ROOT).replace(os.sep, '/')))
    made = []
    for s, c, rel in rows:
        k = c['en']
        d = os.path.join(COMFY, 'out', '立绘_' + s, k)
        miss = [p for p in ('sheet', 'art', 'faces') if not os.path.exists(os.path.join(d, p + '.png'))]
        if len(miss) == 3:
            made.append((s, k, c['name'], rel, '全缺'))
            continue
        W = 1760
        canvas = Image.new('RGB', (W, 60 + 1173 + 20 + 800), 'white')
        dr = ImageDraw.Draw(canvas)
        dr.text((10, 10), '%s  %s  %s' % (c['name'], k, s), fill='black', font=FONT)
        if 'sheet' not in miss:
            sh = Image.open(os.path.join(d, 'sheet.png')).convert('RGB')
            sh = sh.resize((W, round(sh.height * W / sh.width)), Image.LANCZOS)
            canvas.paste(sh, (0, 60))
        Y = 60 + 1173 + 20
        x = 0
        for p in ('art', 'faces'):
            if p in miss:
                continue
            im = fit_h(flat(Image.open(os.path.join(d, p + '.png'))), 800)
            canvas.paste(im, (x, Y))
            x += im.width + 10
        idp = c.get('identity')
        if idp:
            ip = idp if os.path.isabs(idp) else os.path.join(COMFY, idp)
            if not os.path.exists(ip):
                ip = os.path.join(COMFY, 'out', idp)
            if os.path.exists(ip):
                im = fit_h(flat(Image.open(ip)), 380)
                canvas.paste(im, (x, Y + 50))
                dr.text((x, Y), '参考', fill='red', font=FONT)
        os.makedirs(os.path.join(OUT, s), exist_ok=True)
        canvas.save(os.path.join(OUT, s, k + '.jpg'), quality=85)
        made.append((s, k, c['name'], rel, ','.join(miss)))
    per = -(-len(made) // n_parts)
    for i in range(n_parts):
        part = made[i * per:(i + 1) * per]
        if not part:
            continue
        with open(os.path.join(OUT, '份_%d.tsv' % (i + 1)), 'w', encoding='utf-8') as fh:
            for r in part:
                fh.write('\t'.join(r) + '\n')
    print('一共', len(made), '位，全缺', sum(1 for r in made if r[4] == '全缺'), '，缺一部分', sum(1 for r in made if r[4] and r[4] != '全缺'), '，每份', per)
    for r in made:
        if r[4]:
            print(' ', *r)


if __name__ == '__main__':
    main()
