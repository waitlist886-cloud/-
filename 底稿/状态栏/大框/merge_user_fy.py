#!/usr/bin/env python3
# 风月：拿用户在平台上的发布卡（导出）当底子，把我们这一版风月卡的新东西并上去（11-08）。
# 三方合并：上一版（用户那一张多半是从它来的，git 里上一回提交的风月卡）、用户导出、这一版（make_fy_card.py 打的）。
#   世界书逐条：正文跟上一版一样 → 换成这一版的；不一样的，旅伴（## 旅途同行：）照用户的（用户改了体态那一行），
#     别的照这一版（用户那一张这几条是 11-08 武侠、合篇那一轮以前的旧字，不是用户改的；列出来）。别的栏（触发、深度、范围）跟上一版一样的照这一版。
#   提示词：用户的照 user_base.safety_cut 拿掉那一块和那一小句，别的照留；这一版的提示词跟上一版一样才这么并（不一样就停）。
#   别的字段（样式、规则、介绍页、快捷键、前后置文本）：用户的跟上一版一样的换成这一版的，不一样的照用户的；卡名、简介、封面这些照用户的。
#   风月每次导出字段名都换一套，这里按几组别名认，写出来照用户那一份的字段名。
# 用法：python -I -X utf8 merge_user_fy.py <用户导出.json> <上一版风月卡.json> <这一版风月卡.json> <输出.json>
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import user_base as UB  # noqa: E402

BAN_RE = re.compile(r'rili|扣扣|日历|风月|fengyue', re.I)
ALIAS = {
    'wb': ['wb', 'world_bk', 'world_book', 'wbook'],
    'pre': ['pre_prompt', 'pre_pt', 'prpt', 'ppt'],
    'ptx': ['pretxt', 'ptx', 'pre_text', 'pre_tx'],
    'post': ['post_tx', 'posttxt', 'post_text', 'potx', 'suffix_txt'],
    'css': ['bicss', 'built_in_css', 'inner_css', 'custom_css', 'builtInCss'],
    'rules': ['rgx_rep', 'regex_rp', 're_replaces', 'regex_replaces', 'reg_rp', 'rx_rp'],
    'intro': ['dsc', 'descr', 'description', 'desc'],
    'cmds': ['short_cmds', 'scmd', 'sc_cmds', 'shortcut_commands'],
}


def key(d, kind, what):
    ks = [k for k in ALIAS[kind] if k in d]
    if len(ks) != 1:
        sys.exit('%s认不出%s那一栏：%s' % (what, kind, ks))
    return ks[0]


u = json.load(open(sys.argv[1], encoding='utf-8'))
o = json.load(open(sys.argv[2], encoding='utf-8'))
n = json.load(open(sys.argv[3], encoding='utf-8'))
K = {c: (key(u, c, '用户那一张'), key(o, c, '上一版'), key(n, c, '这一版')) for c in ALIAS}
uw, ow, nw = (d[K['wb'][j]] for j, d in enumerate((u, o, n)))
assert len(uw) == len(ow) == len(nw), (len(uw), len(ow), len(nw))
kept, older, settings_kept = [], [], []
for i, (ue, oe, ne) in enumerate(zip(uw, ow, nw)):
    for f in set(ue) | set(oe) | set(ne):
        if f == 'value':
            continue
        if ue.get(f) == oe.get(f):
            if f in ne:
                ue[f] = ne[f]
        else:
            settings_kept.append((i, f))
    if ue['value'] == oe['value']:
        ue['value'] = ne['value']
    elif ue['value'].startswith('## 旅途同行：'):
        kept.append(i)
    else:
        older.append((i, ue['value'].split('\n', 1)[0][:24]))
        ue['value'] = ne['value']
# 提示词
up, op, np_ = u[K['pre'][0]], o[K['pre'][1]], n[K['pre'][2]]
assert op == np_, '这一版的提示词跟上一版不一样了，这个脚本没写怎么并'
sp, cut = UB.safety_cut(up)
u[K['pre'][0]] = sp
for k in UB.MUST_STAY:
    assert k in sp, ('用户那两节不见了', k)
# 别的字段：样式、规则、介绍页、快捷键、前后置文本都是我们打的，用户没动过（用户那一张跟上一版不一样的，是 11-08 那一轮以前的旧版本：
# 后置文本少武侠那一句、样式少龙形那几条、规则少藏预载那一条），一律换成这一版的
other = []
for c in ('ptx', 'post', 'css', 'rules', 'intro', 'cmds'):
    ku, ko, kn = K[c]
    if u[ku] != n[kn]:
        other.append('%s 换成这一版的（用户那一张%s上一版）' % (c, '就是' if u[ku] == o[ko] else '比上一版还旧，不是'))
        u[ku] = n[kn]
text = json.dumps(u, ensure_ascii=False, indent=2)
hits = sorted(set(m.group(0) for m in BAN_RE.finditer(text)))
if hits:
    sys.exit('屏蔽词：%s' % hits)
assert 'minor_protection_mechanism' not in text
open(sys.argv[4], 'w', encoding='utf-8').write(text)
print('世界书 %s：%d 条；旅伴留用户正文的 %d 条 %s；用户那一张是旧字、换成这一版的 %d 条' % (K['wb'][0], len(uw), len(kept), kept, len(older)))
for x in older:
    print('   ', x)
print('别的栏留用户的', settings_kept[:8])
print('提示词：拿掉 %d 样（那一块、那一小句），%d 字 → %d 字' % (cut, len(up), len(sp)))
print('别的字段：', other or '都跟这一版一样')
print('ok', sys.argv[4], os.path.getsize(sys.argv[4]) // 1024, 'KB；屏蔽词 0')
