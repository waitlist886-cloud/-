# 把新两扇贴回现成的大框截图：拿占位图按样式的 cover 算出位置，和截图比对得到真实露出的区域（花边、框线、顶栏都留着）
# mock_frame.py <左图或-> <右图或-> <输出>
import sys
import numpy as np
from PIL import Image, ImageFilter
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'E:\\aldran_art\\底稿\\状态栏\\'
shot = Image.open(BASE + '大框\\截图\\宽屏_迷宫纪_最新一条.jpg').convert('RGB')
W, H = shot.size
SIDE = W // 2 - 380 + 48


def cover(im, side):
    """照样式：cover，右扇贴左边裁外侧，左扇贴右边裁外侧，上下居中。"""
    s = max(SIDE / im.width, H / im.height)
    w, h = int(round(im.width * s)), int(round(im.height * s))
    r = im.convert('RGB').resize((w, h), Image.LANCZOS)
    top = (h - H) // 2
    left = 0 if side == 'r' else w - SIDE
    return r.crop((left, top, left + SIDE, top + H))


def grad(side):
    """样式里外侧压的那道暗：从外侧 .42 到 34% 透明。"""
    x = np.arange(SIDE) / (SIDE - 1)
    d = x if side == 'r' else 1 - x
    k = np.clip(1 - (d - 0.66) / 0.34, 0, 1)
    k = 1 - 0.42 * (1 - k)
    return k[None, :, None]


def mask_of(side, ph):
    x0 = W - SIDE if side == 'r' else 0
    S = np.asarray(shot.crop((x0, 0, x0 + SIDE, H))).astype(float)
    P = np.asarray(cover(ph, side)).astype(float) * grad(side)
    D = np.abs(S - P).max(axis=2)
    m = Image.fromarray(np.uint8(np.clip(D, 0, 255))).filter(ImageFilter.GaussianBlur(2))
    m = np.asarray(m) < 34
    m[:64, :] = False
    if side == 'l':
        m = m[:, ::-1]
    bound = np.full(H, -1)
    for y in range(64, H):
        run = np.convolve(m[y].astype(float), np.ones(14) / 14, mode='valid')
        hit = np.where(run > 0.6)[0]
        if len(hit):
            bound[y] = hit[0]
    good = bound >= 0
    idx = np.arange(H)
    bound = np.interp(idx, idx[good], bound[good])
    bound = np.array([np.median(bound[max(0, y - 3):y + 4]) for y in range(H)])
    out_m = np.zeros((H, SIDE), dtype=np.uint8)
    for y in range(64, H):
        out_m[y, max(0, int(bound[y]) - 5):] = 255
    if side == 'l':
        out_m = out_m[:, ::-1]
    return Image.fromarray(out_m).filter(ImageFilter.GaussianBlur(0.7)), x0


out = shot.copy()
for side, arg, name in (('l', sys.argv[1], 'maze_left.webp'), ('r', sys.argv[2], 'maze_right.webp')):
    if arg == '-':
        continue
    ph = Image.open(BASE + '手札\\占位图\\' + name)
    m, x0 = mask_of(side, ph)
    art = cover(Image.open(arg), side)
    arr = np.uint8(np.asarray(art).astype(float) * grad(side))
    out.paste(Image.fromarray(arr), (x0, 0), m)
    # 顶栏那一条是平台的毛玻璃，照新图糊一遍
    top = Image.fromarray(arr).crop((0, 0, SIDE, 64)).filter(ImageFilter.GaussianBlur(10))
    top = Image.eval(top, lambda v: int(v * 0.55))
    tm = Image.new('L', (SIDE, 64), 255)
    out.paste(top, (x0, 0), tm)
out.save(sys.argv[3], quality=92)
print('ok', out.size, 'side', SIDE)
