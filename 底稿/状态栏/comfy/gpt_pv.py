#!/usr/bin/env python3
# 照用户 11-03 发的原神 PV 截图的画法出两扇（GPT 加风格参考）。python gpt_pv.py [名字…]，写 out/四方_11-03/pv/，已有的不重出。
# 风格参考放在 语料/风格参考_11-03/（米哈游的图，不进仓库），只学画法，不学里面的人和东西；提示词里不要月相（参考图里有）。
# 参考图一次最多五张。要透明底就在提示词里写 transparent background，出来是 RGBA。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_gen

OUT = os.path.join(HERE, 'out', '四方_11-03', 'pv')
S = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '语料', '风格参考_11-03')
REFS = os.path.join(HERE, 'out', '四方_11-03', '外部试图')
GUIDE_F, SHEET_F = os.path.join(OUT, '_guide_fusion.png'), os.path.join(OUT, '_sheet_fusion.png')
GIANT, MECH, CHALK, FACE = [os.path.join(S, n) for n in ('pv_giant.png', 'pv_mech.png', 'pv_chalk.png', 'pv_face.png')]

STYLE = ('Draw it the way the style reference images are drawn: a high-end animated storybook sequence from a Japanese fantasy game, like a paper theatre lit from behind. '
         'Monumental, simplified figures built from large flat cut-paper shapes with crisp, confident silhouettes, overlapping in clear layers. '
         'Hair and cloth are huge sweeping ribbon shapes and long calligraphic curves; wings and flames are big graphic strokes. '
         'Inside the flat colour areas: fine parallel hatching, engraved line texture and dry-brush chalk grain, like gouache and linocut printing; edges of the light shapes break into chalky dry-brush. '
         'Thin pale or coloured outlines, not black. A limited palette, with soft coloured light washing across the layers, and large plain luminous discs behind the figures. '
         'Big calm empty areas, far fewer small details than a normal anime illustration. A few small four-pointed stars are fine. '
         'Do not use: glossy anime key-art shading, realistic metal, sparkles everywhere, floating gold dust, busy ornament, 3D look, western cartoon proportions, thick black outlines, text, logo, frame, crescents, moon phases.')
ROLES3 = 'The attached images are style references only: copy how they are drawn, and do not copy their characters, objects or scenes. '
SIZE_L = 'Tall portrait picture, aspect ratio 2:3. Keep the main shapes in the right two thirds of the picture, and keep the top tenth of the picture as plain dark sky. '
TRAVELER = 'At the lower right, a small cloaked traveler seen from behind stands on a floating rock, cape blowing, raising a staff with a small light toward the right. '
FLOOR = 'Along the very bottom edge, a dark band of silhouetted grass and dark flowers with a few small glowing white flowers. '

