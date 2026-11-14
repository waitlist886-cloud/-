#!/usr/bin/env python3
# 看了头一轮出的图以后改的场面（只跑一回，改过的那一条记 rev2，再跑会停）。改完把旧图改名留着，再出那几幅：
#   python -I -X utf8 review_legends2.py
#   瓦尔克斯「背扛」：头一稿把“祂跪着一膝、断了左角”那几句画成了远处的第二个巨人，剩的那只角贴着天像一弯月牙；人是拿手托的拳，不是拿背扛；
#   拳底下画了孩子。改成：画里只有一只拳和一截腕，不挂祂的参考图，写明没有别的巨人；拳落在他弓起的背和肩上；拳底下的人都是大人。
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def patch(g, key, fn):
    p = os.path.join(HERE, g + '.json')
    d = json.load(io.open(p, encoding='utf-8'))
    f = [x for x in d['falls'] if x['key'] == key]
    assert len(f) == 1 and not f[0].get('rev2'), key
    fn(f[0])
    f[0]['rev2'] = True
    with io.open(p, 'w', encoding='utf-8', newline='\n') as h:
        json.dump(d, h, ensure_ascii=False, indent=1)
        h.write('\n')
    print('改了', key)


def valkes(f):
    f.pop('beast', None)
    f['camera'] = 'low from behind him at three-quarter, looking up past his bowed back at the underside of the fist, strong foreshortening'
    f['text'] = ("Scene: just past noon on the south bank of a wide river, pale grey dust in the air, rubble underfoot. "
                 "A boulder-like fist of grey-brown quarry stone, as large as a house, its edges dissolving into drifting grey dust, comes down from above and fills the entire top third of the frame; "
                 "only the underside of the fist and a part of the wrist are visible, the wrist rising out of the top edge of the picture. It is the fist of a hill-tall stone giant whose body is entirely outside the frame: "
                 "no other part of the giant is shown anywhere, there is no second figure, no head and no horn in the distance, and the far background is only the river plain, a low stone bridge, dust and a pale hazy sky. "
                 "Directly beneath the fist, seen from behind at three-quarter, the half-orc Valkes has turned his back to it and bowed under it with his knees bent: about two metres twenty, grey-green skin, short dark hair, shoulders as wide as half a gate, a heavy dark leather coat. "
                 "The stone has landed across his bent back and broad shoulders and he carries its whole weight there, his head lowered between his shoulders; he does not catch it with his hands, his arms are spread low to both sides to shelter the people in front of him. "
                 "The crushed gravel at his feet has sunk in to his knees and the ground cracks outward in rings. A broken iron door bar longer than a man stands planted upright in the rubble beside him. "
                 "He looks sideways over his shoulder toward the people with his mouth open as if asking them something; one of his lower tusks is a broken stub. "
                 "In the pocket of shadow under the fist, close around his legs, five or six people stand huddled and still on their feet with their faces upturned: soldiers in iron helmets and grown-up refugees, all of them adults. "
                 "Chips of stone and dust fall large and out of focus across the foreground corners.")
    f['note'] = f.get('note', '') + '（主会话第二回：只画拳和腕，不挂祂的参考图，写明远处没有别的巨人；拳落在背上；拳底下都是大人。）'


patch('gF', 's17_f_valkes', valkes)
