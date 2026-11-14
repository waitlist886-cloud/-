#!/usr/bin/env python3
# 主会话审七组传奇稿以后的改动。只跑一回：改过的文件顶上记 "reviewed"，再跑会停。
#   python -I -X utf8 review_legends.py
# 改了什么、为什么：
#   近况（at）里拿“月银纪留下来的老传奇里，这些年走了几位，她不在其中”这一类话凑数的，换成他这些年照旧在做的那一件事。
#   席恩头六张写“不出墙”，那时候墙还没有；欧德第十四张的年份照北归道收束是4601年；狄昂第十二张末一句是陨落那一下，留给陨落那一栏。
#   法隆的经过不写是谁动的手（长垒这一边不知道），只写死在自己人手里。
#   场面：茨维娅照经过改成坐着；费利克斯那一道环原写成天上一张发光的圆盘，会画成月亮，改成贴着头盔的一条平光；诺伦的盔写明整个头罩在盔里、金鬃是盔上的；
#   罗特鲁德照页上凝名以后的样子（看上去五十上下、辫子白了几缕）画，立绘是她十七岁那一套，所以加 differs；库米罗妮不写 young-looking；
#   里纳尔多的日纹照立绘那一轮定的写成褐布上金色轮形的纹，炉门不写成一张发光的圆；雅克写成还睁着眼看那支军绕路；席恩抵眉心写明不留痕。
#   辛美尔两句台词换成第七页里核得到的两句；没有句末标点的台词补上。
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load(g):
    return json.load(io.open(os.path.join(HERE, g + '.json'), encoding='utf-8'))


