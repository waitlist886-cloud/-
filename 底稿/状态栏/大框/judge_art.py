#!/usr/bin/env python3
# 检定演出面板的美术（11-23，状态栏第三轮「检定演出」那一份）：一纪一张拼图，六样：二十面骰、对决徽记（剑压着盾）、空心徽记（别的类往里放字形）、
# 框角的花饰、结果绶带、裂开的骰子。品红平底出图再抠透明（抠法照 底稿/图标/tools/gpt_generic.py 的 key）。
#   CODEX_HOME=C:/Users/waitl/.codex_b <ComfyUI 的 python> 底稿/状态栏/大框/judge_art.py gen [纪…]   出图，写 out/第三轮_检定演出/sheet_<纪>.png，已有的不重出
#   <ComfyUI 的 python> 底稿/状态栏/大框/judge_art.py cut [纪…]    抠底、切六样、压 webp：out/第三轮_检定演出/art/judge_<纪>_<件>.webp，另出一张 总览.jpg
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', 'comfy'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '图标', 'tools'))
sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.join(ROOT, 'out', '第三轮_检定演出')
COLS, ROWS = 3, 2
PARTS = ['die', 'duel', 'ring', 'corner', 'ribbon', 'crack']
# 每一件压成多宽（显示尺寸的两倍上下）
WIDTH = {'die': 208, 'duel': 184, 'ring': 184, 'corner': 150, 'ribbon': 480, 'crack': 208}

STYLE = ('A sheet of ornate user-interface ornaments for the dice-check panel of a high-end Japanese anime-style fantasy RPG. '
         'Stylized game UI art, not photorealistic: confident simplified shapes, smooth cel-shaded colour planes finished with a little soft hand-painted gradient, crisp clean silhouettes, '
         'fine engraved line ornament, bright rim highlights, materials that read at a glance. Every piece is drawn flat-on from the front like an emblem, perfectly symmetrical where it can be, light from the upper left. ')
GRID = ('Landscape picture, aspect ratio 3:2. Exactly six separate objects in a perfectly regular grid of 3 columns and 2 rows, in the listed order, left to right, top to bottom. '
        'Each object is centered in its own cell, fills about three quarters of the cell, has empty space all around it and never touches or overlaps a neighbour. '
        'The background is one flat, solid, pure magenta colour (#FF00FF) filling the whole picture edge to edge: no gradient, no checkerboard, no texture, no vignette, no cell borders. '
        'No object contains any magenta, pink or purple-red. Any glow stays on the object itself as inner light and a few small sparkles hugging its surface; no haze, halo or smoke spreading onto the background. '
        'No text, no letters, no numbers, no numerals, no runes that look like writing, no labels, no hands, no ground, no cast shadow on the background. ')
ITEMS = ('The six objects, all made of the same materials so they belong to one set: '
         '1. A twenty-sided die (icosahedron) seen exactly face-on: one large flat equilateral triangle face pointing up sits in the very middle and faces the viewer, completely blank and smooth, '
         'the neighbouring facets fold away around it into a regular hexagonal outline; %(die)s. No number on any face. '
         '2. A round duel medallion: an ornate circular frame, inside it a kite shield seen from the front with a straight sword laid diagonally across it; %(duel)s. '
         '3. A round medallion frame, the same ring as object 2 but its centre is an empty, plain, dark flat disc with nothing in it. '
         '4. A corner ornament for a panel frame: an L-shaped filigree bracket that fits the top-left corner, two slim arms of equal length meeting at a small jewel at the corner, the inside of the L empty; %(corner)s. '
         '5. A blank horizontal ribbon banner, long and low, about four times as wide as it is tall, flat across the middle with nothing written on it, both ends folded back into forked swallowtails; %(ribbon)s. '
         '6. The same twenty-sided die as object 1, same view and same size, but broken: a deep jagged crack splits the blank middle face from top to bottom, hairline fractures spread to the edges and two or three small chips are flying off. ')

