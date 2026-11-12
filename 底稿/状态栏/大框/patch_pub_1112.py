#!/usr/bin/env python3
# 11-12 玩家反馈那一轮的补丁：在线上那一张底卡（11-10 早上那一回打的）上只打这一轮的修法，别的一个字不动。
# 为什么不照 make_1001_slice.py 整张重打：11-10 往后生成脚本里又添了装备栏十一个部位、§技、§起手、§状态、主角立绘、基本算式这些，
# 只在四纪大框上验过，用户 11-10 说两张底卡先不重打；这一轮是修复，不把没上过线的新记法一起带进去。
# 打的三样：
#   一、提示词、后置词、世界书里那几条（fix_1112.py）。
#   二、新条目接在世界书末尾（底卡新条目/ 里这一轮新写的三份：日用器物.md、知识变现.md、领地.md）。
#   三、显示规则和样式（mod_page.py）：扩展页。
# 用法：python -I -X utf8 patch_pub_1112.py <修复前的卡.json> <输出.json>
import copy
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import fix_1112 as FX      # noqa: E402
import mod_page as MP      # noqa: E402
import new_base as NB      # noqa: E402

NEW_FILES = ['日用器物.md', '知识变现.md', '领地.md']
LIMIT_CSS, LIMIT_RULES, LIMIT_PRIO = 2097152, 500, 8192

src, dst = sys.argv[1], sys.argv[2]
old = json.load(open(src, encoding='utf-8'))
card = copy.deepcopy(old)
pr = card['prompt']
assert '## 迷雾' not in pr['systemPrompt'], '这一张已经打过了，拿修复前的那一张来打'

# 一、提示词和世界书里那几条
n_lore = FX.apply(card, four=False)

# 二、新条目：同一个文件夹里接在最后一条后头（跟 new_base.entries 一个算法，只收这一轮的三份）
lb = pr['lorebook']
heads = {(e.get('content') or '').strip().split('\n')[0] for e in lb}
folders = {}
for e in lb:
    folders.setdefault(e['folder'], []).append(e['priority'])
new = []
bump = {}
for f, title, st, content in NB.load():
    if f not in NEW_FILES:
        continue
    assert content.split('\n')[0] not in heads, ('已经有这一条了', title)
    assert st['folder'] in folders, ('文件夹在底卡里没有', st['folder'])
    bump[st['folder']] = bump.get(st['folder'], 0) + 1
    prio = max(folders[st['folder']]) + bump[st['folder']]
    assert prio <= LIMIT_PRIO, prio
    new.append({'enabled': True, 'triggerWords': st['trig'], 'triggerWordsType': 'OR', 'blackListWords': st.get('black', []),
                'blackListWordsType': 'OR', 'folder': st['folder'], 'priority': prio, 'probability': 100, 'scanDepth': st['depth'],
                'triggerRange': st['range'], 'impactRange': ['system'], 'contentMethod': 'single', 'content': content})
assert len(new) == len(NEW_FILES), [e['content'][:20] for e in new]
lb.extend(new)

# 命运骰和开关那一组的优先级：11-10 早上那一回写的是 9100 起，超了平台上限 8192（11-10 夜查出来，features_1110.PRIO0 改成了 8158），这里跟着挪
import features_1110 as FT  # noqa: E402
n_prio = 0
for e in lb:
    if e['folder'] == FT.FOLDER and e['priority'] >= 9100:
        e['priority'] = e['priority'] - 9100 + FT.PRIO0
        n_prio += 1

# 三、显示规则和样式
rules = card['assistantRegexReplace']
added, changed = MP.apply_rules(rules)
card['injectStyles'] = card['injectStyles'].rstrip() + '\n' + MP.css(MP.L_PUB, MP.R_PUB) + '\n'

# ---- 核对 ----
assert len(rules) <= LIMIT_RULES, len(rules)
assert len(card['injectStyles']) <= LIMIT_CSS, len(card['injectStyles'])
for r in rules:
    m = re.match(r'^/([\s\S]*)/([a-z]*)$', r['regex'])
    assert m and set(m.group(2)) <= set('gims'), r['regex'][:60]
for e in lb:
    assert 0 <= e['priority'] <= LIMIT_PRIO, ('优先级超了', e['priority'], (e.get('content') or '')[:30])
for e in new:
    assert len(e['triggerWords']) <= 20, e['content'][:30]
diff = sorted(k for k in old if old[k] != card[k])
assert diff == ['assistantRegexReplace', 'changelog', 'injectStyles', 'prompt'], diff
assert sorted(k for k in old['prompt'] if old['prompt'][k] != pr[k]) == ['lorebook', 'rearPrompt', 'systemPrompt']
ol = old['prompt']['lorebook']
ch_body = [i for i in range(len(ol)) if ol[i].get('content') != lb[i].get('content')]
ch_trig = [i for i in range(len(ol)) if ol[i]['triggerWords'] != lb[i]['triggerWords']]
ch_else = [i for i in range(len(ol)) if {k: v for k, v in ol[i].items() if k not in ('content', 'triggerWords')}
           != {k: v for k, v in lb[i].items() if k not in ('content', 'triggerWords')}]
assert all(ol[i]['folder'] == FT.FOLDER and set(k for k in ol[i] if ol[i][k] != lb[i][k]) == {'priority'} for i in ch_else), ch_else
assert len(ch_else) == n_prio
print('主提示词 %d → %d 字，后置词 %d → %d 字' % (len(old['prompt']['systemPrompt']), len(pr['systemPrompt']), len(old['prompt']['rearPrompt']), len(pr['rearPrompt'])))
print('世界书 %d → %d 条：正文改了 %s，触发改了 %s，新添 %d 条 %s' % (len(ol), len(lb), ch_body, ch_trig, len(new), [e['content'].split('\n')[0] for e in new]))
print('命运骰和开关那一组的优先级挪进上限以内：%d 条' % n_prio)
print('显示规则 %d → %d 条（添 %d，改 %d），样式 %d → %d 字' % (len(old['assistantRegexReplace']), len(rules), added, changed, len(old['injectStyles']), len(card['injectStyles'])))
with open(dst, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False)
print('ok', dst, os.path.getsize(dst) // 1024, 'KB')
