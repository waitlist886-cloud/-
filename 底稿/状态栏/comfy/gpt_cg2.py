#!/usr/bin/env python3
# 门面第二本书（纷争纪）用的图，都出在 out/门面_原画_纷争纪/：
#   card  二十二张圣牌的牌面（c01 到 c22，竖幅 2:3，照二十二张第七版的牌面，一张一幅，画里不写数和字）
#   road  路的长卷十一段（r01 到 r11，横幅 3:2，从高处斜着看的一条路，路边是这一段留下来的东西）
#   era   二十一幅时代原画（sNN_era，场面在 小样_纷争纪书/scenes/era_scenes.json）
#   cut   节点原画和死的那一刻（场面在 小样_纷争纪书/scenes/sNN.json，画法照 gpt_cg.py 光锥那一路）
#   python gpt_cg2.py c04 r04 s04_era        出这几幅
#   python gpt_cg2.py cards|road|era|scenes  出这一类的全部（出过的跳过）
#   python gpt_cg2.py falls                  传奇之陨（场面在 小样_纷争纪书/scenes/legends/g?.json 的 falls，键 sNN_f_名；scenes 那一类也带着它们）
#   python gpt_cg2.py --left [cards|road|era|scenes]   还缺哪几幅
#   CG_DRY=1 只打提示词和参考图，不出图；CG_WORKERS=5 并着出
#   FIX 里有的键、它指的上一稿又在 out 里的，走“只改一处”那一路（拿上一稿当底，别的不动）；CG_DRY 打的照旧是场面稿那一条提示词。
#   要照场面稿从头画，先把 FIX 那一条指的旧图挪开。11-13 人体那一轮的十五条都在 FIX 里。
import glob
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_cg as G  # noqa: E402    节点原画那一套提示词、对照条
import gpt_front as F  # noqa: E402
from gpt_gen import gen  # noqa: E402

OUT = os.path.join(HERE, 'out', '门面_原画_纷争纪')
ROOT = G.ROOT
BOOK = os.path.join(ROOT, '底稿', '门面', '小样_纷争纪书')
SCENES = os.path.join(BOOK, 'scenes')
K2 = os.path.join(HERE, 'out', '门面_主画_11-10', 'k2.png')            # 纷争纪主画：这一纪的颜色照它
BB1 = os.path.join(HERE, 'out', '门面_小样_11-10', 'bb3_1.png')        # 纷争纪大幅牌背：牌面跟它是同一副牌
G.POR_ALL += ['立绘_山铜纪', '立绘_前传']                               # 活到山铜纪的人（海塔、瑟尔卡这些）画在那两套里

NO_MOON = ' There is no moon and no crescent anywhere in the picture.'
# 试图里魔神的一只大弯角贴着夜空，看着就是一弯月牙
NO_ARC = (' Nothing pale and curved may stand alone against the sky where it could be read as a crescent: horns are short and straight or branching, '
          'never one great curved sweep, and no bow, blade or arc of light is drawn as a single pale curve in the sky.')

# ---------- 牌面 ----------
# 第二版（11-12）：用户说“圣牌的样式参考原神的月谕圣牌”。牌是一扇尖拱的石窗框，脚下横一条空白的缎带，画填在窗里、溢出框外，一张牌一个主色，透明底。
# 先出一张空框 cf0 当全副牌的样板（框和缎带照它），牌背 cb0 是同一扇窗关着。第一版（骨白细框的长方牌）的图在 out/门面_原画_纷争纪/牌面_第一版/。
MY = os.path.join(ROOT, '语料', '门面参考_11-10')                       # 月谕圣牌的页面截图，只当样式参考，不进库
MY_REFS = [os.path.join(MY, '月谕圣牌_%s.png' % n) for n in ('皇帝', '力量', '世界')]
CARD_FRAME0 = os.path.join(OUT, 'cf0.png')

FRAME_DESC = ("A tall narrow window frame carved from pale silver-white stone, seen perfectly flat from the front, standing upright in the middle of the canvas; "
              "it is about three fifths of the canvas wide and nine tenths of the canvas tall, with clear empty margin on every side. "
              "Its top is a steep pointed gable with a small stepped shoulder at each upper corner. Inside the gable the window opening ends in a pointed arch with a slight ogee curve, and a narrow carved band follows the arch. "
              "In the middle of the gable, above the arch, sits one small carved boss: two crossed swords under a laurel wreath that is broken open at the top. "
              "The two side jambs are narrow and straight, with one lighter bevel line along the inner edge. Below, the jambs run down past the window sill and meet in a V-shaped point like the foot of a shield, with a small plain spearhead finial at the point. "
              "In front of the lower part of the frame lies one broad ribbon of pale cloth-of-silver. Its middle band hangs across the whole width of the frame in one shallow downward curve, just below the window sill; "
              "at each side it folds back behind the frame, and its two ends sweep outward and upward to left and right and end in forked swallow-tail cuts, slightly frayed, like old war pennons. "
              "The ribbon is completely blank except for one small round stud at its centre. ")
FRAME_LOOK = ("The stone and the ribbon are pale silver-white with cool grey shading and thin lighter edge lines, matte, with a fine grain; no gold on them. ")
CARD_F0 = ("Draw one tall 2:3 portrait picture on a fully transparent background. "
           "The attached pictures are finished cards from another deck, shown on a plain dark grey backdrop; they are here only to show the kind of object to draw: a tall arched window frame of pale stone with a ribbon across its foot, cut out against the background, and the level of finish. "
           "Design a new, different frame of that same kind for our own deck, and draw it empty. Do not copy the ornament of their frames, and draw none of their pictures. "
           "Our frame. " + FRAME_DESC +
           "The window. The opening of the window is empty: fill it with one flat even mid-grey and nothing else, as a placeholder. "
           "Drawing manner: flat stylized game illustration, clean flat shapes with crisp edges, simple two-step shading, exquisitely made and precise. " + FRAME_LOOK +
           "Crisp clean outer outline against the transparent background, and nothing else on the canvas: no shadow on the background, no glow, no floating bits, no dark grey backdrop.")
CARD_LEAD = ("Draw one tall 2:3 portrait picture on a fully transparent background: one card of a deck of twenty-two picture cards. "
             "Each card of this deck is a tall arched window frame of pale stone with a ribbon across its foot, cut out against the transparent background; a picture fills the window and breaks out over the frame. "
             "The first attached picture is the approved empty frame of this deck. Reproduce exactly this frame and this ribbon: the same shape and proportions, the same position and size on the canvas, the same pale silver-white stone, the same carving, the same blank ribbon. "
             "Replace the flat grey placeholder in its window with the picture described below. "
             "The other attached pictures are finished cards from a different deck, shown on a plain dark grey backdrop. They show the finish to match: how the picture inside the window is drawn, how one colour rules each card, "
             "and how parts of the picture overlap the frame and the ribbon and spill out past them. Take only that manner from them: do not copy their subjects, figures, symbols or compositions, do not use the ornament of their frames, "
             "and do not reproduce their dark grey backdrop, because our background is transparent. ")
CARD_LAYOUT = (" Layout. Inside the window everything is one picture, composed like a tarot trump or a stained-glass window: emblematic, frontal and still, the main figure or object large and clear in the middle, the ground low in the window, "
               "the sky or backdrop above built from a few large layered shapes with a faint pattern. The picture has three depths: the backdrop stays inside the window, behind the stone; the main subject stands in the window; "
               "and the things named under 'Breaking out' are drawn in front of the stone frame and the ribbon, overlapping them and reaching into the transparent margin, so that the picture seems too large for its window. "
               "A few small loose motifs that belong to this picture (sparks, leaves, feathers, shards or drops, as fits it) float in the margin close around the frame. "
               "The small everyday scene named at the end of the description sits small in one lower corner of the window, just above the ribbon, like a footnote. "
               "The frame and the ribbon stay clearly readable as a frame and a ribbon, and the boss in the gable stays visible. The middle band of the ribbon stays clear and blank for most of its width, on both sides of its stud, because a motto will be engraved there later: things that break out at the foot of the card overlap only the ribbon's upper edge, its two folds or its two ends.")
CARD_LAYOUT_BARE = (" Layout. The window shows one quiet picture and nothing else. Nothing is drawn in front of the stone frame or the ribbon, nothing overlaps them, and the transparent margin round the frame is completely empty.")
CARD_STYLE = (" Drawing manner: flat stylized game illustration in the manner of the reference cards: clean flat colour shapes with crisp edges, layered like cut paper, simple two-step shading, soft inner gradients, "
              "small geometric patterns and sparkles, thin lighter echo lines along the edges, a fine paper grain; exquisitely made, precise and jewel-like. "
              "Figures are simplified and emblematic, with small calm faces or faces turned away; no portrait likeness. No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D. "
              + FRAME_LOOK + "They keep this same pale silver-white on every card of the deck; only the picture changes colour. "
              "Crisp clean outer outline against the transparent background; no shadow, glow or haze on the background, no dark backdrop, and nothing in the margin except what is named.")
CARD_BACK = ("Draw one tall 2:3 portrait picture on a fully transparent background: the back of the cards of a deck of twenty-two picture cards. "
             "The first attached picture is the approved empty frame of this deck. Reproduce exactly this frame and this ribbon: the same shape and proportions, the same position and size on the canvas, the same pale silver-white stone, the same carving, the same blank ribbon. "
             "The second attached picture is a finished card from a different deck and shows only the level of finish; copy nothing from it. "
             "On the back of the card the window is shut. Replace the flat grey placeholder with a pair of tall narrow door leaves of dark iron-grey that meet in the middle and fill the whole opening, bound with three plain bands and a row of small rivets, "
             "with a faint pattern of fine diagonal lines on the dark metal. Across the two leaves, in the middle, lies one emblem in plain bone white: two crossed swords, points down, under a laurel wreath that is broken open at the top. The blades are clean: no blood, no drips, no stains. "
             "A thin line of dark dried-blood red runs round the inside edge of the opening. Nothing is drawn in front of the stone frame or the ribbon, and the transparent margin round the frame is completely empty. "
             "Drawing manner: flat stylized game illustration, clean flat shapes with crisp edges, simple two-step shading, a fine paper grain; exquisitely made and precise. " + FRAME_LOOK +
             "Crisp clean outer outline against the transparent background; no shadow, glow or haze on the background, no dark backdrop.")