# 右扇融合（用户 11-03：图一 right_pv 的姿势和构图，图二 right_a 的五官和元素神）
FUSE = ('Image 1 is the layout: repaint it as a tall portrait picture with aspect ratio 7:10, keeping every figure exactly where it is in image 1, at the same size, in the same pose and facing the same way, with the same position of every arm, hand, weapon and wing, and the same big ribbons flowing away to the right. The plain flat dark strip along the right side of image 1 is unpainted: continue the deep indigo night sky, the long ribbons and a few soft clouds across it, with no new figures. '
        'Images 2 and 3 show what the characters look like: image 3 is a sheet of enlarged close-ups taken from image 2. Give each figure in the layout the face, eyes, hair, costume and attributes that the same character has in images 2 and 3, completely replacing the simplified closed-eye faces of image 1. Faces are fine, delicate anime faces with clean lines, with the same eye shape, lashes, small nose and small mouth as in image 3. '
        'The archer has long pale gold hair, a small gold leaf circlet, a white dress, huge white feathered wings and a gold bow. '
        'The god behind her has a head and body of faceted grey-violet stone, spiky stone hair, a round gold clasp on his chest and wings of layered faceted rock, exactly as in image 2, and he does not wear a robe. '
        'The duke has long flowing red hair, a high black and crimson collar, a black gloved hand on a golden sun staff, one wing of red and orange flame and one wing of faceted blue ice crystals. '
        'The blonde goddess has a large pale flower in her long blonde hair, a small black cat on her shoulder and a white and gold dress. '
        'The small goddess has honey-brown hair with pale flowers, small branching antlers and a white and green dress, and holds wheat. '
        'The healer has short curly green hair, small white wings at her temple and a green and white cape with a gold star; her hands stay as in image 1. '
        'The man wears a white hood and robe, with short light-brown hair showing. '
        'The crowned queen has rich auburn hair in a large braided bun with long side locks, a tall spiked gold crown, amber eyes, a thin scar across one eye, a white and gold high collar and gold armor; her black gloved arm and her long sword stay exactly as in image 1. '
        'The silver-haired queen has very long silver hair with a braid across her head, a large black bow, a pointed ear, a small red mark on her forehead, amber eyes, long earrings, a crimson and black high collar closed at the neck, a gold star and gold chains; she keeps her red crystal scepter, but her hand holding it must be visible, and it must stand clear of the other queen\'s crown. '
        'Rendering: the same drawing style as images 1 and 2. Flat cut-paper shapes with smooth colour, fine parallel hatching and dry-brush chalk grain inside the colour areas, thin pale or coloured outlines, matte. No glossy shading, no sparkles, no floating gold dust, no 3D look, no black outlines, no text, no logo, no frame, no crescents, no moon phases.')

