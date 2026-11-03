#!/usr/bin/env python3
# 迷宫纪 1001 年那一套的零件（11-03）：七神、双王一人一张，烟、云、花、石、徽记一样一张，白底出，抠图另跑 cut_cpu.py。已有的不重出。
#   python maze1001_parts.py [名字前缀…]    只出名字以这些前缀开头的
# 长相照底卡 #86 到 #92，配色和服装参考 Elona Mobile 立绘，双王照用户 11-03 的两张图。画法要日式二次元（用户 11-03：别往西方动画跑）。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import kit

OUT = os.path.join(HERE, 'out', '四方_11-03', 'parts')
ST = ('official art, game cg, genshin impact, anime coloring, soft cel shading, delicate thin lineart, detailed face, beautiful detailed eyes, shiny hair, gradient hair, '
      'intricate fantasy costume, gold embroidery, ')
PLAIN = ' Plain white background. simple background, white background'
FIG = ' The figure faces left and looks to the left.'
# 名字：(提示词, 宽, 高, [种子…])
PARTS = {
    # ---- 七神：一人一个动作，都朝左，朝着对话
    'lulwy': (ST + '1girl, solo, goddess of wind, cowboy shot, from side, facing left, drawing a bow, aiming to the left, large white feathered wings spread, very long wild golden hair blowing in the wind, golden eyes, '
              'small golden circlet, white and gold flowing dress with sheer layers, gold armor pieces, white feathers floating. A wind goddess drawing a great golden bow, seen from the side, the arrow pointing left.' + PLAIN, 768, 1120, [21, 22]),
    'itzpalt': (ST + '1boy, solo, handsome noble man, cowboy shot, three quarter view, facing left, thrusting a golden sun staff forward to the left, upswept fiery red hair, red eyes, long crimson and cream robes with gold trim, '
                'one wing made of flames and one wing made of frost and ice mist, crackling lightning around the wings. A stern red-haired duke of the gods points his golden sun staff to the left.' + PLAIN, 768, 1120, [21, 22]),
    'opatos': (ST + '1boy, solo, huge muscular mature man, god of earth, cowboy shot, three quarter view, facing left, long black hair, red iron eyes, half of his body is cracked grey stone with glowing seams, bare chest, '
               'large hard wings of layered rock ridges like mountain ranges, both hands gripping a colossal stone war hammer. A colossal half-stone god looks to the left, calm and immovable.' + PLAIN, 768, 1120, [21, 22]),
    'ehekatl': (ST + '1girl, solo, goddess of luck, cowboy shot, three quarter view, facing left, smiling, one hand raised tossing a gold coin into the air to the left, long wavy blonde hair, blue eyes, white frilled dress with gold trim, '
                'small gold bells in her hair and on her sash, a small black cat sitting on her shoulder, scattered gold coins floating. A cheerful goddess flips a shining gold coin.' + PLAIN, 768, 1120, [21, 22]),
    'kumiromi': (ST + '1girl, solo, small petite goddess of harvest, full body, three quarter view, facing left, holding out a sheaf of golden wheat with both hands toward the left, short blonde hair, green eyes, small fawn antlers wrapped in vines and leaves, '
                 'green hooded robe with leaf patterns, halo of glowing seeds behind her head. A small gentle goddess offers a sheaf of wheat.' + PLAIN, 768, 1120, [21, 22]),
    'jure': (ST + '1girl, solo, goddess of healing, full body, kneeling, three quarter view, facing left, both hands cupped holding a glowing green light, long wavy green hair, jade green eyes, tiny white wings on the sides of her head, '
             'pink and white layered robes, falling white feathers. A small gentle healer kneels and offers a healing light.' + PLAIN, 768, 1120, [21, 22]),
    'yevan': (ST + '1boy, solo, slender man, cowboy shot, three quarter view, facing left, plain undyed long robe with a deep hood shadowing his eyes, faint gentle smile, long pale hair falling from the hood, one hand resting on the hilt of a sheathed sword at his hip. '
              'A polite and quietly dangerous traveler in a simple hooded robe, no ornaments.' + PLAIN, 768, 1120, [21, 22]),
    # ---- 第四轮：左扇伸过框线的巨手、旅人，楣两肩的西式飘带和金饰，索恩薇娅的发色照用户的图
    'hand': ('official art, game cg, anime coloring, no humans, a huge shadow hand with long clawed fingers reaching to the right, the hand is made of black and deep violet smoke, faint glowing violet veins, thin gold edge light, wisps of violet smoke trailing from the wrist on the left. Ominous and beautiful.' + PLAIN, 1120, 768, [61, 62, 63]),
    'navyribbon': ('official art, game cg, anime coloring, no humans, abstract swirling ribbons of deep navy blue and indigo smoke with thin glowing gold edge lines, big sweeping baroque curls and spirals, tendrils, stylized, ornamental.' + PLAIN, 1120, 768, [61, 62, 63]),
    'corner': ('official art, game ui ornament, no humans, an ornate golden baroque acanthus scroll, european filigree corner ornament, curling leaves, small stars and a gem, fine gold metalwork, elegant.' + PLAIN, 1120, 768, [61, 62]),
    'traveler': (ST + '1other, solo, a lone cloaked traveler seen from behind, full body, standing, hood up, long flowing cape blowing to the left, one arm raised holding up a staff with a small glowing light to the right, dark blue cloak with gold trim, faceless, back view.' + PLAIN, 768, 1120, [61, 62]),
    'sornb': (ST + '1girl, solo, mature young woman, queen, cowboy shot, three quarter view, facing left, raising a long sword high in her right hand, stern expression, dark brown hair with auburn tips, gradient hair, long side locks, large braided hair bun, small spiked gold crown, amber eyes, vertical scar over one eye, '
              'white high collar cape with gold trim and gold star patterns, white scarf, gold epaulettes with fringe, ornate gold breastplate with a star, black undersuit.' + PLAIN, 768, 1120, [22, 24, 25]),
    'baltc': (ST + '1girl, solo, mature young woman, queen, cowboy shot, three quarter view, facing left, one hand raised beside her head holding an ornate gold scepter upright, the whole scepter visible, cold expression, very long straight silver hair, blunt bangs, braid on the side of her head, large black hair bow, pointed ears, gold eyes, small red diamond mark on her forehead, '
              'crimson and black high collar long coat with gold trim and chains, black dress, gem brooches, long earrings.' + PLAIN, 768, 1120, [26, 27, 28, 29]),
    # ---- 第三轮：和紫烟同一路的深蓝奶金飘带、积云，楣和座的两肩用
    'ribbon': ('official art, game cg, anime coloring, no humans, abstract swirling ribbons of deep navy blue and pale cream gold cloud with thin glowing gold edge lines, big sweeping curls and spirals, stylized ornamental cloud scroll, small gold stars.' + PLAIN, 1120, 768, [51, 52, 53]),
    'cumulus': ('official art, game cg, anime coloring, no humans, a bank of billowing anime cumulus clouds, pale cream gold lit edges, soft indigo and violet shadows, painterly fantasy clouds, isolated clouds.' + PLAIN, 1120, 768, [51, 52, 53]),
    # ---- 第二轮：欧巴德斯要半身是人，艾赫卡托尔要成年人的样子（底卡一百六十五公分）
    'opatos2': (ST + '1boy, solo, tall muscular handsome man, god of earth, cowboy shot, three quarter view, facing left, long black hair, red eyes, handsome face with fair skin, half of his body is human, his other arm and shoulder and the side of his chest are cracked grey stone with glowing gold seams, open dark robe with gold trim hanging from his waist, '
                'large hard wings of layered rock ridges like mountain ranges spread behind him, one hand gripping a colossal stone war hammer. A calm immortal god, half flesh and half stone, looks to the left.' + PLAIN, 768, 1120, [21, 22, 23]),
    'ehekatl2': (ST + '1girl, solo, adult woman, mature female, tall, goddess of luck, cowboy shot, three quarter view, facing left, sly smile, one hand raised flipping a gold coin into the air to the left, very long wavy blonde hair, blue eyes, long elegant white gown with gold trim reaching the floor, wide sleeves, '
                 'small gold bells on her sash and hair ornament, a small black cat sitting on her shoulder, scattered gold coins floating. A beautiful smiling goddess flips a shining gold coin.' + PLAIN, 768, 1120, [21, 22, 23]),
    # ---- 双王：长相照用户的图
    'sorn': (ST + '1girl, solo, mature young woman, queen, cowboy shot, three quarter view, facing left, raising a long sword high in her right hand, stern expression, dark auburn hair, long side locks, large braided hair bun, small spiked gold crown, amber eyes, vertical scar over one eye, '
             'white high collar cape with gold trim and gold star patterns, white scarf, gold epaulettes with fringe, ornate gold breastplate with a star, black undersuit.' + PLAIN, 768, 1120, [21, 22, 23]),
    'balt': (ST + '1girl, solo, mature young woman, queen, cowboy shot, three quarter view, facing left, stretching out a gold scepter forward to the left, cold expression, very long straight silver hair, blunt bangs, braid on the side of her head, large black hair bow, pointed ears, gold eyes, small red diamond mark on her forehead, '
             'crimson and black high collar long coat with gold trim and chains, black dress, gem brooches, long earrings.' + PLAIN, 768, 1120, [21, 22, 23]),
    # ---- 盖在框边上的东西：烟、云、花、石
    'smoke': ('official art, game cg, anime coloring, no humans, abstract swirling ribbons of violet and indigo smoke with thin glowing gold edge lines, big sweeping curls and spirals, tendrils, dark purple shading, stylized, ornamental.' + PLAIN, 768, 1120, [31, 32, 33]),
    'cloud': ('official art, game cg, anime coloring, no humans, a large stylized swirling cloud bank, curling wave-like clouds in deep navy blue and pale cream gold with thin gold line art, ornamental spiral cloud pattern, east asian cloud scroll shapes, stars.' + PLAIN, 1120, 768, [31, 32, 33]),
    'flowers': ('official art, game cg, anime coloring, no humans, a lush cluster of white lilies, red spider lilies, golden wheat and green vines with leaves, gold glowing pollen, delicate line art, botanical ornament.' + PLAIN, 768, 1120, [31, 32]),
    'ledge': ('official art, game cg, anime coloring, a jagged floating rock ledge seen from the side, dark purple stone with gold cracks, and a lone small cloaked traveler standing on it seen from behind, long flowing cape, holding up a staff with a small light to the right.' + PLAIN, 1120, 768, [31, 32]),
    'crest': ('official art, game ui ornament, no humans, an ornate symmetrical golden crest, large eight pointed star in the center with thin radiating lines, art nouveau gold filigree scrolls curling out to both sides, small stars, fine metalwork, front view.' + PLAIN, 1120, 768, [31, 32]),
    'city': ('official art, game cg, anime coloring, no humans, a fantasy city of white towers with blue roofs and arched stone bridges on a cloud, small airships floating nearby, distant view, delicate line art, soft blue and cream colors.' + PLAIN, 1120, 768, [31, 32]),
}
# 整幅的背景：不抠
SCENES = {
    'bg_right': ('official art, game cg, anime coloring, scenery, no humans, a deep navy blue night sky full of stars, enormous thin golden halo rings and arcs, soft rays of golden light coming from the left, drifting clouds tinted indigo and cream gold, four pointed sparkles, floating glowing orbs. Fantasy game event illustration background.', 768, 1120, [41, 42]),
    'band_sky': ('official art, game cg, anime coloring, scenery, no humans, a deep navy blue night sky, fine gold constellation lines and thin gold arcs, small four pointed stars, faint indigo clouds at the edges. Dark ornamental fantasy game ui background, even tone.', 1120, 768, [41, 42]),
    'bg_lefb': ('official art, game cg, anime background, painterly, soft atmospheric perspective, volumetric light, fantasy scenery, no humans, a colossal labyrinth city of pale stone in concentric rings descending into a dark abyss, gothic spires, many arched stone bridges, a glowing gold spiral stairway winding down, indigo and violet shadows, luminous mist. '
                'High in the dark sky a black sun with a pale gold corona. A vast faceless shadow made of violet smoke looms over the city, with long tendrils and one huge dark hand reaching to the right. Highly detailed, ominous, beautiful.', 768, 1120, [44, 45, 46]),
    'bg_left': ('official art, game cg, anime coloring, fantasy scenery, no humans, a colossal labyrinth city in concentric rings descending into a dark well, gothic spires, arched stone bridges, a glowing gold spiral stairway winding down, indigo and violet shadows. High in the dark sky a black sun with a pale gold corona. '
                'A vast faceless shadow made of violet smoke rises behind the city with long tendrils. Highly detailed fantasy game background art, dramatic, ominous.', 768, 1120, [41, 42, 43]),
}

