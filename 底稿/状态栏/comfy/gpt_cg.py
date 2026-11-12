#!/usr/bin/env python3
# 门面·时代页的原画（11-12，用户要的：点进时代先是一幅专属这个时代的原画，不复用壁画；主线每个关键的叙事节点一幅过场动画式的原画）。
# 画法照角色艺术照那一路（崩铁光锥），横幅 3:2。人照立绘：一个人一张“全身加脸”的对照条当长相参考，人多的拼成一排。
#   python gpt_cg.py                     列出键
#   python gpt_cg.py m07_key m07_n2      出这几幅
#   CG_WORKERS=5 python gpt_cg.py m07    出这一个时代的全部
# 要带 PIL 的 Python（ComfyUI 那个）。出过的跳过，要重出先把旧图改名。图在 out/门面_原画_11-12/，不进库。
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image  # noqa: E402

from gpt_gen import gen  # noqa: E402

OUT = os.path.join(HERE, 'out', '门面_原画_11-12')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LC = os.path.join(ROOT, '语料', '人物参考_11-04', 'hsr_lc')      # 光锥的画法参考，不进库
POR = {'ge': '立绘_月银纪史诗', 'zg': '立绘_诸国期', 'sa': '立绘_萨尔维斯'}
GREY = (126, 128, 136)


def por_dir(key):
    return os.path.join(HERE, 'out', POR[key[:2]], key)


def flat(path, h):
    im = Image.open(path)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, GREY + (255,))
    bg.alpha_composite(im)
    w = round(im.width * h / im.height)
    return bg.convert('RGB').resize((w, h), Image.LANCZOS)


def ident(key, cell):
    """一个人的对照条：左边全身（哪一套衣服照 cell），右边艺术照的脸。"""
    os.makedirs(os.path.join(OUT, '_ident'), exist_ok=True)
    dst = os.path.join(OUT, '_ident', '%s_%s.png' % (key, cell))
    if not os.path.exists(dst):
        a = flat(os.path.join(por_dir(key), 'cell_%s.png' % cell), 1024)
        b = flat(os.path.join(por_dir(key), 'art.png'), 1024)
        im = Image.new('RGB', (a.width + b.width + 36, 1024), GREY)
        im.paste(a, (0, 0))
        im.paste(b, (a.width + 36, 0))
        im.save(dst)
    return dst


def lineup(name, pairs):
    """一排人的全身，从左到右照 pairs 的次序。"""
    os.makedirs(os.path.join(OUT, '_ident'), exist_ok=True)
    dst = os.path.join(OUT, '_ident', name + '.png')
    if not os.path.exists(dst):
        cells = [flat(os.path.join(por_dir(k), 'cell_%s.png' % c), 720) for k, c in pairs]
        gap = 14
        im = Image.new('RGB', (sum(c.width for c in cells) + gap * (len(cells) - 1), 720), GREY)
        x = 0
        for c in cells:
            im.paste(c, (x, 0))
            x += c.width + gap
        im.save(dst)
    return dst


LEAD_KEY = ("Draw in the rendering of the attached official illustrations from Honkai: Star Rail (the first %d attached pictures), for style only: do not copy their characters, costumes, props or composition. "
            "This is the key visual of one age of a fantasy epic, the picture a game shows when a chapter opens: one wide, sweeping view of a whole land, the danger hanging over it and the young people of that age, "
            "painted with the full finish of that game's Light Cone art. ")
LEAD_CUT = ("Draw in the rendering of the attached official Light Cone illustrations from Honkai: Star Rail (the first %d attached pictures), for style only: do not copy their characters, costumes, props or composition. "
            "This is a story illustration: one frozen frame of an animated cutscene, caught at the single most dramatic instant of the scene and kept like a record of it, painted with the full finish of that game's Light Cone art. ")
LOOK = ("Luminous, high-key colour. One strong directional light, %s; highlights bloom softly toward white on hair, shoulders and edges; the shadow sides take a saturated tint of the palette; razor-sharp cast shadow shapes. "
        "Thin crisp line art in a darker tint of each local colour, smooth skin with very simple shading, hair drawn in big clean ribbon-like shapes, glowing gradient irises. "
        "Deep space: large soft out-of-focus shapes in the near foreground at the corners of the frame, the figures sharp, a vast simplified far background in atmospheric haze; drifting sparks, motes and streaks of light. "
        "The camera is bold and cinematic: %s. ")
ONE = ("The next attached picture is a reference sheet of the character in this scene: the full figure on the left and a close-up of the same face on the right. "
       "Keep the same face, eye colour, hair colour, hairstyle and build so that the character is instantly recognisable, and draw them in a new pose for this scene. ")
MANY = ("The next %d attached pictures are reference sheets of the characters in this scene, in this order: %s. Each shows the full figure on the left and a close-up of the same face on the right. "
        "Keep each one's face, eye colour, hair colour, hairstyle and build so that every character is instantly recognisable, and draw them in new poses for this scene. ")
ROW = ("The next attached picture is a line-up of the characters in this scene, standing in a row, in this order from left to right: %s. "
       "Keep each one's hair colour, hairstyle, build and clothes so that every character is recognisable even from behind, and draw them in new poses for this scene. ")
DRAGON = ("The last attached picture shows the dragon of this scene: keep its head shape, its crest and its burnt-red scales, but redraw it in the clean Light Cone rendering of the style references, not in the painterly rendering of that picture. ")
NO_BLADE = "It is alive, and there is no blade, sword or spike stuck in it. "      # 断刃那一幅刃是穿在颅顶上的，不加这一句
FACE = "Faces are drawn straight and well proportioned in that game's anime style: both eyes level and the same size, nose and mouth centred, nothing skewed. "
# 11-12 用户看了头一稿回：“场面可以直接一些，比如罗南的金血，麦伦与焚原厮杀后的龙血与伤”。
# 场面里写了血和伤的（资料里 raw=True），照写的画出来；只挡到断肢、露骨、内脏那一步。没写的照旧不画。
CALM = "No blood and no wounds are shown. "
RAW = ("This is a hard-fought scene and it is shown plainly: the blood, soot, burns, torn cloth and wounds described above are clearly visible, painted with the same clean finish as everything else. "
       "No gore beyond that: no severed limbs, no exposed bone or organs, no mutilation. ")
TAIL = ("Everyone is fully and modestly clothed; nothing is sexualized. %s"
        "The world is Western high fantasy of swords and magic with medieval Europe as its base: no East Asian garments, roofs or motifs, no modern objects. Dragons are heavy Western wyrms with bat-like wings, no antlers, no whiskers. "
        "There is no moon and no crescent anywhere in the picture. No text, no letters, no logo, no watermark, no frame, no border, no caption, no user interface. "
        "Landscape picture, wider than tall, aspect ratio 3:2, the painting filling the whole frame edge to edge.")
KEY_ROOM = ("Keep the people and the most important things within the middle half of the picture's width. The lowest fifth of the picture is quiet, darker foreground, so that a title can be laid over it. ")

# 11-12 用户看了第七歌的试样回：节点原画的画风可以；时代原画要做成片头和纪元原画那种原神界面的画风（门面的定稿样 t2），同时带一点石壁壁画的感觉。
# 所以时代原画（kind='era'）换一路：画法照 gpt_front.py 的定稿样和 STYLE_LOCK，再添一段“画在石壁上”。光锥那一路只留给节点原画和旅伴死的那一刻（kind='cut'）。
import gpt_front as F  # noqa: E402

ERA_SERIES = ("Draw one wide 3:2 landscape picture, a plate from the same storybook-style series as the first attached picture: the opening picture of one age in the long history of a world. ")
MURAL_FEEL = (" One thing sets this plate apart from the sample: it is also a wall painting. The whole picture is painted on one great slab of pale stone instead of paper. "
              "In place of the paper grain there is a fine stone grain everywhere, with a few long hairline cracks; the colours are matte mineral pigments, a little dry and chalky, rubbed thin here and there so that the stone shows through; "
              "in a few places a small flake of paint has chipped away and left bare stone; a few of the longest contour lines are shallowly carved into the stone and catch a thin pale edge. "
              "Everything else stays exactly in the manner of the sample: the same clean flat shapes, elegant long curves, thin echo lines and tiny simplified people. "
              "It must not turn into a crude prehistoric cave painting: no stick figures, no handprints, no rough daubing, no dark cave. The painting fills the whole frame edge to edge.")
ERA_ROOM = (" Keep the people and the most important things within the middle half of the picture's width, and keep the lowest fifth of the picture quiet.")

FEN1 = os.path.join(HERE, 'out', '四方_11-03', 'boss', 'fenyuan1.png')
FEN2 = os.path.join(HERE, 'out', '四方_11-03', 'boss', 'fenyuan2.png')

# 键是 时代_key 或 时代_n几。style 是光锥参考（至多两张），who 是（立绘键，哪一套衣服，提示词里的叫法），extra 是另加的参考（排在最后）。
S = {}

