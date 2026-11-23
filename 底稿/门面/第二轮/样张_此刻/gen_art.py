#!/usr/bin/env python3
# 门面第二轮样张「此刻」要的四张图（11-23）：牌桌正中那张正面朝上的牌、此刻那一本首屏的主画、路的开头两幅。
# 出在 out/门面第二轮/此刻/（不进库）。画法照门面定稿样 t2、迷宫纪主画 k4、大幅牌背 bb_3。
#   CODEX_HOME=C:/Users/waitl/.codex_b <ComfyUI 的 python> 底稿/门面/第二轮/样张_此刻/gen_art.py [键…]
#   键：card main r1 r2（不写就全出，出过的跳过）；CG_DRY=1 只打提示词
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
sys.path.insert(0, COMFY)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
from gpt_gen import gen  # noqa: E402

OUT = os.path.join(ROOT, 'out', '门面第二轮', '此刻')
REFD = os.path.join(OUT, 'ref')
T2 = os.path.join(ROOT, '底稿', '门面', '画风定稿样_t2.png')
K4 = os.path.join(COMFY, 'out', '门面_主画_11-10', 'k4.png')
SHELL = os.path.join(ROOT, '底稿', '门面', '小样_外壳', 'assets')


def png(src, name):
    """webp 参考转成 png 放 ref/ 下（Codex 认 png 稳）。"""
    from PIL import Image
    os.makedirs(REFD, exist_ok=True)
    dst = os.path.join(REFD, name)
    if not os.path.exists(dst):
        Image.open(src).convert('RGB').save(dst)
    return dst


NO_MOON = ' There is no moon and no crescent anywhere in the picture.'
WEST = (' The world is Western high fantasy at the dawn of a magical industrial age, Victorian-era Europe in spirit: European masonry, arcades, domes, '
        'brass, wrought iron and glass. No East Asian motifs: no paper lanterns, no pagodas or upturned eaves, no auspicious clouds. '
        'No modern cars, no skyscrapers, no neon signs, no real-world flags or heraldry.')
CLEAN = ' No text, no letters, no numerals, no logo, no interface elements, no watermark, no signature.'
PEOPLE = (' Any people are small and simple, with natural human proportions, each with exactly two arms and two legs; no close-ups and no faces in detail.')

AGE = ('This picture belongs to the age called "the present": the year a thousand and one of the age of the labyrinth, a magical and steam-powered age. '
       'Its look is the deep blue and gold of the labyrinth age with a new layer of polished brass and lamplight on top of it: gas lamps, brass fittings, '
       'printed paper, glass-roofed stations, and a train that runs on rails of pale shimmering alloy; a city that stays lit all night. ')

STYLE_PLATE = (" Drawing manner: the FIRST attached picture is the approved main plate of the labyrinth age and the SECOND is the approved style plate of the whole series; "
               "the new picture must look as if the same hand had painted it for the same book: large calm flat colour shapes layered like cut paper, "
               "thin lighter echo lines along the edges, soft inner gradients only, simplified forms with few details, big sweeping curves of smoke and cloud, "
               "a fine paper grain over everything. Colours: deep indigo, slate blue and soft lavender for the cool world; warm amber and brass gold only for the lamps, "
               "lit windows and polished brass. Huge things are drawn as layered pale silhouettes. Take only the drawing manner and the colours from the attached pictures, "
               "never their composition. No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D render.")

