#!/usr/bin/env python3
# 山铜纪两扇的人（11-05）：一个人一个假人（mannequin.py），比例和姿势这边定，GPT 只穿衣服上色，出来抠成透明，一层一层贴。用户看了假人说姿势还是怪，手脚都摊在一个平面上，所以只留下薇丝塔、矮人王、瓦尔德拉克这三个，别的人不用假人（gpt_bronze.py 的 DYN）。
#   python bronze_poses.py sheet 输出.jpg        把假人摆到底图上看
#   python bronze_poses.py refs                  写 ref/man_<名字>.png，给 gpt_bronze.py 用
# root 是骨盆在两扇原图上的位置（1049×1500 那一套像素，左扇接着 left3），u 是头高。canvas、cu、croot 是给 GPT 那张底稿的尺寸、头高、骨盆位置。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
from PIL import Image
from mannequin import draw

ROOT = os.path.join(HERE, 'out', '山铜纪_11-04')
L, R = 1, -1


def turned(deg):
    """身子往图的左边转多少度：a 那一头（图的左边）往后退。回 (横轴, 胸口朝向)。"""
    import math
    t = math.radians(deg)
    return (-math.cos(t), 0, -math.sin(t)), (-math.sin(t), 0, math.cos(t))


# 东陆的人都朝窗口那边（图的左边）。a 是图上靠左的胳膊和腿
RIGHT = {
    # 白鸦的头：矮壮，往左一个大弓步。前腿弯，后腿蹬直，身子压过去，细剑平着刺出去，另一只手攥着旗杆，旗杆往后斜
    'vesta': dict(kind='stocky', root=(445, 1150), u=68, canvas=(1536, 1024), cu=118, croot=(860, 540),
                  spine=((-.32, .94, 0), (-.46, .88, .05)), hips=(-.8, -.06, -.58), shoulders=(-.72, -.2, -.66), neck=(-.42, .9, .1), head=(-.18, .98, .02), face=(-.86, .08, .5),
                  arm_a=((-.92, .28, .25), (-.97, .2, .1), (-.98, .16, .05)), arm_b=((.1, -.62, .78), (.22, .86, .45), (.12, .95, .2)),
                  leg_a=((-.86, -.46, .22), (-.1, -.99, 0), (-.9, -.05, .4)), leg_b=((.62, -.76, .18), (.82, -.56, -.05), (.3, -.55, .75)),
                  props=[('wra', (-.97, .22, .05), .25, 3.3, .07, (150, 110, 60)), ('wrb', (.2, .98, 0), 2.6, 3.4, .13, (120, 80, 50))]),
    # 矮人王：往前压着打铁。近的那条胳膊把大锤抡到头上，远的那只手拿长钳夹着砧上的铁条
    'brom': dict(kind='dwarf', root=(235, 1400), u=80, canvas=(1024, 1024), cu=120, croot=(640, 640),
                 spine=((-.2, .98, .05), (-.32, .94, .1)), hips=(-.86, .03, -.5), shoulders=(-.8, -.1, -.58), neck=(-.45, .88, .15), head=(-.22, .97, .05), face=(-.85, -.18, .5),
                 arm_a=((-.72, -.55, .42), (-.92, -.3, .2), (-.95, -.25, .1)), arm_b=((.42, .82, .38), (-.28, .95, .1), (-.5, .85, .1)),
                 leg_a=((-.35, -.93, .1), (-.1, -.99, 0), (-.8, -.05, .6)), leg_b=((.3, -.95, .1), (.15, -.98, -.05), (.1, -.05, .99)),
                 props=[('wrb', (-.72, .68, .1), .35, 1.65, .2, (120, 80, 50)), ('wra', (-.9, -.42, .1), .1, 1.5, .1, (60, 60, 66))]),
}


# 魔族那一边朝窗口是往图的右边，七个人各拆各的那一尊
LEFT = {
    # 瓦尔德拉克：跪在石臂上，一条腿跪着、一条腿支起来，两只手把长柄大刀往下压，肩膀弓着，头抬起来
    'valdrak': dict(kind='man', root=(735, 298), u=48, canvas=(1024, 1024), cu=118, croot=(430, 470),
                    spine=((.2, .95, .2), (.42, .86, .28)), hips=(-.82, 0, .57), shoulders=(-.8, .05, .6), neck=(.38, .9, .2), head=(.1, 1, .05), face=(.55, .08, .83),
                    arm_a=dict(to=(787, 262, .6), pole=(-.3, -1, .3), hand=(.3, .1, -.9)), arm_b=dict(to=(795, 305, .4), pole=(.5, -.6, .4), hand=(.3, .1, -.9)),
                    leg_a=((-.25, -.96, .1), (-.97, -.12, -.2), (-.25, -.95, 0)), leg_b=((.84, -.38, .38), (.04, -.99, .1), (.88, -.1, .45)),
                    props=[('wra', (.14, -.99, 0), 1.0, 3.2, .17, (120, 80, 50))]),
}


def refs(table=RIGHT):
    os.makedirs(os.path.join(ROOT, 'ref'), exist_ok=True)
    for n, f in table.items():
        g = dict(f)
        g['lroot'], g['lu'] = f['root'], f['u']
        g['root'], g['u'] = f['croot'], f['cu']
        im, _ = draw(f['canvas'], [g])
        im.save(os.path.join(ROOT, 'ref', 'man_%s.png' % n))


def sheet(out, base='plate7.png', table=RIGHT, hero=True):
    """所有假人摆到底图上：底图、假人都按图的像素。假人的底透明，颜色跟 draw 一样。"""
    import numpy as np
    plate = Image.open(os.path.join(ROOT, base)).convert('RGB')
    W, H = plate.size
    c = plate.convert('RGBA')
    if hero:
        t = Image.open(os.path.join(ROOT, 't3.png')).convert('RGBA')
        s, hx, hy = HERO
        f = t.resize((int(t.width * s), int(t.height * s)), Image.LANCZOS)
        c.alpha_composite(f, (int(hx - 473 * s), max(int(hy - 476 * s), 0)), (0, max(-int(hy - 476 * s), 0)))
    for n, f in table.items():
        im, _ = draw((W, H), [f], bg=(255, 0, 255))
        a = np.asarray(im).astype(int)
        mask = (abs(a[..., 0] - 255) + a[..., 1] + abs(a[..., 2] - 255)) > 60
        rgba = np.dstack([a, mask * 255]).astype('uint8')
        c.alpha_composite(Image.fromarray(rgba, 'RGBA'))
    c.convert('RGB').save(out, quality=90)


HERO = (.6, 440, 425)      # t3 缩放多少，手放在图的哪里

if __name__ == '__main__':
    if sys.argv[1] == 'refs':
        refs(RIGHT)
        refs(LEFT)
    elif sys.argv[1] == 'sheetl':
        sheet(sys.argv[2], base=sys.argv[3], table=LEFT, hero=False)
    else:
        sheet(sys.argv[2])
