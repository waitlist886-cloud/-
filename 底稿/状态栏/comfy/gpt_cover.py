#!/usr/bin/env python3
# 风月五张卡的封面（11-25，用户：“我在想或许可以给风月这里的每一张卡重新跑一个封面”）。
# 五张：moon 月银纪、strife 纷争纪、bronze 山铜纪、pre 迷宫纪前传、now 迷宫纪此刻。一套同一个构图框架：
#   前景偏中两位那一纪的要紧人物（此刻那一张是主角的背影加两位旅伴），膝上或腰上取景，占画面下三分之二；
#   背后中段是那一纪的标志场面；上四分之一是干净的天空或暗部；人物近旁一盏暖光（火把、炉火、余烬、提灯、门外的晨光），压在那一纪的冷色调上。
# 规格：风月卡里的 cov 是平台图床的 /cover 变体，线上那几张卡的封面取回来是 400×300（4:3），风月建卡技能的封面流程也写 4:3；
#   背景 bgi 照桌面横版 16:9。Codex 出图只有 3:2（1536×1024），这里出 3:2，再从同一张裁 4:3 封面（1365×1024）和 16:9 背景（1536×864）。
# 画法照 gpt_cg.py 的光锥那一路（LOOK、FACE、BODY、POSE、DIFF），护栏照 gpt_cg5.py、gpt_cg_now.py（不画十字、月牙、字、现代的东西，兽耳不另画人耳）。
#   python gpt_cover.py moon strife       各出一稿（<纪>_v<N>.png，N 接着往上数，旧稿不动）
#   python gpt_cover.py all               五张各出一稿
#   CG_DRY=1 只打提示词和参考图；CODEX_HOME 指到用哪个 Codex 号；COVER_OUT 换出图的文件夹（默认会话的临时目录）
#   python gpt_cover.py --crop moon_v2 [上移像素]   从这一稿裁 4:3 封面和 16:9 背景，写到 out/发布卡_风月_四纪/封面/
# 要带 PIL 的 Python（ComfyUI 那一个）。
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_cg as G  # noqa: E402
import gpt_cg5 as C5  # noqa: E402  只用它的 gen5（--ephemeral 那一版）和几句护栏
from PIL import Image  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.environ.get('COVER_OUT') or os.path.join(os.environ.get('TEMP', HERE), 'claude', '85a810c2c0993c77', '5db2a7b9-8873-4e56-8761-1fd2a1d38fa6', 'scratchpad', '风月封面', '稿')
FINAL = os.path.join(ROOT, 'out', '发布卡_风月_四纪', '封面')
G.OUT = OUT
G.POR_ALL = ['立绘_v3', '立绘_月银纪史诗', '立绘_纷争纪', '立绘_山铜纪', '立绘_前传', '立绘_诸国期', '立绘_萨尔维斯']
STYLE = ('anaxa', 'fire')          # 五张同一对画法参考，好看得出是一套
ERA_CN = {'moon': '月银纪', 'strife': '纷争纪', 'bronze': '山铜纪', 'pre': '迷宫纪前传', 'now': '迷宫纪此刻'}

LEAD = ("Draw in the rendering of the attached official Light Cone illustrations from Honkai: Star Rail (the first %d attached pictures), for style only: do not copy their characters, costumes, props or composition. "
        "This is the cover key visual of one volume of a five-volume Japanese fantasy role-playing game series, the picture that shows on the game's card in a store list: "
        "bold, clear and striking even when shown small, painted with the full finish of that game's Light Cone art. ")
# 五张一样的框架
SERIES = ("All five covers of the series share one layout, and this cover follows it exactly. "
          "The named characters stand in the lower two thirds of the picture, near the middle of its width, large and close to us, seen from about the knees or the waist up, their heads at about the middle of the picture's height. "
          "Behind them, filling the middle band of the picture, stands the great landmark of this age, vast and far away. "
          "The top quarter of the picture is quiet: open sky or darkness with nothing important in it. "
          "One small warm light burns close to the characters and lights their faces, and it is the only warm colour against the cool palette of this age. "
          "Keep the characters and every important thing inside the middle four fifths of the width and away from the bottom edge: the picture will be trimmed a little on every side. ")
CUT_SCALE = ("Scale is shown boldly: where the scene names something vast (a beast, a wall, a tower, a pit, a mountain range), it is truly vast, "
             "and the sky, the ground and the light around it visibly react to it. ")
TAIL = ("Everyone is fully and modestly clothed; nothing is sexualized. No blood and no wounds are shown. "
        "The world is Western high fantasy of swords and magic with medieval Europe as its base: no East Asian garments, roofs or motifs, nothing from the real modern world, no firearms. "
        "Dragons are heavy Western wyrms with bat-like wings, no antlers, no whiskers. "
        "No real-world religious crosses anywhere: no cross shape on any roof, spire, tower, gravestone, crown, banner, shield or pendant. "
        "There is no moon, no crescent and no eclipse anywhere in the picture. "
        "No text, no letters, no numbers, no runes that read as writing, no logo, no watermark, no title, no frame, no border, no caption, no user interface: the picture carries no words at all. "
        "Landscape picture, wider than tall, aspect ratio 3:2, the painting filling the whole frame edge to edge.")
TAIL_NOW = ("Everyone is fully and modestly clothed; nothing is sexualized. No blood and no wounds are shown. "
            "The world is Western high fantasy of swords and magic, in a late age of brass, steam and arcane engines: gas lamps and glowing crystal lamps, armoured steam trains on stone viaducts, "
            "wooden and brass airships with sails, clockwork and riveted iron belong to it. Clothes, armour and buildings are European fantasy: no East Asian garments, roofs or motifs. "
            "Nothing from the real modern world: no cars, no phones, no screens, no neon, no plastic, no modern firearms, no modern uniforms. "
            "No real-world religious crosses anywhere: no cross shape on any roof, spire, tower, gravestone, crown, banner, shield or pendant; spires end in plain points, balls or bells. "
            "There is no moon, no crescent and no eclipse anywhere in the picture. "
            "No text, no letters, no numbers, no logo, no watermark, no title, no frame, no border, no caption, no user interface: the picture carries no words at all; signs and notices are blank or show only fine illegible lines. "
            "Landscape picture, wider than tall, aspect ratio 3:2, the painting filling the whole frame edge to edge.")

