#!/usr/bin/env python3
# 门面背景音乐（11-27）：用户在 Suno 定稿的八首 wav → 能一圈一圈接着放的 mp3，放 小样_外壳/assets/bgm/，循环点写进 data/bgm.json。
#   python -I -X utf8 底稿/门面/载入页/音乐/make_bgm.py <wav 所在目录> <ffmpeg>
# 原 wav 不进库（用户自己的下载目录里）。
#
# 怎么接成一圈（每一首）：
#   一、掐头：开头过 -40 dB 以前的那一点（都不到半秒）掐掉，留 30 毫秒。掐尾：末尾照 50 毫秒一格看，最后一格过 -48 dB 的地方为止，后面的静音不要。
#       掐完的叫 T（长 N 秒）。
#   二、交叉：T 的末尾是收束的那一下和它的余音，跟开头的前奏叠起来。交叉长 X 秒（3 到 6 秒）：从末 8 秒里最响的那一下往后算到结尾，夹在 3 到 6 之间。
#       文件 F = T[0 : N-X] ＋ （T[N-X : N] 用 cos 淡出 叠 T[0 : X] 用 sin 淡入，等功率）＋ T[X : X+1.5]。
#       头一遍从 F 的 0 秒放，听到的是原样的前奏；放到 F 的 N 秒那一刻跳回 X 秒，跳的两边内容一模一样（末尾多拷的那 1.5 秒就是 X 秒以后那 1.5 秒），
#       所以解码器在开头多出来的几十毫秒（mp3 的编码延迟，各家解码器不一样）不碍事：循环点 [X, N] 两头一起挪，挪进去的地方两边还是同样的声音。
#       接上的那一下就是“这一首收住的余音里，前奏又起来了”。
#   三、响度：放一圈（F 的 X 到 N 秒）照 EBU R128 量，整体拉到 -20 LUFS（只乘一个数，不压动态），真峰值不过 -1 dBTP。
#   四、压 mp3：48kHz 立体声，160kbps（一首过 4MB 的用 128kbps）。
# 播放（bgm_shell.js）：WebAudio 解成缓冲，AudioBufferSourceNode 设 loop、loopStart=X、loopEnd=N，样本级接上，没有 <audio loop> 那一下空隙；iOS 上音量也调得动。
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHELL = os.path.normpath(os.path.join(HERE, '..', '..', '小样_外壳'))
OUT = os.path.join(SHELL, 'assets', 'bgm')
SRC, FF = sys.argv[1], sys.argv[2]
SR = 48000
PAD = 1.5
TARGET = -20.0
TP_MAX = -1.0
TRACKS = [      # 场景名、文件、给人看的一句
    ('gate', 'The Hall of Departure.wav', '死之神殿（载入页和牌桌）'),
    ('moon', 'Dawn of the Northern Plains.wav', '月银纪'),
    ('strife', 'The Wall of Ash.wav', '纷争纪'),
    ('bronze', 'Bronze Rebirth.wav', '山铜纪'),
    ('maze', "The Oboe's Descent.wav", '迷宫纪前传'),
    ('now', "The Labyrinth's Heart.wav", '此刻（迷宫纪1001年）'),
    ('library', 'Library of Starlight.wav', '大图书馆'),
    ('build', 'Before the New Journey.wav', '建档'),
]


