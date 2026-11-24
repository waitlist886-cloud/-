#!/usr/bin/env python3
# 大图书馆的图（11-24）：圆厅主画两张、十四间厅廊的书架背景、各厅书脊、各厅封面、十二种纸、借阅卡、青火印、地图室。
# 画风照书架样张（../../样张_书架/tools/gen_shelf.py）：平涂剪纸、浅线描边、灰白石柱、柱间青火，若娜瓦不出场，不画人。
# 走本机 Codex，用 ComfyUI 自带的 python 跑：
#   <ComfyUI 的 python> -X utf8 gen_lib.py gen [名…]     出图（已有的不重出），先用 ~/.codex_b，撞了额度换 ~/.codex，两个都撞了就停
#   <ComfyUI 的 python> -X utf8 gen_lib.py list          列出全部名字
#   <ComfyUI 的 python> -X utf8 gen_lib.py cut [名…]     抠底、切图、转 webp 写进 底稿/门面/共用/assets/lib/
#   <ComfyUI 的 python> -X utf8 gen_lib.py sheet         拼总览图 ../截图/图总览.jpg
# 原图在 底稿/状态栏/comfy/out/大图书馆/（不进库）。要整张重画：把那一张的 png 挪进 旧/ 再 gen。
import os
import re
import sys
import shutil
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', 'comfy'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '图标', 'tools'))
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
OUT = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'out', '大图书馆')
LIB = os.path.join(ROOT, '底稿', '门面', '共用', 'assets', 'lib')
SHOT = os.path.normpath(os.path.join(HERE, '..', '截图'))
SAMPLE = os.path.join(ROOT, 'out', '门面第二轮', '书架')
REFSRC = {
    'front': os.path.join(SAMPLE, 'ref', 'maze_front.png'),
    'guild': os.path.join(SAMPLE, 'ref', 'maze_guild.png'),
    'shelf': os.path.join(SAMPLE, 'shelf_main.png'),
    'spines': os.path.join(SAMPLE, 'spines_flat.png'),
}
HOMES = ['C:/Users/waitl/.codex_b', 'C:/Users/waitl/.codex']

STYLE = ('Art style exactly like the attached reference pictures: a flat layered paper-cut illustration, smooth flat colour planes stacked like cut paper, '
         'thin soft pale outlines, big sweeping curves, fine paper grain, calm and solemn fairy-tale mood, Japanese fantasy RPG title-screen quality. '
         'Palette: deep indigo, slate blue, cool grey and bone-white stone. ')
FIRE = ('The only bright, saturated colour is a pale cyan-teal flame (ghost fire, blue-green, never orange): small flames float in the air by themselves between the pillars, '
        'no lamp, no holder, no chain, casting cool cyan light on the stone. ')
NOPEOPLE = 'No people, no faces, no hands, no figures, no statues of people, no animals. '
MAG = ('The background is one flat, solid, pure magenta colour (#FF00FF) filling the whole picture edge to edge: no gradient, no texture, no vignette, no cast shadow. '
       'The objects contain no magenta, pink or purple-red. ')
NOTEXT = 'No text, no letters, no numbers, no runes that look like writing, no signature, no watermark. '
FLAT = ('Flat 2D illustration, NOT a 3D render: no cylinders, no round glossy shading, no photographic texture. '
        'Draw everything as flat cut-paper layers with flat colour fills, a soft inner tone or two, and thin pale outlines. ')
ROOM = ('The library is the hall of a silent goddess of records: tall pale grey-white stone pillars and round arches, and between the pillars small cyan-teal flames float. ')
CALM = ('Composition: a straight-on, symmetric view into the room. The middle band of the picture, from about 35% to 80% of the height and across the central 70% of the width, '
        'is a calm, softly lit, uncluttered wall of plain shelving in shadow so that a row of book spines can be laid over it later; keep detail and contrast low there. '
        'The richest detail lives at the left and right edges and in the upper vaulting. The bottom tenth is a plain dark stone floor. ')

