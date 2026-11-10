#!/usr/bin/env python3
# 角色立绘（第三版，设定图）。用户 11-05 定的：四套衣服一张图一次出，切开用，人才是同一个；表情另出一张。写法试出来的经过见 立绘画法.md 第十三节。
# 这是卡里来回切换的差分，不是设定稿。用户定的：面相、镜头、身形基本一样，都看镜头；姿势和手里的东西随衣服轻微变，私服放松，战斗装持自己的武器、绷紧，正装端庄。
# 一位三张，先后不能乱：
#   sheet  四套衣服（常服、私服、战斗、正装）横版一张，切成 cell_casual/private/battle/formal.png，一格 640×960（cast_slice.py）
#   art    艺术照，参考是官方艺术卡加切好的常服
#   faces  九格表情，参考是切好的常服和放大的头
# 这个人有第二版的常服（out/立绘_v2/<en>/casual.png），拿它当最后一张参考定手法和长相，腿不照它；没有就用现有立绘裁的头。
# 四个人碰在一起切不开的话换个说法重出一回，再不行报失败，不硬切。
# 图写 out/立绘_v3/<en>/，已有的不重出。未成年那一档（minor）不在这里出，资料里写了 young_ok 的除外（希尔妲、芙莉莲，看着十五到十七的老传奇）：
#   参考只用不露肤的几张，不写身段，穿戴整齐，艺术照只到头肩。
#   python gpt_sheet.py eleanor kamelika   出这几位缺的
#   python gpt_sheet.py --all              全员
#   python gpt_sheet.py --list             列谁缺什么
# 环境变量 CAST_WORKERS 改同时跑几张，默认 3。
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cast_slice as CS
import era_fashion as EF
import gpt_cast as G
import gpt_gen
from PIL import Image

# CAST_SET=前传 这一类：只读 cast/<set>/*.json，图写 out/立绘_<set>/（一纪一套，11-05 铺开各纪）
SET = os.environ.get('CAST_SET', '')
OUT = os.environ.get('SHEET_OUT') or os.path.join(HERE, 'out', '立绘_' + SET if SET else '立绘_v3')   # SHEET_OUT 改输出目录，SHEET_ONLY=1 只出设定图，SHEET_STRICT=1 双臂下垂、手里不拿东西
LEGS = {
    'woman': ("LEGS, the most important point, follow the standing adult woman in the first attached picture: a high waist and a short torso; measured from the top of the head to the sole, the crotch sits at 47 percent of the height, so the legs are longer than the head and torso together; the knee at 68 percent; the lower leg clearly longer than the thigh. Even under a long skirt the hips sit that high. The legs are NOT crossed; the weight on one leg, the other knee a little relaxed. Tall boots stop a hand below the knee. "),
    'man': ("LEGS: long legs and a short torso: measured from the top of the head to the sole, the crotch sits at 48 percent of the height and the knee at 69 percent. The legs are NOT crossed; the weight on one leg. "),
    'small': '',
}
LEGS['burly'] = LEGS['man']
LEGS['girl'] = ''   # 年少模样的不写腿和身段
LEGS['youth'] = LEGS['man']
LEGS['boy'] = ''   # 少年同少女，不写腿和身段
LEGS['child'] = ''   # 孩童（十三岁以下），同上
G.BODY['child'] = ('BODY: a child of about ten: about 5 heads tall, a large head, short limbs, a small slim body, fully covered by the clothes, nothing about the body emphasised. A natural, lively stance; small hands drawn with care. ')
G.FACE['child'] = ('FACE, as in the references: large, bright, gently rounded eyes with a thin tapering dark-brown upper lash line; soft round cheeks; a tiny nose; a small mouth; a round, childlike face. Clean skin with very little shading; skin shadows are a soft warm tone. ')
G.BODY['boy'] = ('BODY: a teenage boy: about 6.5 heads tall, a relatively large head, narrow shoulders, slim limbs, a slender youthful build, fully covered by his clothes, nothing about the body emphasised. A light natural stance, the weight on one leg; fingers drawn with care. ')
G.FACE['boy'] = ('FACE, as in the references: medium, sharp, gently slanted almond eyes, a thin tapering dark-brown upper lash line and a fine eyelid crease; the iris a soft luminous gradient with a small highlight; straight eyebrows; a small nose shown by a faint shadow; a small mouth; a youthful face with a soft jaw, not angular. Clean skin with very little shading; skin shadows are a soft warm tone. ')
# 十九岁模样、软乎乎不习武的年轻男人（霍布）
G.BODY['youth'] = ('BODY: a young man of about nineteen with the proportions of the younger adult male characters of that game: about 7 heads tall, a little short and soft, rounded relaxed shoulders, NOT muscular and NOT trained, but clearly a grown young man and NOT a child. A lazy, easy stance, the weight sunk on one leg; hands drawn with care. ')
# 年少模样但资料写了块头大的（葛嘉）：资料里写 sturdy: true，只换掉肩窄、四肢细那半句，年少的照旧不写 build
STURDY = {'girl': ('BODY: a teenage girl: about 6 heads tall, a relatively large head, tall and sturdy for her age: broad shoulders, a strong thick neck, solid arms and big capable hands, a sturdy frame rather than a slender one, fully covered by her clothes, nothing about the body emphasised. A steady, grounded stance; fingers drawn with care. '),
          'boy': ('BODY: a teenage boy: about 6.5 heads tall, a relatively large head, tall and sturdy for his age: broad shoulders, a strong thick neck, solid arms and big capable hands, a sturdy frame rather than a slender one, fully covered by his clothes, nothing about the body emphasised. A steady, grounded stance; fingers drawn with care. ')}


