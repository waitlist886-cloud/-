#!/usr/bin/env python3
# 史诗战的分阶段立绘和神明显像（11-07 起）。一阶段一张、一位神一张，都是 2:3，写 out/史诗战_试/<键>.png（不进库）。
#   python gpt_epic.py trial [键…]     出样张（TRIAL 那几张，已有的跳过）
# 名号和每一阶的样子在 底稿/立绘/史诗战名号/（另一个会话写的，不进卡），拆成一阶一条在 epic/阶段表.json（epic_rows.py）。
# 画风：崩铁光锥那一路，两张光锥图只当画法参考，跟立绘的艺术照一个路子；*_old 那几张照 gpt_boss.py 的老画法（11-04 那四位）做对照。
# 同一个对手第二阶起拿上一阶那一张当最后一张参考，样子才连得上；神明显像不拿参考以外的图。
import concurrent.futures as cf
import os
import sys
import time

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_gen  # noqa: E402
import gpt_boss  # noqa: E402  只借老画法那一句 STYLE

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
LC = os.path.join(ROOT, '语料', '人物参考_11-04', 'hsr_lc')   # 用户给的崩铁光锥图，不进库
STYLE_REFS = [os.path.join(LC, 'fire.png'), os.path.join(LC, 'anaxa.png')]
OUT = os.path.join(HERE, 'out', '史诗战_试')

STYLE = ('Draw in the exact rendering style of the first two attached pictures, which are official Light Cone card art from the game Honkai: Star Rail. '
         'They are style references only: do not copy their characters, faces, costumes, props or composition, and do not put any figure from them into this picture. '
         'Thin crisp line art in a darker tint of each local colour; luminous, saturated colour with razor-sharp shadow shapes; light that blooms softly toward white against deep, rich darks; big clean flowing shapes; fine ornamental detail where the eye lands. ')
BOSS = ('This picture is the splash key art shown when an epic boss battle begins in a high-end Japanese fantasy RPG of swords and magic: '
        'one colossal being dominates the picture, seen slightly from below, its silhouette instantly readable even at a small size, ominous, majestic and beautiful. ')
GOD = ('This picture is the divine manifestation art of a god, the full-length plate for the codex of the gods in a high-end Japanese fantasy RPG of swords and magic: '
       'the god alone, large and centred, in the place and the light that belong to it, shown with the calm, absolute majesty of a deity rather than in the middle of a fight. ')
END = ' Portrait picture, aspect ratio 2:3. No text, no letters, no logo, no frame, no signature, no interface. No crescent or moon shapes anywhere.'
# 样张里这一句是写在 END 上的，锡蒙力那一张地上就多画了几个躺着的人：往后只给画面里本来有死人的那几阶加
DEAD = ' Nothing gory: the dead are drawn as grey, bloodless shapes.'
NEXT = ('The LAST attached picture shows this same being in its previous phase: keep it unmistakably the same being, with the same design, materials and colours, '
        'the same scale against the land and the same place, and change only what is described here for this phase, with a new composition. ')

# 七曜兽的君王·赤火，伊格纳隆（月银纪 M29）
IGN = 'An elemental king of fire: a colossal dragon-king, the sovereign of all fire in the land. '
# 千里无踪的过客巴耶力（纷争纪魔神 1，S49 塌天）
BAY = 'A demon god that is an empty cloak: a colossal standing cloak of grey feathers, as tall as a floating tower, with nothing inside it, the hood empty and dark, the sleeves empty, no face, no hands, no body, the hem never touching anything. '
# 万旗冢（前传 P12，第五十一层的楼层主）
WQ = ('A colossal floor guardian inside a dungeon that looks like an open world: a hunched thing taller than a fortress wall, heaped together out of the armour, shields and grey, bloodless bodies of the fallen of two armies, '
      'its whole body bristling with thousands of flagpoles and tattered banners as dense as a field of wheat; its two arms are huge bundles of long spears; '
      'set into the middle of its chest are two war horns twisted around each other, one of eastern bronze and one of western black horn. ')
WQ_LAND = ('A flat plain of young green winter wheat under a grey sky that looks as if dawn is about to break and never does; at the two far ends of the field stand two tall royal banners, one of an eastern kingdom and one of a western empire, with no king under either; '
           'in the middle stands a boundary stele made of one slab of white stone and one slab of black obsidian riveted back to back.' + DEAD + ' ')