# 各厅：书架背景里有什么、四种书脊、封面、纸
HALLS = {
    'yuan': dict(
        wing='The curved wall of the great round hall, lined with bone-white stone shelves that follow the curve. Big books bound in pale stone-coloured cloth and white boards, '
             'a few laid flat with a tiny cyan flame mark on their spines. Above, a ring of tall arches. Quiet, clean, cool, the most orderly room of all.',
        spines=['tall pale grey-white stone-coloured cloth spine, thin cyan-teal foil lines and a tiny flame mark near the top, otherwise blank',
                'a small stout spine of blue-grey cloth with thin brass caps top and bottom and a small round compass emblem',
                'a thin spine whose upper half is tanned hide painted with faint silvery lines and lower half is rough grey paper, joined by an evenly twisted cord',
                'a spine of two plain white wooden boards sewn together with hemp string, the boards slightly uneven'],
        cover='a front cover of pale grey-white stone-coloured cloth, cool to the eye, a thin cyan-teal foil border, and in the centre one small cyan flame between two slender stone pillars, '
              'above a blank empty title cartouche framed by a thin line',
    ),
    'ming': dict(
        wing='A hall of weapon manuals and battle diagrams. Wide shelves of huge folio atlases lying flat and leaning, iron-bound fighting manuals, a few long racks of spears and swords on the side walls, '
             'framed pale drawing plates of fencing stances drawn only as circles, arcs and arrows (no human figures), and rolled diagrams in cases.',
        spines=['a thick white-stone coloured hard spine with a small embossed white kite bird with folded wings near the top and two thin gold bands',
                'a spine made of thin hammered iron sheets threaded on bronze-green rings, with a strip that looks like a flattened old sword blade',
                'a very tall folio spine of brown ox leather with bronze-green corner caps and a pressed round seal',
                'a black obsidian-coloured hard board spine with one steel clasp and a small engraved number plate (blank)'],
        cover='a front cover of white-stone coloured hard board, embossed in pale relief: seven crossed swords fanning around a centre, four small beasts in the four corners drawn as simple emblems, '
              'a thin gold line border and a blank title cartouche',
    ),
    'shen': dict(
        wing='The hall of gods and demon gods. Tall dark slate shelves reaching up into the vault, holding long deerskin scrolls in rows of pigeonholes with bronze end caps, '
             'black stone-like books, and thin lines of cyan-teal fire that hang in the air like written strokes (abstract wavy lines, not letters). '
             'Seven tall pillars in a row, each crowned with a different simple emblem (a feather, a mountain, an open page, a ring of years, a boundary stone, a scale, a shield). Solemn and vast.',
        spines=['a black stone-looking spine with no title and one thin vertical line of cyan-teal fire running down it',
                'a white lambskin spine without gold, with one tiny round holy seal pressed near the top',
                'a grey cloth hard spine with thin iron plates on the corners, like an evidence box',
                'a rolled deerskin scroll standing upright, bronze caps at both ends engraved with a small mark'],
        cover='a front cover that looks like a slab of black stone but is paper, no title, a single thin line of cyan-teal fire running from top to bottom, '
              'and seven tiny pale emblems in a ring around it',
    ),
    'moon': dict(
        wing='The corridor of the age of beasts and bonfires. Rough grey stone and dark timber shelves holding bundles of tanned beast-hide scrolls tied with thongs, '
             'books bound in hide with the fur still at the edges, great beast horns and a huge pale skull of an ancient beast mounted high on the wall, '
             'faint silver dust glittering on the hides. Wild and ancient but quiet.',
        spines=['a spine of stitched tanned hide with visible leather thongs, decorated with cold pale silver glowing lines',
                'a spine of pale wolf hide with a strip of grey fur along one edge and a silver-painted beast claw mark',
                'a white lambskin spine with one ring-shaped silver band embossed near the top',
                'a deep blue star-chart book spine with thin copper corner caps and silver thread stitching'],
        cover='a front cover of tanned beast hide with uneven fur-trimmed edges, stitched with leather thongs, painted in glowing pale silver powder: '
              'a great beast curled around a small flame, and a blank space for a title',
    ),
    'strife': dict(
        wing='The corridor of the long war wall. Grim grey stone like the inside of a fortress wall, narrow arrow slits high up, iron-bound chests and crates of war reports, '
             'stacks of thick report bundles tied with cord, a torn and faded dull-red banner hanging (no emblem text), dented shields leaning on the side. Heavy and solemn.',
        spines=['an iron-plated spine with rivets and dented corner plates, dark iron grey with a strip of deep dull red cloth, smudged with soot',
                'a small worn account-book spine of soft dark leather, the corners rubbed round, a strap',
                'a bundle of reed paper sheets bound with a leather cord, a small dull brass horn hanging from the cord',
                'a long grey cloth album spine, plain, with no title and a dark iron band'],
        cover='a front cover clad in dark iron plates with rivets, dented corner plates, soot smudges, a strip of deep dull red cloth across it, '
              'and a small blank iron title plate',
    ),
    'bronze': dict(
        wing='The corridor of stone rubbings. Huge black rubbings of carved steles hang like tapestries from the arches, black with the white grain of stone and abstract carved reliefs '
             '(a sword, a sheaf of wheat, a wheel, a crown, no letters), stone tablets lean on the side walls, shelves of rubbing albums bound with grey cord. '
             'Accents of old bronze-green metal.',
        # 头一回四种都画成了蓝灰布面，看不出碑拓；11-24 整张重画，前两种写死黑底白纹
        spines=['a spine made of a black ink stone rubbing: almost pure black paper with mottled white rubbed stone grain, chisel marks and a thin white border, bound with grey cord, NOT blue',
                'another black rubbing album spine: black ground with white rubbed relief of a wheat ear, old bronze-green metal caps top and bottom',
                'a spine of two hard wooden boards with an iron clasp and one old rusty nail driven through',
                'a grey paper spine sewn with hemp, with one pressed clay seal of an open hand'],
        cover='a front cover that is a mounted black stone rubbing: black ground, white rubbed stone grain, a carved relief of a sword standing in a sheaf of wheat, '
              'framed with old bronze-green metal corners, a blank rubbed panel for the title',
    ),
    'maze': dict(
        wing='The corridor of the adventurers guild archive. Walls of wooden pigeonholes stuffed with rolled and folded commission slips, old wooden crates branded with a small balance-scale mark, '
             'a big notice board with many blank paper slips pinned on it, coils of rope, a hanging lantern holding a cyan-teal flame, '
             'ledgers bound with rough hemp rope. Busy but tidy.',
        spines=['a spine of a thick bundle of commission slips bound with a rough hemp rope tied in knots, deep indigo board with brass bands',
                'a small stout spine of dark navy cloth with brass caps top and bottom and a small round brass emblem',
                'a spine made of an old crate board with a branded small balance-scale mark',
                'a very narrow tall spine of pale paper with a blue edge stripe, like a register of names'],
        cover=None,   # 用样张那一张公会委托存档的封面（用户看过）
    ),
    'arcane': dict(
        wing='The hall of arcane art and engineering. Shelves of grey-blue bound reports and boxed folios, framed engraved technical plates on the walls drawn only with lines, circles and gears, '
             'a big armillary model of orbit rings, brass pipes and gauges running along the pillars, a heavy typewriter on a desk at the side, '
             'small crystals glowing cyan-teal inside glass. Precise and orderly.',
        spines=['a grey-blue thick paper spine with two bronze rivets and one thin white line',
                'a grey cloth folio box spine embossed with thin orbit rings',
                'a spine whose cover is an old copper nameplate riveted on dark board',
                'a bundle of typewritten sheets bound with plain string between two thin card boards'],
        cover='a front cover of grey cloth, embossed with thin concentric orbit rings crossed by a gear and a pair of compasses, a single white line border, a blank title cartouche',
    ),
    'crown': dict(
        wing='The hall of the star-crown cathedral. White stone, tall narrow pale windows of plain frosted glass, gold leaf on the arches, '
             'a lectern holding a large open illuminated book with gold borders and blank pages, shelves of white vellum books with gilt edges. '
             'Pure, high, bright pale gold and white, the cyan flames floating between the pillars.',
        spines=['a white lambskin spine richly tooled in gold with a small seven-pointed star crown',
                'a white spine whose page edges are dyed in seven bands of colour (white, wheat yellow, teal, iron grey, deep blue, soft red, black)',
                'a small palm-sized spine of waxed cloth with a leather loop to hang at the belt',
                'a narrow tall spine of waxed paper with a thin gold edge'],
        cover='a front cover of white vellum illuminated in gold: a crown made of seven stars with fine rays, a gold leaf vine border, a blank gold-framed title cartouche',
    ),
    'craft': dict(
        wing='The corridor of the songs of trades. Warm-feeling but still cool-coloured guild workshop shelves among tools of trades: '
             'rolls of birch bark tied in bundles hanging from pegs, an anvil and tongs, a loom shuttle, a fishing net, coils of rope and chain, a carpenters plane, '
             'small notebooks stacked in baskets. Lived-in and humble.',
        spines=['a bundle of birch bark rolls tied with a deer-hide cord',
                'a narrow spine of two thin wooden boards with an old chain link as a clasp',
                'a small undyed grey cloth booklet spine',
                'an oilcloth notebook spine with a few small scorch marks'],
        cover='a front cover of birch bark with a deer-hide cord, branded with a small emblem of a hammer, a shuttle and a coiled rope, a blank title space',
    ),
    'child': dict(
        wing='The childrens shelf. A low, soft corner: a low wooden shelf with picture books standing face out (their covers are simple pictures, no text), '
             'round cushions on the floor, carved wooden toy animals, a small wooden toy well and a toy dragon made of cloth, paper stars hanging on strings. '
             'Gentle, soft muted pastel colours, still the same cool palette.',
        spines=['a thick square board-book spine with rounded corners, muted pastel teal',
                'a stout board-book spine with small iron corner caps, pale ochre',
                'a thin booklet spine of ruled ledger paper with a red thread binding',
                'a bundle of typewritten story sheets bound with hemp, with a small woodcut picture on the spine'],
        cover='a front cover of a thick picture book with rounded corners: a simple woodcut-style picture of a small well with a tiny cyan flame above it and stars around, '
              'muted pastel colours, a blank title band',
    ),
    'stage': dict(
        # 头一回的幕布是饱和的大红、挂着木偶人，跟“火是唯一的暖色”和不画人相冲，11-24 整张重画
        wing='The corridor of the stage and storytellers. The backstage of a small theatre: heavy velvet curtains in deep muted indigo-plum (dark, desaturated, not red) drawn aside with pale silver tassels, '
             'stacks of scripts tied with string, flat cut-paper shadow-puppet silhouettes of a dragon, a castle and a ship pinned on a pale screen, '
             'playbills pasted on a pillar in faded slate blue, grey and pale gold (only colour blocks and simple pictures, no text), '
             'a painted backdrop of mountains rolled up, a small toy stage. No puppets shaped like people. Lively but hushed, same cool palette as the rest of the library.',
        spines=['a deep red calfskin spine pressed with gold and brass corner caps',
                'a spine of two linden-wood boards bound with hemp, uneven sizes',
                'a small palm-sized chapbook spine of rough straw paper with a red and green woodcut band',
                'a slim box spine for a deck of printed cards, four-colour printed stripes slightly misregistered'],
        cover='a front cover of deep dusky red calfskin pressed with gold: a little stage with drawn-back curtains framing a blank title space, brass corner caps',
    ),
    'past': dict(
        wing='The corridor of the earlier ages, too old to be read. Very dark ancient shelves of black stone; every book glows faintly from inside like metal still hot from the forge, '
             'dim ember red-gold heat shimmer hugging the spines only, the air above them faintly wavering. '
             'The books are of strange materials: bark, silk thread, eggshell white, pure gold, white stone, straw, frost crystal, scorched hide. Deep, hushed, forbidden.',
        spines=['an ancient spine of tree bark with branches still on it, glowing ember red-gold from inside through cracks',
                'an ancient spine of pure gold, glowing hot, sealed with a dark band',
                'an ancient spine of smooth eggshell white with a hot red-gold glow hugging its edges',
                'an ancient spine of scorched black hide with molten gold cracks as if still burning inside'],
        cover='a front cover of an ancient book that glows like hot metal: deep crimson with molten gold cracks, sealed by a dark band with a round seal, no title',
    ),
    'future': dict(
        wing='The corridor of the ages not yet written. A long corridor going far into soft pale mist; the near shelves hold books bound in new white tanned hide with faint gold, '
             'deeper shelves hold fewer and paler books, then they are almost blank, and at the far end there is one empty shelf slot and a plain blank wall in mist. '
             'Light, quiet, endless.',
        spines=['a new white tanned hide spine with thin gold lines',
                'a whiter new hide spine with only very faint gold lines',
                'an almost blank white hide spine with one faint thin line',
                'a completely blank pale white spine, smooth and empty'],
        cover='a front cover of new white tanned hide, almost blank, with a very faint thin gold border fading away at the bottom and a blank title space',
    ),
}

