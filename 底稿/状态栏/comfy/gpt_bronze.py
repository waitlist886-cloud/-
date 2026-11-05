#!/usr/bin/env python3
# 山铜纪那一套四方（11-04）。python gpt_bronze.py [名字…]，写 out/山铜纪_11-04/，已有的不重出。
# 内容照用户原话：右侧是黎明篡位当夜以挽昼斩落王座分割晨昏的索恩薇娅，以及东大陆比较具有代表性的传奇。左侧是落下了王棋的巴尔缇娜，背后环抱她满身伤痕缓缓消散的薇瑟兰，以及镇杀对应魔神拆解权柄的七位魔神将。
# 这一纪元左右扇不会如其他纪元那样有明显互相对立的感觉，而是更多的各自的群像。底栏是灰雨的废墟，卡顶花边是象征恶神的爪与大迷宫的虚影。
# 画法照定下的那一套（README 第七回的纸剧场，脸照纷争纪第三稿那种清楚的大眼睛）。调子：右扇一道直的剑光把天切成两半，外侧还是半夜，靠窗一侧已经是黎明的金和白；左扇黑曜石和灰，灰雨斜着落，只有红莲色和山铜的暗金是暖的。
# 长相照底卡 #874、#875 到 #881、#888、#889、#918、#922、#934 和山铜纪各页人物条。薇瑟兰照山铜纪那一条：高个子，褐里夹灰的短发，洗白了的旧军大氅烧掉半边，手里什么也不拿。王棋 #69。三尊的样子照山铜纪第四、五页。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_gen

OUT = os.path.join(HERE, 'out', '山铜纪_11-04')
REF = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '语料', '人物参考_11-04')
STRIFE_R, STRIFE_L, STRIFE_T, MAZE_R, MAZE_T, MOON_R, FRIEREN = [os.path.join(REF, n + '.png') for n in ('strife_right_style', 'strife_left_style', 'strife_top_style', 'maze_right_style', 'maze_top_style', 'moon_right_style', 'frieren')]
QUEEN_B, QUEEN_T = os.path.join(HERE, 'refs', '巴尔缇娜_用户_11-03.webp'), os.path.join(HERE, 'refs', '索恩薇娅_用户_11-03.webp')

SERIES = ('Images 1 and 2 are finished pictures from the same series, and this picture must look as if the same hand drew all of them: a high-end animated storybook sequence from a Japanese fantasy game, like a paper theatre lit from behind. '
          'Monumental figures built from large flat cut-paper shapes with crisp, confident silhouettes, overlapping in clear layers. Hair and cloth are huge sweeping shapes with long calligraphic curves. Inside the flat colour areas: smooth clean colour with very fine parallel hatching, thin pale or coloured outlines, never black. Matte. Big calm empty areas between the figures. '
          'Beautiful clean anime faces drawn as in those images: clear eyes with visible irises and highlights, thin eyebrows, small straight nose, tiny mouth, soft curved jaw, and each face looks like a different person. Do not copy the characters, scenes or colours of those images. ')
CLEAN = ('Keep it clean: no grit, no rust, no scratches, no smudged smoke, no sparkles everywhere, no glossy key-art shading, no 3D look, no thick black outlines. The world is European high fantasy, swords and sorcery, with nothing East Asian: no pagodas, no curved roofs, no curling auspicious clouds, no ink wash, no wide hanging sleeves. '
         'Natural anatomy: heads on normal short necks, every arm with a clear shoulder, elbow, wrist and hand at the right length. Everyone is fully clothed, not sexualized. No text, no logo, no frame, no large round discs, no moons or crescents. ')
GROUP = 'This is a group portrait of legends, not a battle: nobody is charging at anybody and no army faces another. Each person is doing something of their own, calm and monumental. '

JOBS = {
    # 右扇：靠窗在左。天叫一道剑光切成两半，上和外侧还是半夜，下和靠窗一侧已经是黎明。她从底下往上斩，王座在靠窗的上头，苇棚区的火把从右下顺着白石大阶流上来
    'right': ([STRIFE_R, MAZE_R, QUEEN_T, FRIEREN],
              SERIES + 'Image 3 is the character design of the swordswoman: keep her face, her pale gold eyes and her hair colour, but not her hairstyle or costume. Image 4 is the character design of the small elf mage: keep her face, hair and costume. ' + CLEAN + GROUP +
              'A tall portrait picture, aspect ratio 7:10. The left edge of the picture will sit against a dark window, so everything important stays inside the picture, and blades and hands stop just before the left edge. The top tenth of the picture is plain sky. '
              'THE SKY IS CUT IN TWO. One perfectly straight, razor-thin line of blinding white-gold light crosses the whole picture, from near the upper left corner descending to the right edge at about half the height of the picture. Above and to the right of the line it is still midnight: a flat deep indigo night with a few small stars. Below and to the left of the line it is already dawn: flat layers of clear pale gold, warm rose and white, the morning of a whole world arriving at once. The two halves of the sky have slipped very slightly along the cut, like cut paper, with gold light pouring through the seam. Everything below the line is lit by that dawn, with warm gold rim light on the edges of the shapes. '
              'At the upper left, on the line: an immense gothic throne of white stone and pale gold at the head of a long white staircase. The line of light passes straight through it: the top of its tall back has been sheared off and is sliding away along the cut, with pieces falling. A heavy white-gold crown, cut cleanly into two halves, tumbles through the air in front of the throne. The throne is empty. '
              'In the middle of the upper half, large and in front, standing on the long white stair below the throne: a tall woman of twenty-seven with a soldier\'s straight back, the swordswoman of image 3. Old-copper dark auburn hair cut to the shoulders and tied low at the nape, a few short strands at her forehead scorched pale, pale gold eyes, a fine white scar at the tail of her left eyebrow, a calm hard face. A long worn military greatcoat in dawn white and old copper, with a light mail shirt of dull copper under it, an old polished leather sword belt, no jewels at all. Her right arm has just swept upward to the upper left, and at the end of that stroke the sword points straight along the line of light, which starts from its tip. The sword is plain: a straight narrow blade, a simple iron crossguard, a hilt wrapped in hemp cord. Her long coat flows away to the right as huge sweeping shapes. '
              'From the lower right, a broad white stone stairway with white angel statues on both sides climbs from a wide river up to her feet, and it is crowded with very small silhouettes of poor people carrying torches and a few white candles: a long winding river of small warm flames. Far behind on the right, in soft pale layers, the white spires of a great gothic city in the dawn, with long banners bearing a golden kite bird. '
              'Below her, in the lower half of the picture, large and in front, the legends of the eastern continent, a layered group portrait from left to right and overlapping, each standing or sitting in the dawn light: '
              'First, an elf queen, tall and slender, silver hair the colour of laurel falling to her waist, green-gold eyes, long pointed ears, a crown of living branches woven with fine gold, in a long robe of white and forest green; she rests one hand on a young branch that grows out of the stone and looks out serenely. '
              'Second, a mercenary captain, a woman not tall but very thick in the shoulders, raven-black hair tied back carelessly with a leather cord, violet eyes, a worn old leather armour, a very narrow straight sword of dull copper colour held low; over her shoulder she carries a big ragged banner, sewn together badly from pieces of white cloth, with a clumsy white raven on it, flowing away behind her. Close behind her, smaller, her four comrades: a lean beast-eared archer man with a burnt longbow, a half-orc lancer with lower tusks and a chipped lance, a broad old dwarf with a sledgehammer, and a slight young woman with two small horns and a little amulet at her throat, one hand cupped to her mouth, calling out. '
              'Third, the small elf mage of image 4, silver-white hair in two long tails, standing a little apart and holding her tall staff, looking at something small in her palm with a calm expressionless face. '
              'Fourth, in front and low on the left, a dwarf king, short and solid as an anvil, with a thick auburn beard braided with rings of fire-coloured copper and eyes like white-hot iron, in a leather forge apron over dark mail. His right arm from the shoulder is cast entirely of dull gold orichalcum; it rests on the head of a long forge hammer. A small white-hot flame burns in a stone hearth beside him. '
              'Fifth, sitting on a step at the far lower right of the group, a sleepy-looking youth of nineteen with soft wheat-gold hair with bits of straw in it and a single grain of wheat on a straw cord at his neck, in a plain peasant tunic, a sheaf of wheat across his knees. '
              'Continue the dawn sky and the sweeping shapes of cloth all the way to the right edge, with no new important figures there.'),
    # 左扇：靠窗在右。黑曜石的棋盘从右下往左上升，七个人站在格子上，上头三尊死了的魔神正在被拆开。她在最前头落子，老师从背后抱着她，手盖在她手上，正在散成灰和光
    'left': ([STRIFE_L, MAZE_R, QUEEN_B],
             SERIES + 'Image 3 is the character design of the woman in black and crimson: keep her face, her silver hair, her golden eyes and the small red mark on her forehead. ' + CLEAN + GROUP +
             'A tall portrait picture, aspect ratio 7:10. The right edge of the picture will sit against a dark window, so everything important stays inside the picture. The top tenth of the picture is plain dark sky. '
             'The ground colour is obsidian black and deep charcoal, opening into soft flat layers of ash grey mist. Grey rain falls through the whole picture in fine, straight, slanted lines, with small flakes of pale ash among them, quiet and clean. The warm colours are rare and precious: the crimson of an ember-red coat, and the dull warm gold of orichalcum on the edges of things. '
             'At the top, far away and colossal, three dead demon gods loom in the sky, drawn as flat dark shapes with thin ember outlines, each clearly a different being, and each of them is being taken apart. '
             '(a) A hunched giant wound in coil upon coil of heavy chain, its hands five huge pincers, a smooth blank plate of orichalcum where the face should be, split by a crack of light. Its chains are being pulled away from it in three long strands. '
             '(b) A towering figure wrapped in grey cloth, tall as a fog bank, with no face under the cloth, only a few pale blank masks surfacing in its folds. The cloth is unravelling in two long strips. '
             '(c) A starving giant, nothing but a skeleton sitting on a yellow-grey throne, ribs standing around a hollow belly, with a gaping mouth in the belly that opens downward. It is breaking apart into two long shards. '
             'Each strand, strip and shard narrows into one thin ribbon of pale gold light and falls to one of the seven people below, seven ribbons in all. '
             'Below the gods: a vast chessboard of black obsidian and white stone squares, thin lines of dull gold between them, tilted up and rising from the lower right to the upper left of the picture like a great floor seen in perspective. Seven great lords stand on its squares like living chess pieces, in a cascade, each one distinct, each holding the end of a ribbon of light in their own way, not fighting anyone: '
             'One, highest, hovering above the board: a lean man with short dark teal hair tossed by the wind, hawk-like teal eyes, a close-fitting high-altitude flying uniform, six wings of light and wind on his back, not all the same size, a small copper bell at his belt. '
             'Two: an enormous bull-horned man, deep bronze skin covered in bright violet lightning scars, huge horns with heavy metal rings fitted on them, a beard with little sparks in it, a blacksmith\'s leather apron over dark violet and gold plate, chains of orichalcum wound around him, an old key and an iron ring on a cord at his neck. '
             'Three: a towering horned man with ash-grey skin, his right horn broken off with a molten red crack and twenty fine notches on the stump, his left horn glossy black obsidian, burn scars across his chest and arms, a long black and red military coat over heavy armour, a long-hafted heavy blade resting on his shoulder, wreathed in blue flame. '
             'Four: a woman with long deep-sea blue hair that is always wet, iridescent scales along her cheekbones and neck, deep blue eyes, a long pearl-coloured gown that moves like a tide around her feet, a shark-skin glove to the elbow on her left arm; a smooth tall wave stands at her back. '
             'Five: a tall full-figured woman with long frost-silver hair wound with thin blood-red thorns, crimson eyes, a severe black and crimson high-necked gown, thin black gloves, holding a slender needle between two fingers, a faint knowing smile. '
             'Six: a very thin pale man, almost translucent, a piece of crystal-clear bone showing along his left jaw, a gold-wire monocle of crystal, ice-blue eyes, a black high-collared robe, holding up a small bronze bell with a chip in its rim. '
             'Seven, smallest: a tiny girlish woman floating a hand above the board, long deep violet hair whose ends dissolve into stardust, a small black star in her hair, violet eyes half closed, layers of thin veils, a hand mirror held against her chest. '
             'At the bottom right, in front of everyone and by far the largest, two women. The woman of image 3: long silver hair falling loose, golden eyes lowered, the small red mark on her forehead, slightly pointed ears, cold pale skin, a slim black gown, a dull gold orichalcum corset belt, a long ember-crimson half-cape coat with a dark starry lining worn over her left shoulder, a long black glove on her right arm. She leans over the nearest squares of the board and with her black-gloved right hand she is setting down one chess king, about the size of her hand, of black obsidian banded with orichalcum. She looks at nothing but that piece. Her face is calm, and very sad. '
             'Behind her, wrapping both arms around her shoulders from behind: a taller woman of about thirty, with very short hair of brown mixed with grey, a plain tired gentle face, eyes closed, her cheek resting against the silver hair, the faintest smile. An old washed-white army greatcoat with no insignia, half of it burnt away. She is covered with wounds, long cuts across her face, her arms and her side. Her empty hand rests lightly over the black-gloved hand that holds the piece. And she is slowly vanishing: from the shoulders and back outward, her body and her coat are coming apart into flakes of pale ash and small motes of soft gold light that drift up and away to the left through the grey rain. She carries no weapon. '
             'Long sweeping shapes of the crimson coat and the white greatcoat flow to the left. Continue the mist and the rain to the left edge, with no new important figures there.'),
    # 座：灰雨城的废墟，两段，不翻转。左边南门和门洞，右边南坡的碑和书屋。框下沿以下暗，输入框压在正中
    'ruin_l': ([STRIFE_L, MAZE_R],
               SERIES.replace('Beautiful clean anime faces drawn as in those images: clear eyes with visible irises and highlights, thin eyebrows, small straight nose, tiny mouth, soft curved jaw, and each face looks like a different person. ', '') + CLEAN +
               'A very wide landscape picture, aspect ratio 3:1, on a fully transparent background: a strip for the bottom of a game screen, the ruins of a small burned city under grey rain, seen from straight in front. Everything above the ruins is fully transparent, no sky and no background. The ruins are highest on the left side and low on the right. '
               'A low ring wall built of fallen blocks of white stone, one man high, black with old fire. In it, on the left of centre, a deep arched stone gate, half collapsed, its vault blackened by smoke; the two gateposts are densely covered with thousands of small carved tally marks. Inside the arch a small warm fire still burns on the ground, the only warm colour in the picture, and beside it stand a few small woven baskets. Behind the wall stand burnt gables and broken house walls, charred beams, a cracked bronze bell lying on the ground, a long ruined workshop with its roof gone. Behind everything, on the far left, the foot of a colossal pale white rampart with a broken gap in it. '
               'Fine grey rain falls in straight slanted lines with flakes of pale ash, and the ground is wet black, shining a little. A few small pale flowers and thin green shoots grow from the ash. No people at all. The palette is charcoal, ash grey, wet black and cold white stone. The foot of the strip sinks into a flat band of dark ash-grey mist at the bottom edge of the picture.'),
    'ruin_r': ([STRIFE_L, MAZE_R],
               SERIES.replace('Beautiful clean anime faces drawn as in those images: clear eyes with visible irises and highlights, thin eyebrows, small straight nose, tiny mouth, soft curved jaw, and each face looks like a different person. ', '') + CLEAN +
               'A very wide landscape picture, aspect ratio 3:1, on a fully transparent background: a strip for the bottom of a game screen, the edge of a small burned city under grey rain, seen from straight in front. Everything above the ground is fully transparent, no sky and no background. The land rises on the right side and stays low on the left. '
               'On the left, low broken house walls and the shell of a small library, one tall wall still standing with empty charred bookshelves built into it, and stones heaped on stones. In the middle a low ring wall of fallen white stone. On the right, a slope covered with a great many very small graves, each one only a wooden marker, row upon row, and on the slope stands one tall plain stele of dull gold orichalcum, weathered and dark, with a long broken lance lying across its foot. At the bottom of the slope a small clear spring. '
               'Fine grey rain falls in straight slanted lines with flakes of pale ash, and the ground is wet black, shining a little. A few small white bell-shaped flowers and thin green shoots grow among the graves. No people at all. No letters on the stele. The palette is charcoal, ash grey, wet black and cold white stone, with only the dull gold of the stele warm. The foot of the strip sinks into a flat band of dark ash-grey mist at the bottom edge of the picture.'),
    # 楣：恶神的爪和大迷宫的虚影。正中一座倒悬的螺旋塔只有线，两个肩膀上爪子扣住框角，不镜像
    'crest': ([STRIFE_T, MAZE_T],
              'Images 1 and 2 show finished ornaments from the same series: draw this in exactly the same way, flat cut-paper shapes with smooth clean colour and very fine parallel hatching, thin pale outlines, matte, crisp silhouette. '
              'A single ornament on a fully transparent background, no background at all: the ghostly apparition of a vast labyrinth, an inverted spiral tower hanging point-downward, ring below ring of tiny arches and stairs narrowing to a point at the bottom, drawn only in thin pale violet-grey and dull gold lines, half transparent, like a thing not yet arrived. It is held from above in the grip of two enormous black talons that come down from the upper left and the upper right, curved and sharp, of black obsidian with a thin ember-red edge, their tips nearly meeting around the tower. Symmetrical in its overall shape but not a mirror copy. Wider than tall. Nothing else, no text.'),
    'strip': ([STRIFE_T, MAZE_T],
              'Images 1 and 2 show finished ornaments from the same series: draw this in exactly the same way, flat cut-paper shapes with smooth clean colour and very fine parallel hatching, thin pale outlines, matte, crisp silhouette. '
              'A very wide ornament, aspect ratio 3:1, on a fully transparent background, no background at all: a long horizontal decorative border: many long black curved talons with thin ember-red edges, overlapping and hooked over one another like the fingers of a great hand, flowing along one band across the whole width, and between them, half transparent, thin pale violet-grey and dull gold lines drawing fragments of arches, stairs and spiral galleries of a ghostly labyrinth. The same thickness everywhere, fading into thin tips at both ends. Nothing else, no text.'),
    'corner_l': ([STRIFE_T, MAZE_T],
                 'Images 1 and 2 show finished ornaments from the same series: draw this in exactly the same way, flat cut-paper shapes with smooth clean colour and very fine parallel hatching, thin pale outlines, matte, crisp silhouette. '
                 'A single corner ornament on a fully transparent background, no background at all: it sits on the upper LEFT corner of a window. A colossal black clawed hand of a dark god grips that corner from above and outside: three long jointed fingers with long curved obsidian talons come over the corner, one running along the top edge toward the right, two curling down along the left side, with thin ember-red edges and fine hatching. Behind the fingers, half transparent, thin pale violet-grey and dull gold lines draw a few arches and a broken spiral stair of a ghostly labyrinth. Nothing else, no text.'),
    'corner_r': ([STRIFE_T, MAZE_T],
                 'Images 1 and 2 show finished ornaments from the same series: draw this in exactly the same way, flat cut-paper shapes with smooth clean colour and very fine parallel hatching, thin pale outlines, matte, crisp silhouette. '
                 'A single corner ornament on a fully transparent background, no background at all: it sits on the upper RIGHT corner of a window. A colossal black clawed hand of a dark god grips that corner from above and outside: four long jointed fingers with long curved obsidian talons come over the corner, two running along the top edge toward the left, two curling down along the right side, with thin ember-red edges and fine hatching. Behind the fingers, half transparent, thin pale violet-grey and dull gold lines draw a few galleries and a piece of an inverted spiral of a ghostly labyrinth. Nothing else, no text.'),
}