TRIAL = {
    'm29_ignalon_1': (BOSS + IGN + 'Night over a chain of dozens of volcanoes in the far south, all of them glowing at once, rivers of lava threading down to a dark sea. '
                      'In the crater-heart of the largest volcano burns a ball of light whiter than fire, so bright that the rock rim around it glows white-hot. '
                      'Within the white light sits a colossal, perfectly motionless shape: the silhouette of a dragon-king seated upright like a temple statue, wings folded close around it like a mantle, horns rising like a crown, its eyes two points of a deeper white. '
                      'The heat bends the air in waves. On the crater rim tiny human figures shield their faces with their arms; one of them, staring too long, has hair turned white. '
                      'Palette: white-gold core, molten orange, charcoal black rock, a deep night-blue sky full of ash.', None),
    'm29_ignalon_1_old': ('OLD', 'm29_ignalon_1'),
    'm29_ignalon_2': (BOSS + NEXT + IGN + 'Second phase: it has risen to its feet inside the volcano. The dragon-king now stands taller than the mountain, wings half open, molten lava pouring over its shoulders and down its body like a long royal robe with a trailing hem; '
                      'the burning peaks around it flare up behind its head like a crown of fire. Dozens of volcanoes erupt together, the rivers of lava turn their course and run toward it, and where the lava meets the sea huge white columns of steam rise into the night. '
                      'Every flame in the land leans toward it like grass in the wind. Its eyes and the core of its chest glow white. Palette: white-gold, molten orange and red, black rock, white steam, deep sky.', 'm29_ignalon_1'),
    'm29_ignalon_3': (BOSS + NEXT + IGN + 'Final phase: the lava robe has slid off and fallen away. What remains is a single fire so white that its edges cannot be seen, and within it only the faint outline of the same dragon-king, seated again, calm and absolute, like a statue made of light. '
                      'Streaks of orange fire hurled at it by mages far below are swallowed the moment they touch it and burn white. The crater around it has turned to glowing glass and the air shimmers; everything else in the picture is dark against its whiteness. '
                      'Palette: blinding white with a faint gold edge, black glass, dark red embers.', 'm29_ignalon_2'),
    'g01_bayeli_1': (BOSS + BAY + 'A vast grey dead land under a pale overcast sky. In the middle layer of the sky hang dozens of floating stone towers resting on floating rocks, with griffin riders flying between the towers and the ground. '
                     'Among the clouds hangs the empty feather cloak, upright in the air. The wind is drawn as long thin white streaks flowing across the whole picture, and every streak bends and parts around the cloak. '
                     'A griffin rider carrying a message flies right past it without seeing it. Palette: faded ash grey, feather white, a pale sky, the warm stone of the towers small and far away. Eerie, quiet and beautiful.', None),
    'g01_bayeli_2': (BOSS + NEXT + BAY + 'Second phase: the uppermost layer of the sky is falling. A whole dome of sky, like a gigantic upturned bowl of grey cloud and broken light hundreds of miles wide, is slowly coming down over the edge of the dead land, and the floating towers tilt and fall with it. '
                     'The feather cloak has come apart into this falling sky: its grey feathers have become an endless veil drifting down from the collapsing dome, so that the whole sky looks like the same cloak and there is no single place where it is. '
                     'Below, small soldiers and griffin riders who have just arrived somewhere are fading out, translucent like ghosts, and the people beside them do not turn their heads. Palette: ash grey, white, dusk-violet shadow.', 'g01_bayeli_1'),
    'g01_bayeli_3': (BOSS + NEXT + BAY + 'Final phase: the grey veil has drawn back together into the empty feather cloak, now standing upright on a plain of shattered rock. Inside the cloak there is only an empty shadow in the shape of a person, a hollow darkness with no face. '
                     'From every direction, long white streaks of wind rush toward it and break sharply aside just before touching it, so that around the cloak there is a clear oval of perfectly still air where not one feather stirs: that hole in the wind is the god. '
                     'From the upper corner one great shining gust of white and pale blue comes straight down at the still place. Palette: grey, feather white, a cold blue-white gust, dark ground.', 'g01_bayeli_2'),
    'p12_wanqi_1': (BOSS + WQ + WQ_LAND + 'First phase: the colossus crouches before the boundary stele and is raising its head, and the two horns in its chest are sounding together. '
                    'On both sides of it, ranks of soldiers with grey faces, dead and silent, are rising out of the wheat rank after rank, counting off. Palette: grey sky, pale green wheat, faded banner colours, bronze and black, bone grey.', None),
    'p12_wanqi_2': (BOSS + NEXT + WQ + WQ_LAND + 'Second phase: the two grey armies have charged across the boundary and crashed together in the wheat. The colossus has risen to its full height and lunges into the thickest knot of living adventurers, one spear-bundle arm sweeping through the air in a wide arc. '
                    'From the backs of the living, flagpoles have begun to sprout, each carrying the small banner of that person\'s homeland, and the colossus turns toward wherever the banners are thickest. Flags and spears fill the air; the two horns in its chest blare. '
                    'Dynamic diagonal composition. Palette: grey, dust, faded banners, bronze glints, trampled green wheat.', 'p12_wanqi_1'),
    'p12_wanqi_3': (BOSS + NEXT + WQ + WQ_LAND + 'Final phase: the battle is over. The colossus kneels before the white-and-black boundary stele like a mourner, its chest opened wide like two great doors, and inside lie layers upon layers of fallen soldiers in rows. '
                    'The fallen on the field slide across the wheat toward its open chest together with their flagpoles and banners, ropes and straps trailing, as if pulled home. At the centre of its chest the two twisted horns still glow, one bronze and one black. '
                    'One small adventurer, a horned tiefling man in a worn grey cloak, has climbed onto its chest and grips the twisted horns with both hands, about to wrench them apart. A grey dawn that never comes, falling banner cloth, solemn and quiet.', 'p12_wanqi_2'),
    'god_ruiendal': (GOD + 'The god of swift horses, the gallop and the hunt, leader of a thousand riders. A very tall, lean hunter god with long wind-blown pale hair, the hide of a white-maned wild horse worn over his shoulders as a cloak with the horse\'s head as a hood, a great longbow on his back, '
                     'standing at the edge of a wide northern snowfield at night as a storm passes. Behind him runs a pack of hounds that cannot be seen: only long lines of fresh paw prints racing across the snow and snow kicked up as if by invisible bodies. '
                     'High in the storm clouds, streaks of white light run like a herd of horses galloping across the sky. Palette: snow white, silver, storm blue-grey, a warm glint of gold on the bow.', None),
    'god_simoli': (GOD + 'A demon god, the reflection of the god of the hunt: the black-maned lord, the sound of hooves behind the hunter. A rider grown together with a colossal black-maned beast, so that one cannot tell where the rider ends and the beast begins; '
                   'the mane falls over the head and hides the face completely; the mane streams back like black smoke and becomes a whole host of black riders behind it; its hooves raise no dust. '
                   'It stands on its high seat: the flat top of a black mountain with sheer cliffs on four sides, rising from a wasteland of black stone, with a camp of black-maned beasts at its foot. Palette: black, iron grey, the tips of the mane cold silver, a low dark-red sky.', None),
}


