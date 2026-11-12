#!/usr/bin/env python3
# 把 ext/ 里那几个测试桩推到图床仓库的 probe 分支（孤立分支，跟 comfy/gh_img_up.py 一个路子），地址钉提交号，清单写 ext_manifest.json。
# 推送走本机 git 的凭据管理器，不经手密码和令牌。
# 用法：python push_ext.py [--repo waitlist886-cloud/aldran-img] [--dry]
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, 'ext')
opt = {a.split('=')[0]: (a.split('=', 1)[1] if '=' in a else True) for a in sys.argv[1:] if a.startswith('--')}
REPO = opt.get('--repo', 'waitlist886-cloud/aldran-img')
BRANCH = 'probe'


def git(cwd, *a):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError('git %s 失败：%s' % (' '.join(a[:2]), (r.stderr or r.stdout).strip()[-400:]))
    return r.stdout.strip()


files = sorted(f for f in os.listdir(EXT) if os.path.isfile(os.path.join(EXT, f)))
print('要推的：', files)
if '--dry' in opt:
    sys.exit(0)
tmp = tempfile.mkdtemp(prefix='ghprobe_')
try:
    git(tmp, 'init', '-q')
    git(tmp, 'checkout', '-q', '-b', BRANCH)
    for f in files:
        shutil.copy2(os.path.join(EXT, f), os.path.join(tmp, f))
    with open(os.path.join(tmp, '.gitattributes'), 'w', newline='\n') as fh:
        fh.write('* -text\n')          # 文件照原样进库，不换行尾
    git(tmp, 'add', '-A')
    git(tmp, '-c', 'user.name=Claude', '-c', 'user.email=noreply@anthropic.com', 'commit', '-q', '-m', 'probe：门面探针的测试桩 %d 个' % len(files))
    commit = git(tmp, 'rev-parse', 'HEAD')
    git(tmp, 'push', '-q', '--force', 'https://github.com/%s.git' % REPO, 'HEAD:refs/heads/%s' % BRANCH)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
man = {'repo': REPO, 'branch': BRANCH, 'commit': commit, 'path': '/gh/%s@%s/' % (REPO, commit),
       'base': 'https://cdn.jsdelivr.net/gh/%s@%s/' % (REPO, commit),
       'raw': 'https://raw.githubusercontent.com/%s/%s/' % (REPO, commit),
       'files': {f: os.path.getsize(os.path.join(EXT, f)) for f in files}}
json.dump(man, open(os.path.join(HERE, 'ext_manifest.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print('推好了，提交', commit)
print(man['base'])
