#!/usr/bin/env python3
# 月银纪那一面长墙上的二十七幅壁画（门面·月银纪的书，11-12）。一个时代一幅，竖幅 2:3。
# 三种画法跟着年代走：十五歌是岩画（越往后越讲究），诸国期六幅是湿壁画，萨尔维斯六幅是月银漆的嵌线。
# 墙上的光（火把、地上的火、辉塔的永昼、最后一年的暗）是页面里算的，所以画一律要平光、不带明暗、四边留一圈同色的空墙好接缝。
#   python gpt_mural.py                 列出键
#   python gpt_mural.py m07 m20 m23     出这几幅（先出这三幅当定稿样，别的拿它们当参考）
#   MURAL_WORKERS=4 python gpt_mural.py all
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from gpt_gen import gen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "门面_壁画_11-12")

PLATE = (
    "Draw one tall 2:3 portrait picture: a flat, straight-on reproduction of one section of an ancient wall with a wall painting on it, "
    "like a museum plate of a mural photographed head-on in perfectly even light. The wall surface fills the whole picture from edge to edge: "
    "no room, no floor, no ceiling, no perspective, no frame around the picture, no cast shadows, no visible light source, no vignette, no darkened corners. "
    "The painting sits in the middle of the section. Toward all four edges it thins out and stops, leaving a band of bare wall of the same material "
    "and the same even colour all the way round, so that this section can be joined seamlessly to its neighbours on the same wall. "
)
COMPOSE = (
    " Composition: bold and simple, readable from far away. The one vast thing in the scene is drawn as a single great flat shape that curves around the small people; "
    "people are tiny. Leave plenty of wall unpainted."
)
# 画里没有庞然大物的那几幅用这一句：头一回 m20 用了上面那一句，它自己添了一条盘在画顶上的红龙
COMPOSE_PLAIN = (
    " Composition: bold and simple, readable from far away; people are small. Draw only what the subject names: do not add any dragon, beast or giant figure of your own. Leave plenty of wall unpainted."
)
PLAIN_KEYS = {"m15", "m16", "m17", "m18", "m20", "m22", "m23", "m24", "m25", "m26", "m27"}
# 只改一处的重画：拿上一稿当参考，别的都不动
FIX = {
    "m20": ("m20_v2.png",
            "Redraw the attached picture and keep everything about it exactly the same: the plaster wall, the two border bands, the seven kings with their seven swords and seven mantles, the armies and banners, the tent with its candle, "
            "the stepped platform, the goddess of pale light, the rivers, the sunset and the colours, the cracks and the worn edges, the framing and the size. Change one thing only: remove the red dragon completely. "
            "Where its body arched over the scene, the scene simply ends in a plain soft arched edge and above it is bare plaster like the rest of the wall. There is no dragon, no beast and no wing anywhere in the picture."),
}
NO_MOON = " There is no moon and no crescent anywhere in the picture."
CLEAN = " No text, no letters, no numerals, no runes that look like writing, no logo, no watermark, no signature."
WEST = (
    " The world is Western high fantasy with medieval Europe as its base. No East Asian motifs: no cloud spirals, no pagodas, no long serpentine dragons with antlers or whiskers. "
    "Dragons, if any, are heavy Western wyrms with bat-like wings. No crosses, no Christian symbols, no real-world heraldry."
)