# 每一张：who（立绘键, 衣着格, 提示词里叫他什么）、light、camera、text、young
SC = {
    'moon': dict(
        who=[('hilda', 'casual', 'the fire-carrier girl with the ash-gold braid (left)'), ('ge7_maren', 'battle', 'the tall reaper with the cloth-wrapped sword (right)')],
        young=True,
        light="the small warm orange flame of a torch held by the girl, low in the middle of the picture, against the deep silver-blue of an endless night; cold silver starlight rims the hair and shoulders from behind",
        camera="a little below the two figures and close, looking slightly up past them toward the night sky; the two stand side by side just left and right of the centre",
        text=("Scene: the long night before the first dawn of the world, on a high frozen ridge of pale grass above a vast dark land. "
              "On the left of centre stands the fire-carrier girl, who looks fifteen: ash-gold hair in one thick braid hanging below the waist and tied with a scrap of faded red yarn, the fringe tousled by the wind, bright amber eyes, "
              "her late father's fox-fur coat two sizes too big with the sleeves rolled up and a hemp rope for a belt, a small smoke-blackened clay pot hanging at her neck on a cord with one ember glowing in it. "
              "She faces us three-quarter, and in her right hand she holds up a short wooden torch at chest height, its small flame bright and steady; her left hand cups the clay pot at her chest. Her look is stubborn and warm, fixed on the far land. "
              "One step behind her on the right stands the reaper, a tall man of twenty-four: deep wheat-bronze hair tied loosely at the back with a single straw, eyes the green of young wheat, a clean handsome face with the mouth held shut, "
              "his face and hands fair and pale, clearly lighter than the burnt-copper skin of his neck and arms; his eyes are green, not gold; "
              "a short linen tunic with a leather jerkin and a rope belt, cloth wraps on his forearms; a long sword wrapped in cloth from end to end is slung across his back, its wrapped hilt rising over his right shoulder. "
              "He faces us three-quarter, his right hand gripping the strap across his chest, his left hand empty at his side, watching over the girl's head into the dark. "
              "Behind them the land falls away to an endless plain under the night, dotted with a few tiny far campfires where people huddle together. "
              "Across the plain, far away and half-lost in silver mist, the colossal beasts of the first age loom as huge pale silhouettes outlined in cold silver light, each bigger than the mountains, standing on the far land in the middle band of the picture, their heads below the top quarter: "
              "a great dragon with vast bat-like wings half-spread over a mountain range, a giant stag whose branching antlers are as tall as hills, and a colossal shaggy bear walking through cloud. No beast has tusks or horns that curve into a pale arc. "
              "The top quarter of the picture is deep, quiet night sky scattered with fine silver stars. The whole palette is silver-blue and indigo; the only warm colour is the torch, the ember in the pot and the tiny far campfires.")),
    'strife': dict(
        who=[('z2_nolen', 'battle', 'the armoured emperor in the lion-head helm (left)'), ('calantia', 'battle', 'the elf watcher with the great longbow (right)')],
        light="the warm gold-orange fire of an iron brazier on the wall walk between and behind the two figures, against a blood-red sky; the emperor's engraved armour glows dawn-gold along its grooves",
        camera="on the top of a great wall, close and a little low, looking along the wall walk; the two stand just left and right of the centre",
        text=("Scene: the top of an immense wall of white stone that runs out to the horizon on both sides, crowned with battlements and square towers, each tower with a tiny beacon fire. "
              "On the left of centre stands the emperor, facing us three-quarter: a full suit of bright mirror-polished silver plate engraved all over with flowing lines and sunrise rays that glow dawn-gold, "
              "a closed helm shaped like a lion's head with the visor down and only a thin line of green light in the slit, a great mane of pale gold hair spilling out of the helm over the shoulders, no crown, "
              "a huge white cloak with a deep white fur collar blown sideways by the wind. Both gauntleted hands rest one over the other on the pommel of a great white-gold two-handed sword, longer than a man, planted point-down on the stone in front of him. No face and no skin are seen. "
              "On the right of centre, on the battlement edge, stands the elf watcher, facing us three-quarter: tall and slim, long pale-green hair shading to silver in one long braid, long pointed elf ears, amber eyes, two faint wind-reddened streaks across her cheekbones, "
              "a patched grey-white hooded cloak with the hood down and pinned back, a moss-green tunic, a leather bracer on her left forearm, a quiver of grey-fletched arrows at her hip. "
              "Her great longbow is slung diagonally across her back on a leather strap, its upper end rising above her left shoulder; the bow is at rest, its single string lying straight and flat along the wood from tip to tip. "
              "Both her hands rest on the top stone of the battlement in front of her. She looks out over the wall, still and piercing. "
              "Between and a little behind them on the wall walk burns an iron brazier, and beside it, small, stands a plain wooden cradle covered with a wool blanket. "
              "Beyond the wall to the right the land is a scorched red plain under a blood-red sky, and on the far horizon colossal dark shapes of demon gods rise like storm clouds, taller than mountains, "
              "horned and shadowed, their outlines burning with ember light, faceless at this distance; they are unmistakably giant figures with heads, horns, shoulders and arms, not mountains, and they fill the right half of the middle band. "
              "The top quarter of the picture is dark red smoke and cloud, quiet. The palette is crimson, dark red and white stone; the warm gold of the brazier and the armour answers it.")),
    'bronze': dict(
        who=[('s4a_thornevia', 'casual', 'the tall soldier woman with short copper-gold hair (left)'), ('s4c_baltina', 'casual', 'the grey-haired girl with the notebook (right)')],
        young=True,
        light="the warm orange glow of a heap of embers on the ground in front of the two figures, lighting them from below, against a cool grey rainy daylight; a thin break in the clouds lets one pale copper shaft of light fall on the far field",
        camera="close and a little low, at the edge of a field; the two stand side by side just left and right of the centre",
        text=("Scene: the morning after an endless war, on a grey field in light rain. "
              "On the left of centre stands the soldier woman, who looks twenty-seven, facing us three-quarter: tall and tight-shouldered, old-copper gold-brown hair cut short with a knife to just under the ears, the front locks singed paler, pale gold eyes, "
              "a thin white scar at the tail of one eyebrow, a faded plain officer coat with a high collar over old patched leather armour, a worn belt with a plain straight sword whose grip is wrapped in hemp cord. "
              "Her sword stays sheathed in a plain dark scabbard hanging at her left hip, only its hemp-wrapped hilt showing at her waist; her right hand hangs relaxed at her side and holds nothing; in her left hand she holds up a newly forged iron ploughshare: the pointed, slightly curved triangular blade of a farm plough, unmistakably a plough's share, "
              "still faintly glowing orange at its edge as if she has just lifted it out of the embers. Her look is level and weary and a little hopeful. "
              "On the right of centre stands the grey-haired girl, who looks sixteen, facing us three-quarter: small and straight-backed, long straight ash-grey hair worn loose, gold eyes faintly lit, a tiny ember-red mark at one temple, short pointed ears, pale cool skin, "
              "a long deep grey coat with a high collar closed to the throat over a dark high-necked dress, black leather gloves. She holds a small open leather notebook in her left hand and a grey pen in her right, about to write, calm and serious, looking at the plough blade. "
              "At their feet lies a heap of glowing embers and blackened iron scraps. "
              "Behind them stretches a wide grey field with fresh dark plough furrows, and across it, far away in the middle band, stand rows of colossal rusted clockwork soldier-machines, each as tall as a tower but small with distance, kneeling in a long line with their heads bowed, their tops below the top quarter, "
              "half overgrown with grass and moss, some partly dismantled, with thin smoke rising from a forge among them. Between the field and the machines stand a few plain white stone steles of different heights, smooth and blank. "
              "The top quarter of the picture is soft grey rain cloud, quiet. The palette is cool grey, slate and weathered copper-green; the only warm colour is the embers, the hot edge of the plough blade and the far shaft of copper light.")),
    'pre': dict(
        who=[('q1_molly', 'casual', 'the small halfling healer girl with the lamp (left)'), ('q1_bent', 'casual', 'the barefoot well-digger with the knotted rope (right)')],
        young=True,
        light="the warm amber light of the bronze lamp held up by the halfling girl, lighting both faces, against the cool brown dusk; deep inside the pit far below a faint amber glow",
        camera="close and a little low, on the rim of a vast pit; the two stand side by side just left and right of the centre, the pit opening behind and below them",
        text=("Scene: dusk at the lip of the Great Labyrinth. "
              "On the left of centre stands the halfling girl, small, the height of a human child of thirteen, facing us three-quarter: a round face with rosy cheeks, honey-gold curly hair tied at the back with a strip of white cloth, light green eyes, "
              "a small tuft of white down on the tip of each ear (just a little fluff, not wings), a grey-white short robe with the hem tucked into her belt, the sleeves rolled to the elbow, "
              "a medicine box wider than her back strapped on her back: a plain box of dark leather with brass corners and no emblem at all on it. "
              "With her right hand she holds up a bronze cart lamp, its shade blackened on one side, a white candle burning inside it; her left hand holds the strap of the medicine box. She looks up at her companion, bright and chattering. "
              "On the right of centre stands the well-digger, a man of twenty-five, facing us three-quarter: not tall, broad-shouldered and long-armed, straw-yellow hair cropped very short under an oilcloth cap, a round face with a small scar across the bridge of the nose, olive-green eyes, "
              "a grey wool coat with mended cuffs over a coarse shirt, brown trousers rolled at the ankle. He stands upright on both legs on the rim, his body facing us. A coil of knotted rope with a small bronze bell on its end hangs over his left shoulder, his left hand holding the coil; his right hand is raised to shade his eyes as he looks down into the pit, cheerful and alert. "
              "Behind and below them opens the great well: one vast round pit in the open ground, several hundred paces across, its inner walls stepping down ring below ring into darkness, with wooden stairs, ladders and tiny lantern lights clinging to the rings, a faint amber glow far down in the depths. "
              "Along the far rim stand a camp of canvas tents, and a wide wooden notice board: a plain rectangle of planks between two posts, nothing sticking up above its top edge, with rows of pale paper slips pinned on it fluttering in the wind, blank or with only fine illegible lines. "
              "There are no tall wooden poles with crossbars anywhere. "
              "The top quarter of the picture is a quiet dusk sky of dull bronze and smoky brown. The palette is copper-brown, umber and dark teal shadow; the only warm colour is the lamp and the lantern lights.")),
    'now': dict(
        who=[('ariya', 'battle', 'the crimson-haired mage with the staff (left, outside)'), ('mia', 'battle', 'the thief with the faded red scarf (right, outside)')],
        light="the gold-white light of sunrise flooding in through the opening doors toward us, against the deep indigo-violet shadow of the hall; rim light on the edges of the cloak and the door leaves",
        camera="from inside a tall dim hall, low and just behind the protagonist, looking out through a pair of great doors being pushed open; the protagonist is in the centre foreground, the two companions outside on the steps just left and right of the centre",
        text=("Scene: dawn, the moment a pair of tall arched wooden doors with brass fittings swings open from inside a dim stone hall. The two door leaves are already swinging outward and stand half open at the left and right edges of the doorway. "
              "In the foreground a little right of the centre, seen purely from behind and cut off at the hips by the bottom of the frame, stands the protagonist, a young adventurer whose face and hair are never seen: a hooded travelling cloak with a deep hood pulled up over the head, the hood covering the whole head and all of the hair, so that only the rounded back of the cloth hood shows, no hair, no ear, no cheek and no neck visible; a pack on the back; "
              "the protagonist stands right beside the right door leaf, so close that its edge is just beside the right shoulder: the right hand rests flat on the edge of that door at shoulder height with the elbow bent, giving it the last push; the left arm hangs relaxed at the side under the cloak. "
              "The arm is short and natural, upper arm and forearm of normal human length: the hand is less than a forearm's length from the shoulder. The protagonist does not touch the left door, which stands wide open far away on the left. A strong wind rushes in through the opening, blowing the cloak back toward us, and loose paper slips and leaves fly past. "
              "Outside, a few steps below on wide stone stairs, two companions have turned back toward the door to wait, facing us: "
              "on the left the crimson-haired mage, a young woman of eighteen with long straight vivid crimson hair and a side fringe, amber-gold eyes, a slim star-shaped gold hair ornament, a fitted black battle coat with a high collar, "
              "a short crimson mantle over one shoulder with a round gold clasp; her right hand holds a tall dark staff upright whose head is a large teardrop red crystal, her left hand raised a little in greeting, a cool proud half-smile. "
              "On the right the thief, a young woman of eighteen with warm dark brown hair in a high messy ponytail, big lively amber eyes, brass flight goggles pushed up on her forehead, a faded red scarf, a fitted dark grey hooded jacket with crossed straps and pouches; "
              "she beckons toward us with her right hand, her left hand on her hip, a quick grin. "
              "Beyond them, filling the middle band, lies a vast city built around the mouth of an enormous round pit: terraces, domes and spires step down on every side to the rim of the pit, which opens dark and huge in the middle distance with faint lights deep inside it; gas lamps still lit, an armoured steam train crossing a stone viaduct, "
              "two wooden airships with sails in the sky, and on the far horizon behind the city a colossal snow-capped mountain range, the Skyspine, its peaks catching the first gold light. "
              "The top quarter of the picture is the dark arched lintel of the hall above the doors and a quiet indigo-violet sky beyond it. The palette is indigo, violet and deep blue; the warm colour is the sunrise gold pouring through the doors.")),
}


def job(era):
    s = SC[era]
    style = [os.path.join(G.LC, n + '.png') for n in STYLE]
    refs = list(style) + [G.ident(k, c) for k, c, _ in s['who']]
    who = G.MANY % (len(s['who']), '; '.join(d for _, _, d in s['who']))
    p = ((LEAD % len(style)) + SERIES + (G.LOOK % (s['light'], s['camera'])) + who + G.POSE + G.DIFF + s['text'] + ' ' + CUT_SCALE + G.FACE + G.BODY
         + (G.YOUNG if s.get('young') else '') + (TAIL_NOW if era == 'now' else TAIL))
    p += ' ' + C5.CUT_FEEL + C5.SMALL + C5.NO_CROSS
    if C5.BOW_RX.search(s['text']):
        p += C5.CUT_BOW
    if C5.EARS_RX.search(s['text']):
        p += C5.EARS
    if C5.GREAT_WELL_RX.search(s['text']) or 'Great Labyrinth' in s['text']:
        p += C5.GREAT_WELL
    if era == 'now':
        p += ("Only the protagonist is seen from behind; the two companions outside face us. Nobody else is in the picture except tiny far figures in the city. ")
    else:
        p += ("Exactly the two named characters are in the picture; nobody else, except tiny far figures where the scene names them. ")
    return p, refs


# ---- 竖版盒绘（11-25 用户贴了一屏经典 JRPG 盒绘说“封面大概这种感觉”）----
# 一支队伍层层叠在竖版画面上（三到六位，最前正中一位当主角），后头压一个巨大的身影或者那一纪的标志，上方五分之一留干净的标题带（标题另外排版叠上去，图上不画字）。
# 上面那五张横版的留作同一个场面横着铺开的背景（人少一些）。键写 box_<纪>，稿叫 box_<纪>_v<N>.png。
BOX_LEAD = ("Draw in the rendering of the attached official Light Cone illustrations from Honkai: Star Rail (the first %d attached pictures), for style only: do not copy their characters, costumes, props or composition. "
            "This is the box art of one volume of a five-volume Japanese fantasy role-playing game series, a tall cover in the manner of classic JRPG box art: "
            "the whole party of that age stacked in layers in one heroic group picture, a colossal shape of that age looming behind them, painted with the full finish of that game's Light Cone art, saturated colour and dense detail. ")
