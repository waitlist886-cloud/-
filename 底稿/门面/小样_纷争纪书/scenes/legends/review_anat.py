# 11-13 人体那一轮：用户看了传奇之陨回“有很多出现人体问题……肢体错位或者看起来跟断了一样，甚至还有的背部和胸前分不清，左右躯干分不清”。
# 主会话把四十五幅照原尺寸逐张看了一遍，十一幅有毛病，其中八幅的病根是场面稿写了 seen from behind at three-quarter 又要露脸。
# 这里把这十一幅的场面改成三种朝向之一（正面或斜正面、纯背影、正侧面），每只手在做什么写明。珂伦娜那一幅不算错（她本来四条胳膊），
# 背影里看不清，顺手改成侧面、四条胳膊都看得见。跑过一回就不再跑（各条带 anat 记号）。旧图挪成 <键>_a0.png。
#   python -I -X utf8 review_anat.py          只报
#   python -I -X utf8 review_anat.py --apply  写盘、挪旧图
import glob
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '状态栏', 'comfy', 'out', '门面_原画_纷争纪'))

# 键: (改哪几栏, 为什么)
R = {}

R['s04_f_sefer'] = dict(why='两只手都握在杆的高处，左臂像从脑后绕出来。改成右手单手拖杆、左臂照跑步摆在身前。', sub=[(
    "He has swung a long burnt-bent iron bar back over his shoulder in both hands and his mouth is open in a roar.",
    "He runs with a natural sprinter's stride, one knee driving forward. In his right hand alone, held low and out to his right side, he drags a long burnt-bent iron bar whose red-hot end trails behind him just over the ground in a shower of sparks; "
    "his left arm swings forward in front of his left side, bent at the elbow, the fist clenched. Both arms are plainly seen from shoulder to hand, and nothing crosses his chest or passes behind his head. His mouth is open in a roar.")])

R['s17_f_valkes'] = dict(
    why='头偏在一侧肩上、腰带落在两肩当中，看不出是胸还是背。改成从拳底下的人堆里往上看，他正面弓着身、背顶着石头。',
    camera="very low, from among the people he shelters, looking up at his bowed chest and face, the underside of the fist filling the top of the frame, strong foreshortening",
    light="cold pale noon light blocked by the fist, a thin line of silver along the edge of the fist and along his shoulders and arms, and a soft pale light thrown up from the dusty ground onto his face and chest",
    sub=[(
        "Directly beneath the fist, seen from behind at three-quarter, the half-orc Valkes has turned his back to it and bowed under it with his knees bent: about two metres twenty, grey-green skin, short dark hair, shoulders as wide as half a gate, a heavy dark leather coat. The stone has landed across his bent back and broad shoulders and he carries its whole weight there, his head lowered between his shoulders; he does not catch it with his hands, his arms are spread low to both sides to shelter the people in front of him.",
        "Directly beneath the fist the half-orc Valkes stands facing the camera, seen from the front and from low down, bowed forward under the stone the way a man carries a roof beam across his shoulders: about two metres twenty, grey-green skin, short dark hair, shoulders as wide as half a gate, a heavy dark leather coat. "
        "His knees are bent and wide apart, his chest is toward us, and his broad back and the back of his shoulders are pressed up against the underside of the fist, which lies across them behind and above his lowered head; he carries its whole weight there. "
        "He does not touch the stone with his hands: his two arms are spread out low, one to each side, with the hands open, sheltering the people at his feet."),
        (
        "He looks sideways over his shoulder toward the people with his mouth open as if asking them something; one of his lower tusks is a broken stub. In the pocket of shadow under the fist, close around his legs, five or six people stand huddled and still on their feet with their faces upturned: soldiers in iron helmets and grown-up refugees, all of them adults.",
        "He looks down at the people right in front of him, toward the camera, with his mouth open as if asking them something; one of his lower tusks is a broken stub. "
        "In the near foreground along the bottom of the frame, seen from behind and partly out of focus, are the heads and shoulders of five or six people who stand close under him, still on their feet, their faces unseen and turned up toward him: iron helmets, a hood, a bandaged head; soldiers and grown-up refugees, all of them adults.")])

