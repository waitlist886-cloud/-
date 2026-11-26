#!/usr/bin/env python3
# 月银纪的书用的图：二十七幅壁画缩成 webp，量出每幅四边那一圈空墙的颜色（页面拿它铺墙、接缝）；时代页里的人用艺术照缩一张小的。
# 要带 PIL 的 Python（ComfyUI 那一个）。先跑 build_data.py（人的名单从 data/moon.json 里读）。
#   python prep_assets.py            壁画和人都做
#   python prep_assets.py tiles      只做壁画
#   python prep_assets.py por        只做人像拼图（一个时代一张）
#   python prep_assets.py spr        只做档案页的立绘加表情（一人一张）
#   python prep_assets.py cg         只做时代原画和节点原画（照 cg_table.json），写 data/cg.json
import io
import json
import os
import sys

from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
COMFY = os.path.normpath(os.path.join(HERE, '..', '..', '状态栏', 'comfy'))
SRC = os.path.join(COMFY, 'out', '门面_壁画_11-12')
ASSETS = os.path.join(HERE, 'assets')
TW, TH = 896, 1344
PSET_DIR = {'1001': '立绘_v3'}


def ground(im):
    """四边那一圈（各 3%）的平均色，去掉最亮最暗的两头，免得叫画的边角带偏。"""
    w, h = im.size
    b = max(4, int(w * 0.03))
    px = []
    small = im.resize((w // 4, h // 4), Image.BILINEAR)
    sw, sh = small.size
    sb = max(1, b // 4)
    data = small.load()
    for y in range(sh):
        for x in range(sw):
            if x < sb or x >= sw - sb or y < sb or y >= sh - sb:
                px.append(data[x, y])
    px.sort(key=lambda c: c[0] + c[1] + c[2])
    px = px[len(px) // 5: len(px) * 4 // 5]
    n = len(px)
    return [round(sum(c[i] for c in px) / n) for i in range(3)]


def tiles():
    os.makedirs(ASSETS, exist_ok=True)
    out = {}
    for i in range(1, 28):
        k = 'm%02d' % i
        p = os.path.join(SRC, k + '.png')
        if not os.path.exists(p):
            print('还没有', k)
            continue
        im = Image.open(p).convert('RGB')
        if im.size != (1024, 1536):
            print('尺寸不对', k, im.size)
        im2 = im.resize((TW, TH), Image.LANCZOS)
        dst = os.path.join(ASSETS, k + '.webp')
        im2.save(dst, 'WEBP', quality=84, method=6)
        out[k] = {'g': ground(im)}
        print(k, os.path.getsize(dst) // 1024, 'KB', '墙色', out[k]['g'])
    open(os.path.join(HERE, 'data', 'tiles.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(out, separators=(',', ':')) + '\n')
    print('写了 data/tiles.json，', len(out), '幅')


PW, PH, PCOLS = 300, 450, 8


def por():
    """时代页里的人像：一个时代一张拼图 assets/pa/时代.webp（旅伴、相遇、传奇，一格 300×450，一行八格），哪一格是谁写进 data/pa.json。
    这张私有网页一版至多五百来个文件，一人一张小图装不下，所以并图。"""
    d = json.load(open(os.path.join(HERE, 'data', 'moon.json'), encoding='utf-8'))
    dst_dir = os.path.join(ASSETS, 'pa')
    os.makedirs(dst_dir, exist_ok=True)
    out, total, miss = {}, 0, 0
    for e in d['eras']:
        keys, srcs = [], []
        for c in e['cast'] + e.get('meet', []) + e.get('legends', []):
            if not c.get('key') or c['key'] in keys:
                continue
            src = os.path.join(COMFY, 'out', PSET_DIR.get(c['pset'], '立绘_' + c['pset']), 'art', 'art_' + c['key'] + '.webp')
            if not os.path.exists(src):
                print('没有艺术照', e['id'], c['name'], src)
                miss += 1
                continue
            keys.append(c['key'])
            srcs.append(src)
        if not keys:
            continue
        cols = min(PCOLS, len(keys))
        rows = (len(keys) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * PW, rows * PH), (18, 19, 26))
        for i, src in enumerate(srcs):
            sheet.paste(Image.open(src).convert('RGB').resize((PW, PH), Image.LANCZOS), (i % cols * PW, i // cols * PH))
        dst = os.path.join(dst_dir, e['id'] + '.webp')
        sheet.save(dst, 'WEBP', quality=82, method=6)
        out[e['id']] = {'c': cols, 'r': rows, 'k': keys}
        total += os.path.getsize(dst)
    open(os.path.join(HERE, 'data', 'pa.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(out, separators=(',', ':')) + '\n')
    print('人像拼图：', len(out), '张，', total // 1024, 'KB；缺', miss, '，写了 data/pa.json')


def cg():
    """时代原画和节点原画（comfy/gpt_cg.py 出的）。哪一幅配哪一条主线的哪一幕、叫什么，照手写的 cg_table.json；图还没出的那一行跳过。"""
    table = json.load(open(os.path.join(HERE, 'cg_table.json'), encoding='utf-8'))
    src_dir = os.path.join(COMFY, 'out', '门面_原画_11-12')
    dst_dir = os.path.join(ASSETS, 'cg')
    os.makedirs(dst_dir, exist_ok=True)
    out, total = {}, 0
    for stem, t in table.items():
        base = t.get('src', stem)              # src：档案里挂的就是某一幅节点原画（奥瑞克的火盂），不另出图
        src = os.path.join(src_dir, base + '.png')
        if not os.path.exists(src):
            print('还没有', stem)
            continue
        rev = table.get(base, t).get('rev')
        name = base + ('_r%d' % rev if rev else '')      # 重画过的换一个文件名发，免得浏览器还拿着旧图
        dst = os.path.join(dst_dir, name + '.webp')
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
            im = Image.open(src).convert('RGB')
            if im.width > 1536:
                im = im.resize((1536, round(im.height * 1536 / im.width)), Image.LANCZOS)
            im.save(dst, 'WEBP', quality=86, method=6)
        total += os.path.getsize(dst)
        era = out.setdefault(stem.split('_')[0], {'nodes': {}})
        rel = 'assets/cg/%s.webp' % name
        if t.get('key'):
            era['key'] = {'src': rel}
        elif t.get('death'):          # 旅伴死的那一刻，挂在这个人的档案上
            era.setdefault('deaths', {})[t['death']] = {'src': rel, 'name': t.get('name', '')}
        else:
            slot, item = era['nodes'].setdefault(t['line'], {}), {'src': rel, 'name': t.get('name', '')}
            if t['act'] in slot:          # 一幕配了两幅的（第七歌二幕：那一声、白线之晨），存成一串，页面照先后排
                prev = slot[t['act']]
                slot[t['act']] = (prev if isinstance(prev, list) else [prev]) + [item]
            else:
                slot[t['act']] = item
        print(name, os.path.getsize(dst) // 1024, 'KB')
    open(os.path.join(HERE, 'data', 'cg.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n')
    print('写了 data/cg.json，', sum(1 + sum(len(v) for v in e['nodes'].values()) for e in out.values() if e.get('key')), '幅，', total // 1024, 'KB')


def spr():
    """档案页用的图，一人一张 assets/ps/键.webp（2560×1216）：上面一行是四套衣服（烘好的 por_键.webp，2560×960），
    下面一行是九格表情（烘好的 face_键.webp 是 3×3，这里排成一行，一格 256）。备了哪些人写进 data/have.json。"""
    d = json.load(open(os.path.join(HERE, 'data', 'moon.json'), encoding='utf-8'))
    dst_dir = os.path.join(ASSETS, 'ps')
    os.makedirs(dst_dir, exist_ok=True)
    have, total = [], 0
    for e in d['eras']:
        for c in e['cast'] + e.get('meet', []) + e.get('legends', []):          # 11-25 传奇也有档案了
            k = c.get('key')
            if not k or k in have:
                continue
            art = os.path.join(COMFY, 'out', PSET_DIR.get(c['pset'], '立绘_' + c['pset']), 'art')
            a, b = os.path.join(art, 'por_' + k + '.webp'), os.path.join(art, 'face_' + k + '.webp')
            if not os.path.exists(a) or not os.path.exists(b):
                print('没有', e['id'], c['name'], a if not os.path.exists(a) else b)
                continue
            dst = os.path.join(dst_dir, k + '.webp')
            if not os.path.exists(dst) or os.path.getmtime(dst) < max(os.path.getmtime(a), os.path.getmtime(b)):
                row = Image.open(a).convert('RGBA')
                face = Image.open(b).convert('RGBA')
                if row.size != (2560, 960) or face.size != (768, 768):
                    print('尺寸不对', k, row.size, face.size)
                    continue
                sheet = Image.new('RGBA', (2560, 1216), (0, 0, 0, 0))
                sheet.paste(row, (0, 0))
                for i in range(9):
                    sheet.paste(face.crop((i % 3 * 256, i // 3 * 256, i % 3 * 256 + 256, i // 3 * 256 + 256)), (i * 256, 960))
                sheet.save(dst, 'WEBP', quality=88, method=6)
            have.append(k)
            total += os.path.getsize(dst)
    open(os.path.join(HERE, 'data', 'have.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps({'ps': sorted(have)}, separators=(',', ':')) + '\n')
    print('立绘加表情', len(have), '张，', total // 1024, 'KB，写了 data/have.json')


if __name__ == '__main__':
    what = sys.argv[1:] or ['tiles', 'por', 'cg', 'spr']
    if 'spr' in what:
        spr()
    if 'tiles' in what:
        tiles()
    if 'por' in what:
        por()
    if 'cg' in what:
        cg()
