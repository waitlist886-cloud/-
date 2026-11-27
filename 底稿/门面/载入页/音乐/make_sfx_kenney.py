#!/usr/bin/env python3
# 门面交互音效第二版（11-26 夜）：合成的那一版用户嫌“廉价超古早像素游戏”，换成 Kenney 两个包里的真录音。
#   包：Kenney RPG Audio、Kenney Casino Audio（kenney.nl 官方下载，CC0，包里 License.txt 写明 Creative Commons Zero）。
#   包的原文件不进库，放在会话临时目录；这里只拿 ffmpeg 读，处理完的 mp3 写进 小样_外壳/assets/sfx/。
#   python -I -X utf8 底稿/门面/载入页/音乐/make_sfx_kenney.py <解开的包所在目录> <ffmpeg>
#   <解开的包所在目录> 底下要有 kenney_rpg-audio/Audio/ 和 kenney_casino-audio/Audio/。
# 每一声：取哪个文件、怎么处理，照下面 RECIPES；处理完照“有声部分的均方根”统一到同一个响度（-21 dBFS），峰值压在 -3 dBFS 以下，
# 轻重再照 data/sfx.json 的 gain 调（都比背景音乐低）。
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', '..', '小样_外壳', 'assets', 'sfx'))
PK, FF = sys.argv[1], sys.argv[2]
SR = 44100
RPG = os.path.join(PK, 'kenney_rpg-audio', 'Audio')
CAS = os.path.join(PK, 'kenney_casino-audio', 'Audio')

# 一声 = 几段源（文件、起点延迟毫秒、音量、处理串），混起来再走整体处理串
# pitch(r)：变调连带变速（像放慢的磁带，门轴、印更沉）；verb：几道衰减的回声当厅里的混响
def pitch(r):
    return 'asetrate=%d,aresample=%d' % (int(SR * r), SR)

VERB_S = 'aecho=0.8:0.55:45|90|140:0.22|0.13|0.07'                 # 小屋子
VERB_M = 'aecho=0.8:0.6:70|130|210|300:0.28|0.18|0.11|0.06'        # 厅
VERB_L = 'aecho=0.8:0.7:90|170|260|380|520:0.32|0.22|0.15|0.09|0.05'  # 大殿门口

RECIPES = {
    'deal':       {'src': [(CAS, 'card-place-1', 0, 1.0, '')], 'post': 'highpass=f=90', 'tail': 0.08,
                   '说': '牌落在桌上'},
    'flip':       {'src': [(CAS, 'card-slide-3', 0, 1.0, '')], 'post': 'highpass=f=110', 'tail': 0.08,
                   '说': '牌翻开（滑过桌面）'},
    'book_open':  {'src': [(RPG, 'bookOpen', 0, 1.0, ''), (RPG, 'bookFlip2', 110, 0.55, '')], 'post': 'highpass=f=70,' + VERB_S, 'tail': 0.25,
                   '说': '翻开书：书皮打开，接一下书页'},
    'page':       {'src': [(RPG, 'bookFlip1', 0, 1.0, '')], 'post': 'highpass=f=120', 'tail': 0.1, 'max': 0.7,
                   '说': '换时代页：翻一页'},
    'arch_open':  {'src': [(RPG, 'bookFlip2', 0, 1.0, '')], 'post': 'highpass=f=120', 'tail': 0.08,
                   '说': '档案展开：纸页掀开'},
    'arch_close': {'src': [(RPG, 'bookClose', 0, 1.0, '')], 'post': 'lowpass=f=6000,' + VERB_S, 'tail': 0.15,
                   '说': '档案合上：书合上'},
    'cloth':      {'src': [(RPG, 'cloth1', 0, 1.0, '')], 'post': 'highpass=f=80', 'tail': 0.1,
                   '说': '换衣着：布料抖一下'},
    'spoil':      {'src': [(RPG, 'metalClick', 0, 1.0, '')], 'post': 'highpass=f=300,lowpass=f=9000', 'tail': 0.06, 'max': 0.35,
                   '说': '剧透开关：小搭扣'},
    'hall':       {'src': [(RPG, 'doorOpen_1', 0, 1.0, pitch(0.94))], 'post': 'lowpass=f=7000,' + VERB_M, 'tail': 0.6,
                   '说': '推门进厅：木门开，带一点厅里的回声'},
    'draw_book':  {'src': [(RPG, 'bookPlace1', 0, 1.0, '')], 'post': 'lowpass=f=7000', 'tail': 0.1,
                   '说': '从架上抽一本书'},
    'bcard':      {'src': [(CAS, 'card-slide-1', 0, 1.0, '')], 'post': 'highpass=f=100', 'tail': 0.08,
                   '说': '建档：一叠牌滑进来'},
    'dice':       {'src': [(CAS, 'dice-throw-1', 0, 1.0, '')], 'post': 'highpass=f=80', 'tail': 0.1,
                   '说': '建档：掷骰子'},
    'seal':       {'src': [(RPG, 'chop', 0, 1.0, pitch(0.78)), (RPG, 'dropLeather', 15, 0.8, pitch(0.85))], 'post': 'lowpass=f=4200,' + VERB_S, 'tail': 0.3,
                   '说': '建档：铸印压下去（木头上一记闷响）'},
    'door':       {'src': [(RPG, 'doorOpen_2', 0, 1.0, pitch(0.8))], 'post': 'lowpass=f=4000,' + VERB_L, 'tail': 1.0,
                   '说': '推开门扉：门轴，降调加大殿回声'},
}
TARGET = 10 ** (-21 / 20)      # 有声部分的均方根
PEAK = 10 ** (-3 / 20)