R['s12_f_dion'] = dict(
    why='两只脚朝向相反、披风往前飘，分不清往哪边走。改成整个人正侧面朝左（朝着灯），倒退着往右走，脚印从左边一路排到脚尖前。',
    camera="level, from his left side at a middle distance, the boy in full profile, slightly tilted, the goddess tall at the right edge of the frame",
    sub=[(
        "In the middle of the picture the boy with the bronze shield walks backward toward the right, seen in profile from his left side: slim and upright, about seventeen, black hair ruffled by wind with a faint gold sheen on the lit strands, deep stormy slate-blue eyes lifted to the lamp on the left, the chin raised, every line of the body stiff and proud. His clothes cover him from neck to wrist to ankle, dark sail-cloth grey.",
        "In the middle of the picture the boy with the bronze shield is seen in clean profile from his left side. His whole body faces LEFT, toward the wall and the lamp: his face, his chest, his knees and the toes of both boots all point left, and his chin is raised to the lamp. "
        "But he is walking backward, away from it, toward the right: one leg reaches back behind him, to the right, with the toe feeling for the ground, the other leg is still straight under him, and his arms hang at his sides with the hands closed. "
        "A line of his own bootprints in the pale frost runs from the left edge of the picture up to his toes, so that he faces the tracks he has just made. The air is perfectly still: his hair and his coat hang straight down and nothing streams from him. "
        "He is slim and upright, about seventeen, black hair with a faint gold sheen on the lit strands, deep stormy slate-blue eyes, every line of the body stiff and proud. His clothes cover him from neck to wrist to ankle, dark sail-cloth grey."),
        (
        "On his back he carries a round bronze shield polished like a still lake,",
        "On his back, on the side toward the right of the picture, he carries a round bronze shield polished like a still lake,"),
        (
        "He steps backward over bare ground without looking where he puts his feet. At the right edge of the frame, tall and thin and cut off by the frame, the goddess of lamps walks away to the south ahead of him:",
        "He does not look where he puts his feet. At the right edge of the frame, in the direction he is backing toward, tall and thin and partly cut off by the frame, the goddess of lamps walks away to the right, seen from behind:")])

R['s08_f_ryan'] = dict(
    why='躯干像背，腰带和灯又像在身前，头扭成正侧面。改成从潮这一边看过去，他正面站在缺口里。',
    camera="low, from within the front rank of the horde, looking up at him standing in the mouth of the breach, the wall towering behind him, slightly tilted",
    light="dusty amber low sun from behind the camera and the horde, falling full on him and on the white stone, the long shadows of spears reaching across the rubble toward his feet; the cold grey of the wall above; one small warm amber point from the lamp at his belt",
    text=("Scene: Late afternoon at a ruined stretch of the White Stone Wall in the far north, the worst-kept section of the line. The wall fills the background, enormous, pale and scarred with burn marks, rising out of the top of the frame; "
          "a huge breach has been torn through it in the middle of the picture, its broken white blocks piled at the base, and through the gap only an empty walkway and a dust-brown sky are seen: no other defender anywhere. "
          "In the mouth of the breach, in the middle of the picture, the shackled former miner stands facing the camera, seen from the front at three-quarter and from low down, his feet planted apart on the rubble, alone. "
          "He is a lean, hard-muscled human man who looks about thirty, 178 cm, with thick forearms and shoulders, close-cropped hair and skin as pale as someone who has never been in the sun. "
          "His bare arms and torn grey shirt are marked with soot, scratches and dark blood. His left arm hangs at his left side: on that wrist is one coarse iron shackle with its lock open, and a length of heavy chain swings from it. "
          "His right hand, at his right hip, grips a worn miner's hammer whose head has three notches knocked out of it. At his belt hangs a small oil lamp burning with a steady amber flame. "
          "His face squints against the low sun, tired and set, not afraid. "
          "The enemy is on our side of him. In the near foreground, along the bottom edge and at both lower corners, large, dark and out of focus and seen from behind, are the horned helmets, the shoulders, the torches and the long spear shafts "
          "of the front rank of a tide of demon-kin warriors closing on him, only twenty paces from where he stands, and their long shadows stretch across the white rubble to his feet. "
          "Drifting grey ash, sparks and chips of white stone hang in the air between."))