S['m07_key'] = dict(
    kind='key', style=('wheat', 'aglaea_card'),
    row=[('ge7_hob15', 'battle', 'a small flour-dusted boy hugging a sack of grain'),
         ('ge7_inga', 'casual', 'a short, broad dwarf girl with two thick copper-red braids and a leather apron'),
         ('ge7_oswin', 'battle', 'a tall youth in a deep indigo robe with a round shield painted with a grey mountain and a white-ash spear'),
         ('ge7_maren', 'casual', 'a tall lean reaper in an undyed linen tunic, wheat-bronze hair tied back with one straw, a sickle resting on his shoulder'),
         ('ge7_fia', 'casual', 'a tall slender huntress with honey hair cut very short, a short bow in her hand and a quiver on her back'),
         ('ge7_ragna', 'casual', 'a barefoot shepherd girl with silver-white hair, a fleece vest and a long wooden staff'),
         ('ge7_ronan', 'casual', 'a very tall, broad boy with untidy black hair, a boiled-leather cuirass and a spear'),
         ('ge7_cadoc', 'casual', 'a thin boy in a wool cloak with a scorched black hem, a coiled whip in his hand')],
    light='warm gold from a low sun on the right, against a burning red glow from the left',
    camera='a low, wide-angle view from just behind the group, looking up past them at an enormous sky, the horizon low in the frame and gently tilted',
    text=("Scene: the Thousand-ear Plain in autumn, an endless plain of ripe golden wheat rolling to the horizon under an enormous sky. "
          "The sky is split on a diagonal. On the right it is still a clear, luminous autumn blue with tall white clouds. On the left it has turned a burning red, because an immense red-scaled dragon is gliding in from far away on that side, "
          "its wings spread so wide that they cover that whole half of the sky: we see it high and distant, mostly as one vast dark-red shape edged with fire, and its shadow slides across the plain, and where the shadow falls the tips of the wheat are turning black and beginning to smoulder. "
          "Far off on the plain, small: a walled town whose granaries stand taller than its walls, like a cluster of towers; nearer, a town on a river island with two pale stone arch bridges like two rainbows. "
          "In the lower middle of the picture, seen from behind and from three-quarter behind, eight young people stand close together in a loose line in the waist-high wheat on a small rise, small against the sky, the hot wind from those wings blowing their hair and clothes back toward us. "
          "The reaper stands a step ahead of the others in the middle: he alone turns his head enough for us to see his face in profile, calm and shut, his green eyes on the red sky. "
          "Out-of-focus ears of wheat sway across the bottom corners of the frame, a few of them glowing at the tips."))

# 头一稿（m07_n1_v1.png）是从桥侧看过去的，马和人画成了背着城门往外走，方向反了；改成从门洞里往外看，他们朝着门走回来
S['m07_n1'] = dict(
    kind='cut', style=('fire', 'anaxa'),
    who=[('ge7_maren', 'casual', 'the reaper who came back'), ('ge7_ronan', 'battle', 'the boy who guards the gate')],
    light='the cold blue of an early-winter dusk outside, warm firelight from a ward-fire above the gate spilling onto the threshold, and a dull red glow low on the far horizon',
    camera='from inside the gateway, at the gate-boy\'s shoulder just behind him, looking out along the bridge; the dark arch and the open gate leaf frame the view; a little tilted',
    text=("Scene: early-winter dusk at the north gate of a small river town on an island. We stand inside the gateway looking out. The dark stone arch of the gate frames the top and the sides of the picture, and one leaf of the heavy iron-bound gate has just been pulled open. "
          "Through it a pale stone arch bridge runs straight away from us over a dark river to the open plain, where the horizon glows a dull red under a bank of smoke. The first thin snow of the year is falling, and warm light from a ward-fire burning on the gate tower above spills down onto the wet stones just outside the arch. "
          "In the near right foreground, large and partly cut off by the frame, stands the boy who guards the gate, seen from behind at three-quarter so that we see one cheek and one pale-gold eye: very tall, untidy black hair, a boiled-leather cuirass, a white-ash spear upright in his right hand, his left hand still on the edge of the open gate. He has opened the gate for a rider who was promised to come back. "
          "Coming toward him across the bridge, walking toward us and already close, is a riderless bay horse: its head low, the saddle empty, the reins trailing on the stones, a rider's rolled cloak still tied behind the saddle. "
          "A few steps behind the horse, also walking toward us, comes the only man who came back: tall and lean, a worn sickle resting on his shoulder, his linen tunic clean, without a mark on him; his face is calm and shut, his young-wheat-green eyes looking away to one side, not at the boy. Behind him the bridge is empty all the way back to the plain. "
          "Snowflakes drift large and out of focus across the near corners; sparks from the ward-fire fall the other way."))

S['m07_n2'] = dict(
    kind='cut', style=('anaxa', 'fire'),
    who=[('ge7_maren', 'casual', 'the reaper')], extra=[FEN1], dragon=True,
    light='furnace orange-red pouring from the dragon\'s jaws on the left, with deep cool blue-violet shadow on the right',
    camera='level with the man\'s shoulder and slightly low, a little tilted, the dragon\'s head looming in from the left edge of the frame and cut off by it',
    text=("Scene: a small river town in high summer is about to be burned. An immense red-scaled dragon has coiled its whole body around the town wall as if the town were its throne, and has laid its chin on top of the south gate tower. "
          "We stand on the wall walk right in front of its head. The head fills the whole left half of the picture, enormous: each tooth is as long as a man, one molten-gold eye is half closed in contempt, and heat-haze and fire, half of it red and half of it black, leak between its teeth. "
          "Facing it at arm's length, on the right, one man stands on the battlement, tiny beside that head, and he is standing in the fire itself: flames curl round his boots and climb his linen tunic and do not burn him; his long wheat-bronze hair and the straw that ties it whip in the furnace wind. "
          "His back is straight, his face calm and unafraid, lifted a little toward the dragon's eye the way a farmer looks up at coming weather; his lips are just parted, he has this instant said one quiet word to it, an old name. "
          "His arm hangs at his side, half of a split wooden tally stick gripped in his lowered fist. The dragon's eye has opened wide at the word and for one breath its head is perfectly still. "
          "Far behind him, small: a stone arch bridge crowded with townsfolk fleeing, and a wooden notice board on the gate tower with papers nailed to it, their edges catching fire. "
          "Burning ears of wheat and glowing ash whirl large and out of focus across the corners of the frame."))

S['m07_n3'] = dict(
    kind='cut', style=('anaxa', 'fire'), raw=True,
    who=[('ge7_maren', 'casual', 'the reaper')], extra=[FEN2], dragon=True,
    light='blazing gold-orange from the ring of fire ahead, against the thin cold blue of the high sky behind and above',
    camera='just behind and a little below the man, wide-angle, looking up the slope of the dragon\'s back toward its head, strongly tilted',
    text=("Scene: high above the clouds at first light, on the third day of a fight that has not stopped. An immense red-scaled dragon is flying, and a man is walking on its back. "
          "We look along the dragon's spine from behind him: the ridge of huge burnt-red scales runs away from us like a mountain path toward the dragon's lifted head, far ahead, and above that head fire burns in a perfect floating ring, a crown of flame that touches nothing. "
          "The dragon is badly hurt: all along its back and neck the scales have been hacked open in a dozen places, and these wounds do not bleed red: they seep a black, smoking blood that streams backward in the wind in long dark ribbons. "
          "The man is in the near middle of the picture, seen from behind at three-quarter so that we see one cheek and one green eye: he walks forward against the wind along the spine, leaning into it, limping a little, his long wheat-bronze hair torn loose and streaming back toward us. "
          "Three days of this show on him: his plain linen shirt is torn at the shoulder and sleeve and soaked with black dragon blood, there are open cuts on his forearm and across his brow with red blood running from them, his knuckles are split, and the skin of his arms and neck has the dark burnt-copper colour of something that has been through fire. "
          "In his right hand, held low, is the broken half of a sword: the blade has snapped off jagged a hand's length above the guard, black blood on the steel, the break still glowing blue-white. "
          "On the back of his shirt, between the shoulder blades, a single ear of wheat embroidered in gold thread still shows clean through the stains and catches the light. "
          "The dragon's two vast wings rise at the edges of the frame like red sails, one of them with an old arrow hole in its membrane. Far below, through gaps in the cloud, lies a burnt red plain, and every fire down there leans toward the crown like wheat bent by wind, long streaks of flame bending upward. "
          "Torn cloud, sparks and drops of black blood rush past large and out of focus in the near corners."))

S['m07_n4'] = dict(
    kind='cut', style=('fire', 'wheat'),
    who=[('ge7_ragna', 'casual', 'the barefoot shepherd girl'), ('ge7_hob15', 'battle', 'the sleeping boy')],
    light='the pale cold blue of snow before dawn, warmed by the gold of torches and of the wheat; the spring water catches the first light and glows',
    camera='low, near the ground beside the spring, looking up at the girl, a little tilted',
    text=("Scene: deep winter on a high black-stone plateau, just before dawn, in heavy snow. Behind, a long column of refugees, thousands of small figures with torches and ox-drawn grain carts, winds away across the snow toward the shut gate of a small walled mining town, where people with torches look down from the wall. "
          "In the foreground, sharp, a barefoot shepherd girl has just struck a snow-covered rock with the butt of her long wooden staff: the rock has split, and a spring of clear water bursts up through the snow in a bright arc, steaming in the cold, already running away as a small stream beside the carts. "
          "She stands with both hands on the staff, her bare feet planted in the snow without flinching, a bronze ring at one ankle, her silver-white hair and the fleece of her vest whipped by the wind, her pale grey eyes bright, looking down at the water with a small fierce smile. Her long wool tunic reaches her shins. "
          "Right beside her stands a grain cart: its load of golden wheat is heaped full under a cap of fresh snow, and against its wheel, wrapped to the chin in an oilcloth cloak, a small flour-dusted boy with fluffy wheat-gold hair is fast asleep sitting up, a few grains of wheat spilling from his open hand. "
          "Snowflakes drift large and out of focus across the near corners, some of them lit gold."))


