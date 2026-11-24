#!/usr/bin/env python3
# 大陆全图地标上挂的原画（11-24）：旧 1001 页外链在 imgur 上，取下来转 webp 放进 assets/mp/<imgur 键>.webp，
# build_data.py 认到本地有这一张就写本地路径。已经取过的跳过。要带 PIL 的 Python（ComfyUI 那个 venv）。
#   python tools/localize_pics.py
import io
import json
import os
import re
import sys
import time
import urllib.request

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.normpath(os.path.join(HERE, '..'))
OUT = os.path.join(BOOK, 'assets', 'mp')
os.makedirs(OUT, exist_ok=True)
s = open(os.path.join(BOOK, 'data', 'now.json'), encoding='utf-8').read()
urls = sorted(set(re.findall(r'https?://i\.imgur\.com/[A-Za-z0-9]+\.\w+', s)))
print('外链', len(urls))
ok = bad = skip = 0
for u in urls:
    key = re.search(r'imgur\.com/([A-Za-z0-9]+)\.', u).group(1)
    dst = os.path.join(OUT, key + '.webp')
    if os.path.exists(dst):
        skip += 1
        continue
    data = None
    for i in range(4):
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=60).read()
            break
        except Exception as e:
            print('  重试', key, i + 1, str(e)[:80])
            time.sleep(3 * (i + 1))
    if not data:
        bad += 1
        print('取不到', u)
        continue
    im = Image.open(io.BytesIO(data)).convert('RGB')
    w, h = im.size
    if w > 1280:
        im = im.resize((1280, round(h * 1280 / w)), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=80, method=6)
    ok += 1
    if ok % 20 == 0:
        print('已取', ok)
    time.sleep(0.4)
tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
print('取了 %d，跳过 %d，取不到 %d；assets/mp/ 合计 %.1f MB' % (ok, skip, bad, tot / 1048576))