BOX_SERIES = ("All five covers of the series share one box-art layout, and this cover follows it exactly. "
              "The top fifth of the picture is a clean title band: open sky, light or shadow only, with no head, no face, no weapon tip and nothing important in it, because a title will be laid over it later. Nothing rises into the top fifth: not the colossal shape, not a mountain peak, a tower, a building, a banner or a weapon; the sky there is plain and quiet. "
              "Below the title band, one colossal shape of this age looms over the whole upper-middle part of the picture, behind the party. "
              "In the lower three fifths stands the party, stacked in layers like on a game box: the main character in the front centre, the largest figure, seen from about the thighs up; "
              "the others arranged around and behind on both sides at different depths and heights, each one fully visible from at least the waist up, none hiding another's face, each in a pose and with an item that shows who they are. "
              "Several layers of depth: the party, the landscape of the age behind them, the colossal shape behind that, and the sky. Strong light from high behind the party rims every figure, and one warm light near the main character lights the faces. "
              "Keep every face and every important thing inside the picture with a margin on all sides; nothing is cut off at the left or right edge except scenery. ")
BOX_REFS = ("The next %d attached pictures are reference sheets of the party, two characters to a picture at most: each character is shown as a full figure with a close-up of the same face to its right. In order: %s. "
            "Keep each one's face, eye colour, hair colour, hairstyle, race marks, build and clothes so that every character is instantly recognisable, and draw them in new poses for this picture. ")
BOX_COUNT = ("Count the people: exactly %d characters are in the party%s, nobody else except tiny far figures. Every one of them has exactly two arms and two hands; "
             "no hand, arm or weapon floats without an owner, and every hand that holds something really grips it. ")
TAIL_BOX = lambda t: t.replace("Landscape picture, wider than tall, aspect ratio 3:2", "Portrait picture, taller than wide, aspect ratio 2:3")

BOX = {
    'moon': dict(
        who=[('hilda', 'casual', 'the fire-carrier girl with the ash-gold braid, the main character'), ('ge7_maren', 'battle', 'the tall reaper with the cloth-wrapped sword'),
             ('kain', 'battle', 'the storm herdsman with the iron-capped staff'), ('pora', 'battle', 'the pearl diver with the pale pearl crown'),
             ('ge7_ronan', 'battle', 'the very tall golden-eyed boy with the white-ash spear')],
        young=True,
        text=("Scene: the long night before the first dawn of the world, on a high frozen ridge. "
              "Front centre, the main character: the fire-carrier girl, who looks fifteen, ash-gold hair in one thick braid tied with faded red yarn, bright amber eyes, her late father's fox-fur coat too big for her with a hemp rope belt, "
              "a small smoke-blackened clay pot with one ember glowing in it hanging at her neck. She holds up a short wooden torch high in her right hand, its flame bright, the warmest light in the picture; her left hand cups the clay pot. "
              "Behind her right shoulder (on the viewer's right) the tall reaper, twenty-four, wheat-bronze hair tied with a straw, green eyes, a fair face and pale hands but the neck and arms burnt copper, "
              "a cloth-wrapped long sword across his back, his right hand on the strap at his chest. "
              "On the viewer's left, a step behind, the storm herdsman, about twenty-five, black hair singed into tight curls, storm-grey eyes, a leopard-skin vest over a leather jerkin, gripping an iron-capped white-ash staff across his body in both hands, small arcs of lightning on it. "
              "Further left and lower, the pearl diver, a young woman who looks nineteen, long ink-black hair drifting as if under water, pale grey-blue eyes, a sea-green diver's wrap, a crown of pale pearls glowing blue on her head, one hand at her throat as if about to sing. "
              "Behind on the far right, standing tallest, the golden-eyed boy, sixteen but grown to a man's frame, untidy blue-black hair, a boiled-leather cuirass, holding a white-ash spear upright beside him. "
              "Behind and above the party, below the title band, a colossal dragon of the first age rises over the mountains with vast bat-like wings half-spread, pale and silver-outlined in mist, bigger than the mountains, its fire glowing faintly in its throat; "
              "beside it in the mist the antlers of a giant stag tall as hills. Far below the ridge, a great ritual bonfire burns on the dark plain with tiny people gathered round it, and more tiny campfires scattered to the horizon. "
              "The title band at the top is deep quiet night sky with fine silver stars. Palette: silver-blue and indigo; the only warm colours are the torch, the ember, the bonfire and the dragon's throat.")),
    'strife': dict(
        who=[('z2_nolen', 'battle', 'the armoured emperor in the lion-head helm, the main character'), ('calantia', 'battle', 'the elf watcher with the longbow'),
             ('z1_zvia_a', 'formal', 'the night-demon girl with crimson horns and a candle'), ('z3_konstanze', 'battle', 'the shield-line girl with the coiled gold braid'),
             ('z4b_brunhild', 'casual', 'the red-bearded dwarf gunner')],
        young=True,
        text=("Scene: the top of an immense wall of white stone that runs to the horizon, square towers with beacon fires along it, under a blood-red sky. "
              "Front centre, the main character: the emperor in full bright mirror-polished silver plate engraved with flowing lines and sunrise rays glowing dawn-gold, a closed lion-head helm with the visor down and only a thin green light in the slit, "
              "a great pale gold mane spilling from the helm, no crown, a huge white fur-collared cloak blown out by the wind; both gauntleted hands rest on the pommel of a great white-gold two-handed sword planted point-down before him. No face and no skin are seen. "
              "On the viewer's right, a step behind, the elf watcher: tall, long pale-green hair in a long braid, long pointed elf ears, amber eyes, a patched grey-white cloak, her longbow slung diagonally across her back on a strap with its string lying straight along the wood, one hand raised to shade her eyes as she looks out. "
              "On the viewer's left, a step behind, the night-demon girl, seventeen: long black braid, very pale skin with a bluish cast, a dark cloak with the hood down. Her horns: a pair of long slender glossy dark-crimson horns, almost black at the root, growing from the top of the head just above the temples, rising straight upward first and then curving backward in one smooth arc, the tips pointing back and a little up, both the same size; they never curve inward toward each other and never form a crescent or a ring shape. Her eyes are dark red, and the pupil in each eye is one thin black vertical slit like a cat's eye in daylight, running from the top of the iris to the bottom; her eyes are open wide, looking straight at us, with the slit pupils drawn as crisp black vertical lines and a bright highlight beside each slit, exactly like the close-up face on her reference sheet; never a round pupil, never a round dark dot. She holds a lit candle stub forward in her left hand, calm. "
              "Further right and lower, the shield-line girl, seventeen: deep-gold hair in a thick braid coiled at the back of her head, grey-blue eyes, an oversized leather jerkin with a small iron chest plate, holding a round wooden shield on her left arm. "
              "Lower left in front, the dwarf gunner: short and broad, a red-brown beard plaited in two strands with copper rings, pale grey eyes, a heavy leather apron over work clothes, a short brass ramrod over his shoulder. "
              "Between the party, on the wall walk, an iron brazier burns, and beside it stands a small wooden cradle covered with a wool blanket. "
              "Behind and above the party, below the title band, colossal shadowy demon gods rise over the scorched red plain beyond the wall like storm clouds, taller than mountains, horned, their outlines burning with ember light, faceless at this distance. "
              "The title band at the top is dark red smoke and cloud. Palette: crimson, dark red and white stone, with the warm gold of the brazier and the armour.")),
    'bronze': dict(
        who=[('s4a_thornevia', 'casual', 'the tall soldier woman with short copper-gold hair, the main character'), ('s4c_baltina', 'casual', 'the grey-haired demon-kin girl with the notebook'),
             ('s3b_delo', 'casual', 'the small violet-haired demon-kin woman with the little lamp'), ('s4a_joren', 'casual', 'the short dwarf cook with ginger braids'),
             ('s3a_hano', 'casual', 'the bone-white demon-kin gatekeeper')],
        young=True,
        text=("Scene: the morning after an endless war, on a grey field in light rain with fresh plough furrows. "
              "Front centre, the main character: the soldier woman who looks twenty-seven, old-copper gold-brown hair cut short with a knife, the front locks singed paler, pale gold eyes, a faded officer coat over patched leather armour, "
              "her plain sword sheathed in a dark leather scabbard at her left hip, only the hemp-wrapped hilt showing and no bare blade. In her left hand she holds up a newly forged iron ploughshare, unmistakably the pointed, slightly curved triangular share of a farm plough with a socket at its back, its edge still glowing orange from the embers at her feet; her right hand hangs at her side. "
              "On the viewer's right, a little behind, the grey-haired girl who looks sixteen: long straight ash-grey hair, gold eyes faintly lit, a tiny ember-red mark at one temple, short pointed ears, a long deep grey high-collared coat, black gloves, an open notebook in one hand and a grey pen in the other. "
              "On the viewer's left, a step behind, the violet-haired demon-kin woman, twenty-seven: small and slight, deep violet hair hanging below the waist with ends glinting faintly as if dusted with ash, short pointed ears, violet eyes, a dark indigo dress under a grey shawl; she holds a small lamp in her left hand and her right hand is held out open, palm up, a gentle look. "
              "Lower left in front, the dwarf cook: short and stout, two thick ginger-red braids coiled on her head, a burn-patched oilcloth apron, holding a big iron ladle over her shoulder, grinning. "
              "Behind on the far right, standing tallest, the gatekeeper: a tall lean man of a bone-white demon-kin folk, pale skin with bone-white gleaming knuckles and brow ridges, a washed-out grey cloak, holding a thick ledger closed against his chest. "
              "At the party's feet a heap of glowing embers and scrap iron. "
              "Behind and above the party, one colossal rusted clockwork soldier-machine kneels with its head bowed, as tall as a tower, half overgrown with moss and grass, its bowed head reaching up only to just below the title band, a forge's thin smoke rising beside it; "
              "more kneeling machines fade into the rain in a long row, and plain white blank stone steles stand in the grass between the field and the machines. "
              "The title band at the top is soft grey rain cloud with one pale copper shaft of light breaking through. Palette: cool grey, slate and weathered copper-green; the warm colours are the embers and the glowing ploughshare.")),
    'pre': dict(
        who=[('q1_bent', 'casual', 'the barefoot well-digger with the knotted rope, the main character'), ('q1_molly', 'casual', 'the small halfling healer girl with the lamp'),
             ('q1_kaya', 'casual', 'the horned tiefling farm girl with mist-blue hair'), ('q1_talon', 'casual', 'the tall fire-horn demon-kin soldier'),
             ('q1_linus', 'casual', 'the ink-blue-haired craftsman with the brass beam lamp')],
        young=True,
        text=("Scene: dusk at the lip of the Great Labyrinth, the day the adventurers' guild first stood at its rim. "
              "Front centre, the main character: the well-digger, twenty-five, straw-yellow hair cropped short under an oilcloth cap, a round face with a small scar across the bridge of the nose, olive-green eyes, a grey wool coat with mended cuffs, "
              "a coil of knotted rope with a small bronze bell over his left shoulder, his left hand on the coil, his right hand clenched at his chest, grinning with resolve. "
              "In front of him on the viewer's left, small, the halfling healer girl, who looks thirteen though seventeen: honey-gold curls tied with a strip of white cloth, light green eyes, a small tuft of white down on the tip of each ear, a grey-white short robe, "
              "a plain dark leather medicine box with brass corners and no emblem on her back; she holds up a bronze cart lamp with a white candle burning in it, the warmest light in the picture. "
              "On the viewer's right, a step behind, the tiefling farm girl: mist-blue hair, a pair of horns, fair skin with cheeks reddened by fog, a black leather jerkin over a tucked-up dress, a black iron forearm guard, a farm pitchfork held upright. "
              "Behind on the far left, standing tallest, the fire-horn demon-kin soldier: very tall and broad, two horns growing straight up from the forehead glowing faintly like embers, black leather armour, a heavy pick-hammer over his shoulder. "
              "Behind on the far right, the craftsman: thin, ink-blue hair tied back carelessly, cyan-blue eyes, a teal short coat with a leather harness, holding up a long brass beam lamp whose glass front throws a pale beam. "
              "Behind and below the party opens the great well, one vast round pit several hundred paces across, its walls stepping down ring below ring into darkness with tiny lantern lights; "
              "and out of the pit rises one colossal surging wave of black tide, its crest staying below the title band, dark teal and black like smoke and water, curling over the far rim taller than towers, flecked with faint cold sparks, faceless. "
              "On the near rim behind the party a camp of canvas tents and a plain wooden notice board with pale paper slips, blank or with only fine illegible lines. "
              "The title band at the top is a quiet dusk sky of dull bronze and smoky brown. Palette: copper-brown, umber and dark teal; the warm colour is the lamp and the lantern lights.")),
    'now': dict(
        who=[('mia', 'battle', 'the thief with the faded red scarf, the main character facing us'), ('ariya', 'battle', 'the crimson-haired mage with the red-crystal staff'),
             ('sid', 'battle', 'the tall silver-haired northern berserker'), ('sylphy', 'battle', 'the silver-haired high elf ranger'),
             ('fiona', 'battle', 'the golden-haired saintess in white')],
        text=("Scene: dawn on the great stone stairs outside the adventurers' guild of a vast city built around the mouth of an enormous round pit. "
              "In the very front at the bottom centre, seen purely from behind and cut off at the waist by the bottom of the frame, stands the protagonist in a hooded travelling cloak with the hood up; the face is never seen. "
              "Facing us just beyond the protagonist, front centre, the main character of the party: the thief, eighteen, warm dark brown hair in a high messy ponytail, big lively amber eyes, brass flight goggles pushed up on her forehead, a faded red scarf, "
              "a fitted dark grey hooded jacket with crossed straps; she holds out her right hand toward the protagonist and us with a quick grin, her left hand on her hip. "
              "On the viewer's left, a step behind, the crimson-haired mage, eighteen: long straight vivid crimson hair, amber-gold eyes, a star-shaped gold hair ornament, a black battle coat with a short crimson mantle, holding her tall dark staff with a teardrop red crystal upright, a small magic circle turning by her other hand. "
              "On the viewer's right, a step behind, the northern berserker, nineteen and tall: shaggy silver-white hair, pale icy blue eyes, a thin chain circlet with ice-blue crystals, a dark navy riveted leather coat with a fur collar; over her right shoulder rests a one-handed war axe with a short wooden haft wrapped in old rope and a single iron blade, nothing else on it. "
              "Behind on the far left, the high elf ranger: long straight silver-white hair, pale green eyes, long pointed elf ears, a dark forest-green field jacket with silver leaf-shaped guards, a slim bow slung across her back, one hand raised in greeting. "
              "Behind on the far right, the saintess, eighteen: soft golden hair past the shoulders, amber eyes, a thin gold circlet, a white field coat with silver star-etched shoulder plates, holding a short silver staff with a small glowing star-shaped head. "
              "Behind and below them the city steps down in terraces of domes, spires and gas lamps to the rim of the vast pit, an armoured steam train crossing a stone viaduct; "
              "and behind the city the colossal snow-capped mountain range of the Skyspine towers across the whole width, its highest peaks staying below the title band, its peaks catching the first gold light, with two wooden airships with sails crossing in front of it. "
              "The title band at the top is a quiet indigo-violet dawn sky. Palette: indigo, violet and deep blue; the warm colour is the sunrise gold on the faces and the peaks.")),
}
BOX_N = {'moon': (5, ''), 'strife': (5, ''), 'bronze': (5, ''), 'pre': (5, ''), 'now': (6, ', counting the protagonist seen from behind')}


