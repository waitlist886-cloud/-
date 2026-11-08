#!/usr/bin/env python3
# 11-07 晚：每条回复一个内框、新旧一个样子，页签在每一条末尾、不钉在屏幕上，点了页签那一页滑进来盖在正文上；超程铭刻的人常驻同行页、标远讯。
# 写法都在 history_far.py。在 11-07 修格式那一张发布卡上打（发出去的第一版也认，先把第一版那一块样式拿掉再打），别的一个字不动：
#   显示正则：远讯那三条插在通用的「角色行」前头（页签照旧是收卷那一条加在末尾）；
#   样式：@L@（只认最新一条）换成每一条，旧回复藏死的两条去掉，末尾接 history_far.CSS_ADD；
#   提示词：骨架⑧添远讯一组的写法、相遇状态添 远讯，后置词添一句，#1385 超程铭刻添第 7 条；changelog 添一句。
# 为什么不照 make_pub_card.py 重打：跟 patch_pub_1107.py 一样，frame.css、rules_frame.json 里有没上线的对话框和别的纪。
# 用法（仓库根上）：python -I -X utf8 底稿/状态栏/大框/patch_pub_1107b.py <11-07 那一张或第一版.json> <输出.json>
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
import history_far as HF

sys.stdout.reconfigure(encoding='utf-8')
LIMIT = 2097152
R = '.rili-markdown-renderer:has(.sz-hud)'


def once(s, a, b, what):
    assert s.count(a) == 1, ('对不上', what, s.count(a), a[:80])
    return s.replace(a, b)


strip = lambda rs: [{k: v for k, v in r.items() if k != 'name'} for r in rs]
src, dst = sys.argv[1], sys.argv[2]
card = json.load(open(src, encoding='utf-8'))
pr = card['prompt']
lb = pr['lorebook']
rules = card['assistantRegexReplace']
css = card['injectStyles']

# ---- 认是哪一张：11-07 修格式那一张，还是发出去的第一版（打过远讯、旧回复另配淡页签） ----
v1 = card['changelog'].startswith(HF.CHANGELOG_V1)
if v1:
    i = css.index(HF.OLD_MARK)
    css = css[:i].rstrip() + '\n'
    card['changelog'] = card['changelog'][len(HF.CHANGELOG_V1):]
    assert HF.FAR_SKEL in pr['systemPrompt'] and HF.INSCRIBE_ADD in lb[1385]['content'], '第一版的提示词不全'
    assert sum(r['regex'] == HF.FAR_RULES[0]['regex'] for r in rules) == 1
assert card['changelog'].startswith('11-07 修格式'), '不是 11-07 修格式那一张：' + card['changelog'][:30]
assert HF.MARK not in css and 'sz-far' not in css, '样式里已经有这一块了'
base = json.loads(json.dumps(card))
base['injectStyles'] = card['injectStyles']   # 核对字段用的：第一版的话 base 的样式是原来那一份
card['injectStyles'] = css

# ---- 规则 ----
if not v1:
    gi = [i for i, r in enumerate(rules) if r['regex'] == HF.GENERIC_ROW]
    assert len(gi) == 1, gi
    rules[gi[0]:gi[0]] = strip(HF.FAR_RULES)
assert len(rules) <= 500, len(rules)   # 页签照旧在末尾（收卷那一条），排在哪一行由样式管

# ---- 样式 ----
n = css.count(HF.L_OLD)
assert n > 50, n
css = css.replace(HF.L_OLD, HF.L_NEW)
for line in HF.O_DROP:
    css = once(css, line.replace('@O@', HF.O_SEL) + '\n', '', '去掉旧回复藏死的那一条')
assert HF.O_SEL not in css and HF.L_OLD not in css
css = css.rstrip() + '\n' + HF.CSS_ADD.replace('@R@', R) + '\n'
assert '@' + 'L@' not in css and '@' + 'O@' not in css and '@' + 'R@' not in css
assert len(css) <= LIMIT, len(css)
card['injectStyles'] = css

# ---- 提示词 ----
if not v1:
    for what, a, b in HF.SYS_EDITS:
        pr['systemPrompt'] = once(pr['systemPrompt'], a, b, what)
    for what, a, b in HF.REAR_EDITS:
        pr['rearPrompt'] = once(pr['rearPrompt'], a, b, what)
    hit = [i for i, e in enumerate(lb) if (e.get('content') or '').startswith(HF.INSCRIBE_HEAD)]
    assert hit == [1385], hit
    lb[1385]['content'] = lb[1385]['content'].rstrip() + HF.INSCRIBE_ADD
card['changelog'] = HF.CHANGELOG + card['changelog']
assert len(card['changelog']) <= 2048, len(card['changelog'])

# ---- 核对 ----
diff = sorted(k for k in base if base[k] != card[k])
print('认出来是', '第一版' if v1 else '11-07 修格式那一张', '；改了的字段', diff, '；@L@ 换了', n, '处')
if not v1:
    assert diff == ['assistantRegexReplace', 'changelog', 'injectStyles', 'prompt'], diff
    assert [k for k in base['prompt'] if base['prompt'][k] != pr[k]] == ['systemPrompt', 'rearPrompt', 'lorebook']
    assert [i for i, (a, b) in enumerate(zip(base['prompt']['lorebook'], lb)) if a != b] == [1385]
with open(dst, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', dst, os.path.getsize(dst) // 1024, 'KB', '规则', len(rules), '条', '样式', len(css), '字', 'changelog', len(card['changelog']), '字')