PAPERS = {
    'hide': 'a sheet of tanned beast hide used as writing skin: warm pale ochre-grey, uneven tone, faint pores and creases, soft scraped surface, faint glitter of pale silver dust',
    'annal': 'a sheet of fine pale white chronicle paper, smooth, very faint fibres, slightly cool white, clean, a hint of aged tone',
    'report': 'a sheet of rough grey war-report paper, coarse fibres, faint charcoal smudges and soot, a faint water stain, worn',
    'rubbing': 'a black stone rubbing: deep black ground with soft white rubbed stone grain, tiny pits and chisel marks, like ink rubbed over a stone surface, no carved letters',
    'ledger': 'a sheet of ledger paper: pale cream-grey paper with a regular grid of very faint pale slate-blue ruled lines, evenly spaced squares',
    'form': 'a sheet of guild commission paper: rough handmade paper, cool ivory to pale grey, faint fibres, gentle uneven tone, nothing printed',
    'print': 'a sheet of smooth machine-made printing paper, pale cool off-white with a very faint even grain, crisp and clean',
    'bone': 'a sheet of very thin bone-white paper, almost translucent, faint long fibres, cool white with the faintest blue-grey tint',
    'vellum': 'a sheet of fine vellum parchment: warm pale cream with soft mottling and faint veins of the skin, a few tiny flecks of gold leaf',
    'type': 'a sheet of thin typewriter paper, pale cool white-grey, smooth, very faint fibres, slightly translucent',
    'kid': 'a sheet of thick soft card paper for a picture book, pale warm white with a soft felt-like texture and tiny coloured fibres',
    # 头一回出成了橙黄，11-24 整张重画，写明很浅
    'bill': 'a sheet of cheap playbill paper: very pale cool ivory-grey paper (light, low saturation, not yellow, not orange) with sparse faint misregistered specks of pale red and pale blue ink',
}

