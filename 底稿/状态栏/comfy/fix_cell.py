#!/usr/bin/env python3
# 单格重画（11-07）：风尚审图查出来正装和战斗两列最糊，整张设定图重出又会把脸和一边才有的记号重掷一遍（缺指缺耳查了三回）。
# 这里只换一格的衣服：拿这一格的人放进 1024×1536 的竖版，叫 GPT 原样重画、只换衣服，出来以后拿头那一块跟输入对齐（归一化互相关），
# 还原到格子里原来的位置。常服、艺术照、九格都不动。对齐的相关值同时当脸走样的报警。
#   CAST_SET=纷争纪 python fix_cell.py run 任务.json        任务是 [{"en":"z4b_azro","cell":"formal"}, …]，文字读资料里 formal、battle、casual 那一栏；已有的跳过；撞 429 就停
#   CAST_SET=纷争纪 python fix_cell.py sheet 输出.jpg 任务.json   拼 改前｜改后 的对照
#   CAST_SET=纷争纪 python fix_cell.py apply 任务.json [--only a,b] [--skip a,b]   换进正式目录，旧的挪 备选/<键>/风尚前/
# 1001 那一套不设 CAST_SET。工作目录 out/风尚_1107/<纪>/<键>/。
import json
import os
import shutil
import sys
import threading
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cast_slice as CS  # noqa: E402
import era_fashion as EF  # noqa: E402
import gpt_gen  # noqa: E402
import gpt_sheet as S  # noqa: E402

SETN = S.SET or '1001'
WORK = os.path.join(HERE, 'out', '风尚_1107', SETN)
ALT = S.OUT + '_备选'
CELLS = ('casual', 'private', 'battle', 'formal')
CW, CH = 640, 960
OW, OH, OX, OY = 1280, 1440, 320, 480   # 新人放在一张大一圈的底上，枪尖伸出格子也留着
GREY = (60, 62, 74, 255)
OUT_W, OUT_H = 1024, 1536
LOW_NCC = 0.60   # 低于这个，脸多半走样了
stop = threading.Event()

EDIT = ('Image 1 is a finished full-body character sprite from a Japanese RPG, on a transparent background. Repaint the very same picture, portrait, aspect ratio 2:3, at the same scale and position. '
        'The character keeps EXACTLY the same face, expression, eyes, eye colour, hair, hairstyle, skin colour, head angle, horns, ears, tail, wings, glasses, scars, missing fingers and every other mark of the body, and the same body proportions, height and stance. '
        'The ONLY change is the outfit, redrawn as described here (the hands and what they hold may change as far as this description says): {text} '
        '{era}'
        'Same rendering as the input, as crisp or crisper: sharp thin warm-brown line art, clean colouring with soft gradients, light shading, fine detail on metal, leather and cloth. '
        'No East Asian dress: no crossed wrap collars, no wide hanging sleeves, no looped cord or knotted cloth fastenings across the chest, no stiff mandarin collar. No crescent shapes. '
        'The whole figure and everything held stays inside the picture. Transparent background: no floor, no cast shadow, no glow or haze around the figure beyond a small magical light on the gear itself. No text, no labels, no numbers, no frame. Fully clothed, modest, not sexualized. ')
RETRY = 'Keep the figure well inside the picture with a clean empty transparent background all around it. '


def wd(k):
    p = os.path.join(WORK, k)
    os.makedirs(p, exist_ok=True)
    return p


def cell_img(k, cell):
    return Image.open(os.path.join(S.d(k), 'cell_%s.png' % cell)).convert('RGBA')


def on_grey(im):
    bg = Image.new('RGBA', im.size, GREY)
    bg.alpha_composite(im)
    return bg.convert('RGB')


