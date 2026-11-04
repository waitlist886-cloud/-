#!/usr/bin/env python3
# 月银纪那一套四方（11-04）。python gpt_moon.py [名字…]，写 out/月银纪_11-04/，已有的不重出。
# 内容照用户 11-02 最早那段话：右边传奇，右上凯尔萨斯举猎龙大枪遥指左边，右下希尔妲双手护火，左边巨兽王种，左上魔神虚影，正上方浮塔与各族和魔族，下方一双正神的手托起框。
# 画法照迷宫纪 1001 年定稿那一套（第九、十回），调子换成黎明前的冷银蓝，全图只有火是暖的（天亮以前人只有火）。不画圆盘，不写月相。
# 长相照各页旅伴条的外貌。凯尔萨斯没有画像，脸在光里（#1007、#1013）；魔神、正神不画脸。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_gen

OUT = os.path.join(HERE, 'out', '月银纪_11-04')
PV = os.path.join(HERE, 'out', '四方_11-03', 'pv')
S = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '语料', '风格参考_11-03')
GIANT, MECH, CHALK, FACE = [os.path.join(S, n) for n in ('pv_giant.png', 'pv_mech.png', 'pv_chalk.png', 'pv_face.png')]

RENDER = ('Draw it the way the style reference images are drawn: a high-end animated storybook sequence from a Japanese fantasy game, like a paper theatre lit from behind. '
          'Monumental figures built from large flat cut-paper shapes with crisp, confident silhouettes, overlapping in clear layers. Hair and cloth are huge sweeping ribbon shapes and long calligraphic curves. '
          'Inside the flat colour areas: smooth colour, fine parallel hatching, engraved line texture and dry-brush chalk grain, like gouache and linocut printing. Thin pale or coloured outlines, not black. Matte. '
          'Big calm empty areas, fewer small details than a normal anime illustration. A few small four-pointed stars are fine. ')
PALETTE = ('The palette is a cold sky before dawn: deep slate blue, ash blue and pale silver, with silver-white light on the edges of the shapes. Warm amber firelight is the only warm colour in the picture, and it is rare and precious. ')
NOT = ('Do not use: glossy anime key-art shading, realistic metal, sparkles everywhere, floating gold dust, busy ornament, 3D look, western cartoon proportions, thick black outlines, text, logo, frame, '
       'large round discs, moons, crescents, moon phases. ')
STYLE = RENDER + PALETTE + NOT
ROLES = 'The attached images are style references only: copy how they are drawn, and do not copy their characters, objects or scenes. '

