#!/usr/bin/env python3
# 图鉴的小图（11-17 夜）：图鉴的人物卡原来拿整张人像拼图（assets/pa/，一本 6 到 12 兆）缩着画，
# 年代轴的小圆点拿整幅时代原画（一本 0.7 到 6 兆）当底，打开图鉴在“全纪”那一页就把这些全拉下来，手机上要等很久。
# 日里的介绍页在沙箱里，浏览器不留缓存，每回打开都重新下一遍。这一步给图鉴单出两样小图，写进 data/atlas.json：
#   - 人物：每个有像的人从拼图里切出那一格，缩成 180×270，八列六行拼一张（assets/at/p1.webp、p2.webp……），人身上记 th=[张, 第几格]，D.th={张: [列, 行]}
#   - 年代轴：每个时代的图居中裁成 128×128，八列拼一张（assets/at/ax.webp），时代上记 tx=第几格，D.ax=[列, 行]
# 选中一个人时右边那张大像照旧用整张拼图（只取那一张）。
#   带 PIL 的 Python 跑：python -I -X utf8 底稿/门面/共用/prep_atlas_thumbs.py [书…]
# build_atlas.py 重出 atlas.json 以后要再跑一遍这个（它出的 atlas.json 里没有 th、tx）。
import io
import json
import math
import os
import sys

from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
FRONT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BOOKS = {'moon': '小样_月银纪书', 'strife': '小样_纷争纪书', 'bronze': '小样_山铜纪书', 'maze': '小样_迷宫纪书'}
TW, TH, COLS, ROWS = 180, 270, 8, 6          # 人物小图一格多大，一张拼几列几行（卡在电脑上一百三十来像素宽，手机上一百一十来像素、三倍屏，120 那一版在手机上发虚）
AX, AXC = 128, 8                             # 年代轴一格多大，几列
Q = 78


def one(key):
    bdir = os.path.join(FRONT, BOOKS[key])
    path = os.path.join(bdir, 'data', 'atlas.json')
    D = json.load(open(path, encoding='utf-8'))
    out = os.path.join(bdir, 'assets', 'at')
    os.makedirs(out, exist_ok=True)
    for fn in os.listdir(out):
        if fn.endswith('.webp'):
            os.remove(os.path.join(out, fn))
    # 一、人物
    sheets, cells, index = {}, [], {}
    for p in D.get('people', []):
        p.pop('th', None)
        if not p.get('pa'):
            continue
        k = (p['pa'][0], p['pa'][1])
        if k not in index:
            index[k] = len(cells)
            cells.append(k)
        n = index[k]
        p['th'] = ['p%d' % (n // (COLS * ROWS) + 1), n % (COLS * ROWS)]
    th, total = {}, 0
    for s in range(math.ceil(len(cells) / (COLS * ROWS))):
        chunk = cells[s * COLS * ROWS:(s + 1) * COLS * ROWS]
        rows = math.ceil(len(chunk) / COLS)
        cols = COLS if rows > 1 else len(chunk)
        canvas = Image.new('RGBA', (cols * TW, rows * TH), (0, 0, 0, 0))
        for i, (sheet, idx) in enumerate(chunk):
            if sheet not in sheets:
                sheets[sheet] = Image.open(os.path.join(bdir, 'assets', 'pa', sheet + '.webp')).convert('RGBA')
            im = sheets[sheet]
            c, r = D['pa'][sheet]
            cw, ch = im.width / c, im.height / r
            x, y = idx % c, idx // c
            cell = im.crop((round(x * cw), round(y * ch), round((x + 1) * cw), round((y + 1) * ch))).resize((TW, TH), Image.LANCZOS)
            canvas.paste(cell, ((i % cols) * TW, (i // cols) * TH))
        name = 'p%d' % (s + 1)
        canvas.save(os.path.join(out, name + '.webp'), 'WEBP', quality=Q, method=6)
        th[name] = [cols, rows]
        total += os.path.getsize(os.path.join(out, name + '.webp'))
    D['th'] = th          # 只有一行的那一张列数照实际的，格子编号照旧是这一张里第几格
    # 二、年代轴
    per = [p for p in D.get('periods', []) if p.get('img')]
    for p in D.get('periods', []):
        p.pop('tx', None)
    if per:
        cols = min(AXC, len(per))
        rows = math.ceil(len(per) / cols)
        canvas = Image.new('RGB', (cols * AX, rows * AX), (27, 28, 36))
        for i, p in enumerate(per):
            src = os.path.join(bdir, p['img']) if not p['img'].startswith('common/') else os.path.join(FRONT, '共用', p['img'][len('common/'):])
            im = Image.open(src).convert('RGB')
            s = AX / min(im.width, im.height)
            im = im.resize((max(AX, round(im.width * s)), max(AX, round(im.height * s))), Image.LANCZOS)
            l, t = (im.width - AX) // 2, (im.height - AX) // 2
            canvas.paste(im.crop((l, t, l + AX, t + AX)), ((i % cols) * AX, (i // cols) * AX))
            p['tx'] = i
        canvas.save(os.path.join(out, 'ax.webp'), 'WEBP', quality=Q, method=6)
        D['ax'] = [cols, rows]
        total += os.path.getsize(os.path.join(out, 'ax.webp'))
    else:
        D.pop('ax', None)
    json.dump(D, open(path, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, separators=(',', ':'))
    pa_bytes = sum(os.path.getsize(os.path.join(bdir, 'assets', 'pa', s + '.webp')) for s in D.get('pa', {}))
    per_bytes = sum(os.path.getsize(os.path.join(bdir, p['img'])) for p in per if not p['img'].startswith('common/'))
    print('%s 人 %d 格拼 %d 张，年代 %d 格；小图合计 %.2f MB（原来拼图 %.1f MB，时代图 %.1f MB）'
          % (BOOKS[key], len(cells), len(th), len(per), total / 1048576, pa_bytes / 1048576, per_bytes / 1048576))


if __name__ == '__main__':
    for k in (sys.argv[1:] or list(BOOKS)):
        one(k)
