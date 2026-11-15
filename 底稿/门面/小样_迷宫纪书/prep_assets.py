#!/usr/bin/env python3
# 迷宫纪的书用的图。要带 PIL 的 Python（ComfyUI 那一个）。先跑 build_data.py（人的名单从 data/maze.json 里读）。
#   python prep_assets.py            都做
#   python prep_assets.py mural      壁画（assets/mural/键.webp），名字、出自哪一条照 scenes/qN.json，写 data/mural.json；没出图的跳过
#   python prep_assets.py por        时代页里的人像拼图，一页一张（assets/pa/），写 data/pa.json
#   python prep_assets.py spr        档案页的立绘加表情，一人一张（assets/ps/，不进库），写 data/have.json
#   python prep_assets.py boss       灾祸那一栏史诗战的图，一个对手一张拼图（assets/boss/），写 data/have.json 的 boss
# 壁画是 comfy/gpt_cg4.py 出的，在 comfy/out/门面_原画_迷宫纪/（不进库）。人像、对手的做法照山铜纪那一本（小样_山铜纪书/prep_assets.py）。
import glob
import io
import json
import os
import sys

from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
COMFY = os.path.normpath(os.path.join(HERE, '..', '..', '状态栏', 'comfy'))
SRC = os.path.join(COMFY, 'out', '门面_原画_迷宫纪')
ASSETS = os.path.join(HERE, 'assets')
PSET_DIR = {'1001': '立绘_v3'}
GODS = os.path.join(COMFY, 'out', '神明显像')
EPIC = os.path.join(COMFY, 'out', '史诗战', 'maze')


def data():
    return json.load(open(os.path.join(HERE, 'data', 'maze.json'), encoding='utf-8'))


def fresh(dst, *srcs):
    return os.path.exists(dst) and all(os.path.getmtime(dst) >= os.path.getmtime(s) for s in srcs)


