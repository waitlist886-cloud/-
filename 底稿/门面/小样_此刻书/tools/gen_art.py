#!/usr/bin/env python3
# 此刻那一本（迷宫纪 1001 年，门面第五本书，11-24）要的图。画法照样张（底稿/门面/第二轮/样张_此刻/gen_art.py）、门面定稿样 t2、迷宫纪主画 k4。
# 原图出在 底稿/状态栏/comfy/out/门面_此刻/（不进库），prep_assets.py 转成书里的 webp。牌面、首屏主画、路上头两幅（r1 r2）照用样张那四张（out/门面第二轮/此刻/）。
#   CODEX_HOME=C:/Users/waitl/.codex_b <ComfyUI 的 python> 底稿/门面/小样_此刻书/tools/gen_art.py [键…]
#   键：r3 r4 r5 r6 map ticket lamp（不写就全出，出过的跳过）；CG_DRY=1 只打提示词
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
sys.path.insert(0, COMFY)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
from gpt_gen import gen  # noqa: E402

OUT = os.path.join(COMFY, 'out', '门面_此刻')
REFD = os.path.join(OUT, 'ref')
T2 = os.path.join(ROOT, '底稿', '门面', '画风定稿样_t2.png')
K4 = os.path.join(COMFY, 'out', '门面_主画_11-10', 'k4.png')
SAMPLE = os.path.join(ROOT, 'out', '门面第二轮', '此刻')
MAP_SRC = os.path.join(ROOT, '底稿', '地图', '样张', '迷宫纪_底图_1001_无字.jpg')


