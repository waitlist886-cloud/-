#!/usr/bin/env python3
# 载入页的分层图（11-26，美化第四轮方向稿第三节第 5 小节）。画风照风月五张封面（光锥的画法参考两张），走 Codex 出图（gpt_cg5.gen5）。
#   python -I -X utf8 底稿/门面/载入页/tools/gen_gate.py sky past_a fut_a door stones fog1 fog2     头一批（各出一稿，<键>_v<N>.png）
#   python -I -X utf8 底稿/门面/载入页/tools/gen_gate.py past_b fut_b                              破败那两版：拿定了的完好那一版当底（GATE_BASE_past=past_a_v1 这样指）
#   CODEX_HOME 指到哪个号；GATE_OUT 换出稿的文件夹（默认会话的临时目录）；CG_WORKERS 并几路（默认 3）；CG_DRY=1 只打提示词
# 图都不出字、不画十字和新月，魔物、英雄只出剪影。
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
sys.path.insert(0, COMFY)
import gpt_cg5 as C5  # noqa: E402

OUT = os.environ.get('GATE_OUT') or os.path.join(os.environ.get('TEMP', HERE), 'claude', '85a810c2c0993c77', '5db2a7b9-8873-4e56-8761-1fd2a1d38fa6', 'scratchpad', '载入页', '稿')
LC = os.path.join(ROOT, '语料', '人物参考_11-04', 'hsr_lc')
COV = os.path.join(ROOT, 'out', '发布卡_风月_四纪', '封面')
STYLE = [os.path.join(LC, 'anaxa.png'), os.path.join(LC, 'fire.png')]

LEAD = ("Draw in the rendering of the attached official Light Cone illustrations from Honkai: Star Rail (the first 2 attached pictures), for style only: do not copy their characters, costumes, props or composition. "
        "%s"
        "This picture is one layer of the loading screen of a Japanese fantasy role-playing game: the road a soul walks through the rift between the past, the future and the present of one world, among stars, fire and grey mist. "
        "Painted with the full finish of that game's Light Cone art: dense detail, luminous light, saturated colour inside a dark night palette. ")
WORLD = ("The world is Western high fantasy of swords and magic: medieval European stone, bronze and iron, and in its latest age brass, steam, gas lamps and wooden airships. No East Asian roofs, garments or motifs. Nothing from the real modern world. ")
TAIL = ("No people with visible faces: every figure is a dark silhouette or seen from behind, small or far. "
        "No real-world religious crosses anywhere: no cross shape on any roof, spire, tower, grave, banner or door; spires end in plain points, balls or flames. "
        "There is no moon, no crescent and no eclipse anywhere in the picture, and no pale curved arc against the sky. "
        "Every light and every star is a soft round glow or a soft round point: no star-shaped flares, no four-pointed sparkles, no lens-flare spikes, no horizontal or vertical light streaks crossing a light anywhere. "
        "No pole, mast, post or spire carries a crossbar: banners hang from walls or from single plain poles, spires and domes end in plain points, balls or small flames. "
        "No text, no letters, no numbers, no runes that read as writing, no logo, no watermark, no frame, no border, no user interface: the picture carries no words at all. ")
WIDE = "Landscape picture, wider than tall, aspect ratio 3:2, the painting filling the whole frame edge to edge. "
TALL = "Portrait picture, taller than wide, aspect ratio 2:3. "

COVER_REF = ("The third attached picture is the cover of one volume of this same game: match its world, its palette and its density of detail, but do not copy its characters or composition. ")

