#!/usr/bin/env python3
# 建档样张（门面第二轮，11-23）要的图：三张魂牌、四族种族牌、五档命星牌面、星牌牌背、山铜纪身份牌框、若娜瓦的手两种姿势。
#   CODEX_HOME=C:/Users/waitl/.codex_b <ComfyUI 的 python> 底稿/门面/第二轮/样张_建档/gen_art.py [键…]   不带键列出有哪些
# 出在 out/门面第二轮/建档/<键>.png，已有的跳过。画法照 gpt_front.py 的定稿样 t2 和大幅牌背 bb_ 那一路。
# 手照 hand9 那一套（h9_take、h9_open 当第一张参考），牌画成纯绿占位，出完拿 prep_art.py 抠掉。
import os
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

OUT = os.path.join(ROOT, 'out', '门面第二轮', '建档')
REFD = os.path.join(OUT, 'ref')
SAMPLE = os.path.join(COMFY, 'out', '门面_小样_11-10')
LOCK = F.LOCK


def webp_ref(name):
    """外壳 assets 里的 webp 转成 png 当参考。"""
    from PIL import Image
    os.makedirs(REFD, exist_ok=True)
    dst = os.path.join(REFD, name + '.png')
    if not os.path.exists(dst):
        Image.open(os.path.join(ROOT, '底稿', '门面', '小样_外壳', 'assets', name + '.webp')).save(dst)
    return dst


CARD_STYLE = (
    " Drawing manner: the same hand as the attached pictures, which are approved cards and the approved style sample of this series: flat cut-paper colour shapes layered one over another, "
    "big flowing curves, thin lighter echo lines along the edges of the big shapes, soft inner gradients only, a fine paper grain over everything; metallic lines look like foil stamped on matte paper. "
    "Calm and clear: big simple shapes first, fine line detail second, quiet ground between them. Figures, if any, are simplified pale cut-paper silhouettes without detailed faces. "
    "No dense filigree, no gothic tracery, no heraldic shields, no realistic lighting, no heavy painterly rendering, no 3D render."
)
CARD = (
    "Draw one tall 2:3 portrait picture: the face of one fortune-telling card from a luxury deck, seen perfectly flat from the front and filling the whole picture from edge to edge. "
    "It belongs to the same deck as the attached card backs: an ornate window with an arched top stands in the upper three quarters of the card, drawn with one bold dark outline and two fine metallic lines inside it, "
    "crowned by a small crest on the arch and ending in a small hanging pendant at its foot; the picture lives inside the window. "
    "Outside the window the ground carries a fine tone-on-tone pattern and delicate line ornament that runs off all four edges, no outer border line. "
    "The lowest fifth of the card, below the window, is darker and calm, with only the fine ground pattern, because a title will be printed there later. "
    "One small warm flame is the only warm colour in the whole card. "
)
NOFACE = " Nobody's face is drawn in detail; nobody is naked; no blood."