# 11-07 一阶出来以后加的对照：光锥参考在大怪物身上几乎不起作用，跟老画法差不多，另试两种真正不一样的画法
# 用户 11-07 挑了丙（card，照卡里四方）。又说瑞恩达尔的衣服看着像中式，要排查玄幻风和过度的中式风：
# 丙那一句去掉了“飘带一样的形状”（框里的飘带照留，画人身上就成了仙侠的样子），每一张都接 WEST 那一句。
REF = os.path.join(ROOT, '语料', '人物参考_11-04')
WEST = (' The world is Western high fantasy of swords and magic, a Japanese fantasy RPG set in a European-inspired world: every garment, armour, building and ornament is European medieval, Renaissance or original fantasy design. '
        'Absolutely no East Asian or Chinese elements: no hanfu, no wrap-collared or cross-collared robes, no wide trailing sleeves, no sash belts with hanging tassels or cords, no Chinese knots, jade pendants, hairpins or topknots, '
        'no pagoda or temple roofs, no auspicious cloud scrolls, no long serpentine Chinese dragon (a dragon here is a Western dragon with four limbs and great bat-like wings), and no xianxia look of immortals floating in streaming celestial ribbons. '
        'Banners, shields and badges carry European heraldry: lions, eagles, towers, keys, stars, suns with straight rays; no round chrysanthemum-like crests.')
VARIANTS = {
    # 卡里四方的定稿（迷宫纪、纷争纪右扇裁下来的），画风跟框统一
    'card': (('Draw in the exact rendering style of the attached pictures, which are crops of this game\'s own frame art: an elegant hand-painted look in the manner of a Genshin Impact promotional illustration and a paper theatre, refined thin line art, soft luminous gradients, graceful ornamental detail. '
              'They are style references only: do not copy their figures, faces, costumes or composition. '), [os.path.join(REF, 'maze_right_style.png'), os.path.join(REF, 'strife_right_style.png')]),
    # 崩铁英雄谭 PV 那一路（山铜纪右扇用过）：干笔色块
    'pv': (('Draw in the exact rendering style of the attached pictures, which are frames from an animated Honkai: Star Rail hero-epic short: bold hard-edged blocks of flat colour, dry-brush texture, paint running down in vertical streaks, figures read as silhouettes against huge shapes of light. '
            'They are style references only: do not copy their figures, buildings or composition. '), [os.path.join(REF, 'pv_red_temple.png'), os.path.join(REF, 'pv_back_detail.png')]),
}
for _k in ('m29_ignalon_1', 'p12_wanqi_1', 'g01_bayeli_1'):
    for _v in VARIANTS:
        TRIAL['%s_%s' % (_k, _v)] = ('VAR:' + _v, _k)

# 第二轮样张（11-07，丙加 WEST）：三个对手的二三阶接丙的一阶，两位神重出。键尾 _c，第三栏写画法
TRIAL['m29_ignalon_2_c'] = (TRIAL['m29_ignalon_2'][0], 'm29_ignalon_1_card', 'card')
TRIAL['m29_ignalon_3_c'] = (TRIAL['m29_ignalon_3'][0], 'm29_ignalon_2_c', 'card')
TRIAL['g01_bayeli_2_c'] = (TRIAL['g01_bayeli_2'][0], 'g01_bayeli_1_card', 'card')
TRIAL['g01_bayeli_3_c'] = (TRIAL['g01_bayeli_3'][0], 'g01_bayeli_2_c', 'card')
TRIAL['p12_wanqi_2_c'] = (TRIAL['p12_wanqi_2'][0], 'p12_wanqi_1_card', 'card')
TRIAL['p12_wanqi_3_c'] = (TRIAL['p12_wanqi_3'][0].replace('One small adventurer, a horned tiefling man in a worn grey cloak, has climbed onto its chest',
                                                       'One adventurer, a horned tiefling man in a worn grey travelling cloak and leather armour, large enough to be read clearly in the picture, has climbed onto its chest'), 'p12_wanqi_2_c', 'card')
