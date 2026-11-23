#!/usr/bin/env python3
# 书架样张的图（11-23）：殿里的书架主画、《公会委托存档》封面和书脊、一排书脊、委托单的纸、藏书票。
# 走本机 Codex（CODEX_HOME=C:/Users/waitl/.codex_b），用 ComfyUI 自带的 python 跑：
#   CODEX_HOME=C:/Users/waitl/.codex_b <ComfyUI 的 python> -X utf8 gen_shelf.py gen [名…]   出图，已有的不重出
#   <ComfyUI 的 python> -X utf8 gen_shelf.py key                                             抠品红底、切图、转 webp 进样张的 img/
# 画风参考拿门面现有两张（迷宫纪卷扉页、公会章首横幅）转成 png 喂进去。
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', 'comfy'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '图标', 'tools'))
sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.join(ROOT, 'out', '门面第二轮', '书架')
IMG = os.path.join(HERE, '..', 'img')
REFSRC = [os.path.join(ROOT, '底稿', '门面', '共用', 'assets', 'wb', 'maze_front.webp'),
          os.path.join(ROOT, '底稿', '门面', '共用', 'assets', 'wb', 'maze_guild.webp')]

STYLE = ('Art style exactly like the attached reference pictures: a flat layered paper-cut illustration, smooth flat colour planes stacked like cut paper, '
         'thin soft pale outlines, big sweeping curves, fine paper grain, calm and solemn fairy-tale mood, Japanese fantasy RPG title-screen quality. '
         'Palette: deep indigo, slate blue, cool grey and bone-white stone. ')
FIRE = 'The only bright, saturated colour is a pale cyan-teal flame (ghost fire, blue-green, never orange). '
MAG = ('The background is one flat, solid, pure magenta colour (#FF00FF) filling the whole picture edge to edge: no gradient, no texture, no vignette, no cast shadow. '
       'The objects contain no magenta, pink or purple-red. ')
NOTEXT = 'No text, no letters, no numbers, no runes that look like writing, no signature, no watermark. '

