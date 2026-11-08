# 风月（用户的导出当底子，11-08 第四回）：只添这一轮的武侠古风禁用词、真龙的龙形，加几处底卡自己用着的武侠字眼，用户在平台上改过的东西一处不碰。
# 先跑 patch_fy_user_css.py 换样式，再拿它的输出跑这一份。每一处旧串必须正好出现一次，对不上就停（说明用户那一张这里改过，交给用户自己看）。
# 用法：python -I -X utf8 patch_fy_user_1108.py <换过样式的风月卡.json> <输出.json>
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import four_era_prompt as FP

BAN_RE = re.compile(r'rili|扣扣|日历|风月|fengyue', re.I)
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding='utf-8'))
wb_key = [k for k, v in d.items() if isinstance(v, list) and v and isinstance(v[0], dict) and 'key' in v[0] and 'value' in v[0]]
assert len(wb_key) == 1, wb_key
wb = d[wb_key[0]]
rear_key = [k for k in ('potx', 'post_text', 'posttxt', 'suffix_txt', 'post_tx') if k in d]
assert len(rear_key) == 1, rear_key
rear_key = rear_key[0]

LIST = dict((w, b) for w, a, b in FP.SYS_EDITS)['武侠黑名单']          # 残酷世界、冰冷现实。＋ 换行 ＋ 整张表
REAR = dict((w, b) for w, a, b in FP.REAR_EDITS)['武侠']
WB_EDITS = [   # (条目开头, 旧, 新)
    ('# 输出驱动·骨架', '残酷世界、冰冷现实。', LIST),
    ('# 输出驱动·骨架', '典礼、宴会、觐见写正装）', '典礼、宴会、觐见写正装；真龙化回原形的时候写 龙形）'),
    ('# 名录与固定名词', '凛的师父', '凛的老师'),
    ('# 名录与固定名词', '菲伦的师父', '菲伦的老师'),
    ('【基修亚·科伦德】', '（LVL289·凛师父）', '（LVL289·凛的老师）'),
    ('【芙莉莲·银露】', '翠冠王庭（菲伦师父）', '翠冠王庭（菲伦的老师）'),
    ('# 边境为什么没有流派', '他们每个人都有十几个师父，', '他们每个人都有十几个老师，'),
    ('# 军制总纲', '跨时代的飞升', '跨时代的跃升'),
    ('## 凡世至强：法典之影', '官府里烂掉的那一块', '官署里烂掉的那一块'),
    ('# 首轮入局驱动', '具体日期、时辰、地点', '具体日期、钟点、地点'),
]
log = []
for head, a, b in WB_EDITS:
    hit = [e for e in wb if (e.get('value') or '').startswith(head)]
    assert len(hit) == 1, ('条目对不上', head, len(hit))
    v = hit[0]['value']
    assert v.count(a) == 1, ('旧串对不上', head, a, v.count(a))
    hit[0]['value'] = v.replace(a, b)
    log.append('%s：%s → %s' % (head.lstrip('#【 '), a[:24], b[:24].replace('\n', '⏎')))
r = d[rear_key]
a = '界面不入戏，角色只知自己所见所闻。'
assert r.count(a) == 1, ('后置词对不上', r.count(a))
d[rear_key] = r.replace(a, REAR)
log.append('后置词：' + a + ' 后头接武侠那一句')
s = json.dumps(d, ensure_ascii=False, indent=2)
bad = sorted(set(m.group(0) for m in BAN_RE.finditer(s)))
assert not bad, ('屏蔽词', bad)
open(dst, 'w', encoding='utf-8').write(s)
print('\n'.join(log))
print('写了', dst, len(s.encode('utf-8')), '字节')