# 十六七岁（资料写 teen: true，11-05 用户定的）：男女一眼分得清、衣服照设定，身材照旧不写，不露肤，不暗示
TEEN = {'girl': ('BODY: a girl of sixteen or seventeen, about 7 heads tall, the head a natural size and NOT oversized, her shoulders clearly wider than her head, a neck of natural length, arms of natural length and substance, her own height and overall frame as described: clearly a young woman-to-be in her face, hair, posture and gestures, not a small child and not androgynous. Her clothes follow the design as described, neatly fitted but modest and covering, nothing about the body emphasised, nothing suggestive. A natural stance that shows her personality; fingers drawn with care. '),
        'boy': ('BODY: a boy of sixteen or seventeen, about 7.5 heads tall, the head a natural size and NOT oversized, his shoulders clearly wider than his head, a neck of natural length, arms of natural length and substance, his own height and overall frame as described: clearly a young man-to-be in his face, hair, posture and gestures, not a small child and not androgynous. His clothes follow the design as described, neatly fitted but modest and covering, nothing about the body emphasised, nothing suggestive. A natural stance that shows his personality; fingers drawn with care. ')}


# 十八九岁（资料写 ya: true，11-06 用户把底卡十位改成十八九岁）：身材不写，衣服照设定、不露肤，脸不再是孩子脸
YA_BODY = ('BODY: the first attached picture is a PROPORTION reference only, a standing game model of a young woman of about eighteen to twenty: take from it the head-to-body ratio, the shoulder width, the length of the arms and legs and the lightness of the frame, and nothing else (not its clothes, hair, face or rendering). ''So: about 6.5 to 7 heads tall with the head a natural size, slim straight shoulders a little wider than the head, a slender neck, a light slim frame, long slim legs and arms, small hands; clearly a young adult, visibly younger and slighter than a woman of thirty, and clearly not a child. ''Her clothes follow the design as described, fully covering, nothing about the body emphasised, nothing suggestive. A natural easy stance that shows her personality; fingers drawn with care. ')
YA = {'girl': YA_BODY, 'woman': YA_BODY}
LEGS_YA = 'LEGS: as in the first attached picture: long slim legs, the crotch at about 48 percent of the height measured from the top of the head, the knee at about 70 percent, the lower leg a little longer than the thigh; the weight on one leg, the other knee relaxed. '
YOUNG_YA = ' This character is a young woman of eighteen or nineteen: keep the outfit design as described, fully covered and modest, nothing about the body emphasised, nothing suggestive.'


# 半身人（11-06 用户定的）：幼态脸，跟矮人分开。矮人照旧走 small 的成年脸。不写胸、胯，衣服穿严实，跟年少的一样对待
HALF_BODY = 'BODY: a halfling, one of a small folk about the height of a human child: about 4 heads tall, a relatively large round head, short soft limbs, small hands and feet, a small round frame fully covered by the clothes, nothing about the body emphasised. A light natural stance; fingers drawn with care. '
HALF_FACE = 'FACE, as in the references: a soft round baby face: large round bright eyes with a small highlight, a thin tapering dark-brown upper lash line, short light brows, full round cheeks with a faint blush, a tiny button nose, a small mouth, a short soft chin. Pale clean skin with very little shading; skin shadows a soft warm tone. The eyes are large and round, NOT sharp or narrow almond eyes. '
YOUNG_HALF = ' This character is a halfling with a youthful round face: a wholesome, fully covered look, nothing about the body emphasised, nothing suggestive.'


def halfling(c):
    return c.get('tier') == 'small' and 'halfling' in (c.get('who') or '').lower()


def legs(c, t):
    return LEGS_YA if c.get('ya') else LEGS[t]


def body(c, t):
    if halfling(c):
        return HALF_BODY
    if c.get('ya') and t in YA:
        return YA[t]
    if c.get('teen') and t in TEEN:
        return TEEN[t]
    return STURDY[t] if c.get('sturdy') and t in STURDY else G.BODY[t]