JOBS = {}
JOBS['hall_pc'] = STYLE + FIRE + ROOM + (
    'Wide landscape picture, aspect ratio 16:9. The inside of a vast round hall seen from the entrance, slightly from above. All around the circular wall stands a ring of tall round-arched doorways '
    '(about eleven visible, evenly spaced, each a dark opening leading to a corridor of bookshelves, each with a blank stone plaque above it), separated by tall pale grey-white stone pillars, '
    'and between every pair of pillars one small cyan-teal flame floats in the air. Above, a great shallow dome with concentric rings of coffers and a round open oculus with soft cool light. '
    'In the exact centre of the floor stands one long stone table, and on it lies one huge open book with bone-white pages (blank, no writing), a small cyan flame floating above it. '
    'At one corner of the table lies a small borrowing card. The floor is pale stone laid in concentric rings around the table, with a faint reflection of the cyan flames. '
    'Symmetric, quiet, immense. ') + NOPEOPLE + NOTEXT
JOBS['hall_m'] = STYLE + FIRE + ROOM + (
    'Tall portrait picture, aspect ratio 9:16. The inside of a vast round hall seen from the floor looking forward and up: in the lower third, one long stone table with one huge open book '
    'with bone-white blank pages and a small cyan flame floating above it; behind and above it, the circular wall rises in tiers of round-arched doorways, '
    'each tier a ring of tall arches separated by pale grey-white stone pillars with small cyan-teal flames floating between them, and at the very top a great dome with a round open oculus '
    'with soft cool light. Symmetric, quiet, immense. ') + NOPEOPLE + NOTEXT
