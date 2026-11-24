# 把 本事_第二稿.json 套进 门面外壳的 build.json（eras.<纪>.periods[].skills），顺手改 life.json 里“走一遍前半生”的 sk 提示。
# 用法（仓库根上跑）：
#   python -I -X utf8 底稿/门面/第二轮/建档/tools/apply_skills.py --dry      只报，不写
#   python -I -X utf8 底稿/门面/第二轮/建档/tools/apply_skills.py            写 build.json 和 life.json
#   --no-desc  skills 里不写 d（shell.js 只读 s、from、to）
#   --no-life  不碰 life.json
#   --src 另一份 json   --build 另一份 build.json   --life 另一份 life.json
# 本事_第二稿.json 的样子：{时段 id: [{"s": 短名, "d": 说明, "from": 年, "to": 年, "was": [第一稿替下的几项]}]}，
# 时段 id 照 build.json 里 periods 的 id，1001 年那一段是 "1001"（eras.maze.periods 里，不在 eras.maze.now）。
# build.json 照原来的排法写回（json.dumps indent=1 加一个换行）。
# life.json 是手排的，只改 "sk": [...] 那一截：shell.js 的 lifeSkills 拿提示里的字去本事短名里找子串，
# 第一稿的名字换掉以后提示会落空，这里照 was 把落空的提示换成接替它的新短名。
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
args = sys.argv[1:]
def opt(name, default):
    if name in args:
        i = args.index(name); return args[i + 1]
    return default
DRY = '--dry' in args
NO_DESC = '--no-desc' in args
NO_LIFE = '--no-life' in args
SRC = opt('--src', os.path.join(HERE, '..', '本事_第二稿.json'))
BUILD = opt('--build', os.path.join(ROOT, '底稿', '门面', '小样_外壳', 'data', 'build.json'))
LIFE = opt('--life', os.path.join(ROOT, '底稿', '门面', '小样_外壳', 'data', 'life.json'))

src = json.load(open(SRC, encoding='utf-8'))
btxt = open(BUILD, encoding='utf-8').read()
build = json.loads(btxt)
if json.dumps(build, ensure_ascii=False, indent=1) + '\n' != btxt:
    print('提醒：build.json 原来不是 indent=1 的排法，写回会改排版。')

def norm(x):
    return x if isinstance(x, dict) else {'s': x}

# 时段 id -> (纪, period)
where = {}
for era, E in build['eras'].items():
    for P in E.get('periods', []):
        where[P['id']] = (era, P)
miss = [k for k in src if k not in where]
if miss:
    sys.exit('json 里有 build.json 没有的时段：' + '、'.join(miss))
left = [k for k in where if k not in src]

old_of = {k: [norm(x) for x in where[k][1].get('skills', [])] for k in where}

def new_item(it):
    o = {'s': it['s']}
    if not NO_DESC and it.get('d'): o['d'] = it['d']
    if it.get('from') is not None: o['from'] = it['from']
    if it.get('to') is not None: o['to'] = it['to']
    return o

print('== build.json')
for k, items in src.items():
    era, P = where[k]
    olds = [x['s'] for x in old_of[k]]
    news = [x['s'] for x in items]
    gone = [s for s in olds if s not in news]
    add = [s for s in news if s not in olds]
    wasall = {w for x in items for w in x.get('was', [])}
    orphan = [s for s in gone if s not in wasall]
    print(f'{era}.{k}（{P.get("name", "")}）{len(olds)} -> {len(news)} 项')
    if add: print('  新：' + '、'.join(add))
    if gone: print('  拿掉：' + '、'.join(gone))
    if orphan: print('  （拿掉的里头没有 was 接的：' + '、'.join(orphan) + '）')
if left: print('json 里没有、照旧不动的时段：' + '、'.join(left))

# life.json
life_plan = []
if not NO_LIFE and os.path.exists(LIFE):
    ltxt = open(LIFE, encoding='utf-8').read()
    life = json.loads(ltxt)
    def periods_for(era, seg):
        if era == 'now':
            return ['1001'] if '1001' in where else []
        lo, hi = seg.get('from'), seg.get('to')
        out = []
        for P in build['eras'].get(era, {}).get('periods', []):
            if P['id'] == '1001' and era == 'maze': continue
            if lo is not None and P['to'] < lo: continue
            if hi is not None and P['from'] > hi: continue
            out.append(P['id'])
        return out
    # 照文件里的先后收所有带 sk 的项
    found = []
    def walk(x, ctx):
        if isinstance(x, dict):
            if 'sk' in x: found.append((ctx, x))
            for v in x.values(): walk(v, ctx)
        elif isinstance(x, list):
            for v in x: walk(v, ctx)
    for era, segs in life.get('eras', {}).items():
        seglist = segs if isinstance(segs, list) else [segs]
        for seg in seglist:
            walk(seg, (era, seg.get('name', ''), periods_for(era, seg)))
    print('\n== life.json 的本事提示')
    unresolved = []
    for (era, sname, pids), o in found:
        hints = o['sk']; out = []
        for h in hints:
            newnames = [it['s'] for p in pids for it in (src.get(p) or [new_item(x) for x in old_of[p]])]
            if any(h in n for n in newnames):
                if h not in out: out.append(h)
                continue
            olds = {x['s'] for p in pids for x in old_of[p] if h in x['s']}
            rep = []
            for p in pids:
                for it in src.get(p, []):
                    if olds & set(it.get('was', [])) and it['s'] not in rep and it['s'] not in out:
                        rep.append(it['s'])
            if rep: out.extend(rep)
            elif olds and any(olds & set(it.get('was', [])) for p in pids for it in src.get(p, [])):
                pass  # 跟前一条提示接的是同一项，新短名已经在里头了，这一条用不着
            else:
                unresolved.append((era, sname, o.get('t'), h)); out.append(h)
        life_plan.append((hints, out))
        if out != hints:
            print(f'  {era}·{sname}·{o.get("t")}：{hints} -> {out}')
    if unresolved:
        print('  找不到接替的提示（照旧留着，那一项在前半生里挑不出本事）：')
        for u in unresolved: print('   ', u)
    ms = list(re.finditer(r'"sk": \[[^\]]*\]', ltxt))
    if len(ms) != len(found):
        sys.exit(f'life.json 里 "sk" 出现 {len(ms)} 处，解出来 {len(found)} 处，对不上，不改 life.json。')
    for m, (hints, _) in zip(ms, life_plan):
        if json.loads('{' + m.group(0) + '}')['sk'] != hints:
            sys.exit('life.json 的 sk 先后跟解出来的对不上，不改 life.json。')

if DRY:
    print('\n--dry：没有写盘。')
    sys.exit(0)

for k, items in src.items():
    where[k][1]['skills'] = [new_item(x) for x in items]
open(BUILD, 'w', encoding='utf-8', newline='\n').write(json.dumps(build, ensure_ascii=False, indent=1) + '\n')
print('写了', BUILD)

if life_plan:
    pieces, last = [], 0
    for m, (hints, out) in zip(ms, life_plan):
        pieces.append(ltxt[last:m.start()])
        pieces.append('"sk": [' + ', '.join(json.dumps(x, ensure_ascii=False) for x in out) + ']')
        last = m.end()
    pieces.append(ltxt[last:])
    new = ''.join(pieces)
    json.loads(new)
    if new != ltxt:
        open(LIFE, 'w', encoding='utf-8', newline='\n').write(new)
        print('写了', LIFE)