J = {
    'sky': dict(cover='迷宫纪前传_背景.jpg', shape=WIDE, text=(
        "Subject: the far background, an empty void with no ground and no figures. A boundless deep indigo-black night full of countless fine stars, a few brighter stars with soft glints, "
        "faint drifting nebulae of cold blue, violet and a little dusty rose, very dark overall. "
        "Down the middle of the picture runs one long, thin, vertical rift in the sky, like a hairline crack in black glass: very faint pale gold light seeps out of it, brightest at the centre, fading out toward the top and bottom. "
        "From the bottom edge a low bank of soft grey mist rises, thin and dark, filling only the bottom fifth. "
        "The middle of the picture is quiet and dark so that something small and bright can stand in front of it later. No planets, no moon, no sun, no land, no buildings, no figures. ")),
    'past_a': dict(cover='纷争纪_背景.jpg', shape=WIDE, text=(
        "Subject: the PAST of the world, a vast panorama of old ages seen from a dark rise, glorious and terrible, in a deep, old, smoky palette of umber, rust, dark crimson and dim gold, lit by fires. "
        "It reads like one long frieze of memories spread across the whole width, each further one darker and older: "
        "on the far left, wild primeval mountains under smoke, and on them colossal beasts of the first age, a giant stag with antlers like dead forests and a bat-winged Western dragon, alive, huge pale misty silhouettes in the haze whose faces are lost in the mist; "
        "left of centre, a long colossal wall of white stone running away to the horizon with beacon fires burning on its towers and the glow of a battle beyond it; "
        "right of centre, a soaring shining tower of white stone and gold, an imperial spire of an old radiant empire, whole and glowing at its tip with a steady light; "
        "on the far right, out of a black tide of smoke-like water and mist, one colossal monster head rises, faceless and eyeless, a dark mass of horns, ridges and jaws far taller than a whole city, outlined only by the fires below it, terrifying in scale; smaller dark monster silhouettes swarm in the tide around it. "
        "In the foreground along the bottom edge lie dark rocks, scattered huge beast ribs and old weapons, in near-black silhouette. "
        "The lower middle of the picture is dark open ground with nothing big in it. "
        "The top third is dark smoky sky that fades to almost pure black at the top edge. "
        "The past has only stone, bone, fire, banners and beasts: no airships, no machines, no gears, no steam and no smokestacks anywhere. "
        "No sword or spear stands upright in the ground, and nothing anywhere is shaped like a cross: the old weapons on the ground lie flat and broken. "
        "The colossal monster head on the right is enormous, taller than the whole wall and the whole city, its top reaching high into the sky, so huge it is frightening. "
        "The whole picture is darker, dimmer and older than an ordinary painting: smoke, ash and embers, the farthest things almost lost in shadow. ")),
    'fut_a': dict(cover='迷宫纪此刻_背景.jpg', shape=WIDE, text=(
        "Subject: the FUTURE of the world, seen far away and deep in the distance, ever brighter toward the centre, in a palette of deep indigo and violet lit by countless warm gold and white lights. "
        "In the middle distance a colossal city spreads across the whole width, terraces, domes and spires stepping down to the rim of an enormous round pit, a sea of tens of thousands of warm lights like a lake of lamps; "
        "above it great floating towers of stone and brass hang in the sky with lit windows, two wooden airships with sails crossing between them; "
        "strings of round paper-and-brass lanterns of an adventurers' guild hall glow gold along a grand stone stair on the left; "
        "on a high crag on the right stands one small lone hero seen purely from behind as a dark silhouette, a cloak blowing, a sword at the hip, looking toward the centre; the face is never seen. "
        "Exactly in the centre of the picture, at the vanishing point far away, the lights gather into one tall narrow vertical glow of white light, like light leaking from a far doorway, the brightest thing in the picture. "
        "The bottom third of the picture is soft dark mist that fades to almost pure black at the bottom edge, with nothing in it. "
        "The top edge is deep night sky with a few stars. ")),
    'door': dict(cover='迷宫纪此刻_背景.jpg', shape=TALL, text=(
        "Subject: one immense pair of closed double doors, seen straight on, perfectly symmetrical, standing alone, cut out on a flat, even, pure magenta background (#FF00FF) that fills everything around the doors. "
        "The doors fill most of the picture's height: a tall pointed arch of pale ancient stone framing two tall leaves of dark weathered bronze, closed. "
        "The two leaves meet exactly on the vertical centre line of the picture, and through the thin straight seam between them a crisp line of brilliant white light leaks, from the bottom of the doors to the top. "
        "The bronze leaves are carved in deep relief with rows of small flames, stars and spirals and a great ring of tiny flames around the centre, worn and old; no faces, no figures, no cross, no crescent. "
        "Wide shallow stone steps at the foot of the doors. "
        "The carvings on the doors are only round suns with many flame-shaped rays, small flames and spirals: no stars of any kind (no four-pointed, five-pointed or six-pointed stars), no religious symbols, nothing that reads as a cross; the great ornament at the centre is a round sun of many flame-shaped rays. "
        "The magenta background is completely flat: no mist, no glow, no shadow and no sky on it, and nothing of the door is magenta or pink. ")),
    'stones': dict(cover='山铜纪_背景.jpg', shape=WIDE, text=(
        "Subject: a sprite sheet of twelve separate paving stones for a road, laid out in a neat grid of four columns and three rows on a flat, even, pure magenta background (#FF00FF), "
        "each object isolated with wide magenta gaps around it, none touching, all seen from the same angle from above at about forty-five degrees, lit from the upper left, each about the same size and flat enough to walk on. "
        "Row 1: a flat slab cut from a giant pale beast bone; a broken section of a huge rib bone lying flat; a cracked block of white wall-stone with a soot scorch mark; a battered square block of wall stone with a small iron ring. "
        "Row 2: a broken copper-green bronze ploughshare lying flat; a slab of dark old field earth with a furrow and a bronze rivet in it; a curved block from the rim of an old stone well, worn smooth; a slab of dark stone with a rusted iron chain link set in it. "
        "Row 3: a worn stone doorstep with a brass edge; a step of polished stone with a small brass lantern hook; a slab of white marble with a faint inlaid gold spiral; a dark basalt slab with a thin glowing ember-orange crack. "
        "The magenta background is completely flat: no shadow, no glow and no ground on it, and nothing of any stone is magenta or pink. ")),
    'fog1': dict(cover=None, shape=WIDE, text=(
        "Subject: only mist. Thick banks of soft silver-grey mist and drifting fog rolling low across the picture on a pure black background, the densest along the bottom, thinning upward into wisps, "
        "lit faintly from below by a warm glow so that the undersides are a little gold. Nothing else at all: no ground, no figures, no buildings, no stars. ")),
    'fog2': dict(cover=None, shape=WIDE, text=(
        "Subject: only mist. Long thin streaks and curling wisps of pale grey-blue mist drifting sideways across a pure black background, scattered over the whole picture with black gaps between them, "
        "cold and faint. Nothing else at all: no ground, no figures, no buildings, no stars. ")),
}
# ---- 第二版（11-26 夜）：路上往前走，两侧一幅一幅的景从前方迎面掠过。景是“记忆的碎片”：主体居中，四边化进暗雾，不出方框 ----
SHARD = ("Subject: one memory fragment of this world, a single scene painted as a vignette: the subject sits in the middle, and toward all four edges the painting dissolves softly into dark smoky mist and deep night, "
         "so that the outer fifth of the picture on every side is almost black mist with no hard edge, no frame and no border. ")