# ---- 时代原画，门面的画风加石壁感（第二稿，留着对照，现行的是后面片头画风那一套）。m07_key 是头一稿光锥画风的那一幅，也留着对照 ----
S['m07_era_a'] = dict(
    kind='era_stone',
    text=("Scene: the Thousand-ear Plain in the autumn when the dragon came. The lower third of the picture is an endless plain of ripe wheat, drawn as long flowing rows that bend like waves, in pale straw and old gold. "
          "In the lower centre a single small campfire burns on a river beach, the brightest warm point of the picture. Around it stand eight tiny young people seen from behind, drawn very small and simplified, each known by one thing: "
          "a reaper with a sickle on his shoulder, a youth with a round shield and a spear, a short broad girl with two thick braids, a small boy hugging a sack of grain, a barefoot girl with a long staff, a thin boy in a ragged cloak, a tall girl with a short bow, a very tall boy with a spear. "
          "Far off on the plain stand three tiny walled towns: one whose granaries rise taller than its walls like a cluster of towers, one on a river island with two arch bridges like two rainbows, one beside a cliff with a row of water wheels. "
          "Above them all, filling the upper two thirds, an immense dragon is drawn as overlapping cut-paper silhouettes in ash rose, burnt red and slate: it lies along a long cliff at the edge of the plain, its body curving in one great S, "
          "its two wings spread like sails so that they darken half the sky, its horned head lowered toward the tiny people, thin pale echo lines running along its edges. There is no crown on its head. "
          "All the wheat on the plain leans toward the dragon like grass in a wind, and the smoke of the little fire rises between the wings in one long S-curve. "
          "Palette: stone grey, slate, ash rose and burnt red, pale straw gold, bone white, and one warm orange flame."))

S['m07_era_b'] = dict(
    kind='era_stone',
    text=("Scene: the summer when the dragon took a town for its throne. In the middle of the picture a small walled town stands on an island where a river parts, with two pale arch bridges like two rainbows, one to each bank. "
          "An immense dragon, drawn as overlapping cut-paper silhouettes in ash rose, burnt red and slate, has coiled its whole body once around the town wall, its tail trailing away across the plain in a long S-curve, "
          "its two wings half open above the roofs like sails, thin pale echo lines running along its edges. Its horned head rests with the chin on top of the gate tower. There is no crown on its head. "
          "On the wall in front of that head stands one tiny man with a sickle on his shoulder, alone, facing it; a small ward-fire burning in an iron basket on the gate tower beside him is the brightest warm point of the picture. "
          "Over the farther bridge a thin line of tiny people is leaving the town. All around lies an endless plain of ripe wheat, drawn as long flowing rows that bend like waves toward the dragon, in pale straw and old gold; "
          "far off, small, a town whose granaries rise taller than its walls, and a long cliff with a row of water wheels. "
          "Palette: stone grey, slate, ash rose and burnt red, pale straw gold, bone white, and one warm orange flame."))

# ---- 旅伴死的那一刻（过场原画的画法）。不画血和伤口，画那一刻以前或者站着的样子 ----
S['m07_d_oswin'] = dict(
    kind='cut', style=('anaxa', 'fire'), raw=True,
    who=[('ge7_oswin', 'battle', 'the highland prince')], extra=[FEN1], dragon=True,
    light='furnace red-orange from the dragon above, against the cold blue of an early-spring dawn',
    camera='low, from inside a ring of raised shields, looking up past the prince toward the dragon\'s throat; strongly tilted',
    text=("Scene: early spring on a burnt plain below a long cliff, black wheat stubble underfoot, the ground still burning from the dragon's last breath. An immense red-scaled dragon rears above. Under its throat one patch of scales has gone dark, and behind that dark scale a single point of light glows; its jaws are opening again, and the next breath of fire is already pouring down out of them toward the place where the prince stands. "
          "In the middle of the picture a young highland prince has just thrown his javelin. He is caught at the very end of the throw: his whole body stretched forward on one leg, the throwing arm fully extended, his short straw-coloured hair swept back by the hot wind, his blue eyes narrowed on the mark, his mouth shut, no grin now. "
          "The fight has marked him: his deep indigo robe is singed and smoking at the hem and one sleeve is burnt away, there is a raw burn along his throwing forearm, blood runs from a cut at his temple, soot on his face. "
          "The white-ash javelin with its wolf-fang head is in the air, flying up a narrow slit that has opened in the curtain of red flame, straight toward the dark scale. "
          "Around him his twelve old shield-bearers, white-haired highland warriors, stand in a closed ring, their round wooden shields painted with a grey mountain raised edge to edge against the fire. The shields are charred and burning at the rims, the old men's beards are singed, two of them are down on one knee and bleeding but still hold their shields up; not one has stepped back. "
          "The nearest, a one-eyed old man with blood in his white beard, is large in the foreground and partly cut off by the frame. Burnt ears of wheat and embers whirl large and out of focus across the corners."))

S['m07_d_ronan'] = dict(
    kind='cut', style=('anaxa', 'fire'), raw=True,
    who=[('ge7_ronan', 'battle', 'the boy who guards the gate')], extra=[FEN1], dragon=True,
    light='smoky amber late-morning light from behind the dragon, with one shaft of clear pale light falling on the boy and the post',
    camera='low and close, from the side of the post, looking up at the boy and past him at the dragon\'s eye, the foot of the post in the near foreground; a little tilted',
    text=("Scene: late morning at the south gate of a small river town; smoke drifts everywhere, and the town is empty. Beside the gate stands the wooden post where notices are nailed, a few papers still fluttering on it. "
          "A very tall boy has lashed himself to that post with his own belt so that he stays on his feet. He stands straight against it, feet planted, his white-ash spear still held upright in his fist, his head up; we see him from the side at three-quarter, his eyes closed, his face calm. He is utterly still. "
          "He has been through the dragon's fire: his boiled-leather cuirass is scorched black and cracked, one shoulder piece burnt away, his sleeves charred to the elbow, soot and ash on his cheek and in his untidy black hair, thin smoke still rising from him. "
          "His blood is not red but gold, the shining gold of his line: it has run from under the cuirass and down the wooden post in bright thin streams and gathered in a small glowing pool at the foot of the post, and one thread of gold runs from the corner of his mouth. "
          "A crow is coming down out of the smoke with its wings spread, a moment from settling on his shoulder. "
          "In front of him, filling the upper left of the picture, the immense head of the red dragon has been lowered to his height and waits, one molten-gold eye open, watching him; at the corner of its mouth a spear wound seeps black, smoking blood. "
          "Behind the dragon's coils, far and small, a stone arch bridge stands empty: everyone has crossed. Glowing ash drifts large and out of focus across the corners."))

# 11-12 第七歌改稿：红土线上那一回改给麦伦，是二幕的第二幅节点原画，叫白线之晨。卡多克撤了，下面 m07_d_cadoc 那一条只留着当记录（图是 m07_n2b 的底）
S['m07_n2b'] = dict(
    kind='cut', style=('fire', 'anaxa'), raw=True,
    who=[('ge7_maren', 'casual', 'the reaper')], extra=[FEN1], dragon=True,
    light='the cold pale gold of first light from the right, against the deep red glow of scorched earth and of the dragon\'s fire',
    camera='low on the red earth beside the cart, looking up at the man and at the huge head above him; a little tilted',
    text=("Scene: dawn at the foot of a long cliff. The ground here is burnt red earth, and its edge runs across the picture like a shoreline; outside it the wheat stubble is still pale. "
          "A tall lean man in a plain linen tunic has walked out alone to that line, unarmed, pulling by its shaft a two-wheeled cart loaded with sacks and blocks of white salt, the way a village brings its yearly tribute. "
          "The immense head of the red dragon has come down out of the sky to him and fills the whole upper left of the picture, one molten-gold eye turned on the small figure. It has just answered him: fire pours from its jaws and over him, half of it red and half of it black. "
          "The red flame streams around the man and does not touch him. The black flame does not spare him: it has caught his left arm and shoulder and the side of his chest, the linen there burning away in black tatters, the skin under it scorched to the dark colour of burnt copper with raw red burns at its edges. "
          "He does not step back. He stands straight, one hand still on the shaft, the other open at his side, his long wheat-bronze hair blown back by the blast, his green eyes steady on the dragon's eye, his mouth closed. He carries no weapon at all. "
          "On the cart the salt is beginning to melt in the heat and runs down in white streams onto the red earth, drawing a white line across it. "
          "Far behind him, small, a line of some thirty armed men and women stands watching and does not move. Grains of salt and sparks drift large and out of focus across the corners."))

