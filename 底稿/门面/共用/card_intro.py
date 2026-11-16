# 把打好的卡里的介绍页原样取出来存成一个文件，给 act_sandbox.mjs 当薄壳的地址用（验的就是卡里那一段，一个字不差）。
#   python -I -X utf8 底稿/门面/共用/card_intro.py <卡.json> 底稿/门面/小样_外壳/thin_card.html      （thin*.html 不进库）
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
card = json.load(open(sys.argv[1], encoding='utf-8'))
s = card['introPage']
open(sys.argv[2], 'w', encoding='utf-8', newline='').write(s)
print('介绍页', len(s), '字；薄壳', 'FRONT_CFG' in s, '；带原来那一页', '__OLD1001=' in s)
print('更新说明头一句：', (card.get('changelog') or '').split('\n')[0][:120])
