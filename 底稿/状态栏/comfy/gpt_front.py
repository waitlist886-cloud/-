#!/usr/bin/env python3
# 门面（介绍页重做）的美术。11-10 起，方向在根目录 门面重做_方向稿.md。
# 画风照用户 11-10 给的那一批参考（语料/门面参考_11-10/画风_*，不进库）：平涂的装饰插画，大曲线，纸的颗粒。纹样用西幻的，不用祥云灯笼。
# 角色自己的立绘、艺术照照旧走 gpt_sheet.py 那一套，这里只管片头、牌、分屏和各纪的书用的底图。
#   python gpt_front.py t1 t2 t3     出这几张，写 out/门面_试_11-10/<键>.png，已有的跳过；不带参数列出有哪些键
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from gpt_gen import gen

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.normpath(os.path.join(HERE, "..", "..", "..", "语料", "门面参考_11-10"))
OUT = os.path.join(HERE, "out", "门面_试_11-10")


def ref(*names):
    return [os.path.join(REF, n) for n in names]


def head_crop(src, dst, box):
    """从用户给的形象图上裁出头和领口，只拿发色、瞳色、头饰当参考，不带姿势。box 是左、上、右、下占整张的比例。"""
    if os.path.exists(dst):
        return dst
    from PIL import Image
    im = Image.open(src).convert("RGB")
    w, h = im.size
    im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h))).save(dst)
    return dst


# 画法：照参考图的做法，不照它的人物、构图和纹样
STYLE = (
    " Drawing manner: a flat decorative event illustration, in the same hand as the attached style reference pictures. "
    "Large clean flat colour shapes layered like cut paper; big flowing S-curves and spirals of smoke, flame, cloth and water that sweep around the focal point; "
    "thin lighter echo lines running along the edges of the big shapes; a limited harmonious palette of two or three hues plus warm cream white; "
    "only soft inner gradients; a fine paper grain over everything; soft drop shadows between the paper layers. "
    "No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D render. "
    "Figures are simplified, drawn in clean anime cel style with flat colours and elegant thin line art. "
    "Take only the drawing manner from the style references: do not copy their characters, compositions, symbols or lettering."
)
# 西幻护栏：技法照参考，纹样不照（参考图多是东方题材的活动页）
WEST = (
    " The world is Western high fantasy with medieval and Renaissance Europe as its base. "
    "Ornament comes from Art Nouveau borders, stained-glass tracery, illuminated-manuscript vines, tarot-card frames, heraldry, flames, smoke, feathers, wheat and thorns. "
    "No East Asian motifs: no auspicious-cloud spirals, no paper lanterns, no pagodas or upturned eaves, no hanfu or kimono, no knotted tassels, no calligraphy brush strokes, no koi, no Chinese dragons."
)
CLEAN = " No text, no letters, no numerals, no logo, no interface elements, no watermark, no signature."

T1 = (
    "Draw one wide 3:2 landscape picture. The first three attached pictures are style references. The last attached picture shows only the hair, eyes and hair ornaments of the woman in this scene: "
    "take her colours and ornaments from it and nothing else, not the pose and not the clothing cut. "
    "Scene: the temple of death, a vast dark hall seen frontally and symmetrically. In the centre, behind a long dark stone table, sits the Ruler of Death, an adult woman of calm and grave beauty, "
    "seen from the waist up, eyes closed, head slightly bowed. Very long straight white hair flows down past the table edge, one small stray lock on top of her head; a pair of red eye-shaped ornaments at her temples. "
    "She wears a high-collared black gown with thin red and silver line patterns that covers her completely from neck to wrists, and long black gloves with pointed fingertips; she is dignified and fully clothed. "
    "Both her hands rest on the table, the right hand just letting go of a card. Behind her spread large crimson wing-like shapes, each feather bearing a closed or half-open red eye, fading into the dark. "
    "On the table in front of her stand four tall arched cards side by side, like four small stained-glass windows with thin ornate silver frames. "
    "Card one: a small fire under a starry night with huge beasts carved in stone around it, cold silver grey and blue with one warm flame. "
    "Card two: a long white wall under a blood-red sky with crossed spears, iron grey and dark red. "
    "Card three: a black stele and a white stele standing back to back with one sword of dawn before them, obsidian black, white stone and amber. "
    "Card four: a round well descending into deep blue with a ring of golden light at the bottom, deep blue and gold. "
    "A few embers rise slowly. Palette of the hall: black, deep crimson, bone white and a little silver; each card keeps its own palette. Leave calm empty dark space at the top."
)
T2 = (
    "Draw one wide 3:2 landscape picture, a single plate from a storybook-style trailer that tells the history of a world. All the attached pictures are style references. "
    "Scene: the long night before the first dawn. In the lower centre a single small fire burns, the only warm colour in the picture. A woman kneels beside it and shelters the flame with both hands; "
    "she is drawn small and simplified, wearing furs and rough wool, with one long braid. Around the fire sits a ring of tiny huddled people in furs. "
    "All around and above them the darkness is filled with enormous beasts drawn as overlapping cut-paper silhouettes in cold silver blue and slate: a mammoth with long tusks, a great stag with a forest of antlers, "
    "a serpent-like wingless dragon coiled across the sky, a whale swimming in a sea of mist. Their bodies curve and spiral around the little fire like waves, with thin pale echo lines along their edges, as if painted on a cave wall. "
    "The smoke of the fire rises in one long S-curve and turns into a river of stars. A faint pale glow lies on the horizon. No moon. "
    "Palette: deep indigo, slate blue, silver grey, bone white, and one warm orange flame."
)
T3 = (
    "Draw one wide 3:2 landscape picture divided into four tall vertical panels side by side. The panels are separated by thin burning seams, lines of ember and small flame, as if the picture had been cut apart by fire. "
    "All the attached pictures are style references. Each panel is its own age of one world, with its own palette, all drawn in the same flat decorative manner. "
    "Panel one, cold silver and blue: a cave wall painted with hunters and a great beast in ochre and silver lines, lit from below by a small fire; far above, a tall slender tower with a point of white light. "
    "Panel two, iron grey and dark red: a winding road across a battlefield climbing toward a long white wall on the horizon; broken siege engines and planted spears stand along the road; a red sky. "
    "Panel three, obsidian black, white stone and amber: a field of standing stone steles; the nearest stele is half black and half white, a plain sword planted before it; the first light of dawn breaks behind. "
    "Panel four, deep blue and gold: the view straight down a vast round shaft sinking into the earth, ring after ring of galleries and stairs, tiny lamps, one rope hanging down the middle, golden light at the very bottom. "
    "A small flame appears once in every panel."
)
# 11-10 夜用户看了三张试图，回“照那张定”：画风照 t2（片头月银纪那一幅）。
# 定稿样收在 底稿/门面/画风定稿样_t2.png，往后门面的图都拿它当第一张画法参考，再配一两张用户给的参考。
LOCK = os.path.normpath(os.path.join(HERE, "..", "..", "门面", "画风定稿样_t2.png"))
MAIN = os.path.join(HERE, "out", "门面_主画_11-10")
STYLE_LOCK = (
    " Drawing manner: the first attached picture is the approved sample of this very series. Match its hand exactly: the same shape language, line weight, paper grain, softness and level of detail. "
    "Large calm flat colour shapes layered like cut paper; the vast things in the picture are drawn as overlapping pale cut-paper silhouettes that curve and spiral around the small focal point like waves, "
    "with thin lighter echo lines running along their edges; people are tiny and simplified; one small warm flame is the only warm accent against a cool limited palette of two or three hues; "
    "plenty of quiet empty space; soft inner gradients only; a fine paper grain over everything. "
    "Keep it simple and airy: no dense ornament, no gothic tracery, no heraldic shields or coats of arms, no ornate picture frame, no border. "
    "No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D render. "
    "The other attached pictures are secondary style references. Take only the drawing manner from all of them: do not copy their characters, creatures, compositions or symbols."
)
# 定稿以后用的西幻护栏：不点装饰纹样的名字（点了它就往密里画），只说世界的底子和不要什么
WEST_PLAIN = (
    " The world is Western high fantasy with medieval and Renaissance Europe as its base: European arms, armour, masonry and dress. "
    "No East Asian motifs: no auspicious-cloud spirals, no paper lanterns, no pagodas or upturned eaves, no hanfu or kimono, no knotted tassels, no calligraphy brush strokes. "
    "Dragons, if any, are heavy Western wyrms with bat-like wings and swept-back horns, never long serpentine Eastern dragons with antlers or whiskers. No real-world heraldry such as lions rampant or fleurs-de-lis."
)
SERIES = "Draw one wide 3:2 landscape picture, a plate from the same storybook-style trailer series as the first attached picture. "

# 四纪的主画：下面一小团火和很小的人，上面是这一纪的庞然大物。月银纪那一张就是定稿样 t2。
K2 = (
    SERIES +
    "Scene: the age of the long war. Across the middle of the picture a colossal white stone wall runs in one great S-curve from the lower left to the far horizon, with towers along it. "
    "In the lower centre, on top of the wall, a single beacon fire burns in an iron brazier, the brightest warm point in the picture; around it stands a handful of tiny soldiers in plain helmets and cloaks, with spears and one plain banner without any emblem. "
    "Above the wall the whole sky is filled with two hosts of enormous beings drawn as overlapping cut-paper silhouettes, facing each other. "
    "On the right, over the defended land, giants of pale steel white and soft gold in armour: one raises a great round shield, one draws a bow of light, one carries a mountain on his shoulders. "
    "On the left, over the wasteland, giants of dark red and ember orange with horns and broken crowns: one has a single broken horn, one sits like a king among beasts. "
    "Their bodies curve around the little beacon like waves, with thin pale echo lines along their edges. "
    "Below the wall on the left lies a dark red plain with tiny broken siege engines and planted spears; on the right, the small lit windows of a town. A few falling sparks. "
    "Palette: iron grey, bone white, dark blood red, a little steel blue, and one warm orange flame."
)
K3 = (
    SERIES +
    "Scene: the age of the two kings. The sky is cut in two by one clean diagonal stroke, as if by a sword. The left half is night, obsidian black and grey, with fine grey ash falling like rain; the right half is dawn, white stone, pale gold and amber. "
    "In each half stands one colossal woman drawn as a cut-paper silhouette, the two back to back. On the night side, a slender witch-queen with very long pale hair and a long cloak, one hand raised, a few points of ember around her. "
    "On the dawn side, a swordswoman with her hair bound up and a long cloak blown sideways, holding a plain longsword upright before her. Both are fully clothed, calm and grave. "
    "Between them at the bottom centre stands a ruined city gate arch; inside the arch a small fire burns, and beside the fire sits a woven basket covered with a cloth. "
    "In front of the arch spreads a field of standing stone steles, each one half black and half white, with a few tiny people cutting letters into them. "
    "Curving bands of ash on the left and of light on the right sweep around the arch like waves, with thin echo lines along their edges. "
    "Palette: obsidian black, ash grey, white stone, amber and pale gold, and one warm orange flame."
)
K4 = (
    SERIES +
    "Scene: the age of the great labyrinth. We look down into a vast round shaft sinking into the earth. Ring after ring of galleries, arches and stairways spiral downward in great sweeping curves, "
    "drawn as overlapping cut-paper layers in deep blue and indigo with thin pale echo lines along their edges. "
    "In the centre one rope hangs straight down the shaft, with knots along it. On the rope and on a narrow ledge near the top a small party of tiny adventurers climbs down; one of them holds up a lamp, the only warm colour in the upper part of the picture. "
    "A few small paper notices are pinned to the wall beside them. In the darkness between the rings, enormous shapes are half seen as paler silhouettes, like things asleep in the walls: a great stone hand, a coil of wings, a horned head. "
    "At the very bottom of the shaft a ring of golden light glows, as if a dawn lay beneath the earth. "
    "Palette: deep blue, indigo, slate, bone white, gold, and one warm orange lamp flame."
)


