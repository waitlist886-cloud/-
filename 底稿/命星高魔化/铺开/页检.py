# -*- coding: utf-8 -*-
"""铺开·页检：一页并完、重拼以后，拿提交里的那一页当底，比几样检查的数。一页一行，数没变坏的只印「同」。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/页检.py 拼好的页.md… [--ref 提交号]
比的：cardscan 合计、check_people_v7 硬问题、authormark 合计、ngram hits、regex_check 硬问题、starlint 过线。
另印受保护的行里变了几类（星标题、条目设置、固定锚定、底座、体态数据、## 标题）。"""
import io, os, re, sys, subprocess, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
PY = [sys.executable, '-I', '-X', 'utf8']
ref = sys.argv[sys.argv.index('--ref') + 1] if '--ref' in sys.argv else 'HEAD'
files = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] != '--ref']


def run(args):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=ROOT)
    return (r.stdout or '') + (r.stderr or '')


def num(pat, s, default=-1):
    m = re.findall(pat, s)
    return int(m[-1]) if m else default


def measure(path):
    d = {}
    d['卡面'] = num(r'合计\s*(\d+)', run(PY + ['tools/cardscan.py', path]))
    o = run(PY + ['tools/check_people_v7.py', path, '.'])
    d['硬'] = num(r'硬问题合计\s*(\d+)', o)
    d['作者'] = num(r'合计\s*(\d+)', run(PY + ['tools/authormark.py', path]))
    d['撞句'] = num(r'hits\s*(\d+)', run(PY + ['tools/ngram.py', path, '语料'])) if os.path.isdir(os.path.join(ROOT, '语料')) else -1
    d['正则'] = num(r'硬问题合计\s*(\d+)', run(PY + ['tools/regex_check.py', path]))
    d['星线'] = num(r'过线\s*(\d+)', run(PY + ['tools/starlint.py', path]))
    return d


PROT = [('星标题', re.compile(r'^### .+ \((Art|Special|Passive)')), ('条目设置', re.compile(r'^> 条目设置')),
        ('固定锚定', re.compile(r'^固定锚定：')), ('底座', re.compile(r'^底座：')), ('体态', re.compile(r'^体态数据：')),
        ('二级标题', re.compile(r'^## '))]


def prot(path):
    out = {k: [] for k, _ in PROT}
    for l in io.open(path, encoding='utf-8', newline='').read().replace('\r', '').split('\n'):
        for k, rx in PROT:
            if rx.match(l):
                out[k].append(l)
    return out


tmp = tempfile.mkdtemp(prefix='yejian_')
for f in files:
    rel = os.path.relpath(os.path.abspath(f), ROOT).replace('\\', '/')
    old = os.path.join(tmp, os.path.basename(f))
    r = subprocess.run(['git', 'show', '%s:%s' % (ref, rel)], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        print('%s｜提交里没有这一页' % rel)
        continue
    open(old, 'wb').write(r.stdout)
    a, b = measure(old), measure(os.path.join(ROOT, rel))
    worse = ['%s %d→%d' % (k, a[k], b[k]) for k in a if b[k] > a[k]]
    better = ['%s %d→%d' % (k, a[k], b[k]) for k in a if b[k] < a[k]]
    pa, pb = prot(old), prot(os.path.join(ROOT, rel))
    ch = []
    for k, _ in PROT:
        sa, sb = pa[k], pb[k]
        if sa != sb:
            n = len(set(sa) ^ set(sb))
            ch.append('%s %d' % (k, n))
    print('%s｜%s%s｜受保护的行变了：%s' % (os.path.basename(f), ('变坏 ' + '、'.join(worse)) if worse else '同',
                                   ('，变好 ' + '、'.join(better)) if better else '', '、'.join(ch) or '无'))