YOUNG = ' The character looks like a teenager: draw a youthful, wholesome, fully covered look, nothing about the body emphasised, nothing suggestive.'
YOUNG_TEEN = ' The character is a teenager of sixteen or seventeen: keep the outfit design as described, fully covered and modest, nothing about the body emphasised, nothing suggestive.'
SHEET = ('A character design sheet on one wide picture: FOUR full-body standing figures of this one character in a single horizontal row, in four different outfits. All four are exactly the same person: the same face, the same eyes, the same height and build, the same head size. '
         'Draw each figure as its own finished character sprite, with the same care as a full-page illustration: a crisp thin line, sharp almond eyes, every lock of hair a clean ribbon shape, never a mass of small wavy strands, even at this size. '
         'These are outfit variations of one game sprite for a visual novel, swapped in the same spot on screen, so the face and camera stay the same: in all four the same very slight three-quarter turn of the body, the same head size and height, the face toward the viewer and the eyes looking straight into the camera, the same overall build. Within that, the body language changes a little to suit each outfit, a slight adjustment and not a new pose: '
         '1) the everyday outfit: this character\'s natural, easy standing pose, holding their usual small item if they have one. '
         '2) the private outfit: more relaxed, the shoulders loose and lowered, the weight settled on one leg, a soft expression, the hands loosely holding a small personal object or simply at rest. '
         '3) the battle outfit: tense and ready, the shoulders squared, the feet a little wider and planted, a firm expression, gripping this character\'s own weapon in the hand or hands, kept close to the body. '
         '4) the formal outfit: dignified and very upright, the back straight, the feet close together, the hands composed in front or at the sides, a serene expression. '
         'Everyone stands: no chair, no throne, no furniture. Nothing rises higher than the top of the head: a long staff, spear or halberd is held at a slant beside the body, its head or blade always at the upper end and never pointing at the ground. '
         'The air is almost still: the hair and loose cloth hang naturally with a slight lift, staying inside each figure\'s own quarter of the picture and never touching the neighbouring figure: there is always a clear empty gap between figures. '
         'Every figure is complete from the top of the head to the soles of the feet, the feet all on one level, the heads all at one height, filling the full height of the picture. Even light, no dramatic shadow. '
         'Fully clothed, modest, not sexualized. Transparent background: no floor, no cast shadow. No text, no labels, no numbers, no frame, no dividing lines. Landscape picture, aspect ratio 3:2. ')
STRICT = ('Stricter still: in all four figures both arms hang straight down, relaxed at the sides, in exactly the same position, the hands empty and open. Nothing is held in the hands: any staff, flower, food, bag, cloak, tool or rope in the descriptions is left out or hung from the belt; a weapon is worn at the hip or carried on the back. Ignore the pose in the LAST attached picture. Laid over one another, the four figures would match at the head, shoulders, arms, hips and feet, and differ only in clothes. ')
RETRY = 'Leave much wider empty gaps between the figures this time and keep every sword, staff, cape and lock of hair well inside its own quarter. '
# 11-05 前传第五页查图查出来反复出的毛病，设定图统一防着
GUARD = ("Every item named in the descriptions appears only once on each figure, never duplicated. Left and right always mean the character's own left and right. "
         'No East Asian dress or hair: no crossed wrap collars, no wide hanging sleeves, no topknot with a pin through it. No crescent or moon shapes anywhere. '
         'Robes, gowns and coats are cut in the European medieval and renaissance manner: they close down the front with plain round buttons in a straight row or with lacing, never with looped cord or knotted cloth fastenings across the chest; a high collar is a soft or fold-over European collar, never a stiff mandarin collar; fitted sleeves narrow to the wrist; sashes and belts are narrow; cords end in small plain knots with no tassels and no decorative knots. '
         'Each character looks exactly the age the description gives: when it says forty, fifty, sixty or older, the face plainly shows it with visible lines at the eyes and mouth, never a youthful face. '
         'Characters with animal ears have only those animal ears, no human ears beside them. No earrings, ear studs or other jewellery unless the description names them. ')
# 1001 那一套（不设 CAST_SET）：现今的魔导奇幻，衣服和战斗装照现在二次元游戏的设计走，不写中世纪（11-06 用户要的）；四纪照旧用 GUARD
GUARD_1001 = GUARD.replace('Robes, gowns and coats are cut in the European medieval and renaissance manner: they close', 'This is a present-day magitech fantasy world with electric lamps, trains, rune-engraved brass and glowing crystal cores: clothes and battle gear are designed like a modern fantasy game\'s, tailored and layered, with straps, buckles, plates and a few glowing rune or crystal details, sleek and cool rather than medieval, never real-world streetwear; they close')
assert GUARD_1001 != GUARD


# 11-06 用户看了头一版说再华丽些：传奇的战装一句写重，而且放进第三格的描述前头（IMPOSING_LEAD），末尾再压一句（IMPOSING）
IMPOSING_LEAD = ('LEGENDARY WAR GEAR, by far the most elaborate figure on this sheet: this character is a living legend and this gear is the finest in the world, designed like the final boss or the top-rarity limited character of a modern gacha fantasy game. ')
IMPOSING = ('The third figure must be far richer and more dramatic than the other three: over-designed, layered war gear with large sculpted pauldrons, ornate plates of rare dark metal chased with gold or silver filigree, many fine engraved rune lines and set crystals that glow and throw coloured light onto the armour, a heavy cloak or mantle with an elaborate lining, long ribbons or a sash, a tall ornamented collar or crest, and an oversized, highly detailed signature weapon with its own glow and ornament, gripped and ready; the silhouette reads as powerful and intimidating at a glance, while the face, hair and body proportions stay exactly the same as the other three figures and the whole figure, weapon included, stays inside its own quarter of the picture. ')


def imposing_of(c, k):
    return IMPOSING if (not SET and c.get('imposing')) else ''


def battle_of(c):
    return (IMPOSING_LEAD if (not SET and c.get('imposing')) else '') + c['battle']