# 11-10 夜用户看了 k3 回“双王的长相修正下”：头一稿把巴尔缇娜画成了戴兜帽的，索恩薇娅画成了浅金发。
# 照卡里 1001 那一套的立绘改（out/立绘_v3/baltina、thornevia 的 head.png 当长相参考），构图照 k3 不动，顺手去掉碑上那个月牙。
K3B = (
    "Redraw the second attached picture. The first attached picture is the approved style sample of this series. "
    "Keep the composition, the palette, the drawing manner and every other element of the second picture exactly as they are: the sky split by one diagonal stroke with ash rain on the left and dawn on the right, "
    "the ruined gate arch with the small fire and the covered basket, the field of half-black half-white steles with the tiny carvers, the sweeping bands of ash and light. "
    "Change only the two colossal women, so that they are clearly the two characters whose heads are shown in the third and the fourth attached pictures. "
    "Draw them in the same simplified flat cut-paper manner as before, still back to back, calm and grave, eyes closed or lowered, both fully clothed. "
    "Left, on the night side, the woman of the third picture: a slender long-lived woman with slightly pointed ears; very long straight ash-silver hair falling free down her back; one small braid along the side of her head, tied at the back with a black ribbon bow; "
    "no hood and nothing covering her head; a small red mark at her temple; a high-collared black gown and a long cloak with a deep crimson lining and a little gold trim; one gloved hand raised, a few embers above it. "
    "Right, on the dawn side, the woman of the fourth picture: a tall lean soldierly woman; dark old-copper brown hair, a reddish brown and not blonde, bound up in a braided bun at the back of her head, with one long thin strand falling in front of each ear; "
    "a white officer's coat with a little gold trim and a long white cloak blown sideways, brown leather gloves; she holds a plain longsword upright before her with both hands. No crown on either woman. "
    "Their hair colours must read clearly even though the figures stay pale and flat: silver grey on the left, dark copper brown on the right. "
    "Take only hair, face and ornaments from the third and fourth pictures, not their rendering style. "
    "Also remove the crescent carved on one stele at the right and leave that stone plain."
)
# 11-10 夜用户回“露脸”：神殿的牌桌照定稿画风重出。神殿照现有开场白：灰白石柱的长廊，柱间悬着青火，她坐在尽头的高座上。
T1B = (
    "Draw one wide 3:2 landscape picture in the same series and the same hand as the first attached picture. The second attached picture is a secondary style reference. "
    "The last attached picture shows only the hair, eyes and hair ornaments of the woman in this scene: take her colours and ornaments from it and nothing else, not the pose and not the clothing cut. "
    "Scene: the temple of death. A long hall of tall grey-white stone pillars recedes symmetrically into the dark; between the pillars hang still blue-green flames that light the hall with a cold clear light. "
    "At the end of the hall, in the centre of the picture, the Ruler of Death sits on a high seat behind a long pale stone table. She is an adult woman of calm and grave beauty, seen at middle distance from about the knees up, "
    "looking straight at the viewer with quiet golden eyes. Very long straight white hair falls along both sides of the seat down to the floor, one small stray lock on top of her head; a pair of red eye-shaped ornaments at her temples. "
    "She wears a high-collared black gown with a dark red mantle over her shoulders that covers her completely, and long black gloves with pointed fingertips; she is dignified and fully clothed. "
    "Her right hand is stretched out over the table, palm down, just letting go of a card. "
    "Behind the seat spread large wing-like shapes of deep crimson, drawn as overlapping cut-paper layers that curve around her like the great silhouettes in the first picture, with thin echo lines; each feather bears one closed or half-open red eye. "
    "On the table stand four tall arched cards side by side, each a small window into another world, and each holds one tiny warm flame, the only warm colours in the picture. "
    "Card one: cold silver blue, huge beasts around a small fire. Card two: iron grey and dark red, a long white wall with a beacon. "
    "Card three: half black and half white, a sword of dawn before two steles. Card four: deep blue, a round shaft with golden light at the bottom. "
    "Palette of the hall: grey-white stone, black, deep crimson, and the cold blue-green of the flames. Plenty of quiet dark space above her."
)


# 11-10 夜用户又改回“不露脸只有手”，脸留到建档完被请离神殿的那一眼。会动的小样要的分层素材：
# 神殿底图（竖幅，没有人、桌上是空的）、手、牌、翼上的眼睛，后三样透明底，各自能动。
SAMPLE = os.path.join(HERE, "out", "门面_小样_11-10")
STYLE_SPRITE = (
    " Drawing manner: the same hand as the first attached picture, the approved style sample of this series: flat cut-paper colour shapes, thin lighter echo lines along the edges, soft inner gradients only, a fine paper grain, "
    "no realistic lighting, no heavy rendering, no 3D. Keep it simple and clean."
)
SCENE_REF = "The second attached picture shows the scene these parts belong to. "
H_BG = (
    "Draw one tall 2:3 portrait picture in the same series and the same hand as the first attached picture. "
    "The second attached picture shows this scene in an earlier wide version: keep its hall, its still blue-green flames, its pale stone table, its palette and its drawing manner, and redraw it for a tall phone screen with these changes. "
    "The woman is not visible at all: at the end of the hall, where the high seat stands, there is only deep quiet darkness and the dim outline of the tall back of a stone seat. No person, no face, no hair, no hands anywhere in the picture. "
    "In the darkness behind the seat, large wing-like shapes of very dark crimson are barely visible, as overlapping cut-paper layers; all their eyes are closed. "
    "The pale stone table runs across the bottom of the picture and fills its lower third, seen from the front and slightly from above; its top is completely empty, no cards and no objects. "
    "Tall grey-white pillars stand on both sides and recede symmetrically into the dark; three or four blue-green flames hang between the pillars on each side. The upper third of the picture is calm darkness."
)
H_HANDS = (
    "Draw one wide 3:2 landscape picture on a fully transparent background. " + SCENE_REF +
    "Draw only two forearms with hands reaching straight down from the top edge of the picture, as seen by someone sitting across a table from their owner. "
    "They are the hands of the woman in the second picture: long black gloves with pointed fingertips, the cuffs of a black gown, and around each forearm the hanging edge of a dark red mantle; a few long straight strands of white hair hang beside each arm. "
    "The hand on the left side of the picture rests relaxed, palm down, fingers slightly spread. "
    "The hand on the right side of the picture is lowered with its index and middle fingers extended and the other fingers curled, as if it has just let go of a card. "
    "The two arms are far apart, one in the left third and one in the right third of the picture, with a wide empty transparent gap between them; they do not touch or overlap. "
    "The arms and the hair are cut off cleanly by the top edge. Nothing else: no table, no cards, no body, no face, no shadow, no background."
)
H_CARDS = (
    "Draw one wide 3:2 landscape picture on a fully transparent background. " + SCENE_REF +
    "Draw five tall cards standing upright side by side in one row, seen perfectly flat from the front, evenly spaced with clear transparent gaps between them, all exactly the same size and outline: "
    "a tall narrow card with a pointed-arch top and a thin pale silver frame, like the four cards in the second picture. "
    "Card one: cold silver blue, huge pale beasts curving around a small fire with tiny people. "
    "Card two: iron grey and dark red, a long white wall with a beacon fire under a red sky. "
    "Card three: half night black and half dawn gold, one plain longsword upright before two standing stones, one black and one white. "
    "Card four: deep blue, a round shaft seen from above with a golden light at the bottom and a tiny lamp near the top. "
    "Card five is the back of the cards: dark crimson, with one closed eye drawn in thin silver line in the centre and a thin silver border. "
    "Each of the first four cards holds one tiny warm flame. No table, no hands, no shadow, no background."
)
H_EYE = (
    "Draw one wide 3:2 landscape picture on a fully transparent background. " + SCENE_REF +
    "Draw three versions of one single large eye, side by side in one row, evenly spaced with clear transparent gaps, all the same size, like the eyes on the crimson wings in the second picture: "
    "an almond-shaped eye set on a dark crimson feather-shaped patch. First: fully closed, one curved lid line. Second: half open, the red iris half hidden under the lid. "
    "Third: fully open, a red iris with a narrow dark slit pupil and one small pale highlight. Deep crimson, red and a little pale rose only. Nothing else: no wings, no face, no background."
)


# 11-10 夜用户看了第一版小样回“效果还是不行”，给了崩铁《来自星空的寓言集·上篇》黑天鹅抽牌那一段当参考：
# 手是近景里的主角，一个镜头一个手势，镜头之间硬切。照第一版那两只手的设计，一只手一张竖幅大图，不带头发（好转动）。
STYLE_HANDS = (
    " Drawing manner: exactly the manner of the second attached picture, which belongs to the same series as the first attached picture, the approved style sample: "
    "flat cut-paper colour shapes, thin lighter echo lines along the edges, soft inner gradients only, a fine paper grain, crisp clean outlines against the transparent background, "
    "no realistic lighting, no heavy rendering, no 3D. Keep it simple and clean."
)
HANDS_REF = (
    "The second attached picture shows two gloved forearms already drawn for this series. Keep their design exactly: a long charcoal-black glove with a faint violet tint and long pointed fingertips, "
    "thin lighter echo lines along the fingers, the scalloped cuff of a black gown above the wrist, and the hanging folds of a dark crimson mantle around the forearm. "
)
HANDS_END = " The arm is centred horizontally. No hair strands. Nothing else: no table, no cards, no body, no face, no jewellery, no shadow, no background."
H2_OPEN = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS_REF +
    "Draw only ONE such forearm and hand, large, reaching straight down from the top edge of the picture, as seen by someone sitting across a table from its owner: the back of the hand faces the viewer. "
    "The pose is the open hand on the left of the second picture: palm down, all five fingers long, elegant and relaxed, slightly spread and gently curved, as if gliding just above a table top. "
    "The hand is big: the fingertips reach down to about five sixths of the picture height, the wrist sits at about half the height, "
    "and the cuff and the crimson mantle folds fill the upper part and are cut off cleanly by the top edge." + HANDS_END
)
H2_PRESS = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS_REF +
    "Draw only ONE such forearm and hand, large, reaching straight down from the top edge of the picture, as seen by someone sitting across a table from its owner: the back of the hand faces the viewer. "
    "The pose is the hand on the right of the second picture: the index and middle fingers extended straight down, close together, and the ring finger, the little finger and the thumb curled in, "
    "as if pressing two fingertips on a card that lies on a table. "
    "The hand is big: the two fingertips reach down to about five sixths of the picture height, the wrist sits at about half the height, "
    "and the cuff and the crimson mantle folds fill the upper part and are cut off cleanly by the top edge." + HANDS_END
)
H2_HOLD = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS_REF +
    "Draw only ONE such forearm and hand, large, rising straight up from the bottom edge of the picture; the back of the hand faces the viewer. "
    "The pose: the index and middle fingers are extended straight upward, close together, their tips slightly apart, exactly as if a thin card were pinched upright between them; "
    "the ring finger, the little finger and the thumb are curled in. It is the elegant gesture of holding up one card between two fingers, but there is no card in the picture: "
    "the space above and between the fingertips is empty. "
    "The hand is big: the fingertips are at about one fifth of the picture height from the top, the wrist at about three fifths, "
    "and the cuff with the crimson mantle folds fills the lower part and is cut off cleanly by the bottom edge." + HANDS_END
)