R['s15_f_wulde'] = dict(
    why='背对镜头，两只手都伸在身子左边，像两条左臂。改成正侧面朝右，两条胳膊一高一低都往前伸。',
    camera="low and wide from her right side, she in full profile in the lower left of the frame, looking up along her raised hand into the starless hole in the sky at the upper right, tilted",
    light="the cold silver-blue of the failing starlight on her face and raised hand, a warm red and gold edge from the winged god's fire along her back, the sky inside the dark outline pure black",
    sub=[(
        "Filling the whole upper half of the picture and cropped by the frame on three sides, a vast dark silhouette",
        "Filling the upper right of the picture and cropped by the frame at the top and the right, a vast dark silhouette"),
        (
        "In the middle foreground a tall thin woman of about forty-two stands seen from behind at three-quarter, shoulders curved slightly forward,",
        "In the lower left of the picture a tall thin woman of about forty-two stands in clean profile, facing RIGHT toward the dark silhouette and seen from her right side, shoulders curved slightly forward,"),
        (
        "Her feet are planted wide between the dark giant and the figure behind her, her left hand held out flat palm up with a thin ring of faint pale points of light hanging above it like a small map of stars, her right hand open and steady toward the hole in the sky, her grey eyes fixed upward. Close behind her and to the right, much taller than she is,",
        "Her feet are planted apart, both pointing right, between the dark giant and the figure behind her. Both her arms reach forward, to the right, one above the other, and each is plainly seen from shoulder to hand: "
        "the nearer arm, her right, is raised high with the open hand held up steady toward the hole in the sky; the farther arm, her left, is held out lower, at the height of her waist, with the palm flat and upward, "
        "and above that palm hangs a thin ring of faint pale points of light like a small map of stars. Her grey eyes are fixed upward to the right. Behind her, to the left of her in the picture and a step further from us, much taller than she is,")])

R['s12_f_kailan'] = dict(
    why='两条腿劈得过开，后腿比前腿长出一截。改成朝右前方跑的斜正面，步子照真人跑步的大小，只有头回过去。',
    camera="low from the grass a little ahead of him, looking up at him as he runs toward us and to the right, wide-angle, slightly tilted",
    sub=[(
        "In the middle of the picture the runner is caught in mid-stride just over the line, running toward the right but with his head and shoulders twisted back toward us and the wall, one foot still touching the green.",
        "In the middle of the picture the runner runs from left to right and a little toward us, seen from the front at three-quarter so that his chest is toward us, caught in a light, natural running stride just over the line: "
        "the forward knee is lifted, the back foot is only just leaving the green grass behind him, both legs are the same length and the stride is no longer than a real runner's. "
        "As he runs he looks back over the shoulder that is nearer to us, toward the wall on the left, his head turned no further than that shoulder, so that we see his face at three-quarter, turned to the left of the picture. "
        "The arm nearer to us is flung back toward the wall with the hand open, waving the watchers away; the other arm is bent at his side as a runner's is."),
        (
        "His mouth is wide open, shouting something back over his shoulder.",
        "His mouth is wide open, laughing and shouting something back to them.")])

