#!/usr/bin/env python3
# 状态栏背包的通用图标（11-23）：AI 随手给的掉落、素材、杂物用的那一批，十二张拼图、一张十二样，一共 144 格。
# 画风参考 底稿/图标/参考_原神背包_11-23/（只学画风：单件居中、赛璐璐加一点厚涂、轮廓干净、物件自己带光）。
# 资料 底稿/图标/generic/sheets.json（一张一节：title、cat、theme 整张的调子、items 十二样各有 name、words 认它的字、look 英文外观）。
#   <ComfyUI 的 python> 底稿/图标/tools/gpt_generic.py list            照资料写 底稿/图标/generic/清单.tsv
#   CODEX_HOME=C:/Users/waitl/.codex_b <ComfyUI 的 python> 底稿/图标/tools/gpt_generic.py gen [张名…]   出图，写 out/图标_通用_11-23/sheet_<张名>.png，已有的不重出
#   CODEX_HOME=… <ComfyUI 的 python> 底稿/图标/tools/gpt_generic.py one <格号…>   某一格画坏了单出一张（先改资料里那一格的 look），写 fix_<格号>.png，cut 的时候盖掉拼图里那一格
#   <ComfyUI 的 python> 底稿/图标/tools/gpt_generic.py cut [张名…]    抠品红底、切格：格/gNNN.png（192 方格透明底）、generic.webp（12 列一张一行，一格 128）、总览.jpg
# 底是纯品红平底（跟 gpt_relic.py 一样，直接要透明底会出假棋盘格和雾），所以物件里不写品红、粉、紫红，暗系写 deep indigo。
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', 'comfy'))
sys.stdout.reconfigure(encoding='utf-8')

DATA = os.path.join(ROOT, '底稿', '图标', 'generic', 'sheets.json')
TSV = os.path.join(ROOT, '底稿', '图标', 'generic', '清单.tsv')
OUT = os.path.join(ROOT, 'out', '图标_通用_11-23')
COLS, ROWS = 4, 3
CELL, BOX = 128, 192

STYLE = ('A sheet of item icons for the inventory screen of a high-end Japanese anime-style fantasy action RPG. '
         'Stylized game item art, not photorealistic: slightly chunky simplified shapes with confident proportions, smooth cel-shaded colour planes finished with a little soft hand-painted gradient, '
         'crisp clean silhouettes, bright warm rim highlights, saturated but harmonious colours, materials that read at a glance (metal, glass, cloth, bone, wood, crystal), no gritty texture noise. '
         'Each object is a single item seen in three-quarter view or from the front slightly from above, instantly recognisable at a very small size, light from the upper left. ')
GRID = ('Landscape picture, aspect ratio 3:2. Exactly twelve separate objects in a perfectly regular grid of 4 columns and 3 rows, in the listed order, left to right, top to bottom. '
        'Each object is centered in its own cell, fills about two thirds of the cell, has empty space all around it and never touches or overlaps a neighbour; long objects lie on the diagonal of their cell. '
        'The background is one flat, solid, pure magenta colour (#FF00FF) filling the whole picture edge to edge: no gradient, no checkerboard, no texture, no vignette, no cell borders. '
        'No object contains any magenta, pink or purple-red. Any magical light stays on the object itself as inner glow and a few small sparkles hugging its surface; no haze, halo or smoke spreading onto the background. '
        'No text, no letters, no numbers, no labels, no frames, no stars or rarity marks, no hands, no ground, no cast shadow on the background. ')


def load():
    return json.load(open(DATA, encoding='utf-8'))


def cells(data):
    """格号照资料的次序排：一张一行，g001 起。"""
    n = 0
    for row, (k, s) in enumerate(data.items()):
        for col, it in enumerate(s['items']):
            n += 1
            yield 'g%03d' % n, k, row, col, s, it


def write_list():
    data = load()
    with open(TSV, 'w', encoding='utf-8', newline='\n') as f:
        f.write('格号\t张\t行\t列\t中文名\t认它的字\t类别\t英文外观\n')
        for g, k, row, col, s, it in cells(data):
            f.write('\t'.join([g, k, str(row), str(col), it['name'], it['words'], s['cat'], it['look']]) + '\n')
    print('清单', sum(len(s['items']) for s in data.values()), '格 →', TSV)


def prompt(s):
    assert len(s['items']) == COLS * ROWS
    items = ' '.join('%d. %s.' % (i + 1, it['look']) for i, it in enumerate(s['items']))
    return STYLE + s['theme'] + ' ' + GRID + 'The twelve objects: ' + items


def gen(names):
    import gpt_gen
    data = load()
    os.makedirs(OUT, exist_ok=True)

    def job(k):
        try:
            return gpt_gen.gen(os.path.join(OUT, 'sheet_' + k), prompt(data[k]))
        except Exception as x:   # 一张出错（额度、超时）不连累别的
            return '没成：%s' % str(x)[:300]

    with ThreadPoolExecutor(3) as ex:
        for k, r in zip(names, ex.map(job, names)):
            print(k, r, flush=True)