def hand_refs():
    return [LOCK, os.path.join(SAMPLE, "h_hands.png")]


# 11-10 夜用户看了第三版（手装了骨骼）：若娜瓦的手照神殿牌桌第一稿（t1）那一身来，不要袖子，黑丝手套加指甲；
# 夹牌的那只像六根指头，重画；两指之间要留出缝，牌才能放进两指的图层中间（一指在牌前、一指在牌后）。
STYLE_HANDS3 = (
    " Drawing manner: the first attached picture is the approved style sample of this series, and the third attached picture shows the same manner applied to a gloved hand "
    "(take from the third picture only how it is drawn, not its red sleeve, its cuff or its pose): "
    "flat cut-paper colour shapes, thin lighter echo lines along the edges, soft inner gradients only, a fine paper grain, crisp clean outlines against the transparent background, "
    "no realistic lighting, no heavy rendering, no 3D. Keep it simple and clean."
)
HANDS3_REF = (
    "The second attached picture shows the woman this hand belongs to: take from it only her colours, black with deep crimson accents. "
    "Design of the arm: a long opera glove of sheer black silk that covers the hand and the whole forearm and runs off the edge of the picture. "
    "Draw the glove as one smoky charcoal-black shape, a little lighter and warmer over the knuckles and the back of the hand where skin shows faintly through the thin silk, "
    "with a thin lighter echo line along its edges. Each fingertip ends in one long almond-shaped fingernail in deep crimson with a small pale highlight. "
    "There is no sleeve, no cuff, no cloak, no cloth, no bracelet and no ring: only the gloved arm. The hand is slender and elegant and has exactly five fingers. "
)
HANDS3_END = " The arm is centred horizontally. Nothing else: no table, no cards, no body, no face, no hair, no shadow, no background."
H3_OPEN = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS3_REF +
    "Draw only ONE such forearm and hand, large, reaching straight down from the top edge of the picture, as seen by someone sitting across a table from its owner: the back of the hand faces the viewer. "
    "Pose: palm down, the four fingers and the thumb all long, relaxed, clearly spread apart and gently curved, as if gliding just above a table top; the thumb points out to one side. "
    "The hand is big: the fingertips reach down to about five sixths of the picture height, the wrist sits at about half the height, "
    "and the gloved forearm runs straight up and is cut off cleanly by the top edge." + HANDS3_END
)
H3_PRESS = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS3_REF +
    "Draw only ONE such forearm and hand, large, reaching straight down from the top edge of the picture, as seen by someone sitting across a table from its owner: the back of the hand faces the viewer. "
    "Pose: the index finger and the middle finger are extended straight down and parted in a narrow V, so that a clear empty gap separates them along their whole length, from the knuckles to the nails. "
    "The ring finger and the little finger are curled up into the palm and show only as two small rounded knuckles beside the middle finger. The thumb is tucked behind the palm, out of sight. "
    "Count what is visible: two long extended fingers and two curled knuckles, nothing more. "
    "It is the gesture of picking up a card by its top edge between two fingers, but there is no card in the picture. "
    "The hand is big: the two fingertips reach down to about five sixths of the picture height, the wrist sits at about half the height, "
    "and the gloved forearm runs straight up and is cut off cleanly by the top edge." + HANDS3_END
)
H3_HOLD = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS3_REF +
    "Draw only ONE such forearm and hand, large, rising straight up from the bottom edge of the picture; the back of the hand faces the viewer. "
    "Pose: the index finger and the middle finger are extended straight up and parted in a narrow V, so that a clear empty gap separates them along their whole length, from the knuckles to the nails. "
    "The ring finger and the little finger are curled down into the palm and show only as two small rounded knuckles beside the middle finger. The thumb is tucked behind the palm, out of sight. "
    "Count what is visible: two long extended fingers and two curled knuckles, nothing more. "
    "It is the elegant gesture of holding up one card pinched between two fingers, but there is no card in the picture: the space between and above the fingers is empty. "
    "The hand is big: the fingertips are at about one fifth of the picture height from the top, the wrist at about three fifths, "
    "and the gloved forearm fills the lower part and is cut off cleanly by the bottom edge." + HANDS3_END
)
# 四纪各一张专属的牌背：整张图就是牌，一圈细框，当中一个徽记，各用这一纪主画的颜色，各有一点暖火。
STYLE_CARD = (
    " Drawing manner: the same hand as the first attached picture: flat cut-paper colour shapes, thin lighter echo lines along the edges, soft inner gradients only, a fine paper grain. "
    "Simple and airy, no dense ornament, no realistic lighting, no heavy rendering, no 3D."
)
BACK_COMMON = (
    "Draw one tall 2:3 portrait picture: the back of a fortune-telling card, seen perfectly flat from the front. The card fills the whole picture from edge to edge; the picture is the card itself, with square corners. "
    "No table, no hands, no shadow, and nothing outside the card. Layout: one thin double-line frame a little inside the edges, one small four-pointed star in each corner, "
    "and a single emblem in the centre with plenty of quiet empty ground around it. "
    "The first attached picture is the approved style sample of this series. The second attached picture is the main painting of the age this card belongs to: take its palette and its mood, not its composition. "
)
B_0 = BACK_COMMON + (
    "This is the card of the age before the first dawn. Ground: deep indigo and slate blue. Line work: silver white. "
    "Emblem: one small warm flame in the centre, the only warm colour on the card, inside a ring of seven small stars; around the ring a pair of stag antlers curves upward like a wreath."
)
B_1 = BACK_COMMON + (
    "This is the card of the age of the long war. Ground: iron grey, with dark blood red in the lower third. Line work: bone white. "
    "Emblem: a battlemented white tower with two crossed spears behind it; on top of the tower one small warm beacon flame, the only warm colour on the card; above the flame a plain crown broken in two."
)
B_2 = BACK_COMMON + (
    "This is the card of the age of the two kings. The ground is cut in two by one clean diagonal line: obsidian black on one side, white stone on the other. Line work: pale gold. "
    "Emblem: one plain longsword standing upright on the dividing line, with one standing stone on each side of it, a black one and a white one; "
    "at the foot of the sword one small warm flame, the only warm colour on the card."
)
B_3 = BACK_COMMON + (
    "This is the card of the age of the great labyrinth. Ground: deep blue and indigo. Line work: gold. "
    "Emblem: a round shaft seen from straight above, drawn as five concentric rings winding inward like a spiral stair, with one rope hanging to the centre; "
    "at the very centre one small warm lamp flame, the only warm colour on the card."
)
# 四纪的大幅牌背（11-12）：四条画带上放的不是这一纪的原画，是这一纪牌背的“精装版”：同一个徽记，画得更大更细，四周用这一纪的记号排成一幅对称的图。
# 原画留到选定以后张开才出现。小牌背（b_0 到 b_3）当第一张参考，徽记、底色、线色照它；不要边框（画带会裁掉左右一成），下面四分之一留暗留空给页面印字。
STYLE_BB = (
    " Drawing manner: the same hand as the attached small card back and the style sample: flat cut-paper colour shapes, thin lighter echo lines along the edges, soft inner gradients only, a fine paper grain. "
    "Richer and more finely drawn than the small card, but still calm and clear: big simple shapes first, fine line detail second, quiet ground between them. "
    "No dense filigree, no gothic tracery, no heraldic shields, no realistic lighting, no heavy rendering, no 3D."
)
BB_COMMON = (
    "Draw one tall 2:3 portrait picture: the grand full-art edition of the back of a fortune-telling card, seen perfectly flat from the front and filling the whole picture from edge to edge. "
    "The first attached picture is the approved small card back of this age. Keep its emblem: the same objects, the same shapes, the same colours, the same ground colours and the same line colour. "
    "Make it the deluxe edition of that very card: the emblem larger and more finely drawn, standing in the middle of a calm ornamental composition built only from the signs of this age. "
    "Layout: no frame, no border lines and no corner stars; the design runs off all four edges. The picture will later be cropped at the left and at the right by about one tenth, so keep everything important inside the middle four fifths of the width. "
    "The centre of the emblem sits a little above the middle of the picture, at about 45 percent of the height from the top. "
    "The lowest quarter of the picture is quiet and darker, with only low simple shapes, because a title will be printed over it later; do not draw any title, letters or numerals anywhere. The top sixth is quiet as well. "
    "This is an emblem, flat and frontal like the back of a tarot card: no scene, no landscape view, no people, no faces, no creatures, no table, no hands, no shadow. "
    "The second attached picture is the approved style sample of this series. If there is a third attached picture, it is the main painting of this age: take its palette, not its composition and not its figures. "
)
BB_0 = BB_COMMON + (
    "This is the card of the age before the first dawn. Ground: deep indigo and slate blue, with a few large pale cut-paper wave shapes drifting across it as on the small card. Line work: silver white. "
    "The whole design is mirror-symmetrical about the vertical centre line. "
    "Emblem: one small warm flame in the centre, the only warm colour in the picture, inside the ring of seven small four-pointed stars. Around the ring run two thin concentric circles with small tick marks, like a star dial. "
    "The pair of stag antlers that cradles the ring is far larger here: the two antlers spring from one point below the flame and rise outward and upward like a great silver crown, tine after tine, up to the top sixth of the picture, "
    "with a few tiny stars hanging between the tines. Below the point where the antlers meet, three thin curved lines fan downward like ripples and fade into the dark."
)
BB_1 = BB_COMMON + (
    "This is the card of the age of the long war. Ground: iron grey above, turning to dark blood red in the lower third, as on the small card. Line work: bone white. "
    "The whole design is mirror-symmetrical about the vertical centre line. "
    "Emblem: the white battlemented tower, taller and finer than on the small card, with a small arched gate; on its top the warm beacon flame, the only warm colour in the picture; above the flame the plain crown broken in two, its two halves floating a little apart inside one thin circle, with three or four tiny sparks rising between them. "
    "Behind the tower the two crossed spears become a fan of seven plain spears. From both sides of the tower a low battlemented wall runs out level to the left and to the right and off the edges, like two outstretched arms. "
    "Below the wall, in the red, a row of small plain swords stands planted point-down, growing fainter and smaller toward the bottom."
)
BB_2 = BB_COMMON + (
    "This is the card of the age of the two kings. As on the small card, the ground is cut in two by one clean diagonal line running from the lower left to the upper right: obsidian black on the upper left side, white stone on the lower right side. Line work: pale gold. "
    "The design is balanced like a pair of scales: whatever the dark side has in black, the light side has in white. "
    "Emblem: the plain longsword standing upright exactly on the vertical centre line, larger and finer than on the small card, its point at the bottom; at its foot one small warm flame, the only warm colour in the picture. "
    "Beside the sword one standing stone on each side, a black one on the dark side and a white one on the light side; behind each of them three more standing stones step away outward and get smaller, so that the stones form a half ring around the sword. "
    "Around the upper half of the sword one thin gold circle, half of it lying on the black and half on the white. On the dark side a few thin lines of fine grey ash fall straight down; on the light side a few thin pale rays rise."
)
BB_3 = BB_COMMON + (
    "This is the card of the age of the great labyrinth. Ground: deep blue and indigo. Line work: gold. "
    "The whole design is mirror-symmetrical about the vertical centre line. "
    "Emblem: the round shaft seen from straight above, larger than on the small card: seven concentric rings of small arcaded galleries and stairs winding inward, with the rope hanging from the top edge of the picture straight down to the centre, "
    "and at the very centre the small warm lamp, the only warm colour in the picture. "
    "Outside the outermost ring more rings go on as thin gold arcs that run off the left and right edges like ripples, with a few tiny lamps on them drawn as plain gold dots. "
    "On the centre line, above and below the shaft, one small four-pointed gold star."
)
# 大幅牌背第二稿（11-12）：用户说“大卡背可以比小卡背精美亿点”。当中一扇拱顶的花窗，窗里是徽记和一层压一层的色片，窗外满铺暗纹和金属线的花饰，四枚小圆章。
STYLE_BB2 = (
    " Drawing manner: the same hand as the attached small card back: flat cut-paper colour shapes with thin lighter echo lines along their edges, soft inner gradients only, a fine paper grain. "
    "But exquisitely ornate: intricate, precise and jewel-like, with a clear order of importance (the window and its emblem first, the four medallions second, the ground ornament last). "
    "Crisp clean edges; the metallic lines look like foil stamped on matte paper. No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D."
)
BB2_COMMON = (
    "Draw one tall 2:3 portrait picture: the grand full-art back of a fortune-telling card from a luxury deck, seen perfectly flat from the front and filling the whole picture from edge to edge. "
    "It must look precious and exquisitely made, a hundred times richer and finer than the small card. "
    "The first attached picture is the approved small card back of this age. Keep its emblem, its ground colours and its line colour, and build this grand edition around that same emblem. "
    "Composition: "
    "(1) In the upper middle stands a tall ornate window with an arched top, about three fifths of the picture wide. Its top, crowned by a small crest, is at about 12 percent of the picture height from the top; its foot, ending in a small hanging pendant, is at about 70 percent. "
    "The window is drawn with one bold dark outline and two or three fine metallic lines running inside it. Inside the window stands the emblem, large and finely drawn, its centre at about 41 percent of the picture height, "
    "with a halo of thin concentric rings, small tick marks and fine rays behind it. "
    "(2) Inside the window, around the emblem, layered decorative shapes of this age fill all the space: bands of flat colour overlapping like cut paper, each edged with a thin lighter line, in three or four close shades, so that the window glows like enamel or stained glass. "
    "(3) Outside the window the ground is covered from edge to edge with a fine tone-on-tone pattern of this age and with delicate line ornament in the metallic line colour: slender curling stems, small four-pointed stars, tiny beads and dots, thin arcs. "
    "The ornament is richest close to the window and thins out toward the edges, and it runs off all four edges: no outer border line, because the picture will later be cropped at the left and right by about one tenth. "
    "(4) Four small round medallions sit around the window, two beside its arch and two beside its foot, each holding one small sign of this age as a plain silhouette. "
    "The lowest quarter of the picture, below the window, is darker and calmer, only the fine ground pattern, because a title will be printed there later; do not draw any title, letters, numerals or writing anywhere. "
    "One small warm flame is the only warm colour in the whole picture; everything else stays in the cool palette of this age. "
    "This is an ornamental emblem, flat and frontal: no scene, no landscape view, no people, no faces, no hands, no table, no cast shadows. "
)
BB2_0 = BB2_COMMON + (
    "This is the card of the age before the first dawn. Ground: deep indigo and slate blue. Metallic line colour: silver white. The whole design is mirror-symmetrical about the vertical centre line. "
    "Emblem: the small warm flame inside the ring of seven four-pointed stars, cradled by the pair of great silver stag antlers, which rise and branch up into the arch of the window like a crown. "
    "Layered shapes inside the window: long pale wave shapes like night wind and drifting snow, and a field of tiny stars. Crest on the arch: one seven-pointed star. Pendant at the foot: a small drop shaped like a flame, in silver outline only. "
    "Ground pattern outside the window: a star chart of thin circles, dotted lines and tiny stars. "
    "The four medallions: a stag's head with antlers, a whale, a mammoth, a winged Western wyrm, each a plain pale silhouette."
)
BB2_1 = BB2_COMMON + (
    "This is the card of the age of the long war. Ground: iron grey above, turning to dark blood red in the lower third. Metallic line colour: bone white. The whole design is mirror-symmetrical about the vertical centre line. "
    "Emblem: the white battlemented tower with its arched gate; on its top the warm beacon flame; above the flame the plain crown broken in two inside one thin circle; behind the tower a fan of seven plain spears. "
    "From both sides of the tower a battlemented wall runs out level to the frame of the window. "
    "Layered shapes inside the window: above the wall, tall pennon and blade shapes in close greys rising like smoke; below the wall, in dark red, a field of small swords planted point-down. "
    "Crest on the arch: a plain round shield. Pendant at the foot: a small sword, point down. "
    "Ground pattern outside the window: fine courses of masonry in the grey, a faint lattice of crossed spears in the red. "
    "The four medallions: a round shield, a drawn bow with its arrow, a curved war horn, a smith's hammer, each a plain bone-white silhouette."
)
BB2_2 = BB2_COMMON + (
    "This is the card of the age of the two kings. Metallic line colour: pale gold. "
    "The whole picture, window and ground alike, is cut in two by one clean diagonal line running from the lower left to the upper right: obsidian black and dark slate on the upper left side, white stone and pale grey on the lower right side. "
    "The shapes are mirror-symmetrical about the vertical centre line; only the colours change sides across the diagonal, like night and day. "
    "Emblem: the plain longsword standing upright on the centre line, point down, with one small warm flame at its foot; one standing stone on each side of it, black on the dark side and white on the light side, and behind them a half ring of smaller standing stones; one thin gold ring around the hilt. "
    "Layered shapes inside the window: on the dark side long strands falling like ash and flowing hair, on the light side long strands rising like rays and cloak folds, all pure abstract shapes with no figures. "
    "Crest on the arch: a small plain crown split into a dark half and a light half. Pendant at the foot: a small plain ring. "
    "Ground pattern outside the window: on the dark side thin falling lines and tiny stars, on the light side thin rays and a grain of small dots. "
    "The four medallions: a raven, a chess king, a standing stone with one carved line, a rising half sun."
)
BB2_3 = BB2_COMMON + (
    "This is the card of the age of the great labyrinth. Ground: deep blue and indigo. Metallic line colour: gold. The whole design is mirror-symmetrical about the vertical centre line. "
    "Emblem: the round shaft seen from straight above, filling the width of the window: seven concentric rings of small arcaded galleries and stairs winding inward, the rope hanging from the crest of the arch straight down to the centre, and at the very centre the small warm lamp. "
    "Layered shapes inside the window, above and below the shaft: tiers of small arches and flights of stairs stacked like cut paper in close blues. "
    "Crest on the arch: a small compass star. Pendant at the foot: a small key. "
    "Ground pattern outside the window: thin concentric ripple arcs crossed by a faint map grid, with a few tiny lamps as plain gold dots. "
    "The four medallions: a key, a coiled rope, an unlit lantern in outline, a compass rose."
)
# 第三稿：第二稿带参考的那一组框更厚更华丽，可花饰一直铺到图高的八成多，跟页面的标题打架。窗脚收到六成四，七成二以下只留暗纹。
def bb3(p):
    a1 = "its foot, ending in a small hanging pendant, is at about 70 percent. "
    a2 = "The lowest quarter of the picture, below the window, is darker and calmer, only the fine ground pattern, because a title will be printed there later; "
    assert a1 in p and a2 in p
    p = p.replace(a1, "its foot is at about 64 percent, and the small pendant hanging from it, together with every scroll, leaf and stem around the foot, ends above 72 percent of the picture height. ")
    p = p.replace(a2, "Everything below 74 percent of the picture height is darker and calm: only the faint ground pattern, with no scrolls, no leaves, no stems, no medallions and no large stars there, because a title will be printed there later; ")
    return p + (" The frame of the window is bold and sculpted, with rich scrollwork at the crest, at the four medallions and at the foot. "
                "The pendant is drawn in the metallic line colour only; there is no second flame anywhere.")


