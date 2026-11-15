#!/usr/bin/env python3
# 主会话审场面稿时改的（11-15）。一处一条：(文件, 键, 旧串, 新串)，旧串在那一幅的 text 里必须正好出现一次。
#   python -I -X utf8 review_1115.py         套上（已经套过的跳过）
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

EDITS = [
    # 夜魇遮哪只眼，旅伴条和1001年的立绘对不上（底稿/立绘/待定.md），壁画上人很小，不点哪一只
    ('q3.json', 'q3_c', 'blue-black hair hiding her left eye', 'blue-black hair falling over one eye'),
    # 比法别用往后的东西
    ('q4.json', 'q4_i', 'thicker than a lift shaft', 'thicker than a tower'),
    # 角一律短而直，弯角、卷角衬着暗处也会画成月牙
    ('q5.json', 'q5_a', 'two horns sweeping back with an old bronze ring on the left one', 'two short horns angled back with an old bronze ring on the left one'),
    ('q5.json', 'q5_b', 'swept-back horns with a bronze ring on the left one', 'two short horns angled back with a bronze ring on the left one'),
    ('q5.json', 'q5_c', 'a towering bull-horned woman, horns wrapped in hemp rope,', 'a towering woman with two short thick horns wrapped in hemp rope'),
    ('q5.json', 'q5_e', 'short curled horns', 'two short straight horns'),
    # 灯影不晃就够了，写成水底下另一座城，模型会照字面画出一座倒过来的城
    ('q5.json', 'q5_g', ', like a second, upside-down city beneath the surface.', '.'),
    # 页一、页二和地开那一夜：角照旧收成短而直；边官泽菲写明是夜翼，好接上 FOLK 那一句
    ('q0.json', 'q0_a', 'a young tiefling woman with short swept-back horns', 'a young tiefling woman with two short straight horns'),
    ('q0.json', 'q0_a', 'Beyond the stones a winged man sits on a rock', 'Beyond the stones a night-wing man sits on a rock'),
    ('q1.json', 'q1_a', 'a young tiefling woman with short swept-back horns', 'a young tiefling woman with two short straight horns'),
    ('q1.json', 'q1_b', 'short swept-back horns, an old copper ring on one horn', 'two short horns angled back, an old copper ring on one horn'),
    ('q1.json', 'q1_d', 'A young tiefling woman with short swept-back horns', 'A young tiefling woman with two short straight horns'),
    ('q1.json', 'q1_e', 'a tiefling with dark horns curled back', 'a tiefling with two short dark horns'),
    ('q1.json', 'q1_f', 'glossy black horns curled back', 'two short glossy black horns'),
    ('q2.json', 'q2_c', 'two sideways-curving horns', 'two short horns'),
    # lantern 容易画成纸灯笼
    ('q6.json', 'q6_c', 'A lantern stands on the nearest slab.', 'A small iron-framed oil lamp stands on the nearest slab.'),
]

