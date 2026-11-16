#!/usr/bin/env python3
# 把新门面做进卡（11-15 拼装那一轮）：卡的 introPage 换成一段薄壳，页面、数据和图在图床上。
#   python -I -X utf8 底稿/门面/共用/into_card.py <打好的卡.json> <输出的卡.json> [--no-old]
# 先后（都在仓库根上跑）：
#   1. 照常打四纪大框（v12 --fast，再 make_four_era_card.py），这时卡的介绍页还是原来那一整页。
#   2. python -I -X utf8 底稿/门面/小样_外壳/make_old1001.py <打好的卡.json>     原来那一整页留作 1001 年那条路
#   3. python -I -X utf8 底稿/门面/共用/deploy_front.py                          推图床，写 front.json
#   4. 这一支：introPage 换成薄壳（make_thin.py 照 front.json 出的），更新说明添一句。别的字段一个不动。
#      原来那一整页介绍页留在薄壳里当退路：图床的几个镜像都连不上（或者八秒还没载下来）的时候，玩家点一下就换回它，
#      迷宫纪 1001 年的建档器和世界之书照旧能用。所以介绍页还是一百六十来万字。平台要是嫌大存不上，加 --no-old 不留，只有几千字。
# 核对：输出的卡跟输入的卡只差 introPage 和 changelog。
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_thin  # noqa: E402

NOTE = '11-15 介绍页换成新门面：牌桌上选纪元，四本书各看各的时代，右上角一本世界之书，建档完一下填进输入框。迷宫纪1001年的建档、读档和旧世界之书在牌桌左上角原样留着。门面的图和页面放在图床上，载不下来的时候可以点一下退回原来的介绍页。'


def main():
    src, dst = [a for a in sys.argv[1:] if not a.startswith('--')][:2]
    raw = open(src, encoding='utf-8').read()
    card = json.loads(raw)
    old = card.get('introPage') or ''
    assert 'FRONT_CFG' not in old and len(old) > 200000, '这张卡的介绍页已经不是原来那一整页了，拿 make_four_era_card.py 刚打出来的那一张当输入'
    keep_old = '--no-old' not in sys.argv          # 原来那一整页留在薄壳里当退路（图床连不上时换回它）；--no-old 不留，介绍页只有几千字
    thin = make_thin.thin_html(old=old if keep_old else None)
    assert 'FRONT_CFG' in thin and (len(thin) < 20000 or keep_old)
    card['introPage'] = thin
    cl = card.get('changelog') or ''
    if NOTE[:14] not in cl:
        cl2 = (NOTE + '\n' + cl).strip()
        if len(cl2) > 2048:           # 平台的更新说明至多 2048 字，放不下就从末尾收
            cl2 = cl2[:2048]
        card['changelog'] = cl2
    compact = ', ' not in raw[:20000] and '": ' not in raw[:20000]
    with open(dst, 'w', encoding='utf-8', newline='') as f:
        if compact:
            json.dump(card, f, ensure_ascii=False, separators=(',', ':'))
        else:
            json.dump(card, f, ensure_ascii=False)
    back = json.load(open(dst, encoding='utf-8'))
    src_card = json.loads(raw)
    diff = sorted(k for k in set(back) | set(src_card) if back.get(k) != src_card.get(k))
    print('介绍页', len(old), '字 →', len(thin), '字；跟输入的卡不一样的字段：', diff)
    assert set(diff) <= {'introPage', 'changelog'}, diff
    print('写好了', dst, '%.1f MB' % (os.path.getsize(dst) / 1048576))


if __name__ == '__main__':
    main()
