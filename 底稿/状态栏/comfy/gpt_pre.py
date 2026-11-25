#!/usr/bin/env python3
# 迷宫纪前传那一套四方（11-25）。python gpt_pre.py [名字…]，写 out/前传_11-25/，已有的不重出。CODEX_HOME 切号。
# 方向稿第四版第四节：前传是铜版画、木刻的井口、公会、黑潮，框里是委托单的浅黄羊皮纸，铜褐边，徽记旅印（一圈印纹，正中四角星）。
# 左扇：井（木架绞盘的竖井口，一层一层的地层，绳和灯往下，最底下黑潮往上涌）；右扇：冒险者公会（断门、委托板、一队人提灯朝井走）；
# 楣：旅印居中，绳上挂委托单当花边，两肩绳圈和小灯；座：井口边上的帐篷和灯，两头高、当中低。
# 画法照月银纪那一套 RENDER（gpt_moon.py），拿四套定稿的扇当画法参考；调子换成铜版画的褐和铜、羊皮纸的浅黄、灯的琥珀，黑潮是墨黑带青。
# 跟迷宫纪 1001 那一套错开：不画螺旋的井、黑日、巨影、星环，不用靛紫。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_gen
from gpt_moon import RENDER, ROLES, CHALK

OUT = os.path.join(HERE, 'out', '前传_11-25')
REF = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '语料', '人物参考_11-04')
MOON_L, STRIFE_R, STRIFE_TOP = [os.path.join(REF, n) for n in ('moon_left_style.png', 'strife_right_style.png', 'strife_top_style.png')]
BRONZE_R = os.path.join(OUT, '_ref_bronze_right.png')   # frame_art 的山铜纪右扇转 png 当参考


def ref_bronze():
    if not os.path.exists(BRONZE_R):
        from PIL import Image
        os.makedirs(OUT, exist_ok=True)
        im = Image.open(os.path.join(HERE, 'out', 'frame_art', 'bronze_right.webp')).convert('RGBA')
        bg = Image.new('RGBA', im.size, (20, 18, 30, 255))
        bg.alpha_composite(im)
        bg.convert('RGB').resize((1050, 1500)).save(BRONZE_R)


PALETTE = ('The palette is an old copper engraving warmed by lamplight: deep umber and burnt-sienna shadows, lines of copper and tarnished bronze, the cream of aged parchment on the lit edges, and the amber of oil lamps and lanterns as the warm light. '
           'The only cold colour is the black tide from the deep: ink black with dark teal and a little pale sea-green foam. Do not use indigo, violet or purple. ')
ENGRAVE = ('Inside the flat colour shapes, more than usual, use the fine parallel line hatching and cross-hatching of a copper-plate engraving and the gouge marks of a woodcut, so the picture reads like a hand-coloured engraving, still in the same flat cut-paper layered style. ')
NOT = ('Do not use: glossy anime key-art shading, realistic metal, sparkles everywhere, floating gold dust, busy ornament, 3D look, western cartoon proportions, thick black outlines, '
       'any text, letters, numbers or writing anywhere (papers and notices are blank or show only a wax seal or a small sketch), logo, frame, crosses or cross shapes, '
       'large round discs, moons, crescents, moon phases, a black sun, a spiral, guns, modern objects. ')
STYLE = RENDER + ENGRAVE + PALETTE + NOT
SAME = ('Images 1 and 2 are two side panels of the same game interface that are already finished; this picture is a new panel for the same set, so it must look as if the same hand drew it: copy exactly how they are drawn (shapes, hatching, outlines, grain, layering), '
        'but do not copy their characters, creatures, objects, scenes or colours. ')