R['s12_f_edmund'] = dict(
    why='上身是背、下摆像正面的开襟，头扭过来。改成从圈里往外看，他正面朝我们走进来，看得见那一笑。',
    camera="low and wide from inside the ring, looking outward at him as he walks in toward us between two of the fires, level",
    light="a cold blue night; the warm red light of the ring of campfires behind him rims his shoulders, his hair and the edge of his coat, and a faint warm glow from a low shielded fire on our side lights his face",
    text=("Scene: deep night on the grey plain south of a long wall, at the height of a great war between gods. We stand inside a ring of the demon-folk's army, looking outward. "
          "In the middle distance a wide ring of campfires curves across the picture from edge to edge, with dozens of dark armoured horned shapes standing between the fires, all of them turned to look at the one man who has walked in among them. "
          "That man, the tall thin court musician, has already passed between two of the fires and comes walking toward us, alone, in the middle of the picture, seen from the front, his whole figure in view: "
          "forty-six years old to look at, about 184 centimetres, neatly trimmed deep blue-black hair with four or five thread-thin white strands at the temples, a grey wool coat down to the knee, buttoned, and at his belt a small bone vial holding a pinch of grey-white sand. "
          "He carries no weapon. His two arms hang relaxed at his sides with the hands open and empty. He walks at an easy pace, one foot in front of the other. "
          "He walks a little to one side, so that an empty place the width of a person is left beside him, on the right of him as we look at him, as if for someone walking next to him; "
          "his head is turned a little toward that empty place, and the corner of his mouth is lifted in a small, rare, genuine smile. "
          "In the near foreground along the bottom edge, large, dark and out of focus and seen from behind, are the rims of three or four battered shields and the tops of the helmets of weary soldiers crouched close together: "
          "the nearest of three hundred surrounded men, watching him come. "
          "Far behind him, beyond the ring, the long wall is a thin pale line on the horizon, and a vast pale column of light stands in the sky, the gods' war, too far to show any detail. "
          "On the ground between him and us a line of old broken spears lies in the dust. Ash and glowing sparks drift large and out of focus across the near corners."))

R['s16_f_rotrude'] = dict(
    why='背对镜头，脸扭过来过了九十度。改成从敌人这一边隔着花瓣看过去，她正面站着，右手低持剑、左手刚撒出去。',
    camera="low, from among the oncoming soldiers, looking through the hanging wall of petals up at her, the ropes and the tilted tower above her, tilted",
    sub=[(
        "In the middle foreground a tall spare woman who looks about fifty stands seen from behind at three-quarter, about 168 cm:",
        "In the middle of the picture a tall spare woman who looks about fifty stands facing the camera, seen from the front at three-quarter, about 168 cm, planted at the foot of the ropes with her feet apart:"),
        (
        "her long cherry-pink hair streaked with white and worn in one braid pinned at the end with a single dried rose,",
        "her long cherry-pink hair streaked with white and worn in one braid that hangs forward over one shoulder, pinned at the end with a single dried rose,"),
        (
        "She stands planted at the foot of the ropes, the thin sword in her right hand held low and ready, her left hand has just opened a cloth pouch at her belt and flung a handful of dried rose petals out across the front of her, so that each petal hangs in the air as a bright small blade, a wide curving wall of them between her and the enemy. Beyond the wall of petals a dark wave of horned soldiers surges across the sand toward the rope foot, spears raised, held at the edge of the petals. Behind her, a few steps back,",
        "Her right hand holds the thin sword low at her right side, the point toward the sand, ready. Her left arm is stretched out to her other side at the height of her shoulder with the hand open: "
        "she has just flung a handful of dried rose petals from the cloth pouch at her belt in a wide arc in front of her, so that each petal hangs in the air as a bright small blade, a broad curving wall of them between her and us. "
        "The enemy is on our side of that wall: in the near foreground, along the bottom edge and at the lower corners, dark and out of focus and seen from behind, are the horned helmets, the shoulders and the raised spears "
        "of the front of a wave of soldiers surging toward her across the sand, held at the edge of the petals. Behind her, a few steps back,")])