S['m07_d_cadoc'] = dict(
    kind='cut', style=('fire', 'anaxa'),
    who=[('ge7_cadoc', 'casual', 'the boy with the salt cart')], extra=[FEN1], dragon=True,
    light='the cold pale gold of first light from the right, against the deep red glow of scorched earth and of the dragon\'s fire',
    camera='low on the red earth beside the cart, looking up at the boy and at the huge head above him; a little tilted',
    text=("Scene: dawn at the foot of a long cliff. The ground here is burnt red earth, and its edge runs across the picture like a shoreline; outside it the wheat stubble is still pale. "
          "A thin boy in a wool cloak with a scorched black hem has walked out alone to that line, pulling by its shaft a two-wheeled cart loaded with sacks and blocks of white salt, the way a village brings its yearly tribute. "
          "The immense head of the red dragon has come down out of the sky to him and fills the whole upper left of the picture, one molten-gold eye turned on the small figure. It has just answered him: fire pours from its jaws and over him, half of it red and half of it black. "
          "The red flame streams around the boy and does not touch him. The black flame runs through the red like ink through water, and it has just caught the hem of his cloak and the shaft of the cart. "
          "He does not step back. He stands straight, one hand still on the shaft, the other open at his side, his short dark hair and his cloak blown back by the blast, his dark red eyes steady on the dragon's eye, his mouth closed. "
          "On the cart the salt is beginning to melt in the heat and runs down in white streams onto the red earth, drawing a white line across it. "
          "Far behind the boy, small, a line of some thirty armed men and women stands watching and does not move. Grains of salt and sparks drift large and out of focus across the corners."))

S['m07_d_maren'] = dict(
    kind='cut', style=('anaxa', 'fire'), raw=True, blade=True,
    who=[('ge7_maren', 'casual', 'the reaper')], extra=[FEN2], dragon=True,
    light='the last orange of falling fire from above, with the cold clear blue of morning opening behind',
    camera='looking steeply down a cliff from above and to one side, the dragon\'s head and the man large in the frame, the ground dizzyingly far below; strongly tilted',
    text=("Scene: the fall. A sheer face of pale rock runs down the whole picture. An immense red-scaled dragon is plunging down it head-first, its wings torn back by the wind, its hide hacked open in many places; the ring of fire that crowned it has just gone out and breaks into a rain of burning fragments that fall with it down the cliff. "
          "The broken half of a sword has been driven up through its lower jaw: the jagged tip stands out through the top of its skull and glows blue-white, and black, smoking blood pours from the wound under the jaw and streams upward past everything in the wind of the fall. "
          "The man who did it falls with the dragon. One hand still grips the hilt under the jaw, his arm black to the elbow with the dragon's blood; his body is flung out into the air, his long wheat-bronze hair streams upward. "
          "He is spent and hurt after three days and two nights of this: his plain linen shirt is torn and spattered black, red blood runs from a gash across his brow and from cuts on his forearms, his lip is split, and the skin of his arms and neck has a dark burnt-copper colour. "
          "On the back of the shirt, between the shoulder blades, a single ear of wheat embroidered in gold thread is still clean. His face is calm, his green eyes open, looking not at the ground but far away to one side. "
          "Far below lie a burnt red plain and a river. The red glow that hung over the plain is going out, falling with the dragon, and behind it the true blue of morning shows. Sparks, torn cloud and drops of black blood rush upward large and out of focus across the corners."))


# ---- 时代原画（现行）：片头月银纪那六幅的画风 ----
# 11-12 用户看了石壁那一稿回：“月银纪时代原画统一用你之前发给我的这一种的画风”，附的是片头样片月银纪那一处的六幅（gpt_front.py 的 pv1_a 到 pv1_f，图在 out/门面_片头_11-12/）。
# 所以二十七幅时代原画都照片头那一路：画法、颜色、纸纹照那六幅，拿它们当参考（不拿带角花的定稿样 t2）；石壁那一段不用了。
# 颜色是月银纪这一套：靛蓝、石板蓝、银、骨白，暖色只留给火和灯。白天的几幅靠明暗分（照诸神落座那一幅的亮），不往暖里调。
# look 定拿哪几幅当参考：night 夜里的兽和火，dawn 天亮前后，day 白天，tower 辉塔的冷光，fall 灯灭以后。
PVD = os.path.join(HERE, 'out', '门面_片头_11-12')
PV_REFS = {'night': 'ab', 'dawn': 'ca', 'day': 'ca', 'tower': 'dea', 'fall': 'fa'}
PV_LEAD = ("Draw one wide 3:2 landscape picture, a new plate for the same storybook-style trailer series as the attached pictures: the opening picture of one age in the long history of a world. ")
PV_STYLE = (" Drawing manner: all the attached pictures are approved plates of this very series, and the new plate must look as if the same hand had painted it for the same film. "
            "Match them exactly: the same shape language, line weight, paper grain, softness, inner glow and level of detail. "
            "Large calm flat colour shapes layered like cut paper; the vast things in the picture are drawn as overlapping pale cut-paper silhouettes that curve and spiral around the small focal point like waves, "
            "with thin lighter echo lines running along their edges; people are tiny and simplified; lights glow softly from within; "
            "small warm flames are the only warm accents against a cool limited palette of indigo, slate blue, silver and bone white; plenty of quiet empty space; soft inner gradients only; a fine paper grain over everything. "
            "Keep it simple and airy: no dense ornament, no gothic tracery, no heraldic shields or coats of arms, no ornate picture frame, no border, and no leaf, vine or scroll ornament in the corners. "
            "It is painted on paper, not on a wall: no stone texture, no cracks, no chipped paint, no fresco or parchment look, no dusty ochre or sepia cast. "
            "No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D render. "
            "Take only the drawing manner and the palette from the attached plates. Do not copy their compositions, and do not bring in any beast, giant figure, tower or building from them that the scene above does not name.")
PV_ROOM = (" Layout: the picture is used as a wide banner with a title laid over its lower left corner. Keep the small fire, the people and everything important within the middle half of the picture's width, "
           "and place the fire and the people between half and two thirds of the way down; the vast shapes fill the picture above them. "
           "The lowest quarter of the picture is only quiet, darker foreground with nothing important in it.")
PV_NO_MOON = ' There is no moon and no crescent anywhere in the picture.'

S['m07_era'] = dict(
    kind='era', look='night',
    text=("Scene: the autumn night when the dragon came to the Thousand-ear Plain. The land is an endless plain of ripe wheat under the night sky, drawn as long flowing rows that bend like waves, in silver and pale straw-white, all leaning one way. "
          "A river parts around an island on which stands a small walled town with two pale stone arch bridges, one to each bank, like two rainbows; a tiny ward-fire burns on each of its two gate towers. "
          "The river beach below the town is dotted with the tiny campfires of people who have fled here, one beside another. The nearest and brightest of them burns a little right of centre, and around it stand seven tiny young people, simplified, each known by one thing: "
          "a reaper with a sickle on his shoulder, a youth with a round shield and a spear, a short broad girl with two thick braids, a small boy hugging a sack of grain, a barefoot girl with a long staff, a tall girl with a short bow, a very tall boy with a spear. They look up. "
          "Far off on the plain, tiny: a second walled town whose granaries rise taller than its walls like a cluster of towers. "
          "Above them all, filling the upper half of the picture, an immense dragon is drawn as overlapping pale cut-paper silhouettes in silver blue and slate: a heavy Western wyrm that lies along the top of a long cliff at the edge of the plain like a range of hills, "
          "its body curving in one great S, its two bat-like wings spread like sails so that they cover half the sky, its horned head lowered toward the plain, thin lighter echo lines running along its edges. There is no crown on its head. "
          "A thin seam of ember red glows between the scales of its throat and along the edge of its jaws, the sky under its wings is stained a deep dull red, and far out on the plain a thin line of red-orange fire creeps through the wheat, the fields behind that line black. "
          "The smoke of the nearest campfire rises in one long S-curve between the wings and thins into a river of stars. "
          "Palette: deep indigo, slate blue, silver grey, bone white, pale straw, and the warm orange and ember red of the fires."))

# 另外二十六个时代。写法都是“这个时代开场的地方、火边很小的人、上面是这一段的庞然大物”，是事情做成以前的样子，做成的那一下留给壁画和节点原画。
# 题材照 gpt_mural.py 那二十七幅对过的（兽的样子、颜色、数目），地方照各页主线的开局。万兽十四歌都画成夜里（天亮以前），第十五歌是头一回日出，
# 诸国期六页照页名走一天（晨、午、午后、傍晚、黄昏、夜），萨尔维斯六页是辉塔的冷光。
S['m01_era'] = dict(
    kind='era', look='night',
    text=("Scene: the first winter of the long night. A wide snow plain crossed by a frozen river. A little right of centre stands a broken old stone bridge of grey arches; under its one whole arch a small fire burns, "
          "and some forty tiny people in furs are packed close around it, so that the arch glows from inside like a lantern. "
          "From the bridge a line of six tiny figures is setting out across the snow toward the dark horizon, their footprints behind them; the first of them is a girl with one thick ash-gold braid, a fur coat too big for her "
          "and a tall basket on her back in which a clay pot of embers glows. "
          "On the far bank, filling the upper half of the picture, lies an enormous wolf with a mane of snow, drawn as overlapping pale cut-paper silhouettes in silver blue and bone white: its body curves along the whole horizon like a range of snow hills, "
          "its mane streams away as drifting snow, its head is lowered toward the bridge, and it watches the fire. Snow falls. "
          "The smoke of the fire rises in one long S-curve past the wolf's head and thins into a river of stars; far ahead of the six walkers there is only darkness and one very faint pale line. "
          "Palette: deep indigo, slate blue, silver grey, bone white, and the warm orange of the fire and of the embers in the basket."))