def pair_sheet(name, pairs):
    """两个人一张的对照：各人 G.ident 那一条（全身加脸）左右并排。"""
    os.makedirs(os.path.join(OUT, '_ident'), exist_ok=True)
    dst = os.path.join(OUT, '_ident', name + '.png')
    if not os.path.exists(dst):
        ims = [Image.open(G.ident(k, c)).convert('RGB') for k, c in pairs]
        gap = 60
        im = Image.new('RGB', (sum(i.width for i in ims) + gap * (len(ims) - 1), 1024), G.GREY)
        x = 0
        for i in ims:
            im.paste(i, (x, 0))
            x += i.width + gap
        if im.width > 3000:
            im = im.resize((3000, round(1024 * 3000 / im.width)), Image.LANCZOS)
        im.save(dst)
    return dst


def job_box(era):
    s = BOX[era]
    style = [os.path.join(G.LC, n + '.png') for n in STYLE]
    w = s['who']
    groups = [w[i:i + 2] for i in range(0, len(w), 2)]
    refs = list(style) + [pair_sheet('box_%s_%d' % (era, n), [(k, c) for k, c, _ in g]) for n, g in enumerate(groups)]
    order = '; '.join('picture %d shows %s' % (len(style) + 1 + n, ' and, to its right, '.join(d for _, _, d in g)) for n, g in enumerate(groups))
    p = ((BOX_LEAD % len(style)) + BOX_SERIES + (BOX_REFS % (len(groups), order)) + G.POSE + G.DIFF + s['text'] + ' ' + CUT_SCALE + G.FACE + G.BODY
         + (G.YOUNG if s.get('young') else '') + TAIL_BOX(TAIL_NOW if era == 'now' else TAIL))
    p += ' ' + C5.CUT_FEEL + C5.SMALL + C5.NO_CROSS + (BOX_COUNT % BOX_N[era])
    if C5.BOW_RX.search(s['text']):
        p += C5.CUT_BOW
    if C5.EARS_RX.search(s['text']):
        p += C5.EARS
    if C5.GREAT_WELL_RX.search(s['text']) or 'Great Labyrinth' in s['text']:
        p += C5.GREAT_WELL
    p += ''.join(v for k, v in C5.FOLK.items() if k in s['text'])
    return p, refs


# ---- 用户给的新构图（11-26，box2_<纪>）----
# 用户看了盒绘第一版说“还是差了点意思”，五张各给了构图；又贴了八张经典 JRPG 主视觉当参考（只学做法，不喂图）：
# 景别差和大小对比、背靠背、对角线和动感、近景大脸、一个主色调点一个亮色；人少一点、脸大一点，别一排人站得一样大。
G.POR_ALL.append('立绘_神明')
BOX2_LEAD = ("Draw in the rendering of the attached official Light Cone illustrations from Honkai: Star Rail (the first %d attached pictures), for style only: do not copy their characters, costumes, props or composition. "
             "This is the key visual for one volume of a five-volume Japanese fantasy role-playing game series, a tall cover in the manner of the great modern JRPG key visuals: "
             "bold scale contrast between one huge near shape and small far figures, strong diagonals, everything in motion (hair, cloaks, light, sparks), "
             "a single dominant colour for the whole picture with one bright accent, painted with the full finish of that game's Light Cone art, dense detail. "
             "Nobody stands in a row and nobody is the same size as their neighbour: the figures are layered at clearly different distances and sizes. ")
BOX2_BAND = ("The top fifth of the picture is a clean title band of open sky, light or shadow with no face and nothing important in it, because a title will be laid over it later; "
             "only soft continuations of cloak, light or cloud may pass through it. ")
BOX2_REFS = ("The next %d attached pictures are reference sheets of the main characters: each character is shown as a full figure with a close-up of the same face to its right. In order: %s. "
             "Keep each one's face, eye colour, hair colour, hairstyle, race marks and build so that every character is instantly recognisable, and draw them in the new poses and clothes this picture describes. ")

