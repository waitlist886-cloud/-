#!/usr/bin/env python3
# 11-12 玩家反馈那一轮，风月那一张的补丁：跟 patch_pub_1112.py 打的是同一批东西，照风月卡的结构落。
#   - 提示词：风月把日里的主提示词照节切开放在 pre_prompt 和几条常驻世界书里，fix_1112 的每个旧串在整张卡里正好落在一个字段的一处，找到那一处就换。
#   - 世界书里那几条照正文头一行认；新条目三份照风月的格式接在末尾（触发并成一条正则，RE2 的写法，不用前瞻）。
#   - 显示规则：mod_page 那几条照 make_fy_card.py 的 port() 转成只认 g 的写法，转换那一组存、显各放一份；样式换成风月的两个前缀。
#   - 打完整份文件查一遍风月的屏蔽词。
# 用法：python -I -X utf8 patch_fy_1112.py <修复前的风月卡.json> <输出.json>
import ast
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
BAN_RE = re.compile('rili|扣扣|日历|风月|fengyue', re.I)
L_FY = 'div:not(x-x):not(.x1):not(.x2):not(.x3):where(#customized-answer:has(.sz-hud))'
R_FY = '.markdown-body:has(.sz-hud)'

# make_fy_card.py 是一口气跑到底的脚本，这里只拿它转规则的那几个函数
_src = open(os.path.join(HERE, 'make_fy_card.py'), encoding='utf-8').read()
_ns = {'re': re}
for node in ast.parse(_src).body:
    if isinstance(node, ast.FunctionDef) and node.name in ('scan', 'groups', 'no_m', 'shift_backrefs', 'port'):
        exec(compile(ast.Module([node], []), 'make_fy_card.py', 'exec'), _ns)
port = _ns['port']

src, dst = sys.argv[1], sys.argv[2]
old = json.load(open(src, encoding='utf-8'))
card = copy.deepcopy(old)


def find_list(need):
    ks = [k for k, v in card.items() if isinstance(v, list) and v and isinstance(v[0], dict) and need <= set(v[0])]
    assert len(ks) == 1, (need, ks)
    return ks[0]


K_WB = find_list({'key', 'value', 'key_region'})
K_RX = find_list({'match_regex', 'replace_text'})
K_CSS = [k for k, v in card.items() if isinstance(v, str) and '.sz-hud' in v and len(v) > 100000]
assert len(K_CSS) == 1, K_CSS
K_CSS = K_CSS[0]
wb, rules = card[K_WB], card[K_RX]
assert not any('## 迷雾' in (e.get('value') or '') for e in wb) and '## 迷雾' not in json.dumps(card, ensure_ascii=False)[:200000], '这一张已经打过了'


# ---- 一、提示词：每个旧串在整张卡里正好一处 ----
def string_fields():
    for k, v in card.items():
        if isinstance(v, str) and k != K_CSS:
            yield (k,), v
    for i, e in enumerate(wb):
        yield (K_WB, i, 'value'), e['value']


def put(path, s):
    if len(path) == 1:
        card[path[0]] = s
    else:
        card[path[0]][path[1]][path[2]] = s


where = {}
for what, a, b, scope in [('主提示词 ' + w, a, b, s) for w, a, b, s in FX.SYS] + [('后置词 ' + w, a, b, s) for w, a, b, s in FX.REAR]:
    if scope == 'four':
        continue
    hits = [(p, v) for p, v in string_fields() if a in v]
    assert len(hits) == 1 and hits[0][1].count(a) == 1, ('对不上', what, [(p, v.count(a)) for p, v in hits])
    put(hits[0][0], hits[0][1].replace(a, b))
    where[what] = hits[0][0]

# ---- 二、世界书里那几条 ----
n_lore = 0
for head, eds in FX.LORE_EDITS.items():
    idx = [i for i, e in enumerate(wb) if e['value'].lstrip().startswith(head)]
    assert len(idx) == 1, (head, idx)
    c = wb[idx[0]]['value']
    for ed in eds:
        if len(ed) > 3 and ed[3] == 'four':
            continue
        assert c.count(ed[1]) == 1, (head, ed[0], c.count(ed[1]))
        c = c.replace(ed[1], ed[2])
        n_lore += 1
    wb[idx[0]]['value'] = c
for head, (drop, add) in FX.TRIG_EDIT.items():
    idx = [i for i, e in enumerate(wb) if e['value'].lstrip().startswith(head)]
    assert len(idx) == 1, (head, idx)
    e = wb[idx[0]]
    extra = [w for w in ('专利', '配方', '秘方', '图纸') if w not in e['key'].split('|')]
    e['key'] = e['key'] + ''.join('|' + w for w in extra)
    re.compile(e['key'])
    n_lore += 1


# 人物条的触发：认「名（」的那一批各添一支，她在 ⑧角色 有一组、或者开过口，下一轮档案跟进来（缘故见 fix_1112.card_triggers）
_PAREN = re.compile(r'(?:^|\|)([^|()\[\]?*+{}\\]{1,12})\[（\(\]')
n_card = 0
for e in wb:
    alts = e['key'].split('|')
    for name in _PAREN.findall(e['key']):
        add = '§(?:角色|话)｜' + name
        if name in alts or add in e['key']:
            continue
        if len((e['key'] + '|' + add).encode('utf-8')) > 600:
            continue
        e['key'] = e['key'] + '|' + add
        re.compile(e['key'])
        n_card += 1
