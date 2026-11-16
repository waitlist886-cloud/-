#!/usr/bin/env python3
# 把门面（外壳和四本书）推上图床仓库（11-15 拼装那一轮）。卡里的介绍页只留一段薄壳，页面、数据和图都从这里取。
#   python -I -X utf8 底稿/门面/共用/deploy_front.py [段名…] [--dry] [--list]
# 一段一个孤立分支（照 底稿/状态栏/comfy/gh_img_up.py 的做法：jsDelivr 一个版本不过 150 MB、单个文件不过 20 MB，这里一段不过 120 MB），
# 地址钉提交号：https://cdn.jsdelivr.net/gh/<仓库>@<提交>/<路径>。内容没变的段跳过。推送走本机 git 的凭据管理器。
# 一本书拆三段：页面和小图（front_<书>）、原画（front_<书>_cg）、档案页的立绘加表情（front_<书>_ps），迷宫纪没有原画那一段。
# 段里的路径就是页面上写的相对路径（assets/cg/x.webp 在 front_<书>_cg 里也放在 assets/cg/x.webp），外壳照 front.json 里各段的提交号拼地址。
# 推完写 共用/front.json：{"repo", "shell": 提交, "books": {"moon": {"core": 提交, "parts": {"assets/cg/": 提交, "assets/ps/": 提交}}, …}}，
# make_thin.py 照它出薄壳。清单（每段多少文件、多大、内容的哈希）记在 共用/front_manifest.json。
# 这是往公开仓库推：四本书的页面、数据里的字（时代页、卡片、世界之书）都在里头，跟卡的介绍页一样谁都看得到。
import fnmatch
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.normpath(os.path.join(HERE, '..'))
REPO = 'waitlist886-cloud/aldran-img'
CAP = 120 * 1024 * 1024
FILE_CAP = 19 * 1024 * 1024
KEEP_EXT = ('.html', '.js', '.css', '.json', '.webp', '.png', '.jpg', '.svg', '.woff2', '.mp3', '.ogg')
BOOKS = {'moon': '小样_月银纪书', 'strife': '小样_纷争纪书', 'bronze': '小样_山铜纪书', 'maze': '小样_迷宫纪书'}
SPLIT = {'moon': ['assets/cg/', 'assets/ps/'], 'strife': ['assets/cg/', 'assets/ps/'], 'bronze': ['assets/cg/', 'assets/ps/'], 'maze': ['assets/ps/']}
# 书的目录里不往上推的：留底的旧页面、单独打开用的壳、拷进来的共用那一份（外壳那一段里有）、书里已经不用的旧图
SKIP = ['index_*.html', 'local.html', 'common/*', '共用/*', 'scenes/*', 'node_modules/*', 'assets/_*', '*/_*',
        'assets/stele/b[0-9][0-9]*.webp',          # 山铜纪改形制以前的旧碑图
        'assets/map/*', 'assets/ui/*']             # 月银纪那一本原来自带的地图和入口图，挪进共用了
UNITS = {'front_shell': {'src': '小样_外壳', 'take': ['index.html', 'shell.js', 'shell.css', 'old1001.html', 'common/*', 'data/*', 'assets/*'], 'skip': ['local.html', '*/_*']}}
for b, d in BOOKS.items():
    UNITS['front_' + b] = {'src': d, 'take': ['index.html', 'data/*', 'assets/*'], 'skip': SKIP + [p + '*' for p in SPLIT[b]]}
    for p in SPLIT[b]:
        UNITS['front_%s_%s' % (b, p.split('/')[1])] = {'src': d, 'take': [p + '*'], 'skip': ['*/_*']}


def files_of(u):
    base = os.path.join(FRONT, u['src'])
    out = []
    for sub, dirs, fs in os.walk(base):
        for f in fs:
            rel = os.path.relpath(os.path.join(sub, f), base).replace(os.sep, '/')
            if not rel.lower().endswith(KEEP_EXT):
                continue
            if not any(fnmatch.fnmatch(rel, t) for t in u['take']):
                continue
            if any(fnmatch.fnmatch(rel, s) for s in u.get('skip', [])):
                continue
            assert rel.isascii(), ('路径里有非 ASCII 字符，图床上不放', rel)
            out.append(rel)
    return sorted(out)


