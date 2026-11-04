#!/usr/bin/env python3
# 史诗战的 Boss 立绘（11-04）。一阶段一张，2:3，写 out/四方_11-03/boss/<英文名>.png，已有的不重出；转 webp 写 art_fu_ab/boss_<英文名>.webp（要 PIL，用 ComfyUI 那个 venv 的 python）。
#   python gpt_boss.py [英文名…]
#   python -c "import gpt_boss; gpt_boss.webp('yanzuo1')"
# 长相照底卡各楼层主条目写，同一位的几阶拿 yanzuo.png 这样的第一张当参考，人和构图才连得上。不露脸的阶段不露脸。
# 参考图：写英文名是 boss/ 下那一张，带斜杠的是相对这个文件夹的路径（refs/ 下用户给的长相图）。
# 新添一位：这里添一行，大框/boss_art.json 添「名号 → {"1": "__ART__/boss_英文名1.webp", ...}」，只有一张的写成字符串。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_gen

OUT = os.path.join(HERE, 'out', '四方_11-03', 'boss')
ART = os.path.join(HERE, 'out', '四方_11-03', 'art_fu_ab')
STYLE = ('Vertical key art of a boss for a high-end Japanese fantasy action RPG, the splash picture shown when the boss fight begins. Rich painterly anime rendering with crisp line art, dramatic rim light, deep shadows, an ominous and beautiful mood. '
         'The figure is huge, seen slightly from below, head and shoulders in the upper third of the picture, filling the height. Portrait picture, aspect ratio 2:3. No text, no logo, no frame, no signature. ')