JOBS['maproom'] = STYLE + FIRE + ROOM + (
    'Wide landscape picture, aspect ratio 16:9. A round map room off the great hall: under a low dome, one large round stone table in the centre with a big unrolled map of two continents '
    'and seas (drawn only as coastlines, mountains and rivers, no lettering), held flat by small stones; around it on the walls, four more great maps hang between the pillars, '
    'each a different tint (silvery blue, iron grey, bronze-green, indigo), with drawn coastlines only. Brass dividers and a compass rose on the table. ') + NOPEOPLE + NOTEXT
for k, h in HALLS.items():
    JOBS['wing_' + k] = STYLE + FIRE + ROOM + 'Wide landscape picture, aspect ratio 16:9. ' + h['wing'] + ' ' + CALM + NOPEOPLE + NOTEXT
    JOBS['spines_' + k] = FLAT + STYLE + MAG + (
        'Wide landscape picture, aspect ratio 16:9. Exactly four upright book spines seen straight on, standing in one row, all the same height (about 85% of the picture height), '
        'each a flat upright rectangle with slightly rounded top and bottom bands, different thicknesses, evenly spaced with a wide clear gap between each, like a design sheet, '
        'in this order left to right: ' + ' '.join('%d. %s.' % (i + 1, s) for i, s in enumerate(h['spines'])) +
        ' Spines have no title text: leave a plain blank band in the middle of each spine. Same flat paper-cut style with thin pale outlines. ') + NOTEXT
    if h['cover']:
        JOBS['cover_' + k] = FLAT + STYLE + MAG + (
            'Portrait picture, aspect ratio 2:3. One closed book seen straight on from the front, upright and centred, filling about 85% of the picture height: ' + h['cover'] + '. '
            'Flat, symmetric, the whole cover visible with a little magenta around it. ') + NOTEXT