CAVE = (
    "The wall is rough, dark, warm grey-brown limestone: a cave wall, matt, with shallow natural bumps and a few hairline cracks. "
    "The painting is a rock painting made with fingers, chewed twigs and pigment blown from the mouth: red ochre, yellow ochre, charcoal black and chalk white. "
    "The pigments sit rich and luminous against the dark rock, with soft blown halos round the stencilled shapes. Flat silhouettes, dots and strokes; no pen outlines, no shading, no perspective. "
    "People are tiny simple silhouettes with a little character in their poses. Somewhere in the painting there is one small fire, a plain flame shape painted in the brightest orange-red with a white-hot centre: it is the brightest spot on the wall. "
)
CAVE_1 = CAVE + "This is among the very oldest paintings on the wall: the hand is rough and direct, a few stencilled handprints sit near the lower edge of the painting. "
CAVE_2 = CAVE + (
    "This painting is some centuries younger than the oldest ones: the shapes are cleaner and more deliberate, rows of small repeated dots and chevrons run as borders above and below the scene, "
    "and two new pigments appear sparingly, a dull malachite green and a pale grey-blue. "
)
CAVE_3 = CAVE + (
    "This is one of the latest and finest of the rock paintings: the rock was smoothed and washed with a thin pale clay ground before painting, so the middle of the section is a little lighter than its bare edges; "
    "the figures are archaic and elegant, long-limbed, in profile, with thin dark contour lines; bands of simple wave and zigzag ornament run above and below the scene; "
    "pigments are ochre red, ochre yellow, black, white, malachite green and a little deep blue. Still flat, no shading. "
)
FRESCO = (
    "The wall is dressed stone covered with warm off-white lime plaster. The painting is a medieval European fresco in the Romanesque to early Gothic manner: "
    "flat figures with firm dark outlines, simplified drapery folds, calm stylised faces; earth pigments (red earth, yellow ochre, green earth, bone black, lime white) with accents of lapis blue and vermilion "
    "and a little worn gold leaf on crowns; a narrow painted border band of a simple repeating geometric pattern along the top and the bottom of the painting. "
    "The fresco is old: hairline cracks, colours slightly faded, small losses of plaster near the corners showing pale stone. No perspective, no modelling beyond flat tone. "
    "Gods, where they appear, are tall calm figures of pale light in plain robes, without faces, and without any halo, disc or rays behind the head. "
)
LACQUER = (
    "The wall is a panel of polished black-blue stone under dark lacquer. The picture on it is drawn in inlay: fine bright lines of a cool silver-white metal set flush into the dark lacquer, "
    "with thin flat fields of pale teal, pearl white and deep indigo, and tiny dots of white light. The drawing is precise, geometric and elegant, like a jeweller's engraving of a high arcane civilisation: "
    "perfect circles and rings, tall slender towers, fine straight radiating lines, small flat silver figures in profile. The silver lines seem to glow faintly from within. "
    "No warm colours at all unless stated. The panel is flawless: no cracks, no wear, no dust. A thin double silver line runs as a border well inside the edges; outside it is bare black-blue lacquer. "
)
SAME_WALL = (
    " The attached picture is an approved neighbouring section of this same wall. Match it exactly in the colour and texture of the bare wall, the pigments, the hand, "
    "the size of the figures and the level of finish; keep the same band of bare wall round the edges. Draw a different scene: do not copy its figures or its composition."
)

S = {}
S["m01"] = (CAVE_1, "Subject: a broken stone bridge over a frozen river; under its one remaining arch a small fire with a handful of tiny people huddled round it. "
            "From the fire a line of six tiny walking figures leads away up the wall across empty snow, the first of them a girl carrying a small pot of fire. "
            "Facing the fire from the far bank, an enormous wolf with a mane of snow, drawn as one great chalk-white silhouette curving over the whole scene, watching. Dots of falling snow.")
S["m02"] = (CAVE_1, "Subject: the gate of a small walled town. Before the gate lies an enormous lizard like a mountain ridge, moss on its back, drawn as one great flat dark shape curving along the bottom and up one side; "
            "its one visible eye is a huge disc of concentric white and black rings. All around stand dozens of tiny people painted solid chalk-white: people turned to stone, a town of statues. "
            "In front, one tiny young man walks backwards toward the beast, holding up a small round polished shield in which he watches it. At one edge a tiny boat and fishing nets drawn as hatched grids. One small fire on the shore.")
S["m03"] = (CAVE_1, "Subject: a shallow river ford in winter, the river a band of wavy white lines. At the ford stands a tall standing stone; one tiny warrior stands upright with his back to the stone, bound to it by a belt round his waist, spear in hand, "
            "and a black raven sits on the top of the stone. Facing him from the other bank an enormous woolly mammoth with long curved tusks and a hump of snow, drawn as one great pale silhouette filling the upper half, smaller mammoths behind it as overlapping curves. "
            "A long row of short tally strokes at the foot of the stone. Far behind the warrior, one small fire with a few tiny people.")
S["m04"] = (CAVE_1, "Subject: an enormous burrowing dragon, a heavy wingless wyrm, floating among clouds across the top of the painting and carrying a whole walled town with fields on its back. "
            "Beneath it one huge strong man wearing a spotted leopard pelt marked with small zigzag lightning strokes heaves upward with both arms, lifting the beast and its town; beside him a small youth holds up a burning torch. "
            "In a lower corner a tiny king peeks out of a big bronze jar, hiding. The torch is the one small fire.")
