#!/usr/bin/env python3
# 查图报告落到资料上（11-06）：读报告目录里的 <组名>.json，改资料、把要重出的旧图挪进备选，列出要重出的键。
#   python apply_review.py <报告目录> [--apply] [--tag 查图前] [--skip en1,en2] [组名 …]
# 一条：{"set":"山铜纪","page":"s3a","en":"s3a_karn","redo":["sheet"],"append":{"who":" …"},"replace":{"casual":["旧","新"]},"why":"…"}
# redo 有 sheet 的挪整个文件夹（艺术照和表情照设定图出，跟着重出）；只有 art、faces 的只挪那一张。
# 不加 --apply 只报。动完在各纪跑 cast_lint，再照它打出来的命令重出（已有的图 gpt_sheet.py 不重出，只补挪走的）。
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = {'who', 'face', 'face_extra', 'casual', 'private', 'battle', 'battle_pose', 'formal', 'art', 'art_extra', 'build', 'palette'}
ONE = {'art': ['art.png', 'art_参考.json', 'art.log'], 'faces': ['faces.png', 'faces_raw.png', 'faces.log']}

args = sys.argv[1:]
apply_ = '--apply' in args
tag = '查图前'
skip = set()
names = []
i = 0
root = args[0]
i = 1
while i < len(args):
    a = args[i]
    if a == '--apply':
        pass
    elif a == '--tag':
        i += 1
        tag = args[i]
    elif a == '--skip':
        i += 1
        skip = set(args[i].split(','))
    else:
        names.append(a)
    i += 1

files = [os.path.join(root, n + '.json') for n in names] if names else sorted(glob.glob(os.path.join(root, '*.json')))
items = []
for f in files:
    for it in json.load(open(f, encoding='utf-8')):
        it['_from'] = os.path.basename(f)
        items.append(it)

seen = {}
problems = []
docs = {}
for it in items:
    en = it['en']
    if en in skip:
        continue
    if en in seen:
        problems.append('%s 报了两回（%s、%s），后一回接着改' % (en, seen[en], it['_from']))
    seen[en] = it['_from']
    p = os.path.join(HERE, 'cast', it['set'], it['page'] + '.json') if it['set'] != '1001' else os.path.join(HERE, 'cast', it['page'] + '.json')
    if p not in docs:
        docs[p] = json.load(open(p, encoding='utf-8'))
    hit = [c for c in docs[p] if c['en'] == en]
    if not hit:
        problems.append('%s 在 %s 里找不到' % (en, p))
        continue
    c = hit[0]
    for k, (old, new) in (it.get('replace') or {}).items():
        if k not in FIELDS:
            problems.append('%s replace 栏不认得 %s' % (en, k))
            continue
        if c.get(k, '').count(old) != 1:
            problems.append('%s replace %s 的旧字串出现 %d 回：%s' % (en, k, c.get(k, '').count(old), old[:60]))
            continue
        c[k] = c[k].replace(old, new)
    for k, s in (it.get('append') or {}).items():
        if k not in FIELDS:
            problems.append('%s append 栏不认得 %s' % (en, k))
            continue
        c[k] = (c.get(k) or '').rstrip() + ' ' + s.strip()

redo = {}
for it in items:
    if it['en'] in skip:
        continue
    r = set(it.get('redo') or [])
    redo.setdefault(it['set'], {}).setdefault(it['en'], set()).update(r)

print('条数', len(items), '人数', len(seen), '要改的页', len(docs))
for s in problems:
    print('  问题：' + s)
for s, m in redo.items():
    print(s, len(m), '位', '设定图', sum(1 for r in m.values() if 'sheet' in r), '艺术照', sum(1 for r in m.values() if 'art' in r and 'sheet' not in r), '表情', sum(1 for r in m.values() if 'faces' in r and 'sheet' not in r))
    print('   CAST_SET=%s CAST_WORKERS=4 gpt_sheet.py %s' % (s, ' '.join(sorted(m))))
if not apply_:
    print('（没有 --apply，什么也没动）')
    sys.exit(0)
for p, d in docs.items():
    open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(d, ensure_ascii=False, indent=1) + '\n')
n = 0
for s, m in redo.items():
    for en, r in m.items():
        src = os.path.join(HERE, 'out', '立绘_' + s if s != '1001' else '立绘_v3', en)
        dst = os.path.join(HERE, 'out', ('立绘_%s_备选' % s) if s != '1001' else '立绘_v3_备选', en, tag)
        if not os.path.isdir(src):
            print('  没有文件夹', src)
            continue
        os.makedirs(dst, exist_ok=True)
        if 'sheet' in r:
            for x in os.listdir(src):
                os.replace(os.path.join(src, x), os.path.join(dst, x))
                n += 1
        else:
            for w in r:
                for x in ONE.get(w, []):
                    a = os.path.join(src, x)
                    if os.path.exists(a):
                        os.replace(a, os.path.join(dst, x))
                        n += 1
print('挪了', n, '个文件；资料写回', len(docs), '份')