# 四纪老纪（11-07）：中世纪那一句连“一排圆扣”一起写死了，两万年的衣裳全成一个剪裁（风尚审图查出来的）。按页认时段，换成这一段的风尚、奇幻那一层和扣法（era_fashion.py）
_MEDIEVAL = 'Robes, gowns and coats are cut in the European medieval and renaissance manner: they close down the front with plain round buttons in a straight row or with lacing, never with looped cord or knotted cloth fastenings across the chest; a high collar is a soft or fold-over European collar, never a stiff mandarin collar; fitted sleeves narrow to the wrist; sashes and belts are narrow; cords end in small plain knots with no tassels and no decorative knots. '
assert _MEDIEVAL in GUARD
_NO_EAST = 'Fastenings are never looped cord or knotted cloth across the chest, a raised collar is never a stiff mandarin collar, and cords end in small plain knots with no tassels. '


def guard_of(c):
    if not SET or SET == '主角':   # 11-10 主角预设立绘（cast/主角/）：建档的人都是迷宫纪1001年出发的，照 1001 那一套
        return GUARD_1001
    return GUARD.replace(_MEDIEVAL, _NO_EAST + EF.block(SET, c['en']))


B3 = "3) the battle outfit: tense and ready, the shoulders squared, the feet a little wider and planted, a firm expression, gripping this character's own weapon in the hand or hands, kept close to the body. "   # 第三格那一句，资料里有 battle_pose 的换掉
assert B3 in SHEET
FACES = G.FACES.replace('The attached picture shows this character:', 'The attached pictures show this character, full figure and a close-up of the head:')
# 11-07：闭盔不露脸的人（诺伦），九格的表情不能靠面甲变形，只靠头的角度（用户看了狮王盔的九格说搞笑）。资料写 faces_fixed: true 走这一版。
_I = FACES.index('Top row, left to right:')
_J = FACES.index('Transparent background')
FACES_FIXED = (FACES[:_I].replace('the eyes at the same height, ', '')
               + 'The helm is a closed piece of armour: it never changes shape, never opens, and shows no eyes, mouth or face in any cell; the ONLY difference between the nine cells is the angle of the head and neck, and the set of the shoulders. '
               'Top row, left to right: the helm level and square to the viewer, at rest; the head tilted a little to one side, as if listening kindly; the head raised a touch with the chin up, open and at ease. '
               'Middle row, left to right: the head lowered slightly, the visor fixed on the viewer, resolute; the head thrust a little forward and the shoulders squared, hard; the head bowed, the visor turned down and away. '
               'Bottom row, left to right: the head drawn back a touch with the chin lifted, startled; the head turned half away, the visor toward the ground; the head dropped and tilted to one side, as if bearing a blow. '
               + FACES[_J:])
CELLS = ('casual', 'private', 'battle', 'formal')
# 11-07 神明立绘：资料里写 cells 就只出那几套（行走人世三套不出战斗服，神座只出正装一格），不写照旧四套
SHEET1 = ('A single full-length character sprite of this one being, a finished game sprite drawn with the same care as a full-page illustration: a crisp thin line, clean colour with soft gradients, every lock of hair a clean ribbon shape. '
          'It is shown on or before its divine seat exactly as described; the seat is part of the sprite and is drawn complete. The whole sprite, from its highest point to the base of the seat, fills the height of the picture. '
          'Even light, no dramatic shadow. Fully clothed, modest, not sexualized. Transparent background: no floor beyond the seat itself, no cast shadow, no landscape. No text, no labels, no numbers, no frame. Portrait picture, aspect ratio 2:3. ')
# 非人形的魔神（兽、空羽衣、一团东西）：艺术照不照人的脸写
ART_NH = ('Draw in the rendering of the attached official key art from Honkai: Star Rail, for style only: do not copy their characters, costumes or props. The LAST attached picture is a close-up of this exact being and the one before it its full sprite on its divine seat: keep its shape, materials, colours and marks exactly. '
          'A dramatic promotional art piece of it, the same kind of picture as the references: a close crop with the camera tilted on a diagonal, seen from below as if by a worshipper kneeling at the foot of the seat, the being large and cut off by the frame. '
          'Luminous colour: one strong directional light in %s floods in from one side, razor-sharp shadow shapes, the highlights blooming softly toward white. Large out-of-focus foreground shapes that belong to it drift across the corners; the background is soft glowing colour, not a detailed scene. '
          'No text, no logo, no frame. Portrait picture, aspect ratio 2:3. No crescent or moon shapes anywhere. ')


def cells_of(c):
    return list(c.get('cells') or CELLS)


def first_cell(k):
    return os.path.join(d(k), 'cell_' + cells_of(G.CAST[k])[0] + '.png')


def sheet_text(c):
    cs = cells_of(c)
    if len(cs) == 4:
        return SHEET
    if cs == ['formal']:
        return SHEET1
    if cs == ['casual', 'private', 'formal']:
        t = SHEET
        for a, b in (('FOUR full-body standing figures', 'THREE full-body standing figures'), ('in four different outfits', 'in three different outfits'),
                     ('All four are exactly', 'All three are exactly'), ('in all four the same', 'in all three the same'), (B3, ''),
                     ('4) the formal outfit', '3) the formal outfit'), ('own quarter of the picture', 'own third of the picture')):
            assert a in t, a[:40]
            t = t.replace(a, b)
        return t
    raise ValueError('cells 只认四套、三套（常服私服正装）、一套（正装）：%s' % cs)
