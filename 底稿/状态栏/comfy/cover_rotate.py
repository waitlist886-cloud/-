#!/usr/bin/env python3
# 日里封面轮换（11-28，用户：用风月那五张封面做轮换，一秒换一张）。
# 五张竖版盒绘照年代次序排，出三种：硬切 webp、淡入淡出 webp、硬切 gif（平台不收 webp 时用）。
#   python cover_rotate.py [每张毫秒，默认 1000]
# 要带 PIL 的 Python（ComfyUI 那一个）。写到 out/发布卡_四纪大框/封面/。
import os
import sys
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = os.path.join(ROOT, 'out', '发布卡_风月_四纪', '封面')
DST = os.path.join(ROOT, 'out', '发布卡_四纪大框', '封面')
ORDER = ['月银纪', '纷争纪', '山铜纪', '迷宫纪前传', '迷宫纪此刻']
SIZE = (800, 1200)


def load():
    out = []
    for n in ORDER:
        im = Image.open(os.path.join(SRC, n + '_封面.png')).convert('RGB')
        out.append(im.resize(SIZE, Image.LANCZOS))
    return out


def main(ms):
    os.makedirs(DST, exist_ok=True)
    frames = load()
    # 硬切
    p = os.path.join(DST, '日里_封面轮换_硬切.webp')
    frames[0].save(p, save_all=True, append_images=frames[1:], duration=ms, loop=0, quality=82, method=6)
    print(p, os.path.getsize(p) // 1024, 'KB')
    # 淡入淡出：停 ms-180，再用 3 帧各 60 毫秒化到下一张
    seq, dur = [], []
    steps = 3
    for i, a in enumerate(frames):
        b = frames[(i + 1) % len(frames)]
        seq.append(a); dur.append(ms - steps * 60)
        for k in range(1, steps + 1):
            seq.append(Image.blend(a, b, k / (steps + 1))); dur.append(60)
    p = os.path.join(DST, '日里_封面轮换_淡入.webp')
    seq[0].save(p, save_all=True, append_images=seq[1:], duration=dur, loop=0, quality=74, method=6)
    print(p, os.path.getsize(p) // 1024, 'KB')
    # gif 兜底（256 色，画会有点颗粒）
    g = [f.resize((600, 900), Image.LANCZOS).quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
    p = os.path.join(DST, '日里_封面轮换_硬切.gif')
    g[0].save(p, save_all=True, append_images=g[1:], duration=ms, loop=0, optimize=True)
    print(p, os.path.getsize(p) // 1024, 'KB')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
