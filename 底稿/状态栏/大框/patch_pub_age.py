#!/usr/bin/env python3
# 11-08：给迷宫纪发布卡套成年线（用户：“顺便给迷宫纪的底卡也更新18岁改动吧”）。11-06 定的：980 年蕾雅提出、两个王盖章，
# 法定成年、公会报名、面板觉醒从十六挪到十八；十位旅伴 16→18、17→19、米娅 15→刚满18；任务人物菲雅十九、艾米十七。
# 发布卡是老底卡（没有四纪、没有洗稿层），v12 里这些改在洗稿层上，字句跟发布卡对不上，所以照 v12 试打出来的卡整条搬：
#   底卡三十二条（九条世界规则 #0 #47 #474 #486 #613 #882 #1031 #1053 #1054，十位旅伴条，#824 #839 #854，羁绊 #1304—#1313）换成 v12 的正文
#   （v12 的这几条连带洗稿层的润色一起来；凡世至强末尾「前传的局」那一节发布卡用不上，切掉），触发和设置不动；
#   介绍页套 进卡补丁_rili_v12.py 的 INTRO_AGE（八十八条，旧串、新串、次数，对不上就停），建档器的开局岁数一起改了。
# 用法（仓库根上）：python -I -X utf8 底稿/状态栏/大框/patch_pub_age.py <发布卡.json> <v12 试打的卡.json> <输出.json>
import importlib.util
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.dont_write_bytecode = True
pub_p, v12_p, dst = sys.argv[1:4]
card = json.load(open(pub_p, encoding='utf-8'))
v12 = json.load(open(v12_p, encoding='utf-8'))['prompt']['lorebook']
base = json.loads(json.dumps(card))
lb = card['prompt']['lorebook']
assert 'sz-far' in card['injectStyles'], '要在打过远讯和内框的那一张上打'
assert '18' not in lb[1304]['content'].split('\n')[0], '这一张好像已经套过成年线'

IDX = [0, 47, 474, 486, 613, 882, 1031, 1053, 1054, 797, 799, 801, 805, 807, 809, 813, 815, 818, 820, 824, 839, 854] + list(range(1304, 1314))
for i in IDX:
    old, new = lb[i]['content'], v12[i]['content']
    assert old.split('\n')[0].lstrip('#【 ')[:4] == new.split('\n')[0].lstrip('#【 ')[:4] or i >= 1304, (i, old[:30], new[:30])
    new = re.split(r'\n### 前传的局｜', new)[0].rstrip()
    lb[i]['content'] = new

spec = importlib.util.spec_from_file_location('p12', os.path.join('out', '进卡_v12', 'tools', '进卡补丁_rili_v12.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
intro = card['introPage']
for a, b, n in m.INTRO_AGE:
    assert intro.count(a) == n, ('介绍页对不上', a[:40], intro.count(a), n)
    intro = intro.replace(a, b)
card['introPage'] = intro
card['changelog'] = ('11-08 成年线：法定成年、公会报名和面板觉醒从十六岁挪到十八岁（980 年定的）；十位旅伴改成十八九岁，米娅刚满十八；建档的开局岁数跟着改。') + card['changelog']
assert len(card['changelog']) <= 2048

diff = sorted(k for k in base if base[k] != card[k])
assert diff == ['changelog', 'introPage', 'prompt'], diff
assert [k for k in base['prompt'] if base['prompt'][k] != card['prompt'][k]] == ['lorebook']
changed = [i for i, (a, b) in enumerate(zip(base['prompt']['lorebook'], lb)) if a != b]
assert changed == sorted(IDX), changed
with open(dst, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', dst, '换了', len(changed), '条世界书，介绍页', len(m.INTRO_AGE), '处')