JOBS = {
    'right': ([os.path.join(PV, 'right_f7.png'), GIANT, FACE, CHALK],
              'Image 1 shows only how figures are arranged on the page: a tall cascade from the top of the picture to the bottom, overlapping in layers, every figure turned to the left, the biggest figures at the bottom, with long ribbons of cloth flowing away to the right. Use that kind of arrangement and that sense of scale, as a tall portrait picture with aspect ratio 7:10, but every person here is different: do not copy any character, costume, face or colour from image 1. Images 2, 3 and 4 are style references only: copy how they are drawn, and do not copy their characters, objects or scenes. '
              'Everyone is doing something different and all of it is aimed to the left, toward the left edge of the picture. From top to bottom: '
              'First, highest of all, an emperor-mage in heavy dark gold armour engraved with magic circles and a long cloak that is a field of night sky full of stars, with long straight platinum hair and a plain crown floating in the air above his head, touching nothing. His face cannot be seen at all: it dissolves into a white glare. With both arms he levels a colossal dragon-hunting lance, longer than a ship\'s mast, pointing up and to the left, and its huge tip passes out of the left edge of the picture. '
              'Second, behind him and far to the right, huge and dim, a giant with grey-green skin and two short tusks, bent under half a mountain carried on his back, gripping a tall straight staff of white stone. '
              'Third, in the air at the upper middle, a rider on a white horse with huge white wings, leaping to the left. The rider is a young man with a cloth tied over his eyes, his long hair half pale gold and half white, holding a slim ash-wood spear. '
              'Fourth, at the middle left, an old king with long silver-white hair and beard both in thick braids tipped with ivory beads, ice-blue eyes and an old scar from his left brow to his cheekbone, in a tattered royal robe of pale hide, swinging overhead an enormous greatsword carved from a single white mammoth tusk, longer than he is tall. '
              'Fifth, an elf archer with pale gold hair tied back with a vine cord, long ears and deep green eyes, in plain leaf-brown clothes, drawing a long bow to its full stretch, aiming up and to the left with a single arrow whose tip holds a thin line of sunset gold. '
              'Sixth, at the middle right, a young shepherd with messy black hair curling at the tips, storm-grey eyes and a thin white scar on his jaw, in a short wool tunic and a vest of lightning-spotted leopard skin, holding a pale ash-wood shepherd\'s staff. His head is tipped back, breathing in, and thin violet lightning falls from above and coils around him into his chest. '
              'Seventh, at the lower right, a woman with very long black hair with blue tips drifting as if under water, a crown of white pearls, pale skin and a long white linen robe, her eyes closed and her head lifted, singing, with one great blue-green wave curling up behind her. '
              'Eighth, a tall thin woman scholar with a straight black bob with a raven-blue sheen and violet eyes, in a worn grey scholar\'s robe, her raised right hand wearing one silver ring; a huge thin ring of glowing silver runes turns in the air around her. '
              'Ninth, in front at the lower left, a very broad short dwarf with a red-brown beard in two long braids and a singed left eyebrow, in a leather apron, planting an enormous wide shield in front of him with a two-handed war hammer on his shoulder, immovable. '
              'Tenth, at the very bottom in front of everyone and the largest of all, a young woman kneeling, in an oversized fox-fur coat with the sleeves rolled up and a hood edged with fox-tail fur, a thick ash-gold braid falling past her waist and tied with a faded red yarn, amber eyes, a scatter of freckles and wind-reddened cheeks, with a tall basket of birch bark and willow on her back. She bends over and shelters one small flame with both cupped hands. The flame lights her face from below, and it is the only warm light in the picture. '
              'Faces are fine, delicate anime faces with clean lines and clear eyes, and each face looks like a different person. Fully clothed everyone, not sexualized. Continue the night sky, long ribbons of pale cloth and a few soft clouds all the way to the right edge, with no new figures. ' + STYLE),
    'left': ([CHALK, GIANT, MECH],
             ROLES + 'Tall portrait picture, aspect ratio 2:3. Keep the main shapes in the right two thirds of the picture, and keep the top tenth of the picture as plain dark sky. Subject: the great beasts of the old world, in the long night before dawn, with the shadow of a god above them. Every beast faces right, toward the right edge of the picture, each one huge and each one doing something different. From top to bottom: '
             'First, very large and very faint, filling the upper part of the sky, the shadow of a demon god leaning in from the upper left: one vast faceless outline of smoke in dark violet-blue, with no features at all except two thin slits of cold light where eyes would be. '
             'Second, below it, a colossal blue-green ancient dragon with wings so wide they are like a weather front across the sky, flying to the right; far behind it hangs a huge floating crag of rock with a tiny walled town and fields on its back. '
             'Third, at the middle, on a ridge, a colossal pale stag king with antlers as wide as half the sky and thin violet lightning coiled between the tines, its head lowered to the right; beside and behind it a mountain-sized frost mammoth with a whole winter of snow on its back, huge curving tusks and icy breath. '
             'Fourth, lower down, a titanic wild boar whose mane is rows of stone spires and whose tusks are like two plows, charging to the right, and in the far distance a vast whale rising out of sea fog with grass and a small tree growing on its back like an island. '
             'Fifth, at the bottom, in front and the largest of all, a crownless red-scaled ancient dragon crouching low, its huge head thrust out to the lower right and wreathed in red and black fire, with a broken sword blade wedged deep into its skull between the eyes. Its snout, its horns and one huge claw reach to the right edge of the picture and pass beyond it. '
             'Along the very bottom edge, dark silhouetted grass. ' + STYLE),
    # right 放回大框一看，顶上的巨枪压在顶栏底下，底下的希尔妲叫座盖住了。人缩到 0.79 贴在大一圈的底上（_guide_right2.png，moon_guide 那几行拼的），空的地方叫 GPT 接着画，别的不动
    'right2': ([os.path.join(OUT, '_guide_right2.png'), GIANT, FACE],
               'Image 1 is a finished picture that has been shrunk and placed on a larger plain dark blue page: the plain flat areas at the top, along the right side and along the bottom are unpainted. Repaint it as a tall portrait picture with aspect ratio 7:10, keeping every figure exactly where it is in image 1, at the same size, in the same pose and facing the same way, with the same faces, hair, costumes, colours and drawing style. '
               'Paint the unpainted areas: at the top and along the right side continue the deep blue night sky with a few small stars, a few soft clouds and long pale ribbons of cloth flowing away to the right, with no new figures. Along the bottom continue the kneeling woman’s fur coat and the dwarf’s legs and apron downward, ending in soft mist and pale ribbons. '
               'Change only two things. The old king with the braided beard wears no crown at all. The small flame in the hands of the kneeling woman is twice as large, a clear warm amber flame that lights her hands and face. '
               'Images 2 and 3 are style references only: copy how they are drawn, and do not copy their characters, objects or scenes. ' + NOT),
    # 楣：正中浮塔，两道弧上各族和魔族朝塔走
    'tower': ([CHALK, GIANT, MECH],
              ROLES + 'A wide landscape picture with aspect ratio 3:2 on a fully transparent background: a symmetrical emblem for the top centre of a game interface. In the centre a tall slender tower of pale silver stone floats in the air, its base a broken point of rock with a few small rocks hovering under it, its top holding a small soft crown of white light. A long thin arc of silver runs out to the left and to the right from under the tower like a pair of wings, curling up at the ends with small four-pointed stars. Standing on each arc, a line of small silhouettes walks toward the tower: humans, long-eared elves, stocky dwarfs, dragon-kin with small horns and tails, beast-eared folk, small halflings, and horned demon-kin walking among them. Flat cut-paper shapes with fine hatching, pale silver and ash blue. Only the emblem, nothing behind it, no shadow. ' + STYLE),
    'ribbon': ([CHALK, GIANT, MECH],
               ROLES + 'A landscape picture with aspect ratio 3:2 on a fully transparent background: an ornament for the corner of a game interface. A cluster of long sweeping calligraphic ribbons curling into one large spiral and two small ones, in slate blue and soft silver with thin pale edges, with fine parallel hatching and dry-brush chalk grain inside the shapes. Only the ribbons, nothing behind them, no shadow. ' + STYLE),
    # 座：一双正神的手。只画一只，另一只镜像，托在框底的两角。只有手和袖口，没有脸
    'hand': ([CHALK, GIANT, MECH],
             ROLES + 'A square picture with a fully transparent background: one huge open hand of a god, reaching up from the lower right corner of the picture, seen from the side with the palm facing up and the long fingers gently curled upward and to the left, as if carrying the corner of something heavy and precious. The skin is smooth pale marble white with very thin silver lines, drawn as large flat shapes with fine hatching. The wrist goes into a long wide sleeve of soft silver-blue cloth, and the sleeve dissolves into mist and sweeping ribbons at the bottom right corner. No body, no face, no jewellery, nothing else. Only the hand and the sleeve, nothing behind them, no shadow. ' + STYLE),
    # 用户 11-04 给了一张捧手的照片（_ref_hands.png 是从那张裁的，只留手）：不是从两角伸上来，是两只手掌心朝上拢在一起，从两侧捧着整个框。对正神来说，人、魔族、巨兽都是看着长大的孩子
    'hands': ([os.path.join(OUT, '_ref_hands.png'), CHALK, GIANT],
              'Image 1 shows only the pose of the hands: two open hands cupped together side by side, palms facing up and the little-finger edges touching at the centre, the way someone cradles something small and alive in both hands. Copy that pose, and nothing else from image 1. Images 2 and 3 are style references only: copy how they are drawn, and do not copy their characters, objects or scenes. '
              'A wide landscape picture, aspect ratio 2:1, on a fully transparent background: the colossal cupped hands of a god, seen from the front and slightly above, perfectly symmetrical, filling the width of the picture. The hollow of the two palms is wide, open and empty, and it takes up the middle of the picture. The thumbs rise on the far left and far right like the two sides of a bowl. The fingers curve toward the viewer and run off the bottom edge of the picture. The skin is smooth pale marble white with very thin silver lines and soft blue-grey shadow in the hollow of the palms, drawn as large flat shapes with fine parallel hatching; gentle, elegant, long-fingered hands with no nail polish and no jewellery. '
              'Behind each thumb the wrist goes outward and slightly upward into a long wide sleeve of soft silver-blue cloth, and each sleeve sweeps away to the left or right edge of the picture and dissolves into mist and thin ribbons. No body, no face, nothing inside the hands. Only the hands and the sleeves, nothing behind them, no shadow. ' + STYLE),
    # hands 放进去太大，一片白，把两扇的人都盖了，也看不出是手。改成从框的两个下角包上来：手指托在框底下往中间合，拇指贴着框的两边往上，手腕和袖子低低地往外散。灰方块就是窗口
    'hands2': ([os.path.join(OUT, '_guide_hands.png'), os.path.join(OUT, 'hands.png'), CHALK],
               'Image 1 is a layout guide: the grey rectangle stands for a large flat panel that is NOT drawn. Image 2 shows how the hands and sleeves are drawn: copy its drawing style, its skin and its cloth, but not its pose. Image 3 is a style reference only. '
               'A very wide landscape picture, aspect ratio 3:1, on a fully transparent background: the colossal hands of a god holding the panel of image 1 from below and from both sides, tenderly, the way a parent lifts something small and precious in both hands. The left hand is at the lower left corner of the panel and the right hand is at the lower right corner, perfectly mirrored. '
               'Each hand curls around the bottom corner of the panel: the long fingers run under the bottom edge of the panel, pointing toward the centre, with their fingertips nearly meeting below the middle of the panel; the palm sits at the bottom corner; the thumb rises against the side of the panel, pointing straight up, no higher than the middle of the panel. The wrists are outside the panel and low down, and each goes into a wide sleeve of soft silver-blue cloth that sweeps outward and downward to the far lower corners of the picture and dissolves into mist and thin ribbons. The hands stay low: nothing rises higher than the thumbs. '
               'Inside the grey rectangle nothing at all is drawn, and that whole area is fully transparent; do not draw the rectangle or its outline. The skin is smooth pale marble with very thin silver lines and soft blue-grey shadow, in large flat shapes with fine parallel hatching. Gentle, elegant, long-fingered hands, with no nail polish and no jewellery. No body, no face. Only the hands and sleeves, nothing behind them, no shadow. ' + STYLE),
    # 座的底：一条横贯全屏的暗原，几堆小火
    'ground': ([GIANT, MECH, CHALK],
               ROLES + 'A very wide landscape picture with aspect ratio 3:1 on a fully transparent background: a strip for the bottom of a game screen. A dark plain seen from far away: silhouettes of low grass and rolling mist in slate blue with soft silver light on the tops, with a few tiny campfires scattered along it, each a single small warm spark. The land rises highest at the far left and far right ends and stays low across the middle. Only the land, the mist and the fires, nothing behind them, no sky, no shadow. ' + STYLE),
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name in (sys.argv[1:] or JOBS):
        refs, prompt = JOBS[name]
        print(name, gpt_gen.gen(os.path.join(OUT, name), prompt, refs=refs), flush=True)
