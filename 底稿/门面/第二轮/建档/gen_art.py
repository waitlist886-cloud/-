#!/usr/bin/env python3
# 建档升级（门面第二轮，11-24）要的图：样张那一套（魂三张、四族、星牌、山铜纪身份牌框、手两种）以外补齐的。
#   CODEX_HOME=C:/Users/waitl/.codex_b python 底稿/门面/第二轮/建档/gen_art.py [键…]   不带键列出有哪些；写 all 跑全部
# 原图出在 底稿/状态栏/comfy/out/门面_建档/<键>.png（不进库），已有的跳过；处理成 webp 照 prep_art.py。
# 画法照样张 gen_art.py（定稿样 t2 加大幅牌背 bb_），手照 hand9 那一套，牌、骰子画成纯绿占位，出完抠掉。
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
sys.path.insert(0, COMFY)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
from gpt_gen import gen  # noqa: E402
import gpt_front as F  # noqa: E402

OUT = os.path.join(COMFY, 'out', '门面_建档')
REFD = os.path.join(OUT, 'ref')
SAMPLE_OUT = os.path.join(ROOT, 'out', '门面第二轮', '建档')          # 样张那一回出的原图
SAMPLE = os.path.join(COMFY, 'out', '门面_小样_11-10')
LOCK = F.LOCK
os.makedirs(OUT, exist_ok=True)
# 样张出过的原图挪过来一份（往后都在这一处）
for n in os.listdir(SAMPLE_OUT) if os.path.isdir(SAMPLE_OUT) else []:
    if n.endswith('.png') and not os.path.exists(os.path.join(OUT, n)):
        shutil.copy(os.path.join(SAMPLE_OUT, n), os.path.join(OUT, n))


def webp_ref(name, folder=None):
    from PIL import Image
    os.makedirs(REFD, exist_ok=True)
    dst = os.path.join(REFD, name + '.png')
    if not os.path.exists(dst):
        Image.open(os.path.join(folder or os.path.join(ROOT, '底稿', '门面', '小样_外壳', 'assets'), name + '.webp')).save(dst)
    return dst


def out_ref(name):
    return os.path.join(OUT, name + '.png')


CARD_STYLE = (
    " Drawing manner: the same hand as the attached pictures, which are approved cards and the approved style sample of this series: flat cut-paper colour shapes layered one over another, "
    "big flowing curves, thin lighter echo lines along the edges of the big shapes, soft inner gradients only, a fine paper grain over everything; metallic lines look like foil stamped on matte paper. "
    "Calm and clear: big simple shapes first, fine line detail second, quiet ground between them. Figures, if any, are simplified pale cut-paper silhouettes without detailed faces. "
    "No dense filigree, no gothic tracery, no heraldic shields, no realistic lighting, no heavy painterly rendering, no 3D render."
)
CARD = (
    "Draw one tall 2:3 portrait picture: the face of one fortune-telling card from a luxury deck, seen perfectly flat from the front and filling the whole picture from edge to edge. "
    "It belongs to the same deck as the attached cards: an ornate window with an arched top stands in the upper three quarters of the card, drawn with one bold dark outline and two fine metallic lines inside it, "
    "crowned by a small crest on the arch and ending in a small hanging pendant at its foot; the picture lives inside the window. "
    "Outside the window the ground carries a fine tone-on-tone pattern and delicate line ornament that runs off all four edges, no outer border line. "
    "The lowest fifth of the card, below the window, is darker and calm, with only the fine ground pattern, because a title will be printed there later. "
    "One small warm flame is the only warm colour in the whole card. "
)
NOFACE = " Nobody's face is drawn in detail; nobody is naked; no blood."

