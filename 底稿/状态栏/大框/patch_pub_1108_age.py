#!/usr/bin/env python3
# 11-08 档案改生日以后，主角首轮把年龄写成 18岁（生于迷宫纪982年·寒星月·下旬四日），面板身份那一行的年龄栏只认二十个字，整行落进兜底。
# 发布卡（迷宫纪大框）上只改这一条正则：年龄栏放宽到四十字。四纪大框那一张在 make_rules_frame.py 里同样改了。
# 用法：python -I -X utf8 底稿/状态栏/大框/patch_pub_1108_age.py <发布卡.json>（原地写回）
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
p = sys.argv[1]
card = json.load(open(p, encoding='utf-8'))
OLD = '/§面板｜身份｜([^｜\\n]{1,20})｜([^｜\\n]{0,30})｜([^｜\\n]{0,20})｜'
NEW = '/§面板｜身份｜([^｜\\n]{1,20})｜([^｜\\n]{0,30})｜([^｜\\n]{0,40})｜'
hit = [r for r in card['assistantRegexReplace'] if r['regex'].startswith(OLD)]
done = [r for r in card['assistantRegexReplace'] if r['regex'].startswith(NEW)]
if done and not hit:
    print('已经改过了')
    sys.exit(0)
assert len(hit) == 1, len(hit)
hit[0]['regex'] = NEW + hit[0]['regex'][len(OLD):]
card['changelog'] = ('11-08 修：主角年龄写了生日以后，面板身份那一行照常显示。' + card['changelog'])[:2048]
with open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('改好了')
