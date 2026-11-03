# 从 Hugging Face 多线分段下模型（11-03，单线 1MB/s，八线 55MB/s 上下）：python dl_model.py 仓库 路径 子目录 [线程数]。接着 .part 已有的部分下，完了核 sha256 再改名
import hashlib
import json
import os
import queue
import sys
import threading
import time
import urllib.request
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
M = r'C:\Users\waitl\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models'
repo, path, sub = sys.argv[1:4]
N = int(sys.argv[4]) if len(sys.argv) > 4 else 8
name = os.path.basename(path)
dst = os.path.join(M, sub, name)
part = dst + '.part'
d = os.path.dirname(path)
api = 'https://huggingface.co/api/models/%s/tree/main' % repo + ('/' + d if d else '')
x = [i for i in json.load(urllib.request.urlopen(api, timeout=60)) if i['path'] == path][0]
oid, size = x['lfs']['oid'], x['lfs']['size']
url = 'https://huggingface.co/%s/resolve/main/%s' % (repo, path)
have = os.path.getsize(part) if os.path.exists(part) else 0
have -= have % (1 << 20)
with open(part, 'ab') as f:
    f.truncate(size)
CH = 64 << 20
q = queue.Queue()
for s in range(have, size, CH):
    q.put((s, min(s + CH, size) - 1))
done = [have]
lock = threading.Lock()
errs = []


def work():
    with open(part, 'r+b') as f:
        while True:
            try:
                s, e = q.get_nowait()
            except queue.Empty:
                return
            for attempt in range(8):
                try:
                    req = urllib.request.Request(url, headers={'Range': 'bytes=%d-%d' % (s, e), 'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=120) as r:
                        pos = s
                        while True:
                            b = r.read(1 << 20)
                            if not b:
                                break
                            f.seek(pos)
                            f.write(b)
                            pos += len(b)
                            with lock:
                                done[0] += len(b)
                    if pos != e + 1:
                        raise IOError('短了 %d' % (e + 1 - pos))
                    break
                except Exception as ex:
                    with lock:
                        done[0] -= max(0, locals().get('pos', s) - s)
                    time.sleep(3 + attempt * 2)
                    if attempt == 7:
                        errs.append((s, str(ex)))


ts = [threading.Thread(target=work, daemon=True) for _ in range(N)]
for t in ts:
    t.start()
t0 = time.time()
start = done[0]
while any(t.is_alive() for t in ts):
    time.sleep(20)
    print('%.2f / %.2f GB  %.1f MB/s' % (done[0] / 1e9, size / 1e9, (done[0] - start) / 1e6 / max(time.time() - t0, 1)), flush=True)
if errs:
    raise SystemExit('有段没下成 %s' % errs[:3])
h = hashlib.sha256()
with open(part, 'rb') as f:
    for chunk in iter(lambda: f.read(1 << 22), b''):
        h.update(chunk)
if h.hexdigest() != oid:
    raise SystemExit('sha256 不对，没改名：' + h.hexdigest())
os.replace(part, dst)
print('好了', name, 'sha256 对得上', flush=True)