BB2_REF = (
    " The last attached picture is a page from another game with three ornate arch-topped cards on it. It is there only to show how rich, dense and finely made such cards can be, and the idea of an arch-topped ornate frame with a crest and a pendant. "
    "Do not copy its colours, its symbols, its characters or its angular geometric style."
)
# 牌桌的桌面：从正上方看的一张圆桌，页面里把它放倒成斜着看。只要大块的颜色和层次，细线页面里另画（放大了才不糊）。
TABLE = (
    "Draw one square 1:1 picture: the top of a great round stone table seen from exactly above, a flat top-down view with no perspective. "
    "The round table fills the picture and touches all four edges; the four corners outside the circle are pure black. "
    "The table is dark slate-blue stone. It is built of broad concentric bands like layers of cut paper, each band a slightly different deep blue-grey, with a thin paler echo line where two bands meet. "
    "In the very centre lies one large closed eye carved into the stone, glowing softly with a still blue-green light from within; the glow spreads a little over the innermost band. "
    "On the two outer bands a few very faint feather shapes are carved, like the tips of great wings, all pointing toward the centre. "
    "Keep it calm, dark and empty: no objects on the table, no cards, no candles, no cloth, no people. The first attached picture is the approved style sample of this series."
)


def hand3_refs():
    return [LOCK, os.path.join(OUT, "t1.png"), os.path.join(SAMPLE, "h2_open.png")]