S['m02_era'] = dict(
    kind='era', look='night',
    text=("Scene: an island of fishermen in the western sea, on an autumn night. Along the shingle every house dries its nets on tall poles, and the nets hang across the lower picture like veils, the sea wind blowing points of light through their meshes. "
          "A little right of centre one small fire burns on the beach, and beside it a tiny young man pushes a small boat into the water, about to sail east. "
          "Beyond the sea, filling the upper half of the picture and drawn as overlapping pale cut-paper silhouettes in silver blue and slate, an enormous lizard lies like a mountain ridge at the foot of a mountain, "
          "moss and small trees on its back, its long tail curled around a tiny walled town; its one visible eye, set in its head, is a great round disc of pale concentric rings, wide open. "
          "Before the town gate and all along the road stand rows of tiny bone-white people, turned to stone in mid-step, a town of statues. Thin lighter echo lines run along the lizard's back like the contour lines of hills. "
          "Palette: deep indigo, slate blue, sea grey, silver, bone white, and the one warm orange fire on the beach."))

S['m03_era'] = dict(
    kind='era', look='night',
    text=("Scene: the far north in the last days of autumn, at night. Across the middle of the picture a wide river runs in pale bands of ripple and new ice; at its broadest ford, a little right of centre, one tall standing stone rises on the near bank with a raven perched on top, "
          "and beside the stone stands one tiny young warrior with a spear, looking across the water; a little behind him a small fire burns with a few tiny people round it. "
          "On the far bank stands a long timber hall with rows of horns and antlers hung along its gable, its door open and a hearth glowing inside. "
          "Behind the hall, filling the upper half of the picture, an enormous woolly mammoth is rising to its feet, drawn as overlapping pale cut-paper silhouettes in silver blue and bone white: its back carries a whole winter of snow like a mountain ridge, "
          "its long curved tusks sweep down toward the ford, and behind it the backs of a herd of smaller mammoths overlap like hills; low clouds press down on its shoulders, and the first snow of the year blows from it across the river. "
          "Palette: deep indigo, slate blue, silver grey, bone white, and the warm orange of the fire and the hearth."))

S['m04_era'] = dict(
    kind='era', look='night',
    text=("Scene: an early-spring night on the southern grassland, a plain of grass without end, drawn as long flowing rows that bend like waves. Herds of wild horses run across it, their long manes streaming as if the wind lived in them. "
          "A little right of centre stands the great round tent of a queen of the riding tribes with a small fire burning before it; by the fire stand a few tiny riders, one very tall man in a spotted leopard pelt, and a boy holding up a torch. "
          "Far to the north the land rises to a dark highland whose top is lost in cloud. Above that highland, filling the upper half of the picture and drawn as overlapping pale cut-paper silhouettes in silver blue and slate, "
          "an enormous burrowing wyrm floats among the clouds: this one is heavy, blunt-headed and has no wings, its body curving in one great S; on its back it carries a whole walled town, with wheat fields and sheep pastures outside the walls and tiny lit windows inside them. "
          "Palette: deep indigo, slate blue, silver grey, bone white, a pale grey-green in the grass, and the warm orange of the fire and the torch."))

S['m05_era'] = dict(
    kind='era', look='night',
    text=("Scene: an autumn night by a lake so still that it mirrors the whole sky. On its near shore, a little right of centre, stands a small grass-roofed hut with fishing nets and strips of birch bark hung to dry under its eaves; "
          "a small fire burns by the door, and beside it sit a tiny old poet and a tiny boy. Close by, an ancient tree leans over the water with its long branches hanging down into the lake, and a pale salmon leaps under it. "
          "Far away beyond the lake, tiny on the horizon, a hall-town lies fast asleep on a white hill, not one window lit. "
          "Above that town, filling the upper half of the picture and drawn as overlapping pale cut-paper silhouettes in silver blue and slate, hovers an enormous fire-salamander with two great wing membranes spread over half the sky; "
          "the membranes glow a dull ember red along their veins, and along its throat seven holes are burnt through in a row like the holes of a flute, from which long wavy lines of music drift down over the sleeping town. Its whole shape is mirrored upside down in the lake. "
          "Palette: deep indigo, slate blue, silver grey, bone white, the dull ember red of the wing veins, and the one warm orange fire by the hut."))

S['m06_era'] = dict(
    kind='era', look='night',
    text=("Scene: an autumn night deep in a forest without end, its tall trunks drawn as rows of pale cut-paper shapes. In a clearing a little right of centre stands a round wooden hut with nine doors facing nine ways; "
          "a hearth burns at its centre, and its light shines out through all nine open doors like the spokes of a wheel. A tiny man sits on one threshold whittling a stick, and a tiny woman stands beside the hut looking out into the trees; a small stream runs past. "
          "All around the clearing the forest is scored with long black scorched furrows that cross one another like a net, the trees felled along them. "
          "Behind the trees, filling the upper half of the picture and drawn as overlapping cut-paper silhouettes in slate and silver blue, looms an enormous rhinoceros, its back higher than the treetops, its head lowered toward the hut; "
          "its single long horn glows red-hot, and the furrow it has just ploughed still smokes behind it. "
          "Palette: deep indigo, slate blue, silver grey, bone white, charcoal black in the furrows, the red-hot horn, and the warm orange light of the hearth."))

S['m08_era'] = dict(
    kind='era', look='night',
    text=("Scene: a summer night on the eastern edge of a black-stone highland. A little right of centre a long timber hall stands on a ridge with its great door open and a hearth glowing inside, and no one is singing there: the benches are empty. "
          "On the mountain road before the door two tiny dwarves are arriving on foot: a stocky woman with two long copper-red braids and a white bone sword at her belt, and a stonemason with a plaited beard and chisels stuck in his apron. "
          "Behind the ridge lies a round pool of perfectly black water in which nothing is mirrored, not even the stars. "
          "Out of that pool, filling the upper half of the picture, rises an enormous eyeless salamander, drawn as overlapping cut-paper silhouettes in the darkest indigo and black, a little darker than the night around it, with thin pale echo lines along its edges: "
          "wet smooth skin without scales, four long thin limbs, a broad blunt head, and a mouth that opens wider than the hall's door, from which long wavy lines of wailing spread across the sky like ripples on water. "
          "Palette: near-black indigo, slate blue, silver grey, bone white, a touch of copper red in the woman's braids, and the one warm orange hearth."))

S['m09_era'] = dict(
    kind='era', look='night',
    text=("Scene: noon at the edge of the first forest, and the sky is the colour of dusk. The forest stretches away as rows of pale cut-paper treetops, and from the middle of it one colossal tree rises above all the others like a pillar holding up the sky. "
          "On the crown of that tree perches an enormous bird, drawn as overlapping pale cut-paper silhouettes in slate and silver blue, and its two spread wings cover the whole sky from one edge of the picture to the other, so that everything beneath them lies in a dim blue twilight; "
          "its two huge round eyes look down from above the canopy. At the far left and right edges, beyond its wingtips, thin veils of rain are falling in pale daylight; under the wings the forest is dry and dark. "
          "In front, a little right of centre, a row of white standing stones marks the edge of the forest, and behind the stones lies the small camp of the watchers: one small fire and a few tiny long-eared archers, one of them holding a great longbow taller than himself and looking up. "
          "Palette: slate blue, deep indigo, a dusky violet grey, silver, bone white in the stones, and the one warm orange campfire."))

S['m10_era'] = dict(
    kind='era', look='night',
    text=("Scene: an autumn night at the southern foot of a great mountain range. Under the wall of a small city lies the camp of an allied army: rows of tiny tents, round shields stacked in lines, tiny soldiers with wooden spears, and many small campfires, the nearest a little right of centre. "
          "Beyond the camp the mountainside is covered from mid-slope down by a white forest: every tree is white from tip to root and has not a single leaf, and thin threads of lightning hang in the branches. "
          "On the mountain above, filling the upper half of the picture and drawn as overlapping pale cut-paper silhouettes in bone white and silver blue, stands an enormous stag, its shoulders higher than the city wall, "
          "its antlers branching across the whole sky like a bare forest; zigzag lightning is caught and coiled among the tines. "
          "Palette: deep indigo, slate blue, silver, bone white, a pale violet in the lightning, and the warm orange of the campfires."))

S['m11_era'] = dict(
    kind='era', look='night',
    text=("Scene: a summer night at the place where the southern shore forks. On the left a slow river of lava runs down a black slope into the sea in glowing red seams; on the right tall pillars of lightning stand upon the sea; "
          "between them the water boils, and white steam rises and fills the middle of the picture. In the steam, drawn as overlapping pale cut-paper silhouettes in silver blue and slate, crouches an enormous three-headed beast that could cover a fishing village: "
          "a lion's head larger than a city gate, a goat's head whose horns spread like two mountain ridges, and for a tail a great serpent that trails away into the sea. "
          "High above the steam, small and bright among the clouds and stars, a white winged horse flies free with no rider on its back. "
          "On the shingle in front, a little right of centre, one small fire burns, and beside it stands one tiny young man with a sealed letter in his hand, looking up at the horse. "
          "Palette: deep indigo, slate blue, silver grey, bone white, a pale violet in the lightning, the ember red of the lava, and the one warm orange fire."))

S['m12_era'] = dict(
    kind='era', look='night',
    text=("Scene: a summer night in a harbour kingdom on the western sea. A bay lies between two long reefs that close around it like two cupped hands; inside the bay stands a city whose walls rise straight out of the water, "
          "with a palace of white stone on its northern height and, beside the palace, one tall slender tide-watching tower, the highest thing in the city. Warm lamps burn in the windows and are mirrored in the still water; "
          "small pearl divers' boats lie along the quay, each with a tiny lantern. On the top of the tower stands a tiny girl with a crown of white pearls, singing. "
          "Outside the bay, filling the upper half of the picture and drawn as overlapping pale cut-paper silhouettes in silver blue and slate, the back of an enormous sea beast rises out of the deep water like a newly risen reef, the sea heaping up behind it, "
          "and from it long lines of answering song rise and curve over the whole bay like waves. "
          "Palette: deep indigo, sea slate, silver, pearl white, and the small warm orange lamps of the city."))

