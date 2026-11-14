# 纷争纪的长卷：照页面的拼法（一段 1536 宽、相邻两段叠 7.5%、后一段左边渐显）把十一段拼成一整条，看接缝、切接缝那一块。
#   python road_strip.py strip <输出.jpg> [高]          整条拼出来（缩到给定的高，默认 256），看路在哪里断
#   python road_strip.py joins <输出目录>                十道接缝各切一块（以接缝为中心、原尺寸 1536×1024，jNN_in.png），给 gpt_cg2.py 的 jNN 当底
# 原图在 comfy/out/门面_原画_纷争纪/rNN.png（要带 PIL、numpy 的 Python）
import io
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', '..', '状态栏', 'comfy', 'out', '门面_原画_纷争纪'))
NP, PW, PH = 11, 1536, 1024
OV = round(PW * 0.075)          # 页面上相邻两段叠多少（index.html 的 OV）
STEP = PW - OV


def seg(k, name=None):
    return np.asarray(Image.open(os.path.join(SRC, (name or 'r%02d' % (k + 1)) + '.png')).convert('RGB'), dtype=np.float32)


def build(segs=None):
    """照页面的叠法拼成一整条：后一段左边 OV 宽从透明渐到不透明，压在前一段上。"""
    W = STEP * (NP - 1) + PW
    out = np.zeros((PH, W, 3), np.float32)
    for k in range(NP):
        im = seg(k) if segs is None else segs[k]
        x0 = k * STEP
        if k == 0:
            out[:, x0:x0 + PW] = im
            continue
        a = np.ones((1, PW, 1), np.float32)
        a[0, :OV, 0] = np.linspace(0, 1, OV, endpoint=False)
        out[:, x0:x0 + PW] = out[:, x0:x0 + PW] * (1 - a) + im * a
    return out


def junction_x(j):
    """第 j 道接缝（1..10，第 j 段和第 j+1 段之间）在整条上的正中。"""
    return j * STEP + OV // 2


# 重画出来的那一块跟原来的两头不会一像素不差：先找整体挪了几像素、颜色偏了多少，再在两边各找一道差得最少的缝接上
EDGE_L, EDGE_R = (96, 470), (1066, 1440)        # 两边拿来比对、找缝的范围（当中 512..1024 是重画的那三分之一，留一点余量）


def outer_mask():
    m = np.zeros(PW, bool)
    m[EDGE_L[0]:EDGE_L[1]] = True
    m[EDGE_R[0]:EDGE_R[1]] = True
    return m


def fit(G, W):
    """把 G 对齐到 W：整像素平移（先粗后细），再逐通道做一次线性的颜色校正。只拿两边的那几块算。"""
    m = outer_mask()
    g, w = G.mean(2), W.mean(2)
    best = (1e18, 0, 0)
    for dy in range(-24, 25, 4):
        for dx in range(-24, 25, 4):
            d = np.abs(np.roll(np.roll(g, dy, 0), dx, 1)[48:-48:4, :][:, m[::1]][:, ::4] - w[48:-48:4, :][:, m][:, ::4]).mean()
            if d < best[0]:
                best = (d, dx, dy)
    _, bx, by = best
    for dy in range(by - 4, by + 5):
        for dx in range(bx - 4, bx + 5):
            d = np.abs(np.roll(np.roll(g, dy, 0), dx, 1)[48:-48:2, :][:, m][:, ::2] - w[48:-48:2, :][:, m][:, ::2]).mean()
            if d < best[0]:
                best = (d, dx, dy)
    d0, dx, dy = best
    G = np.roll(np.roll(G, dy, 0), dx, 1)
    # 挪出去的边拿 W 补上（只会是外侧几像素）
    if dx > 0:
        G[:, :dx] = W[:, :dx]
    elif dx < 0:
        G[:, dx:] = W[:, dx:]
    if dy > 0:
        G[:dy] = W[:dy]
    elif dy < 0:
        G[dy:] = W[dy:]
    gains = []
    for ch in range(3):
        a, b = np.polyfit(G[48:-48, m, ch].ravel()[::7], W[48:-48, m, ch].ravel()[::7], 1)
        G[..., ch] = G[..., ch] * a + b
        gains.append((round(float(a), 3), round(float(b), 1)))
    after = np.abs(G[:, m] - W[:, m]).mean()
    return G, '挪了 (%d, %d)，差 %.1f → %.1f，颜色 %s' % (dx, dy, d0, after, gains)


