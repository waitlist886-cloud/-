#!/usr/bin/env python3
# 日里：拿用户在平台上的发布卡（导出）当底子，把我们这一版 1001年切片的新东西并上去（11-08）。
# 三方合并：上一版（用户导进去的那一张：out/发布卡_迷宫纪大框/底本_发布卡_11-08.json）、用户导出、这一版（make_1001_slice.py 打的切片）。
#   世界书逐条逐栏：用户这一栏跟上一版一样 → 换成这一版的；不一样（用户改过）→ 留用户的。
#     用户改过的正文（九位旅伴的体态那一行）照留；用户改过的触发（凡世至强那二十三条添了光名字）照留，里头的「名（」照 name_paren 换成认两种括号；
#     深度、范围这些用户没改，照这一版（底卡触发修订）。
#   主提示词：用户的（照 user_base.safety_cut 拿掉那一块）上面套这一版的改动（four_era_prompt.system_1001）；后置词用户没改，照这一版。
#   显示规则、样式、介绍页、更新说明：这一版的（用户没改过这几样）。别的字段（卡名、封面、标签、平台记的数）照用户的。
# 用法：python -I -X utf8 merge_user_rili.py <用户导出.json> <上一版.json> <这一版切片.json> <输出.json>
import copy
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import four_era_prompt as FP  # noqa: E402
import name_paren as NP       # noqa: E402
import user_base as UB        # noqa: E402

u = json.load(open(sys.argv[1], encoding='utf-8'))
o = json.load(open(sys.argv[2], encoding='utf-8'))
n = json.load(open(sys.argv[3], encoding='utf-8'))
out = copy.deepcopy(u)
ul, ol, nl = u['prompt']['lorebook'], o['prompt']['lorebook'], n['prompt']['lorebook']
assert len(ul) == len(ol) == len(nl), (len(ul), len(ol), len(nl))
ml = []
kept_content, kept_trig, other_kept = [], [], []
for i, (ue, oe, ne) in enumerate(zip(ul, ol, nl)):
    me = copy.deepcopy(ne)
    for k in set(ue) | set(oe):
        if k in ('content', 'triggerWords'):
            continue
        if ue.get(k) != oe.get(k):
            if k in ne or k in ue:
                me[k] = ue.get(k)
            if k not in ('id', 'createdAt', 'updatedAt', 'cardId', 'order'):
                other_kept.append((i, k))
    if ue['content'] != oe['content']:
        me['content'] = ue['content']
        kept_content.append(i)
    if ue['triggerWords'] != oe['triggerWords']:
        me['triggerWords'] = [NP.fixed_word(w) for w in ue['triggerWords']]
        kept_trig.append(i)
    ml.append(me)
out['prompt']['lorebook'] = ml
sp, cut = UB.safety_cut(u['prompt']['systemPrompt'])
out['prompt']['systemPrompt'] = FP.system_1001(sp)
for k in ('rearPrompt', 'headPrompt', 'suggestionsPrompt'):
    if k in n['prompt'] or k in u['prompt']:
        if u['prompt'].get(k) == o['prompt'].get(k):
            out['prompt'][k] = n['prompt'].get(k)
        else:
            assert k != 'rearPrompt', '用户改过后置词，这个脚本没写怎么并'
for k in ('assistantRegexReplace', 'injectStyles', 'introPage', 'changelog'):
    out[k] = copy.deepcopy(n[k])
for k in UB.MUST_STAY:
    assert k in out['prompt']['systemPrompt'], ('用户那两节不见了', k)
assert 'minor_protection_mechanism' not in json.dumps(out, ensure_ascii=False)
print('世界书：留用户正文的 %d 条 %s；留用户触发的 %d 条（「名（」换成两种括号）；别的栏留用户的 %s' % (len(kept_content), kept_content, len(kept_trig), other_kept[:6]))
print('主提示词：拿掉 %d 样（那一块、那一小句），用户 %d 字 → %d 字' % (cut, len(u['prompt']['systemPrompt']), len(out['prompt']['systemPrompt'])))
with open(sys.argv[4], 'w', encoding='utf-8', newline='\n') as f:
    json.dump(out, f, ensure_ascii=False)
print('ok', sys.argv[4], os.path.getsize(sys.argv[4]) // 1024, 'KB')
