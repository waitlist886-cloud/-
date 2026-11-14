#!/usr/bin/env python3
# 11-12 主会话审稿以后落进各份 scenes/mNN.json 的改动。只跑一回（跑过的再跑会停在 assert 上），留着当记录。
#   python -I -X utf8 review_1112.py
# 做了什么：
# 一、死期和死的那一刻只留“死在这段剧情里”的（照第七歌的口径）：主线各幕到收束里死的、下落不明的；外加主线的结尾和歌里明着唱到的横死（阿尔凯、戈尔）。
#     几十年以后老死、病死的不算，页上的档案里“没有你的那一版”本来就有下场的全文。挪出来的稿子留在 later_fates、later_deaths，往后要用再拿。
# 二、玩家看得见的名字改了二十来个：口语的半句、引的一句话、跟别的时代重了的。
# 三、几幅场面改了字（见各条）。四、画里有孩子的补 young，立绘是别纪那一套的补 differs。
import glob
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

# 留下的死期（别的挪进 later_fates）
KEEP_FATE = {
    'm01': ['海拉斯', '妮欧贝', '看火的老人'], 'm02': ['埃纳尔', '沃尔夫里克', '白礁国的老王'], 'm03': ['埃蒙'],
    'm04': ['希波拉', '阿尔凯'], 'm05': ['芬尼', '戈尔'], 'm06': ['艾丹'], 'm08': ['赫罗斯'], 'm10': ['卡娅'],
    'm12': ['德米安', '珠湾王', '三夜来援的人'], 'm14': ['墨勒'], 'm16': ['奥瑞克'], 'm17': ['贾罗', '铜谷的王'],
    'm20': ['雷米', '柯黛'], 'm22': ['哈德温', '海德薇', '莉瑟', '埃利奥'], 'm23': ['阿德里安', '希奥'],
    'm25': ['薇丝拉', '尤里安'], 'm26': ['塔尔森', '玛姬', '茵瑞尔', '七人原的第七个人'], 'm27': ['贝洛尼卡'],
}
# 留下的死的那一刻（别的挪进 later_deaths）
KEEP_DEATH = ['m01_d_hellas', 'm01_d_niobe', 'm02_d_einar', 'm03_d_emon', 'm04_d_hipola', 'm04_d_arke', 'm06_d_aidan', 'm10_d_kaya',
              'm12_d_damian', 'm14_d_mele', 'm17_d_jaro', 'm22_d_hedwig', 'm23_d_adrian', 'm23_d_theo', 'm25_d_vesla', 'm25_d_julian', 'm26_d_inriel']
RENAME = {
    'm03_n2': ('无脚印', '雪上无痕'), 'm05_n4': ('让座', '火边一席'), 'm08_n2': ('一条胳膊', '一夜之握'), 'm09_n1': ('偏了一寸', '一寸之偏'),
    'm10_n1': ('趴下', '一声趴下'), 'm12_n2': ('憋住的潮', '屏住的潮'), 'm13_n4': ('灯还亮着', '未熄的灯'), 'm14_n3': ('白火', '獠牙之间'),
    'm16_a3': ('刷不掉', '愈洗愈亮'), 'm16_b2': ('你的刀呢', '赤手'), 'm16_c1': ('烛火晃了', '烛火一晃'), 'm17_a4': ('落在谷口', '谷口落鳞'),
    'm17_d1': ('一一二号', '炉口之盾'), 'm18_a3': ('车底下', '车底的脚'), 'm18_a4': ('两个印', '挨着的印'), 'm18_c2': ('别回头', '头顶一箭'),
    'm20_b3': ('很白', '北岸归人'), 'm21_a3': ('山在走', '负山而行'), 'm21_a4': ('弯腰', '草山羊'), 'm23_a4': ('回去吧', '狼皮里子'),
    'm24_a2': ('硬的', '小角'),
}
# 立绘资料是别的样子、场面里另写了样子的（年纪、衣着、冠）
DIFFERS = ['m11_n3', 'm24_a2', 'm24_a4']
YOUNG_RX = re.compile(r'\b(child\w*|kid\w*|baby|babies|infant\w*|toddler\w*|little (?:girl|boy|sister|brother)|small (?:girl|boy)|(?:six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen)[- ]year|(?:girl|boy|son|daughter|lad) of (?:about )?(?:six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen)\b)', re.I)