JOBS = {
    # 右扇：构图照 GPT 中间版（设定最对），双王的长相照用户的图。这张传了六张，工具只收最后五张，构图稿多半没进去，出来的构图也确实不一样；gpt_gen 现在超过五张直接报错，要重出得先删一张
    'right_a': ([os.path.join(HERE, 'out', '四方_11-03', 'gpt_mid', 'right.png'), os.path.join(REFS, '参考_巴尔缇娜.png'), os.path.join(REFS, '参考_索恩薇娅.png'), GIANT, MECH, FACE],
                'Image 1 is the composition guide: redraw it completely in a new style as a tall portrait picture with aspect ratio 1:2, keeping every figure in the same place and the same pose, all turned to the left. Keep who each figure is: the winged goddess drawing a bow with large white wings, the half-stone god with rock wings, the red-haired duke with wings of flame and frost and a sun staff, the blonde goddess with a small black cat on her shoulder, the small goddess with fawn antlers holding wheat, the green-haired healer with tiny head wings, the calm man in a plain undyed hood. '
                'Images 2 and 3 show who the two queens in front are: copy their faces, hair and costume design, not their rendering. The silver-haired queen has a large black bow, pointed ears, a small red mark on her forehead and a closed high collar; the crowned queen has a braided bun and a scar across one eye. '
                'Images 4, 5 and 6 are style references only: copy how they are drawn, and do not copy their characters, objects or scenes. Faces are clean side profiles with very few features, drawn as in image 6. Deep indigo night behind everyone with one or two large pale luminous discs. ' + STYLE),
    # 左扇三种意象，都是大迷宫，不是一座真的城
    'left_a': ([CHALK, GIANT, MECH],
               ROLES3 + SIZE_L + 'Subject: the Great Labyrinth as a symbol, not a real place. A colossal faceless shadow, one huge flat silhouette of deep violet and indigo with no facial features at all, looms behind everything in side profile facing right, its long veil falling in sweeping ribbons, one enormous clawed hand of flat shapes reaching toward the right edge. A black sun floats before it: a plain black disc with a pale gold dry-brush halo. The veil ribbons coil down into a vast spiral abyss: ring after ring of pale stone arcades drawn as simple paper strips with tiny arches, turning inward and falling into a star-flecked darkness. One thin gold ribbon of stairs winds down through the rings. ' + TRAVELER + FLOOR + STYLE),
    'left_b': ([CHALK, GIANT, MECH],
               ROLES3 + SIZE_L + 'Subject: the Great Labyrinth as a symbol, not a real place. A huge ring hangs in a deep indigo void like a great seal, its rim a band of pale gold beads and seven-pointed stars. Inside the ring is a dizzying spiral: floating broken arches and fragments of stairs coil round and round, smaller and smaller, falling into a black star-flecked centre where a black sun with a pale dry-brush halo sits. Sweeping dry-brush strokes of indigo and white curl out from the ring across the sky like a slow whirlpool, and some of them run off the right edge. A few small black orbs with brush-stroke halos hang around the ring. Robed silhouettes stand small along a curved pale ledge at the bottom, looking up. Nearest them, at the lower right, a cloaked traveler seen from behind, a dark silhouette with a glowing rim, raises a staff toward the right. ' + STYLE),
    'left_c2': ([CHALK, GIANT, MECH],
                ROLES3 + 'Tall portrait picture, aspect ratio 2:3, keeping the top tenth of the picture as plain dark sky. The vertical axis of the main shape stands sixty percent of the way across the picture from the left. Subject: the Great Labyrinth as a symbol, not a real place. A colossal inverted spiral tower hangs point-down from a black sun with a pale gold dry-brush halo, turning down through a star-flecked void of deep indigo and violet. Each turn of the spiral carries a fragment of a different land, drawn like a small paper diorama: a mossy green cavern, frost-covered arches, an ember-lit forge, a drowned hall, a corridor of stars. The lower the turn, the darker it gets, until the tip dissolves into darkness above a floating rock. Thin gold stairs run along the spiral. Behind it, very large and very faint, a faceless shadow with a long clawed hand reaches toward the right edge, its fingers touching the edge. At the lower right, a small cloaked traveler seen from behind stands on the floating rock, cape blowing, raising a staff with a small light toward the right. ' + STYLE),
    'left_c': ([CHALK, GIANT, MECH],
               ROLES3 + SIZE_L + 'Subject: the Great Labyrinth as a symbol, not a real place. A colossal inverted spiral tower hangs point-down from a black sun with a pale gold dry-brush halo, turning down through a star-flecked void of deep indigo and violet. Each turn of the spiral carries a fragment of a different land, drawn like a small paper diorama: a mossy green cavern, frost-covered arches, an ember-lit forge, a drowned hall, a corridor of stars. The lower the turn, the darker it gets, until the tip dissolves into darkness. A thin gold ribbon of stairs runs along the spiral. Behind it, very large and very faint, a faceless shadow with a long clawed hand reaches toward the right edge. ' + TRAVELER + STYLE),
    # 右扇再收一档：人物往 PV 那种大块剪纸收，身份只留几样记号，整张不透明
    'right_pv': ([os.path.join(OUT, '_guide_right_pv.png'), GIANT, MECH, CHALK, FACE],
                 'Image 1 is the composition guide: repaint it as a tall portrait picture with aspect ratio 1:2, keeping every figure in the same place and the same pose, all turned to the left. Images 2, 3, 4 and 5 are style references: copy how they are drawn, and do not copy their characters, objects or scenes. '
                 'Simplify the figures drastically, the way images 2 and 5 are drawn: each figure is only a few very large flat shapes with a soft colour gradient across them. Long hair, capes and robes merge into huge sweeping ribbon shapes that flow away to the right and off the picture. Faces are pure side-profile silhouettes with a thin pale outline, one thin line for a closed eye, no irises, no nose or mouth shading. Costume detail is reduced to a few thin gold lines and one small emblem each. '
                 'Keep only these marks of who each one is: the goddess with large white wings draws a golden bow aimed left; the god with half of his body cracked stone has wings of layered rock; the red-haired duke has one wing of flame and one of frost and a golden sun staff; the blonde goddess has a small black cat on her shoulder; the small goddess has little fawn antlers and holds wheat; the green-haired healer has tiny wings on her head; the calm man wears a plain undyed hood; the queen in front has a small spiked gold crown, a braided bun and a scar across her eye, and raises a long straight sword; the queen beside her has very long silver hair, a large black bow, a pointed ear, a small red mark on her forehead and a crimson high collar, and holds up a scepter with a red crystal. '
                 'Palette: a deep indigo night with one or two huge pale discs, the figures in pale cream and lavender washed with soft coloured light, with only small accents of crimson, gold and green. ' + STYLE),
    # 右扇拆两层：人物透明底，天空单独一张，这样只有人物盖过框线，宽屏上天空也够宽
    'right_fig': ([os.path.join(HERE, 'out', '四方_11-03', 'gpt_mid', 'right.png'), os.path.join(REFS, '参考_巴尔缇娜.png'), os.path.join(REFS, '参考_索恩薇娅.png'), GIANT, FACE],
                  'Image 1 is the composition guide: redraw it completely in a new style as a tall portrait picture with aspect ratio 1:2, keeping every figure in the same place and the same pose, all turned to the left. Keep who each figure is and what each is doing: the winged goddess with large white wings draws a bow aimed left; the god with black hair, half of his body human and half cracked stone, has wings of layered rock ridges; the red-haired duke has one wing of flame and one wing of frost and thrusts a golden sun staff to the left; the blonde goddess has a small black cat on her shoulder; the small goddess with little fawn antlers holds out a sheaf of wheat; the green-haired healer with tiny wings on her head holds out cupped hands; the calm man in a plain undyed hooded robe rests one hand on a sheathed sword. '
                  'In front, the crowned queen raises a long straight sword high in her black gloved hand, the blade pointing up and to the left, and the silver-haired queen holds up a scepter topped with a red crystal. '
                  'Images 2 and 3 show who the two queens are: copy their faces, hair and costume design, not their rendering. The silver-haired queen has a large black bow, pointed ears, a small red mark on her forehead and a closed high collar; the crowned queen has a braided bun and a scar across one eye. '
                  'Images 4 and 5 are style references only: copy how they are drawn, and do not copy their characters, objects or scenes. Faces are clean side profiles with very few features. The figures are pale and luminous with rich crimson, emerald and gold accents. '
                  'Use a transparent background: only the figures with their hair, wings and cloth, with no sky, no clouds, no discs and no loose ribbons behind them. No part of a figure touches the top edge or the right edge of the picture; they may run off the bottom edge. ' + STYLE),
    'sky_right': ([CHALK, GIANT, MECH],
                  ROLES3 + 'Tall portrait picture, aspect ratio 2:3: an empty night sky with no figures at all. Deep dark indigo and violet, with fine parallel hatching and dry-brush chalk grain. Two very large pale discs with brush-stroke halos in the upper half, a few very thin gold arcs, long soft brush sweeps of slightly lighter indigo, and a few small four-pointed stars. Keep it dark overall, so that pale figures placed in front of it stand out. ' + STYLE),
    # 右扇外侧的云：挡住人物图的外缘，像纸剧场的侧幕
    'cloud_wall': ([CHALK, GIANT, MECH],
                   ROLES3 + 'Tall portrait picture, aspect ratio 1:2, with a transparent background: a tall stack of flat, layered clouds made like cut-paper stage scenery, filling the right two thirds of the picture from the bottom up, with a billowing scalloped edge running down its left side and transparent empty space at the far left. The stack is widest at the bottom and thins out toward the top, where a few small clouds drift. Deep indigo and muted lavender with pale cream light along the upper edge of each cloud, fine parallel hatching and dry-brush chalk grain inside the shapes. Only the clouds, with no sky behind them, no discs, no stars and no shadow. ' + STYLE),
    # 左扇：c2 的构图，每一圈换成底卡写的那些层（#1019 雪原都市、机械工厂、亡国王宫、深海神殿，#1022 灰白石城和永昼灯塔，#1101 骨谷）
    'left_d': ([os.path.join(OUT, 'left_c2.png'), CHALK, GIANT],
               'Image 1 is the composition guide: repaint it as a tall portrait picture with aspect ratio 2:3 in exactly the same drawing style, keeping the black sun, the inverted spiral tower, the position of every turn, the large faint shadow with its clawed hand reaching to the right edge, and the floating rock and the traveler exactly where they are. '
               'Change only what each turn of the spiral contains, from top to bottom: first, a walled ring city of pale white stone with one tall lighthouse, at the rim of a great pit; second, a snow-covered city of frosted towers; third, a vast factory of iron gears, pipes and furnaces lit orange; fourth, a fallen royal palace with a broken throne hall; fifth, a drowned temple under deep blue-green water; last and lowest, a narrow dark canyon whose walls are made of bones and ribs, dissolving into darkness. '
               'The traveler is a small figure in a cloak with the hood up and no hair showing, seen from behind. Images 2 and 3 are style references only: copy how they are drawn, and do not copy their characters, objects or scenes. ' + STYLE),
    # 楣和座的零件，透明底
    'orn_ribbon': ([CHALK, GIANT, MECH],
                   ROLES3 + 'A landscape picture with aspect ratio 3:2 on a fully transparent background: an ornament for the corner of a game interface. A cluster of long sweeping calligraphic ribbons curling into one large spiral and two small ones, in deep indigo and soft lavender with thin pale cream edges, with fine parallel hatching and dry-brush chalk grain inside the shapes. Only the ribbons, nothing behind them, no shadow. ' + STYLE),
    'orn_crest': ([CHALK, GIANT, MECH],
                  ROLES3 + 'A landscape picture with aspect ratio 3:2 on a fully transparent background: a symmetrical emblem for the top of a game interface. A large eight-pointed star of pale cream gold in the centre, drawn flat with fine hatching, with a thin ring around it, and two long thin calligraphic arcs sweeping out to the left and right like wings, ending in small curls and small four-pointed stars. Matte, no glossy metal, no glow. Only the emblem, nothing behind it, no shadow. ' + STYLE),
    'orn_meadow': ([GIANT, MECH, CHALK],
                   ROLES3 + 'A very wide landscape picture with aspect ratio 3:1 on a fully transparent background: a strip for the bottom of a game screen. Dark indigo silhouettes of grass and large dark flowers with soft violet light on them, and a few small glowing white flowers on thin stems, as in the bottom of the style references. The plants are tallest at the far left and far right ends and low across the middle. Only the plants, nothing behind them, no ground block, no shadow. ' + STYLE),
}