SOUL = CARD + (
    "The palette of these three soul cards: deep slate blue-black and ash grey, bone white, silver line work, and one small warm flame. "
    "Crest on the arch: a small closed eye shape drawn in silver lines. "
)
J = {}
J['soul_native'] = (SOUL + (
    "This card is THE SOUL BORN IN THIS WORLD. Inside the window: night in a valley of tall standing stones; in the middle a small stone house with one window lit warm by a hearth; "
    "in the doorway the pale silhouette of a mother holding a swaddled newborn against her shoulder; from the chimney a thin S-curve of smoke rises and becomes a thread of tiny stars that ends in one bright star at the top of the arch. "
    "Big pale cut-paper shapes of hills and rain clouds curve around the house like a cradle. Pendant at the foot: a small acorn."
), [webp_ref('bb_2'), LOCK, webp_ref('era_2')])
J['soul_reborn'] = (SOUL + (
    "This card is THE SOUL REBORN WITH ITS MEMORIES. Inside the window: in the upper half a tall pale translucent silhouette of an adult kneels with head bowed, its body dissolving from the feet into a long ribbon of pale light; "
    "the ribbon spirals down through the window like a falling leaf and pours into a small wooden cradle at the bottom, where one tiny warm flame glows on the blanket. "
    "Between them an open book floats with its pages turning into small birds that fly down along the ribbon. Concentric rings and a slow spiral fill the ground of the window. Pendant at the foot: a small spiral shell."
), [webp_ref('bb_2'), LOCK, webp_ref('bb_3')])
J['soul_isekai'] = (SOUL + (
    "This card is THE SOUL THAT FALLS IN WHOLE, BODY AND ALL. Inside the window: the sky is torn open at the top by one jagged rift full of strange tiny stars of another sky; "
    "through it falls a small pale silhouette of a young traveller in ordinary clothes with a shoulder bag, falling head first with arms open, a coat flapping, a few small belongings tumbling beside them. "
    "Below spreads the wide land of this world in layered cut-paper ridges, a white wall and a field of standing stones far away, and one small warm campfire where the traveller will land. "
    "Long trails of light follow the fall in a great S-curve. Pendant at the foot: a small falling star."
), [webp_ref('bb_2'), LOCK, webp_ref('era_2')])

RACE = CARD + (
    "This is a kin card of the age of the two kings. The palette: obsidian black and dark slate, white stone and pale grey, pale gold line work, and one small warm amber flame. "
    "The whole card is cut by one clean diagonal line from the lower left to the upper right, darker on the upper left side, lighter on the lower right side, like the attached card back. "
    "Inside the window stands ONE full-length figure as a single flat silhouette, seen from the front, centred, filling about two thirds of the window height, "
    "drawn as a dark cut-paper shape on the light side and a pale one on the dark side so that it reads against both; only its outline tells who it is, no face detail. "
    "Behind the figure, a large round crest medallion drawn in pale gold lines, like a halo, holds the sign of this kin. "
)
J['race_human'] = (RACE + (
    "THE HUMANS. The figure: a young human in a plain travelling cloak with a longsword at the hip and a short spear held upright, ordinary human proportions, round ears, short hair. "
    "The crest behind: a rising half sun over a short stretch of battlemented wall, with one ear of wheat crossed by one sword. Pendant at the foot: a small ear of wheat."
), [webp_ref('bb_2'), LOCK, webp_ref('back_2')])
J['race_highelf'] = (RACE + (
    "THE HIGH ELVES. The figure: a tall slender elf with very long pointed ears and very long straight hair falling to the knees, a long robe, holding a tall slender bow. "
    "The crest behind: a tall tree whose branches form a ring, with one six-pointed star in its crown and a closed gate at its roots. Pendant at the foot: a small leaf."
), [webp_ref('bb_2'), LOCK, webp_ref('back_2')])
J['race_dwarf'] = (RACE + (
    "THE DWARVES. The figure: a short, broad, stocky dwarf, about half the height of the human card figures, with a long braided beard reaching the belt, a heavy apron over mail, a smith's hammer on the shoulder. "
    "The crest behind: an anvil with a flame above it and two crossed hammers, inside a ring of small cog teeth. Pendant at the foot: a small hammer."
), [webp_ref('bb_2'), LOCK, webp_ref('back_2')])
J['race_demon'] = (RACE + (
    "THE DEMON KIN OF THE FLAME HORNS. The figure: a tall powerful demon warrior of humanoid shape with two great curved horns sweeping back from the brow, the tips of the horns burning with small flames, "
    "a long tail, a heavy greatsword planted point down before the feet, a ragged cloak. "
    "The crest behind: a pair of curved horns cradling a flame, inside a ring of thin thorns. Pendant at the foot: a small horn."
), [webp_ref('bb_2'), LOCK, webp_ref('back_2')])