SAME = 'The attached picture is the same character and setting: keep the same pose, the same framing, the same throne on the spiral ruin behind. Only change what is described here. '
# 底卡「黑潮螺旋城·楼层主战」：往里屈的角冠，一整片没有开孔的面甲，背后一对铁鳞的翼，巨大的黑曜石板甲和巨剑，王座后面一点光把他衬成黑影
YANZUO = 'A false demon king standing before a dark throne on a spiral ruin: immense obsidian plate armour, perfectly symmetrical and handsome in its menace; a black horned crown whose horns curve inward; a pair of iron-scaled wings spread behind him; both gauntlets resting on a colossal black greatsword. Far behind him a single tiny point of pale light in the darkness makes him a looming silhouette. '
BOSS = {
    # 最早那一张，只拿来当另外三张的参考，不进卡
    'yanzuo': (YANZUO + 'A single smooth full-face visor with no eye holes at all, the face completely hidden. Crimson lotus hellfire leaks from the seams of the armour and runs along the cracks like a burning net; the edge of the sword glows red-hot. Falling embers, cracked black stone.', ()),
    # 一阶：弑君，弑神，焚天的魔王。狰狞、庞大、端正，还没有火
    'yanzuo1': (SAME + YANZUO + 'This is his first form: there is NO fire and NO glowing cracks anywhere. The armour is whole, cold, flawless black obsidian with a faint pale rim light; a single smooth full-face visor with no eye holes, the face completely hidden. The sword is cold black stone. Cold blue-black shadows, drifting ash, an icy, absolute calm.', ('yanzuo',)),
    # 二阶：至暗之剑，身引红莲的柴薪。板甲崩开，业火从甲缝里溢出来，碎掉一半的头盔里露出那张脸
    'yanzuo2': (SAME + YANZUO + 'This is his second form: the plate armour has burst open, crimson lotus hellfire pours from the seams and runs along the cracks so the whole suit becomes a red-hot burning net, the great sword burns red from fuller to tip. The left half of the helmet has shattered and fallen away, revealing half of a pale, strangely familiar, beautiful androgynous face with a closed eye; the right half is still the smooth black visor. He looks like he is being burned as he walks forward. Falling embers, flames on the ground.', ('yanzuo',)),
    # 11-04 用户：二三阶要有区别，三阶长相基本照巴尔缇娜，甲应该完全碎了。yanzuo2、yanzuo3 是头一版，留作记录，不进卡；现行的是 yanzuo1、yanzuo2d、yanzuo3d
    # 试过不要的：二阶从脚下仰拍，一条腿画得巨大，人压小了；三阶写成 sea-scale mail，画成一整身铠甲。底卡「海魔和赛壬的鳞甲」说的是长在身上的鳞，这一阶甲已经碎尽了
    'yanzuo2c': ('The attached picture shows the same character: keep his obsidian plate armour, the black horned crown with inward-curving horns, the iron-scaled wings and the spiral ruin. New pose and framing: he walks toward the viewer in one slow, heavy, relentless step. Natural human proportions and a calm camera: only a slightly low angle, NOT an extreme low-angle view, NO huge foreshortened leg, NO distorted anatomy; the head and shoulders are large and clear. Three-quarter view with the body turned slightly to one side, framed from the thighs up so that the upper body fills the picture, the head in the upper third, slightly right of centre. '
                 'One hand holds the colossal greatsword low at his side, its blade angled down and trailing behind him, burning red from the fuller to the tip; the other arm hangs at his side with an open gauntlet. Both wings are half spread behind him, one of them burning along its edge and trailing sparks. '
                 'This is his second form: the armour has cracked open, crimson lotus hellfire leaks from the seams and runs along the cracks like a burning net, a few plates are breaking off and falling, but the armour is still mostly solid black and clearly readable as armour, so that black metal and orange-red fire stand in clean contrast. '
                 'The left half of the helmet has shattered and fallen away, revealing half of a pale, beautiful, expressionless face with one closed eye and a few loose strands of ash-silver hair; the other half is still the smooth black visor, following the natural shape of a helmet, under the horned crown. He looks like he is being burned as he walks forward, and he does not stop. '
                 'The background stays nearly black and cold blue-black, the dark spiral ruin barely visible with one tiny far point of pale light; only the figure burns, the sky is NOT red.', ('yanzuo1',)),
    'yanzuo3d': ('Two attached pictures. The FIRST shows the woman, and her face must match it as closely as possible: the same longer, narrower face with a small sharp chin, the same large upturned golden amber eyes with dark upper lashes, the same straight thin nose and small closed mouth, the same blunt straight bangs, the same very long cool silver-white hair with a small braid running along the side of the head, the same pointed ears, the same cold pale skin, a tiny red diamond mark on her forehead, the same long drop earrings. Her hair is cool silver-white with grey shadows, NOT beige, NOT cream, NOT gold. '
                 'The SECOND picture is used ONLY for the great iron-scaled wings, the black greatsword and the black armour that is now breaking apart; do not copy its pose or its colours. '
                 'This is the final form of a false demon king: the black armour has shattered completely and NONE of it remains on her body. No breastplate, no pauldrons, no gauntlets, no greaves, no scale armour, no mail, no armour of any kind. The last black fragments of the shell hang and float in the air all around her, drifting away and dissolving into ash. What stood inside it is a solemn, dignified adult demon woman in a plain, modest, floor-length black dress with a high collar and long sleeves, its hem a little torn, with a narrow dark gold belt at the waist. '
                 'The demon traits grow naturally from her own body, and only a little of each: two elegant dark curved horns with fine flame-pattern markings rising through her silver hair; thin ember-like flame markings on the side of her neck and the backs of her hands; a slender tail; a few small patches of iridescent pearl sea-scales growing directly from her skin at the temples and along the sides of her neck and on the backs of her hands; and an enormous, magnificent, austere pair of iron-scaled wings growing from her back, half open. '
                 'Composition: NOT symmetrical, NOT frontal. Three-quarter view from the thighs up, natural proportions, the body turned slightly, the head a little tilted, looking straight at the viewer. Her face is large and sharp, in the upper third of the picture, about one fifth of the height of the picture, slightly right of centre. The expression is calm and grave with the faintest sorrow, as if she has just given a quiet sigh; the mouth is closed; her sanity has returned; no malice at all. '
                 'She holds the colossal greatsword lowered in one bare hand, its point near the ground beside her, and a clean crimson flame has just been lit along the blade: that flame is the ONLY saturated red in the whole picture. '
                 'Light and colour are the opposite of a hellscape: the single point of light behind her has become a wide dawn over the spiral ruin, a cool, slightly deep pearl-blue sky at the top fading to pale gold lower down, so that her silver hair stands out clearly against it. Luminous and high-key, with the black dress and the black fragments as the strong dark accents. A martyr at peace, beautiful and sorrowful. Not sexualized, modest and fully covered. NO fire on the ground, NO red sky.', ('refs/巴尔缇娜_用户_11-03.webp', 'yanzuo1')),
    # 2c 比例对了，火太收，底卡要的是一整身甲勾成烧红的网。姿势、比例、头盔和半张脸不动，只把火加上去
    'yanzuo2d': ('The attached picture is the finished illustration: keep its composition, pose, natural proportions, horned crown, half-shattered helmet, half of the pale face with the closed eye and the silver hair, the wings and the dark background exactly as they are. Only make the fire much stronger on the figure itself. '
                 'The plate armour has burst open: plates on the chest, shoulders, arms and thighs are splitting and lifting away from the body, and crimson lotus hellfire pours out of every seam and gap. The cracks now run over the whole suit like one red-hot burning net, glowing orange at the core and crimson at the edges, with lotus-shaped flames rising from the shoulders and the chest and licking up along the arms. The greatsword burns red-hot from the fuller to the tip. One wing burns along its whole lower edge, trailing sparks. Embers stream backward from his body as he walks. '
                 'He still reads clearly as a figure in black armour, with black metal and orange-red fire in hard contrast. The background stays cold and nearly black, the sky is NOT red, and the half face is NOT covered by flames.', ('yanzuo2c',)),
    # 月银纪·焚原（第七歌那一条灾祸之兽）：红鳞古龙，飞龙远裔，不是真龙。一段盘城，二段飞上高处，火在头顶烧成一圈，名号缀一个冠字。画里还没有断刃，那是它死的时候才有的
    'fenyuan1': ('The attached picture shows a red-scaled ancient dragon in its lower part: use that dragon as the reference for the look of the scales and the head, but it is alive here, and there is NO blade, NO sword and NO spike stuck in its head or skull. Ignore the other beasts in that picture. '
                 'An ancient red-scaled wyrm, old and enormous, a far descendant of wyverns and not a noble true dragon: a long heavy head with a jagged crest of burnt-red scales, a bare head with no crown of any kind, small burning eyes half closed with contempt. Its body is coiled around a walled stone city as though the whole city were its throne, and its huge chin rests on the top of the gate tower, whose stone is cracking and glowing. One vast wing is half spread behind it, so wide that the whole sky behind is lit dull red. A slow breath of fire leaks from the corner of its jaws, and the fire is half red and half pure black. One scale patch under its throat is dark and thin. Very small human figures stand on the wall below for scale, none of them detailed. Fields of blackened wheat in the far distance. The head is in the upper third of the picture and looks down at the viewer. Cold blue dawn sky at the very top edge, everything below it burning. ', ('out/月银纪_11-04/left.png',)),
    'fenyuan2': ('The attached picture shows the same dragon: keep the same head, the same burnt-red scales and the same crest, and there is NO blade stuck in its head. New scene: it has climbed high into the air above the clouds and hangs there with both vast wings fully open, its head lifted and turned down toward the viewer, ready to dive. Above its head fire burns in a perfect floating ring, a crown of flame that touches nothing. Far below, every fire on the burnt plain leans toward it like wheat in the wind, long streaks of flame bending up toward the ring. The wing membrane has an arrow hole in it, and the wounds in its body do not bleed: they seep black, dripping and smoking. Half of the flame on its body is black. It is magnificent and insane with pride. Cold deep sky around it, the red light comes only from the ring and from the plain far below. ', ('fenyuan1',)),
    # 三阶第一版（留作记录）：不是巴尔缇娜的样子
    'yanzuo3': (SAME + 'This is the final form: the black armour has shattered completely and its fragments are falling away. Inside stands not a monster but a solemn, dignified adult demon woman warrior, the perfect image of all demon-kin at once: two curved horns with flame-pattern markings along them, ember tattoos of flame on her neck and hands, a slender demon tail, armour of iridescent sea-scale mail covering her shoulders and body like a knight, and an enormous, magnificent, austere pair of iron-scaled wings. Long dark hair with ember-red tips. Her eyes are open now, clear and amber-red, her sanity has returned; the expression is calm, sorrowful and resolved, no malice at all. She holds the great sword with a clean crimson flame newly lit along the blade. A pale dawn-like glow behind her from the point of light. Ash and embers floating upward, a feeling of a martyr. Not sexualized, fully armoured, heroic.', ('yanzuo',)),
}


def job(name):
    os.makedirs(OUT, exist_ok=True)
    prompt, refs = BOSS[name]
    return gpt_gen.gen(os.path.join(OUT, name), STYLE + prompt, refs=[os.path.join(HERE, r) if '/' in r else os.path.join(OUT, r + '.png') for r in refs])


def webp(name, width=560, quality=62, art=ART):
    from PIL import Image
    im = Image.open(os.path.join(OUT, name + '.png')).convert('RGB')
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)   # 样式里最宽显示四百多像素
    p = os.path.join(art, 'boss_%s.webp' % name)
    im.save(p, quality=quality, method=6)
    print(name, im.size, os.path.getsize(p) // 1024, 'KB')


if __name__ == '__main__':
    names = sys.argv[1:] or list(BOSS)
    for n in names:
        print(n, job(n), flush=True)