def render(name, R):
    args = [FF, '-loglevel', 'error']
    for d, f, _, _, _ in R['src']:
        args += ['-i', os.path.join(d, f + '.ogg')]
    fl = []
    for k, (_, _, ms, vol, pre) in enumerate(R['src']):
        ch = 'aformat=channel_layouts=mono,aresample=%d' % SR + (',' + pre if pre else '') + ',volume=%.3f' % vol + (',adelay=%d' % ms if ms else '')
        fl.append('[%d:a]%s[s%d]' % (k, ch, k))
    n = len(R['src'])
    mix = ''.join('[s%d]' % k for k in range(n)) + ('amix=inputs=%d:normalize=0:duration=longest' % n if n > 1 else 'anull')
    fl.append(mix + ',apad=pad_dur=%.2f,' % R['tail'] + R['post'] + '[o]')
    args += ['-filter_complex', ';'.join(fl), '-map', '[o]', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    a = np.frombuffer(subprocess.run(args, capture_output=True, check=True).stdout, dtype='<f4').astype(np.float64)
    # 掐掉开头的静音（留 4 毫秒），末尾照有声的地方往后留一点再淡出
    env = np.convolve(np.abs(a), np.ones(256) / 256, 'same')
    on = np.where(env > env.max() * 0.02)[0]; off = np.where(env > env.max() * 0.003)[0]          # 起点照 -34 dB，终点照 -50 dB（留住尾音和回声）
    s0 = max(0, on[0] - int(SR * .004)); s1 = min(len(a), off[-1] + int(SR * .03))
    if 'max' in R: s1 = min(s1, s0 + int(SR * R['max']))
    a = a[s0:s1].copy()
    fi, fo = int(SR * .004), min(len(a) // 3, int(SR * (.3 if R['tail'] >= .3 else .08)))
    a[:fi] *= np.linspace(0, 1, fi); a[-fo:] *= np.linspace(1, 0, fo) ** 2
    # 响度：有声的那几帧（包络过峰值一成的）算均方根，统一到 TARGET，峰值压住
    act = a[np.convolve(np.abs(a), np.ones(256) / 256, 'same') > np.abs(a).max() * 0.1]
    g = TARGET / np.sqrt((act ** 2).mean())
    g = min(g, PEAK / np.abs(a).max())
    a *= g
    raw = a.astype('<f4').tobytes()
    dst = os.path.join(OUT, name + '.mp3')
    subprocess.run([FF, '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-q:a', '4', dst], input=raw, check=True)
    rms = 20 * np.log10(np.sqrt(((act * g) ** 2).mean()))
    return len(a) / SR, 20 * np.log10(np.abs(a).max()), rms, os.path.getsize(dst)


os.makedirs(OUT, exist_ok=True)
for k in ('pick', 'star'):          # 带魔法感的三声先拿掉（开书的光换成真录的翻书）
    p = os.path.join(OUT, k + '.mp3')
    if os.path.exists(p): os.remove(p)
for name, R in RECIPES.items():
    dur, pk, rms, sz = render(name, R)
    print('%-10s %5.2fs 峰 %5.1f dB 有声均方根 %5.1f dB %6d B  %s' % (name, dur, pk, rms, sz, ' + '.join(f for _, f, _, _, _ in R['src'])))