# 废墟：坟前插的是木签，这个世界没有十字架。两段往外接的，超宽屏上座也有东西
JOBS.update({
    'ruin_r_b': ([os.path.join(OUT, 'ruin_r.png')],
                 'Image 1 is a finished strip on a fully transparent background. Repaint it with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size, in the same drawing style and colours, and keeping the background fully transparent. Change one thing only: all the small grave markers on the slope are cross-shaped now; replace every one with one plain thin upright wooden stake, a single leaning stick with no crossbar at all. There must be no crosses anywhere in the picture. No text, no logo, no frame.'),
    'ruin_lo': ([os.path.join(OUT, 'ruin_l.png')],
                'Image 1 shows a finished strip from the same picture, on a fully transparent background: draw in exactly the same way and colours. A very wide landscape picture, aspect ratio 3:1, on a fully transparent background, the part of the scene further to the left of image 1, with no sky and no background. A colossal rampart of pale white stone with tall blind arches and square buttresses, the same as the white wall at the far left of image 1, runs across the whole width of the picture and is broken in two places, with slopes of fallen white blocks at its foot and charred beams among them. It stays low at the right end of the picture, where it meets image 1, and rises to the left. Fine grey rain falls in straight slanted lines with flakes of pale ash, the ground is wet black, a few small pale flowers and thin green shoots. No people. The foot of the strip sinks into a flat band of dark ash-grey mist at the bottom edge of the picture. No text, no logo, no frame.'),
    'ruin_ro': ([os.path.join(OUT, 'ruin_r.png')],
                'Image 1 shows a finished strip from the same picture, on a fully transparent background: draw in exactly the same way and colours. A very wide landscape picture, aspect ratio 3:1, on a fully transparent background, the part of the scene further to the right of image 1, with no sky and no background. The slope of image 1 goes on rising to the right: black burnt fields in long wet furrows, a low broken field wall of white stone, a few charred tree stumps, more very small graves each marked with one plain thin wooden stake with no crossbar, and a few thin green shoots and small white bell-shaped flowers coming up through the ash. Fine grey rain falls in straight slanted lines with flakes of pale ash. No crosses. No people. The foot of the strip sinks into a flat band of dark ash-grey mist at the bottom edge of the picture. No text, no logo, no frame.'),
})

# 第二稿（11-04）用户原话：注意核对一下已有形象，角色的行为可以更加动态，有张力一些。
# 长相照卡里已有的立绘（ref/sheet_west、sheet_east，bronze_sheets.py 裁的），立绘和底卡对不上的照立绘（莫尔图斯年轻、黑短发、金眼、不戴单片镜）。白鸦四个人没有立绘，照底卡 #934（托伦灰褐皮肤，霍德短胡子，莉赛尔银灰长发无角）。
# 动作照各人的伟业和 #112 的拆权：瓦尔德拉克、格罗姆、赛壬缇娅拆铸枷者（炉枷、狱枷、誓枷），涅芙拉、赛勒斐恩拆饥渊者（食梦、渡），莉西娅、莫尔图斯拆噬名者（匿名、唱名）。
REFD = os.path.join(OUT, 'ref')
ACTION = ('This is a scene of legends caught at the height of action, not a posed portrait. Nobody stands still and nobody looks at the viewer: every body is thrown on a strong diagonal, mid-leap, mid-swing, mid-stride, the weight committed, muscles and cloth under strain. Hair and cloth are whipped hard in the direction of the force in huge sweeping shapes. Faces are fierce and alive, eyes open and blazing, some mouths open and shouting. '
          'But each person is in the middle of their own deed: there are no two armies facing each other, and nobody aims at the side edges of the picture as if at an enemy beyond them. ')