def seam(cost):
    """从上到下一条竖缝，每行最多横挪一像素，走差最小的那条路（动态规划）。返回每行缝在哪一列。"""
    h, w = cost.shape
    acc = cost.copy()
    back = np.zeros((h, w), np.int8)
    for y in range(1, h):
        prev = acc[y - 1]
        l = np.r_[np.inf, prev[:-1]]
        r = np.r_[prev[1:], np.inf]
        stack = np.vstack([l, prev, r])
        i = stack.argmin(0)
        acc[y] += stack[i, np.arange(w)]
        back[y] = i - 1
    x = np.empty(h, int)
    x[-1] = int(acc[-1].argmin())
    for y in range(h - 1, 0, -1):
        x[y - 1] = x[y] + back[y, x[y]]
    return x


def stitch(G, W, feather=10):
    """左缝以左、右缝以右用旧图 W，两缝之间用重画的 G，缝两边各羽化 feather 像素。"""
    diff = np.abs(G - W).sum(2)
    k = np.ones(9) / 9
    diff = np.apply_along_axis(lambda r: np.convolve(r, k, 'same'), 1, diff)
    xl = seam(diff[:, EDGE_L[0]:EDGE_L[1]]) + EDGE_L[0]
    xr = seam(diff[:, EDGE_R[0]:EDGE_R[1]]) + EDGE_R[0]
    cols = np.arange(PW)[None, :]
    a = np.clip((cols - xl[:, None] + feather) / (2 * feather), 0, 1) * np.clip((xr[:, None] + feather - cols) / (2 * feather), 0, 1)
    return W * (1 - a[..., None]) + G * a[..., None]


# ---------- 小改 ----------
# 十道接缝并上以后，还有几处路断在半路、或者多出一截通到哪儿都不去的路（多半是原来每一段里自带的岔路、勾子）。
# 拿接好的那一块当底（pNN_in.png，cutp 切），叫 GPT 只改那一处（gpt_cg2.py 的 pNN），再贴回去：
# 只在给定的框里、跟底图差得多的地方用新图，往外扩一圈、羽化。框是窗口里的百分比（左, 上, 右, 下），框跟别的小改的框不重叠。
# 框后头写 'full' 的：框里整块用新图（白草地上的路跟地差得少，照差多少挑会漏掉没擦干净的旧路）；不写的照差多少挑。
PATCHES = [
    ('p02', 2, [(6, 3, 30, 40, 'full'), (40, 46, 62, 68)]),  # 接缝二：路弯上多出来往左上去的一截；左上通到牌那块空地的小路，牌后头多出来的一截
    ('p03', 3, [(16, 52, 56, 86)]),                        # 接缝三：门那一排过来的路断在两辆篷车边上，接到山口城门下来的那条路
    ('p04', 4, [(10, 18, 48, 66)]),                        # 接缝四：左下来的路断在半路；上头一截勾子通到哪儿都不去
    ('p05', 5, [(18, 18, 46, 50)]),                        # 接缝五：左上一截勾子通到哪儿都不去
    ('p06', 6, [(14, 15, 58, 56), (42, 12, 60, 32, 'full')]),  # 接缝六：左边来的路断在半路；上头一截勾子通到哪儿都不去（火车边上那一头在白草地上，整块用新图）
    ('p06b', 6, [(25, 36, 42, 56)]),                       # 接缝六第二回：接上的那一截从一匹白马脚底下穿过去，把马拿掉
    ('p09', 9, [(52, 60, 82, 100)]),                       # 接缝九：路分了岔，一支往下出了画
]
PATCH_T = 40          # 框里跟底图平均差多少算改了的地方（0..255，先模糊过）


def patch_x0(j):
    return junction_x(j) - PW // 2


