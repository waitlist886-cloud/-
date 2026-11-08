#!/usr/bin/env python3
# 11-07 玩家反馈迷宫纪大框的发布卡格式崩了（挂了破甲、防截断、防抢话、相遇日记几个 MOD，gemini）。在线上那一张卡上直接打补丁，别的一个字不动：
#   显示正则：转换那一组最前头插 robust_rules.CONVERT_PRE，展开那一组帧记号以前插 FRAME_PRE，改 REGEX_EDITS、REP_EDITS 那几处；
#   样式：末尾接 CSS_ADD；
#   提示词：后置词里 §底座 那一句原来写成「§底座：日期·HH:MM·…」，冒号和不带空格的点正是模型抄歪的样子，照骨架那一行重写，另添 MOD 写成记录一句；
#           骨架里 MOD 那一句「照其模板输出」会被读成照抄 MOD 的 HTML，改成照它的栏目写、写法换成记录。
# 为什么不照 make_pub_card.py 重打：那以后 frame.css、rules_frame.json 又添了对话框和别的纪，重打会把没上线的东西带进去。
# 用法（仓库根上）：python -I -X utf8 底稿/状态栏/大框/patch_pub_1107.py <线上那一张.json> <输出.json>
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import robust_rules as RR

sys.stdout.reconfigure(encoding='utf-8')
LIMIT = 2097152
L = 'div[style*="contain: layout"]:has(.sz-hud):not(:has(~ div .sz-hud))'
R = '.rili-markdown-renderer:has(.sz-hud)'


def once(s, a, b, what):
    assert s.count(a) == 1, ('对不上', what, s.count(a), a[:80])
    return s.replace(a, b)


src, dst = sys.argv[1], sys.argv[2]
card = json.load(open(src, encoding='utf-8'))
base = json.loads(json.dumps(card))
rules = card['assistantRegexReplace']

# ---- 规则 ----
assert rules[0]['regex'].startswith('/^([\\s\\S]*(?:<details\\b|<summary\\b|<div class="(?:arc-'), rules[0]['regex'][:60]
assert all(r['applyMode'] == 'all' for r in rules[:132]) and rules[132]['applyMode'] == 'front-end'
for e, old, new in RR.REGEX_EDITS:
    hit = [r for r in rules if old in r['regex']]
    assert len(hit) == 1, (e, len(hit))
    hit[0]['regex'] = hit[0]['regex'].replace(old, new)
for e, old, new in RR.REP_EDITS:
    hit = [r for r in rules if old in r['replaceString']]
    assert len(hit) == 1, (e, len(hit))
    hit[0]['replaceString'] = hit[0]['replaceString'].replace(old, new)
fence = [i for i, r in enumerate(rules) if r['regex'] == '/^\\s*```[a-zA-Z]*\\s*\\n(§底座｜)/']
assert len(fence) == 1
assert rules[fence[0] + 1]['regex'] == '/^((?:[\\s\\S]*\\n|)§底座｜[\\s\\S]*)$/', rules[fence[0] + 1]['regex']   # 帧记号，上面改过
strip = lambda rs: [{k: v for k, v in r.items() if k != 'name'} for r in rs]
border = next(i for i, r in enumerate(rules) if r['applyMode'] == 'front-end')
assert border == 132 and fence[0] > border
mod = [i for i, r in enumerate(rules) if r['regex'].startswith('/§MOD｜(')]
assert len(mod) == 1 and mod[0] > fence[0], mod
rules[mod[0]:mod[0]] = strip(RR.FRAME_MOD_WRAP)            # 先插后头的，前头的下标不动
rules[fence[0] + 1:fence[0] + 1] = strip(RR.FRAME_PRE)
rules[border:border] = strip(RR.CONVERT_POST)               # 转换那一组的末尾
rules[0:0] = strip(RR.CONVERT_PRE)
assert all(r['applyMode'] == 'all' for r in rules[:132 + len(RR.CONVERT_PRE) + len(RR.CONVERT_POST)])
assert len(rules) <= 500, len(rules)
card['assistantRegexReplace'] = rules

# ---- 样式 ----
css = card['injectStyles'].rstrip() + '\n' + RR.CSS_ADD.replace('@L@', L).replace('@R@', R) + '\n'
assert len(css) <= LIMIT, len(css)
card['injectStyles'] = css

# ---- 提示词 ----
pr = card['prompt']
pr['rearPrompt'] = once(pr['rearPrompt'], '第一个字是 §底座：日期·HH:MM·地点·潮汐·防抢话·档位，时间以分钟记账，接 §环境 和 §推演九行。',
                        '第一行照这个样子写，只换内容：§底座｜纪元：迷宫纪1001年·季·月名·旬日 · HH:MM 时段词 · 完整地点 · 第一兆·魔兽离巢·潮位 · 防抢话 开 · 档位 很长'
                        '（大段之间是「空格·空格」，日期和地点里的点不带空格，不加括号注），时间以分钟记账，接 §环境 和 §推演九行。', '后置词 底座')
pr['rearPrompt'] = once(pr['rearPrompt'], '每轮写全，没变的照抄。',
                        '每轮写全，没变的照抄。上一轮要是缺了几行、混进了 HTML、或者写成了一段字，这一轮照骨架把整套写全，别照着上一轮的错抄。', '后置词 自愈')
pr['rearPrompt'] = once(pr['rearPrompt'], '主角面板禁写「未知」「同上」。',
                        '主角面板禁写「未知」「同上」。挂了相遇日记这类 MOD，照它的栏目写成 §MOD｜MOD名｜栏名｜内容，一人或一个势力一行，不写它模板里的 HTML。', '后置词 MOD')
pr['systemPrompt'] = once(pr['systemPrompt'], 'MOD 面板：挂了相遇日记这类 MOD 就照其模板输出，一栏一行 `§MOD｜MOD名｜栏名｜内容`，',
                          'MOD 面板：挂了相遇日记这类 MOD，照它要的栏目和内容写，写法换成记录、不抄它模板里的 HTML：一栏一行 `§MOD｜MOD名｜栏名｜内容`，'
                          '相遇日记一人或一个势力一行（`§MOD｜相遇日记｜名字｜身份或势力 ｜ 好感 Lv.n 名称或势力七档 ｜ 现状 ｜ 因果`），', '骨架 MOD')
card['changelog'] = ('11-07 修格式：§底座 那一行写歪一点、写成半角竖线或加粗、前头多一段话、干脆没写，状态栏都不再塌成窄条或整片字；'
                     '相遇日记这类 MOD 不论写成 HTML 还是一段字，都整理成一人一张，放进见闻页。') + card.get('changelog', '')
assert len(card['changelog']) <= 2048, len(card['changelog'])

# ---- 核对 ----
diff = sorted(k for k in base if base[k] != card[k])
print('改了的字段', diff)
assert diff == ['assistantRegexReplace', 'changelog', 'injectStyles', 'prompt'], diff
assert [k for k in base['prompt'] if base['prompt'][k] != pr[k]] == ['systemPrompt', 'rearPrompt']
with open(dst, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', dst, os.path.getsize(dst) // 1024, 'KB', '规则', len(rules), '条（原', len(base['assistantRegexReplace']), '）', '样式', len(css), '字')
