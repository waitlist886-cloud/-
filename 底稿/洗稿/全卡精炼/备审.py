#!/usr/bin/env python3
# 全卡精炼洗稿：Codex 交回来以后、派审稿人以前，主会话先做的几样（11-16）。在仓库根上跑：
#   python -I -X utf8 底稿/洗稿/全卡精炼/备审.py <份名…>
# 1. 把仓库里最新的 自查.py、洗稿说明.md 拷进活的文件夹（派活以后这两份可能又添了规矩）。
# 2. 稿/ 还没留底的留一份（稿_Codex原样/）。
# 3. 照原稿还原页首、Special 命星的头一段和凡世至强的整节（还原星头.py），栏名照原稿改回、连着的空行收掉（还原栏名.py）。
# 4. 跑自查、查栏目，把结果印出来，也写进活的文件夹的 自查_备审.txt。
# Gemini 洗的份（job.json 里 washer=gemini）在第 3 步以后多一步：改写了却没收短的节（留九成六以上，背景条不算）整节退回原稿（查没收短.py）。
import io
import json
import os
import shutil
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
BASE = 'C:/Users/waitl/codex_work/wash_1115'


def run(*a, cwd=None):
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', *a], cwd=cwd, capture_output=True)
    return r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')


for job in sys.argv[1:]:
    d = BASE + '/' + job
    print('=' * 12, job)
    for f in ('自查.py', '洗稿说明.md'):
        shutil.copy2(os.path.join(HERE, f), os.path.join(d, f))
    if not os.path.isdir(d + '/稿_Codex原样'):
        shutil.copytree(d + '/稿', d + '/稿_Codex原样')
    meta = json.load(open(d + '/job.json', encoding='utf-8'))
    for base in meta['files']:
        out = run(os.path.join(HERE, '还原星头.py'), d + '/稿/' + base, d + '/原/' + base)
        print('  ' + out.strip().split('\n')[-1])
    out = run(os.path.join(HERE, '还原节首.py'), job, '--fix', cwd=ROOT)        # 命星、人物两节开头给作者看的那一段照原稿还原
    print('  ' + out.strip().split('\n')[-1])
    out = run(os.path.join(HERE, '还原栏名.py'), '--job', job, cwd=ROOT)          # 栏名照原稿改回，对不齐的印出来
    for l in out.strip().split('\n'):
        if '栏对不齐' not in l:
            print('  ' + l.strip()[:150])
    if meta.get('washer') == 'gemini':
        # Gemini（尤其 Flash）叫它自己改过两遍还是电报的块（虚字的比例不到原稿七成），整块退回原稿，不留给审稿人重写。
        out = run(os.path.join(HERE, '还原电报.py'), job, '--apply', cwd=ROOT)
        for l in out.strip().split('\n'):
            print('  ' + l.strip()[:150])
        # 有时把一节改写一遍却没收短，这种节只担改字的风险：留九成六以上的整节退回原稿（背景条不算）。
        out = run(os.path.join(HERE, '查没收短.py'), job, '--min', '0.96', '--apply', cwd=ROOT)
        for l in out.strip().split('\n'):
            print('  ' + l.strip()[:150])
    chk = run(os.path.join(d, '自查.py'), cwd=d)
    col = run(os.path.join(HERE, '查栏目.py'), '--job', job, cwd=ROOT)
    open(d + '/自查_备审.txt', 'w', encoding='utf-8', newline='\n').write(chk + '\n' + col)
    for l in chk.strip().split('\n'):
        if l.startswith('==') or l.strip().startswith('错') or l.startswith('错 '):
            print('  ' + l.strip()[:150])
    for l in col.strip().split('\n'):
        if '！' in l:
            print('  ' + l.strip()[:150])