SKETCH = ('The last image is only a rough layout sketch: its crude coloured stick figures, blobs and arrows show where each figure goes, how each body is thrown and which way the motion goes. Follow its placement and its poses closely, but do not copy its drawing at all: no stick lines, no arrows, no flat blobs. ')
SHEETN = ('Image 4 is a sheet of character designs with a name above each one: these names are only for you. Keep each one\'s face shape, eye colour, hair, horns, build, colours and costume, redrawn in the drawing style of images 1 and 2 and not in the glossy rendered style of the sheet. Do not write any names or letters in the picture. Their poses in the sheet do not matter. ')
JOBS.update({
    # 右扇：靠窗在左。一道直光切开天，她整个人甩成一条斜线把剑斩到头；底下各人在各人的事里
    'right2': ([STRIFE_R, MAZE_R, QUEEN_T, os.path.join(REFD, 'sheet_east.png'), os.path.join(REFD, 'sketch_right.png')],
               SERIES + 'Image 3 is the character design of the swordswoman, keep her face, her eyes and her hair. ' + SHEETN + SKETCH + CLEAN + ACTION +
               'A tall portrait picture, aspect ratio 7:10. The left edge of the picture will sit against a dark window, so everything important stays inside the picture. The top tenth of the picture is plain sky, it will be covered. '
               'THE SKY HAS JUST BEEN CUT IN TWO. One perfectly straight, razor-thin line of blinding white-gold light crosses the whole picture from near the upper left corner down to the right edge at about half the height of the picture. Above and to the right of the line it is still deep midnight, flat deep indigo and violet with a few small stars. Below and to the left of the line it is already dawn: rose, pale gold and white, as if the night had been sliced off. A shock of wind blows outward from the line, and every cloth, flag, flame and strand of hair in the picture is blown away from it. '
               'At the upper left, on the line: an immense throne of white stone and pale gold at the head of the white stairs, unmistakably a chair as tall as a cathedral. The line has just gone through its tall back: the upper half is sliding off along the cut and toppling away, with blocks of white stone bursting outward along the cut. Below it the crown of the old king, split in two clean halves, spins in the air with its pieces flying. '
               'THORNEVIA, large in the upper middle, is the heart of the picture, at the very end of one tremendous rising two-handed slash. Her whole body is a single long diagonal from her back foot to the tip of the blade: both hands on the worn hemp grip of a plain old straight sword with an iron guard, arms driven out to the upper left at full stretch, the blade lying exactly along the line of light with the light pouring off it; her torso twisted hard into the blow, her front knee deeply bent on the top step of the stair, her back leg flung straight out behind her with the toe just leaving the stone. Her face is seen in three-quarter profile, fierce and burning, jaw set, pale gold eyes wide open, a fine white scar at the tail of her left eyebrow. Her chestnut brown hair is in the braided chignon at the back of her head as in image 3, with her long side locks and fringe torn loose and flying back. She has no crown. She wears the white high-collared mantle with gold edges and small gold stars over a black under-suit and a gold breastplate, and the great white mantle cracks out behind her like a sail in a huge whipping arc across the dawn to the right. '
               'From the left, the broad white stair falls away down to the lower left, flanked by white angel statues, and it is packed with very small dark silhouettes of poor people running up it with their torches raised high, a river of little flames, arms in the air. '
               'Below her, in the lower half, large and in overlapping layers from left to right, five deeds at once: '
               'AESRELIA at the left, the elf queen: her platinum silver hair and white and silver robe with pale green lining are lifted straight up by a surge of green wind, her crown is of living branches and fine silver; one arm flung high, the other hand driven down, and from under that hand living roots and branches explode out of the split white stairs, twisting up around her, bursting into new leaves. '
               'VESTA in the middle, the mercenary captain, a short woman with very thick shoulders in worn old leather armour, raven-black hair tied back with a leather cord and flying, violet eyes, mouth open shouting: she lunges up and forward with all her weight and her very narrow copper-coloured sword, its guard bound with copper wire, slashes clean through a great taut rope and iron bar that barred the way, the ends of the cut ropes whipping away; in her other fist she drags a pole with a badly sewn, ragged white flag with a clumsy white raven on it, which streams out to the right and is torn at the edges. '
               'Behind and to the right of her, smaller, her four comrades in a rush, each in their own motion: a very tall half-orc with grey-brown skin, long legs and no expression on his horse at a full gallop with a lance levelled; a tall lean beast-eared hunter with pale amber eyes and a notched left ear, drawing at full stretch a short bow whose limbs are burning, aiming high up into the sky; a broad dwarf with a short trimmed beard and huge hands, swinging a sledgehammer back over his shoulder; a pale woman with long silver-grey hair and no horns, crying out with all her strength, one hand at her throat. '
               'BROMGAR in front at the lower left, the dwarf king, short and solid as an anvil, dark brown beard braided with rings of fire-coloured copper, broad forehead, eyes like white-hot iron, a fur mantle over black and gold armour, his whole right arm of gleaming gold-coloured orichalcum: he has heaved a great forge hammer up over his head with that arm, back arched and twisted, about to bring it down on a white-hot bar on a black anvil, with a fountain of sparks and the mouth of a roaring furnace behind him. '
               'FRIEREN in front in the middle, the elf mage in her long white and gold robe with silver-white hair in two long tails: she thrusts her tall staff out and up at arm\'s length, its head an open ring of plain gold with a red jewel, and a wide whirling band of tiny silver magic marks rushes around her body, her hair and robe blown hard sideways. Her face stays calm and still, the one calm thing in the storm. '
               'HOB in front at the lower right, a youth of about nineteen with soft wheat-gold hair and a straw cord at his neck with one grain on it, in a plain peasant tunic, a sheaf of wheat tied on his back: he is in mid-stride, whole body swung round like a sower, flinging a great handful of seed in a long arc up and outward, and the seed trails across the air as a stream of small golden lights. '
               'Continue the dawn sky and the sweeping shapes of cloth all the way to the right edge, with no new important figures there.'),
    # 左扇：靠窗在右。她把王棋砸在盘上，盘从那里裂开；老师从背后抱着她，半边身子散成灰和光往上卷；上头七个人正把三尊拆开
    'left2': ([STRIFE_L, MAZE_R, QUEEN_B, os.path.join(REFD, 'sheet_west.png'), os.path.join(REFD, 'sketch_left.png')],
              SERIES + 'Image 3 is the character design of the woman in black and crimson, keep her face, her straight fringe, the braid over her crown and the big black ribbon, her golden eyes, the small red star-shaped mark on her forehead, her pointed ears and her diamond earrings. ' + SHEETN + SKETCH + CLEAN + ACTION +
              'A tall portrait picture, aspect ratio 7:10. The right edge of the picture will sit against a dark window, so everything important stays inside the picture. The top tenth of the picture is plain sky, it will be covered. '
              'The world is black obsidian and ash: a charcoal sky with fine straight slanted grey rain and flakes of pale ash, flat layered banks of ash-grey mist, the only colours are the people. Under everything lies an immense chessboard of black obsidian and white stone with thin gold lines; it has been shattered, and huge tilted square slabs of it hang in the air and rise toward the upper left, and the generals stand and leap on them. '
              'THE QUEEN, large at the lower right, is the heart of the picture: she has just slammed down the king. Her whole body lunges low over the board on a steep diagonal, her right arm in its long black glove driven straight down at full stretch, the fingers crushing a black chess king with a small plain crown of dull gold onto the board at the lower middle of the picture. Where the piece strikes, the board cracks open in a ring of gold-lit fractures and the squares around it jump upward. Her long silver hair and her crimson half-cape are blown up and back by the blow in great sweeping shapes. She wears a black gown and a dull gold orichalcum corset and a high-collared black coat with a crimson lining. Her golden eyes are wide open and burning, looking down at the piece, brows drawn, teeth just showing, with one tear flying from her eye. '
              'BEHIND HER, THE TEACHER, a tall woman of about thirty with very short brown hair going grey, has flung both arms around her from behind and holds on with everything she has left, one forearm across her collarbone and the other hand gripping her at the waist, her cheek pressed hard against the silver hair, eyes shut, a small fierce smile. She wears a washed-white old army greatcoat half burnt away, and her bare forearms and face are crossed with fresh red wounds. Her back and her outer shoulder are coming apart: cloth, skin and hair break up into a great rushing stream of pale ash and flakes of gold light that pours away up and to the right, and this stream is the brightest thing in the picture. '
              'ABOVE THEM, THREE COLOSSAL DEAD-WHITE GODS ARE BEING TORN APART. The gods are enormous pale flat layered shapes in low-contrast ash greys, almost part of the sky, and only the seven people on them carry strong colour. Each of the seven is wrenching one glowing thing out of a god. '
              'THE CHAIN GOD fills the upper right, as in the sheet: a hunched colossus of grey stone wrapped in loop after loop of chain, rearing up out of a pit, its face a single smooth oval plate of dull gold orichalcum with no eyes and no mouth, now cracked across; one long arm reaches down to the left and ends in a hand whose five fingers are five huge pincers. On it, three people: '
              'VALDRAK falls on it from above, a man with deep grey skin and wild long black hair, the left horn gleaming black and the right horn broken with molten red cracks, wearing a black and crimson greatcoat that blows up over him: head down and both hands on a long-hafted heavy blade, he has rammed it to the guard into the god\'s shoulder, blue-white flame bursting out along the blade, and a white-hot iron shackle tears out of the wound. '
              'GROM, a mountain of a man, bronze skin crawling with bright violet lightning scars, huge bull horns with heavy metal rings, wild black hair and beard, bare chest wrapped in orichalcum chains and dark purple and gold plate: feet braced on a tilted slab, leaning back at full strength with a chain over his shoulder, roaring, he drags the god\'s pincer hand down, violet lightning racing along the chain and an iron ring bursting off its wrist. '
              'SIRENTIA rises at the god\'s flank near the right edge on the crest of a dark sea that has come up out of nowhere, drawn as big flat curving layers of deep blue water with pale foam: wet deep-blue hair flying up, iridescent scales along her cheekbone and neck, a pearl-coloured gown soaked and clinging to nothing, one arm flung high with the palm cut open, an arc of blood going into the water, and a single shining grain of salt in that palm. '
              'THE NAME GOD stands at the left of the middle: a towering column of wrapped grey cloth with no face at all at the top, and pale human faces with open mouths rising up through the folds. Two people on it: '
              'LYSIA whirls around it in mid-air, flung nearly horizontal, silver-white hair with a black ribbon and thorns in it, crimson eyes and a dangerous smile, a crimson gown flaring and black lace gloves: with both hands she hauls on a long thread of blood-red thorns that she has stitched in a spiral round and round the column, and the grey cloth is ripping open along it; a blank white wax tablet tumbles out of the tear toward her. '
              'MORTUS strides on a slab below, a gaunt young man with short black hair, very pale skin, amber gold eyes and a line of white crystal bone showing at his left jaw, in a black high-collared coat with white under-robes that flies out behind him: with both arms he swings a heavy bronze bell on a short chain in a huge arc at full stretch, and pale flakes that were names and little faces stream out of the grey cloth toward the bell. '
              'THE HUNGER GOD is in the upper left: a gaunt yellowed giant, nothing but a skeleton, ribs propping up a huge empty belly that is a dark pit, its open mouth growing downward beneath the ribs. Two people on it: '
              'SELEPHIEN comes down through it in a power dive on a long straight line from the upper right, a lean young man with short dark blue hair, sharp teal eyes and a black high-collared flying coat, six uneven wings swept back behind him, dark as smoked glass at the root and turning to streaming teal light and wind at the tips, a copper bell flying from his belt; he goes through the ribs like a thrown spear and they burst apart around him. '
              'NEPHRA falls into the pit from the left, a slight woman with long deep violet hair whose ends turn into stardust, violet eyes and layered black and violet veils all streaming upward as she drops; she thrusts out a hand mirror at arm\'s length into the dark of the god\'s belly, and the mirror is exploding into long sharp shards of cold light. '
              'Keep the seven people clear and readable against the pale gods, like figures in a stage set, each with space around them, and let the mist and rain fill the rest.'),
})

JOBS.update({
    # right2 的人和动作留下，天照头一稿切干净（那一道直光要一直走到右边，光上全是半夜），教堂换回一把椅子
    'right3': ([os.path.join(OUT, 'right2.png'), os.path.join(OUT, 'fix', 'throne.png')],
               'Image 1 is a finished illustration: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. Repaint image 1 with the same aspect ratio and the same framing, keeping every person, every face, every pose, every costume, the sword, the stairs, the crowd with torches, the angels, the roots, the forge, the flag and all the cloth exactly as they are, in the same place and at the same size, in the same drawing style and colours. Only two things change. '
               'First, the sky is cut in two by one perfectly straight, razor-thin line of blinding white-gold light. It runs from the upper left corner along the blade of the sword, passes behind the swordswoman\'s body and behind her white mantle, and continues dead straight at exactly the same angle all the way to the right edge of the picture, where it arrives at about 57 percent of the height of the picture, just above the man on the horse. Everything above and to the right of that line is flat deep indigo and violet midnight with a few small stars, with no rose or pink in it at all, so the white mantle now stands out brightly against the dark. Everything below and to the left of that line is already dawn: rose, pale gold and white, as if the night had been sliced off. The edge between them is clean and straight, no clouds cross it. '
               'Second, the gothic cathedral at the upper left is replaced by an immense throne, unmistakably a chair as tall as a cathedral, drawn like the throne in image 2: a very tall straight back of white stone and pale gold, two broad armrests, a deep seat and a stepped dais, with no windows, no doors, no towers. The line of light passes straight through the tall back: the whole upper piece has been sheared off cleanly and is sliding away up and to the right along the cut and tipping over, with a clear gap of dark sky between the two cut faces and blocks of white stone bursting from the cut. The two falling halves of the crown stay where they are. '
               'No text, no logo, no frame, no crescents, no moon phases.'),
})

KEEP_ALL = ('Image 1 is a finished illustration: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. Repaint image 1 with the same aspect ratio and the same framing, keeping every other person, face, pose and costume and everything else in the picture exactly as it is, in the same place and at the same size, in the same drawing style and colours. Only one thing changes. ')
JOBS.update({
    # 用户回：巴尔缇娜与索恩薇娅的动作第一版不错，其他的保留二板。人照立绘（盘发、白金披风），动作照头一稿（ref/pose_thornevia、pose_queen 是头一稿裁的）
    'right4': ([os.path.join(OUT, 'right3.png'), os.path.join(REFD, 'pose_thornevia.png')],
               KEEP_ALL + 'The tall swordswoman in the white mantle changes her pose. Image 2 shows the pose she must have and how she stands: tall, perfectly upright and steady at the top of the stair, facing us, her torso frontal and square, chin raised, her sword arm stretched straight out to the upper left at full length, holding the plain old sword in one hand by its hemp grip with the blade lying exactly along the line of light, her other arm down at her side. Her head is turned a little toward the sword and her face is calm, resolved and unsmiling, pale gold eyes looking straight along the blade. Both her legs are straight and both feet stand on the top step, in long black boots: there is no lunge and no leg flung out behind her any more, and the line of light and the night sky and dawn continue where that leg used to be. Her sword hand and the sword stay exactly where they are now in image 1, and she is as tall in the picture as she is in image 2. '
               'Keep her own face, her chestnut brown hair in the big braided chignon at the back of her head with the long side locks blowing back, and her own costume from image 1: the white high-collared mantle with gold edges and small gold stars, black under-suit and sleeves, gold breastplate, gold cord at the waist. Take only the pose from image 2, not its hair, coat, colours or anyone else in it. The great white mantle still cracks out behind her to the right in a huge sweeping arc against the night, exactly as it does now. No text, no logo, no frame, no crescents, no moon phases.'),
    'left3': ([os.path.join(OUT, 'left2_fixed.png'), os.path.join(REFD, 'pose_queen.png')],
              KEEP_ALL + 'The two women at the lower right change their poses to those in image 2, and they are drawn at the same size and in the same place as they are in image 2, which is the lower right part of the picture from a little above two thirds of its height down to the bottom edge, with the chess king at the lower left of them. '
              'The woman with long silver hair sits half reclining, leaning back into the taller woman behind her, with a quiet, terrible calm. Her head is bowed a little, her golden eyes half lowered and looking down at the piece, her mouth closed, no snarl, no teeth, no tear. Her arm in its long black glove is stretched out low to the left, and her gloved fingers rest on the top of a black chess king as she sets it down on the board. Her long silver hair falls and streams to the left, and her crimson half-cape spreads out over the board to the left in big sweeping shapes. Keep her face design from image 2: straight fringe, the braid over her crown, big black ribbon, small red star-shaped mark on her forehead, pointed ear, diamond earring, black gown with dull gold corset, high-collared black coat with a crimson lining. '
              'The taller woman behind her has both arms around her from behind, one scarred bare forearm coming down across her body with the hand resting in her lap on the crimson cloth, her cheek laid on top of the silver hair, her eyes closed and a small peaceful smile. Her face and her forearms are crossed with fresh red wounds. Her short brown hair goes grey at the temples. She wears the washed-white old army greatcoat half burnt away, and her back and her outer shoulder are coming apart into flakes of pale ash and gold light that drift away to the right and upward. '
              'The chess king has a small plain crown of dull gold at its top, with no cross. Around its foot the black and white board still has a few fine gold-lit cracks. The cape and hair pass in front of the broken slabs but stop before the foot of the man with the bell, and everyone else stays exactly as they are in image 1, including the woman in the sea, whose lower body now goes behind the short brown hair. Take only these two women and the king from image 2, none of the other people in it. No text, no logo, no frame, no crescents, no moon phases.'),
})