SH = {
    'm1': "The first age, the long night before the first dawn: a vast frozen snowfield under a starry night, one great bonfire burning in the middle of it, the only warm light in a cold silver-blue world; tiny dark silhouettes of people huddle around it, seen from far away. ",
    'm2': "The age of great beasts: across a pale misty plain under a faint aurora walk colossal beasts as dark silhouettes, a giant stag whose antlers are like a dead forest and a bat-winged Western dragon with its jaws firmly closed, each bigger than the hills; they are only dark shapes against the pale sky, no faces, no eyes, no teeth visible. ",
    'm3': "The luminous empire: a city of slender white towers and white bridges shining with silver light, its tallest spire glowing at the tip with a soft round light; every tower stands on the ground, nothing floats in the sky, the sky holds only tiny round stars; seen from far away at night. ",
    's1': "The age of strife: an endless colossal wall of white stone at night running from the left to the far horizon, square towers along it each with a beacon fire, the fires shrinking into the distance like a line of stars. ",
    's2': "The black tide: beyond a white wall, a colossal black tide of smoke and water rises like a wave taller than mountains, and out of it looms one immense monstrous head as a dark silhouette with horns and jaws, faceless and eyeless, under a blood-red sky with ember light; tiny beacon fires on the wall below. ",
    'b1': "The age of bronze after the war: a grey rainy field with fresh plough furrows; two great long banners, one silver-grey and one copper-gold, fly from the tops of two tall plain poles standing back to back, the cloth streaming like long pennants, with no crossbar on either pole; far behind, a row of colossal rusted clockwork giants kneel in the rain with their heads bowed. ",
    'b2': "A walled city-state of the age of bronze at dusk: steep copper-green roofs, round towers, forge chimneys glowing orange, a stone bridge over a river, warm windows; seen from a hill. ",
    'p1': "The mouth of the Great Labyrinth at dusk: one vast round pit in open ground, several hundred paces across, its walls stepping down ring below ring into darkness, wooden stairs and tiny lantern lights clinging to the rings, a faint amber glow deep inside. ",
    'p2': "An adventurers' guild hall at night: a grand old stone hall with open doors spilling warm light, strings of round glowing paper-and-brass lanterns across the square in front, a wooden notice board with blank pinned papers, a few adventurers seen only from behind as small dark silhouettes. ",
    'n1': "Today: a vast city at dawn built in terraces around the rim of an enormous round pit, a sea of tens of thousands of warm lights, gas lamps, an armoured steam train crossing a stone viaduct, the first gold light on the domes. ",
    'n2': "Floating towers: great towers of stone and brass hang in the dawn sky above the clouds with lit windows; two airships with long gas envelopes and brass propellers pass between them, no sails on any ship. ",
    'n3': "A lone young hero seen purely from behind as a dark silhouette, standing on a high crag with a cloak blowing and a sword at the hip, looking out over a vast dawn land with a far city and mountains; the face is never seen. ",
}
for _k, _t in SH.items():
    J['sh_' + _k] = dict(cover={'m': '月银纪_背景.jpg', 's': '纷争纪_背景.jpg', 'b': '山铜纪_背景.jpg', 'p': '迷宫纪前传_背景.jpg', 'n': '迷宫纪此刻_背景.jpg'}[_k[0]], shape=WIDE, text=SHARD + _t)