def save_json(name, obj):
    open(os.path.join(HERE, 'data', name), 'w', encoding='utf-8', newline='\n').write(json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n')


def have_update(**kw):
    hp = os.path.join(HERE, 'data', 'have.json')
    old = json.load(open(hp, encoding='utf-8')) if os.path.exists(hp) else {}
    old.update(kw)
    save_json('have.json', old)


# ---- 壁画 ----
MW = 1280          # 壁画存多宽（贴在井壁上和点开看大图都用这一张）


def mural():
    names = {}
    for p in sorted(glob.glob(os.path.join(HERE, 'scenes', 'q?.json'))):
        for m in json.load(open(p, encoding='utf-8-sig')).get('murals', []):
            names[m['key']] = {'name': m.get('name', ''), 'line': m.get('line', ''), 'task': m.get('task', '')}
    dst_dir = os.path.join(ASSETS, 'mural')
    os.makedirs(dst_dir, exist_ok=True)
    out, total, lack = {}, 0, []
    for key, info in sorted(names.items()):
        src = os.path.join(SRC, key + '.png')
        if not os.path.exists(src):
            lack.append(key)
            continue
        dst = os.path.join(dst_dir, key + '.webp')
        if not fresh(dst, src):
            im = Image.open(src).convert('RGB')
            if im.width > MW:
                im = im.resize((MW, round(im.height * MW / im.width)), Image.LANCZOS)
            im.save(dst, 'WEBP', quality=82, method=6)
        out[key] = dict(info, v=int(os.path.getmtime(dst)))
        total += os.path.getsize(dst)
    save_json('mural.json', out)
    print('壁画', len(out), '幅，', total // 1024, 'KB；还没出图的', len(lack), '幅', ' '.join(lack[:16]) + (' …' if len(lack) > 16 else ''))


# ---- 人像（照山铜纪那一本）----
PW, PH, PCOLS = 300, 450, 8


def art_of(c):
    if c.get('pset') == '神明显像':
        return os.path.join(GODS, c['key'] + '.png')
    return os.path.join(COMFY, 'out', PSET_DIR.get(c['pset'], '立绘_' + c['pset']), 'art', 'art_' + c['key'] + '.webp')


def people(e):
    return e['cast'] + e.get('meet', []) + e.get('legends', []) + e.get('gods', [])


def por():
    dst_dir = os.path.join(ASSETS, 'pa')
    os.makedirs(dst_dir, exist_ok=True)
    out, total, miss = {}, 0, 0
    for e in data()['eras']:
        keys, srcs = [], []
        for c in people(e):
            if not c.get('key') or c['key'] in keys:
                continue
            src = art_of(c)
            if not os.path.exists(src):
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
        sheet.save(dst, 'WEBP', quality=80, method=6)
        out[e['id']] = {'c': cols, 'r': rows, 'k': keys}
        total += os.path.getsize(dst)
    save_json('pa.json', out)
    print('人像拼图：', len(out), '张，', total // 1024, 'KB；缺', miss, '，写了 data/pa.json')


def spr():
    dst_dir = os.path.join(ASSETS, 'ps')
    os.makedirs(dst_dir, exist_ok=True)
    have, total, miss = [], 0, 0
    for e in data()['eras']:
        for c in e['cast'] + e.get('meet', []) + e.get('legends', []):
            k = c.get('key')
            if not k or k in have or c.get('pset') == '神明显像':
                continue
            art = os.path.join(COMFY, 'out', PSET_DIR.get(c['pset'], '立绘_' + c['pset']), 'art')
            a, b = os.path.join(art, 'por_' + k + '.webp'), os.path.join(art, 'face_' + k + '.webp')
            if not os.path.exists(a) or not os.path.exists(b):
                miss += 1
                continue
            dst = os.path.join(dst_dir, k + '.webp')
            if not fresh(dst, a, b):
                row = Image.open(a).convert('RGBA')
                face = Image.open(b).convert('RGBA')
                if row.size != (2560, 960) or face.size != (768, 768):
                    print('尺寸不对', k, row.size, face.size)
                    continue
                sheet = Image.new('RGBA', (2560, 1216), (0, 0, 0, 0))
                sheet.paste(row, (0, 0))
                for i in range(9):
                    sheet.paste(face.crop((i % 3 * 256, i // 3 * 256, i % 3 * 256 + 256, i // 3 * 256 + 256)), (i * 256, 960))
                sheet.save(dst, 'WEBP', quality=86, method=6)
            have.append(k)
            total += os.path.getsize(dst)
    have_update(ps=sorted(have))
    print('立绘加表情', len(have), '张，', total // 1024, 'KB；没有的', miss, '，写了 data/have.json')


BW, BH = 480, 720


def boss():
    dst_dir = os.path.join(ASSETS, 'boss')
    os.makedirs(dst_dir, exist_ok=True)
    out, total = {}, 0
    for e in data()['eras']:
        for b in e.get('bosses', []):
            ks = b.get('imgs', [])
            if not ks or ks[0] in out:
                continue
            got = [(j, os.path.join(EPIC, k + '.png')) for j, k in enumerate(ks) if os.path.exists(os.path.join(EPIC, k + '.png'))]
            if not got:
                continue
            dst = os.path.join(dst_dir, ks[0] + '.webp')
            newest = max(os.path.getmtime(p) for _, p in got)
            ok = os.path.exists(dst) and os.path.getmtime(dst) >= newest
            if ok:
                with Image.open(dst) as old_im:
                    ok = old_im.size == (BW * len(got), BH)
            if not ok:
                strip = Image.new('RGB', (BW * len(got), BH))
                for i, (_, p) in enumerate(got):
                    strip.paste(Image.open(p).convert('RGB').resize((BW, BH), Image.LANCZOS), (BW * i, 0))
                strip.save(dst, 'WEBP', quality=78, method=6)
            out[ks[0]] = {'n': len(got), 'p': [j for j, _ in got], 'v': int(os.path.getmtime(dst))}
            total += os.path.getsize(dst)
    have_update(boss=out)
    print('灾祸的拼图', len(out), '张（合计', sum(v['n'] for v in out.values()), '格），', total // 1024, 'KB')


if __name__ == '__main__':
    what = sys.argv[1:] or ['mural', 'por', 'spr', 'boss']
    for name, fn in (('mural', mural), ('por', por), ('spr', spr), ('boss', boss)):
        if name in what:
            fn()