STAR = (
    "Draw one tall 2:3 portrait picture: the face of one fate-star card from a luxury fantasy deck, seen perfectly flat from the front, filling the whole picture from edge to edge. "
    "The card is a frame only: the central field, about seventy percent of the card width and sixty-five percent of its height, centred slightly above the middle, is an EMPTY plain smooth panel of dark ink colour with only a very faint paper grain, "
    "nothing drawn in it, because the name and the text will be printed there later. "
    "Around the field runs the ornamental frame of this rarity; at the top centre of the frame sits a small medallion holding the star sign of this rarity; at the bottom centre a small plain cartouche, empty. "
)
STAR_REF = lambda: [webp_ref('bb_2'), LOCK, webp_ref('back_2')]
J['star_normal'] = (STAR + (
    "Rarity NORMAL, the humblest: a plain thin frame of grey stone colour, one single thin pale line, small square corners, no ornament at all, the medallion is a plain round dot. Ground of the border: matte ash grey. "
    "Muted and modest, almost bare."
), STAR_REF)
J['star_rare'] = (STAR + (
    "Rarity RARE: a clean frame of cool silver blue on deep slate blue, two thin parallel silver lines, small rounded corner flourishes, the medallion holds one small four-pointed star. "
    "Neat and quiet, slightly richer than a plain card."
), STAR_REF)
J['star_epic'] = (STAR + (
    "Rarity EPIC: a frame of deep violet and amethyst on dark plum, three fine lines in pale lilac silver, slender curling stems in the corners, a scatter of tiny stars along the frame, "
    "the medallion holds a six-pointed star with short rays. Rich and elegant."
), STAR_REF)
J['star_legend'] = (STAR + (
    "Rarity LEGEND: a grand frame of pale gold foil on deep midnight blue, an arched top, laurel-like stems climbing both sides, fine rays fanning out behind the medallion, "
    "which holds an eight-pointed golden star with a soft glow. Precious and radiant, clearly a high rank."
), STAR_REF)
J['star_unique'] = (STAR + (
    "Rarity UNIQUE, the one of a kind, which must look utterly different from every other card at first glance: the frame is not metal but light. "
    "A pure white blazing star at the top centre breaks through the frame and the edge of the card, and from it long sharp rays of white, pale gold and faint prismatic colour (pale cyan, pale rose, pale gold) shoot out across the whole border; "
    "the border ground is the black of deep space strewn with many tiny stars and thin concentric orbit rings; a thin ring of white fire runs all around the central field; "
    "small shards of the frame float loose at the corners as if the card cannot hold what it carries. The central field itself stays empty and dark."
), STAR_REF)
J['star_back'] = (
    "Draw one tall 2:3 portrait picture: the back of a fate-star card from the same luxury deck as the attached card backs, seen perfectly flat from the front and filling the whole picture from edge to edge. "
    "Ground: deep midnight blue turning to obsidian black. Metallic line colour: pale gold. The design is mirror-symmetrical: a large star chart of thin concentric circles, dotted orbit lines and tick marks, "
    "with one eight-pointed star in the very centre and a small warm flame at its heart; seven smaller four-pointed stars around it on a ring; fine ground pattern of tiny stars and dots running off all four edges, no outer border line. "
    "Flat ornamental emblem: no scene, no people, no letters.", lambda: [webp_ref('bb_2'), webp_ref('bb_3'), LOCK])

J['id_bronze'] = (
    "Draw one tall 2:3 portrait picture, seen perfectly flat from the front and filling the whole picture: one carved panel cut out of a tall mercenary memorial stele, where the name of one sword-for-hire is carved. "
    "The stele is stone split by one clean diagonal from the lower left to the upper right: polished obsidian black on the upper left, white limestone on the lower right, like the attached card back. "
    "Composition: the top is a carved round arch with a small crest of a plain sword point down between two small standing stones, in pale gold inlay. "
    "Below the arch, in the upper half, a recessed arched niche about sixty percent of the width, its inside smooth, plain and EMPTY, slightly darker, where a portrait will be placed later. "
    "Below the niche, a long horizontal recessed band, smooth and EMPTY, where a name will be carved later; under it three shorter empty recessed bands. "
    "Fine carved border lines in the stone, a few hairline cracks, small chips at the edges, worn soft corners; a thin line of pale gold inlay runs around the niche; "
    "at the very bottom a small warm amber flame carved and glowing in a little cup of stone, the only warm colour. "
    "Flat frontal stone relief drawn in the cut-paper manner: no letters, no numerals, no writing, no people.", lambda: [webp_ref('bb_2'), LOCK, webp_ref('era_2')])