# 融合那几张要用上面出的图，放在表的后头。right_f2 是 right_f1 的另一张，现行是在 right_f1 上改出来的 right_f3
FUSION = {
    'right_f1': ([GUIDE_F, os.path.join(OUT, 'right_a.png'), SHEET_F], FUSE),
    'right_f2': ([GUIDE_F, os.path.join(OUT, 'right_a.png'), SHEET_F], FUSE),
    'right_f3': ([os.path.join(OUT, 'right_f1.png'), SHEET_F],
                 'Image 1 is a finished picture. Repaint it with aspect ratio 7:10, keeping everything the same: every figure, face, pose, colour, ribbon, cloud and the whole layout. Make only these small changes. '
                 'First, remove the red crystal, its gold star-shaped mount and its thin stem from above the crowned queen: nothing stands on or above her crown, and the cloak and the green cape behind it continue unbroken. '
                 'Second, give that crystal to the silver-haired queen: her black gloved hand comes up from her crimson coat in front of her chest, holding a slim gold scepter upright, with the small red crystal at its tip at the height of her collar, well to the right of the other queen\'s crown. '
                 'Third, the red-haired duke\'s wing of faceted blue ice crystals is larger and rises clearly above his shoulder, as in image 2. '
                 'Fourth, the small goddess has slightly larger branching antlers, as in image 2. '
                 'Image 2 is a sheet of close-ups: use it only to keep the faces right. Same drawing style as image 1. No text, no logo, no frame.'),
    # 左扇甲乙融合：构图照甲，圆环、悬空的断拱和小黑环照乙
    'left_ab': ([os.path.join(OUT, 'left_a.png'), os.path.join(OUT, 'left_b.png'), CHALK],
                'Image 1 is the layout: repaint it as a tall portrait picture with aspect ratio 2:3 in exactly the same drawing style, keeping the top tenth of the picture as plain dark sky. Keep from image 1, in the same places: the colossal faceless shadow in side profile with its long veil of sweeping ribbons, its huge clawed hand reaching to the right, the black sun with the pale gold dry-brush halo, the spiral well of pale stone arcades going down into darkness, the gold stair winding down into it, the small hooded traveler on the rock at the lower right raising a staff, and the dark grass with small white flowers along the bottom edge. '
                'Bring in from image 2: a great ring of gold beads and gold seven-pointed stars, hung as a large tilted ellipse around the upper part of the well, passing behind the hand; and, floating inside and above that ring, a few broken pale stone arches and fragments of stairs drifting upward out of the well, and two or three small black orbs with brush-stroke halos in the sky. Keep it calm and readable, with large empty areas. Image 3 is a style reference only: copy how it is drawn, and do not copy its objects. ' + STYLE),
    # 双王换脸的 GPT 对比版（用户 11-03 发了图二双王那一段当标准）。现行的脸是 fix_queens.py 直接移植的
    'right_f5': ([os.path.join(OUT, 'right_f3.png'), os.path.join(OUT, '_queens_close.png')],
                 'Image 1 is a finished picture. Repaint it with aspect ratio 7:10, keeping everything the same: every figure, pose, colour, ribbon, cloud and the whole layout, including the sword, the gloved hands and the scepter. Change only the heads of the two queens at the bottom of image 1. Image 2 is a close-up of exactly those two queens: copy their heads from it as faithfully as you can, at the size and position of the heads in image 1. '
                 'Copy the same stern half-lidded eyes with amber irises and fine lashes, thin straight eyebrows, small straight nose, tiny flat mouth and the same soft jaw line. The left queen in image 2 has rich auburn hair with long swept bangs falling past her cheek, a very large bun of thick braids, a tall gold crown with five faceted spikes, a thin red scar running down through her eye, and a gold diamond-shaped earring. The right queen in image 2 has silver hair with long straight bangs, a thick braid running across her head into a large dark purple bow, a long pointed ear, a small red diamond-shaped mark on her forehead, and a gold diamond earring with red drops. Same drawing style as image 1. No text, no logo, no frame.'),
}
JOBS.update(FUSION)


