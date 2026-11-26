#!/usr/bin/env python3
# rec_gate.mjs 录下来的帧拼成 mp4（30 帧，照每一帧的时间戳），另出一张每隔一秒半一格的缩略表给人先扫一眼。
#   python -I -X utf8 底稿/门面/载入页/tools/make_video.py <帧目录> <宽> <高> <输出.mp4> [ffmpeg 路径]
# 录屏录的是整个窗口，比页面大的照左上角裁成页面那么大；比页面小的（还没撑开窗口的头几帧）丢掉。
import glob
import os
import subprocess
import sys

from PIL import Image

d, W, H, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
ff = sys.argv[5] if len(sys.argv) > 5 else 'ffmpeg'
rows = open(os.path.join(d, 'list.txt'), encoding='utf-8').read().split('\n')
items, i = [], 0
while i < len(rows) - 1:
    if rows[i].startswith('file ') and rows[i + 1].startswith('duration '):
        items.append([rows[i][6:-1], float(rows[i + 1][9:])])
        i += 2
    else:
        i += 1
keep = []
for f, dur in items:
    im = Image.open(os.path.join(d, f))
    if im.size[0] >= W and im.size[1] >= H:
        if im.size != (W, H):
            im.crop((0, 0, W, H)).save(os.path.join(d, f), quality=88)
        keep.append([f, dur])
    elif keep:
        keep[-1][1] += dur
lst = os.path.join(d, 'list_ok.txt')
with open(lst, 'w', encoding='utf-8') as fh:
    for f, dur in keep:
        fh.write("file '%s'\nduration %.4f\n" % (f, dur))
    fh.write("file '%s'\n" % keep[-1][0])
subprocess.check_call([ff, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-vf', 'fps=30,scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p', '-c:v', 'libx264', '-crf', '21', '-preset', 'slow', '-movflags', '+faststart', out])
tot = sum(x[1] for x in keep)
print(os.path.basename(out), '%d 帧（录到的，去掉尺寸不对的）' % len(keep), '%.1f 秒' % tot, '%.1f MB' % (os.path.getsize(out) / 1048576))
# 缩略表：每 1.5 秒一格
cells, t, acc, k = [], 0.0, 0.0, 0
for f, dur in keep:
    if acc >= t:
        cells.append(f)
        t += 1.5
    acc += dur
cw = 180 if W < H else 360
ch = round(H * cw / W)
cols = 8 if W < H else 4
sheet = Image.new('RGB', (cols * (cw + 6), ((len(cells) + cols - 1) // cols) * (ch + 6)), (20, 20, 20))
for n, f in enumerate(cells):
    sheet.paste(Image.open(os.path.join(d, f)).convert('RGB').resize((cw, ch)), ((n % cols) * (cw + 6), (n // cols) * (ch + 6)))
sheet.save(out[:-4] + '_缩略表.jpg', quality=84)
