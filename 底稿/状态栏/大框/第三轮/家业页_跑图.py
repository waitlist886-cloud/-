#!/usr/bin/env python3
# 家业页这一份要的图（11-23 状态栏第三轮）：魔宠坐骑的头像一张拼图（4×4 十六种），领地卡头上的那幅地一纪一张。
# 出图走本机 Codex 的订阅额度（底稿/状态栏/comfy/gpt_gen.py），画风照 out/图标_通用_11-23/总览.jpg 那一批（底稿/图标/tools/gpt_generic.py 的 STYLE）。
#   CODEX_HOME=C:/Users/waitl/.codex_b <ComfyUI 的 python> 底稿/状态栏/大框/第三轮/家业页_跑图.py gen [pets land_maze land_moon land_strife land_bronze land_pre]
#   <ComfyUI 的 python> 底稿/状态栏/大框/第三轮/家业页_跑图.py cut      抠底、切格、压成 webp：out/第三轮_家业页/art/pets.webp（4×4，一格 128）、land_<纪>.webp（1200×400）、总览.jpg
# 原图在 out/第三轮_家业页/sheet_pets.png、land_<纪>.png，已有的不重出。
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', 'comfy'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '图标', 'tools'))
sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.join(ROOT, 'out', '第三轮_家业页')
ART = os.path.join(OUT, 'art')

# 次序就是拼图里的格子（一行四只），跟 estate_page.py 的 PETS 对着
PETS = [
    ('狮鹫', 'a griffin: a golden-brown eagle head with a white feathered crest and amber eyes, chest feathers under a leather riding harness with a small sun medallion'),
    ('风暴亚龙', 'a young storm wyvern: a slate-blue scaled dragon head with small swept-back horns, a pale frost-blue frill, bright yellow eyes, a few tiny sparks at the jaw'),
    ('月鹿', 'a white-silver stag with elegant branching antlers that glow faintly pale blue, small silver bells and a blue ribbon hanging from the antlers'),
    ('狼', 'a grey wolf with thick fur, ice-blue eyes and a red cloth collar'),
    ('鹰', 'a brown and white falcon with sharp golden eyes and a small leather hood pushed back on its head'),
    ('猫', 'a sleek dark grey cat with one notched ear, big green eyes and a brass coin tag on a thin collar'),
    ('马', 'a chestnut horse with a white blaze and a flowing dark mane, leather bridle with brass fittings'),
    ('机关驮兽', 'a dwarven mechanical pack beast: a brass and iron ox-like automaton head with riveted plates, one glowing amber crystal eye and two small steam pipes'),
    ('猎犬', 'a lean grey-backed hunting dog with floppy ears, brown eyes and a studded leather collar'),
    ('海骑', 'a sea steed: a teal-blue hippocampus horse head with a translucent fin mane, pearly scales on the neck and a coral bridle'),
    ('枭', 'a tawny owl with big round golden eyes and ear tufts'),
    ('狐', 'a red fox with a white chest, clever amber eyes and a small green scarf'),
    ('发条猎犬', 'a clockwork hound: a slim black-steel mechanical dog head with brass gears showing at the jaw, one cyan glass eye and a wind-up key behind the neck'),
    ('陆行蜥', 'a riding land drake: a sand-coloured wingless lizard mount head with a blunt snout, calm orange eyes, leather blinkers and a saddle strap'),
    ('渡鸦', 'a glossy black raven with a blue sheen on its feathers, a bright eye and a tiny scroll tube tied at its neck'),
    ('岩羊', 'a shaggy white-grey mountain ram with big curled horns and a woven red pack strap'),
]
STYLE = ('A sheet of creature portrait icons for the companion and mount screen of a high-end Japanese anime-style fantasy action RPG. '
         'Stylized game art, not photorealistic: confident simplified shapes, smooth cel-shaded colour planes finished with a little soft hand-painted gradient, '
         'crisp clean silhouettes, bright warm rim highlights, saturated but harmonious colours, no gritty texture noise. '
         'Each icon is a head-and-shoulders bust portrait of one creature in three-quarter view facing left, with a noble, alert expression, instantly recognisable at a very small size, light from the upper left. ')