TRIAL['god_ruiendal_c'] = (GOD + 'The god of swift horses, the gallop and the hunt, leader of a thousand riders, drawn as a Northern European huntsman king. A very tall, lean god with long wind-blown pale hair and a calm, keen face, '
                           'wearing the hide of a white-maned wild horse as a hooded mantle: the horse\'s head with its pricked ears and white mane forms the hood, the hide falls down his back like a cape. Under it a fitted dark leather hunting jerkin over a linen shirt, a broad leather belt with a curled hunting horn and a quiver, '
                           'close-fitting breeches and tall riding boots, leather bracers; a great longbow of pale ash in his hand. He stands at the edge of a wide northern snowfield at night as a storm passes. '
                           'Behind him runs a pack of hounds that cannot be seen: only long lines of fresh paw prints racing across the snow and snow kicked up as if by invisible bodies. High in the storm clouds, streaks of white light run like a herd of horses galloping across the sky. '
                           'Palette: snow white, silver, storm blue-grey, warm brown leather, a glint of gold on the bow.', None, 'card')
TRIAL['god_simoli_c'] = (GOD + 'A demon god, the reflection of the god of the hunt: the black-maned lord, the sound of hooves behind the hunter. Its body is a rider and a colossal black-maned beast grown into one: from the waist down the rider becomes the beast\'s neck and shoulders, like a dark armoured centaur, so that one cannot tell where the rider ends and the beast begins. '
                         'A long, heavy black mane falls over the rider\'s head and hides the face completely; the mane streams back like black smoke and becomes a whole host of shadowy black riders galloping behind it; its hooves raise no dust. '
                         'It stands on its high seat: the flat top of a black mountain with sheer cliffs on four sides, rising from a wasteland of black stone, with a camp of black-maned beasts at its foot. Palette: black, iron grey, the tips of the mane cold silver, a low dark-red sky.', None, 'card')


def job(k):
    p, prev = TRIAL[k][:2]
    style = TRIAL[k][2] if len(TRIAL[k]) > 2 else None
    if style:   # 第二轮起：照这个画法，加 WEST
        text, srefs = VARIANTS[style]
        refs = list(srefs) + ([os.path.join(OUT, prev + '.png')] if prev else [])
        return gpt_gen.gen(os.path.join(OUT, k), text + p + END + WEST, refs=refs, timeout=1200)
    if p.startswith('VAR:'):   # 同一张的提示词，换画法和画法参考
        style, refs = VARIANTS[p[4:]]
        return gpt_gen.gen(os.path.join(OUT, k), style + TRIAL[prev][0] + END, refs=list(refs), timeout=1200)
    if p == 'OLD':   # 老画法对照：gpt_boss.py 那一句 STYLE，不给光锥参考，提示词照新的那一张（去掉新画法那几句）
        src, _ = TRIAL[prev]
        return gpt_gen.gen(os.path.join(OUT, k), gpt_boss.STYLE + src.replace(BOSS, ''), refs=[], timeout=1200)
    refs = list(STYLE_REFS) + ([os.path.join(OUT, prev + '.png')] if prev else [])
    return gpt_gen.gen(os.path.join(OUT, k), STYLE + p + END, refs=refs, timeout=1200)


def run(keys, workers=4):
    """按依赖跑：上一阶出好了才开下一阶。"""
    os.makedirs(OUT, exist_ok=True)
    todo = [k for k in keys if not os.path.exists(os.path.join(OUT, k + '.png'))]
    done, bad, running = set(), [], {}
    with cf.ThreadPoolExecutor(workers) as ex:
        while todo or running:
            for k in list(todo):
                dep = None if TRIAL[k][0] == 'OLD' or TRIAL[k][0].startswith('VAR:') else TRIAL[k][1]   # 对照只借提示词，不用等
                if len(running) < workers and (dep is None or os.path.exists(os.path.join(OUT, dep + '.png'))):
                    if dep and dep in bad:
                        todo.remove(k); bad.append(k); continue
                    running[ex.submit(job, k)] = (k, time.time()); todo.remove(k)
            if not running:
                break
            fin, _ = cf.wait(list(running), return_when=cf.FIRST_COMPLETED)
            for f in fin:
                k, t0 = running.pop(f)
                try:
                    f.result(); done.add(k); print('好了', k, '%ds' % (time.time() - t0), flush=True)
                except Exception as e:   # noqa: BLE001
                    bad.append(k); print('失败', k, e, flush=True)
    print('== 好了 %d 失败 %d %s' % (len(done), len(bad), ' '.join(bad)), flush=True)