SOLO = ('Square picture, aspect ratio 1:1. Exactly one object, centered, filling about two thirds of the picture, with empty space all around it. '
        'The background is one flat, solid, pure magenta colour (#FF00FF) filling the whole picture edge to edge: no gradient, no checkerboard, no texture, no vignette. '
        'The object contains no magenta, pink or purple-red. Any magical light stays on the object itself; no haze, halo or smoke spreading onto the background. '
        'No text, no letters, no numbers, no labels, no frame, no stars or rarity marks, no hands, no ground, no cast shadow on the background. ')


def one(gs):
    import gpt_gen
    data = load()
    table = {g: (s, it) for g, k, row, col, s, it in cells(data)}
    for g in gs:
        s, it = table[g]
        pr = STYLE.replace('A sheet of item icons', 'One item icon') + SOLO + 'The object: ' + it['look'] + '.'
        try:
            print(g, gpt_gen.gen(os.path.join(OUT, 'fix_' + g), pr), flush=True)
        except Exception as x:
            print(g, '没成：%s' % str(x)[:300], flush=True)


def key(path):
    """品红平底抠成透明。底色照四边取，像素里“红蓝高、绿低”的那一截当成混进来的底色，照比例算透明度再把底色减掉；
    只对连着底的那一片这样算，物件里头不挨底的蓝紫不动。"""
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    edge = np.concatenate([im[:6].reshape(-1, 3), im[-6:].reshape(-1, 3), im[:, :6].reshape(-1, 3), im[:, -6:].reshape(-1, 3)])
    bg = np.median(edge, axis=0)
    mb = min(bg[0], bg[2]) - bg[1]
    if mb < 120:
        raise RuntimeError('%s 的底不是品红（四边取到 %s）' % (path, bg.round()))
    m = np.minimum(im[..., 0] * (255 / bg[0]), im[..., 2] * (255 / bg[2])) - im[..., 1]
    soft = np.clip(1 - (m - 14) / (255 - bg[1] - 14 - 22), 0, 1)
    # 连着底的那一片（带一点品红味的像素一路连到四边）才照 soft 算
    lab, n = ndimage.label(m > 28)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    solid = np.linalg.norm(im - bg, axis=2) < 70
    hit = np.unique(lab[solid])
    # 物件里头透出底色的地方（玻璃瓶、圈住的空当）不挨四边，照品红味够不够重算进来
    peak = ndimage.maximum(m, lab, index=range(1, n + 1)) if n else []
    deep = [i + 1 for i, v in enumerate(peak) if v > 0.45 * (255 - bg[1])]
    open_ = set(border) | set(hit)
    zone = np.isin(lab, [v for v in open_ | set(deep) if v])
    alpha = np.where(zone, soft, 1.0)
    # 圈死的小空当（钥匙孔、链环）里模型常把底画暗一点：照色相算，红蓝比绿高得多的就是底
    shut = np.isin(lab, [v for v in set(deep) - open_ if v])
    hue = m / np.maximum(np.maximum(im[..., 0], im[..., 2]), 1)
    alpha = np.where(shut, np.minimum(alpha, np.clip(1 - (hue - 0.5) / 0.3, 0, 1)), alpha)
    alpha = np.where(zone, alpha * np.clip(1 - (hue - 0.4) / 0.3, 0, 1), alpha)   # 连着底的也一样：暗一档的品红（孔里的影子）照底算
    # 物件自己的靛蓝、蓝紫（红蓝都不高，或者蓝比红高一截；离纯底有几个像素）不是透出来的底，照实心算。
    # 透出来的底是红蓝一起往上抬，所以白汽、暖色的光混了底以后红不会比蓝低
    far = ndimage.distance_transform_edt(~solid) > 3
    own = far & (m < 0.8 * (255 - bg[1])) & (hue < 0.7) & (((np.maximum(im[..., 0], im[..., 2]) < 170) & (im[..., 2] >= im[..., 0] - 10)) | (im[..., 2] - im[..., 0] > 40))
    alpha[own] = 1.0
    zone = zone & ~own
    a3 = np.clip(alpha, 1e-3, 1)[..., None]
    rgb = np.clip((im - (1 - a3) * bg) / a3, 0, 255)
    # 半透明的地方（汽、电光、小星、玻璃）减完底色还带一点粉，把红蓝里多出来的那一截照透明的程度压掉
    w = np.clip((1 - alpha) * 4, 0, 1) * zone
    for c in (0, 2):
        rgb[..., c] -= np.clip(rgb[..., c] - rgb[..., 1], 0, None) * w
    # 物件的边和贴身的光：半透明那几个像素的颜色照最近的实心像素取，免得橙、黄、绿的边上和电光外头留一圈红粉；离实心远的（汽）不动
    opaque = alpha > 0.985
    dist, idx = ndimage.distance_transform_edt(~opaque, return_indices=True)
    rim = (~opaque) & (alpha > 0.02) & (dist <= 4.5)
    rgb[rim] = rgb[idx[0][rim], idx[1][rim]]
    rgb[alpha < 0.02] = 0
    return Image.fromarray(np.dstack([rgb, alpha * 255]).astype('uint8'), 'RGBA')