JOBS.update({
    # 用户说 right4 的索恩薇娅看着怪：比头一稿小了将近四成，两条腿笔直并排露着。底是 bronze_collage.py 把头一稿的她贴回来的，守住大小和姿势，头发和衣服换回立绘
    'right5': ([os.path.join(REFD, 'collage_thornevia.png'), os.path.join(REFD, 'p_thornevia.png')],
               'Image 1 is a finished illustration: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. The tall swordswoman in the upper middle has been roughly pasted into it from an earlier draft, at the right size and in the right pose, and her clothes do not match yet. Repaint image 1 with the same aspect ratio and the same framing, keeping every other person, face, pose and costume and everything else in the picture exactly as it is, in the same place and at the same size, in the same drawing style and colours. '
               'Redraw only the swordswoman. Keep exactly the pose, the size and the proportions she has in image 1: the same large head, the same broad soldier\'s shoulders and solid body, standing square and upright with her chin raised, her arm stretched straight out to the upper left holding the old sword, and her other arm down at her side. Her calm, resolved face with pale gold eyes stays as it is in image 1. Do not make her slimmer, smaller or longer in the leg. '
               'Give her the hair and clothes of the character design in image 2, redrawn in the flat style of image 1: chestnut brown hair in a big braided chignon at the back of her head, a fringe and long side locks blowing back to the right. A high white collar and a white scarf at the throat, a gold breastplate with small stars over a black under-suit with black sleeves, and over them a long open white military coat with gold edges and small gold stars. The long white coat falls straight down in big plain folds in front of her legs and hides them completely, and it goes down behind the flag and behind the wild black hair of the woman shouting below: no legs, no boots, no feet and no steps show under her. The great white mantle from her shoulders still cracks out behind her to the right in a huge sweeping arc against the night, joined to her shoulders. She has no crown. '
               'Remove anything left over from the old figure. No text, no logo, no frame, no crescents, no moon phases.'),
})

JOBS.update({
    # 用户又说她还是怪：right5 叫 GPT 照立绘重画，胳膊像从胸口长出来，身子又直又窄，一身白贴在浅色台阶上发虚。这回不重画，头一稿的她一根线不动，只换发型和配色，深红的里子留着压分量
    't1': ([os.path.join(REFD, 'pose_thornevia.png'), os.path.join(REFD, 'p_thornevia.png')],
           'Image 1 is a finished illustration: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. Repaint image 1 with the same aspect ratio and the same framing, keeping the drawing of the standing swordswoman exactly as it is: the same pose, the same proportions, the same shoulders and arm, the same head size and angle, the same face and expression, the same folds and outline of every piece of cloth, the same belts, in the same place and at the same size, and everything else in the picture untouched. This is a recolouring and a change of hairstyle, not a redrawing. Only these things change, and image 2 shows the character they come from. '
           'Her hair: chestnut brown, smooth and straight, gathered into a big braided chignon at the back of her head, with a straight fringe falling over her forehead and two long side locks falling in front of her shoulders, a few strands lifting in the wind. Remove the old wavy hair and the old low ponytail. '
           'Under her eye a fine thin scar runs down her cheek, as in image 2. '
           'Her long open coat and the outer face of her mantle change colour from cream and dull brown to clean white, with thin gold edges and two or three small gold stars, and a small gold star on the lapel. The inner lining of the coat and mantle stays a deep dark wine red, so the figure keeps its weight. Her sleeve becomes black with thin gold bands at the cuff. The patch of chain mail on her chest becomes a gold breastplate with a fine pattern of small stars, keeping the same shape and the same belts below it, and the shirt under the collar becomes black with a white scarf at the throat. '
           'Her skin, her pale gold eyes, her hand, the old sword, the sky, the line of light, the crown, the stairs, the flag, the two women at the bottom and the city at the right do not change at all. No text, no logo, no frame, no crescents, no moon phases.'),
})

JOBS.update({
    # t1 贴回右扇（bronze_collage.py 拼的底）。她一根线不动，只把接缝和天收干净
    'right6': ([os.path.join(REFD, 'collage2.png')],
               'Image 1 is a finished illustration: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. Its upper part, with the tall swordswoman, her white coat with the dark wine-red lining, the sky and the distant city, has been pasted in from another draft. Repaint image 1 with the same aspect ratio and the same framing, keeping every person, face, pose and costume exactly as it is, in the same place and at the same size, in the same drawing style. Above all keep the swordswoman exactly as she is: the same pose, the same proportions, the same head, face, hair and hand, the same coat and every fold of it. Only tidy up these things. '
               'First, make the join seamless. Remove every left-over piece of an older version of her: stray white coat tails, gold edges and belts below her, and any stair steps showing directly under her. Her long coat and its dark wine-red lining simply continue straight down behind the stitched flag and behind the wild black hair of the shouting woman, and her great white mantle with its wine-red lining sweeps away to the lower right behind the flag and behind the man on the horse. The old sword in her hand joins cleanly to its long blade at the upper left. '
               'Second, make the sky one thing. Everything above the line of light is one flat deep indigo midnight with a few small stars, the same colour as the upper left corner, with no purple haze. The line of light is one perfectly straight, razor-thin line of blinding white-gold light that comes out from behind her shoulder and runs dead straight to the right edge of the picture, passing behind the city and banners. Below the line it is dawn: rose, pale gold and white. Keep the pale city with its spires and its white banners at the right, in the same place. '
               'The throne, the falling crown, the stone fragments, the stairs, the torch crowd and all the people in the lower half do not change at all. No text, no logo, no frame, no crescents, no moon phases.'),
})

JOBS.update({
    # right6 又把她拉长了（下半身露得太多，九头身）。头一稿下半身早早藏进人群，所以比例好看。这回把她单独抠出来，贴到干净的底上，不再叫 GPT 碰她
    't1_cut': ([os.path.join(OUT, 't1.png')],
               'Image 1 is a finished illustration: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. Repaint image 1 with the same aspect ratio and the same framing on a fully transparent background, keeping only the tall swordswoman exactly as she is drawn: the same pose, the same proportions, the same head, face, hair, hand and hilt of the old sword, the same coat, breastplate and belts, and every fold, in the same place and at the same size. Do not redraw her and do not make her longer or slimmer. Remove everything else completely: the sky, the stars, the line of light and its glow, the city and banners, the crowd, the stairs, the crown, the stitched flag and its pole, and the two women at the bottom. Where the flag and the two women used to hide her, her long coat simply continues straight down in plain folds with its dark wine-red lining until the bottom edge of the picture, and her mantle continues to the lower right corner. Everything around her is fully transparent, with no background and no halo. No text, no logo, no frame.'),
    'plate6': ([os.path.join(OUT, 'right6.png')],
               'Image 1 is a finished illustration: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. Repaint image 1 with the same aspect ratio and the same framing, keeping every other person, face, pose and costume, the throne, the falling stone blocks, the torch crowd, the angels and the distant city and banners exactly as they are, in the same place and at the same size, in the same drawing style and colours. '
               'Remove completely the tall swordswoman in the white coat: her body, head, hair, arm, hand, coat, wine-red mantle and everything of hers, leaving only the long blade and cross guard of the sword lying on the line of light at the upper left. Remove the two small gold pieces at the right edge of the picture. Remove the stitched flag but keep the wooden pole in the shouting woman\'s fist. Where she stood, fill in what is behind her: above the line of light one flat deep indigo midnight sky with a few small stars; a perfectly straight, razor-thin line of blinding white-gold light with a soft glow, running from the cross guard of the sword straight to the right edge of the picture at about 43 percent of its height, passing behind the city; below the line, dawn in rose, pale gold and white, with a few soft flat clouds; and the broad white stairs climbing up empty to their top step, joining the stairs on the left. Nothing stands on the stairs in the middle. No text, no logo, no frame, no crescents, no moon phases.'),
    # 旗从 right4 抠出来（那一张的旗是干净的，上头没有她的下摆）
    'flag_cut': ([os.path.join(OUT, 'right4.png')],
                 'Image 1 is a finished illustration. Repaint it with the same aspect ratio and the same framing on a fully transparent background, keeping only the ragged stitched white flag with the clumsy white raven on it and its wooden pole, from the top of the pole down to the shouting woman\'s fist, exactly as drawn, in the same place and at the same size. Remove everything else completely, including the woman and her hand, so everything around the flag and pole is fully transparent, with no background and no halo. No text, no logo, no frame.'),
})

JOBS.update({
    # 底上打磨过的人抠一层出来，压在她的外套和披风上面（她站在他们后头）
    'front_cut': ([os.path.join(OUT, 'plate6_fixed.png')],
                  'Image 1 is a finished illustration. Repaint it with the same aspect ratio and the same framing on a fully transparent background, keeping only these people, exactly as they are drawn, in the same place and at the same size, with every strand of their flying hair and every piece of their cloth: the elf queen at the left with the living roots and branches around her; the shouting woman in leather armour with her sword and her wooden pole; the man on the galloping brown horse with his lance; the beast-eared archer; the dwarf with the sledgehammer; the crying woman with silver-grey hair; the dwarf king with his hammer, anvil and sparks; the elf mage with her staff and the band of silver marks; and the barefoot youth with the sheaf and the stream of golden seeds. Remove everything else completely: the sky, the line of light, the throne, the stone blocks, the city, the banners, the angels, the torch crowd, all the stairs, the walls, the furnace, and the pale cloth shapes at the bottom right. Everything around these people is fully transparent, with no background and no halo. No text, no logo, no frame.'),
})

# 用户看了 t2 回：严格照白厄那张的镜像，其他地方细看还是不自然，最大的问题是姿势、人体和比例。t2 作废。图裁自 back_view_pose.webp，左右翻过来
MIRROR = os.path.join(REF, 'back_view_mirror.png')
JOBS.update({
    't3': ([MIRROR, os.path.join(REFD, 'p_thornevia.png'), os.path.join(OUT, 't1_cut.png')],
           'Image 1 is the exact pose to copy, and it must be copied strictly. Repaint image 1 with the same aspect ratio and the same framing, and keep every contour of the figure where it is: the figure stands in exactly the same place and at exactly the same size in the picture, with exactly the same proportions. The same head size and the same narrow shoulders. The same arm raised high on the left of the picture, bent at the elbow, with the hand just above the height of the head. The same long sword rising from that hand at the same steep angle, up and to the left. The same other arm hanging at the side, a little away from the body, with the fist at the hip on the right of the picture. The same long straight coat falling to just above the ankles. The same sash flying out to the left from the shoulders and the same layered coat tails flying out to the left from the hip, in the same places. The same two feet close together, standing evenly. Do not widen the stance, do not enlarge the coat, do not lengthen or thin anything, do not change the angle of anything. '
           'Only the person, her clothes and the drawing change. It is a woman soldier seen from directly behind, her face turned away. Her hair is the colour of image 2: chestnut brown drawn back smoothly and wound into one big braided bun at the back of her head, with two long thin loose locks blown out to the left. A high white collar with a thin gold edge, and the end of a white scarf. A short shoulder cape of deep wine red with a thin gold edge and small gold stars, sitting on both shoulders where image 1 has its dark shoulder cape. A black sleeve with thin gold bands at the cuff on the raised arm, and a black sleeve on the hanging arm. A long white military coat with thin gold edges and soft lilac-grey shadows in its folds, a straight vent up the back showing a dark wine-red lining, and a brown leather belt with hanging straps at the waist. The flying sash is white with a gold border, and the flying coat tails are layers of dark wine red and pale gold. Long dark boots. The sword is a plain old straight sword: a long narrow blade of pale steel, a plain iron cross guard, a grip bound in hemp, with no ornament at all. '
           'Draw it in the style of image 3, not the style of image 1: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte, a clean Japanese game illustration. Everything around the figure is fully transparent: no sky, no arch, no ground. She has no crown. No text, no logo, no frame, no crescents, no moon phases.'),
    # 人物以后一个人一张抠好贴上来，这张只留台阶、王座、光线和远处的城。旧剑也擦掉，她手里那把才是剑
    'plate7': ([os.path.join(OUT, 'plate6.png')],
               'Repaint this illustration with the same aspect ratio and the same framing, keeping the whole upper part exactly as it is, in the same place and at the same size: the deep indigo night sky and stars, the razor-thin straight line of white-gold light and the rose and pale gold dawn below it, the sliced gothic throne with its flying pieces of white stone, the angel statue, the red banner, the small hooded torch bearers on the stairs at the upper left, the distant pale city with its banners at the right. '
               'Make two changes only. One: remove the long sword and its cross guard lying along the line of light. The line of light stays perfectly straight, and the two halves of the throne are seen cleanly along it. Two: remove every large figure in the lower part of the picture: all the people, the roots and leaves, the anvil and furnace, the flag, the coloured ribbons, the sparks and the seeds. In their place the same wide flight of pale white stairs simply continues evenly, with the same step lines, all the way down to the bottom edge of the picture and from the left edge to the right edge, with nothing on it. Same flat cut-paper drawing style with very fine parallel hatching. No text, no logo, no frame, no crescents, no moon phases.'),
})


