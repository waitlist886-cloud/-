#!/usr/bin/env python3
# 背包格子那一份要上图床的图（11-23）：通用图标一张、专属器物的图标五张（一纪一张）、原画一件一张。
#   python -I -X utf8 底稿/状态栏/大框/第三轮/bag_bake.py        写 out/第三轮_背包格子/上传/ 和同目录的 清单.tsv
# 通用那一张 bagi.webp：12 列 18 行、一格 112。上六行是旧的 72 格（items.webp，104 放到 112，行列不变，旧样式里的 --ix、--iy 照用），
# 下十二行是 11-23 的 144 格（generic.webp，行号加 6）。
# 专属图标 bagr_<纪>.webp：12 列，行数看这一纪有几件，排法照 bag_icons.relic_layout()（样式也读它，两头对得上）。
# 原画 ra_<键>.webp：长边 512，一张不过 60KB（先降画质，还过就缩边）。
import os
import sys

sys.dont_write_bytecode = True
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import bag_icons

OUT = os.path.join(ROOT, 'out', '第三轮_背包格子', '上传')
CUT = os.path.join(ROOT, 'out', '图标_原画', '抠')
OLD = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'out', 'frame_art', 'items.webp')
GEN = os.path.join(ROOT, 'out', '图标_通用_11-23', 'generic.webp')
CELL = 128     # 专属图标一格
CELL_G = 112   # 通用图标一格：格子里最大显示 70 像素上下，128 的那一版 1MB，112 压到 0.77MB
LIMIT = 60 * 1024


def save(im, path, q, aq=90):
    im.save(path, 'WEBP', quality=q, method=6, alpha_quality=aq)
    return os.path.getsize(path)


def generic():
    old = Image.open(OLD).convert('RGBA')
    gen = Image.open(GEN).convert('RGBA')
    assert old.size == (1248, 624) and gen.size == (1536, 1536), (old.size, gen.size)
    c = CELL_G
    sheet = Image.new('RGBA', (c * 12, c * 18), (0, 0, 0, 0))
    sheet.alpha_composite(old.resize((c * 12, c * 6), Image.LANCZOS), (0, 0))
    sheet.alpha_composite(gen.resize((c * 12, c * 12), Image.LANCZOS), (0, c * 6))
    return save(sheet, os.path.join(OUT, 'bagi.webp'), 72, 80)


def icon(key):
    im = Image.open(os.path.join(CUT, key + '.png')).convert('RGBA')
    im.thumbnail((CELL - 10, CELL - 10), Image.LANCZOS)
    cell = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
    cell.alpha_composite(im, ((CELL - im.width) // 2, (CELL - im.height) // 2))
    return cell


def relic_sheets():
    lay = bag_icons.relic_layout()
    out = []
    for sid, (fname, rows) in bag_icons.SHEETS.items():
        sheet = Image.new('RGBA', (CELL * 12, CELL * rows), (0, 0, 0, 0))
        n = 0
        for key, (s, x, y) in lay.items():
            if s == sid:
                sheet.alpha_composite(icon(key), (x * CELL, y * CELL))
                n += 1
        out.append((fname, save(sheet, os.path.join(OUT, fname), 82, 90), n))
    return out


def art(key):
    src = Image.open(os.path.join(CUT, key + '.png')).convert('RGBA')
    bb = src.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    src = src.crop(bb)
    p = os.path.join(OUT, 'ra_%s.webp' % key)
    for side in (512, 480, 448, 416, 384):
        im = src.copy()
        im.thumbnail((side, side), Image.LANCZOS)
        for q in (84, 78, 72, 66, 60, 54):
            n = save(im, p, q, 86)
            if n <= LIMIT:
                return n, im.size, q
    return n, im.size, q


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = [('bagi.webp', generic(), '通用图标 12 列 18 行（旧 72 格在上六行，11-23 的 144 格在下十二行）')]
    for fname, n, cnt in relic_sheets():
        rows.append((fname, n, '专属图标 %d 件' % cnt))
    names = {r['key']: r['name'] for r in bag_icons.relics()}
    for key in sorted(names):
        n, size, q = art(key)
        rows.append(('ra_%s.webp' % key, n, '原画 %s %dx%d q%d' % (names[key], size[0], size[1], q)))
    with open(os.path.join(os.path.dirname(OUT), '清单.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('文件名\t字节\t说明\n')
        for r in rows:
            f.write('%s\t%d\t%s\n' % r)
    tot = sum(r[1] for r in rows)
    big = [r for r in rows if r[0].startswith('ra_') and r[1] > LIMIT]
    print('%d 个文件，合计 %.2f MB；拼图 %s；原画最大 %d 字节，过 60KB 的 %d 张' % (
        len(rows), tot / 1e6, ' '.join('%s=%dKB' % (r[0], r[1] // 1024) for r in rows[:6]), max(r[1] for r in rows[6:]), len(big)))


if __name__ == '__main__':
    main()