JOBS = {
    'shelf_main': STYLE + FIRE + (
        'Wide landscape picture, aspect ratio 16:9. The inside of a vast silent hall of tall pale grey-white stone pillars that recede in perspective far into darkness. '
        'Between every pair of pillars a small cyan-teal flame floats in the air by itself, no lamp, no holder, no chain, casting cool cyan light on the stone. '
        'Between the pillars stand very tall bookshelves of pale stone with several tiers, row after row going far into the distance: the nearer shelves hold large old books of many kinds, '
        'deeper shelves hold books whose spines faintly glow like sealed embers, and at the far end the shelves become sparse, then empty, then there is only a plain blank wall in soft mist. '
        'The bottom fifth of the picture is a calm dark stone floor with a faint reflection of the cyan flames, uncluttered. Symmetric, quiet, a long axis toward the far wall. '
        'No people, no hands, no figures, no animals. ') + NOTEXT,
    'cover_guild': STYLE + MAG + (
        'Landscape picture, aspect ratio 3:2. A design sheet of one closed book, shown twice, side by side with a wide gap: on the left its spine seen straight on (a tall narrow upright strip), '
        'on the right its front cover seen straight on (an upright rectangle about two thirds as wide as tall). Both are the same height and stand upright. '
        'The book is a thick bundle of guild commission slips of slightly different sizes and paper tones, edges uneven and peeking out, bound along the left edge with a thick rough hemp rope '
        'threaded through punched holes and tied in knots. Hard covers of deep indigo-blue board with dark-gold line borders and small brass corner caps. '
        'On the front cover: one round pressed seal of pale grey-white stone (a matte grey impression) and one round seal of copper-bronze with a tiny balance-scale emblem, '
        'a coiled knotted rope drawn as a gold line ornament around a blank empty title cartouche. On the spine: rope knots, a blank cartouche, small brass bands. '
        'Same flat paper-cut style with thin pale outlines. ') + NOTEXT,
    'spines': STYLE + MAG + (
        'Wide landscape picture, aspect ratio 16:9. Exactly nine upright book spines seen straight on, standing in one row, all the same height, evenly spaced with a clear gap between each, '
        'like a design sheet, in this order left to right: '
        '1. pale grey-white stone-coloured cloth spine with thin cyan-teal foil lines and a tiny flame mark at the top. '
        '2. a spine of stitched tanned hide with visible leather thongs, decorated with cold pale silver glowing lines. '
        '3. an iron-plated spine with rivets and dented corner plates, dark iron grey with a strip of deep dull red cloth, smudged with soot. '
        '4. a spine of mounted black stone rubbing paper, black with white rubbed stone grain and white lines, bound with grey cord. '
        '5. a small stout spine of dark navy cloth with brass caps top and bottom and a small round brass emblem. '
        '6. a very old spine that glows like hot metal, deep crimson and molten gold cracks as if still burning inside, sealed with a dark band. '
        '7. another ancient hot spine, ember red-gold, with a heat glow hugging its surface only. '
        '8. a new spine of plain pale ivory cloth with only two faint thin lines, nearly blank. '
        '9. a completely blank pale spine, smooth and empty. '
        'Same flat paper-cut style with thin pale outlines. ') + NOTEXT,
    'paper_slip': (
        'Portrait picture, aspect ratio 2:3. A flat straight-on scan of a single sheet of old guild commission paper filling the whole picture edge to edge, nothing else, no table, no background. '
        'Rough handmade paper, cool ivory to pale grey, faint fibres and paper grain, very faint pale slate-blue printed ruled lines forming an empty form: '
        'a thin header band of small empty boxes along the top, a large empty main box in the middle, a narrow empty band of boxes at the bottom. '
        'A small nail hole near the top edge, slightly soft worn corners, a very faint round ring stain, gentle uneven tone. '
        'Absolutely no text, no letters, no numbers, no stamps, no seals, no signatures. Flat even lighting, no perspective, no shadow. '),
    'bookplate': (
        'Square picture, aspect ratio 1:1. One ex-libris bookplate stamp emblem, centered, filling about two thirds of the picture: inside a narrow round-arched frame drawn with a fine line, '
        'two slender pale grey-white stone pillars stand left and right, and between them hangs a single small floating cyan-teal flame. Below them a thin empty ribbon band. '
        'Clean engraved line-art in cool slate-grey ink on a bone-white oval plate, the flame is the only colour, pale cyan-teal. Flat, symmetric, quiet. ') + MAG + NOTEXT,
}


# 头一回的 spines、cover_guild 画成了立体渲染（书脊像圆柱），跟主画的平涂剪纸不搭，补一版平的
FLAT = ('Flat 2D illustration, NOT a 3D render: no cylinders, no glossy realistic shading, no photographic texture. '
        'Draw everything as flat cut-paper layers with flat colour fills, a soft inner tone or two, and thin pale outlines, like the attached references. ')
JOBS['spines_flat'] = FLAT + JOBS['spines'].replace('Exactly nine upright book spines seen straight on', 'Exactly nine upright book spines seen straight on, each a flat upright rectangle with slightly rounded top and bottom bands')
JOBS['cover_flat'] = FLAT + JOBS['cover_guild']


def refs():
    from PIL import Image
    os.makedirs(os.path.join(OUT, 'ref'), exist_ok=True)
    out = []
    for p in REFSRC:
        dst = os.path.join(OUT, 'ref', os.path.splitext(os.path.basename(p))[0] + '.png')
        if not os.path.exists(dst):
            Image.open(p).convert('RGB').save(dst)
        out.append(dst)
    return out


def gen(names):
    import gpt_gen
    os.makedirs(OUT, exist_ok=True)
    r = refs()

    def job(k):
        use = r if k in ('shelf_main', 'cover_guild', 'spines', 'spines_flat', 'cover_flat') else r[1:]
        try:
            return gpt_gen.gen(os.path.join(OUT, k), JOBS[k], refs=use)
        except Exception as x:
            return '没成：%s' % str(x)[:300]

    with ThreadPoolExecutor(3) as ex:
        for k, res in zip(names, ex.map(job, names)):
            print(k, res, flush=True)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'gen':
        gen(sys.argv[2:] or list(JOBS))
    else:
        print(__doc__ or '用法见文件头')