J = {}
# ---------- 种族牌：样张四张以外的八族（同一副牌，跟样张的人类、高等精灵、矮人、魔族放在一起） ----------
RACE = CARD + (
    "This is a kin card from the same deck as the attached kin cards. The palette: deep slate blue-black and dark slate, white stone and pale grey, pale gold line work, and one small warm amber flame. "
    "The whole card is cut by one clean diagonal line from the lower left to the upper right, darker on the upper left side, lighter on the lower right side, like the attached cards. "
    "Inside the window stands ONE full-length figure as a single flat silhouette, seen from the front, centred, filling about two thirds of the window height, "
    "drawn as a dark cut-paper shape on the light side and a pale one on the dark side so that it reads against both; only its outline tells who it is, no face detail. "
    "Behind the figure, a large round crest medallion drawn in pale gold lines, like a halo, holds the sign of this kin. "
)
RACE_REF = lambda: [webp_ref('race_dwarf', SAMPLE_AS), webp_ref('race_highelf', SAMPLE_AS), LOCK]
SAMPLE_AS = os.path.join(ROOT, '底稿', '门面', '第二轮', '样张_建档', 'assets')
J['race_halfling'] = (RACE + (
    "THE HALFLINGS. The figure: a small cheerful halfling about half the height of a human, curly hair, bare big feet, a short travelling coat with many pockets, a walking staff with a small bundle tied to it. "
    "The crest behind: a big wooden cart wheel with a sprig of clover through its spokes. Pendant at the foot: a small acorn cup."
), RACE_REF)
J['race_beastkin'] = (RACE + (
    "THE BEAST-EARED KIN. The figure: a slender young courier with tall pointed fox ears on the head and a big bushy fox tail, a short cape, a messenger satchel across the body, one hand holding a sealed letter. "
    "The crest behind: a running paw print inside a ring of eight small marks, with a sealed letter crossing it. Pendant at the foot: a small bell."
), RACE_REF)
J['race_halforc'] = (RACE + (
    "THE HALF-ORCS. The figure: a tall broad-shouldered half-orc with two short lower tusks, long hair in heavy braids, a fur mantle, a great double-bitted axe resting on the shoulder. "
    "The crest behind: a tall lineage tree whose roots and branches are split down the middle by a short stretch of wall, names-like small marks on its leaves. Pendant at the foot: a small tusk."
), RACE_REF)
J['race_dragonborn'] = (RACE + (
    "THE DRAGON-BLOODED. The figure: a human-shaped warrior with two short swept-back horns, scales along the cheekbones and the forearms, a long hooded cloak half pulled back, a spear held upright. "
    "The crest behind: a ring made of overlapping dragon scales around a jagged mountain ridge. Pendant at the foot: a single scale."
), RACE_REF)
J['race_truedragon'] = (RACE + (
    "THE TRUE DRAGON YOUNG. The figure: a young Western dragon, the size of a horse, sitting upright like a proud hound, bat-like wings half open, swept-back horns, a long tail curled around its feet. "
    "The crest behind: a ring of snowy mountain peaks around one great dragon eye with a slit pupil. Pendant at the foot: a small claw."
), RACE_REF)
J['race_tiefling'] = (RACE + (
    "THE TIEFLINGS. The figure: a slim young traveller with two curved horns rising from the brow, a thin long tail ending in a small spade, a long coat, one hand holding up a small lantern. "
    "The crest behind: a feather quill crossing a small pair of horns, as if writing a name, inside a ring of thin thorns. Pendant at the foot: a small quill nib."
), RACE_REF)
J['race_merfolk'] = (RACE + (
    "THE SEA-BORN. The figure: a graceful sea-born woman standing knee-deep in stylised waves, long wet flowing hair, thin fin-like frills along the forearms and behind the ears, gill marks on the side of the neck, a coral spear. "
    "The crest behind: a spiral shell above three curling waves with one small star. Pendant at the foot: a small pearl."
), RACE_REF)
J['race_custom'] = (RACE + (
    "THE KIN NOT YET WRITTEN. The figure: a human-sized figure drawn only as a dotted and dashed outline of pale gold light, empty inside so that the ground shows through, like a shape waiting to be filled in, "
    "with a few loose strokes of light drifting off it like unfinished pen lines. "
    "The crest behind: an empty ring with a feather quill laid across it and a small drop of ink. Pendant at the foot: a small ink drop."
), RACE_REF)