def fit_mask(G, W, m2d):
    """跟 fit 一样，只是拿一张二维的掩码（True 的地方）来比对、校颜色。"""
    g, w = G.mean(2), W.mean(2)

    def score(dx, dy, st):
        gg = np.roll(np.roll(g, dy, 0), dx, 1)[::st, ::st]
        mm = m2d[::st, ::st]
        return np.abs(gg[mm] - w[::st, ::st][mm]).mean()

    best = (score(0, 0, 4), 0, 0)
    for dy in range(-24, 25, 4):
        for dx in range(-24, 25, 4):
            d = score(dx, dy, 4)
            if d < best[0]:
                best = (d, dx, dy)
    _, bx, by = best
    for dy in range(by - 4, by + 5):
        for dx in range(bx - 4, bx + 5):
            d = score(dx, dy, 2)
            if d < best[0]:
                best = (d, dx, dy)
    d0, dx, dy = best
    G = np.roll(np.roll(G, dy, 0), dx, 1)
    gains = []
    for ch in range(3):
        a, b = np.polyfit(G[..., ch][m2d].ravel()[::7], W[..., ch][m2d].ravel()[::7], 1)
        G[..., ch] = G[..., ch] * a + b
        gains.append((round(float(a), 3), round(float(b), 1)))
    after = np.abs(G - W).mean(2)[m2d].mean()
    return G, '挪了 (%d, %d)，差 %.1f → %.1f，颜色 %s' % (dx, dy, d0, after, gains)


def apply_patch(S, name, j, boxes, keep=None):
    """把 SRC/name.png 贴进整条 S（就地改），返回说明；keep 给一个目录就把贴好的窗口和掩码存下来看。"""
    from scipy import ndimage
    p = os.path.join(SRC, name + '.png')
    if not os.path.exists(p):
        return None
    x0 = patch_x0(j)
    W = S[:, x0:x0 + PW].copy()
    G = np.asarray(Image.open(p).convert('RGB').resize((PW, PH), Image.LANCZOS), dtype=np.float32)
    inside = np.zeros((PH, PW), bool)
    whole = np.zeros((PH, PW), bool)
    for bx in boxes:
        a, b, c, d = [round(v / 100 * n) for v, n in zip(bx[:4], (PW, PH, PW, PH))]
        inside[b:d, a:c] = True
        if bx[4:] == ('full',):
            whole[b:d, a:c] = True
    outside = ~ndimage.binary_dilation(inside, iterations=24)
    outside[:24] = outside[-24:] = False
    G, info = fit_mask(G, W, outside)
    D = ndimage.uniform_filter(np.abs(G - W).mean(2), 15)
    M = (D > PATCH_T) & inside
    M = np.maximum(ndimage.maximum_filter(M.astype(np.float32), size=41) * inside, whole)
    A = ndimage.gaussian_filter(M, 7)
    A = np.minimum(A, ndimage.gaussian_filter(inside.astype(np.float32), 7))
    S[:, x0:x0 + PW] = W * (1 - A[..., None]) + G * A[..., None]
    if keep:
        Image.fromarray(S[:, x0:x0 + PW].clip(0, 255).astype(np.uint8)).save(os.path.join(keep, name + '_merged.png'))
        v = W.copy()
        v[..., 0] = v[..., 0] * (1 - A) + 255 * A
        Image.fromarray(v.clip(0, 255).astype(np.uint8)).resize((768, 512), Image.LANCZOS).save(os.path.join(keep, name + '_mask.jpg'), quality=85)
    return info + '，改了框里 %.0f%% 的地方' % (100 * (A > 0.5).sum() / max(1, inside.sum()))