HAND_REF = lambda: [os.path.join(SAMPLE, 'h9_take.png'), os.path.join(SAMPLE, 'h9_open.png')]
HAND_COMMON = (
    "Draw one tall 2:3 portrait picture on a fully transparent background. "
    "The two attached pictures are our approved drawings of this very hand: a young woman's right hand and forearm in a tight matte black glove whose fingertips taper into long slender needle-sharp black claws, "
    "with three long thin pale silver-white lines running along the back of the hand and down the forearm. Draw the same hand, the same glove, the same claws, the same silver lines, the same clean toon shading with thin crisp outlines "
    "and the same broad soft plane of muted cool grey light on one side with a thin pale rim of light, exactly as in the attached drawings. Nothing on the hand is red. "
    "Draw the hand with the correct anatomy of a real human hand, exactly five digits, smooth and elegant: no tendons, no veins, no wrinkles. "
    "The forearm rises from the bottom edge of the picture, roughly vertical, and is cut off cleanly by the bottom edge. "
)
J['hand_push'] = (HAND_COMMON + (
    "The pose: the hand lies flat and relaxed, palm down, seen from straight above, as if resting on a table top, its fingers pointing up in the picture. "
    "Just above the fingertips lies one flat rectangular card in portrait orientation, a flat pure green placeholder (exactly #00FF00, no shadow, no texture), about as wide as the hand, lying flat on the invisible table. "
    "The pads of the index and middle finger rest on the lower part of the card, pressing lightly and sliding it forward, away from the wrist; their claws lie on the green card. "
    "The ring and little finger are relaxed and slightly curled beside them, the thumb relaxed on the left side, clearly separated. "
    "Placement: the top edge of the card at about 6 percent of the picture height, the fingertips at about 30 percent, the knuckles at about 45 percent, the wrist at about 60 percent. "
    "Nothing of the hand is tinted green; green appears nowhere except the card. Nothing else: no table, no body, no face, no hair, no background."
), HAND_REF)
J['hand_flip'] = (HAND_COMMON + (
    "The pose: the hand is turning a card over. The card is one flat rectangular card, a flat pure green placeholder (exactly #00FF00, no shadow, no texture), standing up on its long lower edge, tilted toward us like a page being turned. "
    "The thumb is tucked under the card's right edge lifting it, and the tips of the index and middle finger lie on the card's upper corner guiding it over; ring and little finger curl gracefully away. "
    "The wrist is turned slightly so that we see the hand from the back and the side, elegant like a dealer turning a card. "
    "Placement: the card fills the upper third of the picture, the hand the middle, the forearm runs down to the bottom edge. "
    "Nothing of the hand is tinted green; green appears nowhere except the card. Nothing else: no table, no body, no face, no hair, no background."
), HAND_REF)


def one(key):
    prompt, refs = J[key]
    style = '' if key.startswith('hand') else CARD_STYLE + F.WEST_PLAIN
    try:
        r = refs() if callable(refs) else refs
        print('好了', key, gen(os.path.join(OUT, key), prompt + style + F.CLEAN + (NOFACE if key.startswith(('soul', 'race')) else ''), refs=r), flush=True)
    except Exception as e:
        print('失败', key, str(e)[:300], flush=True)


if __name__ == '__main__':
    keys = [k for k in sys.argv[1:] if k in J]
    if not keys:
        print('键：', ' '.join(J))
        sys.exit(0)
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(int(os.environ.get('WORKERS', '3'))) as ex:
        list(ex.map(one, keys))
