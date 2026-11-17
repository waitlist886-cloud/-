#!/usr/bin/env python3
# 世界之书换装（11-17 前端精修）：每一章章首的横幅、每一卷扉页的小画，从各本书现成的图里裁，
# 写 共用/assets/wb/*.webp 和 共用/data/wb_dress.json。带 PIL 的 Python 跑：python prep_wb.py
# 挑哪一幅是主会话定的（★），改了这张表重跑就行。地图那一章不要横幅（地图自己就是图）。
import io
import json
import os
import sys

from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.normpath(os.path.join(HERE, '..'))
OUT = os.path.join(HERE, 'assets', 'wb')
BW, BH = 1080, 360          # 横幅 3:1
FW, FH = 640, 860           # 扉页的小画


def src(name):
    for d in ('小样_月银纪书/assets/cg', '小样_纷争纪书/assets/cg', '小样_山铜纪书/assets/cg', '小样_迷宫纪书/assets/mural', '小样_外壳/assets', '小样_牌桌/assets'):
        p = os.path.join(FRONT, d, name + '.webp')
        if os.path.exists(p):
            return p
    raise SystemExit('没有这一幅：' + name)


def crop(im, w, h, fy=.5, fx=.5):
    sw, sh = im.size
    s = max(w / sw, h / sh)
    im = im.resize((round(sw * s), round(sh * s)), Image.LANCZOS)
    x = round((im.width - w) * fx)
    y = round((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def strips(names, w, h, fy=.5):
    """几幅图各取当中一竖条拼成一幅（四纪编年、一卷的编年：头一幅接末一幅）"""
    n = len(names)
    out = Image.new('RGB', (w, h))
    sw = w // n
    for k, nm in enumerate(names):
        im = crop(Image.open(src(nm)).convert('RGB'), sw if k < n - 1 else w - sw * (n - 1), h, fy)
        out.paste(im, (k * sw, 0))
    return out


# 卷 → 章 → 图（字符串是一幅；('pair', 甲, 乙) 头尾两幅各取一半；('quad', …) 几幅各取一竖条；第三个数是取景的高低）
BAN = {
    'general': {'arrive': ('bg', .42), 'ages': ('quad', 'era_0', 'era_1', 'era_2', 'era_3'), 'races': ('s07_era', .62),
                'ranks': ('m23_era', .32), 'gods': ('s19_era', .3)},
    'moon': {'age': ('era_0', .45), 'realms': ('m24_era', .5), 'gods': ('m16_era', .3), 'beasts': ('m11_era', .45),
             'names': ('m09_era', .45), 'life': ('m13_era', .55), 'chron': ('pair', 'm01_era', 'm27_era')},
    'strife': {'age': ('era_1', .4), 'realms': ('s09_era', .6), 'demons': ('s03_era', .4), 'gods': ('s20_era', .5),
               'paths': ('s11_era', .55), 'arms': ('s13_era', .62), 'life': ('s05_era', .6), 'chron': ('pair', 's01_era', 's21_era')},
    'bronze': {'age': ('era_2', .1),'realms': ('e4', .55), 'west': ('e5', .5), 'gods': ('e3', .5), 'ruins': ('e1', .4),
               'trade': ('e2', .6), 'life': ('e6', .6), 'chron': ('pair', 'e1', 'e6')},
    'maze': {'age': ('era_3', .55), 'realms': ('q0_a', .6), 'guild': ('q1_a', .6), 'well': ('q4_a', .45), 'tide': ('q5_a', .4),
             'life': ('q2_a', .6), 'today': ('q6_a', .5), 'chron': ('pair', 'q0_a', 'q6_a')},
}
FRONTIS = {'general': ('table', .5), 'moon': ('era_0', .5), 'strife': ('era_1', .5), 'bronze': ('era_2', .5), 'maze': ('era_3', .5)}
# 每一卷头一章的题记：月银纪、纷争纪取合篇题诗的头一行和末一行，山铜纪、迷宫纪前传取旅印合篇头一章的章描述，通用卷取神殿的头一句
EPI = {
    'general': ['生者自有去处，亡魂也有归程。', '死之神殿 · 头一句'],
    'moon': ['长夜啊，把春天还给灰桥。', '向长夜索春 · 题诗第一行'],
    'strife': ['孩子啊，天亮以前火永不熄。', '向长夜索春 · 题诗末一行'],
    'bronze': ['灰雨城的门洞里燃着一罐火，火畔摆着几只摇篮，等人在天黑以前来领。', '奥尔德兰的旅印 · 上部序章《火畔的摇篮》'],
    'maze': ['井口边的人放下绳，又放下更长的绳，向黑暗里唱一声，阿卡迪亚接着。', '奥尔德兰的旅印 · 中部序章《更长的绳》'],
}


def main():
    os.makedirs(OUT, exist_ok=True)
    dress = {'v': 1, 'ban': {}, 'front': {}, 'epi': EPI}
    for vol, pages in BAN.items():
        for pid, spec in pages.items():
            if spec[0] == 'quad':
                im = strips(list(spec[1:]), BW, BH, .45)
            elif spec[0] == 'pair':
                im = strips([spec[1], spec[2]], BW, BH, .5)
            else:
                im = crop(Image.open(src(spec[0])).convert('RGB'), BW, BH, spec[1])
            name = '%s_%s' % (vol, pid)
            im.save(os.path.join(OUT, name + '.webp'), quality=80, method=6)
            dress['ban'].setdefault(vol, {})[pid] = name
    for vol, (nm, fy) in FRONTIS.items():
        im = crop(Image.open(src(nm)).convert('RGB'), FW, FH, fy)
        im.save(os.path.join(OUT, vol + '_front.webp'), quality=80, method=6)
        dress['front'][vol] = vol + '_front'
    json.dump(dress, open(os.path.join(HERE, 'data', 'wb_dress.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print('横幅', sum(len(p) for p in dress['ban'].values()), '扉页', len(dress['front']), '共 %.1f KB' % (tot / 1024))


if __name__ == '__main__':
    main()
