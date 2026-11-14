#!/usr/bin/env python3
# 纷争纪的书用的图。要带 PIL 的 Python（ComfyUI 那一个）。先跑 build_data.py（人的名单从 data/strife.json 里读）。
#   python prep_assets.py            都做
#   python prep_assets.py cards      二十二张牌面和牌背（assets/card/，带透明的拱窗形）
#   python prep_assets.py road       路的长卷十一段（assets/road/），量出头一段左边、末一段右边的颜色写进 data/roadc.json
#   python prep_assets.py por        时代页里的人像拼图，一张牌一张（assets/pa/），神和魔神用神明显像
#   python prep_assets.py spr        档案页的立绘加表情，一人一张（assets/ps/），神和魔神的显像（assets/god/）
#   python prep_assets.py cg         时代原画、节点原画、死的那一刻、传奇之陨（照 cg_table.json），写 data/cg.json
import io
import json
import os
import sys

from PIL import Image, ImageFilter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
COMFY = os.path.normpath(os.path.join(HERE, '..', '..', '状态栏', 'comfy'))
SRC = os.path.join(COMFY, 'out', '门面_原画_纷争纪')
ASSETS = os.path.join(HERE, 'assets')
PSET_DIR = {'1001': '立绘_v3'}
GODS = os.path.join(COMFY, 'out', '神明显像')


def data():
    return json.load(open(os.path.join(HERE, 'data', 'strife.json'), encoding='utf-8'))


def fresh(dst, *srcs):
    return os.path.exists(dst) and all(os.path.getmtime(dst) >= os.path.getmtime(s) for s in srcs)


NW, NH = 1120, 1680          # 归一以后的画布（最后缩成 800×1200）
HALF, FOOT_Y = 258, 1610     # 石框两根边柱外沿之间的半宽、尖脚落在哪一行


def frame_of(a):
    """量一张牌里石框在哪：回 (中线 x, 边柱外沿的半宽, 尖脚 y)。模型照样板重画的框，大小差到一成多、位置也不一样，要归一。
    边柱外沿：一行里从外往里头一段连着十八个石头色的像素。溢出框的东西多半不是石头色、也多半只占几行，所以取各行里出现最多的那个位置；
    一边叫东西挡得厉害的，照另一边和中线算（各张牌的中线都在 509 到 511）。尖脚：中线上最低的石头色像素。"""
    import numpy as np
    H, W = a.shape[:2]
    rgb = a[..., :3].astype(int)
    st = (a[..., 3] > 200) & (rgb.mean(-1) > 150) & (rgb.max(-1) - rgb.min(-1) < 30)
    run = 18
    c = np.cumsum(np.pad(st, ((0, 0), (1, 0))), axis=1)
    full = (c[:, run:] - c[:, :-run]) == run
    ls, rs = [], []
    for y in range(int(H * .30), int(H * .66)):
        xs = np.flatnonzero(full[y])
        if len(xs):
            if 150 <= xs[0] <= 400:
                ls.append(xs[0])
            if 620 <= xs[-1] + run - 1 <= 880:
                rs.append(xs[-1] + run - 1)

    def mode(vals):
        if not vals:
            return 0, 0
        k = np.convolve(np.bincount(np.array(vals, dtype=int), minlength=W), np.ones(5), 'same')
        return int(k.argmax()), int(k.max())
    (xl, nl), (xr, nr) = mode(ls), mode(rs)
    if nl >= 60 and nr >= 60:
        xc, half = (xl + xr) / 2, (xr - xl) / 2
    elif nl >= 60:
        xc, half = 510, 510 - xl
    elif nr >= 60:
        xc, half = 510, xr - 510
    else:
        return None
    ys = np.flatnonzero(st[:, int(xc) - 5:int(xc) + 6].any(axis=1))
    return xc, half, int(ys[-1])