# 艺术照走过三回（立绘画法.md 第十七节）：头一回整张一个色相、硬影压脸，人认不出；第二回照立绘但素了，用户要回看官方；这一回官方的力度拿回来，眼睛那一块不压影子，颜色是这个人自己的。
ART = ('Draw in the rendering of the attached official key art from Honkai: Star Rail, for style only: do not copy their characters, costumes or props. The LAST attached picture is a close-up of this exact character\'s head and the one before it the full sprite: the same face, eye shape, eye colour, hair colour, hairstyle and outfit, instantly recognisable as that sprite. Above all the face must be the same drawing as that close-up: the same face shape, the same proportions of eyes, nose and mouth, the same age. '
       'A dramatic promotional art portrait, the same kind of picture as the references: a close crop with the camera tilted on a diagonal, the face large and off-centre, the figure cut off by the frame, the hair drawn in big clean shapes at exactly its length in the sprite (short hair stays short). '
       'Luminous, high-key colour: one strong directional light in %s floods in from one side, the highlights bloom softly toward white on the hair and shoulder, the shadow side of the skin takes a saturated tint of the palette, while the hair keeps its own colour in shadow, only darker. Razor-sharp shadow shapes cast by foreground things fall across the hair, neck and clothes and the far edge of the cheek, but the whole eye area stays clear, lit and beautifully detailed: the eyes are the brightest focal point, with a glowing gradient iris. '
       'Large out-of-focus foreground shapes that belong to this character drift across the corners of the frame; the background is soft glowing colour and bokeh, not a detailed scene. Thin crisp line art in a darker tint of each local colour, smooth skin with very simple shading. The hair, eye and clothing colours stay recognisably the character\'s own. Fully clothed, not sexualized. No text, no logo, no frame. Portrait picture, aspect ratio 2:3. ')
ART_END = ' Whatever is said above, no shadow crosses the eyes: a shadow on the face stays at the far edge of the cheek or below the eyes. The hair keeps its own colour and length from the sprite; coloured light only rims its edges; grey, white and silver hair stays neutral grey or white, never lavender, violet, pink or blue. However much the picture is tilted, the face itself is drawn correctly: both eyes the same size and level with each other across the face, the nose and mouth centred, nothing skewed or distorted. No crescent or moon shapes anywhere.'
STRAIGHT = (' The face is drawn straight and well proportioned: both eyes level with each other and the same size and shape, the nose centred between them, '
            'the mouth centred under the nose, the jaw symmetrical; the head is turned only slightly and tilted only a little, never skewed or distorted.')
# 用户 11-05 和底卡 #490：跨进传奇就不再老了，几千年也还是凝名那时的样子，多出来的是眼神。
OLD_EYES = 'This character has lived for a very long time without ageing: the face stays as it is, and only the eyes carry the weight of those years, calm and deep. '
NOT_LEGEND = ('eleanor', 'tifa', 'kamelika', 'alice', 'sisne')


# cast/覆盖.json：按人补的。who 换整段；face 换掉通用的脸（要看现有立绘和原型的人，比如爱丽丝）；ref_head 用现有立绘的头当最后一张参考，不用第二版常服；build 是档案有体态数据的成年人的身材（只有五位）；art_close 艺术照只到头肩
for _k, _v in json.load(open(os.path.join(HERE, 'cast', '覆盖.json'), encoding='utf-8')).items():
    G.CAST[_k].update(_v)
if SET:   # 一纪一套：只认这一纪的资料，键不跟 1001 那一套混
    import glob as _glob
    G.CAST = {}
    for _f in sorted(_glob.glob(os.path.join(HERE, 'cast', SET, '*.json'))):
        for _c in json.load(open(_f, encoding='utf-8')):
            assert _c['en'] not in G.CAST, ('键重了', _c['en'], _f)
            G.CAST[_c['en']] = _c
    # 11-10 主角预设的换族属（same_person）：脸、身子、头发照本人那一条，只换常服、私服、正装；艺术照、表情、战斗装都照本人，不另出
    for _k, _c in list(G.CAST.items()):
        if _c.get('same_person'):
            _m = {kk: vv for kk, vv in G.CAST[_c['same_person']].items() if kk not in ('name', 'en', 'src', 'palette', 'casual', 'private', 'battle', 'formal', 'art', 'battle_note', 'cells')}
            _m.update(_c)
            G.CAST[_k] = _m
SAME_LEAD = ('The LAST two attached pictures show this exact character, the full everyday sprite and a close-up of the head: copy the face, the eye shape and eye colour, the hair colour and hairstyle, '
             'the skin colour, every mark, horn, ear or tail, the height, the build and the body proportions exactly, so that every figure is unmistakably the same person as that sprite; '
             'ONLY the clothes and what is held in the hands change, as described below. Ignore that sprite\'s clothes. ')


def d(k):
    return os.path.join(OUT, k)


def tier(c):
    return c.get('tier') or ('man' if c.get('sex') == 'm' else 'woman')


