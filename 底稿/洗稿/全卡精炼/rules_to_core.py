#!/usr/bin/env python3
# 全卡精炼洗稿：把各条里抄了上千遍的那几句通用规矩，写进四纪各自的常驻条目（11-16）。
#   python -I -X utf8 底稿/洗稿/全卡精炼/rules_to_core.py [--apply]
# 洗稿时这几句从条目里拿掉（洗稿说明第二节第 6 条），常驻每轮都在，规矩不丢。写过的跳过，跑多少回都一样。
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
MARK = '条目里写的经过、默认收束和正史里的下场'

BULLETS = """- {MARK}，是玩家不在场、不插手时的样子。玩家在场插手了，照玩家做的事走，能出手，能救人，能改，分量和代价照这一纪的尺度。{REC}记的是正史，这一局改了的，往后照改了的{REDO}。
- 玩家一直没碰上的人，下场照正史发生。正史里的下场是底，叙述里不点破，也不拿它吓玩家。玩家跟谁到了已识以上，他往后的事看这一局，他自己拿的主意也照这一局算。
- 分时段写的条目只取底座年份所在的那一段，往后的事不提前说，人物嘴里也不说。
- 旅伴条和人物条不分潮汐，潮汐格写主线、幕间、收束还是自由都用。
- 条目里写了共战点、协战的，照战斗规则打。羁绊的章一轮只推一步，后面的事不预告。"""

JOBS = [
    # 文件，这一纪记正史的东西，改了以后怎么说，插在哪一句后头（整行），写成列表还是一段
    ('纷争纪/补卷/第一项_常驻与纪元钟.md', '歌、牌、战报和伤亡册', '唱、照改了的记',
     '- 锁管的是主持的 AI，不乱编，不自己改正史，不管玩家。玩家在场插手了，照玩家做的事走。', 'list'),
    ('山铜纪/补卷/第一项_常驻与纪元钟.md', '碑和号墙', '刻',
     '- 锁管的是主持的 AI，不乱编，不自己改正史，不管玩家。玩家在场插手了，照玩家做的事走。', 'list'),
    ('迷宫纪前传/补卷/第一项_常驻与纪元钟.md', '委托单、深度板和未归板', '记',
     '- 锁管的是主持的 AI，不乱编，不自己改正史，不管玩家。玩家在场插手了，照玩家做的事走。', 'list'),
    ('moon/batch1/g1_core.md', '歌和传唱', '唱', '## 裁定锁', 'para'),
]


def main():
    apply = '--apply' in sys.argv
    for f, rec, redo, anchor, kind in JOBS:
        p = os.path.join(ROOT, f)
        raw = open(p, encoding='utf-8', newline='').read()
        nl = '\r\n' if '\r\n' in raw else '\n'
        s = raw.replace('\r\n', '\n')
        if MARK in s:
            print('写过了，跳过', f)
            continue
        text = BULLETS.replace('{MARK}', MARK).replace('{REC}', rec).replace('{REDO}', redo)
        lines = s.split('\n')
        idx = [i for i, l in enumerate(lines) if l == anchor]
        assert idx, ('找不到落脚的那一行', f, anchor)
        i = idx[0]                                   # 都落在头一条（常驻）里
        if kind == 'list':
            lines[i + 1:i + 1] = text.split('\n')
        else:
            para = '各条目共用的几条规矩，条目里不再重讲。' + ''.join(x[2:] for x in text.split('\n'))
            lines[i:i] = [para, '']
        out = '\n'.join(lines)
        print('%s：添 %d 字%s' % (f, len(out) - len(s), '，写好了' if apply else '（没写，加 --apply）'))
        if apply:
            open(p, 'w', encoding='utf-8', newline='').write(out.replace('\n', nl) if nl == '\r\n' else out)


if __name__ == '__main__':
    main()
