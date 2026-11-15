#!/usr/bin/env python3
# 迷宫纪的书分批发布的清单。一回至多 255 个文件、64MB，一版至多 511 个文件（连页面）。
#   python publish_plan.py            打印三批的件数和大小，写 publish_A.json、publish_B.json、publish_C.json（files 用的列表，路径照仓库里这一本的目录）
# A 是页面以外的数据、壁画、人像拼图、灾祸的图（头一回发，跟页面一起）；B、C 是档案页的立绘加表情（assets/ps，不进库），照大小均分。
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def rel(ps):
    return [os.path.relpath(p, HERE).replace(os.sep, '/') for p in ps]


def main():
    os.chdir(HERE)
    A = rel(sorted(glob.glob('data/*.json')) + sorted(glob.glob('data/prof/*.json')) + sorted(glob.glob('assets/mural/*.webp'))
            + sorted(glob.glob('assets/pa/*.webp')) + sorted(glob.glob('assets/boss/*.webp')))
    ps = rel(sorted(glob.glob('assets/ps/*.webp')))
    B, C, sb, sc = [], [], 0, 0
    for p in sorted(ps, key=lambda x: -os.path.getsize(x)):
        if sb <= sc:
            B.append(p)
            sb += os.path.getsize(p)
        else:
            C.append(p)
            sc += os.path.getsize(p)
    for n, L in (('A', A), ('B', sorted(B)), ('C', sorted(C))):
        mb = sum(os.path.getsize(x) for x in L) / 2 ** 20
        print(n, len(L), '个', round(mb, 1), 'MB')
        json.dump([{'path': x} for x in L], open('publish_%s.json' % n, 'w', encoding='utf-8'), ensure_ascii=False)
    print('合计', len(A) + len(B) + len(C) + 1, '个（连页面）')


if __name__ == '__main__':
    main()