# 左扇也拿掉七个人，留巨神、棋盘、海和她们俩
JOBS['plate_l'] = ([os.path.join(REFD, 'left3_small.png')],
                   'Repaint this illustration with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size, except that seven people are removed: the winged man diving at the top, with his wings and his bell; the horned man kneeling on the great stone arm, with his blade and its blue flames and his red coat; the woman with the hand mirror inside the ribs of the skeleton, with her purple veils and the shards; the huge horned man hauling on the chain in the middle, while the chain itself stays, from the broken gold ring down to the place where his hands were; the woman in crimson in front of the grey column, with her red gown and red thorn threads; the woman rising from the blue sea at the right, while the blue swells stay; and the young man in black with the bronze bell at the lower left, with the bell and the pale flakes around it. Where they were, the same grey rain and ash-grey mist, the bones of the skeleton, the grey wrapped cloth of the column, the stone arm and the broken stone slabs simply continue. Keep exactly as they are: the giant skeleton with its skull, the giant column of wrapped grey cloth with the faces in it, the giant stone arm with its chains and cracked gold plate and pincers, the blue sea, the stone slabs, the chessboard floor with its gold cracks, and the two women at the lower right with every detail of their faces, hair and clothes and the chess piece. Same flat cut-paper drawing style with very fine parallel hatching. No text, no logo, no frame, no crescents, no moon phases.')

# 再拿掉她们俩：两张一减就是她们的遮罩，头发丝也留得住。别的人贴在她们后头
JOBS['plate_l2'] = ([os.path.join(OUT, 'plate_l.png')],
                    'Repaint this illustration with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size, except that the two women at the lower right, and the chess piece under the gloved hand, are removed, with all of their long hair, the red cape, the torn white coat and the golden flakes. Where they were, the same grey rain and ash-grey mist, the deep blue sea with its swells and the broken stone slab simply continue, and the black and white chessboard floor with its gold cracks continues along the bottom of the picture. Same flat cut-paper drawing style with very fine parallel hatching. No people at all. No text, no logo, no frame, no crescents, no moon phases.')

# 用户看了 t3 回“腿部站姿修一下”：两只靴子并得太紧、笔直，像娃娃。只改腿
JOBS['t4'] = ([os.path.join(REFD, 't3_grey.png'), MIRROR],
              'Image 1 is a finished character drawing on a plain grey background. Repaint image 1 with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size: the head and hair, the raised arm and the sword, the shoulder cape, the sash, the belt, the white coat and all its flying tails. Change only the legs and boots below the hem of the coat, which are stiff and too close together, like a doll. '
              'She now stands with a natural, relaxed and strong stance, seen from directly behind, on a flight of stairs, with her feet about shoulder width apart, like the spacing of the legs in image 2. Her left leg, on the left of the picture, steps up on to the next stair: the knee a little bent, the boot a little higher in the picture and pointing slightly to the left. Her right leg, on the right of the picture, carries her weight: it comes down straight from under the coat where the wine-red lining shows, the boot lower in the picture and turned slightly outward to the right. Each long dark boot has a natural calf: fuller at the calf, narrowing to the ankle, with a heel and the sole seen from behind. The legs are of natural length and thickness. '
              'Same drawing style: flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte. Everything around the figure is fully transparent: no grey, no stairs, no ground, no shadow. No text, no logo, no frame, no crescents, no moon phases.')


# 第四稿。用户看了第三稿说还是怪，贴上去的效果也怪：“保留巴尔缇娜那个，其他你自己看着改吧，就一个底图”。所以一扇只要一张画，不再叠人。
# 群像是 AI 画不好的地方，就不正面画：右扇只有她一个主角，传奇是台阶底下背对镜头的剪影，靠手里的东西认人（第五稿 plate8）；左扇七个人缩成巨神身上很小的影子，越小巨神越大（l5）。
UNIFY = ('Flat cut-paper shapes, smooth clean colour with very fine parallel hatching, thin coloured outlines, matte, a clean Japanese fantasy game illustration. No text, no logo, no frame, no crescents, no moon phases.')
JOBS['l5'] = ([os.path.join(OUT, 'plate_l2.png')],
              'Repaint this illustration as one single unified finished picture with the same aspect ratio and the same framing, keeping everything where it is: the charcoal sky and grey rain, the giant skeleton with its skull and ribs, the giant column of wrapped grey cloth with faces in it, the giant stone arm with its chains and cracked gold plate, the blue sea, the broken stone slabs and the chessboard floor with its gold cracks. Give it aerial perspective: the giants fade softly into the rain and mist, paler and with less contrast, so that they feel enormous and far away. '
              'Add seven very small figures, each no taller than about one fifteenth of the height of the picture, so small that they are nearly silhouettes with no faces and no details, each with one small touch of colour, like ants on a colossus. A dark horned man kneeling on top of the stone arm, driving down a blade with a tiny blue-white flame. A huge dark horned man on the stone slab in the middle, leaning back and hauling on the chain, which runs taut from him up to the stone arm. A woman waist-deep in the blue sea with one arm raised and a tiny thread of red. A woman among the ribs of the skeleton holding up one tiny point of violet light. A tiny figure with dark wings flying beside the skull, with a thin trail of teal light. A tiny figure in crimson in front of the grey column, and one thin red thread winding round the column from her hand. A tiny dark figure on the chessboard at the foot of the column, swinging a bell with one tiny glint of bronze. ' + UNIFY)


SEA_BOX = (770, 660, 1049, 912)
# 海里那个小人叫薇瑟兰挡住了（她在 l5 的 (830, 1040)），在看得见的那片海上再画一个，旧的那个在她们后头。裁的是 sea_in
JOBS['sea'] = ([os.path.join(REFD, 'sea_in.png')],
               'Image 1 is a crop of a finished illustration of a stormy blue sea. Repaint it with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size, adding only one thing near the middle of the crop: one very small woman waist-deep in the blue water, nearly a silhouette, with long dark hair, no face and no details, about one fifth of the height of this crop, her one arm raised high, with a tiny thin thread of red falling from her raised hand. Same flat cut-paper drawing style with very fine parallel hatching. No text, no logo, no frame.')


# 摇钟那个小人的腿叫披风盖住了，也在看得见的地方再画一个，旧的擦掉。裁的是 bell_in
BELL_BOX = (70, 1120, 340, 1330)
JOBS['bell'] = ([os.path.join(REFD, 'bell_in.png')],
                'Image 1 is a crop of a finished illustration of grey mist above a floor of broken stone slabs. Repaint it with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size, adding only one thing near the middle of the crop, standing on the stone: one very small dark figure in a long coat, nearly a silhouette, with no face and no details, about a quarter of the height of this crop, his coat flying as he swings a small bronze bell on a short chain out to the left, with one tiny glint of bronze. Same flat cut-paper drawing style with very fine parallel hatching. No text, no logo, no frame.')


# 第五稿。用户看了第四稿说：“索恩薇娅的服饰可以进行一下调整，更符合她的设定，同时修复一下左手。右边的感觉可以参考一下崩铁的《黄金史诗翁法罗斯英雄谭》pv”。
# 那一夜她还不是皇帝，是叫冠台判成逆军的南线营官（主线七年巡礼的旅伴条）：领章自己撕了的旧外套、肩上补过四回的旧皮甲、旧皮带、麻绳缠柄的旧剑、腰后的布袋，右手背一大片烫伤。t5a 照这个，配色留着立绘的白金和旧铜；t5b 是登基以后的（#874：白金旧铜的军礼服、黎明色的长军袍、山铜链甲）。PV 那几帧放在 语料/，不进库。
T4_GREY = os.path.join(REFD, 't4_grey.png')
PV_BACK, PV_GOLD, PV_RED = (os.path.join(REF, n + '.png') for n in ('pv_back_detail', 'pv_gold_colossus', 'pv_red_temple'))
T5_HEAD = ('Image 1 is a drawing of a woman seen from directly behind, holding a sword up high. Image 2 shows the hair colour and the palette of this character. Image 3 shows only the level of finish I want for the clothes: crisp anime drawing with rough dry-brush texture in the cloth; do not copy that costume. '
           'Repaint image 1 with the same aspect ratio and the same framing, keeping exactly the same pose, the same proportions, the same stance, the same head and the same braided bun of hair in old-copper dark gold-brown, the same raised arm and the same place in the picture. Change only her clothes, her sword and her two hands. ')
T5_TAIL = ('Her sword, in her raised left hand, is a plain old straight longsword of dull grey steel with a simple straight iron crossguard and a grip wound with rough hemp cord. No ornament, no jewel. Blade, crossguard, grip and pommel form one straight line. '
           'Her raised left hand is bare, strong and of natural size, about as large as her face, with a natural wrist: a firm fist closed round the hemp grip directly below the crossguard, seen from behind, with the back of the hand and the four knuckles clearly visible, four fingers wrapped round the grip and the thumb locked over them. Her sleeve slides a little down her raised forearm. Her right arm hangs a little away from her body and ends in a bare relaxed fist of natural size, with five clearly separated fingers and a large pale burn scar across the back of that hand. '
           'Everything around the figure is fully transparent: no background, no ground, no shadow. No text, no logo, no frame.')
JOBS['t5a'] = ([T4_GREY, os.path.join(REFD, 'p_thornevia.png'), PV_BACK], T5_HEAD +
               'She is not a queen: she is a front-line infantry officer from the slums, who has worn the same clothes for seven years on the march. She wears one long plain army greatcoat with a straight military cut, of washed-out ivory white cloth gone grey in the folds, with a narrow trim of tarnished old bronze, faded and mended in places, its hem frayed, ending at mid-calf. It has a stiff high collar, and on the collar are the two torn patches where she ripped off the rank badges herself, with loose threads. Over the shoulders of the coat she wears a short old harness of dark brown leather with a plain pauldron on each shoulder, visibly patched with four pieces of different leather and thick stitches. Round her waist is one wide old leather belt polished by years of wear, with a plain iron buckle, an empty plain leather scabbard hanging at her left hip, and a small grey cloth bag at the small of her back. The coat is split up the back from the waist, and its two long tails fly out to the left in a strong wind, in two large simple shapes, showing plain dark trousers and tall scuffed brown boots. A long strip of old patched sailcloth tied at her neck as a scarf flies out to the left. There is no dress, no gown, no layered skirt, no red, no yellow panels, no stars, no gold embroidery, no jewels, no earrings. ' + T5_TAIL)
JOBS['t5b'] = ([T4_GREY, os.path.join(REFD, 'p_thornevia.png'), PV_BACK], T5_HEAD +
               'She wears the strict military dress uniform of a ruler who refuses ornament: a straight-cut tunic in white-gold and tarnished old bronze, with a stiff high collar, straight square shoulders and clean regulation lines, with only one small golden kite crest at the back of the collar and at each cuff. Over it she wears a long military coat in the colour of dawn: deep indigo at the shoulders, passing through violet and rose to warm gold at the hem, heavy plain cloth with a thin bronze edge. The coat is split up the back from the waist and its two long tails fly out to the left in a strong wind, in two large simple shapes, and on the inside of one flying tail we see that the lining is pale and covered with thin hand-drawn lines like an old street map. Fine copper-gold chain mail glints just below the tunic at the hips. Round her waist is one wide old leather sword belt polished by years of wear, with a plain iron buckle and an empty plain leather scabbard at her left hip. Plain dark trousers and tall plain boots. There is no dress, no gown, no layered skirt, no red, no stars, no jewels, no earrings. ' + T5_TAIL)