# 一张牌一个主色（月谕圣牌每张一个颜色）。后半句是这一张里唯一许出现的别的颜色。
HUE = {
    1: ('a cold glacier cyan against blue-black night', 'the only warm notes are the small red mouth of the oven and a touch of pale gold on the four things on the table'),
    2: ('a soft ash grey with a lilac cast', 'the only accent is a little ember orange along the charred edges of the paper'),
    3: ('a warm straw gold', 'the wild left half is a dark moss green, and that is the only second colour'),
    4: ('a deep rust red, the red of baked earth', 'iron grey for the armour and the spears and bone white for small lights are the only other tones'),
    5: ('a warm ivory and pale holy gold', 'small touches of deep wine red in the robe and the cup are the only accent'),
    6: ('a deep pine green', 'the god is drawn in pale mint and white, and a little warm gold marks the golden hilt in the corner scene'),
    7: ('a clear sky blue with cream-white stone', 'small touches of warm brown for the harness and the cart are the only accent'),
    8: ('a tawny amber, the colour of a lion', 'a little cream white for the wall and the dress is the only second tone'),
    9: ('a deep midnight indigo', 'the lanterns are a warm yellow and are the only other colour, and each lantern is a small sharp warm light, never a large glowing disc'),
    10: ('a hot vermilion, the colour of flame', 'the green half of the earth is one small patch of fresh green and the other half is black'),
    11: ('bone white and black, with a cool steel blue-grey between them', 'there is no other colour except the white of the steam'),
    12: ('a dusky mauve', 'the running light is a honey gold and is the only second colour'),
    13: ('a dusty rose, the colour of a cold dawn', 'the white of the horse and a few black shapes are the only other tones'),
    14: ('a bright turquoise, the colour of a clear river', 'small touches of warm coral on the banners are the only accent'),
    15: ('a dark wine magenta', 'the small campfire in the corner scene is the only warm orange'),
    16: ('a storm slate-blue', 'the bolt and the three sun-discs are a sharp pale yellow and the dunes a dull sand, and those are the only other colours'),
    17: ('a luminous cobalt blue', 'the stars and the wall are silver-white, and that is the only second tone'),
    18: ('an iron slate grey', 'a dull verdigris green on the iron wolf and the pool, and one small orange fire in the corner scene, are the only accents'),
    19: ('a bright sun yellow', 'a clear sky blue and the white of the wall and the horse are the only other tones'),
    20: ('a pearl white with a faint peach-gold warmth', 'dove grey for the two armies and the coffins is the only second tone'),
    21: ('a fresh spring leaf green', 'the rain is a soft grey, the wild flowers are small dots of white, yellow and pink, and the fire by the basket is one small warm orange'),
    22: ('a pale grey-blue, almost colourless', 'there is no accent at all'),
}
# 画里哪几样东西压在石框和缎带前面、伸到框外。第二十二张什么也不出框。
BREAK = {
    1: "the tall dark shadows that rise out of the cracks climb out of the window on both sides and lean over the two jambs, each taller than the last; the split in the ground runs forward to the upper edge of the ribbon. The robed figure's head and raised forearm stay hidden behind the gable and do not reappear above it.",
    2: "the flakes of ash hang perfectly still outside the window too, all round the frame; the charred roll of paper rests against the upper edge of the ribbon, at one fold; the top of the cracked right pillar stands in front of the gable's right shoulder.",
    3: "the tangle of wild horned stalks on the left grows out over the left jamb and up past the gable's shoulder; on the right the three bound sheaves lean out over the right fold of the ribbon. The empty chair stays inside the window.",
    4: "the forest of spear points rises out past the gable and both its shoulders; the upside-down crown rests against the upper edge of the ribbon, at one fold; red dust drifts out at both sides.",
    5: "the back of the high seat and the straight rays behind the god's head rise in front of the gable; the two crossed keys rest against the upper edge of the ribbon, at one fold; the first and the last of the seven doors stand just outside the two jambs.",
    6: "the god's great open hand and forearm reach down from above the gable, in front of the stone; the foot of the mountain spreads down to the sill; the two long shadows fall forward down to the sill, and the two horns of the left shadow, plain to see, just reach over the upper edge of the ribbon.",
    7: "the heads and horns of the two oxen and the front of the cart come forward over the sill and the upper edge of the ribbon; the white wall runs on past both jambs to left and right; the last block hangs on its ropes in front of the gable.",
    8: "the lion's mane and its tail sweep out over one jamb and one fold of the ribbon; the garland of stag antlers hangs across in front of the lower frame, its two ends reaching past both jambs.",
    9: "the hands that hold the lanterns reach in from outside the window, across the two jambs, by turns from the left and from the right, so that the sleeves lie in front of the stone; a few sparks drift outside.",
    10: "the wheel of flame is wider than the window: its rim passes in front of both jambs and tongues of flame lick out into the margin; the single drop of blood hangs just above the ribbon. The four faceless shadows sit on the outside of the frame, two on the shoulders of the gable and two on the ends of the ribbon.",
    11: "the sword is taller than the window: its pommel and grip stand in front of the gable and its point comes down to the upper edge of the ribbon; the two empty pans of the balance hang level in front of the two jambs. The black half and the white half of the picture stop at the stone, and the frame itself stays pale.",
    12: "the free end of the beam and the loose ends of the pale ribbon reach out past the right jamb; the pale gold light that runs down gathers in a small pool on one fold of the ribbon; a few drops of the same light hang in the margin.",
    13: "the white horse is walking out of the window to the left: its head, neck and one raised foreleg are in front of the left jamb; the barrel of the abandoned cannon juts forward over one fold of the ribbon; the long grass grows up over the sill.",
    14: "the river runs forward over one fold of the ribbon and falls from it in a few drops; the banner on the city wall flies out past one jamb and the two open banners on the far bank fly out past the other.",
    15: "the horns of the dark thing on the seat rise in front of the gable, one on each side of the boss; the two loose chains hang forward in wide loops over the two folds of the ribbon.",
    16: "the falling tower tips out of the window through the upper right, its top in front of the right shoulder of the gable; the jagged bolt comes down out of the margin at the upper left, across the gable; the three sun-discs tumble away into the right margin, each smaller than the last; a little sand blows out at the bottom.",
    17: "the large eight-pointed star stands above the window, in front of the top of the gable, with the seven small stars scattered in the margin round it; the water poured onto the dry ground runs forward over one fold of the ribbon and drips from it.",
    18: "the dog sits outside the window on the left, in front of the left jamb and the end of the ribbon, and the iron wolf sits outside it on the right, both with heads lifted, howling; the long crack in the false sky does not stop at the window but runs on up across the stone of the gable itself; the crayfish climbs out over one fold of the ribbon.",
    19: "the straight rays of the large sun reach out past the gable into the margin all round the top; the long banner the child holds streams out over the right jamb; the ears of the ripe wheat stand up along the sill, just overlapping the upper edge of the ribbon.",
    20: "the great war horn hangs above the window, in front of the gable, and the rings of sound from its mouth spread out into the margin; the open lids of the nearest stone coffins lean forward over the sill and the upper edge of the ribbon; the lowered spears of the two armies cross the jambs at left and right.",
    21: "the great wreath is larger than the frame: it circles the whole frame, passing in front of the jambs, the shoulders and the two ends of the ribbon, with its gap at the very top, above the gable; the four faceless shadows are outside the wreath, near the four corners of the frame.",
}