# ---------- 誓心九张 ----------
OATH = CARD + (
    "This is a vow card from the same deck as the attached soul cards. The palette: deep slate blue-black and ash grey, bone white, silver line work, and one small warm flame. "
    "Crest on the arch: a small open hand drawn in silver lines. Inside the window, one calm symbolic scene, few big shapes. "
)
OATH_REF = lambda: [webp_ref('soul_native', SAMPLE_AS), webp_ref('soul_reborn', SAMPLE_AS), LOCK]
J['oath_lg'] = (OATH + "The vow of LAWFUL GOOD: a tall plain knight's shield planted upright in the ground at the edge of a sleeping village of small houses; a small lantern with the warm flame hangs from the top of the shield; stars above. Pendant: a small shield.", OATH_REF)
J['oath_ng'] = (OATH + "The vow of NEUTRAL GOOD: on a wide road under the night sky, one pale hand reaches down and clasps the hand of a fallen traveller to help them up; a small campfire with the warm flame waits beside the road. Pendant: a small loaf of bread.", OATH_REF)
J['oath_cg'] = (OATH + "The vow of CHAOTIC GOOD: a heavy iron chain bursts open in the middle, its broken links flying apart and turning into a flock of small white birds that sweep up into the sky; a small flame burns at the break. Pendant: a small feather.", OATH_REF)
J['oath_ln'] = (OATH + "The vow of LAWFUL NEUTRAL: a large perfectly level balance scale standing on a stone step; on one pan a sealed scroll, on the other an iron key; a small oil lamp with the warm flame on the step below. Pendant: a small key.", OATH_REF)
J['oath_tn'] = (OATH + "The vow of TRUE NEUTRAL: a quiet still lake, one standing stone in the middle and its perfect reflection below, half the sky in pale dawn grey and half in starry night meeting in a clean vertical line, no sun, no moon and no crescent anywhere in the sky; one small flame floats above the stone. Pendant: a small hourglass.", OATH_REF)
J['oath_cn'] = (OATH + "The vow of CHAOTIC NEUTRAL: a weathervane spinning on top of a crooked signpost at a fork of many roads, leaves and a single tossed coin whirling in the wind around it; a small flame in a lantern swings from the signpost. Pendant: a small coin.", OATH_REF)
J['oath_le'] = (OATH + "The vow of LAWFUL EVIL: a tall iron gate with spikes, a heavy crown resting on a thick closed ledger in front of it, chains running from the ledger to the gate; one small cold-burning candle flame on the ledger. Pendant: a small padlock.", OATH_REF)
J['oath_ne'] = (OATH + "The vow of NEUTRAL EVIL: a smooth pale mask held up in front of a dark hooded shape, behind the mask the other hand hides a thin dagger and a small pouch of coins; one small candle flame in front. Pendant: a small mask.", OATH_REF)
J['oath_ce'] = (OATH + "The vow of CHAOTIC EVIL: a cracked grinning mask lies in a tangle of thorns, a torch with a wild ragged flame thrown down beside it, sparks flying, shapes of wolves howling in the dark around. Pendant: a small broken fang.", OATH_REF)