BOX2 = {
    'moon': dict(
        refs=[[('sa6_kelsas', 'battle', 'the emperor with white-gold hair and the star-field cloak')], [('hilda', 'casual', 'the fire-carrier girl with the ash-gold braid')],
              [('ge7_maren', 'battle', 'the tall reaper with the cloth-wrapped sword'), ('pora', 'battle', 'the pearl diver with the pearl crown')]],
        young=True, count=None,
        text=("Composition: one great diagonal from the top right down to the bottom left, ten thousand years of an age stacked in one picture. "
              "In the upper right, just below the title band, very large and close (his figure from the hips up fills the whole upper right quarter of the picture, his shoulders as wide as a third of the picture's width), stands the emperor of the luminous empire seen purely from behind, high up on a crag of light: long white-gold hair loose over his shoulders, "
              "heavy dark-gold plate, a plain thin gold crown with small upright points floating a hand's breadth above his head, clearly a crown and not a flat halo ring. With his right arm he raises high above him a colossal dragon-hunting swordspear half again as tall as himself, its head not a small spear point but a long, broad, tapering sword-blade of aged dark gold and bronze as long as his own body, with a small cross-guard where the blade meets the shaft, its tip staying below the title band, "
              "held upright in one hand by its long shaft; his left arm hangs at his side. His face is not seen. "
              "From his shoulders a vast cloak pours down and spreads across the whole upper half of the picture like the curtain of the night sky: deep blue-black and full of small silver stars and faint constellations, its edges dissolving into the real night sky. "
              "Under the canopy of that cloak, arranged down the diagonal from upper right to lower left, stand the heroes of the old songs, small and distant near the emperor and larger toward the bottom, each one a little further back in time than the one above: "
              "highest, a red-curled girl scribe of the empire with a copper pen in her hair; below her a mist-blue-haired young priest in white holding a lamp; below him the pearl diver with long ink-black hair and a crown of pale pearls glowing blue, singing with a hand at her throat; "
              "below her a storm herdsman with black curls and a staff crackling with small lightning; and larger, the tall reaper with wheat-bronze hair tied with a straw, green eyes, a cloth-wrapped long sword on his back, looking up. "
              "Each of them faces a little toward the emperor above, in a different pose, none in a row. "
              "At the very bottom left, nearest to us and the closest face in the picture: the fire-carrier girl, who looks fifteen, kneeling in the snow, ash-gold hair in one thick braid tied with faded red yarn, bright amber eyes, her father's fox-fur coat too big for her, "
              "a small smoke-blackened clay pot at her neck on a cord; both her hands are cupped together in front of her chest holding one tiny flame of pure silver-white fire, the brightest point in the whole picture, lighting her face from below. She looks down at the flame. "
              "Background, in layers behind the heroes: colossal beasts of the first age half-hidden in silver mist (a great dragon with bat-like wings, a giant stag with branching antlers), "
              "the slender floating towers of the luminous empire drifting in the sky with pale light at their tips, and far below on the dark ground small walled city-states each burning a great silver-white fire. "
              "Palette: deep night blue and silver; the one accent is the silver-white flame in the girl's hands.")),
    'strife': dict(
        refs=[[('gw_veselan', 'formal', 'the goddess in the pale greatcoat')], [('z1_zvia_a', 'formal', 'the night-demon girl with crimson horns'), ('z2_nolen', 'battle', 'the armoured emperor in the lion-head helm')],
              [('z5b_wethlo', 'battle', 'the pale blood-demon swordsman'), ('z1_feige', 'casual', 'the old king of the snow line')]],
        young=True, count=None,
        text=("Composition: the picture is split down the middle by one colossal sword. "
              "In the upper middle of the picture, her head below the title band (the top fifth stays plain red cloud), the goddess towers over everything, enormous, seen from the waist up and as big as the sky: a woman who looks about thirty with short soft wavy warm-brown hair with a few ashen strands, steady grey eyes, a calm face, "
              "a washed-pale cream greatcoat with brass buttons buttoned to the throat, a thin ring of pale light behind her head. "
              "Both her hands rest flat, one over the other, on top of the cross-guard and pommel of a colossal plain sword that stands point-down in front of her: she presses down on it, she does not grip it. "
              "The blade runs straight down from her hands through the whole height of the picture to the ground, a long pale line of light that divides the picture into a left half and a right half. "
              "Left half, the side of the allied peoples: an immense white stone wall stained with smoke and dried blood, magic-crystal cannons glowing blue-white along it, floating towers in the sky, and behind them colossal radiant figures of the gods of war in golden armour, faceless at this distance. "
              "Right half, the side of the demon-kin: a scorched red plain, walking siege-temples and idol warships, and colossal horned demon gods rising like storm clouds with ember-lit outlines, faceless at this distance. Smoke and sparks roll across both halves. "
              "In the lower left, close to us, the two central characters with large faces: in front, the night-demon girl, seventeen, very pale skin with a bluish cast, waist-length black hair in one long braid, "
              "a pair of long slender glossy dark-crimson horns rising straight up from just above the temples and then sweeping backward and slightly outward in one smooth arc, the tips pointing back and away from each other, the gap between the two tips wider than the gap between the roots; the horns never bend inward toward each other and never form a crescent or a ring; both the same size; "
              "dark red eyes in which each pupil is one thin black vertical slit like a cat's eye, crisp and clearly drawn because her face is large; her head is turned in three-quarter view toward the right so that her horns are seen partly from the side, showing clearly that they sweep backward over the back of her head rather than curling toward each other; a dark cloak with the hood down; she holds a lit candle stub in her left hand at her chest. "
              "Just behind her shoulder on the left, also large and close, the armoured emperor (he must be in the picture) in bright mirror-polished silver plate engraved with sunrise rays glowing dawn-gold, a closed lion-head helm with the visor down and a thin green light in the slit, a great pale gold mane spilling from the helm, no face and no skin seen, "
              "a white fur-collared cloak blowing. "
              "Behind those two, smaller and further back along a diagonal toward the middle, the legends of both sides with different expressions: on the left, an old king of about fifty with a long silver-white braid threaded with ivory beads and a frost-ivory greatsword on his back, stern; "
              "an old bent white-haired king of about sixty-five with ember-red eyes and a small fire in a clay lamp in his hands, sorrowful; "
              "on the right side of the sword, a tall pale blood-demon swordsman with short black hair, very small horns, dark red slit-pupil eyes, black lacquered leather armour with a dark red stripe, a narrow straight sword low at his side, quiet and hungry; "
              "and a huge dark-skinned fire-horned demon-kin man with thick ram-like horns burning with orange flame, fully clothed in a dark leather war coat closed over the chest, fierce. "
              "Palette: crimson and dark red with smoke grey; the accents are the pale line of the great sword and the dawn-gold of the armour.")),
    'bronze': dict(
        refs=[[('baltina', 'formal', 'the silver-haired demon-kin queen'), ('thornevia', 'formal', 'the copper-haired soldier empress')],
              [('s1_himmel', 'battle', 'the blue-haired hero'), ('s3b_frieren', 'casual', 'the silver-haired elf mage')], [('s6n_maribel_dean', 'casual', 'the clockwork girl in black and white')]],
        young=False, count=None,
        text=("Composition: two queens back to back fill the upper half of the picture, below the title band, very large, seen in profile from the shoulders up, their backs touching, each looking out to her own side. "
              "On the left, facing left toward the west: the demon-kin queen, who looks about twenty-six, long straight ash-silver hair, gold eyes, cold pale skin, a small ember-red mark at one temple, short pointed ears only a little longer than human ears (not long elf ears), a still, distant look. Her jewellery is only a small red teardrop gem at each ear and a round red gem brooch: no cross-shaped earring, pendant or brooch. "
              "On the right, facing right toward the east: the soldier empress, who looks about twenty-seven, dark old-copper gold-brown hair in a braided bun with one long strand falling at the side, the front locks burnt paler, pale gold eyes, a firm look. Neither queen wears any dangling sword-shaped, dagger-shaped or cross-shaped earring or pendant: the empress wears no earrings at all, and nothing hangs below either queen's brooch. "
              "Their hair streams together in the wind behind their heads, silver and copper, and copper-coloured embers drift between them. "
              "Below their shoulders, as if seen through their two profiles like a double exposure, lies the whole age in smaller figures and scenes, layered on a diagonal: "
              "a field of fresh plough furrows in grey rain with a newly forged ploughshare glowing orange in a heap of embers; plain white blank stone steles standing in the grass; "
              "rows of colossal rusted clockwork soldier-machines kneeling with heads bowed, overgrown with moss; "
              "a party of four heroes walking together, small: a slight blue-haired young hero with a sword, a silver-haired elf girl mage with two long tails and a staff, a tall green-haired priest with square glasses, and a short broad dwarf in a horned iron helmet with a white beard and an axe; "
              "on the far right, seven tall dark silhouettes of demon generals standing on a ridge, horned and winged, faceless at this distance. "
              "Far back and very small, half hidden behind the party of heroes, no bigger than the heroes and easy to miss, a slender clockwork girl in an obsidian-black gown with a white lace headdress and a large gilded wind-up key at her back, looking off to one side, easy to miss. "
              "On the far horizon, very small, one warm glow of fire held inside the curved shape of a great ark, as if a ship carried a fire; nobody looks at it. "
              "Palette: cool grey and weathered copper; the one accent is the copper-orange of the embers and the glowing ploughshare.")),
    'pre': dict(
        refs=[[('q5b_thornevia', 'battle', 'the copper-haired soldier empress')], [('baltina', 'formal', 'the silver-haired demon-kin queen')],
              [('q4b_gideon', 'casual', 'the horned guild master'), ('q4a_orven', 'casual', 'the young map-maker of the deep well')]],
        young=False, count=None,
        text=("Composition: a black tide fills the whole background. "
              "From the great round pit of the labyrinth in the middle distance (a vast round open pit in the ground with ring-shaped terraces stepping down into darkness, not a flat maze pattern) a colossal black tide surges up and out, one towering wave of black water and smoke taller than mountains, rearing over the lands and about to break, its crest curling high, dark teal at its edges, filling the sky below the title band, flecked with cold sparks, faceless. "
              "Across the dark lands on both sides, the lights of the nations burn like countless tiny sparks, and arcs of blue-white electric lightning crackle and leap across the sky from tall iron masts and towers, crackling against the tide. "
              "In the foreground on the right, large, the soldier empress stands with her back to us, facing away into the tide: we see her back and the back of her head, and she glances back over her left shoulder so that only the line of her cheek and one pale gold eye show past the shoulder; "
              "old-copper dark gold-brown hair in a low braided bun with one long thin strand falling at the side, plain dark enchanted steel armour under a worn cloak blowing toward the tide, a plain straight sword drawn point-down in her right hand. "
              "Behind her, a little further back on the left and facing us: the demon-kin queen, ash-silver hair, gold eyes, cold pale skin, a small ember-red mark at one temple, short pointed ears only a little longer than human ears (not long elf ears), calm; Her jewellery is only a small red teardrop gem at each ear and a round red gem brooch: no cross-shaped earring, pendant or brooch.; "
              "she sits at a small stone table with a chessboard and with her right hand sets down a white king chess piece onto the board, the piece glowing softly, the brightest point in the picture; this king piece is topped by a small crown of upright points around a round ball, with no cross on top, and no piece on the board carries a cross. "
              "Below the chessboard, as if the board's light spills downward into the picture, the legends of this age stand small and layered on a diagonal: "
              "a tall tiefling with dark red hair in a tail and horns sweeping back with a copper ring on one; a young map-maker with a scroll case; a dark-skinned dwarf with a great forge hammer; "
              "a cloaked shadowy dark elf; a silver-haired elf woman with a spear; each in a different pose. "
              "Palette: deep umber and black with dark teal; the accents are the electric blue-white and the glowing white king piece.")),
    'now': dict(refs=None, same_as_box=True),
}
BOX2_NOW_BG = ("and behind the city the colossal snow-capped mountain range of the Skyspine towers across the whole width, its highest peaks staying below the title band,",
               "and filling the middle distance behind the party, dark and in deep shadow, the great gate of the city of Arcadia: a huge dim stone gateway at the rim of the pit, worn and soot-dark, with a few lamps, its tall doors made of plain vertical dark planks with iron studs, no cross shape and no cross-shaped iron bands on them; "
               "beyond it the city of Arcadia and the round pit of the Great Labyrinth fall away into blue shadow, and only on the far horizon the colossal snow-capped mountain range of the Skyspine catches the first gold light, its highest peaks staying below the title band,")