S["m05"] = (CAVE_1, "Subject: a hall-town on a white hill where everyone sleeps: dozens of tiny people lying down in rows, drawn as short horizontal strokes. Above the town hovers an enormous fire-salamander with glowing red wing membranes spread over half the town, "
            "a row of seven holes along its throat like a flute, wavy lines of music drifting down from it. In the middle one tiny boy stands upright, the only one awake, holding the point of a long spear pressed against his own brow. "
            "A white salmon painted in a small pool at the lower left. One small fire in the hall's hearth.")
S["m06"] = (CAVE_2, "Subject: a round hut with nine doors facing nine directions, drawn from above like a wheel, a hearth fire at its centre and two tiny figures, a man and a woman, inside. "
            "Around it the plain is scored with long black scorched furrows crossing each other like a net, ploughed by an enormous rhinoceros with one long red-hot horn, drawn as a great dark silhouette curving round the hut. "
            "At the lower right a small clear spring drawn as concentric rings; a wounded man lies exactly nine footprints away from it, and another figure walks toward him carrying water in two cupped hands, the water spilling in dots between the fingers.")
S["m07"] = (CAVE_2, "Subject: three small walled towns among fields of ripe wheat, the wheat drawn as rows of short yellow strokes bending in the wind. An enormous red dragon, a heavy Western wyrm with bat wings, lies along the top of a cliff across the upper part of the painting "
            "like a range of red-hot hills, wings half open so that half the sky is red. One tiny man with a sickle stands on the dragon's head driving half a broken sword down into its skull. Black dots of rain fall. "
            "One small fire at a town gate, where a tiny seated figure cuts tally marks.")
S["m08"] = (CAVE_2, "Subject: a long hall with one empty seat, drawn simply; below it a round pool painted solid charcoal black. Out of the pool crawls an enormous eyeless salamander with long thin limbs, painted in solid charcoal black like the pool itself with only a thin chalk-white outline (it is black, not red), its mouth opened wider than the hall's door, wavy lines of wailing coming from it."
            "Facing it stands a small stocky dwarf woman with two long copper-red braids, her bare hands raised to catch its jaws, a white bone sword hanging unused at her belt. In an upper corner a mountain with a sleeping fire inside it, a red dot. One small fire in the hall's hearth.")
S["m09"] = (CAVE_2, "Subject: a vast forest drawn as rows of tree shapes; above it an enormous bird whose spread wings cover the whole sky from edge to edge, one great dark flat shape with two huge round eyes; beneath it the forest is dim. "
            "On a row of white standing stones at the forest's edge a tiny long-eared archer draws a great longbow straight upward; the arrow already loosed is a long bright yellow-white line with a small sun disc at its tip, piercing the wing, and where it pierces, a shaft of light falls on the trees. One small fire in the archers' camp.")
S["m10"] = (CAVE_2, "Subject: a mountain range; on the highest peak stands an enormous white stag whose antlers branch across the whole upper painting like a bare forest, zigzag lightning strokes caught and coiled among the tines. Below, a forest painted chalk white. "
            "On the peak beside the stag's hooves one tiny man kneels with his mouth open to the sky, a zigzag of lightning going into his mouth; from the peak outward the sky clears in concentric rings. On the slope a small house with a tiny woman in its doorway, and one small fire before the house.")
S["m11"] = (CAVE_3, "Subject: a tiny rider on a white winged horse flying steeply upward toward the top of the painting above bands of cloud; the golden bridle has snapped and one long white feather drifts down behind them. "
            "Far below, at a shore where a red lava flow meets the sea on one side and pillars of lightning strike the sea on the other, crouches a three-headed chimera, a lion's head, a horned goat's head and a snake for a tail, drawn as one great dark shape in white steam. "
            "In a lower corner a tiny messenger holds a sealed letter. One small fire on the shore.")
S["m12"] = (CAVE_3, "Subject: a harbour city inside a bay whose two reefs close like two hands. The city is sinking: the sea, drawn as rows of wave lines, has risen over the houses, and under the water rows of small lamps still burn in the windows. "
            "On the last tower above the water a tiny girl stands singing, a crown of white pearls on her head, lines of song rising from her mouth. Outside the bay the back of an enormous sea beast rises like a reef half the width of the painting, answering lines of song rising from it. "
            "A few pearl divers' boats. The small lamps under the water are the warm lights of this painting.")