# 第二回：h3_open 对了，拿它当这只手的定稿样。h3_press 小臂上多了两道红边（是参考图里旧袖子带进来的），照它的姿势重画、小臂画素的；
# h3_hold 两指张得太开（像比“二”），改成两指几乎并着、中间只留一道窄缝，夹牌才像。
STYLE_HANDS3B = (
    " Drawing manner: the first attached picture is the approved style sample of this series; the second attached picture is the approved drawing of this very arm, so match its colours, its line and its finish exactly: "
    "flat cut-paper colour shapes, thin lighter echo lines along the edges, soft inner gradients only, a fine paper grain, crisp clean outlines against the transparent background, "
    "no realistic lighting, no heavy rendering, no 3D. Keep it simple and clean."
)
HANDS3B_REF = (
    "The second attached picture is the approved design of this arm: a long opera glove of sheer black silk, smoky charcoal-black, a little lighter and warmer over the knuckles and the back of the hand where skin shows faintly through, "
    "a thin lighter echo line along its edges, and one long almond-shaped deep crimson fingernail on each fingertip. "
    "The forearm is completely plain: one smooth dark glove from the wrist to the edge of the picture, with no red bands, no trim, no piping, no ribbons, no seams, no folds of cloth and no pattern. "
    "The only red in the whole picture is the fingernails. There is no sleeve, no cuff, no cloak, no bracelet and no ring. "
)
H3_PRESS2 = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS3B_REF +
    "The third attached picture shows the pose, the size and the placement to keep: one forearm and hand reaching straight down from the top edge, the back of the hand toward the viewer, "
    "the index finger and the middle finger extended straight down side by side with a clear narrow empty gap between them along their whole length, from the knuckles to the nails, "
    "the ring finger and the little finger curled into two small rounded knuckles beside them, the thumb out of sight. "
    "Redraw that third picture with the plain forearm of the second picture: remove the wavy red bands from the forearm and keep everything else as it is. "
    "Count what is visible: two long extended fingers and two curled knuckles, nothing more." + HANDS3_END
)
H3_HOLD2 = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS3B_REF +
    "The third attached picture shows the hand to redraw, its size and its placement: one forearm and hand rising straight up from the bottom edge, the back of the hand toward the viewer, "
    "the index finger and the middle finger extended upward, the ring finger and the little finger curled into two small rounded knuckles beside them, the thumb folded across the palm. "
    "Change only one thing: bring the two extended fingers together. They now point straight up, almost parallel, side by side, both the same length, "
    "separated only by a clear narrow empty gap about a third of a finger wide that runs along their whole length, from the knuckles to the nails. They do not touch, do not cross and do not spread into a wide V. "
    "It is the elegant gesture of holding up one card pinched between two fingertips, but there is no card in the picture: the space between and above the fingers is empty. "
    "Count what is visible: two long extended fingers and two curled knuckles, nothing more. Keep the forearm plain and smooth, without the twisting fold lines." + HANDS3_END
)


# 第三回（11-11）：翻牌改成整只手夹着牌绕手腕转过来，要一张手心那一面的图。轮廓照手背那张左右镜像的来，转到侧面的时候两张图换着用。
H3_PALM = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS3B_REF +
    "The third attached picture shows this very hand from the BACK, already mirrored left to right: it gives the outline, the size and the placement to keep. "
    "Draw the same hand, in the same pose and the same outline, but seen from the other side: the PALM faces the viewer, as if the wrist had been turned around. "
    "The forearm rises straight up from the bottom edge. The index finger and the middle finger are extended straight up, almost parallel, side by side, both the same length, "
    "separated by a clear narrow empty gap that runs along their whole length. From this side we see their soft inner pads, not their nails: "
    "only the very tips of their long crimson nails peek out above the two fingertips as small red points. "
    "The ring finger and the little finger are curled down onto the palm, on the LEFT side of the two extended fingers, and we see their folded last joints with their crimson nails facing the viewer. "
    "The thumb lies folded across the lower palm, pointing left, its crimson nail visible. The palm is the same smoky sheer black silk, a little lighter and warmer in the hollow of the palm, with two or three thin crease lines. "
    "Count what is visible: two long extended fingers seen from their pad side, two curled fingers with nails, one thumb. Keep the forearm plain and smooth." + HANDS3_END
)


# 第四回（11-11）：用户看了第九版：不要把牌夹在两指中间，要像参考片那样把牌拿起来，食指中指配合拇指。
# 参考片里：食指、中指并着搭在牌背上（在牌的前面），拇指从另一面抵着（在牌的后面），无名指小指蜷着。
# 所以要一张带拇指的手：拇指在一旁伸着，跟食指之间留一道缝（页面里把拇指单拆一层放到牌后面）。
H4_TAKE = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS3B_REF +
    "The third attached picture shows this very hand in an earlier pose; keep its size, its placement, its forearm and its manner of drawing exactly: "
    "one forearm and hand rising straight up from the bottom edge, the back of the hand toward the viewer. It is a right hand. "
    "Change the pose to the classic way of holding up one playing card between the thumb and two fingers, but there is no card in the picture: "
    "the index finger and the middle finger are extended straight up, almost parallel, side by side, both the same length, separated only by a clear narrow empty gap about a quarter of a finger wide that runs from the knuckles to the nails; "
    "the thumb is now clearly visible on the LEFT side of the hand: long and slender, extended upward and slightly outward, lying alongside the index finger but separated from it by a clear empty transparent gap along its whole free length, "
    "from the web of the thumb up to its nail. The tip of the thumb reaches up to about the middle of the index finger, and its long crimson almond nail is visible. "
    "The ring finger and the little finger stay curled into two small rounded knuckles on the RIGHT side of the hand. "
    "Count what is visible: one thumb on the left, two long extended fingers in the middle, two curled knuckles on the right, nothing more. "
    "The space above and between the fingers is empty. Keep the forearm plain and smooth, without twisting fold lines." + HANDS3_END
)


# 第五回（11-11）：用户看了第十一版：“五根手指都要调整，对整个手进行优化”。h4_take 的毛病：食指中指两根一样长、笔直平行，像两根棍子；
# 拇指跟手指一样细长、贴着食指平行着，像第三根手指；无名指小指是两团圆疙瘩，看不出是手指；手背没有结构。
# 这一回照真手写：两指不一样长、带关节、略弯；拇指短而厚、从掌侧靠手腕的地方斜着出来，跟食指之间是一个敞开的 V；
# 无名指小指画成松松收拢的两根手指（看得出指节和折过去的那一道）。拇指要够长：扣过来以后指尖要够得到牌角（食指中节那么高）。
H5_TAKE = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS3B_REF +
    "The third attached picture is an earlier drawing of this hand that came out too stiff, like a mannequin: take from it ONLY the size of the hand, its placement on the page "
    "and the plain forearm rising straight up from the bottom edge. Redraw the whole hand from the wrist upward as a real, graceful woman's hand, the way a skilled fashion illustrator "
    "who knows anatomy would draw it. It is a right hand seen from the back, the fingers pointing up. "
    "The gesture: she is holding up a single playing card between her thumb and her first two fingers, but the card itself is NOT in the picture. "
    "INDEX FINGER and MIDDLE FINGER: long, slender and tapering toward the tips, extended upward close together as one elegant pair with only a narrow empty gap between them. "
    "They must not look like two identical rods: the middle finger is clearly a little longer than the index finger; each finger shows its three segments, with slightly fuller knuckle joints "
    "and a faint lighter touch on each joint; and each has a very slight natural bow and lean, as relaxed extended fingers do. "
    "RING FINGER and LITTLE FINGER: folded down toward the palm in a loose, relaxed curl. Draw them as two clearly separate folded fingers, not as round lumps: "
    "from each knuckle the first segment rises a short way, then the finger bends over and tucks its tip in toward the palm, with a small curved crease line at the bend; "
    "the ring finger's bend sits higher, the little finger is smaller and its bend sits lower and outermost. Their nails are tucked out of sight. "
    "THUMB: a real thumb on the LEFT side of the hand, a little broader than the fingers, growing out of the side of the palm low down near the wrist from its fleshy base. "
    "It points upward and outward, leaning away from the index finger at about thirty degrees, with a slight bend at its middle joint. It is a long, elegant thumb: "
    "its tip reaches up to about halfway along the lowest segment of the index finger. Its crimson almond nail is seen at a three-quarter angle. "
    "Between the thumb and the index finger there is a wide, completely empty V-shaped opening (transparent background), with the smooth curved web of the glove at the bottom of the V. "
    "BACK OF THE HAND: narrow and elegant, the four knuckles in a gentle arc that is highest at the middle finger, two or three faint tendon lines fanning from the slim wrist toward the knuckles. "
    "Count what is visible: one thumb on the left leaning outward, two long extended fingers with crimson nails, two folded fingers on the right with no nails showing. Exactly five fingers, no more. "
    "The space above and between the fingers is empty. Keep the forearm plain and smooth, without twisting fold lines." + HANDS3_END
)


# 第六回（11-11）：h5_take 的毛病是正对着的手背又长又宽、手腕粗、两根手指当中有缝、拇指朝外叉着，不好看，也像筷子。
# 照参考片逐帧量出来的比例重画，量的数在 底稿/门面/小样_牌桌/参考_黑天鹅抽牌_逐帧.md，姿势图是 make_h6_pose.py 画的灰色色块（不是照片也不是别人的画）。
H6_TAKE = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. " + HANDS3B_REF +
    "The third attached picture is a plain grey block diagram that I drew myself. It is NOT a style reference: take from it only the pose, the proportions, the size and the placement of every part, "
    "and follow those closely. Redraw it as the hand of an elegant woman in the approved glove design, the way a top anime key animator draws a beautiful gloved hand: "
    "big clear simple shapes, smooth flowing contour lines, long tapering fingers, a small back of the hand, a narrow wrist. No knobby joints, no bulging tendons, no wrinkles. "
    "It is a right hand seen from the back, raised, the fingers pointing up. The wrist is bent back a little, so the back of the hand looks short and the fingers look long. "
    "The gesture: she holds up a single playing card between her thumb and her first two fingers, but the card itself is NOT in the picture. "
    "INDEX FINGER and MIDDLE FINGER: both extended straight up and leaning about fifteen degrees to the right, pressed together side by side so that they touch along their whole length, "
    "with no gap between them, only one thin contour line where they meet. They are very long, more than twice as long as the visible back of the hand, slender, "
    "and they taper smoothly to fine pointed tips, each ending in a long almond-shaped deep crimson nail. The middle finger, on the right, is a little longer and reaches higher. "
    "RING FINGER and LITTLE FINGER: curled down into the palm. From the back they show as two smooth rounded forms on the right side of the hand, the first segment of each finger ending in a softly bent knuckle: "
    "the ring finger's form is taller and sits right beside the middle finger, the little finger's form is smaller, lower and outermost. Their nails are tucked out of sight. "
    "THUMB: on the left side, lying close alongside the index finger and pointing up, almost parallel to it. It is clearly shorter: its tip reaches a little less than halfway up the index finger. "
    "It is slim, tapers to a pointed tip and has its own crimson almond nail. Between the thumb and the index finger there is a narrow sliver of empty transparent background all along the thumb's inner edge, "
    "from its tip down to the web of the hand, so that the thumb is clearly a separate finger. "
    "BACK OF THE HAND: short and neat, widest at the row of knuckles, narrowing quickly to the wrist. WRIST: slim, only about half as wide as the row of knuckles. "
    "FOREARM: plain, slim and smooth, running straight down to the bottom edge of the picture, vertical. "
    "The whole hand is a little larger than in the diagram if needed, but keep the same proportions between its parts. Exactly five fingers: one thumb on the left, two long extended fingers with crimson nails, "
    "two curled fingers on the right with no nails showing. The space above and around the fingers is empty." + HANDS3_END
)