def load(p):
    raw = subprocess.run([FF, '-loglevel', 'error', '-i', p, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, '<f4').astype(np.float64).reshape(-1, 2)


def frames_db(a, ms):
    w = int(SR * ms / 1000); n = len(a) // w
    m = (a[:n * w] ** 2).mean(1).reshape(n, w).mean(1)
    return 10 * np.log10(m + 1e-12), w


def ebur(arr):
    """拿 ffmpeg 的 ebur128 量整体响度和真峰值"""
    r = subprocess.run([FF, '-hide_banner', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       input=arr.astype('<f4').tobytes(), capture_output=True)
    t = r.stderr.decode('utf-8', 'replace')
    tail = t[t.rfind('Summary:'):]
    I = float(re.search(r'I:\s+(-?[\d.]+) LUFS', tail).group(1))
    P = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', tail).group(1))
    return I, P


def measure_file(p):
    r = subprocess.run([FF, '-hide_banner', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True)
    t = r.stderr.decode('utf-8', 'replace'); tail = t[t.rfind('Summary:'):]
    return float(re.search(r'I:\s+(-?[\d.]+) LUFS', tail).group(1)), float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', tail).group(1))


def seam_jump(F, j, i):
    """放的时候从第 i 个样本（N 秒）跳回第 j 个（X 秒）：跳前跳后 20 毫秒的电平（dB），和跳的两边多拷的那一段最大差多少"""
    w = int(SR * .02)
    before = 10 * np.log10((F[i - w:i] ** 2).mean() + 1e-12); after = 10 * np.log10((F[j:j + w] ** 2).mean() + 1e-12)
    diff = np.abs(F[i:i + int(SR * PAD) - 1] - F[j:j + int(SR * PAD) - 1]).max()          # 跳的两边多拷的那一段是不是一模一样
    return before, after, diff


def build(name, fn):
    a = load(os.path.join(SRC, fn))
    db, w = frames_db(a, 50)
    h = max(0, int(np.argmax(db > -40)) * w - int(SR * .03))
    e = (len(db) - 1 - int(np.argmax(db[::-1] > -48)) + 1) * w
    T = a[h:e]
    N = len(T) / SR
    d5, w5 = frames_db(T, 500)
    k8 = len(d5) - 16          # 末 8 秒
    pk = k8 + int(np.argmax(d5[k8:]))
    X = float(np.clip(N - (pk + 1) * .5, 3.0, 6.0))
    nX = int(round(X * SR)); nN = len(T)
    u = np.linspace(0, 1, nX)[:, None]
    xf = T[nN - nX:] * np.cos(u * np.pi / 2) + T[:nX] * np.sin(u * np.pi / 2)
    F = np.concatenate([T[:nN - nX], xf, T[nX:nX + int(PAD * SR)]])
    loop = (nX / SR, nN / SR)
    I, P = ebur(F[nX:nN])
    g = 10 ** ((TARGET - I) / 20)
    if P + 20 * np.log10(g) > TP_MAX:
        g = 10 ** ((TP_MAX - P) / 20)
    F = F * g
    sb, sa, sd = seam_jump(F, nX, nN)
    br = '160k' if len(F) / SR * 160000 / 8 <= 4.0e6 else '128k'
    dst = os.path.join(OUT, name + '.mp3')
    subprocess.run([FF, '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'libmp3lame', '-b:a', br, dst],
                   input=F.astype('<f4').tobytes(), check=True)
    fI, fP = measure_file(dst)
    # 交叉那一段跟前后比：放一圈的样子（N 前 8 秒接 X 后 8 秒），每半秒的电平
    ring = np.concatenate([F[int((loop[1] - 8) * SR):int(loop[1] * SR)], F[int(loop[0] * SR):int((loop[0] + 8) * SR)]])
    rd, _ = frames_db(ring, 500)
    info = {'src': 'assets/bgm/%s.mp3' % name, 'loop': [round(loop[0], 4), round(loop[1], 4)], 'from': fn,
            'trim': [round(h / SR, 3), round((len(a) - e) / SR, 3)], 'xfade': round(X, 2), 'gain_db': round(20 * np.log10(g), 2),
            'lufs': fI, 'tp': fP, 'br': br, 'bytes': os.path.getsize(dst), 'dur': round(len(F) / SR, 2)}
    print('%-8s %-32s 原长 %6.1fs 掐头 %.2fs 掐尾 %.2fs 交叉 %.1fs 循环 %.2f→%.2f 增益 %+.1fdB  成品 %.1f LUFS 真峰 %.1f dBTP %s %.2f MB'
          % (name, fn, len(a) / SR, info['trim'][0], info['trim'][1], X, loop[1], loop[0], info['gain_db'], fI, fP, br, info['bytes'] / 1048576))
    print('         跳回那一下：跳前 20ms %.1f dB 跳后 %.1f dB，两边多拷的 1.5 秒最大样本差 %.1e；放一圈 N 前 8 秒｜X 后 8 秒每半秒：%s'
          % (sb, sa, sd, ' '.join('%.0f' % x for x in rd[:16]) + ' ｜ ' + ' '.join('%.0f' % x for x in rd[16:])))
    return info, ring


os.makedirs(OUT, exist_ok=True)
tracks, rings = {}, {}
for name, fn, say in TRACKS:
    info, ring = build(name, fn)
    info['说'] = say
    tracks[name] = info
    rings[name] = ring
for f in os.listdir(OUT):          # 探针那一段不用了
    if f == 'probe.mp3':
        os.remove(os.path.join(OUT, f))
json.dump(tracks, open(os.path.join(HERE, 'bgm_tracks.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if len(sys.argv) > 3:          # 第三个参数：接缝波形图存到哪个目录（放一圈 N 前 8 秒接 X 后 8 秒的样本，给 seam_plot 用）
    for k, r in rings.items():
        np.save(os.path.join(sys.argv[3], 'ring_%s.npy' % k), r[::4].astype(np.float32))
print('合计 %.1f MB' % (sum(t['bytes'] for t in tracks.values()) / 1048576))
