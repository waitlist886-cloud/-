# 算碧湾的轮廓（Azgaar 地图坐标，2200×1400）：赤盐内海的西南一块 ∪ 出海那条河放宽 ∪ 河口外一小块海，
# 圆一圆、毛一毛边，描成一条平滑的闭合路径。输出 SVG 的 d。
# 用法：python bay_shape.py <lake10_river.json> <输出.txt>
import json, sys
import numpy as np
from scipy import ndimage as ndi

d = json.load(open(sys.argv[1], encoding='utf-8'))
lake = np.array(d['lake'])
river = np.array(d['rivers'][0]['pts'])
S = 8.0                                   # 一个地图单位几个像素
X0, Y0, X1, Y1 = 80.0, 1050.0, 490.0, 1225.0
Wp, Hp = int((X1 - X0) * S), int((Y1 - Y0) * S)
yy, xx = np.mgrid[0:Hp, 0:Wp]
mx, my = X0 + xx / S, Y0 + yy / S


def poly_mask(P):
    # 偶奇规则填多边形（射线法，按行做）
    m = np.zeros((Hp, Wp), bool)
    px, py = (P[:, 0] - X0) * S, (P[:, 1] - Y0) * S
    n = len(P)
    for r in range(Hp):
        y = r + 0.5
        xs = []
        for i in range(n):
            x1, y1, x2, y2 = px[i], py[i], px[(i + 1) % n], py[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for a, b in zip(xs[0::2], xs[1::2]):
            m[r, max(0, int(a)):min(Wp, int(b) + 1)] = True
    return m


lake_m = poly_mask(lake)
river_m = poly_mask(river)
src = river[0]
far = river[np.argmax(((river - src) ** 2).sum(1))]          # 河口：离源头最远的那一点
# 湖的西南一块：一个斜着的椭圆
cx, cy, rx, ry, ang = 262.0, 1156.0, 80.0, 44.0, np.deg2rad(-12)
dx, dy = mx - cx, my - cy
u = dx * np.cos(ang) + dy * np.sin(ang)
v = -dx * np.sin(ang) + dy * np.cos(ang)
ell = (u / rx) ** 2 + (v / ry) ** 2 <= 1
# 湖的西半边归湾：外沿就是原来的湖岸（Azgaar 的毛边），跟盐原之间是一道起伏的分界
xdiv = 300 + 22 * np.sin((my - 1070) / 37) + 9 * np.sin((my - 1070) / 13)
bay = lake_m & (mx < xdiv)
# 湾口：从河口往湖的西南角拉一道喇叭口，口宽里窄（不再顺着那条河绕）
ax_, ay_, bx_, by_ = far[0], far[1], 205.0, 1150.0
cx_, cy_ = 158.0, 1190.0                                        # 中线往南弯一点
jit = np.random.default_rng(5)
for t in np.linspace(0, 1, 90):
    px_ = (1 - t) ** 2 * ax_ + 2 * (1 - t) * t * cx_ + t ** 2 * bx_
    py_ = (1 - t) ** 2 * ay_ + 2 * (1 - t) * t * cy_ + t ** 2 * by_
    rr = 27.0 * (1 - t) ** 1.4 + 14.0 * (1 - (1 - t) ** 1.4) + jit.normal(0, 1.8)
    bay |= ((mx - px_) ** 2 + (my - py_) ** 2) <= rr ** 2
mouth = ((mx - far[0]) ** 2 + (my - far[1]) ** 2) <= (10 ** 2)       # 河口外一小块海
bay |= mouth
join = ((mx - src[0]) ** 2 + (my - src[1]) ** 2) <= (14 ** 2)          # 河道接湖那一头补一个圆，跟湖里那一块连上
# 毛边加圆：先模糊加噪声再取阈值
rng = np.random.default_rng(11)
noise = ndi.gaussian_filter(rng.standard_normal((Hp, Wp)), 3 * S)
noise /= np.abs(noise).max()
noise2 = ndi.gaussian_filter(rng.standard_normal((Hp, Wp)), 1.2 * S)
noise2 /= np.abs(noise2).max()
noise3 = ndi.gaussian_filter(rng.standard_normal((Hp, Wp)), 0.5 * S)
noise3 /= np.abs(noise3).max()
f = ndi.gaussian_filter(bay.astype(float), 0.9 * S) + noise * 0.12 + noise2 * 0.16 + noise3 * 0.10
bay = f > 0.5
lab, n = ndi.label(bay)
bay = lab == (1 + int(np.argmax(ndi.sum(bay, lab, range(1, n + 1)))))
bay = ndi.binary_fill_holes(bay)


def trace(b):
    # Moore 邻域描边：从最上最左的一个点起，顺时针绕一圈
    H, W = b.shape
    pad = np.zeros((H + 2, W + 2), bool)
    pad[1:-1, 1:-1] = b
    ys, xs = np.nonzero(pad)
    start = (ys[0], xs[0])
    nb = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
    out = [start]
    cur, back = start, 6
    for _ in range(4 * (H + W) * 20):
        found = False
        for k in range(8):
            dirn = (back + 1 + k) % 8
            ny, nx = cur[0] + nb[dirn][0], cur[1] + nb[dirn][1]
            if pad[ny, nx]:
                back = (dirn + 4) % 8
                cur = (ny, nx)
                found = True
                break
        if not found or cur == start:
            break
        out.append(cur)
    return np.array([(x - 1, y - 1) for y, x in out], float)


B = trace(bay)
P = np.c_[X0 + B[:, 0] / S, Y0 + B[:, 1] / S]
# 每隔一个地图单位上下取一点，再滑动平均
step = max(1, int(S * 0.9))
P = P[::step]
k = 3
P = np.array([P[(np.arange(i - k, i + k + 1)) % len(P)].mean(0) for i in range(len(P))])
parts = ['M%.2f,%.2f' % tuple(P[0])]
for i in range(len(P)):
    a, b = P[i], P[(i + 1) % len(P)]
    m = (a + b) / 2
    parts.append('Q%.2f,%.2f %.2f,%.2f' % (a[0], a[1], m[0], m[1]))
parts.append('Z')
open(sys.argv[2], 'w', encoding='utf-8').write(''.join(parts))
print('ok', len(P), '点；河口', far.round(1).tolist(), '湾面积（地图单位²）', round(bay.sum() / S / S, 1))