# 图边裁到的人补全：(新名字, 底图, 用谁的提示词, 追加的话)，种子 1。kit.extend 往左上续画
EXTENDS = [
    ('lulwyx_1', 'lulwy_21', 'lulwy', ' The whole golden bow and the whole arrow are visible, the arrow points left.'),
    ('itzpaltx_1', 'itzpalt_22', 'itzpalt', ' The whole golden sun staff and the whole flame wing are visible.'),
    ('kumiromix_1', 'kumiromi_22', 'kumiromi', ' The whole sheaf of wheat is visible.'),
    ('baltcx_1', 'baltc_26', 'baltc', ' The whole scepter is visible, her left sleeve is fully visible.'),
    ('sornx_1', 'sornb_22', 'sornb', ' Her raised arm in a black glove holds up the long sword, the whole crown is visible.'),
]
# 左扇的底，Turbo 那张再拿精修版画一遍（软一点，黑日也画实了）
REPAINT_PROMPT = ('official art, game cg, anime background, painterly, soft atmospheric perspective, volumetric light, fantasy scenery, no humans, a colossal labyrinth city of pale stone in concentric rings descending into a dark abyss, gothic spires, arched stone bridges, a glowing gold spiral stairway, indigo and violet shadows, luminous mist. '
                  'High in the dark sky a black sun with a pale gold corona. A vast faceless shadow made of violet smoke looms over the city with long tendrils and a huge clawed hand. Highly detailed, ominous, beautiful, soft shading, no thick outlines.')


