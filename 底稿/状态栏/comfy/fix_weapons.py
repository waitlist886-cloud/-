#!/usr/bin/env python3
# 1001 那一套：只改战斗格里的兵器（11-07，用户要大兵器更有威慑力、长柄别扭曲、弓分短弓长弓猎弓巨弓）。
# 做法：两位的战斗格拼成一张 3:2 的图交给 GPT，叫它原样重画、只换兵器；出来的图按连通区域切成两个人，
# 按拼图时的缩放还原到设定图的尺度，跟设定图里另外三套衣服一起重切四格（四格同一个比例，脚踩格子底），
# 再重做 head.png 和 sheet.png。旧的四格、head、sheet 挪进 out/立绘_v3_备选/<键>/兵器前/。
# 兵器画得太大会把四格一起缩小（格子 640×960 是定的），人缩到 0.85 以下的那一位单独再出一回、叫它画小一点，三回还不行就放弃。
#   python fix_weapons.py <组名> <键…>               出图、切图、拼对比，写在 out/兵器_1107/<组名>/
#   python fix_weapons.py --apply <组名> [键…]        把那一组（或点名的几位）换进 out/立绘_v3/
#   python fix_weapons.py --list                      列出写了兵器的人
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cast_slice as CS  # noqa: E402
import gpt_gen  # noqa: E402

V = os.path.join(HERE, 'out', '立绘_v3')
ALT = os.path.join(HERE, 'out', '立绘_v3_备选')
WORK = os.path.join(HERE, 'out', '兵器_1107')
CELLS = ('casual', 'private', 'battle', 'formal')
# 拼图：一位一张竖版 2:3，人放大到 1.12 倍（出图里人高一千一百多像素，比四套衣服的设定图清楚），头顶上留两成多的空给枪尖、弓梢。
# 头一回试过两位一张横版（人缩到 0.78 倍再放大回来），用户说糙、质感差，不用了，留着只为对照。
PER = 1
LAYOUT = {2: dict(size=(1536, 1024), k=0.78, foot=1000, ratio='3:2', words='two character sprites from the same set, side by side on a transparent background, one on the left and one on the right'),
          1: dict(size=(1024, 1536), k=1.12, foot=1500, ratio='2:3', words='one character sprite on a transparent background')}
MIN_SCALE = 0.85   # 四格的比例缩到旧的这个数以下，算兵器画太大

