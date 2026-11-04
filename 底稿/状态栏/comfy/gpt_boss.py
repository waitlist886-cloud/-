#!/usr/bin/env python3
# 史诗战的 Boss 立绘（11-04）。一阶段一张，2:3，写 out/四方_11-03/boss/<英文名>.png，已有的不重出；转 webp 写 art_fu_ab/boss_<英文名>.webp（要 PIL，用 ComfyUI 那个 venv 的 python）。
#   python gpt_boss.py [英文名…]
#   python -c "import gpt_boss; gpt_boss.webp('yanzuo1')"
# 长相照底卡各楼层主条目写，同一位的几阶拿 yanzuo.png 这样的第一张当参考，人和构图才连得上。不露脸的阶段不露脸。
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
    # 三阶：传奇们的化身，无缘黎明的殉道者。甲碎尽，一个完美的魔族，各族的特征匀称地长在同一副身子上；她睁开眼睛，神志回来了，点燃剑上的赤焰。不是巴尔缇娜的样子
    'yanzuo3': (SAME + 'This is the final form: the black armour has shattered completely and its fragments are falling away. Inside stands not a monster but a solemn, dignified adult demon woman warrior, the perfect image of all demon-kin at once: two curved horns with flame-pattern markings along them, ember tattoos of flame on her neck and hands, a slender demon tail, armour of iridescent sea-scale mail covering her shoulders and body like a knight, and an enormous, magnificent, austere pair of iron-scaled wings. Long dark hair with ember-red tips. Her eyes are open now, clear and amber-red, her sanity has returned; the expression is calm, sorrowful and resolved, no malice at all. She holds the great sword with a clean crimson flame newly lit along the blade. A pale dawn-like glow behind her from the point of light. Ash and embers floating upward, a feeling of a martyr. Not sexualized, fully armoured, heroic.', ('yanzuo',)),
}


def job(name):
    os.makedirs(OUT, exist_ok=True)
    prompt, refs = BOSS[name]
    return gpt_gen.gen(os.path.join(OUT, name), STYLE + prompt, refs=[os.path.join(OUT, r + '.png') for r in refs])


def webp(name, width=560, quality=62):
    from PIL import Image
    im = Image.open(os.path.join(OUT, name + '.png')).convert('RGB')
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)   # 样式里最宽显示四百多像素
    p = os.path.join(ART, 'boss_%s.webp' % name)
    im.save(p, quality=quality, method=6)
    print(name, im.size, os.path.getsize(p) // 1024, 'KB')


if __name__ == '__main__':
    names = sys.argv[1:] or list(BOSS)
    for n in names:
        print(n, job(n), flush=True)