def save(g, d):
    d['reviewed'] = True
    with io.open(os.path.join(HERE, g + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write('\n')


def at(d, name, cards, new, has=None, sub=None):
    """换一段近况。has 是旧文里必有的一截（防改错段）；给 sub=(旧, 新) 时只换那一截。"""
    segs = [s for s in d['legends'][name]['at'] if s['cards'] == list(cards)]
    assert len(segs) == 1, (name, cards)
    s = segs[0]
    if has:
        assert has in s['text'], (name, cards, s['text'])
    if sub:
        assert s['text'].count(sub[0]) == 1, (name, cards, sub[0])
        s['text'] = s['text'].replace(sub[0], sub[1])
    else:
        s['text'] = new


def fall(d, key):
    fs = [f for f in d['falls'] if f['key'] == key]
    assert len(fs) == 1, key
    return fs[0]


def rep(f, field, old, new):
    assert f[field].count(old) == 1, (f['key'], field, old)
    f[field] = f[field].replace(old, new)


def quotes(d):
    for x in d['legends'].values():
        if x.get('quotes'):
            x['quotes'] = [q if q[-1] in '。？”' else q + '。' for q in x['quotes']]


G = {g: load(g) for g in ('gA', 'gB', 'gC', 'gD', 'gE', 'gF', 'gH')}
for g, d in G.items():
    assert not d.get('reviewed'), g + ' 已经改过了'

# ---------- gA ----------
d = G['gA']
at(d, '希尔妲', (11, 18), '她照旧顺着墙从北走到南，又从南走到北。南段哪一座烽火凉了，守塔的人就托人去请她，她到了，从罐子里拨一点火种出来，再点一回。', has='这些年走了几位')
at(d, '希尔妲', (19, 20), '长垒上挂起了号角。她还背着那一罐火种顺着墙走，哪里的火要灭，她往哪里去，每一堆火边只待一夜。', has='还在世的有四位')
at(d, '霍布', (11, 11), '他照旧在赤原边上种麦。对炉街上的人吃的面包，是用他的麦磨的。', has='1050到1500年')
at(d, '霍布', (13, 13), '他照旧在赤原边上和墙后头两头走，种麦。他盖的那几座粮仓还在墙后头，仓门上照旧没有刻字。', has='这些年又走了几位')
at(d, '霍布', (15, 17), '5951年那一冬以后，他照旧在赤原边上和南段墙后种麦，他走过的地方麦子长得好。他睡着的时候多，叫不醒，到割麦那天自己醒。', has='走了的几位没有他')
at(d, '霍布', (19, 21), '他照旧在赤原边上和墙后头两头走，种麦，在垄头上睡。赤原边的麦一年熟一回，收成还是别处的一半。', has='还在世的有四位')
f = fall(d, 's07_f_zvia')
rep(f, 'text', 'stands Zvia, a thin tall night-demon woman who looks sixty, about 166 cm, her back as straight as a spear planted in snow,',
    'Zvia sits on the bare ground with her legs folded under her, a thin tall night-demon woman who looks sixty, her back as straight as a spear planted in snow,')
rep(f, 'text', 'In one hand she holds a plain white wooden staff planted in the dirt,', 'One hand rests on a plain white wooden staff planted upright in the dirt beside her,')
rep(f, 'text', 'She stands at the feet of a short, wide dwarf', 'She sits at the very feet of a short, wide dwarf')
f['note'] = f.get('note', '') + '（主会话：照经过改成坐着。）'

# ---------- gB ----------
d = G['gB']
at(d, '瑞恩·无名', (8, 8), None, sub=('谁也没有告诉任何人', '走以前没有告诉任何人'))
at(d, '古尔巴', (1, 6), '他不替哪一国打仗。早年各国的王派使节来请他，他问要顶多久，使节答不上来，他没有去。腰上那只草兜里，装着给孩子编的草山羊。', has='月银纪5850年')
d['legends']['古尔巴']['quotes'] = ['要顶多久？']
f = fall(d, 's08_f_faron')
rep(f, 'how', '当夜他死在自己人手里，动手的是他营里血誓祭司带来的人。', '当夜他死在自己人手里，为的就是那一句我不打了。')
f = fall(d, 's10_f_felix')
rep(f, 'text', 'as tall as a tower stands with his back to us', 'as tall as a tower is sinking to his knees with his back to us')
rep(f, 'text', 'a huge round shield held up in front of him', 'a huge round shield still held up in front of him')
rep(f, 'text', 'A wide flat disc of pale silver-white light hangs above and behind him over the whole group to his left, and the blood rain strikes it and runs off its edge in glowing sheets.',
    'A low, wide canopy of pale silver-white light, flat as a table top and seen almost edge-on so that it reads as one long straight band of light just above the helmets, hangs above and behind him over the whole group to his left, faint ring-lines running through it, and the red rain strikes it and runs off its edge in glowing sheets.')
rep(f, 'text', 'outside the edge of the disc', 'outside the edge of the canopy')
f['raw'] = True          # 神血那一场红雨要画出来；不带这一项，总说里会写“不画血”
f['note'] = f.get('note', '') + '（主会话：环不写成天上一张发光的圆盘，改成贴着头盔的一条平光；举盾者写成正在跪下去。）'

# ---------- gC ----------
d = G['gC']
at(d, '狄昂', (12, 12), '正神一位一位往南去的那些年，他背着铜盾跟在后头过了几回南界，又一个人回来。有人问他跟着谁，他不回头。', has='2104年莉薇兰南去')
f = fall(d, 's12_f_nolen')
rep(f, 'text', 'with the visor down and a great mane of pale gold spilling over the shoulders, a thin line of green light in the visor slit,',
    "with the visor down, a crest of pale gold horsehair fixed to the helm and spilling over the shoulders (the crest is part of the helm, not hair), a thin line of green light in the visor slit, the whole head enclosed in the helm so that no face, no skin and no hair of the wearer can be seen,")

# ---------- gD ----------
d = G['gD']
f = fall(d, 's16_f_rotrude')
rep(f, 'text', 'a tall slender young woman stands seen from behind at three-quarter, about 168 cm, long cherry-pink hair in one braid pinned at the end with a single dried rose,',
    'a tall spare woman who looks about fifty stands seen from behind at three-quarter, about 168 cm: she is the swordswoman of the reference sheet many decades later, the same face grown older with fine lines at the eyes, her long cherry-pink hair streaked with white and worn in one braid pinned at the end with a single dried rose,')
f['differs'] = True
f['note'] = f.get('note', '') + '（主会话：照凡世至强那一条画，凝名那年六十八岁、看上去五十上下、辫子白了几缕；立绘是她十七岁那一套，加 differs。画面照旧不画伤。）'
f = fall(d, 's15_f_sekody')
rep(f, 'text', 'stands a small young-looking harvest goddess', 'stands a small slight harvest goddess')
f = fall(d, 's16_f_io')
rep(f, 'text', 'a vast round iron furnace door glowing white-orange in the middle of the picture',
    'a vast riveted iron furnace door, taller than a man, glowing white-orange along its seams and through its grate, in the middle of the picture')
rep(f, 'text', 'in a thick leather apron with a sun-disc badge on the chest, a smoke-blackened helmet and a faded sun-disc cloth wound round his head',
    'in a thick leather apron with a small gold wheel-shaped emblem stitched on brown cloth at the chest, a smoke-blackened helmet with a faded brown cloth wound round it')

# ---------- gE ----------
d = G['gE']
f = fall(d, 's19_f_yak')
rep(f, 'text', 'tawny amber eyes open and looking straight at us', 'tawny amber eyes open and steady, turned toward the far column')

# ---------- gF ----------
d = G['gF']
at(d, '欧德', (12, 12), '2988年春皇帝交了冠往南去，金鸢城东门那堆火还是他守着，他蹲在火边添柴。', has='这一段不出城')
at(d, '欧德', (14, 14), None, sub=('4602年初雪月', '4601年初雪月'))
at(d, '席恩', (1, 6), '他是九矛猎团的头。九矛只猎兽，不替哪一国打仗，到了纷争纪也一样。入夜他醒着，九矛的篝火边睡着的人睡得安稳。', has='不出墙')
f = fall(d, 's17_f_xien')
rep(f, 'text', 'He holds a long white-wood spear upright in both hands and presses its frost-white tip against the middle of his own brow,',
    'He holds a long white-wood spear in both hands with its head turned toward himself and rests the flat of its frost-white tip lightly against the middle of his own brow, the calm gesture of a night vigil that leaves no mark,')

# ---------- gH ----------
d = G['gH']
d['legends']['辛美尔']['quotes'] = ['路过的勇者。这张脸记住了，往后你们段城是要给我立像的。', '写人都在。']

for g, d in G.items():
    quotes(d)
    save(g, d)
print('改完', ' '.join(G))
