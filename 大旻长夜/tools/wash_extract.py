# 洗稿取料：人物档案的性格、灵魂内核两栏（世界书和介绍页共用一份），介绍页里给玩家看的文字。
# 用法：python3 -I -X utf8 大旻长夜/tools/wash_extract.py   写 大旻长夜/洗稿/份N_输入.json 和 份表.json
# 设定类的数据（二十一道途 roads、武学与命格目录、命箓 mingluData、开局 starts）照旧，不取。
import json, re, os, sys, html as H
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
card = json.load(open(os.path.join(ROOT, '原卡', '大旻长夜_风月原卡.json'), encoding='utf-8'))
WB, INTRO = card['world_book'], card['intro']
OUT = os.path.join(ROOT, '洗稿')
js = re.findall(r'<script[^>]*>([\s\S]*?)</script>', INTRO)[0]
def arr(name):
    i = js.find('const %s=' % name); j = i + len('const %s=' % name)
    v, end = json.JSONDecoder().raw_decode(js[j:]); return v
def sec(v, name):
    m = re.search(r'^### %s\n([\s\S]*?)(?=\n### |\Z)' % re.escape(name), v, re.M); return m.group(1).strip() if m else None
CJK = re.compile(r'[一-鿿]')
items = {}
# 1) 人物：性格、灵魂内核（世界书 #i 与介绍页 forceData 同名人物共用）
souls = []
for i, e in enumerate(WB):
    if e['group'] != '超维·40人物灵魂档案': continue
    name = re.search(r'## 人物灵魂档案：(.+)', e['value']).group(1).strip()
    ctx = '；'.join(x for x in [sec(e['value'], '人物定位'), (re.search(r'组织锚定：([^\n]+)', e['value']) or [None, ''])[1], (re.search(r'超凡锚定：([^\n]+)', e['value']) or [None, ''])[1]] if x)
    for f in ('性格', '灵魂内核'):
        souls.append({'k': 'wb:%d:%s' % (i, f), 'who': name, 'ctx': ctx, 't': sec(e['value'], f)})
# 2) 介绍页数据
def walk(v, path, out, skip=()):
    if isinstance(v, str):
        if len(CJK.findall(v)) >= 6 and path[-1] not in skip: out.append((path, v))
    elif isinstance(v, list):
        for n, x in enumerate(v): walk(x, path + [n], out, skip)
    elif isinstance(v, dict):
        for k, x in v.items(): walk(x, path + [k], out, skip)
SKIP = ('portrait', 'name', 'age', 'race', 'oath', 'tier', 'gender', 'path', 'sequence', 'affiliation', 'role', 'index', 'cat', 'tags',
        'personality', 'soul')   # 人物的性格、灵魂内核走第 1 类，同一份
def rows(name, skip=SKIP):
    out = []; walk(arr(name), [name], out, skip); return out
force = rows('forceData'); hero = rows('heroineArchiveData', SKIP[:-2]); regions = rows('atlasRegions')
small = rows('historyData') + rows('sigilData') + rows('forceCatMeta') + rows('startPresets')
# 3) 页面上写死的文字（标签之间、六个汉字以上）
body = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', INTRO)
static = []
for m in re.finditer(r'>([^<>]+)<', body):
    t = H.unescape(m.group(1)).strip()
    if len(CJK.findall(t)) >= 6 and t not in [x[1] for x in static]: static.append((['static', len(static)], t))
def pack(lst): return [{'k': json.dumps(p, ensure_ascii=False), 't': t} for p, t in lst]
# 分份：人物两栏一份；页面文字和小数据加女主一份；山河两份；势力四份
force_by_cat = {}
for p, t in force: force_by_cat.setdefault(p[1], []).append((p, t))
cats = list(force_by_cat)
def split_even(groups, n):
    parts = [[] for _ in range(n)]; sizes = [0] * n
    for g in sorted(groups, key=lambda g: -sum(len(t) for _, t in g)):
        j = sizes.index(min(sizes)); parts[j] += g; sizes[j] += sum(len(t) for _, t in g)
    return parts
reg_groups = {}
for p, t in regions: reg_groups.setdefault(p[1], []).append((p, t))
PARTS = [('人物两栏', souls),
         ('页面与女主', pack(static + small + hero)),
         *[('山河%d' % (n + 1), pack(x)) for n, x in enumerate(split_even(list(reg_groups.values()), 2))],
         *[('势力%d' % (n + 1), pack(x)) for n, x in enumerate(split_even([force_by_cat[c] for c in cats], 4))]]
table = []
for n, (title, lst) in enumerate(PARTS, 1):
    fn = os.path.join(OUT, '份%d_输入.json' % n)
    json.dump(lst, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    table.append({'份': n, '名': title, '条': len(lst), '字': sum(len(x['t']) for x in lst)})
    print('份%d %-6s %4d 条 %6d 字' % (n, title, len(lst), sum(len(x['t']) for x in lst)))
json.dump(table, open(os.path.join(OUT, '份表.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# 专名表：校验时查改后有没有丢
names = set()
for i, e in enumerate(WB):
    m = re.search(r'^#+ [^\n：]*：(.+)$', e['value'], re.M)
    if m and 2 <= len(m.group(1).strip()) <= 12: names.add(m.group(1).strip())
for p, t in force + hero + regions:
    pass
fd = arr('forceData')
for k, v in fd.items():
    names.add(k)
    for pp in v.get('people', []): names.add(pp['name'])
for h in arr('heroineArchiveData'): names.add(h['name'])
for r in arr('atlasRegions'):
    for key in ('name', 'title'):
        if isinstance(r, dict) and isinstance(r.get(key), str) and len(r[key]) <= 12: names.add(r[key])
json.dump(sorted(n for n in names if len(n) >= 2), open(os.path.join(OUT, '专名表.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('专名', len(names))