# ===== 第三轮样张（11-07）：用户发了参考，“黑魂，原神，法环这种西幻风格压迫感极强的强敌” =====
# 参考十张收在 语料/Boss参考_11-07/（不进库）：原神 Boss 卡五张（关闭钮、UID、水印裁掉了），黑魂三教宗、法环佛提萨克斯、玛莲妮亚、艾尔登之兽、葛弗雷。
# 两种对照，同四个对手的一阶：_hc 丙的画法加压迫感；_hg 拿原神 Boss 卡当画法参考加压迫感。法环、黑魂那几张是写实的，只取压迫感写进字里，不当画法参考。
HEAVY = ('This picture is the key art of a formidable boss of a Western dark-fantasy action RPG, with the crushing presence of the great bosses of Dark Souls, Elden Ring and Genshin Impact: '
         'the enemy is overwhelming and menacing, bearing down on the viewer from a low angle and filling the frame, its silhouette heavy and sharp, its gaze, or the darkness where its face should be, fixed on the viewer; '
         'tiny armed warriors at its feet give the scale; a dark, oppressive atmosphere of storm, smoke, embers and dust, deep heavy colours, strong backlight and rim light that only make it more threatening. '
         'It must feel terrifying and unbeatable, a true final boss, never decorative, cute or pretty. ')
BOSS_REF = os.path.join(ROOT, '语料', 'Boss参考_11-07')
VARIANTS['gi'] = (('Draw in the rendering style of the attached pictures, official boss key art from Genshin Impact: crisp anime line art, bold saturated colour, dynamic painterly effects of energy, debris and light. '
                   'They are style references only: do not copy their characters, costumes, colours or the round backdrop. '), [os.path.join(BOSS_REF, 'gi_card_purple_dragon.png'), os.path.join(BOSS_REF, 'gi_card_raiden.png')])
VARIANTS['card_heavy'] = (VARIANTS['card'][0].replace('an elegant hand-painted look', 'a hand-painted look').replace('graceful ornamental detail', 'heavy dramatic contrast and fine ornamental detail'), VARIANTS['card'][1])
_BAYEN = ('A demon god giant as tall as a hill, grey-brown stone skin, two horns on the head, a seam of black light seeping from a wound on the left shoulder; hands like boulders. It walks wrapped in a shroud of dust, mostly dissolved into dust haze, face hidden in the dust. '
          'The southern horizon: mountains lowering one after another as the dust giant approaches. In the foreground fortress walls fall away block by block from their seams, cannon platforms with their cannons tip over, '
          'and the light of crystal cannons strikes the giant and vanishes into it like stones thrown into water. Palette: ash grey, dust yellow, black light.')
for _k, _src in (('m29_ignalon_1', TRIAL['m29_ignalon_1'][0]), ('g01_bayeli_1', TRIAL['g01_bayeli_1'][0]), ('p12_wanqi_1', TRIAL['p12_wanqi_1'][0]), ('s15_bayen_1', BOSS + _BAYEN)):
    TRIAL[_k + '_hc'] = (HEAVY + _src.replace(BOSS, ''), None, 'card_heavy')
    TRIAL[_k + '_hg'] = (HEAVY + _src.replace(BOSS, ''), None, 'gi')


# ===== 正式出图（11-07，画法照丙加 WEST）=====
#   python gpt_epic.py batch <份…>       份：moon strife_god1 strife_god2 strife_other bronze maze gods_zheng gods_mo；已有的跳过
#   python gpt_epic.py list <份…>        只数缺几张，不出图
# 提示词是子任务照 底稿/立绘/史诗战_写提示词说明.md 写的 epic/prompts/<份>.json；
# 史诗战写 out/史诗战/<份>/<键>.png，神明显像写 out/神明显像/<键>.png。
# 参考图排法：丙的两张画法参考，有立绘的人接他的战斗格和脸，最后一张是上一阶（prev）或者同一个东西别的仗（design_ref）。
import json  # noqa: E402

PROMPTS = os.path.join(HERE, 'epic', 'prompts')
EPIC_OUT = os.path.join(HERE, 'out', '史诗战')
GOD_OUT = os.path.join(HERE, 'out', '神明显像')
BOSS_DIR = os.path.join(HERE, 'out', '四方_11-03', 'boss')
CARD_TEXT, CARD_REFS = VARIANTS['card']
# 11-07 用户定了丙加压迫感：史诗战用 card_heavy 加 HEAVY；魔神显像也加压迫感（GOD_MO，静的、在高座上）；正神显像照旧 card 加 GOD
HEAVY_TEXT = VARIANTS['card_heavy'][0]
GOD_MO = ('This picture is the divine manifestation art of a demon god, the full-length plate for the codex of the gods in a Western dark-fantasy RPG: the demon god alone, large and centred, on its high seat, '
          'seen from a low angle, with a calm, absolute and menacing majesty: oppressive and terrifying even in stillness, deep heavy colours and strong backlight, never decorative, cute or pretty. ')
PERSON = ('The two attached pictures right after the style references show this exact character, a full-length sprite and a close-up of the face: keep the same face, eyes, hair colour and hairstyle, '
          'the same build and the same costume design, redrawn in this picture\'s style and scale. ')