# 第七回（11-11）：见上面的话。只拿 h3_open 当手套的颜色和料子，不拿它的手当样子；不给姿势图。
H7_TAKE = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. "
    "Subject: a young woman's right hand and forearm, raised into the picture from the bottom edge and seen from the BACK of the hand, holding up one card. "
    "Draw the hand from life, with the correct anatomy of a real human hand. This is the most important thing in the picture: a real wrist; the back of the hand with its row of four knuckles; "
    "every finger with its three segments and its two joints in natural proportion, natural thickness and natural taper; a real thumb base. "
    "It must look like the hand of a living, elegant woman with long slender fingers. Not tubes, not petals, not a mitten, not a paper cut-out. "
    "The pose is the classic way a fortune-teller presents a tarot card: the card stands upright above the hand. The index finger and the middle finger are extended upward, close together side by side, "
    "lying flat against the FRONT of the card, so we see their backs and their nails; they cover the lower third of the card, near its vertical centre line. "
    "The thumb is BEHIND the card, pressing the card against those two fingers, so the thumb itself is hidden by the card; only the base of the thumb may show at the left side of the hand below the card. "
    "The ring finger and the little finger are relaxed and curled down toward the palm, below the bottom edge of the card; from the back we see their first segments and their bent knuckles, drawn as real folded fingers. "
    "The wrist is bent back slightly. The forearm runs straight down to the bottom edge of the picture, vertical and centred. The two extended fingers lean about fifteen degrees to the right of the forearm, "
    "and the card leans a few degrees further to the right than the fingers, so that forearm, fingers and card make one gentle arc. "
    "The glove: the first attached picture is the approved design of this arm. Take from it ONLY the colours and the material, not the drawing of its hand: a long opera glove of sheer black silk, smoky charcoal-black, "
    "a little lighter and warmer over the knuckles and the back of the hand where skin shows faintly through, and one long almond-shaped deep crimson fingernail on each fingertip. "
    "The forearm is plain: one smooth dark glove from the wrist to the bottom edge, with no bands, no trim, no seams, no folds and no pattern. No sleeve, no cuff, no bracelet, no ring, no jewellery. "
    "THE CARD is only a placeholder that will be cut out afterwards: draw it as a completely flat, featureless rectangle of pure solid bright green, exactly the colour #00FF00, with sharp straight edges and square corners, "
    "two units wide and three units tall, with no border, no outline, no shading, no highlight, no pattern and no thickness. Its height is a little less than the length of the hand from wrist to fingertips. "
    "Nothing of the hand may be tinted green, and green must not appear anywhere else in the picture. "
    "Size and placement: the top edge of the card is near the top of the picture; the fingertips are at about thirty percent of the picture height from the top; the wrist is at about sixty percent; "
    "the forearm fills the rest, down to the bottom edge. "
    "Nothing else: no table, no body, no face, no hair, no shadow, no background."
)
STYLE_HANDS7 = (
    " Drawing manner: the quality of a key frame from a top anime film. Clean, confident contour lines; flat base tones; one soft shadow tone and a thin lighter edge that explain the forms "
    "(the roundness of each finger, the knuckles, the fold of the curled fingers, the turn of the wrist); a fine paper grain like the first attached picture. "
    "Crisp clean outlines against the transparent background. No photographic rendering, no heavy texture, no glow."
)


# 第八回（11-11）：h7 三张像真人的手了，用户接着说：“整体光滑一些，别太骨感,整体的黑丝和光影也可以大致参考黑天鹅的”。
# 手背不画筋、指节只留柔的起伏、手腕不画褶；手套压得更黑带冷紫，受光的一侧是大块柔的蓝紫亮面加一道亮边（明暗的样子给一小块参考片的手，只取料子和光，不取首饰）。
# 牌的位置改成参考片那样：牌的下边压在两根手指的中段，指尖到牌高的三分之一；拇指整个藏在牌和手后面不画。这样抠掉牌以后手上没有被牌边切出来的平头。
PV_LIGHT = os.path.join(HERE, "..", "..", "..", "语料", "门面参考_11-10", "pv_hand_light.png")
H8_TAKE = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. "
    "Subject: a young woman's right hand and forearm, raised into the picture from the bottom edge and seen from the BACK of the hand, holding up one card. "
    "Draw the hand with the correct anatomy of a real human hand: a real wrist, the back of the hand, four fingers each with its three segments in natural proportion and natural taper. "
    "But it is a SMOOTH, soft, youthful hand inside a silk glove: no bony knuckles, no tendons or cords on the back of the hand, no veins, no wrinkles at the wrist. "
    "The knuckles are only gentle rounded forms; each finger joint is shown by a soft change of plane, at most by one tiny crease. Long, slender, gracefully tapering fingers with a soft fullness. Elegant, never skeletal. "
    "The pose is the classic way a fortune-teller presents a tarot card: the card stands upright above the hand. The index finger and the middle finger are extended upward, close together side by side, "
    "lying flat against the FRONT of the card, so we see their backs and their nails. ONLY the upper half of these two fingers lies on the card: the bottom edge of the card crosses them about halfway along their length, "
    "and their tips reach about one third of the way up the card, near its vertical centre line. Below the bottom edge of the card the lower half of the two fingers, the knuckles and the whole back of the hand are fully visible. "
    "The thumb is completely hidden behind the card and behind the hand: do not draw any part of the thumb. "
    "The ring finger and the little finger are relaxed and curled down toward the palm, well below the card; from the back they are two soft folded fingers, and the tips of their nails may just show. "
    "No part of the hand is cut off by the edge of the card: the card is simply behind the two extended fingers. "
    "The wrist is bent back slightly. The forearm runs straight down to the bottom edge of the picture, vertical and centred. The two extended fingers lean about fifteen degrees to the right of the forearm, "
    "and the card leans a few degrees further to the right than the fingers, so that forearm, fingers and card make one gentle arc. "
    "THE GLOVE AND THE LIGHT: the first attached picture shows the look we want for the glove. Take from it ONLY the material and the light: a glove of black silk, deep violet-black; "
    "broad smooth planes of soft lavender-blue light on the side that faces the light, a thin pale rim of light along the lit contour, deep shadow everywhere else; clean cel shading in two or three tones with soft edges. "
    "Do NOT copy its ring, its jewel, its chain or its cuff: our glove is completely plain, one smooth long opera glove from the fingertips down to the bottom edge of the picture, with no ring, no jewel, no chain, no cuff, no seam and no pattern. "
    "Our glove has one more thing: a long almond-shaped deep crimson fingernail on every fingertip, glossy, clearly visible on the two extended fingers. The crimson nails are the only red in the picture. "
    "THE CARD is only a placeholder that will be cut out afterwards: draw it as a completely flat, featureless rectangle of pure solid bright green, exactly the colour #00FF00, with sharp straight edges and square corners, "
    "two units wide and three units tall, with no border, no outline, no shading, no highlight, no pattern and no thickness, and with no shadow cast on it by the fingers. "
    "Its height is a little less than the length of the hand from wrist to fingertips. Nothing of the hand may be tinted green, and green must not appear anywhere else in the picture. "
    "Size and placement: the top edge of the card is near the top of the picture; the fingertips are at about twenty-six percent of the picture height from the top; the bottom edge of the card at about thirty-eight percent; "
    "the knuckles at about fifty percent; the wrist at about sixty-six percent; the forearm fills the rest, down to the bottom edge. "
    "Nothing else: no table, no body, no face, no hair, no background."
)
STYLE_HANDS8 = (
    " Drawing manner: a key frame from a top anime film. Clean, confident contour lines; smooth cel shading in two or three tones with soft gradients; a faint fine grain. "
    "Crisp clean outlines against the transparent background. No photographic rendering, no heavy texture, no glow, no sparkles."
)


# 发牌的那只手（11-11）：照第八回的画法，跟 h8_take_b 是同一条手臂。手指朝上画，用的时候转半圈。
H8_OPEN = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. "
    "Subject: a young woman's right hand and forearm, rising into the picture from the bottom edge and seen from the BACK of the hand. "
    "It is the same arm as in the first attached picture, now with the hand open. "
    "Draw the hand with the correct anatomy of a real human hand: a real wrist, the back of the hand, one thumb and four fingers, each finger with its three segments in natural proportion and natural taper. Exactly five digits. "
    "But it is a SMOOTH, soft, youthful hand inside a silk glove: no bony knuckles, no tendons or cords on the back of the hand, no veins, no wrinkles at the wrist. "
    "The knuckles are only gentle rounded forms; each finger joint is shown by a soft change of plane, at most by one tiny crease. Long, slender, gracefully tapering fingers with a soft fullness. Elegant, never skeletal, never claw-like. "
    "The pose: the hand is open, flat and relaxed, its palm turned away from us, like a hand gliding just above a table top and seen from straight above. "
    "The four fingers point upward, long and gently fanned: between each pair of neighbouring fingers there is a narrow clear gap of empty background along their whole length, from the knuckle to the nail; "
    "no finger touches or overlaps another. The fingers are almost straight, with only a slight natural curve, not stiff. The middle finger is the longest. "
    "The thumb is on the LEFT side of the hand, relaxed and extended, angled out about forty degrees away from the index finger and clearly separated from it by empty background; we see it from the back with its nail. "
    "The wrist is straight. The forearm runs straight down to the bottom edge of the picture, vertical and centred, and is cut off cleanly by the bottom edge. "
    "THE GLOVE AND THE LIGHT: exactly as in the first attached picture, which is the approved drawing of this same arm: a plain long opera glove of black silk, deep violet-black; "
    "broad smooth planes of soft lavender-blue light on the side that faces the light, a thin pale rim of light along the lit contour, deep shadow everywhere else; clean cel shading in two or three tones with soft edges. "
    "The light comes from the same side as in the first attached picture. The second attached picture is only a further reference for this silk and this light: do not copy its ring, its jewel, its chain or its cuff. "
    "Our glove is completely plain from the fingertips down to the bottom edge of the picture: no ring, no jewel, no chain, no cuff, no seam and no pattern. "
    "One long almond-shaped deep crimson fingernail on every one of the five fingertips, glossy, the same nails as in the first attached picture. The crimson nails are the only red in the picture. "
    "Size and placement: the tip of the middle finger is at about ten percent of the picture height from the top; the knuckles at about thirty-six percent; the wrist at about fifty percent; "
    "the forearm fills the rest, down to the bottom edge. The hand is centred horizontally, and the tip of the thumb stays well inside the left edge of the picture. "
    "Nothing else: no card, no table, no body, no face, no hair, no cast shadow, no background."
)