def norm_card(src):
    """第二版的牌是抠出来的拱窗形（透明底）。很淡的杂点清掉；照石框归一（同一个大小，尖脚落在同一处）；
    画到原图边上叫边切断的东西（吊石头的绳、日头的光芒）在边上淡出去。回 1120×1680 的图和缩放了多少。"""
    import numpy as np
    im = Image.open(src).convert('RGBA')
    if im.size != (1024, 1536):
        print('尺寸不对', os.path.basename(src), im.size)
        im = im.resize((1024, 1536), Image.LANCZOS)
    a = np.array(im)
    H, W = a.shape[:2]
    al = a[..., 3].astype(float)
    al[al < 12] = 0
    xs, ys = np.arange(W)[None, :], np.arange(H)[:, None]
    ramp = np.minimum(1, np.minimum(np.minimum(xs, W - 1 - xs), np.minimum(ys, H - 1 - ys)) / 22.0)
    a[..., 3] = (al * ramp).astype(np.uint8)
    fr = frame_of(a)
    if fr is None:
        print('量不出石框，照样板的位置放', os.path.basename(src))
        fr = (510, 262, 1480)
    xc, half, yf = fr
    s = HALF / half
    sm = Image.fromarray(a, 'RGBA').resize((round(W * s), round(H * s)), Image.LANCZOS)
    x, y = round(NW / 2 - xc * s), round(FOOT_Y - yf * s)
    box = (max(0, -x), max(0, -y), min(sm.width, NW - x), min(sm.height, NH - y))
    if box != (0, 0, sm.width, sm.height):
        print('  出了画布，裁掉一点', os.path.basename(src), box, sm.size)
    cv = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
    cv.alpha_composite(sm.crop(box), (max(0, x), max(0, y)))
    return cv, round(s, 3)


def finish_card(cv):
    """垫一圈暗影烘进图里（立在路的画上跟底下分得开，页面上不用滤镜），缩成 800×1200。"""
    sh = cv.getchannel('A').filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.6))
    base = Image.new('RGBA', cv.size, (5, 6, 11, 0))
    base.paste(Image.new('RGBA', cv.size, (5, 6, 11, 255)), (0, 8), sh)
    base.alpha_composite(cv)
    return base.resize((800, 1200), Image.LANCZOS)


KAI = 'C:/Windows/Fonts/simkai.ttf'      # 楷体：页边那一行是一只手写在牌上的
FS_MAX, FS_MIN, LS = 27, 15, 0.10      # 刻字最大、最小的字号（归一画布上的像素），字距是字号的一成


