#!/usr/bin/env python3
# 11-22 新人查图以后的重出。读 底稿/立绘/新人查图_1122/重出单_*.tsv（键<Tab>sheet|art|faces|cell:<格>），
# 旧图挪进 out/立绘_<纪>_备选/<键>/查图前_1122/，sheet、art、faces 交 gpt_sheet 补缺，cell:<格> 交 fix_cell（FIX_WORK=新人_1122）。
#   "<ComfyUI venv python>" -X utf8 底稿/立绘/tools/redo_newcast.py plan     只列
#   "<ComfyUI venv python>" -X utf8 底稿/立绘/tools/redo_newcast.py run      挪图、出图、出单格对照
# 单格查过以后：FIX_WORK=新人_1122 FIX_BAK=查图前_1122 CAST_SET=<纪> fix_cell.py apply <单格单.json>
import glob
import json
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
CHK = os.path.join(ROOT, '底稿', '立绘', '新人查图_1122')
PY = sys.executable
BAK = os.environ.get('REDO_BAK', '查图前_1122')
LIST = os.environ.get('REDO_LIST', '重出单_[A-Z].tsv')   # 二回：REDO_LIST='重出单_二回_*.tsv' REDO_BAK=查图二回前_1122 REDO_WORK=新人二回_1122
WORK = os.environ.get('REDO_WORK', '新人_1122')
FIRST = ['q3x_tolun', 'q2x_karonva']        # 别人拿它们的头像当参考，先出


def set_of(k):
    for f in glob.glob(os.path.join(COMFY, 'out', '新人查图_1122', '份_*.tsv')):
        for l in open(f, encoding='utf-8'):
            p = l.rstrip('\n').split('\t')
            if p[1] == k:
                return p[0]
    raise SystemExit('找不到纪：' + k)


def load():
    jobs = {}
    for f in sorted(glob.glob(os.path.join(CHK, LIST))):
        for l in open(f, encoding='utf-8'):
            l = l.strip()
            if not l or l.startswith('#'):
                continue
            k, how = [x.strip() for x in l.split('\t')[:2]]
            jobs[k] = how
    return jobs


def move(s, k, names):
    d = os.path.join(COMFY, 'out', '立绘_' + s, k)
    dst = os.path.join(COMFY, 'out', '立绘_%s_备选' % s, k, BAK)
    os.makedirs(dst, exist_ok=True)
    for n in names:
        for p in glob.glob(os.path.join(d, n)):
            if os.path.isfile(p):
                shutil.move(p, os.path.join(dst, os.path.basename(p)))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    jobs = load()
    order = [k for k in FIRST if k in jobs] + [k for k in jobs if k not in FIRST]
    cells = {}
    for k in order:
        how = jobs[k]
        s = set_of(k)
        print(s, k, how)
        if cmd != 'run':
            continue
        if how.startswith('cell:'):
            cells.setdefault(s, []).append({'en': k, 'cell': how[5:]})
            continue
        if how == 'sheet':
            move(s, k, ['*.png', '*.log'])
        elif how == 'art':
            move(s, k, ['art.png', 'art.log'])
        elif how == 'faces':
            move(s, k, ['faces.png', 'faces_raw.png', 'faces.log'])
        else:
            print('  不认得', how)
            continue
        subprocess.run([PY, '-X', 'utf8', 'gpt_sheet.py', k], cwd=COMFY, env=dict(os.environ, CAST_SET=s))
    if cmd != 'run':
        print(len(order), '位；单格', sum(1 for h in jobs.values() if h.startswith('cell:')))
        return
    for s, js in cells.items():
        jp = os.path.join(CHK, ('单格_%s.json' if WORK == '新人_1122' else '单格_' + WORK + '_%s.json') % s)
        json.dump(js, open(jp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        env = dict(os.environ, CAST_SET=s, FIX_WORK=WORK)
        subprocess.run([PY, '-X', 'utf8', 'fix_cell.py', 'run', jp], cwd=COMFY, env=env)
        subprocess.run([PY, '-X', 'utf8', 'fix_cell.py', 'sheet', 'out/%s/对照_%s.jpg' % (WORK, s), jp], cwd=COMFY, env=env)
    print('重出跑完')


if __name__ == '__main__':
    main()
