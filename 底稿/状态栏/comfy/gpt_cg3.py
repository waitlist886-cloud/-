#!/usr/bin/env python3
# 门面第三本书（山铜纪）用的图，都出在 out/门面_原画_山铜纪/（不进库）。样子照 门面重做_方向稿.md 第二十七节，画风照第五节。
#   tpl    空碑样板四张：t_bronze 山铜铸的碑，t_white 白石碑，t_obsidian 黑曜碑，t_border 界碑（白石黑曜背靠背铆着）。竖幅 2:3，透明底，碑面平而空。
#   stele  碑三十六块（b01 到 b36，照 山铜纪/山铜纪_碑_第一版.md 的次序，三十五块加无字碑），各拿它那一种样板当第一张参考，碑面照旧空着，字是页面刻上去的。
#   road   长卷十二段（r01 到 r12，一页两段，横幅 3:2）。从高处斜着看长垒，白石的墙从左到右贯穿，画面上半是墙西、下半是墙东。
#          墙在每一段左右两边出入的高度写死（墙脚 47%、垛口 39%），墙北贴着墙一条空地（30% 到 38%），墙南一条更宽的空地（50% 到 69%），留给页面立碑。
#          r02 起每一段拿左边那一段当参考，接缝照它接，所以长卷要一段一段按次序出（ROAD_SEQ=1 时 road 那一类自动排成一条）。
#   era    时代原画六幅（e1 到 e6，一页一幅，横幅 3:2，门面那一路的画法）。
#   hor    远景七张（h1 到 h7，11-14 改成往前走的路以后要的）：一页一张路尽头的天和地平线，h7 是 947 年归寂月最后一夜，地平线在图高六成，下面一片薄雾地。
#   walk   人物立牌六张（w_bal_1..3 巴尔缇娜小时候、少女、成年，w_sor_1..3 索恩薇娅少年兵、军官、白衣），透明底、从正背后看往前走；
#          先出 w_bal_3 w_sor_3，再出另外四张；--wnorm 照身高缩到同一个比例（原图留作 _raw）。
#   join   长卷接缝的补（j01 到 j11，第 n 道是 rNN 和下一段之间），接不上的才用：--cut jNN 切底，出 jNN，--merge jNN 并回两段；
#          东西接上了、只差明暗的用 --tone jNN（不重画，两边往中间的颜色靠）。
#   python gpt_cg3.py t_bronze r01 e1        出这几幅（出过的跳过）
#   python gpt_cg3.py tpl|stele|road|era     出这一类的全部
#   python gpt_cg3.py --left [tpl|stele|road|era]   还缺哪几幅
#   CG_DRY=1 只打提示词和参考图，不出图；CG_WORKERS=3 并着出（road 那一类照旧一段一段排着出）
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_cg as G  # noqa: E402
import gpt_front as F  # noqa: E402
from gpt_gen import gen  # noqa: E402

OUT = os.path.join(HERE, 'out', '门面_原画_山铜纪')
K3B = os.path.join(HERE, 'out', '门面_主画_11-10', 'k3b.png')          # 山铜纪主画：颜色和这一纪的手法照它
BB2 = os.path.join(HERE, 'out', '门面_小样_11-10', 'bb3_2.png')        # 山铜纪的大幅牌背（用户认过的牌背版）
R04 = os.path.join(HERE, 'out', '门面_原画_纷争纪', 'r04.png')         # 纷争纪长卷认过的一段：鸟瞰的视角和手法照它，别的不拿
PVD = G.PVD                                                              # 片头月银纪那六幅

NO_MOON = ' There is no moon and no crescent anywhere in the picture.'
NO_ARC = (' Nothing pale and curved may stand alone against the sky where it could be read as a crescent: horns are short and straight or branching, '
          'and no bow, blade or arc of light is drawn as a single pale curve in the sky.')
PEOPLE = (' Any people are tiny and simple, with natural human proportions, each with exactly two arms and two legs, standing or walking plainly; no close-ups and no faces in detail.')
PALETTE = ('Palette of this age: obsidian black, white stone, slate and soft lavender grey, the dark bronze-gold of cast orichalcum, and amber dawn light; '
           'small warm orange only for fires and lamps. ')
GRAIN = 'a fine paper grain like the grain of a stone rubbing over everything'

# ---------- 空碑样板 ----------
STELE_SHAPE = ("one standing memorial stele seen perfectly flat from the front, alone in the middle of the canvas, with clear empty transparent margin on every side. "
               "It is a tall upright slab about half the canvas wide and seven tenths of the canvas tall, slightly narrower at the top than at the foot, with a shallow round-arched top; "
               "it stands on a low plain two-step plinth whose bottom edge is about one tenth of the canvas above the bottom of the canvas. "
               "A narrow plain raised border runs round the front, and inside the border the front face is ONE large flat smooth panel that is completely blank: "
               "no letters, no runes, no symbols, no carving, no ornament, no crack and no stain on it. Leave the face empty and evenly lit, because words will be engraved on it later. "
               "Nothing at all stands in front of the face or covers any part of it. ")
STELE_STYLE = (" Drawing manner: flat stylized game illustration in the hand of the attached plates of this series: clean flat colour shapes with crisp edges, simple two-step shading, "
               "thin lighter echo lines along the edges, soft inner gradients only, " + GRAIN + ". Matte, no glare, no realistic rendering, no 3D render. "
               "The stele is lit evenly from the front with a slightly brighter left edge. Take only the drawing manner and the colours from the attached plates, never their compositions, figures or symbols.")
MATERIAL = {
    'bronze': ("Material: cast orichalcum, an old bronze-gold metal: dark golden brown with a soft green-grey patina settling into the border and the plinth, "
               "a dull warm sheen along the edges, like a weathered bronze plaque; the face is the same metal, smooth and dull. "),
    'white': ("Material: pale white limestone, the same stone as a great white wall: cool grey shading, a little weathering on the edges, the face smooth and pale. "),
    'obsidian': ("Material: black volcanic glass: very dark, almost black, with a faint purple-grey sheen along the edges and corners, drawn flat and matte; the face smooth and dark. "),
    'border': ("Material: two slabs set back to back. The front slab is pale white limestone, the same stone as a great white wall; directly behind it stands a slightly larger slab of black volcanic glass, "
               "so that a thin black rim of it shows all round the white one. The two are clamped together by two short straps of dark bronze-gold metal on each side edge, "
               "with large round rivets; the straps hold only the side edges and never cross the white face. "),
}
TPL_LEAD = "Draw one tall 2:3 portrait picture on a fully transparent background: "
TPL = {'t_bronze': 'bronze', 't_white': 'white', 't_obsidian': 'obsidian', 't_border': 'border'}

# ---------- 碑三十六块 ----------
# 次序照 山铜纪_碑_第一版.md；样板照“碑：”那一行的材料；around 是碑脚下、四周插着的东西（照“碑：”那一行，英文）
STELE_LEAD = ("Draw one tall 2:3 portrait picture on a fully transparent background, in exactly the manner of the first attached picture, which is the approved blank stele of this series. "
              "Draw one stele of that same make: the same shape, the same proportions, the same blank face, the same size and the same position on the canvas, with the same clear transparent margin above and to both sides. ")
STELE_KEEP = (" The front face of the stele stays completely blank and uncovered: no letters, runes, symbols or carving on it, and nothing standing in front of it. "
              "Everything named around the foot is small and grouped low around the plinth on a small patch of ground; nothing in front of the stele rises higher than the bottom fifth of its face. "
              "Anything said to stand behind the stele may show beside its edges and above it, but never in front of the face. "
              "Outside that small patch of ground and those few things the background stays fully transparent.")
STELES = [
    ('b01', '雨城清查', 'bronze', "A tiny basket the size of a fingernail is carved low on the plinth. Around the foot stands a ring of small plain wooden boards stuck upright in the earth, about a dozen, each a narrow grave-board without any writing."),
    ('b02', '机兵化犁', 'bronze', "It stands at the mouth of a great furnace: behind it, low, the dark arched mouth of a brick furnace glows orange. Around the foot stands a ring of new iron plowshares planted point-down; along an iron rail at one side hangs a row of small bronze bells."),
    ('b03', '盐路赎身', 'bronze', "It stands beside the low stone rim of a salt well; round the well rim hangs a ring of opened iron shackles, locked one to another in a chain."),
    ('b04', '归林', 'bronze', "It stands at the foot of a stone watch-tower: behind it, low, the bottom of the tower door shows racks stacked with stag antlers; at the foot lies one empty bow rack."),
    ('b05', '九年之路', 'bronze', "At a village entrance: around the foot stands a ring of plain pale wooden hunting longbows planted upright in the snow-patched earth, unstrung, "
                                 "each clearly a bow: a long, nearly straight stave of pale wood with a dark leather grip wrapped round its middle and a loose bowstring tied at its upper tip and hanging down."),
    ('b06', '扶剑礼', 'bronze', "It stands at the foot of a wide flight of pale palace steps; three paces to its right, one plain greatsword stands upright in a stone block, its hilt untouched. Nothing else around it."),
    ('b07', '炭巷', 'bronze', "It stands at the mouth of a narrow lane under a riverbank, the lane dark with soot behind it; before the foot stands one row of iron shovels with snapped-off handles, planted in the earth."),
    ('b08', '灰旗', 'white', "This stele is an old weathered grey gate-stone set against the inner side of a stone gateway, rougher and greyer than the sample; above its top a small piece of plain grey cloth is nailed fast to the gate arch."),
    ('b09', '河心三日', 'white', "This stele is a single rough river boulder, grey and rounded, with one roughly flat face toward us (the face stays blank), standing in shallow water at a river ford, a few reeds and pebbles at its foot. No plinth: it rises straight out of the water."),
    ('b10', '南沼停火', 'bronze', "It stands beside a small round salt spring with a low stone rim; around the foot stand two rings of old weapons planted upright, an inner ring of short spears and an outer ring of curved swords, one ring for each of two peoples."),
    ('b11', '换俘碑', 'bronze', "It stands inside a city gateway: to its left and right, two tall plain wooden flagpoles, one at each side, each with a plain cloth banner hanging slack, one pale and one dark, with no emblem."),
    ('b12', '废弃水闸', 'bronze', "It stands on a stone platform beside an old sluice gate; nailed to the plinth at its foot are the two halves of one war horn that has been split lengthwise, one half on each side, both mouths pointing the same way."),
    ('b13', '红水', 'bronze', "It stands at the mouth of an old stone dock; around the foot stand the weapons of several fallen companies, planted in the mud, about half of them missing so that the ring has gaps; the water at the dock mouth is dark red."),
    ('b14', '喂山', 'bronze', "It stands before a temple door cut into a mountain; at its foot, rough sealing stones that were broken out of that door are stacked one on another in a low neat pile."),
    ('b15', '白母', 'bronze', "It stands in a snowy mountain pass; around the foot stands a close row of old wooden wagon shafts dug out of the snow, planted upright one beside another, a few still tied with half a harness rope."),
    ('b16', '赤盐边镇', 'bronze', "It stands outside a town gate on red salt ground; at its foot stands one long row of broken salt rakes planted in the reddish earth, about forty of them."),
    ('b17', '灰雨之夜', 'bronze', "It stands on a grassy slope outside a town gate; across its foot, pressed into the grass, lies one long cavalry lance with its point broken off. Nothing else around it."),
    ('b18', '黎明篡位', 'bronze', "It stands outside a palace hall on pale paving. Nothing at all stands around it: only the bare paving."),
    ('b19', '十四家之乱', 'bronze', "It stands on a river beach of pale pebbles; to its left a row of long-barrelled guns is planted upright, to its right a row of short spears, the two rows facing each other across the stele."),
    ('b20', '白杉堡', 'bronze', "It stands among broken white fortress stones; around it twenty-seven plain knightly swords are planted point-down in a ring, their crossguards worn smooth."),
    ('b21', '碎碑矿坑', 'bronze', "It stands at the mouth of a mine pit; beside it rises a small heap of broken bronze-gold rings, and a few broken shards of a larger stele lie at the foot of the heap."),
    ('b22', '苍焰角城', 'obsidian', "It stands where a mountain road leaves a city gate on black volcanic ground; around the foot a dense ring of about eighty plain spears is planted upright, sunk deep so that only their upper shafts and points show, like a low fence round the plinth."),
    ('b23', '血棘红园', 'obsidian', "It stands outside the door of a dance hall; around the foot twelve small plain family pennons on short poles are planted upside down, their cloth hanging toward the earth, each a different plain colour with no emblem."),
    ('b24', '骸钟墓城', 'obsidian', "It stands at the foot of an old bell tower; around the foot burns a ring of small grey stone lamps, each with a small steady flame."),
    ('b25', '无名碑林', 'bronze', "It stands at the edge of a marsh among many small plain standing stones without any marks, set close together behind it like a crowd, all lower than it; reeds at its foot."),
    ('b26', '魇镜幻都', 'obsidian', "Its face is polished like a black mirror (still blank, only a faint soft sheen across it, no reflection of any figure). It stands at a city gate beside dark still water."),
    ('b27', '黑翼天塔', 'obsidian', "This stele is set into a cliff face: rough dark rock surrounds it on three sides like a niche, the slab sunk flush into the rock, a narrow ledge of rock at its foot."),
    ('b28', '雷暴荒地', 'obsidian', "At its foot lies one long heavy chain of bronze-gold metal coiled in loops round the plinth, thick as an arm."),
    ('b29', '最后一尊', 'bronze', "It stands at the end of a line of plain stone bowls set on the bare grey ground; the last three bowls lead up to its foot. "
                                 "Nothing else lies around it: no weapons, no armour, no helmets, no cloth, only the bowls, the bare grey ground and a few pebbles."),
    ('b30', '深潮蓝堡', 'obsidian', "It stands on a sea shore facing the open sea; the lower part of the plinth stands in shallow water with small waves breaking round it."),
    ('b31', '第一条', 'bronze', "This is the first law stone of a new city: the slab is broader and heavier than the sample, but its face is just as blank. Nothing stands around it: only plain dark paving."),
    ('b32', '界碑', 'border', "It stands at the foot of a long white wall, on open ground a bowshot from it. Nothing else around it."),
    ('b33', '烧麦', 'white', "It stands in a wheat field burnt black; around the foot stand blackened sickles planted in the ash, from both sides, and a few unburnt stalks of golden wheat beyond them."),
    ('b34', '献祭台', 'bronze', "It stands on the bare stone base of a demolished platform on a mountain plateau: square foundation stones round it, nothing standing on them."),
    ('b35', '不灭王炉', 'bronze', "It stands at the bottom of a deep stair in front of a great furnace; behind it, low, the furnace mouth glows orange and white."),
    ('b36', '无字碑', 'white', "It stands beside a collapsed gateway of a great white wall: a few fallen white blocks lie at one side of its foot. The plinth is plain too."),
]

# ---------- 长卷 ----------
ROAD_LEAD = ("Draw one wide 3:2 landscape picture: one section of a very long painted scroll that follows one great white wall across a world through nine hundred years of uneasy peace after a long war. "
             "The view is from high above and a little to one side, a bird's-eye three-quarter view; the horizon is very high, about one tenth from the top of the picture. "
             "One long white battlemented wall of pale stone runs straight across the whole picture from the left edge to the right edge, with only a very gentle sway; "
             "it is about one twelfth of the picture tall, with a walkway along its top and plain square towers at long intervals. "
             "Fixed measures that every section obeys so that the sections join: at the left edge and at the right edge alike, the foot of the wall on its near side is exactly 47 percent of the picture height down from the top, "
             "and the top of its battlements is exactly 39 percent down; the wall leaves both edges straight, at full height, never broken, hidden or turned. "
             "The land beyond the wall, in the upper part of the picture, is the western land; the land on this side, in the lower part, is the eastern land. "
             "Right behind the wall, along its whole length, runs a band of open level ground from 30 to 38 percent down; in front of the wall, along its whole length, runs a wider band of open level ground from 50 to 69 percent down. "
             "Keep both bands mostly bare: short grass, flat earth and a few small stones, nothing tall and nothing that catches the eye, because standing stones will be set there later. "
             "The things named below stand outside those bands, in the far land above the far band or in the lowest part of the picture below the near band, small and clear like pieces set out on a table. ")
ROAD_STYLE = (" Drawing manner: match the hand of the attached plates exactly: large calm flat colour shapes layered like cut paper, thin lighter echo lines along the edges, soft inner gradients only, " + GRAIN + ". "
              "Things are simplified into clean silhouettes with plenty of quiet ground between them. Nothing is drawn in close-up; everything is small and seen from above. "
              "The left and right edges are not veiled in smoke or fog: the wall, the two bands and the land run straight out of the picture at both edges. "
              "No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D, no picture frame, no border. " + PALETTE)
ROAD_REF0 = (" The first attached picture is a plate from an earlier book of this series: take only its bird's-eye viewpoint and its hand from it, never its road, its red earth or anything drawn in it. "
             "The second attached picture is the approved main plate of this age: take its colours from it.")
# 11-14 第一回铺开时 r02|r03 那道缝没接上（r02 右下的林子到缝就断，天也一下子亮了一截）：原来写的是“左边那一段画过的一样也别再画”，
# 它连跨过缝的林子、天也不接了。改成跨过缝的照接、别的才不重复，左边那一段排头一张参考（r01 挪到第二张）。
ROAD_CONT = (" this picture continues it seamlessly, as if the two had been painted on one long sheet and cut apart. "
             "At this picture's left edge everything must be exactly what runs out of that picture's right edge: the wall with its height, its white stone, its battlements and the things hanging on it; "
             "the two bands of open ground; the colour and brightness of the land and of the snow, water or wheat on it; and the colour and brightness of the sky and its clouds. "
             "Whatever is cut by that picture's right edge (a field, a forest, a river, a snowfield, a road, a bank of cloud) runs on into this picture across its left edge and only then ends or gives way to what this section names; "
             "the change of light named for this section happens gradually across this picture, never as a jump at its left edge. "
             "Apart from what crosses that edge, do not repeat the things drawn in that picture. ")


def road_ref(n):
    if n == 2:      # 左边那一段就是头一段，只给一回
        return (" The first attached picture is the approved first section of this very scroll and the section immediately to the LEFT of this one:" + ROAD_CONT +
                "Match its hand, viewpoint, scale and the wall exactly. The second attached picture is the approved main plate of this age: its colours.")
    return (" The first attached picture is the section immediately to the LEFT of this one:" + ROAD_CONT +
            "The second attached picture is the approved first section of this scroll: match its hand, viewpoint, scale and the wall exactly. "
            "The third attached picture is the approved main plate of this age: its colours.")