# ---------- 身份牌框：月银纪、纷争纪、迷宫纪、此刻（山铜纪样张有） ----------
ID_COMMON = (
    "Draw one tall 2:3 portrait picture, seen perfectly flat from the front and filling the whole picture: one identity plate that will hold a person's portrait and name. "
    "Composition that must be kept exactly like the attached stone panel: a small crest at the top centre; below it, in the upper half, a recessed arched niche about sixty percent of the width, its inside smooth, plain and EMPTY, slightly darker, where a portrait will be placed later; "
    "below the niche, a long horizontal empty band where a name will be written later; under it three shorter empty bands. All bands and the niche stay completely EMPTY. "
    "At the very bottom one small warm flame is the only warm colour. Flat frontal object drawn in the cut-paper manner: no letters, no numerals, no writing, no people. "
)
ID_REF = lambda: [webp_ref('id_bronze', SAMPLE_AS), LOCK]
J['id_moon'] = (ID_COMMON + (
    "This plate is a name board from the age of hearth fires and great beasts: one tall board of old dark wood, its grain showing, edges worn round, bound top and bottom with plaited leather cords strung with small bone beads; "
    "soot darkens the lower corners; the crest at the top is a small fire carved and inlaid with a fleck of pale silver; the niche is carved into the wood; the bands are smoothed strips of paler wood. "
    "Palette: deep night blue around, dark warm-grey wood, bone white, silver lines, and one small flame in a tiny clay bowl at the bottom."
), lambda: [webp_ref('id_bronze', SAMPLE_AS), LOCK, webp_ref('era_0')])
J['id_strife'] = (ID_COMMON + (
    "This plate is one page of the muster roll of the great wall: a sheet of thick rough grey-white war-report paper pinned to a slab of grey stone by four iron nails, its edges torn and singed; "
    "the niche is a square-arched frame ruled in charcoal; the bands are ruled charcoal lines; a broad red wax seal stamp sits empty at the upper right; the crest at the top is a small stretch of battlemented white wall. "
    "Palette: iron grey, pale stone white, faded dark red, charcoal, and one small flame of a beacon brazier at the bottom."
), lambda: [webp_ref('id_bronze', SAMPLE_AS), LOCK, webp_ref('era_1')])
J['id_maze'] = (ID_COMMON + (
    "This plate is an adventurers' guild travel seal card: a thick card of deep blue lacquer framed in worn bronze, small rivets at the corners; "
    "the crest at the top is a round bronze seal medallion bearing a small balance scale over a shaft going down into the earth; the niche is a recessed window rimmed with a thin gold line; the bands are recessed bronze slots. "
    "Palette: deep night blue, worn bronze and pale gold, and one small flame in a tiny lantern at the bottom."
), lambda: [webp_ref('id_bronze', SAMPLE_AS), LOCK, webp_ref('era_3')])
J['id_now'] = (ID_COMMON + (
    "This plate is a modern travel licence of an age of brass, steam and gaslight: a stiff card of deep blue enamel framed in polished brass with engraved fine borders and tiny screws, "
    "a punched ticket-stub edge along one side, a small brass gear and a rail line engraved along the bottom; the crest at the top is a small brass seal with a star over a winding rail line; "
    "the niche is a glass-covered window rimmed in brass; the bands are brass slots. Palette: deep night blue, warm brass and pale gold, cream paper, and one small flame in a tiny gas lamp at the bottom."
), lambda: [webp_ref('id_bronze', SAMPLE_AS), LOCK, webp_ref('era_3')])

# ---------- 手：点一下、掷骰子 ----------
HAND_REF = lambda: [os.path.join(OUT, 'hand_push.png'), os.path.join(SAMPLE, 'h9_take.png'), os.path.join(SAMPLE, 'h9_open.png')]
HAND_COMMON = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. "
    "The attached pictures are our approved drawings of this very hand: a young woman's right hand and forearm in a tight matte black glove whose fingertips taper into long slender needle-sharp black claws, "
    "with three long thin pale silver-white lines running along the back of the hand and down the forearm. Draw the same hand, the same glove, the same claws, the same silver lines, the same clean toon shading with thin crisp outlines "
    "and the same broad soft plane of muted cool grey light on one side with a thin pale rim of light, exactly as in the attached drawings. Nothing on the hand is red. "
    "Draw the hand with the correct anatomy of a real human hand, exactly five digits, smooth and elegant: no tendons, no veins, no wrinkles. "
    "The forearm rises from the bottom edge of the picture, roughly vertical, and is cut off cleanly by the bottom edge. "
)
J['hand_tap'] = (HAND_COMMON + (
    "The pose: seen from above, the hand is pointing down at a card lying on a table and tapping it once with the tip of the index finger: the index finger is extended and touches the card with its claw tip; "
    "the middle, ring and little fingers are curled loosely under the palm, the thumb relaxed at the side. "
    "The card is one flat rectangular card in portrait orientation, a flat pure green placeholder (exactly #00FF00, no shadow, no texture), lying flat above the fingertip, about as wide as the hand. "
    "Placement: the top edge of the card at about 4 percent of the picture height, the tapping fingertip at about 30 percent, the knuckles at about 45 percent, the wrist at about 62 percent. "
    "Nothing of the hand is tinted green; green appears nowhere except the card. Nothing else: no table, no body, no face, no hair, no background."
), HAND_REF)
J['hand_dice'] = (HAND_COMMON + (
    "The pose: seen from above, the hand has just flicked two dice onto a table: palm facing down, the fingers spread open and slightly lifted in a graceful releasing gesture, as if the dice just left them. "
    "Just beyond the fingertips, two small cubes tumble in the air, each a flat pure green placeholder (exactly #00FF00, no shadow, no texture, no pips), side by side, each about as big as a fingertip. "
    "Placement: the two cubes at about 10 percent of the picture height, the fingertips at about 26 percent, the knuckles at about 42 percent, the wrist at about 60 percent. "
    "Nothing of the hand is tinted green; green appears nowhere except the two cubes. Nothing else: no table, no body, no face, no hair, no background."
), HAND_REF)