# PV 的路子：大块的硬边色块上刮着干笔和颗粒，竖着往下淌的颜料，只有靛紫、琥珀金、一点暗玫瑰和近黑的剪影，大东西画成破碎的面。那一轮圆弧不搬（不写月相），这里的天只叫一道直线切开。
PV_STYLE = ('The art direction: a Japanese animated film poster, painted with big graphic masses of flat colour with hard edges, roughly scumbled with dry-brush and grunge paint texture, with long vertical streaks and drips of paint running down the big fields of colour, like paint scraped across a wall. Very high contrast and a strongly limited palette: deep ultramarine-violet going almost black, blazing cadmium amber-gold, a little dusky rose, and near-black silhouettes. The big forms are drawn as broken faceted planes. Hard rim light. No soft airbrush, no fine hatching and no thin outlines on the background. ')
PV_END = ('Do not copy the giant curved disc in the reference: this sky is cut by one straight line only. No crescents, no moon phases. No text, no logo, no frame.')
JOBS['plate8'] = ([os.path.join(OUT, 'plate7.png'), PV_GOLD, PV_RED],
                  'Image 1 shows the layout of a picture. Images 2 and 3 are frames from an animated film, given only as a reference for the art direction; do not copy their subjects, their figures or their shapes. Repaint image 1 with the same aspect ratio and the same framing, keeping the layout: one razor-straight line of white-gold light running from the upper left down to the right edge, the throne at the upper left cut through by that line, the wide stairs rising to it, and the far city on the right. ' + PV_STYLE +
                  'Above the line: the deep ultramarine-violet night, almost black at the top, with drips and scumble and a few small stars. Below the line: a huge field of blazing amber-gold dawn with vertical streaks, passing into dusky rose and violet lower down. The throne is colossal, as large as a cathedral, a wreck of pale stone and tarnished olive-gold in broken faceted planes, sliced clean along the line of light: the part above the line lifts away and bursts into sharp shards of pale violet stone flying up into the night. The stairs are enormous dark violet planes scraped with dry-brush, each step with a hard edge of gold light, falling almost to black at the bottom of the picture, with an empty clear space in the middle of the stairs where a figure will stand. A thin river of tiny torch flames climbs the left side of the stairs toward the throne, carried by tiny black figures. The city on the far right is one flat pale silhouette of spires. '
                  'At the very bottom of the picture, large near-black silhouettes seen from behind fill the foreground, with hard gold rim light along their edges and raised arms, looking up the stairs: from left to right, a very broad short dwarf heaving up a great hammer; a slender elf queen with a crown of branches; a stocky woman lifting a tall pole with a torn white flag bearing a black raven, the only pale thing among them; a lean archer with pointed beast ears raising a short bow with one small flame on it; an elf with two long tails of hair holding up a tall staff topped with an open gold ring; a youth with a sheaf of wheat on his back raising one fist. Their heads stay in the lowest quarter of the picture. ' + PV_END)


# t5a 太破了，像要饭的，那一夜她还是个带兵的营官。只收拾衣服：布干净一点，直的军服线条，白金旧铜的底子还看得出来，补丁留两三块，布袋小一点
T5A_GREY = os.path.join(REFD, 't5a_grey.png')
JOBS['t5c'] = ([T5A_GREY],
               'Repaint this drawing with the same aspect ratio and the same framing, keeping exactly as they are, in the same place and at the same size: the pose, the head and the braided bun of hair, the raised arm, the sword, both hands, the leather harness with its patched pauldrons, the belt, the scabbard, the trousers and the boots. Change only the coat, the scarf and the cloth bag. '
               'The coat is still an old faded army officer\'s greatcoat, but it is in better repair and it reads as a soldier\'s coat, not as rags: clean strong straight military lines, ivory white cloth (not grey-brown), a narrow trim of tarnished old gold-bronze along every edge, the cuffs and the hem. It keeps the stiff high collar with the two torn places where the rank badges were ripped off. Only two small neat patches and one short line of stitching on the whole coat, and the hem is only slightly worn, not torn to shreds. Its two long tails still fly out to the left in two large simple shapes. '
               'The scarf is one long strip of plain off-white old sailcloth, with only one small patch and a slightly frayed end. The small grey cloth bag sits tight at the small of her back, under the belt, half hidden, no bigger than her fist. '
               'Same drawing. Everything around the figure is fully transparent: no background, no ground, no shadow. No text, no logo, no frame.')


# 她贴到 plate8 上，整张再画一遍，光才是一处来的。r11a 是那一夜的营官（t5c），r11b 是登基以后的军装（t5b）
HERO8 = dict(k=.62, x=100, y=60)
def r11_prompt(what):
    return ('Image 1 is a rough paste-up: a painted background with a figure pasted on it. Images 2 and 3 are frames from an animated film, given only as a reference for the art direction and for how the figure is painted; do not copy their subjects or their costume. Repaint image 1 as one single unified finished illustration with the same aspect ratio and the same framing, painted all at once in one light, with nothing looking pasted on. ' + PV_STYLE +
            'Keep the composition exactly as it is: the razor-straight line of light, the throne with its flying shards, the torch bearers, the stairs, the far city, and the group of silhouettes in the foreground with their hammer, crown of branches, raven flag, bow, ring staff and sheaf of wheat. Give the steps hard, irregular, broken edges of gold light, set wider apart toward the viewer, not ruled lines. '
            'Keep the woman seen from behind exactly as she is, in the same place, at the same size and in the same pose and proportions: ' + what + ' Paint her in crisp anime drawing with rough dry-brush texture in the cloth, as in image 2. Now light her with the scene: hard gold rim light along the edges of her raised arm, her sword, her hair, her shoulders and her flying coat tails, and her shaded side falling into cool indigo-violet. The blade flashes where the line of light crosses it. A long dark shadow falls from her boots down the stairs toward the viewer and stops above the silhouettes. ' + PV_END)
COMP_A, COMP_B = os.path.join(REFD, 'comp_r11a.png'), os.path.join(REFD, 'comp_r11b.png')
JOBS['r11a'] = ([COMP_A, PV_BACK, PV_GOLD], r11_prompt('the raised left arm with its firm bare fist closed on the hemp grip, the plain old sword with its straight iron crossguard, the braided bun of old-copper hair, the two patched dark leather pauldrons and the harness, the long plain ivory army greatcoat with its narrow tarnished bronze trim and its two flying tails, the torn places on the high collar, the long strip of old sailcloth flying from her neck, the old leather belt with the empty scabbard, the dark trousers and the tall scuffed boots, one a stair higher, and the bare right fist with its pale burn scar. The ivory cloth takes gold on its lit planes and violet in its shadows.'))
JOBS['r11b'] = ([COMP_B, PV_BACK, PV_GOLD], r11_prompt('the raised left arm with its firm bare fist closed on the hemp grip, the plain old sword with its straight iron crossguard, the braided bun of old-copper hair, the straight military tunic, the long military coat going from deep indigo at the shoulders through violet and rose to warm gold at the hem, its two flying tails, the pale lining with thin lines like an old street map on the inside of one tail, the small gold crests at the collar and cuffs, the glint of chain mail at the hips, the old leather belt with the empty scabbard, the dark trousers and the tall boots, and the bare right fist with its pale burn scar.'))


# r11a 的台阶上金色刮痕太碎，跟人抢。台阶照 r11b 那样收：大块的暗紫，一级只留一道断续的金边
JOBS['r12a'] = ([os.path.join(OUT, 'r11a.png'), os.path.join(OUT, 'r11b.png')],
                'Repaint image 1 with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size, in the same painting style: the woman, her coat, her sword, her scarf, the sky, the line of light, the throne, the torch bearers, the far city and the group of silhouettes in the foreground. Change only the surface of the stairs, which are too busy with smears of gold and compete with her. Make the stairs as calm as the stairs in image 2: big dark violet planes with dry-brush texture, each step with only one thin broken line of gold light along its edge and only a few small scrapes of gold. Her long shadow stays. Image 2 is only a reference for the stairs: take nothing else from it. No text, no logo, no frame, no crescents, no moon phases.')


# 用户拍了自己的左手（语料/人物参考_11-04/left_hand_user.png，握着东西、从胳膊后头看）：从背后看是手背对着我们，四指绕到另一侧看不见指尖，拇指在靠头那一边，剑柄藏在手和手腕后头。
# 照片抠出手和手腕，转到她小臂的方向贴上去当底稿，旧的手和露在外头的剑柄先盖掉，裁下这一块叫 GPT 只画这只手。G 是拳头顶上剑柄穿出来的地方，写在画的像素上
HAND_BOX = (325, 305, 445, 425)      # 裁小一点，手占得大，手指才画得清楚
HAND_G = {'a': ((373, 348), (378, 354)), 'b': ((380, 348), (385, 354))}     # 旧的拳头顶、新的拳头顶（往下让一点，露一小截剑柄）
HAND_SRC = {'a': 'r12a', 'b': 'r11b'}
HAND_PHOTO = os.path.join(REF, 'left_hand_user.png')
HAND_TURNED = os.path.join(REFD, 'left_hand_user_turned.png')
HAND_TH = 27                          # 照片的小臂差不多竖直，她的往左歪 24 度
HAND_POLY = [(30, 758), (60, 680), (92, 600), (82, 552), (40, 500), (14, 430), (22, 340), (48, 285), (50, 240), (100, 205), (112, 185), (96, 150), (100, 130), (130, 122), (165, 140), (195, 150), (240, 190), (300, 215), (350, 235), (395, 225), (415, 195), (440, 185), (472, 215), (480, 260), (470, 340), (450, 420), (420, 480), (415, 540), (400, 620), (385, 758)]   # 照片上的手，写在缩到 500 宽的图上
# 照片上看得见的就这几样，一样一样写清楚：左边一排指节鼓包，手指从那里绕到后头看不见；只有食指一小节从左上弯过来；拇指在右上，根部很厚，尖靠着东西；东西从两者之间的凹处伸出来
HAND_PROMPT = ('Image 1 is a crop from a finished illustration, with a rough photograph of a hand pasted on it as a guide. Image 2 is that photograph, turned to the same angle: a real left hand gripping a can, seen from behind the arm. Repaint image 1 with the same aspect ratio and the same framing. Keep exactly as they are, in the same place and at the same size, in the same painting style: the blade, the straight iron crossguard with its two round ends, the sleeve and its cuff, the line of light and the painted sky. '
               'Turn the pasted photograph into her raised left hand, drawn by a skilled anime illustrator with a clear dark brown outline and clean two-tone skin shading, with a hard gold rim light on the left edge and a cooler shadow on the right. Look carefully at what can be seen in the photograph, and draw exactly that: '
               'One. We look at the broad, plain back of the hand. It fills the fist. Two. The left edge of the hand is a row of knuckles running from the top of the fist downward: rounded bumps in the outline, with small dips between them, each with one short curved line. Three. The fingers go away from us from those knuckles and around the far side, hidden by the hand. No fingers lie across the back of the hand, and no fingertips and no palm can be seen. The only finger we can see is the index finger at the top left: one short rounded segment that bends over the top edge of the fist towards the grip. Four. The thumb is at the top right: from a thick muscular base on the right side of the hand it rises, narrows, and its tip leans in against the grip. Five. Between the index finger and the thumb the top edge of the hand dips in a small concave curve with a small crease in the web of the thumb, and the grip rises out of the hand from there. Six. The wrist is narrower than the hand, with a few fine creases across it, and it runs straight into the bare forearm and the sleeve cuff, as in the photograph. '
               'The sword grip is thinner than the can, so the index finger and the thumb are closer together and both press against the grip. The rough hemp-corded grip comes up out of that dip: a short length of it is visible, and then it meets the middle of the crossguard. Below that the grip is hidden behind the hand and wrist, and no pommel can be seen. Keep the hand the same size as the pasted photograph. There is no can. No text, no logo, no frame.')


def hand_in(name):
    """底稿：旧的手盖掉，画上一小截剑柄，照片的手转过去贴上。"""
    import math
    from PIL import Image, ImageDraw, ImageFilter
    x0, y0, x1, y1 = HAND_BOX
    Z = 1024 / (x1 - x0)
    whole = Image.open(os.path.join(OUT, HAND_SRC[name] + '.png')).convert('RGB')
    c = whole.crop(HAND_BOX).resize((1024, 1024), Image.LANCZOS)
    (ox, oy), (gx, gy) = HAND_G[name]
    # 旧的手和剑柄：拿一块只有天的地方盖上。上沿贴着护手底下，不碰护手
    old = [(ox - 17, oy + 4), (ox - 1, oy - 1), (ox + 19, oy - 8), (ox + 27, oy - 6), (ox + 41, oy + 44), (ox + 7, oy + 50), (ox - 13, oy + 30)]
    m = Image.new('L', c.size, 0)
    ImageDraw.Draw(m).polygon([((x - x0) * Z, (y - y0) * Z) for x, y in old], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(4))
    bb = m.getbbox()
    layer = c.copy()
    layer.paste(whole.crop((304, 364, 362, 420)).resize((bb[2] - bb[0], bb[3] - bb[1]), Image.LANCZOS), bb[:2])
    c.paste(layer, (0, 0), m)
    gc = c.convert('RGBA')
    d = ImageDraw.Draw(gc)
    # 一小截麻绳缠的剑柄：顺着剑的方向，从护手底下到拳头里头
    ux, uy = 0.41, 0.91
    wx, wy = uy * 4.5, -ux * 4.5
    top = (gx - ux * 12, gy - uy * 12)
    bot = (gx + ux * 12, gy + uy * 12)
    d.polygon([((p[0] - x0) * Z, (p[1] - y0) * Z) for p in ((top[0] + wx, top[1] + wy), (bot[0] + wx, bot[1] + wy), (bot[0] - wx, bot[1] - wy), (top[0] - wx, top[1] - wy))], fill=(158, 124, 72, 255))
    for i in range(-12, 13, 3):
        cx, cy = gx + ux * i, gy + uy * i
        d.line([((cx + wx - x0) * Z, (cy + wy - y0) * Z), ((cx - wx - x0) * Z, (cy - wy + 1 - y0) * Z)], fill=(84, 60, 32, 255), width=4)
    # 照片：500 宽的坐标换到原图，抠手，缩放，转到小臂的方向
    ph0 = Image.open(HAND_PHOTO).convert('RGBA')
    F = ph0.width / 500
    pm = Image.new('L', ph0.size, 0)
    ImageDraw.Draw(pm).polygon([(x * F, y * F) for x, y in HAND_POLY], fill=255)
    ph = ph0.copy()
    ph.putalpha(pm.filter(ImageFilter.GaussianBlur(3)))
    S = 0.08 / F * Z         # 拳头 450 宽（500 宽的图上）缩到画上 36 像素
    ph = ph.resize((int(ph.width * S), int(ph.height * S)), Image.LANCZOS)
    rot = ph.rotate(HAND_TH, expand=True, resample=Image.BICUBIC)
    t = math.radians(HAND_TH)
    ax, ay = 300 * F * S - ph.width / 2, 205 * F * S - ph.height / 2
    rx = rot.width / 2 + ax * math.cos(t) + ay * math.sin(t)
    ry = rot.height / 2 - ax * math.sin(t) + ay * math.cos(t)
    gc.alpha_composite(rot, (int((gx - x0) * Z - rx), int((gy - y0) * Z - ry)))
    p = os.path.join(REFD, 'hand_in_%s.png' % name)
    gc.convert('RGB').save(p)
    if not os.path.exists(HAND_TURNED):
        ph0.convert('RGB').rotate(HAND_TH, expand=True, resample=Image.BICUBIC, fillcolor=(40, 40, 40)).save(HAND_TURNED)
    return p


