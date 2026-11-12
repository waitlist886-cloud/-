#!/usr/bin/env python3
# 月银纪的书用的图：二十七幅壁画缩成 webp，量出每幅四边那一圈空墙的颜色（页面拿它铺墙、接缝）；时代页里的人用艺术照缩一张小的。
# 要带 PIL 的 Python（ComfyUI 那一个）。先跑 build_data.py（人的名单从 data/moon.json 里读）。
#   python prep_assets.py            壁画和人都做
#   python prep_assets.py tiles      只做壁画
#   python prep_assets.py por        只做人
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


def por():
    d = json.load(open(os.path.join(HERE, 'data', 'moon.json'), encoding='utf-8'))
    dst_dir = os.path.join(ASSETS, 'por')
    os.makedirs(dst_dir, exist_ok=True)
    n = miss = total = 0
    for e in d['eras']:
        for c in e['cast'] + e.get('meet', []) + e.get('legends', []):
            if not c['key']:
                continue
            src = os.path.join(COMFY, 'out', PSET_DIR.get(c['pset'], '立绘_' + c['pset']), 'art', 'art_' + c['key'] + '.webp')
            dst = os.path.join(dst_dir, c['key'] + '.webp')
            if not os.path.exists(src):
                print('没有艺术照', e['id'], c['name'], src)
                miss += 1
                continue
            if not os.path.exists(dst):
                im = Image.open(src).convert('RGB').resize((360, 540), Image.LANCZOS)
                im.save(dst, 'WEBP', quality=80, method=6)
            total += os.path.getsize(dst)
            n += 1
    print('人：', n, '张，', total // 1024, 'KB；缺', miss)


def cg():
    """时代原画和节点原画（comfy/gpt_cg.py 出的）。哪一幅配哪一条主线的哪一幕、叫什么，照手写的 cg_table.json；图还没出的那一行跳过。"""
    table = json.load(open(os.path.join(HERE, 'cg_table.json'), encoding='utf-8'))
    src_dir = os.path.join(COMFY, 'out', '门面_原画_11-12')
    dst_dir = os.path.join(ASSETS, 'cg')
    os.makedirs(dst_dir, exist_ok=True)
    out, total = {}, 0
    for stem, t in table.items():
        src = os.path.join(src_dir, stem + '.png')
        if not os.path.exists(src):
            print('还没有', stem)
            continue
        name = stem + ('_r%d' % t['rev'] if t.get('rev') else '')      # 重画过的换一个文件名发，免得浏览器还拿着旧图
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


SPR_ERAS = ['m07']        # 档案页的立绘和表情先只备试样的那个时代（这张私有网页一版至多五百来个文件，全铺要另想办法）


def spr():
    """档案页用的立绘（四套衣服一行，2560×960）和表情（九格，768×768），照立绘烘好的 webp 原样拷。备了哪些人写进 data/have.json。"""
    import shutil
    d = json.load(open(os.path.join(HERE, 'data', 'moon.json'), encoding='utf-8'))
    for sub in ('spr', 'face'):
        os.makedirs(os.path.join(ASSETS, sub), exist_ok=True)
    for e in d['eras']:
        if e['id'] not in SPR_ERAS:
            continue
        for c in e['cast'] + e.get('meet', []):
            if not c.get('key'):
                continue
            art = os.path.join(COMFY, 'out', PSET_DIR.get(c['pset'], '立绘_' + c['pset']), 'art')
            for sub, pre in (('spr', 'por_'), ('face', 'face_')):
                src = os.path.join(art, pre + c['key'] + '.webp')
                dst = os.path.join(ASSETS, sub, c['key'] + '.webp')
                if not os.path.exists(src):
                    print('没有', e['id'], c['name'], src)
                elif not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
                    shutil.copyfile(src, dst)
    have = {sub: sorted(f[:-5] for f in os.listdir(os.path.join(ASSETS, sub)) if f.endswith('.webp')) for sub in ('spr', 'face')}
    open(os.path.join(HERE, 'data', 'have.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(have, separators=(',', ':')) + '\n')
    size = sum(os.path.getsize(os.path.join(ASSETS, sub, k + '.webp')) for sub in have for k in have[sub])
    print('立绘', len(have['spr']), '张，表情', len(have['face']), '张，', size // 1024, 'KB，写了 data/have.json')


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
