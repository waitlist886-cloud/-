# 11-08 用户回“照倾向改”：灰河分两条（时代地图方向稿第十四节）。
#   墙西的灰河：从灰高原当中的泉眼一带往西南，过渡口（河心三日），往南扎进断岭的裂口，坐标挪到这一条的当中；
#   炉城底下流出来的那一条另起一行“断崖下的河”：过了轰鸣断崖往西流进落星洼，不过墙，往后（联邦的图上）叫熔铁灰河。
# 用法：python -I -X utf8 灰河分两条.py（在 底稿/地图/地点谱/ 下跑，跑完再跑 合表.py）
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = '11-08 灰河分两条：这一行只管墙西从灰高原起头的那一条，炉城底下那一条另起一行“断崖下的河”'
for era, years in [('山铜纪', '山铜纪2到947年'), ('迷宫纪前传', '前传全程（约430年以前流进落星洼，往后流进双月内海）')]:
    p = os.path.join(HERE, era + '.tsv')
    rows = list(csv.DictReader(open(p, encoding='utf8'), delimiter='\t'))
    cols = list(rows[0].keys())
    hit = [r for r in rows if r['名字'] == '灰河']
    assert len(hit) == 1, (era, len(hit))
    r = hit[0]
    if NOTE not in r['要说明的']:
        r['要说明的'] = (r['要说明的'] + '；' if r['要说明的'] else '') + NOTE + f"，原来 {r['地图x']},{r['地图y']}"
        r['地图x'], r['地图y'] = '746', '984'
        r['位置'] = '西陆东南，从灰高原当中的泉眼一带流出来，往西南穿过高原的南半边，过了渡口（河心三日）往南扎进断岭的裂口'
    if not any(x['名字'] == '断崖下的河' for x in rows):
        new = {c: '' for c in cols}
        new.update({'名字': '断崖下的河', '时段与年份': years, '类': '自然', '主要还是次要': '次要', '1001年叫什么': '熔铁灰河',
                    '别纪的叫法': '纷争纪·轰鸣断崖崖下那一条河', '位置': '炉城底下的热泉汇成的暖河，过了轰鸣断崖往西流进落星洼，不过墙，跟墙西的灰河不连着',
                    '地图x': '1500', '地图y': '1146', '出处': '山铜纪·地点｜轰鸣断崖与铁瀑' if era == '山铜纪' else '迷宫纪·地点｜西陆的河与南边两片内海',
                    '要说明的': '11-08 灰河分两条时添的一行；联邦约600年修图把它跟墙西的灰河画成一条熔铁灰河'})
        rows.insert(rows.index(r) + 1, new)
    with open(p, 'w', encoding='utf8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print(era, 'ok')