def job_box2(era):
    s = BOX2[era]
    if s.get('same_as_box'):
        p, refs = job_box(era)
        a, b = BOX2_NOW_BG
        assert p.count(a) == 1
        p = p.replace(a, b).replace("The title band at the top is a quiet indigo-violet dawn sky.", "The title band at the top is a deep, dark indigo-violet night-blue sky. The whole background is dark and moody, in deep shadow and blue dusk; the gate and the city glow only with small lamps; only the party in front is lit by warm light, so they stand out against the dark.")
        return p, refs
    style = [os.path.join(G.LC, n + '.png') for n in STYLE]
    sheets, order = [], []
    for n, g in enumerate(s['refs']):
        sheets.append(G.ident(*g[0][:2]) if len(g) == 1 else pair_sheet('box2_%s_%d' % (era, n), [(k, c) for k, c, _ in g]))
        order.append('picture %d shows %s' % (len(style) + 1 + n, ' and, to its right, '.join(d for _, _, d in g)))
    refs = style + sheets
    p = ((BOX2_LEAD % len(style)) + BOX2_BAND + (BOX2_REFS % (len(sheets), '; '.join(order))) + G.POSE + G.DIFF + s['text'] + ' ' + CUT_SCALE + G.FACE + G.BODY
         + (G.YOUNG if s.get('young') else '') + TAIL_BOX(TAIL))
    p += ' ' + C5.CUT_FEEL + C5.SMALL + C5.NO_CROSS + ("Every person has exactly two arms and two hands; no hand, arm or weapon floats without an owner, and every hand that holds something really grips it. ")
    p += ''.join(v for k, v in C5.FOLK.items() if k in s['text'])
    return p, refs


WIDE2 = ("This is the wide landscape version of this cover, used as a page background: the same scene and the same characters spread out horizontally across a 3:2 frame, "
         "the figures a little smaller so that more of the world shows on both sides; keep the top fifth quiet. ")
NOW_WIDE_BG = ("The whole view outside is much darker than a bright sunrise: an early blue dusk-dawn with deep indigo shadows, the only strong warm light being a thin gold rim on the far peaks and on the two companions. Behind the companions, at the bottom of the stairs, the middle band is dark and in deep shadow: the great soot-dark stone gate of the city of Arcadia with a few lamps, "
               "its tall doors plain vertical planks with iron studs and no cross shape; beyond it the city and the round pit of the Great Labyrinth fall away into blue dusk, "
               "and only the far snow-capped Skyspine range catches the first gold light. ")


def job_wide2(era):
    if era == 'now':
        p, refs = job('now')
        return p.replace("Beyond them, filling the middle band,", NOW_WIDE_BG + "Further beyond,", 1), refs
    p, refs = job_box2(era)
    p = WIDE2 + p.replace("Portrait picture, taller than wide, aspect ratio 2:3", "Landscape picture, wider than tall, aspect ratio 3:2")
    return p, refs


# ---- 月银纪照用户的草图（11-26，box3_moon_<落法>）：左右对称，一条中轴 ----
MOON3_BASE = ("Composition: strictly symmetrical left and right about one vertical centre line, like a church window or a tarot card. "
    "At the very top centre, the tip of a colossal dragon-hunting swordspear points straight up at the zenith: its head is a long, broad, tapering sword-blade of aged dark gold and bronze with a small cross-guard, "
    "and its point may pierce into the top strip of the picture. Below it, in the upper middle on the centre line, small and far away at the highest point, stands the emperor of the luminous empire seen purely from behind: "
    "long white-gold hair loose over heavy dark-gold plate, a plain thin gold crown with small upright points floating a hand's breadth above his head; with his right arm he holds the swordspear upright above him by its long shaft. His face is not seen. "
    "From his shoulders his cloak pours down and spreads out to the left and the right into one immense triangle, narrow at his shoulders and widening all the way down to the bottom corners of the picture, like a great tent or curtain: "
    "the cloak is a field of deep night sky full of silver stars and faint constellation lines, and it fills the whole middle of the picture. "
    "Two long sweeping curves of starlight run from the spear tip down to the left and the right edges, the upper rim of the night sky. "
    "Inside the starry cloak, on the centre line and a little to each side, the heroes of the old songs are arranged in tiers from top to bottom, %s "
    "the higher ones smaller and later in history and nearest the emperor, the lower ones larger and earlier: "
    "near the top a red-curled girl scribe of the empire with a copper pen in her hair and a book; a young priest in white with mist-blue hair holding a small lamp; a woman in white robes with a gold circlet; "
    "a man in a pale tunic with a short sword; the pearl diver with long ink-black hair and a crown of pale pearls glowing blue, a hand at her throat; the storm herdsman with tight black curls and a staff crackling with small lightning; "
    "a very tall black-haired youth with a white-ash spear and golden eyes; and lowest and largest, a little to the side of the centre, the tall reaper with wheat-bronze hair tied with a straw, green eyes, a cloth-wrapped long sword on his back. "
    "Eight or nine heroes in all, each in a different calm pose, faces turned slightly up toward the emperor. "
    "At the very bottom centre, the largest figure and the closest face, facing us straight on: the fire-carrier girl, who looks fifteen, kneeling in the snow, ash-gold hair in one thick braid over her shoulder tied with faded red yarn, bright amber eyes looking down at her hands, "
    "her father's fox-fur coat too big for her, a small smoke-blackened clay pot at her neck on a cord; both her hands are cupped together in front of her chest, five fingers on each, holding one tiny flame of pure silver-white fire, the brightest point in the whole picture, lighting her face from below. "
    "Outside the cloak, on the left and the right, the parts of the night it does not cover: on the left a colossal ancient dragon with vast bat-like wings rearing in silver mist, and below it the slender luminous towers of the empire; "
    "on the right a giant stag with branching antlers tall as hills, and below it floating towers drifting in the sky with pale light at their tips; the two sides mirror each other. "
    "Far below at the bottom edges, small walled city-states burn great silver-white fires. "
    "Palette: deep night blue and silver; the one accent is the silver-white flame in the girl's hands. ")
MOON3_WAYS = {
    'a': "standing as solid, fully painted figures on broad terraces and steps formed by the folds of the cloak, like a staircase of night,",
    'b': "drawn as translucent figures of pale silver starlight floating inside the starry cloak like constellations, their outlines traced by stars and thin glowing lines, each face still clear,",
    'c': "the lower ones solid and fully painted standing on folds of the cloak, the higher ones turning gradually into translucent figures of silver starlight like constellations as they rise toward the emperor,",
}


def job_moon3(way):
    style = [os.path.join(G.LC, n + '.png') for n in STYLE]
    refs = style + [G.ident('sa6_kelsas', 'battle'), G.ident('hilda', 'casual'), pair_sheet('box2_moon_2', [('ge7_maren', 'battle'), ('pora', 'battle')])]
    order = ('picture 3 shows the emperor with white-gold hair and the star-field cloak; picture 4 shows the fire-carrier girl with the ash-gold braid; '
             'picture 5 shows the tall reaper with the cloth-wrapped sword and, to its right, the pearl diver with the pearl crown')
    band = ("The top strip of the picture, about one eighth of its height, is quiet sky that only the spear tip and the two curves of starlight pass through, because a title will be laid over it later. ")
    p = ((BOX2_LEAD % len(style)) + band + (BOX2_REFS % (3, order)) + G.POSE + G.DIFF + (MOON3_BASE % MOON3_WAYS[way]) + CUT_SCALE + G.FACE + G.BODY
         + G.YOUNG + TAIL_BOX(TAIL))
    p = p.replace("Nobody stands in a row and nobody is the same size as their neighbour: the figures are layered at clearly different distances and sizes. ", "The figures are layered at clearly different distances and sizes. ")
    p += ' ' + C5.CUT_FEEL + C5.SMALL + C5.NO_CROSS + ("Every person has exactly two arms and two hands; no hand, arm or weapon floats without an owner, and every hand that holds something really grips it. ")
    return p, refs


# ---- 11-26 用户看了第二版：月银纪定 C 抠细处（box3_moon_d），山铜纪重画（box2_bronze4），前传只改巴尔缇娜的耳朵（box2_pre4），此刻照用户挑的那张横版的构图（box4_now、wide4_now）----
EAR = ("Her ears are exactly as on her reference sheet: small, about the size of a human ear, close to the head and only slightly pointed at the very tip; "
       "they are NOT long elf ears, they do not stick out sideways or upward, and they are mostly covered by her hair. ")
MOON3_WAYS['d'] = MOON3_WAYS['c']
MOON3_D_EMP = ("Below it, in the upper middle on the centre line, at the highest point, stands the emperor of the luminous empire seen purely from behind, small but clearly readable: "
               "we see the back of his head with long white-gold hair falling loose down his back, both his broad armoured shoulders in heavy dark-gold plate, his back, and his right arm raised straight up; "
               "his right gauntleted hand visibly grips the long shaft of the swordspear above his head, holding it upright; his left arm hangs at his side. "
               "A plain thin gold crown with small upright points floats a hand's breadth above his head. His face is not seen. "
               "The cloak is clearly fastened at both his shoulders and pours down from them; ")
MOON3_D_HEROES = ("near the top, smallest and latest, a red-curled girl scribe with freckles and a copper pen stuck in her curls, holding a book; "
                  "below her a slim young priest with short pale mist-blue hair and a few strands sticking up, in a plain white robe, holding a small lamp; "
                  "then the pearl diver, a young woman with long ink-black hair with a blue sheen drifting as if under water, pale grey-blue eyes, a sea-green diver's wrap, a crown of pale pearls glowing blue, one hand at her throat as if singing; "
                  "beside her the storm herdsman, a sturdy young man with black hair singed into tight curls, storm-grey eyes, a leopard-skin vest, an iron-capped white-ash staff with small lightning crawling on it; "
                  "then a white-haired poet boy of seventeen with snow-white hair tied back, lake-grey-blue eyes, a moss-green tunic, holding a long white ash-wood spear; "
                  "then a black-haired fisherman's boy of seventeen with sea-tousled hair and slate-blue eyes, a seal-skin vest, holding a round bronze shield; "
                  "lower still, larger, a very tall black-haired youth with blazing golden eyes in a boiled-leather cuirass holding a white-ash spear upright, "
                  "and beside him the tall reaper with deep wheat-bronze hair tied with a single straw, green eyes, a fair face, a cloth-wrapped long sword on his back. ")


def job_moon3d():
    p, refs = job_moon3('c')
    a = p[p.index("Below it, in the upper middle on the centre line, small and far away"):p.index("From his shoulders his cloak")]
    p = p.replace(a, MOON3_D_EMP).replace("From his shoulders his cloak pours down and spreads", "it spreads")
    i = p.index("near the top a red-curled girl scribe")
    j = p.index("Eight or nine heroes in all")
    return p[:i] + MOON3_D_HEROES + p[j:], refs