# 一位一句：只写兵器，握法照旧
WEAPONS = {
    # 巨剑
    'eleanor': 'an enormous two-handed greatsword planted point-down in front of her with both gauntlets resting on its pommel: the blade is nearly as tall as she is and as broad as her forearm, bright steel with a deep fuller down which a name has been chiselled away, the crossguard as wide as her shoulders and sculpted with a knightly crest, a long two-hand grip wrapped in dark blue leather, a heavy faceted pommel; a weapon that looks far too big for anyone else to lift.',
    'valdrak': 'a huge black greatsword planted point-down in front of him with both hands on the grip, drawn in front of the cloak so the whole blade shows: a blade as tall as his chest and a hand\'s breadth wide, black metal with seams of cooling lava, a thin molten-orange line of light along both edges, a wide jagged crossguard like a cooled lava flow, a long grip bound in dark red, a heavy pommel; brutal and immense.',
    'herman': 'a huge dark greatsword planted point-down in front of him, both hands on the pommel, the whole blade visible in front of the cape: a broad black blade as tall as his chest with dragon-scale patterns cast along the flat and a glowing ember-orange groove down its centre, a wide crossguard shaped like two dragon horns, a long grip bound in crimson, a pommel set with a red stone.',
    # 长枪、戟
    'reinhardt': 'a tall knight\'s war lance held upright in his left hand, taller than he is: a thick shaft of pale wood bound with gold rings, a long leaf-shaped silver head as long as his forearm chased with gold filigree and a soft white glow along its edges, a sculpted gold vamplate (hand guard) above his hand, and the plain white unmarked banner hanging from below the head as before; a lance fit for the commander of the whole order.',
    'elena': 'a tall straight silver holy lance held upright against her shoulder in both hands, taller than she is: a shaft of white metal wrapped at the grip in white cord, a long thorn-edged blade head as long as her forearm with small wing-shaped guards at the socket, fine gold-lined engravings, and three faint rings of white light turning around the blade; a holy weapon that dominates the picture.',
    'selephen': 'a long slim wind-lance of pale metal held upright beside him in both hands, taller than he is: the shaft fluted and spiralled like a twisted current of air, a long needle-sharp spiral tip glowing cyan, trailing streaks of light and a few drifting feathers of light at the socket; sharp, elegant and clearly a legend\'s weapon.',
    'alexander': 'a tall silver trident-halberd held upright in front of him in both hands, taller than he is: a heavy broad axe-blade on one side engraved with waves, three long barbed prongs on top, a length of anchor chain wound round the upper shaft, runes along the blade glowing faint sea-blue, a reinforced dark-steel shaft with a butt spike; the weapon of an admiral who boards ships himself.',
    'aletia': 'a tall silver halberd-staff held upright in one hand, taller than she is: a large crystal blade like a prism, as long as her forearm, that splits the light into coloured rays, a crescent counter-blade behind it, silver filigree spiralling down the upper shaft, a few small gem shards floating around the head; refined and formidable.',
    'sirentia': 'a long trident of dark blue metal held point upward in her right hand, taller than she is: three long prongs with inward barbs, the middle one longest, coral and pearl inlaid at the socket, the coral-red thread wound round the shaft as before, tide-light running along the prongs and a few drops of water hanging in the air around the head.',
    'zephyr': 'a long cavalry saddle-lance held upright by his side, taller than he is: a slim tapered shaft of pale wood banded in steel, a bright steel tip, a conical vamplate (hand guard) at the grip, and the long grey-blue pennant streaming from below the tip; built for speed, long and unmistakable.',
    # 锤、斧
    'grom': 'a huge black iron hammer-maul planted head-down in front of him, both hands on the haft: the head a massive block of black iron bigger than his own torso, bound with bronze bands and chains, thin lines of electric blue light crawling over it, the haft as thick as his wrist and wrapped in chain; a weapon only a colossus could lift.',
    'bromgar': 'a huge forge-hammer held upright with its head resting on the floor, both hands on the haft: the head a massive block of black iron with copper edging, bigger than his chest, orange rune lines glowing over it like a furnace and heat shimmer rising off it, the haft thick and iron-banded; a king\'s forge-hammer.',
    'thorin': 'an enormous rune-carved war-hammer held upright with its head on the floor, both hands on the haft: a massive head of black iron edged with red copper, as big as his whole torso, carved with glowing furnace-red runes on every face, the haft thick, iron-banded and braced with brass; the hammer of a grand master smith.',
    'galeblade': 'a huge double-headed battle-axe shouldered across the back of one shoulder as before, the axe-head resting just behind the shoulder: two broad crescent blades each as long as his forearm, dark steel with a bright honed edge and tribal runes, a lion-head boss at the centre, a long thick haft bound in leather and fur.',
    # 弓：巨弓、大长弓、猎弓、长弓
    'elandil': 'a giant bow of living branch-wood drawn halfway with an arrow of pale light nocked: a true great bow as tall as he is, thick limbs of dark wood with bark and small green leaves still growing along them, silver bindings at the grip and tips, the string a bright line; the bow of a ranger-general, far larger and heavier than an ordinary bow.',
    'calantia': 'a great war-longbow gripped diagonally across her body as before, an arrow nocked and the string not drawn: the bow about as tall as she is, with thick ancient yew-like limbs worn pale and smooth from thirteen thousand years of use, horn nocks, a leather-bound grip, small tally marks cut into the belly of the bow; heavy, old and formidable, a bow meant for things larger than men.',
    'sylphy': 'a fine elven hunting bow held in her left hand, an arrow drawn in her right as before: a slender recurve bow a little shorter than she is, silver-white wood with leaf-shaped carved tips, thin silver inlay and a small glowing green leaf-rune at the grip, the string a bright line; elegant, light and precise rather than big.',
    'linwy': 'a tall northern longbow held upright in one hand, an arrow nocked and half-drawn along it as before: a long straight-limbed longbow nearly as tall as she is, of pale ice-blue wood with faintly glowing frost runes along the limbs, horn tips rimed with ice, a fur-wrapped grip; a hunter\'s long-range bow, simple and tall.',
}

EDIT = ('Image 1 is a finished picture: {words}. '
        'Repaint it as the very same picture, aspect ratio {ratio}, at the same scale and in the same layout: each figure keeps exactly its face, hair, eyes, skin, body proportions, height, pose, clothes, armour, colours, lighting and position; nothing about the characters themselves changes. '
        'The ONLY change is the weapon each one holds, redrawn as described below and held in the same hand(s) at the same spot. '
        '{spec} '
        'Every weapon is drawn straight and solid, in correct perspective, with a straight shaft or blade (no bends, kinks, warps or impossible joints), its full length visible. '
        'Size limit: the weapon\'s highest point rises at most about one head-height above the top of the head, and it reaches sideways at most about one arm\'s length beyond the body; it stays well inside its own part of the picture and never overlaps or touches another figure. '
        'Within that limit make the weapon imposing through mass, ornament and detail rather than height: a thick shaft or grip, a large heavy head or a broad blade, rich engraving and fittings. '
        'Render at the finest detail you can, at least as crisp as the input: sharp thin warm-brown line art, clean colouring with soft gradients, light shading, fine engraving, filigree and texture on the metal and wood of the weapon. '
        'Transparent background: no floor, no cast shadow, no glow or haze around the figures. No text, no labels, no numbers, no frame, no dividing lines. ')