def ribbon_of(a):
    """量缎带当中那一段在哪。回 dict：fit（中线 y 关于 x-560 的二次式系数）、h（缎带高的中位数）、free（没叫东西挡住的那一段 x 范围）、
    stud（当中那颗圆钉的 (x, y, r)，没有就是 None）、rib（缎带色的像素）。量不出来回 None。
    缎带是全图最亮最素的一条（亮度两百上下、几乎没有饱和度），它底下是压着阴影的石脚，上头是窗里的画。模型每张画的缎带高低差十几个像素，所以逐张量。"""
    import numpy as np
    rgb = a[..., :3].astype(int)
    lum, sat = rgb.mean(-1), rgb.max(-1) - rgb.min(-1)
    rib = (a[..., 3] > 200) & (lum >= 196) & (sat <= 14)
    cx, y0, y1 = NW // 2, FOOT_Y - 300, FOOT_Y - 80

    def runs(x):
        col = rib[y0:y1, x]
        out, s, gap = [], None, 0
        for i, v in enumerate(col):
            if v:
                if s is None:
                    s = i
                gap = 0
            elif s is not None:
                gap += 1
                if gap > 2:               # 两个像素以内的断口不算断
                    out.append((s + y0, i - gap + y0))
                    s, gap = None, 0
        if s is not None:
            out.append((s + y0, len(col) - 1 - gap + y0))
        return [r for r in out if r[1] - r[0] >= 30]

    seed = []
    for x in (cx - 60, cx - 48, cx + 48, cx + 60):
        r = [q for q in runs(x) if 55 <= q[1] - q[0] <= 130]
        if r:
            seed.append(max(r, key=lambda q: q[1] - q[0]))
    if len(seed) < 2:
        return None
    c0 = float(np.median([(t + b) / 2 for t, b in seed]))
    h0 = float(np.median([b - t for t, b in seed]))
    cols = {}
    for step in (-3, 3):
        x, c, miss = cx + (48 if step > 0 else -48), c0, 0
        while 250 < x < NW - 250 and miss < 4:
            r = [q for q in runs(x) if q[0] - 14 <= c <= q[1] + 14]
            if r:
                t, b = max(r, key=lambda q: q[1] - q[0])
                cols[x] = (t, b)
                if abs((b - t) - h0) < h0 * .1:
                    c, miss = (t + b) / 2, 0
                else:
                    miss += 0 if (b - t) > h0 * .55 else 1
            else:
                miss += 1
            x += step
    good = [(x, (t + b) / 2) for x, (t, b) in cols.items() if abs((b - t) - h0) < h0 * .1]
    if len(good) < 20:
        return None
    gx, gy = np.array([g[0] - cx for g in good], float), np.array([g[1] for g in good], float)
    fit = np.polyfit(gx, gy, 2)
    keep = np.abs(np.polyval(fit, gx) - gy) < 5
    fit = np.polyfit(gx[keep], gy[keep], 2)
    yc = lambda x: float(np.polyval(fit, x - cx))
    # 圆钉：中线附近、缎带里头不是缎带色的一小团（连成一片、不挨着缎带上下沿的；挨着的是画里压上来的东西）
    stud = None
    wy0, wy1 = int(yc(cx) - h0 / 2 + 5), int(yc(cx) + h0 / 2 - 5)
    wx0, wx1 = cx - 70, cx + 70
    nr = ~rib[wy0:wy1, wx0:wx1]
    seen = np.zeros_like(nr)
    best = None
    for sy, sx in zip(*np.nonzero(nr)):
        if seen[sy, sx]:
            continue
        stack, pts = [(sy, sx)], []
        seen[sy, sx] = True
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < nr.shape[0] and 0 <= xx < nr.shape[1] and nr[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
        py, px = [p[0] for p in pts], [p[1] for p in pts]
        w, hh = max(px) - min(px) + 1, max(py) - min(py) + 1
        if not (8 <= w <= 46 and 8 <= hh <= 46) or min(py) == 0 or max(py) == nr.shape[0] - 1:
            continue
        bx, by = (max(px) + min(px)) / 2 + wx0, (max(py) + min(py)) / 2 + wy0
        dist = abs(bx - cx) + abs(by - yc(cx))
        if dist < 34 and (best is None or dist < best[0]):
            best = (dist, (bx, by, max(w, hh) / 2))
    if best:
        stud = best[1]
    return {'fit': fit, 'h': h0, 'cols': cols, 'stud': stud, 'rib': rib, 'yc': yc}


def engrave(cv, line):
    """把这一张牌的页边那一行顺着缎带的弧刻上去（月谕圣牌的缎带上有一行很淡的字）。当中那颗圆钉抹掉，字居中排一行；
    缎带叫画里的东西压住的那一截不刻，字排在没压住的那一段里，放不下最小字号就不刻。回 (图, 说明)。"""
    import math

    import numpy as np
    from PIL import ImageDraw, ImageFont
    a = np.array(cv)
    rb = ribbon_of(a)
    if rb is None:
        return cv, '量不出缎带，没刻'
    cx, yc, h0, rib = NW // 2, rb['yc'], rb['h'], rb['rib']
    if rb['stud']:                      # 抹掉圆钉：拿它左右两边的缎带镜像过来，左右渐变着拼
        sx, sy, sr = rb['stud']
        R = int(sr + 8)
        x0, x1 = int(sx - R), int(sx + R)
        for y in range(int(sy - R), int(sy + R) + 1):
            for x in range(x0, x1 + 1):
                if (x - sx) ** 2 + (y - sy) ** 2 > R * R:
                    continue
                xl, xr = x0 - 1 - (x - x0), x1 + 1 + (x1 - x)
                w = (x - x0) / max(1, x1 - x0)
                okl, okr = rib[y, xl], rib[y, xr]
                if okl and okr:
                    a[y, x] = (a[y, xl].astype(float) * (1 - w) + a[y, xr].astype(float) * w).astype(np.uint8)
                elif okl or okr:
                    a[y, x] = a[y, xl if okl else xr]
                else:
                    continue
                rib[y, x] = True
    text = line.strip().rstrip('。')
    n = sum(1 for c in text if c not in '，。')

    def units(t):                       # 一截字有多宽，拿字号当单位
        return (sum(1 for c in t if c not in '，。') + .45 * t.count('，') + .9 * t.count('。')) * (1 + LS)

    def spans(fs, rows=1):              # 字那一条（上下各留五个像素）整条落在缎带色里的几段 x 范围；三个像素以内的断口不算断
        half = (fs * rows + 6 * (rows - 1)) / 2 + 5
        ok = [bool(rib[int(yc(x) - half):int(yc(x) + half) + 1, x].all()) for x in range(260, NW - 260)]
        out, st, gap = [], None, 0
        for i, v in enumerate(ok):
            if v:
                if st is None:
                    st = i
                gap = 0
            elif st is not None:
                gap += 1
                if gap > 3:
                    out.append((st + 260, i - gap + 260))
                    st, gap = None, 0
        if st is not None:
            out.append((st + 260, len(ok) - 1 - gap + 260))
        return [q for q in out if q[1] - q[0] >= 3 * fs]

    def one(fs):                        # 整行排在一段里：挑离中线最近的那一段
        fit = [q for q in spans(fs) if q[1] - q[0] - 24 >= units(text) * fs]
        if not fit:
            return None
        q = min(fit, key=lambda q: abs((q[0] + q[1]) / 2 - cx))
        return [(text, q, 0)]

    def two(fs):                        # 照句子（没有句号就照逗号）分成前后两截，排在前后两段里
        sp = spans(fs)
        cuts = [i for i, c in enumerate(text) if c == '。'] or [i for i, c in enumerate(text) if c == '，']
        best = None
        for i in cuts:
            l, r = text[:i], text[i + 1:]
            for p in range(len(sp)):
                for q in range(p + 1, len(sp)):
                    if sp[p][1] - sp[p][0] - 20 >= units(l) * fs and sp[q][1] - sp[q][0] - 20 >= units(r) * fs:
                        gapw = sp[q][0] - sp[p][1]
                        if best is None or gapw < best[0]:
                            best = (gapw, [(l, sp[p], 0), (r, sp[q], 0)])
        return best and best[1]

    def stack(fs):                      # 同一段里上下排两行（缎带当中叫东西压住、只剩一头空着的时候）
        cuts = [i for i, c in enumerate(text) if c == '。'] or [i for i, c in enumerate(text) if c == '，']
        for i in sorted(cuts, key=lambda i: abs(units(text[:i]) - units(text[i + 1:]))):
            l, r = text[:i], text[i + 1:]
            fit = [q for q in spans(fs, 2) if q[1] - q[0] - 20 >= max(units(l), units(r)) * fs]
            if fit:
                q = min(fit, key=lambda q: abs((q[0] + q[1]) / 2 - cx))
                return [(l, q, -(fs + 6) / 2), (r, q, (fs + 6) / 2)]
        return None

    plan, fs = None, FS_MAX
    f1 = next((f for f in range(FS_MAX, FS_MIN - 1, -1) if one(f)), None)
    f2 = next((f for f in range(FS_MAX, FS_MIN - 1, -1) if two(f)), None)
    f3 = next((f for f in range(min(FS_MAX, 22), FS_MIN - 1, -1) if stack(f)), None)
    if f1 and f1 >= min(max(f2 or 0, f3 or 0), 19):
        plan, fs = one(f1), f1
    elif f2 and f2 >= (f3 or 0):
        plan, fs = two(f2), f2
    elif f3:
        plan, fs = stack(f3), f3
    if plan is None:
        return Image.fromarray(a, 'RGBA'), '缎带上空着的几段 %s，%d 个字放不下，没刻' % (spans(FS_MIN), n)
    SS = 3
    font = ImageFont.truetype(KAI, fs * SS)
    mask = np.zeros(a.shape[:2], float)

    def put(g, x, y):                   # 把一小块字的蒙版贴到 (x, y) 为中心的地方，取大
        gh, gw = g.shape
        t, l = int(round(y - gh / 2)), int(round(x - gw / 2))
        mask[t:t + gh, l:l + gw] = np.maximum(mask[t:t + gh, l:l + gw], g)

    for chunk, (xl, xr), dy in plan:
        total = units(chunk) * fs
        want = cx if len(plan) == 1 else (xl + xr) / 2
        mid = min(max(want, xl + 10 + total / 2), xr - 10 - total / 2)
        x = mid - total / 2
        for c in chunk:
            if c == '，':
                x += .45 * (1 + LS) * fs
                continue
            if c == '。':               # 句与句之间刻一个小点
                xm = x + .45 * (1 + LS) * fs
                d = Image.new('L', (fs * SS, fs * SS), 0)
                r = fs * SS * .075
                ImageDraw.Draw(d).ellipse([fs * SS / 2 - r, fs * SS / 2 - r, fs * SS / 2 + r, fs * SS / 2 + r], fill=255)
                put(np.asarray(d.resize((fs, fs), Image.LANCZOS), float) / 255, xm, yc(xm) + dy)
                x += .9 * (1 + LS) * fs
                continue
            xm = x + (1 + LS) * fs / 2
            slope = 2 * rb['fit'][0] * (xm - cx) + rb['fit'][1]
            g = Image.new('L', (fs * SS * 2, fs * SS * 2), 0)
            ImageDraw.Draw(g).text((fs * SS, fs * SS), c, font=font, fill=255, anchor='mm')
            g = g.rotate(-math.degrees(math.atan(slope)), resample=Image.BICUBIC).resize((fs * 2, fs * 2), Image.LANCZOS)
            put(np.asarray(g, float) / 255, xm, yc(xm) + dy)
            x += (1 + LS) * fs
    how = '排在 %d 到 %d' % plan[0][1] if len(plan) == 1 else ('上下两行排在 %d 到 %d' % plan[0][1] if plan[0][2] else '分两截排在 %s 和 %s' % (plan[0][1], plan[1][1]))
    mask *= rib                         # 只刻在缎带上
    rgbf = a[..., :3].astype(float)
    hi = np.zeros_like(mask)            # 刻痕右下那一道亮边
    hi[2:, 1:] = mask[:-2, :-1]
    hi = np.clip(hi - mask, 0, 1) * rib
    dark = np.array([92, 96, 112], float)
    rgbf = rgbf * (1 - mask[..., None] * .68) + dark * (mask[..., None] * .68)
    rgbf = rgbf + (255 - rgbf) * (hi[..., None] * .55)
    a[..., :3] = np.clip(rgbf, 0, 255).astype(np.uint8)
    return Image.fromarray(a, 'RGBA'), '刻了 %d 个字，字号 %d，%s' % (n, fs, how)


def cut_card(src, line=''):
    cv, s = norm_card(src)
    note = ''
    if line:
        cv, note = engrave(cv, line)
    return finish_card(cv), s, note


def cards():
    dst_dir = os.path.join(ASSETS, 'card')
    os.makedirs(dst_dir, exist_ok=True)
    n = tot = 0
    scale = {}
    d = data()
    lines = {'c%02d' % (i + 1): e['card'].get('margin', '') for i, e in enumerate(d['eras'])}      # 缎带上刻这一张的页边那一行
    lines['c22'] = d['last'].get('margin', '')
    for k in ['c%02d' % i for i in range(1, 23)] + ['cb0']:
        p = os.path.join(SRC, k + '.png')
        if not os.path.exists(p):
            print('还没有', k)
            continue
        dst = os.path.join(dst_dir, ('back' if k == 'cb0' else k) + '.webp')     # 牌背是同一扇石窗关着（cb0），缎带上不刻字
        if not fresh(dst, p, __file__):
            im, scale[k], note = cut_card(p, lines.get(k, ''))
            im.save(dst, 'WEBP', quality=88, method=6)
            if note:
                print(' ', k, note)
        n += 1
        tot += os.path.getsize(dst)
    # 归一以后每张牌的尖脚都在图高的同一处，页面照这个数把牌脚落在路边的空地上
    open(os.path.join(HERE, 'data', 'card.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps({'foot': round(FOOT_Y / NH, 4), 'half': round(HALF / NW, 4)}, separators=(',', ':')) + '\n')
    print('牌面连牌背', n, '张，', tot // 1024, 'KB，写了 data/card.json；这一回重做的缩放', scale)


def edge(im, x0, x1):
    """一条竖带的平均色。"""
    w, h = im.size
    box = im.crop((int(w * x0), int(h * .2), max(int(w * x0) + 1, int(w * x1)), int(h * .9))).resize((1, 1), Image.BOX)
    return list(box.getpixel((0, 0)))


ROADV = '_v2'        # 11-13 十道接缝重画成一条连着的路以后换了文件名，浏览器不拿旧图（index.html 的 ROADV 跟着改）


def road():
    dst_dir = os.path.join(ASSETS, 'road')
    os.makedirs(dst_dir, exist_ok=True)
    out, tot = {}, 0
    for i in range(1, 12):
        k = 'r%02d' % i
        p = os.path.join(SRC, k + '.png')
        if not os.path.exists(p):
            print('还没有', k)
            continue
        im = Image.open(p).convert('RGB')
        if im.size != (1536, 1024):
            print('尺寸不对', k, im.size)
        dst = os.path.join(dst_dir, k + ROADV + '.webp')
        if not fresh(dst, p):
            im.save(dst, 'WEBP', quality=84, method=6)
        out[k] = {'l': edge(im, 0, .02), 'r': edge(im, .98, 1), 'sky': edge(im.crop((0, 0, im.width, int(im.height * .09))), 0, 1)}
        tot += os.path.getsize(dst)
        print(k, os.path.getsize(dst) // 1024, 'KB', out[k])
    open(os.path.join(HERE, 'data', 'roadc.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(out, separators=(',', ':')) + '\n')
    print('长卷', len(out), '段，', tot // 1024, 'KB，写了 data/roadc.json')


PW, PH, PCOLS = 300, 450, 8


def art_of(c):
    if c.get('pset') == '神明显像':
        return os.path.join(GODS, c['key'] + '.png')
    return os.path.join(COMFY, 'out', PSET_DIR.get(c['pset'], '立绘_' + c['pset']), 'art', 'art_' + c['key'] + '.webp')


def por():
    """时代页里的人像：一张牌一张拼图 assets/pa/牌.webp（旅伴、相遇、传奇、神与魔神，一格 300×450，一行八格），哪一格是谁写进 data/pa.json。"""
    dst_dir = os.path.join(ASSETS, 'pa')
    os.makedirs(dst_dir, exist_ok=True)
    out, total, miss = {}, 0, 0
    for e in data()['eras']:
        keys, srcs = [], []
        for c in e['cast'] + e.get('meet', []) + e.get('legends', []) + e.get('gods', []):
            if not c.get('key') or c['key'] in keys:
                continue
            src = art_of(c)
            if not os.path.exists(src):
                print('没有图', e['id'], c['name'], src)
                miss += 1
                continue
            keys.append(c['key'])
            srcs.append(src)
        if not keys:
            continue
        cols = min(PCOLS, len(keys))
        rows = (len(keys) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * PW, rows * PH), (18, 19, 26))
        for i, src in enumerate(srcs):
            sheet.paste(Image.open(src).convert('RGB').resize((PW, PH), Image.LANCZOS), (i % cols * PW, i // cols * PH))
        dst = os.path.join(dst_dir, e['id'] + '.webp')
        sheet.save(dst, 'WEBP', quality=82, method=6)
        out[e['id']] = {'c': cols, 'r': rows, 'k': keys}
        total += os.path.getsize(dst)
    open(os.path.join(HERE, 'data', 'pa.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(out, separators=(',', ':')) + '\n')
    print('人像拼图：', len(out), '张，', total // 1024, 'KB；缺', miss, '，写了 data/pa.json')


def spr():
    """档案页用的图，一人一张 assets/ps/键.webp（2560×1216）：上面一行四套衣服，下面一行九格表情。神和魔神的显像另存 assets/god/键.webp。
    备了哪些写进 data/have.json。未穿甲的诺伦那一套不在名单里（build_data.py 不收），这里再挡一道。"""
    dst_dir, god_dir = os.path.join(ASSETS, 'ps'), os.path.join(ASSETS, 'god')
    os.makedirs(dst_dir, exist_ok=True)
    os.makedirs(god_dir, exist_ok=True)
    have, gods, total = [], [], 0
    for e in data()['eras']:
        for c in e['cast'] + e.get('meet', []) + e.get('legends', []):      # 传奇的档案也看立绘和表情（11-12）
            k = c.get('key')
            if not k or k in have or k.endswith('_bare'):
                continue
            art = os.path.join(COMFY, 'out', PSET_DIR.get(c['pset'], '立绘_' + c['pset']), 'art')
            a, b = os.path.join(art, 'por_' + k + '.webp'), os.path.join(art, 'face_' + k + '.webp')
            if not os.path.exists(a) or not os.path.exists(b):
                print('没有', e['id'], c['name'], a if not os.path.exists(a) else b)
                continue
            dst = os.path.join(dst_dir, k + '.webp')
            if not fresh(dst, a, b):
                row = Image.open(a).convert('RGBA')
                face = Image.open(b).convert('RGBA')
                if row.size != (2560, 960) or face.size != (768, 768):
                    print('尺寸不对', k, row.size, face.size)
                    continue
                sheet = Image.new('RGBA', (2560, 1216), (0, 0, 0, 0))
                sheet.paste(row, (0, 0))
                for i in range(9):
                    sheet.paste(face.crop((i % 3 * 256, i // 3 * 256, i % 3 * 256 + 256, i // 3 * 256 + 256)), (i * 256, 960))
                sheet.save(dst, 'WEBP', quality=88, method=6)
            have.append(k)
            total += os.path.getsize(dst)
        for g in e.get('gods', []):
            k = g.get('key')
            if not k or k in gods:
                continue
            src = os.path.join(GODS, k + '.png')
            if not os.path.exists(src):
                print('没有显像', g['name'], k)
                continue
            dst = os.path.join(god_dir, k + '.webp')
            if not fresh(dst, src):
                Image.open(src).convert('RGB').resize((768, 1152), Image.LANCZOS).save(dst, 'WEBP', quality=84, method=6)
            gods.append(k)
            total += os.path.getsize(dst)
    open(os.path.join(HERE, 'data', 'have.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps({'ps': sorted(have), 'god': sorted(gods)}, separators=(',', ':')) + '\n')
    print('立绘加表情', len(have), '张，显像', len(gods), '张，', total // 1024, 'KB，写了 data/have.json')


def cg():
    """时代原画、节点原画、死的那一刻（comfy/gpt_cg2.py 出的）。哪一幅配哪一条主线的哪一幕、叫什么，照 cg_table.json（scenes/merge_scenes.py 并出来的）；图还没出的那一行跳过。"""
    table = json.load(open(os.path.join(HERE, 'cg_table.json'), encoding='utf-8'))
    dst_dir = os.path.join(ASSETS, 'cg')
    os.makedirs(dst_dir, exist_ok=True)
    out, total, n, lack = {}, 0, 0, []
    for stem, t in table.items():
        base = t.get('src', stem)
        src = os.path.join(SRC, base + '.png')
        if not os.path.exists(src):
            lack.append(stem)
            continue
        rev = table.get(base, t).get('rev')
        name = base + ('_r%d' % rev if rev else '')      # 重画过的换一个文件名发，免得浏览器还拿着旧图
        dst = os.path.join(dst_dir, name + '.webp')
        if not fresh(dst, src):
            im = Image.open(src).convert('RGB')
            if im.width > 1536:
                im = im.resize((1536, round(im.height * 1536 / im.width)), Image.LANCZOS)
            im.save(dst, 'WEBP', quality=86, method=6)
        total += os.path.getsize(dst)
        n += 1
        era = out.setdefault(stem.split('_')[0], {'nodes': {}})
        rel = 'assets/cg/%s.webp' % name
        if t.get('key'):
            era['key'] = {'src': rel}
        elif t.get('death'):
            era.setdefault('deaths', {})[t['death']] = {'src': rel, 'name': t.get('name', '')}
        elif t.get('fall'):           # 传奇之陨：时代页上单排一栏，传奇的档案里也有
            era.setdefault('falls', {})[t['fall']] = {k: v for k, v in (('src', rel), ('name', t.get('name', '')), ('when', t.get('when', '')), ('where', t.get('where', '')), ('label', t.get('label', ''))) if v}
        else:
            slot, item = era['nodes'].setdefault(t['line'], {}), {'src': rel, 'name': t.get('name', '')}
            if t['act'] in slot:
                prev = slot[t['act']]
                slot[t['act']] = (prev if isinstance(prev, list) else [prev]) + [item]
            else:
                slot[t['act']] = item
    open(os.path.join(HERE, 'data', 'cg.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n')
    print('写了 data/cg.json：', n, '幅，', total // 1024, 'KB；还没出图的', len(lack), '幅', ' '.join(lack[:12]) + (' …' if len(lack) > 12 else ''))


if __name__ == '__main__':
    what = sys.argv[1:] or ['cards', 'road', 'por', 'spr', 'cg']
    for name, fn in (('cards', cards), ('road', road), ('spr', spr), ('por', por), ('cg', cg)):
        if name in what:
            fn()