R['s20_f_wethlo'] = dict(
    why='背对镜头，两只手一起握剑伸向身子一侧，上身拧得厉害。改成正侧面朝右，双手一前一后握着同一个剑柄平举在胸前。',
    camera="low and wide from his right side, he in full profile at the left of the frame, looking along his levelled blade and its streak of red light toward the giant at the right, a slight tilt",
    sub=[(
        "In the near foreground on the left, the blood-demon vanguard, a tall lean demon who looks just past thirty, stands alone, seen from behind at three-quarter, in dull black leather armour with dark blood-red edges, short black hair showing a pair of very small horns, a narrow long sword with a row of fine blood grooves raised in a two-handed grip.",
        "In the near foreground on the left, the blood-demon vanguard stands alone in clean profile, facing RIGHT toward the giant and seen from his right side: a tall lean demon who looks just past thirty, "
        "in dull black leather armour with dark blood-red edges, short black hair showing a pair of very small horns. His feet are planted apart, both pointing right, the front knee a little bent. "
        "He holds a narrow long sword with a row of fine blood grooves straight out in front of him in both hands, the two hands one behind the other on the one hilt at the height of his chest, the elbows a little bent, the point levelled at the giant."),
        (
        "His left side from ribs to shoulder is an old burn scar half hidden by torn armour, fresh blood runs down his right hand to the hilt from an open cut across the fingertip, his face is pale with a faint bluish tinge and in profile,",
        "Fresh blood runs down the hand nearer to us to the hilt from an open cut across the fingertip; his face is pale with a faint bluish tinge and in profile,"),
        (
        "Behind and beside him in a ragged line far back,",
        "Behind him, at the left edge of the picture, in a ragged line far back and small,")])

R['s08_f_tirian'] = dict(
    why='胸背不分明，手臂偏长。改成正侧面朝左，近侧的左手扶弓，远侧的手垂着。',
    camera="level from his left side at the height of his waist, he in full profile at centre right, the wall face rising out of frame behind him, slightly tilted",
    sub=[(
        "the pale-haired elf archer stands on the walkway, seen from behind at three-quarter angle, tall and slender, looking out through a wide gap between two stone merlons toward the south. He looks about twenty-five, with long pale gold hair nearly white and a quiet ageless face turned a little toward the gap. His right arm hangs straight down at his side, relaxed, the sleeve loose, not hidden. His left hand rests on an old longbow whose lower tip is set against the stone, the deep right-hand-shaped grip mark in the wood clearly visible.",
        "the pale-haired elf archer stands on the walkway in clean profile, facing LEFT toward the south and seen from his left side, tall and slender, both feet side by side and pointing left, looking out through a wide gap between two stone merlons. "
        "He looks about twenty-five, with long pale gold hair nearly white and a quiet ageless face. An old longbow stands upright in front of him with its lower tip set on the stone, and his nearer hand, the left, rests on it at the height of his chest, "
        "the arm bent at the elbow; the deep hand-shaped grip mark in the wood is clearly visible. His farther arm hangs straight down at his side, relaxed; only its hand shows, below the edge of his cloak. His arms are of ordinary length."),
        (
        "Along his line of sight, very small and thin, one single long arrow is crossing the sunlit air toward him,",
        "Along his line of sight, far away to the left, very small and thin, one single long arrow is crossing the sunlit air toward him,")])

R['s10_f_toka'] = dict(
    why='背对镜头腾空，两条腿都在身后。改成纯背影，步子照真人跑步写。',
    camera="low and wide from the grass directly behind him, the horizon slightly tilted, the beast's body filling the foreground corner",
    sub=[(
        "In the middle ground the beast-eared hunter runs alone across the open grass toward them, seen from behind at three-quarter angle, mid-stride, his hands open at his sides and his waist bare where the rope was once wound.",
        "In the middle ground the beast-eared hunter runs alone across the open grass toward them, straight away from us, seen from directly behind: we see his back, the back of his head and his laid-back ears, and no part of his face. "
        "He is caught in a natural running stride: one leg forward and bent with the foot about to land, the other leg behind him pushing off the grass, the arms swinging opposite to the legs and bent at the elbows, the hands open; "
        "he is not leaping and both legs are the same length. His waist is bare where the rope was once wound.")])