RETRY = 'Leave a much wider empty gap between the figures this time and keep every weapon, cape and lock of hair well inside its own part of the picture. '
SMALLER = 'Draw the weapon noticeably smaller than you would otherwise: its top no higher than half a head above the head, its sides within half an arm\'s length of the body; impressive by its design and detail, not by sheer size. '


def figs_of(k):
    figs = CS.figures(CS.clean(Image.open(os.path.join(V, k, 'sheet.png'))))
    if figs is None:
        raise RuntimeError('设定图分不开 ' + k)
    return figs


def make_input(stem, keys):
    L = LAYOUT[len(keys)]
    W, H = L['size']
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for i, k in enumerate(keys):
        fig = figs_of(k)[2]
        bb = fig.getchannel('A').getbbox()
        c = fig.crop(bb)
        r = c.resize((round(c.width * L['k']), round(c.height * L['k'])), Image.LANCZOS)
        hx = (CS.head_x(fig) - bb[0]) * L['k']
        cx = W // 2 if len(keys) == 1 else W // 4 + i * (W // 2)
        canvas.alpha_composite(r, (round(cx - hx), L['foot'] - r.height))
    canvas.save(stem + '_in.png')
    return stem + '_in.png'


def head_png(cell, path):
    bb = cell.getchannel('A').getbbox()
    h = bb[3] - bb[1]
    a = cell.getchannel('A').crop((0, bb[1], cell.width, bb[1] + h // 8))
    x0, _, x1, _ = a.getbbox()
    cx = (x0 + x1) // 2
    w = h * 22 // 100
    crop = cell.crop((max(0, cx - w // 2), bb[1], min(cell.width, cx + w // 2), bb[1] + w))
    bg = Image.new('RGBA', crop.size, (255, 255, 255, 255))
    bg.alpha_composite(crop)
    bg.convert('RGB').resize((crop.width * 4, crop.height * 4), Image.LANCZOS).save(path)


def rebuild(k, new_fig, kscale, outdir):
    """new_fig：出图里切出来的这一位（出图尺度）。还原到设定图尺度，跟另外三套一起重切四格。回新旧四格比例之比。"""
    figs = figs_of(k)
    old = figs[2]
    bb = new_fig.getchannel('A').getbbox()
    c = new_fig.crop(bb).resize((round((bb[2] - bb[0]) / kscale), round((bb[3] - bb[1]) / kscale)), Image.LANCZOS)
    # 放回设定图上旧人的位置：脚底对齐，头对准旧人的头
    obb = old.getchannel('A').getbbox()
    ohx = CS.head_x(old)
    nhx = (CS.head_x(new_fig) - bb[0]) / kscale
    layer = Image.new('RGBA', (old.width * 2, old.height * 2), (0, 0, 0, 0))   # 大一圈，枪尖伸出设定图也留着
    ox, oy = old.width // 2, old.height // 2
    layer.alpha_composite(c, (round(ox + ohx - nhx), oy + obb[3] - c.height))
    big = []
    for f in figs:
        b = Image.new('RGBA', layer.size, (0, 0, 0, 0))
        b.alpha_composite(f, (ox, oy))
        big.append(b)
    big[2] = layer
    cells, s = CS.cells(big)
    s_old = CS.cells(figs)[1]
    os.makedirs(outdir, exist_ok=True)
    for name, f in zip(CELLS, cells):
        f.save(os.path.join(outdir, 'cell_%s.png' % name))
    head_png(cells[0], os.path.join(outdir, 'head.png'))
    sheet = Image.new('RGBA', (old.width, old.height), (0, 0, 0, 0))
    for f in big:
        sheet.alpha_composite(f.crop((ox, oy, ox + old.width, oy + old.height)))
    sheet.save(os.path.join(outdir, 'sheet.png'))
    return s / s_old


def grey(im, h):
    im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, (60, 62, 74, 255))
    bg.alpha_composite(im)
    im = bg.convert('RGB')
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def compare(stem, keys, note):
    F = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 26)
    gdir = os.path.dirname(stem)
    outs = []
    for n in range(0, len(keys), 4):
        cols = []
        for k in keys[n:n + 4]:
            a = grey(Image.open(os.path.join(V, k, 'cell_battle.png')), 900)
            b = grey(Image.open(os.path.join(gdir, k, 'cell_battle.png')), 900)
            s = Image.new('RGB', (a.width + b.width + 10, 940), (20, 20, 26))
            s.paste(a, (0, 40))
            s.paste(b, (a.width + 10, 40))
            ImageDraw.Draw(s).text((4, 4), '%s  改前 ｜ 改后  %s' % (k, note.get(k, '')), font=F, fill=(255, 230, 160))
            cols.append(s)
        big = Image.new('RGB', (sum(c.width for c in cols) + 30, 940), (20, 20, 26))
        x = 0
        for c in cols:
            big.paste(c, (x, 0))
            x += c.width + 30
        p = '%s_对比_%d.jpg' % (stem, n // 4 + 1)
        big.save(p, quality=88)
        outs.append(p)
    return outs


def gen_cut(gdir, tag, keys, extra):
    L = LAYOUT[len(keys)]
    stem = os.path.join(gdir, tag)
    src = make_input(stem, keys)
    spec = ' '.join(('%s figure: %s' % (('LEFT', 'RIGHT')[i] if len(keys) == 2 else 'The', WEAPONS[k])) for i, k in enumerate(keys))
    for attempt in range(2):
        st = stem if attempt == 0 else stem + '_b'
        prompt = EDIT.format(words=L['words'], ratio=L['ratio'], spec=spec) + extra + (RETRY if attempt else '')
        out = gpt_gen.gen(st, prompt, refs=[src])[0]
        figs = CS.figures(CS.clean(Image.open(out)), len(keys))
        if figs is not None:
            return figs
        print('分不开，重出一回', tag, keys)
    return None


def one(gdir, tag, g, extra, note):
    """一组（一位或两位）：出图、切、重切四格。回还要再出的键。"""
    figs = gen_cut(gdir, tag, g, extra)
    if figs is None:
        print('两回都分不开', g)
        return list(g)
    nxt = []
    for k, f in zip(g, figs):
        ratio = rebuild(k, f, LAYOUT[len(g)]['k'], os.path.join(gdir, k))
        note[k] = '四格 %.2f%s' % (ratio, '' if ratio >= MIN_SCALE else ' 太大')
        print('%s 四格比例 %.3f %s' % (k, ratio, '好了' if ratio >= MIN_SCALE else '兵器太大，再出一回'), flush=True)
        if ratio < MIN_SCALE:
            nxt.append(k)
    return nxt


def run(group, keys):
    from concurrent.futures import ThreadPoolExecutor
    for k in keys:
        if k not in WEAPONS:
            raise KeyError('没写兵器 ' + k)
    gdir = os.path.join(WORK, group)
    os.makedirs(gdir, exist_ok=True)
    todo, note, extra = list(keys), {}, ''
    workers = int(os.environ.get('CAST_WORKERS') or 3)
    for rnd in range(3):
        if not todo:
            break
        groups = [todo[i:i + PER] for i in range(0, len(todo), PER)]
        with ThreadPoolExecutor(workers) as ex:
            rs = list(ex.map(lambda a: one(gdir, 'r%d_%s' % (rnd, '_'.join(a)), a, extra, note), groups))
        todo, extra = [k for r in rs for k in r], SMALLER
    if todo:
        print('三回还是太大，留着最后一回的：', ' '.join(todo))
    print('对比', ' '.join(compare(os.path.join(gdir, 'gpt'), list(keys), note)))


def apply(group, keys=()):
    gdir = os.path.join(WORK, group)
    ks = keys or [d for d in os.listdir(gdir) if os.path.isdir(os.path.join(gdir, d))]
    for k in ks:
        od = os.path.join(gdir, k)
        bak = os.path.join(ALT, k, '兵器前')
        os.makedirs(bak, exist_ok=True)
        for f in ['cell_%s.png' % n for n in CELLS] + ['head.png', 'sheet.png']:
            if os.path.exists(os.path.join(V, k, f)) and not os.path.exists(os.path.join(bak, f)):
                shutil.move(os.path.join(V, k, f), os.path.join(bak, f))
            shutil.copy2(os.path.join(od, f), os.path.join(V, k, f))
        print('换了', k, '旧的在', bak)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--list']:
        for k in WEAPONS:
            print(k)
    elif a[:1] == ['--apply']:
        apply(a[1], a[2:])
    else:
        run(a[0], a[1:])