CARDS = {
    1: ("The picture: a table set with four things in a row: a ring, an unlit lamp, a key and a seal. Behind the table stands a robed figure, one arm raised straight up pointing at the sky and the other pointing down at the earth. "
        "He is too tall for the window: the top of the arch cuts him off at the shoulders, and his head and the hand of his raised arm are out of sight above it, behind the stone gable, so that his face is not on the card at all. We see him only from the shoulders down, the raised arm going straight up and out of sight at the elbow. He is not headless and there is no empty collar: his shoulders touch the very top of the opening, and the robe and the arm simply continue upward behind the stone. "
        "Under the table the ground has split open, and tall dark shadows rise out of the cracks one behind another, each taller than the last. "
        "In one lower corner, small: a little window of a poor street, and through it someone kneading dough beside an oven whose mouth still glows red."),
    2: ("The picture: two tall pillars. The left pillar is whole and finely carved; the right pillar is bare, cracked and scorched. Between them hangs a thin veil, and behind the veil there is no one: only empty dark. "
        "At the foot of the pillars lie a roll of paper with charred edges and a small heap of grey ash, and all through the air between the pillars flakes of ash hang perfectly still: not one of them is falling. "
        "In one lower corner, small: someone crouches in the ash, picking burnt grains of wheat out of it one by one into a cupped hand."),
    3: ("The picture: a field seen from the front, divided down the middle. The left half grows wild and too tall, a tangle of stalks, and what grows there ends in small straight horns like a young goat's instead of ears of grain. The horns are short, straight, dark cones, almost black: never curved, never pale and never yellow. "
        "The right half is reaped clean and neat, and its harvest stands bound in exactly three sheaves. In the very middle of the field, on the dividing line, stands one plain high-backed chair, and nobody sits on it. "
        "In one lower corner, small: beyond the bank of the field a little wedding procession wades across a ditch, the bride lifted over the water."),
    4: ("The picture: a wide plain of red earth under a sky the colour of iron. In the middle stands a seat of rough stone, and on it sits an armoured figure in a closed helm with the visor down, both hands resting on the pommel of a great sword that stands point-down before him. "
        "Behind him the points of spears rise as thick as a forest. He wears no crown: a plain crown lies upside down in the red earth beside his foot. "
        "In one lower corner, small: a far village where someone winnows grain, and all the chaff flies one way."),
    5: ("The picture: on a high seat sits a tall calm god in long robes, holding up a cup in one hand. Two keys lie crossed on the step at the god's feet, laid down, not held. "
        "Below the seat kneels an armoured figure in a closed helm, seen from behind, asking. Behind the kneeling figure stand seven doors in a row, each of a different make: living wood, bronze set in rock, hide and bone, a gate among clouds, white temple stone, a round door in a green hill, and last a plain gap between two wagons. "
        "On the surface of the wine in the cup a tiny desert of sand dunes is reflected. "
        "In one lower corner, small: through the crack of a door a family sits eating at a table, and one extra place is laid with nobody at it."),
    6: ("The picture: a single mountain in the middle, and two travellers standing one on each side of it, facing each other across it. Above the peak a god leans out of the sky, drawn as a large pale figure seen to the waist, one open hand stretched down over both of them in blessing. "
        "Each traveller casts a long shadow on the ground toward us, and the shadow of the one on the left has two horns, though the traveller himself is hooded. "
        "In one lower corner, small: on a mountain pass two soldiers exchange weapons, one holding out a knife with a golden hilt and the other a knife of plain iron."),
    7: ("The picture: a heavy cart loaded high with blocks of white stone, drawn by two great draught oxen, one white and one black, seen from the front and a little to one side. "
        "The driver standing on the cart is an old dwarf with only one arm; the hand he has left grips a mason's hammer raised to his shoulder. "
        "Behind the cart a long white battlemented wall runs across the whole picture from edge to edge, and at its middle the last gap is just being closed: one last block is being lowered into place by ropes. "
        "In one lower corner, small: at the foot of the wall a few masons squat eating, their bowls set on the freshly laid stone."),
    8: ("The picture: a woman in a plain long dress and a hooded cloak stands beside a great lion and gently closes its jaws with both hands; the lion lets her. "
        "Behind her rises the top of a white battlemented wall, and on it people stand in rows one behind another, row above row, and each row is younger than the one in front of it: grey-bearded in the front row, then grown men and women, then youths, the last faces almost children. "
        "A long garland of stag antlers hangs along the wall under their feet. "
        "In one lower corner, small: in a courtyard inside the wall an old man teaches a grandchild to draw a small bow."),
    9: ("The picture: night, a steep mountain path that zigzags up the whole card from the bottom to the top. Along it burn lanterns one above another, and a hand holds each lantern in from the side of the path: only the hands and sleeves are shown, and no two are alike: "
        "the wide sleeve of a scholar's long robe, a soldier's leather bracer, a hand that also holds a tower key on a ring, a craftsman's black leather glove. Each lantern has plainly been lit from the one below it. "
        "At the top of the path stands one small hooded figure who holds a lantern out and shines it back down the path. "
        "In one lower corner, small: a village at the foot of the mountain, where the wheel of a mill is turning."),
    10: ("The picture: one great wheel made of flame, filling the middle of the card. Down its left side a snake slides head-first; up its right side climbs a thing with the head of a beast. From the lowest point of the rim one single drop of blood is falling. "
         "Four faceless shadows sit on the outside of the stone frame, one at each of its four corners, each with its head bowed over something it reads, as if counting. "
         "Below the wheel lies the earth, half of it still green and half already black. "
         "In one lower corner, small, on the green half: someone mowing grass with a scythe."),
    11: ("The picture: the whole card is split exactly down the middle, the left half bone white and the right half black, and one sword stands upright, point down, on the dividing line. "
         "From the sword's crossguard hangs a balance whose two pans are both empty and level. On the ground under the balance lie a single arrow and a ring of pale light with a piece broken out of it. "
         "Far behind, a straight line is drawn across the ground from edge to edge, and beyond that line nothing grows. "
         "In one lower corner, small, on the near side of the line: a workshop with a tall chimney pouring white steam, and a few leather aprons hung to dry by its door."),
    # 头一稿写成 gallows、hangs by one ankle，出图那边按自伤和暴力拦了；照塔罗第十二张那个安静的倒悬写
    12: ("The picture: one tall plain stone pillar stands in the left part of the window, and from its capital a single short stone beam juts out to the right only, like a bracket or an upside-down letter L. It must not look like a cross: nothing rises above the beam, and the beam does not cross the pillar. Beneath the free end of the beam, beside the pillar, a serene god floats head-downward in the air, exactly in the calm pose of the twelfth trump of the classic tarot: "
         "one foot rests against the beam, held there by a loop of pale ribbon, the other leg is crossed lightly behind it, the hands are folded behind the back, the eyes are open and the face is perfectly peaceful, and the long robe falls neatly. "
         "The god is weightless, unharmed and at rest, like a figure in a stained-glass window; nothing about it is violent. "
         "The ring of pale gold light that belongs round the god's head is running down like water, along the body and into the stone of the pillar, which glows faintly where the light has soaked in. "
         "Far behind, one thin white line is drawn across the ground. "
         "In one lower corner, small: at the foot of the pillar a messenger with a fox's ears and tail sits changing shoes, and the sole of the old shoe is worn right through."),
    13: ("The picture: a white horse walking from right to left, saddled and bridled, with nobody in the saddle; yet on the ground beside it lies the shadow of a horse with a rider. "
         "Before the horse stands a short queue of people waiting, facing it: one who wears a crown, one in a priest's long robe, a child with small horns, and an old person with long pointed ears. "
         "In the long grass in the foreground lies an abandoned cannon, its barrel carved with marks. The saddle cloth, the robes and any flag are patterned only with plain diamonds and dots: no fleur-de-lis, no lilies and no heraldic flowers anywhere. Far off, between two towers on the horizon, the top edge of a rayed sun is just rising. "
         "In one lower corner, small: at the end of the queue two bearers carry a stretcher, and the wounded one lying on it is drinking from a cup."),
    14: ("The picture: a broad river. In the middle of it a ferryman stands on a rock that rises out of the water, and pours water in a long thin stream from one cup into another without spilling a drop. "
         "On the near bank stands a walled city, and one banner with a plain device of a rising sun's rays flies on its wall. On the far bank two banners are planted in the ground and stand open, and a third beside them is still furled round its staff. "
         "In one lower corner, small: a market on the bank, where a woman selling wool weighs it on a hand scale."),
    15: ("The picture: this card is the mirror of a card with a god on a high seat, turned dark. On a high seat of black stone sits a horned thing, a dark reflection of a god, drawn as a tall shadow with a faintly gleaming outline and no face. At its feet stands one bowl filled with something dark red. "
         "Below the seat stand two horned people, a man and a woman, each with a pair of small dark horns plainly visible above the forehead, each tethered to the seat by a chain round the neck; the chains hang so loose and the loops are so wide that they could lift them off over their own heads. "
         "In one lower corner, small: in a camp at the foot of the seat someone toasts bread on a stick over a small fire."),
    16: ("The picture: a tall tower that floats in the air on a great rock is struck from above by a jagged bolt and is tipping over, falling head-first. "
         "The disc of the sun that crowned it has flown off and broken into three: three whole round rayed sun-discs, each smaller than the last, tumbling away to the right. Two small figures fall from the tower with their arms spread. "
         "Below is a sea of sand dunes. "
         "In one lower corner, small: along the edge of the sand a caravan of camels walks on toward the east as before; the leader carries a crown strapped on his back, and not one of them looks up."),
    17: ("The picture: in the upper sky one large eight-pointed star and seven small ones around it. Below it a white battlemented wall runs across the card, and on the wall stand seven stone pillars in a row: six are carved, each with a different plain device, and the seventh is perfectly smooth and blank. "
         "In the foreground an elf woman with long pointed ears kneels on one knee at the edge of a small pool, a jar in each hand, pouring one jar into the pool and the other onto the dry ground. "
         "In one lower corner, small: in a vegetable patch below the wall someone waters the rows from a can."),
    18: ("The picture: a road runs straight away from us between two tall watchtowers. On the left of the road sits a dog and on the right a wolf made of riveted iron plates, and both lift their heads and howl at the same sky. "
         "In the middle of the road, further off, kneels a soldier cast of iron, seen from behind, with a large wind-up key standing in its back, stopped; its face is turned away from us, toward the far end of the road. "
         "In the sky there is no heavenly body at all, no sun and no star: only a flat painted false sky with one long crack in it, and from the crack water drips. "
         "In the foreground a crayfish climbs out of a small dark pool toward the bank. "
         "In one lower corner, small: in the gateway under one watchtower a night watchman warms his hands at a small fire."),
    19: ("The picture: bright morning, a large rayed sun high in a clear sky. A white battlemented wall runs across the card, and on top of it a child rides a white horse bareback and holds up a long banner with both hands. "
         "Below the wall four small travellers come home in a line from the right, from the south, one behind another: a young swordsman, a tall priest, a short broad dwarf and a slender elf with a staff: four of them, none missing. "
         "Along the foot of the wall grows a single row of ripe wheat. "
         "In one lower corner, small: far out on a sea, the roofs of a city are sinking under the water, and there are still people standing on the roofs."),
    20: ("The picture: high in the sky hangs a great war horn, sounding, with rings of sound spreading from its mouth, and no one blows it. Below, rows of stone coffins stand with all their lids open, and not one of the sleepers inside has sat up. "
         "In the middle distance two armies face each other across an open strip of ground, and every spear and sword on both sides hangs lowered; between the two armies stands one small plain woman in a long dress and a headcloth, seen from behind. "
         "Far beyond them nine tall shadows have stopped halfway across the plain. Beside that halfway place stands a balance, forgotten: one of its pans has sunk right to the ground, and nobody is looking at it. "
         "In one lower corner, small: in the camp behind one army someone is already striking a tent."),
    21: ("The picture: a great wreath of leaves and wild flowers circles the whole card, lying in front of the stone frame, and at its very top a piece is missing, so that the wreath is open toward the viewer like a gap left in a ring. "
         "Inside the window we look into the arched gateway of a small town built against the foot of a great white wall; outside the arch grey rain falls in straight lines, and inside the arch, beside a small fire, stands a basket with a blanket in it. "
         "Seven thin threads of pale light fall slanting into the basket, and an eighth, fainter than the seven, comes in from the upper left and stops in mid-air, unfinished. "
         "Outside the wreath, near the four corners of the frame, are four faceless shadows: one like something that is still growing, one that holds a pen, one like wind pressing all in one direction, and one that fences its corner off neatly with straight lines. "
         "In one lower corner, small, just outside the gateway: someone carries two buckets of water home through the rain."),
    22: ("The picture: almost nothing. The window shows only the bare edge of a high cliff, seen from behind and a little above: flat rock in the lower third, ending in a clean broken edge, and beyond the edge only pale empty air filling the upper two thirds. "
         "Nothing and no one stands on the edge. There is no small corner scene on this card. Leave it quiet and empty."),
}

# ---------- 路的长卷 ----------
ROAD_LEAD = ("Draw one wide 3:2 landscape picture: one section of a very long painted scroll that follows a single road across a war-torn land through the eleven thousand years of one war. "
             "The view is from high above and to one side, a bird's-eye three-quarter view. The horizon is very high in the picture, about one eighth from the top, so that almost the whole picture is ground seen from above. "
             "One pale dusty road enters at the middle of the left edge, winds across the land in two broad lazy bends, the first swinging down toward the bottom of the picture and the second up toward the horizon, and leaves at the middle of the right edge. "
             "The road itself is empty: no one walks on it and nothing lies on it. At the outside of each of the two bends there is a small bare level patch of ground beside the road, clear of everything, like a place kept empty for a standing stone. "
             "Along both sides of the road lies what this stretch of the war left behind, set out small and clear like pieces on a table. ")
ROAD_EDGE = (" The far left and the far right of the picture, about one twelfth of the width on each side, are veiled in thick pale drifting smoke with nothing important in them, so that this section can be joined to its neighbours.")
ROAD_STYLE = (" Drawing manner: the attached pictures are approved plates of the same series; match their hand exactly: large calm flat colour shapes layered like cut paper, thin lighter echo lines along the edges, soft inner gradients only, a fine paper grain over everything. "
              "Things are simplified into clean silhouettes, with plenty of quiet ground between them. Nothing is drawn in close-up; everything is small and seen from above. "
              "The fallen are shown with restraint: still shapes under cloaks and shields, helmets set on swords planted in the earth, riderless horses standing; no blood, no wounds, no faces. "
              "No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D, no picture frame, no border. Take only the drawing manner and the palette from the attached plates, not their compositions. "
              "Palette of this series: iron grey, slate blue-grey, dark dried-blood red, bone white, pale gold only for holy light, and small warm orange only for fires.")