BOX2['bronze4'] = dict(
    refs=[[('s5b_baltina', 'casual', 'the silver-haired demon-kin woman'), ('s4a_thornevia', 'casual', 'the copper-haired soldier woman')],
          [('s2n_yolanda', 'casual', 'the red-scarfed rooftop swordswoman'), ('s3a_vista', 'casual', 'the raven-haired captain of the White Raven company')],
          [('gw_veselan', 'formal', 'the goddess in the pale greatcoat')]],
    young=True, count=None,
    text=("Composition: two women back to back fill the upper half of the picture, below the title band, very large, seen in profile from the shoulders up, their backs touching, each looking out to her own side. "
          "On the left, facing left toward the west: the demon-kin woman who leads the outcasts of the west, who looks about twenty-five, long straight ash-silver hair worn loose, gold eyes, cold pale skin, a small ruby-like mark at one temple, "
          "a plain long deep grey travelling coat with mountain-copper buttons over a plain dark dress; no crown, no jewels. " + EAR +
          "On the right, facing right toward the east: the soldier woman from the reed-hut slums, who looks about twenty-seven, old-copper gold-brown hair cut short with a knife to just under the ears, the front locks singed paler, pale gold eyes, a thin white scar at the tail of one eyebrow, "
          "a faded plain officer coat with the collar insignia torn off over old patched leather armour; no crown, no earrings, no jewels, nothing ornate: she is a plain soldier, not yet an empress. "
          "Their hair streams together in the wind behind their heads, silver and copper, and copper-coloured embers drift between them. "
          "Behind and above the two women, in the space between and behind their heads, a great goddess fills the upper middle of the picture, huge and faint, dissolving into light: "
          "a woman who looks about thirty with short soft wavy warm-brown hair with a few ashen strands, steady grey eyes, a pale cream greatcoat, a thin ring of pale light behind her head; "
          "she is wounded, one hand pressed to her side where a thin line of pale light leaks out, and she looks back over her shoulder at the world below as she fades; "
          "her shoulders and the hem of her coat break apart into drifting motes of light and pale flakes scattering outward into the sky. Her head stays below the title band. "
          "Below the two women's shoulders, as if seen through their profiles like a double exposure, lies the age in smaller figures and scenes, layered on a diagonal: "
          "on the left, night rooftops of a crowded lower city with a line of masked figures standing along the ridges holding swords that glow with light, "
          "and in front of them the rooftop swordswoman, a girl of sixteen with ragged apricot-red short hair, teal-green eyes, a thin scar across the bridge of her nose and a faded red headscarf, a grey short cloak, a sword with a line of light along its edge; "
          "in the middle, a company charging on foot through a smashed city gate, led by the White Raven captain, a broad-shouldered short woman with glossy raven-black hair tied back and violet eyes, in worn leather armour, a coil of rope on her belt, a white raven flying above her; "
          "beside them a band of cloaked people in grey with small dark-red flames burning on their blades and fingertips, and above a doorway a moth made of glowing ember-red ash; "
          "on the right, on a ridge, seven tall demon-kin generals standing side by side, each different and recognisable: a huge fire-horned man in black iron armour with glowing seams, "
          "a tall graceful crimson-haired succubus woman in a deep crimson dress, a thin night-wing man with large dark wings, a pale bone-white man in a charcoal robe holding a small clay lamp, "
          "a colossal bull-horned man in a smith's apron, a small violet-haired woman in a grey coat, and a sea-blue-haired deep-tide woman in a deep blue robe; behind them a few more demon-kin legends with horns. "
          "Plain white blank stone steles stand in the grass at the bottom, and a newly forged ploughshare glows orange in a heap of embers. "
          "On the far horizon, very small, one warm glow of fire held inside the curved shape of a great ark; nobody looks at it. "
          "Palette: cool grey and weathered copper; the accents are the copper-orange embers and the pale light of the fading goddess."))
BOX2['pre4'] = dict(BOX2['pre'])
BOX2['pre4']['text'] = BOX2['pre']['text'].replace("short pointed ears only a little longer than human ears (not long elf ears), calm; Her jewellery is only a small red teardrop gem at each ear and a round red gem brooch: no cross-shaped earring, pendant or brooch.; ",
                                                     "calm; " + EAR + "Her jewellery is only a small red teardrop gem at each ear and a round red gem brooch: no cross-shaped earring, pendant or brooch. ")
assert BOX2['pre4']['text'] != BOX2['pre']['text']

NOW4 = ("Composition: we are inside the dim stone hall of the adventurers' guild, looking out through a pair of tall arched wooden doors with brass fittings that are being pushed open at dawn, "
        "the door leaves made of plain vertical planks with brass studs and no cross shape on them. "
        "On the right in the foreground, seen purely from behind and cut off at the waist by the bottom of the frame, stands the protagonist, whose face and hair are never seen: a dark purple hooded travelling cloak with a deep hood pulled up over the whole head and all of the hair, "
        "so that only the rounded back of the cloth hood shows, no hair, no ear, no cheek; a rolled blanket and a pack with a small lamp on the back; the right hand rests flat on the edge of the right door leaf at shoulder height, giving it the last push, the arm of normal length. "
        "A strong wind rushes in, blowing the cloak back toward us, and loose paper slips and leaves fly past. "
        "Outside the doors a wide stone road with long flights of stairs runs away from us into the city, getting smaller and smaller into the distance. The companions are scattered along this road at very different distances: "
        "closest of all, just outside the doorway, one on each side: on the left the crimson-haired mage, eighteen, long straight vivid crimson hair, amber-gold eyes, a star-shaped gold hair ornament, a black battle coat with a short crimson mantle, "
        "her tall dark staff with a teardrop red crystal upright in her right hand, her left hand open toward us with a cool proud smile; and a little to the right of the centre the thief, eighteen, warm dark brown hair in a high messy ponytail, big amber eyes, brass flight goggles on her forehead, "
        "a faded red scarf, a dark grey hooded jacket with crossed straps, holding out her right hand toward us with a grin, her left hand on her hip. "
        "Further down the road, smaller: the tall northern berserker with shaggy silver-white hair and a fur-collared navy coat, a one-handed war axe on her shoulder, walking away down the stairs and turning her head back to look at us over her shoulder; "
        "further still, smaller, the high elf ranger with long silver-white hair, long pointed ears and a green field jacket with a bow on her back, walking on ahead with her back to us; "
        "and far away at the bottom of the stairs, small, the golden-haired saintess in a white coat, standing still and waiting, one hand raised to wave. "
        "Beyond them the vast city built around the mouth of an enormous round pit: terraces, domes and spires stepping down to the rim, gas lamps still lit, an armoured steam train crossing a stone viaduct, "
        "two wooden airships with sails in the sky, and on the far horizon the colossal snow-capped mountain range of the Skyspine with the sun rising beside its highest peak. "
        "Palette: indigo, violet and deep blue; the warm colour is the sunrise gold pouring through the doors onto the companions. ")


def job_now4(tall):
    style = [os.path.join(G.LC, n + '.png') for n in STYLE]
    refs = style + [pair_sheet('now4_0', [('ariya', 'battle'), ('mia', 'battle')]), pair_sheet('now4_1', [('sid', 'battle'), ('sylphy', 'battle')]), G.ident('fiona', 'battle')]
    order = ('picture 3 shows the crimson-haired mage and, to its right, the thief with the faded red scarf; picture 4 shows the silver-haired northern berserker and, to its right, the silver-haired high elf ranger; '
             'picture 5 shows the golden-haired saintess in white')
    lead = BOX2_LEAD % len(style)
    if not tall:
        lead = lead.replace("a tall cover", "a wide cover")
    band = BOX2_BAND if tall else "The top strip of the picture is the dark arched lintel of the doorway and quiet sky, with nothing important in it. "
    body = NOW4
    if tall:
        body = body.replace("Composition: we are inside", "Composition, gathered into a tall frame: the doorway is very tall and narrow, its arch near the top of the picture, and the road runs straight away from us deep into the picture. We are inside")
    p = (lead + band + (BOX2_REFS % (3, order)) + G.POSE + G.DIFF + body + CUT_SCALE + G.FACE + G.BODY
         + (TAIL_BOX(TAIL_NOW) if tall else TAIL_NOW))
    p = p.replace("Nobody stands in a row and nobody is the same size as their neighbour: the figures are layered at clearly different distances and sizes. ", "The figures are at clearly different distances and sizes along the road. ")
    p += ' ' + C5.SMALL + C5.NO_CROSS
    p += "Count the people: exactly six named figures (the hooded protagonist and five companions), nobody else except tiny far figures in the city. Every person has exactly two arms and two hands. "
    return p, refs



def job_moon3d_wide():
    p, refs = job_moon3d()
    p = WIDE2 + p.replace("Portrait picture, taller than wide, aspect ratio 2:3", "Landscape picture, wider than tall, aspect ratio 3:2")
    p += ("The emperor's crown is a small solid gold crown with a ring of upright pointed spikes, clearly a crown seen from behind, floating just above his head: it is NOT a flat ring of light and NOT a halo. "
          "The whole swordspear is inside the picture: its blade tip ends well inside the top strip of the picture, with clear dark sky above the tip, and nothing of it is cut off by the top edge. "
          "Keep the emperor and the spear smaller if needed so that the tip fits. ")
    return p, refs



# ---- 11-26 山铜纪第五版（box2_bronze5／wide2_bronze5）：用户嫌传奇和魔神将的长相对不上。露脸的九位拼一张格子表（cover_grid.py）当一张参考图 ----
import cover_grid as CG  # noqa: E402
BRONZE5_GRID = ['s4b_valdrak', 's4b_lithia', 's4b_selephen', 's5a_mortus', 's4b_grom', 's5a_delo', 's4b_sirentia', 's2n_yolanda', 's3a_vista']   # 七人照 g_碎碑矿坑 第 84 行，黎明那几年的版本
BRONZE5_CELLS = ("The last attached picture is a face chart: nine portrait cells in three rows of three, with no names on it. Each cell is one character of this picture, and each must be drawn with exactly that face, hair colour, hairstyle, eye colour, skin colour, horns, ears and marks: "
                 "row 1 cell 1: the fire-horned man, very tall, dark skin, short brown hair, red eyes, a pair of two curved dark horns, both horns whole; "
                 "row 1 cell 2: the succubus woman, long silver-white hair with a crimson flower and thorn ornament, red eyes, pointed ears, black gloves; "
                 "row 1 cell 3: the night-wing man, short ragged dark teal-black hair, teal eyes, pointed ears, large dark feathered wings; "
                 "row 2 cell 1: the bone-folk man, black hair, pale blue eyes, pale skin with bone-white patches on the cheek, holding a small clay lamp; "
                 "row 2 cell 2: the bull-horned colossus, dark skin, a pair of wide bull horns, long dark-brown hair in a thick braid, a beard, a leather smith's apron; "
                 "row 2 cell 3: the nightmare-blood woman, long wavy violet hair, violet eyes, small and slight, a worn brown coat; "
                 "row 3 cell 1: the deep-tide woman, long deep-blue hair, blue eyes, fin-shaped ears, faint scales on the cheek; "
                 "row 3 cell 2: the rooftop swordswoman, ragged apricot-red short hair under a faded red headscarf, teal-green eyes; "
                 "row 3 cell 3: the White Raven captain, glossy raven-black hair tied back, violet eyes, worn leather armour. "
                 "Draw them in the new poses this picture describes, not the poses of the cells. Anyone who is not in the chart is drawn only as a distant figure whose face cannot be seen. ")
