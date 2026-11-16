#!/usr/bin/env python3
# 把图床上的“指针”挪到现在这一版门面（11-16）。
#   python -I -X utf8 底稿/门面/共用/push_ptr.py [--check]
# 指针就是 共用/front.json（各段的提交号，加 n：这一份是哪一刻的，加 g：这是第几代指针），放在图床仓库的两处：
#   · front_ptr_g<代> 分支：一代一个分支，推上去就不再动。还没有的分支镜像不缓存，新推的一分钟里就取得到，
#     薄壳（make_thin.py）从自己带的那一代顺着往后一代一代问，问到没有为止。门面的更新靠这一路，一分钟里到所有玩家手里。
#   · front_ptr 分支：一直是最新一代。这个地址 jsDelivr 要缓存到十二个钟头（11-16 量的：连着清了四十分钟缓存，五个镜像一个都没跟上），
#     GitHub 自己那一头（raw.githubusercontent.com）五分钟。只认这一处的旧薄壳（11-16、11-16b 两份）靠它，新薄壳拿它垫底。
# 卡里的薄壳取到了、n 比自己带的那一份新，就照它的提交号去取外壳和四本书；取不到照卡里写的那一份。
# 这样门面（页面、数据、图）更新以后不用再改卡的介绍页，推完图床、把指针挪过去就行。薄壳自己的写法变了才要重新贴介绍页。
# 先后：deploy_front.py（推各段）→ warm_front.py（新地址上的文件取一遍，都对了）→ 这一支。别在预取以前挪指针，玩家会撞上还没备好的文件。
# 代数一定连着（1、2、3……），薄壳是一代一代往后问的，中间空一代就断了。所以代数不记在本地，每回从图床仓库上现有的分支数出来。
# --check 只看各镜像上现在是哪一版，不推。
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_front as DF  # noqa: E402    （它一进来就把输出换成 utf-8 的了）
import make_thin  # noqa: E402

BRANCH = 'front_ptr'
GEN = 'front_ptr_g%d'


def fetch(u, ms=8000):
    req = urllib.request.Request(u, headers={'User-Agent': 'aldran-front/1.0'})
    with urllib.request.urlopen(req, timeout=ms / 1000) as r:
        return r.read().decode('utf-8', 'replace')


def remote_gens(repo):
    """图床仓库上现有的各代（照分支名数）。"""
    out = DF.git(HERE, 'ls-remote', '--heads', 'https://github.com/%s.git' % repo, 'refs/heads/front_ptr_g*')
    return sorted(int(m.group(1)) for m in re.finditer(r'refs/heads/front_ptr_g(\d+)\s*$', out, re.M))


def remote_gen_cfg(repo, g):
    """某一代的 front.json（直接从仓库取，不走镜像）。"""
    tmp = tempfile.mkdtemp(prefix='ptrg_')
    try:
        DF.git(tmp, 'init', '-q')
        DF.git(tmp, 'fetch', '-q', '--depth', '1', 'https://github.com/%s.git' % repo, 'refs/heads/' + GEN % g)
        return json.loads(DF.git(tmp, 'show', 'FETCH_HEAD:front.json'))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def look(cfg):
    """各镜像上：老地址（front_ptr）是哪一版，这一代的分支取不取得到。回这一代取得到的镜像数。"""
    ok = 0
    g = cfg.get('g')
    for m in make_thin.MIRRORS:
        try:
            j = json.loads(fetch('%sgh/%s@%s/front.json' % (m, cfg['repo'], BRANCH)))
            old = '是这一版' if j.get('n') == cfg.get('n') and j.get('shell') == cfg['shell'] else '还是旧的（n=%s）' % j.get('n')
        except Exception as e:  # noqa: BLE001
            old = '取不到：%s' % str(e)[:40]
        gen = '没有代数'
        if g:
            try:
                j = json.loads(fetch('%sgh/%s@%s/front.json' % (m, cfg['repo'], GEN % g)))
                gen = '取得到' if j.get('g') == g and j.get('n') == cfg.get('n') else '不对（n=%s）' % j.get('n')
                ok += gen == '取得到'
            except urllib.error.HTTPError as e:
                gen = '还没有（%s）' % e.code
            except Exception as e:  # noqa: BLE001
                gen = '取不到：%s' % str(e)[:40]
        print('  %-34s 第 %s 代的分支%s｜老地址%s' % (m, g or '?', gen, old))
    return ok


def push(cfg, fp, branches):
    tmp = tempfile.mkdtemp(prefix='ptr_')
    try:
        DF.git(tmp, 'init', '-q')
        DF.git(tmp, 'config', 'core.autocrlf', 'false')
        DF.git(tmp, 'checkout', '-q', '-b', BRANCH)
        shutil.copy2(fp, os.path.join(tmp, 'front.json'))
        DF.git(tmp, 'add', '-A')
        DF.git(tmp, '-c', 'user.name=Claude', '-c', 'user.email=noreply@anthropic.com', 'commit', '-q', '-m', '指针 第 %s 代 n=%s' % (cfg.get('g'), cfg['n']))
        commit = DF.git(tmp, 'rev-parse', 'HEAD')
        for b in branches:
            DF.git(tmp, 'push', '-q', '--force', 'https://github.com/%s.git' % cfg['repo'], 'HEAD:refs/heads/%s' % b)
        return commit
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    fp = os.path.join(HERE, 'front.json')
    cfg = json.load(open(fp, encoding='utf-8'))
    assert cfg.get('n'), 'front.json 里没有 n，先跑一遍 deploy_front.py'
    if '--check' in sys.argv:
        print('本地这一版 n=%s，第 %s 代' % (cfg['n'], cfg.get('g') or '?'))
        look(cfg)
        return
    gens = remote_gens(cfg['repo'])
    last = gens[-1] if gens else 0
    assert gens == list(range(1, last + 1)), ('图床上各代的分支不连着，薄壳会在空的那一代断掉，先补上', gens)
    same = False
    if last:
        r = remote_gen_cfg(cfg['repo'], last)
        same = r.get('n') == cfg['n'] and r.get('shell') == cfg['shell'] and r.get('books') == cfg['books']
    g = last if same else last + 1
    if cfg.get('g') != g:
        cfg['g'] = g
        json.dump(cfg, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if same:
        print('这一版已经是图床上的第 %d 代，不另起一代；老地址再推一遍' % g)
        commit = push(cfg, fp, [BRANCH])
    else:
        commit = push(cfg, fp, [GEN % g, BRANCH])
    print('指针推好了 %s（第 %d 代，n=%s）' % (commit[:10], g, cfg['n']))
    try:
        r = fetch('https://purge.jsdelivr.net/gh/%s@%s/front.json' % (cfg['repo'], BRANCH), 20000)
        print('叫 jsDelivr 清了一遍老地址：', ' '.join(r.split())[:120])
    except Exception as e:  # noqa: BLE001
        print('清缓存那一下没成（不要紧）：', str(e)[:100])
    n = 0
    for k in range(14):
        time.sleep(8 if k else 3)
        n = look(cfg)
        if n == len(make_thin.MIRRORS):
            break
        print('  …再等等（这一代的分支 %d/%d 个镜像取得到）' % (n, len(make_thin.MIRRORS)))
    print('这一代的分支 %d/%d 个镜像取得到。认代数的薄壳（11-16c 起）这就拿得到新的；只认老地址的旧薄壳，镜像上至多晚十二个钟头。' % (n, len(make_thin.MIRRORS)))


if __name__ == '__main__':
    main()