ROADS = {
    1: ("This section: the first night of the war and the grey years after it. The land is buried under pale grey ash, drifted like snow, and flakes of ash hang in the air. "
        "On the left, on both sides of the road, lie the fallen lamp-towers of a great city: tall slender white towers lying broken across the ground where they came down, their great lamps dark, and under the ash the ground still glows faintly along the arcs of enormous circles that were once drawn there, each arc far wider than the picture. "
        "Among the fallen towers one small bakery stands whole, its oven door open and glowing: the only warm light in the picture. "
        "Toward the right the ash thins: the burnt shell of a library with charred pages lying round it, abandoned book chests, a handcart, and far off a walled town with a few torches at its gate. "
        "The sky strip at the top is black night, and along the horizon tall dark shadow shapes are rising out of cracks in the earth, each taller than a tower.", True),
    2: ("This section: the first hundred and eighty years. On the left the fields have gone wild: wheat grown half mad, taller than a man and tangled, some stalks ending in small straight horns, with three neat sheaves standing at its edge and, far off, three small plain banners, one white, one blue-grey, one straw gold. "
        "By the first bend a frozen river crosses the land; on the ice at a ford one old long white sword stands upright, still in its sheath, a string of ivory beads tied to its hilt. "
        "Toward the right the earth turns red and scorched: long glassy fused streaks where fire ran along the ground, a forest of broken spears standing in the earth, charred helms with horns, one torn white banner with a plain device of rising rays still standing, a saddle with no horse; "
        "and at the far right long straight ramparts of red earth heaved up in ranks, with rune-marked shovels left standing in them. "
        "The sky strip at the top is the colour of iron, full of smoke, with a dull red glow low on the left.", True),
    3: ("This section: the gathering of the peoples and the long march west. On the left seven doors stand alone in the open land in a row beside the road, each of a different make and none attached to any wall: an arch of living wood, a bronze door set in a block of rock, a door frame of hide and bone hung with small bells, a tall gate with a pair of great wings carved on its posts, a white stone temple door, a round door set in a little green mound, and the seventh only a gap between two parked wagons with a pale cloth hung across it. "
        "Past the first bend the land turns to dark marsh with a line of stepping stones and standing dead reeds; beyond it lie the bones of one great winged wyrm, half sunk, and far off thirteen small ruined walled towns, drawn tiny. "
        "By the second bend stands a stone gate in a mountain pass, an iron knife hanging on its post, and beyond the gate, toward the right, many horned helms set on swords planted in the earth. "
        "The sky strip at the top is dark red on the right and slate on the left, with seven tiny winged wyrms flying in a line.", True),
    4: ("This section: the building of the long white wall and the first four hundred years of holding it. Along the top of the picture, just under the horizon, a long white battlemented wall of stone runs across the whole width from edge to edge. "
        "On the left it is still being built: wooden scaffolds, carts loaded with white blocks, a mason's hammer left on a block, and along the line of its foundation a row of swords planted in the earth hilt-upward. Near them stands one flat stone covered all over with tiny scratched marks. "
        "From the first bend on the wall is finished; at one place it has a notch that has been mended many times with newer, paler stone, and before that notch the ground bristles with spent arrows standing as thick as grass. "
        "By the second bend stands a small watch-tower hung from top to bottom with row upon row of stag antlers. Behind the wall, tiny, lie fields and a farmstead; in front of it, shields laid over still shapes, and helmets on planted swords. "
        "The sky strip at the top is pale slate.", True),
    5: ("This section: the years of the lamps and the day the first god fell. The long white battlemented wall runs along the top of the picture from edge to edge, just under the horizon. "
        "On the left a small hill path climbs to a plain stone hall with one lamp burning over its door, and a string of small lanterns stands along the path, each a little warm point; beside the hall are practice yards with straw targets and a rack of blunted spears. "
        "Past the first bend, in front of the wall, stands one enormous round shield, taller than the wall itself, planted upright in the earth like a monument and cracked from rim to boss. Around it the ground is scorched in a wide ring, and inside the ring the trees stand with their roots in the air and the grass is ash-white. "
        "A whole front rank of ordinary shields lies where it was thrown down, and beyond them a tall dark tower lies fallen on its side, burst open, spilling thousands of blades. "
        "On the wall near the right the first few cannon stand between the battlements, their barrels carved with marks. The sky strip at the top is dark slate with one long pale gold streak falling toward the great shield.", True),
    6: ("This section: the years of the furnaces, and the gods walking south. The long white battlemented wall runs along the top of the picture from edge to edge, and now cannon stand all along it between the battlements, their breeches glowing faintly blue-white. "
        "On the left, behind the road, a row of workshops with tall chimneys pours white steam; beside them lie the split shells of burst furnaces, seventeen of them, like cracked iron eggs, and one whole furnace still glows through its door. "
        "Across the lower part of the picture one thin straight line is drawn on the ground from edge to edge; below that line the land is bare and grey and nothing grows. "
        "Past the first bend a file of colossal pale figures, each taller than a tower, walks away from us toward the lower right, across that line and into the bare land: gods, drawn only as faint bone-white silhouettes, each fainter and smaller than the one before, none looking back. "
        "By the second bend, on a flat stone beside the road, lie a plain crown and a folded cloak; near them a pair of worn-out boots. Below the wall lie broken cannon barrels. "
        "The sky strip at the top is iron grey.", True),
    7: ("This section: the dead land, the great cannon, and the first towers to leave the ground. The long white battlemented wall runs along the top of the picture from edge to edge; behind it a line of raised rails runs along the wall. "
        "The lower half of the picture is a dead land: the grass is white, and every piece of old iron lying in it has put out flowers of rust. "
        "On the left one cannon as long as a ship lies on its side in the white grass, its barrel carved with marks; near it a white winged horse stands alone, saddled, with no rider. Beside the road stands a field hospital of white tents with rows of empty stretchers. "
        "Past the first bend an armoured train lies off its rails below the wall, its engine still glowing faintly; and near it kneels one great steam-driven war machine shaped like an armoured giant three storeys tall, rusted fast, flowers of rust all over its shoulders. "
        "By the second bend three small banners lie fallen and two new ones stand planted; and above them, at the upper right, one slender tower is rising into the air on a great floating rock, chains hanging from its foot. "
        "The sky strip at the top is dull slate, darker toward the bottom right.", True),
    8: ("This section: the blood feasts and the falling of the towers. The long white battlemented wall runs along the top of the picture from edge to edge, far off and small. "
        "On the left the ground is dark red: there stands a high seat of black stone, empty, with a long feast table overturned before it, bowls scattered on the ground and two loose chains lying open. On a hill beside it one single arrow as tall as a tree stands planted in the earth. "
        "Past the first bend the land turns to a sea of sand dunes, in places fused into grey glass. Slender towers that once floated in the air lie fallen all across it, half buried, each beside the cracked rock that carried it; one more is still falling in the distance, head-first. "
        "Three great round rayed sun-discs lie half sunk in the sand, far apart from one another. Along the road, small stones are set at even distances, with no marks on them. "
        "By the second bend one big blown-glass lantern of a fallen tower still burns low. The sky strip at the top is dark, and at the far right a red sun sits on the horizon as if it had stopped there.", True),
    9: ("This section: the years of clockwork and iron wolves, when no living thing could walk the dead land. The long white battlemented wall runs along the top of the picture from edge to edge, and on it stand seven stone pillars in a row, six carved and the seventh smooth. "
        "In front of the wall, on the left, lies one enormous broken horn, as long as a fallen tower. "
        "The whole lower part of the picture is the dead land, white grass and rust flowers, and it is full of clockwork soldiers: hundreds of them, man-shaped figures of iron, each with a large wind-up key standing in its back, all kneeling on one knee and all facing the same way, toward the wall. Their keys have stopped. "
        "Among them lie iron wolves, riveted and jointed, fallen in heaps, and a few tracked iron wagons stuck in the sand. "
        "Past the second bend two colossal armoured giants, each taller than the wall, kneel at the edge of the dead land with their heads bowed and their hands on the ground. On a post beside the road hangs one small bell. There is no living person anywhere. "
        "The sky strip at the top is flat dark grey with no sun and no stars, like a painted ceiling, with one long thin crack in it.", True),
    10: ("This section: the brightest morning of the whole war, and the day the fighting stopped. The long white battlemented wall runs along the top of the picture from edge to edge, shining in clear morning light, and a single row of ripe wheat grows all along its foot. "
         "On the left, in the dead land below, there is one perfectly round patch of pure white ground where nothing grows and nothing rots; four small sets of footprints lead out of it toward the wall. "
         "Far off beyond the wall the land is cut by one perfectly straight chasm, as if by a single sword stroke, and beyond that lies a sea with the roofs of a drowned city just showing above the water. "
         "Past the first bend, by a grey shore, a ring of white salt has been drawn on the ground, wide as a town, and inside it lies the dark shape of something vast and dead, drawn only as a flat shadow. Beside a cold campfire a bowl lies upside down. "
         "By the second bend two great camps face each other across an open strip, and every weapon in both has been laid down: spears stacked in sheaves, swords planted in rows, shields leaning. War horns hang on the wall, unblown. "
         "From that place on, toward the right, the roadside is perfectly clean: no helmets, no shields, nothing. The sky strip at the top is pale clear gold.", True),
    11: ("This section: the last one. Grey rain, and then the first dawn. The long white battlemented wall runs along the top of the picture, and rust-brown war horns hang on it in a row. "
         "On the left a small poor town is built against the foot of the wall, its roofs wet. In the town's own low wall is one arched gateway; inside the arch a small fire burns, and beside the fire stands a basket with a blanket in it. "
         "Grey rain falls in straight thin lines over the whole left half of the picture. The road passes the gateway and runs on. "
         "This is the road after the war has ended, and the land beside it is clean: there are NO helmets, NO swords, NO shields, NO spears, NO graves, NO bones, NO cloaked shapes, NO wrecked carts or engines and NO ruins anywhere in this picture. "
         "Beside the road there is only wet grass turning green, small wild flowers, a few low smooth stones, one or two young trees, and a pair of horses grazing free without saddles. "
         "The first of the two bare level patches lies beside the first bend, not far from the gateway; the second lies at the very end of the road, on the flat top of the cliff at the far right. "
         "Toward the right the rain thins and stops. The land ends at the far right in the bare edge of a high cliff with nothing standing on it, and beyond the edge there is only light. "
         "The sky strip at the top is rain grey on the left and at the upper right it opens into pale gold and white: the first light of a dawn, rising from behind the cliff. "
         "Do not veil the right side of this picture in smoke: let it end in that clean light.", False),
}

# ---------- 时代原画 ----------
ERA_LOOK = {'night': ['pv1_a.png', 'pv1_b.png'], 'dusk': ['pv1_c.png', 'pv1_a.png'], 'day': ['pv1_c.png', 'pv1_d.png'], 'rain': ['pv1_f.png', 'pv1_a.png']}
ERA_STYLE = (" Drawing manner: the attached pictures are approved plates of this very series, and the new plate must look as if the same hand had painted it for the same film. "
             "Match them exactly: the same shape language, line weight, paper grain, softness, inner glow and level of detail. "
             "Large calm flat colour shapes layered like cut paper; the vast things in the picture are drawn as overlapping pale cut-paper silhouettes that curve around the small focal point like waves, "
             "with thin lighter echo lines running along their edges; people are tiny and simplified; lights glow softly from within; plenty of quiet empty space; soft inner gradients only; a fine paper grain over everything. "
             "The colours are those of the FIRST attached picture, a plate from the same book about this age of war (that plate is a map-like view from high above: take only its colours and its hand from it, never its viewpoint or anything drawn in it): "
             "iron grey and slate blue-grey, dark dried-blood red, bone white, a little pale gold for holy light, and small warm orange flames as the only warm accents. "
             "Keep it simple and airy: no dense ornament, no gothic tracery, no heraldic shields or coats of arms, no ornate picture frame, no border. "
             "No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D render. No blood and no wounds. "
             "Take only the drawing manner and the palette from the attached plates. Do not copy their compositions, and do not bring in any figure, beast, tower or building from them that the scene above does not name.")

S = {'cf0': dict(kind='frame0'), 'cb0': dict(kind='back')}
for _i, _t in CARDS.items():
    S['c%02d' % _i] = dict(kind='card', text=_t, n=_i)
for _i, (_t, _edge) in ROADS.items():
    S['r%02d' % _i] = dict(kind='road', text=_t, edge=_edge)


def beast_path(name):
    if name.startswith('god_'):
        return os.path.join(HERE, 'out', '神明显像', name + '.png')
    return os.path.join(HERE, 'out', '史诗战', name.rsplit('_', 2)[0], name + '.png')