def stitched(segs=None, keep=None, cut_missing=False):
    """原来的十一段 → 并上重画的接缝 → 打上小改。cut_missing：哪一处小改还没有底图就从这时候的样子切一块存成 pNN_in.png。"""
    S = build(segs)
    done = []
    for j in range(1, NP):
        p = os.path.join(SRC, 'j%02d.png' % j)
        if not os.path.exists(p):
            continue
        c = junction_x(j)
        W = S[:, c - PW // 2:c + PW // 2].copy()
        G = np.asarray(Image.open(p).convert('RGB').resize((PW, PH), Image.LANCZOS), dtype=np.float32)
        G, info = fit(G, W)
        S[:, c - PW // 2:c + PW // 2] = stitch(G, W)
        done.append(j)
        print('接缝', j, info)
    for name, j, boxes in PATCHES:
        pin = os.path.join(SRC, name + '_in.png')
        if cut_missing and not os.path.exists(pin):
            x0 = patch_x0(j)
            Image.fromarray(S[:, x0:x0 + PW].clip(0, 255).astype(np.uint8)).save(pin)
            print('切了', name + '_in.png')
        r = apply_patch(S, name, j, boxes, keep)
        if r:
            print('小改', name, r)
    return S, done


def slots():
    import json
    return json.load(open(os.path.join(HERE, 'data', 'road.json'), encoding='utf-8'))['slots']


def sheet_of(S, dst, h=300, marks=False):
    """整条折成四行看；marks 把二十二张牌的落点打成红圈（看牌是不是还立在空地上）。"""
    s = Image.fromarray(S.clip(0, 255).astype(np.uint8))
    sc = h / PH
    s = s.resize((round(s.size[0] * sc), h), Image.LANCZOS)
    rows, rw = 4, (s.size[0] + 3) // 4
    sheet = Image.new('RGB', (rw, rows * (h + 8)), (10, 11, 15))
    for r in range(rows):
        sheet.paste(s.crop((r * rw, 0, min(s.size[0], (r + 1) * rw), h)), (0, r * (h + 8)))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)

    def at(x, y):
        x *= sc
        r = int(x // rw)
        return x % rw, r * (h + 8) + y * sc

    for j in range(1, NP):
        xx, yy = at(junction_x(j), 0)
        d.line([(xx, yy), (xx, yy + 10)], fill=(255, 80, 80), width=2)
        d.text((xx + 3, yy), str(j), font=font, fill=(255, 120, 120))
    if marks:
        for i, (sx, sy) in enumerate(slots()):
            xx, yy = at((i >> 1) * STEP + sx * PW, sy * PH)
            d.ellipse([xx - 7, yy - 7, xx + 7, yy + 7], outline=(255, 40, 40), width=2)
            d.text((xx + 8, yy - 10), str(i + 1), font=font, fill=(255, 90, 90))
    sheet.save(dst, quality=88)
    print(dst, sheet.size)


def view_sheets(S, out, h=420, parts=3):
    """整条分成 parts*2 截，两截一张，看路是不是一条连着的（接缝标红线，牌的落点打红圈）。"""
    sc = h / PH
    Wt = S.shape[1]
    n = parts * 2
    cut = [round(Wt * i / n) for i in range(n + 1)]
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
    for p_ in range(parts):
        rows = []
        for r in range(2):
            a, b = cut[p_ * 2 + r], cut[p_ * 2 + r + 1]
            im = Image.fromarray(S[:, a:b].clip(0, 255).astype(np.uint8))
            im = im.resize((round((b - a) * sc), h), Image.LANCZOS)
            d = ImageDraw.Draw(im)
            for j in range(1, NP):
                x = (junction_x(j) - a) * sc
                if 0 <= x < im.size[0]:
                    d.line([(x, 0), (x, 14)], fill=(255, 60, 60), width=3)
                    d.text((x + 4, 0), '接缝%d' % j, font=font, fill=(255, 110, 110))
            for i, (sx, sy) in enumerate(slots()):
                x = ((i >> 1) * STEP + sx * PW - a) * sc
                if 0 <= x < im.size[0]:
                    y = sy * PH * sc
                    d.ellipse([x - 6, y - 6, x + 6, y + 6], outline=(255, 40, 40), width=2)
            rows.append(im)
        wmax = max(r.size[0] for r in rows)
        sheet = Image.new('RGB', (wmax, 2 * h + 8), (10, 11, 15))
        for r, im in enumerate(rows):
            sheet.paste(im, (0, r * (h + 8)))
        dst = os.path.join(out, 'view_%d.jpg' % (p_ + 1))
        sheet.save(dst, quality=86)
        print(dst, sheet.size)


def slot_sheet(S, dst):
    """二十二张牌的落点各裁一块（落点在当中、红十字），拼一张看是不是还是空地。"""
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
    cw, ch = 360, 240
    sheet = Image.new('RGB', (cw * 6, (ch + 26) * 4), (10, 11, 15))
    d = ImageDraw.Draw(sheet)
    for i, (sx, sy) in enumerate(slots()):
        x, y = int((i >> 1) * STEP + sx * PW), int(sy * PH)
        x0, y0 = max(0, x - cw // 2), max(0, min(PH - ch, y - ch // 2))
        im = Image.fromarray(S[y0:y0 + ch, x0:x0 + cw].clip(0, 255).astype(np.uint8))
        px_, py_ = (i % 6) * cw, (i // 6) * (ch + 26)
        sheet.paste(im, (px_, py_ + 26))
        cx_, cy_ = px_ + x - x0, py_ + 26 + y - y0
        d.line([(cx_ - 10, cy_), (cx_ + 10, cy_)], fill=(255, 40, 40), width=2)
        d.line([(cx_, cy_ - 10), (cx_, cy_ + 10)], fill=(255, 40, 40), width=2)
        d.text((px_ + 4, py_ + 2), '牌 %d（第 %d 段）' % (i + 1, (i >> 1) + 1), font=font, fill=(235, 225, 190))
    sheet.save(dst, quality=88)
    print(dst, sheet.size)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'cutp':          # 给还没有底图的小改切 pNN_in.png（从并好接缝、打好前面几处小改的样子上切）
        stitched(cut_missing=True)
    elif cmd == 'full':          # 原来那一条（没接过的）存成一整张，好裁
        Image.fromarray(build().clip(0, 255).astype(np.uint8)).save(sys.argv[2])
        print(sys.argv[2])
    elif cmd == 'strip':
        dst, h = sys.argv[2], next((int(a) for a in sys.argv[3:] if a.isdigit()), 256)
        sheet_of(build(), dst, h, marks='--marks' in sys.argv)
    elif cmd == 'joins':
        out = sys.argv[2]
        os.makedirs(out, exist_ok=True)
        S = build()
        for j in range(1, NP):
            c = junction_x(j)
            win = S[:, c - PW // 2:c + PW // 2]
            Image.fromarray(win.clip(0, 255).astype(np.uint8)).save(os.path.join(out, 'j%02d_in.png' % j))
        print('切了十道接缝', out)
    elif cmd in ('merge', 'try'):
        # merge：把重画过的接缝（SRC/jNN.png）并回整条、重切十一段写回 rNN.png（头一回先把原图存成 rNN_a0.png）
        # try <输出目录>：只并、不写回，出整条和每道接缝并好以后的样子给人看
        segs = []
        for k in range(NP):
            a0 = os.path.join(SRC, 'r%02d_a0.png' % (k + 1))
            segs.append(seg(k, 'r%02d_a0' % (k + 1)) if os.path.exists(a0) else seg(k))
        keep = sys.argv[2] if cmd == 'try' else None
        if keep:
            os.makedirs(keep, exist_ok=True)
        S, done = stitched(segs, keep)
        if cmd == 'try':
            out = sys.argv[2]
            os.makedirs(out, exist_ok=True)
            for j in done:
                c = junction_x(j)
                Image.fromarray(S[:, c - PW // 2:c + PW // 2].clip(0, 255).astype(np.uint8)).save(os.path.join(out, 'j%02d_merged.png' % j))
            sheet_of(S, os.path.join(out, 'strip.jpg'), 300, marks=True)
            view_sheets(S, out)
            Image.fromarray(S.clip(0, 255).astype(np.uint8)).save(os.path.join(out, 'full.png'))
            slot_sheet(S, os.path.join(out, 'slots.jpg'))
            print('并了', done, '，写在', out)
        else:
            for k in range(NP):
                a0 = os.path.join(SRC, 'r%02d_a0.png' % (k + 1))
                if not os.path.exists(a0):
                    os.replace(os.path.join(SRC, 'r%02d.png' % (k + 1)), a0)
                Image.fromarray(S[:, k * STEP:k * STEP + PW].clip(0, 255).astype(np.uint8)).save(os.path.join(SRC, 'r%02d.png' % (k + 1)))
            print('并了', done, '，十一段重切写回了 rNN.png（原图是 rNN_a0.png）')
