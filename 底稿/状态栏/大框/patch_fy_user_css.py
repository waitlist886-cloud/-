# 风月：拿用户在平台上导出的那一张当底子，只换样式（要换规则的话加 --rules 连显示规则一起换），别的字段一个不动。
# 11-08 用户：“以这个为基底进行接下来的ui调整，你不用去经手我做出的任何已有世界书内容与提示词改动”（手机上翻回去再贴太麻烦，平台还常卡到刷新）。
# 用法：python -I -X utf8 patch_fy_user_css.py <用户导出.json> <make_fy_card.py 打出来的风月卡.json> <输出.json> [--rules]
# 风月每次导出字段名都换一套（built_in_css 叫 bicss，regex_rp 叫 re_replaces……），这里两边各认各的；写出来照用户那一份的字段名和缩进。
import json, re, sys

ALIAS = {
    'css': ['built_in_css', 'bicss', 'inner_css', 'custom_css', 'builtInCss', 'builtCss'],
    'rules': ['regex_rp', 're_replaces', 'regex_replaces', 'reg_rp', 'rx_rp'],
}
BAN_RE = re.compile(r'rili|扣扣|日历|风月|fengyue', re.I)


def key(d, kind):
    ks = [k for k in ALIAS[kind] if k in d]
    if len(ks) != 1:
        sys.exit('认不出%s那一栏：%s' % (kind, ks or sorted(d)))
    return ks[0]


args = [a for a in sys.argv[1:] if not a.startswith('--')]
with_rules = '--rules' in sys.argv
user = json.load(open(args[0], encoding='utf-8'))
ours = json.load(open(args[1], encoding='utf-8'))
uc, oc = key(user, 'css'), key(ours, 'css')
old_u, new = user[uc], ours[oc]
# 底卡带的那一段旧样式两边应当一样；不一样说明用户在平台上改过样式，换掉会把那些改动一起冲掉，停下来问
head = 100000
if old_u[:head] != new[:head]:
    sys.exit('用户那一张的样式开头跟我们的不一样（平台上改过样式？），没换')
user[uc] = new
changed = ['样式 %s：%d → %d 字' % (uc, len(old_u), len(new))]
if with_rules:
    ur, orr = key(user, 'rules'), key(ours, 'rules')
    changed.append('显示规则 %s：%d → %d 条' % (ur, len(user[ur]), len(ours[orr])))
    user[ur] = ours[orr]
text = json.dumps(user, ensure_ascii=False, indent=2)
hits = sorted(set(m.group(0) for m in BAN_RE.finditer(text)))
if hits:
    sys.exit('屏蔽词：%s' % hits)
open(args[2], 'w', encoding='utf-8').write(text)
print('ok', args[2], '；'.join(changed), '；屏蔽词 0')