J['road'] = dict(cover=None, shape=TALL, text=(
    "Subject: a texture seen from straight above, flat, with no perspective and no horizon: an ancient road running straight from the bottom edge to the top edge and filling the whole width of the picture, "
    "paved with worn irregular flagstones and cobbles of many kinds fitted tightly together like a real old road: pale ivory stone the colour of old bone, white wall-stone with faint soot marks, dark grey basalt with a few thin glowing ember cracks, and here and there a flat green-bronze plate worn smooth; "
    "the stones are all solid with no holes, no rings, no circles, no skulls, no bones, no metal frames and no rivets; moss and fine warm golden light in the joints between the stones. "
    "Even soft light from above, no shadows of anything else, no figures, no objects lying on it. The stones are small and many (about eight across the width), evenly spread from top to bottom so the texture can repeat. "))
RUIN = {
    'past_b': ('past_a', (
        "This is the second version of the attached last picture, used to flicker over it: keep exactly the same composition, the same camera, the same horizon and every big shape in the same place and the same size, "
        "but show the same things fallen into ruin: the living beasts are now only colossal bleached skeletons on the same mountains; the long wall is breached and broken, its beacon fires gone out to embers; "
        "the shining tower has snapped and collapsed, its upper half lying broken across the ground, its light dead; the colossal monster head in the black tide is still there in the same place, darker, the tide higher. "
        "Even darker and colder than the first version, ash falling. "
        "There are no grave markers anywhere: no crosses, no posts or poles with a crossbar, no little upright markers on the ground below the wall or anywhere else; only broken stones, bones and torn banners lie there. ")),
    'fut_b': ('fut_a', (
        "This is the second version of the attached last picture, used to flicker over it: keep exactly the same composition, the same camera, the same horizon and every big shape in the same place and the same size, "
        "but show the same future fallen into ruin: the city's lights are mostly out and its domes broken, the floating towers cracked and tilting with dark windows, the airships torn and drifting, "
        "the guild lanterns torn and unlit, the lone hero on the crag still there in the same place as a dark silhouette, the tall white glow at the centre still there but dimmer. Grey ash drifts. ")),
}