# 11-07 批量头一轮（九十八张）看出来：拿上一阶当参考，模型把构图也照抄了，两阶像同一张。参考只用来认长相，构图、机位、动作、那一刻都换
NEXT2 = ('The LAST attached picture shows this same being in its previous phase. Use it ONLY to keep the being recognisable: its design, materials, colours and marks. '
         'Do NOT copy that picture\'s composition: this phase must be a clearly different picture, with a different camera distance and angle, a different pose and action, and a different moment of the battle, as described here. ')
DESIGN_B = ('The LAST attached picture shows this same being in another battle. Use it ONLY to keep the being recognisable: its design, materials, colours and marks. '
            'Do NOT copy that picture\'s composition, pose, camera or scene: draw the battle described here as a new picture. ')
# 每一阶给一个跟上一阶不一样的机位（只是建议，提示词里写了的照提示词）
CAMERA = {2: 'Unless described otherwise, the camera for this phase is much closer, a dramatic low angle on the head and upper body in the middle of its attack, the frame cutting through it. ',
          3: 'Unless described otherwise, the camera for this phase is pulled far back and high, the whole being and the ruined battlefield in view, the warriors tiny before it. ',
          4: 'Unless described otherwise, the camera for this phase is a sharp three-quarter view from the side, the being turning toward the viewer. ',
          5: 'Unless described otherwise, the camera for this phase looks down from high above at the being and the ground it is breaking. ',
          6: 'Unless described otherwise, the camera for this phase is very close on its hand, weapon or wound, the rest of it looming out of focus behind. ',
          7: 'Unless described otherwise, the camera for this phase is level with its face, eye to eye, filling the frame. '}
GOD_DESIGN = ('The LAST attached picture shows this same god as it appeared in battle. Use it ONLY to keep the same design, materials, colours and marks; do NOT copy its composition or scene: draw the calm manifestation on its high seat described here as a new picture. ')
SETS = {'1001': '立绘_v3'}


def part_of(key):
    if key.startswith('god_'):
        return None
    i = key.rfind('_')
    return key[:key.rfind('_', 0, i)]


def img(key):
    if key.startswith('boss:'):
        return os.path.join(BOSS_DIR, key[5:] + '.png')
    if key.startswith('god_'):
        return os.path.join(GOD_OUT, key + '.png')
    return os.path.join(EPIC_OUT, part_of(key), key + '.png')


def person_refs(pkey):
    """立绘的战斗格和脸。键在哪一套照 cast 下的资料找。"""
    import glob
    for p in glob.glob(os.path.join(HERE, 'cast', '**', '*.json'), recursive=True):
        rel = os.path.relpath(p, os.path.join(HERE, 'cast')).replace(os.sep, '/')
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception:   # noqa: BLE001
            continue
        items = d if isinstance(d, list) else [dict(v, en=k) for k, v in d.items() if isinstance(v, dict)]
        if any(isinstance(c, dict) and c.get('en') == pkey for c in items):
            cset = rel.split('/')[0] if '/' in rel else '1001'
            folder = os.path.join(HERE, 'out', SETS.get(cset, '立绘_' + cset), pkey)
            return [os.path.join(folder, 'cell_battle.png'), os.path.join(folder, 'head.png')]
    raise KeyError('立绘里找不到 ' + pkey)


def load_jobs(parts):
    jobs = {}
    for part in parts:
        data = json.load(open(os.path.join(PROMPTS, part + '.json'), encoding='utf-8'))
        if part.startswith('gods_'):
            for g in data:
                ref = g.get('design_ref')
                head = (MJ_TEXT + MJ_GOD_MO) if part == 'gods_mo' and not g.get('calm') else (MJ_TEXT + MJ_GOD)   # 11-07 用户定了 MJ 那一路；calm 的魔神（薇瑟兰）走正神那种静穆的写法
                text = head + (GOD_DESIGN if ref else '') + g['prompt'] + END + WEST
                jobs[g['key']] = dict(text=text + FACE_JRPG, refs=list(MJ_REFS), last=ref, out=img(g['key']))
            continue
        for b in data:
            pr = person_refs(b['person']) if b.get('person') else []
            for p in b['phases']:
                last = p.get('prev') or p.get('design_ref') or (b.get('design_ref') if p is b['phases'][0] else None)
                lead = (PERSON if pr else '') + (NEXT2 if p.get('prev') else DESIGN_B if last else '') + (CAMERA.get(p['no'], '') if p.get('prev') else '')
                text = MJ_TEXT + HEAVY_MJ + (MJ_COMP_PERSON if pr else MJ_COMP) + lead + b['design'] + ' ' + p['prompt'] + END + (DEAD if p.get('dead') else '') + WEST + FACE_JRPG
                jobs[p['key']] = dict(text=text, refs=list(MJ_REFS) + pr, last=last, out=img(p['key']))
    return jobs


def limited(stem):
    try:
        t = open(stem + '.log', encoding='utf-8', errors='replace').read().lower()
    except OSError:
        return False
    return 'usage_limit' in t or 'usage limit' in t or ' 429' in t


# 11-07 用户说额度用完可以直接换号：本机登了几个号就轮着用。~/.codex 是眼下这个号；另一个号登在 ~/.codex_b（用户自己登，见 CLAUDE.md），有 auth.json 才算。
HOMES = [h for h in (os.path.join(os.path.expanduser('~'), '.codex'), os.path.join(os.path.expanduser('~'), '.codex_b')) if os.path.exists(os.path.join(h, 'auth.json'))]