EMON = ("Scene: the shallow ford of a wide northern river on the grey morning after the winter broke, seen from the far bank. In the near foreground, large, dark and cut off by the lower edge of the frame, "
        "stand the backs of a long line of beasts at the water's edge: ice-maned wolves, bears with frost on their fur, great hawks with folded wings. Their heads are low and they are all looking across the water, "
        "and not one of them has set a paw in the river. Across the ford, in the middle of the picture and small against everything behind it, a tall upright blue-grey standing stone rises out of the shallows, "
        "and a lean youth stands against it on his feet, held upright by a belt of plaited leather wound twice round his waist and knotted behind the stone. He is far away and seen from the front: "
        "a frost-grey wolf pelt hangs from his shoulders down to his knees and covers his body, his head is high, his wild hair, black at the roots and gold at the tips, blows sideways, his face is turned toward the beasts, pale, calm and still. "
        "No wound and no blood can be seen on him from here. A single black crow is just landing on his shoulder, its wings still half open. "
        "Behind him, filling the whole middle distance and cut off by both edges of the frame, lies the immense blue-grey body of a fallen snow mammoth across the broken ice of the river, like a hill that has come down in the night; "
        "the river ice round it is split and heaped, and melt water runs dark between the slabs. On the bank behind the stone, tiny, a band of northern warriors in furs has just come running out of the birches and stopped. "
        "A grey dawn sky is clearing above, with a last band of stars. Blown snow and bits of ice drift large and out of focus across the near corners.")

NIGHT = {
    'key': 'm27_n4a', 'line': '末年·登神术前夜', 'act': '收束', 'name': '落塔', 'extra': True, 'first': True,
    'style': ['himeko_card', 'fire'],
    'who': [['z1_tobias', 'casual', 'the baker'], ['sa6_felix', 'casual', 'the young tower apprentice']],
    'light': 'the blinding cold white of a great lamp breaking apart high above and already dying, against one warm orange wedge of oven light at the lower right',
    'camera': 'very low on the cobbles, looking steeply up the narrow street at the falling tower; strongly tilted',
    'text': ("Scene: deep night in a narrow cobbled street of the lower city of a vast basin capital, at the instant the lights of an empire go out. We look up the street from low on the ground. "
             "Above the roofs, filling the upper half of the picture and cut off by the top of the frame, an immense slim tower of pale stone that has hung in the sky over this street for thousands of years is coming down at a slant, "
             "toppling slowly like a felled tree: the great lamp of cold white light at its head has just flared to a blinding white and is now breaking apart into shards and long streamers of dying light; "
             "blocks of pale stone are coming away from its shaft and falling ahead of it, and its shadow is rushing down the street. All along the street the small cold-white street lamps are bursting and going dark one after another. "
             "Far behind, between the roofs, more slim towers lean and fall across the basin city like a forest going down, and high above them a whole floating upper city of white terraces is sinking, very slowly, toward a ring of black mountains. "
             "In the lower right, at the open door of a bakery, is the only warm light in the picture: an oven door stands wide open and its orange firelight spills out across the cobbles in a long wedge. "
             "In that doorway the baker, a huge, wide, round-bellied man of thirty-eight with close-shaved ginger hair, a ruddy face and scorched forearms, has seized a thin young man of twenty by the arm and the shoulder "
             "and is hauling him bodily off the street and in through the door. The young man, with honey-coloured curly hair and one ink-stained lock, in a long pale grey-white cloak that is too big for him, "
             "is still twisted round with his face lifted, staring up at the falling tower. Behind them in the street a dozen people are running toward the firelight, among them a woman carrying a child. "
             "The wind of the fall blows every rag, shutter and awning in the street out straight. Stone dust, sparks of cold white light and torn cloth fly large and out of focus across the near corners."),
    'note': '主会话添的：收束头几拍（源稿第308到310行），永光猛地一亮，头一座辉塔斜着砸在初光街上，托比亚斯把费利克斯拽进面包房，炉门开着。灯里那一句不写成字。客星城在神渡，这里看不见，不画。排在炉边面包前头。',
}