# ---------- 命路纹章：两张，一张一格一枚 ----------
EMB = (
    "Draw one wide 3:2 landscape picture: a reference sheet of twelve round emblems for a luxury fantasy game, arranged in a precise grid of 4 columns and 3 rows, "
    "all emblems the same size, each centred in its own cell with generous empty space between them, on one plain flat even background of deep slate blue-black with no pattern and no texture. "
    "Every emblem is a round medallion: a thin double ring of pale gold foil line, inside it a deep indigo disc with a faint inner gradient, and in the middle one clear symbol drawn as pale bone-white cut-paper shapes with thin pale-gold echo lines; "
    "small warm amber touches only where a flame is named. All twelve share exactly the same ring design so they read as one set. "
    "Emblems, row by row from the top left: "
)
EMB_REF = lambda: [webp_ref('emblem_maze', os.path.join(ROOT, '底稿', '门面', '共用', 'assets', 'ui')), webp_ref('star_back', SAMPLE_AS), LOCK]
J['emb_a'] = (EMB + (
    "1 a great two-handed warhammer smashing through a cracked round shield; "
    "2 a heart wreathed in a small warm flame and ringed with thorns, a short axe beneath it; "
    "3 an armoured gauntlet gripping a broad sword whose blade carries a small glowing rune core; "
    "4 a long staff at the centre of a spiral of swirling wind, water and flame; "
    "5 an open eye inside a ring of rune marks above an open book; "
    "6 two open hands cradling one small warm flame under a faint halo; "
    "7 a sword of light pointing straight down through a small balance; "
    "8 a hooded cloak with no one inside dissolving into mist, faint footprints fading away; "
    "9 two slim daggers crossed over a black shadow shape and one small star; "
    "10 a smooth mask with three phantom blades fanning out behind it like reflections; "
    "11 a heavy longbow fully drawn, its arrow aimed at a far small star; "
    "12 a hunting bow and a long knife crossed over a pine tree and a track of pawprints."
), EMB_REF)
J['emb_b'] = (EMB + (
    "1 an arrow of glowing magic light crossing a woven net, a small falcon above it; "
    "2 a huge tower shield bearing the shape of a closed gate; "
    "3 two curved blades crossing inside a whirling ring like a dancer's turning step; "
    "4 a straight sword whose blade is inscribed with runes, set inside a rune circle; "
    "5 a clenched fist radiating long rays of aurora-like light; "
    "6 a balance scale holding a coin on one pan and a sealed contract on the other; "
    "7 a round cooking cauldron with a ladle over a small warm campfire, its steam curling into a star; "
    "8 a smith's hammer resting on an anvil, sparks rising in an arc like a bridge; "
    "9 a small glass vial with a sprouting green leaf on one side and a withered leaf on the other; "
    "10 an iron chain closed in a ring around a rolled vow scroll and a short iron rod; "
    "11 a pair of drafting dividers standing over a map of ruins with a small lens; "
    "12 an empty ring with a single feather quill laid across it."
), EMB_REF)

