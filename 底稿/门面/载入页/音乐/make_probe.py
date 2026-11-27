#!/usr/bin/env python3
# 背景音乐探针那一段音（11-26 夜）：正弦叠几个音的钟声琶音，带一点混响、首尾淡入淡出，八秒一圈能接上，压成 mp3。只是用来试“出不出得了声”，曲子往后用 Suno 出的换。
#   python -I -X utf8 底稿/门面/载入页/音乐/make_probe.py <ffmpeg>
import os
import subprocess
import sys
import wave

import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', '..', '小样_外壳', 'assets', 'bgm', 'probe.mp3'))
T = 8.0
n = int(SR * T)
t = np.arange(n) / SR
y = np.zeros(n)
# D 大调的钟：D5 F#5 A5 D6，两遍，第二遍高一点（E5 A5 C#6 E6），每个音 0.5 秒起一个
notes = [587.33, 739.99, 880.0, 1174.66, 659.25, 880.0, 1108.73, 1318.51]
for k, f in enumerate(notes):
    t0 = k * 0.5 + (0.0 if k < 4 else 1.0)
    i0 = int(t0 * SR)
    tt = t[: n - i0]
    env = (1 - np.exp(-tt / 0.008)) * np.exp(-tt * 1.6)
    tone = np.sin(2 * np.pi * f * tt) + 0.28 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 3) + 0.12 * np.sin(2 * np.pi * f * 3.01 * tt) * np.exp(-tt * 5)
    y[i0:] += 0.22 * env * tone
# 底下一层很轻的长音（D3 + A3），让它不那么空
pad = (np.sin(2 * np.pi * 146.83 * t) + 0.6 * np.sin(2 * np.pi * 220.0 * t)) * 0.05 * np.sin(np.pi * t / T) ** 2
y += pad
# 混响：一段衰减的噪声做卷积
rng = np.random.default_rng(7)
ir_len = int(SR * 1.6)
ir = rng.standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (SR * 0.35))
ir[0] = 0
wet = np.convolve(y, ir)[:n]
wet /= np.max(np.abs(wet)) + 1e-9
y = 0.8 * y / (np.max(np.abs(y)) + 1e-9) + 0.25 * wet
# 首尾淡入淡出（一圈接一圈不咔哒）
fade = int(SR * 0.4)
y[:fade] *= np.linspace(0, 1, fade)
y[-int(SR * 1.2):] *= np.linspace(1, 0, int(SR * 1.2)) ** 2
y = y / np.max(np.abs(y)) * 0.5      # 约 -6dB
wav = OUT[:-4] + '.wav'
with wave.open(wav, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((y * 32767).astype('<i2').tobytes())
subprocess.check_call([sys.argv[1] if len(sys.argv) > 1 else 'ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-codec:a', 'libmp3lame', '-b:a', '96k', OUT])
os.remove(wav)
print(OUT, os.path.getsize(OUT), 'bytes')