ROADS = {
    1: ("This section: the first years after the war ended. Light and sky: at the left edge a low ash-grey sky just after rain, damp, with the last thin grey rain falling; across the picture the rain stops and the sky turns a pale soft overcast grey-white toward the right edge. "
        "On the wall a row of rust-brown war horns hangs from the battlements, unblown. "
        "Below the near band, on the left: a small poor town built against the foot of the wall out of fallen white wall-stones, its roofs wet; in its low town wall one deep arched gateway, and inside the arch a small fire burns among a row of small baskets: the only warm light in the picture. "
        "Below the near band, on the right: a big brick furnace beside a small railway halt, its mouth glowing; a line of iron clockwork soldiers, man-shaped, each with a large wind-up key in its back, walks one by one into the furnace mouth, and beside the furnace lies a heap of new iron plowshares; a row of small bronze bells hangs on an iron rail by the furnace. "
        "In the far land above the far band: grey ash plains, and on distant hills a few great empty seats of dark stone, cold. A few flakes of grey ash drift in the air on the left."),
    2: ("This section: the quiet first centuries. Light and sky: pale soft overcast grey-white at the left edge, slowly darkening across the picture into a grey-violet dusk at the right edge. "
        "Below the near band, on the left: a pale salt road crossing the land with a few small salt wagons, and beside it a stone-rimmed salt well hung all round with a ring of opened shackles. "
        "On the wall, in the middle: one watch-tower hung from top to bottom with rows of stag antlers; from its foot a short line of tall slender elves carrying longbows walks away from the wall, down toward a forest at the lower right. "
        "In the far land above the far band: grey steppe and patches of wheat gone half wild, tangled and tall. A few ash flakes still drift, thinning out."),
    3: ("This section: the beginning of the long night. Light and sky: a grey-violet dusk at the left edge turning into deep night toward the right edge, a cold blue-black sky with a few small stars; "
        "as night falls the white wall begins to give off a faint pale glow along its whole length, as it does every night in this age. "
        "Below the near band, on the left: the forest that comes in from the left edge ends a little way into the picture, and beyond it snow lies on the ground; "
        "a long thin line of tiny people in furs walks south across the snow from behind the forest's edge, led by one man who holds up a white glowing branch like a torch; a few small campfires along the line. "
        "Below the near band, on the right: across a dark river, a great sleeping capital city with a palace at the top of a long flight of pale steps, the whole city lying low in the lowest third of the picture so that its domes and towers stay below the near band; "
        "at the foot of the steps one plain greatsword stands upright in a stone, its pommel catching a faint white light. "
        "In the far land above the far band: dark empty plains and a few small cold watch-fires."),
    4: ("This section: the deep of the long night. Light and sky: deep night from edge to edge, a cold blue-black sky with a few small stars, the white wall glowing faintly along its whole length. "
        "Below the near band, on the left: under a steep riverbank, the mouth of a narrow lane of smithies and charcoal heaps, one forge glowing; before the lane mouth stands a row of iron shovels with snapped-off handles. "
        "In the far land above the far band, in the middle: three small walled towns on a hillside, and over the last of them one small plain grey banner. "
        "Below the near band, on the right: a wide river ford with one lone flat-faced river stone standing in the shallows; further right, a reedy southern marsh with three small salt springs, the middle spring ringed by two circles of old weapons planted in the earth. "
        "A few tiny orange sparks drift up from the forge."),
    5: ("This section: the years when peace came near. Light and sky: deep blue-black night at the left edge, the white wall glowing faintly; toward the right edge a dull red glow rises low on the far horizon. "
        "In the wall on the left: a gate-town built into the wall, with a stone bridge over a dry moat and an old elm full of storks' nests; in its gateway two plain flagpoles, one at each end. "
        "In the wall in the middle: an old sluice gate at the foot of the wall with a small stone platform beside it. "
        "Below the near band, on the right: an old stone shipyard dock on a river whose water glows a deep dull red; under the red water lies the dark drowned shape of a great fallen tower; a few small lanterns at the dock mouth. "
        "A few red sparks rise on the right."),
    6: ("This section: the last years before the burning. Light and sky: night with a dull red glow on the far horizon at the left edge, the red fading across the picture into a dark blue night at the right edge, where fine grey rain begins to fall. "
        "In the far land above the far band, on the left: a mountain with a carved temple door at its foot and broken stones piled before the door; further off, a high snowy pass. "
        "Below the near band, in the middle: a small town on red salt flats, a row of broken salt rakes standing before its north gate. "
        "Below the near band, on the right: a small campfire on open ground with five bedrolls round it and one pole flying a crude hand-sewn white banner with a black bird stitched on it. "
        "Near the right edge, below the near band, the first houses of a poor town built against the foot of the wall, and a long low hall with lamps lit in all its windows."),
    7: ("This section: the night of grey rain and the seven years after it. Light and sky: at the left edge, dark night in fine grey rain, lit from below by a red-orange glow of fire; across the picture the rain thins and stops, and at the right edge the sky is the deepest dark blue of the hour just before dawn. "
        "Below the near band, on the left: the poor town at the foot of the wall burns in the rain, a ring of fire around it with one gap broken open in the ring; on the grassy slope outside its south gate lies one long cavalry lance with its point broken off. "
        "Smoke from the burning town drifts across the sky on the left. "
        "Below the near band, from the middle to the right: a lonely road running along the foot of the wall past a few small gate-towns, each showing one lamp; one tiny traveller with a long sword walks the road toward the right. "
        "In the far land above the far band: a dark river winding through the western plain."),
    8: ("This section: the dawn. Light and sky: at the left edge the deepest blue before dawn; in the middle one straight, narrow shaft of pale gold light cuts down across the whole sky from upper right to lower left, like a single sword stroke; "
        "right of that line the sky opens into warm amber dawn, brightest low on the near, eastern side, while the far western side stays a little darker. "
        "Below the near band, on the left: a great capital city across a river, a palace at the top of a long flight of pale steps, a broken crown lying on the top step; a line of tiny torches climbs the steps from a cluster of reed huts along the riverbank. "
        "Below the near band, in the middle: a river beach of pale pebbles with two short rows of planted weapons facing each other, one row of long-barrelled guns and one row of short spears. "
        "In the far land above the far band, on the right: the ruins of a white fortress with swords planted point-down round it, and a deep mine pit with a heap of bronze-gold rings beside it. Motes of dust shine in the dawn light on the right."),
    9: ("This section: the age of the seven cities, morning. Light and sky: amber morning at the left edge brightening into a clear bright day toward the right edge, a high clean pale sky. "
        "In the far land above the far band, spread across the picture: a black stone mesa crowned with a small walled city at the foot of a volcano with a pale blue flame on its summit; a valley of thorny red gardens around a long dance hall; "
        "a city of tombs below one tall old bell tower ringed with small grey lamps; and a wide marsh full of many small plain standing stones. Each is small and clear, with ground between them. "
        "Below the near band: green fields, a new town with a tall plain courthouse, and along a riverbank a long row of upright stone boards like public ledgers."),
    10: ("This section: the age of the seven cities, afternoon. Light and sky: clear bright day at the left edge turning to a bright warm afternoon at the right edge. "
         "In the far land above the far band, spread across the picture: a black lake with a pale city on its shore whose roofs are mirrored in the still water; a coast of high cliffs with a port of slender towers on the clifftops, and one broken tower lying in the sea below; "
         "a dark plain under a small storm with thin lines of lightning; a bare grey plain with a long line of small stone bowls leading to its centre; and near the right edge a deep blue sea bay with a fortress of blue stone standing at the water. "
         "Below the near band: farms and a road with a few small travellers and carts."),
    11: ("This section: the years of wheat, the first half. Light and sky: a bright warm afternoon at the left edge mellowing into a golden late afternoon at the right edge. "
         "Wheat now grows right up to the bands on both sides of the wall: below the near band and above the far band, golden wheat fields in long rows. "
         "In the far land above the far band, on the left: a great new city of black stone in a ring of black glassy hills, with one huge bronze-gold slab standing in its central square; further right, a long covered railway gallery running into dark mountains. "
         "Below the near band, on the right: a gate-town in the wall, and before it one patch of wheat burnt black with two tiny figures holding lamps standing by it."),
    12: ("This section: the last one, the years of wheat and the last night. Light and sky: a golden evening at the left edge, dimming across the picture into night toward the right edge. "
         "In the far land above the far band, on the left: a plateau among southern mountains with the bare square foundation of a demolished platform on it; in the middle, a dark mountain with the glow of a great furnace showing deep inside it through an opening. "
         "Golden wheat on both sides of the wall, darkening as the evening falls. "
         "Near the right end, the white wall has a collapsed gateway, a wide gap of fallen white blocks; at that gap a long jagged crack opens across the ground below the near band and runs away from the wall, "
         "and warm golden light pours up out of the crack into the night like the glow of a great hearth deep underground. The wheat beside the crack leans away from it. "
         "The wall still runs on out of the right edge beyond the gap, at full height."),
}

# ---------- 时代原画 ----------
ERA_LOOK = ['pv1_c.png', 'pv1_a.png']
ERA_STYLE = (" Drawing manner: the attached pictures are approved plates of this very series, and the new plate must look as if the same hand had painted it for the same film. "
             "Match them exactly: the same shape language, line weight, paper grain, softness, inner glow and level of detail. "
             "Large calm flat colour shapes layered like cut paper; the vast things in the picture are drawn as overlapping pale cut-paper silhouettes that curve around the small focal point like waves, "
             "with thin lighter echo lines running along their edges; people are tiny and simplified; lights glow softly from within; plenty of quiet empty space; soft inner gradients only; " + GRAIN + ". "
             "The colours are those of the FIRST attached picture, the approved main plate of this age (take only its colours and its hand from it, never its figures or composition): " + PALETTE +
             "Keep it simple and airy: no dense ornament, no gothic tracery, no heraldic shields or coats of arms, no ornate picture frame, no border. "
             "No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D render. No blood and no wounds. "
             "Take only the drawing manner and the palette from the attached plates. Do not copy their compositions, and do not bring in any figure, beast, tower or building from them that the scene above does not name.")
ERAS = {
    'e1': dict(text=(
        "Scene: the first years after the long war, the age when the war machines were beaten into plowshares. In the lower centre, at the foot of a long white wall, stands a small poor town built of fallen white stones; "
        "in its low town wall one deep arched gateway, and inside the arch a small fire burns among a row of small woven baskets, one of them with a blanket in it; one tiny old woman sits by the fire. "
        "Thin grey rain falls over everything except the dry archway. "
        "Above the town, filling the grey sky, a host of enormous kneeling clockwork soldiers is drawn as overlapping pale cut-paper silhouettes, man-shaped, each with a great wind-up key standing in its back, all bowing toward the little fire; "
        "toward the right their bowed forms turn into the curved shapes of plowshares and then into long ears of wheat that sweep across the sky in a wave. Palette: ash grey, white stone, soft lavender grey, a little dark bronze-gold, and the one warm fire."), refs=[]),
    'e2': dict(text=(
        "Scene: the long night. Across the lower part of the picture a long thin line of tiny people in furs walks south over a snowfield in a gentle S-curve, led by one man who holds up a white glowing branch like a torch; a few small campfires burn along the line, the only warm points. "
        "Above them the night fills the picture: the great white mountains of the north drawn as overlapping pale cut-paper silhouettes that curve over the walkers like waves, and between them the cold blue-black sky with a scatter of small stars. "
        "Far off, small, the long white wall glows faintly along the horizon. Palette: deep blue-black, slate, snow white, a little silver, and small warm fires."), refs=[]),
    'e3': dict(text=(
        "Scene: the years when peace came near, and the river ran red. In the lower centre an old stone shipyard dock opens onto a river whose water glows a deep dull red at night; two tiny figures descend the steps of the dock toward the water, each carrying a small lantern: "
        "on the left a slender woman in a long grey hooded mage's coat, her face hidden by the hood, and on the right a tall young woman with dark copper-brown hair in a braided bun, in a worn officer's coat, with a plain old sword at her hip; both are seen from behind. "
        "On the bank above the dock, small, a campfire with one pole flying a crude hand-sewn white banner with a black bird stitched on it. "
        "Rising out of the red water and curving up through the night sky, drawn as an overlapping pale cut-paper silhouette, is the drowned shape of a great fallen tower, broken in three, red light glowing in its cracks. "
        "Palette: blue-black night, dull red water and glow, slate, bone white, small warm lanterns."), refs=['thornevia']),
    'e4': dict(text=(
        "Scene: the dawn. A long flight of pale stone steps rises from the lower left toward a dark palace at the upper left. Near the top of the steps stands one small figure seen from behind: a woman with dark copper-brown hair in a braided bun, a long strand at each temple, "
        "in a white officer's coat with a little gold edging and a white cape, brown leather gloves, holding a plain old long sword lowered at her side; she wears no crown. On the step before her lies a broken crown in two halves. "
        "Below her, a line of tiny people with torches climbs the steps from reed huts along a dark river. "
        "Across the whole sky one straight narrow shaft of pale gold light falls from the upper right to the lower left like a single sword stroke: left of it the sky is still the deep blue of night, right of it the sky opens into warm amber dawn, "
        "and the great banks of cloud on the dawn side are drawn as overlapping pale cut-paper silhouettes curving toward her. Palette: deep night blue, white stone, amber and pale gold, small warm torches."), refs=['thornevia']),
    'e5': dict(text=(
        "Scene: the age of the seven cities, in broad daylight: a high, clear, pale daytime sky, bright and cool, with no night and no dusk anywhere in the picture. "
        "In the lower centre, on a dark plain of black glassy ground that shines a little under the daylight, a great camp of grey tents surrounds one plain grey tent, a small fire burning at its door; tiny people move between the tents. "
        "Around and above the camp, curving round it like waves, seven distant places of the western land are drawn as overlapping pale cut-paper silhouettes: a black mesa city under a volcano with a pale blue flame on its summit; "
        "a valley of thorny red gardens; a city of tombs under a tall bell tower; a still black lake with a mirrored city; a port of slender towers on high sea cliffs; a plain under a storm with thin lines of lightning; and a blue sea bay with a fortress. "
        "Palette: obsidian black, slate, lavender grey, dark bronze-gold, touches of pale blue and dull red for the seven places, small warm fire."), refs=[]),
    'e6': dict(text=(
        "Scene: the years of wheat, at dusk. A long white wall runs across the picture from the lower left into the distance; on both sides of it golden wheat fields roll away in long waves. "
        "Along the foot of the wall stands a row of boundary stones, each a white stone and a black stone set back to back. In the lower centre, by one of these stones, two tiny people stand facing each other across the stone, each holding up a small lamp: one from each side of the wall. "
        "Above them the evening sky is filled with the waving wheat and the long clouds drawn as overlapping pale cut-paper silhouettes in gold and lavender that curve round the two lamps. "
        "Far off at the horizon, small, one thin crack in the earth glows with warm golden light. Palette: gold, lavender grey, white stone, obsidian black, warm lamps."), refs=[]),
}

# ---------- 远景七张 ----------
# 11-14 用户看了长卷横着走的样子说怪，改成一条往前走的路（一点透视，镜头在路上，碑从远到近），路、长垒、地面由页面拿代码画，碑用 b01 到 b36 抠的图，
# 长卷十二段不用了（留着）。这里只出路尽头的天和地平线：一页一张（h1 犁 到 h6 麦），h7 是 947 年归寂月最后一夜。
# 横幅（gpt_gen 出得最宽的就是 3:2），地平线在图高六成，地平线以下一片平的、颜色均匀的薄雾地，页面会盖住下半截；左边远处长垒收到地平线的那一点点白。
HOR_LEAD = ("Draw one wide 3:2 landscape picture: a far, calm horizon backdrop that will stand at the end of a long straight road in a picture book, with nothing at all in the foreground. "
            "The horizon is one straight, level line at exactly six tenths of the picture height from the top, running from the left edge to the right edge. "
            "Above the horizon: the sky of this moment and a few far things standing on the horizon, all small, low and far away, as described below. "
            "Below the horizon: only an even, flat, featureless ground veiled in thin mist, of one even colour that grows only a little lighter toward the horizon; "
            "no road, no wall, no path, no stones, no grass, no figures and nothing near, because the lower part will be covered by the page. "
            "Near the left edge, a great white wall of this world runs away into the far distance: of it, only a thin pale white sliver shows where it reaches the horizon, very small; draw nothing else of the wall. "
            "The land beyond that wall, on the far left, is the western land; the land on the right is the eastern land. ")
HOR_STYLE = (" Drawing manner: the attached pictures are approved plates of this very series, and this backdrop must look as if the same hand had painted it for the same film. "
             "Match them exactly: the same shape language, line weight, paper grain, softness, inner glow and level of detail; large calm flat colour shapes layered like cut paper, "
             "clouds as overlapping pale cut-paper bands with thin lighter echo lines along their edges, far things as simple flat silhouettes, soft inner gradients only, " + GRAIN + ". "
             "The colours are those of the FIRST attached picture, the approved main plate of this age (take only its colours and its hand from it, never its figures or composition): " + PALETTE +
             "Take only the drawing manner, the palette and the light from the attached plates; do not copy their compositions, and draw none of their figures, beasts, towers or buildings. "
             "Keep it quiet, airy and mostly sky. No people anywhere. No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D render, no ornate frame, no border.")
HORS = {
    'h1': dict(look='e1.png', text=(
        "This moment: the first years after the long war, just after grey rain. The sky is a low ash-grey and pale grey-white, the cloud bands breaking a little, the last thin rain streaks fading away at the upper left; "
        "the light is flat, soft and cool. On the far left, beyond the thin sliver of the wall, a few great empty seats of dark stone stand on low far hills, tiny and cold. "
        "Elsewhere the horizon is only low, pale, far hills.")),
    'h2': dict(look='e2.png', text=(
        "This moment: the long night. A cold blue-black night sky full of small stars; there is no moon and no curved arc of light anywhere in the sky. "
        "The thin sliver of the white wall on the far left gives off a faint pale glow, as it does every night in this age. "
        "Along the horizon on the right, the low snowy mountains of the north as pale overlapping cut-paper silhouettes, and a few tiny cold watch-fires on the far plain.")),
    'h3': dict(look='e3.png', text=(
        "This moment: the years when peace came near, at night. A dark blue-black sky with a few small stars; low on the horizon, a little to the right of the middle, "
        "one place glows a deep, dull red, a wide low red glow that stains the underside of the clouds above it and the mist below it, as if a river far away were glowing red. "
        "Inside that red glow, very small and dark on the horizon, the broken silhouette of a fallen stone tower. No moon.")),
    'h4': dict(look='e4.png', text=(
        "This moment: the dawn. The sky is cut in two halves: the left half is still the deep blue of night with a few small stars, the right half has opened into warm amber dawn, brightest low on the horizon. "
        "Between the two halves, in the middle of the picture, one straight, narrow, perfectly vertical shaft of pale gold light falls from the top edge of the picture straight down to the horizon, like a single sword stroke. "
        "On the horizon under the shaft, very small, the far silhouette of a great city on a low hill with a palace at the top of a long flight of pale steps.")),
    'h5': dict(look='e5.png', text=(
        "This moment: the age of the seven cities, in broad daylight. A clear, high, pale daytime sky with a few calm high cloud bands; bright, clean, cool light. "
        "On the far left, beyond the thin sliver of the white wall, a few far cities of black obsidian with dark towers stand on the horizon, and among them a small volcano with a pale blue flame on its top; "
        "on the right, far cities of white stone with pale towers stand on the horizon. All of them are small, flat, far silhouettes.")),
    'h6': dict(look='e6.png', text=(
        "This moment: the years of wheat, at golden evening. A warm golden-amber sky, brightest low on the horizon, with long lavender-grey cloud bands above. "
        "Right along the horizon lies a thin band of far golden wheat fields, and along the foot of the far white wall a long dotted row of tiny boundary stones runs away into the distance, "
        "each a white stone and a black stone set back to back. Below that thin far band, only the even mist ground.")),
    'h7': dict(look='e2.png', text=(
        "This moment: the last night of the age, as night falls. The deep blue-black sky of early night with a few small stars; no moon. "
        "Far away, right of the middle, the earth along the horizon has cracked open in one long, low, jagged line, and warm golden light pours up out of the crack into the night "
        "like the glow of a great hearth deep underground, lighting the underside of the clouds above it in gold. "
        "Near that crack, very small, the white wall has a collapsed gateway, a little gap of fallen white blocks on the horizon.")),
}


# ---------- 人物立牌六张 ----------
# 11-14 用户：路当中以巴尔缇娜为主角，玩家跟着她往前，遇到索恩薇娅以后两人同行，灰雨之后各走一条并行的路。
# 一人三张（小时候、少女、成年；少年兵、军官、白衣），透明底、全身、从正背后看、往前走、一只脚在前，同一个机位（身后两三步、略高一点）。
# 先出两张成年的（w_bal_3、w_sor_3），另外四张拿同一个人成年那一张当头一张参考对齐机位和画法；出完 --wnorm 照身高缩到同一个比例（原图留作 _raw）。
WALK_LEAD = ("Draw one tall 2:3 portrait picture on a fully transparent background: a full-length standing figure of one person walking away from us, seen from directly behind, "
             "made as a cut-out figure for a picture book. The camera is two or three steps behind her and a little higher than her head, looking slightly down along her back. "
             "She walks forward, straight away from us into the picture, in the middle of a step: one foot a short step ahead of the other. "
             "We see the back of her head, her back and the backs of her legs, never her face. Her toes point away from us: the leading foot is a little further away and so a little higher on the canvas, "
             "and the heel of the trailing foot is just lifting off, so a little of its sole shows. Her arms hang naturally at her sides with a slight swing, the backs of her hands toward us, relaxed and empty unless said otherwise. "
             "She has exactly two arms, two hands, two legs and two feet, with natural proportions for her age. "
             "She stands in the middle of the canvas, and the soles of her feet are at nine tenths of the canvas height from the top. "
             "Draw her at this fixed scale, the same for the whole set: a person 170 centimetres tall reaches from the soles at nine tenths of the canvas height up to one tenth of it. ")
WALK_TAIL = (" There is nothing else in the picture: no ground, no shadow, no props on the ground, no background, no frame; everything around her is fully transparent. "
             "Drawing manner: the flat stylized hand of the attached plates of this series: clean flat colour shapes with crisp edges, simple two-step shading, thin lighter echo lines along the edges, "
             "soft inner gradients only, " + GRAIN + "; matte, softly lit from the front left. Take the colours from the approved main plate of this age among the attached pictures. "
             "No realistic rendering, no 3D render. She is fully and modestly clothed.")
WALKS = {
    'w_bal_3': dict(cm=168, head='baltina', look='e3.png', text=(
        "She is Baltina as a grown woman who looks about twenty-three, slender, about 168 centimetres tall, so the top of her head is at about eleven hundredths of the canvas height. "
        "Long straight silver-grey hair falls loose down her back to her waist; one thin braid taken from the side of her head is drawn back and tied at the back of her head with a small black ribbon bow; "
        "slightly pointed ears. She wears a long black high-collared dress with long sleeves reaching her ankles, and a long black cloak hanging from her shoulders to her calves, "
        "its edge turning back here and there to show its deep red lining, with a thin gold edging along its border; black low boots. No hood.")),
    # 11-14 主会话补的：立绘资料里她从长夜到黎明的年月（到 741 年）一直看着十六七（cast/山铜纪/s2b、s3b、s4c，约 154 到 158 厘米），七城的年月起看着二十五六（s5b，168 厘米）；
    # 661 年灰雨以后换了那一身黑。所以她是四张：小时候、少女灰衣（灰雨魔女那一身灰）、少女黑衣、成年。头一回出的 w_bal_1、w_bal_2 衣服偏紫褐，留作 _v1。
    'w_bal_2': dict(cm=154, head='baltina', look='w_bal_3.png', text=(
        "She is the same Baltina as the Grey Witch of the rain city, a long-lived girl who looks sixteen or seventeen, small and slight, about 154 centimetres tall, "
        "so the top of her head is at about fifteen hundredths of the canvas height. Her straight silver-grey hair falls to the middle of her back, with the same thin side braid drawn back "
        "and tied at the back of her head with a small black ribbon bow; slightly pointed ears. She wears a long ash-grey wool cloak with its hood down and its cuffs frayed to threads, "
        "over a plain dark grey wool dress with long sleeves falling to her shins, grey leggings and patched walking boots; a small leather-bound notebook hangs at her belt on a cord. "
        "Her clothes are plain ash-grey and dark grey, never brown or purple, warm and fully covering. No hood on her head.")),
    'w_bal_2b': dict(cm=158, head='baltina', look='w_bal_3.png', text=(
        "She is the same Baltina in the years after the night of grey rain, a long-lived girl who still looks sixteen or seventeen, slim and straight-backed, about 158 centimetres tall, "
        "so the top of her head is at about thirteen hundredths of the canvas height. Her long straight silver-grey hair falls loose down her back to her waist, with the same thin side braid "
        "drawn back and tied at the back of her head with a small black ribbon bow; slightly pointed ears. She already wears the same black clothes as the grown woman in the first attached picture: "
        "a long black high-collared dress with long sleeves reaching her ankles, black leather gloves, and a long black cloak hanging from her shoulders, its edge turning back here and there "
        "to show its deep red lining, with a thin gold edging along its border; black low boots. She is a girl, smaller and slighter than the woman in the first picture, fully covered. No hood.")),
    'w_bal_1': dict(cm=125, head='baltina', look='w_bal_3.png', text=(
        "She is the same Baltina as a small girl who looks about seven or eight years old, about 125 centimetres tall, so the top of her head is at about thirty-one hundredths of the canvas height; "
        "a child's proportions, with a larger head and short limbs. Her straight silver-grey hair falls to her shoulder blades, with a thin side braid drawn back and tied at the back of her head with a small black ribbon bow. "
        "She wears a long plain ash-grey wool robe with long sleeves, a little too big for her, reaching her ankles, an ash-grey wool shawl wrapped round her shoulders, and small sturdy boots: "
        "the plain grey clothes of the people of the rain city, ash-grey and never brown or purple, warm and fully covering. No hood.")),
    'w_sor_3': dict(cm=174, head='thornevia', look='e4.png', text=(
        "She is Thornevia as a grown woman of about twenty-five, tall and strong, about 174 centimetres tall, so the top of her head is at about eight hundredths of the canvas height. "
        "Her deep copper-brown hair is braided and coiled into a bun at the back of her head, with one long loose strand left at each temple. "
        "She wears a white military coat with a little gold edging at the hem and cuffs, a white cape hanging from both shoulders down her back to below her knees, brown leather gloves, "
        "a long sword in a plain scabbard at her left hip, dark trousers and tall brown boots. No crown and no helmet.")),
    'w_sor_2': dict(cm=174, head='thornevia', look='w_sor_3.png', text=(
        "She is the same Thornevia at about twenty-eight, as a field officer of the southern line, about 174 centimetres tall, so the top of her head is at about eight hundredths of the canvas height. "
        "The same deep copper-brown braided bun with a long loose strand at each temple. She wears an old, faded slate-blue officer's coat with a high collar and mismatched buttons, "
        "the rank insignia torn off the collar so that a paler patch and a few loose threads are left; under it patched brown leather armour, the patches showing at the shoulders; "
        "a small cloth pouch tied at the small of her back; an old sword hanging at her left hip, its hilt wrapped in hemp cord; dark trousers and worn boots. No cape, no crown.")),
    'w_sor_1': dict(cm=168, head='thornevia', look='w_sor_3.png', text=(
        "She is the same Thornevia as a girl soldier of about sixteen or seventeen, in her first years on the wall, about 168 centimetres tall and still a little lanky, "
        "so the top of her head is at about eleven hundredths of the canvas height. The same deep copper-brown braided bun with a long loose strand at each temple. "
        "She wears old, scuffed brown leather armour over a coarse undyed linen coat that reaches her knees, plain dark trousers and worn boots, and a plain old sword in a worn scabbard "
        "slung diagonally across her back, its hilt behind her right shoulder and below the top of her head. Fully covered.")),
}