BRONZE5_LOWER = ("Below the two women's shoulders, as if seen through their profiles like a double exposure, lies the age, layered on a diagonal, with fewer and larger figures so that every visible face is clear: "
                 "across the middle, on a ridge, the seven young demon-kin from the first seven cells of the face chart (they are not yet generals: plain travelling clothes, no crowns, no thrones) stand side by side at slightly different depths, each seen from the chest up, each face clearly drawn and matching its cell, "
                 "in this order from left to right: the fire-horned man with both his horns (row 1 cell 1), the succubus (row 1 cell 2), the bone-folk general with his clay lamp (row 2 cell 1), the bull-horned colossus (row 2 cell 2), "
                 "the nightmare-blood woman (row 2 cell 3), the night-wing man with his wings half open (row 1 cell 3), the deep-tide woman (row 3 cell 1). "
                 "Lower left, on night rooftops of a crowded lower city, the rooftop swordswoman (row 3 cell 2) crouching on a ridge with a sword glowing with a line of light, a few masked rooftop figures far behind her as small silhouettes; "
                 "lower right, the White Raven captain (row 3 cell 3) charging on foot through a smashed city gate with a coil of rope on her belt, a white raven above her, her company behind her only as dark silhouettes; "
                 "between them a few hooded figures seen from behind with small dark-red flames on their blades, and above a doorway a moth made of glowing ember-red ash. "
                 "Plain white blank stone steles stand in the grass at the bottom, and a newly forged ploughshare glows orange in a heap of embers. "
                 "On the far horizon, very small, one warm glow of fire held inside the curved shape of a great ark; nobody looks at it. "
                 "Palette: cool grey and weathered copper; the accents are the copper-orange embers and the pale light of the fading goddess.")


def job_bronze5(wide=False):
    t = BOX2['bronze4']['text']
    i = t.index("Below the two women's shoulders")
    BOX2['bronze5'] = dict(BOX2['bronze4'], refs=[BOX2['bronze4']['refs'][0], BOX2['bronze4']['refs'][2]], text=t[:i] + BRONZE5_LOWER)
    p, refs = job_box2('bronze5')
    os.makedirs(os.path.join(OUT, '_ident'), exist_ok=True)
    g = os.path.join(OUT, '_ident', 'bronze5_grid.png')
    if not os.path.exists(g):
        CG.grid(g, BRONZE5_GRID)
    refs = refs + [g]
    p = p.replace("The next 2 attached pictures are reference sheets of the main characters", "The next 2 attached pictures are reference sheets of the two women and the goddess")
    p += BRONZE5_CELLS
    if wide:
        p = WIDE2 + p.replace("Portrait picture, taller than wide, aspect ratio 2:3", "Landscape picture, wider than tall, aspect ratio 3:2")
    return p, refs



# 11-26 用户：“薇瑟兰有点怪啊这里的人体，不是背影+回眸+消散吗”。只换祂那一段（box2_bronze6／wide2_bronze6），别的照 bronze5
VESELAN_BACK = ("Behind and above the two women, in the space between and behind their heads, a great goddess fills the upper middle of the picture, huge and faint, dissolving into light. "
                "She is seen from BEHIND: her back and both shoulders face us, a pale cream greatcoat over her back, short soft wavy warm-brown hair with a few ashen strands at the back of her head. "
                "She looks back at us over her right shoulder: only her head and neck turn, so that we see her profile, one steady grey eye and the line of her cheek past the shoulder; her shoulders stay square to the back and her waist and back are not twisted at all, a turn any real body can make. "
                "Her arms hang down at her sides close to her body and are mostly hidden by her back and the coat; at most one hand is seen, and nothing crosses her chest. "
                "She is wounded: a crack of pale light leaks out from her back below the left shoulder blade and along her left side. "
                "She is dissolving from the bottom up: the hem of her coat, her cuffs and the ends of her hair break apart into drifting motes of light and pale flakes that float outward and upward into the sky, more and more toward the bottom, so that below her waist she is almost only light. "
                "No halo, or only the faintest trace of one. Her head stays below the title band. ")

OLD_VESELAN = 'Behind and above the two women, in the space between and behind their heads, a great goddess fills the upper middle of the picture, huge and faint, dissolving into light: "\n          "a woman who looks about thirty with short soft wavy warm-brown hair with a few ashen strands, steady grey eyes, a pale cream greatcoat, a thin ring of pale light behind her head; "\n          "she is wounded, one hand pressed to her side where a thin line of pale light leaks out, and she looks back over her shoulder at the world below as she fades; "\n          "her shoulders and the hem of her coat break apart into drifting motes of light and pale flakes scattering outward into the sky. Her head stays below the title band. '


def job_bronze6(wide=False):
    p, refs = job_bronze5(wide)
    i = p.index("Behind and above the two women, in the space between and behind their heads, a great goddess")
    j = p.index("Her head stays below the title band. ", i) + len("Her head stays below the title band. ")
    return p[:i] + VESELAN_BACK + p[j:], refs


def next_stem(era):
    n = 1
    while any(os.path.exists(os.path.join(OUT, '%s_v%d%s' % (era, n, x))) for x in ('.png', '.log', '.prompt.txt')):
        n += 1
    return os.path.join(OUT, '%s_v%d' % (era, n))


def one(era):
    p, refs = job_bronze6() if era == 'box2_bronze6' else job_bronze6(True) if era == 'wide2_bronze6' else job_bronze5() if era == 'box2_bronze5' else job_bronze5(True) if era == 'wide2_bronze5' else job_moon3d_wide() if era == 'wide3_moon_d' else job_now4(True) if era == 'box4_now' else job_now4(False) if era == 'wide4_now' else job_moon3d() if era == 'box3_moon_d' else job_moon3(era[-1]) if era.startswith('box3_moon_') else job_wide2(era[6:]) if era.startswith('wide2_') else job_box2(era[5:]) if era.startswith('box2_') else job_box(era[4:]) if era.startswith('box_') else job(era)
    stem = next_stem(era)
    os.makedirs(OUT, exist_ok=True)
    open(stem + '.prompt.txt', 'w', encoding='utf-8').write(p + '\n\nrefs: ' + ' | '.join(refs) + '\nhome: ' + str(os.environ.get('CODEX_HOME')) + '\n')
    t0 = time.time()
    try:
        out = C5.gen5(stem, p, refs=refs, timeout=1500)
        print(time.strftime('%H:%M:%S'), '好了', os.path.basename(stem), '%d 秒' % (time.time() - t0), [os.path.basename(o) for o in out], flush=True)
    except Exception as e:
        print(time.strftime('%H:%M:%S'), '失败', os.path.basename(stem), str(e)[:300], flush=True)


def crop(stem, shift=0, shift_bg=None):
    """竖版盒绘（box_<纪>_vN）：原样写 <纪>_封面.png（1024×1536），另压一份 jpg（800×1200，q88）。
    横版那一稿（<纪>_vN）：裁 16:9 背景（1536×864，竖向 shift_bg 是顶上裁掉的像素，默认裁上 112 下 48）和 4:3 的横版封面备用（1365×1024，横向居中，shift 往右挪的像素）。
    写 png 原尺寸和压过的 jpg（4:3 那张 1200×900，背景照原尺寸，q88）。"""
    if stem.startswith('box_'):
        era = stem[4:].split('_v')[0]
        cn = ERA_CN[era]
        os.makedirs(FINAL, exist_ok=True)
        im = Image.open(os.path.join(OUT, stem + '.png')).convert('RGB')
        im.save(os.path.join(FINAL, cn + '_封面.png'))
        im.resize((800, 1200), Image.LANCZOS).save(os.path.join(FINAL, cn + '_封面.jpg'), quality=88, optimize=True, progressive=True)
        print('定了', stem, im.size)
        return
    src = os.path.join(OUT, stem + '.png')
    im = Image.open(src).convert('RGB')
    if im.size != (1536, 1024):
        im = im.resize((1536, 1024), Image.LANCZOS)
    era = stem.split('_v')[0]
    cn = ERA_CN[era]
    os.makedirs(FINAL, exist_ok=True)
    x0 = (1536 - 1365) // 2 + shift
    x0 = max(0, min(1536 - 1365, x0))
    cov = im.crop((x0, 0, x0 + 1365, 1024))
    top = 112 if shift_bg is None else shift_bg
    top = max(0, min(1024 - 864, top))
    bg = im.crop((0, top, 1536, top + 864))
    cov.save(os.path.join(FINAL, cn + '_横版封面4比3.png'))
    bg.save(os.path.join(FINAL, cn + '_背景.png'))
    cov.resize((1200, 900), Image.LANCZOS).save(os.path.join(FINAL, cn + '_横版封面4比3.jpg'), quality=88, optimize=True, progressive=True)
    bg.save(os.path.join(FINAL, cn + '_背景.jpg'), quality=88, optimize=True, progressive=True)
    print('裁了', stem, '封面 x0=%d' % x0, '背景 top=%d' % top)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    a = sys.argv[1:]
    if a[:1] == ['--crop']:
        crop(a[1], int(a[2]) if len(a) > 2 else 0, int(a[3]) if len(a) > 3 else None)
        sys.exit(0)
    eras = list(SC) if a == ['all'] else ['box_' + k for k in BOX] if a == ['box'] else ['box2_' + k for k in BOX2] if a == ['box2'] else ['wide2_' + k for k in BOX2] if a == ['wide2'] else [x for x in a if x in ('box4_now', 'wide4_now', 'wide3_moon_d', 'box2_bronze5', 'wide2_bronze5', 'box2_bronze6', 'wide2_bronze6') or x.startswith('box3_moon_') or x.startswith('wide2_') or x in SC or (x.startswith('box_') and x[4:] in BOX) or (x.startswith('box2_') and x[5:] in BOX2)]
    if not eras:
        print('纪：', ' '.join(SC), '｜盒绘：', ' '.join('box_' + k for k in BOX))
        sys.exit(0)
    if os.environ.get('CG_DRY'):
        for e in eras:
            p, refs = job_bronze6() if e == 'box2_bronze6' else job_bronze6(True) if e == 'wide2_bronze6' else job_bronze5() if e == 'box2_bronze5' else job_bronze5(True) if e == 'wide2_bronze5' else job_moon3d_wide() if e == 'wide3_moon_d' else job_now4(True) if e == 'box4_now' else job_now4(False) if e == 'wide4_now' else job_moon3d() if e == 'box3_moon_d' else job_moon3(e[-1]) if e.startswith('box3_moon_') else job_wide2(e[6:]) if e.startswith('wide2_') else job_box2(e[5:]) if e.startswith('box2_') else job_box(e[4:]) if e.startswith('box_') else job(e)
            print('==', e, len(p), '字', [os.path.basename(r) for r in refs])
            print(p)
        sys.exit(0)
    with ThreadPoolExecutor(int(os.environ.get('CG_WORKERS', '5'))) as ex:
        list(ex.map(one, eras))
