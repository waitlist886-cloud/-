# 风月卡的门控比对：同一轮回复，旧卡的触发认旧 HTML、新卡的触发认记录，叫醒的条目（只看认 AI 那一侧的）比一比。
# 用法：python -I -X utf8 wake_cmp_fy.py <风月原卡.json> <新卡.json> <旧回复,记录回复> [<旧回复,记录回复>…]
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
old = json.load(open(sys.argv[1], encoding='utf-8'))['world_bk']
new = json.load(open(sys.argv[2], encoding='utf-8'))['world_bk']
new = [e for e in new if not e['value'].startswith('# 纷争纪传奇：辛美尔')]   # 同步日里时多的那一条，旧卡没有
assert len(old) == len(new)


def compile_all(wb):
    out = []
    for e in wb:
        if not e.get('enable', True) or not e['key_region'] & 4:
            out.append(None)
            continue
        out.append(re.compile(e['key']))
    return out


co, cn = compile_all(old), compile_all(new)
names = [e['value'].split('\n', 1)[0][:30] for e in old]
ALWAYS = {i for i, e in enumerate(old) if e['key'].startswith('[\\s\\S]')}
for pair in sys.argv[3:]:
    a, b = pair.split(',')
    ta = open(a, encoding='utf-8', newline='').read().replace('\r\n', '\n')
    tb = open(b, encoding='utf-8', newline='').read().replace('\r\n', '\n')
    wa = {i for i, r in enumerate(co) if r and r.search(ta)} - ALWAYS
    wb_ = {i for i, r in enumerate(cn) if r and r.search(tb)} - ALWAYS
    print(os.path.basename(a), '旧', len(wa), '新', len(wb_), '共同', len(wa & wb_))
    for i in sorted(wa - wb_):
        print('   只有旧版醒', i, names[i], '|', new[i]['key'][:110])
    for i in sorted(wb_ - wa):
        m = cn[i].search(tb)
        print('   只有新版醒', i, names[i], '| 命中', tb[max(0, m.start() - 12):m.end() + 12].replace('\n', '⏎')[:90], '| key', new[i]['key'][:90])