S['m13_era'] = dict(
    kind='era', look='night',
    text=("Scene: an autumn night on a hillside above a western harbour. A little right of centre stands a small house, and by its door hangs one lamp, lit, the warmest point in the picture; under the lamp sits a tiny young woman mending a fishing net. "
          "Below the hill lies the harbour with its masts and one long hall with a small fire on its roof. Beyond the harbour the whole sea is covered in fog, drawn as soft pale cut-paper bands lying one over another; "
          "and in the fog, filling the upper half of the picture, floats an island that is really the back of an enormous whale: grass and small trees grow on it, birds settle on it, a few tiny ships are moored to it, "
          "and under the waterline one huge eye, larger than a sail, is half open. Far out, between the harbour and the island, one tiny boat with a single sailor is lost in the fog. "
          "Palette: deep indigo, slate blue, fog silver, bone white, and the one warm orange lamp by the door."))

S['m14_era'] = dict(
    kind='era', look='night',
    text=("Scene: an autumn night on a great plain, darker than any night before it. The plain is strewn with pale stones turned up out of the earth, a few of them hanging in mid-air, and a dozen tiny walled towns stand across it with their gates shut and not one light showing. "
          "Only at the east gate of the nearest town, a little right of centre, one fire still burns: a tiny boy of fifteen in an old hide cloak crouches beside it feeding it wood, and next to the fire a wolf pelt is spread over a stone, left empty for whoever comes in from the dark. "
          "Across the plain behind the towns, filling the upper half of the picture and drawn as overlapping cut-paper silhouettes in dark slate and silver blue, comes an enormous wild boar taller than any town gate: "
          "its mane is row upon row of standing stone spikes, its two tusks curve like ploughs, its snout is lowered and roots up the plain in long furrows, and where it has passed the towns' fires are trampled out into thin threads of smoke. "
          "Palette: near-black indigo, slate blue, silver grey, bone white, and the one warm orange fire at the gate."))

S['m15_era'] = dict(
    kind='era', look='dawn',
    text=("Scene: the first dawn. An autumn plain of pale stones and ripe wheat at the very end of the long night. On the right stands a small walled town; before its east gate one small fire burns, tended by a tiny old man in a patched hide cloak, a woman splitting wood beside him. "
          "In the middle of the plain, a little right of centre, eleven tiny kings stand in a ring around a low white stone on which rests a plain circlet of gold; each king holds a small lamp, and behind them the camps and plain banners of their eleven armies spread across the fields. "
          "Beyond them, filling the upper half of the picture, the sun is rising for the first time in the history of this world: the great disc of the sun, pale white gold, stands half risen on the horizon, "
          "and from it long straight rays spread across the whole sky like the points of a crown, drawn as overlapping pale cut-paper bands with thin lighter echo lines; the deep indigo night, with its last few stars, is pushed back into the two upper corners. There are no beasts and no giant figures in this picture. "
          "Palette: deep indigo in the corners, slate blue, silver, bone white, a pale white gold in the sun and in the wheat, and the small warm orange of the fire and the eleven lamps."))

S['m16_era'] = dict(
    kind='era', look='dawn',
    text=("Scene: the first spring after the first dawn, early morning. In the middle of a wide basin three rivers flow together into one, and where they meet lies an island terraced with rings of small plain stone altars; "
          "on every altar stands one small cold white lamp, so that through the thinning river mist the island shows as a ring of pale lights. Three bridges lead to the island, crowded with tiny people walking empty-handed; "
          "at each bridgehead stands a rack hung with the blades they have handed in, and on the rivers tiny boats carry people who hold small warm lanterns. "
          "On a few of the altars tall pale robed figures are already seated; most of the altars are still empty. "
          "Above the island, filling the upper half of the picture and drawn as overlapping pale cut-paper silhouettes in bone white, silver and soft blue, more of them are arriving: vast calm robed figures, men and women, "
          "walking down out of the morning light toward the empty altars, their long robes and hair flowing down around the island like mist, their faces left blank. They are gentle and grave, not threatening. "
          "Palette: pale silver, bone white, soft slate blue, a little cold gold where the morning touches the water, and the small warm orange lanterns on the boats."))

S['m17_era'] = dict(
    kind='era', look='day',
    text=("Scene: high noon over a roaring chasm. A sheer cliff wall runs across the picture, and cut into it is a long row of forge mouths whose small fires glow like a string of lamps hung on the rock; below, a torrent thunders through the gorge in white falls and spray. "
          "At the mouth of the gorge one narrow stone bridge crosses the water, barely wide enough for two to walk abreast. On the bridge, a little right of centre, stands one tiny stocky dwarf, alone, feet planted, with a great round shield on his arm that glows red-hot; "
          "behind him a tiny boy runs back along the bridge toward the forges. "
          "Beyond the far end of the bridge the whole far bank and the sky above it are filled with a host pressing toward him, drawn as overlapping pale cut-paper silhouettes that rear over the bridge like one great wave: maned wolves, horned beasts and raiders with spears, shoulder over shoulder. "
          "The noon sky is bone white and pale blue, without shadows. "
          "Palette: bone white, pale silver, soft slate blue, deep indigo down in the gorge, and the warm orange of the forge fires and the red-hot shield."))

S['m18_era'] = dict(
    kind='era', look='day',
    text=("Scene: the long afternoon of a summer's day. Wheat fields roll away to the horizon in long flowing rows that bend like waves, and two small walled towns stand a day's road apart, one near, a little right of centre, and one tiny in the distance. "
          "The gate of the near town stands open: in the gateway a tiny woman guard with a long spear beckons with one arm, a small lamp hanging in the arch above her, and on the road before the gate a small covered two-wheeled cart has stopped, drawn by an old horse, its tiny round-faced driver looking up at her. "
          "Far off along the same road, filling the upper left of the picture and drawn as overlapping pale cut-paper silhouettes in ash grey and slate, an enormous grey beast lies across the road like a hill of ash, "
          "its mouth wide enough to take a cart and its horse together, the fields around it eaten down to bare earth. "
          "Above it and above the two towns, great slow afternoon clouds are drawn as overlapping pale silhouettes that curve around the open gate like waves. "
          "Palette: bone white, pale silver, soft slate blue, pale straw in the wheat, ash grey, and the one small warm lamp in the gateway."))

S['m19_era'] = dict(
    kind='era', look='cb',
    text=("Scene: early evening at the start of winter, the first snow just beginning to fall. A broad paved road runs straight across the picture through a small town and on toward the horizon; "
          "at both ends of the town rows of stopped wagons wait with tiny lanterns, and tiny townspeople stand watching. "
          "Across the road, where it has lain for eleven years with moss and small trees grown on its back, an ancient dragon is rising at last: a heavy Western wyrm drawn as overlapping pale cut-paper silhouettes in slate and silver blue, "
          "its body lifting from the road, its two bat-like wings opening across the whole upper half of the picture, earth and old moss sliding from its shoulders. "
          "On the road in front of it, a little right of centre, one tiny girl sits calmly with an account book open in her lap and a small lamp beside her. "
          "Dusk: the sky is slate violet, with one band of pale light low on the horizon. "
          "Palette: slate violet, deep indigo, silver grey, bone white, a grey moss green, and the small warm orange of the lamp and the lanterns."))

S['m20_era'] = dict(
    kind='era', look='cb',
    text=("Scene: the dusk when seven kings laid down their swords. Three rivers meet around an island ringed with small stone altars, a small lamp on each, and mist rises from the water. "
          "At the heart of the island stands a round stepped platform, and around its foot, a little right of centre, stand exactly seven tiny crowned kings in a half ring, each in a mantle of a different colour, each holding out a sword hilt first; no one has stepped up yet. "
          "Behind them, along the banks of the three rivers, their seven armies wait as rows of tiny spear points and plain banners; among the tents one small field tent has a single white candle burning at its door. "
          "Upon the platform and above it, filling the upper half of the picture, a goddess of pale light is just taking shape, drawn as overlapping pale cut-paper silhouettes in bone white and silver: "
          "a tall slender woman in a plain robe, faceless, without any halo, one hand raised as if asking a question, her robe flowing down around the island like mist. "
          "The sky is slate violet with one band of pale light on the horizon. "
          "Palette: slate violet, deep indigo, silver, bone white, small touches of seven colours in the kings' mantles, and the warm orange of the lamps and the candle."))

S['m21_era'] = dict(
    kind='era', look='night',
    text=("Scene: night in a quarry valley among white mountains. The cliffs on both sides are cut back in white steps; a river runs down the valley with stone barges on it, and beside the river a small village shows a few lit windows. "
          "Along the valley road, a little right of centre, a line of tiny villagers with lanterns walks on, unharmed. "
          "Above them, filling the upper half of the picture and drawn as overlapping pale cut-paper silhouettes in bone white and silver blue, a giant quarryman walks bent double, carrying an entire white mountain on his back: "
          "a huge broad back, a rope across his chest, a staff in one hand, and the ridges of the mountain he holds up curve over the whole valley like a wave that does not fall. His face is turned down and is not shown. "
          "Palette: deep indigo, slate blue, silver, bone white, and the small warm orange lanterns and windows."))

