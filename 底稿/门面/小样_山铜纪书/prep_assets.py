#!/usr/bin/env python3
# 山铜纪的书用的图。要带 PIL 和 numpy 的 Python（ComfyUI 那一个）。先跑 build_data.py（人的名单从 data/bronze.json 里读）。
#   python prep_assets.py            都做
#   python prep_assets.py sky        路尽头的天和地平线，一页一张加最后一夜（h1..h7，assets/sky/），量地平线底下那一片雾的颜色写进 data/sky.json
#   python prep_assets.py walk       路当中往前走的两个人（巴尔缇娜 w_bal_*、索恩薇娅 w_sor_*，背影抠图，assets/walk/），量人在图里从哪儿到哪儿写进 data/walk.json
#   python prep_assets.py stele      碑三十六块加四张空碑样板（assets/stele/），量碑面的框写进 data/stele.json；没出图的跳过
#   python prep_assets.py por        时代页里的人像拼图，一页一张（assets/pa/），神和魔神用神明显像，写 data/pa.json
#   python prep_assets.py spr        档案页的立绘加表情，一人一张（assets/ps/，不进库），神和魔神的显像（assets/god/），写 data/have.json
#   python prep_assets.py boss       灾祸那一栏史诗战的图（assets/boss/），一阶一张
#   python prep_assets.py cg         时代原画（e1..e6）、节点原画、旅伴死的那一刻（照 cg_table.json），写 data/cg.json
# 图都是 comfy/gpt_cg3.py 出的，在 comfy/out/门面_原画_山铜纪/（不进库）。
import io
import json
import os
import sys

from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
COMFY = os.path.normpath(os.path.join(HERE, '..', '..', '状态栏', 'comfy'))
SRC = os.path.join(COMFY, 'out', '门面_原画_山铜纪')
ASSETS = os.path.join(HERE, 'assets')
PSET_DIR = {'1001': '立绘_v3'}
GODS = os.path.join(COMFY, 'out', '神明显像')
EPIC = os.path.join(COMFY, 'out', '史诗战', 'bronze')
TPL = {'bronze': 't_bronze', 'white': 't_white', 'obsidian': 't_obsidian', 'boundary': 't_border', 'stone': 't_white'}


def data():
    return json.load(open(os.path.join(HERE, 'data', 'bronze.json'), encoding='utf-8'))


def fresh(dst, *srcs):
    return os.path.exists(dst) and all(os.path.getmtime(dst) >= os.path.getmtime(s) for s in srcs)