# 牌：照 bb_3 那一路的大幅牌面（gpt_front.py 的 BB2_COMMON、bb3、STYLE_BB2），这一张是正面朝上的牌，窗里是画、不是徽记
CARD = (
    "Draw one tall 2:3 portrait picture: the grand full-art face of a fortune-telling card from a luxury deck, seen perfectly flat from the front and filling the whole picture from edge to edge. "
    "The FIRST attached picture is the approved grand card of the labyrinth age from the same deck; this new card is its sister: the same arch-topped ornate window with a crest and a pendant, "
    "the same four round medallions, the same foil-like metallic lines and the same placement, but drawn in deep night blue with polished brass gold and a few more warm lamp lights. "
    "Composition: (1) In the upper middle stands a tall ornate window with an arched top, about three fifths of the picture wide; its top, crowned by a small crest, is at about 12 percent of the picture height, "
    "its foot is at about 64 percent, and the small pendant hanging from it ends above 72 percent. "
    "(2) Inside the window is a small calm scene drawn in flat cut-paper layers, like a stained-glass window: the great city at night around the mouth of a vast round well. "
    "At the bottom centre of the window the round mouth of the well opens, ringed by arcades, its depths dark blue with a faint warm glow far below. "
    "From the rim of the well rises one slender white lighthouse tower with a warm lamp burning at its top, the brightest point of the card. "
    "On the left side of the window the western city: black stone towers and straight streets with cold white-blue electric lights. "
    "On the right side of the window the eastern city: white stone domes, glass roofs and brass, with warm amber gas lamps. "
    "One thin curved railway viaduct sweeps across the middle of the window from side to side, with a tiny train on it whose windows glow. "
    "High in the window, above the far hills, a long thin stream of small dark beast silhouettes pours out of a distant forest and flows across the pale sky like a flight of birds: the first omen. "
    "(3) The crest on the arch: a row of ten small round bells hanging side by side, the first one on the left glowing warm, the other nine dark outlines. Pendant at the foot: a small round seal. "
    "(4) Four small round medallions around the window, two beside its arch and two beside its foot, each holding one plain silhouette: a brass gas lamp, a steam locomotive seen from the front, "
    "a compass rose, a small bell. "
    "(5) Outside the window the ground is deep blue and indigo covered edge to edge with fine tone-on-tone ornament in brass gold: thin concentric ripple arcs, a faint map grid, slender curling stems, "
    "small four-pointed stars and tiny beads; the ornament runs off all four edges with no outer border line. "
    "Everything below 74 percent of the picture height is darker and calm: only the faint ground pattern, with no scrolls, no medallions and no large stars, because a title will be printed there later. "
    "The frame of the window is bold and sculpted, with rich scrollwork at the crest, at the four medallions and at the foot. "
    "Drawing manner: the same hand as the attached cards: flat cut-paper colour shapes with thin lighter echo lines, soft inner gradients only, a fine paper grain, exquisitely ornate, intricate and jewel-like, "
    "crisp clean edges, metallic lines like foil stamped on matte paper. The second attached picture is the approved style plate of the series; the third is the main plate of the labyrinth age. "
    "No realistic lighting, no 3D. Only the window scene has people-free architecture; there are no people, no faces and no hands anywhere on the card."
)

MAIN = (
    "Draw one wide 3:2 landscape picture: the title plate of a storybook, the present day of a high fantasy world. " + AGE +
    "Scene: dusk turning to night over a vast city built around the mouth of an enormous round well that goes down into the earth. "
    "We look from a high place at the edge of the city across the whole of it. The round mouth of the well sits in the lower middle of the picture, wide as a lake, "
    "ringed by tier on tier of arcades and stairs going down, deep blue inside with a faint warm glow far below. "
    "Beside the well rises one slender white lighthouse tower, the tallest thing in the city, with a warm lamp burning at its top. "
    "Around the well the city spreads in rings of roofs, domes and bridges with thousands of small warm windows and gas lamps along the streets, like a field of embers. "
    "On the left, far away on the western side, black stone towers with cold white-blue electric lights; on the right, the eastern side, white stone domes, glass station roofs and brass. "
    "From the right a long high railway viaduct curves in on many arches toward the city, and a train with glowing windows runs on it, a thin plume of pale steam trailing behind in a long S-curve. "
    "Above, the sky is a calm deep blue going to indigo with a few stars and long layered cloud bands curling around the lighthouse lamp. "
    "Far away on the horizon at the left, above dark forested hills, a thin dark stream of tiny beast silhouettes pours out of the forest and sweeps along the sky like a flock: "
    "a small first omen that most of the picture does not notice. "
    "In the lower foreground, on a parapet at the edge of the roofs, three tiny travellers with packs and one small lantern stand looking at the city, seen from behind." + PEOPLE + NO_MOON
)