def ytail(c):
    if halfling(c):
        return YOUNG_HALF
    if c.get('ya'):
        return YOUNG_YA
    return YOUNG_TEEN if c.get('teen') else YOUNG


def young(c):
    return c.get('tier') in ('girl', 'boy', 'child') or bool(c.get('minor')) or halfling(c)


def style_refs(c):
    if c.get('ya'):   # 十八到二十岁：第一张是比例参考（用户给的崩铁模型截图裁的，只给比例），后两张是画法（11-06）
        return [os.path.join(G.REF, 'hsr_model', 'firefly_front.png')] + G.lc('lance_full', 'firefly_top')
    if c.get('sex') != 'm' and c.get('teen'):
        return G.lc('lance_full', 'firefly_top') + G.card('saifei')
    if young(c):   # 不露肤的几张
        if c.get('sex') == 'm':
            return G.lc('jingyuan', 'anaxa') + G.card('danheng')
        return G.lc('firefly_top', 'huohuo') + G.card('saifei')
    if c.get('sex') == 'm':
        return G.lc('jingyuan', 'anaxa', 'lance_full')
    return G.lc('himeko_stand', 'aglaea_stand', 'guinaifen')


def sheet_prompt(k, extra=''):
    c = G.CAST[k]
    t = tier(c)
    face = c.get('face') or G.FACE[t if t in ('boy', 'child') else ('man' if c.get('sex') == 'm' else t)]
    if halfling(c):
        face = (c.get('face') or HALF_FACE) + c.get('face_extra', '')
    if c.get('ya') and not c.get('face'):
        face = G.FACE_F % "fresh and clear, a young adult's, no longer childish"
    spec = body(c, t) + legs(c, t) + c.get('build', '') + G.HAIR + face + G.REST + c['who'] + ' '
    if c.get('nonhuman'):   # 11-07 神座：兽、空羽衣、一团东西，不套人的身体和脸
        spec = c['who'] + ' '
    cs = cells_of(c)
    if cs == ['formal']:
        outfits = 'The look: ' + c['formal'] + ' '
    else:
        outfits = 'From left to right: ' + ' '.join('%d) %s' % (i + 1, battle_of(c) if x == 'battle' else c[x]) for i, x in enumerate(cs)) + ' '
    v2 = G.path(k, 'casual')
    # anchor：没有自己旧图的新人，垫一张同一套画法的成品（别人的常服），只取画法，画法稳一些；体型差得远的别垫，会被带过去（霍布垫卢米安被带高带瘦，11-05）
    anc = [os.path.join(os.path.dirname(OUT), c['anchor'])] if c.get('anchor') else []
    anc_lead = ('The %s attached picture is a finished sprite from this same set, of a DIFFERENT character: match its rendering exactly, the thin warm-brown line, the clean colouring with soft gradients, the light shading and the transparent background, but take nothing else from it: not the face, hair, eyes, body, clothes or pose. ')
    if c.get('refs'):   # 用户给了这个人的图，就照用户的图
        last = [os.path.join(G.REF, 'old', r) for r in c['refs']]
        lead = 'The LAST %d attached pictures show this exact character: follow their face, build, hair and clothing design closely; ignore their rendering and background. ' % len(last)
        return G.LC + lead + body(c, t) + legs(c, t) + c.get('build', '') + G.HAIR + face + G.REST + c['who'] + ' ' + outfits + SHEET + imposing_of(c, k) + guard_of(c) + (STRICT if os.environ.get('SHEET_STRICT') else '') + extra + (ytail(c) if (young(c) or c.get('ya')) else ''), style_refs(c)[:2] + last
    if c.get('full_ref'):   # 11-06：整张原立绘当参考，脸照它，衣服照字
        last = [os.path.join(G.REF, 'old', k + '_full.png')]
        lead = ('The LAST attached picture is this exact character\'s existing portrait: copy her face closely: the eye shape, eye colour, brows, mouth and her habitual expression in that picture, so that she is instantly recognisable as the same person, but drawn in the hand of the style references. Take the hair colour, hairstyle and hair ornaments from it too, drawn as a few big clean locks like the style references, NOT in that picture\'s fine scattered wispy strands. Ignore that picture\'s pose, background and heavy glossy rendering; the body proportions follow the BODY line below and the clothes follow the outfit descriptions below, not that picture. ')
        return G.LC + lead + body(c, t) + legs(c, t) + c.get('build', '') + G.HAIR + face + G.REST + c['who'] + ' ' + outfits + SHEET + imposing_of(c, k) + guard_of(c) + (STRICT if os.environ.get('SHEET_STRICT') else '') + extra + (ytail(c) if (young(c) or c.get('ya')) else ''), style_refs(c) + last
    if c.get('same_person'):
        last = [os.path.join(d(c['same_person']), 'cell_casual.png'), os.path.join(d(c['same_person']), 'head.png')]
        lead = SAME_LEAD
    elif os.path.exists(v2) and not c.get('ref_head'):
        last = [v2]
        lead = 'The LAST attached picture shows this exact character: copy its face, eyes, hair colour, hair ornaments and way of drawing, but NOT its leg proportions. '
    elif c.get('identity'):
        last = [os.path.join(os.path.dirname(OUT), c['identity'])]
        # 发色也照资料：同一个人年轻时还没白头发（11-05 前传第一页查出来的）
        lead = 'The LAST attached picture is this same person in another period of their life: keep the same face shape, eye shape and eye colour, so that they are clearly the same person; their age, hair colour, hairstyle and clothes follow the description below, not that picture: when the description is younger than that picture, draw a younger face with smooth skin and none of its lines, wrinkles or tiredness; when the description gives another hairstyle, draw that hairstyle and not the one in the picture (no ponytail, bun or braid the description does not name). Take only the face from it: none of its accessories, glasses, goggles, earrings, hair ornaments or clothes, which belong to another time. '
        if anc:
            lead = anc_lead % 'second-to-last' + lead
            last = anc + last
    else:
        last = (G.EXTRA.get(k) or G.head_of(k))[:1]
        # 11-07：参考图多半是暖光下的旧立绘，皮肤被光染成古铜（莱恩哈特），写明肤色照资料不照参考
        lead = 'The LAST attached picture shows this exact character: keep the face shape, the eyes, the habitual expression, hair colour, hair style, eye colour and hair ornaments; the hair is drawn as a few big clean locks like the style references, NOT in that picture\'s fine scattered wispy strands; ignore its background, its heavy glossy rendering and its lighting: the skin colour follows the description below, not the warm or dark tint that picture\'s light gives the skin. ' if last else ''
        if not last:   # 11-07
            lead = ''
        if last and c.get('loose_ref'):   # 11-06：参考只给身份，脸照风格参考重画，不照搬旧图的眼睛画法和神情
            lead = ('The LAST attached picture is only an identity reference for this character: take from it the hair colour, hairstyle, hair ornaments, eye colour and the general shape of the face, nothing else. '
                    'Do NOT copy its drawing: its eye shape, heavy lashes, eye make-up, lip shading, pose and expression are all discarded. Redraw the face from scratch in the hand of the style references and exactly as the FACE description below says, with eyes fully open, a frank neutral expression, no hand near the face, the head facing the viewer. ')
        if anc:
            lead = anc_lead % ('second-to-last' if last else 'LAST') + lead
            last = anc + last
    sheet = sheet_text(c)
    sheet = sheet.replace('sharp almond eyes, ', 'the eyes exactly as described, ') if c.get('face') or halfling(c) else sheet
    if c.get('battle_pose') and 'battle' in cs:   # 第三格换一句：霍布不打仗、扛粮不拿兵器，希尔妲握短火把
        sheet = sheet.replace(B3, c['battle_pose'])
    tail = ytail(c) if young(c) else ''
    # 11-07：只给兵器看的参考图（凯尔萨斯的贯穹照黑魂的猎龙剑枪）。资料写 weapon_refs，文件在 语料/人物参考_11-04/old/，排在最后，只取兵器的样子
    wr = [os.path.join(G.REF, 'old', r) for r in c.get('weapon_refs', [])]
    wlead = ('The final %d attached picture(s) show ONLY the design of this character\'s weapon: copy that weapon\'s shape, proportions, blade and fittings closely, drawn in the hand of the style references; take nothing else from them, not any face, hair, clothes, pose or background. ' % len(wr)) if wr else ''
    return G.LC + lead + spec + outfits + sheet + imposing_of(c, k) + guard_of(c) + (STRICT if os.environ.get('SHEET_STRICT') else '') + extra + tail + wlead, style_refs(c) + last + wr


