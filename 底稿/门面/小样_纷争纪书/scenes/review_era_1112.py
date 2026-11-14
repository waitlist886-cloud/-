#!/usr/bin/env python3
# 主会话审二十一幅时代原画的场面以后改的（2026-11-12）。跑过一回旧串就没了，再跑会停。
#   python -I -X utf8 review_era_1112.py
# 改了什么：
#   诺伦在第四、五、六、七、十二张里，一律写成整个头罩在狮首闭盔里、看不见头发和脸（头一张试图把盔上的金鬃画成了金发、露了侧脸）；第四张开场时他还没在赤原受冠，写成骑士。
#   第六张火边改成两个并排坐着的兵，一个腰上金柄的刀、一个铁刀（牌文：东撤的前一夜拿金柄的刀换了他的铁刀），原稿写的老魔族膝上横着金刀是起稿的人自己添的。
#   第七张“桌边”原稿没有桌子。第十张举盾的神写明没有光环。
#   第十三张神杀炮照页上写成刻满符文的铜炮（原稿写成魔晶炮）；3046 年拜恩还没叫七柱碑前那七个人伤过，角是全的，胸口也没有东门的火；天上远处的几位神拿掉，换成很小的一匹有翅膀的白马（头一张试图把主画里的三位神连弓搬了进来）。
#   第十五张不写碗，写手里倒扣的杯。第十六张夜里的小圆日轮容易画成月亮，拿掉。
#   第十七张画的是七柱碑以前：拜恩的角和眼都是全的，火边六个人、空着一个位子（第七个人前一夜才到）。
#   第十九张芙莉莲写成 elf woman。
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'era_scenes.json')
HELM = "his whole head enclosed in a closed great helm shaped like a lion's head, so that no hair, no face and no skin can be seen at all"

REPS = {
    's04_era': [
        ("a helmed emperor in bright silver plate armor, a closed lion-faced helm with a gold mane, a long white fur-collared cloak and a sword longer than a man held point-down, seen from behind and never showing his face;",
         "a tall knight in bright silver plate armor seen from behind, " + HELM + ", a long white fur-collared cloak hanging from his shoulders and a sword longer than a man held point-down;"),
    ],
    's05_era': [
        ("and a helmed rider in white-trimmed silver armor beside the cart, back to us, his lion-faced helm tilted toward the door.",
         "and a knight in white-trimmed silver armor standing beside the cart with his back to us, " + HELM + ", the helm tilted toward the door."),
    ],
    's06_era': [
        ("a tired helmed emperor in silver plate armor on a tired white horse, face never shown, his great sword leaning against the stirrup; an old horned demon man holding a flat golden blade across his knees beside a plain iron blade;",
         "an emperor in silver plate armor on a tired white horse, seen from behind, " + HELM + ", his great sword hanging at the saddle; a young soldier and a hooded horned soldier sitting side by side at the fire, one with a gold-hilted knife at his belt and the other with a knife of plain iron;"),
        ("a little pale gold on the golden blade,", "a little pale gold on the gold-hilted knife,"),
    ],
    's07_era': [
        ("Beside the table a helmed emperor in silver armor with a closed lion-faced helm stands with his back to us.",
         "Beside them an emperor in silver armor stands with his back to us, " + HELM + "."),
    ],
    's10_era': [
        ("with only a thin pale gold on the shield rim;", "with only a thin pale gold on the shield rim and no halo round his head;"),
    ],
    's12_era': [
        ("A single helmed emperor, a tiny figure in white-trimmed silver armor, stands on the edge of the field with his lion-faced helm lowered, his back to us, watching them.",
         "At the edge of the field one tiny knight in white-trimmed silver armor stands with his back to us, " + HELM + ", watching them go."),
    ],
    's13_era': [
        ("a huge dwarf-forged crystal cannon on a many-wheeled carriage, its long muzzle raised to the south",
         "a huge dwarf-forged bronze cannon on a many-wheeled carriage, its barrel as long as a ship and carved from breech to muzzle with fine lines of runes, its muzzle raised to the south"),
        ("broad as a ridge, with a faint gate of dull light in its chest, drawn", "broad as a ridge, both of its long horns whole, drawn"),
        ("Behind and above it a few pale gods stand far off in the sky, small by comparison.",
         "Far off on the left of the sky one tiny winged white horse with a rider crosses, the only other thing in the sky."),
        ("pale gold on the far gods,", "pale gold on the far winged horse,"),
    ],
    's15_era': [
        ("a tall demon woman with dark red eyes holding a bowl she does not drink from;", "a tall demon woman with dark red eyes, the cup in her hand turned upside down;"),
    ],
    's16_era': [
        (" A pale yellow sun disc hangs low at the very edge of the horizon, small and round.", " Far to the south a dull red glow lies along the whole horizon."),
        ("pale gold on the far sun disc,", "pale gold on the edges of the nearest tower,"),
    ],
    's17_era': [
        ("with seven tiny, simply drawn people of seven peoples around it:", "with six tiny, simply drawn people of six peoples around it and one place at the fire left empty:"),
        ("its left horn broken short and its right eye an empty dark socket, hands the size of towers hanging open", "both of its long horns whole, hands the size of towers hanging open"),
    ],
    's19_era': [
        ("a slim silver-haired elf girl with two long tails of hair,", "a slim silver-haired elf woman with two long tails of hair,"),
    ],
}

d = json.load(open(P, encoding='utf-8'))
n = 0
for k, reps in REPS.items():
    t = d[k]['text']
    for a, b in reps:
        assert t.count(a) == 1, (k, a[:50], t.count(a))
        t = t.replace(a, b)
        n += 1
    d[k]['text'] = t
for k, v in d.items():
    low = v['text'].lower()
    for w in ('moon', 'crescent', 'rifle', 'pistol', 'musket', 'halo'):
        if w in low and not (w == 'halo' and 'no halo' in low):
            print('注意', k, w)
    print(k, len(v['text'].split()), '词')
json.dump(d, open(P, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print('改了', n, '处')