GRID = ('Square picture, aspect ratio 1:1. Exactly sixteen separate busts in a perfectly regular grid of 4 columns and 4 rows, in the listed order, left to right, top to bottom. '
        'Each bust is centered in its own cell, fills about two thirds of the cell, is cut off cleanly at the shoulders, has empty space all around it and never touches or overlaps a neighbour. '
        'The background is one flat, solid, pure magenta colour (#FF00FF) filling the whole picture edge to edge: no gradient, no checkerboard, no texture, no vignette, no cell borders, no circles or frames behind the busts. '
        'No creature contains any magenta, pink or purple-red; dark creatures are deep indigo, black-blue or charcoal. Any glow stays on the creature itself; no haze, halo or smoke spreading onto the background. '
        'No text, no letters, no numbers, no labels, no frames, no ground, no cast shadow on the background. ')

LAND_STYLE = ('A wide landscape background painting for the "my domain" card of a high-end Japanese anime-style fantasy RPG interface. '
              'Painterly anime background art: clean simplified shapes, soft hand-painted gradients, crisp silhouettes layered in depth, luminous sky, a little atmospheric haze between the layers. '
              'Landscape picture, aspect ratio 3:2. Everything important sits in the middle horizontal band of the picture; the top third is open sky and the bottom fifth is dark, quiet foreground, '
              'and the lower left corner stays calm and dark so that a title can be laid over it. Seen from a distance, slightly from above. '
              'No people in the foreground, no text, no letters, no frame, no border, no user interface. ')
LANDS = {
    'maze': ('A small border fief at the last light before dawn: a compact stone keep with one tall banner on a low hill, a windmill, wheat terraces, a cluster of roofs with a few warm lit windows, a river and a far town on the horizon. '
             'Palette: deep indigo and violet night sky turning to antique gold at the horizon, gold rim light on the keep and the wheat, a scatter of four-pointed stars.'),
    'moon': ('An early bronze-age homestead at a cold misty dawn: a timber palisade village gathered around one great bonfire on a riverside meadow, a ring of grey standing stones, barley plots, a wooden watch platform, snow-capped grey mountains behind. '
             'Palette: slate blue, silver grey and pale mist, with the single warm orange glow of the bonfire and star dust in the sky.'),
    'strife': ('A defended sector behind a colossal ancient wall at a smoky daybreak: the giant wall runs along the horizon with small watch fires on top, in front of it earthwork trenches, timber ballista platforms, a field hospital of tents with white candle lights, a grain cellar mound and a tattered signal banner. '
               'Palette: iron grey, charcoal and rust red, embers of orange in the smoke, a warm wind-blown sky the colour of old iron.'),
    'bronze': ('A granted river land outside a white-stone city in golden afternoon light: a reclaimed riverbank with young wheat plots, a wooden jetty with a barge, a timber fence, a boundary stele of white stone, and far behind it a hill city of white stone stairs, copper roofs and dark obsidian towers. '
               'Palette: warm white, burnished copper and bronze, obsidian black accents, pale gold sky.'),
    'pre': ('A frontier holding near the mouth of a vast labyrinth pit, drawn as a sepia copperplate engraving on old parchment: a walled guild outpost with a bell tower and a hoisted banner, timber cranes and tents along the rim of the pit, terraced fields and a dirt road with wagons. '
            'Fine cross-hatched ink lines in brown-black on warm parchment, a light watercolour wash of ochre and faded teal, no bright colours.'),
}


def gen(names):
    import gpt_gen
    os.makedirs(OUT, exist_ok=True)
    for k in names:
        if k == 'pets':
            stem = os.path.join(OUT, 'sheet_pets')
            pr = STYLE + GRID + 'The sixteen creatures: ' + ' '.join('%d. %s.' % (i + 1, look) for i, (_, look) in enumerate(PETS))
        else:
            stem = os.path.join(OUT, k)
            pr = LAND_STYLE + LANDS[k[len('land_'):]]
        try:
            print(k, gpt_gen.gen(stem, pr), flush=True)
        except Exception as x:   # 额度、超时：这一张不出，别的照出
            print(k, '没成：%s' % str(x)[:300], flush=True)