def save_json(name, obj):
    open(os.path.join(HERE, 'data', name), 'w', encoding='utf-8', newline='\n').write(json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n')


# ---- 路尽头的天 ----
def avg(im, x0, x1, y0, y1):
    w, h = im.size
    box = im.crop((int(w * x0), int(h * y0), max(int(w * x0) + 1, int(w * x1)), max(int(h * y0) + 1, int(h * y1)))).resize((1, 1), Image.BOX)
    return list(box.getpixel((0, 0)))


def sky():
    """gpt_cg3.py 的 h1..h7：3:2 横幅，地平线在图高六成，地平线以下一片匀的薄雾。页面拿它铺天，地面远处的雾就取图里地平线底下那一片的颜色。"""
    dst_dir = os.path.join(ASSETS, 'sky')
    os.makedirs(dst_dir, exist_ok=True)
    out, tot = {}, 0
    for i in range(1, 8):
        k = 'h%d' % i
        p = os.path.join(SRC, k + '.png')
        if not os.path.exists(p):
            print('还没有', k)
            continue
        im = Image.open(p).convert('RGB')
        dst = os.path.join(dst_dir, k + '.webp')
        if not fresh(dst, p):
            im.resize((1536, 1024), Image.LANCZOS).save(dst, 'WEBP', quality=84, method=6)
        out[k] = {'horizon': 0.6, 'mist': avg(im, 0, 1, .62, .72), 'low': avg(im, 0, 1, .52, .59), 'top': avg(im, 0, 1, 0, .1), 'v': int(os.path.getmtime(p))}
        tot += os.path.getsize(dst)
    save_json('sky.json', out)
    print('天', len(out), '张，', tot // 1024, 'KB，写了 data/sky.json')


# ---- 路面、墙面、地面的底纹（11-14）----
TEXS = ['tx_road', 'tx_wall', 'tx_grass', 'tx_wheat']


def tex():
    """gpt_cg3.py 的 tx_*：方的、四边接得上的底纹。缩成 1024×1024（页面要两的幂才能做 mipmap 和 REPEAT），
    量平均亮度写进 data/tex.json（页面拿亮度除以它当明暗，颜色照各页那一套光去染；麦田那一张在麦的年月整张带颜色用）。"""
    import numpy as np
    dst_dir = os.path.join(ASSETS, 'tex')
    os.makedirs(dst_dir, exist_ok=True)
    out, tot = {}, 0
    for k in TEXS:
        p = os.path.join(SRC, k + '.png')
        if not os.path.exists(p):
            print('还没有', k)
            continue
        im = Image.open(p).convert('RGB').resize((1024, 1024), Image.LANCZOS)
        dst = os.path.join(dst_dir, k + '.webp')
        if not fresh(dst, p):
            im.save(dst, 'WEBP', quality=86, method=6)
        a = np.asarray(im, np.float32) / 255
        lum = float((a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114).mean())
        out[k] = {'v': int(os.path.getmtime(p)), 'lum': round(lum, 4)}
        tot += os.path.getsize(dst)
    save_json('tex.json', out)
    print('底纹', len(out), '张，', tot // 1024, 'KB，写了 data/tex.json')


# ---- 路边的景（11-14）----
# 脚底下画了一圈灰石子土的（麦丛），从上往下看像一盆花：图下面那一截里发灰的像素换成一团淡淡的影子。数是从图的哪一成往下算
BASE_SHADOW = {'pr6_tuft': 0.82}


def base_to_shadow(c, top):
    import numpy as np
    a = np.asarray(c).astype(np.float32)
    h = a.shape[0]
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    rows = np.arange(h, dtype=np.float32)[:, None] / h
    band = np.clip((rows - top) / 0.05, 0, 1)                    # 往下渐渐算进来，不切出一道横线
    grey = np.clip(1 - (r - b - 18) / 22, 0, 1)                  # 麦秆是黄的（红比蓝高得多），石子和土是灰的
    k = band * grey
    out = a.copy()
    shade = np.array([42, 30, 20], np.float32)
    for i in range(3):
        out[..., i] = a[..., i] * (1 - k) + shade[i] * k
    out[..., 3] = al * (1 - k) + al * 0.34 * k
    from PIL import ImageFilter
    im = Image.fromarray(out.clip(0, 255).astype('uint8'), 'RGBA')
    sh = Image.fromarray((k * 255).clip(0, 255).astype('uint8'), 'L').filter(ImageFilter.GaussianBlur(3))
    soft = im.filter(ImageFilter.GaussianBlur(2.5))
    return Image.composite(soft, im, sh)


def props():
    """gpt_cg3.py 的 pr*_（透明底，一样一张）。裁到有画的那一块（四周留一点），长边缩到 520，
    一个年代拼成一张大图（键的头三个字 pr1 到 pr6，assets/prop/at_pr1.webp …），一样之间隔 8 像素的透明；
    每一样在拼图里的位置、宽高比写进 data/props.json（props 一节），拼图的大小和版本写进 atlas 一节。
    页面照远近摆在路两边，脚落在地上。私有网页一版至多 511 个文件，所以不再一样一张。"""
    import glob
    dst_dir = os.path.join(ASSETS, 'prop')
    os.makedirs(dst_dir, exist_ok=True)
    items = {}
    for p in sorted(glob.glob(os.path.join(SRC, 'pr[0-9]*.png'))):
        k = os.path.basename(p)[:-4]
        if k.endswith(('_a0', '_a1', '_a2')):
            continue
        im = Image.open(p).convert('RGBA')
        bb = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
        if not bb:
            continue
        m = round(max(bb[2] - bb[0], bb[3] - bb[1]) * 0.015)
        bb = (max(0, bb[0] - m), max(0, bb[1] - m), min(im.width, bb[2] + m), min(im.height, bb[3] + 2))
        c = im.crop(bb)
        s = 520 / max(c.size)
        if s < 1:
            c = c.resize((round(c.width * s), round(c.height * s)), Image.LANCZOS)
        if k in BASE_SHADOW:
            c = base_to_shadow(c, BASE_SHADOW[k])
        items.setdefault(k[:3], []).append((k, c, os.path.getmtime(p)))
    out, atl, tot = {}, {}, 0
    PAD, WMAX = 8, 2048
    for a, lst in sorted(items.items()):
        lst.sort(key=lambda it: -it[1].height)
        x = y = rowh = 0
        place = []
        for k, c, mt in lst:                       # 一排一排往下摆
            if x + c.width > WMAX:
                x, y, rowh = 0, y + rowh + PAD, 0
            place.append((k, c, x, y))
            x += c.width + PAD
            rowh = max(rowh, c.height)
        W = max(px + c.width for k, c, px, py in place)
        H = max(py + c.height for k, c, px, py in place)
        sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for k, c, px, py in place:
            sheet.paste(c, (px, py))
            out[k] = {'a': a, 'x': px, 'y': py, 'w': c.width, 'h': c.height, 'ar': round(c.width / c.height, 4)}
        dst = os.path.join(dst_dir, 'at_%s.webp' % a)
        sheet.save(dst, 'WEBP', quality=86, method=6)
        v = int(max(mt for k, c, mt in lst)) + len(lst)
        atl[a] = {'W': W, 'H': H, 'v': v}
        tot += os.path.getsize(dst)
        print('拼图', a, len(lst), '样', W, 'x', H, os.path.getsize(dst) // 1024, 'KB')
    for f in glob.glob(os.path.join(dst_dir, 'pr*.webp')):          # 一样一张的旧图不再用
        os.remove(f)
    save_json('props.json', {'atlas': atl, 'props': out})
    print('路边的景', len(out), '样，拼成', len(atl), '张，', tot // 1024, 'KB，写了 data/props.json')


# ---- 路当中走的两个人 ----
WALKERS = ['w_bal_1', 'w_bal_2', 'w_bal_2b', 'w_bal_3', 'w_sor_1', 'w_sor_2', 'w_sor_3']


def walk():
    """背影抠图（透明底，1024×1536 上下）。存 assets/walk/键.webp（512×768），量人从头顶到脚底占图的哪一截、左右当中在哪儿，写 data/walk.json；页面照这个把人缩到该有的身高、脚落在路上。"""
    dst_dir = os.path.join(ASSETS, 'walk')
    os.makedirs(dst_dir, exist_ok=True)
    out, tot = {}, 0
    for k in WALKERS:
        p = os.path.join(SRC, k + '.png')
        if not os.path.exists(p):
            print('还没有', k)
            continue
        im = Image.open(p).convert('RGBA')
        W, H = im.size
        bb = im.split()[3].point(lambda v: 255 if v > 40 else 0).getbbox()
        if not bb:
            print('是空的', k)
            continue
        dst = os.path.join(dst_dir, k + '.webp')
        if not fresh(dst, p):
            im.resize((512, round(512 * H / W)), Image.LANCZOS).save(dst, 'WEBP', quality=88, method=6)
        out[k] = {'w': W, 'h': H, 'top': round(bb[1] / H, 4), 'foot': round(bb[3] / H, 4), 'cx': round((bb[0] + bb[2]) / 2 / W, 4), 'v': int(os.path.getmtime(p))}
        tot += os.path.getsize(dst)
    save_json('walk.json', out)
    print('人', len(out), '张，', tot // 1024, 'KB，写了 data/walk.json')


# ---- 碑 ----
def face_of(im):
    """量一块碑的碑面：从碑面当中往四边走，碰到边框（亮度起变化的地方）就停。回 (左, 顶, 右, 底, 尖顶) 的像素。
    gpt_cg3.py 的碑都照同一张样板画，大小和位置差不多，量出来的框只是让页面刻的字落在碑面里头。"""
    import numpy as np
    from PIL import ImageFilter
    a = np.asarray(im.convert('RGBA')).astype(np.float32)
    H, W = a.shape[:2]
    al = a[..., 3]
    lum = 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
    lum = np.asarray(Image.fromarray(lum.astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))).astype(np.float32)
    g = np.maximum(np.abs(np.diff(lum, axis=1, prepend=lum[:, :1])), np.abs(np.diff(lum, axis=0, prepend=lum[:1, :])))
    th = max(6.0, float(np.percentile(g[al > 200], 92)))
    solid = al > 200
    ys, xs = np.nonzero(solid)
    band = (ys > H * .35) & (ys < H * .55)
    cx, cy = int(np.median(xs[band])), int(H * .45)
    ls, rs = [], []
    for y in range(int(H * .38), int(H * .62), 6):
        x = cx
        while x > 0 and g[y, x] <= th and solid[y, x]:
            x -= 1
        ls.append(x)
        x = cx
        while x < W - 1 and g[y, x] <= th and solid[y, x]:
            x += 1
        rs.append(x)
    left, right = int(np.median(ls)), int(np.median(rs))
    tops, bots = [], []
    for x in range(left + (right - left) // 4, right - (right - left) // 4, 6):
        y = cy
        while y > 0 and g[y, x] <= th and solid[y, x]:
            y -= 1
        tops.append(y)
        y = cy
        while y < H - 1 and g[y, x] <= th and solid[y, x]:
            y += 1
        bots.append(y)
    foot = int(np.max(np.nonzero(solid[:, max(0, cx - W // 8):cx + W // 8].any(axis=1))[0]))
    return left, int(np.median(tops)), right, int(np.median(bots)), int(min(tops)), foot


def stele():
    dst_dir = os.path.join(ASSETS, 'stele')
    os.makedirs(dst_dir, exist_ok=True)
    d = data()
    keys = [s['art'] for e in d['eras'] for s in e['steles'] if s.get('art')] + [d['end']['art']] + sorted(set(TPL.values()))
    out, tot, miss = {}, 0, []
    for k in keys:
        p = os.path.join(SRC, k + '.png')
        if not os.path.exists(p):
            miss.append(k)
            continue
        im = Image.open(p).convert('RGBA')
        W, H = im.size
        dst = os.path.join(dst_dir, k + '.webp')
        if k.startswith('m'):
            # 11-14 碑形：横的竖的照原样存，碑牌上的字不刻在图上（点开以后另有一块碑牌），只量有画的那一块：
            # top 是碑最高处在图的哪一成，foot 是碑坪的前沿（落地的地方），l、r 是左右
            tall = H >= W
            if not fresh(dst, p):
                im.resize((640, 960) if tall else (960, 640), Image.LANCZOS).save(dst, 'WEBP', quality=86, method=6)
            bb = im.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox() or (0, 0, W, H)
            out[k] = {'x': round(bb[0] / W, 4), 'y': round(bb[1] / H, 4), 'w': round((bb[2] - bb[0]) / W, 4), 'h': round((bb[3] - bb[1]) / H, 4),
                      'top': round(bb[1] / H, 4), 'foot': round(bb[3] / H, 4), 'o': 't' if tall else 'w', 'v': int(os.path.getmtime(p))}
            tot += os.path.getsize(dst)
            continue
        if not fresh(dst, p):
            im.resize((640, 960), Image.LANCZOS).save(dst, 'WEBP', quality=86, method=6)
        l, t, r, b, apex, foot = face_of(im)
        out[k] = {'x': round(l / W, 4), 'y': round(apex / H, 4), 'w': round((r - l) / W, 4), 'h': round((b - apex) / H, 4), 'top': round(t / H, 4), 'foot': round(foot / H, 4), 'v': int(os.path.getmtime(p))}
        # 有几张抠图底下和两边还连着一块画（碑下的地、城墙），立在路边是一块方的；记一笔，页面给它的边缘虚掉
        a = im.split()[3]
        bot = sum(1 for x in range(0, W, 4) if a.getpixel((x, H - 3)) > 40) / len(range(0, W, 4))
        side = max(sum(1 for y in range(0, H, 4) if a.getpixel((xx, y)) > 40) / len(range(0, H, 4)) for xx in (2, W - 3))
        if bot > 0.1 or side > 0.1:
            out[k]['edge'] = 1
        tot += os.path.getsize(dst)
    # 没出图的碑先拿它那一种空碑样板顶着（页面照 data/stele.json 的 tpl 认）
    tpl = {}
    for e in d['eras']:
        for s in e['steles']:
            tpl[s['name']] = TPL.get(s.get('kind', 'bronze'), 't_bronze')
    tpl['无字碑'] = 't_white'
    save_json('stele.json', {'box': out, 'tpl': tpl})
    print('碑和样板', len(out), '张，', tot // 1024, 'KB；还没出的', len(miss), '：', ' '.join(miss), '；写了 data/stele.json')


# ---- 人像 ----
PW, PH, PCOLS = 300, 450, 8


def art_of(c):
    if c.get('pset') == '神明显像':
        return os.path.join(GODS, c['key'] + '.png')
    return os.path.join(COMFY, 'out', PSET_DIR.get(c['pset'], '立绘_' + c['pset']), 'art', 'art_' + c['key'] + '.webp')


def people(e):
    return e['cast'] + e.get('meet', []) + e.get('legends', []) + e.get('gods', [])


def por():
    """时代页里的人像：一页一张拼图 assets/pa/页.webp（旅伴、相遇、传奇、神与魔神，一格 300×450，一行八格），哪一格是谁写进 data/pa.json。"""
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
                print('没有图', e['id'], c['name'], src)
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
    save_json('pa.json', out)
    print('人像拼图：', len(out), '张，', total // 1024, 'KB；缺', miss, '，写了 data/pa.json')


def spr():
    """档案页用的图，一人一张 assets/ps/键.webp（2560×1216）：上面一行四套衣服，下面一行九格表情。神和魔神的显像另存 assets/god/键.webp。备了哪些写进 data/have.json。"""
    dst_dir, god_dir = os.path.join(ASSETS, 'ps'), os.path.join(ASSETS, 'god')
    os.makedirs(dst_dir, exist_ok=True)
    os.makedirs(god_dir, exist_ok=True)
    have, gods, total = [], [], 0
    for e in data()['eras']:
        for c in e['cast'] + e.get('meet', []) + e.get('legends', []):
            k = c.get('key')
            if not k or k in have or c.get('pset') == '神明显像':
                continue
            art = os.path.join(COMFY, 'out', PSET_DIR.get(c['pset'], '立绘_' + c['pset']), 'art')
            a, b = os.path.join(art, 'por_' + k + '.webp'), os.path.join(art, 'face_' + k + '.webp')
            if not os.path.exists(a) or not os.path.exists(b):
                print('没有', e['id'], c['name'], a if not os.path.exists(a) else b)
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
                sheet.save(dst, 'WEBP', quality=88, method=6)
            have.append(k)
            total += os.path.getsize(dst)
        for g in e.get('gods', []):
            k = g.get('key')
            if not k or k in gods:
                continue
            src = os.path.join(GODS, k + '.png')
            if not os.path.exists(src):
                print('没有显像', g['name'], k)
                continue
            dst = os.path.join(god_dir, k + '.webp')
            if not fresh(dst, src):
                Image.open(src).convert('RGB').resize((768, 1152), Image.LANCZOS).save(dst, 'WEBP', quality=84, method=6)
            gods.append(k)
            total += os.path.getsize(dst)
    hp = os.path.join(HERE, 'data', 'have.json')
    old = json.load(open(hp, encoding='utf-8')) if os.path.exists(hp) else {}
    old.update({'ps': sorted(have), 'god': sorted(gods)})
    save_json('have.json', old)
    print('立绘加表情', len(have), '张，显像', len(gods), '张，', total // 1024, 'KB，写了 data/have.json')


BW, BH = 480, 720          # 灾祸拼图里一格多大


def boss():
    """史诗战的对手：一个对手一张拼图 assets/boss/一阶的键.webp，各阶从左到右一格（480×720）排成一行，省发布的文件数。
    哪一张有几格、各是第几阶写进 data/have.json 的 boss：{一阶的键: {n: 几格, p: [第几阶, …], v: 版本}}；没出图的那一阶跳过，名字照旧用一阶那个键。
    页面上缩略图拿 background-size 和 background-position 露头一格，点开看大图只露那一格。不在拼图里的旧单张从 assets/boss/ 拿掉。"""
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
                strip.save(dst, 'WEBP', quality=80, method=6)
            out[ks[0]] = {'n': len(got), 'p': [j for j, _ in got], 'v': int(os.path.getmtime(dst))}
            total += os.path.getsize(dst)
    gone = [f for f in os.listdir(dst_dir) if f[:-5] not in out]
    for f in gone:
        os.remove(os.path.join(dst_dir, f))
    hp = os.path.join(HERE, 'data', 'have.json')
    old = json.load(open(hp, encoding='utf-8')) if os.path.exists(hp) else {}
    old['boss'] = out
    save_json('have.json', old)
    print('灾祸的拼图', len(out), '张（合计', sum(v['n'] for v in out.values()), '格），', total // 1024, 'KB；拿掉旧的单张', len(gone), '张')


def cg():
    """时代原画、节点原画、死的那一刻。哪一幅配哪一条主线的哪一幕、叫什么，照 cg_table.json（scenes/merge_scenes.py 并出来的）；图还没出的那一行跳过。
    时代原画是 gpt_cg3.py 的 e1..e6，表里写 era 指到哪一页。"""
    table = json.load(open(os.path.join(HERE, 'cg_table.json'), encoding='utf-8'))
    dst_dir = os.path.join(ASSETS, 'cg')
    os.makedirs(dst_dir, exist_ok=True)
    out, total, n, lack = {}, 0, 0, []
    for stem, t in table.items():
        base = t.get('src', stem)
        src = os.path.join(SRC, base + '.png')
        if not os.path.exists(src):
            lack.append(stem)
            continue
        rev = table.get(base, t).get('rev')
        name = base + ('_r%d' % rev if rev else '')
        dst = os.path.join(dst_dir, name + '.webp')
        if not fresh(dst, src):
            im = Image.open(src).convert('RGB')
            if im.width > 1536:
                im = im.resize((1536, round(im.height * 1536 / im.width)), Image.LANCZOS)
            im.save(dst, 'WEBP', quality=86, method=6)
        total += os.path.getsize(dst)
        n += 1
        era = out.setdefault(t.get('era') or stem.split('_')[0], {'nodes': {}})
        rel = 'assets/cg/%s.webp' % name
        if t.get('key'):
            era['key'] = {'src': rel}
        elif t.get('death'):
            era.setdefault('deaths', {})[t['death']] = {'src': rel, 'name': t.get('name', '')}
        else:
            slot, item = era['nodes'].setdefault(t['line'], {}), {'src': rel, 'name': t.get('name', '')}
            if t['act'] in slot:
                prev = slot[t['act']]
                slot[t['act']] = (prev if isinstance(prev, list) else [prev]) + [item]
            else:
                slot[t['act']] = item
    save_json('cg.json', out)
    print('写了 data/cg.json：', n, '幅，', total // 1024, 'KB；还没出图的', len(lack), '幅', ' '.join(lack[:12]) + (' …' if len(lack) > 12 else ''))


if __name__ == '__main__':
    what = sys.argv[1:] or ['sky', 'tex', 'props', 'walk', 'stele', 'por', 'spr', 'boss', 'cg']
    for name, fn in (('sky', sky), ('tex', tex), ('props', props), ('walk', walk), ('stele', stele), ('spr', spr), ('por', por), ('boss', boss), ('cg', cg)):
        if name in what:
            fn()
