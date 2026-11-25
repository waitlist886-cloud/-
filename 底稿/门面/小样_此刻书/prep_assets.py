#!/usr/bin/env python3
# 此刻那一本用的图（11-24）。要 PIL。先跑 build_data.py（人像拼图的名单读 data/pa_keys.json）。
#   python prep_assets.py            都做
#   python prep_assets.py art        首屏、牌面、路上的画、大陆全图、票根、街灯（原图在 底稿/状态栏/comfy/out/门面_此刻/，样张那四张在 out/门面第二轮/此刻/）
#   python prep_assets.py por        图鉴的人像拼图（assets/pa/c、m、l.webp，一格 300×450，八列），档案的大像（assets/art/键.webp，600×900）
#   python prep_assets.py cg         主线各幕的节点原画（11-25）：原图在 底稿/状态栏/comfy/out/门面_原画_此刻/（comfy/gpt_cg_now.py 出），场面稿 scenes/now_*.json，
#                                    只收 scenes/review.json 里审过写了 ok 的；烘成 assets/cg/<键>[_r版次].webp（1536 宽），每条主线头一轮那一幅另出一张小的
#                                    assets/cg/t_<键>….webp（480 宽，路上那一站右边用），写 data/cg.json（{线的 id: {th, acts: {第几幕(从 0 数): {src, name[, sp]}}}}）。
#                                    这一支不用先跑 build_data.py；默认都做的时候不带它，要单叫。
import glob
import io
import json
import os
import sys

from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
SRC = os.path.join(COMFY, 'out', '门面_此刻')
SAMPLE = os.path.join(ROOT, 'out', '门面第二轮', '此刻')
V3 = os.path.join(COMFY, 'out', '立绘_v3', 'art')
A = os.path.join(HERE, 'assets')


def fresh(dst, *srcs):
    return os.path.exists(dst) and all(os.path.getmtime(dst) >= os.path.getmtime(s) for s in srcs)