def make_cells(k, src):
    cs = cells_of(G.CAST[k])
    figs = CS.figures(CS.clean(Image.open(src)), len(cs))
    if figs is None:
        return False
    for name, f in zip(cs, CS.cells(figs)[0]):
        f.save(os.path.join(d(k), 'cell_' + name + '.png'))
    cell = Image.open(first_cell(k))
    bb = cell.getchannel('A').getbbox()
    h = bb[3] - bb[1]
    # 放大的头给表情当参考：竖着取上面 22%，横着按头的位置取透明通道最靠上那一段的中心
    a = cell.getchannel('A').crop((0, bb[1], cell.width, bb[1] + h // 8))
    x0, _, x1, _ = a.getbbox()
    cx = (x0 + x1) // 2
    w = h * 22 // 100
    crop = cell.crop((max(0, cx - w // 2), bb[1], min(cell.width, cx + w // 2), bb[1] + w))
    bg = Image.new('RGBA', crop.size, (255, 255, 255, 255))
    bg.alpha_composite(crop)
    bg.convert('RGB').resize((crop.width * 4, crop.height * 4), Image.LANCZOS).save(os.path.join(d(k), 'head.png'))
    return True


def do_sheet(k):
    os.makedirs(d(k), exist_ok=True)
    if os.path.exists(first_cell(k)):
        return
    sp = G.CAST[k].get('same_person')
    if sp and not os.path.exists(os.path.join(d(sp), 'head.png')):
        raise RuntimeError(k + ' 本人 %s 的设定图还没出' % sp)
    stem = os.path.join(d(k), 'sheet')
    p, refs = sheet_prompt(k)
    t0 = time.time()
    gpt_gen.gen(stem, p, refs=refs, timeout=1200)
    if make_cells(k, stem + '.png'):
        print('  好了 %s sheet %ds' % (k, time.time() - t0), flush=True)
        return
    print('  切不开，重出一回', k, flush=True)
    os.replace(stem + '.png', stem + '_切不开.png')
    p, refs = sheet_prompt(k, RETRY)
    gpt_gen.gen(stem, p, refs=refs, timeout=1200)
    if not make_cells(k, stem + '.png'):
        raise RuntimeError(k + ' 设定图两回都切不开')
    print('  好了 %s sheet（重出） %ds' % (k, time.time() - t0), flush=True)


def art_job(k):
    # 艺术照：风格两张、立绘全身、放大的头（最后一张）。11-05 起跟 art_face_fix.py 同一套
    c = G.CAST[k]
    refs = G.refs_of(dict(c, minor=True) if halfling(c) else c, 'art')[:2] + [first_cell(k), os.path.join(d(k), 'head.png')]
    if c.get('nonhuman'):
        return (ART_NH % c['palette']) + c['who'] + ' ' + c['art'], refs
    # 不再老的传奇才加那一句：1001 那一套照 NOT_LEGEND 名单，铺开的各纪照资料里的 legend（凝了名的）
    eyes = OLD_EYES if (c.get('legend') if SET else k not in NOT_LEGEND) else ''
    p = (ART % c['palette']) + eyes + c.get('face', '') + c['who'] + ' ' + c['art'] + ' ' + c.get('art_extra', '') + STRAIGHT + ART_END
    if c.get('art_close') or young(c) or c.get('ya'):   # 外表容易显小的成年人和年少模样的，艺术照只到头肩
        p += ' The picture is framed from the upper chest up, on the face and the gesture of the hands.' if c.get('teen') else ' Only the head and shoulders are in the picture.'
    if young(c) or c.get('ya'):
        p += ' The collar and clothes fully cover the shoulders and chest.' + ytail(c)
    if c.get('teen'):
        p += ' No half-lidded or sleepy-eyed gaze and no softly parted lips: the mouth is closed, or in a plain wide grin only if the description above gives one; the look is frank and natural, nothing coy about it.'
    return p, refs


def do_next(job):
    k, kind = job
    c = G.CAST[k]
    cell = first_cell(k)
    head = os.path.join(d(k), 'head.png')
    t0 = time.time()
    if kind == 'art':
        p, refs = art_job(k)
    else:
        refs = [cell, head] + (G.head_of(k)[:1] if c.get('ref_head') else [])
        p = (FACES_FIXED if c.get('faces_fixed') else FACES) + c.get('face', '') + c['who'] + (ytail(c) if (young(c) or c.get('ya')) else '')
    gpt_gen.gen(os.path.join(d(k), kind), p, refs=refs, timeout=1200)
    print('  好了 %s %s %ds' % (k, kind, time.time() - t0), flush=True)


def eligible(keys):
    out = []
    for k in keys:
        if G.CAST[k].get('minor') and not G.CAST[k].get('young_ok'):
            print('跳过（未成年那一档）', k, G.CAST[k]['name'], flush=True)
        else:
            out.append(k)
    return out


def missing(k):
    m = []
    if not os.path.exists(first_cell(k)):
        m.append('sheet')
    if G.CAST[k].get('same_person'):   # 换族属只出那一张三套衣服
        return m
    for kind in (('art',) if G.CAST[k].get('no_faces') else ('art', 'faces')):
        if not os.path.exists(os.path.join(d(k), kind + '.png')):
            m.append(kind)
    return m


STOP = []   # 11-07：撞了出图额度就别再开新的（原来会把剩下几百张一张一张白跑失败，一张白耗一万多 token）


def _log_of(i):
    k, kind = (i, 'sheet') if isinstance(i, str) else i
    return os.path.join(d(k), kind + '.log')


def _limited(i):
    try:
        t = open(_log_of(i), encoding='utf-8', errors='replace').read().lower()
    except OSError:
        return False
    return 'usage_limit' in t or 'usage limit' in t


def pool(fn, items):
    def run(i):
        if STOP:
            raise RuntimeError('撞了出图额度，没开')
        try:
            return fn(i)
        except Exception:
            if not STOP and _limited(i):   # 在干活的线程里就立起来，排着队的下一张进门就停
                STOP.append(str(i))
                print('== 撞了出图额度，不再开新的', flush=True)
            raise
    with ThreadPoolExecutor(int(os.environ.get('CAST_WORKERS', '3'))) as ex:
        futs = {str(i): ex.submit(run, i) for i in items}
        for n, f in futs.items():
            try:
                f.result()
            except Exception as e:
                print('  失败', n, str(e)[:200], flush=True)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['--list']:
        for k in G.CAST:
            print(k, G.CAST[k]['name'], '未成年那一档，不出' if G.CAST[k].get('minor') and not G.CAST[k].get('young_ok') else ('齐' if not missing(k) else '缺 ' + ' '.join(missing(k))))
        sys.exit()
    keys = eligible(list(G.CAST) if args == ['--all'] else args)
    pool(do_sheet, [k for k in keys if 'sheet' in missing(k)])
    if not os.environ.get('SHEET_ONLY'):
        pool(do_next, [(k, kind) for k in keys if os.path.exists(first_cell(k)) for kind in missing(k) if kind != 'sheet'])