for k, p in PAPERS.items():
    JOBS['paper_' + k] = (
        'Square picture, aspect ratio 1:1. A flat straight-on scan of ' + p + ', filling the whole picture edge to edge, nothing else: no table, no background, no edges of the sheet, no objects. '
        'An even, seamless, uniform texture with no single big feature, suitable to repeat as a tile. Flat even lighting, no perspective, no shadow, no vignette. ') + NOTEXT
JOBS['card'] = FLAT + STYLE + MAG + (
    'Portrait picture, aspect ratio 2:3. One old library borrowing card seen straight on, centred, filling about 80% of the picture: a slightly yellowed bone-white card, '
    'a thin header band at the top, then many evenly spaced pale slate-blue ruled lines across it with one thin vertical column line, the last line empty, '
    'a small cyan-teal stamp of two pillars and a flame in the top corner, slightly worn soft corners. ') + NOTEXT
JOBS['seal'] = FLAT + STYLE + MAG + (
    'Square picture, aspect ratio 1:1. One round wax seal pressed on a short torn strip of bone-white paper tape, seen straight on, centred: the wax is pale cyan-teal and glows softly like a cold flame, '
    'its impression shows two slender pillars with a small flame between them, the wax edge rough and drippy. ') + NOTEXT


def refs_for(name):
    from PIL import Image
    os.makedirs(os.path.join(OUT, 'ref'), exist_ok=True)
    keys = (['front', 'shelf'] if name.startswith(('wing_', 'hall_', 'maproom')) else
            ['guild', 'spines'] if name.startswith('spines_') else
            ['guild'] if name.startswith(('cover_', 'card', 'seal')) else [])
    out = []
    for k in keys:
        dst = os.path.join(OUT, 'ref', k + '.png')
        if not os.path.exists(dst):
            Image.open(REFSRC[k]).convert('RGB').save(dst)
        out.append(dst)
    return out


STOP = []


def hit_limit(log):
    try:
        t = open(log, encoding='utf-8', errors='replace').read().lower()
    except OSError:
        return False
    return 'usage_limit' in t or 'usage limit' in t or ' 429' in t


