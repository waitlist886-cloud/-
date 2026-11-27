#!/usr/bin/env python3
# 11-26 音乐探针：把 ext/ 里三段测试音（bgm_a 低音长鸣、bgm_b 鼓点、bgm_c 三音琶音，各 20 秒，开头一声高音“叮”）推到图床仓库的 bgm_probe 分支。
# 照 外链样式探针/push_ext.py 的路子：孤立分支，地址钉提交号，清单写 bgm_manifest.json。推送走本机 git 的凭据管理器。
# 三段音怎么合成的写在 测法.md 末尾（本机 ffmpeg 的 aevalsrc）。
# 用法：python -I -X utf8 push_bgm.py [--dry]
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, 'ext')
REPO, BRANCH = 'waitlist886-cloud/aldran-img', 'bgm_probe'
MIRRORS = ['cdn', 'fastly', 'testingcf', 'gcore']


def git(cwd, *a):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError('git %s 失败：%s' % (' '.join(a[:2]), (r.stderr or r.stdout).strip()[-400:]))
    return r.stdout.strip()


files = sorted(f for f in os.listdir(EXT) if os.path.isfile(os.path.join(EXT, f)))
print('要推的：', files)
if '--dry' in sys.argv:
    sys.exit(0)
tmp = tempfile.mkdtemp(prefix='ghbgm_')
try:
    git(tmp, 'init', '-q')
    git(tmp, 'checkout', '-q', '-b', BRANCH)
    for f in files:
        shutil.copy2(os.path.join(EXT, f), os.path.join(tmp, f))
    with open(os.path.join(tmp, '.gitattributes'), 'w', newline='\n') as fh:
        fh.write('* -text\n')
    git(tmp, 'add', '-A')
    git(tmp, '-c', 'user.name=Claude', '-c', 'user.email=noreply@anthropic.com', 'commit', '-q', '-m', 'bgm_probe：音乐探针的测试音 %d 段' % len(files))
    commit = git(tmp, 'rev-parse', 'HEAD')
    git(tmp, 'push', '-q', 'https://github.com/%s.git' % REPO, 'HEAD:refs/heads/%s' % BRANCH)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
path = '/gh/%s@%s/' % (REPO, commit)
man = {'repo': REPO, 'branch': BRANCH, 'commit': commit, 'path': path,
       'base': 'https://cdn.jsdelivr.net' + path,
       'mirrors': {m: 'https://%s.jsdelivr.net%s' % (m, path) for m in MIRRORS},
       'raw': 'https://raw.githubusercontent.com/%s/%s/' % (REPO, commit),
       'files': {f: os.path.getsize(os.path.join(EXT, f)) for f in files}}
with open(os.path.join(HERE, 'bgm_manifest.json'), 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(man, fh, ensure_ascii=False, indent=1)
print('推好了，提交', commit)
print(man['base'])
