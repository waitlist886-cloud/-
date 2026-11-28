#!/usr/bin/env python3
# 大图书馆洗稿试点（11-28）：一本书一个临时工作目录，放进原稿、人设包、规矩、洗稿 skill，交给 Codex（GPT）洗，交回 洗后.md 和 改动说明.md。
#   python -I -X utf8 底稿/洗稿_图书馆/run_wash.py 书名 [书名…] [--round N] [--note 打回意见.md]
# 书名是 书稿/ 下去掉 .md 的文件名（如 纷争纪廊_夜医手记）。人设包照书名末段找 人设/<末段>.md。
# 出：底稿/洗稿_图书馆/试点/<书名>/第N轮/ 下 洗后.md、改动说明.md、codex.log；打回时把上一轮的洗后稿当原稿、意见附进去。
import os, shutil, subprocess, sys, tempfile, glob, io

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
HERE = os.path.join(ROOT, '底稿', '洗稿_图书馆')
BOOKS = os.path.join(ROOT, '底稿', '门面', '第二轮', '大图书馆', '书稿')
SKILL = os.path.join(ROOT, '.claude', 'skills', 'rewrite-natural-prose')
CODEX = sorted(glob.glob(os.path.expandvars(r'%LOCALAPPDATA%\OpenAI\Codex\bin\*\codex.exe')), key=os.path.getmtime)[-1]


def rules():
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import importlib.util
    spec = importlib.util.spec_from_file_location('cp', os.path.join(ROOT, 'tools', 'check_people_v7.py'))
    src = open(os.path.join(ROOT, 'tools', 'check_people_v7.py'), encoding='utf-8').read()
    ns = {}
    exec(compile('\n'.join(l for l in src.split('\n') if l.startswith(('BAN_P', 'BAN_W', 'MOON', 'TECH', "         '"))), 'x', 'exec'), ns)
    out = ['# 规矩', '', '## 禁用标点', '、'.join(ns['BAN_P']), '', '## 禁词（一律不用）', '、'.join(ns['BAN_W'] + ns['MOON'] + ns['TECH']), '']
    out += ['## 旧字、中式口语换成西幻说法（整张换词表）', '', open(os.path.join(ROOT, '旧字换词表_10-20.md'), encoding='utf-8').read(), '']
    out += ['## 八股口径（这一卷自己的病，洗的时候照它躲）', '', open(os.path.join(ROOT, '底稿', '排查_八股', '口径.md'), encoding='utf-8').read()]
    return '\n'.join(out)


def run(book, rnd, note):
    out = os.path.join(HERE, '试点', book, '第%d轮' % rnd)
    os.makedirs(out, exist_ok=True)
    d = tempfile.mkdtemp(prefix='aldran_wash_')
    src = os.path.join(BOOKS, book + '.md') if rnd == 1 else os.path.join(HERE, '试点', book, '第%d轮' % (rnd - 1), '洗后.md')
    shutil.copy(src, os.path.join(d, '原稿.md'))
    shutil.copy(os.path.join(HERE, '人设', book.split('_', 1)[1] + '.md'), os.path.join(d, '人设.md'))
    shutil.copy(os.path.join(HERE, '派活说明_GPT.md'), os.path.join(d, '派活说明.md'))
    io.open(os.path.join(d, '规矩.md'), 'w', encoding='utf-8').write(rules())
    shutil.copytree(SKILL, os.path.join(d, 'skill'))
    prompt = '照这个目录里的 派活说明.md 做：洗 原稿.md，写出 洗后.md 和 改动说明.md。全程中文。'
    if note:
        shutil.copy(note, os.path.join(d, '打回意见.md'))
        prompt += ' 这是打回重洗：原稿.md 是你上一轮的洗后稿，先读 打回意见.md，照意见改，没点到的地方别动，改动说明.md 里逐条写怎么改的。'
    cmd = [CODEX, 'exec', '--skip-git-repo-check', '--sandbox', 'workspace-write', '-C', d, '-c', 'model_reasoning_effort="high"', '--', prompt]
    with open(os.path.join(out, 'codex.log'), 'w', encoding='utf-8') as f:
        rc = subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=3600)
    got = []
    for n in ('洗后.md', '改动说明.md'):
        p = os.path.join(d, n)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(out, n)); got.append(n)
    shutil.rmtree(d, ignore_errors=True)
    print(book, '第%d轮' % rnd, '退出码', rc, '交回', got)


if __name__ == '__main__':
    a = sys.argv[1:]
    rnd, note = 1, None
    if '--round' in a:
        i = a.index('--round'); rnd = int(a[i + 1]); del a[i:i + 2]
    if '--note' in a:
        i = a.index('--note'); note = os.path.abspath(a[i + 1]); del a[i:i + 2]
    for b in a:
        run(b, rnd, note)