def cut():
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(ART, exist_ok=True)
    tiles = []
    p = os.path.join(OUT, 'sheet_pets.png')
    if os.path.exists(p):
        import gpt_generic as GG
        # 一只一只画得满，上下两行挨着，照连通块切会粘在一起：整张先抠底，再照 4×4 的格线直切，一格里取外框。
        # 胸像底下是齐着格线切平的，放进圆头像时贴着格底放，平的那一道边正好落在圆外头
        im = GG.key(p)
        W, H = im.size
        C = 128
        sprite = Image.new('RGBA', (C * 4, C * 4), (0, 0, 0, 0))
        for i in range(16):
            col, row = i % 4, i // 4
            t = im.crop((round(col * W / 4), round(row * H / 4), round((col + 1) * W / 4), round((row + 1) * H / 4)))
            bb = t.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
            c = t.crop(bb)
            k = min((C - 6) / c.width, (C - 4) / c.height)
            c = c.resize((max(1, round(c.width * k)), max(1, round(c.height * k))), Image.LANCZOS)
            cell = Image.new('RGBA', (C, C), (0, 0, 0, 0))
            cell.alpha_composite(c, ((C - c.width) // 2, C - c.height))
            sprite.alpha_composite(cell, (col * C, row * C))
            tiles.append((PETS[i][0], cell))
        # 一格 128 压不进 60KB 就整张缩一档（样式里按百分比取格，格子多大都行；头像最大画到 64 像素）
        for c2, q in ((128, 80), (128, 70), (120, 70), (112, 70), (112, 62), (104, 62)):
            out = sprite if c2 == C else sprite.resize((c2 * 4, c2 * 4), Image.LANCZOS)
            out.save(os.path.join(ART, 'pets.webp'), quality=q, method=6, alpha_quality=60)
            if os.path.getsize(os.path.join(ART, 'pets.webp')) <= 60 * 1024:
                break
        print('pets.webp', out.size, os.path.getsize(os.path.join(ART, 'pets.webp')) // 1024, 'KB，质量', q)
    lands = []
    for k in LANDS:
        p = os.path.join(OUT, 'land_%s.png' % k)
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert('RGB')
        W, H = im.size
        h = round(W / 3)
        top = max(0, min(H - h, round(H * 0.5 - h * 0.52)))   # 取正中偏上的那一道
        full = im.crop((0, top, W, top + h))
        dst = os.path.join(ART, 'land_%s.webp' % k)
        for w, q in ((1200, 78), (1200, 70), (1200, 62), (1080, 62), (1080, 54), (960, 54), (960, 46), (880, 44)):
            band = full.resize((w, w // 3), Image.LANCZOS)
            band.save(dst, quality=q, method=6)
            if os.path.getsize(dst) <= 60 * 1024:
                break
        print('land_%s.webp' % k, band.size, os.path.getsize(dst) // 1024, 'KB，质量', q)
        lands.append((k, band))
    # 总览
    T = 150
    over = Image.new('RGB', (T * 4 + 16 + 620, max(T * 4 + 16, 16 + 210 * len(lands))), (38, 40, 52))
    dr = ImageDraw.Draw(over)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
    for i, (name, cell) in enumerate(tiles):
        x, y = 8 + (i % 4) * T, 8 + (i // 4) * T
        dr.ellipse((x + 8, y + 4, x + T - 8, y + T - 12), fill=(58, 60, 110))
        over.paste(cell, (x + 11, y + 7), cell)
        dr.text((x + 8, y + T - 20), name, font=font, fill=(226, 224, 214))
    for i, (k, band) in enumerate(lands):
        over.paste(band.resize((600, 200), Image.LANCZOS), (T * 4 + 24, 8 + i * 210))
        dr.text((T * 4 + 30, 12 + i * 210), k, font=font, fill=(255, 255, 255))
    over.save(os.path.join(OUT, '总览.jpg'), quality=90)
    print('总览.jpg', over.size)


if __name__ == '__main__':
    cmd, names = (sys.argv[1:2] or ['cut'])[0], sys.argv[2:]
    if cmd == 'gen':
        gen(names or ['pets'] + ['land_' + k for k in LANDS])
    elif cmd == 'cut':
        cut()
    else:
        sys.exit('用法见文件头')
