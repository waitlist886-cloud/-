#!/usr/bin/env python3
# 门面探针（11-12）要从图床载的几个小文件，写进同目录的 ext/。都是现做的测试桩，没有卡里的东西。
#   p.js 外链脚本，m.js 外链模块，p.css 外链样式，p.json 给 fetch 用，px.png 验跨域图能不能进画布，
#   big.webp 一张二百多 KB 的杂色图量下载快慢，beep.mp3 半秒的轻响，v.mp4 / v.webm 一秒的测试片。
# 用法：python gen_ext.py        （要 PIL、numpy 和 ffmpeg）
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, 'ext')
os.makedirs(EXT, exist_ok=True)
FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')


def w(name, text):
    with open(os.path.join(EXT, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


w('p.js', '''/* 奥尔德兰门面探针：外链脚本。跑到这里，说明介绍页让从外面载脚本。 */
window.__probe_js = { ok: 1, at: Date.now(), src: (document.currentScript && document.currentScript.src) || '' };
''')
w('m.js', '''/* 奥尔德兰门面探针：外链模块。 */
export const ok = 'mod-ok';
export default function hello() { return 'hello'; }
''')
w('p.css', '#cssprobe{width:37px;height:11px}\n')
w('p.json', json.dumps({'ok': 1, 'probe': 'aldran-front', 'n': 20261112}) + '\n')

# 16×16 的纯色小图：画进画布以后读回来应当是 (201,164,92)
Image.new('RGB', (16, 16), (201, 164, 92)).save(os.path.join(EXT, 'px.png'))

# 杂色图：压不动，大小稳定，拿来量下载
rng = np.random.default_rng(20261112)
noise = rng.integers(0, 256, (576, 576, 3), dtype=np.uint8)
Image.fromarray(noise, 'RGB').save(os.path.join(EXT, 'big.webp'), quality=82, method=4)


def ff(*a):
    r = subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])


ff('-f', 'lavfi', '-i', 'sine=frequency=660:duration=0.5:sample_rate=44100',
   '-af', 'afade=t=in:d=0.03,afade=t=out:st=0.3:d=0.2,volume=0.45', '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '64k',
   '-map_metadata', '-1', os.path.join(EXT, 'beep.mp3'))
ff('-f', 'lavfi', '-i', 'testsrc=size=96x96:rate=15:duration=1', '-c:v', 'libx264', '-profile:v', 'baseline', '-pix_fmt', 'yuv420p',
   '-movflags', '+faststart', '-an', '-map_metadata', '-1', os.path.join(EXT, 'v.mp4'))
ff('-f', 'lavfi', '-i', 'testsrc=size=96x96:rate=15:duration=1', '-c:v', 'libvpx', '-b:v', '120k', '-an', '-map_metadata', '-1',
   os.path.join(EXT, 'v.webm'))

for f in sorted(os.listdir(EXT)):
    print('%8d  %s' % (os.path.getsize(os.path.join(EXT, f)), f))