S["m13"] = (CAVE_3, "Subject: the sea covered in fog, the fog drawn as soft pale blown-pigment clouds. In it an island that is really the back of an enormous whale, with grass, birds and a few ships tied to it, one huge eye half open under the waterline. "
            "A tiny boat with one man sails away from it; a long rope runs right across the painting from the boat, tied in a long row of different knots. At the far end of the rope, on a hillside, a small house with a lamp lit by its door and a tiny woman waiting. "
            "A leather waterskin painted beside the boat. The lamp by the door is the one small warm light.")
S["m14"] = (CAVE_3, "Subject: a wide dark plain with a dozen small walled towns whose fires have all gone out, each a black smudge. An enormous wild boar taller than a town gate, its mane a row of standing stone spikes, its tusks like two ploughs, "
            "drawn as a great dark shape rooting across the plain and trampling the fires out. Only at the east gate of the last town one fire still burns, with seven tiny armed figures and one old man tending it. "
            "In a lower corner a mother sits holding a small wooden box in which lies one half-burnt log. Slanting strokes of rain.")
S["m15"] = (CAVE_3, "Subject: a white-stone plain at the very end of the night. Eleven tiny kings, each holding a small lamp, stand in a ring around a plain gold circlet that rests on a white stone; one of them bows his head to it. "
            "At the right, by a town's east gate, an old man sits tending a small fire. Above them, across the whole top of the painting, the sun rises for the first time: a great pale gold disc with long straight rays like a crown, laid in real gold leaf, "
            "and the upper part of the wall itself is washed lighter by it. There are no beasts in this painting.")
S["m16"] = (FRESCO, "Subject: an island at the meeting of three rivers, terraced with dozens of small stone altars. On a few of the altars sit tall pale robed gods; most altars are still empty. "
            "On the steps in front a small woman with a grave-digger's spade beside her kneels and cuts tally marks into a step with a chisel, and a line of plain people waits behind her. "
            "Early morning: pale gold and rose light, long thin rays coming from the upper left.")
S["m17"] = (FRESCO, "Subject: high noon over a roaring chasm with waterfalls; a single narrow stone bridge spans it. On the bridge one stocky dwarf warrior with a great red-hot shield stands alone, feet planted, holding back a whole column of beasts and raiders pressing from the far side. "
            "Behind him a boy runs back along the bridge to fetch help. Forges with small fires are cut into the cliff wall. Two deep footprints are sunk into the stone under the dwarf's feet. Bright even midday light, white sky.")
S["m18"] = (FRESCO, "Subject: a walled town among wheat fields in the long afternoon; its gate stands open and the gatekeeper beckons in a lone dusty traveller who has come by the road. "
            "In the lower register, on a green slope, two tribes of beast-eared hunters face each other with bows, and both rows lower their bows to the ground, because between them one exhausted messenger woman kneels. "
            "Warm afternoon light, long soft shadows.")
S["m19"] = (FRESCO, "Subject: a paved royal road running through a town. An ancient dragon, a heavy Western wyrm that has lain across the road for eleven years with moss on its back, now rises and spreads its wings to leave, filling the upper half of the painting. "
            "In front of it a small girl with faint scales at her temple sits calmly on the road, an account book in her lap. Townspeople and stopped wagons watch from both ends of the road. "
            "Early evening, amber light; the first snowflakes begin to fall from the top.")
S["m20"] = (FRESCO, "Subject: sunset. On an island where three rivers meet stands a round stepped altar platform. Exactly seven crowned kings, no more and no fewer (seven crowns, seven swords, seven mantles of seven different colours: red, yellow, blue, white, orange, green and violet), stand in a half ring around its foot, each holding out a sword hilt first to lay it down, none yet stepping up; "
            "their seven armies are small rows of spear points and banners behind them. Upon the platform a soft radiance: a goddess of pale light just taking shape, a tall slender woman's figure in a plain robe, faceless, with no halo, one hand raised as if asking a question. "
            "In a lower corner, between the armies, a small field tent with one white candle burning at its door. Deep amber and rose dusk light, violet shadows.")
S["m21"] = (FRESCO, "Subject: night. A quarry valley with white cliffs; a huge-backed quarryman walks bent double carrying an entire white mountain on his shoulders, a rope across his chest, a staff in his hand, tiny villagers passing safely beneath the mountain he holds up. "
            "In the lower register a man in broken shackles walks through seven concentric town walls toward an empty throne. A bell hangs in a small tower at the top. Deep blue night; the only warm lights are a few small candles and lanterns.")