ERAS = {
    'maze': dict(theme='Materials: deep night-blue enamel and polished warm gold, with tiny four-pointed and eight-pointed star motifs and thin art-nouveau gold curls; the mood of a starlit cathedral at night. ',
                 die='the die is cut from translucent midnight-blue crystal, every edge bound in thin polished gold, a faint star-like sparkle inside',
                 duel='gold ring with small star points, night-blue enamel field, shield in blue enamel with a gold eight-pointed star, sword in bright gold',
                 corner='gold filigree with a small eight-pointed star and a deep blue cabochon',
                 ribbon='the ribbon is rich night-blue silk with a narrow gold border and a tiny gold star at each fold'),
    'moon': dict(theme='Materials: glossy black obsidian and bright cold silver, with pale ice-blue highlights, fine engraved rings and seven small round studs; austere, ancient, the mood of a silver age of heroes and great beasts. No crescent or moon shapes anywhere. ',
                 die='the die is knapped from glossy black obsidian with glassy conchoidal sheen, every edge inlaid with a bright silver line',
                 duel='silver ring engraved with fine concentric lines and seven round studs, obsidian-black field, shield in brushed silver with a plain boss, sword in bright silver',
                 corner='silver filigree with fine parallel engraved lines and a pale ice-blue cabochon',
                 ribbon='the ribbon is pale silver-grey silk with a darker slate border and a small silver stud at each fold'),
    'strife': dict(theme='Materials: dark forged iron with round rivets, worn brass trim and deep red enamel, plus aged cream war-report paper; rough, martial, the mood of an endless war along a great wall. ',
                   die='the die is forged from dark hammered iron, edges worn bright, a small round rivet at each corner, thin lines of red enamel in the seams',
                   duel='riveted iron ring with brass trim, dark red enamel field, heater shield in dented iron with a red stripe, sword in plain steel',
                   corner='iron bracket with three rivets, a brass edge and a small red enamel stud',
                   ribbon='the ribbon is a strip of aged cream war-report paper with torn swallowtail ends, a thin red line along the top and bottom edges and a dark red wax seal blob at the left end'),
    'bronze': dict(theme='Materials: warm orichalcum bronze (a glowing copper-gold metal), white limestone and black obsidian inlay, with straight chiselled lines like a carved boundary stele; calm, monumental, the mood of an age of treaties and stone monuments. ',
                   die='the die is cast in warm orichalcum bronze with a soft satin shine, edges crisply bevelled, the middle face inlaid with a plain white limestone triangle',
                   duel='bronze ring with chiselled straight notches, field split in half white limestone and half black obsidian, round bronze shield with a plain rim, sword in bright bronze',
                   corner='bronze bracket with chiselled straight grooves, a white stone square inlay and a small black obsidian stud',
                   ribbon='the ribbon is ivory-white cloth with a bronze-gold woven border and a small square bronze clasp at each fold'),
}


def prompt(era):
    e = ERAS[era]
    return STYLE + e['theme'] + GRID + ITEMS % e


def gen(names):
    import gpt_gen
    os.makedirs(OUT, exist_ok=True)

    def job(k):
        try:
            return gpt_gen.gen(os.path.join(OUT, 'sheet_' + k), prompt(k))
        except Exception as x:
            return '没成：%s' % str(x)[:300]

    with ThreadPoolExecutor(4) as ex:
        for k, r in zip(names, ex.map(job, names)):
            print(k, r, flush=True)


def cut(names):
    import gpt_generic as GG
    from PIL import Image, ImageDraw
    GG.COLS, GG.ROWS = COLS, ROWS
    art = os.path.join(OUT, 'art')
    os.makedirs(art, exist_ok=True)
    T = 240
    over = Image.new('RGB', (T * 6 + 16, T * len(names) + 16), (30, 30, 46))
    for r, k in enumerate(names):
        p = os.path.join(OUT, 'sheet_%s.png' % k)
        if not os.path.exists(p):
            print(k, '没有图')
            continue
        crops, warn = GG.cut_sheet(p)
        for w in warn:
            print(k, w)
        for i, (part, c) in enumerate(zip(PARTS, crops)):
            if c is None:
                continue
            fx = os.path.join(OUT, 'fix_%s_%s.png' % (k, part))
            if os.path.exists(fx):
                c = GG.key(fx)
                bb = c.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
                c = c.crop(bb) if bb else c
            if part in ('die', 'crack', 'duel', 'ring'):   # 方的几样补成正方，样式里好对心
                s = max(c.size)
                sq = Image.new('RGBA', (s, s), (0, 0, 0, 0))
                sq.alpha_composite(c, ((s - c.width) // 2, (s - c.height) // 2))
                c = sq
            w = WIDTH[part]
            c2 = c.resize((w, max(1, round(c.height * w / c.width))), Image.LANCZOS)
            dst = os.path.join(art, 'judge_%s_%s.webp' % (k, part))
            c2.save(dst, 'WEBP', quality=86, method=6)
            print(k, part, c.size, '→', c2.size, os.path.getsize(dst))
            th = c.copy()
            th.thumbnail((T - 16, T - 16))
            over.paste(th, (8 + i * T + (T - th.width) // 2, 8 + r * T + (T - th.height) // 2), th)
    over.save(os.path.join(OUT, '总览.jpg'), quality=88)


if __name__ == '__main__':
    cmd, names = sys.argv[1], sys.argv[2:] or list(ERAS)
    if cmd == 'gen':
        gen(names)
    elif cmd == 'cut':
        cut(names)
    elif cmd == 'prompt':
        print(prompt(names[0]))