def gen(names):
    import gpt_gen
    os.makedirs(OUT, exist_ok=True)
    home = [0]

    def job(k):
        stem = os.path.join(OUT, k)
        if os.path.exists(stem + '.png'):
            return 'had'
        while home[0] < len(HOMES):
            h = HOMES[home[0]]
            try:
                return gpt_gen.gen(stem, JOBS[k], refs=refs_for(k), home=h)
            except Exception as x:
                if hit_limit(stem + '.log'):
                    if home[0] < len(HOMES) and HOMES[home[0]] == h:
                        print('== %s 撞了额度，换号' % h, flush=True)
                        home[0] += 1
                    continue
                return '没成：%s' % str(x)[:300]
        STOP.append(k)
        return '两个号都撞了额度，没开'

    with ThreadPoolExecutor(3) as ex:
        for k, res in zip(names, ex.map(job, names)):
            print(k, res, flush=True)


# ---------- 抠图、切图 ----------

def save(im, name, h=None, w=None, q=84):
    from PIL import Image
    if h and im.height != h:
        im = im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)
    if w and im.width != w:
        im = im.resize((w, max(1, round(im.height * w / im.width))), Image.LANCZOS)
    os.makedirs(LIB, exist_ok=True)
    p = os.path.join(LIB, name + '.webp')
    im.save(p, 'WEBP', quality=q, method=6)
    print(name, im.size, os.path.getsize(p) // 1024, 'KB')
    return p


def save_under(im, name, w, limit_kb, q=82):
    """主画、书架背景：压到 limit_kb 以内。"""
    from PIL import Image
    im = im.convert('RGB')
    if im.width != w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    os.makedirs(LIB, exist_ok=True)
    p = os.path.join(LIB, name + '.webp')
    while True:
        im.save(p, 'WEBP', quality=q, method=6)
        if os.path.getsize(p) <= limit_kb * 1024 or q <= 50:
            break
        q -= 4
    print(name, im.size, 'q%d' % q, os.path.getsize(p) // 1024, 'KB')


def parts(im, minpx=4000):
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    a = np.array(im)[..., 3] > 40
    lab, n = ndimage.label(ndimage.binary_dilation(a, iterations=4))
    sizes = ndimage.sum_labels(np.ones_like(lab), lab, index=range(1, n + 1))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        if sizes[i] < minpx:
            continue
        m = (lab[sl] == i + 1)
        c = np.array(im.crop((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)))
        c[..., 3] = np.where(m, c[..., 3], 0)
        out.append((sl[1].start, Image.fromarray(c, 'RGBA')))
    return [c for x, c in sorted(out, key=lambda t: t[0])]


def tile(img, size=640, mode='blend'):
    """纸做成能平铺的：blend 是跟错开半张的自己交叉淡入（四边接得上），mirror 是镜像拼四块（带格子线的纸用）。"""
    import numpy as np
    from PIL import Image, ImageOps
    im = img.convert('RGB')
    s = min(im.size)
    im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width - s) // 2 + s, (im.height - s) // 2 + s))
    if mode == 'mirror':
        half = im.resize((size // 2, size // 2), Image.LANCZOS)
        out = Image.new('RGB', (size, size))
        out.paste(half, (0, 0))
        out.paste(ImageOps.mirror(half), (size // 2, 0))
        out.paste(ImageOps.flip(half), (0, size // 2))
        out.paste(ImageOps.flip(ImageOps.mirror(half)), (size // 2, size // 2))
        return out
    a = np.array(im.resize((size, size), Image.LANCZOS)).astype(float)
    r = np.roll(np.roll(a, size // 2, 0), size // 2, 1)
    t = np.linspace(0, 1, size)
    w1 = np.clip(np.sin(np.pi * t) * 1.6, 0, 1)
    w = np.outer(w1, w1)[..., None]
    return Image.fromarray(np.clip(a * w + r * (1 - w), 0, 255).astype('uint8'))


MIRROR = {'ledger'}


def cut(names):
    from PIL import Image
    from gpt_generic import key
    have = lambda n: os.path.exists(os.path.join(OUT, n + '.png'))
    todo = names or [n for n in JOBS if have(n)] + ['cover_maze', 'plate']
    for n in todo:
        src = os.path.join(OUT, n + '.png')
        if n == 'cover_maze':   # 样张那一张公会委托存档的封面
            pc = parts(key(os.path.join(SAMPLE, 'cover_flat.png')))
            save(pc[-1], 'cover_maze', h=900)
            continue
        if n == 'plate':        # 样张那一张藏书票（用户看过）
            bp = key(os.path.join(SAMPLE, 'bookplate.png'))
            bb = bp.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
            save(bp.crop(bb), 'plate', h=640)
            continue
        if not have(n):
            print(n, '没有原图')
            continue
        if n == 'hall_pc' or n == 'maproom' or n.startswith('wing_'):
            save_under(Image.open(src), n, 1920 if n == 'hall_pc' else 1600, 480 if n == 'hall_pc' else 300)
        elif n == 'hall_m':
            save_under(Image.open(src), n, 1080, 400)
        elif n.startswith('spines_'):
            k = n[len('spines_'):]
            ps = parts(key(src))
            print(n, '切出', len(ps), '块')
            for i, c in enumerate(ps[:4]):
                save(c, 'spine_%s_%d' % (k, i + 1), h=720, q=86)
        elif n.startswith('cover_') or n in ('card', 'seal'):
            im = key(src)
            bb = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
            im = im.crop(bb)
            save(im, n, h=900 if n.startswith('cover_') else (700 if n == 'card' else 400), q=76 if n.startswith('cover_') else 84)
        elif n.startswith('paper_'):
            k = n[len('paper_'):]
            save(tile(Image.open(src), 640, 'mirror' if k in MIRROR else 'blend'), n, q=78)


def sheet():
    """总览：主画两张、地图室、各厅书架背景，书脊、封面、纸、借阅卡、印，一张大图。"""
    from PIL import Image, ImageDraw
    files = sorted(os.listdir(LIB))
    def L(n):
        p = os.path.join(LIB, n + '.webp')
        return Image.open(p).convert('RGBA') if os.path.exists(p) else None
    W = 2400
    rows = []
    # 第一行：hall_pc + hall_m
    a, b = L('hall_pc'), L('hall_m')
    rows.append([x for x in (a, b, L('maproom')) if x])
    wings = [L('wing_' + k) for k in HALLS]
    wings = [x for x in wings if x]
    for i in range(0, len(wings), 7):
        rows.append(wings[i:i + 7])
    sp = [L(f[:-5]) for f in files if f.startswith('spine_')]
    for i in range(0, len(sp), 14):
        rows.append(sp[i:i + 14])
    cv = [L(f[:-5]) for f in files if f.startswith('cover_')] + [x for x in (L('card'), L('plate'), L('seal')) if x]
    for i in range(0, len(cv), 9):
        rows.append(cv[i:i + 9])
    pp = [L(f[:-5]) for f in files if f.startswith('paper_')]
    if pp:
        rows.append(pp)
    gap = 12
    imgs = []
    for r in rows:
        if not r:
            continue
        hs = [x.height for x in r]
        # 一行等高，总宽 W
        h0 = 1000
        ws = [x.width * h0 / x.height for x in r]
        scale = (W - gap * (len(r) - 1)) / sum(ws)
        h = round(h0 * scale)
        line = Image.new('RGBA', (W, h), (24, 26, 40, 255))
        x0 = 0
        for x, w in zip(r, ws):
            ww = round(w * scale)
            t = x.resize((max(1, ww), h), Image.LANCZOS)
            line.alpha_composite(t, (x0, 0))
            x0 += ww + gap
        imgs.append(line)
    H = sum(i.height for i in imgs) + gap * (len(imgs) + 1)
    out = Image.new('RGB', (W + 2 * gap, H), (24, 26, 40))
    y = gap
    for i in imgs:
        out.paste(i.convert('RGB'), (gap, y))
        y += i.height + gap
    os.makedirs(SHOT, exist_ok=True)
    p = os.path.join(SHOT, '图总览.jpg')
    if out.height > 4600:
        out = out.resize((round(out.width * 4600 / out.height), 4600), Image.LANCZOS)
    out.save(p, 'JPEG', quality=74)
    print(p, out.size, os.path.getsize(p) // 1024, 'KB')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'gen':
        gen(sys.argv[2:] or list(JOBS))
    elif cmd == 'list':
        print(' '.join(JOBS))
    elif cmd == 'cut':
        cut(sys.argv[2:])
    elif cmd == 'sheet':
        sheet()
    elif cmd == 'show':
        print(JOBS[sys.argv[2]])
    else:
        print('用法见文件头')
