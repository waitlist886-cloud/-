#!/usr/bin/env python3
# 把 walk_sfx.mjs 录的画面跟音效合成一个带声的 mp4（11-26 夜）：无头 Chrome 没有声卡，录不到真的声音，
# 这里照外壳记下的每一声的时刻（sfxlog.json，墙上时刻）把同一份音效文件（assets/sfx/，轻重照 data/sfx.json）混成一条音轨。
#   python -I -X utf8 底稿/门面/载入页/音乐/mix_sfx.py <帧目录> <输出.mp4> <ffmpeg>
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHELL = os.path.normpath(os.path.join(HERE, '..', '..', '小样_外壳'))
d, out, ff = sys.argv[1], sys.argv[2], sys.argv[3]
log = json.load(open(os.path.join(d, 'sfxlog.json'), encoding='utf-8'))
conf = json.load(open(os.path.join(SHELL, 'data', 'sfx.json'), encoding='utf-8'))
t0 = log['frames'][0]
silent = out[:-4] + '_无声.mp4'
subprocess.check_call([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, '..', 'tools', 'make_video.py'), d, '390', '844', silent, ff])
ev = [x for x in log['sfx'] if x['at'] / 1000 - t0 > -0.05 and x['n'] in conf['sounds']]
args = [ff, '-y', '-loglevel', 'error', '-i', silent]
flt = []
for k, x in enumerate(ev):
    v = conf['sounds'][x['n']]
    args += ['-i', os.path.join(SHELL, v['src'])]
    ms = max(0, int((x['at'] / 1000 - t0) * 1000))
    flt.append('[%d:a]adelay=%d|%d,volume=%.3f[a%d]' % (k + 1, ms, ms, float(conf.get('vol', .35)) * float(v.get('gain', 1)) * 2.2, k))
# 混音：音效本来按网页里 0.35 的总音量放，视频里单听音效偏小，整体抬 2.2 倍（彼此的轻重不变）
flt.append(''.join('[a%d]' % k for k in range(len(ev))) + 'amix=inputs=%d:normalize=0:dropout_transition=0,alimiter=limit=0.95,apad[aout]' % len(ev))
args += ['-filter_complex', ';'.join(flt), '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out]
subprocess.check_call(args)
os.remove(silent)
print(os.path.basename(out), '%d 声' % len(ev), '%.1f MB' % (os.path.getsize(out) / 1048576))
print('  ' + '  '.join('%.1fs %s' % (x['at'] / 1000 - t0, x['n']) for x in ev))