# ---------- 位阶徽记：一张六枚 ----------
J['tier_sheet'] = ((
    "Draw one wide 3:2 landscape picture: a reference sheet of six insignia of rank for a luxury fantasy game, arranged in a precise grid of 3 columns and 2 rows, all the same size, each centred in its own cell "
    "with generous empty space between them, on one plain flat even background of deep slate blue-black with no pattern and no texture. "
    "Each insignia is a round medallion with a pale gold foil ring; they grow clearly grander from the first to the sixth, in ring ornament, rays and glow, so the rank reads at a glance. "
    "Symbols drawn as pale bone-white cut-paper shapes with thin pale-gold echo lines, row by row from the top left: "
    "1 ORIGIN, the humblest: a single sprouting seed with one tiny warm spark above it, a plain thin ring; "
    "2 RESONANCE: a small ring with three concentric ripples spreading out like sound, a slightly finer ring; "
    "3 SOUL FORM: a faceted crystal standing upright with soft light inside, the ring now with small notches; "
    "4 PEAK: a sharp mountain summit with a small banner on top, the ring with small rays; "
    "5 HERO: a laurel wreath around an upright sword, the ring with longer rays and small stars; "
    "6 LEGEND, the grandest: a crown made of an eight-pointed radiant star, long fine rays fanning out beyond the ring all around, a faint glow, small orbiting stars. "
    "Only one small warm spark in the first and a warm core in the last; otherwise cool colours."
), EMB_REF)

# ---------- 前半生八章的小画：一章一张，通用，靠材质分纪 ----------
PLATE = (
    "Draw one wide 3:2 landscape picture: a small storybook vignette, a plate from the same storybook-style series as the first attached picture, simple and airy, few big shapes, lots of quiet space, "
    "cool limited palette of slate blue and bone white with pale gold lines, one small warm flame as the only warm accent. People are tiny simplified pale silhouettes without faces. Scene: "
)
PLATE_REF = lambda: [LOCK, webp_ref('soul_native', SAMPLE_AS)]
J['life_bones'] = (PLATE + "a newborn's tiny hand glowing softly in the middle, and around it in a wide ring the pale silhouettes of many kin of this world standing hand in hand: one with long pointed ears, one short and bearded, one with fox ears and a tail, one with horns, one with scales, one tall with tusks; a small flame at the very centre.", PLATE_REF)
J['life_birth'] = (PLATE + "night, a small house in a valley, in its doorway a pale silhouette of a mother lifting a swaddled newborn up toward one bright star; a thin thread of smoke from the chimney curls up to the star; a small warm window.", PLATE_REF)
J['life_home'] = (PLATE + "inside a simple home: a long table, tiny silhouettes of a family around a warm hearth, tools and a coat hanging on the wall, a cat by the fire, a window with a starry night outside.", PLATE_REF)
J['life_child'] = (PLATE + "a sunny meadow by a stream, two tiny children running along a winding path chasing a kite, one carrying a wooden sword, tall grass curving like waves around them, a small campfire far away on a hill.", PLATE_REF)
J['life_youth'] = (PLATE + "dusk in a courtyard, a lone youth practising alone with a weapon, a long shadow behind, an older figure watching quietly from a doorway with a lantern holding the small warm flame.", PLATE_REF)
J['life_path'] = (PLATE + "a crossroads on a hill with a tall signpost of many arms, each road curving away toward a different distant shape: a tower, a long wall, a dark forest, a mountain gate, a city of lights; a small figure stands at the post.", PLATE_REF)
J['life_depart'] = (PLATE + "dawn at the open gate of a small town, a young traveller with a pack and a walking staff stepping out onto a long road that unrolls like a ribbon to the horizon, a few tiny figures waving from the gate, a small warm lantern on the gatepost.", PLATE_REF)
J['life_end'] = (PLATE + "a large open book lying on a table, its pages curling up into the shape of a road and a doorway of soft light; a tiny figure walks out of the page toward the doorway; a small candle flame beside the book.", PLATE_REF)


def one(key):
    prompt, refs = J[key]
    style = '' if key.startswith('hand') else CARD_STYLE + F.WEST_PLAIN
    try:
        r = refs() if callable(refs) else refs
        extra = NOFACE if key.startswith(('race', 'oath', 'life')) else ''
        print('好了', key, gen(os.path.join(OUT, key), prompt + style + F.CLEAN + extra, refs=r), flush=True)
    except Exception as e:
        print('失败', key, str(e)[:300], flush=True)


if __name__ == '__main__':
    args = sys.argv[1:]
    keys = list(J) if args == ['all'] else [k for k in args if k in J]
    if not keys:
        print('键：', ' '.join(J))
        sys.exit(0)
    with ThreadPoolExecutor(int(os.environ.get('WORKERS', '3'))) as ex:
        list(ex.map(one, keys))