JOBS = {
    # 左扇：靠窗在右，人人、事事朝右
    'left': (lambda: [MOON_L, BRONZE_R, CHALK],
             SAME + 'Image 3 is a style reference only. '
             'A tall portrait picture, aspect ratio 2:3. Keep the main shapes in the right two thirds of the picture, keep the top tenth of the picture as plain dark umber sky, and leave nothing important touching the right edge. '
             'Subject: the Great Well in the first centuries after the earth opened, shown like a cross-section on an engraved plate. From top to bottom: '
             'First, at the upper part, the mouth of a colossal straight vertical shaft in the ground, wider than a town, with a huge headframe of dark timber beams built over it, a great wooden windlass wheel and many thick hemp ropes running down into the dark; tiny figures with lamps stand on the timber walkways; a few tents and lantern poles at its rim. '
             'Second, below the surface, the shaft goes down through layer after layer of the deep, each layer a different world cut open in the section like the strata of a cliff: a buried ruined city of pale stone with broken arches; a forest of tall glowing mushrooms; a dark underground sea with an old stone pier; caverns of large amber crystals. Small parties of adventurers climb down rope ladders and narrow ledges along the right side of the shaft, each carrying one small warm lantern, a thin chain of lights going down into the deep. '
             'Third, at the bottom, and the largest shape in the picture, the black tide: a vast surge of ink-black water and shadow rising up out of the depths and curling up and to the right like a breaking wave, its crest edged with dark teal and pale sea-green foam, with the vague dark shapes of monsters in it, horns, claws and fins, but no faces. The lantern lights just above it keep burning. '
             'Along the very bottom edge, dark rock. ' + STYLE),
    # 右扇：靠窗在左，人人、事事朝左
    'right': (lambda: [STRIFE_R, BRONZE_R, CHALK],
              SAME + 'Image 3 is a style reference only. '
              'A tall portrait picture, aspect ratio 2:3: layered from the top of the picture to the bottom, every figure turned to the left and everything aimed toward the left edge of the picture. The top tenth of the picture is plain dark umber sky, and nothing important touches the left edge of the picture: leave a clear margin there. '
              'Subject: the Adventurers\' Guild in its golden age, at the gate where the war ended. From top to bottom: '
              'First, high up and far behind, a colossal broken gate in an endless old defensive wall of pale stone: the gateway is cracked and its top has fallen in, and a long wooden table with two empty chairs facing each other stands in the opening under hanging lanterns, where two kings once signed a peace. '
              'Second, in front of it, a tall guild hall of dark timber and pale stone, with a steep roof, many warm lit windows and wide open doors; above the doors hangs a large round copper sign: a ring of engraved seal pattern with a four-pointed star in the centre, and no letters. '
              'Third, along the front of the hall, a huge wooden notice board taller than a man, covered with dozens of pinned parchment notices, each one blank or with only a red wax seal or a small sketch of a beast; a few notices come loose and flutter away to the left. '
              'Fourth, in front and the largest, a party of five adventurers setting out to the left, toward the well, mid-stride and full of energy, each doing something different: in the lead a young human swordswoman with short copper-red hair and a travelling coat, raising a brass lantern high in her left hand and pointing the way to the left with it, a sword at her hip; behind her a stocky dwarf with a braided brown beard carrying a coil of rope and a miner\'s pick on his shoulder; an elf archer with long pale hair and long ears looking to the left with an arrow on the string; a fox-eared scout girl with a short cape crouched low on a crate, reading a folded parchment map; and a tall young mage with two small curved horns and dark hair in a long hooded robe, holding up a staff with a small flame floating at its tip. '
              'Delicate anime faces with clean lines and clear eyes, each face a different person. Fully clothed, not sexualized. '
              'Fifth, at the bottom, a lively crowd of the camp town in smaller scale: porters with packs, a cart of crates, lantern poles, and the canvas roofs of tents fading into lamp-lit haze. ' + STYLE),
    # 第二稿：头一稿放进五纪并排看，细碎、满，像普通的插画，别的四套是大块剪纸、长飘带、大片空；黑潮画成了浮世绘的爪浪。
    # 拿月银纪、山铜纪两张安静的扇当画法参考，少画几样，留大片空，飘带改成成串飞起来的委托单和灯烟；黑潮写成墨一样涌起来的一整片，不是海浪
    'left2': (lambda: [os.path.join(REF, 'moon_right_style.png'), BRONZE_R, CHALK],
              SAME + 'Image 3 is a style reference only. '
              'A tall portrait picture, aspect ratio 2:3. Keep the main shapes in the right two thirds of the picture, keep the top tenth of the picture as plain dark umber sky, and leave nothing important touching the right edge. '
              'Big calm empty areas and only a few large shapes, like a paper theatre: no crowd of small details. '
              'Subject: the Great Well, a colossal straight vertical shaft going down into the earth, shown as a cut-open cross-section. '
              'At the top, the mouth of the shaft with one huge simple headframe of dark timber over it, one great wooden wheel and a few long hemp ropes falling straight down into the dark like the strings of an instrument. '
              'Down the left side of the shaft, the cut-open layers of the deep as four or five broad bands like the strata of a cliff, each band suggested simply with one big shape: pale broken arches of a buried city; a few tall glowing mushrooms; a flat band of dark still water; large amber crystals. '
              'Down the right side of the shaft, one long thin chain of tiny warm lantern lights, adventurers climbing down on ropes, drawn as a single elegant curving line of lights going down into the deep. '
              'The lower third of the picture: the black tide rising up out of the bottom of the shaft. It is not a sea wave and has no curling crests or claw-like foam: it is a vast slow upwelling of thick ink-black shadow, like ink poured upward into water, billowing in huge soft rounded plumes and long ribbons that sweep up and to the right, with thin dark teal edges and a faint sea-green sheen; inside it, very faint, the outlines of horns, fins and claws of monsters, no faces. The lowest lantern lights stand just above it and keep burning. ' + STYLE),
    'right2': (lambda: [os.path.join(REF, 'moon_right_style.png'), BRONZE_R, CHALK],
               SAME + 'Image 3 is a style reference only. '
               'A tall portrait picture, aspect ratio 2:3: layered from the top of the picture to the bottom, every figure turned to the left and everything aimed toward the left edge of the picture. The top tenth of the picture is plain dark umber sky, and nothing important touches the left edge of the picture. '
               'Big calm empty areas and only a few large shapes, like a paper theatre: no crowd of small details, no busy buildings. '
               'Subject: the Adventurers\' Guild setting out for the Great Well. '
               'At the top and far behind, very simple and pale, a colossal broken gate in an old stone wall, its top fallen in, with a few lanterns hanging in the opening. '
               'Below it, a tall simple guild hall of dark timber with a steep roof and warm lit windows, drawn as one big flat shape, with a large round copper sign over the door: a ring of engraved seal pattern with a four-pointed star in the centre, and no letters. '
               'From the hall, long streams of blank parchment notices fly out to the left like ribbons in the wind, dozens of them in long sweeping curving lines, a few with a red wax seal; these streams of paper are the big sweeping ribbon shapes of the picture. '
               'In front, large, a party of five adventurers setting out to the left, mid-stride, each doing something different: in the lead a young human swordswoman with short copper-red hair and a long cream travelling coat, raising a brass lantern high in her left hand toward the left, a sword at her hip; a stocky dwarf with a braided brown beard carrying a coil of rope and a miner\'s pick; an elf archer with long pale hair and long ears; a fox-eared scout girl with a short cape holding a folded parchment map; and a tall young mage with two small curved horns and dark hair in a long hooded robe, a small flame floating above his open hand. Their coats and capes are long sweeping cut-paper shapes flowing to the right. '
               'Delicate anime faces with clean lines and clear eyes, each face a different person. Fully clothed, not sexualized. '
               'At the bottom, only soft lamp-lit haze with a few tent roofs and lantern poles in silhouette. ' + STYLE),
    # 楣正中：旅印
    'seal': (lambda: [STRIFE_TOP, CHALK],
             'Image 1 is the top border of the same game interface, already finished: copy how it is drawn, not its objects. Image 2 is a style reference only. '
             'A single emblem on a fully transparent background, no background at all, seen straight from the front and symmetrical left and right: a round seal of tarnished copper and bronze, like a great wax-seal stamp. '
             'An outer ring of engraved seal pattern made of small repeating notches, dots and short lines, with no letters and no numbers; inside it a thinner ring; in the centre one bold four-pointed star with long sharp points. '
             'Below the seal hang two short pieces of hemp cord, each ending in a small brass lantern with a warm amber flame. Fine engraved lines, crisp silhouette, matte, nothing else in the picture. ' + PALETTE + NOT),
    # 楣两肩：左上角的花边，右肩翻过来
    'corner': (lambda: [STRIFE_TOP, CHALK],
               'Image 1 is the top border of the same game interface, already finished: copy how it is drawn, not its objects. Image 2 is a style reference only. '
               'A single corner ornament on a fully transparent background, no background at all: it decorates the upper left corner of a window, so it curls around that corner: a long sweeping curve runs from the upper right along the top and turns down along the left side, ending in a spiral. '
               'It is made of a thick twisted hemp rope wound with a thin copper band, with three or four small blank parchment notices pinned along it by copper nails, their edges torn in soft waves, one of them with a red wax seal; a small brass lantern with an amber flame hangs at the end of the spiral. Crisp silhouette, fine engraved lines, matte, nothing else in the picture. ' + PALETTE + NOT),
    # 头一稿的角上缠了浮世绘那样的浪，整张重画，不要浪
    'corner2': (lambda: [STRIFE_TOP, CHALK],
                'Image 1 is the top border of the same game interface, already finished: copy how it is drawn, not its objects. Image 2 is a style reference only. '
                'A single corner ornament on a fully transparent background, no background at all: it decorates the upper left corner of a window, so it curls around that corner: a long sweeping curve runs from the upper right along the top and turns down along the left side, ending in a spiral. '
                'It is made only of a thick twisted hemp rope wound with a thin band of engraved copper, and a long ribbon of cream parchment with softly torn wavy edges winding around the rope; three small blank parchment notices are pinned along it by copper nails, one with a red wax seal; a small brass lantern with an amber flame hangs at the end of the spiral. No water, no waves, no foam, no leaves. Crisp silhouette, fine engraved lines, matte, nothing else in the picture. ' + PALETTE + NOT),
    # 楣：沿框上沿走的一条
    'strip': (lambda: [STRIFE_TOP, CHALK],
              'Image 1 is the top border of the same game interface, already finished: copy how it is drawn, not its objects. Image 2 is a style reference only. '
              'A very wide ornament, aspect ratio 3:1, on a fully transparent background, no background at all: a long horizontal decorative border. A hemp rope wound with a thin copper band runs straight across the whole width of the picture with the same thickness everywhere, and small blank parchment notices with softly torn wavy edges hang from it in a steady rhythm like bunting, pinned with copper rings, every fourth one with a small red wax seal; it fades into thin tips at both ends. '
              'Fine engraved lines, crisp silhouette, matte, nothing else in the picture. ' + PALETTE + NOT),
    # 座：井口边上的营地，两头高、当中低
    'camp': (lambda: [MOON_L, BRONZE_R, CHALK],
             SAME + 'Image 3 is a style reference only. '
             'A very wide landscape picture with aspect ratio 3:1 on a fully transparent background: a strip for the bottom of a game screen, seen from the front and a little below. '
             'The camp town at the mouth of the Great Well at night: canvas tents of faded cream and ochre, small timber huts with lit windows, tall lantern poles with warm amber lanterns, stacked crates and barrels, coils of rope, a wooden windlass with a rope going down, a few small figures with lamps. '
             'The camp is piled highest at the far left end and at the far right end of the picture, and stays low across the middle third, where there is only flat dark ground. '
             'Only the camp and the dark ground under it, nothing behind it, no sky, no background, no shadow. ' + STYLE),
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    ref_bronze()
    for name in (sys.argv[1:] or JOBS):
        refs, prompt = JOBS[name]
        print(name, gpt_gen.gen(os.path.join(OUT, name), prompt, refs=refs()), flush=True)
