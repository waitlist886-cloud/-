#!/usr/bin/env python3
# 推完图床以后把各段的文件从 jsDelivr 取一遍（11-15）：一是核每个文件取得到、大小跟本地一样，二是让镜像先把文件备好，头一个打开的玩家不用等它回源。
#   python -I -X utf8 底稿/门面/共用/warm_front.py [段名…] [--all] [--mirror https://fastly.jsdelivr.net/]
# 不写段名只取外壳和四本书的页面那几段（front_shell、front_<书>）；--all 连原画、立绘那几段一起（一千八百来个文件，六百来兆，慢）。
import concurrent.futures as cf
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_front as DF  # noqa: E402    （它一进来就把输出换成 utf-8 的了，这里不再另包一层，包两层前一层回收时会把输出关掉）


def get(url, tries=6):
    # 头一回取的文件镜像要回 GitHub 拿，一下取太多会回 403（过一会儿再取就好，取到过一回以后镜像自己存着）。所以失败了等一等再试。
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'front-warm'})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, len(r.read())
        except Exception as e:          # noqa: BLE001
            last = e
            time.sleep(1.5 * (k + 1))
    return 0, str(last)[:120]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    mirror = 'https://cdn.jsdelivr.net/'
    if '--mirror' in sys.argv:
        mirror = sys.argv[sys.argv.index('--mirror') + 1]
        args = [a for a in args if a != mirror]
    man = json.load(open(os.path.join(HERE, 'front_manifest.json'), encoding='utf-8'))
    units = args or ([u for u in DF.UNITS] if '--all' in sys.argv else ['front_shell'] + ['front_' + b for b in DF.BOOKS])
    bad = 0
    for name in units:
        u = DF.UNITS[name]
        if name not in man:
            print(name, '还没推')
            bad += 1
            continue
        base = os.path.join(DF.FRONT, u['src'])
        fs = DF.files_of(u)
        root = '%sgh/%s@%s/' % (mirror, DF.REPO, man[name]['commit'])
        jobs = {}
        with cf.ThreadPoolExecutor(6) as ex:
            for f in fs:
                jobs[ex.submit(get, root + f)] = f
            miss = []
            for j in cf.as_completed(jobs):
                f = jobs[j]
                st, n = j.result()
                want = os.path.getsize(os.path.join(base, f))
                if st != 200 or n != want:
                    miss.append((f, st, n, want))
        print('%-18s %4d 个文件，取不到或者大小不对的 %d' % (name, len(fs), len(miss)))
        for m in miss[:12]:
            print('     ', m)
        bad += len(miss)
    print('合计不对的', bad)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