WORLD_OLD = ("The world is Western high fantasy of swords and magic in an old age: medieval European stone, wood, bronze and iron only. "
             "There are no airships, no flying ships, no balloons, no gas envelopes, no steam, no smokestacks and no machines in the sky or anywhere else. No East Asian roofs, garments or motifs. Nothing from the real modern world. ")
NO_FLAGS = ("There are no flags, banners, pennants or flagpoles anywhere in the picture, and no shields, coats of arms, crests or emblems on any wall or door. "
            "There are no factories, chimneys or smokestacks: forges and hearths glow only through open doors and windows. "
            "Monsters and beasts are pure dark silhouettes with closed mouths: no visible eyes and no visible teeth. "
            "Airships, where there are any, are long gas envelopes with brass propellers: no sails and no fins shaped like sails. ")
SKY_DOTS = ("Every star in the sky is a tiny round dot of light; nothing in the sky or on any tower is a star-shaped sparkle. "
            "The sun, where it shows at all, is only a soft round glow low on the horizon with no rays and no streaks; there is no round dark cloud ringed with light and no thin curved streak anywhere in the sky. ")


def job(key):
    if key.startswith('sh_'):
        s = J[key]
        refs = list(STYLE) + [os.path.join(COV, s['cover'])]
        lead = LEAD % '' + COVER_REF
        world = WORLD if key.startswith('sh_n') else WORLD_OLD
        tail2 = '' if key == 'sh_b1' else NO_FLAGS
        return lead + s['text'] + world + TAIL + SKY_DOTS + tail2 + s['shape'], refs
    if key in RUIN:
        src, extra = RUIN[key]
        base = os.environ.get('GATE_BASE_' + src.split('_')[0]) or (src + '_v1')
        s = J[src]
        refs = STYLE + [os.path.join(OUT, base + '.png')]
        lead = LEAD % ("The last attached picture is the first version of this very layer. ")
        return lead + extra + s['text'] + WORLD + TAIL + s['shape'], refs
    s = J[key]
    refs = list(STYLE)
    lead = LEAD % ''
    if s['cover']:
        refs.append(os.path.join(COV, s['cover']))
        lead += COVER_REF
    return lead + s['text'] + WORLD + TAIL + s['shape'], refs


def next_stem(key):
    n = 1
    while any(os.path.exists(os.path.join(OUT, '%s_v%d%s' % (key, n, x))) for x in ('.png', '.log', '.prompt.txt')):
        n += 1
    return os.path.join(OUT, '%s_v%d' % (key, n))


def one(key):
    p, refs = job(key)
    stem = next_stem(key)
    os.makedirs(OUT, exist_ok=True)
    open(stem + '.prompt.txt', 'w', encoding='utf-8').write(p + '\n\nrefs: ' + ' | '.join(refs) + '\nhome: ' + str(os.environ.get('CODEX_HOME')) + '\n')
    t0 = time.time()
    try:
        out = C5.gen5(stem, p, refs=refs, timeout=1500)
        print(time.strftime('%H:%M:%S'), '好了', os.path.basename(stem), '%d 秒' % (time.time() - t0), [os.path.basename(o) for o in out], flush=True)
    except Exception as e:
        print(time.strftime('%H:%M:%S'), '失败', os.path.basename(stem), str(e)[:300], flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    keys = [k for k in sys.argv[1:] if k in J or k in RUIN]
    if os.environ.get('CG_DRY'):
        for k in keys:
            p, refs = job(k)
            print('==', k, len(p), [os.path.basename(r) for r in refs]); print(p)
        sys.exit(0)
    with ThreadPoolExecutor(int(os.environ.get('CG_WORKERS', '3'))) as ex:
        list(ex.map(one, keys))
