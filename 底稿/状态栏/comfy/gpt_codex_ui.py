#!/usr/bin/env python3
# 世界之书那一套界面图（11-15，介绍页收尾）：四本书右上角的入口一纪一枚，加一本合着的世界之书。
#   python gpt_codex_ui.py [键…]      不写键就全出；出过的跳过。图写 out/门面_世界之书/<键>.png
# 用户 11-15：“需要什么美术资源你可以自行用codex跑”。走 gpt_gen.gen（ChatGPT Pro 的出图额度）。
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gpt_gen import gen

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', '门面_世界之书')
COMMON = ("Draw one square picture on a fully transparent background: a single ornate game menu icon, painted with rich detail and soft rim light, "
          "centered and filling about eighty percent of the canvas. Western high fantasy, polished like the menu icons of a modern Japanese fantasy RPG. "
          "No text, no letters, no numbers, no runes that look like writing. No crescent shapes and no moons anywhere. "
          "Crisp clean outline against the transparent background: no shadow on the background, no glow, no haze, no backdrop, nothing else on the canvas. ")
JOBS = {
    'emblem_moon': "An ancient weathered stone tablet with a rounded top, pale silver grey stone with dark green moss in the cracks and chipped edges, "
                   "a small campfire carved into its face that glows warm amber as if a real ember lives in the carving, a thin line of tarnished silver inlaid round the edge. "
                   "The tablet stands slightly tilted, seen from the front.",
    'emblem_strife': "A thick military register bound in battered dark leather with tarnished bronze corner plates and a leather strap with a buckle, "
                     "an emblem of two crossed swords over a broken laurel wreath embossed in bronze on the cover, the page edges stained and uneven, a dark red ribbon marker hanging out. "
                     "Seen from the front, slightly turned.",
    'emblem_bronze': "A sheet of heavy paper taken as a charcoal rubbing from a carved monument, showing a straight sword standing upright inside a laurel wreath in dark grey relief, "
                     "the paper slightly curled at the corners and pinned at the top with two small bronze pins, a faint white stone dust on it.",
    'emblem_maze': "A small guild notice slip of yellowed parchment with one torn corner, a red wax seal at the bottom, a short knotted rope threaded through a hole at the top, "
                   "an ink stamp of a compass rose with a small eight pointed star in its centre.",
    'wb_cover': "A closed ancient tome lying slightly turned, deep midnight blue leather cover with fine gold filigree along the edges and gold clasps, "
                "a round gold emblem in the centre of the cover showing a small candle flame inside a ring of tiny stars, the page edges gilded, a dark red ribbon marker. ",
}


def main():
    os.makedirs(OUT, exist_ok=True)
    keys = sys.argv[1:] or list(JOBS)
    for k in keys:
        stem = os.path.join(OUT, k)
        if os.path.exists(stem + '.png'):
            print('有了', k)
            continue
        print('出', k, flush=True)
        print(gen(stem, COMMON + JOBS[k]))


if __name__ == '__main__':
    main()
