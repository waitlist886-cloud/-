# 拿现行全本卡，把显示正则里大框那一段换成新出的 rules_new.json（其余照旧），出一张试验卡
import json, sys
# 用法：python -I -X utf8 试验卡.py <改前的 rules_frame.json> <改后的 rules_frame.json> <出卡.json>（不打卡，只给本地体检、截图用）
S = ''
card = json.load(open('E:/aldran_art/out/发布卡_四纪大框/奥尔德兰_四纪大框_原介绍页_全本.json', encoding='utf-8'))
old = json.load(open(sys.argv[1], encoding='utf-8'))
new = json.load(open(sys.argv[2], encoding='utf-8'))
cr = card['assistantRegexReplace']
key = lambda r: (r['regex'], r['replaceString'], r['applyMode'])
oldk = [key(r) for r in old]
# 卡里大框那一段：照次序一条一条对上旧的
pos = {}
j = 0
mod = set()
for i, r in enumerate(cr):
    if j >= len(oldk):
        break
    if key(r) == oldk[j]:
        pos[j] = i; j += 1
    elif j > 0 and i + 1 < len(cr) and j + 1 < len(oldk) and key(cr[i + 1]) == oldk[j + 1]:
        pos[j] = i; mod.add(j); j += 1     # 打卡时改过字的那几条（mod_page 改的），位置照旧
print('打卡时改过的', sorted(mod))
print('旧大框对上', j, '/', len(oldk))
assert j == len(oldk)
first, last = pos[0], pos[len(oldk) - 1]
extra = {i: r for i, r in enumerate(cr[first:last + 1], first) if i not in pos.values()}
print('卡里夹在中间的别的规则', len(extra), [k for k in extra])
# 新的一份：旧的那几条照名字对上位置，夹在中间的别的规则跟着它前头那一条旧规则走
newnames = [r['name'] for r in new]
oldnames = [r['name'] for r in old]
after = {}  # 旧规则下标 -> 紧跟着的卡里额外规则
for i, r in extra.items():
    prev = max(k for k, v in pos.items() if v < i)
    after.setdefault(prev, []).append(r)
# 旧规则在新表里的位置（名字可能重名，照出现次序配）
from collections import defaultdict
seen = defaultdict(int); occ_old = []
for n in oldnames:
    occ_old.append((n, seen[n])); seen[n] += 1
seen = defaultdict(int); newpos = {}
for i, n in enumerate(newnames):
    newpos[(n, seen[n])] = i; seen[n] += 1
out_mid = []
inv = {}
for k, o in enumerate(occ_old):
    inv[newpos[o]] = k
for i, r in enumerate(new):
    rr = {k: v for k, v in r.items() if k != 'name'}
    if i in inv and inv[i] in mod:
        assert key(old[inv[i]]) == key(r), ('这一条新表里也改了', r['name'])
        rr = cr[pos[inv[i]]]
    out_mid.append(rr)
    if i in inv and inv[i] in after:
        out_mid.extend(after[inv[i]])
card['assistantRegexReplace'] = cr[:first] + out_mid + cr[last + 1:]
print('卡里显示正则', len(cr), '→', len(card['assistantRegexReplace']))
json.dump(card, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False)
