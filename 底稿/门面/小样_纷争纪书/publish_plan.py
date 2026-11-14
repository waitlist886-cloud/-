#!/usr/bin/env python3
# 纷争纪的书分批发布的清单。私有网页一回至多 255 个文件、64MB，一版至多 511 个文件（连页面 512 项）。
#   python -I -X utf8 publish_plan.py            报各批的文件数和大小
#   python -I -X utf8 publish_plan.py A          打出这一批的文件清单（给发布工具的 files，一行一个 JSON 数组）
# 批次：A 页面要的数据和小图（data/、牌面、长卷、人像拼图、神与魔神的显像），B 档案页的立绘加表情（assets/ps/），C、D 原画（assets/cg/，过了 60MB 就分两批）。
# 头一回发 A（连页面，建出地址），再发 B、C、D，都带同一个 index.html。
import glob
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
LIMIT_N, LIMIT_MB = 250, 60


def files(pat):
    return sorted(os.path.relpath(p, HERE).replace('\\', '/') for p in glob.glob(os.path.join(HERE, pat), recursive=True) if os.path.isfile(p))


def size(fs):
    return sum(os.path.getsize(os.path.join(HERE, f)) for f in fs)


def batches():
    a = files('data/*.json') + files('data/prof/*.json') + files('assets/card/*.webp') + files('assets/road/*.webp') + files('assets/pa/*.webp') + files('assets/god/*.webp')
    b = files('assets/ps/*.webp')
    cg = files('assets/cg/*.webp')
    out = {'A': a}
    k = 0
    for name, fs in (('B', b), ('C', cg)):          # 过了上限的按大小切开，批名接着往后排
        cur, cs = [], 0
        for f in fs:
            s = os.path.getsize(os.path.join(HERE, f))
            if cur and (len(cur) >= LIMIT_N or cs + s > LIMIT_MB * 1024 * 1024):
                out['BCDEFGH'[k]] = cur
                k += 1
                cur, cs = [], 0
            cur.append(f)
            cs += s
        if cur:
            out['BCDEFGH'[k]] = cur
            k += 1
    return out


if __name__ == '__main__':
    bs = batches()
    if len(sys.argv) > 1:
        print(json.dumps([{'path': f} for f in bs[sys.argv[1]]], ensure_ascii=False))
        sys.exit(0)
    tot = 0
    for k, fs in bs.items():
        tot += len(fs)
        print(k, len(fs), '个文件', round(size(fs) / 1048576, 1), 'MB', '｜', fs[0], '…', fs[-1])
    print('合计', tot, '个文件（连页面', tot + 1, '项，上限 512）', round(sum(size(f) for f in bs.values()) / 1048576, 1), 'MB')