R['s20_f_corenna'] = dict(
    why='不算错（她本来四条胳膊），可背影里只露出肋下一只拳头，像多出来的。改成正侧面朝右，上面一对举着引水，下面一对抱在胸前，四条都看得见。',
    camera="low and wide from her right side, she in full profile at the left of the frame with one foot over the salt line, the giant cut off by the top right of the frame, a slight tilt",
    sub=[(
        "In the near foreground on the left, the four-armed deep-tide woman stands seen from behind at three-quarter on the edge of the salt line, one foot stepping over it into the ring. She is tall, her blue-grey skin and fine scales salt-crusted. Her upper pair of arms is raised wide, fingers spread, pulling the sheet of sea water up and round; her lower pair is folded still against her chest. A thick dark green braid wet like kelp hangs down her back, a rolled tide chart at her waist, a bone sword with an unground edge strapped across her back, a salt-stiffened grey-green coat to the ankle.",
        "In the near foreground on the left, the four-armed deep-tide woman stands in clean profile on the edge of the salt line, facing RIGHT toward the ring and the giant and seen from her right side, her front foot stepping over the line into the ring, both feet pointing right. "
        "She is tall, her blue-grey skin and fine scales salt-crusted. She is not human and she has four arms, an upper pair and a lower pair, and all four are plainly seen, each from its own shoulder to its own hand. "
        "The upper pair grows from her shoulders: both upper arms are raised forward and high toward the wall of water, one a little above the other, fingers spread, pulling the sheet of sea water up and round. "
        "The lower pair grows from her sides just below the upper pair, under the armpits: both lower arms are folded still across the front of her chest, one forearm laid over the other. She has no other arms. "
        "A thick dark green braid wet like kelp hangs down her back, a rolled tide chart at her waist, a bone sword with an unground edge strapped across her back, a salt-stiffened grey-green coat to the ankle."),
        (
        "Behind her in a long column, small, other scaled blue-grey veterans of her people walk after her, none looking back.",
        "Behind her, to the left and further from us, in a long column, small, other scaled blue-grey veterans of her people walk after her toward the ring, none looking back.")])


def main():
    apply = '--apply' in sys.argv
    files = {}
    where = {}
    for p in sorted(glob.glob(os.path.join(HERE, 'g?.json'))):
        d = json.load(open(p, encoding='utf-8'))
        files[p] = d
        for s in d.get('falls', []):
            where[s['key']] = (p, s)
    done = [k for k in R if where[k][1].get('anat')]
    if done:
        print('这一轮已经跑过：', ' '.join(done))
        if len(done) == len(R):
            return
    for k, r in R.items():
        p, s = where[k]
        if s.get('anat'):
            continue
        old = s['text']
        if 'text' in r:
            s['text'] = r['text']
        for a, b in r.get('sub', []):
            assert s['text'].count(a) == 1, (k, a[:60], s['text'].count(a))
            s['text'] = s['text'].replace(a, b)
        for f in ('camera', 'light'):
            if f in r:
                s[f] = r[f]
        assert 'seen from behind at three-quarter' not in s['text'], k
        s['anat'] = 1
        s['note'] = (s.get('note', '') + '（11-13 人体那一轮：' + r['why'] + '）')
        print('%-16s %s  %d → %d 字' % (k, os.path.basename(p), len(old), len(s['text'])))
        print('    ', r['why'])
    if not apply:
        print('只报，没写盘。加 --apply 才写。')
        return
    for p, d in files.items():
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(d, ensure_ascii=False, indent=1) + '\n')
    moved = 0
    for k in R:
        a, b = os.path.join(OUT, k + '.png'), os.path.join(OUT, k + '_a0.png')
        if os.path.exists(a) and not os.path.exists(b):
            os.rename(a, b)
            moved += 1
    print('写了', len(files), '个文件，旧图挪成 _a0 的', moved, '幅')


if __name__ == '__main__':
    main()