def fusion_refs():
    """右扇融合用的两张：构图稿（right_pv 靠左，右边留白到 7:10，这回外侧也画满），right_a 的脸和神裁大拼一张设定表。"""
    from PIL import Image
    if not os.path.exists(GUIDE_F):
        r = Image.open(os.path.join(OUT, 'right_pv.png')).convert('RGB')
        r = r.resize((int(r.width * 1500 / r.height), 1500), Image.LANCZOS)
        c = Image.new('RGB', (1050, 1500), (30, 28, 72))
        c.paste(r, (0, 0))
        c.save(GUIDE_F)
    if not os.path.exists(SHEET_F):
        a = Image.open(os.path.join(OUT, 'right_a.png')).convert('RGB')
        boxes = [(170, 60, 470, 360), (540, 180, 887, 527), (20, 350, 560, 640),      # 弓手、石神、红发公爵
                 (470, 440, 770, 740), (60, 590, 360, 890), (330, 670, 610, 950),     # 金发女神、鹿角、绿发
                 (630, 640, 887, 897), (0, 920, 440, 1360), (400, 900, 887, 1387)]    # 兜帽、戴冠女王、银发女王
        C = 512
        s = Image.new('RGB', (C * 3 + 16, C * 3 + 16), (24, 22, 56))
        for i, b in enumerate(boxes):
            im = a.crop(b)
            k = C / max(im.size)
            im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
            s.paste(im, (i % 3 * (C + 8) + (C - im.width) // 2, i // 3 * (C + 8) + (C - im.height) // 2))
        s.save(SHEET_F)


if __name__ == '__main__':
    for name in (sys.argv[1:] or JOBS):
        if name in FUSION:
            fusion_refs()
        refs, prompt = JOBS[name]
        print(name, gpt_gen.gen(os.path.join(OUT, name), prompt, refs=refs), flush=True)
    print('done')
