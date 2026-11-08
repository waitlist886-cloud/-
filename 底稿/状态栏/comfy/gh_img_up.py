#!/usr/bin/env python3
# 11-07 晚：ImgBB 从 15:02 UTC 起一直限流，用户回“那可能直接github吧，反正公开也没什么”。图放进 GitHub 的公开仓库，走 jsDelivr 取。
# jsDelivr 的限制（它的 README）：GitHub 上单个文件不过 20 MB，一个包（仓库的一个版本）不过 150 MB。所以一套图一个孤立分支，
# 大的照文件名顺序切成几段，一段不过 120 MB；地址钉在那一段的提交上（jsDelivr 对提交号永久缓存，分支名只缓存 12 个钟头）：
#   https://cdn.jsdelivr.net/gh/<仓库>@<提交号>/<文件名>
# 清单写 out/图床/gh_<套>.json（文件名 → sha1、size、url、commit），跟 imgbb_*.json 一个样子，用 url 那一栏。
# 推送走本机 git 的凭据管理器（跟主仓库一样），不经手密码和令牌。仓库要用户先在 GitHub 上建好（公开、空的）。
# 用法：python gh_img_up.py <套> <图目录> [--repo waitlist886-cloud/aldran-img] [--dry]
#   套用 ASCII 名字（1001、strife、bronze、pre、salvis、zhuguo、moonepic、epic、gods），当分支名；已经推过、内容没变的段跳过。
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out', '图床')
CAP = 120 * 1024 * 1024
FILE_CAP = 19 * 1024 * 1024
args = [a for a in sys.argv[1:] if not a.startswith('--')]
opt = {a.split('=')[0]: (a.split('=', 1)[1] if '=' in a else True) for a in sys.argv[1:] if a.startswith('--')}
SET, SRC = args[0], args[1]
REPO = opt.get('--repo', 'waitlist886-cloud/aldran-img')
DRY = '--dry' in opt
assert SET.isascii() and SET.replace('_', '').isalnum(), '套名用 ASCII：' + SET


def sha1(p):
    h = hashlib.sha1()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def git(cwd, *a):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError('git %s 失败：%s' % (' '.join(a[:2]), (r.stderr or r.stdout).strip()[-400:]))
    return r.stdout.strip()


files = sorted(f for f in os.listdir(SRC) if os.path.isfile(os.path.join(SRC, f)) and f.endswith('.webp') and not f.startswith(('.', '_')))   # 只传烘好的图，查图时留在目录里的拼图不传
big = [f for f in files if os.path.getsize(os.path.join(SRC, f)) > FILE_CAP]
assert not big, ('单个文件过 19 MB，jsDelivr 不给', big[:5])
chunks, cur, size = [], [], 0
for f in files:
    s = os.path.getsize(os.path.join(SRC, f))
    if cur and size + s > CAP:
        chunks.append(cur)
        cur, size = [], 0
    cur.append(f)
    size += s
if cur:
    chunks.append(cur)
man_path = os.path.join(OUT, 'gh_%s.json' % SET)
man = json.load(open(man_path, encoding='utf-8')) if os.path.exists(man_path) else {}
print('== %s：%d 张，%.0f MB，分 %d 段' % (SET, len(files), sum(os.path.getsize(os.path.join(SRC, f)) for f in files) / 1048576, len(chunks)))
for n, part in enumerate(chunks, 1):
    branch = SET if len(chunks) == 1 else '%s_%d' % (SET, n)
    sums = {f: sha1(os.path.join(SRC, f)) for f in part}
    if all(man.get(f, {}).get('sha1') == sums[f] and man[f].get('branch') == branch for f in part):
        print('   %s 没变，跳过' % branch)
        continue
    if DRY:
        print('   %s：%d 张（--dry 不推）' % (branch, len(part)))
        continue
    tmp = tempfile.mkdtemp(prefix='ghimg_')
    try:
        git(tmp, 'init', '-q')
        git(tmp, 'checkout', '-q', '-b', branch)
        for f in part:
            shutil.copy2(os.path.join(SRC, f), os.path.join(tmp, f))
        git(tmp, 'add', '-A')
        git(tmp, '-c', 'user.name=Claude', '-c', 'user.email=noreply@anthropic.com', 'commit', '-q', '-m', '%s：%d 张' % (branch, len(part)))
        commit = git(tmp, 'rev-parse', 'HEAD')
        git(tmp, 'push', '-q', '--force', 'https://github.com/%s.git' % REPO, 'HEAD:refs/heads/%s' % branch)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for f in part:
        man[f] = {'sha1': sums[f], 'size': str(os.path.getsize(os.path.join(SRC, f))), 'branch': branch, 'commit': commit,
                  'url': 'https://cdn.jsdelivr.net/gh/%s@%s/%s' % (REPO, commit, f)}
    os.makedirs(OUT, exist_ok=True)
    json.dump(man, open(man_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('   %s 推好了：%d 张，提交 %s' % (branch, len(part), commit[:10]))
print('清单', man_path, len(man), '条')
