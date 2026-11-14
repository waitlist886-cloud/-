#!/usr/bin/env python3
# 山铜纪的书分批发布的清单（照纷争纪那一本的 publish_plan.py）。私有网页一回至多 255 个文件、64MB，一版至多 511 个文件（连页面 512 项）。
#   python -I -X utf8 publish_plan.py            报各批的文件数和大小
#   python -I -X utf8 publish_plan.py A          打出这一批的文件清单（给发布工具的 files，一行一个 JSON 数组）
# 批次：A 页面要的数据和小图（data/、碑、远景、立牌、人像拼图、神与对手），B 档案页的立绘加表情（assets/ps/），C 往后是原画（assets/cg/，过了上限就切开）。
# 头一回发 A（连页面，建出地址），再发 B、C……，都带同一个 index.html。
# 碑的空样板（t_bronze 这些）只有哪一块碑还没出图的时候才用得上：三十六块都有图了就不发，界碑背面那一张黑曜石（t_obsidian）照发。
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


def unused_steles():
    """页面上碑的图照 index.html 的 imgOf 认：有它自己那一张用那一张，没有拿它那一种空样板顶着；界碑的背面是 t_obsidian。认不到的那几张不发。"""
    d = json.load(open(os.path.join(HERE, 'data', 'bronze.json'), encoding='utf-8'))
    sj = json.load(open(os.path.join(HERE, 'data', 'stele.json'), encoding='utf-8'))
    box, tpl, used = sj['box'], sj['tpl'], set()
    for s in [x for e in d['eras'] for x in e['steles']] + [d['end']]:
        f = s['art'] if s.get('art') in box else tpl.get(s['name'], '')
        used.add(f)
        used.add(('t_obsidian' if 't_obsidian' in box else '') if s.get('kind') == 'boundary' else f)
    # 11-14 碑形以后碑图换成 m01..m43，旧的 b01..b36 留在 assets/stele/ 里没删，不在 box 里的也一并不发
    have = {os.path.splitext(os.path.basename(f))[0] for f in files('assets/stele/*.webp')}
    return {'assets/stele/%s.webp' % k for k in (set(box) | have) if k not in used}


def batches():
    a = files('data/*.json') + files('data/prof/*.json')
    skip = unused_steles()
    for d in sorted(os.listdir(os.path.join(HERE, 'assets'))):
        if d not in ('ps', 'cg') and os.path.isdir(os.path.join(HERE, 'assets', d)):
            a += [f for f in files('assets/%s/*.*' % d) if f not in skip]
    out, k = {}, 0
    for fs in (a, files('assets/ps/*.webp'), files('assets/cg/*.webp')):     # 过了上限的按大小切开，批名接着往后排
        cur, cs = [], 0
        for f in fs:
            s = os.path.getsize(os.path.join(HERE, f))
            if cur and (len(cur) >= LIMIT_N or cs + s > LIMIT_MB * 1024 * 1024):
                out['ABCDEFGH'[k]] = cur
                k += 1
                cur, cs = [], 0
            cur.append(f)
            cs += s
        if cur:
            out['ABCDEFGH'[k]] = cur
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