def map_ref():
    """旧底图补成 3:2（上下各补一条海），出来的图再照同样的比例裁回去，地标的百分数就还对得上。"""
    from PIL import Image
    os.makedirs(REFD, exist_ok=True)
    dst = os.path.join(REFD, 'map_old_32.png')
    if not os.path.exists(dst):
        im = Image.open(MAP_SRC).convert('RGB')
        w, h = im.size
        H = round(w * 2 / 3)
        pad = Image.new('RGB', (w, H), im.getpixel((w // 2, 6)))
        pad.paste(im, (0, (H - h) // 2))
        pad.resize((1536, 1024), Image.LANCZOS).save(dst)
    return dst


NO_MOON = ' There is no moon and no crescent anywhere in the picture.'
WEST = (' The world is Western high fantasy at the dawn of a magical industrial age, Victorian-era Europe in spirit: European masonry, arcades, domes, '
        'brass, wrought iron and glass. No East Asian motifs: no paper lanterns, no pagodas or upturned eaves, no auspicious clouds. '
        'No modern cars, no skyscrapers, no neon signs, no real-world flags or heraldry.')
CLEAN = ' No text, no letters, no numerals, no logo, no interface elements, no watermark, no signature.'
PEOPLE = (' Any people are small and simple, with natural human proportions, each with exactly two arms and two legs; no close-ups and no faces in detail.')
AGE = ('This picture belongs to the age called "the present": the year a thousand and one of the age of the labyrinth, a magical and steam-powered age. '
       'Its look is the deep blue and gold of the labyrinth age with a new layer of polished brass and lamplight on top of it: gas lamps, brass fittings, '
       'printed paper, glass-roofed stations, and a train that runs on rails of pale shimmering alloy. ')
STYLE_PLATE = (" Drawing manner: the FIRST attached picture is the approved main plate of the labyrinth age and the SECOND is the approved style plate of the whole series; "
               "the new picture must look as if the same hand had painted it for the same book: large calm flat colour shapes layered like cut paper, "
               "thin lighter echo lines along the edges, soft inner gradients only, simplified forms with few details, big sweeping curves of smoke and cloud, "
               "a fine paper grain over everything. Colours: deep indigo, slate blue and soft lavender for the cool world; warm amber and brass gold only for the lamps, "
               "lit windows, fire and polished brass. Huge things are drawn as layered pale silhouettes. Take only the drawing manner and the colours from the attached pictures, "
               "never their composition. No realistic lighting, no heavy painterly rendering, no photographic texture, no 3D render.")
MURAL = "Draw one wide 3:2 landscape picture: one painted panel from a long series of storybook murals about the present day of a high fantasy world. "

R3 = (MURAL + AGE +
      "Scene: the white imperial capital at the hour before dawn. A great white stone city of domes, bell towers and blue-and-gold banners rises on a river; "
      "above its highest palace spire a huge pale golden sun-crown, a ring of light like a crown of rays, hangs in the sky half eclipsed by a dark disc, the first rays bleeding out around its rim. "
      "In the foreground, on a long white stone bridge leading to the city gate, stands one lone armoured knight seen from behind, tall and very still, in old-fashioned plate armour "
      "of a fallen kingdom, a tattered pale cloak and a broken lance, facing the gate as if he is still guarding it; his armour is faintly translucent like mist, a ghost who does not know it. "
      "Behind him on the bridge, small and far, a long column of faint pale ghostly soldiers and banners of a kingdom that no longer exists. "
      "Along the river, warm gas lamps and lit windows of the living city. Light: deep indigo night going to a pale band of gold at the horizon." + PEOPLE + NO_MOON)
R4 = (MURAL + AGE +
      "Scene: deep in the primeval forest, an immeasurably vast world tree whose trunk is as wide as a castle and whose crown is lost in cloud, its roots forming arches and bridges. "
      "Elven tree-palace balconies of pale wood and woven branches cling to the trunk with small warm lamps. "
      "In a hollow between two great roots, inside a cradle of glowing pale green leaves and white flowers, a small figure of a sleeping princess lies curled, far away and tiny, "
      "while around her the leaves of the tree are slowly turning to pale grey and drifting down like snow, half the crown green and half the crown grey. "
      "Thin streams of floating motes of colour, red, blue, green and violet, drift through the air in disorder: the elements going astray. "
      "Light: deep blue-green dusk, soft lavender mist, warm amber only in the elven lamps and a faint gold glow around the cradle." + PEOPLE + NO_MOON +
      " The sleeping princess is tiny, seen from far away, simple shapes only.")
R5 = (MURAL + AGE +
      "Scene: a great snowy mountain range under a deep blue sky streaked with long pale clouds. High above the white peaks, a long migration of great dragons flies in one direction "
      "in a slow sweeping line, layered pale silhouettes, some huge and close, most small and far, their wings like sails. "
      "In the foreground on a snowy ledge, a giant frost-giant's fortress of blue ice and dark stone looms on the left; on the right, at the edge of a cliff, "
      "a small girl in a heavy fur cloak, seen from behind, holds in her arms one large egg that shines pale silver-blue, the brightest small thing in the picture, looking up at the dragons. "
      "Far below in a valley, a tiny railway station with warm lamps and a steam train." + PEOPLE + NO_MOON +
      " The girl is small and simple; the egg is the size of her torso.")
R6 = (MURAL + AGE +
      "Scene: night at sea outside a great harbour city. Calm dark water reflects many warm lamps of a harbour with brass lighthouses and moored sailing ships and steamships. "
      "In the middle of the sea, under the surface, glows a vast sunken kingdom: domes, towers and arcades of pale stone deep under the water, lit from inside with pale blue-green light, "
      "seen through the clear dark water like a reflection that should not be there. Above it on the surface, an old ghostly sailing warship with pale torn sails glides silently, "
      "its hull translucent. Faint pale rings of light ripple out over the water from the sunken city as if it were singing. "
      "Light: deep indigo night, warm amber harbour lamps, cool pale aquamarine glow from under the sea." + PEOPLE + NO_MOON +
      " No people visible except tiny silhouettes on the harbour quay.")

MAP = ("Draw one wide 3:2 landscape picture: the world map of one continent, painted as the endpaper map of a luxurious storybook. "
       "The FIRST attached picture is the geography that must be traced exactly: keep every coastline, island, bay, lake, river, the snowy northern ice field, "
       "the eastern forests, the southern desert sands, the dark round mark in the middle of the land and the thin vertical line of the long wall just west of it, "
       "all at exactly the same places, shapes and sizes, and keep the same frame, so that the new map can be laid over the old one; the strip of sea at the very top and bottom stays sea. "
       "Do not add, move or remove any land. Repaint it in the drawing manner of the SECOND attached picture (the style plate of the series) and the THIRD (the main plate of this age): "
       "large flat colour shapes layered like cut paper with thin lighter echo lines along every coastline and river, soft inner gradients, a fine paper grain. "
       "Colours: the sea is deep night indigo and navy with faint concentric ripple lines and a fine brass-gold grid of map lines; the land is soft slate blue, dusty lavender and pale grey-blue, "
       "the forests in layered deep teal shapes, mountains as small stacked pale paper silhouettes, the ice field pale silver-white, the desert pale warm sand-grey, "
       "lakes and rivers lighter blue with pale echo lines. The long wall is a thin line of brass gold. The dark round mark in the middle becomes a small round well-mouth with a faint warm amber glow inside and two thin brass rings around it. "
       "Brass-gold only for the wall, the well rings, a thin decorative compass rose in one corner of the sea and a thin double border line just inside the edge. "
       "Keep the land calm and quiet with few small details, because many labels and pins will be placed on it later." + CLEAN + ' No towns, no symbols, no icons on the land.')

TICKET = ("Draw one wide 3:2 landscape picture: a single ornate railway ticket stub from a magical steam age, seen flat from the front and filling most of the picture, on a plain deep navy blue background. "
          "The ticket is cream ivory printed paper with rounded corners, a perforated torn edge on the right side, a thin double border printed in deep blue, "
          "fine guilloche engraving patterns like on old banknotes, a small round brass-gold foil stamp of a lighthouse on the left, a tiny engraved steam locomotive in the middle band, "
          "and empty lines where the destination will be written later. It is a little worn and creased. "
          "Drawing manner of the attached style plates: flat cut-paper colour shapes, thin lighter echo lines, a fine paper grain, crisp clean edges." + CLEAN + ' The ticket itself carries no words and no numbers at all.')
LAMP = ("Draw one tall 2:3 portrait picture: a single ornate brass gas street lamp of a magical steam age, seen from the front, standing in the middle of a plain deep navy blue background, "
        "slender wrought-iron and brass post, a glass lantern head with a warm amber flame glowing inside, a small brass crest, a soft round halo of warm light around the glass. "
        "Drawing manner of the attached style plates: flat cut-paper colour shapes, thin lighter echo lines, a fine paper grain, crisp clean edges. Nothing else in the picture." + CLEAN)

JOBS = {
    'r3': (R3 + STYLE_PLATE + WEST + CLEAN + ' Landscape picture, aspect ratio 3:2.', lambda: [K4, T2]),
    'r4': (R4 + STYLE_PLATE + WEST + CLEAN + ' Landscape picture, aspect ratio 3:2.', lambda: [K4, T2]),
    'r5': (R5 + STYLE_PLATE + WEST + CLEAN + ' Landscape picture, aspect ratio 3:2.', lambda: [K4, T2]),
    'r6': (R6 + STYLE_PLATE + WEST + CLEAN + ' Landscape picture, aspect ratio 3:2.', lambda: [K4, T2]),
    'map': (MAP + NO_MOON + ' Landscape picture, aspect ratio 3:2.', lambda: [map_ref(), T2, K4]),
    'ticket': (TICKET + WEST + ' Landscape picture, aspect ratio 3:2.', lambda: [T2, K4]),
    'lamp': (LAMP + WEST + ' Portrait picture, aspect ratio 2:3.', lambda: [T2, K4]),
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