S['m22_era'] = dict(
    kind='era', look='night',
    text=("Scene: a winter night in the valley before the gate. Two sheer cliffs stand one on each side of the picture, their faces carved all over with rows of tiny notches from top to bottom. "
          "Between them runs a narrow valley crowded with tiny huts and waiting people, with a single well among them. At the far end of the valley, in the middle of the picture, a great stone gate is set in a wall of mountains and stands shut, "
          "a thin line of pale light showing at its crack; wind streams out through that crack and down the valley. "
          "A little right of centre one forge burns, the only warm light: a tiny smith links small rings into one long chain, and the chain winds on through the crowd and up the valley to the foot of the gate. "
          "Above the gate, filling the upper half of the picture and drawn as overlapping pale cut-paper silhouettes in slate and silver blue, a great ring of mountains curves away to left and right like a crown, hiding the basin inside it; a faint pale glow rises from within the ring. "
          "Palette: deep indigo, slate blue, silver grey, bone white, and the one warm orange forge fire."))

S['m23_era'] = dict(
    kind='era', look='tower',
    text=("Scene: the night the first tower was lit. A city lies in a basin inside a ring of dark mountains. From its centre rises one impossibly tall, slender tower of white stone, its tip among the clouds, wooden scaffolding still standing around its foot. "
          "At its top a single star of cold white light has just been kindled: fine straight rays spread from it, and beneath it a great dome of pale light covers the city and pushes the night back, the edge of the dome drawn as one precise arc. "
          "Under the dome every house has a small lamp hung at its door, and they are all lighting at once, street after street of tiny cold lights. There is only this one tower, and nothing floats in the sky. "
          "Outside the arc, in the darkness in front, a little right of centre, stands a small crowd of tiny people who have come in out of the night, a few of them holding torches, looking in. "
          "The light sweeps outward from the tower in long curved bands that circle the city like waves, with thin echo lines along their edges. "
          "The only warm colour in the picture is those few torches outside the arc; every other light is cold white, pale silver or faint blue. "
          "Palette: deep indigo, slate blue, silver, cold white, a little pale violet, and the tiny warm orange torches."))

S['m24_era'] = dict(
    kind='era', look='dca',
    text=("Scene: the feast in the sky. An entire mountain peak, cut off and turned upside down, floats point-down in the night sky in the middle of the picture. On its flat upper face stands a white city of colonnades and domes that has no streets, "
          "only halls joined by open galleries with cloud beneath them: a ring of halls around one great hall that is open to the sky, where a long banquet table is laid and lamps hang like strings of pearls. "
          "Far below it lies a great city where three rivers meet, full of slender towers, each with a point of cold white light, and thin vertical lines of light join those towers to the floating city above. "
          "Around the floating city, filling the upper half of the picture and drawn as overlapping pale cut-paper silhouettes in bone white and silver blue, vast calm robed figures are seated like guests around a table, their faces left blank, their robes flowing down past the mountain like cloud. "
          "On one of the open galleries, a little right of centre, one tiny guard walks alone past a hall whose door stands a hand's breadth open; a thin warm light falls from the crack onto the floor at his feet, and it is the only warm colour in the picture. "
          "Palette: deep indigo, slate blue, silver, cold white, pearl white, and that one small warm light."))

S['m25_era'] = dict(
    kind='era', look='de',
    text=("Scene: the road out of the light. On the left stands a white city with low walls and straight streets under a dome of pale tower light; a slender tower with a point of cold white light rises at its centre, and the edge of the dome is one precise arc that cuts across the picture. "
          "From a gate under that arc a long file of tiny horned people, men, women and children carrying bundles, walks out into the dark along a road that winds away to the right in one great S-curve toward a deep rift valley of stacked cliffs on the far horizon. "
          "At the head of the file, a little right of centre, a horned woman carries a child; here and there along the file someone carries a small lantern, and those lanterns are the only warm colour in the picture. "
          "Inside the arc everything is bright, even and shadowless; outside it the night is deep and wide, with a few stars, and the land is drawn as long dark waves. "
          "The bands of tower light curve over the city like waves, with thin echo lines along their edges, and stop exactly at the arc. Nothing floats in the sky. "
          "Palette: cold white, silver and pale ice blue inside the arc; deep indigo and slate outside it; and the small warm orange lanterns."))

S['m26_era'] = dict(
    kind='era', look='fd',
    text=("Scene: the last of a long night in the rift valley. A deep rift of stacked cliffs runs across the lower part of the picture; small villages cling to its walls, their houses joined by slender wooden bridges, "
          "and at the very bottom of the rift, a little right of centre, one white candle burns, the only warm light in the picture. "
          "From the rim of the rift a road climbs out and winds away across a wide plain in one long S-curve; on it walks a small party of tiny horned envoys, the first of them carrying a rolled scroll. "
          "Far away where the road ends, filling the upper half of the picture, a ring of mountains stands on the horizon, and above it floats a high palace-city of slender towers on its disc of stone, crowned with points of cold white light; "
          "its light spreads across the sky in long curved bands, drawn as overlapping pale cut-paper shapes with thin echo lines, and fades long before it reaches the rift. Nothing is falling and nothing is burning. "
          "Palette: near-black indigo, slate blue, silver, cold white in the far lights, and the one warm candle."))

S['m27_era'] = dict(
    kind='era', look='ed',
    text=("Scene: the last night of an empire, seen from a height. Inside a ring of dark mountains a whole capital lies laid out as one vast perfect ring, circle within circle of streets filled with cold white light, "
          "a crown of slender lamp towers all round its rim, and ten taller towers in an inner circle burning brighter than all the rest. Above the ring of mountains floats the upper city on its great disc of stone, with its palace and its forest of towers. "
          "At the exact centre of the rings stands one tiny lone figure in a long plain robe, seen from behind, looking up; no face is shown. "
          "The bands of light circle him like waves, drawn as overlapping pale cut-paper shapes with thin echo lines along their edges. The sky overhead is perfectly dark and empty, pressed far away by the light, without a single star. "
          "Everything is cold white, silver and pale blue, very still, very bright, a little too perfect; the only warm colour in the whole picture is one tiny glow from a baker's oven in a street of the lower city, in front and a little right of centre. "
          "Palette: cold white, silver, pale ice blue, deep indigo at the top edge, and that one tiny warm glow."))


def job(key):
    s = S[key]
    if s['kind'] == 'era':
        p = PV_LEAD + s['text'] + PV_STYLE + PV_ROOM + F.WEST_PLAIN + PV_NO_MOON + F.CLEAN
        return p, [os.path.join(PVD, 'pv1_%s.png' % n) for n in PV_REFS.get(s['look'], s['look'])]
    if s['kind'] == 'era_stone':
        p = ERA_SERIES + s['text'] + F.STYLE_LOCK + MURAL_FEEL + ERA_ROOM + F.WEST_PLAIN + ' There is no moon and no crescent anywhere in the picture.' + F.CLEAN
        return p, F.lock_refs()
    style = [os.path.join(LC, n + '.png') for n in s['style']]
    refs, who = list(style), ''
    if s.get('row'):
        refs.append(lineup(key + '_row', [(k, c) for k, c, _ in s['row']]))
        who = ROW % '; '.join(d for _, _, d in s['row'])
    elif s.get('who'):
        refs += [ident(k, c) for k, c, _ in s['who']]
        who = ONE if len(s['who']) == 1 else MANY % (len(s['who']), '; '.join(d for _, _, d in s['who']))
    refs += s.get('extra', [])
    lead = (LEAD_KEY if s['kind'] == 'key' else LEAD_CUT) % len(style)
    p = lead + (LOOK % (s['light'], s['camera'])) + who + ((DRAGON + ('' if s.get('blade') else NO_BLADE)) if s.get('dragon') else '') + s['text'] + ' ' + (KEY_ROOM if s['kind'] == 'key' else '') + FACE + (TAIL % (RAW if s.get('raw') else CALM))
    return p, refs