# 第九回（11-12）：两只手照若娜瓦实际的手重画，姿势不动只换手套。她的手的截图是用户给的，放在 语料/门面参考_11-10/（不进库），只当手套的参考。
RONOVA_HAND = [os.path.join(HERE, "..", "..", "..", "语料", "门面参考_11-10", n) for n in ("若娜瓦手_3_捏.png", "若娜瓦手_4_爪.png", "若娜瓦手_2_胸前_手.png")]
GLOVE9 = (
    "THE NEW GLOVE. The other attached pictures are screenshots of this character's real hand; they are attached only to show her glove. Paint that glove: "
    "(1) Colour and material: a tight, matte black glove with a faint warm dark-brown tint, like soft suede. It is black: not violet, not blue, and not glossy. "
    "(2) Claws: she has no fingernails, and nothing on the hand is red. Instead the tip of every finger of the glove tapers smoothly into a long, slender, needle-sharp claw of the same black, very slightly curved, "
    "about as long as the last segment of the finger. The claw is the fingertip of the glove itself, not a nail set on top of it. "
    "(3) Markings: three long, thin, pale silver-white lines run lengthwise, side by side, along the back of the hand and the wrist and on down the forearm, slim and elegant, as in the screenshots. "
    "Nothing else decorates the glove: no ring, no jewel, no cuff, no seam. "
    "(4) Rendering: clean toon shading as in the screenshots: thin crisp black outlines, a thin black crease line at each finger joint, one flat dark base tone. "
    "So that a black hand can be read against a black background, add a broad soft plane of muted cool grey light on the side that faces the light and a thin pale rim of light along that contour, "
    "on the same side as in the first picture. Smooth and elegant: no tendons, no veins, no wrinkles. "
)
H9_TAKE = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. "
    "The first attached picture is our approved drawing: a young woman's right hand and forearm seen from the back, holding up a card; the card is a flat pure-green placeholder. "
    "Redraw this picture and keep everything about it the same: the pose, the anatomy and the proportions of the hand, the position and the angle of every finger, the forearm, the framing and the size, "
    "the transparent background, and the flat pure green card (exactly #00FF00) just where it is, with the same shape, size and angle and with no shadow on it. The thumb stays completely hidden. "
    "Change only the glove. " + GLOVE9 +
    "On the two extended fingers the claws continue the line of the fingers upward and lie against the front of the green card. On the two curled fingers the claws point down toward the wrist and may only just show. "
    "Nothing of the hand may be tinted green, and green must not appear anywhere except the card. Nothing else in the picture: no table, no body, no face, no hair, no background."
)
H9_OPEN = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. "
    "The first attached picture is our approved drawing: a young woman's right hand and forearm rising from the bottom edge, seen from the back, the hand open and relaxed, the four fingers gently fanned and the thumb out to the left. "
    "Redraw this picture and keep everything about it the same: the pose, the anatomy and the proportions of the hand, the position and the angle of every finger and of the thumb, "
    "the clear gaps of empty background between the fingers, the forearm, the framing and the size, and the transparent background. "
    "Change only the glove. " + GLOVE9 +
    "All five claws continue the line of their fingers. The claws make the fingers a little longer, but nothing else shifts: the knuckles and the wrist stay where they are, "
    "and the claws simply reach further up (the middle claw may come close to the top edge but must stay inside the picture). "
    "Nothing else in the picture: no card, no table, no body, no face, no hair, no cast shadow, no background."
)


def hand3b_refs(pose):
    return lambda: [LOCK, os.path.join(SAMPLE, "h3_open.png"), os.path.join(SAMPLE, pose + ".png")]


def back_refs(n):
    era = [LOCK, os.path.join(MAIN, "k2.png"), os.path.join(MAIN, "k3b.png"), os.path.join(MAIN, "k4.png")][n]
    return lambda: [LOCK] if n == 0 else [LOCK, era]


def bb_refs(n):
    """大幅牌背的参考：这一纪的小牌背、定稿画风样、这一纪的主画（月银纪的主画就是定稿样）。"""
    era = [None, os.path.join(MAIN, "k2.png"), os.path.join(MAIN, "k3b.png"), os.path.join(MAIN, "k4.png")][n]
    return lambda: [os.path.join(SAMPLE, "b_%d.png" % n), LOCK] + ([era] if era else [])


def bb2_refs(n, rich=False):
    """大幅牌背第二稿的参考：这一纪的小牌背、定稿画风样、这一纪的主画；rich 的把画风样换成用户给的活动页（三张花牌），放最后。"""
    era = [None, os.path.join(MAIN, "k2.png"), os.path.join(MAIN, "k3b.png"), os.path.join(MAIN, "k4.png")][n]
    def f():
        r = [os.path.join(SAMPLE, "b_%d.png" % n)] + ([] if rich else [LOCK]) + ([era] if era else [])
        return r + (ref("画风_02_三张牌的活动页.webp") if rich else [])
    return f


def scene_refs():
    return [LOCK, os.path.join(MAIN, "t1b.png")]


def lock_refs():
    return [LOCK] + ref("画风_03_云里的人.webp", "画风_01_卷浪里的人.png")


def cast_head(key):
    """卡里 1001 那一套立绘的头像，当长相参考。"""
    return os.path.join(HERE, "out", "立绘_v3", key, "head.png")


# 11-12 片头样片（序加第一歌）要的画。词照 底稿/门面/片头_词_第四版.md 第 7 到 15 行，一行或半行一幅，序和收只有一粒火、不用图。
# 月银纪这一处的颜色照词走：头两幅只有火是暖的，诸神落座那一幅坛上各一点暖火，辉塔和万灯两幅一点暖色也没有（世界不再燃烧），
# 灯坠那一幅是冷白的光往下砸、砸到地上才冒出暖的余火。不画月亮（卡里不写月相）。人都很小，神和那个站在万灯中央的人不画脸。
# 希尔妲照第一歌的旅伴条：灰金色的粗辫垂到腰下、辫梢一截红毛线，大两号的狐皮外套，背上桦树皮和柳条编的高筐，筐里一罐火种。
PV = os.path.join(HERE, "out", "门面_片头_11-12")
NO_MOON = " No moon and no crescent anywhere in the sky."
PV1_A = (
    "Redraw the first attached picture, which is the approved plate of this series. Keep its composition, palette, drawing manner, paper grain and every other element exactly as they are: "
    "the small fire in the lower centre with the ring of tiny huddled people in furs, the mammoth, the great stag with a forest of antlers, the whale in a sea of mist, the smoke rising in one long S-curve into a river of stars, the snow hills. "
    "Change only three things. One: replace the long serpentine dragon in the upper left with a heavy Western wyrm drawn in the same pale cut-paper manner, with broad bat-like wings, a thick neck and swept-back horns, no whiskers and no antlers; "
    "on its back it carries a tiny walled town with a few small towers, as if the town were built on the beast. "
    "Two: the woman kneeling by the fire is a girl of fifteen with ash-gold hair in one thick braid that hangs below her waist, the end of the braid tied with a bit of red wool; she wears a fox-fur coat too big for her with a fur-trimmed hood pushed back, "
    "and a tall basket of birch bark and willow on her back; she shelters the flame with both hands. She stays small and simplified. "
    "Three: remove the vine and oak-leaf ornaments in the corners and continue the snow hills and the mist there instead, so that the picture has no border ornament at all."
)
PV1_B = (
    SERIES +
    "Scene: a girl sets out alone into the long night, carrying fire. The lower third of the picture is a wide snow plain crossed by a frozen river; at the left stands a broken old stone bridge of grey arches, with a small fire burning under one arch and a few tiny people standing at the bridge head looking after her. "
    "Right of centre, already far out on the snow, walks the girl, tiny and seen from behind: ash-gold hair in one thick braid down to below her waist, a fox-fur coat too big for her, and on her back a tall basket of birch bark and willow in which a clay pot of embers glows, "
    "a small warm light that is the brightest point in the picture; a thin thread of smoke trails behind her. Her footprints run back to the bridge. "
    "Above her the whole night is filled with enormous shapes drawn as overlapping pale cut-paper silhouettes in cold silver blue and slate, parting before her like waves: a pack of great wolves with long manes turning their heads to watch her, "
    "the back of a mammoth, the antlers of a great stag fading into mist. Far ahead of her on the horizon, in the direction she walks, lies only darkness and one very faint pale line. "
    "Palette: deep indigo, slate blue, silver grey, bone white, and the one warm orange of the embers on her back and the fire under the bridge." + NO_MOON
)
PV1_C = (
    SERIES +
    "Scene: the gods take their seats before the altars. Dawn has come: the sky is pale silver and soft blue-white, the first cold daylight of a young world. "
    "Along a broad river ford in the lower part of the picture stands a long curving row of plain square stone altars, receding in one great S-curve toward the horizon; on every altar burns one tiny warm flame. "
    "Before the nearest altars stand a handful of tiny kings and envoys in cloaks and plain circlets, heads bowed, and a few tiny banners without any emblem. "
    "Behind the altars, filling the sky, enormous calm figures are sitting down, drawn as overlapping pale cut-paper silhouettes in bone white, silver and soft blue: robed giants, men and women, each lowering themselves onto a seat behind an altar, "
    "their long robes and hair flowing down and around the row of altars like waves, with thin lighter echo lines along the edges. Their faces are left blank or turned away; no features are drawn. One holds a sheaf of grain, one a hammer, one a small boat, one a lyre. "
    "They are gentle and grave, not threatening. "
    "Palette: pale silver, bone white, soft slate blue, a little ochre on the ground, and the tiny warm orange altar flames." + NO_MOON
)
PV1_D = (
    SERIES +
    "Scene: mankind lifts its lamps into the high sky. A vast round city lies inside a ring of dark mountains, seen from a height. From the city rise many tall slender towers, thin as candles, hundreds of them, drawn as overlapping pale cut-paper shapes; "
    "each tower carries at its top one point of cold white light with a soft round halo, so that the whole sky above the city is hung with lights like a second field of stars, and the night is pushed back to the edges of the picture. "
    "Above the towers floats an upper city on a great disc of stone, with gardens and colonnades, held up by nothing. In the foreground on a hill a few tiny robed scholars hoist one more lamp into the air with ropes and a tall wooden frame, the lamp just leaving their hands. "
    "The beams of the tower lights sweep down in long curved bands that circle the city like waves, with thin echo lines along their edges; under them the streets lie in soft shadowless brightness. "
    "There is no fire and no warm colour anywhere in this picture: every light is cold white, pale silver or faint blue. "
    "Palette: deep indigo at the edges, slate blue, silver, cold white, a little pale violet." + NO_MOON
)
PV1_E = (
    SERIES +
    "Scene: one man stands at the centre of ten thousand lamps. We look from high above and behind at an immense plaza laid out as rings within rings, like a great seal drawn on the ground; along every ring stand countless slender lamp towers with points of cold white light, "
    "so that the rings of light curve around the centre like waves, drawn as overlapping pale cut-paper bands with thin echo lines. At the exact centre of the rings stands one tiny lone figure in a long plain robe, seen from behind, both arms slightly opened toward the sky; "
    "his head is lost in the glare, and no face is shown. Far around the outermost ring sit the tiny lit tables of a feast and a crowd of tiny people looking toward him. "
    "The sky overhead is perfectly dark and empty, pressed far away by the light, with no stars. "
    "There is no fire and no warm colour anywhere in this picture: everything is cold white, silver and pale blue, very still, very bright, a little too perfect. "
    "Palette: cold white, silver, pale ice blue, deep indigo at the top edge." + NO_MOON
)
PV1_F = (
    SERIES +
    "Scene: in one night all the lamps of heaven fall. The slender lamp towers of a vast city inside a ring of mountains are toppling: they tilt and fall like felled trees, and their lights tear loose and plunge down the sky in long slanting streaks of cold white, "
    "dozens of them, drawn as overlapping pale cut-paper bands that sweep diagonally from the upper right to the lower left. The great floating disc of the upper city is sinking sideways into the mountains. "
    "Where the falling lights strike the ground, small ugly smouldering fires begin, dull orange and ember red, the only warm colour in the picture, with thin threads of smoke. "
    "In the darkness that returns behind the falling lights, enormous shapes are rising, drawn as dark slate silhouettes just a little paler than the night: horned heads, broken crowns, long hands, the reversed shadows of gods. "
    "In the lower foreground a few tiny people run with their arms over their heads, and one tiny figure stands still, holding up a small clay pot of embers. "
    "Palette: near-black indigo, slate, cold white streaks, bone white, and the dull orange of the first smouldering fires." + NO_MOON
)