for _k in (1, 2, 3):
    JOBS['hand2_a%d' % _k] = ([os.path.join(REFD, 'hand_in_a.png'), HAND_TURNED], HAND_PROMPT)
    JOBS['hand2_b%d' % _k] = ([os.path.join(REFD, 'hand_in_b.png'), HAND_TURNED], HAND_PROMPT)


# 第六稿。用户回：传奇并没有跟着她篡位，照 PV 的画法换成联邦的普通军人、骑士、法师、圣职者和那些被压迫的人，簇拥着她；手别跟用户的手一样，得是她自己的手；衣服以白色那套为准，跟白厄拉开差距，飘带、披风、那时候佣兵军官身份的护甲。
T5C_GREY = os.path.join(REFD, 't5c_grey.png')
T6_PROMPT = ('Image 1 is a drawing of a woman seen from directly behind, holding a sword up high. Image 2 shows the hair colour and the palette of this character: white cloth with gold edges and dark old armour. Repaint image 1 with the same aspect ratio and the same framing, keeping exactly the same pose, the same proportions, the same stance, the same head and braided bun of hair in old-copper dark gold-brown, the same raised arm, the same legs, the same plain old sword and the same two hands, in the same place in the picture. Change only her clothes. '
             'She is a veteran mercenary captain and front-line officer in field armour over a white officer\'s coat. This must be a distinctive character design, with a silhouette quite unlike a long plain white coat. '
             'The coat: a fitted white military coat with a stiff high collar showing the two torn places where she ripped off her rank badges, with a narrow trim of old gold-bronze. Its skirts only reach the knee and are split into separate panels at the back and sides, which lift a little in the wind. '
             'The armour over it, all worn and mended but well kept: a back plate of dark steel with old bronze edges and a central ridge, riveted, held by leather straps and buckles, with a few dents. On the raised left shoulder a layered spaulder of overlapping steel lames. On the right shoulder a larger rounded pauldron of old leather and steel, visibly mended with thick stitches. On each forearm a bracer of dark leather with steel splints, ending at the wrist, so the hands stay bare. At the hips, below the belt, two hanging tassets of overlapping plates. Steel greaves with knee cops strapped over dark breeches and tall worn boots. '
             'The cape: from the left shoulder a long asymmetrical half-cape of white cloth with a worn gold edge and a warm pale gold lining, frayed at its end, streams out far to the left in a strong wind in one large clean shape. The streamers: three or four long narrow ribbons of white and pale gold, tied at the belt and at the shoulder, fly out with the cape in long S-curves. '
             'Keep the old leather belt polished by years of wear, the empty plain leather scabbard hanging at the hip on the right of the picture, and a small cloth bag at the small of her back. There is no gown, no long skirt, no red, no stars, no jewels, no crown. Everything around the figure is fully transparent: no background, no ground, no shadow. No text, no logo, no frame.')
JOBS['t6a1'] = ([T5C_GREY, os.path.join(REFD, 'p_thornevia.png')], T6_PROMPT)
JOBS['t6a2'] = ([T5C_GREY, os.path.join(REFD, 'p_thornevia.png')], T6_PROMPT)
# 底图：把台阶底下那群传奇拿掉，台阶照 r12a 那样收。上头举火把的小人留着
JOBS['plate9'] = ([os.path.join(OUT, 'plate8.png'), os.path.join(OUT, 'r12a.png')],
                  'Repaint image 1 with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size, in the same painting style: the night sky, the line of light, the throne with its flying shards, the small torch bearers near the throne, and the far city. Remove the whole group of people at the bottom of the picture, with their hammer, flag, bow and staff, and the dark rocks they stand on. The stairs now run on, all the way down to the bottom edge of the picture and across its whole width, with nobody on them. Give the stairs the same surface as the stairs in image 2: big dark violet planes with dry-brush texture, each step with one thin broken line of gold light along its edge. Image 2 is only a reference for the stairs: do not take the woman or anything else from it. No people other than the small torch bearers. No text, no logo, no frame, no crescents, no moon phases.')


# 她（t6a1，膝长的白外套、甲裙、护腿、披风、飘带）贴到 plate9 上，整张再画一遍，人群这时候画上去。人群照主线黎明篡位：南线回来的兵、冠台的卫兵、白烛的祭司点白蜡烛、苇棚区的人举苇子扎的火把、举着烧悬赏单的孩子
PV_CHESS = os.path.join(REF, 'pv_chess_pieces.png')
COMP_13 = os.path.join(REFD, 'comp_r13.png')
R13_PROMPT = ('Image 1 is a rough paste-up: a painted background with a figure pasted on it. Images 2, 3 and 4 are frames from an animated film, given only as a reference for the art direction and for how a crowd of silhouettes is painted; do not copy their subjects, their armour, their red colour or their shapes, and keep the palette of image 1. Repaint image 1 as one single unified finished illustration with the same aspect ratio and the same framing, painted all at once in one light, with nothing looking pasted on. ' + PV_STYLE +
              'Keep the composition exactly as it is: the razor-straight line of light, the throne with its flying shards, the far city and the stairs. '
              'Keep the woman seen from behind exactly as she is, in the same place, at the same size and in the same pose and proportions: her raised arm and plain old sword, her braided bun of old-copper hair, her white coat with its split knee-length skirts, the dark steel back plate, the layered shoulder pieces, the leather bracers, the tassets, the steel greaves, the long white half-cape with its gold edge and gold lining and the long ribbons flying to the left. Paint her in crisp anime drawing with rough dry-brush texture in the cloth, with hard gold rim light along her edges and a shaded side falling into cool indigo-violet. The white cloth takes gold on its lit planes and violet in its shadows. She stays clearly the brightest figure in the lower part of the picture. The blade flashes where the line of light crosses it. '
              'Now add a great crowd of ordinary people, who follow her up the stairs and press around her on both sides. All of them are seen from behind, looking up at her and following her, as dark silhouettes with hard gold rim light and very little detail, with no faces. There are no heroes among them and nobody stands out: foot soldiers in open kettle helmets with long spears and round shields, soldiers in patched leather armour, palace guards with long spears on their shoulders, a knight in plate holding up a longsword, a robed mage with a tall staff with a small cold light at its tip, a priest in a long pale robe holding up a white candle, dock workers and slum dwellers in ragged clothes holding up burning bundles of reeds as torches, women in shawls, an old man with a stick, a child on someone\'s shoulders holding up a burning sheet of paper. Raised fists and open hands reach up towards her. '
              'The crowd is a sea of people. It fills the whole bottom of the picture across its full width: the nearest ones at the very bottom edge are large, their heads and raised arms reaching about a quarter of the way up the picture. Behind them the people get smaller and smaller up the stairs and rise on both sides of her: on the left they join the small torch bearers climbing to the throne, and on the right they run up the stairs towards the far city, getting very small. She walks just ahead of them, with a small clear space of bare stairs around her boots, so that her whole figure, her cape and her ribbons can be seen clearly against the dark stairs; nobody overlaps her. Dozens of small torch flames and candles glow among the people. Her long shadow falls down the stairs onto the people just behind her. No crosses, no text, no logo, no frame. ' + PV_END)
for _k in (1, 2, 3):
    JOBS['r13a%d' % _k] = ([COMP_13, PV_RED, PV_CHESS, PV_GOLD], R13_PROMPT)


# 手：用户回“现在人体对了，但是索恩薇娅的手别跟我的手一样...得是她自己的手”。结构留 hand2_a1 的（手背、左边指节、右上拇指、中间的凹口），轮廓收窄当底稿，写明是她的手：修长，指节小，手腕细。旧的手和露在护臂边上的剑柄先盖掉
H3_BOX = (325, 305, 445, 425)
H3_G = (377, 352)                     # 拳头顶上剑柄穿出来的地方
H3_POLY = [(540, 905), (470, 860), (415, 820), (385, 760), (368, 720), (358, 640), (382, 590), (358, 540), (362, 510), (392, 492), (440, 488), (505, 498), (560, 512), (600, 512), (622, 472), (630, 420), (655, 402), (702, 425), (745, 508), (765, 570), (772, 650), (778, 720), (800, 790)]   # hand2_a1 上的手，写在它 1254 宽的图上
H3_DIP = (590, 510)                   # hand2_a1 上那个凹口
H3_SX, H3_SY = 0.70, 0.84             # 窄一点、长一点。1 是 hand2_a1 原来的大小（拳头宽 38.7 像素）
H3_REF = os.path.join(REFD, 'hand3_ref.png')
H3_PROMPT = ('Image 1 is a crop from a finished illustration, with a rough pasted hand on it as a guide for where the hand goes. Image 2 shows how this fist is built, drawn larger. Repaint image 1 with the same aspect ratio and the same framing. Keep exactly as they are, in the same place and at the same size, in the same painting style: the blade, the straight iron crossguard with its two round ends, the dark leather bracer with its cuff, the line of light and the painted sky. '
             'Draw her raised left hand in the same place and at the same size as the pasted guide, seen from directly behind: the back of the hand faces us, the row of knuckles is in the outline on the left, the first segment of the index finger bends over at the top left, the thumb is at the top right with its tip leaning in against the grip, and in the small dip between them the rough hemp-corded grip rises to the middle of the crossguard. The fingers go away from us around the far side, so no fingertips and no palm can be seen. '
             'This is the hand of a tall, strong young woman who has held a sword all her life. It is slender and long-boned: a narrow hand with long elegant lines, small neat knuckles, fine tendons showing on the back of the hand, a slim tapering thumb, and a slim wrist that goes straight into the leather bracer. Fair clean skin with a couple of small pale old scars. It must be a woman\'s hand: not thick, not puffy, not square, not a man\'s hand, with no hair. Draw it like a skilled anime illustrator, with a fine dark brown outline and clean two-tone skin shading, a hard gold rim light on the left edge and a cooler shadow on the right. '
             'The lower part of the sword grip is hidden behind the hand and the bracer: no grip and no pommel can be seen below the fist or beside the bracer. No text, no logo, no frame.')


def hand3_in(sx=H3_SX, sy=H3_SY, stem='hand3_in'):
    """底稿：旧的手和剑柄盖掉，画一小截麻绳，hand2_a1 的手收窄贴上。"""
    from PIL import Image, ImageDraw, ImageFilter
    x0, y0, x1, y1 = H3_BOX
    Z = 1024 / (x1 - x0)
    whole = Image.open(os.path.join(OUT, 'r13a2.png')).convert('RGB')
    c = whole.crop(H3_BOX).resize((1024, 1024), Image.LANCZOS)
    old = [(361, 349), (372, 345), (392, 339), (398, 342), (402, 362), (414, 392), (406, 404), (401, 400), (394, 383), (391, 375), (372, 376), (362, 362)]
    m = Image.new('L', c.size, 0)
    ImageDraw.Draw(m).polygon([((x - x0) * Z, (y - y0) * Z) for x, y in old], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(3))
    bb = m.getbbox()
    layer = c.copy()
    layer.paste(whole.crop((326, 364, 362, 420)).resize((bb[2] - bb[0], bb[3] - bb[1]), Image.LANCZOS), bb[:2])
    c.paste(layer, (0, 0), m)
    gc = c.convert('RGBA')
    d = ImageDraw.Draw(gc)
    gx, gy = H3_G
    ux, uy, wx, wy = 0.41, 0.91, 3.6, -1.6
    top, bot = (gx - ux * 8, gy - uy * 8), (gx + ux * 6, gy + uy * 6)
    d.polygon([((p[0] - x0) * Z, (p[1] - y0) * Z) for p in ((top[0] + wx, top[1] + wy), (bot[0] + wx, bot[1] + wy), (bot[0] - wx, bot[1] - wy), (top[0] - wx, top[1] - wy))], fill=(158, 124, 72, 255))
    h = Image.open(os.path.join(OUT, 'hand2_a1.png')).convert('RGBA')
    F = h.width / 1254
    hm = Image.new('L', h.size, 0)
    ImageDraw.Draw(hm).polygon([(x * F, y * F) for x, y in H3_POLY], fill=255)
    h.putalpha(hm.filter(ImageFilter.GaussianBlur(2)))
    KX, KY = sx * Z / (10.45 * F), sy * Z / (10.45 * F)
    h = h.resize((int(h.width * KX), int(h.height * KY)), Image.LANCZOS)
    gc.alpha_composite(h, (int((gx - x0) * Z - H3_DIP[0] * F * KX), int((gy - y0) * Z - H3_DIP[1] * F * KY)))
    p = os.path.join(REFD, stem + '.png')
    gc.convert('RGB').save(p)
    r = Image.open(os.path.join(OUT, 'hand2_a1.png')).convert('RGB')
    r.crop((int(320 * F), int(360 * F), int(860 * F), int(960 * F))).save(H3_REF)
    return p