def save(im, dst, q=82):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, 'WEBP', quality=q, method=6)
    print('  ', os.path.relpath(dst, HERE), im.size, os.path.getsize(dst) // 1024, 'KB')


def art():
    jobs = [('card', SAMPLE, 'card', (800, 1200), 86), ('main', SAMPLE, 'main', (2048, 1365), 80), ('main_m', SAMPLE, 'main', (1100, 733), 80),
            ('r1', SAMPLE, 'r1', (1400, 933), 80), ('r2', SAMPLE, 'r2', (1400, 933), 80)]
    jobs += [(k, SRC, k, (1400, 933), 80) for k in ('r3', 'r4', 'r5', 'r6')]
    jobs += [('lamp', SRC, 'lamp', (360, 540), 84)]
    for name, d, k, size, q in jobs:
        src = os.path.join(d, k + '.png')
        dst = os.path.join(A, name + '.webp')
        if not os.path.exists(src):
            print('没有', src)
            continue
        if fresh(dst, src):
            continue
        save(Image.open(src).convert('RGB').resize(size, Image.LANCZOS), dst, q)
    # 票根：裁到票面，四角的深蓝底抠成透明（票面自己是象牙白，跟底色差得远）
    src = os.path.join(SRC, 'ticket.png')
    dst = os.path.join(A, 'ticket.webp')
    if os.path.exists(src) and not fresh(dst, src):
        import numpy as np
        im = Image.open(src).convert('RGB')
        a = np.asarray(im).astype(int)
        d = np.abs(a - np.array(im.getpixel((5, 5)))).sum(2)
        ys, xs = np.where(d > 60)
        alpha = np.clip((d - 40) * 255 // 70, 0, 255).astype('uint8')
        rgba = Image.fromarray(np.dstack([a.astype('uint8'), alpha]), 'RGBA').crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        save(rgba.resize((960, round(960 * rgba.height / rgba.width)), Image.LANCZOS), dst, 86)
    # 大陆全图：出图时上下各补了一条海凑成 3:2，这里照同样的比例裁回旧底图的框（3520×2240 → 2200×1400），地标的百分数照旧
    src = os.path.join(SRC, 'map.png')
    dst = os.path.join(A, 'map.webp')
    if os.path.exists(src) and not fresh(dst, src):
        im = Image.open(src).convert('RGB')
        w, h = im.size
        keep = h * (2240 / (3520 * 2 / 3))
        top = (h - keep) / 2
        im = im.crop((0, round(top), w, round(top + keep))).resize((2200, 1400), Image.LANCZOS)
        save(im, dst, 82)
        save(im.resize((1100, 700), Image.LANCZOS), os.path.join(A, 'map_s.webp'), 80)


PW, PH, PCOLS = 300, 450, 8


def por():
    keys = json.load(open(os.path.join(HERE, 'data', 'pa_keys.json'), encoding='utf-8'))['pa']
    allk = []
    for sk, ks in keys.items():
        cols = min(PCOLS, len(ks))
        rows = (len(ks) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * PW, rows * PH), (12, 18, 40))
        for i, k in enumerate(ks):
            src = os.path.join(V3, 'art_' + k + '.webp')
            sheet.paste(Image.open(src).convert('RGB').resize((PW, PH), Image.LANCZOS), (i % cols * PW, i // cols * PH))
            allk.append(k)
        save(sheet, os.path.join(A, 'pa', sk + '.webp'), 80)
    for k in allk + ['baltina']:
        src = os.path.join(V3, 'art_' + k + '.webp')
        dst = os.path.join(A, 'art', k + '.webp')
        if not fresh(dst, src):
            Image.open(src).convert('RGB').resize((600, 900), Image.LANCZOS).save(dst, 'WEBP', quality=82, method=6) if os.makedirs(os.path.dirname(dst), exist_ok=True) is None else None
    print('档案大像', len(set(allk + ['baltina'])), '张')


CG_SRC = os.path.join(COMFY, 'out', '门面_原画_此刻')
ACT_NO = {'一幕': 0, '二幕': 1, '三幕': 2, '四幕': 3, '五幕': 4}


def cg():
    """主线各幕的节点原画。review.json：{键: 'ok' | 'redo' | 'hold' | 'blank'}，只有 ok 的进书（没审过的不进）。
    rev.json 是重画的版次（gpt_cg_now.py --redo 记的），版次进文件名，换了图浏览器不会拿旧的。"""
    sc = os.path.join(HERE, 'scenes')
    nodes = []
    for f in sorted(glob.glob(os.path.join(sc, 'now_*.json'))):
        nodes += json.load(open(f, encoding='utf-8'))['nodes']
    rj = os.path.join(sc, 'review.json')
    review = json.load(open(rj, encoding='utf-8')) if os.path.exists(rj) else {}
    vj = os.path.join(sc, 'rev.json')
    rev = json.load(open(vj, encoding='utf-8')) if os.path.exists(vj) else {}
    road = json.load(open(os.path.join(HERE, 'src', 'road_text.json'), encoding='utf-8'))
    line_id = {L['title']: 'L%d' % L['src'] for L in road['lines']}
    nacts = {L['title']: len(L['acts']) for L in road['lines']}
    dst_dir = os.path.join(A, 'cg')
    os.makedirs(dst_dir, exist_ok=True)
    out, keep, n, total, wait, lack = {}, set(), 0, 0, [], []
    for s in sorted(nodes, key=lambda x: (x.get('round', 2), x['key'])):
        k = s['key']
        assert s['line'] in line_id, '主线名对不上 road_text.json：' + s['line']
        ai = ACT_NO[s['act']]
        assert ai < nacts[s['line']], '这一条没有这一幕：' + k
        src = os.path.join(CG_SRC, k + '.png')
        if not os.path.exists(src):
            lack.append(k)
            continue
        if review.get(k) != 'ok':
            wait.append(k)
            continue
        name = k + ('_r%d' % rev[k] if rev.get(k) else '')
        dst = os.path.join(dst_dir, name + '.webp')
        if not fresh(dst, src):
            im = Image.open(src).convert('RGB')
            if im.width > 1536:
                im = im.resize((1536, round(im.height * 1536 / im.width)), Image.LANCZOS)
            im.save(dst, 'WEBP', quality=86, method=6)
        keep.add(name + '.webp')
        total += os.path.getsize(dst)
        n += 1
        e = out.setdefault(line_id[s['line']], {'acts': {}})
        item = {'src': 'assets/cg/%s.webp' % name, 'name': s.get('name', '')}
        if s.get('spoil'):
            item['sp'] = 1
        e['acts'][str(ai)] = item
        # 路上那一站右边的小幅：这一条里头一幅审过的（头一轮的排在前头），归剧透的不拿来当
        if 'th' not in e and not s.get('spoil'):
            tdst = os.path.join(dst_dir, 't_' + name + '.webp')
            if not fresh(tdst, src):
                Image.open(src).convert('RGB').resize((480, 320), Image.LANCZOS).save(tdst, 'WEBP', quality=80, method=6)
            keep.add('t_' + name + '.webp')
            total += os.path.getsize(tdst)
            e['th'] = 'assets/cg/t_%s.webp' % name
    for f in os.listdir(dst_dir):          # 换了版次、撤下来的旧图清掉
        if f.endswith('.webp') and f not in keep:
            os.remove(os.path.join(dst_dir, f))
    open(os.path.join(HERE, 'data', 'cg.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, separators=(',', ':'), sort_keys=True) + '\n')
    print('写了 data/cg.json：', n, '幅，', len(out), '条主线有图，', total // 1024, 'KB；出了图还没审过（或没过）的', len(wait), '幅', ' '.join(wait[:16]),
          '；场面稿有、图还没出的', len(lack), '幅')


if __name__ == '__main__':
    what = sys.argv[1:] or ['art', 'por']
    if 'art' in what:
        art()
    if 'por' in what:
        por()
    if 'cg' in what:
        cg()