# 只改一处的重画：拿上一稿当参考，别的都不动。上一稿在的时候走这一路。
FIX = {
    # 断刃：第二稿（直接一些的那一稿，m07_d_maren_v2.png）人是正面，背上那一株金线的麦穗被画到了胸口上，拿它只改这一处出了第三稿（m07_d_maren_v3.png）。
    # 第四稿：用户看了最后一环第三稿又回“麦伦的也照着第一版来，添加龙血和伤口”。拿第一稿当底（构图、镜头和他的姿势不动），把第三稿里的黑血和伤搬过来
    'm07_d_maren': (('m07_d_maren_v1.png', 'm07_d_maren_v3.png'),
                    "Redraw the FIRST attached picture. Keep its composition, its camera angle and above all the falling man's pose exactly as they are: he is seen from behind and to one side, his body flung out almost level in the air, "
                    "his right arm stretched up to the hilt that he still grips under the dragon's jaw, his left arm flung out behind him with the hand open, his legs trailing, his face in profile turned toward the dragon, "
                    "his long wheat-bronze hair tied low and streaming. Keep the dragon's head where it is, with the glowing blue-white tip of the broken blade standing out through the top of its skull, "
                    "its torn wings, the falling fragments of fire, the sheer pale cliff, the clouds, and the burnt red plain and the river far below. "
                    "Now make the scene as hard-fought as the SECOND attached picture, which shows the same moment from the other side. Take from it the following and nothing else. "
                    "One: black, smoking dragon blood pours from the wound under the jaw where the blade has gone in, and streams upward past the man in the wind of the fall; his sword arm is black to the elbow with it; "
                    "the dragon's neck and back are hacked open in many places, and those wounds too seep black smoking blood in long dark ribbons. "
                    "Two: the man is spent and hurt after three days of fighting: his plain linen shirt is torn at the shoulder and at the sleeves and is spattered and soaked black with the dragon's blood; "
                    "red blood runs from a gash across his brow down the side of his face, and from cuts on his forearm; his lip is split, his knuckles are split; the skin of his arms and neck has a dark burnt-copper colour. "
                    "Three: the ear of wheat embroidered in gold thread on the back of his shirt stays where it is in the first picture, and it alone is still clean and bright among the stains. "
                    "His face stays calm and shut, his green eyes open. Drops of black blood, sparks and torn cloud rush past large and out of focus in the near corners. "
                    "Blood and wounds are shown plainly, with no gore: no severed limbs, no exposed bone or organs. The same rendering, colours and finish as the first picture. Everyone is fully clothed. No moon. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 最后一环第三稿：用户看了直接一些的那一稿回“奥斯温的姿势调整回第一版的投枪姿势就差不多了”。拿第一稿当底（构图和投枪的姿势不动），把第二稿里的火、烧着的盾、血和烧伤搬过来
    'm07_d_oswin': (('m07_d_oswin_v1.png', 'm07_d_oswin_v2.png'),
                    "Redraw the FIRST attached picture. Keep its composition, its camera angle and above all the prince's javelin-throwing pose exactly as they are: he is seen from the side, lunging forward, "
                    "the throwing arm stretched straight out toward the dragon with the open hand just after the release, the other arm flung back, the quiver of javelins on his back, his face in profile looking up at the mark. "
                    "Keep the dragon's head and wings where they are, the ring of old shield-bearers behind him, the one-eyed old man large in the right foreground, the cliff and the sky. "
                    "Now make the scene as hard-fought as the SECOND attached picture, which shows the same moment. Take from it the following and nothing else. "
                    "One: the dragon's jaws are wide open and its next breath of fire is already pouring down out of them toward the prince in a broad torrent of red-orange flame, "
                    "while the javelin flies up through a narrow slit in that fire toward the dark scale under the dragon's throat, where a single point of light glows. "
                    "Two: the ground around them is burning; the round shields painted with a grey mountain are charred and burning at the rims, the old men's beards are singed, "
                    "two of the old men are down on one knee and bleeding but still hold their shields up, and the one-eyed old man in the foreground has blood running into his white beard. "
                    "Three: the prince is marked by the fight: the sleeve of his throwing arm is burnt away, there is a raw burn along that forearm, blood runs from a cut at his temple, there is soot on his face, "
                    "and the hem of his indigo robe is singed and smoking. "
                    "Blood, burns and soot are shown plainly, with no gore. The same rendering, colours and finish as the first picture. Everyone is fully clothed. No moon. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 第六歌时代原画头一稿把熔角犀那只烧红的角画成了一弯又长又细的红月牙，远看就是天上一轮红的弯月（这个世界不画月相）。只改角
    'm06_era': ('m06_era_v1.png',
                "Redraw the attached picture and keep everything about it exactly the same: the forest of pale trees, the round hut with its lit doors, the man on the threshold and the woman beside the hut, the stream, the black scorched furrows and the felled trunks, "
                "the enormous rhinoceros above the trees with its body, head and position, the smoke, the stars, the colours, the paper grain, the framing and the size. Change one thing only: the rhinoceros's horn. "
                "In the attached picture the horn is a long thin red crescent that looks like a crescent moon in the sky. Replace it with a stout, nearly straight, cone-shaped horn, thick at the base and tapering to a blunt point, about as long as the animal's head, "
                "standing on its snout and pointing forward and a little upward; it glows red-hot, brightest at the tip and darker toward the base, with a little heat haze around it. It must not look like a crescent, a sickle or a moon. "
                "There is no moon and no crescent anywhere in the picture. No text, no logo, no frame."),
    # 11-12 第七歌改稿：卡多克撤了，旅伴七个。时代原画火边那八个人拿掉一个（左数第六个，坐着的、披破斗篷的瘦男孩），别的不动
    'm07_era': ('m07_era_v1.png',
                "Redraw the attached picture exactly as it is: the same composition, the same dragon lying along the cliff with its wings over half the sky, the same wheat, the same river town with its two arch bridges and two ward-fires, "
                "the same small campfires on the beach, the same smoke rising in an S-curve and turning into stars, the same far town and line of fire, the same colours, paper grain, line and size. "
                "Change one thing only. Around the nearest and brightest campfire there are now SEVEN tiny people instead of eight. Remove the thin boy who sits in a ragged cloak, the sixth figure from the left, "
                "between the barefoot girl with the long staff and the tall girl with the bow, and let the wheat and the firelight fill the place where he sat; do not put anyone or anything else there. "
                "The other seven stay exactly as they are and where they are: the reaper with a sickle on his shoulder, the youth with a round shield and a spear, the girl with two thick braids sitting by the fire, "
                "the small boy sitting with a sack of grain, the barefoot girl with a long staff, the tall girl with a short bow and a quiver, the tall boy with a spear and a cloak. "
                "There is no moon and no crescent anywhere in the picture. No text, no logo, no frame."),
    # 城头那一幅原来叫一袋麦，他朝它举着半截仓签。改稿以后他回的是眠山两个字，改名“那一声”：手放下来，抬着头，刚说完，龙的眼睛睁开、整个头停了一口气。构图、龙、火、城不动
    'm07_n2': ('m07_n2_v1.png',
               "Redraw the attached picture. Keep everything about it: the same composition and camera, the same enormous red dragon head resting its chin on the battlement on the left with fire, half red and half black, leaking between its teeth, "
               "the same wall walk and merlons, the burning notice board on the gate tower at the right, the stone arch bridge crowded with fleeing townsfolk and the town and hills behind, the same light, colours, rendering and finish, "
               "and the same man in the same clothes standing in the flames on the right. "
               "Change only the man's gesture and the moment. He no longer holds anything out toward the dragon. His arm hangs at his side, and the half tally stick is gripped in his lowered fist against his thigh. "
               "He has lifted his face a little toward the dragon's eye, the way a farmer looks up at weather that is coming, and his lips are just parted: he has this instant said one quiet word to it, an old name. "
               "His face is calm and unafraid, with recognition in it and no anger; he is not shouting. "
               "The dragon has heard him. Its molten-gold eye, which was half closed in contempt, has opened wide and is fixed on him, and for this one breath its whole head is perfectly still, the fire between its teeth held back. "
               "Keep his long wheat-bronze hair tied at the nape with a straw, his green eyes, his plain linen tunic with rolled sleeves and the belt of plaited straw rope. The flames still curl round his boots and do not burn him. "
               "Everyone is fully clothed. No moon. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 白线之晨原来画的是卡多克（m07_d_cadoc.png，用户认过那一稿的构图）。改稿以后走到红土线上的是麦伦：构图、龙、盐车、远处那一排人不动，只换人，
    # 红火绕着他走，黑火烧上了他左半边身子。第二张参考（城头那一幅）只拿来认他的长相和衣裳
    'm07_n2b': (('m07_d_cadoc.png', 'm07_n2_v1.png'),
                "Redraw the FIRST attached picture. Keep its composition, camera, light, colours, rendering and finish exactly: dawn at the foot of the long cliff, the burnt red earth with its edge like a shoreline, "
                "the immense red dragon head coming down from the upper left with one molten-gold eye, the fire pouring from its jaws half red and half black, the two-wheeled cart loaded with sacks and blocks of white salt on the right, "
                "the salt melting in the heat and running down in white streams onto the red earth and drawing a white line across it, the line of some thirty armed men and women far behind on the left who watch and do not move, "
                "the pale wheat stubble, the salt crystals and sparks large and out of focus in the corners. "
                "Change the person. In place of the boy stands the grown man from the SECOND attached picture, and he must be recognisably that same man: tall and lean, about twenty-six, with long wheat-bronze hair tied at the nape with a straw, green eyes, "
                "a plain linen tunic with the sleeves rolled up, a belt of plaited straw rope with half of a split wooden tally stick tied to it, dark trousers and worn boots. He wears no cloak. "
                "He carries no weapon of any kind, no sickle and no blade: he has come the way a village brings its yearly tribute, and one hand still rests on the shaft of the cart he has pulled here alone. "
                "He stands where the boy stood, in the same upright pose, facing the dragon with his head raised and his mouth closed; he does not step back and he does not kneel. "
                "The red flame streams around him and does not touch him. The black flame does not spare him: it has caught his left arm and shoulder and the left side of his chest, the linen there is burning away in black tatters, "
                "and the skin under it is scorched to the dark colour of burnt copper with raw red burns at its edges. He bears it without flinching. Burns and soot are shown plainly, with no gore. "
                "Everyone is fully clothed. No moon. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
}


def one(key):
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
        print('失败', key, e, flush=True)


if __name__ == '__main__':
    args = sys.argv[1:]
    # 参数可以是键（m07_n1）、时代（m07，这个时代的全部）、era（二十七幅现行的时代原画）或者 all
    keys = [k for k in sorted(S) if k in args or k.split('_')[0] in args or args == ['all'] or ('era' in args and k.endswith('_era'))]
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
