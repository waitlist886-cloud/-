# 拼 az_bronze.js（山铜纪·麦的年月，约900年）：共用的那几段从 az_strife.js（纷争纪中段）里切出来，山铜纪自己的写在 az_bronze_body.js。
# 用法：python -I make_bronze.py（在 底稿/地图/azgaar/ 下跑；az_strife.js 改了以后重跑一回）
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
s = open('az_strife.js', encoding='utf8').read()
body = open('az_bronze_body.js', encoding='utf8').read()


def seg(a, b):
    i = s.index(a)
    j = s.index(b, i)
    return s[i:j]


head = s[s.index('(async () => {'):s.index('  // 墙东：')]
wall = seg('  // ---- 长垒：', '  // ---- 天上的、发光的 ----')
# 纷争纪的裂影粮道止戈以后不再往墙下运粮，山铜纪那一张换成灰之魔女修的粮道（body 里画），这里去掉
wall = '\n'.join(l for l in wall.split('\n') if not l.startswith('  const darkRoad = ') and not l.startswith('  darkRoad('))
compass = seg('  // 罗盘、比例尺照 Azgaar 自己的', '  // ---- 地名 ----')
labels = seg('  // ---- 地名 ----', "  T1('西 陆',")
tail = s[s.index('  try { await document.fonts.load('):]
for k in ['__WALL_RAIL_ROADS__', '__COMPASS__', '__LABEL_HELPERS__']:
    assert body.count(k) == 1, k
body = body.replace('__WALL_RAIL_ROADS__', wall).replace('__COMPASS__', compass).replace('__LABEL_HELPERS__', labels)
top = """// 山铜纪·麦的年月（约900年）样张：make_bronze.py 拼的（共用的那几段照 az_strife.js，山铜纪自己的在 az_bronze_body.js），build_late.sh bronze 接着跑。
//   山铜纪补卷_14 地图的几层“后段那一张”：墙西从灰雨城城西塌口画出一条往西的车道，790年停在黑曜平原上，862年成了烬灭之都；九座高座一座一座熄了，
//   742到861年七处地方长成了七座城；灯路一站一站往外接，渊月长廊照灯路的线修，890年一期贯通；墙东河岸上的碑一面一面往下游排，平原改叫曙辉平原，
//   870年以后墙下立起界碑，射界里种上了麦；死域照旧在南段对面，沙海在死域里，落星洼到麦的年月是一大片望不到边的水。
//   高座照纷争纪中段那一张的位置（高座_纷争纪.json，塞进 SEATS），都熄了；长垒塞进 WALL_PTS。
"""
out = top + head + body + tail
open('az_bronze.js', 'w', encoding='utf8').write(out)
print('ok', len(out))