def sha1(p):
    h = hashlib.sha1()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def git(cwd, *a):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError('git %s 失败：%s' % (' '.join(a[:2]), (r.stderr or r.stdout).strip()[-600:]))
    return r.stdout.strip()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry, only_list = '--dry' in sys.argv, '--list' in sys.argv
    todo = args or list(UNITS)
    man_path = os.path.join(HERE, 'front_manifest.json')
    man = json.load(open(man_path, encoding='utf-8')) if os.path.exists(man_path) else {}
    for name in todo:
        u = UNITS[name]
        base = os.path.join(FRONT, u['src'])
        fs = files_of(u)
        size = sum(os.path.getsize(os.path.join(base, f)) for f in fs)
        big = [f for f in fs if os.path.getsize(os.path.join(base, f)) > FILE_CAP]
        assert not big, ('单个文件过 19 MB', big[:5])
        assert size <= CAP, ('%s 这一段 %.0f MB，过了 120 MB，要再拆' % (name, size / 1048576))
        assert fs, name + ' 一个文件也没有'
        need = {'front_shell': ['index.html', 'shell.js', 'shell.css', 'old1001.html', 'common/codex.js', 'common/codex.css', 'common/data/wb.json', 'data/build.json']}.get(name, ['index.html'] if name.count('_') == 1 else [])
        lack = [f for f in need if f not in fs]
        assert not lack, ('%s 少了要紧的文件（old1001.html 是 make_old1001.py 出的，common/ 是 sync.py 拷的）' % name, lack)
        h = hashlib.sha1()
        for f in fs:
            h.update(f.encode() + b'\0' + sha1(os.path.join(base, f)).encode() + b'\n')
        digest = h.hexdigest()
        line = '%-18s %4d 个文件 %6.1f MB' % (name, len(fs), size / 1048576)
        if only_list:
            print(line)
            for f in fs:
                print('     ', f)
            continue
        if man.get(name, {}).get('hash') == digest:
            print(line, ' 没变，跳过', man[name]['commit'][:10])
            continue
        if dry:
            print(line, ' 要推（--dry 不推）')
            continue
        tmp = tempfile.mkdtemp(prefix='front_')
        try:
            git(tmp, 'init', '-q')
            git(tmp, 'config', 'core.autocrlf', 'false')          # 文件原样进库（不然 Windows 上带回车的文本会被改成不带的，图床上的大小就跟本地对不上）
            git(tmp, 'checkout', '-q', '-b', name)
            for f in fs:
                t = os.path.join(tmp, f)
                os.makedirs(os.path.dirname(t), exist_ok=True)
                shutil.copy2(os.path.join(base, f), t)
            git(tmp, 'add', '-A')
            git(tmp, '-c', 'user.name=Claude', '-c', 'user.email=noreply@anthropic.com', 'commit', '-q', '-m', '%s：%d 个文件' % (name, len(fs)))
            commit = git(tmp, 'rev-parse', 'HEAD')
            git(tmp, 'push', '-q', '--force', 'https://github.com/%s.git' % REPO, 'HEAD:refs/heads/%s' % name)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        man[name] = {'commit': commit, 'hash': digest, 'files': len(fs), 'bytes': size}
        json.dump(man, open(man_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(line, ' 推好了', commit[:10])
    if only_list or dry:
        return
    if all(('front_' + b) in man for b in BOOKS) and 'front_shell' in man:
        cfg = {'repo': REPO, 'shell': man['front_shell']['commit'], 'books': {}}
        for b in BOOKS:
            cfg['books'][b] = {'core': man['front_' + b]['commit'], 'parts': {p: man['front_%s_%s' % (b, p.split('/')[1])]['commit'] for p in SPLIT[b] if ('front_%s_%s' % (b, p.split('/')[1])) in man}}
        json.dump(cfg, open(os.path.join(HERE, 'front.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('front.json 写好了')


if __name__ == '__main__':
    main()
