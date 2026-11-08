#!/usr/bin/env python3
# 批量传 ImgBB（11-07，Imgur 不给 API 了，用户定先走 ImgBB）。只用标准库。
#   python imgbb_up.py <清单.json> <文件…>        传文件，传过的（清单里有、文件没变）跳过
#   python imgbb_up.py --check <清单.json>          把清单里每个 URL 取回来，核大小和格式（透明 webp 有没有被转掉）
# key 只从两处读：环境变量 IMGBB_KEY，或者注册表 HKCU\Environment 里的 IMGBB_KEY（用户在 PowerShell 里
# [Environment]::SetEnvironmentVariable('IMGBB_KEY','…','User') 设的，桌面版开着时子进程继承不到，所以直接读注册表）。
# key 不进仓库、不进日志、不打印。清单记的是文件的 sha1、大小、URL、删除链接，可以进仓库（删除链接谁拿到都能删，别外传）。
import base64
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
API = 'https://api.imgbb.com/1/upload'


class Limited(Exception):
    """ImgBB 回 Rate limit reached：整批停下，别把后面的一张张都试失败（11-07 撞过一回，传了七百八十张上下以后限了一个多钟头）。"""


def key():
    k = os.environ.get('IMGBB_KEY')
    if not k and os.name == 'nt':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as h:
                k = winreg.QueryValueEx(h, 'IMGBB_KEY')[0]
        except OSError:
            k = None
    if not k:
        raise SystemExit('没有 IMGBB_KEY：在 PowerShell 里跑 [Environment]::SetEnvironmentVariable(\'IMGBB_KEY\',\'你的key\',\'User\')')
    return k.strip()


def sha1(p):
    h = hashlib.sha1()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def post(k, path, name, tries=4):
    data = urllib.parse.urlencode({'key': k, 'name': name, 'image': base64.b64encode(open(path, 'rb').read()).decode()}).encode()
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(API, data=data, headers={'User-Agent': 'aldran-imgbb-up/1'})
            with urllib.request.urlopen(req, timeout=120) as r:
                j = json.loads(r.read().decode('utf-8'))
            if j.get('success'):
                return j['data']
            last = 'success=false ' + json.dumps(j.get('error') or j, ensure_ascii=False)[:200]
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'replace')[:200].replace(k, '***')
            last = 'HTTP %s %s' % (e.code, body)
            if 'Rate limit' in body:
                raise Limited(last)
            if e.code in (400, 401, 403):
                break
        except Exception as e:   # noqa: BLE001
            last = repr(e).replace(k, '***')
        time.sleep(3 * (i + 1))
    raise RuntimeError(last)


def upload(manifest, files):
    k = key()
    m = json.load(open(manifest, encoding='utf-8')) if os.path.exists(manifest) else {}
    ok = skip = bad = 0
    for p in files:
        p = os.path.abspath(p)
        rel = os.path.basename(p)
        h = sha1(p)
        old = m.get(rel)
        if old and old.get('sha1') == h and old.get('url'):
            skip += 1
            continue
        try:
            d = post(k, p, os.path.splitext(rel)[0])
        except Limited as e:
            print('限流了，这一批停下', rel, e)
            print('== 传了 %d 跳过 %d 失败 %d（限流），清单 %s' % (ok, skip, bad, manifest))
            return 'limited'
        except Exception as e:   # noqa: BLE001
            print('失败', rel, e)
            bad += 1
            continue
        m[rel] = {'sha1': h, 'size': os.path.getsize(p), 'url': d['url'], 'display': d.get('display_url'), 'delete': d.get('delete_url'),
                  'w': d.get('width'), 'h': d.get('height'), 'mime': (d.get('image') or {}).get('mime'), 'id': d.get('id'), 'at': int(time.time())}
        json.dump(m, open(manifest, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        ok += 1
        print('好了', rel, d['url'], d.get('width'), d.get('height'), (d.get('image') or {}).get('mime'))
        time.sleep(float(os.environ.get('IMGBB_GAP', '0.5')))   # 每张之间等几秒，慢一点免得撞限流
    print('== 传了 %d 跳过 %d 失败 %d，清单 %s' % (ok, skip, bad, manifest))
    return bad == 0


def check(manifest):
    m = json.load(open(manifest, encoding='utf-8'))
    bad = 0
    for rel, d in m.items():
        try:
            req = urllib.request.Request(d['url'], headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://rilichat.com/'})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
                ct = r.headers.get('Content-Type')
            same = len(b) == d['size']
            alpha = ''
            if b[:4] == b'RIFF' and b[8:12] == b'WEBP':
                alpha = ' VP8X' if b[12:16] == b'VP8X' else (' VP8L' if b[12:16] == b'VP8L' else ' VP8(无透明)')
            print(('对' if same else '大小不同'), rel, ct, len(b), '原', d['size'], alpha)
            bad += 0 if same else 1
        except Exception as e:   # noqa: BLE001
            print('取不到', rel, e)
            bad += 1
    print('== 不对的', bad)


def expand(args):
    """参数可以是目录：传里头的 *.webp（一纪几百张，Windows 命令行装不下那么多路径）。"""
    out = []
    for p in args:
        if os.path.isdir(p):
            out += sorted(os.path.join(p, f) for f in os.listdir(p) if f.endswith('.webp'))
        else:
            out.append(p)
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--check']:
        check(a[1])
    else:
        r = upload(a[0], expand(a[1:]))
        sys.exit(3 if r == 'limited' else (0 if r else 1))
