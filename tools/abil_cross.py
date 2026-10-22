import sys, re
s = open(sys.argv[1], encoding='utf-8').read()
heads = {}
for m in re.finditer(r'(?m)^### (\S+) \((\w+) \| (\w+)\)', s):
    heads[m.group(1)] = (m.group(2), m.group(3))
used = {}
for m in re.finditer(r'(?m)^能力：(.*)$', s):
    for a in re.finditer(r'(Special|Passive|Art)【([^】]+)】\((\w+)', m.group(1)):
        used.setdefault(a.group(2), []).append((a.group(1), a.group(3)))
ok = 0
for n, lst in used.items():
    for t, tier in lst:
        if n not in heads:
            print('无命星条:', n, t, tier)
        elif heads[n] != (t, tier):
            print('类型/品阶不符:', n, (t, tier), heads[n])
        else:
            ok += 1
for n in heads:
    if n not in used:
        print('命星没人用:', n, heads[n])
print('对上', ok, '| 命星', len(heads), '| 能力名', len(used))