n_lore += n_card


# ---- 新条目：照风月的格式 ----
def fy_key(trig):
    parts = []
    for w in trig:
        if w.startswith('/') and w.endswith('/') and len(w) > 2:
            body = w[1:-1]
            assert not re.search(r'\(\?[=!<]', body), ('风月的触发是 RE2，不用前瞻后顾', w)
            parts.append(body)
        else:
            parts.append(re.escape(w).replace('\\ ', ' '))
    key = '|'.join(parts)
    re.compile(key)
    assert len(key.encode('utf-8')) <= 600, (len(key.encode('utf-8')), key[:40])
    return key


region = {'user': 2, 'assistant': 4, 'system': 1}
sorts = {}
for e in wb:
    sorts.setdefault(e['group'], []).append(e['sort'])
heads = {e['value'].strip().split('\n')[0] for e in wb}
new = []
bump = {}
tmpl = {k: v for k, v in wb[-1].items()}
for f, title, st, content in NB.load():
    if f not in NEW_FILES:
        continue
    assert content.split('\n')[0] not in heads, ('已经有这一条了', title)
    assert st['folder'] in sorts, ('文件夹在风月卡里没有', st['folder'])
    bump[st['folder']] = bump.get(st['folder'], 0) + 1
    e = dict(tmpl)
    e.update({'group': st['folder'], 'match_type': 3, 'key': fy_key(st['trig']), 'key_region': sum(region[r] for r in st['range']), 'value_type': 0,
              'value': content, 'value_configs': [], 'value_region': 1, 'sort': max(sorts[st['folder']]) + bump[st['folder']], 'depth': st['depth'],
              'probability': 100, 'enable': True})
    new.append(e)
assert len(new) == len(NEW_FILES)
wb.extend(new)

# ---- 三、显示规则和样式 ----
titles = [r['title'] for r in rules]


def at(title):
    idx = [i for i, t in enumerate(titles) if t == title]
    assert len(idx) == 1, (title, idx)
    return idx[0]


def ins(before, rs, render_only, prefix=''):
    global titles
    i = at(before)
    add = []
    for r in rs:
        p = port(r, render_only)
        p['title'] = prefix + p['title']
        re.compile(p['match_regex'])
        add.append(p)
    rules[i:i] = add
    titles = [r['title'] for r in rules]
    return len(add)


assert 'MOD开页' not in titles
added = 0
for pre, ro in (('存·', False), ('显·', True)):
    added += ins(pre + '转·剩下的标签', MP.CONVERT_HTML, ro, pre)
    added += ins(pre + '稳·MOD并行', MP.CONVERT_UNKNOWN, ro, pre)
    added += ins(pre + '稳·MOD拆行', MP.CONVERT_GATHER, ro, pre)
added += ins('稳·MOD成块·并', MP.FRAME_OPEN, True)
changed = 0
i = at('稳·MOD成块·并')
assert rules[i]['match_regex'] == MP.ANCHOR_WRAP[1:-2], rules[i]['match_regex']
rules[i]['match_regex'] = MP.WRAP_SAME[1:-2]
changed += 1
i = at('收卷')
s = rules[i]['replace_text']
a = s.index('<label class="sz-tab t-news">')
b = s.index('</label>', a) + len('</label>')
assert 't-mod' not in s
rules[i]['replace_text'] = s[:b] + MP.TAB + s[b:]
changed += 1
i = at('角色行')
assert rules[i]['match_regex'] == MP.ROLE_RX[1:-2] and rules[i]['replace_text'].count(MP.ROLE_OLD) == 1
rules[i]['match_regex'] = MP.ROLE_RX_NEW[1:-2]
rules[i]['replace_text'] = rules[i]['replace_text'].replace(MP.ROLE_OLD, MP.ROLE_NEW)
changed += 1
assert L_FY + ':has(.t-news input:checked) .p-news{display:block}' in card[K_CSS], '样式前缀跟这一张对不上'
card[K_CSS] = card[K_CSS].rstrip() + '\n' + '\n'.join(ln for ln in MP.css(L_FY, R_FY).split('\n') if not ln.startswith('/*')) + '\n'

# ---- 核对 ----
out_text = json.dumps(card, ensure_ascii=False)
ban = sorted(set(m.group(0) for m in BAN_RE.finditer(out_text)))
ban0 = sorted(set(m.group(0) for m in BAN_RE.finditer(json.dumps(old, ensure_ascii=False))))
assert ban == ban0 == [], ('屏蔽词', ban, ban0)
diff = sorted(k for k in old if old[k] != card[k])
print('动了的字段', diff)
print('提示词各处落在', sorted({str(v[:2]) for v in where.values()}))
print('世界书 %d → %d 条：那几条改 %d 处，新添 %s' % (len(old[K_WB]), len(wb), n_lore, [e['value'].split('\n')[0] for e in new]))
print('显示规则 %d → %d 条（添 %d，改 %d），样式 %d → %d 字' % (len(old[K_RX]), len(rules), added, changed, len(old[K_CSS]), len(card[K_CSS])))
with open(dst, 'w', encoding='utf-8', newline='\n') as f:
    f.write(out_text)
print('ok', dst, os.path.getsize(dst) // 1024, 'KB，屏蔽词 0')
