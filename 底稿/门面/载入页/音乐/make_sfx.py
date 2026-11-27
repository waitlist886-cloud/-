#!/usr/bin/env python3
# 11-26 夜：这是头一版（本机合成），用户听了嫌像廉价古早像素游戏，换成了 make_sfx_kenney.py 处理的 Kenney 真录音。留档，别再跑（会把真录音盖掉）。
# 门面的交互音效（11-26 夜）：全用 numpy 合成，ffmpeg 压成 mp3，放 小样_外壳/assets/sfx/。不从网上下任何音效包。
#   python -I -X utf8 底稿/门面/载入页/音乐/make_sfx.py <ffmpeg> [名字…]
# 声响类（纸页、布料、木头、石头、骰子）用滤过的噪声做；带音高的（选中、开书的光、星铃）用正弦叠泛音加短混响，调子跟背景音乐那一套一样在 D 大调上下。
# 每一个都归一到同一个峰值（-3dB），轻重在 data/sfx.json 的 gain 里另调。
import os
import subprocess
import sys
import wave

import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', '..', '小样_外壳', 'assets', 'sfx'))
rng = np.random.default_rng(11)
# D 大调的几个音
D4, Fs4, A4, D5, E5, Fs5, A5, B5, D6, E6, Fs6, A6 = 293.66, 369.99, 440.0, 587.33, 659.25, 739.99, 880.0, 987.77, 1174.66, 1318.51, 1479.98, 1760.0


def T(sec):
    return np.arange(int(SR * sec)) / SR


def noise(sec):
    return rng.standard_normal(int(SR * sec))


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def bandpass(x, lo, hi):
    """频域里切一段（简单、够用）：lo 到 hi 之间留着，两边软一点。"""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    w = np.clip((f - lo * 0.7) / (lo * 0.3 + 1), 0, 1) * np.clip((hi * 1.3 - f) / (hi * 0.3 + 1), 0, 1)
    return np.fft.irfft(X * w, n)


def sweep_bp(x, f0, f1, q=0.35):
    """随时间挪的带通：分几段切再接起来（纸页翻过去、东西划过去那种“嗖”）。"""
    n = len(x); seg = 8; out = np.zeros(n); L = n // seg
    for s in range(seg):
        a, b = s * L, n if s == seg - 1 else (s + 1) * L
        fc = f0 * (f1 / f0) ** ((s + 0.5) / seg)
        pad = 512
        lo, hi = max(0, a - pad), min(n, b + pad)
        y = bandpass(x[lo:hi], fc * (1 - q), fc * (1 + q))
        out[a:b] = y[a - lo:a - lo + (b - a)]
    return out


def env(t, att, dec):
    return (1 - np.exp(-t / max(att, 1e-4))) * np.exp(-t / dec)


def bell(f, sec, dec, parts=((1, 1), (2.0, .35), (3.01, .15)), att=0.003):
    t = T(sec)
    y = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (dec / (1 + 0.6 * k))) for k, (r, a) in enumerate(parts))
    return y * (1 - np.exp(-t / att))