R1 = (
    "Draw one wide 3:2 landscape picture: one painted panel from a long series of storybook murals about the present day of a high fantasy world. " + AGE +
    "Scene: the lower city of the great well city in the evening. A crooked street of tall narrow stone and timber houses with iron balconies, lit by warm gas lamps and lit windows, "
    "runs down toward the round rim of the great well, which fills the right side of the picture as a vast dark round drop ringed by arcades, with a heavy iron lift-cage and its chains hanging over it from a brass gantry. "
    "On the left a tavern with a warm glowing doorway and a hanging lamp sign; small adventurers with packs, spears and staves come and go, a few look toward the lift. "
    "At the foot of the lift, on the stone steps of the rim, sits one small girl with long silver-white hair, wrapped in a grey blanket, alone, looking up at the sky; "
    "the passers-by walk past without stopping. Above, between the roofs, the slender white lighthouse tower of the city with its warm lamp, and a calm deep blue sky with cloud bands. "
    "Light: deep indigo and slate blue night, many small warm amber lamps and windows, the lift's brass glinting." + PEOPLE + NO_MOON +
    " Keep the girl small and simple, seen from the side, sitting; she is the only figure who is still."
)

R2 = (
    "Draw one wide 3:2 landscape picture: one painted panel from a long series of storybook murals about the present day of a high fantasy world. " + AGE +
    "Scene: before dawn on a wide plain of ripe wheat. A long train of brass and dark blue carriages with round lit windows runs from left to right along a high slender viaduct of pale stone arches "
    "that sweeps across the picture in one long gentle curve; its rails shine faintly pale silver. A long plume of pale steam rolls back from the engine in big layered S-curves over the wheat. "
    "Far ahead on the right, on the horizon, a great white city with domes and towers glows with warm lamps under the first pale light of dawn. "
    "On the left, at the edge of a dark forest on low hills, a herd of dark beast silhouettes, wolves and large horned beasts, streams out of the trees across the far fields toward the lit farms, "
    "small in the distance, the first sign that something is wrong. In the wheat near the viaduct a small farmstead with one lit window and a lantern on a post. "
    "Light: deep indigo night turning to pale blue at the horizon, warm amber only in the train's windows, the city lamps and the farm lantern." + PEOPLE + NO_MOON +
    " No people are visible except perhaps tiny silhouettes inside the lit train windows."
)

JOBS = {
    'card': (CARD + WEST + NO_MOON + CLEAN + ' Portrait picture, aspect ratio 2:3.', lambda: [png(os.path.join(SHELL, 'bb_3.webp'), 'bb_3.png'), T2, K4]),
    'main': (MAIN + STYLE_PLATE + WEST + CLEAN + ' Landscape picture, aspect ratio 3:2.', lambda: [K4, T2]),
    'r1': (R1 + STYLE_PLATE + WEST + CLEAN + ' Landscape picture, aspect ratio 3:2.', lambda: [K4, T2]),
    'r2': (R2 + STYLE_PLATE + WEST + CLEAN + ' Landscape picture, aspect ratio 3:2.', lambda: [K4, T2]),
}


def one(key):
    p, refs = JOBS[key]
    try:
        out = gen(os.path.join(OUT, key), p, refs=refs(), timeout=1500)
        print('好了', key, out, flush=True)
    except Exception as e:
        print('失败', key, str(e)[:300], flush=True)


if __name__ == '__main__':
    keys = [k for k in sys.argv[1:] if k in JOBS] or list(JOBS)
    os.makedirs(OUT, exist_ok=True)
    if os.environ.get('CG_DRY'):
        for k in keys:
            print('==', k, len(JOBS[k][0]))
            print(JOBS[k][0])
        sys.exit(0)
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(one, keys))
