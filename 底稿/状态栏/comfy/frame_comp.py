#!/usr/bin/env python3
# 四方的画怎么拼（11-03）：背景一张不透明的画，上面一层一层放抠好的东西（人、羽翼、烟、云、石），
# 靠窗那一边只有放上去的东西能伸进窗里，轮廓就是它们自己的轮廓，平的地方停在框线上。
# 一张画布 1400×2000，LINE 是框线的位置：右扇 x=LINE，左扇 x=W-LINE。图放进样式里按视口高缩放。
import numpy as np
from PIL import Image, ImageFilter

W, H, LINE = 1400, 2000, 90


def clean_edges(im, r=4):
    """抠图边上的颜色往里借，去掉白底或深底留下的一圈边。"""
    a = np.asarray(im).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3] / 255.0
    solid = (al > 0.92).astype(np.float32)
    m = Image.fromarray(np.uint8(solid * 255))
    blur_m = np.asarray(m.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255.0
    out = rgb.copy()
    pre = np.zeros_like(rgb)
    for c in range(3):
        ch = Image.fromarray(np.uint8(np.clip(rgb[..., c] * solid, 0, 255)))
        pre[..., c] = np.asarray(ch.filter(ImageFilter.GaussianBlur(r))).astype(np.float32)
    fill = pre / np.maximum(blur_m[..., None], 1e-3)
    edge = (al <= 0.92)[..., None]
    out = np.where(edge, np.clip(fill, 0, 255), rgb)
    return Image.fromarray(np.uint8(np.dstack([out, a[..., 3]])), 'RGBA')


def keep_thin(im, grow=31, thr=26):
    """BiRefNet 爱丢细东西（弓弦、箭杆、发丝）。白底图上不是白的地方，离主体不远的，透明度补回来。"""
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    corners = np.concatenate([a[:6, :6, :3].reshape(-1, 3), a[:6, -6:, :3].reshape(-1, 3), a[-6:, :6, :3].reshape(-1, 3), a[-6:, -6:, :3].reshape(-1, 3)])
    white = np.percentile(corners.min(axis=1), 80)   # 这张图的“白”是多白，Turbo 的白底常在 245 上下
    nonwhite = np.clip((white - a[..., :3].min(axis=2) - 14) / thr, 0, 1) * 255
    al = Image.fromarray(np.uint8(a[..., 3]))
    near = np.asarray(al.point(lambda v: 255 if v > 30 else 0).filter(ImageFilter.MaxFilter(grow))).astype(np.float32) / 255.0
    a[..., 3] = np.maximum(a[..., 3], nonwhite * near)
    return Image.fromarray(np.uint8(a), 'RGBA')


def fade_side(im, side, width):
    """图被裁到边的地方慢慢淡掉，别留一刀直边。"""
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    if side == 'right':
        ramp = np.clip((w - np.arange(w)) / float(width), 0, 1)[None, :]
    elif side == 'left':
        ramp = np.clip(np.arange(w) / float(width), 0, 1)[None, :]
    elif side == 'bottom':
        ramp = np.clip((h - np.arange(h)) / float(width), 0, 1)[:, None]
    else:
        ramp = np.clip(np.arange(h) / float(width), 0, 1)[:, None]
    a[..., 3] *= ramp
    return Image.fromarray(np.uint8(a), 'RGBA')


def attached_only(alpha, seed_col, x0, x1):
    """alpha 是 H×W 的数组，x0 到 x1 这一条里只留连着 seed_col 这一列的部分，别的清零（孤立的小星星、小点，留着会落在窗里）。"""
    on = alpha[:, x0:x1] > 40
    seen = np.zeros_like(on)
    h, w = on.shape
    stack = [(int(y), seed_col - x0) for y in np.nonzero(on[:, seed_col - x0])[0]]
    while stack:
        y, x = stack.pop()
        if y < 0 or y >= h or x < 0 or x >= w or seen[y, x] or not on[y, x]:
            continue
        seen[y, x] = True
        stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    out = alpha.copy()
    out[:, x0:x1][~seen] = 0
    return out


def trim_alpha(im, low=26, high=235):
    """收一收半透明的毛边，别留一层雾。"""
    a = np.asarray(im).astype(np.float32)
    al = np.clip((a[..., 3] - low) / (high - low), 0, 1) * 255
    a[..., 3] = al
    return Image.fromarray(np.uint8(a), 'RGBA')


def tint(im, color, amount):
    """往远处退：整层压一点环境色。"""
    if amount <= 0:
        return im
    a = np.asarray(im).astype(np.float32)
    c = np.array(color, dtype=np.float32)
    a[..., :3] = a[..., :3] * (1 - amount) + c * amount
    return Image.fromarray(np.uint8(a), 'RGBA')


def grade(im, shadow=(18, 24, 58), mid=1.0, gain=1.0, sat=1.0):
    """暗部推向夜蓝，亮部留暖，把不同来路的东西拉进一个调子。"""
    a = np.asarray(im).astype(np.float32)
    rgb = a[..., :3] / 255.0
    lum = (rgb * [0.299, 0.587, 0.114]).sum(axis=2, keepdims=True)
    rgb = lum + (rgb - lum) * sat
    k = np.clip(1 - lum * 1.6, 0, 1) ** 1.5
    rgb = rgb * (1 - k * 0.42) + np.array(shadow, dtype=np.float32) / 255.0 * (k * 0.42)
    rgb = np.clip(rgb * gain, 0, 1)
    a[..., :3] = rgb * 255
    return Image.fromarray(np.uint8(a), 'RGBA')


def rim(im, dx, dy, color=(255, 232, 178), strength=0.8, blur=2.5):
    """朝窗那一侧的轮廓亮一圈，像光从对话那边照过来。"""
    al = im.getchannel('A')
    off = Image.new('L', im.size, 0)
    off.paste(al, (dx, dy))
    a = np.asarray(al).astype(np.float32) / 255.0
    b = np.asarray(off.filter(ImageFilter.GaussianBlur(blur))).astype(np.float32) / 255.0
    edge = np.clip(a - b, 0, 1)[..., None] * strength
    arr = np.asarray(im).astype(np.float32)
    rgb = arr[..., :3]
    c = np.array(color, dtype=np.float32)
    rgb = 255 - (255 - rgb) * (1 - edge * c / 255.0)   # 滤色
    arr[..., :3] = rgb
    return Image.fromarray(np.uint8(np.clip(arr, 0, 255)), 'RGBA')


def drop(canvas, layer, pos, blur=14, offset=(0, 10), color=(4, 6, 20), opacity=0.55):
    al = layer.getchannel('A')
    sh = Image.new('L', canvas.size, 0)
    sh.paste(al, (pos[0] + offset[0], pos[1] + offset[1]))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * opacity))
    s = Image.new('RGBA', canvas.size, color + (0,))
    s.putalpha(sh)
    # 影子只落在已经有东西的地方，不把透明的窗口染黑（窗口上的影子样式里另有）
    ca = canvas.getchannel('A')
    arr = np.minimum(np.asarray(sh), np.asarray(ca))
    s.putalpha(Image.fromarray(arr))
    canvas.alpha_composite(s)