def run_batch(jobs, workers=4):
    """按依赖跑（上一阶、别的仗、史诗战里的魔神出好了才开）；一个号撞了额度就换下一个号，都撞了才停。"""
    todo = [k for k, j in jobs.items() if not os.path.exists(j['out'])]
    done, bad, running = [], [], {}
    stop = False
    homes = list(HOMES) or [None]
    cur = 0
    spent = set()
    print('== 登了 %d 个号：%s' % (len(homes), '，'.join(os.path.basename(h) for h in homes if h)), flush=True)
    t_all = time.time()
    with cf.ThreadPoolExecutor(workers) as ex:
        while (todo and not stop) or running:
            for k in list(todo):
                if stop or len(running) >= workers:
                    break
                j = jobs[k]
                last = j['last']
                if last and not last.startswith('boss:') and last in jobs and not os.path.exists(img(last)):
                    if last in bad:
                        todo.remove(k); bad.append(k); print('跳过（参考的那一张没出来）', k, flush=True)
                    continue
                if last and not os.path.exists(img(last)):
                    todo.remove(k); bad.append(k); print('跳过（参考图不在）', k, img(last), flush=True)
                    continue
                refs = j['refs'] + ([img(last)] if last else [])
                os.makedirs(os.path.dirname(j['out']), exist_ok=True)
                fut = ex.submit(gpt_gen.gen, j['out'][:-4], j['text'], refs, 'gpt-6-luna', 'low', 1200, homes[cur])
                running[fut] = (k, time.time(), homes[cur]); todo.remove(k)
            if not running:
                if todo and not stop:   # 剩下的都在等别人：等的那一个不在这一批里
                    for k in todo:
                        bad.append(k); print('跳过（等的那一张不在这一批）', k, jobs[k]['last'], flush=True)
                    todo = []
                break
            fin, _ = cf.wait(list(running), return_when=cf.FIRST_COMPLETED)
            for f in fin:
                k, t0, h = running.pop(f)
                try:
                    f.result(); done.append(k); print('好了', k, '%ds' % (time.time() - t0), flush=True)
                except Exception as e:   # noqa: BLE001
                    if limited(jobs[k]['out'][:-4]):
                        spent.add(h)
                        left = [i for i, x in enumerate(homes) if x not in spent]
                        if left:
                            todo.insert(0, k)   # 这一张是额度的毛病，换了号接着出
                            if homes[cur] in spent:
                                cur = left[0]; print('== %s 撞了出图额度，换到 %s' % (os.path.basename(h or '.codex'), os.path.basename(homes[cur] or '.codex')), flush=True)
                        else:
                            bad.append(k); stop = True; print('== 撞了出图额度，不再开新的', flush=True)
                    else:
                        bad.append(k); print('失败', k, str(e)[:160], flush=True)
    print('== 好了 %d 失败或跳过 %d 没开 %d，%d 分钟' % (len(done), len(bad), len(todo), (time.time() - t_all) // 60), flush=True)


# ===== 第四轮样张（11-07）：用户说“保持之前那种压迫感，但是改为这种干净一些的midjourney的风格” =====
# 用户发了七张 Midjourney 的图（冰龙压在白城上、圣像巨人、戴冠的巨王和崖上一队人、展翼的魔、云里的龙眼、云巨人和插地的大剑、云上的世界脊背），
# 手机界面裁掉了，收在 语料/Boss参考_11-07/mj_*.png。画法参考取两张：干净明亮的冰龙白城、压迫感重的巨王和崖上一队人。
VARIANTS['mj'] = (('Draw in the style of the attached reference pictures: a clean, cinematic epic-fantasy matte painting in the manner of Midjourney concept art: painterly realism with soft volumetric light, '
                   'deep atmospheric perspective with haze, mist and towering clouds, a restrained and harmonious palette, large calm shapes and a lot of sky, crisp forms without comic line art and without ornamental clutter. '
                   'They are style references only: do not copy their creatures, figures, buildings or composition. '),
                  [os.path.join(BOSS_REF, 'mj_ice_dragon_city.png'), os.path.join(BOSS_REF, 'mj_crowned_giant_party.png')])
HEAVY_MJ = ('This picture is the key art of a formidable boss of a Western fantasy RPG, with the crushing presence of the great bosses of Dark Souls and Elden Ring: the enemy is overwhelming and menacing, '
            'looming over the viewer from a low angle, its silhouette enormous, heavy and sharp, its gaze, or the darkness where its face should be, turned toward the tiny figures below. '
            'It must feel terrifying and unbeatable, a true final boss, never decorative, cute or pretty. ')
MJ_COMP = ('Composition: the colossal being dominates the picture and towers over everything, partly veiled by haze or cloud, its scale overwhelming; in the foreground one or a few tiny figures, seen from behind, stand facing it and give the scale. '
           'Keep the picture clean and readable: one huge silhouette against a clear sky or a clean field of mist, a clear horizon, nothing busy; armies and crowds become small silhouettes in the distance. The mood is dread and awe. '
           'If the enemy described is a person of human size rather than a colossus, draw that person large in the foreground facing the viewer instead, the face clearly visible. ')
MJ_COMP_PERSON = ('Composition: the enemy here is a person of human size, a legend, not a colossus: draw them large in the foreground, facing the viewer from a low angle, imposing and dangerous, '
                  'the face clearly visible, the battlefield and their own side behind them in haze; no tiny figure seen from behind in front of them. ')
# 用户 11-07：“神明显像归为神祇的全力姿态”。不是静穆的肖像，是祂的权柄整个放出来的那一刻（不打仗）
MJ_GOD = ('This picture is the divine manifestation art of a god in its FULL DIVINE POWER, for the codex of the gods in a Western fantasy RPG: the god alone, vast as a mountain, its authority completely unleashed over the land: '
          'its element and its domain surge around it in a storm of light, its halo blazing, its emblem or weapon raised, the sky and the land bending toward it. Not a calm portrait: the god at the height of its might, overwhelming and glorious, though not fighting anyone. '
          'Far below, one tiny nameless pilgrim seen from behind (not the god) looks up at it and gives the scale. Clean and readable: one huge silhouette, a lot of sky. ')
MJ_GOD_MO = ('This picture is the divine manifestation art of a demon god in its FULL UNHOLY POWER, for the codex of the gods in a Western fantasy RPG: the demon god alone, risen from its high seat, vast as a mountain, its authority completely unleashed: '
             'its corrupted domain spreads over the land around it, its dark halo or crown blazing, the sky darkening and the land breaking toward it. Not a calm portrait: the demon god at the height of its dreadful might, though not fighting anyone. '
             'Far below, one tiny nameless pilgrim seen from behind (not the god) looks up at it and gives the scale. Clean and readable: one huge silhouette, haze and sky. ')
for _k, _src in (('m29_ignalon_1', TRIAL['m29_ignalon_1'][0]), ('g01_bayeli_1', TRIAL['g01_bayeli_1'][0]), ('p12_wanqi_1', TRIAL['p12_wanqi_1'][0]), ('s15_bayen_1', BOSS + _BAYEN)):
    TRIAL[_k + '_mj'] = (HEAVY_MJ + MJ_COMP + _src.replace(BOSS, ''), None, 'mj')
TRIAL['god_ruiendal_mj'] = (MJ_GOD + TRIAL['god_ruiendal_c'][0].replace(GOD, ''), None, 'mj')
TRIAL['god_simoli_mj'] = (MJ_GOD_MO + TRIAL['god_simoli_c'][0].replace(GOD, ''), None, 'mj')
MJ_TEXT, MJ_REFS = VARIANTS['mj']
# 用户 11-07：“神明显像补充一点，神明的装扮应该更有神祇的那种感觉”
DIVINE = ('Dress and adorn the god as a true deity, never as a mortal: sacred vestments and divine regalia instead of everyday clothes, garments woven of light and of the god\'s own element, '
          'fine gold or silver filigree, glowing sigils of its domain, a halo or a crown of light behind or above the head, sacred emblems floating near it, the hems dissolving into its element. '
          'Where the description gives plain clothes, keep their cut but make them immaculate, luminous and timeless. Western in spirit, like the gods of Greek and Norse myth, of Elden Ring, or the Archons of Genshin Impact in their divine forms; never Chinese immortal robes. ')
DIVINE_MO = ('Its regalia is that of a fallen deity: unholy vestments and dark regalia, a dark halo, a broken or thorned crown or a corona of shadow, glowing sigils of its corrupted domain; '
             'where it is a beast or a thing rather than a figure, the same unholy majesty shows in its shape, its marks and the light around it. ')
MJ_GOD = MJ_GOD + DIVINE
MJ_GOD_MO = MJ_GOD_MO + DIVINE_MO
# 用户看了第四轮回“基本ok，但是注意人脸应该还是jrpg风格的”：人脸一律画成 JRPG 的动漫脸，别的照旧是写实的笔触；没脸的照旧没脸
FACE_JRPG = (' Every human or humanoid face in the picture is drawn in Japanese RPG anime style, like the face of a character from a JRPG or Genshin Impact: clean, beautiful anime features, '
             'expressive eyes, a small nose and mouth, smooth simple shading on the face; only the faces are anime, everything else keeps the painterly matte-painting look. '
             'Beings described as faceless or with hidden faces stay faceless.')


if __name__ == '__main__':
    if sys.argv[1:2] == ['trial']:
        run(sys.argv[2:] or list(TRIAL), workers=int(os.environ.get('EPIC_WORKERS', '4')))
    elif sys.argv[1:2] in (['batch'], ['list']):
        J = load_jobs(sys.argv[2:])
        miss = [k for k, j in J.items() if not os.path.exists(j['out'])]
        print('一共 %d 张，缺 %d 张' % (len(J), len(miss)), flush=True)
        if sys.argv[1] == 'batch':
            run_batch(J, workers=int(os.environ.get('EPIC_WORKERS', '4')))