S["m22"] = (LACQUER, "Subject: a narrow valley between two sheer cliffs leading to a great stone gate set in a ring of mountains. In the valley a forge, and from it a hundred small rings linked in one long chain winding across the panel, each ring finely engraved with tiny marks. "
            "People queue before the gate. In the lower part the doors of a great granary are thrown open to a crowd carrying sacks. Here alone there is one small warm light: the forge fire, a tiny inlay of copper orange.")
S["m23"] = (LACQUER, "Subject: a city in a basin ringed by mountains. From its centre rises one impossibly tall, slender white tower with a brilliant star-like light at its top; fine straight rays radiate from the light, and beneath it a great dome of pale daylight covers the city and pushes back the darkness, "
            "the edge of the dome drawn as one precise arc. Along a street under the dome a row of small lamps is lit. Beyond, across the upper part, more and more slender towers recede toward the horizon, each with its dot of light. Outside the arc, in the dark, tiny figures look in.")
S["m24"] = (LACQUER, "Subject: a mountain peak cut off and turned upside down, floating point-down in the sky; on its flat top a white city of colonnades and domes where one long banquet table runs the length of a hall, tiny guests seated along it, lamps like strings of pearls. "
            "Far below it on the ground lies a great city where three rivers meet. In the lowest part of the panel, on a field of ice, a few tiny old heroes lay their swords down on the ground. Thin vertical lines of light join the floating city to the towers below.")
S["m25"] = (LACQUER, "Subject: at the left, the precise arc edge of a dome of tower light with a slender tower inside it and notices nailed to the tower's base. From under the dome a long file of tiny horned people, men, women and children with bundles, walks out along a road that winds to the right and downward across the panel into the dark, "
            "toward a deep rift valley drawn as stacked cliffs. At the head of the file a horned woman carries a child. Inside the light the lines are bright silver; outside it the figures are drawn in a dimmer grey silver.")
S["m26"] = (LACQUER, "Subject: at the top, a high palace of slender towers floating above a ring of mountains. From a deep rift valley at the lower left a small party of horned envoys carries a scroll up a long road; the scroll is shown unrolled as seven plain parallel engraved lines. "
            "From the palace one small sealed tablet comes back down. In the lower right, on an open plain at first light, seven tiny figures of seven different peoples, one horned, one long-eared, one stocky and bearded, one with beast ears, one very small, one scaled, one plain human, "
            "stand in a row behind a low earth bank facing an oncoming wave of dark shapes.")
S["m27"] = (LACQUER, "Subject: seen from above, a whole imperial capital laid out as one vast perfect ring: concentric circles and radiating streets, a crown of slender towers all round the rim, an upper city floating above the ring of mountains. "
            "At the exact centre of the ring stands one tiny robed figure, alone, seen from behind, looking up. Ten small towers form an inner circle around him. The sky above is empty. This is the most ornate and precise panel of the whole wall: every line perfect.")

ANCHOR = {"cave": "m07", "fresco": "m20", "lacquer": "m23"}


def kind(key):
    n = int(key[1:])
    return "cave" if n <= 15 else "fresco" if n <= 21 else "lacquer"


def one(key):
    style, subject = S[key]
    a = ANCHOR[kind(key)]
    refs, same = [], ""
    if key in FIX and os.path.exists(os.path.join(OUT, FIX[key][0])):
        try:
            out = gen(os.path.join(OUT, key), FIX[key][1] + NO_MOON + CLEAN, refs=[os.path.join(OUT, FIX[key][0])])
            print("好了（只改一处）", key, out)
        except Exception as e:
            print("失败", key, e)
        return
    if key != a:
        p = os.path.join(OUT, a + ".png")
        if not os.path.exists(p):
            print("失败", key, "定稿样还没出：", a)
            return
        refs, same = [p], SAME_WALL
    try:
        os.makedirs(OUT, exist_ok=True)
        out = gen(os.path.join(OUT, key), PLATE + style + subject + (COMPOSE_PLAIN if key in PLAIN_KEYS else COMPOSE) + same + NO_MOON + WEST + CLEAN, refs=refs)
        print("好了", key, out)
    except Exception as e:
        print("失败", key, e)


if __name__ == "__main__":
    keys = sys.argv[1:]
    if keys == ["all"]:
        keys = sorted(S)
    keys = [k for k in keys if k in S]
    if not keys:
        print("键：", " ".join(sorted(S)))
        sys.exit(0)
    with ThreadPoolExecutor(int(os.environ.get("MURAL_WORKERS", "3"))) as ex:
        list(ex.map(one, keys))