def head_box(k):
    """头那一块，在格子坐标里：看常服那一格（四格同一比例、脚踩格底、头对正中），高度取人高的两成。"""
    a = cell_img(k, 'casual').getchannel('A')
    x0, y0, x1, y1 = a.point(lambda v: 255 if v > 40 else 0).getbbox()
    h = y1 - y0
    w = int(h * 0.20)
    return (320 - w // 2, y0, 320 + w // 2, y0 + w)


def make_input(k, cell):
    """回 (路径, k, ox, oy)：画布坐标 = (ox + k·x, oy + k·y)。"""
    im = cell_img(k, cell)
    x0, y0, x1, y1 = im.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
    half = max(320 - x0, x1 - 320, 1)
    kk = min(1.35, 1440 / (y1 - y0), 490 / half)
    r = im.resize((round(CW * kk), round(CH * kk)), Image.LANCZOS)
    ox = OUT_W // 2 - round(320 * kk)
    oy = 1500 - round(y1 * kk)
    c = Image.new('RGBA', (OUT_W, OUT_H), (0, 0, 0, 0))
    c.alpha_composite(r, (max(0, ox), max(0, oy)), (max(0, -ox), max(0, -oy)))
    p = os.path.join(wd(k), cell + '_in.png')
    c.save(p)
    return p, kk, ox, oy


def gray(im, f=3):
    g = on_grey(im).convert('L')
    return np.asarray(g.resize((g.width // f, g.height // f), Image.BILINEAR), dtype=np.float32)


def align(src, out, box, f=3):
    """src、out 是同大的 RGBA。box 是 src 上头那一块。回 (sc, tx, ty, ncc)：out 坐标 = sc·src 坐标 + t。"""
    A = gray(src, f)
    B = gray(out, f)
    x0, y0, x1, y1 = [v // f for v in box]
    best = (-2, 1.0, 0, 0)
    for sc in np.arange(0.88, 1.13, 0.02):
        tw, th = max(8, round((x1 - x0) * sc)), max(8, round((y1 - y0) * sc))
        T = np.asarray(Image.fromarray(A[y0:y1, x0:x1]).resize((tw, th), Image.BILINEAR), dtype=np.float32)
        T = T - T.mean()
        ts = float(np.sqrt((T * T).sum())) or 1.0
        # 输入里头在 (x0,y0)，放大 sc 以后的位置按“脚底不动”估一个中心，周围找
        cx, cy = x0 * sc + (1 - sc) * B.shape[1] / 2, y0 * sc + (1 - sc) * (1500 / f)
        for dy in range(-30, 31, 2):
            for dx in range(-30, 31, 2):
                px, py = int(round(cx + dx)), int(round(cy + dy))
                if px < 0 or py < 0 or px + tw > B.shape[1] or py + th > B.shape[0]:
                    continue
                W = B[py:py + th, px:px + tw]
                W = W - W.mean()
                ws = float(np.sqrt((W * W).sum())) or 1.0
                v = float((T * W).sum()) / (ts * ws)
                if v > best[0]:
                    best = (v, float(sc), px, py)
    v, sc, px, py = best
    # 细化一步
    tw, th = max(8, round((x1 - x0) * sc)), max(8, round((y1 - y0) * sc))
    T = np.asarray(Image.fromarray(A[y0:y1, x0:x1]).resize((tw, th), Image.BILINEAR), dtype=np.float32)
    T = T - T.mean()
    ts = float(np.sqrt((T * T).sum())) or 1.0
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            qx, qy = px + dx, py + dy
            if qx < 0 or qy < 0 or qx + tw > B.shape[1] or qy + th > B.shape[0]:
                continue
            W = B[qy:qy + th, qx:qx + tw]
            W = W - W.mean()
            ws = float(np.sqrt((W * W).sum())) or 1.0
            u = float((T * W).sum()) / (ts * ws)
            if u > v:
                v, best = u, (u, sc, qx, qy)
    v, sc, px, py = best
    return sc, (px - x0 * sc) * f, (py - y0 * sc) * f, v


def prompt_of(k, cell):
    c = S.G.CAST[k]
    text = c[cell]
    era = '' if not S.SET else EF.block(S.SET, k)
    if not S.SET:   # 1001：现今的魔导奇幻
        era = ('This is a present-day magitech fantasy world with electric lamps, trains, rune-engraved brass and glowing crystal cores: the outfit is designed like a modern fantasy game\'s, tailored and layered, sleek and cool rather than medieval, never real-world streetwear. ')
    tail = S.ytail(c) if (S.young(c) or c.get('ya')) else ''
    return EDIT.format(text=text, era=era) + tail


def job(k, cell):
    c = S.G.CAST[k]
    d = wd(k)
    stem = os.path.join(d, cell)
    meta_p = stem + '_meta.json'
    if os.path.exists(meta_p):
        return json.load(open(meta_p, encoding='utf-8'))
    src, kk, ox, oy = make_input(k, cell)
    p = prompt_of(k, cell)
    fig = None
    for attempt in range(2):
        st = stem if attempt == 0 else stem + '_b'
        out = gpt_gen.gen(st, p + (RETRY if attempt else ''), refs=[src], timeout=900)[0]
        figs = CS.figures(CS.clean(Image.open(out)), 1)
        if figs is not None:
            fig = figs[0]
            break
    if fig is None:
        raise RuntimeError('切不开')
    srcim = Image.open(src).convert('RGBA')
    b = head_box(k)
    box = [round(ox + kk * b[0]), round(oy + kk * b[1]), round(ox + kk * b[2]), round(oy + kk * b[3])]
    sc, tx, ty, ncc = align(srcim, fig, box)
    if ncc < LOW_NCC:     # 对不上：脚底对脚底、正中对正中
        fb = fig.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
        sb = srcim.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
        sc, tx, ty = 1.0, 0.0, float(sb[3] - fb[3])
    # out → 格子：x_cell = (x_out − tx)/(sc·kk) − ox/kk
    A = 1 / (sc * kk)
    bx = -tx * A - ox / kk
    by = -ty * A - oy / kk
    W2, H2 = round(fig.width * A), round(fig.height * A)
    r = fig.resize((W2, H2), Image.LANCZOS)
    o = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    o.alpha_composite(r, (max(0, round(bx) + OX), max(0, round(by) + OY)), (max(0, -(round(bx) + OX)), max(0, -(round(by) + OY))))
    o.save(stem + '_fig.png')
    meta = {'en': k, 'cell': cell, 'ncc': round(ncc, 3), 'sc': round(sc, 3), 'k': round(kk, 3)}
    json.dump(meta, open(meta_p, 'w', encoding='utf-8'), ensure_ascii=False)
    return meta


def run(jobs):
    from concurrent.futures import ThreadPoolExecutor
    workers = int(os.environ.get('CAST_WORKERS') or 4)
    res = []
    lock = threading.Lock()

    def one(j):
        if stop.is_set():
            return
        k, cell = j['en'], j['cell']
        t0 = time.time()
        try:
            m = job(k, cell)
            with lock:
                res.append(m)
            print('  好了 %s %s ncc %.3f sc %.3f %ds%s' % (k, cell, m['ncc'], m['sc'], time.time() - t0, '  ←脸？' if m['ncc'] < LOW_NCC else ''), flush=True)
        except Exception as e:   # noqa: BLE001
            log = os.path.join(wd(k), cell + '.log')
            txt = open(log, encoding='utf-8', errors='replace').read() if os.path.exists(log) else ''
            print('  失败 %s %s %s' % (k, cell, str(e)[:120]), flush=True)
            if 'usage_limit' in txt or ' 429' in txt:
                print('== 撞限了，停 %s' % time.strftime('%H:%M', time.gmtime()), flush=True)
                stop.set()

    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(one, jobs))
    print('== 好了 %d / %d' % (len(res), len(jobs)), flush=True)


def sheet(outp, jobs, H=600, per=5):
    F = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
    tiles = []
    for j in jobs:
        k, cell = j['en'], j['cell']
        new = os.path.join(WORK, k, cell + '_fig.png')
        if not os.path.exists(new):
            continue
        meta = json.load(open(os.path.join(WORK, k, cell + '_meta.json'), encoding='utf-8'))
        old = cell_img(k, cell)
        if os.path.exists(os.path.join(ALT, k, '风尚前', 'cell_%s.png' % cell)):
            old = Image.open(os.path.join(ALT, k, '风尚前', 'cell_%s.png' % cell)).convert('RGBA')
        n = Image.open(new).convert('RGBA').crop((OX, OY - 120, OX + CW, OY + CH))
        o = old.copy()
        bo = o.getchannel('A').getbbox()
        bn = n.getchannel('A').getbbox()
        o = o.crop((bo[0], bo[1], bo[2], bo[3]))
        n = n.crop((bn[0], bn[1], bn[2], bn[3]))
        ims = []
        for im in (o, n):
            g = on_grey(im)
            ims.append(g.resize((max(1, round(g.width * H / g.height)), H), Image.LANCZOS))
        w = ims[0].width + ims[1].width + 6
        t = Image.new('RGB', (max(w, 200), H + 28), (20, 20, 26))
        t.paste(ims[0], (0, 28))
        t.paste(ims[1], (ims[0].width + 6, 28))
        flag = '  脸？' if meta['ncc'] < LOW_NCC else ''
        ImageDraw.Draw(t).text((2, 1), '%s %s %s ncc%.2f%s' % (S.G.CAST[k]['name'][:6], k.split('_', 1)[-1], cell[:1], meta['ncc'], flag), font=F, fill=(255, 120, 120) if flag else (255, 230, 160))
        tiles.append(t)
    if not tiles:
        print('没有图')
        return
    TW = max(t.width for t in tiles)
    ROWS = 4
    n = 0
    for at in range(0, len(tiles), per * ROWS):   # 一张至多四行，看得清
        part = tiles[at:at + per * ROWS]
        rows = (len(part) + per - 1) // per
        s = Image.new('RGB', (per * (TW + 8), rows * (H + 34)), (20, 20, 26))
        for i, t in enumerate(part):
            s.paste(t, ((i % per) * (TW + 8), (i // per) * (H + 34)))
        if s.width > 3000:
            s = s.resize((3000, round(s.height * 3000 / s.width)), Image.LANCZOS)
        n += 1
        o = outp if at == 0 and len(tiles) <= per * ROWS else outp.replace('.jpg', '_%d.jpg' % n)
        s.save(o, quality=84)
        print(o, s.size, len(part))


def apply_person(k, cells):
    bak = os.path.join(ALT, k, '风尚前')
    os.makedirs(bak, exist_ok=True)
    d = S.d(k)
    have = [c for c in CELLS if os.path.exists(os.path.join(d, 'cell_%s.png' % c))]   # 神的立绘只有三套（没有战斗服），认实际有的格子
    cur = {c: cell_img(k, c) for c in have}
    figs = {}
    for c in cells:
        o = Image.open(os.path.join(WORK, k, c + '_fig.png')).convert('RGBA')
        bb = o.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
        dy = (OY + CH) - bb[3]                  # 脚踩格底
        figs[c] = (o, bb, dy)
    # 放不放得下：新人的外框，头对正中的格子里
    f = 1.0
    for c, (o, bb, dy) in figs.items():
        top = bb[1] + dy - OY
        left, right = bb[0] - OX, bb[2] - OX
        if top < 0:
            f = min(f, CH / (CH - top))
        half = max(320 - left, right - 320)
        if half > 320:
            f = min(f, 320 / half)
    out = {}
    for c in have:
        if c in figs:
            o, bb, dy = figs[c]
            n = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
            n.alpha_composite(o, (0, dy))
            if f < 1.0:
                w2, h2 = round(OW * f), round(OH * f)
                rr = n.resize((w2, h2), Image.LANCZOS)
                n = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
                n.alpha_composite(rr, (OX + 320 - round((OX + 320) * f), OY + CH - round((OY + CH) * f)))
            out[c] = n.crop((OX, OY, OX + CW, OY + CH))
        elif f < 1.0:
            w2, h2 = round(CW * f), round(CH * f)
            rr = cur[c].resize((w2, h2), Image.LANCZOS)
            n = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
            n.alpha_composite(rr, (320 - round(320 * f), CH - h2))
            out[c] = n
    names = ['cell_%s.png' % c for c in out] + ['sheet.png', 'head.png']
    if 'casual' in cells:
        names += ['art.png', 'art.log', 'art_参考.json', 'faces.png', 'faces.log', 'faces_raw.png']
    for n in names:
        src = os.path.join(d, n)
        if os.path.exists(src) and not os.path.exists(os.path.join(bak, n)):
            shutil.copy2(src, os.path.join(bak, n))
    for c, im in out.items():
        im.save(os.path.join(d, 'cell_%s.png' % c))
    # 设定图拼成一行四格（查图总图用），head 照常服那一格重做
    sh = Image.new('RGBA', (CW * len(have), CH), (0, 0, 0, 0))
    for i, c in enumerate(have):
        sh.alpha_composite(cell_img(k, c), (i * CW, 0))
    sh.save(os.path.join(d, 'sheet.png'))
    if f < 1.0 or 'casual' in cells:
        cell = cell_img(k, 'casual')
        bb = cell.getchannel('A').getbbox()
        h = bb[3] - bb[1]
        a = cell.getchannel('A').crop((0, bb[1], cell.width, bb[1] + h // 8))
        x0, _, x1, _ = a.getbbox()
        cx = (x0 + x1) // 2
        w = h * 22 // 100
        crop = cell.crop((max(0, cx - w // 2), bb[1], min(cell.width, cx + w // 2), bb[1] + w))
        bg = Image.new('RGBA', crop.size, (255, 255, 255, 255))
        bg.alpha_composite(crop)
        bg.convert('RGB').resize((crop.width * 4, crop.height * 4), Image.LANCZOS).save(os.path.join(d, 'head.png'))
    if 'casual' in cells:   # 常服换了，艺术照和九格要跟着重出（gpt_sheet 补缺）
        for n in ('art.png', 'faces.png', 'faces_raw.png'):
            p = os.path.join(d, n)
            if os.path.exists(p):
                os.remove(p)
    return f


def apply_all(jobs, only=None, skip=()):
    by = {}
    for j in jobs:
        if os.path.exists(os.path.join(WORK, j['en'], j['cell'] + '_fig.png')):
            by.setdefault(j['en'], []).append(j['cell'])
    n = 0
    small = []
    for k, cells in by.items():
        if (only and k not in only) or k in skip:
            continue
        f = apply_person(k, cells)
        n += 1
        if f < 0.85:
            small.append((k, round(f, 2)))
    print('换了', n, '位', ('人缩到 0.85 以下：' + str(small)) if small else '')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'run':
        run(json.load(open(a[1], encoding='utf-8')))
    elif a[0] == 'sheet':
        sheet(a[1], json.load(open(a[2], encoding='utf-8')))
    elif a[0] == 'apply':
        only = set(a[a.index('--only') + 1].split(',')) if '--only' in a else None
        skip = set(a[a.index('--skip') + 1].split(',')) if '--skip' in a else set()
        apply_all(json.load(open(a[1], encoding='utf-8')), only, skip)
