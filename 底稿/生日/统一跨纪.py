#!/usr/bin/env python3
# 收稿：几份子任务给同一个人起了不同的生日（差一两年），照这个人头一回出场那一页的统一；巴尔缇娜改到山铜纪2年（2年霜降月那一夜她不满周岁）。
# 只在分段稿和不分段的页上换「生于…」那一段，换完照打印的命令重拼。登记表跟着改。
import glob
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
FIX = [  # (哪一纪的文件, 旧, 新, 谁)
    ('纷争纪/parts*/*.md', '月银纪10043年·金穗月·下旬五日', '月银纪10042年·金穗月·上旬四日', '托比亚斯，照萨尔维斯'),
    ('纷争纪/parts*/*.md', '月银纪10056年·清露月·下旬八日', '月银纪10055年·清露月·中旬三日', '费利克斯，照萨尔维斯'),
    ('山铜纪/parts*/*.md', '纷争纪10995年·清露月·上旬三日', '纷争纪10996年·萌芽月·上旬四日', '玛蒂尔德，照纷争纪'),
    ('山铜纪/parts*/*.md', '纷争纪10983年·霜降月·下旬九日', '纷争纪10984年·萌芽月·中旬五日', '瑟尔卡，照纷争纪'),
    ('山铜纪/parts*/*.md', '纷争纪10777年·长曦月·中旬三日', '纷争纪10779年·萌芽月·下旬八日', '芙莉莲，照纷争纪'),
    ('山铜纪/parts*/*.md', '纷争纪10973年·寒星月·中旬一日', '纷争纪10974年·萌芽月·下旬十日', '西蒙，照纷争纪'),
    ('山铜纪/parts*/*.md', '纷争纪10991年·金穗月·中旬五日', '纷争纪10992年·萌芽月·中旬八日', '迪特里希，照纷争纪'),
    ('迷宫纪前传/parts*/*.md', '山铜纪921年·金穗月·中旬八日', '山铜纪920年·长曦月·中旬七日', '卡雅，照山铜纪'),
    ('迷宫纪前传/parts*/*.md', '山铜纪923年·霜降月·上旬七日', '山铜纪922年·金穗月·下旬一日', '本特，照山铜纪'),
    ('山铜纪/parts*/*.md', '生于山铜纪1年·花信月·中旬二日', '生于山铜纪2年·花信月·中旬二日', '巴尔缇娜，2年霜降月不满周岁'),
]
pages = set()
for pat, old, new, who in FIX:
    n = 0
    for f in glob.glob(os.path.join(ROOT, pat)):
        raw = open(f, encoding='utf-8', newline='').read()
        if old in raw:
            k = raw.count(old)
            open(f, 'w', encoding='utf-8', newline='').write(raw.replace(old, new))
            n += k
            pages.add(os.path.relpath(os.path.dirname(f), ROOT).replace('\\', '/'))
    print('%-20s 换了 %d 处' % (who, n))
    if n == 0:
        assert any(new in open(f, encoding='utf-8').read() for f in glob.glob(os.path.join(ROOT, pat))), who   # 上一回已经换过
for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), '登记_*.tsv')):
    raw = open(f, encoding='utf-8', newline='').read()
    for _, old, new, _w in FIX:
        raw = raw.replace(old, new)
    open(f, 'w', encoding='utf-8', newline='').write(raw)
print('要重拼的分段目录', sorted(pages))
