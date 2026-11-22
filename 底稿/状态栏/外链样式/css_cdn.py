#!/usr/bin/env python3
# 卡的样式挪上图床（11-22）。11-21 外链样式探针在手机上跑通以后做的：卡的样式格（injectStyles，四纪大框里一百五十万字）整份搬到
# 图床仓库 waitlist886-cloud/aldran-img 的 card_css 分支，卡里的样式格只留一行说明，显示正则末尾添一条，在每条回复的末尾插一个
# <link rel="stylesheet">。往后美术和样式加多少都不占卡。
#   python -I -X utf8 底稿/状态栏/外链样式/css_cdn.py <卡.json> <输出的卡.json> [--no-push]
# 先后（四纪大框）：make_four_era_card.py 打出来以后、拷 _原介绍页.json 和 into_card.py 以前跑这一支。
#
# 做的事：
#   1. 样式照平台的规矩加 .custom-styles 作用域（scope.mjs，postcss；第一次在本目录 npm install）。平台只对样式格做这一步，
#      link 载进来的样式它不管，所以先做好，跟原来放在样式格里一个效果（平台拿掉的 @import、@supports 这些也照样拿掉）。
#   2. 照内容的 sha256 起名 aldran_<前十二位>.css，推到 card_css 分支（不强推，旧的文件和提交都留着，发出去的老卡一直取得到），
#      地址钉提交号，清单记在 manifest.json；同一份样式推过了就照清单用原来那个地址，不再推。
#   3. 从 jsDelivr 取一回，大小对上才往下走（也顺带把它预热进 CDN 缓存）。
#   4. 卡：injectStyles 换成一行注释，assistantRegexReplace 末尾添一条（只在前端显示，不进给模型的上下文）：
#      /$/ → 空一行加 <link rel="stylesheet" href="…">。日里的聊天页是虚拟列表，同时挂在页面上的只有视口附近四五行，
#      每条回复各插一份，叠起来也就两三份（11-22 本地量过：五条回复每条一份，样式重算 10ms，只插一份 5ms）。
# 核对：输出的卡跟输入的卡只差 injectStyles、injectStylesSizeBytes 和多出来的那一条正则。
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, 'out')
MAN = os.path.join(HERE, 'manifest.json')
REPO = 'waitlist886-cloud/aldran-img'
BRANCH = 'card_css'
MARK = '/* 奥尔德兰：样式在图床'
LINK_RULE_TAG = 'data-aldran-css'


def git(cwd, *a, check=True):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if check and r.returncode:
        raise RuntimeError('git %s 失败：%s' % (' '.join(a[:2]), (r.stderr or r.stdout).strip()[-400:]))
    return r


def scope(css):
    os.makedirs(OUTDIR, exist_ok=True)
    src = os.path.join(OUTDIR, '_raw.css')
    dst = os.path.join(OUTDIR, '_scoped.css')
    open(src, 'w', encoding='utf-8', newline='').write(css)
    if not os.path.isdir(os.path.join(HERE, 'node_modules', 'postcss')):
        subprocess.run('npm install --silent', cwd=HERE, shell=True, check=True)
    r = subprocess.run(['node', os.path.join(HERE, 'scope.mjs'), src, dst], capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        raise SystemExit('scope.mjs 失败：' + r.stderr[-800:])
    print('作用域', r.stdout.strip())
    return open(dst, encoding='utf-8', newline='').read()


def push(fname, data):
    tmp = tempfile.mkdtemp(prefix='ghcss_')
    try:
        url = 'https://github.com/%s.git' % REPO
        has = git(tmp, 'ls-remote', '--heads', url, BRANCH).stdout.strip()
        if has:
            git(tmp, 'clone', '-q', '--depth', '1', '--branch', BRANCH, url, 'r')
            wd = os.path.join(tmp, 'r')
        else:
            wd = os.path.join(tmp, 'r')
            os.makedirs(wd)
            git(wd, 'init', '-q')
            git(wd, 'checkout', '-q', '-b', BRANCH)
            with open(os.path.join(wd, '.gitattributes'), 'w', newline='\n') as fh:
                fh.write('* -text\n')      # 文件照原样进库，不换行尾
        with open(os.path.join(wd, fname), 'wb') as fh:
            fh.write(data)
        git(wd, 'add', '-A')
        git(wd, '-c', 'user.name=Claude', '-c', 'user.email=noreply@anthropic.com', 'commit', '-q', '-m', 'card_css：%s' % fname)
        commit = git(wd, 'rev-parse', 'HEAD').stdout.strip()
        git(wd, 'push', '-q', url, 'HEAD:refs/heads/%s' % BRANCH)
        return commit
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def fetch_check(url, size):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'aldran-css-check'})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
                ct = r.headers.get('Content-Type', '')
            if len(body) == size:
                print('取到了', len(body), '字节', ct)
                return
            print('大小对不上', len(body), size)
        except Exception as ex:
            print('第', i + 1, '回没取到：', ex)
    raise SystemExit('图床上的样式取不到或者大小不对：' + url)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    src, dst = args[:2]
    card = json.load(open(src, encoding='utf-8'))
    css = card.get('injectStyles') or ''
    if css.startswith(MARK):
        raise SystemExit('这张卡的样式已经在图床上了')
    rules = card['assistantRegexReplace']
    assert not any(LINK_RULE_TAG in r['replaceString'] for r in rules)
    scoped = scope(css)
    data = scoped.encode('utf-8')
    sha = hashlib.sha256(data).hexdigest()[:12]
    fname = 'aldran_%s.css' % sha
    open(os.path.join(OUTDIR, fname), 'wb').write(data)
    man = json.load(open(MAN, encoding='utf-8')) if os.path.exists(MAN) else {}
    if fname in man:
        commit = man[fname]['commit']
        print('这一份推过了', commit)
    elif '--no-push' in sys.argv:
        commit = 'NOPUSH'
    else:
        commit = push(fname, data)
        man[fname] = {'commit': commit, 'bytes': len(data), 'src_chars': len(css)}
        json.dump(man, open(MAN, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
        print('推好了', commit)
    url = 'https://cdn.jsdelivr.net/gh/%s@%s/%s' % (REPO, commit, fname)
    if commit != 'NOPUSH':
        fetch_check(url, len(data))
    stub = '%s %s ，显示正则的末一条在每条回复末尾插 link 载进来（css_cdn.py，11-22）。原样式 %d 字。 */' % (MARK, url, len(css))
    card['injectStyles'] = stub
    if 'injectStylesSizeBytes' in card:
        card['injectStylesSizeBytes'] = len(stub.encode('utf-8'))
    rules.append({'regex': '/$/', 'replaceString': '\n\n<link rel="stylesheet" %s href="%s">' % (LINK_RULE_TAG, url),
                  'enabled': True, 'messageRole': 'assistant', 'applyMode': 'front-end'})
    old = json.load(open(src, encoding='utf-8'))
    diff = sorted(k for k in set(old) | set(card) if old.get(k) != card.get(k))
    assert set(diff) <= {'injectStyles', 'injectStylesSizeBytes', 'assistantRegexReplace'}, diff
    assert old['assistantRegexReplace'] == rules[:-1]
    json.dump(card, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('ok', dst, os.path.getsize(dst) // 1024, 'KB（原', os.path.getsize(src) // 1024, 'KB）；样式', len(css), '字挪上图床', url)


if __name__ == '__main__':
    main()