def finish():
    tmp = os.path.join(OUT, 'tmp')
    for name, src, key, extra in EXTENDS:
        kit.extend(os.path.join(OUT, src + '.png'), os.path.join(OUT, name + '.png'), PARTS[key][0] + extra, seed=1, tmp=tmp)
    kit.extend_right(os.path.join(OUT, 'sornx_1.png'), os.path.join(OUT, 'sornz_1.png'), PARTS['sornb'][0] + ' Her white cape with gold trim falls fully visible on the right side.', seed=1, tmp=tmp)
    kit.gen(os.path.join(OUT, 'bg_lefa_a55.png'), REPAINT_PROMPT, 768, 1120, seed=9, model='aesthetic', init=os.path.join(OUT, 'bg_lefb_46.png'), denoise=0.55, steps=24)


def main():
    want = sys.argv[1:]
    done = []
    for name, (p, w, h, seeds) in list(PARTS.items()) + list(SCENES.items()):
        if want and not any(name.startswith(x) for x in want):
            continue
        for sd in seeds:
            src = os.path.join(OUT, '%s_%d.png' % (name, sd))
            kit.gen(src, p, w, h, seed=sd, model='turbo')
            done.append(name)
    if not want:
        finish()
    print('done', len(done))


if __name__ == '__main__':
    main()