# 键 → (提示词, 参考图, 画法那一段, 西幻那一段, 写到哪个目录)
JOBS = {
    "pv1_a": (PV1_A, lambda: [LOCK], "", WEST_PLAIN, PV),
    "pv1_b": (PV1_B, lock_refs, STYLE_LOCK, WEST_PLAIN, PV),
    "pv1_c": (PV1_C, lock_refs, STYLE_LOCK, WEST_PLAIN, PV),
    "pv1_d": (PV1_D, lock_refs, STYLE_LOCK, WEST_PLAIN, PV),
    "pv1_e": (PV1_E, lock_refs, STYLE_LOCK, WEST_PLAIN, PV),
    "pv1_f": (PV1_F, lock_refs, STYLE_LOCK, WEST_PLAIN, PV),
    "t1": (T1, lambda: ref("画风_02_三张牌的活动页.webp", "画风_07_三联竖幅.webp", "画风_01_卷浪里的人.png")
           + [head_crop(ref("执政_若娜瓦.webp")[0], os.path.join(REF, "执政_若娜瓦_头.png"), (0.22, 0.03, 0.80, 0.225))], STYLE, WEST, OUT),
    "t2": (T2, lambda: ref("画风_03_云里的人.webp", "画风_01_卷浪里的人.png", "画风_04_水雾和红叶.webp", "画风_05_漩涡和关卡点.webp"), STYLE, WEST, OUT),
    "t3": (T3, lambda: ref("画风_07_三联竖幅.webp", "画风_01_卷浪里的人.png", "画风_03_云里的人.webp", "画风_04_水雾和红叶.webp"), STYLE, WEST, OUT),
    "k2": (K2, lock_refs, STYLE_LOCK, WEST_PLAIN, MAIN),
    "k3": (K3, lock_refs, STYLE_LOCK, WEST_PLAIN, MAIN),
    "k4": (K4, lock_refs, STYLE_LOCK, WEST_PLAIN, MAIN),
    "k3b": (K3B, lambda: [LOCK, os.path.join(MAIN, "k3.png"), cast_head("baltina"), cast_head("thornevia")], "", WEST_PLAIN, MAIN),
    "t1b": (T1B, lambda: [LOCK] + ref("画风_02_三张牌的活动页.webp")
            + [head_crop(ref("执政_若娜瓦.webp")[0], os.path.join(REF, "执政_若娜瓦_头.png"), (0.22, 0.03, 0.80, 0.225))], STYLE_LOCK, WEST_PLAIN, MAIN),
    "h_bg": (H_BG, scene_refs, STYLE_LOCK, WEST_PLAIN, SAMPLE),
    "h_hands": (H_HANDS, scene_refs, STYLE_SPRITE, "", SAMPLE),
    "h_cards": (H_CARDS, scene_refs, STYLE_SPRITE, WEST_PLAIN, SAMPLE),
    "h_eye": (H_EYE, scene_refs, STYLE_SPRITE, "", SAMPLE),
    "h2_open": (H2_OPEN, hand_refs, STYLE_HANDS, "", SAMPLE),
    "h2_press": (H2_PRESS, hand_refs, STYLE_HANDS, "", SAMPLE),
    "h2_hold": (H2_HOLD, hand_refs, STYLE_HANDS, "", SAMPLE),
    "h3_open": (H3_OPEN, hand3_refs, STYLE_HANDS3, "", SAMPLE),
    "h3_press": (H3_PRESS, hand3_refs, STYLE_HANDS3, "", SAMPLE),
    "h3_hold": (H3_HOLD, hand3_refs, STYLE_HANDS3, "", SAMPLE),
    "h3_press2": (H3_PRESS2, hand3b_refs("h3_press"), STYLE_HANDS3B, "", SAMPLE),
    "h3_hold2": (H3_HOLD2, hand3b_refs("h3_hold"), STYLE_HANDS3B, "", SAMPLE),
    "h3_palm": (H3_PALM, hand3b_refs("h3_hold2_mirror"), STYLE_HANDS3B, "", SAMPLE),
    "h3_palm_b": (H3_PALM, hand3b_refs("h3_hold2_mirror"), STYLE_HANDS3B, "", SAMPLE),
    "h4_take": (H4_TAKE, hand3b_refs("h3_hold2"), STYLE_HANDS3B, "", SAMPLE),
    "h4_take_b": (H4_TAKE, hand3b_refs("h3_hold2"), STYLE_HANDS3B, "", SAMPLE),
    "h5_take": (H5_TAKE, hand3b_refs("h4_take"), STYLE_HANDS3B, "", SAMPLE),
    "h5_take_b": (H5_TAKE, hand3b_refs("h4_take"), STYLE_HANDS3B, "", SAMPLE),
    "h5_take_c": (H5_TAKE, hand3b_refs("h4_take"), STYLE_HANDS3B, "", SAMPLE),
    "h6_take": (H6_TAKE, hand3b_refs("h6_pose"), STYLE_HANDS3B, "", SAMPLE),
    "h6_take_b": (H6_TAKE, hand3b_refs("h6_pose"), STYLE_HANDS3B, "", SAMPLE),
    "h6_take_c": (H6_TAKE, hand3b_refs("h6_pose"), STYLE_HANDS3B, "", SAMPLE),
    "h7_take": (H7_TAKE, lambda: [os.path.join(SAMPLE, "h3_open.png")], STYLE_HANDS7, "", SAMPLE),
    "h7_take_b": (H7_TAKE, lambda: [os.path.join(SAMPLE, "h3_open.png")], STYLE_HANDS7, "", SAMPLE),
    "h7_take_c": (H7_TAKE, lambda: [os.path.join(SAMPLE, "h3_open.png")], STYLE_HANDS7, "", SAMPLE),
    "h8_take": (H8_TAKE, lambda: [PV_LIGHT], STYLE_HANDS8, "", SAMPLE),
    "h8_take_b": (H8_TAKE, lambda: [PV_LIGHT], STYLE_HANDS8, "", SAMPLE),
    "h8_take_c": (H8_TAKE, lambda: [PV_LIGHT], STYLE_HANDS8, "", SAMPLE),
    "h8_open": (H8_OPEN, lambda: [os.path.join(SAMPLE, "h8_take_b_cut.png"), PV_LIGHT], STYLE_HANDS8, "", SAMPLE),
    "h8_open_b": (H8_OPEN, lambda: [os.path.join(SAMPLE, "h8_take_b_cut.png"), PV_LIGHT], STYLE_HANDS8, "", SAMPLE),
    "h8_open_c": (H8_OPEN, lambda: [os.path.join(SAMPLE, "h8_take_b_cut.png"), PV_LIGHT], STYLE_HANDS8, "", SAMPLE),
    "h9_take": (H9_TAKE, lambda: [os.path.join(SAMPLE, "h8_take_b.png")] + RONOVA_HAND, STYLE_HANDS8, "", SAMPLE),
    "h9_take_b": (H9_TAKE, lambda: [os.path.join(SAMPLE, "h8_take_b.png")] + RONOVA_HAND, STYLE_HANDS8, "", SAMPLE),
    "h9_take_c": (H9_TAKE, lambda: [os.path.join(SAMPLE, "h8_take_b.png")] + RONOVA_HAND, STYLE_HANDS8, "", SAMPLE),
    "h9_open": (H9_OPEN, lambda: [os.path.join(SAMPLE, "h8_open.png")] + RONOVA_HAND, STYLE_HANDS8, "", SAMPLE),
    "h9_open_b": (H9_OPEN, lambda: [os.path.join(SAMPLE, "h8_open.png")] + RONOVA_HAND, STYLE_HANDS8, "", SAMPLE),
    "h9_open_c": (H9_OPEN, lambda: [os.path.join(SAMPLE, "h8_open.png")] + RONOVA_HAND, STYLE_HANDS8, "", SAMPLE),
    "b_0": (B_0.replace("The second attached picture is the main painting of the age this card belongs to: take its palette and its mood, not its composition. ", "The first attached picture is also the main painting of the age this card belongs to: take its palette and its mood, not its composition. "), back_refs(0), STYLE_CARD, WEST_PLAIN, SAMPLE),
    "b_1": (B_1, back_refs(1), STYLE_CARD, WEST_PLAIN, SAMPLE),
    "b_2": (B_2, back_refs(2), STYLE_CARD, WEST_PLAIN, SAMPLE),
    "b_3": (B_3, back_refs(3), STYLE_CARD, WEST_PLAIN, SAMPLE),
    "table": (TABLE, lambda: [LOCK], STYLE_CARD, "", SAMPLE),
    "bb2_0": (BB2_0, bb2_refs(0), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb2_1": (BB2_1, bb2_refs(1), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb2_2": (BB2_2, bb2_refs(2), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb2_3": (BB2_3, bb2_refs(3), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb3_0": (bb3(BB2_0) + BB2_REF, bb2_refs(0, True), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb3_1": (bb3(BB2_1) + BB2_REF, bb2_refs(1, True), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb3_2": (bb3(BB2_2) + BB2_REF, bb2_refs(2, True), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb3_3": (bb3(BB2_3) + BB2_REF, bb2_refs(3, True), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb2_0r": (BB2_0 + BB2_REF, bb2_refs(0, True), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb2_1r": (BB2_1 + BB2_REF, bb2_refs(1, True), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb2_2r": (BB2_2 + BB2_REF, bb2_refs(2, True), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb2_3r": (BB2_3 + BB2_REF, bb2_refs(3, True), STYLE_BB2, WEST_PLAIN, SAMPLE),
    "bb_0": (BB_0, bb_refs(0), STYLE_BB, WEST_PLAIN, SAMPLE),
    "bb_1": (BB_1, bb_refs(1), STYLE_BB, WEST_PLAIN, SAMPLE),
    "bb_2": (BB_2, bb_refs(2), STYLE_BB, WEST_PLAIN, SAMPLE),
    "bb_3": (BB_3, bb_refs(3), STYLE_BB, WEST_PLAIN, SAMPLE),
    "bb_0b": (BB_0, bb_refs(0), STYLE_BB, WEST_PLAIN, SAMPLE),
    "bb_1b": (BB_1, bb_refs(1), STYLE_BB, WEST_PLAIN, SAMPLE),
    "bb_2b": (BB_2, bb_refs(2), STYLE_BB, WEST_PLAIN, SAMPLE),
    "bb_3b": (BB_3, bb_refs(3), STYLE_BB, WEST_PLAIN, SAMPLE),
}


def one(key):
    prompt, refs, style, west, outdir = JOBS[key]
    try:
        os.makedirs(outdir, exist_ok=True)
        out = gen(os.path.join(outdir, key), prompt + style + west + CLEAN, refs=refs())
        print("好了", key, out)
    except Exception as e:
        print("失败", key, e)


if __name__ == "__main__":
    keys = [k for k in sys.argv[1:] if k in JOBS]
    if not keys:
        print("键：", " ".join(JOBS))
        sys.exit(0)
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(int(os.environ.get("FRONT_WORKERS", "3"))) as ex:
        list(ex.map(one, keys))