for _k in (1, 2, 3):
    JOBS['hand3_%d' % _k] = ([os.path.join(REFD, 'hand3_in.png'), H3_REF], H3_PROMPT)
    # 再窄一点，食指和中指的第一节露出来
    JOBS['hand4_%d' % _k] = ([os.path.join(REFD, 'hand4_in.png'), H3_REF], H3_PROMPT.replace('the first segment of the index finger bends over at the top left,', 'the slim first segments of the index finger and the middle finger bend over at the top left, separated by one fine dark line,') + ' The fist must stay as narrow as the pasted guide.')


# 用户又回：“或者改成带手套/手甲，披风改成遮住整个后背”。人和人群都留 r13a2，只把她这一块裁下来改披风和手。F14_BOX 写在 r13a2 的像素上
F14_BOX = (90, 300, 650, 1040)
F14_PROMPT = ('Image 1 is a crop from a finished illustration: a woman seen from directly behind on a great flight of stairs, holding a sword up high, with small crowds and torches behind her. Repaint image 1 with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size, in the same painting style: the sky, the throne, the stairs, all the small people, spears and torches, her head and braided bun of hair, the high white collar with its torn places, her raised arm and its position, the sword, the two layered shoulder pieces, the leather bracers, the white coat skirts, the steel greaves and the boots. Change only two things. '
              'First, the cape. She now wears one full cape that covers her whole back: a long heavy white cape with a worn gold edge and a warm pale gold lining, fastened at both shoulders under the shoulder pieces. It falls from both shoulders over her entire back, hiding the back plate, the belt, the bag, the scabbard and the tassets completely, as one big clean white shape with a few long folds, down to the back of her knees. Below the waist the wind catches it and its left side sweeps far out to the left in one huge shape with a frayed end, where it turns over and shows the gold lining; this replaces the old half-cape. The long ribbons still fly out from under it to the left. The white coat skirts show below the hem of the cape on the right, and her armoured legs show below that. The white cloth takes gold on its lit planes and violet in its shadows, with rough dry-brush texture and a hard gold rim light along its edges. '
              'Second, the hands. Both hands now wear half-gauntlets: dark leather gloves with riveted plates of old steel over the back of the hand and small overlapping plates over the knuckles and along the fingers, trimmed with old bronze. The gauntlet of the raised left hand is seen from behind, gripping the sword: its back plate faces us. The right hand hangs at her side in a gauntleted fist. No bare skin on the hands. No text, no logo, no frame.')
for _k in (1, 2):
    JOBS['f14_%d' % _k] = ([os.path.join(REFD, 'f14_in.png')], F14_PROMPT)


# 举剑那只手甲单画：f14_1 这一块裁下来，贴上 hand4_1 的手（修长的轮廓和手背、指节、拇指的结构）当底稿，旧的手甲和露在护臂边上的剑柄先盖掉。H5_ 的框写在 H3_BOX 那个 1024 宽的画面上
H5_POLY = [(484, 318), (505, 330), (530, 400), (540, 470), (548, 560), (560, 625), (420, 672), (385, 620), (345, 560), (325, 500), (330, 440), (320, 400), (332, 382), (375, 378), (400, 388), (398, 330), (440, 318), (470, 316)]
H5_OLD = [(306, 404), (480, 334), (570, 298), (660, 262), (700, 300), (710, 600), (790, 760), (750, 870), (680, 810), (612, 700), (600, 660), (560, 622), (400, 650), (320, 510)]
H5_PROMPT = ('Image 1 is a crop from a finished illustration, with a rough pasted bare hand on it as a guide for the pose and size of her fist. Image 2 shows how this fist is built, drawn larger. Repaint image 1 with the same aspect ratio and the same framing. Keep exactly as they are, in the same place and at the same size, in the same painting style: the blade, the straight iron crossguard with its two round ends, the steel bracer on her forearm, her hair, the line of light and the painted sky. '
             'Turn the pasted hand into her raised left hand wearing a half-gauntlet, seen from directly behind, with the same narrow silhouette, in the same place and at the same size. It is a dark worn leather glove. On the back of the hand, facing us, lies one riveted plate of old steel with a thin old-bronze edge, shaped to the hand. Along the left edge, over the row of knuckles, runs a line of small overlapping steel plates following the bumps of the knuckles. The first segments of the index and middle fingers bend over at the top left, each with one small steel plate, separated by a fine dark line. At the top right the slim leather-covered thumb, with one small plate, curls in against the grip. In the dip between them the rough hemp-corded grip rises to the middle of the crossguard. The fingers go away from us around the far side, so no fingertips and no palm can be seen. A short flared leather cuff at the wrist goes down over the top of the steel bracer. No bare skin. '
             'The lower part of the sword grip is hidden behind the hand and the bracer: no grip and no pommel can be seen below the fist or beside the bracer. Draw it in crisp anime line art with clean flat colours and a little dry-brush wear, with a hard gold rim light on the left edge and a cooler shadow on the right. It should look slim, strong and well made. No text, no logo, no frame.')
H5_IN, H5_REF = os.path.join(REFD, 'hand5_in.png'), os.path.join(REFD, 'hand5_ref.png')


def hand5_in():
    from PIL import Image, ImageDraw, ImageFilter
    F14 = Image.open(os.path.join(OUT, 'f14_1.png')).convert('RGB')
    x0, y0, x1, y1 = H3_BOX
    fx, fy = F14.width / (F14_BOX[2] - F14_BOX[0]), F14.height / (F14_BOX[3] - F14_BOX[1])
    box = (int((x0 - F14_BOX[0]) * fx), int((y0 - F14_BOX[1]) * fy), int((x1 - F14_BOX[0]) * fx), int((y1 - F14_BOX[1]) * fy))
    c = F14.crop(box).resize((1024, 1024), Image.LANCZOS)
    # 旧的手甲和剑柄盖掉：一行一行拿左右两边的颜色接过去，别的交给 GPT
    import numpy as np
    m = Image.new('L', c.size, 0)
    d = ImageDraw.Draw(m)
    d.polygon(H5_OLD, fill=255)
    mask = np.asarray(m) > 0
    arr = np.asarray(c).astype(np.float32).copy()
    for y in np.nonzero(mask.any(axis=1))[0]:
        xs = np.nonzero(~mask[y])[0]
        if y < 430 or y >= 600:      # 这几行左边挨着护手和护臂，只拿右边的天
            xs = xs[xs > 560]
        arr[y, :, :] = np.stack([np.interp(np.arange(1024), xs, arr[y, xs, k]) for k in range(3)], axis=1)
    fill = Image.fromarray(np.uint8(arr)).filter(ImageFilter.GaussianBlur(6))
    c.paste(fill, (0, 0), m.filter(ImageFilter.GaussianBlur(2)))
    gc = c.convert('RGBA')
    h = Image.open(os.path.join(OUT, 'hand4_1.png')).convert('RGBA').resize((1024, 1024), Image.LANCZOS)
    hm = Image.new('L', h.size, 0)
    ImageDraw.Draw(hm).polygon(H5_POLY, fill=255)
    h.putalpha(hm.filter(ImageFilter.GaussianBlur(2)))
    gc.alpha_composite(h)
    gc.convert('RGB').save(H5_IN)
    Image.open(os.path.join(OUT, 'hand4_1.png')).convert('RGB').resize((1024, 1024), Image.LANCZOS).crop((280, 280, 620, 700)).save(H5_REF)
    return H5_IN


for _k in (1, 2, 3):
    JOBS['hand5_%d' % _k] = ([H5_IN, H5_REF], H5_PROMPT)


# hand5_1 右边的天上留着底稿擦除的污迹，只修天
JOBS['hand6'] = ([os.path.join(OUT, 'hand5_1.png')],
                 'Repaint this crop from a finished illustration with the same aspect ratio and the same framing, keeping everything exactly as it is, in the same place and at the same size, in the same painting style: the blade, the crossguard, the gauntlet, the hemp grip, the bracer, the hair and the line of light. Change only the painted sky to the right of the gauntlet and the bracer: it has a dark smudge next to the bracer and a blurred smooth patch above it. Repaint that part of the sky so that it matches the rest of the sky: fields of orange and amber with long vertical streaks of paint and rough dry-brush texture, with a few violet patches further to the right, as sharp as the rest of the picture. There is nothing dark and nothing else next to the bracer. No text, no logo, no frame.')


def mirror_ref():
    from PIL import Image, ImageOps
    if not os.path.exists(T4_GREY) and os.path.exists(os.path.join(OUT, 't4.png')):
        t = Image.open(os.path.join(OUT, 't4.png')).convert('RGBA')
        g = Image.new('RGBA', t.size, (205, 205, 205, 255))
        g.alpha_composite(t)
        g.convert('RGB').save(T4_GREY)
    if not os.path.exists(T5A_GREY) and os.path.exists(os.path.join(OUT, 't5a.png')):
        t = Image.open(os.path.join(OUT, 't5a.png')).convert('RGBA')
        g = Image.new('RGBA', t.size, (205, 205, 205, 255))
        g.alpha_composite(t)
        g.convert('RGB').save(T5A_GREY)
    for fig, comp in (('t5c', COMP_A), ('t5b', COMP_B)):
        if not os.path.exists(comp) and os.path.exists(os.path.join(OUT, fig + '.png')) and os.path.exists(os.path.join(OUT, 'plate8.png')):
            c = Image.open(os.path.join(OUT, 'plate8.png')).convert('RGBA')
            t = Image.open(os.path.join(OUT, fig + '.png')).convert('RGBA')
            t = t.resize((int(t.width * HERO8['k']), int(t.height * HERO8['k'])), Image.LANCZOS)
            c.alpha_composite(t, (HERO8['x'], HERO8['y']))
            c.convert('RGB').save(comp)
    for n, src in HAND_SRC.items():
        if not os.path.exists(os.path.join(REFD, 'hand_in_%s.png' % n)) and os.path.exists(os.path.join(OUT, src + '.png')):
            hand_in(n)
    if not os.path.exists(T5C_GREY) and os.path.exists(os.path.join(OUT, 't5c.png')):
        t = Image.open(os.path.join(OUT, 't5c.png')).convert('RGBA')
        g = Image.new('RGBA', t.size, (205, 205, 205, 255))
        g.alpha_composite(t)
        g.convert('RGB').save(T5C_GREY)
    if not os.path.exists(COMP_13) and os.path.exists(os.path.join(OUT, 't6a1.png')) and os.path.exists(os.path.join(OUT, 'plate9.png')):
        c = Image.open(os.path.join(OUT, 'plate9.png')).convert('RGBA')
        t = Image.open(os.path.join(OUT, 't6a1.png')).convert('RGBA')
        t = t.resize((int(t.width * HERO8['k']), int(t.height * HERO8['k'])), Image.LANCZOS)
        c.alpha_composite(t, (HERO8['x'], HERO8['y']))
        c.convert('RGB').save(COMP_13)
    if not os.path.exists(os.path.join(REFD, 'hand3_in.png')) and os.path.exists(os.path.join(OUT, 'r13a2.png')):
        hand3_in()
    if not os.path.exists(os.path.join(REFD, 'hand4_in.png')) and os.path.exists(os.path.join(OUT, 'r13a2.png')):
        hand3_in(sx=0.62, sy=0.82, stem='hand4_in')
    p = os.path.join(REFD, 'f14_in.png')
    if not os.path.exists(p) and os.path.exists(os.path.join(OUT, 'r13a2.png')):
        c = Image.open(os.path.join(OUT, 'r13a2.png')).convert('RGB').crop(F14_BOX)
        k = 1536 / max(c.size)
        c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS).save(p)
    if not os.path.exists(H5_IN) and os.path.exists(os.path.join(OUT, 'f14_1.png')) and os.path.exists(os.path.join(OUT, 'hand4_1.png')):
        hand5_in()
    p = os.path.join(REFD, 'bell_in.png')
    if not os.path.exists(p) and os.path.exists(os.path.join(OUT, 'l5.png')):
        Image.open(os.path.join(OUT, 'l5.png')).convert('RGB').crop(BELL_BOX).resize((1024, 796), Image.LANCZOS).save(p)
    p = os.path.join(REFD, 'sea_in.png')
    if not os.path.exists(p) and os.path.exists(os.path.join(OUT, 'l5.png')):
        Image.open(os.path.join(OUT, 'l5.png')).convert('RGB').crop(SEA_BOX).resize((1024, 924), Image.LANCZOS).save(p)
    if not os.path.exists(MIRROR):
        ImageOps.mirror(Image.open(os.path.join(REF, 'back_view_pose.webp')).convert('RGB').crop((875, 515, 1225, 1040))).resize((1024, 1536), Image.LANCZOS).save(MIRROR)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    mirror_ref()
    for name in (sys.argv[1:] or JOBS):
        refs, prompt = JOBS[name]
        print(name, gpt_gen.gen(os.path.join(OUT, name), prompt, refs=refs), flush=True)