def place(canvas, path_or_im, x, y, scale=1.0, flip=False, shadow=True, tint_to=None, tint_amt=0, rim_dir=None, rim_strength=0.8, crop=None, rot=0, grade_kw=None, shadow_kw=None, fade_bottom=None):
    """x,y 是放好以后左上角的位置（画布坐标）。"""
    im = Image.open(path_or_im).convert('RGBA') if isinstance(path_or_im, str) else path_or_im.convert('RGBA')
    if crop:
        im = im.crop(crop)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, Image.BICUBIC, expand=True)
    if fade_bottom:
        a = np.asarray(im).astype(np.float32)
        h = a.shape[0]
        ramp = np.clip((h - np.arange(h)) / float(fade_bottom), 0, 1)[:, None]
        a[..., 3] *= ramp
        im = Image.fromarray(np.uint8(a), 'RGBA')
    if grade_kw is not None:
        im = grade(im, **grade_kw)
    if tint_to is not None:
        im = tint(im, tint_to, tint_amt)
    if rim_dir is not None:
        im = rim(im, rim_dir[0], rim_dir[1], strength=rim_strength)
    if shadow:
        drop(canvas, im, (x, y), **(shadow_kw or {}))
    canvas.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))
    return im


def base_canvas(bg_path, side, darken_top=None):
    """背景铺满框线外面那一块，框线靠窗那一侧透明。bg 是不透明的画。"""
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bg = Image.open(bg_path).convert('RGB')
    s = max((W - LINE) / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * s + 0.5), int(bg.height * s + 0.5)), Image.LANCZOS)
    if side == 'right':
        bg = bg.crop((0, (bg.height - H) // 2, W - LINE, (bg.height - H) // 2 + H))
        c.paste(bg, (LINE, 0))
    else:
        bg = bg.crop((bg.width - (W - LINE), (bg.height - H) // 2, bg.width, (bg.height - H) // 2 + H))
        c.paste(bg, (0, 0))
    return c


def save_webp(im, path, quality=88):
    im.save(path, quality=quality, method=6, alpha_quality=92)