def cut_sheet(path):
    """一张切十二样：连通块照重心归到最近的格子，一格的块并起来取外框（照 comfy/make_icons.py）。回十二张裁好的原尺寸图。"""
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    im = key(path)
    px = np.array(im)
    a = px[..., 3] > 40
    W, H = im.size
    lab, n = ndimage.label(ndimage.binary_dilation(a, iterations=3))
    sizes = ndimage.sum_labels(np.ones_like(lab), lab, index=range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i, v in enumerate(sizes) if v >= 260])
    px[..., 3][~keep] = 0
    im = Image.fromarray(px, 'RGBA')
    boxes = [None] * (COLS * ROWS)
    warn = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        if sizes[i] < 260:
            continue
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        cy, cx = ndimage.center_of_mass(lab[sl] == i + 1)
        cx, cy = cx + x0, cy + y0
        k = min(int(cy / (H / ROWS)), ROWS - 1) * COLS + min(int(cx / (W / COLS)), COLS - 1)
        if (x1 - x0) > W / COLS * 1.25 or (y1 - y0) > H / ROWS * 1.25:
            warn.append('第 %d 格有一块跨了格（%d×%d），多半是两样粘在一起' % (k + 1, x1 - x0, y1 - y0))
        b = boxes[k]
        boxes[k] = (x0, y0, x1, y1) if b is None else (min(b[0], x0), min(b[1], y0), max(b[2], x1), max(b[3], y1))
    out = []
    for k, b in enumerate(boxes):
        if b is None:
            warn.append('第 %d 格是空的' % (k + 1))
            out.append(None)
            continue
        c = im.crop(b)
        bb = c.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
        out.append(c.crop(bb) if bb else c)
    return out, warn


def fit(im, size, pad):
    from PIL import Image
    cell = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    if im is None:
        return cell
    s = (size - pad) / max(im.size)
    c = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    cell.alpha_composite(c, ((size - c.width) // 2, (size - c.height) // 2))
    return cell


def cut(names):
    from PIL import Image, ImageDraw, ImageFont
    data = load()
    os.makedirs(os.path.join(OUT, '格'), exist_ok=True)
    rows = list(data)
    sprite = Image.new('RGBA', (CELL * COLS * ROWS, CELL * len(rows)), (0, 0, 0, 0))
    T, LBL = 132, 34
    over = Image.new('RGB', (T * 12 + 16, (T + LBL) * len(rows) + 16), (38, 40, 52))
    dr = ImageDraw.Draw(over)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 11)
    done = 0
    for g, k, row, col, s, it in cells(data):
        p = os.path.join(OUT, 'sheet_%s.png' % k)
        x, y = 8 + col * T, 8 + row * (T + LBL)
        dr.rounded_rectangle((x + 3, y + 3, x + T - 3, y + T - 3), 10, fill=(74, 78, 98))
        dr.text((x + 6, y + T - 1), g[1:], font=small, fill=(150, 156, 180))
        dr.text((x + 34, y + T - 3), it['name'], font=font, fill=(226, 224, 214))
        if not os.path.exists(p):
            continue
        if col == 0:
            if not names or k in names or not all(os.path.exists(os.path.join(OUT, '格', 'g%03d.png' % (row * 12 + i + 1))) for i in range(12)):
                crops, warn = cut_sheet(p)
                for w in warn:
                    print(k, w)
                for i, c in enumerate(crops):
                    fx = os.path.join(OUT, 'fix_g%03d.png' % (row * 12 + i + 1))
                    if os.path.exists(fx):   # 单出的那一张盖掉拼图里这一格
                        c = key(fx)
                        c = c.crop(c.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox())
                    fit(c, BOX, 12).save(os.path.join(OUT, '格', 'g%03d.png' % (row * 12 + i + 1)))
        gp = os.path.join(OUT, '格', g + '.png')
        if os.path.exists(gp):
            c = Image.open(gp).convert('RGBA')
            bb = c.getchannel('A').getbbox()
            c = c.crop(bb) if bb else None
            sprite.alpha_composite(fit(c, CELL, 10), (col * CELL, row * CELL))
            ic = fit(c, T - 14, 10)
            over.paste(ic, (x + 7, y + 7), ic)
            done += 1
    sprite.save(os.path.join(OUT, 'generic.webp'), quality=82, method=6, alpha_quality=90)
    over.save(os.path.join(OUT, '总览.jpg'), quality=90)
    print('切了', done, '格；generic.webp', sprite.size, os.path.getsize(os.path.join(OUT, 'generic.webp')) // 1024, 'KB；总览.jpg', over.size)


if __name__ == '__main__':
    cmd, names = (sys.argv[1:2] or ['list'])[0], sys.argv[2:]
    if cmd == 'list':
        write_list()
    elif cmd == 'gen':
        gen(names or list(load()))
    elif cmd == 'one':
        one(names)
    elif cmd == 'cut':
        cut(names)
    elif cmd == 'prompt':
        print(prompt(load()[names[0]]))
    else:
        sys.exit('用法见文件头')
