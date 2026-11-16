#!/usr/bin/env python3
# 传奇之陨新添那一批：照改法文件把要改、要重画的原图挪成 <键>_a0.png，列出要出的键（11-16）。
#   python -I -X utf8 底稿/门面/小样_纷争纪书/scenes/查图/fix_apply.py [改法_X.json …] [--redo 键,键] [--flip 键] [--apply]
#   不写改法文件就读同目录所有 改法_*.json。--redo：整幅重画的键（场面稿另改过了）。--flip：整幅左右翻转（要带 PIL 的 Python）。
#   不加 --apply 只报。挪过的不再挪（<键>_a0.png 已经在的跳过）。
# 出图：cd 底稿/状态栏/comfy && CG_WORKERS=4 <带 PIL 的 python> -X utf8 gpt_cg2.py <键…>
#   判“改”的键 gpt_cg2.py 会照改法拿 <键>_a0.png 当底只改那一处；--redo 的键照（改过的）场面稿整幅重出。
import glob
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
IMG = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'out', '门面_原画_纷争纪')


def main():
    args = sys.argv[1:]
    apply = '--apply' in args
    redo, flip = [], []
    files = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--redo':
            redo += [x for x in args[i + 1].split(',') if x]
            i += 2
        elif a == '--flip':
            flip += [x for x in args[i + 1].split(',') if x]
            i += 2
        elif a.startswith('--'):
            i += 1
        else:
            files.append(a)
            i += 1
    if not files and not redo and not flip:
        files = sorted(glob.glob(os.path.join(HERE, '改法_*.json')))
    todo, skip, again = [], [], []
    for f in files:
        d = json.load(open(f, encoding='utf-8'))
        for k, v in d.items():
            if v.get('verdict') == '改':
                todo.append(k)
            elif v.get('verdict') == '重画':
                again.append(k)
            else:
                skip.append(k)
    todo += redo
    moved = []
    for k in todo:
        src, dst = os.path.join(IMG, k + '.png'), os.path.join(IMG, k + '_a0.png')
        if os.path.exists(dst):
            continue
        assert os.path.exists(src), ('没有这幅图', k)
        if apply:
            os.rename(src, dst)
            if os.path.exists(os.path.join(IMG, k + '.log')):
                os.replace(os.path.join(IMG, k + '.log'), os.path.join(IMG, k + '_a0.log'))
        moved.append(k)
    for k in flip:
        src, dst = os.path.join(IMG, k + '.png'), os.path.join(IMG, k + '_a0.png')
        if os.path.exists(dst):
            continue
        if apply:
            from PIL import Image, ImageOps
            os.rename(src, dst)
            ImageOps.mirror(Image.open(dst)).save(src)
        print('左右翻转', k, '' if apply else '（没动，加 --apply）')
    print('要改 %d 幅（其中整幅重画 %d），这一回挪成 _a0 的 %d 幅%s' % (len(todo), len(redo), len(moved), '' if apply else '（没动，加 --apply）'))
    print('不改 %d 幅：%s' % (len(skip), ' '.join(skip)))
    if again:
        print('改法里判了重画、要另改场面稿的 %d 幅：%s' % (len(again), ' '.join(again)))
    print('要出的键：')
    print(' '.join(todo))


if __name__ == '__main__':
    main()