def load():
    p = os.path.join(SCENES, 'era_scenes.json')
    if os.path.exists(p):
        for k, v in json.load(open(p, encoding='utf-8')).items():
            S[k] = dict(kind='era', text=v['text'], time=v.get('time', 'night'))
    dp = os.path.join(BOOK, 'data', 'strife.json')
    age = {}
    if os.path.exists(dp):
        for e in json.load(open(dp, encoding='utf-8'))['eras']:
            for c in e.get('cast', []) + e.get('meet', []):
                if c.get('key') and c.get('age') is not None:
                    age[(e['id'], c['key'])] = c['age']
    flag = set()
    for f in glob.glob(os.path.join(HERE, 'cast', '**', '*.json'), recursive=True):
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        for x in (d if isinstance(d, list) else []):
            if isinstance(x, dict) and x.get('en') and (x.get('minor') or x.get('teen') or x.get('child')):
                flag.add(x['en'])
    for p in sorted(glob.glob(os.path.join(SCENES, 's??.json'))):
        d = json.load(open(p, encoding='utf-8'))
        for s in d.get('nodes', []) + d.get('deaths', []):
            if s['key'] in S or s.get('same'):
                continue
            e = dict(kind='cut', style=tuple(s['style']), light=s['light'], camera=s['camera'], text=s['text'], raw=bool(s.get('raw')), scene=True)
            ppl = [tuple(x) for x in (s.get('row') or s.get('who') or [])]
            if s.get('row'):
                e['row'] = ppl
            elif ppl:
                e['who'] = ppl
            if s.get('beast'):
                e['extra'] = [beast_path(s['beast'])]
                e['beast'] = True
            if s.get('minor') or s.get('young') or any(age.get((d['era'], k), 99) < 18 or k in flag for k, _, _ in ppl):
                e['young'] = True
                e['raw'] = False if s.get('minor') else e['raw']
            if s.get('differs'):
                e['differs'] = True
            S[s['key']] = e
    # 传奇之陨（11-12）：场面在 scenes/legends/g?.json 的 falls，一位传奇一幅，画法跟死的那一刻一样。
    # 立绘标了 minor、teen、child 的，或者稿子里写了 young 的，照未成年那一条画（不画伤，raw 不算数）。
    for p in sorted(glob.glob(os.path.join(SCENES, 'legends', 'g?.json'))):
        d = json.load(open(p, encoding='utf-8'))
        for s in d.get('falls', []):
            if s.get('noart') or s['key'] in S:
                continue
            e = dict(kind='cut', style=tuple(s['style']), light=s['light'], camera=s['camera'], text=s['text'], raw=bool(s.get('raw')), scene=True, fall=True)
            ppl = [tuple(x) for x in (s.get('who') or [])]
            if ppl:
                e['who'] = ppl
            if s.get('beast'):
                e['extra'] = [beast_path(s['beast'])]
                e['beast'] = True
            if s.get('young') or any(k in flag for k, _, _ in ppl):
                e['young'] = True
                if s.get('young'):
                    e['raw'] = False
            if s.get('differs'):
                e['differs'] = True
            S[s['key']] = e


load()


def job(key):
    s = S[key]
    if s['kind'] == 'frame0':
        return CARD_F0 + F.CLEAN, MY_REFS
    if s['kind'] == 'back':
        return CARD_BACK + NO_MOON + F.CLEAN, [CARD_FRAME0, MY_REFS[0]]
    if s['kind'] == 'card':
        n = s['n']
        hue = " Colour. This card is ruled by one colour: %s. Build the whole picture from deep shades, mid tones and pale tints of that colour; %s. No rainbow of colours." % HUE[n]
        if n in BREAK:
            p = CARD_LEAD + s['text'] + ' Breaking out: ' + BREAK[n] + hue + CARD_LAYOUT + CARD_STYLE
        else:               # 第二十二张：什么也不出框。总说里“东西压在框前”“边上飘着小东西”“角上的小景”那几句不能带
            p = CARD_LEAD + s['text'] + hue + CARD_LAYOUT_BARE + CARD_STYLE
        return p + F.WEST_PLAIN + NO_MOON + F.CLEAN, [CARD_FRAME0] + MY_REFS
    if s['kind'] == 'road':
        lead, style = ROAD_LEAD, ROAD_STYLE
        if key == 'r11':          # 止戈以后的路是干净的：总说里“路边摆着这一段留下来的东西”“倒下的人怎么画”那两句不能带，带了它照样画头盔和残骸
            a = "Along both sides of the road lies what this stretch of the war left behind, set out small and clear like pieces on a table. "
            b = "The fallen are shown with restraint: still shapes under cloaks and shields, helmets set on swords planted in the earth, riderless horses standing; no blood, no wounds, no faces. "
            assert a in lead and b in style
            lead, style = lead.replace(a, ''), style.replace(b, 'Nothing of the war lies anywhere on this land. ')
        p = lead + s['text'] + (ROAD_EDGE if s['edge'] else '') + style + F.WEST_PLAIN + NO_MOON + F.CLEAN
        r04 = os.path.join(OUT, 'r04.png')          # 认过的一段当画法的样；头两段试图是拿主画 k2 当样出的
        return p, [r04 if (os.path.exists(r04) and key != 'r04') else K2, os.path.join(G.PVD, 'pv1_c.png')]
    if s['kind'] == 'era':
        p = G.PV_LEAD + s['text'] + ERA_STYLE + G.PV_ROOM + F.WEST_PLAIN + NO_MOON + NO_ARC + F.CLEAN
        # 颜色拿认过的长卷当样（夜和黄昏照死域那一段，白天和雨照白墙那一段）。头一轮拿主画 k2 当样，模型把主画里的三位神连弓搬进了画里。
        key = os.path.join(OUT, 'r04.png' if s['time'] in ('day', 'rain') else 'r07.png')
        return p, [key if os.path.exists(key) else K2] + [os.path.join(G.PVD, n) for n in ERA_LOOK.get(s['time'], ERA_LOOK['night'])]
    G.S[key] = s            # 节点原画和死的那一刻：提示词照 gpt_cg.py 那一套拼
    return G.job(key)


STOP = []