def walk_norm(key, feet=0.90, px_per_cm=None):
    """照身高把立牌缩到同一个比例：170 厘米的人从图高九成量到一成（每厘米 0.8×1536/170 像素），脚底落在图高九成，左右照两条腿那一截的正中摆到图当中。
    原图头一回动以前留作 <键>_raw.png，再跑一回从 _raw 重做。"""
    np, Image = _np()
    raw = os.path.join(OUT, key + '_raw.png')
    p = os.path.join(OUT, key + '.png')
    if not os.path.exists(raw):
        os.replace(p, raw)
    im = Image.open(raw).convert('RGBA')
    W, H = im.size
    a = np.asarray(im)[..., 3]
    ys, xs = np.nonzero(a > 40)
    top, bot = ys.min(), ys.max()
    low = a[int(bot - (bot - top) * 0.22):bot + 1] > 40           # 两条腿那一截
    lx = np.nonzero(low.any(0))[0]
    cx = (lx.min() + lx.max()) / 2
    ppc = px_per_cm or 0.80 * H / 170
    s = WALKS[key]['cm'] * ppc / (bot - top + 1)
    fig = im.resize((max(1, round(W * s)), max(1, round(H * s))), Image.LANCZOS)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.alpha_composite(fig, (round(W / 2 - cx * s), round(feet * H - (bot + 1) * s)))
    out.save(p)
    print('缩好 %s：原来 %d 像素高、脚底在 %d，缩放 %.3f' % (key, bot - top + 1, bot, s))