def main():
    done = 0
    for p in sorted(glob.glob(os.path.join(HERE, 'm??.json'))):
        eid = os.path.basename(p)[:-5]
        d = json.load(open(p, encoding='utf-8'))
        assert 'later_fates' not in d and 'later_deaths' not in d, eid + ' 已经审过了'
        scenes = {s['key']: s for s in d.get('nodes', []) + d.get('deaths', [])}
        # 一、死期和死的那一刻
        keep = KEEP_FATE.get(eid, [])
        fates = d.get('fates') or {}
        for n in keep:
            assert n in fates, (eid, n)
        d['later_fates'] = {n: f for n, f in fates.items() if n not in keep}
        d['fates'] = {n: f for n, f in fates.items() if n in keep}
        d['later_deaths'] = [s for s in d.get('deaths', []) if s['key'] not in KEEP_DEATH]
        d['deaths'] = [s for s in d.get('deaths', []) if s['key'] in KEEP_DEATH]
        # 二、名字
        for k, (a, b) in RENAME.items():
            if k.startswith(eid):
                assert scenes[k]['name'] == a, (k, scenes[k]['name'])
                scenes[k]['name'] = b
        # 三、几幅的字
        if eid == 'm03':      # 埃蒙：立绘资料是十七岁那一档，不画牙和血。改成从对岸兽群背后望过去，远处青石上站着的人，披着狼皮，乌鸦落在肩上
            s = scenes['m03_d_emon']
            s['text'] = EMON
            s.pop('raw', None)
            s['young'] = True
            s['camera'] = 'from the far bank, low behind the line of beasts and between their shoulders, looking across the water at the standing stone; a little tilted'
            s['light'] = 'a cold grey-blue dawn from behind the fallen mammoth, a thin pale rim of light on the stone, on the wolf pelt and on the edges of the ice'
            s['note'] = '主会话改：源稿他十八岁、立绘资料按十七岁那一档画的，不画腰上的牙和血。从对岸兽群背后望过去，他是远处青石上站着的小人，身上披着狼皮，乌鸦落在肩上（歌名鸦栖之石）。'
        if eid == 'm06':      # 艾丹：角尖从身前穿出来那一句太直白，改成角从身后挑中了他，尖叫他身子挡着
            s = scenes['m06_d_aidan']
            a = "The tip of the horn, from behind, has run right through his side below the ribs and stands out of his jerkin on the near side, black with the beast's blood and his own red blood spreading down his leather;"
            assert s['text'].count(a) == 1
            s['text'] = s['text'].replace(a, "The beast's horn, swinging up as it fell, has caught him under the ribs from behind: its tip is hidden by his body, and where it met him his leather jerkin is torn and dark, red blood spreading down his side and over his belt;")
        if eid == 'm15':      # 老欧德：换成纷争纪那一套的立绘（凝名以后一直是六十五岁的样子），不拿十五岁那一张当参考
            n = 0
            for s in scenes.values():
                for w in s.get('who', []):
                    if w[0] == 'ge14_ode':
                        w[0], w[1] = 'z6b_ode', 'casual'
                        n += 1
            assert n == 3, n
        if eid == 'm23':      # 金盾：那张参考画的是军团的环和天上的巨影，不是兽，拿掉
            assert scenes['m23_d_adrian'].pop('beast') == 'moon_039_2'
        if eid == 'm24':      # 无眠者：橙冰是冰，照史诗战认过的设计是冰蓝的鳞嵌着银，冰里一点橙光
            for k, f, a, b in (
                    ('m24_b2', 'text', 'orange-scaled', 'ice-blue-scaled, with a faint orange light deep inside the ice'),
                    ('m24_b4', 'text', 'orange-scaled', 'ice-blue-scaled, with a faint orange light deep inside the ice'),
                    ('m24_b3', 'text', 'orange scales studded with plates of silver', 'ice-blue scales with a faint orange light deep inside them, studded with plates of silver'),
                    ('m24_b2', 'light', 'with orange-amber glints from the ice ridge as it breaks', 'with faint orange glints deep inside the blue ice of the ridge as it breaks'),
                    ('m24_b4', 'light', "with orange glints from the dragon's scales", "with faint orange glints deep inside the dragon's ice-blue scales")):
                assert scenes[k][f].count(a) == 1, (k, f)
                scenes[k][f] = scenes[k][f].replace(a, b)
        if eid == 'm26':      # 第七个人是死了、埋了的，只是没有人知道他是谁，不算下落不明
            assert d['fates']['七人原的第七个人'].pop('label') == '下落不明'
        if eid == 'm16':      # 奥瑞克进藤缝那一拍就是一幕那一幅（火盂），他的档案里挂同一幅
            d['deaths'].append({'key': 'm16_d_orik', 'death': '奥瑞克', 'name': '火盂', 'same': 'm16_d1', 'age': 21})
        if eid == 'm27':
            s = scenes['m27_n4']      # 天亮以后塔已经倒了、灯都灭了，环印也不亮了
            a = "In the far background, over the broken roofs, a gigantic cold-white spire leans over at a steep slant into the sky, and across the street surface faint lines of pale gold light still run along the paving in great curves."
            assert s['text'].count(a) == 1
            s['text'] = s['text'].replace(a, "In the far background, across the broken roofs, the shaft of a gigantic fallen tower of pale stone lies slanting over the street like a toppled column, its great lamp dark, pale dust still rising from it.")
            d['nodes'].append(NIGHT)
            scenes[NIGHT['key']] = NIGHT
        # 四、标记
        n = int(eid[1:])
        pre = 'ge%d_' % n if n <= 15 else ('zg%d_' % (n - 15) if n <= 21 else 'sa%d_' % (n - 21))
        for s in d['nodes'] + d['deaths']:
            if s.get('same'):
                continue
            if YOUNG_RX.search(s['text']):
                s['young'] = True
            if s['key'] in DIFFERS or any(not w[0].startswith(pre) for w in (s.get('who') or s.get('row') or [])):
                s['differs'] = True
        open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(d, ensure_ascii=False, indent=1) + '\n')
        done += 1
        print(eid, '死期', len(d['fates']), '（挪出', len(d['later_fates']), '）死的那一刻', len(d['deaths']), '（挪出', len(d['later_deaths']), '）')
    print('改了', done, '份')


if __name__ == '__main__':
    main()