# 只改一处的重画（照 gpt_cg.py 的 FIX）：拿上一稿当底，别的都不动。上一稿在的时候走这一路，不在就照场面稿从头画。
FIX = {
    # 11-13 人体那一轮：狄昂倒退着走。头一稿（_a0）和重画的一稿（_a1）后脚的脚尖都朝右，像在往右迈步，跟朝左的上身和前脚对不上。
    # 模型不会画“倒退着走”的侧面，拿 _a1 当底只改两条腿：两只脚尖都朝左，后脚落在身后半步、前脚掌着地。
    's12_f_dion': ('s12_f_dion_a1.png',
                   "Redraw the attached picture and keep everything about it exactly the same: the same composition and camera, the dark night sky with drifting sparks, the long wall on the left with the single lamp on its very tall pole, "
                   "the frost on the ground and the line of footprints that comes from the left edge to the boy's feet, the tall thin woman with long ash-grey hair in a gown scorched at the hem who walks away at the right edge holding a pale lantern low, "
                   "and the boy in the middle: the same face in clean profile looking up to the LEFT at the lamp, the same black hair, the same dark clothes buttoned to the neck, the same short cloak, the same round polished bronze shield on his back, "
                   "the same colours, rendering and finish. Change one thing only: the boy's two legs and feet. "
                   "In the attached picture his rear leg ends in a boot whose toe points to the RIGHT, as if he were striding to the right. That is wrong and must be corrected. "
                   "He is walking BACKWARD. His whole body faces LEFT, and so do both of his feet. Draw the legs like this. Both boots point to the left: toe on the left, heel on the right, exactly like his front boot in the attached picture. "
                   "The front leg stands straight under his body with the boot flat on the ground. The other leg reaches one short step behind him, toward the right of the picture, the knee slightly bent, "
                   "and its boot touches the ground behind him with the ball of the foot, the toe down on the frost and still pointing LEFT, the heel a little lifted: the foot of someone feeling for the ground behind him without looking. "
                   "Seen from the side, the two boots are the same size and shape, one a short step to the right of the other, both with their toes toward the left edge of the picture. The two legs are the same length and the step is short. "
                   "His arms stay at his sides as they are. The air is perfectly still, so let the short cloak hang down behind him instead of streaming. "
                   "He is unhurt, clean and fully dressed. There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 托卡：重画的一稿（_a1）是纯背影，可只画清楚了一条腿（往后蹬、靴底朝着镜头的那一条），另一条到膝盖就没了，看着像断了。独立复查的子任务查出来的。
    # 拿 _a1 当底只补那一条往前迈的腿。
    's10_f_toka': ('s10_f_toka_a1.png',
                   "Redraw the attached picture and keep everything about it exactly the same: the same composition and low camera directly behind the running man, the stormy dawn sky and the rain, the wet grass slope, "
                   "the huge grey-blue flank of the dead beast with the coil of rope in the left foreground, the wide field of horned soldiers with banners on the right, "
                   "and the man himself seen from directly behind: the same silver-grey hair and black-tipped beast ears laid back, the same grey hooded cloak streaming to the left, the same leather jerkin, bracers and open hands, "
                   "the same colours, rendering and finish. Change one thing only: his legs. "
                   "In the attached picture only ONE leg is drawn completely, the one that trails behind him with the sole of its boot turned toward us; the other leg stops at the knee and has no shin and no foot, so he looks one-legged. That must be corrected. "
                   "Draw both legs completely, each from the hip to the boot. Keep the trailing leg as it is: it is his LEFT leg, pushed off behind him, the knee bent, the sole of the boot toward us. "
                   "Add the other leg, his RIGHT leg, clearly and fully: its thigh comes down from the right side of his hips, the knee is bent and driving forward, and the whole lower leg is visible to the right of the trailing leg, "
                   "the shin in the same dark trousers and the same tall strapped boot coming down to plant in the wet grass a little ahead of him and a little to the right, with a small splash where it lands. "
                   "The two legs are the same length and thickness, they wear the same trousers and the same boots, and the stride between them is an ordinary running stride. "
                   "No part of his face is shown. There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 下面四幅是独立复查的子任务指出来、主会话放大核对过的小处，都拿原图（_a0）当底只改这一处。
    # 茵妮：撑在前景地上的那只大手只有四根指头
    's14_f_inny': ('s14_f_inny_a0.png',
                   "Redraw the attached picture and keep everything about it exactly the same: the same composition and low camera, the white-haired woman crawling toward us on one knee with a wounded man tied on her back in a carrying frame of wood and rope, "
                   "her face and expression, her patched cloak, her boots, the wall of shields and spears on the left, the horned army and the glowing cannons on the right, the stretcher-bearers in white, the dust, the dry grass, the colours, rendering and finish. "
                   "Change one thing only: the big hand she plants on the ground in the right foreground. In the attached picture that hand has only four digits. "
                   "Redraw it as a normal human hand with exactly FIVE digits, palm down on the dirt, seen from the front and a little above: the thumb on the left side of the hand as we look at it, pointing toward the lower left, "
                   "and then four fingers fanned out to the right of it, the index, the middle, the ring and the little finger, each with its nail, the little finger the shortest and the furthest to the right. "
                   "The hand stays the same size and in the same place at the end of the same forearm with its leather bracer. "
                   "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 露卡：两条腿当中多出一条淡色的小腿和靴子
    's17_f_luka': ('s17_f_luka_a0.png',
                   "Redraw the attached picture and keep everything about it exactly the same: the same composition and low camera, the enormous stone foot bound round with rope and brass bells on the left, the vast stone giant reaching down through the haze, "
                   "the thick rope with its bells stretched across the picture, the fox-eared white-haired woman hauling on the rope with both hands, her shouting face, her scarf streaming, her pale fox tail, "
                   "the line of small rope-pullers far behind her on the right, the rubble, the flying dirt, the colours, rendering and finish. "
                   "Change one thing only. In the attached picture a third, pale lower leg with a pale boot shows beneath the woman's hips, between her front leg and her back leg. It belongs to no one and must be removed. "
                   "She has exactly two legs: the front leg, bent, with its tall dark buckled boot braced in the churned earth on the left, and the back leg stretched out behind her to the right with its dark boot dug in. "
                   "In the space between and behind her two legs there is only flying dirt, dust and the trampled ground: no other leg, no boot and no figure. "
                   "The rope-pullers behind her stay small and far away to the right, each clearly separate from her. "
                   "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 海蒂：剑首从拳头左上方伸出去，剑身从护手往左下走，柄和刃不在一条线上
    's16_f_heidi': ('s16_f_heidi_a0.png',
                    "Redraw the attached picture and keep everything about it exactly the same: the same composition and low camera, the rainy night sky with sparks, the broken white stone wall on both sides with small torch-bearers on top, "
                    "the burning camp and horned standards on the horizon, the mud and puddles, and the blonde woman standing in the breach: her face lifted and shouting, her hair, her worn long coat with its torn red lining, "
                    "her armour and belts, the round shield on her other arm, her stance and boots, the colours, rendering and finish. "
                    "Change one thing only: the sword in her hand on the left of the picture, and the way her gloved fist holds it. "
                    "In the attached picture the pommel sticks out to the upper left of her fist while the blade leaves the guard toward the lower left, so the hilt and the blade are not in one line and the sword looks bent at the guard. "
                    "Redraw it as one straight sword. The blade keeps its place and its direction: it runs from its tip in the mud at the lower left straight up to the cross-guard just below her fist. "
                    "The grip continues exactly along that same straight line, up through her closed fist, and the round pommel shows just above her fist on that same line, up and a little to the right of the hand. "
                    "Her fingers wrap round the grip with the thumb closed over them. Nothing sticks out of the fist to the upper left. "
                    "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 伊奥：老铁匠的后脚脚尖朝后（背着他正在推的门）；伊奥撑在地上的那只右手画成了左手（拇指在外侧）
    's16_f_io': ('s16_f_io_a0.png',
                 "Redraw the attached picture and keep everything about it exactly the same: the same composition and low tilted camera, the huge riveted iron furnace door glowing along its seams, the old smith on the left pushing it shut with both gloved hands, "
                 "his kerchief, apron and tongs, the red-haired young man crouching in the right foreground with a coil of rope over his shoulder and a tall torch in his other hand, his face in profile, the spotted fur, "
                 "the tipped bucket of coals, the chains, the sparks, the colours, rendering and finish. Change two small things only. "
                 "One: the old smith's back foot, the boot at the far left of the picture. In the attached picture its toe points to the left, backward, away from the door he is pushing. Turn that boot round: "
                 "its toe points to the right, toward the door, the same way he is pushing, with the ball of the foot braced on the floor and the heel a little raised, the way a man braces his back leg when he shoves something heavy. "
                 "Two: the gloved hand that the red-haired man plants on the floor at the bottom of the picture. It is his right hand, at the end of his right forearm, and it must be drawn as a right hand seen from above: "
                 "palm down, four fingers spread and pointing toward the lower left, and the thumb on the RIGHT side of the hand as we look at it, the side nearer to his own knee and to the rope, pointing toward the lower right. Five digits in all, in the same dark glove. "
                 "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 节点原画（独立复查筛出来、主会话放大核对过的）。
    # 第十九张头一幅：四个人的背影里，精灵的杖画成了对不上的两截（杖头在右肩后头，杖身从左手往下）
    's19_n1': ('s19_n1_a0.png',
               "Redraw the attached picture and keep everything about it exactly the same: the same composition seen through the stone gate arch with its open iron-studded doors, the wall with candles above, the dusk sky, the road through the ripe wheat, "
               "the four travellers walking away from us seen from behind, in the same order, sizes and poses: the blue-haired youth in a white cloak who lifts one hand in a wave, the tall man in a pale priest's robe with his hands behind his back, "
               "the dwarf in a horned helmet and red cloak with an axe on his shoulder and a lantern, and the elf with long white hair in a white dress with a satchel; "
               "and in the right foreground the armoured man in a blue cloak who holds a dark red jug and watches them go, the lantern on the wall, the fireflies, the colours, rendering and finish. "
               "Change one thing only: the elf's staff. In the attached picture the staff is drawn in two pieces that do not line up: its head with the small red orb stands behind her right shoulder, while its lower shaft comes down from her left hand on her other side. "
               "Redraw it as ONE straight staff carried upright in her left hand, on the left of her as we see her from behind: its foot touches the road beside her left boot, the shaft rises in one straight line through her left hand, "
               "and its head with the small red orb stands above her left shoulder, a little taller than she is. Nothing stands behind her right shoulder. "
               "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 塔沿：丹克瓦特后头那条腿迈得太开。量过，后腿的大腿比小腿长出一半，靴子离胯比前腿够得到的远三成，衣摆盖着接不上
    's16_c2': ('s16_c2_a0.png',
               "Redraw the attached picture and keep everything about it exactly the same: the same composition and low camera on the stone rim of the tower, the furnace glow and the chained wall on the left with the small faces at the high window, "
               "the grey soldiers with nets crouching behind the parapet and the wounded man in the left foreground, the night sky full of bat-winged soldiers, the two flying spears, the pale desert far below, "
               "and the tall horned man in the middle who braces a long hooked pole upright in both hands: his face turned over his shoulder, his rust-red hair and short horns, his torn sand-coloured coat flying to the left, "
               "the blood on his shoulder and hands, his belts, his front leg and front boot on the right, the colours, rendering and finish. "
               "Change one thing only: his rear leg, the one whose tall boot shows under the flying coat at the lower left. "
               "In the attached picture that boot is planted too far away from his body: the stride is wider than a man's legs can reach, so the leg looks far too long and does not seem to join his hips. "
               "Bring that boot in toward him by about a third of the distance, so that it stands on the stones under the middle of the flying coat tails. Its knee is a little bent, "
               "and the thigh in its dark trouser can be seen running up from the top of the boot under the coat toward his hip, so that the leg clearly belongs to him. "
               "His stance stays wide and braced, as wide as a fencer's stance and no wider. The two legs are the same length and thickness and the two boots are the same size. The front leg and front boot stay exactly where they are. "
               "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 第二十张第三幅：墙头弓手的弓弦从上弓梢出来横过她的胯和腰包，跟出画的下弓梢对不上
    's20_n3': ('s20_n3_a0.png',
               "Redraw the attached picture and keep everything about it exactly the same: the same composition on the wall walk at dawn, the red-haired archer in an iron helmet and leather jerkin seen from behind in the left foreground with her braid, "
               "the white-haired old man in a dark cloak holding a brass horn on the right, the row of soldiers along the parapet on the left, the pale salt flat below with one small figure in a long pale dress standing alone on it and her long shadow, "
               "the dark host, the fortress and the winged shapes on the horizon, the low sun, the colours, rendering and finish. "
               "Change one thing only: the string of the bow that the archer holds low at her side. "
               "In the attached picture the string leaves the upper tip of the bow and runs far away from the bow, across the front of her hip and her belt pouch, and it never meets the lower limb of the bow. That is wrong. "
               "Redraw it as the taut string of a strung bow: one thin straight line from the upper tip of the bow to its lower tip, lying close along the bow on the side nearer to her, "
               "only a hand's breadth from the grip where her hand holds it, and leaving the bottom of the picture together with the lower limb. "
               "No line crosses her hip, her belt or her pouch. The bow itself, her hand on its grip and the arrow hanging from her fingers stay exactly as they are. "
               "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 箭尾：老人一条前臂连着上面那只手，托在姑娘肘底下的第二只大手没有胳膊。照他站的位置，另一条胳膊在姑娘身后，从左边伸不过来，所以拿掉下面那只手
    's08_a1': ('s08_a1_a0.png',
               "Redraw the attached picture and keep everything about it exactly the same: the same composition and close low camera, the white-haired old man bending over the girl from the left in his grey work tunic dusted with stone powder, "
               "his lined face, his thick bare forearm coming in from the left, the girl in profile at full draw with her two short wheat-coloured braids and her ice-blue eye, her grey wool tunic and belt, the bow and the arrow, "
               "the yard, the old round shield with the arrow through it and the cracked stone behind it, the white battlements far away, the blossoms and dust in the corners, the light, colours, rendering and finish. "
               "Change one thing only. In the attached picture the old man has TWO big hands on the girl's drawing arm but only one arm: his forearm ends in the upper hand, which lies over her arm beside her cheek and presses down with its thumb, "
               "and a second big hand cups her elbow from below, directly under that same forearm, with no arm of its own. Remove that second, lower hand completely. "
               "Where it was, show only what was behind it: the girl's grey sleeve at the elbow, which simply points back toward him, and the old man's grey tunic and leather belt. "
               "He has exactly one hand in the picture, the upper one at the end of his forearm; keep it exactly as it is. Do not add any other hand or arm anywhere. "
               "Everyone is fully clothed. There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 塔落：学徒撑在地上的那只手画成一个没有指头的块
    's01_n2': ('s01_n2_a0.png',
               "Redraw the attached picture and keep everything about it exactly the same: the same composition and tilted low camera inside the broken bakery, the big ginger-haired baker in his apron dragging the young apprentice in by the cloak and by the arm, "
               "both their faces, the oven glowing at the back with the neighbours crouched round it, the falling tower of pale light, the street of roofs with flashing circles, the black shapes beyond, the debris, the colours, rendering and finish. "
               "Change one thing only: the hand at the end of the apprentice's other arm, the arm in the pale rolled sleeve that he plants on the floorboards at the lower right of his body, toward the right of the picture. "
               "In the attached picture that hand is a smooth rounded lump with no fingers. Redraw it as a real clenched fist pressed on the boards: the back of the hand toward us, four knuckles in a row, "
               "the creases between the four folded fingers clearly drawn, and the thumb folded across the front of the fingers; it is smeared with ash and is the same size as his other hand. "
               "His other hand, spread on the floor at the bottom of the picture with five fingers, stays exactly as it is. "
               "Everyone is fully clothed. There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 龙焰：乌格拉斯垂着的右手掌心朝着我们，拇指却在靠身子的一侧，是左手的样子
    's06_n3': ('s06_n3_a0.png',
               "Redraw the attached picture and keep everything about it exactly the same: the same composition and low camera, the long row of horned men and women facing us, the tall lean man in the middle with his pale grey skin, yellow eyes, "
               "short slate-blue hair and two filed horns glowing gold, his worn leather coat, belts and bracers, the dragons sweeping overhead with their sheet of gold-orange flame, the column of the army far behind, the frost in the corners, "
               "the light, colours, rendering and finish. "
               "Change one thing only: the open hand that hangs at the central man's side on the left of the picture, below his leather bracer. It is his RIGHT hand, and its palm is turned toward us, with an old red scar across the palm. "
               "In the attached picture the thumb of that hand is on the wrong side, the side next to his own body, which makes it a left hand. "
               "Redraw it as a correct right hand seen from the palm side, hanging relaxed with the fingers pointing down: the thumb is on the OUTER side of the hand, away from his body, toward the left edge of the picture; "
               "the four fingers hang down beside it, and the little finger is the one nearest to his coat. Five digits in all. The red scar still crosses the open palm. The hand stays the same size and in the same place. "
               "Everyone is fully clothed. There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 左手：姑娘满弓，弓弦却穿过拉弦的手一路斜到她的腰带，回不到下弓梢
    's08_a4': ('s08_a4_a0.png',
               "Redraw the attached picture and keep everything about it exactly the same: the same composition, the pale-haired elf in a dark green coat standing on the left with a great bow on his back, one arm hanging at his side and the other hand under the girl's elbow, "
               "the girl with two short wheat-coloured braids at full draw in the middle, her ice-blue eyes, her grey tunic, belt and quiver, the horn bow in her outstretched hand on the right and the arrow across it, "
               "the white wall with its wooden lookout platform, the far row of archers and straw targets, the wet flagstones, the blossoms, the light, colours, rendering and finish. "
               "Change one thing only: the string of the girl's bow. In the attached picture a thin pale line comes down from the top, passes through her drawing hand at her cheek and runs on down and to the LEFT, across the front of her tunic to her belt; "
               "it never returns to the bow. That is wrong. Redraw it as the string of a fully drawn bow, in two straight taut lines that meet at her drawing hand: "
               "the upper line runs from the upper tip of the bow, at the top right of the picture, down to the nock of the arrow in her drawing hand at her cheek; "
               "the lower line runs from that same point down and to the RIGHT to the lower tip of the bow at the bottom right of the picture. Bow and string together make one long narrow triangle with its point at her cheek. "
               "No line runs from her hand down toward her belt, and nothing crosses the left side of her tunic. The bow, the arrow, her two hands and her face stay exactly as they are. "
               "Everyone is fully clothed. There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 塌口：箭拉到了胸前，弓弦却直直地挂在弓边上没有动，箭不在弦上
    's08_b2': ('s08_b2_a0.png',
               "Redraw the attached picture and keep everything about it exactly the same: the same composition and low camera in the gap of the broken white wall at night, the tall white-haired old woman with her thick plait, her shouting face, her leather vest and dark dress, "
               "the old bow upright in her fist on the left, the arrow lying across her body with its feathered end at the two clasped hands in the middle, the flaxen-haired young man on the right grimacing with his own bow in his other fist, "
               "the boy peering from the stairway, the watchtower, the line of fire, the horned beast and the running horned soldiers on the left, the sparks, the colours, rendering and finish. "
               "Change one thing only: the string of the old woman's bow. In the attached picture the string hangs straight and slack beside the bow, from the top of the picture down to the bottom, "
               "although the arrow has been pulled far back across her body: the arrow is not on the string at all. That is wrong. "
               "Redraw the string as drawn back with the arrow, in two straight taut lines that meet at the nock, the feathered end of the arrow where the hands grip it: "
               "the upper line runs from the upper tip of the bow, at the top of the picture, down to the nock; the lower line runs from the nock down and to the left to the lower tip of the bow at the bottom left, passing in front of her skirt. "
               "The nock of the arrow sits exactly in the angle where the two lines meet. Remove the old slack string completely. The bow, the arrow, all the hands and both faces stay exactly as they are. "
               "Everyone is fully clothed. There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 拔节：姑娘的身子其实是左侧面，可朝着我们的那一面是一整块平的绿布，像背，脸又正对着我们，看着像脖子拧过了头
    's12_a1': ('s12_a1_a0.png',
               "Redraw the attached picture and keep everything about it exactly the same: the same composition and low camera among the bright green winter wheat at dawn, the woman in a wide straw hat and brown linen dress on the left who lays one hand on the girl, "
               "the line of dew drops glowing across the field and the workers straightening up along it, the far city with its round granary and scale beam, the small temple of four pillars under a thatched roof, the blossoms, the seed fluff and dew in the corners, "
               "and the girl in the right foreground: her head, her face, her wide cornflower-blue eyes and parted lips, her flax-coloured hair and the thick braid with a dried ear of wheat in it, exactly as they are. "
               "Change one thing only: make it clear at a glance that we see the girl's left side and the FRONT of her upper body, not her back. "
               "In the attached picture the side of her green tunic that faces us is one flat blank shape, so it reads as her back while her face looks at us, as if her neck were twisted too far round. "
               "Turn her shoulders a little toward us and draw the front of her tunic plainly below her chin: the white collar opens in a short V at her throat, and a laced opening runs from it down the middle of her chest toward the basket. "
               "The braid hangs forward over her far shoulder and down in front of her chest. The apron's waistband goes round her waist to a bow tied at the small of her back, on the left. "
               "The older woman's hand rests on the back of her near shoulder, where it is now. Her near arm still reaches down to the hand planted in the grass, and her far arm still holds the weed basket with its sprouts. "
               "Her head is turned toward us no further than her near shoulder. She is modestly and fully dressed in her long-sleeved working dress. "
               "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
}

# ---------- 长卷的接缝 ----------
# 11-13 用户：“纷争纪的长路，能不能实现直接就是一条连通的路，年月之间的路断开的有点多”。
# 十一段长卷每段两头画了烟，相邻两段在烟里叠着接上，路一到接缝就断，两边的路高低也对不上。
# 照页面的拼法把整条拼出来，以每道接缝为中心切一块 1536×1024（小样_纷争纪书/road_strip.py joins，jNN_in.png），
# 拿它当底只重画当中那三分之一：去掉烟，把左边进烟的路和右边出烟的路接成一条，地和天从左边那一纪慢慢变成右边那一纪。
# 出来的图再由 road_strip.py merge 照两边的旧图找缝并回整条、重切十一段。
JOIN_LEAD = ("Edit the attached picture. It shows the place where two sections of one long painted scroll meet: the left part of the picture belongs to one section and the right part to the next. "
             "Down the middle runs a tall band of pale drifting smoke that hides the join, and the road breaks there. "
             "Keep the left third and the right third of the picture exactly as they are: the same shapes in the same places, the same colours, the same road. Repaint only the middle third between them. ")
JOIN_ROAD = ("In the middle third, remove the band of smoke completely, so that no smoke, fog or mist column is left anywhere in the picture. "
             "The pale dusty road must become one single unbroken road running from the left edge of the picture to the right edge. ")
JOIN_ROAD2 = (" Through the middle the road keeps exactly the same width, the same pale dusty colour and the same thin edge lines as in the left and right thirds; it curves smoothly, with no sharp corner, no gap, no fork and no second road, and nothing lies on it. ")
JOIN_STYLE = (" Paint the middle in exactly the hand of the rest of the picture: large calm flat colour shapes layered like cut paper, thin lighter echo lines along the edges, soft inner gradients only, a fine paper grain over everything, everything small and seen from high above. "
              "Do not put any large new object, building, figure or monument in the middle third: only ground, grass, stones, a few small bare trees and small things of the same kind as on either side. "
              "The viewpoint, the height of the horizon and the scale stay exactly the same across the whole picture, and there is no vertical seam or line anywhere.")
WALL_ON = 'The long white battlemented wall runs on unbroken along the top of the picture through the middle third, joining the wall on the left to the wall on the right. '
JOINS = {
    1: ("On the left the road climbs from the lower left and ends at the gate of a small walled town on the horizon, about a third of the way across the picture. "
        "On the right it comes out from behind the smoke about halfway down the picture and runs on to the lower right past the frozen river. "
        "Join them: the road leaves the town gate, runs a little way to the right just below the horizon, then curves down across the middle in one long smooth bend and runs into the road on the right where it begins, about halfway down.",
        "The ground changes gradually from left to right: the pale grey ash of the left thins out into the wild grass and the edge of the wheat on the right. "
        "The sky strip at the top changes gradually from the black night of the left into the smoky iron grey with a dull red glow of the right; the tall dark shadow shapes rising out of the earth stay only in the left third.", None),
    2: ("On the left the road runs along the bottom of the picture, about nine tenths of the way down, and reaches the smoke there. "
        "On the right it starts about three fifths of the way down, just before the first of the seven doors, and runs on to the right past them. "
        "Join them: from the bottom the road bends up to the right in one smooth curve and runs into the road on the right before the first door.",
        "The ground changes gradually from the scorched dark red earth of the left into the cold slate blue-grey land of the right. The sky strip at the top runs on from the smoky iron grey of the left into the slate grey of the right.", None),
    3: ("On the left the road comes out of a bend at the lower left and reaches the smoke a little more than halfway down. "
        "On the right it continues at about the same height and runs on to the right below the wall. Join them in one gentle curve at that height.",
        "On the right the long white battlemented wall begins: in the middle third its first stretch rises from the foot of the mountains and runs off to the right, still being built. "
        "The ground changes gradually from the slate marsh of the left into the grey and dark red ground of the right. The sky strip at the top changes gradually from the dark red of the left into the pale slate of the right.", None),
    4: ("On the left the road winds up in an S-bend and runs to the right toward the smoke about a quarter of the way down, just under the wall. "
        "On the right it starts a little less than halfway down and bends down to the right. Join them: the road runs on from the left, then curves gently down through the middle and runs into the road on the right.",
        WALL_ON + "The ground stays the same grey and dark red as on either side. The sky strip stays pale slate.",
        'about two thirds of the way across and three quarters of the way down'),
    5: ("On the left the road comes down from a bend and reaches the smoke about three fifths of the way down. "
        "On the right it starts about halfway down and swings down in a tight bend. Join them in one smooth gentle curve.",
        WALL_ON + "Toward the right its battlements begin to carry cannon. The ground stays dark red and grey. The sky strip changes gradually from dark slate on the left to iron grey on the right.",
        'about three eighths of the way across and three tenths of the way down'),
    6: ("On the left the road runs to the right just below the wall, about a fifth of the way down, and reaches the smoke there. "
        "On the right it comes out about three fifths of the way down and runs on to the right past the fallen cannon. "
        "Join them: the road runs on from the left near the top, then bends down in one long, smooth, wide curve through the middle and runs into the road on the right.",
        WALL_ON + "The ground changes gradually from the dark red earth of the left into the white grass of the dead land on the right, with a few small rust-red flowers. "
        "The faint pale walking figures at the lower left stay where they are, in the left third. The sky strip runs on in iron grey.", None),
    7: ("On the left the road climbs from the lower left and reaches the smoke about a third of the way down. "
        "On the right it starts about halfway down and runs on to the right, lined with small stones. Join them in one smooth curve that comes gently down through the middle.",
        "The long white battlemented wall runs on along the top through the middle third, growing smaller and farther off toward the right. "
        "The ground changes gradually from the white grass of the left into the dark red ground and pale sand dunes of the right. The sky strip runs on in dull slate.", None),
    8: ("On the left the road runs through the dunes and reaches the smoke about halfway down. On the right it continues at about the same height. Join them in one gentle curve.",
        WALL_ON + "The ground changes gradually from the pale sand dunes of the left into the dull red dead land of the right with its kneeling iron soldiers. "
        "The sky strip changes gradually from the dark sky with a red glow on the left to flat dark grey on the right.",
        'about five eighths of the way across and seven tenths of the way down'),
    9: ("On the left the road winds up from the lower left and runs to the right toward the smoke about a quarter of the way down. "
        "On the right it starts a little more than halfway down and runs on to the right. Join them: the road runs on from the left, then curves down through the middle in one long smooth bend and runs into the road on the right.",
        WALL_ON + "The ground changes gradually from the dead land of the left, with its kneeling iron soldiers, into the dull red and grey ground of the right. "
        "The sky strip changes gradually from flat dark grey on the left to the pale clear gold morning on the right, where the far sea beyond the wall begins.",
        'a little more than halfway across and two thirds of the way down'),
    10: ("On the left the road comes across from the camps and reaches the smoke a little more than halfway down. "
         "On the right it continues from about the same height, passing in front of the arched gateway of the small town. Join them in one gentle curve.",
         WALL_ON + "War horns hang on it. The ground changes gradually from the grey ground of the left into the wet green grass of the right, and grey rain begins to fall in thin straight lines toward the right. "
         "The sky strip changes gradually from pale clear gold on the left to rain grey on the right. In the middle third the roadside is clean: no helmets, no weapons, no shields, no graves.", None),
}


# 牌立在路边那几块光秃的椭圆空地上（小样_纷争纪书/data/road.json 的落点），落在这一块里的照百分比写明不许动。
# 头一回试第六道没写，它把那一块改成了路，牌会立在路当中。
PATCHES = {1: [(22, 35), (90, 75)], 2: [(17, 28), (75, 81)], 3: [(20, 35), (71, 80)], 4: [(29, 35), (63, 77)], 5: [(37, 30), (68, 70)],
           6: [(33, 30), (82, 68)], 7: [(34, 31), (79, 71)], 8: [(27, 30), (62, 70)], 9: [(28, 34), (56, 66)], 10: [(20, 47), (71, 62)]}


def join_prompt(n):
    road, land, _ = JOINS[n]
    spots = ' and '.join('one about %d%% of the way across and %d%% of the way down' % p for p in PATCHES[n])
    keep = (' The small bare oval patches of level ground beside the road, where standing stones will be set, stay exactly where they are, clear and empty: '
            + spots + '. The road runs beside each patch, never over it.')
    return (JOIN_LEAD + JOIN_ROAD + road + JOIN_ROAD2 + land + keep + JOIN_STYLE
            + F.WEST_PLAIN + NO_MOON + F.CLEAN + ' Landscape picture, aspect ratio 3:2.')


for _n in JOINS:
    S['j%02d' % _n] = dict(kind='join')
    FIX['j%02d' % _n] = ('j%02d_in.png' % _n, join_prompt(_n))

# 十道接缝并上以后，还有几处路断在半路、或者多出一截通到哪儿都不去的路。拿并好的那一块（pNN_in.png，road_strip.py cutp 切的）当底只改那一处，
# road_strip.py 再照框贴回去。原来每一段里自带的岔路、绕着牌那块空地打的勾子，这一回一起拿掉，整条只剩一条路；
# 只有第二段左上那一条通到牌那块空地的小路留着（那张牌离大路太远），截到空地边上为止。
PATCH_LEAD = ("Edit the attached picture. It is part of a painted bird's-eye map of a war-torn land, drawn as flat layered cut-paper shapes, with one pale dusty road winding across it. "
              "Keep everything in the picture exactly as it is: the same composition, every object in the same place, the same colours, the same drawing manner and paper grain. "
              "Change only the road, and only in the way described here. ")
PATCH_TAIL = (" Any new piece of road has exactly the same width, pale dusty colour and thin edge lines as the rest of the road and curves smoothly, with no sharp corner and no gap. "
              "Where road is removed, paint the same kind of ground as around it, so that no trace of the old road is left. No other change anywhere in the picture.")
PATCHES = {
    'p02': ("Two changes. First, near the middle of the picture the road comes up from the bottom and bends to the right toward the row of seven doors, at about 58% across and 63% down. "
            "From that bend a short extra piece of road runs on up and to the left toward the saddle and ends in nothing at about 44% across and 53% down. "
            "Remove that extra piece completely and paint scorched dark red ground there, so that the road simply bends up from the bottom and runs on to the right toward the doors, with no branch. "
            "Second, at the upper left a narrow side road climbs from the left edge to a small bare oval patch of level ground at about 17% across and 25% down, passes along the right side of the patch, "
            "and then curls on over the top of it to a loose end at about 14% across and 11% down. Keep the side road up to the patch, but remove the part beyond it, from about 23% across and 22% down to its loose end, "
            "so that the side road ends right beside the patch. Keep that patch bare and empty, and keep the other bare oval patch at about 76% across and 82% down bare and empty too."),
    'p03': ("One change. At the lower left, the road comes in along the bottom of the picture from the left edge, past the round door in the green mound and the two covered wagons, and stops short at about 20% across and 78% down. "
            "Continue it: from that end it runs on to the right, passing below the two small grazing horses, to about 40% across and 76% down, then curves gently up and runs into the road that comes down from the stone gate in the mountain pass, "
            "joining it at about 52% across and 59% down; from there they are one road, which runs on to the right edge exactly as it does now. "
            "Keep the bare oval patch of level ground at about 71% across and 80% down where it is, bare and empty."),
    'p04': ("Two changes on the left side. First, at the lower left the road comes in from the left edge at about 72% down, rises to the right and stops short at about 26% across and 62% down. "
            "Continue it: from that end it curves up and turns to the right into the road at about 25% across and 43% down, where that road heads off to the right; from there they are one road, which runs on to the right edge exactly as it does now. "
            "Second, remove everything of the old road to the left of and above that joining point: the hook-shaped piece that runs from there back up the left side to about 16% across and 30% down, curls over the top at about 20% across and 25% down "
            "and runs right to a loose end at about 45% across and 25% down. Remove all of it and paint the grey and dark red ground there. "
            "Keep the small bare oval patch of level ground at about 28% across and 34% down where it is, bare and empty; it now lies just above the road. Keep the other bare oval patch at about 63% across and 77% down bare and empty too."),
    'p05': ("One change. Near the upper left, a side branch leaves the road at about 33% across and 47% down, where the road coming in from the left edge meets it. "
            "The branch climbs up past about 35% across and 38% down, curls round the bare oval patch of level ground at about 37% across and 30% down and runs on to a loose end at about 42% across and 24% down. "
            "Remove that whole side branch and paint the dark red and grey ground there, so that the road simply comes in from the left edge and runs on to the right with no branch. "
            "Keep the bare oval patch at about 37% across and 30% down where it is, bare and empty, and keep the other bare oval patch at about 68% across and 70% down bare and empty too."),
    'p06': ("Two changes on the left side. First, at the left the road comes in from the left edge at about 57% down and stops short at about 26% across and 50% down. "
            "Continue it to the right so that it runs into the road at about 38% across and 50% down; from there they are one road, which runs on to the right edge exactly as it does now. "
            "Second, remove the hook-shaped piece of road above that point: from about 37% across and 46% down it runs up and to the left past 28% across and 34% down, curls over the top at about 21% across and 24% down "
            "and runs right along the top to a loose end at about 54% across and 23% down. Remove all of it and paint the ground there as around it: dark red ground on the left, white grass on the right. "
            "Keep the bare oval patch of level ground at about 34% across and 29% down where it is, bare and empty, and keep the other bare oval patch at about 82% across and 68% down bare and empty too."),
    'p06b': ("One change. A small white riderless horse with a saddle cloth stands right on the road at about 33% across and 46% down, with the road running under its hooves. "
             "Remove that horse completely and paint the road there, so that the road at that place is empty and runs on unbroken, the same width, pale dusty colour and edge lines as on either side. "
             "Keep every other horse, the ruined arch, the crown and cloak on the flat stone, the pale walking figures and everything else exactly as they are."),
    'p09': ("One change. At about 64% across and 64% down the road forks: one branch runs on to the right edge, and the other runs down round the left side of the white ring of salt to the bottom edge of the picture at about 72% across. "
            "Remove that second branch, all of it from the fork to the bottom edge, and paint the ground and dry grass there as around it, so that the road coming down from above simply bends and runs on to the right with no branch. "
            "Keep the white ring of salt, the dark shape inside it, the overturned bowl and the small campfire as they are. Keep the bare oval patch of level ground at about 58% across and 66% down where it is, bare and empty."),
}
for _k, _t in PATCHES.items():
    S[_k] = dict(kind='patch')
    FIX[_k] = (_k + '_in.png', PATCH_LEAD + _t + PATCH_TAIL + NO_MOON + F.CLEAN + ' Landscape picture, aspect ratio 3:2.')

# 11-16 传奇之陨新添那一批：七位审稿人查完，小处的改法由子任务对着原图核对过以后写在
# 底稿/门面/小样_纷争纪书/scenes/查图/改法_*.json（{键: {verdict: 改|不改|重画, see, keep, change}}，说明是同目录 派活说明_改图.md）。
# 判“改”的拿原图 <键>_a0.png 当底只改那一处：出以前先把 <键>.png 改名成 <键>_a0.png（fix_apply.py 做这一步），再 python gpt_cg2.py <键…>。
FIX_LEAD = 'Redraw the attached picture and keep everything about it exactly the same: '
FIX_MID = ' Change only this: '
FIX_TAIL = (' Everything not mentioned stays exactly as it is in the attached picture, in the same place and at the same size. '
            'There is no moon and no crescent anywhere. There is no cross and no cross-shaped mark anywhere. '
            'No text, no letters, no numerals, no logo, no frame. Landscape picture, aspect ratio 3:2.')
FIXDIR = os.path.normpath(os.path.join(HERE, '..', '..', '门面', '小样_纷争纪书', 'scenes', '查图'))
for _f in sorted(glob.glob(os.path.join(FIXDIR, '改法_*.json'))):
    for _k, _v in json.load(open(_f, encoding='utf-8')).items():
        if _v.get('verdict') == '改' and (_v.get('change') or '').strip() and _k not in FIX:
            FIX[_k] = (_k + '_a0.png', FIX_LEAD + (_v.get('keep') or 'the same composition and camera, every figure with the same pose, face, body, clothing and gear, the same background, light, colours, rendering and finish.').strip()
                       + FIX_MID + _v['change'].strip() + FIX_TAIL)
# 第二回（11-16 复查以后还要改的）：改法二_*.json。判“改”的拿头一回改完的那一张 <键>_a1.png 当底再改一处（出以前把 <键>.png 改名成 <键>_a1.png），
# 盖掉头一回的改法；判“重画”的把头一回的改法拿掉，照（改过的）场面稿整幅出。
for _f in sorted(glob.glob(os.path.join(FIXDIR, '改法二_*.json'))):
    for _k, _v in json.load(open(_f, encoding='utf-8')).items():
        if _v.get('verdict') == '重画':
            FIX.pop(_k, None)
        elif _v.get('verdict') == '改' and (_v.get('change') or '').strip():
            FIX[_k] = (_k + '_a1.png', FIX_LEAD + (_v.get('keep') or 'the same composition and camera, every figure with the same pose, face, body, clothing and gear, the same background, light, colours, rendering and finish.').strip()
                       + FIX_MID + _v['change'].strip() + FIX_TAIL)



def limited(key):
    try:
        t = open(os.path.join(OUT, key + '.log'), encoding='utf-8', errors='replace').read().lower()
    except OSError:
        return False
    return 'usage_limit' in t or 'usage limit' in t


def one(key):
    if STOP:
        print('没开（撞了出图额度）', key, flush=True)
        return
    try:
        os.makedirs(OUT, exist_ok=True)
        srcs = FIX.get(key, ((), ''))[0]
        srcs = [os.path.join(OUT, n) for n in ((srcs,) if isinstance(srcs, str) else srcs)]
        if srcs and all(os.path.exists(p_) for p_ in srcs):
            out = gen(os.path.join(OUT, key), FIX[key][1], refs=srcs, timeout=1500)
            print('好了（只改一处）', key, out, flush=True)
            return
        p, refs = job(key)
        out = gen(os.path.join(OUT, key), p, refs=refs, timeout=1500)
        print('好了', key, out, flush=True)
    except Exception as e:
        if not STOP and limited(key):
            STOP.append(key)
            print('== 撞了出图额度，不再开新的', flush=True)
        print('失败', key, str(e)[:200], flush=True)


GROUPS = {'cards': 'card', 'road': 'road', 'era': 'era', 'scenes': 'cut', 'joins': 'join', 'patches': 'patch'}        # 空框 cf0、牌背 cb0 点名才出

if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] == ['--left']:
        kinds = [GROUPS[a] for a in args[1:] if a in GROUPS] or ([] if 'falls' in args else list(GROUPS.values()))
        left = [k for k in sorted(S) if (S[k]['kind'] in kinds or ('falls' in args and S[k].get('fall'))) and not os.path.exists(os.path.join(OUT, k + '.png'))]
        print(' '.join(left))
        print('缺', len(left))
        sys.exit(0)
    kinds = [GROUPS[a] for a in args if a in GROUPS]
    keys = [k for k in sorted(S) if k in args or S[k]['kind'] in kinds or k.split('_')[0] in args or args == ['all'] or ('falls' in args and S[k].get('fall'))]
    if not keys:
        print('键：', ' '.join(sorted(S)))
        sys.exit(0)
    if os.environ.get('CG_DRY'):
        for k in keys:
            p, refs = job(k)
            print('==', k, len(p), '字', [os.path.basename(r) for r in refs])
            print(p)
        sys.exit(0)
    with ThreadPoolExecutor(int(os.environ.get('CG_WORKERS', '3'))) as ex:
        list(ex.map(one, keys))