def reverb(x, sec=0.9, decay=0.25, mix=0.25):
    ir_len = int(SR * sec)
    ir = rng.standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (SR * decay))
    ir = onepole_lp(ir, 5000)
    ir[0] = 0
    wet = np.convolve(x, ir)[: len(x) + ir_len // 2]
    wet /= np.max(np.abs(wet)) + 1e-9
    dry = np.concatenate([x, np.zeros(len(wet) - len(x))])
    dry /= np.max(np.abs(dry)) + 1e-9
    return dry * (1 - mix) + wet * mix


def place(total, *items):
    out = np.zeros(int(SR * total))
    for at, x in items:
        i = int(at * SR); j = min(len(out), i + len(x))
        out[i:j] += x[: j - i]
    return out


def tail(x, ms=12):
    n = int(SR * ms / 1000)
    x = x.copy(); x[-n:] *= np.linspace(1, 0, n); x[:64] *= np.linspace(0, 1, 64)
    return x


S = {}
# ---- 牌桌 ----
t = T(.14)
S['deal'] = bandpass(noise(.14), 900, 5200) * env(t, .002, .028) + 0.5 * np.sin(2 * np.pi * 150 * t) * env(t, .002, .03)          # 牌落在桌面：一下纸拍
t = T(.26)
S['flip'] = sweep_bp(noise(.26), 1400, 5200) * np.sin(np.pi * np.clip(t / .26, 0, 1)) ** 1.5 * 0.8 + place(.26, (.2, bandpass(noise(.05), 800, 4000) * env(T(.05), .001, .012)))       # 翻牌：嗖一下，末了一拍
S['pick'] = reverb(bell(D6, .7, .32) * 0.7 + bell(A6, .7, .26) * 0.45 + place(.7, (.06, bell(Fs6, .64, .22) * 0.35)), .8, .22, .3)          # 选中这一本：两三个亮的钟音叠着
# ---- 书 ----
sh = sweep_bp(noise(.9), 500, 3500) * np.sin(np.pi * np.clip(T(.9) / .9, 0, 1)) ** 2 * 0.35
S['book_open'] = reverb(place(1.0, (0, sh), (.18, bell(D5, .8, .35) * .45), (.30, bell(Fs5, .7, .3) * .4), (.42, bell(A5, .6, .28) * .4), (.54, bell(D6, .5, .25) * .35)), 1.0, .3, .35)      # 开书的光：一口气加一串上行的琶音
t = T(.32)
pg = sweep_bp(noise(.32), 2400, 900, .45) * np.sin(np.pi * np.clip(t / .32, 0, 1)) ** 1.2
pg *= 0.75 + 0.25 * np.sin(2 * np.pi * 38 * t)          # 纸页抖一抖
S['page'] = pg + place(.32, (.27, bandpass(noise(.05), 600, 3000) * env(T(.05), .001, .01) * .6))
t = T(.24)
S['arch_open'] = sweep_bp(noise(.24), 700, 2600, .4) * np.sin(np.pi * np.clip(t / .24, 0, 1)) * 0.8 + place(.24, (.04, bell(A5, .2, .07) * .18))      # 档案摊开：纸面滑开，带一点光
t = T(.2)
S['arch_close'] = bandpass(noise(.2), 200, 1400) * env(t, .004, .045) + 0.6 * np.sin(2 * np.pi * 110 * t) * env(t, .002, .05)          # 档案合上：一下闷的
t = T(.34)
cl = bandpass(noise(.34), 900, 6000) * np.sin(np.pi * np.clip(t / .34, 0, 1)) ** 1.5
grain = np.repeat(rng.random(int(.34 * 220) + 1), int(SR / 220) + 1)[: len(t)]
S['cloth'] = cl * (0.35 + 0.65 * grain)          # 换衣着：布料一抖
t = T(.09)
S['spoil'] = (np.sin(2 * np.pi * 820 * t) * env(t, .0008, .018) + .5 * np.sin(2 * np.pi * 1640 * t) * env(t, .0008, .01) + bandpass(noise(.09), 1500, 6000) * env(t, .0005, .004) * .5)      # 剧透开关：木头轻扣一声
# ---- 大图书馆 ----
t = T(.8)
S['hall'] = reverb(np.sin(2 * np.pi * 72 * t) * env(t, .006, .18) * .8 + bandpass(noise(.8), 120, 700) * env(t, .01, .12) * .7 + sweep_bp(noise(.8), 300, 900) * np.sin(np.pi * np.clip(t / .8, 0, 1)) * .25, 1.2, .4, .35)      # 推门进厅：厚门一推，厅里回一下
t = T(.32)
S['draw_book'] = sweep_bp(noise(.32), 1800, 700, .4) * np.sin(np.pi * np.clip(t / .26, 0, 1)) ** 1.3 * .7 + place(.32, (.24, bandpass(noise(.08), 150, 900) * env(T(.08), .002, .02) + np.sin(2 * np.pi * 130 * T(.08)) * env(T(.08), .002, .025) * .6))       # 从架上抽书：书脊擦过，落在手里一下
# ---- 建档 ----
t = T(.22)
S['bcard'] = sweep_bp(noise(.22), 1600, 4800) * np.sin(np.pi * np.clip(t / .22, 0, 1)) ** 1.6 * .7 + place(.22, (.17, bandpass(noise(.04), 1000, 4000) * env(T(.04), .001, .01) * .6))     # 牌翻过来
def knock(f, dec=.02):
    t = T(.08)
    return np.sin(2 * np.pi * f * t) * env(t, .0005, dec) + bandpass(noise(.08), 1200, 5000) * env(t, .0003, .005) * .7
S['dice'] = place(.62, (0, knock(1180)), (.09, knock(1350) * .8), (.17, knock(990) * .9), (.26, knock(1240) * .6), (.36, knock(1100) * .45), (.45, knock(1300) * .3), (.52, knock(1050) * .2))   # 掷骰子：几下碰撞，越碰越轻
S['star'] = reverb(place(1.3, (0, bell(D6, 1.2, .55, ((1, 1), (2.76, .3), (5.4, .12)))), (.11, bell(A6, 1.1, .45, ((1, .7), (2.76, .2), (5.4, .08)))), (.22, bell(Fs6, 1.0, .4, ((1, .5), (2.76, .15))))), 1.0, .35, .35)      # 命星落下：星铃
t = T(.55)
S['seal'] = reverb(np.sin(2 * np.pi * 62 * t) * env(t, .003, .09) + .7 * np.sin(2 * np.pi * 124 * t) * env(t, .002, .04) + bandpass(noise(.55), 80, 900) * env(t, .002, .05) * .9, .7, .25, .2)      # 铸印：印压下去一声闷响
# ---- 推开门扉：低沉的门轴 ----
t = T(1.1)
f = 78 + 30 * np.sin(np.pi * np.clip(t / 1.1, 0, 1)) + 6 * np.sin(2 * np.pi * 7 * t)
ph = 2 * np.pi * np.cumsum(f) / SR
saw = sum(np.sin(k * ph) / k for k in range(1, 9))
fric = bandpass(noise(1.1), 300, 1800) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 11 * t)))
S['door'] = reverb((onepole_lp(saw, 900) * .7 + fric * .25) * np.sin(np.pi * np.clip(t / 1.1, 0, 1)) ** .8 + place(1.1, (0, np.sin(2 * np.pi * 55 * T(.4)) * env(T(.4), .01, .12) * .8)), 1.3, .45, .35)


def write(name, y):
    y = tail(np.asarray(y, float))
    y = y / (np.max(np.abs(y)) + 1e-9) * 0.707          # -3dB
    os.makedirs(OUT, exist_ok=True)
    wav = os.path.join(OUT, name + '.wav')
    with wave.open(wav, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype('<i2').tobytes())
    mp3 = os.path.join(OUT, name + '.mp3')
    subprocess.check_call([FF, '-y', '-loglevel', 'error', '-i', wav, '-codec:a', 'libmp3lame', '-b:a', '80k', mp3])
    os.remove(wav)
    return os.path.getsize(mp3), len(y) / SR


if __name__ == '__main__':
    FF = sys.argv[1] if len(sys.argv) > 1 else 'ffmpeg'
    only = sys.argv[2:]
    tot = 0
    for k, y in S.items():
        if only and k not in only:
            continue
        b, d = write(k, y)
        tot += b
        print('%-10s %5.2f 秒 %5.1f KB' % (k, d, b / 1024))
    print('合计 %.1f KB' % (tot / 1024))