# ---------- 只改一处 ----------
# 拿原图（<键>_v1.png）当底只改一处，别的都不动（照 gpt_cg.py 的 FIX）。头一张参考是底，后面的只给长相。原图在的时候走这一路。
FIX = {
    # 11-14 主会话：e3 巴尔缇娜不戴兜帽（用户在主画 k3 上专门叫改过，门面方向稿第五节），照旧背影或侧背、头发露出来，乔装的灰斗篷留着、兜帽放下
    'e3': (('e3_v1.png', F.cast_head('baltina')),
           "Redraw the FIRST attached picture and keep everything about it exactly the same: the same composition, the huge drowned tower broken in three rising over the dull red water, "
           "the cloud ribbons and the stars, the crude white banner with the black bird and the small campfire with crates and a barrel on the left, the bollards and ropes, the stone dock and its steps, "
           "the colours, the paper grain, the line, the framing and the size. The two small figures still walk down the steps away from us, each with a lantern, in the same places and the same poses, "
           "and the woman on the right, with her copper-brown braided bun, her worn pale coat with the ragged hem and the sword at her hip, stays exactly as she is. "
           "Change one thing only: the woman on the left. She no longer wears her hood. The hood of her long grey mage's cloak is down, lying in soft folds on her shoulders, and her head is bare. "
           "She is still seen from behind, her head turned only very slightly toward the woman beside her, so that one slightly pointed ear shows but not her face. "
           "Her hair is long, straight and silver-grey, falling loose down her back over the grey cloak to below her shoulder blades; one thin braid taken from the side of her head is drawn back "
           "and tied at the back of her head with a small black ribbon bow. Where the cloak parts as she walks, its deep red lining and the hem of a long black dress show. "
           "The SECOND attached picture shows only her head: take her hair colour, her hair style with the side braid and the black bow, and her slightly pointed ears from it, and nothing else; "
           "she stays tiny and seen from behind, and she holds her lantern exactly as before. "
           "Everyone is fully clothed. No moon. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 11-14 主会话：e4 苇棚区那几间圆顶草屋改成河滩上一排低矮的芦苇顶棚屋，斜顶、木桩撑着，挨着水，别的不动。
    # 这一条出的是 e4_v2.png（棚屋改好了，可棚屋后头多立了几根顶上带横木的杆子，像十字架），第二回拿它当底只拿掉横木，见下面 'e4'
    'e4_v2': ('e4_v1.png',
           "Redraw the attached picture and keep everything about it exactly the same: the same composition, the long flight of pale steps, the dark palace at the upper left, "
           "the woman in the white coat and white cape standing near the top of the steps with her sword lowered and the broken crown in two halves before her, the straight shaft of pale gold light, "
           "the night sky on the left and the amber dawn on the right, the clouds, the hills, the river with its reflected lights, the line of tiny people with torches climbing the steps, "
           "the colours, the paper grain, the line, the framing and the size. "
           "Change one thing only: the huts by the river at the lower right. In the attached picture they are round domed straw huts. Replace them with one row of low, poor reed shacks "
           "along the river beach, right beside the water: small huts with simple sloping roofs of bundled reeds and a few lean-tos, built of rough boards and propped up on short wooden stilts "
           "at the water's edge, patched and crooked like the hovels that poor river people build for themselves. No domes and no round huts. "
           "The torches and the people keep their places; a little warm light shows in one or two doorways. "
           "Everyone is fully clothed. No moon. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'e4': ('e4_v2.png',
           "Redraw the attached picture and keep everything about it exactly the same: the same composition, the steps, the palace, the woman in white with the broken crown before her, "
           "the shaft of gold light, the sky, the hills, the river, the torch-bearers, and the row of low reed shacks on the beach with their sloping reed roofs, boards, ladders, patched cloth, "
           "the stilted platform over the water and the lit doorway, the colours, the paper grain, the line, the framing and the size. "
           "Change one thing only: behind the shacks stand two or three tall wooden poles with a short crossbar near the top, which look like crosses. Remove the crossbars: "
           "each becomes one plain straight upright pole with a fishing net hanging from its top to dry. Nothing in the picture is shaped like a cross. "
           "Everyone is fully clothed. No moon. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 11-14 节点原画试画：灰旗三幕的弓手，弓弦的两半在他后颈会合，拉弦的右手却在肩膀右边；头上的灰布带勒在眼睛上像蒙眼。拿原图（_a0）当底只改这两处。
    'p2_d3': ('p2_d3_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the same composition and camera, the vast glowing molten gate of rock with the blinding white light pouring through its gap "
              "and the pale streaks of light stuck along its edges, the red-glowing cliffs, the scorched slope, and the archer seen directly from behind: his build, his torn grey jacket, the empty quivers on his back and hip, "
              "his straight left arm holding the reddish copper bow at its middle, his raised right arm and the place of his right hand, the blood on his arms, the small grey rag nailed to the upper limb of the bow, "
              "the colours, rendering and finish. Change two things only. "
              "One, the bowstring. In the attached picture the two halves of the string meet behind the back of his neck while his drawing hand is somewhere else; that is wrong. "
              "The string is one single string: it runs straight from the upper tip of the bow to the fingers of his right hand, exactly where his right hand is now, and from those same fingers straight down to the lower tip of the bow, "
              "so the two halves meet inside his right hand. The broken arrow shaft lies across the bow at his left hand and its back end sits on the string in his right hand's fingers. "
              "Remove every other string line, including the ones that meet behind his neck. "
              "Two, the grey cloth band on his head. It is tied round his forehead ABOVE his eyes like a headband, with its knot and two short loose ends at the back of his head; his eyes are not covered. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 11-14 改成往前走的路以后：三块碑背后连着一块画（b17 城门和城墙，b32 白墙和墙柱，b35 炉门的拱和台阶），立在路边是一块方的。
    # 拿原图（_a0）当底，只拿掉碑背后的东西，碑、碑座和碑脚的东西不动，底透明。
    'b17': ('b17_a0.png',
            "Edit the attached picture of a memorial stele. Keep the stele itself exactly as it is: its shape, its dark bronze-gold metal, its border, its blank face, its two-step plinth, its colours and finish. "
            "Keep the small patch of grass and earth directly under the plinth and the long broken cavalry lance lying across the grass at its foot, exactly as they are. "
            "Remove everything else: the town gate, the town walls and towers, the hills and every other part of the scenery behind and beside the stele. "
            "Everything outside the stele, its plinth, the small patch of ground under it and the lance is fully transparent, with a clean crisp edge. "
            "Same size, same position in the canvas, portrait 2:3. No text, no letters, no logo, no frame."),
    'b32': ('b32_a0.png',
            "Edit the attached picture of a memorial stele. Keep the stele itself exactly as it is: the pale white stone slab, the thin black volcanic-glass slab behind it showing as a rim, the four dark bronze-gold clamps on the side edges, "
            "its blank face, its two-step plinth, its colours and finish. Keep the small patch of dry grass, earth and the few small stones directly under and around the plinth, exactly as they are. "
            "Remove everything else: the long white wall and its square pillars behind the stele, and every other part of the scenery. "
            "Everything outside the stele, its plinth and that small patch of ground is fully transparent, with a clean crisp edge. "
            "Same size, same position in the canvas, portrait 2:3. No text, no letters, no logo, no frame."),
    'b35': ('b35_a0.png',
            "Edit the attached picture of a memorial stele. Keep the stele itself exactly as it is: its shape, its dark bronze-gold metal, its border, its blank face, its two-step plinth, its colours and finish. "
            "Keep the few paving stones directly under the plinth and the small things at its foot: the wooden bucket of coal and the tongs on the left, the small anvil and hammer on the right, exactly as they are. "
            "Remove everything else: the stone arch, the glowing furnace mouth and its flames, the stairs and every other part of the scenery behind the stele. "
            "Keep only a faint warm orange glow along the stele's outer edges, as if a furnace burned somewhere behind it. "
            "Everything outside the stele, its plinth, those few paving stones and the small things at its foot is fully transparent, with a clean crisp edge. "
            "Same size, same position in the canvas, portrait 2:3. No text, no letters, no logo, no frame."),
    # 11-14 子任务查图（查7）指出来、主会话放大核对过的：第六页七幅。都拿原图（_a0）当底只改那几处。
    'p6_d4': (('p6_d4_a0.png', os.path.join(OUT, '_ident', 's6a_linos_casual.png')),
              "Edit the FIRST attached picture and keep everything about it exactly the same: the same composition and camera, the towering troll woman with the rust-red braid carving the copper plate on the right, "
              "her face, her hands and her cloth-wrapped bare feet, the copper plate and its fourteen carved strokes, the stone well, the stone house, the coal heap, the black ridge with the tunnel mouth, "
              "the barefoot fire-horn man sitting on the bench, the dawn light, the colours, rendering and finish. Change two things only. "
              "One, the second figure sitting on the bench beside the fire-horn man. In the attached picture it is a black-haired woman in a long dress with two whole wings and a lit lamp; that is wrong. "
              "It is the man shown in the SECOND attached picture, a man of the night-wing folk: take his face, his short silver-grey hair and his dark long coat from that picture. "
              "He sits on the bench in the same place and at the same size. A pair of black feathered wings grows from his back, and his LEFT wing is burnt and torn away to half its size, its ragged edge charred black. "
              "On his lap he holds an old copper lamp in both hands, and the lamp is NOT lit: no flame and no glow in it. "
              "Two, the train far off along the rails: it has exactly fourteen wagons behind the engine; add wagons of the same kind at its tail to make fourteen. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p6_e3': ('p6_e3_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the same composition and camera, the kneeling horned woman in profile with her open book and her flat hand over the small flame, "
              "her face and features, her dark red horns with blackened tips, her black braid, her amber eyes, her black coat, knee pads and pouches, the sawn iron ring on her chest, the charred posts, the black ash, "
              "the broken pots, the boundary stone and the white wall far behind, the farmer watching at the edge, the colours, rendering and finish. Change one thing only: her skin. "
              "Her skin is charcoal-grey all over: her face, her ears, her neck and both of her hands are a smooth, even dark grey like cold charcoal, with soft lighter grey highlights, "
              "and only the very tips of her fingers are ash-white. No pink or pale skin anywhere on her. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p6_g2': ('p6_g2_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same, every person, the long table, the throne, the windows, the light, the colours, rendering and finish. "
              "Change one thing only: the gold cross embroidered on the back of the collar of the grey-haired man seated at the near end of the table in the foreground. Remove that cross completely: "
              "the back of his collar is plain grey cloth with one thin pale border line, and no cross or symbol of any kind. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p6_g3': (('p6_g3_a0.png', os.path.join(OUT, '_ident', 's6b_secunda_battle.png')),
              "Edit the FIRST attached picture and keep everything about it exactly the same: the same composition and camera looking down the long arched gateway into the sunset light, "
              "the black-haired horned woman in the grey army coat raising her right hand flat, the grey-cropped gate-keeper with the copper key, the white candle in the floor, the little girl and the horned man holding her hand, "
              "the stone tablets, the soldiers, the colours, rendering and finish. Change two things only. "
              "One, the person standing at the far left edge beside the black-haired woman, holding a round pale shield. In the attached picture it is a fair-haired man; that is wrong. "
              "It is the woman shown in the SECOND attached picture, a border officer of the bone folk: a tall, slender, pale woman with long silver-white hair gathered low at the back of her head, violet eyes and bone-white hands; "
              "take her face, hair and clothes from that picture. She stands in the same place facing us, and the round shield of pale bone is strapped on her LEFT arm, which is on the right side of her body as we look at her. "
              "Two, the knight on the grey horse at the far end of the gateway, seen from behind: his white round shield is on his LEFT arm, which is on the left side of his body as we see his back, "
              "and we see only the back of the shield, its face turned away from us toward the town. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p6_g4': ('p6_g4_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the same composition and camera, the woman sitting in profile on the low stone, her face, her silver hair with snow in it, "
              "her dark red coat and black dress, the pose of her arms and the place of both hands, the glowing boundary stone, the white wall with its archers, the orange sky, the snowy fields, the colours, rendering and finish. "
              "Change one thing only: the colour of her two hands, so that the glove is continuous. Her near arm is covered by a long black leather glove up above the elbow; "
              "the hand at the end of that same arm, the one lying open in her lap, is therefore a black-gloved hand. Her other hand, the one resting on her knee, is bare: a slender pale hand with no glove. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p6_i3': ('p6_i3_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the same composition and camera, the folding table with the pot and the bowls, the mist-haired horned young woman raising her hand with the sleeping boy against her, "
              "the round old halfling ladling porridge, the barefoot young man holding out the bowl, the glowing ceiling of fog and the shadows on it, the white wall, the snow, the colours, rendering and finish. "
              "Change one thing only: the creature on the rock on the left beyond the stone. In the attached picture it is a dragon; that is wrong. "
              "It is a person of the night-wing folk: a slim man of ordinary size in a dark coat, with short dark hair, crouching on top of the rock and watching the table, "
              "a pair of large black feathered wings folded against his back. No dragon and no scaly creature anywhere. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p6_i4': ('p6_i4_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the same high view down over the wide snowy basin, the glowing white wall across the top with its water gate and its tiny watchers, "
              "the line of small boundary stones, the dark cracks in the snow all running toward the water gate, the ring of snow leaping up around the little table, the steaming pot, the faint grey light at the east, "
              "the colours, rendering and finish. Change two things only. "
              "One, the four figures at the little table. They are: a round little halfling, much shorter than the others, with curly grey-white hair, red cheeks and a grey-white robe with a white stole; "
              "a broad young man with wheat-straw hair under an oilcloth cap and a grey wool coat, barefoot in the snow; a young woman with mist-blue hair in a coiled braid and a pair of small slate-grey horns sweeping back from her brow, in a homespun dress and wool vest; "
              "and a small child with mist-blue curls and two tiny horn buds at the brow, waking and clinging to her. The three grown figures look down at their feet. Keep them in the same places and at the same small size. "
              "Two, the creature perched on the rock at the upper left. In the attached picture it is a dragon; that is wrong. It is a person of the night-wing folk: a slim man of ordinary size in a dark coat, "
              "crouching on the rock with a pair of large black feathered wings half opened on his back. No dragon and no scaly creature anywhere. "
              "Remove the bright four-pointed stars drawn on the boundary stones; each small stone is plain, half white stone and half black obsidian. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 11-14 子任务查图（查4）指出来、主会话放大核对过的：第四页七幅、第五页两幅（p5_a4 那一枝樱花是日式的意象）。
    'p4_d2': ('p4_d2_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the white throne hall, the glass lamps and crystals, the long white stair, the banquet tables and the frozen feasters, "
              "the old emperor on the throne, the copper-haired woman's outstretched sword arm, the historian at her desk, the colours, rendering and finish. "
              "Change one thing only: the pieces of the cut crown. The crown has been cut through the middle into exactly TWO halves, no more. "
              "One half is falling just beside the throne near the old man's head; the other half is the one already tumbling down the stair, as it is now. "
              "In the attached picture there are two crown pieces up near the throne; keep only one of them there and remove the other, so that in the whole picture there are exactly two crown halves. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p4_d4': ('p4_d4_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the great white wall and its fortress across the top, the golden stubble fields and the sheaves, the farm track, the thatched stone cottage, "
              "the running dog, the pink-haired soldier seen from behind with her patched cuirass, short spear, round shield and boots, the mother in the doorway with both hands at her mouth, the two young women beside her with the pitchfork and the basket, "
              "the colours, rendering and finish. Change two things only. "
              "One, the faces of the two young women beside the doorway: in the attached picture they are both grinning; that is wrong. Neither of them has recognised the soldier yet: "
              "their mouths are closed, their brows slightly drawn, their eyes fixed on her in an uncertain, searching stare. "
              "Two, the soldier's left arm: in the attached picture it cannot be seen at all. Her left hand is raised to her left shoulder and grips the gathered neck of the fat sack resting on that shoulder, "
              "so that her left upper arm and her hand on the sack are clearly visible. Her right arm hangs at her side as it is now. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p4_d_regha': ('p4_d_regha_a0.png',
                   "Redraw the attached picture and keep everything about it exactly the same: the running wolf-eared woman, her pose, her face, her silver-grey hair and wolf tail, her coat, satchel and boots, "
                   "the dark field, the torch-lit barricade and soldiers, the flying earth, the colours, rendering and finish. Change one thing only: "
                   "beside her face, under her hair, a small human ear is showing; she has no human ears, only the two grey wolf ears on top of her head. "
                   "Cover that place with her silver-grey hair, so that no human ear shows anywhere. "
                   "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p4_e1': ('p4_e1_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the burning door frame, the platinum-haired young man holding it up with his arms spread and his clenched face, "
              "his cuirass and shield, the old men climbing out behind him, the burning huts, the river, the bronze plate, the colours, rendering and finish. Change two things only. "
              "One, his hands. Each hand simply grips the burning wooden post of the door frame, the fingers wrapped round the wood. The iron nails belong to the door frame: only their glowing red heads show on the posts, "
              "pressed under his palms. No nail passes through his hand or his wrist. There is no blood on his wrists or forearms and no wound on the inside of his wrists; "
              "only small flames crawl over the backs of his hands and his sleeves are scorched. "
              "Two, the man swinging the hammer against the bronze plate on the left: he wears a plain dark hood and a dark scarf pulled up over his nose and mouth, a common labourer's clothes, "
              "with no headband and no trailing ties; nothing about him looks East Asian. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p4_e4': ('p4_e4_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the blond woman seen from behind at the snowy parapet, her fur cloak, plate armour and great sword, the falling snow, "
              "the courtyard below with the steaming well and the young man with the horse, the colours, rendering and finish. "
              "Change one thing only: what is in her right hand. In the attached picture she holds a small three-dimensional model of a well with a little roof in her open hand; that is wrong. "
              "Her right hand hangs at her side clenched in a tight fist, and between her fingers shows only one edge of a small flat round bronze badge with a well engraved on it. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p4_g3': (('p4_g3_a0.png', os.path.join(OUT, '_ident', 's4b_ugo_private.png'), os.path.join(OUT, '_ident', 's4b_boru_casual.png')),
              "Edit the FIRST attached picture and keep everything about it exactly the same: the vast dark mine hall, the bound stone giant with the golden chain of rings, the bell, the glowing slab, "
              "the grey-haired witch striking it with the hammer, the crumbling grey figure at its foot, the colours, rendering and finish. Change only the two small figures off to the right. "
              "The one holding the clasp of the chain at the other's waist is the man in the SECOND attached picture: a gaunt giant of the bull-horned demon-kin, even taller than the smith beside him, ash-grey skin, "
              "his horns sawn off flat at the roots, close-cropped iron-grey hair, a ragged sackcloth tunic, bare feet with a bronze ring round one ankle. "
              "The old bull-horned smith whose waist he holds is the man in the THIRD attached picture: enormous, deep bronze skin, bull horns, cropped copper-brown hair, a burned leather apron, and NO beard. "
              "Take their faces from those pictures and keep both figures small and in the same place, the taller grey one fastening the clasp at the smith's waist. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p5_a2': ('p5_a2_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the shut gateway with the heaped black stones and the blue light leaking through, the seated horned commander in the iron collar with chained wrists, "
              "his face, his sleeveless shirt and burn-scarred arms, the armour on the floor, the kneeling girl, the people in the background, the colours, rendering and finish. "
              "Change one thing only: his horns. Both of his great black horns are still whole, glossy and unbroken. The horn on the left of the picture is drawn as a broken stump with glowing red cracks; "
              "redraw it as a complete smooth black horn, the mirror of the other one, curving the same way. No cracks and no red glow on either horn. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    'p5_a4': ('p5_a4_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the commander with the broken horn standing before the black stele, the ring of planted spears, the girl among them, "
              "the stonecutter at the back of the stele, the glowing blue-green lava plain and the road, the black-rock city, the colours, rendering and finish. "
              "Change one thing only: remove every branch of pink-white blossom and every flower petal from the picture, in the top left corner, the bottom left and the bottom right. "
              "In their place there is only dark rock, and drifting in the air are fine grey ash and small blue-green motes of light. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 11-14 主会话查图：鸦旗二幕「后颈一箭」那个兽耳弓手，弓弦上半截画成了弯弯曲曲的一道，下半截没落到弓的下梢、落在他背上；
    # 查3 又指出白鹿后颈已经钉着那一箭，他手里却还扣着一支箭。场面写的是刚松了弦。照场面改：弓上没有箭，右手刚松开，弦回成一根直线。
    'p3_e2': ('p3_e2_a0.png',
              "Edit the attached picture. Keep the composition and the low camera behind the beast-eared archer, his grey-brown animal ears and messy ash-brown hair, his heavy snow-dusted coat, "
              "the quiver on his back, his left arm stretched out to the right holding the bow at its middle, the bow itself, the great white antlered stag on the far slope with the dark arrow in the back of its neck, "
              "the storm of snow over the mountains, the cart and the running figures far below, the colours, the rendering and the finish exactly as they are. Change only the following. "
              "The arrow has already been loosed: it is the one dark arrow now buried in the back of the stag's neck. So there is NO arrow on the bow and none in his hand. "
              "His right hand has just let go of the string: it is open and relaxed beside his cheek, the fingers slightly spread, holding nothing. "
              "The bowstring has snapped back to rest: one single straight string running from the upper tip of the bow to the lower tip, close to the bow, with only a faint blur of vibration along it. "
              "Remove the arrow lying along the bow, the wavy line in the air and the line that ends on his back." + " There is no moon and no crescent anywhere. No text, no letters, no numbers, no logo, no frame. Landscape picture, aspect ratio 3:2."),
    # 11-14 主会话查图：湾的喉咙，海族守潮人左手的口子从掌心一直划到手腕。改成只在掌心，手腕和小臂上的鳞干干净净。
    'p5_j3': ('p5_j3_a0.png',
              "Redraw the attached picture and keep everything about it exactly the same: the same composition and camera, the kneeling sea-haired woman with her silver fin crown and soaked deep blue robe, "
              "her open mouth, the spiral shell in her other hand, her outstretched arm with its pale scales, the glowing blue lines running through the dark water, the great wave, the cliffs and the frightened people behind, "
              "the colours, rendering and finish. Change one thing only: the wound on her outstretched hand. "
              "It is one short cut across the middle of her open palm only, from the base of the fingers toward the heel of the hand, and it stops well before the wrist. "
              "Her wrist and forearm are clean and unmarked, the scales whole, with no cut, no red line and no blood on them. A few drops of blood fall from the palm into the water. "
              "There is no moon and no crescent anywhere. No text, no logo, no frame. Landscape picture, aspect ratio 3:2."),
}

# 11-14 子任务查图（查1、查6）指出来、主会话放大核对过的，第二批。都拿原图（_a0）当底只改那几处。
_KEEP = ("Edit the attached picture. Keep every person, their faces, poses, clothes and places, the setting, the composition, the camera, the light, "
         "the colours, the rendering and the finish exactly as they are. Change only the following. ")
_TAIL = " There is no moon and no crescent anywhere. No text, no letters, no numbers, no logo, no frame. Landscape picture, aspect ratio 3:2."
_NIKO_EAR = ("The young man with long white hair and two drooping white dog ears has, beside his face, a small human ear showing among his hair; "
             "he has no human ears, only the two drooping white dog ears. Cover that place with his white hair so that no human ear shows anywhere.")
FIX.update({
    # p1_a2 头一回（从 _a0 改，那一稿留作 _a1）几乎没改动：心形还在，篮子还是十一只。篮子的数难改，不再追，第二回只改领口那颗心形的白石。
    'p1_a2': ('p1_a2_a1.png', _KEEP +
              "Look at the high stand-up collar of the tall grey-robed man holding the lantern: pinned at the front of the collar hangs a small white pendant shaped like a HEART. "
              "Replace that heart with a small, rough, irregular white stone, lumpy and uneven like a worn tooth or a pebble from a riverbed, with no point at the bottom and no notch at the top. "
              "Nothing heart-shaped anywhere in the picture." + _TAIL),
    'p1_a3': ('p1_a3_a0.png', _KEEP +
              "The old man's hand pressed flat on the carved stone is at the end of his RIGHT arm, so it must be a right hand: we see the back of the hand, the four fingers point up, "
              "and the thumb lies on the LEFT side of the hand as we look at it. Redraw only that hand so; it stays flat on the stone in the same place." + _TAIL),
    'p1_b1': ('p1_b1_a0.png', _KEEP +
              "Remove the wooden cross hanging on the wall behind the sickbed. In its place hang a small plain iron wall-sconce holding one white candle, unlit. No cross anywhere in the picture." + _TAIL),
    'p1_b4': ('p1_b4_a0.png', _KEEP +
              "The white candle on the old grave is wrong: it is drawn as a thick whole candle with a flame. Make it a short, thin stub of white candle that has never been lit: "
              "a clean white wick, no flame, no glow, no melted wax. The pebble beside it stays." + _TAIL),
    'p1_c4': ('p1_c4_a0.png', _KEEP +
              "One, the grey ox on the left: its horn is drawn large, pale and curved against the open blue sky, like a crescent. Make its horns short, thick and nearly straight, darker in colour, "
              "and let them overlap the leaves and the ox's own head rather than standing alone against the sky. "
              "Two, the young man lying in the grass: on his lower leg the rolled-up trouser cuff floats in the middle of the bare calf. The trouser leg is rolled up to just below the knee: "
              "the cloth covers the thigh and the knee and ends there in the rolled cuff, and the bare shin and foot below it." + _TAIL),
    'p1_d2': ('p1_d2_a0.png', _KEEP + _NIKO_EAR + _TAIL),
    'p1_d3': ('p1_d3_a0.png', _KEEP + _NIKO_EAR + _TAIL),
    'p1_d4': ('p1_d4_a0.png', _KEEP + _NIKO_EAR + _TAIL),
    'p2_a1': ('p2_a1_a0.png', _KEEP +
              "The cavalry lance held in the man's left fist does not continue through his hand: above the fist it is a thin dark wooden shaft slanting one way, below the fist it turns into a wide pale blade slanting the other way. "
              "Make it one single straight lance: the same dark wooden shaft continues through his fist in exactly the same straight line, down to its butt, with no blade below the hand." + _TAIL),
    'p2_a2': ('p2_a2_a0.png', _KEEP +
              "One, the small barefoot girl in the big curly fleece coat has one arm too many. She has exactly two arms: her right hand holds the hand of the girl beside her, and her left hand hangs at her side; "
              "her shoes hang by their laces round her neck with no hand holding them. Remove the extra hand and forearm that come up out of the fleece sleeve to hold the laces at her chest. "
              "Two, the white bow on the guide's back: its upper end stands alone against the night sky as a pale curve, like a crescent. Shorten and turn the bow so that its upper tip lies behind his hair and scarf and does not reach into the open sky." + _TAIL),
    'p2_b3': ('p2_b3_a0.png', _KEEP +
              "The young man's pince-nez is clipped onto his cheek below his eye. Put it where it belongs: the small gold clip pinches the bridge of his nose and the two round lenses sit in front of his eyes. "
              "Nothing is clipped to his cheek." + _TAIL),
    'p5_h3': ('p5_h3_a0.png', _KEEP +
              "The bull-horned man's two horns are bare: remove the iron rings and the padlocks hanging from both horns. The shackles and locks on his wrists stay as they are." + _TAIL),
    'p5_h4': ('p5_h4_a0.png', _KEEP +
              "The bull-horned man's two horns are bare: remove the iron rings and the padlocks hanging from both horns. The shackles and locks on his wrists stay as they are." + _TAIL),
    'p5_j3': ('p5_j3_a0.png', _KEEP +
              "One, the wound on her outstretched hand: it is one short cut across the middle of her open palm only, and it stops well before the wrist. Her wrist and forearm are clean and unmarked, the scales whole, "
              "with no cut, no red line and no blood on them. A few drops of blood fall from the palm into the water. "
              "Two, her kneeling leg on the left of the picture: the knee rests on the rock and the shin lies along the rock behind it, so the foot is behind her and mostly hidden under her robe. "
              "No foot shows beside her knee pointing at us." + _TAIL),
    'p6_a1': ('p6_a1_a0.png', _KEEP +
              "The black-gloved hand holding the ladle has a stray pale flesh-coloured finger sticking out between the glove and the ladle handle. Remove it: the hand is one black-gloved hand "
              "with a thumb and four fingers wrapped round the ladle handle, and nothing pale between them." + _TAIL),
    'p6_a3': ('p6_a3_a0.png', _KEEP +
              "The two red banners far off in the camp carry crosses, one with rays like a church emblem. Make both banners plain dark red cloth with no cross and no emblem. No cross anywhere in the picture." + _TAIL),
    'p6_b2': ('p6_b2_a0.png', _KEEP +
              "Add one arrow standing upright in the grass a single step to the right of the black stone, its point stuck in the ground and its grey fletching at the top, perfectly still." + _TAIL),
    'p6_b4': ('p6_b4_a0.png', _KEEP +
              "The blue-haired man setting the loaf on the stone is in his mid-forties and his face is quiet and sad: his mouth is level, not smiling; there are fine lines at the corners of his eyes, "
              "and a little grey shows in his blue hair at the temples. Keep his face, hair, pose and clothes otherwise as they are." + _TAIL),
    'p6_c4': ('p6_c4_a0.png', _KEEP +
              "One, the two white-robed priests walking down the mountain path with lanterns have a gold cross on the back of their robes; remove both crosses, the robes are plain white. No cross anywhere in the picture. "
              "Two, the kneeling shaven-headed man's face is quiet and sorrowful, not smiling: his mouth is level and his lips slightly parted as if he were humming low; his eyes stay half closed." + _TAIL),
    'p6_d1': ('p6_d1_a0.png', _KEEP +
              "The tall thin man in the dark robe holding up the lamp is a night-wing whose wings are membranous like a bat's, grey-brown, never feathered. His right wing, folded neatly behind him, "
              "is drawn as a black feathered bird wing; redraw it as a folded grey-brown membranous wing with thin bony ribs. His burnt left wing, with its charred holes, stays as it is." + _TAIL),
    'p6_d3': (('p6_d3_a0.png', os.path.join(OUT, '_ident', 's6a_reva_casual.png')),
              "Edit the FIRST attached picture. Keep every other person, their faces, poses, clothes and places, the setting, the composition, the camera, the light, the colours, the rendering and the finish exactly as they are. Change only the following. "
              "One, the walls and pillars of the station are carved with readable numbers; replace every carved number with rows of plain short upright tally strokes cut into the stone, so that no digit or letter can be read anywhere. "
              "Two, the big barefoot woman walking behind the man at the front, with blood running from the torn soles of her feet, is the troll woman shown in the SECOND attached picture: "
              "a head taller than everyone else, rough grey-teal hide, a short dark horn stub on each side of the forehead, coarse rust-red hair in one braid wound round her neck, a white scar on her chin. "
              "Take her face, hair, skin and clothes from that picture; keep her in the same place and pose, barefoot, with the blood on her soles. "
              "Three, the young man carrying a child on his back has a reddish-brown mark on his left cheek; make it a smudge of grey-black coal dust." + _TAIL),
    # p4_e4 头一回改的那一稿（_a1）拳头攥起来了，可指缝里露出来的还是一座带顶棚的小井。拿 _a1 当底再改一回。
    'p4_e4': ('p4_e4_a1.png', _KEEP +
              "Her right hand is a tight fist hanging at her side. What shows between her fingers is wrong: it is a little three-dimensional model of a well with a roof. "
              "Remove that model completely. Inside her fist she holds a FLAT round bronze badge the size of a small coin; only a thin curved sliver of its edge shows between two of her fingers, "
              "dull bronze, with no roof, no bucket and nothing standing up from it. The fist is closed and the badge is almost hidden." + _TAIL),
    # p6_d4 头一回改的那一稿（_a1）把利诺斯的翅膀画成了黑羽翼，他的立绘是灰褐的膜翼。拿 _a1 当底只改翅膀。
    'p6_d4': ('p6_d4_a1.png', _KEEP +
              "The silver-haired man sitting on the bench with the unlit copper lamp is a night-wing whose wings are membranous like a bat's, grey-brown, never feathered. "
              "Redraw only his wings: his right wing is a neatly folded grey-brown membranous wing with thin bony ribs; his left wing is the same kind but its outer half is burnt through into ragged charred holes, "
              "so that it cannot fold and drags behind him. No feathers on either wing. The lamp stays unlit." + _TAIL),
    # 11-14 子任务查图（查5）指出来、主会话放大核对过的，第三批。
    'p5_b3': ('p5_b3_a0.png', _KEEP +
              "The thin priest in the faded red robe reaching into the tiny flame on the silver dish: only his fingers and the palm of his reaching hand have turned black. "
              "His wrist and forearm are his normal skin colour, and no blood runs from his sleeve or down his arm onto the floor; remove the black from his forearm and the streams of blood from his sleeve. "
              "The nobles around the table stay exactly as they are." + _TAIL),
    'p5_c3': (('p5_c3_a0.png', os.path.join(OUT, '_ident', 's5b_dora_formal.png')),
              "Edit the FIRST attached picture. Keep every other person, their faces, poses, clothes and places, the white hall, the judges, the benches, the crowd, the composition, the camera, the light, "
              "the colours, the rendering and the finish exactly as they are. Change only the following. "
              "The person seated on the bench at the right edge, looking up at the copper-haired woman with an open mouth, is drawn as a young fair-haired man; that is wrong. "
              "It is the woman in the SECOND attached picture, a dock porter of forty-seven: a big, broad-shouldered woman with straw-yellow hair, cornflower-blue eyes, a wind-reddened freckled face with fine lines, "
              "a clean blue jacket with a dented tin tag on a cord outside it. Take her face, hair and build from that picture. She sits in the same place, looks up at the copper-haired woman with her mouth open in wonder, "
              "her big hands on her knees." + _TAIL),
    'p5_d3': ('p5_d3_a0.png', _KEEP +
              "The tall thin shaved-headed apprentice has one arm too many. He has exactly two arms: his LEFT hand is raised in front of him with the fingers spread, counting the strokes on his fingertips, "
              "and his RIGHT hand holds the bell rope. Remove the extra hand and forearm that come out of his sleeve to point at the raised hand." + _TAIL),
    'p5_d4': ('p5_d4_a0.png', _KEEP +
              "The young woman with the red-brown braid has a small human ear showing at the side of her face, under her hair; she has no human ears, only the two tall red-brown fox ears on top of her head. "
              "Cover that place with her red-brown hair so that no human ear shows anywhere." + _TAIL),
    'p5_d_hakan': ('p5_d_hakan_a0.png', _KEEP +
                   "The man's yellow eyes have round pupils; he is of a snake-like people and his pupils are narrow vertical slits like a snake's. Redraw only his pupils as thin vertical slits in both eyes." + _TAIL),
    'p5_e4': ('p5_e4_a0.png', _KEEP +
              "One, the rough grey stones standing all over the marsh behind are carved with crosses, like a graveyard of crosses; replace every cross with one short row of small uneven upright tally strokes, "
              "so that no cross shape can be seen anywhere. "
              "Two, the new copper stele in the foreground is carved with rows of identical T-shapes that look like letters; replace them with rows of small uneven marks, short upright and slanting strokes of different lengths, "
              "with no letter or repeated symbol." + _TAIL),
    # p5_h1 头一回（_a1）把角改成了一根横着贯穿画面的长角，跟这个人别的几幅（角往外再往上弯）对不上。角是他的样子，照原图留着，第二回只改肩上的紫纹。
    'p5_h1': ('p5_h1_a0.png', _KEEP +
              "Keep his horns exactly as they are in the attached picture. "
              "His skin is unmarked except for an old broad burn scar across his shoulders: remove the glowing purple branching marks from his shoulder and arm, and keep only a plain, darker, non-glowing burn scar there. "
              "The violet light of the lightning on the chain may still tint his skin, but no glowing lines are drawn on it." + _TAIL),
    'p5_h2': ('p5_h2_a0.png', _KEEP +
              "The bull-horned giant's two horns are bare: remove the copper bands round the roots of both horns. The shackles and locks on his wrists stay as they are." + _TAIL),
})

# 11-14 子任务查图（查3）指出来、主会话放大核对过的，第四批。p3_e2 在上头 FIX 里照场面改了。
_EAR = ("has, at the side of his head under his hair, a small human ear showing; he has no human ears, only the two {ears} on top of his head. "
        "Cover that place with his {hair} so that no human ear shows anywhere.")
FIX.update({
    'p3_d1': ('p3_d1_a0.png', _KEEP +
              "The rock wall on the right of the passage is covered with scratched tally lines and crude marks. Among them is a five-pointed star scratched inside a circle, like a pentagram. "
              "Replace that one mark with a short row of crude upright tally scratches like the others, so that no star and no circle can be seen anywhere on the walls." + _TAIL),
    'p3_d2': ('p3_d2_a0.png', _KEEP +
              "One, the swordswoman's left hand gripping the root: the blood is drawn in branching streams over the back of her hand and down across her wrist. That is wrong. "
              "The only wound on that hand is the split web between her thumb and forefinger: a little blood runs from that one place onto the root and drips down. "
              "The back of her hand and her wrist are clean, wet only with spring water and white sap. "
              "Two, the cut on the lower edge of that forearm: make it a small shallow scratch, a thin pale red line with no blood running from it." + _TAIL),
    'p3_d4': ('p3_d4_a0.png', _KEEP +
              "The raven-haired swordswoman sitting on the right holds the new sword out at arm's length, and she cannot take her eyes off it. Her eyes now look straight at us; "
              "turn only her eyes so that she looks to the right and a little up, along the blade toward its tip, fixed on the steel. Her head, her face and the sword stay exactly where they are." + _TAIL),
    'p3_e1': ('p3_e1_a0.png', _KEEP +
              "The beast-eared archer standing beside her " + _EAR.format(ears='grey-brown animal ears', hair='ash-brown hair') + _TAIL),
    'p3_e3': ('p3_e3_a0.png', _KEEP +
              "One, on the chest of the half-orc lancer's leather jerkin there is a white cloth patch with a black crow on it. Remove that patch: the jerkin there is plain worn leather, spattered like the rest. "
              "Two, the banners and pennants carried by the column of riders far behind: their cloth is plain grey canvas with one clumsy white bird stitched on it, lopsided, one wing sewn crooked. "
              "No black bird anywhere in the picture." + _TAIL),
    'p3_e4': ('p3_e4_a0.png', _KEEP +
              "The young dwarf sitting against the wall in the near foreground is not wounded: the back of his hand resting on his knee and his wrist are splashed with blood. "
              "Remove all the blood from his hand and wrist; they are only grey with dust like the rest of him. The stocky dwarf in the doorway keeps his split, bleeding knuckles." + _TAIL),
    'p3_f3': ('p3_f3_a0.png', _KEEP +
              "One, the little sea-blue-haired girl's small blue shawl is fastened at the front with a gold cord tied in an ornamental knot; replace that knot with one plain round button of dull silver. "
              "Two, the grey-haired girl standing at the far end of the table has a small shield-shaped badge with a cross-like mark on each lapel of her short black jacket; "
              "remove both badges, the lapels are plain with grey piping." + _TAIL),
    'p3_f4': ('p3_f4_a0.png', _KEEP +
              "The lamps hung on the lines across the long street beyond the fire are drawn as round ribbed paper lanterns with tassels hanging below. "
              "Replace every one of them with a small iron-framed glass street lamp, one with red glass and the next with white glass, one red and one white all the way down the street, "
              "each glowing softly in the falling rain. No paper lanterns, no ribs and no tassels anywhere." + _TAIL),
    'p4_a1': ('p4_a1_a0.png', _KEEP +
              "The fox-eared messenger standing in the road " + _EAR.format(ears='russet-brown fox ears', hair='short russet hair') + _TAIL),
    'p4_a3': ('p4_a3_a0.png', _KEEP +
              "The copper-haired woman on the left: the wrist of her hanging left hand is wound with strips of white cloth, and her outstretched right forearm that holds out the bread is also wrapped with white cloth strips. "
              "Remove all those cloth strips: her wrist and her forearm are bare, clean and unmarked." + _TAIL),
    'p4_b3': ('p4_b3_a0.png', _KEEP +
              "The ground round the open black boxes, on the right and on the left of the picture, is drawn as blood-red mud with red puddles. "
              "Make it ordinary dark brown wet earth, stained darker in patches, with grey-brown puddles of rain water. No red on the ground anywhere." + _TAIL),
    'p4_b4': ('p4_b4_a0.png', _KEEP +
              "On the wagon in the background, the huge bull-horned man knocking in a nail has three horns. He has exactly two horns, one on each side of his head, both curving outward; "
              "remove the third horn that curls up from the top of his head." + _TAIL),
    'p4_c2': ('p4_c2_a0.png', _KEEP +
              "The stone signpost at the crossroads is shaped like a cross with two arms and has letter-like carvings on it. "
              "Make it one rough stone pillar with only ONE short stone arm sticking out to one side near the top, like a waymark: no second arm, nothing shaped like a cross, and no letters or carvings on it." + _TAIL),
    'p4_c4': ('p4_c4_a0.png', _KEEP +
              "The dwarf cook is seen directly from behind, looking out over the river. "
              "One, her two boots are drawn from the front with their laces facing us. Turn them so that we see them from behind: the heels and the backs of the boots face us and the toes point away toward the river. "
              "Two, from behind we see only the ties of her apron: the apron strings are tied in a bow at the small of her back, and below the bow hangs the back of her wool skirt, the same colour as now. "
              "Remove the patched front of the apron that hangs down her back." + _TAIL),
})

# 11-14 子任务查图（查2）指出来、主会话放大核对过的，第五批。
_MORT = ("a small pale boy of five: short, slightly messy dark hair, nearly black; pale ice-blue eyes; small rounded ears like a human child's; NO horns at all; "
         "his knuckles and brow faintly gleaming bone-white")
FIX.update({
    'p2_d4': ('p2_d4_a0.png', _KEEP +
              "The tiefling's hand pressed flat against the standing stone has only four digits. It is his LEFT hand seen from the back: give it exactly one thumb and four fingers, "
              "the four fingers spread up toward the two carved marks and the thumb lying lower down on the right side of the hand, toward his wrist, also pressed flat. Keep the grey ash on his fingers." + _TAIL),
    'p2_d_florian': ('p2_d_florian_a0.png', _KEEP +
                     "One, the red-haired soldier is blowing the brass bugle: its mouthpiece is pressed between his lips in the middle of his mouth, his lips tight round it and his cheeks hard; "
                     "it does not rest against his cheek beside his mouth. Two, the top rim of his ear on the right of the picture has a small V-shaped notch cut into it." + _TAIL),
    'p2_e1': ('p2_e1_a0.png', _KEEP +
              "The bows thrust out of the reeds at the left and right edges of the picture are fully drawn and aimed down the path. Each bowstring is pulled back toward the reeds in a sharp V: "
              "from the upper tip and from the lower tip of the bow the two halves of the string run back out of the picture into the reeds, to one point where a hidden drawing hand holds it, "
              "and the back end of each arrow sits on its string at that point. No string runs straight from tip to tip in front of the arrows, and no string crosses the bow itself." + _TAIL),
    'p2_e2': ('p2_e2_a0.png', _KEEP +
              "The lizardfolk egg keeper on the left holds the long reed pipe in one hand, and that hand and forearm are drawn as a human hand with smooth pink skin and round fingernails. "
              "Make them a lizardfolk hand and forearm like her other one resting on the mud: reed-yellow scales striped brown, four long fingers with short dark claws." + _TAIL),
    'p2_e3': ('p2_e3_a0.png', _KEEP +
              "One, two peoples stand on the opposite rims of the spring. On the left, a little behind the old lizardfolk elder, stands a group of five or six other lizardfolk, adults of different sizes "
              "with scales from reed-yellow to grey-green, in woven reed cloaks and aprons. On the right, a little behind the horned headman, stands a group of five or six horned demon-kin of the west, of several kinds: "
              "charcoal-skinned ember-horned men and women, a pale bull-horned one, a grey-skinned one with curled horns, in plain dark wool. Both groups are empty-handed and quiet, watching across the water; "
              "nobody carries a weapon. The grey-haired girl in the middle stays alone between them. "
              "Two, the tip of the old elder's tail lying on the ground at the bottom left is blunt and broken off, not pointed." + _TAIL),
    'p3_a1': ('p3_a1_a0.png', _KEEP +
              "The hand lying flat on the open register in the near foreground has six digits. Redraw it in the same place and pose with exactly one thumb and four fingers; "
              "the little finger, on the side away from the thumb, is bent and crooked." + _TAIL),
    'p3_a3': ('p3_a3_a0.png', _KEEP +
              "The boy sitting on the cot inside the tent, wrapped in the grey blanket and holding the bone bell-clapper, is drawn with two black horns, pale blond hair and golden eyes; that is wrong. "
              "He is " + _MORT + ". Keep his face, his size, his pose and the blanket otherwise as they are." + _TAIL),
    'p3_a4': ('p3_a4_a0.png', _KEEP +
              "The child holding a fold of the pale man's sleeve is drawn with a horn, pointed ears and pale ash hair; that is wrong. "
              "He is " + _MORT + ". Keep him in full profile in the same place and pose, his small fist still holding the sleeve." + _TAIL),
    'p3_b2': ('p3_b2_a0.png', _KEEP +
              "The front half of the cow-horn bugle flying out of the old man's hand is carved with two square panels of seal-like characters. "
              "Replace them with plain carved rings round the horn, simple grooves with no characters and no symbols." + _TAIL),
    'p3_c2': ('p3_c2_a0.png', _KEEP +
              "One, the copper-haired woman is human: the pointed elf-like ear showing on the right of the picture is wrong; make it a small rounded human ear, partly covered by her loose hair. "
              "Two, the cut at the outer end of her left eyebrow, on the right of the picture, is a short fresh cut that is bleeding, and a little blood has run from it down into the outer corner of that eye; "
              "remove the thin red line that runs straight down through the eye. "
              "Three, the iron furnace-hook raised over the top of the picture bends round in a large half-circle before its square end. Make its end a short, square, right-angled hook: "
              "the straight pole turns sharply once at a right angle into a short square-cut hook, with no curve and no half-circle; its tip stays in the air right above her head." + _TAIL),
    'p3_c3': ('p3_c3_a0.png', _KEEP +
              "The two banners hanging before the palace doors each carry a gold four-pointed star. Replace the star on each with a golden kite: "
              "a bird of prey with its wings spread wide, embroidered in gold on the same cloth." + _TAIL),
})

# 11-14 开岭（p5_m1、p5_m2、p5_m4）：m1 屋脊左头卷起一个大弯钩、m4 屋檐上立着四根弯骨头，贴着夜空都像月牙，拿掉。m2 她的头发画成了齐下巴的短发，七城的年月她头发留到肩、在脑后低低地束着（照她人物条的样子那一栏），只改头发
FIX['p5_m1'] = ('p5_m1_a0.png', _KEEP +
                "The long pale whale-bone ridge on top of the longhall roof curls up at its left end into a big curved white hook against the night sky, "
                "and small curved spikes stick up along the ridge. Remove the hook and all the spikes: the ridge is one straight, smooth pale bone that ends "
                "bluntly at the left in a plain rounded stump bound with a dark iron band, lying flat along the roof. Nothing curved stands up against the sky. "
                "The old woman, the six children, the frost picture on the ice, the open lit doorway, the mountains and the aurora stay exactly as they are." + _TAIL)
FIX['p5_m2'] = ('p5_m2_a0.png', _KEEP +
                "The tall woman standing on the right in the long grey-brown coat has short hair cut to the jaw. Change only her hair: "
                "deep gold-brown hair with an old-copper sheen, grown down to her shoulders and gathered low at the nape of her neck into a short tail tied with a plain cord, "
                "a few loose locks falling beside her temple and cheek, so that in this side view the tied tail shows at the back of her neck. "
                "Her face, her pale gold eye, her expression, her coat, her sword, the bell at her wrist and her hands stay exactly as they are, "
                "and so do the blonde girl with the birch pole, the old bearded man with the ledger, the carts, the oxen, the blocked pass and the longhall." + _TAIL)
FIX['p5_m4'] = ('p5_m4_a0.png', _KEEP +
                "Along the snowy eave of the longhall at the top of the picture stand four big curved pale tusks pointing up into the starry night sky; "
                "they look like crescents. Remove all four: where they were, the eave is only plain snow-covered log ends and wooden roof beams, and behind them the starry sky. "
                "Nothing curved stands up against the sky. The young man with the lantern, the young woman drawing the frost line on the door, the door, "
                "the frost line, the snow and the valley stay exactly as they are." + _TAIL)

# 11-14 门楣二幕（p5_k2）：账碑画成了立在河岸石墙顶上的一排圆顶石板，远看是一排墓碑。门楣主线写的是一面接一面嵌在河岸的石墙里，拿原图当底只改账碑
FIX['p5_k2'] = ('p5_k2_a0.png', _KEEP +
                "Along the top of the stone river wall behind the three women stands a long row of tall round-topped slabs that look like gravestones. Remove all of them, "
                "so that nothing at all stands on top of the wall. Instead, the account plaques are flat, square bronze plates set flush into the vertical face of the river wall itself, "
                "one beside another in a long even row running along the wall into the distance, each plate a little taller than a man, framed by the wall's stone blocks, "
                "its surface covered with rows of small cut marks that are not letters, catching the lamp light. "
                "The three women, the benches, the lamps, the river, the city on the hill and the mist stay exactly as they are." + _TAIL)

# p3_e3 头一回（_a1）补丁和黑鸦都拿掉了、旗成了灰布白鸟，可打头那面大旗上的白鸟缝成了一团圆加两道交叉的弯，远看像骷髅加交叉骨。拿 _a1 当底只改那一面旗上的图样。
FIX['p3_e3'] = ('p3_e3_a1.png', _KEEP +
                "On the large dark grey banner at the front of the column of riders far behind, the white figure stitched on the cloth is unclear and could be mistaken for a skull and crossed bones. "
                "Redraw only that figure as a clumsy white bird seen from the side, sewn in thick white thread: a small round head with a short beak, one wing raised and sewn badly crooked, a short tail and two thin legs; "
                "clearly a bird, with nothing that looks like a skull or bones. The smaller pennants keep their white birds as they are." + _TAIL)

# p2_e1 头一回（_a1）弦收成 V 了，可一打弓只剩左右两张、握弓的手没了，弓悬在芦苇里。拿 _a1 当底补上握弓的鳞手。
FIX['p2_e1'] = ('p2_e1_a1.png', _KEEP +
                "Each of the two drawn bows at the left and right edges of the picture must be held by a hand, and none is drawn now. Add them. "
                "At the left edge, a lizardfolk hand with reed-yellow scales striped brown and four long fingers with short dark claws grips that bow at its leather-wrapped middle, "
                "the arrow resting across the back of the hand, its scaled forearm reaching in from the reeds at the left edge. At the right edge, the same kind of scaled four-fingered hand "
                "grips that bow at its middle, its forearm reaching in from the reeds at the right edge. Keep the bows, the drawn strings and the arrows exactly as they are. "
                "Deeper among the reed stems on both sides, a few more iron arrowheads glint, aimed down the path." + _TAIL)


def fix_srcs(key):
    srcs = FIX[key][0]
    return [s if os.path.isabs(s) else os.path.join(OUT, s) for s in ((srcs,) if isinstance(srcs, str) else srcs)]


# ---------- 长卷的接缝 ----------
# 一段接一段出，接缝多半接得上；接不上的照纷争纪那一本（gpt_cg2.py 的 jNN、小样_纷争纪书/road_strip.py）补：
# 以缝为中心切一块 1536×1024（左边那一段的右半、右边那一段的左半，jNN_in.png），拿它当底只重画当中那三分之一，
# 再对齐、校色、在两边各找一道差得最少的缝并回去，写回两段（原图头一回改以前留作 rNN_a0.png）。
#   python gpt_cg3.py --cut j02        切 j02_in.png（r02 和 r03 之间那一道）
#   python gpt_cg3.py j02              重画
#   python gpt_cg3.py --merge j02      并回 r02、r03
JOIN_LEAD = ("Edit the attached picture. It shows the place where two sections of one long painted scroll meet: the left half belongs to one section and the right half to the next, "
             "and down the middle the two do not join cleanly. "
             "Keep the left third and the right third of the picture exactly as they are: the same shapes in the same places, the same colours, the same light. Repaint only the middle third between them, so that the two run into each other without any break. ")
JOIN_TAIL = (" Through the middle third the long white wall runs on unbroken at exactly the same height, with the same white stone, the same battlements and the same things hanging on it as on either side. "
             "The two strips of open level ground beside the wall, just behind it and just in front of it, stay bare through the middle third: short grass, flat earth, a few small stones. "
             "Do not put any large new object, building, figure or monument in the middle third. "
             "Paint the middle in exactly the hand of the rest of the picture: large calm flat colour shapes layered like cut paper, thin lighter echo lines along the edges, soft inner gradients only, " + GRAIN + ", "
             "everything small and seen from high above. The viewpoint, the height of the horizon and the scale stay exactly the same across the whole picture, "
             "and there is no vertical seam, line or sudden change of colour anywhere.")
JOINS = {      # 第几道缝: 这一道要怎么接（看过接缝以后照实写）
    # r02 右上角画成了压着雨的深灰蓝云，r03 左头的天是淡一些的灰紫黄昏，天在缝上差一截；林子和地是接上的。
    2: ("The sky changes gradually across the middle third, the dark rain-grey clouds of the left third thinning out into the softer grey-violet dusk clouds of the right third, "
        "with no straight vertical edge anywhere in the clouds. The forest in the lower part runs on unbroken from the left third into the right third, its treetops at the same height. "
        "Behind the wall the dim plain with its pale patches of half-wild wheat runs on unbroken, and the dark stepped stone seats on the horizon stay where they are."),
    # r03 右边是满天星的深夜，r04 左头的天和墙北的地亮了一截；墙南下边左是临河的王城，右是河岸底下的铁匠巷，到缝上一刀切开。
    3: ("The sky and the land behind the wall change gradually across the middle third from the deep blue-black night with small stars of the left third into the dim night clouds of the right third, "
        "with no straight vertical edge anywhere in the sky or on the land. "
        "In the lower part, the great riverside city of the left third, with its palace at the top of the long flight of pale steps and the plain sword standing in a stone at the foot of those steps, stays exactly as it is; "
        "its houses and its low river wall end within the middle third, and there the dark river at the bottom bends away out of the bottom of the picture, "
        "while the dark rocky riverbank rises and runs into the lane of smithies of the right third, whose first house begins just inside the right third."),
    # r06 右头是下着雨的深蓝夜、墙脚下安安静静的几间房和点着灯的长屋，r07 左头一上来天和墙北的地就是火光的红。
    # 头一回（j06_v1）天接上了，墙南那一半照旧留着一道竖直的切口：红盐地和烧着的城的城墙都在缝上齐齐断开，烟的阴影也从缝上起。
    # 第二回拿并好的那一块当底，只说下半截。
    6: ("The sky and the land behind the wall already join well: keep them as they are. "
        "In the lower half, in front of the wall, a straight vertical line still runs down the middle of the picture where the two sections were cut: remove it completely. "
        "The pale red cracked salt flat at the bottom left ends in a ragged, natural, curving edge within the middle third, and wet grey-green grass continues beyond it. "
        "The dark smoke of the burning town on the right drifts up and to the left in soft rounded billows that thin out gradually over the wet grass, with no straight edge; "
        "the grass under the smoke is only a little darker. The burning town keeps its gate, its fire and the lance lying before it, "
        "but its outer wall begins a little further to the right than now, so that some open wet grass lies between the salt flat and the town. "
        "The quiet little houses and the long lit hall at the foot of the wall on the left stay exactly as they are."),
    # r05 右下的船坞和红水在缝上齐齐切断，r06 左下是草地和浅红的盐地。
    5: ("The dull red glow low on the far horizon runs on evenly through the middle third, and the dark plain behind the wall runs on unbroken. "
        "In the lower part, the old stone shipyard dock of the left third, with its sheds, its half-built ship and its lanterns, stays as it is but ends naturally within the middle third with the end of its stone quay; "
        "the dark red river of the left third bends away out of the bottom of the picture within the middle third, "
        "and beyond a strip of dark grass and stones the pale red cracked salt flat of the right third begins, its edge ragged and natural. No straight vertical line anywhere."),
    # 下面几道缝：墙在缝上两座塔挨着，r07|r08、r08|r09、r10|r11 天和地的明暗冷暖也差一截，下面的东西在缝上切断。
    7: ("Where two wall towers now stand side by side in the middle of the wall, keep only one of them, so that the towers stand at even, long intervals. "
        "The dark blue sky of the hour before dawn runs on evenly; the thin rain in the right third fades out gradually toward the left. Behind the wall the dark river winding through the plain runs on unbroken. "
        "In the lower part, the lonely lamp-lit road of the left third, with its small gate-towns, runs on through the middle third and leads to the gate of the great riverside city of the right third; "
        "the city keeps its palace, its long flight of pale steps with the broken crown and the climbing torches, and its reed huts by the water, "
        "but its outer wall and houses end in a natural rounded corner within the middle third instead of a straight cut."),
    8: ("Where two wall towers now stand side by side in the middle of the wall, keep only one of them, so that the towers stand at even, long intervals. "
        "The sky changes gradually across the middle third from the warm amber dawn of the left third into the brighter, cooler morning sky of the right third, "
        "and the land on both sides of the wall changes gradually in the same way, with no straight vertical edge anywhere. "
        "Behind the wall, the mine pit with its headframe and heap of rings on the left and the black volcano with its walled city on the right stay as they are, with open plain between them. "
        "In the lower part, the pale pebble river beach with its planted weapons and two small figures on the left, and its river, end naturally within the middle third, "
        "and the green fields, hedges and fences of the right third begin beyond them."),
    9: ("Where two wall towers now stand side by side in the middle of the wall, keep only one of them, so that the towers stand at even, long intervals. "
        "Everything else in the middle third stays exactly as it is and runs on unbroken: the sky, the marsh full of small standing stones behind the wall, "
        "and below, the river with the long row of upright stone boards along its bank and the fields beyond."),
    10: ("Where two wall towers now stand side by side in the middle of the wall, keep only one of them, so that the towers stand at even, long intervals. "
         "The sky changes gradually across the middle third from the warm golden late-afternoon clouds of the left third into the clear blue afternoon sky of the right third, "
         "and the land on both sides of the wall changes gradually from warm to cool in the same way, with no straight vertical edge anywhere. "
         "Behind the wall, the stone fortress on its rocky islet in the water on the left and the black glassy hills with the dark city and its bronze-gold slab on the right stay as they are, with open plain between them. "
         "In the lower part, the farmland of fields, hedges, roads and farmhouses runs on unbroken from left to right, and the roads join."),
    11: ("Where two wall towers now stand side by side in the middle of the wall, keep only one of them, so that the towers stand at even, long intervals. "
         "The golden sky, the railway gallery and the mountains behind the wall run on unbroken. "
         "In the lower part, the gate-town on the left with its gate, the patch of wheat burnt black and the two small figures with lamps stay exactly as they are; "
         "the town's last house ends naturally within the middle third, and the golden wheat fields run on beyond it."),
}


def join_prompt(n):
    t = JOINS.get(n, "The sky, the land and everything on it change gradually across the middle third from the way they are in the left third into the way they are in the right third.")
    return JOIN_LEAD + t + JOIN_TAIL + NO_MOON + NO_ARC + F.CLEAN + ' Landscape picture, aspect ratio 3:2.'


def _np():
    import numpy as np
    from PIL import Image
    return np, Image


def join_cut(n):
    np, Image = _np()
    a = Image.open(os.path.join(OUT, 'r%02d.png' % n)).convert('RGB')
    b = Image.open(os.path.join(OUT, 'r%02d.png' % (n + 1))).convert('RGB')
    W, H = a.size
    blk = Image.new('RGB', (W, H))
    blk.paste(a.crop((W // 2, 0, W, H)), (0, 0))
    blk.paste(b.crop((0, 0, W // 2, H)), (W // 2, 0))
    p = os.path.join(OUT, 'j%02d_in.png' % n)
    blk.save(p)
    print('切好', p)


def _fit(G, Wm, m):
    """把重画的 G 对齐到原来的 Wm：整像素平移，再逐通道线性校色，只拿两边那几块算（照 road_strip.py 的 fit）。"""
    np, _ = _np()
    g, w = G.mean(2), Wm.mean(2)
    best = (1e18, 0, 0)
    for step, rng in ((4, [(dy, dx) for dy in range(-24, 25, 4) for dx in range(-24, 25, 4)]), (1, None)):
        if rng is None:
            _, bx, by = best
            rng = [(dy, dx) for dy in range(by - 4, by + 5) for dx in range(bx - 4, bx + 5)]
        for dy, dx in rng:
            d = np.abs(np.roll(np.roll(g, dy, 0), dx, 1)[48:-48:step][:, m][:, ::step] - w[48:-48:step][:, m][:, ::step]).mean()
            if d < best[0]:
                best = (d, dx, dy)
    d0, dx, dy = best
    G = np.roll(np.roll(G, dy, 0), dx, 1)
    if dx > 0:
        G[:, :dx] = Wm[:, :dx]
    elif dx < 0:
        G[:, dx:] = Wm[:, dx:]
    if dy > 0:
        G[:dy] = Wm[:dy]
    elif dy < 0:
        G[dy:] = Wm[dy:]
    for ch in range(3):
        k, c = np.polyfit(G[48:-48, m, ch].ravel()[::7], Wm[48:-48, m, ch].ravel()[::7], 1)
        G[..., ch] = G[..., ch] * k + c
    after = np.abs(G[:, m] - Wm[:, m]).mean()
    return np.clip(G, 0, 255), '挪了 (%d, %d)，差 %.1f → %.1f' % (dx, dy, d0, after)


def _seam(cost):
    np, _ = _np()
    h, w = cost.shape
    acc = cost.copy()
    back = np.zeros((h, w), np.int8)
    for y in range(1, h):
        prev = acc[y - 1]
        stack = np.vstack([np.r_[np.inf, prev[:-1]], prev, np.r_[prev[1:], np.inf]])
        i = stack.argmin(0)
        acc[y] += stack[i, np.arange(w)]
        back[y] = i - 1
    x = np.empty(h, int)
    x[-1] = int(acc[-1].argmin())
    for y in range(h - 1, 0, -1):
        x[y - 1] = x[y] + back[y, x[y]]
    return x


def join_merge(n, feather=12):
    np, Image = _np()
    Wm = np.asarray(Image.open(os.path.join(OUT, 'j%02d_in.png' % n)).convert('RGB'), np.float32)
    G = Image.open(os.path.join(OUT, 'j%02d.png' % n)).convert('RGB')
    PH, PW = Wm.shape[:2]
    if G.size != (PW, PH):
        G = G.resize((PW, PH), Image.LANCZOS)
    G = np.asarray(G, np.float32).copy()
    el, er = (int(PW * 0.0625), int(PW * 0.306)), (int(PW * 0.694), int(PW * 0.9375))   # 两边拿来对齐、找缝的范围，当中三分之一是重画的
    m = np.zeros(PW, bool)
    m[el[0]:el[1]] = True
    m[er[0]:er[1]] = True
    G, msg = _fit(G, Wm, m)
    diff = np.abs(G - Wm).sum(2)
    k = np.ones(9) / 9
    diff = np.apply_along_axis(lambda r: np.convolve(r, k, 'same'), 1, diff)
    xl = _seam(diff[:, el[0]:el[1]]) + el[0]
    xr = _seam(diff[:, er[0]:er[1]]) + er[0]
    cols = np.arange(PW)[None, :]
    a = np.clip((cols - xl[:, None] + feather) / (2 * feather), 0, 1) * np.clip((xr[:, None] + feather - cols) / (2 * feather), 0, 1)
    R = Wm * (1 - a[..., None]) + G * a[..., None]
    R = Image.fromarray(np.clip(R + 0.5, 0, 255).astype(np.uint8))
    half = PW // 2
    for seg, box, at in ((n, (0, 0, half, PH), half), (n + 1, (half, 0, PW, PH), 0)):
        p = os.path.join(OUT, 'r%02d.png' % seg)
        a0 = os.path.join(OUT, 'r%02d_a0.png' % seg)
        im = Image.open(p)
        if not os.path.exists(a0):
            im.save(a0)
        im = im.convert('RGB')
        im.paste(R.crop(box), (at, 0))
        im.save(p)
    R.save(os.path.join(OUT, 'j%02d_并好.png' % n))
    print('并好 j%02d：%s，左缝 %d..%d，右缝 %d..%d' % (n, msg, xl.min(), xl.max(), xr.min(), xr.max()))


def join_tone(n, reach=384, strip=48, sig=24.0, lim=(0.8, 1.25)):
    """缝两边东西是接上的、只差明暗冷暖的，不重画：两边贴着缝各取一窄条，按行比颜色（中位数、竖着抹匀），
    两边各往中间值靠，离缝越远改得越少，reach 像素以外不动。原图头一回改以前留作 rNN_a0.png。"""
    np, Image = _np()
    pa, pb = (os.path.join(OUT, 'r%02d.png' % k) for k in (n, n + 1))
    A = np.asarray(Image.open(pa).convert('RGB'), np.float32)
    B = np.asarray(Image.open(pb).convert('RGB'), np.float32)
    H, W = A.shape[:2]
    ea, eb = np.median(A[:, -strip:], 1), np.median(B[:, :strip], 1)
    r = int(sig * 3)
    ker = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2)
    ker /= ker.sum()
    sm = lambda v: np.stack([np.convolve(np.pad(v[:, c], r, mode='edge'), ker, 'valid') for c in range(3)], 1)  # noqa: E731
    ea, eb = sm(ea), sm(eb)
    t = (ea + eb) / 2
    ga = np.clip((t + 4) / (ea + 4), *lim)
    gb = np.clip((t + 4) / (eb + 4), *lim)
    x = np.arange(reach, dtype=np.float32) / (reach - 1)
    ramp = x * x * (3 - 2 * x)                                   # 0 → 1，平滑
    A[:, W - reach:] *= 1 + (ga[:, None, :] - 1) * ramp[None, :, None]
    B[:, :reach] *= 1 + (gb[:, None, :] - 1) * ramp[::-1][None, :, None]
    for k, p, arr in ((n, pa, A), (n + 1, pb, B)):
        a0 = os.path.join(OUT, 'r%02d_a0.png' % k)
        if not os.path.exists(a0):
            Image.open(p).save(a0)
        Image.fromarray(np.clip(arr + 0.5, 0, 255).astype(np.uint8)).save(p)
    print('调好 j%02d 的明暗：左边那一段改了 %.2f..%.2f，右边那一段改了 %.2f..%.2f' % (n, ga.min(), ga.max(), gb.min(), gb.max()))


# ---------- 长卷的小改 ----------
# 一段里某一处画得跟碑对不上的，切一块 3:2 当底（放大到 1536×1024），叫 GPT 只改那一处，再缩回原大小、对齐校色，
# 只把 inner 那一框（往外羽化）贴回去。  python gpt_cg3.py --pcut p08 / p08 / --pmerge p08
PATCH_LEAD = ("Edit the attached picture. It is part of a long painted bird's-eye scroll in flat layered cut-paper shapes with a fine paper grain. "
              "Keep everything in the picture exactly as it is: the same composition, every object in the same place, the same light, colours, drawing manner and grain. Change only what is described here. ")
PATCHES = {
    # r08 鸢羽滩：碑上写的是河滩上一边一排插着的铳枪、一边一排渡口的短枪，模型把铳枪画成了四门带轮子的炮。
    'p08': dict(seg='r08', box=(840, 600, 1416, 984), inner=(846, 722, 1068, 880),
                text=("On the pale pebble beach, on the left, there are four wheeled cannons on carriages: remove them completely. In their place, plant one short straight row of seven long, slender handheld guns "
                      "stuck upright in the pebbles, butt down and muzzle up, each a long thin dark barrel on a narrow wooden stock, about as tall as the planted spears on the right, "
                      "the row facing the row of spears across the beach. The small standing figures, the row of spears, the pebbles and the river stay exactly as they are.")),
}


def patch_cut(key):
    _, Image = _np()
    pt = PATCHES[key]
    im = Image.open(os.path.join(OUT, pt['seg'] + '.png')).convert('RGB')
    im.crop(pt['box']).resize((1536, 1024), Image.LANCZOS).save(os.path.join(OUT, key + '_in.png'))
    print('切好', key)


def patch_merge(key, feather=14):
    np, Image = _np()
    pt = PATCHES[key]
    x0, y0, x1, y1 = pt['box']
    w, h = x1 - x0, y1 - y0
    p = os.path.join(OUT, pt['seg'] + '.png')
    seg = Image.open(p).convert('RGB')
    Wm = np.asarray(seg.crop(pt['box']), np.float32)
    G = np.asarray(Image.open(os.path.join(OUT, key + '.png')).convert('RGB').resize((w, h), Image.LANCZOS), np.float32).copy()
    ring = np.ones((h, w), bool)
    ix0, iy0, ix1, iy1 = (pt['inner'][0] - x0, pt['inner'][1] - y0, pt['inner'][2] - x0, pt['inner'][3] - y0)
    ring[max(iy0 - 24, 0):iy1 + 24, max(ix0 - 24, 0):ix1 + 24] = False
    g, wv = G.mean(2), Wm.mean(2)
    best = (1e18, 0, 0)
    for dy in range(-12, 13):
        for dx in range(-12, 13):
            d = np.abs(np.roll(np.roll(g, dy, 0), dx, 1)[ring] - wv[ring]).mean()
            if d < best[0]:
                best = (d, dx, dy)
    _, dx, dy = best
    G = np.roll(np.roll(G, dy, 0), dx, 1)
    for ch in range(3):
        k, c = np.polyfit(G[..., ch][ring][::5], Wm[..., ch][ring][::5], 1)
        G[..., ch] = G[..., ch] * k + c
    yy, xx = np.mgrid[0:h, 0:w]
    a = (np.clip((xx - ix0 + feather) / (2 * feather), 0, 1) * np.clip((ix1 + feather - xx) / (2 * feather), 0, 1) *
         np.clip((yy - iy0 + feather) / (2 * feather), 0, 1) * np.clip((iy1 + feather - yy) / (2 * feather), 0, 1))
    R = Wm * (1 - a[..., None]) + G * a[..., None]
    a0 = os.path.join(OUT, pt['seg'] + '_a0.png')
    if not os.path.exists(a0):
        seg.save(a0)
    seg.paste(Image.fromarray(np.clip(R + 0.5, 0, 255).astype(np.uint8)), (x0, y0))
    seg.save(p)
    print('贴好 %s：挪了 (%d, %d)，外圈差 %.1f' % (key, dx, dy, best[0]))


# ---------- 路的底纹和路边的景（11-14，用户看了手机上的路说“整体还是有些粗糙”）----------
# tex   四张能铺开的底纹（方的，四边接得上）：路面、墙面、草地、麦田。页面拿它们贴在路、墙、地上，颜色照各页那一套光去染（麦田那一张自己带颜色）。
# prop  路边的景，一样一张，透明底，照碑那一路的画法；页面照远近摆在路两边，走过去从身边过去。先出麦的年月那一套（pr6_ 打头）当样子。
TEX_LEAD = ("Draw one square 1:1 picture that is a seamless, tileable texture, meant to be repeated edge to edge, again and again, to cover a large surface in a painted picture-book game: ")
TEX_TAIL = (" The texture fills the whole square evenly, with no single focal point, no vignette, no frame, no border, no text, no objects, no people and no shadows of things outside it; "
            "the light is even, flat and soft, with no light direction. The left edge continues seamlessly into the right edge and the top edge into the bottom edge, "
            "so that copies laid side by side join without any visible seam. Drawing manner: the same hand as the attached plates of this series: flat stylized painted game art, "
            "large calm colour shapes, simple two-step shading, soft inner gradients, " + GRAIN + "; matte, no realistic photographic texture, no 3D render. "
            "Take only the drawing manner from the attached plates, never their compositions or anything drawn in them. Square picture, aspect ratio 1:1.")
TEXS = {
    'tx_road': ("an old road paved with large irregular flagstones, seen from directly above: rounded rectangular stones of different sizes laid in loose rows, "
                "thin darker joints between them with a few tiny tufts of grass and moss, some stones a little worn or chipped. Keep the colours neutral: pale grey stones and darker grey joints, "
                "almost no colour at all, because colour will be laid over it later."),
    'tx_wall': ("the face of a great wall built of pale limestone blocks, seen straight on: long rectangular blocks laid in level courses in a running bond, every course the same height, "
                "about eight courses from the top of the square to the bottom, with thin, slightly darker joints, faint vertical weathering streaks and a few small chips. "
                "Pale grey, almost no colour at all, because colour will be laid over it later."),
    'tx_grass': ("open grassland ground seen from directly above: soft clumps of short grass, small patches of bare earth, a few scattered small stones and tiny wild flowers, "
                 "in gentle uneven drifts. Muted, fairly neutral olive green and earth brown, because a colour will be laid over it later."),
    'tx_wheat': ("a field of ripe golden wheat seen from directly above: dense ears of wheat bending in soft swirling drifts, slightly darker gaps between the rows, "
                 "a few lighter strands catching the light; warm gold, honey and soft ochre, as in the light of a late golden evening."),
}
PROP_LEAD = ("Draw one picture on a fully transparent background: a single piece of scenery that stands in the open fields beside a picture-book road, ")
PROP_TAIL = (" It stands alone in the middle of the canvas on a tiny patch of its own ground, with clear empty transparent margin on every side, seen from the front at eye level and a little from above, "
             "as it would be seen from the road. Everything outside the thing and its tiny patch of ground is fully transparent, with a clean crisp edge: no other ground, no horizon, no sky, no frame. "
             "Drawing manner: flat stylized game illustration in the hand of the attached plates of this series: clean flat colour shapes with crisp edges, simple two-step shading, "
             "thin lighter echo lines along the edges, soft inner gradients only, " + GRAIN + ". Matte, no glare, no realistic rendering, no 3D render. "
             "It is lit evenly from the front with a slightly brighter left edge. The first attached picture is an approved piece of this same set: match its drawing manner, line, colours and finish exactly, "
             "but draw none of its things: no stele, no standing stone, no plinth, unless they are named here. The second attached picture is the approved main plate of this age: its colours. "
             "Take only the drawing manner and the colours from the attached plates, never their compositions, figures or symbols. Draw no wall behind it: no great wall, no castle or town wall, no battlements and no stone backdrop of any kind; only the thing itself on its little patch of ground, with open transparent space behind it. There are no people and no animals in this picture.")
PROP_SHAPE = {'w': ' Landscape picture, aspect ratio 3:2.', 't': ' Portrait picture, aspect ratio 2:3.', 's': ' Square picture, aspect ratio 1:1.'}
PROPS = {      # 键: (幅, 写的是什么)。麦的年月那一套：金黄的麦地，墙西一排界碑，墙东白石的农家，墙西黑石的农家，机兵化犁留下的老犁
    'pr6_stook': ('s', "a stook of harvested wheat in a reaped field: eight bundled sheaves of golden wheat stood upright and leaning together into a small tent shape, on a patch of short golden stubble, "
                       "in the warm colours of a golden evening."),
    'pr6_tuft': ('s', "a thick clump of tall ripe wheat growing wild at the edge of a field: a few dozen golden stalks with heavy ears bending in different directions, "
                      "two or three red field poppies among them, on a small patch of earth."),
    'pr6_sacks': ('s', "a small stack of five full grain sacks of pale undyed sackcloth tied at the neck, with a wooden hay rake leaning against them, on a patch of stubble."),
    'pr6_marker': ('t', "a small boundary marker: two short stone blocks set back to back, a pale white limestone block in front and, directly behind it, a slightly larger block of black volcanic glass "
                        "so that a thin black rim shows round the white one; the two are clamped together at their side edges by two short straps of dark bronze-gold metal with large round rivets. "
                        "It is short and squat, no taller than its own width and a half, plain, with no carving and no writing, standing on a little patch of grass."),
    'pr6_cart': ('w', "an old wooden two-wheeled farm cart standing in a reaped field, heaped with full grain sacks and a few golden wheat sheaves, its shafts resting on the ground; no animal."),
    'pr6_plow': ('w', "an old abandoned clockwork war machine of dark iron, about the size of a big man, which was turned into a plow a long time ago and then left in a wheat field: "
                      "its blocky armoured body, with a large winding key on its back, is slumped forward over a heavy iron plowshare that has taken the place of its arms, "
                      "its plates rusted orange-brown and overgrown with wheat stalks and small wild flowers, its feet half sunk into the earth. It is clearly very old, still and harmless; its face is a plain dark visor."),
    'pr6_house_e': ('w', "a small farmstead of the eastern land on the edge of a golden wheat field: a low house of whitewashed stone with a pale grey slate roof and one chimney, "
                         "beside it a small granary of white stone raised on short stone legs, a low wooden fence and two wheat stooks."),
    'pr6_house_w': ('w', "a small farmstead of the western land on the edge of a golden wheat field: a low house and a barn built of dark grey-black volcanic stone with dark slate roofs, "
                         "a stone chimney with a thin curl of smoke, a low dry-stone wall and two wheat stooks."),
    'pr6_tree': ('t', "a single broad old oak tree standing alone in a field, its full round crown of leaves just starting to turn golden at the edges, a thick gnarled trunk, a little shadow and stubble at its foot."),
    'pr6_brazier': ('t', "a road lamp at the edge of the fields: an iron fire basket on top of a tall plain iron post planted in the ground, a small steady flame burning in the basket, "
                         "a little patch of grass round the foot of the post."),
    # ---- 犁的年月（2 到 300 年）：灰雨刚停的阴天，路只有一条，在墙东边；仗刚打完，跪下的机兵、化了犁的机兵、帐子、烧焦的树、盐车、重盖的农家 ----
    'pr1_kneel': ('s', "a clockwork war machine of the old war that ran down and knelt where it stopped: a blocky automaton of dark grey iron about the size of a big man, a large winding key on its back, "
                       "kneeling on one knee in the mud with its head bowed and its plain dark visor facing the ground, its arms hanging loose, its plates dulled and spotted with the first rust, "
                       "a little grey ash still lying on its shoulders, a few new weeds at its knee. It is still and harmless."),
    'pr1_plowbot': ('w', "a clockwork war machine of dark grey iron, about the size of a big man, newly turned into a plow: its forearms have been taken off and a heavy iron plowshare is bolted in their place, "
                         "and it stands leaning forward at the end of a fresh dark furrow in muddy earth, a large winding key on its back, a few leather harness straps hanging from its shoulders, "
                         "its plain dark visor facing the furrow. It is still and harmless."),
    'pr1_tents': ('w', "a small camp of people who lost their homes in the war: two patched canvas tents of faded grey and brown, a little smouldering campfire ringed with stones "
                       "with a dented iron pot beside it, a bundle of blankets and a wooden crate."),
    'pr1_deadtree': ('t', "a tree killed by the fire of the war: a tall bare dead tree with charred black and ash-grey branches reaching out unevenly, its bark split, "
                          "a drift of grey ash and a few small new green shoots at its foot."),
    'pr1_debris': ('w', "leftovers of an old battle half sunk into a muddy field: a broken wooden cart wheel lying flat, two dented round shields, a snapped spear shaft lying on the ground "
                        "and a dented open helmet among weeds and grey ash; everything old, still and quiet, nothing standing upright."),
    'pr1_cairn': ('s', "a small memorial cairn by the roadside: a waist-high heap of rounded grey field stones, three white wax candles burning on the flat top stone with little drips of wax, "
                       "a faded strip of grey cloth tied round one stone, a few small wild flowers laid at its foot."),
    'pr1_saltcart': ('w', "a heavy two-wheeled wooden cart loaded with rough white blocks of salt tied down under ropes and a folded grey tarpaulin, its shafts resting on the ground, "
                          "a small wooden water barrel hanging at the back; no animal."),
    'pr1_hut': ('w', "a small farmhouse being rebuilt after the war: low walls of rough grey field stone, the roof half covered with fresh golden thatch and half still bare, "
                     "a ladder leaning against the wall, a stack of cut logs and a pile of new thatch bundles beside it."),
    'pr1_tuft': ('s', "a clump of dry winter grass and thistles at the edge of a muddy field: pale brown and grey-green stalks bending in different directions, two purple thistle heads, "
                      "on a small patch of dark earth."),
    # ---- 长夜的年月（301 到 579 年）：夜，墙上一线一线的灯；赶路的人、车队、亮着窗的农家、烧炭的窑、南边的沼 ----
    'pr2_campfire': ('s', "a travellers' campfire by the road at night: a ring of stones round a bright crackling fire, a small iron kettle hanging from a three-legged iron stand over it, "
                          "two rolled blankets and a pack lying beside it, warm orange light on the nearby ground."),
    'pr2_lantern': ('t', "a road lantern at night: a black iron lantern with four small glass panes and a little pointed iron cap, set on top of a plain straight wooden post planted in the ground; "
                         "a warm steady candle flame inside lights the glass, a soft round glow falls on the post and the grass at its foot."),
    'pr2_wagons': ('w', "a caravan resting for the night: two big covered wagons with arched pale canvas tops standing side by side, a small fire glowing between them, "
                        "barrels and sacks unloaded on the ground, a lantern hanging at the back of one wagon; no animals."),
    'pr2_house': ('w', "a small farmhouse of grey stone at night, its two small windows glowing warm yellow, smoke curling from the chimney, a low dry-stone wall and a woodpile, "
                       "a little warm light spilling on the ground at the door."),
    'pr2_kiln': ('w', "a charcoal burner's kiln at night: a low dome-shaped mound of earth and turf with thin smoke rising from small vents and a dull red glow showing at its base, "
                      "a heap of cut logs beside it with one long iron rake leaning against the heap."),
    'pr2_reeds': ('s', "a clump of tall marsh reeds and dark brown cattails growing from a small black pool of still water, a few reeds bent by the wind, faint starlight on the water."),
    'pr2_baretree': ('t', "a bare tree in the winter night: a slender tree with no leaves, its thin dark branches spreading up into a rounded crown, a little frost on the upper twigs, "
                          "a patch of frosted grass at its foot."),
    # ---- 白鸦的年月（580 到 660 年）：夜，天边泛红；白鸦那一团的旗、佣兵的营、坠下来的浮塔石块、废了的水闸、红水、赤盐 ----
    'pr3_crowbanner': ('t', "a tall plain wooden pole planted in the ground, with a long narrow pennant fixed along the top of the pole and streaming out sideways in the wind: "
                            "the cloth is dark charcoal grey with a ragged edge and carries one simple white bird with spread wings, a crow, sewn on in rough white cloth. "
                            "Nothing crosses the pole; the pole has no crossbar and no arms."),
    'pr3_camp': ('w', "a small mercenary camp at night: two tents of dark weathered canvas, a fire burning in a ring of stones, a few round shields leaning in a row against a fallen log, "
                      "one tall spear stuck upright in the ground beside a tent, saddlebags and a bedroll."),
    'pr3_towerrock': ('w', "fallen pieces of a great floating stone tower that crashed to the ground long ago: three huge carved blocks of pale stone, one broken in half, sunk at an angle into the earth, "
                           "their faces carved with long straight bands of old geometric pattern in which a few thin lines still glow a faint cold blue; grass and moss growing in the cracks."),
    'pr3_sluice': ('w', "an old abandoned sluice gate across a narrow dry ditch in the open field: two short square stone pillars standing on either side of the ditch, "
                        "a heavy wooden gate stuck half open between them, a small rusted iron winch on top, weeds growing in the dry ditch; no wall on either side of the pillars."),
    'pr3_redpool': ('w', "a small round pool of still water among dark reeds and stones, the water glowing deep red with the reflection of a far fire on the horizon, a few reed stalks standing in it."),
    'pr3_salt': ('w', "a salt workers' place at night: three cone-shaped heaps of coarse reddish salt, a long wooden salt rake leaning on one heap, two woven baskets, a little lantern on a crate."),
    'pr3_watch': ('t', "a squat round watchtower of rough grey stone, as tall as three men, with a crenellated top where an iron fire basket burns, a small arched wooden door at its foot and one narrow window."),
    # ---- 黎明的年月（661 到 741 年）：天快亮；灰雨以后路分开，墙西是落过灰的地（巴尔缇娜那一边），墙东是白杉、晨旗、军帐（索恩薇娅那一边） ----
    'pr4w_ashtree': ('t', "a dead tree in a land where grey ash fell like rain: a tall leafless tree whose bark and branches are coated pale ash-grey, ash heaped softly round its roots, "
                          "one single small green leaf on a low twig."),
    'pr4w_ruin': ('w', "the burnt ruin of a small stone house: two broken walls of blackened grey stone with an empty window, a fallen roof beam lying across the rubble, "
                       "everything powdered with pale grey ash, a few weeds already growing in the doorway."),
    'pr4w_pillar': ('t', "a broken pillar of black volcanic glass standing alone: a tall slab of glossy black stone, cracked and snapped off at the top, a faint dull red glow deep inside the cracks, "
                         "small black shards lying at its foot on grey ash."),
    'pr4w_camp': ('w', "a camp of the western clans at dawn: two round tents of dark brown hide, a small fire, one tall dark pole with a long narrow deep-red pennant along its top, "
                       "a pile of firewood and a black iron cauldron."),
    'pr4w_ash': ('w', "a few low drifts of pale grey ash in a dead field, with a half-buried cart wheel lying flat and a broken clay jar sticking out of them."),
    'pr4e_fir': ('t', "a slender young fir tree with silvery white bark and dark blue-green needles, straight and narrow, on a patch of grass with a few small spring flowers."),
    'pr4e_banner': ('t', "a tall plain wooden pole planted in the ground, with a long narrow pennant fixed along the top of the pole and lifting sideways in the wind: "
                         "deep blue cloth with its tail cut into two points, bearing one simple golden ring with a small golden dot in its middle. "
                         "No rays, no stripes. Nothing crosses the pole; the pole has no crossbar and no arms."),
    'pr4e_shrine': ('t', "a small wayside shrine: a square pillar of pale stone as tall as a man with a small pointed stone roof, a little arched niche near its top in which three white candles burn, "
                         "a few wild flowers and a folded white cloth laid at its foot."),
    'pr4e_tents': ('w', "a small army camp at dawn: three neat white canvas tents in a row with short blue pennants on top of their tent poles, a small fire, "
                        "a few round shields leaning against one tent."),
    'pr4e_farm': ('w', "a small farmstead of the eastern land at dawn: a low white house with a grey slate roof and a smoking chimney, a vegetable garden behind a low wooden fence, "
                       "a stone well with a little wooden roof."),
    # ---- 七城的年月（742 到 861 年）：大白天，青草；墙西是七城的地（黑曜石的方尖碑、血棘、铁匠铺、深红的旗、紫晶），墙东是果园、羊、农舍 ----
    'pr5w_obelisk': ('t', "a tall narrow four-sided obelisk of glossy black volcanic glass standing in green grass, its faces carved with long vertical bands of plain geometric pattern "
                          "that glow faintly red, a square black plinth at its foot."),
    'pr5w_thorn': ('s', "a big wild thorn bush with dark stems and long sharp thorns, covered in small deep crimson flowers and a few red berries, on a patch of green grass."),
    'pr5w_forge': ('w', "a small smithy of the western land: a low building of dark grey-black volcanic stone with a slate roof and a tall stone chimney with smoke, "
                        "its wide front open and a forge fire glowing orange inside, an anvil on a stump and a water barrel by the door."),
    'pr5w_pennant': ('t', "a tall dark iron pole planted in the ground, with a long narrow pennant fixed along the top of the pole and lifting sideways in the wind: "
                          "deep crimson cloth with its tail cut into two points, bearing one simple black flame with two short horns. "
                          "Nothing crosses the pole; the pole has no crossbar and no arms."),
    'pr5w_crystal': ('s', "a cluster of tall violet crystals growing out of a dark rock among green grass, faceted, glowing softly from inside."),
    'pr5w_rocks': ('w', "a group of jagged dark grey rocks with sharp edges standing out of green grass, patches of orange and pale green lichen on them, a few tufts of grass between them."),
    'pr5_tree': ('t', "a broad old oak tree in high summer standing alone in a meadow: a full round crown of fresh green leaves, a thick gnarled trunk, a little shadow and grass at its foot."),
    'pr5e_sheep': ('w', "three woolly white sheep on a patch of green grass: one with its head down grazing, one standing and looking to the side, one lying down; simple and gentle."),
    'pr5e_apple': ('t', "an apple tree in a summer orchard: a broad rounded crown of fresh green leaves dotted with small red apples, a short twisted trunk, a wooden ladder leaning against it, "
                        "two apples lying in the grass."),
    'pr5e_cottage': ('w', "a small cottage of the eastern land on a bright summer day: plain whitewashed stone walls, a steep roof of golden thatch, a small chimney, "
                          "a flowering garden in front with blue and pink flowers, a low woven wicker fence."),
    'pr5e_wall': ('w', "a short stretch of old low dry-stone wall in a meadow, mossy on top, with wild flowers growing along its foot: white daisies, red poppies and blue cornflowers."),
}
# 一纪一套光（第二张参考图换成路尽头那一纪的天，h1 到 h5；麦的年月照旧拿山铜纪主画）
PROP_SKY = {'pr1': 'h1', 'pr2': 'h2', 'pr3': 'h3', 'pr4': 'h4', 'pr5': 'h5'}
PROP_LIGHT = {
    'pr1': " Light and colour: a calm grey overcast day just after a long rain of ash, soft even light, muted grey, lavender and earth colours with only a faint warm tint.",
    'pr2': " Light and colour: a clear night under the stars with no moon at all: everything in cool dark blue and slate grey, softly lit by starlight; the only warm light is from its own fire, lamp or windows, if it has any.",
    'pr3': " Light and colour: a night under the stars with no moon at all, cool dark blue-grey, with a dim red glow from a distant fire on the horizon tinting its left edge; any fire or lamp of its own is warm.",
    'pr4': " Light and colour: early dawn before sunrise: cool lavender-blue shadows and a warm golden-pink light on its right side.",
    'pr5': " Light and colour: a bright clear summer day, fresh green grass, the light of a pale blue sky, soft shadows.",
}
PROP_ANIMALS = {'pr5e_sheep'}



# ---------- 碑形（11-14 墙东补叙与碑形）----------
# 用户 11-14：碑照事件做成剑冢、方尖碑、雕像、群像浮雕这些不同的样子，参照现实里知名的样子，不再一色墓碑。
# 四十三块一块一个键 m01..m43（次序照 11-14 以后的碑第一版），横竖照方向稿第四节那张表；碑牌留空，字是页面刻上去的。
# 画法照 11-14 的样图（门面_碑形_试_11-14），头一张参考是同材料认过的那一张样图，第二张是山铜纪主画。
MON_DIR = os.path.join(HERE, 'out', '门面_碑形_试_11-14')
MON_REF = {'bronze': ('m_yucheng.png', 'm_fenchao.png'), 'obsidian': ('m_cangyan.png', 'm_cangyan.png'),
           'white': ('m_changzhuo.png', 'm_changzhuo.png'), 'stone': ('m_changzhuo.png', 'm_changzhuo.png'),
           'border': ('m_changzhuo.png', 'm_changzhuo.png')}
MON_LEAD = {
    'tall': "Draw one tall 2:3 portrait picture on a fully transparent background, in the drawing manner of the first attached picture, which is an approved memorial of this series. ",
    'wide': "Draw one wide 3:2 landscape picture on a fully transparent background, in the drawing manner of the first attached picture, which is an approved memorial of this series. ",
}
MON_FRAME = ("Draw one memorial monument, alone in the middle of the canvas, seen from the front and a little from above, with clear empty transparent margin above and to both sides. "
             "It stands on its own small, low apron of flat paving stones, which is part of the monument; the bottom edge of the apron is about one tenth of the canvas above the bottom of the canvas. "
             "Outside the apron the background stays fully transparent: no ground beyond it, no sky, no landscape, no other buildings. ")
MON_PLAQUE = ("Where it is said below, there is one plain rectangular plaque, completely blank: no letters, runes, symbols or carving on it, evenly lit, "
              "because words will be engraved on it later; nothing stands in front of it. ")
MON_SCULPT = ("Every figure in it is sculpted and part of the monument, simplified forms in the monument's own material with smooth worn faces that show no individual features; "
              "there are no living people in this picture. ")
MON_STYLE = (" Drawing manner: flat stylized game illustration in the hand of the attached pictures: clean flat colour shapes with crisp edges, simple two-step shading, "
             "thin lighter echo lines along the edges, soft inner gradients only, " + GRAIN + ". Matte, no glare, no realistic rendering, no photographic texture, no 3D render. "
             "Lit evenly from the front with a slightly brighter left edge. "
             "Take only the drawing manner, the rendering of the material and the colours from the attached pictures, never their shapes, figures or what they show. "
             "No cross shape anywhere: no crosses, no cross-shaped hilts or posts standing against the sky.")
MON_MAT = dict(MATERIAL, stone="Material: weathered grey natural stone, rough where it is unworked and smooth where it was cut. ")
MONS = [
    # (键, 碑, 横竖, 材料, 样子)；样子里不写碑名
    ('m01', '雨城清查', 'wide', 'bronze', None),      # 样图 m_yucheng
    ('m02', '机兵化犁', 'tall', 'bronze',
     "A statue. On a low square plinth kneels a cast bronze-gold statue of a clockwork soldier, a tall humanoid automaton: a smooth metal face plate with two round glass eyes, "
     "a plain blank iron plate on its chest, a small bell under its chin, a winding key on its back. It kneels on one knee with its head bowed; its right arm from the elbow down "
     "has been hammered into a broad plough blade whose point is driven into the earth. Around the plinth a ring of new iron ploughshares is planted point-down, and behind it, low, "
     "an iron rail strung with a row of small bronze bells. The blank plaque is set into the front of the plinth, below the kneeling knee."),
    ('m03', '盐路赎身', 'wide', 'bronze',
     "A well. The low round rim of an old salt well, waist-high, clad all round in plates of cast bronze-gold metal; hung around the rim, chained one to another, "
     "a ring of opened iron shackles with their cuffs hanging open. White salt crust lies on the paving around it. The blank plaque is a flat panel on the front of the well rim, facing us."),
    ('m04', '归林', 'tall', 'bronze',
     "A watch-tower. A square watch-tower of pale grey stone, three storeys tall, with narrow arrow slits; its door stands open, and through the door and out of the arrow slits "
     "show the tips of many stag antlers stacked on wooden racks from the floor to the top; beside the door hangs one empty bow rack. The blank plaque is a bronze plate set into the wall beside the door."),
    ('m05', '九年之路', 'wide', 'bronze',
     "A group of walking figures. On a long low stone base, a line of about ten cast bronze-gold figures of northern travellers walks from right to left, wrapped in fur cloaks and hoods: "
     "grown people carrying small children on their backs, an old man leaning on a long bow as a staff, a woman with a bundle; the one at the front turns to look back at those behind. "
     "Each figure stands or walks plainly with natural proportions. Around the base stand plain pale wooden longbows planted upright, unstrung. The blank plaque runs along the front of the stone base."),
    ('m06', '扶剑礼', 'tall', 'bronze',
     "A sculpture of hands. On a square plinth stands a great cast bronze-gold sculpture, taller than a man: one hand grips the plain grip of a sword hilt that has a round disc guard "
     "and ends just below the guard, with no blade at all; on the back of that hand fourteen other hands are laid one upon another, a tall stack of hands pressing down, "
     "each hand a little different, some with rings, some gloved. Only the hilt and the hands: no blade, no bodies, no arms beyond the wrists. The blank plaque is set into the front of the plinth."),
    ('m07', '炭巷', 'tall', 'bronze',
     "An arch. At the mouth of a narrow soot-dark lane, a free-standing arch of cast bronze-gold metal, just taller than a man, plain and heavy, cast from the skeleton of an old machine: "
     "riveted ribs and a few old gear teeth show in its surface. In the middle of the top of the arch is set the blank plaque. Under the arch, planted across the lane mouth, "
     "stands one row of iron shovels with their handles snapped off."),
    ('m08', '灰旗', 'tall', 'stone',
     "A gate-stone. An old weathered grey gate-stone, a rough upright slab, set against the inner side of a stone gateway whose lower part shows behind it; its front face is flat and "
     "blank, and that face is the blank plaque. Above it a small piece of plain grey cloth is nailed fast to the stone of the gateway."),
    ('m09', '河心三日', 'wide', 'stone',
     "A river stone. A single great rounded grey river boulder rising out of shallow water at a ford, with one roughly flat face toward us that stays blank, and that face is the blank plaque; "
     "a few reeds and pebbles around it and small ripples round its foot. Instead of a paved apron there is only a small patch of shallow water at its foot; everything else is transparent."),
    ('m10', '南沼停火', 'wide', 'bronze',
     "A salt spring. A small round salt spring with a waist-high railing of cast bronze-gold metal all round it; the blank plaque is on the railing's front side. Outside the railing "
     "stand two rings of old weapons planted upright, an inner ring of short spears and an outer ring of curved swords. White salt crust lies on the stones."),
    ('m11', '换俘碑', 'wide', 'bronze',
     "A gateway. The inner end of a stone city gateway, a deep arched passage through a thick wall of pale stone, seen from inside the town; at each end of the passage stands "
     "a tall plain wooden flagpole with a plain cloth banner hanging slack, one pale and one dark, with no emblems. Set into the wall of the passage beside the arch is the blank plaque, a bronze plate. "
     "Only this short piece of the gateway, cut off cleanly at its edges, stands on the apron."),
    ('m12', '废弃水闸', 'wide', 'bronze',
     "A split war horn. On an old square stone platform beside a disused wooden sluice gate, a great straight war horn of cast bronze-gold metal, longer than a man and wide at the mouth, "
     "has been cast split lengthwise into two halves; the two halves stand apart at the two ends of the platform, both mouthpieces pointing toward the sluice gate. "
     "Between them, on a low post, stands the blank plaque."),
    ('m13', '红水', 'wide', 'bronze',
     "A ring of weapons in a dock. At the mouth of an old stone dock, with dark red water lying in it, a ring of weapons is planted in the mud: swords, axes, spears and hooks "
     "of several mercenary companies; about half the places in the ring hold instead a plain bronze-gold rod without a blade. In the middle of the ring a squat stone block carries the blank plaque."),
    ('m14', '喂山', 'wide', 'stone',
     "A carved cliff. A cliff face of grey mountain rock with an old temple door cut into it; stone carvers have carved the rock on both sides of the doorway into two great sealing stones "
     "swung outward, as if someone pushed the door open from inside. Above the doorway the blank plaque, a bronze plate, is set into the rock. Before the door, rough broken sealing stones "
     "are stacked in a neat low pile. Only this piece of cliff, cut off cleanly at its edges, stands on the apron."),
    ('m15', '白母', 'wide', 'bronze',
     "A great skull on a cairn. In a snowy mountain pass, a heap of old wooden wagon shafts dug out of the snow, planted upright and leaning together like a cairn, some still tied "
     "with half a harness rope; laid on top of the heap, the huge white skull of a stag-like beast whose antlers, wider than a wagon, branch many times. At the foot of the heap "
     "stands the blank plaque, a bronze plate on a low stone. Patches of snow lie on the apron."),
    ('m16', '赤盐边镇', 'wide', 'bronze',
     "A row of broken salt rakes. On a long low bed of red salt edged with pale stone, one long row of about forty broken wooden salt rakes is planted: each rake is pushed head-down "
     "into the salt with its toothed head buried, so that only its snapped wooden handle sticks up, the handles at uneven heights and leaning a little this way and that, like a ragged fence "
     "of broken poles; a few broken-off rake heads with their long wooden teeth lie on the salt among them. At the head of the row, on a small square stone block, stands one long salt rake "
     "cast in bronze-gold metal, its handle planted in the block and leaning forward toward the left, its broad toothed head at the top seen from the side with its teeth pointing to the left; "
     "the blank plaque is fixed on its handle at eye height. No crosses and no T-shapes anywhere."),
    ('m17', '灰雨之夜', 'wide', 'bronze',
     "A stele and five figures. On a grassy slope stands a cast bronze-gold stele with a round-arched top whose face is the blank plaque; behind it and to its right, five cast "
     "bronze-gold figures of mercenaries walk side by side, shoulder to shoulder, toward the right, cloaks blowing, their faces cast vague and smooth with no features. "
     "Across the foot of the stele, pressed into the grass, lies one long cavalry lance with its point broken off."),
    ('m18', '黎明篡位', 'wide', 'bronze',
     "A relief wall. A long low wall of cast bronze-gold metal, about three fifths of the canvas wide, stands on a plinth of pale palace stone. On its face, in high relief bursting out "
     "of the wall: a crowd of common people from a riverbank slum, dockhands, washerwomen, old soldiers with patched coats, a boy, a grey-haired woman, carrying burning torches whose flames "
     "are cast in the same metal, surging from the lower left up a wide flight of steps toward the upper right. On the top step at the right end lies ONE single royal crown that has been "
     "cut clean through into two halves; the two halves lie a hand's breadth apart, each plainly half of the same ring, so that anyone sees one crown cut in two, never two crowns. "
     "An old plain sword with a rope-wrapped grip leans against that step beside it. No ruler, no queen and no leading figure is shown; the crowd itself is the subject. "
     "Along the front of the stone plinth, under the relief, runs the long blank plaque."),
    ('m19', '十四家之乱', 'wide', 'bronze',
     "A broken flagpole between two rows of weapons. On a river beach of pale pebbles stands a tall flagpole cast in bronze-gold metal, three times the height of a man, snapped off "
     "near its top, the broken end jagged, a torn bronze banner hanging from it. To its left one row of long-barrelled guns is planted muzzle-down, rusted all one colour; to its right "
     "one row of short spears is planted upright; the two rows face each other across the pole. At the foot of the pole stands the blank plaque on a low block."),
    ('m20', '白杉堡', 'tall', 'bronze', None),        # 样图 m_baishan
    ('m21', '碎碑矿坑', 'wide', 'bronze',
     "A cairn of broken rings. At the mouth of a mine pit framed with old timber beams, a cairn heaped from hundreds of broken bronze-gold rings and shackle loops, a small hill "
     "taller than a man; set into the side of the cairn facing us is the blank plaque."),
    ('m22', '苍焰角城', 'tall', 'obsidian', None),    # 样图 m_cangyan
    ('m23', '血棘红园', 'wide', 'obsidian',
     "A row of inverted banners. One row of twelve family banners planted upside down: the poles are polished black volcanic glass, the banners are cast in dark bronze-gold metal "
     "and hang toward the ground, each a different plain shape with no emblem. At the head of the row stands a squat post of black glass whose face is the blank plaque."),
    ('m24', '旁听', 'tall', 'bronze',
     "A column. A tall round column of cast bronze-gold metal on a square stone base, about four fifths of the canvas tall; a relief band winds round the column in a spiral from "
     "the base to the top, showing a long queue of small simplified common people walking one after another up the spiral, dockhands, old soldiers, women carrying children. "
     "On top of the column, instead of any statue, stands a sheaf of bronze reeds bound with a cord. The blank plaque is set into the front of the square base."),
    ('m25', '三条长凳', 'wide', 'bronze',
     "Three benches. On a riverbank paved with stones, three long benches cast in dark bronze-gold metal stand facing each other in a U shape, the middle one with a backrest and "
     "room for three; they look like plain wooden kitchen benches turned to metal, their edges worn smooth. The blank plaque is set into the backrest of the middle bench. "
     "A low stone river wall runs behind them."),
    ('m26', '门楣', 'tall', 'white',
     "A doorway and a small figure. A free-standing doorframe of white stone, the size of a large door, with no wall around it: two posts and a lintel, the lintel plain and blank. "
     "Beneath the doorframe stands a small cast bronze-gold statue of a young girl in a plain long dress and an apron, her head tilted back, looking up at the lintel, one hand raised "
     "pointing at it, her mouth open as if reading aloud. A row of small pebbles lies along the threshold. The blank plaque is a bronze plate set into the foot of the left post."),
    ('m27', '骸钟墓城', 'tall', 'obsidian',
     "A small bell tower. A slender square bell tower of black volcanic glass with a pointed roof, about four fifths of the canvas tall; in its open belfry hangs one bronze-gold bell "
     "whose clapper is chained fast. Around its foot burns a ring of small grey stone lamps, each with a small steady flame. Beside its door is the blank plaque."),
    ('m28', '无名碑林', 'wide', 'bronze',
     "A field of standing stones. At the edge of a marsh, many small plain standing stones without any marks, set close together like a crowd, and at the front among them one taller "
     "slab of bronze-gold metal with a round-arched top whose face is the blank plaque; reeds and patches of shallow water at their feet."),
    ('m29', '魇镜幻都', 'tall', 'obsidian',
     "A standing mirror. A tall upright mirror of polished black volcanic glass, twice the height of a man, in a simple heavy frame of the same black stone, standing at the edge "
     "of dark still water; the mirror surface shows only a soft dark sheen, with no reflection of any figure. Set into the foot of the frame below the mirror is the blank plaque."),
    ('m30', '分潮', 'tall', 'bronze', None),          # 样图 m_fenchao
    ('m31', '黑翼天塔', 'wide', 'obsidian',
     "A carved cliff with wings. A cliff face of dark rock above the sea; carved into it in high relief, six great feathered wings spread out, three on each side, each longer than "
     "a tower; between the wings a slab of black glass is set into the rock, and its face is the blank plaque; on top of the cliff stands a slender spire. Only this piece of cliff, "
     "cut off cleanly at its edges, stands on the apron."),
    ('m32', '开岭', 'tall', 'stone',
     "A cleft cliff. A cliff of grey rock in a snowy mountain pass, split from top to bottom by one straight narrow cleft wide enough for a wagon, the two walls of the cleft smooth "
     "as if cut with a blade; a row of iron rings is fixed along both walls inside the cleft. At the mouth of the cleft stands one block of stone split off from the cliff, its cut face "
     "toward us, flat and smooth as if polished: that face is the blank plaque. Snow lies on the ledges."),
    ('m33', '雷暴荒地', 'tall', 'obsidian',
     "A chained column. A tall column of black volcanic glass on a stepped base; one great heavy chain of bronze-gold metal, thick as an arm, is wound round and round the column "
     "from its top to its foot, and the spare length lies coiled at the foot. The blank plaque is set into the base."),
    ('m34', '最后一尊', 'wide', 'bronze',
     "A line of bowls leading to a great bowl. Its apron is bare grey ground of packed earth with a few pebbles instead of paving. On it a long line of about fifteen plain grey stone bowls, "
     "each as big as two cupped hands, set on the ground one after another, leads from the left toward the right; at the right end the line ends at one great plain bowl cast in bronze-gold metal, "
     "as wide as a cartwheel, resting on a low round drum of grey stone, and the front of that stone drum is the blank plaque. Nothing else stands there: no wall, no arch, no ruins, no pillar, "
     "no slab, no stele, no weapons, no cloth, only the bowls, the bare ground and the great bowl on its drum."),
    ('m35', '深潮蓝堡', 'tall', 'obsidian',
     "A lighthouse. A lighthouse tower of black volcanic glass standing on a rocky shore, its foot in shallow water with small waves breaking round it; at its top a lantern room "
     "with seven small lamps in a ring, glowing softly. Beside its door is the blank plaque."),
    ('m36', '第一条', 'tall', 'bronze',
     "A law stele. A broad, heavy stele of cast bronze-gold metal, broader and taller than a common stele, with a round-arched top; across its top a relief panel shows the black "
     "towers of a city standing in a row; the large face below the relief is the blank plaque. It stands on plain dark paving."),
    ('m37', '界碑', 'tall', 'border',
     "A boundary stone on open ground. Its front slab is pale white limestone and its face is the blank plaque."),
    ('m38', '曜石', 'wide', 'obsidian',
     "A black mirror in the ground, seen a little more from above. On a platform of dark stone paving, a large round disc of polished black volcanic glass is set flush into the ground, "
     "shining like a dark mirror; at its edge stands a tall plain candlestand of bronze-gold metal holding one unlit white candle. The blank plaque is set into the foot of the candlestand."),
    ('m39', '烧麦', 'tall', 'white',
     "A white stone in a burnt field. One single rough block of pale white limestone, as tall as a man and a little wider at its foot, roughly squared, its top uneven and broken off, "
     "not arched and not carved into any shape; its front face is cut flat and smooth, and that face is the blank plaque. Instead of a paved apron, its foot stands in a small patch of wheat field "
     "burnt black, charred stubble and grey ash; everything else is transparent. Around its foot about a dozen blackened sickles are thrust blade-first deep into the ash, so that only their short "
     "wooden handles stick up; a few unburnt stalks of golden wheat stand beyond them."),
    ('m40', '献祭台', 'tall', 'bronze',
     "A fist. On the square bare stone base of a demolished platform stands a great fist cast in bronze-gold metal, taller than a man, rising from the stone at the wrist, gripping "
     "the heavy head of an executioner's hammer whose broken haft juts out. The blank plaque is set into the stone base below the fist."),
    ('m41', '门与粮', 'wide', 'white', None),         # 样图 m_changzhuo
    ('m42', '不灭王炉', 'tall', 'bronze',
     "A furnace. A monument shaped like a dwarven forge furnace, cast in bronze-gold metal, squat and heavy, its round mouth open and filled with a steady white flame; before the mouth "
     "stand a heavy anvil with a hammer resting on it. The blank plaque is set into the side of the anvil's block. Behind it, low, show the bottom steps of a deep stone stair."),
    ('m43', '无字碑', 'tall', 'white',
     "A wordless white monolith. One tall plain monolith of pale white limestone, the same stone as a great white wall, about twice the height of a man, a tall rectangle with a flat top "
     "and slightly worn edges; no carving, no relief, no figures and no statues on it or around it. It stands in the rubble of a collapsed stone gateway: beside it one broken door jamb "
     "of the same white stone, half fallen, and a few fallen white blocks lying around its foot. Its front face is completely blank, and that face is the blank plaque."),
]
MON_SAMPLE = {'m01': 'm_yucheng', 'm20': 'm_baishan', 'm22': 'm_cangyan', 'm30': 'm_fenchao', 'm41': 'm_changzhuo'}
# 11-14 查图：雨城清查那张样图（横的山铜）左头方柱、当中长台、右头断墙拱门，九年之路、最后一尊照抄了它。返工的几块头一张参考换成已经出好、没有墙的同材料那一张
MON_REF_KEY = {'m34': os.path.join(OUT, 'm03.png'), 'm16': os.path.join(OUT, 'm13.png')}
# 九年之路拿原图当底只拿掉照抄的断墙拱门和方柱（原图留作 m05_a0.png）
FIX['m05'] = ('m05_a0.png',
              "Redraw the FIRST attached picture and keep everything about it exactly the same: the same line of walking cast bronze-gold figures in the same places and poses, "
              "the long low stone base under them with the long blank bronze plaque along its front, the paving apron, the pale wooden longbows planted upright beside the base, "
              "the drawing manner, the colours, the light and the size. Change one thing only: remove the ruined brick wall with its round archway that rises behind the figures, "
              "and remove the square stone pillar with its small plaque at the left end of the base; nothing stands behind or beside the figures any more. Where the wall and the pillar were, "
              "the background is fully transparent, like everywhere else outside the monument. Add nothing new. Fully transparent background. Landscape picture, aspect ratio 3:2.")

# ---------- 键 ----------
S = {}
for k, m in TPL.items():
    S[k] = dict(kind='tpl', mat=m)
for k, t in TEXS.items():
    S[k] = dict(kind='tex', text=t)
for k, (shape, t) in PROPS.items():
    S[k] = dict(kind='prop', text=t, shape=shape)
for k, name, m, around in STELES:
    S[k] = dict(kind='stele', name=name, mat=m, around=around)
for i, t in ROADS.items():
    S['r%02d' % i] = dict(kind='road', text=t, n=i)
for k, v in ERAS.items():
    S[k] = dict(kind='era', text=v['text'], heads=v['refs'])
for _n in range(1, 12):
    S['j%02d' % _n] = dict(kind='join', n=_n)
for _k in PATCHES:
    S[_k] = dict(kind='patch')
for _k, _v in HORS.items():
    S[_k] = dict(kind='hor', text=_v['text'], look=_v['look'])
for _k in WALKS:
    S[_k] = dict(kind='walk')
for _k, _n, _o, _m, _t in MONS:
    S[_k] = dict(kind='mon', name=_n, orient=_o, mat=_m, text=_t)


def tpl_path(mat):
    return os.path.join(OUT, {'bronze': 't_bronze', 'white': 't_white', 'obsidian': 't_obsidian', 'border': 't_border'}[mat] + '.png')


# ---------- 节点原画和旅伴死的那一刻（11-14）----------
# 场面写在 小样_山铜纪书/scenes/pN.json（nodes 一幕一幅，deaths 死的那一刻），画法照 gpt_cg.py 那一套（崩铁光锥，人体护栏 BODY、POSE 在 G.job 里）。
# 立绘标了 minor、teen、child 的，或者那一页里不满十八的，照未成年那一条画（不画伤）；场面稿写了 minor 的连 raw 也不算数。
#   python gpt_cg3.py scenes          出全部（出过的跳过）
#   python gpt_cg3.py p4              出第四页那几幅
#   python gpt_cg3.py --left scenes   还缺哪几幅
G.POR_ALL += ['立绘_山铜纪', '立绘_前传']
G.OUT = OUT                       # 对照条（_ident）也放在山铜纪这一边
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BOOK = os.path.join(ROOT, '底稿', '门面', '小样_山铜纪书')
SCENES = os.path.join(BOOK, 'scenes')


def beast_path(name):
    if name.startswith('god_'):
        return os.path.join(HERE, 'out', '神明显像', name + '.png')
    return os.path.join(HERE, 'out', '史诗战', name.rsplit('_', 2)[0], name + '.png')


def load_scenes():
    import glob
    dp = os.path.join(BOOK, 'data', 'bronze.json')
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
    for p in sorted(glob.glob(os.path.join(SCENES, 'p?.json'))):
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
            # 山铜纪的立绘好些是往后几页的样子（凝名以后的断角、紫纹，出坑以后的外套），一律照场面写的画，只留脸、颜色和身架
            e['differs'] = True
            S[s['key']] = e


load_scenes()


# 11-23 原画核对（底稿/立绘/原画核对_11-23/山铜纪书.md）：11-22 长相重画以后原画没跟上。根子之一是 _ident/ 里的对照条是 11-14 留下的，
# ident() 见文件在就不重拼，立绘换了它照旧给旧脸；这一回重画前把画里各人的对照条删了重拼。
# 下面五幅人只差颜色、别处 11-14 已经 FIX 对过，拿旧图（挪进 备选/角前_1123/）当底只改那一处；别的几幅整幅重画（p3_h1 p4_b1 p4_b3 p4_d_boru p5_b4 p5_j1 p6_j2 p6_j3）。
BK1123 = os.path.join(OUT, '备选', '角前_1123')
_NUR = ("The barefoot fire-horn girl is drawn with brown hair, pale skin and horns that are too long. Change only her, taking her look from the SECOND attached picture: "
        "glossy blue-black hair, clearly not brown or red, tied back loosely with a red cord; skin of the warm brick-red-brown fire-horn hue, not pale; "
        "a pair of tiny new horns only a finger long, pale in colour, much smaller than now. She stays a thin ten-year-old child in the same place, the same pose and the same old brown coat. ")
_VAL = ("The tall horned man's skin is drawn as ordinary warm brown; make his skin a deep ash grey like volcanic ash, as in the THIRD attached picture, and keep his face, his red eyes, his horns, his clothes and his pose exactly as they are. ")
FIX.update({
    'p5_a2': ((os.path.join(BK1123, 'p5_a2.png'), G.ident('s5b_nur_child', 'casual'), G.ident('s5a_valdrak', 'private')), _KEEP + _NUR + _VAL + _TAIL),
    'p5_a4': ((os.path.join(BK1123, 'p5_a4.png'), G.ident('s5b_nur_child', 'formal'), G.ident('s5a_valdrak', 'formal')), _KEEP + _NUR + _VAL +
              "There are no flowers, blossoms or petals anywhere." + _TAIL),
    'p5_d_hakan': ((os.path.join(BK1123, 'p5_d_hakan.png'), G.ident('s5b_hakan', 'battle')), _KEEP +
                   "The rowing four-armed man is drawn with long wild white hair and the worn face of an old man. Change only his head, taking it from the SECOND attached picture: "
                   "sea-blue hair tied back in a short tail, a few wet locks whipped loose by the wind, the face of a man who looks about thirty-five, faded grey-green scales on his cheeks and neck, "
                   "yellow eyes with narrow vertical slit pupils like a snake's, his mouth shut and set. Keep his four arms, his hands on the four oars, his body, his clothes, the boat, the sea and the reefs exactly as they are." + _TAIL),
    'p1_nd2': ((os.path.join(BK1123, 'p1_nd2.png'), G.ident('s1n_mabel', 'casual')), _KEEP +
               "The healer in the navy cap climbing the ladder is drawn with golden-blonde hair. Change only the colour of her hair to light flaxen brown, a soft light brown like the woman in the SECOND attached picture, "
               "with the thin braid at each temple and the same length and waves; the orange firelight may warm its edges, but the hair itself is light brown, not gold and not blonde. Her face, cap, clothes, box and pose stay as they are." + _TAIL),
    'p1_nd3': ((os.path.join(BK1123, 'p1_nd3.png'), G.ident('s1n_mabel', 'casual')), _KEEP +
               "The healer sitting on the left is drawn with long ginger-orange hair. Change only the colour of her hair to light flaxen brown, a soft light brown like the woman in the SECOND attached picture, "
               "with the thin braids at the temples, the same length and the same waves; not orange, not red, not blonde. Her burnt cap, her face, clothes, bell and pose stay as they are." + _TAIL),
})
# 头一回出来以后查图：p1_nd3 头发改成了蜂蜜金，再从原图改一回、说得更重；p4_d_boru 整幅重画出来博鲁只剩一只角、尖也没缺，拿重画那一稿（_n1）补角；
# p6_j2 整幅重画出来默娜成了跟多尔特一样的红发，拿 _n1 只改她的头发。
FIX.update({
    'p1_nd3': ((os.path.join(BK1123, 'p1_nd3.png'), G.ident('s1n_mabel', 'casual')), _KEEP +
               "The healer sitting on the left is drawn with long ginger-orange hair. Change only the colour of her hair to a warm medium light brown, the colour of hazelnut shells, "
               "exactly the hair colour of the woman in the SECOND attached picture: clearly brown, darker than blonde, never golden, never orange, never red. "
               "Keep the thin braids at the temples, the same length and the same waves. Her burnt cap, her face, clothes, bell and pose stay as they are." + _TAIL),
    'p4_d_boru': ((os.path.join(BK1123, 'p4_d_boru_n1.png'), G.ident('s4b_boru', 'casual')), _KEEP +
                  "The huge bull-horned smith on the left has only one horn, growing from the back of his head. He has two thick bull horns like the man in the SECOND attached picture, "
                  "one growing from each side of his head above the temples and jutting out sideways before curving forward: the near horn, on his left side toward us, has its tip chipped off short and blunt, "
                  "and the far horn shows beyond his head against the dark. His face, his copper-brown hair, his body, the chain, the grey prisoner and everything else stay as they are." + _TAIL),
    'p6_j2': ((os.path.join(BK1123, 'p6_j2_n1.png'), os.path.join(BK1123, 'p6_j2.png')), _KEEP +
              "The young woman in the long grey wool dress sitting at the table in the middle, her hands flat on the table, is drawn with red hair, so that she looks like the red-haired apprentice sitting on the floor behind her. "
              "Change only her hair: soft light brown hair, plain and not red, mostly hidden under her plain grey kerchief, as on the woman at the table in the SECOND attached picture. "
              "Her face, her dress, her hands, and every other person stay exactly as they are; the apprentice on the floor keeps her apricot-red hair." + _TAIL),
})


def job(key):
    s = S[key]
    if s['kind'] == 'tpl':
        p = TPL_LEAD + STELE_SHAPE + MATERIAL[s['mat']] + STELE_STYLE + F.WEST_PLAIN + F.CLEAN
        return p, [K3B, BB2]
    if s['kind'] == 'stele':
        p = (STELE_LEAD + MATERIAL[s['mat']] + 'Around it: ' + s['around'] + STELE_KEEP + STELE_STYLE + ' There are no people in this picture.' +
             F.WEST_PLAIN + NO_MOON + F.CLEAN)
        return p, [tpl_path(s['mat']), K3B]
    if s['kind'] == 'road':
        n = s['n']
        if n == 1:
            return ROAD_LEAD + s['text'] + ROAD_STYLE + ROAD_REF0 + PEOPLE + F.WEST_PLAIN + NO_MOON + NO_ARC + F.CLEAN, [R04, K3B]
        r01, left = os.path.join(OUT, 'r01.png'), os.path.join(OUT, 'r%02d.png' % (n - 1))
        p = ROAD_LEAD + s['text'] + ROAD_STYLE + road_ref(n) + PEOPLE + F.WEST_PLAIN + NO_MOON + NO_ARC + F.CLEAN
        return p, ([left, K3B] if n == 2 else [left, r01, K3B])
    if s['kind'] == 'era':
        heads = [F.cast_head(h) for h in s['heads']]
        p = G.PV_LEAD + s['text'] + ERA_STYLE + G.PV_ROOM + PEOPLE + F.WEST_PLAIN + NO_MOON + NO_ARC + F.CLEAN
        if heads:
            p += (' The last attached picture shows only the face, hair and eyes of the woman with dark copper-brown hair: take her hair colour, hair style and eye colour from it and nothing else; '
                  'she stays tiny and is seen from behind, so her face is not shown.')
        return p, [K3B] + [os.path.join(PVD, n) for n in ERA_LOOK] + heads
    if s['kind'] == 'mon':
        ref = MON_REF_KEY.get(key) or os.path.join(MON_DIR, MON_REF[s['mat']][0 if s['orient'] == 'wide' else 1])
        p = (MON_LEAD[s['orient']] + MON_FRAME + s['text'] + ' ' + MON_MAT[s['mat']] + MON_PLAQUE + MON_SCULPT + MON_STYLE +
             F.WEST_PLAIN + NO_MOON + NO_ARC + F.CLEAN)
        return p, [ref, K3B]
    if s['kind'] == 'tex':
        look = os.path.join(OUT, 'h6.png' if key == 'tx_wheat' else 'h5.png')
        return TEX_LEAD + s['text'] + TEX_TAIL + F.CLEAN, [K3B, look]
    if s['kind'] == 'prop':
        era = key[:3]
        tail = PROP_TAIL
        if key in PROP_ANIMALS:
            tail = tail.replace(' There are no people and no animals in this picture.', ' There are no people in this picture; the animals named here are the only living things.')
        if era in PROP_SKY:
            tail = tail.replace('The second attached picture is the approved main plate of this age: its colours.', 'The second attached picture is the sky of this stretch of the road: take its colours and its light.')
            return (PROP_LEAD + s['text'] + tail + PROP_LIGHT[era] + F.WEST_PLAIN + NO_MOON + F.CLEAN + PROP_SHAPE[s['shape']]), [os.path.join(OUT, 'b33.png'), os.path.join(OUT, PROP_SKY[era] + '.png')]
        return (PROP_LEAD + s['text'] + tail + F.WEST_PLAIN + NO_MOON + F.CLEAN + PROP_SHAPE[s['shape']]), [os.path.join(OUT, 'b33.png'), K3B]
    if s['kind'] == 'join':
        return join_prompt(s['n']), [os.path.join(OUT, 'j%02d_in.png' % s['n'])]
    if s['kind'] == 'patch':
        return (PATCH_LEAD + PATCHES[key]['text'] + ' ' + PEOPLE + NO_MOON + F.CLEAN + ' Landscape picture, aspect ratio 3:2.'), [os.path.join(OUT, key + '_in.png')]
    if s['kind'] == 'walk':
        w = WALKS[key]
        look = os.path.join(OUT, w['look'])
        if w['look'].startswith('w_'):     # 拿同一个人成年那一张（缩之前的原图）对齐机位、比例和画法
            raw = os.path.join(OUT, w['look'][:-4] + '_raw.png')
            look = raw if os.path.exists(raw) else look
            lead = (" The FIRST attached picture is the approved figure of this same person as she will look later, from this very set: match its camera, its walking pose, its line, "
                    "its colours and its finish exactly, and change only her age, her size and her clothes as described. ")
            refs = [look, K3B, F.cast_head(w['head'])]
            note = (" The SECOND attached picture is the approved main plate of this age: its colours. The THIRD attached picture shows only her face and hair: take her hair colour and hair style from it and nothing else.")
        else:
            lead = ""
            refs = [K3B, look, F.cast_head(w['head'])]
            note = (" The FIRST attached picture is the approved main plate of this age: its colours and its hand. The SECOND attached picture is an approved plate of this series in which she appears small, "
                    "seen from behind: take her look from it, never its composition. The THIRD attached picture shows only her face and hair: take her hair colour and hair style from it and nothing else.")
        return WALK_LEAD + lead + w['text'] + WALK_TAIL + note + F.WEST_PLAIN + F.CLEAN, refs
    if s['kind'] == 'hor':
        # 颜色照山铜纪主画，手法照片头月银纪那两幅，光照这一页的时代原画（只取光和颜色）
        p = HOR_LEAD + s['text'] + HOR_STYLE + F.WEST_PLAIN + NO_MOON + NO_ARC + F.CLEAN + ' Landscape picture, aspect ratio 3:2.'
        return p, [K3B] + [os.path.join(PVD, n) for n in ERA_LOOK] + [os.path.join(OUT, s['look'])]
    if s['kind'] == 'cut':
        G.S[key] = s            # 提示词照 gpt_cg.py 那一套拼，后头再添山铜纪试画查出来的几条
        p, refs = G.job(key)
        p += ' ' + CUT_FEEL + CUT_COUNT + CUT_HEADBAND
        if BOW_RX.search(s['text']):
            p += CUT_BOW
        if s.get('raw'):
            p += CUT_WOUND
        p += ''.join(v for k, v in FOLK.items() if k in s['text'])
        return p, refs
    raise KeyError(key)


# 11-14 查图：场面里只写了 night-wing 没给立绘的，画成了一条龙。各族的叫法照这个补一句。
FOLK = {
    'night-wing': "A night-wing is a person of a winged demon-kin people: a man or woman of ordinary human size and shape with a pair of large dark wings growing from the back, most often membranous like a bat's, sometimes feathered; never a dragon, a bat or a bird. ",
    'fire-horn': "A fire-horn is a person of a horned demon-kin people, ordinary human size and shape with horns on the head that may glow or burn like torches; never a beast. ",
    'bone folk': "The bone folk are a tall, pale demon-kin people with bone-white skin; they are living people, not skeletons. ",
}


# 11-14 山铜纪试画六幅查出来的：弓弦的两半在后脑勺会合、拉弦的手却在一边（纷争纪、月银纪也出过好几回），
# 头上的布带画成了蒙眼，逃命的孩子一个个在笑、人数多画一个，划在手上的伤口拖到了手腕上。
import re  # noqa: E402
BOW_RX = re.compile(r'\bbows?\b|bowstring|\barchers?\b|\barrows?\b')
CUT_BOW = ("Archery is drawn correctly. A bow is gripped at its middle by the bow hand. The bowstring is one single string: on a drawn bow it runs straight from the upper tip of the bow "
           "to the fingers of the drawing hand, and from those same fingers straight to the lower tip, so the two halves of the string meet at one point inside the drawing hand, "
           "and the back end of the arrow sits on the string at that point. An undrawn bow has one straight string from tip to tip. ")
CUT_FEEL = ("Every face shows the feeling the scene gives that person: nobody grins or laughs unless the scene says so, and people running from danger look afraid, desperate or grimly set. ")
CUT_COUNT = "Where the scene gives a number of people, draw exactly that many. "
CUT_HEADBAND = "A band or strip of cloth tied round someone's head sits on the forehead above the eyes and never covers the eyes, unless the scene says the eyes are covered. "
CUT_WOUND = "Wounds are only where the scene puts them; there is no cut across the inside of any wrist or forearm. "


STOP = []


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
        s = S[key]
        if s['kind'] == 'road' and s['n'] > 1:          # 长卷一段一段接：左边那一段出完才出这一段
            left = os.path.join(OUT, 'r%02d.png' % (s['n'] - 1))
            for _ in range(240):
                if os.path.exists(left) or STOP:
                    break
                time.sleep(15)
            if not os.path.exists(left):
                print('没开（左边那一段还没有）', key, flush=True)
                return
        if s['kind'] == 'mon' and not s['text']:
            print('样图，不出（拷过来了）', key, flush=True)
            return
        if s['kind'] == 'stele':
            tp = tpl_path(s['mat'])
            if not os.path.exists(tp):
                print('没开（样板还没有）', key, flush=True)
                return
        if s['kind'] in ('join', 'patch') and not os.path.exists(os.path.join(OUT, key + '_in.png')):
            print('没开（先 --cut / --pcut %s）' % key, flush=True)
            return
        if key in FIX and all(os.path.exists(p_) for p_ in fix_srcs(key)):
            out = gen(os.path.join(OUT, key), FIX[key][1], refs=fix_srcs(key), timeout=1500)
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


GROUPS = {'tpl': 'tpl', 'stele': 'stele', 'road': 'road', 'era': 'era', 'hor': 'hor', 'walk': 'walk', 'scenes': 'cut', 'tex': 'tex', 'prop': 'prop', 'mon': 'mon'}

# 11-23 用户看了 p6_j3 重画那一稿：裙子正中裂开，一条白丝袜的腿从几层裙摆中间穿出来，两腿的站法看不清。拿那一稿（挪成 备选/角前_1123/p6_j3_r2.png）当底只改裙子和腿。
FIX['p6_j3'] = (os.path.join(BK1123, 'p6_j3_r2.png'), _KEEP +
    "Look at the young woman in the maid headdress in the middle, lunging forward with the golden key-shaped blade. Her skirt is drawn split open down the front, "
    "with one leg in a white stocking showing through the middle of the ruffled layers, and her two legs do not read clearly. Redraw only her skirt and legs: "
    "the skirt is ONE closed, full, floor-length layered skirt with no opening or slit at the front; its dark outer layer and the white ruffled petticoat underneath both fall closed all the way round, "
    "the white ruffles showing only along the hem. Her legs are completely hidden inside the skirt; she stands in a wide forward lunge, her front foot stepping toward us and her back foot planted behind, "
    "and only the toes of her two brown lace-up boots peek out under the hem, one in front and one behind, so the stance reads clearly. "
    "Keep her face, hair, headdress, ribbon, blouse, corset, sleeves, both arms and hands, the key-blade and the big golden key at her back exactly as they are." + _TAIL)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] == ['--left']:
        kinds = [GROUPS[a] for a in args[1:] if a in GROUPS] or list(GROUPS.values())
        left = [k for k in sorted(S) if S[k]['kind'] in kinds and not os.path.exists(os.path.join(OUT, k + '.png'))]
        print(' '.join(left))
        print('缺', len(left))
        sys.exit(0)
    if args[:1] in (['--cut'], ['--merge'], ['--tone']):
        for a in args[1:]:
            {'--cut': join_cut, '--merge': join_merge, '--tone': join_tone}[args[0]](int(a.lstrip('j')))
        sys.exit(0)
    if args[:1] in (['--pcut'], ['--pmerge']):
        for a in args[1:]:
            (patch_cut if args[0] == '--pcut' else patch_merge)(a)
        sys.exit(0)
    if args[:1] == ['--wnorm']:
        for a in (args[1:] or list(WALKS)):
            walk_norm(a)
        sys.exit(0)
    kinds = [GROUPS[a] for a in args if a in GROUPS]
    keys = [k for k in sorted(S) if k in args or S[k]['kind'] in kinds or (args == ['all'] and S[k]['kind'] not in ('join', 'patch'))
            or (S[k]['kind'] == 'cut' and k.split('_')[0] in args)]
    if not keys:
        print('键：', ' '.join(sorted(S)))
        sys.exit(0)
    if os.environ.get('CG_DRY'):
        for k in keys:
            p, refs = job(k)
            print('==', k, len(p), '字', [os.path.basename(r) for r in refs])
            print(p)
        sys.exit(0)
    roads = [k for k in keys if S[k]['kind'] == 'road']
    rest = [k for k in keys if S[k]['kind'] != 'road']

    def chain():
        for k in roads:
            one(k)
    with ThreadPoolExecutor(int(os.environ.get('CG_WORKERS', '3')) + (1 if roads else 0)) as ex:
        fut = ex.submit(chain) if roads else None
        list(ex.map(one, rest))
        if fut:
            fut.result()