# 试画以后整段重写的（键：新的 text）。q3_a 头一稿把墙画到了她对面；q4_c 头一稿两个人都面朝帘子，原意是背守着帘子、她刚从帘子里出来
TEXTS = {
    'q3_a': ("Scene: midnight, seen from high on top of a colossal white stone wall, looking out over it. The wall's seven broad terraces step down and away "
             "from us across the whole bottom of the picture, seen from above and from behind, crowded with tiny defenders seen from the back as one dark mass, "
             "small torches being passed down from terrace to terrace. Beyond the foot of the wall lies a dark wheat field. Out in the field, just below the "
             "centre of the picture, one tiny woman stands alone with her back to us, facing away toward the enemy: tall, dark gold-brown hair tied low, "
             "a pale gold and bronze coat, a plain sword sheathed at her hip. The ground under her sinks in widening rings like a well spiralling down. "
             "Beyond her, a black tide pours from a long rift across the land and splits into two streams around her. Between her and the rift, seven columns "
             "of grey-red robed figures under tall banners, each banner with one simple dark mark, have halted facing her. Behind the rift, close together in "
             "the upper middle, rise three colossal pale shapes, taller than anything else: a hunched giant with five long straight tongs for hands and slack "
             "chains, its face a blank bronze plate; a tall figure shrouded in grey cloth, faceless; a gaunt giant with jutting ribs and a hollow pit for a "
             "belly, not a skeleton. Along the low eastern horizon behind them a band of dawn light flares."),
    'q4_c': ("Scene: deep underground, a vast dark hall of stone pillars receding into blackness, thin water flowing one way across its floor. We look straight "
             "at the end of a narrow side passage, filled from wall to wall by a curtain of fine grey rain that falls from nowhere and never wets the ground, "
             "a soft grey veil; nothing shows through it. In front of the veil, in the centre and slightly low, two figures face toward us with their backs "
             "to the rain. A sturdy rabbit-eared guide sits on a stone right before it: thick snow-white braid, long ears tipped with grey, the left one "
             "folded in the middle, a grey short coat, a palm-sized wooden board with seven notches in her hand. Beside her stands a tall pale woman who has "
             "just stepped out of the rain: long silver-grey hair loosely knotted at the nape and beaded with tiny grey droplets, a dark red long coat hung "
             "from her left shoulder only, a black dress, a long black glove on her right arm. In the lower left foreground a small travelling oven glows; "
             "a fire-horned baker in a floury apron, white cloth round one short horn's root, holds out two loaves toward the woman, one white, one dark. "
             "A few figures sleep in blankets by the oven."),
    # 头一稿把灰雨城那一道残响之门画进了长垒的门洞里，裂开的成了长垒。这一稿让那一道门单独立在黑潮里，长垒在后头完好
    'q5_d': ("Scene: night on a wide plain flooded with black tide, the tide lying flat on the ground like spilled ink. Far behind, across the whole horizon, "
             "runs a long white stone rampart; every banner along it glows softly as if lit from behind, and its own great gate stands whole and untouched. "
             "In the middle of the picture, alone in the black flood a few hundred paces in front of the rampart, stands a single old stone town gate with no "
             "wall around it, the ghost of a gate from a town that burned long ago: a stone gateway under a burning wooden lintel; inside its passage a row of "
             "small woven baskets and a tall pale figure at a little table, faces unclear. At the two ends of this gate's threshold, a gateway's width apart "
             "and not looking at each other, stand two women. Left: a woman with long silver-grey hair pinned loosely with a dark red ornament, dark red coat "
             "over one shoulder, black gown, bending to press a heavy seal onto the threshold stone with her bare right hand. Right: a tall woman with dark "
             "gold-brown hair tied low, copper chain mail and an old copper cloak, cutting a long sword low and flat along the ground. This old town gate "
             "cracks upward from its threshold and its burning lintel crumbles into grey ash falling like rain. From the threshold a straight path of pale "
             "gold light splits the black tide and runs toward the viewer, to rooftops in the foreground crowded with tiny people. The white rampart behind "
             "stays whole."),
}


def main():
    by_file = {}
    for f, k, a, b in EDITS:
        by_file.setdefault(f, []).append((k, a, b))
    for k in TEXTS:
        by_file.setdefault(k.split('_')[0] + '.json', [])
    for f, edits in by_file.items():
        p = os.path.join(HERE, f)
        d = json.load(open(p, encoding='utf-8-sig'))
        ms = {m['key']: m for m in d['murals']}
        n = 0
        for k, t in TEXTS.items():
            if k in ms and ms[k]['text'] != t:
                ms[k]['text'] = t
                n += 1
        for k, a, b in edits:
            t = ms[k]['text']
            if a not in t and b in t:
                continue
            if t.count(a) != 1:
                sys.exit('对不上：%s %s「%s」出现 %d 次' % (f, k, a, t.count(a)))
            ms[k]['text'] = t.replace(a, b)
            n += 1
        open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
        print(f, '改了', n, '处')


if __name__ == '__main__':
    main()
